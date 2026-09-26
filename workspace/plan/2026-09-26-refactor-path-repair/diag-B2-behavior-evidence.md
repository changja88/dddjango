# 진단 B2 — 백로그 2 «리팩터 동작 보존 증거» 설계 초안 (2026-09-26 · 미검토)

출처: `workspace/plan/2026-09-26-refactor-campaign/plugin-improvement-backlog.md` 2순위 · `review-R3-risk.md:85-132`(F4) ·
`review-R1-strategy.md:202-217`(M7) · `goals.md:54`(성공 기준 3) · `plan-v2.md:44-45·63-65`. 상태 = 설계 초안(적대 검토 전).
인용 약칭: `cmd` = `dddjango/commands/dddjango.md`, `coder`·`dr`·`at`·`arch` = `dddjango/agents/{coder,discipline-reviewer,acceptance-tester,design-architect}.md`.

## 0. 요지

- 지금 G2 는 **체크 위반 집합의 차분**(registry_gate)과 **테스트 실행 결과**만 기계로 잰다. 슬라이스 0 이 «동작 불변»이라는 주장은
  G1 기록(`cmd:91`)·역할 보고(`cmd:110`)·감수자의 hunk 대조(`dr:58`)라는 **LLM 판단**에만 기대고, 같은 레인이 테스트까지 고친다(R3 F4).
- 제안: 새 스크립트 `behavior_guard.py`(가칭)가 **리팩터 창**(슬라이스 0 시작 직전 ~ 끝) 양 끝에서 다섯 표면을 떠서 비교한다 —
  보호 테스트 blob · 마이그레이션(파일 집합 + `makemigrations --check`) · OpenAPI(wire 층) · OHS/published_event 공개 표면 · URL 목록(admin 포함).
