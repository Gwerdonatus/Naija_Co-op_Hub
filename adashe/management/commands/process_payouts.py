from django.core.management.base import BaseCommand
from adashe.models import SavingsPool
from adashe.utils import process_payout_for_pool  # Make sure you have this function in adashe/utils.py

class Command(BaseCommand):
    help = "Process payouts for active savings pools."

    def handle(self, *args, **options):
        pools = SavingsPool.objects.filter(is_active=True)
        for pool in pools:
            process_payout_for_pool(pool)
            self.stdout.write(self.style.SUCCESS(f"Processed payout for pool: {pool.name}"))
