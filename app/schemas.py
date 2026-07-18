from pydantic import BaseModel, validator
from typing import List
from datetime import datetime


class Widget(BaseModel):
    # placeholder
    pass


class Layout(BaseModel):
    # placeholder
    pass


class DashboardBase(BaseModel):
    schema_version: str = "1.0"
    dashboard_id: str
    title: str
    layout: Layout
    widgets: List[Widget]

    @validator('dashboard_id')
    def validate_dashboard_id(cls, v):
        if not v or not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError(
                'dashboard_id должен содержать только буквы, цифры, - и _')
        return v


class DashboardCreate(DashboardBase):  # POST
    pass


class DashboardResponse(DashboardBase):  # GET
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


