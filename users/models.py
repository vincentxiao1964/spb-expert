from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.conf import settings

class CustomUser(AbstractUser):
    class MembershipLevel(models.IntegerChoices):
        LEVEL_1 = 1, _('Level 1 Member')
        LEVEL_2 = 2, _('Level 2 Member')

    phone_number = models.CharField(_('Phone Number'), max_length=20, unique=True, blank=True, null=True)
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', null=True, blank=True)
    membership_level = models.IntegerField(
        _('Membership Level'),
        choices=MembershipLevel.choices,
        default=MembershipLevel.LEVEL_1
    )
    approved_posts_count = models.IntegerField(_('Approved Posts Count'), default=0)
    company_name = models.CharField(_('Company Name'), max_length=100, blank=True)
    job_title = models.CharField(_('Job Title'), max_length=100, blank=True)
    business_content = models.TextField(_('Business Content'), blank=True)
    openid = models.CharField(_('WeChat OpenID'), max_length=100, blank=True, null=True, unique=True)
    unionid = models.CharField(_('WeChat UnionID'), max_length=100, blank=True, null=True, unique=True)
    oa_openid = models.CharField(_('WeChat OA OpenID'), max_length=100, blank=True, null=True, unique=True)
    source_channel = models.CharField(_('Source Channel'), max_length=32, blank=True, null=True, db_index=True)

    def __str__(self):
        return self.username

    def update_level(self):
        """Check and update membership level based on approved posts."""
        if self.approved_posts_count >= 10 and self.membership_level == self.MembershipLevel.LEVEL_1:
            self.membership_level = self.MembershipLevel.LEVEL_2
            self.save()

class UserFollow(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower} follows {self.followed}"

class VisitorLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ip_address} - {self.path} at {self.created_at}"

class LoginLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    login_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-login_time']

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    LoginLog.objects.create(user=user, ip_address=ip, user_agent=user_agent)


class ChannelEvent(models.Model):
    class EventType(models.TextChoices):
        LISTING_CREATE = 'LISTING_CREATE', _('Listing Create')
        PRIVATE_MESSAGE_SENT = 'PRIVATE_MESSAGE_SENT', _('Private Message Sent')
        FAVORITE_ADD = 'FAVORITE_ADD', _('Favorite Add')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='channel_events')
    source_channel = models.CharField(_('Source Channel'), max_length=32, blank=True, null=True, db_index=True)
    event_type = models.CharField(_('Event Type'), max_length=40, choices=EventType.choices)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
        ]
        ordering = ['-created_at']
