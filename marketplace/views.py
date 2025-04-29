# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages

# Standard library imports
import uuid
import sys
from decimal import Decimal

# Models imports
from .models import Product, Category, BulkPurchase, BulkContribution, SellerProfile, Order
from payments.models import Wallet, Transaction
from notifications.models import Notification

# Forms imports
from .forms import ProductForm, SellerProfileForm
from marketplace.models import Product
from django.core.serializers.json import DjangoJSONEncoder


# Utility functions
from payments.utils import initialize_payment, create_paystack_subaccount


# ---------------------------
# Template-based Views (existing)
# ---------------------------
@login_required
def post_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user  # Assign current user as seller
            product.save()
            return redirect('marketplace:product_list')
    else:
        form = ProductForm()
    return render(request, 'marketplace/post_product.html', {'form': form})

def product_list(request):
    query = request.GET.get('query', '')
    category_filter = request.GET.get('category', '')

    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category_filter:
        products = products.filter(category__id=category_filter)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()

    return render(request, 'marketplace/product_list.html', {
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'selected_category': category_filter
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'marketplace/product_detail.html', {'product': product})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('marketplace:product_list')
    else:
        form = ProductForm()
    return render(request, 'marketplace/add_product.html', {'form': form})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user != product.seller:
        return redirect('marketplace:product_list')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('marketplace:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'marketplace/edit_product.html', {'form': form, 'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user == product.seller:
        product.delete()
        return HttpResponseRedirect(reverse('marketplace:product_list'))
    else:
        return redirect('marketplace:product_list')

# ---------------------------
# API Views (Django REST Framework)
# ---------------------------
from rest_framework import generics, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSerializer, CategorySerializer, BulkPurchaseSerializer

# Product API views (already provided)
class ProductListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-timestamp')
        query = self.request.query_params.get('query', None)
        category_filter = self.request.query_params.get('category', None)
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if category_filter:
            queryset = queryset.filter(category__id=category_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all()

    def perform_update(self, serializer):
        product = self.get_object()
        if self.request.user != product.seller:
            raise PermissionDenied("You can only update your own product.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.seller:
            raise PermissionDenied("You can only delete your own product.")
        instance.delete()

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

# Bulk Purchase API Views
class BulkPurchaseListCreateAPIView(generics.ListCreateAPIView):
    """
    List all bulk purchase opportunities or create a new one.
    (Only products marked as 'bulk' should be linked here.)
    """
    serializer_class = BulkPurchaseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = BulkPurchase.objects.all().order_by('-product__timestamp')

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        if product.listing_type != 'bulk':
            raise serializers.ValidationError("Product is not marked as bulk purchase.")
        serializer.save()

class BulkPurchaseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BulkPurchaseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = BulkPurchase.objects.all()

    def perform_update(self, serializer):
        bulk_purchase = self.get_object()
        if self.request.user != bulk_purchase.product.seller:
            raise PermissionDenied("You can only update your own bulk purchase.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.product.seller:
            raise PermissionDenied("You can only delete your own bulk purchase.")
        instance.delete()

# API view to allow users to contribute to a bulk purchase
class BulkContributionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, bulk_id):
        bulk_purchase = get_object_or_404(BulkPurchase, id=bulk_id)
        amount = request.data.get('amount')
        try:
            amount = Decimal(amount)
        except:
            return Response({"error": "Invalid amount"}, status=400)
        # Create contribution record
        BulkContribution.objects.create(
            bulk_purchase=bulk_purchase,
            user=request.user,
            amount=amount
        )
        bulk_purchase.collected_amount += amount
        bulk_purchase.save()
        return Response({
            "message": "Contribution added",
            "collected_amount": bulk_purchase.collected_amount
        })

# ---------------------------
# Cart & Payment Views
# ---------------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', [])
    if product.id not in cart:
        cart.append(product.id)
        request.session['cart'] = cart
    # Redirect to product detail with a query parameter to trigger the "Added to Cart" modal
    return redirect(f"{reverse('marketplace:product_detail', args=[product.id])}?added_to_cart=1")

@login_required
def view_cart(request):
    cart_ids = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart_ids)
    return render(request, 'marketplace/cart.html', {'products': products})

@login_required
def checkout_cart(request):
    cart_ids = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart_ids)
    if not products:
        messages.error(request, "Your cart is empty.")
        return redirect('marketplace:product_list')
    total = sum(product.price for product in products)
    return render(request, 'marketplace/checkout_cart.html', {'products': products, 'total': total})

@login_required
def buy_cart_from_balance(request):
    cart_ids = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart_ids)
    total = sum(product.price for product in products)
    wallet, created = Wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0.00')})
    if wallet.balance >= total:
        wallet.balance -= total
        wallet.save()
        # Clear the cart after successful purchase
        request.session['cart'] = []
        order_details = {
            'product_titles': [product.title for product in products],
            'total_price': str(total),
            'wallet_balance': str(wallet.balance),
            'message': "Purchase successful! Your balance has been updated."
        }
        request.session['order_success_data'] = order_details
        messages.success(request, "Purchase successful! Your balance has been updated.")
        return redirect('marketplace:order_success')
    else:
        messages.error(request, "Insufficient funds. Please add money to your wallet.")
        return redirect('marketplace:checkout_cart')

from django.core.serializers.json import DjangoJSONEncoder

@login_required
def buy_cart_paystack(request):
    cart_ids = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart_ids)
    
    if not products:
        messages.error(request, "Your cart is empty.")
        return redirect('marketplace:checkout_cart')
    
    total = sum(product.price for product in products)
    reference = str(uuid.uuid4())
    response = initialize_payment(request.user.email, total, reference)

    if response.get("status"):
        Transaction.objects.create(
            user=request.user,
            transaction_type="purchase",
            amount=total,
            reference=reference,
            status="pending",
            cart_data=json.dumps(cart_ids, cls=DjangoJSONEncoder)  # Save cart info
        )
        return redirect(response["data"]["authorization_url"])
    else:
        messages.error(request, "Error initiating payment. Please try again.")
        return redirect('marketplace:checkout_cart')


