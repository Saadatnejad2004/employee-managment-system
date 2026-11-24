from io import StringIO

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command

from employees.roles import EMPLOYEE, HR_ADMIN, ROLE_PERMISSIONS

pytestmark = pytest.mark.django_db


def test_setup_roles_creates_every_role_with_the_right_permissions():
    call_command("setup_roles", stdout=StringIO())
    for role, codenames in ROLE_PERMISSIONS.items():
        granted = set(Group.objects.get(name=role).permissions.values_list("codename", flat=True))
        assert granted == set(codenames)


def test_setup_roles_is_idempotent_and_removes_drift():
    call_command("setup_roles", stdout=StringIO())
    employee_group = Group.objects.get(name=EMPLOYEE)
    employee_group.permissions.add(*Group.objects.get(name=HR_ADMIN).permissions.all())  # drift

    call_command("setup_roles", stdout=StringIO())
    call_command("setup_roles", stdout=StringIO())

    assert list(employee_group.permissions.values_list("codename", flat=True)) == ["view_employee"]
