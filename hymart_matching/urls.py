from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CargoRequestViewSet

router = DefaultRouter()
router.register(r'cargo-requests', CargoRequestViewSet, basename='cargo-request')

urlpatterns = [
    path('', include(router.urls)),
]
