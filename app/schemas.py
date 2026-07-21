from pydantic import BaseModel, validator
from typing import List, Dict, Optional, Any
from datetime import datetime


class Position(BaseModel):
    x: int
    y: int
    w: int
    h: int


class Dataset(BaseModel):
    """Единый табличный формат данных"""
    dataset_id: str
    columns: List[Dict[str, str]]
    rows: List[List[Any]]


class Widget(BaseModel):
    """Виджет с единым контрактом рендеринга"""
    widget_id: str
    type: str  # line_chart, bar_chart, pie_chart, kpi_card, table
    position: Position
    # настройки виджета: x_field, y_field, title, aggregation, и т.д.
    config: dict

    @validator('type')
    def validate_widget_type(cls, v):
        allowed = ["line_chart", "bar_chart", "pie_chart", "kpi_card", "table"]
        if v not in allowed:
            raise ValueError(f'Тип виджета должен быть одним из: {
                             ", ".join(allowed)}')
        return v


class Layout(BaseModel):
    type: str = "grid"
    columns: int = 1


class DashboardBase(BaseModel):
    schema_version: str = "1.0"
    dashboard_id: str
    title: str
    layout: Layout
    widgets: List[Widget]
    datasets: Optional[List[Dataset]] = []  # данные для виджетов

    @validator('dashboard_id')
    def validate_dashboard_id(cls, v):
        if not v or not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                'dashboard_id должен содержать только буквы, цифры, - и _')
        return v


class DashboardCreate(DashboardBase):  # POST
    dashboard_id: str
    title: str
    layout: Dict
    widgets: List
    author: Optional[str] = None


class DashboardResponse(DashboardCreate):  # GET
    id: int
    author: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    role: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes: True
