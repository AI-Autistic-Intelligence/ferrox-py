from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from ferrox_py.core.container import Container
from ferrox_py.core.controllers import BaseController
from ..persistence import get_repository


class CreateDatasetRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=128, description="Unique dataset identifier", json_schema_extra={"example": "dataset_clickstream"})
    description: Optional[str] = Field(None, description="Human-readable description of dataset schema and purpose", json_schema_extra={"example": "High-volume web clickstream events"})
    source: str = Field("internal", description="Origin data source system", json_schema_extra={"example": "Kafka topic user-clicks"})
    schema_definition: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema attribute dictionary", json_schema_extra={"example": {"user_id": "string", "url": "string", "timestamp": "string"}})
    row_count: int = Field(0, ge=0, description="Estimated initial row count")


class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    source: str
    schema_definition: Dict[str, Any]
    row_count: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CatalogController(BaseController):
    def __init__(self, container: Container):
        super().__init__(prefix="/catalog", tags=["Data Catalog"])
        self.container = container
        self.repo = get_repository()

        @self.router.get(
            "/datasets",
            response_model=Dict[str, Any],
            summary="List Data Catalog Datasets",
            description="Queries metadata catalog datasets with optional pagination, sorting, and text filtering.",
        )
        async def list_datasets(
            skip: int = Query(0, ge=0, description="Number of items to skip"),
            take: int = Query(10, ge=1, le=100, description="Number of items to return"),
            sort: Optional[str] = Query(None, description="Sort field (prefix with - for descending, e.g. -row_count)"),
            filter_str: Optional[str] = Query(None, alias="filter", description="Search query string matching dataset name or description"),
        ):
            datasets = await self.repo.list_datasets(skip=skip, take=take, sort=sort, filter_str=filter_str)
            return self.ok(
                {
                    "total": len(datasets),
                    "skip": skip,
                    "take": take,
                    "datasets": datasets,
                },
                "Catalog queried successfully",
            )

        @self.router.post(
            "/datasets",
            response_model=Dict[str, Any],
            status_code=status.HTTP_201_CREATED,
            summary="Register New Dataset",
            description="Registers a new dataset schema contract into the enterprise data catalog.",
        )
        async def create_dataset(payload: CreateDatasetRequest):
            existing = await self.repo.get_dataset(payload.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Dataset '{payload.name}' already exists in catalog.",
                )
            entity = await self.repo.save_dataset(
                name=payload.name,
                description=payload.description,
                source=payload.source,
                schema_definition=payload.schema_definition,
                row_count=payload.row_count,
            )
            return self.ok(entity, "Dataset registered successfully")

        @self.router.get(
            "/datasets/{name}",
            response_model=Dict[str, Any],
            summary="Get Dataset Details",
            description="Retrieves dataset metadata schema and statistics by unique name.",
        )
        async def get_dataset(name: str):
            dataset = await self.repo.get_dataset(name)
            if not dataset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dataset '{name}' not found in catalog.",
                )
            return self.ok(dataset, "Dataset retrieved successfully")

        @self.router.delete(
            "/datasets/{name}",
            response_model=Dict[str, Any],
            summary="Delete Dataset",
            description="Removes a dataset from the catalog metadata repository.",
        )
        async def delete_dataset(name: str):
            deleted = await self.repo.delete_dataset(name)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dataset '{name}' not found.",
                )
            return self.ok({"deleted": True, "name": name}, "Dataset deleted successfully")
