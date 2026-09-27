판정: 수정 후 승인 — blocker 1 · major 3 · minor 12 — 설계·계획 커버리지와 ontology 연쇄는 성립하나 G2 잔존 도구가 커밋된 이동을 «무변»으로 오판하고, 반대 방향 경로의 제외 세탁 1갈래와 병합 행 누락이 남는다

# 로드맵 5 구현 독립 리뷰 O (2026-09-27)

- 대상: 작업 트리 미커밋 변경 전부(HEAD `203cdffb` 기준 · 새 파일 포함).
- 근거 문서: 설계 v5(부록 C) · `scope-limit-norms.md` · 계획 v2(부록 A) · `behavior-tests-step5.md` · `progress.md` 끝 행 · `step5-lens-sections.md`.
- 실험 위치: scratch `review-O/`(`exp_residual.py` · `exp_verdict.py` · `exp_opp.py` · `exp_check2.py` · `scan_*.py`). 저장소에 쓴 파일은 이 문서 하나다. `git status` 는 리뷰 전후가 같다 [실측].
- 표기: [실측] = 명령·실험 결과 · [추정] = 확인하지 않은 판단.

## 0. 검증 실행 결과 [실측]

| 항목 | 결과 |
|---|---|
| `make verify` | ontology · cross · backstop · regen **green**. core 는 **봉인 드리프트만** red(`manifest_seal --check --draft` — 봉인 write 전 예상 red) |
| core 에서 봉인 뒤에 막힌 단계(개별 실행) | `manifest_seal --self-test` M0 위양성 1(봉인 전 예상 · 로드맵 4 기록과 같다) · `ab_score --self-test` 5/5 · scripts byte 미러 `diff -rq` 일치 · REQUEST_GUIDE `cmp` 일치 · `request_guide_contract` self-test 157/157 · 본 검사 PASS |
| `make verify-mutation` | 12종 전건 red(M12 라벨 드리프트 포함) |
| `claude plugin validate dddjango --strict` | 통과 |
| 러너 `refactor_audit_fixture_run.py` | PASS(Claude 결속 1,836/1,836 · Codex 1,668/1,836 = 90% 기록 · N-OV Codex 결속 · self-test 두 런타임 red 0) |
| `runtime_parity_check` | 리팩토링 모드 절 정합(6,480자) · 6′ 정합 |
| render-sync · ledger · issued · structural · query-golden | 전부 green(그래프 소유 절 547 · red 0) |
| G12 라벨 드리프트 | 적중 332 · 미검토 0 |

## 1. 설계·계획 커버리지

