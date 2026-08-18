# Q6 — RDFS/OWL 추론 층의 실효: 규칙 적용성 판정에 추론이 실제로 주는 가치

- 조사일: 2026-08-18
- 레인: Q6 (온톨로지 v3 리서치)
- 조사 방법: 웹 조사(실도구 문서·저장소·논문·운영 사례 중심, 마케팅 문서 배제)

---

## 1. 핵심 발견

1. **dddjango가 필요로 하는 «규칙 상속»(레이어·계층에 걸린 규칙의 하위 전파)은 RDFS 수준의 전이 폐포(subClassOf 전이 + 타입 전파)만으로 충족되며, 이 수준은 OWL 추론기 없이 SPARQL 프로퍼티 패스(`rdf:type/rdfs:subClassOf*`)로 완결된다.** 프로퍼티 패스가 못 하는 것(도메인/레인지 유발 타입 추론, 복합 OWL 공리)은 dddjango의 규칙 적용성 판정에 필요하지 않다.
2. **SHACL은 규칙 상속을 표준 의미론으로 이미 내장하고 있다.** `sh:targetClass`와 `sh:class`는 «SHACL instance» 정의에 따라 데이터 그래프 안의 `rdfs:subClassOf` 체인을 스스로 따라간다 — 즉 상위 클래스에 붙인 셰이프는 추론기 없이도 하위 클래스 인스턴스에 자동 적용된다. 단, **클래스 계층 트리플이 데이터 그래프에 물리적으로 함께 있어야 한다**는 전제가 붙는다.
3. **SPARQL 엔테일먼트 리짐(entailment regime)은 W3C 스펙(1.1, 1.2 개정 진행)은 존재하지만 실무 구현은 스펙 그대로가 아니다.** 실제 스토어는 로드 시 머티리얼라이제이션(materialization, GraphDB)이나 쿼리 리라이팅(Stardog) 또는 하이브리드로 구현하며, rdflib(Python)에는 엔테일먼트 리짐 지원 자체가 없다. «리짐을 켠다»는 설계는 이식성이 없는 가정이다.
4. **OWL DL 추론기 생태계는 대부분 유기(abandoned) 상태다.** 2023년 전수 조사(95종)에서 «사용 가능하며 유지되는 것»은 25종뿐. HermiT는 마지막 커밋 6년 이상 경과, Pellet은 사망(포크 Openllet만 부분 유지), FaCT++도 방치. 활발히 유지되는 것은 ELK(OWL 2 EL 한정), Konclude, Whelk 정도이며, 오래된 Java 의존성 부패(javax.xml.bind 제거 등)로 실행 자체가 실패하는 사례가 보고된다.
5. **Python 스택의 owlrl(OWL 2 RL 전방 체이닝)은 소규모 그래프에서는 실용적이지만 성능 절벽이 검증돼 있다.** 벤치마크에서 Rust 구현 reasonable 대비 38배 느리고, 학술 평가에서는 대형 그래프에 대해 180분 내 종료 실패 사례가 있다. pySHACL은 owlrl을 이용한 사전 추론(`inference='rdfs'|'owlrl'`)을 내장 옵션으로 제공한다.
6. **추론이 실효를 검증받은 실무 패턴은 «질의 시 추론»이 아니라 «저작·CI 시점의 검증 + 릴리스 머티리얼라이제이션»이다.** OBO 생태계의 ROBOT `reason` 명령이 대표 사례: ELK로 분류(암묵 subClassOf 계산)·unsatisfiable 클래스 검출·의도치 않은 동치 검출을 CI에서 돌리고, 추론된 공리를 `--annotate-inferred-axioms`로 표시해 릴리스 산출물에 머티리얼라이즈한다. 소비 시점에는 추론기가 없다.
7. **«왜 이 규칙이 걸렸는가»의 설명 가능성은 도구 계열에 따라 극단적으로 갈린다.** DL 계열은 저스티피케이션(justification, 함의를 성립시키는 최소 공리 집합) 도구가 성숙(Protégé Explanation Workbench, Evee). 상용 스토어도 지원(GraphDB proof 플러그인 — 어떤 룰이 어떤 전제로 발화했는지, Stardog `reasoning explain` — 최소 단언 집합 출력). 반면 **owlrl은 유래(provenance)를 전혀 남기지 않는다** — Python 스택에서 설명 가능성은 자작해야 한다.
8. **추론 도입의 최대 비용은 성능이 아니라 저작 규율이다.** OWA(열린 세계 가정)와 «domain/range는 제약이 아니라 추론 유발 장치»라는 의미론이 저작자 기대와 어긋나는 것이 수십 년째 반복 검증된 최다 실수 축이다(Rector et al.: 보편/존재 한정 혼동, OWA 오해, domain/range 오해). 예: `hasAge`의 도메인을 Person으로 선언하면 고양이 Felix에 나이를 달는 순간 추론기가 Felix를 Person으로 «추론»한다 — 오류 보고가 아니라 조용한 오염이다.
9. **학계의 최신 방향도 «검증 시 추론기 제거»다.** 2026년 Artificial Intelligence지 논문이 온톨로지 함의를 SHACL 셰이프로 컴파일(리라이팅)해 표준 SHACL 검증기만으로 온톨로지-인지 검증을 수행하는 기법을 제시 — 추론을 저작 파이프라인 안으로 밀어 넣는 방향이 주류화되고 있다.
10. **추론기 성능 자체는 dddjango 규모에서 논점이 아니다.** ELK는 SNOMED CT 30만 클래스를 노트북에서 4초 내에 분류한다. 클래스 수십~수백 규모에서는 어떤 추론기든 순간에 끝난다. 진짜 논점은 운영 복잡도(Java 의존·유지보수 위험)·디버깅 가능성·저작 규율 비용이다.

---

## 2. 실무 증거 (사례별)

### 사례 A — SHACL 타깃 의미론: 추론기 없는 규칙 상속 (W3C SHACL Recommendation)

SHACL 스펙의 «SHACL instance» 정의: 노드 n의 SHACL 타입은 «그래프 안의 rdf:type 값들과 그 값들의 SHACL 슈퍼클래스들»이다. 따라서 `sh:targetClass ex:Layer`인 셰이프는 `ex:DomainLayer rdfs:subClassOf ex:Layer`가 데이터 그래프에 있으면 DomainLayer 인스턴스에도 적용된다. `sh:class` 제약도 같은 정의를 쓴다. 스펙은 명시적으로 «full RDFS inferencing is not required»라 하며, 필요한 subClassOf 트리플이 데이터 그래프에 존재하는 것만 요구한다. **규칙 상속이라는 dddjango의 1차 요구는 SHACL 표준 의미론 그 자체로 해결된다.**

### 사례 B — OBO/ROBOT: CI 시점 추론의 검증된 운영 패턴

바이오 온톨로지 생태계(GO, Uberon, Mondo 등 수백 개 온톨로지)의 표준 빌드 도구 ROBOT의 `reason` 명령은 (1) 논리 검증 — 비일관성·unsatisfiable 클래스 검출, `--equivalent-classes-allowed none`으로 의도치 않은 클래스 동치 검출, (2) 자동 분류 — 추론된 subClassOf를 릴리스 산출물에 단언(머티리얼라이즈)하는 두 기능을 수행한다. 기본 추론기는 ELK이고 HermiT·Whelk 등을 선택할 수 있다. `--annotate-inferred-axioms true`로 추론 유래를 공리에 주석으로 남기고, unsatisfiable 발생 시 `-D`로 디버깅용 최소 온톨로지를 추출한다. **추론은 저작·CI 단계의 품질 게이트로 쓰이고, 소비자는 머티리얼라이즈된 산출물을 추론기 없이 읽는다** — 이것이 10년 이상 대규모로 운영 검증된 유일한 «추론의 실효» 패턴이다.

### 사례 C — 추론기 생태계 전수 조사 (Abicht, "OWL Reasoners still useable in 2023", arXiv:2309.06888)

95종 전수 조사 결과: 사용 가능+유지 25종, 파일 자체가 없는 것 20종. HermiT는 마지막 커밋 6년+로 «abandoned»(Protégé 5.6.1 동봉본으로만 연명), Pellet은 두 저장소 모두 방치(2011/2017)에 Ubuntu 20.04에서 컴파일 오류로 실행 실패, FaCT++는 2017년 이후 방치, jFact는 2016년이 마지막 릴리스. 유지되는 것은 ELK(문서·병렬화 우수), Konclude(2021 v0.7.0), Openllet(2023 기준 유지), Whelk(2022 v1.1.2). Java 1.5 시절 의존성, 제거된 javax.xml.bind, 접근 불가 Maven 저장소 등 **빌드 부패가 광범위**하다. 10개 이상의 PR이 방치된 저장소가 다수.

### 사례 D — Python 스택의 실측: owlrl vs reasonable

- rdflib 공식 토론(#1882): Brick 빌딩 모델 머티리얼라이제이션 워크로드에서 Rust 기반 reasonable이 AllegroGraph 대비 7배, **owlrl 대비 38배 빠름**.
- 학술 성능 평가에서 rdflib+owlrl 조합이 대형 워크로드에서 **180분 내 종료 실패**.
- owlrl 저장소 스스로 «OWL RL이 정의하는 모든 트리플로 그래프를 확장하는 단순 구현»이며 일반 OWL Restriction 일부는 다루지 못함을 명시.
- pySHACL은 `inference` 파라미터('rdfs'/'owlrl'/'both'/'none', 기본 none)로 owlrl 사전 추론을 내장하고, `ont_graph`로 온톨로지 정의를 데이터 그래프에 «접종(inoculate)»하는 기능을 제공. 원격 SPARQL 그래프 모드에서는 그래프를 수정할 수 없어 추론이 통째로 비활성화된다 — 추론이 «데이터 그래프를 불려서» 작동한다는 구조적 증거.

### 사례 E — SPARQL 엔테일먼트 리짐의 실무 지원 현황

W3C SPARQL 1.1 Entailment Regimes는 RDF/RDFS/D/OWL RL 등 리짐을 정의하고 SPARQL 1.2에서 개정 중이나, 스펙 자체가 구현 기법을 규정하지 않는다. 실무 구현은: **GraphDB** — 로드 시 전방 체이닝 머티리얼라이제이션(RDFS/OWL RL/QL + 커스텀 룰셋, «total materialization»), **Stardog** — 질의 시 쿼리 리라이팅(RDFS/OWL DL·QL·RL·SL+SWRL), **Jena** — 사전 머티리얼라이즈된 추론 모델. owl:sameAs는 머티리얼라이즈하지 않는 하이브리드가 일반적. **rdflib는 엔테일먼트 리짐 미지원** — Python 파이프라인에서 «리짐»은 선택지가 아니며, 추론이 필요하면 명시적으로 그래프를 확장(owlrl)하거나 질의를 프로퍼티 패스로 쓰는 수밖에 없다.

### 사례 F — 프로퍼티 패스로 하는 «추론기 없는 추론»의 범위와 한계

실무 문서(ancisoft) 기준, 프로퍼티 패스로 처리 가능한 패턴: `rdfs:subClassOf+`/`*`(서브섬션 전이 폐포), `(owl:equivalentClass|^owl:equivalentClass)*`(동치 대칭·전이), `rdf:type/rdfs:subClassOf*`(타입 전파 — «Layer의 모든 인스턴스» 질의), rdfs:subPropertyOf 유사 패턴. 한계: owl:intersectionOf·owl:FunctionalProperty·역속성 같은 복합 공리는 불가, 새 트리플을 만들지 않으므로 매 질의마다 순회 비용 발생(소규모 그래프에서는 무시 가능, 대형 그래프에서 느려짐). 저자는 복잡 온톨로지에만 진짜 추론기(HermiT, RDFox, owlrl)를 권한다. **dddjango의 규칙 적용성 질의는 전부 «처리 가능» 목록 안에 있다.**

### 사례 G — 설명 가능성(«왜 걸렸나»)의 도구 지형

- **DL 계열**: 저스티피케이션(함의를 성립시키는 최소 공리 집합) 연구·도구가 성숙 — Protégé Explanation Workbench(정규·laconic 저스티피케이션 계산·비교), Horridge의 Protégé 4 함의 설명, Evee(누락된 함의 «왜 안 걸렸나»까지 설명하는 Protégé 플러그인). unsatisfiable 클래스·모순 디버깅의 표준 수단.
- **룰 기반 스토어**: GraphDB proof 플러그인 — 특정 문장이 «어느 룰이 어떤 전제와 매칭돼» 도출됐는지 질의로 노출(오픈 소스), provenance 플러그인으로 특정 네임드 그래프발 암묵 문장 추적. Stardog `reasoning explain` — 추론 성립에 필요한 최소 단언 집합을 사람이 읽을 수 있는 형식으로 출력.
- **Python owlrl**: 유래 기록 없음. 확장된 그래프에 원본과 추론 트리플이 구분 없이 섞인다. **설명 가능성이 필요하면 파이프라인이 직접 (a) 추론 전후 diff를 떠서 추론 트리플을 분리하고 (b) 규칙 상속처럼 규칙적인 추론은 유래를 재구성 가능한 형태(subClassOf 경로)로 한정해야 한다.**
- 온톨로지 QC에서의 추론 활용(Mungall의 디버깅 시리즈): disjointness 공리를 «트립와이어»로 심어 두면 추론기가 모델링 오류를 unsatisfiable로 표면화한다 — 추론의 가치가 «적용성 판정»보다 «저작 오류 검출»에서 크다는 실무 증언.

### 사례 H — 저작 규율 비용: OWA·domain/range의 반복 검증된 함정

- Rector et al.(맨체스터, OWL-DL 교육 실전 보고): 최다 오류는 ① 정보를 명시하지 않음(OWA에서 «말하지 않은 것»은 거짓이 아니라 미지), ② 존재/보편 한정 혼동, ③ domain/range를 DB 제약으로 오독. 
- domain/range는 위반을 보고하지 않고 **타입을 추론한다**: range가 Person인 속성을 고양이에 쓰면 고양이가 Person이 «된다». OWL 처리기는 minCardinality 1 미충족도 오류로 보고하지 않는다(«나중에 데이터가 올 수 있으므로») — 검증 의도에는 SHACL(닫힌 세계)이 맞고 OWL 공리는 부적합하다는 것이 SHACL 설계자(Knublauch)와 TopQuadrant의 공식 입장.
- OOPS!(OntOlogy Pitfall Scanner) 카탈로그가 40여 종의 저작 함정을 목록화 — domain/range 과소·과대 지정이 대표 항목. **추론을 켜는 순간 이 함정들이 «조용한 오염» 경로가 된다.**

### 사례 I — 분류가 진짜 필요해질 때의 선택지: ELK와 OWL 2 EL

ELK는 OWL 2 EL 프로파일 전용 consequence-based 추론기로, SNOMED CT(약 30만 클래스)를 노트북에서 4~5초에 분류한다. 병렬화 지원, Protégé 플러그인·독립 실행·라이브러리 3형태, 활발히 유지됨. 단 EL 프로파일 한정이라 데이터 프로퍼티 domain/range 등 일부 공리는 미지원(HermiT·Pellet과의 비교 평가에서 확인). **«암묵 서브섬션을 계산해야 하는»(= 클래스 정의로부터 계층 자체를 도출하는) 요구가 생기기 전에는 필요 없다.**

### 사례 J — 검증 시 추론기를 제거하는 리라이팅 (AIJ 2026, arXiv:2507.12286)

Horn-ALCHIQ 온톨로지의 함의를 «core universal model» 기반으로 SHACL 셰이프에 컴파일해, 수정 없는 표준 SHACL 검증기로 온톨로지-인지 검증을 수행. 최악 복잡도 EXPTIME-complete이지만 데이터 복잡도는 PTIME. 연구 수준이지만, **«추론을 저작 시점에 셰이프로 구워 넣고 소비 시점은 순수 SHACL»이라는 아키텍처 방향의 학술적 뒷받침**이다.

---

## 3. dddjango 설계에 주는 함의

1. **추론 층은 «채택하지 않는 것»을 기본값으로 하라.** dddjango의 규칙 적용성 판정(레이어·계층 규칙의 하위 전파)은 ① 정본 그래프에 `rdfs:subClassOf`를 명시 단언하고 ② SHACL 타깃 의미론(자동 서브클래스 적용)과 SPARQL 프로퍼티 패스(`rdf:type/rdfs:subClassOf*`)로 소비하면 완결된다. 판별 기준을 명문화하라: **전이 폐포·타입 전파 = 프로퍼티 패스로 충분 / 클래스 정의로부터의 분류·일관성 검사 = 추론기 필요** — dddjango는 전자다.
2. **추론기를 쓴다면 ROBOT 패턴으로 위치를 고정하라: 저작·CI 시점만.** 온톨로지 개정 CI에서 (a) unsatisfiable·의도치 않은 동치 검출(트립와이어 disjointness 포함), (b) 필요 시 추론된 subClassOf의 머티리얼라이제이션을 수행하고, 파이프라인 에이전트(소비자)는 머티리얼라이즈된 정본을 추론기 없이 읽는다. 질의 시 추론(엔테일먼트 리짐)은 rdflib에 존재하지도 않고 이식성도 없으므로 설계에서 배제.
3. **머티리얼라이즈하는 트리플에는 유래를 강제하라.** owlrl은 유래를 남기지 않으므로, 추론 전후 diff로 추론 트리플을 분리해 별도 네임드 그래프(예: `:inferred`)에 두거나 ROBOT식 주석(`is_inferred true`)을 달아라. 이것이 없으면 «왜 이 규칙이 걸렸는가» 질문에 답할 수 없고, 증분 갱신(원본 수정 시 폐포 재계산)도 불가능해진다. 규칙 적용성의 설명은 «subClassOf 경로 출력»(프로퍼티 패스 질의로 재구성 가능)으로 충분하도록 추론 범위를 좁게 유지하는 것이 최선의 설명 가능성 전략이다.
4. **저-공리(low-axiom) 저작 프로파일을 하우스룰로 동결하라.** 계층은 `rdfs:subClassOf`만, 제약 의도는 전부 SHACL로, `rdfs:domain`/`rdfs:range`/`owl:equivalentClass`/`owl:inverseOf` 같은 «추론 유발» 공리는 금지 또는 심의 항목으로 지정. 이는 OWA 함정(조용한 타입 오염)을 원천 차단하고, 프로퍼티 패스만으로 의미론이 닫히게 한다. LLM 저작자는 인간 초보자와 같은 오류 축(domain/range를 제약으로 오독)을 밟는다고 가정해야 한다.
5. **Python 스택을 유지하라.** rdflib + pySHACL(+ 필요 시 `inference='rdfs'`)로 충분하다. dddjango 규모(규범 3,217문장·606절 → 수천~수만 트리플)에서는 owlrl조차 성능 문제가 없으며, Java DL 추론기(HermiT 등)는 생태계 유기화·빌드 부패 위험 때문에 도입하지 않는 것이 안전하다. 훗날 분류가 필요해지면 ELK(활발 유지, EL 한정)를 CI 단계에만 붙인다.
6. **SHACL 셰이프가 서브클래스에 자동 적용된다는 사실을 «규칙 상속의 공식 메커니즘»으로 삼되, 전제 조건을 파이프라인이 보장하라.** 검증·질의에 쓰이는 데이터 그래프에는 클래스 계층 트리플이 반드시 동봉돼야 한다(pySHACL `ont_graph` 접종 또는 정본 그래프 병합을 빌드 단계에서 강제). 이 전제가 깨지면 규칙이 오류 없이 조용히 미적용된다.

---

## 4. 위험·한계

1. **침묵 미적용 위험**: SHACL 타깃 상속과 프로퍼티 패스 모두 «데이터 그래프에 subClassOf가 있어야» 작동한다. 온톨로지와 인스턴스 데이터를 분리 배포하고 병합을 빠뜨리면 상위 규칙이 하위에 적용되지 않은 채 검증이 «통과»한다 — 오류가 아니라 누락이므로 발견이 어렵다. 병합 보장 + «상속 적용 수» 회귀 검사로 방어해야 한다.
2. **owlrl 성능 절벽**: 순수 Python 전방 체이닝은 그래프가 커지면(수십만 트리플급) 38배 격차·180분 초과가 실측된 수준으로 느려진다. dddjango 규모에서는 무관하지만, 그래프에 코드베이스 인스턴스까지 넣는 확장을 하면 reasonable(Rust) 등으로의 교체 경로를 준비해야 한다.
3. **DL 추론기 의존은 유지보수 부채**: HermiT·Pellet·FaCT++는 사실상 유기 상태이고 Java 의존성 부패로 실행 실패 사례가 보고된다. 이들을 파이프라인에 넣으면 수년 내 빌드가 깨질 확률이 높다. 유지되는 것은 ELK·Konclude·Whelk 정도이며 각각 표현력 제약이 있다.
4. **OWA 의미론 함정은 추론을 켜는 순간 활성화된다**: domain/range·equivalentClass가 들어간 그래프에 owlrl을 돌리면 저작자 의도와 다른 타입·동치가 조용히 머티리얼라이즈돼 규칙 적용성 판정을 오염시킬 수 있다. 저-공리 프로파일을 강제하지 않으면, LLM이 «그럴듯한» OWL 공리를 추가하는 것 자체가 오염 벡터가 된다.
5. **설명 가능성은 공짜가 아니다**: 저스티피케이션 도구는 DL/Java 세계(Protégé)와 상용 스토어(GraphDB·Stardog)에 있고 Python owlrl에는 없다. 추론 범위를 넓힐수록 «왜»의 재구성 비용이 커지므로, 설명 요구가 있는 한 추론 범위는 프로퍼티 패스로 재현 가능한 수준(서브섬션 전이)에 묶어 두는 것이 구조적으로 안전하다.

---

## 5. 출처 URL 전체 목록

1. https://www.w3.org/TR/shacl/#targets — W3C SHACL Recommendation: 타깃·SHACL instance 정의
2. https://spinrdf.org/shacl-and-owl.html — SHACL and OWL Compared (Knublauch)
3. https://learn.topquadrant.com/webinar-owl-vs-shacl — TopQuadrant: OWL vs SHACL
4. http://robot.obolibrary.org/reason.html — ROBOT reason 명령 문서
5. https://arxiv.org/abs/2309.06888 — Abicht, "OWL Reasoners still useable in 2023"
6. https://ar5iv.labs.arxiv.org/html/2309.06888 — 위 논문 HTML판(세부 수치)
7. https://github.com/RDFLib/OWL-RL — owlrl 저장소
8. https://github.com/RDFLib/rdflib/discussions/1882 — rdflib 토론: reasonable vs owlrl 성능(38배)
9. https://github.com/gtfierro/reasonable — reasonable(Rust OWL 2 RL) 저장소
10. https://github.com/RDFLib/pySHACL — pySHACL: inference 파라미터·ont_graph
11. https://www.w3.org/TR/sparql11-entailment/ — SPARQL 1.1 Entailment Regimes
12. https://www.w3.org/TR/sparql12-entailment/ — SPARQL 1.2 Entailment Regimes(개정)
13. https://www.w3.org/wiki/SparqlImplementations — SPARQL 구현 목록(W3C Wiki)
14. https://graphdb.ontotext.com/documentation/11.4/inference.html — GraphDB 추론(머티리얼라이제이션) 문서
15. https://graphdb.ontotext.com/documentation/10.0/proof-plugin.html — GraphDB proof 플러그인
16. https://docs.stardog.com/inference-engine/ — Stardog 추론 엔진(쿼리 리라이팅)
17. https://docs.stardog.com/stardog-cli-reference/reasoning/reasoning-explain — Stardog reasoning explain
18. https://www.ancisoft.com/blog/using-sparql-for-limited-rdfs-and-owl-reasoning/ — SPARQL 프로퍼티 패스로 하는 제한적 RDFS/OWL 추론
19. https://ceur-ws.org/Vol-401/iswc2008pd_submission_47.pdf — Horridge, Explanation of OWL Entailments in Protégé 4
20. https://www.semantic-web-journal.net/content/owl-explanation-workbench-toolkit-working-justifications-entailments-owl-ontologies — OWL Explanation Workbench
21. https://arxiv.org/pdf/2308.07294 — Evee: 누락 함의 설명(Protégé 플러그인)
22. http://owl.cs.manchester.ac.uk/research/explanation/ — 맨체스터대 Explanation in OWL
23. https://douroucouli.wordpress.com/2018/08/03/debugging-ontologies-using-owl-reasoning-part-1-basics-and-disjoint-classes-axioms/ — Mungall, 추론 기반 온톨로지 디버깅 1부
24. https://douroucouli.wordpress.com/2018/09/04/debugging-ontologies-using-owl-reasoning-part-2-unintentional-entailed-equivalence/ — 같은 시리즈 2부(의도치 않은 동치)
25. https://douroucouli.wordpress.com/2020/09/04/the-open-world-assumption-considered-harmful/ — Mungall, OWA Considered Harmful
26. https://www.cs.man.ac.uk/~horrocks/Teaching/cs646/Papers/ekaw-experience-with-owl-rector-et-al-final.pdf — Rector et al., OWL-DL 공통 오류 실전 보고
27. https://oops.linkeddata.es/catalogue.jsp — OOPS! 온톨로지 함정 카탈로그
28. https://www.w3.org/TR/owl2-primer/ — OWL 2 Primer(domain/range 추론 의미론)
29. https://github.com/liveontologies/elk-reasoner/wiki/Introduction — ELK 소개(SNOMED 수 초 분류)
30. https://www.uni-ulm.de/fileadmin/website_uni_ulm/iui.inst.090/Publikationen/2012/KazKroSim12ELK_TR.pdf — ELK 기술 보고서
31. https://github.com/IHTSDO/snomed-owl-toolkit — SNOMED CT OWL Toolkit(운영 사용)
32. https://dmkg-workshop.github.io/papers/paper2861.pdf — OWL 2 DL 추론기 성능 평가(소규모 온톨로지 비교)
33. https://arxiv.org/abs/2507.12286 — SHACL Validation in the Presence of Ontologies(리라이팅, AIJ 2026)
34. https://arxiv.org/pdf/1402.0576 — Optimizing SPARQL Query Answering over OWL Ontologies(리라이팅 vs 머티리얼라이제이션)
