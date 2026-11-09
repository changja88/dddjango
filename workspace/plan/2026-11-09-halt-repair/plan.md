# 현장 보고 수리 1판 — 레인을 멈추는 항목 11개 계획 v3 (dddjango 2.34.0 후보 · 2026-11-09 · 계획 독립 검토 1 · 좁은 재확인 반영)

배포판 2.33.0(태그 `dddjango--v2.33.0` · a4f005ec)으로 재현했다. 묶음 순서(사용자 결정 2026-11-09 «진행하자»): 1 레인 멈춤 → 2 위반을 못 잡음 → 3 소음 · 글 → 4 F4-150 → 5 web. 이 문서는 1판이다. F4-150 은 4판.

판 번호: 2.34.0 — 표준 글이 늘고(입력 확인의 자리 · OHS 사건 값) 새로 막히는 꼴이 생기므로 minor.

## 결정

- 사용자 결정(«나.» 2026-11-09): 빈 값 · 범위 같은 입력 확인은 **입력 스키마 선언으로만** 한다. 컨트롤러의 호출 전 `if` 는 금지 · 응답은 framework 422. 역할 나눔(컨트롤러 = 입력 · 유스케이스 = 말이 되는 요청인지)은 사용자 원칙이다.
- 질문 생략 · 설계 처리 · 이의 시 뒤집음: F4-105 = OHS 입구도 설계에서 승인한 값만 공개 예외로 옮겨도 된다(사용자 «빈도가 이유가 될수는 없어» 뒤, 규칙 목적 대조에서 답이 나옴 — 오류 종류를 늘리지 않고 2026-10-11 결정 «승인 값은 실어도 된다» 와 같다).
- 질문 생략 · 설계 처리 · 이의 시 뒤집음: F4-143 = 리뷰 문구를 «사실 · 도메인 이벤트를 내보내는 유스케이스» 로 좁힌다(스트림 조각 · 바깥 저장소 쓰기는 대상이 아니다). 전달 수단으로 좁히지 않는다 — 자기 포트로 사실을 내보내며 저장 경계를 빼먹는 꼴은 이 리뷰가 유일한 눈이다.

## 항목 · 고침

### 항목 처분 다시 적기 — F4-34 · 55

읽기 대조와 재현은 `if missing:` 을 호출 앞 입력 검사로 세웠지만, 현장 코드는 `readiness = build_<쓰임새>().execute(…)` · `missing = readiness.missing` · `if missing:` 이다. 쓰임새 호출 **뒤** 이고 2.23.1(F4-96) 뒤로 읽혀 #571 로 판정되며 앵커 기존분이다. **F4-34 · 55 의 #15 몫은 이 판의 대상이 아니다.** 호출 앞 입력 검사의 현장 사례는 F4-130 이다. F4-34 · 55 의 #5 별칭 몫은 2.23.1 로 닫혔다.

### 단위 A — 호출 앞 입력 검사 판정(#15)

**«쓰임새 호출» 의 정의**: 호출 사슬의 뿌리 이름이 자기 BC 의 `composition_root` 또는 `application_layer` import 에서 오거나, 그런 호출의 결과로 묶인 이름인 호출. 응용 층 자료 생성(`*Command` · `*Query` · `*Result`)은 세지 않는다. 이 호출이 그 `if` 앞에 없으면 «호출 앞»(쓰임새 호출이 하나도 없는 operation 포함). `_analyze_results` 의 호출 대입 첫 고리도 쓰임새 호출만 받는다. 같은 파일 도움 함수 안에서 쓰임새를 부르는 꼴은 호출 앞으로 나온다(현장 0건 · 받아들임).

