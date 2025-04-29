from django.urls import path
from . import views

urlpatterns = [
    path('order-tracking/', views.order_tracking_view, name='order_tracking'),
    path('api/track/<str:order_id>/', views.fetch_tracking_data, name='fetch_tracking_data'),
    path('partners/', views.list_logistic_companies, name='list_logistic_companies'),
    path('apply/', views.logistic_company_apply, name='logistic_company_apply'),
]

    