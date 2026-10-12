def test_anonymous_access_unauthorized(client):
    """Сценарій: Анонімний доступ.

    Перевірка отримання статус-коду 401 Unauthorized при спробі
    доступу до захищених маршрутів без токена або з недійсним токеном.
    """
    # 1. Захищений маршрут створення доставки
    res_deliv = client.post(
        "/deliveries/",
        json={"target_lat": 50.45, "target_lon": 30.52, "prey_type": "Meat"},
    )
    assert res_deliv.status_code == 401
    assert "detail" in res_deliv.json()

    # 2. Захищений маршрут отримання інформації про себе (/users/me)
    res_me = client.get("/users/me")
    assert res_me.status_code == 401

    # 3. Захищений маршрут адмін-панелі (/users/admin-panel)
    res_admin = client.get("/users/admin-panel")
    assert res_admin.status_code == 401

    # 4. Запит з недійсним (фейковим) токеном
    fake_token = "Bearer this.is.an.invalid.token.string"
    res_fake = client.get("/users/me", headers={"Authorization": fake_token})
    assert res_fake.status_code == 401


def test_successful_authentication(client):
    """Сценарій: Успішна автентифікація.

    Перевірка успішної реєстрації та отримання доступу (статус 200) з правильними даними.
    """
    # Реєстрація звичайного користувача
    reg_res = client.post(
        "/users/register",
        json={
            "username": "zombie_fan",
            "password": "valid_password_123",
            "full_name": "Zombie Fan",
        },
    )
    assert reg_res.status_code == 200
    user_data = reg_res.json()
    assert user_data["username"] == "zombie_fan"
    assert user_data["role"] == "user"
    assert user_data["is_admin"] is False

    # Успішний вхід
    login_res = client.post(
        "/users/login",
        json={"username": "zombie_fan", "password": "valid_password_123"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["role"] == "user"

    # Перевірка доступу до захищеного маршруту з валідним токеном
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "zombie_fan"


def test_login_failure_scenarios(client):
    """Сценарій: Помилки входу.

    Перевірка відмови в доступі при неправильному паролі або неіснуючому логіні (статус 401).
    """
    # Створюємо користувача для перевірки
    client.post(
        "/users/register",
        json={"username": "alice", "password": "correct_password"},
    )

    # 1. Спроба входу з неправильним паролем
    bad_pass_res = client.post(
        "/users/login",
        json={"username": "alice", "password": "WRONG_password"},
    )
    assert bad_pass_res.status_code == 401
    assert "Невірний логін або пароль" in bad_pass_res.json()["detail"]

    # 2. Спроба входу з неіснуючим іменем користувача
    non_existent_res = client.post(
        "/users/login",
        json={"username": "ghost_user", "password": "correct_password"},
    )
    assert non_existent_res.status_code == 401
    assert "Невірний логін або пароль" in non_existent_res.json()["detail"]

    # 3. Спроба повторної реєстрації того самого імені (перевірка валідації 400)
    duplicate_res = client.post(
        "/users/register",
        json={"username": "alice", "password": "another_password"},
    )
    assert duplicate_res.status_code == 400


def test_vertical_privilege_escalation(client, registered_user, admin_user):
    """Сценарій: Вертикальне розмежування ролей.

    Перевірка заборони доступу звичайному користувачу до адмін-панелі зі статус-кодом 403 Forbidden,
    та надання доступу адміністратору (200 OK).
    """
    # 1. Звичайний користувач намагається зайти в адмін-панель -> 403 Forbidden
    user_headers = registered_user["headers"]
    user_res = client.get("/users/admin-panel", headers=user_headers)
    assert user_res.status_code == 403
    assert "потрібні права адміністратора" in user_res.json()["detail"]

    # 2. Звичайний користувач намагається відкрити адмін-дашборд -> 403 Forbidden
    dashboard_res = client.get("/dashboard/admin", headers=user_headers)
    assert dashboard_res.status_code == 403

    # 3. Адміністратор отримує повний доступ до адмін-панелі -> 200 OK
    admin_headers = admin_user["headers"]
    admin_res = client.get("/users/admin-panel", headers=admin_headers)
    assert admin_res.status_code == 200
    assert "Вітаємо в адмін-панелі" in admin_res.json()["message"]

    # 4. Адміністратор відкриває адмін-дашборд -> 200 OK
    admin_dash_res = client.get("/dashboard/admin", headers=admin_headers)
    assert admin_dash_res.status_code == 200


def test_horizontal_privilege_escalation_user_profile_idor(
    client, registered_user, second_user, admin_user
):
    """Сценарій: Горизонтальне розмежування прав (IDOR) на профілі користувачів.

    Спроба авторизованого користувача змінити дані профілю іншого користувача
    повинна повертати статус 403 Forbidden.
    """
    # user1 намагається змінити профіль user2
    user1_headers = registered_user["headers"]
    user2_id = second_user["id"]

    attack_res = client.put(
        f"/users/{user2_id}",
        json={"full_name": "Hacked by User 1"},
        headers=user1_headers,
    )
    assert attack_res.status_code == 403
    assert "IDOR" in attack_res.json()["detail"]

    # user2 може успішно змінити свій власний профіль
    user2_headers = second_user["headers"]
    legit_res = client.put(
        f"/users/{user2_id}",
        json={"full_name": "Daryl Dixon Legit"},
        headers=user2_headers,
    )
    assert legit_res.status_code == 200
    assert legit_res.json()["full_name"] == "Daryl Dixon Legit"

    # Адміністратор має повноваження оновити будь-який профіль у разі потреби
    admin_headers = admin_user["headers"]
    admin_update_res = client.put(
        f"/users/{user2_id}",
        json={"full_name": "Daryl Dixon (Verified by Overlord)"},
        headers=admin_headers,
    )
    assert admin_update_res.status_code == 200
    assert admin_update_res.json()["full_name"] == "Daryl Dixon (Verified by Overlord)"
