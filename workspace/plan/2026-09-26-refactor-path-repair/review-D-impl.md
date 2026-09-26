# 구현 독립 리뷰 D — 리팩터 요청 경로 수리 (2026-09-26)

- 대상: 작업 트리 미커밋 변경(`git diff HEAD`). 사용자 변경 4건(`docs/master.html` · `field-report-4/…` · `refactor-campaign/` · `request-guide-audit/synthesis-v2.md`)은 제외했다.
- 근거: `plan-v2.md`(처분표) · `plan-v1.md`(E1~E16) · `design-v3.md` · `review-C-plan.md` · `behavior-tests.md` · scratch `apply_edits.py`·`apply_edits2.py` · `docs/DEVELOPMENT.md`.
- 표기: C = `dddjango/commands/dddjango.md` · CX = `codex-dddjango/skills/dddjango/SKILL.md` · HR = `dddjango/skills/discipline-houserules/SKILL.md` · G = `dddjango/REQUEST_GUIDE.md` · TB = `dddjango/scripts/check-transaction-boundary.py`.
- 방법
  - rdflib 로 HEAD ttl 과 작업 트리 ttl 을 비교했다. 블록 텍스트 변화·새 블록·statesNorm 부착·Expression 체인·라벨을 실측했다(scratch `revD/revd_graph.py`).
  - `make verify` 구성 명령 가운데 읽기 전용인 것을 개별 실행했다(아래 §4).
  - F4-20 은 scratch 사본(`revD/f420/`)에서 탐침 케이스와 수리 시제품을 돌렸다.
  - 실행 전후 `git status --porcelain` 과 `git diff HEAD` 해시가 같음을 확인했다(저장소 쓰기 0).
  - 이 파일 외에는 쓰지 않았다. Serena·Graphify 는 쓰지 않았다.

## 판정: **수정 후 승인** — blocker 0 · major 4 · minor 14

- 계획 v2 처분표의 «수용» 26건은 정본·투영·Codex 미러에 모두 들어갔다.
- 그래프 기계 정합(계수·체인·wiring·ISSUED·LEDGER·렌더·rulepack)은 전부 맞다.
- `make verify` 는 봉인 재발행 전제의 봉인 2줄 외에는 green 으로 예측된다.
- 다만 네 가지를 고쳐야 한다.
  - 새 문장 둘이 바뀌지 않은 문장과 충돌한다(M-1 · M-2).
  - F4-20 수리가 참양성을 놓치는 새 경로를 만든다(M-3). 실측으로 재현했다.
  - 행동 시험 뒤 2차 보정이 검토 없이 규범을 바꿨다(M-4).

## Blocker

없음.

## Major

