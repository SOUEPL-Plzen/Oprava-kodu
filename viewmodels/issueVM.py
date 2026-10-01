"""Výdej na fakturu. Patří k views/issue.kv."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty

from domain.documents import InvoiceDocument
from domain.entities import InvoiceHeader, InvoiceLineInput, PartyInput
from domain.errors import AppError
from domain.money import Money, Quantity, VatBreakdown
from domain.validation import Catalogue, ChoiceId, DateField, PriceField, QuantityField
from viewmodels.transferVM import availability

CHOOSE_PRODUCT = "Vyberte zboží"
CHOOSE_WAREHOUSE = "Vyberte sklad"


class IssueVM(EventDispatcher):
    party_kind = StringProperty("fyzicka")
    first_name = StringProperty("")
    last_name = StringProperty("")
    company_name = StringProperty("")
    ico = StringProperty("")
    dic = StringProperty("")
    street = StringProperty("")
    city = StringProperty("")
    zip_code = StringProperty("")
    country = StringProperty("Česká republika")
    email = StringProperty("")
    phone = StringProperty("")
    issued_on = StringProperty("")
    taxable_on = StringProperty("")
    due_on = StringProperty("")
    payment_method = StringProperty("bankovní převod")
    payment_methods = ListProperty(list(Catalogue.PAYMENT_METHODS))
    variable_symbol = StringProperty("")
    invoice_note = StringProperty("")
    line_product = StringProperty(CHOOSE_PRODUCT)
    line_warehouse = StringProperty(CHOOSE_WAREHOUSE)
    line_qty = StringProperty("")
    line_price = StringProperty("")
    line_available = StringProperty("Skladem: —")
    draft_lines = ListProperty([])
    draft_totals_text = StringProperty("Základ 0,00 Kč    DPH 0,00 Kč    Celkem 0,00 Kč")

    def __init__(self, shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell
        today = date.today()
        self.issued_on = today.isoformat()
        self.taxable_on = today.isoformat()
        self.due_on = (today + timedelta(days=14)).isoformat()
        self.bind(draft_lines=self._sync_totals, line_product=self._sync_line_product)

    def add_line(self) -> None:
        def action() -> None:
            product_id = ChoiceId(self.line_product).require("Vyberte zboží.")
            warehouse_id = ChoiceId(self.line_warehouse).require("Vyberte sklad.")
            quantity = QuantityField(self.line_qty).amount
            price = PriceField(self.line_price).amount
            product = self.shell.find_product(product_id)
            if product is None:
                raise AppError("Zboží neexistuje.")
            warehouse = self.shell.find_warehouse(warehouse_id)
            already = self._draft_qty(product_id, warehouse_id)
            available = self.shell.available_qty(product_id, warehouse_id)
            if already + quantity > available:
                raise AppError(
                    f"Na skladě {warehouse['code']} je {Quantity(available).format()} {product['unit']} "
                    f"a v dokladu už je {Quantity(already).format()}."
                )
            breakdown = VatBreakdown.from_line(quantity, price, Money(Decimal(product["vat_rate"])).amount)
            self.draft_lines = self.draft_lines + [
                {
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "title": f"{product['sku']} — {product['name']}",
                    "warehouse": warehouse["code"],
                    "quantity": str(quantity),
                    "quantity_label": Quantity(quantity).format(),
                    "unit": product["unit"],
                    "unit_price": str(price),
                    "price_label": Money(price).format(),
                    "vat_rate": product["vat_rate"],
                    "gross_label": f"{breakdown.gross.format()} Kč",
                    "line_net": str(breakdown.net.amount),
                    "line_vat": str(breakdown.vat.amount),
                    "line_gross": str(breakdown.gross.amount),
                }
            ]
            self.line_qty = ""
            self.shell.succeed("Položka byla přidána na fakturu.")

        self.shell.guard(action)

    def remove_line(self, index: int) -> None:
        self.draft_lines = [line for position, line in enumerate(self.draft_lines) if position != index]
        self.shell.succeed("Položka byla odebrána.")

    def issue_invoice(self) -> None:
        def action() -> None:
            if not self.draft_lines:
                raise AppError("Přidejte alespoň jednu položku faktury.")
            detail = self.shell.service.issue_invoice(
                PartyInput(
                    kind=self.party_kind,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    company_name=self.company_name,
                    ico=self.ico,
                    dic=self.dic,
                    street=self.street,
                    city=self.city,
                    zip_code=self.zip_code,
                    country=self.country,
                    email=self.email,
                    phone=self.phone,
                ),
                InvoiceHeader(
                    issued_on=DateField(self.issued_on, "Datum vystavení").value,
                    taxable_on=DateField(self.taxable_on, "DUZP").value,
                    due_on=DateField(self.due_on, "Datum splatnosti").value,
                    payment_method=self.payment_method,
                    variable_symbol=self.variable_symbol,
                    note=self.invoice_note,
                ),
                [
                    InvoiceLineInput(
                        product_id=int(line["product_id"]),
                        warehouse_id=int(line["warehouse_id"]),
                        quantity=QuantityField(str(line["quantity"]).replace(".", ",")).amount,
                        unit_price=PriceField(str(line["unit_price"]).replace(".", ",")).amount,
                    )
                    for line in self.draft_lines
                ],
            )
            self.draft_lines = []
            self.line_qty = ""
            self.invoice_note = ""
            self.variable_symbol = ""
            self.shell.reload_lists()
            self.shell.show_document(InvoiceDocument(detail).render())
            self.shell.succeed(f"Faktura {detail.invoice_number} byla vystavena a zboží vydáno.")

        self.shell.guard(action)

    def refresh_available(self) -> None:
        self.line_available = availability(self.shell, self.line_product, self.line_warehouse)

    def _sync_line_product(self, *_args) -> None:
        product_id = ChoiceId(self.line_product).value
        for product in self.shell.products_vm.rows:
            if product["id"] == product_id:
                self.line_price = product["unit_price"].replace(".", ",")
                break
        self.refresh_available()

    def _sync_totals(self, *_args) -> None:
        net = vat = gross = Decimal(0)
        for line in self.draft_lines:
            net += Decimal(line["line_net"])
            vat += Decimal(line["line_vat"])
            gross += Decimal(line["line_gross"])
        self.draft_totals_text = (
            f"Základ {Money(net).format()} Kč    DPH {Money(vat).format()} Kč    "
            f"Celkem {Money(gross).format()} Kč"
        )

    def _draft_qty(self, product_id: int, warehouse_id: int) -> Decimal:
        total = Decimal(0)
        for line in self.draft_lines:
            if line["product_id"] == product_id and line["warehouse_id"] == warehouse_id:
                total += Decimal(line["quantity"])
        return total
