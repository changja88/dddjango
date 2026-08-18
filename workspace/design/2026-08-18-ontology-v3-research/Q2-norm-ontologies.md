# Q2 — 규범·규칙 온톨로지 선례 조사

조사일: 2026-08-18 · 레인: Q2 (규범·규칙 온톨로지 선례)
범위: LKIF-Core 등 법률 온톨로지 / ODRL / 의무논리의 OWL 표현 시도와 한계 / SPIN·SHACL rules / 규칙 개정·이력·출처 표현(PROV-O, OWL versionInfo, OBO 관례, FRBR 계열) / 코딩·아키텍처 규칙의 그래프 모델링 사례 / 표준 어휘 재사용 vs 자체 어휘 균형

---

## 1. 핵심 발견

1. **20년치 선례가 하나의 구조로 수렴한다: "온톨로지는 분류·어휘, 규범 평가는 별도 엔진".** LKIF(OWL 온톨로지 + 별도 LKIF 규칙 언어), LegalRuleML(Akoma Ntoso 문서 표준 + 별도 규칙 마크업 + defeasible logic 추론기), ODRL(OWL 어휘 + 별도 Evaluator 의미론), SHACL(RDF 데이터 + 별도 셰이프 검증기) 모두 같은 이원 구조다. **의무·금지·허용을 OWL 추론만으로 집행하려던 시도는 반복적으로 한계에 부딪혔다.**
2. **OWL이 규범 표현에 실패하는 이유는 문서화가 잘 되어 있다**: 개방세계 가정(명시 안 된 것은 거짓이 아니라 미지), 단조 추론(예외·우선 적용 불가), 이가 논리(위반 상태를 "규범은 유효한데 어겨졌다"로 표현 불가 — 모순이 되어버림), 산술 불가. contrary-to-duty(위반 시의 보정 의무) 표현은 표준 의무논리조차 역설을 일으키는 지점이다.
3. **위반을 모순이 아니라 1급 데이터로 만드는 것이 실무 해법이다.** SHACL의 sh:ValidationReport/sh:ValidationResult가 정확히 이 패턴이고, 최근 연구(conflict-tolerant deontic RDF)도 위반·충돌을 명시적 개체로 표현하는 방향으로 갔다.
4. **ODRL은 의무·금지·허용(의무 위반 시 구제 포함)의 유일한 W3C 표준 어휘지만, 어휘일 뿐 행동 의미론이 비어 있다.** Formal Semantics는 아직 Community Group 드래프트이고, 2025–26 문헌이 지적하는 결함이 구체적이다: odrl:Duty의 역할 4중첩(의무·허가 조건·구제·결과), 강한 허용/약한 허용 미구분, achievement 의무만 커버(유지·과정 의무 의미론 없음), 규범 공백(허용도 금지도 아님)의 해석 전략 부재.
5. **개정·이력·출처는 계층별로 다른 표준이 사실상 확정돼 있다**: 문서·규칙 판본 정체성은 FRBR Work/Expression 분리(Akoma Ntoso가 표준 관례화, 시점 식별자 `@YYYY-MM-DD`), 변경 행위·유래는 PROV-O(+저작·버전 특화 PAV), 온톨로지 항의 수명은 OBO 관례(IRI 영구 불변·재사용 금지, owl:deprecated=true, IAO "term replaced by", 라벨에 "obsolete " 접두).
6. **SPIN은 죽었고 SHACL이 계승했다.** SHACL-AF(sh:rule)는 W3C Note에 머물렀지만, 2025–26 현재 SHACL 1.2 Rules·Node Expressions가 Recommendation 트랙 Working Draft로 승격 중이다. 단, 규칙 반복(iteration)은 1회만 정의되는 등 미완 지점이 있고 엔진별 지원 편차가 존재한다.
7. **아키텍처 규칙의 그래프 모델링 선례는 실재한다**: ArchCNL(통제 자연어로 아키텍처 규칙 작성 → OWL 변환 → 코드 온톨로지에 대해 적합성 검사, 박사학위 논문 + 도구), DL 기반 아키텍처 적합성 검사 연구, OpenCRE(보안 요구·표준·도구 규칙을 스타 토폴로지 그래프로 상호 링크), SEPSES(CVE/CWE/CAPEC를 RDF KG로 통합, 3,600만 트리플, 생성물 SHACL 검증), 코드 스멜 온톨로지(ONTOCEAN·OSORE). **그러나 "산문 코딩 스타일 가이드 전체를 그래프 정본으로 운영"한 사례는 확인되지 않았다** — dddjango가 시도하는 조합은 선행 사례가 희박하다.
8. **어휘 재사용의 실무 균형점은 "구조·메타데이터는 표준 재사용, 도메인 내용은 자체 어휘 + 표준으로의 매핑"이다.** 통 임포트(hard reuse)는 외부 진화에 종속되는 안정성 리스크로 지적되며, 항 단위 참조(soft reuse)가 추세다. DPV(Data Privacy Vocabulary)가 "ODRL 골격과 나란히 쓰이는 자체 도메인 어휘"의 성공 모델이다.