@login_required
def buy_from_balance(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user, defaults={'balance': Decimal('0.00')})
    
    if wallet.balance >= product.price:
        # Deduct the product price from the user's wallet
        wallet.balance -= product.price
        wallet.save()
        
        # Create the Order object
        order = Order.objects.create(
            buyer=request.user,
            product=product,
            status='paid'  # You can change this status as per your workflow
        )
        
        # Prepare order success details to be used on the success page
        order_details = {
            'product_title': product.title,
            'product_price': str(product.price),
            'wallet_balance': str(wallet.balance),
            'message': "Purchase successful! Your balance has been updated."
        }
        request.session['order_success_data'] = order_details
        
        messages.success(request, "Purchase successful! Your balance has been updated.")
        
        # Redirect to order success page with the newly created order's ID
        return redirect('marketplace:order_success', order_id=order.id)
    else:
        messages.error(request, "Insufficient funds. Please add money to your wallet.")
        product_detail_url = reverse('marketplace:product_detail', args=[product.id])
        return redirect(f"{product_detail_url}?insufficient_funds=1")




@login_required
def buy_paystack(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reference = str(uuid.uuid4())
    
    # Initialize payment for the product price
    response = initialize_payment(request.user.email, product.price, reference)
    
    if response.get("status"):
        Transaction.objects.create(
            user=request.user,
            transaction_type="purchase",
            amount=product.price,
            reference=reference,
            status="pending",
            product=product  # ✅ Link the product here
        )
        return redirect(response["data"]["authorization_url"])
    
    else:
        messages.error(request, "Error initiating payment. Please try again.")
        return redirect('marketplace:product_detail', product_id=product.id)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)

    context = {
        'order': order,
        'order_details': {
            'product_title': order.product.title,  # Changed from 'name' to 'title'
            'product_price': order.product.price,
            'wallet_balance': order.buyer.wallet.balance,
            'message': "Your order was successful!"
        }
    }
    return render(request, 'marketplace/order_success.html', context)





@login_required
def shipping_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        # Update the order with shipping details and status change
        order.shipping_address = address
        order.shipping_phone = phone
        order.status = 'processing'  # or whatever status indicates payment confirmed & shipping details received
        order.save()

        # Create a notification for the seller
        seller = order.product.seller  # Ensure your Order model links to a Product that has a seller field.
        notification_message = (
            f"Your item '{order.product.title}' was purchased. "
            f"Shipping details: {address}, {phone}. Buyer: {order.buyer.username}."
        )
        # Optionally, you can set a link (for example, to view order details)
        notification_link = reverse('marketplace:product_detail', args=[order.product.id])
        Notification.objects.create(
            recipient=seller,
            message=notification_message,
            link=notification_link
        )
        
        messages.success(request, "Shipping details submitted successfully!")
        return redirect('marketplace:order_success', order_id=order.id)

    
    return render(request, 'marketplace/shipping_details.html', {'order': order})



@login_required
def seller_registration(request):
    # Check if user already has a seller profile.
    try:
        seller_profile = request.user.seller_profile
        messages.info(request, "You already have a seller profile.")
        return redirect('marketplace:post_product')  # Adjust redirection as needed.
    except SellerProfile.DoesNotExist:
        seller_profile = None

    if request.method == "POST":
        form = SellerProfileForm(request.POST)
        if form.is_valid():
            seller_profile = form.save(commit=False)
            seller_profile.user = request.user

            # Call Paystack API to create a subaccount using the bank code from the form.
            try:
                subaccount_id = create_paystack_subaccount(
                    business_name=form.cleaned_data['business_name'],
                    bank_code=form.cleaned_data['bank_name'],  # This is now the bank code.
                    account_number=form.cleaned_data['account_number'],
                    percentage_charge=5,  # your commission percentage (if applicable)
                    description=f"Subaccount for {request.user.username}"
                )
                seller_profile.paystack_subaccount_id = subaccount_id
            except Exception as e:
                messages.error(request, f"Error creating Paystack subaccount: {str(e)}")
                return render(request, 'marketplace/seller_registration.html', {'form': form})
            
            seller_profile.save()
            messages.success(request, "Seller registration successful!")
            return redirect('marketplace:post_product')  # Or wherever you want to redirect.
    else:
        form = SellerProfileForm()
    
    return render(request, 'marketplace/seller_registration.html', {'form': form})
