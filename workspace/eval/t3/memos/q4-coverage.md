# T3 게이트 조항 — q4 무앵커 절 커버리지 공백 재평가

> 발주: T3 웨이브 4 조항 분석. 등재 경위 = 웨이브 1 병합 기록(`2026-08-18-ontology-adoption-log.md` 2026-08-22 ⓒ③ — 「q4=837은 무앵커 절 923 Work가 질의 스코프 밖임을 검산 — rulepack 커버리지 공백으로 웨이브 4 재평가 등재」). 그때의 923은 웨이브 1 시점 값이고, **이관 물량 종결(웨이브 3) 후 실측치는 1,707**이다.
> 실측 기준: HEAD 워킹트리 · `ontology/{rules,wiring,vocab}/*.ttl` 64파일 · 트리플 45,677 · `.venv` rdflib 7.6.0.

---

## 0. 판정 요지

| 물음 | 판정 |
|---|---|
| ① 공백 규모·성격 | **그래프 Work 3,400 중 1,707(50.2%)이 q4 밖.** 성격은 발주 전제(«(전문)·frontmatter·h1»)와 **다르다** — 그 셋은 75 Work(4.4%)뿐이고, 나머지 1,632(95.6%)는 **번호만 없는 평범한 h2/h3/h4 절**이다. 빠진 쪽은 무작위가 아니라 **agent 7문서 + command 1문서 전량(1,254 Work)** — 파이프라인이 실제로 실행하는 지시문서다. |
| ② 현 운용의 실해 | **오늘 시점 실해는 사실상 0.** 폐루프 기본 off · T2 A/B 종결(효과 주장 금지) · 정확 조인(tier 1)은 alias 3건뿐이고 **전부 앵커 절 소유**라 넓혀도 exact join은 1건도 늘지 않는다. 늘어나는 것은 tier 2 «후보»뿐인데, 주입문이 스스로 «후보를 근거로 다른 코드를 고치지 않는다»고 **행동을 금지한** 정보이고 이미 «7.04배 팽창»으로 결함 등재된 채널이다. |
| ②′ **예정된 실해** | **웨이브 4의 «alias 재검토(모노레포 538규칙)»가 이 공백을 실해로 전환시킨다.** 무앵커 Work에 alias를 달면 현행 생성기가 **침묵 탈락**시킨다 — 실증 완료(§3.3): `make verify` green · 그래프 SHACL green · alias 대장 검사 ⑥·⑥′·⑥″ green · 그런데 팩 `by_alias`에 그 alias가 없다. **RED 지적 0.** 이 저장소가 가장 일관되게 막아온 결함 유형(AS-07·AS-08 계열)이 정확히 팩 커버리지 축에 열려 있다. |
| ③ 처분 권고 | **① q4 개정으로 무앵커 전량 포함 — 즉시 실행.** 단 «주입 용량 상한»은 **분리 등재**(폐루프 off 인 동안 실해 0이므로 재개 결정 시 처리). ③ 부분 포함은 검토 결과 **전건 열등**(§4.3). |

---

## 1. 공백의 정확한 규모

### 1.1 원인 — q4의 단일 트리플 패턴

`workspace/tools/queries/q4-injection-order.rq`:

```sparql
  ?section djr:inDocument ?document ;
           djr:sectionNumber ?sectionNumber .     # ← OPTIONAL 이 아니다
```

`djr:sectionNumber`는 `ontology_migrate.py:148`이 `census["anchor"]`가 있을 때만 기입한다. 셰이프도 `SectionShape-sectionNumber`가 `sh:maxCount 1`뿐 **`minCount` 없음** — 무앵커 절은 정당한 형상이다. 따라서 앵커 없는 절의 블록·Work는 질의에서 **조용히 사라진다**. `?sectionNumber`는 SELECT 변수이자 `works.*.section_number`·`by_section.*.number`·정렬 키까지 겸하고 있어 한 곳의 필수 바인딩이 네 곳을 동시에 잠근다.

### 1.2 계수

| 축 | 앵커(팩 안) | 무앵커(팩 밖) | 계 |
|---|---:|---:|---:|
| Work | **1,693** | **1,707** | 3,400 |
| 블록 | 1,084 | 665 | 1,749 |
| 절 | 409 | 125 | 534 |

`rulepack.json` 실측 `works` = 1,693 · `by_section` = 409 — 위 표와 일치(팩 = q4 전량).

