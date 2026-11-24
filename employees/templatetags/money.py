from django import template

from employees.money import format_money

register = template.Library()


@register.filter
def money(cents):
    """Render an amount stored in cents as dollars: {{ emp.salary_cents|money }}."""
    return format_money(cents)
