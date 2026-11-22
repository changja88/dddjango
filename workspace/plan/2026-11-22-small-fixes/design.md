# 설계 v2.1(확정) — dddjango 2.45.0: 새 보고 다섯(F4-181 · 182 · 189 · 201 · 203)

작성 2026-11-22 · 운영자. 배포판 = 2.44.1(77a1ed54). 재현 = `a/` ~ `d/` REPORT + 운영자 재현. 검토 처분 = `op-rev-DISPOSITION.md`(v0 = `design-v0.md` · v1 = `design-v1.md`).

## 0. 결정

| 번호 | 결정 | 출처 |
|---|---|---|
| U1 | 범위 = 새 보고 넷 한 판 | 사용자 «진행하자.»(운영자 추천에) |
| U2 | F4-203 — 검사기는 두고 e2e 행 타입 길(파일 안 `Protocol` + `.create()`)을 하우스룰에 한 문장 | 사용자 «1»(앞 «가.» 는 운영자의 틀린 전제 위 답이라 거둠) |
| U3 | F4-201 = 표에 정규식 예외 칸 · 기존 `exempt` 글자 그대로 · 옛 정본 사본은 계속 받음 | 사용자 «나.» |
| O1 | F4-181 = ⓓ 승인 유입을 따로 세고, **감사에는 묶음 한 물음으로 남긴다** | 운영자(질문 생략 · 설계 처리 · 이의 시 뒤집음) — 검토 B1 뒤 바뀜: 계획 요약에 적는다 |
| O2 | F4-182 = **캐시 이름 · `__pycache__` 아래 캐시(`.pyc` · `.pyo`)만 남은 폴더만** BC 아님(지금 있는 `cache_only_instance` 뜻 그대로) · 빈 폴더는 손대지 않음 | 운영자(같음) — 검토 B3 뒤 두 번 좁힘: 계획 요약에 적는다 |
| O3 | F4-189 = 검사기 · 도구가 제 폴더를 `sys.path` 앞에 | 운영자(같음) |
| O4 | 게이트 «진단 미파싱 줄끼리 상쇄» 는 판 밖 후보(현장 측정부터) | 운영자(같음) |
| O5 | 판 2.45.0(minor) · dddjango-web 무변 | 운영자 |

## 1. F4-181 — registry_gate ⓓ 승인 유입

**문제**: 승인 목록이 있어도 ⓓ 신규에 들인 다른 레인 줄이 섞여 줄마다 닫게 된다.

**게이트**
1. 출처 재실행 표본에 그 검사기의 ⓓ 줄도 싣는다.
2. 차례: ⓓ 짝짓기 → `--group-moves` 따라가기(`_follow_moves`) → 남은 신규에 승인 유입 증명(위반 줄과 같은 식 · 미증명 · 측정 무효 · 생략은 신규).
3. ⓓ 증명은 결과 · 진단을 위반 쪽과 따로 든다(`inflow` · `retained_reasons` · 머지 표 · 꼬리 «승인 유입 N건» · sidecar `provenance` 에 섞이지 않음). 사본 · 실행 캐시만 같이 쓴다.
4. 유입이 있으면 `== ⓓ 승인 유입 k건 — 감수자 묶음 물음 ==`(줄 · 머지 SHA) · sidecar `candidate_inflow`. `candidate_lines` 는 신규만.
5. 무변: exit · 귀속 · ⓓ legacy · 해소. 목록이 없거나 ⓓ 유입 0 이면 출력 · sidecar byte 무변(툴체인 행 밖).