### 1.3 성격 — 발주 전제의 정정

무앵커 절 125개를 헤딩 스냅숏으로 분류:

| 절 유형 | 절 | Work | 비중 |
|---|---:|---:|---:|
| **h2 (번호 없음)** | 78 | **1,281** | 75.0% |
| **h3 (번호 없음)** | 11 | 271 | 15.9% |
| **h4 (번호 없음)** | 11 | 80 | 4.7% |
| frontmatter(`---`) | 19 | 60 | 3.5% |
| h1 | 6 | 15 | 0.9% |
| 계 | 125 | 1,707 | |

→ **발주 전제 «대부분 (전문)·frontmatter·h1»은 사실이 아니다.** frontmatter+h1은 75 Work(4.4%)뿐이다. 나머지 95.6%는 `## 입력` · `## 산출` · `## 경계` · `## 작업 방식 (안쪽 루프 TDD)` 같은 **규범을 정면으로 진술하는 절**이며, 번호가 없는 유일한 이유는 **원문 헤딩에 번호가 없기 때문**이다(byte 등가 규율상 원문 헤딩에 번호를 새로 심을 수 없다).

### 1.4 문서별 — 빠진 쪽의 편향

무앵커 Work 1,707의 소속:

| 문서군 | Work | 앵커 Work |
|---|---:|---:|
| `agents/*.md` 7문서 | 919 | **0** |
| `commands/dddjango.md` | 335 | **0** |
| `skills/*/SKILL.md` 10문서 | 309 | 0 (houserules만 예외 64) |
| `discipline-houserules/SKILL.md` | 11 | 64 |
| `*/references/final.md` 잔여 | 133 | 1,629 |

→ **참조성 `final.md`는 92.4%가 팩 안**이고, **실행 지시문서(agent·command·SKILL)는 100%가 팩 밖**이다. 팩은 「무엇을 참조할지」는 알고 「어떻게 일할지」는 모르는 색인이 되어 있다.

---

## 2. 배선 보유 — 공백이 실제로 무엇을 끊는가

