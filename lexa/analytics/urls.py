from django.urls import path
from . import views

urlpatterns = [
    path('case-analytics/', views.CaseAnalyticListCreateView.as_view(), name='case_analytic_list_create'),
    path('revenue-analytics/', views.RevenueAnalyticListView.as_view(), name='revenue_analytic_list'),
    path('case-performance/', views.case_performance_analytics, name='case_performance_analytics'),
    path('generate-revenue-report/', views.generate_revenue_report, name='generate_revenue_report'),
]