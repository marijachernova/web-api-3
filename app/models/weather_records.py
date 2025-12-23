from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class WeatherBase(SQLModel):
    """Базовая схема с общими полями"""
    city: str = Field(max_length=100)
    latitude: float = Field(description="Широта")
    longitude: float = Field(description="Долгота")
    temperature: float = Field(description="Температура в °C")
    humidity: Optional[float] = Field(default=None, ge=0, le=100, description="Влажность в %")
    pressure: Optional[float] = Field(default=None, description="Давление в гПа")
    wind_speed: Optional[float] = Field(default=None, description="Скорость ветра в км/ч")
    recorded_at: datetime = Field(description="Время измерения данных с API")

class WeatherRecord(WeatherBase, table=True):
    """Модель для записей погоды"""
    __tablename__ = "weather_records"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True, description="Время создания записи")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Время последнего обновления")

class WeatherCreate(WeatherBase):
    """Схема для создания новой записи (API input)"""
    pass
   
class WeatherUpdate(SQLModel):
    """Схема для обновления записи"""
    city: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None