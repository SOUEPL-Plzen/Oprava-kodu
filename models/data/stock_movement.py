"""Tabulka movements. Druhy pohybu jsou potomci jednoho záznamu."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.data.base import Entity, Timestamped, table_args
from models.data.product import Product
from models.data.warehouse import Warehouse
from domain.money import Quantity


class StockMovement(Timestamped, Entity):
    __tablename__ = "movements"
    __table_args__ = table_args()

    kind: Mapped[str] = mapped_column(String(32))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    related_warehouse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    invoice_id: Mapped[Optional[int]] = mapped_column(ForeignKey("invoices.id"), nullable=True)
    note: Mapped[str] = mapped_column(String(512), default="", server_default="")
    product: Mapped[Product] = relationship()
    warehouse: Mapped[Warehouse] = relationship(foreign_keys=[warehouse_id])
    related_warehouse: Mapped[Optional[Warehouse]] = relationship(foreign_keys=[related_warehouse_id])
    invoice: Mapped[Optional["Invoice"]] = relationship()

    __mapper_args__ = {"polymorphic_on": "kind", "polymorphic_identity": "pohyb"}

    def movement_label(self) -> str:
        return self.kind

    def sign(self) -> str:
        return ""

    def route(self) -> str:
        return self.warehouse.code

    def to_dto(self):
        from domain.entities import MovementCard

        note = f"  {self.note}" if self.note else ""
        description = (
            f"{self.product.sku} {self.product.name}   {self.sign()}{Quantity(self.quantity).format()} "
            f"{self.product.unit}   {self.route()}{note}"
        )
        return MovementCard(
            created_at=self.created_at,
            kind=self.kind,
            quantity=Quantity(self.quantity).amount,
            note=self.note,
            sku=self.product.sku,
            product_name=self.product.name,
            unit=self.product.unit,
            warehouse_code=self.warehouse.code,
            related_code=None if self.related_warehouse is None else self.related_warehouse.code,
            kind_label=self.movement_label(),
            description=description,
        )


class Receipt(StockMovement):
    __mapper_args__ = {"polymorphic_identity": "prijem"}

    def movement_label(self) -> str:
        return "Příjem"

    def sign(self) -> str:
        return "+"


class TransferOut(StockMovement):
    __mapper_args__ = {"polymorphic_identity": "presun_vydaj"}

    def movement_label(self) -> str:
        return "Přesun ven"

    def sign(self) -> str:
        return "−"

    def route(self) -> str:
        target = self.related_warehouse.code if self.related_warehouse is not None else ""
        return f"{self.warehouse.code} → {target}"


class TransferIn(StockMovement):
    __mapper_args__ = {"polymorphic_identity": "presun_prijem"}

    def movement_label(self) -> str:
        return "Přesun sem"

    def sign(self) -> str:
        return "+"

    def route(self) -> str:
        source = self.related_warehouse.code if self.related_warehouse is not None else ""
        return f"{source} → {self.warehouse.code}"


class InvoiceIssue(StockMovement):
    __mapper_args__ = {"polymorphic_identity": "vydej_faktura"}

    def movement_label(self) -> str:
        return "Výdej fakturou"

    def sign(self) -> str:
        return "−"
