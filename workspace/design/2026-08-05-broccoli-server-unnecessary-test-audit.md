# Broccoli Server 불필요 테스트 전수 감사

- 작성일: 2026-08-05
- 상태: 조사·원인 분석 기준선 · 플러그인 변경 전 사용자 검토 대기
- 조사 대상: `/Users/hyun/Desktop/broccoli-server`
- 적용 대상: dddjango가 생성·조정하는 테스트 정책
- 관련 정책: [현행 계약 테스트 정책](../plan/2026-07-14-current-contract-test-policy-plan.md)
- 관련 설계: [API 에러 관리 최종 설계](2026-08-03-api-error-management-design.md)

## 1. 목적

`broccoli-server`의 테스트 코드를 전수 조사해 다음을 구분한다.

1. 제품 계약을 보호하지 않는, 사실상 없어도 되는 테스트
2. Python·Django·Pydantic·Django Ninja 자체 동작을 재검증하는 테스트
3. 구현 전 Red를 위해 만들었으나 Green 이후에도 남은 테스트 비계
4. private helper·소스 구조·docstring·테스트 seam에 결합된 테스트
5. 외부 계약과 중복된 내부 Schema·구조 테스트
6. 단순해 보여도 공개 wire·DB·도메인 계약이라 유지해야 하는 테스트
7. 불필요 테스트를 작성하게 만든 생성 원인과 이를 막지 못한 파이프라인 원인

이 문서는 현재 대상을 일괄 삭제하기 위한 명령서가 아니다. dddjango 플러그인을 개정하기 전에
어떤 생성 패턴을 막고 어떤 현행 테스트를 조정해야 하는지 합의하기 위한 조사 기준선이다.

## 2. 조사 범위와 방법

### 2.1 전수 범위

| 항목 | 수치 |
|---|---:|
| `test/` 아래 Python 파일과 테스트 지원 파일 | 695개 |
| 실제 `test_*.py` 모듈 | 521개 |
| 테스트 영역 Python 코드 | 120,894줄 |
| AST 기준 `test_*` 함수 정의 | 4,464개 |
| pytest가 수집한 concrete case | 6,528개 |
| 전체 suite 실행 결과 | 6,528 passed |

### 2.2 조사 절차

1. pytest 전체 수집·실행으로 현재 suite 기준선을 확인했다.
2. 테스트 파일 전부를 AST로 읽어 assertion, `pytest.raises`, framework import,
   introspection, private import, 파일 읽기, `.dddjango` 문자열을 분류했다.
3. `pytest.fail`, `find_spec`, `import_module`, `model_json_schema`, `model_dump`,
   `issubclass`, `isinstance`, `hasattr`, `inspect.signature`, `get_type_hints`,
   `dataclasses.fields`, `ast.parse`, `__doc__` 후보를 전수 검색했다.
4. 기계 검색 결과는 삭제 판정으로 사용하지 않고 후보 함수 본문과 중복 외부 테스트를 직접 읽었다.
5. dddjango의 `discipline-tdd`, `implementation-test`, 역할 프롬프트와 대조했다.

자동 분석에서 본문에 직접 `assert`가 없는 테스트가 다수 발견됐지만, 대부분
`assert_problem()` 같은 테스트 helper 안에 assertion을 캡슐화한 정상 테스트였다. 따라서
단순 `assert` 유무나 짧은 함수 길이는 삭제 근거로 사용하지 않았다.

## 3. 판정 기준

### 3.1 삭제

다음 조건을 모두 만족하면 테스트 전체를 삭제 대상으로 분류한다.

- 현재 승인된 요구·설계·지원 계약을 보호하지 않는다.
- 제거해도 같은 계약을 검증하는 더 바깥의 테스트가 남거나, 애초에 제품 행동을 검증하지 않는다.
- 테스트의 오라클이 테스트 인프라, 구현 위치, private helper, framework 기본 동작 또는
  직접 생성한 객체의 자명한 성질이다.

### 3.2 부분 제거 또는 경계 재작성

한 테스트에 유효한 제품 계약과 불필요한 구조 단언이 섞였으면 파일이나 테스트를 통째로
삭제하지 않는다. 불필요한 assertion만 제거하거나 실제 mounted HTTP·공개 service 경계로 옮긴다.

### 3.3 유지

다음은 단순해 보여도 현재 계약이면 유지한다.

- 외부 HTTP status/body/header 중 승인된 공개 계약
- 공개 OHS의 실제 입력·출력·예외 행동
- wire 또는 DB에 노출되는 Enum의 정확한 literal 값
- 도메인 불변식과 상태 전이
- DB 제약, repository round-trip, 중복 방지
- 동시성, 멱등성, rollback, after-commit 의미
- 실제 health·routing endpoint
- 명시적으로 승인된 value object 불변성

### 3.4 승인 근거 확인

Python OHS의 exact dataclass field, signature, frozen 여부처럼 구조가 실제 공개 계약일 수 있는
항목은 명세 근거 없이 자동 삭제하지 않는다. 명세가 사라졌거나 침묵하면 `pending`이다.

## 4. 요약 판정

| 질문 | 결론 |
|---|---|
| 너무 당연한 것을 테스트하는가 | 그렇다. StrEnum·자기 타입·slots·tuple 등 다수 |
| framework 자체를 테스트하는가 | 그렇다. Pydantic validator 배치, Django StrEnum coercion, Ninja Schema 생성 등 |
| 테스트를 위한 테스트가 있는가 | 그렇다. Red import 비계, walking-skeleton availability, monkeypatch seam 검사 |
| `.dddjango` 문서를 실행·파싱하는 테스트가 있는가 | 없다 |
| `.dddjango` 추적성 문제는 있는가 | 있다. 인용한 명세 24개 중 20개가 현재 없음 |
| 프로덕션에 테스트 실행 코드가 섞였는가 | 없다. 다만 테스트 도구에 맞춘 의미·주석은 일부 있음 |

## 5. 구현 전 Red 비계 잔존

### 5.1 관찰 결과

59개 테스트·지원 파일에 최소 하나 이상의 “아직 구현되지 않았다” 동적 import 가드가 남아 있다.
해당 파일들에는 `pytest.fail()` 호출이 총 85곳 있다. 85곳 전부가 비계라는 뜻은 아니며,
일부는 정상적인 assertion fallback이다.

| BC | 비계 포함 파일 수 |
|---|---:|
| report | 39 |
| parental_controls | 6 |
| accounts | 5 |
| delivery | 2 |
| lessons | 2 |
| managed_copy | 2 |
| products | 2 |
| usage_quota | 1 |

대표 위치:

- `application/usage_quota/test/_acceptance_contract.py`
- `application/lessons/test/integration/_acceptance_helpers.py`
- `application/report/test/unit/**`
- `application/report/test/integration/**`

대표 형태:

```python
def _published_contract_module_exists() -> bool:
    try:
        return find_spec(SERVICE_MODULE) is not None
    except ImportError, ModuleNotFoundError, ValueError:
        return False


def _required_module(module_name: str) -> ModuleType:
    try:
        return import_module(module_name)
    except (ImportError, ModuleNotFoundError) as exc:
        pytest.fail(
            f"published contract is not implemented: {exc}",
            pytrace=False,
        )
```

### 5.2 확정 삭제

`application/usage_quota/test/integration/test_usage_quota_http.py`의
`test_usage_quota_published_contract_is_available_for_acceptance_suite`는 계약 로더를 호출할 뿐
제품 결과를 검증하지 않는다.

```python
def test_usage_quota_published_contract_is_available_for_acceptance_suite() -> None:
    load_usage_quota_contract()
```

이 walking-skeleton availability 테스트는 삭제한다.

### 5.3 조정 원칙

- 구현 전 Red에서 collection-friendly import 비계가 필요했더라도 첫 Green 뒤 제거한다.
- 구현이 존재하면 정상적인 정적 import를 사용한다.
- 59개 파일의 실제 행동 테스트를 통째로 삭제하지 않는다.
- `pytest.fail()` 전체를 금지하지 않는다.
- 플러그인은 Refactor 단계에 “Red 전용 import/decorator/availability 비계 제거”를 명시해야 한다.

## 6. Pydantic·Django Ninja 내부 직접 테스트

### 6.1 직접 framework-level 후보 18개

| 파일 | 테스트 수 | 판정 |
|---|---:|---|
| `application/ai_chat/test/unit/test_schema_in.py` | 9 | 삭제 |
| `application/usage_quota/test/unit/test_usage_quota_no_plan_schema.py` | 2 | 외부 HTTP 중복이면 삭제 |
| `common/test/unit/ninja/response/test_validation_error_out.py` | 4 | 폐기된 전역 validation Schema이므로 삭제 |
| `application/accounts/test/unit/test_child_profile_replace_schema.py` | 1 | mounted OpenAPI 계약이면 경계 재작성, 아니면 삭제 |
| `application/lessons/test/unit/presentation/test_lesson_list_openapi.py` | 2 | 내부 helper·테스트 전용 Schema이므로 삭제/경계 재작성 |

### 6.2 AI Chat validator 배치 고정

`application/ai_chat/test/unit/test_schema_in.py`는 파일 설명에서 HTTP 인수 테스트가 이미
외부 결과를 검증한다고 밝히면서, Pydantic validator가 model-level인지 field-level인지와
`ValidationError.loc`을 다시 고정한다.

```python
assert _locs_of(raised.value) == [()]
assert _locs_of(raised.value) == [("tool_outputs",)]
```

이는 제품 계약이 아니라 Pydantic 내부 배치에 결합된 테스트다. HTTP 경계의 입력 허용·거부가
남아 있으므로 파일의 9개 테스트를 삭제 대상으로 분류한다.

### 6.3 Schema 생성 직접 호출

다음 형태는 기본적으로 만들지 않는다.

```python
schema_type.model_json_schema()
schema_type().model_dump(mode="json")
```

공개 OpenAPI 계약이 필요하면 실제 URLconf에 mount된 문서 endpoint를 호출한다. 공개 HTTP body가
필요하면 실제 request를 보낸다. 내부 Schema나 OpenAPI helper의 반환 dict를 직접 검사하지 않는다.

### 6.4 common ErrorOut 예외

`common/test/unit/ninja/response/test_error_out.py`는 자동 삭제 대상으로 확정하지 않는다.
현재 사용자가 승인한 exact common `ErrorOut` shape를 보호하는 테스트라면 유효할 수 있다.
다만 플러그인이 field 목록을 기본값으로 고정해서는 안 되며, 테스트 유지에는 해당 프로젝트의
별도 shape 승인 근거가 필요하다.

## 7. 기존 전역 validation 오류 계약 결합

### 7.1 관찰 결과

68개 테스트 함수가 기존 `validation-error` 또는 `ValidationErrorOut` 어휘를 직접 참조한다.
이 집계는 삭제 건수가 아니라 재검토할 계약 결합 건수다.

대표 위치:

- `application/accounts/test/integration/test_children_acceptance.py`
- `application/ai_chat/test/integration/test_ai_chat_room_access_acceptance.py`
- `application/lessons/test/integration/api/test_lesson_api_openapi.py`
- `application/billing/test/integration/api/test_checkout_payment_http.py`
- `broccoli_server/test/test_api_error_handlers.py`

### 7.2 분리 판정

| 현재 검증 | 조치 |
|---|---|
| 필드 누락·Pydantic 파싱 실패와 기존 exact 전역 오류 body | exact body·`invalid-params` assertion 제거; 필요 시 status smoke만 유지 |
| validator `loc`에서 공개 필드명을 계산 | 삭제 |
| `ValidationErrorOut` OpenAPI component | 삭제 |
| 요청 크기 제한·cursor 서명·원자적 거부 등 application 규칙 | 행동 테스트 유지 |
| domain error와 framework 422의 경계 | 새 승인 error profile에 따라 재작성 |

잘못된 입력을 거부하는 행위가 제품 계약일 수는 있다. 그러나 Pydantic이 어느 오류 구조와 위치를
만드는지까지 커스텀 계약으로 고정하지 않는다.

## 8. framework·언어 자체 동작 테스트

### 8.1 Django의 StrEnum field coercion 3개

다음 테스트는 Django model field에 `StrEnum` member를 직접 넣고 문자열로 저장·조회되는지 검사한다.

