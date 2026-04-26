from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Now

from apps.projects.models import Project
from apps.teams.models import Membership, TimeStampedModel


class TaskQuerySet(models.QuerySet):
    def for_project(self, project):
        return self.filter(project=project)

    def by_status(self, status):
        return self.filter(status=status)

    def assigned_to(self, user):
        return self.filter(assignee=user)

    def backlog(self):
        return self.filter(status=Task.Status.BACKLOG)

    def in_progress(self):
        return self.filter(status=Task.Status.IN_PROGRESS)

    def in_review(self):
        return self.filter(status=Task.Status.REVIEW)

    def done(self):
        return self.filter(status=Task.Status.DONE)

    def urgent(self):
        return self.filter(priority=Task.Priority.URGENT)

    def with_relations(self):
        return self.select_related("project", "assignee", "created_by")


class Task(TimeStampedModel):
    class Status(models.TextChoices):
        BACKLOG = "backlog", "Backlog"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        NORMAL = 2, "Normal"
        HIGH = 3, "High"
        URGENT = 4, "Urgent"

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        db_default=Status.BACKLOG,
    )
    priority = models.IntegerField(
        choices=Priority,
        db_default=Priority.NORMAL,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    position = models.PositiveIntegerField(db_default=0)

    objects = TaskQuerySet.as_manager()

    class Meta:
        ordering = ["-priority", "position", "-created_at"]
        indexes = [
            models.Index(
                fields=["project", "status"],
                name="idx_task_project_status",
            ),
            models.Index(
                fields=["assignee", "status"],
                name="idx_task_assignee_status",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(priority__gte=1, priority__lte=4),
                name="task_priority_valid_range",
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        if self.assignee_id and self.project_id:
            team = self.project.team
            if not Membership.objects.filter(
                team=team, user=self.assignee, is_active=True
            ).exists():
                raise ValidationError(
                    {"assignee": "Assignee must be an active member of the project's team."}
                )

        if self.completed_at and self.status != self.Status.DONE:
            raise ValidationError(
                {"completed_at": "completed_at can only be set when status is done."}
            )

    def mark_done(self):
        from django.utils import timezone

        self.status = self.Status.DONE
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def transition_to(self, new_status):
        self.status = new_status
        if new_status == self.Status.DONE:
            self.mark_done()
            return
        if self.status != self.Status.DONE and self.completed_at:
            self.completed_at = None
        self.save(update_fields=["status", "completed_at", "updated_at"])
