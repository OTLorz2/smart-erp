from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.base_data import Material, Warehouse, Supplier, Customer
from ..schemas.base_data import (
    MaterialCreate, MaterialUpdate, MaterialResponse,
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse,
    CustomerCreate, CustomerUpdate, CustomerResponse,
)

router = APIRouter(prefix="/base-data", tags=["基础数据"])


# ==================== Material ====================
@router.get("/materials", response_model=List[MaterialResponse])
def list_materials(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取物料列表"""
    query = db.query(Material)
    if is_active is not None:
        query = query.filter(Material.is_active == is_active)
    return query.offset(skip).limit(limit).all()


@router.get("/materials/{material_id}", response_model=MaterialResponse)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取物料详情"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")
    return material


@router.post("/materials", response_model=MaterialResponse)
def create_material(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建物料"""
    existing = db.query(Material).filter(Material.code == material_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="物料编码已存在")

    material = Material(**material_data.model_dump())
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


@router.put("/materials/{material_id}", response_model=MaterialResponse)
def update_material(
    material_id: int,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新物料"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")

    for field, value in material_data.model_dump(exclude_unset=True).items():
        setattr(material, field, value)

    db.commit()
    db.refresh(material)
    return material


# ==================== Warehouse ====================
@router.get("/warehouses", response_model=List[WarehouseResponse])
def list_warehouses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取仓库列表"""
    return db.query(Warehouse).offset(skip).limit(limit).all()


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取仓库详情"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return warehouse


@router.post("/warehouses", response_model=WarehouseResponse)
def create_warehouse(
    warehouse_data: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建仓库"""
    existing = db.query(Warehouse).filter(Warehouse.code == warehouse_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="仓库编码已存在")

    warehouse = Warehouse(**warehouse_data.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: int,
    warehouse_data: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新仓库"""
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")

    for field, value in warehouse_data.model_dump(exclude_unset=True).items():
        setattr(warehouse, field, value)

    db.commit()
    db.refresh(warehouse)
    return warehouse


# ==================== Supplier ====================
@router.get("/suppliers", response_model=List[SupplierResponse])
def list_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取供应商列表"""
    return db.query(Supplier).offset(skip).limit(limit).all()


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建供应商"""
    existing = db.query(Supplier).filter(Supplier.code == supplier_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="供应商编码已存在")

    supplier = Supplier(**supplier_data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


# ==================== Customer ====================
@router.get("/customers", response_model=List[CustomerResponse])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取客户列表"""
    return db.query(Customer).offset(skip).limit(limit).all()


@router.post("/customers", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建客户"""
    existing = db.query(Customer).filter(Customer.code == customer_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="客户编码已存在")

    customer = Customer(**customer_data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer