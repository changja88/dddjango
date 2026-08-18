# Q5 — 그래프→산문 렌더: 온톨로지에서 사람이 읽는 문서를 생성하는 도구·관례

조사일: 2026-08-18 · 레인: Q5 · 조사 방식: 웹 실무 증거(도구 저장소·논문·운영 사례) 중심, 마케팅 문서 배제

---

## 1. 핵심 발견

1. **그래프→참조 문서 렌더러는 성숙한 생태계다.** Widoco(LODE 계열, 100+ 온톨로지 실사용), pyLODE(rdflib+Jinja/dominate 기반, HTML·markdown·asciidoc 출력), Ontospy, SHACL Play(SHACL 셰이프→HTML 문서·UML 다이어그램) 등이 실무에서 검증돼 있다. pyLODE는 OWL(OntPub)·SKOS(VocPub)·**SHACL 셰이프 그래프(Valpub)** 프로필까지 지원한다.

2. **순수 "그래프 전량→산문 전량" 렌더 사례는 발견되지 않았다. 모든 성숙 사례가 하이브리드다.** Widoco조차 Abstract·Introduction·Overview·Description 절은 사람 소유의 HTML 파일(sections 폴더)로 분리해 두고, 갱신 시 `-crossRef` 플래그로 **기계 생성 절(용어 교차참조·개요)만 재생성**하며 수기 절은 절대 덮어쓰지 않는다. 이것이 사실상의 업계 표준 패턴이다.

3. **"산문을 그래프 밖에 두는가"의 답은 '절 유형'으로 갈린다.** 실무 관례는 문서를 두 층으로 나눈다:
   - **용어 단위 산문(정의·사용 예·편집자 노트·정의 출처)** → 그래프 **안**의 주석 속성(annotation property) 리터럴로 저장: `rdfs:comment`, `skos:definition`, OBO의 IAO:0000115(textual definition)·IAO:0000112(example of usage)·IAO:0000116(editor note)·IAO:0000232(curator note)·definition source. schema.org는 `rdfs:comment` 안에 HTML 마크업 포함 산문까지 넣고 거기서 용어 페이지를 생성한다.
   - **서사 산문(튜토리얼·해설·설계 근거·장문 예제)** → 그래프 **밖** 수기 문서: DPV의 Primer/Guides, OBO/ODK의 mkdocs how-to·explanation 문서, schema.org의 developer 가이드, Widoco sections.

4. **렌더 문서의 품질은 렌더러가 아니라 그래프 주석의 완결성이 결정한다.** pyLODE는 명시적으로 "잘 문서화된 입력에서만 좋은 결과를 낸다(only producing good results for well documented inputs)"를 설계 철학으로 내건다. 이를 지키는 실무 장치는 **그래프 쪽 결정적 검사**다: ROBOT report의 missing_definition 등 수십 종 SPARQL 검사(OBO Foundry 원칙 FP-006 '모든 용어에 텍스트 정의')를 CI에서 강제한다.

5. **동기화(동기) 유지의 실무 해법은 CI 자동화다.** OnToology는 GitHub push 시 Widoco 문서+AR2DTool 다이어그램+OOPS! 평가를 자동 재생성한다(100+ 저장소 등록). ODK는 저장소 골격 생성 시 mkdocs 문서 템플릿과 워크플로 문서 자동 생성을 포함하고 GitHub Actions로 배포한다. 공통 규율: **렌더 산출물은 커밋 훅/CI 산물이며 사람이 직접 편집하지 않는다.**

6. **리터레이트 온톨로지 계열은 "어느 쪽도 우위가 없는 단일 소스" 접근이다.** Tawny-OWL(Clojure DSL)의 lenticular text는 같은 소스를 온톨로지 중심 뷰/문서 중심 뷰로 전환하며 저작하고, ELOT는 org-mode 플레인텍스트 하나가 온톨로지와 문서의 단일 소스다(headline=분류 계층, description list=공리·주석). ELOT는 ISO 23726-3 Industrial Data Ontology 등 수십 개 프로젝트에서 실사용됐고 기존 OWL을 ELOT org 형식으로 역변환하는 exporter(Java/OWLAPI)도 제공한다 — 즉 **산문 정본→리터레이트 단일 소스로의 이관 경로**가 도구로 존재한다.

