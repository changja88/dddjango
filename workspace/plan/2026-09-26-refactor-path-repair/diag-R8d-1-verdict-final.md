# 진단 — core verdict 소비자의 --final 재분류 누락 (2026-09-30)

> 진단 서브에이전트 결과를 운영 세션이 옮겨 저장(사용자 결정 09-30 10시대 «둘 다 지금 진단 (권장)»).
> 기준: 착수 시 main HEAD `144e25e9`(8c 전), 진단 도중 8c 가 `a34e93db` 로 커밋됨. 두 판 모두 scratchpad 사본에서 돌렸고 결과는 모든 사례에서 같았다. 행 번호는 `a34e93db` 기준.
> 실험 폴더: scratchpad `diag-origins/`(`h.py` · `t_all.py` · `t_lens.py` · 원형 수리 `repo/dddjango/scripts/fix_ra.py` · `fx-8c.log` · `fx-fix2.log`). 저장소 파일은 고치지 않았다.

## 0 요약
- `check-verdict` 는 재분류 결과를 `verdict-log.md` 에만 남긴다(`--final` 의 채택 전환·새 번호·중복 번호 교체·원 행 제거, `--final` 없이 exit 0 으로 끝나는 «별도 요청 → 채택»). core 의 `resolution`·`residual`(과 8c `_scope` 의 병합 대상)은 원본 `verdict.md` 를 읽는다.
- (a) 실행 불능(fail-closed) [실측]: `--final` 이 새 번호를 준 M 을 ⓐ 로 두면 G1 `resolution` 과 G2 `residual` 이 «ⓐ 항목 M2 이 verdict.md 에 없다» 로 멈춘다. 문서화된 복구 경로가 없다.
- (b) 틀린 판정(fail-open) [실측]: M 번호가 중복되면 dict 적재에서 뒤 행이 앞 행을 덮어, M1 이 M2 의 원 행으로 잔존 확인을 받는다. 파일 무변으로 걸러야 할 결정적 잔존을 건너뛰고 정직한 리뷰어의 «해소»만으로 M_m=0.
- 병합 재분류·원 행 중복·통과 아닌 원 행에서도 결정적 바닥이 사라지고 묶음에 남의 행이 섞인다 [실측]. `resolution` 렌즈 배정 오류도 실측.
- 빈도: 리허설 4레인에서 `--final` 0회 · 재분류 0건. 현장에는 리팩토링 audit 커밋 0건(배포 전).
- 권장: web 처럼 exit 0 판을 `verdict-final.md` 로 쓰고 core 소비자가 그것을 읽는다. 원형 도구 변경 33행 · 5 사례 모두 옳음 · 기존 픽스처 198/199.
- 판정: **major** · 배포(로드맵 9) 전에 고칠 가치가 있다.

## 1 소비자 목록
| 파일:행 | 소비자 | 읽는 것 | `--final` 을 알아야 하나 |
|---|---|---|---|
| `dddjango/scripts/refactor_audit.py:1001-1006` | `_load_verdicts` | `verdict.md` 고정(:1003) | 적재기 — 호출자가 결정 |
| `refactor_audit.py:1248` | `cmd_check_verdict` 입력 | `verdict.md` | 아니다(검사 대상은 원문) |
| Coordinator `dddjango.md:229` «G0 정지 재개» | `check-verdict` 재실행 exit 0 이면 재사용 | `verdict.md` | 부수 결함: `--final` 뒤 재실행은 항상 exit 2(실측 5/5) → 재개 불가 · R2·R3 재실행(비용 · fail-closed) · web(:286)도 같음 |
| `refactor_audit.py:1432-1436`(8c `_scope`) | 병합 차감 | 종류는 로그, `merge_to` 는 `verdict.md` | 부분적 — 번호 중복이 겹칠 때만 틀릴 수 있음(추정 · 드묾) |
| `refactor_audit.py:1514-1520` `_origins` | M → 원 행·병합 행 | `verdict.md` dict | **알아야 한다** — 새 번호면 실행 불능(:1518) · 중복 번호는 뒤 행이 이김 · 병합 재분류·원 행 제거 미반영 |
| `:1708` · `:1727` `cmd_resolution` | 렌즈별 M 목록(Phase 1 활성 렌즈·리뷰어 파견 목록 출처 · `dddjango.md:249`) | `_origins` | **알아야 한다** — 실행 불능 · 렌즈 틀림 |
| `:1848` · `:1864` · `:1865` · `:1874` `cmd_residual` | 항목 파일 · 결정적 바닥 · 묶음 · ⓓ 표식 | `_origins` · `verdicts[mid]` | **알아야 한다** — 핵심 결함 자리 |
| `dddjango.md:227` «잇기»(graph-owned · R-3516~3518 블록) · Codex `SKILL.md:243` | «그 실행의 `verdict.md` 를 그대로 쓰며(M 목록 동결)» | 산문 | **알아야 한다** — web 은 같은 자리에 `verdict-final.md`(web md:284) |
| `dddjango.md:241` G0 | 목록·계수 출처 = 로그 마지막 exit 0 판 | 로그 | 이미 반영 |
| Codex byte 미러 | 위 도구와 동일 | — | 함께 |

