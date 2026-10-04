from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.config import settings
from src.database import Base, engine
from src.routers import users, deliveries

# Ініціалізація таблиць (в реальному проекті використовується Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(debug=settings.DEBUG, title="Zombie Night Delivery Aggregator")


# Глобальний обробник 500 помилок (ЛР №3)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if not settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error (Zombie systems are down)"},
        )
    return JSONResponse(status_code=500, content={"message": f"Dev Error: {str(exc)}"})


@app.get("/")
def home():
    return {"message": "Welcome to the Zombie Delivery System!"}


app.include_router(users.router)
app.include_router(deliveries.router)
