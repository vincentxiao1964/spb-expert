from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Section(models.Model):
    """
    Forum Section (e.g., Technical, Market, General)
    """
    name = models.CharField(_('Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    order = models.PositiveIntegerField(_('Order'), default=0)
    is_active = models.BooleanField(_('Is Active'), default=True)

    class Meta:
        verbose_name = _('Section')
        verbose_name_plural = _('Sections')
        ordering = ['order']

    def __str__(self):
        return self.name

class Thread(models.Model):
    """
    Forum Thread
    """
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')
        HIDDEN = 'HIDDEN', _('Hidden (Moderated)')

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_threads')
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    
    view_count = models.PositiveIntegerField(_('View Count'), default=0)
    reply_count = models.PositiveIntegerField(_('Reply Count'), default=0)
    
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.OPEN)
    is_pinned = models.BooleanField(_('Is Pinned'), default=False)
    
    last_reply_at = models.DateTimeField(_('Last Reply At'), auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')
        ordering = ['-is_pinned', '-last_reply_at']

    def __str__(self):
        return self.title

class Post(models.Model):
    """
    Forum Post (Reply)
    """
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField(_('Content'))
    
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['created_at']

    def __str__(self):
        return f"Post by {self.author} in {self.thread}"
