"""
Deadline notification scheduler
Uses APScheduler to check and send deadline reminders
"""
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from datetime import datetime, timedelta
from models.firebase_models import User, Task, Habit
from utils.email_sender import send_task_deadline_notification, send_habit_deadline_notification
import logging

scheduler = BackgroundScheduler()

def check_deadline_notifications():
    """
    Check for upcoming task and habit deadlines
    Send email notifications
    """
    try:
        if not current_app.config.get('ENABLE_DEADLINE_NOTIFICATIONS'):
            return
        
        # Check task deadlines
        check_task_deadlines()
        
        # Check habit deadlines
        check_habit_deadlines()
        
    except Exception as e:
        logging.error(f"Error in deadline notification check: {str(e)}")


def check_task_deadlines():
    """
    Check for upcoming task deadlines and send notifications
    Firebase version - simplified
    """
    try:
        # Note: Firebase doesn't support complex date range queries easily
        # For production, consider using Firebase Functions or Cloud Scheduler
        # This is a simplified version
        
        logging.info("Task deadline check skipped - requires Firebase Functions for production")
        # TODO: Implement with Firebase Functions or migrate to polling-based approach
        
    except Exception as e:
        logging.error(f"Error checking task deadlines: {str(e)}")


def check_habit_deadlines():
    """
    Check for upcoming habit deadlines and send notifications
    Firebase version - simplified
    """
    try:
        # Note: Firebase doesn't support complex queries easily
        # For production, consider using Firebase Functions or Cloud Scheduler
        # This is a simplified version
        
        logging.info("Habit deadline check skipped - requires Firebase Functions for production")
        # TODO: Implement with Firebase Functions or migrate to polling-based approach
        
    except Exception as e:
        logging.error(f"Error checking habit deadlines: {str(e)}")


def start_notification_scheduler(app):
    """
    Start the deadline notification scheduler
    
    Args:
        app: Flask application instance
    """
    try:
        with app.app_context():
            interval = app.config.get('NOTIFICATION_CHECK_INTERVAL', 3600)
            
            # Add job to check deadlines every X seconds
            scheduler.add_job(
                func=check_deadline_notifications,
                trigger="interval",
                seconds=interval,
                id="deadline_checker",
                name="Check deadline notifications",
                replace_existing=True
            )
            
            if not scheduler.running:
                scheduler.start()
                logging.info(f"Deadline notification scheduler started (check interval: {interval}s)")
            
    except Exception as e:
        logging.error(f"Error starting notification scheduler: {str(e)}")


def stop_notification_scheduler():
    """
    Stop the notification scheduler
    """
    try:
        if scheduler.running:
            scheduler.shutdown()
            logging.info("Deadline notification scheduler stopped")
    except Exception as e:
        logging.error(f"Error stopping notification scheduler: {str(e)}")