| # | 위치 | 문제 | 근거 | 권고 |
|---|---|---|---|---|
| M-1 | C:106(s006/b11 · R-3486) | **«미룰 수 없음» 항목이 «동작 변경은 별도 요청으로»로 이번 실행에서 빠진다.** 새 STOP 은 «미룰 수 없음» 항목에서 ⓑ 만 뺀다. 선택지 «동작 변경은 별도 요청으로 / 작업 중단»은 그대로 남는다. «별도 요청»을 고르면 그 항목은 `ⓐ 재상정` 절로 가고, G2 잔존 M 에서도 빠진다(C:173). 결과적으로 «손대지 않아도 해로운» 위반을 안은 채 G2 를 통과한다. 이것은 R-0199(«미룰 수 없음»엔 ⓑ 없음 · C:80)를 우회하는 미룸이다. 같은 날 쓴 충돌 규칙(C:83 · R-3480)은 «미룰 수 없음» 항목을 «경계를 넓혀 정리 / 작업 중단» 둘로 닫았다. 여기서는 그 형태를 따르지 않았다. 게다가 이 경로는 드물지 않다. 대표 예시인 catch-all handler(C:79)는 정리하면 밖에서 보이는 오류 응답이 바뀌는 바로 그 유형이다. | C:79 · C:80 R-0199 · C:83 · C:106 · C:173 R-0411 | s006/b11 괄호를 바꾼다: ««미룰 수 없음» 항목은 «동작 변경을 포함한 별도 요청을 먼저 진행(이 요청은 여기서 정지 — ⓐ′ 와 같은 형태) / 작업 중단» 둘뿐이다». R-3486 라벨에 같은 뜻을 반영한다. 또는 C:173 에 «처분 = 별도 요청인 «미룰 수 없음» 항목이 남으면 G2 를 제시하지 않는다»를 둔다. 둘 중 하나로 정한다. |
| M-2 | C:113(s007/b3 · R-3499) ↔ C:121(s007/b11 · R-0299) · C:205(s010/b6 · R-0442) | **검사기 오탐 STOP 의 경로를 두 문장이 서로 반대로 정한다.** 새 문장(C:113)은 coder 가 보고한 «`STOP_FOR_USER_APPROVAL`(플러그인 결함)»을 «설계 반송이 아니라 사용자 선택지»로 보낸다. 바뀌지 않은 두 문장은 역할이 보고한 `STOP_FOR_USER_APPROVAL` 을 **예외 없이** 다르게 처리한다. Phase 2 5번 하위 불릿(C:121)은 «G2 blocker · design-architect 를 거쳐 G1/G1′ 반송»이다. 엣지 절(C:205)은 «모두 design-architect/G1 반송»이다. 예외는 C:113 한 곳에만 있다. 그런데 괄호가 가리키는 것은 엣지 절뿐이고 C:121 은 가리키지 않는다. 반송받은 architect 는 오탐을 «설계로» 피해 가게 된다. 그것이 N20(R-3489)이 막으려는 우회 구현의 설계판이다. 런타임은 일반 규칙(C:121·C:205) 쪽으로 읽을 위험이 있다. 같은 문면이 CX 에도 있다(CX:131 ↔ CX 엣지 절). | C:113 · C:121 · C:205 · R-0299 · R-0442 | R-0299·R-0442 에 clarification 개정을 넣는다. 두 문장에 «단 Phase 2 3번 슬라이스 0 의 검사기 오탐 STOP(플러그인 결함)은 이 반송의 대상이 아니다 — 그 절차를 따른다»를 덧붙인다(라벨 무변 가능). C:113 괄호는 «(Phase 2 5번·엣지 절 Contract mismatch)»로 넓힌다. CX 에도 같게 반영한다. |
| M-3 | TB:516-527 · TB:35-38(docstring) | **반복 변수 전파가 «이름» 단위라 참양성이 사라지는 새 경로가 생긴다.** 한 함수 안에서 반복 변수 이름을 다시 쓰면 문제가 된다. 팩토리 컬렉션 루프가 `order` 를 `factory_born` 에 넣는다. 그러면 조회 결과를 도는 다른 루프의 `order`(필드 직접 대입 뒤 save)도 통과한다. **실측(scratch `revD/f420/tree/…/mixed_orders`)**: `for order in [Order.open_pending(i) …]: save(order)` 다음에 `for order in repo.list_open(): order.status = "closed"; save(order)` 를 둔 코드다. HEAD 는 #195 2줄(:19 오탐 · :22 참양성)로 exit 2 였다. 작업 트리는 **exit 0** 이다. 참양성 :22 가 사라졌다. 컬렉션 이름 집합 `element_factory` 도 흐름을 보지 않는다. 그래서 `orders = [F() …]` 뒤에 `orders = list(repo…)` 로 재대입해도 같은 누락이 난다. docstring 은 «fail-closed»라고 적었고, 진단(`diag-B3-F4-20.md` §4)은 «새 사각지대가 생기지 않는다»고 적었다. 둘 다 이 경로를 빠뜨렸다(정직 기록 불비). 같은 부류의 약점이 스칼라 대입에는 이미 있었다. 하지만 반복 변수는 이번에 새로 열린 통로다. | TB:503-527 · `diag-B3-F4-20.md`:57 · 탐침 출력(HEAD exit 2 / 작업 트리 exit 0) | fail-closed 로 좁힌다. 같은 함수에서 비팩토리 반복(또는 비팩토리 대입)의 target 이기도 한 이름은 전파하지 않는다. **시제품 확인**(`revD/f420/proto/check-transaction-boundary.py` · 3행 교체 — `loop_factory - loop_other`): 탐침은 :19·:22 둘 다 red 가 된다(참양성 복원 · 이름 충돌 함수의 오탐은 fail-closed 로 남는다). `good` 은 exit 0 이고, `bad_rules` 는 현재 출력과 byte 동일하다. 섞인 루프 케이스를 bad_rules 픽스처로 추가한다. 그다음 EXPECTED 두 표와 `pregate_symbol_kinds.json` 을 다시 산출한다. docstring 에 «이름 단위 판정 — 같은 이름이 비팩토리로도 묶이면 전파 안 함»을 적는다. |
| M-4 | C:67(s004/b1 · F1) · C:86(s005/b14 · F4) · `apply_edits2.py` | **행동 시험 뒤 2차 보정(F1~F5)이 계획·리뷰를 거치지 않고 규범을 바꿨다.** (a) F1 은 «정리 요청에는 «이 기능을 둘 자리» 질문을 내지 않는다»를 넣었다. 이것은 R-0204(«기존 영역 접촉 신호 시 둘 자리 선택 추가» · Obligation · C:80 문면 무조건)를 제한한다. 그런데 R-0204 는 개정되지 않았고 C:80 에도 예외가 없다. 새 제한은 Obligation 인 R-3470 라벨 안에만 들어갔다. 계획 v2 는 같은 이유(새 차단이 기존 규범을 제한)로 R-0411 을 개정했다(M-8c). 그 원칙과 어긋난다. (b) F4 는 «G0 정지 때 스코프 메모가 있으면 `scope.md` 도 쓴다»를 넣었다. 그런데 기존 폴더를 쓰는 경우를 다루지 않는다. ⑴(G2 승인 끝)·⑵ 폴더에서 G0 가 멈추면 **승인된 `scope.md` 를 승인되지 않은 메모로 덮어쓴다**. 이것은 경계 절이 위임을 금지한 «`scope.md` 사후 개정»에 닿는다(C:217). 그런데 N25(R-3494) 면제 목록에는 `refactor-scope.md` append 만 있다. (c) 보정 뒤 문면(F1·F2·F4·F5)을 다시 시험하는 항목이 2차 목록(`progress.md`)에 없다. 2차는 T2b·T4b·T4pp·T4ca·T4cb·T9·T10·T11·CTRL 이다. | C:67 · C:80 R-0204 · C:86 · C:217 R-0452 · `behavior-tests.md` F1~F5 | (a) R-0204 에 clarification 을 넣는다. C:80 문장에 «(정리 요청 제외 — 모드 판별 절)»을 붙인다. R-3470 라벨의 «배치 질문 없음»은 Prohibition 인 R-3471 쪽으로 옮기는 것을 검토한다. (b) F4 를 «신규 폴더일 때만 `scope.md` 를 쓰고, 기존 폴더면 스코프 메모를 `G0 정지` 절 안에 싣는다»로 좁힌다. (c) 2차에 T1(F1·F5 배치 질문 자리) · T3(F2·F4) · T5(F3 목록 머리 줄) 회귀 1회씩을 더한다. |

