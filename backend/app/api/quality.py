from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.quality import QCRecord, QCStatus, QCType, QCStandard, UnqualifiedRecord, DispositionType
from ..models.base_data import Material
from ..models.production import ProductionOrder
from ..models.inventory import InventoryRecord

router = APIRouter(prefix="/quality", tags=["质量管理"])


def generate_qc_no() -> str:
    return f"QC{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


# ==================== QC Standard API ====================

@router.get("/standards")
def list_qc_standards(
    skip: int = 0,
    limit: int = 100,
    qc_type: QCType = None,
    material_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取质检标准列表"""
    query = db.query(QCStandard)
    if qc_type:
        query = query.filter(QCStandard.qc_type == qc_type)
    if material_id:
        query = query.filter(QCStandard.material_id == material_id)
    return query.order_by(QCStandard.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/standards/{standard_id}")
def get_qc_standard(
    standard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取质检标准详情"""
    standard = db.query(QCStandard).filter(QCStandard.id == standard_id).first()
    if not standard:
        raise HTTPException(status_code=404, detail="质检标准不存在")
    return standard


@router.post("/standards")
def create_qc_standard(
    material_id: int,
    qc_type: QCType,
    item_name: str,
    standard: str = None,
    tolerance: str = None,
    inspector_level: str = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建质检标准"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")

    std = QCStandard(
        material_id=material_id,
        qc_type=qc_type,
        item_name=item_name,
        standard=standard,
        tolerance=tolerance,
        inspector_level=inspector_level,
        remark=remark,
        creator_id=current_user.id
    )
    db.add(std)
    db.commit()
    db.refresh(std)
    return std


@router.put("/standards/{standard_id}")
def update_qc_standard(
    standard_id: int,
    item_name: str = None,
    standard: str = None,
    tolerance: str = None,
    inspector_level: str = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新质检标准"""
    std = db.query(QCStandard).filter(QCStandard.id == standard_id).first()
    if not std:
        raise HTTPException(status_code=404, detail="质检标准不存在")

    if item_name:
        std.item_name = item_name
    if standard is not None:
        std.standard = standard
    if tolerance is not None:
        std.tolerance = tolerance
    if inspector_level is not None:
        std.inspector_level = inspector_level
    if remark is not None:
        std.remark = remark

    db.commit()
    db.refresh(std)
    return std


@router.delete("/standards/{standard_id}")
def delete_qc_standard(
    standard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除质检标准"""
    std = db.query(QCStandard).filter(QCStandard.id == standard_id).first()
    if not std:
        raise HTTPException(status_code=404, detail="质检标准不存在")

    db.delete(std)
    db.commit()
    return {"deleted": True}


# ==================== QC Record API ====================

@router.get("/records")
def list_qc_records(
    skip: int = 0,
    limit: int = 100,
    qc_type: QCType = None,
    status: QCStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取质检记录列表"""
    query = db.query(QCRecord)
    if qc_type:
        query = query.filter(QCRecord.qc_type == qc_type)
    if status:
        query = query.filter(QCRecord.status == status)
    return query.order_by(QCRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/records/{record_id}")
def get_qc_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取质检记录详情"""
    record = db.query(QCRecord).filter(QCRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质检记录不存在")
    return record


@router.post("/records")
def create_qc_record(
    qc_type: QCType,
    material_id: int,
    quantity: float,
    batch_no: str = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建质检单"""
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="物料不存在")

    record = QCRecord(
        record_no=generate_qc_no(),
        qc_type=qc_type,
        material_id=material_id,
        quantity=quantity,
        batch_no=batch_no,
        remark=remark,
        inspector_id=current_user.id
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/records/{record_id}/result")
def update_qc_result(
    record_id: int,
    qualified_qty: float,
    unqualified_qty: float,
    result: str = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """录入质检结果"""
    record = db.query(QCRecord).filter(QCRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质检记录不存在")

    record.qualified_qty = qualified_qty
    record.unqualified_qty = unqualified_qty
    record.result = result
    record.remark = remark

    if qualified_qty >= record.quantity:
        record.status = QCStatus.PASSED
    elif qualified_qty > 0:
        record.status = QCStatus.REWORK
    else:
        record.status = QCStatus.FAILED

    record.inspect_date = datetime.utcnow()
    record.inspector_id = current_user.id

    db.commit()
    db.refresh(record)
    return record


@router.put("/records/{record_id}/status")
def update_qc_status(
    record_id: int,
    status: QCStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新质检状态"""
    record = db.query(QCRecord).filter(QCRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质检记录不存在")

    record.status = status
    db.commit()
    db.refresh(record)
    return record


@router.get("/records/{record_id}/trace")
def get_qc_trace(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取质量追溯信息"""
    record = db.query(QCRecord).filter(QCRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="质检记录不存在")

    trace_info = {
        "qc_record": record,
        "material": record.material,
        "unqualified_records": record.unqualified_records
    }

    # 根据质检类型追溯上游
    if record.qc_type == QCType.IQC:
        # 追溯采购入库单
        trace_info["source_type"] = "purchase"
    elif record.qc_type == QCType.OQC:
        # 追溯生产工单
        orders = db.query(ProductionOrder).filter(
            ProductionOrder.product_id == record.material_id,
            ProductionOrder.status.in_(["completed", "qc_passed"])
        ).all()
        trace_info["source_type"] = "production"
        trace_info["production_orders"] = orders
    elif record.qc_type == QCType.IPQC:
        # 追溯生产工单
        orders = db.query(ProductionOrder).filter(
            ProductionOrder.product_id == record.material_id,
            ProductionOrder.status == "in_progress"
        ).all()
        trace_info["source_type"] = "production"
        trace_info["production_orders"] = orders

    return trace_info


# ==================== Unqualified Record API ====================

@router.get("/unqualified")
def list_unqualified(
    skip: int = 0,
    limit: int = 100,
    disposition: DispositionType = None,
    qc_record_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取不良品列表"""
    query = db.query(UnqualifiedRecord)
    if disposition:
        query = query.filter(UnqualifiedRecord.disposition == disposition)
    if qc_record_id:
        query = query.filter(UnqualifiedRecord.qc_record_id == qc_record_id)
    return query.order_by(UnqualifiedRecord.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/unqualified")
def create_unqualified(
    qc_record_id: int,
    defect_type: str,
    quantity: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """登记不良品"""
    qc_record = db.query(QCRecord).filter(QCRecord.id == qc_record_id).first()
    if not qc_record:
        raise HTTPException(status_code=404, detail="质检记录不存在")

    record = UnqualifiedRecord(
        qc_record_id=qc_record_id,
        defect_type=defect_type,
        quantity=quantity
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/unqualified/{record_id}")
def update_unqualified(
    record_id: int,
    disposition: DispositionType = None,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """处理不良品"""
    record = db.query(UnqualifiedRecord).filter(UnqualifiedRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="不良品记录不存在")

    if disposition:
        record.disposition = disposition
        record.disposition_date = datetime.utcnow()
        record.disposition_by = current_user.id
    if remark is not None:
        record.remark = remark

    db.commit()
    db.refresh(record)
    return record