"""Money helpers. The database stores integer cents; people think in dollars."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
MAX_CENTS = 2_147_483_647  # ceiling of PositiveIntegerField on every supported DB


def cents_to_dollars(cents):
    """5000000 -> Decimal('50000.00'). Accepts None/float (e.g. an Avg())."""
    return (Decimal(str(cents or 0)) / 100).quantize(CENT, rounding=ROUND_HALF_UP)


def dollars_to_cents(dollars):
    """Decimal('50000.00') -> 5000000, rounded half-up to the cent."""
    return int((Decimal(dollars) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def format_money(cents):
    """5000000 -> '$50,000.00'."""
    return f"${cents_to_dollars(cents):,.2f}"
