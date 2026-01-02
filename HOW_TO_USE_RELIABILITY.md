# How to Use & Manage Reliability Improvements

## 🎯 **Quick Access**

### 1. **System Status Dashboard**
Navigate to: **Dashboard → System → System Status**

Or directly: `http://localhost:8000/dashboard/system-status/`

**Features:**
- ✅ Real-time health check
- ✅ Database status
- ✅ Disk space monitoring
- ✅ View recent logs (app logs & error logs)
- ✅ Manage database backups
- ✅ Create new backups with one click

---

## 📊 **Health Check Endpoints**

### Public Endpoints (No Login Required):

1. **Full Health Check:**
   ```
   GET /health/
   ```
   Returns comprehensive system status including:
   - Database connectivity
   - Disk space usage
   - Media directory status
   - Static files status

2. **Readiness Probe:**
   ```
   GET /health/ready/
   ```
   Quick check if system is ready (for Kubernetes/Docker)

3. **Liveness Probe:**
   ```
   GET /health/live/
   ```
   Minimal check if system is alive

**Test in browser:**
- Visit: `http://localhost:8000/health/`
- Should return JSON with system status

---

## 📝 **Viewing Logs**

### Option 1: System Status Dashboard
1. Go to Dashboard → System → System Status
2. Scroll to "Recent Logs" section
3. View last 20 lines of:
   - Application logs (app.log)
   - Error logs (errors.log)

### Option 2: Direct File Access
Logs are stored in: `logs/` directory
- `logs/app.log` - All application logs
- `logs/errors.log` - Error logs only
- `logs/django.log` - Django framework logs
- `logs/django_errors.log` - Django errors

**View logs:**
```bash
# Windows PowerShell
Get-Content logs\app.log -Tail 50

# Linux/Mac
tail -f logs/app.log
```

---

## 💾 **Database Backups**

### Create Backup:

**Option 1: Dashboard (Recommended)**
1. Go to Dashboard → System → System Status
2. Scroll to "Database Backups" section
3. Click "Create Backup" button
4. Backup will be created instantly

**Option 2: Command Line**
```bash
python manage.py backup_db
```

**Option 3: Keep more backups**
```bash
python manage.py backup_db --keep 60
```

### View Backups:
- Dashboard → System → System Status → Database Backups section
- Shows: Filename, Size, Date, Download link

### Download Backup:
- Click "Download" button next to any backup
- Backup files are stored in: `backups/` directory

### Automated Backups:

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py backup_db`
7. Start in: `D:\wetechnologies\wetechnologies`

**Linux/Mac (Cron):**
```bash
crontab -e
# Add this line:
0 2 * * * cd /path/to/wetechnologies && python manage.py backup_db
```

---

## 🔍 **Monitoring Performance**

### Slow Request Tracking:
The performance middleware automatically logs:
- Requests taking >1 second (warning)
- Requests taking >5 seconds (error)

**View in logs:**
```bash
# Check for slow requests
grep "Slow request" logs/app.log
```

### Check Health Status:
```bash
# Using curl
curl http://localhost:8000/health/

# Using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health/ | Select-Object -ExpandProperty Content
```

---

## 🚨 **Error Tracking**

### View Errors:
1. **Dashboard:** System Status → Recent Logs → Error Logs
2. **File:** `logs/errors.log`
3. **Django Errors:** `logs/django_errors.log`

### Error Log Format:
```
2025-01-15 10:30:45 - wetech - ERROR - Payment failed: Connection timeout - [views.py:1681]
```

### Search Errors:
```bash
# Find all errors today
grep "ERROR" logs/errors.log | grep "2025-01-15"

# Find payment errors
grep "Payment" logs/errors.log
```

---

## 🔄 **Retry Mechanisms**

### Automatic Retries:
Payment APIs (Pesapal & AzamPay) now automatically retry on:
- Network connection errors
- Request timeouts
- Temporary failures

**Retry Configuration:**
- Max retries: 3
- Initial delay: 2 seconds
- Backoff: Exponential (2x each retry)

**View retry attempts in logs:**
```bash
grep "retry" logs/app.log
```

---

## 🔒 **Security Features**

### Production Settings:
When `DEBUG=False`, these are automatically enabled:
- SSL redirect
- Secure cookies
- XSS protection
- Content type sniffing protection
- HSTS headers

### Environment Variables:
Set these in production:
```bash
# Windows
set DEBUG=False
set SECRET_KEY=your-secret-key-here

