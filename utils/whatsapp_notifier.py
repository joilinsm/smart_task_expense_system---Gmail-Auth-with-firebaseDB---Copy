"""
WhatsApp notification service using Twilio
Sends deadline reminders via WhatsApp
"""
from twilio.rest import Client
from flask import current_app
import logging

def send_whatsapp_notification(phone_number, message):
    """
    Send WhatsApp message notification
    
    Args:
        phone_number: Recipient phone number (format: +1234567890)
        message: Message content
    
    Returns:
        True if message sent successfully, False otherwise
    """
    try:
        # Get Twilio credentials
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        twilio_whatsapp = current_app.config.get('TWILIO_WHATSAPP_NUMBER')
        
        if not account_sid or not auth_token:
            logging.warning("Twilio credentials not configured for WhatsApp")
            if current_app.config.get('DEBUG'):
                print(f"\n{'='*50}")
                print(f"DEBUG MODE: WhatsApp Message (Twilio not configured)")
                print(f"To: {phone_number}")
                print(f"Message: {message}")
                print(f"{'='*50}\n")
            return False
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send WhatsApp message
        msg = client.messages.create(
            body=message,
            from_=twilio_whatsapp,
            to=f'whatsapp:{phone_number}'
        )
        
        logging.info(f"WhatsApp message sent to {phone_number}: {msg.sid}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to send WhatsApp notification to {phone_number}: {str(e)}")
        if current_app.config.get('DEBUG'):
            print(f"\n{'='*50}")
            print(f"DEBUG MODE: WhatsApp Message")
            print(f"To: {phone_number}")
            print(f"Message: {message}")
            print(f"Note: Twilio not fully configured, showing as debug output")
            print(f"{'='*50}\n")
        return False


def send_task_deadline_whatsapp(phone_number, task_title, due_date, hours_remaining):
    """
    Send task deadline reminder via WhatsApp
    
    Args:
        phone_number: Recipient phone number
        task_title: Task title
        due_date: Due date string
        hours_remaining: Hours until deadline
    
    Returns:
        True if sent successfully, False otherwise
    """
    message = f"""
⏰ TASK DEADLINE REMINDER

Task: {task_title}
Due: {due_date}
⏳ Only {hours_remaining} hours remaining!

Complete your task on time to maintain productivity!

Dashboard: http://localhost:5000/dashboard
    """
    
    return send_whatsapp_notification(phone_number, message.strip())


def send_habit_deadline_whatsapp(phone_number, habit_title, deadline_time, time_remaining):
    """
    Send habit deadline reminder via WhatsApp
    
    Args:
        phone_number: Recipient phone number
        habit_title: Habit title
        deadline_time: Target completion time
        time_remaining: Time until deadline
    
    Returns:
        True if sent successfully, False otherwise
    """
    message = f"""
📅 DAILY HABIT REMINDER

Habit: {habit_title}
Target: {deadline_time}
⏳ {time_remaining} remaining

Complete this habit to maintain your streak! 🔥

Dashboard: http://localhost:5000/dashboard
    """
    
    return send_whatsapp_notification(phone_number, message.strip())
