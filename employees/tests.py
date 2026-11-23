from datetime import date
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Department, Employee
from .roles import EMPLOYEE, HR_ADMIN, MANAGER

User = get_user_model()
PASSWORD = "correct-horse-battery-staple"


class RoleTestBase(TestCase):
    """Two departments, four people, one per role (plus a peer and an outsider)."""

    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", stdout=StringIO())
        cls.eng = Department.objects.create(name="Engineering")
        cls.sales = Department.objects.create(name="Sales")

        cls.hr_user, cls.hr = cls._person("hr", HR_ADMIN, cls.eng, "Hana", "Reyes", 9_000_000)
        cls.mgr_user, cls.mgr = cls._person("mgr", MANAGER, cls.eng, "Mo", "Khan", 7_000_000)
        cls.peer_user, cls.peer = cls._person("peer", EMPLOYEE, cls.eng, "Pia", "Lund", 6_100_000)
        cls.out_user, cls.outsider = cls._person("out", EMPLOYEE, cls.sales, "Omar", "Vega", 5_500_000)

    @classmethod
    def _person(cls, username, role, department, first, last, salary_cents):
        user = User.objects.create_user(username, password=PASSWORD)
        user.groups.add(Group.objects.get(name=role))
        employee = Employee.objects.create(
            first_name=first, last_name=last, email=f"{username}@example.com",
            job_title="Staff", salary_cents=salary_cents, date_hired=date(2024, 1, 1),
            department=department, user=user,
        )
        return user, employee

    def login(self, user):
        self.client.force_login(user)

    def names(self, response):
        return {e.last_name for e in response.context["employees"]}


class AuthenticationTests(RoleTestBase):
    def test_anonymous_is_redirected_to_login_everywhere(self):
        urls = [
            reverse("employee_list"), reverse("dashboard"), reverse("department_list"),
            reverse("employee_create"), reverse("employee_detail", args=[self.hr.pk]),
            reverse("my_profile"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response, f"{reverse('login')}?next={url}", fetch_redirect_response=False
                )

    def test_login_page_is_public_and_login_works(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        response = self.client.post(
            reverse("login"), {"username": "hr", "password": PASSWORD}
        )
        self.assertRedirects(response, reverse("employee_list"), fetch_redirect_response=False)

    def test_wrong_password_is_rejected(self):
        response = self.client.post(reverse("login"), {"username": "hr", "password": "nope"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")

    def test_logout_requires_post(self):
        self.login(self.hr_user)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"), fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse("employee_list")).status_code, 302)

    def test_terminating_an_employee_disables_their_login(self):
        self.peer.status = "terminated"
        self.peer.save()
        self.peer_user.refresh_from_db()
        self.assertFalse(self.peer_user.is_active)
        self.assertFalse(self.client.login(username="peer", password=PASSWORD))


class HRAdminTests(RoleTestBase):
    def setUp(self):
        self.login(self.hr_user)

    def test_sees_everyone_and_all_screens(self):
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(self.names(response), {"Reyes", "Khan", "Lund", "Vega"})
        for name in ("dashboard", "department_list", "employee_create", "department_create"):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_sees_other_peoples_salary(self):
        response = self.client.get(reverse("employee_detail", args=[self.outsider.pk]))
        self.assertContains(response, "55,000.00")

    def test_can_delete(self):
        self.client.post(reverse("employee_delete", args=[self.outsider.pk]))
        self.assertFalse(Employee.objects.filter(pk=self.outsider.pk).exists())


class ManagerTests(RoleTestBase):
    def setUp(self):
        self.login(self.mgr_user)

    def test_list_is_limited_to_own_department(self):
        response = self.client.get(reverse("employee_list"))
        # HR (Reyes) also belongs to Engineering; Sales (Vega) must be hidden.
        self.assertEqual(self.names(response), {"Reyes", "Khan", "Lund"})

    def test_search_cannot_reach_other_departments(self):
        response = self.client.get(reverse("employee_list"), {"q": "Vega"})
        self.assertEqual(self.names(response), set())

    def test_other_department_profile_is_404(self):
        response = self.client.get(reverse("employee_detail", args=[self.outsider.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_see_colleague_salary(self):
        response = self.client.get(reverse("employee_detail", args=[self.peer.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Salary")
        self.assertNotContains(response, "61,000")

    def test_can_see_own_salary(self):
        response = self.client.get(reverse("employee_detail", args=[self.mgr.pk]))
        self.assertContains(response, "70,000.00")

    def test_forbidden_screens(self):
        for name in ("dashboard", "department_list", "employee_create", "department_create"):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 403)

    def test_cannot_edit_or_delete(self):
        for name in ("employee_update", "employee_delete"):
            with self.subTest(name=name):
                url = reverse(name, args=[self.peer.pk])
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Employee.objects.filter(pk=self.peer.pk).exists())

    def test_no_edit_buttons_rendered(self):
        response = self.client.get(reverse("employee_list"))
        self.assertNotContains(response, "Add Employee")
        self.assertNotContains(response, "/update/")
        self.assertNotContains(response, "/delete/")


class EmployeeRoleTests(RoleTestBase):
    def setUp(self):
        self.login(self.peer_user)

    def test_list_shows_only_self(self):
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(self.names(response), {"Lund"})

    def test_colleague_in_same_department_is_404(self):
        response = self.client.get(reverse("employee_detail", args=[self.mgr.pk]))
        self.assertEqual(response.status_code, 404)

    def test_my_profile_shows_own_salary(self):
        response = self.client.get(reverse("my_profile"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "61,000.00")

    def test_cannot_edit_own_record_or_see_reports(self):
        self.assertEqual(self.client.get(reverse("employee_update", args=[self.peer.pk])).status_code, 403)
        self.assertEqual(self.client.get(reverse("dashboard")).status_code, 403)


class EdgeCaseTests(RoleTestBase):
    def test_user_without_group_is_denied(self):
        user = User.objects.create_user("nobody", password=PASSWORD)
        self.login(user)
        self.assertEqual(self.client.get(reverse("employee_list")).status_code, 403)

    def test_group_member_without_employee_profile_sees_nothing(self):
        user = User.objects.create_user("orphan", password=PASSWORD)
        user.groups.add(Group.objects.get(name=EMPLOYEE))
        self.login(user)
        self.assertEqual(self.names(self.client.get(reverse("employee_list"))), set())
        self.assertEqual(self.client.get(reverse("my_profile")).status_code, 404)

    def test_setup_roles_is_idempotent_and_resets_drift(self):
        group = Group.objects.get(name=EMPLOYEE)
        group.permissions.add(*Group.objects.get(name=HR_ADMIN).permissions.all())  # simulate drift
        call_command("setup_roles", stdout=StringIO())
        call_command("setup_roles", stdout=StringIO())
        self.assertEqual(
            list(group.permissions.values_list("codename", flat=True)), ["view_employee"]
        )
