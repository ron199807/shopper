from rest_framework import permissions

class IsClient(permissions.BasePermission):
    """
    Allows access only to users who are clients.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['client', 'both']

class IsListOwner(permissions.BasePermission):
    """
    Allows access only to the client who owns the shopping list.
    """
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user

class IsListOpenForBids(permissions.BasePermission):
    """
    Allows actions only if the shopping list is open for bids.
    """
    def has_object_permission(self, request, view, obj):
        return obj.status == 'open'