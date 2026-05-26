# dddjango 스모크 테스트 피드백 로그

작성일: 2026-05-26
대상: 설치된 플러그인 `dddjango@dddjango-local` (user scope, enabled)
toy 프로젝트: `~/Desktop/dddjango-smoke/` (Django 4.2.30, config + catalog 앱, Product 모델 시드)
실행 기능: `/dddjango 재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API`
G0 확정 결정: JSON 어댑터=Django Ninja · Order=단일상품+수량 · 동시성=원자적 차감 보장 · 인증·멱등성=제외

이 로그는 **스모크 진행 중 누적**한다. 전체 스모크가 끝나면 이 로그를 입력으로 개선 계획을 세운다.

## 1. 채점 — 통과 항목

- ✅ **모드 판별**: 신규 모델·신규 계약 → 풀 파이프라인(Phase 0~3) 판단. 사양의 *시작: 모드 판별* 일치.
- ✅ **트래커 라인**: `dddjango [✓ 스코프]→[✓ 설계 (ddd·api·db)]→[▶ 구현]→[· 마무리]`. 완료/진행 표기 + 설계에 lens 표기 유지.
- ✅ **G0 스코프**: 스코프 확정에 영향 주는 실질 결정 4개를 한 묶음으로 질문(자유서술 아님) → `scope.md` 작성 → lens 추론 `ddd·api·db`(예측 적중) → G0 배너 3부 구조(방금 끝낸 것/승인 대기/다음에 할 것) + 1승인/2수정/3자유입력.
- ✅ **G1 설계 게이트**: 설계 완료 후 구현 진입 전 사용자 승인 요청. *사용자 승인 없이 게이트 통과 안 함* 사양 작동.
- ✅ **G2 구현 — 생성 코드 품질** (models.py/settings.py 직접 확인):
  - 설계 명세가 **단일 근거로 작동** — 코드 주석에 `design-spec §2.4`, `§4.4 D1`, `§2.3-1/M1` 절 번호 인용.
  - db lens가 SQLite 현실 반영 — 조건부 단일 UPDATE(`stock>=q WHERE`)로 read-then-write 갭 제거, `select_for_update`는 SQLite no-op이라 의도적 회피, `busy_timeout`으로 `database is locked` 흡수.
  - ddd·db lens 협력 — `quantity>=1` 불변식을 도메인 팩토리(`Order.create`) + DB CheckConstraint 양쪽 방어.
- ✅ **G2 감사 리포트 존재**: 수정 요청 시 후보로 "#3 415 Content-Type 게이트를 미들웨어로 끌어올리기(감사가 별도 작업으로 남긴 구조 개선)"가 제시됨 → discipline-reviewer 감사가 실제로 돌았고 우선순위 판단까지 나왔다는 증거.
- ✅ **G2 배너 + 수정 요청 진입**: 1승인(→Phase 3)/2수정요청(→해당 슬라이스 재실행)/3자유입력 구조 사양 일치. 옵션 2 선택 시 피드백 수집 단계로 진입.

## 2. 개선 항목 (스모크 후 계획 대상)

### #1 게이트 거부/수정 요청 시 권고를 선택지로 제시
- **현상**: 게이트는 선택지(1/2/3)인데, 수정 요청을 고르면 "구체적으로 적어주세요"라는 **자유 텍스트 서술**로 빠진다. Coordinator가 감사 권고 등 구체 후보를 알고 있으면서도 1급 선택지로 내놓지 않고 예시 문장으로만 흘린다.
- **왜 문제**: ① 게이트 UX(선택지)와 비일관 ② 사용자에게 백지 서술 부담 ③ 객관식 선호 원칙(AskUserQuestion 도구 철학, superpowers brainstorming "Prefer multiple choice")과 어긋남.
- **개선안**: 게이트 거부/수정 요청 시 — 감사 리포트 권고·명백한 수정 후보가 **있으면** `AskUserQuestion` 선택지로 제시(권고 1개=옵션, 필요시 multiSelect), **기타=자유입력 항상 유지**. 후보가 **없으면** 현행 자유 피드백. 게이트 거부 전반에 적용.
- **설계 정합성**: 커맨드에 이미 *"G1 미해결 트레이드오프는 배너에 옵션으로 제시"* 가 있어, 이를 게이트 거부 전반으로 **확장**하는 셈.
- **반영 위치**: `dddjango/commands/dddjango.md` (진행 가시성의 수정요청 처리 + 엣지 처리 "게이트 거부").

