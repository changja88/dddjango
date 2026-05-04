# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 정체

이 저장소는 **`dddjango` Claude Code + OpenAI Codex 듀얼 플랫폼 플러그인**의 소스 트리다. Python/Django 개발 컨벤션(DDD, 아키텍처 패턴, DB 설계, API 설계)을 공통 스킬과 Claude용 커맨드로 패키징한다.

레이아웃:

```
.claude-plugin/plugin.json     -- Claude Code 플러그인 메타
.claude-plugin/marketplace.json -- Claude Code marketplace 메타
.codex-plugin/plugin.json      -- OpenAI Codex 플러그인 메타
.agents/plugins/marketplace.json -- Codex repo-local marketplace
commands/                      -- Claude Code 슬래시 커맨드 5개 (api, feature, refactor, test, web)
skills/                        -- Claude/Codex 공통 스킬 11개 (architecture-* 4개, implementation-* 7개)
  └─ <skill>/
      ├─ SKILL.md              -- 진입점 (frontmatter + 본문)
      ├─ references/*.md       -- 본문 섹션이 가리키는 상세 문서 (지연 로딩)
      └─ evals/evals.json      -- (일부 스킬) 평가 시드
workspace/                     -- 작업 보조 자료 + 평가 산출물 (배포 패키지 외 영역)
```

## 평가 워크플로

이 플러그인은 마크다운/JSON 자산이라 빌드 단계가 없다. "테스트"는 스킬 응답을 평가하는 작업이다.

- 스킬 단위 A/B 평가: `workspace/<skill>/test/iteration-N/<tc>/{with_skill,without_skill}/{outputs/output.md, grading.json, timing.json}`. `grading.json`의 `expectations[].passed`로 합격을 본다. `timing.json`은 token/duration 비교용.
- 통합 검증: `workspace/test/{final-validation, cross-skill-test, korean-validation, command-test}/.../GRADING.md`. 합격/불합격을 표 형태로 정리한다.
- 새 evaluation을 추가할 때는 기존 iteration 옆에 `iteration-N+1/`을 만들고 같은 프롬프트를 두 조건(스킬 ON/OFF)으로 비교한다.
- 듀얼 플랫폼 릴리스 전에는 Claude Code와 Codex에서 같은 대표 프롬프트를 실행해 한국어 응답, DRF 금지, Django Ninja 사용, DDD/계층 분리를 확인한다.

## 플랫폼 패키징 원칙

- `skills/`는 Claude Code와 Codex가 공유하는 단일 원천이다. 플랫폼별 차이를 이유로 스킬 파일을 복제하지 않는다.
- Claude Code 표면은 `.claude-plugin/plugin.json`과 `commands/`를 포함한다.
- Codex 표면은 `.codex-plugin/plugin.json`과 `.agents/plugins/marketplace.json`를 포함한다.
- `.claude-plugin/plugin.json`과 `.codex-plugin/plugin.json`의 `version`은 같은 릴리스에서 항상 동일하게 유지한다.
- `.claude-plugin/marketplace.json`의 plugin entry version도 같은 릴리스 버전으로 맞춘다.
- Codex에는 slash command가 주 진입점이 아니므로, 사용 예시는 `.codex-plugin/plugin.json`의 `interface.defaultPrompt`와 README에 반영한다.

## 스킬 작성 컨벤션

### 진입점(`skills/<name>/SKILL.md`)

frontmatter는 다음 형식. 트리거 키워드를 한국어/영어 모두 길게 적는다(undertrigger 방지).

```yaml
---
name: <skill-name>
description: >
  <어떤 상황에 어떤 동사로 트리거되는지 + 무엇을 다루고 무엇을 위임하는지 + 금지 패턴이 있다면 명시>
---
```

YAML 폴드 스칼라(`description: >`)를 쓴다. 자연어 description을 여러 줄로 나누어 가독성을 살리는 형태다.

### 본문 ↔ reference 매칭

본문은 SKILL.md 안에 짧게 두고 상세 컨벤션·코드 예제는 `references/<topic>.md`로 분리한다. 본문은 번호 매긴 섹션(예: `## 1. URL 설계`)으로 나누고, 각 섹션 끝에 다음 한 줄을 둔다:

```markdown
> Reference: `references/<topic>.md`
```

섹션과 reference 파일은 1:1로 매칭한다. SKILL.md 상단에 모드별 reference 로딩 규칙을 명시한다(예: 작성 시 → 코드 생성 직전, 리뷰 시 → 결과 확정 전, 리팩터링 시 → 변경 제시 전).

### 모드

스킬은 트리거 동사로 모드를 결정한다. 카테고리별로 기본 모드가 다르다.

**`architecture-*` 스킬** — 본문 한국어 표기(영어 별칭 괄호):

| 트리거 동사 | 모드 | 산출 |
|---|---|---|
| "설계해줘" | **설계** (Design) | 결정/원칙/구조. 코드 미생성. |
| "리뷰해줘" | **리뷰** (Review) | 기존 설계의 컨벤션 위반 지적. |
| "리팩터링해줘" | **리팩터링** (Refactoring) | `[Before] / [After] / [Reason]` 포맷의 변경 제시. |

**`implementation-*` 스킬** — 본문 한국어 표기(영어 별칭 괄호):

