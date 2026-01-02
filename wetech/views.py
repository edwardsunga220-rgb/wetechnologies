
import azampay
from .models import Product
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from django.conf import settings
from .models import Client 
from django.db.models import Count
from .models import ServiceCategory
from .models import Invoice, Client, Product 
from .models import Product, ServiceCategory
from .forms import ServiceItemForm, ServiceTagFormSet
from .models import Product, Client, ServiceItem, ContactMessage, Invoice, Project, EmailTemplate, SentEmail
from django.db import transaction
from django.db import connection
import time
import os
import shutil


def home(request):
    # 1. Fetch the 3 newest products to show as "Latest Releases"
    recent_products = Product.objects.all().order_by('-created_at')[:3]
    
    # 2. Fetch Services (just the categories) to show "What We Do"
    services = ServiceCategory.objects.all().order_by('order')[:4]
    
    # 3. List of available background images
    background_images = [
       
        'images/img/estatepro.jpg',
        'images/img/logistic.jpg',
        'images/img/medical.jpg',
         'images/img/ci.jpg',
    ]
    
    # Generate full static URLs for all background images
    hero_bg_images = [settings.STATIC_URL + img for img in background_images]
    
    context = {
        'recent_products': recent_products,
        'services': services,
        'hero_background_images': hero_bg_images
    }
    return render(request, 'index.html', context)

def overview(request):
    return render(request, 'overview.html')



def portfolio(request):
    return render(request, 'portfolio.html')

def clients(request):
    return render(request, 'clients.html')

def about(request):
    return render(request, 'about.html')



def pricing(request):
    return render(request, 'pricing.html')

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)



def dash_clients(request):
    return render(request, 'dashboard/clients.html')


def dash_email(request):
    return render(request, 'dashboard/email.html')


@login_required(login_url='login')
def dash_settings(request):
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.decorators import login_required
    from .forms import ProfileForm, CustomPasswordChangeForm
    from django.urls import reverse
    
    user = request.user
    active_tab = request.GET.get('tab', 'profile')
    
    # Initialize forms
    profile_form = ProfileForm(instance=user)
    password_form = CustomPasswordChangeForm()
    
    # Handle form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect(reverse('dash_settings') + '?tab=profile')
        
        elif form_type == 'password':
            password_form = CustomPasswordChangeForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                new_password = password_form.cleaned_data['new_password']
                
                # Verify current password
                if not user.check_password(current_password):
                    messages.error(request, 'Current password is incorrect.')
                    return redirect(reverse('dash_settings') + '?tab=security')
                else:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)  # Keep user logged in
                    messages.success(request, 'Password changed successfully!')
                    return redirect(reverse('dash_settings') + '?tab=security')
        
        elif form_type == 'preferences':
            # Handle preferences updates (can be stored in user session or separate model)
            theme = request.POST.get('theme', 'dark')
            items_per_page = request.POST.get('items_per_page', '20')
            date_format = request.POST.get('date_format', 'Y-m-d')
            time_format = request.POST.get('time_format', '12')
            
            # Store in session
            request.session['theme'] = theme
            request.session['items_per_page'] = items_per_page
            request.session['date_format'] = date_format
            request.session['time_format'] = time_format
            
            messages.success(request, 'Preferences saved successfully!')
            return redirect(reverse('dash_settings') + '?tab=preferences')
        
        elif form_type == 'notifications':
            # Handle notification preferences
            email_notifications = request.POST.get('email_notifications') == 'on'
            sms_notifications = request.POST.get('sms_notifications') == 'on'
            digest_frequency = request.POST.get('digest_frequency', 'daily')
            
            request.session['email_notifications'] = email_notifications
            request.session['sms_notifications'] = sms_notifications
            request.session['digest_frequency'] = digest_frequency
            
            messages.success(request, 'Notification preferences saved!')
            return redirect(reverse('dash_settings') + '?tab=notifications')
        
        elif form_type == 'business':
            # Handle business information - save to BusinessSettings model
            try:
                from .models import BusinessSettings
                business = BusinessSettings.load()
                business.company_name = request.POST.get('company_name', business.company_name)
                business.company_email = request.POST.get('company_email', business.company_email)
                business.company_phone = request.POST.get('company_phone', business.company_phone)
                business.company_address = request.POST.get('company_address', business.company_address)
                business.save()
                
                messages.success(request, 'Business information saved!')
                return redirect(reverse('dash_settings') + '?tab=business')
            except Exception as e:
                messages.error(request, f'Error saving business settings: {str(e)}. Please run migrations first.')
                return redirect(reverse('dash_settings') + '?tab=business')
    
    # Get current values for display
    try:
        from .models import BusinessSettings
        business = BusinessSettings.load()
    except Exception:
        # If table doesn't exist yet, use defaults
        business = type('obj', (object,), {
            'company_name': 'WeTech',
            'company_email': 'support@we-tech.com',
            'company_phone': '+255 777 749 824',
            'company_address': 'Dar es Salaam, Tanzania\nInnovation Hub'
        })()
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'active_tab': active_tab,
        'theme': request.session.get('theme', 'dark'),
        'items_per_page': request.session.get('items_per_page', '20'),
        'date_format': request.session.get('date_format', 'Y-m-d'),
        'time_format': request.session.get('time_format', '12'),
        'email_notifications': request.session.get('email_notifications', True),
        'sms_notifications': request.session.get('sms_notifications', False),
        'digest_frequency': request.session.get('digest_frequency', 'daily'),
        'company_name': business.company_name,
        'company_email': business.company_email,
        'company_phone': business.company_phone,
        'company_address': business.company_address,
    }
    
    return render(request, 'dashboard/settings.html', context)



# Removed duplicate save_lead function - see line 880 for the complete version

# 2. Update Clients View
@login_required(login_url='login')
def dash_clients(request):
    clients = Client.objects.all().order_by('-created_at')
    return render(request, 'dashboard/clients.html', {'clients': clients})

# 3. Update Email View (Enhanced Email Composer)
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json

@login_required(login_url='login')
def dash_email(request):
    
    # Get all clients with email addresses
    clients = Client.objects.filter(contact_info__contains='@').order_by('-created_at')
    
    # Get email templates
    templates = EmailTemplate.objects.all().order_by('-created_at')
    
    # Get sent emails
    sent_emails = SentEmail.objects.all().order_by('-sent_at')[:50]
    
    # Statistics
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    total_sent = SentEmail.objects.count()
    sent_today = SentEmail.objects.filter(sent_at__gte=today_start).count()
    sent_this_week = SentEmail.objects.filter(sent_at__gte=week_start).count()
    sent_this_month = SentEmail.objects.filter(sent_at__gte=month_start).count()
    
    # Most contacted clients
    most_contacted = SentEmail.objects.values('recipient', 'recipient_name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Template usage
    template_usage = SentEmail.objects.exclude(template=None).values('template__name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        recipient_name = request.POST.get('recipient_name', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        template_id = request.POST.get('template_id')
        client_id = request.POST.get('client_id')
        
        # Get client if provided
        client = None
        if client_id:
            try:
                client = Client.objects.get(id=client_id)
                recipient = client.contact_info
                recipient_name = client.name
            except Client.DoesNotExist:
                pass
        
        # Get template if provided
        template = None
        if template_id:
            try:
                template = EmailTemplate.objects.get(id=template_id)
            except EmailTemplate.DoesNotExist:
                pass
        
        # Save to sent emails history
        sent_email = SentEmail.objects.create(
            recipient=recipient,
            recipient_name=recipient_name,
            subject=subject,
            message=message,
            client=client,
            template=template,
            status='sent'
        )
        
        # Try to send email (requires email configuration)
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@wetech.com',
                [recipient],
                fail_silently=False,
            )
            sent_email.status = 'sent'
            sent_email.save()
            messages.success(request, f'Email sent to {recipient} successfully!')
        except Exception as e:
            sent_email.status = 'failed'
            sent_email.save()
            messages.error(request, f'Failed to send email: {str(e)}')
        
        return redirect('dash_email')
    
    # Prepare template categories for dropdown
    template_categories = EmailTemplate.CATEGORY_CHOICES
    
    context = {
        'clients': clients,
        'templates': templates,
        'sent_emails': sent_emails,
        'total_sent': total_sent,
        'sent_today': sent_today,
        'sent_this_week': sent_this_week,
        'sent_this_month': sent_this_month,
        'most_contacted': most_contacted,
        'template_usage': template_usage,
        'template_categories': template_categories,
    }
    
    return render(request, 'dashboard/email.html', context)











from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialApp
from django.conf import settings

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard') # Redirects to dashboard after login
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def google_login_redirect(request):
    """Redirect to Google OAuth login"""
    # Redirect to allauth's Google login endpoint
    return redirect('/accounts/google/login/')

def marketplace(request):
    # Fetch all products
    all_products = Product.objects.all()
    
    # Featured products (newest 3)
    featured_products = all_products.order_by('-created_at')[:3]
    
    # Trending (you can customize this logic - for now using newest)
    trending_products = all_products.order_by('-created_at')[:4]
    
    # Best sellers (for now using oldest, you can add a sales_count field later)
    bestsellers = all_products.order_by('created_at')[:4]
    
    # All products for main grid
    products = all_products.order_by('-created_at')
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'trending_products': trending_products,
        'bestsellers': bestsellers,
    }
    return render(request, 'marketplace.html', context)


