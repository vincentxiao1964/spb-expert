from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class AdminMessage(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    company_name = models.CharField(_('Company Name'), max_length=100, blank=True)
    phone_number = models.CharField(_('Phone Number'), max_length=20, blank=True)
    message = models.TextField(_('Message'))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class MemberMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(_('Message Content'))
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Forum Topic')
        verbose_name_plural = _('Forum')

    def __str__(self):
        return f"Message from {self.user.username} at {self.created_at}"

class MessageReply(models.Model):
    message = models.ForeignKey(MemberMessage, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_replies')
    content = models.TextField(_('Reply Content'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.user.username} on {self.message.id}"

class PrivateMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(_('Content'), blank=True)
    image = models.ImageField(_('Image'), upload_to='chat_images/', blank=True, null=True)
    is_read = models.BooleanField(_('Is Read'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Private Message')
        verbose_name_plural = _('Private Messages')

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.created_at}"

class Notification(models.Model):
    class Type(models.TextChoices):
        MESSAGE = 'MESSAGE', _('New Message')
        REPLY = 'REPLY', _('New Reply')
        FOLLOW = 'FOLLOW', _('New Follower')
        SYSTEM = 'SYSTEM', _('System Notification')
        APPROVAL = 'APPROVAL', _('Listing Approval')

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='triggered_notifications')
    notification_type = models.CharField(_('Type'), max_length=20, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    is_read = models.BooleanField(_('Is Read'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Link to related object
    target_url = models.CharField(_('Target URL'), max_length=500, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.recipient}"
