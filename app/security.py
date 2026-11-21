from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# Параметри за замовчуванням відповідають рекомендаціям OWASP (Argon2id, 64 MiB RAM, 3 ітерації)
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Генерує хеш Argon2id з автоматичною унікальною сіллю ($argon2id$v=19$...)."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Безпечна перевірка пароля (стійка до атак за часом — constant-time comparison)."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
