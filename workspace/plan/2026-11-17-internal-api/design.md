> 설계 정리본 — F4-150 판(dddjango 2.41.0) 설계 확정 v1.3(설계 독립 검토 둘 · 좁은 재확인 둘에서 닫힘)에서 현장 코드 이름 · 현장 커밋을 걷은 판. 구현 중 바뀐 것(구현 독립 검토 처분 — 빈 `internal_api.py` 앵커 기준선 · `internal_api.urls` 마운트 꼴 · 보존 폴더 scope 대조 밖 · 문장 고침)은 `plan-2.41.0.md` «독립 검토 반영» 이 정본이다.

# F4-150 — 내부 API 객체의 표준 자리(설계 v1.3 확정 · 2026-11-18)

확정 = v1.3 + 좁은 재확인 2(검토자 C — A · B · C · T 중9 닫힘 · 새 차단 · 중요 0 · 사소 3 반영). v1.3 = v1.2 + 좁은 재확인 1 의 처분(검토자 T 중9 덜 닫힘 · 검토자 C 새 중요 A · B · C · 사소 — `op-rev/DISPOSITION.md` 끝 절). v1.2 = v1.1(`design-v1.1.md`) + 설계 독립 검토 둘의 처분(검토자 T 차단 0 · 중요 10 · 사소 7 · 검토자 C 차단 1 · 중요 4 · 사소 6 · 모두 받음). 재료: 재현 `work-a/REPORT.md` · 지도 `work-b/REPORT.md` · 검토 `rv-t/REVIEW.md` · `rv-c/REVIEW.md`(시제품 P1 · P2 · 적대 꼴 V1 ~ V19 · 출력 `rv-c/out/`).

## 1. 문제

한 BC 가 손님용 창구와, 앞단이 인터넷에 열지 않는 창구(부르는 쪽 = 같은 시스템의 SSE 서버 · 워커)를 함께 가질 때, 규칙 글(ninja §2.3 R-0715)은 별도 scope 를 허용하지만 표준 트리 · 검사기는 API 객체 하나 · BC 등록 함수 하나만 안다. 배포판 2.40.0 재현(운영자 확인):

