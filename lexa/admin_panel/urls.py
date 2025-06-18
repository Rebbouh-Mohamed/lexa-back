from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('users/<int:user_id>/approve/', views.approve_user, name='approve_user'),
    path('users/<int:user_id>/block/', views.block_user, name='block_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    path('actions/', views.AdminActionListCreateView.as_view(), name='admin_action_list_create'),
    
    path('subscriptions/', views.SubscriptionListCreateView.as_view(), name='subscription_list_create'),
    path('subscriptions/<int:pk>/', views.SubscriptionDetailView.as_view(), name='subscription_detail'),
    
    path('dashboard/', views.admin_dashboard_stats, name='admin_dashboard_stats'),
]
