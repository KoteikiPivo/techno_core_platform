from fastapi import HTTPException, Header, Depends


def check_role(role: str = Header(...)):
    if role not in ["Designer", "Viewer"]:
        raise HTTPException(status_code=400, detail="Неверная роль")
    return role


def require_designer(role: str = Depends(check_role)):
    if role != "Designer":
        raise HTTPException(
            status_code=403, detail="Доступ запрещен: только для Designer")
    return role
