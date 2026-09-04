from __future__ import annotations

from django.contrib import admin

_SharedAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin  # 타 모듈 맨몸 별칭 — 사용처의 헤더 ignore 만 #646 ⓑ(별칭 해소는 같은 모듈 안)
