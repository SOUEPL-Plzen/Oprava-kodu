"""Aplikační služba. Validuje formuláře a předává práci ORM objektům."""

from __future__ import annotations

import re
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from models.data import CompanyProfile, Invoice as InvoiceRow, Product as ProductRow, StockItem, StockMovement, Warehouse as WarehouseRow
from domain.entities import Company, InvoiceDetail, InvoiceHeader, InvoiceLineInput, InvoiceSummary, MovementRow, PartyInput, Product, StockRow, Warehouse
from domain.errors import ValidationError
from domain.money import Money, Quantity
from domain.validation import Catalogue, Dic, EmailAddress, Field, Ico, PostalCode
from domain.ledger import InvoiceBook, StockLedger

_CODE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]{0,31}$")
_SKU = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._\-]{0,63}$")


class InventoryService:
    def __init__(self, database) -> None:
        self.db = database

    def list_warehouses(self) -> list[Warehouse]:
        with self.db.session() as session:
            rows = session.scalars(select(WarehouseRow).order_by(WarehouseRow.code)).all()
            return [row.to_dto() for row in rows]

    def add_warehouse(self, code: str, name: str, address: str) -> None:
        normalized_code = Field.read(code, "Kód skladu", 32, required=True).upper()
        if not _CODE.fullmatch(normalized_code):
            raise ValidationError("Kód skladu může obsahovat písmena, čísla, pomlčku a podtržítko.")
        try:
            with self.db.session() as session:
                session.add(
                    WarehouseRow(
                        code=normalized_code,
                        name=Field.read(name, "Název skladu", 255, required=True),
                        address=Field.read(address, "Adresa", 512, required=False),
                    )
                )
        except IntegrityError as exc:
            if _is_duplicate(exc):
                raise ValidationError("Sklad s tímto kódem už existuje.") from exc
            raise

    def list_products(self) -> list[Product]:
        with self.db.session() as session:
            rows = session.scalars(
                select(ProductRow).options(selectinload(ProductRow.stocks)).order_by(ProductRow.name)
            ).all()
            return [row.to_dto() for row in rows]

    def add_product(self, sku: str, name: str, unit: str, unit_price: Decimal, vat_rate: Decimal) -> None:
        normalized_sku = Field.read(sku, "SKU", 64, required=True).upper()
        if not _SKU.fullmatch(normalized_sku):
            raise ValidationError("SKU může obsahovat písmena, čísla, tečku, pomlčku a podtržítko.")
        if unit not in Catalogue.UNITS:
            raise ValidationError("Vyberte měrnou jednotku.")
        price = Money(unit_price).amount
        if price < 0:
            raise ValidationError("Cena nesmí být záporná.")
        rate = Money(vat_rate).amount
        if rate not in Catalogue.VAT_RATES:
            raise ValidationError("Sazba DPH musí být 0, 12 nebo 21 %.")
        try:
            with self.db.session() as session:
                session.add(
                    ProductRow(
                        sku=normalized_sku,
                        name=Field.read(name, "Název zboží", 255, required=True),
                        unit=unit,
                        unit_price=price,
                        vat_rate=rate,
                    )
                )
        except IntegrityError as exc:
            if _is_duplicate(exc):
                raise ValidationError("Zboží s tímto SKU už existuje.") from exc
            raise

    def list_stock(self) -> list[StockRow]:
        with self.db.session() as session:
            rows = session.scalars(
                select(StockItem)
                .join(StockItem.product)
                .join(StockItem.warehouse)
                .options(selectinload(StockItem.product), selectinload(StockItem.warehouse))
                .order_by(ProductRow.name, WarehouseRow.code)
            ).all()
            return [row.to_dto() for row in rows]

    def list_movements(self, limit: int = 40) -> list[MovementRow]:
        with self.db.session() as session:
            rows = session.scalars(
                select(StockMovement)
                .options(
                    selectinload(StockMovement.product),
                    selectinload(StockMovement.warehouse),
                    selectinload(StockMovement.related_warehouse),
                )
                .order_by(StockMovement.id.desc())
                .limit(int(limit))
            ).all()
            return [row.to_dto() for row in rows]

    def receive(self, product_id: int, warehouse_id: int, quantity: Decimal, note: str) -> None:
        qty = Quantity(quantity).amount
        if qty <= 0:
            raise ValidationError("Množství musí být větší než nula.")
        text = Field.read(note, "Poznámka", 512, required=False)
        with self.db.session() as session:
            StockLedger(session).receive(product_id, warehouse_id, qty, text)

    def transfer(
        self,
        product_id: int,
        from_warehouse_id: int,
        to_warehouse_id: int,
        quantity: Decimal,
        note: str,
    ) -> None:
        qty = Quantity(quantity).amount
        if qty <= 0:
            raise ValidationError("Množství musí být větší než nula.")
        text = Field.read(note, "Poznámka", 512, required=False)
        with self.db.session() as session:
            StockLedger(session).transfer(product_id, from_warehouse_id, to_warehouse_id, qty, text)

    def list_invoices(self) -> list[InvoiceSummary]:
        with self.db.session() as session:
            rows = session.scalars(
                select(InvoiceRow).options(selectinload(InvoiceRow.buyer)).order_by(InvoiceRow.id.desc())
            ).all()
            return [row.to_summary() for row in rows]

    def get_invoice(self, invoice_id: int) -> InvoiceDetail:
        with self.db.session() as session:
            invoice = session.scalar(
                select(InvoiceRow)
                .where(InvoiceRow.id == invoice_id)
                .options(selectinload(InvoiceRow.buyer), selectinload(InvoiceRow.lines))
            )
            if invoice is None:
                raise ValidationError("Faktura neexistuje.")
            return invoice.to_detail()

    def issue_invoice(self, party: PartyInput, header: InvoiceHeader, lines: list[InvoiceLineInput]) -> InvoiceDetail:
        normalized_party = self._validate_party(party)
        normalized_header = self._validate_header(header)
        prepared = []
        for line in lines:
            qty = Quantity(line.quantity).amount
            if qty <= 0:
                raise ValidationError("Množství na položce musí být větší než nula.")
            prepared.append(
                InvoiceLineInput(
                    product_id=line.product_id,
                    warehouse_id=line.warehouse_id,
                    quantity=qty,
                    unit_price=Money(line.unit_price).amount,
                )
            )
        with self.db.session() as session:
            return InvoiceBook(session).issue(normalized_party, normalized_header, prepared)

    def get_company(self) -> Company:
        with self.db.session() as session:
            company = session.get(CompanyProfile, 1)
            if company is None:
                raise ValidationError("Chybí nastavení dodavatele.")
            return company.to_dto()

    def save_company(self, company: Company) -> None:
        normalized = self._validate_company(company)
        with self.db.session() as session:
            profile = session.get(CompanyProfile, 1)
            if profile is None:
                profile = CompanyProfile.empty()
                session.add(profile)
            profile.copy_from(normalized)

    def _validate_company(self, company: Company) -> Company:
        name = Field.read(company.company_name, "Název dodavatele", 255, required=True)
        ico = Ico(company.ico).value
        dic = Dic(company.dic).value
        if ico and not Ico(ico).is_valid():
            raise ValidationError("IČO dodavatele není platné.")
        if dic and not Dic(dic).is_valid():
            raise ValidationError("DIČ dodavatele musí být ve tvaru CZ a 8 až 10 číslic.")
        country = Field.read(company.country, "Stát", 64, required=True)
        return Company(
            company_name=name,
            ico=ico,
            dic=dic,
            street=Field.read(company.street, "Ulice", 255, required=True),
            city=Field.read(company.city, "Město", 128, required=True),
            zip_code=PostalCode(Field.read(company.zip_code, "PSČ", 16, required=True), country).value,
            country=country,
            email=EmailAddress(company.email).value,
            phone=Field.read(company.phone, "Telefon", 32, required=False),
            bank_account=Field.read(company.bank_account, "Číslo účtu", 64, required=False),
            bank_code=Field.read(company.bank_code, "Kód banky", 8, required=False),
            iban=Field.read(company.iban, "IBAN", 42, required=False).replace(" ", "").upper(),
        )

    def _validate_party(self, party: PartyInput) -> PartyInput:
        if party.kind not in ("fyzicka", "pravnicka"):
            raise ValidationError("Vyberte, jestli je odběratel fyzická, nebo právnická osoba.")
        physical = party.kind == "fyzicka"
        ico = Ico(party.ico).value
        dic = Dic(party.dic).value
        if not physical and not ico:
            raise ValidationError("U právnické osoby vyplňte IČO.")
        if ico and not Ico(ico).is_valid():
            raise ValidationError("IČO odběratele není platné.")
        if dic and not Dic(dic).is_valid():
            raise ValidationError("DIČ odběratele musí být ve tvaru CZ a 8 až 10 číslic.")
        country = Field.read(party.country, "Stát", 64, required=True)
        return PartyInput(
            kind=party.kind,
            first_name=Field.read(party.first_name, "Jméno", 128, required=physical),
            last_name=Field.read(party.last_name, "Příjmení", 128, required=physical),
            company_name=Field.read(party.company_name, "Název firmy", 255, required=not physical),
            ico=ico,
            dic=dic,
            street=Field.read(party.street, "Ulice", 255, required=True),
            city=Field.read(party.city, "Město", 128, required=True),
            zip_code=PostalCode(Field.read(party.zip_code, "PSČ", 16, required=True), country).value,
            country=country,
            email=EmailAddress(party.email).value,
            phone=Field.read(party.phone, "Telefon", 32, required=False),
        )

    def _validate_header(self, header: InvoiceHeader) -> InvoiceHeader:
        if header.due_on < header.issued_on:
            raise ValidationError("Datum splatnosti nesmí být dřív než datum vystavení.")
        if header.payment_method not in Catalogue.PAYMENT_METHODS:
            raise ValidationError("Vyberte způsob úhrady.")
        variable_symbol = Field.read(header.variable_symbol, "Variabilní symbol", 10, required=False)
        if variable_symbol and not re.fullmatch(r"\d{1,10}", variable_symbol):
            raise ValidationError("Variabilní symbol může mít nejvýše 10 číslic.")
        return InvoiceHeader(
            issued_on=header.issued_on,
            taxable_on=header.taxable_on,
            due_on=header.due_on,
            payment_method=header.payment_method,
            variable_symbol=variable_symbol,
            note=Field.read(header.note, "Poznámka", 2000, required=False),
        )


def _is_duplicate(exc: IntegrityError) -> bool:
    orig = getattr(exc, "orig", None)
    if getattr(orig, "errno", None) == 1062:
        return True
    args = getattr(orig, "args", ())
    return bool(args) and args[0] == 1062
