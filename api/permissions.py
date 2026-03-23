from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # Check if obj has user field
        if hasattr(obj, 'user'):
            return obj.user == user or user.is_staff or user.is_superuser
            
        # Check if obj has listing field (for ListingImage)
        if hasattr(obj, 'listing'):
            return obj.listing.user == user or user.is_staff or user.is_superuser
            
        return user.is_staff or user.is_superuser


class IsActiveForWrite(BasePermission):
    """
    Allow read to anyone per outer permission, but block write if user is inactive.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return bool(user.is_active)
