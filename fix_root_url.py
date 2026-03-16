import os

# 1. Create config/views.py
views_content = """from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "message": "Welcome to SPB Expert API",
        "version": "v1",
        "endpoints": {
            "admin": "/admin/",
            "store": "/api/v1/store/",
            "users": "/api/v1/users/",
            "procurement": "/api/v1/procurement/",
            "logistics": "/api/v1/logistics/"
        }
    })
"""

views_path = r'd:\spb-expert11\config\views.py'
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(views_content)
print(f"Created {views_path}")

# 2. Update config/urls.py
urls_content = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/v1/store/', include('apps.store.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/procurement/', include('apps.procurement.urls')),
    path('api/v1/logistics/', include('apps.logistics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

urls_path = r'd:\spb-expert11\config\urls.py'
with open(urls_path, 'w', encoding='utf-8') as f:
    f.write(urls_content)
print(f"Updated {urls_path}")