## Minor

| # | 위치 | 문제 | 근거 | 권고 |
|---|---|---|---|---|
| m-1 | C:189(s009/b2) ↔ C:79(s005/b8) | 수정 모드의 스캔 대상 문구가 M-6 처분 이전 형태로 남았다(«이번 수정이 파일을 추가·변경하는 BC 전부»). Phase 0 쪽은 «스코프 메모가 적은 BC + 설계 확장 시 추가 스캔·G0 재승인»이다. 또 설계가 스캔 밖 BC 에 파일을 두는 것을 **감지하는 지점**이 Phase 1 어디에도 없다. G1/G1′ 배너 전 file-plan BC 와 스캔한 BC 를 대조하는 단계가 없다. | plan-v2 M-6 | C:189 괄호를 «Phase 0 3번의 대상 BC 정의 그대로»로 바꾼다. G1/G1′ 배너 직전에 «file-plan 의 BC ⊆ 스캔 BC» 확인 한 구절을 둔다. |
| m-2 | C:58(s003/b10) ↔ C:82 | «사전 위임은 … 빚 질문의 생략이 아니다»는 «발주가 빚 답을 ⓐ 로 미리 정했으면 그대로 받는다(무질문)»와 문면이 부딪힌다. T8 은 무질문으로 합격했지만, 질문을 그래도 내야 한다고 읽힐 여지가 있다. | T8 | «빚 질문(발주 고정 ⓐ 는 질문 없이 결정 줄 기록)»으로 한정한다. |
| m-3 | C:85(잇기) | «앞 실행이 마지막으로 승인받은 게이트의 다음 단계부터 잇고, 새 ⓐ 가 있으면 G1′ 로 합친 뒤 Phase 2»라고 적었다. 마지막 승인 게이트가 G0 뿐이면 다음 단계는 Phase 1 이다. 그런데 뒤 문장은 G1′ 을 거쳐 Phase 2 로 건너뛰라고 읽힌다. | review-C M-2 | «Phase 1 이전이면 새 ⓐ 를 Phase 1 입력(슬라이스 0)에 합치고, G1 이후면 G1′ 로 합친다». |
| m-4 | C:106 | «앞의 STOP 과 …»이 두 STOP(동작 불변 불가·비위반 이동) 가운데 어느 것인지 모호하다. 비위반 이동 STOP 의 답(«범위에서 빼고 진행 / 요청 종료»)은 처분 목록에 없어 기록 위치가 없다. 선택지가 다른데 «같은 STOP» 이라고 부른다. | — | «동작 불변 불가 STOP 과 …»으로 특정한다. 비위반 이동 STOP 의 답 기록 위치(예: `scope.md` 범위 아님 줄 또는 STOP 기록 파일)를 한 구절로 정한다. |
| m-5 | C:84 · C:106 | 정리 요청에서 재상정으로 ⓐ 가 전부 빠지고 불편 항목도 없으면 할 일이 없는 설계로 진행된다. «정리할 것이 없으면 멈춘다»는 G0 에만 있다. | R-3481 | s006/b11 끝에 «정리 요청에서 남은 ⓐ·불편이 0 이면 G0 정지와 같이 끝낸다»를 둔다. |
| m-6 | C:191(s009/b4 · R-3493) | 수정 모드는 «G2 배너에 ⓐ 잔존 1행을 둔다»라고만 적었다. M>0 차단(R-0411)이 수정 모드 G2 에도 걸린다는 문면이 없어, 표시만 하는 의무로 읽힐 수 있다. | C:173 · C:195 | «ⓐ 잔존 1행과 그 차단 조건(M>0 이면 G2 제시 금지)»으로 적는다. |
| m-7 | C:82(b10 · R-3476) | 출처 없는 ⓑ 의 STOP 선택지 «ⓐ / 원문 갖춘 ⓑ / 작업 중단»에 ⓐ′ 가 없다. 빚이 있는 BC 가 2개 이상이면 C:80 이 ⓐ′ 를 필수 선택지로 둔다. | C:80 R-3473 | «(빚이 있는 대상 BC 가 2개 이상이면 ⓐ′ 포함)». |
| m-8 | G:103 | «여러 업무 영역에 걸치면 영역별 정리를 먼저 따로 진행하는 선택지도 나옵니다»는 과약속이다. 런타임 조건은 «**빚이 있는** 대상 BC 가 2개 이상»(C:80)이다. | — | «여러 업무 영역에 정리할 위반이 있으면 …». |
| m-9 | G:179-188(§7) | 대리 규칙에 «실행 선택의 **폐기**도 사용자 원문이 필요하다»가 없다(런타임 C:85 «출처 없는 폐기는 위임되지 않는다»). 현장 기존 폴더는 96개 중 95개가 ⑶ 미종료로 판정된다(T2a·T5). 그래서 대리 레인은 기존 폴더를 처음 고를 때마다 실행 선택에서 멈춘다. 대가 목록의 첫 항목이 «잇기»라 대리가 그것을 고르면 대량 귀속이 난다(T5 실측 커밋 1,924). | T2a · T5 | §7 에 한 줄: «끝나지 않은 이전 작업을 버리는 결정도 사용자 원문(파일·줄·시각)과 함께 전하고, 이미 승인된 작업이면 그 승인 기록 위치를 전합니다». |
| m-10 | G:122-124(§4) ↔ C:82 | 가이드는 사용자가 «정리할 대상을 밝혀 이번에는 미룬다는 결정»을 요청에 적을 수 있다고 약속한다. 그런데 런타임의 «본인 직접»은 «이 실행에서 사용자가 직접 답함»뿐이라, 대화형 본인 요청문 안의 ⓑ 를 어떤 출처로 볼지가 없다. 출처 없는 ⓑ 로 분류되면 본인 앞에서 STOP 기록이 나고, STOP 선택지에는 «본인 직접 ⓑ»가 없다. | C:82 · G:122 | b10 에 «대화형 세션에서 사용자가 직접 입력한 요청문의 미룸은 본인 직접(요청 시각)»을 더하거나, 가이드에 «요청에 적은 미룸은 첫 단계 질문에서 다시 확인합니다»를 적는다. |
| m-11 | C:85(새 실행) · C:82(N10) | «앞 기록은 git 이력»은 무커밋 대화형 실행(C:218 — 커밋은 사용자 지시 소관)에서는 성립하지 않는다. 이관 빚 목록(경로 미정 · C:160)이 실행 사이에 이월되는지도 정해지지 않았다. 이것은 «앞 실행의 ⓑ 를 이월하지 않는다»·N10(이관 빚 = 미룸)과 부딪힐 수 있다. | C:160 · C:218 | «앞 기록은 git 이력(무커밋이면 `refactor-scope.md` 를 새로 쓰기 전 앞 실행 절을 보존)» · «새 실행은 앞 실행의 이관 빚 목록을 쓰지 않는다». |
| m-12 | HR:29 ↔ C:82 · `dddjango/agents/coder.md`:57 | 용어가 겹친다. HR 은 «사용자 ⓐ 결정»을 발주 고정·대리 답까지 포함하도록 정의한다. C 는 «사용자 결정» 표기를 본인 직접·사용자 원문에만 쓴다. 계획 m-7 처분대로이긴 하다. 하지만 coder·reviewer 가 두 문서를 함께 읽으면 헷갈릴 수 있다. `coder.md`:57 «G0 사용자 빚 결정»은 그대로다. | plan-v2 m-7 | 이번에는 기록만 한다. 다음 개정에서 «G0 ⓐ 결정»으로 용어를 통일한다. |
| m-13 | C:85 · R-3470 | nit ① «Phase 2 6번이 `· build_anchor <SHA>` 를 덧붙인다» — 파일 기록 시점은 Phase 2 첫 파견 직전이다(C:122). 6번에서 붙인다고 오독할 수 있다. nit ② R-3470(Obligation) 라벨 안에 금지 내용(«배치 질문 없음»)이 섞였다(M-4a). | C:122 | «Phase 2 첫 파견 직전(6번 규칙)» · M-4a 처리 때 함께 정리한다. |
| m-14 | 운영 | 조감도 HTML(`ontology-adoption-map.html`, 사용자 상시 지침)을 아직 갱신하지 않았다. 봉인도 아직 재발행하지 않았다(전제대로). 행동 시험 2차가 진행 중이라, 이 판정은 1차 결과와 문면만을 근거로 한다. | `progress.md` «다음» | 커밋 전 순서: 조감도 → seal `--write` → `make verify`. |

