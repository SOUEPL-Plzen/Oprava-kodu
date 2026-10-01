"""Chyby domény. Uživatelský text zobrazí viewmodel."""


class AppError(Exception):
    """Chyba, kterou aplikace umí ukázat."""


class ValidationError(AppError):
    """Vstup nesplňuje pravidla skladu nebo faktury."""


class StockError(AppError):
    """Na skladě není dostatek zboží."""