- `application/accounts/test/integration/test_django_parent_repository.py`
  - `test_parent_model_accepts_social_provider_enum_member_as_field_value`
- `application/accounts/test/integration/test_django_child_repository.py`
  - `test_child_model_accepts_gender_enum_member_as_field_value`
- `application/notifications/test/integration/test_django_notification_record_repository.py`
  - `test_notification_record_model_accepts_enum_members_as_field_values`

이는 Python `StrEnum`이 `str` 하위 타입이라는 사실과 Django field coercion을 재검증한다.
애플리케이션이 저장 contract를 통제하려면 `.value`를 명시적으로 저장하고 실제 DB literal만
검증한다. 위 세 테스트는 삭제 대상으로 분류한다.

### 8.2 StrEnum이 문자열인지 검사하는 테스트 6개

대표 형태:

```python
assert isinstance(Gender.MALE, str)
assert str(Gender.MALE) == "male"
```

대상:

- accounts `SocialProvider`
- accounts `Gender`
- child_settings `NotificationCategory`
- notifications의 event type, payload schema version, policy 3개

`Gender.MALE.value == "male"`처럼 exact 공개 literal은 유지할 수 있다. `isinstance`와
`str(member)`는 Python 자체 보장이므로 제거한다.

delivery와 lessons의 혼합 Enum 계약 테스트도 exact member value 집합은 유지하되
`issubclass(..., StrEnum)` assertion만 제거한다.

### 8.3 JSON duplicate key 1개

`broccoli_server/test/test_api_routing.py`의
`test_openapi_schema_does_not_contain_duplicate_object_keys`는 Python dict를 JSON으로 직렬화하는
기본 경로에서 중복 key가 없는지 다시 검사한다. custom raw JSON serializer가 없는 현재 구조에서는
framework·언어 성질이므로 삭제한다.

### 8.4 freezegun 호환을 제품 계약으로 만든 테스트 2개

- `application/products/test/unit/application/test_application_dto_validation.py`
  - `test_date_only_accepts_a_date_subclass`
- `application/products/test/unit/domain/test_product.py`
  - `test_product_accepts_date_subclass_sale_dates`

두 테스트 모두 `freezegun FakeDate` 호환이 근거라고 명시한다. 테스트 도구 때문에 프로덕션 의미를
고정한 사례다. 실제 날짜를 사용하거나 clock seam으로 분리하고 해당 테스트는 삭제한다.

## 9. 테스트를 위한 테스트와 자명한 구조 단언

### 9.1 monkeypatch seam 검사 1개

`application/ai_chat/test/unit/test_composition_root.py`의
`test_every_patch_seam_is_a_module_level_name`은 `monkeypatch`가 가능한 전역 이름인지 검사한다.

```python
assert callable(getattr(composition_root, seam))
```

제품 계약이 아니라 테스트 가능성을 테스트하므로 삭제한다.

### 9.2 production docstring 검사 4개

- accounts display-name/birth-year service의 예외 이름 문구
- accounts counting-age service의 예외 이름 문구
- notifications port의 예외 목록 문구
- report repository의 “최신 판이 활성판” 문구

docstring 철자는 런타임 계약이 아니다. 실제 예외·repository 행위를 검증하는 테스트가 남으므로
네 테스트는 삭제한다.

### 9.3 slots assertion 6개

accounts의 세 published request/response 쌍이 다음을 검사한다.

```python
assert not hasattr(value, "__dict__")
```

불변성이 승인된 계약이면 `FrozenInstanceError` assertion은 유지할 수 있다. `slots`는 구현·성능 선택이므로
`__dict__` assertion만 부분 제거한다.

### 9.4 직접 생성한 객체의 자기 타입 검사 1개

`test_declared_failures_keep_their_canonical_exact_classes`는 직접 생성한
`ChildProfileNotFoundV1`이 `ChildProfileNotFoundV1`인지 확인한다. 동어반복이므로 삭제한다.

### 9.5 tuple 여부만 검사하는 테스트 2개

- AI Chat function-call pair resolver 결과가 tuple인지
- AI Chat transcript assembler의 past conversation이 tuple인지

불변 collection type이 공개 계약으로 승인됐다면 유지할 수 있다. 앞 테스트가 동일 결과의 내용과
순서를 이미 검증하고 단지 구현 collection type만 별도 고정한 것이라면 삭제한다. 현재 명세 근거를
확인하기 전까지 `pending`이다.

### 9.6 adapter가 port를 상속했는지만 검사하는 테스트 8개

report 6개, entitlements 1개, AI Chat 1개가 `issubclass` 또는 `isinstance`만 단언한다.
adapter의 변환·예외 번역·I/O 결과 테스트는 유지하되 nominal 상속만 검사하는 테스트는
타입 검사기와 클래스 선언이 대신하므로 삭제 후보로 분류한다. runtime nominal contract가 별도로
승인된 경우만 유지한다.

## 10. private production 심볼 직접 테스트

재현 가능한 AST 집계 기준으로 5개 테스트 파일이 production private 심볼 6개를 직접 import한다.

| private 심볼 | 대표 파일 |
|---|---|
| `_turn_actor` | `application/ai_chat/test/unit/test_turn_controller.py` |
| `_raise_published` | `application/notifications/test/unit/test_notification_published_exceptions.py` |
| `_expected_period_starts_for` | `application/report/test/unit/child_subject_trend_narration/test_subject_trend_snapshot_selection.py` |
| `_gate_facts` | `application/report/test/unit/test_question_gate_provenance_ohs.py` |
| `_to_application_request` | 같은 report OHS 파일 |
| `_problem_for` | `broccoli_server/test/test_api_error_handlers.py` |

`_expected_period_starts_for`는 바로 앞 공개 `Window` 테스트와 완전히 중복되므로 해당 테스트를 삭제한다.
나머지는 공개 controller·published service·mounted HTTP 결과로 재작성한다. private 구현을 별도 계약으로
승격하지 않는다.

## 11. production source를 읽는 pytest

5개 파일, 8개 테스트 함수가 production `.py`를 `Path.read_text`, `inspect.getsource`, `ast.parse`로
읽어 import 구조를 검사한다.

