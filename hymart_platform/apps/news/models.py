from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Article(models.Model):
    """
    News Articles / Industry Information
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending Review')
        PUBLISHED = 'PUBLISHED', _('Published')
        REJECTED = 'REJECTED', _('Rejected')

    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_articles')
    
    content = models.TextField(_('Content'))
    summary = models.TextField(_('Summary'), max_length=500, blank=True)
    cover_image = models.ImageField(_('Cover Image'), upload_to='news/covers/', blank=True, null=True)
    
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    view_count = models.PositiveIntegerField(_('View Count'), default=0)
    
    published_at = models.DateTimeField(_('Published At'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

class Comment(models.Model):
    """
    Comments on News Articles
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='news_comments')
    content = models.TextField(_('Comment Content'))
    
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.article}"
