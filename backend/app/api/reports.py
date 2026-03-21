from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from io import BytesIO

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.base_data import Material, Customer, Supplier, Warehouse
from ..models.inventory import WarehouseStock, InventoryRecord, InventoryRecordType
from ..models.sales import SalesOrder, SalesOrderItem, SalesOrderStatus
from ..models.purchase import PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
from ..models.production import ProductionOrder, ProductionOrderStatus
from ..models.quality import QCRecord, QCRecordStatus
from ..utils.export import ExportHelper, ColumnConfig
from ..utils.import_excel import ExcelImporter, ImportSchema, ValidationRule

router = APIRouter(prefix="/reports", tags=["报表中心"])


# ============= Phase 1: Export/Import APIs =============

@router.post("/export")
def export_data(
    data_type: str,  # materials, customers, suppliers, inventory, sales, purchase
    format: str = "excel",  # excel, csv
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """通用导出接口"""
    columns = []
    data = []

    if data_type == "materials":
        columns = [
            ColumnConfig(key="code", title="物料编码", width=15),
            ColumnConfig(key="name", title="物料名称", width=20),
            ColumnConfig(key="category", title="分类", width=10),
            ColumnConfig(key="specification", title="规格型号", width=20),
            ColumnConfig(key="unit", title="单位", width=8),
            ColumnConfig(key="safety_stock", title="安全库存", width=12),
            ColumnConfig(key="price", title="参考单价", width=12, format="currency"),
        ]
        materials = db.query(Material).filter(Material.is_active == True).all()
        data = [{"code": m.code, "name": m.name, "category": m.category.value,
                 "specification": m.specification or "", "unit": m.unit,
                 "safety_stock": float(m.safety_stock or 0), "price": float(m.price or 0)} for m in materials]

    elif data_type == "customers":
        columns = [
            ColumnConfig(key="code", title="客户编码", width=15),
            ColumnConfig(key="name", title="客户名称", width=20),
            ColumnConfig(key="contact", title="联系人", width=12),
            ColumnConfig(key="phone", title="联系电话", width=15),
            ColumnConfig(key="email", title="邮箱", width=20),
            ColumnConfig(key="address", title="地址", width=25),
        ]
        customers = db.query(Customer).filter(Customer.is_active == True).all()
        data = [{"code": c.code, "name": c.name, "contact": c.contact or "",
                 "phone": c.phone or "", "email": c.email or "", "address": c.address or ""} for c in customers]

    elif data_type == "suppliers":
        columns = [
            ColumnConfig(key="code", title="供应商编码", width=15),
            ColumnConfig(key="name", title="供应商名称", width=20),
            ColumnConfig(key="contact", title="联系人", width=12),
            ColumnConfig(key="phone", title="联系电话", width=15),
            ColumnConfig(key="email", title="邮箱", width=20),
            ColumnConfig(key="address", title="地址", width=25),
        ]
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
        data = [{"code": s.code, "name": s.name, "contact": s.contact or "",
                 "phone": s.phone or "", "email": s.email or "", "address": s.address or ""} for s in suppliers]

    elif data_type == "inventory":
        columns = [
            ColumnConfig(key="material_code", title="物料编码", width=15),
            ColumnConfig(key="material_name", title="物料名称", width=20),
            ColumnConfig(key="warehouse_name", title="仓库", width=15),
            ColumnConfig(key="quantity", title="库存数量", width=12),
            ColumnConfig(key="price", title="单价", width=12, format="currency"),
            ColumnConfig(key="total_price", title="总金额", width=15, format="currency"),
        ]
        stocks = db.query(WarehouseStock).join(Material, WarehouseStock.material_id == Material.id).join(Warehouse).all()
        data = []
        for stock in stocks:
            total_price = float(stock.quantity or 0) * float(stock.material.price or 0)
            data.append({
                "material_code": stock.material.code,
                "material_name": stock.material.name,
                "warehouse_name": stock.warehouse.name if stock.warehouse else "",
                "quantity": float(stock.quantity or 0),
                "price": float(stock.material.price or 0),
                "total_price": total_price
            })

    elif data_type == "sales":
        columns = [
            ColumnConfig(key="order_no", title="订单编号", width=18),
            ColumnConfig(key="customer_name", title="客户", width=20),
            ColumnConfig(key="total_amount", title="金额", width=15, format="currency"),
            ColumnConfig(key="status", title="状态", width=12),
            ColumnConfig(key="created_at", title="创建时间", width=18),
        ]
        orders = db.query(SalesOrder).join(Customer).order_by(SalesOrder.created_at.desc()).limit(100).all()
        data = [{"order_no": o.order_no, "customer_name": o.customer.name,
                 "total_amount": float(o.total_amount or 0), "status": o.status.value,
                 "created_at": o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else ""} for o in orders]

    elif data_type == "purchase":
        columns = [
            ColumnConfig(key="order_no", title="订单编号", width=18),
            ColumnConfig(key="supplier_name", title="供应商", width=20),
            ColumnConfig(key="total_amount", title="金额", width=15, format="currency"),
            ColumnConfig(key="status", title="状态", width=12),
            ColumnConfig(key="created_at", title="创建时间", width=18),
        ]
        orders = db.query(PurchaseOrder).join(Supplier).order_by(PurchaseOrder.created_at.desc()).limit(100).all()
        data = [{"order_no": o.order_no, "supplier_name": o.supplier.name,
                 "total_amount": float(o.total_amount or 0), "status": o.status.value,
                 "created_at": o.created_at.strftime("%Y-%m-%d %H:%M") if o.created_at else ""} for o in orders]

    else:
        raise HTTPException(status_code=400, detail=f"不支持的数据类型: {data_type}")

    if format == "excel":
        content = ExportHelper.to_excel(data, columns, data_type)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={data_type}_{datetime.now().strftime('%Y%m%d')}.xlsx"}
        )
    else:
        content = ExportHelper.to_csv(data, columns)
        return StreamingResponse(
            BytesIO(content.encode('utf-8-sig')),
            media_type="text/csv; charset=utf-8-sig",
            headers={"Content-Disposition": f"attachment; filename={data_type}_{datetime.now().strftime('%Y%m%d')}.csv"}
        )