# Linux/Mac
export DEBUG=False
export SECRET_KEY=your-secret-key-here
```

---

## 📈 **What Gets Logged**

### Payment Operations:
- ✅ Payment initiation
- ✅ Authentication attempts
- ✅ Payment redirects
- ✅ Payment callbacks
- ✅ Invoice status changes
- ✅ Errors with full context

### Lead Submissions:
- ✅ Lead creation
- ✅ Client creation
- ✅ Invoice creation
- ✅ Payment redirects
- ✅ Errors with stack traces

### System Operations:
- ✅ Health check results
- ✅ Slow requests
- ✅ Database operations
- ✅ Backup creation
- ✅ Error tracking

---

## 🎛️ **Dashboard Navigation**

### Access System Status:
1. Login to dashboard
2. Click "System" in sidebar
3. Click "System Status"
4. View all reliability features

### Menu Location:
```
Dashboard
├── Command Center
├── Content & Services
├── Marketplace
├── Business
└── System
    ├── Message Logs
    ├── System Status ← NEW!
    └── Settings
```

---

## 🧪 **Testing**

### Test Health Endpoint:
```bash
# Should return 200 OK
curl http://localhost:8000/health/
```

### Test Logging:
```python
# In Django shell
python manage.py shell
>>> from wetech.utils.logger import logger
>>> logger.info("Test message")
# Check logs/app.log
```

### Test Backup:
```bash
python manage.py backup_db
# Check backups/ directory
```

### Test Retry:
- Temporarily disconnect internet
- Try making a payment
- Check logs for retry attempts

---

## 📱 **Mobile/Remote Access**

### Health Check URL:
```
http://YOUR_IP:8000/health/
```

### System Status Dashboard:
```
http://YOUR_IP:8000/dashboard/system-status/
```

---

## 🔔 **Alerts & Notifications**

### Setup Uptime Monitoring:
1. Sign up at https://uptimerobot.com (free)
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://yourdomain.com/health/`
   - Interval: 5 minutes
3. Get email/SMS alerts when system is down

### Setup Error Tracking (Sentry):
1. Sign up at https://sentry.io (free tier available)
2. Install: `pip install sentry-sdk`
3. Add to `settings.py`:
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.django import DjangoIntegration
   
   if not DEBUG:
       sentry_sdk.init(
           dsn="YOUR_SENTRY_DSN",
           integrations=[DjangoIntegration()],
       )
   ```

---

## 📚 **Useful Commands**

```bash
# View last 50 log lines
tail -n 50 logs/app.log

# Watch logs in real-time
tail -f logs/app.log

# Search for specific error
grep "Payment failed" logs/errors.log

# Count errors today
grep "$(date +%Y-%m-%d)" logs/errors.log | wc -l

# List all backups
ls -lh backups/

# Create backup manually
python manage.py backup_db

# Check disk space
df -h  # Linux/Mac
Get-PSDrive C  # Windows PowerShell
```

---

## 🎯 **Quick Reference**

| Feature | Location | Access |
|---------|----------|--------|
| System Status | Dashboard → System → System Status | `/dashboard/system-status/` |
| Health Check | Public endpoint | `/health/` |
| View Logs | System Status page | Dashboard UI |
| Create Backup | System Status page | Dashboard UI |
| Backup Command | Terminal | `python manage.py backup_db` |
| Log Files | File system | `logs/` directory |
| Backup Files | File system | `backups/` directory |

---

## ✅ **Verification**

After implementation, verify everything works:

1. ✅ Server starts without errors
2. ✅ `/health/` endpoint returns 200 OK
3. ✅ System Status page loads
4. ✅ Logs directory is created
5. ✅ Backup command works
6. ✅ Logs appear in dashboard
7. ✅ Backups appear in dashboard

---

**All reliability features are now active and ready to use!** 🚀

