# 로드맵 5 구현 기록 — dddjango 리팩토링 커맨드 (2026-09-27)

- 설계 정본 `step5-refactor-command-design-v5.md`(부록 C) · 계획 `step5-plan-v2.md`(부록 A) · 행동 시험 `behavior-tests-step5.md` · 구현 리뷰 `review-O-step5-impl.md`.
- 기준 HEAD `203cdffb`. 작업 트리에서 구현했다(브랜치 커밋 없음).

## 1. 무엇을 바꿨나

| 몫 | 내용 |
|---|---|
| 투영 | q4 `norm_kind`(FILTER 형) · `overrides` · 생성기 `blocks{h,n,works}`(설치본 `refactor_audit.normalize` 공유 — E8 본문 미동봉 유지) · SHACL `NormShape-overrides` |
| 도구 | `dddjango/scripts/refactor_audit.py`(plan · outline · check · sections · check-verdict · residual · self-test · 표준 라이브러리) · `behavior_guard.py close` 가 `map_items{pairs,dirs,fm}` 를 싣는다 · Codex byte 미러 · 봉인 pipeline 등재(도구·입구) · registry Checker 개체 · rulepack_smoke 명부 + G12 라벨 드리프트 · reverse_coverage 설명 |
| 러너 | `workspace/tools/refactor_audit_fixture_run.py` 54 사례(verify-base-regen) · `behavior_guard_fixture_run.py` +1 |
| 규범 | 신설 70(R-3509~R-3578) · 새 Expression 4(R-0186 · R-3226 · R-0096 · R-0836) · Coordinator 끝 절 «리팩토링 모드»(블록 12) + 모드 판별 문단(s004/b2) + 제자리 개정(C1~C12) · 적용 범위 Override **R-3526**(`djr:overrides` 56 · 몫 ⑴·⑵ · 어구 52) · 리뷰어 4 BC 점검 모드 절 · architect 의미 항목 판정 모드 절 · 에이전트 7 모드 무관 1행 · 사본 셋 정정 |
| 입구 | `commands/refactor.md`(Skill 위임 · `disable-model-invocation`) · Codex `dddjango-refactor/`(+ `policy.allow_implicit_invocation: false` — 0.157 바이너리 확인) · 매니페스트 2 · corpus-manifest · LEDGER prose · corpus_lint |
| 미러·문서 | Codex Coordinator·역할 SKILL 7 의미 미러 · parity 대조 절 +1(리팩토링 모드 — 마커 행 정규화 · 입구 표기 쌍) · REQUEST_GUIDE(§4 예외 · §6 리팩토링 · §7 대리) + byte 미러 · README · AGENTS · DEVELOPMENT |
| 계수·원장 | ISSUED +70 · 계수표(Block 2,970 · Expression 3,795 · Norm/Work 3,587 · Section 552) · q4 골든 3,578 · LEDGER 재기준선(절 단위 · ninja 소스 주소 이월 행) · 분류 문서 N 374 |

## 2. 구현 리뷰 O 처분 (수정 후 승인 · blocker 1 · major 3 · minor 12)