@router.get("/export/template/{data_type}")
def download_template(
    data_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """下载导入模板"""
    columns = []

    if data_type == "materials":
        columns = [
            ColumnConfig(key="code", title="物料编码", width=15),
            ColumnConfig(key="name", title="物料名称", width=20),
            ColumnConfig(key="category", title="分类", width=10),
            ColumnConfig(key="specification", title="规格型号", width=20),
            ColumnConfig(key="unit", title="单位", width=8),
            ColumnConfig(key="safety_stock", title="安全库存", width=12),
            ColumnConfig(key="price", title="参考单价", width=12),
            ColumnConfig(key="description", title="描述", width=30),
        ]
    elif data_type == "customers":
        columns = [
            ColumnConfig(key="code", title="客户编码", width=15),
            ColumnConfig(key="name", title="客户名称", width=20),
            ColumnConfig(key="contact", title="联系人", width=12),
            ColumnConfig(key="phone", title="联系电话", width=15),
            ColumnConfig(key="email", title="邮箱", width=20),
            ColumnConfig(key="address", title="地址", width=25),
        ]
    elif data_type == "suppliers":
        columns = [
            ColumnConfig(key="code", title="供应商编码", width=15),
            ColumnConfig(key="name", title="供应商名称", width=20),
            ColumnConfig(key="contact", title="联系人", width=12),
            ColumnConfig(key="phone", title="联系电话", width=15),
            ColumnConfig(key="email", title="邮箱", width=20),
            ColumnConfig(key="address", title="地址", width=25),
        ]
    else:
        raise HTTPException(status_code=400, detail=f"不支持的数据类型: {data_type}")

    content = ExportHelper.generate_template(columns)
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={data_type}_template.xlsx"}
    )


