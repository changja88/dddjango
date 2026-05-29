# 게이트 질문 기록 — Round 3 (B1-fix 검증 · codex vs claude)

> 목적: **B1 일반화 표준 편집 이후** 같은 입력 위에서 두 런타임이 게이트에서 무엇을·어떻게 묻는가를 1:1 대조한다.
> 관찰 축: (1) 1차/2차의 "claude=결정을 사용자 게이트로 노출 / codex=무언 최소 결정" 성향 재현 여부, (2) **편집된 B1 표준이 설계 단계 질문에 드러나는가**(판정 소유·경합 가드/판정 분리), (3) 질문 깊이·선택지·권장안 차이.
> 채우는 법: 사용자가 각 세션의 게이트 출력(질문 원문)을 붙여넣으면, 아래 해당 게이트에 **원문 그대로** 양쪽을 나눠 기록한다.

- **claude-3** = Claude Code `/dddjango` @ `~/Desktop/dddjango-claude-index`
- **codex-4** = Codex CLI `dddjango` 스킬 @ `~/Desktop/dddjango-codex-index`
- 두 타깃은 `dddjango-smoke-sample` 에서 `git clone` 한 **바이트 동일** 복제(추적 코드 동일 해시·시드 동일). 입력은 각 폴더 `PROMPT.md`(= 고정 프롬프트 + 고정 게이트 답).
- 고정 프롬프트: `재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.`
- 고정 게이트 답(PROMPT.md §2): G0 배치=**① 새 독립 영역** · 렌즈=ddd+db+api · 스코프=제안대로 · plain Django · Django test · G1/G2 무수정 승인 · thinking OFF.
- ⚠️ 캐시: 표준 12파일 편집본은 **미커밋** 상태 → 풀런 전 **플러그인 캐시 동기화·검증 필요**(DEVLOG §4 "플러그인 캐시 신선도").

---

## G0 — 스코프 / 렌즈 / 배치

### claude-3

> 멀티 서브게이트 UI: `☐ 배치 ☐ 주문 단위 ☐ 인증 ☐ G0 승인`

**[G0-a 배치]** (원문)

> 주문 생성 기능(주문 애그리거트)을 어디에 둘까요? 설계 영역 경계가 여기서 갈립니다.
> 1. **새 ordering 앱으로 분리** — 주문을 독립 영역(새 앱)으로 둡니다. 경계가 또렷하고 나중에 따로 키우기 쉽지만, 주문↔catalog(재고) 사이 연결 계층이 생깁니다.
> 2. 기존 catalog에 포함 — 주문을 catalog 앱 안에 둡니다. 지금은 단순하지만 상품 카탈로그와 주문 책임이 한 영역에 얽힙니다.
> 3. 설계자가 결정 — design-architect가 애그리거트 경계·연결 계층 필요 여부를 따져 설계 단계에서 정합니다.
> 4. Type something.

**→ 답: `1` (새 ordering 앱으로 분리)** = ① 새 독립 영역.

**[G0-b 주문 단위]** (원문)

> 한 번의 주문 요청에 담는 상품 단위는?
> 1. **단일 상품 + 수량** — 한 주문 = 상품 1개 + 수량. 현재 요구를 만족하는 가장 단순한 형태(권장).
> 2. 다중 라인아이템 — 한 주문에 여러 상품을 담습니다. 주문-주문항목 구조가 필요하고 부분 재고부족 처리 규칙이 추가됩니다.
> 3. Type something.

**→ 답: `1` (단일 상품 + 수량)** = 스코프 제안대로.

**[G0-c 인증]** (원문)

> 이번 범위에서 인증·사용자 연결은?
> 1. **이번 범위 제외(익명)** — 인증 없이 주문 생성. 주문에 사용자 소유자 개념을 넣지 않습니다(권장, 범위 최소화).
> 2. 로그인 사용자 필요 — 인증된 사용자만 주문 가능하고 주문에 소유자(user)를 기록합니다.
> 3. Type something.

**→ 답: `1` (이번 범위 제외/익명)** = 인증 범위 밖(최소 스코프).
> 비교 메모: 이 "인증" 축은 **클로드만 명시적으로 게이트로 노출**(코덱스 G0는 단일 승인으로 통합·미노출). DR-14의 "claude가 결정을 ~3배 더 노출" 성향 재현.

**[G0-d G0 승인]** (원문)

