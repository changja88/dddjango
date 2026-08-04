# API 에러 관리 플러그인 개정 구현 계획 (적대 리뷰 반영판)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans`. 정본을 먼저 고친 뒤 미러를 갱신한다. 아래 체크박스는 승인 당시의 작업 분해를 보존한 역사 기록이며 소급 완료 표시는 하지 않는다. 실제 실행·완료 상태와 미해결 항목은 이 문서의 `Status`, `Implementation Adversarial Review Record`, 최종 검증 증거를 기준으로 판정한다.

**Status:** ErrorOut shape 비고정 보정·구현·재검증 완료 · v4 사용자 동결 승인 대기

**Approved design:** `workspace/design/2026-08-03-api-error-management-design.md` (설계 본문 commit `73c575e`; 사용자 승인·구 설계 superseded metadata는 이 계획과 같은 문서 기준선 commit에 기록)

**Goal:** dddjango가 새로 만드는 단일 Django Ninja JSON API 표면의 에러 계약을 중앙 handler/RFC 9457 기본값에서, 공통 wire shape 하나 + BC별 `ErrorCode`/`ErrorOut` + controller 직접 `Status` 반환 방식으로 바꾼다. Claude와 Codex 런타임, 11개 reference 미러, 19개 결정적 백스탑, 활성 평가 기준이 같은 계약을 말하게 한다.

**Architecture:** 배포 정본은 `dddjango/`다. `references/final.md`는 Claude 정본을 먼저 수정한다. `corpus_mirror_sync.py --write`는 workspace source mirror에는 본문만 splice하고 Codex 배포본에는 전체 파일을 byte-exact 복사한다. workspace/Codex mirror를 직접 편집하지 않는다. 역할·Coordinator·`SKILL.md`는 플랫폼 형식을 유지한 의미 미러로 수동 갱신한다. checker는 Claude 정본을 구현한 뒤 Codex 배포 위치에 byte-exact 복사한다. 집행은 ① 설계의 사용자 승인 게이트, ② reference와 역할 프롬프트, ③ 19개 결정적 checker, ④ 대상 프로젝트의 runtime/OpenAPI 계약 테스트, ⑤ discipline reviewer의 의미 점검으로 나눈다.

## 0. 구현 경계와 변경 불변식

### 0.1 이번 작업에 포함

- Claude 플러그인 정본 `dddjango/`의 API 에러 reference, 상시 캐리어 `SKILL.md`, Coordinator, 관련 역할 5개, 관련 checker를 개정한다.
- Codex 플러그인 `codex-dddjango/`의 의미 미러와 checker byte mirror를 같은 계약으로 개정한다.
- `README.md`, 활성 eval rubric/method/golden을 새 출력 프로필에 맞춘다.
- checker용 합성 발화 매트릭스와 실제 Ninja/Ninja Extra runtime fixture를 개발/평가 도구로 추가해 양성·음성·brownfield 카브아웃과 `Status`/직렬화 계약을 반복 검증한다.
- `workspace/DEVLOG.md`에 변경 이유, checker 소유권, 평가 버전 경계를 기록한다.

### 0.2 이번 작업에서 하지 않음

- `/Users/hyun/Desktop/broccoli-server` 프로덕션 코드는 이 저장소 작업에서 수정하지 않는다. 그 서버는 설계 근거 사례이며 실제 이주는 별도 작업이다.
- 과거 `workspace/eval/results/*.md`를 새 표준으로 다시 써서 역사적 관측을 바꾸지 않는다.
- 기존 RFC 9457 지식 자체를 삭제하지 않는다. 기존 프로젝트가 이미 채택한 RFC 계약은 brownfield 프로필로 보존한다.
- 플러그인 manifest 버전 변경, tag, push, marketplace release는 하지 않는다. 구현·검증 승인 뒤 별도 release 작업으로 남긴다.
- 서버렌더 Django, DRF, plain Django view의 에러 규칙을 새 Ninja 프로필로 이주하지 않는다.
- checker 수를 늘리지 않는다. `check-catch-all-handler.py` 삭제와 `check-api-error-controller-contract.py` 추가를 상쇄해 19개를 유지한다.

### 0.3 절대 보존할 계약

1. 신규 dddjango code 프로필의 공통 경로는 `common/ninja/response/error_out.py::ErrorOut`이다.
2. 플러그인은 공통 `ErrorOut` property를 정하지 않는다. 기존 프로젝트의 관찰된 exact shape 또는 신규 G1에서 별도로 승인된 exact shape가 기준선이며, 필드·타입·required/default·nullable·Field metadata·model config/legacy Config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 의미 변경은 checker 통과를 승인으로 간주하지 않고 Coordinator가 사용자에게 별도로 멈춰 묻는다.
3. `common/ninja/response/`의 추적 대상 프로덕션 Python 파일은 빈 `__init__.py`와 `error_out.py`뿐이다.
4. 에러 계약이 있는 BC는 `<bc>/presentation_layer/schema/error_out.py` 하나에 `<Bc>ErrorCode(StrEnum)` 하나, `<Bc>ErrorOut(ErrorOut)` 하나, 준비된 concrete ErrorOut 전부를 둔다.
5. 준비된 concrete ErrorOut은 `<Bc>ErrorOut`을 상속하고 새 필드·validator·child `model_config`를 만들지 않는다. 재선언 field는 공통 annotation/nullability와 default를 제외한 `Field(...)` metadata를 그대로 보존하며, 사건별 default를 채워 인자 없이 생성된다.
6. 알려진 BC 예외/실패 Result는 해당 controller가 직접 concrete ErrorOut 또는 BC base ErrorOut으로 바꾸고 `Status(<승인된 HTTP status 표현>, error)`를 반환한다. `status` body property는 필수가 아니다.
7. 오류 factory/helper/serializer/exception mapping 함수와 custom exception handler/catch-all을 만들지 않는다.
8. framework 401/403/route 404/검증 422/throttle 429/일반 `HttpError`/raw infra/미식별 500은 Django Ninja/Django 기본 처리에 맡긴다.
9. controller `try`에는 예외를 반환 계약으로 삼는 application 호출 최상위 문장 하나만 둔다. 구체 예외만 catch하고 입력 준비·성공 변환은 `try` 밖에 둔다. 실패 Result/None을 반환하는 호출은 모든 `try` 밖에서 대입하고 바로 다음 실행 문장에서 판정한다.
10. controller가 직접 반환하는 BC 오류만 `response={status: <Bc>ErrorOut}`에 선언한다. `openapi_extra`와 생성 OpenAPI 사후가공을 사용하지 않는다.
11. 비오류 성공 arm의 파일·스트리밍·redirect와 schema 없는 204는 에러 helper 금지/일반 JSON schema 우회 규칙의 대상이 아니다. 알려진 BC 실패 arm에서 이 응답들로 ErrorOut 직접 반환 계약을 우회하는 것은 허용하지 않는다.
12. project `api.py`는 API 인스턴스와 API 자체 설정만 소유한다. BC registrar 조립은 project `urls.py`, DI 조립은 기존대로 BC `composition_root.py`가 소유한다. 두 composition root를 합치지 않는다.

## 1. 정독 결과와 변경 표면

### 1.0 정독 범위와 권위 분류

| 묶음 | 정독/대조 범위 | 계획에서의 취급 |
|---|---|---|
| Claude 배포본 | `dddjango/` 추적 파일 50개: manifest, command 1, agents 7, `SKILL.md` 11, reference 11, checker 19 | 정본. 관련 reference/SKILL/역할/checker를 먼저 수정 |
| Codex 배포본 | `codex-dddjango/` 추적 파일 51개: manifest, orchestrator·역할·지식 SKILL, reference 11, checker 19, `openai.yaml` | reference/checker는 byte mirror, SKILL은 의미 mirror. manifest/interface는 이번 계약 변경과 무관 |
| workspace reference | `workspace/reference/**` 33개와 `corpus_mirror_sync.py` | `final.md` 11개는 source body mirror. `external/internal/review`와 `spec.md`는 원재료·검토 기록이라 본문 수정 금지 |
| 설계·계획·개발 기록 | 현행/과거 `workspace/design`, `workspace/plan`, `workspace/DEVLOG.md` | 2026-08-03 설계가 정본. 2026-07-16 설계는 당시 근거를 보존하고 superseded metadata만 표시. 과거 계획은 수정하지 않음 |
| 평가 코퍼스 | 활성 rubric/method/metrix/golden, `workspace/eval/results` 14개, eval README | 활성 4개 기준만 새 epoch로 변경. 결과 14개는 산출 당시 기준의 역사 기록으로 보존 |
| 생성 시각화 | `workspace/flow/dddjango-timeline.html`, `workspace/tools/smoke_timeline.html`, 이번 정독용 `graphify-out/` | 전자는 현행 파이프라인을 설명하는 파생 carrier라 문구만 동기. 후자 둘은 역사 관측/조사 artifact라 구현 diff에서 제외 |

정독은 파일 목록 확인만으로 끝내지 않았다. Graphify의 scan/AST/semantic-chunk 중간 산출물로 API reference→Ninja 구현→houserules→역할→checker/eval 후보 관계를 좁힌 뒤, 각 파일의 직접 정독과 grep으로 실제 전파 경로를 확정했다. Python checker는 AST 구조와 직접 참조를 대조했다. 아래 표와 각 Task는 그 결과에서 실제 충돌이 확인된 활성 표면만 변경 대상으로 좁힌 것이다.

| 현재 코퍼스 | 새 계약 | 주 변경 소유자 |
|---|---|---|
| `architecture-api`가 RFC 9457을 모든 신규 오류의 단일 기본값으로 서술 | 일반 RFC 지식은 유지하되 dddjango 신규 Ninja 기본값을 code JSON 프로필로 우선 선택 | `architecture-api` reference/SKILL |
| `implementation-django-ninja`가 operation `raise` + 중앙 helper/handler/catch-all을 처방 | controller의 좁은 `try` + 구체 catch + 직접 `Status` 반환, framework 기본 오류 | Ninja reference/SKILL, coder |
| houserules가 `<problem>_error_out.py`와 helper/handler 승격을 허용 | BC당 단일 `schema/error_out.py`, error helper/handler 승격 금지 | houserules reference/SKILL |
| 테스트 규칙이 `type/instance/problem+json`과 extension profile을 고정 | 승인된 프로젝트별 exact JSON shape, no-arg concrete, 승인 HTTP status, framework 기본 body 비-snapshot | implementation-test reference/SKILL, acceptance tester |
| 서버렌더 reference가 삭제될 `common.ninja.errors` retry 판별 helper를 import | HTML 503 의미는 보존하고 판별은 현재 유일 consumer인 web middleware-local | implementation-django-web reference |
| 범용 Clean Code가 try/catch를 항상 별도 함수로 추출하도록 읽힘 | adapter entrypoint가 승인 mapping owner이면 작은 구체 catch를 inline 유지 | discipline-cleancode reference |
| Coordinator/역할이 Error response 11-slot과 중앙 변환점을 강제 | 아래 12-slot과 사용자 승인 게이트, controller 직접 매핑을 강제 | Coordinator + 관련 역할 5개 |
| `check-error-centralization`이 application HTTP 누수만 확인 | 공통/BC ErrorOut 구조·Enum·무인자·중복 code 계약을 검사 | checker 정본/미러 |
| `check-catch-all-handler`가 catch-all 존재를 강제 | 삭제하고 controller 계약 checker로 교체 | checker 정본/미러, 게이트 목록 |
| `check-openapi-error-declaration`이 `openapi_extra` 누락만 touched-file에서 검사 | code-profile controller의 실제 반환 status↔`response=`를 전수 대조하고 수동 후가공을 금지 | checker 정본/미러 |
| eval `NJ-7`이 catch-all을 합격 조건으로 둠 | 동일 ID/차원 수를 framework 기본 보존 + controller 직접 오류 계약으로 재정의 | 활성 RUBRIC/METHOD/metrix |
| 현행 eval/timeline이 결과 부재·16 checker·33차원·touched-only를 서술 | 실제 14개 역사 결과, 19 checker, 34차원, profile별 full-tree 범위로 정합화 | eval README/활성 기준, pipeline timeline |

### 1.1 Error response contract 12-slot

Error response가 있는 설계 명세는 다음 12개 항목을 표 형태로 반드시 가진다. `none`은 허용하지만 이유를 같이 쓴다.

1. `contract scope` — API instance, namespace/version, public/internal, project-relative API/controller/URLconf/BC registrar module 목록, 완전한 `scope-bc`와 그중 `error-bc` 부분집합
2. `scope evidence` — 현재 API/Schema/handler/OpenAPI와 외부 클라이언트 계약 증거, 프로젝트의 승인된 모든 API surface별 `code-profile | preserve` module inventory(API/controller/URLconf/registrar/error/common). 현재 scope 밖 surface도 공유 여부를 판정할 만큼 경로와 profile을 적는다.
3. `error profile` — 신규 기본 `dddjango-code-json` 또는 `preserve-established`
4. `compatibility/rollout` — breaking 여부, version 분리/동시 배포/보존 결정
5. `common ErrorOut action` — `reuse | create | approved-change | none`과 canonical import
6. `common ErrorOut shape/approval` — 플러그인 기본 필드 없이 실제 exact field set·타입·required/default·nullable·Field metadata·model config/legacy Config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 직렬화와, 기준선 변경 시 별도의 사용자 승인 증거
7. `BC error module` — 정확한 `<bc>/presentation_layer/schema/error_out.py` 또는 `none`
8. `BC ErrorCode` — `<Bc>ErrorCode` 멤버와 wire 문자열
9. `BC ErrorOut` — `<Bc>ErrorOut` 상속과 승인된 공통 식별자 필드의 `<Bc>ErrorCode` narrowing
10. `prepared error mapping` — 내부 예외/실패 Result → concrete/base → exact approved body/header와 HTTP status
11. `controller mapping` — application 호출, 좁은 `try`, catch 타입, direct two-argument `Status` 반환 위치와 status 표현
12. `response/OpenAPI/tests` — endpoint별 HTTP status/schema, exact approved body, framework-default 제외, runtime/OpenAPI/no-arg 검증

`preserve-established`는 새 code 프로필을 섞는 면허가 아니다. 해당 scope의 기존 canonical 경로·media type·wire shape를 그대로 명시하고, 새 프로필로 바꾸려면 별도 compatibility 승인으로 `dddjango-code-json` 전환을 결정한다.
`dddjango-code-json`에서 5번 `common ErrorOut action`의 `none`은 허용하지 않는다. `error-bc`가 비어도 profile을 식별하는 공통 wire contract는 `reuse | create | approved-change` 중 하나여야 한다. 7~9번 BC 항목만 공개 BC 오류가 없다는 근거와 함께 `none`일 수 있다.

### 1.2 checker 활성 범위

산출물 형태나 BC 디렉터리만으로 신규 프로필을 추측하면 같은 `code` 필드·경로를 쓰는 brownfield, 같은 BC 안의 v1/v2 controller, 다중 API instance를 오인한다. 따라서 승인된 12-slot이 checker 활성화와 파일 membership의 권위다.

