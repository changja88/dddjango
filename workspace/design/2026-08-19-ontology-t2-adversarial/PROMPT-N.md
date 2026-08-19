너는 적대 검증자다. dddjango 온톨로지 T2 계획의 **동결 정합·실물 정합**을 반증하라 — 계획이 동결 문면을 어기거나, 실물 좌표가 틀렸거나, 판정 기준의 전제 규약을 미작성 문서로 미루는 결함(T1 계획 리뷰의 blocker 공통 뿌리였음)을 찾아라.

## 재료 (저장소 루트 기준)
- 검증 대상: `workspace/design/2026-08-19-ontology-t2-plan.md` 전문.
- 동결 정본: `workspace/design/2026-08-18-ontology-blueprint-v3.md` — 특히 E8(42행)·§6(93~98행)·§7(110행)·§8 T2 행(120행)·§9 도구 처분표(140~146행)·§10.
- 실물 대조: `dddjango/scripts/findings.py`·`dddjango/scripts/registry_gate.py`·`workspace/tools/regen_loop_prototype.py`·`workspace/tools/session_telemetry.py`·`workspace/eval/ab/B3-demo-record.md`·`workspace/tools/ontology-authoring.md`(§13~§17)·`ontology/wiring/registry.ttl`·`workspace/design/2026-08-19-ontology-t1-review.md`.

## 집중 질문
1. 계획의 각 실물 주장(§1 표)이 실제 파일과 일치하는가 — 수치·경로·docstring 문면 표본 재검.
2. 동결 위반: E8(주입 재료 = 번호+검사기 산출 발췌 한정)·§6(B암 재료 T0 스냅숏·배선 재지정 순서·층화 폴백)·§8 완료 기준(설치본 위반 레코드 경로·CNL·반송 계수기 세션 jsonl 파생) 중 계획이 빠뜨리거나 어긴 항목.
3. 판정 기준의 전제 규약이 이번에도 미작성 문서로 밀렸는가 — 예: 채점 하니스의 «커밋 고정» 절차 문면, 위반 그래프 적재 위치(`workspace/eval/violations/`)가 §3 트리 규약과 충돌하는지, 반송 이벤트의 조작적 정의 부재.
4. T2-1 개작 순서와 A/B 순서의 정합 — 개작(처치 도구)과 실런 사이 시점 규율이 계획에 명시돼 있는가.
5. 놓친 T2 완료 기준(블루프린트 §8 T2 행 전건 대조 — 하나라도 계획에 없으면 발견).

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
# L-N 동결·실물 정합 결과
| # | 심각도 | 결함 | 근거(문면 인용) | 수정 제안 |
(발견 0이면 «발견 0») + 블루프린트 §8 T2 완료 기준 전건 대조표