## 확인해서 문제없던 항목

**계획 대비**
- 처분표의 «수용» 26건이 모두 들어갔다.
  - B-1(재상정 절 · 오탐 STOP 선택지 · M 에서 재상정 제외 · `재상정 제외 K건` 행 · N25 · R-0203 라벨)
  - M-1(⑴~⑷ · 대가 3 · Read/`git show`) · M-2 · M-3(STOP 선택지 셋 · 두 번째에 작업 중단 · 가이드 §7 한 줄)
  - M-4(b14 · b12 끝 문장 삭제) · M-5(순서 · 이름표 · b9 폴더 ⓐ/ⓑ 치환 3건) · M-6(C:79) · M-7 · M-8 · M-9
  - m-1~m-8 · m-10~m-13 · m-15 docstring · m-16 progress
- 기각 m-9 와 기록 m-14 도 처분대로다.
- 계획 밖의 변경은 `apply_edits2.py` 의 F1~F5 뿐이다. 모두 `behavior-tests.md` 에 기록돼 있다(문제는 M-4).

**그래프**(rdflib 실측)
- 신설 30(R-3470~R-3499): 모두 rev1 이다. `specializationOf` 가 맞고, 진술 블록은 각각 하나다. 배치는 계획과 같다.
  - s005/b10 ← N5~N10 · b13 ← N13~N16 · b14 ← N27·N28 · s006/b11 ← N17·N18·N29 · s007/b3 ← N19·N20·N30
