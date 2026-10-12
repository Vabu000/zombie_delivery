from typing import Optional

from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.auth import get_current_user, require_admin, require_courier_or_admin
from src.database import get_db
from src.models import Delivery, DeliveryStatus, User

router = APIRouter(prefix="/dashboard", tags=["Dashboard Stubs"])


def render_html_page(title: str, role_badge: str, content_html: str) -> HTMLResponse:
    html = f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Zombie Delivery</title>
    <style>
        :root {{
            --bg-dark: #0a0e14;
            --card-bg: #141b24;
            --border-color: #233142;
            --toxic-green: #00ff88;
            --blood-red: #ff3366;
            --amber-warn: #ffaa00;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
        }}
        body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}
        header {{
            background: rgba(20, 27, 36, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--toxic-green);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .role-tag {{
            background: rgba(0, 255, 136, 0.15);
            color: var(--toxic-green);
            border: 1px solid var(--toxic-green);
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .role-tag.admin {{
            background: rgba(255, 51, 102, 0.15);
            color: var(--blood-red);
            border-color: var(--blood-red);
        }}
        .role-tag.courier {{
            background: rgba(255, 170, 0, 0.15);
            color: var(--amber-warn);
            border-color: var(--amber-warn);
        }}
        main {{
            flex: 1;
            max-width: 1000px;
            margin: 2rem auto;
            padding: 0 1.5rem;
            width: 100%;
            box-sizing: border-box;
        }}
        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.75rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }}
        h1, h2, h3 {{
            margin-top: 0;
            color: #ffffff;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        .metric-card {{
            background: #0d1218;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.2rem;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            color: var(--toxic-green);
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 4px;
        }}
        .btn {{
            display: inline-block;
            background: var(--toxic-green);
            color: #000000;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            transition: all 0.2s ease;
            margin-right: 8px;
            margin-bottom: 8px;
        }}
        .btn:hover {{
            background: #00cc6a;
            transform: translateY(-2px);
        }}
        .btn-outline {{
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
        }}
        .btn-outline:hover {{
            border-color: var(--toxic-green);
            color: var(--toxic-green);
        }}
        footer {{
            text-align: center;
            padding: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span>🧟</span> Zombie Delivery Network
        </div>
        <div>
            {role_badge}
        </div>
    </header>
    <main>
        {content_html}
    </main>
    <footer>
        Zombie Night Delivery Aggregator &copy; 2026. Sandbox & Production Safe Architecture.
    </footer>
</body>
</html>"""
    return HTMLResponse(content=html)


@router.get("/")
def dashboard_hub(accept: str = Header(default="")):
    """Головний навігаційний портал / хаб системи."""
    if "text/html" in accept:
        content = """
        <div class="card">
            <h1>🧟 Ласкаво просимо до Zombie Night Delivery Aggregator</h1>
            <p>Система нічної постапокаліптичної агрегації та маршрутизації замовлень.</p>
            <div class="grid">
                <div class="metric-card">
                    <div class="metric-value">👤</div>
                    <div class="metric-label"><a href="/dashboard/user" class="btn">Кабінет Клієнта</a></div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">🏍️</div>
                    <div class="metric-label"><a href="/dashboard/courier" class="btn btn-outline">Кабінет Кур'єра</a></div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">🧠</div>
                    <div class="metric-label"><a href="/dashboard/admin" class="btn btn-outline">Панель Overlord</a></div>
                </div>
            </div>
            <p><a href="/docs" class="btn btn-outline">Документація Swagger UI</a></p>
        </div>
        """
        return render_html_page("Портал", '<span class="role-tag">Публічний Хаб</span>', content)
    return {
        "title": "Zombie Night Delivery Portal",
        "description": "Агрегатор нічної доставки в умовах зомбі-апокаліпсису",
        "stubs": {
            "user_dashboard": "/dashboard/user",
            "courier_dashboard": "/dashboard/courier",
            "admin_dashboard": "/dashboard/admin",
        },
        "api_docs": "/docs",
    }


@router.get("/user")
def user_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    format: Optional[str] = Query(None),
    accept: str = Header(default=""),
):
    """Домашня сторінка-заглушка для звичайного користувача (клієнта-виживалого)."""
    my_deliveries = db.query(Delivery).filter(Delivery.owner_id == current_user.id).all()
    total_orders = len(my_deliveries)
    active_orders = sum(
        1 for d in my_deliveries if d.status in [DeliveryStatus.PENDING, DeliveryStatus.IN_TRANSIT]
    )

    if (format != "json") and ("text/html" in accept):
        content = f"""
        <div class="card">
            <h2>Привіт, Виживаючий <b>{current_user.username}</b>!</h2>
            <p>Це ваша домашня сторінка клієнта у системі Zombie Delivery. Тут ви можете створювати замовлення на провізію та відстежувати кур'єрів.</p>
            <div class="grid">
                <div class="metric-card">
                    <div class="metric-value">{total_orders}</div>
                    <div class="metric-label">Всього замовлень</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{active_orders}</div>
                    <div class="metric-label">Активних доставок</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">SECURE</div>
                    <div class="metric-label">Статус бункера</div>
                </div>
            </div>
            <h3>Швидкі дії клієнта:</h3>
            <a href="/docs#/Deliveries/create_delivery_deliveries__post" class="btn">+ Нове замовлення провізії</a>
            <a href="/docs#/Deliveries/get_deliveries_deliveries__get" class="btn btn-outline">Мої замовлення</a>
        </div>
        """
        return render_html_page(
            "Кабінет Виживалого",
            f'<span class="role-tag">Клієнт: {current_user.username}</span>',
            content,
        )

    return {
        "title": "Домашня сторінка користувача-виживалого",
        "username": current_user.username,
        "role": current_user.role,
        "total_orders": total_orders,
        "active_orders": active_orders,
        "accessible_features": [
            "Створення замовлень здобичі/провізії (POST /deliveries/)",
            "Перегляд виключно власних замовлень (GET /deliveries/)",
            "Редагування власних маршрутів до відправлення (PUT /deliveries/{id})",
            "Оновлення особистого профілю (PUT /users/{id})",
        ],
    }


@router.get("/courier")
def courier_dashboard(
    current_user: User = Depends(require_courier_or_admin),
    db: Session = Depends(get_db),
    format: Optional[str] = Query(None),
    accept: str = Header(default=""),
):
    """Домашня сторінка-заглушка для кур'єра зомбі (нічного мисливця)."""
    pending_count = db.query(Delivery).filter(Delivery.status == DeliveryStatus.PENDING).count()
    my_active_count = (
        db.query(Delivery)
        .filter(
            Delivery.courier_id == current_user.id,
            Delivery.status == DeliveryStatus.IN_TRANSIT,
        )
        .count()
    )

    if (format != "json") and ("text/html" in accept):
        content = f"""
        <div class="card">
            <h2>Мисливець <b>{current_user.username}</b> готовий до нічної зміни!</h2>
            <p>Панель нічного кур'єра зомбі. Виконуйте доставку через небезпечні зони зараження за винагороду.</p>
            <div class="grid">
                <div class="metric-card">
                    <div class="metric-value">{pending_count}</div>
                    <div class="metric-label">Доступно замовлень у пулі</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{my_active_count}</div>
                    <div class="metric-label">Ваших активних рейсів</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">HUNTING</div>
                    <div class="metric-label">Режим полювання</div>
                </div>
            </div>
            <h3>Дії кур'єра:</h3>
            <a href="/docs#/Deliveries/claim_delivery_deliveries__delivery_id__claim_post" class="btn">Взяти замовлення в рейс</a>
            <a href="/docs#/Deliveries/get_deliveries_deliveries__get" class="btn btn-outline">Переглянути доступні замовлення</a>
        </div>
        """
        return render_html_page(
            "Панель Кур'єра",
            f'<span class="role-tag courier">Кур\'єр: {current_user.username}</span>',
            content,
        )

    return {
        "title": "Домашня сторінка кур'єра зомбі",
        "username": current_user.username,
        "role": current_user.role,
        "pending_pool": pending_count,
        "my_active_deliveries": my_active_count,
        "accessible_features": [
            "Перегляд доступних замовлень (GET /deliveries/?status_filter=PENDING)",
            "Взяття замовлення в доставку (POST /deliveries/{id}/claim)",
            "Завершення доставки (POST /deliveries/{id}/complete)",
            "Зміна статусу доставки (PATCH /deliveries/{id}/status)",
        ],
    }


@router.get("/admin")
def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    format: Optional[str] = Query(None),
    accept: str = Header(default=""),
):
    """Домашня сторінка-заглушка для адміністратора (Overlord)."""
    users_count = db.query(User).count()
    total_deliveries = db.query(Delivery).count()
    active_deliveries = (
        db.query(Delivery)
        .filter(Delivery.status.in_([DeliveryStatus.PENDING, DeliveryStatus.IN_TRANSIT]))
        .count()
    )

    if (format != "json") and ("text/html" in accept):
        content = f"""
        <div class="card">
            <h2>Командний пункт Overlord <b>{current_user.username}</b></h2>
            <p>Глобальне керування нічною логістичною мережею Zombie Delivery. Повний контроль над користувачами та маршрутами.</p>
            <div class="grid">
                <div class="metric-card">
                    <div class="metric-value">{users_count}</div>
                    <div class="metric-label">Зареєстровано суб'єктів</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_deliveries}</div>
                    <div class="metric-label">Всього доставок у системі</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{active_deliveries}</div>
                    <div class="metric-label">Активних місій</div>
                </div>
            </div>
            <h3>Адміністративні функції:</h3>
            <a href="/users/admin-panel" class="btn">Системний статус</a>
            <a href="/docs#/Deliveries/get_deliveries_deliveries__get" class="btn btn-outline">Глобальний моніторинг усіх доставок</a>
        </div>
        """
        return render_html_page(
            "Overlord Command Center",
            f'<span class="role-tag admin">ADMIN: {current_user.username}</span>',
            content,
        )

    return {
        "title": "Адміністративна панель Hive Overlord",
        "username": current_user.username,
        "role": current_user.role,
        "total_users": users_count,
        "total_deliveries": total_deliveries,
        "active_deliveries": active_deliveries,
        "accessible_features": [
            "Глобальний доступ до всіх замовлень (GET /deliveries/)",
            "Модифікація та скасування будь-яких замовлень",
            "Моніторинг користувачів та кур'єрів",
            "Доступ до адмін-панелі (GET /users/admin-panel)",
        ],
    }
