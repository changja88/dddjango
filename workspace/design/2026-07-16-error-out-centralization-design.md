# ErrorOut 중앙 계약 설계

- 작성: 2026-07-16
- 상태: 적대 리뷰 3종 PASS v4 · 사용자 승인 · 구현 대기
- 범위: Django Ninja Problem Details 응답 Schema의 소유·배치·재사용 규율과 파이프라인 역할 책임
- 비범위: 도메인 예외 계층, 예외→HTTP status 매핑 내용, problem type URI 카탈로그의 전역 통합, DRF/plain Django 계약의 강제 이주

## 1. 문제

현재 플러그인은 각 BC의 `presentation_layer/schema/error_out.py`에 `ErrorOut`을 만들도록 안내한다. 반면 런타임 problem body와 exception handler는 presentation 단일 변환점으로 모으도록 안내한다. 이 때문에 다음 상태가 동시에 가능하다.

1. 클라이언트가 받는 동일한 Problem Details envelope가 BC마다 복제된다.
2. 어떤 예시는 `ProblemOut`, 다른 예시는 `ErrorOut`을 사용한다.
3. 프로젝트 공통 Schema가 있어도 architect와 coder가 이를 확인하지 않고 로컬 Schema를 추가한다.
4. runtime helper의 extension과 `response={status: Schema}`의 OpenAPI 계약이 어긋난다.
5. 기존 백스톱은 application 계층의 HTTP 변환 누수만 검사하므로 Schema 중복을 잡지 못한다.

## 2. 결정

### 2.1 신규 표준의 공통 base와 계약 scope

Django Ninja로 새 Problem Details 계약을 도입하고 프로젝트에 확립된 오류 Schema가 없으며 **단일 canonical `NinjaExtraAPI` + 단일 problem profile + dddjango 표준 레이아웃**을 채택했다면, 첫 HTTP BC부터 다음 경로를 그 계약 scope의 공통 오류 응답 계약으로 사용한다.

```text
<project_root>/common/ninja/response/error_out.py
```

정식 클래스명은 `ErrorOut`이다. `ProblemOut`은 새 코드에서 만들지 않는다.

```python
from ninja import Schema


class ErrorOut(Schema):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None
```

이는 RFC 9457 자체의 required 정책이 아니라 dddjango가 신규 표준 프로젝트에 제안하는 output profile이다. runtime body는 `type/title/status/detail`을 항상 포함하고 `instance`는 값이 없으면 생략한다. generated OpenAPI는 `title/status/detail`을 required, `type`을 `about:blank` default, `instance`를 optional nullable로 광고하며 이를 실제 생성 결과로 검증한다.

이 규칙은 일반적인 “두 소비자부터 `common/` 승격” 규칙의 좁은 예외다. `ErrorOut`은 미래의 재사용 helper가 아니라 단일 `NinjaExtraAPI`가 외부 클라이언트에게 공개하는 프로젝트 HTTP protocol profile이다.

중앙화 단위는 저장소 전체가 아니라 **contract scope**다. scope는 API 인스턴스/namespace, public·internal surface, API version, problem profile의 조합으로 식별한다. 같은 프로젝트라도 `/api/v1`과 `/api/v2`, public과 internal API가 서로 다른 required/default/extension 계약을 가지면 각각 독립 canonical base를 가질 수 있다. 기존 프로젝트의 version 디렉터리 규약을 우선하고, dddjango 표준 fallback은 다음과 같다.

problem profile 분리는 단순 이름표가 아니다. 서로 다른 API 인스턴스/namespace/version이거나 core envelope의 required/default, 전역 wire alias, Pydantic config, 공통 extension 의미처럼 외부에서 관찰되는 계약 차이가 있어야 하며, architect가 그 차이와 compatibility 이유를 리터럴로 기록한다. problem-specific concrete extension의 차이는 scope 분리 근거가 아니다. 같은 API instance/namespace/version과 같은 core profile이면 같은 scope로 추정하고, 동일 core 복제를 피하려고 근거 없이 BC 이름을 profile 이름으로 바꾸는 것은 허용하지 않는다.