---

## 2. 실무 증거 (사례별)

### 2.1 LKIF-Core — 법률 온톨로지의 대표 선례

- **구성**: 15개 모듈 3계층(추상: top·place·mereology·time·spacetime / 기본: process·role·action·expression / 법률: legal-action·legal-role·norm) + 프레임워크 모듈(modification·rules). norm 모듈은 expression 모듈을 확장하며, **규범을 "자격 부여(qualification)"로 모델링**한다 — 어떤 상황(situation)을 의무화(obliged)하거나 불허(disallowed)하는 자격으로서의 규범이고, 의무 상황·금지 상황은 규범이 적용되는 상황의 하위로 포섭된다.
- **핵심 설계 결정**: 의무논리 전체를 OWL에 넣지 않았다. LKIF는 OWL 단편 + SWRL 위에 **의무 진술용 별도 어휘와 별도 LKIF 규칙 언어를 추가**하는 이원 구조를 택했다.
- **문서화된 한계(제작자 자신의 보고)**:
  - OWL은 순수 논리 언어라 **수량·단위·산술 계산이 불가능** — 법조문에 핵심적인 계산(기간·금액·비율)을 처리할 모듈이 따로 필요.
  - **지식 획득 병목**: 어떤 도메인이든 형식화하려면 인접 도메인의 형식 표현이 연쇄적으로 필요해진다. 품질 좋은 기반·도메인 온톨로지 재사용으로만 완화 가능.
  - modification·rules 모듈은 성능 문제로 코어에서 확장판으로 밀려났다(호환성 목적 유지).
- **현황**: 1.1이 2008년, 이후 사실상 동결(2026-02 라이선스만 갱신). 살아 있는 규범 코퍼스의 운영 기반이라기보다 **개념 참조 지도**로 소비된다. 규범 온톨로지가 "만들어 두면 알아서 쓰인다"가 아니라는 증거이기도 하다.

### 2.2 ODRL — 의무·권리 표현의 W3C 표준과 그 균열

- **모델**: odrl:Permission / odrl:Prohibition / odrl:Duty 인스턴스로 허용·금지·의무를 표현. 자산(asset)·행위(action)·당사자(party)·제약(constraint) + 위반 시 구제(remedy)·결과(consequence) 어휘까지 갖췄다. 의무·금지·허용·예외를 표현할 표준 어휘로는 현존 유일한 W3C Recommendation.
- **결정적 공백 — 행동 의미론 부재**: 모델 명세도 OWL 어휘도 "주어진 시점·세계 상태에서 어떤 Permission/Prohibition/Obligation이 활성인가"를 판정하는 **Evaluator의 행동을 기술하지 않는다**. 이를 메우는 ODRL Formal Semantics는 아직 W3C Community Group 드래프트다.
- **2025–26 문헌이 정리한 구체 결함**:
  - **odrl:Duty의 역할 과적**: 하나의 클래스가 ①독립 의무 ②허가의 선행조건 ③위반 구제(remedy) ④결과(consequence)의 4가지 구조적 역할을 겸한다. 구제·결과 의무의 활성화 절차는 정의돼 있지 않다.
  - **허용의 미명세**: 개방/폐쇄 세계 중 무엇인지 파라미터화만 되고 특성화가 없어, 선언 안 된 행위의 지위가 배포마다 달라진다. 강한 허용(명시적 보호)과 약한 허용(금지 부재)의 온톨로지적 구분이 없다.
  - **achievement 의무만 커버**: 유지(maintenance)·과정(process) 의무는 평가 의미론이 없다 — 지속 상태나 진행 중 활동에 대한 전이가 정의돼 있지 않다.
  - **규범 공백 해소 전략 표현 불가**: 허용도 금지도 아닌 행위에 대한 open/closed 기본 정책을 언어 안에서 말할 수 없다.
  - **위반 판정 권한의 공백**(UFO-L 그라운딩 논문): 위반 선언을 누구의 규범적 권한으로 하는지가 구현자에게 암묵 위임되어 배포 간 비호환 판정을 낳는다. 논문의 처방은 행위 수준 규범(의무·금지·허용) 외에 **권한 수준 지위(Power 등)를 명시**하라는 것.
