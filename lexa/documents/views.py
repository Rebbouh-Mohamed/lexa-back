from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.template import Template, Context
import uuid
from django.db import models
from django.db.models import Q, Count
import mimetypes

from .models import Document, DocumentTemplate, DocumentVersion, DocumentShare
from .serializers import (
    DocumentSerializer, DocumentTemplateSerializer, DocumentVersionSerializer,
    DocumentShareSerializer, DocumentCreateFromTemplateSerializer
)
# Import Case model if it exists, otherwise comment out
# from cases.models import Case


class DocumentTemplateListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        return DocumentTemplate.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DocumentTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DocumentTemplate.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )

    def get_object(self):
        """Override to allow access to public templates but only allow modification of own templates"""
        obj = super().get_object()
        
        # For update/delete operations, ensure user owns the template
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != self.request.user:
                raise Http404("Template not found or access denied")
        
        return obj


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # Removed 'case' from filterset_fields since Document model doesn't have case relationship
    filterset_fields = ['document_type', 'template_type', 'language', 'is_final']
    search_fields = ['title_fr', 'title_ar', 'content']
    ordering_fields = ['created_at', 'updated_at', 'title_fr']

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).select_related(
            'template'
        ).prefetch_related('versions', 'shares')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Debug logging - remove in production
        print("Request data:", request.data)
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_document_from_template(request):
    """Create a new document from a template"""
    serializer = DocumentCreateFromTemplateSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        try:
            # Use the serializer's create method which handles all the logic
            document = serializer.create(serializer.validated_data)
            
            # Create initial version
            DocumentVersion.objects.create(
                document=document,
                version_number=1,
                content=document.content,
                created_by=request.user,
                change_notes="Initial version from template"
            )
            
            document_serializer = DocumentSerializer(document, context={'request': request})
            return Response(document_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create document: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_document_version(request, document_id):
    """Create a new version of an existing document"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    # Validate required fields
    content = request.data.get('content')
    if not content:
        return Response(
            {'error': 'Content is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the latest version number
    latest_version = document.versions.first()
    new_version_number = (latest_version.version_number if latest_version else 0) + 1
    
    # Handle file upload if provided
    file_data = request.data.get('file')
    
    # Create new version
    version = DocumentVersion.objects.create(
        document=document,
        version_number=new_version_number,
        content=content,
        file=file_data,
        change_notes=request.data.get('change_notes', ''),
        created_by=request.user
    )
    
    # Update document version and content
    document.version = new_version_number
    document.content = content
    if file_data:
        document.file = file_data
    document.save(update_fields=['version', 'content', 'file', 'updated_at'])
    
    serializer = DocumentVersionSerializer(version, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def share_document(request, document_id):
    """Share a document with external parties"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    # Validate required fields
    email = request.data.get('email')
    if not email:
        return Response(
            {'error': 'Email is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    access_level = request.data.get('access_level', 'view')
    if access_level not in ['view', 'download', 'edit']:
        return Response(
            {'error': 'Invalid access level'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already shared with this email
    existing_share = DocumentShare.objects.filter(
        document=document,
        shared_with_email=email,
        is_active=True
    ).first()
    
    if existing_share:
        return Response(
            {'error': 'Document is already shared with this email'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate unique access token
    access_token = str(uuid.uuid4())
    
    # Parse expires_at if provided
    expires_at = request.data.get('expires_at')
    if expires_at:
        try:
            from django.utils.dateparse import parse_datetime
            expires_at = parse_datetime(expires_at)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid expires_at format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    share = DocumentShare.objects.create(
        document=document,
        shared_with_email=email,
        access_level=access_level,
        access_token=access_token,
        expires_at=expires_at,
        shared_by=request.user
    )
    
    # TODO: Send email notification to shared user
    
    serializer = DocumentShareSerializer(share, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_shared_document(request, access_token):
    """Download a shared document using access token"""
    share = get_object_or_404(
        DocumentShare,
        access_token=access_token,
        is_active=True
    )
    
    # Check if expired
    if share.expires_at and share.expires_at < timezone.now():
        raise Http404("Share link has expired")
    
    # Update access tracking
    share.accessed_count += 1
    share.last_accessed = timezone.now()
    share.save(update_fields=['accessed_count', 'last_accessed'])
    
    document = share.document
    
    if share.access_level == 'view':
        # Return document content as JSON for viewing
        response_data = {
            'title': document.title_fr,
            'content': document.content,
            'created_at': document.created_at,
            'language': document.language,
            'document_type': document.document_type,
        }
        
        # Add case reference if case relationship exists
        # Uncomment if Document has case relationship
        # if hasattr(document, 'case') and document.case:
        #     response_data['case_reference'] = document.case.reference
        
        return Response(response_data)
    
    elif share.access_level in ['download', 'edit'] and document.file:
        # Return file for download
        try:
            response = HttpResponse(
                document.file.read(),
                content_type=document.file_type or 'application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
            return response
        except Exception as e:
            return Response(
                {'error': 'Failed to download file'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(
        {'error': 'No file available for download'}, 
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_document(request, document_id):
    """Download a document file"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if not document.file:
        return Response(
            {'error': 'No file available'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        response = HttpResponse(
            document.file.read(),
            content_type=document.file_type or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
        return response
    except Exception as e:
        return Response(
            {'error': 'Failed to download file'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_analytics(request):
    """Get document analytics for the user"""
    user_documents = Document.objects.filter(user=request.user)
    
    analytics = {
        'total_documents': user_documents.count(),
        'documents_by_type': list(user_documents.values('document_type').annotate(
            count=Count('id')
        )),
        'documents_by_language': list(user_documents.values('language').annotate(
            count=Count('id')
        )),
        'documents_by_template_type': list(user_documents.exclude(
            template_type=''
        ).values('template_type').annotate(
            count=Count('id')
        )),
        'recent_documents': DocumentSerializer(
            user_documents.order_by('-created_at')[:10], 
            many=True,
            context={'request': request}
        ).data,
        'shared_documents_count': DocumentShare.objects.filter(
            document__user=request.user, 
            is_active=True
        ).count(),
        'templates_count': DocumentTemplate.objects.filter(
            user=request.user
        ).count(),
        'total_file_size': user_documents.aggregate(
            total_size=models.Sum('file_size')
        )['total_size'] or 0,
        'documents_shared_with_me': DocumentShare.objects.filter(
            shared_with_email=request.user.email,
            is_active=True
        ).count() if hasattr(request.user, 'email') else 0
    }
    
    return Response(analytics)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def revoke_document_share(request, share_id):
    """Revoke a document share"""
    share = get_object_or_404(
        DocumentShare, 
        id=share_id, 
        document__user=request.user
    )
    
    share.is_active = False
    share.save(update_fields=['is_active'])
    
    return Response({'message': 'Share revoked successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_versions(request, document_id):
    """Get all versions of a document"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    versions = document.versions.all()
    
    serializer = DocumentVersionSerializer(
        versions, 
        many=True, 
        context={'request': request}
    )
    return Response(serializer.data)