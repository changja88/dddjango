# 설계 R8d — ① core verdict-final · ②-A web plan 소비자 · D plan grep 묶음 (2026-09-30)

기준: main HEAD `a1d97bc3`(도구는 8c `a34e93db` 와 같음). 행 번호는 모두 HEAD 기준이다.
입력: 진단 `diag-R8d-1-verdict-final.md` · `diag-R8d-2-plan-consumer.md` · 선례 `design-R8c-E1-E2.md` · `repair-R8c-impl.md` · scratch `review-R8c/review-R8c.md`.
사용자 결정(09-30): ① 권장안(web 방식 `verdict-final.md`) · ②-A 안 A · D «D도 함께 (권장)», 별 커밋. 이 문서는 그 범위 안의 설계만 담는다.
적대 리뷰(09-30 · 둘 다 «수정 후 승인»): scratch `review-R8d-core/review-R8d-core.md`(minor 3 · nit 3) · `review-R8d-web/review-R8d-web.md`(major 1 · minor 3 · nit 3). 운영 세션 처분은 §8 에 있다. 본문 §0~§7 은 처분을 반영한 판이다.
프로토타입: scratch `r8d/`(HEAD 복제 `repo/` — `git clone --shared` · 현장 레인 사본 APFS 복제 `field/`). 저장소 파일은 이 문서 말고 고치지 않았다.
- 적용 스크립트
  - ①: `p1_core.py`(도구) · `p1_fx.py`(픽스처) · 리뷰 반영 `p1b_fx.py` · `onto_r3517.py` · `ledger_r8d.py`
  - web: 커밋 판별 픽스처 조립 `build_web_fx.py`(→ `fx-web-A2.sh` · `fx-web-D2.sh` · `fx-web-O.sh`)
  - 도구 판: `tools-A` · `tools-ADN` · `tools-ADNO`
  - 합친 diff: `r8d-all.patch`
표기: **[실측]** = 이번에 돌려 확인함 · **[추정]** = 코드를 읽어 추론함.

## 0 요약

- **①** `check-verdict` 가 exit 0 일 때 확정 표를 `verdict-final.md` 로 쓴다(web `:1157-1175`·`:1587` 과 같은 모양).
  - core 소비자 넷(`_scope` 병합 차감 · `_origins` · `cmd_resolution` · `cmd_residual`)은 이 파일만 읽는다. 없으면 실행 불능(exit 1)이다.
  - 실행 불능 안내는 조건부다. BC 가 바뀌지 않았을 때만 재실행하고, 바뀌었으면 멈추라고 안내한다(리뷰 core m1).
  - `--final` 이 병합 대상을 기록에서 빼면 그 병합 항목은 채택으로 확정한다. 고아 병합을 금지하는 5행이다(core m2).
  - 8c `_scope` 의 이중 판독은 한 곳 판독으로 줄인다(§1.2).
  - 문면은 R-3517 rev2 한 규범뿐이다(잇기 동결 대상).
- **②-A** web `compute_plan` 에서 범위 밖 `web/` 적중 줄은 정적 로드만 하는 줄을 빼고 모두 «경계 교차 소비자»가 된다. 모양 표지는 달지 않고, 문면도 바꾸지 않는다.
  - 영역 화면 소비자뿐 아니라 **client·정적 단위의 G2 영향 화면 공백도 닫힌다**(HEAD 는 client 소비자 0 · 정적 `<img>` 참조 줄 누락 — 리뷰 web m3 [실측]).
- **D** `_refs` 를 `_Refs` 메모로 바꾼다. 필요한 파일의 꼬리를 git grep 두 번(-F · -F -w)에 묶고, Python 에서 파일별로 나눈다(ASCII 경계).
  - `_plan_names` 의 `경로:` 쌍도 쌍마다 두 번으로 묶는다(리뷰 web M1).
  - `src/debt.py` 는 바꾸지 않는다.
- **web 고아 병합**: core m2 와 같은 결함이 web 에서 재현됐다 [실측]. 같은 모양으로 고치고 별 web 커밋에 둔다(§3′).
- **실측**
  - 픽스처: core 199 → **213 ✓**. web 151 → **177**(②-A) → **184**(D) → **186**(고아 병합) **PASS**.
  - HEAD 대조: 새 사례가 HEAD 도구에서 core 14 · web 15 red 다(web D 사례는 ②-A 도구에서 5 red).
  - 변이: core 9/9 · web 8/8 를 잡았다.
  - 현장 plan: HEAD 55.6~59.1초 → **1.6~1.8초** · plan.md byte 동일.
  - 현장 `--names` 폴더 쌍: 9.7~41.3초 → **2.0~3.2초** · 산출 동일.
  - verify: 최종 판(① + 재봉인 + web 셋)에서 `make verify` 5묶음 green · `make verify-web` green(§6).
- 열린 쟁점: 없음(§7).

## 1 ① core — `verdict-final.md`

### 1.1 코드 (`dddjango/scripts/refactor_audit.py` · Codex byte 미러 · +42/−13 [실측])

