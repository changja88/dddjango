# ⑥ 독립 감사 — 현장 보고(typecheck) 수리 · 브랜치 `fix/field-typecheck` (2026-09-03)

- 대상: HEAD `49741cd` · main `7e93b08`(merge-base) · 5커밋(036a874 · b2e1f42 · 33b0bd7 · 27342a3 · 49741cd) · 71파일 +8187/−3661.
- 방법: 저장소 무수정(읽기·`git`·스크래치 실행만). `make verify` 재실행(로그 `/tmp/djr-verify.pm8Zef` — 기존 `OW5m75` 부재) · 전/후 `git status --porcelain` 0행. 라이브 저장소 접촉은 검사기 실행만 · `DJR_FINDINGS_JSON=<스크래치>`로 sink 격리 · `.dddjango/violations` 목록 전/후 diff 0. mypy = spring `.venv` 2.3.1 · Python 3.14.7. 스크래치 `scratchpad/b3/rv6/`(`orig/`=main scripts 트리 · `live/` · `fx/` · `ev/` · `mypy/`).
- 심각도 어휘 = 배치 2 루브릭(BLOCKER 문제 불성립/품질 훼손 · MAJOR 근거 약함·수정 필요 · MINOR 표현·범위 · 검증됨).

## 0. 항목별 판정 표

| # | 항목 | 판정 | 요지 |
|---|---|---|---|
| 1 | 절차 준수 | **검증됨**(MINOR 미반영 3) | 게이트 ①→③→⑥ 3회·적대 리뷰 ①③⑤ 각 3기 산출 실재(rv1/rv3/rv5 A·B·C 9본). BLOCKER 3·MAJOR 19 전건 «반영 또는 명시 이월»로 닫힘(§1 표). ⑤ MINOR 중 3건은 기록 미반영 |
| 2 | 커밋 위생 | **검증됨**(MINOR 1) | 4커밋 범위 분리 정확(검사기/규범/봉인·문서/⑤ 반영)·메시지 수치 전건 실물 일치. 036a874만 타 워크스트림 docs(reading-v21714 21파일·배치 3 루브릭·ledger) 동승. 원문 보존: dddjango측 삽입은 처분 블록 1개, 본문 변경 3곳은 발주측 18:40 추기 형식 |
| 3 | 코퍼스·미러 정합 | **검증됨** | `make verify` 6/6 green(197초) · gate 90/90 · shacl 64파일 0 · hierarchy 9종 0 · issued 0 · ledger 0 · render-sync 540 red 0 · q4 7종 일치 · corpus_mirror_sync 11/11 · 검사기/rulepack/symbol_kinds codex `cmp` 0 · `diff -rq --exclude=__pycache__` 0 · manifest draft green(256파일) |
| 4 | 무손실 최종 | **검증됨** | main 검사기(md5 = 태그 v2.17.16) ↔ HEAD: spring 3225+84=3309 · kkebi 173+172=345 stdout diff **0** · 사이드카 0 · 픽스처 good 3→0(exit 2→0) · bad 7→8(11→12) · 증거 6→0 · bad_rules `#298` 0 |
| 5 | 미결 2 처리 | **검증됨(상신 방식)** · rev2 문면 **정정 요구 3**(채택 전) | ⓐ/ⓑ 양자 제시·6행 브리프·문면 확정 존중 — 규약 정합. rev2 전제(수치 탑)는 mypy 실측 일치. 단 rev2 문면에 관용구 방향 미명시·float 자리 `bool` 합성 경로·R-3443 적용 단위 누락 |
| 6 | 범위 밖·이월 정직성 | **MAJOR 1 · MINOR 4** | 현장 보고 **D(NoReturn)·E(`Any` 정책 — «사용자 결정 … 문면+검사기 필수»)가 036a874 시점부터 원문에 있는데** 루브릭·회신·처분 블록·로드맵 어디에도 처분 없음. 그 외 누락 4(§6) |
| 7 | 머지 판정 | **조건부 머지 가능** | 코드·그래프·미러·검증 전건 green — 조건 = 문서 1커밋(§7) |

