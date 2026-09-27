# 로드맵 5 — dddjango 리팩토링 커맨드 구현 계획 v1 (2026-09-27)

- 설계 정본: `step5-refactor-command-design-v5.md`(부록 C = 재검토 N 반영) · 대상 규범 `scope-limit-norms.md`(N 반영본 — 대상 56 = ⑴ 43 · ⑵ 13 · A 40 · N 361).
- 판형: 6a `workspace/eval/web-g0-debt/plan-v2.md` · 로드맵 4 `step4-norm-map.md`·`step4-impl-log.md`·커밋 `6c4cf39f`.
- 표기: **[실측]** = 명령·파일 결과 · **[추정]** = 확인하지 않은 판단. 행 번호는 HEAD `203cdffb` 기준 실측.
- 원칙(사용자): 리팩토링은 기존 테스트 충분 가정(테스트 강화·보호·대상 프로젝트용 새 실행 장치 없음) · 이미 있는 장치로 되는 일에 새 장치 없음. 아래 `refactor_audit_fixture_run.py` 는 **플러그인 도구의 단위 시험 러너**(설계 §10 · `behavior_guard_fixture_run.py` 판형)라 이 원칙의 대상이 아니다.

## 0. 기준선

| 항목 | 값 |
|---|---|
| HEAD | `203cdffb` chore: manifest 봉인 재발행 — 로드맵 4 이후 정렬 [실측] |
| `make verify` | **green 5/5**(333초 — core 78 · ontology 84 · backstop 120 · cross 255 · regen 333) [실측 09-27] |
| 배포 여부 | 마지막 태그 `dddjango--v2.18.4`(`c1f78938` · 09-26 05:07). `e3ad8e16`·`1698dae1`·`6c4cf39f` 는 태그 밖 → **R-3470~R-3508 은 미배포**(제자리 편집) · 그 이전 R-ID 는 배포됨(뜻이 바뀌면 새 Expression) [실측] |
| ISSUED | 마지막 `R-3508`(3,508행) → **다음 R-3509** [실측] |
| rulepack | 최상위 키 `_generated·built_from·by_alias·by_checker·by_path·by_section·schema·works` · works 필드 `agents·aliases·block·block_order·checkers·document·expression·label·order_rank·section·section_number` · **`blocks`·`norm_kind`·`overrides` 부재** · works 3,508 · 규범 진술 블록 1,793 · 크기 2,259,063 B [실측] |
| 그래프 | `djr:overrides` 트리플 0 · `a djr:Override` 35 · vocab `djr.ttl:165` 에 `djr:overrides` 정의 · SHACL NormShape 에 overrides 속성 없음 [실측] |
| 계수표 | `target-counts.json`: Block 2,928 · Expression 3,721 · Norm/Work 3,517 · Section 546 [실측] |
| 결속 원형 | scratch `review-N/bind.py`(재검토 N) — Claude 1,793/1,793 · Codex 1,645/1,793 [N 실측] |

## 1. 규범 지도 (norm map)

### 1-0. 편집 방식 결정

- **새 절은 문서 끝에 붙인다** — 절 키는 서수(`s<NNN>` · `ontology_census.parse_sections` — 모든 제목 수준이 경계)라 중간 삽입은 뒤 절 전부의 Section·Block IRI·LEDGER 키·rulepack `block` 을 바꾼다 [실측 `ontology_census.py:48~108`]. 끝에 붙이면 개명 0. 선례 `56b27e12`(implementation-django final 새 절 `s094-18` · SectionShape 545→546 · LEDGER `baseline:… 새 절`) [실측].
- `ontology_render.py --apply` 는 **md 에 이미 있는 절만** 치환한다(«현재 분할에 절 없음» 오류 — `:88~99`) [실측]. 그래서 새 절은 ① md 끝에 제목 1행(+마커 1행)을 먼저 쓰고 ② 그래프에 Section·Block·Norm 을 rdflib 구조 편집으로 넣고(레시피 memory `ontology-revision-recipe` §1 · `ontology_canon.canon_turtle`) ③ `--apply` 로 본문을 투영한다.
- `ontology_migrate.py` 는 쓰지 않는다 — 문서 ttl 전체를 명세에서 다시 쓰고 T1 census 행을 요구한다(`:112~135` · 새 절은 census 행이 없다) [실측].
- 기존 절 안의 새 규범은 **기존 블록 문면 끝에 문장을 더하고 `statesNorm` 에 추가**한다(로드맵 4 판형 — 새 블록 IRI 0 · 블록 순서 불변) [실측 `6c4cf39f`].
- 개정 원칙(로드맵 3·4 와 같다): 배포 규범의 뜻이 바뀌면 새 Expression `@<구현일>`(revisionKind amendment|clarification) · 미배포 규범(R-3470~R-3508)은 제자리 편집 · **리팩토링 모드 전용 규범은 새 절에, 기능 모드 동작이 바뀌는 곳만 제자리**.
- 규범 하나 = 블록 하나(q4 «한 Work = 한 블록» fail-closed — `ontology_rulepack.py:118`) [실측].

### 1-1. Coordinator — `ontology/rules/command-dddjango.ttl` · `dddjango/commands/dddjango.md`(219행)

절 서수 [실측]: s001 1~13 (전문) · s002 14~31 산출물 위치 · s003 32~63 진행 가시성 · s004 64~68 모드 판별 · s005 69~87 Phase 0 · s006 88~107 Phase 1 · s007 108~179 Phase 2 · s008 180~184 Phase 3 · s009 185~197 수정 모드 · s010 198~210 엣지 · s011 211~219 경계.

**기존 절 개정**

