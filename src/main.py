from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.config import settings
from src.database import Base, engine
from src.routers import dashboard, deliveries, users

# Ініціалізація структури бази даних
Base.metadata.create_all(bind=engine)

app = FastAPI(
    debug=settings.DEBUG,
    title="Zombie Night Delivery Aggregator",
    description="Агрегатор нічної доставки та логістики в постапокаліптичному світі.",
    version="1.0.0",
)


# Глобальний обробник 500 помилок (ЛР №3 - безпека: приховування стек-трейсів у Production)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if not settings.DEBUG:
        # У Production-середовищі (DEBUG=False) користувачеві не показуються деталі чи стектрейси коду
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Server Error (Zombie systems are down). Please contact system administrator."
            },
        )
    # У Sandbox / Dev середовищі (DEBUG=True) повертаємо деталізовану інформацію для відладки
    return JSONResponse(
        status_code=500,
        content={"message": f"Dev Error: {exc!s}", "type": type(exc).__name__},
    )


@app.get("/")
def home():
    return {
        "message": "Welcome to the Zombie Night Delivery System!",
        "environment": settings.ENV,
        "debug_mode": settings.DEBUG,
        "dashboards": {
            "hub": "/dashboard/",
            "user": "/dashboard/user",
            "courier": "/dashboard/courier",
            "admin": "/dashboard/admin",
        },
        "docs": "/docs",
    }


# Допоміжний маршрут для тестування глобального обробника 500 помилок
@app.get("/debug/trigger-500", include_in_schema=False)
def trigger_simulated_error():
    raise RuntimeError("Simulated internal zombie apocalypse system failure")


app.include_router(users.router)
app.include_router(deliveries.router)
app.include_router(dashboard.router)
