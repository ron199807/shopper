from rest_framework import serializers
from django.utils import timezone
from .models import ShoppingList, ShoppingListItem
from apps.users.serializers import UserSerializer

class ShoppingListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingListItem
        fields = ['id', 'name', 'quantity', 'unit', 'estimated_price', 'notes']

class ShoppingListSerializer(serializers.ModelSerializer):
    items_structured = ShoppingListItemSerializer(many=True, read_only=True)
    client_details = UserSerializer(source='client', read_only=True)
    bid_count = serializers.IntegerField(read_only=True)
    lowest_bid_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = ShoppingList
        fields = [
            'id', 'title', 'description', 'store_name', 'store_address',
            'store_city', 'items', 'items_structured', 'estimated_total',
            'max_budget', 'platform_fee_percentage', 'preferred_delivery_time',
            'bidding_deadline', 'expires_at', 'delivery_latitude',
            'delivery_longitude', 'status', 'client_details', 'bid_count',
            'lowest_bid_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'status', 'created_at', 'updated_at']
    
    def get_lowest_bid_amount(self, obj):
        lowest_bid = obj.lowest_bid
        return lowest_bid.amount if lowest_bid else None
    
    def validate(self, data):
        # Validate that bidding_deadline is in the future
        if 'bidding_deadline' in data and data['bidding_deadline'] <= timezone.now():
            raise serializers.ValidationError({
                'bidding_deadline': 'Bidding deadline must be in the future'
            })
        
        # Validate that preferred_delivery_time is after bidding_deadline
        if ('preferred_delivery_time' in data and 'bidding_deadline' in data and 
            data['preferred_delivery_time'] <= data['bidding_deadline']):
            raise serializers.ValidationError({
                'preferred_delivery_time': 'Delivery time must be after bidding deadline'
            })
        
        return data

class CreateShoppingListSerializer(serializers.ModelSerializer):
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ShoppingList
        fields = [
            'title', 'description', 'store_name', 'store_address',
            'store_city', 'items', 'items_data', 'estimated_total',
            'max_budget', 'preferred_delivery_time', 'bidding_deadline',
            'delivery_latitude', 'delivery_longitude'
        ]
    
    def validate_items_data(self, value):
        """Validate the structured items data"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Items must be a list")
        
        for item in value:
            required_fields = ['name', 'quantity']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Each item must have a '{field}' field")
            
            if not isinstance(item.get('quantity', 0), (int, float)) or item.get('quantity', 0) <= 0:
                raise serializers.ValidationError("Quantity must be a positive number")
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items_data', [])
        
        # Create the shopping list
        shopping_list = ShoppingList.objects.create(
            client=self.context['request'].user,
            **validated_data
        )
        
        # Create structured items if provided
        for item_data in items_data:
            ShoppingListItem.objects.create(
                shopping_list=shopping_list,
                **item_data
            )
        
        return shopping_list

class ShoppingListStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ['status']
    
    def validate_status(self, value):
        valid_statuses = ['cancelled']  # Clients can only cancel their lists
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status can only be changed to: {', '.join(valid_statuses)}")
        return value

class BidOnShoppingListSerializer(serializers.Serializer):
    """Serializer for viewing bids on a shopping list (client view)"""
    id = serializers.IntegerField()
    shopper_email = serializers.EmailField(source='shopper.email')
    shopper_name = serializers.CharField(source='shopper.get_full_name')
    shopper_rating = serializers.FloatField(source='shopper.average_rating')
    shopper_completed_jobs = serializers.IntegerField(source='shopper.completed_jobs')
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    message = serializers.CharField()
    estimated_time = serializers.IntegerField()
    distance_to_store = serializers.DecimalField(max_digits=6, decimal_places=2)
    created_at = serializers.DateTimeField()