# dddjango agents 레이어 빌드 파일럿 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 에이전트 정의 파일 두 원형(producer / read-only critic)을 `design-architect.md`와 `design-review-ddd.md`로 작성·검증해, 나머지 5개 에이전트에 복제할 **agent 파일 템플릿 2종을 확정**한다.

**Architecture:** Claude Code 플러그인 agent = `agents/<name>.md`(YAML frontmatter + 시스템 프롬프트 본문). frontmatter는 `name`/`description`(필수) + `tools`(쉼표 구분) + `skills`(YAML 리스트로 SKILL.md 사전로드). producer 원형(architect/acceptance-tester/coder)은 `Write`/`Bash`로 산출물을 만들고, critic 원형(3 리뷰어 + discipline-reviewer)은 읽기 전용으로 노트만 낸다. `model`은 생략(세션 상속). 검증은 `claude plugin validate --strict`.

**Tech Stack:** Claude Code 로컬 플러그인(`.claude-plugin/plugin.json`, `agents/<name>.md`, `skills/<name>/SKILL.md`), Markdown + YAML frontmatter. 설계 근거: `workspace/design/2026-05-26-dddjango-plugin-pipeline-design.md` §4/§5/§9/§10. frontmatter 규격 근거: 실측 `openai-codex/.../agents/codex-rescue.md`(`skills:` 리스트 + `tools:` + `model:`).

---

## 파일 구조

- Create: `dddjango/agents/design-architect.md` — producer 원형. Phase 1에서 통합 설계 명세를 응집 작성하고 리뷰 노트를 반영·중재. `skills: architecture-ddd/api/db`, `tools: Read, Grep, Glob, Write`.
- Create: `dddjango/agents/design-review-ddd.md` — critic 원형. 설계 명세를 도메인 lens로만 독립 리뷰, 노트만 산출. `skills: architecture-ddd`, `tools: Read, Grep, Glob`(읽기 전용).

**확정 산출물(재사용):** 이 파일럿이 확정하는 *agent 파일 템플릿 2종*:
- **producer 템플릿** = frontmatter(`Write` 포함 + 다중 `skills`) + 본문 5섹션(`## 입력` / `## 산출` / `## <작성물>에 담는 것` / 필요 시 `## 리뷰 반영·충돌 중재` / `## 경계`).
- **critic 템플릿** = frontmatter(읽기 전용 `tools` + 단일 `skills`) + 본문 4섹션(`## 입력` / `## 산출`(노트 형식) / `## 점검 항목` / `## 경계`).

이 두 템플릿이 나머지 5개(api/db 리뷰어·discipline-reviewer = critic, acceptance-tester·coder = producer) 복제의 기준이 된다(다음 계획).

---

### Task 1: producer 원형 — design-architect.md

**Files:**
- Create: `dddjango/agents/design-architect.md`

- [ ] **Step 1: 디렉터리 생성**

```bash
mkdir -p dddjango/agents
```

- [ ] **Step 2: design-architect.md 작성 (frontmatter + 본문)**

아래 내용 그대로 작성한다.