### #2 패키지·파일·테스트 디렉터리 구조가 설계에서 결정되지 않음 (사용자 직접 검수 발견)
- **현상**: design-spec 405줄에 도메인·API·DB는 상세하나 **물리적 코드 배치·테스트 디렉터리 조직이 전무**. toy는 `catalog/` 루트 평면(models·services·api·exceptions·middleware) + 단일 `settings.py` + `catalog/tests/` 평면(인수+단위 5파일 혼재).
- **코퍼스엔 규칙 있음**: implementation-django §3.1(`apps/<app>/` + `config/settings/` 분리, `tests/` 평면파일), architecture-ddd §6.1(`src/<context>/{domain,application,infrastructure,interface}/` + `tests/{unit,integration,e2e}/`, Django 차선 간소화 허용), implementation-test §4.2(`tests/{unit,integration}/` + 디렉터리별 conftest).
- **왜 문제**: ddd lens 활성인데 §6.1 패키지/테스트 구조가 명세·리뷰·구현 어디에도 반영 안 됨 → 구조 무결정 → coder가 기존 평면 답습. 사용자 지적 ③(테스트 의미군 폴더)은 ddd §6.1 / implementation-test §4.2가 직접 지지.
- **개선안**: design-architect가 "패키지/파일 배치 + 테스트 디렉터리 조직"을 명세 결정 항목으로 다루게(활성 ddd lens면 §6.1, Django 제약이면 차선 간소화 명시). design-review-ddd 점검 항목에 구조 포함.
- **단서(공정성)**: toy 초기 구조를 비표준으로 시작(`startproject config . / startapp catalog`)한 영향 있음 + /dddjango가 기존 구조 존중. 그래도 "구조 무결정"은 공백.
- **반영 위치**: `dddjango/agents/design-architect.md`(구조 결정) · `design-review-ddd.md`(구조 점검). 필요시 architecture-ddd SKILL 핵심원칙에 구조 결정 끌어올림.

### #3 코드 주석·docstring 언어가 전역 지침과 어긋남 (영어 주석)
- **현상**: 생성 코드 주석·docstring이 전부 영어. 전역 지침은 "Use Korean for all comments".
- **코퍼스엔 규칙 없음**: 주석 언어는 코퍼스 주제 밖(cleancode는 주석 *철학*만) — 코퍼스 공백이 아니라 범위 밖.
- **왜 문제**: 전역 CLAUDE.md 언어 지침이 서브에이전트(coder)까지 전파 안 됨 → 사용자 코드베이스 언어 일관성 저하.
- **개선안**: coder 에이전트(또는 커맨드의 코드 관례 전달부)에 "코드 주석·docstring 언어는 프로젝트 기존 관례 우선, 없으면 한국어" 명시. 기존 코드에 영어 주석이 지배적이면 그 관례 존중.
- **반영 위치**: `dddjango/agents/coder.md` (또는 커맨드의 관례 전달부).