| 위치 | 함수 수 | 현재 검사 |
|---|---:|---|
| `application/billing/test/unit/infra/test_import_isolation.py` | 4 | BC/common/Django import 격리 |
| `application/lessons/test/unit/domain/test_lesson_list_position.py` | 1 | domain module의 Django import 부재 |
| report command/value-object 테스트 3파일 | 3 | Django import·타 고정 상수 import 부재 |

아키텍처 규칙 자체가 유효할 수는 있지만 제품의 pytest 행위 테스트로 두지 않는다. 저오탐으로
결정 가능한 규칙이면 별도 checker/backstop으로 이동하고, 의미 판정이 필요한 규칙이면 discipline
reviewer가 본다. report의 혼합 테스트는 공개 contract assertion을 유지하고 AST block만 제거한다.

## 12. migration 구현 직접 테스트

직접 migration module의 seed 함수를 호출하거나 `MigrationExecutor`로 migration 결과를 검사하는
테스트가 6개 있다.

| 위치 | 수 |
|---|---:|
| subject marking prompt revision | 3 |
| learning-attitude narration prompt revision | 1 |
| learning-attitude trend narration prompt revision | 2 |

현재 DB에서 seed 결과가 존재하고 repository가 이를 읽는 행위는 current-state 테스트로 검증할 수 있다.
특정 migration module·함수·과거 state·적용 순서가 오라클인 테스트는 dddjango의 기존 정책대로
신규 생성·확장하지 않는다. 기존 6개를 실제로 삭제할 때는
[현행 계약 테스트 정책](../plan/2026-07-14-current-contract-test-policy-plan.md)의 종료 근거 절차를 따른다.

## 13. OpenAPI 경계 오류

다음 4개 테스트는 root API 객체의 `api.get_openapi_schema()`를 직접 호출한다.

- products 2개
- notifications delivery snapshot 1개
- notifications list 1개

OpenAPI가 공개 계약이면 실제 URLconf에 mount된 `/openapi.json`을 Django client로 가져와 검증한다.
내부 API 객체 직접 호출 테스트는 mounted 경계 테스트로 재작성하거나, 문서 계약 자체가 승인되지
않았다면 삭제한다.

lessons의 테스트 전용 `Schema`와 `lesson_list_openapi_extra()` 직접 테스트도 같은 이유로 제거한다.

## 14. 성공 Schema 중복 후보

다음 5개는 framework 자체 테스트로 확정하지 않지만 외부 HTTP 인수 테스트와의 중복 검토가 필요하다.

- managed_copy success Schema mapping 3개
- lessons success Schema mapping 2개

성공 body의 exact field와 nullable 의미가 공개 계약이고 바깥 테스트가 없다면 유지한다. 동일 HTTP body가
이미 인수 테스트로 보호되면 내부 `model_dump()` mapping 테스트는 삭제한다.

## 15. `.dddjango` 문서 조사

### 15.1 문서 자체를 테스트하는 코드는 없음

- `.dddjango` 파일을 `open()`·`read_text()`로 읽는 테스트: 0
- design-spec·scope를 parse해 테스트 성공 여부를 정하는 코드: 0
- production의 실행 가능한 `.dddjango` 경로 문자열: 0

### 15.2 추적성 단절

| 항목 | 수 |
|---|---:|
| `.dddjango`를 주석·docstring에서 언급하는 test/support 파일 | 51 |
| 전체 문자열 언급 | 61 |
| 고유한 literal `design-spec.md` 경로 | 24 |
| 현재 존재하는 경로 | 4 |
| 현재 사라진 경로 | 20 |

문제를 해결하기 위해 `.dddjango` 문서를 읽는 pytest를 추가하면 안 된다. 승인된 `scope.md`와
`design-spec.md`를 커밋된 근거로 유지하거나, 정리해야 한다면 안정적인 requirement ID·보존 문서로
연결한다. 존재하지 않는 경로를 테스트 docstring에서 “단일 진실의 출처”라고 인용하지 않는다.

## 16. production 코드의 테스트 누수

실행 코드 기준 누수는 발견되지 않았다.

| 검사 | 결과 |
|---|---:|
| production의 `pytest`, `unittest.mock`, `factory_boy`, `freezegun` import | 0 |
| production의 `test_*` 함수·클래스 | 0 |
| production의 실행 가능한 `.dddjango` 문자열 | 0 |

다만 production 주석·docstring 5곳이 `freezegun` 또는 `pytest-django`를 직접 언급한다.
그중 products의 두 date-subclass 테스트는 테스트 도구 호환을 제품 의미로 고정했다. 실행 코드 누수는
아니지만 test-induced design 후보로 분류한다.

## 17. 메타·introspection 후보를 일괄 삭제하지 않는 이유

전수 패턴 검색에서는 `dataclasses.fields`, `inspect.signature`, `get_type_hints`, `issubclass`,
`hasattr` 등 meta/introspection assertion이 광범위하게 발견됐다. 그중 assertion이 사실상 meta
검사뿐인 후보 함수도 53개였다.

그러나 다음은 실제 공개 Python 계약일 수 있다.

- OHS request/response의 exact field set
- 공개 service의 호출 signature
- 공개 예외 hierarchy
- composition root가 조립하는 실제 collaborator type
- event union과 Enum 집합 동기화

따라서 `hasattr`, `issubclass`, `signature`, `fields` 사용 자체를 백스탑으로 전면 금지하지 않는다.
공개 승인 계약인지, implementation detail인지 의미 검토해 분류한다.

## 18. 불필요 테스트 생성 원인 분석

### 18.1 조사 방법

전수 감사 뒤 원인 추적은 서로 다른 세 축으로 독립 수행하고 결과를 교차 검증했다.

1. **생성 경로 추적**: reference → architect → `design-spec.md` → acceptance/coder → 실제 테스트의
   지시 흐름을 대조했다.
2. **예방 경로 추적**: G1/G2 게이트, 역할 경계, discipline review, 19개 checker, 평가 rubric이
   불필요 테스트를 막을 수 있었는지 확인했다.
