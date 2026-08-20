# 선행 설계 리뷰 레인 AQ — T2-4 열린 스코프 (적용 전)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only). **범위 제한이 없다** — 레인 AP가 지정 과제를 맡고 있으니, 너는 **저자도 AP 프롬프트도 보지 못한 축**을 찾는 것이 임무다. 칭찬·요약 금지. 모든 주장에 **파일:행 인용 또는 재현 명령**.

## 대상

`workspace/design/2026-08-20-ontology-t2-4-design.md` — T2-4(SPARQL 규칙 팩 카탈로그·C암 재료 ②) 설계 판단표 v1. **아직 구현 0줄.**

§1(실물 좌표 M1~M15)과 §7(자인 약점 W1~W12)에 저자의 근거와 자신 없는 지점이 공개돼 있다. **자인을 되읊는 것은 발견이 아니다.**

## 이 저장소를 이해할 좌표

- 온톨로지 스택: `ontology/{vocab,shapes,rules,wiring}/*.ttl` · `ontology/ISSUED` · `ontology/LEDGER.tsv` · 검사 도구 `workspace/tools/ontology_*.py` · 저작 규약 `workspace/tools/ontology-authoring.md`
- 질의 엔진은 `.venv/bin/python`(rdflib 7.6.0). 시스템 `python3`에는 rdflib가 **없다** — 이 비대칭 자체가 설계 제약이다(E7 배포 경계).
- 검사기·위반 파이프라인: `dddjango/scripts/{findings,registry_gate,regen_core,checker_registry}.py` · 미러 `codex-dddjango/scripts/`
- 실험: `workspace/design/2026-08-19-ontology-t2-plan.md` · 동결 `…blueprint-v3.md` · 발주 `workspace/eval/ab/T1-order-pool.md` · 규약 `…autonomous-protocol.md`
- 빌드·검증 진입점: `Makefile`(`verify`·`verify-base`·`ontology-*`) — 무엇이 상시 검사되고 무엇이 안 되는지 여기서 확인된다.
- 선행 판단표와 그 리뷰 이력: `2026-08-20-ontology-t2-3-design.md` · `2026-08-20-ontology-t2-3-adversarial/`(레인 AM/AN/AO·MEDIATION·SELF-FINDINGS) · `2026-08-20-ontology-t2-2-alias-ledger.md`

## 공격을 시작할 만한 방향 (구속 아님 — 더 나은 축을 찾으면 버려라)

- **문서가 침묵한 것**: 판단표가 «정하지 않는다»고 선언한 것(§0) 중, 실제로는 **정하지 않으면 구현이 막히는** 항목이 있는가.
- **선행 자산과의 충돌**: T2-3이 만든 루프·sidecar·계수기·runtime parity 검사·probe와 T2-4가 신설하려는 것 사이의 계약 충돌. 특히 `identity()`의 단일 canonicalizer 지위, `DJR_LOOP_*` 환경 스위치 공간, step 6′ 절차 문면(양 런타임 미러).
- **검증 자산의 검출력**: §5 V1~V6이 실제로 무엇을 잡고 무엇을 못 잡는지. T2-3에서 「픽스처 통과 ≠ 검출력」이 실증됐다 — 같은 함정이 여기 어디에 있는가.
- **어휘·셰이프 정합**: `djr:pathGlob` 신규 사용이 `djr-shapes.ttl`·`meta-house.ttl`·`ontology_structural_check`·`ontology_meta_shacl`·골든 페어 규약과 어떻게 상호작용하는가. 저-공리 프로파일(E2)·blank node 금지(E4)·정본 직렬화 게이트를 통과하는가.
- **원장 규율**: 새 TTL 파일·새 산출물이 `LEDGER.tsv`·`ISSUED`·`ontology_ledger_check`·`ontology_issued_check`·`reverse_coverage`(미설명 파일 0 규율)·`tree_mirror_check`에 어떤 의무를 만드는가. 판단표가 그걸 등재했는가.
- **실험 타당성**: 이 팩이 T2-5 18실런에서 실제로 무엇을 측정하게 되는지. 판정 산식(§2 T2-0a)·층화 비대칭·개정 7(공통 post-treatment checkpoint)과의 상호작용에서 **결과가 해석 불가능해지는** 조합이 있는가.
- **비용·시간**: 팩 생성·verify 편입이 `make verify` 소요를 얼마나 늘리는가(현재 실측치를 재라). 상시 검사에 SPARQL을 넣는 것의 대가.
- **되돌리기**: T2 게이트에서 C가 지면 이 산출물은 어떻게 처분되는가. §7 롤백 경로와 정합하는가.

## 산출 형식

발견마다: **ID · 심각도(blocker/major/minor) · 주장 · 실측 근거(인용/명령) · 왜 저자가 못 봤는가 · 요구 조치**.

마지막에 두 절을 반드시 두라.

1. **「가장 위험한 단일 결함」** — 하나만 고르고, 그것이 실런 18런을 무효로 만들 수 있는 경로를 끝까지 그려라.
2. **「이 설계가 옳은 지점」** — 공격이 실패한 곳. 저자가 이미 방어를 마친 축을 명시하면 중재가 시간을 아낀다. (칭찬 금지 — 「공격했으나 뚫리지 않았다」의 기록이다.)

발견이 없으면 없다고 쓰라. 채우지 마라.
