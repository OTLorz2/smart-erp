"""Data validation utilities"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator
from datetime import datetime


class MaterialValidator:
    """Validator for material data"""

    @staticmethod
    def validate_code(code: str) -> bool:
        """Validate material code format"""
        if not code or len(code) < 3:
            return False
        return True

    @staticmethod
    def validate_unit(unit: str) -> bool:
        """Validate unit of measurement"""
        valid_units = ['个', '件', '台', '套', '米', 'cm', 'mm', 'kg', '吨', '升', 'ml', '盒', '包', '箱']
        return unit in valid_units


class CustomerValidator:
    """Validator for customer data"""

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number"""
        import re
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone)) if phone else True

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) if email else True


class OrderValidator:
    """Validator for order data"""

    @staticmethod
    def validate_quantity(quantity: float) -> bool:
        """Validate quantity is positive"""
        return quantity > 0

    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price is non-negative"""
        return price >= 0


class ValidationResult(BaseModel):
    """Validation result"""
    valid: bool
    errors: List[str] = []


def validate_material_import(data: List[Dict[str, Any]]) -> ValidationResult:
    """Validate material import data"""
    errors = []

    for idx, row in enumerate(data, start=1):
        code = row.get("物料编码", "")
        name = row.get("物料名称", "")
        unit = row.get("单位", "")

        if not code:
            errors.append(f"Row {idx}: 物料编码不能为空")
        elif len(code) < 3:
            errors.append(f"Row {idx}: 物料编码长度不能少于3位")

        if not name:
            errors.append(f"Row {idx}: 物料名称不能为空")

        if unit and not MaterialValidator.validate_unit(unit):
            errors.append(f"Row {idx}: 单位 '{unit}' 不在允许列表中")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )


def validate_customer_import(data: List[Dict[str, Any]]) -> ValidationResult:
    """Validate customer import data"""
    errors = []

    for idx, row in enumerate(data, start=1):
        name = row.get("客户名称", "")
        phone = row.get("联系电话", "")
        email = row.get("邮箱", "")

        if not name:
            errors.append(f"Row {idx}: 客户名称不能为空")

        if phone and not CustomerValidator.validate_phone(phone):
            errors.append(f"Row {idx}: 联系电话格式不正确")

        if email and not CustomerValidator.validate_email(email):
            errors.append(f"Row {idx}: 邮箱格式不正确")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )


def validate_supplier_import(data: List[Dict[str, Any]]) -> ValidationResult:
    """Validate supplier import data"""
    errors = []

    for idx, row in enumerate(data, start=1):
        name = row.get("供应商名称", "")
        phone = row.get("联系电话", "")
        email = row.get("邮箱", "")

        if not name:
            errors.append(f"Row {idx}: 供应商名称不能为空")

        if phone and not CustomerValidator.validate_phone(phone):
            errors.append(f"Row {idx}: 联系电话格式不正确")

        if email and not CustomerValidator.validate_email(email):
            errors.append(f"Row {idx}: 邮箱格式不正确")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors
    )