from decimal import Decimal

import pytest
from django.urls import reverse

from employees.forms import DepartmentForm, EmployeeForm
from employees.models import Employee

pytestmark = pytest.mark.django_db


@pytest.fixture
def payload(eng):
    def make(**overrides):
        data = {
            "first_name": "Ada", "last_name": "Lovelace", "email": "Ada@Example.com",
            "phone": "", "job_title": "Engineer", "salary": "50000.00",
            "date_hired": "2025-01-15", "status": "active", "department": eng.pk,
        }  # fmt: skip
        return data | overrides

    return make


def test_salary_is_entered_in_dollars_and_stored_in_cents(payload):
    form = EmployeeForm(payload())
    assert form.is_valid(), form.errors
    assert form.save().salary_cents == 5_000_000


def test_edit_form_shows_dollars_not_cents(peer):
    assert EmployeeForm(instance=peer).initial["salary"] == Decimal("61000.00")


def test_editing_round_trips_without_changing_the_salary(peer, payload):
    form = EmployeeForm(payload(email="peer@example.com", salary="61000.00"), instance=peer)
    assert form.is_valid(), form.errors
    assert form.save().salary_cents == 6_100_000


@pytest.mark.parametrize("bad_salary", ["-1", "99999999999", "abc"])
def test_rejects_invalid_salaries(payload, bad_salary):
    assert "salary" in EmployeeForm(payload(salary=bad_salary)).errors


def test_email_is_lowercased(payload):
    form = EmployeeForm(payload())
    assert form.is_valid()
    assert form.save().email == "ada@example.com"


def test_email_uniqueness_is_case_insensitive(hr, payload):
    assert "email" in EmployeeForm(payload(email="HR@EXAMPLE.COM")).errors


def test_department_budget_in_dollars():
    form = DepartmentForm({"name": "Ops", "description": "", "budget": "1234.56"})
    assert form.is_valid(), form.errors
    assert form.save().budget_cents == 123_456


def test_create_view_end_to_end(client, login, hr, payload):
    response = login(hr).post(reverse("employee_create"), payload())
    assert response.status_code == 302
    assert Employee.objects.get(email="ada@example.com").salary_cents == 5_000_000
