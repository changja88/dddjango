# dddjango 빌드 파일럿 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 플러그인 스캐폴드(`plugin.json`)와 대표 스킬 1개(`implementation-django`)의 `SKILL.md`를 `final.md`에서 변환·검증해, 나머지 9개 스킬에 복제할 **SKILL.md 포맷을 확정**한다.

**Architecture:** SKILL.md = 간결한 운영 본문(트리거 description + 사용 시점 + 핵심 원칙 + 주제→절 TOC, ≤500줄). 기존 `final.md`는 `references/final.md`로 번들(점진적 공개). 검증은 `claude plugin validate`.

**Tech Stack:** Claude Code 로컬 플러그인 (`.claude-plugin/plugin.json`, `skills/<name>/SKILL.md`), Markdown + YAML frontmatter. (규격: code.claude.com, Claude Code 2.1.143+)

---

## 파일 구조

- Create: `dddjango/.claude-plugin/plugin.json` — 플러그인 매니페스트(최소)
- Create: `dddjango/skills/implementation-django/SKILL.md` — 운영 본문
- Create: `dddjango/skills/implementation-django/references/final.md` — `workspace/reference/implementation-django/reference/final.md`에서 번들(P1 메모 제거)

**확정 산출물(재사용):** 이 파일럿이 확정하는 *SKILL.md 템플릿*(frontmatter 규칙 + 본문 3섹션 구조)이 나머지 9개 복제의 기준이 된다.

---

### Task 1: 플러그인 스캐폴드 (plugin.json)

**Files:**
- Create: `dddjango/.claude-plugin/plugin.json`

- [ ] **Step 1: plugin.json 작성**

```json
{
  "name": "dddjango",
  "displayName": "dddjango",
  "version": "0.1.0",
  "description": "DDD 방식으로 Django 기능을 설계·구현하는 오케스트레이터. /dddjango로 요구→설계→구현(TDD)을 단계별 게이트로 빌드한다.",
  "author": { "name": "changja88", "email": "dev@numchida.com" },
  "license": "MIT"
}
```

- [ ] **Step 2: JSON 유효성 확인**

Run: `python3 -c "import json,sys; json.load(open('dddjango/.claude-plugin/plugin.json')); print('valid')"`
Expected: `valid`

- [ ] **Step 3: 커밋**

```bash
git add dddjango/.claude-plugin/plugin.json
git commit -m "Add dddjango plugin manifest scaffold"
```

---

### Task 2: 대표 스킬 references 번들

**Files:**
- Create: `dddjango/skills/implementation-django/references/final.md`

- [ ] **Step 1: 디렉터리 생성 + final.md 복사**

```bash
mkdir -p dddjango/skills/implementation-django/references
cp workspace/reference/implementation-django/reference/final.md \
   dddjango/skills/implementation-django/references/final.md
```

- [ ] **Step 2: 빌드 과정 메모(`## P1 Source Sufficiency`) 제거**

`dddjango/skills/implementation-django/references/final.md`를 열어 파일 맨 앞의 `## P1 Source Sufficiency` 섹션을 삭제한다(다음 섹션 `## 목차` 직전까지). `## 목차` 이후 본문(§1~§17)은 그대로 둔다.

- [ ] **Step 3: 번들 확인**

Run: `rg -c '^## [0-9]' dddjango/skills/implementation-django/references/final.md`
Expected: `17` (§1~§17 보존)
Run: `rg -n 'P1 Source Sufficiency' dddjango/skills/implementation-django/references/final.md || echo "removed"`
Expected: `removed`

---

### Task 3: SKILL.md 운영 본문 작성

**Files:**
- Create: `dddjango/skills/implementation-django/SKILL.md`

- [ ] **Step 1: SKILL.md 작성 (frontmatter + 본문 3섹션)**

