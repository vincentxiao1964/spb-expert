from .models import VisitorLog
from django.utils import timezone

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Filter out static, media, admin, favicon
        path = request.path
        if any(path.startswith(prefix) for prefix in ['/static/', '/media/', '/admin/', '/favicon.ico']):
            return response

        ch = request.GET.get('ch')
        if ch:
            ch = ''.join(c for c in ch if c.isalnum() or c in ('-', '_'))[:32]
            if ch:
                response.set_cookie(
                    'src_ch',
                    ch,
                    max_age=60 * 60 * 24 * 90,
                    samesite='Lax',
                    secure=request.is_secure()
                )

        # Get IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        user = request.user if request.user.is_authenticated else None

        # Log
        try:
            VisitorLog.objects.create(
                user=user,
                ip_address=ip,
                path=request.get_full_path()[:255],
                method=request.method,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
            )
        except Exception:
            # Don't fail request if logging fails
            pass

        return response
