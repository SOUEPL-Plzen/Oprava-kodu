"""Společné chování viewmodelů."""

from __future__ import annotations

import traceback

from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty, StringProperty

from domain.errors import AppError


class ViewModel(EventDispatcher):
    """Základ obrazovky: hláška a zachycení chyb domény."""

    message = StringProperty("")
    message_is_error = BooleanProperty(False)

    def succeed(self, text: str) -> None:
        self.message_is_error = False
        self.message = text

    def guard(self, action) -> None:
        try:
            action()
        except AppError as exc:
            self.message_is_error = True
            self.message = str(exc)
        except Exception as exc:
            traceback.print_exc()
            self.message_is_error = True
            self.message = f"Neočekávaná chyba: {exc}"
