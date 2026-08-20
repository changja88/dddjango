# 반증 레인 AO 중재 — 부분 채택 3건 + 상정 권고안 (2026-08-20)

> 규약 R1′의 «기각·부분 채택 건은 그 사유를 codex 반증 레인에 회부» 이행 결과.
> **4과제 전건 «반박 성립»** — 저자가 깎아낸 3건이 전부 틀렸고, 상정 권고안보다 나은 4안이 제시됐다.
> 판정: **전건 재채택(부분 채택 → 완전 채택 3 · 권고안 교체 1) · 기각 0.**
>
> 이 레인은 «중재 편향 방어»(R1′ 횡단 규칙)가 실제로 작동한 사례다. 저자의 «전건 채택에 가까운» 판정에
> 남은 3개의 깎기가 모두 근거 부족이었음이 실물로 드러났다.

## 저자 재현 검증

| 검증 | 결과 |
|---|---|
| AO#3의 설치 cache 실측 | **확증·심화** — source manifest `2.12.0` ↔ 설치 cache `2.11.0`. `--exclude=__pycache__` diff **30건**(codex 실측과 정확히 일치). 더욱이 **`findings.py`가 cache에 아예 없다** — T2-1 공용 구조화 출력 모듈 전체가 설치본에 미반영이다 |
| AO#1의 A암 현행 경로 | **확증** — `dddjango.md:137`(신규 red → coder/design/G1 반송)·`:164`(contract mismatch → G1)·`:165`(checker red → 소유자 반송)·`:99`(승인 범위 밖 귀속 → 우선 철회). A암은 gate red에서 **무행동하지 않는다** |

## 과제별 판정

### 과제 1 — AM#11의 «회전 레코드로 갈음» → **반박 성립 · 재채택**

**저자 오류**: 「A암도 회전 0 레코드를 남기면 3암 비교 가능」이라 했으나, ⓐ 회전의 정의는 «재생성 호출 1회»이므로 호출이 없는 A에 turn 이벤트를 쓰면 **사건과 run-level 영점 요약을 혼동**하고, ⓑ 더 치명적으로 **A암도 현행 파이프라인의 수리 경로(소유자 반송·철회·G1 회귀)를 탄다**. 즉 A의 실제 상태는 `regen_turns=0` ∧ `repair_cycles ≥ 0`이다. 「수리 노력」에 3암 공통으로 존재하는 관측은 총 토큰·시간뿐인데 그것은 설계·감사·테스트가 뒤섞여 pre-G2 수리를 분리하지 못한다.

**처분(채택)**:
- turn 이벤트는 **실제 재생성 호출 때만** 기록한다. run summary에 `regen_turn_count`를 의무화하고 A는 `0`.
- **`pre_gate_repair_cycles` 신설** — 1사이클 = «G2 blocker receipt 생성 → 소유자 재호출/철회/G1 반송 → 같은 exact gate receipt 재실행». 암·소유자·토큰·시간·변경 경로·전후 blocker identity를 기록.
- 두 지표의 역할 분리: `regen_turn_count` = **처치 노출량**, `pre_gate_repair_cycles` = **3암 공통 수리 노력**.

### 과제 2 — AN#7의 «실런 진단 플래그·셸 A 조기 종료» → **부분 반박 성립 · 부분 재채택**

**반박 실패한 부분**: 실런에서 `no_progress`를 진단 플래그로만 두는 처분은 사전 등록(`t2-plan:42`·`:69`)·동결 §6과 정합하며 **사용자 개정이 필요 없다**. 저자 처분 유지.

**반박 성립한 부분**: 셸 A에만 조기 종료를 허용한 것. 누락 시나리오가 구체적이다 — 위반 집합이 `{X}→{X}→{X}→∅`일 때 실런 정답은 turn 2에 `no_progress=true`를 기록하되 **계속하여** 3회전 후 `zero`다. 그런데 셸 A는 turn 2에서 끝나므로, 구현이 `no_progress`를 terminal로 잘못 공유하거나 2→3 budget 전이를 생략해도 **harness가 통과한다**. 세 번째 호출 receipt·예산 감소·post-edit 증거 재실행 전이가 전혀 커버되지 않는다.

**처분(채택)**: 셸 A와 셸 B는 **같은 상태기계**를 쓰고 양쪽 모두 `no_progress`를 **비종료 진단**으로 처리한다. harness에 결정적 fake-regenerator 픽스처 `{X}→{X}→{X}→∅`를 두어 **2→3 전이와 최종 `zero`를 단언**한다. 2회 조기 종료가 필요한 빠른 smoke는 별도 비규범 smoke로 둘 수 있으나 **상태기계 회귀 증거·셸 parity 증거로 산입하지 않는다**.

### 과제 3 — AN#13의 «probe 설계만·실행은 T2-0b» → **반박 성립 · 재채택**

**저자 오류**: live cache 갱신 이연은 정당하지만(R3-3), 「T2-3에서는 설계만」은 **blocker를 해소하지 않고 검증되지 않은 artifact를 다음 게이트로 넘긴다**. 그리고 **설치 갱신 없이 가능한 검증이 실제로 존재한다** — `corpus_mirror_sync.py --check` 11/11 · source scripts `diff -rq` green · `claude plugin validate dddjango --strict` Validation passed · prototype `--self-test` green(전부 이미 Makefile에 배선).