- deontic 유형은 문장과 맞는다(Prohibition: R-3471·R-3472·R-3475·R-3489·R-3495 · Permission: R-3477·R-3494). 예외는 R-3470 라벨의 혼재(m-13)다.
- 개정 17: `wasRevisionOf` 가 직전 current 를 가리키고 revision 은 +1 이다.
  - R-0411 은 `@2026-09-03b` rev3 → rev4 다.
  - R-0157 은 rev2 → rev3 clarification 이다.
  - R-0157·R-0454 는 clarification 이고 라벨이 무변이다. 나머지 15건은 amendment 이고 라벨을 교체했다.
- 새 블록 6: s005 order 10~14 · s006 order 11 이 연속이고 `kind-norm` 이다.
  - 구분자: b10~b13 은 `\n`, b14·s006/b11 은 `\n\n` 이다. 렌더하면 4번 항목 아래 3칸 들여쓴 느슨한 목록이 된다(C:81-87).
- wiring: command 29건은 `a/command-dddjango`, R-3495 는 `a/agent-discipline-reviewer` 다. 누락이 없다.
- ISSUED: R-3470~R-3499 가 연속 append 되고 R-3495 만 houserules 경로다. `ontology_issued_check` 가 정합이다.
- LEDGER: 9행 append(command s002·s003·s004·s005·s006·s007·s009·s011 + houserules s004-1). `ontology_ledger_check` 가 정합이다.
- 2차 보정은 오늘 새로 넣은 문장만 건드렸다: s004/b1 안의 오늘 추가 문장, s005/b12~b14, 라벨 R-3470·R-3483·R-3496·R-3497. 개정 Expression 이나 기존 규범 라벨은 건드리지 않았다(`TODAY_NEW` 가드).
- 계수: Norm/Work 3478 → 3508(+30) · Expression 3648 → 3695(+47 = 30 + 17) · Block 2920 → 2926(+6) · q4 3469 → 3499.

