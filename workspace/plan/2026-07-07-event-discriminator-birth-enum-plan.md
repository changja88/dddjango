# 발행 이벤트 discriminator birth-enum 규약 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 스펙(`workspace/design/2026-07-07-event-discriminator-birth-enum-design.md`, 2026-07-07 사용자 승인)을 dddjango 플러그인에 반영: 스킬 문서 6종 + SKILL.md 라우팅 4종 + reviewer ⑤ 신설 + codex 미러 동기. **백스톱 신설 없음 — 게이트 수 18 유지**(discriminator와 버전 태그가 AST 형태 동일 → 형태 판정 FP 불가피, reviewer 의미 점검 전담).

**Architecture:** 정본 `dddjango/` 수정 → final.md는 `corpus_mirror_sync --write` 자동 전파, SKILL.md·agents는 수동 미러. 규칙 본문 소유자 = architecture-ddd §3.7(birth-enum 원리·배치·수명), 표기 = django-ninja §3.1, 승격 기준 접속 = cleancode §2.14, 동기 테스트 = implementation-test §15.5 신설, outbox 예제 = implementation-django §16.5, 배치 관례 = houserules §2 트리.

## Global Constraints

- 기존 문체·`§` 상호참조 준수. "예외 신설"이 아니라 "판정의 선행 확정"으로 서술(DR-60 §3.1 "이름이 type/kind라는 이유로 승격하지 않는다"는 유지 — 트리거는 이름이 아니라 발행 봉투 위치).
- 버전 태그(`payload_schema_version`) 리터럴 동결을 모든 관련 절에 짝 조항으로 병기 — discriminator와 형태가 같아 혼동 최다 예상 지점.
- 평(non-Literal) Enum 필드는 discriminator 불가(Pydantic) — `Literal[EventType.X] = EventType.X` 파생이 유일 경로임을 명시.
- 커밋은 전체 검증 후 단일 feat 커밋.

---

### Task 1: architecture-ddd — §3.7 birth-enum 본문(소유자) + §2.5 1문장 + §6 예제 + SKILL.md

**Files:** `dddjango/skills/architecture-ddd/references/final.md`(§3.7 Outbox 패턴 끝 1197행 뒤·§2.5 361행 끝·IntegrationEvent 예제 1944-1957행), `SKILL.md`(핵심 원칙 도메인 이벤트 불릿 뒤)

