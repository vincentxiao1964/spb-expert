from pathlib import Path
import os
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

CACHE_DIR = os.getenv('DJANGO_CACHE_DIR', '/tmp/spb-expert9-cache')
os.makedirs(CACHE_DIR, exist_ok=True)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': CACHE_DIR,
        'TIMEOUT': None,
    }
}

def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_list(name: str, default: list) -> list:
    value = os.getenv(name)
    if value is None:
        return default
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]


DEBUG = _env_bool("DEBUG", False)

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key")
if not DEBUG and SECRET_KEY == "django-insecure-default-key":
    raise ValueError("SECRET_KEY must be set in production")

ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders', 
    'crispy_forms',
    'crispy_bootstrap5',
    
    # Local
    'users',
    'market',
    'ads',
    'api',
    'core',
    'transactions',
    'crew',
    'tools',
    'hymart_matching',
    'hymart_shipdata',
    'news',
    'forum',
    'reports',
    'regulatory',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.VisitorTrackingMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spb_expert.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'spb_expert.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('zh-hans', _('Simplified Chinese')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Increase max upload size to 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'users:login'

AUTH_USER_MODEL = 'users.CustomUser'

SITE_ID = 1

CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", [])

CORS_ALLOW_ALL_ORIGINS = _env_bool("CORS_ALLOW_ALL_ORIGINS", False)
CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS", [])
CORS_ALLOW_CREDENTIALS = _env_bool("CORS_ALLOW_CREDENTIALS", True)

SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", False)
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", False)

SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", False)

if _env_bool("USE_X_FORWARDED_PROTO", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
}

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# WeChat Mini Program Configuration
WECHAT_MINI_PROGRAM_APP_ID = os.getenv('WECHAT_MINI_PROGRAM_APP_ID')
WECHAT_MINI_PROGRAM_APP_SECRET = os.getenv('WECHAT_MINI_PROGRAM_APP_SECRET')

# WeChat Official Account Configuration
WECHAT_OA_APP_ID = os.getenv('WECHAT_OA_APP_ID')
WECHAT_OA_ORIGINAL_ID = os.getenv('WECHAT_OA_ORIGINAL_ID')
WECHAT_OA_APP_SECRET = os.getenv('WECHAT_OA_APP_SECRET')
WECHAT_OA_OAUTH_SCOPE = os.getenv('WECHAT_OA_OAUTH_SCOPE', 'snsapi_base')

# Tencent Cloud SMS
TENCENT_CLOUD_SECRET_ID = os.getenv('TENCENT_CLOUD_SECRET_ID')
TENCENT_CLOUD_SECRET_KEY = os.getenv('TENCENT_CLOUD_SECRET_KEY')
SMS_SDK_APP_ID = os.getenv('SMS_SDK_APP_ID')
SMS_SIGN_NAME = os.getenv('SMS_SIGN_NAME')
SMS_TEMPLATE_ID = os.getenv('SMS_TEMPLATE_ID')
SMS_TEMPLATE_PARAM_SET = os.getenv('SMS_TEMPLATE_PARAM_SET', '')
SMS_REGION = os.getenv('SMS_REGION', 'ap-guangzhou')
SMS_CODE_TTL_SECONDS = int(os.getenv('SMS_CODE_TTL_SECONDS', '300'))
SMS_SEND_INTERVAL_SECONDS = int(os.getenv('SMS_SEND_INTERVAL_SECONDS', '60'))

# Email (for overseas users / cost control)
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = _env_bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'no-reply@barge-expert.com')
EMAIL_CODE_TTL_SECONDS = int(os.getenv('EMAIL_CODE_TTL_SECONDS', '600'))
EMAIL_SEND_INTERVAL_SECONDS = int(os.getenv('EMAIL_SEND_INTERVAL_SECONDS', '60'))
EMAIL_VERIFICATION_SUBJECT = os.getenv('EMAIL_VERIFICATION_SUBJECT', 'SPB EXPERT verification code')
