from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "application.catalog.infra_layer.django_catalog"
    # 앱 라벨 보존 — 테이블명 catalog_product/catalog_order 유지(기존 데이터 정합 §5.2).
    label = "catalog"
