"""Row-level (object scope) access rules for employee records."""

from .models import Employee


def employees_visible_to(user):
    """
    Return the Employee queryset this user is allowed to see.

    * ``view_all_employees``        -> everyone (HR)
    * ``view_department_employees`` -> own department (managers)
    * otherwise                     -> only their own record
    * no linked employee profile    -> nothing
    """
    queryset = Employee.objects.select_related("department")

    if user.has_perm("employees.view_all_employees"):
        return queryset

    # Reverse one-to-one raises when missing; getattr() with a default
    # handles that (and AnonymousUser) without a try/except.
    profile = getattr(user, "employee_profile", None)
    if profile is None:
        return queryset.none()

    if user.has_perm("employees.view_department_employees"):
        return queryset.filter(department_id=profile.department_id)

    return queryset.filter(pk=profile.pk)


def can_view_salary(user, employee):
    """HR (``view_salary``) can see anyone's salary; others only their own."""
    return user.has_perm("employees.view_salary") or employee.user_id == user.pk


class EmployeeScopeMixin:
    """
    Restrict a view's queryset to the rows the current user may access.

    Use together with PermissionRequiredMixin (which answers "may this user
    use this screen?"); this mixin answers "which rows may they see?".
    Out-of-scope objects return 404, so their existence is not revealed.
    """

    def get_queryset(self):
        return employees_visible_to(self.request.user)
