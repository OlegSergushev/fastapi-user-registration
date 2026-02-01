# FastAPI User Registration API

## 1. Что это за проект?

Это полноценное REST API для регистрации и аутентификации пользователей, построенное на **FastAPI**. Проект включает все необходимые функции для работы с пользователями: 
 - регистрацию
 - вход
 - управление профилем
 - безопасную аутентификацию с использованием JWT токенов

## 2. Зачем он нужен и какую проблему решает?

### Решаемые проблемы:
- **Быстрый старт** - готовый шаблон для добавления системы пользователей в любой проект
- **Безопасность** - встроенные механизмы безопасности (хэширование паролей, JWT токены)
- **Стандартизация** - RESTful API, соответствующий лучшим практикам
- **Документация** - автоматическая генерация Swagger документации

### Где можно использовать:
- Как основа для стартапа или нового проекта
- Как учебный пример работы с FastAPI и JWT
- Как микросервис аутентификации в микросервисной архитектуре
- Как шаблон для быстрого добавления регистрации пользователей

## 3. Как установить и запустить?

### Предварительные требования:
- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Установка:

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/ваш_username/fastapi-user-registration.git
cd fastapi-user-registration

# 2. Создайте виртуальное окружение
python -m venv .venv

# 3. Активируйте виртуальное окружение
# Для Windows:
.venv\Scripts\activate
# Для Linux/Mac:
source .venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Настройте окружение
# Скопируйте пример файла окружения
cp .env.example .env
# Отредактируйте .env файл, установите SECRET_KEY

# 6. Запустите сервер
python run.py
```
## 4. Как использовать?

После запуска сервера доступна автоматическая документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Основные эндпоинты:

- Регистрация и вход:
```bash
POST /register/ - Регистрация нового пользователя
POST /login/    - Вход в систему (получение JWT токена)
```
- Управление профилем (требуют токен):
```bash
GET    /profile/           - Получить свой профиль
PATCH  /profile/           - Частичное обновление профиля
PUT    /profile/           - Полное обновление профиля
PATCH  /profile/password/  - Смена пароля
DELETE /profile/           - Мягкое удаление профиля
GET    /profile/status/    - Статус профиля
```
- Пользователи:
```bash
GET /users/          - Список пользователей
GET /users/{id}      - Пользователь по ID
```

## Структура проекта:

```bash
fastapi-user-registration/
├── app/                    # Основное приложение
│   ├── __init__.py
│   ├── main.py            # Эндпоинты FastAPI
│   ├── models.py          # Модель User (SQLAlchemy)
│   ├── schemas.py         # Схемы Pydantic для валидации
│   ├── database.py        # Подключение к БД
│   └── auth.py            # JWT аутентификация
├── run.py                 # Скрипт запуска
├── requirements.txt       # Зависимости Python
├── .env.example          # Пример переменных окружения
└── README.md             # Этот файл
```

## База данных:

> Проект использует SQLite для простоты развертывания. 
Структура таблицы users:
```bash
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    deleted_at TIMESTAMP,
    deletion_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Особенности реализации:

- JWT аутентификация - безопасные токены с временем жизни
- Валидация данных - строгая проверка всех входных данных
- Мягкое удаление - данные сохраняются при "удалении" аккаунта
- Хэширование паролей - использование bcrypt для безопасности
- RESTful API - соответствие REST принципам
- Автодокументация - Swagger/OpenAPI спецификация
