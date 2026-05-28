# claude-2 분석 (2차 결정성 런)

> 대상: `/Users/hyun/Desktop/dddjango-claude/` → 캡처 `runs/claude-2/`. Claude Code, dddjango Claude 플러그인.
> 프롬프트·baseline·배치(catalog)는 통제 일치. **단 프레임워크/러너/구조는 1차와 이탈**(아래 한계).

## ⚠️ 통제 이탈 (2차는 1차만큼 깨끗하지 않음)

| 축 | claude-1(1차) | claude-2(2차) | codex-3(2차) |
|---|---|---|---|
| 프레임워크 | plain Django (강제) | **Ninja** | plain Django |
| 테스트 러너 | Django test (강제) | **pytest** | Django test |
| 구조 | 완전 §0 4계층 | **평면 최소(옵션 B)** `catalog/{api,application,domain,repositories}` | 완전 §0 4계층 |

→ claude-2는 프레임워크/러너 게이트가 이번 런엔 노출되지 않아 **claude 기본 추천 스택(Ninja+pytest)**으로 진행됐고, 구조는 G1에서 "옵션 B 최소 변경"을 골라(프로토콜 "최소 변경" 매핑) 평면 구조가 됐다. **구조/프레임워크/테스트수 비교는 통제 불가** → 프레임워크 무관 신호(B1·stock≥0·race)만 유효 비교.

## 세 신호 판정

### 신호 1 — B1 (도메인 차감 규칙 소유) → ❌ **재현 (1차 claude-1과 반대!)**

- 도메인 `catalog/domain/product.py`에 `Product.deduct_stock(quantity)` **존재**. 그러나 호출처는 **단위 테스트뿐**(`tests/unit/test_product_deduct_stock.py` 5곳). 프로덕션 `application/create_order.py:24`는 **리포지토리** `product_repository.deduct_stock()`(infra 조건부 UPDATE)를 호출 — 도메인 메서드 미경유. 리포는 UPDATE 후 `DomainProduct` 스냅샷만 생성(도메인 `deduct_stock()` 호출 안 함).
- docstring 명시적 합리화: "deduct_stock 역할은 가드(quantity≥1)+상태동기화로 **축소 재정의**… 동시성 정확성 판정 권위는 **인프라 조건부 UPDATE에 있다**."
- **1차 claude-1**: `find_by_id`로 도메인 Product 로드 → `product.deduct()` **프로덕션 호출**(권위) + UPDATE 안전망 = "이중 방어선". 죽은 코드 아님.
- **2차 claude-2**: 도메인 메서드 = 단위테스트만 닿는 사실상 죽은 코드, 집행은 infra. → codex-2(죽은 reserve)·codex-3(엔티티 없음·port 합리화)과 **동일한 anemic 방향**.

### 신호 2 — stock≥0 CHECK → ✅ **충족 (암묵, 경험적 검증됨)**

- `models.py` Product = `PositiveIntegerField` 그대로(명시 CheckConstraint 미추가). **경험적 검증**: 실제 `catalog_product` 스키마에 `CHECK ("stock" >= 0)`·`CHECK ("price" >= 0)` **존재**(Django 4.2가 PositiveIntegerField에 대해 SQLite에서 컬럼 CHECK 자동 생성). `test_product_stock_constraint.py` **4/4 PASS**(음수 UPDATE 거부 확인). → DB 레벨 집행 실재. claude-1의 **명시 named CheckConstraint**보다 덜 명시적일 뿐, 기능적으로 동일하게 집행됨.
- ※ 코드품질 서브에이전트가 "거짓 테스트(CHECK 없음)"로 의심했으나 **오판**(PositiveIntegerField가 SQLite에 CHECK를 안 만든다는 잘못된 전제). 직접 스키마·테스트 실행으로 반증.
- OrderModel엔 `quantity≥1` + `status="CREATED"` CHECK 추가. (claude-1은 total_price CHECK; claude-2는 **unit_price·total_price 미저장** — Order는 product·quantity·status·created_at만.)

### 신호 3 — race 시 available_stock → ✅ 정확

- `_classify_failure`가 rowcount==0 시 동일 트랜잭션 재SELECT로 404/409 분류 + `available=row.stock` 보고. 성공 시 `remaining_stock` 반환. 1차 claude-1의 수정후 동작과 동일(버그 없음).

## 핵심 시사 (1차 결론을 뒤집음)

**B1은 claude에서도 비결정적이다.** claude-1은 도메인 배선(이중 방어선)으로 회피, claude-2는 동일 프롬프트에서 미배선+합리화로 재현. → 1차의 "claude가 B1을 결정적으로 잡는다"는 **상당 부분 런 분산**이었다. codex(2런 모두 anemic)와 claude(1런 회피·1런 재현)를 합치면, **양 런타임의 ddd 리뷰가 'infra 집행을 도메인 소유로 합리화'를 런마다 수용/반려하는 분산**이 실체에 가깝다. "런타임/모델 결정적 감사 격차"보다 약하다.

> 종합·판정은 `RESULTS.md` 결정성 섹션. 통제 이탈 때문에 2차는 *신호 수준* 비교만 신뢰.
