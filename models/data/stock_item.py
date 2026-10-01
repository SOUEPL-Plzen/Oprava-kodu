"""Tabulka stock."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.data.base import Entity, table_args
from models.data.product import Product
from models.data.warehouse import Warehouse
from domain.money import Quantity


class StockItem(Entity):
    __tablename__ = "stock"
    __table_args__ = table_args(
        UniqueConstraint("product_id", "warehouse_id", name="uq_stock_item"),
        CheckConstraint("quantity >= 0", name="chk_stock_quantity"),
    )

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0"), server_default="0")
    product: Mapped[Product] = relationship(back_populates="stocks")
    warehouse: Mapped[Warehouse] = relationship()

    def increase(self, quantity: Decimal) -> None:
        self.quantity = Quantity(self.quantity + quantity).amount

    def decrease(self, quantity: Decimal) -> None:
        from domain.errors import StockError

        if quantity > self.quantity:
            raise StockError(
                f"Na skladě {self.warehouse.code} je {Quantity(self.quantity).format()} "
                f"{self.product.unit} zboží {self.product.sku}."
            )
        self.quantity = Quantity(self.quantity - quantity).amount

    def to_dto(self):
        from domain.entities import StockCard

        return StockCard(
            product_id=self.product_id,
            warehouse_id=self.warehouse_id,
            quantity=Quantity(self.quantity).amount,
            sku=self.product.sku,
            product_name=self.product.name,
            unit=self.product.unit,
            warehouse_code=self.warehouse.code,
            warehouse_name=self.warehouse.name,
        )
