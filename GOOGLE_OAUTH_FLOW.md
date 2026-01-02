# Google OAuth Login Flow - Complete Guide

## 🔄 Complete Flow Diagram

```
User clicks "Continue with Google"
         ↓
Step 1: Browser redirects to /accounts/google/login/
         ↓
Step 2: Django-allauth checks if user already connected Google?
         ├─ YES → Auto-login → Redirect to /dashboard/
         └─ NO → Continue to Step 3
         ↓
Step 3: Show confirmation page (socialaccount/login.html)
         ↓
Step 4: User clicks "Continue" button
         ↓
Step 5: Redirect to Google OAuth consent screen
         ↓
Step 6: User logs in with Google account
         ↓
Step 7: User grants permissions to your app
         ↓
Step 8: Google redirects back to /accounts/google/login/callback/
         ↓
Step 9: Django-allauth processes the OAuth response
         ├─ Creates/updates user account
         ├─ Creates social account connection
         └─ Logs user in
         ↓
Step 10: Redirect to LOGIN_REDIRECT_URL (/dashboard/)
```

## 📋 Detailed Step-by-Step Explanation

### **Step 1: User Clicks "Continue with Google" Button**

Location: `wetech/templates/login.html` (line 334)
```html
<a href="/accounts/google/login/" class="btn-google">
    Continue with Google
</a>
```

### **Step 2: Django-allauth Checks Existing Connection**

Location: Django-allauth internal logic

**If user is already logged in with Google account:**
- Allauth checks the database for existing `SocialAccount` record
- If found → Automatically logs user in
- Redirects directly to `/dashboard/` (skips confirmation page)
- This is why you don't see the confirmation page on subsequent logins!

**If no existing connection:**
- Continues to Step 3

### **Step 3: Show Confirmation Page**

Location: `wetech/templates/socialaccount/login.html`

This page appears ONLY on the first login. It shows:
- "Sign In Via Google" heading
- Message: "You are about to sign in using a third-party account from Google"
- "Continue" button

### **Step 4: User Clicks "Continue" Button**

The form submits a POST request to `/accounts/google/login/` with CSRF token.

### **Step 5: Redirect to Google OAuth**

Location: Django-allauth redirects to Google's OAuth consent screen

URL looks like:
```
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=http://127.0.0.1:8000/accounts/google/login/callback/&
  response_type=code&
  scope=profile email&
  access_type=online
```

### **Step 6: User Logs in with Google**

- User enters their Google email/password
- Google authenticates the user

### **Step 7: User Grants Permissions**

- Google shows what permissions your app is requesting (profile, email)
- User clicks "Allow" or "Deny"

### **Step 8: Google Redirects Back**

Location: `/accounts/google/login/callback/`

Google sends the user back with:
- Authorization code (in URL parameter `code`)
- State parameter (for security)

Example callback URL:
```
http://127.0.0.1:8000/accounts/google/login/callback/?code=4/0Axxx...&state=yyy...
```

### **Step 9: Django-allauth Processes OAuth Response**

Location: Django-allauth internal logic

What happens:
1. **Exchange authorization code for access token**
   - Allauth makes server-to-server request to Google
   - Exchanges the code for an access token and refresh token

2. **Fetch user info from Google**
   - Uses access token to call Google's API
   - Gets user's email, name, profile picture, etc.

3. **Create or update user account**
   ```python
   # If user with this email exists:
   - Links Google account to existing user
   
   # If new user:
   - Creates new User account with:
     * email = Google email
     * username = Google email (or generated)
     * first_name = Google given name
     * last_name = Google family name
   ```

4. **Create SocialAccount record**
   - Stores the connection between Django User and Google account
   - Table: `socialaccount_socialaccount`

5. **Log user in**
   - Creates Django session
   - Sets user as authenticated

### **Step 10: Redirect to Dashboard**

Location: `wetechnologies/settings.py` (line 198)
```python
LOGIN_REDIRECT_URL = '/dashboard/'
```

User is now:
- ✅ Logged in
- ✅ Redirected to dashboard
- ✅ Ready to use the system

## 🔍 Important Settings Explained

### **SOCIALACCOUNT_AUTO_SIGNUP = True**
- Automatically creates user accounts without showing signup form
- If False, would show a form to fill additional details

### **ACCOUNT_EMAIL_VERIFICATION = 'none'**
- Doesn't require email verification
- If set to 'mandatory', user would need to verify email before login

### **LOGIN_REDIRECT_URL = '/dashboard/'**
- Where users go after successful login
- Can be changed to any URL you want

## 🔐 Security Flow

1. **CSRF Protection**: All POST requests include CSRF token
2. **State Parameter**: OAuth state prevents CSRF attacks
3. **HTTPS Required**: Google requires HTTPS for production (ngrok provides this for development)
4. **Scope Limitation**: Only requests 'profile' and 'email' scopes (minimal permissions)

## 🗄️ Database Records Created

After first Google login, these records are created:

**1. User Table (auth_user)**
```
id | username | email | first_name | last_name | date_joined
1  | user@example.com | user@example.com | John | Doe | 2025-01-XX
```

**2. SocialAccount Table (socialaccount_socialaccount)**
```
id | user_id | provider | uid | date_created
1  | 1       | google   | 123456789 | 2025-01-XX
```

**3. Session Table (django_session)**
```
session_key | session_data | expire_date
abc123...   | encrypted...  | 2025-02-XX
```

## 🔄 Why You Don't See Confirmation Page After First Login

This is the expected behavior! Here's why:

1. **First Login**: 
   - No SocialAccount record exists
   - Shows confirmation page
   - Creates SocialAccount record

2. **Subsequent Logins**:
   - SocialAccount record exists
   - Allauth recognizes existing connection
   - Automatically logs in (no confirmation needed)
   - Direct redirect to dashboard

## 🛠️ Testing the Flow

To see the confirmation page again:
1. Logout: `/logout/`
2. Go to Django Admin: `/admin/`
3. Delete SocialAccount: Social applications > Social accounts > Delete your account
4. Try Google login again → Will show confirmation page

## 📝 Flow Summary

```
First Time:
Login Page → Google Button → Confirmation Page → Google Login → Callback → Dashboard

Second Time (and after):
Login Page → Google Button → Dashboard (auto-login, no confirmation page)
```

This is the standard OAuth flow and provides the best user experience!

