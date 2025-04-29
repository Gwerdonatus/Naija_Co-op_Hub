from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from .models import SavingsPool, Contribution, Payout
from .forms import SavingsPoolForm
from django.db import models
import uuid
from django.urls import reverse
from payments.utils import initialize_payment  # adjust the import path if necessary
from payments.models import Transaction

 

@login_required
def create_savings_pool(request):
    """Handles savings pool creation."""
    if request.method == "POST":
        form = SavingsPoolForm(request.POST)
        if form.is_valid():
            pool = form.save(commit=False)
            pool.created_by = request.user
            pool.save()
            pool.members.add(request.user)  # Add creator as a member
            
            # Debugging: Print saved pool details
            print(f"Pool Created: {pool.name}, ID: {pool.id}, Members: {pool.members.count()}")

            # Send email notification
            #send_mail(
             #   'Adashe Pool Created',
              #  f'Your Adashe pool "{pool.name}" has been created.',
               # 'admin@naijacoop.com',
                #[request.user.email],
                #fail_silently=False,
            #)

            return redirect('savings_pool_list')
    else:
        form = SavingsPoolForm()
    return render(request, 'adashe/create_savings_pool.html', {'form': form})

@login_required
def savings_pool_list(request):
    """Shows active savings pools."""
    pools = SavingsPool.objects.filter(is_active=True).order_by('-id')  # Show newest first
    return render(request, 'adashe/savings_pool_list.html', {'pools': pools})

@login_required
def view_contributions(request, pool_id):
    """View contributions for a savings pool (only if user is a member)."""
    pool = get_object_or_404(SavingsPool, id=pool_id)

    # Ensure only members can view the contributions
    if request.user not in pool.members.all():
        return HttpResponseForbidden("You are not authorized to view this pool's details.")

    contributions = Contribution.objects.filter(savings_pool=pool)
    return render(request, 'adashe/contributions.html', {'contributions': contributions, 'pool': pool})


@login_required
def user_dashboard(request):
    user = request.user  # Get the logged-in user

    available_pools = SavingsPool.objects.filter(is_active=True)  # Active pools
    joined_pools = user.joined_pools.all()  
    user_contributions = Contribution.objects.filter(user=user)  # Contributions
    user_payouts = Payout.objects.filter(user=user)  # Payouts

    return render(request, "adashe/adashe_dashboard.html", {
        "available_cycles": available_pools,  
        "joined_pools": joined_pools,
        "user_contributions": user_contributions,
        "user_payouts": user_payouts,
    })



@login_required
def join_savings_pool(request, pool_id):
    """Allows a user to join a savings pool."""
    pool = get_object_or_404(SavingsPool, id=pool_id)

    # Add user to the pool if they haven't joined yet
    if request.user not in pool.members.all():
        pool.members.add(request.user)

    return redirect("user_dashboard")



def pool_details(request, pool_id):
    pool = get_object_or_404(SavingsPool, id=pool_id)
    
    # Get user's contributions & payouts for this pool
    user_contributions = Contribution.objects.filter(savings_pool=pool, user=request.user)
    user_payouts = Payout.objects.filter(savings_pool=pool, user=request.user)

    # Calculate progress (Percentage of completed contributions)
    total_expected_contributions = pool.members.count() * pool.contribution_amount
    total_actual_contributions = Contribution.objects.filter(savings_pool=pool).aggregate(total=models.Sum('amount'))['total'] or 0
    contribution_progress = (total_actual_contributions / total_expected_contributions * 100) if total_expected_contributions > 0 else 0

    context = {
        'pool': pool,
        'user_contributions': user_contributions,
        'user_payouts': user_payouts,
        'contribution_progress': round(contribution_progress, 2),
    }
    return render(request, 'adashe/pool_details.html', context)



@login_required
def contribute_to_pool(request, pool_id):
    pool = get_object_or_404(SavingsPool, id=pool_id)
    amount = pool.contribution_amount
    reference = str(uuid.uuid4()) 

    # Initialize the payment via Paystack
    response = initialize_payment(request.user.email, float(amount), reference)
    
    if response.get("status"):
        # Create a transaction of type "contribution" and link to the pool
        Transaction.objects.create(
            user=request.user,
            transaction_type="contribution",
            amount=amount,
            reference=reference,
            status="pending",
            pool=pool,
        )
        # Redirect user to the Paystack authorization URL
        return redirect(response["data"]["authorization_url"])
    else:
        # Optionally, add error messaging
        return redirect('pool_details', pool_id=pool.id)