**글**(graph-owned · Codex 같은 뜻)
- 커맨드 Phase 2 «ⓓ 목록을 위한 registry_gate»(170행 · R-3664 라벨): 6번과 같은 인자(승인 목록 동반).
- 집중 감사 방아쇠 넷(R-3725 · R-3727 리비전): 커맨드 231 · Codex `dddjango/SKILL.md:250` «ⓓ 신규» / 커맨드 255 · Codex 272 «새 ⓓ 줄» → 넷 다 «ⓓ 신규 · ⓓ 승인 유입» 에 새로 선 줄.
- 커맨드 Phase 2 5번 · R-0284: 동봉 = ⓓ 신규 + (있으면) ⓓ 승인 유입 절.
- discipline-reviewer «ⓓ 후보 마무리»: «ⓓ 승인 유입» 은 줄마다 답하지 않고 묶음 한 물음에 답한다 — **이 실행의 변경(주어 파일 밖 — 표 · 설정 · 부르는 쪽 포함)이 답을 바꿀 수 있는 줄이 있나**. 있으면 그 줄은 신규처럼 닫고, 나머지는 «착륙 레인 몫 — k건 기각» 한 줄 + 확인한 변경 범위. 무응답 금지는 그대로(R-1074 · R-1075 리비전).
- discipline-reviewer 100행(+ Codex · R-1011 리비전) «#63 ⓓ 후보 줄은 전부 … 네가 닫는다»: 신규는 줄마다 · 승인 유입은 위 묶음 물음으로.
- 승인 머지 목록 문단: G2 배너에 «ⓓ 승인 유입 k건». registry_gate 머리 docstring 두 문단 · `:944`.
- 게이트 «ⓓ 신규» 머리 글 «감수자 입력은 신규분만»: 유입 ≥ 1 일 때만 «신규분 + 승인 유입 묶음»(0 이면 글자 무변).

**시험**: c1(신규 1 · 유입 4) · c2(고친 줄 신규) · c3(신규 · 출력 byte 무변) · g_cross(유입 절과 sidecar 에 남음) · g_moves(legacy 3 · 해소 0 그대로) · 목록 없음 byte 무변.
**변이**: ⓓ 표본 안 실음 · F1 건너뜀 · L 건너뜀 · 가름을 따라가기 앞에 · 위반 쪽 결과에 섞음 · 유입 절 안 찍음. **글 계약**: 방아쇠 넷에 «ⓓ 승인 유입».

## 2. F4-182 — BC 자리

**문제**: `application/` 직계의 `__pycache__` · 캐시만 남은 폴더가 BC 로 세어져 거짓 red · #365 가림.

**동작**
- `business_vocab.bc_folder(p)` 거짓 = 점 이름 · layer-skeleton 일곱 이름(`build` · `dist` 는 BC) · `checker_target.cache_only_instance(p)`. **새 술어 · 새 부산물 목록 · git 조회를 만들지 않는다**(F4-16 · 17 때 정한 뜻 그대로: `__pycache__` 아래 캐시 파일 ≥ 1 · 그 밖 파일 0). 그래서 **빈 폴더 · 링크 · 읽기 불능은 BC 다**.
- 쓰는 자리: `server_bc_dirs` · `container_bc_names` · layer-skeleton · context-isolation 두 자리 · 채택 신호 열거 열여섯(composition-root 포함) · pre-gate `baseline_bcs`(`design_pregate.py:6346`). port-adapter 는 BC 마다 한 번만.
- registry_gate 지금 사본: `_snapshot_cache_instances` 가 `application/` 직계 폴더에도 `cache_only_instance` 를 건다(`not bc_folder` 가 아님 — 파일 · 이름 거름까지 사본에서 빠지면 안 됨). anchor_diff 무변.

**시험**: V0 · V1 · V2 · V4 ~ V6 · full_cache · cache_min_api · build · dist · 지운 BC · 옮긴 BC 의 캐시(= 지운 트리와 같음) · `.gitkeep` 새 BC(red 17 그대로) · 앵커부터 `.gitkeep`(exit 0) · gitlink · 추적된 ruff/pytest(옛 판과 같음) · 빈 폴더 · `.DS_Store` 동반(옛 판과 같음) · P8 · pre-gate 예보 · #365 되살아남 · guard_zero 둘. `registry_gate_smoke:642-647`(`cache_bc` 를 사본에 남김 — 2.18.2 의 선택 인스턴스 경계)은 기대를 뒤집고 판 기록에 적는다.
**변이**: cache 조건 뺌 · 사본 거름 뺌 · build 를 이름 거름에 · 빈 폴더를 거짓으로 · pre-gate 줄 되돌림.