| HEAD 행 | 변경 |
|---|---|
| :16 사용 문구 | `verdict.md 검사 → verdict-log.md append · (exit 0) verdict-final.md · \`요약:\` 1행` |
| :1001-1006 `_load_verdicts` | 인자 `name: str = "verdict.md"` 추가(web `:1160` 과 같음). 앞에 `VERDICT_FINAL` 상수 |
| 신설 `_write_final(audit, verdicts, final)` | web `:1165-1175` 를 그대로 옮긴다. 머리 `# verdict-final — check-verdict exit 0 <시각>[ · final]`, 표 `M \| 원 행 \| 판정 \| 근거 \| 파일:행 목록`, 병합은 `병합 → <대상>`, 칸 속 `\|` 이스케이프 |
| 신설 `_final_verdicts(audit) -> dict[str, Verdict]` | 없으면 ToolError(아래 안내문) |
| :1237-1238 `_finalize_verdicts` 끝 | 고아 병합 금지 5행: `adopted_m = {채택 M}` · 병합 대상 `M` 이 그 밖이면 reclass «병합 대상 M 이 확정 기록에 없다 → 채택» · `kind, merge_to = "채택", ""` |
| :1293-1294 로그 append 뒤 | `if code == EXIT_OK: _write_final(audit, verdicts, final)` — `--final` 이면 `_finalize_verdicts` 뒤 목록, 아니면 «별도 요청 → 채택» 재분류가 반영된 목록이다 |
| :1382-1383 · :1431-1435 `_scope` | 병합 차감 = `{v.mid for v in _final_verdicts(...).values() if v.kind == "병합" and v.merge_to in (adopted_c if C else adopted)}` · docstring |
| :1518 `_origins` | 메시지 «ⓐ 항목 M 이 verdict-final.md 에 없다» |
| :1708 · :1848 | `verdicts = _final_verdicts(audit)` |

실행 불능 안내문(1안 · 조건부):

> 의미 audit 의 verdict-final.md 이 없다(check-verdict exit 0 판 없음) — 대상 BC 가 그 plan.md 의 HEAD 뒤 바뀌지 않았을 때만(G0 정지 재개 조건) `check-verdict <audit>` 를 다시 돌린다(앞 확정 판이 final 이면 --final). 바뀌었으면 다시 돌리지 않고 멈춘다 — 재실행은 바뀐 코드로 원 행을 다시 검사해 G0 확정 표를 바꾼다

- `_previous` 는 그대로 남는다. `check-verdict` 가 R3 재실행 번호 대조와 대리 축소에 쓴다.
- «상시 답 인식 블록»(:159-193)은 건드리지 않는다.

### 1.2 `_scope` 이중 판독 단순화 — 결정과 근거

8c 는 차감 조건을 «로그 마지막 exit 0 판이 `병합→M/C`» ∧ «verdict.md 가 병합» ∧ «대상 조건»으로 잡았다. **앞의 두 조건을 `verdict-final.md` 한 곳 판독으로 바꾸고, 대상 조건(mi1 x4·x5 · mi-B)은 남긴다.**

1. 이중 판독을 한 이유는 core 로그 표에 병합 대상(`merge_to`)이 없기 때문이었다. `verdict-final.md` 에는 종류와 대상이 둘 다 있다.
2. 로그의 exit 0 판과 `verdict-final.md` 는 **같은 호출이 같은 `verdicts` 목록으로** 쓴다. 그래서 8c 교집합과 논리적으로 같다. 갈리는 것은 x3(편집 드리프트)과 «로그 없음·확정 표 있음»(비현실)뿐이다(리뷰 core 확인).
3. `_origins` 와 `_scope` 가 한 출처를 읽는다. B1 과 진단 B·C·D·E 의 뿌리(서로 다른 출처)가 없어진다.
4. x3 기대 반전: 확정 뒤 verdict.md 만 고친 편집은 따르지 않는다. M2 원 행은 M1 묶음에 `(병합 M2)` 로 실려 리뷰어가 확인하므로 조용히 빠지지 않는다. G0 계약(`dddjango.md:241` «`verdict.md` 원 판정을 따르지 않는다»)과 같다.

### 1.3 fail-closed

| 상태 | 동작 [사례] |
|---|---|
| `verdict-final.md` 없음 | `resolution`·`residual` 실행 불능(exit 1) · 조건부 안내 [E2-0 · F9 · F9′] |
| 깨짐(표 없음·M 행 없음·병합 행만) | ⓐ `M` 마다 «verdict-final.md 에 없다» 실행 불능 [실측 — 리뷰 `t_broken.py`] |
| exit 2 재실행 · exit 1 | 앞 확정 표를 지우거나 바꾸지 않는다. 확정 표는 늘 로그의 마지막 exit 0 판이다 [F8] |
| 번호 중복 · 새 번호 · 원 행 이동 | 확정 표는 `--final` 이 정리한 뒤 목록이라 M 이 유일하다 [F1~F6] |
| 병합 대상이 기록에서 빠짐(고아) | 병합 항목은 채택으로 확정한다. G0 이 ⓐ/ⓑ 를 묻는다 [F10] |
| 칸 속 `\|`(근거 칸) | 이스케이프로 칸이 밀리지 않는다. ⓓ 표식이 파일:행 칸에 남아 `--candidates` 가드가 선다 [F11] |
| 손으로 고친 확정 표 | 검출하지 않는다. web 과 같다(§5) |

### 1.4 옛 폴더와 현장 영향

- **옛 폴더**: 수리 전 도구로 만든 audit 에는 로그만 있고 `verdict-final.md` 가 없다. G1 `resolution` 이나 G2 `residual` 이 조건부 안내와 함께 멈춘다.
  - 재실행 회복은 **코드 무변일 때만 결정적이다** [실측 7/7 모양 — 리뷰 `t_refinal`].
  - Phase 2 뒤에는 다르다 [실측 — 리뷰 `t_recover`]. `check-verdict` 가 원 행 `파일:행` 을 현재 작업 트리에 다시 대조하므로, 원 행 파일이 줄면 `--final` 이 그 원 행을 판정에서 뺀다. G0 이 승인한 원 행이 조용히 빠진다.
  - 그래서 안내문이 «바뀌었으면 다시 돌리지 않고 멈춘다»로 막는다(F9′). 도구가 git diff 로 직접 판정하는 2안은 넣지 않는다(§5).
