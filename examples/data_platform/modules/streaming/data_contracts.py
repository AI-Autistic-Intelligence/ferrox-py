from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DataLineage(BaseModel):
    """
    Solves Point 3 (Lineage & Governance):
    Every event MUST carry its origin, ingestion timestamp, and processor version.
    """
    source_system: str
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    processor_version: str = "v1.1.0"


class BinanceTradeContract(BaseModel):
    """
    Validates real-time Trade executions.
    """
    event_type: str = Field(alias="e")
    event_time: int = Field(alias="E")
    symbol: str = Field(alias="s")
    trade_id: int = Field(alias="t")
    price: float = Field(alias="p")
    quantity: float = Field(alias="q")
    is_buyer_maker: bool = Field(alias="m")
    
    lineage: DataLineage | None = None

    @field_validator("price", "quantity", mode="before")
    def parse_floats(cls, v):
        return float(v)

class BinanceDepthContract(BaseModel):
    """
    Validates Order Book Depth (Top 5 Bids/Asks) for detecting Spoofing and Imbalances.
    """
    last_update_id: int = Field(alias="lastUpdateId")
    bids: list[list[float]]
    asks: list[list[float]]
    symbol: str = "UNKNOWN" # Injected by the multiplexer
    
    lineage: DataLineage | None = None