> 위 선택과 스코프·lens(ddd·api·db)대로 설계(G1)로 진행할까요?
> 1. **승인 — 설계로 진행** — 스코프 메모와 활성 lens를 확정하고 design-architect를 호출합니다.
> 2. 수정 요청 — 스코프·범위·lens를 더 손봅니다.
> 3. Type something.

**→ 답: `1` (승인 — 설계로 진행)** = 무수정 승인.

---
**클로드 G0 종합**: 4개 서브게이트(배치·주문단위·인증·G0승인)로 분할 노출. 답 = 새 ordering 앱 / 단일 상품+수량 / 익명 / 승인. **코덱스 G0(단일 통합 승인)와 결정 내용은 동일하나 노출 입도가 4:1.**

### codex-4

**[G0 스코프 승인]** (원문)

> dddjango · G0 스코프 승인
> 방금 끝낸 것 : 프로젝트 구조를 확인했고, G0 스코프 메모를 작성했습니다: `.dddjango/order-stock-api/scope.md`
> 승인 대기 : 단일 상품·수량 주문 API, 재고 충분 시 주문 생성+재고 차감, 재고 부족 시 409 거절+상태 변경 없음
> 다음에 할 것 : 승인되면 dddjango 설계 단계로 넘어가 architect와 ddd/api/db 리뷰어를 실행합니다
>
> 제안 lens는 ddd + api + db입니다. 배치는 PROMPT.md의 고정 게이트 답에 맞춰 ① 새 독립 영역, 즉 별도 orders 앱으로 제안했습니다. API는 plain Django JsonResponse, 테스트는 Django 기본 test runner로 둡니다.
>
> 승인하려면 "승인", 고치려면 무엇을 바꿀지 적어주세요.
>
> Serena: 도구가 이 세션에 노출되지 않아 사용하지 못했고, rg/파일 읽기로 구조를 확인했습니다.

**→ 답: `승인`** (배치·lens·스택·스코프 전부 고정 답과 일치, 무수정).

관찰: G0의 **모든 결정(스코프+lens+배치+프레임워크+러너)을 단일 승인 게이트로 통합**해 제시. PROMPT.md를 **선제적으로 읽어** 고정 답에 맞춰 제안(배치 ①을 자발적으로 정렬). Serena 미노출 → rg/파일읽기 폴백 보고.

---

## G1 — 설계 승인 (판정 소유·동시성 분리가 질문/명세에 드러나는가)

### claude-3

> 멀티 서브게이트 UI: `☐ OD-1 catalog ☐ OD-2 멱등성 ☐ OD-3 FK ☐ G1 승인`

**[G1-OD1 catalog 변경 — 판정 소유]** (원문)

> OD-1: oversell(재고 초과 차감)을 동시성 하에서 막으려면 재고 판정 소유자인 catalog에 손을 대야 합니다. catalog 변경을 승인하시겠어요? (리뷰 3lens가 이 선택으로 수렴)
> 1. **옵션 A — 승인(권장)** — catalog Product에 version 컬럼 + `deduct_stock(qty)` 도메인 동작 추가. 재고 판정이 소유자(catalog)에 머물러 BC 경계·빈혈모델 회피, SQLite/Postgres 무관 정합성 만족. 단 catalog 무변경 스코프 소폭 확장.
> 2. 옵션 B — A + Postgres select_for_update 보강 — 고경합 처리량은 나으나 SQLite는 no-op이라 개발/테스트는 여전히 A 경로 의존(이중 경로 복잡도).
> 3. Type something.

**→ 답: `1` (옵션 A)** = 판정을 소유자 도메인(`deduct_stock`)에 두고 version/CAS 단일 경로.

**🔬 B1 핵심**: 클로드는 **"재고 판정 소유자 catalog에 `deduct_stock()` 추가 → 빈혈모델 회피"**를 **사용자 게이트로 직접 노출**(코덱스는 명세에 무언 반영). 옵션 텍스트에 "빈혈모델 회피"가 명문 등장 = 편집 B1 표준 발현. DR-14 claude-2가 `deduct_stock()`를 **미배선(죽은코드)**으로 둔 것과 대비 — 이번엔 설계가 "소유자에 머물러"를 명시. **배선 여부는 G2/grep에서 확정.**

**[G1-OD2 멱등성]** (원문)

> OD-2: 주문 생성 멱등성 키(Idempotency-Key) 도입 여부? 동시성 가드는 같은 의도의 재시도로 인한 중복 주문은 못 막습니다.
> 1. **미도입(권장)** — 이번 스코프 고수. 네트워크 재시도 중복 주문 계약 노출이 잔존함을 수용. 명세에 명시 기록.
> 2. 도입 — Idempotency-Key로 중복 주문 차단. 키 저장소·replay/conflict 계약 추가 비용.
> 3. Type something.