- **G0 정지 재개**(R-3519)는 이미 BC 무변을 확인한 뒤 `check-verdict` 를 다시 돌린다. exit 0 이면 그 자리에서 확정 표가 생긴다.
- **현장** [실측]: `refactor_audit.py` 는 어느 core 릴리즈에도 없다(태그 `dddjango--v*` 61개 전부 · 최신 v2.18.4 미포함). web 도 `dddjango-web--v1.1.24`·`v1.1.25` 에 없다.
  - 그래서 설치본은 refactor audit 을 만들 수 없고, 진행 중 레인(G1~G2) 영향은 0 이다.
  - 옛 폴더는 scratch 리허설 산출물(R8-R · R8-R2)뿐이다.
  - 보강 조회(리뷰 core n1): `spring_dream_server` 워크트리 11개 모두 audit·`모드 리팩토링` 0 이다.

### 1.5 문면 — graph-owned 1 규범

| 대상 | 변경 |
|---|---|
| `ontology/rules/command-dddjango.ttl` R-3517(블록 s012/b2 · `dddjango.md:227`) | rev2 · `revision-amendment` · 새 Expression `R-3517@<구현일>`(wasRevisionOf `@2026-09-27`) |
| 블록 문구 | «그 실행의 `verdict.md` 를 그대로 쓰며(M 목록 동결)» → «그 실행의 `verdict-final.md`(`check-verdict` exit 0 판의 확정 표 — `verdict.md` 는 architect 원문이다)를 그대로 쓰며(M 목록 동결)» |
| prefLabel | «(verdict 동결·…)» → «(verdict-final 동결·새 빚은 R1 분만)» |
| 딸린 작업 | rdflib+canon(왕복 byte 동일) → `ontology_gate.py`(90/90) → `ontology_render.py --apply command-dddjango`(1줄) → LEDGER `command-dddjango s012` 1행 → ExpressionShape 3811→**3812** → `make rulepack`(core·Codex) [모두 실측] |
| Codex 의미 미러 | `codex-dddjango/skills/dddjango/SKILL.md:243` 같은 치환. core :227 과 줄이 같다 [실측 diff 0] |
| byte 미러 | `codex-dddjango/skills/dddjango/scripts/refactor_audit.py` |

- 새 채번은 없다. q4 골든은 verify-ontology 가 green 이라 `--emit` 하지 않는다 [실측].
- 바꾸지 않는 문면: R3(:237 · architect 가 쓰는 문장) · G0(:241 · 로그 마지막 exit 0 판 = 확정 표와 같은 내용) · G0 정지 재개(:229) · `design-architect.md:122` · web.
- web R3 처럼 «확정 표 = 소비자 M 목록» 대칭 문장을 core R3 에 두는 것은 넣지 않는다(§5 · 리뷰 core n3 선택).

### 1.6 시험 — `workspace/tools/refactor_audit_fixture_run.py`

기존 사례 적응

- `_res_folder(..., confirm=True)`: 판정 표를 쓴 뒤 `check-verdict` exit 0 으로 확정 표를 만든다. E2 계열 4곳은 `confirm=False` 로 두고 스스로 돈다.
- E2-0: «로그 없음 → M4 판정 없음 red(2)» → **«verdict-final.md 없음 → 실행 불능(1)»**.
- x3: «결정적 잔존 1» → **«결정적 잔존 0 · 리뷰어 1 · `(병합 M2)`»**(§1.2-4).
- E2-7 · mi1 x4·x5 · mi-B 는 그대로 green 이다 [실측].

새 사례 `final_cases`

| ID | 입력 → 뒤 | 기대 |
|---|---|---|
| F1 새 번호 | M1 만 판정 · 통과 행 2 → `--final` 이 M2 · `M1, M2` ⓐ | resolution red 0 · `렌즈 ddd: M1 · M2` · residual 결정적 잔존 1 · 리뷰어 1 |
| F2 번호 중복(fail-open) | `M1 #1(P)` · `M1 #2(C)` → M1 #1 · M2 #2 · `M1` ⓐ | M_m=1 · exit 2(residual 한 번 호출) |
| F3 렌즈 | `M1 ddd#1` · `M1 discipline#1` | `렌즈 ddd: M1` · discipline 없음 |
| F4 병합→채택 | M3 제외(red) · M4 병합→M3 → 둘 다 채택 · `M3` ⓐ | M_m=1 |
| F5 원 행 두 번 | M1 #1(C) · M2 #1·#2(P) → M2 #2 | 결정적 잔존 1 · 리뷰어 1 · `### M2` 없음 |
| F6 통과 아닌 원 행 | M1 #1(P)·#2(인용 불일치) → M1 #1 | M_m=1 |
| F7 별도 요청 재분류 | exit 0(비 final) | 확정 표 `\| M1 \| ddd-01#1 \| 채택 \|` · verdict.md 원문 보존 |
| F8 exit 2 재실행 | F7 뒤 verdict.md 범주 밖 | exit 2 · 확정 표 byte 그대로 |
| F9 옛 폴더 | 확정 표 삭제(`unlink(missing_ok=True)`) | residual exit 1 · 안내 → 짝: BC 되돌림(무변) 뒤 `check-verdict` → M_m=1 |
| F9′ 옛 폴더 + BC 변경 | 확정 표 삭제 + 원 행 파일(policy.py) 축소 | residual exit 1 · «바뀌었으면 다시 돌리지 않고 멈춘다» |
| F10 고아 병합 | #1(C) · #3(인용 불일치) · #4(P) · `M1 채택 · M3 #3 채택 · M4 #4 병합 → M3` → `--final` | 확정 표 `\| M4 \| ddd-01#4 \| 채택 \|` · `병합 → M3` 없음 · 재분류 줄 |
| F11 이스케이프 | `M1 \| … \| 채택 \| 근거 a \\| b \| <P> [ⓓ#644]` · P 변경 | residual exit 1 «ⓓ 겹침 항목»(--candidates 요구) |

