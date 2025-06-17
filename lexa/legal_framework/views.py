from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import AlgerianLegalCode, AlgerianCourt, TaxConfiguration, LegalProcedure
from .serializers import (
    AlgerianLegalCodeSerializer, AlgerianCourtSerializer,
    TaxConfigurationSerializer, LegalProcedureSerializer
)
from django.db import models

class AlgerianLegalCodeListView(generics.ListAPIView):
    queryset = AlgerianLegalCode.objects.filter(is_active=True)
    serializer_class = AlgerianLegalCodeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['code_type']
    search_fields = ['code_name_fr', 'code_name_ar', 'article_number', 'article_content_fr']
    ordering_fields = ['code_type', 'article_number']

class AlgerianCourtListView(generics.ListAPIView):
    queryset = AlgerianCourt.objects.filter(is_active=True)
    serializer_class = AlgerianCourtSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['court_level', 'jurisdiction_type', 'wilaya']
    search_fields = ['court_name_fr', 'court_name_ar', 'city']
    ordering_fields = ['wilaya', 'court_name_fr']

class TaxConfigurationListView(generics.ListAPIView):
    serializer_class = TaxConfigurationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tax_type', 'is_active']
    search_fields = ['description_fr', 'description_ar']
    ordering_fields = ['tax_type', 'effective_from']

    def get_queryset(self):
        return TaxConfiguration.objects.filter(is_active=True)

class LegalProcedureListView(generics.ListAPIView):
    queryset = LegalProcedure.objects.filter(is_active=True)
    serializer_class = LegalProcedureSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['procedure_type', 'court_level']
    search_fields = ['procedure_name_fr', 'procedure_name_ar', 'description_fr']
    ordering_fields = ['procedure_type', 'procedure_name_fr']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_tax_rate(request, tax_type):
    """Get current tax rate for a specific tax type"""
    try:
        current_date = timezone.now().date()
        tax_config = TaxConfiguration.objects.filter(
            tax_type=tax_type,
            is_active=True,
            effective_from__lte=current_date
        ).filter(
            models.Q(effective_to__gte=current_date) | models.Q(effective_to__isnull=True)
        ).order_by('-effective_from').first()
        
        if tax_config:
            return Response(TaxConfigurationSerializer(tax_config).data)
        else:
            return Response({'error': 'No active tax configuration found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)