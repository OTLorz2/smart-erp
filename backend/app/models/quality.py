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

    def __repr__(self):
        return f"<QCRecord {self.record_no} - {self.status}>"