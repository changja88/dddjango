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
- 게이트 ④의 데이터 그래프 = **변경 파일 + vocab/*.ttl + wiring/*.ttl 병합**(파일 단독 검증 금지 — SHACL 대상 선정·sh:class가 데이터 그래프 안의 subClassOf 경로 기준).
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
- T1 게이트에서 어휘 v1 재심·안정화 선언(§7 안정화 조항)과 함께 최종 봉인.
