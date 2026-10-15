from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatasetModel(Base):
    __tablename__ = "data_catalog_datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    source = Column(String(128), nullable=False, default="internal")
    schema_definition = Column(Text, nullable=False, default="{}")
    row_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        try:
            schema = json.loads(self.schema_definition)
        except Exception:
            schema = {}
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "schema_definition": schema,
            "row_count": self.row_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class IngestionModel(Base):
    __tablename__ = "data_ingestion_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(128), nullable=False, index=True)
    source = Column(String(128), nullable=False)
    payload = Column(Text, nullable=False, default="{}")
    status = Column(String(32), nullable=False, default="success")
    ingested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        try:
            data = json.loads(self.payload)
        except Exception:
            data = {}
        return {
            "id": self.id,
            "pipeline_name": self.pipeline_name,
            "source": self.source,
            "payload": data,
            "status": self.status,
            "ingested_at": self.ingested_at.isoformat() if self.ingested_at else None,
        }


class PipelineRunModel(Base):
    __tablename__ = "data_pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dag_name = Column(String(128), nullable=False, index=True)
    status = Column(String(32), nullable=False, default="completed")
    duration_ms = Column(Float, nullable=False, default=0.0)
    results = Column(Text, nullable=False, default="{}")
    executed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        try:
            res = json.loads(self.results)
        except Exception:
            res = {}
        return {
            "id": self.id,
            "dag_name": self.dag_name,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "results": res,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
