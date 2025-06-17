from django.contrib import admin
from .models import AlgerianLegalCode, AlgerianCourt, TaxConfiguration, LegalProcedure

@admin.register(AlgerianLegalCode)
class AlgerianLegalCodeAdmin(admin.ModelAdmin):
    list_display = ('code_name_fr', 'code_type', 'article_number', 'is_active')
    list_filter = ('code_type', 'is_active', 'effective_date')
    search_fields = ('code_name_fr', 'code_name_ar', 'article_number')
    ordering = ('code_type', 'article_number')

@admin.register(AlgerianCourt)
class AlgerianCourtAdmin(admin.ModelAdmin):
    list_display = ('court_name_fr', 'court_level', 'jurisdiction_type', 'wilaya', 'is_active')
    list_filter = ('court_level', 'jurisdiction_type', 'wilaya', 'is_active')
    search_fields = ('court_name_fr', 'court_name_ar', 'city')
    ordering = ('wilaya', 'court_name_fr')

@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_rate', 'effective_from', 'effective_to', 'is_active')
    list_filter = ('tax_type', 'is_active', 'effective_from')
    ordering = ('tax_type', '-effective_from')

@admin.register(LegalProcedure)
class LegalProcedureAdmin(admin.ModelAdmin):
    list_display = ('procedure_name_fr', 'procedure_type', 'court_level', 'timeline_days', 'is_active')
    list_filter = ('procedure_type', 'court_level', 'is_active')
    search_fields = ('procedure_name_fr', 'procedure_name_ar')
    ordering = ('procedure_type', 'procedure_name_fr')