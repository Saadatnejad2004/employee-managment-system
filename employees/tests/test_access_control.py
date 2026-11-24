"""
The access matrix: who may open which screen, and what happens when they may not.

  200  allowed            302  not logged in -> login page
  403  logged in, but the role lacks the permission
  404  object exists but is outside the user's scope (existence is not revealed)
"""

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse

from employees.models import Employee
from employees.roles import EMPLOYEE

from .conftest import last_names
from .factories import UserFactory

pytestmark = pytest.mark.django_db

# (actor fixture | None for anonymous, url name, target fixture | None, expected status)
MATRIX = [
    # --- HR Admin: everything ---
    ("hr", "employee_list", None, 200),
    ("hr", "dashboard", None, 200),
    ("hr", "department_list", None, 200),
    ("hr", "department_create", None, 200),
    ("hr", "employee_create", None, 200),
    ("hr", "employee_detail", "outsider", 200),
    ("hr", "employee_update", "outsider", 200),
    ("hr", "employee_delete", "outsider", 200),
    # --- Manager: own department, read-only ---
    ("mgr", "employee_list", None, 200),
    ("mgr", "employee_detail", "peer", 200),
    ("mgr", "employee_detail", "outsider", 404),
    ("mgr", "dashboard", None, 403),
    ("mgr", "department_list", None, 403),
    ("mgr", "employee_create", None, 403),
    ("mgr", "employee_update", "peer", 403),
    ("mgr", "employee_delete", "peer", 403),
    # --- Employee: self only, read-only ---
    ("peer", "employee_list", None, 200),
    ("peer", "employee_detail", "peer", 200),
    ("peer", "employee_detail", "mgr", 404),
    ("peer", "employee_detail", "outsider", 404),
    ("peer", "employee_update", "peer", 403),
    ("peer", "dashboard", None, 403),
    ("peer", "department_list", None, 403),
    # --- Anonymous: login page for everything ---
    (None, "employee_list", None, 302),
    (None, "dashboard", None, 302),
    (None, "department_list", None, 302),
    (None, "employee_create", None, 302),
    (None, "employee_detail", "hr", 302),
    (None, "my_profile", None, 302),
]


@pytest.mark.parametrize(("actor", "view", "target", "expected"), MATRIX)
def test_access_matrix(request, client, login, actor, view, target, expected):
    if actor:
        login(request.getfixturevalue(actor))
    args = [request.getfixturevalue(target).pk] if target else []

    response = client.get(reverse(view, args=args))

    assert response.status_code == expected
    if expected == 302:
        assert response.url.startswith(reverse("login"))


def test_forbidden_writes_change_nothing(client, login, mgr, peer):
    login(mgr)
    for view in ("employee_update", "employee_delete"):
        assert client.post(reverse(view, args=[peer.pk])).status_code == 403
    assert Employee.objects.filter(pk=peer.pk).exists()


def test_hr_can_delete(client, login, hr, outsider):
    login(hr)
    client.post(reverse("employee_delete", args=[outsider.pk]))
    assert not Employee.objects.filter(pk=outsider.pk).exists()


# --- row-level scoping ---------------------------------------------------------


def test_hr_sees_everyone(client, login, hr, mgr, peer, outsider):
    response = login(hr).get(reverse("employee_list"))
    assert last_names(response) == {"Reyes", "Khan", "Lund", "Vega"}


def test_manager_sees_only_own_department(client, login, hr, mgr, peer, outsider):
    response = login(mgr).get(reverse("employee_list"))
    assert last_names(response) == {"Reyes", "Khan", "Lund"}  # HR (Reyes) is in Engineering too


def test_manager_search_cannot_reach_other_departments(client, login, mgr, outsider):
    response = login(mgr).get(reverse("employee_list"), {"q": "Vega"})
    assert last_names(response) == set()


def test_employee_sees_only_self(client, login, mgr, peer, outsider):
    response = login(peer).get(reverse("employee_list"))
    assert last_names(response) == {"Lund"}


def test_buttons_are_hidden_without_permission(client, login, mgr, peer):
    html = login(mgr).get(reverse("employee_list")).content.decode()
    assert "Add Employee" not in html
    assert "/update/" not in html
    assert "/delete/" not in html


# --- field-level salary visibility ---------------------------------------------


def test_hr_sees_anyones_salary(client, login, hr, outsider):
    response = login(hr).get(reverse("employee_detail", args=[outsider.pk]))
    assert "$55,000.00" in response.content.decode()


def test_manager_does_not_see_colleague_salary(client, login, mgr, peer):
    response = login(mgr).get(reverse("employee_detail", args=[peer.pk]))
    html = response.content.decode()
    assert response.status_code == 200
    assert "Salary" not in html
    assert "61,000" not in html


def test_people_see_their_own_salary(client, login, mgr, peer):
    assert (
        "$70,000.00" in login(mgr).get(reverse("employee_detail", args=[mgr.pk])).content.decode()
    )
    response = login(peer).get(reverse("my_profile"), follow=True)
    assert "$61,000.00" in response.content.decode()


# --- edge cases -----------------------------------------------------------------


def test_user_without_any_group_is_denied(client, login, roles):
    assert login(UserFactory()).get(reverse("employee_list")).status_code == 403


def test_group_member_without_employee_profile_sees_nothing(client, login, roles):
    user = UserFactory()
    user.groups.add(Group.objects.get(name=EMPLOYEE))
    login(user)
    assert last_names(client.get(reverse("employee_list"))) == set()
    assert client.get(reverse("my_profile")).status_code == 404