| 설계 | 구현 | 판정 |
|---|---|---|
| §1-1 입구 | `commands/refactor.md` frontmatter 4키 · 본문 표지 · corpus-manifest 1행 · LEDGER prose · 봉인 pipeline 2파일 · Codex 얇은 스킬 + `policy.allow_implicit_invocation: false` | 성립 |
| §1-2 판별·단조성·fail-closed·축소 금지 | s004 C1(판별 입력 둘 · 단조성 · 표지 손상 정지 · 우선 규칙) · 모드 판별 문단의 따르지 않는 지시 | 성립 |
| §1-3 정리 요청 입구 정지 · ⓐ′ 안내 대상 | R-3470 · R-3473 · R-0204 | 성립 |
| §2 흐름·모드 기록·폴더·재개 | s012 b1~b3 · C5(실행 줄 `· 모드 리팩토링 · audit`) · G0 정지 재개(행동 시험 뒤 «미커밋 0»·평가 순서 보강) | 성립 |
| §3 BC_AUDIT · 도구 | 리뷰어 4 새 절 · 점검 절 목록 = 도구 상수(self-test 대조) · `refactor_audit.py` 6 하위 명령 | 성립 — 결함은 §2 표(B1·M1·M2·m1~m9) |
| §4 판정·적용 범위 | architect 새 절 · N-OV = **R-3526**(⑴·⑵ 문면 = 설계 문면 · 끝 2문장 가산) · `overrides` 56 = 표 1(58) − R-0186·R-3226 **전건 일치** · 어구 52 = 분류 A 40행의 어구 수와 같고 도구 상수 = 규범 문면(self-test 두 런타임) · 사본 셋 새 Expression(R-0186·R-3226·R-0096 `@2026-09-27` · `wasRevisionOf`) | 성립 |
| §4-4 에이전트 1행 7곳 | 7곳 모두 있음. architect·coder 는 «(리팩토링 모드면)» 항목 안에 붙어 있다(뜻은 같다 — nit) | 성립 |
| §5 G0 | 배너·질문 순서(C12)·결정 줄 정형(C11)·사용자 판단 위임 불가(:58·:218) | 성립 — 목록 출처 모호(m8) |
| §6 Phase 1~2 | :106(C6) · :114(C7) · 5번 조각 감사·홀리스틱·감사 입력(s012) · task 항목 | 성립 — 반송 뒤 증거 재실행 없음(M3) |
| §7 G2 | M_c · `residual` 층 판정 · 반송 1회 · 재상정 · 배너 다섯 목록 | 문면 성립 — 도구 결함 B1·M1·m5·m6 |
| §8 개정 지점 | 전부 반영. `docs/work_flow.html` 만 미갱신(§7 판단) | 성립 |
| §9 가이드 | §4 예외 · §6 리팩토링 소절 · 정리만 요청 안내 · 대리 표지 줄 · 사용자 판단 대리 불가 · byte 미러 | 성립 |
| §10 단위 시험 | 목록 전부 있음 | 빈틈: 커밋된 이동(B1) · 병합 행 재확인(M1) · 반대 방향 경로 세탁(M2) · 없는 절 토큰(m1) 사례 부재 |
| §10 행동 시험 R-T0 | Claude 격리 실하네스 합격 | **Codex 동형 1회 미실행**(m10) |
| 계획 «설계 편차» | `:22·:24`(R0′ 문면 «Phase 0 4번의 기능 폴더 목록·slug 규칙은 여기에 쓰지 않는다») · `:35`(task 항목) · `:94`(슬롯 한도) · `:116`(«마지막 홀리스틱 1회 존치는 이 형태로 채운다») · `:117`(감사 입력) · C1 우선 규칙 1문장 | 문면으로 성립 |
| 기능 모드 무변 | 의도된 변화만 있다: 정리만 요청 입구 정지 · ⓐ′ 안내 대상 · 폴더 목록에서 `refactor-` 폴더 숨김 · 둘 자리 질문 제외 대상 표기. 그 밖 개정은 전부 «리팩토링 모드» 한정 조건절이다 [실측 — 문장 단위 diff 18곳] | 성립 |
| Codex 의미 미러 | Coordinator 추가 문장 55 중 51 정규화 일치 · 나머지는 플랫폼 표기(`Read/Grep/Glob` ↔ 네이티브 도구 등) · 역할 SKILL 7 · 경로 사상 문면 | 성립 |

## 2. 결함

### Blocker

**B1. `residual` 결정적 바닥이 커밋된 이동을 «파일 무변»으로 판정한다**
- 위치: `dddjango/scripts/refactor_audit.py:1161`(`_git(project, "diff", "--name-only", anchor)`).
- 근거 [실측 `exp_residual.py`]: 0C 창처럼 `git mv` 를 커밋하면 `git diff --name-only <앵커>` 가 새 경로만 낸다(rename 감지 기본값). 옛 경로를 쓴 항목 M1 이 `잔존 | 파일 무변(build_anchor..작업 트리)` 로 떨어졌다. `behavior_guard.py:1003·:1236` 은 같은 이유로 `--no-renames` 를 쓴다.
- 영향: 순수 이동(0T 테스트 배치 정리 · 0C 파일트리 이동)으로 고친 항목이 리뷰어 확인 없이 전건 잔존 → 반송 → 또 잔존 → `ⓐ 재상정` STOP. 리팩토링의 가장 흔한 처치가 G2 에서 거짓 STOP 을 부른다. 러너의 이동 사례는 **커밋하지 않은** 이름 변경(삭제 + untracked)이라 이 결함을 가렸다(R-T11·R-T19 도 수정 픽스처).
- 고칠 것: `"diff", "--no-renames", "--name-only", anchor` 한 인자. 러너에 «커밋된 `git mv` 항목 → 결정적 잔존 아님(리뷰어 묶음)» 1사례.
- 원칙 필터: 도구 자체 단위 시험(예외) · 새 장치 없음.