- [실측] 199 → **213 ✓**(새 14 · 적응 2).
- HEAD 도구를 같은 러너로 돌리면 E2-0 · x3 · F1~F10(F9 짝 제외)이 red(14)다. F11 은 HEAD 가 verdict.md 를 바로 읽어 green 이다. 러너는 끝까지 돈다.

### 1.7 변이 [실측 — 작업 트리 사본 9개 병렬]

| 변이 | red |
|---|---|
| V1 소비자가 verdict.md 를 읽음 | 8(x3 · F1~F6) |
| V2 확정 표에 원 판정을 씀 | 9(F1~F7 · F10) |
| V3 exit 2 에서도 씀 | 1(F8) |
| V4 확정 표 없으면 verdict.md 로 대체 | 3(E2-0 · F9 · F9′) |
| V5 `_scope` 를 8c 이중 판독으로 되돌림 | 1(x3) |
| V6 대상 조건 제거 | 3(x4 · x5 · mi-B) |
| V7 칸 이스케이프 제거(NOESC) | 1(F11) |
| V8 고아 병합 5행 제거 | 1(F10) |
| V9 안내문을 무조건 재실행으로 | 1(F9′) |

## 2 ②-A web — 경계 교차 소비자 분류

### 2.1 코드 (`dddjango-web/scripts/refactor_audit.py` `compute_plan` :685-696 · Codex byte 미러 · +4/−3 [실측])

```python
            where: str = f"{path}:{line}"
            load: bool = bool(LOAD_LINE.search(text))
            if CONSUMER_LINE.search(text) or not load:      # 정적 로드 줄(<script>·<link>)만 빼고 모양과 무관
                data.consumers.append(where)
            if load:
                data.line_edits[where] = "(가)"
```

- 새로 소비자가 되는 것
  - import 전 모양 · 점 경로 문자열·`importlib` · 다른 영역의 `render(…)`.
  - 주석 줄 · 비로드 HTML 참조(`<img>`·`{% static %}`) · 컨테이너 줄(`web/urls.py`).
- include·extends 는 전과 같다. `web/` 밖 적중은 `outside_refs` 그대로다.
- 편집 허용(`in_scope`)과 check·check-verdict 판정은 소비자를 읽지 않는다. `Plan`(:983-1015)도 읽지 않는다. 목록이 늘기만 하므로 새 fail-open 은 없다(리뷰 web 총평 [실측]).

### 2.2 결정

- **정적 로드 전용 줄 제외**(사용자 범위의 «LOAD_LINE 이 아니면»)
  - 영역 단위에서는 이 갈래가 출력을 바꾸지 않는다. 범위 안 정적 파일은 «영역 전속»이기 때문이다.
  - **정적·컨테이너 단위에서는 출력을 정한다**(현장 제외 삭제 시 `static/css` 0→17 · `static/js` 5→33 · `web/*.py` 353→399 — 리뷰 web m1 [실측]).
  - 제외해도 안전한 까닭: 로드 전용 줄은 소비자가 아니라 줄 편집 (가)로 영향 화면에 든다. Phase 2 진입의 «영향 화면(… 줄 편집 페이지)»(`dddjango-web.md:304`)과 G2 시각 대조(`:308`)가 그 페이지를 포함한다.
  - R1·R1′ 로 고정한다(제외 삭제 변이 MNL → R1′ red [실측]).
- **모양 표지를 달지 않는다**
  - 분류 정규식이 틀리면 새 실패면이 된다.
  - 화면이 없는 소비자(`web/urls.py` · DS 컴포넌트 · CSS/JS 주석 · 컨테이너 파일)가 영향 화면을 넓히는 쪽은 비용만 드는 fail-safe 다. 관찰 뒤 판단한다(§5).
- **문면 변경 없음**
  - 소비자 목록을 쓰는 문면은 `dddjango-web.md:290` · `:296`(«경계 교차 소비자 페이지는 G2 영향 화면») · `:304` · `:308` 과 Codex `:315` · `:321` · `:329` · `:333` 이다. 모양을 정의하는 문면은 Claude·Codex·에이전트·스킬 어디에도 없다(리뷰 web n3 grep).
  - 설계 v5 §3-3 «include·extends»는 이 문서가 대체한다. v5 는 역사 문서라 고치지 않는다.

### 2.3 호환

- 수리 전 plan.md 로 `plan --against`(G0 정지 재개)를 하면 «다름 경계 교차 소비자» exit 2 → 새 점검이다(fail-closed · 비용 R2·R3) [AQ6].
- 설치본에 도구가 없으므로(§1.4) 현장 영향은 없다.

### 2.4 시험 — `fixtures_refactor_audit.sh` (②-A 커밋 몫)

- **A′ 절(A11 뒤)**
  - 기존 프로젝트: A12 `chart_view_model.py:1`·`:2` 소비자 · A12′ 같은 줄은 (가) 아님. 절 추출 도우미는 `PSEC`(HEAD :600 `SEC` 과 겹치지 않게).
  - 모양 표본 프로젝트 Q(진단 `mini/` 14 모양 + `tests/` 적중 + 한글 주석 줄 + client 모듈): AQ0 `소비자 12`.
  - AQ1 × 9: Python·문자열 모양이 소비자다.
  - AQ2·AQ2′: include(+ (가)) · extends 다.
  - AQ3·AQ3′·AQ3″: 한계를 고정한다 — 상대 import · 동적 include · URL 이름은 미탐이다.
  - AQ4·AQ4′: `tests/` 적중은 `web/ 밖` 이지 소비자가 아니다.
  - AQ5·AQ6: 같은 트리 `--against` 는 같음이고, 옛 plan.md 는 «다름 경계 교차 소비자» exit 2 다.
  - AQ7(옛 D 판 AD1 을 옮기고 개명): 주석 줄(한글이 바로 붙은 점 경로)이 소비자다.
  - AQ8: client 단위 `web/client/users` 를 다른 영역이 import 한 줄이 소비자다(HEAD 0).
