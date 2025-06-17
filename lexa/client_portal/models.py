from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
import uuid
from cases.models import Case
from documents.models import Document

User = get_user_model()

class ClientAccess(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='client_accesses')
    client_email = models.EmailField()
    access_token = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Access control
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    
    # Tracking
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Creator
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Client Access')
        verbose_name_plural = _('Client Accesses')
        unique_together = ['case', 'client_email']

    def __str__(self):
        return f"Access for {self.client_email} to case {self.case.reference}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

class ClientMessage(models.Model):
    SENDER_TYPES = [
        ('lawyer', _('Lawyer')),
        ('client', _('Client')),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='client_messages')
    sender_id = models.CharField(max_length=100)  # User ID or client email
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES)
    sender_name = models.CharField(max_length=200)
    
    # Message content
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Reply information
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Client Message')
        verbose_name_plural = _('Client Messages')
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender_name} - {self.subject or 'No subject'}"

class ClientDocument(models.Model):
    ACCESS_LEVELS = [
        ('view', _('View only')),
        ('download', _('View and download')),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='client_shares')
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    client_email = models.EmailField()
    
    # Access control
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='view')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Sharing details
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE)
    share_message = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Client Document')
        verbose_name_plural = _('Client Documents')
        unique_together = ['document', 'client_email']

    def __str__(self):
        return f"{self.document.title_fr} shared with {self.client_email}"