### Major

**M1. G2 잔존 확인 묶음에 병합 행이 빠진다**
- 위치: `refactor_audit.py:1204~1206`(`for o in v.origin` — 병합된 행 `origin` 이 아닌 대상 M 자기 행만).
- 근거 [실측 `exp_residual.py`]: M3 «병합 → M2»(다른 파일·다른 규칙) — `residual` 은 M3 의 렌즈에 M2 를 배정하고 파일 집합에도 M3 파일을 넣지만, `review-ddd.md` 에는 M2 의 원 행만 실렸다.
- 영향: 병합된 위반은 G2 에서 아무도 다시 보지 않는다. 리뷰어가 M2 원 행만 보고 «해소»를 내면 병합 위반이 남아도 M_m 에서 빠진다(거짓 해소). R-T3 실측에서 병합→M 이 17행이었다.
- 고칠 것: 본문 루프를 `origin`(병합 포함)으로 바꾸고 병합 행에 «(병합 M<k>)» 표시. 러너 1사례.
- 원칙 필터: 새 장치 없음.

**M2. 제외 ③ 의 반대 방향 경로가 리뷰어 반대 방향 인용 문장의 한정 어구를 보지 않는다 — 세탁 통로**
- 위치: `refactor_audit.py:918~924`(`opp_ok` 뒤 한정 어구 검사는 architect 제외 인용의 문장만 본다).
- 근거 [실측 `exp_opp.py`]: 리뷰어가 반대 방향 규칙으로 R-0180 문장(«확립된 API 스택이 있으면 … 신규 표면의 스택 확정은» — 어구 «신규 표면»)을 적은 행에서
  - `사용자 판단` → red(«결정 18 이 가른 충돌») — 설계대로.
  - `제외 | R-0180 «lens는 관심사(계약·데이터의 유무)만 제안한다»`(같은 블록의 어구 없는 다른 문장) → **exit 0 · 제외 1**.
- 영향: 설계 §4-4 가 명시한 «R-0180·R-1645 문장은 제외·반대 방향 근거가 되지 않는다(N-m2)»가 제외 경로에서 뚫린다. 리뷰어는 «두 규칙이 반대 방향이면 두 문구를 모두 적는다»는 문면대로 확립 스택 조항을 반대 방향 열에 적기 쉽고, architect 는 그 R-ID 로 같은 블록의 무해한 문장을 인용해 채택 항목을 뺄 수 있다.
- 고칠 것(최소): 제외가 `opp_ok` 로만 서는 경우(종류 ∉ 허용·예외) `_user_judgment` 와 같은 검사를 리뷰어 반대 방향 인용에 건다 — N-OV 가 반대 방향 블록에 있거나, 그 블록이 대상을 품고 반대 방향 인용 문장에 어구가 있으면 red. 러너 1사례(R-0180 형).
- 원칙 필터: 기존 함수 재사용 · 새 장치 없음. (허용·예외 경로의 «R-ID ↔ 인용 문장» 불일치는 블록 단위 결속이라는 설계 수용 범위라 뺐다 — 끝 절.)

