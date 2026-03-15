from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import Bid, BidHistory
from apps.lists.models import ShoppingList
from .serializers import (
    BidSerializer, CreateBidSerializer, UpdateBidSerializer,
    ShoppingListForShopperSerializer, BidHistorySerializer
)
from .permissions import IsShopper, IsBidOwner, IsBidActive
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, extend_schema_view
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    get=extend_schema(
        tags=['Dashboard'],
        summary="Shopper dashboard",
        description="Get shopper dashboard with statistics and recent activity.",
        responses={200: OpenApiTypes.OBJECT},
    )
)

class ShopperDashboardView(generics.GenericAPIView):
    """
    GET /api/bids/dashboard/
    Get shopper dashboard with stats and recent activity
    """
    permission_classes = [permissions.IsAuthenticated, IsShopper]
    
    def get(self, request):
        user = request.user
        now = timezone.now()
        
        # Get counts
        active_bids = Bid.objects.filter(
            shopper=user, 
            is_active=True, 
            status='active'
        ).count()
        
        won_bids = Bid.objects.filter(
            shopper=user, 
            status='won'
        ).count()
        
        completed_bids = Bid.objects.filter(
            shopper=user,
            shopping_list__status='delivered'
        ).count()
        
        # Get recent bids
        recent_bids = Bid.objects.filter(
            shopper=user
        ).select_related('shopping_list').order_by('-created_at')[:5]
        
        # Get open lists nearby (simplified - you'd use PostGIS for real distance)
        nearby_lists = ShoppingList.objects.filter(
            status='open',
            bidding_deadline__gt=now
        ).annotate(
            total_count=Count('bids')
        ).order_by('-created_at')[:10]
        
        data = {
            'stats': {
                'active_bids': active_bids,
                'won_bids': won_bids,
                'completed_bids': completed_bids,
                'total_earnings': 0,  # Calculate from completed transactions
                'average_rating': user.average_rating,
                'completed_jobs': user.completed_jobs,
            },
            'recent_bids': BidSerializer(recent_bids, many=True).data,
            'nearby_lists': ShoppingListForShopperSerializer(nearby_lists, many=True).data
        }
        
        return Response(data)
    
@extend_schema_view(
    get=extend_schema(
        tags=['Bids'],
        summary="Get available lists",
        description="Get all shopping lists available for bidding.",
        parameters=[
            OpenApiParameter(name='city', description='Filter by city', required=False, type=str),
            OpenApiParameter(name='max_distance', description='Maximum distance in miles/km', required=False, type=float),
        ],
        responses={200: ShoppingListForShopperSerializer(many=True)},
    )
)

class AvailableListsView(generics.ListAPIView):
    """
    GET /api/bids/available-lists/
    Get all shopping lists available for bidding
    """
    serializer_class = ShoppingListForShopperSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        now = timezone.now()
        queryset = ShoppingList.objects.filter(
            status='open',
            bidding_deadline__gt=now
        ).annotate(
            total_count=Count('bids')
        ).select_related('client').order_by('bidding_deadline')
        
        # Filter by city if provided
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(store_city__icontains=city)
        
        # Filter by max distance (simplified)
        max_distance = self.request.query_params.get('max_distance')
        if max_distance:
            # In production, you'd filter by actual distance using PostGIS
            pass
        
        return queryset

@extend_schema_view(
    get=extend_schema(
        tags=['Bids'],
        summary="Get list details for shoppers",
        description="Get detailed information about a specific list for bidding.",
        responses={200: ShoppingListForShopperSerializer},
    )
)

class ListDetailForShopperView(generics.RetrieveAPIView):
    """
    GET /api/bids/lists/{id}/
    Get detailed information about a specific list for bidding
    """
    serializer_class = ShoppingListForShopperSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopper]
    queryset = ShoppingList.objects.filter(status='open')

@extend_schema_view(
    post=extend_schema(
        tags=['Bids'],
        summary="Place a bid",
        description="Place a new bid on a shopping list.",
        request=CreateBidSerializer,
        responses={201: BidSerializer},
    )
)

class PlaceBidView(generics.CreateAPIView):
    """
    POST /api/bids/
    Place a new bid on a shopping list
    """
    serializer_class = CreateBidSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopper]
    
    def perform_create(self, serializer):
        serializer.save()

