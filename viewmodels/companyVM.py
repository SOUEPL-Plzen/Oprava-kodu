"""Dodavatel na faktuře. Patří k views/company.kv."""

from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from domain.entities import Company


class CompanyVM(EventDispatcher):
    co_name = StringProperty("")
    co_ico = StringProperty("")
    co_dic = StringProperty("")
    co_street = StringProperty("")
    co_city = StringProperty("")
    co_zip = StringProperty("")
    co_country = StringProperty("Česká republika")
    co_email = StringProperty("")
    co_phone = StringProperty("")
    co_account = StringProperty("")
    co_bank = StringProperty("")
    co_iban = StringProperty("")

    def __init__(self, shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell

    def load(self) -> None:
        company = self.shell.service.get_company()
        self.co_name = company.company_name
        self.co_ico = company.ico
        self.co_dic = company.dic
        self.co_street = company.street
        self.co_city = company.city
        self.co_zip = company.zip_code
        self.co_country = company.country
        self.co_email = company.email
        self.co_phone = company.phone
        self.co_account = company.bank_account
        self.co_bank = company.bank_code
        self.co_iban = company.iban

    def save_company(self) -> None:
        def action() -> None:
            self.shell.service.save_company(
                Company(
                    company_name=self.co_name,
                    ico=self.co_ico,
                    dic=self.co_dic,
                    street=self.co_street,
                    city=self.co_city,
                    zip_code=self.co_zip,
                    country=self.co_country,
                    email=self.co_email,
                    phone=self.co_phone,
                    bank_account=self.co_account,
                    bank_code=self.co_bank,
                    iban=self.co_iban,
                )
            )
            self.load()
            self.shell.succeed("Dodavatel byl uložen.")

        self.shell.guard(action)