**→ 답: `1` (미도입)** = 스코프 확장 금지(코덱스도 미도입, 일관).
> 비교 메모: 멱등성 축도 **클로드만 게이트로 노출**(코덱스 미노출). 노출철학 대조 누적.

**[G1-OD3 FK]** (원문)

> OD-3: 주문의 product_id를 DB 외래키(FK)로 둘까요?
> 1. **FK 미설정 + 인덱스 없음(권장)** — 정수 컬럼만. 두 BC를 DB 레벨에서 분리, 주문은 product_id+가격 스냅샷으로 자기완결(orphan 무해). 조회 후속 시 인덱스 추가.
> 2. DB FK 설정 — 참조 무결성을 DB가 보장하나 ordering↔catalog 두 BC를 DB 레벨에서 결합(독립성 약화).
> 3. Type something.

**→ 답: `1` (FK 미설정, 권장)** = 클로드 architect 권장 따름.

**⚠️ 설계 분기(DIVERGENCE)**: FK 정책에서 두 런타임 갈림 — **코덱스 = `catalog.Product` FK+PROTECT**(참조무결성·실용), **클로드 = FK 미설정**(BC를 DB레벨까지 순수 분리·주문 자기완결). 둘 다 정당한 DDD 선택. **FK는 고정 축 아님 → architect 변동으로 수용·기록**(DR-14 원칙: 변동 억압 안 함). B1(판정 소유)과 직교라 핵심 비교 불변. 비교 리포트에 "설계철학 차이: 클로드 BC-순수 / 코덱스 무결성-실용"으로 적을 것.

**[G1 승인]** (원문)

> 위 결정과 최종 설계 명세대로 구현(G2)으로 진행할까요?
> 1. **승인 — 구현으로** — 명세를 단일 근거로 acceptance-tester·coder를 호출해 이중 루프 TDD 시작.
> 2. 수정 요청 · 3. Type something.

**→ 답: `1` (승인)** = 무수정 승인.

**🔬 B1 판정 — 클로드 설계 단계 CLEAN (코덱스보다 더 명시적)** (명세 `create-order/design-spec.md` 351줄 정독):
- **L75**: `stock>=qty` 판정 = catalog 도메인 동작 `Product.deduct_stock(qty)` 소유 + **"그 동작 안에서 production 경로에 내린다"** — DR-14 claude-2 죽은코드 정면 차단(프로덕션 호출 명시).
- **L173**: 흐름 "조회 → `Order.place()` → ACL 포트로 차감 위임(catalog 도메인 판정) → 영속화" = **빈혈 차단 순서 §3.2** 인용, 배선이 흐름에 박힘.
- **L76·77·185·189**: WHERE엔 version 경합가드만, `stock>=qty` 복제 금지, CAS 0행=재시도 트리거(판정 대체 아님), Rule ownership=catalog 도메인 — **§9.5·§9.6·§3.2 인용**.
- **L186·187**: `stock>=0`/PositiveInteger CHECK는 불변식 백스톱(판정 아님), IntegrityError는 "version CAS 누락 신호"로 로깅·경합 재시도와 분리.
- 인프라 판정 누수 패턴 grep = **0**(L76 금지 서술·CHECK 백스톱 외 없음).
- **잔여 확인(G2)**: 명세는 "프로덕션 호출" 명시 → 코더가 따르면 배선됨. *실제 배선/누수 없음*은 G2 산출 grep·discipline에서 확정.

---
**🔱 G1 설계 분기 종합(코덱스 vs 클로드)** — 둘 다 B1 CLEAN·낙관적 version CAS·`stock>=0` 백스톱·BC 분리(orders/ordering 신규앱). 차이:
| 축 | 코덱스 | 클로드 |
|---|---|---|
| 경합 소진 | 409 `/inventory-conflict` 수렴 | **503+Retry-After** `/stock-contention` (409 out-of-stock과 의미 분리) |
| 재시도 상한 | 1회 | **3회** |
| product FK | FK+PROTECT | **FK 미설정**(BC-순수) |
| SQLite 직렬화 | 1회 재시도 | **busy_timeout 5s + BEGIN IMMEDIATE**(명세가 메커니즘 소유=DR-06 준수) |
| 게이트 노출 | G1 단일 승인 | **OD-1/2/3 + 승인 4분할**(판정소유·멱등성·FK 결정을 각각 사용자에게) |
- 종합: **노출철학(클로드>코덱스)·오류 분류 풍부함(클로드 503 분리·멱등성 갭 정직 기재)이 1·2차와 동일하게 재현.** 코드 우열은 G2 산출로 판정.

