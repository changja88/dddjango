# dddjango Workflow

이 문서는 `dddjango` 작업이 어떤 순서로 사고되고 통합되어야 하는지 정의한다. 개별 스킬의 trigger 문서가 아니라, dddjango 작업으로 들어온 뒤의 흐름 문서다.

## 1. 기본 흐름

1. 요청의 도메인 복잡도를 판단한다.
2. 도메인 규칙, 상태 전이, 정책, 불변식이 있으면 DDD 판단을 먼저 한다.
3. 하위 도메인 유형과 바운디드 컨텍스트를 정한다.
4. 컨텍스트 맵과 컨텍스트 간 관계 패턴을 정한다.
5. 유비쿼터스 언어를 정리한다.
6. 애그리거트, 값 객체, 유스케이스, 트랜잭션 경계를 정한다.
7. 필요한 구현 아키텍처 패턴을 선택한다.
8. DB, API, Django/Python 구현으로 매핑한다.
9. 테스트 전략을 정하고 구현 또는 리뷰한다.
10. diff, 테스트 결과, 로그, 리뷰 findings로 검증한다.

## 2. 작업 유형별 흐름

| 유형 | 기준 | 흐름 |
|---|---|---|
| 단순 작업 | 도메인 규칙이 거의 없고 변경 범위가 작음 | 관련 implementation/quality 기준만 적용 |
| DDD 작업 | 상태 전이, 정책, 불변식, 도메인 용어가 중요함 | `architecture-ddd` 판단 후 구현 매핑 |
| 복합 작업 | DDD, DB, API, Django, 테스트 중 여러 관점이 얽힘 | 역할 분해 후 통합 |
| 위험 작업 | 위험 도메인 명사와 상태 전이, 트랜잭션, 스키마, API, 테스트 영향이 함께 있음 | 역할 분해와 검증 우선 |
| 리뷰 작업 | 기존 설계/코드의 문제를 찾는 작업 | findings 우선, 심각도와 근거 명시 |

역할 분해는 다음 중 하나일 때 적용한다.

- DDD, DB, API, Django, 테스트, 리팩터링 중 둘 이상의 책임 영역이 실제로 얽혀 있다.
- 사용자가 subagent 실행, 역할 분해, 병렬 검토, 책임 분배를 명시적으로 요청한다.
- 주문, 결제, 재고, 예약, 환불, 권한, ledger 같은 위험 도메인 명사가 상태 전이, 트랜잭션, 스키마, API 계약, 테스트 영향과 함께 나타난다.

단순 단일 파일 수정, 작은 필드 rename, 짧은 설명 요청, 이미 도메인 계약이 확정된 작은 구현에는 전체 역할 분해를 강제하지 않는다. 사용자가 `subagent 계획은 필요 없어`처럼 opt-out을 명시하면 전체 역할 분해를 출력하지 않는다.

## 3. 역할 분해

복합 작업에서는 다음 역할을 사용한다.

| 역할 | 책임 | 관련 skill |
|---|---|---|
| Coordinator | 작업 범위, 역할 배분, 결과 통합 | `workflow-dddjango-subagents` |
| Domain Agent | 하위 도메인, 컨텍스트, 언어, 애그리거트, 불변식, 도메인 이벤트 | `architecture-ddd` |
| Architecture Agent | 구현 패턴, 의존성 방향, port/adapter, transaction boundary | `architecture-implementation-patterns` |
| DB Agent | 스키마, 제약조건, 인덱스, 트랜잭션, rollout constraints, backfill/index-lock risk | `architecture-db`, 필요 시 `implementation-django` |
| API Agent | REST 계약, status code, Problem Details, OpenAPI | `architecture-api`, `implementation-django-ninja` |
| Django Agent | ORM, service, selector, concrete migration files, transaction, settings/security/performance, web template/static | `implementation-django`, `implementation-django-web`, `implementation-python` |
| Test Agent | TDD 흐름, pytest, fixture, test double, API/integration tests, `tests/**` 파일 소유 | `implementation-tdd`, `implementation-test` |
| Review Agent | 코드 품질, 설계 위험, 누락 검증, regressions | `implementation-cleancode` |

이 표는 runtime `workflow-dddjango-subagents` role map의 canonical source다. runtime `SKILL.md`와 `references/role-map.md`로 옮길 때 역할명, 책임 범위, 관련 skill을 임의로 줄이지 않는다. 특히 Django Agent가 `web template/static` 책임을 가진다면 `implementation-django-web`을 반드시 포함한다.

Domain Agent의 판단이 DB Agent, API Agent, Django Agent, Test Agent의 기준이 된다.

## 4. Sequential Fallback

subagent를 사용할 수 없거나 사용하지 않는 경우에도 역할 순서는 유지한다.

순차 실행은 다음 순서를 따른다.

1. Domain
2. Architecture
3. DB
4. API
5. Django
6. TDD/Test
7. Review
8. Integration

단순 작업에서는 이 전체 순서를 강제하지 않는다.

## 5. Handoff Contract