- **명시적 실행 계약:** positional `TARGET_DIR` 뒤에 `--error-profile`, `--scope <stable-scope-id>`, `--api-module <project-relative-path>`, 반복 가능한 `--controller-module <project-relative-path>`, `--scope-bc <snake_case>`, `--error-bc <snake_case>`를 전달한다. registrar 조립 slice에는 `--urlconf-module <project-relative-path>`와 반복 가능한 `--registrar-module <project-relative-path>`도 전달한다. schema checker에는 추가로 프로젝트 전체 canonical error module 후보를 분류한 `--project-code-error-module <path>`와 `--project-preserve-error-module <path>`를 반복 전달한다. `scope`는 사람이 읽는 진단 label일 뿐 selector가 아니다. 실제 selector는 정확한 source 경로·BC 집합·전역 module inventory다. 프로덕션 wire와 무관한 marker 파일·상수는 추가하지 않는다.
- **BC 집합 의미:** `scope-bc`는 해당 단일 API surface에 참여하는 전체 BC, `error-bc`는 공개 BC ErrorOut 계약이 있는 부분집합이며 `error-bc ⊆ scope-bc`다. 오류가 없는 BC는 `scope-bc`에만 들어가고 BC `error_out.py`가 없어도 정상이다. 다만 `dddjango-code-json` profile이면 `error-bc`가 비어도 canonical common `ErrorOut`은 항상 필요하다. 지정 `error-bc`의 BC module 부재와 common 부재는 artifact 생략 우회이므로 exit 2다.
- **지원 경계:** 이번 checker가 결정적으로 지원하는 단위는 승인 설계의 “명시적으로 분리된 단일 신규 API surface”다. API module에는 대상 API instance가 정확히 하나여야 한다. Coordinator는 checker 실행 전에 12-slot의 project-wide surface inventory를 서로 대조한다. 같은 profile의 여러 surface가 동일 common/error module을 승인해 재사용하는 것은 한 경로로 dedupe해 허용한다. 반면 같은 API/controller/URLconf/registrar/error/common module이 `dddjango-code-json`과 `preserve-established` 양쪽에 속하거나, 같은 경로가 같은 profile 안에서도 서로 다른 역할·계약으로 중복되거나, 동일 API module에 instance가 복수면 artifact로 profile을 추론하지 않고 exit 1 상당의 `STOP_FOR_USER_APPROVAL`로 G1에 반송한다. 개별 checker가 전달받지 않은 타 scope를 발견한다고 주장하지 않는다. 분리된 brownfield module은 검사 대상 source 목록에 섞지 않는다.
- **신규 프로필:** `dddjango-code-json`이면 common, 모든 `scope-bc` 계층, 모든 `error-bc` schema, 열거된 controller/API module의 선택된 전체 트리를 검사한다. 선택된 production source 집합은 Git tracked + untracked non-ignored이며 test/migration/cache/venv/generated artifact는 제외한다. symlink/root 탈출, 읽기 실패, 선택 파일 syntax error는 exit 1이다. git touched 여부로 구조 위반을 숨기지 않는다.
- **프로젝트 전역 code 유일성:** schema checker가 발견한 canonical error module 후보는 정확히 한 error-module inventory에 속해야 하며 누락·양쪽 중복·root 탈출은 exit 1이다. 승인 설계대로 `project-code-error-module` 전체의 `<Bc>ErrorCode` wire value는 프로젝트 전역에서 중복되지 않아야 한다. 독립 API version도 새 Enum에 같은 문자열을 복제하지 말고 동일 BC Enum을 재사용한다. canonical 모양이 같은 `project-preserve-error-module`의 RFC/code 문자열은 검색에서 제외한다. error-module inventory의 형태적 완전성은 checker가, 전체 surface/profile inventory의 의미상 완전성과 module 공유 여부는 G1/API reviewer와 Coordinator preflight가 보증한다. scope-local 완화는 별도 설계 승인 없이는 하지 않는다.
- **brownfield 검출력 보존:** `preserve-established`는 신규 schema/direct-Status 계약만 N/A다. 기존 `check-error-centralization`의 touched application HTTP 누수 직접형은 context checker로 옮겨 계속 실행하고, 기존 OpenAPI checker의 touched `openapi_extra`-only/`response=` 누락 검사는 그대로 유지한다. context S1~S3, 성공 schema 우회, transient 등 다른 legacy checker도 기존 범위를 유지한다. 기존 untouched 코드는 grandfather하되 이번 변경의 새 위반은 통과시키지 않는다.
- **자동 모드와 CLI 호환:** Error response가 아닌 G2에서 Coordinator는 `--error-profile auto`를 명시한다. 수동 `[TARGET_DIR]` 단독 호출을 호환한다면 진단용 auto로만 처리하고 “Error response G2 증거 아님”을 출력한다. `auto` 추론은 승인 프로필을 대신하지 않는다.
- **종료코드:** `0=clean/not-applicable/help`, `1=사용 오류·선택 범위 불완전·분석 불능`, `2=명백한 계약 위반`이다. `argparse` 기본 사용 오류도 1로 정규화한다. 활성 code mode의 필수 인자/파일 누락, root 밖 경로, 잘못된 BC 관계는 1이고, 지정 `error-bc` artifact 부재처럼 해석 가능한 계약 위반은 2다.

### 1.3 실행 전 작업트리 보호

- [ ] 이 계획 실행 전에 두 설계의 승인/superseded metadata와 이 계획이 하나의 문서 기준선 commit으로 기록돼 있는지 확인한다. 설계 본문 `73c575e`만 승인 metadata commit인 것처럼 인용하지 않는다.
- [ ] 구현 시작 즉시 `git status --short`, 현재 branch/HEAD, 대상 파일별 기존 diff를 기록한다.
- [ ] 구현 시작 parent의 full SHA와 `workspace/eval/results/*.md` tracked count(현재 14), `git status --porcelain -- workspace/eval/results`, 각 tracked result blob hash를 기록한다. 마지막 F2에서 같은 baseline과 대조한다.
- [ ] 이 계획의 대상 파일에 사용자 미커밋 변경이 이미 있으면 덮어쓰거나 함께 stage하지 않는다. 해당 파일만 중단해 사용자와 변경 경계를 먼저 정한다.
- [ ] 새로 생성되는 checker와 matrix 이외의 예상 밖 파일은 자동으로 포함하지 않는다. 정본→미러 도구가 만든 파일도 Task B5의 예상 경로와 대조한다.
- [ ] 과거 design/plan/eval result와 `workspace/reference/**/{external,internal,review}/**`는 읽기 근거이며 구현 본문 수정 대상이 아니다. 대체된 2026-07-16 설계의 후속 정본 metadata는 이 계획과 함께 선행 commit됐으므로 구현 중 다시 수정하지 않는다. 배포 reference 본문은 `dddjango/**/references/final.md`만 먼저 고친다.

---

## Part A — 먼저 실패하는 checker 발화 매트릭스

### Task A1: 단일 합성 매트릭스 도구 추가

**Files:**

- Create: `workspace/tools/api_error_backstop_matrix.py`

- [ ] Step 1: `tempfile.TemporaryDirectory` 안에 최소 Django/Ninja 소스 트리만 문자열 fixture로 만들고 checker를 `subprocess.run`하는 data-driven runner를 작성한다. Django/ninja import 실행은 하지 않고 AST checker의 exit code/stdout만 검증한다.
- [ ] Step 2: 각 case는 `name`, `files`, `checker`, checker별 `checker_args`(`TARGET_DIR`, profile/scope, 정확한 API/controller/URLconf/registrar source, scope/error BC, project code/preserve error-module inventory 포함), `expected_exit`, `expected_fragment`를 가진다. 실패 시 전체 case 이름과 실제 stdout/stderr를 출력하고 마지막에 통과 수를 출력한다. Coordinator prompt의 명령 계약에서 추출해 verifier가 합성한 명령도 같은 runner에서 실행해 문서용 인자와 checker CLI가 갈리지 않게 한다. 이를 별도 Coordinator renderer의 런타임 관측으로 부르지 않는다.
- [ ] Step 3: 정본 checker만 대상으로 RED를 먼저 실행한다.

```bash
python3 workspace/tools/api_error_backstop_matrix.py
```

Expected before implementation: 새 controller checker 부재 또는 새 계약 위반을 기존 checker가 놓쳐 non-zero.

- [ ] Step 4: 아래 최소 matrix를 모두 등록한다.

| 소유 checker | exit 0 사례 | exit 2 사례 | exit 1 사례 | reviewer-only 사각 |
|---|---|---|---|---|
| schema contract | common+error BC enum/base+2 concrete, plugin 기본 property와 body status가 없는 custom shape, 승인된 common default/nullable/field alias/model config, default+alias 또는 nullable 식별자, concrete 없이 발생별 base만 쓰는 BC, common은 있지만 `error-bc`가 빈 scope, `scope-bc`지만 `error-bc`가 아닌 오류 없는 BC, 같은 code profile 두 surface가 동일 common/BC Enum module을 dedupe해 재사용, canonical 모양이 같은 preserve error module을 preserve inventory로 제외한 surface | 지정 `error-bc` artifact 전무, common/init/error_out 누락·파일 증식(`error-bc`가 비어도 common 누락은 위반), common concrete, canonical module 밖 concrete, Enum/base 누락·복수, BC base가 식별자 외 field를 재선언하거나 식별자 annotation/nullability·required/default·Field metadata를 바꿈, child model_config, 잘못된 상속, concrete 새 field/validator 또는 annotation/Field metadata drift, 필수 기본값 누락, 문자열 식별자, 두 code scope/다른 API version이 같은 wire value를 별도 Enum에 중복 정의, `Literal`/`str` 식별자 | syntax/read/root 탈출, 필수 class base 해석 불능, profile/source/inventory 인자 누락, `error-bc ⊄ scope-bc`, 발견 후보의 inventory 누락·code/preserve 양쪽 중복 | project-wide surface inventory의 의미상 완전성, 공개 ErrorCode 필요성 |
| controller contract | sync/async `try`의 outer call 1문장, 구체 tuple catch가 하나의 prepared concrete로 수렴, no-arg concrete, 발생별 BC base, 모든 `try` 밖의 실패 Result/None 호출과 즉시 분기가 승인 ErrorOut을 준비해 2-argument `Status(<승인된 HTTP status 표현>, error)` 반환, 서로 다른 호출의 exception/Result 경로, 성공 전용 operation, mixed scope의 no-error owner controller, `Retry-After`, 같은 BC의 선택 밖 preserve controller/handler | 선택된 error-BC controller가 직접 import한 presentation-local 1-hop serializer/factory/mapping helper, decorator/register handler, 넓은 try/try 안 return·성공변환, 같은 호출의 exception+Result 이중 처리, broad/framework/raw-infra catch, 즉시 raise/catch, `except Known: raise HttpError|re-raise|handler forwarding`, managed catch의 direct `Status` 부재, concrete 인자 생성, 오류 tuple/raw Response/dict | 필수 ErrorOut/Status symbol의 불명 re-export, 선택 controller/활성 1-hop module syntax·read 실패, runtime binding 기준으로 필수 provenance가 불명확한 rebind | outer call이 실제 주 application 협력자인지, exception re-export가 사실상 broad인지, 직접 import한 1-hop class method·2-hop·선택 밖 helper |
| context isolation + legacy purity | BC presentation의 자기 error import, ACL의 업스트림 구체 예외 번역, 분리된 preserve scope, 기존 S1~S3 | root `api.py`의 BC import·GlobalErrorCode/ErrorOut/catalog/mapping/path branch, code scope domain/application/infra의 Ninja/ErrorOut, 타 BC ErrorCode/ErrorOut, ACL 밖 타 BC 예외, preserve 변경분의 기존 application HTTP 누수 직접형 | API instance 복수, API/controller module overlap·syntax/read 실패, source 인자 불완전 | 상대/동적 import, root mapping 동형, scope membership 완전성 |
| composition/registrar | 기존 DI V1~V3 정상·면제, 정확한 URLconf가 side-effect 없는 BC registrar를 한 번씩 명시 호출, 분리된 preserve URLconf/registrar | code registrar의 project API import·module-top-level `register_controllers`, URLconf의 registrar 미호출·중복 호출, registrar가 아닌 곳의 등록, 기존 off-tree/오배치/부재 DI V1~V3 | URLconf/registrar selector 누락·중복·overlap·syntax/read/root 탈출 | 동적 호출·re-export, registrar 내부의 의미상 잘못된 controller 집합 |
| OpenAPI | 직접 404/409 반환과 같은 BC base, framework status 미선언, 분리된 preserve API의 기존 `response=` 정합, security/example용 decorator metadata | 실제 오류 status 누락, 다른 BC/common/concrete schema, 직접 BC 반환 없는 401/403/route 404/422/429/500 ErrorOut 광고, framework response용 `openapi_extra`, 활성 code API의 `get_openapi_schema` override/monkeypatch/postprocessor, preserve 변경분의 `openapi_extra`-only 오류 선언 | 활성 code scope의 필수 error response mapping 해석 실패, source overlap | 동적 mapping, status별 식별자 subset 정밀도 |
| success bypass | Schema 객체/성공 `Status`, direct-import alias의 FileResponse/StreamingHttpResponse/redirect, schema 없는 204 | 선언된 JSON 200~203을 raw `JsonResponse`/`HttpResponse` 또는 그 direct alias로 반환 | 선택 파일 syntax/read 실패 | helper/re-export/subclass 경유 성공 우회 |

- [ ] Step 5: runner 자체가 checker 파일 수를 세지 않게 한다. checker count/byte mirror는 최종 검증에서 별도로 확인해 테스트 관심사를 섞지 않는다.
- [ ] Step 6: test/migration/docstring/log의 `code` 문자열, Pydantic `ClassVar`·private attribute, direct import/`as` alias·단순 상대 import·로컬 1단계 assignment, cache/untracked 비프로덕션 파일을 오탐 방지 case로 넣는다. common `ErrorOut`의 default/nullable/Field alias/model config는 승인 shape로 허용한다. BC base는 식별자 annotation wrapper·required/default·Field metadata를 보존하고, concrete는 새 field/validator/child model_config와 annotation/Field metadata drift 없이 사건별 default만 제공해야 한다. raw dict/helper/handler만 만들고 명세에 적힌 `error-bc` module을 생략하는 회피도 반드시 실패시킨다. direct alias는 지원하되 필수 Schema/Status의 불명 re-export는 exit 1, exception re-export의 broad 의미와 2-hop helper는 reviewer라고 oracle을 고정한다.
- [ ] Step 7: legacy 회귀를 별도 행으로 고정한다. `preserve-established`의 touched application HTTP 누수와 `openapi_extra`-only 오류 선언은 exit 2, 같은 기존 untouched 코드는 exit 0, 신규 schema/direct-Status/registrar 규칙은 N/A여야 한다. `auto`와 인자 누락의 차이는 네 API-error contract checker 각각에서, composition checker는 기존 positional mode와 명시 profile mode 양쪽에서 검증한다.

### Task A2: 실제 Django Ninja/Ninja Extra 호환성 선행 게이트

**Files:**

- Create: `workspace/eval/fixtures/api_error_contract/requirements.txt`
- Create: `workspace/eval/fixtures/api_error_contract/test_api_error_contract.py`

