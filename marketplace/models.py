from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

LISTING_TYPES = (
    ('normal', 'Normal'),
    ('bulk', 'Bulk Purchase'),
    ('skill', 'Skill'),
    ('wholesale', 'Wholesale'),
)

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES, default='normal')

    def __str__(self):
        return self.title

# New model for bulk purchase details
class BulkPurchase(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='bulk_purchase')
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateTimeField()
    # Track contributors via a through model
    contributors = models.ManyToManyField(User, through='BulkContribution', blank=True)

    def __str__(self):
        return f"BulkPurchase for {self.product.title}"

# Through model to record each contribution
class BulkContribution(models.Model):
    bulk_purchase = models.ForeignKey(BulkPurchase, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    contributed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} contributed {self.amount} to {self.bulk_purchase.product.title}"
    



class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    business_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_holder_name = models.CharField(max_length=255)
    paystack_subaccount_id = models.CharField(max_length=100, blank=True, null=True) 


    def __str__(self):
        return f"{self.user.username}'s Seller Profile"
    
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    shipping_address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Filled when the buyer submits their shipping details."
    )
    shipping_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text="Filled when the buyer submits their shipping details."
    )

    def __str__(self):
        return f"Order #{self.pk} - {self.product.name} for {self.buyer.username}"

