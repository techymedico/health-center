from sqlalchemy.orm import Session
from app.database import Subscription
from app.scraper.notification_logic import check_upcoming_doctors
from datetime import datetime
import logging
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

def send_email_notification(email: str, doctors: list):
    """Send email notification about upcoming doctors."""
    try:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured, skipping email")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏥 {len(doctors)} Doctor(s) Arriving Soon - IITJ Health Center"
        msg['From'] = settings.SMTP_FROM or settings.SMTP_USER
        msg['To'] = email
        
        # Create HTML body
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #2563eb;">🏥 Doctors Arriving Soon</h2>
                    <p>The following doctor(s) will be available shortly:</p>
                    <ul style="list-style: none; padding: 0;">
        """
        
        for doc in doctors:
            html_body += f"""
                        <li style="background: #f0f9ff; padding: 15px; margin: 10px 0; border-left: 4px solid #2563eb;">
                            <strong>{doc['name']}</strong> ({doc['category']})<br>
                            <span style="color: #666;">Starting in {doc['starts_in_minutes']} minutes</span><br>
                            <span style="color: #666;">Time: {doc['time_range']}</span>
                        </li>
            """
        
        html_body += """
                    </ul>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        This is an automated notification from IITJ Health Center Schedule App.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return False

def send_push_notification(subscription_info: dict, doctors: list):
    """Send web push notification."""
    try:
        if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
            logger.warning("VAPID keys not configured, skipping push notification")
            return False
        
        from pywebpush import webpush
        
        # Create notification payload
        title = f"🏥 {len(doctors)} Doctor(s) Arriving Soon"
        body = "\n".join([f"• {d['name']} in {d['starts_in_minutes']} min" for d in doctors[:3]])
        
        payload = json.dumps({
            "title": title,
            "body": body,
            "icon": "/logo.png",
            "badge": "/badge.png"
        })
        
        # Send push notification
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={
                "sub": settings.VAPID_CLAIMS_EMAIL
            }
        )
        
        logger.info("Push notification sent successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send push notification: {str(e)}")
        return False

def check_and_notify(db: Session):
    """
    Check for upcoming doctors and send notifications to all subscribers.
    Called by the scheduler every minute.
    """
    try:
        from app.database import Schedule, FCMToken, DoctorSubscription
        from app.services.fcm_service import send_fcm_multicast
        
        # Get all schedules
        schedules = db.query(Schedule).all()
        
        # Convert to list of dicts for notification_logic
        schedule_data = []
        for s in schedules:
            schedule_data.append({
                "date": s.date,
                "name": s.name,
                "timing": s.timing,
                "category": s.category,
                "room": s.room
            })
        
        # Use simplified check since our data is already clean
        upcoming = check_upcoming_from_clean_data(schedule_data)
        
        if not upcoming:
            logger.debug("No upcoming doctors found")
            return
        
        logger.info(f"Found {len(upcoming)} upcoming doctor(s)")
        
        # Send to each doctor's subscribers
        for doctor_info in upcoming:
            doctor_name = doctor_info['name']
            
            # Get web/email subscriptions
            subscriptions = db.query(Subscription).filter(Subscription.is_active == True).all()
            
            for sub in subscriptions:
                # Send email if configured
                if sub.email:
                    send_email_notification(sub.email, [doctor_info])
                
                # Send push notification if configured
                if sub.push_subscription:
                    try:
                        push_info = json.loads(sub.push_subscription)
                        send_push_notification(push_info, [doctor_info])
                    except json.JSONDecodeError:
                        logger.error(f"Invalid push subscription JSON for subscription {sub.id}")
            
            # Get FCM subscriptions for this specific doctor
            doctor_subs = db.query(DoctorSubscription).filter(
                DoctorSubscription.doctor_name == doctor_name
            ).all()
            
            if doctor_subs:
                # Get FCM tokens for these devices
                device_ids = [sub.device_id for sub in doctor_subs]
                fcm_tokens_objs = db.query(FCMToken).filter(
                    FCMToken.device_id.in_(device_ids)
                ).all()
                
                fcm_tokens = [token.fcm_token for token in fcm_tokens_objs]
                
                if fcm_tokens:
                    # Send FCM notifications
                    title = "🏥 Doctor Duty Started"
                    body = f"Dr. {doctor_name} ({doctor_info['category']}) duty starts in {doctor_info['starts_in_minutes']} minutes"
                    data = {
                        "doctor_name": doctor_name,
                        "category": doctor_info['category'],
                        "time_range": doctor_info['time_range'],
                        "starts_in_minutes": str(doctor_info['starts_in_minutes'])
                    }
                    
                    result = send_fcm_multicast(fcm_tokens, title, body, data)
                    logger.info(f"FCM sent to {result['success']} devices for {doctor_name}")
        
    except Exception as e:
        logger.error(f"Error in check_and_notify: {str(e)}")

def check_upcoming_from_clean_data(schedule_data: list) -> list:
    """
    Simplified version of check_upcoming_doctors for our clean data format.
    Returns list of upcoming doctors.
    """
    from datetime import datetime, timedelta
    from app.scraper.notification_logic import parse_time_range
    
    current_dt = datetime.now()
    current_date_str = current_dt.strftime("%d/%m/%Y")
    upcoming = []
    
    for row in schedule_data:
        # Check if date matches
        if current_date_str not in row.get("date", ""):
            continue
        
        timing_str = row.get("timing")
        if not timing_str:
            continue
        
        times = parse_time_range(timing_str)
        if not times:
            continue
        
        start, end = times
        start_dt = datetime.combine(current_dt.date(), start)
        
        # Check if doctor starts within next 60 minutes
        time_diff = start_dt - current_dt
        minutes_until = time_diff.total_seconds() / 60
        
        if 0 <= minutes_until <= 60:
            upcoming.append({
                "name": row.get("name"),
                "category": row.get("category"),
                "starts_in_minutes": int(minutes_until),
                "time_range": timing_str
            })
    
    return upcoming
