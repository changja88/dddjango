from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """프로젝트 초기부터 커스텀 User 모델을 사용한다.

    Django 공식 문서 권장사항:
    프로젝트 시작 시점에 커스텀 User 모델을 정의해야 한다.
    나중에 변경하면 마이그레이션이 매우 복잡해진다.
    """

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"

    def __str__(self):
        return self.username