- **R 절(D 절 뒤 — 리뷰 보강)**
  - R1: 정적 단위 `plan web/static/js` 의 `<script src>` 로드 줄은 (가)다.
  - R1′: 같은 줄은 소비자가 아니다.
  - R2: `plan web/static/images` 의 비로드 `<img>` 참조 줄이 소비자다.
- [실측] 151 → **177 PASS**(새 26).
  - HEAD 도구는 15 red(A12 · AQ0 · AQ1×9 · AQ6 · AQ7 · AQ8 · R2).
  - 변이 VA(분류 되돌림) 15 red · MNL(제외 삭제) 1 red(R1′).

### 2.5 현장 회귀 [실측]

두 단위는 설계 실측이다(레인 사본 `field/` · HEAD plan.md = 레인 plan.md byte 동일 확인 뒤).

| 단위 | HEAD 소비자 | ②-A 소비자 |
|---|---|---|
| `web/home` | 없음 | `web/auth/login/view/login_view.py:18` · `web/urls.py:7` |
| `web/employee_choice` | 없음 | 영역 VM 6줄(chart · consultation · home · intake · preferences · related_persons) + `web/urls.py:13` |

25단위 전수는 리뷰 web m3 의 실측이다(`review-R8d-web/units/`·`unitsD/`). 소비자 절 밖은 모두 byte 가 같다.

| 단위 | HEAD 소비자 | ②-A 소비자(줄) | 화면 폴더 | 화면 없는 파일 |
|---|---|---|---|---|
| `web/*.py` | 0 | **353** | 12 | 20 |
| `client/accounts` · `media_library` · `place_directory` · `fortune_employee` | 0 | 56 · 15 · 10 · 9 | 12 · 5 · 4 · 3 | 0 |
| `client/` 나머지 5 | 0 | 3~6 | 1~2 | 0 |
| `design_system` | 158 | 163(+5 CSS·JS 주석) | 13 | 2 |
| `static/images` · `files` · `js` · `htmx` | 0 · 0 · 0 · 2 | 5 · 7 · 5(주석) · 4 | 1 | 1~2 |
| 영역 5개(auth · chart · intake · preferences · related_persons) | 0 | 1(`web/urls.py`) | 0 | 1 |
| `consultation` · `employee_choice` · `home` | 1 · 0 · 0 | 6 · 7 · 2 | 1 · 6 · 1 | 1 |

- **닫히는 공백**
  - client 단위는 HEAD 에서 소비자 0 이고 범위 페이지도 없어, G2 영향 화면이 통째로 비었다. ②-A 뒤에는 화면 1~12개가 잡힌다.
  - 정적 단위의 비로드 참조 줄은 HEAD 에서 어느 목록에도 없었다. ②-A 뒤에는 소비자가 된다.
- **과잉**
  - 컨테이너 단위는 루트 꼬리 `web`(`web/__init__.py`) 이 `-w` 로 모든 `from web.…` 과 주석 속 «web» 에 걸려 353줄이 된다. HEAD 에서도 (가) 46줄을 만드는 기존 소음이다.
  - 비용(수정 전 렌더 보존·전후 대조 화면 증가)만 드는 fail-safe 라 관찰 대상으로 둔다(§5-4).

## 3 D web — 꼬리 묶음 grep (별 커밋)

### 3.1 코드 (`dddjango-web/scripts/refactor_audit.py` · Codex byte 미러 · ②-A 판 대비 +48/−18 [실측])

| HEAD 행 | 변경 |
|---|---|
| :620-626 `_refs` | 클래스 `_Refs(project)` 로 |
| `warm(rels)` | 메모에 없는 파일의 꼬리를 모아 `reference_lines(경로 꼬리 전부)` 한 번 · `reference_lines(점 경로 전부, word=True)` 한 번. 파일마다 경로 꼬리는 `t[0] in 줄`, 점 경로는 `(?<![A-Za-z0-9_])<꼬리>(?![A-Za-z0-9_])` 로 나누고, 자기 자신을 빼고 정렬한다 |
| `__call__(rel)` | 메모에 없으면 그 파일만 `warm` |
| :629-650 `_owners` | 첫 인자 `project` → `refs: _Refs` |
| :653 `compute_plan` | 범위 첫 계산 뒤 `refs.warm(범위 ∪ (영역이면 static/ 전부))` · :721 앞 `refs.warm(targets)` · :668 지역 변수 `refs` → `lines` · :667·:687·:722 호출을 `refs(f)` 로 |
| :929-937 `_plan_names` 경로 쌍 | 구성원마다 grep 1~2회 → **쌍마다** 경로 꼬리 -F 한 번 · 점 경로 -F -w 한 번. 한 쌍의 표지(`경로 \`old\``)가 같아 분배가 필요 없다. `## grep 명령` 기록은 그대로다 |

