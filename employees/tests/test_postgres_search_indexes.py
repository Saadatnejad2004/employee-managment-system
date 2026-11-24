"""PostgreSQL-only checks. They are skipped on SQLite and run in CI, which uses Postgres."""

import pytest
from django.db import connection

from employees.models import Employee

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.skipif(
        connection.vendor != "postgresql", reason="trigram indexes are PostgreSQL-only"
    ),
]

SEARCHED = ["first_name", "last_name", "email", "job_title"]


def test_trigram_indexes_exist():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT indexname FROM pg_indexes "
            "WHERE tablename = 'employees_employee' AND indexname LIKE 'emp\\_%\\_trgm\\_idx'"
        )
        names = {row[0] for row in cursor.fetchall()}
    assert names == {f"emp_{field}_trgm_idx" for field in SEARCHED}


@pytest.mark.parametrize("field", SEARCHED)
def test_icontains_search_can_use_the_trigram_index(field):
    with connection.cursor() as cursor:
        # The test table is tiny, so force the planner to consider indexes.
        cursor.execute("SET LOCAL enable_seqscan = off")
    plan = Employee.objects.filter(**{f"{field}__icontains": "smith"}).explain()
    assert f"emp_{field}_trgm_idx" in plan
