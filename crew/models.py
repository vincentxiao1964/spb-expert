from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class CrewListing(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')

    class NationalityType(models.TextChoices):
        DOMESTIC = 'DOMESTIC', _('Chinese Crew')
        INTERNATIONAL = 'INTERNATIONAL', _('Foreign Crew')

    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Available')
        HIRED = 'HIRED', _('Hired')

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='crew_profile', verbose_name=_("User"))
    
    # Basic Info
    name = models.CharField(_("Name"), max_length=100)
    gender = models.CharField(_("Gender"), max_length=1, choices=Gender.choices, default=Gender.MALE)
    nationality_type = models.CharField(_("Crew Type"), max_length=20, choices=NationalityType.choices, default=NationalityType.DOMESTIC)
    nationality = models.CharField(_("Nationality"), max_length=100, help_text=_("e.g. China, Philippines, India"))
    residence = models.CharField(_("Residence Address"), max_length=255)
    
    # Professional Info
    position = models.CharField(_("Rank/Position"), max_length=100, help_text=_("e.g. Captain, Chief Engineer, Able Seaman"))
    total_sea_experience = models.DecimalField(_("Total Sea Experience (Years)"), max_digits=4, decimal_places=1)
    current_rank_experience = models.DecimalField(_("Experience in Current Rank (Years)"), max_digits=4, decimal_places=1)
    cert_number = models.CharField(_("Seaman's Book / Certificate No."), max_length=100)
    
    # Contact Info
    phone = models.CharField(_("Phone Number"), max_length=50)
    email = models.EmailField(_("Email Address"))
    
    # Job Expectations
    expected_salary = models.CharField(_("Expected Salary"), max_length=100, help_text=_("e.g. 5000 USD/Month"))
    
    # Resume / Bio
    resume = models.TextField(_("Resume"), help_text=_("Describe past ships, ranks, shipping companies, manning agencies, etc."))
    
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Crew Listing")
        verbose_name_plural = _("Crew Listings")
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} - {self.position}"
