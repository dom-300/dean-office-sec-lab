from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.auth.jwt_handler import verify_token
from app.database import get_db
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """АВТЕНТИФІКАЦІЯ (401): Перевіряє JWT access token і повертає активного користувача з БД."""
    if credentials is None:
        raise _unauthorized("Потрібна автентифікація")

    try:
        payload = verify_token(credentials.credentials)
    except InvalidTokenError:
        raise _unauthorized("Невалідний або протермінований токен")

    if payload.get("type") != "access":
        raise _unauthorized("Потрібен access token")

    user_id = payload.get("sub")
    if not user_id or not user_id.isdigit():
        raise _unauthorized("Некоректний ідентифікатор суб'єкта в токені")

    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        raise _unauthorized("Користувача не знайдено або деактивовано")

    return user


def require_role(*allowed_roles: str):
    """АВТОРИЗАЦІЯ за роллю (403): Перевіряє актуальні ролі користувача з бази даних."""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {r.name for r in current_user.roles}
        if not user_roles.intersection(allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Доступ заборонено. Потрібна роль: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


def require_permission(*required_perms: str):
    """АВТОРИЗАЦІЯ за дозволом (403): Перевіряє конкретні права (permissions) з матриці RBAC."""
    def perm_checker(current_user: User = Depends(get_current_user)) -> User:
        user_perms = {
            perm.name
            for role in current_user.roles
            for perm in role.permissions
        }
        if not set(required_perms).issubset(user_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостатньо прав. Потрібні дозволи: {', '.join(required_perms)}",
            )
        return current_user

    return perm_checker
