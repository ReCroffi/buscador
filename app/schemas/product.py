from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    query: str = Field(min_length=3, max_length=255)
    sku: str | None = None
    brand: str | None = None
    model: str | None = None


class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    normalized_query: str
    created_at: datetime
    updated_at: datetime

