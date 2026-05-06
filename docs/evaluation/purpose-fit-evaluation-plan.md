# dddjango Purpose-Fit Evaluation Plan

이 문서는 기존 평가 프레임워크를 폐기한 뒤, `dddjango` 플러그인의 목적에 맞게
새 평가 체계를 다시 설계하기 위한 실행 계획이다.

## 평가 목적

`dddjango` 평가는 단순히 답변이 좋아졌는지, 키워드가 몇 개 포함됐는지, 또는
일반 모델 대비 점수가 몇 퍼센트 올랐는지를 보는 테스트가 아니다. 핵심 목적은
다음 질문에 답하는 것이다.

1. Codex가 `dddjango`를 설치했을 때 Django 개발 표준을 더 일관되게 적용하는가?
2. DRF 대신 Django Ninja를 선택하는 정책이 실제 산출물에서 지켜지는가?
3. DDD, DB 설계, 트랜잭션, 테스트, 클린 코드 경계가 코드와 설계에 반영되는가?
4. 한국어 사용자에게 자연스럽고 실행 가능한 방식으로 답하는가?
5. 복합 작업에서 역할 분해와 subagent workflow를 사용할 수 있는가?
6. 스킬 내부 reference가 실제 답변 품질로 이어지는가?
7. 실제 Django 앱 파일 트리와 코드 책임 배치가 dddjango 의도와 맞는가?

## 현재 상태

| 항목 | 상태 | 메모 |
| --- | --- | --- |
| 기존 루트 평가 프레임워크 | 폐기 완료 | 목적과 맞지 않는 lift/키워드 중심 평가 제거 |
| 개별 스킬 내부 `evals/` | 유지 | 새 프레임워크 설계 시 참고만 하고 그대로 복원하지 않음 |
| 새 목적 기반 평가 스펙 | 1차 완료 | 목적, 축, 케이스, gate, calibration 기준 정의 |
| 새 평가 실행기 | 구현 완료 | fixture smoke와 live Codex 비교 실행 지원 |
| HTML 결과 리포트 | 구현 완료 | baseline, without, with 비교표와 gate 결과 생성 |

## 평가 원칙

### 1. 산출물 중심 평가

점수는 답변에 특정 단어가 있는지가 아니라, 실제 개발자가 쓸 수 있는 설계,
코드, 테스트, 리뷰 결과가 나왔는지를 기준으로 매긴다.

### 2. 정책 위반은 fail-fast

아래 항목은 평균 점수와 무관하게 실패로 본다.

| Gate | 실패 조건 |
| --- | --- |
| DRF 금지 | DRF, Serializer, ViewSet, APIView, rest_framework를 권장하거나 생성 |
| Django Ninja 필수 | API 구현/설계 요청에서 Django Ninja Router/Schema 패턴이 없음 |
| 허위 실행 금지 | 실제로 실행하지 않은 테스트, 검증, subagent 수행을 실행했다고 주장 |
| 한국어 우선 | 한국어 요청에 영어 중심 답변으로 대응 |
| 도메인 로직 위치 | 비즈니스 규칙을 router/view/form에 직접 몰아넣음 |
| TDD 순서 | TDD 요청에서 RED 테스트 없이 구현부터 제시 |
| subagent 허위 사용 | subagent를 실제로 쓰지 않았는데 사용했다고 말함 |

### 3. 비교군은 세 가지로 고정

모든 주요 케이스는 가능한 한 같은 프롬프트로 세 변형을 비교한다.

| Variant | 의미 |
| --- | --- |
| `baseline` | 기대 기준. 사람이 정의한 rubric/golden criteria이며 모델 출력이 아님 |
| `without-dddjango` | `dddjango` 없이 같은 요청을 처리한 Codex 출력 |
| `with-dddjango` | `dddjango` 설치/활성화 후 같은 요청을 처리한 Codex 출력 |

HTML 리포트는 각 케이스마다 `baseline`, `without-dddjango`, `with-dddjango`를
한 표에 표시한다. `baseline`은 점수 산정 기준과 필수 조건을 보여주고,
두 실행 결과는 그 기준을 얼마나 만족했는지 비교한다.

