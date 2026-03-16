from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from market.sitemaps import StaticViewSitemap, ShipListingSitemap, MarketNewsSitemap
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView
from api import views

sitemaps = {
    'static': StaticViewSitemap,
    'listings': ShipListingSitemap,
    'news': MarketNewsSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('i18n/', include('django.conf.urls.i18n')),
    path('users/', include('users.urls')),
    path('market/', include('market.urls')),
    path('ads/', include('ads.urls')),
    path('api/v1/', include('api.urls')),
    path('api/v1/auth/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('tools/', include('tools.urls')),
    path('crew/', include('crew.urls')),
    path('hymart/api/', include('hymart_matching.urls')),
    path('hymart/data/', include('hymart_shipdata.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
