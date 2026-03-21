from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.inventory import InventoryRecord, InventoryRecordType, WarehouseStock
from ..schemas.inventory import (
    InventoryRecordCreate, InventoryRecordResponse,
    StockResponse, StockAlertResponse,
    StockCheckRequest, StockCheckResponse,
)
from ..models.base_data import Material, Warehouse

router = APIRouter(prefix="/inventory", tags=["库存管理"])


def generate_record_no(prefix: str) -> str:
    """生成单据编号"""
    now = datetime.now()
    return f"{prefix}{now.strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


@router.get("/records", response_model=List[InventoryRecordResponse])
def list_inventory_records(
    skip: int = 0,
    limit: int = 100,
    material_id: int = None,
    warehouse_id: int = None,
    record_type: InventoryRecordType = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取库存记录列表"""
    query = db.query(InventoryRecord)
    if material_id:
        query = query.filter(InventoryRecord.material_id == material_id)
    if warehouse_id:
        query = query.filter(InventoryRecord.warehouse_id == warehouse_id)
    if record_type:
        query = query.filter(InventoryRecord.type == record_type)
    return query.order_by(InventoryRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/records", response_model=InventoryRecordResponse)
def create_inventory_record(
    record_data: InventoryRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建库存记录（出入库）"""
    # Validate material and warehouse exist
    material = db.query(Material).filter(Material.id == record_data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")

    warehouse = db.query(Warehouse).filter(Warehouse.id == record_data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")

    # Generate record number
    if record_data.type in [InventoryRecordType.PURCHASE_IN, InventoryRecordType.OTHER_IN]:
        record_no = generate_record_no("IN")
    elif record_data.type in [InventoryRecordType.SALES_OUT, InventoryRecordType.OTHER_OUT]:
        record_no = generate_record_no("OUT")
    else:
        record_no = generate_record_no("IO")

    # Calculate total price
    total_price = record_data.quantity * record_data.unit_price

    # Create record
    record = InventoryRecord(
        record_no=record_no,
        type=record_data.type,
        material_id=record_data.material_id,
        warehouse_id=record_data.warehouse_id,
        quantity=record_data.quantity,
        unit_price=record_data.unit_price,
        total_price=total_price,
        batch_no=record_data.batch_no,
        remark=record_data.remark,
        operator_id=current_user.id
    )
    db.add(record)

    # Update stock
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.material_id == record_data.material_id,
        WarehouseStock.warehouse_id == record_data.warehouse_id
    ).first()

    if record_data.type in [InventoryRecordType.PURCHASE_IN, InventoryRecordType.PRODUCTION_IN, InventoryRecordType.OTHER_IN]:
        #入库
        if stock:
            stock.quantity += record_data.quantity
        else:
            stock = WarehouseStock(
                material_id=record_data.material_id,
                warehouse_id=record_data.warehouse_id,
                quantity=record_data.quantity
            )
            db.add(stock)
    else:
        #出库
        if not stock or stock.quantity < record_data.quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        stock.quantity -= record_data.quantity

    db.commit()
    db.refresh(record)
    return record


@router.get("/stocks", response_model=List[StockResponse])
def list_stocks(
    warehouse_id: int = None,
    material_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取库存列表"""
    query = db.query(
        WarehouseStock,
        Material.code.label("material_code"),
        Material.name.label("material_name"),
        Warehouse.name.label("warehouse_name")
    ).join(
        Material, WarehouseStock.material_id == Material.id
    ).join(
        Warehouse, WarehouseStock.warehouse_id == Warehouse.id
    )

    if warehouse_id:
        query = query.filter(WarehouseStock.warehouse_id == warehouse_id)
    if material_id:
        query = query.filter(WarehouseStock.material_id == material_id)

    results = query.all()
    return [
        StockResponse(
            material_id=rs.WarehouseStock.material_id,
            material_code=rs.material_code,
            material_name=rs.material_name,
            warehouse_id=rs.WarehouseStock.warehouse_id,
            warehouse_name=rs.warehouse_name,
            quantity=rs.WarehouseStock.quantity
        )
        for rs in results
    ]


@router.get("/alerts", response_model=List[StockAlertResponse])
def get_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取库存预警列表"""
    # Find stocks below safety stock or min stock
    results = db.query(
        WarehouseStock,
        Material.code,
        Material.name,
        Material.safety_stock,
        Material.min_stock,
        Warehouse.name.label("warehouse_name")
    ).join(
        Material, WarehouseStock.material_id == Material.id
    ).join(
        Warehouse, WarehouseStock.warehouse_id == Warehouse.id
    ).filter(
        (WarehouseStock.quantity < Material.safety_stock) |
        (WarehouseStock.quantity < Material.min_stock)
    ).all()

    return [
        StockAlertResponse(
            material_id=rs.WarehouseStock.material_id,
            material_code=rs.code,
            material_name=rs.name,
            warehouse_name=rs.warehouse_name,
            current_quantity=rs.WarehouseStock.quantity,
            safety_stock=rs.safety_stock or 0,
            min_stock=rs.min_stock or 0
        )
        for rs in results
    ]


@router.get("/records/{record_id}", response_model=InventoryRecordResponse)
def get_inventory_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取单条出入库记录详情"""
    record = db.query(InventoryRecord).filter(InventoryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


@router.put("/records/{record_id}", response_model=InventoryRecordResponse)
def update_inventory_record(
    record_id: int,
    record_data: InventoryRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新出入库记录"""
    record = db.query(InventoryRecord).filter(InventoryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Validate material and warehouse exist
    material = db.query(Material).filter(Material.id == record_data.material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")

    warehouse = db.query(Warehouse).filter(Warehouse.id == record_data.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="仓库不存在")

    # Calculate quantity difference for stock adjustment
    quantity_diff = record_data.quantity - record.quantity

    # Update stock if quantity changed
    if quantity_diff != 0:
        stock = db.query(WarehouseStock).filter(
            WarehouseStock.material_id == record_data.material_id,
            WarehouseStock.warehouse_id == record_data.warehouse_id
        ).first()

        if record.type in [InventoryRecordType.PURCHASE_IN, InventoryRecordType.PRODUCTION_IN, InventoryRecordType.OTHER_IN]:
            # 入库
            if stock:
                stock.quantity += quantity_diff
            else:
                stock = WarehouseStock(
                    material_id=record_data.material_id,
                    warehouse_id=record_data.warehouse_id,
                    quantity=record_data.quantity
                )
                db.add(stock)
        else:
            # 出库
            if not stock or stock.quantity < quantity_diff:
                raise HTTPException(status_code=400, detail="库存不足")
            stock.quantity -= quantity_diff

    # Update record
    record.type = record_data.type
    record.material_id = record_data.material_id
    record.warehouse_id = record_data.warehouse_id
    record.quantity = record_data.quantity
    record.unit_price = record_data.unit_price
    record.total_price = record_data.quantity * record_data.unit_price
    record.batch_no = record_data.batch_no
    record.remark = record_data.remark

    db.commit()
    db.refresh(record)
    return record


@router.delete("/records/{record_id}")
def delete_inventory_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除出入库记录"""
    record = db.query(InventoryRecord).filter(InventoryRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    # Reverse stock change
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.material_id == record.material_id,
        WarehouseStock.warehouse_id == record.warehouse_id
    ).first()

    if record.type in [InventoryRecordType.PURCHASE_IN, InventoryRecordType.PRODUCTION_IN, InventoryRecordType.OTHER_IN]:
        # Reverse入库
        if stock:
            stock.quantity -= record.quantity
            if stock.quantity <= 0:
                db.delete(stock)
    else:
        # Reverse出库
        if stock:
            stock.quantity += record.quantity

    db.delete(record)
    db.commit()
    return {"message": "记录已删除"}


@router.get("/stocks/{material_id}/{warehouse_id}")
def get_stock_by_material_warehouse(
    material_id: int,
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取特定物料仓库的库存"""
    stock = db.query(WarehouseStock).filter(
        WarehouseStock.material_id == material_id,
        WarehouseStock.warehouse_id == warehouse_id
    ).first()

    if not stock:
        raise HTTPException(status_code=404, detail="库存记录不存在")

    material = db.query(Material).filter(Material.id == material_id).first()
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()

    return {
        "material_id": stock.material_id,
        "material_code": material.code if material else "",
        "material_name": material.name if material else "",
        "warehouse_id": stock.warehouse_id,
        "warehouse_name": warehouse.name if warehouse else "",
        "quantity": stock.quantity
    }


@router.post("/check", response_model=List[StockCheckResponse])
def check_stock(
    check_data: List[StockCheckRequest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """库存盘点"""
    results = []
    for item in check_data:
        stock = db.query(WarehouseStock).filter(
            WarehouseStock.material_id == item.material_id,
            WarehouseStock.warehouse_id == item.warehouse_id
        ).first()

        material = db.query(Material).filter(Material.id == item.material_id).first()
        warehouse = db.query(Warehouse).filter(Warehouse.id == item.warehouse_id).first()

        system_qty = stock.quantity if stock else 0
        diff = item.actual_quantity - system_qty

        results.append(StockCheckResponse(
            material_id=item.material_id,
            material_code=material.code if material else "",
            material_name=material.name if material else "",
            warehouse_name=warehouse.name if warehouse else "",
            system_quantity=system_qty,
            actual_quantity=item.actual_quantity,
            difference=diff
        ))

    return results