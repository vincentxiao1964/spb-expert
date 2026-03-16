from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.store.views import CategoryViewSet, ProductViewSet
from apps.services.views import ServiceCategoryViewSet, ServiceListingViewSet
from apps.crew.views import JobPositionViewSet, JobListingViewSet, CrewResumeViewSet
from apps.orders.views import OrderViewSet
from apps.payments.views import PaymentViewSet
from apps.inquiries.views import InquiryViewSet
from apps.notifications.views import NotificationViewSet
from apps.users.views import UserViewSet, UserStatsView, CompanyListingViewSet
from apps.reviews.views import ReviewViewSet
from apps.news.views import ArticleViewSet
from apps.forum.views import SectionViewSet, ThreadViewSet
from apps.reports.views import ReportViewSet
from apps.regulatory.views import RegulatoryViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')
router.register(r'companies', CompanyListingViewSet, basename='company')
router.register(r'store/categories', CategoryViewSet, basename='store-category')
router.register(r'store/products', ProductViewSet, basename='store-product')
router.register(r'services/categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'services/listings', ServiceListingViewSet, basename='service-listing')
router.register(r'crew/positions', JobPositionViewSet, basename='crew-position')
router.register(r'crew/jobs', JobListingViewSet, basename='crew-job')
router.register(r'crew/resumes', CrewResumeViewSet, basename='crew-resume')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'inquiries', InquiryViewSet, basename='inquiry')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'reviews', ReviewViewSet, basename='review')

# News & Forum & Reports
router.register(r'news', ArticleViewSet, basename='news')
router.register(r'forum/sections', SectionViewSet, basename='forum-section')
router.register(r'forum/threads', ThreadViewSet, basename='forum-thread')
router.register(r'reports', ReportViewSet, basename='report')

# Regulatory Interface (Admin only)
router.register(r'regulatory', RegulatoryViewSet, basename='regulatory')

urlpatterns = [
    path('mine/stats/', UserStatsView.as_view(), name='user-stats'),
    path('', include(router.urls)),
]
