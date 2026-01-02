# Quick Start: Reliability Features Integration

## 🚀 **Step 1: Add Health Check Endpoints**

Add to `wetech/urls.py`:
```python
from wetech.views.health import health_check, readiness_check, liveness_check

urlpatterns = [
    # ... existing patterns ...
    path('health/', health_check, name='health_check'),
    path('health/ready/', readiness_check, name='readiness_check'),
    path('health/live/', liveness_check, name='liveness_check'),
]
```

**Test it:**
```bash
curl http://localhost:8000/health/
```

---

## 🚀 **Step 2: Enable Logging**

Update `wetech/views.py` imports:
```python
from wetech.utils.logger import logger
from django.db import transaction
```

Update critical functions (example):
```python
@csrf_exempt
@transaction.atomic
def save_lead(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info("Lead submission started", extra={'source': data.get('source')})
            
            with transaction.atomic():
                client = Client.objects.create(
                    name=data.get('name'),
                    contact_info=data.get('contact'),
                    product_interested=data.get('product'),
                    source=data.get('source')
                )
                logger.info(f"Client created: {client.id}", extra={'client_id': client.id})
                
                # ... rest of code ...
                
        except Exception as e:
            logger.error(f"Lead submission failed: {str(e)}", exc_info=True, 
                        extra={'data': data if 'data' in locals() else None})
            return JsonResponse({'status': 'error', 'message': str(e)})
```

---

## 🚀 **Step 3: Add Performance Monitoring**

Update `wetechnologies/settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'wetech.middleware.performance.PerformanceMonitoringMiddleware',  # ADD THIS
]
```

---

## 🚀 **Step 4: Add Retry to Payment APIs**

Update `wetech/pesapal.py`:
```python
from wetech.utils.retry import retry_network

class Pesapal:
    @retry_network
    def get_access_token(self):
        # ... existing code ...
        pass
    
    @retry_network
    def submit_order(self, token, order_data):
        # ... existing code ...
        pass
```

Update `wetech/azampay.py`:
```python
from wetech.utils.retry import retry_network

class AzamPayClient:
    @retry_network
    def mobile_checkout(self, mobile_number, amount, external_id, provider):
        # ... existing code ...
        pass
```

---

## 🚀 **Step 5: Setup Database Backups**

**Manual backup:**
```bash
python manage.py backup_db
```

**Automated backup (Linux/Mac cron):**
```bash
# Edit crontab: crontab -e
# Add this line to backup daily at 2 AM:
0 2 * * * cd /path/to/wetechnologies && python manage.py backup_db
```

**Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 2:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py backup_db`
7. Start in: `D:\wetechnologies\wetechnologies`

---

## 🚀 **Step 6: Update .gitignore**

Add to `.gitignore`:
```
# Logs
logs/
*.log

# Backups
backups/
*.sqlite3.backup
```

---

## 🚀 **Step 7: Test Everything**

```bash
# 1. Test logging
python manage.py shell
>>> from wetech.utils.logger import logger
>>> logger.info("Test log message")

# 2. Test health check
curl http://localhost:8000/health/

# 3. Test backup
python manage.py backup_db

# 4. Check logs directory
ls logs/
# Should see: app.log and errors.log
```

---

## 📊 **Monitoring Setup**

### Option 1: UptimeRobot (Free)
1. Sign up at https://uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://yourdomain.com/health/`
   - Interval: 5 minutes
3. Get email alerts when system is down

### Option 2: Sentry (Error Tracking)
```bash
pip install sentry-sdk
```

Add to `settings.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn="YOUR_SENTRY_DSN_HERE",
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False
    )
```

Get DSN from: https://sentry.io

---

## ✅ **Verification Checklist**

- [ ] Health check endpoint returns 200 OK
- [ ] Logs directory created with app.log and errors.log
- [ ] Database backup command works
- [ ] Performance middleware logs slow requests
- [ ] Payment APIs retry on network failures
- [ ] Critical views use @transaction.atomic
- [ ] Error logging works in production

---

## 🎯 **Next Steps**

After implementing these basics, move to:
1. Rate limiting (django-ratelimit)
2. Caching (Redis)
3. PostgreSQL migration
4. Comprehensive testing
5. Security hardening

See `RELIABILITY_IMPROVEMENTS.md` for full details.

