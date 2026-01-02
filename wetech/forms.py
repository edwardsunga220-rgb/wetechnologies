from django import forms
from .models import Product, Project, ProjectImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'price', 'old_price', 'image', 'description', 'features', 'demo_link']
        
        # We add CSS classes here to match your dark UI
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter System Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00 (Optional)'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short description...'}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Django, Offline Mode, Multi-Store...'}),
            'demo_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }


        from django.forms import inlineformset_factory
from .models import ServiceItem, ServiceTag, ServiceCategory

class ServiceItemForm(forms.ModelForm):
    class Meta:
        model = ServiceItem
        fields = ['category', 'title', 'description', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'cyber-input'}),
            'title': forms.TextInput(attrs={'class': 'cyber-input', 'placeholder': 'e.g. Backend Architecture'}),
            'description': forms.Textarea(attrs={'class': 'cyber-input', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

# This "FormSet" allows us to edit multiple tags attached to one service
ServiceTagFormSet = forms.inlineformset_factory(
    ServiceItem, ServiceTag,
    fields=['name', 'icon'],
    extra=3, # Show 3 empty tag rows by default
    can_delete=True,
    widgets={
        'name': forms.TextInput(attrs={'class': 'cyber-input', 'placeholder': 'Tag Name (e.g. Python)'}),
        'icon': forms.TextInput(attrs={'class': 'cyber-input', 'placeholder': 'Icon Class (e.g. bi bi-code)'}),
    }
)



from django import forms
from .models import NewsItem

class NewsItemForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = ['title', 'category', 'description', 'image', 'external_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'dash-input', 'placeholder': 'Article Headline'}),
            'category': forms.Select(attrs={'class': 'dash-select'}),
            'description': forms.Textarea(attrs={'class': 'dash-input', 'rows': 3, 'placeholder': 'Short summary for the menu...'}),
            'external_link': forms.URLInput(attrs={'class': 'dash-input', 'placeholder': 'https://medium.com/...'}),
            'image': forms.FileInput(attrs={'class': 'dash-file'}),
        }


        from .models import Project, ProjectImage

# 4. PROJECT FORM (Portfolio)
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'category', 'client_name', 'description', 'image', 'live_link', 'completed_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'cyber-input', 'placeholder': 'Project Name'}),
            'category': forms.Select(attrs={'class': 'cyber-input'}),
            'client_name': forms.TextInput(attrs={'class': 'cyber-input', 'placeholder': 'Client Name'}),
            'description': forms.Textarea(attrs={'class': 'cyber-input', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'live_link': forms.URLInput(attrs={'class': 'cyber-input', 'placeholder': 'https://...'}),
            'completed_date': forms.DateInput(attrs={'class': 'cyber-input', 'type': 'date'}),
        }

# 5. GALLERY FORMSET (Multiple Images)
ProjectImageFormSet = forms.inlineformset_factory(
    Project, ProjectImage,
    fields=['image'],
    extra=3, # Allow 3 gallery images by default
    can_delete=True,
    widgets={
        'image': forms.FileInput(attrs={'class': 'form-control-file'}),
    }
)


# Settings Forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'cyber-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'cyber-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'cyber-input', 'placeholder': 'Email Address'}),
        }

class CustomPasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'cyber-input', 'placeholder': 'Current Password'}),
        label='Current Password'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'cyber-input', 'placeholder': 'New Password'}),
        label='New Password',
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'cyber-input', 'placeholder': 'Confirm New Password'}),
        label='Confirm New Password'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("New passwords don't match.")
        
        return cleaned_data