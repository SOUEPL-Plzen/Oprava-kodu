"""Společné stavební prvky obrazovek."""

from __future__ import annotations

from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import ListProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

TEXT = (0.12, 0.16, 0.22, 1)
MUTED = (0.35, 0.42, 0.51, 1)
NAVY = (0.09, 0.16, 0.27, 1)
PRIMARY = (0.15, 0.39, 0.85, 1)
OK_COLOR = (0.09, 0.42, 0.30, 1)
DANGER = (0.70, 0.16, 0.14, 1)
BG = (0.94, 0.95, 0.97, 1)
WHITE = (1, 1, 1, 1)
HEADER_BG = (0.90, 0.93, 0.96, 1)
ZEBRA = (0.96, 0.97, 0.98, 1)


def paint(widget, rgba, radius: int = 0) -> None:
    with widget.canvas.before:
        Color(*rgba)
        shape = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius]) if radius else Rectangle(
            pos=widget.pos, size=widget.size
        )
    widget.bind(pos=lambda _w, pos: setattr(shape, "pos", pos), size=lambda _w, size: setattr(shape, "size", size))


def fit_left(label: Label) -> None:
    label.bind(size=lambda widget, _size: setattr(widget, "text_size", (widget.width, widget.height)))


class Card(BoxLayout):
    """Karta. Vzhled je v KV."""


class DataTable(BoxLayout):
    """Tabulka. Sloupce a řádky přijdou z KV, vykreslení je v ovládacím prvku."""

    headers = StringProperty("")
    rows = ListProperty([])
    empty_text = StringProperty("Zatím tu nic není.")

    def __init__(self, **kwargs) -> None:
        super().__init__(orientation="vertical", size_hint_y=None, spacing=2, **kwargs)
        self.bind(minimum_height=self.setter("height"))
        self.bind(headers=self._refresh, rows=self._refresh, empty_text=self._refresh)

    def _columns(self) -> list[tuple[str, str, float]]:
        columns = []
        for part in self.headers.split(";"):
            if not part.strip():
                continue
            key, title, weight = part.split("|")
            columns.append((key, title, float(weight)))
        return columns

    def _refresh(self, *_args) -> None:
        columns = self._columns()
        if not columns:
            return
        self.clear_widgets()
        self.add_widget(self._line([title for _key, title, _weight in columns], HEADER_BG, MUTED, bold=True))
        if not self.rows:
            note = Label(
                text=self.empty_text,
                color=MUTED,
                font_size=14,
                size_hint_y=None,
                height=36,
                halign="left",
                valign="middle",
            )
            fit_left(note)
            self.add_widget(note)
            return
        for index, row in enumerate(self.rows):
            values = [str(row.get(key, "")) for key, _title, _weight in columns]
            self.add_widget(self._line(values, ZEBRA if index % 2 == 0 else WHITE, TEXT, bold=False))

    def _line(self, values: list[str], background, color, bold: bool) -> BoxLayout:
        row = BoxLayout(size_hint_y=None, height=38, spacing=8, padding=(8, 0))
        paint(row, background)
        for (_key, _title, weight), value in zip(self._columns(), values):
            label = Label(
                text=value,
                color=color,
                bold=bold,
                font_size=14,
                halign="left",
                valign="middle",
                shorten=True,
                shorten_from="right",
                size_hint_x=weight,
            )
            fit_left(label)
            row.add_widget(label)
        return row


def caption(text: str) -> Label:
    label = Label(text=text, color=MUTED, font_size=13, halign="left", valign="middle", size_hint_y=None, height=18)
    fit_left(label)
    return label


def text_input(hint: str = "", multiline: bool = False) -> TextInput:
    return TextInput(
        hint_text=hint,
        multiline=multiline,
        write_tab=not multiline,
        font_size=15,
        padding=[10, 10, 10, 8],
        background_normal="",
        background_active="",
        background_color=(0.965, 0.973, 0.982, 1),
        foreground_color=TEXT,
        hint_text_color=(0.55, 0.60, 0.66, 1),
        cursor_color=TEXT,
        selection_color=(0.15, 0.39, 0.85, 0.28),
    )


def bind_text(vm, prop: str, hint: str = "", multiline: bool = False) -> TextInput:
    editor = text_input(hint, multiline)
    editor.text = getattr(vm, prop)
    editor.bind(text=vm.setter(prop))
    vm.bind(**{prop: editor.setter("text")})
    return editor


def field(title: str, editor, height: int = 68) -> BoxLayout:
    box = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None, height=height)
    box.add_widget(caption(title))
    editor.size_hint_y = None
    editor.height = height - 24
    box.add_widget(editor)
    return box


def pair(left, right) -> BoxLayout:
    row = BoxLayout(size_hint_y=None, height=left.height, spacing=12)
    row.add_widget(left)
    row.add_widget(right)
    return row


