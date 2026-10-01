"""Objekty, které přecházejí z databáze do viewmodelu."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from domain.money import Money, Quantity


class ContactCard:
    """Společné řádky adresy a identifikace na dokladu."""

    street: str
    city: str
    zip_code: str
    country: str
    email: str
    phone: str
    ico: str
    dic: str

    def identity_line(self) -> str | None:
        parts = []
        if self.ico:
            parts.append(f"IČO: {self.ico}")
        if self.dic:
            parts.append(f"DIČ: {self.dic}")
        return "   ".join(parts) if parts else None

    def address_line(self) -> str | None:
        place = ", ".join(
            part for part in (self.street, f"{self.zip_code} {self.city}".strip(), self.country) if part and part.strip()
        )
        return place or None

    def contact_line(self) -> str | None:
        parts = [part for part in (self.email, self.phone) if part]
        return "   ".join(parts) if parts else None


@dataclass
class WarehouseCard:
    id: int
    code: str
    name: str
    address: str

    def as_table(self) -> dict:
        return {"id": self.id, "code": self.code, "name": self.name, "address": self.address}


# Zpětná jména, která používá služba a testy.
Warehouse = WarehouseCard


@dataclass
class ProductCard:
    id: int
    sku: str
    name: str
    unit: str
    unit_price: Decimal
    vat_rate: Decimal
    stock_qty: Decimal

    def as_table(self) -> dict:
        rate = Quantity(self.vat_rate).format()
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "unit": self.unit,
            "unit_price": f"{self.unit_price:.2f}",
            "price_label": f"{Money(self.unit_price).format()} Kč",
            "vat_rate": rate,
            "vat_label": f"{rate} %",
            "stock_label": f"{Quantity(self.stock_qty).format()} {self.unit}",
        }


Product = ProductCard


@dataclass
class StockCard:
    product_id: int
    warehouse_id: int
    quantity: Decimal
    sku: str
    product_name: str
    unit: str
    warehouse_code: str
    warehouse_name: str

    def as_table(self) -> dict:
        return {
            "sku": self.sku,
            "name": self.product_name,
            "warehouse": f"{self.warehouse_code} — {self.warehouse_name}",
            "quantity_label": f"{Quantity(self.quantity).format()} {self.unit}",
        }


StockRow = StockCard


@dataclass
class MovementCard:
    created_at: datetime
    kind: str
    quantity: Decimal
    note: str
    sku: str
    product_name: str
    unit: str
    warehouse_code: str
    related_code: str | None
    kind_label: str
    description: str

    def as_table(self) -> dict:
        return {
            "when": self.created_at.strftime("%d.%m.%Y %H:%M"),
            "kind_label": self.kind_label,
            "description": self.description,
        }


MovementRow = MovementCard


@dataclass
class SupplierCard(ContactCard):
    company_name: str
    ico: str
    dic: str
    street: str
    city: str
    zip_code: str
    country: str
    email: str
    phone: str
    bank_account: str
    bank_code: str
    iban: str

    def bank_line(self) -> str | None:
        parts = []
        if self.bank_account:
            number = f"{self.bank_account}/{self.bank_code}" if self.bank_code else self.bank_account
            parts.append(f"Účet: {number}")
        if self.iban:
            parts.append(f"IBAN: {self.iban}")
        return "   ".join(parts) if parts else None


Company = SupplierCard


@dataclass
class PartyInput:
    kind: str
    first_name: str = ""
    last_name: str = ""
    company_name: str = ""
    ico: str = ""
    dic: str = ""
    street: str = ""
    city: str = ""
    zip_code: str = ""
    country: str = "Česká republika"
    email: str = ""
    phone: str = ""


@dataclass
class PartyCard(ContactCard):
    id: int
    kind: str
    first_name: str
    last_name: str
    company_name: str
    ico: str
    dic: str
    street: str
    city: str
    zip_code: str
    country: str
    email: str
    phone: str

    def display_name(self) -> str:
        person = f"{self.first_name} {self.last_name}".strip()
        if self.company_name:
            return f"{person} ({self.company_name})" if person else self.company_name
        return person

    def kind_label(self) -> str:
        return "Odběratel"

    def contact_person_line(self) -> str | None:
        return None


class NaturalPersonCard(PartyCard):
    def display_name(self) -> str:
        person = f"{self.first_name} {self.last_name}".strip()
        if self.company_name:
            return f"{person} ({self.company_name})"
        return person

    def kind_label(self) -> str:
        return "Fyzická osoba"


class LegalEntityCard(PartyCard):
    def display_name(self) -> str:
        person = f"{self.first_name} {self.last_name}".strip()
        return self.company_name or person

    def kind_label(self) -> str:
        return "Právnická osoba"

    def contact_person_line(self) -> str | None:
        name = f"{self.first_name} {self.last_name}".strip()
        return f"Kontaktní osoba: {name}" if name else None


Party = PartyCard


@dataclass
class InvoiceLineInput:
    product_id: int
    warehouse_id: int
    quantity: Decimal
    unit_price: Decimal


@dataclass
class InvoiceHeader:
    issued_on: date
    taxable_on: date
    due_on: date
    payment_method: str
    variable_symbol: str
    note: str


@dataclass
class InvoiceLineCard:
    item_name: str
    sku: str
    unit: str
    warehouse_code: str
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal
    line_net: Decimal
    line_vat: Decimal
    line_gross: Decimal

    def render(self) -> str:
        return (
            f"{self.sku}  {self.item_name}  |  sklad {self.warehouse_code}  |  "
            f"{Quantity(self.quantity).format()} {self.unit}  ×  {Money(self.unit_price).format()} Kč  |  "
            f"DPH {Quantity(self.vat_rate).format()} %  |  {Money(self.line_gross).format()} Kč"
        )


InvoiceLine = InvoiceLineCard


@dataclass
class InvoiceSummary:
    id: int
    invoice_number: str
    issued_on: date
    total_gross: Decimal
    payment_method: str
    buyer_name: str

    def as_table(self) -> dict:
        return {
            "id": self.id,
            "number": self.invoice_number,
            "issued": self.issued_on.strftime("%d.%m.%Y"),
            "buyer": self.buyer_name,
            "total": f"{Money(self.total_gross).format()} Kč",
            "payment": self.payment_method,
        }


@dataclass
class InvoiceDetail:
    id: int
    invoice_number: str
    issued_on: date
    taxable_on: date
    due_on: date
    payment_method: str
    variable_symbol: str
    note: str
    total_net: Decimal
    total_vat: Decimal
    total_gross: Decimal
    supplier: SupplierCard
    buyer: PartyCard
    lines: list[InvoiceLineCard] = field(default_factory=list)
