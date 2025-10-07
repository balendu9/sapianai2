from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.models.participant import QuestParticipant
from app.models.admin import AdminUser
from app.schemas.notification import (
    NotificationCreate, NotificationResponse, NotificationMarkRead,
    BulkNotificationCreate, AdminSpecialNotification
)
from app.routers.auth import get_current_admin

router = APIRouter()

@router.get("/{user_id}/notifications", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's notifications"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(desc(Notification.created_at)).limit(limit).all()
    
    return [NotificationResponse(**notification.to_dict()) for notification in notifications]

@router.post("/{user_id}/notifications", response_model=NotificationResponse)
async def create_notification(
    user_id: str,
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification for a user"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create notification
    new_notification = Notification(
        user_id=user_id,
        title=notification.title,
        message=notification.message,
        notification_type=notification.notification_type,
        quest_id=notification.quest_id,
        metadata=notification.metadata or {}
    )
    
    try:
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        
        return NotificationResponse(**new_notification.to_dict())
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create notification: {str(e)}")

@router.post("/{user_id}/notifications/mark-read")
async def mark_notifications_read(
    user_id: str,
    mark_read: NotificationMarkRead,
    db: Session = Depends(get_db)
):
    """Mark notifications as read"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update notifications
    updated_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.notification_id.in_(mark_read.notification_ids)
    ).update({
        "is_read": True,
        "read_at": datetime.now()
    })
    
    db.commit()
    
    return {
        "message": f"Marked {updated_count} notifications as read",
        "updated_count": updated_count
    }

@router.get("/{user_id}/notifications/unread-count")
async def get_unread_count(user_id: str, db: Session = Depends(get_db)):
    """Get count of unread notifications for a user"""
    # Check if user exists
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    unread_count = db.query(func.count(Notification.notification_id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).scalar()
    
    return {"unread_count": unread_count}

# Admin endpoints for sending notifications

@router.post("/admin/send-special-notification")
async def send_special_notification(
    notification_data: AdminSpecialNotification,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send special notification to users (admin only)"""
    
    notifications_created = 0
    
    try:
        if notification_data.target_type == "all_users":
            # Get all users
            users = db.query(User).all()
            user_ids = [user.user_id for user in users]
            
        elif notification_data.target_type == "specific_users":
            if not notification_data.user_ids:
                raise HTTPException(status_code=400, detail="user_ids required for specific_users target")
            user_ids = notification_data.user_ids
            
        elif notification_data.target_type == "quest_participants":
            if not notification_data.quest_id:
                raise HTTPException(status_code=400, detail="quest_id required for quest_participants target")
            
            # Get all participants in the quest
            participants = db.query(QuestParticipant).filter(
                QuestParticipant.quest_id == notification_data.quest_id
            ).all()
            user_ids = [participant.user_id for participant in participants]
            
        else:
            raise HTTPException(status_code=400, detail="Invalid target_type")
        
        # Create notifications for all target users
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                title=notification_data.title,
                message=notification_data.message,
                notification_type=notification_data.notification_type,
                quest_id=notification_data.quest_id,
                metadata=notification_data.metadata or {}
            )
            db.add(notification)
            notifications_created += 1
        
        db.commit()
        
        return {
            "message": f"Sent {notifications_created} notifications successfully",
            "notifications_sent": notifications_created,
            "target_users": len(user_ids)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send notifications: {str(e)}")

@router.post("/admin/send-bulk-notification")
async def send_bulk_notification(
    notification_data: BulkNotificationCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send notification to multiple specific users (admin only)"""
    
    notifications_created = 0
    
    try:
        for user_id in notification_data.user_ids:
            # Check if user exists
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                continue  # Skip non-existent users
            
            notification = Notification(
                user_id=user_id,
                title=notification_data.title,
                message=notification_data.message,
                notification_type=notification_data.notification_type,
                quest_id=notification_data.quest_id,
                metadata=notification_data.metadata or {}
            )
            db.add(notification)
            notifications_created += 1
        
        db.commit()
        
        return {
            "message": f"Sent {notifications_created} notifications successfully",
            "notifications_sent": notifications_created,
            "requested_users": len(notification_data.user_ids)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send bulk notifications: {str(e)}")

# Helper function to create quest-related notifications
async def create_quest_notification(
    db: Session,
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    quest_id: str = None,
    metadata: dict = None
):
    """Helper function to create quest-related notifications"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        quest_id=quest_id,
        metadata=metadata or {}
    )
    
    db.add(notification)
    return notification
