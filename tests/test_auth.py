from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, engine
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_unauthorized_access():
    response = client.post(
        "/deliveries/", json={"target_lat": 1.0, "target_lon": 1.0, "prey_type": "Meat"}
    )
    assert response.status_code == 401


def test_successful_registration_and_login():
    res = client.post(
        "/users/register", json={"username": "zombie1", "password": "123"}
    )
    assert res.status_code == 200

    res = client.post("/users/login", json={"username": "zombie1", "password": "123"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_vertical_privilege_escalation():
    # Реєструємо звичайного юзера
    client.post("/users/register", json={"username": "user", "password": "123"})
    token = client.post(
        "/users/login", json={"username": "user", "password": "123"}
    ).json()["access_token"]

    # Спроба зайти в адмінку
    res = client.get("/users/admin-panel", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403


def test_horizontal_privilege_escalation_idor():
    # Юзер 1
    client.post("/users/register", json={"username": "user1", "password": "123"})
    t1 = client.post(
        "/users/login", json={"username": "user1", "password": "123"}
    ).json()["access_token"]

    # Юзер 2
    client.post("/users/register", json={"username": "user2", "password": "123"})
    t2 = client.post(
        "/users/login", json={"username": "user2", "password": "123"}
    ).json()["access_token"]

    # Юзер 1 створює доставку
    client.post(
        "/deliveries/",
        json={"target_lat": 1.0, "target_lon": 2.0, "prey_type": "Brain"},
        headers={"Authorization": f"Bearer {t1}"},
    )

    # Юзер 2 намагається змінити доставку Юзера 1 (id=1)
    res = client.put(
        "/deliveries/1",
        json={"target_lat": 5.0, "target_lon": 5.0, "prey_type": "Blood"},
        headers={"Authorization": f"Bearer {t2}"},
    )
    assert res.status_code == 403