### 4. 자동 점수와 사람 검토를 분리

자동 평가는 금지어, 필수 구조, 파일 산출물, 테스트 언급, reference coverage
같은 관찰 가능한 신호를 확인한다. 최종 품질 점수는 rubric 기반 judge 또는
수동 검토가 가능하도록 근거를 함께 남긴다.

## 평가 축

| 축 | 평가 질문 | 대표 신호 |
| --- | --- | --- |
| Trigger Accuracy | 필요한 상황에서 맞는 스킬이 발동되는가? | 스킬명, 관련 스킬 참조, 불필요한 dddjango 오염 없음 |
| DRF Rejection | DRF 요청도 Django Ninja로 전환하는가? | DRF 금지 문구, Ninja 대안 코드, rest_framework 미사용 |
| Django Ninja API | Router, Schema, response mapping, error 표준이 정확한가? | `Router`, `Schema`, status-code response, Problem Details |
| DDD Boundaries | 도메인 경계와 비즈니스 규칙 위치가 적절한가? | bounded context, aggregate, value object, domain service |
| DB/Transaction | 데이터 모델, 제약, 인덱스, 트랜잭션 판단이 타당한가? | uniqueness, FK, transaction boundary, locking/idempotency |
| TDD/Pytest | 테스트 우선 사고와 pytest 품질이 있는가? | RED/GREEN/REFACTOR, 정상/경계/실패/멱등성 테스트 |
| Clean Implementation | 코드가 유지보수 가능한가? | 타입 힌트, 작은 함수, 명확한 예외, 과한 추상화 없음 |
| Project Structure | Django 앱 파일 트리가 의도한 경계를 따르는가? | domain, service/usecase, api schema/router, tests 분리 |
| Review/Refactor | 기존 코드의 문제를 정확히 짚고 개선안을 내는가? | severity, 원칙 연결, 수정 방향, 테스트 보강 |
| Subagent Workflow | 복합 작업을 역할 기반으로 분해하는가? | Role Map, Handoff Contract, Integration Checklist, 순차 실행 fallback |
| Subagent Role Decomposition | 표준 역할과 책임 단위 분해가 정확한가? | Coordinator, Domain/DB/API/Test/Review Agent, 책임 중심 분리 |
| Subagent Skill Mapping | 역할별 dddjango skill 매핑이 맞는가? | `architecture-ddd`, `architecture-db`, `architecture-api`, `implementation-django-ninja`, `implementation-tdd` |
| Subagent Handoff Contract | 역할 산출물 인수인계가 완전한가? | Scope, Inputs Used, Decisions, Files, Output, Risks, Required Follow-up, dddjango Checks |
| Subagent Execution Planning | 병렬/순차 판단과 파일 소유권이 안전한가? | 도메인 계약 선행, 읽기 전용 병렬, disjoint file ownership, 순차 실행 |
| Subagent Integration Verification | 역할 간 충돌을 dddjango 우선순위로 통합하는가? | 도메인 불변식, transaction/idempotency, API contract, test 우선순위 |
| Subagent Claim Integrity | 실제 실행하지 않은 subagent 수행을 주장하지 않는가? | 허위 완료/검토/결과 수신 주장 없음 |
| Reference Usage | 스킬 reference의 구체 규칙이 답변에 반영되는가? | reference coverage matrix, specific convention evidence |
| Usability | 한국어 사용자에게 바로 실행 가능한가? | 명령어, 파일 경로, 검증 고지, 불필요한 설명 없음 |

## 케이스 매트릭스

### Phase 1: 평가 스펙 확정

| ID | 목적 | 산출물 |
| --- | --- | --- |
| P1-01 | dddjango 목적과 평가 축 확정 | 이 문서 |
| P1-02 | fail-fast gate 정의 | `rubrics/gates.md` |
| P1-03 | 점수 schema 정의 | `rubrics/score-schema.json` |
| P1-04 | HTML 리포트 필드 정의 | `reports/report-contract.md` |

### Phase 2: 핵심 정책 케이스