```text
common/ninja/response/v1/error_out.py
common/ninja/response/v2/error_out.py
```

version만으로 경로를 가를 수 없으면 기존 API package/namespace를 discriminator로 우선 사용한다. 확립된 규약이 없는 신규 표준 fallback은 다음과 같다. `<api_namespace>`는 controller가 실제 mount된 public/internal namespace이고, 별도 profile slug는 위의 관찰 가능한 차이가 있을 때만 허용한다.

```text
common/ninja/response/<api_namespace>/error_out.py
common/ninja/response/<api_namespace>/<version>/error_out.py
common/ninja/response/<api_namespace>/<version>/<profile_slug>/error_out.py
```

중복 비교와 reviewer blocker는 동일 contract scope 안에서만 적용한다.

first-BC common은 단일 소비자일 때 root common package 하나를 먼저 만드는 비용을 의식적으로 수용한다. 대신 두 번째 동일-scope BC가 생길 때 파일 이동, import 갱신, 공개 alias 판단이 필요 없고 클라이언트 protocol identity가 첫 표면부터 고정된다. 두 번째 표면이 다른 version/profile이면 공유하지 않는다.

예외 범위는 Schema에만 적용한다. 오류 처리 코드는 다음 세 종류로 나눈다.

1. generic problem serializer, transient recognizer, framework `HttpError`/validation/catch-all handler는 실제 둘 이상의 경계가 공유할 때 `common/ninja/errors.py`로 승격한다. 단일 BC에서만 쓰이면 그 BC presentation에 둔다.
2. BC-specific exception→problem mapping은 BC presentation에 계속 로컬로 두고, shared API integration이 등록만 한다. common 모듈이 모든 BC의 도메인 예외를 import하지 않는다.
3. 공통 `ErrorOut` Schema만 위 birth-common 예외를 적용한다.

### 2.2 기존 프로젝트 우선

다음 우선순위를 적용한다.

1. 프로젝트에 이미 확립된 공통 오류 Schema와 import 경로가 있으면 이름이 다르더라도 외부 계약과 기존 관례를 먼저 존중한다. 기존 공용 코드가 `src/shared/http/` 같은 레이아웃을 쓰면 `<root>/common/`을 새로 만들지 않고 그 등가 canonical path를 사용한다.
2. 하나의 기존 BC 로컬 Schema만 있고 새 consumer가 없으며 error wire contract가 변경되지 않으면, 그 BC의 다른 코드를 touch하더라도 소급 이동하지 않는다.
3. 기존 BC 로컬 Schema를 새 BC도 동일하게 필요로 하면 공통 경로로 승격하되, 공개 import 소비자가 확인되면 G1에서 호환 alias 또는 단계적 이주 여부를 결정한다.
4. DRF, plain Django view, 서버 렌더 표면에는 Django Ninja `ErrorOut`을 강제하지 않는다.
5. 같은 필드명이더라도 contract scope, required/default, alias, validator, config 또는 의미가 다르면 동일 계약으로 단정하지 않는다.

### 2.3 BC 로컬 Schema의 허용 조건

BC 로컬 오류 Schema는 공통 base를 복사하는 파일이 아니라 문서화된 problem-specific extension 계약일 때만 허용한다.

```python
from common.ninja.response.error_out import ErrorOut


class InventoryConflictErrorOut(ErrorOut):
    available_quantity: int
```

허용 조건은 모두 충족해야 한다.

1. 승인된 설계 명세가 extension의 wire key, 타입, 의미를 명시한다.
2. 로컬 클래스가 공통 `ErrorOut`을 상속한다.
3. controller의 `response={...}`가 base가 아니라 concrete Schema를 선언한다.
4. extension이 같은 contract scope의 다른 problem/operation과 공유되지 않는다는 현재 근거가 있다.

