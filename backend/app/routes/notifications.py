from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Subscription
from pydantic import BaseModel, EmailStr
from typing import Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class SubscribeRequest(BaseModel):
    email: Optional[EmailStr] = None
    push_subscription: Optional[dict] = None

class UnsubscribeRequest(BaseModel):
    email: Optional[EmailStr] = None
    subscription_id: Optional[int] = None

@router.post("/subscribe")
def subscribe(request: SubscribeRequest, db: Session = Depends(get_db)):
    """
    Subscribe to notifications.
    Can provide email, push subscription, or both.
    """
    if not request.email and not request.push_subscription:
        raise HTTPException(status_code=400, detail="Must provide email or push subscription")
    
    try:
        # Check if subscription already exists for this email
        existing = None
        if request.email:
            existing = db.query(Subscription).filter(Subscription.email == request.email).first()
        
        if existing:
            # Update existing subscription
            if request.email:
                existing.email = request.email
            if request.push_subscription:
                existing.push_subscription = json.dumps(request.push_subscription)
            existing.is_active = True
            db.commit()
            
            return {
                "status": "success",
                "message": "Subscription updated",
                "subscription_id": existing.id
            }
        else:
            # Create new subscription
            new_sub = Subscription(
                email=request.email,
                push_subscription=json.dumps(request.push_subscription) if request.push_subscription else None,
                is_active=True
            )
            db.add(new_sub)
            db.commit()
            db.refresh(new_sub)
            
            return {
                "status": "success",
                "message": "Subscription created",
                "subscription_id": new_sub.id
            }
    
    except Exception as e:
        logger.error(f"Subscription failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Subscription failed: {str(e)}")

@router.post("/unsubscribe")
def unsubscribe(request: UnsubscribeRequest, db: Session = Depends(get_db)):
    """
    Unsubscribe from notifications.
    Can use email or subscription_id.
    """
    if not request.email and not request.subscription_id:
        raise HTTPException(status_code=400, detail="Must provide email or subscription_id")
    
    try:
        subscription = None
        
        if request.subscription_id:
            subscription = db.query(Subscription).filter(Subscription.id == request.subscription_id).first()
        elif request.email:
            subscription = db.query(Subscription).filter(Subscription.email == request.email).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        subscription.is_active = False
        db.commit()
        
        return {
            "status": "success",
            "message": "Unsubscribed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unsubscribe failed: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unsubscribe failed: {str(e)}")

@router.get("/subscriptions")
def get_subscriptions(db: Session = Depends(get_db)):
    """
    Get all active subscriptions (admin endpoint - should be protected in production).
    """
    subscriptions = db.query(Subscription).filter(Subscription.is_active == True).all()
    
    results = []
    for sub in subscriptions:
        results.append({
            "id": sub.id,
            "email": sub.email,
            "has_push": bool(sub.push_subscription),
            "created_at": sub.created_at.isoformat() if sub.created_at else None
        })
    
    return {
        "count": len(results),
        "data": results
    }

@router.post("/test-notification")
def send_test_notification(
    doctor_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Send a test notification to verify FCM is working.
    
    If doctor_name is provided, sends to subscribers of that doctor.
    If not provided, sends to ALL registered devices.
    
    Example:
        POST /test-notification?doctor_name=Dr.%20Smith
        POST /test-notification (sends to all)
    """
    try:
        from app.database import FCMToken, DoctorSubscription
        from app.services.fcm_rest import send_fcm_multicast_rest
        
        fcm_tokens = []
        
        if doctor_name:
            # Send to specific doctor's subscribers
            doctor_subs = db.query(DoctorSubscription).filter(
                DoctorSubscription.doctor_name == doctor_name
            ).all()
            
            if not doctor_subs:
                return {
                    "status": "warning",
                    "message": f"No subscribers found for doctor: {doctor_name}",
                    "doctor_name": doctor_name,
                    "subscribers": 0
                }
            
            device_ids = [sub.device_id for sub in doctor_subs]
            fcm_tokens_objs = db.query(FCMToken).filter(
                FCMToken.device_id.in_(device_ids)
            ).all()
            
            fcm_tokens = [token.fcm_token for token in fcm_tokens_objs]
            target_desc = f"subscribers of {doctor_name}"
        else:
            # Send to ALL registered devices
            fcm_tokens_objs = db.query(FCMToken).all()
            fcm_tokens = [token.fcm_token for token in fcm_tokens_objs]
            target_desc = "all registered devices"
        
        if not fcm_tokens:
            return {
                "status": "warning",
                "message": f"No FCM tokens found for {target_desc}",
                "tokens_found": 0
            }
        
        # Send test notification
        title = "🧪 Test Notification"
        body = f"This is a test notification for {target_desc}. If you see this, notifications are working! ✅"
        data = {
            "type": "test",
            "timestamp": str(datetime.now()),
            "target": target_desc
        }
        
        result = send_fcm_multicast_rest(fcm_tokens, title, body, data)
        
        logger.info(f"Test notification sent: {result['success']} success, {result['failure']} failed")
        
        return {
            "status": "success",
            "message": f"Test notification sent to {target_desc}",
            "tokens_sent": len(fcm_tokens),
            "success_count": result['success'],
            "failure_count": result['failure'],
            "doctor_name": doctor_name if doctor_name else "N/A"
        }
        
    except Exception as e:
        logger.error(f"Test notification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send test notification: {str(e)}")
