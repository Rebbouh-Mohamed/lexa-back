from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return hasattr(obj, 'user') and obj.user == request.user

class IsLawyerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow lawyers and admins.
    """

    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.role in ['lawyer', 'admin'])

class IsActiveUser(permissions.BasePermission):
    """
    Custom permission to only allow active users.
    """

    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.status == 'active')

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        return (request.user and 
                request.user.is_authenticated and 
                request.user.role == 'admin')

class HasValidSubscription(permissions.BasePermission):
    """
    Custom permission to check if user has valid subscription.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users always have access
        if request.user.role == 'admin':
            return True
        
        # Check subscription status
        return request.user.subscription_status in ['trial', 'active']