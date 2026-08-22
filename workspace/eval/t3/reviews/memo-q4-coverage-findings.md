# T3 적대 리뷰 — 마감 처분 메모 q4-coverage

- 대상: `workspace/eval/t3/memos/q4-coverage.md` (전문 정독 · 재현 명령 §7 직접 실행)
- 대조 재료: `workspace/tools/queries/q4-injection-order.rq`(+q1·q3) · `workspace/tools/ontology_rulepack.py` · `dddjango/scripts/rulepack.py` · `dddjango/scripts/regen_core.py` · `workspace/tools/rulepack_smoke.py` · `workspace/tools/query_golden_check.py` · `workspace/eval/fixtures/rulepack/query-golden.json` · `workspace/tools/ontology_structural_check.py`(⑥·⑥′·⑥″ 실행) · `workspace/tools/manifest_seal.py` + `workspace/eval/ab/T2-0b-manifest.json` · `Makefile`(verify 사슬) · `ontology/shapes/djr-shapes.ttl` · `ontology/wiring/aliases.ttl` · `workspace/plan/2026-08-11-rule-owner-map.md`(538규칙 원장) · `workspace/eval/ab/BK2-RUNSTATE.md`(실험 종결 실측) · `workspace/eval/t3/T3-EXECUTION.md`
- 검증 방식: 문면 대조가 아니라 **개정을 실물로 조립해 태웠다** — ① 개정 q4를 in-memory 패치로 실행(3,400행) ② §6.2 명세대로 개정 팩 전체를 `/tmp/rulepack-revised.json`으로 소성 ③ 그 팩에 대해 `rulepack_smoke.py` 14단언 + `--mutation-test` 11변이 실실행 ④ §3.3 실험을 rule#999와 원장 실재 번호(rule#1) 양쪽으로 재현 + `alias_errors()` 직접 실행 ⑤ 정렬 키 이전을 앵커 1,693 Work 전량 상대 순서 비교로 검산.
- 판정: **apply** — blocker 0 · caution 6(아래). 메모의 기계 검증 가능 주장은 전건 재현됐다.

## 검증 통과 확인 (실측 재현 전건)

| 메모 주장 | 실측 | 판정 |
|---|---|---|
| §1.2 계수 앵커 1,693/1,084/409 · 무앵커 1,707/665/125 | §7 명령 재현 — 동일 | ✓ |
| §1.3 무앵커 성격 h2 78/1,281 · h3 11/271 · h4 11/80 · frontmatter 19/60 · h1 6/15 | headingSnapshot 분류 재현 — 표와 자릿수까지 동일 | ✓ |
| §1.4 문서별 agents 919 · commands 335 · SKILL 320(309+64절 예외 표기 포함) · final.md 133 | 개정 팩에서 재계수 — 동일 | ✓ |
| §2 검사기 27종 전부 무앵커 보유 · 집행 무앵커 447 · 무앵커 alias 0 · pathGlob 절 4건 전부 앵커 | 재계수 — 27/27 · 447 · by_alias 3건 불변 · 무앵커 glob 0 | ✓ |
| §1.1 `SectionShape-sectionNumber` maxCount 1뿐 minCount 없음 · `ontology_migrate.py:148` anchor 조건부 기입 | djr-shapes.ttl L174-177 · migrate L147-148 실독 | ✓ |
| §3.1 `--selector` 기본값 없음(미지정=중단) · step 6′ 기본 off · 실험 종결 | regen_core L330-331·L369 · commands 6′ 문면 · BK2-RUNSTATE «⏹ 실험 종결(08-22 13:1x · 사용자 '지금 즉시 전부 중단' · 유효 측정 0건 · 폐루프 기본 off 존치)» | ✓ |
| §3.3 핵심 기전 — 무앵커 Work의 alias는 현행 생성기에서 침묵 탈락·RED 0·`_validate_refs()`는 `by_alias→works` 단방향 | R-2492(무앵커·enforcedBy 2종 실측)에 alias 주입 후 현행 q4 경로 재현: works 1,693 · by_alias 3 · 미수록 · problems 0. `_validate_refs` L129-158 실독 — 역방향 부재 | ✓ (단 실험 번호 문제 — C-1) |
| §4.1 개정 실측 works 3,400 · by_section 534 · by_checker 27 · by_alias 3 · fail-closed 0 · 1 Work=1 블록 · prefLabel 곱셈 0 | 개정 q4 실행 — rows 3,400 = distinct 3,400 · problems 0 · 전 지표 동일 | ✓ |
| §4.1 **정렬 키 이전 무손실** — 기존 1,693 상대 순서 완전 보존 | `(document, sNNN 서수, blockOrder, wid)` vs 현행 `(document, _natural(sn), blockOrder, wid)` 전량 비교 — **불일치 0건**. 절 IRI 말단 전건 `s\d+(-…)?` 형식 부합. G3a 고정점 rank(R-0120)<rank(R-0124) 유지 | ✓ |
| §4.1 tier 2 팽창 표 | 표본 4행 재계수: 56→145 · 38→91 · 21→87 · 2→17 — 동일 | ✓ |
| §6.1 q4 diff | 명세의 두 줄 교체가 현행 파일에 byte-정확히 적용됨. q1은 pathGlob 앵커 절 전유(실측 0건 무앵커)·q3은 주소 필수라 불변 논거 성립 | ✓ |
| §6.2 지점 | L144 `ordered.append` · L136 `section_number` · L166 `by_section number` · L197~ report — 4지점 전부 실제 라인과 일치. 생성기 안에 sectionNumber를 바인딩 전제로 쓰는 **다른 지점 없음**(전수 grep) | ✓ |
| §6.2 #5 신설 검사 실현 가능성 | `djr:AliasEntry`는 typed class(vocab L9 · aliases.ttl 3건) — `?a a djr:AliasEntry` 질의 + build()의 키 변환(`rule#N`→`#N`)과 동형으로 구현 가능. 주입 실험에서 정확히 그 미수록을 잡음. problems 적재→exit 2 경로(L226-231)는 기록 전 차단 — fail-closed 성립 | ✓ |
| §6.3 소비자 0건 | repo 전역 grep(py·md·html·json — .venv 제외): `works.*.section_number`·`by_section.*.number`를 읽는 코드 0건. `dddjango/scripts/rulepack.py`는 order_rank·label·aliases·checkers·works만 소비 | ✓ |
| §6.4 골든·하네스 | **개정 팩으로 실실행: 14단언 14통과 · 변이 11종 전건 red.** G1 27종 유지·G3a ids [r:2,r:1,r:4] 유지·G7 s023-6.2 키·글롭 10케이스 유지·G3d/G5/G9 유지. 골든 필드(q4.rows·distinct_works·with_alias) 실재 | ✓ |
| §6.4 firing_probe·manifest | `verify`는 firing_probe 비호출·`verify-firing`은 `ALLOW_STALE=1`→`--allow-stale-cache`(Makefile L96-97) · `manifest_seal.py --seal` 플래그 실재(L1350) | ✓ (범위 오지목 — C-2) |
| §5·§8 전제 | 웨이브 4 «alias 재검토» 편성 실재(T3-EXECUTION 표) · 2.16.0이 08-22 오전 릴리즈됨(BK2-RUNSTATE) — 2.17.0 검토 정합 | ✓ |