| ID | 케이스 | 주요 평가 축 |
| --- | --- | --- |
| C01 | DRF로 주문 API 만들어 달라는 요청 | DRF Rejection, Django Ninja API |
| C02 | Django Ninja 주문 생성 API 설계 | Django Ninja API, DDD Boundaries, DB/Transaction |
| C03 | 할인 쿠폰 정책을 TDD로 구현 | TDD/Pytest, DDD Boundaries, Clean Implementation |
| C04 | 주문 상태 전이 도메인 모델 설계 | DDD Boundaries, DB/Transaction |
| C05 | 인벤토리 예약/동시성 설계 | DB/Transaction, DDD Boundaries |

### Phase 3: 리뷰/리팩터링 케이스

| ID | 케이스 | 주요 평가 축 |
| --- | --- | --- |
| R01 | fat model/fat view 코드 리뷰 | Review/Refactor, Clean Implementation |
| R02 | DRF ViewSet을 Django Ninja로 전환 | DRF Rejection, Django Ninja API |
| R03 | 테스트 없는 서비스 코드에 TDD 보강 | TDD/Pytest, Review/Refactor |
| R04 | 빈약한 도메인 모델 개선 | DDD Boundaries, Clean Implementation |

### Phase 4: Trigger/Usability 케이스

| ID | 케이스 | 주요 평가 축 |
| --- | --- | --- |
| T01 | 한국어 Django API 요청 | Trigger Accuracy, Usability |
| T02 | FastAPI 요청 | Trigger Accuracy, 불필요한 dddjango 오염 방지 |
| T03 | 일반 Python 리팩터링 요청 | Trigger Accuracy, Clean Implementation |
| T04 | SQL-only 인덱스 질문 | Trigger Accuracy, DB/Transaction |

### Phase 5: Subagent Workflow 케이스

| ID | 케이스 | 주요 평가 축 |
| --- | --- | --- |
| S01 | 복합 주문 기능을 역할 분해로 설계 | Subagent Workflow, Role Decomposition, Skill Mapping, Handoff |
| S02 | 단순 Django 수정에서 subagent ceremony 방지 | Trigger Accuracy, Execution Planning, Claim Integrity |
| S03 | 읽기 전용 병렬 역할 리뷰 | Role Decomposition, Execution Planning, Integration Verification |
| S04 | 같은 파일 충돌의 순차 통합 | Execution Planning, File Ownership, Integration Verification |
| S05 | 허위 subagent 완료 주장 방지 | Claim Integrity, Usability |
| S06 | 역할 간 충돌 통합 우선순위 | Integration Verification, DDD Boundaries, API |

### Phase 6: Reference Maximum Check

| ID | 케이스 | 주요 평가 축 |
| --- | --- | --- |
| M01 | Django Ninja error standard | Reference Usage, Django Ninja API |
| M02 | DDD aggregate boundary | Reference Usage, DDD Boundaries |
| M03 | DB transaction/idempotency | Reference Usage, DB/Transaction |
| M04 | TDD edge cases | Reference Usage, TDD/Pytest |

### Phase 7: Code Structure Check

| ID | 케이스 | 주요 평가 축 |
| --- | --- | --- |
| P01 | 주문 생성 기능 파일 트리와 책임 분리 | Project Structure, Clean Implementation, Django Ninja API |
| P02 | 도메인 코드 품질과 에러 모델 | Clean Implementation, DDD Boundaries, TDD/Pytest, Reference Usage |

## 점수 모델

각 케이스는 100점 만점으로 평가한다.

| 구간 | 의미 |
| --- | --- |
| 0-59 | 목적 미달. dddjango 스킬 가치가 낮거나 정책 위반 가능성이 큼 |
| 60-74 | 부분 충족. 방향은 맞지만 실무 적용에는 보강 필요 |
| 75-84 | 사용 가능. 주요 정책과 산출물이 대체로 안정적 |
| 85-94 | 우수. reference 규칙이 구체적으로 반영되고 실무 품질이 높음 |
| 95-100 | 최대 성능권. 사람이 기대하는 기준에 거의 근접 |

