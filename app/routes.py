from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List

from . import crud, schemas
from .database import get_db
from .auth import require_designer

router = APIRouter(prefix="/api/v1", tags=["dashboards"])

responses_auth = {
    400: {"description": "Неверный запрос (например, неверная роль)"},
    403: {"description": "Доступ запрещен: только для Designer"},
}
responses_not_found = {404: {"description": "Дашборд не найден"}}

@router.post("/dashboards",
             response_model=schemas.DashboardResponse,
             status_code=status.HTTP_201_CREATED,
             responses={**responses_auth, 409: {"description": "Конфликт: дашборд с таким ID уже существует"}})
def create_dashboard(dashboard: schemas.DashboardCreate,
                     user_id: str = Header(..., alias="User-id", description="ID пользователя (автора)"),
                     db: Session = Depends(get_db),
                     role: str = Depends(require_designer)):
    """Создать новый дашборд"""
    dashboard.author = user_id
    existing = crud.get_dashboard(db, dashboard.dashboard_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Дашборд с dashboard_id '{
                dashboard.dashboard_id}' уже существует"
        )
    return crud.create_dashboard(db, dashboard)


@router.get("/dashboards/{dashboard_id}",
            response_model=schemas.DashboardResponse,
            responses=responses_not_found)
def get_dashboard(dashboard_id: str, db: Session = Depends(get_db)):
    """Получить дашборд"""
    dashboard = crud.get_dashboard(db, dashboard_id)
    if not dashboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дашборд с dashboard_id '{dashboard_id}' не найден"
        )
    return dashboard


@router.get("/dashboards",
            response_model=List[schemas.DashboardResponse])
def get_all_dashboards(skip: int = 0, limit: int = 100,
                       db: Session = Depends(get_db)):
    """Получить все дашборды"""
    return crud.get_all_dashboards(db, skip=skip, limit=limit)


@router.put("/dashboards/{dashboard_id}",
            response_model=schemas.DashboardResponse,
            responses={**responses_auth, **responses_not_found})
def update_dashboard(dashboard_id: str, dashboard: schemas.DashboardCreate,
                     db: Session = Depends(get_db),
                     role: str = Depends(require_designer)):
    """Обновить дашборд"""
    if dashboard_id != dashboard.dashboard_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dashboard_id в пути и в теле запроса не совпадают"
        )

    updated = crud.update_dashboard(db, dashboard_id, dashboard)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дашборд с dashboard_id '{dashboard_id}' не найден"
        )
    return updated


@router.delete("/dashboards/{dashboard_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               responses={**responses_auth, **responses_not_found})
def delete_dashboard(dashboard_id: str, db: Session = Depends(get_db), role: str = Depends(require_designer)):
    """Удалить дашборд"""
    deleted = crud.delete_dashboard(db, dashboard_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дашборд с dashboard_id '{dashboard_id}' не найден"
        )
    return None  # 204 No Content


@router.get("/sources")
def get_sources():
    """Получить список источников"""
    # placeholder
    return [
        {"id": "csv_provider", "name": "CSV файлы", "type": "file"},
        {"id": "postgres", "name": "PostgreSQL", "type": "database"},
        {"id": "clickhouse", "name": "ClickHouse", "type": "database"},
        {"id": "api_provider", "name": "Внешний API", "type": "http"}
    ]


@router.get("/widgets")
def get_widgets():
    """Получить список виджетов"""
    # placeholder
    return [
        {"id": "line_chart", "name": "Линейный график", "category": "chart"},
        {"id": "bar_chart", "name": "Столбчатая диаграмма", "category": "chart"},
        {"id": "pie_chart", "name": "Круговая диаграмма", "category": "chart"},
        {"id": "table", "name": "Таблица", "category": "table"},
        {"id": "map", "name": "Карта", "category": "map"},
        {"id": "metric", "name": "Метрика (число)", "category": "metric"}
    ]


@router.post("/login/")
def login(username: str, role: str):
    return {"message": f"Пользователь {username} вошел как {role}", "role": role}
