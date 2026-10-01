"""Tabulka invoice_lines."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.data.base import Entity, table_args
from domain.money import Money, Quantity


class InvoiceLine(Entity):
    __tablename__ = "invoice_lines"
    __table_args__ = table_args()

    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    item_name: Mapped[str] = mapped_column(String(255))
    sku: Mapped[str] = mapped_column(String(64))
    unit: Mapped[str] = mapped_column(String(16))
    warehouse_code: Mapped[str] = mapped_column(String(32))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    vat_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    line_net: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    line_vat: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    line_gross: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    invoice: Mapped["Invoice"] = relationship(back_populates="lines")

    def to_dto(self):
        from domain.entities import InvoiceLineCard

        return InvoiceLineCard(
            item_name=self.item_name,
            sku=self.sku,
            unit=self.unit,
            warehouse_code=self.warehouse_code,
            quantity=Quantity(self.quantity).amount,
            unit_price=Money(self.unit_price).amount,
            vat_rate=Money(self.vat_rate).amount,
            line_net=Money(self.line_net).amount,
            line_vat=Money(self.line_vat).amount,
            line_gross=Money(self.line_gross).amount,
        )