## 1. 절차 준수 — 리뷰 BLOCKER/MAJOR 전건 대조

게이트 실재: ① «수리 범위 확정»(루브릭 ① 결론 → 계획 v1 :3 «사용자 결정(범위 = A + C′ · 제안 3 제외 · 제안 4 기각 · B 발주측)») → ③ «문면 확정»(루브릭 :51 «→ 사용자 «문면 확정»» · 계획 v2 :100 «확정 대상 문면») → ⑥(본 감사 · 릴리즈 게이트 미결 2 동반 상신). 리뷰 산출 9본 실재·각 3축·심각도·10줄 요약 형식 준수.

| 단계·리뷰어 | 판정 | 닫힘 방식 | 근거 |
|---|---|---|---|
| rv1 A A-1 «죽은 조건» MAJOR(과장) | 반영 | 회신 A행 «전제는 과장(float/bool 가드 생존·어드민 폼 2곳)» | reply.md:7 |
| rv1 A A-2(a) 구멍 2건 명시 의무 MAJOR | 반영(→⑤ 재발견) | v2 D1-1(int→float 삭제·bool⊂int만) → 렌더 :484 | plan.md:92 |
| rv1 A A-3 제안 3 축소 채택 MAJOR | **명시 이월**(사용자 결정 «제외») | 계획 v1 :3 · 회신 A-3 «범위 밖·필요 시 별도 발주» | plan.md:3 · reply.md:8 |
| rv1 A C-1 BLOCKER(불성립) | 반영(C 기각) | 루브릭 ① 표·회신 C행 | rubric.md:37 |
| rv1 A ⓒ 효과 과대 MAJOR | 반영 | 계획 «효과 서술 정정(C)» :131-132 · 회신 효과 서술 0 | plan.md:132 |
| rv1 B 3-C′·4-⓪ BLOCKER(alias 사각 — 조사자 전제 반증) | 반영(C′ 검사기 수리 채택) | 계획 Part 2 전체 · b2e1f42 | plan.md:49-75 |
| rv1 B 3-C″ MAJOR(원인 귀속 — STOP-C 잔재) | 반영 | 회신 C행 «09-01 STOP … WIP 2파일 잔재» | reply.md:11 |
| rv1 B 4-해석 MAJOR(해석 불일치 반증) | 반영 | 루브릭 ① 표 «반증 … 상관 100%» | rubric.md:38 |
| rv1 B 5-C MAJOR(문면만이면 no-op) | 반영 | C 문면 no-op → 검사기 수리 | rubric.md:48 |
| rv1 C A 수리 범위 MAJOR(PhoneNumber `-> None`) | 반영 | 렌더 :543 | final.md:543 |
| rv3 A P2-1 / B 3-d / C 하네스 오독 MAJOR | 반영 | D2-1 · findings_count:130 · baseline:252 · fixture_matrix 무변 | b2e1f42 diff |
| rv3 A P2-2 bad 픽스처 이웃 red MAJOR | 반영(→⑤ 재정정) | D2-2 → 49741cd 절대 import · `#298` 0 실측 | 본 감사 §4 |
| rv3 A P1-3 `result: int` MAJOR | 반영 | D1-5 · 렌더 :517 | final.md:517 |
| rv3 B 2-b′ int→float 모순 MAJOR-1 | 반영 | D1-1 · 렌더 :484 «float 자리의 int는 거부하지 않는다» | final.md:484 |
| rv3 C R-3442 소급 red MAJOR | 반영(→⑤ 재발견) | D1-3 brownfield 문장 | final.md:484 |
| rv3 C wiring enforcedBy #69 MAJOR | 반영 | D1-4 · wiring delegatedTo만 | wiring ttl:490-492 |
| rv3 C 전이 면제·데코레이터 alias 로드맵 누락 MAJOR | 반영 | D2-3(데코레이터 helper 포함) · D2-7 → R-15(b) | roadmap.md:51 |
| rv5 C MAJOR-1 판별 기준 비결정 | **명시 이월**(미결 2 ⓐ/ⓑ) | 계획 «미결 2» · 로드맵 R-14 · 처분 블록 | plan.md:154-159 |
| rv5 C MAJOR-2 예방 경로 | **명시 이월**(R-14b) | roadmap.md:53 | — |
| rv5 C MAJOR-3 적용 단위 | **명시 이월**(미결 2) | plan.md:157-158 | — |
| rv5 C MAJOR-4 로드맵 R-14 stale · B M1 | 반영 | 49741cd roadmap diff | — |
| rv5 A/B/C MINOR 8 | 반영 5 · **미반영 3** | 아래 | — |

