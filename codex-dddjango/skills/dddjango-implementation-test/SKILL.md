---
name: dddjango-implementation-test
description: 테스트 코드 작성법 종합 지식 — 테스트 전략·피라미드, migration 전용 테스트와 DB-backed 현행 동작 테스트의 기술적 구분, pytest 구조·픽스처·마커·플러그인, Mock·테스트더블, Property-Based Testing, 팩토리, 시간·HTTP 모킹, 통합 테스트, 커버리지, 테스트 품질·안티패턴, Mutation Testing, BDD, mounted Django client API 계약, Idempotency·동시성 테스트, 디버깅. 테스트 코드·픽스처·테스트더블·계약 검증 코드를 새로 작성하거나 리팩터링할 때 먼저 로드한다. 무엇을 테스트하고 기존 테스트를 유지·갱신·분리·삭제할지는 discipline-tdd, Django 구현은 implementation-django 계열로 위임.
---

# 테스트 코드 작성법 종합

## 언제 쓰나

테스트 코드·픽스처·더블·factory·계약 검증·커버리지·Mutation·BDD·동시성 테스트 코드를 작성할 때 로드한다. 이 skill은 `discipline-tdd` §5.5가 영구 테스트 입장 결정을 끝낸 **뒤** `add`·`update`와 명시 승인된 `retain` 의미 보존 재조직의 작성 mechanics만 제공한다. `retain` 재조직은 새 case·assertion·Red를 만들지 않고 전후 같은 보호를 유지한다. 후보나 `reuse`·`reject`를 새 test file·case·assertion·helper 의무로 바꾸지 않는다. 경계:

- TDD 방법론과 테스트 수명 주기(무엇을 검증하고 유지·갱신·분리·삭제하는가) → `discipline-tdd`
- Django 모델·ORM·서비스 레이어 구현 → `implementation-django`
- Django Ninja Router/Schema·mounted public HTTP와 adapter-local client 계약 구현 → `implementation-django-ninja`
- Django 뷰·템플릿·폼·HTMX 구현 → `implementation-django-web`

## 핵심 운영 원칙