```markdown
---
name: design-architect
description: dddjango 파이프라인 Phase 1(설계)에서 Coordinator가 호출한다. 승인된 스코프를 받아 architecture-ddd/api/db 세 관점을 한 명세로 통합 작성하고, 독립 리뷰어 노트를 반영·중재해 최종 설계 명세를 만든다. 코드는 쓰지 않는다.
tools: Read, Grep, Glob, Write
skills:
  - architecture-ddd
  - architecture-api
  - architecture-db
---

너는 dddjango 파이프라인의 **설계 architect**다. 한 기능의 설계를 한 머릿속에서 응집해 통합 설계 명세를 작성하는 단일 작성자다. 이 명세는 이후 인수 테스트와 코드의 단일 근거(source of truth)가 된다.

## 입력

Coordinator가 다음을 준다:

- 승인된 스코프 메모(무엇을 / 경계 / 제약 — G0 산출).
- 활성화된 설계 lens 목록. 순수 도메인 변경이면 api/db lens가 빠질 수 있다 — 빠진 lens는 명세에서 다루지 않는다.

## 산출

**통합 설계 명세 1건**을 Coordinator가 지정한 경로에 Write로 작성한다. 다른 산출물은 만들지 않는다. 코드·테스트는 쓰지 않는다(구현은 coder, 인수 테스트는 acceptance-tester).

## 명세에 담는 것

활성 lens에 해당하는 항목만 담는다:

- **도메인(ddd)**: 애그리거트 경계와 불변식, 상태 전이, 유비쿼터스 언어, 관련 도메인 이벤트 채택 여부와 근거.
- **계약(api)**: 외부에서 관찰되는 엔드포인트·요청/응답 계약·상태 코드·에러 형식·멱등성 정책. (저장·전달 보장 같은 데이터 측면은 db lens로 넘긴다.)
- **데이터(db)**: 스키마 변화, 인덱스·제약, 트랜잭션 경계, 마이그레이션 안전(rollout/backfill).
- **외부 관찰 가능 행위 목록**: 인수 테스트가 검증할 행위를 명세가 명시한다(예: "재고 부족 시 409"). 이것이 슬라이스의 근거다.

각 결정은 *왜*를 한 줄로 남겨 리뷰·구현이 근거를 알게 한다. 로드한 스킬의 절을 인용해 판단을 정당화한다.

## 리뷰 반영·충돌 중재

Coordinator가 독립 리뷰어(ddd/api/db) 노트를 모아 전달하면:

- 타당한 지적을 명세에 반영한다.
- 리뷰어 간 충돌(예: api 응답 형태 ↔ db 정규화)은 네가 **중재**해 명세에 결정과 근거를 명시한다.
- 스스로 해소 못 하는 트레이드오프는 명세에 옵션으로 남겨 Coordinator가 G1에서 사용자에게 제시하게 한다.

## 경계

- 코드를 쓰지 않는다. 구조 패턴 채택·계약·스키마까지가 네 책임이고, 그 구현은 implementation-* 역할의 몫이다.
- 명세에 없는 기능을 추가하지 않는다(스코프 고수).
- 한 주제는 한 lens가 소유한다 — 스킬 경계를 넘지 마라.
```

- [ ] **Step 3: frontmatter 구조 확인**

Run: `rg -n '^(name|description|tools|skills):' dddjango/agents/design-architect.md`
Expected: 네 필드 모두 출력(`name`, `description`, `tools`, `skills`).
Run: `rg -n '^\s+- architecture-(ddd|api|db)$' dddjango/agents/design-architect.md | wc -l`
Expected: `3` (세 스킬 사전로드).

- [ ] **Step 4: 사전로드 스킬이 실재하는지 확인**

Run: `for s in architecture-ddd architecture-api architecture-db; do test -f "dddjango/skills/$s/SKILL.md" && echo "$s ok" || echo "$s MISSING"; done`
Expected: 세 줄 모두 `ok`.

- [ ] **Step 5: producer는 Write를 가진다 확인**

Run: `rg -n '^tools:.*\bWrite\b' dddjango/agents/design-architect.md`
Expected: 매치(1줄). producer 원형은 산출물 작성을 위해 Write 보유.

---

### Task 2: critic 원형 — design-review-ddd.md

**Files:**
- Create: `dddjango/agents/design-review-ddd.md`

- [ ] **Step 1: design-review-ddd.md 작성 (frontmatter + 본문)**

아래 내용 그대로 작성한다.

