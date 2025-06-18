from rest_framework import serializers
from .models import Jurisdiction, CaseType, Case, Audience, CaseMetric

class JurisdictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jurisdiction
        fields = '__all__'

class CaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseType
        fields = '__all__'

class CaseMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseMetric
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class AudienceSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    
    class Meta:
        model = Audience
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate(self, data):
        # Set default values for required fields if not provided
        if 'result_fr' not in data:
            data['result_fr'] = "report"
        if 'result_ar' not in data:
            data['result_ar'] = "تأجيل"
        if 'judge_name' not in data:
            data['judge_name'] = ""
        return data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class CaseSerializer(serializers.ModelSerializer):
    jurisdiction_name = serializers.CharField(source='jurisdiction.name_fr', read_only=True)
    case_type_name = serializers.CharField(source='case_type.subtype_fr', read_only=True)
    audiences = AudienceSerializer(many=True, read_only=True)
    metrics = CaseMetricSerializer(read_only=True)
    audiences_count = serializers.SerializerMethodField()
    # documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Case
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_audiences_count(self, obj):
        return obj.audiences.count()

    # def get_documents_count(self, obj):
    #     return obj.documents.count()

class CaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        exclude = ['user']

    def create(self, validated_data):
        
        validated_data['user'] = self.context['request'].user
        case = super().create(validated_data)
        # Create associated metrics
        CaseMetric.objects.create(case=case, user=case.user)
        return case