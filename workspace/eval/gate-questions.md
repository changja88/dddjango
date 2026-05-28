# 게이트 질문 비교 — codex vs claude

> 목적: 같은 입력(프롬프트·baseline) 위에서 **두 런타임이 게이트에서 무엇을·어떻게 묻는가**를 1:1 대조한다.
> 1차에서 관찰된 "claude=결정을 사용자 게이트로 노출 / codex=무언으로 최소 결정" 성향이 2차에도 재현되는지, 질문 자체의 깊이·선택지·권장안 차이를 본다.
> 채우는 법: 사용자가 각 세션의 게이트 출력을 붙여넣으면, 아래 해당 게이트에 **원문 그대로** 양쪽을 나눠 기록한다.

- **codex-3** = Codex CLI @ `dddjango-codex`
- **claude-2** = Claude Code @ `dddjango-claude`
- 고정 프롬프트: "재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API."

---

## G0 — 스코프 / 렌즈 / 배치

### codex-3

```
• dddjango  [✓ 스코프] → [· 설계 (ddd·api·db)] → [· 구현] → [· 마무리]

  ─────────────────────────────────────
  dddjango · G0 스코프 승인
  방금 끝낸 것 : .dddjango/stock-aware-order-api/scope.md에 기능 범위, 제외 범위, 기존 프로젝트 신호, 활성 lens를 정리했습니다.
  승인 대기   : 재고 충분 시 주문 생성+재고 차감, 부족 시 409 Conflict로 거절하는 API 범위와 설계 lens ddd·api·db 승인
  다음에 할 것 : 승인 후 design-architect와 lens 리뷰어를 서브에이전트로 실행해 설계 명세를 만듭니다.
  ─────────────────────────────────────

  이 기능을 둘 자리도 같이 골라주세요.

  1. 기존 catalog에 포함
  2. 새 독립 주문/판매 영역으로 분리
  3. 설계자가 결정

  승인하려면 "승인, 1"처럼 답해주세요. 고치려면 무엇을 바꿀지 적어주세요.
```

- 노출 게이트: G0에서 **스코프+렌즈+배치를 한 번에** 제시. 배치는 3지선다(기존 catalog / 신규 분리 / 설계자 결정).
- 렌즈: ddd·api·db 3개 모두 활성 제안.
- 응답 형식: `"승인, 1"`.

### claude-2

G0를 **2개의 연속 질문 배치**로 물음(사용자 확인). 탭: `G0 승인` · `배치` · `주문 형태`.

**질문 1 — G0 승인:**
```
←  ☐ G0 승인  ☐ 배치  ☐ 주문 형태  ✔ Submit  →

G0 스코프·lens를 승인하시겠습니까? (수정 요청 시 자유입력으로 알려주세요)

❯ 1. 승인
     스코프 메모와 활성 lens(ddd·api·db) 그대로 설계 단계로 진행
  2. lens 축소
     api 또는 db lens가 불필요하다고 보면 줄여서 진행 (어느 것을 뺄지 알려주세요)
  3. Type something.
  4. Chat about this
```

**질문 2 — 배치:**
```
←  ☒ G0 승인  ☐ 배치  ☐ 주문 형태  ✔ Submit  →

주문 기능(Order)을 어디에 둘까요? (재고는 기존 catalog.Product를 차감)

❯ 1. 새 독립 영역(orders 앱)으로 분리
     경계가 또렷하고 나중에 따로 키우기 쉬움. 단 orders↔catalog 연결 계층이 생김
  2. 기존 catalog 앱에 포함
     지금은 단순하나 주문과 카탈로그가 한 영역에 얽힘
  3. 모르겠다 — 설계자가 정함
     architect가 설계 단계에서 애그리거트 경계 근거로 배치 결정
  4. Type something.
  5. Chat about this
```

