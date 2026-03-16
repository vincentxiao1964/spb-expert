from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipExtendedInfoViewSet, VoyageHistoryViewSet

router = DefaultRouter()
router.register(r'extended-info', ShipExtendedInfoViewSet, basename='ship-extended-info')
router.register(r'voyage-history', VoyageHistoryViewSet, basename='voyage-history')

urlpatterns = [
    path('', include(router.urls)),
]
