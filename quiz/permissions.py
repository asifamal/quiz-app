from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users.
    Checks if user.role == 'ADMIN'.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has admin role."""
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'ADMIN'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission for admin users."""
        return self.has_permission(request, view)


class IsNormalUser(BasePermission):
    """
    Custom permission to only allow normal users.
    Checks if user.role == 'USER'.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has user role."""
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'USER'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission for normal users."""
        return self.has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow owners of an object or admin users.
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is owner or admin."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Admin users have full access
        if hasattr(request.user, 'role') and request.user.role == 'ADMIN':
            return True
        
        # Check ownership based on object type
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to allow admin users full access,
    but read-only access for others.
    """
    
    def has_permission(self, request, view):
        """Allow read permissions for any authenticated user, write for admins."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Read permissions for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions only for admin users
        return (
            hasattr(request.user, 'role') and 
            request.user.role == 'ADMIN'
        )
    
    def has_object_permission(self, request, view, obj):
        """Allow read permissions for any authenticated user, write for admins."""
        return self.has_permission(request, view)