from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Bid(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('withdrawn', 'Withdrawn'),
    )
    
    # Shopper placing the bid
    shopper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bids',
        limit_choices_to={'user_type__in': ['shopper', 'both']}
    )
    
    # Shopping list being bid on
    shopping_list = models.ForeignKey(
        'lists.ShoppingList',
        on_delete=models.CASCADE,
        related_name='bids'
    )
    
    # Bid details
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    
    # Shopper's message to client
    message = models.TextField(max_length=500, blank=True)
    
    # Estimated shopping time (in minutes)
    estimated_time = models.IntegerField(help_text="Estimated shopping time in minutes")
    
    # Distance from shopper to store (calculated at bid time)
    distance_to_store = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        help_text="Distance in miles/km"
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['amount']  # Lowest bid first
        unique_together = ['shopper', 'shopping_list']  # Shopper can only bid once per list
        indexes = [
            models.Index(fields=['shopping_list', 'status']),
            models.Index(fields=['shopper', 'status']),
        ]
    
    def __str__(self):
        return f"${self.amount} - {self.shopper.email} - {self.shopping_list.title}"
    
    def mark_as_won(self):
        """Mark this bid as won and all others as lost"""
        self.status = 'won'
        self.save()
        
        # Mark all other bids on this list as lost
        self.shopping_list.bids.exclude(id=self.id).update(
            status='lost',
            is_active=False
        )
        
        # Update the shopping list
        self.shopping_list.selected_shopper = self.shopper
        self.shopping_list.status = 'assigned'
        self.shopping_list.save()

class BidHistory(models.Model):
    """Track bid changes for audit"""
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name='history')
    old_amount = models.DecimalField(max_digits=10, decimal_places=2)
    new_amount = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-changed_at']