**닫히지 않은 항목(MINOR·기록)** — 리뷰 MAJOR/BLOCKER 미닫힘 0.
- rv5 A MINOR-3 전반: `_module_bindings` docstring 선례를 `_final_module_bindings` 판형으로 — HEAD `check-public-surface-annotation.py:148` 여전히 «`_module_bindings` 판형»(후반 «if/try 밖 모듈 블록» 병기는 반영 :35-36).
- rv5 A MINOR-2 잔여: 계획 v2 D2-1 «`checker_cross_matrix` +1행»(plan.md:123) 미정정(실물 무변 — 루브릭 ④만 정정) · 통합 절 :80 «수리 전 red 증명 커밋 포함» 실물 커밋 부재 미주석(증거 dir 대체) · 루브릭 ④ :54 «docstring «검출 한계» 4항» ↔ 실물 5항.
- rv5 B M2는 반영(검수표 «wiring 근거» 행 실재 plan.md:146).

## 2. 커밋 위생

| 커밋 | 범위 | 메시지 사실성(실물 대조) | 판정 |
|---|---|---|---|
| b2e1f42 fix(check) | 검사기 ×2(byte) · symbol_kinds ×2 · 픽스처 8 · 하네스 2 | «#493×7→8 · baseline 11→12 · cross 무변» = findings_count:130 `#493×8`/12 · baseline:252 `(2,12,12,4,False)` · cross_matrix 무변경 ✓ · «orig 6→0 · 차분 0» 본 감사 재현 ✓ | 검증됨 |
| 33b0bd7 norm | ttl 2 · ISSUED 2행 · LEDGER 1행 · 렌더 3본 각 +7/−5 · rulepack ×2 · target-counts +2/+2/+2 · q4 3443 | 전건 diff 일치 · 확정 문면 밖 hunk 0(불릿 2·예제 4지점만) | 검증됨 |
| 27342a3 docs(seal) | 봉인 draft(T2-0b 64행) · 증거 5파일 · 검수표·루브릭 ④·회신·로드맵 R-15/16·조감도 1행 · design md 1행(cache_parity ok→drift — 기계 렌더·미설치 정상) | ✓ | 검증됨 |
| 49741cd fix(check,docs) | 검사기 docstring 2행(모듈 블록 병기)만 · aliased_shadow import 1행 · symbol_kinds(해시) · 봉인 12행 · rv5 3본 · 문서 5 | 코드 변경은 docstring·픽스처 1행뿐 — 판정 로직 무접촉 ✓ | 검증됨 |
| 036a874 docs | 현장 보고·루브릭·계획·rv1/rv3 + **타 워크스트림**(reading-v21714 21파일 · 배치 3 루브릭 · ledger.md +23 · 로드맵 신설) | 메시지가 동승을 명시 · docs 한정 · main 대비 충돌 0 | **MINOR**(범위 분리 미흡 — 이 브랜치가 배치 3 ⓪① 기록까지 운반) |

- 훅: `core.hooksPath=workspace/hooks` · pre-commit = md 변경 시 ledger-check · ttl 변경 시 ontology_gate. 통과 «흔적»은 커밋 객체에 남지 않음 — `make verify` 재실행(gate 90/90 · ledger 0)으로 동치 확인.
- 원문 보존: `git diff 036a874..HEAD` 현장 보고 = 상단 처분 블록 삽입(+11) + 본문 3곳(C행 25건·«추기 18:40» 절·제안 3항) 변경. 본문 변경은 발주자 어조·발주측 커밋(96e8719) 언급이라 발주측 추기의 재반입으로 판단 — 단 spring_dream 트리에 원본 파일 부재(find 0건)라 대조 불가(관찰).

