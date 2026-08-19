# T0 실행 계획 적대 리뷰 — L1 표준 정합(Standards Compliance)

- **리뷰 대상**: `workspace/design/2026-08-18-ontology-t0-plan.md` (비동결). 동결 블루프린트 v3.2의 결정(E1~E8)은 리뷰 대상 아님 — 단 T0 계획이 동결본·W3C 표준과 모순되는 지점은 지적.
- **방법**: 계획 문면 → 관련 W3C 명세·공식 문서 1차 출처 대조(WebFetch/WebSearch + REC 원문 curl 발췌) + 저장소 실물 대조(Makefile·scripts·fixtures).
- **읽은 출처**: 1차 출처 14곳 — W3C REC/명세 7종(RDFC-1.0 REC+편집자판, SHACL 2017 REC 원문 발췌, N-Quads 1.1, Turtle 1.1, PROV-O, SKOS Reference, vann), 공식 저장소·문서 7종(pySHACL README·FEATURES, rdflib.compare 문서·이슈, edmcouncil/rdf-toolkit, W3C rdf-canon 구현 리포트, YoucTagh/rdf-canon). 저장소 실물 4곳(t0-plan, blueprint v3.2, Makefile, dddjango/scripts·fixtures 레인).
- **판정일**: 2026-08-18(착수)~19(완료).

## 지적 요약 표

| ID | 심각도 | 표적 | 한 줄 주장 |
|---|---|---|---|
| L1-1 | major | A9·A6 | SHACL-SHACL은 «SHACL 문법 규칙의 부분집합»만 검증 — 하우스 규율(sh:closed 말단 한정·부정형 셰이프)은 meta-SHACL 단에서 차단되지 않아 매핑 표 항목이 설계상 달성 불능 |
| L1-2 | major | A5 ③·§7 | «정렬 N-Triples 해시 = RDFC-1.0» 동치는 canonical n-quads form을 그대로 구현할 때만 성립 — 성립 조건(이스케이프·언어 태그·무정규화·코드포인트 정렬)이 계획에 미등재 |
| L1-3 | major | §7 | cons 셀 «범위 한정 자체 구현» 과소평가 — 동일 내용 리스트 2개면 N-Degree 해싱까지 필요, 사실상 전체 알고리즘. «§4.4 축약 경로»는 명세에 없는 명칭 |
| L1-4 | minor | §7·A1 | «기성 구현 부재 시» 전제 미실사 — W3C 등재 파이썬 RDFC-1.0 구현 실존(86/86), rdflib.compare는 RGDA1(비호환), URDNA2015 구현은 이스케이프 차이로 해시 불일치 가능 |
| L1-5 | minor | A5 ② | 정렬 Turtle 직렬화기의 기성 선례(FIBO rdf-toolkit) 미실사·미기록 — house 포맷 자체는 합법이나 포맷 명세·비채택 근거의 문서화 의무 필요 |
| L1-6 | major | A5·A9 | Expression IRI의 `@`는 Turtle 접두명 로컬부에 비허용(`\@` 이스케이프 필수) — 직렬화기 출력 규약·오류 계열 픽스처에 이 함정이 없음 |
| L1-7 | major | A6 | sh:closed는 rdf:type을 자동 무시하지 않음 — sh:ignoredProperties (rdf:type) 규율이 A6에 부재, 없으면 closed 셰이프의 valid 골든까지 전부 red |
| L1-8 | major | A5 ④·A8·D2 | 게이트 ④·pre-commit 훅의 데이터 그래프 합성 미정의 — SHACL 대상 선정·sh:class는 «데이터 그래프 안의» subClassOf 경로 기준이라 파일 단위 검증은 거짓 green/red 동시 발생(E2가 막으려는 침묵 미적용의 재도입) |
| L1-9 | minor | A4 | vann 트리플의 주어·형식 규약 미확정 — 자기 어휘는 정규 용법, 제3자 어휘 전 접두 등재는 의미상 «그 어휘의 선호 접두» 제3자 주장이므로 형식·근거 문서화 필요 |
| L1-10 | minor | A3 | PROV-O «개정 연결»의 프로퍼티 미특정 — 정규 후보(wasRevisionOf·specializationOf·Activity)를 체크리스트에 명시하지 않으면 자체 신설로 표류할 위험. SKOS 용법은 정합 확인 |

집계: **blocker 0 · major 6 · minor 4** (총 10건).

---

## 지적 상세

### L1-1 (major) — meta-SHACL 단에 하우스 규율 차단을 기대: SHACL-SHACL의 커버리지와 불일치