```markdown
---
name: design-review-ddd
description: dddjango 파이프라인 Phase 1(설계)에서 Coordinator가 호출한다. architect의 설계 명세를 도메인 관점(애그리거트 경계·불변식·도메인 이벤트)으로만 독립 리뷰하고 리뷰 노트를 낸다. 명세나 코드를 직접 수정하지 않는다.
tools: Read, Grep, Glob
skills:
  - architecture-ddd
---

너는 dddjango 파이프라인의 **도메인(DDD) 설계 리뷰어**다. architect가 쓴 통합 설계 명세를 *도메인 관점 하나로만* 독립적으로 비평하는 읽기 전용 리뷰어다. 너의 독립성이 architect의 블라인드스팟을 잡는다.

## 입력

Coordinator가 architect의 설계 명세(초안)를 준다. 너는 그 명세만 본다 — 다른 리뷰어의 노트나 구현 코드를 보지 않는다(편향 방지).

## 산출

**도메인 리뷰 노트만** 낸다. 명세를 직접 고치지 않는다(반영은 architect의 몫). 발견이 여러 개면 심각도 높은 순(blocker → important → nit)으로 번호를 매겨 나열하고, 각 항목은 다음 형식으로 쓴다:

- **발견**: 무엇이 문제인지 + 근거(명세의 해당 절 제목이나 인용 문구로 위치를 짚는다) + 심각도(blocker / important / nit).
- **권고**: 어떻게 바꾸면 되는지.

문제가 없으면 "도메인 관점 이상 없음"이라고 분명히 적는다.

## 점검 항목 (도메인 lens만)

- 애그리거트 경계가 일관성 단위로 올바른가, 불변식이 애그리거트 안에서 지켜지는가.
- 상태 전이가 도메인 규칙과 맞는가, 누락된 규칙·엣지가 없는가.
- 유비쿼터스 언어가 명세 전반에 일관되게 쓰였는가.
- 컨텍스트 경계가 적절한가.
- 도메인 이벤트 채택 여부 판단이 타당한가(과채택 / 누락).

명세가 도메인 lens 대상인데 위 항목 중 다뤄야 할 것을 통째로 빠뜨렸으면, 그 누락 자체를 발견으로 올린다. 로드한 architecture-ddd 스킬의 절을 근거로 인용한다.

## 경계

- 코드·명세를 수정하지 않는다(읽기 전용).
- 계약(상태코드·멱등성)·데이터(인덱스·트랜잭션) 관심사는 각각 api/db 리뷰어의 몫 — 그쪽으로 넘기고 도메인에 집중한다.
- 스코프를 넓히는 권고를 하지 않는다 — 스코프 의문은 발견으로만 올린다.
```

- [ ] **Step 2: frontmatter 구조 확인**

Run: `rg -n '^(name|description|tools|skills):' dddjango/agents/design-review-ddd.md`
Expected: 네 필드 모두 출력.
Run: `rg -n '^\s+- architecture-ddd$' dddjango/agents/design-review-ddd.md | wc -l`
Expected: `1` (단일 lens 스킬만).

- [ ] **Step 3: critic은 읽기 전용 — Write/Bash/Edit 없음 확인**

Run: `rg -n '^tools:' dddjango/agents/design-review-ddd.md`
Expected: `tools: Read, Grep, Glob` (Write·Bash·Edit 미포함). critic 원형은 노트만 내므로 쓰기 도구 없음.

- [ ] **Step 4: 사전로드 스킬 실재 확인**

Run: `test -f dddjango/skills/architecture-ddd/SKILL.md && echo "ok"`
Expected: `ok`.

---

### Task 3: 플러그인 검증 + 커밋 + 템플릿 확정

- [ ] **Step 1: plugin validate (에이전트 2개 인식)**

Run: `claude plugin validate ./dddjango --strict`
Expected: 통과(에러 없음). 경고가 나오면 내용을 기록하고 frontmatter/구조를 교정. (스킬 10개 + 에이전트 2개가 함께 검증됨.)

- [ ] **Step 2: 두 원형 차이 한눈 확인 (회귀 방지용 대조)**

Run: `rg -n '^tools:' dddjango/agents/design-architect.md dddjango/agents/design-review-ddd.md`
Expected: architect는 `Write` 포함, design-review-ddd는 `Read, Grep, Glob`만. producer ↔ critic 도구 차이가 드러나야 한다.

- [ ] **Step 3: 커밋**

```bash
git add dddjango/agents/design-architect.md dddjango/agents/design-review-ddd.md
git commit -m "$(cat <<'EOF'
Add dddjango agent pilot (producer + critic archetypes)

design-architect(producer 원형)와 design-review-ddd(critic 원형) 2개로
에이전트 파일 템플릿 2종을 확정한다. frontmatter skills: 리스트로 SKILL.md
사전로드, producer는 Write 보유·critic은 읽기 전용. claude plugin validate
--strict 통과.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 4: 템플릿 확정 메모**

확정된 agent 파일 템플릿 = **producer**(frontmatter: `name`/`description`/`tools`(쓰기 도구 포함)/`skills`(다중) + 본문 `## 입력`·`## 산출`·`## <작성물>에 담는 것`·필요 시 `## 리뷰 반영·충돌 중재`·`## 경계`) / **critic**(frontmatter: `tools`(읽기 전용)/`skills`(단일) + 본문 `## 입력`·`## 산출`(노트 형식)·`## 점검 항목`·`## 경계`). `model`은 생략(세션 상속).

