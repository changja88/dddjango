# AGENTS.md

이 저장소는 일반 Django 애플리케이션이 아니라, Python/Django 개발 표준을 Claude Code 플러그인 형태로 패키징하는 `dddjango` 소스 트리다. 핵심 산출물은 Django, DDD, DB 설계, API 설계, 테스트, 클린 코드 관련 스킬과 슬래시 커맨드다.

## 저장소 정체

- 플러그인 이름: `dddjango`
- 메타데이터: `.claude-plugin/plugin.json`
- 목적: Python/Django 개발 컨벤션을 Claude Code 스킬과 커맨드로 제공
- 기준 기술: Python, Django 5.x, Django Ninja, pytest, DDD, REST API, RDB 설계
- 금지 정책: DRF(Django REST Framework) 사용 금지. API 구현은 Django Ninja 기준으로 안내한다.

## 주요 디렉터리

```text
.claude-plugin/
  plugin.json              # 플러그인 메타데이터
commands/
  api.md                   # Django Ninja API 개발 커맨드
  feature.md               # 신규 기능 전체 개발 커맨드
  refactor.md              # 코드 리팩터링 커맨드
  test.md                  # 테스트 작성 커맨드
  web.md                   # Django 웹 페이지 개발 커맨드
skills/
  architecture-*           # 설계/원칙 중심 스킬
  implementation-*         # 구현/코드 패턴 중심 스킬
workspace/
  skill-hierarchy.md       # 스킬 계층과 위임 관계
  <skill>/reference/       # 스킬 작성 당시 참고 자료
  <skill>/test/            # 스킬 평가 산출물
```

## 스킬 구성

Architecture 계열은 "무엇을 어떻게 설계할지"를 다룬다.

- `architecture-ddd`: 바운디드 컨텍스트, 애그리거트, 엔티티, 값 객체, 도메인 이벤트
- `architecture-implementation-patterns`: 헥사고날, 클린/어니언 아키텍처, CQRS, 이벤트 소싱, Repository, Unit of Work
- `architecture-db`: 관계형 DB 모델링, 정규화, 인덱스, 트랜잭션, 쿼리 최적화
- `architecture-api`: REST 리소스, URL, HTTP 메서드, 상태 코드, 에러 포맷, 페이지네이션, 버저닝

Implementation 계열은 "코드로 어떻게 작성할지"를 다룬다.

- `implementation-cleancode`: 네이밍, 함수, SOLID, 리팩터링, 복잡도 관리
- `implementation-python`: Python 3.10+ 관례, 타입 힌트, dataclass, async, Ruff
- `implementation-django`: Django 5.x 모델, ORM, QuerySet, 설정, 보안, 서비스 레이어
- `implementation-django-ninja`: Django Ninja Schema, Router, 인증, 페이지네이션, 에러 처리
- `implementation-django-web`: Django 템플릿, 정적 파일, 디자인 시스템, TemplateView, HTMX
- `implementation-tdd`: Red-Green-Refactor, TDD 방식, 테스트 우선 개발
- `implementation-test`: pytest, fixture, mock, factory, HTTP/time mocking, coverage, 통합 테스트

## 작업 규칙

- 모든 사용자 응답은 기본적으로 한국어로 작성한다.
- 스킬 또는 커맨드를 수정할 때는 관련 `SKILL.md`와 `references/*.md`의 연결을 유지한다.
- `skills/<skill>/SKILL.md`는 짧은 진입점이며, 상세 규칙은 `skills/<skill>/references/*.md`로 분리한다.
- `workspace/<skill>/reference/`는 스킬 작성 당시의 참고 자료이고, `skills/<skill>/references/`는 실제 스킬이 지연 로딩하는 문서다. 단수/복수 디렉터리를 혼동하지 않는다.
- 새 스킬이나 책임 변경이 있으면 `workspace/skill-hierarchy.md`, 관련 `SKILL.md` frontmatter, 영향을 받는 `commands/*.md`를 함께 갱신한다.
- DRF 금지처럼 중요한 정책을 추가하거나 바꿀 때는 스킬 description, 본문, 평가 assertion을 함께 갱신한다.
- 사용자가 Django API를 요청하면 Django Ninja를 기준으로 설계/구현한다.

## 커맨드 작성 규칙

`commands/*.md`는 Claude Code 슬래시 커맨드 문서다.

- frontmatter에는 `description`과 `allowed-tools`를 둔다.
- 본문에는 단계별 절차, 로드할 스킬, 적용 모드, 사용자 확인 시점을 명시한다.
- 커맨드 본문에서는 모드를 영어로 표기한다. 예: `Design`, `Writing`, `Review`, `Refactoring`.
- `commands/feature.md`가 가장 종합적인 예시다.

## 평가와 검증

이 저장소는 마크다운/JSON 자산 중심이라 별도 빌드 단계가 없다. 검증은 스킬 응답 평가 산출물로 관리한다.

- 스킬별 A/B 평가: `workspace/<skill>/test/iteration-N/...`
- 통합 검증: `workspace/test/.../GRADING.md`
- 평가 결과는 `grading.json`의 `expectations[].passed`, `timing.json`의 토큰/시간 데이터를 함께 본다.
- 새 평가를 추가할 때는 기존 iteration 옆에 `iteration-N+1/` 구조를 만든다.

## 현재 상태 참고

- 루트에 `config.toml`은 없다. 기존 안내가 `config.toml`을 가리키더라도 현재 코드베이스 기준의 실제 지침 파일은 `CLAUDE.md`와 이 `AGENTS.md`다.
- 작업 트리는 수정/미추적 파일이 많은 상태일 수 있다. 기존 변경을 임의로 되돌리지 말고, 요청 범위에 필요한 파일만 다룬다.
- `.idea/`, `.claude/settings.local.json`, Python 캐시와 가상환경은 `.gitignore` 대상이다.
