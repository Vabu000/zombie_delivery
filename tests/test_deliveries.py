def test_deliveries_anonymous_access(client):
    """Сценарій: Анонімний доступ до предметної області.

    Перевірка отримання 401 Unauthorized без токена.
    """
    # Спроба створення
    res = client.post(
        "/deliveries/",
        json={"target_lat": 50.45, "target_lon": 30.52, "prey_type": "Brain"},
    )
    assert res.status_code == 401

    # Спроба отримання списку
    res_list = client.get("/deliveries/")
    assert res_list.status_code == 401


def test_delivery_creation_and_business_logic_mvp(client, registered_user):
    """Сценарій: Створення замовлення та базова бізнес-логіка розрахунку ціни (MVP)."""
    headers = registered_user["headers"]
    payload = {
        "title": "Термінова доставка мізків",
        "target_lat": 50.4501,
        "target_lon": 30.5234,
        "prey_type": "Brain",
        "danger_level": "NIGHTMARE",
        "notes": "Обережно, активні снайпери людей!",
    }
    res = client.post("/deliveries/", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Термінова доставка мізків"
    assert data["status"] == "PENDING"
    assert data["owner_id"] == registered_user["id"]
    # Розрахунок винагороди: base(10) * danger(3.0) * prey(2.0) = 60
    assert data["reward_brains"] == 60


def test_horizontal_idor_on_delivery_entity(client, registered_user, second_user, admin_user):
    """Сценарій: Горизонтальне розмежування прав (IDOR) на сутності предметної області.

    Спроба авторизованого користувача змінити, переглянути або видалити
    чужу сутність (доставку) повинна повертати статус 403 Forbidden.
    """
    user1_headers = registered_user["headers"]
    user2_headers = second_user["headers"]
    admin_headers = admin_user["headers"]

    # 1. User 1 створює власну доставку
    create_res = client.post(
        "/deliveries/",
        json={
            "title": "Секретний бункер User 1",
            "target_lat": 10.0,
            "target_lon": 20.0,
            "prey_type": "Plasma",
            "danger_level": "HIGH",
        },
        headers=user1_headers,
    )
    assert create_res.status_code == 201
    delivery_id = create_res.json()["id"]

    # 2. User 2 намагається переглянути деталі чужої доставки -> 403 Forbidden
    idor_get = client.get(f"/deliveries/{delivery_id}", headers=user2_headers)
    assert idor_get.status_code == 403
    assert "IDOR" in idor_get.json()["detail"]

    # 3. User 2 намагається змінити чужу доставку (IDOR) -> 403 Forbidden
    idor_put = client.put(
        f"/deliveries/{delivery_id}",
        json={"target_lat": 99.9, "target_lon": 99.9, "prey_type": "Rotten Meat"},
        headers=user2_headers,
    )
    assert idor_put.status_code == 403
    assert "Ви не можете редагувати чужі маршрути" in idor_put.json()["detail"]

    # 4. User 2 намагається видалити чужу доставку -> 403 Forbidden
    idor_delete = client.delete(f"/deliveries/{delivery_id}", headers=user2_headers)
    assert idor_delete.status_code == 403

    # 5. User 1 (власник) успішно оновлює власну доставку -> 200 OK
    legit_put = client.put(
        f"/deliveries/{delivery_id}",
        json={"title": "Оновлена доставка User 1", "notes": "Додано захист"},
        headers=user1_headers,
    )
    assert legit_put.status_code == 200
    assert legit_put.json()["title"] == "Оновлена доставка User 1"

    # 6. Адміністратор має право переглядати та редагувати будь-яку доставку
    admin_get = client.get(f"/deliveries/{delivery_id}", headers=admin_headers)
    assert admin_get.status_code == 200


def test_courier_workflow_and_role_escalation_guard(client, registered_user, courier_user):
    """Сценарій: Робота кур'єра зомбі та захист від виконання дій кур'єра звичайним користувачем."""
    user_headers = registered_user["headers"]
    courier_headers = courier_user["headers"]

    # Створюємо замовлення
    deliv_res = client.post(
        "/deliveries/",
        json={"target_lat": 15.0, "target_lon": 25.0, "prey_type": "Antidote"},
        headers=user_headers,
    )
    assert deliv_res.status_code == 201
    delivery_id = deliv_res.json()["id"]

    # 1. Звичайний користувач намагається взяти замовлення як кур'єр -> 403 Forbidden
    illegal_claim = client.post(f"/deliveries/{delivery_id}/claim", headers=user_headers)
    assert illegal_claim.status_code == 403

    # 2. Справжній кур'єр бере замовлення в доставку -> 200 OK
    claim_res = client.post(f"/deliveries/{delivery_id}/claim", headers=courier_headers)
    assert claim_res.status_code == 200
    assert claim_res.json()["status"] == "IN_TRANSIT"
    assert claim_res.json()["courier_id"] == courier_user["id"]

    # 3. Кур'єр завершує доставку -> 200 OK
    complete_res = client.post(f"/deliveries/{delivery_id}/complete", headers=courier_headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "DELIVERED"

    # 4. Спроба редагувати вже завершену доставку -> 400 Bad Request
    edit_finished = client.put(
        f"/deliveries/{delivery_id}",
        json={"target_lat": 1.0},
        headers=user_headers,
    )
    assert edit_finished.status_code == 400
