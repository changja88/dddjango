# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 정체

이 저장소는 **`dddjango` Claude Code 플러그인**의 소스 트리다. Python/Django 개발 컨벤션(DDD, 아키텍처 패턴, DB 설계, API 설계)을 스킬·커맨드로 패키징한 것.

레이아웃:

```
.claude-plugin/plugin.json     -- 플러그인 메타 (name, version, description, repository)
commands/                      -- 슬래시 커맨드 5개 (api, feature, refactor, test, web)
skills/                        -- 스킬 11개 (architecture-*, implementation-*)
  └─ <skill>/
      ├─ SKILL.md              -- 진입점 (frontmatter + 본문)
      ├─ references/*.md       -- 지연 로딩되는 상세 문서
      └─ evals/evals.json      -- (일부 스킬) 평가 시드
workspace/                     -- 작업 보조 자료 + 검증 산출물 (배포 패키지에 미포함)
```

## 빌드/테스트

이 플러그인은 마크다운/JSON 자산이라 빌드 단계가 없다. "테스트"는 스킬 응답을 평가하는 워크플로우다:

- 스킬 단위 A/B 평가: `workspace/<skill>/test/iteration-N/<tc>/{with_skill,without_skill}/{outputs/output.md, grading.json, timing.json}`. `grading.json`의 `expectations[].passed`로 합격을 판정한다.
- 통합 검증: `workspace/test/{final-validation, cross-skill-test, korean-validation, command-test}/.../GRADING.md`. 합격/불합격을 표 형태로 정리한다.
- 새 evaluation을 돌릴 때는 기존 iteration 옆에 `iteration-N/`을 새로 만들고 같은 프롬프트를 두 조건(스킬 ON/OFF)으로 비교한다.

로컬 설치/검증은 `claude plugin install` 또는 마켓플레이스 sync 후 캐시(`~/.claude/plugins/cache/dddjango/`)에서 로드되는지 확인한다.

## 스킬 작성 컨벤션

### 진입점(`skills/<name>/SKILL.md`)

frontmatter는 다음을 포함한다 -- description은 트리거 키워드를 한국어/영어 모두 포함한 자연어로 길게 쓴다(undertrigger 방지).

```yaml
---
name: <skill-name>
description: >
  <어떤 상황에 어떤 동사로 트리거되는지 + 무엇을 다루고 무엇을 위임하는지 + 금지 패턴이 있다면 명시>
---
```

본문은 짧게 진입만 두고 상세 컨벤션·코드 예제는 `references/<topic>.md`로 분리한다. SKILL.md에 "어떤 주제에서 어떤 reference를 언제 읽는지" 로딩 규칙을 명시한다.

### 모드 분리

스킬은 트리거 동사로 모드를 결정한다:

| 동사 | 모드 | 의미 |
|---|---|---|
| "설계해줘" | Design | 결정/원칙/구조 산출. 코드 미생성. |
| "만들어줘", "작성해줘", "구현해줘" | Writing | 실행 가능한 코드 생성. |
| "리뷰해줘" | Review | 기존 코드에 대한 컨벤션 위반 지적. |
| "리팩터링해줘" | Refactoring | `[Before] / [After] / [Reason]` 포맷의 변경 제시. |

각 모드별로 reference 로딩 규칙이 다르다(예: Writing은 "코드 생성 직전 읽기", Review는 "결과 확정 전 인용한 컨벤션의 reference 읽기").

### 응답 구조

스킬 출력은 한국어로 작성한다. 본문 컨벤션을 인용할 때는 `[Convention: <한 줄 요약>] -- <상세 내용>` 형식. 이 플러그인의 기존 SKILL.md를 표준 템플릿으로 참고한다.

### 스킬 간 위임

각 스킬은 책임을 명확히 분리하고 frontmatter description에 위임 관계를 적는다. 예:

- `implementation-django-ninja` → API 설계 원칙은 `architecture-api`, Django 코어는 `implementation-django`
- `architecture-api` → 구현은 `implementation-django-ninja`
- `architecture-ddd` → 데이터 스키마는 `architecture-db`, 구현 패턴은 `architecture-implementation-patterns`

위임 관계는 `workspace/skill-hierarchy.md`에 전체가 정리되어 있다.

### 금지 패턴(중요)

- **DRF(Django REST Framework) 사용 금지** -- 모든 API는 Django Ninja로 작성. DRF Serializer/ViewSet/APIView/permission_classes를 발견하면 Ninja 패턴으로 전환 권고. 이 정책은 `architecture-api`, `implementation-django`, `implementation-django-ninja`의 description과 본문 양쪽에 명시되어 있고 평가에서도 검증된다.

## 커맨드 작성 컨벤션

`commands/<name>.md`는 사용자가 `/dddjango:<name>`으로 호출하는 슬래시 커맨드다. frontmatter:

```yaml
---
description: <한 줄 설명>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion
---
```

본문은 단계별 절차를 적고 각 단계마다 "어떤 스킬을 어떤 모드로 따른다"를 명시한다. 분기(예: TDD 여부 질문)·사용자 확인 시점·스킬 로딩 순서도 적는다. `commands/feature.md`가 가장 풍부한 예시.

## workspace 디렉토리 사용 규칙

`workspace/`는 **개발 보조 자료 + 검증 산출물 보관소**이지 플러그인 패키지의 일부가 아니다. 배포 시 제외된다(별도 packaging이나 .gitignore에서 처리).

분류:

- `workspace/<skill>/reference/{external,final,internal,review}.md` -- 스킬 작성 시 참고한 외부 자료, 내부 정리, 최종 종합, 검토 노트. 스킬을 수정·확장할 때 먼저 읽으면 맥락 파악이 빠르다.
- `workspace/<skill>/test/iteration-N/...` -- 스킬별 A/B 평가 산출물(과거 iteration 누적).
- `workspace/test/{final-validation, cross-skill-test, korean-validation, command-test}/...` -- 통합 검증 산출물. `GRADING.md`가 PASS/FAIL 표.
- `workspace/skill-hierarchy.md` -- 11개 스킬의 레벨 분류와 위임 관계 정리. 스킬 간 책임을 정할 때 참조.

## 작업 시 알아둘 점

- **plugin.json의 `repository`** -- `https://github.com/changja88/dddjango`로 설정되어 있다. 실제 GitHub repo가 아직 만들어지지 않았다면 만든 뒤 push하거나, 다른 owner/이름이라면 이 값을 수정한다.
- **응답 언어** -- 사용자 답변과 스킬 출력 모두 한국어. `workspace/test/korean-validation/`이 이를 검증한다.
- **새 스킬을 만들 때** -- 먼저 `workspace/skill-hierarchy.md`에서 책임 분리·위임 관계를 정하고, 기존 SKILL.md 한 개를 템플릿으로 복사해 시작한다. frontmatter description의 트리거 키워드 정밀도가 invocation 정확도를 좌우하므로, 작성 후 description optimization(skill-creator의 `run_loop.py`)을 돌려보는 것이 안전하다.
- **금지 패턴 수정 시** -- DRF 정책처럼 "이 패턴은 쓰지 말 것"을 추가/변경할 때는 description과 본문 양쪽에 명시하고, 평가 assertion에도 반영해 회귀를 막는다.