- **교훈**: 표준 어휘가 있어도 **평가 의미론을 스스로 결정적으로 정의하지 않으면 집행이 갈라진다**. ODRL을 차용하려면 골격(3분류 + 구제)만 가져오고 함정(Duty 과적, 허용 모호)은 자체 프로파일로 봉인해야 한다.

### 2.3 의무논리의 OWL 표현 시도와 한계

- **원리적 한계(반복 확인됨)**: OWL/DL은 결정가능성을 위해 표현력을 제한한 단조·개방세계 논리다. defeasible(우선순위로 뒤집히는) 규칙과 strict 규칙의 구분이 없고, 허용·의무 연산자가 없다. 표준 의무논리(SDL) 자체도 contrary-to-duty 역설(위반을 전제로 한 보정 의무), Good Samaritan 역설 등을 안고 있어, **"OWL에 의무논리를 심는다"는 이중으로 어려운 문제**다.
- **그래도 작동한 패턴 — 규정을 클래스 포섭으로 환원**(2025, 텍스트 주석 기반 OWL DL 컴플라이언스 검사): 규범 구문을 만들지 않고 **"규제 대상 클래스 ⊑ 요건 클래스"의 일반 클래스 포함(GCI)** 으로 표현. 준수 개체는 분류로 확인되고 위반 개체는 온톨로지 비일관으로 검출됐다. 단, 보고된 한계가 곧 이 접근의 상한선이다: 폐쇄세계를 데이터 설계로 흉내 내야 하고, 자연어→형식 연산자 매핑이 수작업이며, 도메인 온톨로지의 개념 공백이 즉시 병목이 되고, **defeasibility·예외·허용은 다루지 못했다(의무만)**.
- **위반·충돌의 1급 개체화**(2025, conflict-tolerant deontic RDF): 표준 의무논리 스킴을 RDF 기반으로 재구성해 의무·허용·선택 및 그 부정을 1차 표현하고, **위반과 충돌을 명시적으로 표현·추론**한다. "위반=모순"의 막다른 길을 피하는 최신 연구 방향.
- **혼합 아키텍처들**: LegalRuleML 규칙을 defeasible logic 추론기(SPINdle 계열)로 번역해 추론을 돌리는 연구, LegalRuleML→TPTP 변환으로 범용 정리증명기를 쓰는 연구(LogiKEy 프레임워크 — 고차논리에 의무논리를 얕게 임베딩) 등 — 전부 **표현(표준 마크업)과 추론(전용 엔진)을 분리**한다.

### 2.4 LegalRuleML + Akoma Ntoso — 문서 표준과 규칙 표준의 분업

