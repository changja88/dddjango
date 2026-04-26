from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Book(models.Model):
    class Category(models.TextChoices):
        FICTION = "fiction", "Fiction"
        NON_FICTION = "non_fiction", "Non-Fiction"
        SCIENCE = "science", "Science"
        TECHNOLOGY = "technology", "Technology"
        HISTORY = "history", "History"
        PHILOSOPHY = "philosophy", "Philosophy"
        ART = "art", "Art"
        CHILDREN = "children", "Children"
        COMICS = "comics", "Comics"
        OTHER = "other", "Other"

    title = models.CharField("제목", max_length=255)
    author = models.CharField("저자", max_length=255)
    price = models.DecimalField("가격", max_digits=10, decimal_places=2)
    isbn = models.CharField("ISBN", max_length=13, unique=True)
    published_date = models.DateField("출판일")
    category = models.CharField(
        "카테고리",
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    description = models.TextField("설명", blank=True, default="")
    created_at = models.DateTimeField("등록일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "도서"
        verbose_name_plural = "도서 목록"
        indexes = [
            models.Index(fields=["isbn"]),
            models.Index(fields=["category"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.author})"

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=models.Avg("rating"))["avg"]
        if avg is None:
            return 0
        return round(avg, 1)

    @property
    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="도서",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="작성자",
    )
    rating = models.PositiveSmallIntegerField(
        "별점",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "리뷰"
        verbose_name_plural = "리뷰 목록"
        constraints = [
            models.UniqueConstraint(
                fields=["book", "reviewer"],
                name="unique_review_per_user_per_book",
            ),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.reviewer} ({self.rating}점)"
