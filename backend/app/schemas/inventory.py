from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from ..models.inventory import InventoryRecordType


class InventoryRecordBase(BaseModel):
    type: InventoryRecordType
    material_id: int
    warehouse_id: int
    quantity: Decimal = Field(..., decimal_places=2)
    unit_price: Optional[Decimal] = Decimal("0")
    batch_no: Optional[str] = None
    remark: Optional[str] = None


class InventoryRecordCreate(InventoryRecordBase):
    pass


class InventoryRecordResponse(InventoryRecordBase):
    id: int
    record_no: str
    total_price: Decimal
    operator_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Stock schemas
class StockResponse(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    warehouse_id: int
    warehouse_name: str
    quantity: Decimal

    class Config:
        from_attributes = True


class StockAlertResponse(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    warehouse_name: str
    current_quantity: Decimal
    safety_stock: Decimal
    min_stock: Decimal

    class Config:
        from_attributes = True


# Stock check schemas
class StockCheckRequest(BaseModel):
    material_id: int
    warehouse_id: int
    actual_quantity: Decimal


class StockCheckResponse(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    warehouse_name: str
    system_quantity: Decimal
    actual_quantity: Decimal
    difference: Decimal