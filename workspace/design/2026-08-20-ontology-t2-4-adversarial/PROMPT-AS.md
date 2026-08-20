# 사후 산출 리뷰 레인 AS — T2-4 구현 실물 반증

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only). 이번엔 설계가 아니라 **구현된 실물**을 공격한다. 커밋 `3c03d81`(feat(ontology): T2-4 규칙 팩 구현). 칭찬·요약 금지 — 결함만. 모든 주장에 **파일:행 인용 또는 재현 명령**.

## 무엇이 승인됐고 무엇이 만들어졌나

**동결 개정 8**(사용자 승인 «규칙 번호·명칭까지»): C암 주입 = `<violations>{rule,file,message}` + **`<rules>{rule,label}`**(번호·명칭). **규범 본문은 양 암 미동봉**(E8 무접촉). B암 프롬프트는 **byte 불변**.
**동결 개정 9**(사용자 승인 «계수 후 유효 유지»): `rule=null` 선행계약 위반이 섞인 런은 유효 비교 유지·계수만.

산출 실물:
- `workspace/tools/ontology_rulepack.py`(생성기·rdflib) → `dddjango/scripts/rulepack.json` + codex 미러
- `dddjango/scripts/rulepack.py`(무의존 조회·글롭 matcher) + codex 미러
- `dddjango/scripts/regen_core.py`(`select_graph`·`assemble_prompt(records, rules=None)`·**셸 B CLI**) + 미러
- `workspace/tools/queries/q1~q4.rq` · `derive_path_globs.py` + `section-path-map.tsv` → `ontology/wiring/paths.ttl`
- `workspace/tools/rulepack_smoke.py`(10단언·변이 8종) · `firing_probe.py`(4트리×5단언) · `query_golden_check.py`
- `ontology/vocab/djr.ttl`(`djr:experimentRun`) · `ontology/shapes/djr-shapes.ttl`(`ViolationShape-experimentRun`·`SectionShape-pathGlob`) · 골든 3벌
- `workspace/tools/violation_adapter.py`(사건 노드에 실런 축·`canonical_locator` 단일화) · `findings.py`(`experiment_run_id`)
- 양 런타임 step 6′ 개정 + `regen_loop_prototype.py` selector 배선 + `regen_loop_smoke.py` T5

판단표 정본 = `workspace/design/2026-08-20-ontology-t2-4-design.md` v3. 선행 리뷰 이력 = 같은 폴더 `log-AP/AQ/AR.txt` · `MEDIATION-AP-AQ.md` · `MEDIATION-AR.md` · `SELF-FINDINGS.md`. **이미 지적돼 반영된 것을 되읊는 것은 발견이 아니다.**

## 검증 과제

### 1. 개정 8 이행의 **실물** 대조 — 최우선
- `<rules>` 에 실제로 실리는 것이 «번호·명칭»뿐인가? 팩·프롬프트 어디에도 규범 본문이 새지 않는가? **팩 JSON 전수**와 프롬프트 실물을 만들어 확인하라.
- **B암 byte 불변**이 정말 성립하는가. `rulepack_smoke` G2 는 저자가 쓴 대조다 — 그 대조 자체가 자기 참조가 아닌지 검사하고, **T2-3 커밋 시점의 실제 출력**(`git show`)과 현재 출력을 직접 비교하라.
- `assemble_prompt(records, rules=None)` 이 `rules=[]`(빈 배열)일 때와 `None` 일 때 같은가? 호출자가 빈 배열을 넘길 경로가 있는가?

### 2. selector 계약의 결함
- `regen_core.select_graph` 를 실독하고 정렬·중복 제거·tier 부여의 **비결정성**을 찾아라(같은 입력이 다른 순서를 낼 수 있는가 — 특히 tier 2 의 `min(order_rank)` 동률, tier 3 의 원래 순서 보존, `identity()` 의 `None` 처리).
- `pack.locate` 가 `by_checker` 에 **없는** 검사기, `by_alias` 에 있으나 `works` 에 없는 Work, 빈 `works` 목록에서 어떻게 동작하는가.
- C가 **B보다 나빠질** 구체 경로를 하나 이상 구성하라(무관 규칙 명칭이 최대 몇 건 실리는지 실측하고, 그것이 coder 를 어디로 끌고 갈 수 있는지).

### 3. 발화 증명 probe 의 검출력
- `firing_probe.py` 가 **놓치는** 파손을 만들어라. 예: 팩은 읽지만 결과를 버리는 구현, `<rules>` 를 실었으나 내용이 상수인 구현, 두 런타임이 **같은** 오작동을 하는 경우.
- probe 가 cache 레인을 red 로 내는 것이 정말 「C 실런 금지」를 강제하는가 — `make verify` 는 이 probe 를 돌리지 않는다(`verify-firing` 별도). 그러면 누가 언제 이 게이트를 통과시키는가? 강제되지 않는 게이트인지 판정하라.

### 4. 어댑터·run 격리 수리의 완결성
- `experiment_run_id` 가 **전 사슬**에 실제로 흐르는가: `findings.py` → 게이트 sidecar → `collect_violations.py` → `violation_adapter.py`. 중간에 끊기는 지점을 찾아라(특히 sidecar 와 수집기).
- `_vid` 에 실런을 넣은 것이 **기존 노드 IRI 를 전부 바꿨다**. 이미 적재된 위반 그래프·골든·문서의 IRI 와 어긋나는 곳이 있는가?
- `regen_core.canonical_locator` 단일화가 정말 단일인가 — 아직 자체 정규화를 하는 코드가 남아 있는지 전수로 찾아라.

### 5. 팩·글롭의 정적 무결성
- `ontology_rulepack.py` 의 fail-closed 가 실제로 무는지 변조로 실증하라(구분자 섞임·Work 2블록·alias 함수성 위반·채번 형식 밖).
- `derive_path_globs.py` 의 `section_iri()` 는 **정규식으로 TTL 을 긁는다**. 그 파싱이 깨지는 입력을 만들어라.
- `compile_glob` 의 문법 구현이 `derive_path_globs` docstring 의 폐쇄 정의와 **정확히** 일치하는가. 불일치하는 입력을 찾아라(`**` 중첩·연속 `*`·빈 세그먼트·끝 슬래시).

### 6. verify 편입의 실효
- 새로 편입된 검사들이 **실제로 red 를 낼 수 있는지** 각각 변조로 확인하라. 항상 green 인 검사가 있는가?
- `make verify` 소요 증분을 실측하라(T2-4 전후). 상시 검사에 SPARQL 을 넣은 대가가 얼마인가.

### 7. 열린 스코프
위 과제 밖에서 발견한 것. 특히 **저자가 급하게 처리한 흔적**(주석과 코드의 불일치·미사용 코드·문서와 실물의 드리프트)을 찾아라.

## 산출 형식

발견마다: **ID · 심각도(blocker/major/minor) · 주장 · 실측 근거 · 요구 조치**. 마지막에 「이 구현이 옳은 지점」(공격했으나 뚫리지 않은 축)을 두라. 발견이 없으면 없다고 쓰라.
