"""Spuštění skladové karty: python main.py"""

from __future__ import annotations

import logging
import os
import traceback

logging.getLogger("mysql.connector").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.config import Config

Config.set("graphics", "width", "1280")
Config.set("graphics", "height", "820")
Config.set("graphics", "minimum_width", "1100")
Config.set("graphics", "minimum_height", "700")
Config.set("input", "mouse", "mouse,multitouch_on_demand")
Config.set("kivy", "log_level", "warning")

from kivy.core.text import LabelBase

_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
_FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
_FONT_ITALIC = "/System/Library/Fonts/Supplemental/Arial Italic.ttf"
_FONT_BOLD_ITALIC = "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"
if os.path.exists(_FONT):
    LabelBase.register(
        name="Roboto",
        fn_regular=_FONT,
        fn_bold=_FONT_BOLD if os.path.exists(_FONT_BOLD) else _FONT,
        fn_italic=_FONT_ITALIC if os.path.exists(_FONT_ITALIC) else _FONT,
        fn_bolditalic=_FONT_BOLD_ITALIC if os.path.exists(_FONT_BOLD_ITALIC) else _FONT,
    )

from config import DB_CONFIG
from domain.database import Database
from domain.inventory_service import InventoryService
from viewmodels.shellVM import ShellVM
from views.main_view import SkladApp


def create_app() -> SkladApp:
    try:
        database = Database(DB_CONFIG)
        database.initialize()
        viewmodel = ShellVM(InventoryService(database))
        return SkladApp(viewmodel)
    except Exception as exc:
        traceback.print_exc()
        return SkladApp(None, startup_error=f"Nepodařilo se otevřít databázi.\n{exc}")


def main() -> None:
    create_app().run()


if __name__ == "__main__":
    main()