- **LegalRuleML**(OASIS): RuleML을 법 규범 특화로 확장 — defeasibility, 의무 연산자, 부정, 시간성. 문서는 metadata(규범의 법원(法源)·시간 정보·관할·권한) / context / statements 3부로 구성된다. **isomorphism(동형성) 원칙** — 형식 규칙과 원문 조항 사이 1:1 대응 링크를 유지해 개정 추적과 근거 제시를 가능하게 한다. GDPR을 LegalRuleML로 모델링한 실증 연구가 있다.
- **Akoma Ntoso**(OASIS): 법률 문서의 XML 구조 표준. **FRBR 4층(Work/Expression/Manifestation/Item)을 채택**해 "같은 법(Work)"과 "특정 시점의 개정판(Expression)"과 "특정 포맷 파일(Manifestation)"을 분리한다. 개정·관보 게재·판본 비교·통합(consolidation)·시점별(point-in-time) 재구성까지 수명주기 전체를 다루는 변경 관리 메커니즘을 제공한다. 명명 규약(Naming Convention)이 URN 식별자 체계를 규정한다.
- **컴포넌트 수준 버저닝의 최신 연구**(2025–26, LRMoo 기반): Akoma Ntoso의 버저닝이 문서 수준에 머무는 것을 지적하고, **조문·항 단위까지 Work/Expression 계층을 재귀 적용**한다. 법 전체도 각 조문도 각각 불변 Work + 시점 붙은 Expression(`urn…;1988` 불변 / `@1992-03-31` 판본)을 갖고, 개정은 F28 Expression Creation **이벤트**(수단=개정 문서, 대상=이전 판, 결과=새 판)로 모델링돼 정밀 추적이 가능하다. CEUR "Legal Rules, Text and Ontologies Over Time"도 규칙·텍스트·온톨로지의 시간 차원 분리(효력 발생·적용 가능·집행 가능)를 다룬 같은 계보의 선행 연구다.
- **교훈**: 규칙 코퍼스의 개정 관리는 (a) 규칙 정체성과 판본의 분리, (b) 개정의 이벤트화, (c) 형식 규칙↔산문 원문 동형 링크 — 세 장치가 표준 패턴이다.

### 2.5 SPIN → SHACL, 그리고 SHACL 1.2 Rules

- **이행 완료**: SPIN의 모든 기능이 SHACL에 직접 대응물을 갖는다(spin:constraint→sh:sparql, SPIN 템플릿→SHACL Core 프로퍼티/제약 컴포넌트, spin:rule(CONSTRUCT)→sh:rule). SHACL은 타겟팅이 클래스에 국한되지 않고, 셰이프 전제조건과 규칙을 결합할 수 있어 SPIN보다 유연하다. 다중 컬럼 매직 프로퍼티, SPARQL 구문 트리의 RDF 표현 등 일부는 승계되지 않았다.
- **SHACL-AF의 지위**: sh:rule·sh:SPARQLRule을 정의한 Advanced Features 문서는 **W3C Note**(권고 아님)였고, 작업반 시간 제약으로 **규칙 반복을 1회만 정의**(무한 루프 회피). 구현 필수가 아니어서 엔진별 지원 범위가 다르다.
- **2025–26 현황**: Data Shapes WG가 재차터되어 SHACL 1.2 패밀리(Core·SPARQL·**Rules**·**Node Expressions**·Profiling·UI)가 Recommendation 트랙 Working Draft로 진행 중(차터 2026-12까지). SHACL 1.2 Rules는 셰이프 타겟 매칭 시 트리플을 생성하는 선언적 추론(sh:TripleRule/sh:SPARQLRule)이며 **단조적(추가만, 삭제 없음)** — 원본과 추론분을 분리한 계층적 추론에 안전하다.
- **검증+추론 결합 연구**: SHACL 제약과 추론 규칙의 상호작용(ISWC 2019) 등 이론 정리도 진행됐다.
- **교훈**: "그래프 정본 + SHACL 제약 + 소량의 SHACL/SPARQL 규칙"은 현재 실무에서 가장 안전한 조합이되, **재귀·불동점이 필요한 규칙 체계는 SHACL 밖(애플리케이션 코드)에서 결정적으로 돌려야 한다**.

### 2.6 개정·이력·출처의 표현 — 계층별 표준

| 계층 | 표준·관례 | 내용 |
|---|---|---|
| 변경 행위·유래 | **PROV-O** | Entity/Activity/Agent, prov:wasRevisionOf·wasDerivedFrom·wasAttributedTo. W3C Recommendation |
| 저작·버전 메타 | **PAV** | PROV-O 특화 경량판: pav:version, pav:previousVersion, pav:createdBy·curatedBy 등. 생명과학 데이터셋 실전 사용 |
| 온톨로지 파일 판본 | **OWL 어노테이션** | owl:versionInfo·priorVersion·backwardCompatibleWith·incompatibleWith·deprecated. 선언적 표시일 뿐 집행력 없음 |
| 항(term) 수명 | **OBO 관례** | PURL 영구 불변·**식별자 재사용 절대 금지**·의미 안정성 원칙, 폐기 시 owl:deprecated=true + 논리 공리 제거 + IAO:0100001(term replaced by) 또는 consider + 라벨 "obsolete " 접두 + **동일 IRI 무기한 유지**(과거 데이터 보호) |
| 문서·규칙 판본 정체성 | **FRBR/Akoma Ntoso/LRMoo** | Work(불변 정체성) vs Expression(시점 판본) 분리, 시점 식별자, 개정의 이벤트 모델링 (§2.4) |

