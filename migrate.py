from app.database import engine
from app.models import Base
import sqlite3


def migrate():
    # Создаем таблицы заново (осторожно: удалит существующие данные!)
    # Base.metadata.drop_all(bind=engine)  # Раскомментировать для пересоздания
    Base.metadata.create_all(bind=engine)

    # Альтернативный способ - ALTER TABLE через raw SQL
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    try:
        # Добавляем новые поля если их нет
        cursor.execute("ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP")
        print("Added deleted_at column")
    except sqlite3.OperationalError:
        print("Column deleted_at already exists")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN deletion_reason TEXT")
        print("Added deletion_reason column")
    except sqlite3.OperationalError:
        print("Column deletion_reason already exists")

    conn.commit()
    conn.close()
    print("Migration completed!")


if __name__ == "__main__":
    migrate()
