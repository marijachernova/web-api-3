# Асинхронное FastAPI приложение для получения данных о погоде с open-meteo с real-time уведомлениями через WebSocket и интеграцией с NATS.

Функциональность:
REST API - полный CRUD для управления записями о погоде (items)
WebSocket - real-time уведомления о изменениях (/ws/items)
Фоновая задача - автоматическое получение погоды с API open-meteo каждые 30 секунд
NATS интеграция - публикация событий и подписка на внешние команды
Асинхронная БД - SQLite с SQLModel
Документация - автоматическая Swagger документация

---

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

### Запуск
1. Установка зависимостей
# Клонирование репозитория
git clone <repository-url>
cd "WebAPI3"

# Создание виртуального окружения (опционально)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
.\venv\Scripts\activate.ps1  # Windows

# Установка зависимостей
pip install -r requirements.txt
2. Запуск NATS сервера 
# Запуск NATS 
.\nats-server.exe -p 4222 -m 8222
# Подписка на канал
nats sub -s nats://127.0.0.1:4222 items.updates
# Отправка тестового сообщения
.\nats pub -s nats://127.0.0.1:4222 items.updates "Hello from NATS"
# Проверка работы NATS
curl http://localhost:8222/  # Мониторинг NATS
3. Запуск приложения
python -m uvicorn app.main

Основные URL

Документация API: http://localhost:8000/docs
Мониторинг NATS: http://localhost:8222
