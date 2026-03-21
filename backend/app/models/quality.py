from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class QCStatus(str, enum.Enum):
    """质检状态"""
    PENDING = "pending"       # 待质检
    PASSED = "passed"         # 合格
    FAILED = "failed"         # 不合格
    REWORK = "rework"         # 返工


class QCType(str, enum.Enum):
    """质检类型"""
    IQC = "iqc"               # 来料检验
    IPQC = "ipqc"             # 制程检验
    OQC = "oqc"               # 成品检验


class QCRecord(Base):
    """质检记录"""
    __tablename__ = "qc_records"

    id = Column(Integer, primary_key=True, index=True)
    record_no = Column(String(50), unique=True, index=True, nullable=False)  # 质检单号
    qc_type = Column(SQLEnum(QCType), nullable=False)  # 质检类型
    batch_no = Column(String(50), nullable=True)  # 批次号
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)  # 检验数量
    qualified_qty = Column(Numeric(12, 2), default=0)  # 合格数量
    unqualified_qty = Column(Numeric(12, 2), default=0)  # 不合格数量
    status = Column(SQLEnum(QCStatus), default=QCStatus.PENDING)
    result = Column(String(50), nullable=True)  # 检验结果
    remark = Column(Text, nullable=True)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 质检员
    inspect_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    material = relationship("Material")
    inspector = relationship("User")
    unqualified_records = relationship("UnqualifiedRecord", back_populates="qc_record", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QCRecord {self.record_no} - {self.status}>"


class QCStandard(Base):
    """质检标准"""
    __tablename__ = "qc_standards"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)  # 物料
    qc_type = Column(SQLEnum(QCType), nullable=False)  # 质检类型
    item_name = Column(String(100), nullable=False)  # 检验项目
    standard = Column(String(200), nullable=True)  # 标准值
    tolerance = Column(String(100), nullable=True)  # 公差范围
    inspector_level = Column(String(20), nullable=True)  # 检验等级
    remark = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    material = relationship("Material")
    creator = relationship("User")

    def __repr__(self):
        return f"<QCStandard {self.item_name}>"


class DispositionType(str, enum.Enum):
    """不良品处理方式"""
    SCRAP = "scrap"         # 报废
    REWORK = "rework"       # 返工
    SPECIAL_ACCEPT = "special_accept"  # 特采
    RETURN = "return"       # 退货


class UnqualifiedRecord(Base):
    """不良品记录"""
    __tablename__ = "unqualified_records"

    id = Column(Integer, primary_key=True, index=True)
    qc_record_id = Column(Integer, ForeignKey("qc_records.id"), nullable=False)
    defect_type = Column(String(100), nullable=False)  # 不良类型
    quantity = Column(Numeric(12, 2), nullable=False)  # 数量
    disposition = Column(SQLEnum(DispositionType), nullable=True)  # 处理方式
    disposition_date = Column(DateTime, nullable=True)  # 处理日期
    disposition_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 处理人
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    qc_record = relationship("QCRecord", back_populates="unqualified_records")
    disposition_by_user = relationship("User")

    def __repr__(self):
        return f"<UnqualifiedRecord defect={self.defect_type} qty={self.quantity}>"