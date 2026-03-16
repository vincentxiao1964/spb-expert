from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Report(models.Model):
    """
    User Report / Complaint
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        RESOLVED = 'RESOLVED', _('Resolved')
        IGNORED = 'IGNORED', _('Ignored')

    class Reason(models.TextChoices):
        SPAM = 'SPAM', _('Spam')
        ABUSE = 'ABUSE', _('Abuse/Harassment')
        INAPPROPRIATE = 'INAPPROPRIATE', _('Inappropriate Content')
        FRAUD = 'FRAUD', _('Fraud/Scam')
        OTHER = 'OTHER', _('Other')

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_filed')
    
    # Generic relation to reported content (Thread, Post, Article, Comment, Product, User, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    reason = models.CharField(_('Reason'), max_length=50, choices=Reason.choices)
    description = models.TextField(_('Description'), blank=True)
    
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    resolution_note = models.TextField(_('Resolution Note'), blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='reports_resolved',
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.id} by {self.reporter} ({self.get_status_display()})"
