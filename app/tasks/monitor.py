import asyncio
import logging
from typing import Optional
import signal
from app.services.weather_saver import weather_saver
from app.config import settings

logger = logging.getLogger(__name__)

class BackgroundCollector:
    """Фоновый сборщик данных"""
    
    def __init__(self):
        self.task: Optional[asyncio.Task] = None
        self.is_running = False
        self.interval = settings.COLLECTION_INTERVAL
        
    async def start(self):
        """Запустить фоновый сбор"""
        if self.is_running:
            logger.warning("Фоновый сбор уже запущен")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._collection_loop())
        logger.info(f"Фоновый сбор данных запущен (интервал: {self.interval} секунд)")
        
        # Обработка сигналов для graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        asyncio.create_task(self._run_once_immediately())

    async def _run_once_immediately(self):
        try:
            logger.info("Немедленный сбор данных при старте...")
            records = await weather_saver.save_all_cities_weather()
            if records:
                logger.info(f"Первоначальный сбор завершен. Сохранено: {len(records)} записей")
        except Exception as e:
            logger.error(f"Ошибка при первоначальном сборе: {e}")
    
    async def stop(self):
        """Остановить фоновый сбор"""
        if not self.is_running:
            return
        
        logger.info("Остановка фонового сбора данных...")
        self.is_running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Ошибка при остановке задачи: {e}")
        
        logger.info("Фоновый сбор данных остановлен")
    
    async def _collection_loop(self):
        """Основной цикл сбора данных"""
        logger.info(f"Начинаем фоновый сбор данных. Интервал: {self.interval} секунд")
        
        while self.is_running:
            try:
                logger.info("Выполняем очередной сбор данных...")
                records = await weather_saver.save_all_cities_weather()
                
                if records:
                    logger.info(f"Сбор данных завершен. Сохранено записей: {len(records)}")
                else:
                    logger.warning("Не удалось сохранить данные")
                
            except asyncio.CancelledError:
                logger.info("Задача сбора данных отменена")
                break
            except Exception as e:
                logger.error(f"Ошибка в фоновом сборе: {e}")
            
            # Ждем перед следующим сбором
            try:
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break

background_collector = BackgroundCollector()