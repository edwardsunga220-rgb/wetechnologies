from django.urls import path
from django.contrib.auth import views as auth_views 
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('overview/', views.overview, name='overview'),
    path('services/', views.services, name='services'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('clients/', views.clients, name='clients'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('pricing/', views.pricing, name='pricing'),
    path('page-not-found/', views.custom_404, name='404'),
    path('marketplace/', views.marketplace, name='marketplace'),
    
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/products/', views.dash_products, name='dash_products'),
   
    path('dashboard/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('dashboard/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),

    path('dashboard/upload/', views.dash_upload, name='dash_upload'),
    path('dashboard/clients/', views.dash_clients, name='dash_clients'),
    path('dashboard/clients/delete/<int:client_id>/', views.delete_client, name='delete_client'),
    path('dashboard/invoices/', views.dash_invoices, name='dash_invoices'),
    path('dashboard/email/', views.dash_email, name='dash_email'),
    path('dashboard/logs/', views.dash_logs, name='dash_logs'),
    path('dashboard/logs/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('dashboard/logs/mark-unread/<int:message_id>/', views.mark_message_unread, name='mark_message_unread'),
    path('dashboard/logs/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('dashboard/logs/bulk-mark-read/', views.bulk_mark_read, name='bulk_mark_read'),
    path('dashboard/logs/bulk-mark-unread/', views.bulk_mark_unread, name='bulk_mark_unread'),
    path('dashboard/logs/bulk-delete/', views.bulk_delete_messages, name='bulk_delete_messages'),
    path('dashboard/settings/', views.dash_settings, name='dash_settings'),
    path('dashboard/system-status/', views.dash_system_status, name='dash_system_status'),
    path('dashboard/system-status/logs/', views.dash_system_logs, name='dash_system_logs'),
    path('dashboard/system-status/backups/', views.dash_system_backups, name='dash_system_backups'),
    path('dashboard/system-status/backups/create/', views.dash_system_backup_create, name='dash_system_backup_create'),
    path('dashboard/system-status/backups/download/<str:filename>/', views.dash_system_backup_download, name='dash_system_backup_download'),
    
  
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    path('save-lead/', views.save_lead, name='save_lead'),
    # In urls.py

# ... existing dashboard urls ...
path('dashboard/invoices/create/', views.create_invoice, name='create_invoice'),
path('dashboard/invoices/status/<int:invoice_id>/', views.update_invoice_status, name='update_invoice_status'),

# PUBLIC INVOICE URL (This is the link you send to WhatsApp)
path('invoice/<str:invoice_id>/', views.view_invoice, name='view_invoice'),

path('dashboard/services/', views.dash_services, name='dash_services'),
path('dashboard/services/create/', views.create_service, name='create_service'),
path('dashboard/services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
path('dashboard/services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
path('portfolio/project/<int:project_id>/', views.project_detail, name='project_detail'),


path('dashboard/news/', views.dash_news, name='dash_news'),
path('dashboard/news/add/', views.dash_news_add, name='dash_news_add'),
path('dashboard/news/delete/<int:pk>/', views.dash_news_delete, name='dash_news_delete'),

path('news/', views.news_hub, name='news_hub'),
path('subscribe/', views.subscribe_newsletter, name='subscribe'),
 path('dashboard/subscribers/delete/<int:pk>/', views.dash_subscriber_delete, name='dash_subscriber_delete'),
    path('dashboard/subscribers/export/', views.dash_subscribers_export, name='dash_subscribers_export'),
    # urls.py
path('calculator/', views.calculator, name='calculator'),
path('api/save-estimate/', views.save_estimate, name='save_estimate'),


     path('dashboard/projects/', views.dash_projects, name='dash_projects'),
path('dashboard/projects/create/', views.create_project, name='create_project'),
path('dashboard/projects/edit/<int:project_id>/', views.edit_project, name='edit_project'),
path('dashboard/projects/delete/<int:project_id>/', views.delete_project, name='delete_project'),


    path('payment/pesapal/pay/<str:invoice_id>/', views.pay_with_pesapal, name='pay_with_pesapal'),
    path('payment/pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),
    
    path('payment/azampay/pay/<str:invoice_id>/', views.pay_with_azampay, name='pay_with_azampay'),
    path('payment/azampay/callback/', views.azampay_callback, name='azampay_callback'),
    
    # Health check endpoints
    path('health/', views.health_check, name='health_check'),
    path('health/ready/', views.readiness_check, name='readiness_check'),
    path('health/live/', views.liveness_check, name='liveness_check'),
]