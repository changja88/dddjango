# ⑥ 재검 — 현장 보고(typecheck) 수리 · 브랜치 `fix/field-typecheck` HEAD `68a5141` (2026-09-03)

- 대상: 감사(`rv6/audit.md`, 대상 49741cd) 이후 반영 커밋 1개 `68a5141`(15파일 +92/−18). 저장소 무수정(읽기·`git`·스크래치 실행만) — 전/후 `git status --porcelain` 0행. spring_dream_server 접촉은 `git show`/`log`·`--block-hash`(출력 전용)뿐 — 그쪽 dirty 1행(`?? .claude/` 08-29 기존)은 본 재검 전부터 존재.
- 1차 자료 경로 변경: 지시된 `~/.herdr/worktrees/spring_dream_server/feat-fortune-catalog/`는 재검 도중 소멸(레인이 `aacaaa0`로 main 머지·워크트리 정리). 같은 파일을 `~/Desktop/spring_dream_server` main 체크아웃(추적 파일 `.dddjango/20260903-1214-fortune-catalog/pregate-report.md` 180행·md5 1f13f3e0 · `docs/superpowers/orders/lane/REPORT-fortune-catalog.md`)과 `aacaaa0^2`(= f6ef7ff) git 이력으로 대조했다.
- 스크래치 `rv6/recheck/`: `make-verify.out` · `schema-tree/`(6-3 재현) · `spec-{9ee721e,75e3672,854ba47,67f6411}.md`(블록 해시).

## 0. 항목별 판정 표

| # | 항목 | 판정 | 요지 |
|---|---|---|---|
| 1 | 머지 조건 닫힘 | **검증됨** | MAJOR 6-1(D·E 처분) 3문서(현장 보고 블록·회신·로드맵 R-18/R-19) 일관 등재 · 지정 MINOR 7건(6-2·6-3·6-4·docstring 선례명·D2-1·통합 절·«5항») 전건 실물 반영. 미반영은 권고 2(6-5 R-14b 범위 · 036a874 동승 주석)+선택 1 — 조건 아님 |
| 2 | rev2 제안 문면 | **검증됨(새 결함 0 · 관찰 2)** | R2-1·R2-2 문면 정확 · R2-3은 «공통으로» 지시문+MAJOR-3 문장의 2조각(채택 시 1문장 조립 필요). 원리 오류·규범 충돌 없음. 그래프 미반영 확인: ttl `R-3442@2026-09-03 revision 1` · 문구 «거부할 하위 타입» ttl/final.md(양 런타임)/rulepack 0건 |
| 3 | 회귀 없음 | **검증됨** | 코드 변경 = docstring 1행(양 미러 동일) + symbol_kinds 해시 재소성 · codex `cmp`/`diff -rq` 0 · symbol_kinds in-sync 56·27 · `make verify` 재실행 **6/6 green 179초**(tree clean) · seal draft green 256 · mirror 11/11 |
| 4 | ledger 레인 4 사실성 | **검증됨(MINOR 2 · 관찰 2)** | 지정 수치 전건 1차 자료 일치(4회·스탬프 4/4·corrected 2·형식 0·결손 0·G2 귀속 0·≈6h31m·해시 6cf8e2ffdfc3→cb95a1bddb32·재실행 0). MINOR: 계약 실존 집계가 run 1 수치(행 5·밖 3 — 최종 run은 행 6·밖 4, ⑵ 절 «6행»과 자기 불일치) · 레인 4만 «pre-gate 총 소요» 절 부재. 판정 규칙 정합 ✓ |
| 5 | 최종 판정 | **머지 가능** | 머지 조건 잔존 0. 잔존은 비조건 MINOR 4·관찰 4. 릴리즈는 미결 2(+B 기록 충돌 재확인) 사용자 결정에 종속 — 감사와 동일 |

## 1. 머지 조건 닫힘 — 감사 요구 ↔ 68a5141 실물

