# 검증 보고 — 주문 생성 API (재고 검증·차감)

> Phase 3 마무리. **실제 실행한 검증만** 기재한다. 미실행 항목은 사유를 명시한다.
> 작성: 2026-05-29 (Coordinator 직접 실행 결과 기준).

## 기능 요약
`POST /api/orders` — 상품+수량을 받아 재고 충분 시 차감 후 주문 생성(201), 부족 시 거절(409). 동시 주문에도 oversell 0.
- 배치: 새 `ordering` 앱(별개 BC). catalog `Product`에 `version`+`deduct_stock(qty)` 추가(OD-1 승인).
- 어댑터: Django Ninja 1.6.2(신규 도입). 에러는 RFC 9457 `application/problem+json`.
- 동시성: 응용 서비스 트랜잭션 경계 + 낙관적 version CAS 조건부 UPDATE(0행→fresh 재조회→도메인 재실행, 각 시도=독립 atomic·retry는 트랜잭션 밖). 충분성 판정은 catalog `deduct_stock` 소유(SQL에 미복제). SQLite `busy_timeout=5000`/IMMEDIATE.

## 실행한 검증 (증거)

### 1. 테스트 스위트 — 통과
- 커맨드: `.venv/bin/python manage.py test application.ordering catalog`
- 결과: **Found 43 test(s) … OK (skipped=1)**. 0.230s.
- 덮은 외부 행위(인수, 블랙박스 HTTP): 201 성공+재고차감 / 409 부족+상태불변(requested 에코) / 404 없는 상품 / 422 검증(quantity<1·필수누락·타입오류, errors[]) / 400 malformed JSON / 415 미지원 Content-Type / 동시성 oversell 0.
- 단위·통합(코더 내부 루프): 도메인(Order·Quantity)·응용(트랜잭션·retry 경계)·ACL 번역·리포지토리·problem_detail 변환·503 매핑.

### 2. 동시성 oversell 0 — 비결정(flaky) 없음
- 커맨드: `.venv/bin/python manage.py test …OversellPreventionTest` ×3 (Coordinator 직접) + 코더 13회.
- 결과: **3/3 OK**(추가로 코더 13/13). 동시 20요청·재고 5 → 정확히 5건 201·나머지 409/503·최종 재고 0.

### 3. 503 경합 소진 — 결정론 통과
- `test_place_order_contention`: 재시도 상한 소진 시 503 + `Retry-After` + 원자성(주문 0건·재고 불변), 409와 의미 분리. 결정론적 Green.

### 4. manage.py check — 이슈 없음
- 커맨드: `.venv/bin/python manage.py check`
- 결과: **System check identified no issues (0 silenced).**

### 5. 마이그레이션 — 누락 없음
- 커맨드: `.venv/bin/python manage.py makemigrations --check --dry-run`
- 결과: **No changes detected.** (catalog `0002_product_version` Expand + ordering `0001_initial` 적용 상태와 모델 일치.)

### 6. 하우스룰(구조·타입·주석) 점검 — 위반 0건
- discipline-reviewer 홀리스틱 감사 결과. 표준 파일트리 §0 불변식 6개 전부 충족, 4계층 `_layer` 분리·명명 규약(OrderModel/Order, OrderRepository/DjangoOrderRepository, ProductStockPort/DjangoProductStockPort)·ACL 격리(catalog import는 `catalog_acl.py`에만)·프로덕션 시그니처 타입 전수·한국어 주석 일관. must-fix 0.

## 미실행 항목 (사유 명시)
- **mypy strict**: 프로젝트에 타입 체커·`pyproject.toml`/`mypy.ini` 구성이 **없음** → 실행하지 않음. 프로덕션 시그니처 타입은 전수 작성됨(정적 검증기는 미구성이라 자동 확인 불가).
- **ruff/린터**: 동일하게 미구성 → 미실행.

## 의도적 skip 1건 (정직 기재)
- `StockContentionExhaustionTest`(인수 스켈레톤): 블랙박스 HTTP로 내부 재시도 타이밍을 결정론적으로 강제 불가 → `@unittest.skip` 유지. 동일 행위(503·Retry-After·원자성)는 코더 소유 통합 테스트 `test_place_order_contention`이 결정론적으로 대체 검증함.

## 후속 후보 (G2에서 미반영 승인된 nice-to-fix)
1. 415 분기가 Ninja `HttpError(400)` 도달에 결합 — 견고성 개선 여지(현재 계약은 Green).
2. CAS 0행 경합(`StockUpdateConflict`)의 catalog 결정론적 단위 테스트 부재(통합 동시성 테스트로만 커버).
3. skip 스켈레톤 정리(제거/docstring), `assert order.id` → 명시 예외(`python -O` 안전).
4. 계약 노출(수용됨): 멱등키 미도입(OD-2)으로 재시도성 중복 주문 가능. OpenAPI 문서의 에러 미디어타입 표기는 Ninja 1.6 한계(런타임은 `problem+json` 정확).