@login_required(login_url='login')
def dash_products(request):
    from django.db.models import Count, Sum, Avg, Q, Max, Min
    from django.utils import timezone
    from datetime import timedelta
    
    # Get all products
    products = Product.objects.all().order_by('-created_at')
    
    # Statistics
    total_products = products.count()
    
    # Products by category
    products_by_category = products.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Products with/without demo links
    products_with_demo = products.exclude(Q(demo_link__isnull=True) | Q(demo_link='')).count()
    products_without_demo = total_products - products_with_demo
    
    # Price statistics
    total_inventory_value = products.aggregate(Sum('price'))['price__sum'] or 0
    avg_price = products.aggregate(Avg('price'))['price__avg'] or 0
    max_price = products.aggregate(Max('price'))['price__max'] or 0
    min_price = products.aggregate(Min('price'))['price__min'] or 0
    
    # Products with discounts (old_price)
    products_with_discount = products.exclude(Q(old_price__isnull=True) | Q(old_price__lte=0)).count()
    
    # Recent products
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    recent_products_7d = products.filter(created_at__gte=last_7_days).count()
    recent_products_30d = products.filter(created_at__gte=last_30_days).count()
    
    # Average price by category
    avg_price_by_category = products.values('category').annotate(
        avg_price=Avg('price'),
        count=Count('id')
    ).order_by('-avg_price')
    
    # Category choices for filter
    category_choices = Product.CATEGORY_CHOICES
    
    # Recent products list
    recent_products = products[:5]
    
    context = {
        'products': products,
        'total_products': total_products,
        'products_by_category': products_by_category,
        'products_with_demo': products_with_demo,
        'products_without_demo': products_without_demo,
        'total_inventory_value': total_inventory_value,
        'avg_price': avg_price,
        'max_price': max_price,
        'min_price': min_price,
        'products_with_discount': products_with_discount,
        'recent_products_7d': recent_products_7d,
        'recent_products_30d': recent_products_30d,
        'avg_price_by_category': avg_price_by_category,
        'category_choices': category_choices,
        'recent_products': recent_products,
    }
    
    return render(request, 'dashboard/products.html', context)

@login_required(login_url='login')
def delete_product(request, product_id):
    # Logic to delete a product
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'System has been deleted successfully.')
    return redirect('dash_products')


@login_required(login_url='login')
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # We pass 'instance=product' so Django knows we are updating, not creating
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'System updated successfully!')
            return redirect('dash_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/edit_product.html', {'form': form, 'product': product})


@login_required(login_url='login')
def dash_upload(request):
    if request.method == 'POST':
        # Process the form data when button is clicked
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'System uploaded successfully!')
            return redirect('dash_products')
    else:
        # Create an empty form to display
        form = ProductForm()

    # Pass the 'form' variable to the template
    return render(request, 'dashboard/upload.html', {'form': form})


from django.core.paginator import Paginator # <--- Add this import at the top
from django.urls import reverse # Import this at top

# Removed duplicate save_lead function - see line 880 for the complete version

# 2. Update dash_clients with Pagination
@login_required(login_url='login')
def dash_clients(request):
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get all clients
    client_list = Client.objects.all().order_by('-created_at')
    
    # Statistics
    total_clients = client_list.count()
    
    # Clients by source
    clients_by_source = client_list.values('source').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Clients by status
    clients_by_status = client_list.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent clients
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    recent_clients_7d = client_list.filter(created_at__gte=last_7_days).count()
    recent_clients_30d = client_list.filter(created_at__gte=last_30_days).count()
    
    # Source counts
    whatsapp_clients = client_list.filter(source='WhatsApp').count()
    email_clients = client_list.filter(source='Email').count()
    website_clients = client_list.filter(Q(source='Website') | Q(source='')).count()
    
    # Status counts
    new_clients = client_list.filter(status='New').count()
    contacted_clients = client_list.filter(status__icontains='Contact').count()
    qualified_clients = client_list.filter(status__icontains='Qualif').count()
    converted_clients = client_list.filter(status__icontains='Convert').count()
    
    # Products interested breakdown
    products_interested = client_list.values('product_interested').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Get unique status values for filter
    status_choices = client_list.values_list('status', flat=True).distinct()
    
    # Get unique source values for filter
    source_choices = client_list.values_list('source', flat=True).distinct()
    
    # Show 20 clients per page for better overview
    paginator = Paginator(client_list, 20) 
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    
    context = {
        'clients': clients,
        'total_clients': total_clients,
        'clients_by_source': clients_by_source,
        'clients_by_status': clients_by_status,
        'recent_clients_7d': recent_clients_7d,
        'recent_clients_30d': recent_clients_30d,
        'whatsapp_clients': whatsapp_clients,
        'email_clients': email_clients,
        'website_clients': website_clients,
        'new_clients': new_clients,
        'contacted_clients': contacted_clients,
        'qualified_clients': qualified_clients,
        'converted_clients': converted_clients,
        'products_interested': products_interested,
        'status_choices': status_choices,
        'source_choices': source_choices,
    }
    
    return render(request, 'dashboard/clients.html', context)

@login_required(login_url='login')
def delete_client(request, client_id):
    # Handle bulk delete chain if requested
    bulk_ids = request.GET.get('bulk', '')
    current_index = int(request.GET.get('index', -1))
    
    # Try to delete the client (might already be deleted in bulk operation)
    try:
        client = Client.objects.get(id=client_id)
        client_name = client.name
        client.delete()
        deleted = True
    except Client.DoesNotExist:
        # Client already deleted or doesn't exist, skip it
        deleted = False
        client_name = None
    
    if bulk_ids and current_index >= 0:
        # This is part of a bulk delete operation
        ids_list = [id.strip() for id in bulk_ids.split(',') if id.strip()]
        current_index += 1
        
        # Find next valid client ID to delete
        while current_index < len(ids_list):
            next_id = ids_list[current_index]
            # Check if this client still exists before trying to delete it
            if Client.objects.filter(id=next_id).exists():
                return redirect('/dashboard/clients/delete/' + next_id + '/?bulk=' + bulk_ids + '&index=' + str(current_index))
            current_index += 1
        
        # All done with bulk delete (or all remaining clients already deleted)
        total_requested = len(ids_list)
        messages.success(request, f'{total_requested} client(s) processed successfully.')
        return redirect('dash_clients')
    else:
        # Single delete
        if deleted:
            messages.success(request, f'Client "{client_name}" has been deleted successfully.')
        else:
            messages.warning(request, 'Client was not found or already deleted.')
        return redirect('dash_clients')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Import your models (Adjust 'portfolio' and 'core' if your app names differ)



