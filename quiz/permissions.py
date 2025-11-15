from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'ADMIN'
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsNormalUser(BasePermission):
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and 
            request.user.role == 'USER'
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if hasattr(request.user, 'role') and request.user.role == 'ADMIN':
            return True
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsAdminOrReadOnly(BasePermission):
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        return (
            hasattr(request.user, 'role') and 
            request.user.role == 'ADMIN'
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)