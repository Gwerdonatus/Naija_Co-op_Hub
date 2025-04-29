from django.urls import path
from .views import deposit
from django.urls import path
from .views import paystack_webhook,verify_payment


urlpatterns = [
    path("deposit/", deposit, name="deposit"),
    path("webhook/", paystack_webhook, name="paystack_webhook"),
    path("verify/", verify_payment, name="verify_payment"),
]

