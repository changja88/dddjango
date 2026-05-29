"""B1 검증용 최소 Django 설정 — 파일 기반 SQLite(스레드 공유 가능)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "b1-verify-not-a-secret"
DEBUG = True
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "variants",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # 인메모리가 아닌 파일 DB — 스레드 부하 테스트에서 연결 간 공유가 필요하다.
        "NAME": BASE_DIR / "b1verify.sqlite3",
        "OPTIONS": {
            # 쓰기 락 충돌 시 즉시 죽지 않고 잠시 대기(스레드 부하 테스트 안정화).
            "timeout": 20,
        },
        # 테스트 DB를 *파일*로 강제한다. 기본값(공유캐시 인메모리)은 테이블 락(SQLITE_LOCKED)이
        # busy_timeout으로 재시도되지 않아 스레드 부하 테스트가 죽는다. 파일 DB는 SQLITE_BUSY라
        # timeout으로 직렬화된다.
        "TEST": {"NAME": BASE_DIR / "test_b1verify.sqlite3"},
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
