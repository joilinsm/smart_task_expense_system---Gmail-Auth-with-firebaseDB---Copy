# 🔧 MAIL NOT SENDING - TROUBLESHOOTING GUIDE

## I Need to See the Actual Error

Without seeing the exact error message from Render, I can't fix it. Let's find it together.

---

## Step 1: Check Render Logs (CRITICAL)

### How to access:

1. Go to: **https://dashboard.render.com**
2. Click your service: `smart-task-expense`
3. Click **Logs** tab (at the top)
4. Scroll down to the most recent logs
5. Register again with a test email to trigger the error
6. Watch the logs in real-time

### What to look for:

Look for ANY of these messages:

**If email was attempted:**
```
📧 SENDING OTP EMAIL
============================================================
MAIL_SERVER: smtp.gmail.com
MAIL_PORT: 587
MAIL_USERNAME: SET ✅ or NOT SET ❌
MAIL_PASSWORD: SET ✅ or NOT SET ❌
...
```

**If email succeeded:**
```
✅ EMAIL SENT SUCCESSFULLY!
To: your-email@gmail.com
OTP Code: 123456
```

**If email failed:**
```
❌ EMAIL SENDING FAILED
Error: [SPECIFIC ERROR MESSAGE HERE]
```

---

## Step 2: Verify Environment Variables in Render

1. Go to Render Dashboard
2. Click your service
3. Click **Settings** (not Logs)
4. Scroll to **Environment Variables** section

**CHECK THESE EXIST:**

- [ ] MAIL_USERNAME
- [ ] MAIL_PASSWORD
- [ ] MAIL_DEFAULT_SENDER
- [ ] FLASK_ENV
- [ ] SECRET_KEY

If ANY are missing → **Add them now**

---

## Step 3: Screenshot Your Environment Variables

1. Scroll down to Environment Variables section
2. Take a screenshot showing ALL variables
3. Share the screenshot (hide sensitive values if needed)

This will show me exactly what's configured.

---

## Step 4: Test Registration & Check Logs

1. Go to your live URL
2. Click Register
3. Fill form (use a real email)
4. Click Submit
5. Go back to Render Logs tab
6. Look for email messages
7. **Copy the EXACT error message**

---

## Common Issues I'll Check For

### Issue 1: MAIL_USERNAME or MAIL_PASSWORD NOT SET

**Error you'll see:**
```
❌ EMAIL CREDENTIALS NOT CONFIGURED
Add MAIL_USERNAME and MAIL_PASSWORD to Render environment variables
```

**Fix:** Add email variables to Render

---

### Issue 2: WRONG Email Credentials

**Error you'll see:**
```
❌ EMAIL SENDING FAILED
Error: (535, b'5.7.8 Username and password not accepted...
```

**Fix:** Use correct app password (not Gmail password)

---

### Issue 3: Gmail Blocking Render IP

**Error you'll see:**
```
❌ EMAIL SENDING FAILED
Error: (421, b'4.7.0 Try again later. Please retry your connection later. Information ref...
```

**Fix:** Check Gmail security: https://myaccount.google.com/security

---

### Issue 4: Port/TLS Issue

**Error you'll see:**
```
❌ EMAIL SENDING FAILED
Error: SMTPServerDisconnected
```

**Fix:** Verify MAIL_PORT=587 and TLS enabled

---

## What I Need From You

Please provide:

1. **Screenshot of Environment Variables in Render**
   - Shows what's actually set

2. **Exact Error Message from Render Logs**
   - Copy-paste the error when registration fails

3. **Confirmation:**
   - Did you click Save after adding variables?
   - Did you click Redeploy Latest?
   - Did you wait for deployment to finish (✅)?

---

## Testing Checklist

Before reporting error, verify:

- [ ] Went to Render Dashboard
- [ ] Clicked on your service
- [ ] Went to Settings → Environment Variables
- [ ] MAIL_USERNAME is set
- [ ] MAIL_PASSWORD is set
- [ ] MAIL_DEFAULT_SENDER is set
- [ ] Clicked Save
- [ ] Went to Deployments
- [ ] Clicked Redeploy Latest
- [ ] Waited 5 minutes for green ✅
- [ ] Tried registering again
- [ ] Checked Render Logs for error

---

## Exact Steps to See Error

### 1. Open Render Logs:
```
Dashboard → Your Service → Logs
```

### 2. Clear logs (optional):
Scroll to bottom to see most recent

### 3. Open your website in new tab:
```
https://smart-task-expense.onrender.com
```

### 4. Click Register

### 5. Fill form:
```
Username: testuser123
Email: your-real-email@gmail.com
Password: Test@1234
Confirm: Test@1234
First Name: Test
Last Name: User
```

### 6. Click Register button

### 7. Go back to Logs tab

### 8. Look for "EMAIL" messages

### 9. Copy ANY error you see

---

## Once You Have the Error

Share with me:

```
What you see in Render Logs:
[PASTE EXACT ERROR HERE]

Screenshot of Environment Variables:
[DESCRIBE WHAT'S SET]

Confirmation:
- Clicked Save? YES/NO
- Clicked Redeploy Latest? YES/NO
- Waited for deployment? YES/NO
```

---

## Possible Solutions Based on Error

### If "Not configured":
→ Add email variables

### If "Invalid credentials":
→ Check Gmail app password

### If "Connection timeout":
→ Check firewall/VPN settings

### If "Gmail blocked":
→ Allow Render IP in Gmail security

### If "Other":
→ Share exact error, I'll diagnose

---

## Why I Need the Error

The error message tells me:
- If variables are missing
- If credentials are wrong
- If connection failed
- If Firebase failed
- If something else failed

Without it, I'm guessing. With it, I know exactly what to fix.

---

## DO THIS RIGHT NOW:

1. Open Render Logs
2. Register with test email
3. Copy the error you see
4. Paste it here
5. I'll give you the exact fix

**That's all I need to solve this!**
