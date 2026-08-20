# 선행 설계 리뷰 레인 AL — AliasEntry 귀속 판단표 반증 (적용 전)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 **아직 코드·정본 그래프에 적용되지 않은** 판단표의 오류를 실증하라. 칭찬·요약 금지 — 결함만.

## 리뷰 대상

`workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md` — 검사기 규칙 번호(#N)와 그래프 정본 Work(R-NNNN)의 **지시(alias) 판정표** + 선결 판단 3건 + 함수성 검사 설계 + 커버리지 격차 등재.

문서의 «0. 저자 판단 요약»과 «6. 자인 약점»을 먼저 읽어라 — 저자가 가장 자신 없어 하는 지점이 거기 공개돼 있다.

## 재료 좌표

- 규칙 정본 문면: `workspace/design/2026-08-08-tree-revision-spec.md`(번호별 표 행) · 소유: `workspace/plan/2026-08-11-rule-owner-map.md`
- Work 정본: `ontology/rules/*.ttl`(`djr:R-NNNN a djr:<유형> ; skos:prefLabel "…"@ko ; djr:text …`) · 배선: `ontology/wiring/*.ttl`
- 이관 명세(basis 원문): `workspace/design/2026-08-19-ontology-t1-migrate/spec-*.json` (`sections[].blocks[].norms[] = {label, class, enforcedBy, delegatedTo, basis}`)
- 어휘·셰이프: `ontology/vocab/djr.ttl`(AliasEntry·AliasType·aliasFor/aliasText/aliasType) · `ontology/shapes/djr-shapes.ttl`(AliasEntryShape)
- 동결 문면: `workspace/design/2026-08-18-ontology-blueprint-v2.md`(alias 문법·유형 3종·lint) · `-v3.md` E6 · `workspace/design/2026-08-19-ontology-t2-plan.md` §T2-2
- 저작 규율: `workspace/tools/ontology-authoring.md`(§1 금지·§5 ISSUED·§14 인코딩·§15 공정·§16 배선 4원)

## 검증 과제 (전부 실측·인용으로)

1. **등재 3건 전건 반증**: `#3→R-0124` · `#119→R-0075` · `#486→R-0118`. 각각 규칙 정본 문면과 Work 문면(`djr:text` 원문까지)을 직접 인용해 «주어·양상·술어 일치» 주장이 성립하는지 대조하라. 하나라도 부분 겹침·다른 사건이면 그 등재는 거짓 alias다.
2. **미등재 16건의 «미등재가 옳다» 반증**: 표본이 아니라 **전수**. 각 행의 미등재 사유가 실제 문면으로 지지되는지, 반대로 **등재되어야 하는데 누락된 것**이 있는지. 특히 저자가 «집행 축 인용»·«스코프 상이»로 처리한 #8·#10·#20·#21·#490·#488 을 공격하라.
3. **보류 4건 재판정**: #195·#257·#259·#260 — 각각 {등재(어느 유형) | 미등재}로 확정하거나 «판정 불능 사유»를 명시하라. 합성 Work(R-0108·R-0106)를 구성 규칙이 지시한다고 볼 수 있는지가 쟁점이다.
4. **선결 판단 3건 반증**: ⓐ `aliasText` 문법이 정말 `"rule#N"`인가(v2 L29 «비한정 #N 등재 금지» 원문 확인 + t2-plan §T2-2 문면과의 층위 구분이 궤변이 아닌지) ⓑ alias IRI 규약이 게이트 문법(`ontology_gate.py` FRAGMENT_BAD·`ontology_canon.py` PN_LOCAL_SAFE/ENCODE_CHARS)과 정합인지 — 실제로 `--write` 통과하는지 임시 사본에서 실행 검증 ⓒ `#486` 이중 인용 해소가 옳은지(R-0122 본문 원문을 읽고 «사례 인용» 독법을 공격).
5. **함수성 검사 설계 결함**: ⑥·⑥′ SPARQL 이 실제로 무는가 — golden 제외 관용구·`rdfs:subClassOf*` 폐포·`load_graph`가 병합하는 그래프 범위(`ontology_structural_check.py:24–34`)를 대조하고, **잡지 못하는 위반 모양**(우회 시나리오)을 구체적으로 제시하라. `--self-test` 로 검출력을 증명한다는 설계가 정본 red-first 대비 충분한가.
6. **저작 사양의 실물 정합**: `ontology/wiring/aliases.ttl` 배치가 정말 안전한가(render_sync·render·gate ④ 병합·미러 동기·`corpus_mirror_sync`·`ontology_issued_check`·`ontology_ledger_check` 전부 대조) · 계수 기대표 2→5 산식이 맞는가(골든 2 + 신규 3 — `target-counts.json` 의 계수 정의를 실제로 확인) · ISSUED/LEDGER 무변 주장이 맞는가.
7. **격차 등재(§5)의 사실성**: «T2-1 귀속 #N ∩ 파일럿 후보 = ∅»·«docstring #N 446종»·«파일럿 3.9%» 수치를 재실측해 검증하라. 틀렸다면 정정치를. 또한 이 격차를 «선언된 현황»으로 처리하는 처분이 동결 §8(T2 완료 기준)·개정 2 문면과 충돌하지 않는지 대조하라.

## 출력 형식

| # | 심각도(blocker/major/minor) | 결함(행 식별 포함) | 근거(파일:행 인용·실측) | 수정 제안(판정 교체면 무엇으로) |

결함 없는 과제는 «반증 실패 — N건 대조» 한 줄. 저장소 수정 금지(read-only). 실행 검증은 임시 디렉터리 사본에서 하라.
