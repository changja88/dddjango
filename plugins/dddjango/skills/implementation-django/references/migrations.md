# 마이그레이션 베스트 프랙티스

## 기본 원칙 [DDoc] [TSD]

```bash
# 마이그레이션을 작게 유지한다
# sqlmigrate로 실제 SQL을 확인한다
python manage.py sqlmigrate myapp 0002

# 마이그레이션 파일은 반드시 버전 관리에 포함한다
# .gitignore에 migrations/를 추가하지 않는다
```

## 데이터 마이그레이션 [DDoc]

```python
from django.db import migrations

def forward_func(apps, schema_editor):
    User = apps.get_model("users", "User")
    for user in User.objects.filter(display_name=""):
        user.display_name = user.username
        user.save(update_fields=["display_name"])

def reverse_func(apps, schema_editor):
    pass  # 롤백 시 데이터 원복이 불가능하면 pass

class Migration(migrations.Migration):
    dependencies = [("users", "0005_add_display_name")]
    operations = [
        migrations.RunPython(forward_func, reverse_func),
    ]
```

- `apps.get_model()`로 히스토리 시점의 모델을 가져온다 -- 직접 임포트하지 않는다.
- 데이터 마이그레이션은 `squashmigrations`에서 보존되지 않으므로 별도 관리한다.

## 무중단(Zero-Downtime) 마이그레이션 [DfP]

```python
# 나쁜 예: NOT NULL 컬럼 추가와 동시에 배포
# -> 구버전 코드가 INSERT할 때 새 컬럼을 모르므로 제약 위반

# 좋은 예: 3단계 배포
# 1단계: NULL 허용 컬럼 추가 + 배포
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name="order",
            name="tracking_number",
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]

# 2단계: 데이터 채우기 + NOT NULL로 변경
# 3단계: 구버전 코드 제거
```

- 대형 테이블에서는 락 시간을 최소화하기 위해 마이그레이션을 작은 단위로 분할한다.
- PostgreSQL에서는 `django-pg-zero-downtime-migrations` 같은 도구를 고려한다.
- `AddIndex`는 PostgreSQL에서 `CREATE INDEX CONCURRENTLY`를 사용하도록 설정할 수 있다.
