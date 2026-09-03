# 수리 배치 3 · 1단계 적대 리뷰 B — 후보 N-1 (filtered 근거 유형 닫기)

- 대상 주장: pre-gate 처분 라벨 `filtered`의 근거 «유형»이 닫혀 있지 않아 규범 해석 사유가 filtered로 기재될 수 있고, 진탐이 버려져 ③형이 재발한다(reading #188 `57a4705e1218`).
- 리뷰 방식: 1차 자료 원문 재구성(reading pregate-report 44회 · STOP-149 · 최종 트리 · 검사기 코드) → 현행 규범 문면 대조 → 처방 P1~P3 무손실 판정. 저장소 파일 무수정.
- 도구: Serena/graphify 미opt-in(표식 부재) — 기본 도구.

## 1. 항목별 판정 표

| 항목 | 판정 | 한 줄 근거 |
|---|---|---|
| ⓐ(1) 타임라인 재현 | **검증됨**(정정 3건) | 44회 전건 재구성 — #188은 run 2(09-02 08:43 KST)~run 29(20:30 KST) 26회 red 지속·명시 filtered 13회, STOP-149 21:50 → 승인 21:59(지침 8 = 접기) → G1′ 마감 00:07 → run 31부터 소멸(⓪의 «run 30»은 형식 red 회차). run 2는 원 G1(09-01 03:44)이 아니라 D54 amendment 최종본이다 |
| ⓐ(2) 현행 정의 부합 | **MAJOR** — «규범 미준수 + 잔여 공백»이나 N-1의 처방(유형 닫기)은 이 사례를 막지 못한다 | #188 술어는 순수 트리 차집합(검사기 :302-307)·file-plan 투영이 정확 → «도구 한계» 속(genus) 밖 = rev3 문면상 미준수. 단 레인은 rev1(v2.17.14 — 정의 자체 부재) 하에서 돌았고, rev3 하에서도 «선례: OHS-only 4영역 통과 · 실코드: P3 트리 #188 exit 0»으로 **형식상 적법한** 근거를 달 수 있다 — P1의 3유형 중 2개가 그대로 뚫린다 |
| ⓐ(3) 레인 2·3 동계열 여부 | **MAJOR**(과대 계수) | 레인 2·3은 rev1 하 라벨 «집합» 혼동(ignored↔filtered 맞바꿈·신조 라벨)이며 전건 무해·rev2로 종결. N-1은 «구조 규칙 진탐에 대한 허위 도구-한계 주장» — 다른 계열. 실 레인 수 1 → ⓪ 자체 필터(≥2 레인) 미달 |
| ⓐ(4) rev2 이후 재발 | **MAJOR**(현행 규범 하 발화 0) | 카탈로그 레인: v2.17.16 1회 실행(03:59Z)·예보 1건(#392 factory_boy)·처분 미기재(43행·mtime 12:59 KST). rev2+ 하 N-1 계열 관측 0건 — «실전 발화 시» 원칙 위배 |
| ⓑ P1 닫힌 근거 유형 | **MAJOR**(오차단 위험 + 표적 미차단) | 정당 filtered 매핑: #107→사각 목록 ✓ · #493→실코드 exit 0 ✓ · #593→사각 목록(정형 보충) ✓ · **#392·#160/#484 → 사각 목록 부재**(선례 의존 — 첫 BC 프로젝트면 오차단). 표적 #188은 선례·실코드 경로로 통과 |
| ⓑ P2 discipline-reviewer 항목 추가 | **BLOCKER** | 리뷰어는 리뷰 다발과 병렬(첫 pre-gate와 동시) 호출·처분은 «명세 개정 승인마다» Coordinator가 사후 append(R-3433) → 감사 시점에 처분이 존재하지 않음. pregate-report는 코디네이터 소유(dddjango.md:28) — 역할 경계 침범 + 문서 키 1개 추가 개정 |
| ⓑ P3 승격 시 자연 소멸 | **주장 반증·행위는 타당** | R-3436 rev2가 폐지하는 것은 «구형 명세 skip»뿐. R-1(권고→반송 의무)에서 filtered는 도구-한계 유일 우회로로 존속(#392 등 R-5 잔존이 있어 폐지 불가) → 허위 filtered = 게이트 우회. 우려는 승격 시 **커진다**. 그러나 «지금 아무것도 안 함»은 옳다 — 정위치가 R-1의 R-3433 개정이기 때문 |
| ⓒ 효과 과대 | **MAJOR** | #188 = 149건 중 1·8범주 중 최소 범주(영역 1개 접기·OHS 폴더·계약 불변). 한계 비용 ≈1~17분(G1′ 2h17m의 1/149~1/8). STOP 발생 자체는 표면 밖 148건이 원인 — #188 한계 비용 0. 베이스라인 ③형 ≈56분/레인은 부적용 |
| 코퍼스 정합(P1 가정) | 검증됨(충돌 0) | 아래 §3-2 IRI 전수 |
| 일반화 | MINOR(부분 의존) | 오독의 «그럴듯함»은 spring_dream_server의 OHS-only BC 4개(선례 풍부)에 기인. 공백 자체는 런타임 중립 |
| 무손실 | 검증됨(강화) / P1은 오차단 위험 | 관찰 모드에서 라벨 규율 강화는 «강화». 검출 집합(예보) 불변 |

## 2. 타임라인 · 근거 인용

### 2-1. #188 `57a4705e1218` 전건 (reading pregate-report.md · KST = Z+9)

| run | 시각(Z) | 항목 | #188 | 처분 | 출처 행 |
|---|---|---|---|---|---|
| 1 | 09-01T23:20 | skip(구형) | — | — | :2 |
| **2** | 09-01T23:43 | 11건 | red | **filtered** «OHS-only area · projection-only 1:N 진단» | :26, :83, :89 |
| 3~11 | 23:44~00:48 | 11→2건 | red | (처분 미기재 — run 2 처분 존치) | :107~:593 |
| 12·13·14 | 01:24~01:55 | 2건 | red | filtered 재기재 ×3 | :659, :733, :807 |
| 16 | 02:34 | 2건 | red | **«stable filtered» — final epoch seal** «가짜 driving_layer/api/citation_validation/ 생성 금지 · 실제 G2 registry gate가 최종 판정» | :943 |
| 19·20·23 | 04:58~08:02 | 2건 | red | filtered ×3 | :1154, :1243, :1362 |
| 24·25·26 | 08:58~09:49 | 1건(#188만) | red | filtered ×3 | :1453, :1543, :1633 |
| 28·29 | 10:58·11:30 | 1건 | red | filtered ×2 | :1803, :1895 |
| 30 | 13:36 | 형식 red | — | — | :1980 |
| **31** | 14:26 | 3건 | **소멸** | — | :1988 |

- red 지속 26회(run 2~29 중 예보 회차) · 명시 filtered 13회 · 표적 텍스트 불변(«승인된 OHS-only area다 … 승인되지 않은 외부 surface»).
- 실물 이벤트(spring_dream_server git, KST): P3 착지 `43e9628` **09-02 14:53**(run 2 후 6h — `application_layer/citation_validation` 미존재·`api_router.py` 0B·controller 0 → 가드 False·#188 침묵) → STOP-149 `87fef40` **21:50:59** → 승인 A `d24bff8` **21:59:29** → G1′ 마감 `e606eb9` **09-03 00:07:54**(`evidence_provisioning/validate_citations` 최초 등장) → P4 구현 `585c9c6` **02:32:40**.
- STOP-149: L76 «#188: application `citation_validation` area에 대응 HTTP API area가 없음» · L165 «P4가 concrete api surface를 만들면서 1:1 규칙이 활성화 — citation_validation 영역에 api 없음»(1건) · L179 지침 8 «HTTP 없는 영역을 위해 api 영역을 만들지 않는다 … `citation_validation` use case를 `evidence_provisioning` 영역 아래로 접는 안을 권고(OHS 폴더·published 계약 불변)».
- 최종 트리: `application/fortune_reading/application_layer/evidence_provisioning/{prepare_fortune_evidence, validate_citations}/` · `citation_validation/` 부재 · `driving_layer/api/evidence_provisioning/` 존재 — 예보 함의(영역 1:1)와 동일.

### 2-2. 왜 «도구 한계»가 아닌가 — 검사기 원문

- `dddjango/scripts/check-usecase-dto-placement.py:302-307`: `if api is not None and _has_concrete_api_surface(...)` → `app_areas - api_areas`(webhook 제외)마다 #188. 술어는 **디렉터리 집합 차**뿐 — 스텁 본문·문법·시뮬레이션과 무관. file-plan이 곧 트리라 투영 오차가 원리적으로 0.
- `:259-273` `_has_concrete_api_surface`: `api_router.py` 비어있지 않음 ∨ `*_controller.py` 존재 ∨ webhook 내용 ∨ registrar 사용. P3(0B·0 controller)에서 False → 침묵, P4(394B·1 controller)에서 True → 발화. pre-gate는 controller add를 스텁으로 실체화해 **P4 종상태**를 정확히 예보했다.
- 레인의 «OHS-only area는 면제» 독법은 **BC 단위 면제**(api 표면 없는 BC — 실트리에 `fortune_calculation/chart_calculation`·`fortune_intent/request_understanding`·`llm_access/generation`·`notification/email_notice` 4건 통과)를 **영역 단위**로 오적용한 규범 오독이다. 따라서 오탐도 미탐도 아닌 «진탐의 오라벨» — ⓪ 판정과 일치.

### 2-3. 규범 문면 3판 대조

- v2.17.14(rev1, `git show dddjango--v2.17.14:dddjango/commands/dddjango.md`): «처분 라벨 `corrected | ignored | filtered` 를 append» — **의미 정의 없음**. 레인 R은 이 판 하에서 완주 → 당시 미준수 아님.
- rev3 현행 `ontology/rules/command-dddjango.ttl:3274` = `dddjango/commands/dddjango.md:96`: «`filtered` = pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정(실코드 대조·기존 통과 선례 **등** 근거 병기 의무)» + «각 채널의 정의 밖 재량 라벨은 없다». 속(genus)은 닫혔고 근거 유형은 «등»으로 열려 있다 — ⓪의 문면 판독 정확.
- 그러나 rev3 하 동일 처분의 «적법 기재» 가능성: 「시뮬레이션 한계(projection-only) · 통과 선례: `application/llm_access/application_layer/generation`(api 부재·registry 통과) · 실코드 대조: P3 `43e9628` #188 exit 0」— P1이 제안한 3유형 중 **선례·실코드 2유형을 그대로 만족**한다(선례 BC의 가드 상태가 다르다는 사실은 검사기 코드를 읽어야 안다). 즉 근거 유형을 닫아도 오독은 통과한다.
- 정정 후보(참고): 이 사례를 결정적으로 거르는 문면은 «경로·폴더 존재만으로 판정되는 구조 규칙(file-plan 투영 = 설계)에는 filtered 가 없다»이나, 이는 «유형 닫기»가 아니라 새 판별 기준이며 현행 규범 하 발화 0.

### 2-4. 사각 목록 대조(BLIND_SPOTS — `design_pregate.py:1503-1531` · rerun 리포트 :57-73 동일 9행)

| 정당 filtered 사례 | 사각 목록 항목 | 실코드/선례 경로 | P1 매핑 |
|---|---|---|---|
| #107 update 대상 미실체화(reading ×20) | «미시뮬레이션: update 계획» ✓ | — | ✓ |
| #493 self 미타입 ×15(레인 2) | 없음(v2.17.15 수리로 소멸) | 전 트리 self 스캔 0·통과 코드 exit 0 ✓ | ✓ |
| #593 마이그레이션(레인 3) | «정형 보충 … 마이그레이션 칸» ✓(배치 2 수리) | — | ✓ |
| **#392 factory_boy(레인 1 · 카탈로그 현재 발화)** | **없음**(R-5a 잔존) | 선례 10파일 존재(spring_dream_server) / 첫 BC 프로젝트면 0 | △ 오차단 위험 |
| **#160/#484 OHS aux 예외(레인 1)** | **없음**(R-5b 잔존) | 선례 의존 | △ 오차단 위험 |
| #212/#283 ABC · #329/#332/#630 Meta | 없음(수리 소멸) | — | (소멸) |

→ «사각 목록에 없는 실제 도구 한계» = #392 · #160/#484(둘 다 스텁 본문 `...` 기인 — 규칙이 본문 내용을 요구). 목록의 «C급» 항목은 «표면 밖(미발화)»을 말하므로 «본문 기인 오발화»의 인용처가 못 된다.

### 2-5. 개정 비용(P1·P2 가정 — `docs/DEVELOPMENT.md` §3)

- R-3433 rev4 amendment → `ontology_render.py --apply command-dddjango`(블록 s006/b9는 R-3432·R-3434·R-3435·R-3436과 공유 — 1블록 재투영) → `make rulepack` → LEDGER 재기준선(command-dddjango s006) → codex `SKILL.md:114` 의미 미러(현행 parity 1/1 확인) → ledger.md 판정 규칙 행 «rev3» 갱신. P2는 `agent-discipline-reviewer` 문서 키 추가 개정.

## 3. P1~P3 판정 · 권고

### 3-1. 판정

- **P1(근거 유형 닫힌 목록)** — MAJOR. ⓑ 무손실: #392·#160/#484가 사각 목록 밖이라 선례 없는 프로젝트(첫 BC·kkebi형)에서 정당 filtered 오차단. ⓒ 효과: 표적 #188이 선례·실코드 2경로로 통과(§2-3). 필요조건도 충분조건도 아님.
- **P2(discipline-reviewer G1 항목)** — BLOCKER. 시점(처분은 리뷰어 호출 뒤 append)·소유(코디네이터 소유 산출물)·비용(문서 키 +1) 모두 불성립.
- **P3(무행위 — 승격 시 자연 소멸)** — 소멸 주장은 반증(R-3436은 구형 skip만 폐지·filtered는 R-1 이후 유일 우회로로 존속 → 허위 filtered의 무게는 «권고 오처분»에서 «게이트 우회»로 커진다). 행위(지금 안 함)는 타당 — 정위치가 R-1.

### 3-2. 3축 예비

- 코퍼스 정합: 건드릴 IRI = `R-3433`(@2026-09-03 → rev4) · 동블록 `R-3432/R-3434/R-3435/R-3436`(재투영만) · `R-3438`(s002/b8 — 리포트 소유 문면·라벨 열거만이라 무변경) · `R-3437`(무관) · rulepack `works/R-3433.expression` · codex SKILL.md L81/L114 · design v4 §8 ⑴ «R-3433 rev2가 정본» 산문 참조 · ledger.md 판정 규칙 행. 충돌·중복·약화 없음. P2 시 `agent-discipline-reviewer` 추가.
- 일반화: 오독의 발생 조건(OHS-only BC 선례 4건·Codex 장수 레인 44회)은 프로젝트 고유. 공백 문면 자체는 양 런타임 동일(parity 확인).
- 무손실: 예보 집합 불변·게이트 강도 불변. 관찰 모드에서 처분 규율 강화는 «강화»(완화 아님). P1만 오차단 위험.

### 3-3. 권고 처방 (1개)

**기각 — «규범 미준수(rev3 속 밖) + 현행 규범 하 발화 0·1레인» 사례로 재분류하고 배치 3 비대상. 이월 조건 2개를 R-1(차단 승격) 브리프에 등재한다.**

1. R-1의 R-3433 개정(권고→반송 의무)에 «구조 규칙(경로·폴더 존재만으로 판정)은 file-plan 투영이 곧 설계라 filtered 대상이 아니다 — 처분은 corrected 또는 ignored(+G2 증거)뿐» 1문을 **필수 조항**으로 등재한다. 승격 후 filtered가 유일 우회로가 되는 그 시점이 정위치이며, 근거 «유형» 닫기(P1)는 이 조항의 보조로만 넣는다(사각 목록 인용 ∨ 실코드 exit 0 ∨ 통과 선례 — 단 #392·#160/#484가 사각 목록에 오르기 전에는 «스텁 본문 `...` 기인» 4번째 유형이 필요).
2. 카탈로그 레인 #392(`869e0acd832f`) 처분이 rev3 하 **첫 filtered 표본**이다 — ledger 레인 4 행에 근거 형식(사각 목록/선례/실코드 중 무엇을 썼는가)을 실측 기록하고, 그 결과로 1의 문면을 확정한다.
3. (기록 정정 권고 — 본 리뷰는 무수정) ledger 레인 R 발견 ⑧에 «rev1 하 발생 · rev3 문면상 미준수 · P1 3유형으로는 미차단(선례·P3 exit 0 우회)»을 추기하고, ⓪ N-1 절의 «run 30 소멸»을 «run 31»로, «G1 시점»을 «D54 amendment 최종본(G1 후 amendment)»으로 정정.

## 4. 10줄 요약

1. 타임라인 검증됨: #188은 run 2(09-02 08:43 KST) 예보 → 26회 red 지속·명시 filtered 13회 → STOP-149(21:50)·승인 지침 8(21:59) → G1′ 접기(00:07) → run 31 소멸 · 최종 트리 `evidence_provisioning/validate_citations` 확인(⓪의 «run 30»·«G1 시점»은 정정).
2. 진탐 확정: #188 술어는 순수 트리 차집합(검사기 :302-307)이라 file-plan 투영 오차 0 — 레인의 «OHS-only 면제»는 BC 단위 가드(`_has_concrete_api_surface` :259)를 영역 단위로 오적용한 규범 오독.
3. 현행 rev3 문면(«도구 한계» 속)에서 이 사유는 정의 밖 = **규범 미준수**; 단 레인 R은 rev1(v2.17.14·정의 부재) 하에서 돌았다.
4. 그러나 rev3에서도 «선례: OHS-only 4영역 통과 · 실코드: P3 트리 exit 0»으로 형식상 적법 기재가 가능 — P1의 3유형 중 2유형이 그대로 뚫린다(유형 닫기는 표적 미차단).
5. P1 오차단 위험: 정당 filtered #392·#160/#484가 사각 목록에 없어 선례 없는 프로젝트(첫 BC)에서 금지됨 → MAJOR.
6. P2(discipline-reviewer) BLOCKER: 처분은 리뷰어 호출 뒤 Coordinator가 append·리포트는 코디네이터 소유 — 시점·경계 불성립.
7. P3 «승격 시 자연 소멸» 반증: R-3436은 구형 skip만 폐지, filtered는 반송 의무 하 유일 우회로로 존속 → 허위 filtered의 무게가 커진다(정위치 = R-1).
8. 계열·발화: 레인 2·3은 rev1 라벨 집합 혼동(무해·rev2 종결)이라 동계열 아님 → 실 레인 1·rev2+ 관측 0(카탈로그 1회·처분 미기재) → ⓪ 자체 필터 미달.
9. 효과 과대: #188 한계 비용 ≈1~17분(149건 중 1·8범주 중 최소 — G1′ 2h17m 안분), STOP 발생은 표면 밖 148건이 원인 · ③형 ≈56분 베이스라인 부적용.
10. **권고: 기각 — 미준수+발화 미달로 재분류·배치 3 비대상.** R-1 브리프에 «구조 규칙에는 filtered 없음» 필수 조항 + 카탈로그 #392 처분 실측(첫 rev3 filtered 표본) 2건을 이월 등재.
