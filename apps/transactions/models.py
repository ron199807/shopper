from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    )
    
    # Relationships
    shopping_list = models.OneToOneField(
        'lists.ShoppingList',
        on_delete=models.CASCADE,
        related_name='transaction'
    )
    bid = models.OneToOneField(
        'bids.Bid',
        on_delete=models.CASCADE,
        related_name='transaction'
    )
    
    # Amounts
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)
    shopper_payout = models.DecimalField(max_digits=10, decimal_places=2)
    total_charged = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment details
    payment_method = models.CharField(max_length=50)  # stripe, paypal, etc.
    payment_intent_id = models.CharField(max_length=255, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Transaction {self.id} - {self.shopping_list.title}"
    
    def calculate_fees(self):
        """Calculate platform fee and shopper payout"""
        self.platform_fee = self.bid_amount * (self.shopping_list.platform_fee_percentage / 100)
        self.shopper_payout = self.bid_amount - self.platform_fee
        self.total_charged = self.bid_amount  # Client pays the bid amount

class Payout(models.Model):
    """Shopper payouts"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    shopper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name='payout'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payout_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)