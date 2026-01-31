from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, Subscription
from pydantic import BaseModel, EmailStr
from typing import Optional
import json
import logging

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
