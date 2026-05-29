# B1 해결책 검증 — 낙관적 동시성 패턴 (PoC 결과)

> 목적: 표준에 박기 전에, 후보 해결책(**낙관적 동시성 = 도메인이 규칙 소유 + version 가드**)이
> 실제로 (V1) 동시성 안전하고 (V2) 구조적으로 B1을 막는지 **결정적으로** 증명한다.
> 결과: **두 주장 모두 입증. 11/11 테스트 통과.**
> 실행: `~/Desktop/dddjango-smoke/.venv/bin/python manage.py test variants -v 2` (Django 4.2.30 / Py 3.9.6 / SQLite)

## 무엇을 비교했나 — 같은 1기능("재고 충분하면 차감")의 세 변형

| 변형 | 재고 판정의 위치 | 동시성 수단 |
|---|---|---|
| **N (naive)** | 도메인 `Product.deduct()` (메모리) | 없음 — 무방비 save |
| **O (optimistic, 후보)** | 도메인 `Product.deduct()` (권위) | repo `WHERE version=N` (경합 감지) + 재시도 |
| **C (conditional, 현행)** | **SQL** `WHERE stock>=qty` | 조건부 원자 UPDATE |

도메인 모델(`domain.Product.deduct()`)은 셋이 **동일하게 공유**한다. 차이는 *누가 그 규칙을 실제로 호출하느냐*뿐.

## 결과표

| 신호 | N (naive) | O (optimistic) | C (conditional) |
|---|---|---|---|
| **race-safe? (V1)** | ❌ oversell | ✅ 안전 | ✅ 안전 |
| **domain-owns-rule? (V2a)** | ✅ 호출됨 | ✅ **호출됨** | ❌ 미호출(죽은 코드) |
| **repo-logic-free? (V2b)** | ✅ | ✅ **version 가드만** | ❌ `stock__gte`가 SQL에 |
| **B1 발생?** | (안전성 결함) | ✅ **불가능** | ❌ **발생** |
| stock>=0 백스톱 | ✅ | ✅ (자동 CHECK) | ✅ |

→ **오직 O만 "동시성 안전 + 도메인 소유 + repo 무로직"을 동시에 만족한다.** C는 안전하지만 규칙을 SQL에 복제해 도메인을 죽이고(B1), N은 도메인을 살리지만 안전하지 않다.

## 핵심 증거 (결정적 — 스레드·타이밍 무관, 100% 재현)

**V1 — 동시성 안전** (`test_concurrency_deterministic.py`)
- `test_naive_oversells_under_concurrent_load`: 두 stale 객체(둘 다 stock=5)가 각 3개 차감 → 최종 stock=2. **6개 팔렸는데 3개만 빠짐 = oversell.** (테스트가 진짜 레이스를 잡는다는 증거)
- `test_stale_write_is_rejected_by_version_guard`: 첫 save는 rows=1(version 0→1), stale 둘째 save는 **rows=0(경합 감지)**. lost update 없음.
- `test_service_retry_reruns_domain_rule_and_rejects_oversell`: 경합 후 재시도가 **fresh 재고로 도메인 규칙을 재실행** → 2<3이라 `InsufficientStock`. 재고 불변.

**V2 — B1 구조적 불가능** (`test_b1_structure.py`)
- `test_optimistic_calls_domain_rule_in_production_path`: spy로 확인 — 프로덕션 경로가 `Product.deduct()`를 **실제 호출**(`calls == [(1,3)]`). 죽은 코드 아님.
- `test_conditional_never_calls_domain_rule`: conditional 경로는 `Product.deduct()`를 **한 번도 안 부름**(`calls == []`) = B1 재현.
- `test_optimistic_repo_has_no_business_rule`: optimistic repo 소스에 `stock__gte`/`stock>=` **부재**, `version`만 존재.
- `test_conditional_repo_embeds_business_rule`: conditional repo 소스에 `stock__gte` **존재** = "repo는 로직 없음" 원칙 위반 가시화.

## 보강 증거 (실제 스레드 부하, best-effort) (`test_concurrency_threaded.py`)

50 스레드가 재고 20에 동시 주문:
- **O / C**: oversell 0, `최종재고 == 20 - 성공수`, 음수 없음 — 부하에서도 안전.
- **N**: `ok=50, 재고는 3개만 빠짐(final=17) → lost_update OBSERVED` = **47개 oversell**. 결정적 결과가 실부하에서도 재현됨.

## 기판(substrate) 주의 — 정직 기록

- **Postgres 미설치** → SQLite로 검증. 1차 시도에서 Django 기본 테스트 DB(공유캐시 인메모리)는 테이블 락(`SQLITE_LOCKED`)이 `busy_timeout`으로 재시도되지 않아 스레드 테스트가 죽었다 → **테스트 DB를 파일로 강제**(`settings.TEST.NAME`)하여 `SQLITE_BUSY`로 직렬화·해결.
- SQLite는 쓰기를 직렬화하므로 스레드 부하의 인터리빙이 제한적이다. 그래서 **V1의 권위 증거는 결정적 테스트**(stale 객체 순차 재현)이고, 스레드 부하는 보강일 뿐이다. 다행히 파일 DB에서 naive oversell이 부하로도 재현됐다.
- 이 기판 민감성은 우리 표준 `dddjango/agents/design-architect.md:34`("sqlite `select_for_update` no-op")가 이미 지적한 지점과 같은 뿌리다.

## 결론

**후보(낙관적 동시성)는 검증을 통과했다.** 핵심은 메커니즘적 보장이다:

> version 가드는 `WHERE version=N`만 검사하므로 비즈니스 규칙(`stock>=qty`)을 **담을 수가 없다.** 따라서
> 규칙은 도메인 `deduct()` 말고 살 곳이 없고, 올바른 동작을 위해 구현은 **반드시** 그것을 호출해야 한다
> (재시도마다 fresh 데이터로). → **B1을 "권하지 않는" 게 아니라 "발생 자체를 불가능"하게 만든다.**

대조적으로 현행 conditional UPDATE는 안전하지만 규칙을 SQL에 복제하여 도메인을 죽이는 **B1 어포던스 자체**다.

## 이 PoC가 증명하지 *않는* 것 (정직 경계)

패턴이 race-safe + B1-proof임을 **구성적**으로 증명했다. 그러나 **이 패턴을 표준에 넣었을 때
스토캐스틱 플러그인 런에서 B1 빈도가 준다는 것은 증명하지 않는다** — 그건 별도의 측정 하네스
(게이트 고정 · N≥5~10 · 블라인드 루브릭, DEVLOG DR-14 참조) 영역이며 이번 범위 밖이다.

## 트레이드오프 (표준 인코딩 시 고려)

낙관적 버전은 version 컬럼 + 재시도 루프 + 충돌 예외가 붙어, 단일 필드 감소엔 조건부 UPDATE보다
코드가 늘어난다. "DDD 핵심=로직 관리 / repo는 로직 없음"을 기준으로 하면 정당한 대가다.
재시도 상한(thrash 방지)은 명시 필요(본 PoC는 `max_retries=10`).
