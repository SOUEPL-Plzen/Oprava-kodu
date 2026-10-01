"""Formulář skladu. Patří k views/warehouses.kv."""

from __future__ import annotations

from kivy.event import EventDispatcher
from kivy.properties import ListProperty, StringProperty


class WarehousesVM(EventDispatcher):
    rows = ListProperty([])
    wh_code = StringProperty("")
    wh_name = StringProperty("")
    wh_address = StringProperty("")

    def __init__(self, shell, **kwargs) -> None:
        super().__init__(**kwargs)
        self.shell = shell

    def add_warehouse(self) -> None:
        def action() -> None:
            self.shell.service.add_warehouse(self.wh_code, self.wh_name, self.wh_address)
            self.wh_code = ""
            self.wh_name = ""
            self.wh_address = ""
            self.shell.reload_lists()
            self.shell.succeed("Sklad byl uložen.")

        self.shell.guard(action)
