"""Session nad MySQL. Schéma zakládá SQLAlchemy z ORM tříd."""

from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from models.data import (
    CompanyProfile,
    Invoice,
    InvoiceLine,
    Party,
    Product,
    StockItem,
    StockMovement,
    Warehouse,
)
from models.data.base import Record
from domain.errors import ValidationError


class Database:
    """Jednotka práce: otevře session, po úspěchu commitne, při chybě vrátí změny."""

    def __init__(self, config: dict) -> None:
        self.config = config
        self.engine = None
        self._sessions: sessionmaker | None = None

    def initialize(self) -> None:
        name = self.config["database"]
        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            raise ValidationError("Neplatný název databáze.")
        self._create_database(name)
        if self.engine is not None:
            self.engine.dispose()
        self.engine = create_engine(self._url(name), pool_pre_ping=True, connect_args=self._connect_args())
        Record.metadata.create_all(self.engine)
        self._sessions = sessionmaker(bind=self.engine, autoflush=True, expire_on_commit=False)
        with self.session() as session:
            if session.get(CompanyProfile, 1) is None:
                session.add(CompanyProfile.empty())

    def reset_data(self) -> None:
        """Vymaže provozní data. Používají to testy, ne obrazovky aplikace."""
        with self.session() as session:
            for model in (StockMovement, InvoiceLine, Invoice, StockItem, Party, Product, Warehouse):
                session.execute(delete(model))
            company = session.get(CompanyProfile, 1)
            if company is None:
                session.add(CompanyProfile.empty())
            else:
                company.clear()

    @contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessions is None:
            raise ValidationError("Databáze není inicializovaná.")
        orm_session = self._sessions()
        try:
            yield orm_session
            orm_session.commit()
        except Exception:
            orm_session.rollback()
            raise
        finally:
            orm_session.close()

    def _create_database(self, name: str) -> None:
        engine = create_engine(self._url("mysql"), pool_pre_ping=True, connect_args=self._connect_args())
        try:
            with engine.connect() as connection:
                connection.execute(
                    text(
                        f"CREATE DATABASE IF NOT EXISTS `{name}` "
                        "CHARACTER SET utf8mb4 COLLATE utf8mb4_czech_ci"
                    )
                )
                connection.commit()
        finally:
            engine.dispose()

    def _url(self, database: str) -> URL:
        return URL.create(
            "mysql+mysqlconnector",
            username=self.config["user"],
            password=self.config["password"],
            host=self.config["host"],
            port=int(self.config["port"]),
            database=database,
        )

    @staticmethod
    def _connect_args() -> dict:
        return {"charset": "utf8mb4", "use_pure": True, "connection_timeout": 8}


def select_company(session: Session) -> CompanyProfile:
    company = session.scalar(select(CompanyProfile).where(CompanyProfile.id == 1).with_for_update())
    if company is None:
        raise ValidationError("Chybí nastavení dodavatele.")
    return company
