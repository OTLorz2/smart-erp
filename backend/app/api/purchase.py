from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.purchase import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from ..models.base_data import Supplier, Material

router = APIRouter(prefix="/purchase", tags=["采购管理"])


def generate_order_no() -> str:
    """生成订单编号"""
    return f"PO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


@router.get("/orders")
def list_purchase_orders(
    skip: int = 0,
    limit: int = 100,
    status: PurchaseOrderStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取采购订单列表"""
    query = db.query(PurchaseOrder)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    return query.order_by(PurchaseOrder.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/orders/{order_id}")
def get_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取采购订单详情"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("/orders")
def create_purchase_order(
    supplier_id: int,
    delivery_date: datetime = None,
    remark: str = None,
    items: List[dict] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建采购订单"""
    # Validate supplier
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    # Generate order number
    order_no = generate_order_no()

    # Calculate total amount
    total_amount = 0
    order_items = []
    for item in items:
        material = db.query(Material).filter(Material.id == item.get("material_id")).first()
        if not material:
            raise HTTPException(status_code=400, detail=f"物料ID {item.get('material_id')} 不存在")
        quantity = item.get("quantity", 0)
        unit_price = item.get("unit_price", 0)
        total_price = quantity * unit_price
        total_amount += total_price
        order_items.append({
            "material_id": item.get("material_id"),
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": total_price
        })

    # Create order
    order = PurchaseOrder(
        order_no=order_no,
        supplier_id=supplier_id,
        delivery_date=delivery_date,
        total_amount=total_amount,
        remark=remark,
        creator_id=current_user.id
    )
    db.add(order)
    db.flush()

    # Create order items
    for item_data in order_items:
        item = PurchaseOrderItem(order_id=order.id, **item_data)
        db.add(item)

    db.commit()
    db.refresh(order)
    return order


@router.put("/orders/{order_id}/status")
def update_purchase_order_status(
    order_id: int,
    status: PurchaseOrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新采购订单状态"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    order.status = status
    db.commit()
    return order