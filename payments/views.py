import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Wallet, Transaction
from .utils import initialize_payment
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from adashe.models import Contribution
from decimal import Decimal
from marketplace.models import Order

@login_required
def deposit(request):
    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        reference = str(uuid.uuid4())  # Generate unique reference
        response = initialize_payment(request.user.email, amount, reference)

        if response.get("status"):
            # Save transaction as pending
            Transaction.objects.create(
                user=request.user,
                transaction_type="deposit",
                amount=amount,
                reference=reference,
                status="pending"
            )
            return redirect(response["data"]["authorization_url"])  # Redirect to Paystack payment page

    return render(request, "payments/deposit.html")



@csrf_exempt
@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack payment confirmation"""
    try:
        payload = json.loads(request.body)
        event = payload.get("event")
        
        # Process only successful payments
        if event == "charge.success":
            data = payload.get("data", {})
            reference = data.get("reference")
            amount = int(data.get("amount", 0)) / 100  # Convert to Naira
            status = data.get("status")

            if status == "success":
                try:
                    transaction = Transaction.objects.get(reference=reference, status="pending")
                    
                    # For deposit transactions, update the wallet balance.
                    if transaction.transaction_type == "deposit":
                        user_wallet = Wallet.objects.get(user=transaction.user)
                        user_wallet.balance += amount
                        user_wallet.save()
                        message = "Wallet updated successfully"
                    # For purchase transactions, do NOT update the wallet.
                    elif transaction.transaction_type == "purchase":
                        message = "Purchase completed successfully"
                    
                    # Mark transaction as completed for both cases.
                    transaction.status = "completed"
                    transaction.save()
                    
                    return JsonResponse({"message": message}, status=200)

                except Transaction.DoesNotExist:
                    return JsonResponse({"error": "Transaction not found"}, status=400)
                except Wallet.DoesNotExist:
                    return JsonResponse({"error": "Wallet not found"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"message": "Webhook received"}, status=200)




def verify_payment(request):
    reference = request.GET.get("reference") or request.GET.get("trxref")
    if not reference:
        return redirect('dashboard')

    url = f"{settings.PAYSTACK_ENDPOINT}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(url, headers=headers)
    resp_data = response.json()

    if resp_data.get("status") and resp_data.get("data", {}).get("status") == "success":
        try:
            transaction = Transaction.objects.get(reference=reference, status="pending")
        except Transaction.DoesNotExist:
            return redirect('dashboard')

        amount = Decimal(resp_data["data"].get("amount", 0)) / Decimal(100)

        if transaction.transaction_type == "deposit":
            wallet, created = Wallet.objects.get_or_create(
                user=transaction.user,
                defaults={'balance': Decimal('0.00')}
            )
            wallet.balance += amount
            wallet.save()
            transaction.status = "completed"
            transaction.save()
            return redirect('dashboard')

        elif transaction.transaction_type == "purchase":
            # Assuming your Transaction model has a product attribute:
            if not hasattr(transaction, 'product') or transaction.product is None:
                # If there's no product associated, handle accordingly.
                return redirect('dashboard')
            product = transaction.product
            # Create an Order object for the purchase
            order = Order.objects.create(
                buyer=transaction.user,
                product=product,
                status="paid"  # You can adjust the status as needed.
            )
            transaction.status = "completed"
            transaction.save()
            # Redirect to order_success with the newly created order's ID.
            return redirect('marketplace:order_success', order_id=order.id)

        elif transaction.transaction_type == "contribution":
            transaction.status = "completed"
            transaction.save()
            # Create a Contribution record in the Adashe app if transaction.pool exists.
            if transaction.pool:
                Contribution.objects.create(
                    user=transaction.user,
                    savings_pool=transaction.pool,
                    amount=transaction.amount,
                )
                return redirect('pool_details', pool_id=transaction.pool.id)
            else:
                return redirect('user_dashboard')
    return redirect('dashboard')
