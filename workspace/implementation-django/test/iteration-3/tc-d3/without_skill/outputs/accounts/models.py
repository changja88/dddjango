from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for the SaaS project management tool."""

    email = models.EmailField("email address", unique=True)
    display_name = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "accounts_user"
        ordering = ["email"]

    def __str__(self):
        return self.display_name or self.username