**M3. G2 반송 뒤 5번 이후 증거가 낡은 채 G2 배너로 간다 (행동 시험 논점 ③)**
- 위치: `commands/dddjango.md` s012 **G2** 문단 — «새 창을 열어 coder 에 1회 반송 → close → `residual` 재실행»뿐이다.
- 근거 [실측 문면]: 반송은 5번 감사·관련 테스트·전체 suite·6번 게이트 **뒤**의 코드 변경이다. `behavior_guard close` 는 테스트를 돌리지 않는다. 기존 규칙 «재생성이 코드를 바꿨으면 5번 이후 증거는 전부 낡았다 — 마지막 편집 뒤 … 모두 다시 실행한 결과만 7번 배너에 올린다»(6′)는 재생성 루프 한정 문면이다.
- 영향: G2 배너의 테스트 green·M_c(6번 게이트)·감사가 반송 전 코드 기준일 수 있다.
- 고칠 것: s012/b12 에 1구 — «반송이 코드를 바꿨으면 5번 이후 증거는 낡았다(6′ 규칙) — 반송 창 diff 의 5번 감사(조각 감사 판형)·관련 테스트·전체 suite·6번 게이트를 다시 돈 결과만 G2 배너에 올린다». graph 개정 → render → LEDGER → Codex 의미 미러.
- 원칙 필터: 기존 규칙 준용 · 새 장치 없음 · 테스트는 «있는 테스트를 다시 돌림»이라 강화·추가가 아니다.

### Minor