핵심은 이들이 경쟁 관계가 아니라 **직교 계층**이라는 점이다: "규칙 R-014는(항 수명) v3에서 문구가 바뀌었고(판본 정체성) 그 개정은 2026-08-01 파이프라인 실패 사례에서 유래했다(유래)"를 각각 다른 어휘가 담당한다.

### 2.7 코딩·아키텍처 규칙의 그래프 모델링 — 흩어진 실존 사례

- **ArchCNL / 온톨로지 기반 아키텍처 집행**(함부르크대 박사학위 논문 + ECSA 논문 + 공개 도구): 아키텍처 규칙을 **통제 자연어(CNL) 문장으로 작성 → Xtext로 OWL 공리 변환 → 코드에서 추출한 온톨로지에 대해 적합성 검사**. 규칙 문서가 곧 검증 가능한 사양이 된다. 프로젝트 고유 개념으로 규칙을 표현할 수 있고 산문처럼 읽혀 문서 역할을 겸한다는 것이 평가 결과. dddjango의 "산문은 그래프의 투영물" 목표와 가장 가까운 실존 선례다.
- **DL 기반 아키텍처 적합성 검사**: 아키텍처 개념 언어 정의 → 일관성 검증 → 소스 코드 매핑 → 적합성 검사(CoCoME 사례 연구, PowerLoom 프로토타입) 계보의 연구가 존재한다.
- **OpenCRE**(OWASP): 보안 요구·표준(OWASP·NIST·ISO·CWE)·치트시트·도구 규칙을 **공통 요구(CRE) 허브에 스타 토폴로지로 링크**하고 전이성(A→B, B→C ⇒ A→C)으로 표준 간 매핑을 생성한다. RDF는 아니지만 "규칙 코퍼스의 그래프화·허브화"가 실제 서비스(opencre.org)로 운영되는 사례.
- **SEPSES CSKG**: CVE·CWE·CAPEC·CPE·CVSS를 통합한 RDF 지식 그래프(50만+ 인스턴스, 3,600만 트리플), 소스 갱신에 맞춰 지속 갱신, **생성된 RDF를 SHACL로 검증**해 품질 보장, SPARQL·Linked Data·덤프 다중 인터페이스 제공. "표준·취약점 규칙 코퍼스의 RDF 정본화 + SHACL 품질 게이트"의 운영 증거.
- **코드 스멜·리팩토링 온톨로지**: ONTOCEAN(스멜 분석)+OSORE(리팩토링) 조합의 추천 연구, 스멜 분류 온톨로지 연구 등 — 학술 프로토타입 수준이며 운영 채택 증거는 약하다.
- **공백 확인**: "PEP 8·Effective Dart류 산문 스타일 가이드 전체를 RDF 정본으로 저작하고 산문을 렌더로 강등"한 사례는 검색 범위에서 발견되지 않았다. 가장 가까운 실무 관행은 린터 생태계의 **구조화 규칙 메타데이터**(SonarQube·ESLint·Semgrep의 규칙 ID·심각도·태그·설명 JSON/YAML)로, 그래프는 아니지만 "규칙=구조화 레코드 + 실행 가능 검사기" 패턴이 지배적이다.

### 2.8 표준 어휘 재사용 vs 자체 어휘 — 실무 균형점

