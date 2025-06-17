from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import Http404
import uuid
from .models import ClientAccess, ClientMessage, ClientDocument
from .serializers import ClientAccessSerializer, ClientMessageSerializer, ClientDocumentSerializer
from cases.models import Case

class ClientAccessListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientAccessSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['case', 'is_active']
    search_fields = ['client_email', 'case__reference']

    def get_queryset(self):
        return ClientAccess.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ClientAccessDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientAccessSerializer

    def get_queryset(self):
        return ClientAccess.objects.filter(created_by=self.request.user)

class ClientMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientMessageSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case', 'sender_type', 'is_read']
    search_fields = ['subject', 'message', 'sender_name']
    ordering_fields = ['created_at']

    def get_queryset(self):
        # Get messages for cases where user is the lawyer
        user_cases = Case.objects.filter(user=self.request.user)
        return ClientMessage.objects.filter(case__in=user_cases)

class ClientMessageDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientMessageSerializer

    def get_queryset(self):
        user_cases = Case.objects.filter(user=self.request.user)
        return ClientMessage.objects.filter(case__in=user_cases)

class ClientDocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientDocumentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['case', 'access_level', 'is_active']
    search_fields = ['client_email', 'document__title_fr']

    def get_queryset(self):
        return ClientDocument.objects.filter(shared_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(shared_by=self.request.user)

class ClientDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientDocumentSerializer

    def get_queryset(self):
        return ClientDocument.objects.filter(shared_by=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_client_access(request):
    """Generate client access token for a case"""
    case_id = request.data.get('case_id')
    client_email = request.data.get('client_email')
    expires_days = int(request.data.get('expires_days', 30))
    
    try:
        case = Case.objects.get(id=case_id, user=request.user)
    except Case.DoesNotExist:
        return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Calculate expiry date
    expires_at = timezone.now() + timezone.timedelta(days=expires_days)
    
    # Create or update client access
    client_access, created = ClientAccess.objects.update_or_create(
        case=case,
        client_email=client_email,
        defaults={
            'access_token': uuid.uuid4(),
            'expires_at': expires_at,
            'is_active': True,
            'created_by': request.user
        }
    )
    
    serializer = ClientAccessSerializer(client_access)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_client_access(request):
    """Verify client access token and email"""
    access_token = request.data.get('access_token')
    client_email = request.data.get('client_email')
    
    try:
        client_access = ClientAccess.objects.get(
            access_token=access_token,
            client_email=client_email,
            is_active=True
        )
        
        if client_access.is_expired:
            return Response({'error': 'Access token has expired'}, status=status.HTTP_403_FORBIDDEN)
        
        # Update access tracking
        client_access.access_count += 1
        client_access.last_accessed = timezone.now()
        client_access.save(update_fields=['access_count', 'last_accessed'])
        
        # Return case information
        case_data = {
            'case_reference': client_access.case.reference,
            'case_title': client_access.case.title,
            'status': client_access.case.status,
            'description': client_access.case.description,
            'open_date': client_access.case.open_date,
        }
        
        return Response({
            'valid': True,
            'case': case_data,
            'access_expires': client_access.expires_at
        })
        
    except ClientAccess.DoesNotExist:
        return Response({'error': 'Invalid access credentials'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_client_message(request):
    """Send message from client through portal"""
    access_token = request.data.get('access_token')
    client_email = request.data.get('client_email')
    
    # Verify access
    try:
        client_access = ClientAccess.objects.get(
            access_token=access_token,
            client_email=client_email,
            is_active=True
        )
        
        if client_access.is_expired:
            return Response({'error': 'Access token has expired'}, status=status.HTTP_403_FORBIDDEN)
        
    except ClientAccess.DoesNotExist:
        return Response({'error': 'Invalid access credentials'}, status=status.HTTP_403_FORBIDDEN)
    
    # Create message
    message = ClientMessage.objects.create(
        case=client_access.case,
        sender_id=client_email,
        sender_type='client',
        sender_name=request.data.get('sender_name', client_email),
        subject=request.data.get('subject', ''),
        message=request.data.get('message'),
        attachments=request.data.get('attachments', [])
    )
    
    # TODO: Send notification to lawyer
    
    serializer = ClientMessageSerializer(message)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
