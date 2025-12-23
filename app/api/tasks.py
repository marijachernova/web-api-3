from fastapi import APIRouter, HTTPException
import logging
from app.tasks.monitor import background_collector
from datetime import datetime
from app.ws.manager import manager
from app.nats.client import publish_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/background/start")
async def start_background_task():
    """Запустить фоновую задачу"""
    try:
        await background_collector.start()

        payload = {
            "event": "background_task_started",
            "interval_seconds": background_collector.interval,
            "timestamp": datetime.now().isoformat()
        }

        if not await publish_event(payload):
            await manager.broadcast(payload)

        return {
            "status": "success",
            "message": "Фоновая задача запущена"
        }
    
    except Exception as e:
        logger.error(f"Ошибка при запуске фоновой задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/background/stop")
async def stop_background_task():
    """Остановить фоновую задачу"""
    try:
        await background_collector.stop()

        payload = {
            "event": "background_task_stopped",
            "timestamp": datetime.now().isoformat()
        }

        if not await publish_event(payload):
            await manager.broadcast(payload)

        return {
            "status": "success",
            "message": "Фоновая задача остановлена"
        }
    
    except Exception as e:
        logger.error(f"Ошибка при остановке фоновой задачи: {e}")
        raise HTTPException(status_code=500, detail=str(e))