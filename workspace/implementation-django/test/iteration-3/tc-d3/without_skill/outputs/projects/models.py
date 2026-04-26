from django.conf import settings
from django.db import models


class Project(models.Model):
    """A project that belongs to a team and contains tasks."""

    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects_project"
        constraints = [
            models.UniqueConstraint(
                fields=["team", "slug"],
                name="unique_project_slug_per_team",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
