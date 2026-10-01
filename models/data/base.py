"""Společný základ tabulek. Konkrétní tabulka z něj dědí."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

MYSQL = {
    "mysql_engine": "InnoDB",
    "mysql_charset": "utf8mb4",
    "mysql_collate": "utf8mb4_czech_ci",
}


class Record(DeclarativeBase):
    """Abstraktní ORM záznam. Žádná tabulka mu nepatří."""

    __abstract__ = True


class Entity(Record):
    """Tabulka s číselným primárním klíčem."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Timestamped:
    """Část tabulky: okamžik vzniku řádku."""

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, server_default=func.now())


def table_args(*constraints) -> tuple:
    if not constraints:
        return (MYSQL,)
    return (*constraints, MYSQL)
