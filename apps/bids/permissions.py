from rest_framework import permissions
from django.utils import timezone
from apps.bids.models import Bid

class IsShopper(permissions.BasePermission):
    """
    Allows access only to users who are shoppers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in ['shopper', 'both']

class IsBidOwner(permissions.BasePermission):
    """
    Allows access only to the shopper who owns the bid.
    """
    def has_object_permission(self, request, view, obj):
        return obj.shopper == request.user

class IsBidActive(permissions.BasePermission):
    """
    Allows actions only if the bid is active.
    """
    def has_object_permission(self, request, view, obj):
        return obj.is_active and obj.status == 'active'

class CanPlaceBid(permissions.BasePermission):
    """
    Check if user can place a bid on a specific shopping list.
    """
    def has_object_permission(self, request, view, obj):
        # obj here is the ShoppingList
        return (obj.status == 'open' and 
                obj.bidding_deadline > timezone.now() and
                not Bid.objects.filter(shopper=request.user, shopping_list=obj).exists())