from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


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