- **git -w 와의 동등성**
  - git 의 낱말 문자는 ASCII 영숫자·`_` 이고, 0x80 이상 바이트는 낱말 문자가 아니다. 그래서 «앞뒤가 낱말 문자 아닌 출현이 하나라도 있다»와 같다.
  - Python `\w` 는 한글을 낱말 문자로 봐서 git 과 갈린다. 명시 ASCII 클래스가 필수다.
  - 리뷰 web [실측]: 현장 361 파일 전부에서 개별 `_refs` 와 `warm(전부)` 가 hit 4,705개까지 같았다. `-w` 퍼징(비UTF-8 포함)도 불일치 0 이었다.
- `src/debt.py` 는 바꾸지 않는다. backstop `--debt-scan`(기능 레인)과 공유하므로 영향 0 이다.
- 인자 길이는 grep 시간이 꼬리 수에 선형이다(56개 1.0초 · 2,000개 9.3초 — 리뷰 web n1 [실측]). E2BIG 은 정적 약 2.5만 파일부터이고 exit 1(fail-closed)이다. 나눠 돌리기는 넣지 않는다(§5).

### 3.2 `--names`

- `cmd_plan`(:889)은 `--names` 에서도 `compute_plan` 전체를 돈다. `_plan_names` 가 `data.scope`·`line_edits`·`keys` 를 쓰기 때문이다. 이 재계산은 그대로 둔다(D 뒤 2초 안).
- `_plan_names` 경로 쌍은 구성원마다 2회였다. 이제 쌍마다 -F 1회 · -F -w 1회로 묶는다.
  - 웹 리팩토링의 주력 교정(WS·WN 개명·이동)에서 폴더 쌍은 흔하다(리뷰 web M1).
  - `이름:` 쌍 grep 은 쌍마다 2회 그대로다.

| 현장 `plan web/home --names` [실측 · 단독 순차] | D(쌍 묶음 전) | D(쌍 묶음) | plan-names.md |
|---|---|---|---|
| 레인 명세(쌍 0) | — | 1.8초 | HEAD 와 같음(머리 시각 제외) |
| `경로: home/home/ → home/main/` + `이름:` 1 | 9.7초 | **3.1초** | 같음 |
| `경로: consultation/conversation/ → …`(구성원 28) | 19.6초 | **2.0초** | 같음 |
| `경로: consultation/` + `home/home/`(구성원 56) | 41.3초 | **3.2초** | 같음 |

### 3.3 시험 (D 커밋 몫)

- **Q 표본 추가**: 형제 모듈 `home_view_model2.py` 와 그 import 줄. AQ0 `소비자 12` → `13`.
- **A″ 절**
  - AD2: `_Refs` 분배 — `home_view_model.py` 몫에 한글 줄은 있고 형제 줄은 없다(W6-T5 `web.a.q`/`web.a.q2`).
  - AD2′: 형제 모듈 몫은 자기 줄만이다.
  - AD3: `GIT_TRACE` 로 센 plan git grep 이 4회 이하다(지금 2회).
  - AD4: 같은 트리 두 번 plan 이 byte 동일하다(결정성).
- **R′ 절(리뷰 보강)**
  - R3: Q 의 `debt_universe` 파일마다 `_Refs.warm(전부)` 와 개별 grep(-F · -F -w · 자기 제외)이 같다(전 파일 차등 대조). 판별 표본으로 경로 꼬리 주석 줄과 자기 점 경로 주석 줄을 넣는다.
  - R4: `--names` 폴더 쌍 (나) 에 `chart_view_model.py:1` 이 있다.
  - R5: `--names` 폴더 쌍 git grep 이 6회 이하다.
- [실측] 177 → **184 PASS**(새 7).
  - ②-A 도구로 돌리면 5 red(AD2 · AD2′ · AD3 · R3 · R5)다. 쌍 묶음 전 D 도구로는 1 red(R5)다.
- 변이 [실측]
  - VD1 `\w` 경계: AD2 · R3 red.
  - VD2 경계 없는 부분 문자열: AD2 · R3 red.
  - VD3 메모 무효: AD3 · R5 red.
  - MDa(.py 경로 꼬리 적중 버림): R3 red.
  - MDb(자기 제외 삭제): R3 red.
- **현장 사본** [실측 · `GIT_OPTIONAL_LOCKS=0` · 단독 순차]

| 실행 | HEAD | D(②-A 포함) | 동일성 |
|---|---|---|---|
| `plan web/home` | 58.8초 | **1.6초** | plan.md sha 같음(HEAD↔D-only · A↔A+D) |
| `plan web/employee_choice` | 59.1초 | **1.8초** | 같음(두 짝 모두) |

- 8개 병렬 부하에서 HEAD 274~280초 · D 16~20초였다.

## 3′ web 고아 병합 확정 금지 — core m2 의 web 짝 (별 커밋)

- **재현** [실측 — web 픽스처 G 판정 표에 `M9 | screen-01#6 | 병합 → M12` · `M12 | screen-01#2(인용 불일치) | 채택`]
  - `check-verdict` exit 2(«M12 원 행 … 통과 행이 아니다») → `--final` exit 0 → 재분류 «M12 원 행이 없는 판정 — 기록에서 뺀다».
  - 확정 표에는 `| M9 | screen-01#6 | 병합 → M12 |` 가 남는데, M12 는 없다.
  - 통과 행 #6 의 위반이 G0 질문에도 G2 확인에도 오르지 않는다(`mutlogs2/web-orphan-repro.log`).
- **수리**: web `_finalize_verdicts` 끝(:1516-1517)에 core 와 같은 모양의 5행을 둔다. 대상 판별은 web 관례대로 `re.fullmatch(r"M\d+", v.merge_to)` 다. 검사기 키 병합은 대상이 M 이 아니라 해당 없다.
- **시험**: K 절 끝 K6(재분류 줄 «M9 병합 대상 M12 이 확정 기록에 없다 → 채택») · K6b(확정 표 `M9 = 채택` · `병합 → M12` 없음).
  - [실측] 184 → **186 PASS**. 수리 전 도구 2 red. 변이 VO(5행 무효) 2 red.

