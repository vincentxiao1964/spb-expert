from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class InquiriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inquiries'
    verbose_name = _('Inquiries & Quotations')
