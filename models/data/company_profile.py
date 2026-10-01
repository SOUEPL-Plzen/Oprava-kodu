"""Tabulka company_settings. Jeden řádek, dodavatel na fakturách."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column  # bank fields below use String

from models.data.base import Record, table_args
from models.data.mixins import AddressMixin, OrganizationMixin


class CompanyProfile(AddressMixin, OrganizationMixin, Record):
    __tablename__ = "company_settings"
    __table_args__ = table_args()

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    bank_account: Mapped[str] = mapped_column(String(64), default="", server_default="")
    bank_code: Mapped[str] = mapped_column(String(8), default="", server_default="")
    iban: Mapped[str] = mapped_column(String(42), default="", server_default="")

    @classmethod
    def empty(cls) -> "CompanyProfile":
        return cls(id=1, company_name="", country="Česká republika")

    def copy_from(self, company) -> None:
        self.company_name = company.company_name
        self.ico = company.ico
        self.dic = company.dic
        self.street = company.street
        self.city = company.city
        self.zip_code = company.zip_code
        self.country = company.country
        self.email = company.email
        self.phone = company.phone
        self.bank_account = company.bank_account
        self.bank_code = company.bank_code
        self.iban = company.iban

    def clear(self) -> None:
        from domain.entities import SupplierCard

        self.copy_from(
            SupplierCard(
                company_name="",
                ico="",
                dic="",
                street="",
                city="",
                zip_code="",
                country="Česká republika",
                email="",
                phone="",
                bank_account="",
                bank_code="",
                iban="",
            )
        )

    def to_dto(self):
        from domain.entities import SupplierCard

        return SupplierCard(
            company_name=self.company_name,
            ico=self.ico,
            dic=self.dic,
            street=self.street,
            city=self.city,
            zip_code=self.zip_code,
            country=self.country or "Česká republika",
            email=self.email,
            phone=self.phone,
            bank_account=self.bank_account,
            bank_code=self.bank_code,
            iban=self.iban,
        )
