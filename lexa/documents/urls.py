from django.urls import path
from . import views

urlpatterns = [
    # Document Templates
    path('templates/', views.DocumentTemplateListCreateView.as_view(), name='document_template_list_create'),
    path('templates/<int:pk>/', views.DocumentTemplateDetailView.as_view(), name='document_template_detail'),
    
    # Documents
    path('', views.DocumentListCreateView.as_view(), name='document_list_create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('create-from-template/', views.create_document_from_template, name='create_document_from_template'),
    path('<int:document_id>/versions/', views.create_document_version, name='create_document_version'),
    path('<int:document_id>/share/', views.share_document, name='share_document'),
    path('<int:document_id>/download/', views.download_document, name='download_document'),
    path('analytics/', views.document_analytics, name='document_analytics'),
    
    # Public access
    path('shared/<str:access_token>/', views.download_shared_document, name='download_shared_document'),
]