- [ ] Step 1: 구현 시점의 dddjango 문서상 지원 범위와 실제 신규 target의 Django pin을 먼저 근거로 삼고, 그 범위에서 공식 배포 metadata가 resolve하는 호환 최신 Django·django-ninja·django-ninja-extra·Pydantic·pytest를 `requirements.txt`에 exact pin한다. 기억이나 테스트를 편하게 통과하는 임의 버전을 고르지 않고 출처·확인일·해석된 버전을 실행 로그에 남긴다.
- [ ] Step 2: 외부 프로젝트에 의존하지 않는 최소 Django URLconf/settings와 `NinjaExtraAPI` class controller를 test 안에 만든다. 이 runtime fixture의 한 승인 shape 변형은 성공 Schema와 `ErrorOut` 모두 `status` 필드를 가진 다중 `response={...}` operation을 포함한다. 이는 과거 `Status` wrapper와 body의 `status` 필드 충돌로 500이 난 회귀를 직접 재현하는 조합이지 plugin 기본 property가 아니다. body status가 없는 custom shape는 A1 matrix에서 별도로 고정한다.
- [ ] Step 3: 실제 mounted Django client로 다음을 검증한다.

  - concrete ErrorOut 전수 발견과 `ConcreteErrorOut()` 실제 생성
  - Enum 밖 문자열 code 거부와 common exact field/type/required set
  - 성공 경로가 body에도 `status`가 있는 `SuccessOut`을 `Status(2xx, success)`로 반환하고, 다중 `response={success, errors...}`에서 정확한 성공 Schema를 골라 500이 되지 않음
  - sync/async controller의 direct two-argument `Status` 직렬화
  - 승인된 HTTP status와 slot-6 exact body, 승인된 BC 오류 header 일치
  - 인증 backend가 실패 시 `None` 또는 `AuthenticationError`를 사용하고 `ErrorOut`을 `request.auth`로 반환하지 않음
  - 일반 `HttpError`와 기본 401/403/route 404/422/429/미식별 500이 BC code/shape로 바뀌지 않음
  - test client의 exception re-raise를 끄고 `DEBUG=False` 500 실제 HTTP 응답에서 traceback 비노출; framework body exact snapshot 금지
  - FileResponse, StreamingHttpResponse, redirect, schema 없는 204가 ErrorOut 계약으로 오인되지 않음
  - `urls.py` registrar 조립으로 route가 실제 mount됨
  - 생성 OpenAPI의 직접 BC status→`<Bc>ErrorOut`, `application/json`, framework BC ErrorOut 비광고

- [ ] Step 4: framework 401의 `WWW-Authenticate`와 429의 `Retry-After`는 실제 값을 기록한다. 승인된 기존/public 계약이 이 header를 요구하는데 framework default가 제공하지 않으면 helper/handler를 몰래 추가하지 말고 `preserve-established` 또는 별도 계약 결정을 위해 G1/사용자에게 반송한다. 신규 in-house 기본 profile은 framework가 실제 제공하는 header만 계약하며, BC가 공개한 503 등은 controller가 승인된 header를 직접 보장한다.
- [ ] Step 5: 격리 환경에서 bytecode를 쓰지 않고 실행한다.

```bash
uv run --isolated --no-project \
  --with-requirements workspace/eval/fixtures/api_error_contract/requirements.txt \
  -- python -B -m pytest -q -p no:cacheprovider workspace/eval/fixtures/api_error_contract/test_api_error_contract.py
```

Expected: skip/xfail 없이 사전 기록한 테스트 수가 모두 PASS. `Status`가 지원 pin과 위 Schema 조합에서 500/오직 tuple로만 동작하면 승인 설계와 구현 전제가 충돌한 것이므로 Part B로 진행하지 않고 `STOP_FOR_USER_APPROVAL`로 반송한다. tuple fallback이나 Schema의 `status` 필드 개명으로 조용히 우회하지 않는다.

- [ ] Step 6: 이 fixture는 플러그인 개발/평가 증거이지 타깃 프로젝트를 검사하는 20번째 runtime checker가 아니다. 실제 기능 구현 때는 승인된 target pin과 endpoint 계약 테스트를 다시 실행한다.

---

## Part B — reference 정본과 상시 캐리어

### Task B1: architecture-api — 프로필 선택을 일반 RFC 지식보다 앞세우기

**Files:**

- Modify: `dddjango/skills/architecture-api/references/final.md`
- Modify: `dddjango/skills/architecture-api/SKILL.md`
- Modify semantic mirror: `codex-dddjango/skills/architecture-api/SKILL.md`

- [ ] Step 1: 기존 RFC 9457 설명을 “선택 가능한 일반/기존 계약 프로필”로 유지하고, §6 앞에 error profile 선택 순서를 추가한다: 확립 계약 보존 → 신규 dddjango Ninja면 `dddjango-code-json` → 별도 요구가 있을 때 RFC 9457.
- [ ] Step 2: 신규 기본 프로필의 wire 계약을 `application/json`, 프로젝트별 승인 exact shape, BC 식별자 안정성, mapping별 HTTP status, framework 기본 오류 비계약화로 적고 plugin 기본 property 목록을 두지 않는다.
- [ ] Step 3: “모든 오류는 Problem Details”, “status마다 type URI”처럼 무조건형인 체크리스트·멱등 replay 문구를 “선택된 error profile”로 바꾼다. idempotency outcome→HTTP 표현의 소유자는 중앙 handler가 아니라 해당 controller/presentation임을 고친다.
- [ ] Step 4: RFC 9457의 `type`, `about:blank`, `application/problem+json` 예시는 RFC 프로필 절 안에만 남긴다. dddjango code 프로필과 같은 scope에서 혼합하지 않는다고 명시한다.
- [ ] Step 5: Claude/Codex 두 `SKILL.md`의 핵심 원칙과 라우팅 설명을 같은 우선순위로 줄여 넣는다. “RFC 9457 강제” 한 줄을 제거하는 데서 끝내지 말고 brownfield 보존 조건을 함께 넣는다. 플랫폼 형식은 유지하고 의미를 대조한다.
- [ ] Step 6: 일반 401 `WWW-Authenticate`·429 `Retry-After` 규범과 framework-default profile의 실제 capability를 충돌 없이 서술한다. 확립 계약이 header를 요구하면 보존/별도 설계 대상으로 올리고, framework가 주지 않는 header를 맞추려고 금지된 global handler/helper를 자동 생성하지 않는다. BC가 직접 공개하는 retryable 오류의 `Retry-After` 의무는 유지한다.
- [ ] Step 7: 설계 §12의 일반 판단을 빠짐없이 보존한다. 클라이언트가 구분·관찰할 공개 오류만 ErrorCode로 만들고, 여러 내부 예외를 하나의 공개 ErrorCode로 합칠 수 있으며, slot 6/10이 안정적으로 지정한 body field만 같은 ErrorCode에서 동일성을 요구한다. 승인된 공개 문자열 field에 `str(exc)`·민감정보를 자동 공개하지 않는다. 배포 ErrorCode 변경은 breaking이고 클라이언트는 같은 계약의 Enum 한 곳에서 소비한다. 실제 클라이언트 수정은 별도 이주 작업이지만 12-slot rollout에는 동시 전환/버전 분리 결정을 남긴다.

### Task B2: implementation-django-ninja — 중앙 handler 레시피를 controller 직접 반환으로 교체

**Files:**

- Modify: `dddjango/skills/implementation-django-ninja/references/final.md`
- Modify: `dddjango/skills/implementation-django-ninja/SKILL.md`
- Modify semantic mirror: `codex-dddjango/skills/implementation-django-ninja/SKILL.md`

- [ ] Step 1: §2.2 operation 규칙을 “입력 Schema 준비 → application 호출 1문장 `try` → 구체 catch → 직접 ErrorOut `Status` → 성공 변환” 순서로 바꾼다.
- [ ] Step 2: §2.3 API 등록 예시를 project `api.py`의 단일 API 인스턴스, BC `register_<bc>_api(api)`, project `urls.py`의 명시 조립으로 바꾼다. 기존 BC `composition_root.py`는 use-case DI 전용이라고 분리 설명한다.
- [ ] Step 3: §6.2를 다음 하위 절로 전면 교체한다.

  - 공통 `ErrorOut` 현재 shape와 사용자 승인 게이트
  - BC `StrEnum`/base/concrete 한 파일 예시
  - no-arg concrete와 발생별 BC base 직접 생성
  - 좁은 sync/async `try`, 구체 catch/tuple, Result/None 직접 반환
  - `Status(<승인된 HTTP status 표현>, error)`와 header 설정
  - error helper/factory/serializer/mapping/handler 금지
  - framework 기본 401/403/404/422/429/HttpError/500
  - 인증 backend는 실패 시 `None` 또는 `AuthenticationError`, 절대 ErrorOut 반환 금지
  - raw infra 기본 500과 공개할 때의 BC 예외 정규화
  - endpoint `response=`/OpenAPI 선언과 수동 후가공 금지
  - 406/415가 별도 승인된 경우에도 `HttpError`의 framework body를 쓰며 problem helper·custom handler를 만들지 않는 경계
  - RFC 9457 brownfield 보존 카브아웃

- [ ] Step 4: `validation_error_out.py`, invalid-params, `problem_response`, `problem`, slug/type URI catalog, custom validation/HttpError/catch-all handler, transient raw DB 전역 recognizer의 생성 레시피를 신규 기본 절에서 제거한다. RFC brownfield는 기존 계약을 관찰·보존하라는 짧은 호환성 절로만 남기고, 새 helper/handler를 만드는 복사 가능한 레시피는 남기지 않는다.
- [ ] Step 5: 문서 다른 절의 중앙 handler/catch-all/Problem helper 교차참조를 새 §6.2 anchor로 전수 교정한다. 깨진 JSON/validation은 framework 기본 body를 exact 계약으로 고정하지 않는다고 쓴다. §6.3의 415 데코레이터는 더 이상 `problem()`을 호출하거나 “helper가 없으면 먼저 만든다”고 하지 않으며, 406/415가 정말 필요한 scope에서만 `HttpError` 기본 흐름을 사용한다. 클래스 controller를 415 때문에 함수형 Router로 자동 격리하지 않는다.
- [ ] Step 6: Claude/Codex 두 `SKILL.md`의 설명·핵심 원칙·라우팅 표를 code 프로필 기준으로 갱신하고, 오류 tuple/수제 Response 금지와 파일·스트리밍·redirect 카브아웃을 같이 남긴다. 플랫폼 형식은 유지하고 의미를 대조한다.

### Task B3: discipline-houserules — 파일 트리와 소유권 고정

**Files:**

- Modify: `dddjango/skills/discipline-houserules/references/final.md`
- Modify: `dddjango/skills/discipline-houserules/SKILL.md`
- Modify semantic mirror: `codex-dddjango/skills/discipline-houserules/SKILL.md`

- [ ] Step 1: 표준 트리의 root `common/ninja/response/`를 빈 `__init__.py` + `error_out.py`로 고정한다. `<problem>_error_out.py`, validation/retryable 파일 예시를 제거한다.
- [ ] Step 2: BC presentation tree에 단일 `schema/error_out.py`를 두고 `<Bc>ErrorCode`, `<Bc>ErrorOut`, concrete ErrorOut을 같은 파일에 둔다. HTTP 오류가 없는 BC에는 미리 만들지 않는다.
- [ ] Step 3: `snake_case` BC 디렉터리→PascalCase 이름 규칙, `StrEnum` 하나, base 하나, concrete 상속/no-arg, 새 field/validator/child model_config와 annotation/Field metadata drift 금지를 적는다.
- [ ] Step 4: error helper/handler는 “공유되면 common 승격” 대상이 아니라 신규 code 프로필에서 금지임을 명시한다. 서로 다른 controller의 짧은 mapping 중복은 허용한다.
- [ ] Step 5: project `api.py`, project `urls.py`, BC registrar, BC DI `composition_root.py`의 네 책임을 한 표에서 구분한다. BC router가 `from <project>.api import api` 후 module import 시 `register_controllers`하는 구 방식을 제거하고, registrar 함수는 side effect 없이 `urls.py`가 명시 호출하게 한다.
- [ ] Step 6: 계층 import 규칙에 domain/application/infra의 Ninja/ErrorOut 금지와 타 BC ErrorCode/ErrorOut 금지를 추가한다. 타 BC 도메인 예외는 기존 규칙대로 ACL 안의 명시적 번역 import만 허용하고 presentation/application 직접 catch는 금지한다.
- [ ] Step 7: brownfield 기존 API error contract를 자동 이주하지 않는 이주 조문을 넣고, Claude/Codex 두 `SKILL.md`도 같은 의미로 갱신한다.
- [ ] Step 8: ACL 절의 transient 설명에서 “raw `OperationalError`를 presentation 전역 recognizer가 problem으로 변환”하는 신규 기본 경로를 제거한다. raw infra 오류는 기본 500으로 두고, 공개할 안정적 의미가 승인된 경우에만 infra가 자기 BC의 구체 예외로 정규화해 controller가 처리한다. 기존 RFC brownfield의 cause 보존 규칙과 합성 인프라 예외 금지는 별도 호환 문맥으로 유지한다.

### Task B4: implementation-test — 외부 계약 중심 테스트로 교체

**Files:**

- Modify: `dddjango/skills/implementation-test/references/final.md`
- Modify: `dddjango/skills/implementation-test/SKILL.md`
- Modify semantic mirror: `codex-dddjango/skills/implementation-test/SKILL.md`

- [ ] Step 1: 기존 11-slot을 12-slot으로 바꾸고 신규 기본 기대값을 code 프로필로 전환한다. `preserve-established` scope의 테스트는 승인된 기존 RFC/wire 계약을 그대로 검증하게 남기되, `type`/`instance`/problem+json을 모든 신규 scope에 강제하는 문구는 제거한다.
- [ ] Step 2: Schema 단위 테스트에 common `ErrorOut`의 승인된 exact field set·타입·required/default/nullable·alias/config, slot 6 식별자 field의 BC Enum 허용/미정의 문자열 거부, 모든 concrete subclass 동적 발견+무인자 생성, 승인된 base 밖 필수 field 부재, 프로젝트 전역 ErrorCode 중복 부재와 slot 6/10이 안정적으로 지정한 field를 넣는다. 어느 property 이름도 플러그인 기본값으로 두지 않으며 common shape가 승인 변경되면 G1의 테스트 계약 변화와 함께 literal oracle을 갱신한다.
- [ ] Step 3: HTTP 통합 테스트는 application 협력자를 구체 예외로 실패시켜 slot-6 exact body, mapping별 HTTP status, 필요한 header, 미식별 예외의 framework 기본 500 경로를 검증한다. body에 status property가 승인된 scope만 HTTP/body status 일치를 검사한다. 여러 구체 예외 tuple이 하나의 공개 식별자/concrete로 수렴하는 정상 사례와 공개 문자열에 내부 예외 문자열이 자동 노출되지 않는 사례도 둔다.
- [ ] Step 4: framework smoke는 인증 backend 실패가 `ErrorOut`을 반환하지 않는지와 401/403/route 404/422/429가 BC ErrorOut/code로 변환되지 않는지를 확인한다. framework body 전체 snapshot은 만들지 않고, header는 §1.1 compatibility 결정상 요구되는 것만 단언한다.
- [ ] Step 5: OpenAPI는 관리 대상 BC status→`<Bc>ErrorOut`, framework ErrorOut 광고 부재, `application/json`, 수동 augmentation 부재를 확인한다.
- [ ] Step 6: 내부 helper/factory/handler 단위 테스트를 만들지 않는다. 존재 금지는 checker/reviewer, 외부 동작은 HTTP 계약 테스트가 담당한다고 경계를 명시한다. 406/415를 별도 계약한 경우도 framework body exact snapshot이나 문제 helper 테스트를 만들지 않는다. Claude/Codex 두 `SKILL.md`는 플랫폼 형식을 유지한 채 같은 테스트 경계를 말하게 한다.

### Task B5: implementation-django-web — 삭제되는 Ninja helper 의존만 분리

