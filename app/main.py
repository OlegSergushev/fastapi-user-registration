from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
from .auth import get_password_hash, verify_password

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Registration API",
    description="API для регистрации пользователей",
    version="1.0.0"
)


@app.post("/register/", response_model=schemas.UserResponse)
async def register_user(
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


@app.get("/users/", response_model=list[schemas.UserResponse])
async def get_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """
    Получение списка пользователей
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/")
async def root():
    return {
        "message": "User Registration API",
        "docs": "/docs",
        "redoc": "/redoc"
    }