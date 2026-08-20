# 열린 스코프 레인 AN — T2-3 구간 전체의 미검토 위험 (적용 전)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only). 이 레인은 **정해진 과제 목록이 없다** — 저자가 «묻지 않은 것»을 찾는 것이 임무다. 칭찬·요약 금지.

## 맥락

이 저장소는 dddjango 플러그인(Django DDD 파이프라인 — 에이전트 + 결정적 검사기 27종)에 **온톨로지(RDF/SHACL/SPARQL) 정본 체계**를 도입하는 중이다. 동결 블루프린트 v3.2 아래 T0→T5 절차로 진행하며, 현재 **T2**(폐루프 완성 + 3암 A/B 실런)의 3번째 조각 **T2-3**에 착수했다.

T2-3이 만들려는 것:
- ⓐ 재생성 루프의 후반부(위반 레코드 → 주입 프롬프트 → 재생성 → 재검사 → 회전·수렴)
- ⓑ 그 루프를 파이프라인 coder에 편입하는 배선
- ⓒ 세션 jsonl에서 «사용자 게이트 반송 횟수»를 결정적으로 파생하는 계수기

저자의 설계 판단표: `workspace/design/2026-08-20-ontology-t2-3-design.md`(L1~L9·C1~C4·B1~B12·자인 W1~W12).

## 재료 좌표 (필요한 만큼만 읽어라)

- 계획·동결: `workspace/design/2026-08-19-ontology-t2-plan.md` · `-2026-08-18-ontology-blueprint-v3.md` · `2026-08-19-ontology-autonomous-protocol.md`
- 실물: `workspace/tools/`(regen_loop_prototype·session_telemetry·collect_violations·violation_adapter·ontology_structural_check·checker_baseline_matrix·findings_count_matrix·construct_drift_report) · `dddjango/scripts/` · `dddjango/commands/dddjango.md` · `dddjango/agents/`
- 기록: `workspace/eval/ab/`(B3-demo-record·T0-rule-owner-map-snapshot·T2-checker-baseline·T2-construct-drift·T1-order-pool) · `workspace/design/2026-08-18-ontology-adoption-log.md`
- 앞선 중재: `workspace/design/2026-08-19-ontology-t2-1-adversarial/MEDIATION-3.md` · `2026-08-20-ontology-t2-2-adversarial/MEDIATION-AL.md`

## 임무

**T2-3 구간 전체에서, 설계 판단표가 다루지 않은 위험을 찾아라.** 다음은 탐색 방향의 예시일 뿐 목록이 아니다:

- T2-3 산출물이 **이미 착지한 T2-1/T2-2 자산**과 충돌하는 지점(하네스 72레인·계수 골든·drift 골든·위반 sink·alias 대장·구조 검사 ⑥⑥′⑥″·`make verify` 편입분)
- T2-3이 **T2-4/T2-0b/T2-5에 남기는 빚** — 지금 정하지 않으면 실런 직전에 되돌릴 수 없어지는 결정
- 동결 문면(E1~E8·§1·§6·§7·§8)과 이 설계의 **문면 충돌** — 특히 개정 없이 조용히 어긋나는 것
- 측정 타당성: 이 구간이 만들려는 지표가 **A/B 판정을 오염**시키는 경로(교락·Goodhart·자기 귀속·관측이 처치를 바꾸는 경로)
- 안전·가역성: 실행되면 되돌리기 어려운 것(코퍼스 정본 개작·원장 append·설치본 경로·과금 유발 호출)
- 자율 완주 규약(R1~R7)의 **절차 위반**: 사용자 정지 조건(A/B 실패·방향 변경형 개정·비가역 외부 행위·T5 최종)에 해당하는데 자율로 처리하려는 것
- 이 저장소에 **이미 알려졌으나 T2-3이 상속하는 미처분 결함**(예: `anchor_diff` sink 스크럽·layer-skeleton #393/#395 오귀속·`ViolationShape` minCount 1 ↔ D12 충돌·context-isolation 가드 도달 불능)이 T2-3에서 증폭되는지

## 규율

- **실측·인용이 없는 지적은 내지 마라.** 파일:행 또는 실행 결과를 근거로 붙여라.
- 저자가 §6에 자인한 W1~W12를 되풀이하지 마라 — 자인의 **처분이 틀렸음**을 보이는 것만 발견으로 친다.
- 「더 좋을 수도 있다」류 취향 제안 금지. 실패 시나리오를 구체적으로 적어라(입력·상태 → 잘못된 결과).

## 출력 형식

| # | 심각도(blocker/major/minor) | 발견 | 근거(파일:행·실측) | 처분 제안 | 지금 처리 / T2-4 이월 / T2-0b 이월 / 사용자 상정 |

발견이 없으면 «발견 0 — 탐색한 축 목록»으로 무엇을 뒤졌는지 적어라. 저장소 수정 금지(read-only).
