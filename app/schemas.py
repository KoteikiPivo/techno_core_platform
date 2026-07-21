from pydantic import BaseModel, validator, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class Position(BaseModel):
    x: int
    y: int
    w: int
    h: int


class DataSource(BaseModel):
    provider: str = Field(...,
                          description="Провайдер данных (например, csv_provider)")
    dataset_id: str = Field(..., description="ID набора данных")


class Dataset(BaseModel):
    """Единый табличный формат данных"""
    dataset_id: str
    columns: List[Dict[str, str]]
    rows: List[List[Any]]


class Widget(BaseModel):
    """Виджет с единым контрактом рендеринга"""
    widget_id: str = Field(...,
                           description="Провайдер данных (например, csv_provider)")
    # line_chart, bar_chart, pie_chart, kpi_card, table
    type: str = Field(..., description="Тип виджета (line_chart, bar_chart, pie_chart, kpi_card, table)")
    position: Dict[str, int] = Field(..., description="Координаты x, y, w, h")
    data_source: Optional[DataSource] = Field(
        None, description="Источник данных виджет")
    # настройки виджета: x_field, y_field, title, aggregation, и т.д.
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Настройки виджета")

    @validator('type')
    def validate_widget_type(cls, v):
        allowed = ["line_chart", "bar_chart", "pie_chart", "kpi_card", "table"]
        if v not in allowed:
            raise ValueError(f'Тип виджета должен быть одним из: {
                             ", ".join(allowed)}')
        return v


class Layout(BaseModel):
    type: str = Field(default="grid", description="Тип сетки")
    columns: int = Field(default=12, description="Количество колонок")


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
