from decimal import Decimal
from adashe.models import SavingsPool, Payout
from notifications.models import Notification

def process_payout_for_pool(pool):
    """
    Processes a payout for the given savings pool.
    Finds the next user in the payout order who hasn't received a payout,
    calculates the payout amount, creates a Payout record, sends a notification,
    and then checks if the pool is complete.
    """
    if not pool.is_active:
        return

    # Determine the next user in the payout order who hasn't been paid yet.
    # Here, we assume that pool.payout_order.all() returns the intended order.
    next_user = None
    for user in pool.payout_order.all():
        # Check if a payout exists for this user in this pool.
        if not pool.payout_set.filter(user=user, is_completed=True).exists():
            next_user = user
            break

    if not next_user:
        # If everyone has been paid, mark the pool as inactive.
        pool.is_active = False
        pool.save()
        return

    # Calculate the total contributions for this cycle.
    # For simplicity, assume each member contributed exactly pool.contribution_amount.
    total_contribution = pool.contribution_amount * pool.members.count()

    # Create the payout record.
    payout = Payout.objects.create(
        user=next_user,
        savings_pool=pool,
        amount=total_contribution,
        is_completed=True  # In an automated system, mark as complete immediately.
    )

    # Send a notification to the user.
    Notification.objects.create(
        recipient=next_user,
        message=f"Congratulations! You've received your payout of ₦{total_contribution} from the '{pool.name}' pool.",
        link=f"/pool/{pool.id}/"  # Adjust URL as needed.
    )

    # Optionally, log the payout (or perform additional actions).
    print(f"Payout processed for {next_user.username} in pool {pool.name}")

    # Check if the pool should be marked as complete.
    pool.check_pool_completion()
