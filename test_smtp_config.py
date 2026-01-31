"""
SMTP Configuration Test Script
Tests email sending without running the full Flask app
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection():
    """Test SMTP connection and authentication"""
    print("\n" + "="*70)
    print("🧪 SMTP CONNECTION TEST")
    print("="*70 + "\n")
    
    # Get configuration from environment
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    
    # Display configuration
    print("📧 Configuration:")
    print(f"  Server: {mail_server}")
    print(f"  Port: {mail_port}")
    print(f"  TLS: {mail_use_tls}")
    print(f"  Username: {'SET ✅' if mail_username else '❌ NOT SET'}")
    print(f"  Password: {'SET ✅' if mail_password else '❌ NOT SET'}")
    print()
    
    # Validate credentials
    if not mail_username or not mail_password:
        print("❌ ERROR: MAIL_USERNAME and MAIL_PASSWORD must be set")
        print("\nSet environment variables:")
        print("  set MAIL_USERNAME=your-email@gmail.com")
        print("  set MAIL_PASSWORD=your-app-password")
        return False
    
    # Test connection
    try:
        print("🔌 Step 1: Connecting to SMTP server...")
        server = smtplib.SMTP(mail_server, mail_port, timeout=30)
        print("✅ Connected successfully\n")
        
        print("🔒 Step 2: Starting TLS encryption...")
        if mail_use_tls:
            server.starttls()
            print("✅ TLS enabled successfully\n")
        else:
            print("⚠️ TLS disabled\n")
        
        print("🔑 Step 3: Authenticating...")
        server.login(mail_username, mail_password)
        print("✅ Authentication successful\n")
        
        print("🔌 Step 4: Closing connection...")
        server.quit()
        print("✅ Connection closed\n")
        
        print("="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nYour SMTP configuration is working correctly.")
        print("Email sending should work in the Flask app.\n")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ AUTHENTICATION FAILED\n")
        print(f"Error: {str(e)}\n")
        print("Solutions:")
        print("  1. For Gmail, use App Password (not regular password)")
        print("  2. Enable 2-Step Verification in Google Account")
        print("  3. Create App Password: Google Account → Security → App Passwords")
        print("  4. Remove all spaces from the 16-character password")
        print("  5. Verify MAIL_USERNAME is your correct email address\n")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP ERROR\n")
        print(f"Error: {str(e)}\n")
        print("Solutions:")
        print("  1. Check MAIL_SERVER is correct (smtp.gmail.com for Gmail)")
        print("  2. Verify MAIL_PORT (587 for TLS, 465 for SSL)")
        print("  3. Ensure MAIL_USE_TLS=True for port 587")
        print("  4. Check firewall allows outbound connection on this port\n")
        return False
        
    except Exception as e:
        print(f"❌ CONNECTION FAILED\n")
        print(f"Error: {type(e).__name__}: {str(e)}\n")
        print("Solutions:")
        print("  1. Check your internet connection")
        print("  2. Verify server and port are correct")
        print("  3. Check firewall/antivirus isn't blocking SMTP")
        print("  4. Try port 465 with SSL instead of 587 with TLS\n")
        return False


def send_test_email(recipient_email):
    """Send a test email to verify full functionality"""
    print("\n" + "="*70)
    print("📧 SENDING TEST EMAIL")
    print("="*70 + "\n")
    
    # Get configuration
    mail_server = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    mail_username = os.getenv('MAIL_USERNAME')
    mail_password = os.getenv('MAIL_PASSWORD')
    mail_sender = os.getenv('MAIL_DEFAULT_SENDER', mail_username)
    
    if not mail_username or not mail_password:
        print("❌ ERROR: SMTP credentials not set")
        return False
    
    if not recipient_email:
        print("❌ ERROR: Recipient email not provided")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'SMTP Test - Smart Task & Expense System'
        msg['From'] = mail_sender
        msg['To'] = recipient_email
        
        # Plain text version
        text_body = """
Hello!

This is a test email from Smart Task & Expense System.

If you received this email, your SMTP configuration is working correctly!

Test OTP Code: 123456

Best regards,
Smart Task & Expense Team
        """
        
        # HTML version
        html_body = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #0d6efd; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f8f9fa; padding: 30px; }
        .otp { font-size: 32px; font-weight: bold; color: #0d6efd; text-align: center; 
               padding: 20px; background-color: white; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ SMTP Test Successful!</h1>
        </div>
        <div class="content">
            <h2>Hello!</h2>
            <p>This is a test email from Smart Task & Expense System.</p>
            <p>If you received this email, your SMTP configuration is working correctly!</p>
            <p>Test OTP Code:</p>
            <div class="otp">123456</div>
        </div>
    </div>
</body>
</html>
        """
        
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        print(f"Sending test email to: {recipient_email}")
        print(f"From: {mail_sender}")
        print(f"Via: {mail_server}:{mail_port}\n")
        
        with smtplib.SMTP(mail_server, mail_port, timeout=30) as server:
            if mail_use_tls:
                server.starttls()
            server.login(mail_username, mail_password)
            server.send_message(msg)
        
        print("="*70)
        print("✅ TEST EMAIL SENT SUCCESSFULLY!")
        print("="*70)
        print(f"\nCheck your inbox at: {recipient_email}")
        print("(Don't forget to check spam/junk folder)\n")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {str(e)}\n")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 SMTP CONFIGURATION TESTER")
    print("="*70)
    print("\nThis script tests your SMTP email configuration.")
    print("Make sure you have set the following environment variables:")
    print("  - MAIL_SERVER")
    print("  - MAIL_PORT")
    print("  - MAIL_USE_TLS")
    print("  - MAIL_USERNAME")
    print("  - MAIL_PASSWORD")
    print("\n" + "="*70 + "\n")
    
    # Test connection
    connection_ok = test_smtp_connection()
    
    if connection_ok:
        print("\n" + "="*70)
        response = input("\n📧 Do you want to send a test email? (y/n): ").strip().lower()
        
        if response == 'y':
            recipient = input("Enter recipient email address: ").strip()
            if recipient:
                send_test_email(recipient)
            else:
                print("❌ No recipient email provided")
    else:
        print("\n❌ Connection test failed. Fix the issues above before testing email sending.\n")
