"""Kontrola vstupů z formulářů."""

from __future__ import annotations

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from domain.errors import ValidationError
from domain.money import Money, Quantity


class Catalogue:
    UNITS = ("ks", "kg", "g", "m", "m²", "l", "bal")
    VAT_RATES = (Decimal("21"), Decimal("12"), Decimal("0"))
    PAYMENT_METHODS = ("bankovní převod", "hotovost", "platební karta", "dobírka")


class Field:
    """Textové pole s délkou a povinností."""

    def __init__(self, value: str, label: str, max_len: int, required: bool = False) -> None:
        self.text = value.strip()
        if required and not self.text:
            raise ValidationError(f"Vyplňte pole {label}.")
        if len(self.text) > max_len:
            raise ValidationError(f"Pole {label} může mít nejvýše {max_len} znaků.")

    @classmethod
    def read(cls, value: str, label: str, max_len: int, required: bool = False) -> str:
        return cls(value, label, max_len, required).text


class Ico:
    """České IČO včetně kontrolního součtu."""

    def __init__(self, raw: str) -> None:
        self.value = raw.strip().replace(" ", "")

    def is_valid(self) -> bool:
        if not re.fullmatch(r"\d{8}", self.value):
            return False
        total = sum(int(digit) * weight for digit, weight in zip(self.value[:7], (8, 7, 6, 5, 4, 3, 2)))
        remainder = total % 11
        if remainder == 0:
            check = 1
        elif remainder == 1:
            check = 0
        else:
            check = 11 - remainder
        return check == int(self.value[7])


class Dic:
    def __init__(self, raw: str) -> None:
        self.value = raw.strip().replace(" ", "").upper()

    def is_valid(self) -> bool:
        return re.fullmatch(r"CZ\d{8,10}", self.value) is not None


class EmailAddress:
    def __init__(self, raw: str) -> None:
        self.value = Field(raw, "E-mail", 255, required=False).text
        if self.value and "@" not in self.value:
            raise ValidationError("E-mail nemá platný tvar.")


class PostalCode:
    _CZECH = {"česká republika", "ceska republika", "česko", "cesko", "cz", "czech republic"}

    def __init__(self, raw: str, country: str) -> None:
        text = Field(raw, "PSČ", 16, required=True).text
        if country.casefold() not in self._CZECH:
            self.value = text
            return
        compact = text.replace(" ", "")
        if not re.fullmatch(r"\d{5}", compact):
            raise ValidationError("PSČ v České republice zadejte jako 5 číslic.")
        self.value = f"{compact[:3]} {compact[3:]}"


class DecimalField:
    def __init__(self, value: str, label: str, *, positive: bool = False, non_negative: bool = False) -> None:
        text = value.strip().replace(" ", "").replace(",", ".")
        if not text:
            raise ValidationError(f"Vyplňte pole {label}.")
        try:
            number = Decimal(text)
        except InvalidOperation:
            raise ValidationError(f"Pole {label} musí být číslo.") from None
        if not number.is_finite():
            raise ValidationError(f"Pole {label} musí být číslo.")
        if positive and number <= 0:
            raise ValidationError(f"Pole {label} musí být větší než nula.")
        if non_negative and number < 0:
            raise ValidationError(f"Pole {label} nesmí být záporné.")
        self.amount = number


class QuantityField(DecimalField):
    def __init__(self, value: str) -> None:
        super().__init__(value, "Množství", positive=True)
        quantity = Quantity(self.amount)
        if quantity.amount <= 0:
            raise ValidationError("Pole Množství musí být větší než nula.")
        self.amount = quantity.amount


class PriceField(DecimalField):
    def __init__(self, value: str) -> None:
        super().__init__(value, "Cena bez DPH", non_negative=True)
        self.amount = Money(self.amount).amount


class DateField:
    def __init__(self, value: str, label: str) -> None:
        text = value.strip()
        if not text:
            raise ValidationError(f"Vyplňte pole {label}.")
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d. %m. %Y"):
            try:
                self.value = datetime.strptime(text, fmt).date()
                return
            except ValueError:
                continue
        raise ValidationError(f"Pole {label} zadejte jako RRRR-MM-DD nebo DD.MM.RRRR.")


class ChoiceId:
    _PATTERN = re.compile(r"^#(\d+)\b")

    def __init__(self, label: str) -> None:
        match = self._PATTERN.match(label.strip())
        self.value = int(match.group(1)) if match else None

    def require(self, message: str) -> int:
        if self.value is None:
            raise ValidationError(message)
        return self.value