7. **정본 방향의 반례도 있다: CIDOC CRM은 산문 스펙이 정본이고 RDF가 자동 파생물이다.** 커뮤니티 합의·해설 담론이 산문 중심인 표준은 산문 정본을 유지하며, RDF 인코딩은 별도 가이드라인(application profile)이 필요할 만큼 비자명한 변환으로 취급한다. 정본 방향은 이념이 아니라 **주 소비자가 누구인가**로 결정된다 — dddjango의 소비자는 LLM 에이전트이므로 그래프 정본 방향과 정합한다.

8. **FIBO는 "그래프 정본 + 산문 투영"의 가장 큰 운영 사례이며, 저작 규율로 품질을 지킨다.** OWL이 정본이고 글로서리·SKOS 파생·CSV/Excel 데이터 사전·FIB-DM 모델 변환이 전부 투영물이다. 핵심 규율: **"제약(restriction)으로 모델링되는(될 수 있는) 내용은 개념 정의에 본질적이지 않는 한 산문 정의에 중복 서술하지 말라"** — 글로서리가 모델에서 정의문을 자동 합성하기 때문. 이중 정본 드리프트를 저작 규칙으로 차단하는 방식이다.

---

## 2. 실무 증거 (사례별)

### 2.1 Widoco — 수기 절과 기계 절의 명시적 분리

- LODE 환경을 확장한 Java 도구. 온톨로지에서 HTML 문서 골격+교차참조 절을 생성하고, RDF 직렬화(XML·Turtle·NT), WebVOWL 시각화, OOPS! 평가 리포트를 함께 만든다. 100개 이상 온톨로지에서 직접 사용, OnToology·VoCol을 통한 간접 채택 다수(Widoco adoption 페이지).
- **하이브리드 메커니즘이 1급 기능이다**: 생성 문서는 LaTeX 프로젝트처럼 모듈식 sections로 나뉘고, Abstract·Introduction·Overview·Description은 수기 편집용 플레이스홀더 파일로 남는다. 재생성 시 `-rewriteAll`(전체) 대신 `-crossRef`(교차참조·개요만)를 쓰면 수기 절이 보존된다(Pandit의 실전 워크플로 기록).
- 탄생 동기 자체가 실패 경험이다(개발자 Garijo의 기록): 기존 도구(LODE·Parrot)는 ①외부 웹서비스라 통제 불가·크기 제한, ②산출물이 거대한 단일 HTML이라 서론·다이어그램 추가 편집이 고통, ③온톨로지 안에 주석되지 않은 메타데이터는 결국 수기 보충 필요.
- 한계: Java 의존, 선택 절을 손으로 채워야 함, 온톨로지에 없는 메타데이터는 수기 필수(KBSS 리뷰·Springer 논문 공통 지적).

### 2.2 pyLODE — 얇은 렌더러 + "입력 품질이 곧 출력 품질" 철학

- rdflib로 그래프를 파싱하고 Jinja/dominate로 HTML·markdown·asciidoc을 생성하는 Python 재구현. 정적 산출물(JS 없음), CLI 실행, CURIE 자동 생성·표준 온톨로지 캐시.
- 주석 표시 우선순위를 코드로 정의: DC description → rdfs:comment → skos:definition → sdo:description 순으로 산문을 채운다. **README에 명시: "잘 문서화된 입력에서만 좋은 결과" — 렌더러가 주석 모범 관행을 역으로 강제하는 설계.**
- 프로필 3종+: OntPub(OWL), VocPub(SKOS), Supermodel(다부품 모델의 프로필·모듈 문서화), Valpub(SHACL 셰이프 그래프) — **SHACL 제약의 문서 렌더가 기성 도구로 가능하다는 증거.**
- SPHN(스위스 개인화 의료 네트워크) 등이 스키마 문서 파이프라인에 채택.

### 2.3 ROBOT report / ODK — 문서 품질을 그래프 쪽 검사로 강제

- ROBOT은 OBO 생태계의 온톨로지 워크플로 자동화 도구(변환·추론·추출·질의·검사·템플릿). `robot report`는 OBO 기술 워킹그룹이 큐레이션한 수십 종 SPARQL 모범 관행 검사를 실행하고, missing_definition(IAO:0000115 부재), missing label 등을 ERROR/WARN/INFO 수준으로 설정해 CI 게이트로 쓴다. OBO Foundry 원칙 FP-006이 텍스트 정의를 규범으로 요구하고 자동 검사가 이를 집행한다.
- `robot template`은 스프레드시트→OWL 컴파일 저작 경로: 정본 그래프의 저작 표면이 꼭 Turtle일 필요가 없음을 보여준다.
- ODK는 저장소 생성 시 mkdocs 기반 문서 골격+주요 워크플로 문서 자동 생성을 포함하고 GitHub Actions로 문서를 자동 배포한다. **term 수준 산문은 그래프 안(IAO 주석), 프로젝트 수준 산문은 mkdocs 수기 — 두 층이 다른 파이프라인으로 유지되는 대규모 실례**(수백 개 OBO 온톨로지).