## 3. 코퍼스·미러 정합 — 실측

| 검사 | 결과 | 출처 |
|---|---|---|
| `make verify` | **6/6 green** 197초 · 전/후 `git status` 0행 | `/tmp/djr-verify.pm8Zef` |
| ontology_gate | 90파일 green 90 · red 0 | verify-ontology.log:94 |
| shacl-full / hierarchy / golden / gate-smoke | 64파일 위반 0 / 9종 불일치 0(target-counts 3452/3452/3546) / 23 불일치 0 / 12 케이스 0 | :99·:101·:126·:140 |
| issued-check / ledger-check / render-sync | 위반 0 / 위반 0 / 540절 red 0·warn 0·SyncDebt 0 | :142·:144·:146 |
| structural / query-golden(q4 3443) | 7종 성립 / 7종 전건 일치 | :163·:165 |
| corpus_mirror_sync `--check` | 11/11 in-sync | 본 감사 직접 실행 |
| rulepack | Work 3443 · 팩 == render(그래프) · 양 런타임 미러 동일 | base-core.log:406-411 |
| manifest_seal `--check --draft` | green · 그룹 10 · 256파일 · draft · sealed_commit 27342a3(HEAD 아님 — draft 관행·설치 후 `--write` 재발행 필요) | :412 |
| fixture / baseline / findings_count / cross | 102/102 · 73/73 · 73/73 · 350/350 | :199·:279·:353 · cross.log:2-3 |
| gen_pregate_symbol_kinds `--check` | in-sync 56종·27검사기·양 미러 | regen.log:30 |
| byte cmp | 검사기 · rulepack.json · pregate_symbol_kinds.json · architecture-ddd final.md — codex 전부 `cmp` 0 · `diff -rq --exclude=__pycache__` 0 | 본 감사 |

## 4. 무손실 최종 — 독립 재현

| 대상 | main 검사기(`git archive main dddjango/scripts` · md5 c082d5d8 = 태그 `dddjango--v2.17.16`) | HEAD 검사기(md5 972d1cf5) | 차분 |
|---|---|---|---|
| `~/Desktop/spring_dream_server` @96e8719 | exit 2 · #493 3225 · ⓓ#69 84 · 레코드 3309 | 동일 | stdout diff **0행** · 사이드카 0 |
| `~/Desktop/kkebi-server` @6608fb0 | exit 2 · #493 173 · ⓓ#69 172 · 레코드 345 | 동일 | **0행** · 사이드카 0 |
| 픽스처 `public_surface/good` | exit 2 · #493 3(book_usage_policy 2·reading_cursor 1) | exit 0 · clean | 오탐 소거 |
| 픽스처 `public_surface/bad_rules` | exit 2 · #493 7 · 전체 11 | exit 2 · #493 **8**(aliased_shadow:7 `FIRST`) · 12 | 미탐 폐쇄 |
| 증거 `evidence-alias-strenum/`(표준 트리 배치) | #493 6 | clean(파일 2) | orig 6 → 0 |
| bad_rules × `check-domain-model` | — | `#298` 0(⑤ 절대 import 반영 확인) | — |
| 렌더 §3.1 예제(:487-546 추출 59행) | mypy full(strict+warn_unreachable+redundant-expr) **0** · plain **0** · 런타임 `Money(True)`/`Money(-1)` ValueError · `subtract` OK · HEAD 검사기 #493/#69 **0** | — | 검수표 일치 |

## 5. 미결 2 — 상신 방식 · rev2 문면 실측

**상신 방식**: 계획 «미결 2» 6행 · ⓐ rev2 채택 / ⓑ 현행 유지 양자 제시 · 사이클 비용(≈10분) 명시 · 로드맵 R-14·처분 블록에 «릴리즈 게이트 상신» 일관. 결정 브리프 규약(10줄 이하·수치·유도 없음)과 «문면은 사용자 소유» 규약 정합 — **검증됨**.

**mypy 2.3.1 실측**(`--strict` 및 `--strict --warn-unreachable --enable-error-code redundant-expr` 동일 결과):

