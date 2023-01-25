from rest_framework import permissions

class IsManager(permissions.BasePermission):
    message = 'Only managers can access this route.'
    
    def has_permission(self, request, view):
        if request.user.groups.filter(name="Manager").exists():
            return True
        
        return False


class IsCustomer(permissions.BasePermission):
    message = 'Only customers can access this route.'
    
    def has_permission(self, request, view):
        if request.user.groups.filter(name="Customer").exists():
            return True
        
        return False
    