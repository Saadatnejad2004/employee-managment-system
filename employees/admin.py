from django.contrib import admin

from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "budget_cents")
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "department", "status", "user")
    list_filter = ("department", "status")
    search_fields = ("first_name", "last_name", "email")
    # Linking a login account to an employee is a privileged action, so it is
    # done here in the admin (staff only), not in the public employee form.
    autocomplete_fields = ("user",)
    list_select_related = ("department", "user")
