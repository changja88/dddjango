# W3 적대 리뷰 — «discipline-docs» 묶음 (discipline-cleancode-skill · discipline-houserules-skill · discipline-houserules-final)

- 리뷰 일자: 2026-08-22 · 리뷰어: 적대 검증 레인(승인 아님·반박 목적)
- 검사 범위: 3 spec + 3 worksheet **전수 절**(표본 아님) · 4렌즈(경계·kind / 규범 식별 / 배선 / 재진술)
- 실물 대조: 원문 3종(56·83·242행 — 발주서 행수와 일치) · 발주서 3종 · `check-*.py` 27종 docstring(로스터 27 확인) · `workspace/plan/2026-08-11-rule-owner-map.md` · `ontology_migrate.py` docstring · 파일럿 2종 + 웨이브 기이관 spec(판례 대조)
- 기계 검증: 3 spec 모두 `ontology_migrate.py`(--write 없이) **exit 0** · Work 계수 20/75/58 = 발주서와 전건 일치 재확인

## 판정 요약

**반려(pass=false).** 규범 식별·재진술 유예·계수는 발주서와 전건 대사되고 worksheet 기록도 충실하나, `discipline-houserules-final` 의 **배선 4건이 실물 대조에서 무너진다** — 그중 #430·#432 두 건은 «존재하지 않는 기계 집행»을 그래프에 주장하는 basis 허위로, 저작자 자신이 #10·#82 에 적용한 기준(«enforcedBy 를 걸면 그래프가 존재하지 않는 집행을 주장하게 된다» — worksheet §4)과 정면 모순이다.

---

## HIGH

### F1 — [배선] discipline-houserules-final / s010 (b2) : #430 의 `enforcedBy check-layer-skeleton.py` 는 실장 부재

- **주장**: #430(«`<project>/` 는 `application/` 을 등록만 하고 «타입»으로 알지 않는다» — import 금지 = **ast/내용 판정**)을 근거5 로 `check-layer-skeleton.py` 에 단독 배선했으나, 실물 대조 결과 그 검사기에 #430 진단은 **없다**. `grep '#430' check-layer-skeleton.py` → 0건. docstring 「무엇을 잡나」의 `<project>/` 몫은 «#429·#436 `<project>/` 직계 폐쇄»뿐이고(15행), 26행이 «내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다 — 여기는 «존재·폐쇄»만 본다»로 **현행 미커버를 자기 선언**한다. rule-owner-map 의 #430 행(ast·작업=재작성)은 미래 계획이지 실장이 아니다 — 같은 조건(map ⓒ 지목 + docstring Phase 3 유예)의 #10·#82·#628 은 저작자가 스스로 위임(또는 타 검사기)으로 처리했으면서 #430 만 enforcedBy 로 남긴 내적 비일관.
- **수정안**: #10·#82 와 동일 처리 — `delegatedTo: [agent-discipline-reviewer]` 단독으로 바꾸고, basis 를 근거9 형(«④map ⓒ 지목이나 ②docstring 26행 Phase 3 유예 선언 → 현행 집행 주체는 에이전트»)으로 교체.

### F2 — [배선] discipline-houserules-final / s010 (b3) : #432 의 `enforcedBy check-layer-skeleton.py` 는 실장 부재 (+ 실제 기계 흔적은 context-isolation #433)

- **주장**: #432(«`<project>/` 는 BC 가 늘어도 커지지 않는다» — 내용/속성 판정)도 F1 과 동일하게 check-layer-skeleton 에 진단 0건·docstring Phase 3 유예 선언 하에 enforcedBy 단독 배선됐다. 더구나 27종 전수 grep 에서 #432 를 언급하는 유일한 실장은 `check-context-isolation.py` 858행의 **#433 진단**(«규칙을 «주소 목록»으로 적지 않는다 — BC 경로 리터럴 … BC 가 늘 때마다 이 파일이 바뀐다 · #432»)이다 — 배선하려면 이쪽이 근거 실물이고, layer-skeleton 은 어느 쪽으로도 성립하지 않는다.
- **수정안**: ⓐ `delegatedTo: [agent-discipline-reviewer]` 로 강등(F1 과 동일 사유), 또는 ⓑ `enforcedBy: [check-context-isolation.py]` + 위임 병기로 바꾸고 basis 에 «context-isolation #433 진단이 #432 판정 물음을 부분 실장(858행) · map ⓒ layer-skeleton 은 Phase 3 유예» 를 명기.

## MEDIUM

