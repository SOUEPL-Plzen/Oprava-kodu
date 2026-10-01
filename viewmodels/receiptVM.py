"""Příjem na sklad. Patří k views/receipt.kv."""

from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from domain.validation import ChoiceId, QuantityField

CHOOSE_PRODUCT = "Vyberte zboží"
CHOOSE_WAREHOUSE = "Vyberte sklad"


class ReceiptVM(EventDispatcher):
    rc_product = StringProperty(CHOOSE_PRODUCT)
    rc_warehouse = StringProperty(CHOOSE_WAREHOUSE)
    rc_qty = StringProperty("")
    rc_note = StringProperty("")

    def __init__(self, shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell

    def receive(self) -> None:
        def action() -> None:
            self.shell.service.receive(
                ChoiceId(self.rc_product).require("Vyberte zboží."),
                ChoiceId(self.rc_warehouse).require("Vyberte sklad."),
                QuantityField(self.rc_qty).amount,
                self.rc_note,
            )
            self.rc_qty = ""
            self.rc_note = ""
            self.shell.reload_lists()
            self.shell.succeed("Příjem na sklad byl uložen.")

        self.shell.guard(action)
