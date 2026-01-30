# Backend-приложение с системой аутентификации и авторизации.

## Структура проекта:

├── app/
│   ├── __init__.py
│   ├── main.py              # Основное приложение FastAPI
│   ├── models.py            # SQLAlchemy модель User
│   ├── schemas.py           # Pydantic схемы для валидации
│   ├── database.py          # Подключение к SQLite
│   └── auth.py              # JWT аутентификация
├── run.py                   # Скрипт запуска
├── requirements.txt         # Зависимости Python
├── .env                     # Переменные окружения
└── users.db                 # База данных SQLite