- **재사용 형태의 스펙트럼**: 통 임포트(owl:imports) / 항 단위 참조(soft reuse) / 정렬 문서(alignment)로 나뉘며, **항 단위 참조가 재사용자의 절반 수준까지 증가**하는 추세다(재사용 지형 조사 연구).
- **통 임포트의 리스크**: 임포트한 온톨로지의 진화가 내 통제 밖이라 안정성이 흔들린다(엔터프라이즈 경험 보고). 반대로 재사용 없이 고립되면 상호운용을 잃는다 — "재사용이야말로 온톨로지 설계의 진짜 시험대"라는 문제 제기도 있다.
- **중간층 어휘의 위치**: Dublin Core·SKOS·FOAF 같은 중간층(mid-level) 어휘는 크기와 구체성의 절충으로 재사용 1순위지만, 도메인 특화 속성에서 공백이 생기는 것도 문서화돼 있다.
- **성공 모델 — DPV**: W3C DPVCG의 Data Privacy Vocabulary는 **자체 도메인 어휘를 만들되 ODRL(정책 골격)·SHACL(검증)과 조합**되도록 설계했다. ODRL은 정책 표현 언어만 제공하고 법적·관할 내용은 비워두므로 DPV가 그 내용을 채운다. GDPR ROPA 문서를 DPV로 쓰고 SHACL로 정합성 검증, SPARQL로 보고서 생성 — **"표준 골격 + 자체 내용 어휘 + SHACL 게이트"** 3층 조합의 운영 증거. Parajudica(2025) 같은 다중 프레임워크 컴플라이언스 추론 연구도 이 계보다.
- **실무 규칙으로 정리하면**: ①메타데이터·유래·판본·분류 골격(DCTERMS·PROV-O·SKOS·FRBR 패턴·ODRL 3분류)은 재사용 ②도메인 개념(Django·파일트리·레이어·검사기)은 자체 IRI로 저작 ③표준과의 연결은 통 임포트가 아니라 항 단위 참조·정렬로 유지.

---

## 3. dddjango 설계에 주는 함의

1. **역할 분담을 처음부터 고정하라**: RDFS/OWL은 분류·상속·범위 질의(규칙↔절↔스킬↔검사기↔레이어의 구조 그래프), SHACL은 규칙 정본 자체의 정합성 게이트(셰이프), 규범의 실제 집행은 기존 결정적 검사기 27종과 파이프라인 게이트. **의무·금지의 판정을 OWL 추론기에 맡기는 설계는 선례상 실패 경로다.**
2. **규범 어휘는 ODRL 3분류(의무·금지·허용)+예외를 골격만 차용한 자체 프로파일로**: odrl:Duty 4중 역할 같은 함정을 피해, dddjango 어휘에서 의무/금지/허용/예외조건/우선(overrides)을 **각각 별도 프로퍼티·클래스로 분리**하고, 규범 공백(명시 안 된 행위)의 기본 정책(open/closed)을 코퍼스 차원에서 명문화한다.
3. **위반은 1급 개체로**: 검사기 27종의 출력을 SHACL ValidationResult 스타일(위반 개체 = 규칙 IRI + 대상 파일/심볼 + 심각도 + 근거)로 통일하면, 규칙 준수율 측정·개정 근거 축적이 그래프 질의로 가능해진다.
4. **규칙 정체성과 판본을 FRBR식으로 분리**: 규칙 ID는 불변 Work IRI, 개정마다 시점 붙은 Expression. 개정은 PROV-O Activity(사유·유래 파이프라인 사례를 prov:wasDerivedFrom으로 연결)로 이벤트화. 폐기는 OBO 관례(IRI 무기한 유지, owl:deprecated + replaced-by, 라벨 "obsolete " 접두, **ID 재사용 절대 금지**)를 그대로 채택.
5. **산문 렌더는 LegalRuleML의 isomorphism 원칙으로**: 그래프의 규범 노드 ↔ 렌더된 산문 절이 1:1 링크를 유지해야 개정 파급과 근거 제시(에이전트가 규칙 출처 절을 실독하는 현행 소비 방식)가 살아남는다. 606절 구조가 그대로 Expression 컴포넌트 계층이 될 수 있다(조문 단위 버저닝 연구의 재귀 Work/Expression 패턴).
6. **저작 게이트웨이로 CNL(통제 자연어) 형식을 검토하라**: ArchCNL 선례처럼 규범 문장의 문형을 제한하면(주어=대상 클래스, 양상=의무/금지/허용, 조건=예외) 산문↔Turtle 왕복 변환이 검증 가능해지고, LLM 저작 시 규범 문장 3,217개의 일괄 이관 품질을 기계 검사할 수 있다.

