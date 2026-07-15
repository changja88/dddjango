# ErrorOut 중앙화 구현 계획

**상태:** 구현·최종 적대 리뷰·재검증 완료

**기준:** 전체 기능 리뷰 `9d86cf7`, 구현 금지 surface 감사 `6caa0da`

## 목표

Django Ninja의 공통 Problem Details envelope인 `ErrorOut`을 같은 HTTP 계약 scope에서 한 번만 정의한다. architect가 재사용·로컬 확장 결정을 명세하고, coder가 구현 직전 현재 프로젝트의 common과 기존 canonical 경로를 다시 검색하며, 불일치가 있으면 임의로 새 BC Schema를 만들지 않고 Coordinator의 G1′로 돌려보낸다.

## 범위

- 수정 대상은 실제 플러그인 정본 `dddjango/`, Codex 의미 미러 `codex-dddjango/`, 세 canonical reference의 source mirror, 사용자 설명 문서다.
- 외부 runtime/live 실행, 로그인, 임시 Python 환경, 대량 Django fixture·prompt matrix는 만들거나 실행하지 않는다.
- 신규 checker·검사 로직·게이트 수, manifest version, `workspace/eval`, release는 변경하지 않는다. 기존 `check-common-container`의 진단 문구만 첫-BC `ErrorOut` 예외와 정합화한다.
- 검증은 정적 RED 증거, corpus mirror, Claude/Codex 의미 anchor, plugin 구조 검증, 전체 diff 검토와 세 축의 fresh-context 적대 리뷰로 제한한다.

## 계약 결정

1. 중앙화 단위는 `API instance/namespace + public/internal + version + core problem profile`로 식별한 contract scope다.
2. 같은 API/namespace/version/core profile은 같은 scope로 추정한다. problem-specific extension 차이만으로 scope를 나누지 않는다.
3. 신규 단일-scope dddjango 표준 표면은 첫 BC부터 `<root>/common/ninja/response/error_out.py::ErrorOut`을 사용한다. 독립 scope를 둘 이상 새로 도입하면 namespace/version/profile fallback 경로로 충돌을 피한다.
4. brownfield에 이미 공용 또는 공개 경로가 있으면 이동·별칭을 발명하지 않고 그 경로를 canonical로 보존한다.
5. 공통 base는 `type`, `title`, `status`, `detail`, `instance` core만 소유한다.
6. BC 로컬 Schema는 `InventoryConflictErrorOut(ErrorOut)`처럼 실제 wire extension을 가진 concrete response일 때만 허용한다. core 재선언, 이름만 다른 base, arbitrary extension bag은 금지한다. wire alias가 있으면 concrete `response=`와 operation `by_alias=True`를 한 계약으로 기록한다.
7. BC-specific exception→status/type/title/detail/extension 값 mapping은 계속 BC presentation이 소유한다.
8. generic serializer·recognizer·framework handler는 실제 공유가 생길 때만 common으로 승격한다. Schema의 birth-common 규칙과 별개다.
9. DRF, plain Django view, server-rendered HTML은 Ninja `ErrorOut`으로 강제 이주하지 않는다.

## 책임 배치

| 역할 | 책임 |
|---|---|
| design-architect | 11-slot Error response 결정을 명세하고 scope·기존 경로·base·local concrete·response·compatibility 근거를 남긴다. |
| design-review-api | required/default/nullable/alias/extension wire 의미와 concrete OpenAPI response를 검토한다. 파일 배치·DRY는 재판정하지 않는다. |
| acceptance-tester | 실제 core-only status가 있으면 대표 하나를, 없으면 대표 extension-bearing status의 상속 core+extension을 runtime/OpenAPI exact assertion으로 Red 증명한다. 새 status를 발명하거나 내부 helper 존재를 검사하지 않는다. |
| coder | 생성 전 현재 tree의 common/local/controller/helper/import를 재검색하고, 승인 명세와 tree가 다르면 로컬 Schema를 만들지 않은 채 구조화된 handoff를 반환한다. |
| discipline-reviewer | 같은 scope의 core 복제, 승인되지 않은 로컬 Schema, base 미상속, 계층 역의존 같은 구조·DRY 위반만 감사한다. API 계약 의미는 재판정하지 않는다. |
| Coordinator | G1 전후에 11-slot 완전성을 확인하고, stale-spec·duplicate blocker를 G1′로 반송하며, 실제 Green과 불일치 해소 전에는 G2를 열지 않는다. |

