import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

mail_server = 'smtp.gmail.com'
mail_port = 587
mail_username = 'externalverseforu@gmail.com'
mail_password = 'ouil rgry mevx awzi'

try:
    print(f"\n{'='*60}")
    print(f"Testing Gmail SMTP Connection...")
    print(f"{'='*60}")
    print(f"Server: {mail_server}")
    print(f"Port: {mail_port}")
    print(f"Username: {mail_username}")
    
    print(f"\nStep 1: Connecting to SMTP server...", end=' ')
    with smtplib.SMTP(mail_server, mail_port) as server:
        print("✅")
        
        print(f"Step 2: Enabling TLS encryption...", end=' ')
        server.starttls()
        print("✅")
        
        print(f"Step 3: Logging in with credentials...", end=' ')
        server.login(mail_username, mail_password)
        print("✅")
    
    print(f"\n{'='*60}")
    print(f"✅ ALL TESTS PASSED - EMAIL CREDENTIALS ARE VALID!")
    print(f"{'='*60}\n")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌\n")
    print(f"\n{'='*60}")
    print(f"❌ AUTHENTICATION FAILED")
    print(f"{'='*60}")
    print(f"Error: {e}")
    print(f"\nPossible causes:")
    print(f"1. App Password is incorrect or wrong format")
    print(f"2. 2-Step Verification not enabled on Gmail account")
    print(f"3. Gmail account doesn't allow app-specific passwords")
    print(f"\nSolution:")
    print(f"1. Open: https://myaccount.google.com/apppasswords")
    print(f"2. Select Device: Windows Computer")
    print(f"3. Select App: Mail")
    print(f"4. Generate new 16-character App Password")
    print(f"5. Copy and use that password in MAIL_PASSWORD")
    print(f"\nNote: App passwords are different from your Gmail password!")
    print(f"{'='*60}\n")
    
except smtplib.SMTPException as e:
    print(f"❌\n")
    print(f"\n{'='*60}")
    print(f"❌ SMTP ERROR")
    print(f"{'='*60}")
    print(f"Error: {e}")
    print(f"This could be a server issue or connection problem")
    print(f"{'='*60}\n")
    
except Exception as e:
    print(f"❌\n")
    print(f"\n{'='*60}")
    print(f"❌ UNEXPECTED ERROR")
    print(f"{'='*60}")
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
    print(f"{'='*60}\n")
