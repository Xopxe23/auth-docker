import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("email, password, status_code", [
    ("georgeduday95@yandex.ru", "GeorgeDudaev", 422),
    ("georgeduday95@yandex.ru", "george123", 422),
    ("georgeduday@gmail.com", "Geor ge95", 422),
    ("georgeduday", "George95", 422),
    ("georgeduday95@yandex.ru", "George95", 201),
    ("georgeduday95@yandex.ru", "George95", 400),
])
async def test_register_user(email: str, password: str, status_code: int, async_client: AsyncClient):
    response = await async_client.post(url="/auth/register", json={
        "email": email,
        "password": password
    })
    assert response.status_code == status_code


@pytest.mark.parametrize("email, password, status_code", [
    ("georgeduday95@yandex.ru", "George95", 200),
    ("georgeduday95@yandex.ru", "George123", 400),
    ("george@yandex.ru", "George123", 400),
    ("georgeduday@gmail.com", "Geo95RGe", 200),
])
async def test_login_user(email: str, password: str, status_code: int, async_client: AsyncClient):
    response = await async_client.post(url="/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == status_code


async def test_refresh(
        async_client: AsyncClient,
        authenticated_async_client: AsyncClient
):
    refresh_token = authenticated_async_client.cookies.get("REFRESH_TOKEN")
    response = await authenticated_async_client.post(url="/auth/refresh")
    assert response.status_code == 200
    assert response.cookies.get("REFRESH_TOKEN") != refresh_token
    response = await async_client.post(url="/auth/refresh")
    assert response.status_code == 401


async def test_me(
        async_client: AsyncClient,
        authenticated_async_client: AsyncClient
):
    response = await async_client.get(url="/auth/me")
    assert response.status_code == 401
    response = await authenticated_async_client.get(url="/auth/me")
    assert response.status_code == 200
    response = response.json()
    assert response["email"] == "georgeduday@gmail.com"
