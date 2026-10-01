"""Přesun mezi sklady. Patří k views/transfer.kv."""

from __future__ import annotations

from decimal import Decimal

from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from domain.money import Quantity
from domain.validation import ChoiceId, QuantityField

CHOOSE_PRODUCT = "Vyberte zboží"
CHOOSE_WAREHOUSE = "Vyberte sklad"


class TransferVM(EventDispatcher):
    tr_product = StringProperty(CHOOSE_PRODUCT)
    tr_from = StringProperty(CHOOSE_WAREHOUSE)
    tr_to = StringProperty(CHOOSE_WAREHOUSE)
    tr_qty = StringProperty("")
    tr_note = StringProperty("")
    tr_available = StringProperty("Skladem: —")

    def __init__(self, shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell

    def transfer(self) -> None:
        def action() -> None:
            self.shell.service.transfer(
                ChoiceId(self.tr_product).require("Vyberte zboží."),
                ChoiceId(self.tr_from).require("Vyberte zdrojový sklad."),
                ChoiceId(self.tr_to).require("Vyberte cílový sklad."),
                QuantityField(self.tr_qty).amount,
                self.tr_note,
            )
            self.tr_qty = ""
            self.tr_note = ""
            self.shell.reload_lists()
            self.shell.succeed("Zboží bylo přesunuto.")

        self.shell.guard(action)

    def refresh_available(self) -> None:
        self.tr_available = availability(self.shell, self.tr_product, self.tr_from)


def availability(shell, product_label: str, warehouse_label: str) -> str:
    product_id = ChoiceId(product_label).value
    warehouse_id = ChoiceId(warehouse_label).value
    if product_id is None or warehouse_id is None:
        return "Skladem: —"
    product = shell.find_product(product_id)
    row = shell.stock_index.get((product_id, warehouse_id))
    quantity = Decimal(0) if row is None else row.quantity
    unit = product["unit"] if product else ""
    return f"Skladem: {Quantity(quantity).format()} {unit}".rstrip()
