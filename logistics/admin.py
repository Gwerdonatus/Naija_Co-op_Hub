from django.contrib import admin
from .models import LogisticCompany

@admin.register(LogisticCompany)
class LogisticCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'applied_on')
    list_filter = ('status', 'applied_on')
    search_fields = ('name', 'email')