| 꼴(호출 앞) | 지금 | 새 판 |
|---|---|---|
| 오류 동작(`Status` 오류 반환 · 오류 Schema · raw 오류 반환)이 있는 가지 — `if not query:` · `if kind == "x":` · 다른 이름 참조 · `match` | exit 1 또는 exit 2 | exit 2 위반. 메시지는 호출 앞 전용 |
| `raise HttpError(400 등)` · 그 밖의 `raise` | exit 1 | exit 2 위반(우회로 막기) |
| `raise HttpError(406 · 415)` | exit 1 | 비켜 줌(§6.3 의 표준 길) |
| 오류 동작이 없는 가지 — `if cursor is None: cursor = ""` · 성공 조기 반환 | `is None` 은 exit 2 오탐 · `not` 은 exit 0 | 통과(`_branch_has_error_behavior` 를 먼저 건다) |
| `page = helper(); if page is None:` + 오류 반환(주어가 쓰임새 호출 결과가 아님) | exit 0 | exit 2 위반(None 길은 쓰임새 호출 결과만) |

호출 **뒤** 는 바꾸지 않는다 — None 길 · exception path · #571 · 호출 뒤 못 읽음 exit 1(`f496-c3 · c4 · c4b · c4c · c5d` 그대로).

메시지(세 갈래): 입력의 모양 · 범위는 입력 Schema(`Field` 제약 · `Query` · `Header` · `Path`) · 로그인과 권한은 framework 인증 틀 · 요청의 뜻 판정은 유스케이스(그 뒤 catch). 호출 앞 위반에는 `constructor not owned` · `Status not owned` 두 줄을 내지 않는다(`allowed_error_calls`) — catch 로 옮기라는 뜻으로 읽힌다.

옛 코드는 앵커 기존분으로 통과한다. 승인된 400 을 고쳐 줄이 달라지면 exit 2 다 — G1 에서 계약 변경(400 → 422) 또는 사용자 승인 빚 목록으로 간다(메시지와 §2.2 에 한 줄).

되돌아옴 막기: `workspace/tools/api_error_backstop_matrix.py` 의 `f496-c5 · c5b · c5c` 를 새 판정으로 뒤집고, C-7 불변식(«옛 출력에 분석 불능 글이 있어야 출력이 바뀐다»)의 예외는 새 픽스처 사례 이름 접두로 건다. 현장 꼴(`query = filters.query.strip()` 뒤 `if not query:`)을 픽스처로.

### 단위 B — F4-105(한 구현자가 끝까지)

승인 표면은 CLI 가 아니라 명세와 코드의 공개 계약이다.

- **G1**: `exception-map` 행에 값 칸을 더한다(`<= 잡는예외 as` 뒤 공백 2+ `값 <필드>`). pre-gate 는 값 칸 없는 `as` 는 지금대로 #474, 값 칸이 있고 published 예외의 symbols 또는 기준선 실물에 같은 이름 필드가 있으면 통과.
- **G2(설정 없이 코드만)**: `except <자기 BC domain_layer 구체 예외 하나> as n:` 의 본문이 `raise <자기 BC contract/exception 클래스>(kw=n.f) [from None]` 한 문장이고, `f` 가 `_exception_class_fields` 의 공개 필드, `kw` 가 그 published 클래스의 선언 필드일 때만 #474 · #153 을 비켜 준다. `str(n)` · 통째 쓰기 · `from n` 은 그대로 위반.
- 필드 대조: `_exception_class_fields` 는 #15 안에 묶여 있어 옮기지 않고, 작은 새 읽기를 `dddjango/scripts/checker_target.py` 에 둔다. `optional`(`str | None`) 필드도 받는다(컨트롤러 규칙을 옮기면 현장 필드가 거절된다). #6 의 `_check_ohs_service` 에 `root` 를 넘긴다.
- 공용 판정 하나를 `dddjango/scripts/checker_target.py` 에 두고 #474(`check-api-error-controller-contract.py`) · #153(`check-context-isolation.py`) 이 함께 쓴다. 프로필 무관(#6 은 프로필을 안 쓴다) · preserve 예외 없음은 컨트롤러 이야기로 남긴다. pre-gate 에 #153 예보는 없다 — 스텁으로 번들 검사기가 돈다.

### 단위 C — 기준선 · #2

