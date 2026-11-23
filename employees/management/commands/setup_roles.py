from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from employees.models import Department, Employee
from employees.roles import ROLE_PERMISSIONS


class Command(BaseCommand):
    help = "Create or update the role groups (HR Admin, Manager, Employee) and their permissions."

    def handle(self, *args, **options):
        content_types = ContentType.objects.get_for_models(Employee, Department).values()

        for role, codenames in ROLE_PERMISSIONS.items():
            permissions = Permission.objects.filter(
                content_type__in=content_types, codename__in=codenames
            )
            missing = set(codenames) - {p.codename for p in permissions}
            if missing:
                raise CommandError(
                    f"Unknown permissions for role '{role}': {sorted(missing)}. "
                    "Did you run `python manage.py migrate`?"
                )

            group, created = Group.objects.get_or_create(name=role)
            group.permissions.set(permissions)  # idempotent: exact match, no leftovers
            self.stdout.write(
                self.style.SUCCESS(f"{'Created' if created else 'Updated'} role '{role}' "
                                   f"({permissions.count()} permissions)")
            )