| # | 행 | 블록 | 기존 R-ID [실측] | 처리 | 설계 |
|---|---|---|---|---|---|
| C1 | :67 | s004/b1 | R-0163~R-0167 · R-3470 · R-3471 · R-3472 | **신설 3**: 판별 입력 둘(정확한 표지 · 미종료 실행 줄 `· 모드 리팩토링`) + 요청문 «리팩토링 모드로» 비입력 · 단조성 불변식 · 표지 fail-closed 입구 정지. **제자리 3**: R-3470 → «표지 없는 `/dddjango` 정리만 요청은 27종 전 `/dddjango:refactor <BC>` 안내·입구 정지(기록·폴더 없음) · 혼합 요청은 기능 모드» · R-3471 → «이동 근거는 G0 ⓐ → 슬라이스 0 뿐(리팩토링 모드 포함) · 리팩토링 모드엔 배치 질문 없음» · R-3472 → 따르지 않는 지시에 R2·R3 축소(렌즈·조각·audit 재사용·판정 생략·일괄 채택·결과 지정 — 게이트 피드백 포함) | §1-2 · §1-3 |
| C2 | :79 | s005/b8 | R-0185 · **R-0186**(배포) | R-0186 새 Expression(amendment): «「리팩터링 대상」의 별도 정의는 없다» → «기능 요청의 리팩터링 대상은 백스톱 위반이다 — 리팩토링 모드는 BC 점검 항목도 대상(«리팩토링 모드» 절)» | §4-4 사본 ① |
| C3 | :80 | s005/b9 | R-0196~R-0206 · R-3473 | R-3473 제자리: ⓐ′ 안내 대상 = `/dddjango:refactor <BC>`(BC별 실행 · 의미 점검 포함 — 대가 줄) · «정리 요청은 제외» 문구 삭제. **신설 1**: 기능 모드 폴더 목록의 `refactor-` 폴더는 미종료 리팩토링 실행이 있을 때만 «미종료 리팩토링 실행 잇기»로 보인다 | §1-3 · §2-3 |
| C4 | :84 | s005/b12 | R-3481 | 제자리: «정리 요청인데» → «리팩토링 모드에서 N_c 0 · N_m 0 · 불편 0 이면» | §2-1 |
| C5 | :85 | s005/b13 | R-3482~R-3485 | R-3482 제자리: 실행 줄 `실행 · G0 승인 <값> · 모드 리팩토링`(리팩토링 모드만 · 기계 기록) | §2-2 |
| C6 | :106 | s006/b11 | R-3486 · R-3487 · R-3498 | R-3487 제자리: «`M<n>` ⓐ 항목의 이동·분할은 G0 ⓐ 근거가 있는 이동(STOP 아님) · 항목 밖 이동은 STOP» · R-3498 제자리: «정리 요청에서 재상정 뒤…» → «리팩토링 모드에서» | §6 |
| C7 | :114 | s007/b3 | R-3503 | 제자리: 창 재개설 조건에 «G2 잔존 반송(리팩토링 모드 — 원 창 종류)» | §6 · §7 |
| C8 | :174 | s007/b57 | R-3490 | 제자리: «리팩토링 모드의 M 은 «리팩토링 모드» 절의 M_c + M_m» 1구 | §7 |
| C9 | :218 | s011/b5 | R-0451 · **R-0452**(배포) · R-3494 | R-0452 새 Expression(amendment): 위임되지 않는 것에 «사용자 판단 항목(리팩토링 모드)» · R-3494 제자리: 기계 기록에 `audit/` 산출·실행 줄 모드 표기·G0 정지 절 `모드 리팩토링 · audit <R2 시각>` | §5 · §8 |
| C10 | :58 | s003/b10 | R-0151~R-0157 · R-3437 | 사전 위임 문장이 경계 절 제외 목록을 **열거해 복사**한다(«경계 절의 STOP·blocker·shape·사후 scope 개정·출처 없는 G0 ⓑ·출처 없는 실행 폐기 제외») [실측] → R-0157(배포 · 이 문장 소속 [추정 — 구현 때 블록 문장 대응 확인]) 새 Expression(amendment): 열거에 «사용자 판단 항목» · 새 절 N-G0 에 «번호 목록 먼저(R-0155)를 빚 질문에도» 1구 | §5 |
| — | :22·:24 | s002/b5·b6 | R-0136~R-0138 | **무개정** — 리팩토링 폴더 slug·후보는 새 절 예외 규범(N-R0′)이 정한다(«한 기능 = 한 폴더» 보존) | §2-3 |
| — | :35 · :94 · :116 · :117 | s003/b1 · s006/b3 · s007/b5 · s007/b6 | 배포 규범들(R-0141… · R-0213·R-0214 · R-0278… · R-0283·R-0284) | **무개정** — task 4단계의 R2 다발 · 슬롯 한도 다발 반복 · 5번 감사 조각화 · 감사 입력 `M<n>` 대응표는 전부 리팩토링 모드 전용이라 새 절 규범(N-R2 · N-P2)이 예외로 정한다 | §2-1 · §6 |

**새 절 `s012` «## 리팩토링 모드 (입구 `/dddjango:refactor`)»** — 파일 끝(경계 뒤) · 블록 13 · 신설 약 27 [추정 — 구현 때 확정]

| 블록 | 내용(설계 §) | 규범(가칭) |
|---|---|---|
| b1 | 흐름 표 R0→G2 · R0 대상 BC 1개(실재·기능 혼입·0/2개↑ → 입구 정지 · 기록·폴더 없음) · 불편 서술 = 항목 후보 | N-R0 ×2 |
| b2 | R0′ 폴더: 후보 = 같은 BC `refactor-<bc 케밥>` 만(없으면 «새 폴더»뿐 · slug 이 시점 확정 — «승인 뒤 확정» 예외) · 잇기는 `모드 리팩토링` 실행만(verdict 동결) · 새 실행은 R2·R3 새로 · `/dddjango` 재개 전환 지점 | N-R0′ ×3 |
| b3 | G0 정지 재개: audit·verdict 재사용 조건(`git diff --quiet` + untracked 없음 + `check-verdict` exit 0) · 거부는 본인 직접 | N-R0″ ×1 |
| b4 | R1 = Phase 0 3번 그대로 · `C<n>` 부여(스캔 표 순서) | N-R1 ×1 |
| b5 | R2: `refactor_audit.py plan`·`outline` 출력대로 BC_AUDIT 다발 · 파견 입력(조각·outline 경로·렌즈·`C<n>`·불편·**적용 범위 규범 원문**) · 받은 표 그대로 Write(대화 재출력 금지) · 슬롯 한도 단위 반복은 위반 아님 · task 4단계에 R2 다발 | N-R2 ×2 |
| b6 | R2′: `check` → 불일치 행만 원 리뷰어 1회 재인용 → 다시 `check` → 남으면 «인용 불일치» 목록 | N-R2′ ×1 |
| b7 | R3: architect «의미 항목 판정» 파견(`check.md`·`sections.md`·`outline.md`·`C<n>`) · `check-verdict` exit 0 까지 · red 면 1회 재호출 → 또 red 면 `--final`(채택 재분류 기록) | N-R3 ×2 |
| b8 | **적용 범위 규범**(Override · ⑴·⑵ 문면 + 어구 40 «…») — `djr:overrides` 56 · enforcedBy `c/refactor_audit.py` | N-OV ×1 |
| b9 | G0 배너 1행(계수 = `check-verdict` `요약:`) · 규모 1행 · 문서 층 변경 1행 · 질문 순서(폴더·실행 → 사용자 판단 → 빚 → 승인) · ⓐ′ 없음 · «미룰 수 없음»은 `C<n>` 만 · 목록 표시(제외·오탐·별도 요청·병합→C·인용 불일치·규칙 근거 없는 불편 — 경로·건수) · 번호 목록 먼저(:58 규칙을 빚 질문에도) | N-G0 ×3 |
| b10 | 사용자 판단: G0 질문(STOP 아님) · 대리 답 불수용(사유 = 규범 해석 선택) · 결정 줄 `M<n> · 사용자 판단 = 위반|허용 · 출처 = …` · 수정 요청 = 판정 근거 오류 지적만 · 결과 지정은 사용자 판단 범주로만 · 대리 출처 축소 금지(재실행 입력 첫 줄 = 결정 출처 정형) · 끝 선택지 | N-G0′ ×3 |
| b11 | Phase 1~2: 슬라이스 0 만 · 파견 입력 = `모드 리팩토링`·`M<n>` ⓐ 목록·**적용 범위 규범 원문**(architect 명세·Phase 1 리뷰어·acceptance-tester·coder·DR) · 슬라이스 0 엔 ⑴ 만 · 5번 감사 입력에 `M<n>` 대응표(diff 대조) · 조각 감사 + 홀리스틱 = 종합 + 경계 교차 | N-P ×3 |
| b12 | G2: M_c(현행 ∩ `C<n>` ⓐ · 병합→C 는 그 `C<n>`) · M_m(`residual` 층 판정) · M>0 → 원 창 종류 새 창 반송 1회 → 그래도 M>0 → `ⓐ 재상정` STOP · 배너 다섯 목록 재표시 | N-G2 ×3 |
| b13 | 기계 기록(`audit/<R2 시각>/` 전부 · 실행 줄 모드 · G0 정지 절 표기)은 사후 개정 아님 | N-REC ×1 |

