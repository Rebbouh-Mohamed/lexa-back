from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from cases.models import Case
import os

User = get_user_model()

class DocumentTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('constitution_avocat', _('Constitution d\'avocat')),
        ('requete_introductive', _('Requête introductive')),
        ('conclusions', _('Conclusions')),
        ('memoire', _('Mémoire')),
        ('assignation', _('Assignation')),
        ('citation', _('Citation')),
        ('ordonnance', _('Ordonnance')),
        ('jugement', _('Jugement')),
        ('appel', _('Appel')),
        ('pourvoi', _('Pourvoi')),
        ('contrat', _('Contrat')),
        ('acte_notarie', _('Acte notarié')),
        ('attestation', _('Attestation')),
        ('lettre_mise_demeure', _('Lettre de mise en demeure')),
        ('rapport_expertise', _('Rapport d\'expertise')),
        ('proces_verbal', _('Procès-verbal')),
    ]

    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)
    content_fr = models.TextField()
    content_ar = models.TextField(blank=True)
    
    # Template variables/placeholders
    variables = models.JSONField(default=list, help_text="List of variables that can be replaced in template")
    
    # Usage settings
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)  # Available to all users
    category = models.CharField(max_length=100, blank=True)
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_templates')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Document Template')
        verbose_name_plural = _('Document Templates')
        ordering = ['name']

    def __str__(self):
        return self.name

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('template', _('Generated from template')),
        ('uploaded', _('Uploaded file')),
        ('scanned', _('Scanned document')),
        ('external', _('External document')),
    ]
    
    LANGUAGE_CHOICES = [
        ('fr', _('French')),
        ('ar', _('Arabic')),
        ('bilingual', _('Bilingual')),
    ]

    # Basic information
    title_fr = models.CharField(max_length=300)
    title_ar = models.CharField(max_length=300, blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='uploaded')
    template_type = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='fr')
    
    # Content (for generated documents)
    content = models.TextField(blank=True)
    
    # File handling
    file = models.FileField(upload_to='documents/%Y/%m/', null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    
    # Relationships
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents')
    template = models.ForeignKey(DocumentTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Document metadata
    version = models.PositiveIntegerField(default=1)
    is_final = models.BooleanField(default=False)
    is_confidential = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    
    # Legal tracking
    date_signed = models.DateField(null=True, blank=True)
    signatory = models.CharField(max_length=200, blank=True)
    witness = models.CharField(max_length=200, blank=True)
    
    # Access control
    is_shared_with_client = models.BooleanField(default=False)
    client_access_expires = models.DateTimeField(null=True, blank=True)
    
    # User relationship
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-created_at']

    def __str__(self):
        return self.title_fr

    @property
    def file_name(self):
        if self.file:
            return os.path.basename(self.file.name)
        return None

    @property
    def file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None

class DocumentVersion(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='document_versions/%Y/%m/', null=True, blank=True)
    change_notes = models.TextField(blank=True)
    
    # User who created this version
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Document Version')
        verbose_name_plural = _('Document Versions')
        unique_together = ['document', 'version_number']
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.document.title_fr} v{self.version_number}"

class DocumentShare(models.Model):
    ACCESS_LEVELS = [
        ('view', _('View only')),
        ('download', _('View and download')),
        ('edit', _('View, download and edit')),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    shared_with_email = models.EmailField()
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='view')
    access_token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Tracking
    accessed_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # User who shared
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Document Share')
        verbose_name_plural = _('Document Shares')

    def __str__(self):
        return f"{self.document.title_fr} shared with {self.shared_with_email}"