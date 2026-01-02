# Google OAuth Setup Instructions

## Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
   - Also enable "Google Identity Services API"

4. Create OAuth 2.0 Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - For development: `http://127.0.0.1:8000/accounts/google/login/callback/`
     - For your domain: `https://yourdomain.com/accounts/google/login/callback/`
     - For ngrok: `https://your-ngrok-url.ngrok-free.dev/accounts/google/login/callback/`
   - Click "Create"
   - Copy the **Client ID** and **Client Secret**

## Step 2: Update Django Settings

1. Open `wetechnologies/settings.py`
2. Find the `SOCIALACCOUNT_PROVIDERS` section
3. Replace:
   - `YOUR_GOOGLE_CLIENT_ID` with your actual Client ID
   - `YOUR_GOOGLE_CLIENT_SECRET` with your actual Client Secret

Example:
```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': '123456789-abcdefg.apps.googleusercontent.com',
            'secret': 'GOCSPX-your-secret-here',
            'key': ''
        }
    }
}
```

## Step 3: Configure Site in Django Admin

1. Run: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Login with your admin credentials
4. Go to "Sites" > "Sites"
5. Edit the site with ID=1
6. Set:
   - Domain name: `127.0.0.1:8000` (for development) or your actual domain
   - Display name: `WeTech`

## Step 4: Add Social Application in Django Admin

1. In Django Admin, go to "Social applications" > "Social applications"
2. Click "Add social application"
3. Fill in:
   - Provider: `Google`
   - Name: `Google OAuth`
   - Client id: Your Google Client ID
   - Secret key: Your Google Client Secret
   - Sites: Select your site and move it to "Chosen sites"
4. Click "Save"

## Step 5: Test the Login

1. Go to your login page: http://127.0.0.1:8000/login/
2. Click "Continue with Google"
3. You should be redirected to Google's login page
4. After logging in, you'll be redirected back to your dashboard

## Troubleshooting

- **"Redirect URI mismatch"**: Make sure the redirect URI in Google Console exactly matches: `http://127.0.0.1:8000/accounts/google/login/callback/`
- **"Invalid client"**: Double-check your Client ID and Secret are correct
- **"Site matching query does not exist"**: Make sure you've configured the Site in Django Admin

