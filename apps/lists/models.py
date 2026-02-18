from django.db import models
from django.conf import settings
from django.utils import timezone

class ShoppingList(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open for Bids'),
        ('bidding_closed', 'Bidding Closed'),
        ('assigned', 'Shopper Assigned'),
        ('in_progress', 'Shopping in Progress'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )
    
    # Client who posted the list
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='posted_lists',
        limit_choices_to={'user_type__in': ['client', 'both']}
    )
    
    # List details
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Store details
    store_name = models.CharField(max_length=200)
    store_address = models.CharField(max_length=255)
    store_city = models.CharField(max_length=100)
    
    # Shopping list items (stored as JSON for flexibility)
    items = models.JSONField()  # [{"name": "Milk", "quantity": 2, "estimated_price": 3.99}, ...]
    
    # Budget and pricing
    estimated_total = models.DecimalField(max_digits=10, decimal_places=2)
    max_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Fees (your platform commission)
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    # Timeline
    preferred_delivery_time = models.DateTimeField()
    bidding_deadline = models.DateTimeField()
    expires_at = models.DateTimeField()
    
    # Location for distance calculation
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Selected shopper (when assigned)
    selected_shopper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_lists',
        limit_choices_to={'user_type__in': ['shopper', 'both']}
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['bidding_deadline']),
            models.Index(fields=['store_city']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.client.email}"
    
    @property
    def bid_count(self):
        return self.bids.count()
    
    @property
    def lowest_bid(self):
        return self.bids.filter(is_active=True).order_by('amount').first()
    
    def close_bidding(self):
        """Close bidding when deadline passes"""
        if timezone.now() >= self.bidding_deadline and self.status == 'open':
            self.status = 'bidding_closed'
            self.save()

class ShoppingListItem(models.Model):
    """Optional: If you want more structured items instead of JSON"""
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items_structured')
    name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    unit = models.CharField(max_length=20, blank=True)  # kg, liters, pieces, etc.
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)  # e.g., "organic only", "any brand"
    
    def __str__(self):
        return f"{self.quantity}x {self.name}"