- 배선(`wiring/command-dddjango.ttl`): 전부 `delegatedTo` Coordinator, 도구가 판정하는 것(N-R2′·N-R3·N-OV·N-G0 계수·N-G2 M_m)은 `enforcedBy c/refactor_audit.py` 도 [추정].
- 합계(Coordinator): 신설 약 31(s004 3 · s005 1 · s012 약 27) · 새 Expression 3(R-0186·R-0452·R-0157) · 제자리 11(R-3470·R-3471·R-3472·R-3473·R-3481·R-3482·R-3487·R-3498·R-3503·R-3490·R-3494).

### 1-2. 에이전트 7 — 새 절(끝) + 모드 무관 1행

절 서수 [실측]: architect s001~s007(경계 107~112) · ddd s001~s005(경계 44~49) · api s001~s007(실행 모드 s002 13~20 · 입력 s003 · 경계 86~91) · db s001~s005 · DR s001~s008(Phase 2 점검 s007 69~134 · 경계 s008) · acceptance-tester s001~s005 · coder s001~s006.

| 에이전트(ttl) | 1행 위치(모드 무관) | 새 절(파일 끝) | 그 밖 | 신설 [추정] |
|---|---|---|---|---|
| design-review-ddd | s002/b1 끝(입력 — R-3368·R-3369 블록) | s006 «## BC 점검 모드 (BC_AUDIT)»: 기본 모드 = Phase 1 · 명시 입력 때만 · 점검 절 목록(도메인 렌즈) · 산출 표(설계 §3-3) · 표만 낸다 · 테스트 충분성 비항목 · 코드 수정 금지 · G2 «잔존 확인» 입력·결과 형식(해소는 새 `파일:행` 필수) | — | 5 |
| design-review-db | s002/b1 끝(R-3323·R-3324) | s006 같은 틀 + ORM·보안 약 117(implementation-django 절 — 플러그인 루트 경로로 읽기) · 보안 절은 db 가 켜지면 db | — | 5 |
| design-review-api | s003 입력 끝 블록(R-2614 블록 — `:20` 은 s002/b3 R-2613) [실측] | s008 같은 틀 + ninja 약 80 · 보안 대행 조건(db 렌즈 꺼짐) | s002 실행 모드 끝에 모드 이름 `BC_AUDIT` 1구(신설 1) | 6 |
| discipline-reviewer | s002 입력 끝 블록 | s009 같은 틀 + 구현 체크리스트 적용 범위(입장 표·diff 전제 항목 제외 — R-0919 는 ⑵ 로 풀림) · python 약 73 · 테스트 항목 = 배치·파일·디렉터리 이름(**케이스 이름 제외**) · 쿼리·ORM 관용구는 db 몫 | — | 6 |
| design-architect | s002 입력 끝 블록 | s008 «## 의미 항목 판정 모드»: 판정 범주 6 · `M<n>` 부여·유지 · 출구별 근거 형식(§4-3) · 근거는 `sections.md` 뿐(자기 스킬 밖 규범 탐색 금지) · 비용·일정 사유 금지 · `verdict.md` 는 `:32`(s003/b1 R-1567 «다른 산출물은 만들지 않는다»)·`:112`(s007/b3 R-1760 «스킬 경계») 의 **예외**(Exception 규범 — 배포 규범 무개정) · 코드 수정 금지 | — | 5 |
| acceptance-tester | s002/b1 끝(R-3238~R-3242) | — | 리팩토링 모드 파견 입력(모드·`M<n>` 목록·원문) 1구 | 2 |
| coder | s002 입력 끝 블록 | — | 같음 | 2 |

- 1행 문면(7곳 동일): «파견 입력에 적용 범위 규범이 실려 있으면 그 규범이 정한 몫과 때를 따른다.»
- 합계(에이전트): 신설 약 31 · 새 절 5(ddd s006 · db s006 · api s008 · DR s009 · architect s008).
- **전체 신설 약 62**(R-3509~R-3570 [추정]) · 새 Expression 5(R-0186 · R-0452 · R-0157 · R-3226 · R-0096) · 새 절 6(SectionShape 546 → 552).

### 1-3. 사본 셋 정정 (설계 §4-4 끝)

