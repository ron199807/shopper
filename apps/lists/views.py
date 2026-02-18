from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q
from .models import ShoppingList
from .serializers import (
    ShoppingListSerializer, CreateShoppingListSerializer,
    ShoppingListStatusUpdateSerializer, BidOnShoppingListSerializer
)
from .permissions import IsClient, IsListOwner, IsListOpenForBids
from apps.bids.models import Bid

class ClientShoppingListCreateView(generics.CreateAPIView):
    """
    POST /api/lists/
    Create a new shopping list (Client only)
    """
    serializer_class = CreateShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]
    
    def perform_create(self, serializer):
        serializer.save()

class ClientShoppingListView(generics.ListAPIView):
    """
    GET /api/lists/
    Get all shopping lists created by the authenticated client
    """
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]
    
    def get_queryset(self):
        return ShoppingList.objects.filter(
            client=self.request.user
        ).select_related('client').prefetch_related('bids').order_by('-created_at')

class ClientShoppingListDetailView(generics.RetrieveAPIView):
    """
    GET /api/lists/{id}/
    Get detailed information about a specific shopping list
    """
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient, IsListOwner]
    
    def get_queryset(self):
        return ShoppingList.objects.filter(client=self.request.user)

class ClientShoppingListBidsView(generics.ListAPIView):
    """
    GET /api/lists/{id}/bids/
    Get all bids for a specific shopping list (Client only)
    """
    serializer_class = BidOnShoppingListSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient, IsListOwner]
    
    def get_queryset(self):
        shopping_list_id = self.kwargs['pk']
        return Bid.objects.filter(
            shopping_list_id=shopping_list_id,
            is_active=True
        ).select_related('shopper').order_by('amount')

class ClientAcceptBidView(APIView):
    """
    POST /api/lists/{id}/accept-bid/{bid_id}/
    Accept a bid and assign shopper (Client only)
    """
    permission_classes = [permissions.IsAuthenticated, IsClient, IsListOwner, IsListOpenForBids]
    
    def post(self, request, pk, bid_id):
        try:
            shopping_list = ShoppingList.objects.get(id=pk, client=request.user)
            bid = Bid.objects.get(id=bid_id, shopping_list=shopping_list, is_active=True)
        except (ShoppingList.DoesNotExist, Bid.DoesNotExist):
            return Response(
                {'error': 'Shopping list or bid not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mark this bid as won and close other bids
        bid.mark_as_won()
        
        serializer = ShoppingListSerializer(shopping_list)
        return Response(serializer.data)

class ClientUpdateListStatusView(generics.UpdateAPIView):
    """
    PATCH /api/lists/{id}/status/
    Update shopping list status (e.g., cancel)
    """
    serializer_class = ShoppingListStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient, IsListOwner]
    
    def get_queryset(self):
        return ShoppingList.objects.filter(client=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save()

class OpenShoppingListsView(generics.ListAPIView):
    """
    GET /api/lists/open/
    Get all open shopping lists (public, for shoppers to browse)
    """
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can browse open lists
    
    def get_queryset(self):
        now = timezone.now()
        return ShoppingList.objects.filter(
            status='open',
            bidding_deadline__gt=now
        ).select_related('client').order_by('-created_at')[:50]  # Limit to 50 most recent

class NearbyShoppingListsView(generics.ListAPIView):
    """
    GET /api/lists/nearby/?lat={lat}&lng={lng}&radius={radius}
    Get open shopping lists near a location
    """
    serializer_class = ShoppingListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius', 10)  # Default 10 miles/km
        
        if not lat or not lng:
            return ShoppingList.objects.none()
        
        # Note: In production, use PostGIS for proper distance calculations
        # This is a simplified version
        now = timezone.now()
        return ShoppingList.objects.filter(
            status='open',
            bidding_deadline__gt=now
        ).select_related('client').order_by('-created_at')[:50]