from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class PurchaseOrderStatus(str, enum.Enum):
    """采购订单状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    CONFIRMED = "confirmed"   # 已确认
    RECEIVED = "received"     # 已入库
    COMPLETED = "completed"   # 已完成
    CANCELLED = "cancelled"   # 已取消


class PurchaseOrder(Base):
    """采购订单"""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)  # 订单编号
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)  # 订单日期
    delivery_date = Column(DateTime, nullable=True)  # 交货日期
    total_amount = Column(Numeric(12, 2), default=0)  # 订单金额
    status = Column(SQLEnum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT)
    remark = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")
    creator = relationship("User")

    def __repr__(self):
        return f"<PurchaseOrder {self.order_no} - {self.status}>"


class PurchaseOrderItem(Base):
    """采购订单明细"""
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)  # 数量
    unit_price = Column(Numeric(12, 2), nullable=False)  # 单价
    total_price = Column(Numeric(12, 2), nullable=False)  # 总价
    received_qty = Column(Numeric(12, 2), default=0)  # 已入库数量

    # Relationships
    order = relationship("PurchaseOrder", back_populates="items")
    material = relationship("Material")

    def __repr__(self):
        return f"<PurchaseOrderItem order={self.order_id} material={self.material_id}>"