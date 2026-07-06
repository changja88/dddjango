---
name: implementation-test
description: 테스트 코드 작성법 종합 지식 — 테스트 전략·피라미드, 테스트 더블 분류, pytest 구조·픽스처·심화 설정·마커·플러그인, Mock·테스트더블 실전, Property-Based Testing(Hypothesis), 팩토리(factory_boy+Faker), 시간 모킹, HTTP 모킹, Docker 통합 테스트, 커버리지, 멀티환경 테스트, 테스트 코드 품질 원칙·안티패턴, Mutation Testing, BDD pytest-bdd, Django Ninja TestClient API 계약 테스트, Idempotency·동시성 테스트, 테스트 디버깅. 테스트 코드·픽스처·테스트더블·계약 검증 코드를 새로 작성하거나 리팩터링할 때 먼저 로드한다. TDD 실천(Red-Green-Refactor 등 방법론)은 discipline-tdd, Django 코어 특화 구현은 implementation-django, JSON API 어댑터 특화는 implementation-django-ninja, 서버렌더 특화는 implementation-django-web으로 위임.
user-invocable: false
---

# 테스트 코드 작성법 종합

## 언제 쓰나

테스트 코드·픽스처·더블·factory·계약 검증·커버리지·Mutation·BDD·동시성 테스트 코드를 설계·작성할 때 로드한다. 경계:

- TDD 방법론(언제·왜 테스트를 먼저 쓰는가, Red-Green-Refactor) → `discipline-tdd`
- Django 모델·ORM·서비스 레이어 구현 → `implementation-django`
- Django Ninja Router/Schema·TestClient 계약 어댑터 구현 → `implementation-django-ninja`
- Django 뷰·템플릿·폼·HTMX 구현 → `implementation-django-web`

## 핵심 운영 원칙

- 행동을 증명하는 가장 작은 테스트 범위를 선택; 피라미드 하단일수록 빠르고 안정 (§1)
- 테스트 러너·작성은 **pytest(pytest-django)** 기본 — 함수형 + `assert` + `@pytest.mark.django_db`(DB 접근 명시) + 픽스처 (§3, §4, §19.4)
- 테스트 더블은 역할과 리스크 기준으로 선택: Stub→상태 검증, Mock→상호작용 검증, Fake→가벼운 협력자 (§2, §7.1)
- mock이 필요할 때(외부 경계 한정 — 기존 §7.1 교리 불변)의 **도구는 pytest-mock `mocker` 픽스처**(자동 teardown); raw `unittest.mock` 폴백 금지 (§7)
- **적극적 = 경계에서 수제 대신 전용 도구로 *업그레이드*하는 것이지, 더 많이 *mock·도구 추가*하는 것이 아니다.**
- 픽스처는 명시적·격리적으로 작성, conftest 계층을 활용해 공유 범위 최소화 (§3.7, §4.2)
- 검증은 상태·결과 우선, 화이트박스(내부 구현) 검증 회피 (§7.1, §15.3)
- Hypothesis로 경계값·속성 기반 테스트, @example로 재현 케이스 고정 (§8)
- ORM 영속 픽스처의 기본은 **factory_boy**(만능 아님 — 정확 필드 행·VO/dataclass 직접 생성은 정당); 최소 필요 상태만 지정, DB fixture 최소화 (§9)
- 동시성·idempotency 테스트는 DB 의미론이 필요하면 DB-backed 테스트로 (§20)
- 커버리지 수치보다 의미 있는 assertion이 중요; mutmut로 테스트 유효성 검증 (§13, §17)
- AAA(Arrange-Act-Assert) 패턴으로 테스트 구조 일관화 (§15.2)
- 외부 계약(HTTP 응답·DB 저장값·이벤트) 검증의 assert 기댓값은 리터럴로 — 프로덕션 상수 역수입은 자기참조 오라클; 도메인 내부 단위 테스트의 심볼 단언과 arrange의 심볼 사용은 허용 (§15.4)
- 테스트 안티패턴(복잡한 조건문·프로덕션 로직 재사용·숨겨진 의존성)을 피한다 (§16 — 상수 역수입 오라클은 §15.4)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| 테스트 전략과 피라미드 | §1 |
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