**Files:**

- Modify: `dddjango/skills/implementation-django-web/references/final.md`

- [ ] Step 1: 서버렌더 §11의 HTML 책임(도메인 오류 view-local, 시스템 오류 `handler500`, transient HTML 503+`Retry-After`, HTMX fragment)은 그대로 보존한다.
- [ ] Step 2: 삭제될 `common.ninja.errors._is_retryable_db_error` import와 JSON problem helper 교차참조를 제거한다. 현재 유일한 consumer인 서버렌더 middleware-local 판별 함수로 두고, 실제 Django 경계 두 곳 이상이 공유할 때만 `common/django/` 승격을 검토한다.
- [ ] Step 3: 서버렌더 규칙을 code JSON/`Status`로 이주하거나 Ninja `common/ninja/response/`에 새 파일을 추가하지 않는다. `implementation-django-web/SKILL.md`에는 삭제 심볼이 없으므로 의미 변경이 생기지 않는 한 수정하지 않는다.

### Task B6: discipline-cleancode — try/catch 분리 원칙의 adapter 카브아웃

**Files:**

- Modify: `dddjango/skills/discipline-cleancode/references/final.md`

- [ ] Step 1: §12.3의 “Try/Catch 분리”가 인지 경계를 좁히라는 원칙이지 모든 catch를 별도 함수로 추출하라는 절대 규칙은 아니라고 한정한다.
- [ ] Step 2: 선택된 framework profile이 adapter entrypoint를 예외→HTTP mapping owner로 승인한 경우에는 작은 구체 catch와 직접 반환을 그 entrypoint에 두며, mapping helper 추출로 소유권을 흩뜨리지 않는다고 적는다. 일반 broad catch 금지와 정상/오류 흐름 명료성은 유지한다.
- [ ] Step 3: 범용 Clean Code 전체를 Ninja 규칙으로 바꾸지 않고 이 충돌 문장만 최소 수정한다. `discipline-cleancode/SKILL.md`는 이미 구현 상세를 reference에 위임하므로 수정하지 않는다.

### Task B7: canonical reference 미러 동기

- [ ] Step 0: 어떤 reference도 편집하기 전에 `python3 workspace/tools/corpus_mirror_sync.py --check --format json`이 11종 drift 0인지 확인한다. 하나라도 이미 drift면 사용자 변경일 수 있으므로 `--write`로 자동 수리하지 않고 작업을 중단한다.
- [ ] Step 1: Claude 정본 여섯 reference를 모두 수정한 뒤 다시 JSON check한다. drift skill 집합이 정확히 `{architecture-api, implementation-django-ninja, discipline-houserules, implementation-test, implementation-django-web, discipline-cleancode}`인지 확인한 뒤 한 번만 write한다. 다른 skill이 섞이면 중단한다.

```bash
python3 workspace/tools/corpus_mirror_sync.py --write
python3 workspace/tools/corpus_mirror_sync.py --check
```

Expected: 11/11 source-body↔Claude, Claude↔Codex reference in sync.

- [ ] Step 2: 자동 갱신된 다음 12개 파일을 diff에서 확인한다.

  - `workspace/reference/{architecture-api,implementation-django-ninja,discipline-houserules,implementation-test,implementation-django-web,discipline-cleancode}/reference/final.md`
  - `codex-dddjango/skills/{architecture-api,implementation-django-ninja,discipline-houserules,implementation-test,implementation-django-web,discipline-cleancode}/references/final.md`

---

## Part C — Coordinator와 역할 프롬프트

### Task C1: design-architect와 API reviewer의 12-slot 생산·검토

**Files:**

- Modify: `dddjango/agents/design-architect.md`
- Modify: `dddjango/agents/design-review-api.md`
- Modify: `codex-dddjango/skills/dddjango-design-architect/SKILL.md`
- Modify: `codex-dddjango/skills/dddjango-design-review-api/SKILL.md`

- [ ] Step 1: architect의 기존 Error response 11-slot과 “중앙 변환점” 문단을 §1.1의 12-slot으로 교체한다.
- [ ] Step 2: 신규 API의 default는 `dddjango-code-json`, 기존 외부 계약 증거가 있으면 `preserve-established`임을 명시한다. dependency 미설치만으로 plain Django나 old profile로 내리지 않는다.
- [ ] Step 3: common `ErrorOut`의 `reuse`는 관찰된 exact baseline을 요구한다. `create`와 `approved-change`는 field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 직렬화/field 의미 전체에 대해 일반 G1과 분리된 명시적 사용자 승인 증거가 없으면 `STOP_FOR_USER_APPROVAL` handoff를 만들고 G1을 완료하지 않는다.
- [ ] Step 4: API reviewer는 wire 의미(ErrorCode와 승인 body field의 안정성, HTTP status, 공개 문자열 안전성), framework 기본 제외, response/OpenAPI, compatibility를 검토한다. 파일 배치·helper 의미 우회는 discipline reviewer와 중복 판정하지 않는다.
- [ ] Step 5: API reviewer가 RFC 자체를 위반으로 보지 않고, 선택된 profile과 구현이 불일치할 때만 blocker로 올리게 한다.
- [ ] Step 6: Claude/Codex 두 역할에서 12개 slot 이름과 profile 값이 문자 단위로 검색 가능하도록 동일 anchor를 둔다.
- [ ] Step 7: `response/OpenAPI/tests` slot에는 인증 backend의 `None|AuthenticationError` 규칙, framework header의 established dependency, common exact shape oracle, status→BC base까지만 정확하고 status별 식별자 subset은 과대 허용되는 OpenAPI 한계를 적는다. 기존 RFC 기대의 종료/변경은 canonical product spec의 “현재 승인 계약” 근거로 테스트 계약 변화에 명시한다.
- [ ] Step 8: API reviewer 체크리스트에 공개 ErrorCode 최소화, 여러 내부 예외→한 ErrorCode 허용, slot 6/10이 지정한 안정 body field, 승인 문자열 field의 `str(exc)`·민감정보 금지, ErrorCode breaking/클라이언트 Enum rollout을 명시한다. 이는 의미 판단이라 새 checker 조건으로 승격하지 않는다.

### Task C2: acceptance tester와 coder의 실행 규칙 교체

**Files:**

- Modify: `dddjango/agents/acceptance-tester.md`
- Modify: `dddjango/agents/coder.md`
- Modify: `codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md`
- Modify: `codex-dddjango/skills/dddjango-coder/SKILL.md`

- [ ] Step 1: acceptance tester는 Part B4의 Schema/HTTP/framework/OpenAPI 계약을 outside-in Red로 만든다. 인증 실패와 common exact shape도 포함하고, 새 framework status를 발명하거나 framework body exact snapshot을 만들지 않는다.
- [ ] Step 2: coder preflight 검색 목록을 common response 디렉터리, 모든 BC error module, ErrorCode 값, concrete 생성, controller try/catch/Status, handler/helper, root api import, response/OpenAPI로 교체한다.
- [ ] Step 3: coder는 정본 tree와 12-slot이 다르면 임의로 맞추지 않고 `TREE_CONTRACT_MISMATCH`를 반환한다. common `ErrorOut`의 `reuse`는 관찰 exact baseline을 요구하고, `create`·`approved-change`의 별도 명시적 사용자 승인 부재면 `STOP_FOR_USER_APPROVAL`을 반환한다.
- [ ] Step 4: 구현 순서를 common reuse/create → BC error module → failing contract tests → controller direct mapping → registrar/root composition → OpenAPI green으로 고정한다.
- [ ] Step 5: generic helper로 DRY하려는 리팩터링을 금지하고, 명시적인 controller mapping 몇 줄의 반복을 허용한다고 명시한다.
- [ ] Step 6: coder는 target의 실제 dependency pin에서 two-argument `Status`/다중 response와 slot 6이 실제 승인한 status 표현을 계약 테스트로 실행한다. body status field가 승인된 scope에서만 Part A2의 같은 이름 충돌 회귀도 실행한다. 실패하면 tuple이나 field rename으로 독단 우회하지 않고 `RUNTIME_CONTRACT_MISMATCH`로 설계에 반송한다.
- [ ] Step 7: coder는 controller에 주입된 Django `HttpResponse`에 설정한 승인 header가 mounted client 최종 응답까지 전달되는지, skip/xfail 없이 예정 테스트가 전부 실행되는지 확인한다. plugin fixture green은 target pin 증거를 대신하지 않는다.

### Task C3: discipline reviewer의 의미 레인 재작성

**Files:**

- Modify: `dddjango/agents/discipline-reviewer.md`
- Modify: `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`

- [ ] Step 1: 기존 “operation은 예외를 raise하고 중앙 handler가 전수 변환” 불릿을 제거한다.
- [ ] Step 2: 새 blocker 불릿을 다섯 축으로 나눈다.

  1. common/BC 파일 소유권과 승인 shape
  2. helper/handler 의미 우회와 다른 이름의 factory/serializer/mapping
  3. controller 좁은 try·구체 catch·즉시 raise/catch 금지
  4. prepared concrete no-arg/직접 Status와 사건별 승인값의 BC base 직접 생성
  5. 실제 반환 status↔OpenAPI와 framework 기본 오류 비광고

- [ ] Step 3: checker exit 0이 보증하지 않는 간접 helper, 동적 import, exception base가 사실상 broad한 변종, 여러 API scope compatibility를 reviewer 사각 목록으로 명시한다.
- [ ] Step 4: 타 BC 예외 규칙은 ACL의 업스트림 번역 허용과 controller의 cross-BC catch 금지를 구분한다.
- [ ] Step 5: transient 규칙을 “raw infra 전역 handler 필수”에서 “raw는 기본 500; 공개할 의미가 있으면 infra가 자기 BC 예외로 정규화하고 controller가 매핑”으로 바꾼다. 영구장애를 retryable로 오분류하지 않는 기존 의미는 유지한다.
- [ ] Step 6: catch-all 안전망/NJ-7 불릿을 제거하고 운영 `DEBUG=False` 전제를 보안 체크로 남긴다.
- [ ] Step 7: import가 없어도 HTTP 의미의 `status`/`code` DTO·분기·값 객체가 domain/application을 흐르는 기존 Goodhart 변종을 의미 blocker로 유지한다. 주문 상태 같은 도메인 `status`와 이름만으로 혼동하지 않고 실제 HTTP 의미와 소비 경로를 본다.
- [ ] Step 8: 인증 backend가 ErrorOut/Schema를 truthy 반환해 `request.auth`를 오염시키는 경우와 framework header 의존을 숨긴 경우를 reviewer 사각 목록에 넣는다.
- [ ] Step 9: G1의 project-wide surface inventory와 현재 API/controller/URLconf/registrar module, scope BC/error BC의 의미상 완전성, shared-module mixed profile, API instance 복수를 검토한다. 직접 import한 1-hop class method·2-hop·선택 밖 helper, 필수 심볼 re-export, 동적 registrar, root-local catalog/mapping의 동형처럼 checker 증명 문법 밖인 우회도 의미 blocker로 본다.

### Task C4: Coordinator gate와 Codex orchestrator 동기

**Files:**

- Modify: `dddjango/commands/dddjango.md`
- Modify: `codex-dddjango/skills/dddjango/SKILL.md`

- [ ] Step 1: G1 전/승인 후 재검사에서 11-slot을 12-slot으로 바꾸고 common shape 변경 승인 증거를 별도 차단 조건으로 둔다.
- [ ] Step 2: Error response scope의 Phase 1 discipline review 필수 호출은 유지하되, central handler 존재가 아니라 새 구조·직접 mapping을 검토하게 한다.
- [ ] Step 3: Phase 2 역할 전달 문구와 G2 배너를 canonical common shape, BC enum/base/concrete, no-arg 실행, controller mapping, framework-default smoke, OpenAPI 결과로 바꾼다.
- [ ] Step 4: 19개 checker 목록에서 `check-catch-all-handler.py`를 같은 순번의 `check-api-error-controller-contract.py`로 교체하고, `check-error-centralization`, `check-context-isolation`, `check-openapi-error-declaration`, `check-response-schema-bypass`, 기존 `check-composition-root`의 설명을 새 책임으로 갱신한다. composition checker에는 기존 DI slice와 별개인 registrar 조립 slice가 추가된다고 구분한다.
- [ ] Step 5: 유지 checker 설명도 함께 정합화한다. `check-common-container.py`의 problem helper 예시는 일반 횡단 utility로, `check-transient-overmapping.py`는 `preserve-established` brownfield handler의 과잉매핑 방어로, `check-synthetic-infra-exc.py`는 신규 프로필의 자기 BC 예외 정규화와 brownfield cause 보존으로 설명한다. 어느 것도 신규 code 프로필의 handler/recognizer 정당화 근거로 쓰지 않는다.
- [ ] Step 6: Error response scope에서는 승인된 12-slot을 읽고 먼저 project-wide surface inventory의 모든 module set을 비교한다. 같은 profile의 승인된 common/error module 재사용은 한 경로로 dedupe한다. 누락, 역할·계약이 충돌하는 같은-profile 중복, code/preserve 공유가 있으면 checker가 타 scope를 추론하게 두지 않고 `STOP_FOR_USER_APPROVAL`로 G1에 반송한다. 통과하면 네 API-error contract checker에는 `--error-profile`, `--scope`, `--api-module`, 반복 `--controller-module`, `--scope-bc`, `--error-bc`를 전달하고, schema checker에는 반복 `--project-code-error-module`/`--project-preserve-error-module`, composition checker에는 정확한 `--urlconf-module`/반복 `--registrar-module`을 더한다. Error response가 아닌 G2도 `--error-profile auto`를 명시해 기존 positional checker 동작을 유지한다.
- [ ] Step 7: 19개 중 하나가 exit 1(분석 불능) 또는 exit 2(blocker)이면 G2를 열지 않는다고 명시한다.
- [ ] Step 8: Claude/Codex의 게이트 순서, checker 이름 19개, 명시 인자, 12-slot anchor를 기계 대조한다. 플랫폼 전용 frontmatter/호출 구문 차이는 유지한다.
- [ ] Step 9: Coordinator의 “19개 모두 touched 공집합이면 비어 돈다”는 일괄 설명을 고친다. 기존 checker, preserve legacy slice, context S1~S3, 성공 우회는 touched 기반이지만 code-profile schema/controller/context 신규 slice/OpenAPI 구조 불변식은 명시 선택 전체 트리를 본다고 checker별로 구분한다.

---

## Part D — 결정적 백스탑 구현

### Task D1: `check-error-centralization.py`를 ErrorOut schema contract checker로 교체

**Files:**

- Modify: `dddjango/scripts/check-error-centralization.py`
- Mirror: `codex-dddjango/skills/dddjango/scripts/check-error-centralization.py`

