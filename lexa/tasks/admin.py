from django.contrib import admin
from .models import Task, TaskComment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'case', 'priority', 'status', 'assigned_to', 'due_date', 'created_at')
    list_filter = ('priority', 'status', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'case__reference')
    ordering = ('-created_at',)

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    search_fields = ('task__title', 'comment')
    ordering = ('-created_at',)