"""
Direct FCM HTTP v1 API implementation to bypass Firebase Admin SDK issues.
"""
import requests
import json
import logging
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from app.config import get_settings
import os

logger = logging.getLogger(__name__)
settings = get_settings()

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

def get_access_token():
    """Get OAuth2 access token from service account credentials."""
    try:
        if not settings.FIREBASE_CREDENTIALS_PATH:
            logger.error("Firebase credentials path not set")
            return None
            
        if not os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            logger.error(f"Firebase credentials file not found at {settings.FIREBASE_CREDENTIALS_PATH}")
            return None
        
        credentials = service_account.Credentials.from_service_account_file(
            settings.FIREBASE_CREDENTIALS_PATH,
            scopes=SCOPES
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        logger.error(f"Failed to get access token: {str(e)}")
        return None

def send_fcm_notification_rest(token: str, title: str, body: str, data: dict = None):
    """
    Send FCM notification using HTTP v1 REST API.
    
    Args:
        token: FCM device token
        title: Notification title
        body: Notification body
        data: Optional data payload
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        access_token = get_access_token()
        if not access_token:
            logger.error("Failed to get access token")
            return False
        
        project_id = "iitjhealthcenter"
        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }
        
        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body
                },
                "data": data or {},
                "android": {
                    "priority": "high",
                    "notification": {
                        "icon": "ic_notification",
                        "color": "#667eea",
                        "sound": "default"
                    }
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=message)
        
        if response.status_code == 200:
            logger.info(f"FCM notification sent successfully to token {token[:20]}...")
            return True
        else:
            logger.error(f"FCM send failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send FCM notification via REST: {str(e)}")
        return False

def send_fcm_multicast_rest(tokens: list, title: str, body: str, data: dict = None):
    """
    Send FCM notification to multiple devices using HTTP v1 REST API.
    
    Args:
        tokens: List of FCM device tokens
        title: Notification title
        body: Notification body
        data: Optional data payload
    
    Returns:
        dict: Success and failure counts
    """
    success_count = 0
    failure_count = 0
    
    for token in tokens:
        if send_fcm_notification_rest(token, title, body, data):
            success_count += 1
        else:
            failure_count += 1
    
    logger.info(f"FCM REST batch sent: {success_count} success, {failure_count} failed")
    return {"success": success_count, "failure": failure_count}
