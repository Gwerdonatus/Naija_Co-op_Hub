from django.contrib import admin
from .models import Product, Category
from .models import SellerProfile

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(SellerProfile)

