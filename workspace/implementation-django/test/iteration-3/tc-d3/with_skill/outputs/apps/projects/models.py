from django.conf import settings
from django.db import models

from apps.teams.models import Team, TimeStampedModel


class ProjectQuerySet(models.QuerySet):
    def for_team(self, team):
        return self.filter(team=team)

    def active(self):
        return self.filter(is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)


class Project(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_projects",
    )
    is_archived = models.BooleanField(db_default=False)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "slug"],
                name="unique_project_slug_per_team",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