| 감사 요구 | 실물(HEAD) | 판정 |
|---|---|---|
| **MAJOR 6-1** D·E 처분 행 + 로드맵 등재(또는 «미접수» 명시) | 현장 보고 처분 블록 :13 `D(추기) … **R-18 등재**(극소·다음 규범 정합 배치)` · :14 `E(추기) … **R-19 등재** — 착수 시점·범위 … 사용자 재확인 후` · :15 `B 재확인 … 두 기록이 충돌 → 릴리즈 게이트에서 사용자 재확인 \| 미결` · 회신 :13-16 D/E/B 재확인 3행 · 로드맵 :53 R-18(«항상 raise/sys.exit 도우미는 `-> NoReturn`» 1줄) · :54 R-19(`Any` 정책 — 하우스룰 §4 절 + #493 확장 · «사용자 재확인 후 별도 수리 배치(⓪~⑥ 판형)») · 이력 :95-96 | **닫힘**. 원문 :200-211 대조 일치 — E 원문 «사용자 결정 … 문면과 검사기 둘 다 필수»가 R-19 «규범+검사기(중)»로 보존되고 착수는 재확인 게이트로 남김(명시적 결정 게이트 규약 정합). 번호는 감사 제안(R-18=E)과 반대(R-18=D·R-19=E)이나 3문서 일관 |
| 6-2 C 추기 제안 2 처분 | 회신 «C 추기» 행 «제안 2 … **기각** — 별칭이 원명으로 풀리므로 우회·금지 모두 불필요, #345는 정의만 계수» · 현장 보고 블록 C 추기 행 동문 | 닫힘 |
| 6-3 `_Schema`/`_BaseModel` 프로브(픽스처 또는 «스크래치 실측 갈음» 명기) | `evidence-alias-schema/` 4파일 · README «픽스처 대신 스크래치 실측으로 갈음(api/ 트리 도입 시 cross 최소성 훼손)» | 닫힘 — **본 재검 독립 재현 일치**: 표준 트리 7파일(`__init__.py`×6 + `schema_in.py`) · 감사 `orig/`(main 검사기) exit 2 `#493` ×2(:6·:11 `model_config`) / HEAD 검사기 exit 0 «clean — 파일 7개 … e0585441b2e6939d» — 커밋된 txt 2본과 문자열 동일 |
| 6-4 R-15(c) TypeAlias facet | 로드맵 :51 «(c) #493 `TypeAlias` 첫 대입(`Power = dict[str, float]`) ↔ ruff UP040 충돌(kkebi 사용자 override 현존)» | 닫힘 |
| rv5 A MINOR-3 docstring 선례명 | `check-public-surface-annotation.py:148` «check-error-centralization `_final_module_bindings` 판형» — 선례 실재 `check-error-centralization.py:4124 def _final_module_bindings(parsed) -> dict[str, str]`(동파일 :866 `_module_bindings`는 `dict[int, dict[str, str]]`라 정정이 정확) · codex 미러 동일 hunk | 닫힘 |
| 계획 D2-1 «`checker_cross_matrix` +1행» | plan :123 «`checker_cross_matrix` 무변(census는 비-0 exit만 기록 — ⑤ 정정)» | 닫힘 |
| 통합 절 «수리 전 red 증명 커밋 포함» | plan :80 «수리 전 red 증명은 별도 커밋 대신 증거 폴더 `evidence-alias-*`의 orig 출력으로 보존 — ⑥ 감사 주석» | 닫힘 |
| 루브릭 «검출 한계 4항» | rubric :54 «5항(⑤ 반영 후)» · 실물 docstring :31-40 불릿 **5** | 닫힘 |
| 6-5 R-14b delegatedTo 실집행 경로 조사 1구 | 로드맵 R-14b 행 무변 | **미반영**(권고) |
| 036a874 타 워크스트림 동승 주석 | 없음 | **미반영**(권고) |
| (선택) «표현·정밀도가 규칙이면 시그니처 타입을 바꾼다» 1구 | 없음 | 미반영(선택) |

커밋 위생: 메시지의 항목 열거(D·E·R-18/19 · C 추기 19건 증거 orig 2→0 · B 충돌 항목화 · MINOR 4종 · rev2 R2-1~3 · ledger 레인 4 발견 ⑩⑪⑫ · 봉인 draft)가 15파일 diff와 전건 대응. 봉인 `sealed_commit` 49741cd(HEAD 아님 — draft 관행·감사와 동일 관찰).

## 2. rev2 제안 문면(plan :156 · «미결 2»)

> «거부할 수 있는 것은 선언 타입의 **하위 타입** 값뿐이다(`bool`⊂`int`처럼 상속으로 통과하는 값). 거르는 형은 `type(x) is <거부할 하위 타입>`(예: `type(amount) is bool`)뿐이며, `type(x) is not <선언 타입>` 형은 승격 값까지 거부하므로 쓰지 않는다. 수치 탑 **승격**으로 통과하는 값(`float` 자리의 `int`·`complex` 자리의 `float`)은 시그니처가 수용을 약속한 것이므로 거부하지 않는다. `bool`은 값 의미가 다른 하위 타입이라 어느 수치 자리에서든 거부할 수 있다.» + 적용 대상 문장을 R-3442·R-3443 공통으로(«두 규범의 적용 대상은 …»). — MAJOR-3 rev2: «적용 대상은 이번 작업이 새로 쓰는 값 객체와 **손대는 줄**이다 — 손대지 않는 기존 재검사는 소급 대상이 아니며 정리는 발주 소관이다.»

| 요구 | 판정 | 근거 |
|---|---|---|
| R2-1 거르는 형 = `type(x) is <거부할 하위 타입>`만 · `is not <선언 타입>` 금지 | **정확** | 문장 2 그대로. 금지 사유(«승격 값까지 거부»)는 float/complex 자리에서만 성립하지만 int 자리의 `type(x) is not int`는 R-3443(선언 타입 재검사 금지)이 이미 잡으므로 금지의 일관성은 유지 |
| R2-2 bool은 어느 수치 자리에서든 거부 가능 | **정확** | 문장 5. 합성 경로(bool→int→float) 오독 폐쇄. 감사 mypy 실측(float 자리 `type(x) is bool` 침묵)과 정합 |
| R2-3 적용 대상 두 규범 공통 | **의도 반영 · 문면 미완결** | «공통으로(«두 규범의 적용 대상은 …»)»는 지시문이고 실제 문장은 MAJOR-3 항에 분리돼 있다 — ⓐ 채택 시 «R-3442·R-3443의 적용 대상은 이번 작업이 새로 쓰는 값 객체와 손대는 줄이다 …» 1문장으로 조립해야 함(관찰 — 제안 단계라 결함 아님) |
| 새 결함(원리·충돌) | **0** | PEP 484 승격/상속 구분·런타임 `issubclass(bool,int)`·`isinstance(1,float)=False`와 일치. R-3443·cleancode §12.7·R-3158 충돌 없음. 렌더 예제 :503 `if type(self.amount) is bool` 형이 rev2 허용형과 일치 |
| 관찰 | «뿐»이 `isinstance(x, bool)`(bool은 final이라 의미 동치)까지 배제 — 결정성을 위한 표기 단일화 선택으로 읽히며 오류는 아님. 채택 시 리뷰어가 `isinstance(x, bool)`를 위반으로 볼 수 있음을 사용자가 인지하면 됨 |

그래프 미반영 확인: `ontology/rules/architecture-ddd-final.ttl:1737-1739` `<…#R-3442@2026-09-03> a djr:Expression ; djr:revision 1` · :2232 s016-3.1 text는 확정 문면(«`type(x) is T` 형으로 쓴다(예: `bool`⊂`int`)») · «거부할 하위 타입» grep — ttl 0 · `dddjango/skills/architecture-ddd/references/final.md` 0 · codex final.md 0(claude↔codex `cmp` 0) · `rulepack.json` 0. 미결 2는 여전히 사용자 ⓐ/ⓑ 결정 대기.

## 3. 회귀 없음 — 실측

| 검사 | 결과 |
|---|---|
| `git show 68a5141 -- dddjango/scripts codex-…/scripts` | `check-public-surface-annotation.py` **docstring 1행**(`_module_bindings` → `_final_module_bindings`) ×2(양 미러 동일 hunk) + `pregate_symbol_kinds.json` 해시 1행 ×2(077559362070262c → 3a5551e2a9fa5b09 = HEAD 파일 sha256 선두 16자 실측 일치). 판정 로직 무접촉 |
| codex 미러 | 전 스크립트 `cmp` OK · `diff -rq --exclude=__pycache__` exit 0 |
| `gen_pregate_symbol_kinds.py --check` | in-sync(종류 56·검사기 27종·양쪽 미러 일치) |
| `make verify` 재실행 | **6/6 green 179초**(web 31·core 54·ontology 69·backstop 100·regen 131·cross 179) · 로그 `/tmp/djr-verify.PfKQ4o` · 전/후 tree 0행. 기존 로그 `fHh9rm`(19:01-19:04 · 커밋 직전)도 6 로그 전건 green 표지 |
| `manifest_seal.py --check --draft` | green · 그룹 10 · 봉인 256 · 배정 18런 · draft(sealed_commit 49741cd — draft 관행) |
| `corpus_mirror_sync.py --check` | 11/11 in-sync |
| T2-0b 매니페스트 해시 갱신(9c78acf1…) | raw sha256(3a5551e2…)과 다르나 도구 규약이 `sha256(bytes + "\0mode:" + mode)`(manifest_seal.py:245-252)라 정상 — `--check` green이 증명 |

## 4. ledger 레인 4 — 1차 자료 대조

| ledger 수치 | 1차 자료 | 판정 |
|---|---|---|
| pre-gate 4회 12:59·13:24·13:33·13:42 | pregate-report 헤더 4개 UTC 03:59:52·04:24:15·04:33:47·04:42:39(:2·:45·:89·:138) | ✓ |
| 스탬프 v2.17.16 4/4 | 4 헤더 전부 «실행기: design_pregate.py · dddjango v2.17.16» | ✓ |
| corrected 2(#392 `869e0acd832f` · #576 `1e5a7ecc6e40`) · 다음 실행 소멸 | run 1 #392 1건 → run 2 #576 1건 → run 3·4 green 0건 · 처분 라벨 절 :133-136 corrected ×2 | ✓ |
| 형식 0 · ignored/filtered 0 · 결손 0 · 판정 불능 0 · 도구 오류 0 | 4 run 전부 예보 red/green만(형식 red 없음) · «결손 0(항목 0) · 판정 불능 0» 4/4 | ✓ |
| G2 귀속 0(anchor 9ee721e · 27종) · legacy 2607 · mypy(BC) 0 · ruff clean | REPORT «`registry_gate.py . --anchor 9ee721e…` 귀속 0건 → green (27종). legacy 잔존 2607 … » · «mypy application/fortune_catalog 0» · «ruff check clean · format --check clean(53파일)» · `build_anchor` = 9ee721e9… | ✓ |
| 총 ≈6h31m · STOP 0 | G0 e1294f5 12:24 → REPORT f6ef7ff 18:55:37 = 6h31m · REPORT «STOP(발주자 결정)은 발화하지 않았다» | ✓ |
| 타임라인(11:33 투입·11:53 회수·G1 13:43·슬라이스 0 13:55 왕복 2회 ≈14분·17:33·ruff 17:42·18:30) | 5b9391a 11:33 · fdcdab9 11:53 · 9ee721e 13:43:01 · 59d08c7 13:55→99253ce 14:05→9c8814e 14:09 · 854ba47 17:33 · ed3cdf3 17:42 · 67f6411 18:30 | ✓ |
| Phase 2 명세 개정 3회(15:26·17:33·18:30) · 블록 해시 6cf8e2ffdfc3 → cb95a1bddb32 · 재실행 0 | `design-spec.md` 이력 = 9ee721e·75e3672 15:26·854ba47 17:33·67f6411 18:30 · `--block-hash` 실측 9ee721e **6cf8e2ffdfc3**(= run 4 헤더) → 75e3672 70c766f686f6 → 854ba47 09dbd671e00b → 67f6411 **cb95a1bddb32**(현 작업본 동일) — 3회 모두 해시 변동 · 13:42 이후 리포트 0 | ✓ (발견 ⑩ 근거 정확) |
| ⑵ #93 «G1 boundary-imports 블록 6행에 미기재·산문 §167에만» | G1 명세 :489 블록 6행(dependency_wiring ×3·rag_runtime_adapter·test ×2 — OHS→port 예외 import 없음) · :167 산문 «각 함수는 `ActiveServiceBundleContractMismatch`·`RelationTableContractMismatch`를 잡아 …» | ✓ («§167»은 행 번호) |
| 런타임 Claude Opus 4.8 | 5b9391a «claude Opus 4.8 레인 feat/fortune-catalog» | ✓ |
| **계약 실존 «행 5 · 이름 판정 5 · 실존 확인 2 · 저장소 밖 3»** | run 1(:15)만 행 5·밖 3 — run 2·3·4(:58·:102·:151) 및 **최종(G1 근거) run은 «행 6 · 이름 판정 6 · 실존 확인 2 · 저장소 밖 4»**. 같은 절 ⑵는 «블록 6행»이라 자기 불일치 | **MINOR**(수치 출처 오기 — 결손 0·판정 불능 0·도구 오류 0은 4/4 불변이라 결론 무영향) |
| «pre-gate 총 소요» 절 | 레인 1~3은 각 «### pre-gate 총 소요» 절 보유(헤더 판정 규칙 ⑶ «+ pre-gate 총 소요 보고») · 레인 4는 타임라인 4회 시각만(12:59~13:42 = 43분 산출 가능) · 절 부재 | **MINOR**(형식 — 판정식 입력 아님) |
| «정합 3회(15:26 #574 · 18:30 #85/#642)» | 정합 라벨 커밋 2(75e3672·67f6411) · REPORT «설계 진화 5건»·«5회 정합» | 관찰(계수 단위 혼용 — 규칙 번호 3 기준) |
| 총괄 표 «귀속 예보(최종) 2건» | 최종 run 예보 0건 · 누적 ID 2 — 레인 1 «15건»은 최종 run 계수라 열 의미 혼용 | 관찰 |

**판정 규칙 정합**: 헤더 규칙 = 실전 레인 ≥2(신규 BC ≥1)에서 ⑴ 오탐 0 ⑵ 미탐 0 ⑶ 형식 ≤1/레인 (+총 소요 보고) ⑷ 실존 채널 별도 계수. 레인 **2·4**(둘 다 신규 BC)가 ⑴⑵⑶ 전건 충족이라 문언상 요건은 레인 1 없이도 성립. 레인 1 ⑶ ✗(2)를 «파서 `_Class` 수리로 소멸한 계열»로 처리한 근거 = 발견 ⑦(:125 «`_GroupAssetItem` — 언더스코어 선두 클래스를 파서가 함수로 분류») ↔ v2.17.16 커밋 f0fcdb4 «수리 배치 2 Part 1 — 파서 `_Class` 분류…» 실재 ✓. 09-02 사용자 결정 ⓐ(«수리 배치 후 재실측 1레인»)의 재실측 조건(v2.17.16 스탬프 세션 완주·정위치 형식 red만 계상)을 그대로 적용했고, 결론은 «요건 성립 → G-A 브리프 상신»으로 승격 결정 자체는 사용자 게이트에 남김 — 명시적 결정 게이트·브리프 규약 정합. 실존 채널 «표본 1·진탐 0 → 비승격 유지» ✓.

## 5. 최종 판정

**머지 가능** — 감사의 머지 조건(D·E 처분 기록)은 68a5141로 충족, 지정 MINOR 7건 전건 반영, 코드 변경은 docstring 1행뿐이며 검증 전건 green(재실행). 잔존은 전부 비조건:
- 권고 MINOR 4: 6-5 R-14b 범위 1구 · 036a874 동승 주석 · ledger 계약 실존 집계를 최종 run 수치(행 6·밖 4)로 정정 · 레인 4 «pre-gate 총 소요» 절(43분) 추가 — 머지 전후 무관(docs).
- 관찰 4: rev2 R2-3 채택 시 1문장 조립 · «뿐»의 `isinstance(x, bool)` 배제 · «정합 3회»·«귀속 예보(최종)» 계수 단위 · 봉인 sealed_commit 49741cd(설치 후 `--write`).
- 릴리즈 게이트(머지와 별개): 미결 2 ⓐ/ⓑ 사용자 결정(ⓐ면 R2-1~3 반영 1사이클) + 68a5141이 새로 항목화한 **B 기록 충돌**(개정판 «B 1순위» vs 세션 «B 기각») 재확인.

## 6. 10줄 요약

1. 머지 조건: 감사 MAJOR 6-1(D·E 처분)은 현장 보고 처분 블록 D/E/B 재확인 3행 + 회신 3행 + 로드맵 R-18(D `-> NoReturn` 1줄)·R-19(E `Any` 정책 — «사용자 재확인 후» 별도 배치)로 3문서 일관 등재 — 원문 :200-211 «사용자 결정·문면+검사기 필수»가 보존됨. 닫힘.
2. 지정 MINOR 7건 전건 실물 반영: 6-2 제안 2 기각 사유 · 6-3 `evidence-alias-schema/` orig 2→0(본 재검 독립 재현 문자열 일치) · 6-4 R-15(c) · docstring :148 `_final_module_bindings`(선례 :4124 실재) · D2-1 «무변» · 통합 절 증거 폴더 주석 · 루브릭 «5항»(실물 불릿 5).
3. 미반영은 권고·선택뿐: 6-5 R-14b delegatedTo 범위 1구 · 036a874 동승 주석 · «시그니처 타입을 바꾼다» 1구 — 조건 아님.
4. rev2 문면: R2-1(`type(x) is <거부할 하위 타입>`만 · `is not <선언 타입>` 금지)·R2-2(bool 어느 수치 자리든 거부 가능) 정확, R2-3은 «공통으로» 지시문+MAJOR-3 문장 2조각(채택 시 1문장 조립). 원리 오류·규범 충돌 0 · 렌더 예제 형과 일치.
5. rev2 그래프 미반영 확인: ttl `R-3442@2026-09-03 revision 1` · «거부할 하위 타입» ttl/final.md(양 런타임 cmp 0)/rulepack 0건 — 사용자 ⓐ/ⓑ 결정 대기 그대로.
6. 회귀: 68a5141 코드 변경 = docstring 1행(양 미러 동일)+symbol_kinds 해시 재소성(HEAD sha256 선두 일치) · codex cmp/diff -rq 0 · symbol_kinds in-sync 56·27 · seal draft green 256 · mirror 11/11.
7. `make verify` 재실행 6/6 green 179초(로그 `/tmp/djr-verify.PfKQ4o`) · 전/후 tree clean · 기존 `fHh9rm` 6 로그도 전건 green 표지.
8. ledger 레인 4 지정 수치 전건 1차 자료 일치 — 4회(UTC 03:59~04:42 = KST 12:59~13:42)·스탬프 4/4·corrected 2 다음 run 소멸·형식/결손 0·G2 귀속 0(REPORT·anchor 9ee721e)·G0 12:24→REPORT 18:55 = 6h31m·해시 실측 9ee721e 6cf8e2ffdfc3→(70c766f686f6→09dbd671e00b)→67f6411 cb95a1bddb32·13:42 이후 리포트 0.
9. ledger MINOR 2: 계약 실존 집계 «행 5·밖 3»은 run 1 수치(최종 run은 행 6·밖 4 — ⑵ «6행»과 자기 불일치·결론 무영향) · 레인 4만 «pre-gate 총 소요» 절 부재(43분). 판정 규칙 정합 ✓ — 레인 2·4가 ⑴⑵⑶ 전건 충족이라 ≥2 레인 요건 문언상 성립, 레인 1 ⑶ 소멸 근거(f0fcdb4 `_Class` 파서)·09-02 ⓐ 재실측 조건 일치, 결정은 G-A 브리프로 사용자 게이트 유지.
10. 판정: **머지 가능**(조건 잔존 0 · 권고 MINOR 4 · 관찰 4). 릴리즈는 미결 2 결정(+68a5141이 항목화한 B 기록 충돌 재확인)에 종속 — 감사 판정과 동일. 1차 자료는 herdr 워크트리 소멸(머지 aacaaa0)로 spring main 체크아웃·git 이력에서 대조.