@router.post("/import/validate")
async def validate_import(
    file: bytes,
    data_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """预验证导入数据"""
    importer = ExcelImporter(file)
    schema = ImportSchema(columns=[], required_columns=[])
    result = importer.parse(schema)

    if not result.success:
        return {"valid": False, "errors": result.errors}

    return {
        "valid": True,
        "total_rows": result.total_rows,
        "preview": [row.data for row in result.rows[:5]]
    }


# ============= Phase 2: Dashboard APIs =============

@router.get("/dashboard/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """经营概览统计"""
    today = datetime.now().date()
    month_start = today.replace(day=1)

    # 今日销售
    today_sales = db.query(func.sum(SalesOrder.total_amount)).filter(
        func.date(SalesOrder.created_at) == today,
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.SHIPPED])
    ).scalar() or 0

    # 本月销售
    month_sales = db.query(func.sum(SalesOrder.total_amount)).filter(
        SalesOrder.created_at >= month_start,
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.SHIPPED])
    ).scalar() or 0

    # 待处理订单
    pending_orders = db.query(SalesOrder).filter(
        SalesOrder.status == SalesOrderStatus.PENDING
    ).count()

    # 库存价值
    total_inventory_value = db.query(
        func.sum(WarehouseStock.quantity * Material.price)
    ).join(Material).scalar() or 0

    # 库存预警数量
    low_stock_items = db.query(WarehouseStock).join(Material).filter(
        WarehouseStock.quantity <= Material.safety_stock
    ).count()

    # 采购待收货
    pending_purchases = db.query(PurchaseOrder).filter(
        PurchaseOrder.status == PurchaseOrderStatus.CONFIRMED
    ).count()

    return {
        "today_sales": float(today_sales),
        "month_sales": float(month_sales),
        "pending_orders": pending_orders,
        "inventory_value": float(total_inventory_value),
        "low_stock_items": low_stock_items,
        "pending_purchases": pending_purchases,
    }


@router.get("/dashboard/trends")
def get_dashboard_trends(
    days: int = Query(default=7, ge=7, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """趋势数据"""
    start_date = datetime.now() - timedelta(days=days)

    # 销售趋势
    sales_data = db.query(
        func.date(SalesOrder.created_at).label("date"),
        func.sum(SalesOrder.total_amount).label("amount")
    ).filter(
        SalesOrder.created_at >= start_date,
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.SHIPPED])
    ).group_by(func.date(SalesOrder.created_at)).all()

    # 采购趋势
    purchase_data = db.query(
        func.date(PurchaseOrder.created_at).label("date"),
        func.sum(PurchaseOrder.total_amount).label("amount")
    ).filter(
        PurchaseOrder.created_at >= start_date,
        PurchaseOrder.status.in_([PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.RECEIVED])
    ).group_by(func.date(PurchaseOrder.created_at)).all()

    return {
        "sales": [{"date": str(s.date), "amount": float(s.amount)} for s in sales_data],
        "purchases": [{"date": str(p.date), "amount": float(p.amount)} for p in purchase_data],
    }


@router.get("/dashboard/alerts")
def get_dashboard_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """预警提醒"""
    alerts = []

    # 库存预警
    low_stock = db.query(WarehouseStock, Material).join(
        Material, WarehouseStock.material_id == Material.id
    ).filter(
        WarehouseStock.quantity <= Material.safety_stock
    ).limit(10).all()

    for stock, material in low_stock:
        alerts.append({
            "type": "inventory",
            "level": "warning",
            "title": "库存不足",
            "content": f"物料 {material.name} 库存不足，当前: {stock.quantity}, 安全库存: {material.safety_stock}",
            "material_id": material.id
        })

    # 待处理销售订单
    pending_orders = db.query(SalesOrder).filter(
        SalesOrder.status == SalesOrderStatus.PENDING
    ).limit(5).all()

    for order in pending_orders:
        alerts.append({
            "type": "sales",
            "level": "info",
            "title": "待处理订单",
            "content": f"订单 {order.order_no} 待确认",
            "order_id": order.id
        })

    # 待生产
    pending_production = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionOrderStatus.PENDING
    ).limit(5).all()

    for order in pending_production:
        alerts.append({
            "type": "production",
            "level": "info",
            "title": "待生产",
            "content": f"生产单 {order.order_no} 待排产",
            "order_id": order.id
        })

    return alerts


# ============= Phase 3: Business Reports APIs =============

# Inventory Reports
@router.get("/inventory/summary")
def get_inventory_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """库存汇总"""
    total_items = db.query(Material).filter(Material.is_active == True).count()
    total_stocks = db.query(WarehouseStock).filter(WarehouseStock.quantity > 0).count()
    total_value = db.query(
        func.sum(WarehouseStock.quantity * Material.price)
    ).join(Material).scalar() or 0

    return {
        "total_items": total_items,
        "total_stocks": total_stocks,
        "total_value": float(total_value)
    }


@router.get("/inventory/alerts")
def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """库存预警"""
    alerts = db.query(WarehouseStock, Material).join(
        Material, WarehouseStock.material_id == Material.id
    ).filter(
        WarehouseStock.quantity <= Material.safety_stock
    ).all()

    return [{
        "material_code": m.code,
        "material_name": m.name,
        "current_stock": float(s.quantity),
        "safety_stock": float(m.safety_stock),
        "warehouse": s.warehouse.name if s.warehouse else ""
    } for s, m in alerts]


# Sales Reports
@router.get("/sales/summary")
def get_sales_summary(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """销售汇总"""
    query = db.query(SalesOrder).filter(
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.SHIPPED])
    )

    if start_date:
        query = query.filter(func.date(SalesOrder.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(SalesOrder.created_at) <= end_date)

    orders = query.all()
    total_amount = sum(float(o.total_amount or 0) for o in orders)
    order_count = len(orders)

    return {
        "total_amount": total_amount,
        "order_count": order_count,
        "avg_amount": total_amount / order_count if order_count > 0 else 0
    }


@router.get("/sales/by-customer")
def get_sales_by_customer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """按客户统计销售"""
    results = db.query(
        Customer.name,
        func.sum(SalesOrder.total_amount).label("total")
    ).join(SalesOrder).filter(
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.SHIPPED])
    ).group_by(Customer.id, Customer.name).all()

    return [{"customer_name": r.name, "total_amount": float(r.total)} for r in results]


@router.get("/sales/by-product")
def get_sales_by_product(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """按产品统计销售"""
    results = db.query(
        Material.name,
        func.sum(SalesOrderItem.quantity).label("quantity"),
        func.sum(SalesOrderItem.total_price).label("amount")
    ).join(SalesOrderItem, Material.id == SalesOrderItem.material_id).join(
        SalesOrder, SalesOrderItem.order_id == SalesOrder.id
    ).filter(
        SalesOrder.status.in_([SalesOrderStatus.CONFIRMED, SalesOrderStatus.SHIPPED])
    ).group_by(Material.id, Material.name).all()

    return [{
        "material_name": r.name,
        "quantity": float(r.quantity),
        "amount": float(r.amount)
    } for r in results]


# Purchase Reports
@router.get("/purchase/summary")
def get_purchase_summary(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """采购汇总"""
    query = db.query(PurchaseOrder).filter(
        PurchaseOrder.status.in_([PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.RECEIVED])
    )

    if start_date:
        query = query.filter(func.date(PurchaseOrder.created_at) >= start_date)
    if end_date:
        query = query.filter(func.date(PurchaseOrder.created_at) <= end_date)

    orders = query.all()
    total_amount = sum(float(o.total_amount or 0) for o in orders)
    order_count = len(orders)

    return {
        "total_amount": total_amount,
        "order_count": order_count,
        "avg_amount": total_amount / order_count if order_count > 0 else 0
    }


@router.get("/purchase/by-supplier")
def get_purchase_by_supplier(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """按供应商统计采购"""
    results = db.query(
        Supplier.name,
        func.sum(PurchaseOrder.total_amount).label("total")
    ).join(PurchaseOrder).filter(
        PurchaseOrder.status.in_([PurchaseOrderStatus.CONFIRMED, PurchaseOrderStatus.RECEIVED])
    ).group_by(Supplier.id, Supplier.name).all()

    return [{"supplier_name": r.name, "total_amount": float(r.total)} for r in results]


# Production Reports
@router.get("/production/summary")
def get_production_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """生产汇总"""
    total_orders = db.query(ProductionOrder).count()
    completed = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionOrderStatus.COMPLETED
    ).count()
    in_progress = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionOrderStatus.IN_PROGRESS
    ).count()

    return {
        "total_orders": total_orders,
        "completed": completed,
        "in_progress": in_progress,
        "pending": total_orders - completed - in_progress
    }


@router.get("/production/efficiency")
def get_production_efficiency(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """生产效率"""
    completed = db.query(ProductionOrder).filter(
        ProductionOrder.status == ProductionOrderStatus.COMPLETED
    ).all()

    efficiency_data = []
    for order in completed:
        if order.planned_quantity and order.planned_quantity > 0:
            efficiency = float(order.output_quantity or 0) / float(order.planned_quantity) * 100
            efficiency_data.append({
                "order_no": order.order_no,
                "efficiency": round(efficiency, 2)
            })

    return efficiency_data[:20]


# Quality Reports
@router.get("/quality/summary")
def get_quality_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """质量汇总"""
    total = db.query(QCRecord).count()
    passed = db.query(QCRecord).filter(QCRecord.status == QCRecordStatus.PASSED).count()
    failed = db.query(QCRecord).filter(QCRecord.status == QCRecordStatus.FAILED).count()

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / total * 100, 2) if total > 0 else 0
    }


@router.get("/quality/defects")
def get_quality_defects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """不良统计"""
    failed_records = db.query(QCRecord).filter(
        QCRecord.status == QCRecordStatus.FAILED
    ).all()

    return [{
        "material_name": r.material.name if r.material else "",
        "defect_type": r.defect_type or "",
        "defect_count": r.defect_count,
        "record_no": r.record_no,
        "created_at": r.created_at.strftime("%Y-%m-%d") if r.created_at else ""
    } for r in failed_records]