- [ ] Step 1: 기존 application HTTP 신호의 합성 회귀를 먼저 고정한 뒤 그 로직을 Task D3의 legacy layer-purity slice로 옮긴다. D3 matrix가 GREEN이 되기 전에는 여기서 삭제하지 않아 preserve/auto 검출력이 사라지는 중간 상태를 만들지 않는다.
- [ ] Step 2: §1.2의 CLI/exit grammar를 구현한다. code profile에서는 common 규칙을 항상 적용하고 BC-specific 규칙만 `error-bc`에 적용하며 preserve에서는 둘 다 N/A다. `scope-bc`/`error-bc` 관계, 반복 `project-code-error-module`/`project-preserve-error-module`, selected source의 tracked+untracked non-ignored 수집을 검증한다.
- [ ] Step 3: `error-bc` 이름(`snake_case`→PascalCase)을 수집하고 common `ErrorOut`의 전체 field와 그중 required field를 AST에서 동적으로 도출한다. default/nullable/모든 Field metadata/model config·legacy Config/decorator는 승인 shape의 일부로 common에 허용하되 BC/concrete의 drift를 막는다. `code/title/status/detail`, `error_type/msg/is_show` 등 어느 property set도 checker 상수로 하드코딩하지 않는다.
- [ ] Step 4: `dddjango-code-json`이면 `error-bc` 수와 무관하게 common response 디렉터리의 허용 파일, 빈 `__init__.py`, 단일 `ErrorOut`, common 안의 Enum/concrete/helper 부재를 검사한다. 오류 없는 BC에는 BC `error_out.py`를 강요하지 않지만 이 profile의 공통 wire contract는 생략할 수 없다.
- [ ] Step 5: 각 `error-bc`에 정확한 `<Bc>ErrorCode(StrEnum)` 하나와 `<Bc>ErrorOut(CommonErrorOut)` 하나, 나머지 concrete의 base 상속을 검사한다. BC base는 common 필드 중 정확히 하나의 `str` 자리를 자기 Enum으로 좁히되 annotation wrapper/nullability·required/default·Field metadata를 보존하고, 추가 field·validator·child model_config를 두지 않으며 그 필드명은 고정하지 않는다.
- [ ] Step 6: concrete는 common required field 각각에 class default가 있고, 승인되지 않은 새 field/validator/child model_config나 annotation/Field metadata drift가 없으며, 동적으로 발견한 식별자 field default가 자기 Enum member인지 검사한다. 실제 `ConcreteErrorOut()` 실행 가능성은 대상 프로젝트 계약 테스트가 최종 보증한다.
- [ ] Step 7: 이 project inventory/유일성 slice는 `dddjango-code-json`에서만 실행하고 preserve/auto에서는 N/A다. checker가 발견한 canonical error module 후보와 두 project inventory를 정확히 대조한다. 후보가 어느 inventory에도 없거나 양쪽에 있거나 root 밖/반복 인자 중복 경로이면 exit 1이다. Coordinator가 같은-profile 재사용 경로를 먼저 dedupe한 `project-code-error-module` 전체의 `<Bc>ErrorCode` value에서 snake_case와 프로젝트 전역 중복을 검사하고 controller/schema에서 동적으로 발견한 식별자 필드에 원시 문자열을 직접 대입하는 것을 차단한다. 독립 version도 중복 정의가 아니라 동일 BC Enum을 재사용한다. canonical 모양이 같은 `project-preserve-error-module`의 RFC/code 문자열은 제외하고 BC prefix는 권장일 뿐 조건으로 만들지 않는다.
- [ ] Step 8: 각 `error-bc` 안의 별도 `<problem>_error_out.py`, common concrete, canonical module 밖 ErrorOut 정의를 보고한다. 다른 `scope-bc` 중 오류 없는 BC의 module 부재는 정상이다.
- [ ] Step 9: Task A1 schema case를 RED→GREEN으로 만든 뒤 Codex 파일을 byte-exact 복사한다.

### Task D2: catch-all checker를 controller contract checker로 교체

**Files:**

- Delete: `dddjango/scripts/check-catch-all-handler.py`
- Delete: `codex-dddjango/skills/dddjango/scripts/check-catch-all-handler.py`
- Create: `dddjango/scripts/check-api-error-controller-contract.py`
- Mirror: `codex-dddjango/skills/dddjango/scripts/check-api-error-controller-contract.py`

- [ ] Step 1: §1.2 CLI로 열거된 정확한 controller module을 검증하되, code profile에서 controller 동작 계약을 활성화하는 대상은 owner가 `error-bc`인 controller로 한정한다. `scope-bc`이지만 `error-bc`가 아닌 owner는 source/owner만 검증하고 ErrorOut·try/Result·helper/handler·1-hop 의미 규칙을 적용하지 않는다. helper/handler 직접형의 managed set은 활성 controller들, 각 `error-bc`의 canonical error module, 활성 controller가 직접 import하는 같은 BC `presentation_layer` production module의 1-hop closure, 그리고 정확히 선택된 API module이 직접 import하는 자기 API package의 production 1-hop module로 제한한다. API package 1-hop은 root `api.py` purity를 helper로 우회하지 못하게 하는 범위이며, 같은 BC/API package 전체를 재귀 scan하지 않는다. managed helper의 금지된 factory/serializer/mapping/handler 정의는 실제 호출 여부와 무관하게 차단하고, model config mutation helper body는 선택된 controller/API가 직접 import한 module-level function/lambda의 실제 직접 호출 경로에서만 연결한다. 활성 code profile의 이 managed set에서 `@*.exception_handler`, `.add_exception_handler`, ErrorOut→raw HTTP 직렬화, concrete 고정값 factory, exception→ErrorOut mapping helper를 차단하고 preserve에서는 owner/동작 신규 규칙을 N/A로 둔다. 직접 import한 1-hop class method·2-hop·선택 밖 helper는 discipline reviewer가 맡는다.
- [ ] Step 2: managed `try`의 body는 Assign/AnnAssign/Expr-Await 계열 top-level statement 정확히 하나, outer call 하나만 허용한다. 입력 준비·return·성공 변환·분기·복수 outer call은 차단하고 호출 인자의 값 객체 생성은 허용한다. 그 outer call이 의미상 주 application use case인지는 정적으로 추측하지 않고 discipline reviewer가 판정한다.
- [ ] Step 3: bare/`Exception`/`BaseException` catch를 차단하고 tuple의 모든 원소가 직접 import된 구체 이름인지 확인한다. import provenance가 보이는 Ninja/Django framework 예외와 DB/SDK raw infra 예외 catch도 차단한다. 예외 re-export의 broad 의미는 reviewer에게 남긴다.
- [ ] Step 4: 같은 `try`에서 직접 만든 예외를 즉시 catch하는 `raise`, managed catch의 `raise HttpError`, bare/명시 re-raise, handler forwarding을 차단한다. 각 managed catch는 prepared concrete 또는 발생별 BC base를 직접 만든 뒤 `Status(<literal/status constant 또는 error의 승인 field>, error)`로 끝나야 한다. 실패 Result/None 호출은 모든 `try` 밖의 대입문이어야 하며 바로 다음 실행 문장의 분기에서 같은 직접 반환 문법을 쓴다. 같은 호출을 exception path와 Result path로 이중 처리하지 않되, 서로 다른 호출은 각자 승인된 경로를 사용할 수 있다.
- [ ] Step 5: prepared concrete constructor의 인자/키워드를 차단한다. BC base direct constructor는 사건별 승인값을 위해 허용하되 승인된 common field만 받고 direct Status로 반환되어야 한다.
- [ ] Step 6: 오류 `(status, body)` tuple, `Response`/`JsonResponse`/`HttpResponse`, dict 반환을 차단한다. 비오류 성공 arm의 성공 응답과 FileResponse/Streaming/redirect만 이 checker에서 제외하며, managed catch/Result 오류 arm의 non-`Status` terminal은 같은 타입이어도 차단한다.
- [ ] Step 7: 증명 문법은 direct/`as` import, 단순 상대 import, canonical 상속, 로컬 1단계 assignment와 direct 반환까지만 지원한다. 필수 ErrorOut/Status를 해석하지 못하면 활성 code scope에서 exit 1이다. 직접 import한 class method·2-hop helper 등 callable의 계층 의미, exception re-export 의미는 false positive를 내지 않고 reviewer 사각으로 남긴다.
- [ ] Step 8: Task A1 controller case를 RED→GREEN으로 만든 뒤 checker count가 19인지 확인한다.

### Task D3: `check-context-isolation.py`에 에러 경계 슬라이스 추가

**Files:**

- Modify: `dddjango/scripts/check-context-isolation.py`
- Mirror: `codex-dddjango/skills/dddjango/scripts/check-context-isolation.py`

- [ ] Step 1: positional `TARGET_DIR` 단독·`auto`·`preserve-established` legacy lane은 기존 전역 S1~S3 의미 predicate와 ACL 카브아웃을 그대로 쓰고, 기존처럼 touched file에만 적용해 untouched를 grandfather한다. 파일 read 실패와 S1~S3 syntax failure는 skip한다. Git touched 판정 실패는 fail-open이라고 부르지 않고, 기존대로 후보를 touched로 보수 판정해 나머지 직접 신호가 있으면 차단한다.
- [ ] Step 2: 구 `check-error-centralization.py`의 application HTTP raw regex·진단 label·전역 collector·touched/untracked 판정을 byte-level 동작 회귀로 옮긴다. positional/auto/preserve에서는 정확한 legacy collector를 사용하고 syntax parse 없이 raw text를 검사한다. 이 slice는 구 checker처럼 표준 `application/` 컨테이너 밖 `application_layer/`도 찾아야 하므로 기존 no-`application/` 조기 반환보다 먼저 실행한다.
- [ ] Step 3: §1.2 CLI를 구현한다. `dddjango-code-json`은 selector와 `scope-bc`로 한 번 만든 TARGET_DIR 기준 상대 production inventory(Git tracked+untracked non-ignored, test/migration/cache/venv/generated 제외)를 공유한다. 변경하지 않은 S1~S3 의미 predicate는 이 filtered production 전체에 적용해 touched 상태로 구조 위반을 숨기지 않고, legacy HTTP raw signal predicate는 같은 inventory의 touched `application_layer` 부분집합에만 적용한다. root/layer/error-language 신규 slice도 같은 filtered full tree를 쓰며, touched Ninja import가 legacy와 layer slice 양쪽에 걸려도 한 번만 진단한다.
- [ ] Step 4: root API slice — 전달된 정확한 `api-module`에 API instance가 하나인지 확인하고 BC import, root-local GlobalErrorCode/ErrorOut/catalog/exception mapping/path별 error branch, custom handler를 차단한다. registrar 위치·호출은 중복 검사하지 않고 Task D3b의 기존 composition-root checker가 소유한다. 동적 root mapping 동형은 reviewer 몫이다.
- [ ] Step 5: layer purity slice — code-profile `scope-bc`의 domain/application/infra production source가 Ninja/Ninja Extra, Django HTTP response/status, common/BC ErrorOut/ErrorCode를 import하면 차단한다.
- [ ] Step 6: BC error language slice — 다른 BC ErrorCode/ErrorOut import는 code-profile 계층에서 차단한다. 다른 BC domain exception은 기존 S1처럼 `infra_layer/acl/`의 명시 번역만 허용한다.
- [ ] Step 7: code-profile inventory의 root/resolve·symlink 탈출·selected membership·read·strict UTF-8·syntax 분석 실패는 exit 1로 fail-closed하고, blocker가 함께 있어도 분석 오류 exit 1을 우선한다. docstring과 출력은 positional/auto/preserve의 exact legacy touched lane, code의 filtered touched raw-signal lane, code filtered full-tree 구조 lane을 구분한다.
- [ ] Step 8: Task A1의 root/local catalog/legacy purity 사례와 기존 S1~S3 회귀를 모두 GREEN으로 만든 뒤 미러한다.

### Task D3b: 기존 `check-composition-root.py`에 API registrar 조립 slice 추가

**Files:**

- Modify: `dddjango/scripts/check-composition-root.py`
- Mirror: `codex-dddjango/skills/dddjango/scripts/check-composition-root.py`

- [ ] Step 1: 기존 positional `TARGET_DIR` 실행, touched BC 선택, DI V1(off-tree `composition/`)·V2(오배치)·V3(부재) 판정과 종료코드를 회귀 fixture로 먼저 고정하고 그대로 보존한다. API registrar는 같은 “조립 위치” 책임의 독립 slice로 추가하며 DI composition root와 project URL composition root를 하나의 파일로 합치라는 규칙으로 오해하지 않게 진단을 분리한다.
- [ ] Step 2: 선택적 `--error-profile`, `--scope`, `--api-module`, 정확히 하나의 `--urlconf-module`, 반복 가능한 `--registrar-module`을 받는다. `auto`/`preserve-established`에서는 새 registrar slice를 N/A로 두되 기존 DI 검사는 항상 실행한다. `dddjango-code-json`에서 selector 누락·중복·역할 overlap·root/symlink 탈출·read/syntax 실패는 exit 1이다.
- [ ] Step 3: 정확히 선택된 registrar module에서 project API module import와 module-top-level `register_controllers` 호출을 차단한다. side-effect 없는 `register_<bc>_api(api)` 함수가 registration을 소유하고, 정확히 선택된 URLconf가 각 registrar를 명시적으로 한 번 호출하는 직접형을 검사한다. URLconf 밖이나 임의 helper가 대신 조립하는 직접형은 exit 2다.
- [ ] Step 4: 같은 BC/프로젝트 안의 선택 밖 preserve registrar·URLconf는 읽지 않는다. direct/`as` import와 1단계 명시 호출까지만 결정적으로 증명하고 re-export·동적 호출·registrar 내부 controller 집합의 의미는 discipline reviewer와 mounted route 계약 테스트가 맡는다.
- [ ] Step 5: Task A1의 기존 DI V1~V3 회귀, 정상 code registrar, project API import/module-top-level side effect, registrar 누락·중복 호출, 분리된 preserve URLconf, selector 분석 불능 사례를 RED→GREEN으로 만든 뒤 미러한다.

### Task D4: `check-openapi-error-declaration.py`를 실제 반환↔선언 대조로 확장

**Files:**

- Modify: `dddjango/scripts/check-openapi-error-declaration.py`
- Mirror: `codex-dddjango/skills/dddjango/scripts/check-openapi-error-declaration.py`

- [ ] Step 1: 기존 touched-file `openapi_extra` 오류 status와 `response=` 누락 검출을 먼저 회귀 fixture로 고정한다. preserve/auto branch에서 finding 의미와 touched/grandfather 동작을 유지한 뒤 code-profile 기능을 추가한다. 단, production component filter는 TARGET-relative 경로에 적용해 ancestor `test`/`venv`가 전체 프로젝트를 숨기던 결함을 고치고, 복수 finding은 filesystem 순서 대신 TARGET-relative lexical 순서로 결정화한다.
- [ ] Step 2: §1.2 CLI와 정확한 controller module selector를 구현한다. code branch는 operation이 직접 반환하는 `Status`의 첫 인자를 모아 관리 대상 오류 status를 구한다. literal과 `status.HTTP_404_NOT_FOUND`/`HTTPStatus.NOT_FOUND` 같은 결정적 표준 상수, 또는 같은 반환 error의 slot-6 승인 body field를 지원하되 `status`라는 property를 요구하지 않는다.
- [ ] Step 3: decorator `response={...}`의 status key와 Schema symbol을 파싱하고 실제 반환하는 각 오류 status가 같은 BC `<Bc>ErrorOut`으로 선언됐는지 대조한다. 보증은 status→BC base class까지이며 status별 식별자 Enum subset의 과대 노출은 승인된 한계라고 진단한다.
- [ ] Step 4: `response=`에 ErrorOut을 선언했지만 해당 operation에 직접 BC ErrorOut 반환이 없는 framework 401/403/route 404/422/429/500 광고를 차단한다. 404/422 숫자 자체가 아니라 직접 BC 반환 존재 여부로 판별한다.
- [ ] Step 5: code profile에서 framework error response용 `openapi_extra`와 모든 `get_openapi_schema` override/monkeypatch/별도 postprocessor 직접형을 차단한다. decorator의 servers/security/examples 등 non-response metadata는 보존하되 생성 schema 사후수정과 혼동하지 않는다.
- [ ] Step 6: preserve/auto에서는 기존 touched `openapi_extra`-only 오류 선언 검사를 유지하고 신규 BC base/direct-Status 정합은 N/A로 둔다. 승인된 production filter·root-relative filter·deterministic ordering 교정 외 finding set/content와 exit는 legacy differential로 보존한다.
- [ ] Step 7: 필수 error status/Schema mapping을 해석하지 못하면 code mode에서 exit 1이다. 동적 성공 response처럼 오류 계약 증명과 무관한 표현이나 분리된 brownfield controller는 건드리지 않는다.
- [ ] Step 8: Task A1 OpenAPI/legacy case를 RED→GREEN으로 만든 뒤 미러한다.

