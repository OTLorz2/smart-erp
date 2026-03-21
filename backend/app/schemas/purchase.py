from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from ..models.purchase import PurchaseQuotationStatus


class PurchaseQuotationItemBase(BaseModel):
    material_id: int
    quantity: Decimal = Field(..., decimal_places=2)
    unit_price: Decimal = Field(..., decimal_places=2)
    total_price: Decimal = Field(..., decimal_places=2)


class PurchaseQuotationItemCreate(PurchaseQuotationItemBase):
    pass


class PurchaseQuotationItemResponse(PurchaseQuotationItemBase):
    id: int
    quote_id: int

    class Config:
        from_attributes = True


class PurchaseQuotationBase(BaseModel):
    supplier_id: int
    reply_date: Optional[datetime] = None
    remark: Optional[str] = None


class PurchaseQuotationCreate(PurchaseQuotationBase):
    items: List[PurchaseQuotationItemCreate] = []


class PurchaseQuotationResponse(PurchaseQuotationBase):
    id: int
    quote_no: str
    quote_date: datetime
    total_amount: Decimal
    status: PurchaseQuotationStatus
    creator_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderUpdate(BaseModel):
    delivery_date: Optional[datetime] = None
    remark: Optional[str] = None
    status: Optional[str] = None


class ReceiveRequest(BaseModel):
    items: List[dict] = []


class ReceiveResponse(BaseModel):
    order_id: int
    received: bool
    inventory_records: List[int]