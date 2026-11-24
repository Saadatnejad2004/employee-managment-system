"""Reporting queries, kept out of the views so they can be tested without HTTP."""

from django.db.models import Avg, Count, Q, Sum
from django.db.models.functions import Coalesce

from .models import Department, Employee

# Statuses that count towards headcount and payroll. Terminated staff are
# kept as records (history) but are no longer paid.
PAYABLE_STATUSES = ("active", "on_leave")


def company_summary():
    """Headcount and payroll figures in ONE query. Money values are cents."""
    payable = Q(status__in=PAYABLE_STATUSES)
    summary = Employee.objects.aggregate(
        headcount=Count("pk", filter=payable),
        active=Count("pk", filter=Q(status="active")),
        payroll_cents=Coalesce(Sum("salary_cents", filter=payable), 0),
        avg_salary_cents=Coalesce(Avg("salary_cents", filter=payable), 0.0),
    )
    return summary


def department_breakdown():
    """Per-department headcount and payroll in ONE query (LEFT JOIN + GROUP BY)."""
    payable = Q(employees__status__in=PAYABLE_STATUSES)
    return Department.objects.annotate(
        emp_count=Count("employees", filter=payable),
        dept_payroll=Coalesce(Sum("employees__salary_cents", filter=payable), 0),
    ).order_by("-emp_count", "name")