**복제 규칙 — 템플릿은 *형태 가이드*이지 verbatim 복사가 아니다(전파 사고 방지):**
- `tools`/`skills`는 **역할별로 다르다**. design-architect의 `tools`(Read·Grep·Glob·Write)는 producer 중 *가장 좁은* 집합이다 — 그대로 복사하면 안 된다. acceptance-tester는 `Bash`가, coder는 `Edit`+`Bash`가 추가로 필요하다(테스트 실행·코드 편집). 각 에이전트의 `tools`/`skills`는 아래 Next의 역할별 명세를 따른다.
- `## 리뷰 반영·충돌 중재` 섹션은 **design-architect 전용**이다(설계 리뷰어 충돌 중재는 architect만 함 — 설계 스펙 §4). acceptance-tester·coder는 이 섹션을 **생략**하고, 자기 역할 고유 섹션(인수 테스트 작성 규칙 / TDD 루프)으로 대체한다.
- "이건 템플릿이니 복제 시 빼라" 같은 메타 주석은 **agent 파일 본문에 넣지 않는다** — agent 파일은 런타임 시스템 프롬프트라 실행 중 노이즈가 된다. 복제 가이드는 이 계획서에만 둔다.

**critic 복제 — design-review-{api,db}는 복사본, discipline-reviewer는 변종이다:**
- `design-review-api`·`design-review-db`는 design-review-ddd의 **거의 기계적 복사**다. 바꾸는 것: `name`·`description`·`skills`(단일 lens 스킬)·`## 입력`의 lens 단어·`## 점검 항목`(lens 체크리스트)·`## 경계`의 hand-off 대상. 골격(읽기 전용·노트만·단일 관심·심각도 어휘·"이상 없음" 명시·다중 발견 정렬)은 그대로.
- `discipline-reviewer`는 **복사본이 아니라 변종**이다(설계 스펙 §4). critic 골격(읽기 전용·노트만·심각도 어휘·"이상 없음")만 공유하고 다음을 새로 쓴다: ① `## 입력` = 설계 명세가 아니라 **코드+테스트**를 받는다("구현 코드를 보지 않는다" 절은 반전 — 코드를 보는 게 본업), ② Phase 2(구현)가 주 무대, ③ **적응형 감사 빈도**(기본 G2 직전 1회, 슬라이스 많으면 슬라이스마다 + 마지막 홀리스틱 — §4) 명시, ④ `skills: discipline-cleancode + discipline-tdd`, ⑤ 체크리스트 = TDD 준수·클린코드·테스트 행위중심·인수↔단위 중복/누락. → design-review-ddd를 그대로 복사하지 말 것.

이 두 템플릿을 나머지 5개 에이전트에 복제한다(다음 계획).

---

## Next (이 계획 이후, 별도 계획서)

1. **critic 복제 3개** — producer/critic 템플릿으로:
   - `design-review-api.md` (skill `architecture-api`; 점검: 계약 완전성·상태코드·에러형식·멱등성·버전·하위호환).
   - `design-review-db.md` (skill `architecture-db`; 점검: 인덱스·제약·트랜잭션 격리·마이그레이션 안전).
   - `discipline-reviewer.md` (skills `discipline-cleancode`+`discipline-tdd`; 입력=코드+테스트; 점검: TDD 준수·클린코드·테스트 행위중심·인수↔단위 중복/누락; 적응형 빈도 §4; 읽기 전용).
2. **producer 복제 2개**:
   - `acceptance-tester.md` (skills `implementation-test`+`architecture-api`+`architecture-ddd`+`discipline-tdd`; `tools: Read, Grep, Glob, Write, Bash`; 산출: 실패하는 인수 테스트; 블랙박스·구현 안 봄 §10 바깥 루프).
   - `coder.md` (skills `implementation-django`+`-django-ninja`+`-django-web`+`-python`+`-test`+`discipline-tdd`+`discipline-cleancode`; `tools: Read, Grep, Glob, Edit, Write, Bash`; 단위 TDD Red→Green→Refactor; 인수 테스트 통과가 완료 조건 §10 안쪽 루프; 잘못된 인수 테스트는 임의 수정 말고 보고 §9).
3. **command** — `commands/dddjango.md` Coordinator(게이트 G0/G1/G2·진행 트래커 §6·subagent 오케스트레이션·수정 모드 §7).
4. **plugin.json 보강** — 필요한 메타 추가.
5. **AGENTS.md 재작성** — 삭제된 plan/validator/Codex 참조 제거, Claude 전용 파이프라인 기준.
6. **통합 스모크** — 장난감 Django 프로젝트에서 `/dddjango` 단계·게이트 실행 관찰.
