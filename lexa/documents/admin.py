from django.contrib import admin
from .models import Document, DocumentTemplate, DocumentVersion, DocumentShare

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'is_active', 'is_public', 'user', 'created_at')
    list_filter = ('template_type', 'is_active', 'is_public', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title_fr', 'document_type', 'language', 'version', 'user', 'created_at')
    list_filter = ('document_type', 'language', 'is_final', 'is_confidential', 'created_at')
    search_fields = ('title_fr', 'title_ar', 'case__reference', 'case__title')
    ordering = ('-created_at',)
    readonly_fields = ('file_size', 'file_type', 'created_at', 'updated_at')

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('document__title_fr', 'change_notes')
    ordering = ('-created_at',)

@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ('document', 'shared_with_email', 'access_level', 'is_active', 'shared_by', 'created_at')
    list_filter = ('access_level', 'is_active', 'created_at')
    search_fields = ('document__title_fr', 'shared_with_email')
    ordering = ('-created_at',)
    readonly_fields = ('access_token', 'accessed_count', 'last_accessed')