web 선례: `dddjango-web/scripts/refactor_audit.py:1157`(`VERDICT_FINAL`) · `:1165`(`_write_final`) · `:1587`(exit 0 일 때 쓰기) · `:1662`·`:1681`(residual 이 `verdict-final.md` 를 읽고 없으면 실행 불능).

## 2 재현
공통: 합성 프로젝트 → `check-verdict`(exit 2) → `--final`(exit 0) → 결정 줄 → 코드는 C(`thing_controller.py`)만 바꿈 → `resolution` → `residual` → 리뷰어가 전 항목 «해소 | C:7». 8c 전·후 같음.

| 사례 | verdict.md → `--final` 로그 | 결정 | 결과 | 옳은 결과 | 성격 |
|---|---|---|---|---|---|
| A 새 번호 [실측] | M1 #1 만 판정 → 로그 M1 #1 · **M2 #2(새 번호)** | M1·M2 ⓐ | `resolution`·`residual` 모두 exit 1 «M2 이 verdict.md 에 없다» | 정상 진행(M1 결정적 잔존 · M2 리뷰어) | fail-closed · G1 에서 멈춤 · 복구 경로 없음 |
| B 번호 중복 [실측] | `M1 #1(P)` · `M1 #2(C)` → 로그 M1 #1 · M2 #2 | M1 ⓐ · M2 ⓑ | M1 묶음에 M2 의 행 · 결정적 잔존 0 · 해소 답 뒤 **M_m=0 exit 0** | M1 은 P 무변 → 결정적 잔존 1(exit 2) | **fail-open** — 리뷰어가 정직해도 틀림 |
| B2 렌즈 [실측] | `M1 ddd-01#1` · `M1 discipline-01#1` | M1 ⓐ | `resolution` «렌즈 discipline: M1» | 렌즈 ddd | Phase 1 ddd 리뷰어가 M1 을 못 받음 |
| C 병합→채택 [실측] | M3 제외(근거 형식 red) · M4 병합→M3 → 로그 M3·M4 채택 | M3 ⓐ · M4 ⓑ | M3 묶음에 M4 행 · 결정적 잔존 0 → M_m=0 | M3 결정적 잔존 | 바닥 소실(틀린 해소는 리뷰어 오류에 달림) |
| D 원 행 두 번 [실측] | M1 #1(C) · M2 #1·#2(P) → 로그 M2 #2 | M1·M2 ⓐ | M2 묶음에 #1 · 결정적 잔존 0 → M_m=0 | M2 결정적 잔존 | 바닥 소실 |
| E 통과 아닌 원 행 [실측] | M1 #1(P) · #2(인용 불일치, C) → 로그 M1 #1 | M1 ⓐ | M1 묶음에 #2 · 결정적 잔존 0 → M_m=0 | M1 결정적 잔존 | 바닥 소실 |

- B 기제: `{v.mid: v for v in _load_verdicts(audit)}`(:1708 · :1848) — 중복 M 은 뒤 행이 이김, 로그는 앞 행을 M1 로 두고 뒤 행을 새 번호로 옮김 → 도구가 로그와 정반대 행을 M1 로 봄.
- C·D·E 기제: `files` 가 남의 행 파일까지 포함 → «변경 파일이 하나라도 있으면 바닥 없음»(:1875 부근)을 남의 파일 변경이 뚫음.
- 원형 수리(`fix_ra.py` · 8c 위에 web 방식 이식) [실측]: A 정상 진행 · B·C·E 결정적 잔존 1(exit 2) · D M2 결정적 잔존 + M1 리뷰어 — 5개 모두 옳음.

