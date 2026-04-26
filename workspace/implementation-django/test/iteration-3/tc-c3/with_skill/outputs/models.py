from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.db.models.functions import Now


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Seller(TimeStampedModel):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(db_default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=Product.Status.ACTIVE)

    def by_category(self, category_slug):
        return self.filter(category__slug=category_slug)

    def by_price_range(self, min_price=None, max_price=None):
        qs = self
        if min_price is not None:
            qs = qs.filter(price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(price__lte=max_price)
        return qs

    def with_avg_rating(self):
        return self.annotate(avg_rating=Avg("reviews__rating"))


class Product(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(db_default=0)
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        db_default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    status = models.CharField(
        max_length=20,
        choices=Status,
        default=Status.ACTIVE,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name="products",
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["category", "price"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name="product_price_non_negative",
            ),
            models.CheckConstraint(
                check=models.Q(discount_rate__gte=0, discount_rate__lte=100),
                name="product_discount_rate_range",
            ),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.price is not None and self.price < 0:
            raise ValidationError({"price": "Price must be non-negative."})
        if (
            self.discount_rate is not None
            and not (Decimal("0") <= self.discount_rate <= Decimal("100"))
        ):
            raise ValidationError(
                {"discount_rate": "Discount rate must be between 0 and 100."}
            )

    @property
    def discounted_price(self):
        if self.discount_rate:
            return self.price * (1 - self.discount_rate / Decimal("100"))
        return self.price


class Review(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_range",
            ),
        ]

    def __str__(self):
        return f"Review({self.product_id}, {self.rating})"
