from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

class User(AbstractUser):
    """
    Custom User Model for Hymart Platform
    Extends Django's AbstractUser to include mobile, avatar, and role.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        GENERAL = 'GENERAL', _('General User')  # Individual/Buyer
        COMPANY = 'COMPANY', _('Company')       # Supplier/Service Provider/Ship Owner
        CREW = 'CREW', _('Crew Member')         # Job seeker

    mobile = models.CharField(_('Mobile Number'), max_length=11, unique=True, null=True, blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', null=True, blank=True)
    role = models.CharField(_('Role'), max_length=20, choices=Role.choices, default=Role.GENERAL)
    
    # Company info (basic) - Detailed info should go to a CompanyProfile model
    company_name = models.CharField(_('Company Name'), max_length=100, blank=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']

    def __str__(self):
        if self.mobile:
            return f"{self.username} ({self.mobile})"
        return self.username


class CompanyProfile(models.Model):
    """
    Extended profile for Company users (Suppliers, Service Providers)
    """
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending Review')
        VERIFIED = 'VERIFIED', _('Verified')
        REJECTED = 'REJECTED', _('Rejected')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    business_license_no = models.CharField(_('Business License No.'), max_length=50, blank=True)
    business_license_img = models.ImageField(_('Business License Image'), upload_to='licenses/', blank=True, null=True)
    
    address = models.CharField(_('Company Address'), max_length=255, blank=True)
    contact_person = models.CharField(_('Contact Person'), max_length=50, blank=True)
    contact_phone = models.CharField(_('Contact Phone'), max_length=20, blank=True)
    
    website = models.URLField(_('Website'), blank=True)
    description = models.TextField(_('Company Description'), blank=True)
    
    verification_status = models.CharField(
        _('Verification Status'), 
        max_length=20, 
        choices=VerificationStatus.choices, 
        default=VerificationStatus.PENDING
    )
    is_verified = models.BooleanField(_('Is Verified'), default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Company Profile')
        verbose_name_plural = _('Company Profiles')

    def __str__(self):
        return f"{self.user.company_name} ({self.get_verification_status_display()})"


class CrewProfile(models.Model):
    """
    Extended profile for Crew members (Job seekers)
    """
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Available for Hire')
        ONBOARD = 'ONBOARD', _('On Board / Unavailable')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='crew_profile')
    real_name = models.CharField(_('Real Name'), max_length=50)
    gender = models.CharField(_('Gender'), max_length=1, choices=Gender.choices, default=Gender.MALE)
    birth_date = models.DateField(_('Birth Date'), null=True, blank=True)
    
    position = models.CharField(_('Target Position'), max_length=50, help_text=_('e.g. Captain, Chief Engineer'))
    years_of_experience = models.PositiveIntegerField(_('Years of Experience'), default=0)
    
    certificate_number = models.CharField(_('Seafarer Certificate No.'), max_length=50, blank=True)
    
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    resume_file = models.FileField(_('Resume File'), upload_to='resumes/', blank=True, null=True)
    
    bio = models.TextField(_('Bio/Self Introduction'), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Crew Profile')
        verbose_name_plural = _('Crew Profiles')

    def __str__(self):
        return f"{self.real_name} - {self.position}"

class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    LoginLog.objects.create(
        user=user,
        ip_address=ip,
        user_agent=user_agent
    )
