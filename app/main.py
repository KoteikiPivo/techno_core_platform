from fastapi import FastAPI
from .database import engine, Base
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dashboard API",
    description="Сервис для хранения и управления дашбордами",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Dashboard API работает", "docs": "/docs"}