---

## 4. 위험·한계

1. **표현력의 상한**: 조건부·절차적 규범, contrary-to-duty(위반 시 보정 규칙), 산술 판정은 RDF/SHACL 선언만으로 안 되고 SPARQL이나 코드로 내려간다 — SPARQL 덩어리가 새로운 "산문"이 되어 정본성이 다시 흐려질 위험이 있다.
2. **표준의 미완**: ODRL Formal Semantics는 CG 드래프트, SHACL 1.2 Rules는 Working Draft(반복 1회 제한 이력, 차터 2026-12), 엔진별 SHACL-AF 지원 편차 — 지금 채택하면 사양 이동을 추적할 유지비가 든다.
3. **지식 획득 병목(LKIF의 교훈)**: 규범을 형식화하면 인접 개념(Django 구성물·파일트리·타입·검사기 의미)의 온톨로지가 연쇄적으로 필요해져 범위가 폭발할 수 있다 — 규범 문장 3,217개 전부가 아니라 구조·관계·메타부터 그래프화하는 단계적 이관이 안전하다.
4. **선례 공백**: 산문 스타일 가이드 전체의 그래프 정본화 운영 사례는 발견되지 않았다 — dddjango는 사실상 첫 사례에 가까우며, 실패 시 되돌릴 수 있는 이중 정본 기간(산문 정본 유지 + 그래프 미러 lint)이 필요하다.
5. **소비자 특수성 미검증**: 학계 선례는 기계 추론기 소비를 전제한다. LLM 에이전트가 Turtle 정본·SPARQL 결과를 소비할 때의 규칙 준수율 개선 효과는 선행 증거가 없어 자체 A/B 측정(FC 골든 세트 등)으로 검증해야 한다.

---

## 5. 출처 URL 전체 목록

### LKIF-Core·법률 온톨로지
1. https://github.com/RinkeHoekstra/lkif-core/blob/master/README.md
2. https://github.com/RinkeHoekstra/lkif-core/blob/master/norm.owl
3. https://ceur-ws.org/Vol-321/paper3.pdf — The LKIF Core Ontology of Basic Legal Concepts
4. https://www.marcellodibello.com/files/research_files/publications/ontology.pdf — LKIF Core: Principled Ontology Development for the Legal Domain

### ODRL
5. https://w3c.github.io/odrl/formal-semantics/ — ODRL Formal Semantics (CG Draft)
6. https://arxiv.org/abs/2606.24344 — What Does ODRL Mean? Cross-Level Ontological Grounding in UFO-L
7. https://ceur-ws.org/Vol-3977/OPAL2025-6.pdf — Improving ODRL 2.2: current limitations and theoretical solutions
8. https://ceur-ws.org/Vol-3977/OPAL2025-4.pdf — Towards a Formal Semantics of ODRL 2.2

### 의무논리·OWL 표현 시도
9. https://arxiv.org/html/2504.05951 — Representing Normative Regulations in OWL DL for Automated Compliance Checking
10. https://academic.oup.com/logcom/article/35/8/exaf054/8320660 — Conflict-tolerant deontic RDF (Deontic Traditional Scheme)
11. https://arxiv.org/pdf/1411.4823 — Automated Reasoning in Deontic Logic
12. https://arxiv.org/pdf/2209.05090 — Bridging between LegalRuleML and TPTP
13. https://arxiv.org/pdf/1903.10187 — LogiKEy: Designing Normative Theories for Ethical and Legal Reasoning
14. https://www.researchgate.net/publication/229763739_Deontic_Logic_and_Legal_Knowledge_Representation

### LegalRuleML·Akoma Ntoso·규칙 버저닝
15. https://link.springer.com/chapter/10.1007/978-3-319-21768-0_6 — LegalRuleML: Design Principles and Foundations
16. https://arxiv.org/pdf/1711.06128 — Enabling Reasoning with LegalRuleML
17. https://aclanthology.org/2020.lrec-1.698.pdf — Representing the GDPR in LegalRuleML
18. https://docs.oasis-open.org/legaldocml/akn-core/v1.0/cs01/part1-vocabulary/akn-core-v1.0-cs01-part1-vocabulary.html — Akoma Ntoso XML Vocabulary
19. https://docs.oasis-open.org/legaldocml/akn-nc/v1.0/akn-nc-v1.0.html — Akoma Ntoso Naming Convention
20. https://arxiv.org/html/2506.07853v3 — LRMoo 기반 조문 단위 법규 버저닝(이벤트 중심)
21. https://ceur-ws.org/Vol-874/paper7.pdf — Legal Rules, Text and Ontologies Over Time
22. https://link.springer.com/chapter/10.1007/978-94-007-1887-6_7 — Legislative Change Management with Akoma-Ntoso

