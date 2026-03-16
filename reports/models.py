from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

class Report(models.Model):
    class Reason(models.TextChoices):
        SPAM = 'SPAM', _('Spam or Advertising')
        OFFENSIVE = 'OFFENSIVE', _('Offensive Content')
        FRAUD = 'FRAUD', _('Fraud or Scam')
        ILLEGAL = 'ILLEGAL', _('Illegal Content')
        OTHER = 'OTHER', _('Other')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        RESOLVED = 'RESOLVED', _('Resolved')
        IGNORED = 'IGNORED', _('Ignored')

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='filed_reports')
    
    # Generic relation to reported object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    reason = models.CharField(max_length=20, choices=Reason.choices)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Report {self.id} by {self.reporter}'
