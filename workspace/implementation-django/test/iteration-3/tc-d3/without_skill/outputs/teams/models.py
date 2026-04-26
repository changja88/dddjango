from django.conf import settings
from django.db import models


class Team(models.Model):
    """A team that owns projects."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="TeamMembership",
        related_name="teams",
    )

    class Meta:
        db_table = "teams_team"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TeamMembership(models.Model):
    """Through model that tracks a user's role within a team."""

    class Role(models.TextChoices):
        ADMIN = "admin", "관리자"
        MEMBER = "member", "멤버"
        VIEWER = "viewer", "뷰어"

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teams_membership"
        constraints = [
            models.UniqueConstraint(
                fields=["team", "user"],
                name="unique_team_membership",
            ),
        ]
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user} - {self.team} ({self.get_role_display()})"
