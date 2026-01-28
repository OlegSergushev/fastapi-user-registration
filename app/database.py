from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Для простоты используем SQLite, но можно заменить на PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./users.db"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Только для SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Зависимость для получения сессии базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()