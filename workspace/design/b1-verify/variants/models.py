"""ORM 모델 — 변형별로 분리. PositiveIntegerField는 stock>=0 CHECK를 자동 생성한다(불변식 백스톱).

도메인 엔티티(domain.Product)와 의도적으로 다른 클래스다(표준 §0 #6).
"""
from django.db import models


class ProductNaive(models.Model):
    """대조군 — 동시성 보호 없음."""

    stock = models.PositiveIntegerField(default=0)


class ProductOptimistic(models.Model):
    """후보 — 낙관적 동시성. version이 경합을 감지한다(비즈니스 규칙 아님)."""

    stock = models.PositiveIntegerField(default=0)
    version = models.IntegerField(default=0)


class ProductConditional(models.Model):
    """현행 — 조건부 원자 UPDATE. 비즈니스 규칙이 SQL WHERE에 들어간다."""

    stock = models.PositiveIntegerField(default=0)
