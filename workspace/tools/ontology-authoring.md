# 온톨로지 저작 규약 (T0 A2 — 2026-08-19 초판)

> `ontology/` 정본 트리의 저작·게이트·채번 규약. 규범 정본은 블루프린트 v3.2(E1~E8) — 이 문서는 그 실행 규약이다. 수기 문서라 ontology/ 밖(§3 «정본 직렬화본만 존재»)에 둔다. T0 계획: `workspace/design/2026-08-18-ontology-t0-plan.md`.

## 1. 금지 목록 (E4 — 게이트가 기계 차단)

| 금지 | 범위 | 차단 단 |
|---|---|---|
| blank node | rules/·wiring/·vocab/ 전 노드, shapes/ 셰이프 노드 (SHACL 리스트 인자의 cons 셀만 예외 — sh:in·sh:or·sh:languageIn·sh:ignoredProperties 등 RDF 컬렉션) | ② |
| 미등록 접두사 | 전 정본 파일 — @prefix (접두, IRI) 쌍이 prefixes.ttl vann 등재 쌍과 정확 일치해야 통과 | ② |
| Turtle `#` 주석 | 전 정본 파일(전면 금지 — 직렬화기가 주석을 출력하지 않아 재직렬화 diff≠0) | ② |
| 비정본 직렬화 | 전 정본 파일 — 파일 == canon(parse(파일)) 이어야 함 | ② |
| PN_LOCAL 비허용 문자의 접두명 축약 | `@` 등 포함 로컬네임(Expression IRI 등)은 `<전체 IRI>` 표기 고정 | ①/② |
| 추론 유발 공리 | `rdfs:domain`/`rdfs:range`·`owl:*` (E2 저-공리 — 계층은 `rdfs:subClassOf`만) | ④(셰이프)·심의 예외 |

## 2. 4단 저작 게이트 사용법 · 수리 루프 (도구: `workspace/tools/ontology_gate.py`)

