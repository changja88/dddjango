import re

from django.conf import settings
from django.db import models

MENTION_PATTERN = re.compile(r"@(\w+)")


class Comment(models.Model):
    """A comment attached to a task, with @username mention support."""

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments_comment"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"

    def extract_mentions(self) -> list[str]:
        """Return a list of usernames mentioned via @username in the body."""
        return MENTION_PATTERN.findall(self.body)


class Mention(models.Model):
    """Persisted record of a user being mentioned in a comment."""

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="mentions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentions_received",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments_mention"
        constraints = [
            models.UniqueConstraint(
                fields=["comment", "user"],
                name="unique_mention_per_comment",
            ),
        ]

    def __str__(self):
        return f"@{self.user.username} in comment #{self.comment_id}"