금지한다.

- core 필드를 BC 로컬에서 다시 선언
- `extensions: dict[str, object]` 같은 범용 bag으로 계약을 숨김
- `extra="allow"`로 OpenAPI에 없는 임의 필드를 허용
- 모든 BC의 problem type과 extension을 공통 거대 union/registry로 통합
- domain/application 계층이 `ErrorOut`을 import

동일 contract scope에서 key/type/required/default/alias/validator/config/meaning이 같은 concrete extension 계약을 둘 이상의 problem/operation이 실제로 공유하면 concrete Schema 전체를 `common/ninja/response/`로 승격한다. 동등성이 불명확하면 자동 통합하지 않고 architect로 반송한다.

framework validation의 `invalid-params`처럼 API scope 전체에 적용되는 extension은 첫 사용부터 scope-common concrete Schema로 둔다.

```python
from ninja import Field, Schema


class InvalidParamOut(Schema):
    name: str
    reason: str


class ValidationErrorOut(ErrorOut):
    invalid_params: list[InvalidParamOut] = Field(alias="invalid-params")
```

OpenAPI와 runtime wire key가 모두 `invalid-params`인지 계약 테스트로 확인한다.

### 2.4 runtime body와 Schema 정합

core-only `problem()`은 공통 core Schema를 실제로 serialize하고, `instance`가 있을 때만 wire body에 포함한다. 임의 `**extensions`로 Schema를 우회하지 않는다. extension-bearing mapping은 승인된 concrete Schema 인스턴스를 만들고 같은 response 변환점을 통과시킨다.

```python
def problem_response(body: ErrorOut) -> Response:
    return Response(
        body.model_dump(by_alias=True, exclude_none=True),
        status=body.status,
        content_type="application/problem+json",
    )


def problem(
    status: int,
    *,
    title: str,
    detail: str,
    type: str = "about:blank",
    instance: str | None = None,
) -> Response:
    return problem_response(
        ErrorOut(
            type=type,
            title=title,
            status=status,
            detail=detail,
            instance=instance,
        )
    )
```

예를 들어 inventory conflict mapping은 `InventoryConflictErrorOut(..., available_quantity=...)`를 만들어 `problem_response()`에 넘긴다. core-only status가 선언되지 않은 extension key를 내보내거나 concrete Schema 밖의 key를 response에 섞는 것은 계약 위반이다.

`type` URI, 안정적인 `title`, exception→status 매핑, `detail`, problem-specific extension 값 생성은 presentation의 problem mapping이 소유한다. 공통 `ErrorOut`은 이 카탈로그를 소유하지 않는다.

Schema와 runtime helper는 정적 문구만으로 일치한다고 간주하지 않는다. 신규 contract scope의 core profile은 `type/title/status/detail`의 runtime 존재, `instance` 부재 시 omission, 예상 밖 extension key 부재, generated OpenAPI required/default/nullable을 최소 한 번 검증한다. extension-bearing status마다 다음 두 외부 계약을 추가로 실제 artifact로 검증한다.

1. generated OpenAPI의 해당 status가 concrete Schema를 참조하고 properties/required/default/alias가 명세와 일치한다.
2. TestClient 응답이 `application/problem+json`, HTTP/body status 일치, required extension과 wire alias 보존, concrete Schema 밖 key 부재를 만족한다.

Ninja의 현행 수용 한계 때문에 OpenAPI media type이 `application/json`으로 표시될 수 있다. OpenAPI 검증은 media type이 아니라 status별 Schema ref/shape를, runtime 검증은 실제 `application/problem+json`을 본다.

## 3. 역할 소유권

### 3.1 design-architect — 결정 책임

새·변경 Ninja API 표면을 설계하기 전에 다음을 조사한다.

- `common/ninja/response/`와 그에 준하는 기존 공통 응답 패키지
- `application/*/presentation_layer/schema/**/*error*.py`
- 기존 controller의 오류 `response={...}` 선언
- runtime problem helper/handler와 외부 공개 import 소비자