- ① 파스(rdflib) → ② 정본 재직렬화 diff=0(+접두·IRI 의무 검사) → ③ RDFC-1.0 해시 전후 비교 → ④ SHACL(pySHACL `-i none`, 리포트 그래프 SPARQL 판정).
- `shapes/golden/`은 ①~③만 적용, ④는 기대 판정(red/green) 대조.
- 실패 시 구조화 되먹임 리포트(JSON, `schema: "gate-report/1"` — 단·파일·노드·사유). 필드 추가=호환 확장, 기존 필드 의미 변경=버전 증가. LLM 수리 루프는 이 리포트만 재료로 1~2회.
- 게이트 ④의 데이터 그래프 = **변경 파일 + vocab/*.ttl + wiring/*.ttl + rules/*.ttl 전량 병합**(파일 단독 검증 금지 — SHACL 대상 선정·sh:class가 데이터 그래프 안의 subClassOf 경로 기준. rules 전량은 교차 참조 restates·aliasFor의 위양성 red 해소 — T1-2 개작, §16).
- `rules/`·`wiring/`는 첫 정본 파일과 함께 생성된다 — 빈 디렉터리는 비커밋(§«정본 직렬화본만 존재» 문면상 .gitkeep류 이물 금지). 게이트·도구는 결측 디렉터리에 무해함을 확인함.

## 3. 정본 직렬화 규칙 명세 (canon/1 — `ontology_canon.py` 구현과 문면 일치)

- 정렬: 접두 선언(접두명 코드포인트 순) → 주어(IRI 코드포인트 순) → **술어(rdf:type 우선 — `a` 표기, 이후 전체 IRI 코드포인트 순)** → 목적어(직렬화 토큰 코드포인트 순).
- 포맷: 주어당 1블록, 술어·목적어는 ` ;`/` ,` 연속, 4칸 들여쓰기, 블록 사이 빈 줄 1, 파일 끝 개행 1, EOL=LF.
- 주석 미출력(§1 금지와 짝). 리터럴·IRI는 원시 UTF-8(과잉 이스케이프 금지), **유니코드 NFC 고정**(macOS NFD 유입 방어 — 저작 입력을 NFC 정규화 후 직렬화).
- **언어 태그는 소문자만**(RDFC-1.0 REC §1 Note 권고 — `@ko`).
- PN_LOCAL 비허용 문자(`@` 등) 포함 로컬네임은 접두명 축약 금지 — `<전체 IRI>` 고정.
- 직렬화기 버전 상수는 직렬화기 모듈에 두고, **직렬화 규칙 변경 = 같은 커밋에 전 코퍼스 재직렬화**(아래 §4).
- 알려진 사슬 특성: rdflib는 파스 시 일부 타입 리터럴의 어휘형을 정규화한다(예: `"…T00:00:00Z"^^xsd:dateTime` → `"+00:00"`). 게이트 ②가 정규형을 정본 파일에 강제 재작성하므로 저장 파일 기준 결정성·상호운용은 유지되나, 저작자는 diff에 이 재작성이 보일 수 있음을 인지한다.

## 4. 재직렬화 전용 커밋 규칙 (E4)

직렬화기(또는 그 규칙·버전) 변경은 논리 변경과 **분리 커밋**으로 하고, 같은 커밋에 전 코퍼스 재직렬화를 동반한다(트리플 집합 불변 — 게이트 ③이 증명). 커밋 메시지에 «재직렬화 전용» 명기.

## 5. ISSUED 채번 절차 · 행 형식 (E6)

- 파일: `ontology/ISSUED` — **append-only**(행 수정·삭제 금지). Work IRI는 이 대장 경유로만 발행.
- 행 형식(TAB 구분 3필드): `R-NNNN<TAB>YYYY-MM-DD<TAB>최초 등재 문서 경로`
- 절차: 다음 번호 = 대장 마지막 번호+1(결번 재사용 금지) → 행 append → 같은 커밋에서 rules/에 Work 노드 등장. ISSUED↔rules/ 정합 검사(v2 registry_lint 동형)는 채번이 시작되는 T1 산출물.
- djr: 기저 URI = `https://numchida.com/ns/djr#` (D5 — 사용자 승인 2026-08-19. 비역참조 불변 문자열 — 역참조 서버를 전제하지 않는 식별자).
- prefixes.ttl의 제3자 어휘(skos·prov 등) vann 등재는 **저장소 등록부**이지 해당 어휘의 자기 선언이 아니다 — «이 저장소가 이 접두로 이 어휘를 쓴다»는 대조 기준일 뿐, 어휘 소유자의 선호 접두 주장으로 배포하지 않는다.

## 6. 오류 계열→차단 단 매핑 표 (A9 — 검수 대상 · **이 표가 정본**, T0 계획은 이 표를 참조)

픽스처: `workspace/eval/fixtures/ontology_gate/cases/` · 하네스: `workspace/tools/ontology_gate_smoke.py`(gate-report의 «단» 필드 단언).

| 오류 계열 | 라벨 | 픽스처 | 차단 단 (스모크 실증) |
|---|---|---|---|
| blank node(rules/·wiring/·vocab/ 노드) | 동결 | red 1 | ② IRI 의무 검사 |
| blank node(shapes/ 셰이프 노드) | 동결 | red 1 | ② |
| cons 셀 리스트 인자(sh:in 보유 valid 셰이프) | 동결 — 예외 실증 | **green 1** | 통과(과차단 방지 대조군) |
| 미등록 접두사 | 동결 | red 1 | ② vann 쌍 대조 |
| `#` 주석 | 동결 | red 1 | ② 재직렬화 diff≠0 |
| 해시 조작(재직렬화 전후 트리플 삽입 — 결함 주입 훅+픽스처) | 동결 | red 1 | ③ |
| 비정본 직렬화(순서·포맷 어긋남) | 계획 추가 | red 1 | ② |
| Expression IRI 접두명 축약 표기(`@` 미이스케이프) | 계획 추가 | red 1 | ① |
| djr IRI fragment 문법 위반(§14 원시 금지 문자 — rdflib 무저항 통과 실측) | T1-2 추가 | red 1 | ② fragment 검사 |
| 셰이프 위반(완결성 누락 — 대표 1 · 골든 페어와 재료 공유) | 동결 | red 1 | ④ |
| sh:closed 상위 클래스 타깃 | 계획 추가 | red 1 | meta-SHACL 2층(하우스) |
| sh:closed의 ignoredProperties(rdf:type) 누락 | 계획 추가 | red 1 | meta-SHACL 2층(하우스) |

## 7. 어휘 개정 절차 (djr 어휘 자체의 개정 — 규칙 개정(E6)과 별개)

1. 리네임/형상 변경 맵을 기록(구→신 대응 전수)
2. 스크립트 일괄 변환(수기 금지) — vocab+shapes+rules+wiring 전 파일
3. 전후 그래프가 «리네임 맵 적용과 동형»임을 확인
4. §4 재직렬화 전용 커밋 관례로 커밋
- **안정화**: T1 게이트에서 해상도 확정과 동시에 어휘 v1 재심·안정화 선언(T1 계획 이월). 이후 개정은 본 절차 의무 — T3 전량 이관 후 개정 비용은 코퍼스 전체 규모임을 자인.

## 8. RDFC-1.0 구현 결정 (A1 실사 — 2026-08-19)

- **채택: `rdfcanon` 1.0.0** (PyPI — W3C rdf-canon 구현 리포트 등재).
- 실사 결과: W3C 공식 스위트 실행 — sha256 대상 63건 중 60 통과, sha384 1건 별도 실행 통과. **실패 3건(test011·013·014)의 원인은 rdfcanon이 아니라 rdflib 파스 단계의 타입 리터럴 정규화**(§3 사슬 특성) — 자체 구현도 rdflib 파스를 쓰는 한 동일하므로 채택 판단에 중립. 알고리즘 본체(N-Degree 포함)는 정합.
- 주의 2점: ① rdfcanon은 `rdflib==7.5.0` 정확 핀 — 우리는 rdflib 7.6.0 고정(pySHACL 0.40.1 사슬 요구)이라 **`pip --no-deps` 설치로 강등 차단**(위 실사가 7.6.0 위에서 수행됨) ② `RDFCanonTimeTicker`를 명시 전달해야 함(기본값 None 처리 버그) — 호출부 규약.
- 도구 스모크(`ontology_env_smoke.py`)에 공식 스위트 발췌 벡터 3종(지면·이중 링크·다이아몬드 N-Degree)을 내장해 상시 검증.
- 기각한 대안: 자체 구현(공유 리스트 cons 셀이 N-Degree 해싱을 요구 — 사실상 전체 알고리즘 재작성, L1-3) · rdflib.compare(RGDA1 — RDFC-1.0 비호환 알고리즘).

## 9. 정렬 직렬화기 — 기성 선례와 비채택 근거

- 선례: EDM Council **rdf-toolkit**(FIBO 정본 직렬화기 — pre-commit에서 강제, 주어→술어→목적어 정렬). 비채택 근거: Java(JRE 11+) 의존 — A1 파이썬 단일 사슬·E7 배포 경계와 충돌. house 포맷은 §3에 사양으로 고정한다(Turtle REC는 정본 직렬형을 정의하지 않으므로 house 포맷 자체는 합법).

## 10. 어휘 동봉 표 2종 (E5 — vocab/djr.ttl 딸림. 정본 파일은 주석 금지라 여기 수록)

### 10.1 ODRL 봉인 목록 (명명 참조만 — rdfs:seeAlso 1종, subClassOf 연결 금지)

| ODRL 항 | 우리 대응 | 봉인하는 함정 |
|---|---|---|
| odrl:Duty | djr:Obligation (seeAlso) | Duty 역할 과적(의무·보상·조건 겸용) — 자체 프로파일로 배제 |
| odrl:Prohibition | djr:Prohibition (seeAlso) | — |
| odrl:Permission | djr:Permission (seeAlso) | 강한/약한 허용 미구분 — 규범 공백 기본 정책은 open(E5)으로 별도 확정 |
| (도입 안 함) | — | 유지/과정 의무 구분, odrl:Policy 계층, 제재(remedy) 모델 전부 — 차용 범위 밖 |

### 10.2 프로퍼티 역할 표

| 프로퍼티 | 역할 | 금지 |
|---|---|---|
| skos:prefLabel | 명칭만(언어당 1 — 셰이프 sh:uniqueLang) | 규범 본문·설명 서술 |
| skos:definition | **미사용** | 전면 |
| djr:text | 규범·산문 본문의 유일한 자리(블록 리터럴 — E5 리터럴 우선) | 리터럴 복제 |
| rdfs:seeAlso | ODRL 명명 참조 1종 | subClassOf 대체 사용 |
| rdfs:subClassOf | 계층의 유일 수단(E2) | — |
| rdfs:domain·rdfs:range·owl:* | **미사용**(E2 저-공리) | 전면(심의 예외) |
| prov:wasRevisionOf | Expression 개정 연쇄 | 자체 신설 대체 |
| prov:specializationOf | Expression→Work | 자체 신설 대체 |
| prov:Activity(+wasGeneratedBy) | 개정 이벤트 | — |

## 11. 훅 단일 루트

이 저장소의 git 훅 단일 루트 = `workspace/hooks`(`git config core.hooksPath` — ③묶음 설치 타깃 제공). `.git/hooks`에 직접 설치된 훅은 **조용히 무시**되므로, 설치 타깃이 비샘플 훅 존재 시 경고한다. 훅 퇴행 조건: ttl 변경 없음 → 즉시 exit 0 · venv 부재+ttl 변경 → 명시 오류+`make ontology-env` 안내(fail-closed).

## 12. A3 어휘의 열린 결정 — 처분 현황 (신선한 눈 감사 m-4 반영, 2026-08-19)

- ~~규범 유형 5종 ⊑ djr:Norm ⊑ djr:Work 계층~~ — **확정**(vocab·셰이프 실장, 골든 12/12·계수 회귀가 상속 실증).
- ~~djr:severity 값 공간~~ — **확정: sh:Violation/sh:Warning/sh:Info IRI**(셰이프 sh:in·findings/0 대응 표·역할 표 3자 일치).
- ~~블록↔Work 연결 형상~~ — **확정: 3노드형**(2026-08-19 사용자 «전부 승인» — 블루프린트 §3 **개정 1** 기록: E6 정체성 모델 우선·리터럴 복제 없음 유지).
- ~~규범 소유 의무~~ — **확정: «검사기(enforcedBy) ∨ 위임 에이전트(delegatedTo)» — 무소유만 차단**(감사 M-2 재정, 같은 승인. NormShape sh:or(HasChecker·HasDelegate) 실장·work-delegated-valid 골든).
- ~~alias 재이피케이션(AliasEntry)·RevisionKind 군~~ — **확정: 존치**(같은 승인. deprecated/replacedBy 보완 완료).
- ~~kind-checklist-item 존치 여부~~ — **확정: 존치**(2026-08-19 T1-6 재심 — 코퍼스 체크박스 0 실증(게이트 1 상정·처분안 승인)에도 kind 5종은 닫힌 집합 계약이고 체크박스 등장 시 즉시 필요·삭제 재개정 비용이 더 큼. 파일럿 미실증 kind임을 자인).
- **어휘 v1 안정화 선언(2026-08-19 — T1-6·파일럿 실저작 재심 완료)**: T1-2 개정분(BlockShape-text sh:or·djr:parentSection)까지 포함해 djr 어휘 v1을 **봉인**한다. 파일럿 117 Work·73블록·4절 실저작에서 어휘 결함 0(구조 검증 5종 조인 성립). 이후 개정은 §7 절차(리네임 맵·스크립트 일괄 변환·동형 확인·재직렬화 커밋) 의무 — T3 전량 이관 후 개정 비용은 코퍼스 전체 규모임을 자인.

## 13. 블록 경계·공백 소유 규약 (T1-2 — 라운드트립의 근간)

- **블록 리터럴 = 원문 스팬 verbatim** — 문장 내부 경질 개행(ninja 관례)·한 행 다문장(ddd 관례) 모두 그대로. 블록 간 구분자(공백·개행·빈 줄)는 **선행 블록의 후행 스팬에 귀속**한다. 렌더 = 블록 순서 단순 연결(구분자 삽입 0) — byte 등가가 규약으로 성립한다.
- 리스트 항(`- `·`1. `)·blockquote(`> `)는 **마커 포함 verbatim**으로 norm/prose 블록에 귀속(kind 확장 불요). checklist-item kind는 체크박스 형태(`- [ ]`/`- [x]`) 한정.
- kind=code 리터럴 = **여는 펜스~닫는 펜스 전체 라인 verbatim**(언어 태그 포함 — closed 셰이프에 별도 자리 불요). 표 머리행·구분행도 kind=table-row(단 계수 2축에서는 데이터 행만 산입).
- 소비 시 trim·정규화(재진술 대조·규칙 팩)는 T2 소비층 몫 — 정본 리터럴은 verbatim 불변.
- **절 스팬의 소유 분해**: 절 원문 스팬(센서스 행 범위) = 헤딩 라인(Section의 djr:headingSnapshot 소유·개행 포함) + 블록 시퀀스(헤딩 다음 행부터 절 끝까지의 연속 비중첩 행 범위 분할 — 무손실). 절 선두 구분자(헤딩 직후 빈 줄)는 **첫 블록의 선두 스팬에 귀속**(선행 블록이 없는 유일 예외 — 블록 간 구분자는 §13 원칙대로 선행 블록 후행 귀속). 렌더 = headingSnapshot + 블록 리터럴 단순 연결.
- **해상도의 실현 층**: «문장 해상도» = **Work 채번 단위가 문장**이라는 뜻이다. 블록 경계는 언제나 §13 자연 단위(문단·불릿·펜스·표 행 묶음 — 행 범위)이고, 한 블록의 여러 규범 문장은 `djr:statesNorm` **다중 연결**로 각자의 Work를 가리킨다(개정 1 3노드형 — 행 중간 분할 불요, byte 등가 불변). 블록 내 문장→Work 대응(문장 등장 순=채번 순)은 검수표에 기록한다. «절 해상도» = 절의 규범 전체가 Work 1개.
- **preflight(이관 공정 ⓪)**: 이관 대상 원문의 NFC·LF·탭 스캔 — 위반 시 원문 선정정 커밋 **후** 이관(이관 커밋에 원문 정정 혼입 금지).
- 픽스처: red/green 3벌(경질 개행 문장·한 행 다문장·문단 경계) — fixture 레인 `workspace/eval/fixtures/ontology_gate/` 편입(T1-4 렌더러와 함께).

## 14. 절/블록 IRI 인코딩 (E6 실장)

- **절 IRI** = djr 기저 + `s/` + 문서 저장소 상대 경로 + `/` + 절 키. **블록 IRI** = 절 IRI + `/b` + 블록 서수. 예: `<https://numchida.com/ns/djr#s/dddjango/skills/architecture-ddd/references/final.md/s017-3.2/b3>`.
- **문서 IRI** = djr 기저 + `d/` + 문서 저장소 상대 경로. **검사기 IRI** = djr 기저 + `c/` + 스크립트 파일명(`c/check-naming.py`). **에이전트 IRI** = djr 기저 + `a/` + doc_key(`a/agent-discipline-reviewer` — Coordinator는 `a/command-dddjango`).
- **절 키 = `s<서수 3자리>`(+ 헤딩 앵커 있으면 `-<앵커>`)** — 센서스 도구(`ontology_census.py`) 산출 규약과 동일 문면. 서수 = 문서 내 등장 순(1부터). 신규 절 삽입 시 기존 서수 불변·새 절만 **다음 미사용 서수**(절 키 대장 = 원장 `LEDGER.tsv` 겸용 — 결번 재사용 금지). 무앵커 문서 선두 절 = `(전문)` 절(키는 `s001`).
- **폐쇄 인코딩 집합**: 공백·`#`·`%`·`` ` ``·`<`·`>`·`"`·`{`·`}`·`|`·`\`·`^`·C0/C1 제어문자**만** percent-encoding(`%` 자기 포함 — 가역성 성립). pct-encoding hex는 **대문자 고정**(정규형 — 게이트 ② 검사와 문면 일치). 한글·`§`·`·` 등 RFC 3987 ucschar는 원시 표기. NFC 고정. 왕복(인코딩→디코딩) 항등 픽스처 의무.
- **게이트 ② 확장(T0 개작)**: djr 네임스페이스 IRI의 fragment 문법 검사(정규식 — rdflib가 위법 IRI를 무저항 통과시킴이 실측됐으므로 기계 백스톱).
- 전 절/블록·Expression IRI는 `<전체 IRI>` 표기(§1 — PN_LOCAL 비허용 문자 `/`·`@` 포함).
- **alias IRI**(T2-2) = djr 기저 + `alias-<공간>-<번호>`(예 `djr:alias-rule-486`) — PN_LOCAL 안전이라 접두 축약형을 쓴다. `#`는 fragment 금지 문자라 IRI 에 넣지 않고, **정본 문자열은 `djr:aliasText`**(동결 v2 문법 `rule#N` — 비한정 «#N»·전치 0 금지)가 진다. 대장 파일은 `wiring/aliases.ttl`(문서 횡단 선언 — `rules/`는 render manifest 대조로 exit 2). 함수성·해소·문법은 `ontology_structural_check.py` ⑥·⑥′·⑥″가 fail-closed 로 문다.
- **djr:headingSnapshot = 채번 시점 헤딩 라인 전체 verbatim**(`### 6.2 …` — 레벨 포함, 렌더가 헤딩 라인을 재생성할 수 있게). 채번 후 불변 — 현행 헤딩은 djr:headingCurrent(개정 시 갱신). **djr:parentSection** 채택(절 트리 질의 — §7 어휘 개정 절차 경유, 안정화 선언 전 편입).

## 15. 이관 공정 절차서 (블루프린트 §4-2 실장 — 파일럿이 첫 실증)

- **⓪ preflight**(§13) → **① LLM 블록 분해**(kind 5종 — norm/prose/code/table-row/checklist-item·순서 채번·§13 스팬 소유 준수) → **② 규범 블록 식별 + Work 채번**(ISSUED — 시작값 R-0001·경로 필드=`rules/<문서 키>.ttl`) **+ 초기 Expression 채번**(`<djr IRI…R-NNNN@이관일>`·`djr:revision 1`·`prov:specializationOf`→Work·Work의 `djr:currentExpression`→Expression — 개정 1 3노드형) → **③ wiring 저작**(§16) → **④ Section 노드**(headingSnapshot·headingCurrent·sectionOwner·parentSection)·Document 노드 → **⑤ 4단 게이트+SHACL+계수 기대표 갱신**(기대표 diff가 이관 절의 블록 계수와 대조 가능해야 — 무규율 갱신 금지, diff 사유 병기) → **⑥ 렌더 라운드트립 대조**(마커 제거 후 byte 잔차 0) → **⑦ 검수 패키지**(저작 근거 포함).
- **문서 키**: 센서스 manifest(`corpus-manifest.tsv`)의 doc_key 열이 정본 — 스킬 `<스킬명>-skill`/`<스킬명>-final`·에이전트 `agent-<이름>`·커맨드 `command-dddjango`.
- **재진술**: 정본 1곳만 Work 승격 + 사본 블록에 `djr:restates`. 상대 블록이 **미이관 절(그래프 밖)이면 restates 생략 + 원장 비고에 유예 기록**(T3 소급 연결) — 파일럿 실물(ninja §6.2↔§2.2 축자 쌍)이 이 케이스.
- **공정 기록**: 전 이관 절의 게이트 반송·수리 루프 횟수·검수 반송을 gate-report 로그로 집계 — T2 CNL 결정 재료(블루프린트 §4-6).

## 16. wiring 저작 규약 (기계 참조가 아니라 판단 작업 — 저작 근거 의무)

- **enforcedBy 저작 = 4원 종합 판단**: ① 규범 문면의 역할명(«schema checker» 등) ② 검사기 docstring의 § 인용 ③ P0 «커버» 판정 ④ registry #N 대응. **근거를 검수표에 기록**(무근거 배선 금지). 검사기 비커버 규범은 위임 기본값 표의 Agent로 `djr:delegatedTo`(임의 저작 금지 — 기본값 이탈은 문면 근거 필요·**역도 성립: 담당 검사기의 문면·docstring 근거가 있는데 기본값으로 도피하면 오배선**).
- **배선 전 로스터 전수 실독 의무**(T1 적대 검증 L-F 교훈 — 2026-08-19): ②는 «아는 검사기 몇 종의 docstring»이 아니라 **check-*.py 27종 로스터 전수의 docstring 선두**를 배선 작업 전에 한 번 실독하는 것이다. T1 파일럿 저작이 8종만 참조해 9종의 정확한 담당(response-schema-bypass·choices-literal-consumption·synthetic-infra-exc·transaction-boundary·usecase-dto-placement·app-container·business-vocabulary·db-table·context-isolation)을 놓친 것이 실증 — 독립 리뷰(codex 4레인)가 21건을 교정했다.
- **역할명→검사기 파일명 매핑 표**(E07 추론의 실측 승격 — docstring·marker 발행 실측 2026-08-19):

| 문면 역할명·marker (ninja §6.2) | 실물 검사기 |
|---|---|
| «schema checker» | `check-error-centralization.py`(FrameworkErrorSchema schema contract backstop) |
| «controller checker» / marker `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`(발행) | `check-api-error-controller-contract.py` |
| «OpenAPI checker» / marker `RESOLVED_DYNAMIC_ERROR_SHAPE_ANALYSIS`(소비·발행) | `check-openapi-error-declaration.py`(+ `check-error-centralization.py` 소비) |

- **위임 기본값 표**(문서군→기본 Agent — rule-owner-map ⓓ 관례 준용: human 판정 전건이 discipline-reviewer였음):

| 문서군 | 기본 delegatedTo | 근거 |
|---|---|---|
| architecture-ddd | `agent-design-review-ddd`(설계 시점 규범)·`agent-discipline-reviewer`(구현 시점 규범 — §3.2 등) | 파이프라인 Phase 1/2 판정 주체 분리 |
| architecture-db / architecture-api | `agent-design-review-db` / `agent-design-review-api` | 동상 |
| discipline-cleancode·discipline-tdd·discipline-houserules·implementation-* | `agent-discipline-reviewer` | rule-owner-map ⓓ 유일 관례 |
| command+agents(절차 층) | `command-dddjango`(Coordinator) | 절차 준수 판정 주체 — rule-owner-map 스코프 밖 |

- **`wiring/registry.ttl` 신설**: Checker 27종+Agent 개체의 공유 선언(문서 횡단 개체 — 문서별 wiring 파일의 중복 선언 금지).
- **게이트 ④ 병합 확장(T0 개작)**: ④(훅 경유 포함)의 데이터 그래프 = 변경 파일 + vocab + wiring + **rules 전량**(교차 참조 restates·aliasFor의 위양성 red 해소 — §2 문면 동반 갱신됨). 성능은 파일럿 규모에서 무시 가능 — T3 규모에서 재평가.
- **셰이프 개정(§7 절차 경유 — 안정화 선언 전)**: BlockShape의 djr:text = `sh:or(rdf:langString·xsd:string)` + 저작 규약: norm/prose/checklist=`@ko`·code/table-row=`xsd:string`(kind↔datatype 정합은 SPARQL 검사 — `ontology_structural_check.py`, T1-6).

## 17. 롤백 절차 — 렌더본의 산문 정본 재선언 (블루프린트 안전망 실장 — 2026-08-19 리허설 실증)

절 단위 «한 걸음 복귀». 복귀 스위치 = rules 정본의 `djr:sectionOwner` 한 트리플.

1. **복귀(재선언)**: ① rules 정본에서 해당 Section의 `djr:sectionOwner`를 `djr:owner-graph`→`djr:owner-prose`로 변경(게이트 통과) — 렌더·동기 검증 스코프에서 즉시 제외 ② 코퍼스 파일에서 그 절의 마커 라인 제거(마커 제거본 == 이관 시점 원문 — byte 등가가 이를 보장) ③ 원장에 owner=prose 재선언 행 append(현재 해시·사유). Work·블록 노드는 tombstone으로 존치(ISSUED 결번 없음 — E6).
2. **재이관(왕복)**: 역순 — sectionOwner 되돌림(게이트) → `ontology_render.py --apply` → 원장 owner=graph 행 append. 채번 재발행 없음(기존 Work 재사용).
3. 왕복 전후 `verify-ontology` 전체 green이어야 한다. 원장의 append-only 이력이 리허설/롤백 궤적의 증빙이다(2026-08-19 s051-8 왕복 리허설 — LEDGER rollback-rehearsal 행 2개).
- T1 전면 중단 시: 위 절차를 전 이관 절에 적용 + Makefile verify 의존에서 verify-ontology 한 줄 삭제(t0-plan §7) — 센서스·원장·도구는 무해 존치.
