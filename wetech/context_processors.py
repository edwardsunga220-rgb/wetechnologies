# core/context_processors.py
from .models import NewsItem
from django.db import OperationalError, DatabaseError
from django.core.exceptions import ImproperlyConfigured

def navbar_news(request):
    # Fetch the latest 3 news items to display in the menu
    latest_news = NewsItem.objects.all()[:3] 
    return {
        'navbar_news_items': latest_news
    }

def business_settings(request):
    # Get business settings (singleton pattern)
    try:
        from .models import BusinessSettings
        # Use get_or_create to ensure the instance exists and always get fresh data
        business, created = BusinessSettings.objects.get_or_create(pk=1)
        # Refresh from database to ensure we have the latest values
        business.refresh_from_db()
        return {
            'business_settings': business,
            'company_name': business.company_name,
            'company_email': business.company_email,
            'company_phone': business.company_phone,
            'company_address': business.company_address,
        }
    except (OperationalError, DatabaseError) as e:
        # Database table doesn't exist yet (migrations not run)
        # Return defaults without crashing
        return {
            'business_settings': None,
            'company_name': 'WeTech',
            'company_email': 'support@we-tech.com',
            'company_phone': '+255 777 749 824',
            'company_address': 'Dar es Salaam, Tanzania\nInnovation Hub',
        }
    except Exception as e:
        # For any other unexpected error, log and return defaults
        # In production, you might want to log this
        return {
            'business_settings': None,
            'company_name': 'WeTech',
            'company_email': 'support@we-tech.com',
            'company_phone': '+255 777 749 824',
            'company_address': 'Dar es Salaam, Tanzania\nInnovation Hub',
        }