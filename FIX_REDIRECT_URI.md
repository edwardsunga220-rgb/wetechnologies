# 🔧 Fix: Google OAuth redirect_uri_mismatch Error

## ❌ Error You're Seeing:
```
Error 400: redirect_uri_mismatch
Access blocked: This app's request is invalid
```

## ✅ Solution: Add Exact Redirect URI to Google Cloud Console

### Step 1: Go to Google Cloud Console

1. Open: https://console.cloud.google.com/
2. Select your project
3. Go to **APIs & Services** > **Credentials**
4. Click on your **OAuth 2.0 Client ID** (the one you're using)

### Step 2: Add the Redirect URI

In the **"Authorized redirect URIs"** section, you MUST add this EXACT URL:

```
https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/
```

**CRITICAL DETAILS:**
- ✅ Must start with `https://` (NOT `http://`)
- ✅ Must match your ngrok domain EXACTLY: `sphygmic-debora-moschate.ngrok-free.dev`
- ✅ Must include the path: `/accounts/google/login/callback/`
- ✅ Must end with a trailing slash `/`
- ✅ No extra spaces or characters

### Step 3: Save and Test

1. Click **"Save"** at the bottom
2. Wait 1-2 minutes for changes to propagate
3. Try logging in again

---

## ⚠️ Common Mistakes:

### ❌ WRONG:
```
http://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/  (http instead of https)
https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback  (missing trailing slash)
https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/callback/  (wrong path)
```

### ✅ CORRECT:
```
https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/
```

---

## 📝 If Your Ngrok URL Changes:

If you get a new ngrok URL, you need to:
1. Update the redirect URI in Google Cloud Console
2. Update the domain in Django Admin > Sites > Sites (Site ID 1)
3. Update `ALLOWED_HOSTS` in `settings.py` (if needed)

---

## 🔍 Verify Your Current Setup:

Your Django site is configured to use:
- **Domain:** `sphygmic-debora-moschate.ngrok-free.dev`
- **Redirect URI:** `https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/`

Make sure Google Cloud Console has the EXACT same redirect URI!

