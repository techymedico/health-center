from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, FCMToken, DoctorSubscription
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class RegisterTokenRequest(BaseModel):
    device_id: str
    fcm_token: str

class SubscribeDoctorRequest(BaseModel):
    device_id: str
    doctor_name: str

class UnsubscribeDoctorRequest(BaseModel):
    device_id: str
    doctor_name: str

@router.post("/register-fcm-token")
def register_fcm_token(request: RegisterTokenRequest, db: Session = Depends(get_db)):
    """
    Register or update FCM token for a device.
    """
    try:
        # Check if device already exists
        existing = db.query(FCMToken).filter(FCMToken.device_id == request.device_id).first()
        
        if existing:
            # Update existing token
            existing.fcm_token = request.fcm_token
            db.commit()
            
            return {
                "status": "success",
                "message": "FCM token updated",
                "device_id": request.device_id
            }
        else:
            # Create new token
            new_token = FCMToken(
                device_id=request.device_id,
                fcm_token=request.fcm_token
            )
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            
            return {
                "status": "success",
                "message": "FCM token registered",
                "device_id": request.device_id
            }
    
    except Exception as e:
        logger.error(f"Failed to register FCM token: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/subscribe-doctor")
def subscribe_doctor(request: SubscribeDoctorRequest, db: Session = Depends(get_db)):
    """
    Subscribe a device to notifications for a specific doctor.
    """
    try:
        # Check if subscription already exists
        existing = db.query(DoctorSubscription).filter(
            DoctorSubscription.device_id == request.device_id,
            DoctorSubscription.doctor_name == request.doctor_name
        ).first()
        
        if existing:
            return {
                "status": "success",
                "message": "Already subscribed to this doctor"
            }
        
        # Create new subscription
        subscription = DoctorSubscription(
            device_id=request.device_id,
            doctor_name=request.doctor_name
        )
        db.add(subscription)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Subscribed to {request.doctor_name}"
        }
    
    except Exception as e:
        logger.error(f"Failed to subscribe: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Subscription failed: {str(e)}")

@router.post("/unsubscribe-doctor")
def unsubscribe_doctor(request: UnsubscribeDoctorRequest, db: Session = Depends(get_db)):
    """
    Unsubscribe a device from notifications for a specific doctor.
    """
    try:
        subscription = db.query(DoctorSubscription).filter(
            DoctorSubscription.device_id == request.device_id,
            DoctorSubscription.doctor_name == request.doctor_name
        ).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        db.delete(subscription)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Unsubscribed from {request.doctor_name}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unsubscribe: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unsubscribe failed: {str(e)}")

@router.get("/subscriptions/{device_id}")
def get_subscriptions(device_id: str, db: Session = Depends(get_db)):
    """
    Get all doctor subscriptions for a device.
    """
    subscriptions = db.query(DoctorSubscription).filter(
        DoctorSubscription.device_id == device_id
    ).all()
    
    doctor_names = [sub.doctor_name for sub in subscriptions]
    
    return {
        "device_id": device_id,
        "subscribed_doctors": doctor_names,
        "count": len(doctor_names)
    }
