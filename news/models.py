from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending Review')
        PUBLISHED = 'PUBLISHED', _('Published')
        REJECTED = 'REJECTED', _('Rejected')

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    summary = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='news/covers/', blank=True, null=True)
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.article}'