### 2.4 schema.org — 그래프 정본에서 수백만이 읽는 용어 페이지 생성

- 정본은 GitHub의 Turtle 파일(schema.ttl 계열)이며 편집 작업이 Turtle로 이뤄진다. 용어 페이지 HTML·임베디드 JSON-LD는 릴리스 파이프라인이 생성하고 staging에서 검수 후 발행한다.
- 용어 산문은 `rdfs:label`·`rdfs:comment`(언어 태그, HTML 마크업 허용)에 산다. 즉 **뉘앙스 있는 설명 산문이 그래프 리터럴 안에 존재**한다. 반면 Getting Started·developers 가이드류 장문 산문은 그래프 밖 수기 문서다.

### 2.5 FIBO — 대규모 "그래프 정본, 다중 투영" 운영과 저작 규율

- OWL 2 DL이 정본. 온라인 글로서리, SKOS 파생 어휘, CSV/Excel 데이터 사전, FIB-DM(관계형 모델 변환)까지 전부 투영물로 발행.
- ONTOLOGY_GUIDE의 정의 저작 규칙: 정의는 공인 출처(정부 글로서리·ISO)에서 인용하고 출처를 주석으로 남기며, **제약으로 표현되는 내용은 산문 정의에 중복하지 않는다**(글로서리 생성기가 모델에서 정의문을 합성하므로). — 그래프 축과 산문 축의 역할 분담을 저작 시점에 강제하는 규율.

### 2.6 DPV — 생성 스펙과 수기 가이드의 명시적 이원 구조

- W3C DPVCG의 Data Privacy Vocabulary. RDF(RDFS+SKOS 기본, OWL2 대안 직렬화)가 정본이고 스펙 HTML(w3id.org/dpv/2.x)은 RDF에서 생성된다. CSV 직렬화도 비시맨틱웹 사용자를 위해 병행 제공.
- **Primer(입문 해설)와 Guides(도메인·응용별 장문 안내: OWL2 사용법, ISO 동의 표준 매핑 등)는 생성 스펙과 분리된 수기 문서**로 유지된다. 레퍼런스=생성, 해설=수기라는 절 유형 분업의 현행 W3C 커뮤니티 사례.

### 2.7 리터레이트 온톨로지 — Tawny-OWL·ELOT

- Tawny-OWL: Clojure DSL로 온톨로지를 프로그래밍하며 버전관리·테스트·CI 등 소프트웨어 공학 인프라를 그대로 사용. lenticular text로 같은 소스를 문서 중심/온톨로지 중심 두 뷰로 편집 — "프로그램 뷰와 문서 뷰 어느 쪽도 우위가 없다"가 명시 원칙. Karyotype Ontology(반복 패턴으로 1,200+ 클래스 생성, 테스트 3,088개)로 실증. 논문(arXiv:1512.04250)은 한계도 명시: 온톨로지는 영어의 풍부한 표현력이 없고, 이 방식은 기존 출판 인센티브 구조와 마찰한다.
- ELOT: org-mode 플레인텍스트 하나가 온톨로지+문서의 단일 소스. headline이 분류 계층, description list가 공리·주석이 되고 SPARQL 질의·rdfpuml 다이어그램이 문서 옆에 공존. Emacs 패키지+VS Code 확장, 기존 OWL→org 역변환 exporter 제공. ISO 23726-3 Industrial Data Ontology 등 수십 프로젝트 실사용. 한계: 편집 환경 종속(Emacs/org 생태계)이 강하다.

### 2.8 OnToology — 렌더의 CI화

- GitHub 저장소를 등록하면 push마다 Widoco 문서·AR2DTool 다이어그램·OOPS! 평가·JSON-LD 컨텍스트를 자동 생성해 PR로 돌려준다. 100+ 저장소 등록. **"렌더 산출물은 사람이 만들지 않는다"를 서비스로 구현한 사례.** 동시에 외부 서비스 의존이라는 Widoco 탄생 동기의 교훈(서비스 소멸·크기 제한)이 그대로 적용되는 구조이기도 하다.

### 2.9 CIDOC CRM — 산문 정본의 반례

