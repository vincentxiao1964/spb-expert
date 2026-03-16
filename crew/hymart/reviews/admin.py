from django.contrib import admin
from .models import Review, ReviewReport, ReviewAppeal, SensitiveWord

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'rating', 'is_public', 'is_pinned', 'hidden_by_owner', 'flagged_sensitive', 'is_deleted', 'created_at')
    list_filter = ('is_public', 'is_pinned', 'hidden_by_owner', 'flagged_sensitive', 'is_deleted')
    search_fields = ('comment', 'reviewer__username')
    ordering = ('-created_at',)
    raw_id_fields = ('order_item', 'reviewer')
    actions = ['publish_selected', 'unpublish_selected', 'pin_selected', 'unpin_selected', 'hide_selected', 'unhide_selected', 'delete_selected_soft', 'restore_selected', 'export_selected_csv']

    def publish_selected(self, request, queryset):
        queryset.update(is_public=True)
    publish_selected.short_description = '发布所选评价'

    def unpublish_selected(self, request, queryset):
        queryset.update(is_public=False)
    unpublish_selected.short_description = '取消发布所选评价'

    def pin_selected(self, request, queryset):
        queryset.update(is_pinned=True)
    pin_selected.short_description = '置顶所选评价'

    def unpin_selected(self, request, queryset):
        queryset.update(is_pinned=False)
    unpin_selected.short_description = '取消置顶所选评价'

    def hide_selected(self, request, queryset):
        queryset.update(hidden_by_owner=True)
    hide_selected.short_description = '隐藏所选评价'

    def unhide_selected(self, request, queryset):
        queryset.update(hidden_by_owner=False)
    unhide_selected.short_description = '取消隐藏所选评价'

    def delete_selected_soft(self, request, queryset):
        queryset.update(is_deleted=True)
    delete_selected_soft.short_description = '软删除所选评价'

    def restore_selected(self, request, queryset):
        queryset.update(is_deleted=False)
    restore_selected.short_description = '恢复所选评价'

    def export_selected_csv(self, request, queryset):
        import csv
        from io import StringIO
        from django.http import HttpResponse
        output = StringIO()
        writer = csv.writer(output)
        header = ['id', 'reviewer', 'reviewer_id', 'owner', 'owner_id', 'object_type', 'object_id', 'rating', 'comment', 'reply', 'is_public', 'is_pinned', 'hidden_by_owner', 'flagged_sensitive', 'status', 'sensitive_terms', 'created_at', 'image_urls', 'like_count']
        writer.writerow(header)
        for r in queryset.select_related('order_item', 'reviewer'):
            oi = r.order_item
            obj_type = 'product' if oi and oi.product_id else ('service' if oi and oi.service_id else '')
            obj_id = oi.product_id if oi and oi.product_id else (oi.service_id if oi and oi.service_id else '')
            owner = oi.product.owner if oi and oi.product_id else (oi.service.owner if oi and oi.service_id else None)
            status_val = 'deleted' if r.is_deleted else ('unpublished' if not r.is_public else ('hidden' if r.hidden_by_owner else ('sensitive' if r.flagged_sensitive else 'normal')))
            imgs = [request.build_absolute_uri(img.image.url) for img in r.images.all()]
            like_cnt = r.likes.count() if hasattr(r, 'likes') else 0
            writer.writerow([
                r.id,
                r.reviewer.username if r.reviewer_id else '',
                r.reviewer_id or '',
                owner.username if owner else '',
                owner.id if owner else '',
                obj_type,
                obj_id,
                r.rating,
                (r.comment or '').replace('\n', ' ').replace('\r', ' '),
                (r.reply or '').replace('\n', ' ').replace('\r', ' '),
                r.is_public,
                r.is_pinned,
                r.hidden_by_owner,
                r.flagged_sensitive,
                status_val,
                r.sensitive_terms,
                r.created_at.isoformat(),
                ';'.join(imgs),
                like_cnt,
            ])
        resp = HttpResponse(output.getvalue(), content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename=\"admin_selected_reviews.csv\"'
        return resp
    export_selected_csv.short_description = '导出所选评价为 CSV'

@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'reporter', 'status', 'created_at', 'resolved_at', 'resolved_by')
    list_filter = ('status',)
    search_fields = ('reason', 'reporter__username')
    ordering = ('-created_at',)
    raw_id_fields = ('review', 'reporter', 'resolved_by')

@admin.register(ReviewAppeal)
class ReviewAppealAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'applicant', 'status', 'created_at', 'resolved_at', 'resolved_by')
    list_filter = ('status',)
    search_fields = ('reason', 'applicant__username')
    ordering = ('-created_at',)
    raw_id_fields = ('review', 'applicant', 'resolved_by')

@admin.register(SensitiveWord)
class SensitiveWordAdmin(admin.ModelAdmin):
    list_display = ('id', 'word', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('word',)
    ordering = ('word',)
