import pytest

from schema import Schema
from user.models import ServiceUser


@pytest.mark.django_db
def test_user_login(api_client):
    # given
    ServiceUser.objects.create(email="goodpang@example.com")

    # when
    response = api_client.post("/users/log-in", data={"email": "goodpang@example.com"})

    # then
    assert response.status_code == 200
    assert Schema({"results": {"token": str}}).validate(response.json())
