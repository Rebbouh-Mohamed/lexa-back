from rest_framework import serializers
from .models import AlgerianLegalCode, AlgerianCourt, TaxConfiguration, LegalProcedure

class AlgerianLegalCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgerianLegalCode
        fields = '__all__'

class AlgerianCourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgerianCourt
        fields = '__all__'

class TaxConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxConfiguration
        fields = '__all__'

class LegalProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalProcedure
        fields = '__all__'
