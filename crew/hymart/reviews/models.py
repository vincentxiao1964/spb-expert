from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from orders.models import OrderItem

class Review(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    reply = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    hidden_by_owner = models.BooleanField(default=False)
    flagged_sensitive = models.BooleanField(default=False)
    sensitive_terms = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review #{self.id} - {self.rating}"

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='reviews/images/')
    created_at = models.DateTimeField(auto_now_add=True)

class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['review', 'user'], name='unique_review_like_user')
        ]


class ViolationReason(models.TextChoices):
    FRAUD = 'fraud', '涉嫌诈骗'
    MALICIOUS_REVIEW = 'malicious_review', '恶意差评'
    FALSE_PRICING = 'false_pricing', '虚假报价'
    IP_INFRINGEMENT = 'ip_infringement', '侵权投诉'
    ILLEGAL_CONTENT = 'illegal_content', '违法内容'
    OTHER = 'other', '其他'


class ViolationSeverity(models.TextChoices):
    MINOR = 'minor', '轻微'
    MAJOR = 'major', '严重'
    CRITICAL = 'critical', '特别严重'


def get_violation_severity_for_reason(reason_code):
    if reason_code in [ViolationReason.FRAUD, ViolationReason.ILLEGAL_CONTENT]:
        return ViolationSeverity.CRITICAL
    if reason_code in [ViolationReason.IP_INFRINGEMENT, ViolationReason.FALSE_PRICING, ViolationReason.MALICIOUS_REVIEW]:
        return ViolationSeverity.MAJOR
    return ViolationSeverity.MINOR


class ViolationCase(models.Model):
    class Source(models.TextChoices):
        REPORT = 'report', '用户举报'
        RULE = 'rule', '规则命中'
        MANUAL = 'manual', '人工巡检'

    class Status(models.TextChoices):
        OPEN = 'open', '开放'
        IN_PROGRESS = 'in_progress', '处理中'
        CLOSED = 'closed', '已结案'

    class Decision(models.TextChoices):
        NONE = 'none', '未决'
        NO_VIOLATION = 'no_violation', '不违规'
        VIOLATION = 'violation', '违规'
        UNCLEAR = 'unclear', '存疑'

    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    target_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='violation_cases')
    primary_reason = models.CharField(max_length=50, choices=ViolationReason.choices, default=ViolationReason.OTHER)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.REPORT)
    severity = models.CharField(max_length=20, choices=ViolationSeverity.choices, default=ViolationSeverity.MAJOR)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    decision = models.CharField(max_length=20, choices=Decision.choices, default=Decision.NONE)
    decision_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='decided_violation_cases')


class Punishment(models.Model):
    class Type(models.TextChoices):
        WARNING = 'warning', '警告'
        MUTE = 'mute', '禁言'
        BAN = 'ban', '封禁账号'
        CONTENT_REMOVE = 'content_remove', '删除内容'
        LISTING_OFFLINE = 'listing_offline', '下架商品服务'
        OTHER = 'other', '其他'

    class Status(models.TextChoices):
        ACTIVE = 'active', '生效中'
        EXPIRED = 'expired', '已过期'
        REVOKED = 'revoked', '已撤销'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='punishments')
    case = models.ForeignKey(ViolationCase, on_delete=models.CASCADE, related_name='punishments')
    type = models.CharField(max_length=50, choices=Type.choices)
    params = models.JSONField(default=dict, blank=True)
    start_at = models.DateTimeField(default=timezone.now)
    end_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    operator = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='issued_punishments')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        now = timezone.now()
        if self.status != self.Status.ACTIVE:
            return False
        if self.end_at and self.end_at <= now:
            return False
        return True


class ReviewReport(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_reports')
    reason_category = models.CharField(max_length=50, choices=ViolationReason.choices, default=ViolationReason.OTHER)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='resolved_review_reports')
    case = models.ForeignKey(ViolationCase, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['review', 'reporter'], name='unique_review_report_user')
        ]

class ReviewAppeal(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='appeals')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_appeals')
    reason = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    resolution_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='resolved_review_appeals')

class SensitiveWord(models.Model):
    word = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
