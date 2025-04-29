from rest_framework import serializers
from .models import Product, Category, BulkPurchase

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source='seller.username')  # Display seller's username

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'image', 'category', 'seller', 'timestamp', 'listing_type']

# Serializer for bulk purchase details
class BulkPurchaseSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = BulkPurchase
        fields = ['id', 'product', 'product_id', 'target_amount', 'collected_amount', 'deadline']
