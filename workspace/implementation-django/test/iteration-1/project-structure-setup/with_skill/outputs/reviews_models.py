from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Review(TimeStampedModel):
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    content = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["book", "author"],
                name="review_unique_per_user_book",
            ),
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_range",
            ),
        ]

    def __str__(self):
        return f"Review by {self.author} on {self.book.title} ({self.rating}/5)"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.rating is not None and not (1 <= self.rating <= 5):
            raise ValidationError(
                {"rating": "Rating must be between 1 and 5."}
            )
