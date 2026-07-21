from fastapi import HTTPException, Header, Depends
from typing import Literal


def check_role(role: Literal["Designer", "Viewer"] = Header(..., description="Роль пользователя. Допустимые: Designer, Viewer")):
    if role not in ["Designer", "Viewer"]:
        raise HTTPException(status_code=400, detail="Неверная роль. Допустимые: Designer, Viewer")
    return role


def require_designer(role: str = Depends(check_role)):
    if role != "Designer":
        raise HTTPException(
            status_code=403, detail="Доступ запрещен: только для Designer")
    return role