| 사본 | 위치 [실측] | 규범 | 처리 |
|---|---|---|---|
| Coordinator `:79` | s005/b8 | R-0186 | C2 |
| houserules final `:282` | `discipline-houserules-final` s014/b1 | R-3226(배포) · R-3227 · R-3228 | R-3226 새 Expression(amendment) — «기능 요청의 리팩터링 대상» · 소스 미러 `workspace/reference/discipline-houserules/reference/final.md` 수동 span 교체 → `corpus_mirror_sync.py --write`(Codex byte `codex-dddjango/skills/dddjango-discipline-houserules/references/final.md`) |
| ninja final `:858` | `implementation-django-ninja-final` s023-6.2/b36 | R-0094~R-0097(문장은 R-0096 — N·금지) | R-0096 새 Expression(clarification) · 소스 미러 동일 절차(Codex `codex-dddjango/skills/implementation-django-ninja/references/final.md`) |

### 1-4. 적용 범위 규범과 `djr:overrides`

- N-OV(Override · s012/b8) `djr:overrides` 목적어 56 = 분류 표 1(58) − R-3226 · R-0186. 몫 ⑵ 13 = R-2614 · R-3323 · R-3368 · R-0965 · R-0982 · R-1058 · R-1059 · R-3420 · R-3422 · R-1137 · R-1140 · R-0919 · R-0284 · 몫 ⑴ = 나머지 43. 그래프에는 몫 구분을 싣지 않는다(문면이 가른다 — 설계 §8).
- 어구 40 은 규범 문면에 «…» 로 싣고 `refactor_audit.py` 상수와 `--self-test` 가 대조한다.
- SHACL: `djr:NormShape-overrides`(path `djr:overrides` · class `djr:Norm` · nodeKind IRI) 추가 → `ontology_meta_shacl.py`(meta-SHACL 2층)·`shapes/golden` 영향 확인 [추정 — 구현 첫날].

## 2. 투영·도구

### 2-1. rulepack 3필드 — `workspace/tools/ontology_rulepack.py`(274행)

| 필드 | 경로 | 비고 |
|---|---|---|
| `works[*].norm_kind` | q4 `q4-injection-order.rq` SELECT 에 `?normKind`(VALUES {Obligation Prohibition Permission Exception Override} 로 rdf:type 한정) + GROUP BY 추가 → 생성기 `works[wid]` | 종류 1개 단언(아니면 problems) |
| `works[*].overrides` | q4 에 `GROUP_CONCAT(?ov)` (`OPTIONAL { ?work djr:overrides ?ov }`) → 정렬 목록 | 56 트리플 |
| 최상위 `blocks` | 생성기가 `g` 에서 직접: `statesNorm` 을 가진 블록마다 `djr:text` 를 읽어 `h = sha256(normalize(text))[:16]` · `n = 행 수(끝 개행 규칙은 `review-N/bind.py:nlines`)` · `works` = statesNorm R-ID 정렬 | **본문은 싣지 않는다**(q4 는 계속 `djr:text` 미추출 — 파일 머리 계약 · E8). 정규화 함수는 `dddjango/scripts/refactor_audit.py` 의 `normalize` 를 import(선례: 생성기가 `dddjango/scripts/rulepack.py` 의 `validate_glob` 를 import — `:176~179`) → 단일 출처 |

- 스키마 문자열 `rulepack/1` 유지(추가만 — 읽기 모듈 `rulepack.py:116~131` 은 모르는 키를 거부하지 않는다 [실측]).
- 연쇄: `make rulepack` → `ontology_rulepack.py --check`(verify-base-core) · `rulepack_smoke.py` G4 «본문 미동봉» 은 해시라 통과 [추정] · `query_golden_check.py --emit`(q4 `distinct_works` 3,508 → 약 3,570) · `target-counts.json`(Norm/Work/Expression/Block/Section) · Codex byte 미러 `codex-dddjango/skills/dddjango/scripts/rulepack.json` 은 생성기가 함께 쓴다(`MIRROR_OUT`).
- 크기: 블록 1,793 × 약 90 B ≈ +160 KB [추정].

### 2-2. `dddjango/scripts/refactor_audit.py` (신설 · stdlib · Codex byte 미러)

| 하위 명령 | 입력 → 출력 | 핵심 알고리즘 | exit |
|---|---|---|---|
| `plan <bc>` | 대상 프로젝트 cwd · `application/<bc>/` → stdout 표 + `audit/<R2 시각>/plan.md`(조각별 파일 목록) | 렌즈: ddd·discipline 항상 · api = HTTP 어댑터 파일(`driving_layer/api/**` 또는 ninja Router·api_controller AST) · db = `models.Model` 하위 클래스(AST) · 보안 절 = db 켜지면 db 아니면 api · 조각 = #81 층 순서(`standard_tree.py` import) · 문턱 5,000행 · 초과 단일 파일 단독 조각 · 트리 밖 조각 | 0 / 1 도구 오류 |
| `outline <bc> --out <audit>` | → `outline.md` | 파일별 최상위 def/class/메서드 + 행(AST) | 0 / 1 |
| `check <audit>` | `<렌즈>-<조각>.md` 표 → `check.md` | 행마다 ① 인용 ⊂ 인용 문서 §절 본문(정규화: `**`·`*`·백틱·줄머리 `> ` 제거 + **공백류 전부 제거**) ② `파일:행` 실재·BC 안 → **블록 결속**: rulepack `blocks` 를 문서별·`n` 별로 묶어 설치본 문서 행에 `n` 행 창을 밀고 해시 일치 범위 [i,j] → 인용 ⊂ 범위 본문이면 그 블록 `works`·`norm_kind` 부착 · **서로 다른 블록 둘 이상 적중 = 결속 실패** · 결속 실패 행은 R-ID 없음(제외·오탐 근거 불가) | 0 전건 통과 / 2 불일치 있음 / 1 |
| `sections <audit>` | → `sections.md` | 인용 절 + 반대 방향 절 전체 원문 + 블록별 `R-ID · 종류 · 라벨` 주석 + 적용 범위 규범 원문 + 대상 목록(`R-ID · 종류 · 라벨` — 목록은 N-OV 의 `overrides`) | 0 / 1 |
| `check-verdict <audit> [--feedback <파일>] [--final]` | `verdict.md` → `verdict-log.md` append + stdout `요약:` 1행 | 판정 1개·`M<n>` 유일 · **제외** ① 결속 ② 근거 R-ID ∈ 결속 블록 works ∧ (종류 ∈ {Permission, Exception} ∨ 리뷰어 «반대 방향 규칙» 열의 결속 R-ID) ③ 근거 ∉ 대상 56 ∪ {N-OV} ∧ (결속 블록 works ∩ 대상 ≠ ∅ → **인용이 든 문장**에 A 어구 없음) ④ 혼합 블록이면 제외 인용 구간 ∩ 위반 인용 구간 = ∅ · **오탐** 인용 ⊂ 위반 행 결속 블록 + 같은 문장 A 규칙 · **별도 요청** 리뷰어 «아니오» 없으면 채택 재분류 + 근거 유형(모델 필드 AST · HTTP 어댑터 층 응답·예외 정의 행 · `application/<다른 bc>/` — 합성 파일은 BC 범위) · **병합** M→M 대상 채택만 · M→C 리뷰어 «`C<n>` 과 같음» 행만 · **사용자 판단** 반대 방향 인용에 ③ 식 · **대리 축소** `--feedback` 첫 줄 결정 출처가 대리면 앞 판정 대비 채택→비채택 전환 red · `--final` = 남은 red 행을 채택으로 기록하고 0 | 0 / 2 red / 1 |
| `residual <폴더> [--finalize <시각>]` | `refactor-scope.md`(ⓐ `M<n>`)·`build_anchor`·0C 대응표(`behavior/` close 기록) → `residual/<시각>/bottom.md` + `review-<렌즈>.md` / `--finalize` → 리뷰어 `result-<렌즈>.md` 대조 · stdout `요약: M_m=…` | 결정적 바닥: 항목 파일이 `build_anchor..작업 트리` 무변 → 잔존 · ⓓ 겹침은 대응표 새 경로에 같은 `[ⓓ#N]` → 잔존 · 나머지만 렌즈별 묶음 · «해소»는 새 `파일:행` 실재 검사(없으면 잔존) | 0 / 2 M_m>0 / 1 |
| `--self-test` | — | 렌즈별 점검 절 목록의 절 실재 · 경로 사상표 · A 상수 = N-OV 문면 «…» | 0 / 1 |

