"""Tabulka invoices."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy import Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.data.base import Entity, Timestamped, table_args
from models.data.company_profile import CompanyProfile
from models.data.party import Party
from domain.money import Money


class Invoice(Timestamped, Entity):
    __tablename__ = "invoices"
    __table_args__ = table_args(UniqueConstraint("invoice_number", name="uq_invoices_number"))

    invoice_number: Mapped[str] = mapped_column(String(32))
    issued_on: Mapped[date] = mapped_column(Date)
    taxable_on: Mapped[date] = mapped_column(Date)
    due_on: Mapped[date] = mapped_column(Date)
    payment_method: Mapped[str] = mapped_column(String(64))
    variable_symbol: Mapped[str] = mapped_column(String(10), default="", server_default="")
    note: Mapped[str] = mapped_column(String(2000), default="", server_default="")
    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id"))
    total_net: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_vat: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total_gross: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    supplier_name: Mapped[str] = mapped_column(String(255))
    supplier_ico: Mapped[str] = mapped_column(String(16), default="", server_default="")
    supplier_dic: Mapped[str] = mapped_column(String(20), default="", server_default="")
    supplier_street: Mapped[str] = mapped_column(String(255), default="", server_default="")
    supplier_city: Mapped[str] = mapped_column(String(128), default="", server_default="")
    supplier_zip: Mapped[str] = mapped_column(String(16), default="", server_default="")
    supplier_country: Mapped[str] = mapped_column(String(64), default="", server_default="")
    supplier_email: Mapped[str] = mapped_column(String(255), default="", server_default="")
    supplier_phone: Mapped[str] = mapped_column(String(32), default="", server_default="")
    supplier_account: Mapped[str] = mapped_column(String(64), default="", server_default="")
    supplier_bank: Mapped[str] = mapped_column(String(8), default="", server_default="")
    supplier_iban: Mapped[str] = mapped_column(String(42), default="", server_default="")
    buyer: Mapped[Party] = relationship()
    lines: Mapped[List["InvoiceLine"]] = relationship(
        back_populates="invoice",
        order_by="InvoiceLine.id",
        cascade="all, delete-orphan",
    )

    def snapshot_supplier(self, company: CompanyProfile) -> None:
        self.supplier_name = company.company_name
        self.supplier_ico = company.ico
        self.supplier_dic = company.dic
        self.supplier_street = company.street
        self.supplier_city = company.city
        self.supplier_zip = company.zip_code
        self.supplier_country = company.country
        self.supplier_email = company.email
        self.supplier_phone = company.phone
        self.supplier_account = company.bank_account
        self.supplier_bank = company.bank_code
        self.supplier_iban = company.iban

    def supplier_card(self):
        from domain.entities import SupplierCard

        return SupplierCard(
            company_name=self.supplier_name,
            ico=self.supplier_ico,
            dic=self.supplier_dic,
            street=self.supplier_street,
            city=self.supplier_city,
            zip_code=self.supplier_zip,
            country=self.supplier_country,
            email=self.supplier_email,
            phone=self.supplier_phone,
            bank_account=self.supplier_account,
            bank_code=self.supplier_bank,
            iban=self.supplier_iban,
        )

    def to_summary(self):
        from domain.entities import InvoiceSummary

        return InvoiceSummary(
            id=self.id,
            invoice_number=self.invoice_number,
            issued_on=self.issued_on,
            total_gross=Money(self.total_gross).amount,
            payment_method=self.payment_method,
            buyer_name=self.buyer.to_dto().display_name(),
        )

    def to_detail(self):
        from domain.entities import InvoiceDetail

        return InvoiceDetail(
            id=self.id,
            invoice_number=self.invoice_number,
            issued_on=self.issued_on,
            taxable_on=self.taxable_on,
            due_on=self.due_on,
            payment_method=self.payment_method,
            variable_symbol=self.variable_symbol,
            note=self.note,
            total_net=Money(self.total_net).amount,
            total_vat=Money(self.total_vat).amount,
            total_gross=Money(self.total_gross).amount,
            supplier=self.supplier_card(),
            buyer=self.buyer.to_dto(),
            lines=[line.to_dto() for line in self.lines],
        )
