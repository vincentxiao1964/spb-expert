import os

# 1. Update config/settings.py
settings_path = r'D:\spb-expert11\config\settings.py'
with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "rest_framework_simplejwt" not in content:
    # Add to INSTALLED_APPS
    content = content.replace("'rest_framework',", "'rest_framework',\n    'rest_framework_simplejwt',")
    
    # Add REST_FRAMEWORK config
    config = """
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7), # Long for dev
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}
"""
    content += config
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {settings_path}")

# 2. Update apps/users/urls.py
users_urls_path = r'D:\spb-expert11\apps\users\urls.py'
with open(users_urls_path, 'r', encoding='utf-8') as f:
    content = f.read()

if "TokenObtainPairView" not in content:
    # Add imports
    content = "from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView\n" + content
    
    # Add paths
    if "urlpatterns = [" in content:
        content = content.replace("urlpatterns = [", 
                                  "urlpatterns = [\n    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),\n    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),")
    
    with open(users_urls_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {users_urls_path}")
