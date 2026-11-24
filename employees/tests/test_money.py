from decimal import Decimal

import pytest
from django.template import Context, Template

from employees.money import cents_to_dollars, dollars_to_cents, format_money


@pytest.mark.parametrize(
    ("cents", "expected"),
    [
        (5_000_000, "$50,000.00"),
        (0, "$0.00"),
        (None, "$0.00"),
        (5, "$0.05"),
        (5_000_000.4, "$50,000.00"),
    ],
)
def test_format_money(cents, expected):
    assert format_money(cents) == expected


def test_conversions_round_half_up():
    assert cents_to_dollars(1) == Decimal("0.01")
    assert dollars_to_cents(Decimal("50000.00")) == 5_000_000
    assert dollars_to_cents(Decimal("0.145")) == 15  # not banker's rounding


def test_money_template_filter():
    html = Template("{% load money %}{{ value|money }}").render(Context({"value": 123_456}))
    assert html == "$1,234.56"
