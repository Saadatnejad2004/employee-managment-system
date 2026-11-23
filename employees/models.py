from django.conf import settings
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    budget_cents = models.PositiveIntegerField(default=0, help_text="Budget in cents")

    def __str__(self):
        return self.name


class Employee(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("on_leave", "On Leave"),
        ("terminated", "Terminated"),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100)
    salary_cents = models.PositiveIntegerField(default=0, help_text="Salary in cents")
    date_hired = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")

    # Links an HR record to a login account. This is what lets the system
    # answer "which employee/department is the person who is logged in?".
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="employee_profile",
        help_text="Login account for this employee (drives role-based access).",
    )

    class Meta:
        permissions = [
            ("view_all_employees", "Can view employees in every department"),
            ("view_department_employees", "Can view employees in their own department"),
            ("view_salary", "Can view salary information"),
            ("view_reports", "Can view the reports dashboard"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.job_title})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # A terminated employee must not keep a working login.
        if self.user_id and self.status == "terminated" and self.user.is_active:
            self.user.is_active = False
            self.user.save(update_fields=["is_active"])
