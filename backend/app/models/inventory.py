from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class InventoryRecordType(str, enum.Enum):
    """库存记录类型"""
    PURCHASE_IN = "purchase_in"      # 采购入库
    PRODUCTION_IN = "production_in"  # 生产入库
    OTHER_IN = "other_in"            # 其他入库
    SALES_OUT = "sales_out"          # 销售出库
    PRODUCTION_OUT = "production_out" # 生产领料
    OTHER_OUT = "other_out"          # 其他出库


class InventoryRecord(Base):
    """库存记录"""
    __tablename__ = "inventory_records"

    id = Column(Integer, primary_key=True, index=True)
    record_no = Column(String(50), unique=True, index=True, nullable=False)  # 单据编号
    type = Column(SQLEnum(InventoryRecordType), nullable=False)  # 类型
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)  # 数量
    unit_price = Column(Numeric(12, 2), default=0)  # 单价
    total_price = Column(Numeric(12, 2), default=0)  # 总价
    batch_no = Column(String(50), nullable=True)  # 批次号
    remark = Column(Text, nullable=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    material = relationship("Material", back_populates="inventory_records")
    warehouse = relationship("Warehouse", back_populates="inventory_records")
    operator = relationship("User")

    def __repr__(self):
        return f"<InventoryRecord {self.record_no} - {self.type}>"


class WarehouseStock(Base):
    """仓库库存"""
    __tablename__ = "warehouse_stocks"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Numeric(12, 2), default=0)  # 当前库存
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    material = relationship("Material", back_populates="warehouse_stocks")
    warehouse = relationship("Warehouse", back_populates="stocks")

    def __repr__(self):
        return f"<WarehouseStock material={self.material_id} warehouse={self.warehouse_id}>"


class AuditLog(Base):
    """审计日志"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)  # 操作类型
    resource = Column(String(50), nullable=False)  # 资源类型
    resource_id = Column(Integer, nullable=True)  # 资源ID
    details = Column(Text, nullable=True)  # 详情
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} - {self.resource}>"