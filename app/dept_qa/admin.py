from django.contrib import admin
from .models import Task, Checklist, ChecklistTask, IssueResolution

admin.site.register(Task)
admin.site.register(Checklist)
admin.site.register(ChecklistTask)
admin.site.register(IssueResolution)