설계 명세에 다음 열한 슬롯을 반드시 채운다.

```text
Error response schema
- contract scope: <API instance/namespace + public/internal + version + problem profile>
- scope evidence: <동일 scope 추정 또는 관찰 가능한 wire 차이와 compatibility 이유>
- existing canonical path: <경로 또는 없음>
- base action: reuse | create-common | promote-to-common | preserve-brownfield
- canonical base: <import path와 class>
- common core profile: <필드의 타입·required/default 정책>
- local concrete action: none | reuse | create | promote
- local concrete schema: <없음 또는 경로·class>
- local justification: <extension key·type·meaning 또는 없음>
- response declaration: <status → concrete schema>
- compatibility: <기존 import/body/OpenAPI 영향 또는 없음>
```

이 열한 항목 중 하나라도 없으면 명세는 Phase 2 입력으로 불완전하다.

### 3.2 coder — 구현 전 재검증 책임

coder는 설계를 다시 결정하지 않지만 새 오류 Schema를 만들기 전에 reuse-before-create preflight를 실행한다.

1. 공통 오류 Schema와 모든 BC의 관련 Schema를 재검색한다.
2. 명세의 `existing canonical path`가 현재 트리와 일치하는지 확인한다.
3. 공통 base가 있으면 import하고 core 필드를 재선언하지 않는다.
4. 로컬 Schema는 명세가 extension을 명시했을 때만 concrete subclass로 만든다.
5. 명세가 로컬 복제를 요구하거나 현재 트리와 어긋나면 임의 보정하지 않고 Coordinator에 구조화된 mismatch를 보고한다. Coordinator가 G1/G1′에서 design-architect로 반송한다.
6. `response={...}`가 실제 concrete Schema를 가리키는지 확인한다.
7. acceptance가 만든 core-only 및 extension OpenAPI/runtime 계약 테스트를 실제 실행한다.

### 3.3 design-review-api와 acceptance-tester — 외부 계약 책임

`design-review-api`는 물리 파일 경로를 감사하지 않는다. 대신 contract scope와 scope evidence, core profile의 required/default/전역 alias/config, extension wire key/type/meaning, version compatibility, status별 concrete response 계약이 완결됐는지 검토한다. BC 이름만 바꾼 profile 분리와 extension-bearing status의 base-only response 선언은 반송한다.

`acceptance-tester`는 contract scope마다 대표 core-only status의 generated OpenAPI required/default/nullable과 runtime core 4필드·`instance` omission·예상 밖 key 부재를 검증한다. extension-bearing status마다 concrete Schema ref/shape와 TestClient runtime body/content-type/정확한 key 집합을 추가 검증하는 바깥 Red를 소유한다. 내부 helper 자체를 직접 테스트하지 않는다.

### 3.4 discipline-reviewer — 독립 감사 책임

discipline-reviewer는 DRY·배치·import·승인 명세 집행만 감사한다. 다음은 Phase 2 blocker다.

- 공통 base가 있는데 BC가 core shape를 다시 선언
- 이름만 바꾼 동일 Schema 복제
- 설계 근거 없는 BC 로컬 오류 Schema
- extension Schema가 공통 base를 상속하지 않음
- domain/application이 common Ninja Schema에 의존
- coder가 명세와 트리의 불일치를 발견하고도 반송 없이 구현

required/default, alias, validator, config, problem 의미, generated OpenAPI와 runtime body의 기술적 정확성은 새로 판정하지 않는다. 명세와 acceptance 결과가 충돌하거나 동일 계약인지 불명확하면 각각 architect/API reviewer/acceptance-tester 소유로 반송한다.

### 3.5 Coordinator — 게이트와 반송 책임

Coordinator는 직접 배치를 결정하지 않는다.

