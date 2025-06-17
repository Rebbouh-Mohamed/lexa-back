from rest_framework import serializers
from .models import ClientAccess, ClientMessage, ClientDocument

class ClientAccessSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ClientAccess
        fields = '__all__'
        read_only_fields = ['access_token', 'created_by', 'created_at']

class ClientMessageSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    
    class Meta:
        model = ClientMessage
        fields = '__all__'
        read_only_fields = ['created_at']

class ClientDocumentSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title_fr', read_only=True)
    document_type = serializers.CharField(source='document.document_type', read_only=True)
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    
    class Meta:
        model = ClientDocument
        fields = '__all__'
        read_only_fields = ['shared_by', 'created_at']