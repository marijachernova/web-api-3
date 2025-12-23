import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class OpenMeteoService:
    """Сервис для работы с Open-Meteo API"""

    # Координаты городов
    CITY_COORDINATES = {
        "Moscow": {"lat": 55.7558, "lon": 37.6176},
        "London": {"lat": 51.5074, "lon": -0.1278},
        "New York": {"lat": 40.7128, "lon": -74.0060},
        "Tokyo": {"lat": 35.6762, "lon": 139.6503},
        "Paris": {"lat": 48.8566, "lon": 2.3522},
        "Berlin": {"lat": 52.5200, "lon": 13.4050},
    }
    
    async def get_current_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """Получить текущую погоду для города"""
        if city not in self.CITY_COORDINATES:
            logger.error(f"Город {city} не найден в списке")
            return None
        
        coords = self.CITY_COORDINATES[city]
        
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "pressure_msl",
                "wind_speed_10m"
            ],
            "timezone": "auto",
            "forecast_days": 1
        }
        
        try:
            logger.info(f"Запрашиваем погоду для {city}...")
            
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.get(
                    settings.OPENMETEO_URL, 
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                current = data.get("current", {})
                
                # Парсим время
                time_str = current.get("time", "")
                if time_str:
                    recorded_at = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                else:
                    recorded_at = datetime.utcnow()
                
                # Формируем результат
                result = {
                    "city": city,
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "temperature": current.get("temperature_2m", 0.0),
                    "humidity": current.get("relative_humidity_2m"),
                    "pressure": current.get("pressure_msl"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "recorded_at": recorded_at,
                }
                
                logger.info(f"Данные для {city} получены: {result['temperature']}°C")
                return result
                
        except httpx.RequestError as e:
            logger.error(f"Сетевая ошибка для {city}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка для {city}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Неизвестная ошибка для {city}: {e}")
            return None
    
    async def get_all_cities_weather(self) -> Dict[str, Optional[Dict[str, Any]]]:
        """Получить погоду для всех городов"""
        results = {}
        
        for city in self.CITY_COORDINATES.keys():
            weather_data = await self.get_current_weather(city)
            results[city] = weather_data
            # Небольшая пауза между запросами
            import asyncio
            await asyncio.sleep(0.5)
        
        return results

openmeteo_service = OpenMeteoService()