| # | 위치 | 근거 [실측] | 영향 | 고칠 것(최소) |
|---|---|---|---|---|
| m1 | `refactor_audit.py:727~729`·`:834` | 없는 절 토큰(`§99.9`·`§없는 절 제목`)이 문서 전체로 대체돼 `check` 통과 · `sections.md` 267 KB(ddd final 전체) | 설계 §3-1 ① «그 문서 §절 본문» 이탈 · R3 입력 비대 | 절 없음 → 인용 불일치(재인용 대상) |
| m2 | `:704~705`·`:737` | 칸 6개 미만 행이 **무언 삭제**(요약 «행 2» — 3행 중) · `application/demo/../other/…:1` 이 BC 안으로 통과 | «무언 삭제 금지» 위반 · BC 밖 위치 | 번호 행의 칸 부족 → 인용 불일치(형식) · 경로 `normpath` 뒤 접두 검사 |
| m3 | `:850~859`·`:1054~1060` | 대상 없는 `병합` → `IndexError` 역추적 exit 1 · `--final` 뒤에도 판정 없는 통과 행·중복은 exit 2 로 남는데 Coordinator 문면은 «`--final` 로 끝낸다»뿐 | R3 종료 조건 미정 | 대상 없는 병합 = 범주 밖 red · `--final` 이 판정 없는 통과 행을 채택으로 기록(로그 표) |
| m4 | `:891~897`·`:1047~1052` | ① 첫 줄이 «대리 … — 사용자 원문 없음» 이면 부분 문자열로 비대리 판정 → 채택 축소 통과 ② `--feedback` 없이 재실행하면 앞 exit 0 대비 축소를 보지 않는다 | 대리 축소 검사 fail-open 2갈래(Coordinator 누락 한 번으로 열림) | 출처 값 머리(`출처 = 본인 직접` · `출처 = 사용자 원문`)만 비대리 · 앞 exit 0 판이 있고 `--feedback` 이 없는데 채택이 줄면 red |
| m5 | `:1233~1236`·`:1215~1216` | «해소» 근거가 아무 실재 `파일:행`(무변 파일 `test_policy.py:1`)이어도 해소 · 리뷰어 대상이 남은 첫 호출은 결정적 잔존이 있어도 exit 0 | 설계 «새 `파일:행`» 미집행 · docstring «exit 0 = 통과»와 어긋남 | 근거 위치 ∈ 앵커 이후 변경(`--no-renames`) ∪ 대응 새 경로 · docstring 에 «미정 = exit 0 + `M_m 미정`» 명기 |
| m6 | `:1178` · 리뷰어 BC_AUDIT 산출 문면 | `[ⓓ#N]` 표기를 만드는 문면이 R2 입력·리뷰어 표·architect 판정 어디에도 없다 | 설계 §7 의 ⓓ 겹침 fail-closed 갈래가 사문 | §3 논점 ① 처분(R1 ⓓ 후보를 R2 입력에) |
| m7 | `cmd_residual` 재실행 | 반송 뒤 재실행이 이미 해소된 항목까지 다시 묶는다 | 재호출 비용 · 해소→잔존 뒤집힘이 반송을 받은 적 없는 항목을 곧장 재상정 STOP 으로 보낸다 | §3 논점 ② 처분 |
| m8 | s012 **G0** «목록 파일 경로와 건수» | 재분류(별도 요청 → 채택 · `--final`)는 `verdict-log.md` 표에만 있고 `verdict.md` 는 원 판정 그대로다 | G0 목록이 `verdict.md` 를 가리키면 채택된 항목이 «별도 요청» 목록에 보인다 | 1구: 목록·계수 출처 = `verdict-log.md` 마지막 exit 0 판 |
| m9 | `_chunks` `:555~556` | «트리 밖» 파일은 행 수와 무관하게 한 조각 | 평면 레거시 BC(모든 파일이 트리 밖)에서 5,000행 문턱이 무력. 현장 spring_dream 은 트리 밖 0행 [실측 git grep] | 트리 밖도 같은 문턱으로 쌓기 |
| m10 | `behavior-tests-step5.md` R-T0 | 계획 §6 R-T0 합격 문장에 Codex 동형 1회가 있는데 기록에 Codex 실행이 없다. «합격 20/20» 표기 | 기록상 거짓 green(스파이크가 기제는 확인 — 위험은 낮다 [추정]) | Codex 1회 실행하거나 R-T0 을 «Claude 합격 · Codex 미실행(사유)» 으로 정정 |
| m11 | 문면 nit | DR BC_AUDIT «기본 모드는 Phase 1 설계 리뷰다»(DR 은 모드 명시 필수 · Phase 1 은 lightweight) · Phase 0 «`refactor-` 로 시작하는 리팩토링 폴더»(폴더명은 날짜 prefix 로 시작 — slug 기준) · `reverse_coverage` 가 `commands/refactor.md` 를 «flow 정본»으로 설명(`:177~178`) · 리뷰어 4 frontmatter description 에 BC_AUDIT 없음 | 오독 여지 | 문구 정정(DR 은 «명시가 없으면 이 절을 따르지 않는다») · «slug 가 `refactor-` 로 시작하는» · 설명 분기 1행 |
| m12 | 릴리즈 메모(로드맵 9) | 표지 없는 «정리만» 발주는 새 판에서 입구 정지다 | 설치본 갱신 뒤 정리형 자율 발주가 첫 단계에서 멈춘다 | 메모 1행: «정리만 발주는 표지 줄로 — REQUEST_GUIDE §6» |

## 3. 행동 시험이 넘긴 논점 3건 — 판단

