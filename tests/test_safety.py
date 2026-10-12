from starlette.testclient import TestClient

from src.config import settings
from src.main import app


def test_exception_handler_safety_production():
    """ЛР №3 Безпека: Перевірка приховування внутрішніх стектрейсів та деталей помилки 500

    при вимкненому режимі DEBUG (Production).
    """
    original_debug = settings.DEBUG
    original_app_debug = app.debug
    try:
        settings.DEBUG = False
        app.debug = False
        app.middleware_stack = None  # Перебудова middleware стеку для застосування debug=False
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/debug/trigger-500")
        assert response.status_code == 500
        data = response.json()
        assert "message" in data
        # Перевірка: жодних слідів RuntimeError, стектрейсів чи деталей реалізації
        assert "RuntimeError" not in data["message"]
        assert "traceback" not in data["message"].lower()
        assert "Zombie systems are down" in data["message"]
    finally:
        settings.DEBUG = original_debug
        app.debug = original_app_debug
        app.middleware_stack = None


def test_exception_handler_sandbox_dev_mode():
    """ЛР №3: Перевірка надання інформації для розробника у Sandbox режимі (DEBUG=True)."""
    original_debug = settings.DEBUG
    original_app_debug = app.debug
    try:
        settings.DEBUG = True
        app.debug = (
            False  # Щоб ServerErrorMiddleware передавав обробку до FastAPI exception handler
        )
        app.middleware_stack = None
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/debug/trigger-500")
        assert response.status_code == 500
        data = response.json()
        assert "message" in data
        assert "Dev Error" in data["message"]
        assert data.get("type") == "RuntimeError"
    finally:
        settings.DEBUG = original_debug
        app.debug = original_app_debug
        app.middleware_stack = None


def test_environment_configuration_isolation():
    """ЛР №3: Перевірка розділення налаштувань та ізоляції баз даних."""
    assert settings.DATABASE_URL is not None
    assert settings.SECRET_KEY is not None
    assert "db" in settings.DATABASE_URL
