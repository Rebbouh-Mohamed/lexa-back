from rest_framework import serializers
from .models import Task, TaskComment

class TaskCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class TaskSerializer(serializers.ModelSerializer):
    # Read-only fields for display
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_reference = serializers.CharField(source='case.reference', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    
    # Add case_id as a write-only field to handle the frontend payload
    case_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['user', 'created_by', 'created_at', 'updated_at']
        extra_fields = ['case_id']  # Include the write-only field
    
    def create(self, validated_data):
        # Handle case_id if provided
        case_id = validated_data.pop('case_id', None)
        if case_id:
            from cases.models import Case
            try:
                case = Case.objects.get(id=case_id, user=self.context['request'].user)
                validated_data['case'] = case
            except Case.DoesNotExist:
                # You can either raise an error or set case to None
                validated_data['case'] = None
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Handle case_id if provided in updates
        case_id = validated_data.pop('case_id', None)
        if case_id is not None:  # Check for None to allow clearing the case
            if case_id:
                from cases.models import Case
                try:
                    case = Case.objects.get(id=case_id, user=self.context['request'].user)
                    validated_data['case'] = case
                except Case.DoesNotExist:
                    validated_data['case'] = None
            else:
                validated_data['case'] = None
        
        return super().update(instance, validated_data)