from django.contrib import admin

from project.models import ProgressDetail,Project,ProjectType,ProjectChangeHistory,Major,Bank
# Register your models here.
admin.site.register(ProjectChangeHistory)
admin.site.register(Project)
admin.site.register(Major)
admin.site.register(ProjectType)
admin.site.register(Bank)
admin.site.register(ProgressDetail)