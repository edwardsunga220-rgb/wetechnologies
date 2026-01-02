from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, FileResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.db import connection
from pathlib import Path
import os
import time
from django.conf import settings
from .models import (
    Product, Client, Invoice, 
    ServiceCategory, ServiceItem, ServiceTag, 
    ContactMessage, Project, EmailTemplate, SentEmail, BusinessSettings, NewsItem, Subscriber, ProjectImage
)

# ==========================================
# 1. MARKETPLACE & PRODUCTS
# ==========================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

# ==========================================
# 2. CRM (CLIENTS & INVOICES)
# ==========================================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_info', 'product_interested', 'source', 'status', 'created_at')
    list_filter = ('source', 'status', 'created_at')
    search_fields = ('name', 'contact_info', 'product_interested')
    ordering = ('-created_at',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'client', 'product', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_id', 'client__name', 'product_name')
    readonly_fields = ('invoice_id', 'created_at')
    autocomplete_fields = ['client', 'product']

# ==========================================
# 3. SERVICES (WITH NESTED TAGS)
# ==========================================
class ServiceTagInline(admin.TabularInline):
    model = ServiceTag
    extra = 1

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'order')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    inlines = [ServiceTagInline]

# ==========================================
# 4. SYSTEM LOGS & MESSAGES
# ==========================================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_read', 'mark_as_unread', 'bulk_delete']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} messages marked as read.', messages.SUCCESS)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} messages marked as unread.', messages.SUCCESS)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    def bulk_delete(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} messages deleted.', messages.SUCCESS)
    bulk_delete.short_description = "Delete selected messages"

# ==========================================
# 5. PROJECTS
# ==========================================
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'client_name', 'completed_date')
    list_filter = ('category', 'completed_date')
    search_fields = ('title', 'client_name')
    inlines = [ProjectImageInline]

# ==========================================
# 6. NEWS & SUBSCRIBERS
# ==========================================
@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)

# ==========================================
# 7. EMAIL MANAGEMENT
# ==========================================
@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subject', 'created_at', 'updated_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'subject', 'body')
    ordering = ('-created_at',)

@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'recipient_name', 'subject', 'status', 'sent_at', 'client')
    list_filter = ('status', 'sent_at', 'template')
    search_fields = ('recipient', 'recipient_name', 'subject', 'message')
    readonly_fields = ('sent_at',)
    ordering = ('-sent_at',)

