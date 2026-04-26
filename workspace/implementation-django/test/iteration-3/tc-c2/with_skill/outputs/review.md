# DRF Code Review: ProductSerializer / ProductViewSet

## Review Findings

### 1. `fields = '__all__'` in Serializer

```
[DRF Serializer 설계] -- fields = "__all__"은 모델에 새 필드가 추가될 때 의도치 않은
데이터 노출 위험이 있다. 목록/상세/생성/수정 시나리오마다 Serializer를 분리하고, 각각
명시적 필드 목록을 선언해야 한다.
```

### 2. 단일 Serializer로 모든 액션을 처리

```
[DRF Serializer 설계] -- 하나의 ProductSerializer가 list, detail, create, update를
모두 담당한다. 읽기 응답에 불필요한 쓰기 필드가 노출되거나, 생성 시 설정하면 안 되는
필드가 입력 가능해지는 보안 문제가 발생할 수 있다. get_serializer_class()를 오버라이드
하여 액션별 Serializer를 반환해야 한다.
```

### 3. create()에서 perform_create() 미사용

```
[DRF ViewSet/Router] -- create() 전체를 오버라이드하면 DRF가 제공하는 validation,
response 생성, content negotiation 파이프라인을 우회한다. DRF는 이 목적으로
perform_create() 훅을 제공하며, serializer.save(created_by=request.user) 한 줄로
동일한 결과를 얻을 수 있다.
```

### 4. 이중 save() -- update_fields 없이 전체 필드 재저장

```
[Performance] -- create()에서 serializer.save()로 객체를 생성한 뒤,
product.created_by를 설정하고 product.save()를 다시 호출한다. 이는 불필요한 두 번째
INSERT/UPDATE를 발생시킨다. perform_create()에서 serializer.save(created_by=
request.user)를 사용하면 한 번의 save()로 해결된다. 불가피하게 두 번째 save()가
필요한 경우에도 save(update_fields=["created_by"])로 변경된 필드만 업데이트해야 한다.
```

### 5. list()에서 queryset 속성 무시 및 재선언

```
[DRF ViewSet/Router] -- ViewSet에 이미 queryset = Product.objects.all()이 선언되어
있지만, list()에서 Product.objects.all()을 다시 호출한다. DRF의 get_queryset() 메커
니즘이 무시되며, 필터링, 페이지네이션, 권한 체크 등 DRF 내장 파이프라인이 모두 우회된다.
list()를 오버라이드할 필요 없이 기본 구현을 그대로 사용하면 된다.
```

### 6. Pagination 미적용

```
[DRF Pagination] -- list()를 수동으로 오버라이드하면서 self.paginate_queryset()를
호출하지 않는다. 데이터가 늘어나면 전체 레코드를 한 번에 반환하게 되어 응답 시간과 메모리
사용량이 급격히 증가한다. 기본 list()를 사용하거나, 수동 오버라이드 시 반드시
paginate_queryset()과 get_paginated_response()를 호출해야 한다.
```

### 7. Permission 미설정

```
[DRF Permission] -- permission_classes가 지정되지 않아 DRF 기본 설정
(AllowAny일 경우)에 의존한다. 인증되지 않은 사용자가 create/update/delete를
수행할 수 있는 보안 취약점이 된다. 최소한
permission_classes = [permissions.IsAuthenticatedOrReadOnly]를 명시해야 한다.
```

### 8. queryset에 select_related/prefetch_related 누락

```
[QuerySet] -- Product 모델이 FK 관계(created_by 등)를 가진다면, queryset에
select_related()를 적용하지 않으면 Serializer에서 관련 객체 접근 시 N+1 쿼리가
발생한다. queryset 선언 시 접근 패턴에 맞는 select_related/prefetch_related를
추가해야 한다.
```

## Review Checklist

- [x] Project structure: N/A (단일 파일 리뷰)
- [x] Model field ordering: N/A (모델 정의 미포함)
- [x] Boolean flag proliferation: N/A
- [ ] Missing select_related/prefetch_related on FK/M2M access in loops -- **Finding #8**
- [ ] N+1 queries in views or templates -- **Finding #8과 연관**
- [ ] save() without update_fields when only specific fields changed -- **Finding #4**
- [x] Signals used for same-app logic: 해당 없음
- [ ] fields = "__all__" in Serializer -- **Finding #1**
- [x] Multi-table inheritance: 해당 없음
- [x] Raw SQL with string interpolation: 해당 없음
- [x] Missing CSRF protection: DRF SessionAuthentication은 CSRF 내장 적용
- [x] CBV with 4+ Mixins: 해당 없음
- [ ] Fat views with business logic that belongs in model/service -- **Finding #3, #4**
- [x] Missing assertNumQueries: N/A (테스트 코드 미포함)
- [x] Django 5.x features not used: N/A (모델 정의 미포함)
