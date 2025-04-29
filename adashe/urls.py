from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_savings_pool, name='create_savings_pool'),
    path('list/', views.savings_pool_list, name='savings_pool_list'),
    path('pool/<int:pool_id>/contributions/', views.view_contributions, name='view_contributions'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('join/<int:pool_id>/', views.join_savings_pool, name='join_savings_pool'),
    path('pool/<int:pool_id>/', views.pool_details, name='pool_details'),
    path('pool/<int:pool_id>/contribute/', views.contribute_to_pool, name='contribute_to_pool'),
]



