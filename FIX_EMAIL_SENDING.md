# 📧 OTP EMAIL NOT SENDING - FIX NOW

## Problem Identified

Your email credentials are in `.env` locally but **NOT SET IN RENDER ENVIRONMENT VARIABLES**.

When Render runs your app, it doesn't have:
- `MAIL_USERNAME`
- `MAIL_PASSWORD`

So the email sending fails silently.

---

## Solution: Add Email Environment Variables to Render

### Step 1: Go to Render Dashboard
- URL: https://dashboard.render.com
- Click your service (smart-task-expense)

### Step 2: Go to Settings → Environment Variables

### Step 3: Add These 3 Variables

```
Name: MAIL_USERNAME
Value: externalverseforu@gmail.com

Name: MAIL_PASSWORD
Value: ouil rgry mevx awzi

Name: MAIL_DEFAULT_SENDER
Value: externalverseforu@gmail.com
```

### Step 4: Save & Redeploy

1. Click **Save**
2. Go to **Deployments** tab
3. Click **Redeploy Latest**
4. Wait for ✅ (2-5 minutes)

---

## Test Email Sending

After redeploy:

1. Go to your live URL: `https://smart-task-expense.onrender.com`
2. Register a new account with **a real email address**
3. OTP email should arrive in ~30 seconds

**Check spam folder** if not in inbox.

---

## ALL Environment Variables Needed for Render

### Firebase (already added):
- FIREBASE_TYPE
- FIREBASE_PROJECT_ID
- FIREBASE_PRIVATE_KEY_ID
- FIREBASE_PRIVATE_KEY
- FIREBASE_CLIENT_EMAIL
- FIREBASE_CLIENT_ID
- FIREBASE_CLIENT_X509_CERT_URL

### Email (ADD THESE NOW):
- MAIL_USERNAME = externalverseforu@gmail.com
- MAIL_PASSWORD = ouil rgry mevx awzi
- MAIL_DEFAULT_SENDER = externalverseforu@gmail.com

### Optional (recommended):
- SECRET_KEY = [generate-a-random-key]

---

## Why It's Not Sending

**Local development:**
```
.env file → Python loads MAIL_USERNAME/MAIL_PASSWORD → Email sends ✅
```

**Render without env vars:**
```
No .env file (security) → No MAIL_USERNAME/MAIL_PASSWORD → Email fails ❌
```

**Render with env vars:**
```
Environment variables set → Python loads them → Email sends ✅
```

---

## Time to Fix: 5 Minutes

1. Add 3 email variables: 2 min
2. Redeploy: 3 min
3. Test registration: 1 min

**Go to Render NOW and add the email variables!**
