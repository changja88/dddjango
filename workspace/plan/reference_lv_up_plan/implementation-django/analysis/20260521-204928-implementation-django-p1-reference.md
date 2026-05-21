수정 대상: reference
원인 분류: P1 source reference gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
초기 발견 수: Blocker 0, Major 2, 열린 Minor 1

## 평가 기준

- 대상 reference: `workspace/reference/implementation-django/reference/final.md`
- 대상 skill: `dddjango/skills/implementation-django/`
- 평가 루프: 평가 -> analysis -> plan -> 수정 -> 재평가

## 현재 평가

`implementation-django` source reference는 모델, ORM, QuerySet/Manager, settings, migration, caching, security, performance, Django test acceptance의 기본 판단 근거는 제공한다. 그러나 P1 종료 조건에는 부족한 source gap이 있다.

## Blocker

없음.

## Major

1. Transaction/consistency 근거 부족
   - `final.md`는 `transaction.atomic()`, `transaction.on_commit()`, `select_for_update()`, isolation/retry, idempotency storage, risky write consistency 판단 기준을 독립적으로 다루지 않는다.
   - 현재 skill bundled reference는 해당 내용을 runtime rule로 제공하지만 source reference가 이를 충분히 뒷받침하지 못한다.
   - 허용 claim: migration lock risk와 `TransactionTestCase` 사용 기준은 현재 reference로 말할 수 있다.
   - 금지 claim: risky write의 transaction owner, lock/idempotency, external side-effect timing, retry/isolation 판단 기준이 source reference에 충분히 정리됐다고 말할 수 없다.

2. REST API/DRF boundary 혼선
   - `final.md`의 `Django REST Framework 패턴` 섹션은 DRF Serializer/ViewSet/DefaultRouter를 좋은 예로 제시한다.
   - dddjango runtime routing은 greenfield REST endpoint 구현을 `implementation-django-ninja`로 보내고, `implementation-django`는 Django-side model/ORM/service/migration work를 담당한다.
   - 허용 claim: 기존 DRF 코드 유지보수나 migration review에서 DRF 패턴을 참고할 수 있다.
   - 금지 claim: new API 기본 구현 방식으로 DRF Serializer/ViewSet/DefaultRouter를 권장한다고 말할 수 없다.

## Minor

1. Service layer 도입 기준 중 `모델 파일이 500줄을 넘길 때`는 파일 크기를 단독 기준처럼 보이게 한다.
   - 프로젝트 전역 원칙은 변경 이유, orchestration, transaction, external side effect, 중복 흐름을 기준으로 책임을 나누도록 요구한다.
   - 허용 claim: 모델이 이해하기 어려워지는 경우 service layer를 고려한다.
   - 금지 claim: 500줄 자체가 service layer 도입의 충분조건이라고 말할 수 없다.

## Note

- `settings`, caching, security, performance, middleware, model validation, QuerySet/Manager, migration, integration test acceptance는 현재 reference에 기본 근거가 있다.
- Eval pack 문제는 현재 단계에서 발견하지 않았다.

## Subagent 리뷰/순차 fallback

- 리뷰 방식: real-subagent
- 리뷰 상태: real-subagent 2건 완료. source coverage 충분 판정과 메인 재평가가 일치한다.
- skill-creator 리뷰: DRF boundary가 source에 있고 skill progressive disclosure가 부족하다고 지적했다. source reference 자체의 추가 gap으로 분류하지 않고 skill gap으로 분류했다.
- 독립 P1 리뷰: source coverage는 requested Django areas에 충분하다고 판정했다.

## 재평가

- transaction/consistency source gap은 `final.md`의 `트랜잭션과 일관성 경계` 추가로 닫혔다.
- REST API/DRF boundary 혼선은 `REST API 경계와 기존 DRF 유지보수` 섹션으로 닫혔다.
- service layer 파일 크기 기준 minor는 변경 이유와 orchestration 기준으로 보정해 닫혔다.
- 리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
