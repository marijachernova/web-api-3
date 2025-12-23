import os
from typing import List

class Settings:
    APP_TITLE = "Weather Data Collector"
    APP_VERSION = "1.0.0"
    
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./weather.db")
    
    # Города для мониторинга
    MONITORED_CITIES: List[str] = [
        "Moscow",
        "London", 
        "New York",
        "Tokyo",
        "Paris",
        "Berlin"
    ]
    
    # Интервал сбора данных (в секундах)
    COLLECTION_INTERVAL = int(os.getenv("COLLECTION_INTERVAL", "30"))
    
    # Настройки API
    OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"
    REQUEST_TIMEOUT = 30.0

settings = Settings()