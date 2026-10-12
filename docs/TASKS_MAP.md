# 🗺️ Навігаційна карта реалізації завдань (ЛР №1, ЛР №2, ЛР №3)

Цей документ створено спеціально для того, щоб ви могли швидко зорієнтуватися в проєкті та впевнено продемонструвати викладачу виконання кожного пункту завдань на максимальний бал.

---

# 📌 Лабораторна робота №1: Базовий каркас, Архітектура та Контроль якості

| № | Вимога завдання | Бали | Де саме реалізовано у проєкті | Як продемонструвати викладачу |
|---|---|:---:|---|---|
| **1** | **Вибір предметної області**<br>Вибір, опис сутностей та обґрунтування актуальності. | **Основні (частина 6 б.)** | 📄 [docs/domain_choice.md](domain_choice.md)<br>Предметна область: **Zombie Night Delivery Aggregator** (агрегатор нічної логістики провізії в постапокаліпсисі). | Показати документ [docs/domain_choice.md](domain_choice.md) з детальним аналізом ролей, проблем нічної доставки та бізнес-логіки. |
| **2** | **Архітектурне проєктування**<br>Опис взаємодії клієнтів, бекенду, БД, кешування та балансування. | **Основні (частина 6 б.)** | 📄 [docs/architecture.md](architecture.md)<br>Розділи 1-4: клієнти (Web/Mobile), Nginx Load Balancer, FastAPI кластер, Redis кеш, ізольовані БД. | Відкрити [docs/architecture.md](architecture.md) та показати діаграми Mermaid (C4 Container Diagram та Sequence Diagram). |
| **3** | **Ініціалізація репозиторію**<br>Організована структура директорій (код, документація, конфігурація). | **Основні (частина 6 б.)** | Структура репозиторію:<br>• `src/` — вихідний код додатку<br>• `docs/` — технічна та архітектурна документація<br>• `tests/` — модульні та інтеграційні тести<br>• `.env.*` — ізольовані конфігурації | Виконати команду `tree /F` або показати дерево каталогів у провіднику / редакторі. |
| **4** | **Базовий каркас проєкту**<br>FastAPI додаток + початкові налаштування реляційної БД. | **Основні (частина 6 б.)** | 🐍 [src/main.py](../src/main.py) — екземпляр `FastAPI`<br>🐍 [src/database.py](../src/database.py) — підключення SQLAlchemy (`engine`, `SessionLocal`, `Base`) | Запустити сервер `uvicorn src.main:app` та відкрити [http://localhost:8000/docs](http://localhost:8000/docs). |
| **5** | **Графічне представлення архітектурних рішень**<br>Зображення архітектури у вигляді схем/зображень. | **Додаткові (1 бал)** | 🎨 [docs/architecture_diagram.svg](architecture_diagram.svg)<br>Високоякісна векторна SVG діаграма з відображенням усіх рівнів системи. | Відкрити файл [docs/architecture_diagram.svg](architecture_diagram.svg) у веб-браузері. |
| **6** | **Інтеграція інструментів контролю якості коду**<br>Ruff (лінтер + форматер, замінює flake8/black). | **Додаткові (1 бал)** | ⚙️ [pyproject.toml](../pyproject.toml) — конфігурація `[tool.ruff]`<br>⚙️ [requirements.txt](../requirements.txt) — залежності `ruff` | Виконати команди:<br>`ruff check .`<br>`ruff format --check .` |
| **7** | **Налаштування та демонстрація pre-commit хуків**<br>Блокування коміту при синтаксичних чи стильових помилках. | **Додаткові (2 бали)** | ⚙️ [.pre-commit-config.yaml](../.pre-commit-config.yaml)<br>📄 [docs/pre_commit_guide.md](pre_commit_guide.md)<br>📜 [scripts/demo_pre_commit.ps1](../scripts/demo_pre_commit.ps1) | Запустити `pre-commit run --all-files` або запустити скрипт демонстрації `.\scripts\demo_pre_commit.ps1`. |

---

# 📌 Лабораторна робота №2: Аутентифікація, Ролі, MVP бізнес-логіки та Pytest

| № | Вимога завдання | Бали | Де саме реалізовано у проєкті | Як продемонструвати викладачу |
|---|---|:---:|---|---|
| **1** | **Модифікувати проєкт** | **Основні (частина 5 б.)** | Розширено попередню кодову базу модульною структурою (`src/routers/`). | Продемонструвати підключення роутерів у [src/main.py](../src/main.py). |
| **2** | **База даних користувачів** | **Основні (частина 5 б.)** | 🐍 [src/models.py](../src/models.py) (`class User`) — поля `id`, `username`, `hashed_password`, `role`, `is_admin`, `full_name`, `created_at`. | Показати модель `User` у [src/models.py](../src/models.py) та створення таблиць `Base.metadata.create_all`. |
| **3** | **Декілька ролей користувачів**<br>Мінімум 2 ролі: адмін та звичайний користувач (+ кур'єр). | **Основні (частина 5 б.)** | 🐍 [src/models.py](../src/models.py) (`class UserRole`):<br>• `UserRole.USER` = "user"<br>• `UserRole.COURIER` = "courier"<br>• `UserRole.ADMIN` = "admin" | Показати константи ролей у [src/models.py](../src/models.py) та гарди `require_admin`, `require_courier_or_admin` у [src/auth.py](../src/auth.py). |
| **4** | **Реєстрація для звичайних користувачів** | **Основні (частина 5 б.)** | 🐍 [src/routers/users.py](../src/routers/users.py):<br>• `POST /users/register` — звичайний клієнт<br>• `POST /users/register-admin` — адмін (захищено ключем)<br>• `POST /users/register-courier` — кур'єр | Виконати у Swagger або pytest:<br>`test_successful_authentication` |
| **5** | **Можливість входу для різних типів користувачів** | **Основні (частина 5 б.)** | 🐍 [src/routers/users.py](../src/routers/users.py):<br>• `POST /users/login` — перевірка хешу пароля bcrypt, видача JWT токена з роллю. | Виконати у Swagger або pytest:<br>`test_successful_authentication` |
| **6** | **Домашні сторінки-заглушки для різних користувачів** | **Основні (частина 5 б.)** | 🐍 [src/routers/dashboard.py](../src/routers/dashboard.py):<br>• `/dashboard/user` — кабінет клієнта-виживалого<br>• `/dashboard/courier` — кабінет зомбі-кур'єра<br>• `/dashboard/admin` — командний центр Overlord<br>• `/dashboard/` — публічний портал-хаб<br>*(Підтримує як красивий Dark Zombie HTML для браузера, так і структурований JSON)* | Відкрити у браузері [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/) або запустити `pytest tests/test_dashboard_stubs.py`. |
| **7** | **Додати оновлений код до Git та обґрунтувати рішення** | **Основні (частина 5 б.)** | Git-історія комітів + обґрунтування у [docs/architecture.md](architecture.md) та [README.md](../README.md). | Показати `git log --oneline` та розділ архітектурних рішень у документації. |
| **8** | **MVP базової бізнес-логіки (2 бали)**<br>Повноцінна функціональність предметної області. | **Додаткові (2 бали)** | 🐍 [src/routers/deliveries.py](../src/routers/deliveries.py):<br>• `POST /deliveries/` — створення доставки з авторозрахунком винагороди `reward_brains`<br>• `GET /deliveries/` — фільтрований список доставок згідно з роллю<br>• `GET /deliveries/{id}` — деталі замовлення<br>• `PUT /deliveries/{id}` — редагування маршруту (до відправлення)<br>• `POST /deliveries/{id}/claim` — взяття в рейс кур'єром<br>• `POST /deliveries/{id}/complete` — завершення доставки<br>• `DELETE /deliveries/{id}` — скасування | Запустити тести MVP:<br>`pytest tests/test_deliveries.py -v` |
| **9** | **Pytest: Юніт- та інтеграційні тести контролю доступу (3 бали)** | **Додаткові (3 бали)** | 🧪 [tests/test_auth.py](../tests/test_auth.py)<br>🧪 [tests/test_deliveries.py](../tests/test_deliveries.py)<br>*(Всі 4 обов'язкові сценарії перевірки)* | Запустити `pytest -v` (16 успішних тестів). |

### Специфікація сценаріїв тестування (ЛР №2):
1. **Анонімний доступ (401 Unauthorized)**:
   - Функція: `test_anonymous_access_unauthorized` у [tests/test_auth.py](../tests/test_auth.py)
   - Функція: `test_deliveries_anonymous_access` у [tests/test_deliveries.py](../tests/test_deliveries.py)
   - Перевіряє відхилення запитів без Bearer токена або з підробленим токеном.
2. **Успішна автентифікація та помилки входу (200 OK / 401 Unauthorized)**:
   - Функція: `test_successful_authentication` у [tests/test_auth.py](../tests/test_auth.py)
   - Функція: `test_login_failure_scenarios` у [tests/test_auth.py](../tests/test_auth.py)
   - Перевіряє успішний логін (200), невірний пароль (401) та неіснуючого користувача (401).
3. **Вертикальне розмежування ролей (403 Forbidden)**:
   - Функція: `test_vertical_privilege_escalation` у [tests/test_auth.py](../tests/test_auth.py)
   - Функція: `test_courier_workflow_and_role_escalation_guard` у [tests/test_deliveries.py](../tests/test_deliveries.py)
   - Перевіряє заборону доступу звичайному користувачу до адмін-панелі (403), взяття доставки кур'єра (403) та успішний доступ адміна (200).
4. **Горизонтальне розмежування прав IDOR (403 Forbidden)**:
   - Функція: `test_horizontal_privilege_escalation_user_profile_idor` у [tests/test_auth.py](../tests/test_auth.py)
   - Функція: `test_horizontal_idor_on_delivery_entity` у [tests/test_deliveries.py](../tests/test_deliveries.py)
   - Перевіряє спроби змінити чужий профіль (403), переглянути чужу доставку (403), змінити чужу доставку (403) або видалити чужу доставку (403).

---

# 📌 Лабораторна робота №3: Конфігурації, Ізоляція БД, Безпека та CI/CD

| № | Вимога завдання | Бали | Де саме реалізовано у проєкті | Як продемонструвати викладачу |
|---|---|:---:|---|---|
| **1** | **Розділення конфігурацій через змінні оточення**<br>Жодних hardcoded значень, зчитування `.env.sandbox` та `.env.production`. | **Основні (частина 7 б.)** | ⚙️ [.env.sandbox](../.env.sandbox)<br>⚙️ [.env.production](../.env.production)<br>🐍 [src/config.py](../src/config.py) (`pydantic-settings`) | Показати обидва `.env` файли та завантаження налаштувань у [src/config.py](../src/config.py). |
| **2** | **Ізоляція баз даних**<br>Окремі БД для Sandbox (`sandbox.db`) та Production (`production.db`). | **Основні (частина 7 б.)** | ⚙️ [.env.sandbox](../.env.sandbox) (`DATABASE_URL=sqlite:///./sandbox.db`)<br>⚙️ [.env.production](../.env.production) (`DATABASE_URL=sqlite:///./production.db`)<br>🐍 [src/database.py](../src/database.py) | Показати рядки підключення у конфігах. Запустити з `$env:ENV="sandbox"` та `$env:ENV="production"` і показати створення двох різних файлів БД. |
| **3** | **Налаштування режимів безпеки**<br>• `DEBUG=False` у Production.<br>• Приховування внутрішніх стектрейсів коду при помилці 500. | **Основні (частина 7 б.)** | ⚙️ [.env.production](../.env.production) (`DEBUG=False`)<br>🐍 [src/main.py](../src/main.py) (`@app.exception_handler(Exception)`)<br>🧪 [tests/test_safety.py](../tests/test_safety.py) | Запустити тест:<br>`pytest tests/test_safety.py -v`<br>Показати в [src/main.py](../src/main.py) перевірку `if not settings.DEBUG`. |
| **4** | **Документування**<br>Оновлений README.md з інструкціями для обох середовищ. | **Основні (частина 7 б.)** | 📄 [README.md](../README.md)<br>Розділи: Sandbox, Production, Pytest, Ruff, Pre-commit. | Відкрити [README.md](../README.md). |
| **5** | **Варіант A: CI/CD пайплайн**<br>Автоматичний запуск у GitHub Actions на PR та push у main/master (Ruff + Pytest). | **Додаткові (3 бали)** | 🤖 [.github/workflows/main.yml](../.github/workflows/main.yml) | Відкрити [.github/workflows/main.yml](../.github/workflows/main.yml) та показати кроки `ruff check .`, `ruff format --check .`, `pytest tests/ -v`. |

---

## ⚡ Швидкі команди для демонстрації проекту

```bash
# 1. Запуск усіх тестів (16 тестів, 100% проходження):
pytest -v

# 2. Перевірка якості коду лінтером Ruff:
ruff check .
ruff format --check .

# 3. Перевірка pre-commit хуків:
pre-commit run --all-files

# 4. Запуск у тестовому середовищі (Sandbox):
# PowerShell:
$env:ENV="sandbox"; uvicorn src.main:app --reload
# Bash:
export ENV=sandbox && uvicorn src.main:app --reload

# 5. Запуск у робочому середовищі (Production):
# PowerShell:
$env:ENV="production"; uvicorn src.main:app
# Bash:
export ENV=production && uvicorn src.main:app
```
