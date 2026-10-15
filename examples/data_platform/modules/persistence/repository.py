import json
import os
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from .models import Base, DatasetModel, IngestionModel, PipelineRunModel


class DataPlatformRepository(ABC):
    @abstractmethod
    async def list_datasets(self, skip: int = 0, take: int = 10, sort: Optional[str] = None, filter_str: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_dataset(self, name: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def save_dataset(self, name: str, description: Optional[str], source: str, schema_definition: Dict[str, Any], row_count: int = 0) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def delete_dataset(self, name: str) -> bool:
        pass

    @abstractmethod
    async def record_ingestion(self, pipeline_name: str, source: str, payload: Dict[str, Any], status: str = "success") -> Dict[str, Any]:
        pass

    @abstractmethod
    async def list_ingestions(self, limit: int = 20) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def record_pipeline_run(self, dag_name: str, status: str, duration_ms: float, results: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def list_pipeline_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def ping(self) -> bool:
        pass


class InMemoryRepository(DataPlatformRepository):
    def __init__(self):
        self._datasets: Dict[str, Dict[str, Any]] = {}
        self._ingestions: List[Dict[str, Any]] = []
        self._pipeline_runs: List[Dict[str, Any]] = []
        self._next_id = 1
        self._seed_default_data()

    def _seed_default_data(self):
        now = datetime.now(timezone.utc).isoformat()
        seeds = [
            {
                "id": 1,
                "name": "dataset_weather",
                "description": "Global meteorological sensor feeds updated in real-time.",
                "source": "Open-Meteo REST API",
                "schema_definition": {"city": "string", "temperature": "float", "humidity": "integer"},
                "row_count": 14250,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 2,
                "name": "dataset_finance",
                "description": "High-frequency cryptocurrency order book snapshots and tick metrics.",
                "source": "Binance WebSocket Depth",
                "schema_definition": {"symbol": "string", "bidPrice": "float", "askPrice": "float", "volume": "float"},
                "row_count": 894200,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": 3,
                "name": "dataset_ecommerce",
                "description": "Aggregated shopping cart checkout events and order conversions.",
                "source": "Ferrox-PHP EShop SAGA Outbox",
                "schema_definition": {"order_id": "string", "customer_id": "string", "total_amount": "float", "status": "string"},
                "row_count": 52100,
                "created_at": now,
                "updated_at": now,
            },
        ]
        for item in seeds:
            self._datasets[item["name"]] = item
        self._next_id = 4

    async def list_datasets(self, skip: int = 0, take: int = 10, sort: Optional[str] = None, filter_str: Optional[str] = None) -> List[Dict[str, Any]]:
        results = list(self._datasets.values())
        if filter_str:
            q = filter_str.lower()
            results = [r for r in results if q in r["name"].lower() or (r["description"] and q in r["description"].lower())]
        if sort:
            desc = sort.startswith("-")
            field = sort.lstrip("+-")
            results = sorted(results, key=lambda x: x.get(field, 0), reverse=desc)
        return results[skip : skip + take]

    async def get_dataset(self, name: str) -> Optional[Dict[str, Any]]:
        return self._datasets.get(name)

    async def save_dataset(self, name: str, description: Optional[str], source: str, schema_definition: Dict[str, Any], row_count: int = 0) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        if name in self._datasets:
            entity = self._datasets[name]
            entity["description"] = description
            entity["source"] = source
            entity["schema_definition"] = schema_definition
            entity["row_count"] = row_count
            entity["updated_at"] = now
            return entity

        entity = {
            "id": self._next_id,
            "name": name,
            "description": description,
            "source": source,
            "schema_definition": schema_definition,
            "row_count": row_count,
            "created_at": now,
            "updated_at": now,
        }
        self._next_id += 1
        self._datasets[name] = entity
        return entity

    async def delete_dataset(self, name: str) -> bool:
        if name in self._datasets:
            del self._datasets[name]
            return True
        return False

    async def record_ingestion(self, pipeline_name: str, source: str, payload: Dict[str, Any], status: str = "success") -> Dict[str, Any]:
        rec = {
            "id": len(self._ingestions) + 1,
            "pipeline_name": pipeline_name,
            "source": source,
            "payload": payload,
            "status": status,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        self._ingestions.append(rec)
        return rec

    async def list_ingestions(self, limit: int = 20) -> List[Dict[str, Any]]:
        return list(reversed(self._ingestions))[:limit]

    async def record_pipeline_run(self, dag_name: str, status: str, duration_ms: float, results: Dict[str, Any]) -> Dict[str, Any]:
        rec = {
            "id": len(self._pipeline_runs) + 1,
            "dag_name": dag_name,
            "status": status,
            "duration_ms": duration_ms,
            "results": results,
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pipeline_runs.append(rec)
        return rec

    async def list_pipeline_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        return list(reversed(self._pipeline_runs))[:limit]

    async def ping(self) -> bool:
        return True


class SqlAlchemyRepository(DataPlatformRepository):
    def __init__(self, database_url: str):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Standardize synchronous connection string for sync operations
        sync_url = database_url
        if sync_url.startswith("postgresql+asyncpg://"):
            sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
        elif sync_url.startswith("sqlite+aiosqlite://"):
            sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")

        self.engine = create_engine(sync_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def _sync_list_datasets(self, skip: int, take: int, sort: Optional[str], filter_str: Optional[str]) -> List[Dict[str, Any]]:
        with self.SessionLocal() as session:
            query = session.query(DatasetModel)
            if filter_str:
                query = query.filter(DatasetModel.name.ilike(f"%{filter_str}%"))
            if sort:
                desc = sort.startswith("-")
                field_name = sort.lstrip("+-")
                col = getattr(DatasetModel, field_name, None)
                if col is not None:
                    query = query.order_by(col.desc() if desc else col.asc())
            rows = query.offset(skip).limit(take).all()
            return [r.to_dict() for r in rows]

    async def list_datasets(self, skip: int = 0, take: int = 10, sort: Optional[str] = None, filter_str: Optional[str] = None) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._sync_list_datasets, skip, take, sort, filter_str)

    def _sync_get_dataset(self, name: str) -> Optional[Dict[str, Any]]:
        with self.SessionLocal() as session:
            row = session.query(DatasetModel).filter(DatasetModel.name == name).first()
            return row.to_dict() if row else None

    async def get_dataset(self, name: str) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(self._sync_get_dataset, name)

    def _sync_save_dataset(self, name: str, description: Optional[str], source: str, schema_definition: Dict[str, Any], row_count: int) -> Dict[str, Any]:
        with self.SessionLocal() as session:
            row = session.query(DatasetModel).filter(DatasetModel.name == name).first()
            if row:
                row.description = description
                row.source = source
                row.schema_definition = json.dumps(schema_definition)
                row.row_count = row_count
                row.updated_at = datetime.now(timezone.utc)
            else:
                row = DatasetModel(
                    name=name,
                    description=description,
                    source=source,
                    schema_definition=json.dumps(schema_definition),
                    row_count=row_count,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                session.add(row)
            session.commit()
            session.refresh(row)
            return row.to_dict()

    async def save_dataset(self, name: str, description: Optional[str], source: str, schema_definition: Dict[str, Any], row_count: int = 0) -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync_save_dataset, name, description, source, schema_definition, row_count)

    def _sync_delete_dataset(self, name: str) -> bool:
        with self.SessionLocal() as session:
            row = session.query(DatasetModel).filter(DatasetModel.name == name).first()
            if row:
                session.delete(row)
                session.commit()
                return True
            return False

    async def delete_dataset(self, name: str) -> bool:
        return await asyncio.to_thread(self._sync_delete_dataset, name)

    def _sync_record_ingestion(self, pipeline_name: str, source: str, payload: Dict[str, Any], status: str) -> Dict[str, Any]:
        with self.SessionLocal() as session:
            row = IngestionModel(
                pipeline_name=pipeline_name,
                source=source,
                payload=json.dumps(payload),
                status=status,
                ingested_at=datetime.now(timezone.utc),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.to_dict()

    async def record_ingestion(self, pipeline_name: str, source: str, payload: Dict[str, Any], status: str = "success") -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync_record_ingestion, pipeline_name, source, payload, status)

    def _sync_list_ingestions(self, limit: int) -> List[Dict[str, Any]]:
        with self.SessionLocal() as session:
            rows = session.query(IngestionModel).order_by(IngestionModel.id.desc()).limit(limit).all()
            return [r.to_dict() for r in rows]

    async def list_ingestions(self, limit: int = 20) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._sync_list_ingestions, limit)

    def _sync_record_pipeline_run(self, dag_name: str, status: str, duration_ms: float, results: Dict[str, Any]) -> Dict[str, Any]:
        with self.SessionLocal() as session:
            row = PipelineRunModel(
                dag_name=dag_name,
                status=status,
                duration_ms=duration_ms,
                results=json.dumps(results),
                executed_at=datetime.now(timezone.utc),
            )
            session.add(row)
            session.commit()
            session.refresh(row)
            return row.to_dict()

    async def record_pipeline_run(self, dag_name: str, status: str, duration_ms: float, results: Dict[str, Any]) -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync_record_pipeline_run, dag_name, status, duration_ms, results)

    def _sync_list_pipeline_runs(self, limit: int) -> List[Dict[str, Any]]:
        with self.SessionLocal() as session:
            rows = session.query(PipelineRunModel).order_by(PipelineRunModel.id.desc()).limit(limit).all()
            return [r.to_dict() for r in rows]

    async def list_pipeline_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._sync_list_pipeline_runs, limit)

    def _sync_ping(self) -> bool:
        from sqlalchemy import text
        with self.SessionLocal() as session:
            res = session.execute(text("SELECT 1"))
            return bool(res.scalar())

    async def ping(self) -> bool:
        try:
            return await asyncio.to_thread(self._sync_ping)
        except Exception:
            return False


_global_repo: Optional[DataPlatformRepository] = None

def get_repository() -> DataPlatformRepository:
    global _global_repo
    if _global_repo is None:
        db_url = os.getenv("DATABASE_URL")
        use_memory = os.getenv("MEMORY_DB", "").lower() in ("true", "1", "yes")
        
        if db_url and not use_memory:
            try:
                _global_repo = SqlAlchemyRepository(db_url)
            except Exception as e:
                print(f"[Warning] Failed to initialize SQLAlchemy repository with {db_url}: {e}. Falling back to InMemoryRepository.")
                _global_repo = InMemoryRepository()
        else:
            _global_repo = InMemoryRepository()
    return _global_repo
