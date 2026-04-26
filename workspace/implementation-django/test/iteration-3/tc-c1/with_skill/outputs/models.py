from django.conf import settings
from django.db import models
from django.db.models import F
from django.db.models.functions import Now


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PostQuerySet(models.QuerySet):
    def by_category(self, category):
        return self.filter(category=category)

    def by_author(self, user):
        return self.filter(author=user)

    def notices(self):
        return self.filter(category=Post.Category.NOTICE)

    def list_fields(self):
        return self.select_related("author").only(
            "id",
            "title",
            "category",
            "view_count",
            "created_at",
            "author__id",
            "author__username",
        )


class Post(TimeStampedModel):
    class Category(models.TextChoices):
        NOTICE = "notice", "공지"
        FREE = "free", "자유"
        QUESTION = "question", "질문"

    title = models.CharField("제목", max_length=200)
    content = models.TextField("내용")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="작성자",
    )
    category = models.CharField(
        "카테고리",
        max_length=20,
        choices=Category,
        default=Category.FREE,
    )
    has_attachment = models.BooleanField("첨부파일 여부", db_default=False)
    view_count = models.PositiveIntegerField("조회수", db_default=0)

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = "게시글"
        verbose_name_plural = "게시글"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="post_created_desc_idx"),
            models.Index(fields=["category"], name="post_category_idx"),
            models.Index(fields=["author"], name="post_author_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(view_count__gte=0),
                name="post_view_count_non_negative",
            ),
        ]

    def __str__(self):
        return self.title

    def increment_view_count(self):
        Post.objects.filter(pk=self.pk).update(view_count=F("view_count") + 1)
        self.refresh_from_db(fields=["view_count"])