### #4 패키지 매니저 — uv 기본 + 관례 감지 (강제 아님)
- **현상**: 스모크 toy를 `venv + pip`로 셋업. 사용자는 uv 사용을 원함.
- **코퍼스**: `uv` 0건(범위 밖). 오히려 implementation-django §3.1은 `requirements/{base,dev,prod}.txt`(pip)를 권장 레이아웃으로 가정. implementation-python/test는 `pyproject.toml`(도구 설정용).
- **왜 문제/판단**: uv는 속도·`uv.lock` 재현성 이점. 단 `/dddjango`는 기존 프로젝트에 붙으므로 **"강제"는 기존 관례 침습 + 플러그인 범용성 저하**.
- **개선안**: 강제 대신 **관례 감지** — `uv.lock`/`pyproject.toml` 있으면 uv, `requirements.txt`면 pip, 정해진 게 없으면 uv 기본. 진지하게 uv를 밀면 코퍼스 §3.1을 `requirements/*.txt`→`pyproject.toml`+uv로 현대화 검토(**#2와 얽힘**).
- **단서**: "내 모든 프로젝트는 uv"가 개인 정책이면 전역 CLAUDE.md/프로젝트 설정이 적합지, 범용 플러그인 강제는 부적합.
- **반영 위치**: `dddjango/agents/coder.md`(관례 감지) + (선택) implementation-django §3.1 현대화.

### #5 타입힌트 — 지역 변수 누락 + 강제 게이트 공백 (사용자 직접 검수 발견)
- **현상**: 함수 시그니처 타입힌트는 양호하나 **지역 변수 어노테이션이 다수 누락**. 증거: `api.py` `problem_response`의 `body = {...}` → `body: dict[str, Any]` 없음.
- **코퍼스**: implementation-python §1 "타입 어노테이션 **전 코드베이스 일관 적용**" + mypy/pyright **strict 모드 보장**(§22–§23). 규칙은 이미 강하게 있음.
- **책임 배치**: 소유=implementation-python §1(있음) / 작성=coder(시그니처는 따름, toy 증거) / **강제 게이트=공백** — discipline-reviewer 본문에 타입 점검 0건 + 검증 단계가 mypy/pyright 미실행(toy Phase 3는 test·check·drift만).
- **단서(정직)**: 지역 변수 어노테이션은 **mypy strict로도 강제 안 됨**(타입체커가 추론). ruff ANN 룰도 주로 함수 시그니처 대상. 즉 "변수도 무조건"은 표준 도구로 자동 강제가 어려워, 해결 단계에서 **정책 수위 결정 필요**(추론 가능한 곳까지 강제하면 노이즈 우려). 시그니처 강제(`disallow_untyped_defs`)는 mypy strict로 자동화 가능.
- **반영 위치**: `dddjango/agents/discipline-reviewer.md`(점검 항목) + 검증 단계 mypy/pyright strict 실행(`commands/dddjango.md` Phase 3/G2 검증) + 정책 수위 결정.

### #6 프로젝트 표준 도구 설정 (pydantic·mypy·django-stubs·ruff·pyproject) — 지식+적용 (사용자 제안)
- **제안**: 프로젝트 기본 설정을 표준화해 프로젝트 간 일관성 확보.
- **코퍼스 현황**: ruff/mypy strict `pyproject.toml` = implementation-python §22.1 있음. **`django-stubs`/mypy plugin·pydantic 프로젝트표준·통합 부트스트랩 = 0건(공백)**. django-stubs는 Django mypy strict의 사실상 필수 → **#5의 숨은 전제**.
- **형태 판단**: "스킬로 추가"는 절반 — *무엇이 표준인가*(지식)는 스킬 적합(python §22 보강 or 신규 `implementation-tooling`), *설정 깔기*(액션)는 coder/커맨드/별도 부트스트랩. 스킬은 코드 실행 안 함.
- **/dddjango 긴장**: 기능 추가 ≠ 프로젝트 부트스트랩(다른 관심사). 기존 프로젝트에 도구 있으면 존중(#4 동형 침습 우려) — "없으면 추가, 있으면 존중".
- **옵션**: A) 지식스킬 보강 + coder 관례감지 적용 (**추천**, #4/#5 전제 충족) · B) 별도 부트스트랩 단계/커맨드 · C) 개인 cookiecutter 템플릿(플러그인 밖, 감지만).
- **클러스터**: #4(uv)·#5(타입게이트)와 "도구·환경 표준화" 한 묶음 — 해결 단계에서 함께.
- **반영 위치(잠정)**: implementation-python §22 보강 + (신규?) Django stubs/mypy 지식 + `coder.md` 적용 정책. 형태는 해결 단계 확정.

## 1-b. 추가 채점 — 거부 경로 + Phase 3 (스모크 후반)

- ✅ **게이트 거부/재실행 경로**: 수정 요청 → 권고 반영 → **Phase 3로 안 넘어가고 G2 배너 재등장**("권고사항이 반영된 G2 구현을…"). 옵션 2 문구가 "수정 요청"→"추가 수정(아직 더 고칠 부분)"으로 맥락화. *게이트 거부 = 해당 단계 재실행, 다음 안 감* 사양 정확.
- ✅ **권고 반영 = 진짜 리팩터링**: 감사 #3(415 게이트) 반영 시 `catalog/middleware.py` 신설로 진입 전 검사, api.py 우회 경로(JsonOnlyParser·on_http_error·__cause__ 언래핑) **죽은 코드 정리** + 415 계약 보존 + 화이트박스 테스트를 구조 테스트로 교체. #1은 명세와 다른 판정순서가 의도적 최적화임을 주석 명시(임의 수정 안 함).
- ✅ **이중 루프 TDD 실행 증거**: 재검증 33 OK(인수 8 + 동시성 1 + 단위 24). 인수 테스트 S1~S8은 외부 계약 안전망으로 미수정 유지(Green).
- ✅ **창발 동작 — 마이그레이션 적용 게이트**(사양 미명시, Opus가 옳게 채움): 실DB 스키마 변경(SQLite CHECK 추가=테이블 재작성, 되돌리기 어려움) 앞에서 승인 요청 + **사전 점검(stock<0 행 0개)** 선제 실행. 부수효과 작업을 사용자 체크포인트로 통제하는 파이프라인 철학과 정합. 하이브리드 설계("판단은 Opus가 운전")의 모범 작동.
- ✅ **Phase 3 검증 보고 정직성**(교과서적): 실행한 것만(33 OK·check 0·drift 없음) 명령과 함께 보고 + **미실행 3건을 사유와 함께 명시**(실DB migrate=사용자 보류·적용명령 안내 / 런서버 E2E=자동 인수테스트가 계약 검증 / 마무리 재실행 생략). *미실행을 실행한 것처럼 보고 안 함* 규율 정확.
- ✅ **lens 리뷰 실제 기여**: 동시성 blocker(select_for_update가 SQLite no-op)를 **db 리뷰가 독립 발견** → 조건부 원자 UPDATE로 해결. (병렬 디스패치 육안은 미확인이나 리뷰가 의미 있게 작동한 건 확정.)
- ✅ **산출물 경로 규약**: `.dddjango/create-order-with-stock-check/{scope,design-spec}.md` (케밥 slug) 정확.
- ✅ **스코프 경계·한계 정직**: F1~F4 미구현 + 멱등성/SQLite database-is-locked 한계를 "G1에서 인지·수용"으로 명시(YAGNI + 위험 고지).

## 3. 산출물 코드 품질 정독 (2026-05-26, 메인이 직접 11파일 검수)

self-report가 아니라 명세 + 코드 5(models·services·api·middleware·exceptions) + 테스트 5를 직접 정독:
- ✅ 명세→코드 충실(절번호 주석), 레이어 경계(도메인/응용/어댑터/가드) 깨끗, 인수 블랙박스+부수효과 검증, 동시성 conservation 불변식으로 oversell 포착, 단위가 내부협력자(가격 스냅샷 불변성 등) 검증, 전역원칙 실천, #3(415) 리팩터링 동작보존.
- nit(toy 코드 흠, 파이프라인 결함 아님): `middleware.py`→`catalog.api` problem 유틸 의존(`problems.py` 분리 권장); `unit_services` 성공/부족이 인수와 시나리오 중복.

## 4. 스모크 종료 채점

- **파이프라인 동작**: 전 구간(G0→G1→G2→Phase3 + 거부/재실행 + 창발 게이트) 의도대로, blocker 0.
- **산출물 코드 품질**: 메인 정독 합격(명세 충실·레이어·의미있는 테스트).
- **사용자 직접 검수가 진행 중** — 개선점이 누적되고 있다(아래). **해결은 피드백 수집이 끝난 뒤 일괄/우선순위로** 진행(사용자 합의).
- **개선점 해결 상태 (2026-05-26 편집 완료, 미커밋·동적검증 대기)**:
  - **#1** 게이트 수정요청 선택지화 — ✅ `commands/dddjango.md`(배너-승인 + 엣지 게이트거부): 권고·수정후보 있으면 AskUserQuestion 선택지+기타 자유입력, 없으면 자유피드백.
  - **#2** 패키지/파일/테스트 구조 무결정 — ✅ 신규 `discipline-houserules` §1~§3(결정순서·충돌중재·평면금지) + design-architect(명세에 구조 결정)·coder(집행)·discipline-reviewer(점검)·commands(유령입력 교정). 근본원인 6층위(RC1~6) 규명. proactive 1차+게이트 backstop.
  - **#3** 코드 주석 언어 — ✅ `discipline-houserules` §5(기존 관례 우선, 없으면 한국어).
  - **#4** 패키지 매니저 uv — ⏸️ **보류 → 향후 `init`**(부트스트랩은 /dddjango 범위 밖). houserules §6 명시.
  - **#5** 타입힌트 — ✅ `discipline-houserules` §4(시그니처 강제=mypy strict / 지역변수 권장) + discipline-reviewer 점검 + Phase3 mypy(구성 시).
  - **#6** 표준 도구셋 — ⏸️ **보류 → 향후 `init`**(코퍼스엔 ruff/mypy/pydantic/pytest 다 있고 django-stubs만 공백 → init 때 채움).
- 미확인 1건: G1 리뷰어 병렬 디스패치 육안(기능적 우려는 db blocker 독립 발견으로 해소).

**→ 파이프라인 동작·코드 품질 자체는 합격. 개선점 6건 중 #1·#2·#3·#5 편집 완료(미커밋), #4·#6은 향후 `/dddjango init`으로 이월. 다음: 동적검증(플러그인 재설치+/dddjango 재현) 일괄 → 통과 시 커밋.**