## 3. F4-189 — `-I` 에서 돌기

**동작**: 첫 같은 폴더 import 앞에 `behavior_support.py:43-44` 꼴. 27종은 `sys` · `pathlib.Path` import 를 그 앞으로 올리고 regen_core 는 모듈 수준 `sys` 를 더한다. behavior_guard · regen_core · refactor_audit 는 모듈 수준.

**시험**: 검사기 27 import(`-I` · `-P` · `PYTHONSAFEPATH=1` · Django 가 드는 정본 자산은 뺌) · 세 도구는 함수 안 import 까지(`support --collect` · `--selector sparql` · refactor_audit 의 folder_group 로딩) · `PYTHONSAFEPATH=1` 게이트 exit 2 · 심은 `json.py` 안 읽음 · checker_lint 꼴 검사.
**변이**: 검사기 하나의 줄 · behavior_guard 줄 · regen_core 줄 · refactor_audit 줄 지움.

## 4. F4-201 — `exempt_pattern`

**정본**: `PreRouteResponse.exempt_pattern: NotRequired[tuple[str | None, str]]` · `_exempted` = 글자 칸(그대로) 또는 정규식 칸의 글자 값 하나가 문서 경로(템플릿 글)에 `re.fullmatch` · 깨진 정규식은 그대로 실패.

**옛 사본(U3)**: 지금 자산 → `pre_route_responses_canonical_2_38_0.py` · 받는 셋. 맞은 자산의 칸 이름으로 표를 잰다 — 옛 사본 + 새 칸 = #63 «지금 판 정본이라야» · 옛 사본 + 옛 칸 = 무변. 새 칸의 꼴 · 설정 실존 · 좁힌 행(ⓓ) 집합은 `exempt` 와 같음.

**글**(graph-owned)
- ninja final §6.2: 코드 `:4099` · 산문 `:4080` · `:4054` + R-3749 · R-3750 라벨. 칸 뜻은 미들웨어가 설정을 보는 법(글자 같음 / fullmatch)을 G1 근거로. 옛 판도 받되 새 칸은 지금 판만.
- **문서 때문에 설정 값을 바꾸지 않는다**(그 값은 실행 때 제외 범위다). 템플릿 글에는 맞고 실제 값 일부에는 안 맞는 꼴(`[^0-9]+` · path 자리 `[^/]+` · mount 앞머리에 기대는 앞 와일드카드)이 하나라도 든 설정에는 이 칸을 쓰지 않는다(문서에 남김 = 날 수 있다 쪽). `\d+` 처럼 템플릿에 안 맞는 꼴은 문서에 남을 뿐이라 된다.
- test final 행 시험: 글자와 다르게 맞는 operation 이 있으면 그 하나로 «문서 없음 = 실제 없음».
- design-review-api 12번 좁힌 칸 목록(+ Codex).
- 딸린 것: workspace/reference 소스 미러 둘 · LEDGER · 계수표 · q4 골든 · rulepack · seal · reverse_coverage · canonical check · 픽스처 사본 · backstop 기대 글 하나(`pre-route-b-canonical-function-docstring` 33 → 34번째).

**시험**: behavior smoke(정규식 · `\d+` · 앞머리 · 글자 `.` 무변 · 두 칸 합 · 새 칸 메서드 조건 · 깨진 정규식) · backstop(정상 · 꼴 · 설정 없음 · 좁힌 행 ⓓ · 옛 사본 둘 × 새 / 옛 칸).
**변이**: match 로 · 갈래 맞바꿈 · 합을 교집합으로 · 메서드 조건 뺌 · 꼴 검사 뺌 · 자산별 칸 검사 뺌 · 좁힘 집합에서 새 칸 뺌.

## 5. F4-203 — e2e 행 타입 길(글만)

