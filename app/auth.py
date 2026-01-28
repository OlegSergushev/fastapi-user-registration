from passlib.context import CryptContext

# Настройка хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Хэширование пароля
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля
    """
    return pwd_context.verify(plain_password, hashed_password)