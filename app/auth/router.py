from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, User
from app.schemas import LoginRequest, LoginResponse, UserCreate, UserResponse
from app.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Фіктивний хеш для вирівнювання часу відповіді при неіснуючому користувачі (захист від Timing Enumeration)
DUMMY_HASH = hash_password("DummyPasswordForTimingProtection123!")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    normalized_email = user_data.email.lower()

    # Перевірка унікальності username та email (без урахування регістру)
    if db.query(User).filter(func.lower(User.username) == user_data.username.lower()).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username вже зайнятий")

    if db.query(User).filter(func.lower(User.email) == normalized_email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email вже зареєстровано")

    new_user = User(
        username=user_data.username,
        email=normalized_email,
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
    )

    # Принцип мінімальних привілеїв (PoLP): кожен новий користувач отримує лише базову роль student
    student_role = db.query(Role).filter(Role.name == "student").first()
    if student_role:
        new_user.roles.append(student_role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    # Виконуємо криптографічну перевірку завжди, навіть якщо користувача не знайдено
    target_hash = user.password_hash if user else DUMMY_HASH
    is_valid = verify_password(credentials.password, target_hash)

    if not user or not is_valid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Невірний логін або пароль")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Акаунт деактивовано")

    return LoginResponse(
        message="Вхід успішний",
        user_id=user.id,
        username=user.username,
        roles=[r.name for r in user.roles],
    )