### F3 — [배선] discipline-houserules-final / s007 (b6) : #178 의 basis 가 «다른 규칙(#91)의 인용»으로 서 있다

- **주장**: #178 을 `check-missable-entrance.py` 에 배선한 근거13 의 ② 인용(«33·249행 «#91 — BC 가 형제를 늘리지 않는다» 직접 인용»)은 전부 **#91 의 앵커**다. `grep '#178' check-missable-entrance.py` → 0건 — 담당 규칙 목록(총 14: #172~#181·#451·#512·#514~#517·#629)에 #178 이 없다. rule-owner-map 은 #178 을 `check-layer-skeleton.py`(ast) 에 건다. 이 배선이 성립하려면 실제로 그 위반(입구 로직)을 잡는 **#179 진단**(«task 함수는 build 1회 + 유스케이스 1회뿐 — 그 밖 문장·둘째 task 면 위반»)을 인용해야 하는데 basis 는 이를 한 줄도 언급하지 않는다 — 4원 근거의 ② 가 허위 앵커(#91 문면의 복붙 재사용)로 채워진 셈.
- **수정안**: enforcedBy 유지가 목적이면 basis 를 «②missable-entrance #179 진단이 «입구 로직 금지 위반» 적출을 실장 — #178 은 그 위반의 처방(새 칸 금지·위반 수리) 규범 · ④map #178→layer-skeleton 은 Phase 3(재작성) 유예» 로 재작성하고 위임 병기 유지. 그 근거 재작성이 안 되면 위임 단독으로 강등.

### F4 — [배선] discipline-houserules-final / s006 (b4) : #628 규범 2·3 의 `enforcedBy check-business-vocabulary.py` 는 진단 부재 · «281행 진단 실장» 은 #617 의 것

- **주장**: 근거10 의 «281행 진단 실장»은 사실과 다르다 — 281행은 **#617**(<data>_out 업무 어휘 0) 진단의 `f.add("#617", …)` 이고 메시지 문자열이 #628 을 «언급»할 뿐이다. #628 의 세 규범 중 ①(어휘=domain_layer 공개 심볼 토큰 집합 정의)은 검사기가 그 정의를 소비해 #617·#587·#47 로 실장한다고 볼 여지가 있으나, ②(«별도의 용어집 파일은 두지 않는다» — 이 문면의 실물은 로스터 밖 데이터 모듈 `scripts/business_vocab.py` 5행 주석)과 ③(불용어 목록=저장소 데이터)은 **어떤 check-*.py 에도 위반 진단이 없다**. 저작자 자신의 «로스터 밖 도구는 enforcedBy 대상이 아니다» 원칙(tree_mirror_check·checker_lint 등 처리)에 따르면 ②③ 의 실현 주체(business_vocab.py)는 enforcedBy 로 걸 수 없는 자리다.
- **수정안**: 규범 ① basis 를 «②정의 소비 실장 = #617/#587/#47 진단(business_vocab.py 토큰 집합 소비)» 로 교정. 규범 ②③ 은 `delegatedTo: [agent-discipline-reviewer]` 병기(또는 단독)로 바꾸고 basis 에 «실현 실물은 business_vocab.py(로스터 밖 데이터 모듈) — 진단 0» 을 명기. 세 규범 공용 basis 의 «281행 진단 실장» 문구는 삭제.

## LOW

### F5 — [경계·kind] discipline-cleancode-skill / s001 : frontmatter [4,6] 병합 — 웨이브 «행 단위» 판례 이탈

- **주장**: 웨이브 판례는 frontmatter 를 행 단위로 가른다 — 저작자 자신이 인용한 `agent-coder`/s001 도, 기이관 skill 3종(architecture-api·discipline-tdd·implementation-django) 전건도 `[4,4]`(user-invocable 행) + `[5,6]`(닫는 `---`+빈 줄) 이다. 이 spec 은 `[4,6]` 한 블록으로 병합해 블록 IRI 입도가 코퍼스 내 동형 구조와 어긋난다(worksheet §4 메모가 판정을 기록했으나 «왜 판례의 [4,4] 분리를 버렸는가»는 다루지 않음). byte 등가·계수에는 영향 없음.
- **수정안**: `[4,4]` prose + `[5,6]` prose 로 분할(웨이브 판형 동조).

### F6 — [경계·kind] discipline-houserules-skill / s001 : F5 와 동일한 [4,6] 병합

- **주장·수정안**: F5 와 동일(같은 저작 손의 동일 이탈 — houserules-final 은 frontmatter 부재라 비해당).

