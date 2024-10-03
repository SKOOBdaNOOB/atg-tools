from django.db import models
from app.core.models import Platform, Component, ProductGeneration


class Task(models.Model):
    """
    Represents tasks or subtasks needed for QA checklists.
    """
    name = models.CharField(max_length=500)
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subtasks', blank=True, null=True)
    components = models.ManyToManyField(Component, related_name='tasks', blank=True)
    product_generations = models.ManyToManyField(ProductGeneration, related_name='tasks', blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def is_subtask(self):
        """
        Determines if the task is a subtask.
        """
        return self.parent_task is not None


class Checklist(models.Model):
    """
    Represents a QA checklist for a specific platform.
    """
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, related_name='checklists')
    created_on = models.DateTimeField(auto_now_add=True)
    completed_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Checklist for {self.platform.iris_number} - {self.created_on.strftime('%Y-%m-%d')}"

    def is_complete(self):
        """
        Checks if all tasks are marked as complete.
        Returns False if there are no tasks.
        """
        if not self.tasks.exists():
            return False
        return not self.tasks.filter(status__in=['Incomplete', 'Failed']).exists()
    
    def completion_percentage(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='Complete').count()
        return int((completed_tasks / total_tasks) * 100)


class ChecklistTask(models.Model):
    """
    Tracks the status of individual tasks within a checklist.
    """
    STATUS_CHOICES = [
        ('Complete', 'Complete'),
        ('Incomplete', 'Incomplete'),
        ('Failed', 'Failed'),
    ]

    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Incomplete')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('checklist', 'task')
        ordering = ['task__order']

    def __str__(self):
        return f"{self.task.name} - {self.status}"


class IssueResolution(models.Model):
    """
    Records issues found during QA and their resolutions.
    """
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='issues')
    issue_description = models.TextField()
    resolution = models.TextField(blank=True, null=True)
    reported_on = models.DateTimeField(auto_now_add=True)
    resolved_on = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Issue on {self.checklist.platform.iris_number} - Reported on {self.reported_on.strftime('%Y-%m-%d')}"
