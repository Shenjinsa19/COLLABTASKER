from rest_framework.permissions import BasePermission, SAFE_METHODS
class IsAdminPMOrReadOnly(BasePermission):
    def has_permission(self,request,view):
        user=request.user
        if not user.is_authenticated:
            return False
        if user.role in ['admin','pm']:
            return True  
        if user.role=='collab':
            return request.method in SAFE_METHODS  # collab read oly
        return False
