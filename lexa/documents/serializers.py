from rest_framework import serializers
from .models import Document, DocumentTemplate, DocumentVersion, DocumentShare

class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

class DocumentShareSerializer(serializers.ModelSerializer):
    shared_by_name = serializers.CharField(source='shared_by.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentShare
        fields = '__all__'
        read_only_fields = ['shared_by', 'access_token', 'created_at']

class DocumentSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    versions = DocumentVersionSerializer(many=True, read_only=True)
    shares = DocumentShareSerializer(many=True, read_only=True)
    file_name = serializers.CharField(read_only=True)
    file_extension = serializers.CharField(read_only=True)
    
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ['user', 'file_size', 'file_type', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # Handle file metadata
        if 'file' in validated_data and validated_data['file']:
            file_obj = validated_data['file']
            validated_data['file_size'] = file_obj.size
            validated_data['file_type'] = file_obj.content_type
        
        return super().create(validated_data)

class DocumentCreateFromTemplateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    case_id = serializers.IntegerField()
    title_fr = serializers.CharField(max_length=300)
    title_ar = serializers.CharField(max_length=300, required=False, allow_blank=True)
    variables = serializers.JSONField(required=False)
    language = serializers.ChoiceField(choices=Document.LANGUAGE_CHOICES, default='fr')