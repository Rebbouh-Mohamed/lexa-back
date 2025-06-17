from django.urls import path
from . import views

urlpatterns = [
    path('legal-codes/', views.AlgerianLegalCodeListView.as_view(), name='legal_codes'),
    path('courts/', views.AlgerianCourtListView.as_view(), name='courts'),
    path('tax-configurations/', views.TaxConfigurationListView.as_view(), name='tax_configurations'),
    path('procedures/', views.LegalProcedureListView.as_view(), name='legal_procedures'),
    path('tax-rate/<str:tax_type>/', views.get_current_tax_rate, name='current_tax_rate'),
]