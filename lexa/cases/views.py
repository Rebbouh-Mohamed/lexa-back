from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count, Sum
from .models import Jurisdiction, CaseType, Case, Audience, CaseMetric
from .serializers import (
    JurisdictionSerializer, CaseTypeSerializer, CaseSerializer,
    CaseCreateSerializer, AudienceSerializer, CaseMetricSerializer
)
from django.utils import timezone
from rest_framework.views import APIView

class JurisdictionListCreateView(generics.ListCreateAPIView):
    queryset = Jurisdiction.objects.filter(is_active=True)
    serializer_class = JurisdictionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['wilaya', 'type_fr', 'level']
    search_fields = ['name_fr', 'name_ar']
    ordering_fields = ['name_fr', 'wilaya']

class JurisdictionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer

class CaseTypeListCreateView(generics.ListCreateAPIView):
    queryset = CaseType.objects.all()
    serializer_class = CaseTypeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category_fr']
    search_fields = ['subtype_fr', 'subtype_ar']

class CaseTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CaseType.objects.all()
    serializer_class = CaseTypeSerializer

class CaseListCreateView(generics.ListCreateAPIView):
    serializer_class = CaseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'jurisdiction', 'case_type', 'priority']
    search_fields = ['reference', 'title', 'client_name', 'description']
    ordering_fields = ['created_at', 'open_date', 'updated_at']

    def get_queryset(self):
        return Case.objects.filter(user=self.request.user).select_related(
            'jurisdiction', 'case_type'
        ).prefetch_related('audiences')#(, 'documents') later zidha direct

    def get_serializer_class(self):
        if self.request.method == 'POST':
            print(self.request.data)
            return CaseCreateSerializer
        return CaseSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CaseSerializer

    def get_queryset(self):
        return Case.objects.filter(user=self.request.user).select_related(
            'jurisdiction', 'case_type'
        ).prefetch_related('audiences') #(,'documents') later zidha direct

class AudienceListCreateView(generics.ListCreateAPIView):
    serializer_class = AudienceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case', 'type_fr', 'chamber_fr', 'result_fr']
    search_fields = ['notes', 'judge_name']
    ordering_fields = ['date', 'created_at']

    def get_queryset(self):
        print("User:", self.request.user)
        return Audience.objects.filter(user=self.request.user).select_related('case')

    def create(self, request, *args, **kwargs):
        print("Request data:", request.data)  # Debug: Log incoming data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)  # Debug: Log validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        print("Validated data:", serializer.validated_data)
        try:
            serializer.save(user=self.request.user)
            print("Successfully saved audience")
        except Exception as e:
            print("Error during save:", str(e))
            raise

class AudienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AudienceSerializer

    def get_queryset(self):
        return Audience.objects.filter(user=self.request.user)

class CaseMetricDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CaseMetricSerializer

    def get_object(self):
        case_id = self.kwargs['case_id']
        case = Case.objects.get(id=case_id, user=self.request.user)
        metric, created = CaseMetric.objects.get_or_create(
            case=case,
            defaults={'user': self.request.user}
        )
        return metric

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def case_dashboard_stats(request):
    """Get dashboard statistics for cases"""
    user_cases = Case.objects.filter(user=request.user)
    
    stats = {
        'total_cases': user_cases.count(),
        'active_cases': user_cases.filter(status__in=['ouvert', 'en_cours_instruction']).count(),
        'closed_cases': user_cases.filter(status__in=['clos', 'archive']).count(),
        'upcoming_audiences': Audience.objects.filter(
            user=request.user,
            date__gte=timezone.now()
        ).count(),
        'cases_by_status': user_cases.values('status').annotate(
            count=Count('id')
        ),
        'cases_by_type': user_cases.values(
            'case_type__category_fr'
        ).annotate(count=Count('id')),
        'recent_cases': CaseSerializer(
            user_cases.order_by('-created_at')[:5], many=True
        ).data
    }
    
    return Response(stats)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def case_search(request):
    """Advanced case search"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})
    
    cases = Case.objects.filter(
        user=request.user
    ).filter(
        Q(reference__icontains=query) |
        Q(title__icontains=query) |
        Q(client_name__icontains=query) |
        Q(description__icontains=query)
    ).select_related('jurisdiction', 'case_type')[:20]
    
    serializer = CaseSerializer(cases, many=True)
    return Response({'results': serializer.data})


###
class AudienceChoicesView(APIView):
    def get(self, request):
        return Response({
            'type_fr_choices': Audience.AUDIENCE_TYPES,  # Use the correct field name
            'chamber_fr_choices': Audience.CHAMBER_TYPES,  # Use the correct field name
            'stage_fr_choices': Audience.PROCEDURAL_STAGES,  # Use the correct field name
        })