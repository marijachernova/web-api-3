from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.config import settings
from sqlmodel import SQLModel

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,           
    class_=AsyncSession,   
    autocommit=False,       
    autoflush=False,        
    expire_on_commit=False  
)

async def init_db():
    """Инициализировать БД (создать таблицы)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("База данных инициализирована")
    
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()