- **문장 분할**: 결속 범위 원문을 `다.`·`.`+공백·목록 머리(`- `·`* `·`1. `)·표 칸(`|`)·원숫자(①~⑳)·빈 줄에서 나눈 뒤 문장별 정규화 · 인용이 걸친 문장 전부가 판정 대상.
- **플랫폼 경로 사상**: 자기 위치로 판별(`<scripts>/../commands/dddjango.md` 있으면 Claude, `<scripts>/../SKILL.md` 면 Codex · `--platform` 로 강제). rulepack `document` `dddjango/<rel>` → Claude 플러그인 루트 `<rel>` · Codex: `agents/<a>.md` → `skills/dddjango-<a>/SKILL.md` · `commands/dddjango.md` → `skills/dddjango/SKILL.md` · `skills/<x>/…` → `skills/dddjango-<x>/…` 있으면 그것, 없으면 `skills/<x>/…`(corpus_mirror_sync `paths_for` 규칙과 같다 — `:110~118` [실측]).
- 점검 절 목록(렌즈별 `문서 §절`)은 진단 5B §1-4 분류 방법으로 뽑아 리뷰어 새 절 문면에 고정하고, 같은 목록을 도구 상수로 둬 `--self-test` 가 절 실재를 본다(구현 2일차 — scratch 스크립트로 추출).
- 원형 재사용: `review-N/bind.py`(결속) · `sentlevel.py`(문장 단위) · `afree.py`(부분 인용) — scratch 전용, 저장소에 넣지 않는다.

### 2-3. 단위 시험 러너 — `workspace/tools/refactor_audit_fixture_run.py` (신설)

- 판형: `behavior_guard_fixture_run.py`(합성 git 저장소 · 사례별 exit·요약 대조). 편입: Makefile `verify-base-regen` 에 1행(behavior_guard 러너 옆) · 봉인 밖(pregate·behavior 러너 선례).
- 사례(설계 §10 + 부록 C): plan 결정성·보안 대행 · outline 산출 · check(날조·틀린 절·BC 밖 → 불일치 · 마크업 · 줄바꿈 걸친 인용 통과 · 두 블록 적중 → 결속 실패) · 결속 전수(Claude 1,793/1,793 단언 · Codex 결속률 **기록**) · check-verdict 13종(의무 제외 · 대상 R-0674/R-0965/R-0982/R-0125 제외 · N-OV 제외 두 경로 · R-0125 부분 인용 + R-0117 · R-0183 제외 · touched 인용 오탐 · 다른 문장 오탐 · 혼합 겹침 · «아니오» 없는 별도 요청 재분류 · 같은 파일·표시 없는 M→C · 대리 축소 · 사용자 판단 대상 문장 red / 형제 문장 통과 · `--final` 재분류) · residual(무변 → 결정적 잔존 · 근거 없는 해소 → 잔존) · `--self-test`.
- 결속 사례는 저장소 `dddjango/`·`codex-dddjango/` 를 코퍼스로 쓰고, 판정 사례는 합성 `verdict.md` 에 실제 R-ID 를 쓴다(rulepack 은 작업 트리 것).

### 2-4. 등재

| 대상 | 파일 | 처리 |
|---|---|---|
| Codex byte 미러 | `codex-dddjango/skills/dddjango/scripts/refactor_audit.py` | `cp` — verify-base-core `diff -rq dddjango/scripts …` 가 잡는다 [실측 Makefile] |
| registry Checker 개체 | `ontology/wiring/registry.ttl` | `<djr#c/refactor_audit.py> a djr:Checker` (선례 `:28` behavior_guard · `:112` design_pregate) |
| rulepack_smoke 명부 | `workspace/tools/rulepack_smoke.py:88` roster | `"refactor_audit.py"` 추가 |
| 라벨 드리프트 | `rulepack_smoke.py` 새 검사 G12 | 식(`scope-limit-norms.md` «라벨 드리프트 식») 적중 − 검토 완료 ID 집합(적중 319 · ID 만) ≠ ∅ → red · 신설 약 62 의 라벨도 식에 걸리면 집합에 넣는다 |
| reverse_coverage | `workspace/tools/reverse_coverage.py:137~147` 옆 | `refactor_audit.py` 설명 행 |
| 봉인 | `workspace/tools/manifest_seal.py:71~84` pipeline globs | `dddjango/scripts/refactor_audit.py` · `dddjango/commands/refactor.md` 명시 등재(현행은 `commands/dddjango.md` 한 파일 고정) · plugin_payload 의 `codex-dddjango/skills/**/*.md|*.yaml` 은 새 Codex 스킬을 이미 덮는다 [실측] |
| runtime parity | `workspace/tools/runtime_parity_check.py` SECTIONS | `("리팩토링 모드", r"^## 리팩토링 모드", None)` + `_extract` 가 end=None 이면 파일 끝까지(3행 수정 — 두 런타임 모두 절이 파일 끝) · NORMALIZE 에 `/dddjango:refactor` ↔ `$dddjango-refactor` 표기 1쌍 [추정] |

