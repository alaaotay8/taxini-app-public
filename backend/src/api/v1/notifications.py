"""
Notifications API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, desc
from typing import List, Optional
from datetime import datetime

from src.models.notification import Notification
from src.models.user import User
from src.db.session import get_session
from src.schemas.auth import CurrentUser
from src.services.auth import AuthService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    unread_only: bool = False,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Get user notifications.
    
    Args:
        limit: Maximum number of notifications to return
        offset: Number of notifications to skip
        unread_only: If True, only return unread notifications
        session: Database session
        current_user: Authenticated user
    
    Returns:
        List of notifications with count
    """
    try:
        # Get user
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build query
        query = select(Notification).where(Notification.user_id == user.id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        # Order by created_at descending (newest first)
        query = query.order_by(desc(Notification.created_at))
        
        # Count total
        count_query = select(Notification).where(Notification.user_id == user.id)
        if unread_only:
            count_query = count_query.where(Notification.is_read == False)
        
        total = len(session.exec(count_query).all())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        notifications = session.exec(query).all()
        
        # Format notifications
        notifications_list = [
            {
                "id": str(n.id),
                "notification_type": n.notification_type,
                "title": n.title,
                "message": n.message,
                "data": n.data,
                "is_read": n.is_read,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifications
        ]
        
        return {
            "success": True,
            "notifications": notifications_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Mark a notification as read.
    
    Args:
        notification_id: Notification ID
        session: Database session
        current_user: Authenticated user
    
    Returns:
        Success confirmation
    """
    try:
        # Get user
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get notification
        notification = session.exec(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user.id
            )
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Mark as read
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        session.add(notification)
        session.commit()
        
        return {
            "success": True,
            "message": "Notification marked as read"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/mark-all-read")
async def mark_all_notifications_read(
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Mark all notifications as read for the current user.
    
    Args:
        session: Database session
        current_user: Authenticated user
    
    Returns:
        Count of marked notifications
    """
    try:
        # Get user
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all unread notifications
        notifications = session.exec(
            select(Notification).where(
                Notification.user_id == user.id,
                Notification.is_read == False
            )
        ).all()
        
        # Mark all as read
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            session.add(notification)
            count += 1
        
        session.commit()
        
        return {
            "success": True,
            "message": f"Marked {count} notifications as read",
            "count": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    session: Session = Depends(get_session),
    current_user: CurrentUser = Depends(AuthService.get_current_user_dependency)
) -> dict:
    """
    Delete a notification.
    
    Args:
        notification_id: Notification ID
        session: Database session
        current_user: Authenticated user
    
    Returns:
        Success confirmation
    """
    try:
        # Get user
        from src.core.settings import settings
        
        if settings.development_mode:
            user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
        else:
            user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get notification
        notification = session.exec(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user.id
            )
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        # Delete notification
        session.delete(notification)
        session.commit()
        
        return {
            "success": True,
            "message": "Notification deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
