import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spb_expert.settings')
django.setup()

print("=== Server Diagnosis ===")
print(f"Python Version: {sys.version}")
print(f"Django Version: {django.get_version()}")

try:
    import jwt
    print(f"PyJWT Version: {jwt.__version__}")
except ImportError:
    print("PyJWT not installed")

try:
    import rest_framework_simplejwt
    print(f"SimpleJWT Version: {rest_framework_simplejwt.__version__}")
except ImportError:
    print("SimpleJWT not installed")

# Check WeChat Config
appid = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_ID', None)
secret = getattr(settings, 'WECHAT_MINI_PROGRAM_APP_SECRET', None)
print(f"WeChat AppID Configured: {'Yes' if appid else 'No'} ({appid if appid else 'Missing'})")
print(f"WeChat Secret Configured: {'Yes' if secret else 'No'}")

# Test JWT Generation
print("\nTesting JWT Generation...")
try:
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # Create or get a dummy user for testing
    user, created = User.objects.get_or_create(username='diagnosis_test_user')
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    print(f"JWT Generation Success! Access Token length: {len(access)}")
    print(f"Access Token type: {type(access)}")
except Exception as e:
    print(f"JWT Generation FAILED: {e}")
    import traceback
    traceback.print_exc()

print("=== Diagnosis Complete ===")
