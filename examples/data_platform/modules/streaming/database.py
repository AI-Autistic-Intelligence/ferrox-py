from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class CryptoTrade(Base):
    __tablename__ = 'crypto_trades'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_time = Column(BigInteger, index=True)
    symbol = Column(String(20), index=True)
    trade_id = Column(BigInteger, unique=True)
    price = Column(Float)
    quantity = Column(Float)
    is_buyer_maker = Column(Boolean)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    source_system = Column(String(50))
    processor_version = Column(String(20))

class CryptoDepth(Base):
    __tablename__ = 'crypto_depth'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True)
    last_update_id = Column(BigInteger)
    bids = Column(JSON)
    asks = Column(JSON)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    source_system = Column(String(50))
    processor_version = Column(String(20))

# For Data Platform, we'll use an async postgres connection, but fallback to sqlite if needed
DATABASE_URL = "sqlite+aiosqlite:///ferrox_data_platform.db"
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
