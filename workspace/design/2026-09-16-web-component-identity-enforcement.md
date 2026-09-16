# dddjango-web 1.1.20 — 컴포넌트 정체 집행 (설계 정본)

**정본** · 2026-09-16 · hyun 지시 「니가 알아서 끝까지 진행. 완료 또는 3회 반복 실패 시에만 보고」

## 1. 문제 (hyun OK 확정)

> 파이프라인이 **선언된 컴포넌트 정체를 이탈(override)로 대체 가능한 것으로 취급**해, 구현이 선언한 컴포넌트를 다른 것으로 바꿔 그려도 승인·통과된다.

증상: A8 관계인 화면의 드롭다운 4개(관계·태어난 시·시·도·시·군)가 시안이 `component-from-global-scope="…Select"`로 선언한 커스텀 Select 대신 **native `<select>`**로 그려짐.

## 2. 근거 (전부 코드 확인)

- **동결 무죄(확증)**: `20260912-1640-web-related-persons/design-ref/관계인.dc.html`에 `.Select` ×4 + `_ds`가 동결돼 있음. architect는 이탈 표 D2(`20260907-2302-user-info-input/design-spec.md:461`)에 "시안=dc Select"라 **적고도** native로 갔다("설계자 결정 · **G1 override**", 사유 「접근성·bespoke JS 회피」). → 정체가 없어서가 아니라 **있는데도 override**.
- **이탈 표 = 순수 산문, 기계 집행 0**: `dddjango-web/scripts/**`에서 이탈/deviation/override 파싱 0건. G1 override는 Coordinator가 `scope.md`에 자유문으로 기록, coder·discipline이 자율 대조.
- **dddart는 정체를 코드로 안 잡는다**: 레포 전체 `component-from-global-scope` 0회. 「dc.html은 형상 근거일 뿐, 위젯은 새로 쓴다」 규율 + 스크린샷 육안 대조가 전부. Flutter엔 native 평탄화 유혹이 없어서 성립. **HTML은 native `<select>`가 강한 유혹** → dddjango-web은 dddart에 없는 **코드 가드**가 필요(오마주가 아니라 타깃 차이 보정).
- **연결 키 불안정**: dc.html Select엔 `id`/`name` 없고 한글 `label`뿐. 관계 필드는 `select_field.html`(공용 native 파셜)조차 우회해 인라인 native. 트레이스는 `{% comment %}`라 렌더에서 소멸. → **필드별 매핑 불가 → 화면/트리 단위 검사**.

## 3. 삽입 지점 (코드 확인)

- `check_design_evidence.py`:
  - `validate_visual(build, project, spec, input_digest, impl_digest)` (:441) — `build`(→`design-ref/*.dc.html` 바이트), `project`(→`web/**` 트리) 이미 수령.
  - `implementation_digest(project, spec)` (:419) — `project/web/**` 전수 접근.
  - `Defects(messages)` (:29) — 결함 메시지 리스트. `main()`에서 exit 2 = `[design-evidence] defect:`.
  - `run()` phase `visual`에서 검사 실행(:566).
- A8 빌드 게이트: Coordinator가 `--phase visual` 실행(command:192, exit 2 반송) + G2 `backstop.py`(command:194, exit 2 반송). backstop은 이미 design build마다 `validate_inputs→implementation_digest→validate_visual`를 돌리고 `Defects`를 `design_defects`로 접는다.

## 4. 메커니즘 — 결정적·브라우저 0 정체 검사

새 함수 `validate_component_identity(build, project)` (in `check_design_evidence.py`), `Defects`로 반송:

1. `build/design-ref/**/*.dc.html` 파싱 → `component-from-global-scope="X.Type"`의 **Type 집합** 수집(마지막 `.` 뒤). dc.html 없으면 no-op(이미지 단독 시안 등).
2. **레지스트리** `NATIVE_FLATTEN = {'Select': [r'<select\b'], 'Dropdown': [r'<select\b']}` — 커스텀 타입 → 그 타입을 평탄화한 **금지 native 형태**. (구조상 확장 지점; 지금은 실사용 타입만 채운다 — YAGNI.)
3. 선언 집합 ∩ 레지스트리의 각 타입에 대해, `project/web/**/*.html`에서 금지 native 패턴을 스캔. 발견 시 결함:
   `component-identity: 시안이 커스텀 'Select'를 선언했으나 구현이 native <select> 를 렌더함 (web/…:NN). 선언 컴포넌트를 충실히 실현하라(커스텀 드롭다운) — native 로 평탄화 금지.`