| 호출 | 결과 | 의미 |
|---|---|---|
| `f(x: float)` ← `1` / `True` | 통과 / 통과 | int→float 승격(PEP 484) · bool→int→float 합성 |
| `g(x: int)` ← `True` | 통과 | bool ⊂ int(상속) |
| `h(x: complex)` ← `1.5` / `1` | 통과 / 통과 | float·int→complex 승격 |
| `type(amount) is bool` (int 자리) | 침묵 | rev2 허용 형 |
| `type(seconds) is not float` / `type(seconds) is int` (float 자리) | 침묵 / 침묵 | 발주측 4파일 형상 — 승격 값(int) 거부하는데 mypy 무감 |
| `not isinstance(seconds, float): raise` (raise-only) | 침묵 | — |
| `not isinstance(amount, int) or amount < 0` | **redundant-expr** | 현장 보고 발화 형상(유일) |
| `type(seconds) is bool` (float 자리) · `T(True, 1)` | 침묵 · 통과 | bool은 float 자리도 통과 |
| 런타임 | `issubclass(bool,int)=True` · `issubclass(int,float)=False` · `isinstance(1,float)=False` | 상속/승격 구분은 런타임 사실과 일치 |

**판정**: rev2의 원리(«상속으로 통과 = 거부 가능 · 승격으로 통과 = 거부 금지»)는 PEP 484·mypy·런타임 모두와 일치하며 R-3443·R-3158·cleancode §12.7과 충돌 없음. 단 mypy는 두 경우를 구분하지 못하므로(전부 침묵) 결정성은 문면이 혼자 져야 한다 — 그래서 아래 결함이 실전에 그대로 새어 나간다.

**rev2 제안 문면 결함(채택 전 정정 요구)**:
- **R2-1 관용구 방향 미명시(MAJOR-급)**: «`type(x) is T`로 거른다»의 T가 «거부할 하위 타입»(예제 `type(self.amount) is bool`)인지 «선언 타입»(`type(x) is not int`)인지 문면이 정하지 않는다. int 자리에선 둘이 같지만 float 자리에선 `type(x) is not float`가 승격 int까지 거부 — **발주측이 같은 날 4파일에 채택한 바로 그 형상**이고 현행 rev1도 같은 구멍. 통과 문면: «`type(x) is <거부할 하위 타입>`(예: `type(amount) is bool`) 형으로만 거른다 — `type(x) is not <선언 타입>` 형은 승격 값까지 거부하므로 쓰지 않는다».
- **R2-2 합성 경로(MINOR)**: `float` 자리의 `bool`은 상속(bool⊂int)+승격(int→float) 합성으로 통과 — rev2 이분법상 «승격으로 통과 → 거부 금지»로 읽힐 수 있다. 통과 문면: «`bool`은 값 의미가 다른 하위 타입이라 어느 수치 자리에서든 거부할 수 있다».
- **R2-3 적용 단위의 귀속(MINOR)**: «적용 대상 = 새로 쓰는 값 객체와 손대는 줄» 문장은 R-3442 불릿 안에만 있고 R-3443(Prohibition)에는 없다 — 리뷰어가 R-3443을 untouched 코드에 적용할 수 있다. 통과 문면: 적용 대상 문장을 두 불릿 공통으로(«R-3442·R-3443의 적용 대상은 …») 또는 R-3443에 «같은 적용 대상» 1구 부착.
- (선택) rv1 A·rv3 B가 제안한 «표현·정밀도가 규칙이면 시그니처의 타입을 바꾼다» 1구가 확정·rev2 모두에서 빠짐 — float 강제가 진짜 도메인 규칙인 레인(qt 스펙 :63 «유한 float»)의 출구.

## 6. 범위 밖·로드맵 이월의 정직성

R-14b·R-15(a)(b)·R-16·R-17은 각각 rv5 C MAJOR-2·rv3 C 전이 면제/family·rv3 A 부기·rv5 B O2를 정확히 덮는다. 덮지 못한 발견:

