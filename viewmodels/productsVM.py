"""Formulář zboží. Patří k views/products.kv."""

from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty

from domain.money import Money
from domain.validation import Catalogue, DecimalField, PriceField


class ProductsVM(EventDispatcher):
    rows = ListProperty([])
    pr_sku = StringProperty("")
    pr_name = StringProperty("")
    pr_unit = StringProperty("ks")
    pr_price = StringProperty("")
    pr_vat = StringProperty("21")
    units = ListProperty(list(Catalogue.UNITS))
    vat_rates = ListProperty(["21", "12", "0"])

    def __init__(self, shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell

    def add_product(self) -> None:
        def action() -> None:
            self.shell.service.add_product(
                self.pr_sku,
                self.pr_name,
                self.pr_unit,
                PriceField(self.pr_price).amount,
                Money(DecimalField(self.pr_vat, "DPH", non_negative=True).amount).amount,
            )
            self.pr_sku = ""
            self.pr_name = ""
            self.pr_price = ""
            self.shell.reload_lists()
            self.shell.succeed("Zboží bylo uloženo.")

        self.shell.guard(action)
