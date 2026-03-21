from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base


class MaterialCategory(str, enum.Enum):
    """物料分类"""
    RAW = "raw"           # 原材料
    SEMI = "semi"         # 半成品
    FINISHED = "finished" # 成品
    CONSUMABLE = "consumable"  # 消耗品


class Material(Base):
    """物料主数据"""
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 物料编码
    name = Column(String(100), nullable=False)  # 物料名称
    category = Column(SQLEnum(MaterialCategory), default=MaterialCategory.RAW)  # 分类
    specification = Column(String(200), nullable=True)  # 规格型号
    unit = Column(String(20), nullable=False)  # 单位
    safety_stock = Column(Numeric(12, 2), default=0)  # 安全库存
    min_stock = Column(Numeric(12, 2), default=0)  # 最小库存
    price = Column(Numeric(12, 2), default=0)  # 参考单价
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    inventory_records = relationship("InventoryRecord", back_populates="material")
    warehouse_stocks = relationship("WarehouseStock", back_populates="material")

    def __repr__(self):
        return f"<Material {self.code} - {self.name}>"


class Warehouse(Base):
    """仓库"""
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 仓库编码
    name = Column(String(100), nullable=False)  # 仓库名称
    address = Column(String(200), nullable=True)
    manager = Column(String(50), nullable=True)  # 仓库管理员
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # 默认仓库
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stocks = relationship("WarehouseStock", back_populates="warehouse")
    inventory_records = relationship("InventoryRecord", back_populates="warehouse")

    def __repr__(self):
        return f"<Warehouse {self.code} - {self.name}>"


class Supplier(Base):
    """供应商"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 供应商编码
    name = Column(String(100), nullable=False)  # 供应商名称
    contact = Column(String(50), nullable=True)  # 联系人
    phone = Column(String(20), nullable=True)  # 电话
    email = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier {self.code} - {self.name}>"


class Customer(Base):
    """客户"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # 客户编码
    name = Column(String(100), nullable=False)  # 客户名称
    contact = Column(String(50), nullable=True)  # 联系人
    phone = Column(String(20), nullable=True)  # 电话
    email = Column(String(100), nullable=True)
    address = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sales_orders = relationship("SalesOrder", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.code} - {self.name}>"