## 4 커밋 단위

| 순서 | 커밋 | 내용 | 픽스처 [실측] |
|---|---|---|---|
| 1 | **① core** `fix(refactor-audit): check-verdict 확정 표 verdict-final.md — core 소비자가 --final 재분류를 따른다 (로드맵 8d ①)` | 도구(+ 조건부 안내 · 고아 병합 5행) + Codex byte · 픽스처 러너(F1~F11 · 적응) · ttl · md 재투영 · LEDGER 1 · target-counts · rulepack ×2 · Codex SKILL.md | core 213 ✓ |
| 2 | **chore 봉인** | `manifest_seal.py --write`(① 파일만 — web 은 봉인 글롭 밖) | — |
| 3 | **②-A web** | 도구 + Codex byte · 픽스처(A′ 절 · R1·R1′·R2) + Codex byte | web 177 |
| 4 | **D web** | 도구(`_Refs` · `_plan_names` 쌍 묶음) + Codex byte · 픽스처(Q 형제 표본 · A″ · R′ 절) + Codex byte | web 184 |
| 5 | **web 고아 병합** `fix(refactor-audit-web): 고아 병합 확정 금지 — --final 이 대상을 빼면 병합 항목은 채택` | 도구 + Codex byte · 픽스처 K6·K6b + Codex byte | web 186 |

- ① 커밋 절차: **«① 적용 + 재봉인한 작업 트리에서 `make verify` green → ① 커밋 → 봉인 커밋»**(8c `a34e93db`→`ea0526f9` 와 같다). 봉인은 커밋 직전 마지막 쓰기다.
- web 커밋 3~5 는 각 커밋 전 `make verify-web` green 을 확인한다. web 파일은 봉인 대상이 아니다.
- 묶지 않는 근거
  - ① 과 web: 플러그인과 릴리즈 시리즈가 다르고(`make release` / `make release-web`), 봉인 대상 여부도 다르다.
  - ②-A 와 D: 사용자 결정대로 별 커밋이다. D 의 byte 동일 기준이 ②-A 판이라 ②-A 가 먼저다.
  - web 고아 병합: ②-A·D 와 뿌리가 다르다(check-verdict 기록 무결성). core m2 와 짝이지만 플러그인이 다르다.

## 5 범위 밖 (기록만)

1. **`--final` 뒤 G0 정지 재개 불가**(core :229 · web :286): 비 final 재실행은 항상 exit 2 → 새 점검이다(fail-closed · 비용). 후보는 «`verdict-final.md` 있음 + audit 무변»으로 재개하는 것이다.
2. 손으로 고친 `verdict-final.md`(중복 M 등)는 검출하지 않는다. web 과 같다. 쓰는 곳이 도구 한 곳이다.
3. ②-A 뒤 남는 미탐: 상대 import(현장 0) · 동적 include · URL 이름 참조. AQ3 로 고정한다.
4. 모양·«화면 없음» 표지와 진단 안 C(영향 화면 후보 절 · 화면 폴더로 올리는 전이 사상)는 관찰 뒤 다룬다.
   - 관찰 대상: 컨테이너 단위 루트 꼬리 `web` 소음(0 → 353줄 · 사실상 전 파일)과 화면 없는 소비자(`web/urls.py` · DS 컴포넌트 · CSS/JS 주석).
5. core 의 BC 밖 소비자(설계 v3 B-M4(a) 보류)는 그대로다.
6. core m1 2안: 도구가 `plan.md` HEAD 대비 `git diff --quiet`·미추적 0 을 직접 판정하는 것은 넣지 않는다. 안내문(1안)으로 막는다.
7. core R3 에 web R3(md:292)의 «확정 표 = 소비자 M 목록» 대칭 문장을 두는 것은 넣지 않는다. Phase 1 파견 M 목록·G0 목록 파일의 출처 명시는 HEAD 와 같은 공백이다(리뷰 core n3 선택).
8. web n1: `warm` 바늘 5,000개 나눠 돌리기는 넣지 않는다. 현장 361 파일이고, E2BIG 은 정적 약 2.5만 파일부터이며 exit 1(fail-closed)이다. 규모 가정일 뿐이다.
9. web n2: ②-A 뒤 소비자 항목에 import·주석·문자열 줄이 들어가 `--against` 재개가 더 민감해진다. G0 정지 중 다른 단위 윗줄이 바뀌면 새 점검이다(fail-closed · 비용) [추정].
10. 공유 파서 결함: 파일 이름에 `:` 가 든 파일이 꼬리에 적중하면 `reference_lines` 의 `raw.split(':', 2)` 가 실패해 exit 1 이다. HEAD 와 D 가 같다(리뷰 web `colon/` [실측]).
11. **릴리즈 창**: ① 은 `dddjango/scripts/` 를 바꿔 pre-gate digest 를 낡게 한다. 진행 중 G1~G2 레인 착륙 뒤 `make release` 한다(DEVELOPMENT §6). web 커밋은 `make release-web` 이다.

## 6 실측 로그 (scratch `r8d/`)

- core 픽스처
  - `base-core.log`(HEAD 199) · `p1-core.log`(1차 210) · `p1b-core.log`(리뷰 반영 213).
  - `mutlogs2/core-HEADTOOL.log`(14 red · 끝까지 돎) · `mutlogs2/core-V1~V9*.log`.
