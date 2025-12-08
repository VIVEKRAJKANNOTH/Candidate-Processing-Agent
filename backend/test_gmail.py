"""
Gmail SMTP Test Script
Run this to test your Gmail credentials before using in the app.
"""
import smtplib
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

EMAIL = os.getenv('GMAIL_ADDRESS')
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

print(f"Testing with:")
print(f"  EMAIL: {EMAIL}")
print(f"  APP_PASSWORD: {APP_PASSWORD[:4]}{'*' * (len(APP_PASSWORD)-4) if APP_PASSWORD else 'NOT SET'}")
print()

try:
    print("Connecting to smtp.gmail.com:465...")
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    print("Connected! Attempting login...")
    server.login(EMAIL, APP_PASSWORD)
    print("✅ SUCCESS! Login worked.")
    server.quit()
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ AUTHENTICATION ERROR: {e}")
    print()
    print("To fix this:")
    print("1. Ensure 2FA is enabled: https://myaccount.google.com/security")
    print("2. Generate App Password: https://myaccount.google.com/apppasswords")  
    print("3. Update GMAIL_APP_PASSWORD in .env (no spaces)")
except Exception as e:
    print(f"❌ ERROR: {e}")
