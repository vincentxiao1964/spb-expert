from django.db import models
from django.contrib.auth.models import User


class JobPosition(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='positions',
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])


class JobListing(models.Model):
    class ShipType(models.TextChoices):
        BULK_CARRIER = 'BULK', 'Bulk Carrier'
        CONTAINER = 'CONTAINER', 'Container Ship'
        TANKER = 'TANKER', 'Tanker'
        GENERAL_CARGO = 'GENERAL', 'General Cargo'
        OTHER = 'OTHER', 'Other'

    employer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_listings',
    )
    position = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        related_name='listings',
    )
    title = models.CharField(max_length=200)
    ship_type = models.CharField(max_length=20, choices=ShipType.choices, default=ShipType.BULK_CARRIER)
    salary_range = models.CharField(max_length=100)
    contract_duration = models.CharField(max_length=100)
    requirements = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.employer.username})"
