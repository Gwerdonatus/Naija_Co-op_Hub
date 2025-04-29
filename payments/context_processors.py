from .models import Wallet

def wallet_balance(request):
    if request.user.is_authenticated:
        try:
            balance = Wallet.objects.get(user=request.user).balance
        except Wallet.DoesNotExist:
            balance = 0.00
        return {"wallet_balance": balance}
    return {}