| 논점 | 판단 | 근거 |
|---|---|---|
| ① R1 의 대상 BC ⓓ 후보를 R2 파견 입력에 싣는가 | **싣는다 — discipline 렌즈 파견 입력에만.** 리뷰어 표 «위반 요지»에 같은 후보면 `[ⓓ#N]` 을 적게 하는 1구를 BC_AUDIT 산출 문면에 더한다 | ⓓ 후보는 R1(27종)이 이미 낸다 — 새 장치 없음. 설계 §7 의 ⓓ 겹침 갈래는 행의 `[ⓓ#N]` 에만 기대는데 지금 그 표기를 만드는 경로가 없다(m6). 200행 신호(R-3420 승격 감사)와 #11 후보는 discipline 몫이다. 예시 1 «큰 파일 분할»의 결정적 발견 보조다. 비용: 파견 입력 수십 행 |
| ② G2 재측정이 해소된 항목까지 다시 묶는 비용 | **이월한다**: 직전 `--finalize` 에서 해소였고 반송 창 diff(`--no-renames`)가 그 항목 파일·대응 경로를 건드리지 않았으면 해소를 유지하고 묶음에서 뺀다. 다시 묶는 것은 잔존·판단 불가였던 항목과 반송이 건드린 파일의 항목뿐이다 | 반송은 잔존 항목만 고친다. 해소 항목 재판정은 호출 수가 아니라 뒤집힘이 문제다 — 뒤집힌 항목은 반송을 받은 적이 없어 곧장 `ⓐ 재상정` STOP(거짓 STOP)이 된다. `residual` 안의 수십 행 변경이다 |
| ③ 반송 창 뒤 5번 감사 재호출 | **재호출한다** — M3 처분 그대로(기존 6′ «5번 이후 증거는 전부 낡았다» 규칙 준용 · 반송 창 diff 한정 조각 감사 판형) | 반송은 5번·6번 뒤의 코드 변경이다. 감사만이 아니라 관련 테스트·전체 suite·6번 게이트도 같이 낡는다 |

## 4. 봉인·커밋 준비

- 봉인 대상 [실측 `manifest_seal.py` GROUPS]
  - pipeline: `dddjango/scripts/refactor_audit.py` · `dddjango/commands/refactor.md` 등재됨.
  - plugin_payload: `codex-dddjango/skills/**/*.md|*.yaml` 이 새 Codex 스킬(`dddjango-refactor/SKILL.md` · `agents/openai.yaml`)을 덮는다(verify 가 «봉인 후 추가»로 잡았다).
  - Codex scripts 미러(`refactor_audit.py`)는 `script_trees[source-codex]` 가 덮는다.
  - 러너 `refactor_audit_fixture_run.py` 는 봉인 밖(behavior·pregate 러너 선례) — 계획대로.
- 6a 겹침 [실측]: `Makefile`·`AGENTS.md` diff 는 로드맵 5 hunk 하나씩뿐이고 `workspace/eval/web-g0-debt/` 는 문서만(untracked)이다 → 지금은 stash 불필요. 6a 가 먼저 착륙하면 계획 §7 규칙대로 한다.
- 순서: B1·M1·M2·M3(+ 채택한 minor) → 러너 사례 → `make verify`(core 는 봉인 드리프트만) → `make verify-mutation` → `manifest_seal.py --write`(마지막 쓰기) → `make verify` 5/5 → `evidence/verify-2026-09-27-step5.log` → feat 커밋 → 재봉인 chore 커밋.
- **넣을 것**
  - `dddjango/**`: `commands/{dddjango,refactor}.md` · `agents/*.md` 7 · `skills/discipline-houserules/references/final.md` · `skills/implementation-django-ninja/references/final.md` · `scripts/{refactor_audit.py,behavior_guard.py,rulepack.json}` · `.claude-plugin/plugin.json` · `REQUEST_GUIDE.md`.
  - `codex-dddjango/**`: `skills/dddjango/SKILL.md` · 역할 SKILL 7 · `skills/dddjango-refactor/`(SKILL.md · agents/openai.yaml) · scripts 미러 3 · final 2 · `REQUEST_GUIDE.md` · `.codex-plugin/plugin.json`.
  - `ontology/**`: `ISSUED` · `LEDGER.tsv` · rules 10 · wiring 9(registry 포함) · `shapes/djr-shapes.ttl`.
  - `workspace/tools/`: `ontology_rulepack.py` · `queries/q4-injection-order.rq` · `rulepack_smoke.py` · `reverse_coverage.py` · `manifest_seal.py` · `runtime_parity_check.py` · `corpus_lint.py` · `behavior_guard_fixture_run.py` · `refactor_audit_fixture_run.py`(신규).
  - `workspace/eval/fixtures/ontology_gate/target-counts.json` · `workspace/eval/fixtures/rulepack/query-golden.json` · `workspace/eval/ab/T2-0b-manifest.json`(봉인 write 뒤).
  - `workspace/reference/discipline-houserules/reference/final.md`(ninja 소스 미러는 09-11 source-address 이월 행 선례대로 무변 — `corpus_mirror_sync --check` green).
  - `workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv` · `workspace/design/ontology-adoption-map.html`(추가 1행 — 로드맵 5·6a 설계 행이 한 줄에 섞였다 · 6a 문구만 따로 커밋하려면 `git add -p`).
  - `Makefile` · `README.md` · `AGENTS.md` · `docs/DEVELOPMENT.md`.
  - 로드맵 5 문서 묶음(`workspace/plan/2026-09-26-refactor-path-repair/`): `diag-5{A,B,C}-*.md` · `morning-briefs-2026-09-27.md` · `review-{K,L,M,N}-*.md` · `review-P5-plan-v1.md` · `spike-5-entry-mechanics.md` · `step5-refactor-command-design-v{1,2,3-delta,4,5}.md` · `scope-limit-norms.md` · `step5-lens-sections.md` · `step5-plan-v{1,2}.md` · `behavior-tests-step5.md` · 이 문서 · `progress.md` · `evening-report.md` · 증거 로그.
