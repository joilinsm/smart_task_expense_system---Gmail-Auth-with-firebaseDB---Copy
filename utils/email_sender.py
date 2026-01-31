"""
Email utility for sending OTP verification emails
Uses Python's built-in smtplib for email sending
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

def send_otp_email(user_email, username, otp_code):
    """
    Send OTP verification email to user
    
    Args:
        user_email: Recipient email address
        username: Username for personalization
        otp_code: 6-digit OTP code
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Get email configuration
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT')
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', mail_username)
        
        # Debug: Log email attempt
        print(f"\n{'='*60}")
        print(f"📧 ATTEMPTING TO SEND OTP EMAIL")
        print(f"{'='*60}")
        print(f"To: {user_email}")
        print(f"Username: {username}")
        print(f"OTP Code: {otp_code}")
        print(f"SMTP Server: {mail_server}:{mail_port}")
        print(f"TLS Enabled: {mail_use_tls}")
        print(f"From: {mail_sender}")
        print(f"Credentials: {'SET ✅' if mail_username and mail_password else '❌ MISSING'}")
        print(f"{'='*60}\n")
        
        # Validate credentials
        if not mail_username or not mail_password:
            error_msg = "SMTP credentials not configured. Set MAIL_USERNAME and MAIL_PASSWORD environment variables."
            print(f"❌ ERROR: {error_msg}")
            logging.error(error_msg)
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Email Verification - Smart Task & Expense System'
        msg['From'] = mail_sender
        msg['To'] = user_email
        
        # Plain text version
        text_body = f"""
Hello {username},

Thank you for registering with Smart Task & Expense Intelligence System!

Your email verification code is: {otp_code}

This code is valid for 10 minutes.

Please enter this code on the verification page to activate your account.

If you didn't request this verification, please ignore this email.

Best regards,
Smart Task & Expense Team
        """
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #0d6efd; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
        .otp-code {{ font-size: 32px; font-weight: bold; color: #0d6efd; text-align: center; padding: 20px; background-color: white; border-radius: 5px; margin: 20px 0; letter-spacing: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Smart Task & Expense System</h1>
        </div>
        <div class="content">
            <h2>Hello {username},</h2>
            <p>Thank you for registering with Smart Task & Expense Intelligence System!</p>
            <p>Your email verification code is:</p>
            <div class="otp-code">{otp_code}</div>
            <p><strong>This code is valid for 10 minutes.</strong></p>
            <p>Please enter this code on the verification page to activate your account.</p>
            <p>If you didn't request this verification, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Smart Task & Expense Intelligence System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach both parts
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via SMTP with proper error handling
        print(f"Connecting to {mail_server}:{mail_port}...")
        server = None
        try:
            server = smtplib.SMTP(mail_server, mail_port, timeout=30)
            server.set_debuglevel(0)  # Set to 1 for verbose SMTP debugging
            
            print(f"Connection established. Starting TLS...")
            if mail_use_tls:
                server.starttls()  # Enable TLS encryption
                print(f"TLS enabled successfully")
            
            print(f"Logging in as {mail_username}...")
            server.login(mail_username, mail_password)
            print(f"Login successful")
            
            print(f"Sending message...")
            server.send_message(msg)
            print(f"Message sent successfully")
            
        finally:
            if server:
                server.quit()
                print(f"Connection closed")
        
        # Success message
        print(f"\n{'='*60}")
        print(f"✅ EMAIL SENT SUCCESSFULLY")
        print(f"{'='*60}")
        print(f"To: {user_email}")
        print(f"OTP: {otp_code}")
        print(f"{'='*60}\n")
        
        logging.info(f"OTP email sent successfully to {user_email}")
        return True
    
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication failed: {str(e)}. Check MAIL_USERNAME and MAIL_PASSWORD. For Gmail, use App Password."
        print(f"\n{'='*60}")
        print(f"❌ SMTP AUTHENTICATION ERROR")
        print(f"{'='*60}")
        print(f"Error: {error_msg}")
        print(f"Recipient: {user_email}")
        print(f"{'='*60}\n")
        logging.error(f"SMTP auth error sending to {user_email}: {error_msg}")
        return False
        
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        print(f"\n{'='*60}")
        print(f"❌ SMTP ERROR")
        print(f"{'='*60}")
        print(f"Error: {error_msg}")
        print(f"Recipient: {user_email}")
        print(f"{'='*60}\n")
        logging.error(f"SMTP error sending to {user_email}: {error_msg}")
        return False
        
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n{'='*60}")
        print(f"❌ EMAIL SENDING FAILED")
        print(f"{'='*60}")
        print(f"Error: {error_msg}")
        print(f"Recipient: {user_email}")
        print(f"SMTP: {mail_server}:{mail_port}")
        print(f"{'='*60}\n")
        logging.error(f"Failed to send OTP email to {user_email}: {error_msg}")
        
        # In development, print OTP to console for testing
        if current_app.config.get('DEBUG'):
            print(f"\n{'='*60}")
            print(f"🔐 DEBUG MODE - OTP CODE (EMAIL FAILED)")
            print(f"{'='*60}")
            print(f"User: {username} ({user_email})")
            print(f"OTP CODE: {otp_code}")
            print(f"Valid for: 10 minutes")
            print(f"{'='*60}\n")
        return False


def send_verification_reminder_email(user_email, username):
    """
    Send email verification reminder to existing users
    
    Args:
        user_email: Recipient email address
        username: Username for personalization
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Get email configuration
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', mail_username)
        
        if not mail_username or not mail_password:
            raise Exception("Email credentials not configured")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Verify Your Email - Action Required'
        msg['From'] = mail_sender
        msg['To'] = user_email
        
        # Plain text version
        text_body = f"""
Hello {username},

We noticed that your email address has not been verified yet.

To ensure the security of your account and access all features, please verify your email address.

Click the link below to request a verification code:
[Verification Link - Add your domain]

If you have any questions, please contact our support team.

Best regards,
Smart Task & Expense Team
        """
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #ffc107; color: #333; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
        .button {{ display: inline-block; padding: 12px 30px; background-color: #0d6efd; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Email Verification Required</h1>
        </div>
        <div class="content">
            <h2>Hello {username},</h2>
            <p>We noticed that your email address has not been verified yet.</p>
            <p>To ensure the security of your account and access all features, please verify your email address.</p>
            <p style="text-align: center;">
                <strong>Please log in to your account to request a verification code.</strong>
            </p>
            <p>If you have any questions, please contact our support team.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Smart Task & Expense Intelligence System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach both parts
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via SMTP
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()  # Enable TLS encryption
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        logging.info(f"Verification reminder sent to {user_email}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to send verification reminder to {user_email}: {str(e)}")
        return False


def send_password_reset_email(user_email, username, otp_code):
    """
    Send password reset OTP email to user
    
    Args:
        user_email: Recipient email address
        username: Username for personalization
        otp_code: 6-digit OTP code
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        # Get email configuration
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', mail_username)
        
        if not mail_username or not mail_password:
            raise Exception("Email credentials not configured")
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Password Reset - Smart Task & Expense System'
        msg['From'] = mail_sender
        msg['To'] = user_email
        
        # Plain text version
        text_body = f"""
Hello {username},

We received a request to reset your password for Smart Task & Expense Intelligence System.

Your password reset code is: {otp_code}

This code is valid for 10 minutes.

Please enter this code on the password reset page to create a new password.

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

For security reasons, never share this code with anyone.

Best regards,
Smart Task & Expense Team
        """
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
        .otp-code {{ font-size: 32px; font-weight: bold; color: #dc3545; text-align: center; padding: 20px; background-color: white; border-radius: 5px; margin: 20px 0; letter-spacing: 5px; }}
        .warning {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔑 Password Reset Request</h1>
        </div>
        <div class="content">
            <h2>Hello {username},</h2>
            <p>We received a request to reset your password for Smart Task & Expense Intelligence System.</p>
            <p>Your password reset code is:</p>
            <div class="otp-code">{otp_code}</div>
            <p><strong>This code is valid for 10 minutes.</strong></p>
            <p>Please enter this code on the password reset page to create a new password.</p>
            <div class="warning">
                <p><strong>⚠️ Security Notice:</strong></p>
                <ul>
                    <li>If you didn't request this reset, ignore this email</li>
                    <li>Never share this code with anyone</li>
                    <li>Our team will never ask for this code</li>
                </ul>
            </div>
        </div>
        <div class="footer">
            <p>&copy; 2026 Smart Task & Expense Intelligence System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach both parts
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via SMTP
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()  # Enable TLS encryption
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        logging.info(f"Password reset email sent successfully to {user_email}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to send password reset email to {user_email}: {str(e)}")
        # In development, print OTP to console
        if current_app.config.get('DEBUG'):
            print(f"\n{'='*50}")
            print(f"DEBUG MODE: Password Reset OTP for {username} ({user_email})")
            print(f"OTP CODE: {otp_code}")
            print(f"{'='*50}\n")
        return False


def send_task_deadline_notification(user_email, username, task_title, due_date, hours_remaining):
    """
    Send task deadline reminder email
    
    Args:
        user_email: Recipient email address
        username: Username for personalization
        task_title: Title of the task
        due_date: Due date of the task
        hours_remaining: Hours remaining until deadline
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', mail_username)
        
        if not mail_username or not mail_password:
            raise Exception("Email credentials not configured")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'⏰ Task Deadline Reminder: {task_title}'
        msg['From'] = mail_sender
        msg['To'] = user_email
        
        text_body = f"""
Hello {username},

This is a reminder that your task "{task_title}" is due soon!

Due Date: {due_date}
Time Remaining: {hours_remaining} hours

Please complete this task on time.

Access your dashboard to view or update: http://localhost:5000/dashboard

Best regards,
Smart Task & Expense Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #fd7e14; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
        .task-box {{ background-color: white; padding: 20px; border-left: 4px solid #fd7e14; margin: 20px 0; border-radius: 5px; }}
        .deadline {{ font-size: 18px; font-weight: bold; color: #fd7e14; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Task Deadline Reminder</h1>
        </div>
        <div class="content">
            <h2>Hello {username},</h2>
            <p>This is a reminder that your task is due soon!</p>
            <div class="task-box">
                <h3>{task_title}</h3>
                <p><strong>Due Date:</strong> {due_date}</p>
                <p class="deadline">⏳ Only {hours_remaining} hours remaining!</p>
            </div>
            <p>Please complete this task on time to maintain your productivity.</p>
            <p><a href="http://localhost:5000/dashboard" style="background-color: #fd7e14; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Dashboard</a></p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Smart Task & Expense Intelligence System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        logging.info(f"Task deadline reminder sent to {user_email}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to send task deadline reminder to {user_email}: {str(e)}")
        if current_app.config.get('DEBUG'):
            print(f"\n{'='*50}")
            print(f"DEBUG MODE: Task Deadline Notification for {username}")
            print(f"Task: {task_title}")
            print(f"Due: {due_date}")
            print(f"Hours Remaining: {hours_remaining}")
            print(f"{'='*50}\n")
        return False


def send_habit_deadline_notification(user_email, username, habit_title, deadline_time, time_remaining):
    """
    Send habit deadline reminder email
    
    Args:
        user_email: Recipient email address
        username: Username for personalization
        habit_title: Title of the habit
        deadline_time: Time when habit should be completed
        time_remaining: Time remaining until deadline
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', mail_username)
        
        if not mail_username or not mail_password:
            raise Exception("Email credentials not configured")
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'📅 Daily Habit Reminder: {habit_title}'
        msg['From'] = mail_sender
        msg['To'] = user_email
        
        text_body = f"""
Hello {username},

Don't forget to complete your daily habit!

Habit: {habit_title}
Target Time: {deadline_time}
Time Remaining: {time_remaining}

Complete this habit today to maintain your streak!

Access your dashboard: http://localhost:5000/dashboard

Best regards,
Smart Task & Expense Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #198754; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px; }}
        .habit-box {{ background-color: white; padding: 20px; border-left: 4px solid #198754; margin: 20px 0; border-radius: 5px; }}
        .streak {{ font-size: 18px; font-weight: bold; color: #198754; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Daily Habit Reminder</h1>
        </div>
        <div class="content">
            <h2>Hello {username},</h2>
            <p>Don't forget to complete your daily habit!</p>
            <div class="habit-box">
                <h3>🎯 {habit_title}</h3>
                <p><strong>Target Time:</strong> {deadline_time}</p>
                <p class="streak">⏳ {time_remaining} remaining</p>
            </div>
            <p>Complete this habit today to maintain your streak and build positive routines!</p>
            <p><a href="http://localhost:5000/dashboard" style="background-color: #198754; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Mark Habit Complete</a></p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Smart Task & Expense Intelligence System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        logging.info(f"Habit deadline reminder sent to {user_email}")
        return True
    
    except Exception as e:
        logging.error(f"Failed to send habit deadline reminder to {user_email}: {str(e)}")
        if current_app.config.get('DEBUG'):
            print(f"\n{'='*50}")
            print(f"DEBUG MODE: Habit Deadline Notification for {username}")
            print(f"Habit: {habit_title}")
            print(f"Target: {deadline_time}")
            print(f"Time Remaining: {time_remaining}")
            print(f"{'='*50}\n")
        return False