- [ ] Step 1: §3.7 끝(### 3.8 직전)에 `#### 발행 이벤트 타입 — 1종째부터 enum (birth-enum)` 신설: 위치 기반 판정(발행 봉투 discriminator — outbox 저장·wire 노출로 승격 앵커 기본 도달 → 판정을 탄생 시점에 확정, 이름 트리거는 여전히 금지)·배치(`domain_layer/<aggregate>/event/event_type.py`, BC 내부 소유, 경계-로컬 금지 이유=infra 역방향 import)·파생 표기 포인터(ninja §3.1·test §15.5)·수명 append-only(값 변경·삭제 금지, 폐기=발행 중단+주석, 비호환=새 버전 태그+upcasting)·제외 짝 조항(버전 태그 리터럴 동결·소비 측 중계 스키마)·소비자 미지 값 방침
- [ ] Step 2: §2.5 "BC 간 enum·상수 공유 경계" 단락 끝에 1문장 — 발행 봉투 discriminator enum도 같은 원리(발행 BC 내부 자산·소비 BC는 wire 값 수용·import 금지)
- [ ] Step 3: §6 IntegrationEvent 예제 — `OrderEventType(StrEnum)` 발행 BC 소유 선언 추가 + `event_type: str` 필드에 단일 출처 주석(wire 형은 str 유지 — BC 경계를 넘는 published language)
- [ ] Step 4: SKILL.md 핵심 원칙에 birth-enum 1줄(§3.7 참조)
- [ ] Step 5: 검증 `grep -n 'birth-enum' final.md SKILL.md`

### Task 2: implementation-django-ninja — §3.1 불릿 + SKILL.md

**Files:** `dddjango/skills/implementation-django-ninja/references/final.md`(§3.1 불릿 끝 288행 뒤), `SKILL.md`(핵심 원칙 schema 불릿 뒤)

- [ ] Step 1: 불릿 추가 — 태그 `Literal[EventType.X] = EventType.X` 파생·봉투 `Annotated[Union[...], Field(discriminator="event_type")]`·평 Enum 불가·OpenAPI `const` 동일(계약 안정성 논거 불성립)·버전 태그 리터럴 동결·동기 테스트 §15.5 포인터·페이지네이션 직접 조합 회피(#1308 open)
- [ ] Step 2: SKILL.md 핵심 원칙 1줄
- [ ] Step 3: 검증 `grep -n 'discriminator' final.md SKILL.md`

### Task 3: discipline-cleancode — §2.14 접속 + SKILL.md

**Files:** `dddjango/skills/discipline-cleancode/references/final.md`(§2.14 원리 1항 끝 310행·허용 목록 Literal 항목 318행), `SKILL.md`(21행 불릿)

- [ ] Step 1: 원리 1항 끝("이름이 type/kind라는 이유만으로 승격하지 않는다." 뒤)에 birth-enum 선행 확정 1문장(`architecture-ddd` §3.7 참조)
- [ ] Step 2: 허용 목록 `Literal[...]` 항목에 경계 병기 — 발행 봉투 discriminator 자리는 enum 파생이 규율(맨 문자열이면 위반)·버전 태그는 같은 형태라도 리터럴 동결
- [ ] Step 3: SKILL.md 21행 불릿 끝에 birth-enum 절 병기
- [ ] Step 4: 검증 `grep -n 'birth-enum' final.md SKILL.md`

### Task 4: implementation-test — §15.5 신설 + SKILL.md

**Files:** `dddjango/skills/implementation-test/references/final.md`(§15.4 끝 2084행 뒤·`## 16.` 직전), `SKILL.md`(32-33행 불릿 뒤)

- [ ] Step 1: `### 15.5 발행 이벤트 봉투의 union-enum 동기 계약 테스트 (birth-enum 세트)` 신설 — 세트(선택 아님) 규정·검증 완료된 표준형 코드(get_args 태그 수집 == enum 멤버 집합)·§15.4와의 경계(구조 동기 vs 외부 계약 — 발행 payload 기댓값은 여전히 리터럴)
- [ ] Step 2: SKILL.md 핵심 불릿 1줄(§15.5)
- [ ] Step 3: 검증 `grep -n '15.5' final.md SKILL.md`

### Task 5: implementation-django — §16.5 outbox 예제 보강

**Files:** `dddjango/skills/implementation-django/references/final.md`(§16.5 1598-1621행)

- [ ] Step 1: 첫 코드 블록에 `OrderEventType(StrEnum)` 선언(domain_layer event 슬롯 주석·birth-enum 참조) + `event_type` 컬럼 주석(값 단일 출처·소비 심볼) + services.py `event_type="order.confirmed"` → `event_type=OrderEventType.ORDER_CONFIRMED`(심볼 소비 — kwarg 대입은 §2.5 소비 규율, `.value` 평탄화는 `default=`/마이그레이션 경계만)
- [ ] Step 2: 검증 `grep -n 'OrderEventType' final.md`

### Task 6: discipline-houserules — event 슬롯 배치 관례

**Files:** `dddjango/skills/discipline-houserules/references/final.md`(§2 트리 82행 event/ 주석)

- [ ] Step 1: event/ 슬롯 주석에 `event_type.py`(발행 discriminator enum·birth-enum) 병기
- [ ] Step 2: 검증 `grep -n 'event_type.py' final.md`

### Task 7: discipline-reviewer ⑤ 신설 + codex 수동 미러

**Files:** `dddjango/agents/discipline-reviewer.md`(41행 상수 승격 불릿), `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`(동일 불릿)

- [ ] Step 1: ④ 뒤에 ⑤ 신설 — 발행 봉투 discriminator가 domain StrEnum 파생 없이 맨 문자열 `Literal["…"]`/원시 str 선언이면 **important**(1종째부터 birth-enum — `architecture-ddd` §3.7); 동기 계약 테스트 부재(§15.5)도 세트로 봄. 제외: 버전 태그·소비 측 중계 스키마·상류 pass-through·데이터소스 BC
- [ ] Step 2: 거짓지적 방지 목록 `Literal[...]로 잠긴 인자 자리`에 경계 병기(발행 봉투 discriminator만 ⑤의 예외로 잡음·버전 태그는 그대로 허용) + 근거 tail에 `§3.7`·`§15.5` 추가
- [ ] Step 3: codex reviewer SKILL.md 동일 문안 반영, diff로 불릿 동일 확인
- [ ] Step 4: 검증 — 신설 불릿 양쪽 diff 0

### Task 8: 미러 동기·검증·기록·커밋

- [ ] Step 1: `python3 workspace/tools/corpus_mirror_sync.py --write` → `--check` exit 0(11/11)
- [ ] Step 2: SKILL.md 4종(architecture-ddd·django-ninja·cleancode·test) codex 수동 미러 → diff 0 확인
- [ ] Step 3: `claude plugin validate dddjango --strict` PASS
- [ ] Step 4: 설계 문서 상태를 "확정(2026-07-07 사용자 승인)"으로 갱신, DEVLOG §2에 DR-61(발단·확정 규칙·배치 조정 근거·기술 검증 4/4·열린 항목: reviewer ⑤ 라이브 발화 관측) + §0 최근 작업 갱신
- [ ] Step 5: `git diff --stat` 전수 확인 → 단일 feat 커밋

## Self-Review 결과

- 스펙 §4 표 9행 ↔ Task 1~8 전 항목 대응(표 1↔T1, 표 2↔T2, 표 3↔T3, 표 4↔T4, 표 5↔T5, 표 6↔T6, 표 7↔T7, 표 8·9↔T8).
- birth-enum 규칙 전문은 T1(소유자 architecture-ddd §3.7)에만, 나머지는 요지+참조 — DR-60 계획의 소유 지도 관례 준수.
- 버전 태그 짝 조항이 T1·T2·T3·T7 네 곳에 일관 병기(혼동 최다 지점 방어).
- reviewer ⑤는 기존 ①(미승격)과 배타 — ①은 분기·판정 앵커의 미승격, ⑤는 발행 봉투 위치의 선언 형태(분기 존재 무관). 백스톱 분업 서술 불요(⑤ 대응 백스톱 없음 — 전담 명시).
