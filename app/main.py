from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from app.db.sessions import init_db
from app.config import settings
from app.tasks.monitor import background_collector
from app.ws.router import router as ws_router
from app.api.weather_records import router as weather_router
from app.api.tasks import router as tasks_router
from app.nats.client import connect_nats
from fastapi.middleware.cors import CORSMiddleware

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # Стартуем
    logger.info("Запуск приложения...")
    
    # Инициализируем БД
    await init_db()
    logger.info("База данных готова")
    
    await connect_nats()

    try:
        # Запускаем фоновый сбор данных
        await background_collector.start()
        logger.info(f"Фоновый сбор данных запущен (интервал: {settings.COLLECTION_INTERVAL} сек)")
    except Exception as e:
        logger.error(f"Ошибка при запуске фонового сбора: {e}")
    
    yield
    
    # Останавливаем при завершении приложения
    logger.info("Остановка приложения...")
    try:
        await background_collector.stop()
        logger.info("Фоновый сбор данных остановлен")
    except Exception as e:
        logger.error(f"Ошибка при остановке фонового сбора: {e}") 
    
# Создаем приложение FastAPI
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router)
app.include_router(tasks_router)
app.include_router(ws_router)