- **뺄 것**: `docs/master.html` · `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` · `workspace/plan/2026-09-26-refactor-campaign/` · `workspace/plan/2026-09-26-request-guide-audit/synthesis-v2.md` · `workspace/eval/web-g0-debt/`(6a 몫).

## 5. `docs/work_flow.html`

- 이번 커밋에서는 갱신하지 않는다 — 로드맵 3·4·5 누적분을 로드맵 9 릴리즈 전 한 번에 재생성(archify 렌더 + 전수 DOM 검증 1회로 세 로드맵을 덮는다)하고, 계획 §5 행은 편차로 `progress.md` 에 적는다.

## 6. 뺀 권고 (원칙 필터)

| 권고 | 뺀 이유 |
|---|---|
| 제외 근거와 위반 규칙의 의미 관련성 검사(아무 허용·예외 규범이나 제외 근거가 된다 — R-T3 의 R-0506 ×2 형) | 재검토 N 이 이미 뺀 권고(설계 부록 C) · 결정적 판정 불가 |
| 허용·예외 경로에서 근거 R-ID 와 인용 문장의 대응 검사(R-0983 를 같은 블록의 다른 문장으로 인용하면 통과) | 설계 §3-1 «결속은 블록의 규범 집합까지» 수용 범위 · 규범별 문장 투영은 N 이 뺀 «규범별 원문 투영»과 같은 새 장치 |
| `_defines_model` 이 커스텀 베이스 모델(`AbstractBaseUser` 등 — spring_dream accounts 1건 [실측])을 못 봐 «모델 필드» 별도 요청이 채택으로 재분류 | fail-closed 방향 · 동작 불변 불가면 Phase 1 `ⓐ 재상정`(기존 장치)이 받는다 |
| «응답·예외 경로» 토큰 판정(`raise`·`errors` 등) 정밀화 | 리뷰어 «아니오 — 사유» 가 1차 관문 · 정밀 판정기는 새 장치 |
| Codex 결속률 90% 개선(의미 미러 원문 복원) | 설계 §3-1 이 뺐다(fail-closed · G0 ⓐ/ⓑ 가 사용자에게 보인다) |
| 사용자 판단 항목 상한 | 재검토 N 이 뺀 권고 |
| 대상 프로젝트 테스트 보강·새 테스트 실행 장치 | 사용자 원칙(기존 테스트 충분 가정) — M3 는 있는 테스트를 다시 돌리는 것이라 해당 없음 |
