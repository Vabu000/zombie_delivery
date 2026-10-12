# Архітектурне проєктування системи (ЛР №1)

## 1. Загальний огляд архітектури
Проєкт побудовано за принципами багатошарової сервісної архітектури (Tiered Microservice-ready Architecture), що забезпечує високу масштабованість, ізоляцію середовищ та відмовостійкість.

Система складається з таких ключових рівнів:
1. **Клієнтський рівень (Presentation Tier)**:
   - Web UI / SPA (Single Page Application) та мобільні термінали кур'єрів.
   - REST API клієнти, Swagger UI (`/docs`), ReDoc (`/redoc`).
2. **Рівень маршрутизації та балансування (Gateway & Load Balancing Tier)**:
   - **Nginx Reverse Proxy / Load Balancer**: виконує SSL-термінацію, розподіл запитів між пулом воркерів бекенду (Round-Robin або Least-Connected), віддачу статичних файлів та первинний захист від DDoS.
3. **Рівень додатку та бізнес-логіки (Application Tier)**:
   - **FastAPI / Uvicorn Workers**: асинхронний бекенд на Python.
   - Pydantic v2 валідація вхідних даних та схем DTO.
   - JWT (JSON Web Tokens) автентифікація з рольовою моделлю доступу (RBAC).
   - Захист від IDOR (Insecure Direct Object References) на рівні бізнес-сервісів.
   - Глобальний обробник виключень із санітизацією стектрейсів у режимі `DEBUG=False`.
4. **Рівень кешування та черг (Cache & Messaging Tier)**:
   - **Redis Cache**: кешування доступних замовлень (гарячий пул для кур'єрів), rate limiting для запобігання брутфорсу паролів, сесійні блокування (Distributed Locks).
5. **Рівень збереження даних (Persistence Tier)**:
   - **Реляційна СУБД**: PostgreSQL у промисловому середовищі (Production), SQLite у пісочниці (Sandbox) та тестовому оточенні.
   - SQLAlchemy ORM для безпечної взаємодії з БД без ризику SQL Injection.

---

## 2. Схема архітектури системи (Mermaid C4 Diagram)

```mermaid
graph TB
    subgraph Clients["Клієнтські інтерфейси"]
        ClientWeb["Survivor Web Dashboard<br/>(Клієнт-виживаючий)"]
        CourierMobile["Courier Tracker App<br/>(Зомбі-кур'єр)"]
        AdminUI["Overlord Control Panel<br/>(Адміністратор)"]
    end

    subgraph LoadBalancer["Шлюз та балансування навантаження"]
        Nginx["Nginx Reverse Proxy & Load Balancer<br/>:80 / :443 (SSL Termination, Rate Limit)"]
    end

    subgraph BackendCluster["Бекенд-кластер (FastAPI)"]
        Worker1["FastAPI Instance #1<br/>Uvicorn Worker"]
        Worker2["FastAPI Instance #2<br/>Uvicorn Worker"]
        WorkerN["FastAPI Instance #N<br/>Uvicorn Worker"]
    end

    subgraph CachingLayer["Рівень кешування та черг"]
        Redis["Redis Cache & Pub/Sub<br/>(Кеш пулу замовлень, Rate Limiting)"]
    end

    subgraph DatabaseLayer["Рівень збереження даних (Data Isolation)"]
        ProdDB[("Production DB<br/>PostgreSQL / production.db<br/>(DEBUG=False, Ізольовані дані)")]
        SandboxDB[("Sandbox DB<br/>SQLite / sandbox.db<br/>(DEBUG=True, Тестове середовище)")]
    end

    ClientWeb -->|HTTPS / REST API| Nginx
    CourierMobile -->|HTTPS / WebSockets| Nginx
    AdminUI -->|HTTPS / Admin API| Nginx

    Nginx -->|Upstream Round-Robin| Worker1
    Nginx -->|Upstream Round-Robin| Worker2
    Nginx -->|Upstream Round-Robin| WorkerN

    Worker1 <-->|Кешування & Lock| Redis
    Worker2 <-->|Кешування & Lock| Redis
    WorkerN <-->|Кешування & Lock| Redis

    Worker1 -->|ORM Запити| ProdDB
    Worker2 -->|ORM Запити| ProdDB
    WorkerN -->|ORM Запити| ProdDB

    Worker1 -.->|ENV=sandbox| SandboxDB
```

---

## 3. Діаграма послідовності створення та виконання замовлення (Data Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Survivor as Клієнт (Survivor)
    participant API as FastAPI Backend
    participant Auth as JWT Guard & RBAC
    participant DB as Реляційна БД
    actor Courier as Кур'єр (Зомбі)

    Survivor->>API: POST /deliveries/ (Координати, Тип вантажу, Рівень загрози)
    API->>Auth: Перевірка JWT токена
    Auth-->>API: Авторизовано (role: user, id: 1)
    API->>API: Розрахунок винагороди reward_brains (base * danger_mult * prey_mult)
    API->>DB: Збереження замовлення (status: PENDING, owner_id: 1)
    DB-->>API: Збережено (id: 42)
    API-->>Survivor: 201 Created (Деталі замовлення)

    Note over Courier,API: Кур'єр моніторить доступні замовлення
    Courier->>API: GET /deliveries/?status_filter=PENDING
    API->>DB: Запит замовлень у статусі PENDING
    DB-->>API: Список замовлень [id: 42, ...]
    API-->>Courier: 200 OK (Список доступних доставок)

    Courier->>API: POST /deliveries/42/claim
    API->>Auth: Перевірка ролі (потрібен courier або admin)
    Auth-->>API: Доступ дозволено (role: courier, id: 7)
    API->>DB: Оновлення статусу -> IN_TRANSIT, courier_id -> 7
    DB-->>API: Оновлено
    API-->>Courier: 200 OK (Замовлення взято в рейс)

    Note over Courier,Survivor: Доставка через небезпечну зону
    Courier->>API: POST /deliveries/42/complete
    API->>DB: Оновлення статусу -> DELIVERED
    DB-->>API: Оновлено
    API-->>Courier: 200 OK (Доставку завершено, винагороду нараховано)
```

---

## 4. Політика безпеки та ізоляції середовищ
1. **Розділення налаштувань**: Усі конфігурації завантажуються виключно через змінні середовища за допомогою `pydantic-settings`.
2. **Ізоляція баз даних**:
   - У тестовому середовищі (`ENV=sandbox`) застосовується `sandbox.db`.
   - У робочому середовищі (`ENV=production`) застосовується `production.db` (або виділений інстанс PostgreSQL).
3. **Захист від витоку даних при збоях (500 Error Sanitization)**:
   - При `DEBUG=False` у Production будь-яка непередбачена системна помилка перехоплюється глобальним middleware і клієнту повертається безпечна уніфікована JSON-відповідь: `{"message": "Internal Server Error (Zombie systems are down). Please contact system administrator."}`.
   - Жодні назви бібліотек, внутрішні шляхи до файлів, рядки вихідного коду чи змінні стектрейсу не потрапляють у відповідь клієнту.
4. **Захист від горизонтального підвищення привілеїв (IDOR)**:
   - Кожна операція читання (`GET /deliveries/{id}`), редагування (`PUT /deliveries/{id}`), видалення (`DELETE /deliveries/{id}`) та оновлення профілю (`PUT /users/{id}`) перевіряє право власності: `owner_id == current_user.id or current_user.is_admin`. У разі невідповідності повертається `403 Forbidden`.
