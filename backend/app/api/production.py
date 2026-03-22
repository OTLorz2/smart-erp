from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.production import (
    ProductionOrder, ProductionOrderItem, ProductionRecord, ProductionOrderStatus,
    BOM, BOMItem, BOMStatus, ProcessRoute, ProcessStep, ProcessRouteStatus
)
from ..models.base_data import Material

router = APIRouter(prefix="/production", tags=["生产管理"])


def generate_bom_no() -> str:
    return f"BOM{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


def generate_route_no() -> str:
    return f"RT{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


def generate_order_no() -> str:
    return f"PO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


# ==================== BOM API ====================

@router.get("/boms")
def list_boms(
    skip: int = 0,
    limit: int = 100,
    status: BOMStatus = None,
    product_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取BOM列表"""
    query = db.query(BOM)
    if status:
        query = query.filter(BOM.status == status)
    if product_id:
        query = query.filter(BOM.product_id == product_id)
    return query.order_by(BOM.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/boms/{bom_id}")
def get_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取BOM详情"""
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM不存在")
    return bom


@router.post("/boms")
def create_bom(
    product_id: int,
    version: str = "v1",
    effective_date: datetime = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建BOM"""
    product = db.query(Material).filter(Material.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    bom = BOM(
        bom_no=generate_bom_no(),
        product_id=product_id,
        version=version,
        effective_date=effective_date,
        remark=remark,
        creator_id=current_user.id
    )
    db.add(bom)
    db.commit()
    db.refresh(bom)
    return bom


@router.put("/boms/{bom_id}")
def update_bom(
    bom_id: int,
    version: str = None,
    effective_date: datetime = None,
    status: BOMStatus = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新BOM"""
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM不存在")

    if version:
        bom.version = version
    if effective_date:
        bom.effective_date = effective_date
    if status:
        bom.status = status
    if remark is not None:
        bom.remark = remark

    db.commit()
    db.refresh(bom)
    return bom


@router.delete("/boms/{bom_id}")
def delete_bom(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除BOM"""
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM不存在")

    db.delete(bom)
    db.commit()
    return {"deleted": True}


@router.get("/boms/{bom_id}/items")
def get_bom_items(
    bom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取BOM明细"""
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM不存在")
    return bom.items


@router.put("/boms/{bom_id}/items")
def update_bom_items(
    bom_id: int,
    items: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新BOM明细"""
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM不存在")

    # Delete existing items
    db.query(BOMItem).filter(BOMItem.bom_id == bom_id).delete()

    # Add new items
    for item in items:
        material_id = item.get("material_id")
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise HTTPException(status_code=400, detail=f"物料ID {material_id} 不存在")

        bom_item = BOMItem(
            bom_id=bom_id,
            material_id=material_id,
            quantity=item.get("quantity", 0),
            scrap_rate=item.get("scrap_rate", 0)
        )
        db.add(bom_item)

    db.commit()
    db.refresh(bom)
    return bom.items


# ==================== Process Route API ====================

@router.get("/routes")
def list_routes(
    skip: int = 0,
    limit: int = 100,
    status: ProcessRouteStatus = None,
    product_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取工艺路线列表"""
    query = db.query(ProcessRoute)
    if status:
        query = query.filter(ProcessRoute.status == status)
    if product_id:
        query = query.filter(ProcessRoute.product_id == product_id)
    return query.order_by(ProcessRoute.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/routes/{route_id}")
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取工艺路线详情"""
    route = db.query(ProcessRoute).filter(ProcessRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="工艺路线不存在")
    return route


@router.post("/routes")
def create_route(
    product_id: int,
    version: str = "v1",
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建工艺路线"""
    product = db.query(Material).filter(Material.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    route = ProcessRoute(
        route_no=generate_route_no(),
        product_id=product_id,
        version=version,
        remark=remark,
        creator_id=current_user.id
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.put("/routes/{route_id}")
def update_route(
    route_id: int,
    version: str = None,
    status: ProcessRouteStatus = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新工艺路线"""
    route = db.query(ProcessRoute).filter(ProcessRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="工艺路线不存在")

    if version:
        route.version = version
    if status:
        route.status = status
    if remark is not None:
        route.remark = remark

    db.commit()
    db.refresh(route)
    return route


@router.delete("/routes/{route_id}")
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除工艺路线"""
    route = db.query(ProcessRoute).filter(ProcessRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="工艺路线不存在")

    db.delete(route)
    db.commit()
    return {"deleted": True}


@router.get("/routes/{route_id}/steps")
def get_route_steps(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取工序步骤"""
    route = db.query(ProcessRoute).filter(ProcessRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="工艺路线不存在")
    return sorted(route.steps, key=lambda x: x.step_no)


@router.put("/routes/{route_id}/steps")
def update_route_steps(
    route_id: int,
    steps: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新工序步骤"""
    route = db.query(ProcessRoute).filter(ProcessRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="工艺路线不存在")

    # Delete existing steps
    db.query(ProcessStep).filter(ProcessStep.route_id == route_id).delete()

    # Add new steps
    for item in steps:
        step = ProcessStep(
            route_id=route_id,
            step_no=item.get("step_no", 0),
            step_name=item.get("step_name", ""),
            station_id=item.get("station_id"),
            standard_time=item.get("standard_time"),
            remark=item.get("remark")
        )
        db.add(step)

    db.commit()
    db.refresh(route)
    return sorted(route.steps, key=lambda x: x.step_no)


# ==================== Production Order API ====================

@router.get("/orders")
def list_production_orders(
    skip: int = 0,
    limit: int = 100,
    status: ProductionOrderStatus = None,
    product_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取生产工单列表"""
    query = db.query(ProductionOrder)
    if status:
        query = query.filter(ProductionOrder.status == status)
    if product_id:
        query = query.filter(ProductionOrder.product_id == product_id)
    return query.order_by(ProductionOrder.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/orders/{order_id}")
def get_production_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取生产工单详情"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")
    return order


@router.post("/orders")
def create_production_order(
    product_id: int,
    quantity: float,
    start_date: datetime = None,
    end_date: datetime = None,
    remark: str = None,
    items: List[dict] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建生产工单"""
    product = db.query(Material).filter(Material.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")

    order = ProductionOrder(
        order_no=generate_order_no(),
        product_id=product_id,
        quantity=quantity,
        start_date=start_date,
        end_date=end_date,
        remark=remark,
        creator_id=current_user.id
    )
    db.add(order)
    db.flush()

    # Add items
    for item in items:
        material_id = item.get("material_id")
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise HTTPException(status_code=400, detail=f"物料ID {material_id} 不存在")

        order_item = ProductionOrderItem(
            order_id=order.id,
            material_id=material_id,
            quantity=item.get("quantity", 0)
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order


@router.put("/orders/{order_id}")
def update_production_order(
    order_id: int,
    quantity: float = None,
    start_date: datetime = None,
    end_date: datetime = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新生产工单"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")

    if quantity:
        order.quantity = quantity
    if start_date:
        order.start_date = start_date
    if end_date:
        order.end_date = end_date
    if remark is not None:
        order.remark = remark

    db.commit()
    db.refresh(order)
    return order


@router.delete("/orders/{order_id}")
def delete_production_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除生产工单"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")

    db.delete(order)
    db.commit()
    return {"deleted": True}


# Define valid state transitions for production orders
VALID_TRANSITIONS = {
    ProductionOrderStatus.DRAFT: [ProductionOrderStatus.PENDING, ProductionOrderStatus.CANCELLED],
    ProductionOrderStatus.PENDING: [ProductionOrderStatus.IN_PROGRESS, ProductionOrderStatus.CANCELLED],
    ProductionOrderStatus.IN_PROGRESS: [ProductionOrderStatus.COMPLETED, ProductionOrderStatus.QC_PASSED, ProductionOrderStatus.CANCELLED],
    ProductionOrderStatus.QC_PASSED: [ProductionOrderStatus.COMPLETED, ProductionOrderStatus.CANCELLED],
    ProductionOrderStatus.QC_FAILED: [ProductionOrderStatus.IN_PROGRESS, ProductionOrderStatus.CANCELLED],
    ProductionOrderStatus.COMPLETED: [],  # Final state
    ProductionOrderStatus.CANCELLED: [],  # Final state
}


def validate_status_transition(current: ProductionOrderStatus, new: ProductionOrderStatus) -> bool:
    """Validate if status transition is allowed"""
    return new in VALID_TRANSITIONS.get(current, [])


@router.put("/orders/{order_id}/status")
def update_production_order_status(
    order_id: int,
    status: ProductionOrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新工单状态"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")

    # Validate state transition
    if not validate_status_transition(order.status, status):
        raise HTTPException(
            status_code=400,
            detail=f"不能从 {order.status.value} 转换到 {status.value}"
        )

    order.status = status
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders/{order_id}/items")
def get_production_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取工单物料明细"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")
    return order.items


@router.put("/orders/{order_id}/items")
def update_production_order_items(
    order_id: int,
    items: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新工单物料明细"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")

    # Delete existing items
    db.query(ProductionOrderItem).filter(ProductionOrderItem.order_id == order_id).delete()

    # Add new items
    for item in items:
        material_id = item.get("material_id")
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise HTTPException(status_code=400, detail=f"物料ID {material_id} 不存在")

        order_item = ProductionOrderItem(
            order_id=order_id,
            material_id=material_id,
            quantity=item.get("quantity", 0)
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order.items


# ==================== Production Record API ====================

@router.get("/orders/{order_id}/records")
def get_production_records(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取报工记录"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")
    return db.query(ProductionRecord).filter(ProductionRecord.order_id == order_id).order_by(ProductionRecord.created_at.desc()).all()


@router.post("/orders/{order_id}/report")
def report_production(
    order_id: int,
    quantity: float,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """提交报工"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")

    if order.status not in [ProductionOrderStatus.PENDING, ProductionOrderStatus.IN_PROGRESS]:
        raise HTTPException(status_code=400, detail="工单状态不允许报工")

    # Create record
    record = ProductionRecord(
        order_id=order_id,
        quantity=quantity,
        worker_id=current_user.id,
        remark=remark
    )
    db.add(record)

    # Update completed quantity
    order.completed_qty = (order.completed_qty or 0) + quantity
    if order.status == ProductionOrderStatus.PENDING:
        order.status = ProductionOrderStatus.IN_PROGRESS

    db.commit()
    db.refresh(order)
    return {"order": order, "record": record}


@router.post("/orders/{order_id}/start")
def start_production(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """开始生产"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")

    if order.status != ProductionOrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="工单状态不是待生产")

    order.status = ProductionOrderStatus.IN_PROGRESS
    order.actual_start = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/{order_id}/complete")
def complete_production(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """完工确认"""
    order = db.query(ProductionOrder).filter(ProductionOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="生产工单不存在")

    if order.status not in [ProductionOrderStatus.IN_PROGRESS, ProductionOrderStatus.QC_PASSED]:
        raise HTTPException(status_code=400, detail="工单状态不允许完工")

    order.status = ProductionOrderStatus.COMPLETED
    order.actual_end = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order