## 3. 입구

| 파일 | 내용 | 검증 |
|---|---|---|
| `dddjango/commands/refactor.md`(신설 · 산문) | frontmatter `description`·`argument-hint: <대상 BC> [불편 서술]`·`disable-model-invocation: true`·`allowed-tools: Skill(dddjango:dddjango)` + 본문 3~5줄(설계 §1-1 — 표지 원문 한 글자도 바꾸지 말고 Skill args 로) | `claude plugin validate dddjango --strict` |
| `workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv` | 행 `command-refactor	dddjango/commands/refactor.md	<행 수>	E10` | `ontology_ledger_check.py`(새 절 무단 등장 검출 ②) |
| `ontology/LEDGER.tsv` | `command-refactor	s001	<sha256>	prose	-	-	-	-	baseline:<날짜> 로드맵 5 입구` | 같음 |
| `workspace/tools/corpus_lint.py:57~84` | `collect_docs` 에 `commands/*.md` · `is_normative` 에 `commands/` 전부 | verify-base-core |
| `dddjango/.claude-plugin/plugin.json` | description 에 «/dddjango:refactor 로 대상 BC 전체를 표준으로 정리» 1구 | validate |
| `codex-dddjango/skills/dddjango-refactor/SKILL.md`(신설) | 얇은 스킬(설계 §1-1 문면 — `wc -l` → 구간 읽기 · `scripts/` 기준 = 형제 `dddjango/` · 첫 줄 = 표지 + 인자) | 구현 때 Codex 1회(R-T0) |
| `codex-dddjango/skills/dddjango-refactor/agents/openai.yaml`(신설) | `interface`(display_name 등 — `dddjango/agents/openai.yaml` 판형) + 암묵 호출 차단 키 | **구현 첫날 실측**: `allow_implicit_invocation` 키 이름·위치(저장소에 선례 0 [실측]) — Codex 바이너리 문자열·공식 문서로 확인, 없으면 description 에 «명시 호출 전용» 문면으로 갈음하고 기록 |
| `codex-dddjango/.codex-plugin/plugin.json` | `interface.longDescription` 에 리팩토링 입구 1구 | — |

## 4. Codex 의미 미러 (손 미러 — `corpus_mirror_sync` 밖)

| Claude | Codex | 내용 |
|---|---|---|
| `commands/dddjango.md` C1~C9 + 새 절 | `codex-dddjango/skills/dddjango/SKILL.md`(235행 · 끝 절 `## 경계` 227) | 같은 개정 + 파일 끝 `## 리팩토링 모드` — parity 대조 대상(정규화 뒤 동일) |
| `agents/design-review-ddd.md` | `skills/dddjango-design-review-ddd/SKILL.md` | 1행 + BC_AUDIT 절 |
| `agents/design-review-db.md` | `skills/dddjango-design-review-db/SKILL.md` | 같음 |
| `agents/design-review-api.md` | `skills/dddjango-design-review-api/SKILL.md` | 같음 + 모드 이름 |
| `agents/discipline-reviewer.md` | `skills/dddjango-discipline-reviewer/SKILL.md` | 같음 |
| `agents/design-architect.md` | `skills/dddjango-design-architect/SKILL.md` | 1행 + 판정 모드 절 |
| `agents/acceptance-tester.md` | `skills/dddjango-acceptance-tester/SKILL.md` | 1행 + 파견 입력 |
| `agents/coder.md` | `skills/dddjango-coder/SKILL.md` | 1행 + 파견 입력 |
| 기술 규칙 경로 열람 | 역할 SKILL 4(ddd·api·db·DR) | Codex 경로(`skills/implementation-django-ninja/…` 등) 표기 |
| houserules·ninja final | corpus_mirror_sync `--write` 가 byte 미러 | — |

- 행 번호 표기 차이(`dddjango:` ↔ `dddjango-` · `AskUserQuestion` ↔ 게이트 질문 채널)는 parity NORMALIZE 가 이미 흡수한다 [실측].

## 5. 가이드·문서

| 파일 | 위치 [실측] | 처리 |
|---|---|---|
| `dddjango/REQUEST_GUIDE.md`(203행 · byte 미러 `codex-dddjango/REQUEST_GUIDE.md`) | §4 `:86~128` · §6 `:147~176`(정리 문단 `:163~175` — «지금은 하지 않으며» `:173~174`) · §7 `:177~197` | 새 소절 «리팩토링 요청»(§6 뒤 또는 §6 안 — 정리 문단 `:163~175` 를 대체): 언제·인자(BC 1 + 불편)·적을 것/적지 않을 것·새 동작이면 입구 정지·테스트 단언·보호는 고치지 않음 · `/dddjango` 에 정리만 요청하면 안내로 멈춤 · §4 에 «전용 커맨드는 진행 방식을 고르는 입구» 예외 1행 · §7 에 모델형 대리는 `/dddjango` 에 정확한 표지 줄 · 사용자 판단 항목은 대리 답 불가. Codex 판(`$dddjango-refactor`) 예시 병기. `request_guide_contract.py` 는 링크 계약만 본다(상대 링크 금지) [실측] |
| `README.md` | `:303` «커맨드 1개» · `:5`·`:107`·`:120`·`:152` 사용 예 | «커맨드 2개»(`/dddjango:dddjango` · `/dddjango:refactor`) + 사용 예 1행 |
| `AGENTS.md` | `:21` `commands/dddjango.md`(Coordinator) | `commands/refactor.md`(입구) 추가 |
| `docs/DEVELOPMENT.md` | `:20` 트리 | 입구 파일 보호(봉인 pipeline 등재) 1행 |
| `docs/work_flow.html` | archify 산출 | 리팩토링 입구 경로 1갈래(memory `archify-workflow-quirks` 판형 · 전수 검증) — 구현 리뷰 전 |
| 조감도 `workspace/design/ontology-adoption-map.html` | 설계 단계 행 | 구현·검증 결과 행 |

## 6. 행동 시험 R-T0~R-T19

