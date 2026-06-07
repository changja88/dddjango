# aclex Claude 처방 계획 — 최신 채점지 결함 추적

> **출처**: `20260606-1448-aclex-claude.md` (DR-44 ACL 예외 전수성·플러그인 1.5.0 라이브 런, 2026-06-06).
> 단일-패스 채점 PASS → 5-서브에이전트 심층 적대 감사가 **major 4 + minor 3** 적출 → PASS→결함발견.
> **ID = 루브릭 코드**(`RUBRIC.md`). 채점지 §정정 원번호(major `1~4`·minor `①~③`) 병기.
> **적대 검증 완료(2026-06-06)**: 7개 결함 각각 독립 사본에서 적대적 재현/반증. **7개 모두 실재(반증 0)**, 2건 평가 조정. → 아래 §적대 검증 결과.
> **수정 대상 = 표준(플러그인 스킬/하우스룰/에이전트/백스톱)**. fixture 코드는 증거일 뿐, 처방은 *재발 방지*를 위해 표준을 고친 뒤 라이브 재검증(DR-XX 루프).
> **정직 경계**: 모든 관측 **N=1**.

## 진행도 요약

| 루브릭 코드 ⟨채점지#⟩ | 문제 (한 줄) | 심각도(조정) | 적대검증 | 원인 | 해결안 | 구현 | 검증 |
|----|-------------|--------|:----:|:----:|:------:|:----:|:----:|
| **SD-7** ⟨major 1⟩ | ACL이 인프라 예외(`OperationalError`·`IntegrityError`) 번역 안 하고 누수 → HTTP 500 | major (↑ 보안 치명 여지) | ✅CONFIRMED | ✅ | ⬜ | ⬜ | ⬜ |
| **Q-2** ⟨major 2⟩ | 올바른 CT + 깨진 본문 → 400 `application/json` (problem+json 아님) | major | ✅CONFIRMED | ✅ | ⬜ | ⬜ | ⬜ |
| **Q-3 / FC-2** ⟨major 3⟩ | `test_sequential…oversell` 순차 → CAS 약속 미실현 + 죽은 단언 | major → **minor~medium** (↓) | ◐PARTIAL | ✅ | ⬜ | ⬜ | ⬜ |
| **FC-2** ⟨major 4⟩ | `test_stock_check_constraint` 오귀속(암묵 CHECK) → 산출물 삭제해도 green | major | ✅CONFIRMED | ✅ | ⬜ | ⬜ | ⬜ |
| **Q-2** ⟨minor ①⟩ | 거대정수 `product_id`(`10**30`) → 500 (헤지 반증: sqlite 아님·구조적) | minor | ◐PARTIAL | ✅ | ⬜ | ⬜ | ⬜ |
| **SD-6** ⟨minor ②⟩ | `InvalidOrderQuantity` 중앙 핸들러 부재 (순수 latent) | minor | ✅CONFIRMED | ✅ | ⬜ | ⬜ | ⬜ |
| **Q-3** ⟨minor ③⟩ | §6.8 write-conflict 종단 미검증 (종단 테스트 skip·조각 mock 3개) | minor | ✅CONFIRMED | ✅ | ⬜ | ⬜ | ⬜ |

> 범례: ⬜ 미착수 · 🔄 진행중 · ✅ 완료 · ◐ 부분. `검증`=표준 수정 후 라이브 재검증(DR-XX 루프).

---

## 적대 검증 결과 (2026-06-06, 7 독립 서브에이전트·각 전용 fixture 사본)

### SD-7 ⟨major 1⟩ — ✅ CONFIRMED (심각도 ↑ 여지)
- **검증**: 인프라 예외 주입(repo `save_with_cas`에 `OperationalError`/`IntegrityError`) → 정상 주문 POST → **HTTP 500 결정적 재현**. ACL은 도메인 예외 3종만 catch(`catalog_product_stock_adapter.py:46-51`), `problem.py:92-139`에 포괄/인프라/500·503 핸들러 0. **+ fixture `config/settings.py:26` `DEBUG=True` → 500 본문에 전체 스택트레이스(내부 절대경로·계층 호출체인·SQL 원문) `text/plain` 노출 = 보안 치명** (단 prod `DEBUG=False`면 스택은 안 새나 여전히 500·problem 아님).
- **원인(확정)**: DR-44 ACL 전수성이 *포트 도메인 예외 집합*에만 앵커 → 인프라 transient 범위 밖. **표준-수준 빈틈**(정본 `ACL-EX`). §6.7 동시성 테스트 sequential이라 영구 green으로 가려짐.
- **해결안 후보(미확정)**: ACL/presentation에 인프라 예외(`OperationalError`/`IntegrityError`/상위 `DatabaseError`) 경계 — retryable problem(503 또는 500-problem)으로 번역 + 인프라 예외 HTTP 주입 회귀 테스트. 표준 측 = houserules/ddd ACL 전수성 정의에 인프라-예외 패밀리 포함 + reviewer/백스톱.
- **체크**: [x] 적대검증 [x] 원인 [ ] 해결안 [ ] 구현 [ ] 라이브검증

