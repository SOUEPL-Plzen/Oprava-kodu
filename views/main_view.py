"""Spuštění okna. Obrazovky jsou v KV, stav ve viewmodelech."""

from __future__ import annotations

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.label import Label

from views.shell import ShellView
from views.widgets import BG, DANGER


class SkladApp(App):
    vm = ObjectProperty(None, allownone=True)

    def __init__(self, viewmodel=None, startup_error: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.vm = viewmodel
        self.startup_error = startup_error
        self.title = "Skladová karta"

    def build(self):
        Window.clearcolor = BG
        if self.startup_error or self.vm is None:
            label = Label(text=self.startup_error or "Aplikaci se nepodařilo spustit.", color=DANGER, font_size=18, halign="center", valign="middle")
            label.bind(size=label.setter("text_size"))
            return label
        return ShellView()
