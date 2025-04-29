from django.urls import path
from .views import SignupAPIView, signup_form, LoginAPIView, login_form, LogoutAPIView, logout_view
from . import views

urlpatterns = [
    # Frontend paths for forms
    path('signup/', signup_form, name='signup_form'),  # Render signup HTML
    path('login/', login_form, name='login_form'),     # Render login HTML
    path('logout/', logout_view, name='logout'),

    # API paths for handling user actions
    path('signup/api/', SignupAPIView.as_view(), name='signup_api'),  # API for signup
    path('login/api/', LoginAPIView.as_view(), name='login_api'),   # API for login
    path('logout/', LogoutAPIView.as_view(), name='logout'),

    # User profile view
    path('profile/<str:username>/', views.profile_view, name='profile_view'),
    path('profile/<str:username>/edit/', views.profile_edit, name='profile_edit'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('change-password/', views.change_password, name='change_password'),
]

