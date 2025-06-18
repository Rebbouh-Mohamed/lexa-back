from rest_framework import serializers
from .models import Document, DocumentTemplate, DocumentVersion, DocumentShare


class DocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DocumentVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentVersion
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class DocumentShareSerializer(serializers.ModelSerializer):
    shared_by_name = serializers.CharField(source='shared_by.get_full_name', read_only=True)
    
    class Meta:
        model = DocumentShare
        fields = '__all__'
        read_only_fields = ['shared_by', 'access_token', 'created_at']

    def create(self, validated_data):
        validated_data['shared_by'] = self.context['request'].user
        # Generate access token if not provided
        if 'access_token' not in validated_data:
            import uuid
            validated_data['access_token'] = str(uuid.uuid4())
        return super().create(validated_data)


class DocumentSerializer(serializers.ModelSerializer):
    # Note: Removed case_title and case_reference as Case relationship doesn't exist in Document model
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

    def update(self, instance, validated_data):
        # Handle file metadata on update
        if 'file' in validated_data and validated_data['file']:
            file_obj = validated_data['file']
            validated_data['file_size'] = file_obj.size
            validated_data['file_type'] = file_obj.content_type
            
        return super().update(instance, validated_data)


class DocumentCreateFromTemplateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    case_id = serializers.IntegerField(required=False)  # Made optional since case relationship might not exist
    title_fr = serializers.CharField(max_length=300)
    title_ar = serializers.CharField(max_length=300, required=False, allow_blank=True)
    variables = serializers.JSONField(required=False, default=dict)
    language = serializers.ChoiceField(choices=Document.LANGUAGE_CHOICES, default='fr')

    def validate_template_id(self, value):
        """Validate that template exists and is accessible by user"""
        try:
            template = DocumentTemplate.objects.get(id=value)
            user = self.context['request'].user
            if not template.is_public and template.user != user:
                raise serializers.ValidationError("Template not found or access denied.")
            return value
        except DocumentTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found.")

    def validate_case_id(self, value):
        """Validate case_id if provided and Case model exists"""
        if value is not None:
            # Uncomment and modify if Case model relationship exists
            # try:
            #     from cases.models import Case
            #     case = Case.objects.get(id=value)
            #     user = self.context['request'].user
            #     if case.user != user:
            #         raise serializers.ValidationError("Case not found or access denied.")
            #     return value
            # except Case.DoesNotExist:
            #     raise serializers.ValidationError("Case not found.")
            pass
        return value

    def create(self, validated_data):
        """Create document from template"""
        template_id = validated_data['template_id']
        template = DocumentTemplate.objects.get(id=template_id)
        user = self.context['request'].user
        
        # Choose content based on language
        if validated_data['language'] == 'ar' and template.content_ar:
            content = template.content_ar
        else:
            content = template.content_fr
            
        # Replace variables in content
        variables = validated_data.get('variables', {})
        for var_name, var_value in variables.items():
            content = content.replace(f'{{{var_name}}}', str(var_value))
        
        # Create document
        document_data = {
            'title_fr': validated_data['title_fr'],
            'title_ar': validated_data.get('title_ar', ''),
            'document_type': 'template',
            'template_type': template.template_type,
            'language': validated_data['language'],
            'content': content,
            'template': template,
            'user': user,
        }
        
        # Add case if provided and exists
        case_id = validated_data.get('case_id')
        if case_id:
            # Uncomment if Case relationship exists in Document model
            # document_data['case_id'] = case_id
            pass
            
        document = Document.objects.create(**document_data)
        return document