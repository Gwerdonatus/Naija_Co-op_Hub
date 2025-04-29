from django.db import models
from django.contrib.auth.models import User
from marketplace.models import Product

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - ₦{self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('contribution', 'Contribution'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default="pending")  # pending, completed, failed
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    cart_data = models.JSONField(null=True, blank=True)
    pool = models.ForeignKey(
        'adashe.SavingsPool', null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} - {self.status}"

