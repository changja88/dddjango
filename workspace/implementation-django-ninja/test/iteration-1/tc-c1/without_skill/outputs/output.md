# DRF to Django Ninja 전환 결과

```python
from ninja import Router, Schema
from ninja.security import django_auth
from datetime import datetime
from typing import Optional

# --- Schemas (DRF Serializer 대체) ---

class TaskOut(Schema):
    id: int
    title: str
    description: str
    status: str
    assignee: Optional[int] = None
    created_at: datetime

class TaskIn(Schema):
    title: str
    description: str
    assignee: Optional[int] = None

# --- Router (DRF ViewSet 대체) ---

router = Router(auth=django_auth, tags=["tasks"])


@router.get("/", response=list[TaskOut])
def list_tasks(request, status: Optional[str] = None):
    qs = Task.objects.all()
    if status:
        qs = qs.filter(status=status)
    return qs


@router.get("/{task_id}", response=TaskOut)
def get_task(request, task_id: int):
    return Task.objects.get(id=task_id)


@router.post("/", response={201: TaskOut})
def create_task(request, payload: TaskIn):
    task = Task.objects.create(**payload.dict())
    return 201, task


@router.put("/{task_id}", response=TaskOut)
def update_task(request, task_id: int, payload: TaskIn):
    task = Task.objects.get(id=task_id)
    for attr, value in payload.dict().items():
        setattr(task, attr, value)
    task.save()
    return task


@router.delete("/{task_id}", response={204: None})
def delete_task(request, task_id: int):
    Task.objects.filter(id=task_id).delete()
    return 204, None


@router.post("/{task_id}/complete", response=TaskOut)
def complete_task(request, task_id: int):
    task = Task.objects.get(id=task_id)
    task.status = "completed"
    task.save(update_fields=["status"])
    return task
```

## 주요 변경 사항

| DRF | Django Ninja | 설명 |
|---|---|---|
| `serializers.ModelSerializer` | `Schema` (Pydantic) | 입출력 스키마를 Pydantic 모델로 정의 |
| `viewsets.ModelViewSet` | `Router` + 개별 함수 | 클래스 기반 ViewSet 대신 함수 기반 엔드포인트 |
| `permissions.IsAuthenticated` | `auth=django_auth` | Router 레벨에서 인증 설정 |
| `get_serializer_class()` 분기 | 입력/출력 Schema 분리 | `TaskIn`(입력), `TaskOut`(출력)으로 명시적 분리 |
| `@action(detail=True)` | `@router.post("/{task_id}/complete")` | 커스텀 액션을 일반 엔드포인트로 전환 |
| `request.query_params.get('status')` | 함수 파라미터 `status: Optional[str] = None` | 쿼리 파라미터가 함수 시그니처로 자동 매핑 |

## URL 등록 방법

```python
# api.py
from ninja import NinjaAPI

api = NinjaAPI()
api.add_router("/tasks", router)

# urls.py
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```
