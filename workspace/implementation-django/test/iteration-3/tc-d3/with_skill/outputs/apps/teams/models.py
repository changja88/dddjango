from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Now


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Team(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MembershipQuerySet(models.QuerySet):
    def admins(self):
        return self.filter(role=Membership.Role.ADMIN)

    def active(self):
        return self.filter(is_active=True)

    def for_user(self, user):
        return self.filter(user=user)


class Membership(TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=10,
        choices=Role,
        default=Role.MEMBER,
    )
    is_active = models.BooleanField(db_default=True)

    objects = MembershipQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["team", "user"],
                name="unique_team_member",
            ),
        ]
        ordering = ["team", "user"]

    def __str__(self):
        return f"{self.user} - {self.team} ({self.get_role_display()})"

    def clean(self):
        if (
            self.role != self.Role.ADMIN
            and self.pk is None
            and not Membership.objects.filter(
                team=self.team, role=self.Role.ADMIN
            ).exists()
        ):
            raise ValidationError(
                "A team must have at least one admin before adding other roles."
            )
