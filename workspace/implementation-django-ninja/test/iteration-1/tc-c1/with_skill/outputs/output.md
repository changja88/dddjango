# DRF -> Django Ninja 전환

## 전환된 코드

### schemas.py

```python
from ninja import ModelSchema, FilterSchema, Schema
from typing import Optional

from .models import Task


class TaskOut(ModelSchema):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assignee', 'created_at']


class TaskIn(Schema):
    title: str
    description: str
    assignee: Optional[int] = None


class TaskFilterSchema(FilterSchema):
    status: Optional[str] = None
```

### api.py

```python
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.errors import HttpError
from ninja.pagination import paginate, LimitOffsetPagination
from ninja.security import SessionAuth

from .models import Task
from .schemas import TaskOut, TaskIn, TaskFilterSchema

router = Router(tags=["tasks"], auth=SessionAuth())


@router.get("/", response=List[TaskOut])
@paginate(LimitOffsetPagination)
def list_tasks(request, filters: Query[TaskFilterSchema]):
    qs = Task.objects.all()
    return filters.filter(qs)


@router.get("/{task_id}", response=TaskOut)
def get_task(request, task_id: int) -> TaskOut:
    return get_object_or_404(Task, id=task_id)


@router.post("/", response={201: TaskOut})
def create_task(request, payload: TaskIn) -> tuple:
    task = Task.objects.create(**payload.dict())
    return 201, task


@router.put("/{task_id}", response=TaskOut)
def update_task(request, task_id: int, payload: TaskIn) -> TaskOut:
    task = get_object_or_404(Task, id=task_id)
    for attr, value in payload.dict().items():
        setattr(task, attr, value)
    task.save()
    return task


@router.delete("/{task_id}", response={204: None})
def delete_task(request, task_id: int) -> tuple:
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return 204, None


@router.post("/{task_id}/complete", response=TaskOut)
def complete_task(request, task_id: int) -> TaskOut:
    task = get_object_or_404(Task, id=task_id)
    task.status = 'completed'
    task.save(update_fields=['status'])
    return task
```

---

## 변경 사항 상세

### 1. DRF Serializer -> Django Ninja Schema

```
[Before]
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assignee', 'created_at']

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee']

[After]
class TaskOut(ModelSchema):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assignee', 'created_at']

class TaskIn(Schema):
    title: str
    description: str
    assignee: Optional[int] = None

[Reason] Schema Design -- ModelSchema를 사용하여 모델 기반 응답 스키마를 자동 생성한다. 입력 스키마는 Schema를 사용하여 명시적 타입 힌트로 요청 데이터를 검증한다. DRF Serializer는 사용하지 않는다.
```

### 2. DRF ViewSet -> Router + 데코레이터 엔드포인트

```
[Before]
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

[After]
router = Router(tags=["tasks"], auth=SessionAuth())

@router.get("/", response=List[TaskOut])
@paginate(LimitOffsetPagination)
def list_tasks(request, filters: Query[TaskFilterSchema]):
    qs = Task.objects.all()
    return filters.filter(qs)

@router.post("/", response={201: TaskOut})
def create_task(request, payload: TaskIn) -> tuple:
    task = Task.objects.create(**payload.dict())
    return 201, task

# ... (get, update, delete 각각 개별 함수로 분리)

[Reason] Routing -- ViewSet을 Router() + 데코레이터 패턴으로 전환한다. 각 엔드포인트를 독립적인 함수로 분리하여 명확한 책임을 가지게 한다. get_serializer_class() 분기 대신, 각 엔드포인트가 자신의 입력/출력 스키마를 직접 선언한다.
```

### 3. DRF permission_classes -> Ninja auth

```
[Before]
permission_classes = [permissions.IsAuthenticated]

[After]
router = Router(tags=["tasks"], auth=SessionAuth())

[Reason] Authentication -- DRF의 permission_classes 대신 Django Ninja의 내장 인증 클래스를 사용한다. SessionAuth()를 Router 수준에서 적용하여 모든 엔드포인트에 인증을 일괄 적용한다.
```

### 4. 수동 쿼리 파라미터 필터링 -> FilterSchema

```
[Before]
def get_queryset(self):
    qs = super().get_queryset()
    status_filter = self.request.query_params.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return qs

[After]
class TaskFilterSchema(FilterSchema):
    status: Optional[str] = None

@router.get("/", response=List[TaskOut])
@paginate(LimitOffsetPagination)
def list_tasks(request, filters: Query[TaskFilterSchema]):
    qs = Task.objects.all()
    return filters.filter(qs)

[Reason] Filtering -- 수동 query_params 파싱 대신 FilterSchema를 사용한다. FilterSchema는 None 값을 자동으로 무시하고(ignore_none=True 기본값), 타입 안전한 필터링을 제공하며, 필터 추가 시 코드 변경이 최소화된다.
```

### 5. 리스트 엔드포인트에 페이지네이션 추가

```
[Before]
# ViewSet.list()에 페이지네이션 없음 (DRF 기본 페이지네이션 미설정 시)

[After]
@router.get("/", response=List[TaskOut])
@paginate(LimitOffsetPagination)
def list_tasks(request, filters: Query[TaskFilterSchema]):
    qs = Task.objects.all()
    return filters.filter(qs)

[Reason] Pagination -- 리스트 엔드포인트에 @paginate 데코레이터를 적용하여 페이지네이션을 제공한다. LimitOffsetPagination을 사용하여 limit/offset 기반 페이지네이션을 지원한다.
```

### 6. @action(detail=True) -> 개별 라우터 엔드포인트

```
[Before]
@action(detail=True, methods=['post'])
def complete(self, request, pk=None):
    task = self.get_object()
    task.status = 'completed'
    task.save(update_fields=['status'])
    return Response(TaskSerializer(task).data)

[After]
@router.post("/{task_id}/complete", response=TaskOut)
def complete_task(request, task_id: int) -> TaskOut:
    task = get_object_or_404(Task, id=task_id)
    task.status = 'completed'
    task.save(update_fields=['status'])
    return task

[Reason] Routing -- DRF의 @action 데코레이터 대신 표준 라우터 데코레이터(@router.post)로 커스텀 액션을 구현한다. 경로 파라미터에 타입 힌트(task_id: int)를 명시하여 자동 검증을 수행하고, response=TaskOut으로 응답 스키마를 선언하여 반환 객체가 자동으로 직렬화된다.
```

### 7. 타입 힌트 추가

```
[Before]
# DRF ViewSet에는 파라미터/반환 타입 힌트 없음

[After]
def list_tasks(request, filters: Query[TaskFilterSchema]):
def get_task(request, task_id: int) -> TaskOut:
def create_task(request, payload: TaskIn) -> tuple:
def update_task(request, task_id: int, payload: TaskIn) -> TaskOut:
def delete_task(request, task_id: int) -> tuple:
def complete_task(request, task_id: int) -> TaskOut:

[Reason] Baseline requirement -- 모든 엔드포인트 파라미터와 반환 타입에 타입 힌트를 명시한다. Django Ninja는 타입 힌트를 기반으로 자동 파싱, 유효성 검증, OpenAPI 문서 생성을 수행한다.
```
