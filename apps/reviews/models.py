from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    # Who is reviewing whom
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    
    # Related shopping list
    shopping_list = models.OneToOneField(
        'lists.ShoppingList',
        on_delete=models.CASCADE,
        related_name='review'
    )
    
    # Review details
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=500, blank=True)
    
    # Categories (for detailed feedback)
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    timeliness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    accuracy_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['reviewer', 'shopping_list']  # One review per list per person
        indexes = [
            models.Index(fields=['reviewee', 'rating']),
        ]
    
    def __str__(self):
        return f"{self.reviewer.email} -> {self.reviewee.email}: {self.rating}★"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update user's average rating
        from django.db.models import Avg
        avg_rating = Review.objects.filter(reviewee=self.reviewee).aggregate(Avg('rating'))
        self.reviewee.average_rating = avg_rating['rating__avg'] or 0
        self.reviewee.save()