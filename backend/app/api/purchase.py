from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import update
from typing import List
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.purchase import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus, PurchaseQuotation, PurchaseQuotationItem, PurchaseQuotationStatus
from ..models.base_data import Supplier, Material
from ..models.inventory import InventoryRecord, InventoryRecordType, WarehouseStock
from ..schemas.purchase import PurchaseQuotationCreate, PurchaseQuotationResponse, ReceiveRequest

router = APIRouter(prefix="/purchase", tags=["采购管理"])


def generate_order_no() -> str:
    """生成订单编号"""
    return f"PO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


def generate_quote_no() -> str:
    """生成询价单编号"""
    return f"PQ{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


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


# Quotation endpoints
@router.get("/quotations")
def list_purchase_quotations(
    skip: int = 0,
    limit: int = 100,
    status: PurchaseQuotationStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取询价单列表"""
    query = db.query(PurchaseQuotation)
    if status:
        query = query.filter(PurchaseQuotation.status == status)
    return query.order_by(PurchaseQuotation.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/quotations/{quote_id}")
def get_purchase_quotation(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取询价单详情"""
    quote = db.query(PurchaseQuotation).filter(PurchaseQuotation.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="询价单不存在")
    return quote


@router.post("/quotations", response_model=PurchaseQuotationResponse)
def create_purchase_quotation(
    quote_data: PurchaseQuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建询价单"""
    supplier = db.query(Supplier).filter(Supplier.id == quote_data.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    quote_no = generate_quote_no()
    total_amount = 0

    quotation = PurchaseQuotation(
        quote_no=quote_no,
        supplier_id=quote_data.supplier_id,
        reply_date=quote_data.reply_date,
        total_amount=0,
        remark=quote_data.remark,
        creator_id=current_user.id
    )
    db.add(quotation)
    db.flush()

    for item in quote_data.items:
        material = db.query(Material).filter(Material.id == item.material_id).first()
        if not material:
            raise HTTPException(status_code=400, detail=f"物料ID {item.material_id} 不存在")
        total_price = item.quantity * item.unit_price
        total_amount += total_price

        quote_item = PurchaseQuotationItem(
            quote_id=quotation.id,
            material_id=item.material_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=total_price
        )
        db.add(quote_item)

    quotation.total_amount = total_amount
    db.commit()
    db.refresh(quotation)
    return quotation


@router.put("/quotations/{quote_id}")
def update_purchase_quotation(
    quote_id: int,
    quote_data: PurchaseQuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新询价单"""
    quotation = db.query(PurchaseQuotation).filter(PurchaseQuotation.id == quote_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="询价单不存在")

    supplier = db.query(Supplier).filter(Supplier.id == quote_data.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")

    quotation.supplier_id = quote_data.supplier_id
    quotation.reply_date = quote_data.reply_date
    quotation.remark = quote_data.remark

    total_amount = 0
    db.query(PurchaseQuotationItem).filter(PurchaseQuotationItem.quote_id == quote_id).delete()
    for item in quote_data.items:
        material = db.query(Material).filter(Material.id == item.material_id).first()
        if not material:
            raise HTTPException(status_code=400, detail=f"物料ID {item.material_id} 不存在")
        total_price = item.quantity * item.unit_price
        total_amount += total_price

        quote_item = PurchaseQuotationItem(
            quote_id=quotation.id,
            material_id=item.material_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=total_price
        )
        db.add(quote_item)

    quotation.total_amount = total_amount
    db.commit()
    db.refresh(quotation)
    return quotation


@router.post("/quotations/{quote_id}/convert")
def convert_quotation_to_order(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """询价单转为采购订单"""
    quotation = db.query(PurchaseQuotation).filter(PurchaseQuotation.id == quote_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="询价单不存在")

    if quotation.status != PurchaseQuotationStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="询价单未确认，无法转为订单")

    order_no = generate_order_no()
    order = PurchaseOrder(
        order_no=order_no,
        supplier_id=quotation.supplier_id,
        total_amount=quotation.total_amount,
        remark=quotation.remark,
        creator_id=current_user.id
    )
    db.add(order)
    db.flush()

    for item in quotation.items:
        order_item = PurchaseOrderItem(
            order_id=order.id,
            material_id=item.material_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(order_item)

    quotation.status = PurchaseQuotationStatus.CONFIRMED
    db.commit()
    db.refresh(order)
    return order


# Order update and receive endpoints
@router.put("/orders/{order_id}")
def update_purchase_order(
    order_id: int,
    delivery_date: datetime = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新采购订单"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if delivery_date:
        order.delivery_date = delivery_date
    if remark:
        order.remark = remark

    db.commit()
    db.refresh(order)
    return order


@router.get("/orders/{order_id}/items")
def get_purchase_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单明细"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order.items


@router.post("/orders/{order_id}/receive")
def receive_order(
    order_id: int,
    receive_data: ReceiveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """入库确认（生成入库记录）"""
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status not in [PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.PENDING]:
        raise HTTPException(status_code=400, detail="订单状态不允许入库")

    record_ids = []
    for item in receive_data.items:
        material_id = item.get("material_id")
        quantity = item.get("quantity", 0)
        warehouse_id = item.get("warehouse_id", 1)

        # Atomic stock increase - try to update first, create if not exists
        stmt = (
            update(WarehouseStock)
            .where(
                WarehouseStock.material_id == material_id,
                WarehouseStock.warehouse_id == warehouse_id
            )
            .values(quantity=WarehouseStock.quantity + quantity)
        )
        result = db.execute(stmt)

        if result.rowcount == 0:
            # Stock record doesn't exist, create new one
            stock = WarehouseStock(
                material_id=material_id,
                warehouse_id=warehouse_id,
                quantity=quantity
            )
            db.add(stock)

        record = InventoryRecord(
            record_no=f"IN{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
            type=InventoryRecordType.PURCHASE_IN,
            material_id=material_id,
            warehouse_id=warehouse_id,
            quantity=quantity,
            unit_price=0,
            total_price=0,
            operator_id=current_user.id
        )
        db.add(record)
        db.flush()
        record_ids.append(record.id)

    order.status = PurchaseOrderStatus.RECEIVED
    db.commit()
    return {"order_id": order_id, "received": True, "inventory_records": record_ids}