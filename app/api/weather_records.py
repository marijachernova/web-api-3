from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
from app.db.sessions import get_session
from app.models.weather_records import WeatherRecord, WeatherCreate, WeatherUpdate
from app.services.weather_saver import weather_saver
from sqlalchemy import select
from app.ws.manager import manager
from app.nats.client import publish_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/items", response_model=List[WeatherRecord])
async def list_items(session: AsyncSession = Depends(get_session)) -> List[WeatherRecord]:
    stmt = select(WeatherRecord).order_by(WeatherRecord.id)
    res = await session.execute(stmt)
    return res.scalars().all()

@router.get("/items/{item_id}", response_model=WeatherRecord)
async def get_item(item_id: int, session: AsyncSession = Depends(get_session)) -> WeatherRecord:
    item = await session.get(WeatherRecord, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/delete/{item_id}")
async def delete_item(item_id: int, session: AsyncSession = Depends(get_session)):
    item = await session.get(WeatherRecord, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.delete(item)
    await session.commit()

    payload = {
        "event": "deleted",
        "item_id": item_id
    }

    if not await publish_event(payload):
        await manager.broadcast(payload)

    return {"status": "deleted"}

@router.post("/items", response_model=WeatherRecord, status_code=201)
async def create_item(data: WeatherCreate, session: AsyncSession = Depends(get_session)) -> WeatherRecord:
    item = WeatherRecord(**data.model_dump())
    session.add(item)
    await session.commit()
    await session.refresh(item)

    payload = {
        "event": "created",
        "item": WeatherRecord.model_validate(item).model_dump(mode="json"),
    }

    if not await publish_event(payload):
        await manager.broadcast(payload)

    return item

@router.patch("/items/{item_id}", response_model=WeatherRecord)
async def update_item(item_id: int, data: WeatherUpdate, session: AsyncSession = Depends(get_session)) -> WeatherRecord:
    item = await session.get(WeatherRecord, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    upd = data.model_dump(exclude_unset=True)
    for k, v in upd.items():
        setattr(item, k, v)

    await session.commit()
    await session.refresh(item)

    payload = {
        "event": "updated",
        "item": WeatherRecord.model_validate(item).model_dump(mode="json")
    }
    
    if not await publish_event(payload):
        await manager.broadcast(payload)

    return item  