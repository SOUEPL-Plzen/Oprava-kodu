"""Okno aplikace. Rozložení je ve views/shell.kv."""

from __future__ import annotations

from pathlib import Path

from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView

import views.templates
import views.widgets
from kivy.lang import Builder


class ShellView(BoxLayout):
    detail_token = NumericProperty(0)


_KV = Path(__file__).resolve().parent
for _name in (
    "theme.kv",
    "overview.kv",
    "warehouses.kv",
    "products.kv",
    "receipt.kv",
    "transfer.kv",
    "issue.kv",
    "invoices.kv",
    "company.kv",
    "shell.kv",
):
    Builder.load_file(str(_KV / _name))
