from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
from . import models, schemas
from .database import engine, get_db
from .auth import (
    authenticate_user, create_access_token,
    get_current_active_user, get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
)
from datetime import timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

# Добавляем схему безопасности
security = HTTPBearer()

app = FastAPI(
    title="User Registration API",
    description="API для регистрации и управления пользователями",
    version="1.0.0",
    # Добавляем настройки безопасности для Swagger
    swagger_ui_parameters={
        "syntaxHighlight.theme": "obsidian",
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
    },
    # Добавляем схемы безопасности
    security=[{"Bearer": []}],
    # Определяем схемы безопасности
    openapi_extra={
        "components": {
            "securitySchemes": {
                "Bearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Введите JWT токен полученный через /login/"
                }
            }
        }
    }
)


@app.post("/register/",
          response_model=schemas.UserResponse,
          status_code=status.HTTP_201_CREATED,
          tags=["Аутентификация"]
          )
def register_user(
        user_data: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    # Проверяем, существует ли уже пользователь с таким email
    existing_user = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )

    # Проверяем совпадение паролей
    if user_data.password != user_data.password_repeat:
        raise HTTPException(
            status_code=400,
            detail="Пароли не совпадают"
        )

    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)

    db_user = models.User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        middle_name=user_data.middle_name,
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.get("/users/", response_model=list[schemas.UserResponse], tags=["Пользователи"])
def get_users(
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
        db: Session = Depends(get_db)
):
    """
    Получить список пользователей.

    По умолчанию возвращаются только активные пользователи.
    Используйте параметр include_inactive=True для получения всех.
    """
    query = db.query(models.User)

    if not include_inactive:
        query = query.filter(models.User.is_active == True)

    users = query.order_by(models.User.id).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["Пользователи"])
def get_user(
        user_id: int,
        include_inactive: bool = False,
        db: Session = Depends(get_db)
):
    """
    Получить пользователя по ID.

    По умолчанию возвращаются только активные пользователи.
    """
    query = db.query(models.User).filter(models.User.id == user_id)

    if not include_inactive:
        query = query.filter(models.User.is_active == True)

    user = query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    return user


@app.get("/", include_in_schema=False)  # exclude_from_schema=True чтобы не показывать в документации
async def root():
    return {
        "name": "User Registration API",
        "version": "1.0.0",
        "description": "API для регистрации и управления пользователями",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "status": "operational"
    }


@app.post("/login/", status_code=status.HTTP_200_OK, tags=["Аутентификация"])
async def login(
        login_data: schemas.UserLogin,
        db: Session = Depends(get_db)
):
    """
    Вход в систему по email и паролю.

    Возвращает JWT токен для доступа к защищенным эндпоинтам.
    """
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    }


@app.get("/profile/", response_model=schemas.UserResponse, dependencies=[Depends(security)], tags=["Профиль"])
async def get_profile(
        current_user: models.User = Depends(get_current_active_user)
):
    """
    Получить профиль текущего пользователя
    """
    return current_user


