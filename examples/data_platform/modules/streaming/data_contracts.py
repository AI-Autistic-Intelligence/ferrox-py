from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

class DataLineage(BaseModel):
    """
    Solves Point 3 (Lineage & Governance):
    Every event MUST carry its origin, ingestion timestamp, and processor version.
    """
    source_system: str
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    processor_version: str = "v1.0.0"


class BinanceTradeContract(BaseModel):
    """
    Solves Point 1 (Data Contracts):
    Strictly validates incoming JSON from the WebSocket. If Binance changes their schema,
    this will loudly fail rather than silently corrupting the Data Lake.
    """
    event_type: str = Field(alias="e")
    event_time: int = Field(alias="E")
    symbol: str = Field(alias="s")
    trade_id: int = Field(alias="t")
    price: float = Field(alias="p")
    quantity: float = Field(alias="q")
    is_buyer_maker: bool = Field(alias="m")
    
    # Lineage is injected by the ingestion engine
    lineage: Optional[DataLineage] = None

    @field_validator("price", "quantity", mode="before")
    def parse_floats(cls, v):
        # Binance sends numbers as strings to avoid precision loss. We cast them to float.
        return float(v)
