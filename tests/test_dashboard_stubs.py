def test_dashboard_hub_access(client):
    """Перевірка доступу до загального навігаційного хабу."""
    # JSON запит
    res = client.get("/dashboard/")
    assert res.status_code == 200
    data = res.json()
    assert "stubs" in data
    assert data["stubs"]["user_dashboard"] == "/dashboard/user"

    # HTML запит
    res_html = client.get("/dashboard/", headers={"Accept": "text/html"})
    assert res_html.status_code == 200
    assert "Zombie Night Delivery Aggregator" in res_html.text


def test_user_dashboard_stub(client, registered_user):
    """Перевірка домашньої сторінки-заглушки для звичайного користувача."""
    headers = registered_user["headers"]

    # JSON перевірка
    res = client.get("/dashboard/user", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == registered_user["username"]
    assert data["role"] == "user"
    assert "accessible_features" in data

    # HTML версія для браузера
    res_html = client.get(
        "/dashboard/user",
        headers={**headers, "Accept": "text/html"},
    )
    assert res_html.status_code == 200
    assert "Кабінет Виживалого" in res_html.text


def test_courier_dashboard_stub(client, courier_user, registered_user):
    """Перевірка домашньої сторінки-заглушки для кур'єра зомбі."""
    courier_headers = courier_user["headers"]
    user_headers = registered_user["headers"]

    # Кур'єр має доступ
    res = client.get("/dashboard/courier", headers=courier_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "courier"

    # Звичайний клієнт НЕ має доступу до панелі кур'єра -> 403 Forbidden
    res_forbidden = client.get("/dashboard/courier", headers=user_headers)
    assert res_forbidden.status_code == 403


def test_admin_dashboard_stub(client, admin_user, registered_user):
    """Перевірка домашньої сторінки-заглушки для адміністратора."""
    admin_headers = admin_user["headers"]
    user_headers = registered_user["headers"]

    # Адміністратор має доступ
    res = client.get("/dashboard/admin", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "admin"
    assert "total_users" in data

    # Звичайний клієнт НЕ має доступу до адмінського дашборду -> 403 Forbidden
    res_forbidden = client.get("/dashboard/admin", headers=user_headers)
    assert res_forbidden.status_code == 403