- 실측으로 발견한 설계 제약 둘: ① ninja_extra `@api_controller` 는 기본값이 `use_unique_op_id=True` 라 operationId 에 **프로세스마다 난수 접미**가 붙는다 —
  OpenAPI 원문 diff 는 **항상 ≠0**이다. ② Ninja Router 의 operationId 는 «모듈 경로 + 함수명»이라 **파일 이동(#490)만으로 바뀐다**.
  → OpenAPI 는 wire 층(W: red)과 문서 층(D: 보고)으로 나눠야 한다(§2.3).

## 1. 현재 상태 — G2 가 이미 모으는 것

| G2 증거 | 위치 | 동작 보존에 대한 의미 |
|---|---|---|
| registry 27종 판정 차분(귀속 0 + legacy 보고) | `cmd:114`, `registry_gate.py:1-15` | 규칙 위반 증감만 본다 — 동작 무관 |
| 관련 테스트 + 전체 suite(Coordinator 실행 · 기준선 대비 관련/무관) | `cmd:111` | 유일한 동작 오라클. 단 그 테스트를 같은 레인이 편집할 수 있다 |
| 입장 표 decision·test diff hunk 대조 · `retain` 무편집 · 의미 보존 재조직 «전후 보호» | `cmd:104·108`, `dr:54·58`, `coder:32` | LLM 감사. 기계 비교 없음 |
| 역할 보고 `path::test | … | 변경 후 현행 보장 위치` — «별도 장부·snapshot 금지» | `cmd:110` | 보고 형식만 |
| Error-contract scope 의 mounted OpenAPI 검증(입장된 operation/status 만) | `cmd:165`, `at:45`(전체 문서 snapshot 금지) | 오류 scope·입장 행 한정 |
| 범위 밖 편집 `git status --porcelain` 대조 | `cmd:161` | 6′ 루프(`DJR_LOOP_ENABLED=on`)에서만 · 경로 범위만 |

불변식별 판정:

| 불변식(backlog 2) | 판정 | 근거 |
|---|---|---|
| e2e 테스트 무편집 · 편집 필요 시 STOP | **부분(LLM)** | `dr:58` hunk 대조·`coder:73` 외부 계약 테스트 임의 수정 금지. 기계 비교 0 · STOP 규칙 없음 |
| OpenAPI JSON diff 0 | **부분(오류 scope 한정)** | `cmd:165`·`at:45` 는 입장 행만. registry #5 는 선언 형태 정적 검사(`cmd:127`) — 문서 비교 아님 |
| `makemigrations --check` 무변 | **부분** | registry #1 = `migrations/` 생성물 모양 순수성(`cmd:123`)만 · Phase 3 는 «실행했으면 보고»(`cmd:174`) — 창 전후 비교 없음 |
| OHS 공개 경로·심볼 diff 0 | **부분(구조만)** | registry #6 = OHS 구조 #146~#171(`cmd:128`) · OHS 수정 시 소비자 테스트 포함(`coder:46`) — 표면 비교 없음 |
| admin URL diff 0 | **없음** | registry #26 은 admin «자리» 명명만(`cmd:148`) |
| 약한 단언 강화 선행 허용 | **없음·규범 충돌** | `add/update` 는 Red 선행(`coder:32`) · 특성화 결과의 영구 고정 금지(`discipline-cleancode/references/final.md:2469`) |

## 2. 측정 설계 (범용 Django 프로젝트 기준)

### 2.0 공통 — 리팩터 창 · 캡처 · 판정

- **창**: 슬라이스 0(ⓐ 빚 슬라이스 — `cmd:80·105`)은 신규 슬라이스보다 앞이므로 연속 구간이다. **열기** = 첫 리팩터 슬라이스의 coder 파견 직전
  (acceptance-tester 산출 뒤 — 그 Red 파일이 창 diff 에 섞이지 않게). **닫기** = 마지막 리팩터 슬라이스 coder 보고(+해당 경량 감사 반영) 수신 뒤,
  첫 비리팩터 슬라이스 파견 전. 순수 리팩터 레인이면 닫기 = G2 직전(6번 직전).
- **캡처 주체 = Coordinator**(앵커와 같은 이유 — 실행자가 기준을 고르지 못하게, `cmd:114`). coder 는 측정하지 않는다.
- **정적 스냅숏**: 임시 인덱스(`GIT_INDEX_FILE`)로 tracked + untracked non-ignored 를 tree 객체로 쓴다(HEAD·인덱스·이력 무변). open/close tree SHA 를
  기록 → 정적 비교(§2.1·2.2(i)·2.4)는 감사자가 언제든 재계산 가능. `git archive` 스냅숏(`anchor_diff.py:97`)은 `.env` 등이 빠져 런타임 probe 에 못 쓴다.
- **런타임 probe**: 프로젝트 인터프리터로 `django.setup()` 한 1 프로세스가 §2.2(ii)·2.3·2.5 를 한꺼번에 뜬다. 입력 `--python`·`--settings` 는
  Phase 2 step 1 이 감지한 값(`cmd:103`)·전체 suite 실행 인터프리터(`cmd:111`)를 그대로 쓰고 open 에 고정 — close 에서 다르면 exit 1.
- **판정 exit**: 0 = 불변(D 층 보고는 exit 무관) · 2 = 불변식 diff · 4 = 일부 미측정(사유 병기) · 1 = 사용 오류·open 캡처 부재·재료 결손.
  사용자 승인 diff 는 `--accepted-file`(항목 ID + 사용자 원문 인용)로 exit 에서 빼고 «승인 diff» 절로 보고(legacy-debt 채널과 같은 꼴).
- **red 처방**: 1차 = 원인 편집의 철회(houserules §1 «스코프 밖 귀속 = 철회»와 같은 결), 철회로 진행 불가면 `STOP_FOR_USER_APPROVAL`. 미측정(4)도 STOP — 조용한 green 금지.

### 2.1 보호 테스트 무편집

- 보호 집합 P = 표준 자리 `application/*/test/e2e/**`(#390) ∪ G0 스코프 메모의 «동결 테스트 경로» 줄(사용자 제약 — 예 spring_dream `tests/web/**`). open 에 고정.
- 측정: open/close tree 에서 P 매칭 경로 → blob 맵 비교. 수정·추가·삭제·이동 전부 Δ. 판정 = Δ0.
- coder 규칙: 리팩터 슬라이스에서 P 편집이 필요하면 편집하지 않고 STOP(사후 검출 전에 사전 정지).
- 오탐 아님(진짜 충돌): e2e 가 factories 나 구현을 import 하는 경우 이동(#490·#383~#392)이 e2e 편집을 강제한다 — #390 빚 자체가 e2e 파일에 산다. → §5 완전판 G0 예측.
- P 가 비면 green 이 아니라 **«보호막 0» 경고**를 배너에 올린다(R3 F4 표: rag_service_library·fortune_intent 등 e2e 0).

### 2.2 마이그레이션 무변

- (i) 정적: `**/migrations/*.py` 경로·blob 집합 Δ0 — 창 안 migration 생성 = red(`plan-v2.md:65` 중단 조건 iii 와 정합).
- (ii) 런타임: `manage.py makemigrations --check --dry-run` 의 (exit, 정규화 stdout) 가 open = close. «무변»이지 «exit 0» 이 아니다 —
  brownfield 에 모델-마이그레이션 불일치가 상존해 open 이 이미 exit 1 이어도 같으면 불변.
- 정규화: 자동 이름의 날짜(`auto_\d{8}_\d{4}`) 치환 · stderr(DB 미접속 시 history 경고) 제외.
- 잡는 것: 모델 클래스를 `models` 가 import 하지 않는 자리로 옮겨 등록이 빠짐(DeleteModel) · 앱 경계 이동 · `db_table`(#630)·모델 개명(#632) 수리 — 뒤 둘은 본질적으로 계약 변경이라 STOP 이 맞다.
- 해당 없음: `manage.py` 부재 → 미측정(4).

### 2.3 OpenAPI — W 층(red) / D 층(보고)

- API 발견: ROOT_URLCONF resolver 전 패턴을 걸어 callback 이 `partial(…, api=NinjaAPI)` 인 것을 `urls_namespace` 로 모은다
  (ninja 자신의 `export_openapi_schema` 가 `resolve("/api/").func.keywords["api"]` 로 찾는 원리 — spring_dream venv django-ninja 1.6.3 `export_openapi_schema.py:32`).
  문서 = `api.get_openapi_schema()`(같은 명령 `:85`). 게이트 probe 는 영구 테스트가 아니므로 `at:45` 의 «전체 문서 snapshot 금지»(영구 artifact 규범)와 충돌하지 않는다 — 규범 문면에 이 구분을 명시한다.
- **W 층**(wire): path×method 별 parameters(name·in·required·스키마) · requestBody(media·스키마) · responses(status·media·스키마) · security.
  `$ref` 인라인 해소 · `title` 제거 · `required` 정렬 · 키 정렬. Δ ≠ 0 = red.
- **D 층**(문서): operationId · components 이름 · summary/description/tags · info. Δ = 보고 + 감수자 입력.
- D 로 내리는 근거(실측, spring_dream venv 읽기 전용):
  ninja_extra 0.31.7 `controllers/base.py:414·643-648` — `use_unique_op_id: bool = True` 기본, `operation_id += f"_{uuid4().hex[:8]}"` → 프로세스마다 난수.
  이 저장소는 `@api_controller` 17 파일·설정 없음 → 원문 diff 는 항상 ≠0. `at:50` 도 이 난수를 인지한다.
  django-ninja `main.py:583-586` — Router operationId = `(module + "_" + name)` → 파일 이동만으로 변함. `openapi/schema.py:207` — `title = model.__name__` → Schema 개명만으로 변함.
- 잡는 것: #647 수리가 Ninja Schema 필드 주석을 `dict[str, Any]` → 구체형으로 바꾸면 **요청 검증 동작(wire)이 바뀐다** — K1 타입 빚(94건)의 실제 위험.
- 해당 없음: Ninja API 0 → «해당 없음(Ninja 0)». DRF 등은 완전판 어댑터. 설정 의존(prod 에서 `openapi_url=None` 등) — probe 설정 기준임을 배너에 병기.

### 2.4 OHS 공개 표면

- 대상: 창에서 바뀐 파일이 속한 BC 의 `driving_layer/open_host_service/**/*.py` · `published_event/**/*.py`(타 BC 가 부를 수 있는 둘 — `check-context-isolation.py:14`). 입력 불요(자동).
- 추출(정적 AST, tree blob): 모듈 경로 → 공개 이름(`__all__` 우선, 없으면 밑줄 제외) → 종류·시그니처(def: 인자 이름·종류·기본값 유무·주석 `ast.dump`·반환;
  class: 기반·공개 메서드 시그니처·클래스 수준 주석 필드와 기본값 유무; 재수출은 대상 경로).
- 판정: 제거·변경 = red, 추가 = 보고(#488 골격의 빈 모듈 등). 무주석 → 주석 신설(#493)은 «추가»로 분류.
- 오탐: `Optional[X]` ↔ `X | None` 같은 표기 동치는 `ast.dump` 가 변경으로 본다 → STOP 에서 사용자 판정(완전판에서 동치 정규화).
- 해당 없음: 두 자리 모두 없는 BC.

### 2.5 URL 목록 (admin 포함 — backlog 의 «admin URL» 을 일반화)

- 측정: `get_resolver()` 재귀 → (결합 route 문자열, `namespace:name`) 정렬 목록. callback 모듈 경로는 제외(이동만으로 바뀜). admin = namespace `admin` 부분집합.
- 잡는 것: admin 모듈을 표준 칸 `django_<bc>/admin/`(houserules `final.md:126`)으로 옮긴 뒤 패키지 `__init__` 이 하위 모듈을 import 하지 않아 **등록이 조용히 빠지는** 경우 ·
  dddjango-web 서버렌더 라우트(OpenAPI 밖).
- 판정: Δ ≠ 0 = red. Ninja URL name 은 view 함수명이라 개명 시 변함 — `reverse()` 소비가 있을 수 있어 red 유지(STOP 에서 판정).
- 해당 없음: admin 미설치 → admin 부분만 «해당 없음», URL 목록은 항상 측정.

### 2.6 약한 단언 강화 선행

- 형태: 창 **열기 전** «보호 강화 슬라이스»(acceptance-tester 소유 `update`) — 예 `"gender" in body["missing"]` → 정확 비교(R3 F4 `decisive_fortune … :287-288`).
  보호 집합 기준선은 이 슬라이스 **뒤**에 찍는다 → 창 안 무편집 불변식은 그대로.
- 충돌: `update` 는 Red 선행(`coder:32`·`at` 동형)인데 강화는 현행 코드에서 green 이다 · 특성화 결과의 영구 고정 금지(`cleancode final.md:2469`).
  성립 조건 = «강화 대상이 명세에 기재된 **승인 현행 계약**» + Red 대신 «앵커 production 에서 green» 증거. 입장 규범 개정이 필요하다 → Q3.

## 3. 소속 — 스크립트 · 역할 · 절 · 미러

- **새 스크립트**(registry_gate 확장 아님): registry_gate 는 «체크 위반 집합 N∖L» 전용 정적 게이트이고 pre-gate 도 같은 판정기를 쓴다(`cmd:79`).
  Django 런타임 probe 를 섞으면 그 계약이 흐려진다. 새 check-* 도 아니다(registry 27종·rulepack·pre-gate 로스터 무변).
  - `dddjango/scripts/behavior_guard.py` — stdlib. `capture <root> --at open|close --out <폴더>/behavior [--python --settings --protect <glob>…]` · `compare … [--accepted-file]`.
    git 헬퍼는 `anchor_diff.py`(`run_git`·`is_git_worktree` — `:67·72`) 재사용.
  - `dddjango/scripts/behavior_probe.py` — 프로젝트 인터프리터가 실행하는 Django 의존 probe(§2.2 ii·2.3·2.5). 플러그인 모듈 import 0.
  - 산출: `<산출물 폴더>/behavior/{open,close}.json` · `report.md`(마지막 줄 `요약:` — 배너 행의 기계 출처).
- **역할**: Coordinator = 캡처·비교·배너(유일한 실행자) · coder = 보호 목록 입력 + P 편집 필요 시 STOP · discipline-reviewer = `report.md` 입력(D 층 diff·«창 이후 재편집»
  hunk 를 의미 보존 관점으로 감사 — ⓓ 후보 동봉과 같은 자리 `cmd:108`) · acceptance-tester = 완전판(§2.6)만.
- **바뀌는 절**(전부 graph-owned → `ontology/rules/*.ttl` 정본 수정 · ISSUED 채번 · `ontology_render.py --apply` · `make rulepack`):

| 정본(doc_key) | 투영 위치 | 변경 |
|---|---|---|
| `command-dddjango` | 산출물 위치(`cmd:14-30`) | `behavior/` 추가 · `cmd:110` «snapshot 금지»는 역할 보고 한정이고 게이트 증거는 대상 아님을 명시 |
| 〃 | Phase 2 step 3(`cmd:105`) | 리팩터 창 정의 · open 캡처 시점 |
| 〃 | step 4(`cmd:106`) | coder 입력에 보호 목록 · 창 닫기 시점 |
| 〃 | step 5(`cmd:108`) | 감사 입력에 `report.md` |
| 〃 | step 6 새 하위 항목(`cmd:114` 뒤) | `compare` 실행·종료 계약(§2.0 exit) · 창 이후 재편집 집계 |
| 〃 | step 7 G2 배너(`cmd:165`) | 배너 1행(아래) + 제시 금지 조건: open 부재 · 미승인 W/Δ · 미승인 미측정 |
| 〃 | 수정 모드(`cmd:187`) · 엣지 · Phase 3(`cmd:174`) | 슬라이스 0 있으면 같은 절차 · 보고 1행 |
| `agent-coder` | 입력(`coder:22-27`) · 경계(`coder:73`) | 보호 목록 · 리팩터 슬라이스 P 편집 필요 → `STOP_FOR_USER_APPROVAL` |
| `agent-discipline-reviewer` | 입력(`dr:21`) · 입장 감사(`dr:58`) | report 입력 · D 층/재편집 감사 |

  배너 행 판형(안): `동작 보존(창 S0~Sk): 보호테스트 Δ0(P n파일) · migrations Δ0/--check 동일 · OpenAPI W Δ0 (D n 보고) · OHS Δ0 (+m) · URL Δ0 · 미측정 0 · 창 이후 재편집 r파일`.
- **Codex 미러**: 의미 미러 `codex-dddjango/skills/dddjango/SKILL.md`(산출물 `:68` · Phase 2 `:122·123·125·131` · G2 `:182` · 수정 모드 `:192-198`) ·
  `dddjango-coder/SKILL.md`(`:14·61`) · `dddjango-discipline-reviewer/SKILL.md`(`:14·47`). 스크립트 2종은 byte 미러(`Makefile:171` `diff -rq`).
- **부속**: 봉인 글롭 추가·재발행(`workspace/tools/manifest_seal.py:74-79`) · `workspace/tools/behavior_guard_smoke.py` + verify 등재(`Makefile:183` 옆 — 런타임 부분은
  메인테이너 `.venv` 에 Django 미설치면 skip 을 **명시 출력**) · 캠페인 발주 판형의 «G2 추가 증거» 줄(`plan-v2.md:45`)은 플러그인 소유로 넘어가 삭제 대상.

## 4. 적용 범위

- **규칙(권장)**: 리팩터 슬라이스(ⓐ)가 1개 이상인 **모든 레인**에 창 단위로 적용한다. 판정 대상은 창 안 변경뿐이다.
  - 근거: B1 방침(«예외 없이 항상 정리» — `plan-v2.md:101`) 이후 서비스 레인 거의 전부에 슬라이스 0 이 생긴다. «동작 불변» 주장은 레인 종류와 무관하게 같다.
  - 같은 레인의 비리팩터 슬라이스는 창 밖이라 불변식을 받지 않는다 — 기존 G2 증거(입장 표·acceptance Red·입장된 mounted OpenAPI)가 그대로 소유한다.
  - 순수 리팩터 레인(K1·K2)은 창 = Phase 2 전체라 닫기 = G2 직전.
- **창 이후 재편집**: 비리팩터 슬라이스 파견 뒤에는 close 재캡처 불가. 이후 창 변경 파일이 다시 편집되면(홀리스틱 감사 반송 등) `compare` 가 G2 시점에
  «close→현재 변경 ∩ 창 변경 파일»을 집계해 배너·감수자에게 넘긴다(기계 보증 밖임을 정직 표기). G2 거부 뒤 재작업은 비리팩터 파견 전이면 창 연장(close 재캡처)이다.
- 수정 모드: 백로그 1(R1 결정 — 수정 모드 G0 에도 빚 스캔)이 슬라이스 0 을 만들면 같은 규칙.

## 5. 최소판 vs 완전판

| | 최소판(MVP) | 완전판 |
|---|---|---|
| 불변식 | §2.1~2.5 전부 · D 층 보고 · `--accepted-file` · 미측정 = STOP | + §2.6 보호 강화 슬라이스 · OHS 표기 동치 정규화 · BC 밖 참조 해석(저장소 전체에서 `application.<bc>` 로 향하는 import 가 close 트리에서 해석되는가 — seed·web 테스트·factories·타 BC ACL, `plan-v2.md:44` 동결 목록을 직접 지킴) · DRF(drf-spectacular) 어댑터 |
| G0 | 변경 없음 | ⓐ 항목 경로가 P·OHS·migrations 에 닿거나 규칙이 #630·#632 면 «불변식 충돌 예상» 표시(백로그 1 의 `refactor-scope.md` 에 합류) → 사전 분리·승인 |
| 규범 | ttl 3종(command·coder·discipline-reviewer) | + acceptance-tester · design-architect · discipline-tdd(입장 규범) |
| 비용 | 스크립트 2종 1.5~2.5일 · smoke 0.5~1일 · 규범/렌더/미러 1일 · 행동 시험 0.5~1일 → **약 4~5일**(리뷰 루프 포함) | +3~5일 |

- 단계 분할 선택지: MVP-a 정적만(§2.1 · 2.2 i · 2.4, 환경 위험 0, 약 2일) → MVP-b 런타임(§2.2 ii · 2.3 · 2.5). 권장은 **한 릴리즈로 함께** —
  K1 의 주 위험(Schema 주석 수리 → 요청 검증 변화)은 W 층만 잡는다. 런타임 실패는 미측정 STOP 으로 떨어지므로 레인을 조용히 통과시키지 않는다.
- 위험:
  1. 런타임 환경 취약성 — import 시점 DB 질의·`.env`·설정 차이로 probe 실패 → 미측정 STOP 증가(사용자 게이트 비용). 파일럿 1 레인으로 빈도 실측 필요.
  2. 오탐 STOP 팽창 — W/D 분리로 대부분 흡수. 남는 것: OHS 표기 동치 · Ninja URL name 개명.
  3. Coordinator 프롬프트 부하(이미 210행 고밀도) — 스크립트 호출 2회 + 배너 1행으로 좁혀 준수 부담 최소화. open 부재 시 `compare` exit 1 → G2 금지(pre-gate `--check-report` 와 같은 관측형 집행).
  4. 오라클 독립성은 완전해지지 않는다 — 창 이후 재편집·D 층 판정은 여전히 LLM. 정직 표기가 대책이다.
  5. 릴리즈 창 제약(백로그 운영 제약) — 8-B-5 구현 단계 중에는 배포 불가.
- 알려진 사각(측정 밖): celery task 이름(모듈 경로 파생)·DB 저장 beat 스케줄 · cache/session 의 pickle 클래스 경로 · settings 점 문자열(`INSTALLED_APPS` 등 —
  `django.setup()` 성공으로 일부만) · import 부작용 signal 수신자 · LLM 경로 과금 e2e(R3 F4 (f) — 이 항목 밖).

## 6. 사용자 결정 질문

1. **적용 범위** — (가) 슬라이스 0 이 있는 모든 레인의 창(권장 · 레인당 probe 2회 수십 초~수 분 + 충돌 STOP 가능) / (나) 순수 리팩터 레인만(K1·K2 — 서비스 레인의 슬라이스 0 은 지금처럼 LLM 판단).
2. **OpenAPI 문서 층(operationId·schema 이름·summary)을 계약으로 볼 것인가** — (가) 보고만(권장 · 파일 이동 #490 이 Router operationId 를 바꿔도 레인 진행) /
   (나) red(OpenAPI 로 클라이언트 코드를 생성하는 앱 — 예 dddart 스냅샷 — 의 타입·메서드 이름 보호. 대가: #490 이동마다 STOP).
3. **약한 단언 강화** — (가) 레인 안 «보호 강화 슬라이스» 허용(입장 규범 개정: 승인 현행 계약 한정 · Red 대신 앵커 green · 창 열기 전) /
   (나) 레인 밖 별도 선행 발주로만(오라클 독립성 유지 · 발주 1건 추가) / (다) 이번 수리 범위 밖(MVP 권장 — 수요는 캠페인 S1 보호막 표에서 확인).
