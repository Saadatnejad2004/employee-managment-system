from unittest import mock

import pytest
from django.db import OperationalError
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_healthz_is_public_and_reports_ok(client):
    response = client.get(reverse("healthz"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthz_reports_503_when_the_database_is_down(client):
    with mock.patch("employees.views.connection.ensure_connection", side_effect=OperationalError):
        response = client.get(reverse("healthz"))
    assert response.status_code == 503