**표적**: A9 매핑 표 마지막 행 «sh:closed 상위 타깃·부정형 셰이프 → meta-SHACL 단», A6 «meta-SHACL 2단: 셰이프 자체를 SHACL-SHACL로 검증».

**사실**: SHACL REC 부록 C의 SHACL-SHACL 셰이프 그래프는 자신을 이렇게 정의한다 — 본문: "The following shapes graph is intended to enforce **many of** the syntactic constraints related to SHACL Core in this specification. As such, it can be understood as a machine-readable version of **a subset of** those constraints"; 그래프 자체의 rdfs:comment: "This shapes graph can be used to validate SHACL shapes graphs against **a subset of** the SHACL syntax rules." (REC 원문 발췌 — https://www.w3.org/TR/shacl/#shacl-shacl). 즉 SHACL-SHACL은 **SHACL 자신의 문법 규칙**의 부분집합만 검증한다.

**추론**: «sh:closed를 말단 아닌 클래스 타깃에 사용»은 SHACL 문법 위반이 전혀 아니다(완전히 유효한 셰이프). 하우스 규율(E3)일 뿐이다. 따라서 pySHACL `-m`(SHACL-SHACL 대조 — https://github.com/RDFLib/pySHACL README)은 이 픽스처를 green으로 통과시키고, A9 매핑 표의 해당 행은 **어느 단에서도 차단되지 않는다**. T0 완료 기준 «매핑 표 전 항목 차단 확인»이 이 행에서 설계상 실패한다. «부정형 셰이프» 역시 sh:not은 REC 정식 구성요소(§4.6.1)라 SHACL-SHACL이 차단할 리 없고, 무엇을 금지하는지 계획 어디에도 정의가 없다 — §0의 «동결 기준 외 추가 확인 항목은 '계획 추가' 라벨» 규율도 미준수(이 행은 라벨 없음).

**수정 방향**: ① meta-SHACL 단을 2층으로 명문화 — 표준 SHACL-SHACL(문법) + **하우스 메타셰이프**(E3·E4 규율: closed 말단 한정, 셰이프 노드 IRI 의무 등). ② «closed 셰이프의 타깃이 말단 클래스인가»는 클래스 계층 조회가 필요해 Core로 불가 — SHACL-SPARQL(sh:sparql — 2017 REC Part 2, https://www.w3.org/TR/shacl/#sparql-constraints)로 저작하며 pySHACL의 SPARQLConstraintComponent 지원은 확인됨(https://github.com/RDFLib/pySHACL/blob/master/FEATURES.md — complete). 단 이 메타셰이프의 데이터 그래프에는 vocab의 subClassOf 트리플 병합이 필요(L1-8과 동일 원리). ③ «부정형 셰이프» 항목은 정의·근거·«계획 추가» 라벨을 붙이거나 삭제.

### L1-2 (major) — «정렬 N-Triples 해시 ≡ RDFC-1.0» 동치 주장: 실질은 참이나 성립 조건이 계획에 없다

**표적**: A5 ③ «정본 그래프는 blank node 부재라 정렬 N-Triples 해시와 동치», §7 리스크 절.

**사실**: RDFC-1.0 REC(https://www.w3.org/TR/rdf-canon/)에서 blank node가 없는 데이터셋의 정본 직렬화는 «각 quad를 **canonical n-quads form**으로 표현 → **코드포인트 순 정렬** → 연결»(§5 Serialization)이고, 알고리즘 단계 중 blank node 관련 단계(2~6)는 공회전하므로 결과는 정렬된 canonical N-Quads 문서다 — 동치 주장의 골자는 옳다. 그러나 동치는 직렬화가 **canonical n-quads form**(REC 부록 A에서 자체 정의 — N-Quads 1.1 REC(2014)에는 canonical form이 없음, https://www.w3.org/TR/n-quads/)과 정확히 일치할 때만 성립하며, 그 형식은 다음을 강제한다(부록 A 원문 발췌):
- ECHAR 강제 대상은 7문자뿐(U+0008 BS, U+0009 TAB, U+000A LF, U+000C FF, U+000D CR, U+0022 `"`, U+005C `\`), U+0000–0007·U+000B·U+000E–001F·U+007F는 **소문자 `\u` + 대문자 HEX 4자리** UCHAR, 그 외 전부 네이티브 유니코드 표현(과잉 이스케이프 금지);
- 항 사이 단일 스페이스(U+0020)·EOL은 단일 LF;
- `xsd:string` 데이터타입 IRI 생략 의무;
- **리터럴 무정규화** — "literal components of quads are not subject to any normalization", `"01"^^xsd:integer`와 `"1"^^xsd:integer`는 별개 자원(어휘형 보존);
- 정렬은 «Unicode code point order».

또 REC §1 Note는 **언어 태그 대소문자**를 정본화 상호운용의 알려진 함정으로 명시한다: "Implementations might represent language tags using all lower case … or use BCP47 formatting conventions, leading to different canonical forms, and therefore, different hashed values. User communities ought to agree to use lower case language tags."

**추론**: 계획·AUTHORING.md 산출물 목록 어디에도 위 조건이 등재되어 있지 않다. rdflib 파스→자체 N-Triples 직렬화 경로가 canonical form과 문자 단위로 일치하는지는 **«미검증»**(rdflib 버전별 이스케이프·비ASCII 처리 확인 필요)이다. 게이트 ③이 «전후 비교»(같은 구현을 두 번 호출)라 형식이 어긋나도 내부 일관성은 유지되지만, 그 경우 산출되는 값은 «RDFC-1.0 해시»가 아니라 house 해시다 — 동결본 E4가 «RDFC-1.0 해시»를 명명 채택한 이상, 표준 명칭을 채우려면 형식 준수가 요건이다.

**수정 방향**: A5 산출물에 «canonical n-quads form(REC 부록 A) 준수»를 명문 요건으로 추가하고, W3C rdf-canon 공식 테스트 스위트(86건 — https://w3c.github.io/rdf-canon/reports/)의 관련 하위집합을 도구 스모크(A1)나 게이트 스모크(A9)에 편입해 준수를 기계 확인. AUTHORING.md 저작 규약에 «언어 태그는 소문자만»(REC §1 Note의 권고 그대로)을 추가.

### L1-3 (major) — cons 셀 «표준 라벨링 경로»의 규모 과소평가: 사실상 전체 알고리즘이 필요

**표적**: §7 «기성 구현 부재 시 이 범위 한정 자체 구현(명세 §4.4 축약 경로)으로 충분», A5 ③ «shapes/의 cons 셀만 표준 라벨링 경로».

**사실**: RDFC-1.0 명세 §4.4의 제목은 «Canonicalization Algorithm» — 알고리즘 본체이지 축약 경로가 아니며, 명세 어디에도 blank node 부재·소수 케이스용 «shortcut path»는 정의되어 있지 않다(REC·편집자판 2회 대조). blank node 라벨링은 §4.6 Hash First Degree Quads로 유일 해시가 나오는 노드만 즉시 발급하고, 해시가 충돌하는 노드는 §4.8 Hash N-Degree Quads(gossip path 탐색)로 넘어간다.

**추론**(명세 알고리즘 단계에서 도출): shapes/에서 cons 셀 해시 충돌은 예외 케이스가 아니라 **정상 저작에서 즉시 발생**한다. 예: 두 셰이프가 같은 내용의 리스트를 가질 때 — `S1 sh:in ("a" "b")`, `S2 sh:in ("a" "b")` — 각 리스트의 두 번째 cons 셀의 1차 해시 입력은 {`_:z <rdf:rest> _:a .`, `_:a <rdf:first> "b" .`, `_:a <rdf:rest> <rdf:nil> .`}로 완전히 동일해 충돌하고, N-Degree 단계 없이는 정본 라벨을 발급할 수 없다. closed 셰이프마다 반복될 `sh:ignoredProperties ( rdf:type )`(L1-7)는 1-원소 리스트라 유입 참조(셰이프 IRI)로 1차 해시가 갈리지만, 2원소 이상 공유 리스트가 하나라도 생기는 순간 «범위 한정 구현»은 깨진다. 즉 자체 구현의 실제 범위는 §4.4~4.8 전체 + 부록 A 직렬화다.

**수정 방향**: §7 리스크 문면을 «전체 알고리즘 구현 또는 기성 구현 채택»으로 교정하고 «§4.4 축약 경로» 표현 삭제. 자체 구현을 유지한다면 W3C 테스트 스위트 통과를 완료 기준에 넣는다(L1-2와 공유). 대안은 L1-4.

### L1-4 (minor) — «기성 구현 부재» 전제의 실사 부재: 파이썬 RDFC-1.0 구현은 실존한다

**표적**: §7 «기성 구현 부재 시 …», A1 도구 사슬 결정.

**사실**:
- W3C rdf-canon **공식 구현 리포트**(https://w3c.github.io/rdf-canon/reports/)에 파이썬 구현 1종이 등재되어 있고 테스트 86/86 통과다: YoucTagh rdf-canon(PyPI `rdfcanon`, rdflib 기반 — https://github.com/YoucTagh/rdf-canon). 단 성숙도 신호는 약함(스타 1·커밋 7 — 저장소 실측 2026-08-19).
- rdflib 내장 canonicalization(`rdflib.compare.to_canonical_graph`)은 **RGDA1**(Sayers-Karp 다이제스트+traces — https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.compare/)로, RDFC-1.0과 다른 알고리즘·다른 라벨이라 상호운용 해시로 쓸 수 없고, 과거 서로 다른 blank node를 붕괴시킨 정확성 이슈도 있었다(https://github.com/RDFLib/rdflib/issues/494).
- URDNA2015 구현(PyLD 등)은 RDFC-1.0과 «essentially the same»이지만 canonical n-quads의 제어문자 이스케이프가 다르다고 REC 부록 B가 명시 — 해시 불일치 가능("The minor change is in the canonical n-quads form where some control characters were previously represented without escaping").

**추론**: 계획은 조건문(«부재 시»)만 두고 실사 절차·판정 기록 의무가 없다. A1이 도구 사슬을 «고정»하는 단계인데 이 결정만 근거 없이 열려 있다.

**수정 방향**: A1 실행 항목에 «rdfcanon 실사(공식 스위트 재실행으로 검증) → 채택 또는 자체 구현 결정 + AUTHORING.md 근거 기록»을 추가. 어느 쪽이든 판정 기준은 공식 테스트 스위트 통과로 통일.

### L1-5 (minor) — 정렬 Turtle 직렬화기: FIBO의 기성 선례(rdf-toolkit)를 실사·기록하지 않았다

**표적**: A5 «자체 정렬 직렬화기», 공격 질문 2.

**사실**: 결정적 Turtle 직렬화의 표준적 기성 도구가 존재한다 — EDM Council **rdf-toolkit**(https://github.com/edmcouncil/rdf-toolkit): "The primary reason for creating this tool was to have a reference serializer for the FIBO ontologies", git pre-commit 훅에서 «모든 RDF 파일이 같은 방식으로 저장되도록» 사용, 주어→술어→목적어 3단 정렬. FIBO가 실제로 쓰는 도구가 이것이다. 구현 언어는 Java(JRE 11+ 필요).

**추론**: Turtle REC는 정본 직렬형을 정의하지 않으므로(어떤 유효 Turtle도 합법) house 정렬 포맷 자체는 표준 위반이 아니고, 게이트 ②의 «파일 == canon(parse(파일))» 구조는 자기일관적이다. Java 의존은 A1의 파이썬 단일 사슬·E7 배포 경계와 충돌하므로 비채택 자체는 방어 가능하다. 문제는 계획이 이 선례를 실사한 흔적도, 비채택 근거도, **house 포맷의 명세 고정**(정렬 키·접두명 사용 규칙·이스케이프 규칙 — 직렬화기 재구현·버전 교체 시 diff 폭발 방지) 의무도 없다는 것이다. E4의 «버전 고정» 정신상 포맷 자체가 사양으로 고정되어야 한다.

**수정 방향**: AUTHORING.md(또는 직렬화기 모듈 docstring)에 ① 정본 포맷 사양(정렬 규칙·이스케이프·접두 사용·개행) ② rdf-toolkit 선례와 비채택 근거 1줄(Java 의존 vs E7)을 기록.

### L1-6 (major) — Expression IRI의 `@`: Turtle 접두명 로컬부 비허용 문자 — 직렬화기·픽스처에 함정 미등재

**표적**: A5 직렬화기 출력 규약, A9 오류 계열 표. (E6의 IRI 체계 자체는 동결 — 리뷰 대상 아님. 여기서 묻는 것은 T0 층의 직렬화기·픽스처가 이를 다루는가다.)

**사실**: Turtle REC 문법(https://www.w3.org/TR/turtle/#sec-grammar-grammar)에서 `@`는 PN_LOCAL([168s])의 허용 문자 집합(PN_CHARS_U·숫자·`:`·`.`·PLX)에 없고, 오직 PN_LOCAL_ESC([172s] — `'\' ('_'|'~'|'.'|'-'|'!'|'$'|'&'|"'"|'('|')'|'*'|'+'|','|';'|'='|'/'|'?'|'#'|'@'|'%')`)로만, 즉 `djr:R-0001\@2026-08-18`처럼 백슬래시 이스케이프로만 표기 가능하다. IRI 자체는 유효하다(RFC 3987 경로에서 `@` 허용 — 동결 결정과 표준의 모순은 없음).

**추론**: T0가 만드는 자체 직렬화기가 접두명 축약을 전 노드에 적용하면 Expression IRI에서 PN_LOCAL_ESC를 정확히 구현해야 하며, 누락 시 **파스 불능 정본**이 산출된다(게이트 ②가 제안한 정본형을 커밋하면 다음 편집의 게이트 ①에서야 터짐). 반대로 저작자(LLM)가 `\@` 없이 쓰면 `djr:R-0001` 뒤 `@2026…`이 별개 토큰으로 파싱돼 의미가 조용히 바뀌거나 문법 오류가 된다 — LLM 저작 오류 계열로 개연성이 높은데 A9 표에 이 계열이 없다. T0 시점 ISSUED는 0건이지만 직렬화기 규약·픽스처는 T0 산출물이다.

**수정 방향**: 직렬화기 사양에 «Work/Expression IRI(또는 PN_LOCAL 비허용 문자를 포함하는 전 로컬네임)는 접두명 축약 금지 — `<전체 IRI>` 표기 고정»을 명시(이스케이프 구현보다 오류 표면이 작음). A9에 «Expression IRI 표기 오류» red 픽스처 1행 추가(차단 단 = ① 또는 ②).

### L1-7 (major) — sh:closed는 rdf:type을 자동 무시하지 않는다: A6 규율에 sh:ignoredProperties 부재

**표적**: A6 «규율: sh:closed는 말단 클래스 타깃만(E3) · SHACL 1.0 범위 · IRI 의무», 공격 질문 4.

**사실**: SHACL REC §4.8.1(https://www.w3.org/TR/shacl/#ClosedConstraintComponent): closed 셰이프에서는 셰이프의 property shapes(IRI sh:path)에 선언되지 않은 술어 값 전부가 위반이며, **rdf:type은 자동 예외가 아니다** — REC 예제가 `sh:ignoredProperties ( rdf:type )`을 명시적으로 붙이는 이유다.

**추론**: A6의 대상 인스턴스(블록·규칙 노드)는 전부 rdf:type을 가지므로(어휘 v1 클래스 선언과 짝), ignoredProperties 없이 closed 셰이프를 저작하면 **valid 골든까지 전부 red**가 된다. 골든 페어 하네스가 T0 안에서 잡아내긴 하겠지만, 규율 문면이 E3의 «말단 타깃 한정»만 옮기고 REC가 요구하는 이 짝 규정을 누락한 것은 설계 결함이다. 부수 접점: `sh:ignoredProperties`의 값은 RDF 리스트라 cons 셀 blank node를 만든다 — E4의 blank node 예외 문면은 «SHACL 리스트 인자(sh:in·sh:or **등** RDF 컬렉션)»이라 '등'으로 포섭된다고 읽히지만, 게이트 ②의 IRI 의무 검사가 화이트리스트 방식이면 명시 열거가 필요하다.

**수정 방향**: A6 규율에 «closed 셰이프는 `sh:ignoredProperties ( rdf:type )`을 의무 동반(추가 무시 프로퍼티는 셰이프별 명시)»을 추가하고, invalid 골든에 «선언 밖 술어» 케이스와 함께 «ignoredProperties 누락 시 rdf:type 위반» 재현 케이스를 넣는다. 게이트 ②의 cons 셀 예외 판정에 sh:ignoredProperties를 명시 열거.

### L1-8 (major) — 게이트 ④·pre-commit 훅의 데이터 그래프 합성 미정의: 파일 단위 SHACL은 거짓 green/red를 동시에 만든다

**표적**: A5 ④(파일 대상 게이트의 SHACL 단), A8 verify [1] «온톨로지 4단 게이트(전 ttl)», D2 «변경된 ttl 한정 4단 게이트+meta-SHACL».

**사실**: SHACL 검증은 (데이터 그래프, 셰이프 그래프) 쌍 위에 정의되고, sh:targetClass의 대상 선정과 sh:class 제약은 «**데이터 그래프 안의**» SHACL instance 판정을 따른다 — REC: "A node n in an RDF graph G is a SHACL instance of a SHACL class C in G if one of the SHACL types of n in G is C"(SHACL types = rdf:type 값들과 그 **SHACL superclasses**, 즉 G 안의 rdfs:subClassOf 경로 — https://www.w3.org/TR/shacl/#targetClass). 블루프린트 E2도 같은 이유로 «계층 트리플의 데이터 그래프 병합을 빌드 강제»를 동결했다.

**추론**: rules/·wiring/ 파일 하나를 vocab 병합 없이 검증하면 ① 상위 클래스 타깃 셰이프의 타깃 상속이 끊겨 **침묵 미적용**(거짓 green — E2가 막으려는 바로 그 결함의 훅 경로 재도입), ② `sh:class 상위클래스` 제약은 subClassOf 부재로 **거짓 위반**(거짓 red)이 난다. verify는 [3]·[4]가 병합 검증을 담당하지만, pre-commit 훅은 문면상 [1](파일 단위 4단)+meta-SHACL뿐이라 훅의 ④ 판정은 신뢰 불가가 된다. 계획 문면 어디에도 게이트 ④의 데이터 그래프 구성(단독 파일인지, vocab+wiring 병합인지)이 정의되어 있지 않다.

**수정 방향**: A5에 게이트 ④의 데이터 그래프 정의를 명문화 — 권고: «변경 파일 + vocab/*.ttl(+wiring) 병합»(파일 수가 작아 훅 수 초 목표와 양립). 대안: 훅의 ④를 생략하고(①~③+meta-SHACL만) SHACL 본검증은 verify·릴리즈 전용으로 명시 — 어느 쪽이든 «훅 ④가 무엇을 보장하는가»를 문서화. L1-1의 하우스 메타셰이프도 동일 병합 규칙 적용.

### L1-9 (minor) — vann 트리플의 형식 규약 미확정: 자기 어휘는 정규, 제3자 등재는 전용(轉用)임을 문서화해야

**표적**: A4 «prefixes.ttl = vann 어노테이션 트리플로 전 접두(djr: 포함) URI 바인딩 등재». (vann 채택 자체는 E4 동결 — 리뷰 대상 아님. 여기서 묻는 것은 T0 층의 사용법이다.)

**사실**: vann(https://vocab.org/vann/)은 «어휘 기술(記述) 어노테이션» 어휘이고, `vann:preferredNamespacePrefix`의 정의는 "The preferred namespace prefix to use when using terms from **this vocabulary**…", `vann:preferredNamespaceUri`도 동형 — 주어는 기술되는 어휘 자신이다. 두 프로퍼티에 rdfs:domain/range 형식 선언은 없다(스펙에 사용 예제도 없음).

**추론**: djr: 자기 선언은 정규 용법 그대로다. skos:·prov:·dcterms: 등 제3자 어휘의 접두를 자기 저장소 등록 목적으로 vann으로 적는 것은 «그 어휘의 선호 접두»에 대한 제3자 주장으로, 도메인 제약이 없어 형식 위반은 아니나 어휘의 의도된 맥락(어휘 문서화)에서 한 발 비껴난 전용이다(어휘 등록 서비스들이 이 프로퍼티를 접두 색인에 쓰는 관행이 있다고 알려져 있으나 이 관행 자체는 «미검증»). 더 실무적인 공백: 계획이 트리플의 주어(네임스페이스 IRI인가 어휘 문서 IRI인가)·목적어 형식(플레인 리터럴인가 xsd:anyURI인가)을 정하지 않아, 게이트 ②의 «미등록 접두사 거부» 대조 알고리즘(파일의 @prefix ↔ vann 트리플 매칭 규칙)이 미정의다.

**수정 방향**: A4에 트리플 형식을 확정 — 권고: 주어 = 해당 어휘의 네임스페이스 IRI, `vann:preferredNamespacePrefix "skos"`(플레인 리터럴), `vann:preferredNamespaceUri "…#"`(리터럴, 네임스페이스 문자열과 문자 단위 일치) — 그리고 게이트 대조 규칙(@prefix 선언의 (접두, IRI) 쌍이 vann 등재 쌍과 정확히 일치해야 통과)을 명문화. 제3자 어휘 등재가 자기 선언이 아니라 저장소 등록부임을 AUTHORING.md에 한 줄 주석.

### L1-10 (minor) — A3 어휘 체크리스트: PROV-O 프로퍼티 미특정(표류 위험), SKOS 용법은 정합

**표적**: A3 «PROV-O 개정 연결» 항목, 공격 질문 6.

**사실**(PROV-O — https://www.w3.org/TR/prov-o/): 개정 연쇄의 정규 프로퍼티는 `prov:wasRevisionOf`(Entity→Entity, prov:wasDerivedFrom의 하위 — "indicates that the derived Entity contains substantial content from the original"), 구체판↔추상물 연결의 정규 프로퍼티는 `prov:specializationOf`("links a more specific Entity to a more general one — e.g., today's BBC news home page versus BBC's news home page on any day" — Expression→Work 관계와 동형), 개정 이벤트는 prov:Activity(E6 문면과 정합). 전부 REC의 Expanded terms.

**사실**(SKOS — https://www.w3.org/TR/skos-reference/): skos:prefLabel 등 라벨 프로퍼티는 도메인 무제약("no domain is stated … the effective domain … is the class of all resources") — skos:Concept이 아닌 블록·규칙 노드에 붙여도 정규 용법이다. A3의 «prefLabel=명칭만·definition 미사용»은 표준과 충돌 없음(정합 확인).

**추론**: A3는 «PROV-O 개정 연결»이라고만 적어 어느 프로퍼티인지 열려 있다. E5(표준 재사용)와 E6(Work/Expression·개정 3분류)를 어휘 v1에 옮길 때 자체 프로퍼티를 신설하면 표준 재사용 원칙과 긴장이 생기고, T1 개정 시 재작업이 된다. 또 SKOS 무결성 조건 S14("A resource has no more than one value of skos:prefLabel per language tag")는 A6 완결성 셰이프에서 `sh:uniqueLang`(pySHACL 지원 확인 — FEATURES.md complete)으로 싸게 집행할 수 있는데 계획에 없다.

**수정 방향**: A3 체크리스트에 PROV-O 사용 프로퍼티를 명시 — 개정 연쇄 `prov:wasRevisionOf`, Expression→Work `prov:specializationOf`, 개정 이벤트 `prov:Activity`(+`prov:wasGeneratedBy`), 자체 신설 금지 확인 항목. A6 완결성 셰이프에 prefLabel `sh:uniqueLang true`(+`sh:maxCount`는 언어별이므로 uniqueLang이 정확) 추가 — «계획 추가» 라벨로.

---

## Overall

**총평**: T0 계획의 표준 스택 선택 자체(pySHACL 판정 방식·`-i none`·SHACL 1.0 범위·완결성 셰이프의 표현 가능성)는 1차 출처 대조에서 대체로 정합했다. 무너지는 곳은 두 군데다. ① **meta-SHACL에 하우스 규율 차단을 떠넘긴 것**(L1-1) — SHACL-SHACL은 SHACL 자신의 문법 부분집합만 보므로, 하우스 메타셰이프 층을 세우지 않으면 T0 완료 기준의 매핑 표 검수가 그 행에서 실패한다. ② **RDFC-1.0 주변의 자신감 과잉**(L1-2·3·4) — 동치 주장의 골자는 옳지만 성립 조건(canonical n-quads form)이 어디에도 등재되지 않았고, cons 셀 «범위 한정 구현»은 명세 알고리즘 구조상 성립하지 않으며, «기성 구현 부재» 전제는 실사 없이 놓였다(W3C 등재 파이썬 구현 실존). 나머지 major(L1-6·7·8)는 각각 Turtle 문법·sh:closed 의미론·SHACL 대상 선정 의미론이 계획의 새 층(직렬화기·셰이프 규율·훅 구성)에 정확히 반영되지 않은 지점이다. blocker는 없다 — 전부 T0 내부에서 국소 수정 가능하고, 동결본과의 정면 모순은 발견하지 못했다.

**저장소 실물 대조**(계획 §1 실물 좌표의 표본 검증 — 전부 일치): `check-common-container.py` 117행·`check-domain-model.py` 존재(`dddjango/scripts/` 33파일), Makefile release [2/7] 문면, `workspace/eval/fixtures/` 레인 실존.

**정합 확인**(공격했으나 계획이 옳았던 지점):
- **A5 ④ 판정 방식**(공격 질문 5): SHACL REC은 sh:conforms를 «검증 결과가 하나라도 있으면 false»로 정의 — 심각도 불문("true if and only if the validation did not produce any validation results"). 따라서 severity별 차등 판정(§4-4 SyncDebt 경고 강등)에는 리포트 그래프 질의가 표준 충실한 유일 경로다. pySHACL 실물도 정합: API `validate()`가 (conforms, results_graph, results_text) 튜플로 리포트 그래프를 반환하고, CLI exit code는 0(conforms)/1(비준수)/2(런타임 오류)/3(미지원 기능)으로 severity를 구분하지 않는다(https://github.com/RDFLib/pySHACL). 계획 문면 그대로 타당.
- **`-i none`**: pySHACL `-i/--inference` 선택지 {none, rdfs, owlrl, both}, 기본값 none — 실존 옵션(기본값과 중복이나 명시는 무해).
- **`#` 주석 → ② 차단 기전**: 파스 시 주석이 소실되고 정본 직렬화기가 주석을 출력하지 않으므로 재직렬화 diff≠0 — 기전 타당.
- **완결성 셰이프의 SHACL 1.0 표현 가능성**(공격 질문 4 후단): 필수 프로퍼티 존재(sh:minCount)·타입(sh:datatype/sh:class)·닫힘(sh:closed)은 전부 Core 범위. 단 «절 내 순서 값 유일성·연속성» 같은 검사는 Core 밖(SHACL-SPARQL 필요)인데, 계획은 존재 검사만 요구하므로 범위 내 — 확장 시점에 유의만.

**자기 기각**(성립할 듯했으나 스스로 기각한 반박):
1. «RDFC-1.0 해시 게이트 자체가 과잉 — `rdflib.compare.isomorphic`으로 충분» → 기각: RDFC-1.0 해시 비교는 동결본 E4의 문면이라 리뷰 대상 밖. (참고로 RDFC-1.0 REC의 정본화 함수 정의상 «해시 동일 ⇔ 데이터셋 동형»이므로 목적 적합성 자체도 문제없음.)
2. «vann 채택 자체가 오용» → 기각: E4 동결 문면이 vann을 명시. vann에 도메인 제약도 없어 형식 위반이 성립하지 않음. 사용법 세부만 L1-9로 좁힘.
3. «Expression IRI의 `@`가 IRI 표준 위반이라 동결본 자체가 깨졌다» → 기각: RFC 3987 경로 성분에서 `@`는 허용 문자 — IRI는 유효. Turtle 접두명 축약의 문제로 좁혀 L1-6으로.
4. «pySHACL이 SHACL-SPARQL을 지원하지 않아 하우스 메타셰이프 수정 방향이 불가» → 기각: FEATURES.md에서 SPARQLConstraintComponent complete 확인.
5. «'SHACL 1.0'이라는 판 명칭이 오류(공식 명칭은 무판)» → 기각: 2017 REC 통칭으로 통용, SHACL 1.2 초안과의 구별 목적이 명확해 지적 실익 없음.
6. «meta-SHACL green이 T0 완료 기준인 것 자체가 커버리지 과신» → 기각: 완료 기준으로서의 meta-SHACL green은 동결본 §8 문면. 계획이 새로 추가한 것은 매핑 표의 차단 단 배정뿐이라 L1-1로 좁힘.

**미검증 잔여**(후속 확인 권고): ① rdflib 각 버전의 N-Triples 직렬화가 canonical n-quads form과 일치하는지(A1 실측 항목으로 — L1-2). ② `rdfcanon` 패키지의 실제 스위트 통과 재현(구현 리포트 등재는 확인했으나 저장소 자체에는 conformance 문구가 없음 — L1-4). ③ 어휘 등록 서비스들의 vann 접두 색인 관행(L1-9의 방증일 뿐 지적 성립에는 불필요). ④ DCTERMS는 계획이 사용 프로퍼티를 특정하지 않아 대조 자체가 불가 — A3 구체화 후 재심 대상.

**1차 출처 목록**: [RDFC-1.0 REC](https://www.w3.org/TR/rdf-canon/) · [동 편집자판](https://w3c.github.io/rdf-canon/spec/) · [rdf-canon 구현 리포트](https://w3c.github.io/rdf-canon/reports/) · [SHACL REC 2017](https://www.w3.org/TR/shacl/) · [N-Quads 1.1](https://www.w3.org/TR/n-quads/) · [Turtle 1.1](https://www.w3.org/TR/turtle/) · [PROV-O](https://www.w3.org/TR/prov-o/) · [SKOS Reference](https://www.w3.org/TR/skos-reference/) · [vann](https://vocab.org/vann/) · [pySHACL](https://github.com/RDFLib/pySHACL) · [pySHACL FEATURES](https://github.com/RDFLib/pySHACL/blob/master/FEATURES.md) · [rdflib.compare](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.compare/) · [rdflib #494](https://github.com/RDFLib/rdflib/issues/494) · [edmcouncil/rdf-toolkit](https://github.com/edmcouncil/rdf-toolkit) · [YoucTagh/rdf-canon](https://github.com/YoucTagh/rdf-canon)