### codex-4

**[G1 설계 승인]** (원문)

> dddjango · G1 설계 승인
> 방금 끝낸 것 : architect 설계 초안 작성, ddd/api/db 독립 리뷰, 리뷰 노트 반영·중재까지 완료.
> 승인 대기 : 최종 설계 명세 `.dddjango/order-stock-api/design-spec.md`
> 다음에 할 것 : 승인되면 인수 테스트 작성 → 구현 슬라이스 TDD → 규율 감사.
>
> 요약:
> - 새 orders 앱/BC에 `POST /api/orders/` 추가, plain Django JsonResponse.
> - 성공 201 / 재고부족 409 `/problems/insufficient-stock` / 동시성충돌 409 `/problems/inventory-conflict`.
> - `OrderModel.product` = `catalog.Product` FK + PROTECT, 도메인 내부는 `product_id`만 다루는 경계.
> - SQLite lock 오류는 1회 재시도 후 409로 수렴, **`Product.version` 기반 재고 writer 계약** 명시.
> - 미해결 트레이드오프: 직접 DB/admin 재고 수정 시 version 미증가하면 CAS 보장 밖 → "application stock writer는 모두 version 갱신" 계약으로 고정.
> Serena: 미노출 → 각 역할이 rg/파일읽기.

**→ 답: `승인`** (무수정).

**🔬 B1 판정 — 설계 단계 CLEAN** (명세 `design-spec.md` 364줄 정독):
- **L217**: `WHERE` 절은 identity·version 경합 가드만, `stock >= quantity` 비즈니스 판정 복제 금지 명시.
- **L234**: "도메인이 비즈니스 판정 소유, DB는 충돌/백스톱 제약만" + **`architecture-ddd §3.2`·§3.6 인용**(편집한 B1 원칙의 집).
- **L88**: 재시도 후 부족 시 도메인 `InsufficientStock` outcome 반환(판정=도메인).
- **L20·78·79**: 스냅샷은 "the stock view used by **the domain decision**", port decrement은 version으로만.
- **L215~216**: 낙관적 CAS(`stock=stock-qty, version=version+1`), version 가드.
- **L199·219·231·241**: `stock >= 0`은 CHECK 백스톱(불변식)으로 판정과 분리(우리 강조 구분 일치).
- 인프라 판정 누수 패턴(`stock__gte`/`filter(stock` 등) grep = **0**(L217의 금지 서술 외 없음).
- **잔여 확인(G2)**: 명세가 "도메인 소유"라 해도 *코드가 실제 도메인 판정 메서드를 프로덕션에서 호출*하는지는 구현/grep/discipline에서 최종 검증.

---

## G2 — 구현 승인

### claude-3

**[G2 구현 승인]** (원문)

> G2 구현이 검증을 모두 통과했고(oversell 0·13회 반복·전체 Green·하우스룰 0위반·must-fix 0) 마무리로 진행합니다. 추가 nice-to-fix? (첫 항목만 고르면 무수정 승인)
> 1. **이대로 승인(권장)**
> 2. ① 415 분기 견고화 (415가 **Ninja**의 HttpError(400) 도달 의존 → 미디어타입 선제 게이트)
> 3. ② CAS 0행 단위테스트 (version 불일치 0행→StockUpdateConflict 결정론 단위테스트 고정)
> 4. ③④ 스켈레톤 정리 + place_order_app `assert order.id`를 명시 예외로(`python -O` 안전)
> 5. Type something

**→ 답: `1` (이대로 승인)** = must-fix 0·B1 clean·테스트 green, nice-to-fix는 후속.

