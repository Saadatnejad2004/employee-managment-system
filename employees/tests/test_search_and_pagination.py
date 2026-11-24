import pytest
from django.urls import reverse

from .conftest import last_names
from .factories import EmployeeFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def as_hr(login, hr, mgr, peer, outsider):
    return login(hr)


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("pia lund", {"Lund"}),  # full name across two fields
        ("lund pia", {"Lund"}),  # word order does not matter
        ("pia vega", set()),  # every word must match
        ("MGR@example", {"Khan"}),  # email, case-insensitive
        ("   ", {"Reyes", "Khan", "Lund", "Vega"}),  # blank query = no filter
    ],
)
def test_search(as_hr, query, expected):
    assert last_names(as_hr.get(reverse("employee_list"), {"q": query})) == expected


def test_pagination_links_encode_the_search_term(as_hr, eng):
    for i in range(12):
        EmployeeFactory(
            department=eng, last_name="Smith", job_title="R&D Lead", email=f"s{i}@x.com"
        )
    html = as_hr.get(reverse("employee_list"), {"q": "r&d lead"}).content.decode()
    assert "q=r%26d%20lead" in html
    assert "q=r&d lead" not in html


def test_pages_do_not_overlap(as_hr, eng):
    EmployeeFactory.create_batch(25, department=eng)
    seen = []
    for page in (1, 2, 3):
        response = as_hr.get(reverse("employee_list"), {"page": page})
        seen += [e.pk for e in response.context["employees"]]
    assert len(seen) == len(set(seen)) == 25 + 4  # 25 new + hr, mgr, peer, outsider
