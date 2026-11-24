"""
Single source of truth for the system's roles.

Each role is a Django ``Group``; the codenames listed are the permissions the
group is granted. ``python manage.py setup_roles`` creates/updates the groups
from this table, so changing a role's rights is a one-line, reviewable change.
"""

HR_ADMIN = "HR Admin"
MANAGER = "Manager"
EMPLOYEE = "Employee"

ROLE_PERMISSIONS = {
    # Full control of people data, salaries, departments and reports.
    HR_ADMIN: [
        "view_employee",
        "add_employee",
        "change_employee",
        "delete_employee",
        "view_all_employees",
        "view_salary",
        "view_reports",
        "view_department",
        "add_department",
        "change_department",
        "delete_department",
    ],
    # Read-only access to people in their own department. No salaries, no reports.
    MANAGER: [
        "view_employee",
        "view_department_employees",
    ],
    # Read-only access to their own profile (including their own salary).
    EMPLOYEE: [
        "view_employee",
    ],
}
