from io import StringIO

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command

from employees.roles import EMPLOYEE, HR_ADMIN, MANAGER

from .factories import DepartmentFactory, EmployeeFactory, UserFactory

PASSWORD = "correct-horse-battery-staple"


@pytest.fixture
def roles(db):
    """Create the role groups, exactly as `manage.py setup_roles` does."""
    call_command("setup_roles", stdout=StringIO())


@pytest.fixture
def person(roles):
    """Factory: person(role, department, **fields) -> Employee with a linked login."""

    def make(role, department, **fields):
        user = UserFactory()
        if role:
            user.groups.add(Group.objects.get(name=role))
        return EmployeeFactory(user=user, department=department, **fields)

    return make


# --- a small world: two departments, one person per role ---------------------


@pytest.fixture
def eng(db):
    return DepartmentFactory(name="Engineering")


@pytest.fixture
def sales(db):
    return DepartmentFactory(name="Sales")


@pytest.fixture
def hr(person, eng):
    return person(
        HR_ADMIN, eng, first_name="Hana", last_name="Reyes", email="hr@example.com",
        salary_cents=9_000_000,
    )  # fmt: skip


@pytest.fixture
def mgr(person, eng):
    return person(
        MANAGER, eng, first_name="Mo", last_name="Khan", email="mgr@example.com",
        salary_cents=7_000_000,
    )  # fmt: skip


@pytest.fixture
def peer(person, eng):
    return person(
        EMPLOYEE, eng, first_name="Pia", last_name="Lund", email="peer@example.com",
        salary_cents=6_100_000,
    )  # fmt: skip


@pytest.fixture
def outsider(person, sales):
    return person(
        EMPLOYEE, sales, first_name="Omar", last_name="Vega", email="out@example.com",
        salary_cents=5_500_000,
    )  # fmt: skip


@pytest.fixture
def login(client):
    """login(employee_or_user) -> the test client, logged in as that person."""

    def do_login(who):
        client.force_login(getattr(who, "user", who))
        return client

    return do_login


def last_names(response):
    return {e.last_name for e in response.context["employees"]}