역할 간 전달은 다음 필드를 포함한다.

- Scope
- Inputs Used
- Decisions
- Files
  - May edit
  - Must not edit
- Output
- Risks
- Required Follow-up
- dddjango Checks

결정한 내용과 결정하지 않은 내용은 `Decisions`에 둔다. 다음 역할이 반드시 확인해야 할 질문은 `Required Follow-up`에 둔다.

## 6. 통합 우선순위

충돌이 있으면 다음 순서로 판단한다.

1. 도메인 불변식
2. 데이터 일관성
3. 트랜잭션과 보안
4. API 계약과 하위 호환성
5. 테스트 가능성
6. Django/Python 관용구
7. 이름과 스타일

## 7. Integration Checklist

복합 workflow의 최종 통합에는 다음 항목을 포함한다.

- Domain and invariants: 도메인 불변식, 상태 전이, ubiquitous language가 구현/테스트/API와 충돌하지 않는지 확인한다.
- Data and transaction: DB constraint, transaction boundary, locking/idempotency, migration rollout risk를 확인한다.
- API contract: Django Ninja Router/Schema, status code, Problem Details, OpenAPI 영향, DRF 신규 구현 금지를 확인한다.
- Implementation mapping: domain logic이 router/view에 들어가지 않고 Django service/selector/model 경계와 맞는지 확인한다.
- Tests and verification: domain rule, API contract, migration risk에 대한 테스트 또는 실행하지 못한 검증 명령을 명확히 남긴다.
- Role handoff closure: 각 역할의 `Risks`와 `Required Follow-up`이 통합 결정에 반영됐는지 확인한다.
- Cache sync report: workspace 밖 plugin cache를 수정했다면 cache 경로, 대응되는 workspace canonical source 위치, 검증 실행/미실행 상태를 함께 보고한다. `workflow-dddjango-subagents` role map 변경은 `workspace/docs/workflow.md`의 역할명, 책임 범위, related skills가 runtime/cache에서 축소되지 않았는지 확인한다.

## 8. Reference Loading

reference는 필요한 것만 읽는다.

스킬 폴더를 생성하기 전에는 `workspace/reference`의 source reference와 `workspace/docs`를 읽는다. runtime skill을 생성한 뒤에는 각 `SKILL.md`에서 직접 링크한 `dddjango/skills/<skill>/references/*.md`를 읽는다. runtime `SKILL.md`에는 workspace-only source path를 최종 reference 경로처럼 남기지 않는다.

| 상황 | 생성 전 authoring source | 생성 후 runtime bundled reference |
|---|---|
| 도메인 경계/모델링 | `workspace/reference/architecture-ddd/reference/final.md` | `dddjango/skills/architecture-ddd/references/strategic-design.md`, `context-map.md`, `tactical-patterns.md` |
| 구현 아키텍처 패턴 | 전용 source reference 필요. 임시로 `architecture-ddd`, `implementation-django`, `implementation-python` source reference를 조합 | `dddjango/skills/architecture-implementation-patterns/references/*.md`; provisional이면 표시 필요 |
| DB schema/transaction/index | `workspace/reference/architecture-db/reference/final.md` | `dddjango/skills/architecture-db/references/*.md` |
| REST 계약/API 오류 | `workspace/reference/architecture-api/reference/final.md` | `dddjango/skills/architecture-api/references/*.md` |
| Django ORM/migration/service | `workspace/reference/implementation-django/reference/final.md` | `dddjango/skills/implementation-django/references/*.md` |
| Django Ninja Router/Schema/API 구현 | 전용 source reference 필요. 임시로 `architecture-api`와 제품 결정을 조합. DRF section은 신규 구현에 사용하지 않음 | `dddjango/skills/implementation-django-ninja/references/*.md`; provisional이면 표시 필요 |
| Django template/static/web | 전용 source reference 필요. 임시로 Django source reference의 template/static/view 부분만 사용 | `dddjango/skills/implementation-django-web/references/*.md`; provisional이면 표시 필요 |
| Python typing/dataclass/protocol | `workspace/reference/implementation-python/reference/final.md` | `dddjango/skills/implementation-python/references/*.md` |
| TDD 흐름 | `workspace/reference/implementation-tdd/reference/final.md` | `dddjango/skills/implementation-tdd/references/*.md` |
| pytest/mock/factory | `workspace/reference/implementation-test/reference/final.md` | `dddjango/skills/implementation-test/references/*.md` |
| 리팩터링/리뷰 | `workspace/reference/implementation-cleancode/reference/final.md` | `dddjango/skills/implementation-cleancode/references/*.md` |
| 역할 분해/handoff | `workspace/docs/workflow.md` | `dddjango/skills/workflow-dddjango-subagents/references/*.md` |

## 9. 검증 방식

완료 판단은 실제 산출물을 기준으로 한다.

- 테스트 실행 결과
- lint/typecheck 결과
- diff
- 로그
- 실행 출력
- 리뷰 findings

실행하지 않은 검증은 실행하지 않았다고 말한다.
