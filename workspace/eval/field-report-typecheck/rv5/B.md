# 적대 리뷰 B(5단계 구현) — 규범 리비전·코퍼스 정합 · 2026-09-03

대상: `fix/field-typecheck` HEAD 27342a3 — `33b0bd7`(그래프 리비전·렌더·rulepack·LEDGER·미러·계수·q4) + `27342a3`(봉인 draft·문서). 저장소 무수정(읽기·도구 read-only 실행·스크래치 실측만).
Serena: skipped — opt-in 표식(`.serena/project.yml`) 없음 · graphify 표식 없음 → 기본 도구.

판정: **BLOCKER 0 · MAJOR 0 · MINOR 2(문서 정정 요구) · 관찰 4** — 그래프·렌더·미러·소성물은 확정 문면과 byte 수준 일치, 레시피 누락 0, 코퍼스 모순 0.

## (1) 문면 byte 일치 표

| 대상 | 실측 방법 | 결과 |
|---|---|---|
| 확정 불릿 1·2 (계획 :101-102, `> ` 제거) | 파일별 **행 단위 exact equality** | 렌더 `dddjango/skills/architecture-ddd/references/final.md:484-485` ✓ · codex `codex-dddjango/skills/dddjango-architecture-ddd/references/final.md:484-485` ✓ · 소스 `workspace/reference/architecture-ddd/reference/final.md:492-493` ✓ — 인접·직후 빈 줄 유지 |
| ttl b3 리터럴 (`s016-3.1/b3` `djr:text`@ko) | rdflib 파스 후 `'\n'+불릿+'\n' in text` | 불릿 1 ✓ · 불릿 2 ✓ · 후행 구분자 `\n\n` 유지 ✓ · statesNorm = R-0494·0495·0496·**3442·3443** ✓ |
| ttl b3·b4 리터럴 ↔ 렌더·소스 | `text in file` verbatim | 렌더 b3 ✓ b4 ✓ · 소스 b3 ✓ b4 ✓ · codex = 렌더 byte 동일(`cmp` 0 · sha256 `3b519580…`) |
| 예제 diff 4지점 (계획 :105-119) | `+` 5행 / `−` 6행 개별 대조 | `+` 5행 전부 ttl b4·렌더 존재 ✓ · `−` 6행 전부 ttl b4 부재 ✓ (렌더에 `def __post_init__(self):` 잔존 2건은 **다른 블록** :628·:777 — 관찰 O2) |
| 확정 문면 밖 변경 | `git show 33b0bd7` 전 hunk | final.md 3본 각 4 hunk **+7/−5**(불릿 2 · docstring/if/raise 3 · result 1 · PhoneNumber 1) 외 0 · ttl: Norm 2+Expression 2(16행)+b3 text/statesNorm+b4 text 외 0 · wiring +2 triple 외 0 |

## (2) 리비전 레시피 체크리스트 (DEVELOPMENT §3 5단 + 메모리 레시피 8단 + ③ B 누락 3)

