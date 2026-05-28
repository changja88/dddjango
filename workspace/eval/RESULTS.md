# dddjango Codex 포트 — Claude ↔ Codex 1:1 코드 품질 비교 (RESULTS)

> 같은 baseline(Product-only, Django 4.2.30) + 같은 프롬프트("재고 부족 409·충분 시 차감·주문 생성 API") + **같은 통제 결정**(G0=catalog 포함 / plain Django / Django test)에서 각 1회 실행.
> - **codex-2** = Codex CLI 0.134.0 (`runs/codex-2/`) — 상세 `codex-2-analysis.md`
> - **claude-1** = Claude Code dddjango v1.0.0 (`runs/claude-1/`) — 상세 `claude-1-analysis.md`
> 도구: 산출물 정적 평가. N=1씩(결정성 미확정 — 아래 한계 참조).

## 한 줄 결론

같은 최소 스택에서 **양쪽 다 완전한 §0 4계층을 생성**했고 빌드도 모두 통과했다. 차이는 *구조 생성*이 아니라 **리뷰·감사 깊이**에서 갈렸다 — **claude-1이 코드 정확성·표준 부합에서 우위**(도메인 죽은 코드 회피, 핵심 불변식 DB 제약 집행, 더 깊은 감사, 3배 많은 테스트). codex-2도 구조는 인상적이었고(Django 통합 레시피 독자 도출) 일부 지점(race 잔여보고)은 오히려 더 정확했다.

## Q1 차원별 대조

| # | 차원 | codex-2 | claude-1 | 우위 |
|---|---|---|---|---|
| Q1-1 | 트리 형태 | 완전 §0 4계층. 빈 `catalog/migrations` 잔존 | 완전 §0 4계층 + `domain_service/event/specification/published_service` 종류폴더까지, 평면 catalog 완전 제거 | **claude**(더 완전·청소) |
| Q1-2 | 도메인 배치 | **Product 엔티티 프로덕션 미사용**, `Product.reserve()` 죽은 코드 | `find_by_id`로 Product 로드 → **`product.deduct()` 매 요청 호출**(권위) | **claude**(도메인 생존) |
| Q1-3 | 트랜잭션·동시성 | `transaction.atomic`+조건부 UPDATE. 도메인 우회 | `transaction.atomic`+조건부 UPDATE. 도메인 `deduct()` 권위 + UPDATE 안전망 이중방어 | **claude**(권위/안전망 분리 실현) |
| Q1-4 | 불변식 DB 집행 | Order CHECK 2종. **Product `stock≥0` 누락** | Product `stock≥0` CHECK + Order `quantity≥1`·`total_price=unit*qty` CHECK | **claude**(핵심 불변식 집행) |
| Q1-5 | 예외 설계 | ProductError/OrderError 계층. `DatabaseBusy`가 product에 오배치 | InsufficientStock/ProductNotFound, 503 경로 없음 | claude(군더더기 적음) |
| Q1-6 | 네이밍 | `ProductModel`/`DjangoProductRepository`. impl 파일명 `product_repository.py` | `<Name>Model`/`DjangoProductRepository`, impl 파일명 `django_product_repository.py` | 동등(claude 파일명 약간 명확) |
| Q1-7 | 테스트 구조 | unit/integration/e2e. **15개** | unit/integration/e2e. **40개**(schema_in 11·error_out 3·결정적 oversell 1 등) | **claude**(3배 촘촘) |
| Q1-8 | 테스트 품질 | Fake 더블·행위중심, 7상태코드. 503은 주입 | Fake 더블·행위중심, 결정적 oversell 증명, 입력검증 11케이스 | **claude**(엣지 깊이) |
| Q1-9 | 포트 계약 | `reserve()->tuple[int,int,int]`(누수·불투명) | `find_by_id()->Optional[Product]`(도메인 매핑)+`deduct_stock()->int` | **claude**(도메인 경계 명확) |
| Q1-10 | 빌드 | migrate/check/15 tests OK | migrate/check/40 tests OK | 동등 |

## 핵심 결함 — 양 파이프라인 비교

| 항목 | codex-2 | claude-1 |
|---|---|---|
| **B1 도메인 죽은 코드** | ❌ 발생. ddd 리뷰·discipline 감사 모두 통과시킴 | ✅ 회피. **DDD 리뷰어가 [blocker] 빈혈모델 포착** → `deduct()`를 흐름에 배선 |
| **stock≥0 제약** | ❌ 누락. 감사·검증 놓침 | ✅ 모델+마이그레이션에 집행. DB 리뷰어 [important] |
| **race 시 available_stock** | ✅ 처음부터 정확(실패 경로서 DB 재조회) | ⚠️ 1차 버그 → **discipline-reviewer가 [important]로 잡아 수정**(DB 재조회로 교정) |
| 코더 메커니즘-대체(DR-06) | PoC서 sqlite 락 자작 이력 | §4.6 "거짓 통과 방어"로 선제 차단, 결정적 테스트 권위 |

→ **감사 방향이 일관**: claude 파이프라인이 B1·stock≥0·race 세 지점 모두에서 더 깊게 잡았다. codex 감사는 B1·stock≥0을 놓쳤다(단 race는 codex 코드가 애초에 옳았다).

## 설계 취향 차이 (우열 아님, 둘 다 타당)

| | codex-2 | claude-1 |
|---|---|---|
| 경로 | `POST /api/orders/` | `POST /orders` + `Location` |
| 검증 코드 | 422(수량)·415(미디어)·400 분리 | 400 통일(422 미사용)·405 `Allow: POST` |
| total_price | 계산(미저장) | 저장 + CHECK |
| DB busy | 503 경로(+sqlite 문자열 결합) | busy_timeout 권장, 503 미도입 |
| remaining_stock 응답 | 포함 | 미포함(status="CREATED" 포함) |

