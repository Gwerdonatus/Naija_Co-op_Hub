from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class SavingsPool(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_pools")
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when pool is created
    members = models.ManyToManyField(User, related_name="joined_pools", blank=True)
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1.00)])
    contribution_frequency = models.CharField(
        max_length=50,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')]
    )
    payout_order = models.ManyToManyField(User, related_name="payout_orders", blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Active: {self.is_active})"

    def save(self, *args, **kwargs):
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        super().save(*args, **kwargs)


    def check_pool_completion(self):
        """Check if all members have received their payouts and deactivate the pool."""
        total_members = self.members.count()
        completed_payouts = self.payout_set.filter(is_completed=True).count()
        if total_members > 0 and completed_payouts >= total_members:
            self.is_active = False
            self.save()

class Contribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    savings_pool = models.ForeignKey(SavingsPool, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1.00)])
    date_contributed = models.DateTimeField(auto_now_add=True)
    is_missed = models.BooleanField(default=False)  # Tracks if a user missed a contribution

    def __str__(self):
        return f"{self.user.username} - {self.savings_pool.name} - {self.amount}"

class Payout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    savings_pool = models.ForeignKey(SavingsPool, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1.00)])
    date_paid = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Payout to {self.user.username} from {self.savings_pool.name}"

    def save(self, *args, **kwargs):
        """Mark pool as completed when the last payout is done."""
        super().save(*args, **kwargs)
        self.savings_pool.check_pool_completion()