## 발견 (심각도순 — blocker 0)

### C-1 [caution · 증거 정확성] §3.3 실증 로그의 «⑥·⑥′·⑥″ 전부 통과 · make verify green»은 rule#999로는 재현 불가

- **실측**: `ontology_structural_check.alias_errors()`의 ⑥″에는 문법 정규식 외에 **원장 실재 분기**가 있다(`text.split("#",1)[1] not in rule_numbers` → «원장 미실재»). 538규칙 원장(`2026-08-11-rule-owner-map.md`)의 번호 집합은 1..636 사이 538개이고 **999는 없다**. `rule#999`를 그래프에 실제로 달고 alias_errors를 돌리면 `⑥″ alias 문법 위반 1건: [alias-rule-999:'rule#999'(원장 미실재)]` — 구조 검사 red → make verify red. 따라서 §3.3 박스의 «alias 대장 검사 ⑥·⑥′·⑥″ 전부 통과 + make verify green + 팩 미수록» 동시 성립은 #999로는 거짓이다(생성기만 in-memory로 돌렸거나, verify green이 alias 없는 트리에 대한 관측일 수밖에 없다).
- **결론은 생존한다**: 원장 실재 번호로 재실증 완료 — `rule#1`(원장 실재·미사용)을 무앵커 R-2492에 달면 `alias_errors = NONE`(⑥ 전 계열 green)이면서 현행 팩 by_alias 미수록·RED 0. 웨이브 4의 현실 시나리오는 언제나 원장 실재 번호이므로 위험 판정 자체는 옳다.
- **처분**: 메모 수정은 리뷰 권한 밖 — 적용 커밋 기록(또는 웨이브 4 로그)에 «§3.3 실증 번호는 #999가 아니라 원장 실재 번호로 성립(#999는 ⑥″ 원장 미실재로 별도 red)» 한 줄 정정을 남길 것. T2-2 선례(거짓 실증 문면이 후속 판단을 오염) 때문에 전건 기록한다.

### C-2 [caution · 오지목] §6.4 manifest 재봉인 범위 — 실제 변경 그룹은 packs + **queries**, graph는 불변

