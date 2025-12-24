# Асинхронное FastAPI приложение для получения данных о погоде с open-meteo с real-time уведомлениями через WebSocket и интеграцией с NATS.

Функциональность:
- REST API: полный CRUD для управления записями о погоде (items)
- WebSocket: real-time уведомления о изменениях (/ws/items)
- Фоновая задача: автоматическое получение погоды с API open-meteo каждые 30 секунд
- NATS интеграцияL публикация событий и подписка на внешние команды
- Асинхронная БД: SQLite с SQLModel
- Документация: автоматическая Swagger документация

---
## REST API
Weather API
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/weather/items` | Получить список записей |
| GET | `/weather/items/{id}` | Получить конкретную запись |
| POST | `/weather/items` | Создать новую запись |
| PATCH | `/weather/items/{id}` | Обновить запись |
| DELETE | `weather/items/{id}` | Удалить запись ||

Tasks API
| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/tasks/background/start` | Запустить фоновую задачу |
| POST | `/tasks/background/stop` | Остановить фоновую задачу ||

---

## Запуск

1. Установка зависимостей
git clone <repository-url> # Клонирование репозитория
cd "WebAPI3"
.\venv\Scripts\activate.ps1  # Создание виртуального окружения (опционально) Windows
pip install -r requirements.txt # Установка зависимостей

2. Запуск NATS сервера 
.\nats-server.exe -p 4222 -m 8222 # Запуск NATS
nats sub -s nats://127.0.0.1:4222 items.updates # Подписка на канал
.\nats pub -s nats://127.0.0.1:4222 items.updates "Hello from NATS" # Отправка тестового сообщения
curl http://localhost:8222/  # Мониторинг NATS

3. Запуск приложения
python -m uvicorn app.main

4.  WebSocket через клиент на URL
ws://localhost:8000/ws/items 

---

## Основные URL

1. Документация API: http://localhost:8000/docs
2. Мониторинг NATS: http://localhost:8222