- 노출 게이트: G0를 **2회 연속 질문 배치**로 분리(승인·배치·주문 형태). codex가 한 메시지에 묶은 것과 대조 — claude는 각 결정을 개별 질문화.
- 렌즈: ddd·api·db 활성 제안 + **lens 축소 선택지** 명시.
- 배치 질문: codex와 같은 3지선다지만 **각 선택의 트레이드오프를 한 줄씩 설명**(독립=경계↑/연결계층, 포함=단순하나 얽힘, 설계자=애그리거트 경계 근거). codex는 선택지에 설명 없음.
**질문 3 — 주문 형태:**
```
←  ☒ G0 승인  ☒ 배치  ☐ 주문 형태  ✔ Submit  →

주문 계약 범위를 어떻게 할까요?

❯ 1. 단일 품목 주문
     주문 1건 = 상품 1개 + 수량. 가장 단순(YAGNI). 추후 복수 품목은 별도 확장
  2. 복수 품목(라인 아이템)
     주문 1건에 여러 상품. 더 현실적이나 부분 부족 처리·트랜잭션 복잡도 증가
  3. 설계자가 정함
     architect가 도메인 관점에서 판단
  4. Type something.
  5. Chat about this
```

- 응답 형식: 선택지 번호.
- **주문 형태 질문은 claude만 노출** — 단일 vs 복수 품목(라인 아이템) 트레이드오프(부분 부족·트랜잭션 복잡도)를 사용자에게 결정 위임. codex는 스코프 메모에 "단일 상품"으로 못박고 묻지 않음(무언 결정).

---

## API 프레임워크 게이트

### codex-3
_(붙여넣기 대기)_

### claude-2
_(붙여넣기 대기)_

---

## 테스트 러너 게이트

### codex-3
_(붙여넣기 대기)_

### claude-2
_(붙여넣기 대기)_

---

## G1 — 설계 승인

### claude-2

탭형 **세 질문**: `구조 배치` · `멱등성` · `G1 승인`.

**질문 1 — 구조 배치:**
```
←  ☐ 구조 배치  ☐ 멱등성  ☐ G1 승인  ✔ Submit  →

구조: 기존 평면 catalog/를 어떻게 배치할까요? (architect가 사용자 결정으로 올린 트레이드오프 8.1)

❯ 1. 옵션 B — 최소 변경 (추천)
     기존 Product/마이그레이션/테이블 그대로 두고 주문 코드만 의미군 폴더로 추가. 기능 범위에 비례, 데이터 이주 리스크 0. 단점: 표준 트리를 부분 적용해 평면 일부 잔존
  2. 옵션 A — 전면 표준 트리 이주
     houserules 표준 트리 전면 적용. 일관된 골격이나 기존 Product 데이터 테이블을 state-only로 이주해야 하고 마이그레이션 안전 검증 필수(테이블 재생성·유실 리스크 관리)
  3. Type something.
  4. Chat about this
```

- claude는 G1에서도 **구조 트리(§0 표준 트리 전면 vs 최소 변경) 결정을 사용자 게이트로 노출** + 추천안(옵션 B) + 마이그레이션 안전 리스크까지 명시. codex-3은 배너에 "catalog 영역 확장"으로 적고 묻지 않음.
**질문 2 — 멱등성:**
```
←  ☒ 구조 배치  ☐ 멱등성  ☐ G1 승인  ✔ Submit  →

멱등성: 중복 주문 방지(Idempotency-Key)를 이번에 도입할까요? (트레이드오프 8.2)

❯ 1. 옵션 A — 미도입 (추천)
     G0 스코프(오버셀 차단)만 충족. 오버셀은 조건부 UPDATE로 이미 차단됨. 단순성 우선. 네트워크 재시도 시 중복 주문 레코드는 허용 공백으로 남음
  2. 옵션 B — Idempotency-Key 도입
     중복 주문까지 방지. §2.7 계약(replay 201 snapshot, conflict 422, DB unique 저장) 구현. 스코프·저장소·계약 추가 비용
  3. Type something.
```

- 멱등성을 별도 탭으로 노출 + 추천(미도입, YAGNI) + 도입 시 비용까지 명시. codex-3은 멱등성 언급 없음.

