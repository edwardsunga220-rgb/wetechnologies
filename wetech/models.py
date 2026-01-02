import random
import string
from django.db import models
# ... rest of your imports

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('saas', 'SaaS Systems'),
        ('mobile', 'Mobile Source Code'),
        ('web', 'Web Templates'),
    ]

    title = models.CharField(max_length=200)
    # This category maps to your filter buttons (saas, mobile, web)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='web')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Optional: Show a crossed-out original price")
    
    image = models.ImageField(upload_to='products/')
    description = models.TextField(help_text="Short description of the system")
    
    # We will store features as a simple text, separated by commas
    features = models.TextField(help_text="Enter features separated by commas (e.g., Django Backend, Offline Mode, Multi-Store)")
    
    demo_link = models.URLField(blank=True, null=True, help_text="Link to the live preview")
    created_at = models.DateTimeField(auto_now_add=True)
    

    def get_features_list(self):
        # This helper function splits the text into a list for the template
        return [f.strip() for f in self.features.split(',')]

    def __str__(self):
        return self.title
    

    # In models.py

class Client(models.Model):
    # NOTICE: These lines must have 4 spaces at the start
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    product_interested = models.CharField(max_length=200)
    source = models.CharField(max_length=50, default='Website')
    status = models.CharField(max_length=20, default='New')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

    import random
import string
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
    ]

    # Link to the Client (Lead)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    
    # --- ADD THIS LINE HERE ---
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    # --------------------------

    # Link to the Product name (Keep this for display purposes)
    product_name = models.CharField(max_length=200)
    
    invoice_id = models.CharField(max_length=20, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate Invoice ID (e.g., INV-8392) if not exists
        if not self.invoice_id:
            self.invoice_id = 'INV-' + ''.join(random.choices(string.digits, k=4))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_id} - {self.client.name}"
    from django.db import models

# 1. The Tabs (e.g., Backend, Mobile, DevOps)
class ServiceCategory(models.Model):
    title = models.CharField(max_length=100) # e.g., "Backend Systems"
    slug = models.SlugField(unique=True, help_text="Unique ID for the tab (e.g., 'backend', 'mobile')") 
    icon = models.CharField(max_length=50, help_text="Bootstrap icon class (e.g., 'bi bi-server')")
    order = models.IntegerField(default=0, help_text="Order to display tabs")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

# 2. The Service Cards (e.g., Django Architecture)
class ServiceItem(models.Model):
    category = models.ForeignKey(ServiceCategory, related_name='services', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 3. The Tech Tags (e.g., Python, Redis)
class ServiceTag(models.Model):
    service = models.ForeignKey(ServiceItem, related_name='tags', on_delete=models.CASCADE)
    name = models.CharField(max_length=50) # e.g., "Python"
    icon = models.CharField(max_length=50, blank=True, default="bi bi-check2") 

    def __str__(self):
        return self.name
        

# ... (Your Product, Client, Invoice, Service models are above here) ...

# 1. CONTACT MESSAGE MODEL (No category choices here)
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

# 2. PROJECT MODEL (Category choices are defined HERE)
class Project(models.Model):
    # Definition must be ABOVE the field that uses it
    CATEGORY_CHOICES = [
        ('mobile', 'Mobile App'),
        ('web', 'Web System'),
        ('backend', 'Backend API'),
    ]

    title = models.CharField(max_length=200)
    # This refers to the list immediately above
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES) 
    client_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='portfolio/')
    description = models.TextField()
    live_link = models.URLField(blank=True, null=True, help_text="Link to the live site or app store")
    completed_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    # In models.py

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='portfolio/gallery/')
    
    def __str__(self):
        return f"Image for {self.project.title}"
    

    # models.py
from django.db import models

class NewsItem(models.Model):
    CATEGORY_CHOICES = [
        ('Backend', 'Backend'),
        ('Mobile', 'Mobile'),
        ('Cloud', 'Cloud'),
        ('AI', 'AI'),
        ('Security', 'Security'),
    ]

    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='news_images/')
    description = models.CharField(max_length=150, help_text="Short description for the menu")
    # If you have a detail page, use a SlugField. For now, we can use an external URL or blank.
    external_link = models.URLField(blank=True, null=True, help_text="Optional link to external article")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Shows newest first
        verbose_name = "News Item"
        verbose_name_plural = "News Items"

    def __str__(self):
        return self.title
    
    # models.py
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    

    # models.py

class ProjectEstimate(models.Model):
    PLATFORM_CHOICES = [
        ('Web App', 'Web App'),
        ('Mobile App', 'Mobile App'),
        ('Admin Panel', 'Admin Panel'),
        ('Combined', 'Combined System')
    ]

    # Contact Info (Optional at first, but good to capture)
    email = models.EmailField(blank=True, null=True)
    
    # Project Details
    platform = models.CharField(max_length=200) # e.g., "Web App, Mobile App"
    features = models.TextField() # e.g., "User Auth, Payments, Chat"
    design_level = models.CharField(max_length=50) # e.g., "Premium"
    
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Estimate: ${self.estimated_price} ({self.created_at.date()})"


# Email Templates Model
class EmailTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('welcome', 'Welcome'),
        ('follow-up', 'Follow-up'),
        ('invoice', 'Invoice'),
        ('product', 'Product'),
        ('custom', 'Custom'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='custom')
    subject = models.CharField(max_length=500)
    body = models.TextField(help_text="Use variables: {{name}}, {{product}}, {{date}}, {{company}}")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


# Sent Email History Model
class SentEmail(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    recipient = models.EmailField()
    recipient_name = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Email to {self.recipient} - {self.subject}"


# Business Settings Model (Singleton)
class BusinessSettings(models.Model):
    company_name = models.CharField(max_length=200, default='WeTech')
    company_email = models.EmailField(default='support@we-tech.com')
    company_phone = models.CharField(max_length=50, default='+255 777 749 824')
    company_address = models.TextField(default='Dar es Salaam, Tanzania\nInnovation Hub')
    
    class Meta:
        verbose_name = 'Business Settings'
        verbose_name_plural = 'Business Settings'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion, just reset to defaults
        pass
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return self.company_name