| F4 | 재현 | 고침 | 파일 |
|---|---|---|---|
| 59 ① | 재현 | 기준선 재실행만 파일을 가리키는 못 읽음에 버틴다(읽은 진단은 내고 exit 1 로 무너지지 않음 · 지금 쪽 판정 그대로). `anchor_diff.py` 판정 하나를 #15 · #5 가 함께 쓴다. #5 는 첫 못 읽음에서 끊지 않고 모은다 | `anchor_diff.py` · `check-api-error-controller-contract.py` · `check-openapi-error-declaration.py` |
| 40 | 일부(앵커에 BC 는 있고 오류 모듈 파일이 없는 꼴만) | `_skeleton_error_bcs` 가 파일 없음도 골격처럼 걷는다 | `anchor_diff.py` |
| 37 | 재현 | `dddjango-code-json` 에서 고정 경로 common 오류 모듈이 있고 inventory 에 없으면 넣는다(`--project-preserve-error-module` 에 있으면 넣지 않음) | `check-error-centralization.py` |
| 44 | 재현 | `_production_inventory` 에서 작업 트리에 없는 경로를 뺀다(`git_root` 기준 `lexists` · 깨진 링크는 오류 유지) | `check-error-centralization.py` |

단위 A 와 C 가 `check-api-error-controller-contract.py` 를 함께 고치므로 C 의 그 몫(F4-59 ①)은 A 구현자가 맡는다.

### 단위 D — 구조 · 실행 검사기