**질문 3 — G1 승인:**
```
←  ☒ 구조 배치  ☒ 멱등성  ☐ G1 승인  ✔ Submit  →

위 결정과 함께 설계 명세를 승인하시겠습니까?

❯ 1. 승인
     선택한 트레이드오프 결정을 명세에 반영하고 구현(G2)으로 진행
  2. 수정 요청
     설계를 더 손봐야 함 — 무엇을 바꿀지 자유입력으로 알려주세요
  3. Type something.
  4. Chat about this
```

- claude G1 = **3탭(구조 배치·멱등성·승인)**. codex-3 G1 = 평문 배너 1개(승인/수정). claude는 두 설계 트레이드오프(트리·멱등성)를 사용자 결정으로 분리 노출 후 최종 승인을 받음.

### codex-3

```
• dddjango  [✓ 스코프] → [✓ 설계 (ddd·api·db)] → [· 구현] → [· 마무리]

  ─────────────────────────────────────
  dddjango · G1 설계 승인
  방금 끝낸 것 : .dddjango/stock-aware-order-api/design-spec.md에 최종 설계 명세를 작성했고, DDD/API/DB 리뷰 노트를 반영했습니다.
  승인 대기   : catalog 영역 확장, POST /api/orders/, 성공 201, 재고 부족 409, 상품 없음 404, 검증 실패 400, unsupported media type 415, 조건부 UPDATE 기반 재고 차감 설계 승인
  다음에 할 것 : 승인 후 acceptance-tester가 실패하는 인수 테스트를 먼저 작성하고, coder가 TDD로 구현합니다.
  ─────────────────────────────────────

  핵심 설계 결정은 다음입니다.

  1. ProductRepository.accept_stock(product_id, quantity)가 재고 수락 도메인 포트가 되고, 성공 시 AcceptedStock(product_id, accepted_quantity, unit_price)를 반환합니다.
  2. 주문 생성과 재고 차감은 CatalogUnitOfWork 하나의 트랜잭션 안에서 처리합니다.
  3. 동시성 방어는 stock >= quantity 조건부 UPDATE로 처리하고, 성공 후 같은 트랜잭션에서 가격을 캡처합니다.
  4. 에러는 Problem Details로 고정하고, unknown field는 400으로 거절합니다.
  5. 기존 catalog_product 테이블은 보존하고, 새 catalog_order 테이블을 추가합니다.

  미해결 트레이드오프는 없습니다.

  승인하려면 승인, 고치려면 무엇을 바꿀지 적어주세요.
```

- 형식: 평문 배너(G0와 동일). 승인/수정 자유응답.
- 설계 특징: `POST /api/orders/`·201·409·404·400·**415**, **조건부 UPDATE** 동시성, Problem Details, unknown field 400. → 1차 codex-2 패턴(`/api/orders/`·415) 재현.
- 포트: `accept_stock() → AcceptedStock(...)` **튜플성 반환**. → 1차 codex-2의 `reserve()→tuple` 누수 포트 패턴 재현(도메인 Product 반환이 아님). **B1 관련 주시 대상.**
- "미해결 트레이드오프 없음" 단언.

### claude-2
_(붙여넣기 대기)_

---

## G2 — 구현 승인

### claude-2

```
←  ☐ G2 승인  ✔ Submit  →

G2 구현을 어떻게 처리할까요? (복수 선택 가능 — 개선 항목을 고르면 해당 항목만 coder에 반영 후 재검증)

❯ 1. [ ] 그대로 승인 (개선 없이 통과)
  41 passed·check 클린 상태. 남은 지적은 비-blocker 품질 개선이므로 현행대로 마무리로 간다.
  2. [ ] I1: 리포지토리 통합 테스트 추가
  명세 §5.3이 요구한 test_product_repository.py 누락 보완(조건부 UPDATE·rowcount 404/409 분류·available 값을 실 DB로 검증).
  3. [ ] I3: busy_timeout/설정 정리
  settings OPTIONS.timeout과 테스트 PRAGMA의 이중 적용을 한 곳으로 일원화.
  4. [ ] I4+I5: 415 결합 단순화 + OpenAPI 스키마
  415를 Ninja 내부(__cause__) 우회 대신 진입 단계 Content-Type 검사로, 에러 problem+json 확장필드를 상태코드별 스키마로 분리(§2.8).
  5. [ ] Type something
  6. Chat about this
```

