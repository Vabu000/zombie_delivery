import pytest
from fastapi.testclient import TestClient

from src.database import Base, engine
from src.main import app


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    res = client.post(
        "/users/register",
        json={"username": "survivor1", "password": "password123", "full_name": "Rick"},
    )
    assert res.status_code == 200
    login_res = client.post(
        "/users/login", json={"username": "survivor1", "password": "password123"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_id = res.json()["id"]
    return {
        "username": "survivor1",
        "id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def second_user(client):
    res = client.post(
        "/users/register",
        json={"username": "survivor2", "password": "password456", "full_name": "Daryl"},
    )
    assert res.status_code == 200
    login_res = client.post(
        "/users/login", json={"username": "survivor2", "password": "password456"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_id = res.json()["id"]
    return {
        "username": "survivor2",
        "id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def admin_user(client):
    from src.config import settings

    res = client.post(
        "/users/register-admin",
        json={
            "username": "overlord_admin",
            "password": "adminpassword",
            "admin_secret": settings.ADMIN_SECRET_KEY,
            "full_name": "Hive Mind Overlord",
        },
    )
    assert res.status_code == 200
    login_res = client.post(
        "/users/login",
        json={"username": "overlord_admin", "password": "adminpassword"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_id = res.json()["id"]
    return {
        "username": "overlord_admin",
        "id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def courier_user(client):
    res = client.post(
        "/users/register-courier",
        json={
            "username": "courier_zombie",
            "password": "hunterpassword",
            "full_name": "Speedy Zombie",
        },
    )
    assert res.status_code == 200
    login_res = client.post(
        "/users/login",
        json={"username": "courier_zombie", "password": "hunterpassword"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    user_id = res.json()["id"]
    return {
        "username": "courier_zombie",
        "id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }
