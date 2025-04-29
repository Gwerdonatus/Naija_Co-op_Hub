from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    ROLE_CHOICES = [
        ('investor', 'Investor'),
        ('cooperative_member', 'Cooperative Member'),
        ('business_owner', 'Business Owner'),
        ('retailer', 'Retailer'),
        ('wholesaler', 'Wholesaler'),
        ('skilled_professional', 'Skilled Professional'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default-profile.png'
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='cooperative_member')
    
    # Additional fields for a unified profile
    bio = models.TextField(blank=True, null=True)
    custom_url = models.SlugField(
        max_length=100, 
        blank=True, 
        null=True, 
        unique=True, 
        help_text="Optional custom URL for your profile"
    )
    skills = models.ManyToManyField(Skill, blank=True, related_name='profiles')

    # Financial overview fields
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    investment_returns = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Adashe (Esusu) Contributions & Payouts fields
    adashe_cycle = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Current Adashe savings cycle"
    )
    total_adashe_contributions = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    next_contribution_date = models.DateField(blank=True, null=True)
    next_payout_date = models.DateField(blank=True, null=True)
    expected_payout = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Membership details
    cooperative_name = models.CharField(max_length=255, blank=True, null=True)
    membership_role = models.CharField(
        max_length=50,
        choices=[('Member', 'Member'), ('Admin', 'Admin')],
        default='Member'
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signals to automatically create and save profiles on User creation/update
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


