from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100, description="Имя")
    last_name: str = Field(..., min_length=2, max_length=100, description="Фамилия")
    middle_name: Optional[str] = Field(None, max_length=100, description="Отчество")
    email: EmailStr = Field(..., description="Email")


class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль (минимум 8 символов)"
    )
    password_repeat: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Повтор пароля"
    )

    @validator('password')
    def password_strength(cls, v):
        # Проверка сложности пароля (опционально)
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        # Можно добавить дополнительные проверки:
        # if not any(c.isdigit() for c in v):
        #     raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Для обновления профиля (частичное обновление)
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None)

    @validator('email')
    def validate_email(cls, v):
        if v is None:
            return v
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Некорректный email')
        return v.lower()

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if v is None:
            return v
        # Проверяем что имя содержит только буквы и дефисы
        if not re.match(r'^[A-Za-zА-Яа-яЁё\- ]+$', v):
            raise ValueError('Имя может содержать только буквы, пробелы и дефисы')
        return v


# Для полного обновления профиля
class UserUpdateFull(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: str = Field(...)

    @validator('email')
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Некорректный email')
        return v.lower()

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not re.match(r'^[A-Za-zА-Яа-яЁё\- ]+$', v):
            raise ValueError('Имя может содержать только буквы, пробелы и дефисы')
        return v


# Для смены пароля
class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)
    new_password_repeat: str = Field(..., min_length=8, max_length=100)

    @validator('new_password')
    def password_strength(cls, v):
        errors = []
        if len(v) < 8:
            errors.append("минимум 8 символов")
        if not any(c.isupper() for c in v):
            errors.append("хотя бы одна заглавная буква")
        if not any(c.islower() for c in v):
            errors.append("хотя бы одна строчная буква")
        if not any(c.isdigit() for c in v):
            errors.append("хотя бы одна цифра")

        if errors:
            raise ValueError(f"Пароль должен содержать: {', '.join(errors)}")
        return v

    @validator('new_password_repeat')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Новые пароли не совпадают')
        return v


# Токен для логина
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    first_name: str
    last_name: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Схема для ответа после удаления
class UserDeleteResponse(BaseModel):
    message: str
    detail: str
    user_id: int
    email: str
    can_be_restored: bool
    restore_period_days: int = 30
    deleted_at: Optional[datetime] = None


# Схема для запроса на удаление (если нужны дополнительные данные)
class UserDeleteRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Причина удаления аккаунта (опционально)"
    )
    password: str = Field(
        ...,
        description="Текущий пароль для подтверждения удаления"
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., examples=["MyPassword123"])