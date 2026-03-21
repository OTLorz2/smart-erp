from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class ProductionOrderStatus(str, enum.Enum):
    """生产工单状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待生产
    IN_PROGRESS = "in_progress"  # 生产中
    QC_PASSED = "qc_passed"   # 质检通过
    QC_FAILED = "qc_failed"   # 质检失败
    COMPLETED = "completed"   # 已完工
    CANCELLED = "cancelled"   # 已取消


class ProductionOrder(Base):
    """生产工单"""
    __tablename__ = "production_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)  # 工单编号
    product_id = Column(Integer, ForeignKey("materials.id"), nullable=False)  # 产品
    quantity = Column(Numeric(12, 2), nullable=False)  # 计划数量
    completed_qty = Column(Numeric(12, 2), default=0)  # 已完成数量
    start_date = Column(DateTime, nullable=True)  # 计划开始日期
    end_date = Column(DateTime, nullable=True)  # 计划结束日期
    actual_start = Column(DateTime, nullable=True)  # 实际开始
    actual_end = Column(DateTime, nullable=True)  # 实际结束
    status = Column(SQLEnum(ProductionOrderStatus), default=ProductionOrderStatus.DRAFT)
    remark = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Material")
    items = relationship("ProductionOrderItem", back_populates="order", cascade="all, delete-orphan")
    creator = relationship("User")

    def __repr__(self):
        return f"<ProductionOrder {self.order_no} - {self.status}>"


class ProductionOrderItem(Base):
    """生产工单物料明细（配方/BOM）"""
    __tablename__ = "production_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)  # 物料
    quantity = Column(Numeric(12, 2), nullable=False)  # 需要数量
    consumed_qty = Column(Numeric(12, 2), default=0)  # 已消耗数量

    # Relationships
    order = relationship("ProductionOrder", back_populates="items")
    material = relationship("Material")

    def __repr__(self):
        return f"<ProductionOrderItem order={self.order_id} material={self.material_id}>"


class ProductionRecord(Base):
    """生产报工记录"""
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("production_orders.id"), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)  # 报工数量
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 操作工人
    remark = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("ProductionOrder")
    worker = relationship("User")

    def __repr__(self):
        return f"<ProductionRecord order={self.order_id} qty={self.quantity}>"


class BOMStatus(str, enum.Enum):
    """BOM状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class BOM(Base):
    """BOM配方主表"""
    __tablename__ = "boms"

    id = Column(Integer, primary_key=True, index=True)
    bom_no = Column(String(50), unique=True, index=True, nullable=False)  # BOM编号
    product_id = Column(Integer, ForeignKey("materials.id"), nullable=False)  # 产品
    version = Column(String(20), nullable=False, default="v1")  # 版本
    status = Column(SQLEnum(BOMStatus), default=BOMStatus.DRAFT)
    effective_date = Column(DateTime, nullable=True)  # 生效日期
    remark = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Material")
    items = relationship("BOMItem", back_populates="bom", cascade="all, delete-orphan")
    creator = relationship("User")

    def __repr__(self):
        return f"<BOM {self.bom_no} - {self.version}>"


class BOMItem(Base):
    """BOM配方明细"""
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("boms.id"), nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)  # 物料
    quantity = Column(Numeric(12, 4), nullable=False)  # 用量
    scrap_rate = Column(Numeric(5, 2), default=0)  # 损耗率%

    # Relationships
    bom = relationship("BOM", back_populates="items")
    material = relationship("Material")

    def __repr__(self):
        return f"<BOMItem bom={self.bom_id} material={self.material_id}>"


class ProcessRouteStatus(str, enum.Enum):
    """工艺路线状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    OBSOLETE = "obsolete"


class ProcessRoute(Base):
    """工艺路线"""
    __tablename__ = "process_routes"

    id = Column(Integer, primary_key=True, index=True)
    route_no = Column(String(50), unique=True, index=True, nullable=False)  # 路线编号
    product_id = Column(Integer, ForeignKey("materials.id"), nullable=False)  # 产品
    version = Column(String(20), nullable=False, default="v1")  # 版本
    status = Column(SQLEnum(ProcessRouteStatus), default=ProcessRouteStatus.DRAFT)
    remark = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Material")
    steps = relationship("ProcessStep", back_populates="route", cascade="all, delete-orphan")
    creator = relationship("User")

    def __repr__(self):
        return f"<ProcessRoute {self.route_no} - {self.version}>"


class ProcessStep(Base):
    """工序步骤"""
    __tablename__ = "process_steps"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("process_routes.id"), nullable=False)
    step_no = Column(Integer, nullable=False)  # 工序序号
    step_name = Column(String(100), nullable=False)  # 工序名称
    station_id = Column(Integer, ForeignKey("materials.id"), nullable=True)  # 工站/设备
    standard_time = Column(Numeric(10, 2), nullable=True)  # 标准工时(分钟)
    remark = Column(Text, nullable=True)

    # Relationships
    route = relationship("ProcessRoute", back_populates="steps")
    station = relationship("Material")

    def __repr__(self):
        return f"<ProcessStep {self.step_no} - {self.step_name}>"