**Coordinator 정합**(M-1·M-2 외)
- 새 문장이 가리키는 곳은 모두 실재한다: Phase 0 2번·3~4번 · Phase 2 3번·6번·7번 · 수정 모드 2번 · 엣지 절 · 경계 절 실행 모드별 절차 · Phase 2 6번 «미룰 수 없음» 재상정(C:160) · HR §1 1번(HR:29).
- R-0309 새 문면은 R-0304(첫 파견 직전 기록) · R-0398(회전 중 재기록 금지) · C:175(재앵커는 발주자 결정 사안)와 양립한다.
- G2 차단 목록(R-0411)과 legacy 잔존 괄호(C:173)의 예외 관계를 문면에 적었다.
- 위임 제외 목록은 C:58 과 C:217 이 같다.

**Codex 미러**
- 바뀐 문장과 새 문장이 모두 대응 위치에 있다: CX:58(평문 fallback 한 줄) · 61 · 102~106 · 125 · 131 · 6번·7번·수정 모드·경계.
- 표기 차이는 정상 범위다: `request_user_input`/평문 · «네이티브 파일 읽기» · `dddjango-discipline-houserules`·`dddjango-discipline-reviewer`.
- 새 토큰 25종의 출현 수가 같다. 차이 +1 은 CX:58 fallback 줄 때문이다.
- `runtime_parity_check` 가 정합이다. houserules 두 런타임의 추가 문장은 동일하다.