- web 픽스처
  - `base-web.log`(151) · `mutlogs2/web-A2-on-A.log`(177) · `web-A2-on-head.log`(15 red) · `web-D2-on-ADN.log`(184) · `web-D2-on-A.log`(5 red) · `web-D2-on-AD.log`(R5 red) · `web-O-on-ADNO.log`(186) · `web-O-on-ADN.log`(2 red).
  - 변이: `web-O-mut-{VA,MNL,VD1,VD2,VD3,MDa,MDb,VO}.log`.
  - 재현: `web-orphan-repro.log`.
  - 조립·실행 스크립트: `build_web_fx.py` · `run_web_matrix.py`.
- 현장
  - `out/`(plan.md 8벌 · 순차 `t-*` · `--names` `n-*`).
  - `timeit.py` · `timenames.py`(명세 `nspec/` — 리뷰 web `names/` 사본).
- verify(최종 판: ① + 재봉인 + web 셋)
  - `verify-2.log`: 5/5 green(core 70초 · ontology 81초 · backstop 112초 · cross 235초 · regen 344초 — regen 안 refactor_audit 픽스처 PASS).
  - `verify-web-2.log`: EXIT 0 · refactor_audit 186/0 · Codex byte 미러 무차이.
  - 1차 판 기록: `verify.log`(재봉인 전 base-core 봉인 14건 RED) · `verify-core-2.log`(재봉인 뒤 green) · `verify-web.log`.

## 7 열린 쟁점

- 없음. 리뷰 두 건도 «사용자 판단 쟁점 없음»이다.
  - x3 기대 반전은 G0 계약에서 답이 나온다.
  - 안내문 1안, 고아 병합 채택, `--names` 쌍 묶음은 ① 과 D 의 목적(확정 표 한 출처 · fail-closed · `--names` 120초)에서 답이 나온다.
  - 표지 생략과 컨테이너 소음은 fail-safe·관찰 원칙으로 처리한다.

## 8 리뷰 처분 (09-30 · 운영 세션)

| 리뷰 | 항목 | 등급 | 처분 | 반영 위치 |
|---|---|---|---|---|
| core | m1 옛 폴더 회복 안내가 Phase 2 뒤 G0 확정 표를 바꿈 · [추정] 오류 | minor | **채택(1안)** — 조건부 안내문 · 시험 F9′(+ 변이 V9) · [추정] 줄을 «코드 무변일 때만 결정적 [실측 7/7] · Phase 2 뒤엔 다르다 [실측]»으로. 2안 불채택 | §1.1 · §1.4 · §1.6 · §1.7 · §5-6 |
| core | m2 `--final` 고아 병합(HEAD 같음) | minor | **채택** — core `_finalize_verdicts` 5행(리뷰 «6행» · ① 커밋) · F10 + V8. web 같은 코드: **재현됨 [실측]** → 같은 모양 수리를 별 web 커밋으로 · K6·K6b + VO | §1.1 · §1.3 · §1.6 · §1.7 · §3′ · §4-5 |
| core | m3 칸 이스케이프 무시험 · ⓓ 가드 우회 | minor | **채택** — F11(`\|` + ⓓ) · V7 NOESC | §1.3 · §1.6 · §1.7 |
| core | n1 현장 근거가 시점에 묶임 | nit | **채택** — «refactor_audit.py 는 어느 릴리즈에도 없다(v2.18.4 미포함)» [실측 태그 61개] | §1.4 · §2.3 |
| core | n2 F9 `unlink` 예외 · F2 이중 호출 | nit | **채택** — `unlink(missing_ok=True)` · F2 한 번 호출 · F9 짝을 BC 무변으로 | §1.6 |
| core | n3 §4 verify 순서 · web R3 대칭 문면(선택) | nit | **채택** — «① 적용 + 재봉인 작업 트리 `make verify` green → ① 커밋 → 봉인 커밋». 대칭 문면은 넣지 않고 기록 | §4 · §1.5 · §5-7 |
| web | M1 `--names` 폴더 쌍이 구성원마다 grep · §3.2 사실 오류 | major | **채택** — 쌍마다 -F 1 · -F -w 1(D 커밋) · R4·R5 · 현장 9.7~41.3초 → 2.0~3.2초 [실측] | §3.1 · §3.2 · §3.3 · §5(옛 6 삭제) |
| web | m1 정적 로드 제외 갈래 무시험 · §2.2 근거가 영역 단위에만 맞음 | minor | **채택** — §2.2 근거 고침(정적·컨테이너 단위 · (가) → :304·:308) · R1·R1′(MNL → R1′ red) | §2.2 · §2.4 |
| web | m2 D 동등성 시험이 경계 하나뿐 · 분배 변이 생존 | minor | **채택** — R3 전 파일 차등 + Q 판별 표본 두 줄(D 커밋) · MDa·MDb → R3 red · AD1 을 A′ 절 AQ7 «주석 줄 소비자»로 옮김 | §2.4 · §3.3 |
| web | m3 폭 측정이 두 단위뿐 · client·정적 공백 수리 효과 미기재 | minor | **채택** — 25단위 표 · §0 «client·정적 단위 공백도 닫힘» · §5-4 컨테이너 루트 꼬리 소음 관찰 · R2 + client 단위 AQ8(②-A 커밋) | §0 · §2.4 · §2.5 · §5-4 |
| web | n1 묶음 인자 길이(E2BIG) | nit | **기록만** — 나눠 돌리기 불채택(현장 361 · fail-closed · 가정 규모) | §3.1 · §5-8 |
| web | n2 `--against` 재개 민감도 | nit | **기록만** | §5-9 |
| web | n3 §2.2 인용 범위 | nit | **채택** — `:296`·`:308`(Codex `:321`·`:333`) 보강 | §2.2 |
| web | 범위 밖 관찰: 파일명 `:` 파서 결함(HEAD 같음) | — | **기록만** | §5-10 |