## 의존성 결정 성향 (반복 관찰 — G0 게이트)

| 결정 | claude 코디네이터 | codex 코디네이터 |
|---|---|---|
| 기능 배치 | "새 orders 앱" 추천 | "기존 catalog" 기본 |
| API 프레임워크 | 게이트 노출 + Ninja 추천 | 무언 plain Django |
| 테스트 러너 | 게이트 노출 + pytest 추천 | 무언 Django test |

→ claude=의존성/구조 결정을 사용자 게이트로 노출+풍부한 표준도구 권장 / codex=YAGNI 무의존 경로 자체 결정. (본 비교는 codex 쪽 최소 스택으로 통제 일치시킴.)

## 최종 판정

- **포트 충실도(메커니즘)**: ✅ 입증 완료(spawn_agent 역할분리·게이트·설치). codex가 동등 구조를 생성.
- **코드 품질**: 같은 통제 스택에서 **claude-1 > codex-2**. 격차의 본질은 **감사/리뷰 깊이**(정확성·불변식·도메인 생존을 codex 감사가 놓침)이지 구조 생성력이 아니다.
- **codex 강점**: §0 구조·Django 통합 레시피를 독자 도출, 일부 정확성(race 잔여보고)은 우위, 설계 명세 밀도 높음.

## 한계 (단정 금지)

- **N=1씩**. claude의 감사 우위가 *결정성*인지(매 런 그런지) *이번 런 운*인지 미확정. 단 B1·stock≥0·race 세 독립 지점에서 일관된 방향이라 *시사적*.
- 다음: codex 2~3회·claude 1~2회 반복으로 감사 격차의 재현성 확인(특히 codex 감사가 B1/stock≥0을 매번 놓치는지). → 이게 codex 포트의 실질 개선 과제(감사 스킬 강화) 여부를 가른다.
- 개선 과제 후보: codex 쪽 discipline-reviewer/ddd 리뷰가 (a) 도메인 죽은 코드 (b) 설계-코드 제약 누락을 잡도록 스킬 본문 보강 — Claude·Codex 공통 코퍼스라 양쪽 반영.

---

## 결정성 검증 (N=2) — codex-3 vs claude-2 (2026-05-29 추가)

> 2차 런: 같은 프롬프트로 codex-3(`runs/codex-3`)·claude-2(`runs/claude-2`) 각 1회 추가. 상세 `codex-3-analysis.md`·`claude-2-analysis.md`, 게이트 질문 `gate-questions.md`, 가독성 종합 `comparison-2.html`.
> **⚠️ 2차 통제 이탈**: claude-2 = Ninja+pytest+평면 최소구조(게이트 미노출로 기본 스택), codex-3 = plain Django+Django test+완전 §0. → 구조·프레임워크·테스트수 비교 불가, 프레임워크 무관 신호만 유효.

### 세 신호의 결정성

| 신호 | codex-2(1차) | codex-3(2차) | claude-1(1차) | claude-2(2차) | 판정 |
|---|---|---|---|---|---|
| B1 도메인 소유 | ✗ 죽은 reserve | ✗ 엔티티 없음(port 합리화) | ✓ deduct 배선 | ✗ deduct 미배선·죽은코드 | **비결정**(claude도 뒤집힘) |
| stock≥0 CHECK | ✗ 누락 | ✓ 명시+마이그가드 | ✓ 명시 | ✓ 암묵(검증됨) | **비결정**(codex 뒤집힘) |
| race available | ✓ | 미보고(스펙OK) | ⚠️→수정 | ✓ | 대등 |

### 결론 (1차 종합을 수정)

- **1차 "claude > codex (13:2:5)"는 상당 부분 N=1 분산이었다.** 양쪽 다 비결정적인 신호가 우연히 모두 claude에 유리하게 정렬된 한 표본. 2차에선 프레임워크 무관 코드가 **대등**(실질 결함은 claude-2가 죽은 도메인 코드 1건 더 많음; codex-3는 명시 CHECK·마이그 안전가드·일관 네이밍에서 앞섬).
- **"런타임/모델의 결정적 감사 깊이 격차" 가설은 약해졌다.** codex-3의 DB 감사가 claude-2보다 오히려 날카로웠다. B1은 양 런타임 ddd 리뷰가 "infra 집행을 도메인 소유로 합리화"를 런마다 수용/반려하는 분산.
- **재현되는 결정적 차이 = 상호작용 철학 + 스택 취향**: claude는 게이트로 결정을 잘게·근거와 함께 노출하고 풍부한 스택(Ninja·pytest)을, codex는 최소만 묻고 plain 스택을. 1·2차 모두 재현. 이는 코드 우열이 아니라 제품 성격 차이.
- **서브에이전트 검증 주의**: 코드품질 리뷰어의 "claude-2 거짓 테스트(stock CHECK 없음)" 주장은 메인이 스키마·테스트 직접 실행으로 **반증**(CHECK 실재, 4/4 PASS). 서브에이전트 결과도 무비판 수용 금지.

### 함의 (스캐폴딩 과제)

- 1차 근거로 세운 "codex discipline/ddd 스킬 보강" 과제는 **재고 필요**. codex가 결정적으로 못 잡는 게 아니라 양쪽 다 흔들린다. 보강한다면 codex 전용이 아니라 **양 런타임 ddd 리뷰가 'infra 집행=도메인 소유' 합리화를 일관 반려**하도록 — 단 공통 코퍼스라 Claude도 영향. 투자 전 N 더 확보 권장.