**처분(채택) — 게이트 2분할**:

- **T2-3 exit 조건(live cache 무수정)**: ① core·wrapper·양 런타임 source mirror diff 0 ② `make verify`·corpus mirror·strict manifest validation green ③ **source plugin root 또는 임시 materialized plugin tree**에서 실제 red 픽스처로 loop probe 성공 ④ 같은 픽스처의 Claude/Codex 행동 parity 성공 ⑤ source tree hash 봉인.
- **T2-0b hard blocker(사용자 승인 필요)**: cache 갱신 후 source ↔ Claude cache ↔ Codex cache 파일목록·해시 동등성 **및 동일 probe를 cache 경로에서 재실행**해야만 manifest 봉인 허용.

즉 **live 배포만 이연하고 artifact 검증은 이연하지 않는다.**

### 과제 4 — 상정 권고안 «가» → **반박 성립 · 권고안을 «라»로 교체**

**반박 실패한 부분**: 「G2 승인 제외 = 인수 테스트 미확정」은 성립하지 않는다. 현행 순서상 인수 테스트 통과 여부는 step 5에서 이미 확정되고 실패는 해결하거나 `pending`으로 설계 반송되므로, 정상 도달한 gate 시점에는 arm-independent 인수 pass가 확정돼 있다.

**반박 성립한 부분(핵심)**: 안 «가»는 **A만 현행 수리 경로에 들어가기 전** 잘라 채점하고 B/C는 루프와 증거 재검증을 마친 뒤 채점한다. 이는 「A는 루프가 없으니 전 상태 = 후 상태」인 대칭 비교가 아니라, **A에 배정된 현행 파이프라인 처치조차 미완료한 상태**와 B/C의 완료 상태를 비교하는 것이다. 따라서 필요한 개정은 「인수 게이트 문면」만이 아니라 **A 처치 정의·런 유효성·공통 측정 종료점 전부**다.

**처분(채택)**: 사용자 상정 권고를 **안 «라» — 공통 post-treatment 측정 종료점**으로 교체한다. 요지:

1. 최초 구현·step 5 검증을 마치고 동결 인수 테스트가 통과한 상태를 **`S0`로 봉인**.
2. 첫 결정적 gate receipt 후 암별 처치 — A는 **null treatment**(재생성 0), B/C는 위반 0이면 종료·아니면 정확히 N=3(`no_progress`는 진단 플래그).
3. 처치 종료 상태를 **`S1_x`로 봉인**.
4. **세 암 모두** `S1_x`에서 같은 동결 인수 테스트와 같은 scorer를 새로 실행.
5. 인수 pass인 `S1_x`만 `V_x` 채점. 인수 실패는 기존대로 판정 실패.
6. **G2 제시·승인은 세 암 모두 채점 요건에서 제외**하고 `pipeline_complete`로 별도 기록.
7. 채점 후 현행 수리 경로를 계속하려면 **별도 비채점 복제본**에서 수행하며, 봉인된 `S1_x`·`V_x`를 바꾸지 못한다.

이 안은 A를 «루프 전 임시 상태»가 아니라 **null treatment가 끝난 post-treatment 상태**로 정의하고, B/C도 같은 checkpoint에서 측정한다. 시간상 A가 먼저 끝나는 것은 처치 차이지만 **측정 단계·acceptance 재검증·scorer epoch는 대칭**이다.

**세 안의 대가 재계산(AO 제공)**:
- **가**: A 정의와 런 유효성을 동시에 바꾸고 A의 기존 owner-remand 수리를 제거 — 저자가 적은 「G2 승인 제외」만으로 불충분.
- **나**: `A = 재생성 0`·`B−A = 폐루프 번들` 사전 등록과 직접 충돌. 다만 목표를 「완성 산출물의 운영 가능성」으로 바꾸면 «가»보다 낫다(그때는 사실상 `full diagnostic / snapshot / SPARQL` 3암의 **다른 실험**).
- **다**: 사전 등록을 유일하게 그대로 지키는 안. **저자의 「18런 상당수 무효화」는 실측이 아니라 가능성**이며, 실제 invalid 비율이 낮으면 «다»가 «가»보다 낫다 — 이 표현은 정정한다.

## 종합 — 이 레인이 바꾼 것

| 항목 | 중재 v1(저자) | AO 반박 후 확정 |
|---|---|---|
| 수리 노력 관측 | 회전 레코드로 갈음 | `regen_turn_count` + **`pre_gate_repair_cycles` 신설** |
| `no_progress` | 실런 진단·셸 A 조기 종료 | 실런 진단 **유지** · **셸 A도 비종료**(상태기계 통일) + fake-regenerator 픽스처 |
| 설치 cache | probe 설계만 | **T2-3 exit 5조건**(source·임시 tree 검증) / T2-0b hard blocker 분리 |
| A암 상정 | 안 «가» | **안 «라»**(공통 post-treatment 측정 종료점) + 개정 문면 초안 |

---
*좌표: `PROMPT-AO.md` · `log-AO.txt` · 선행 중재 `MEDIATION-AM-AN.md`.*