- 형식: 탭형 멀티선택. **규율 감사 비-blocker 지적을 사용자 선택 개선 항목으로 노출**(I1/I3/I4+I5) — 고르면 coder 재반영. codex-3는 같은 감사를 자동 반영 후 평문 배너 승인만 받음(개선 항목 노출 없음).
- 테스트 **41 passed**(codex-3는 18). check 클린.
- ⚠️ **통제 이탈 가능성**: I4에 "415를 **Ninja 내부(__cause__)** 우회"가 보임 → claude-2가 **Django Ninja**로 구현했을 가능성. 프로토콜 고정답은 plain Django. 프레임워크 게이트 답을 확인해야 함(meta.md 이탈 기록 대상). 단 핵심 세 신호(B1·stock≥0·race)는 프레임워크 무관이라 ddd/db 비교는 유효.

### codex-3

```
dddjango  [✓ 스코프] → [✓ 설계 (ddd·api·db)] → [✓ 구현] → [· 마무리]

  ─────────────────────────────────────
  dddjango · G2 구현 승인
  방금 끝낸 것 : 인수 테스트 Red → 구현 Green → 규율 감사 → 지적 반영 → 최종 검증까지 완료했습니다.
  승인 대기   : 구현 결과 승인
  다음에 할 것 : 승인 후 최종 마무리·검증 보고를 정리합니다.
  ─────────────────────────────────────

  구현 요약입니다.
  - POST /api/orders/ 추가
  - 재고 충분: 201, catalog_order 생성, catalog_product.stock 차감
  - 재고 부족: 409 application/problem+json, 주문 미생성, 재고 유지
  - 상품 없음 404, 검증 실패 400, non-JSON 요청 415
  - 조건부 UPDATE stock = stock - quantity WHERE stock >= quantity로 oversell 방지
  - CatalogUnitOfWork.commit() 호출 없이는 rollback되도록 정리
  - 기존 catalog.models.Product는 새 ProductModel 호환 shim으로 정리
  - Order 엔티티는 명세대로 domain_layer/order/entity/order.py에 배치

  검증 결과:
  - python3 manage.py test → Ran 18 tests ... OK
  - python3 manage.py check → no issues
  - makemigrations --check --dry-run → No changes detected
  - migrate --plan → No planned migration operations
  - shell: catalog.models.Product.__name__ → ProductModel
  - compileall application config catalog → passed

  규율 감사: 최초 important findings 3건과 타입 권고 1건을 반영했고, 재감사에서 남은 구조 배치 지적도 반영했습니다.

  승인하려면 승인, 고치려면 무엇을 바꿀지 적어주세요.
```

- 형식: 평문 배너(승인/수정).
- 테스트 18개(codex-2는 15). 409(부족)·415·400·404. 503 언급 없음(codex-2의 503/sqlite 문자열 결합과 대조 — 개선 가능성).
- **규율 감사 활발**: important 3건 + 타입 권고 1건 반영 + 재감사 구조배치 지적 반영. → 1차 codex-2가 B1·stock≥0를 놓친 것과 다른 양상일 수 있음. **그 3건이 B1·stock≥0를 포함했는지가 결정성 판정 핵심** — 캡처 후 코드/감사노트에서 확인.
- `Product` → `ProductModel` 호환 shim. accept_stock→AcceptedStock 튜플 포트(G1) 유지 여부 확인 대상.

### claude-2
_(붙여넣기 대기)_

---

## 요약 대조 (모든 게이트 채운 뒤 작성)

| 축 | codex-3 | claude-2 |
|---|---|---|
| 노출한 게이트 수 | ? | ? |
| 무언 결정(질문 없이 진행)한 지점 | ? | ? |
| 선택지·권장안 제시 방식 | ? | ? |
| 질문이 드러낸 설계 의식 깊이 | ? | ? |
