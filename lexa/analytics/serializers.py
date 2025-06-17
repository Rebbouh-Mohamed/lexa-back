from rest_framework import serializers
from .models import CaseAnalytic, RevenueAnalytic

class CaseAnalyticSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    
    class Meta:
        model = CaseAnalytic
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class RevenueAnalyticSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueAnalytic
        fields = '__all__'
        read_only_fields = ['user', 'created_at']