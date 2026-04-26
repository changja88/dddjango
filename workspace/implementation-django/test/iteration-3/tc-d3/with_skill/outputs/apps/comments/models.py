import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from apps.tasks.models import Task
from apps.teams.models import TimeStampedModel

MENTION_PATTERN = re.compile(r"@(\w+)")


class CommentQuerySet(models.QuerySet):
    def for_task(self, task):
        return self.filter(task=task)

    def with_relations(self):
        return self.select_related("author").prefetch_related("mentions")

    def by_user(self, user):
        return self.filter(author=user)

    def mentioning(self, user):
        return self.filter(mentions=user)


class Comment(TimeStampedModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="mentioned_in_comments",
    )

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["task", "created_at"],
                name="idx_comment_task_created",
            ),
        ]

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._sync_mentions()

    def _sync_mentions(self):
        usernames = set(MENTION_PATTERN.findall(self.body))
        if not usernames:
            self.mentions.clear()
            return

        user_model = get_user_model()
        mentioned_users = user_model.objects.filter(username__in=usernames)
        self.mentions.set(mentioned_users)

    def extract_mention_usernames(self):
        return set(MENTION_PATTERN.findall(self.body))