3. **시간축·반증 추적**: Git 이력에서 테스트 생성 시점의 플러그인 규칙과 이후 수동 변경을 분리하고,
   현재 규칙을 과거 산출물에 소급해 원인을 단정하지 않았는지 적대적으로 검토했다.

현재 정본 근거는 [Coordinator](../../dddjango/commands/dddjango.md),
[design-architect](../../dddjango/agents/design-architect.md),
[acceptance-tester](../../dddjango/agents/acceptance-tester.md),
[coder](../../dddjango/agents/coder.md),
[discipline-reviewer](../../dddjango/agents/discipline-reviewer.md),
[discipline-tdd](../../dddjango/skills/discipline-tdd/references/final.md),
[implementation-test](../../dddjango/skills/implementation-test/references/final.md)다.
과거 산출물은 현재 working tree에 없는 `.dddjango` 명세도 Git blob으로 복원해 당시 문구를 확인했다.

### 18.2 핵심 결론

주원인은 단순히 "TDD를 엄격히 적용해서"가 아니다. **설계 명세가 제품 행동이 아닌 구현 세부와
framework mechanics를 승인된 테스트 계약으로 승격했고, Coordinator가 그 계약의 모든 신규·변경
내부 의무를 unit Red 슬라이스로 기계적으로 변환한 것**이 시작점이다. 그 뒤 기존의 일반적인
white-box·중복 금지 규칙은 더 구체적인 승인 명세를 뒤집지 못했고, Green 이후 Red 비계를 제거하거나
외부 테스트와 중복을 다시 판정할 소유자와 게이트도 없었다.

```text
reference의 넓은 테스트 권고 또는 잘못 해석된 예시
                         ↓
architect가 구현 방식·framework mechanics를 test contract로 명세
                         ↓
G1은 명세 전체를 승인하지만 신규·변경 테스트의 필요성은 직접 표면화하지 않음
                         ↓
Coordinator가 모든 내부 의무를 unit-Red 슬라이스로 생성
                         ↓
coder가 "승인 명세가 단일 근거"라는 우선순위에 따라 테스트 작성
                         ↓
Green 이후 비계 제거·외부/내부 중복 재판정 단계 없음
                         ↓
전체 suite green과 coverage가 오히려 완료 증거가 되어 불필요 테스트가 영구화
```

이 흐름에서 **명세 오염이 1차 원인**, **내부 의무의 자동 Red 변환이 증폭기**, **사후 정리와
필요성 게이트의 부재가 영구화 원인**이다.

### 18.3 Git 재현 앵커

아래 commit은 작성자 귀속을 hash 하나로 단정하기 위한 것이 아니라, 당시 규칙·명세·테스트 본문을
다시 열어 시간축과 인과를 재검증하기 위한 앵커다.

| 저장소 | commit | 확인 가능한 사실 |
|---|---|---|
| dddjango | `672729c` (2026-07-14) | migration 전용 테스트 신규·확장 금지가 도입됐다. 이후 생성된 migration seed/module 테스트는 "규칙이 아직 없었다"로 설명할 수 없다. |
| dddjango | `5a87b2f` (2026-07-16) | ErrorOut/helper 내부 직접 테스트 금지의 선행 규칙을 확인할 수 있다. 다음 날 Broccoli error 명세와 `_problem_for` 테스트가 이를 우회했다. |
| dddjango | `9f54d7a` (2026-07-17) | `dddjango--v1.2.2` release 기준선이다. |
| dddjango | `4a3c838` (2026-08-04 21:46 KST) | BC-owned API error와 현재 테스트 경계가 강화됐다. 이전 산출물에 소급 적용하지 않는다. |
| dddjango | `7718407` (2026-08-05) | manifest version 증가 없이 Claude 호출 정책이 다시 바뀌었다. 동일 버전 prompt drift의 한 근거다. |
| broccoli-server | `e0676d1e` (2026-07-11) | `usage_quota` loader-only Walking Skeleton 테스트의 도입 시점을 확인할 수 있다. |
| broccoli-server | `ef858a92` (2026-07-17) | 당시 전역 `ValidationErrorOut`·handler·OpenAPI 계약과 `_problem_for` 테스트를 확인할 수 있다. |
| broccoli-server | `5d413725` (2026-07-17) | products의 `FakeDate`/date-subclass 계약과 테스트 도구 유발 설계를 확인할 수 있다. |
| broccoli-server | `7722db64` (2026-07-18) | billing 설계 명세와 AST import-isolation 테스트의 직접 대응을 확인할 수 있다. |
| broccoli-server | `03299a57` (2026-07-25) | accounts 공개 계약 테스트에 docstring·`slots`·identity 등 구현 세부가 함께 고정된 시점을 확인할 수 있다. |
| broccoli-server | `1356a078` (2026-07-28) | migration seed 함수·prompt bytes/hash를 현재 결과라는 이름으로 직접 검사한 사례를 확인할 수 있다. |
| broccoli-server | `14792b9e` (2026-08-05) | 2026-08-04 01:56에 시작한 AI Chat 명세와 validator 배치·exact `loc` 테스트의 대응을 확인할 수 있다. |
| broccoli-server | `d5604679`, `8ab27c8b`, `28d4d667` | `.dddjango` 문서 삭제, migration 상수로의 테스트 재앵커, `MigrationExecutor` case 추가 등 플러그인 실행 뒤 수동 변경을 분리할 수 있다. |

## 19. 왜 작성하게 되었는가

