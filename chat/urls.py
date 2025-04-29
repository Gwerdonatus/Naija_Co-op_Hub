from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<str:username>/', views.chat_detail, name='chat_detail'),
    path('chat/<str:username>/send/', views.send_message, name='send_message'),
]
