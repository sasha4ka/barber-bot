## Barber-bot
Бот для администрации салона красоты, позволяющий пользователям записываться к нужному мастеру с выбором времени, мастерам отслеживать записи через интерактивный календарь.

## 1. Функционал
- Веб-панель (WIP) - интерактивный календарь для мастеров; админ-панель для администратора
- Регистрация и JWT-аунтефикация для защиты панели и api
- Меню управлениями записями (создание, просмотр, удаление, перенос) для пользователя через бота
- Отправка уведомлений пользователям для напоминания об активных записях, предупреждений о переносе записи

## 2. Архитектура
```mermaid
flowchart TD
  Candy["1. Candy<br/>reverse proxy"]

  subgraph Services["Application Services"]
    direction LR
    Notification["2. Notification<br/>notification service"]
    API["3. API<br/>RESTFul API"]
    Bot["4. Bot<br/>telegram bot"]
  end

  RabbitMQ["5. RabbitMQ"]
  PostgresDB[("6. Postgres DB")]
  Redis[("7. Redis")]

  Candy --> Services
  Services <-.-> RabbitMQ
  
  Services --> PostgresDB
  Bot --> Redis

  classDef subgraphClass stroke-opacity:0.5
  class Services subgraphClass
```

## 3. Структура проекта
```
├── README.md
├── apps                     # Сервисы
│   ├── api                  # RESTFul API (fastapi)
│   ├── bot                  # Telegram bot (aiogram 3.x)
│   └── notification_service # Сервис уведомлений
├── libs                     # Общие библиотеки
│   └── core_shared          # Работа с db (sqlalchemy 2.x)
├── docker-compose.prod.yaml # Docker compose для продакшен-деплоя
├── docker-compose.yaml      # Docker compose для dev
└── pyproject.toml           # Настройки проекта
```

## 4. Технологический стек
1. *Языки/Фреймворки:* Python 3.14, FastAPI, pydantic, SQLAlchemy 2.x + alembic, aiogram 3.x
1. *Пакетный менеджер, линтеры:* uv, ruff
1. *Базы данных:* PostgresSQL, Redis (aiogram FSM)
1. *Инфраструктура:* Docker, Docker Compose, Github Actions (CI/CD)
1. *Брокер сообщений:* RabbitMQ

## 5. Быстрый запуск
Используйте эти команды для быстрого deployment-а приложения на ваш сервер.
```
1. git clone https://github.com/sasha4ka/book-bot && cd book-bot
2. vim .env # Создайте и заполните файл .env в соответствии с .env.example
3. docker-compose -f "docker-compose.prod.yaml" up -d
```