@login_required(login_url='login')
def dashboard(request):
    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from datetime import timedelta, datetime
    
    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(seconds=1)
    this_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    
    # --- 1. CORE KPI COUNTS ---
    total_products = Product.objects.count()
    total_clients = Client.objects.count()
    total_services = ServiceItem.objects.count()
    unread_msgs = ContactMessage.objects.filter(is_read=False).count()
    
    # --- 2. NEW FEATURES DATA (Projects & Content) ---
    total_projects = Project.objects.count()
    total_news = NewsItem.objects.count()
    total_subscribers = Subscriber.objects.count()

    # --- 3. CHART DATA: Invoice Status ---
    paid_inv = Invoice.objects.filter(status='Paid').count()
    unpaid_inv = Invoice.objects.filter(status='Unpaid').count()
    overdue_inv = Invoice.objects.filter(status='Unpaid', created_at__lt=last_30_days).count()

    # --- 4. CHART DATA: Lead Source ---
    wa_leads = Client.objects.filter(source='WhatsApp').count()
    email_leads = Client.objects.filter(source='Email').count()

    # --- 5. RECENT ACTIVITY ---
    recent_leads = Client.objects.all().order_by('-created_at')[:5]
    
    # --- 6. TRENDS & COMPARISONS (This Month vs Last Month) ---
    products_this_month = Product.objects.filter(created_at__gte=this_month_start).count()
    products_last_month = Product.objects.filter(created_at__gte=last_month_start, created_at__lt=this_month_start).count()
    products_trend = ((products_this_month - products_last_month) / products_last_month * 100) if products_last_month > 0 else 0
    
    clients_this_month = Client.objects.filter(created_at__gte=this_month_start).count()
    clients_last_month = Client.objects.filter(created_at__gte=last_month_start, created_at__lt=this_month_start).count()
    clients_trend = ((clients_this_month - clients_last_month) / clients_last_month * 100) if clients_last_month > 0 else 0
    
    projects_this_month = Project.objects.filter(created_at__gte=this_month_start).count()
    projects_last_month = Project.objects.filter(created_at__gte=last_month_start, created_at__lt=this_month_start).count()
    projects_trend = ((projects_this_month - projects_last_month) / projects_last_month * 100) if projects_last_month > 0 else 0
    
    # Revenue calculations
    revenue_this_month = Invoice.objects.filter(status='Paid', created_at__gte=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_last_month = Invoice.objects.filter(status='Paid', created_at__gte=last_month_start, created_at__lt=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    revenue_trend = ((float(revenue_this_month) - float(revenue_last_month)) / float(revenue_last_month) * 100) if revenue_last_month > 0 else 0
    
    total_revenue = Invoice.objects.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Messages trend
    msgs_this_month = ContactMessage.objects.filter(created_at__gte=this_month_start).count()
    msgs_last_month = ContactMessage.objects.filter(created_at__gte=last_month_start, created_at__lt=this_month_start).count()
    msgs_trend = ((msgs_this_month - msgs_last_month) / msgs_last_month * 100) if msgs_last_month > 0 else 0
    
    subscribers_this_month = Subscriber.objects.filter(created_at__gte=this_month_start).count()
    subscribers_last_month = Subscriber.objects.filter(created_at__gte=last_month_start, created_at__lt=this_month_start).count()
    subscribers_trend = ((subscribers_this_month - subscribers_last_month) / subscribers_last_month * 100) if subscribers_last_month > 0 else 0

    # --- 7. REVENUE TRENDS (Last 6 Months) ---
    revenue_by_month = []
    for i in range(5, -1, -1):
        month_start = (this_month_start - timedelta(days=30*i)).replace(day=1)
        next_month_start = (month_start + timedelta(days=32)).replace(day=1)
        month_revenue = Invoice.objects.filter(
            status='Paid',
            created_at__gte=month_start,
            created_at__lt=next_month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_by_month.append(float(month_revenue))
    
    # --- 8. CONVERSION FUNNEL ---
    total_contacts = ContactMessage.objects.count()
    total_leads = Client.objects.count()
    total_invoices = Invoice.objects.count()
    total_paid = Invoice.objects.filter(status='Paid').count()
    
    conversion_leads = (total_leads / total_contacts * 100) if total_contacts > 0 else 0
    conversion_invoices = (total_invoices / total_leads * 100) if total_leads > 0 else 0
    conversion_paid = (total_paid / total_invoices * 100) if total_invoices > 0 else 0
    
    # --- 9. RECENT ACTIVITY FEED ---
    recent_activities = []
    # Recent clients
    for client in Client.objects.all().order_by('-created_at')[:3]:
        recent_activities.append({
            'type': 'client',
            'icon': 'bi-person-plus',
            'color': '#2ecc71',
            'message': f'New lead: {client.name}',
            'time': client.created_at,
            'url': '/dashboard/clients/'
        })
    # Recent invoices
    for invoice in Invoice.objects.all().order_by('-created_at')[:2]:
        recent_activities.append({
            'type': 'invoice',
            'icon': 'bi-receipt',
            'color': '#3498db',
            'message': f'Invoice {invoice.invoice_id}: ${invoice.amount}',
            'time': invoice.created_at,
            'url': '/dashboard/invoices/'
        })
    # Recent messages
    for msg in ContactMessage.objects.all().order_by('-created_at')[:2]:
        recent_activities.append({
            'type': 'message',
            'icon': 'bi-envelope',
            'color': '#f39c12',
            'message': f'Message from {msg.name}',
            'time': msg.created_at,
            'url': '/dashboard/logs/'
        })
    # Sort by time and take most recent 5
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:5]

    # --- 10. SMART ALERTS ---
    alerts = []
    if overdue_inv > 0:
        alerts.append({
            'type': 'warning',
            'icon': 'bi-exclamation-triangle',
            'title': f'{overdue_inv} Overdue Invoice(s)',
            'message': 'Invoices unpaid for over 30 days',
            'url': '/dashboard/invoices/',
            'priority': 'high'
        })
    if unread_msgs > 0:
        alerts.append({
            'type': 'info',
            'icon': 'bi-envelope',
            'title': f'{unread_msgs} Unread Message(s)',
            'message': 'New contact messages require attention',
            'url': '/dashboard/logs/',
            'priority': 'medium' if unread_msgs < 5 else 'high'
        })
    
    # --- 11. GOAL TRACKING (Example goals - can be made configurable) ---
    revenue_goal = 50000  # $50k monthly goal
    clients_goal = 20  # 20 new clients monthly goal
    revenue_progress = min((float(revenue_this_month) / revenue_goal * 100), 100)
    clients_progress = min((clients_this_month / clients_goal * 100), 100)

    context = {
        # Old Data
        'total_products': total_products,
        'total_clients': total_clients,
        'total_services': total_services,
        'unread_msgs': unread_msgs,
        
        # New Data
        'total_projects': total_projects,
        'total_news': total_news,
        'total_subscribers': total_subscribers,
        
        # Charts & Tables
        'recent_leads': recent_leads,
        'paid_inv': paid_inv,
        'unpaid_inv': unpaid_inv,
        'overdue_inv': overdue_inv,
        'wa_leads': wa_leads,
        'email_leads': email_leads,
        
        # Trends
        'products_trend': products_trend,
        'clients_trend': clients_trend,
        'projects_trend': projects_trend,
        'revenue_trend': revenue_trend,
        'msgs_trend': msgs_trend,
        'subscribers_trend': subscribers_trend,
        
        # Revenue
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        'revenue_by_month': revenue_by_month,
        
        # Conversion Funnel
        'conversion_leads': conversion_leads,
        'conversion_invoices': conversion_invoices,
        'conversion_paid': conversion_paid,
        'total_contacts': total_contacts,
        'total_leads': total_leads,
        'total_invoices': total_invoices,
        'total_paid': total_paid,
        
        # Activity & Alerts
        'recent_activities': recent_activities,
        'alerts': alerts,
        
        # Goals
        'revenue_goal': revenue_goal,
        'clients_goal': clients_goal,
        'revenue_progress': revenue_progress,
        'clients_progress': clients_progress,
    }
    return render(request, 'dashboard.html', context)

# In views.py

# 1. Dashboard List of Invoices
@login_required(login_url='login')
def dash_invoices(request):
    from django.db.models import Count, Sum, Avg, Q
    from django.utils import timezone
    from datetime import timedelta
    
    invoices = Invoice.objects.all().order_by('-created_at')
    clients = Client.objects.all()
    products = Product.objects.all()
    
    # Statistics
    total_invoices = invoices.count()
    
    # Revenue statistics
    total_revenue = invoices.filter(status='Paid').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_revenue = invoices.filter(status='Unpaid').aggregate(Sum('amount'))['amount__sum'] or 0
    avg_invoice_amount = invoices.aggregate(Avg('amount'))['amount__avg'] or 0
    
    # Status counts
    paid_invoices = invoices.filter(status='Paid').count()
    unpaid_invoices = invoices.filter(status='Unpaid').count()
    
    # Conversion rate
    conversion_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
    
    # Recent invoices
    now = timezone.now()
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(seconds=1)
    
    recent_invoices_7d = invoices.filter(created_at__gte=last_7_days).count()
    recent_invoices_30d = invoices.filter(created_at__gte=last_30_days).count()
    
    # Monthly revenue
    this_month_revenue = invoices.filter(status='Paid', created_at__gte=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    last_month_revenue = invoices.filter(status='Paid', created_at__gte=last_month_start, created_at__lt=this_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Revenue trend (last 6 months) - for chart
    revenue_by_month = []
    revenue_months = []
    revenue_data = []
    for i in range(5, -1, -1):
        month_start = (this_month_start - timedelta(days=30*i)).replace(day=1)
        next_month_start = (month_start + timedelta(days=32)).replace(day=1)
        month_revenue = invoices.filter(
            status='Paid',
            created_at__gte=month_start,
            created_at__lt=next_month_start
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_by_month.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(month_revenue)
        })
        revenue_months.append(month_start.strftime('%b'))
        revenue_data.append(float(month_revenue))
    
    # Top clients by revenue
    top_clients = invoices.filter(status='Paid').values('client__name').annotate(
        total_revenue=Sum('amount'),
        invoice_count=Count('id')
    ).order_by('-total_revenue')[:5]
    
    # Product revenue breakdown
    product_revenue = invoices.filter(status='Paid').values('product_name').annotate(
        total_revenue=Sum('amount'),
        count=Count('id')
    ).order_by('-total_revenue')[:10]
    
    # Overdue invoices (unpaid invoices older than 30 days)
    overdue_threshold = now - timedelta(days=30)
    overdue_invoices = invoices.filter(status='Unpaid', created_at__lt=overdue_threshold).count()
    overdue_amount = invoices.filter(status='Unpaid', created_at__lt=overdue_threshold).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Import json for chart data
    import json
    
    context = {
        'invoices': invoices,
        'clients': clients,
        'products': products,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'avg_invoice_amount': avg_invoice_amount,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'conversion_rate': conversion_rate,
        'recent_invoices_7d': recent_invoices_7d,
        'recent_invoices_30d': recent_invoices_30d,
        'this_month_revenue': this_month_revenue,
        'last_month_revenue': last_month_revenue,
        'revenue_by_month': revenue_by_month,
        'revenue_months': json.dumps(revenue_months),
        'revenue_data': json.dumps(revenue_data),
        'top_clients': top_clients,
        'product_revenue': product_revenue,
        'overdue_invoices': overdue_invoices,
        'overdue_amount': overdue_amount,
        'now': now,
    }
    
    return render(request, 'dashboard/invoices.html', context)

@login_required(login_url='login')
def create_invoice(request):
    if request.method == 'POST':
        # 1. Get data from the form
        client_id = request.POST.get('client')
        amount = request.POST.get('amount')
        product_id = request.POST.get('product') # Get the ID from the dropdown
        
        # 2. Fetch the actual objects from the database
        client = Client.objects.get(id=client_id)
        product_obj = Product.objects.get(id=product_id)
        
        # 3. Create the Invoice
        Invoice.objects.create(
            client=client,
            amount=amount,
            product=product_obj,           # Save the link to the product (for the file)
            product_name=product_obj.title # Auto-fill the name from the product title
        )
        
        messages.success(request, 'Invoice generated successfully!')
        return redirect('dash_invoices')
    
# 3. Mark Invoice as Paid
@login_required(login_url='login')
def update_invoice_status(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            if new_status in ['Paid', 'Unpaid']:
                invoice.status = new_status
                invoice.save()
                messages.success(request, f'Invoice {invoice.invoice_id} marked as {new_status}.')
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'})
        except:
            # Fallback: toggle status for GET requests or old format
            if invoice.status == 'Unpaid':
                invoice.status = 'Paid'
                messages.success(request, f'Invoice {invoice.invoice_id} marked as PAID.')
            else:
                invoice.status = 'Unpaid'
                messages.warning(request, f'Invoice {invoice.invoice_id} marked as UNPAID.')
            invoice.save()
            return redirect('dash_invoices')
    else:
        # For GET requests, toggle status (backward compatibility)
        if invoice.status == 'Unpaid':
            invoice.status = 'Paid'
            messages.success(request, f'Invoice {invoice.invoice_id} marked as PAID.')
        else:
            invoice.status = 'Unpaid'
            messages.warning(request, f'Invoice {invoice.invoice_id} marked as UNPAID.')
        invoice.save()
        return redirect('dash_invoices')

# 4. PUBLIC VIEW (What the client sees)
# No login required here so clients can view it via link
def view_invoice(request, invoice_id):
    invoice = Invoice.objects.get(invoice_id=invoice_id)
    return render(request, 'invoice_viewer.html', {'invoice': invoice})


def services(request):
    # Fetch categories ordered by the 'order' field
    # We use 'prefetch_related' to optimize database queries for the nested loop
    categories = ServiceCategory.objects.prefetch_related('services__tags').all()
    
    return render(request, 'services.html', {'categories': categories})


# 1. LIST SERVICES
@login_required(login_url='login')
def dash_services(request):
    from django.db.models import Count
    services = ServiceItem.objects.all().order_by('-created_at')
    categories = ServiceCategory.objects.annotate(service_count=Count('services')).all()
    
    # Statistics
    total_services = services.count()
    services_by_category = {}
    all_tags = []
    for service in services:
        category_name = service.category.title
        services_by_category[category_name] = services_by_category.get(category_name, 0) + 1
        all_tags.extend([tag.name for tag in service.tags.all()])
    
    # Most used tags
    from collections import Counter
    tag_counts = Counter(all_tags)
    most_used_tags = dict(tag_counts.most_common(10))
    
    return render(request, 'dashboard/services.html', {
        'services': services,
        'categories': categories,
        'total_services': total_services,
        'services_by_category': services_by_category,
        'most_used_tags': most_used_tags,
    })

# In views.py

@login_required(login_url='login')
def create_service(request):
    if request.method == 'POST':
        form = ServiceItemForm(request.POST, request.FILES)
        formset = ServiceTagFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            # 1. Save the Service first (Parent)
            service = form.save() 
            
            # 2. Prepare the tags but don't save to DB yet
            tags = formset.save(commit=False)
            
            # 3. Link each tag to the newly created service
            for tag in tags:
                tag.service = service
                tag.save() # Now safe to save!
            
            # 4. Handle deleted tags (if any)
            formset.save_m2m() # Required for some formset types, good practice
            
            messages.success(request, 'Service created successfully!')
            return redirect('dash_services')
    else:
        form = ServiceItemForm()
        formset = ServiceTagFormSet()

    return render(request, 'dashboard/service_form.html', {
        'form': form, 'formset': formset, 'title': 'Add New Service'
    })

# 3. EDIT SERVICE
@login_required(login_url='login')
def edit_service(request, service_id):
    service = get_object_or_404(ServiceItem, id=service_id)
    
    if request.method == 'POST':
        form = ServiceItemForm(request.POST, request.FILES, instance=service)
        # Pass 'instance=service' so it knows which tags to load
        formset = ServiceTagFormSet(request.POST, instance=service)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('dash_services')
    else:
        form = ServiceItemForm(instance=service)
        formset = ServiceTagFormSet(instance=service)

    return render(request, 'dashboard/service_form.html', {
        'form': form, 'formset': formset, 'title': f'Edit: {service.title}'
    })

# 4. DELETE SERVICE
@login_required(login_url='login')
def delete_service(request, service_id):
    service = get_object_or_404(ServiceItem, id=service_id)
    service.delete()
    messages.success(request, 'Service deleted successfully.')
    return redirect('dash_services')


# 1. Update the Public Contact View
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        channel = request.POST.get('channel', 'quick')
        
        # Build full message with additional context
        full_message = message
        if request.POST.get('company'):
            full_message = f"Company: {request.POST.get('company')}\n\n{full_message}"
        if request.POST.get('industry'):
            full_message = f"Industry: {request.POST.get('industry')}\n\n{full_message}"
        if request.POST.get('budget'):
            full_message = f"Budget: {request.POST.get('budget')}\n\n{full_message}"
        if request.POST.get('video_link'):
            full_message = f"Video: {request.POST.get('video_link')}\n\n{full_message}"
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=f"[{channel.upper()}] {subject}" if subject else f"[{channel.upper()}] Contact Inquiry",
            message=full_message
        )
        messages.success(request, 'Message sent! We will contact you shortly.')
        return redirect('contact')
        
    # Pass projects for portfolio matcher
    projects = Project.objects.all().order_by('-completed_date')[:6]
    return render(request, 'contact.html', {'projects': projects})

# 2. Update the Dashboard Logs View (To see the messages)
@login_required(login_url='login')
def dash_logs(request):
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get all messages
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    # Statistics
    total_messages = messages_list.count()
    unread_messages = messages_list.filter(is_read=False).count()
    read_messages = messages_list.filter(is_read=True).count()
    
    # Time-based statistics
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    messages_today = messages_list.filter(created_at__gte=today_start).count()
    messages_this_week = messages_list.filter(created_at__gte=week_start).count()
    messages_this_month = messages_list.filter(created_at__gte=month_start).count()
    
    # Messages by sender (most frequent)
    most_frequent_senders = messages_list.values('email', 'name').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Subject keywords analysis (most common subjects)
    common_subjects = messages_list.values('subject').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    contact_messages = paginator.get_page(page_number)
    
    context = {
        'contact_messages': contact_messages,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'read_messages': read_messages,
        'messages_today': messages_today,
        'messages_this_week': messages_this_week,
        'messages_this_month': messages_this_month,
        'most_frequent_senders': most_frequent_senders,
        'common_subjects': common_subjects,
    }
    
    return render(request, 'dashboard/logs.html', context)


@login_required(login_url='login')
def mark_message_read(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = True
    message.save()
    messages.success(request, 'Message marked as read.')
    return redirect('dash_logs')


@login_required(login_url='login')
def mark_message_unread(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.is_read = False
    message.save()
    messages.success(request, 'Message marked as unread.')
    return redirect('dash_logs')


@login_required(login_url='login')
def delete_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.delete()
    messages.success(request, 'Message deleted successfully.')
    return redirect('dash_logs')


@login_required(login_url='login')
def bulk_mark_read(request):
    if request.method == 'POST':
        message_ids_str = request.POST.get('message_ids', '')
        if message_ids_str:
            message_ids = [int(id) for id in message_ids_str.split(',') if id.strip()]
            ContactMessage.objects.filter(id__in=message_ids).update(is_read=True)
            messages.success(request, f'{len(message_ids)} message(s) marked as read.')
        else:
            message_ids = request.POST.getlist('message_ids')
            if message_ids:
                ContactMessage.objects.filter(id__in=message_ids).update(is_read=True)
                messages.success(request, f'{len(message_ids)} message(s) marked as read.')
    return redirect('dash_logs')


@login_required(login_url='login')
def bulk_mark_unread(request):
    if request.method == 'POST':
        message_ids_str = request.POST.get('message_ids', '')
        if message_ids_str:
            message_ids = [int(id) for id in message_ids_str.split(',') if id.strip()]
            ContactMessage.objects.filter(id__in=message_ids).update(is_read=False)
            messages.success(request, f'{len(message_ids)} message(s) marked as unread.')
        else:
            message_ids = request.POST.getlist('message_ids')
            if message_ids:
                ContactMessage.objects.filter(id__in=message_ids).update(is_read=False)
                messages.success(request, f'{len(message_ids)} message(s) marked as unread.')
    return redirect('dash_logs')


@login_required(login_url='login')
def bulk_delete_messages(request):
    if request.method == 'POST':
        message_ids_str = request.POST.get('message_ids', '')
        if message_ids_str:
            message_ids = [int(id) for id in message_ids_str.split(',') if id.strip()]
            ContactMessage.objects.filter(id__in=message_ids).delete()
            messages.success(request, f'{len(message_ids)} message(s) deleted successfully.')
        else:
            message_ids = request.POST.getlist('message_ids')
            if message_ids:
                ContactMessage.objects.filter(id__in=message_ids).delete()
                messages.success(request, f'{len(message_ids)} message(s) deleted successfully.')
    return redirect('dash_logs')


from .models import Project

def portfolio(request):
    # Fetch all projects, ordered by newest completion date
    projects = Project.objects.all().order_by('-completed_date')
    return render(request, 'portfolio.html', {'projects': projects})


from django.shortcuts import render, get_object_or_404
from .models import Project

def project_detail(request, project_id):
    # Fetch the specific project
    project = get_object_or_404(Project, id=project_id)
    
    # The template can access project.gallery.all due to the related_name we set in models
    return render(request, 'project_detail.html', {'project': project})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import NewsItem
from .forms import NewsItemForm

# views.py
from .models import NewsItem, Subscriber # Import Subscriber

@staff_member_required
@login_required(login_url='login')
def dash_news(request):
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    from collections import Counter
    
    # 1. Get News
    news_items = NewsItem.objects.all().order_by('-created_at')
    
    # 2. Get Subscribers
    subscribers = Subscriber.objects.all().order_by('-created_at')
    
    # Statistics
    total_articles = news_items.count()
    articles_by_category = {}
    articles_with_links = news_items.filter(external_link__isnull=False).exclude(external_link='').count()
    articles_without_links = total_articles - articles_with_links
    
    # Articles by category
    for category_code, category_name in NewsItem.CATEGORY_CHOICES:
        count = news_items.filter(category=category_code).count()
        articles_by_category[category_name] = count
    
    # Recent articles (last 7 and 30 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_articles_7d = news_items.filter(created_at__gte=seven_days_ago).count()
    recent_articles_30d = news_items.filter(created_at__gte=thirty_days_ago).count()
    
    # Subscriber statistics
    total_subscribers = subscribers.count()
    recent_subscribers_7d = subscribers.filter(created_at__gte=seven_days_ago).count()
    recent_subscribers_30d = subscribers.filter(created_at__gte=thirty_days_ago).count()
    
    # Get unique email domains
    email_domains = {}
    for sub in subscribers:
        domain = sub.email.split('@')[-1] if '@' in sub.email else 'unknown'
        email_domains[domain] = email_domains.get(domain, 0) + 1
    top_domains = dict(sorted(email_domains.items(), key=lambda x: x[1], reverse=True)[:5])
    
    # Get category choices for filter
    category_choices = NewsItem.CATEGORY_CHOICES
    
    context = {
        'news_items': news_items, 
        'subscribers': subscribers,
        'total_articles': total_articles,
        'articles_by_category': articles_by_category,
        'articles_with_links': articles_with_links,
        'articles_without_links': articles_without_links,
        'recent_articles_7d': recent_articles_7d,
        'recent_articles_30d': recent_articles_30d,
        'total_subscribers': total_subscribers,
        'recent_subscribers_7d': recent_subscribers_7d,
        'recent_subscribers_30d': recent_subscribers_30d,
        'top_domains': top_domains,
        'category_choices': category_choices,
    }
    
    return render(request, 'dashboard/dash_news.html', context)

# 2. ADD NEWS
@staff_member_required
def dash_news_add(request):
    if request.method == 'POST':
        form = NewsItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dash_news')
    else:
        form = NewsItemForm()
    return render(request, 'dashboard/dash_news_form.html', {'form': form, 'action': 'Add'})

# 3. DELETE NEWS
@staff_member_required
def dash_news_delete(request, pk):
    item = get_object_or_404(NewsItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('dash_news')
    return redirect('dash_news')


# views.py

def news_hub(request):
    # Get all news, newest first
    all_news = NewsItem.objects.all().order_by('-created_at')
    
    # Handle case where there is no news
    if not all_news:
        return render(request, 'news_hub.html', {'featured': None, 'news_list': []})

    # The first item is "Featured"
    featured = all_news[0]
    
    # The rest go into the grid
    news_list = all_news[1:]

    return render(request, 'news_hub.html', {
        'featured': featured,
        'news_list': news_list,
        'categories': NewsItem.CATEGORY_CHOICES # Pass categories for filter buttons
    })

# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Subscriber

@require_POST
def subscribe_newsletter(request):
    email = request.POST.get('email')
    
    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email is required.'})

    if Subscriber.objects.filter(email=email).exists():
        return JsonResponse({'status': 'error', 'message': 'You are already subscribed!'})

    # Save new subscriber
    Subscriber.objects.create(email=email)
    return JsonResponse({'status': 'success', 'message': 'Welcome to the inner circle!'})

import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

# ... existing dash_news view ...

# 1. EXPORT SUBSCRIBERS TO CSV
@staff_member_required
def dash_subscribers_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="wetech_subscribers.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Email', 'Date Joined']) 

    for sub in Subscriber.objects.all():
        writer.writerow([sub.email, sub.created_at.strftime("%Y-%m-%d %H:%M")])

    return response

# 2. DELETE SUBSCRIBER
@staff_member_required
def dash_subscriber_delete(request, pk):
    sub = get_object_or_404(Subscriber, pk=pk)
    if request.method == 'POST':
        sub.delete()
    # Redirect back to the NEWS dashboard, since they are merged now
    return redirect('dash_news')


# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ProjectEstimate
import json

def calculator(request):
    return render(request, 'calculator.html')

@csrf_exempt # Simple for this example, but standard CSRF is better for prod
def save_estimate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Create the record
        estimate = ProjectEstimate.objects.create(
            platform=", ".join(data.get('platforms', [])),
            features=", ".join(data.get('features', [])),
            design_level=data.get('design_level'),
            estimated_price=data.get('total_price'),
            # email=data.get('email') # If you add an email field later
        )
        
        return JsonResponse({'status': 'success', 'id': estimate.id})
    return JsonResponse({'status': 'error'})


from .forms import ProjectForm, ProjectImageFormSet
from .models import Project

# 1. LIST PROJECTS
@login_required(login_url='login')
def dash_projects(request):
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    projects = Project.objects.all().order_by('-completed_date')
    
    # Statistics
    total_projects = projects.count()
    projects_by_category = {}
    projects_with_links = projects.filter(live_link__isnull=False).exclude(live_link='').count()
    projects_without_links = total_projects - projects_with_links
    
    # Projects by category
    for category_code, category_name in Project.CATEGORY_CHOICES:
        count = projects.filter(category=category_code).count()
        projects_by_category[category_name] = count
    
    # Recent projects (last 30 days)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    recent_projects = projects.filter(completed_date__gte=thirty_days_ago).count()
    
    # Gallery images count (projects with gallery images)
    projects_with_gallery = Project.objects.annotate(gallery_count=Count('gallery')).filter(gallery_count__gt=0).count()
    
    # Get unique clients
    unique_clients = projects.values('client_name').distinct().count()
    
    # Get all unique clients for filter
    all_clients = projects.values_list('client_name', flat=True).distinct().order_by('client_name')
    
    # Get category choices
    category_choices = Project.CATEGORY_CHOICES
    
    return render(request, 'dashboard/projects.html', {
        'projects': projects,
        'total_projects': total_projects,
        'projects_by_category': projects_by_category,
        'projects_with_links': projects_with_links,
        'projects_without_links': projects_without_links,
        'recent_projects': recent_projects,
        'projects_with_gallery': projects_with_gallery,
        'unique_clients': unique_clients,
        'all_clients': all_clients,
        'category_choices': category_choices,
    })

# 2. CREATE PROJECT
@login_required(login_url='login')
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        formset = ProjectImageFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            # Save parent project first to get primary key
            project = form.save()
            
            # Set the instance for the formset
            formset.instance = project
            # Save formset - Django will handle empty forms automatically
            formset.save()
            
            messages.success(request, 'Project uploaded successfully!')
            return redirect('dash_projects')
    else:
        form = ProjectForm()
        formset = ProjectImageFormSet()

    return render(request, 'dashboard/project_form.html', {
        'form': form, 'formset': formset, 'title': 'Upload New Project'
    })

# 3. EDIT PROJECT
@login_required(login_url='login')
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        formset = ProjectImageFormSet(request.POST, request.FILES, instance=project)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('dash_projects')
    else:
        form = ProjectForm(instance=project)
        formset = ProjectImageFormSet(instance=project)

    return render(request, 'dashboard/project_form.html', {
        'form': form, 'formset': formset, 'title': f'Edit: {project.title}'
    })

# 4. DELETE PROJECT
@login_required(login_url='login')
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    messages.success(request, 'Project deleted successfully.')
    return redirect('dash_projects')








from .models import Invoice
from .pesapal import Pesapal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
# In views.py

def pay_with_pesapal(request, invoice_id):
    from wetech.utils.logger import logger
    
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    pesapal = Pesapal()
    
    logger.info(f"Pesapal payment initiated", extra={
        'invoice_id': invoice.invoice_id,
        'amount': float(invoice.amount),
        'client_id': invoice.client.id if invoice.client else None
    })

    try:
        # A. Authenticate
        logger.debug("Attempting to get Pesapal access token")
        try:
            result = pesapal.get_access_token()
            # Ensure we got a tuple back
            if not isinstance(result, tuple) or len(result) != 2:
                logger.error("Pesapal authentication: Invalid response format", extra={'invoice_id': invoice.invoice_id})
                messages.error(request, "Pesapal Connection Failed: Invalid response from authentication")
                return redirect('view_invoice', invoice_id=invoice.invoice_id)
            token, error_message = result
        except Exception as auth_error:
            # If get_access_token itself raises an exception
            error_display = f"Authentication error: {str(auth_error)}"
            logger.error(f"Pesapal authentication exception: {error_display}", exc_info=True, extra={'invoice_id': invoice.invoice_id})
            messages.error(request, f"Pesapal Connection Failed: {error_display}")
            return redirect('view_invoice', invoice_id=invoice.invoice_id)
        
        if not token:
            # Show the actual error message to help diagnose the issue
            error_display = error_message if error_message else "Unknown error occurred"
            logger.error(f"Pesapal authentication failed: {error_display}", extra={'invoice_id': invoice.invoice_id})
            messages.error(request, f"Pesapal Connection Failed: {error_display}")
            return redirect('view_invoice', invoice_id=invoice.invoice_id)
        
        logger.info("Pesapal authentication successful", extra={'invoice_id': invoice.invoice_id})

        # B. Register Callback URL
        callback_url = request.build_absolute_uri(reverse('pesapal_callback'))
        ipn_id = pesapal.register_ipn_url(token, callback_url)
        
        if not ipn_id:
            # If IPN fails, we proceed but warn
            logger.warning("IPN Registration failed. Proceeding anyway.", extra={'invoice_id': invoice.invoice_id})

        # C. Prepare Order
        order_data = {
            "id": invoice.invoice_id, 
            "currency": "TZS",
            "amount": float(invoice.amount),
            "description": f"Payment for {invoice.product_name}",
            "callback_url": callback_url,
            "notification_id": ipn_id,
            "billing_address": {
                "email_address": "tech@we-tech.com",
                "phone_number": invoice.client.contact_info if invoice.client.contact_info else "",
                "country_code": "TZ",
                "first_name": invoice.client.name,
                "middle_name": "",
                "last_name": ""
            }
        }

        # D. Submit
        response = pesapal.submit_order(token, order_data)
        
        # Safety check: ensure response is a dict
        if not response or not isinstance(response, dict):
            logger.error("Pesapal order submission: Invalid response", extra={'invoice_id': invoice.invoice_id})
            messages.error(request, "Pesapal Order Error: Invalid response from payment gateway")
            return redirect('view_invoice', invoice_id=invoice.invoice_id)
        
        if 'redirect_url' in response:
            logger.info("Pesapal payment redirect generated", extra={
                'invoice_id': invoice.invoice_id,
                'redirect_url': response['redirect_url']
            })
            return redirect(response['redirect_url'])
        else:
            # Show the specific error from Pesapal
            error_info = response.get('error', {})
            if isinstance(error_info, dict):
                err_msg = error_info.get('message', 'Unknown Error')
            else:
                err_msg = 'Unknown Error'
            logger.error(f"Pesapal order submission failed: {err_msg}", extra={'invoice_id': invoice.invoice_id})
            messages.error(request, f"Pesapal Order Error: {err_msg}")
            return redirect('view_invoice', invoice_id=invoice.invoice_id)

    except Exception as e:
        # Show the system crash error
        logger.error(f"Pesapal payment system error: {str(e)}", exc_info=True, extra={'invoice_id': invoice.invoice_id})
        messages.error(request, f"System Crash: {str(e)}")
        return redirect('view_invoice', invoice_id=invoice.invoice_id)
    
    
# 2. HANDLE CALLBACK (User comes back)
@transaction.atomic
def pesapal_callback(request):
    from wetech.utils.logger import logger
    from django.db import transaction
    
    order_tracking_id = request.GET.get('OrderTrackingId')
    merchant_reference = request.GET.get('OrderMerchantReference')

    logger.info("Pesapal callback received", extra={
        'order_tracking_id': order_tracking_id,
        'merchant_reference': merchant_reference
    })

    if not order_tracking_id or not merchant_reference:
        logger.warning("Pesapal callback missing required parameters")
        return redirect('home')

    # Verify Logic
    pesapal = Pesapal()
    token, error_message = pesapal.get_access_token()
    if not token:
        logger.error(f"Pesapal callback authentication failed: {error_message}", extra={'merchant_reference': merchant_reference})
        messages.error(request, f"Payment verification failed: {error_message or 'Could not authenticate with Pesapal'}")
        return redirect('home')
    
    status_data = pesapal.get_transaction_status(token, order_tracking_id)
    
    payment_status = status_data.get('payment_status_description') # "Completed", "Failed"

    try:
        invoice = Invoice.objects.get(invoice_id=merchant_reference)
        
        with transaction.atomic():
            if payment_status == 'Completed':
                invoice.status = 'Paid'
                invoice.save()
                logger.info(f"Payment verified and invoice marked as paid", extra={
                    'invoice_id': invoice.invoice_id,
                    'order_tracking_id': order_tracking_id
                })
                messages.success(request, "Payment Verified! Download unlocked.")
            elif payment_status == 'Failed':
                logger.warning(f"Payment failed", extra={
                    'invoice_id': invoice.invoice_id,
                    'order_tracking_id': order_tracking_id
                })
                messages.error(request, "Payment Failed.")
            else:
                # If "Pending", we still show message
                logger.info(f"Payment status: {payment_status}", extra={
                    'invoice_id': invoice.invoice_id,
                    'order_tracking_id': order_tracking_id
                })
                messages.info(request, f"Payment Status: {payment_status}")

        return redirect('view_invoice', invoice_id=invoice.invoice_id)

    except Invoice.DoesNotExist:
        logger.error(f"Invoice not found in callback: {merchant_reference}", extra={'merchant_reference': merchant_reference})
        return redirect('home')
    

# In views.py
from .azampay import AzamPayClient # <--- Import the new local file

# ... existing imports ...

def pay_with_azampay(request, invoice_id):
    invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
    
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        provider = request.POST.get('provider')
        
        # Initialize our custom client
        gateway = AzamPayClient()
        
        try:
            # Format phone: remove leading 0, ensure 255 prefix
            # AzamPay needs 2557xxxxxxxx
            clean_phone = phone.replace(' ', '').strip()
            if clean_phone.startswith('0'):
                clean_phone = '255' + clean_phone[1:]
            elif clean_phone.startswith('+255'):
                clean_phone = clean_phone[1:]
            
            # Trigger Payment
            result = gateway.mobile_checkout(
                mobile_number=clean_phone,
                amount=invoice.amount,
                external_id=invoice.invoice_id,
                provider=provider
            )
            
            if result['success']:
                messages.success(request, f"✅ Payment Request sent to {clean_phone}. Check your phone for the PIN popup.")
                
                # OPTIONAL: You can mark invoice as paid immediately if you trust the push,
                # BUT properly you should wait for a Callback (IPN).
                # For now, we wait for the user to confirm manually or refresh.
                
                return redirect('view_invoice', invoice_id=invoice.invoice_id)
            else:
                messages.error(request, f"Payment Failed: {result['message']}")
                return redirect('view_invoice', invoice_id=invoice.invoice_id)

        except Exception as e:
            messages.error(request, f"System Error: {str(e)}")
            return redirect('view_invoice', invoice_id=invoice.invoice_id)
            
    return redirect('view_invoice', invoice_id=invoice.invoice_id)


@csrf_exempt
@transaction.atomic
def save_lead(request):
    from wetech.utils.logger import logger
    from django.db import transaction
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info("Lead submission started", extra={
                'source': data.get('source'),
                'product_id': data.get('product_id'),
                'ip': request.META.get('REMOTE_ADDR')
            })
            
            with transaction.atomic():
                client = Client.objects.create(
                    name=data.get('name'),
                    contact_info=data.get('contact'),
                    product_interested=data.get('product'),
                    source=data.get('source')
                )
                logger.info(f"Client created: {client.id}", extra={'client_id': client.id, 'name': client.name})

                # Handle Payments (Both Pesapal and AzamPay)
                if data.get('source') in ['Pesapal', 'AzamPay']:
                    try:
                        product_id = data.get('product_id')
                        product = Product.objects.get(id=product_id)
                        
                        invoice = Invoice.objects.create(
                            client=client,
                            amount=product.price,
                            product=product,
                            product_name=product.title
                        )
                        logger.info(f"Invoice created: {invoice.invoice_id}", extra={
                            'invoice_id': invoice.invoice_id,
                            'amount': float(invoice.amount),
                            'client_id': client.id
                        })
                        
                        if data.get('source') == 'Pesapal':
                            # Redirect to Pesapal Payment Page (absolute URL)
                            payment_url = request.build_absolute_uri(reverse('pay_with_pesapal', args=[invoice.invoice_id]))
                        else:
                            # Redirect to Invoice Viewer (where the AzamPay modal is) - absolute URL
                            payment_url = request.build_absolute_uri(reverse('view_invoice', args=[invoice.invoice_id]))
                        
                        logger.info(f"Payment redirect generated", extra={
                            'invoice_id': invoice.invoice_id,
                            'source': data.get('source')
                        })
                        return JsonResponse({'status': 'redirect', 'url': payment_url})
                        
                    except Product.DoesNotExist:
                        logger.error(f"Product not found: {product_id}", extra={'product_id': product_id})
                        return JsonResponse({'status': 'error', 'message': 'Product not found'})

            logger.info("Lead submission completed successfully", extra={'client_id': client.id})
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in lead submission: {str(e)}", exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"Lead submission failed: {str(e)}", exc_info=True, extra={
                'data': data if 'data' in locals() else None
            })
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
@transaction.atomic
def azampay_callback(request):
    """
    AzamPay sends a POST request here when payment is complete.
    We read the data and mark invoice as Paid.
    """
    from wetech.utils.logger import logger
    from django.db import transaction
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info("AzamPay callback received", extra={'data': data})
            
            # Extract info (Adjust keys based on actual AzamPay response payload)
            # Usually: utilityRef (Invoice ID), transactionStatus
            invoice_id = data.get('utilityRef') 
            status = data.get('transactionStatus') 

            if status == 'success' or status == 'Success':
                with transaction.atomic():
                    invoice = Invoice.objects.get(invoice_id=invoice_id)
                    invoice.status = 'Paid'
                    invoice.save()
                    logger.info(f"Invoice marked as paid via AzamPay", extra={
                        'invoice_id': invoice_id,
                        'transaction_status': status
                    })
                
            return JsonResponse({'success': True})
        except json.JSONDecodeError as e:
            logger.error(f"AzamPay callback: Invalid JSON", exc_info=True)
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        except Invoice.DoesNotExist:
            logger.error(f"AzamPay callback: Invoice not found", extra={'invoice_id': invoice_id if 'invoice_id' in locals() else None})
            return JsonResponse({'success': False, 'error': 'Invoice not found'})
        except Exception as e:
            logger.error(f"AzamPay callback error: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ==========================================
# HEALTH CHECK ENDPOINTS
# ==========================================

def health_check(request):
    """
    Comprehensive health check endpoint
    
    Returns:
        - 200 OK: System is healthy
        - 503 Service Unavailable: System has issues
    
    Usage:
        GET /health/
    """
    from wetech.utils.logger import logger
    
    checks = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0',
        'checks': {}
    }
    
    # Database connectivity check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks['checks']['database'] = {
            'status': 'ok',
            'response_time_ms': 0
        }
    except Exception as e:
        checks['checks']['database'] = {
            'status': 'error',
            'error': str(e)
        }
        checks['status'] = 'unhealthy'
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
    
    # Disk space check
    try:
        total, used, free = shutil.disk_usage('/')
        disk_usage_percent = (used / total) * 100
        
        checks['checks']['disk'] = {
            'status': 'ok' if disk_usage_percent < 90 else 'warning',
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'used_percent': round(disk_usage_percent, 2)
        }
        
        if disk_usage_percent > 95:
            checks['status'] = 'unhealthy'
            logger.error(f"Disk space critical: {disk_usage_percent:.2f}% used")
        elif disk_usage_percent > 90:
            logger.warning(f"Disk space warning: {disk_usage_percent:.2f}% used")
    except Exception as e:
        checks['checks']['disk'] = {
            'status': 'error',
            'error': str(e)
        }
        logger.error(f"Disk check failed: {str(e)}", exc_info=True)
    
    # Media directory check
    try:
        media_path = settings.MEDIA_ROOT
        if os.path.exists(media_path):
            checks['checks']['media'] = {
                'status': 'ok',
                'path': media_path,
                'writable': os.access(media_path, os.W_OK)
            }
        else:
            checks['checks']['media'] = {
                'status': 'warning',
                'message': 'Media directory does not exist'
            }
    except Exception as e:
        checks['checks']['media'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Static files check
    try:
        static_dirs = settings.STATICFILES_DIRS
        checks['checks']['static'] = {
            'status': 'ok',
            'directories': len(static_dirs) if isinstance(static_dirs, list) else 1
        }
    except Exception as e:
        checks['checks']['static'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Determine HTTP status code
    status_code = 200 if checks['status'] == 'healthy' else 503
    
    return JsonResponse(checks, status=status_code)


def readiness_check(request):
    """
    Kubernetes/Docker readiness probe
    
    Checks if the application is ready to accept traffic
    """
    from wetech.utils.logger import logger
    
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({'status': 'ready'}, status=200)
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'not_ready', 'error': str(e)}, status=503)


def liveness_check(request):
    """
    Kubernetes/Docker liveness probe
    
    Checks if the application is alive (minimal check)
    """
    return JsonResponse({'status': 'alive'}, status=200)


# ==========================================
# SYSTEM STATUS DASHBOARD
# ==========================================

@login_required(login_url='login')
def dash_system_status(request):
    """System status and reliability dashboard"""
    from pathlib import Path
    from django.utils import timezone
    from datetime import timedelta
    from wetech.utils.logger import logger
    import os
    
    # Get system health data
    health_data = {}
    try:
        # Database check
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
    
    # Get recent activities from logs
    logs_dir = Path(settings.BASE_DIR) / 'logs'
    recent_activities = []
    
    # Get recent payment activities
    now = timezone.now()
    recent_invoices = Invoice.objects.all().order_by('-created_at')[:10]
    recent_payments = Invoice.objects.filter(status='Paid', created_at__gte=now - timedelta(days=7)).order_by('-created_at')[:5]
    
    # Get log file stats
    log_stats = {}
    if logs_dir.exists():
        app_log = logs_dir / 'app.log'
        error_log = logs_dir / 'errors.log'
        
        if app_log.exists():
            log_stats['app_log_size'] = round(app_log.stat().st_size / 1024, 2)  # KB
            log_stats['app_log_lines'] = sum(1 for _ in open(app_log, 'r', encoding='utf-8', errors='ignore'))
        
        if error_log.exists():
            log_stats['error_log_size'] = round(error_log.stat().st_size / 1024, 2)  # KB
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
    
    # Performance stats (slow requests from logs)
    slow_requests_today = 0
    if logs_dir.exists():
        app_log = logs_dir / 'app.log'
        if app_log.exists():
            today_str = timezone.now().strftime('%Y-%m-%d')
            try:
                with open(app_log, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if 'Slow request' in line and today_str in line:
                            slow_requests_today += 1
            except:
                pass
    
    # Error count today
    errors_today = 0
    if logs_dir.exists():
        error_log = logs_dir / 'errors.log'
        if error_log.exists():
            today_str = timezone.now().strftime('%Y-%m-%d')
            try:
                with open(error_log, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if today_str in line and 'ERROR' in line:
                            errors_today += 1
            except:
                pass
    
    context = {
        'health_data': health_data,
        'recent_invoices': recent_invoices,
        'recent_payments': recent_payments,
        'log_stats': log_stats,
        'backup_count': backup_count,
        'latest_backup': latest_backup,
        'slow_requests_today': slow_requests_today,
        'errors_today': errors_today,
    }
    
    return render(request, 'dashboard/system_status.html', context)


@login_required(login_url='login')
def dash_system_logs(request):
    """API endpoint to fetch recent logs"""
    from pathlib import Path
    
    logs_dir = Path(settings.BASE_DIR) / 'logs'
    app_log_path = logs_dir / 'app.log'
    error_log_path = logs_dir / 'errors.log'
    
    def get_last_lines(file_path, lines=20):
        """Get last N lines from a file"""
        try:
            if not file_path.exists():
                return "Log file not found"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:])
        except Exception as e:
            return f"Error reading log file: {str(e)}"
    
    return JsonResponse({
        'app_logs': get_last_lines(app_log_path),
        'error_logs': get_last_lines(error_log_path)
    })


@login_required(login_url='login')
def dash_system_backups(request):
    """API endpoint to list backups"""
    from pathlib import Path
    import os
    
    backups_dir = Path(settings.BASE_DIR) / 'backups'
    backups = []
    
    if backups_dir.exists():
        for file in sorted(backups_dir.glob('db_backup_*.sqlite3'), key=os.path.getmtime, reverse=True):
            stat = file.stat()
            size_mb = round(stat.st_size / (1024 * 1024), 2)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
            backups.append({
                'filename': file.name,
                'size': size_mb,
                'date': date,
                'path': str(file)
            })
    
    return JsonResponse({'backups': backups})


@login_required(login_url='login')
def dash_system_backup_create(request):
    """API endpoint to create a backup"""
    if request.method == 'POST':
        from django.core.management import call_command
        from io import StringIO
        from wetech.utils.logger import logger
        
        try:
            # Call the backup command
            out = StringIO()
            call_command('backup_db', stdout=out)
            result = out.getvalue()
            
            return JsonResponse({
                'success': True,
                'message': 'Backup created successfully',
                'output': result
            })
        except Exception as e:
            logger.error(f"Backup creation failed: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required(login_url='login')
def dash_system_backup_download(request, filename):
    """Download a backup file"""
    from pathlib import Path
    from django.http import FileResponse
    import os
    
    backups_dir = Path(settings.BASE_DIR) / 'backups'
    file_path = backups_dir / filename
    
    # Security check: ensure file is in backups directory
    if not file_path.exists() or not str(file_path).startswith(str(backups_dir)):
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound("Backup file not found")
    
    response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response