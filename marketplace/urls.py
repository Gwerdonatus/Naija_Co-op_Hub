from django.urls import path
from .views import (
    post_product, product_list, product_detail, add_product, edit_product, delete_product,
    add_to_cart, view_cart, checkout_cart, buy_from_balance, buy_paystack, order_success,
    buy_cart_from_balance, buy_cart_paystack, shipping_details, seller_registration,
    ProductListCreateAPIView, ProductRetrieveUpdateDestroyAPIView, CategoryListAPIView,
    BulkPurchaseListCreateAPIView, BulkPurchaseRetrieveUpdateDestroyAPIView, BulkContributionAPIView
)

app_name = 'marketplace'

urlpatterns = [
    # Template-based views
    path('post/', post_product, name='post_product'),
    path('', product_list, name='product_list'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add/', add_product, name='add_product'),
    path('edit/<int:product_id>/', edit_product, name='edit_product'),
    path('delete/<int:product_id>/', delete_product, name='delete_product'),
    
    # Product API endpoints
    path('api/products/', ProductListCreateAPIView.as_view(), name='api-product-list-create'),
    path('api/products/<int:pk>/', ProductRetrieveUpdateDestroyAPIView.as_view(), name='api-product-detail'),
    path('api/categories/', CategoryListAPIView.as_view(), name='api-category-list'),
    
    # Bulk Purchase API endpoints
    path('api/bulk-purchases/', BulkPurchaseListCreateAPIView.as_view(), name='api-bulk-purchase-list-create'),
    path('api/bulk-purchases/<int:pk>/', BulkPurchaseRetrieveUpdateDestroyAPIView.as_view(), name='api-bulk-purchase-detail'),
    path('api/bulk-purchases/<int:bulk_id>/contribute/', BulkContributionAPIView.as_view(), name='api-bulk-contribute'),

    # New Cart & Payment URLs
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('checkout/', checkout_cart, name='checkout_cart'),
    path('cart/buy/balance/', buy_cart_from_balance, name='buy_cart_from_balance'),
    path('cart/buy/paystack/', buy_cart_paystack, name='buy_cart_paystack'),

    # Payment endpoints for individual product purchases
    path('buy_from_balance/<int:product_id>/', buy_from_balance, name='buy_from_balance'),
    path('buy_paystack/<int:product_id>/', buy_paystack, name='buy_paystack'),
    path('order_success/<int:order_id>/', order_success, name='order_success'),
    path('seller/register/', seller_registration, name='seller_registration'),
    path('shipping/<int:order_id>/', shipping_details, name='shipping_details'),
]