### Q-2 ⟨major 2⟩ — ✅ CONFIRMED
- **검증**: CT=`application/json` + 깨진 본문 POST → ninja `BodyModel.get_request_data`가 `HttpError(400)` → 기본 핸들러 → **400 `application/json` `{"detail":"Cannot parse request body"}`**(problem+json 아님). `problem.py`에 `HttpError`/포괄 핸들러 없음. 415 데코(`content_negotiation.py:33-42`)는 `request.content_type`만 봐 통과. 대조군: 스키마 위반은 422 problem+json(정상).
- **원인(확정)**: 표준 §2.5 "모든 오류 problem+json" 약속이 ValidationError만 재포장 → ninja 파싱-실패(`HttpError(400)`) 경로 미커버(거짓 완전성).
- **해결안 후보(미확정)**: 중앙 핸들러에 `@api.exception_handler(HttpError)`(최소 파싱-실패 400) 추가 → problem+json 재포장. 표준 §2.5 범위에 ninja 파싱-실패 명시 + 인수 테스트에 "CT=json+깨진본문" 슬라이스(현 §6.6은 text/plain만 커버).
- **체크**: [x] 적대검증 [x] 원인 [ ] 해결안 [ ] 구현 [ ] 라이브검증

### Q-3 / FC-2 ⟨major 3⟩ — ◐ PARTIAL (major → minor~medium 하향)
- **검증**: 대상 `test_create_order_api.py:188`은 **순차(스레드 0)** + 항진단언 `assert (n-remaining)<=n`(`:216`) + CAS 무력화(`save_with_cas`→항상 True) mutation에도 **green** = vacuous 확정(FC-2)·§6.7 미실현(Q-3). **BUT 대조군** `test_save_with_cas_returns_false_on_version_conflict`(`test_product_repository.py:59`)는 같은 mutation에 **RED** → CAS lost-update 안전성은 결정적으로 커버됨. 즉 "CAS 미검증"은 과대평가, 실체 = "이 §6.7 테스트만 무력 + 죽은 단언".
- **원인(확정)**: §6.7 동시성 약속을 §6.8 단위 테스트(repository CAS)로 위임했으나 §6.7 인수 테스트 자체는 순차라 자기 약속 미실현 + 죽은 단언 잔존.
- **해결안 후보(미확정)**: 죽은 단언 제거/의미화(`== 실제 차감총량`) + §6.7 인수에 결정적 CAS 스파이 1건(자기 약속 실현). 표준 측 Q-3 집행(discipline-reviewer "선언 동시성=실제 실현" + 죽은 단언 탐지).
- **체크**: [x] 적대검증 [x] 원인 [ ] 해결안 [ ] 구현 [ ] 라이브검증

### FC-2 ⟨major 4⟩ — ✅ CONFIRMED
- **검증**: 명명 CHECK 제약 **완전 삭제**(모델 `constraints=[]` + 마이그 no-op)해도 테스트 **green** → `PositiveIntegerField` 암묵 CHECK(`stock>=0`)가 대신 IntegrityError. counter-check: 필드를 `IntegerField`로 바꾸면(암묵 CHECK 제거) **RED** → 암묵 필드 CHECK가 유일 보호. 명명 제약 = `stock>=0` 중복(테스트 값 -3은 두 제약 차집합=공집합).
- **원인(확정)**: 테스트가 `PositiveIntegerField`(암묵 `>=0`)와 동일조건 명명제약을 구분 못 하는 음수값으로 검증 → 산출물 고유 보호 검증 0.
- **해결안 후보(미확정)**: 필드를 `IntegerField`로 두고 음수차단을 명명제약에만 의존 OR 명명제약을 필드보다 엄격하게(비즈 하한). 표준 측 = 제약 테스트 오귀속 탐지(reviewer "제약 테스트가 산출물 고유 보호 검증하나").
- **체크**: [x] 적대검증 [x] 원인 [ ] 해결안 [ ] 구현 [ ] 라이브검증