### F7 — [배선] discipline-cleancode-skill / s004 (묶음 3문서 공통 표기) : 위임 기본값 basis 의 «④registry Agent 등재» 는 §16 ④ 의 오라벨

- **주장**: §16 의 4원 ④ 는 «registry **#N** 대응»(규칙 번호 조응)인데, 위임 기본값 규범들의 공용 basis(근거3 계열)는 «④registry Agent 등재»(wiring/registry.ttl 의 Agent 개체 존재)를 ④ 로 표기한다. Agent 등재 사실 자체는 참이나 4원 분류로는 성립하지 않는 자리다 — 기본값 표 경로(«위임 기본값 표 + 27종 전수 0»)만으로 §16 요건이 충족되므로 군더더기 오라벨. 세 spec·worksheet 전반에 반복된다.
- **수정안**: 해당 basis 들에서 «④» 접두만 제거(«registry Agent 등재» 사실 기재는 무방) — 4원 라벨은 실제 성립 항목에만 쓴다.

---

## 대조 완료·이상 없음 (반박 시도 후 기각한 축)

- **계수 전건 대사**: 3문서 29개 REF 절 전부 발주서 규범 수 = spec Work 수(20/75/58) · 문장 등장 순 = 채번 순 실측 일치(s004-1 26행 13문장·30행 5문장·32행 4문장 등 최대 밀도 절 포함).
- **블록 커버리지**: 도구 단언(exit 0) + 수동 대조 — 연속·비중첩·절 끝 커버 이상 없음. code 펜스(31~172행)·TREE 주석 norm 승격·table 머리+구분 한 블록(파일럿 s051-8 판형과 동형) 이상 없음.
- **재진술**: 문서 내 쌍 6건 전부 spec `restates` 수록(방향 = 사본→정본, 도구 주석 «정본 블록 지시»와 합치) · 발주서 재진술 열의 교차 문서 쌍 전건이 worksheet «재진술 유예»에 좌표·문면 대조와 함께 등재(cleancode 14건+기각 2 · skill 15건+기각 3 · final 15건+기각 3). 사본 Work 유지 판정(비축자 쌍)은 §15 파일럿 실물 기준으로 3문서 일관 — 수용.
- **배선 검증 통과 실물**: choices-literal-consumption(§2.14 직접 인용) · public-surface-annotation(#493 축자) · test-config(⑵ 105~111행 축자) · layer-skeleton(#486~#491·#81·#490·#429·#436·#58·#314 — 진단·docstring 합치) · mechanism-ownership(#336~#338·#593) · db-table(#324) · app/common-container(최상위 삼분) · port-adapter-pairing(#457↔#187) · missable-entrance(#91 — 33·249행 실물 확인) · naming 비배선 판정(#28 계열 담당 확인·유사 변형 술어 0) · 로스터 밖 도구(tree_mirror_check·checker_lint·spec_lint·registry_gate) 위임 처리 · agent-coder(«실현 주체는 coder» 문면 이탈)·command-dddjango(«미루기» 절차 층) 병기 — 전부 실물 성립.
- **#92→context-isolation 이탈**: docstring 에 #92 문자열은 없으나 «의존 방향 짝 + #93/#94/#95 각론» 인용이 정확하고 map 이탈 사유가 basis·worksheet 에 기록됨 — 기각(발견 아님).

---

## 처분 (수리자 기록 — 2026-08-22 · 원문 대조 후 판정)

대조 실물: 원문 3종 · `check-*.py` **27종 로스터**(`ls dddjango/scripts/check-*.py | wc -l` = 27) 및 `scripts/business_vocab.py` · `workspace/plan/2026-08-11-rule-owner-map.md` · 웨이브 기이관 spec 12종(판례) · `ontology_migrate.py`·`ontology-authoring.md` §13·§14·§16.
수리 후 재검증: 3 spec 모두 `--write` 없이 **exit 0** · Work 계수 **20/75/58 불변**(발주서 일치).

| # | 처분 | 근거 한 줄 |
|---|---|---|
| F1 | **fixed** | `grep '#430' dddjango/scripts/` 0건 확인 · map 판정 열이 `ast`(#430) 인데 layer-skeleton docstring 26행이 `ast` 내용 판정의 Phase 3 유예를 자기 선언 — `delegatedTo agent-discipline-reviewer` 단독으로 강등(근거24 신설, #10·#82 와 동형). |
| F2 | **fixed(ⓑ 채택)** | 27종 전수에서 #432 의 유일한 기계 흔적 = `check-context-isolation.py` 858행 #433 진단(스코프도 827행 «`<project>/` 파일» 로 일치) — 위임 단독(ⓐ)은 §16 «근거가 있는데 기본값 도피 = 오배선» 에 걸리므로 `enforcedBy check-context-isolation.py` + 위임 병기로 교체(근거25 신설). |
| F3 | **fixed** | 33·249행이 #91 앵커임을 실물 확인, 담당 목록(총 14)에 `#178` 부재 확인 — 배선은 유지하고 basis 를 #179(179·191행 `f.add`) 적출 + #178=처방 규범 구조로 재작성(근거13 교체). |
| F4 | **fixed(부분 정정 포함)** | 281행이 #617 진단의 메시지임을 확인 — 다만 `f.add("#617", …)` 자체는 **280행**이고 281행은 그 메시지 행이라, basis 는 «#617(280~281행)·#587(283~284행)·#47(286~288행)» 로 적었다(지적의 실질은 성립). 규범 ① 은 정의 소비 실장으로 `enforcedBy` 유지·basis 교정(근거10), 규범 ②③ 은 실현 실물이 로스터 밖 `business_vocab.py`(자기 docstring «진단 0»)라 **위임 단독**으로 강등(근거22·23 신설) — «병기» 대신 «단독» 을 고른 이유는 두 규범의 위반 진단이 27종에 0이라 `enforcedBy` 가 존재하지 않는 집행을 주장하게 되기 때문. |
| F5 | **fixed** | 기이관 skill spec 12종(agent-coder 포함) 전건이 `[4,4]`+`[5,6]` 임을 실측 — `[4,6]` 병합을 분할(byte 등가·Work 20 불변, exit 0 재확인). |
| F6 | **fixed** | F5 와 동일 실측·동일 처리(Work 75 불변). |
| F7 | **fixed(적용 범위 명시)** | §16·발주 계약의 ④ = «registry **#N** 대응» 이고 `registry.ttl` 은 #N 을 지지 않음(개체 선언뿐)을 파일 실독으로 확인 — 지적대로 «④» 접두만 제거. **적용 범위를 한 단계 넓혔다**: 같은 성질인 «④registry Checker 등재» 5건도 함께 뗐다(3문서 합계 61건 = Agent 56 · Checker 5). 한 파일 안에서 Agent 변종만 고치면 F1 이 지적한 «내적 비일관» 을 새로 만들기 때문. `basis` 는 그래프에 직렬화되지 않는 검수 기록이라(도구 스키마 확인) 트리플 영향 0. |

**반려 없음(rejected 0).** 네 개 배선 지적(F1~F4)은 전부 원문·검사기 실물에서 재현됐고, 경계 지적(F5·F6)은 코퍼스 12종 실측으로 확정, 라벨 지적(F7)은 계약 문면 대조로 확정했다.

### 수리 중 얻은 판별선 (재발 방지)

- **`rule-owner-map` 의 «판정» 열이 layer-skeleton 배선의 실장 경계다.** `path` 행은 그 검사기가 실제로 지고(#81·#88~#91·#20·#21·#58·#187·#314·#429·#436·#486~#491), `ast` 행은 docstring 26행 Phase 3 유예 구간이다(#10·#82·#178·#430·#432·#628). 이 선으로 `discipline-houserules-final` 의 layer-skeleton 배선 **전건**을 재대조했고, F1·F2 외 추가 이탈은 없었다.
- **로스터 밖 실물(진단 0 데이터 모듈)은 `enforcedBy` 자리가 아니다** — `business_vocab.py`(#628 ②③) 가 `tree_mirror_check`·`checker_lint`·`spec_lint`·`registry_gate` 와 같은 처리로 편입됐다.

### 코퍼스 소급 권고 (이 발주 범위 밖 — 수정하지 않음)

- «④registry Agent/Checker 등재» 라벨은 이 묶음 밖 웨이브 spec·검수표에 **317건**(Agent 315 · Checker 2) 남아 있다(수리 후 전수 스캔). 발주가 쓰기를 허용한 파일은 자기 spec + worksheet 뿐이라 손대지 않았다 — F7 을 코퍼스 전체에 적용하려면 별도 일괄 패스가 필요하다.
- `discipline-houserules-final` `s004-1` 의 트리 좌표 공백(펜스 1블록이라 «트리 N행» 을 블록 IRI 가 못 짚음)은 초판 검수표 §4 기록대로 미해소 — 이번 수리 범위 밖.
