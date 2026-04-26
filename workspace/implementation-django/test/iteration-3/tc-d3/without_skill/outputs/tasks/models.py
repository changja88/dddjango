from django.conf import settings
from django.db import models


class Task(models.Model):
    """A task that belongs to a project."""

    class Status(models.TextChoices):
        BACKLOG = "backlog", "백로그"
        IN_PROGRESS = "in_progress", "진행중"
        REVIEW = "review", "리뷰"
        DONE = "done", "완료"

    class Priority(models.TextChoices):
        URGENT = "urgent", "긴급"
        HIGH = "high", "높음"
        NORMAL = "normal", "보통"
        LOW = "low", "낮음"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BACKLOG,
        db_index=True,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks_task"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["assignee", "status"]),
        ]

    def __str__(self):
        return self.title