- 문화유산 분야 표준. 정본은 산문 스펙 문서이고 공식 RDFS 직렬화는 "자동 생성된 파생물"로 발행된다. RDF 표현이 비자명해 별도 구현 가이드(v1.1)와 application profile이 필요하다. **합의·해석 담론이 산문에서 일어나는 공동체는 산문 정본을 유지한다** — 정본 방향 선택이 소비자·담론 구조의 함수라는 증거.

### 2.10 PROV-O — 수기 서사 + 생성 교차참조의 W3C 고전 사례

- PROV-O 스펙은 수기 서사(도입·예제·컴포넌트 해설)와 OWL 파일에서 생성된 용어 교차참조 절을 결합했고, 각 용어를 PROV-DM 산문 스펙의 대응 개념에 링크한다. 표준 문서에서도 "서사는 수기, 용어 참조는 생성"이 검증된 구성임을 보여준다.

### 2.11 LLM 소비 관점 (2025–26)

- 서브그래프를 Turtle·JSON-LD·markdown으로 LLM 컨텍스트에 넣으면 타입 정보가 추론을 돕는다는 실무 정리(TrustGraph 등)와 ontology-RAG 계열 연구가 활발하다. **그래프→markdown 렌더가 인간용만이 아니라 LLM 소비 포맷으로도 유효**하다는 방증. 단 대부분 인스턴스 그래프 대상이고, "규범 문서를 그래프에서 렌더해 LLM에 먹인" 직접 사례는 발견하지 못했다(dddjango가 선행 사례가 되는 영역).

---

## 3. dddjango 설계에 주는 함의

1. **전환 단위는 '문서'가 아니라 '절 유형'이다.** 30문서를 통째로 렌더 투영물로 바꾸는 사례는 업계에 없다. 각 절을 (a) 용어·규칙 참조성 내용(규칙 문장, 조건·예외, 적용 대상, 관련 검사기 링크, 교차참조)과 (b) 서사성 내용(설계 근거 해설, 장문 코드 예제, 왜/함정 이야기)으로 분해하고, (a)부터 그래프 정본→렌더로 옮기는 것이 검증된 경로다. 606절의 절 유형 센서스가 전환 계획의 첫 산출물이어야 한다.

2. **규범 문장 3,217개의 1차 목적지는 그래프 안 주석 리터럴이다.** OBO(IAO 정의·사용 예·편집자 노트·정의 출처)·schema.org(rdfs:comment)·DPV(skos:definition) 관례처럼, 규범 문장·예시·뉘앙스 산문을 버리거나 그래프 밖에 남기는 게 아니라 **규칙 노드의 주석 속성으로 이주**시킨다. dddjango 전용 주석 어휘(예: 규범문·근거·예제코드·반례·적용조건 프로퍼티)를 정의하면 산문 뉘앙스의 자리가 그래프 안에 생긴다.

3. **Widoco sections 패턴을 렌더러 계약으로 채택한다.** 렌더 파이프라인이 기계 절(그래프에서 생성)과 수기 절(별도 파일, 렌더 시 include)을 명시적으로 구분하고, 재렌더가 수기 절을 절대 덮어쓰지 않는 계약을 처음부터 넣는다. 이러면 "일부 절만 렌더, 나머지 산문 유지"의 점진 전환이 파일 단위로 자연스럽게 표현된다.

4. **문서 품질 게이트는 렌더러가 아니라 그래프 검사기에 둔다.** ROBOT report의 missing_definition 패턴을 본떠, 규칙 노드에 규범문 부재·예제 부재·근거 부재·한국어/영어 라벨 부재 같은 주석 완결성 검사를 SHACL/SPARQL로 작성해 기존 결정적 검사기 27종 옆에 배치한다. "렌더 문서가 빈약하면 그래프 주석이 빈약한 것"을 CI가 판정하게 한다.

5. **FIBO 저작 규율을 도입해 이중 정본 드리프트를 차단한다.** SHACL 제약·관계 축으로 표현된 내용은 규범문 산문에 중복 서술하지 않는다(정의에 본질적인 경우만 예외). 렌더러가 제약→산문 문장화(예: sh:minCount→"…은 최소 1개 필요하다")를 담당하면 산문과 제약이 어긋날 수 없다. SHACL Play·pyLODE Valpub이 SHACL→문서 렌더의 참조 구현이다.

