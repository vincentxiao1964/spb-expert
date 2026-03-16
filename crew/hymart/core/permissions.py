from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsMerchantOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return u and u.is_authenticated and hasattr(u, 'profile') and u.profile.is_merchant

class IsBuyerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return u and u.is_authenticated and hasattr(u, 'profile') and u.profile.is_buyer
