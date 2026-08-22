# 적대 리뷰 — T3 마감 처분 메모 «hash-n-alias» (2026-08-22)

> 대상: `workspace/eval/t3/memos/hash-n-alias.md` · 판정: **apply_with_fixes** (blocker 3 · caution 8)
> 방법: 판정표 §3 등재 20건 **전수** 실독 대조(원장 538행 ↔ `ontology/rules/discipline-houserules-final.ttl`
> prefLabel·블록 `djr:text`) + 처분 전체를 임시 트리(`/tmp/alias-sim`)에 **실적용·실행 재현**
> (gate 4단 · structural ⑥·⑥′·⑥″ · hierarchy 계수 · violation_adapter 조인 · query 골든 대조).

---

## 0. 재현 요약 — 무엇이 green 이고 무엇이 red 인가

임시 트리에 §6-1 그대로 21엔트리 `aliases.ttl` 을 써서 실행한 결과:

| 단계 | 결과 |
|---|---|
| `ontology_gate.py` 전 ttl (4단) | **green** (exit 0 — 단, 수기 숫자순 파일은 2-canon red → `--write` 선행 필수, §6-6 순서대로면 무해) |
| `ontology_structural_check.py --root` ⑥·⑥′·⑥″ | **green** — «alias 대장 21건 · 해소 Work 21종 … 전부 성립» |
| `ontology_hierarchy_check.py --with-golden --emit` | **AliasEntryShape = 23** 정확(§6-2 예측 일치) · 타 셰이프 계수 전부 무변 |
| `violation_adapter` 조인(#488 레코드) | **R-3181 로 실조인**(joined=1) — 재귀속 자체는 기계적으로 성립 |
| **query 골든 대조([11/11])** | **RED 3항** — blocker B1 |
| `violation_adapter --self-test` | **실패(exit 2)** — blocker B2 |

**판정표는 살아남았다**: §3.1 등재 20건 전수(아래 §1)·유지 1건·취소 1건·재귀속 1건 모두 문면 검증 통과.
깨지는 것은 전부 **§6 저작 사양의 부속 절차**이고, 각각 소규모 수정으로 닫힌다.

---

## 1. 판정표 §3.1 전수 대조 — 20/20 통과 (표본 아님)

원장(`workspace/design/2026-08-08-tree-revision-spec.md` 538행) ↔ Work prefLabel ↔ 블록 `djr:text` 3중 대조.

- #10→R-3196 · #20→R-3208 · #21→R-3209 · #58→R-3210 · #72→R-3230 · #74→R-3229 · #82→R-3195 ·
  #88→R-3200 · #89→R-3201 · #92→R-3206 · #178→R-3207 · #187→R-3211 · #314→R-3212 · #430→R-3218 ·
  #432→R-3219 · #436→R-3220 · #487→R-3178 · #488→R-3181 · #489→R-3182 · #491→R-3186 — **전건 주어·양상·술어 일치**,
  등급(Obligation/Prohibition/Exception) 표기도 TTL 클래스와 전건 일치. 대상 전건 `discipline-houserules-final` 소재 확인.
- 유지 `#3`→R-0124: 정본 final.md 에 «관문» 문자열 0건(전수 grep) — «경쟁 Work 0» 주장 확인.
- 취소 `#486`: 원장 812행이 실제 2문(«골격 그대로» + «반환»)이고 T3 블록(s003-0/b2)이 R-3179/R-3180 으로
  원자 분리한 것 확인 — v2 의 #119(→R-0075/R-0076) 처분과 동형이라는 주장 성립.
- 재귀속 `#488`: R-3181 문면·클래스 일치, 어댑터 실조인 확인(§0).
- 계수 재현: Work 3,400(ISSUED 일치) · 라벨 #N 담지 **151건·인용 173회**(메모 §1.1 수치와 정확 일치) ·
  `#337` 라벨 부재(구간 중간항 침묵 탈락) 재확인 · `slot#N` 0건 재확인 · rule-owner-map 538행에 관련 #N 전건 실재
  (⑥″ 원장 대조 green 예상 확인) · 의사결정 #1~#7 Work 7종 실재 · R-2720 블록의 «(#453·#454)» 동시 인용+OHS 스코프 한정 실재.
- §3.3 합성 분해(R-3193/94 · R-3202/03 · R-3204/05 · R-3216/17 · R-3183/84/85 · R-3197/98/99 · R-1728/29) 전건 실재·문면 부합.
- §3.6 50종: agent-discipline-reviewer 라벨 #N 과 대조 — 메모 50종 전건 실재(라벨 공간에 #82·#492·#628 도 있으나
  메모가 타 절에서 처분함 — 계상 충돌 없음).

---

