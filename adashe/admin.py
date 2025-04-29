# Register your models here.
from django.contrib import admin
from .models import SavingsPool, Contribution, Payout

@admin.register(SavingsPool)
class SavingsPoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'start_date', 'end_date', 'contribution_amount', 'contribution_frequency', 'is_active')
    list_filter = ('contribution_frequency', 'is_active', 'created_by')
    search_fields = ('name', 'created_by__username')
    filter_horizontal = ('members', 'payout_order',)
    ordering = ('-created_at',)

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('user', 'savings_pool', 'amount', 'date_contributed', 'is_missed')
    list_filter = ('savings_pool', 'user')
    search_fields = ('user__username', 'savings_pool__name')
    ordering = ('-date_contributed',)

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'savings_pool', 'amount', 'date_paid', 'is_completed')
    list_filter = ('savings_pool', 'user', 'is_completed')
    search_fields = ('user__username', 'savings_pool__name')
    ordering = ('-date_paid',)
