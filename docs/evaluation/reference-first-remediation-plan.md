# Reference-First Remediation Plan

dddjango 평가 개선은 점수가 낮은 케이스를 바로 스킬 문구로 보정하지 않는다.
먼저 낮은 점수가 reference 부족, reference 적용력 부족, 평가 기준 불일치,
또는 실제 스킬 품질 문제 중 어디서 발생했는지 분리한다.

## Current Target Cases

기준 run: `workspace/codex-eval/purpose-fit/20260507-151743-002462`

| Case | With score | Lowest dimensions | First diagnosis | Primary action |
| --- | ---: | --- | --- | --- |
| `s06-integration-conflict-resolution` | 60 | `ddd_boundaries=17`, `usability=50`, `subagent_claim_integrity=50` | reference 일부 부족 + 평가가 일반 DDD literal에 과의존 | reference 소폭 보강 + 행위 기반 평가 정렬 |
| `t05-django-template-view` | 75 | `clean_implementation=25` | Django web reference는 있으나 web 전용 clean 기준이 부족함 | web 전용 평가 기준 정렬 + 조건부 response rule 보강 |
| `m02-ddd-aggregate-boundary` | 67 | `usability=0` | `reference_usage=100`, `ddd_boundaries=100`이므로 reference 부족이 아님 | 평가 기준 정렬 |
| `h03-starlette-no-contamination` | 75 | `usability=50` | 비-Django 오염 방지 케이스이며 Starlette reference를 늘리면 목적이 흐려짐 | 평가 기준 정렬 |

## Global Checklist

- [x] 각 케이스마다 reference 부족 여부를 먼저 판정한다.
- [x] reference가 부족한 케이스만 reference 파일을 보강한다.
- [x] reference는 충분하지만 출력에 반영되지 않는 경우 `SKILL.md`의 low-freedom rule을 보강한다.
- [x] reference도 출력도 충분한데 점수가 낮으면 평가 기준을 수정한다.
- [x] non-Django 케이스는 dddjango 지원 범위를 확장하지 않고 오염 방지 기준만 강화한다.
- [x] 수정 후 `skills/`와 `plugins/dddjango/skills/`를 동기화한다.
- [x] 설정 검증과 캘리브레이션을 먼저 통과시킨다.
- [x] 기존 subset live output 재채점으로 4개 케이스를 확인한다.
- [x] subset 산출물을 수동 리뷰해 목적 적합성, 오염 없음, 키워드 패딩 없음,
  실행 가능성을 확인한다.
- [ ] 4개 케이스가 안정화되면 full live 평가를 실행한다.

## Work Tracks

### Track A: Reference 보강 불필요

먼저 진행한다. 이 트랙은 스킬 지식 자체를 늘리지 않고, 평가 기준이 dddjango의
목적을 제대로 측정하도록 정렬한다.

- [x] `m02-ddd-aggregate-boundary`: `reference_usage=100`,
  `ddd_boundaries=100`이 이미 확인되었으므로 usability 평가 기준만 정렬한다.
- [x] `h03-starlette-no-contamination`: Starlette reference를 추가하지 않고,
  non-Django 오염 방지와 실행 가능성 평가만 정렬한다.
- [x] `m02`/`h03` 캘리브레이션 샘플을 추가한다.
- [x] `validate_eval_config.py`와 `run_calibration.py --write-report`를 통과시킨다.
- [x] subset live 평가로 `m02`, `h03`만 확인한다.

Track A result:

- `m02` latest local-marketplace live output 재채점: `93`
  (`reference_usage=100`, `ddd_boundaries=86`, `usability=100`)
- `h03` live output 재채점: `100`
  (`trigger_accuracy=100`, `usability=100`)
- 두 케이스 모두 forbidden hit 없음.

### Track B: Reference 또는 스킬 지침 보강 후보

Track A가 안정화된 뒤 진행한다.

- [x] `s06-integration-conflict-resolution`: reference 소폭 보강이 필요한지 확인하고
  행위 기반 평가 기준을 정렬한다.