## 2. Blockers

### B1 — verify red: `make verify-ontology` [11/11] query 골든 3항 불일치 (§6-6 누락)

- **증거**: `workspace/eval/fixtures/rulepack/query-golden.json` 이 alias 의존 값을 고정한다 —
  `"q2:exp-A": ["R-0120×1","R-0124×1"]` · `"q2:exp-B": ["R-0120×1"]` · `"q4":{"with_alias":["R-0118","R-0120","R-0124"]}`.
  `query_golden_check.py`(observe)는 rule="#3"/"#488" 합성 레코드를 **실물 대장으로** 어댑터에 태워 Q2 를 재고,
  Q4 의 with_alias 를 실물 그래프에서 잰다. 시뮬레이션 실측: exp-A → `R-0124×1·R-3181×1`, exp-B → `R-3181×1`,
  q4.with_alias → `[R-0124, R-3178, R-3181, R-3182, R-3186]`(5종). **3항 전부 골든과 불일치 → [11/11] RED.**
- 메모 §6-6 의 게이트 목록은 «verify-ontology 10/10»으로 끝난다 — 이 체인은 현재 [0/10]~[11/11] 12단계이고
  (Makefile 21~48행), 누락된 [11/11] 이 정확히 red 나는 자리다.
- **수정안**: §6 에 `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/query_golden_check.py --emit`
  재기록 + diff 검수(기대 diff: q2 두 런 R-0120→R-3181 · q4.with_alias 3→**5종**)를 추가. 이 재기록은 #488→R-3181
  조인을 어댑터로 실제 태우므로 **§6-5 재실증의 기계 부분을 겸한다**(별도 픽스처 런 불요).

### B2 — 재실증 하네스 자체가 깨짐: `violation_adapter.py --self-test` 의 R-0120 하드코딩

- **증거**: `workspace/tools/violation_adapter.py:170` `ok_work = "R-0120" in ttl …` — #488 재귀속 후 self-test 는
  조인엔 성공하고 단언에서 실패한다(exit 2 · 시뮬레이션 실증: joined=1, "R-0120" in ttl == False, R-3181 실재).
  §6-5 의 «같은 검사기이므로 경로 변경 없음»은 하네스 층에서 거짓 — 재실증을 명한 바로 그 절차가 red 를 낸다.
  (verify 체인에는 미편입이라 [n/11] red 는 아니나, §6-5 이행이 이 도구로 막힌다.)
- **수정안**: self_test 의 기대 Work 를 R-3181 로 갱신(또는 대장에서 `alias.get("#488")` 로 파생시켜 하드코딩 제거 —
  후자가 재발 방지형). 174행의 «R-0120 왕복» 출력 문자열도 함께.

### B3 — §6-3 docstring 사양의 내부 모순·소유 모순 (의미 오류가 파일에 박힘)

