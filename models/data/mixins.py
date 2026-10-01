"""Sdílené části tabulek. Nejsou to samostatné tabulky, skládají se do entit."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class AddressMixin:
    """Ulice, město, PSČ, stát a kontakt."""

    street: Mapped[str] = mapped_column(String(255), default="", server_default="")
    city: Mapped[str] = mapped_column(String(128), default="", server_default="")
    zip_code: Mapped[str] = mapped_column(String(16), default="", server_default="")
    country: Mapped[str] = mapped_column(String(64), default="", server_default="")
    email: Mapped[str] = mapped_column(String(255), default="", server_default="")
    phone: Mapped[str] = mapped_column(String(32), default="", server_default="")


class OrganizationMixin:
    """Název, IČO a DIČ. Používá je dodavatel i odběratel."""

    company_name: Mapped[str] = mapped_column(String(255), default="", server_default="")
    ico: Mapped[str] = mapped_column(String(16), default="", server_default="")
    dic: Mapped[str] = mapped_column(String(20), default="", server_default="")
