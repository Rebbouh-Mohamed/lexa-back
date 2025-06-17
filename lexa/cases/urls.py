from django.urls import path
from . import views

urlpatterns = [
    # Jurisdictions
    path('jurisdictions/', views.JurisdictionListCreateView.as_view(), name='jurisdiction_list_create'),
    path('jurisdictions/<int:pk>/', views.JurisdictionDetailView.as_view(), name='jurisdiction_detail'),
    
    # Case Types
    path('case-types/', views.CaseTypeListCreateView.as_view(), name='case_type_list_create'),
    path('case-types/<int:pk>/', views.CaseTypeDetailView.as_view(), name='case_type_detail'),
    
    # Cases
    path('', views.CaseListCreateView.as_view(), name='case_list_create'),
    path('<int:pk>/', views.CaseDetailView.as_view(), name='case_detail'),
    path('dashboard-stats/', views.case_dashboard_stats, name='case_dashboard_stats'),
    path('search/', views.case_search, name='case_search'),
    
    # Audiences
    path('audiences/', views.AudienceListCreateView.as_view(), name='audience_list_create'),
    path('audiences/<int:pk>/', views.AudienceDetailView.as_view(), name='audience_detail'),
    path('audience-choices/', views.AudienceChoicesView.as_view(), name='audience_detail'),

    
    # Case Metrics
    path('<int:case_id>/metrics/', views.CaseMetricDetailView.as_view(), name='case_metrics'),
]