- 환경: scratch `$SCR/r5/`(`$SCR` = 세션 scratchpad) · spring_dream 은 `git clone --shared /Users/hyun/Desktop/spring_dream_server $SCR/r5/sds-<ID>`(원본 무접촉 · 커밋 고정 — 첫 실행 때 HEAD 기록 · 오늘 [실측] `96f8bd7f3`). 플러그인은 작업 트리 `dddjango/`.
- **모의 실행**(대부분): 로드맵 1 판형(`bt/` — 서브에이전트가 작업 트리 Coordinator 로서 첫 사용자 입력·STOP 까지 · 공통 지시 `bt/tester-common.md` 를 `r5/tester-common.md` 로 복사·개정 · 보고 `r5/out/<ID>.md`). 모델 호출이라 **구현 단계에서 실행**.
- **실하네스**: R-T0 만(`claude -p` · Codex CLI) — 구현 단계에서 실행.

| # | 방법 | 픽스처·명령 | 합격 판정 문장 |
|---|---|---|---|
| R-T0 | 실하네스 | `cd $SCR/r5/sds-T0 && claude -p --plugin-dir /Users/hyun/Desktop/dddjango/dddjango "/dddjango:refactor service_policy"` (+ Codex: `codex exec` 동형 1회 — 명령은 구현 첫날 확정) | Skill 1회 · `빌드할 기능` 행에 표지 원문 · 27종 절대 경로 실행 · 권한 거부 0 · R2 파견 = `plan` 출력 · (Codex) 비-final 인용 1건 결속 · 결속 실패 블록 인용이 나오면 기록 |
| R-T1 | 모의 | 입구 표지 요청 · 같은 BC `refactor-service-policy` 폴더 유무 두 판 | 폴더 확정이 R1 앞 · 후보 = 같은 BC `refactor-` 폴더(있으면 그것만) · 승인 시 실행 줄 `모드 리팩토링` |
| R-T2 | 모의(실 BC_AUDIT) | service_policy 전 렌즈 · `refactor_audit.py plan/outline/check` 실제 실행 | `check` 통과 행 인용 실재 · 재인용 뒤 불일치 ≤ 10% · 5B 표본 R-1513 계열 발견 ≥ 1 |
| R-T3 | 모의 | R-T2 산출로 architect 판정 → `check-verdict` | exit 0 · 비용 사유 제외 0 · 대상 목록·N-OV 근거 제외 0 · 규칙 충돌 행 → 사용자 판단 |
| R-T4 | 모의 | R-T3 산출로 G0 | ⓐ′ 없음 · 별도 요청 질문 없음 · 사용자 판단 대리 답 거부 · 다섯 목록 표시 |
| R-T5 | 모의 | `/dddjango` + «구조 정리만»(표지 없음) | 27종 전 입구 정지 · 리팩토링 커맨드 안내 · 폴더 생성 0 |
| R-T6 | 모의 | `/dddjango` + «리팩토링 모드로» + 기능 | 리팩토링 모드 아님 |
| R-T7 | 모의 | `/dddjango` + 정확한 표지(위조) | 리팩토링 모드 · G0 의무 전부 |
| R-T8 | 모의 | 입구 + «ddd 만 · 판정 생략» | 지시 무시 · R2 = `plan` · R3 수행 |
| R-T9 | 모의 | 입구 + 불편 서술에 새 API | 입구 정지 · `/dddjango` 안내 |
| R-T10 | 책상 재생 | G2 직전 상태 픽스처(`r5/state/T10/` — `refactor-scope.md` 실행 줄 `모드 리팩토링`) · `/dddjango 이전 작업 이어서` | G2 가 새 절 산식 · M_m 유지 |
| R-T11 | 도구 + 책상 | 무변 코드 2회 · 고친 픽스처 → `residual` | 무변 = 결정적 잔존 전건(리뷰어 0회) · 고친 것 = 해소 전건(근거 실재) |
| R-T12 | 모의 | 기능 요청 Phase 1 리뷰어(BC_AUDIT 입력 없음) | 코드 열람 0 |
| R-T13 | 책상 재생 + 도구 | 재생판(`839af8a0a` 에서 추가 테스트 파일 뺀 판 · 큰 파일 분할 · 흩어진 규칙) 0C 판정 + 합성 fixture(함수형 Router → 클래스 컨트롤러) `check-verdict` | 재생판 0C 판정 기록 · 예시 2 채택(R-0674·R-0697 근거 제외 red) |
| R-T14 | 모의(대형) | fortune_library(py 587 · 29,648행 [실측]) R2 | 호출 수·토큰·벽시계·Coordinator 컨텍스트·Codex 동시 슬롯·`outline` 크기 기록(합격선 없음) |
| R-T15 | 도구 | 다른 문장 · 한정 어구 · 부분 인용 오탐 | `check-verdict` red |
| R-T16 | 모의 | G0 정지 → 재개(무변 · 변경 · 새 untracked 세 갈래) | 무변 = 재사용 · R1 만 / 변경·새 파일 = 새 점검 |
| R-T17 | 도구 + 모의 | 대리 출처 수정 요청(제외·병합→C 두 갈래) | red · 채택 수 유지 |
| R-T18 | 모의 | 기능 발주 본문에 입구 이름(표지 접두 아님) | fail-closed 발화 안 함 |
| R-T19 | 책상 재생 | G2 잔존 반송 상태 | 원 창 종류로 새 창 · close 뒤 residual 재실행 |

- 행동 시험은 대상 프로젝트 테스트를 강화·추가하지 않는다(원칙). R-T13 재생판은 선례 커밋에서 **추가 테스트 파일을 뺀** 판이다.

## 7. 작업 순서·체크포인트·봉인·커밋

| 단계 | 일 | 체크포인트 |
|---|---|---|
| 1 | 투영(q4·생성기·SHACL·`blocks`) — 그래프 무개정 상태에서 먼저 | `make rulepack` · `ontology_rulepack.py --check` · `query_golden_check.py` · `rulepack_smoke.py`(+ `--mutation-test`) · verify-ontology |
| 2 | `refactor_audit.py`(plan·outline·check·sections) + 러너 전반 | 러너 결속 1,793/1,793 |
| 3 | check-verdict·residual·self-test + 러너 전건 | 러너 green · Codex byte 미러 `diff -rq` |
| 4 | graph 일괄: 새 절 6 · 신설 약 62 · 새 Expression 5 · 제자리 · `djr:overrides` 56 · 배선·registry → gate → `ontology_render.py --apply` 9 doc(command-dddjango · agent 7 · houserules-final · ninja-final) → LEDGER 재기준선(graph 절마다 · 새 절 `baseline:… 새 절`) → 계수표 → q4 골든 → `make rulepack` → 소스 미러 2 + `corpus_mirror_sync --write` | `make verify-ontology` · verify-base-core |
| 5 | 입구 · 매니페스트 · corpus-manifest · LEDGER prose · corpus_lint | `claude plugin validate dddjango --strict` · verify-base-core |
| 6 | Codex 의미 미러 9 + 얇은 스킬 + yaml + parity | `runtime_parity_check.py` · verify-base-regen |
| 7 | 가이드·README·AGENTS·DEVELOPMENT·work_flow | `request_guide_contract.py` · byte 미러 cmp |
| 8 | 행동 시험(R-T0~R-T19) → 보정 | `r5/behavior-tests.md` 기록 |
| 9 | 독립 구현 리뷰 → 처분 → 조감도 | 리뷰 파일 `review-O-step5-impl.md` [가칭] |
| 10 | `make verify` · `make verify-mutation` → **`manifest_seal.py --write` 마지막 쓰기** → `make verify` 재확인 → feat 커밋 → 재봉인 chore 커밋 | 커밋 메시지의 verify n/n 은 커밋 직전 실측 로그만 |