- [x] `t05-django-template-view`: 기존 web reference가 충분한지 재확인한 뒤,
  조건부 response rule 또는 web 전용 clean 기준을 정렬한다.
- [x] Track B 변경 후 cross-suite regression을 실행한다.

Track B interim result:

- `s06`은 새 reference를 만들지 않고 기존
  `repositories-services.md`, `domain-events.md`를 reference matrix에 연결했다.
  같은 live output 재채점 기준 `with-dddjango=90`, `without-dddjango=40`.
- `t05`는 reference 보강 없이 GET-only template page 기준으로 평가를 정렬했다.
  같은 live output 재채점 기준 `with-dddjango=100`, `without-dddjango=67`.
  `json_script`와 `csrf`는 JS 데이터 주입 또는 POST/AJAX/HTMX 상태 변경 요청의
  조건부 검토 항목으로 둔다.
- Cross-suite regression 재채점:
  `t02=75/pass`, `t06=100/pass`, `h02=92/pass`, `s05=100/pass`,
  `s04=83/pass`.

## Agent Review Summary

두 독립 리뷰 모두 "계획의 큰 방향은 맞지만 수정 필요"로 판단했다.

- `s06`: `repositories-services.md`, `domain-events.md` 보강은 타당하지만
  `filetree-with-django.md`는 충돌 판단에 과하다. DDD 키워드 전체를 항상
  출력하도록 만들면 keyword stuffing 위험이 있다.
- `t05`: `json_script`, `csrf`를 모든 GET-only template page에 강제하면
  부자연스럽다. 조건부 보안 기준과 web 전용 clean evaluation이 필요하다.
- `m02`: reference 부족이 아니므로 reference를 늘리지 않는다. usability는
  decision/rationale/actionability 그룹으로 평가한다.
- `h03`: Starlette reference를 추가하지 않는다. 비-Django 오염 방지와 실행
  가능성만 평가한다.

이 문서의 target score는 release 판단이 아니라 automatic signal 회귀 확인용이다.
최신 live scores는 모두 `automatic_confidence=low`, `manual_required=true`이므로
subset 후 사람이 산출물을 확인해야 한다.

## S06: Integration Conflict Resolution

### Diagnosis

`s06`은 실제 개선 대상이다. 현재 산출물은 Role Map, Handoff Contract,
Integration Checklist는 잘 만들지만, 충돌 통합 판단에서 DDD reference를 충분히
끌어오지 못한다. 특히 `ddd_boundaries` 점수가 낮고, 실제 subagent를 실행하지
않았다는 claim integrity 문구도 충분히 안정적이지 않다.

### Reference Review

현재 reference matrix:

- `skills/workflow-dddjango-subagents/SKILL.md`
- `skills/workflow-dddjango-subagents/references/integration-checklist.md`
- `skills/workflow-dddjango-subagents/references/role-map.md`
- `skills/architecture-ddd/references/aggregates.md`
- `skills/implementation-django-ninja/references/routing.md`

추가 검토 후보:

- `skills/architecture-ddd/references/repositories-services.md`
- `skills/architecture-ddd/references/domain-events.md`

`filetree-with-django.md`는 이번 충돌 판단에는 직접성이 낮으므로 추가하지 않는다.

### Improvement Plan

- [x] `reference-matrix.json`의 `s06` reference paths에
  `repositories-services.md`, `domain-events.md`만 추가한다.
- [x] `workflow-dddjango-subagents/references/integration-checklist.md`에 충돌
  판단 시 aggregate root, application use case, cross-aggregate side effect가
  있는지 확인하는 항목을 추가한다.
- [x] `workflow-dddjango-subagents/SKILL.md`는 새 키워드 나열 규칙보다 기존
  `Order.confirm()` 직접 상태 변경 금지 규칙을 유지하고, 필요한 경우 한두 줄만
  보강한다.
- [x] `s06` 평가는 일반 DDD literal 전체가 아니라 다음 행위 기반 신호를
  인정하도록 조정한다:
  `Order.confirm()`, 상태 전이, application service/use case 경유, router 직접
  상태 변경 금지, command endpoint, transaction, test impact.