@extend_schema_view(
    get=extend_schema(
        tags=['Bids'],
        summary="Get my bids",
        description="Get all bids placed by the authenticated shopper.",
        parameters=[
            OpenApiParameter(name='status', description='Filter by status (active, won, lost, withdrawn)', required=False, type=str),
        ],
        responses={200: BidSerializer(many=True)},
    )
)

class MyBidsView(generics.ListAPIView):
    """
    GET /api/bids/my-bids/
    Get all bids placed by the authenticated shopper
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopper]
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status')
        
        queryset = Bid.objects.filter(
            shopper=user
        ).select_related(
            'shopping_list', 'shopper'
        ).order_by('-created_at')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset


@extend_schema_view(
    get=extend_schema(
        tags=['Bids'],
        summary="Get bid details",
        description="Get detailed information about a specific bid.",
        responses={200: BidSerializer},
    )
)

class ListBidsView(generics.ListAPIView):
    """
    GET /api/lists/{id}/bids/
    Get all bids for a specific shopping list
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        list_id = self.kwargs['pk']
        shopping_list = get_object_or_404(ShoppingList, id=list_id)
        user = self.request.user
        
        # Different access levels based on user type and ownership
        if user == shopping_list.client:
            # Client can see all bids on their list
            return Bid.objects.filter(
                shopping_list_id=list_id
            ).select_related('shopper').order_by('-amount')
        elif user.user_type in ['shopper', 'both']:
            # Shoppers can only see their own bids on this list
            return Bid.objects.filter(
                shopping_list_id=list_id,
                shopper=user
            ).select_related('shopper')
        else:
            # No access for others
            return Bid.objects.none()

class BidDetailView(generics.RetrieveAPIView):
    """
    GET /api/bids/{id}/
    Get detailed information about a specific bid
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopper, IsBidOwner]
    queryset = Bid.objects.all()

@extend_schema_view(
    patch=extend_schema(
        tags=['Bids'],
        summary="Update a bid",
        description="Update an existing bid. Only active bids can be updated.",
        request=UpdateBidSerializer,
        responses={200: BidSerializer},
    )
)

class UpdateBidView(generics.UpdateAPIView):
    """
    PUT/PATCH /api/bids/{id}/
    Update an existing bid
    """
    serializer_class = UpdateBidSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopper, IsBidOwner, IsBidActive]
    queryset = Bid.objects.all()
    
    def perform_update(self, serializer):
        # Save old amount for history
        old_amount = self.get_object().amount
        
        # Update the bid
        serializer.save()
        
        # Create history entry
        BidHistory.objects.create(
            bid=self.get_object(),
            old_amount=old_amount,
            new_amount=serializer.validated_data.get('amount', old_amount),
            changed_by=self.request.user
        )

@extend_schema(
    tags=['Bids'],
    summary="Withdraw a bid",
    description="Withdraw an active bid.",
    responses={200: OpenApiTypes.OBJECT},
)

class WithdrawBidView(APIView):
    """
    POST /api/bids/{id}/withdraw/
    Withdraw an active bid
    """
    permission_classes = [permissions.IsAuthenticated, IsShopper, IsBidOwner, IsBidActive]
    
    def post(self, request, pk):
        bid = get_object_or_404(Bid, id=pk)
        
        # Check if shopping list is still open
        if bid.shopping_list.status != 'open':
            return Response(
                {'error': 'Cannot withdraw bid after shopping list is closed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bid.status = 'withdrawn'
        bid.is_active = False
        bid.save()
        
        return Response({'message': 'Bid withdrawn successfully'})
    
@extend_schema_view(
    get=extend_schema(
        tags=['Bids'],
        summary="Get bid history",
        description="Get history of changes to a bid.",
        responses={200: BidHistorySerializer(many=True)},
    )
)

class BidHistoryView(generics.ListAPIView):
    """
    GET /api/bids/{id}/history/
    Get history of changes to a bid
    """
    serializer_class = BidHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsShopper, IsBidOwner]
    
    def get_queryset(self):
        return BidHistory.objects.filter(bid_id=self.kwargs['pk']).order_by('-changed_at')
    
@extend_schema_view(
    get=extend_schema(
        tags=['Bids'],
        summary="Get won bids",
        description="Get all bids that the shopper has won.",
        responses={200: BidSerializer(many=True)},
    )
)

class MyWonBidsView(generics.ListAPIView):
    """
    GET /api/bids/won/
    Get all bids that the shopper has won
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopper]
    
    def get_queryset(self):
        return Bid.objects.filter(
            shopper=self.request.user,
            status='won'
        ).select_related('shopping_list').order_by('-updated_at')