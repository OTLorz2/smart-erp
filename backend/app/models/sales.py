from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class QuotationStatus(str, enum.Enum):
    """报价单状态"""
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class SalesOrderStatus(str, enum.Enum):
    """销售订单状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    CONFIRMED = "confirmed"   # 已确认
    SHIPPED = "shipped"       # 已发货
    COMPLETED = "completed"   # 已完成
    CANCELLED = "cancelled"   # 已取消


class SalesQuotation(Base):
    """销售报价单"""
    __tablename__ = "sales_quotations"

    id = Column(Integer, primary_key=True, index=True)
    quote_no = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    quote_date = Column(DateTime, default=datetime.utcnow)
    valid_date = Column(DateTime, nullable=True)
    total_amount = Column(Numeric(12, 2), default=0)
    status = Column(SQLEnum(QuotationStatus), default=QuotationStatus.DRAFT)
    remark = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="sales_quotations")
    items = relationship("SalesQuotationItem", back_populates="quote", cascade="all, delete-orphan")
    creator = relationship("User")


class SalesQuotationItem(Base):
    """报价单明细"""
    __tablename__ = "sales_quotation_items"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("sales_quotations.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)

    quote = relationship("SalesQuotation", back_populates="items")
    material = relationship("Material")


class SalesOrder(Base):
    """销售订单"""
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)  # 订单编号
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)  # 订单日期
    delivery_date = Column(DateTime, nullable=True)  # 交货日期
    total_amount = Column(Numeric(12, 2), default=0)  # 订单金额
    status = Column(SQLEnum(SalesOrderStatus), default=SalesOrderStatus.DRAFT)
    remark = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="sales_orders")
    items = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")
    creator = relationship("User")

    def __repr__(self):
        return f"<SalesOrder {self.order_no} - {self.status}>"


class SalesOrderItem(Base):
    """销售订单明细"""
    __tablename__ = "sales_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)  # 数量
    unit_price = Column(Numeric(12, 2), nullable=False)  # 单价
    total_price = Column(Numeric(12, 2), nullable=False)  # 总价
    delivered_qty = Column(Numeric(12, 2), default=0)  # 已发货数量

    # Relationships
    order = relationship("SalesOrder", back_populates="items")
    material = relationship("Material")

    def __repr__(self):
        return f"<SalesOrderItem order={self.order_id} material={self.material_id}>"