- **실측**: T2-0b-manifest GROUPS에서 이 처분이 바꾸는 파일의 소속은 `packs`(dddjango/scripts/rulepack.json)와 **`queries`**(workspace/tools/queries/*.rq · ontology_rulepack.py · workspace/eval/fixtures/rulepack/**/* — 즉 q4·생성기·query-golden.json 전부 이 그룹)다. 메모가 적은 «`packs` 그룹 + `graph` 그룹»에서 graph(`ontology/**/*`)는 **이 처분으로는 한 byte도 안 바뀐다**(그래프 무수정 처분). 또 «rulepack.json ×2» — packs globs에는 dddjango 쪽 1개뿐, codex 미러는 봉인 대상이 아니라 mirror_parity 축 소관.
- **실해**: `--seal`은 전 그룹을 재측정하므로 절차 사고는 없다. 다만 재봉인 diff 검수 때 «graph 해시가 바뀌는 이유»는 이 처분이 아니라 형제 웨이브 4 그래프 편집이고, «queries 해시 변화»가 이 처분의 정상 흔적임을 오독하지 말 것.

### C-3 [caution · 드리프트] 메모의 스냅숏 수치는 이미 낡았다 — 적용 시 기대값은 재생성 실측이 정본

- **실측**: 메모 헤더 트리플 45,677 → 현재 46,105(+428 — 형제 작업의 ttl 수정 진행 중, `djr-shapes.ttl`·`djr.ttl` 등 dirty). 이 트리에서 `ontology_rulepack.py --check`는 **이미 red**(팩 노후 — 처분과 무관한 선재 상태)다. 개정 팩 실측 2,181,493B ≠ 메모 2,178,560B(-2,933B 드리프트). Work 계수 축(1,693/1,707/3,400)·인덱스 계수는 현재도 정확.
- **처분**: §4.1·§6.5의 byte·해시 값을 적용 검수의 «기대값»으로 못박지 말 것. 기대값은 계수 축(works 3,400 · 검사기 27 · alias 3 · 절 534 · RED 0 · 골든 q4 3,400)이고 byte는 재생성 실측을 기록한다.

### C-4 [caution · 재발 방지 커버리지] q1에 같은 형태의 잠재 구멍이 남는다 — 신설 검사는 alias 축만 닫는다

- **실측**: q1도 `djr:sectionNumber`를 필수 트리플로 요구한다. 장차 **무앵커 절에 pathGlob이 저작되면** by_path에서 동형의 침묵 탈락이 난다(생성기 RED 없음). 오늘은 실해 0 — 글롭 4건 전부 앵커 절 실측 + `derive_path_globs.py`가 절을 sectionNumber로 지목하는 구조라 정규 저작 경로로는 발생 불가(수기 ttl만 위험). §5 자신이 «다른 축 재발 가능»을 자인하면서 검사는 alias 축만 신설한다.
- **처분**: 적용을 막을 사유는 아니다. §6.2 #5 구현 시 같은 형태의 «pathGlob 전량 ⊆ by_path» 역방향 한 줄을 동반 신설하면 같은 값에 닫힌다 — 권고.

### C-5 [caution · 과소 기술] §4.1/§6.6 «대부분 검사기의 min rank가 agent 문서로 이동» — 실측은 **27/27 전부**

- 개정 팩에서 by_checker 27종 전부의 최소 order_rank Work가 agents/·commands/ 문서 소속이 된다. 방향은 메모와 같고 정도가 «대부분»이 아니라 «전부»다. C암 위반 배열 순서 변화의 폭을 기록할 때 전수임을 명기.

### C-6 [caution · 적용 순서] 재소성·골든 --emit·재봉인은 웨이브 4 그래프 편집 종결 후 1회

- 같은 워킹트리에 형제 메모(hash-n-alias·tree-coords·contract-ref)의 그래프 수정이 진행 중이다. q4 개정 커밋에서 팩·골든·봉인을 먼저 확정하고 뒤에 그래프가 또 바뀌면 --check·골든·봉인이 재차 red가 된다. 메모 자신의 «alias 재검토와 같은 커밋 묶음» 지시(§5)와 정합하게, 재생성물 확정은 웨이브 4 그래프 편집 전체 종결 뒤 한 번으로 몰 것.

## 종합

- **blocker 0.** §6 개정 명세의 지점은 전부 실제 코드와 일치하고 누락 지점이 없다. 정렬 키 이전의 «상대 순서 완전 보존»은 앵커 1,693 전량 비교로 참(불일치 0). 신설 fail-closed 검사는 구현 가능하며 정확히 §3.3의 결함을 잡는다. 개정 팩에 대해 골든 하네스 14단언·변이 11종이 전건 통과 — «고정점 불변» 주장은 예상이 아니라 실측으로 확인됐다.
- **판정: apply.** 단 C-1(실증 번호 정정 기록)·C-3(기대값=계수 축)·C-6(적용 순서)을 적용 커밋에서 준수할 것.