- [x] `값 객체`, `도메인 이벤트`는 있으면 가산할 수 있지만 모든 충돌 판단의
  필수 신호로 강제하지 않는다.
- [x] 실제 subagent를 실행하지 않은 경우 다음 의미를 명확히 포함한다:
  "가정 기반 역할 분해이며 실제 subagent 실행/호출 완료가 아니다."
- [x] API contract는 `PATCH /orders/{id}` status 직접 변경 대신 command endpoint나 application use case를 호출하도록 정리한다.
- [x] DDD 용어만 나열하고 실제 충돌 판단이 없는 답변을 실패시키는 negative
  calibration을 추가한다.

### Validation

```sh
python3 evals/dddjango/scripts/validate_eval_config.py
python3 evals/dddjango/scripts/run_calibration.py --write-report
make eval-dddjango CASE=s06-integration-conflict-resolution VARIANT=with-dddjango
```

Target:

- `gate_status=pass`
- `total_score >= 80`
- `ddd_boundaries >= 80`
- `subagent_claim_integrity >= 80`
- false subagent claim 없음
- manual review: 키워드 나열이 아니라 Domain invariant > API convenience
  충돌 판단이 실제로 설명되어야 함

## T05: Django Template View

### Diagnosis

`t05`는 실제 개선 대상이다. 다만 reference가 없는 것이 아니라,
`implementation-django-web`의 web/template 보안 기준이 일반 페이지 설계 산출물에
안정적으로 반영되지 않고, 평가가 범용 `clean_implementation` structural check에
기대는 문제다.

현재 누락:

- `json_script`
- `csrf`
- clean implementation 구조 신호

### Reference Review

현재 reference matrix:

- `skills/implementation-django-web/SKILL.md`
- `skills/implementation-django-web/references/template-architecture.md`
- `skills/implementation-django-web/references/view-layer.md`
- `skills/implementation-django-web/references/asset-management.md`
- `skills/implementation-django/references/views.md`

추가 reference 파일은 우선 만들지 않는다. 기존 reference 안에 충분한 내용이
있으므로, 먼저 web 전용 평가 기준과 조건부 response rule을 정렬한다.

### Improvement Plan

- [x] `implementation-django-web/SKILL.md`의 기존 template page response rule을 유지하고 평가 기준을 정렬한다.
- [x] 템플릿 기반 페이지 설계 요청이면 다음을 web clean 기준으로 평가한다:
  `{% static %}`, `LoginRequiredMixin`, `context`, `include`, selector/service 분리,
  pagination, N+1 방지, template에 비즈니스 로직 금지, tests.
- [x] `json_script`는 서버 데이터를 JavaScript에 주입할 때 필수로 평가한다.
  GET-only 목록 페이지에서는 "검토 항목"이면 충분하다.
- [x] `csrf`는 POST/AJAX/HTMX/상태 변경 form이 있을 때 필수로 평가한다.
  GET-only 필터 폼에서는 필수로 두지 않는다.
- [x] view/template에 비즈니스 로직을 넣지 않고 selector/service로 분리하는 구조를 명시한다.
- [x] `t05` 평가 기준에 web 전용 clean dimension 또는 alternative structural group을 추가한다.
- [x] 범용 clean structural check의 `Result`, `도메인 예외`, `Enum` 같은
  API/domain 구현 신호가 web/template 케이스를 과도하게 낮추지 않도록 조정한다.
- [x] GET-only 좋은 답변과 POST/HTMX/JS 데이터 주입 답변을 구분하는
  calibration을 추가한다.

### Validation

```sh
python3 evals/dddjango/scripts/validate_eval_config.py
python3 evals/dddjango/scripts/run_calibration.py --write-report
make eval-dddjango CASE=t05-django-template-view VARIANT=with-dddjango
```

Target:

- `gate_status=pass`
- `total_score >= 85`
- `clean_implementation >= 75`
- `{% static %}`, `LoginRequiredMixin`, view/template/context 분리 감지
- POST/AJAX/HTMX/JS 데이터 주입이 있는 샘플에서만 `json_script`, `csrf` 필수 감지
- Django Ninja API 오염 없음
- manual review: GET-only 목록 페이지에 불필요한 boilerplate 보안 문구를
  강제하지 않아야 함

## M02: DDD Aggregate Boundary

### Diagnosis

`m02`는 reference 부족이 아니다. 최신 run에서 `reference_usage=100`,
`ddd_boundaries=100`이다. 낮은 총점은 `usability=0`에서 왔고,
현재 평가 기준이 `판단`, `근거` 같은 일부 단어에 과도하게 의존하기 때문이다.

### Reference Review

현재 reference는 충분하다:

- `skills/architecture-ddd/references/aggregates.md`
- `skills/architecture-ddd/references/bounded-context.md`
- `skills/architecture-ddd/references/domain-events.md`

현재 `reference-matrix.json`의 `m02` reference는 위 3개다. 최신 output과
reference rule은 이미 `reference_usage=100`, `ddd_boundaries=100`을 통과하므로
reference 추가는 하지 않는다.

### Improvement Plan

- [ ] `m02` usability 평가를 사람 기준에 맞게 정렬한다.
- [ ] usability를 단어 목록이 아니라 다음 그룹으로 평가한다:
  decision group: `판단`, `판정`, `결론`, `최종 권고`;
  rationale group: `근거`, `주요 발견`, `불변식`, `경계`;
  actionability group: `점검표`, `검색식`, `검토용 코드`, `권장 경계`.
- [ ] 스킬 본문에는 과도한 키워드 강제 대신 DDD review 답변에서 판단과 근거를 분리하라는 가벼운 지침만 유지한다.
- [ ] reference_usage와 ddd_boundaries가 이미 100인 경우 reference를 늘리지 않는다.
- [ ] `without-dddjango`도 reference_usage가 높게 나온 이유를 기록하고, 이 케이스는
  plugin lift보다 reference-max 목적 적합성 확인용임을 명시한다.
- [ ] DDD 키워드만 나열하고 실제 경계 판단이 없는 답변을 낮게 채점하는
  negative calibration을 추가한다.

### Validation

```sh
python3 evals/dddjango/scripts/validate_eval_config.py
python3 evals/dddjango/scripts/run_calibration.py --write-report
make eval-dddjango CASE=m02-ddd-aggregate-boundary VARIANT=with-dddjango
```

Target:

- `gate_status=pass`
- `total_score >= 85`
- `reference_usage=100`
- `ddd_boundaries=100`
- `usability >= 75`
- manual review: Order/Payment 분리 판단의 근거와 후속 점검이 실제로 유용해야 함

## H03: Starlette No Contamination

### Diagnosis

`h03`은 Starlette 지원 능력 평가가 아니라 non-Django contamination 방지 평가다.
Starlette reference를 추가하면 dddjango가 범용 ASGI/Starlette 플러그인처럼 변할
위험이 있다. 따라서 `t06-flask-no-contamination`과 같은 방식으로 평가 기준을
정렬한다.

### Reference Review

Starlette reference는 추가하지 않는다. 대신 guard paths만 유지한다:

- `skills/architecture-api/SKILL.md`
- `skills/implementation-python/SKILL.md`
- `skills/implementation-test/SKILL.md`

### Improvement Plan

- [ ] `h03` usability 기준을 `검증`, `테스트` 단어 매칭에서 실행 가능성 그룹으로 바꾼다.
- [ ] 실행 가능성은 다음 그룹으로 평가한다:
  install/run group: `pip install`, `uvicorn`, `python -m pip`, `Starlette`;
  request group: `curl`, `POST /orders`, `content-type`;
  response group: `201`, `JSONResponse`, `422`, 오류 응답;
  test direction group: `TestClient`, `pytest`, `검증`, `테스트`.
- [ ] `Starlette만 사용`, `Django 코드 필요 없어`, `ASGI` 같은 scope boundary 표현을 인정한다.
- [ ] forbidden pattern은 실제 오염 패턴으로 좁힌다:
  `from django`, `django.conf`, `from ninja import`, `Django Ninja Router`,
  `관련 스킬 참조`, `dddjango 기준`, `Django app 구조`, `Django ORM`.
