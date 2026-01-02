# 🔴 FIX: redirect_uri_mismatch Error

## The Problem
You're getting `Error 400: redirect_uri_mismatch` because Google Cloud Console doesn't have the correct redirect URI.

## ✅ The Solution (Step-by-Step)

### Step 1: Open Google Cloud Console
1. Go to: **https://console.cloud.google.com/**
2. Make sure you're in the **correct project** (the one where you created OAuth credentials)

### Step 2: Navigate to Credentials
1. Click **"APIs & Services"** in the left sidebar
2. Click **"Credentials"**
3. Find your **OAuth 2.0 Client ID** (the one with your Client ID that starts with numbers)
4. **Click on it** to edit

### Step 3: Add the Redirect URI
1. Scroll down to **"Authorized redirect URIs"** section
2. Click **"+ ADD URI"** button
3. Copy and paste this EXACT URL:
   ```
   https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/
   ```
4. Make sure:
   - ✅ Starts with `https://` (NOT `http://`)
   - ✅ Ends with `/` (trailing slash is REQUIRED)
   - ✅ No extra spaces before or after
   - ✅ Matches EXACTLY: `sphygmic-debora-moschate.ngrok-free.dev`

### Step 4: Save
1. Click **"SAVE"** button at the bottom
2. Wait **1-2 minutes** for changes to take effect

### Step 5: Test
1. Go back to your login page
2. Click "Continue with Google"
3. It should work now! ✅

---

## ❌ Common Mistakes to Avoid

### WRONG ❌:
```
http://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/
(missing 's' in https)

https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback
(missing trailing slash)

https://sphygmic-debora-moschate.ngrok-free.dev/callback/
(wrong path)
```

### CORRECT ✅:
```
https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/
```

---

## 📸 What It Should Look Like

In Google Cloud Console, under "Authorized redirect URIs", you should see:
```
https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/
```

---

## ⚠️ If Your Ngrok URL Changes

If you get a new ngrok URL, you need to:
1. Update the redirect URI in Google Cloud Console with the new URL
2. Update Django Admin > Sites > Sites (Site ID 1) with the new domain
3. Update `ALLOWED_HOSTS` in `settings.py` if needed

---

## 🎯 Quick Checklist

- [ ] Opened Google Cloud Console
- [ ] Went to APIs & Services > Credentials
- [ ] Clicked on my OAuth 2.0 Client ID
- [ ] Added this EXACT URL: `https://sphygmic-debora-moschate.ngrok-free.dev/accounts/google/login/callback/`
- [ ] Clicked SAVE
- [ ] Waited 1-2 minutes
- [ ] Tested the login

---

**Once you complete these steps, the error will be fixed!** 🎉

