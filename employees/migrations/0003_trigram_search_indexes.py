"""
PostgreSQL only: speed up the employee search.

The list view searches with `icontains`, which Django runs as
`UPPER(column) LIKE UPPER('%term%')`. A leading wildcard cannot use a normal
b-tree index, so every search scans the whole table. A trigram GIN index on
`UPPER(column)` makes that same query index-assisted, with no code change.

On other databases (SQLite in local dev) this migration does nothing. The
indexes are created with raw operations on purpose so they are not part of the
model state that SQLite would try to build.
"""

from django.contrib.postgres.indexes import GinIndex, OpClass
from django.db import migrations
from django.db.models.functions import Upper

SEARCHED_FIELDS = ["first_name", "last_name", "email", "job_title"]


def trigram_indexes():
    return [
        GinIndex(OpClass(Upper(field), name="gin_trgm_ops"), name=f"emp_{field}_trgm_idx")
        for field in SEARCHED_FIELDS
    ]


def add_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    employee = apps.get_model("employees", "Employee")
    for index in trigram_indexes():
        schema_editor.add_index(employee, index)


def remove_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    employee = apps.get_model("employees", "Employee")
    for index in trigram_indexes():
        schema_editor.remove_index(employee, index)


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0002_employee_user_and_permissions"),
    ]

    operations = [
        migrations.RunPython(add_indexes, remove_indexes),
    ]
