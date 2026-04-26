from django.conf import settings
from django.db import models


class Post(models.Model):
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
        choices=Category.choices,
    )
    has_attachment = models.BooleanField("첨부파일 여부", default=False)
    view_count = models.PositiveIntegerField("조회수", default=0)
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "게시글"
        verbose_name_plural = "게시글"

    def __str__(self):
        return self.title
