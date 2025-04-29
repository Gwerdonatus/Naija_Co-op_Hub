from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'adashe_cycle', 'total_adashe_contributions', 'next_contribution_date', 'next_payout_date', 'expected_payout')

admin.site.register(Profile, ProfileAdmin)