- 봉인: pipeline 그룹에 새 파일 2개 등재(§2-4) → `--write` 뒤 봉인 대상이 한 글자라도 바뀌면 봉인부터 다시(memory 레시피 §8).
- **커밋에 넣을 것**: `dddjango/**`(commands 2 · agents 7 · skills houserules·ninja final · scripts `refactor_audit.py`·`rulepack.json`) · `codex-dddjango/**`(SKILL 9 · 새 스킬 · scripts 미러 · rulepack 미러 · final 2 · REQUEST_GUIDE · plugin.json) · `ontology/**`(rules 10 · wiring · shapes · ISSUED · LEDGER) · `workspace/tools/**`(생성기 · q4 · 러너 · rulepack_smoke · reverse_coverage · manifest_seal · runtime_parity_check · corpus_lint) · `workspace/eval/fixtures/**`(target-counts · query-golden) · `workspace/eval/ab/T2-0b-manifest.json` · `workspace/reference/**`(소스 미러 2) · `workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv` · `Makefile`(verify-base-regen 1행) · README · AGENTS · docs(DEVELOPMENT · work_flow) · 조감도 · 로드맵 5 문서 묶음(진단 5A/5B/5C · morning-briefs · 검토 K/L/M/N · 스파이크 · 설계 v1~v5 · `scope-limit-norms.md` · 이 계획 · 계획 리뷰 · 구현 기록 · 구현 리뷰 · progress · evening-report).
- **넣지 않을 것**: `docs/master.html` · `workspace/eval/field-report-4/…` · `workspace/plan/2026-09-26-refactor-campaign/` · `workspace/plan/2026-09-26-request-guide-audit/synthesis-v2.md` · `workspace/eval/web-g0-debt/`(6a 몫). **6a 와 겹치는 파일**: `Makefile`(6a 는 verify-web · 5 는 verify-base-regen) · `ontology-adoption-map.html`(두 행) · `progress.md` — 두 작업이 작업 트리에 같이 있으면 `git add -p` 로 hunk 를 가른다. 6a 가 먼저 커밋되면 겹침이 사라진다.
- push 없음(릴리즈는 로드맵 9 의 `make release`).

## 8. 작업량 재추정

| 몫 | 일 [추정] |
|---|---|
| 투영(q4·생성기·SHACL·블록 해시·골든·smoke) | 1.0 |
| `refactor_audit.py` 6 하위 명령 + self-test | 4.0 |
| 단위 시험 러너(약 40 사례) | 1.5 |
| graph 일괄(새 절 6 · 신설 약 62 · Expression 5 · 제자리 · overrides 56 · render 9 · LEDGER · 계수 · 소스 미러) | 3.0 |
| 입구 · 매니페스트 · Codex 의미 미러 9 + 얇은 스킬 + parity | 1.5 |
| 가이드·문서·work_flow | 0.5 |
| 행동 시험 20(모의 17 · 실하네스 1 · 도구 2 겸) + 보정 | 3.0 |
| 구현 리뷰 + 처분 | 1.5 |
| verify·봉인·커밋 | 0.5 |
| **합계** | **16.5** |

- 설계 추정 12~17일 대비 **15~19일**로 올린다. 근거: 재검토 N 뒤 새 절이 1 → 6(에이전트 5 추가 · N-M2 수신자 7) · 신설 규범 약 62(설계는 수를 적지 않았다) · 로드맵 4 실적이 추정 ×1.5 였다. 하단 15 는 행동 시험 보정이 1회로 끝날 때.

## 9. 위험과 미결

| # | 내용 | 처리 |
|---|---|---|
| 1 | 새 절을 «경계» 뒤에 둔다 — 읽는 순서상 경계가 끝이 아니다 | 자명(개명 0 · 선례 `56b27e12`) — 묻지 않는다 |
| 2 | Codex `allow_implicit_invocation` 키 실재 | 구현 첫날 실측 · 없으면 문면 갈음 + 기록(§3) |
| 3 | SHACL property 추가가 meta-SHACL·golden 과 충돌할 수 있다 | 1단계에서 verify-ontology 로 확인 · 충돌 시 golden 페어 1쌍 추가(기존 장치) |
| 4 | 블록 해시는 그래프 편집마다 바뀐다 | `make rulepack` 이 이미 필수 · 추가 비용 0 |
| 5 | Codex 결속률 91.7% — 정당한 허용·예외 42건이 Codex 에서 근거 불가 | 설계 §3-1 대로 fail-closed 유지 · R-T0 기록 |
| 6 | 모의 실행은 모델 판단 변동이 크다(R-T2·R-T3·R-T14) | 합격 문장을 계획 리뷰에서 확정 · 실패 시 문면 보정 1회 · 반복 실행은 R-T2 만 2회 |
| 7 | 6a 와 작업 트리 공유(Makefile·조감도·progress) | §7 hunk 분리 · 먼저 착륙하는 쪽 기준 |
| 8 | `refactor_audit.py` 가 커질수록(추정 1,500행+) 봉인 대상이 무거워진다 | pipeline 등재는 설계 결정 — 그대로 |
| 9 | 러너가 «새 테스트 실행 장치» 원칙에 걸리는가 | 걸리지 않는다 — 원칙의 대상은 리팩토링 대상 프로젝트의 테스트이고, 러너는 플러그인 도구 시험(설계 §10) |

- **사용자 결정: 없음.** 위 항목은 전부 설계 결정·플러그인 정의·선례에서 답이 나온다.
