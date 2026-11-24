import pytest
from django.urls import reverse

from .conftest import PASSWORD

pytestmark = pytest.mark.django_db


def test_login_page_is_public(client):
    assert client.get(reverse("login")).status_code == 200


def test_login_redirects_to_employee_list(client, hr):
    response = client.post(reverse("login"), {"username": hr.user.username, "password": PASSWORD})
    assert response.status_code == 302
    assert response.url == reverse("employee_list")


def test_wrong_password_is_rejected(client, hr):
    response = client.post(reverse("login"), {"username": hr.user.username, "password": "nope"})
    assert response.status_code == 200
    assert "errorlist" in response.content.decode()


def test_logout_requires_post(client, hr, login):
    login(hr)
    assert client.get(reverse("logout")).status_code == 405
    assert client.post(reverse("logout")).status_code == 302
    assert client.get(reverse("employee_list")).status_code == 302  # logged out again


def test_terminating_an_employee_disables_their_login(client, peer):
    peer.status = "terminated"
    peer.save()
    peer.user.refresh_from_db()
    assert peer.user.is_active is False
    assert client.login(username=peer.user.username, password=PASSWORD) is False
