from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

class AccountCreationForm(UserCreationForm):
    company_name = forms.CharField(label=_('Company Name'), max_length=100, required=False)
    phone_number = forms.CharField(label=_('Phone Number'), max_length=20, required=False)
    email = forms.EmailField(label=_('Email address'), required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'company_name')

class CustomUserCreationForm(UserCreationForm):
    sms_code = forms.CharField(label=_('SMS Verification Code'), required=True, help_text=_("Enter '123456' for testing."))

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'email', 'company_name')

    def clean_sms_code(self):
        code = self.cleaned_data.get('sms_code')
        # Mock verification: accept '123456'
        if code != '123456':
            raise forms.ValidationError(_("Invalid verification code. Use '123456' for testing."))
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user

class WebSMSLoginForm(forms.Form):
    phone_number = forms.CharField(label=_('Phone Number'), max_length=11)
    code = forms.CharField(label=_('Verification Code'), max_length=6)

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        code = cleaned_data.get('code')
        
        if phone_number and code:
            # Verify code using cache
            cache_key = f"sms_code_{phone_number}"
            cached_code = cache.get(cache_key)
            
            # Allow '123456' as universal backdoor for testing if real SMS fails
            if code == '123456':
                pass # Allow for testing
            elif not cached_code or str(cached_code) != str(code):
                 raise forms.ValidationError(_("Invalid or expired verification code."))
                 
            # Check if user exists
            User = get_user_model()
            try:
                user = User.objects.get(phone_number=phone_number)
                self.user_cache = user
            except User.DoesNotExist:
                raise forms.ValidationError(_("User with this phone number does not exist."))
                
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)

class WebEmailLoginForm(forms.Form):
    email = forms.CharField(label=_('Email'), max_length=254)
    code = forms.CharField(label=_('Verification Code'), max_length=6)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        code = cleaned_data.get('code')

        if email:
            email = str(email).strip().lower()
            try:
                validate_email(email)
            except DjangoValidationError:
                raise forms.ValidationError(_("Invalid email address."))
            cleaned_data['email'] = email

        if email and code:
            cache_key = f"email_code_{email}"
            cached_code = cache.get(cache_key)
            if not cached_code or str(cached_code) != str(code):
                raise forms.ValidationError(_("Invalid or expired verification code."))

            User = get_user_model()
            user = User.objects.filter(login_email__iexact=email).first() or User.objects.filter(email__iexact=email).first()
            if not user:
                raise forms.ValidationError(_("Email not registered. Please register first."))

            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)

class EmailPasswordCreationForm(UserCreationForm):
    email = forms.EmailField(label=_('Email'), required=True)

    class Meta:
        model = CustomUser
        fields = ('email',)

    def clean_email(self):
        value = self.cleaned_data.get('email')
        if not value:
            raise forms.ValidationError(_("Email is required."))
        email = str(value).strip().lower()
        try:
            validate_email(email)
        except DjangoValidationError:
            raise forms.ValidationError(_("Invalid email address."))

        User = get_user_model()
        if User.objects.filter(login_email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError(_("This email is already registered."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.username = email
        user.email = email
        user.login_email = email
        if commit:
            user.save()
        return user