```markdown
---
name: implementation-django
description: Django 코어 구현 지식 — 모델·ORM·QuerySet/Manager, 마이그레이션, 서비스·셀렉터 레이어, 트랜잭션 경계, 설정·미들웨어·캐싱·보안·시그널, 트랜잭셔널 outbox 구현. dddjango 파이프라인의 코더·설계 역할이 Django 코어 코드를 설계·작성할 때 로드한다. 표현계층(템플릿/폼/HTMX)은 implementation-django-web, JSON API는 implementation-django-ninja로 위임.
user-invocable: false
---

# Django 코어 구현

## 언제 쓰나

Django 코어(모델·ORM·서비스 레이어·트랜잭션·설정·마이그레이션·시그널·캐싱·보안) 코드를 설계·작성할 때 로드한다. 경계:

- 서버렌더 표현계층(뷰=어댑터·템플릿·웹폼·HTMX/CSRF) → `implementation-django-web`
- JSON API 어댑터(Router/Schema) → `implementation-django-ninja`
- 도메인 전략·애그리거트·도메인이벤트 채택 → `architecture-ddd`
- DB 신뢰성·인덱스·트랜잭션 격리·outbox 전달 보장 → `architecture-db`
- Python 관용구 → `implementation-python`, 클린코드 원칙 → `discipline-cleancode`

## 핵심 운영 원칙

- 비즈니스 로직은 fat model + service/selector에, 뷰·시리얼라이저는 얇게 (§4.1, §16)
- 서비스 레이어 도입 시점과 HackSoft service/selector 패턴 (§16.1–§16.2)
- 트랜잭션·일관성 경계는 `transaction.atomic()`, 외부 부수효과는 `transaction.on_commit()` (§16.4)
- 메시지 유실이 불가하면 트랜잭셔널 outbox로 구현 (§16.5 — 채택 기준 `architecture-ddd` §3.7, 전달 보장 `architecture-db` §9.7)
- QuerySet 최적화·N+1 방지는 selector/QuerySet 메서드로 (§5, §11.1)
- 마이그레이션은 안전·무중단 순서 준수 (§10)
- 설정은 환경별 분리, 직접 접근 주의 (§3.3–§3.4)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 설계 철학 | §1 |
| 코딩 스타일·임포트 순서 | §2 |
| 프로젝트/앱/설정 분리 | §3 |
| 모델 설계 (fat model·상속·필드·검증) | §4 |
| QuerySet과 Manager | §5 |
| 뷰·폼 (→ `implementation-django-web` 위임) | §6–§7 |
| 기존 DRF 유지보수 | §8 |
| 시그널 가이드라인 | §9 |
| 마이그레이션 베스트 프랙티스 | §10 |
| 성능 최적화 (N+1·인덱스) | §11 |
| 캐싱 전략 | §12 |
| 보안 | §13 |
| 테스트 패턴 | §14 |
| 미들웨어 | §15 |
| 서비스 레이어·트랜잭션·outbox | §16 |
| Django 5.x 새 기능 | §17 |

전체 깊이는 [`references/final.md`](references/final.md)를 직접 참조한다.
```

- [ ] **Step 2: 본문 분량 확인 (≤500줄)**

Run: `wc -l dddjango/skills/implementation-django/SKILL.md`
Expected: 100줄 미만 (운영 본문이므로 여유 있게 통과)

- [ ] **Step 3: frontmatter·참조 링크 확인**

Run: `rg -n '^(name|description|user-invocable):' dddjango/skills/implementation-django/SKILL.md`
Expected: 세 필드 모두 출력
Run: `test -f dddjango/skills/implementation-django/references/final.md && echo "ref ok"`
Expected: `ref ok`

---

### Task 4: 플러그인 검증

- [ ] **Step 1: validate 실행**

Run: `claude plugin validate ./dddjango --strict`
Expected: 통과(에러 없음). 경고가 나오면 내용을 기록하고 frontmatter/구조를 교정.

- [ ] **Step 2: 수동 로드 확인 (사용자 단계)**

Run: `claude --plugin-dir ./dddjango`
세션에서 `/` 입력 → `implementation-django` 스킬이 로드되는지 확인(또는 `claude --debug`로 로딩 로그 확인). `user-invocable: false`이므로 슬래시 메뉴에 안 보일 수 있다 — 그 경우 `--debug` 로딩 로그 또는 `/agents` 라이브러리로 플러그인 인식 여부만 확인.

---

### Task 5: 커밋 + 포맷 확정

- [ ] **Step 1: 커밋**

```bash
git add dddjango/skills/implementation-django/
git commit -m "Add implementation-django skill (pilot: SKILL.md format)"
```

- [ ] **Step 2: 포맷 확정 메모**

확정된 SKILL.md 템플릿 = ① frontmatter(`name`, `description` 트리거 문구, `user-invocable: false`) + ② 본문 3섹션(`언제 쓰나`=경계, `핵심 운영 원칙`=요약 불릿, `상세 레퍼런스`=주제→절 TOC) + ③ `references/final.md` 번들(P1 메모 제거). 이 템플릿을 나머지 9개 스킬에 복제한다(다음 계획).

---

## Next (이 계획 이후, 별도 계획서)

1. **스킬 9개 복제** — 위 템플릿으로 나머지 9개 SKILL.md + references 생성·검증.
2. **에이전트 7개** — `agents/*.md` (frontmatter `name`/`description` + `skills:` 사전로드 + `tools`). 설계 architect, 설계 리뷰어 ddd/api/db, acceptance-tester, coder, discipline-reviewer.
3. **커맨드** — `commands/dddjango.md` Coordinator(게이트·진행 트래커·subagent 호출).
4. **매니페스트 보강** — plugin.json에 필요한 메타 추가.
5. **AGENTS.md 재작성** — 삭제된 plan/validator/Codex 참조 제거, Claude 전용 파이프라인 기준.
6. **통합 스모크** — 장난감 Django 프로젝트에서 `/dddjango` 단계·게이트 실행 관찰.
