# Firebase Environment Variables Setup for Render.com

## 🔴 Problem
Render deployment failed because Firebase credentials are not set in environment variables.

**Error:**
```
ValueError: Firebase credentials not configured. See .env setup instructions.
```

## ✅ Solution

Your app needs Firebase credentials as **environment variables** in Render. The `firebase-credentials.json` file exists locally but is in `.gitignore` (not pushed to GitHub for security).

---

## Step 1: Extract Firebase Credentials from Your JSON File

1. **Open your local file:**
   - Location: `firebase-credentials.json` (in your project root)
   - Open with any text editor (VS Code, Notepad, etc.)

2. **You'll see content like this:**
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id-12345",
     "private_key_id": "abcdef1234567890",
     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANB...",
     "client_email": "firebase-adminsdk-abc@your-project-id.iam.gserviceaccount.com",
     "client_id": "1234567890",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/..."
   }
   ```

---

## Step 2: Set Environment Variables in Render.com

1. **Go to your web service on Render dashboard**
   - URL: `https://dashboard.render.com/`

2. **Navigate to Environment Variables:**
   - Click on your service name (smart-task-expense or similar)
   - Go to **Settings** tab
   - Scroll to **Environment Variables** section

3. **Add these 6 environment variables** (copy values from your JSON file):

| Environment Variable | Value | Source in JSON |
|---|---|---|
| `FIREBASE_TYPE` | `service_account` | `type` field |
| `FIREBASE_PROJECT_ID` | Your project ID | `project_id` field |
| `FIREBASE_PRIVATE_KEY_ID` | Your key ID | `private_key_id` field |
| `FIREBASE_PRIVATE_KEY` | Your private key | `private_key` field (keep newlines) |
| `FIREBASE_CLIENT_EMAIL` | Your service account email | `client_email` field |
| `FIREBASE_CLIENT_ID` | Your client ID | `client_id` field |
| `FIREBASE_CLIENT_X509_CERT_URL` | Your cert URL | `client_x509_cert_url` field |

### 🚨 IMPORTANT: Private Key Formatting

The `private_key` field contains newlines as `\n` characters. **You must preserve these:**

**Example from JSON file:**
```
"private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC..."
```

**When entering in Render:**
1. Copy the ENTIRE `private_key` value including `-----BEGIN...` and `...END-----`
2. Keep the `\n` characters as-is (they represent newlines)
3. Paste into the Render environment variable field
4. DO NOT manually add actual line breaks - keep the `\n` text

---

## Step 3: Add ALL Required Environment Variables

In Render dashboard → Settings → Environment Variables, add these (even if just the minimum):

```
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-value
FIREBASE_PRIVATE_KEY_ID=your-value
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANB...\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=your-value
FIREBASE_CLIENT_ID=your-value
FIREBASE_CLIENT_X509_CERT_URL=your-value
SECRET_KEY=production-secret-key-change-this
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## Step 4: Deploy

After adding all environment variables:

1. **Manual redeploy:**
   - Go to Deployments tab
   - Click "Redeploy latest" on your most recent deployment
   - Wait for build and deploy to complete

2. **OR** - Force rebuild by pushing code to GitHub:
   ```bash
   # From your project folder
   git add .
   git commit -m "Deploy with Firebase env vars configured"
   git push
   ```

---

## Step 5: Verify Deployment

Once deployment completes (green checkmark):

1. **Visit your live URL**
   - Example: `https://smart-task-expense.onrender.com`

2. **Test login:**
   - Email: `demo`
   - Password: `demo123`

3. **Check logs if errors:**
   - Render dashboard → Logs tab
   - Should see: `✅ Firebase initialized successfully!`

---

## 🔍 Troubleshooting

### Error: "private_key format is invalid"
- **Cause:** Newlines were converted to actual line breaks instead of `\n` text
- **Fix:** Copy the `private_key` field EXACTLY as shown in JSON, with `\n` preserved

### Error: "client_email is empty"
- **Cause:** Missing `FIREBASE_CLIENT_EMAIL` environment variable
- **Fix:** Add this variable from your `firebase-credentials.json` file

### Error: "project_id is empty"
- **Cause:** Missing `FIREBASE_PROJECT_ID` environment variable
- **Fix:** Add this variable from your `firebase-credentials.json` file

### Build succeeds but site shows 500 error
- **Cause:** Check Render logs for the actual error
- **Fix:** Click Logs tab and look for error messages starting with `❌` or Python tracebacks

---

## 📋 Quick Reference

**Files involved:**
- Local: `firebase-credentials.json` (contains all values)
- Render: Environment Variables section (where you paste values)
- Code: `firebase_db.py` (reads environment variables automatically)
- Code: `config.py` (includes `FIREBASE_CONFIG` dict)

**Environment variables read by app:**
```python
# In firebase_db.py line ~182-200
FIREBASE_TYPE
FIREBASE_PROJECT_ID
FIREBASE_PRIVATE_KEY_ID
FIREBASE_PRIVATE_KEY       # Most important - must have \n preserved
FIREBASE_CLIENT_EMAIL
FIREBASE_CLIENT_ID
FIREBASE_CLIENT_X509_CERT_URL
```

---

## ⏱️ Expected Timeline

- Add env vars: 5 minutes
- Redeploy: 2-5 minutes
- Test: 2 minutes
- **Total: ~10 minutes to fix**

---

## ✅ Success Indicators

When properly configured, you should see:

**In Render Logs:**
```
✅ Firebase initialized successfully!
INFO: Started server process
```

**On your website:**
- Login page loads
- Demo account login works
- Dashboard displays
- No 500 errors

---

**Need more help?** Check Render troubleshooting: https://render.com/docs/troubleshooting-deploys
