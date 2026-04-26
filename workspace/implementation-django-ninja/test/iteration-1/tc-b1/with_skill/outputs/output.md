# Code Review: PostSerializer / PostViewSet (DRF)

이 코드는 Django REST Framework(DRF) 패턴으로 작성되어 있다. 프로젝트의 API 구현 컨벤션에 따라 DRF는 사용하지 않으며, 모든 API 코드는 Django Ninja로 구현해야 한다. 아래는 리뷰 체크리스트 전 항목에 대한 점검 결과다.

---

## Findings

**[DRF Serializer 사용]** -- `serializers.ModelSerializer`는 DRF 고유 패턴이다. Django Ninja에서는 `Schema` 또는 `ModelSchema`를 사용하여 요청/응답 데이터를 검증하고 직렬화한다. `PostSerializer`를 `PostOut(ModelSchema)`와 `PostIn(Schema)`으로 전환해야 한다.

**[DRF ViewSet 사용]** -- `viewsets.ModelViewSet`은 DRF의 클래스 기반 뷰 패턴이다. Django Ninja에서는 `Router()` 인스턴스에 `@router.get`, `@router.post` 등 데코레이터 패턴으로 개별 엔드포인트를 정의한다. `PostViewSet` 전체를 Router 기반 함수 엔드포인트로 전환해야 한다.

**[DRF permission_classes 사용]** -- `permissions.IsAuthenticated`는 DRF의 인증/권한 시스템이다. Django Ninja에서는 `HttpBearer`, `SessionAuth` 등 내장 auth 클래스를 `auth=` 파라미터로 전달한다. Router 수준 또는 개별 엔드포인트 수준에서 `auth=SessionAuth()` 등으로 설정해야 한다.

**[DRF PageNumberPagination 사용]** -- `rest_framework.pagination.PageNumberPagination`은 DRF의 페이지네이션 클래스다. Django Ninja에서는 `ninja.pagination`의 `@paginate` 데코레이터와 `PageNumberPagination`을 사용한다. 리스트 엔드포인트에 `@paginate(PageNumberPagination)`을 적용해야 한다.

**[fields = '\_\_all\_\_' 사용]** -- `Meta.fields = '__all__'`은 모델의 모든 필드를 노출하므로 해시된 비밀번호 등 민감한 데이터가 유출될 수 있다. Django Ninja의 `ModelSchema`에서도 동일하게 위험하며, 반드시 노출할 필드를 명시적으로 나열해야 한다.

**[타입 힌트 부재]** -- DRF ViewSet에는 함수 파라미터와 반환 타입에 대한 타입 힌트가 없다. Django Ninja에서는 모든 엔드포인트 파라미터와 반환 타입에 타입 힌트가 필수다. 이는 자동 유효성 검증과 OpenAPI 문서 생성의 기반이 된다.

**[에러 처리 부재]** -- 존재하지 않는 Post 조회, 권한 위반 등에 대한 에러 처리가 없다. Django Ninja에서는 `HttpError(status, message)`를 사용하거나 `@api.exception_handler()`로 일관된 에러 응답(RFC 9457 Problem Details 형식 권장)을 반환해야 한다.

**[비동기 미적용]** -- 데이터베이스 I/O가 포함된 뷰이므로 `async def`와 비동기 ORM 패턴을 고려할 수 있다. Django 4.1+ 환경이라면 비동기 엔드포인트로 전환하여 동시 처리 성능을 개선할 여지가 있다.

**[FilterSchema 미사용]** -- 목록 조회 시 필터링 로직이 없다. 검색이나 조건부 조회가 필요한 경우 Django Ninja의 `FilterSchema`와 `FilterLookup`을 사용하여 타입 안전한 필터링을 구현해야 한다.

**[입력 유효성 검증 부재]** -- `perform_create`에서 요청 본문을 Schema로 검증하지 않고 DRF Serializer에 의존하고 있다. Django Ninja에서는 엔드포인트 파라미터에 Schema 타입을 지정하면 요청 본문이 자동으로 검증된다.

---

## Review Checklist

| # | 항목 | 결과 |
|---|------|------|
| 1 | DRF 패턴 사용 (Serializer, ViewSet, APIView) | FOUND -- Serializer, ViewSet 모두 사용 |
| 2 | 엔드포인트 파라미터/반환 타입 힌트 누락 | FOUND -- 타입 힌트 없음 |
| 3 | Schema에서 모든 모델 필드 노출 | FOUND -- `fields = '__all__'` |
| 4 | 인증 필요 엔드포인트의 인증 누락 | N/A -- 인증은 설정되어 있으나 DRF 방식 |
| 5 | 리스트 엔드포인트 페이지네이션 누락 | N/A -- 페이지네이션은 설정되어 있으나 DRF 방식 |
| 6 | 에러 처리 없음 / 비표준 에러 형식 | FOUND -- 에러 처리 없음 |
| 7 | async 적용 가능한 sync 뷰 | FOUND -- DB I/O가 있는 sync 뷰 |
| 8 | FilterSchema 미사용 | FOUND -- 필터링 로직 없음 |
| 9 | 요청 본문 Schema 검증 누락 | FOUND -- DRF Serializer에 의존 |
| 10 | 엔드포인트 과도한 책임 | OK -- 단일 책임 범위 내 |

---

## Summary

이 코드는 전체가 DRF(Django REST Framework) 패턴으로 작성되어 있으며, 프로젝트 컨벤션인 Django Ninja로의 전면 전환이 필요하다. Serializer를 Schema/ModelSchema로, ViewSet을 Router 데코레이터 패턴으로, permission_classes를 Ninja auth 클래스로, DRF Pagination을 `@paginate` 데코레이터로 각각 교체해야 한다. 추가로 `fields = '__all__'` 제거, 타입 힌트 추가, 에러 처리 도입이 필요하다.
