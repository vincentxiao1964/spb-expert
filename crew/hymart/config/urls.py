"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import health, DashboardSummaryView, MerchantDashboardView, UserDashboardView
from rest_framework import routers
from store.views import CategoryViewSet, ProductViewSet, CartViewSet
from services.views import ServiceCategoryViewSet, ServiceListingViewSet
from orders.views import OrderViewSet, OrderRefundViewSet, ShipmentViewSet
from reviews.views import ReviewViewSet, ReviewReportViewSet, ReviewAppealViewSet, SensitiveWordViewSet, ViolationCaseViewSet, PunishmentViewSet
from core.views import NotificationViewSet
from market.views import CouponViewSet, UserCouponViewSet
from crew.views import JobPositionViewSet, JobListingViewSet
from rest_framework.authtoken.views import obtain_auth_token
from users.views import MeProfileView
from payments.views import PaymentIntentViewSet

router = routers.DefaultRouter()
router.register(r'store/categories', CategoryViewSet, basename='store-categories')
router.register(r'store/products', ProductViewSet, basename='store-products')
router.register(r'store/cart', CartViewSet, basename='store-cart')
router.register(r'services/categories', ServiceCategoryViewSet, basename='services-categories')
router.register(r'services/listings', ServiceListingViewSet, basename='services-listings')
router.register(r'market/coupons', CouponViewSet, basename='market-coupons')
router.register(r'market/user-coupons', UserCouponViewSet, basename='market-user-coupons')
router.register(r'crew/positions', JobPositionViewSet, basename='crew-positions')
router.register(r'crew/job-listings', JobListingViewSet, basename='crew-job-listings')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'orders/refunds', OrderRefundViewSet, basename='orders-refunds')
router.register(r'orders/shipments', ShipmentViewSet, basename='orders-shipments')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'reviews/reports', ReviewReportViewSet, basename='reviews-reports')
router.register(r'reviews/appeals', ReviewAppealViewSet, basename='reviews-appeals')
router.register(r'reviews/sensitive-words', SensitiveWordViewSet, basename='reviews-sensitive-words')
router.register(r'moderation/cases', ViolationCaseViewSet, basename='moderation-cases')
router.register(r'moderation/punishments', PunishmentViewSet, basename='moderation-punishments')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'payments/intents', PaymentIntentViewSet, basename='payments-intents')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health),
    path('api/v1/health/', health),
    path('api/v1/dashboard/summary/', DashboardSummaryView.as_view()),
    path('api/v1/dashboard/merchant/', MerchantDashboardView.as_view()),
    path('api/v1/dashboard/me/', UserDashboardView.as_view()),
    path('api/v1/', include(router.urls)),
    path('api/v1/auth/token/', obtain_auth_token),
    path('api/v1/users/me/', MeProfileView.as_view()),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
