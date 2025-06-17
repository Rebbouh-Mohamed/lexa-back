from django.urls import path
from . import views

urlpatterns = [
    # Client Access Management
    path('access/', views.ClientAccessListCreateView.as_view(), name='client_access_list_create'),
    path('access/<int:pk>/', views.ClientAccessDetailView.as_view(), name='client_access_detail'),
    path('generate-access/', views.generate_client_access, name='generate_client_access'),
    
    # Client Messages
    path('messages/', views.ClientMessageListCreateView.as_view(), name='client_message_list_create'),
    path('messages/<int:pk>/', views.ClientMessageDetailView.as_view(), name='client_message_detail'),
    
    # Client Documents
    path('documents/', views.ClientDocumentListCreateView.as_view(), name='client_document_list_create'),
    path('documents/<int:pk>/', views.ClientDocumentDetailView.as_view(), name='client_document_detail'),
    
    # Public Client Portal APIs
    path('verify-access/', views.verify_client_access, name='verify_client_access'),
    path('send-message/', views.send_client_message, name='send_client_message'),
]