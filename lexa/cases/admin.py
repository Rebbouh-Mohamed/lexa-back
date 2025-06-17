from django.contrib import admin
from .models import Case,CaseMetric,CaseType,Jurisdiction,Audience

admin.site.register(Case)
admin.site.register(CaseMetric)

admin.site.register(CaseType)
admin.site.register(Jurisdiction)
admin.site.register(Audience)

