"""Skladové operace nad ORM session. Nemají vlastní SQL."""

from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.data.invoice import Invoice
from models.data.invoice_line import InvoiceLine
from models.data.party import LegalEntity, NaturalPerson
from models.data.product import Product
from models.data.stock_item import StockItem
from models.data.stock_movement import InvoiceIssue, Receipt, TransferIn, TransferOut
from models.data.warehouse import Warehouse
from domain.entities import InvoiceLineInput
from domain.errors import StockError, ValidationError
from domain.money import Money, Quantity, VatBreakdown


class StockLedger:
    """Příjem, zámek řádku a přesun. Množství mění objekt StockItem."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def receive(self, product_id: int, warehouse_id: int, quantity: Decimal, note: str) -> None:
        self.require_product(product_id)
        self.require_warehouse(warehouse_id)
        item = self.lock(product_id, warehouse_id)
        item.increase(quantity)
        self.session.add(
            Receipt(
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity=quantity,
                note=note,
            )
        )

    def transfer(
        self,
        product_id: int,
        from_warehouse_id: int,
        to_warehouse_id: int,
        quantity: Decimal,
        note: str,
    ) -> None:
        if from_warehouse_id == to_warehouse_id:
            raise ValidationError("Zdrojový a cílový sklad musí být různé.")
        product = self.require_product(product_id)
        source_warehouse = self.require_warehouse(from_warehouse_id)
        self.require_warehouse(to_warehouse_id)
        locked = {warehouse_id: self.lock(product_id, warehouse_id) for warehouse_id in sorted((from_warehouse_id, to_warehouse_id))}
        source = locked[from_warehouse_id]
        target = locked[to_warehouse_id]
        if quantity > source.quantity:
            raise StockError(
                f"Na skladě {source_warehouse.code} je {Quantity(source.quantity).format()} "
                f"{product.unit} zboží {product.sku}, požadováno {Quantity(quantity).format()}."
            )
        source.decrease(quantity)
        target.increase(quantity)
        self.session.add(
            TransferOut(
                product_id=product_id,
                warehouse_id=from_warehouse_id,
                quantity=quantity,
                related_warehouse_id=to_warehouse_id,
                note=note,
            )
        )
        self.session.add(
            TransferIn(
                product_id=product_id,
                warehouse_id=to_warehouse_id,
                quantity=quantity,
                related_warehouse_id=from_warehouse_id,
                note=note,
            )
        )

    def lock(self, product_id: int, warehouse_id: int) -> StockItem:
        item = self.session.scalar(
            select(StockItem)
            .where(StockItem.product_id == product_id, StockItem.warehouse_id == warehouse_id)
            .with_for_update()
        )
        if item is not None:
            return item
        item = StockItem(product_id=product_id, warehouse_id=warehouse_id, quantity=Decimal("0"))
        self.session.add(item)
        self.session.flush()
        return item

    def require_product(self, product_id: int) -> Product:
        product = self.session.get(Product, product_id)
        if product is None:
            raise ValidationError("Zboží neexistuje.")
        return product

    def require_warehouse(self, warehouse_id: int) -> Warehouse:
        warehouse = self.session.get(Warehouse, warehouse_id)
        if warehouse is None:
            raise ValidationError("Sklad neexistuje.")
        return warehouse


class InvoiceBook:
    """Vystaví fakturu a ve stejné session odečte zásobu."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.stock = StockLedger(session)

    def issue(self, party_input, header, lines: list[InvoiceLineInput]):
        from domain.database import select_company

        company = select_company(self.session)
        if not company.company_name:
            raise ValidationError("Než vystavíte fakturu, vyplňte dodavatele na obrazovce Dodavatel.")
        if not lines:
            raise ValidationError("Faktura musí obsahovat alespoň jednu položku.")

        products = {}
        warehouses = {}
        for line in lines:
            products.setdefault(line.product_id, self.stock.require_product(line.product_id))
            warehouses.setdefault(line.warehouse_id, self.stock.require_warehouse(line.warehouse_id))
        keys = sorted({(line.product_id, line.warehouse_id) for line in lines})
        locked = {key: self.stock.lock(*key) for key in keys}
        needed: dict[tuple[int, int], Decimal] = defaultdict(lambda: Decimal(0))
        for line in lines:
            needed[(line.product_id, line.warehouse_id)] += line.quantity
        for key, quantity in needed.items():
            if quantity > locked[key].quantity:
                product = products[key[0]]
                warehouse = warehouses[key[1]]
                raise StockError(
                    f"Na skladě {warehouse.code} je {Quantity(locked[key].quantity).format()} "
                    f"{product.unit} zboží {product.sku}, faktura žádá {Quantity(quantity).format()}."
                )

        number = self._next_number(header.issued_on.year)
        variable_symbol = header.variable_symbol or re.sub(r"\D", "", number)[:10]
        buyer_cls = NaturalPerson if party_input.kind == "fyzicka" else LegalEntity
        buyer = buyer_cls(
            kind=party_input.kind,
            first_name=party_input.first_name,
            last_name=party_input.last_name,
            company_name=party_input.company_name,
            ico=party_input.ico,
            dic=party_input.dic,
            street=party_input.street,
            city=party_input.city,
            zip_code=party_input.zip_code,
            country=party_input.country,
            email=party_input.email,
            phone=party_input.phone,
        )
        invoice = Invoice(
            invoice_number=number,
            issued_on=header.issued_on,
            taxable_on=header.taxable_on,
            due_on=header.due_on,
            payment_method=header.payment_method,
            variable_symbol=variable_symbol,
            note=header.note,
            buyer=buyer,
            total_net=Decimal("0.00"),
            total_vat=Decimal("0.00"),
            total_gross=Decimal("0.00"),
        )
        invoice.snapshot_supplier(company)
        self.session.add(invoice)

        total_net = Decimal(0)
        total_vat = Decimal(0)
        total_gross = Decimal(0)
        for line in lines:
            product = products[line.product_id]
            warehouse = warehouses[line.warehouse_id]
            breakdown = VatBreakdown.from_line(line.quantity, line.unit_price, Decimal(product.vat_rate))
            net, vat, gross = breakdown.net.amount, breakdown.vat.amount, breakdown.gross.amount
            total_net += net
            total_vat += vat
            total_gross += gross
            invoice.lines.append(
                InvoiceLine(
                    product_id=line.product_id,
                    warehouse_id=line.warehouse_id,
                    item_name=product.name,
                    sku=product.sku,
                    unit=product.unit,
                    warehouse_code=warehouse.code,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    vat_rate=Decimal(product.vat_rate),
                    line_net=net,
                    line_vat=vat,
                    line_gross=gross,
                )
            )
            locked[(line.product_id, line.warehouse_id)].decrease(line.quantity)
            self.session.add(
                InvoiceIssue(
                    product_id=line.product_id,
                    warehouse_id=line.warehouse_id,
                    quantity=line.quantity,
                    invoice=invoice,
                    note=f"Faktura {number}",
                )
            )
        invoice.total_net = Money(total_net).amount
        invoice.total_vat = Money(total_vat).amount
        invoice.total_gross = Money(total_gross).amount
        self.session.flush()
        return invoice.to_detail()

    def _next_number(self, year: int) -> str:
        prefix = f"FA-{year}-"
        last = self.session.scalar(
            select(Invoice.invoice_number)
            .where(Invoice.invoice_number.like(prefix + "%"))
            .order_by(Invoice.invoice_number.desc())
            .limit(1)
        )
        sequence = 1
        if last:
            tail = str(last).rsplit("-", 1)[-1]
            if tail.isdigit():
                sequence = int(tail) + 1
        if sequence > 9999:
            raise ValidationError("Číselná řada faktur pro tento rok je vyčerpaná.")
        return f"{prefix}{sequence:04d}"