### Task D5: 성공 schema checker의 책임 문구와 카브아웃 회귀

**Files:**

- Modify: `dddjango/scripts/check-response-schema-bypass.py`
- Mirror: `codex-dddjango/skills/dddjango/scripts/check-response-schema-bypass.py`

- [ ] Step 1: 중앙 problem helper/handler를 정상 예외로 설명한 docstring과 진단 문구를 제거한다.
- [ ] Step 2: 일반 JSON 성공 200~203 raw 응답 우회만 소유하고 error helper는 Task D2, 파일/스트리밍/redirect/204는 제외라는 현재 경계를 명확히 한다.
- [ ] Step 3: 검사 로직을 불필요하게 넓히지 않고 Task A1 회귀 case를 통과시킨다.
- [ ] Step 4: `--controller-module`은 성공 checker의 optional analysis selector로 유지한다. Coordinator는 이 checker를 positional `TARGET_DIR`로 실행하며, selector는 수동·집중 분석 호출에서만 사용한다.

### Task D6: 유지되는 legacy checker의 설명만 새 프로필과 정합화

**Files:**

- Modify wording only: `dddjango/scripts/check-common-container.py`
- Modify wording only: `dddjango/scripts/check-transient-overmapping.py`
- Modify wording only: `dddjango/scripts/check-synthetic-infra-exc.py`
- Modify wording only: `dddjango/scripts/check-idempotency-scope-creep.py`
- Mirror same four files under `codex-dddjango/skills/dddjango/scripts/`

- [ ] Step 1: `check-common-container`의 “problem helper를 공유되면 승격” 예시를 오류와 무관한 일반 횡단 utility 예시로 바꾸고 canonical ErrorOut birth-common만 남긴다.
- [ ] Step 2: `check-transient-overmapping`은 로직을 유지하되 established brownfield handler에만 의미가 있고 신규 code 프로필에서는 custom handler 자체가 먼저 위반임을 docstring/진단에 명시한다.
- [ ] Step 3: `check-synthetic-infra-exc`의 “presentation recognizer 사각” 단일 해법을 새 프로필의 자기 BC 예외 정규화+controller mapping과 brownfield cause 보존 두 경우로 고친다. 탐지 로직은 바꾸지 않는다.
- [ ] Step 4: `check-idempotency-scope-creep`의 원인 설명에서 “중앙 예외핸들러 사망”을 제거하고 승인 범위 밖 멱등성 산출물이라는 checker 본래 책임만 남긴다.
- [ ] Step 5: 네 파일의 logic diff가 주석/문자열 외 0인지 확인한다.

### Task D7: checker 미러와 전체 matrix

- [ ] Step 1: Claude 정본 19개와 Codex 배포 19개의 파일명 집합·byte 내용을 대조한다.

```bash
find dddjango/scripts -maxdepth 1 -name 'check-*.py' | wc -l
find codex-dddjango/skills/dddjango/scripts -maxdepth 1 -name 'check-*.py' | wc -l
python3 -c 'from pathlib import Path; a=Path("dddjango/scripts"); b=Path("codex-dddjango/skills/dddjango/scripts"); ax={p.name:p.read_bytes() for p in a.glob("check-*.py")}; bx={p.name:p.read_bytes() for p in b.glob("check-*.py")}; assert ax.keys()==bx.keys() and ax==bx, (sorted(ax.keys()-bx.keys()), sorted(bx.keys()-ax.keys()), sorted(k for k in ax.keys() & bx.keys() if ax[k] != bx[k]))'
```

Expected: `19`, `19`, Python assertion 통과. 무시된 `__pycache__` 같은 비정본 파일은 비교하지 않는다.

- [ ] Step 2: 전체 발화 matrix를 실행한다.

```bash
python3 workspace/tools/api_error_backstop_matrix.py
```

Expected: 모든 case PASS. 각 위반 case는 정확히 exit 2, 분석 불능 case는 exit 1, 정상/brownfield/excluded case는 exit 0.