## 3 발생 빈도
- 리허설 산출물 4개 [실측]: `8-rehearsal/sds-R8-R`(채택 39 · 병합→M 10) · `8b-rehearsal/sds-R8-R2`(채택 27 · 병합→M 3) · web `sds-R8-WR` · `sds-R8-WR2` — 모두 로그 판 하나, 첫 `check-verdict` exit 0, `final ·` 0 · `재분류:` 0.
- 현장 `spring_dream_server`(git 읽기만): `.dddjango/**/audit/**` 0 커밋 — 리팩토링 모드는 현장에서 아직 한 번도 돌지 않음.
- 픽스처는 `--final` 을 `check-verdict` 단계에서만 시험(`refactor_audit_fixture_run.py:303`) — `--final` 뒤 `resolution`·`residual` 사례 0.
- 추정: `--final` 은 architect 가 두 번 연속 red 를 낼 때만 쓰이는 대체 경로. 가장 그럴듯한 재분류는 큰 표에서 통과 행을 빠뜨린 «판정 없는 통과 행 → 새 번호»(사례 A · fail-closed). B(fail-open)는 번호 중복이 재호출 뒤에도 남아야 해서 드묾.

## 4 수리안
**① web 방식 `verdict-final.md` (권장)** — exit 0 이면 `check-verdict` 가 확정 표 전체(원 행·판정·병합 대상·근거·파일:행)를 `verdict-final.md` 로 쓰고, `resolution`·`residual`·`_scope` 가 그것을 읽음(없으면 실행 불능).
- 도구: 원형 diff 33행 + Codex byte 미러 · 8c `_scope` 의 «로그 종류 × verdict.md 대상» 결합이 한 곳 읽기로 단순해짐.
- 픽스처 [실측]: residual 계열이 `verdict.md` 만 써서 실행 불능이 되므로 `Audit.verdict` 가 `verdict-final.md` 도 쓰게 하면 198/199 통과 · 남는 E2-0 은 기대를 «로그 없음 → 차감 없음» → «verdict-final 없음 → 실행 불능» 으로 · 새 시험 A·B·B2·C·D·E.
- 문면: `dddjango.md:227` «잇기» → `verdict-final.md` — graph-owned(R-3516~3518 블록) → ttl → render → rulepack · Codex `SKILL.md:243` · `:241` 은 출처 표기만 맞춤(선택).
- 위험: 진행 중인 수리 전 audit 은 `check-verdict` 를 한 번 다시 돌려야 함(현장 0건이라 실비용 거의 없음) · core·web 같은 모양.

**② 로그 합성** — 소비자가 로그 마지막 exit 0 표로 M 목록 구성. core 로그 표에 병합 대상·근거·파일:행이 없어 로그 형식 변경 + verdict.md 와 재조인 필요 — 그 조인이 바로 이번 결함이 깨뜨리는 곳이라 취약. 셋 중 위험 최대.

**③ `--final` 이 `verdict.md` 를 제자리 재작성(원본 `verdict-orig.md` 보존)** — 산문 «잇기»·G0 정지 재개까지 자동으로 맞으나, architect 산출물을 도구가 덮어씀(소유 경계 위반) · «verdict.md 원 판정을 따르지 않는다»(:241)·web 관례와 어긋남 · «별도 요청 → 채택» 재분류 별도 처리 · core·web 모양이 갈림.

**권장 ①.** `--final` 뒤 G0 정지 재개 불가 부수 결함(core·web 공통 · 비용만)은 별건 기록(예: 재개 판단을 «`verdict-final.md` 존재 + audit 무변»으로).

## 5 판정
- **major.** 가장 그럴듯한 경로(A)는 G1 에서 복구 경로 없이 멈춤 · 드물지만 fail-open(B) 실측 · C·D·E 는 결정적 바닥 무력화. blocker 가 아닌 이유: 관찰 빈도 0/4 · `--final` 자체가 architect 두 번 연속 red 뒤에만 쓰임.
- 의견: 배포(로드맵 9) 전에 고칠 가치가 있다. web 선례 이식이면 도구 약 33행 + 픽스처 1건 수정. 두면 첫 현장 `--final` 이 곧 실행 정지나 거짓 해소.
