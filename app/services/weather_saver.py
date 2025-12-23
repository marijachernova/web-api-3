import logging
from typing import Optional, List, Dict, Any
from app.models.weather_records import WeatherRecord, WeatherCreate
from app.services.openmeteo_service import openmeteo_service
from app.db.sessions import AsyncSessionLocal
from app.ws.manager import manager
from app.nats.client import publish_event

logger = logging.getLogger(__name__)

class WeatherSaver:
    """Сервис для сохранения погодных данных в БД"""
    
    async def save_weather_data(self, weather_data: Dict[str, Any]) -> Optional[WeatherRecord]:
        """Сохранить данные о погоде в БД"""
        if not weather_data:
            return None
        
        try:
            # Создаем объект WeatherCreate
            weather_create = WeatherCreate(
                city=weather_data["city"],
                latitude=weather_data["latitude"],
                longitude=weather_data["longitude"],
                temperature=weather_data["temperature"],
                humidity=weather_data.get("humidity"),
                pressure=weather_data.get("pressure"),
                wind_speed=weather_data.get("wind_speed"),
                recorded_at=weather_data["recorded_at"]
            )
            
            # Создаем запись в БД
            weather_record = WeatherRecord(**weather_create.dict())
            
            async with AsyncSessionLocal() as session:
                session.add(weather_record)
                await session.commit()
                await session.refresh(weather_record)
                
                logger.info(f"Данные для {weather_data['city']} сохранены в БД. ID: {weather_record.id}")

            payload = {
                    "event": "add",
                    "weather_record": {
                        "id": weather_record.id,
                        "city": weather_record.city,
                        "temperature": weather_record.temperature,
                        "humidity": weather_record.humidity,
                        "pressure": weather_record.pressure,
                        "wind_speed": weather_record.wind_speed,
                        "recorded_at": weather_record.recorded_at
                    }
                }
           
            if not await publish_event(payload):
                await manager.broadcast(payload)

            return weather_record
                
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных для {weather_data.get('city', 'unknown')}: {e}")
            return None
    
    async def save_all_cities_weather(self) -> List[WeatherRecord]:
        """Получить и сохранить данные для всех городов"""
        logger.info("Начинаем сбор данных для всех городов...")
        
        saved_records = []
        
        # Получаем данные для всех городов
        all_weather = await openmeteo_service.get_all_cities_weather()
        
        for city, weather_data in all_weather.items():
            if weather_data:
                record = await self.save_weather_data(weather_data)
                if record:
                    saved_records.append(record)
            else:
                logger.warning(f"Не удалось получить данные для {city}")
        
        logger.info(f"Сбор данных завершен. Сохранено записей: {len(saved_records)}")
        return saved_records 
   
weather_saver = WeatherSaver()