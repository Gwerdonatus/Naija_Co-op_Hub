from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # Community-related URLs
    path('', views.community_list, name='community_list'),
    path('create/', views.community_create, name='community_create'),
    path('<slug:slug>/', views.community_detail, name='community_detail'),
    path('<slug:slug>/join/', views.community_join, name='community_join'),
    path('<slug:slug>/leave/', views.community_leave, name='community_leave'),

    # Post-related URLs
    path('post/<int:post_id>/delete/', views.delete_post, name='post_delete'),

    # Comment-related URLs
    path('post/<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='comment_delete'),

    # Upvotes/Downvotes URLs
    path('upvote/<int:post_id>/', views.upvote_post, name='upvote_post'),
    path('downvote/<int:post_id>/', views.downvote_post, name='downvote_post'),
]