| 원인 | 실제 작동 방식 | 근거·관찰 |
|---|---|---|
| 설계 명세가 구현 세부를 계약으로 승격 | validator 위치, `ValidationError.loc`, AST import 검사, module-global monkeypatch seam, docstring, `slots`, migration seed 함수 같은 구현 결정을 "테스트 기준"으로 명시했다. coder 입장에서는 이를 생략하는 것이 명세 위반이 된다. | 과거 Broccoli `.dddjango/**/design-spec.md`와 실제 테스트가 문구 수준으로 대응한다. 현재 architect도 테스트 계약 변화를 명세의 필수 산출물로 소유한다. |
| 모든 내부 의무를 unit Red로 변환 | 외부 Red가 0개여도 승인된 내부 의무가 있으면 슬라이스를 만들고, 신규·변경 내부 의무는 단위 Red부터 시작한다. 잘못 들어온 내부 의무 하나가 거의 자동으로 영구 테스트 하나 이상이 된다. | Coordinator Phase 2의 internal test-adjustment/unit-Red 규칙 |
| 구체 명세가 일반 원칙보다 강함 | coder는 승인된 명세와 테스트 계약을 단일 근거로 받는다. "public protocol을 테스트하라"는 일반 원칙과 "이 helper·validator·AST를 검사하라"는 구체 명세가 충돌하면 실행 단계는 구체 명세를 따른다. | architect→coder 역할 경계와 G1 잠금 구조 |
| 테스트 피라미드·이중 루프를 수량 압력으로 오해 | 상위 테스트가 이미 행위를 보장해도 같은 실패를 더 낮은 단위 테스트로 재현하는 쪽으로 기울었다. 테스트 수준 선택이 "가장 낮고 빠른 유효 경계"가 아니라 "외부+내부 양쪽"으로 굳었다. | `discipline-tdd`의 이중 루프와 `implementation-test`의 unit 중심 피라미드가 중복 금지 조건보다 더 쉽게 실행됐다. |
| 개념 예시의 과잉 확장 | Walking Skeleton의 실제 예시는 `/health`를 통한 end-to-end 연결 확인인데, Broccoli에서는 계약 loader가 import되는지만 확인하는 availability 테스트로 축소·왜곡됐다. | `usage_quota` loader-only 테스트와 reference의 실제 `/health` 예시 대조 |
| 당시 reference가 직접 내부 호출을 예시 | 구버전에는 `api.get_openapi_schema()` 직접 호출처럼 현재는 금지하는 방식이 recipe로 존재했다. 당시 산출물은 현재 mounted-client 원칙이 아니라 당시 recipe를 따른 것이다. | products·notifications의 direct OpenAPI 테스트와 historical v1.2.2 reference |
| 테스트 도구 편의를 제품 의미로 승격 | `freezegun`의 `FakeDate`를 받기 위해 date subclass 수용을 제품 계약으로 만들거나, monkeypatch가 쉬운 module-global 이름을 별도 테스트했다. | products date-subclass 2개, AI Chat seam 테스트 1개 |

TDD 자체는 원인이 아니다. **무엇을 영구 테스트 의무로 받아들일지 정제하지 않은 상태에서 모든 내부
의무에 TDD를 적용한 것**이 문제다. 동일한 Red→Green→Refactor 절차라도 오라클이 공개 행동·도메인
불변식·DB 보장으로 제한됐다면 이 테스트들은 생성되지 않는다.

## 20. 왜 작성을 막지 못했는가

| 예방 실패 | 왜 통과했는가 | 현재 근거 |
|---|---|---|
| 기존 white-box·중복 금지 규칙이 실행 조건으로 바뀌지 않음 | `implementation-test`에는 public protocol 중심 원칙이 있고 coder와 discipline reviewer에도 외부↔내부 중복 금지가 있다. 그러나 각 테스트가 어떤 독자적 실패를 잡는지, 어느 외부 계약과 중복되지 않는지 제출하는 필수 증거는 없다. | `implementation-test`의 white-box 회피 절, coder·discipline-reviewer의 중복 규칙 |
| G1에서 신규·변경 테스트 의무가 직접 드러나지 않음 | G1 배너는 테스트 계약의 종료·부재/금지·미확정을 직접 나열하지만, 새로 생기는 영구 테스트와 그 필요성은 명세 안에만 남을 수 있다. 사용자는 전체 설계를 승인하면서 validator 위치나 seam 테스트까지 승인한 것으로 처리된다. | Coordinator Phase 1 G1 배너 규칙 |
| 테스트 계약 입장 심사가 없음 | architect가 "현재 제품 계약인가", "framework 자체 동작인가", "더 바깥 테스트와 중복인가", "구현을 바꿔도 유지할 오라클인가"를 통과시켜야만 test contract에 넣는 admission gate가 없다. | architect의 필수 테스트 계약 변화 산출은 있으나 영구 테스트 자격 판정표는 없음 |
| acceptance와 coder 사이의 중복 제거가 선언에 머묾 | acceptance는 외부 계약, coder는 내부 불변식·협력을 소유하지만 같은 행동을 양쪽이 덮는지 보여 주는 일대일 대조표가 없다. 역할 분리는 편집 충돌은 줄였지만 중복 생성까지 막지 못했다. | Phase 2 역할 분리와 `path::test | action | ...` 보고 형식 |
| Green 이후 Red 전용 비계의 정리 소유자가 없음 | acceptance-tester는 구현 전에 Red를 만들고 외부 테스트를 조정한다. coder는 승인된 외부 테스트를 임의로 바꿀 수 없고, 첫 Green 뒤 acceptance-tester를 다시 불러 loader·동적 import·대체 decorator를 제거하는 단계도 없다. | acceptance-tester의 production-blind Red 역할, coder의 외부 테스트 편집 제한 |
| brownfield 검색 범위가 의도적으로 좁음 | 변경 표면의 URL·public symbol·모델명 등을 anchor로 "관련 테스트만" 찾고 전체 suite는 마지막에 실행만 한다. 다른 위치의 오래된 중복·폐기 계약 테스트는 green이면 발견 대상이 아니다. | Coordinator Phase 2 관련 테스트 검색 규칙; [현행 계약 테스트 정책](../plan/2026-07-14-current-contract-test-policy-plan.md)의 전수 inventory 비목표 |
| 19개 checker가 테스트 가치 판단을 하지 않음 | 테스트 전용 checker는 pytest와 Django settings 연결만 확인한다. 나머지는 구조·API error·계층 규칙 등이며 "이 테스트가 제품 계약을 보호하는가"를 판정하지 않는다. | [check-test-config.py](../../dddjango/scripts/check-test-config.py)와 Coordinator checker registry |
| 평가지가 양의 증거만 보상 | 전체 green, coverage, pytest 생태계, 인수 행위 누락은 보지만 중복 테스트 수, framework 재검증, 비계 잔존에 감점 항목이 없다. 6,528개가 모두 통과해도 이번 문제가 드러나지 않은 이유다. | [RUBRIC Q-6](../eval/rubric/RUBRIC.md); rubric은 명세 내적 품질과 미시 유지보수성을 명시적 비측정 |
| 정책 변경 후 정리 lifecycle이 약함 | 한때 승인된 계약이 폐기돼도 관련 anchor에 걸리거나 현재 작업 범위에 들어오지 않으면 테스트는 계속 green으로 남는다. | 기존 `validation-error` 결합 68개와 현재 계약 전환 |
| 배포 provenance가 재현 가능하지 않음 | Claude와 Codex 매니페스트는 모두 `1.2.2`다. 현재 source와 Codex cache는 서로 일치하지만 Claude cache는 release tag 시점 prompt에 머물러 있어, 같은 버전 아래 실제 prompt가 다르다. 버전만 보고 어느 규칙이 실행됐는지 확정할 수 없다. | 두 manifest의 동일 버전, `dddjango--v1.2.2` 이후 정책 커밋과 플랫폼 cache 차이 |