| # | 단계 | 실측 | 판정 |
|---|---|---|---|
| 1 | Norm 2건 클래스·prefLabel·currentExpression | R-3442 `a djr:Obligation` · R-3443 `a djr:Prohibition` · prefLabel@ko 1개씩 · currentExpression `<…#R-344x@2026-09-03>` · Norm 술어 = {type, prefLabel, currentExpression} — R-0495/R-0496 선례와 동형 | ✓ |
| 1′ | Expression | `a djr:Expression` · `prov:specializationOf` Norm · `djr:revision 1` · 술어 3종 — 선례 동형(wasRevisionOf 없음 = 신설 정당) | ✓ |
| 1″ | b3 statesNorm · wiring | statesNorm 5건 · `ontology/wiring/architecture-ddd-final.ttl` R-3442/R-3443 `delegatedTo <…#a/agent-discipline-reviewer>`만 (registry.ttl에 Agent 실존 · shapes `sh:or(HasChecker HasDelegate)` 충족 · §16 기본값 표 «architecture-ddd 구현 시점 규범 → discipline-reviewer» · R-0494 선례) | ✓ |
| 1‴ | ISSUED 2행 | `R-3442\t2026-09-03\trules/architecture-ddd-final.ttl` · `R-3443 …` TAB 3필드 · 연번(직전 R-3441) · 대장 3443행 · 중복 0 · issued-check 정합 | ✓ |
| 2 | 게이트 | `ontology_gate.py` 90/90 green(canon diff=0 포함) · meta-shacl 2층 green · shacl-full 64파일 위반 0 · structural 7종 정합 · golden 23 불일치 0 | ✓ |
| 3 | 렌더 재투영 | render-sync 540절 red 0·warn 0·SyncDebt 0 · s016-3.1 마커 1개·헤딩 불변·77행 | ✓ |
| 3′ | LEDGER graph 재기준선 | 행 `architecture-ddd-final\ts016-3.1\tff912545…\tgraph\t-\t-\t-\t-\trebaseline:…` · **재계산** `sha256(strip_marker(render span s016-3.1)) = ff912545b68ef968…` 일치 · 이력 3행 보존(1e38254c prose→graph migrate→ff912545) · ledger-check 위반 0 | ✓ |
| 4 | 계수표 | target-counts NormShape 3450→**3452** · WorkShape 3450→**3452** · ExpressionShape 3544→**3546** · hierarchy `--with-golden` 셰이프 9종 불일치 0 | ✓ |
| 4′ | q4 골든 | query-golden.json q4 distinct_works/rows 3441→**3443** · query_golden_check 7종 일치 | ✓ |
| 4″ | `make rulepack` | built_from 64경로 중 변경 2(`rules/architecture-ddd-final.ttl` d2aae824… · `wiring/architecture-ddd-final.ttl` f3dbdec5…) = 현재 파일 sha256 일치 · works 3441→3443 · by_section s016-3.1 works +R-3442/R-3443 · codex rulepack `cmp` 동일 · `--check` 정합 | ✓ |
| 5 | 소스 미러 span 수동 교체 + `--write` | 소스 절 `s017-3.1`(소스 키 오프셋) raw span sha256 == LEDGER ff912545 · corpus_mirror_sync `--check` 11/11 in-sync | ✓ |
| 6 | codex 의미 미러(SKILL.md) | architecture-ddd SKILL.md(claude·codex) §3.1 불릿 재진술 0(«§3» 표 행만 — grep setter/불변이어야/동등성/핵심 원칙 0건) · discipline-reviewer md :117 이미 «테스트·타입 체커» 문면 → 갱신 **불요**(근거 확인) | ✓ |
| 7 | spec_lint(#N 신설 시) | 검사기 규칙 번호 신설 없음 · spec_lint 위반 0 · reverse_coverage 미설명 0/죽은 소유자 0 · corpus_lint 0 · checker_lint 0 · tree_mirror in-sync · derive_path_globs 정합 | ✓ (해당 없음·green) |
| 8 | 봉인 draft · verify | `manifest_seal --check --draft` green(그룹 10·파일 256·상태 draft) · verify-ontology 11단 개별 재현 green · verify-base-core 코퍼스 측 항목 green · 검사기 27종 codex `cmp` 차이 0 | ✓ |
| ③B-1 | 봉인 draft(계획 §1.4 누락 지적) | T2-0b-manifest status=draft · plugin_payload/packs/graph/scorer 그룹 해시 갱신(`sha256(bytes+"\0mode:…")` 산식 — 평문 sha와 다름은 정상) | ✓ 반영 |
| ③B-2 | 검수표 기록 위치 | 계획 말미 «검수표» 9행 실측 기입(90/90 · +7/−5 · 3452/3452/3546 · 11/11 · mypy 0 · 6/6) | ✓ 반영 — 단 §16 근거 행 부재(M2) |
| ③B-3 | 조감도 HTML | `workspace/design/ontology-adoption-map.html:638` 2026-09-03 행(R-3442·R-3443·b3 불릿 2·b4 교체·discipline-reviewer 위임·mypy 0) | ✓ 반영 |

## (3) 코퍼스 정합 판정

| 대조 대상 | 관계 | 판정 |
|---|---|---|
| R-0494(동등성)·R-0495(불변)·R-0496(setter 금지) — 같은 b3 | 상보(다른 축) · deontic 분할 판형(0495 Obligation+0496 Prohibition) 동형 채택 | 중복 0 |
| R-3154(Exception — 프레임워크 선언·enum 멤버 주석 면제) | 주석 면제 층 — 값 객체 검증과 무관 | 모순 0 |
| R-3158(mypy strict는 시그니처만 강제) | R-3443 «타입은 시그니처가 약속하고 테스트·타입 체커가 지킨다»와 동방향 | 모순 0 |
| R-1066/R-1098(reviewer ⓓ#69 물음) · `agents/discipline-reviewer.md:117` | 절차 층(물음) ↔ R-3443 실체 기준(답) — delegatedTo discipline-reviewer로 닫힘 · 어휘 «테스트·타입 체커» 일치 | 중복 0 · 정합 |
| #69 검사기 docstring(`check-public-surface-annotation.py:18-20,418-433` — 프로덕션 assert·isinstance 가드+raise만 후보·exit 불산입) | 새 예제 `type(x) is bool` 무발화 — **실측**: 새 블록 `clean`, 원본 블록 #493 blocker 2(:30 `result` · :56 `__post_init__`) | 정합 · enforcedBy 미배선 정당(«#69는 관련 신호일 뿐 집행선 아님») |
| cleancode §12.7 R-1504~1506(«외부» 경계 결정·경계에서 검증) | 일반 원칙 → 값 객체 특수화 | 모순 0 |
| implementation-python §12.0/12.3 R-2752/2755/2756(pydantic boundary coercion·strict — 도메인 규칙 소유 금지) | 좁히기·coercion = 경계 소유 — 동방향·상보 | 모순 0 |
| prefLabel 전수 스캔(값 객체 × 타입/검증/변환/불변식) | R-0114·R-1412(값 객체 승격)뿐 | 스킬 층 성문 중복 0 |
| `type() is` vs `isinstance` 지침 | 코퍼스 0건 · ruff 기본·E721 clean(0.16.4) — E721은 `==`만 잡고 `is` 허용 | 모순 0 |
| rulepack 분류 | «검사기 도달 불가» 2651→**2653**(신규 2건만) · architecture-ddd delegatedTo-only 113건(R-0098~…)과 동형 · by_checker 0 · by_path(Q1 카탈로그 4글롭) 무관 | **정상** — reviewer 채널로만 집행되는 규범의 표준 형상 |
| 렌더본 mypy(spring venv mypy 2.3.1) | 새 블록 strict+warn_unreachable+redundant-expr **0** · plain strict **0** / 원본 full 2(unreachable :17·no-untyped-def :56)·plain 1 | 회신·검수표 수치 재현 |

## (4) 문서 정정 요구

- **M1 (MINOR — 정정 요구)** `workspace/plan/2026-09-03-improvement-roadmap.md:50` R-14 행이 stale: 내용 열이 «C: 하우스룰 §2 … Enum/StrEnum 멤버 예외 명시 | 규범 리비전(소규모 2건)», 상태 열이 «① 적대 리뷰 3기 진행 중». 실제 처분(회신 표 C행·같은 파일 :89 이력 행)은 **C 문면 불성립 → 규범 변경 0 · 검사기 #493 별칭 해소**. 정정안: 내용 열 C를 «C: 불성립(R-3154 기성문) → 검사기 #493 import 별칭 사각 수리(Part 2)»로, 유형 «규범 리비전 1(R-3442/R-3443)+검사기 수리 1», 상태 «④ 구현 완료(fix/field-typecheck) — ⑤⑥ 후 릴리즈 게이트».
- **M2 (MINOR — 정정 요구)** §16 «enforcedBy/delegatedTo 근거는 검수표에 기록(무근거 배선 금지)» · §13 «블록 내 문장→Work 대응은 검수표에 기록»: D1-4가 약속한 검수표 행 «#69 ⓓ 후보는 관련 신호일 뿐 집행선이 아니다»가 계획 말미 검수표·루브릭 ④·LEDGER note 어디에도 없다(근거 자체는 D1-4 델타 본문에만). 정정안: 검수표에 1행 추가 — «wiring 근거 | delegatedTo discipline-reviewer만 | #69 ⓓ 후보(isinstance 가드+raise 한정·exit 불산입·`type() is` 무감각)는 관련 신호일 뿐 집행선 아님 → enforcedBy 미배선 · 문장→Work: 불릿 1→R-3442 · 불릿 2→R-3443».

## (5) 관찰 (결함 아님 — 기록·후속 후보)

- **O1** 봉인 draft `sealed_commit = 036a874`(3커밋 이전 HEAD) — draft 모드는 ⑧′(커밋 실재 대조)를 걸지 않아 green이지만 strict `--check`는 필패. 릴리즈·설치 후 `manifest_seal --write` 재발행 필수(기존 관행·메모리와 일치). T2-0b design md 1행 변경은 `MANIFEST-FACTS` 기계 렌더(cache_parity drift = 미설치 상태 정상).
- **O2** 같은 문서 다른 블록의 `def __post_init__(self):` 무주석 2곳(렌더 :628 «풍부한 도메인 모델» · :777 «애그리거트 루트») — 확정 범위(b4) 밖이라 이번 변경 결함 아님. D1-5 논리(레인이 베끼면 #493 blocker)가 동일 적용 → 로드맵 후보 등재 권고.
- **O3** 규범 산문 안 인라인 «(R-3442)»«(R-3443)» — 11 final.md 중 첫 사례(Coordinator :98에 1건 선례). 사용자 확정 문면이라 변경 요구 없음 · 게이트·lint 무저촉 확인.
- **O4** spring 프로젝트 ruff 설정(UP037)은 기존 `"Money"` 따옴표 주석 6건을 경고 — 변경 전부터 있던 형상·기본 ruff/E721 clean · 확정 범위 밖.

## (6) 10줄 요약

1. **문면 byte 일치 검증됨** — 확정 불릿 2가 ttl b3 리터럴·렌더 :484-485·codex(cmp 0)·소스 :492-493에 행 단위 동일(구분자 `\n\n` 유지), 예제 diff 4지점(+5/−6)이 ttl b4·렌더에 정확히 반영, final.md 3본 hunk +7/−5·ttl 22행·wiring 2 triple 외 확정 문면 밖 변경 0.
2. **리비전 규약 검증됨** — R-3442 Obligation·R-3443 Prohibition(R-0495/0496 분할 선례 동형), prefLabel@ko·currentExpression·Expression(specializationOf·revision 1), b3 statesNorm 5건, wiring delegatedTo agent-discipline-reviewer(§16 기본값·shapes sh:or 충족), ISSUED 2행 TAB 연번·중복 0.
3. **LEDGER 재기준선 재계산 일치** — `sha256(strip_marker(render s016-3.1 span)) = ff912545…` = 원장 유효 행 = 소스 미러 절 raw span 해시; 이력 3행 append-only 보존; ledger/render-sync/issued 전부 위반 0.
4. **계수·소성물 검증됨** — target-counts 3452/3452/3546(hierarchy green), q4 3443(7종 일치), rulepack built_from 변경 2경로 sha = 현재 파일, works 3441→3443, by_section s016-3.1 +2, codex rulepack·검사기 27종 byte 동일.
5. **도구 전건 green 재현** — gate 90/90·meta-shacl·shacl-full 64파일 0·structural·golden 23·corpus_mirror_sync 11/11·reverse_coverage 0/0·spec_lint 0·corpus_lint 0·derive_path_globs·tree_mirror·rulepack --check·manifest --check --draft green.
6. **코퍼스 모순·중복 0** — R-0494~0496 상보, R-3154 무관, R-3158·cleancode §12.7·impl-python §12(pydantic boundary) 동방향, R-1066/R-1098은 절차 층(물음)이고 R-3443이 실체 기준(답)이라 중복 아님, `type() is` 반대 지침 0·ruff E721 clean; rulepack «도달 불가» 2651→2653은 delegatedTo-only 113건과 동형의 정상 분류.
7. **실측 재현** — spring venv mypy 2.3.1로 새 블록 full/plain 0(원본 full 2·plain 1), #493 검사기 새 블록 clean(원본 blocker 2) → 회신·검수표·루브릭 ④ 수치 일치; 조감도 :638·로드맵 R-15 5 file:line 실존.
8. **codex 의미 미러 불요 근거 확인** — architecture-ddd SKILL.md(양 런타임)는 §3.1 불릿을 재진술하지 않고(§3 표 행만), discipline-reviewer :117은 이미 «테스트·타입 체커» 문면; ③ B 누락 3건(봉인 draft·검수표·조감도) 전부 반영.
9. **MINOR 2 — 문서 정정 요구**: M1 로드맵 R-14 행 stale(C를 «하우스룰 §2 규범 리비전»·상태 «① 진행 중»으로 서술 — 실제 C 불성립·검사기 수리와 모순) · M2 §16/§13 검수표 근거 행(«#69 ⓓ 후보는 신호일 뿐 집행선 아님»·문장→Work 대응) 부재 — D1-4 약속 미이행.
10. **관찰 4(결함 아님)** — 봉인 draft sealed_commit=036a874는 strict 시 필패(릴리즈 후 재발행 관행) · 같은 문서 :628/:777 `__post_init__` 무주석 잔존은 범위 밖(로드맵 후보) · 인라인 (R-id) 첫 사례 · spring UP037은 기존 형상. **BLOCKER 0 · MAJOR 0 → 5단계 통과, M1·M2 정정 후 ⑥ 감사 진입 가능.**