| # | 무엇 | 조건 → 영향 | 실레인 |
|---|---|---|---|
| R1 | #429 `<project>/internal_api.py` | 둘째 API 모듈 → G2 귀속 · 빚 | 예 |
| R2 | #107 · #109 | 한 BC 가 두 객체에 등록 → 트리 · 공개 렌더 · 빚 | 예 |
| R3 | #16 code 레인 exit 1(ⓑ 들여온 루트 클래스 · ⓒ 두 scope BC URLconf identity · ⓓ 고정 밖 등록 함수 이름 · ⓔ 한 파일 생성자 둘) | 빚 불가 → STOP | ⓒ ⓔ 예 · ⓑ 현장 HEAD 꼴 |
| R4 | #5 code 레인 exit 1(ⓐ receiver provenance) | 들여온 루트 클래스 · 생성자 둘 | 현장 HEAD 꼴 |
| R5 | #63 경로 앞 레인은 프로젝트 전체 | 렌더마다 같은 프로젝트 전체 #63 | 레인 커밋 재측정 |
| R6 | R-0717(BC 마다 인스턴스) 위반과 못 가름 | `catalog_api.py` = #429 하나 · `api.py` 둘째 생성자 = G2 0 | 아니오 |
| R7 | #437 은 생성자 수를 안 세고 `api.py` 만 | T3 · T3w · T4c 통과 | 아니오 |
| R8 | pre-gate 는 #429 만 예보 | update 칸 미전사 · scope 렌더 exit 1 은 G2 에서 | 예(간접) |
| R9 | F4-151 한계 1(#15 one-hop 이 `api.py` 를 내부 렌더에 끌어옴) | 옛 위반이 신규 | 아니오 |
| R10 | F4-151 한계 2(#16 preserve 기준선 짝 검사) | 기준선 positional 강등 | 아니오 |
| R11 | F4-168 | 2.39.0 에서 닫힘 확인 | — |

같은 꼴 다른 자리: #431(check-context-isolation) · check-usecase-dto-placement 가 `api.py` · `urls.py` 만 · API 표면 판정 덤 경로(`check-composition-root.py:2773` · `check-usecase-dto-placement.py:287`)가 `register_{bc}_api` 고정. dddjango-web: 바뀔 것 없음(in-process api_client · OpenAPI 경로 하나 동결 — 받아들인 위험 기록만).

## 2. 결정

- **사용자 결정**: ① 별도 API 객체 · 주소 뿌리 `/internal/`(2026-11-09 «나.») ② 내부 창구 인증 의무 줄을 넣지 않음 — 일반 인증 규칙(§4.1)만(11-18 Q1 «나.» · 운영자 추천 «가» 와 다름 · 받아들인 위험 = 앞단 설정 누락 시 내부 창구가 인터넷에 열림) ③ 앞단 안쪽 사설망에서 부르는 내부 창구는 http 로 받아도 된다는 한 줄(11-18 Q2 «가» · 근거는 slot 2).
- **운영자 처리**(질문 생략 · 설계 처리 · 이의 시 뒤집음):
  - D1 **둘째 객체** = `<project>/internal_api.py` · 변수 `internal_api` · `urls_namespace="internal_api"`(글 · 검사 없음) · `<project>/urls.py` 의 `path("internal/", internal_api.urls)`. 루트 클래스는 `<project>/api.py` 의 정해진 클래스를 들여 짓는다(§6.2 «루트 API 가 둘 이상이면 모두 이 클래스로» — `internal_api.py` 안 클래스 정의는 금지). **고정 칸** — 내부 창구를 안 쓰는 프로젝트도 빈 파일로 갖는다(근거 #488 · #492 · R-3217 celery 선례 — `<project>/` 아래 «있을 때만» 은 #488 새 예외와 #492 «트리에 조건을 적어 두 채널로 만들지 않는다» 에 부딪힘). #429(R-3216)의 전제 «전역에 딱 하나» 를 «프로젝트 전역에 정해진 개수로 두는 조립 파일» 로 개정한다. 내용 없는 `internal_api.py` 는 API surface 가 아니다(빈 오류 모듈과 같은 판).
  - D2 **BC 안 새 폴더 없음** — 내부 창구 컨트롤러 칸은 공개 창구와 같은 기준으로 고른다(`api/<area>/` · 남이 정한 계약이면 `api/webhook/<provider>/`). 어느 객체에 다는지는 등록 함수 이름이 정한다(#90 · #91 — 새 전송 아님 · «누가 부르나» 로 가르지 않음).
  - D3 **등록 함수** = 같은 `api_router.py` 의 `register_<bc>_api(api: NinjaExtraAPI)` · `register_<bc>_internal_api(api: NinjaExtraAPI)` — 하나 또는 둘. 내부 창구만 가진 BC 는 뒤의 것만. URLconf 는 이름의 scope 에 맞는 표준 객체를 넘긴다.
  - D4 **R-0717 경계** = 닫힌 이름: `<project>/` API 모듈은 `api.py` · `internal_api.py` 뿐(#429) · `internal_api.py` 는 닫힌 허용 목록 · `api.py` 는 지금 허용에 «생성 하나 · 별칭 · 복사 금지» 만 더함(#437 — 진짜 프로젝트 패키지 하나에만) · 등록 함수 이름 둘뿐(#107) · 이름 ↔ 넘긴 객체 ↔ 주소(#440 — 출처로 판독). 새 G1 칸 없음 — slot 1 에 내부 scope 행 · slot 2 에 부르는 서버 · 사설망 · 앞단의 `/internal/` 차단 근거(저장소 파일:행 또는 발주자 진술). **STOP 범위**: 내부 scope 를 새로 만들거나 그 scope 의 endpoint 를 더하거나 바꾸는 실행에서 근거가 아무것도 없을 때만 `STOP_FOR_USER_APPROVAL`(architect · review-api 의 «때만» 목록에 넣음) — 그 밖 실행은 앞서 승인된 근거(이전 명세 파일:행)를 다시 써도 된다.
  - D5 **scope 마다 도는 검사**: 표준 내부 scope 는 공개 scope 와 같은 profile 이면 같은 공통 `FrameworkErrorSchema` · 같은 BC `bc_error_schema.py` 를 쓴다(그 밖의 보존 scope 만 공통 경로를 각각 승인 — ninja §6.2:611-612 고침). OpenAPI 는 객체마다. 경로 앞 응답 정본 · 표는 함께(행 `namespaces` 는 `urls_namespace` · `NOT_API_MIDDLEWARE` 의 «API 경로» 는 두 주소). code 레인은 `--api-module` 파일 이름으로 부를 등록 함수를 정하고(`<project>/internal_api.py` → `register_<bc>_internal_api` · 그 밖 → 지금대로 · 새 flag 없음), 루트 클래스는 #63 의 `_api_class_names` 와 같은 집합으로 받는다(`internal_api.py` 가 들이는 `<project>/api.py` 를 읽음).
  - D6 **F4-151 한계 둘을 함께 닫는다**(#15 one-hop 에서 다른 루트 API 모듈 뺌 · #16 preserve 기준선 모드 짝 검사 풂) — 기존 스모크 계약 둘을 뒤집는다(§5).
  - D7 **#63 은 그대로** — 표준 꼴에서는 안 나고, 비표준 루트 API 가 있으면 렌더마다 프로젝트 전체 #63 이 되풀이된다(받아들인 한계).
  - D8 **pre-gate 는 코드 그대로** — 표준 꼴은 G2 막힘이 없어짐. 남는 빈칸: update 칸 미전사(빈 `internal_api.py` 가 있으면 첫 생성이 update 칸이라 내부 객체 예보 0) · 내부 전용 BC 의 등록 함수 오명명(G2 #440 한 번). architect 자기 점검 · 리뷰어 글 한 줄로 줄인다.
  - D9 **새 트리 행 168행**(`api.py` 아래) — 168 ~ 182행이 +1. 런타임 도구는 «트리 N행» 을 파싱하지 않음(검토자 T 확인 — 진행 레인이 기계로 깨지지 않음 · 사람이 읽는 인용만 낡음). 치환은 대응표 · 제외 목록 · 숫자 참조 손목록 · 일회 대조 스크립트로(§5). DEVELOPMENT §3 에 트리 개정 순서 몇 줄.
  - D10 **글 범위**: 요청 가이드 한 줄(«다른 서버만 부르고 인터넷에서는 못 부르게 앞단이 막는 창구면 그렇다고») · README · master 문서 · 인수 시험 한 줄(내부 창구도 밖과의 계약 · `/internal/…` 마운트 경계) · broker `internal/` 과 다른 뜻 한 줄 · DEVELOPMENT §7.5 TMPDIR 함정.
  - D11 **기존 `/api/internal/…`** 은 소비자 계약이라 옮기지 않는다(옮기면 계약 변경 — slot 4 · 사용자 승인) · 새 내부 창구는 기존 관례와 달라도 `internal_api`(§2.1 «기존 방식을 따른다» 보다 먼저) · 기존 경로를 빚으로 세지 않는다(기계 밖).
  - D12 **오류 식별자 공유의 받아들인 한계**: 두 scope 가 한 BC 오류 모듈을 쓰면 내부 창구만 쓰는 식별자도 공개 문서 enum 에 보인다(검토자 T 시험 — pydantic 2.14) — 숨기려면 그 concrete 를 `Literal` 로 좁힌다(canon 안 · 새 의무 아님). slot 4 · 8 글 한 줄.
  - 현장 영향(검토자 C 시제품 측정): 현장 positional 은 #429 · #107 · #109 가 사라지고 `[#440] urls.py` 한 줄(한 BC 의 공개 등록 함수에 내부 객체를 넘긴 기존 줄) · 앵커 차분에서는 옛 빚 · 개명 2줄로 갚음. 진행 레인 G2 귀속 34 → 33.

## 3. 규칙 문장(그래프 정본에 넣을 꼴 · 최종 문장은 구현에서)

ninja §2.3 «등록»(새 규범 + R-0707 ~ R-0709 · R-0713 · R-0715 ~ R-0717 개정):
- 앞단(리버스 프록시)이 인터넷에 열지 않는 HTTP 창구는 공개 API 객체와 다른 표준 API 객체 `internal_api`(`<project>/internal_api.py` · `urls_namespace="internal_api"`)에 등록하고, `<project>/urls.py` 가 `path("internal/", internal_api.urls)` 로 단다 — 예: SSE 서버 · 워커가 부르는 창구. 공개 API 아래 경로(`/api/internal/…`)에 새로 두지 않는다(§2.1 의 기존 방식보다 먼저). 이미 `/api/internal/…` 로 배포된 창구는 소비자 계약이라 그대로 둔다(옮기면 계약 변경).
- `internal_api` 는 `<project>/api.py` 의 루트 API 클래스를 들여 짓는다(§6.2) — `internal_api.py` 에는 import 들 · 생성 문장 하나 · 그 객체의 프레임워크 오류 핸들러만 둔다.
- BC 는 내부 창구 컨트롤러를 `register_<bc>_internal_api(api: NinjaExtraAPI)` 로 등록한다 — 공개 창구의 `register_<bc>_api` 와 같은 `api_router.py` 에 두고, 내부 창구만 가진 BC 는 이 함수만 둔다. 컨트롤러 칸은 공개 창구와 같은 기준으로 고른다 — 어느 객체에 다는지는 등록 함수 이름이 정한다. URLconf 는 `register_<bc>_internal_api(internal_api)` 처럼 이름의 scope 에 맞는 객체를 넘긴다.
- registrar 는 project API 모듈(`api.py` · `internal_api.py`)을 import 하지 않는다(R-0713 넓힘).
- 표준 API 객체는 공개 API 객체(`<project>/api.py` — 이름은 프로젝트가 고름)와 `internal_api` 둘뿐이다. 신규 BC 마다 · 기능마다 API 인스턴스를 만드는 것은 scope 분리가 아니다(R-0717).
- 그 밖의 public/internal · version 별 인스턴스가 이미 독립 계약 surface 로 확립돼 소비자가 의존하는 경우는 승인된 별도 scope 로 보존할 수 있다(R-0715 · R-0716 — 보존 경로).
- 내용 없는 `internal_api.py` 는 API surface 가 아니다(inventory · preflight 에서 뺀다).

ninja §4.1 «local development를 제외한 API traffic은 HTTPS를 전제로 한다» 뒤(Q2): 내부 창구(`/internal/…`)는 앞단 안쪽 사설망에서 부르면 http 로 받아도 된다 — 부르는 서버 · 사설망 · 앞단 차단의 근거를 G1 명세(slot 2)에 적는다. 사설망에서 http 로 부르는 프로젝트가 앱의 HTTPS 강제 넘김(`SECURE_SSL_REDIRECT`)을 켰으면 `SECURE_REDIRECT_EXEMPT` 에 `^internal/` 을 둔다. architecture-api §8.3 R-2025 «모든 API 통신에 HTTPS 사용» 은 이 예외를 가리키게 개정한다(필수).

ninja §6.2: «프로젝트에 한 번 두는 파일» 목록에 `internal_api.py` · 611-612 «독립된 public/internal …» 을 D5 로 · slot 4 · 8 에 D12 한 줄. §8 · §9: 내부 창구도 밖(다른 서버)과의 계약 — `/internal/…` 마운트 경계에서 검증. implementation-test:2417 «공개 HTTP 계약» 도 같은 뜻.

houserules: 트리 168행 `internal_api.py` · #429(R-3216) 전제 개정 · R-3217 개정(«celery · 내부 창구 채택은 정본 수준 — 안 쓰는 프로젝트도 빈 파일») · #441 글(«예외는 등록 함수 둘») · broker `internal/` 과 다른 뜻 한 줄.

파이프라인 글(그래프 + Codex 같은 뜻):
- `commands/dddjango.md`: preflight(«한 BC 의 `api_router.py` · `urls.py` 가 두 scope 렌더에 함께 나오는 것은 충돌이 아니다» · «선택 API source 의 instance = 그 파일 안에서 짓는 instance» · 빈 `internal_api.py` 는 inventory 밖) · composition command(«부를 등록 함수 이름은 `--api-module` 파일 이름이 정하고, `--registrar-module` 은 그 scope 에 등록하는 BC 의 `api_router.py` 만») · :190(«182행») · :202(#16 설명) · :217(blind spot).
- architect: «API 스택» 문단(:67 — «외부(다른 프로세스 · 다른 서버 — 내부 창구 포함)» · 등록 함수 둘) · slot 1 · 2(내부 scope 행 · 근거 · 빈 파일 · STOP 범위 · 자기 점검 «slot 1 내부 scope 의 BC 는 `register_<bc>_internal_api`»).
- design-review-api: slot 1 · 2 같은 뜻 · «인증은 일반 규칙(§4.1)만 — 내부 창구라는 이유로 더 요구하지 않는다» · HTTPS 는 §4.1 예외.
- discipline-reviewer :73 · :103 · coder :58 · acceptance-tester(+ Codex) 한 줄.

## 4. 검사기 동작(새 판)

**check-layer-skeleton**: `<project>/` 허용 목록에 `internal_api.py`(메시지 «정해진 개수로 두는 조립 파일») · 없으면 #488.

**check-composition-root 트리 레인**:
- #107: `api_router.py` 공개 함수 ⊆ {`register_<bc>_api`, `register_<bc>_internal_api`}(BC 이름은 모듈 경로의 BC 와 정확히 같음 · 1 ~ 2개 · 각자 인자 하나 `api: NinjaExtraAPI`). #109: 두 함수 모두 정본 등록 함수.
- #437 — 대상은 **진짜 프로젝트 패키지 하나**(layer-skeleton `_find_project_pkg` 처럼 `manage.py` 의 `DJANGO_SETTINGS_MODULE` → settings 폴더 순으로 정함). `_find_project_dirs` 가 잡는 그 밖의 `urls.py` + `api.py` 폴더(R-0715 보존 레거시 등)에는 지금의 #437 규칙만 둔다.
  - `internal_api.py`(새 파일 · 닫힌 허용 목록): import 들 · docstring · 정확히 한 문장 `internal_api[: T] = <정해진 클래스>(…)`(클래스는 `<project>.api` 에서 들임 · `_api_class_names` 집합) · `@internal_api.exception_handler` 함수. 그 밖(클래스 정의 · 별칭 · 튜플 · `type(…)(…)` · 둘째 생성 · 다른 함수 · 식 문장)은 #437.
  - `api.py`(지금 허용 그대로 — 정해진 루트 클래스 하나 · 오류 핸들러 함수 · 그 밖 문장): 더하는 금지만 — 루트 API 생성 문장 둘 이상 · 루트 API 객체 또는 생성자의 별칭 대입 · 튜플 대입 속 생성 · `type(…)(…)` 복사. 공개 객체 이름은 자유.
  - 빈 파일은 내용 규칙을 건너뜀(#488).
- #440(이름 ↔ 넘긴 객체 ↔ mount — 판독 규칙): ① 인자 · `.urls` 주인은 import 출처로 푼다 · 모듈 수준 재대입은 줄 ② 등록 함수 인자는 그 이름 scope 의 표준 객체 하나 — 공개 = `<project>/api.py` 의 그 생성 문장 객체(이름 자유 · 생성 문장이 둘 이상이면 첫 생성 문장 객체 — 나머지는 #437) · 내부 = `<project>.internal_api.internal_api` — 그 밖(framework · 저장소 뿌리 · 셋째 객체 · 다른 표준 객체)은 #440 ③ scope = 모듈 경로의 BC + 정확한 함수 이름 ④ `internal_api.urls` 는 글자 그대로 `"internal/"` 하나에만 · `api.urls` 는 `internal/` 에 두지 않음 · `urlpatterns = [...]` · `.append` · `re_path` 모두 ⑤ 공개 객체 이름 · 주소는 고정하지 않음(«`<project>/api.py` 의 객체 · `internal/` 아닌 주소»). #441 은 등록 함수 둘에 같은 규칙.

**check-composition-root code 레인**: `--api-module` 이 `<project>/internal_api.py` 면 `register_<bc>_internal_api` 를 고름 · 짝 scope 함수 허용 · 루트 클래스 = `_api_class_names` 집합(들인 `<project>/api.py` 를 읽음) · **이름 ↔ 객체 어긋남(scope 이름 함수 없이 짝 함수가 import · 호출 · 다른 표준 객체를 넘김)은 #440 줄** · **고른 모듈이 진짜 프로젝트 패키지의 표준 이름(`api.py` · `internal_api.py`)이고 생성 문장이 정확히 하나가 아니거나 생성자 출처를 못 세우거나 #437 금지 문장(별칭 · 복사)이 있으면 #437 줄(overlap)을 내고 객체 대응 분석만 건너뜀** · **내용 없는 `internal_api.py` 를 `--api-module` 로 고르면 사용 오류(«빈 내부 API 모듈은 scope 가 아니다» — API surface 아님)** · 표준 밖 · 못 읽는 객체만 분석 불능(fail-closed — URLconf 의 모듈 수준 재대입(V3)도 여기: 트리 레인 #440 이 같은 사건을 G2 에 내고, 렌더는 고친 뒤 돈다) · preserve 기준선 모드 짝 검사 풂. 귀속 매핑표 overlap 키(#440 · #437)에 하위 사건 등재(트리 · code 두 줄이 한 사건).

**check-openapi-error-declaration #5 code 레인**: receiver provenance 가 `_api_class_names` 집합의 들인 루트 클래스를 받음 · 표준 이름 모듈에서 생성 출처를 못 세우면 **줄 없이 receiver 분석만 건너뜀**(#437 소유자는 check-composition-root — 사건은 #16 의 #437 이 짐 · monkeypatch · 후처리는 #63 경로 앞 레인의 글자 꼴 판독이 계속 봄).

**check-api-error-controller-contract #15**: one-hop 에서 다른 루트 API 모듈(`<project>/api.py` · `internal_api.py`)을 고르지 않음.

**check-context-isolation #431 · check-usecase-dto-placement · API 표면 판정 덤 경로**: `internal_api.py` · `register_<bc>_internal_api` 도.

**그대로**: registry_gate · anchor_diff · refactor_audit · design_pregate(코드).

새로 막는 것: `internal_api.py` 허용 목록 밖 문장 · `api.py` 의 생성 둘 · 별칭 · 복사(T3 · T3w · T4c · V5 · V6 · V7 · V9 · V10 · V14 · V15 · V18b · T1s) · 이름 · 객체 · mount 어긋남(V1 ~ V4 · V8b · V12 · V16 · T2a · T4a). 새로 푸는 것: 표준 꼴 내부 창구(R1 ~ R4). 렌더 exit 1 은 표준 밖 · 못 읽는 객체(V3 재대입 포함)에만 남음. 기계 밖: `application/**` 안 API 생성 · 기존 `/api/internal/…` · 앞단 차단 · 공개 API 아래 둔 내부 창구(T5 · 리뷰어). 그대로 두는 것: 보존 레거시 `api.py`(진짜 프로젝트 패키지 밖) · `api.py` 의 `if TYPE_CHECKING:` · `__all__` · `logger` · `api.add_router(…)` 같은 지금 허용 문장(G0 소음 0).

꼴별 기대(검토자 C 표 + 고침 · 시제품 P4 측정 — `rv-c/out/p4-*` · `adv-p4/` · `field-p4/` · `matrix-p4.txt`): T1 · T1h · T2b · V11 · V20(공개 객체 이름 `api_v1`) · V21(`api.py` 의 `if TYPE_CHECKING:` · `__all__` · `logger`) = 0 · T1s = #437 · T1n · T2bn = #63 #437(`internal_api.py` 를 `NinjaExtraAPI` 로 바로 지음 — D1 «들여 짓는다» 위반) · T2a = #440(내부 렌더 #107 + #440 · exit 2) · T2an = #63 #437 #440 · T2as = #437 #440(내부 렌더 #107 #437 #440) · V22(`api.py` 공개 객체 별칭) = #437 #440(렌더도 #437 줄) · T3 · T3w · T4c = #437 #440(렌더도 줄) · T4a = #429 #440 · V5 · V10 · V14 · V15 · V18b = #437 · V1 · V2 · V4 · V12 = #440 · V6 · V7 · V9 = #437 #440 · V3 = 트리 #440 · 공개 렌더 exit 1 · 현장 내부 #16 `--anchor` = 0(옛 빚 4) · `api_error_backstop_matrix` 기존 사례 불일치 0(보존 레거시 `legacy/api.py` 6건 포함).

## 5. 시험 · 바뀔 파일

- 시험: 꼴별 기대(§4 끝)를 `api_error_backstop_matrix` · `anchor_diff_smoke` · `field_report_checker_smoke` · layer-skeleton 픽스처 사례로 · 적대 꼴(V1 ~ V19 중 막아야 할 것 전부) · **기존 스모크 계약 뒤집음**: `anchor_diff_smoke` test_R7(«#16 preserve 2.22.2 와 같음» 거둠) · test_reg16(`register_lesson_internal_api` 로 다시 + 잘못 단 이름 → #440 사례) · test_reg05(2.40.0 에서도 실패 — 원인 확인) · 좋은 픽스처 여섯에 빈 `config/internal_api.py`(skeleton good_bc · good_cross · good_grouped · good_promoted · good_promoted_flows · folder_group good).
- 트리 다시 매김: 대응표(168 ~ 182 · «172~182» → «173~183» · 살아 있는 «182행» → «183») · 제외 목록(`workspace/plan/**` · decision-record · LEDGER 기존 행 · 옛 행 수 뜻 «트리 171행 그대로» · spec #609 · 규칙 «#182» · 파일 행 수 «{n}행») · 숫자 참조 손목록(mkrev2 `WHAT` · `NAMES` · `_NMR` · `_st` 오프셋 `mkrev2.py:2229` · `:2248`) · 그래프 글자(TREE 리터럴 · 제목 «182행» · prefLabel R-0338 · R-1683 · R-3112) · 검사기 메시지 하드코딩(`check-layer-skeleton.py:88` · `:907-911` · `check-test-config.py:647`) · 골든(`fixture_matrix.py:753` 등) · 일회 대조 스크립트(살아 있는 «트리 N행»(N≥167) ↔ 새 standard_tree 칸 이름).
- 바뀔 파일 어림 60 ~ 70(일꾼 B §6 + 검토 더함: agent-design-architect API 스택 문단 · architecture-api R-2025 · 픽스처 여섯 · 스모크 둘 · DEVELOPMENT §3 · §7.5).

## 6. 받아들인 한계

- 앞단 차단은 기계 밖(slot 2 근거 · 리뷰어) · 내부 창구 인증 의무 없음(Q1).
- 기존 `/api/internal/…` 은 빚으로 세지 않음(기계 밖) · `application/**` 안 API 생성 · 공개 API 아래 둔 새 내부 창구(T5)는 리뷰어 몫.
- URLconf 의 모듈 수준 재대입(V3)은 scope 렌더 exit 1(빚 불가) — 트리 레인 #440 이 G2 에 같은 사건을 내므로 고친 뒤 렌더한다.
- 오류 식별자 공유 시 내부 식별자가 공개 문서 enum 에 보임(D12).
- 비표준 루트 API 면 렌더마다 프로젝트 전체 #63(D7).
- pre-gate 빈칸(D8) · 트리 «N행» 사람 인용이 진행 레인 명세에서 낡음.
- 채택 프로젝트마다 `internal_api.py` 없음 #488 옛 빚 한 줄(G0 미룰 수 있음 · 리팩토링 «늘 정리»).

## 7. 위험

1. 트리 다시 매김 누락 — §5 대조 스크립트.
2. 들인 루트 클래스 판독 — `_api_class_names` 와 같은 집합 · 못 읽으면 표준 이름 모듈은 #437 줄(exit 1 아님) · 비표준 모듈만 분석 불능.
3. #440 판독이 별칭 · 재대입에서 흔들림 — 출처 풀이 · 재대입은 줄 · 적대 꼴 시험.
4. 귀속 매핑표 overlap 키 등재 누락 시 트리 · code 두 줄이 귀속 둘로 셈.
5. R-0717 은 R-3526 오버라이드 목록에 있음 — 대상은 Norm IRI 라 개정해도 이어짐(검토자 T 확인).
6. `dddjango/scripts` 바뀜 → 진행 레인 pre-gate 재예보.
7. 시험 함정: `TMPDIR` 을 저장소 안에 두면 앵커 차분이 조용히 positional.