특히 첫 번째 행은 "금지 규칙이 없었다"는 뜻이 아니다. 규칙은 있었지만 **구체 명세와 충돌했을 때
차단할 우선순위, 필수 증거, 결정적 게이트로 운영되지 않았다.** 따라서 문구를 한 번 더 추가하는 것만으로는
같은 실패를 막기 어렵다.

## 21. 대표 사례의 생성·잔존 경로

| 사례 | 생성 또는 잔존 경로 | 판정 |
|---|---|---|
| AI Chat Pydantic validator·`loc` | 2026-08-04 AI Chat 명세가 model/field validator 배치와 exact `loc` 테스트를 직접 요구했고 실제 unit test가 그대로 구현했다. 이 설계는 8월 4일 새 API error 정책 커밋보다 먼저 시작됐다. | 명세 오염 → unit Red의 직접 사례 |
| billing import isolation AST | 해당 설계 명세가 `ast.parse` 기반 import-isolation 테스트 파일과 assertion을 구체적으로 지정했다. 당시에도 일반 white-box 회피 원칙은 존재했다. | 규칙 부재가 아니라 구체 명세 우선·게이트 실패 |
| AI Chat monkeypatch seam | prompt-cache 명세가 module-global patch seam 목록과 이를 보장하는 테스트를 계약으로 지정했다. | 테스트 편의를 제품 테스트로 승격 |
| products `FakeDate` | 설계 근거가 freezegun 호환과 date subclass 수용을 직접 연결했다. | 테스트 도구가 production 의미를 결정 |
| accounts docstring·`slots` | child display-name/birth-year 명세가 exact identity, module, signature, fields, docstring, frozen, slots 검사를 함께 요구했다. | 공개 계약 후보와 구현 세부를 분리하지 못함 |
| `usage_quota` availability | v1.0.8 시기 Walking Skeleton을 실제 HTTP 연결이 아니라 contract loader 성공으로 해석했다. | reference 개념의 과잉·축소 해석 |
| direct OpenAPI helper | 구버전 reference의 `api.get_openapi_schema()` 직접 호출 recipe가 실제 테스트 방식과 일치한다. 현재는 mounted URLconf/client 검증으로 정책이 바뀌었다. | 당시 정책의 직접 영향 + 이후 lifecycle 부재 |
| 전역 `ValidationErrorOut` 68건 | 2026-07-17 당시 승인 명세는 global `ValidationErrorOut`, exact invalid-params, handler, OpenAPI를 실제 계약으로 요구했다. 2026-08-04 BC-owned error/framework-default 422 정책으로 전환되면서 다수가 폐기 계약 결합이 됐다. | 생성 당시 전부 불필요했다고 볼 수 없으며, 현재는 계약 전환 정리 대상 |
| migration seed/module 테스트 | migration 전용 테스트 금지 정책이 2026-07-14에 먼저 들어왔는데 이후 명세가 seed 함수·module·hash를 "현재 seed 결과"로 다시 이름 붙여 테스트했다. | 규칙 부재가 아닌 우회·enforcement 실패 |

## 22. 시간축과 과대주장 방지

원인 분석을 플러그인 개정 근거로 쓸 때 다음 경계를 유지한다.

1. **현재 플러그인이 과거의 모든 문제를 직접 지시했다고 말하지 않는다.** 2026-08-04 API error
   개정은 helper·handler 내부 테스트, framework exact body snapshot, direct OpenAPI helper 등을 이미 더 강하게
   금지한다. 과거 테스트에는 구버전 prompt가 적용됐다.
2. **기존에 white-box·중복 금지 규칙이 없었다고 말하지 않는다.** public protocol 중심 규칙,
   acceptance↔unit 중복 금지, migration 테스트 금지는 이미 있었다. 이번 발견은 규칙의 존재와 실제 집행이
   분리됐다는 증거다.
3. **기존 `validation-error` 테스트 68개를 생성 당시부터 전부 무가치했다고 보지 않는다.** 당시에는
   승인된 외부 계약이었고, 정책 전환 뒤 stale해졌다. 이는 생성 gate와 별도로 종료 lifecycle 문제다.
4. **migration 테스트 전부를 플러그인이 최초 생성했다고 단정하지 않는다.** 일부는 이후 수동 커밋에서
   문서 참조를 migration 상수로 재앵커하거나 `MigrationExecutor` case를 추가했다. 다만 플러그인 명세가
   금지 규칙을 우회한 직접 사례도 확인됐다.
5. **Walking Skeleton reference 자체가 import availability를 지시했다고 말하지 않는다.** reference의 실제
   `/health` E2E 예시를 Broccoli 설계가 잘못 확장한 것이다.
6. **모든 introspection·exact shape 테스트를 금지하지 않는다.** 별도 승인된 common `ErrorOut` shape,
   공개 OHS signature/field/hierarchy, event union↔Enum 동기화는 실제 계약일 수 있다.
7. **`.dddjango` 문서를 실행하는 테스트가 있다고 말하지 않는다.** 현재 그러한 테스트는 0개다.
   문제는 24개 literal 명세 경로 중 20개가 working tree에서 사라진 추적성 단절이며, Git history에는
   24개 blob이 모두 남아 있다.
