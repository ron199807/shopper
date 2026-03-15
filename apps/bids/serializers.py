from rest_framework import serializers
from django.utils import timezone
from .models import Bid, BidHistory
from apps.lists.models import ShoppingList
from apps.users.serializers import UserSerializer

class BidSerializer(serializers.ModelSerializer):
    shopper_details = UserSerializer(source='shopper', read_only=True)
    shopping_list_title = serializers.CharField(source='shopping_list.title', read_only=True)
    
    class Meta:
        model = Bid
        fields = [
            'id', 'shopper', 'shopper_details', 'shopping_list',
            'shopping_list_title', 'amount', 'message', 'estimated_time',
            'distance_to_store', 'status', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'shopper', 'status', 'created_at', 'updated_at']

class CreateBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['shopping_list', 'amount', 'message', 'estimated_time', 'distance_to_store']
    
    def validate(self, data):
        shopping_list = data['shopping_list']
        user = self.context['request'].user
        
        # Check if shopping list is open for bids
        if shopping_list.status != 'open':
            raise serializers.ValidationError(
                "This shopping list is not open for bids"
            )
        
        # Check if bidding deadline hasn't passed
        if timezone.now() >= shopping_list.bidding_deadline:
            raise serializers.ValidationError(
                "Bidding deadline has passed for this list"
            )
        
        # Check if user has already bid on this list
        if Bid.objects.filter(shopper=user, shopping_list=shopping_list).exists():
            raise serializers.ValidationError(
                "You have already placed a bid on this list"
            )
        
        # Check if user is a shopper
        if user.user_type not in ['shopper', 'both']:
            raise serializers.ValidationError(
                "Only shoppers can place bids"
            )
        
        # Validate amount (optional: add minimum bid logic)
        if data['amount'] <= 0:
            raise serializers.ValidationError(
                "Bid amount must be greater than 0"
            )
        
        return data
    
    def create(self, validated_data):
        validated_data['shopper'] = self.context['request'].user
        return super().create(validated_data)

class UpdateBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['amount', 'message', 'estimated_time']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be greater than 0")
        return value
    
    def validate(self, data):
        bid = self.instance
        
        # Check if bid is still active
        if not bid.is_active or bid.status != 'active':
            raise serializers.ValidationError("Cannot update an inactive bid")
        
        # Check if shopping list is still open
        if bid.shopping_list.status != 'open':
            raise serializers.ValidationError(
                "Cannot update bid because shopping list is no longer open"
            )
        
        return data

class ShoppingListForShopperSerializer(serializers.ModelSerializer):
    """
    Simplified shopping list serializer for shoppers browsing open lists
    """
    client_name = serializers.CharField(source='client.get_full_name')
    client_rating = serializers.FloatField(source='client.average_rating')
    client_total_lists = serializers.IntegerField(source='client.total_lists_posted')
    total_count = serializers.IntegerField(read_only=True)
    lowest_bid = serializers.SerializerMethodField()
    
    class Meta:
        model = ShoppingList
        fields = [
            'id', 'title', 'description', 'store_name', 'store_address',
            'store_city', 'estimated_total', 'max_budget', 'preferred_delivery_time',
            'bidding_deadline', 'delivery_latitude', 'delivery_longitude',
            'client_name', 'client_rating', 'client_total_lists',
            'total_count', 'lowest_bid', 'created_at'
        ]
    
    def get_lowest_bid(self, obj):
        lowest = obj.lowest_bid
        return {
            'amount': float(lowest.amount) if lowest else None,
            'bidder_count': obj.bid_count
        }

class BidHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BidHistory
        fields = ['old_amount', 'new_amount', 'changed_at']