- [ ] `Django Ninja`라는 단어 자체는 부정 문맥에서 쓰일 수 있으므로 critical forbidden으로 두지 않는다.
- [ ] `Django Ninja 없이` 같은 부정 문맥은 통과하고, 실제 Django/Ninja 코드는
  실패하는 calibration을 추가한다.

### Validation

```sh
python3 evals/dddjango/scripts/validate_eval_config.py
python3 evals/dddjango/scripts/run_calibration.py --write-report
make eval-dddjango CASE=h03-starlette-no-contamination VARIANT=with-dddjango
```

Target:

- `gate_status=pass`
- `total_score >= 90`
- Django/Ninja/dddjango 오염 없음
- Starlette/ASGI 실행 안내는 유지
- manual review: Starlette 지원 범위 확장이 아니라 non-Django 오염 방지 목적을
  유지해야 함

## Additional Validation Before Full Eval

- [ ] `t05` calibration:
  GET-only template list page는 `json_script`/`csrf` 없이도 통과한다.
- [ ] `t05` calibration:
  POST/HTMX/JS 데이터 주입 template page는 `csrf`/`json_script`가 없으면 낮게 나온다.
- [ ] `s06` calibration:
  `Order.confirm()`/상태 전이/API 우회 금지/service/test를 설명하면 통과한다.
- [ ] `s06` calibration:
  DDD 용어만 나열하고 충돌 판단이 없는 답변은 낮게 나온다.
- [ ] `s06` calibration:
  실제 실행하지 않은 subagent 완료 주장은 계속 실패한다.
- [ ] `m02` calibration:
  `판정`/`최종 권고`/`주요 발견`/`검색식` 구조의 좋은 답변은 통과한다.
- [ ] `m02` calibration:
  `불변식`/`ID`/`도메인 이벤트`만 나열하고 경계 판단이 없는 답변은 낮게 나온다.
- [ ] `h03` calibration:
  Starlette-only runnable answer는 통과한다.
- [ ] `h03` calibration:
  `Django Ninja 없이` 부정 문맥은 critical fail이 아니다.
- [ ] `h03` calibration:
  `from ninja import Router` 또는 Django app/ORM 구조를 끼운 답변은 실패한다.
- [ ] Cross-suite regression:
  `t02-fastapi-no-contamination`, `t06-flask-no-contamination`,
  `h02-keyword-bait-order-design`, `s05-false-subagent-claim`,
  `s04-same-file-conflict-sequential`을 함께 확인한다.
- [ ] Paraphrase holdout:
  `s06`은 cancel/ship, `m02`는 주문/배송, `t05`는 상세/대시보드,
  `h03`은 ASGI endpoint 변형을 최소 1개씩 추가 검토한다.

## Execution Order

1. [x] Track A: `m02` usability 그룹 평가 정렬.
2. [x] Track A: `h03` non-Django contamination 평가 정렬.
3. [x] Track A: `m02`/`h03` calibration 추가/실행.
4. [x] Track A: `m02`/`h03` subset live 평가와 산출물 manual review.
5. [x] Track B: `s06` 행위 기반 평가 정렬 + 필요한 reference만 소폭 보강.
6. [x] Track B: `t05` web 전용 평가 기준 정렬 + 조건부 response rule 보강.
7. [x] calibration과 cross-suite regression 추가/실행.
8. [x] 4개 기존 subset live output 재채점.
9. [x] subset 산출물 manual review.
10. 결과가 안정화되면 full live 평가.

## Stop Conditions

- reference를 추가했는데 산출물이 키워드 나열로 변하면 즉시 되돌리고
  SKILL 본문을 간결하게 조정한다.
- non-Django 케이스에서 Starlette/Flask 지원 범위를 늘리는 방향으로 흐르면 중단한다.
- full evaluation 전에 subset에서 `gate_status=fail`이 남아 있으면 full run을 돌리지 않는다.
