import pytest
from django.urls import reverse

from employees.models import Employee
from employees.reports import company_summary, department_breakdown

pytestmark = pytest.mark.django_db


def test_terminated_staff_are_excluded_from_payroll_and_headcount(hr, mgr, peer, outsider):
    outsider.status = "terminated"
    outsider.save()
    peer.status = "on_leave"
    peer.save()

    summary = company_summary()

    assert summary["headcount"] == 3  # on-leave staff still count
    assert summary["active"] == 2
    assert summary["payroll_cents"] == 9_000_000 + 7_000_000 + 6_100_000


def test_each_report_is_a_single_query(hr, mgr, django_assert_num_queries):
    with django_assert_num_queries(1):
        company_summary()
    with django_assert_num_queries(1):
        list(department_breakdown())


def test_empty_database_gives_zeros_not_none(db):
    Employee.objects.all().delete()
    summary = company_summary()
    assert summary["payroll_cents"] == 0
    assert summary["headcount"] == 0


def test_department_totals_add_up_to_the_company_total(hr, mgr, peer, outsider):
    assert sum(d.dept_payroll for d in department_breakdown()) == company_summary()["payroll_cents"]


def test_dashboard_renders_dollars_consistently(client, login, hr, mgr, peer, outsider):
    html = login(hr).get(reverse("dashboard")).content.decode()
    assert "$276,000.00" in html  # headline payroll
    assert "$221,000.00" in html  # Engineering row: 90k + 70k + 61k
    assert "22100000" not in html  # no raw cents


def test_department_list_shows_budget_in_dollars(client, login, hr, eng):
    eng.budget_cents = 5_000_000
    eng.save()
    assert "$50,000.00" in login(hr).get(reverse("department_list")).content.decode()
