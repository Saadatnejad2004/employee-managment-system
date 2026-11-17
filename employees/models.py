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

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.job_title})"
