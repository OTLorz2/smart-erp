from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.sales import SalesOrder, SalesOrderItem, SalesOrderStatus, SalesQuotation, SalesQuotationItem, QuotationStatus
from ..models.base_data import Customer, Material
from ..models.inventory import InventoryRecord, InventoryRecordType, WarehouseStock
from ..schemas.sales import SalesQuotationCreate, SalesQuotationResponse, ShipRequest

router = APIRouter(prefix="/sales", tags=["销售管理"])


def generate_order_no() -> str:
    """生成订单编号"""
    return f"SO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


def generate_quote_no() -> str:
    """生成报价单编号"""
    return f"QT{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


@router.get("/orders")
def list_sales_orders(
    skip: int = 0,
    limit: int = 100,
    status: SalesOrderStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取销售订单列表"""
    query = db.query(SalesOrder)
    if status:
        query = query.filter(SalesOrder.status == status)
    return query.order_by(SalesOrder.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/orders/{order_id}")
def get_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取销售订单详情"""
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("/orders")
def create_sales_order(
    customer_id: int,
    delivery_date: datetime = None,
    remark: str = None,
    items: List[dict] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建销售订单"""
    # Validate customer
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

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
    order = SalesOrder(
        order_no=order_no,
        customer_id=customer_id,
        delivery_date=delivery_date,
        total_amount=total_amount,
        remark=remark,
        creator_id=current_user.id
    )
    db.add(order)
    db.flush()  # Get order ID

    # Create order items
    for item_data in order_items:
        item = SalesOrderItem(order_id=order.id, **item_data)
        db.add(item)

    db.commit()
    db.refresh(order)
    return order


@router.put("/orders/{order_id}/status")
def update_sales_order_status(
    order_id: int,
    status: SalesOrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新销售订单状态"""
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    order.status = status
    db.commit()
    return order


# Quotation endpoints
@router.get("/quotations")
def list_sales_quotations(
    skip: int = 0,
    limit: int = 100,
    status: QuotationStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报价单列表"""
    query = db.query(SalesQuotation)
    if status:
        query = query.filter(SalesQuotation.status == status)
    return query.order_by(SalesQuotation.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/quotations/{quote_id}")
def get_sales_quotation(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报价单详情"""
    quote = db.query(SalesQuotation).filter(SalesQuotation.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="报价单不存在")
    return quote


@router.post("/quotations", response_model=SalesQuotationResponse)
def create_sales_quotation(
    quote_data: SalesQuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建报价单"""
    customer = db.query(Customer).filter(Customer.id == quote_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    quote_no = generate_quote_no()
    total_amount = 0

    quotation = SalesQuotation(
        quote_no=quote_no,
        customer_id=quote_data.customer_id,
        valid_date=quote_data.valid_date,
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

        quote_item = SalesQuotationItem(
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
def update_sales_quotation(
    quote_id: int,
    quote_data: SalesQuotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新报价单"""
    quotation = db.query(SalesQuotation).filter(SalesQuotation.id == quote_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="报价单不存在")

    customer = db.query(Customer).filter(Customer.id == quote_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    quotation.customer_id = quote_data.customer_id
    quotation.valid_date = quote_data.valid_date
    quotation.remark = quote_data.remark

    total_amount = 0
    db.query(SalesQuotationItem).filter(SalesQuotationItem.quote_id == quote_id).delete()
    for item in quote_data.items:
        material = db.query(Material).filter(Material.id == item.material_id).first()
        if not material:
            raise HTTPException(status_code=400, detail=f"物料ID {item.material_id} 不存在")
        total_price = item.quantity * item.unit_price
        total_amount += total_price

        quote_item = SalesQuotationItem(
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
    """报价单转为销售订单"""
    quotation = db.query(SalesQuotation).filter(SalesQuotation.id == quote_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="报价单不存在")

    if quotation.status != QuotationStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="报价单未确认，无法转为订单")

    order_no = generate_order_no()
    order = SalesOrder(
        order_no=order_no,
        customer_id=quotation.customer_id,
        total_amount=quotation.total_amount,
        remark=quotation.remark,
        creator_id=current_user.id
    )
    db.add(order)
    db.flush()

    for item in quotation.items:
        order_item = SalesOrderItem(
            order_id=order.id,
            material_id=item.material_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(order_item)

    quotation.status = QuotationStatus.CONFIRMED
    db.commit()
    db.refresh(order)
    return order


# Order update and ship endpoints
@router.put("/orders/{order_id}")
def update_sales_order(
    order_id: int,
    delivery_date: datetime = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新销售订单"""
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
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
def get_sales_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取订单明细"""
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order.items


@router.post("/orders/{order_id}/ship")
def ship_order(
    order_id: int,
    ship_data: ShipRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """发货确认（生成出库记录）"""
    order = db.query(SalesOrder).filter(SalesOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order.status not in [SalesOrderStatus.CONFIRMED, SalesOrderStatus.PENDING]:
        raise HTTPException(status_code=400, detail="订单状态不允许发货")

    record_ids = []
    for item in ship_data.items:
        material_id = item.get("material_id")
        quantity = item.get("quantity", 0)
        warehouse_id = item.get("warehouse_id", 1)

        stock = db.query(WarehouseStock).filter(
            WarehouseStock.material_id == material_id,
            WarehouseStock.warehouse_id == warehouse_id
        ).first()

        if not stock or stock.quantity < quantity:
            raise HTTPException(status_code=400, detail=f"物料ID {material_id} 库存不足")

        stock.quantity -= quantity

        record = InventoryRecord(
            record_no=f"OUT{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
            type=InventoryRecordType.SALES_OUT,
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

    order.status = SalesOrderStatus.SHIPPED
    db.commit()
    return {"order_id": order_id, "shipped": True, "inventory_records": record_ids}