### Q-2 ⟨minor ①⟩ — ◐ PARTIAL (헤지 반증)
- **검증**: `product_id=10**30` POST → `OverflowError` → **500 `text/html`**(problem+json 아님). 경계 정확히 **2^63-1**(max bigint OK, +1 깨짐) → **Postgres bigint도 `DataError`로 동일 500** = sqlite 아티팩트 아님·구조적. 스키마 `schema_in.py:14 Field(gt=0)`에 상한 없음. `problem.py`에 `DatabaseError`/포괄 핸들러 부재.
- **원인(확정)**: 식별자 입력에 상한 미설정 → 범위초과 정수가 DB층까지 가서 raw DB 예외 → 중앙 problem 우회. (채점지 "underdetermined/sqlite" 헤지는 틀림.)
- **해결안 후보(미확정)**: `product_id: Field(gt=0, le=2^63-1)` 상한(범위초과→기존 422 problem 경로 재활용) + 선택적 presentation 최후방 `DatabaseError`/`Exception` problem+json 핸들러(§6.9 일관성 백스톱).
- **체크**: [x] 적대검증 [x] 원인 [ ] 해결안 [ ] 구현 [ ] 라이브검증

### SD-6 ⟨minor ②⟩ — ✅ CONFIRMED (순수 latent)
- **검증**: `InvalidOrderQuantity` 정의(`exception.py:16`)·도메인 raise(`order.py:41-44`)되나 `problem.py` 미등록. 단일 진입점에서 스키마 `Field(ge=1)`가 동일집합(`quantity<1`)을 도메인 도달 전 422로 선차단 → **현재 도달 불가(순수 latent, 500 불가)**. `test_..._repacked_to_422`가 `command.execute.assert_not_called()`로 입증.
- **원인(확정)**: 도메인 예외 전수 vs 등록 핸들러 집합 불일치(중앙 변환 전수성 결손). 스키마/도메인 분리 진화(스키마 완화·신규 진입점) 시 활성화 위험.
- **해결안 후보(미확정)**: `@api.exception_handler(InvalidOrderQuantity)` 추가 + 근본은 "도메인 예외 전수 ↔ 등록 핸들러 집합" 대조 백스톱.
- **체크**: [x] 적대검증 [x] 원인 [ ] 해결안 [ ] 구현 [ ] 라이브검증

### Q-3 ⟨minor ③⟩ — ✅ CONFIRMED
- **검증**: §6.8 종단 HTTP 테스트 `test_write_conflict_exhaustion_returns_409_retryable`(`test_create_order_api.py:270`)가 **`@pytest.mark.skip`**(실행 0). write-conflict는 조각 3개로만 분할: catalog `save_with_cas` spy / ACL `CatalogWriteService` patch / 핸들러 command Mock(+임시 `NinjaAPI`). 진짜 OHS+ACL+프로덕션 `ninja_api` 종단 0.
- **원인(확정)**: sqlite 단일라이터서 결정적 race 자연발생 불가 → 종단 테스트 skip(방어가능 판단)이나 종단 실현 0.
- **해결안 후보(미확정)**: 최외곽 한 지점(repo `save_with_cas`)만 version-경합 스파이 주입, 나머지(catalog command·ACL·프로덕션 `ninja_api`·실 DB)는 실물로 둔 결정적 통합 테스트로 skip 대체(flaky 없이 종단 1건 확보).
- **체크**: [x] 적대검증 [x] 원인 [ ] 해결안 [ ] 구현 [ ] 라이브검증

---

## 처방 우선순위 (적대검증 후)
1. **SD-7 ⟨major1⟩** — 표준-수준 #1, 보안 치명 여지. 가장 시급.
2. **Q-2 ⟨major2⟩** — 표준-수준(§2.5 problem+json 전수성).
3. **FC-2 ⟨major4⟩ / Q-3·FC-2 ⟨major3⟩** — 테스트 건전성 집행(reviewer/표준 테스트 레시피). major3은 하향됐으나 죽은 단언은 즉시 정리 대상.
4. **minor ①②③** — 후순위(상한 검증·핸들러 전수성·종단 테스트).

> 우선순위는 적대검증 반영본. 해결안 설계는 각 항목별로 표준 수정안을 적대 리뷰 후 확정(DR-XX 방식).

## 관련 정본
- 채점지: `workspace/eval/results/20260606-1448-aclex-claude.md`
- 미해결 추적: `workspace/eval/results/REMAINING-ISSUES.md` (`ACL-EX` = SD-7 ⟨major 1⟩)
- 루브릭: `workspace/eval/rubric/RUBRIC.md` · 설계 정본: `workspace/design/2026-06-06-acl-exception-exhaustiveness.md` (v2) · DEVLOG DR-44/45
- 적대검증 사본(일회용): `/tmp/aclex-verify/{sd7,q2maj2,maj3,fc2maj4,q2min1,sd6min2,q3min3}`
