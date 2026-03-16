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
                path=path,
                method=request.method,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255]
            )
        except Exception:
            # Don't fail request if logging fails
            pass

        return response
