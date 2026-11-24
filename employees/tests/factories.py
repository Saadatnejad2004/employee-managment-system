from datetime import date

import factory
from django.contrib.auth import get_user_model

from employees.models import Department, Employee


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Department {n}")
    budget_cents = 0


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "correct-horse-battery-staple")
        if create:
            self.save(update_fields=["password"])


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"person{n}@example.com")
    job_title = "Staff"
    salary_cents = 5_000_000
    date_hired = date(2024, 1, 1)
    department = factory.SubFactory(DepartmentFactory)
