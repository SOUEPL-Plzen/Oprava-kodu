"""Tabulka warehouses."""

from __future__ import annotations

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.data.base import Entity, Timestamped, table_args


class Warehouse(Timestamped, Entity):
    __tablename__ = "warehouses"
    __table_args__ = table_args(UniqueConstraint("code", name="uq_warehouses_code"))

    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(512), default="", server_default="")

    def to_dto(self):
        from domain.entities import WarehouseCard

        return WarehouseCard(id=self.id, code=self.code, name=self.name, address=self.address)