6. **렌더러는 자체 제작이 현실적이되 pyLODE를 참조 구현으로 삼는다.** 기성 도구(Widoco·pyLODE)는 인간용 HTML 어휘 문서에 최적화돼 있고 dddjango의 산출물은 LLM용 markdown 스킬 문서이므로 출력 요구가 다르다. pyLODE 자체가 rdflib+Jinja 얇은 구현이라, 같은 구조(그래프 파싱→주석 우선순위→템플릿)의 markdown 렌더러를 소규모로 자작하는 비용이 낮다. 렌더는 OnToology/ODK처럼 커밋 훅·CI 산물로 자동화하고 산출물 직접 편집을 금지한다.

---

## 4. 위험·한계

1. **렌더 문서는 참조성 정보에만 강하다.** 모든 조사 사례에서 튜토리얼·해설·장문 예제는 끝까지 수기로 남았다(DPV Primer, OBO mkdocs, schema.org 가이드). 서사 절까지 렌더로 밀어붙이면 규범의 뉘앙스·맥락 전달력이 떨어져, 품질(준수율) 향상이라는 1차 목표를 오히려 해칠 수 있다.

2. **입력 주석 품질 종속(garbage in, garbage out).** pyLODE가 명시하듯 렌더는 잘 주석된 그래프에서만 좋은 문서를 낸다. 주석 완결성 검사 없이 전환하면 "그래프는 있는데 문서가 빈약해진" 상태가 조용히 진행된다. 이주 시점에 3,217문장 각각의 주석 귀속을 검증하는 게이트가 없으면 손실이 은폐된다.

3. **부분 전환기의 정본 혼동.** 절반은 그래프 정본, 절반은 산문 정본인 기간에는 "무엇을 고쳐야 하나"가 모호해진다. Widoco도 `-rewriteAll`과 `-crossRef`를 잘못 쓰면 수기 절이 날아간다. 절·파일 단위로 정본 소유를 기계가 판독할 수 있게 표시(생성물 헤더 마킹, 수기 파일 목록)하지 않으면 역편집(생성물을 직접 고침) 사고가 난다.

4. **도구 수명·종속 위험.** LODE·Parrot 등 외부 웹서비스형 도구는 다수가 방치·소멸했고(KBSS 리뷰: 역참조 도구 다수 abandoned), Widoco는 Java, ELOT는 Emacs/org 생태계 종속이다. 장수명이 필요한 1인 저장소는 외부 서비스·무거운 런타임 의존을 피하고 자체 얇은 렌더러가 유리하다 — 대신 렌더러 자체가 유지보수 대상이 되는 비용을 진다.

5. **리터레이트 계열의 인센티브·표현력 한계.** Tawny-OWL 논문 스스로 "온톨로지는 영어의 표현력을 결여한다"고 명시한다. 형식화가 어려운 규범(정성적 판단 기준, 트레이드오프 서사)을 억지로 그래프 축으로 옮기면 규칙이 왜곡되고, 주석 리터럴로만 남기면 그래프화의 이득이 없다 — 어느 문장을 형식화하고 어느 문장을 산문 주석으로 남길지의 선별 기준이 전환의 실질 난제다.

---

## 5. 출처 URL 전체 목록

1. https://github.com/dgarijo/Widoco — Widoco 저장소(기능·LODE 확장·OOPS! 연동)
2. https://dgarijo.com/papers/widoco-iswc2017.pdf — WIDOCO ISWC 2017 논문
3. https://dgarijo.github.io/Widoco/doc/adoption/ — Widoco 채택 현황(100+ 온톨로지, OnToology·VoCol 간접 채택)
4. https://harshp.com/dev/semantic_web/documenting-ontologies-using-widoco — Widoco 실전 워크플로(sections 수기 절 보존, -crossRef 갱신)
5. https://linkingresearch.wordpress.com/2016/08/29/towards-a-human-readable-maintainable-ontology-documentation/ — Widoco 탄생 동기(LODE·Parrot의 실패 경험)
6. https://kbss.felk.cvut.cz/web/open-mic-widoco-and-co — Widoco·Ontospy 비교 리뷰(수기 보충 필요·역참조 도구 방치 실태)
7. https://link.springer.com/chapter/10.1007/978-3-319-68204-4_9 — WIDOCO 논문(Springer, 한계 서술)
8. https://github.com/RDFLib/pyLODE — pyLODE 저장소(프로필 4종, "잘 문서화된 입력" 철학, 주석 우선순위)
9. https://pypi.org/project/pylode/2.12.0/ — pyLODE 출력 포맷(html·md·adoc)
10. https://git.dcc.sib.swiss/sphn-semantic-framework/sphn-schema-doc/-/blob/v2024.1/README.md — SPHN의 pyLODE 기반 스키마 문서 파이프라인
11. https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-019-3002-3 — ROBOT 논문(BMC Bioinformatics)
12. https://oboacademy.github.io/obook/tutorial/robot-tutorial-qc/ — ROBOT report·verify·query QC 튜토리얼
13. http://robot.obolibrary.org/report_queries/missing_definition.html — missing_definition 검사(IAO:0000115 SPARQL)
14. https://obofoundry.org/principles/checks/fp_006 — OBO Foundry FP-006(텍스트 정의 원칙 자동 검사)
15. https://douroucouli.wordpress.com/2019/03/03/checking-ontologies-using-robot-report-with-an-example-from-the-cephalopod-ontology/ — ROBOT report 실전 적용기
16. https://arxiv.org/pdf/2207.02056 — ODK 논문(mkdocs 문서 골격·워크플로 문서 자동 생성·GitHub Actions 배포)
17. https://ceur-ws.org/Vol-2285/ICBO_2018_paper_46.pdf — ROBOT 기반 워크플로 표준화(OBI Makefile 사례)
18. https://oboacademy.github.io/obook/ — OBO Academy obook(튜토리얼·how-to·설명 문서는 mkdocs 수기)
19. https://oboacademy.github.io/obook/explanation/annotation-properties/ — 주석 속성 해설(정의·예시·노트가 그래프 안 산문)
20. https://github.com/information-artifact-ontology/IAO/wiki/OntologyMetadata — IAO 주석 속성 목록(definition·example of usage·editor note·definition source)
21. https://arxiv.org/abs/1512.04250 — A Highly Literate Approach to Ontology Building(lenticular text, Karyotype Ontology, 한계 명시)
22. https://ceur-ws.org/Vol-1515/demo7.pdf — Highly Literate Ontologies 데모 논문
23. https://arxiv.org/pdf/1709.08982 — User and Developer Interaction with Editable and Readable Ontologies
24. https://github.com/phillord/tawny-owl — Tawny-OWL 저장소(프로그래매틱 온톨로지 저작)
25. https://github.com/johanwk/elot — ELOT(org-mode 단일 소스, OWL 역변환 exporter, ISO 23726-3 실사용)
26. https://github.com/edmcouncil/fibo — FIBO 저장소(OWL 정본, 다중 투영 발행)
27. https://github.com/edmcouncil/fibo/blob/master/ONTOLOGY_GUIDE.md — FIBO 정의 저작 규율(제약 내용의 산문 중복 금지)
28. https://www.semanticpartners.com/learn/what-is-fibo — FIBO 개요(글로서리~지식그래프 다중 발행)
29. https://schema.org/docs/developers.html — schema.org 개발자 문서(Turtle 정본·릴리스 파이프라인)
30. https://schema.org/docs/datamodel.html — schema.org 데이터 모델(rdfs:label/comment 기반)
31. https://github.com/w3c/dpv — DPV 저장소(RDF 정본·다중 직렬화·생성 스펙)
32. https://w3c-cg.github.io/dpv/guides/ — DPV Guides(수기 장문 안내 문서)
33. https://w3c.github.io/dpv/2.2/dpv/ — DPV 생성 스펙 페이지
34. https://github.com/OnToology/OnToology — OnToology(push 시 문서·다이어그램·평가 자동 생성)
35. https://ontoology.linkeddata.es/faqs — OnToology 동작 설명
36. https://github.com/sparna-git/shacl-play — SHACL Play(SHACL→HTML 문서·UML 생성)
37. https://shacl-play.sparna.fr/play/doc — SHACL Play 문서 생성기
38. https://cidoc-crm.org/versions-of-the-cidoc-crm — CIDOC CRM(산문 정본, RDF 자동 파생)
39. https://cidoc-crm.org/sites/default/files/Implementing%20the%20CIDOC%20Conceptual%20Reference%20Model%20in%20RDF.pdf — CIDOC CRM RDF 구현 가이드(산문→RDF 변환의 비자명성)
40. https://www.w3.org/TR/2011/WD-prov-o-20111213/ — PROV-O 스펙(수기 서사+생성 교차참조 결합)
41. https://trustgraph.ai/guides/key-concepts/ontologies-and-context-graphs/ — 서브그래프의 Turtle/markdown 렌더가 LLM 컨텍스트로 유효하다는 실무 정리
