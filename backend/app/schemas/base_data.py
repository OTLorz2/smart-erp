from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from ..models.base_data import MaterialCategory


# Material schemas
class MaterialBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    category: MaterialCategory = MaterialCategory.RAW
    specification: Optional[str] = None
    unit: str = Field(..., max_length=20)
    safety_stock: Optional[Decimal] = Decimal("0")
    min_stock: Optional[Decimal] = Decimal("0")
    price: Optional[Decimal] = Decimal("0")
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[MaterialCategory] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    safety_stock: Optional[Decimal] = None
    min_stock: Optional[Decimal] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MaterialResponse(MaterialBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Warehouse schemas
class WarehouseBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    address: Optional[str] = None
    manager: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    manager: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseResponse(WarehouseBase):
    id: int
    is_default: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Supplier schemas
class SupplierBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Customer schemas
class CustomerBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True