# ==========================================
# 8. BUSINESS SETTINGS
# ==========================================
@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not BusinessSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# ==========================================
# 9. SYSTEM MANAGEMENT - Custom Admin Views
# ==========================================
def system_status_view(request):
    """System status dashboard for admin"""
    if not request.user.is_superuser:
        from django.contrib.auth.decorators import user_passes_test
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Permission denied")
    
    from django.utils import timezone
    from datetime import timedelta
    from .models import Invoice
    
    # Get system health data
    health_data = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_data['database'] = {'status': 'ok', 'message': 'Connected'}
    except Exception as e:
        health_data['database'] = {'status': 'error', 'message': str(e)}
    
    # Disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        disk_percent = (used / total) * 100
        health_data['disk'] = {
            'status': 'ok' if disk_percent < 90 else 'warning',
            'used_percent': round(disk_percent, 2),
            'free_gb': round(free / (1024**3), 2),
            'total_gb': round(total / (1024**3), 2)
        }
    except Exception as e:
        health_data['disk'] = {'status': 'error', 'message': str(e)}
    
    # Get recent activities
    now = timezone.now()
    recent_invoices = Invoice.objects.all().order_by('-created_at')[:10]
    recent_payments = Invoice.objects.filter(status='Paid', created_at__gte=now - timedelta(days=7)).order_by('-created_at')[:5]
    
    # Get log file stats
    logs_dir = Path(settings.BASE_DIR) / 'logs'
    log_stats = {}
    if logs_dir.exists():
        app_log = logs_dir / 'app.log'
        error_log = logs_dir / 'errors.log'
        
        if app_log.exists():
            log_stats['app_log_size'] = round(app_log.stat().st_size / 1024, 2)
            log_stats['app_log_lines'] = sum(1 for _ in open(app_log, 'r', encoding='utf-8', errors='ignore'))
        
        if error_log.exists():
            log_stats['error_log_size'] = round(error_log.stat().st_size / 1024, 2)
            log_stats['error_log_lines'] = sum(1 for _ in open(error_log, 'r', encoding='utf-8', errors='ignore'))
    
    # Get backup stats
    backups_dir = Path(settings.BASE_DIR) / 'backups'
    backup_count = 0
    latest_backup = None
    if backups_dir.exists():
        backups = list(backups_dir.glob('db_backup_*.sqlite3'))
        backup_count = len(backups)
        if backups:
            latest_backup = max(backups, key=os.path.getmtime)
            latest_backup_time = time.localtime(latest_backup.stat().st_mtime)
            latest_backup = {
                'filename': latest_backup.name,
                'date': time.strftime('%Y-%m-%d %H:%M:%S', latest_backup_time),
                'size_mb': round(latest_backup.stat().st_size / (1024 * 1024), 2)
            }
    
    # Performance stats
    slow_requests_today = 0
    errors_today = 0
    if logs_dir.exists():
        app_log = logs_dir / 'app.log'
        error_log = logs_dir / 'errors.log'
        today_str = timezone.now().strftime('%Y-%m-%d')
        
        if app_log.exists():
            try:
                with open(app_log, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if 'Slow request' in line and today_str in line:
                            slow_requests_today += 1
            except:
                pass
        
        if error_log.exists():
            try:
                with open(error_log, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if today_str in line and 'ERROR' in line:
                            errors_today += 1
            except:
                pass
    
    context = {
        **admin.site.each_context(request),
        'title': 'System Status & Reliability',
        'health_data': health_data,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'log_stats': log_stats,
        'backup_count': backup_count,
        'latest_backup': latest_backup,
        'slow_requests_today': slow_requests_today,
        'errors_today': errors_today,
    }
    
    return TemplateResponse(request, 'admin/system_status.html', context)

def create_backup_view(request):
    """Create database backup from admin"""
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return HttpResponseRedirect(reverse('admin:index'))
    
    try:
        from django.core.management import call_command
        from io import StringIO
        from wetech.utils.logger import logger
        
        out = StringIO()
        call_command('backup_db', stdout=out)
        result = out.getvalue()
        
        messages.success(request, 'Database backup created successfully!')
        logger.info("Backup created from admin panel", extra={'user': request.user.username})
    except Exception as e:
        messages.error(request, f'Backup failed: {str(e)}')
        logger.error(f"Backup creation failed from admin: {str(e)}", exc_info=True)
    
    return HttpResponseRedirect(reverse('admin:system_status'))

def download_backup_view(request, filename):
    """Download backup file from admin"""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Permission denied")
    
    backups_dir = Path(settings.BASE_DIR) / 'backups'
    file_path = backups_dir / filename
    
    if not file_path.exists() or not str(file_path).startswith(str(backups_dir)):
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound("Backup file not found")
    
    response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def health_check_view(request):
    """Health check endpoint for admin"""
    from django.http import JsonResponse
    
    checks = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks['checks']['database'] = {'status': 'ok'}
    except Exception as e:
        checks['checks']['database'] = {'status': 'error', 'error': str(e)}
        checks['status'] = 'unhealthy'
    
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        disk_percent = (used / total) * 100
        checks['checks']['disk'] = {
            'status': 'ok' if disk_percent < 90 else 'warning',
            'used_percent': round(disk_percent, 2),
            'free_gb': round(free / (1024**3), 2)
        }
    except Exception as e:
        checks['checks']['disk'] = {'status': 'error', 'error': str(e)}
    
    return JsonResponse(checks)

# Add custom admin URLs by extending the admin site's get_urls method
# This is done at the end of the file to ensure all models are registered first
def _get_custom_admin_urls():
    """Get custom admin URLs for system management"""
    return [
        path('system-status/', admin.site.admin_view(system_status_view), name='system_status'),
        path('create-backup/', admin.site.admin_view(create_backup_view), name='create_backup'),
        path('download-backup/<str:filename>/', admin.site.admin_view(download_backup_view), name='download_backup'),
        path('health-check/', admin.site.admin_view(health_check_view), name='health_check'),
    ]

# Store original get_urls method
_original_admin_get_urls = admin.site.get_urls

# Override get_urls to include custom URLs
def _patched_admin_get_urls():
    """Patched get_urls that includes custom system management URLs"""
    return _get_custom_admin_urls() + _original_admin_get_urls()

# Apply the patch
admin.site.get_urls = _patched_admin_get_urls