**🎯 B1 판정 — 코드 레벨 CLEAN (정독+grep 확정)**:
- **판정 소유**: `catalog/models.py:24` `Product.deduct_stock` — `if self.stock < quantity: raise InsufficientStock`(판정이 재고 소유자 catalog 도메인 메서드 안).
- **프로덕션 호출**: `application/ordering/infra_layer/acl/catalog_acl.py:30` `product.deduct_stock(quantity)` → `place_order_app`(bounded retry 3, 매 시도 fresh 재조회 후 도메인부터 재실행) — **죽은코드 아님. DR-14 claude-2 미배선 결함 정반대로 수정**.
- **인프라 누수 0**: ordering 인프라의 `stock>=qty` 매치는 전부 "복제하지 않는다" 주석/docstring(`product_stock_port.py:8`·`catalog_acl.py:7-8`). 실제 SQL 누수 grep = **0**.
- **CAS**: `Product.deduct_stock`의 `filter(pk=, version=).update(stock=F-q, version=F+1)` = version 경합가드만, `updated==0 → StockUpdateConflict`(재시도 트리거).
- **백스톱**: `version` 컬럼 + `stock>=0`(PositiveInteger) CHECK.
- **DR-06**: `config/db_backends/sqlite_serialized/`(busy_timeout 5s + BEGIN IMMEDIATE)는 **명세 §3.3이 지정한 메커니즘을 코더가 구현**(spec-directed, 토끼굴 아님 — 명세 L188 "값·모드는 명세가 결정").

**⚠️ 통제 이탈(프레임워크)**: 클로드가 **plain Django 아닌 django-ninja 1.6.2** 사용(requirements에 추가). 프레임워크 게이트를 클로드가 안 물어 고정 답 적용 기회 없음 = **DR-14 재현**. → 코드 비교는 "프레임워크 무관 신호"만 유효(B1은 무관하므로 유효). **방법론 교훈: Claude 프레임워크 통제는 게이트 답이 아니라 *프롬프트 본문*에 박아야 함**(Claude가 안 게이팅).

**🔱 G2 코드 분기(코덱스 vs 클로드)** — 둘 다 B1 CLEAN. 차이: 프레임워크(코덱스 plain Django / **클로드 ninja**), 동시성 메커니즘(코덱스 select_for_update+CAS+retry1 / **클로드 커스텀 sqlite 백엔드 BEGIN IMMEDIATE + CAS + retry3**), 경합소진(코덱스 409 / 클로드 503), 판정 소유 BC(코덱스 orders도메인 / 클로드 catalog.Product). 테스트수 비교 불가(프레임워크 상이).

### codex-4

**[G2 구현 승인]** (원문)

> dddjango · G2 구현 승인
> 방금 끝낸 것 : 인수 테스트 Red 작성, orders 앱/API 구현, important 감사 지적 반영, 재감사까지 완료.
> 승인 대기 : 구현 결과와 남은 nit 2건 처리 여부
> 구현 요약: 새 `application/orders` BC + `POST /api/orders/`. 충분 시 201+stock 차감+version 증가. 부족 409 `/insufficient-stock`, conflict 409 `/inventory-conflict`. `OrderModel.product`=catalog.Product FK+PROTECT; `Product.stock>=0`·`quantity>0`·`status IN ('created')` 제약. broad OperationalError를 SQLite lock 계열만 inventory conflict로 좁힘.
> 검증: unit 9 OK · integration 7 OK · 전체 16 OK · `makemigrations --check` clean · `check` clean.
> 남은 nit: (1) test helper 타입 시그니처 보강(권장 nit) (2) 입력검증이 schema_in.py 아닌 view helper에 남음(plain Django 허용 단순화).
> Serena: 미노출 → 기본 검색/파일읽기/테스트.

**→ 답: `승인`** (무수정; nit 2건 경미·동작 무결).

**🎯 B1 판정 — 코드 레벨 CLEAN (정독+grep 확정)**:
- **판정 소유**: `domain_layer/order/order.py:28` `Order.create()`가 `if quantity > snapshot.available_stock: raise InsufficientStock` — 판정이 **도메인 엔티티 안**.
- **프로덕션 호출**: `application_layer/create_order/command/create_order_app.py:51` `_execute_once`가 `Order.create(...)` 호출(트랜잭션 안) — **죽은코드 아님**(DR-13 codex-2 `Product.reserve()` 빈혈 결함 부재).
- **인프라 누수 0**: ACL `infra_layer/acl/catalog_acl.py:33-45` `decrement_stock`의 `filter(pk=, version=)` = **version 경합가드만**, `stock>=qty` 복제 없음. `update(stock=F("stock")-qty, version=F("version")+1)`는 SET(차감 write)이지 판정 아님(grep L38 false positive). `updated_count!=1 → InventoryConflict`(재시도 트리거).
- **백스톱**: catalog `Product` `version` 컬럼 + `stock>=0` CHECK(불변식, 판정 아님).
- 소유 배치: 코덱스는 **orders 도메인이 스냅샷 대비 판정**(catalog엔 version+CHECK만, 도메인 메서드 무), 클로드는 catalog.Product `deduct_stock`. 둘 다 B1-clean, 소유 BC만 다른 정당한 분기.
- **결론**: 편집 표준이 코덱스에서 설계→코드 끝까지 B1 차단. **N=1.**