4. **이탈 표를 읽지 않는다** → 정체는 override 불가(문제 정의의 핵심 차단).

**왜 전역 `web/` 스캔이 정당한가**: 이 디자인 시스템은 상호작용 필드를 전부 커스텀 컴포넌트로 선언한다(dc.html에 native `<select>` 0건). 따라서 시안이 커스텀 Select를 쓰는 한, `web/` 어디의 native `<select>`든 = 평탄화. 필드별 매핑(불안정) 없이 성립. `select_field.html`(현재 native)도 이 규칙으로 red가 되고, 수리되면(커스텀 드롭다운) 전역에서 native가 사라져 green.

**"native로 좁힌 것 아닌가"에 대한 답**: 정의는 일반("선언대로 실현")이고, 레지스트리는 각 커스텀 타입의 **금지 평탄화 형태**를 담는 일반 구조다. native `<select>`는 Select의 금지 형태 한 항목일 뿐 — Dialog·Checkbox 등은 항목 추가로 확장. 지금은 실패가 실재하는 Select/Dropdown만 채운다.

## 5. 왜 A8을 통과시키나 (인수 논리)

관계인 재동결 → dc.html `.Select` ×4 → 구현이 native `<select>`면 `--phase visual`/backstop이 exit 2 → coder 반송 → **커스텀 드롭다운을 그릴 때까지 done 불가**. 고정 프롬프트 한 줄만으로 플러그인이 자율 집행.

## 6. coder/스킬 지침 (구현의 나머지 절반)

`coder-web.md`(+필요 시 `implementation-ui`/`implementation-javascript` 스킬 산문)에 명문화:
- 시안이 `component-from-global-scope`로 **커스텀 컴포넌트**를 선언한 상호작용 컨트롤은 **native 등가로 평탄화 금지**. 충실히 실현하며 필요하면 JS로 커스텀 드롭다운을 작성(implementation-javascript).
- **「접근성·bespoke JS 회피」는 정체 교체의 유효한 이탈 사유가 아니다.** 이탈 표는 컴포넌트 **내부 외형**(색·간격·variant)만 조정한다.

## 7. 픽스처 (안쪽 게이트 — 배포 전 증명)

`fixtures_design_evidence.sh`(또는 신규 `fixtures_component_identity.sh`, `run_fixtures.sh` 등재):
- **RED**: design-ref에 `.Select` 선언 + `web/`에 native `<select>` → 검사 exit 2(결함).
- **GREEN**: 같은 선언 + `web/`에 커스텀 드롭다운(트리거+메뉴, native `<select>` 없음) → exit 0.

## 8. 미러·봉인·범위

- `codex-dddjango-web/` byte 미러 동기화(scripts). md는 의미 미러.
- Makefile/파일 목록 변경 시 `manifest_seal.py --write` 별도 chore(변경 커밋 뒤).
- 플러그인 1.1.20 = **검사 + 지침**뿐. 실제 커스텀 Select 컴포넌트는 A8 재실행 때 coder가 짓는다(플러그인엔 안 들어감).

## 9. 리스크 / 적대 검토 대상

- 전역 `web/` 스캔의 오탐(디자인이 커스텀 Select를 안 쓰는데 native가 있는 화면?) — 이 프로젝트엔 없지만 일반성 확인.
- `<select\b` 정규식이 문자열/주석/JS 안의 리터럴을 오탐하는가(check_clip_clearance의 주석 오탐 선례).
- dc.html 파싱이 `_ds` 내부 정의까지 긁어 과대 선언하지 않는가(화면 dc.html만 vs `_ds` 컴포넌트 정의 파일 구분).
- backstop 경로와 `--phase visual` 경로 양쪽에서 실제로 발화하고 A8을 막는가.
- 픽스처가 검사기 자체를 검증(선례 verify-web 무용지물 재발 방지).

## 10. 적대 검토 반영 (구현 확정 · 2026-09-16)

subagent 적대 검토가 잡은 항목을 반영해 구현:

- **[BLOCKING] 배선**: `run()`이 아니라 `validate_visual()` 안에 접었다(`issues.extend(validate_component_identity(build, project))` → `raise Defects(issues)`). backstop.py가 `validate_visual`을 직접 import(:30)·호출(:243)하므로, 이 지점이 G2(backstop)와 CLI `--phase visual` 양쪽이 공유하는 유일한 집행점이다. `run()`에만 넣었으면 G2가 조용히 통과했을 것.
- **[BLOCKING] 주석 스트립**: `COMPONENT_COMMENT_RE`로 `{% comment %}`·`{# #}`·`<!-- -->` 제거 후 `<select[\s/>]` 스캔(check_clip_clearance 선례). 이 수리가 건드리는 파일에 이미 두 사례(select_field.html:2·hour_field.html:7-8)가 있어, 안 하면 올바른 수리도 red로 남을 뻔했다.
- **[HIGH] GREEN 픽스처에 한글 근거 주석**: `test_faithful_dropdown_with_rationale_comment_passes`가 「이전에는 native `<select>`를 썼으나…」 주석 + 커스텀 구현으로 주석 스트립을 실제로 시험.
- **[MEDIUM] hidden native mirror 금지**: coder-web.md·design-architect-web.md에 명문화(숨은 native mirror도 금지).
- **[MEDIUM] blast radius(수용)**: web/ 전역 스캔. 실측상 web/ 전체에 real native `<select>`는 2개(select_field.html·related_person_editor_step.html)뿐 — 둘 다 관계인 수리 범위. 고치면 앱 전역에서 native가 사라져 green. 검사는 **현재 빌드의 design-ref 선언에만** 발화(다른 빌드가 Select 미선언이면 native가 있어도 그 빌드는 안 막힘). 공유 select_field.html 수리가 타 화면 외형을 커스텀으로 바꾸는 건 정체 집행의 의도된 결과 — 수용.
- **[LOW] direct glob**: `design-ref/*.dc.html`(직속만) — `_ds`·`_history`·`_prev-*` 제외.
- **[LOW] `<select[\s/>]`**: 커스텀 엘리먼트 `<select-x>` 오탐 회피 · `*.html`만 스캔.

**증명**: 픽스처 6/6 green · 실제 A8 관계인 빌드 대상 발화 2건 확인(재실행 시 반송 확정) · `make verify-web` green.

## 11. iter 2 (1.1.21) — 검사를 「확인/수정」 경로까지 도달시킴

iter 1 실패 근본원인: 일반 프롬프트("확인하고 수정해")로는 `/dddjango-web` 커맨드(`disable-model-invocation: true`)가 안 돌아 파이프라인·게이트가 통째로 우회됨. A8는 informal 내용 diff로 "일치·변경 없음" 결론 → 정체 검사(구현 게이트 위치)가 발화조차 못 함.

**1.1.21 조치:**
- `check_design_evidence.py`에 **`--phase identity`** 추가 — 시각증거·design-input 없이 `validate_component_identity`만 결정적 실행(exit 2=평탄화). 실제 A8 관계인 빌드에 exit 2·native 2건 확인. 픽스처 8/8(함수 6 + CLI 2).
- **자동 로드 스킬에 강제 문구 + 로드 트리거 확장**:
  - `architecture-web`(검수/리뷰 경로)·`implementation-ui`(수정 경로) description에 "기존 화면을 시안과 대조·확인·수정할 때 로드" 추가 → A8의 "확인" 작업이 스킬을 로드.
  - 두 스킬 본문에 **필수 순응 검증**: 결론 전 `--phase identity` 실행 · exit 2 = must-fix 비순응(내용 동등·D2·접근성으로 미룰 수 없음) · 선언 커스텀 컴포넌트로 재구현(JS 허용) · "검사 없이 일치/변경없음 결론 금지".
- codex byte 미러(scripts) + SKILL 미러. make verify-web GREEN.

## 12. iter 3 (1.1.22) — 「되묻지 말고 바로 수리」

iter 2(1.1.21) 결과: A8가 native↔커스텀 Select 격차를 **정확히 식별**했으나, 디자인 파일 byte-동일(변경 없음)을 보고 AskUserQuestion으로 «의도 확인»하며 정지 — 자율 수리 미달. 강제문구가 "must-fix·재구현"까지였지 "되묻지 말라"가 아니었음.

**1.1.22 조치:** architecture-web·implementation-ui 강제문구에 추가 —
> exit 2면 사용자에게 되묻거나 의도 확인을 요구하지 말고 **바로 수리**한다. 디자인 파일이 안 바뀌어도(byte-동일) 이 비순응은 «확인하고 수정해»가 지시하는 명백한 수리 대상이며, «저장 안 됨/다른 변경» 대안을 제시하며 멈추지 않는다.

스크립트 변경 0(스킬 프로즈만) · codex SKILL 미러 · make verify-web GREEN.
