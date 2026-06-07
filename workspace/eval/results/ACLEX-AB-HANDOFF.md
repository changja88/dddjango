# aclex 테마 A+B — maj1~maj4·min1·min2 처방 라이브 핸드오프 (2026-06-07)

> 너가 `/dddjango`를 직접 돌리고(드라이브), 끝나면 내가 산출물을 읽어 채점한다.
> 정직 경계: **N=1 sanity** — "테마 A+B 처방(커밋 `062a64f`)이 라이브에서 *실현(생산자 예방)/발화(reviewer 차단)*하나"까지. **우열·결정성 결론 아님**(P4③ run-variance — 치명 레인이 런마다 갈림).
> 직전 라이브(`20260606-1448-aclex-claude.md`)에서 난 7결함(maj1~4·min1~3)을 STANDARD에 처방했다. 이 런은 그 처방이 *실제 파이프라인에서 재발을 막나*의 방향타다.

## 0. 준비 상태 (내가 완료)
- ✅ **플러그인 캐시 `062a64f` 신선화**: Claude(`~/.claude/plugins/cache/changja88/dddjango/1.0.0`)·Codex(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0`) 둘 다 레포 HEAD로 `diff -rq` **IDENTICAL**. 처방 6파일(`design-architect`·`discipline-reviewer` + `discipline-houserules`·`implementation-django-ninja`·`architecture-api`·`implementation-test` final) 안착 확인.
- ✅ **커밋 `062a64f`**(테마 A+B 처방·14파일·푸시 안 함, 브랜치 `eval/codex-determinism-n2`).
- ✅ **fixture 2개 greenfield 복원**:
  - 소스: baseline `reset --hard`(claude `6e48b68` / codex `32d1cf5`) + `clean` → `git status` clean·catalog 복원·`application/`·`.dddjango/` 산출물 제거
  - `.venv`: **Django 4.2.30만** — `import ninja`/`import pytest` → ModuleNotFoundError 확인(직전 라이브가 깐 ninja·pytest 스택 제거 = **부트스트랩 관찰면 복원**)
  - `db.sqlite3`: 직전 라이브 `order` 테이블 제거 → catalog migrate → **Widget(10)·Gadget(3) 재시드** → `manage.py check` no issues
  - `~/Desktop/dddjango-aclex-claude` / `~/Desktop/dddjango-aclex-codex`
- ⚠️ **반드시 새 세션에서 시작** — 캐시를 방금 갱신해서 열려 있는 세션은 구 에이전트 텍스트를 메모리에 들고 있다. (기존 세션 쓰려면 `/reload-plugins` 후.)

## 1. 태스크 (양 런 공통 — DR-44 라이브와 **동일 입력**, 변수 통제)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
> ⚠️ 동시성·오버셀·CAS·재시도·pytest·venv·프레임워크·입력 상한·예외 형식을 **프롬프트에 명시하지 않는다** — 표준이 스스로 하는지가 관찰면. 이 태스크가 새 `orders` BC↔`catalog` BC를 **ACL로 통합**시키고 낙관적 CAS 동시성을 끌어내, 테마 A(경계 예외 전수 매핑)·테마 B(테스트 진정성)가 노리는 시나리오를 자연 발생시킨다.

## 2. 고정 게이트 답 (변수 제거 — 양 런 공통)
| 게이트 | 답 | 이유 |
|---|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정해줘" | 강제하면 ACL 통합 축 죽음 |
| G0 렌즈 | **ddd + db + api** | HTTP 계약(409)·동시성 있음 |
| G0 스코프 | **제안대로** | 확장 금지 |
| API 스택/프레임워크 | **"표준 기본대로"** — ⚠️ plain 강제 **금지** | 표준이 스스로 Ninja로 수렴하는지 |
| 테스트 러너 | **"표준 기본대로"** | 표준이 스스로 pytest 부트스트랩하는지 |
| G1 멱등성 | **미도입** | 변수 제거 |
| G1 409 본문 | **available/requested 노출(기본)** | 변수 제거 |
| G1 API 버전 | **미도입**(`/api/orders`) | 변수 제거 |
| G1 설계 / G2 구현 | **명백한 결함 없으면 무수정 승인** | ⭐ 경계 예외 매핑 완전성·테스트 진정성은 *관찰 대상*이지 내가 끼어들 게 아니다 — 표준이 스스로 하는지 본다. 명백한 결함만 반송 |
| thinking | **OFF** (coder) | 비용 레버, 품질 무손실(DR-08) |

## 3. 실행
**Claude**:
```
cd ~/Desktop/dddjango-aclex-claude
claude                       # 새 세션
# 세션 안에서:  /dddjango  → §1 프롬프트 → §2 게이트 답
```
**Codex**:
```
cd ~/Desktop/dddjango-aclex-codex
codex                        # 새 세션 — dddjango 코디네이터 트리거
# §1 프롬프트 → §2 게이트 답
```
**끝나면 (양 런 공통) 채점 전 스모크:**
```
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate
.venv/bin/pytest
```

## 4. 끝나면 나에게 "claude 끝났어" / "codex 끝났어"
내가 fixture의 `application/`·테스트·`.dddjango/`(설계명세)·`requirements.txt`·`pyproject.toml`을 직접 읽어 채점한다(붙여넣을 필요 없음). **정적 관측 + 필요 시 내가 fixture에서 직접 동적 probe**(깨진 JSON 본문·거대 product_id·락 경합 → 실제 HTTP status·content-type).

## 5. 채점 신호 — 테마 A+B 7결함 (처방 실현/발화 여부)
> 직전 채점의 흠을 1.5.0+`062a64f`가 막나/잡나. **maj1·maj2·min1**은 핸들러 *존재*(정적) + 내 *동적 probe*로, **maj3·maj4**는 주로 *reviewer 발화*(프로즈 — DR-22 미발화 위험)로 본다.

| # | 결함(직전 흠) | 처방 | 관측 위치 | PASS(실현) | FAIL(재발) |
|---|---|---|---|---|---|
| **maj1** | ACL이 도메인 예외 3개만 잡음 → raw `OperationalError`/`IntegrityError`가 경계 누수 → **HTTP 500** | presentation **단일 변환점**에 `OperationalError`(transient→503/409 retryable·영구장애→500)·`IntegrityError`(500)·`Exception` catch-all 핸들러 + `_is_retryable_db_error`(locked/deadlock/serialize·sqlstate 40001/40P01). design-architect: transient 인프라 예외도 retryable 매핑. houserules: ACL은 위장 번역 안 함 | `application/<order>/presentation_layer/*` 핸들러 + `.dddjango/.../design-spec` status 표 | DB 예외 핸들러(+HttpError·Exception) 존재·transient 503/409 분기·**미매핑 누수 0**. probe: raw `OperationalError("database is locked")` → 500 아님 | DB 예외 핸들러 누락 → raw 통과 **500** |
| **maj2** | 깨진 JSON 본문 → ninja `HttpError(400)` → `application/json`(problem+json 아님) | `@api.exception_handler(HttpError)` → `problem()` 매핑(status별 title·detail) | presentation 핸들러 | HttpError 핸들러 존재. probe: 깨진 본문 POST → `Content-Type: application/problem+json` | HttpError 핸들러 없음 → 깨진 본문 `application/json` |
| **maj3** | `test_..._do_not_oversell`이 이름은 동시성/oversell인데 **순차** 루프(stale-version·스레드 경합 0) → CAS 충돌 0 + 항진 단언 | reviewer **행사 위장 경계**(이름이 약속한 동시성을 순차로 '검증'하면 vacuous·항진 단언 → important; 재고 차감·소진 순차 검증은 유효) | 동시성/oversell 이름 테스트 + discipline-reviewer 노트 | 동시성 테스트가 **실제 stale-version 주입/스레드 경합·CAS 충돌**을 검증; OR reviewer가 순차-위장 **important 발화** | 순차 위장·항진 단언인데 reviewer **미발화**(DR-22) |
| **maj4** | `test_stock_check_constraint`가 named constraint 아닌 `PositiveIntegerField` 암묵 CHECK를 검증(오귀속) | reviewer **The Liar 변종**(술어 *동치인 기존 암묵 가드*가 먼저 통과 → false green; 다층 방어는 §9.5 정상이라 제약 *제거* 아니라 **테스트 귀속** 수정·strictly stronger `>=N`일 때만 구별 단언) | named constraint 테스트 + reviewer 노트 | 제약 테스트가 **구별 단언**(PositiveIntegerField와 분리); OR reviewer **오귀속 발화** | 동치 가드에 가려진 false green·reviewer 미발화 |
| **min1** | 거대 `product_id` → `OverflowError` → **500** | architecture-api §5.1: 외부 식별자·수치 입력 허용 범위에 **상한**도 포함(하한만 X)·구체 매직넘버는 implementation 위임 | `schema_in` product_id 필드 | 수치 입력 상한 존재. probe: 거대 id POST → **400/422** | 상한 없음 → `OverflowError` **500** |
| **min2** | `InvalidOrderQuantity` 핸들러 부재(schema `Field(ge=1)` 뒤 latent) | implementation-django-ninja §6.2: 스키마가 latent화해도 공통 베이스 매핑에서 **빠뜨리지 않음** | 도메인 예외 핸들러 집합 | 모든 도메인 예외(`InvalidOrderQuantity` 포함) 베이스 매핑 | 핸들러 누락(latent) |
| min3 | write-conflict end-to-end 미검증 | **무처방**(이미 end-to-end 존재) | — | (보너스 관측만) | — |

**척추(상시)**: SD-1~7·SH-1~10·NJ-1~6·FC-1~3·Q-1~7 — 빈혈 아님·계층 순수·Ninja 얇은 operation·BC FK 0·R/C/Q 명명·테스트 진정성. **치명 레인 ❌ 1개 = 픽스처 FAIL.**

## 6. 한계 (정직)
**N=1.** 양 런타임 1회씩 = 우열 비교 아님. P4③ run-variance로 치명 FAIL 레인이 런마다 갈린다(직전 c4live·nj2live에서 Claude↔Codex 반전 전례). 이 런은 **테마 A+B 처방이 라이브서 재발을 막나/잡나**의 방향타다.
- **생산자(예방) 측**(maj1·maj2·min1·min2)이 1차 — architect·coder가 경계 예외를 *전수 매핑*하고 입력 상한을 두는지. 준수 런이면 reviewer는 미발화(=정상)·내 동적 probe가 누수 0 확인.
- **차단(reviewer) 측**(maj3·maj4)은 **라이브 발화 미검증**(DR-22 위험: 프로즈 reviewer가 라이브서 미발화한 P1a 전례). 위장 테스트가 생기는데 reviewer가 미발화면 **프로즈 갭**(→ 보류했던 백스톱 재개 트리거).
- 정본: `workspace/eval/results/ACLEX-CLAUDE-FIX-PLAN.md`(처방 플랜 v3)·커밋 `062a64f`·채점지 `20260606-1448-aclex-claude.md`.
