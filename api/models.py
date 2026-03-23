from django.db import models


class MediaCheckTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PASS = 'PASS', 'Pass'
        REVIEW = 'REVIEW', 'Review'
        RISKY = 'RISKY', 'Risky'
        ERROR = 'ERROR', 'Error'

    trace_id = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    appid = models.CharField(max_length=64, blank=True, null=True)
    openid = models.CharField(max_length=128, blank=True, null=True)
    scene = models.IntegerField(blank=True, null=True)
    media_type = models.IntegerField(blank=True, null=True)
    media_url = models.URLField(max_length=1000, blank=True, null=True)

    object_type = models.CharField(max_length=32)
    object_id = models.IntegerField()
    object_field = models.CharField(max_length=64, blank=True, null=True)

    suggest = models.CharField(max_length=16, blank=True, null=True)
    label = models.IntegerField(blank=True, null=True)
    raw_result = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['status', 'created_at']),
        ]