## 구현 작업

### 1. 정본 계약과 미러

- [x] `discipline-houserules`에 common `ErrorOut` 표준 경로, brownfield 예외, local concrete extension 규칙을 반영한다.
- [x] `implementation-django-ninja`의 로컬 `ProblemOut` 예제를 공통 `ErrorOut` import와 concrete extension 예제로 교체한다.
- [x] `implementation-test`에 core/extension runtime·OpenAPI exact assertion과 실제 Red/Green 증거 규칙을 추가한다.
- [x] 정본을 먼저 수정하고 `corpus_mirror_sync.py --write`로 source mirror와 Codex reference를 갱신한다.

### 2. 역할 프롬프트와 게이트

- [x] architect와 API reviewer에 11-slot 계약 결정과 각자 판정 범위를 배선한다.
- [x] acceptance-tester에 core-only/extension 외부 계약 Red 책임을 배선한다.
- [x] coder에 생성 전 검색과 stale-spec handoff를 배선한다.
- [x] discipline-reviewer에 구조/DRY blocker와 brownfield·다른 표면 false-positive guard를 배선한다.
- [x] Coordinator에 G1 재검사, G1′ 반송, G2 차단 조건을 배선한다.
- [x] Claude와 Codex 역할 프롬프트를 의미상 동일하게 갱신한다.

### 3. 사용자·저장소 문서

- [x] README 표준 tree와 설명을 common base/local concrete 규칙에 맞춘다.
- [x] AGENTS의 reference 정본·미러 설명을 실제 동기 도구 방향과 맞춘다.
- [x] live/login/venv/fixture 절차를 계획에서 제거한다.

### 4. 검증과 독립 리뷰

- [x] 변경 전 canonical path·11-slot·coder preflight·reviewer blocker·Coordinator gate anchor가 없음을 정적으로 확인한다.
- [x] `claude plugin validate dddjango --strict`와 Codex manifest JSON 검증을 통과한다.
- [x] corpus 11종의 workspace source body↔Claude body와 Claude↔Codex whole-file exact mirror를 확인한다.
- [x] 신규 checker·검사 로직·게이트 수와 manifest·eval이 불변이고, 기존 checker의 진단 문구 외 변경 및 임시 verification/venv가 없음을 확인한다.
- [x] 계약·책임 소유 관점의 fresh-context 적대 리뷰를 통과한다.
- [x] 코퍼스·자기모순 관점의 fresh-context 적대 리뷰를 통과한다.
- [x] 실효성·과적합 관점의 fresh-context 적대 리뷰를 통과한다.
- [x] 리뷰 수정 후 전체 검증을 새로 실행하고 최종 diff를 확인한다.

## 최종 합격 조건

- 같은 scope의 신규 core envelope는 한 canonical `ErrorOut`만 가진다.
- coder가 current-tree search 없이 BC-local core Schema를 만들 수 없도록 프롬프트에 명시돼 있다.
- local concrete extension의 필요성·wire 계약·`response=` 선언이 설계 명세에서 추적된다.
- stale spec이나 duplicate blocker가 있으면 Coordinator가 G2 대신 G1′를 선택한다.
- brownfield 경로, 실제 profile 차이, DRF/plain/server-rendered 표면을 오탐으로 중앙화하지 않는다.
- Claude/Codex 런타임 프롬프트와 세 reference mirror가 서로 모순되지 않는다.
- 외부 로그인·live 실행·임시 dependency 환경·대량 fixture 산출물이 없다.