- 승인 스코프가 Ninja endpoint/error contract 또는 오류 response Schema를 새로 만들거나 변경할 때, G1 제시 시점과 승인 후 Phase 2 dispatch 직전에 현재 명세의 11항목 `Error response schema` 슬롯 완결성을 확인한다. 프로젝트에 기존 Ninja API가 있다는 사실만으로 순수 내부 버그 수정에 이 슬롯을 새로 요구하지 않는다.
- Phase 1에서는 API reviewer, Phase 2에서는 acceptance-tester·coder·discipline-reviewer에게 해당 슬롯 중 각 책임에 필요한 부분을 전달한다.
- coder/reviewer가 발견한 명세·트리 불일치는 G1/G1′로 반송한다.
- G2에서 공통 import, 허용된 로컬 concrete Schema, generated OpenAPI와 runtime 계약 테스트 결과를 함께 보고한다.

## 4. 검증 전략

이 변경은 프롬프트·스킬 동작 변경이므로 문서 수정 전에 현행 역할의 실패를 관찰한다.

1. 현재 design-architect가 기존 common Schema를 명세에 기록하는지 확인한다.
2. 현재 coder가 명세가 로컬 생성을 요구해도 common을 재검색하고 반송하는지 확인한다.
3. 현재 discipline-reviewer가 동일 core 복제를 blocker로 잡는지 확인한다.
4. 현재 acceptance-tester가 core-only와 extension OpenAPI/runtime drift를 실제 Red로 만드는지 확인한다.
5. 현재 design-review-api가 근거 없는 profile 분리와 base-only extension response를 반송하는지 확인한다.
6. 현재 Coordinator가 slot 누락과 stale-spec handoff에서 다음 phase를 차단하는지 확인한다.

수정 뒤 같은 압력 시나리오를 fresh context로 반복한다. 역할 격리 시험은 simulation으로 표시하고, committed bootable fixture와 고정된 role+skill/reference bundle을 새 임시 git copy에서 실행한다. agent에게 oracle을 노출하지 않고 실제 search trace, pytest Red/Green, design-spec diff, 생성/비생성 파일, import target, reviewer `file:line` finding으로 판정한다. 자기보고와 키워드 복창은 PASS 증거가 아니다.

Coordinator 실제 배선은 별도 fresh `/dddjango` 위반 주입으로 확인한다. missing-slot, stale-spec handoff, extension OpenAPI/runtime Red 전달, exact duplicate reviewer blocker를 양 runtime에서 각각 3회 실행하여 architect→coder→acceptance/reviewer 반송과 G1/G2 차단이 실제로 발화하는지 본다.

결정적 checker는 선결정하지 않는다. 역할 prompt 보강과 Coordinator live injection 뒤에도 동일 scope의 direct exact core 복제가 반복되면 고정밀 subset의 checker 필요성을 별도 decision gate로 올린다. version/required/default/alias/validator/config/meaning 비교가 필요한 형태는 계속 의미 레인에 둔다. 광범위 이름·필드 집합 검사는 채택하지 않는다.

## 5. 비목표와 안전 경계

- 기존 역사 평가 결과를 소급 수정하지 않는다.
- API body의 의미를 단순 물리 이동 때문에 변경하지 않는다.
- 기존 공개 import의 alias를 자동 생성하지 않는다.
- 모든 오류를 하나의 concrete Schema로 평탄화하지 않는다.
- architecture-api의 일반 RFC 9457 설명을 프로젝트 Python 경로 규칙으로 오염시키지 않는다.
- acceptance-tester와 API design reviewer에게 내부 파일 배치 감사를 넘기지 않는다.
- 공식 `workspace/eval` 채점 체계를 이번 prompt-conformance 실험 때문에 재개하거나 역사 결과를 재채점하지 않는다.
- checker decision gate가 비채택으로 끝나면 manifest version과 백스톱 수를 올리지 않는다. checker가 필요하다는 반복 증거가 나오면 구현을 멈추고 별도 설계 승인을 받는다.