**F4-20**(M-3 외)
- `_is_factory_call` 을 한 출처로 뽑았다. `list(repo…)`·`[r for r in repo…]`·`[repo.get(i) …]` 는 전파하지 않는다(실측).
- 새 good 픽스처(`import_orders`)는 tuple(genexpr) → 이름 → for 경로를 고정한다. bad_rules `close_orders` 는 순진 전파(시제품 A)를 red 로 잡는다.
- EXPECTED 변화는 그 한 키뿐이다: findings (2,15→16,2 · #195×1→×2 · 해시 3종) · baseline (2,15→16,15→16,3).
- 두 런타임 byte 미러와 `pregate_symbol_kinds.json` 재소성(`--check` in-sync)이 맞다.

**가이드**
- 요청 예시 블록과 가이드 전문에 내부 토큰(G0·G1·G2·ⓐ·ⓑ·슬라이스·refactor-scope·build_anchor·BC·registry·lens·Phase)이 0건이다.
- 약속과 런타임이 대응한다:
  - 작은 수정도 조사 · 규모 표시 · 동작이 바뀌는 위반은 따로 묻기 · 이어서/승인됨/폐기 · 조사·검사 축소 지시 금지 · 범위 축소는 미룸이 아님 · 정리할 것 없으면 첫 단계 정지 · 비위반 이동은 하지 않음 · 대리 답 표시 · 원문 없는 미룸 정지와 재질문 불응답 · 동시 작업 알림
  - 예외는 m-8·m-9·m-10 이다.
- Codex byte 미러가 같다. `request_guide_contract` 는 PASS 이고 self-test 는 157/157 이다.
- README G0 설명(README.md:137·155)과 충돌하지 않는다. 명세 §0 한 줄이 들어갔다.

## §4 verify 예측 (읽기 전용 개별 실행)

- **red 예상(봉인 재발행 전제)**: `verify-base-core` 의 두 줄이다.
  - `manifest_seal.py --check --draft` — 지적 26건. 전부 수정 파일·tree 드리프트다. 수정 목록 밖의 지적은 0이다.
  - `manifest_seal.py --self-test` — M0 «무변이 대조»가 같은 원인으로 실패한다.
  - 둘 다 `--write` 뒤 해소되는 성격이다.
- **그 밖의 red 예측: 없음.** 아래를 직접 실행해 모두 exit 0 을 확인했다.
  - verify-ontology 12단: gate 90/90 · meta-SHACL · SHACL full · hierarchy golden · golden 23 · gate-smoke 12 · ISSUED · LEDGER · render-sync 541 · structural(+self-test) · query-golden
  - base-core: corpus_mirror 11/11 · corpus_lint · spec_lint · checker_lint · tree_mirror · adapter_layout · reverse_coverage · fixture 104/104 · baseline 73/73 · findings_count 73/73 · findings_smoke · drift 8/8 · anchor_diff 14 · bounce ×2 · path_globs · rulepack `--check` · ab_score · scripts `diff -rq` · GUIDE `cmp` · request_guide ×2
  - cross: cross-matrix 347 · registry_gate_smoke 33 · bc_registry
  - backstop: api-error 714
  - regen: regen proto·smoke · runtime_parity · rulepack_smoke 14 · pregate_kinds · pregate_fixture · transcription · field_report ×2
  - `make verify-mutation`(rulepack 을 바꾼 커밋의 요구 · DEVELOPMENT.md:136) = 변이 11 전건 red 로 green 이다.
- M-3 을 수리하면 `bad_rules` 픽스처·EXPECTED 두 표·`pregate_symbol_kinds.json`·봉인을 다시 산출해야 한다(봉인은 마지막).