**✅ codex-4 런 종료**(2026-05-29). 독립 검증(메인이 직접 실행): `manage.py check` clean · `manage.py test` **16 OK**(보고와 일치). 산출물 `workspace/eval/runs/codex-4/` 보존(application 56파일, .venv/.git/db 제외). 변경 파일: `catalog/models.py`(version+CHECK)·`catalog/migrations/0002`·`config/{settings,urls}.py`·신규 `application/orders/` 전체. 남은 리스크(설계 고정): 외부 writer가 version 미증가 시 CAS 밖, SQLite lock 매핑은 "database is locked" 메시지 의존.

---

## 관찰 메모 (런 중/후 기록)

**런 종료(2026-05-29) — codex-4 + claude-3 동시 수행 완료.** 비교 리포트 `comparison-3.html`.

1. **B1 차단 = 양쪽 CLEAN(핵심 성과).** 편집 표준(architecture-ddd §3.2 단일출처 + design-review-ddd/discipline-reviewer 2층 탐지)이 두 런타임 설계·코드 끝까지 작동. DR-13 codex-2 빈혈·DR-14 claude-2 죽은코드 **둘 다 부재**. 각 N=1(통계 아님, 발화·작동 sanity).
2. **게이트 노출철학 ≈ 9:3 재현.** 클로드 G0 4분할(배치·주문단위·인증·승인)+G1 4분할(OD-1판정소유·멱등성·FK·승인)+G2 / 코덱스 G0·G1·G2 각 단일. 1·2차 성향 재현, 더 또렷.
3. **통제 이탈 = claude django-ninja**(plain Django 고정답 어김; 프레임워크 게이트 미노출 → 강제 불가, DR-14 재현). 사용자 결정 **"이대로 수락"**. 프레임워크-의존 코드·테스트수(16 vs 43) 비교 무효, B1·판정소유·동시성철학·노출철학은 유효.
4. **설계 분기**(둘 다 정당): 판정소유 BC(코덱스 orders도메인 / 클로드 catalog.Product) · 동시성(코덱스 SFU+retry1 / 클로드 BEGIN IMMEDIATE백엔드+retry3) · 경합소진(409 / 503+Retry-After) · FK(PROTECT / 미설정).
5. **독립 검증**(메인 직접 실행): codex-4 16 OK·check clean / claude-3 43 OK(skip1)·check clean. 양쪽 oversell 0·migration 정합·하우스룰 0위반. 산출물 `runs/{codex-4,claude-3}/` 보존.
6. **방법론 교훈**: Claude 프레임워크 통제는 게이트 답이 아니라 **프롬프트 본문**에 박아야 함(Claude가 안 게이팅). `PROMPT.md` 프레임워크 항목을 게이트표→프롬프트 본문으로 올릴 것.

7. **discipline-reviewer 발화 테스트(B2 메커니즘 검증, 2026-05-29)** — 편집된 리뷰어 3회 독립 실행: **2 clear + 1 fire.**
   - **fire**: 중립 B1-양성 픽스처 `workspace/design/b1-firetest/`(도메인 `Product.deduct` 죽은코드 + repo `filter(stock__gte=qty).update`)에 **[blocker] "비즈니스 판정 인프라 누수 + 죽은 도메인 메서드"** 정확 발화. 인용 앵커 = `architecture-ddd §3.2` + `discipline-cleancode §15.1·§8.1/§8.5·§9.1`(B2 편집이 박은 그 앵커), 레인 준수("쿼리 정확성 아님").
   - **clear codex-4**: blocker 0, B1 명시 클린(판정=`Order.create` 도메인·인프라 누수 없음). 별건 important 1 = quantity 양의정수 판정이 presentation+`Quantity` VO 이중→`InvalidQuantity` 죽은 분기(B1 사촌격 DRY).
   - **clear claude-3**: blocker 0, B1 명시 클린(판정=`Product.deduct_stock` 단일소유). 별건 important 2 = 테스트 결합(private 몽키패치·DB-bound 단위테스트).
   - **결론: B2 탐지 메커니즘 작동 확정** — 누수엔 발화, 깨끗한 코드엔 B1 오탐 0이면서 *다른* 진짜 결함은 잡음(고무도장 아님·판별력 있음). 중간 확신 달성. (여전히 생성 N=1, 빈도통계는 N≥5 별도.)
