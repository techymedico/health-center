import firebase_admin
from firebase_admin import credentials, messaging
from app.config import get_settings
import logging
import os

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize Firebase Admin SDK
_firebase_app = None

def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials."""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        if not settings.FIREBASE_CREDENTIALS_PATH:
            logger.warning("Firebase credentials path not set, FCM notifications disabled")
            return None
        
        if not os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            logger.warning(f"Firebase credentials file not found at {settings.FIREBASE_CREDENTIALS_PATH}")
            return None
        
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
        return _firebase_app
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        return None

def send_fcm_notification(token: str, title: str, body: str, data: dict = None):
    """
    Send FCM notification to a single device.
    
    Args:
        token: FCM device token
        title: Notification title
        body: Notification body
        data: Optional data payload
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        if _firebase_app is None:
            initialize_firebase()
        
        if _firebase_app is None:
            logger.warning("Firebase not initialized, skipping FCM notification")
            return False
        
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            token=token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='ic_notification',
                    color='#667eea',
                    sound='default'
                )
            )
        )
        
        response = messaging.send(message)
        logger.info(f"FCM notification sent successfully: {response}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send FCM notification: {str(e)}")
        return False

def send_fcm_multicast(tokens: list, title: str, body: str, data: dict = None):
    """
    Send FCM notification to multiple devices.
    
    Args:
        tokens: List of FCM device tokens
        title: Notification title
        body: Notification body
        data: Optional data payload
    
    Returns:
        dict: Success and failure counts
    """
    try:
        if _firebase_app is None:
            initialize_firebase()
        
        if _firebase_app is None:
            logger.warning("Firebase not initialized, skipping FCM notifications")
            return {"success": 0, "failure": len(tokens)}
        
        if not tokens:
            return {"success": 0, "failure": 0}
        
        # Send to max 500 tokens at once (FCM limit)
        batch_size = 500
        success_count = 0
        failure_count = 0
        
        for i in range(0, len(tokens), batch_size):
            batch = tokens[i:i + batch_size]
            
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=batch,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='ic_notification',
                        color='#667eea',
                        sound='default'
                    )
                )
            )
            
            response = messaging.send_multicast(message)
            success_count += response.success_count
            failure_count += response.failure_count
            
            logger.info(f"FCM batch sent: {response.success_count} success, {response.failure_count} failed")
        
        return {"success": success_count, "failure": failure_count}
        
    except Exception as e:
        logger.error(f"Failed to send FCM multicast: {str(e)}")
        return {"success": 0, "failure": len(tokens)}