| F4 | 재현 | 고침 | 파일 |
|---|---|---|---|
| 131 | 재현 | `_cross_bc_port_names` 에서 `__init__` 매개변수 주석과 그 `self.<칸>: <포트> = <매개변수>` 대입 주석 안에서만 쓰인 이름을 **파일마다** 넣지 않는다(다른 어댑터가 상속하면 그대로 #14 · `returns` 로 쓰는 포트도 그대로). 현장 꼴을 픽스처로 | `check-context-isolation.py` |
| 94 | 재현 | #101 에 «자기 `composition_root/event_wiring.py` → 자기 `driving_layer/event_subscription/event_router` 한 쌍» 부칙. `from … import event_router` 꼴까지 `node.names` 로 본다 · 구독 함수 import 는 그대로 #101 | `check-composition-root.py` |
| 62 ① · 138 | 재현 | BC `test/` 직계 `conftest.py` 만 골격 폐쇄에서 면제(트리 행은 안 늘린다). 그 파일의 `autouse=True` 고정물은 막는다(unit 까지 DB 를 켜는 것을 막는 #383 의 목적) | `check-layer-skeleton.py` · `check-test-config.py` |
| 138 추기 | 재현 | e2e 의 `driving_layer.cron_job` import 를 구현 칸에서 뺀다 · #658 안내문의 `test/fake/` 고침 | `check-test-config.py` |
| 137 | 재현 | 마지막 성분만 숨김이고 `.py` 가 아닌 경로는 통과. 숨김 폴더 · 숨김 `.py` · `.dddjango` · `.git` · `.mcp.json` 은 거절 유지 | `design_pregate.py` |
| 157 | 재현(실행 불능 + 옛 앵커를 조용히 쓰는 꼴) | `load_run` 이 `refactor-scope.md` 의 이번 실행 줄에 `build_anchor` 가 있을 때만 앵커를 쓴다. `cmd_draft` 도 같은 판정. 실행 줄이 없는 옛 폴더는 지금처럼 파일을 따르고, 실행 줄의 SHA 와 파일 SHA 가 다르면 실행 불능 | `folder_group.py` |

### 단위 E — 글(graph-owned 는 그래프 → render → 미러 → rulepack)

| F4 | 고침 | 정본 |
|---|---|---|
| 130 | §2.2 — `dddjango-code-json` 표면에서 빈 값 · 범위 같은 입력 확인은 입력 Schema 선언으로 두고 operation 본문의 호출 앞 분기로 오류를 반환하지 않는다(응답은 framework 422 · 승인된 400 을 바꾸는 일은 계약 변경 또는 승인 빚) | `implementation-django-ninja` |
| 130 | 상태 코드 표 — 400 설명을 «잘못된 요청 형식(깨진 JSON 등)» 으로, 422 에 «입력 Schema 검증 실패(framework)» 를 | `architecture-api` |
| 130 | G1 표면 — design-architect slot 6 · 10 과 design-review-api 에 «입력 모양 실패는 입력 Schema → framework 422 · slot 10 에 400 행으로 적지 않는다(blocker)» | `agent-design-architect.ttl` · `agent-design-review-api.ttl` |
| 105 | #474 · #153 · R-3690 · architect 의 «OHS 에는 사건 값 예외가 없다» · exception-map 형식을 승인 필드 허용으로. 검사기 머리글도 같이 | `ontology/rules/` · 트리 명세 #474 · #153 |
| 143 | R-3663 — «사실 · 도메인 이벤트를 내보내는 유스케이스에 저장 경계가 없으면 blocker(스트림 조각 · 바깥 저장소 쓰기는 대상이 아니다)» | `agent-design-review-ddd.ttl` |
| 62 · 138 | R-3125 의 `test/fake/` 를 공용 도움 자리로 보내는 말 고침 · 트리 명세 #384 · #596 · `discipline-houserules` final §1 에 `test/` 직계 `conftest.py` 부칙(트리 행은 안 늘림) | `ontology/rules/` · 트리 명세 · `final.md` |
| 94 | 트리 명세 #101 한 줄 | `workspace/design/2026-08-08-tree-revision-spec.md` |
| 137 | architect 에 숨김 경로 허용 범위 한 줄 | `agent-design-architect.ttl` |

Codex 판은 같은 뜻으로 고친다. 검사기 · 예보기는 byte 동일.

### 단위 F — 묶기(운영자)

시험 파일(`field_report_checker_smoke.py` · `pregate_field_report_smoke.py` · `api_error_backstop_matrix.py` · `fixture_matrix.py`) 행을 모은다. `pregate_symbol_kinds.json` · §3 체크리스트 8 EXPECTED · 그래프 체크리스트 3 ~ 5 · `make rulepack` · Codex 미러 대조 · 봉인.

## 뺀 것

- F4-62 ②(입구 공용 값 칸): 기존 `schema_in.py` 에 두고 다른 쪽이 import 하는 적법한 길이 있어 규칙이 막는 것이 아니다. 칸을 더하려면 트리 개정이다.
- F4-55 기대 ③(pre-gate 가 미리 돌림): pre-gate 는 operation 본문을 못 본다. G1 표면은 단위 E 의 설계 · 리뷰 글로 막는다.

## 받아들이는 한계

- F4-40 의 «강등을 파일 단위로» 와 절차 글은 하지 않는다. 재현된 꼴은 3줄로 닫힌다.
- #5 의 두 번 묶인 별칭 못 읽음(F4-34 잔여)은 다른 꼴이라 이 판 밖.
- 글자까지 같은 호출 앞 검사를 같은 파일에 새로 넣으면 집합 차분의 기존 성질로 가려진다.
- 저장 없이 사실을 내보내는 서비스는 실제 사례가 없어 규칙을 정하지 않는다.
- F4-105: 명세의 값 칸과 코드의 필드가 같은지는 G2 기계 밖이다(감수 몫).
- 쓰임새 호출 알아보기: 뿌리가 import 가 아닌 호출은 `.execute` · `use_case` 낱말이 있는 경로만 쓰임새 호출로 친다. 글자로 뿌리만 보면 입력을 다듬는 `filters.query.strip()` 도 호출로 읽혀 F4-130 이 되살아난다. `self._repo.find()` 뒤 `is None` 은 호출 앞 위반이 되고 현장 0건 · 표준이 막는 꼴이다. `run_it(build_x(), id)` 처럼 빌더를 인자로 넘기는 꼴도 호출 앞으로 나온다(현장 0건).
- `raise HttpError(406|415)` 비켜 주기는 조건을 보지 않는다(글자로 `Accept` 를 가리면 정상 경로를 막을 위험이 더 크다).
- F4-138 추기: `test/e2e/conftest.py` 가 cron_job 입구를 import 하고 시험 파일이 고정물로만 받는 꼴은 #390 한 줄이 남는다 — 시험 파일이 직접 import 하는 꼴이 표준.
- 새로 짓는 입력 확인의 422 본문에는 BC `code` 가 없다. web 의 `safe_api_call` 소비자는 코드로 가를 수 없다(문서 확인 항목).

## 일하는 법

- 구현자 셋이 파일이 겹치지 않게 병렬: 1 = 오류 계약(단위 A · B 의 #474 · #153 · 공용 판정 · C 의 F4-59 · 40 · F4-131), 2 = 나머지 검사기와 예보기(F4-37 · 44 · 94 · 62 · 138 · 137 · 157 · F4-105 pre-gate), 3 = 글(단위 E). 시험 파일은 구현자별로 나눠 맡는다. 코덱스 byte 미러 · 기대 파일 · rulepack · 봉인은 운영자가 F 에서 묶는다. 그래프 글은 3 이 모아 고치고 `ontology_render.py --apply` 는 끝에 한 번.
- 되돌아옴 막기: 항목마다 픽스처 · 스모크(옛 판 붉음 → 새 판 녹색). 재현 장난감을 옛 판 · 새 판에 나란히.
- 구현 독립 검토 한 번(과적합 · 다른 규칙과 모순 · 새 오탐 · 커밋 뒤에도 같은가) → 지적 재현 → 처분.
- 검사: `make rulepack` · `make verify` · `make verify-mutation`. 봉인은 커밋 직전 · 배포 뒤 chore.
- 문서: 입력 확인의 자리는 사용자에게 보이는 규칙이므로 README · `docs/` · 요청 가이드에 닿는지 확인해 보고.
- 장부를 읽은 때의 마지막 = F4-157(2026-11-09 16:20 판) · 구현 중 새 항목 F4-158 · 159(2026-11-09 23:35 판 · Django admin 입구의 자리) — 이 판에 넣지 않고 다음 판 후보 · 배포 직전에 다시 읽음.

## 멈출 기준

- 구현 독립 검토 차단이 셋째 좁은 확인에도 안 닫히면 멈추고 묻는다.
- `make verify` 붉음이 이 판 밖 원인이면 멈추고 알린다.

## 계획 독립 검토 처분

- 검토 1: 차단 3 · 중요 11 · 사소 9 — 모두 받아 v2 에 반영. 지적을 운영자가 로그와 현장 코드로 확인했다.
- 좁은 재확인: 차단 1 · 2 · 3 닫힘 · 중요 4 · 5 · 6 · 7 · 10 닫힘 또는 조건 처분 · 새 문제 N1 ~ N6 모두 v3 에 반영(N4 는 앞 검토 권고를 뒤집어 `raise AuthenticationError` 비켜 주기를 뺐다).

## 구현 독립 검토 1 처분

차단 1 · 중요 4 · 사소 8.
- B1(픽스처가 빈 폴더에 기대 커밋 뒤 붉음) — `__init__.py` 넣음.
- M1(pre-gate 와 G2 가 값 칸에 다른 답) — pre-gate 가 G2 와 같은 필드 대조를 쓴다 · 값 칸은 published 필드 이름 · 글 맞춤 · G2 메시지에 통과 조건.
- M2(빌더) · M3(import 뿌리가 아닌 쓰임새 호출) · M4(반복문 · with 안의 호출 앞) — 판정 고침 · 픽스처.
- 좁은 재확인 1: B1 · M1 ~ M4 닫힘 · 새 문제 N1(`__init__` 행으로 선언한 published 예외를 G1 이 막음 — 고침) · N2(한계로 적음).
- S1 · S3 · S4 · S5 · S6 · S7 받음(S7: `.env` 실파일은 거절 유지 · 견본 이름만 허용). S2 는 위 한계. S8 은 계획 낱말 고침 · 변이는 더하지 않음(옛 판 붉음을 확인한 시험이 있다).
