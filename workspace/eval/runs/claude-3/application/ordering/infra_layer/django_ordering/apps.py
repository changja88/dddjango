"""ordering 인프라 Django 앱 설정 (명세 §0 불변식5·§4.3).

AppConfig.name 은 점경로, label 은 짧은 'ordering' 으로 둔다 — 마이그레이션·
테이블 네임스페이스가 'ordering' 으로 잡히도록 한다.
"""
from django.apps import AppConfig


class DjangoOrderingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "application.ordering.infra_layer.django_ordering"
    label = "ordering"
