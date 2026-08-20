# 반증 레인 AT — T2-4 사후 중재의 부분 채택 3건을 반박하라

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only). 임무는 **저자(중재자)가 깎아낸 3곳을 뒤집는 것**이다. 저자의 부분 기각은 이 프로젝트에서 **두 번 연속 전건 뒤집혔다**(T2-3 레인 AO · T2-4 레인 AR) — 편향을 의심할 실적이 있다.

칭찬·요약 금지. 모든 주장에 **파일:행 인용 또는 재현 명령**.

## 읽을 것

- 중재: `workspace/design/2026-08-20-ontology-t2-4-adversarial/MEDIATION-AS.md`
- 원 지적: 같은 폴더 `log-AS.txt`(AS-09 · AS-10 · AS-12 절)
- 판단표: `workspace/design/2026-08-20-ontology-t2-4-design.md` v3
- 동결: `workspace/design/2026-08-18-ontology-blueprint-v3.md`(§2 E5·E7·E8 · §6 · §12 **개정 8·9**) · `workspace/design/2026-08-19-ontology-t2-plan.md` §2
- 규약: `workspace/design/2026-08-19-ontology-autonomous-protocol.md` R2·R3
- 실물: `dddjango/scripts/{regen_core,rulepack,registry_gate,findings}.py` · `workspace/tools/{violation_adapter,findings_count_matrix,query_golden_check,rulepack_smoke}.py`

## 과제 1 — AS-09 처분(「`<rules>` 표지 신설은 개정 8 범위 밖」)을 반박하라

저자는 tier 2 팽창(위반 1건 → 무관 label 최대 31건·7.04배)을 인정하면서도, `<rules>` 항목에 «정확 적중 / 검사기 후보» 표지를 넣는 것은 **개정 8이 정한 필드 범위(번호·명칭) 밖**이라 코드를 바꾸지 않았다.

- 개정 8 원문(블루프린트 §12)과 판단표 §2-M0·§4-R4(`RULE_FIELDS`)를 실독해, 「번호·명칭」이 **필드 2개로 닫힌 계약**인지 아니면 «본문 미동봉»만이 요점인지 판정하라.
- 표지를 넣지 **않았을 때** 실런에서 무엇이 관측 불가능해지는지 끝까지 그려라. 특히 C가 졌을 때 「tier 2 노이즈 탓」과 「그래프 무용 탓」을 사후에 구분할 수 있는가 — 용량 로그(`records_provenance`)만으로 충분한지 실물로 확인하라.
- 표지 없이 같은 목적을 달성하는 대안이 있는가(예: tier 1 적중이 있을 때 tier 2 후보를 아예 싣지 않기). 그 대안이 개정 없이 가능한지 판정하라.

## 과제 2 — AS-10 처분(「생산자는 T2-5 몫」·「`minCount 1` 미채택」)을 반박하라

저자는 `experiment_run_id` 를 세팅하는 orchestrator 가 없다는 지적을 인정하면서도 그것을 T2-5 산출물로 미뤘고, `experimentRun minCount 1` 강제는 「실런 밖 위반까지 죽인다」며 채택하지 않았다.

- 사슬을 실물로 훑어라: `findings.py`(env 읽기) → 게이트 sidecar(`gate-introduced/0`·`gate-contract/0` 가 이 필드를 운반하는가?) → `collect_violations.py` → `violation_adapter.py` → Q2. **끊긴 지점을 전수로** 찾고, 저자가 「어댑터가 굽는 골든」으로 닫았다고 주장하는 구간이 실제로 무엇을 증명하는지 판정하라.
- 게이트 sidecar 가 `experiment_run_id` 를 운반하는지 **직접 확인하라**. 운반하지 않는다면, 실런 중 재생성 루프가 남기는 용량 로그에 실런 식별자가 들어갈 경로가 있는가?
- `minCount 1` 대안(예: 실런 네임스페이스 전용 셰이프·SPARQL 층 검사·run-ready 게이트의 런타임 단언)이 「실런 밖 위반을 죽이지 않으면서」 강제할 수 있는지 설계하라. 가능하다면 저자의 미채택은 근거를 잃는다.

## 과제 3 — AS-12 처분(「scorer 정렬은 T2-0b 로」)을 반박하라

저자는 `findings_count_matrix` 의 violation_id 가 raw `(rule, file, symbol)` 해시로 남은 것을 **의도된 축 차이**(계수 골든 ↔ 사건 동일성)로 처분하고, 정렬하면 27종 EXPECTED 가 전부 바뀐다는 이유로 미뤘다.

- 동결 §6 의 계수 규약과 `findings_count_matrix` docstring 을 대조해, 그 violation_id 가 **사건 동일성을 뜻하는지** 아니면 stdout 계수 지문인지 판정하라.
- 라인번호가 바뀌는 상황이 **채점에서 실제로 발생하는지** 실물로 따져라(재생성 루프가 코드를 고치면 라인이 밀린다 — 그때 scorer 가 같은 위반을 다른 위반으로 셀 수 있는가). 발생한다면 이것은 **A/B 판정 지표(위반 수)의 오염**이고 T2-0b 로 미룰 수 없다.
- 27종 EXPECTED 재생성의 실제 비용과 위험을 산정하라(`--emit-expected` 존재 여부·기계적 갱신 가능성).

## 과제 4 — 중재가 놓친 것

위 3건 밖에서, 수리 자체의 결함을 찾아라. 특히:
- 「전면 채택」으로 분류했으나 **수리가 원 지적을 실제로 닫지 못한** 항목(수리 후 실물을 직접 돌려 확인하라).
- 수리가 **새로 만든** 결함(예: 중복 대표 선택 규칙·U+001F 구분자·`verify-runready` 의존 관계·`canonical_locator` 의 TypeError 가 기존 호출자를 깨뜨리는가).
- 문서와 실물의 드리프트(판단표 v3 §5·§8 이 실물과 어긋나는 곳).

## 산출 형식

과제마다: **판정(반박 성립 / 반박 실패) · 실측 근거 · 저자 판정의 정확한 오류 지점 · 요구 조치**. 반박이 실패했으면 실패했다고 쓰라 — 목적은 저자를 이기는 것이 아니라 **틀린 판정을 남기지 않는 것**이다.