- **(a) 계정이 안 닫힌다**: 27검사기 = layer-skeleton(1) + context-isolation(1) + «나머지 21종(#74)» + 없음 3 = **26**.
  1개(check-composition-root)가 무배정인데, 메모 자신의 §3.1 #488 행이 composition-root 를 발화 검사기로 명기한다.
  «확정 24종/없음 3종»은 이대로는 도달 불가(23종이 되거나 composition-root 에 rule#488 행이 필요).
  같은 논리로 db-table·test-config(#488 발화)·usecase-dto(#92 발화)에 rule#74 하나만 주는 것은 메모 자신의 집행 열과 모순.
- **(b) #74 의 «조인 실값 경로» 전제가 거짓**: 23검사기의 #74 발화는 전건 가드 **메시지 문면**이고, 가드 레코드는
  `rule=null+sentinel(«대상0»)` 이다(`findings.py:330-337`). 어댑터는 자기 계약으로 이를 적재하지 않는다
  (`violation_adapter.py` 머리말 «가드 센티널은 … 노드를 만들 수 없다» — 시뮬레이션에서도 sentinel 집계로만 잡힘).
  `rule="#74"` 레코드를 실발화하는 유일한 도구는 `workspace/tools/checker_lint.py`(f.add("#74",…) — rule-owner-map
  69행이 지정한 소유자)다. 게다가 21종 안의 2개 파일은 명시 결정 주석을 이미 갖고 있다 —
  `check-api-error-controller-contract.py:7040` · `check-error-centralization.py:4753` «#74 는 달지 않는다(소유자
  checker_lint — rule-owner-map)». §6-3 을 문면대로 적용하면 이 결정과 모순되는 «조인 확정» 행이 21파일에 박힌다.
- **수정안**: ① composition-root·db-table·test-config 에 `rule#488 → djr:R-3181`, usecase-dto 에 `rule#92 → djr:R-3206`
  행 배정(메모 자신의 집행 열대로) ② «달지 않는다» 결정을 가진 2파일은 rule#74 행 제외(«없음» 유지)하거나
  #74 행을 checker_lint 쪽에 두는 것으로 소유를 일치 ③ «확정 N종/없음 M종» 수치를 재계산해 명기.
  (docstring 을 기계 대조하는 검사는 없음을 확인 — verify red 는 아니고 의미 오류 등급.)

---

## 3. Cautions

1. **«verify-ontology 10/10» 표기가 낡았다** — 현행 체인은 [0/10]~[11/11]. B1 이 숨은 자리가 바로 이 표기 착오다.
2. **조건 A·B 는 이미 충족돼 있다** — #82: `s011-3/b1` 이 `restates s006/b2`(R-3195 블록)를 이미 가짐 ·
   #487: SKILL `s004-1/b2` 가 `restates final s003-0/b1`(R-3178 블록)을 이미 가짐. «소급 재진술 패스에서 확정된 뒤»라는
   선행 조건은 현재 그래프에서 이미 성립 — 2엔트리를 미룰 근거가 없고, 21엔트리 일괄 기입과 계수 23 이 정합한다.
   #492 도 동형(`s002/b2 restates s003-0/b7` 실재) — 보류의 잔여 쟁점은 «정체성 확정» 인간 판단뿐이며, 메모 자신의
   기준(전문 진술 단일 Work·같은 정본 문서)으로는 `rule#492 → R-3177` 등재가 가능하다. 보류 유지는 안전하나
   근거 문구(«묶고 … 한 뒤»)는 낡은 전제다.
3. **정량 효과 서술의 과장** — «#74 단독 23검사기(85%) 뒤집기»·«발화 커버리지 2/27→24/27»는 문면 발화 기준이다.
   등재로 새로 생기는 **레코드 키 실조인 경로는 #58·#314(layer-skeleton) 둘 + #488(유지·재귀속)뿐**이고, 나머지 18종의
   #N 은 어떤 검사기도 레코드 키로 내지 않는다(#10 은 layer-skeleton 26행이 «Phase 3 편입분»으로 미구현 예고까지 함).
   §3.1 의 «집행 열 = violatesWork 조인의 실값 경로» 각주는 이 구분 없이 쓰였다 — T2-2 §5 의 «후보 발견률 ↔ 확정 조인률»
   수치 정명(AL-9) 규율을 이 메모가 자기 수치에는 적용하지 않았다.
4. **골든 재기록 후 q4.with_alias 는 21이 아니라 5종** — q4 스코프에 드는 alias 대상은
   R-0124·R-3178·R-3181·R-3182·R-3186 뿐. 재기록 diff 검수 때 «21이 아닌 것»을 결함으로 오판하지 말 것.
5. **§4.1 registry «27종 전부 1:1·함수성 성립»은 매끈하지 않다** — command-dddjango 에는 정체성 Work 외에 인용형
   라벨 Work 가 더 있다(«registry #2 에 … 추가» 1542행 · «registry #16 에 …» 1582행 · «registry #6 은 …» 1902행).
   조건 ②(⑥″ 확장) 시행 시 rule 공간과 같은 정체성↔인용 판별 패스가 선행돼야 한다.
6. **자인 ⓑ는 해소 가능** — 23건 전수 grep 결과 전건이 동일 판형의 가드 blocker 메시지 발화였다(구현 메모 아님).
   «규범 인용» 판정 자체는 옳다. 문제는 인용 여부가 아니라 레코드 경로(§2 B3-b)다.
7. **자인 ⓒ(재실증)는 B1+B2 수정으로 자동 이행** — 골든 재기록이 #488→R-3181 조인을 end-to-end 로 태우고,
   self-test 갱신이 그 단언을 상시화한다. 별도 재실증 런은 불요.
8. **적용 마무리 시 조감도 갱신** — 상시 지침대로 `workspace/design/ontology-adoption-map.html` 에 alias 대장
   3→21 확장·#486 취소·#488 재귀속을 반영할 것(이 리뷰 자체는 정본 무변이라 미갱신).

---

## 4. 판정

**apply_with_fixes.** 판정표(§2~§4)와 «무접두 #N 편입 기각 + 조건 3»(§5)은 전수 검증을 통과했고 시뮬레이션에서
대장·게이트·계수 전 단계 green 이다. 그러나 §6 을 문면대로 적용하면 ① [11/11] query 골든 RED(B1) ②
재실증 하네스 exit 2(B2) ③ 21+파일 docstring 에 자기모순 기록(B3)이 남는다. 세 수정 모두 소규모·국소적이며
판정표 재작업을 요구하지 않는다.
