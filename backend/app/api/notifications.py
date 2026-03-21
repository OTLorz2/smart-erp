from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_active_user
from ..models.user import User
from ..models.notification import Notification, NotificationType

router = APIRouter(prefix="/notifications", tags=["通知中心"])


@router.get("")
def list_notifications(
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取通知列表"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取未读通知数量"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    return {"unread_count": count}


@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记通知为已读"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    notification.is_read = True
    db.commit()
    return notification


@router.put("/read-all")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记所有通知为已读"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"success": True}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除通知"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")

    db.delete(notification)
    db.commit()
    return {"success": True}


# Helper function to create notifications (can be called from other modules)
def create_notification(
    db: Session,
    user_id: int,
    title: str,
    content: str = None,
    notification_type: NotificationType = NotificationType.INFO
):
    """创建通知"""
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=notification_type
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification