# Q1 — SHACL 실전 운용: CI·커밋 게이트 패턴, 검증기 선택, 셰이프 설계, 함정

조사일: 2026-08-18 · 레인: Q1 · 조사 방법: 웹 검색 + 1차 문서·저장소·논문 실독

## 1. 핵심 발견

1. **CI 게이트로서의 SHACL은 이미 검증된 실무 패턴이다.** GitHub Actions 마켓플레이스에 pySHACL 기반 액션이 존재하고(HIT Ontology 등 실사용), ETSI SAREF는 GitLab CI에서 표준 규격(TS 103 673) 준수를 SHACL+SPARQL로 게이트하며, Brick Schema는 아예 정본을 OWL에서 SHACL로 전환했다. exit code(0=적합, 1=위반)로 게이트하는 관례가 표준화되어 있다.
2. **검증기 3종(pySHACL·Apache Jena·TopBraid)은 코어 스펙 합치도가 높지만 성능 격차가 크다.** 2026년 벤치마크(133 테스트 케이스)에서 Jena가 파일당 평균 1,024ms로 pySHACL(4,315ms)보다 4.2배 빠르고 분산도 작았다. 단 Jena는 SHACL-AF(고급 기능) 미지원, pySHACL이 스펙 커버리지(SHACL-AF·SHACL-JS·meta-SHACL)가 가장 넓다.
3. **수백~수천 트리플 규모(dddjango 규칙 그래프 규모)에서는 어느 검증기든 성능이 문제가 되지 않는다.** 벤치마크의 파일당 1~4초는 온톨로지 모듈 단위 측정치이고, 성능이 무너지는 임계는 수백만 트리플+OWL 추론 결합 지점이다(pySHACL-OWL이 대규모 그래프 폐포 계산에 12일 소요 사례).
4. **`sh:severity`는 게이트 설계의 핵심 축이지만 함정이 있다.** 스펙상 `sh:conforms` 판정에는 Violation만 반영된다는 보장이 없어(검증기마다 Warning 처리 상이), CI 게이트는 exit code가 아니라 **리포트 그래프를 SPARQL로 질의해 severity별로 직접 판정**하는 쪽이 안전하다. SHACL 1.2에서 severity 구분이 1급 기능으로 격상 중.
5. **오픈월드 RDF 위에서 사실상의 닫힌세계 검증은 `sh:closed` + `sh:ignoredProperties` + `sh:minCount` 조합으로 실무 표준이 확립**되어 있으나, RDFS/OWL 추론과 `sh:closed`는 구조적으로 충돌한다(서브클래스 인스턴스가 부모 셰이프의 closed 제약을 위반). 추론을 켠 채 closed 검증을 하면 안 된다.
6. **재귀 셰이프는 스펙이 의미를 정의하지 않아 구현별 동작이 다르다.** 재귀 지원 여부·방식이 검증기 재량이며, 재귀+부정 조합은 이론적으로도 NP-hard. 셰이프 간 순환 참조는 저작 규약으로 금지하는 것이 실무 정답이다.
7. **검증 리포트는 RDF 그래프(sh:ValidationReport)로 나오므로 기계 소비가 원리상 쉽지만**, focusNode가 블랭크 노드로 나오는 문제, 원본 Turtle 소스 라인으로의 역매핑 부재, `sh:resultAnnotation`이 pySHACL advanced 모드에서만 처리되는 점 등 실무 마찰이 있다.
8. **규칙 레코드 그래프의 무결성 검증 판정: 필수 필드·타입·카디널리티·참조 무결성은 SHACL Core+SPARQL 제약으로 충분히 감당 가능. 규칙 간 모순 검출은 "알려진 모순 패턴을 SHACL-SPARQL로 명시 코딩"하는 방식으로 부분 감당 가능하며, 일반적 논리 모순의 자동 발견은 SHACL의 능력 밖**(OWL 추론기나 전용 검사가 필요).

## 2. 실무 증거 (사례별)

### 2.1 검증기 선택지: 성숙도·성능·차이

**벤치마크 (TIO-SHACL, arXiv 2604.27359, 2026):** TMF Intent Ontology용 SHACL 스위트를 pySHACL 0.31.0, TopBraid SHACL 1.4.3, Apache Jena 5.2.0으로 교차 검증.

| 검증기 | 총시간(133케이스) | 파일당 평균 | 표준편차 | 상대 속도 |
|---|---|---|---|---|
| Apache Jena 5.2.0 | 136.1s | 1,024ms | 185ms | pySHACL 대비 4.2배 |
| TopBraid 1.4.3 | 174.4s | 1,312ms | 235ms | 3.3배 |
| pySHACL 0.31.0 | 573.9s | 4,315ms | 1,398ms | 기준 |

- pySHACL은 분산이 커서(재귀적 리스트 순회 모듈에서 5,000ms 초과) 예측 가능성이 낮다.
- **합치도:** 최종적으로 3종 100% 합의. 단 초기 실행에서 Jena가 32건을 위반으로 오판 — Jena 내장 VocabularyUsageShape가 함수 호출 위치의 리소스에 명시적 `rdf:type`을 요구했기 때문. 테스트 파일 36개에 타입 선언을 추가해 해소. **교훈: 검증기 교체·병행 시 내장 셰이프·기본 동작 차이가 판정 차이를 만든다.**
- pySHACL은 RDFS 추론을 켜면 잘못된 domain/range 배정이 발생해 **추론을 끄고 돌려야 했다**.
- Jena는 가장 빠르지만 SHACL-AF(커스텀 타깃 타입·구성 요소) 미지원 — SPARQL 제약 계층까지만.

**각 검증기 프로필:**

- **pySHACL (RDFLib):** 파이썬 생태계 표준. SHACL Core + SHACL-SPARQL + SHACL-AF(`-a`) + SHACL-JS(옵션) + **meta-SHACL(`-m`: 셰이프 그래프 자체를 SHACL-SHACL로 검증)**. 추론 모드 `none|rdfs|owlrl|both`. CLI exit code 0(적합)/1(위반)/2(런타임 오류)/3(미구현 기능) — CI 게이트에 바로 쓸 수 있는 구조. 전체 데이터그래프를 메모리에 복사해 작업하는 인메모리 설계라 대규모에 약함. `--max-depth`로 셰이프 중첩 깊이 제한 가능. `owl:imports` 처리(`do_owl_imports`)는 콘텐츠 협상 문제가 보고된 바 있음(issue #98). 리포트 출력: human/table/turtle/xml/json-ld/nt/n3.
- **Apache Jena SHACL:** `shacl validate --shapes S.ttl --data D.ttl` CLI. SHACL Core + SPARQL 제약. SHACL Compact Syntax(SHACL-C) 읽기/쓰기 지원. JVM 기동 비용이 있으나 검증 자체는 최고속. 트랜잭션 기반 검증·ValidationListener 등 프로그래매틱 통합 지점 제공.
- **TopBraid SHACL API:** Jena 기반 오픈소스(장기 유지보수, TopQuadrant). SHACL-AF 지원 폭이 넓다. `shaclvalidate` CLI는 Turtle 입출력만 받아 파이프라인 통합이 단순. PNNL이 파이썬 래퍼 `pytqshacl`을 유지(파이썬에서 JVM 검증기를 쓰려는 수요의 방증).
- **기타:** rdf-validate-shacl(JS/RDFJS, Zazuko), GraphDB·RDF4J의 저장소 내장 증분 검증(rsx 확장), eccenca Corporate Memory의 pySHACL 플러그인(상용 파이프라인 실사용).

### 2.2 CI·커밋 게이트 실전 패턴

- **GitHub Action `validate-shacl`(konradhoeffner/shacl):** pySHACL을 러너에 직접 설치해 여러 데이터 파일에 루프 실행. 위반을 GitHub 어노테이션(error/warning/info)으로 표면화하고 README 배지 제공. HIT Ontology 저장소가 실사용 — **"셰이프 파일 + 데이터 파일 목록"만 주면 되는 최소 구성이 커밋 게이트의 실전 최소 단위**임을 보여준다.
- **SAREF Pipeline (ETSI, ISWC 2023):** SAREF 본체+확장 온톨로지 전체를 ETSI Forge(GitLab) CI에서 검증. 기술규격 ETSI TS 103 673 준수를 SHACL·SPARQL 기반 검사로 게이트하고, 통과 산출물에서 포털 문서를 자동 생성. **"규범 문서를 저장소에 두고, 규격 준수를 CI가 기계 판정하고, 사람용 문서는 생성물"이라는 dddjango v3의 목표 구도와 동형의 선례.**
- **Brick Schema:** 정본 자체를 OWL에서 **SHACL 기반 온톨로지로 전환**(1.3 릴리스 계열). `py-brickschema`가 pySHACL로 건물 모델을 Brick 셰이프에 대해 검증(`brick_validate` CLI), SHACL을 추론(태그→클래스 유도)에도 사용. **"검증 가능성을 위해 정본 형식을 SHACL로 옮긴" 대표 사례.**
- **DCAT-AP (EU 데이터 포털 생태계):** SEMIC이 DCAT-AP 3.x에 SHACL 템플릿을 공식 동봉, EU Interoperability Test Bed와 data.europa.eu가 SHACL 검증기를 상시 운영. 독일 GovData.de는 자체 DCAT-AP.de 셰이프를 운영. **실패 교훈 2건:** ① 데이터 제공자들이 "내 데이터가 틀린 건지 셰이프가 틀린 건지" 구분하지 못하는 혼란이 반복 발생 — 셰이프 자체의 품질 관리·버전 관리가 운영 부담이 된다. ② 교환 맥락에 따라 같은 셰이프가 과잉 엄격해지는 문제(URI로 식별되는 조직에 이름 필수 규칙을 적용하면 오탐) — **셰이프는 교환 맥락별 프로필로 나눠야 한다**는 것이 DCAT-AP 3.0.1 개정의 핵심 교훈.
- **운영 관례 종합:** 리포트는 Turtle/JSON-LD로 받아 저장하고, 게이트 판정은 exit code 또는 리포트 그래프 SPARQL 질의로 수행. 검증 전 셰이프 그래프 자체를 meta-SHACL로 먼저 검증하는 2단 게이트(셰이프 lint → 데이터 검증)가 pySHACL `-m`으로 지원된다.

### 2.3 셰이프 설계 패턴

**sh:severity 운용:**
- 값은 `sh:Info`/`sh:Warning`/`sh:Violation`, 무선언 시 기본 Violation.
- 스펙상 적합성(`sh:conforms`) 계산에는 Violation만 반영 — 커스텀 severity나 Warning/Info는 conforms에 영향을 주지 않는 것이 표준이나, **일부 구현은 Warning도 부적합으로 처리하거나 승격 플래그를 제공**하므로 게이트에 쓰기 전 반드시 자기 검증기의 severity 처리를 확인해야 한다.
- Ontotext 실무 경험: 저장소 내장형 증분 검증(트랜잭션 거부형)에서는 severity 구분이 무용(위반이면 무조건 거부)하고, **배치 리포트 분석·CI 대시보드에서 유용**. dddjango처럼 CI 배치 게이트라면 severity 3단을 살릴 수 있다.
- SHACL 1.2는 "Violation이면 실패, Warning/Info는 통과-기록"이라는 CI 게이트 대 대시보드 구분을 1급으로 명문화하는 방향.
- 실전 패턴: severity 3단 + `sh:message`(사람용) + `sh:resultAnnotation`(기계용 메타데이터: 오류 코드·문서 링크·개선 힌트)의 3층 구성. 단 pySHACL에서 resultAnnotation은 `-a`(advanced) 없이는 **조용히 무시**된다.

**SHACL-SPARQL 제약:**
- `sh:sparql`로 임의 SPARQL을 셰이프에 내장 — 교차 참조 해소, 함수 인자 수 검사 등 Core로 불가능한 검사를 감당. TIO-SHACL이 실전에서 대량 사용.
- 반복되는 SPARQL 패턴은 SPARQL-based constraint component로 추상화해 파라미터화된 재사용 제약을 만드는 것이 권장 패턴.
- 한계: ① 임의 복잡도 쿼리는 성능 부담(Ontotext: "복잡한 SHACL 실행은 엔진에 부담"), ② 가독성 저하, ③ `$shapesGraph`/`$currentShape` 변수는 프로세서 간 이식성이 없어 스펙이 사용을 비권장, ④ SPARQL 내 OPTIONAL 미바인딩 변수는 메시지 토큰이 문자 그대로 남는(`{$var}`) 함정 — `COALESCE()`로 방어.
- SHACL 1.2에서 Node Expressions(2025-12 FPWD)·`sh:SelectExpression` 등으로 SPARQL 의존을 줄이는 방향이 진행 중이나 아직 Working Draft.

**닫힌세계 검증 기법:**
- RDF는 오픈월드이지만 SHACL 검증 자체는 "그래프에 있는 것만 본다"는 점에서 이미 사실상 닫힌세계 판정이다. 필수성은 `sh:minCount`, 잉여 속성 금지는 `sh:closed true` + `sh:ignoredProperties (rdf:type ...)`로 표현하는 것이 확립된 관용구.
- OWA/CWA 실무 휴리스틱: **도메인 모델링(무엇이 존재하고 어떤 관계가 가능한가)은 열린세계로, 파이프라인 운영 요건(처리되려면 무엇이 있어야 하는가)은 닫힌세계로** — 규제 데이터처럼 불완전성을 허용하지 않는 도메인에서 SHACL이 채택되는 이유.
- **함정: RDFS/OWL 추론과 `sh:closed`의 충돌**(TopQuadrant/shacl #101). 서브클래스 인스턴스가 추론으로 부모 클래스 인스턴스가 되는 순간, 부모 셰이프의 closed 목록에 없는 자식 속성이 전부 위반이 된다. 추론과 closed 검증은 함께 쓰지 않거나, 셰이프 상속을 수동으로 펼쳐야 한다.
- SHACL 규칙(SHACL-AF rules)으로 트리플을 생성하면서 동시에 검증하면 "검증 대상 그래프가 검증 기계 자신에 의해 변형되는" 순환이 생겨 OWA/CWA 어느 쪽 의미론이 지배하는지 불명확해진다 — 생성(추론)과 검증은 단계를 분리해야 한다.

### 2.4 검증 성능 — 수백~수천 트리플 규모 판정

- 성능 연구(VLDB 2024, Ke·Acosta 등)의 스케일 축은 1M → 4.5M → 34M 트리플이고, 여기서도 병목은 그래프 크기 자체보다 **OWL 추론 결합**이었다(pySHACL-OWL이 대형 데이터셋 폐포 계산에 12일, 검증은 7일 내 미완료). 순수 SHACL 검증은 1M 트리플급에서도 실용 범위.
- TIO-SHACL 수치(온톨로지 모듈 단위 파일당 pySHACL 4.3초, Jena 1.0초)가 dddjango 규모(규범 3,217문장 → 수천~수만 트리플 예상)의 상한 근사치다. **결론: 커밋 게이트 레이턴시 관점에서 pySHACL도 충분하고, 초 단위가 아까우면 Jena로 4배 단축 가능. 이 규모에서 성능은 검증기 선택 기준이 아니다.**
- 반복 실행 시 JVM 검증기는 기동 오버헤드가 지배적이므로(TIO-SHACL은 TopBraid를 싱글턴 캐시로 상쇄) 파일별 프로세스 기동 루프보다 일괄 검증이 유리.

### 2.5 알려진 함정 정리

1. **재귀 셰이프:** W3C 스펙이 재귀 검증의 의미를 정의하지 않고 구현 재량에 맡김. 재귀를 지원하지 않는 구현이 오류 신호 없이 통과시킬 수 있다는 상호운용성 문제가 공식 이슈로 제기됨(w3c/data-shapes #64). 학계는 supported/stable model semantics 등 여러 의미론을 제안했으나 표준화 미완, 재귀+부정 검증은 NP-hard. **실무 대응: 셰이프 간 순환 참조를 저작 규약으로 금지하고, pySHACL `--max-depth` 같은 안전장치를 병용.**
2. **OWL 어휘 혼용:** ① 추론 켜짐 여부에 따라 검증 결과가 달라진다(추론 없이는 암묵 데이터가 검증을 통과). ② pySHACL의 RDFS 추론이 잘못된 domain/range 배정을 만들어 벤치마크에서 추론을 꺼야 했던 사례. ③ `sh:closed`와 추론의 충돌(위 2.3). ④ OWL 제약(owl:Restriction)은 위반 검출이 아니라 추론용이라 "검증"으로 오용하면 통과해서는 안 될 데이터가 통과 — Brick이 OWL→SHACL로 전환한 이유가 이것. **실무 대응: 검증 경로에서는 추론 없음(`-i none`)을 기본으로, 추론이 필요하면 검증 전 단계에서 물질화(materialize)해 고정된 그래프를 검증.**
3. **리포트 기계 소비:** 리포트는 표준 어휘(sh:focusNode/resultPath/value/sourceShape/resultSeverity/resultMessage)의 RDF 그래프라 SPARQL 후처리가 정석. 함정: ① 익명(블랭크 노드) 셰이프가 sourceShape에 오면 리포트 항행성이 급락 — **모든 셰이프에 IRI를 부여**하는 저작 규약이 필요. ② 위반을 원본 Turtle 소스 라인으로 역매핑하는 표준 수단이 없어 IDE형 개발자 경험은 별도 도구 필요. ③ 블랭크 노드 `sh:annotationValue`는 결과 간 정체성이 공유되는 함정. ④ `sh:detail` 중첩 결과로 계층적 실패를 보존 가능.
4. **검증기 간 미묘한 차이:** 코어 합치도는 높으나 내장 셰이프·기본 추론·severity 처리·SHACL-AF 지원 폭이 다르다. **한 검증기를 정본 판정기로 고정**하고, 교체 시 골든 케이스로 회귀 검증하는 운영이 필요.
5. **셰이프 자체의 품질:** GovData.de 사례처럼 소비자가 데이터 오류와 셰이프 오류를 구분 못 하는 혼란이 실제 운영 비용. meta-SHACL로 셰이프 그래프의 형식 오류는 잡을 수 있으나 셰이프의 의미적 과잉·과소 엄격은 못 잡는다 — 셰이프에도 테스트(valid/invalid 골든 페어)가 필요하다. TIO-SHACL이 133케이스를 valid 67/invalid 66으로 구성한 것이 모범.

### 2.6 규칙 레코드 그래프 무결성 검증 — SHACL 감당 범위 판정

| 검사 항목 | 판정 | 수단 |
|---|---|---|
| 필수 필드(레코드 스키마) | **완전 감당** | sh:minCount/maxCount/datatype/nodeKind/pattern/in |
| 잉여 필드 금지 | **완전 감당** | sh:closed + sh:ignoredProperties |
| 제어 어휘·명명 규약 | **완전 감당** | sh:in/sh:pattern (온톨로지 설계 지침 검사에 실사용례 있음: 라벨·주석·명명 규약) |
| 참조 무결성(규칙→절, 규칙→검사기 ID 등) | **감당** | sh:class/sh:node로 대상 타입·형상 검증, "참조 대상이 그래프에 실존"은 SPARQL 제약이나 sh:node로 표현. 오픈월드에서 '존재'는 그래프 내 존재로 정의됨 — 정본 그래프가 자기완결이면 문제 없음 |
| 중복 ID·유일성 | **감당(SPARQL)** | sh:sparql로 동일 키 2건 검출. Core만으로는 불가 |
| 규칙 간 모순(예: 같은 대상에 필수+금지) | **부분 감당** | 모순의 '패턴'을 아는 경우에 한해 SHACL-SPARQL로 쌍별 검출 쿼리를 명시 코딩. 패턴 목록이 곧 검사 능력의 상한 |
| 일반 논리 모순의 자동 발견 | **불가** | SHACL은 추론기가 아님 — 여러 단계 추론 뒤에 드러나는 불일치는 검출 보장 없음(문헌 명시). OWL 추론(일관성 검사)이나 전용 분석 필요 |
| 통계적 품질·아웃라이어·의미적 중복 | **불가** | 데이터 품질 평가 적합성 연구(arXiv 2507.22305)가 명시한 SHACL 밖 영역 |

**종합 판정:** dddjango 규칙 레코드 그래프의 **구조적 무결성(스키마·참조·유일성)은 SHACL Core+SPARQL 제약으로 100% 게이트 가능**하다. **모순 검출은 "모순 패턴 카탈로그를 셰이프로 축적"하는 열거적 접근**이 현실적 상한이며, 이는 결정적 검사기 27종의 사상과 동형이다(패턴을 아는 위반만 잡는다). 의미 수준 모순은 SPARQL 질의 세트나 LLM 리뷰 등 별도 층이 필요하다.

## 3. dddjango 설계에 주는 함의

1. **2단 게이트 표준 채택:** ① meta-SHACL로 셰이프(스키마) 자체 검증 → ② 규칙 그래프 검증. pySHACL `-m` 한 플래그로 1단이 해결된다.
2. **검증기는 pySHACL을 정본 판정기로 고정**하는 것이 합리적 — dddjango 규모에서 성능 격차는 무의미하고, 파이썬 생태계 정합(파이프라인·기존 검사기와 동일 런타임), SHACL-AF·meta-SHACL 커버리지가 가장 넓다. 속도가 문제 되면 Jena CLI로 교체 여지를 남기되, 교체 시 골든 케이스 회귀가 필수(검증기 간 미묘한 차이 실증됨).
3. **추론 없음(`-i none`)을 검증 경로의 불변 규약으로:** 규칙 그래프는 자기완결 정본이므로 추론 의존 검증을 만들지 않는다. RDFS/OWL 추론이 필요해지면 검증 전 물질화 단계로 분리한다. 이 규약은 `sh:closed` 전면 사용을 가능하게 한다.
4. **셰이프 저작 규약 3종:** ① 모든 셰이프·제약에 IRI 부여(블랭크 노드 셰이프 금지 — 리포트 항행성), ② 셰이프 간 순환 참조 금지(재귀 미정의 의미론 회피), ③ severity 3단 + sh:message(한국어) + resultAnnotation(오류 코드·정본 절 링크) 3층 결과 설계. CI는 Violation만 실패 처리하되 판정은 exit code가 아닌 리포트 SPARQL 질의로.
5. **셰이프에도 골든 테스트:** 규칙 셰이프마다 valid/invalid 최소 페어를 저장소에 두고 CI에서 셰이프 회귀를 돌린다(TIO-SHACL 방식). GovData.de의 "셰이프 오류 vs 데이터 오류" 혼란을 예방하는 최소 장치.
6. **모순 검출은 SHACL-SPARQL 패턴 카탈로그로 시작:** 필수+금지 충돌, 동일 키 중복, 소유권(절→스킬) 중복 배정 같은 알려진 모순 축을 SPARQL 제약으로 열거 축적. 일반 모순 자동 발견을 SHACL에 기대하는 설계는 하지 않는다. SAREF·Brick 선례처럼 "정본은 그래프, CI가 기계 판정, 산문은 렌더"라는 전체 구도의 실현 가능성은 충분히 입증되어 있다.

## 4. 위험·한계

- **SHACL 1.2는 아직 Working Draft:** severity 1급화·Node Expressions 등 유용한 개선이 진행 중이나 표준 미완 — 1.2 전용 기능에 지금 의존하면 구현 미지원 위험. 1.0(2017 REC) 범위로 저작하는 것이 안전.
- **모순 검출 상한:** SHACL은 열거된 패턴만 잡는다. "온톨로지 도입으로 규칙 간 모순이 자동 검출되리라"는 기대는 과대 — 검출 능력은 패턴 카탈로그 투자에 비례한다.
- **셰이프 유지보수 비용의 이전:** 규칙이 늘수록 셰이프·골든 페어·모순 쿼리도 함께 자란다. DCAT-AP 생태계의 교훈처럼 셰이프 자체가 새로운 정본 자산이 되어 버전 관리·품질 관리 대상이 된다.
- **검증기 간 미묘한 비합치:** 내장 셰이프·추론 기본값·severity 처리 차이로 같은 그래프가 검증기에 따라 다르게 판정될 수 있음(Jena 32건 오판 사례). 정본 판정기 고정 없이는 판정 자체가 흔들린다.
- **개발자 경험 공백:** 위반→원본 소스 라인 역매핑, 셰이프 디버깅 도구가 산문 lint 대비 빈약. LLM 에이전트가 소비자인 dddjango에서는 리포트가 RDF라는 점이 오히려 유리하나, 사람이 개입하는 순간의 마찰은 별도 투자가 필요하다.

## 5. 출처 URL 전체 목록

1. https://github.com/RDFLib/pySHACL
2. https://github.com/RDFLib/pySHACL/blob/master/README.md
3. https://github.com/RDFLib/pySHACL/issues/226
4. https://github.com/RDFLib/pySHACL/issues/98
5. https://jena.apache.org/documentation/shacl/
6. https://github.com/TopQuadrant/shacl
7. https://github.com/pnnl/pytqshacl
8. https://github.com/zazuko/rdf-validate-shacl
9. https://arxiv.org/html/2604.27359 (TIO-SHACL: Comprehensive SHACL validation for TMF Intent Ontologies)
10. https://arxiv.org/pdf/2507.22305 (Is SHACL Suitable for Data Quality Assessment?)
11. https://arxiv.org/html/2606.03502v1 (A Community Survey on SHACL and ShEx)
12. https://www.vldb.org/pvldb/vol17/p3589-acosta.pdf (Efficient Validation of SHACL Shapes with Reasoning)
13. https://www.vldb.org/pvldb/vol15/p2284-ahmetaj.pdf (Magic Shapes for SHACL Validation)
14. https://proceedings.kr.org/2024/1/kr2024-0001-ahmetaj-et-al.pdf (Consistent Query Answering over SHACL Constraints)
15. https://arxiv.org/pdf/2112.01441 (A Review of SHACL: From Data Validation to Schema Reasoning)
16. https://arxiv.org/pdf/2507.08432 (xpSHACL: Explainable SHACL Validation)
17. https://link.springer.com/chapter/10.1007/978-3-030-00671-6_19 (Semantics and Validation of Recursive SHACL)
18. https://dl.acm.org/doi/10.1145/3366423.3380229 (Stable Model Semantics for Recursive SHACL)
19. https://arxiv.org/pdf/2108.13063 (Satisfiability and Containment of Recursive SHACL)
20. https://github.com/w3c/data-shapes/issues/64 (재귀 미지원 구현의 무신호 통과 문제)
21. https://www.w3.org/TR/shacl/ (SHACL 1.0 Recommendation)
22. https://www.w3.org/TR/shacl12-core/ (SHACL 1.2 Core WD)
23. https://www.w3.org/TR/shacl-sparql/ (SHACL 1.2 SPARQL Extensions)
24. https://www.w3.org/TR/2026/WD-shacl12-node-expr-20260108 (SHACL 1.2 Node Expressions FPWD)
25. https://www.w3.org/TR/shacl12-rules/ (SHACL 1.2 Rules)
26. https://w3c.github.io/shacl/shacl-af/ (SHACL Advanced Features 1.1)
27. https://www.ontotext.com/blog/shacl-ing-the-data-quality-dragon-i-the-problem-and-the-tools/
28. https://www.ontotext.com/blog/shacl-ing-the-data-quality-dragon-ii-application-application-application/
29. https://ontologist.substack.com/p/power-up-your-shacl-validation
30. https://github.com/TopQuadrant/shacl/issues/101 (RDFS 추론과 sh:closed 충돌)
31. https://github.com/TopQuadrant/shacl/issues/96 (sh:and 내 SPARQL 제약 미평가)
32. https://arxiv.org/pdf/2309.02723 (SHACL for regulatory requirements)
33. https://www.sciencedirect.com/science/article/pii/S0004370226000093 (SHACL validation in the presence of ontologies)
34. https://arxiv.org/pdf/2507.12286 (동일 주제 arXiv판)
35. https://github.com/marketplace/actions/validate-shacl (pySHACL GitHub Action, HIT Ontology 실사용)
36. https://iswc2023.semanticweb.org/wp-content/uploads/2023/11/142660133.pdf (SAREF Pipeline and Portal, ISWC 2023)
37. https://link.springer.com/chapter/10.1007/978-3-031-47243-5_8 (SAREF Pipeline Springer)
38. https://github.com/BrickSchema/py-brickschema (Brick의 pySHACL 검증·brick_validate)
39. https://github.com/BrickSchema/Brick/releases (Brick OWL→SHACL 전환)
40. https://brickschema.readthedocs.io/en/latest/validate.html
41. https://semiceu.github.io/DCAT-AP/releases/3.0.1/ (DCAT-AP 3.0.1 SHACL 템플릿·개정 교훈)
42. https://github.com/SEMICeu/DCAT-AP/issues/121 (셰이프 실무 혼란 사례)
43. https://github.com/GovDataOfficial/DCAT-AP.de-SHACL-Validation (GovData.de 운영 셰이프)
44. https://datosgobes.github.io/DCAT-AP-ES/en/validation/
45. https://www.itb.ec.europa.eu/shacl/any/upload (EU Interoperability Test Bed SHACL Validator)
46. https://data.europa.eu/mqa/shacl-validator-ui/ (data.europa.eu SHACL 검증기)
47. https://github.com/eccenca/cmem-plugin-pyshacl (상용 파이프라인의 pySHACL 플러그인)
48. https://arxiv.org/pdf/2605.10540 (SHACL-DS: ERA RINF Knowledge Graph 검증 연구)
49. https://ceur-ws.org/Vol-3759/workshop3.pdf (Enhanced and Scalable RDF Validation for Dataspaces)
50. https://book.validatingrdf.com/bookHtml011.html (Validating RDF Data — SHACL 장)
51. https://graphwise.ai/fundamentals/what-is-shacl/ (severity 기본값 등 기초)
52. https://volodymyrpavlyshyn.medium.com/open-world-vs-closed-world-modeling-owl-and-shacl-semantics-in-agda-f4601229630b (OWA/CWA 의미론 대비)
