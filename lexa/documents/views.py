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
from django.db.models import Q 

import mimetypes
from .models import Document, DocumentTemplate, DocumentVersion, DocumentShare
from .serializers import (
    DocumentSerializer, DocumentTemplateSerializer, DocumentVersionSerializer,
    DocumentShareSerializer, DocumentCreateFromTemplateSerializer
)
from cases.models import Case

class DocumentTemplateListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentTemplateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        return DocumentTemplate.objects.filter(
            models.Q(user=self.request.user) | models.Q(is_public=True)
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentTemplateSerializer

    def get_queryset(self):
        return DocumentTemplate.objects.filter(user=self.request.user)

class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['case', 'document_type', 'template_type', 'language', 'is_final']
    search_fields = ['title_fr', 'title_ar', 'content']
    ordering_fields = ['created_at', 'updated_at', 'title_fr']

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).select_related(
            'case', 'template'
        ).prefetch_related('versions', 'shares')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_document_from_template(request):
    """Create a new document from a template"""
    serializer = DocumentCreateFromTemplateSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Get template and case
        template = get_object_or_404(
                DocumentTemplate,
                id=data['template_id'],
                user=request.user
            ) | get_object_or_404(
                DocumentTemplate,
                id=data['template_id'],
                is_public=True
            )
        case = get_object_or_404(Case, id=data['case_id'], user=request.user)
        
        # Replace variables in template content
        content = template.content_fr
        if data.get('variables'):
            template_obj = Template(content)
            context = Context(data['variables'])
            content = template_obj.render(context)
        
        # Create document
        document = Document.objects.create(
            title_fr=data['title_fr'],
            title_ar=data.get('title_ar', ''),
            case=case,
            template=template,
            document_type='template',
            template_type=template.template_type,
            content=content,
            language=data['language'],
            user=request.user
        )
        
        # Create initial version
        DocumentVersion.objects.create(
            document=document,
            version_number=1,
            content=content,
            created_by=request.user,
            change_notes="Initial version from template"
        )
        
        serializer = DocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_document_version(request, document_id):
    """Create a new version of an existing document"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    # Get the latest version number
    latest_version = document.versions.first()
    new_version_number = (latest_version.version_number if latest_version else 0) + 1
    
    # Create new version
    version = DocumentVersion.objects.create(
        document=document,
        version_number=new_version_number,
        content=request.data.get('content', ''),
        change_notes=request.data.get('change_notes', ''),
        created_by=request.user
    )
    
    # Update document version
    document.version = new_version_number
    document.save(update_fields=['version'])
    
    serializer = DocumentVersionSerializer(version)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def share_document(request, document_id):
    """Share a document with external parties"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    # Generate unique access token
    access_token = str(uuid.uuid4())
    
    share = DocumentShare.objects.create(
        document=document,
        shared_with_email=request.data.get('email'),
        access_level=request.data.get('access_level', 'view'),
        access_token=access_token,
        expires_at=request.data.get('expires_at'),
        shared_by=request.user
    )
    
    # TODO: Send email notification to shared user
    
    serializer = DocumentShareSerializer(share)
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
        return Response({
            'title': document.title_fr,
            'content': document.content,
            'created_at': document.created_at,
            'case_reference': document.case.reference
        })
    
    elif share.access_level in ['download', 'edit'] and document.file:
        # Return file for download
        response = HttpResponse(
            document.file.read(),
            content_type=document.file_type or 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
        return response
    
    return Response({'error': 'No file available for download'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_document(request, document_id):
    """Download a document file"""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    
    if not document.file:
        return Response({'error': 'No file available'}, status=status.HTTP_404_NOT_FOUND)
    
    response = HttpResponse(
        document.file.read(),
        content_type=document.file_type or 'application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{document.file_name}"'
    return response

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_analytics(request):
    """Get document analytics for the user"""
    user_documents = Document.objects.filter(user=request.user)
    
    analytics = {
        'total_documents': user_documents.count(),
        'documents_by_type': user_documents.values('document_type').annotate(
            count=models.Count('id')
        ),
        'documents_by_language': user_documents.values('language').annotate(
            count=models.Count('id')
        ),
        'recent_documents': DocumentSerializer(
            user_documents.order_by('-created_at')[:10], many=True
        ).data,
        'shared_documents': DocumentShare.objects.filter(
            document__user=request.user, is_active=True
        ).count(),
        'templates_count': DocumentTemplate.objects.filter(user=request.user).count()
    }
    
    return Response(analytics)