### SPIN·SHACL rules
23. https://spinrdf.org/spin-shacl.html — From SPIN to SHACL
24. https://www.w3.org/TR/shacl-af/ — SHACL Advanced Features (Note)
25. https://www.w3.org/TR/shacl12-rules/ — SHACL 1.2 Rules (WD)
26. https://www.w3.org/news/2026/first-public-working-draft-shacl-1-2-node-expressions/ — SHACL 1.2 Node Expressions FPWD
27. https://ontologist.substack.com/p/understanding-shacl-12-rules — Understanding SHACL 1.2 Rules
28. https://dl.acm.org/doi/10.1007/978-3-030-30793-6_31 — SHACL Constraints with Inference Rules (ISWC 2019)

### 개정·이력·출처(PROV-O·PAV·OWL·OBO)
29. https://www.w3.org/TR/prov-o/ — PROV-O: The PROV Ontology
30. https://pav-ontology.github.io/pav/ — PAV: Provenance, Authoring and Versioning
31. https://arxiv.org/pdf/1304.7224 — PAV ontology 논문
32. https://www.w3.org/2007/OWL/wiki/Ontology_Versions — OWL 버저닝 어노테이션 정리
33. http://obofoundry.org/id-policy.html — OBO Foundry Identifier Policy
34. https://oboacademy.github.io/obook/howto/obsolete-term/ — OBO 항 폐기 절차
35. http://obofoundry.org/principles/checks/fp_012 — OBO 명명 원칙(obsolete 접두)
36. https://incatools.github.io/ontology-access-kit/guide/obsoletion.html — OAK Obsoletion 가이드

### 코딩·아키텍처 규칙의 그래프화
37. https://dl.acm.org/doi/10.1145/3241403.3241457 — An ontology-based approach for documenting and validating architecture rules (ECSA)
38. https://ediss.sub.uni-hamburg.de/bitstream/ediss/8671/1/dissertation.pdf — Ontology-Based Architecture Enforcement (ArchCNL 박사학위 논문)
39. https://github.com/sandrellaella/architecture-cnl — architecture-cnl 도구
40. https://www.researchgate.net/publication/319605695_Architecture_conformance_checking_with_description_logics
41. https://github.com/OWASP/OpenCRE/blob/main/README.md — OpenCRE
42. https://devguide.owasp.org/en/03-requirements/03-opencre/ — OpenCRE (OWASP Developer Guide)
43. https://link.springer.com/chapter/10.1007/978-3-030-30796-7_13 — The SEPSES Knowledge Graph
44. https://github.com/sepses/cyber-kg-converter — SEPSES Cyber-KB Engine
45. https://link.springer.com/chapter/10.1007/978-3-319-93375-7_15 — ONTOCEAN·OSORE 리팩토링 추천
46. https://dl.acm.org/doi/10.5555/1322468.1322542 — An ontology-based taxonomy of bad code smells

### 어휘 재사용 균형
47. https://arxiv.org/pdf/2011.12599 — The Landscape of Ontology Reuse Approaches
48. https://arxiv.org/pdf/2205.02892 — Ontology Reuse: the Real Test of Ontological Design
49. https://medium.com/@skontopo2009/ontology-reuse-in-the-enterprise-yay-or-nay-76f0a69ca505 — 엔터프라이즈 재사용 경험
50. https://w3id.org/dpv/ — Data Privacy Vocabulary (DPV)
51. https://link.springer.com/chapter/10.1007/978-3-031-77847-6_10 — DPV Version 2.0 논문
52. https://arxiv.org/pdf/2512.05453 — Parajudica: RDF 기반 다중 프레임워크 컴플라이언스 추론