8. **특정 Broccoli 실행이 어느 플랫폼 cache를 사용했는지는 digest receipt 없이 확정하지 않는다.** 다만
   같은 `1.2.2` 버전 아래 Claude와 Codex의 실제 prompt가 다른 상태는 확인됐고 재현성을 해친다.

## 23. 원인 우선순위와 개정 방향

문구를 많이 추가하거나 checker를 먼저 늘리기보다 원인이 유입되는 앞단부터 닫는다.

| 우선순위 | 닫아야 할 원인 | 개정 방향 |
|---:|---|---|
| 1 | architect가 구현 세부를 영구 테스트 계약으로 승인 | test contract 입장 조건에 제품 행동·도메인 불변식·DB 보장·승인된 공개 Python 계약만 허용하고 framework mechanics·private 구조·테스트 seam을 명시적으로 반송한다. |
| 2 | 모든 내부 의무의 자동 unit Red화 | "설계상 내부 결정"과 "영구 테스트가 필요한 내부 계약"을 분리하고, 독자적으로 잡는 실패가 설명된 의무만 unit Red 슬라이스로 만든다. |
| 3 | G1에서 새 테스트의 필요성이 숨음 | 신규·변경 영구 테스트를 배너에 행위 단위로 표면화하고, 외부 테스트와의 중복 및 생략 이유를 함께 보여 준다. |
| 4 | Green 이후 비계·중복 정리 소유자 부재 | Refactor 종료 전에 Red-only loader·동적 import·대체 decorator를 제거하고 acceptance↔unit 중복을 재감사할 명시적 소유자를 둔다. |
| 5 | 관련 범위 밖 stale 테스트의 영구 잔존 | 전체 suite를 무차별 편집하지 않되, 폐기된 계약 식별자와 변경된 public surface를 anchor로 종료 후보를 찾는 제한된 lifecycle 검색을 추가한다. |
| 6 | checker·eval이 양만 확인 | 저오탐 형태만 backstop으로 만들고, 의미 판정은 reviewer가 `보호 계약 / 독자적 실패 / 중복 여부` 증거로 감사한다. eval에는 framework 재검증·Red 비계·중복의 음의 사례를 넣는다. |
| 7 | 같은 버전의 prompt drift | Claude·Codex 의미 미러와 cache provenance를 릴리스 버전·digest로 식별해 어떤 정책이 실행됐는지 재현 가능하게 한다. |

이 순서가 중요한 이유는 checker만 추가하면 이미 오염된 명세를 충실히 구현한 coder를 뒤에서 막는
구조가 되기 때문이다. 먼저 architect가 영구 테스트 자격을 잘못 부여하지 않게 하고, G1에서 사용자가
그 의무를 볼 수 있게 한 뒤, 저오탐으로 결정 가능한 잔존 형태만 백스탑으로 보강한다.

## 24. 플러그인 개정 요구사항

이 감사에서 도출된 최소 정책 요구는 다음과 같다.

1. Red 전용 `find_spec`·동적 import·대체 decorator·availability test는 첫 Green 뒤 제거한다.
2. 외부 인수 테스트가 같은 행위를 보호하면 내부 Schema 테스트를 중복 생성하지 않는다.
3. Pydantic validator 위치·`ValidationError.loc`·framework 기본 직렬화 자체를 테스트하지 않는다.
4. framework 기본 오류는 승인된 범위의 status·비노출 smoke만 허용하고 exact body를 커스텀 계약으로
   snapshot하지 않는다.
5. Python·Django의 `StrEnum` 기본 동작을 테스트하지 않고 공개 literal만 보호한다.
6. private helper, production docstring, production source AST, 테스트 monkeypatch seam을 제품 pytest로
   검증하지 않는다.
7. adapter nominal 상속은 타입 검사기로 맡기고 변환·예외 번역 행동을 테스트한다.
8. migration module·함수·과거 state를 직접 테스트하지 않는다.
9. 테스트 도구 호환을 제품 요구로 승격하지 않는다.
10. `.dddjango` 문서를 pytest로 검사하지 않되, 테스트가 인용하는 승인 근거를 삭제하지 않는다.

## 25. 백스탑 후보와 reviewer 소유 구분

### 25.1 결정적으로 잡을 수 있는 후보

다음은 제한된 AST 패턴으로 저오탐 백스탑을 검토할 수 있다.

- 테스트가 production의 underscore-prefixed symbol을 직접 import
- 테스트가 production `.py`를 읽어 `ast.parse`·`inspect.getsource` 수행
- production `__doc__` 문자열을 assertion
- 구현이 존재하는 Phase 2 완료 시점에 `find_spec`/`import_module` + “not implemented”
  `pytest.fail` 비계가 잔존
- error helper/handler를 직접 호출하는 unit test
- `isinstance(<StrEnum member>, str)`와 순수 `issubclass(..., StrEnum)` mechanics assertion

백스탑 도입 여부는 기존 19개 checker 수와 오탐 비용을 별도 설계에서 결정한다.

### 25.2 의미 reviewer가 판정할 항목

다음은 정적 형태만으로 금지하지 않는다.

- 내부 Schema 테스트가 외부 테스트와 실제로 중복인지
- tuple·frozen·exact field/signature가 공개 OHS 계약인지
- adapter inheritance가 runtime nominal contract인지
- framework 422 테스트 안에 별도 application 규칙이 섞였는지
- 기존 migration 테스트의 현재 의무가 명시적으로 종료됐는지
- meta/introspection assertion이 구현 세부인지 공개 Python 계약인지

## 26. 후속 작업 경계

이 문서 승인 전에는 dddjango 플러그인과 `broccoli-server` 테스트를 수정하지 않는다.
승인 뒤 별도 계획에서 다음 순서로 진행한다.

1. 플러그인 테스트 생성·Refactor·감사 규칙 개정
2. 결정적 백스탑 후보와 reviewer-only 항목 선별
3. Claude/Codex 의미 미러와 reference 정합화
4. 합성 prompt/eval로 불필요 테스트 비생성 검증
5. 별도 승인된 `broccoli-server` 테스트 정리

실제 테스트 삭제는 현재 구현에 맞추기 위한 삭제가 아니라, 이 문서의 판정과 승인된 테스트 계약
변화에 연결해 수행한다.