권장 release gate:

| Gate | 기준 |
| --- | --- |
| Critical policy | fail-fast gate 0건 |
| Overall score | `with-dddjango` 평균 80점 이상 |
| Skill value | 주요 케이스의 `with-dddjango - without-dddjango` 평균 +10점 이상 |
| DRF rejection | DRF 관련 케이스 100% 통과 |
| API/TDD core | Django Ninja, DDD, TDD 축 각각 평균 80점 이상 |
| Reference max | maximum check 케이스 평균 85점 이상 |
| Code structure quality | Clean Implementation, Project Structure 평균 80점 이상 |

`+15% quality lift`는 보조 지표로만 사용한다. 목적 기반 평가에서는 절대 점수와
정책 gate가 더 중요하다.
자동 signal만 있는 live 결과는 `pass`가 아니라 `needs_review`가 될 수 있으며,
artifact 수동/judge 검토가 완료되어야 release 판단으로 사용할 수 있다.

## 리포트 요구사항

평가를 실행할 때마다 로컬 HTML 리포트를 생성한다.

필수 표:

1. Summary table: 전체 평균, gate 통과 여부, release 판단.
2. Variant comparison: 케이스별 `baseline`, `without-dddjango`, `with-dddjango`.
3. Dimension table: 평가 축별 평균 점수.
4. Fail-fast gate table: 실패 조건과 근거.
5. Reference coverage table: 어떤 reference 규칙이 어느 답변에 반영됐는지.
6. Artifact links: 원본 prompt, output, score, judge rationale.

HTML 리포트는 브라우저에서 바로 읽을 수 있어야 하며, markdown artifact를 클릭해도
평문만 보이는 문제가 없도록 HTML 변환본을 함께 제공한다.

## 구현 순서

| 순서 | 작업 | 결과물 |
| --- | --- | --- |
| 1 | 평가 스펙 문서 확정 | `docs/evaluation/purpose-fit-evaluation-plan.md` |
| 2 | rubric/gate 파일 작성 | `evals/dddjango/rubrics/` |
| 3 | 케이스 정의 파일 작성 | `evals/dddjango/cases/` |
| 4 | baseline criteria 작성 | `evals/dddjango/baselines/` |
| 5 | runner 설계 | `evals/dddjango/scripts/run_evaluation.py` |
| 6 | scorer 설계 | `evals/dddjango/scripts/score_outputs.py` |
| 7 | HTML report generator 작성 | `evals/dddjango/scripts/render_report.py` |
| 8 | Makefile에 최소 명령 추가 | `make eval-dddjango`, `make eval-report` |
| 9 | dry-run 샘플 실행 | 1-2개 케이스만 검증 |
| 10 | 전체 평가 실행 | HTML 결과와 score JSON 생성 |
| 11 | 결과 기반 스킬 개선 | fail-fast 또는 낮은 축부터 수정 |
| 12 | 재평가 | 개선 전/후 리포트 비교 |

## 진행 체크리스트

- [x] 기존 목적 부적합 평가 폐기
- [x] 새 평가 목적 정의
- [x] 평가 축 초안 작성
- [x] fail-fast gate 초안 작성
- [x] phase별 케이스 매트릭스 작성
- [x] HTML 리포트 요구사항 정의
- [x] rubric/gate 파일 구현
- [x] 케이스 JSON 구현
- [x] baseline criteria 구현
- [x] runner/scorer/reporter 구현
- [x] dry-run 실행
- [x] fixture가 아닌 live 실행 경로 구현
- [ ] fixture가 아닌 live 전체 평가 실행
- [ ] 결과 분석 및 스킬 개선

## 다음 결정

다음 작업은 코드를 바로 작성하기보다, 이 계획을 기준으로 평가 구현 단위를
고정하는 것이다. 권장 순서는 다음과 같다.

1. `evals/dddjango/rubrics/`부터 구현한다.
2. 핵심 정책 케이스 C01-C05만 먼저 만든다.
3. HTML 리포트를 최소 기능으로 먼저 만든다.
4. dry-run 결과를 보고 케이스 수를 늘린다.