| # | 심각도 | 누락 발견 | 출처 | 어떻게 고치면 통과 |
|---|---|---|---|---|
| 6-1 | **MAJOR(문서·범위)** | 현장 보고 **D**(항상 raise 도우미 `-> NoReturn` 문면 1줄·선택)·**E**(`Any` 정책 부재 — 원문 :205 «**사용자 결정(2026-09-03): 플러그인이 `Any`를 못 쓰게 강제한다 — 문면과 검사기 둘 다 필수**»)가 036a874(루브릭 확정 시점) 원문에 이미 있는데 루브릭 :3(대상 A·C·B만)·회신·처분 상태 블록(A/A-3·4/B/C 4행)·로드맵(§3·§6·§7) 어디에도 처분 없음. 발주측이 «사용자 결정·필수»로 적은 항목이 기록 없이 소실된다 — 명시적 결정 게이트 규약 위반 형상 | 현장 보고 :24-25·:193-205 | 처분 블록에 D·E 행 추가 + 로드맵 §3에 R-18(E: `Any` 정책 — 문면 §4 + 검사기 #493 계열 «명시 Any» 규칙 · 프레임워크 경계 취급 결정 필요)·R-19(D: implementation-python `NoReturn` 1줄) 등재(또는 «미접수 — 사용자 재확인 대기»로 명시). docs 1커밋 |
| 6-2 | MINOR | 현장 보고 C 추기 제안 2 — «imported base는 one-public-symbol/file 계산 제외»·«선언형 base 별칭 없이 직접 import» 문면 1줄, 및 rv1 B (e) «별칭 관행의 근거(imported binding=공개 심볼)는 코퍼스 부재 — 별도 항목» | 현장 보고 :170-176 · rv1/B.md:56 | 회신 C행에 처분 1구(기각 사유: alias는 이제 원명 해소·별칭 자체 적법·one-public-symbol 해석은 레인 과잉 해석) 또는 로드맵 후보 등재 |
| 6-3 | MINOR | 현장 보고 C 추기 «프로브 3개(`_StrEnum`·`_Schema`·`_BaseModel`)» — 픽스처는 StrEnum·dataclass 별칭 2종뿐(Schema/BaseModel 별칭은 rv3 a14·rv5 t5 스크래치만) | 현장 보고 :175 | good 픽스처에 `Schema as _Schema`+무주석 `model_config` 1파일 추가(EXPECTED sha 재실측) — 또는 «스크래치 실측으로 갈음» 명기 |
| 6-4 | MINOR | rv3 C 사건 표 #7 kkebi `TypeAlias` 첫 대입(`Power = dict[str, float]`) #493 ↔ ruff UP040 충돌·사용자 override 현존 — #493 facet인데 R-15/R-16 어디에도 없음 | rv3/C.md:103 | R-15에 (c) TypeAlias facet 1구 추가 |
| 6-5 | MINOR | rv5 C MAJOR-2 후반 — rulepack `agents`(delegatedTo) 필드의 런타임 주입 경로 부재 → architecture-ddd 위임 52건 전부 명목. R-14b는 «교차 참조 1줄»만 담음 | rv5/C.md:76 | R-14b 범위에 «delegatedTo 채널의 실집행 경로(리뷰어 로드 스킬 ↔ wiring) 조사» 1구 |

## 7. 정정 요구 — «어떻게 고치면 통과»

| 우선 | 요구 | 조치 | 시점 |
|---|---|---|---|
| **머지 조건** | 6-1 D·E 처분 | 처분 블록 2행 + 로드맵 R-18/R-19(또는 «미접수·재확인» 명시) | 머지 전 docs 1커밋 |
| 릴리즈 조건 | 미결 2 결정 + R2-1(필수)·R2-2·R2-3 반영 | ⓐ면 R-3442 rev2(+R-3443 적용 단위) 1사이클(ttl→gate→render→LEDGER→counts→q4→rulepack→미러→verify) · ⓑ면 최소 R2-1을 별도 clarification 후보로 로드맵 등재 | 릴리즈 게이트 |
| 권고(MINOR) | §1 미반영 3(선례 문구·D2-1 «+1행»·«red 증명 커밋»·«4항») · 6-2~6-5 · 036a874 동승 docs 주석 | 문서 정정 | 머지 전후 무관 |
| 관행 | 봉인 `--write` 재발행 | 설치 도달 후 | 릴리즈 후 |

## 8. 최종 판정

**조건부 머지 가능** — BLOCKER 0 · MAJOR 1(문서 — 6-1 D·E 처분 누락 · 코드/그래프 무관 · docs 1커밋으로 해소) · MINOR 9 · 관찰 2.
코드(검사기)·그래프(R-3442/R-3443·b3/b4)·미러·소성물·검증 전건 green이며 무손실은 독립 재현으로 확정. 조건 충족 즉시 main 머지 가능. 릴리즈는 미결 2 결정에 종속(rev2 채택 시 R2-1 반영 필수).

## 9. 10줄 요약

1. 절차: 게이트 ①③⑥·적대 리뷰 ①③⑤ 각 3기 산출 9본 실재 — BLOCKER 3·MAJOR 19 전건 «반영 또는 명시 이월(미결 2·R-14b)»로 닫힘, 미닫힘 MAJOR/BLOCKER 0 · ⑤ MINOR 3건만 기록 미반영(docstring 선례 문구·계획 D2-1 «+1행»·루브릭 «4항»/실물 5항).
2. 커밋: 4커밋 범위 분리·메시지 수치 전건 실물 일치(#493×8·12/12·3452/3452/3546·q4 3443·ISSUED 2·LEDGER 1) · 49741cd 코드 변경은 docstring 2행+픽스처 import 1행뿐 · 036a874만 타 워크스트림 docs 동승(MINOR).
3. 정합: `make verify` 6/6 green(197초·전/후 tree clean) · gate 90/90·shacl 0·hierarchy 0·issued 0·ledger 0·render-sync 540/0·q4 7종 · corpus_mirror_sync 11/11 · 검사기/rulepack/symbol_kinds/final.md codex `cmp` 0 · manifest draft green 256파일.
4. 무손실: main 검사기(=v2.17.16 태그) ↔ HEAD — spring 3225+84=3309·kkebi 173+172=345 stdout diff 0·사이드카 0 · 픽스처 good 3→0·bad 7→8·증거 6→0·`#298` 0 · 렌더 예제 mypy full/plain 0·런타임 bool/음수 거부·검사기 0.
5. 미결 2 상신은 ⓐ/ⓑ 6행 브리프로 규약 정합 · rev2 전제는 mypy 실측 일치(int→float·float/int→complex·bool→int 전부 통과 · 발화는 or-체인 isinstance 1형뿐 · `type() is` 형은 전부 침묵).
6. rev2 문면 결함 3 — R2-1 «`type(x) is T`»의 T가 «거부할 하위 타입»인지 «선언 타입»인지 미명시(float 자리 `type(x) is not float` = 발주측 4파일 형상이 승격 int를 거부) · R2-2 float 자리 `bool` 합성 통과 미처리 · R2-3 적용 단위 문장이 R-3443에 없음 — 채택 전 정정.
7. **MAJOR 1(문서)**: 현장 보고 D(`NoReturn`)·E(`Any` 정책 — «사용자 결정·문면+검사기 필수»)가 루브릭 확정 시점 원문에 있는데 처분 블록·회신·로드맵 전부 무기록 → D·E 처분 행 + R-18/R-19 등재(docs 1커밋)가 머지 조건.
8. 로드맵 누락 MINOR 4: C 추기 제안 2(one-public-symbol·별칭 금지 1줄) 처분 · `_Schema`/`_BaseModel` 프로브 픽스처 부재 · kkebi TypeAlias facet(UP040) · delegatedTo 실집행 경로(R-14b 범위 확장).
9. 관찰: 봉인 sealed_commit=27342a3(draft 관행·설치 후 재발행) · 현장 보고 본문 3곳 변경은 발주측 18:40 추기 형식이나 spring 트리에 원본 부재라 대조 불가.
10. 판정: **조건부 머지 가능** — BLOCKER 0·MAJOR 1(docs)·MINOR 9. 조건 = D·E 처분 1커밋 → 머지; 릴리즈는 미결 2 결정(+R2-1 반영)에 종속.
