from sqlalchemy.orm import Session
from . import database, schemas


def create_dashboard(db: Session, dashboard: schemas.DashboardCreate):
    """Создать новый дашборд"""
    db_dashboard = database.Dashboard(
        dashboard_id=dashboard.dashboard_id,
        schema_version=dashboard.schema_version,
        title=dashboard.title,
        layout=dashboard.layout,  # Pydantic model to dict
        widgets=dashboard.widgets,
        author=dashboard.author
    )
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


def get_dashboard(db: Session, dashboard_id: str):
    """Получить дашборд"""
    return db.query(database.Dashboard).filter(
        database.Dashboard.dashboard_id == dashboard_id
    ).first()


def get_all_dashboards(db: Session, skip: int = 0, limit: int = 100):
    """Получить все дашборды"""
    return db.query(database.Dashboard).offset(skip).limit(limit).all()


def update_dashboard(db: Session, dashboard_id: str,
                     dashboard_update: schemas.DashboardCreate):
    """Обновить дашборд"""
    db_dashboard = get_dashboard(db, dashboard_id)
    if not db_dashboard:
        return None

    db_dashboard.schema_version = dashboard_update.schema_version
    db_dashboard.title = dashboard_update.title
    db_dashboard.layout = dashboard_update.layout.model_dump()
    db_dashboard.widgets = [w.model_dump() for w in dashboard_update.widgets]

    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


def delete_dashboard(db: Session, dashboard_id: str):
    """Удалить дашборд"""
    db_dashboard = get_dashboard(db, dashboard_id)
    if not db_dashboard:
        return None

    db.delete(db_dashboard)
    db.commit()
    return True


def create_user(db: Session, user: schemas.UserCreate):
    db_user = database.User(username=user.username, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(database.User).filter(database.User.id == user_id).first()
