"""Řádkové šablony. Mají jen vlastnosti, vzhled je v KV."""

from __future__ import annotations

from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout


class DraftLineView(BoxLayout):
    index = NumericProperty(0)
    title = StringProperty("")
    warehouse = StringProperty("")
    quantity_label = StringProperty("")
    unit = StringProperty("")
    price_label = StringProperty("")
    gross_label = StringProperty("")


class InvoiceRowView(BoxLayout):
    index = NumericProperty(0)
    invoice_id = NumericProperty(0)
    number = StringProperty("")
    issued = StringProperty("")
    buyer = StringProperty("")
    total = StringProperty("")
    payment = StringProperty("")