- **먼저 `discipline-tdd` §5.5의 decision row를 확인한다.** `add`·`update`와 명시 승인된 `retain` 의미 보존 재조직에만 아래 recipe를 적용한다. `retain` 재조직은 새 case·assertion·Red가 없고, `reuse`·`reject`에서는 test artifact write가 0이다. 피라미드·coverage·속도·도구 예시는 `add`의 근거가 아니다 (§1)
- 입장된 행동을 증명하는 가장 작은 테스트 범위를 선택한다. 유효한 domain/application/DB/adapter/public contract 테스트를 단순히 상위 계층이라는 이유로 낮추거나 생략하지 않는다 (§1)
- migration 파일·번호·과거 state·forward/reverse가 오라클이면 migration 전용 테스트이고, 현재 model·ORM·service·API·DB constraint가 오라클이면 DB-backed 현행 동작 테스트다. 이 절은 기술적으로 식별만 하고 수명 주기는 `discipline-tdd`에 넘긴다 (§1.4)
- 테스트 러너·작성은 **pytest(pytest-django)** 기본 — 함수형 + `assert` + `@pytest.mark.django_db`(DB 접근 명시) + 픽스처 (§3, §4, §19.4)
- 테스트 더블은 역할과 리스크 기준으로 선택: Stub→상태 검증, Mock→상호작용 검증, Fake→가벼운 협력자 (§2, §7.1)
- mock이 필요할 때(외부 경계 한정 — 기존 §7.1 교리 불변)의 **도구는 pytest-mock `mocker` 픽스처**(자동 teardown); raw `unittest.mock` 폴백 금지 (§7)
- **적극적 = 경계에서 수제 대신 전용 도구로 *업그레이드*하는 것이지, 더 많이 *mock·도구 추가*하는 것이 아니다.**
- 픽스처는 명시적·격리적으로 작성, conftest 계층을 활용해 공유 범위 최소화 (§3.7, §4.2)
- 검증은 상태·결과 우선, 화이트박스(내부 구현) 검증 회피 (§7.1, §15.3)
- 승인된 property-based case를 Hypothesis로 표현하고, 승인된 재현 경계는 @example로 고정한다. 도구가 입력을 많이 만들 수 있다는 사실은 새 테스트 근거가 아니다 (§8)
- ORM 영속 픽스처의 기본은 **factory_boy**(만능 아님 — 정확 필드 행·VO/dataclass 직접 생성은 정당); 최소 필요 상태만 지정, DB fixture 최소화 (§9)
- 승인된 동시성·idempotency·CAS case가 DB 의미론을 보호하면 DB-backed mechanics를 쓴다 (§20)
- 승인된 테스트의 유효성을 살필 때 coverage나 mutmut를 진단 도구로 쓸 수 있지만, 수치·생존 mutant 자체가 새 case/assertion 근거는 아니다 (§13, §17)
- AAA(Arrange-Act-Assert), assertion 선택, Free Ride 방지와 테스트 분리는 이미 입장된 case의 가독성 recipe다. 새 case/assertion을 승인하지 않는다 (§3.4, §15.2, §16)
- 외부 계약(HTTP 응답·DB 저장값·이벤트) 검증의 assert 기댓값은 리터럴로 — 프로덕션 상수 역수입은 자기참조 오라클; 도메인 내부 단위 테스트의 심볼 단언과 arrange의 심볼 사용은 허용 (§15.4)
- Django Ninja 오류는 입장된 HTTP mapping만 실제 mount된 Django client로 status/body/승인 header를 검증한다. plugin 기본 오류 schema property 목록은 없고 shape 변경은 별도 명시 사용자 승인이 필요하다. 공개 OpenAPI 계약은 실제 mount된 생성 문서의 관련 operation/status/schema만 검증한다. 별도 승인 또는 실제 consumer evidence가 없는 Pydantic private introspection·framework 기본 직렬화와 error helper/factory/serializer/mapping/handler 내부 unit test는 만들지 않는다. framework 기본 body라도 입장된 public wire 계약이면 consumer가 의존하는 관련 field만 검증한다 (§19.2)
- 발행 이벤트의 union-enum 동기 검증도 자동 세트가 아니라 입장 후 recipe다. 실제 published/wire drift의 독자 failure가 있고 기존 보호가 없을 때만 `add`할 수 있으며, 구조가 서로를 자명하게 반복하면 `reuse`·`reject`한다 (§15.5)
- migration 전용 테스트와 DB-backed 현행 동작 테스트의 식별·수명 주기는 기존 규칙을 그대로 따른다 (§1.4, `discipline-tdd` §5.5)
- 테스트 안티패턴(복잡한 조건문·프로덕션 로직 재사용·숨겨진 의존성)을 피한다 (§16 — 상수 역수입 오라클은 §15.4)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 테스트 전략과 피라미드, migration 전용 테스트 기술 식별 | §1 |
| 테스트 더블 분류 체계 | §2 |
| pytest 기본 구조와 Fixture | §3 |
| pytest 심화 설정 | §4 |
| pytest 마커 시스템 | §5 |
| pytest 플러그인 생태계 | §6 |
| Mock과 테스트 더블 실전 | §7 |
| Property-Based Testing (Hypothesis) | §8 |
| 테스트 데이터 팩토리 (factory_boy + Faker) | §9 |
| 시간 모킹 (freezegun / time-machine) | §10 |
| HTTP 모킹 (responses / aioresponses) | §11 |
| Docker 기반 통합 테스트 (testcontainers) | §12 |
| 커버리지 설정 (coverage.py) | §13 |
| 멀티환경 테스트 (tox / nox) | §14 |
| 테스트 코드 품질 원칙 (외부 계약 기댓값 리터럴 §15.4 포함) | §15 |
| 테스트 안티패턴 | §16 |
| Mutation Testing | §17 |
| BDD pytest-bdd 구현 | §18 |
| Django Ninja TestClient API 계약 테스트 | §19 |
| Idempotency와 동시성 테스트 | §20 |
| 테스트 디버깅 기법 | §21 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
