"""Doklad je objekt. Text faktury skládá třída, ne volné funkce."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities import InvoiceDetail
from domain.money import Money


class Document(ABC):
    """Tiskový výstup, který umí vykreslit sám sebe."""

    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError


class InvoiceDocument(Document):
    def __init__(self, detail: InvoiceDetail) -> None:
        self.detail = detail

    def render(self) -> str:
        supplier = self.detail.supplier
        buyer = self.detail.buyer
        lines = [
            f"FAKTURA {self.detail.invoice_number}",
            "",
            "Dodavatel",
            supplier.company_name,
            supplier.identity_line(),
            supplier.address_line(),
            supplier.contact_line(),
            supplier.bank_line(),
            "",
            "Odběratel",
            buyer.display_name(),
            buyer.kind_label(),
            buyer.identity_line(),
            buyer.address_line(),
            buyer.contact_line(),
            buyer.contact_person_line(),
            "",
            f"Datum vystavení: {self._date(self.detail.issued_on)}",
            f"Datum uskutečnění zdanitelného plnění: {self._date(self.detail.taxable_on)}",
            f"Datum splatnosti: {self._date(self.detail.due_on)}",
            f"Způsob úhrady: {self.detail.payment_method}",
            f"Variabilní symbol: {self.detail.variable_symbol}",
        ]
        if self.detail.note:
            lines.extend(["", f"Poznámka: {self.detail.note}"])
        lines.extend(["", "Položky"])
        lines.extend(line.render() for line in self.detail.lines)
        lines.extend(
            [
                "",
                f"Základ daně: {Money(self.detail.total_net).format()} Kč",
                f"DPH: {Money(self.detail.total_vat).format()} Kč",
                f"Celkem k úhradě: {Money(self.detail.total_gross).format()} Kč",
            ]
        )
        return "\n".join(part for part in lines if part)

    @staticmethod
    def _date(value) -> str:
        return value.strftime("%d.%m.%Y")
