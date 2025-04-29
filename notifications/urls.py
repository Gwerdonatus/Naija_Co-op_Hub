from django.urls import path
from .views import notifications_view, mark_all_read

urlpatterns = [
    path('', notifications_view, name='notifications'),
    path('mark-all-read/', mark_all_read, name='mark_all_read'),
]
