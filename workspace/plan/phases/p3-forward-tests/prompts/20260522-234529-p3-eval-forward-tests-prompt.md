# P3 Forward-Test Prompt Set

## Metadata

| field | value |
|---|---|
| work item id | `20260522-234529-p3-eval-forward-tests` |
| phase | `p3-forward-tests` |
| source prompt basis | `workspace/plan/phases/p1-5-usage-cards/cards/20260522-230605-p1-5-skill-usage-cards-evidence.md` |
| prompt selection | one happy prompt and one exclusion prompt per high-risk trigger family |
| prompt safety rule | pass only the `forward-test prompt` text to runtime; do not pass expected trigger, expected route, prior conclusion, suspected bug, or intended fix |

## Forward-Test Matrix

| case id | family | kind | matrix target | expected route for observation only | forward-test prompt |
|---|---|---|---|---|---|
| `p3-ft-01-happy-api-contract` | REST API contract | happy | `architecture-api` | `architecture-api` | `주문 생성 API URL, status code, 에러 응답, Idempotency-Key 계약을 정리해줘.` |
| `p3-ft-01-exclusion-api-to-ninja` | REST API contract | exclusion | `architecture-api` | `implementation-django-ninja` | `Django Ninja Router랑 Schema 코드를 바로 만들어줘.` |
| `p3-ft-02-happy-db-integrity` | Relational DB integrity and rollout | happy | `architecture-db` | `architecture-db` | `쿠폰 중복 사용을 DB에서 막으려면 unique constraint랑 transaction을 어떻게 잡아야 해?` |
| `p3-ft-02-exclusion-db-to-ddd` | Relational DB integrity and rollout | exclusion | `architecture-db` | `architecture-ddd` | `Order aggregate가 어떤 불변식을 가져야 하는지 모델링해줘.` |
| `p3-ft-03-happy-ddd-invariants` | Domain modeling and invariants | happy | `architecture-ddd` | `architecture-ddd` | `환불 도메인에서 어떤 상태 전이와 불변식을 aggregate로 묶어야 할지 잡아줘.` |
| `p3-ft-03-exclusion-ddd-to-db` | Domain modeling and invariants | exclusion | `architecture-ddd` | `architecture-db` | `orders 테이블 정규화와 foreign key를 설계해줘.` |
| `p3-ft-04-happy-patterns-outbox` | Implementation architecture patterns | happy | `architecture-implementation-patterns` | `architecture-implementation-patterns` | `결제 승인 후 재고 차감과 알림 발송을 outbox로 분리할지 서비스에서 바로 호출할지 판단해줘.` |
| `p3-ft-04-exclusion-patterns-to-ddd` | Implementation architecture patterns | exclusion | `architecture-implementation-patterns` | `architecture-ddd` | `쿠폰 정책의 ubiquitous language와 aggregate를 먼저 찾아줘.` |
| `p3-ft-05-happy-cleancode-fat-model` | Maintainability review and refactor | happy | `implementation-cleancode` | `implementation-cleancode` | `이 fat model을 더 읽기 쉽게 리팩터링해줘. 동작은 바꾸면 안 돼.` |
| `p3-ft-05-exclusion-cleancode-to-patterns` | Maintainability review and refactor | exclusion | `implementation-cleancode` | `architecture-implementation-patterns` | `결제와 재고를 outbox로 분리하는 아키텍처 결정을 내려줘.` |
| `p3-ft-06-happy-django-migration` | Django ORM, services, migrations, transactions | happy | `implementation-django` | `implementation-django` | `Django 모델에 주문 상태를 추가하고 안전한 migration 순서까지 반영해줘.` |
| `p3-ft-06-exclusion-django-to-api` | Django ORM, services, migrations, transactions | exclusion | `implementation-django` | `architecture-api` | `POST /orders API 응답 status code와 에러 포맷을 설계해줘.` |
| `p3-ft-07-happy-ninja-router` | Django Ninja API implementation | happy | `implementation-django-ninja` | `implementation-django-ninja` | `Django Ninja로 주문 생성 Router, request/response Schema, TestClient 테스트를 만들어줘.` |
| `p3-ft-07-exclusion-ninja-to-api` | Django Ninja API implementation | exclusion | `implementation-django-ninja` | `architecture-api` | `API URL, status code, header 정책만 먼저 정리해줘.` |
| `p3-ft-08-happy-web-template` | Django server-rendered web | happy | `implementation-django-web` | `implementation-django-web` | `주문 상세 Django 템플릿 페이지를 만들고 권한 체크까지 넣어줘.` |
| `p3-ft-08-exclusion-web-to-ninja` | Django server-rendered web | exclusion | `implementation-django-web` | `implementation-django-ninja` | `주문 목록 JSON API에 pagination을 넣어줘.` |
| `p3-ft-09-happy-python-typing` | Python language and typing implementation | happy | `implementation-python` | `implementation-python` | `이 함수에 Python 3.12 타입 힌트를 제대로 넣고 None 처리도 좁혀줘.` |
| `p3-ft-09-exclusion-python-to-django` | Python language and typing implementation | exclusion | `implementation-python` | `implementation-django` | `Django QuerySet 성능을 select_related로 고쳐줘.` |
| `p3-ft-10-happy-tdd-list` | TDD workflow | happy | `implementation-tdd` | `implementation-tdd` | `쿠폰 할인 정책을 TDD로 진행할 테스트 목록부터 잡아줘.` |
| `p3-ft-10-exclusion-tdd-to-test` | TDD workflow | exclusion | `implementation-tdd` | `implementation-test` | `factory_boy fixture와 pytest mock 구조만 만들어줘.` |
| `p3-ft-11-happy-test-fixture` | pytest and Django test mechanics | happy | `implementation-test` | `implementation-test` | `pytest fixture랑 factory_boy로 주문 테스트 데이터를 정리해줘.` |
| `p3-ft-11-exclusion-test-to-tdd` | pytest and Django test mechanics | exclusion | `implementation-test` | `implementation-tdd` | `이 기능을 TDD로 어떤 순서로 개발할지 테스트 목록을 짜줘.` |
| `p3-ft-12-happy-source-audit` | Source and reference governance | happy | `source-reference-audit` | `source-reference-audit` | `각 skill이 어떤 reference를 근거로 삼는지 provenance gap을 점검해줘.` |
| `p3-ft-12-exclusion-source-to-workflow` | Source and reference governance | exclusion | `source-reference-audit` | `workflow-dddjango-subagents` | `subagent 역할 분담으로 결제 기능 작업 계획을 세워줘.` |
| `p3-ft-13-happy-workflow-roles` | Coordinated dddjango workflow | happy | `workflow-dddjango-subagents` | `workflow-dddjango-subagents` | `주문 결제 기능을 DDD, DB, API, 테스트 역할로 나눠서 진행 계획을 세워줘.` |
| `p3-ft-13-exclusion-workflow-to-source` | Coordinated dddjango workflow | exclusion | `workflow-dddjango-subagents` | `source-reference-audit` | `reference final.md 출처와 provisional 상태를 감사해줘.` |

## Runtime Prompt Template

Use this template for each runtime invocation:

```text
<forward-test prompt>
```

Do not append expected route, scoring criteria, previous P1/P2 conclusions, suspected routing bug, or intended fix.
