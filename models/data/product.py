"""Tabulka products."""

from __future__ import annotations

from decimal import Decimal
from typing import List

from sqlalchemy import Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.data.base import Entity, Timestamped, table_args
from domain.money import Money, Quantity


class Product(Timestamped, Entity):
    __tablename__ = "products"
    __table_args__ = table_args(UniqueConstraint("sku", name="uq_products_sku"))

    sku: Mapped[str] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(255))
    unit: Mapped[str] = mapped_column(String(16))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    vat_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    stocks: Mapped[List["StockItem"]] = relationship(back_populates="product")

    @property
    def stock_qty(self) -> Decimal:
        return sum((item.quantity for item in self.stocks), Decimal(0))

    def to_dto(self):
        from domain.entities import ProductCard

        return ProductCard(
            id=self.id,
            sku=self.sku,
            name=self.name,
            unit=self.unit,
            unit_price=Money(self.unit_price).amount,
            vat_rate=Money(self.vat_rate).amount,
            stock_qty=Quantity(self.stock_qty).amount,
        )
