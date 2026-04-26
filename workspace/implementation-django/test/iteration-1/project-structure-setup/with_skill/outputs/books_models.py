from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Book(TimeStampedModel):
    class Category(models.TextChoices):
        FICTION = "fiction", "Fiction"
        NON_FICTION = "non_fiction", "Non-Fiction"
        SCIENCE = "science", "Science"
        TECHNOLOGY = "technology", "Technology"
        HISTORY = "history", "History"
        PHILOSOPHY = "philosophy", "Philosophy"
        ART = "art", "Art"
        CHILDREN = "children", "Children"
        BIOGRAPHY = "biography", "Biography"
        OTHER = "other", "Other"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    isbn = models.CharField("ISBN", max_length=13, unique=True)
    published_date = models.DateField()
    category = models.CharField(
        max_length=20,
        choices=Category,
        default=Category.OTHER,
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-published_date"]
        indexes = [
            models.Index(fields=["isbn"], name="book_isbn_idx"),
            models.Index(fields=["category"], name="book_category_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=Decimal("0.01")),
                name="book_price_positive",
            ),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

    def get_absolute_url(self):
        return reverse("books:detail", kwargs={"pk": self.pk})

    def get_average_rating(self):
        result = self.reviews.aggregate(avg=models.Avg("rating"))
        return result["avg"]
