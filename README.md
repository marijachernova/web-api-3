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
   
1.1 git clone <repository-url> # Клонирование репозитория

1.2 cd "WebAPI3"

1.3 \venv\Scripts\activate.ps1  # Создание виртуального окружения (опционально) Windows
1.4 pip install -r requirements.txt # Установка зависимостей

3. Запуск NATS сервера 
2.1 .\nats-server.exe -p 4222 -m 8222 # Запуск NATS
2.2 nats sub -s nats://127.0.0.1:4222 items.updates # Подписка на канал
2.3 .\nats pub -s nats://127.0.0.1:4222 items.updates "Hello from NATS" # Отправка тестового сообщения
2.4 curl http://localhost:8222/  # Мониторинг NATS

4. python -m uvicorn app.main # Запуск приложения

5.  ws://localhost:8000/ws/items # WebSocket через клиент на URL 

---

## Основные URL

1. Документация API: http://localhost:8000/docs
2. Мониторинг NATS: http://localhost:8222
