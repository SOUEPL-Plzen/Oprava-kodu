"""Peněžní a množstevní hodnoty. Zaokrouhlení je polovina nahoru."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from domain.errors import ValidationError


class Money:
    """Částka v korunách na dvě desetinná místa."""

    SCALE = Decimal("0.01")
    LIMIT = Decimal("99999999.99")

    def __init__(self, value: Decimal) -> None:
        amount = Decimal(value).quantize(self.SCALE, rounding=ROUND_HALF_UP)
        if amount > self.LIMIT:
            raise ValidationError("Částka je příliš vysoká.")
        self.amount = amount

    def format(self) -> str:
        sign = "-" if self.amount < 0 else ""
        whole, fraction = f"{abs(self.amount):.2f}".split(".")
        groups: list[str] = []
        while whole:
            groups.append(whole[-3:])
            whole = whole[:-3]
        return f"{sign}{' '.join(reversed(groups))},{fraction}"

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)


class Quantity:
    """Množství na tři desetinná místa."""

    SCALE = Decimal("0.001")
    LIMIT = Decimal("999999.999")

    def __init__(self, value: Decimal) -> None:
        amount = Decimal(value).quantize(self.SCALE, rounding=ROUND_HALF_UP)
        if amount > self.LIMIT:
            raise ValidationError("Množství je příliš velké.")
        self.amount = amount

    def format(self) -> str:
        text = f"{self.amount:.3f}".rstrip("0").rstrip(".")
        return text.replace(".", ",")


class VatBreakdown:
    """Základ, daň a částka s DPH jednoho řádku."""

    def __init__(self, net: Money, vat: Money, gross: Money) -> None:
        self.net = net
        self.vat = vat
        self.gross = gross

    @classmethod
    def from_line(cls, quantity: Decimal, unit_price: Decimal, vat_rate: Decimal) -> "VatBreakdown":
        net = Money(quantity * unit_price)
        vat = Money(net.amount * vat_rate / Decimal(100))
        gross = Money(net.amount + vat.amount)
        return cls(net, vat, gross)
