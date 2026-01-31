"""
Test OTP verification with time window
"""
import pyotp
from datetime import datetime

print("\n" + "="*70)
print("🔐 OTP TIME WINDOW TEST")
print("="*70 + "\n")

# Generate secret and OTP
secret = pyotp.random_base32()
totp = pyotp.TOTP(secret)
otp_code = totp.now()

print(f"Generated OTP: {otp_code}")
print(f"Secret: {secret}")
print()

# Test verification with different windows
print("Testing verification with different time windows:")
print()

# Default window (0) - only current 30-second window
result_0 = totp.verify(otp_code, valid_window=0)
print(f"Window 0 (current 30s only):    {result_0} {'✅' if result_0 else '❌'}")

# Window 1 - current + 1 window before/after (90 seconds total)
result_1 = totp.verify(otp_code, valid_window=1)
print(f"Window 1 (±30s = 90s total):    {result_1} {'✅' if result_1 else '❌'}")

# Window 5 - current + 5 windows before/after (330 seconds = 5.5 minutes)
result_5 = totp.verify(otp_code, valid_window=5)
print(f"Window 5 (±150s = 330s total):  {result_5} {'✅' if result_5 else '❌'}")

# Window 10 - current + 10 windows before/after (630 seconds = 10.5 minutes)
result_10 = totp.verify(otp_code, valid_window=10)
print(f"Window 10 (±300s = 630s total): {result_10} {'✅' if result_10 else '❌'}")

print()
print("="*70)
print("✅ RECOMMENDATION: Use valid_window=10 for 10-minute validity")
print("="*70)
print()
print("This allows OTP codes to be valid for ~10 minutes, giving users")
print("enough time to receive the email and enter the code.")
print()
