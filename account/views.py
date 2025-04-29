from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import SignupSerializer
from .forms import UserForm, ProfileForm
from .models import Profile
from notifications.models import Notification

from adashe.models import Contribution, Payout
from marketplace.models import Order  # Ensure Order has relationships to Product and Buyer



# HTML Form Views for Signup and Login
def signup_form(request):
    return render(request, 'account/signup.html')


def login_form(request):
    return render(request, 'account/login.html')


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Account successfully created!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {"detail": "Please provide both username and password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            profile_url = request.build_absolute_uri(
                reverse('profile_view', kwargs={'username': user.username})
            )
            return Response(
                {"message": "Login successful!", "profile_url": profile_url},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )


@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    # Removed automatic redirect based on incomplete profile details.
    return render(request, 'account/profile.html', {
        'profile_user': user,
        'profile': profile,
    })


@login_required
def profile_edit(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # After saving, redirect to the main profile page.
            return redirect('profile_view', username=user.username)
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'account/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def dashboard_view(request):
    """User dashboard displaying profile, financial overview, and Adashe contributions."""
    profile = Profile.objects.get(user=request.user)
    user_contributions = Contribution.objects.filter(user=request.user)
    user_payouts = {payout.cycle.id: payout for payout in Payout.objects.filter(user=request.user)}

    context = {
        'profile': profile,
        'user_contributions': user_contributions,
        'user_payouts': user_payouts,
    }

    return render(request, 'account/dashboard.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {'form': form})


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out"}, status=200)


def logout_view(request):
    logout(request)
    return redirect('/')  # Redirect to home page after logout


def shipping_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        
        # Update the order
        order.shipping_address = address
        order.shipping_phone = phone
        order.status = 'processing'
        order.save()

        # Create a notification for the seller
        seller = order.product.seller  # Ensure product has a valid seller
        if seller:
            notification_message = (
                f"Your item '{order.product.name}' was purchased. "
                f"Shipping details: {address}, {phone}. Buyer: {order.buyer.username}."
            )
            notification_link = reverse('order_detail', args=[order.id])
            Notification.objects.create(
                recipient=seller,
                message=notification_message,
                link=notification_link
            )
        else:
            # Optionally log an error if seller is missing
            print(f"Error: No seller found for order {order.id}")

        messages.success(request, "Shipping details submitted successfully!")
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'shipping_details.html', {'order': order})