| 배선 | 앵커 Work | 무앵커 Work |
|---|---:|---:|
| `djr:enforcedBy`(검사기) | 317 | **447** |
| `djr:delegatedTo`(에이전트) | 1,526 | 1,587 |
| `djr:aliasFor`(모노레포 #N) | **3** | **0** |

- **검사기 축**: 검사기 27종 **전부**가 무앵커 Work를 갖는다. 집행 대상 764 Work 중 **447(58.5%)이 팩 밖** — tier 2 후보 목록이 구조적으로 절반 이하다. 앵커 Work가 0인 검사기는 없으므로 «검사기가 통째로 tier 3로 떨어지는» 최악은 없다.
- **alias 축**: 무앵커 Work의 alias는 **0건**. 즉 **오늘 q4를 넓혀도 exact join은 1건도 늘지 않는다.** 이것이 §3.1 판정의 근거다.
- `by_path`(Q1)는 무영향 — 글롭 4건 전부 앵커 절 소유이고 q1도 `sectionNumber`를 요구하지만 `pathGlob`가 앵커 절에만 저작되어 있다.

무앵커·검사기 보유 Work 447의 소속 상위: `agents/discipline-reviewer.md` 116 · `agents/design-architect.md` 65 · `commands/dddjango.md` 58 · `agents/coder.md` 40 · `agents/design-review-api.md` 32.

---

## 3. 실해 판정

### 3.1 오늘 실해 없음 — 근거 4

1. **폐루프 기본 off.** `commands/dddjango.md:146` step 6′ = 「`DJR_LOOP_ENABLED=on` 일 때만 발화 · 기본값 off · off 면 이 절이 생기기 전과 문자 그대로 같다」. 팩을 읽는 유일한 코드 경로는 `regen_core.py:369` `if args.selector == "sparql"`이며, `--selector`는 **기본값이 없다**(미지정 = 중단). 사람이 두 스위치를 명시해야만 팩이 열린다.
2. **T2 A/B 종결.** 사용자 지시 «지금 즉시 전부 중단» · 유효 효과 측정 0건 · 효과 주장 금지. 팩 변경이 진행 중 실험을 오염시킬 경로가 없다.
3. **정확 조인 무영향.** tier 1 = `by_alias` 조회. alias 3건(`#3`→R-0124 · `#486`→R-0118 · `#488`→R-0120)은 전부 `architecture-ddd/references/final.md` §3.2 소유 = 앵커. `regen_core`가 «처치량 0(uninformative)»을 판정하는 유일한 지표 `exact_n`은 넓혀도 그대로다.
4. **넓히면 커지는 것은 이미 결함으로 등재된 채널.** `_RULES_NOTE`는 candidate를 「이번 위반이 아닐 수 있다 — candidate 를 근거로 다른 코드를 고치지 않는다」로 **행동 금지**한다. T2-4 사후 리뷰(AS-04·AS-09)가 후보 31건에서 «7.04배 팽창»을 결함으로 기록했다. §4.1 실측대로 무앵커를 넣으면 그 팽창이 **추가로 2.84배** 커진다.

### 3.2 그러나 공백 자체는 «표시 계약의 거짓»이다

- q4 헤더 주석: 「입력 없이 **전량 반환**이 계약이다 — 팩을 통째로 굽는 질의」. 이제 **거짓**이다(전량 3,400 중 1,693).
- 생성기 리포트: 「`[rulepack] Work 1693 · 검사기 27 · alias 3 · 절 409`」 + 「검사기 도달 불가 규범 1376건 — selector 진입로 없음(**침묵 탈락 금지**)」. 침묵 탈락을 막겠다고 선언한 바로 그 리포트가, **1,707 Work가 질의 단계에서 사라진 사실은 한 줄도 말하지 않는다.**
- 팩은 설치본에 동봉되는 유일한 기계 판독 «규범 색인»이다. 절반만 담고 있다는 표지가 어디에도 없다.

### 3.3 **예정된 실해 — alias 재검토가 이것을 발화시킨다** (실증)

무앵커 Work `R-2492`(`agents/coder.md` 소속·`enforcedBy` 보유)에 `rule#999` alias를 임시로 달고 현행 생성기를 돌린 결과:

```
[rulepack] Work 1693 · 검사기 27 · alias 3 · 절 409
[rulepack] 검사기 도달 불가 규범 1376건 — selector 진입로 없음(침묵 탈락 금지)
[rulepack] 재료 ttl 64개 · 본문(text) 미동봉 — 개정 8
[rulepack] 경로 글롭 4건(Q1 — 처치 밖 카탈로그)

by_alias   = {'#486':'R-0118', '#488':'R-0120', '#3':'R-0124'}
#999 수록? = False
RED 지적   = 없음
```

- 그래프는 정당하고(SHACL green), alias 대장 검사 ⑥ 함수성·⑥′ 해소 4조건·⑥″ 문법이 전부 통과하며, `make verify`도 green이다. **그런데 팩에는 없다.**
- `Rulepack._validate_refs()`는 `by_alias → works` 방향만 본다. **`AliasEntry → by_alias` 역방향 검사는 존재하지 않는다.**
- 귀결: 위반 레코드가 `rule="#999"`로 말해도 tier 1을 놓치고 tier 2/3으로 흘러간다. 이는 `regen_core`가 «처치량»으로 세는 **유일한 채널의 손실**이며, 로그에도 게이트에도 흔적이 없다.
- **웨이브 4에 «alias(모노레포 538규칙) 재검토»가 편성되어 있다.** 재검토 결과 alias가 agent·command 문서 Work로 하나라도 내려오는 순간 이 침묵 탈락이 실물이 된다. 지금은 latent이나 **다음 작업이 발화 스위치**다.

---

## 4. 처분 3택

### 4.1 ① q4 개정 — 무앵커 전량 포함

`?section djr:sectionNumber ?sectionNumber`를 `OPTIONAL`로 내리고 정렬 키를 절 IRI 서수로 옮긴다. 프로토타입 실측:

| 지표 | 현행 | 개정 후 | 배 |
|---|---:|---:|---:|
| `works` | 1,693 | **3,400** | 2.01 |
| `by_section` | 409 | 534 | 1.31 |
| `by_checker` 키 | 27 | 27 | 1.00 |
| `by_alias` | 3 | 3 | 1.00 |
| 팩 bytes | 1,141,402 | **2,178,560** | 1.91 |
| fail-closed 지적 | 0 | **0** | — |
| 생성기 실행 | 2.0s | ~3.0s | — |

**계약 위험 3종 전건 통과(실측)**:
- 「한 Work = 한 블록」— 2블록 이상 진술 Work = **0건**(앵커·무앵커·전량 모두). 생성기 fail-closed가 물지 않는다.
- `skos:prefLabel` — 결손 0 · 복수 0. 행 곱셈 없음(3,400행 = 고유 Work 3,400).
- U+001F 혼입 — 질의 전 원 그래프 검사에서 0.

**정렬 키 이전이 무손실임을 실증**: 절 IRI 말단(`s005-1.2`·`s001`)의 서수 `NNN`으로 정렬 키를 바꿨을 때, 기존 1,693 Work의 **상대 순서가 완전히 보존된다**(`(document, sNNN, block_order, wid)` 정렬 == 현행 `order_rank` 정렬 — 불일치 0건). 서수는 등장 순 채번이므로 앵커 유무와 무관한 **총 순서**를 준다. 개정 후 무앵커 Work가 사이사이 끼어들어 `order_rank` 절대값은 전부 바뀌지만, 기존 Work끼리의 순서는 그대로다.

**비용 — tier 2 주입 팽창**(검사기 축 후보 전량을 `<rules>`로 실었을 때의 payload bytes):

| 검사기 | 현행 n / bytes | 개정 후 n / bytes | 배 |
|---|---:|---:|---:|
| check-api-error-controller-contract | 56 / 7,909 | **145 / 22,625** | 2.86 |
| check-layer-skeleton | 38 / 5,747 | 91 / 14,166 | 2.46 |
| check-error-centralization | 21 / 2,838 | 87 / 13,697 | 4.83 |
| check-context-isolation | 27 / 3,717 | 76 / 11,502 | 3.09 |
| check-app-container | 2 / 255 | 17 / 2,647 | **10.38** |
| check-transient-overmapping | 1 / 171 | 12 / 1,770 | **10.35** |
| **27종 합계** | — / **50,854** | — / **144,529** | **2.84** |

부수 효과: tier 2의 `order_rank`는 «그 검사기가 집행하는 Work들의 최소값»이라, 문서명 정렬상 앞서는 `agents/*`·`commands/*` Work가 들어오면 **대부분 검사기의 min rank가 agent 문서로 이동**한다 → C암 위반 배열 순서가 바뀐다. 폐루프 off·실험 종결이라 회귀 위험은 없으나 «달라진다»는 사실은 기록 대상이다.

배포 비용: `dddjango/scripts` 4.6M → 5.6M · 플러그인 페이로드 5.6M → 6.6M(+18.5%), codex 미러 동일 → 배포물 총 **+2.07MB**.

### 4.2 ② 현상 유지 + 문서화

q4·생성기를 손대지 않고 ⓐ q4 헤더의 «전량 반환» 문면을 «앵커 절 한정»으로 정정 ⓑ 생성기 리포트에 «무앵커 절 125 · Work 1,707 질의 밖» 한 줄 추가 ⓒ 블루프린트/조감도에 커버리지 한계 등재.

- 장점: 비용 0. 주입 팽창 0. 설치본 재릴리즈 불필요.
- 치명 결함: **§3.3의 alias 침묵 탈락을 그대로 둔다.** 문서화는 사람에게 말할 뿐 기계를 막지 않는다. 웨이브 4의 alias 재검토가 바로 다음 작업이므로, 이 선택은 「발화 예정인 결함을 알면서 남기는」 처분이 된다.
- 이 저장소의 확립된 규율(«막지 못하면 세지 않는다» · fail-closed 우선 · AS-07 「손상 팩과 정상 미등록 조회를 구분한다」)과 정면으로 어긋난다.

### 4.3 ③ 부분 포함 — 검토 결과 전건 열등

검토한 세 변종:

| 변종 | 내용 | 판정 |
|---|---|---|
| **P-a** | 무앵커 중 `enforcedBy` 보유 447만 포함 | **열등.** 주입 팽창은 ①과 **완전히 동일**하다(팽창의 원천이 정확히 그 447이다). 얻는 것은 팩 크기 절약뿐인데, 색인은 여전히 불완전하고 alias 침묵 탈락도 **그대로**다(alias는 `enforcedBy`와 독립). |
| **P-b** | `works`·`by_section`은 전량, `by_checker`만 앵커 한정 | **열등.** 주입은 안 늘지만 `by_checker`가 「그 검사기가 집행하는 Work」라는 이름과 다른 것을 담게 된다 — 침묵 탈락을 색인 안으로 옮겨 심는 것이다. 선별 기준 「앵커가 있는가」는 규범적 의미가 전혀 없다. |
| **P-c** | 전량 포함 + `regen_core`에서 tier 2 후보 상한 K | **①의 상위집합.** 색인 완전성과 주입 용량은 **다른 층의 문제**다(전자는 팩, 후자는 selector). 상한은 주입 계약(동결 개정 8 범위)을 건드리므로 **별건 승인**이 맞고, 폐루프가 off인 지금 급하지 않다. → **①을 먼저 하고 상한은 분리 등재**가 P-c의 올바른 시제다. |

**기각한 대안 하나 더**: 무앵커 절에 합성 `sectionNumber`(예: `"s001"`)를 부여해 앵커화. **기각** — `djr:sectionNumber`는 원문 헤딩의 절 번호라는 뜻이고, 합성값을 넣으면 ⓐ 그래프에 거짓 진술이 들어가고 ⓑ q3이 그 합성값을 진짜 주소처럼 받아 «§s001 절 묶음»을 반환하며 ⓒ LEDGER `section_key`·센서스 좌표와 이중 정본이 된다.

---

## 5. 권고

**① 전량 포함으로 q4를 개정한다. 웨이브 4의 alias 재검토와 같은 커밋 묶음에 넣고, tier 2 주입 상한은 별건으로 분리 등재한다.**

근거 순서:
1. 커버리지 공백 자체는 오늘 실해가 거의 없다(§3.1) — 그래서 **급하지 않다**는 결론이 아니라, **지금이 값싸게 닫을 수 있는 유일한 창**이라는 결론이 나온다. 폐루프가 off이고 실험이 종결됐으므로 `order_rank` 재배열·주입 팽창의 회귀 위험이 0이다. 루프를 다시 켠 뒤에 넓히면 그때는 처치가 바뀐다.
2. **alias 재검토가 바로 다음 작업이고, 그것이 이 공백을 tier 1 손실로 전환시킨다**(§3.3 실증). 순서를 뒤집어 alias부터 하면 침묵 탈락을 기계가 못 잡는 상태로 진입한다.
3. 개정의 기계적 위험이 **실측으로 0**이다 — fail-closed 지적 0 · 1 Work = 1 블록 유지 · prefLabel 곱셈 0 · 기존 1,693 Work 상대 순서 완전 보존 · 하네스 14단언의 고정점(G1 검사기 27 · G3d `#3`→R-0124 · G5 R-0122)이 전부 앵커 소유라 불변.
4. 웨이브 4가 이미 rulepack 재소성 · manifest 재봉인 · **릴리즈 2.17.0 검토**(`rulepack.json`이 설치본 계약)를 예정하고 있다. 개정 비용의 대부분(재소성·재봉인·재릴리즈)이 **이미 지불 예정**이다. 별도로 하면 그 비용을 두 번 낸다.
5. 「팩은 그래프의 렌더 투영물」(E1 계열)이라는 규율상, 투영물이 원본의 절반만 담으면서 그 사실을 말하지 않는 상태가 정상일 수 없다.

**동시에 요구하는 것 — 재발 방지 검사 1건 신설**: `ontology_rulepack.build()`에 「그래프의 `djr:AliasEntry` 전량이 `by_alias`에 실렸는가」 fail-closed 검사를 추가한다. 이번 공백이 눈에 띄지 않은 이유가 정확히 «역방향 검사 부재»이고(§3.3), q4를 넓혀도 다른 축(예: 향후 신설 절 유형)에서 같은 형태가 재발할 수 있다. 이 검사는 §4.2를 택하더라도 **무조건 필요**하다.

**보류(별건 등재)**: tier 2 후보 상한. 폐루프 재개를 결정하는 시점에 ⓐ 상한 K ⓑ 후보 표시 방식 ⓒ `<rules>` 계약(동결 개정 8) 범위를 함께 심의한다. 지금 결정할 재료(주입 효과 측정치)가 존재하지 않는다 — T2가 유효 효과 측정 0건으로 종결했기 때문이다.

---

## 6. 개정 명세 — rulepack 계약 영향 범위

> 팩은 **설치본 계약**이다(양 런타임 미러 · `make verify`의 `diff -rq`가 강제 · manifest `packs` 그룹 봉인 대상). 아래는 전 영향 지점.

### 6.1 질의 (1파일 1지점)

`workspace/tools/queries/q4-injection-order.rq`

```sparql
-  ?section djr:inDocument ?document ;
-           djr:sectionNumber ?sectionNumber .
+  ?section djr:inDocument ?document .
+  OPTIONAL { ?section djr:sectionNumber ?sectionNumber }
```

헤더 주석 동반 정정 2곳: ⓐ 「전량 반환이 계약」의 «전량»이 이제 진짜 전량임을 명기 ⓑ 「`?sectionNumber`는 문자열이라 ORDER BY는 사전순」 주석 — 정렬 소유가 절 IRI 서수로 이동했음을 반영.

**q1·q3은 손대지 않는다.** q1은 `pathGlob` 보유 절만 대상이고 글롭은 앵커 절에만 저작된다. q3은 `$SECTION_NUMBER`가 곧 주소라서 무앵커 절은 애초에 질의 대상이 될 수 없다(주소 없음). 두 질의의 골든도 불변이어야 한다 — 변하면 그것이 red다.

### 6.2 생성기 `workspace/tools/ontology_rulepack.py` (4지점)

| # | 지점 | 개정 |
|---|---|---|
| 1 | `_natural()` 사용처(L144 `ordered.append`) | 정렬 키를 `_natural(sectionNumber)` → **절 IRI 말단 서수** `sNNN` 기반 키로. `(document, section_ordinal, block_order, wid)`. 실측상 기존 순서 완전 보존(§4.1). `_natural`은 남겨도 되나 사용처가 사라지면 제거. |
| 2 | L136 `"section_number": str(r.sectionNumber)` | `str(...) if r.sectionNumber is not None else None` |
| 3 | L166 `by_section[...]["number"]` | 동일하게 `None` 허용 |
| 4 | `report` 행(L197~) | 「무앵커 절 125 · Work 1,707 포함」 계수를 **명시**. 침묵 확대 금지 — 커버리지 축 계수를 리포트가 소유하게 한다. |
| 5 **(신설)** | `build()` 말미 | `AliasEntry` 전량 ⊆ `by_alias` fail-closed 검사(§5 재발 방지). 미수록 시 `problems`에 적재 → exit 2. |

### 6.3 스키마 버전 — `rulepack/1` 유지 판단

변경되는 필드는 `works.*.section_number`와 `by_section.*.number`의 값 공간이 `string` → `string | null`로 넓어지는 것뿐이다.

- **저장소 전 코드에서 두 필드를 읽는 소비자는 0건**이다(`grep section_number` 결과: 생성기 자신 · `derive_path_globs.py`의 **TSV 열 이름**(무관) · `query_golden_check.py`의 **q3 파라미터**(무관)). `dddjango/scripts/rulepack.py`는 `works`에서 `order_rank`·`label`·`aliases`·`checkers`만, `by_section`에서 `works`만 읽는다.
- 따라서 **런타임 조회 모듈 코드 변경 0**이고 `rulepack/1` 유지가 합리적이다. 승격하면 `SCHEMA` 상수 + 양 미러 + 설치본 재릴리즈가 «스키마 때문에» 강제된다 — 실질 없는 비용.
- 다만 «값 공간이 넓어졌다」는 사실은 `rulepack.py` docstring과 T2-4 설계 정본(`2026-08-20-ontology-t2-4-design.md` §스키마)에 기입한다. **최종 판단은 사용자 몫**으로 남긴다(설치본 계약 변경이므로).

### 6.4 골든·하네스 — 갱신 대상과 불변 대상

| 자산 | 처분 |
|---|---|
| `workspace/eval/fixtures/rulepack/query-golden.json` | **갱신.** `q4.rows`·`q4.distinct_works` 1693 → **3400**. `q4.with_alias`(R-0118·R-0120·R-0124)·`q1`·`q3:3.2`·`q3:6.1`·`q2:*`·`adapter`는 **불변이어야 한다** — 변하면 red. `query_golden_check.py --emit` 후 diff를 눈으로 확인. |
| `workspace/tools/rulepack_smoke.py` 14단언 | **불변 예상.** G1(검사기 키 ⊆ 로스터 — 27종 유지) · G3d(`#3`→R-0124 단건 — tier 1 경로는 alias만 보므로 무영향) · G5(R-0122 명칭 꺾쇠 — 앵커 §3.2 소유) · G9(순열 불변) 전부 앵커 고정점. **`--mutation-test` 11변이 재실행 필수**(`make verify-mutation`). |
| `workspace/tools/firing_probe.py` | **일시 red 예상** — 설치 cache의 `rulepack.json` 해시가 source와 어긋난다. **2.17.0 재릴리즈로만 해소**(이미 예정). 개발 중에는 `ALLOW_STALE=1`. |
| `workspace/eval/ab/T2-0b-manifest.json` | **재봉인.** `packs` 그룹(`rulepack.json` ×2) + `graph` 그룹 해시. 병합 판형에 `manifest_seal.py --seal` 단계가 이미 있다(annex는 HEAD 보존 병합). |
| SHACL·구조 검사·`ontology_gate` | **무영향.** `sectionNumber`는 `maxCount 1`만 걸려 있고 구조 검사 7종 중 이 축을 보는 것이 없다. |
| `workspace/eval/fixtures/ontology_gate/target-counts.json` | **무영향**(질의가 아니라 게이트 계수). |

### 6.5 산출물·미러

- `dddjango/scripts/rulepack.json` (1,141,402 B → 2,178,560 B)
- `codex-dddjango/skills/dddjango/scripts/rulepack.json` (동일 — 생성기가 양쪽에 쓴다. `make verify`의 `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts`가 강제)
- 재생성 = `make rulepack`, 대조 = `ontology_rulepack.py --check`(verify-base 상시)

### 6.6 소비층 — 실행 시 무엇이 달라지는가

| 소비자 | 변화 |
|---|---|
| `Rulepack.locate()` tier 1 | **불변.** alias 3건 전부 앵커 소유. |
| `Rulepack.locate()` tier 2 | 후보 **평균 3.34배** · 최악 56 → **145건**. `order_rank`(=min)이 대부분 검사기에서 agent 문서 Work로 이동 → **위반 배열 순서 변화**. |
| `regen_core.select_graph()` | tier 3 폴백 대상 감소(팩 밖 Work가 줄어든다). `exact_n`·`uninformative` 판정 **불변**. |
| `<rules>` 주입 payload | 27종 합계 50,854 B → **144,529 B**(2.84배). 실제 주입은 발화 검사기 1종분이므로 회전당 최악 22.6 KB. |
| `Rulepack.norms_for_path()` (Q1) | **불변**(글롭 4건·앵커 절 소유). |
| `Rulepack._validate_refs()` | **불변** — 참조 무결성은 works 집합 안에서 닫히므로 확대에 안전. |
| 배포 페이로드 | 플러그인 5.6M → 6.6M(+18.5%), 미러 포함 **+2.07MB**. |

---

## 7. 검산 재현

```bash
# 앵커/무앵커 계수
.venv/bin/python - <<'PY'
from pathlib import Path; from rdflib import Graph
g=Graph()
for sub in ("rules","wiring","vocab"):
    for f in sorted((Path("ontology")/sub).glob("*.ttl")): g.parse(f, format="turtle")
for lbl,c in (("anchored","FILTER(BOUND(?sn))"),("unanchored","FILTER(!BOUND(?sn))")):
    q=f"""PREFIX djr: <https://numchida.com/ns/djr#>
    SELECT (COUNT(DISTINCT ?w) AS ?w_) (COUNT(DISTINCT ?b) AS ?b_) (COUNT(DISTINCT ?s) AS ?s_)
    WHERE {{ ?b djr:statesNorm ?w ; djr:inSection ?s . OPTIONAL {{ ?s djr:sectionNumber ?sn }} {c} }}"""
    for r in g.query(q): print(lbl, "Work", int(r.w_), "블록", int(r.b_), "절", int(r.s_))
PY
# 현행 팩 계수 대조
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_rulepack.py --check
# 질의 골든
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/query_golden_check.py
```

기대: `anchored Work 1693 / 블록 1084 / 절 409` · `unanchored Work 1707 / 블록 665 / 절 125` · 팩 리포트 `Work 1693 · 검사기 27 · alias 3 · 절 409` · 골든 `q4.rows = 1693`.

---

## 8. 사용자 확인이 필요한 지점

1. **q4 전량 포함 개정 승인** — 설치본 계약(`rulepack.json`) 변경이며 2.17.0 릴리즈에 실린다.
2. **스키마 버전 유지 여부** — `rulepack/1` 유지 권고(§6.3). 승격을 원하면 `rulepack.py` SCHEMA + 양 미러 동반.
3. **tier 2 주입 상한 분리 등재 동의** — 폐루프 재개 결정 시 심의(지금 결정할 측정 재료 없음).