@app.patch("/profile/", response_model=schemas.UserResponse, dependencies=[Depends(security)], tags=["Профиль"])
async def update_profile(
        user_update: schemas.UserUpdate,
        current_user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Частичное обновление профиля пользователя
    """
    update_data = user_update.dict(exclude_unset=True)

    # Если меняется email, проверяем что он уникальный
    if 'email' in update_data and update_data['email'] != current_user.email:
        existing_user = (db.query(models.User)
                         .filter(models.User.email == update_data['email'].lower())
                         .first())
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        update_data['email'] = update_data['email'].lower()

    # Обновляем поля пользователя
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user


@app.put("/profile/", response_model=schemas.UserResponse, dependencies=[Depends(security)], tags=["Профиль"])
async def update_profile_full(
        user_update: schemas.UserUpdateFull,
        current_user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Полное обновление профиля пользователя (все поля обязательны)
    """
    # Проверяем email на уникальность если он меняется
    if user_update.email != current_user.email:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email.lower()
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

    # Обновляем все поля
    current_user.first_name = user_update.first_name
    current_user.last_name = user_update.last_name
    current_user.middle_name = user_update.middle_name
    current_user.email = user_update.email.lower()

    db.commit()
    db.refresh(current_user)

    return current_user


@app.patch("/profile/password/", dependencies=[Depends(security)], tags=["Профиль"])
def change_password(
        password_data: schemas.PasswordChange,
        current_user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Изменение пароля пользователя
    """
    # Проверяем старый пароль
    from .auth import verify_password

    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )

    # Проверяем что новый пароль отличается от старого
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый пароль должен отличаться от старого"
        )

    # Проверяем совпадение паролей
    if password_data.new_password != password_data.new_password_repeat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новые пароли не совпадают"
        )

    # Обновляем пароль
    from .auth import get_password_hash
    current_user.hashed_password = get_password_hash(password_data.new_password)

    db.commit()

    return {"message": "Пароль успешно изменен"}


@app.delete("/profile/",
            response_model=schemas.UserDeleteResponse,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(security)],
            tags=["Профиль"]
            )
def delete_profile(
        delete_data: schemas.UserDeleteRequest,
        current_user: models.User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Мягкое удаление профиля с подтверждением пароля.

    Требуется подтверждение текущим паролем для безопасности.
    """
    from .auth import verify_password

    # Подтверждаем пароль
    if not verify_password(delete_data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль. Удаление отменено."
        )

    # Помечаем пользователя как неактивного
    current_user.is_active = False
    current_user.deleted_at = func.now()  # Устанавливаем время удаления

    # Сохраняем причину, если указана
    if delete_data.reason:
        current_user.deletion_reason = delete_data.reason

    db.commit()

    return {
        "message": "Профиль успешно деактивирован",
        "detail": "Ваш аккаунт был отключен. Данные сохранены в системе.",
        "user_id": current_user.id,
        "email": current_user.email,
        "can_be_restored": True,
        "restore_period_days": 30,
        "deleted_at": current_user.deleted_at
    }


# endpoint для восстановления профиля
@app.post("/profile/restore/", status_code=status.HTTP_200_OK, tags=["Профиль"])
def restore_profile(
        email: str,
        password: str,
        db: Session = Depends(get_db)
):
    """
    Восстановление деактивированного профиля.

    Пользователь может восстановить профиль в течение определенного периода.
    """

    user = db.query(models.User).filter(
        models.User.email == email.lower(),
        models.User.is_active == False
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Деактивированный профиль с таким email не найден"
        )

    # Проверяем пароль
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )

    # Восстанавливаем профиль
    user.is_active = True
    db.commit()

    # Создаем новый токен
    from .auth import create_access_token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "message": "Профиль успешно восстановлен",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    }


@app.get("/profile/status/", dependencies=[Depends(security)], tags=["Профиль"])
def get_profile_status(
        current_user: models.User = Depends(get_current_active_user)
):
    """
    Получить статус профиля пользователя.

    Показывает:
    - Активен ли профиль
    - Когда был создан
    - Когда последний раз обновлялся
    - Статус удаления (если применимо)
    """
    status_info = {
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "email_verified": True,  # Можно добавить подтверждение email позже
    }

    if current_user.deleted_at:
        status_info.update({
            "deleted_at": current_user.deleted_at,
            "deletion_reason": current_user.deletion_reason,
            "can_be_restored": True,
            "days_since_deletion": (
                    datetime.utcnow() - current_user.deleted_at
            ).days if current_user.deleted_at else None
        })

    return status_info


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = Path("favicon.ico")
    if favicon_path.exists():
        return FileResponse(favicon_path)
    # Если файла нет, возвращаем пустой ответ с 204
    from fastapi import Response
    return Response(status_code=204)

