# dddjango 스킬 계층 구조

## 개요

dddjango 플러그인은 Python 코드 작성을 목표로 하며, 스킬을 **설계(architecture)**와 **구현(implementation)** 두 레벨로 구분한다.
두 레벨은 고정된 호출 순서가 아니라, 상황에 따라 **필요한 스킬을 조합**하여 적용한다.

## 레벨 구분

```
architecture-  ← 설계/원칙: "어떻게 설계하고 무엇을 만드는가" (원칙 중심, 코드 예시 최소화)
implementation-  ← 구현: "어떻게 코드로 작성하는가" (구체적 코드 패턴)
```

### Architecture (설계)

구조와 패턴을 **결정**하는 지식. 원칙과 가이드라인 중심.

| 스킬 | 역할 | 상태 |
|------|------|------|
| `architecture-ddd` | 도메인 주도 설계 (전략/전술 패턴) | 완료 |
| `architecture-implementation-patterns` | 아키텍처 구현 패턴 (헥사고날, CQRS, Event Sourcing) | 완료 |
| `architecture-db` | 데이터베이스 설계 | 완료 |
| `architecture-api` | REST API 설계 원칙 | 완료 |

### Implementation (구현)

결정된 설계를 **코드로 구현**하는 지식. 구체적 코드 예시 포함.

| 스킬 | 역할 | 상태 |
|------|------|------|
| `implementation-cleancode` | 클린코드 원칙 | 완료 |
| `implementation-python` | Python 언어 관례 및 패턴 | 완료 |
| `implementation-django` | Django 프레임워크 관례 (모델, ORM, 설정) | 완료 |
| `implementation-django-ninja` | Django Ninja API 구현 (Schema, Router, 인증) | 완료 |
| `implementation-django-web` | Django 웹 프론트엔드 (템플릿, 정적 파일, 디자인 시스템) | 완료 |
| `implementation-tdd` | TDD 개발 방법론 | 완료 |
| `implementation-test` | 테스트 코드 작성법 | 완료 |

## 조합 방식

스킬은 상호 배타적이 아니며, 상황에 따라 필요한 스킬이 **조합**되어 적용된다.

### 예시 1: "신규 주문 기능 만들어줘"
```
architecture-ddd                      ← 도메인 모델 설계
architecture-implementation-patterns  ← 계층 구조 (헥사고날)
architecture-db                       ← DB 스키마 설계
architecture-api                      ← REST API 설계 원칙
implementation-cleancode              ← 클린코드 원칙 적용
implementation-python                 ← Python 관례 적용
implementation-django                 ← Django 관례 적용
implementation-django-ninja           ← Django Ninja API 구현
implementation-tdd                    ← TDD 사이클로 개발
implementation-test                   ← 테스트 코드 작성
```

### 예시 2: "기존 서비스 로직 리팩토링해줘"
```
architecture-ddd         ← 도메인 모델 검토
implementation-cleancode ← 클린코드 원칙으로 리뷰/리팩토링
implementation-python    ← Python 관례 적용
```

### 예시 3: "주문 페이지 만들어줘"
```
implementation-django-web            ← 템플릿, 정적 파일, 디자인 시스템
implementation-django                ← Django 관례 (뷰, 설정)
implementation-cleancode             ← 클린코드 원칙 적용
implementation-python                ← Python 관례 적용
```

### 예시 4: "이 API에 테스트 추가해줘"
```
implementation-tdd       ← TDD 방법론
implementation-test      ← 테스트 코드 작성법
implementation-django    ← Django 테스트 관례
```

## 스킬 공통 역할

모든 스킬은 3가지 모드로 동작한다:
1. **작성**: 코드 작성 시 원칙을 적용 (코드만 출력)
2. **리뷰**: 기존 코드에서 위반 지적 (코드 + 원칙 근거 설명)
3. **리팩토링**: 개선안 제시 (변경 전/후 + 이유 설명)

## 폴더 구조

```
dddjango/
├── .claude-plugin/
│   └── plugin.json
├── workspace/
│   ├── <skill-name>/
│   │   ├── reference/             ← 소스 문서 (internal, external, review, final)
│   │   └── test/                  ← 테스트 결과 (gitignore)
│   └── skill-hierarchy.md         ← 이 문서
└── skills/
    ├── architecture-ddd/                      ← 설계
    ├── architecture-implementation-patterns/
    ├── architecture-db/
    ├── architecture-api/
    ├── implementation-cleancode/              ← 구현
    ├── implementation-python/
    ├── implementation-django/
    ├── implementation-django-ninja/
    ├── implementation-django-web/
    ├── implementation-tdd/
    └── implementation-test/
```

## 설계 결정 사항

- **2레벨 구조**: architecture(설계) + implementation(구현). 라우터 없음
- **조합 방식**: 고정 순서 없이 상황에 따라 필요한 스킬 조합
- **접두어로 레벨 구분**: `architecture-`(설계), `implementation-`(구현)
- **설계는 원칙 중심**: 코드 예시 최소화, 가이드라인과 의사결정 기준 제공
- **구현은 코드 중심**: 구체적 코드 패턴, 좋은 예/나쁜 예 포함
- **3가지 모드**: 모든 스킬이 작성/리뷰/리팩토링 역할 수행
