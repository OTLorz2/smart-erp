from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from ..models.sales import QuotationStatus


class SalesQuotationItemBase(BaseModel):
    material_id: int
    quantity: Decimal = Field(..., decimal_places=2)
    unit_price: Decimal = Field(..., decimal_places=2)
    total_price: Decimal = Field(..., decimal_places=2)


class SalesQuotationItemCreate(SalesQuotationItemBase):
    pass


class SalesQuotationItemResponse(SalesQuotationItemBase):
    id: int
    quote_id: int

    class Config:
        from_attributes = True


class SalesQuotationBase(BaseModel):
    customer_id: int
    valid_date: Optional[datetime] = None
    remark: Optional[str] = None


class SalesQuotationCreate(SalesQuotationBase):
    items: List[SalesQuotationItemCreate] = []


class SalesQuotationResponse(SalesQuotationBase):
    id: int
    quote_no: str
    quote_date: datetime
    total_amount: Decimal
    status: QuotationStatus
    creator_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class SalesOrderUpdate(BaseModel):
    delivery_date: Optional[datetime] = None
    remark: Optional[str] = None
    status: Optional[str] = None


class ShipRequest(BaseModel):
    items: List[dict] = []


class ShipResponse(BaseModel):
    order_id: int
    shipped: bool
    inventory_records: List[int]