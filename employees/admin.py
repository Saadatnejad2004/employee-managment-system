from django.contrib import admin
from .models import Department, Employee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "budget_cents")
    search_fields = ("name",)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "department", "status")
    list_filter = ("department", "status")
    search_fields = ("first_name", "last_name", "email")