| # | 처분 | 위치 |
|---|---|---|
| B1 커밋된 `git mv` 를 «파일 무변»으로 | 고침 — `git diff --no-renames` · 러너 사례 | `refactor_audit.py` |
| M1 잔존 확인 묶음에 병합 행 누락 | 고침 — 원 행 전부 · «(병합 M<k>)» · 러너 | 같음 |
| M2 반대 방향 경로 제외 세탁 | 고침 — `_opposite_blocked` 를 사용자 판단·제외가 공유 · 러너(R-0180 형 red · R-1395 형 green) | 같음 |
| M3 G2 반송 뒤 증거 낡음 | 고침 — s012 G2 «반송이 코드를 바꿨으면 5번 감사·관련 테스트·전체 suite·6번 게이트를 다시 돈 결과만 G2 배너»(6′ 준용) · R-3536 명칭 | Coordinator + Codex |
| 논점 ① ⓓ 후보 R2 입력 | 채택 — discipline 렌즈 파견 입력에 R1 ⓓ 후보 행 · DR 산출에 `[ⓓ#N]` 표기(residual 의 ⓓ 겹침 갈래가 쓴다) | Coordinator b5 · DR s009 |
| 논점 ② 재측정 이월(m7) | 고침 — `--finalize` 의 해소 항목 파일 해시 스냅숏 · 무변이면 «해소 유지» | `refactor_audit.py` |
| 논점 ③ 반송 뒤 5번 감사 | M3 로 처분 | — |
| m1 없는 절 토큰 | 고침 — 인용 불일치(절 없음) | 도구 |
| m2 칸 부족 행 무언 삭제 · `..` 탈출 | 고침 — 인용 불일치(칸 부족) · normpath | 도구 |
| m3 대상 없는 병합 · `--final` 종료 | 고침 — 범주 밖 red · `--final` 이 무판정 통과 행도 채택 기록 · Coordinator b7 문면 | 도구 + Coordinator |
| m4 대리 판정 fail-open 2갈래 | 고침 — 출처 값 머리로 판정 · 앞 exit 0 뒤 `--feedback` 없는 축소 red | 도구 |
| m5 해소 근거 범위 · docstring | 고침 | 도구 |
| m6 `[ⓓ#N]` 표기 경로 부재 | 논점 ① 로 해소 | — |
| m8 G0 목록 출처 | 고침 — `verdict-log.md` 마지막 exit 0 판 | Coordinator b9 |
| m9 트리 밖 조각 문턱 | 고침 | 도구 |
| m10 Codex 동형 R-T0 | 실행 — R2 파견 직전까지(15분 상한) · 기록 정정 | `behavior-tests-step5.md` |
| m11 문면 nit | 고침 — DR «명시가 없으면 따르지 않는다» · «slug 가 `refactor-` 로 시작하는» · reverse_coverage 입구 설명 · 에이전트 frontmatter description 은 두었다(호출은 `subagent_type` 명시라 동작 무관) | graph + 도구 |
| m12 릴리즈 메모 | 로드맵 9 메모 — 설치본 갱신 뒤 표지 없는 «정리만» 발주는 입구 정지(REQUEST_GUIDE §6 · 대리는 표지 줄) | `progress.md` |
| `docs/work_flow.html` | 이번에 갱신하지 않는다 — 로드맵 3·4·5 누적분을 로드맵 9 릴리즈 전 한 번에 재생성(설계 §8 행의 편차) | — |

## 3. 계획 대비 편차

- 새 절 예외로 처리한 설계 제자리 지점 6곳(`:22·24·35·94·116·117`)과 C1 우선 규칙 — 계획 v2 §1-1 대로.
- 행동 시험 R-T0 는 `-p` 턴 종료로 백그라운드가 끊겨 `--resume` 두 번으로 이었다(둘째 구간 계정 세션 한도 429 → 리뷰어 5건 재파견). R-T14 는 결정적 몫만 재고 토큰은 R-T0 에서 외삽했다(계획 v2 §6 축소 그대로).
- 행동 시험·구현 리뷰 뒤 문면 보정 두 차례(render 5 doc · 2 doc) — LEDGER 재기준선 행으로 남겼다.

## 4. 검증

- 러너 `refactor_audit_fixture_run.py` PASS(54 · Claude 결속 1,836/1,836 · Codex 기록 · self-test 두 런타임) · `behavior_guard_fixture_run.py` PASS · `rulepack_smoke` 15/15 · `--mutation-test` 12/12 · parity 2절 · corpus 11/11 · render-sync·ledger·issued·structural·query-golden green · `claude plugin validate dddjango --strict` 통과.
- `make verify` · `make verify-mutation` · 봉인 · 커밋 결과는 `evidence/verify-2026-09-27-step5.log`.