- [ ] Step 3: 파일 count만 맞고 Coordinator가 새 checker를 호출하지 않는 사각을 막는다. Claude command와 Codex orchestrator에서 `check-*.py` 이름 집합·순서를 실제 19개 파일과 대조한다. 네 API-error contract checker의 profile/scope/API/controller/scope-BC/error-BC와 schema의 project inventory, composition checker의 URLconf/registrar selector까지 추출해 문서 계약과 일치시키며, 삭제된 catch-all은 0회·새 controller checker는 정확히 1회여야 한다.
- [ ] Step 4: Claude command와 Codex orchestrator prompt에서 19개 registry·selector 명령 계약을 추출하고, 그 계약대로 verifier가 합성한 명령을 합성 target에서 실행한다. Coordinator는 실행 가능한 별도 renderer가 아니라 prompt이므로 “실제 렌더링을 런타임 관측했다”고 과장하지 않는다. 네 API-error contract checker와 composition registrar slice는 완전한 code-profile 인자와 preserve/auto 인자를 실행하고, 나머지 14개는 현행 positional target/default CLI를 사용한다. composition checker는 어느 mode에서도 기존 DI slice를 잃지 않는다. root-only 수동 호환이 있더라도 Error response G2 증거로 집계하지 않는다.
- [ ] Step 5: 한 checker의 exit 1과 다른 checker의 exit 2를 각각 합성 실행에 주입해 둘 다 수집되는지 확인하고, Coordinator prompt가 두 exit를 모두 G2 blocker로 보존하며 한 실패 뒤에도 나머지 결과를 수집하도록 명시하는지 별도로 의미 검증한다. 이를 실행 가능한 Coordinator exit-propagation 구현의 관측으로 보고하지 않는다. selector/argparse 계약을 소유하는 API-error-aware 6개(#2·#3·#5·#6·#15·#16)는 각각 `--help=0`, 대표 parser/selector 사용 오류=1, 계약 위반=2를 실제 프로세스로 확인한다. 나머지 13개 positional legacy checker는 기존 CLI를 소급 변경하지 않고 valid target/default 실행과 invalid/missing target=1을 확인한다. 이 13개에 `--help` 계약을 새로 발명하지 않는다.

---

## Part E — 사용자 문서와 평가 계약

### Task E1: README 표준 tree와 에러 설명 교체

**Files:**

- Modify: `README.md`

- [ ] Step 1: common response tree에 빈 `__init__.py`와 단일 `error_out.py`를 표시한다.
- [ ] Step 2: BC `schema/`에 단일 `error_out.py`와 `<Bc>ErrorCode`/`<Bc>ErrorOut`/prepared concrete를 표시하고 `<problem>_error_out.py` 문구를 제거한다.
- [ ] Step 3: controller 직접 catch/Status, framework 기본 오류, helper/handler 금지, project api/urls/BC registrar 책임을 짧은 예시로 설명한다.
- [ ] Step 4: 19종 문구는 유지하되 catch-all 강제처럼 읽히는 설명을 새 checker 책임으로 바꾼다.

### Task E2: 활성 eval을 새 표준 epoch로 갱신하고 과거 결과는 보존

**Files:**

- Modify: `workspace/eval/README.md`
- Modify: `workspace/eval/rubric/RUBRIC.md`
- Modify: `workspace/eval/rubric/EVAL-METHOD.md`
- Modify: `workspace/eval/rubric/rubric-metrix.md`
- Modify: `workspace/eval/tools/FC-GOLDEN.md`

- [ ] Step 1: 구현 시작 직전 parent HEAD의 full SHA를 v3 기준 commit locator로 기록하고, `2026-08-03 code-json profile 전환`을 rubric v4/new epoch 후보로 사전등록한다. 결과 식별 키를 `epoch + error profile + rubric version + dimension ID`로 만들어 구·신 `NJ-7 PASS`를 같은 의미로 집계하지 않는다. 별도 복제 archive를 만들지 않고 immutable Git commit을 재현 정본으로 쓴다.
- [ ] Step 2: `workspace/eval/README.md`의 “과거 결과는 working tree에 없고 git history에만 있다”는 틀린 설명을 실제 14개 결과 파일에 맞게 고치고, v3 history와 v4 candidate/active 경계·소급 금지를 안내한다. 새 `fixtures/api_error_contract/{requirements.txt,test_api_error_contract.py}`의 목적·exact pin·재현 명령과 “20번째 checker가 아님”도 tree에 기록한다.
- [ ] Step 3: SD-6을 “domain/application HTTP 무지 + 알려진 BC 예외→status는 해당 controller가 직접 소유”로 바꾼다. 중앙 handler 발화/예외 raise를 합격 조건에서 제거하고, import 없는 HTTP 의미 `status` DTO Goodhart 변종은 계속 FAIL로 둔다.
- [ ] Step 4: NJ-7 ID와 강도는 유지하되 v4 이름을 `BC 오류 직접 계약`으로 바꾼다. PASS는 좁은 try·구체 catch·직접 no-arg ErrorOut/Status·framework 기본 보존, FAIL은 helper/handler/catch-all·broad catch·raw 오류 응답이다. 현재 차원 수는 NJ-7 포함 34개이므로 “33” 표기와 NJ-1~6 전용 template을 함께 고친다.
- [ ] Step 5: NJ-4는 실제 반환 BC status의 `<Bc>ErrorOut>` 선언과 framework ErrorOut 비광고를 평가한다. 정확성은 status→BC base까지이며 status별 식별자 subset은 Enum 전체로 과대 노출되는 승인된 한계라고 적는다. Q-2는 “선택된 error profile의 wire/status/header/version 일관성”으로 바꾼다.
- [ ] Step 6: EP-1/EP-2는 깨진 body/요청 validation이 framework 기본 400/422 흐름이며 BC ErrorOut/code가 아님을 관측하고 body exact snapshot을 금지한다.
- [ ] Step 7: EP-3을 두 종단으로 분리한다: raw infra 예외는 framework 기본 500, 공개하기로 한 retryable 소진은 자기 BC 예외로 정규화된 뒤 controller가 503/409+code/header로 반환. 둘을 하나의 raw handler 요구로 합치지 않는다.
- [ ] Step 8: EP-4 재고 부족은 409와 승인된 BC JSON을 확인한다. `FC-GOLDEN` M3은 해당 scope가 body status field를 승인했을 때만 그 default를 변조하고, 그렇지 않으면 controller의 HTTP status 표현을 변조해 mapping assertion이 Red인지 보게 한다. 주입 위치는 “해당 controller의 Status/error mapping”으로 둔다.
- [ ] Step 9: `rubric-metrix.md`에 NJ-7뿐 아니라 필수 C 마스크, TIER-OBS/EP 표, 표준 결과 섹션 순서를 복구한다. EVAL-METHOD의 “실재 checker 2개”·미동결 상태·bytecode 청결 절차도 현재 19개/v4 사전등록 상태와 맞춘다.
- [ ] Step 10: 다섯 활성 평가 파일의 모든 `NJ-7`/catch-all/central handler/problem+json 참조를 다시 검색한다. 현재 판정표·집계·오류경로 정독 절차는 새 기준으로 바꾸고, NJ-7 신설 이유 같은 과거 회고는 삭제하지 않은 채 “v3에서 폐기·v4에서 동일 ID 재정의”라고 경계를 붙인다. 과거 results 14개는 byte-for-byte 보존한다.
- [ ] Step 11: 적대 리뷰와 34-ID 기계 대조가 끝나기 전에는 v4를 “동결됨”으로 자기 승인하거나 새 결과를 채점하지 않는다. Task F3에서 사용자에게 v4 diff/epoch를 제시해 명시적 freeze 승인을 받은 뒤에만 active/frozen header를 확정한다.

### Task E3: DEVLOG에 결정과 비결정 기록

**Files:**

- Modify: `workspace/DEVLOG.md`

- [ ] Step 1: 새 DR 항목에 기존 중앙 handler 설계가 사용자 요구와 충돌한 근거, 새 code profile, common/BC/controller 책임을 기록한다.
- [ ] Step 2: checker 교체가 “백스탑 추가”가 아니라 catch-all 삭제↔controller checker 추가의 19개 유지임을 기록한다.
- [ ] Step 3: schema/controller/context/OpenAPI checker의 직접형 책임과 reviewer 사각을 적어 exit 0을 전체 의미 준수로 과대 해석하지 않게 한다.
- [ ] Step 4: RFC knowledge/brownfield, transient legacy checker, eval historical results를 보존한 이유를 기록한다.
- [ ] Step 5: 합성 matrix 결과, corpus mirror, plugin validate, 적대 리뷰 지적·중재 결과와 runtime fixture의 resolved Python/Django/Ninja/Ninja Extra/Pydantic 버전·테스트 수를 실제 실행값으로 채운다.

### Task E4: 현행 파이프라인 시각화만 동기

**Files:**

- Modify: `workspace/flow/dddjango-timeline.html`

- [ ] Step 1: API reviewer 설명의 RFC 9457 단일 기본값을 selected error profile/BC code 계약으로 바꾼다.
- [ ] Step 2: 16종/touched-only 표기를 19종과 checker별 touched/full-tree 구분으로 고치고 새 controller checker 이름을 표시한다.
- [ ] Step 3: `workspace/tools/smoke_timeline.html`은 과거 smoke 관측이므로 수정하지 않는다. 시각화의 문구만 동기하고 레이아웃·스타일 재설계는 하지 않는다.

---

## Part F — 잔존 모순 감사와 최종 검증

### Task F1: 금지/허용 anchor 감사

- [x] Step 1: 활성 배포 표면에서 새 프로필을 정반대로 말하는 문구를 검색한다.

```bash
git grep -n -E '중앙.*(exception_handler|예외.?핸들러)|catch-all.*필수|problem helper|<problem>_error_out|type=about:blank|instance.*problem\+json|11-slot' -- dddjango codex-dddjango README.md workspace/eval/README.md workspace/eval/rubric workspace/eval/tools workspace/flow
grep -R -nE 'catch-all.*필수|problem_response|validation_error_out|common\.ninja\.errors' workspace/eval/fixtures/api_error_contract || true
```

Expected: RFC brownfield 절과 서버렌더 별도 규칙 외 신규 기본 강제 잔존 0. `workspace/eval/results/**`, 과거 design/plan, DEVLOG의 과거 항목은 역사 자료라 이 자동 잔존 게이트의 검색 범위에서 제외하고, 새 문서가 이를 현재 규범으로 다시 참조하지 않는지만 별도로 확인한다.

- [x] Step 2: 새 필수 anchor가 Claude/Codex 양쪽에 있는지 확인한다.

```bash
git grep -n -E 'dddjango-code-json|common ErrorOut shape/approval|BC 오류 직접 계약|check-api-error-controller-contract' -- dddjango codex-dddjango README.md workspace/eval/rubric workspace/eval/tools
```

- [x] Step 3: `check-catch-all-handler.py` 파일/게이트 참조는 역사 문서·과거 results 외 0인지 확인한다.
- [x] Step 4: 일반 RFC 9457 설명이 `architecture-api` brownfield/alternative 프로필에 남아 있고 신규 default와 혼합되지 않았는지 사람이 문맥으로 다시 읽는다.
- [x] Step 5: 삭제/금지된 구현과 구 등록 방식이 활성 표면에 남지 않았는지 별도 검색한다.

```bash
git grep -n -E 'common\.ninja\.errors|problem_response|validation_error_out|from .*\.api import api|^[[:space:]]*api\.register_controllers' -- dddjango codex-dddjango README.md
git grep -n '_is_retryable_db_error' -- dddjango codex-dddjango README.md
git grep -n -E '백스톱 16종|16종 전부|touched만|이번 변경분만' -- dddjango codex-dddjango README.md workspace/flow workspace/eval/README.md
```

Expected: `common.ninja.errors` import, 신규 code-profile 생성 레시피의 `problem_response`/validation schema, module import-side-effect 등록, 16종 현행 표기는 0. `_is_retryable_db_error`는 서버렌더 middleware-local 정의/호출과 명시적인 `preserve-established` checker/reviewer 진단만 allowlist로 문맥 확인하고, 신규 code 프로필의 생성 레시피에는 0이다.

### Task F2: 정적·미러·플러그인 검증

- [x] Step 1: Python 소스를 pyc 생성 없이 compile한다.

```bash
python3 -c 'from pathlib import Path; files=list(Path("dddjango/scripts").glob("*.py"))+list(Path("codex-dddjango/skills/dddjango/scripts").glob("*.py"))+[Path("workspace/tools/api_error_backstop_matrix.py")]; [compile(p.read_text(), str(p), "exec") for p in files]'
```

- [x] Step 2: reference mirror를 다시 확인한다.

```bash
python3 workspace/tools/corpus_mirror_sync.py --check
```

- [x] Step 3: checker count/byte mirror, Coordinator prompt의 명령 계약과 그 계약에서 합성한 checker 명령, 전체 matrix를 다시 검증한다. 실행 가능한 별도 Coordinator renderer가 있는 것처럼 보고하지 않는다.
- [x] Step 4: Part A2 runtime fixture를 `python -B`로 다시 실행하고 resolved version, `Status` 회귀, auth/framework/OpenAPI 결과를 기록한다.
- [x] Step 5: Claude/Codex Coordinator prompt에서 추출한 checker registry 집합·순서가 실제 19개 파일과 같고, 네 API-error contract checker 호출에 승인 profile/scope/API/controller/scope-BC/error-BC, schema checker에 두 project error-module inventory, composition checker에 URLconf/registrar selector가 있는지 검증한다. API-error-aware 6개는 `--help=0`, positional legacy 13개는 valid target/default와 invalid/missing target=1이라는 각자 CLI 계약을 지킨다. 합성 실행에서 exit 1/2를 각각 관측하고, prompt가 둘 다 G2 blocker로 선언하며 모든 결과 수집을 요구하는지는 문서 의미로 대조한다. 이 둘을 실행 가능한 Coordinator 전파 테스트 하나로 합쳐 주장하지 않는다.
- [x] Step 6: 의미 미러 10쌍을 단일 표로 대조한다: 지식 SKILL 4쌍(architecture-api, Ninja, houserules, test), 역할 5쌍(architect, API reviewer, acceptance, coder, discipline reviewer), Coordinator 1쌍. 각 쌍의 12-slot/profile/direct Status/framework default/new checker 필수 anchor와 central handler/catch-all 구 anchor 부재를 검사하고 플랫폼 전용 frontmatter 차이만 허용한다. web/cleancode SKILL 두 쌍은 삭제 심볼·구 규칙을 직접 담지 않아 변경 비대상인지 negative check한다.
- [x] Step 7: RUBRIC·EVAL template·metrix에서 기대 ID 집합 `SD-1..7 + SH-1..10 + NJ-1..7 + FC-1..3 + Q-1..7 = 34`를 파싱해 중복·누락 없이 대조한다. `workspace/eval/results`는 tracked 14개인지, untracked 추가와 `git diff HEAD -- workspace/eval/results`가 0인지 구현 시작 시 기록한 baseline과 byte 대조한다.
- [x] Step 8: Claude plugin 구조를 검증한다.

```bash
claude plugin validate dddjango --strict
```

- [x] Step 9: Codex manifest JSON과 양 manifest version 동일성을 읽기 전용으로 확인한다. 버전은 바꾸지 않는다.
- [x] Step 10: whitespace/diff를 확인한다.

```bash
git diff --check
git status --short
git diff --stat
```

### Task F3: fresh-context 적대 리뷰 3축과 중재

- [x] Step 1: **스펙 추적 reviewer**에게 승인 설계 §1~17과 이 계획의 1:1 누락/왜곡, 특히 12 불변식·필드 변경 승인·framework 기본·helper 금지·try/no-arg를 공격하게 한다.
- [x] Step 2: **코퍼스/미러 reviewer**에게 Claude/Codex/reference/workspace/eval/checker registry의 모순, stale anchor, byte/semantic mirror 누락, 역사 문서 오염을 공격하게 한다.
- [x] Step 3: **과적합/실효 reviewer**에게 checker activation, AST false positive/negative, brownfield/다중 API scope, ACL 카브아웃, 동적 OpenAPI, file/stream/redirect, 평가 소급을 공격하게 한다.
- [x] Step 4: 첫 holdout 전에 checker byte hash를 동결한다. 과적합 reviewer는 A1 matrix를 보지 않은 fresh context에서 설계와 구현된 checker만 보고 최소 8개의 holdout fixture(분리/공유 brownfield, alias/re-export, Pydantic 메타필드, helper 2-hop, dynamic response, auth ErrorOut, artifact 전무)를 임시 경로에 작성한다. 최초 실행의 오탐/미발화를 수정 전 증거로 기록하고 유효 case는 이후 A1 회귀 matrix에 편입한다.
- [x] Step 5: 첫 holdout으로 checker를 고친 뒤 다른 fresh reviewer가 2~4개의 작은 2차 unseen case를 만든다. 최종 판정 전 구현자와 A1 matrix에 공개하지 않고 실행하며, 이 결과를 회귀 matrix 재실행과 별도 효능 증거로 기록한다. 통과 뒤 재발 방지를 위해 편입할 수 있으나 그것을 “unseen 통과” 증거로 재사용하지 않는다.
- [x] Step 6: 지적을 `adopt | reject | defer`로 중재하고 근거를 이 문서의 `Implementation Adversarial Review Record`에 남긴다. 중요한 수정 후 최소 한 reviewer에게 재검토를 요청한다.
- [ ] Step 7: v4 평가 diff·34-ID 대조·epoch key를 사용자에게 제시하고 명시적 freeze 승인을 받는다. 승인 전에는 새 fixture를 채점하거나 active/frozen으로 표시하지 않는다.
- [x] Step 8: 리뷰 반영 뒤 F1/F2를 처음부터 다시 실행한다. 리뷰 전 결과를 최종 증거로 재사용하지 않는다.

### Task F4: 커밋 경계

- [x] Step 1: 구현 diff가 플러그인/corpus/eval/검증 도구/DEVLOG와 이 계획의 구현 리뷰 기록 범위뿐인지 확인한다.
- [x] Step 2: 사용자 소유 변경이 섞이지 않았는지 `git status --short`와 `git diff`로 확인한다.
- [x] Step 3: 아래 예상 파일을 정확히 지정해 구현 이력을 기록한다. 이 계획은 F3의 구현 리뷰 기록 때문에 포함한다. 두 설계 metadata는 선행 문서 기준선 commit에 있으므로 구현 diff에는 포함하지 않는다. 디렉터리 전체를 stage하지 않으며, 목록 밖 생성·수정 파일이 있거나 시작 전 변경과 겹치면 중단해 사용자 변경을 분리한다.

  실제 구현은 fresh-review RED와 root-cause fix를 보존하기 위해 검토 가능한 순서의 작은 commit들로 기록했고, 마지막 closure commit은 README·DEVLOG·이 계획 세 파일만 정확히 stage한다. 아래 목록은 단일 commit 명령의 재실행 지시가 아니라 전체 구현 scope의 allowlist 기록이다.

```bash
git add -- \
  README.md workspace/DEVLOG.md workspace/plan/2026-08-03-api-error-management-plan.md \
  workspace/tools/api_error_backstop_matrix.py \
  workspace/eval/fixtures/api_error_contract/requirements.txt \
  workspace/eval/fixtures/api_error_contract/test_api_error_contract.py \
  workspace/flow/dddjango-timeline.html workspace/eval/README.md \
  dddjango/skills/architecture-api/SKILL.md \
  dddjango/skills/architecture-api/references/final.md \
  dddjango/skills/implementation-django-ninja/SKILL.md \
  dddjango/skills/implementation-django-ninja/references/final.md \
  dddjango/skills/discipline-houserules/SKILL.md \
  dddjango/skills/discipline-houserules/references/final.md \
  dddjango/skills/implementation-test/SKILL.md \
  dddjango/skills/implementation-test/references/final.md \
  dddjango/skills/implementation-django-web/references/final.md \
  dddjango/skills/discipline-cleancode/references/final.md \
  dddjango/agents/design-architect.md dddjango/agents/design-review-api.md \
  dddjango/agents/acceptance-tester.md dddjango/agents/coder.md \
  dddjango/agents/discipline-reviewer.md dddjango/commands/dddjango.md \
  dddjango/scripts/check-error-centralization.py \
  dddjango/scripts/check-api-error-controller-contract.py \
  dddjango/scripts/check-context-isolation.py \
  dddjango/scripts/check-composition-root.py \
  dddjango/scripts/check-openapi-error-declaration.py \
  dddjango/scripts/check-response-schema-bypass.py \
  dddjango/scripts/check-common-container.py \
  dddjango/scripts/check-transient-overmapping.py \
  dddjango/scripts/check-synthetic-infra-exc.py \
  dddjango/scripts/check-idempotency-scope-creep.py \
  codex-dddjango/skills/architecture-api/SKILL.md \
  codex-dddjango/skills/architecture-api/references/final.md \
  codex-dddjango/skills/implementation-django-ninja/SKILL.md \
  codex-dddjango/skills/implementation-django-ninja/references/final.md \
  codex-dddjango/skills/discipline-houserules/SKILL.md \
  codex-dddjango/skills/discipline-houserules/references/final.md \
  codex-dddjango/skills/implementation-test/SKILL.md \
  codex-dddjango/skills/implementation-test/references/final.md \
  codex-dddjango/skills/implementation-django-web/references/final.md \
  codex-dddjango/skills/discipline-cleancode/references/final.md \
  codex-dddjango/skills/dddjango-design-architect/SKILL.md \
  codex-dddjango/skills/dddjango-design-review-api/SKILL.md \
  codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md \
  codex-dddjango/skills/dddjango-coder/SKILL.md \
  codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md \
  codex-dddjango/skills/dddjango/SKILL.md \
  codex-dddjango/skills/dddjango/scripts/check-error-centralization.py \
  codex-dddjango/skills/dddjango/scripts/check-api-error-controller-contract.py \
  codex-dddjango/skills/dddjango/scripts/check-context-isolation.py \
  codex-dddjango/skills/dddjango/scripts/check-composition-root.py \
  codex-dddjango/skills/dddjango/scripts/check-openapi-error-declaration.py \
  codex-dddjango/skills/dddjango/scripts/check-response-schema-bypass.py \
  codex-dddjango/skills/dddjango/scripts/check-common-container.py \
  codex-dddjango/skills/dddjango/scripts/check-transient-overmapping.py \
  codex-dddjango/skills/dddjango/scripts/check-synthetic-infra-exc.py \
  codex-dddjango/skills/dddjango/scripts/check-idempotency-scope-creep.py \
  workspace/reference/architecture-api/reference/final.md \
  workspace/reference/implementation-django-ninja/reference/final.md \
  workspace/reference/discipline-houserules/reference/final.md \
  workspace/reference/implementation-test/reference/final.md \
  workspace/reference/implementation-django-web/reference/final.md \
  workspace/reference/discipline-cleancode/reference/final.md \
  workspace/eval/rubric/RUBRIC.md workspace/eval/rubric/EVAL-METHOD.md \
  workspace/eval/rubric/rubric-metrix.md workspace/eval/tools/FC-GOLDEN.md
git add -u -- \
  dddjango/scripts/check-catch-all-handler.py \
  codex-dddjango/skills/dddjango/scripts/check-catch-all-handler.py
git commit -m "feat: adopt BC-owned API error contracts"
```

릴리즈/version bump는 이 커밋 뒤 별도 사용자 승인 작업이다.

---

## 최종 합격 조건

- Claude/Codex가 모두 신규 Ninja 기본을 `dddjango-code-json`으로 선택하고 RFC 9457은 brownfield/alternative로만 보존한다.
- common response 디렉터리와 BC error module의 단일 파일 규칙이 reference·역할·checker·README에서 일치한다.
- 공통 shape 변경은 사용자 승인 없이 자동 진행되지 않는다.
- Error checker는 승인된 profile, 정확한 API/controller source, scope-BC/error-BC와 project error-module inventory로 활성화된다. code profile은 `error-bc`가 비어도 common ErrorOut을 요구하고, no-error BC의 BC module 부재와 artifact 생략을 구분한다. project-wide surface inventory가 shared-module mixed profile을 발견하면 추측하지 않고 G1로 반송한다.
- canonical dddjango-code-json ErrorCode value는 명시된 project code inventory 전체에서 유일하고 canonical 모양의 preserve module은 명시 inventory로 제외된다. preserve mode에서도 기존 application HTTP 누수와 OpenAPI 누락 검출력이 사라지지 않는다.
- known BC 오류는 controller가 좁은 try/구체 catch/direct no-arg ErrorOut/`Status`로 처리한다.
- helper/factory/serializer/mapping/custom handler/catch-all이 신규 code 프로필에서 생성되지 않는다.
- framework 오류는 custom ErrorOut/OpenAPI로 바뀌지 않으며 body exact snapshot도 생기지 않는다.
- 실제 BC 오류 반환 status와 OpenAPI `<Bc>ErrorOut` 선언이 일치한다.
- 지원 pin의 실제 Ninja Extra class controller에서 한 승인 fixture 변형의 성공/오류 body `status` field와 `Status` wrapper가 충돌하지 않고 auth/header/framework/non-JSON/OpenAPI runtime fixture가 skip 없이 통과한다. 이를 plugin 기본 property로 일반화하지 않는다.
- root API 오류 경계는 context checker, BC registrar/project URLconf 조립은 기존 composition-root checker, BC DI 조립은 같은 checker의 별도 기존 slice가 맡아 책임과 진단이 섞이지 않는다. 정확한 URLconf/registrar selector와 mounted route 계약 테스트가 모두 통과한다.
- checker는 19개이며 Claude/Codex script가 byte-identical하고 합성 matrix가 전부 통과한다.
- reference 11종 mirror, plugin validate, Python compile, diff check가 통과한다.
- 과거 eval results 14개는 byte 보존되고 v3 full commit locator와 v4 `epoch+profile+version+ID`가 분리되며, 34-ID 대조와 사용자 freeze 뒤 새 rubric은 명시된 기준 epoch 이후 산출물에만 적용된다.
- 아래 계획 적대 리뷰의 blocker가 0이고, 구현 후 별도 3축 리뷰·2단 unseen holdout의 blocker도 0이며 채택/기각/연기 근거가 기록된다.

## Planning Adversarial Review Record

| 관점 | 지적 | 판정 | 계획 반영 |
|---|---|---|---|
| 스펙 추적 | F3가 이 계획을 수정하지만 구현 staging에 계획이 없었음 | adopt | F4에 계획 파일을 추가. 두 설계 metadata는 이 계획과 함께 선행 문서 기준선 commit으로 분리 |
| 스펙 추적 | registrar/import side effect를 기존 checker가 본다는 전제가 실제 19개에 없음 | adopt | 첫 초안의 D3 배정을 재검토해 승인 설계대로 기존 `check-composition-root.py`에 URL composition 전용 slice를 추가. D3는 root API만 소유하고 기존 DI V1~V3는 독립 회귀로 보존 |
| 스펙 추적 | route 404 오광고, known catch→HttpError/re-raise, root-local catalog, 일반 HttpError runtime이 빠짐 | adopt | A1·A2·D2·D3·D4에 직접 음성/양성 사례 추가 |
| 스펙 추적 | 설계 §12의 ErrorCode 최소화·예외 병합·승인 안정 field·공개 문자열 안전성·client rollout 추적 부족 | adopt | B1/B4/C1의 knowledge·test·reviewer 레인에 배정. `title/detail` property를 전제하지 않고 새 checker 조건으로 과승격하지 않음 |
| 코퍼스·미러 | `--write`가 비대상 11종 drift까지 덮을 수 있음 | adopt | B7에 편집 전 drift 0과 write 전 정확한 6-skill drift set 게이트 추가 |
| 코퍼스·미러 | 성공 `Status`·승인 exact body, eval 34-ID, 역사 result, 의미 미러 10쌍의 최종 증거 부족 | adopt | A2 성공 회귀, F2 ID/result/10쌍 기계·앵커 검증 추가 |
| 코퍼스·미러 | timeline 권위 분류, Graphify 완료 주장, `_is_retryable_db_error` 전역 0 기대가 부정확 | adopt | 현행 timeline만 동기 대상으로 분리, Graphify 중간 산출물+직접 정독으로 정정, brownfield/web allowlist 분리 |
| 과적합·실효 | opaque `scope`+BC만으로 controller membership과 mixed API를 판정할 수 없음 | adopt | scope는 label로 강등하고 exact API/controller/URLconf/registrar module과 scope-BC/error-BC를 selector로 추가. project-wide surface inventory preflight가 shared module/복수 API를 G1 반송 |
| 과적합·실효 | no-error BC module 부재와 지정 BC artifact 부재 규칙이 모순 | adopt | 전체 `scope-bc`와 ErrorOut이 필요한 `error-bc` 부분집합을 분리. code profile의 common은 항상 필수이고 BC module은 `error-bc`에만 필수 |
| 과적합·실효 | 계획이 code 유일성을 scope-local로 완화했고 per-scope 입력으로 project-global 판정을 약속함 | adopt | 반복 code/preserve canonical error-module inventory를 D1 입력으로 추가해 project-global 유일성과 preserve 제외를 구현 가능하게 고정. 전체 surface 공유 판정은 Coordinator preflight가 소유 |
| 과적합·실효 | surface inventory의 “중복” 금지가 같은 code profile의 승인된 common/Enum 재사용까지 막는 것으로 읽힘 | adopt | 같은-profile 재사용은 경로를 dedupe해 허용하고 역할·계약 충돌 및 code↔preserve 공유만 G1 반송. A1 정상 재사용 oracle과 D1 code-mode 한정도 명시 |
| 과적합·실효 | exact controller를 받아 놓고 BC presentation 전체를 scan하면 같은 BC의 분리 brownfield를 오탐 | adopt | D2 managed set을 exact controller+canonical error module+controller가 직접 import한 presentation-local 1-hop+선택 API가 직접 import한 자기 package production 1-hop으로 제한한다. API 1-hop은 root purity 우회만 닫고 재귀 확장하지 않는다. 2-hop/선택 밖 의미는 reviewer 소유 |
| 과적합·실효 | preserve mode가 기존 application HTTP/OpenAPI checker 검출력을 잃음 | adopt | 기존 직접형을 D3/D4 legacy touched slice로 보존하고 grandfather/신규 위반 matrix 추가 |
| 과적합·실효 | non-error OpenAPI 사후가공 허용은 승인 설계보다 넓음 | adopt | code profile의 모든 `get_openapi_schema` 사후가공 금지로 복원. decorator non-response metadata만 보존 |
| 과적합·실효 | whole-program AST provenance와 단일 holdout은 과적합·오탐 위험 | adopt | direct import/alias/상대 import/1단계 assignment만 증명하고 의미는 reviewer에 위임. hash 고정 1차 holdout+별도 2차 unseen으로 분리 |
| 안전·역사 | G2 전 untracked production을 빼면 새 extra schema/helper가 검사에서 사라짐 | adopt | “추적 중이거나 이번 작업에서 추적 예정”인 tracked+untracked non-ignored production으로 operationalize; ignored/test/generated는 제외 |
| 제안 중재 | concrete Schema를 `<Problem>ErrorOut`으로 일괄 개명 | reject | 사용자 승인 예시와 최종 설계는 `<Problem>Error`를 허용하며 wire/소유 불변식이 아님. Python 예외는 프로젝트의 `Exception` 명명과 구분 |
| 제안 중재 | v3 별도 archive 복제, global header handler, tuple fallback/body status 개명 | reject | full Git SHA+result 무변경 guard로 역사 재현. 나머지는 helper 금지·framework default·승인 wire 계약과 충돌 |
| 범위 | shared-module mixed profile의 범용 지원, Broccoli 실제 이주, client 코드 변경, release/version bump | defer | 단일 분리 surface 밖은 별도 설계/작업. 단 12-slot compatibility에는 client 동시 전환 결정을 필수 기록 |

최종 closure는 계획 본문 리뷰 입력 snapshot SHA-256 `ff812bea53c0cf280e67652d2aeab97ee35592a3bf43560a4b789d04e89c78bf`(792줄)에서 스펙 추적 `blocker 0/high 0`, 코퍼스·미러 `blocker 0/high 0`, 과적합·실효 `blocker 0/high 0`이다. 스펙 reviewer의 790줄 선행 closure 뒤 들어간 same-profile dedupe 보강은 과적합 reviewer와 코퍼스 reviewer가 위 snapshot 전체 재독으로 다시 확인했다. 이 문장은 판정 기록만 추가하며 구현 계약을 바꾸지 않는다. 따라서 계획 단계 blocker는 0이며, 구현 단계는 별도로 아래 record와 Task F3의 새 리뷰를 통과해야 한다.

## Implementation Adversarial Review Record

> Task F3에서 실제 구현 diff와 unseen holdout을 기준으로 채운다. 계획 단계 리뷰 결과를 복사해 PASS로 대신하지 않는다.

| 관점 | 지적 | 판정 | 구현 반영 |
|---|---|---|---|
| 사용자 정정·최종 재감사 | plugin이 공통 `ErrorOut`을 `code/title/status/detail` 같은 property 목록으로 고정하는 것으로 읽힐 여지와 Codex 의미 미러 3곳의 alias/metadata 구문 drift | adopt | plugin 기본 property 목록을 전부 제거했다. 현재 프로젝트의 승인된 exact shape를 동적으로 관찰해 field/type/required/default/nullability/모든 `Field` metadata/model config·legacy `Config`/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 의미를 보존하고, 신규 생성·변경은 일반 G1과 분리된 사용자 명시 승인으로만 허용한다. checker matrix를 최종 674-case로 확장했고 Codex drift와 Pydantic config replacement/header precedence, FieldInfo merge·AliasPath, body-status provenance edge를 정본 의미로 고쳤다. canonical schema 정의의 dynamic field/default/method/hook/config/decorator/import/binding은 단순해 보여도 schema checker가 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`를 내며, target-pin runtime/mounted OpenAPI 및 API/discipline 이중 review를 갖춘 `RESOLVED_DYNAMIC_ERROR_SHAPE_ANALYSIS`로만 해소하게 했다. controller/OpenAPI의 제한된 정적 판정은 보조 진단일 뿐 이 schema proof 요구를 제거하지 않는다. |
| 최종 callable 적대 재검사 | f-string conversion과 project callable의 최종 module/global binding을 정의 시점 값으로 오판하면 runtime alias와 정적 shape가 달라지고, 동적 proof를 확인할 API reviewer의 Phase 2 입력 모드가 없었음 | adopt | `!r`/`!a` 등 미지원 conversion과 final binding·global lookup을 증명하지 못하는 callable은 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`로 보낸다. 정적 증명은 trusted import·안전한 function signature·literal/direct-name 기반 단순 assignment만 허용하는 import-time allowlist로 제한해 direct shadow뿐 아니라 `globals()`·walrus·compound control flow·project import side effect·implicit protocol mutation을 runtime proof로 넘긴다. 33개 regression/control case를 matrix에 추가했고, API reviewer에 읽기 전용 `DYNAMIC_ERROR_SHAPE_PROOF_REVIEW` 입력·산출 계약을 Claude/Codex 양쪽에 추가했다. |
| exact-shape 동적 경계 재감사 | `json_schema_extra` 등 non-alias config callable, class-header `**`, legacy `Config` 상속, class decorator/hook, field default, private binding, canonical schema import side effect와 controller model mutation이 alias 전용 분석 또는 prepared-concrete 경로를 우회할 수 있었음 | adopt | canonical common/BC schema 정의의 statically non-inert surface는 항상 runtime proof로 보내고 직접 import-time side effect·BC executable class body·controller model config 변경/재빌드는 blocker로 분리했다. read-only snapshot/get은 허용한다. blanket project-import marker만으로 form-specific 검사가 가려지지 않도록 inline lambda causal과 literal/static control을 분리해 추가 34개 case를 편입했다. |
| 스펙 추적 | 계획 상태가 아직 “구현 착수 전”이었고 README framework-default 요약에 일반 `HttpError`가 빠짐 | adopt | 상태를 실제 단계로 고치고 README에 일반 `HttpError`를 추가했다. 별도 reviewer가 승인 불변식 12/12를 추적했고 Critical/Important 0으로 판정했다. |
| 코퍼스·미러 | 제품 finding 없음. 해당 reviewer는 과거 matrix 작업 이력 때문에 unseen 판정에는 사용할 수 없음 | adopt | unseen 증거에서 분리했다. 의미 미러 10/10, reference 11/11, checker·registry 19/19, 평가 ID 34/34, 과거 result 14개 byte 보존을 독립 확인했다. |
| 과적합·실효 | D1 fresh 25-case에서 6 root, D2 17-probe에서 6 root, D3 15-probe에서 2 root, D4·D5의 별도 fresh review에서 control-flow·provenance·scope 오탐/미발화를 발견 | adopt | 각 review 전 immutable commit/archive와 checker hash를 기록하고 최초 expected/actual을 보존했다. root-cause 수정과 causal/control matrix 편입 뒤 D1 6/6, D2 최종 4/4, D3 최종 3/3, D4 최종 11/11, D5 최종 인접 probe 4/4를 양 Python에서 재검토해 unresolved Critical/Important/Minor 0으로 닫았다. |
| 2단 holdout | 첫 fresh suite에서 defect를 찾은 뒤 reviewer-separated fix/re-review가 2~4개 인접 unseen control을 추가해 수정의 과적합과 새 오탐을 다시 공격해야 함 | adopt | D2 4-case, D3 3-case, D5 4-case 2차 probe를 최초 실행 증거와 matrix 재실행에서 분리했다. 유효 case는 이후 회귀로 편입했으나 최초 unseen 증거로 재사용하지 않았다. |
| controller 실행성 최종 재감사 | managed 1-hop 외부 호출의 branch/복합 suite/decorator/argument kind 전달 누락과 deferred generator·short-circuit·정적 dead loop 과탐 | adopt | 직접 재현 41개를 causal/control로 다시 실행해 모두 expected exit와 일치시켰다. 정적으로 지원하는 module-level 외부 call 중 실제 실행되는 것만 연결하고 branch의 schema/config/rebuild kind 집합을 보존하며, generator 소비·short-circuit·literal loop/match·compound termination을 구분한다. 핵심 인과/대조 19개를 matrix에 영구 편입했다. |
| 동적 proof·실행성 후속 재감사 | 동적 shape marker가 독립 custom handler/API override를 가리고, `for` 정상 else·break, `try` 예외 진입 상태, `while` body→else, `match` guard fallthrough/baseline에서 외부 호출 실행성을 오판함 | adopt | shape 의존 finding을 명시적으로 표시해 독립 구조 finding이 marker보다 우선하도록 했고 OpenAPI 구조 scan을 catalog 분석보다 먼저 수행한다. 외부 호출 연결은 normal/break/continue/return/raise outcome을 분리하고 예외가 날 수 있는 try prefix에서만 handler를 연결한다. API/controller 직접 경로와 causal/control 29개를 추가해 최종 matrix를 674개로 확장했다. |
| 최종 스펙 추적 리뷰 | slot 6의 별도 shape 승인 carrier가 Pydantic hook을 명시적으로 열거하지 않았고, `serializer/decorator` 금지가 승인된 Schema hook까지 제거하라는 뜻으로 읽힐 수 있었음 | adopt | exact shape·승인 carrier 전부에 validator/serializer/computed field/Pydantic hook inventory와 effective semantics를 추가했다. 금지는 ErrorOut→HTTP response serializer와 exception-handler registration decorator로 좁히고 승인된 common Schema hook은 보존 대상이라고 명시했다. 일반 Enum의 same-value 예시는 ErrorCode가 아닌 domain/shared-kernel 문맥이 이미 명확하므로 별도 중복 문구 제안은 reject했다. |
| 최종 코퍼스·평가 리뷰 | DEVLOG의 오래된 현재 안내가 v4 freeze 전 33항목 채점·결과 생성을 지시하고 현재 checker 수를 16으로 표시함 | adopt | historical DR/결과는 보존하고 Current State·현재 채점 안내·Pointers만 19 checker, 34-ID, `NOT ACTIVE · NOT FROZEN · SCORING PROHIBITED`, tracked v3 결과 14개 byte 보존으로 고쳤다. |
| 최종 과적합 리뷰 | 직접 import한 1-hop module의 class method가 `ErrorOut.model_config`를 바꾸는 호출은 controller checker가 연결하지 못함 | adopt-boundary / reject-expansion | 사용자가 선택한 결정적 백스톱은 common concrete, 오류 응답 helper, 좁은 try·구체 catch, 무인자 concrete다. 임의 객체 호출까지 whole-program 분석하도록 checker를 다시 확장하지 않는다. mutation callable의 정적 연결 범위를 module-level function/lambda로 명시하고 imported class method·2-hop·dynamic dispatch는 API/discipline reviewer의 명시 사각으로 기록한다. 이 사각에서는 checker exit 0을 shape 보존 증거로 쓰지 않는다. |
| 감사 무결성 | 최종 통합 holdout을 추가 실행하려던 일회성 Codex가 timebox 안에 fixture를 실행하지 못함 | reject | 프로세스를 종료했고 어떤 PASS 증거로도 세지 않았다. 완료된 checker별 fresh/2차 holdout, 후속 적대 재감사와 최종 674-case matrix만 판정 근거로 사용한다. |
