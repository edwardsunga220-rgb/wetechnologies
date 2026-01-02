# 🔧 Quick Fix: Google OAuth "invalid_client" Error

## ❌ Error You're Seeing:
```
Access blocked: Authorization Error
The OAuth client was not found.
Error 401: invalid_client
```

## ✅ Solution: Configure Google OAuth in Django Admin

**EASIEST METHOD** (Recommended by django-allauth):

### Step 1: Get Google OAuth Credentials

1. Go to: https://console.cloud.google.com/
2. Click "Create Project" or select existing
3. Go to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Choose "Web application"
6. **Add Authorized redirect URIs:**
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   http://localhost:8000/accounts/google/login/callback/
   ```
   (Add your ngrok URL if using: `https://your-url.ngrok-free.dev/accounts/google/login/callback/`)
7. Click "Create"
8. **COPY** the Client ID (looks like: `123456789-abc...apps.googleusercontent.com`)
9. **COPY** the Client Secret (looks like: `GOCSPX-abc...`)

### Step 2: Configure in Django Admin

1. **Start your server:**
   ```bash
   python manage.py runserver
   ```

2. **Go to Django Admin:**
   - URL: http://127.0.0.1:8000/admin/
   - Login with your admin account

3. **Configure Site (if not done):**
   - Go to "Sites" > "Sites"
   - Click on the site (usually ID=1)
   - Set Domain name: `127.0.0.1:8000`
   - Set Display name: `WeTech`
   - Click "Save"

4. **Add Social Application:**
   - Go to "Social applications" > "Social applications"
   - Click "Add social application" (top right)
   - Fill in:
     - **Provider:** Select `Google` from dropdown
     - **Name:** `Google OAuth` (or any name)
     - **Client id:** Paste your Google Client ID
     - **Secret key:** Paste your Google Client Secret
     - **Sites:** Select your site from "Available sites" and click the arrow (→) to move it to "Chosen sites"
   - Click "Save"

5. **Test:**
   - Go to: http://127.0.0.1:8000/login/
   - Click "Continue with Google"
   - Should now work! ✅

---

## Alternative: Configure in settings.py

If you prefer to use settings.py instead:

1. Open `wetechnologies/settings.py`
2. Find the `SOCIALACCOUNT_PROVIDERS` section
3. Uncomment the 'APP' section
4. Replace with your actual credentials:

```python
'APP': {
    'client_id': '123456789-your-actual-id.apps.googleusercontent.com',
    'secret': 'GOCSPX-your-actual-secret-here',
    'key': ''
}
```

**But Django Admin method is recommended!**

---

## ⚠️ Common Issues:

### Issue 1: "Redirect URI mismatch"
**Fix:** Make sure the redirect URI in Google Console EXACTLY matches:
- `http://127.0.0.1:8000/accounts/google/login/callback/`
- Include the trailing slash `/`
- Use `127.0.0.1` not `localhost` (or add both)

### Issue 2: "Site matching query does not exist"
**Fix:** Make sure you configured the Site in Django Admin (Step 3 above)

### Issue 3: Still getting "invalid_client"
**Fix:** 
- Double-check you copied the ENTIRE Client ID and Secret (they're long!)
- Make sure there are no extra spaces
- Try restarting your Django server after adding credentials

---

## 📝 Your Redirect URI Must Be:

For development:
```
http://127.0.0.1:8000/accounts/google/login/callback/
```

For production/ngrok:
```
https://your-domain.com/accounts/google/login/callback/
```

**Make sure it ends with `/callback/` and matches EXACTLY!**