def choice_spinner(owner, prop: str, choices_owner, choices_prop: str) -> Spinner:
    """Výběr drží formulář, seznam voleb drží kořenový viewmodel."""
    spinner = Spinner(
        text=getattr(owner, prop),
        values=list(getattr(choices_owner, choices_prop)),
        size_hint_y=None,
        height=42,
        font_size=15,
    )
    spinner.bind(text=owner.setter(prop))
    owner.bind(**{prop: spinner.setter("text")})

    def sync_values(_instance, values, widget=spinner) -> None:
        widget.values = list(values)

    choices_owner.bind(**{choices_prop: sync_values})
    return spinner


def option_spinner(vm, prop: str, values_prop: str) -> Spinner:
    spinner = Spinner(
        text=getattr(vm, prop),
        values=list(getattr(vm, values_prop)),
        size_hint_y=None,
        height=42,
        font_size=15,
    )
    spinner.bind(text=vm.setter(prop))
    vm.bind(**{prop: spinner.setter("text")})
    return spinner


def action_button(text: str, callback, color=PRIMARY, width: int = 280) -> Button:
    button = Button(
        text=text,
        size_hint=(None, None),
        size=(width, 44),
        background_normal="",
        background_color=color,
        color=WHITE,
        bold=True,
        font_size=15,
    )
    button.bind(on_release=lambda *_args: callback())
    return button


def button_row(button: Button) -> BoxLayout:
    row = BoxLayout(size_hint_y=None, height=48)
    row.add_widget(button)
    row.add_widget(Widget())
    return row


def section_title(text: str) -> Label:
    label = Label(text=text, color=TEXT, font_size=16, bold=True, halign="left", valign="middle", size_hint_y=None, height=26)
    fit_left(label)
    return label


def info_label(text: str) -> Label:
    label = Label(text=text, color=MUTED, font_size=14, halign="left", valign="middle", size_hint_y=None, height=24)
    fit_left(label)
    return label


def scroll_body() -> tuple:
    from kivy.uix.scrollview import ScrollView

    content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=12, padding=(16, 16, 16, 20))
    content.bind(minimum_height=content.setter("height"))
    scroll = ScrollView(do_scroll_x=False, bar_width=8)
    scroll.add_widget(content)
    return scroll, content


class DraftBoard(BoxLayout):
    """Seznam položek faktury. Řádek kreslí KV šablona."""

    items = ListProperty([])
    empty_text = StringProperty("Na faktuře zatím není žádná položka.")

    def __init__(self, **kwargs) -> None:
        super().__init__(orientation="vertical", size_hint_y=None, spacing=4, **kwargs)
        self.bind(minimum_height=self.setter("height"))
        self.bind(items=self._refresh, empty_text=self._refresh)

    def _refresh(self, *_args) -> None:
        from views.templates import DraftLineView

        self.clear_widgets()
        if not self.items:
            note = Label(text=self.empty_text, color=MUTED, font_size=14, size_hint_y=None, height=24, halign="left", valign="middle")
            fit_left(note)
            self.add_widget(note)
            return
        for index, line in enumerate(self.items):
            self.add_widget(
                DraftLineView(
                    index=index,
                    title=str(line.get("title", "")),
                    warehouse=str(line.get("warehouse", "")),
                    quantity_label=str(line.get("quantity_label", "")),
                    unit=str(line.get("unit", "")),
                    price_label=str(line.get("price_label", "")),
                    gross_label=str(line.get("gross_label", "")),
                )
            )


class InvoiceBoard(BoxLayout):
    """Seznam faktur. Řádek kreslí KV šablona."""

    items = ListProperty([])
    empty_text = StringProperty("Zatím nebyla vystavená žádná faktura.")

    def __init__(self, **kwargs) -> None:
        super().__init__(orientation="vertical", size_hint_y=None, spacing=4, **kwargs)
        self.bind(minimum_height=self.setter("height"))
        self.bind(items=self._refresh, empty_text=self._refresh)

    def _refresh(self, *_args) -> None:
        from views.templates import InvoiceRowView

        self.clear_widgets()
        if not self.items:
            note = Label(text=self.empty_text, color=MUTED, font_size=14, size_hint_y=None, height=24, halign="left", valign="middle")
            fit_left(note)
            self.add_widget(note)
            return
        for index, invoice in enumerate(self.items):
            self.add_widget(
                InvoiceRowView(
                    index=index,
                    invoice_id=int(invoice.get("id", 0)),
                    number=str(invoice.get("number", "")),
                    issued=str(invoice.get("issued", "")),
                    buyer=str(invoice.get("buyer", "")),
                    total=str(invoice.get("total", "")),
                    payment=str(invoice.get("payment", "")),
                )
            )