| 트리거 동사 | 모드 | 산출 |
|---|---|---|
| "만들어줘", "작성해줘", "구현해줘" | **작성** (Writing) | 실행 가능한 코드. |
| "리뷰해줘" | **리뷰** (Review) | 컨벤션 위반 지적. |
| "리팩터링해줘" | **리팩토링** (Refactoring) | `[Before] / [After] / [Reason]`. |

각 SKILL.md 본문에는 `## 운영 모드` 섹션을 두고 모드 선택 규칙(모호 시 기본값, 다중 모드 처리 순서)을 적는다. `architecture-api/SKILL.md`가 표준 예시.

### 응답 구조

스킬 출력은 한국어로 작성한다. 본문 컨벤션을 인용할 때는 `[Convention: <한 줄 요약>] -- <상세 내용>` 형식. 응답 첫 섹션은 `## [주요 내용]`으로 시작한다.

### 스킬 간 위임

각 스킬은 책임을 분리하고 frontmatter description에 위임 관계를 적는다. 예:

- `implementation-django-ninja` → API 설계 원칙은 `architecture-api`, Django 코어는 `implementation-django`
- `architecture-api` → 구현은 `implementation-django-ninja`
- `architecture-ddd` → 데이터 스키마는 `architecture-db`, 구현 패턴은 `architecture-implementation-patterns`

전체 위임 지도는 `workspace/skill-hierarchy.md`에 정리되어 있다. 새 스킬을 추가하거나 기존 책임을 옮길 때 이 파일을 먼저 갱신한다.

### 금지 패턴

- **DRF(Django REST Framework) 사용 금지** — 모든 API는 Django Ninja로 작성한다. DRF Serializer/ViewSet/APIView/`permission_classes`를 발견하면 Ninja 패턴으로 전환을 권고한다. 이 정책은 `architecture-api`, `implementation-django`, `implementation-django-ninja`의 description과 본문 양쪽에 명시되어 있고 평가에서도 검증된다.

## 커맨드 작성 컨벤션

`commands/<name>.md`는 Claude Code 사용자가 호출하는 슬래시 커맨드다. frontmatter는 한 줄 description + 도구 목록:

```yaml
---
description: <한 줄 설명>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
---
```

본문은 단계별 절차를 적고 각 단계마다 "어떤 스킬을 어떤 모드로 따른다"를 명시한다. 분기(예: TDD 여부 질문), 사용자 확인 시점, 스킬 로딩 순서도 적는다.

**모드 표기**: 커맨드 본문은 영어 모드명을 사용한다(예: ``architecture-ddd 스킬의 **Design** 모드를 따른다``). 같은 모드를 가리킬 때 SKILL.md 본문은 한국어("설계 모드"), 커맨드 본문은 영어("Design 모드")로 갈리는 점에 유의한다. 새 커맨드를 추가할 때 이 표기 일관성을 깨지 않는다.

`commands/feature.md`가 가장 풍부한 예시(전체 단계, 분기, 다중 스킬 로딩 포함).

## workspace 디렉토리 사용 규칙

`workspace/`는 **개발 보조 자료 + 평가 산출물 보관소**이지 플러그인 패키지의 일부가 아니다. 추후 `.skill` 패키징 시 별도 처리가 필요한 영역이다.

분류:

- `workspace/<skill>/reference/{external, internal, review, final}.md` — 스킬 작성 시 참고한 외부 자료, 내부 정리, 검토 노트, 최종 종합. **단수 `reference/`**. (스킬 내부의 `references/`는 복수.)
- `workspace/<skill>/test/iteration-N/...` — 스킬별 A/B 평가 산출물(과거 iteration 누적).
- `workspace/test/{final-validation, cross-skill-test, korean-validation, command-test}/...` — 통합 검증 산출물. `GRADING.md`가 PASS/FAIL 표.
- `workspace/skill-hierarchy.md` — 11개 스킬의 레벨 분류와 위임 관계 정리.

스킬을 수정·확장할 때는 해당 스킬의 `workspace/<skill>/reference/`를 먼저 훑으면 작성 당시 맥락 파악이 빠르다.

### 디렉토리 단·복수

| 위치 | 표기 | 용도 |
|---|---|---|
| `skills/<skill>/references/*.md` | **복수** | SKILL.md가 인용하는 지연 로딩 문서 |
| `workspace/<skill>/reference/*.md` | **단수** | 스킬 작성 당시의 작업 자료(외부/내부/리뷰/최종) |

다른 의미이므로 혼용하지 않는다.

## 작업 시 알아둘 점

- **응답 언어** — 사용자 답변과 스킬 출력 모두 한국어. `workspace/test/korean-validation/`이 이를 검증한다.
- **새 스킬을 만들 때** — `workspace/skill-hierarchy.md`에서 책임 분리·위임 관계를 먼저 정하고, 기존 SKILL.md 한 개를 템플릿으로 복사해 시작한다. frontmatter description의 트리거 키워드 정밀도가 invocation 정확도를 좌우하므로, description 후보를 여러 안 써 두고 비교한다.
- **금지 패턴 추가/수정 시** — DRF 정책처럼 "이 패턴은 쓰지 말 것"을 추가하거나 변경할 때는 description과 본문 양쪽에 명시하고, 평가 assertion에도 반영해 회귀를 막는다.
- **위임 관계 변경 시** — 한 스킬의 책임이 바뀌면 (1) 양쪽 SKILL.md frontmatter description, (2) `workspace/skill-hierarchy.md`, (3) 영향받는 commands를 같이 갱신한다.
