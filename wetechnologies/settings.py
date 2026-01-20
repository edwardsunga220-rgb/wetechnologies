from pathlib import Path
import socket
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Use environment variable in production
SECRET_KEY = os.environ.get('SECRET_KEY',)

# SECURITY WARNING: don't run with debug turned on in production!
# Set to False in production and use environment variable
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ==========================================
# AUTOMATIC IP CONFIGURATION FOR MOBILE ACCESS
# ==========================================
def get_local_ip():
    """
    Tricks the OS into revealing the IP address used to connect to the internet
    (Wi-Fi or Ethernet) without actually sending data.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

LOCAL_IP = get_local_ip()

ALLOWED_HOSTS = ['*'].
# This prints the clickable link in your terminal when you run the server
if DEBUG:
    print(f"\n\033[92m  SYSTEM ACCESSIBLE AT: http://{LOCAL_IP}:8000 \033[0m\n")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    
    # allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google provider
    
    'wetech',  
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # allauth middleware
    'wetech.middleware.performance.PerformanceMonitoringMiddleware',  # Performance monitoring
]

ROOT_URLCONF = 'wetechnologies.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Point specifically to the 'templates' folder in the root directory
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wetech.context_processors.navbar_news',
                'wetech.context_processors.business_settings',
                'django.template.context_processors.request',  # Required for allauth
            ],
        },
    },
]

WSGI_APPLICATION = 'wetechnologies.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

import os

# The URL to use when referring to static files
STATIC_URL = 'static/'

# The absolute path to the directory where collectstatic will collect static files for deployment.
# On PythonAnywhere, this will resolve to /home/wetech/wetechnologies/staticfiles
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# This tells Django where to look for your custom static files (development)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media Files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# PESAPAL LIVE CONFIGURATION
# ==========================================
# These are the keys you shared that passed the test
PESAPAL_CONSUMER_KEY = '4GhwfZhAIHWFcfM+5SuXaplx3FOTwIkY'
PESAPAL_CONSUMER_SECRET = 'W/o5cg2sMi/PzNTFgd0BT3nWtVA='

# LIVE URL
PESAPAL_BASE_URL = 'https://pay.pesapal.com/v3'

# CRITICAL: Allow Ngrok to send POST requests (CSRF protection)
CSRF_TRUSTED_ORIGINS = ['https://sphygmic-debora-moschate.ngrok-free.dev']



# AZAMPAY LIVE CONFIGURATION
AZAMPAY_APP_NAME = 'We-Tech'
AZAMPAY_CLIENT_ID = '56d3d192-c4be-43c9-bfba-ca4c58d4c4db'
AZAMPAY_CLIENT_SECRET = 'HA3gUN5zxWHH4HMVhssK/Gc42LJVgeRwRlGvfsR6xE126ho6voLvvVyeLKKDuwoq/VC/Zep1YAne2/LVPUcfMYwyHf6LupeijEHLFwoCACG5jVJ6W4TMBizmrRcvKltZcbUg0jQwoPIR9t9tue2IYx/K9CW/KBxcUStCy9jb+xa+CzV1+cWa7KHBTTb+BTzX7+Eu2GJ1tfQxNZiLlaYqu6Gu2wIClMpSVAILsTxsd69as3bqeiufyfCGtqpgZ1v6c4j0OEAfzViPlnlKwQVJ9siImAka0JbYZ9142DI7FSUysBJfdTp9tyP5wwXX3sRL4WbVSM7/rmYnHQ345Y0n1LZ2fyQAasamXLxj4KPtTu/zVCWQ9Ov0cz8I8CiQ0rQ5oA+pCyxpBhKCctgALWgEebmw6Mwrz99fPMKtQgZgYIwArjYTgXaKlHtwifSGyqoD6YBWx3qd+AS+JjnRbRBYxttU9qFYTmqA6w398UU+BUH4syauJ1WvHay8IJQ0A/Bwi0u5vCBeycUkjqnxzvsHQkryfHRCfuCK9Xd/cNxWVE5EHAI7jZ0X7VmMLe0Dxdrqp6xY1A4h5rmHEmja5ctGabHtiXp0lDzXz9TLG/ynqrcF4LwEVq9VrJMRXMnkI6J7aUnulxh4glCOvDT+e+sHjK+fiTO6vlHNnbC/A9thGWE='
AZAMPAY_SANDBOX = True  # Set to True if testing, False for Live

# ==========================================
# DJANGO-ALLAUTH CONFIGURATION (Google OAuth)
# ==========================================
SITE_ID = 1  # Required for allauth

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default Django auth
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth
]

# Django Sites Framework (Required for allauth)
SITE_ID = 1  # Use Site ID 1 (updated to your ngrok domain)

# allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Set to 'mandatory' if you want email verification
LOGIN_REDIRECT_URL = '/dashboard/'  # Redirect directly to dashboard after Google login
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True  # Allow logout via GET request
SOCIALACCOUNT_AUTO_SIGNUP = True  # Automatically create user accounts - skips signup form
SOCIALACCOUNT_QUERY_EMAIL = True  # Request email from Google
SOCIALACCOUNT_STORE_TOKENS = False  # Don't store OAuth tokens

# Google OAuth Settings
# Configure Google OAuth in Django Admin: Admin > Social applications > Add social application
# Get credentials from: https://console.cloud.google.com/apis/credentials

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        # When using Django Admin configuration, don't define 'APP' here
        # The SocialApp from database will be used automatically
    }
}

# ==========================================
# RELIABILITY & SECURITY SETTINGS
# ==========================================

# Security settings (only active when DEBUG=False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'error_file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'wetech': {
            'handlers': ['file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
logs_dir = BASE_DIR / 'logs'
os.makedirs(logs_dir, exist_ok=True)