**글**: `discipline-houserules-skill.ttl` §4 `s007-4/b1` 끝 한 문장 · R-3148 리비전(clarification) · Codex 손 미러.
«e2e 시험은 자기 BC 모델을 import 하지 않으므로(#390), `factories/` 로 만든 행의 타입은 그 파일 안에 읽는 칸만 적은 `Protocol` 로 달 수 있다 — `row: _Row = XModelFactory.create()`(호출 꼴 `XModelFactory()` 는 mypy 가 factory 로 읽는다 · property · 관계 칸은 Protocol 에 `@property` 로 적는다 · 칸까지 검사되는 것은 모델을 첨자로 단 factory 일 때다).»
«달 수 있다» — 새 의무 없음. #390 · #493 · F4-33 «현행 유지» 무변. TYPE_CHECKING 길은 접음.

## 6. 진행 중 실행

| 항목 | 바뀌는 쪽 |
|---|---|
| F4-181 | ⓓ 신규 수가 줄고 묶음 절이 생김(승인 목록 있을 때만) · 감사가 보는 줄은 줄지 않음 · exit 무변 |
| F4-182 | 캐시 거짓 red 줄고 가리던 #365 되살아남 · 현장 8뿌리 BC 117 모두 실파일(해당 0 — 11-22 셈) |
| F4-189 | 실행 불능 → 정상 · `PYTHONSAFEPATH` 거짓 green → red(현장 0) |
| F4-201 | 옛 사본 · 옛 표 무변(391실행 시제품) |
| F4-203 | 판정 무변 |

pre-gate 실행 트리 지문이 바뀌어 다음 G1′ · G2 전에 재예보.

## 7. 받아들일 한계 · 판 밖
- 빈 폴더 · `.DS_Store` 나 도구 캐시(ruff 등)가 함께 남은 폴더 · git 무시 실파일 폴더는 지금처럼 BC 다 — 게이트 · scope 렌더 · 직접 실행 모두 red, 그 폴더를 지우면 풀린다.
- 앵커에 실파일 없이 커밋된 캐시나 gitlink 만 있는 BC 자리는 두 사본 판정이 갈려 새 red 가 설 수 있다(현장 BC 117 모두 실파일 = 해당 0). 커밋된 캐시는 폴더째 지우면, gitlink 는 안의 캐시만 지우면 풀린다.
- main 에 레인 없이 바로 든 커밋의 ⓓ 는 묶음 기각 사유 «착륙 레인 몫» 이 참이 아니다 — 감수자가 그렇게 적지 않고 신규처럼 닫는 것은 읽어야 보인다.
- BC 안쪽 빈 폴더의 게이트 사본 비대칭 · «진단 미파싱» 상쇄 · web `-I` 실패 도구 셋 · web 캐시 BC(추정) · 빈 BC 폴더 · #390 기존 우회 — 작업 리스트 후보.
- 묶음 물음은 읽어야 보이는 판정이다(검사기가 «답이 바뀌었나» 를 재지 않음).
- 정규식 ↔ 템플릿은 글로 정한 꼴 밖에서 어긋날 수 있고 설정 값은 검사기가 읽지 않는다 · 문서 경로에는 SCRIPT_NAME 이 붙는다.

## 8. 단위

| 단위 | 맡은 파일 |
|---|---|
| C(§1 → §2 → §3 차례) | registry_gate · business_vocab · design_pregate(기준선 BC 한 줄) · 열거 자리 검사기 · 27종 머리 import · 도구 셋 · checker_lint + 픽스처 · registry_gate_smoke · field_report_checker_smoke · fixture_matrix |
| P(§4) | 정본 자산 셋 · openapi 검사기 정본 · 표 구역 · backstop 행렬 · pre_route_behavior 스모크 + 픽스처 · canonical check · seal 목록 · reverse_coverage 갈래 |
| 운영자 | 그래프(§1 · §4 · §5) · render · LEDGER · 계수표 · q4 · rulepack · 소스 미러 · Codex 산문 · 골든 · pregate kinds · 봉인 |
