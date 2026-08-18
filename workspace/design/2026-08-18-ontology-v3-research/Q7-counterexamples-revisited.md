# Q7 — 반례 재검토: 표준 시맨틱 스택 실패 사례를 «1인 + LLM 저작 + LLM 소비» 조건에서 다시 판정한다

- 조사일: 2026-08-18
- 레인: Q7 (반례 재검토)
- 조사 조건: dddjango는 1인 소유 저장소이고, 규범 코퍼스의 저작·편집 대부분을 LLM 에이전트가 수행하며, 규칙의 소비자도 LLM 에이전트다. 이 조건에서 고전적 실패 사례(OSCAL 채택 실패담, 시맨틱웹 침체론, 기업 온톨로지 프로젝트 실패 회고)의 경고 중 무엇이 여전히 유효하고 무엇이 무효화되는지를 판별한다.

---

## 1. 핵심 발견

1. **시맨틱웹의 고전적 실패 원인 대부분은 «웹 스케일 + 다수 이해관계자 + 인간 노동» 전제에서 나온 것이며, 1인 폐쇄 코퍼스 + LLM 저작·소비 조건에서는 인센티브·신뢰·탈중앙 조율·생산자-소비자 가치 불일치 계열이 구조적으로 무효화된다.** 반면 이중 표현 동기화 비용, 형식화 손실, 도구 생태계 정체, LLM의 시맨틱 포맷 소비 효율이라는 4가지 경고는 형태를 바꿔 살아남는다.
2. **OSCAL은 «기계가독 정본으로의 전환이 규격 제정만으로는 일어나지 않는다»는 가장 최신의 실증 반례다.** 2025년 FedRAMP는 Rev5 인가 100건 이상을 처리했지만 OSCAL 제출은 0건이었고, FedRAMP 20x Phase 1 파일럿 참가자조차 기계가독 자료에 OSCAL을 쓰지 않았다. 핵심 저해 요인은 Word 문서와 OSCAL의 이중 유지 부담, 레거시 데이터의 세분성 불일치, 도구 미성숙이다.
3. **MDA(Model-Driven Architecture)의 실패 핵심은 «라운드트립»(모델↔코드 양방향 동기화)이었다.** 생성물과 모델이 급속히 발산하거나 역공학된 모델이 코드를 반영하지 못하는 문제가 반복 재생산됐다. 이는 «산문을 그래프에서 렌더된 투영물로 만든다»는 dddjango 목표에 직접적인 교훈을 준다: 단방향·완전 자동 렌더는 이 함정을 구조적으로 회피하지만, 투영물(산문)을 인간이나 에이전트가 직접 수정하는 순간 MDA의 함정이 그대로 재현된다.
4. **LLM 소비자 관점에서 RDF Turtle 원문은 불리한 소비 표면이라는 벤치마크 증거가 있다.** KG-LLM-Bench에서 그래프 추론 과제 평균 성능은 structured JSON 0.42 > YAML·edge list > RDF Turtle 0.35 > JSON-LD 0.34였고, 토큰 비용은 JSON-LD 약 13,000토큰/프롬프트, Turtle 약 8,000토큰/프롬프트로 최악 2종이었다. 네임스페이스·URI 인코딩 등 시맨틱웹 특유의 «완전하고 무모순적인 명세» 오버헤드가 원인으로 지목된다. llms.txt·AGENTS.md 생태계가 XML류 구조 포맷 대신 markdown을 선택한 이유도 같은 방향이다.
5. **기업 온톨로지·지식그래프 실패 회고의 최신 종합(LACE)은 실패 원인을 기술이 아니라 «노동 문제»로 재정의하고, LLM이 그 경제학을 역전시켰다고 분석한다.** 온톨로지 설계·데이터 매핑·시맨틱 판단이라는 3중 노동 장벽에서, 팩트당 인간 판단 비용 약 $1이 경계지어진(bounded) LLM 분류로 약 $0.001로 떨어진다. 단서: 이 역전은 «거버넌스가 있을 때만» 성립하며, 어휘가 즉흥적이고 증거 사슬이 없는 그래프는 «구조의 확신을 가진 오답»을 내놓아 검색보다 나쁘다. 그리고 «인간 판단은 이제 데이터량이 아니라 스키마 크기와 예외 수에 비례»한다.
6. **온톨로지 그라운딩이 LLM 정답률을 올린다는 실증은 dddjango의 최우선 목표(품질)와 정합한다.** Allemang & Sequeda(data.world)의 실험에서 LLM 질의응답 정확도는 SQL 직행 16% → 지식그래프(SPARQL) 54% → 온톨로지 기반 쿼리 검사(OBQC)+LLM 수리 추가 시 72%(+8% «모름», 총 오류율 20%)로 상승했다. 온톨로지가 LLM 출력의 «검사 가능한 제약»으로 기능할 때 효과가 실증된 것이다.
7. **OWL(열린 세계 가정)과 SHACL(닫힌 세계 검증)의 의미론 갭은 실무 혼선의 실증적 원천이다.** 규칙 집행(위반 검출)은 본질적으로 닫힌 세계 과제이므로, OWL 추론 중심 설계는 dddjango 목적에 맞지 않고 RDFS+SHACL 중심이 안전하다는 것이 학계·실무 양쪽의 수렴 결론이다.
8. **2024–2026 재평가 논의(Latent Space «Ontologies Are So Back», ISWC/SEMANTiCS 신경기호 트랙, LLMs4OL 챌린지, KG-LLM-Bench·LLM-KG-Bench)는 온톨로지를 «에이전트의 논리적 가드레일»로 재소환한다.** 무효화 논거는 두 가지다: 기성 어휘(schema.org·FOAF·Dublin Core)가 이미 LLM 훈련 데이터에 있어 프롬프트로 소환 가능하고, 에이전트가 운영 중 온톨로지를 스스로 갱신할 수 있다. 단, 같은 논의도 유지·드리프트는 «여전히 어려운 문제»로 남겨둔다.

---

## 2. 실무 증거 (사례별)

### 2.1 OSCAL — 기계가독 정본 전환의 최신 실패담

- **채택 공백의 실측**: 2025년 FedRAMP가 처리한 Rev5 인가 100건+ 중 OSCAL 제출 0건. FedRAMP 20x Phase 1 파일럿 참가자들도 기계가독 자료에 OSCAL을 쓰지 않았다(Platform28 구현 가이드). 규격 공표(2021년 1.0) 후 4년, 연방 의무화 시한(2026년 9월)을 앞두고도 실채택이 사실상 0에 수렴한 사례다.
- **이중 유지 부담**: 컴포넌트마다 연결된 통제 항목을 개별 갱신해야 해서 «변경 1건이 다수 참조에 파급»되는 수작업 부하가 남는다(Paramify). Word 기반 워크플로에 익숙한 팀이 구조화 포맷을 병행 유지해야 하는 부담이 채택 저해의 1순위로 지목된다.
- **세분성 불일치**: 레거시 RMF 도구·프로세스는 OSCAL이 요구하는 세분성(문장 수준 통제 정의)으로 데이터를 정의하지 않아, 조직이 내부 데이터 모델을 다시 써야 했다(NIST OSCAL Implementer's Guide 워크숍, 2025-02).
- **반대 방향 증거**: 성숙한 OSCAL 도구를 쓴 조직은 SSP 작성 기간이 4–6개월 → 1–4주로 줄고 자동 검증으로 오류율이 유의미하게 떨어졌다(Platform28). 즉 규격 자체의 결함이 아니라 «전환 비용을 흡수할 도구·자동화 없이 이중 정본을 강요»한 것이 실패 메커니즘이다.
- **판별**: OSCAL 실패담의 본체는 «다수 조직 + 인간 팀 + 레거시 문서 관성»이다. dddjango에는 레거시 문서 관성(산문 30개 스킬 문서가 현 정본)만 남고, 조직 간 조율과 인간 팀 관성은 없다. 따라서 경고의 유효분은 «전환기 이중 정본 관리»로 좁혀진다.

### 2.2 시맨틱웹 침체론 — 고전 원인의 분해

- **자발적 메타데이터의 거짓말 문제**: Doctorow(2001)의 «메타크랩» 논지 — 완전하고 신뢰할 수 있는 메타데이터는 «자기기만에 기반한 백일몽». 경제적 인센티브가 있는 행위자는 메타데이터로 거짓말을 하고, 순수 알고리즘 검색은 금세 쓰레기를 반환한다(twobithistory 회고, HN 스레드).
- **공유 어휘 합의 실패**: 시맨틱웹 최대의 실패는 공유 어휘에 합의하지 못한 것이었고, 그 결과 파편화가 왔다. 표준은 실제 응용이 견인하지 않는 «탈무드식 논쟁»에서 나왔다(Swartz 비판).
- **생산자 부담과 가치 부재**: 추상화 제공 의무가 콘텐츠 생산자에게 있었는데, 생산자는 기계가독화의 부가가치를 체감할 수 없었다. 개발자에게는 트리플·RDFS·OWL의 학습 장벽이 너무 높았다.
- **살아남은 것**: schema.org(보편 온톨로지를 포기하고 즉시 응용에 집중), JSON-LD(단순화), OpenGraph. 그리고 빅테크가 사유 생태계 안에서 시맨틱 문제를 해결한 지식그래프. 공통점은 «작은 스코프 + 명확한 소비자 + 단순한 표기»다.
- **판별**: 거짓말·스팸·인센티브 문제는 적대적 행위자가 없는 1인 폐쇄 코퍼스에서 완전히 무효화된다. 공유 어휘 합의 문제는 어휘 결정권자가 1인이므로 무효화된다. 생산자 부담 문제는 저작자가 LLM이고 소비자가 같은 파이프라인이어서 가치 루프가 닫히므로 대체로 무효화된다. 개발자 마찰 문제는 «LLM도 Turtle을 잘 못 읽는다»는 새로운 형태로 재등장한다(§2.5).

### 2.3 기업 온톨로지·지식그래프 실패 회고

- **전문성 부재**: 2025년 기업 데이터 리더 서베이에서 폐기된 EKG 프로젝트의 67%가 «내부 그래프 전문성 부재»를 1순위 실패 원인으로 꼽았다(Improvado 정리). 전제조건 없이 착수한 팀은 통상 18개월 안에 폐기하거나, 더 단순한 대안보다 비싼 비용으로 연명한다.
- **과공학 온톨로지**: 팀이 «inhibits와 antagonizes를 별개 관계로 둘 것인가»를 수개월 논쟁하고 모든 가능한 엔티티를 덮는 포괄 스키마를 설계했지만, 사용자는 엔티티 3종·관계 5종만 필요로 했다 — 완벽한 온톨로지는 사용되지 않은 채 방치됐다(insilicom).
- **모델링 실패 패턴**: 관계형 사고의 직역, 조기 상속 계층, 분류체계(taxonomy)와 스키마 온톨로지의 혼합, 목적 불명(«분석용인가 그라운딩용인가»), 전사 단일 그래프 야심, SPARQL 엔드포인트 생노출, 그래프 데이터의 컨텍스트 윈도 과적재(context-window stuffing)로 인한 토큰 비용 폭증(The Ontologist).
- **성공 처방**: 온톨로지가 아니라 유스케이스·이해관계자 요구에서 시작, 복잡한 상위 온톨로지에 커밋하기 전에 SHACL 먼저, exemplar(단위 테스트 역할)로 설계 검증, 축적→거버넌스→운영의 단계화, 최초부터 출처(provenance)·시간 추적 내장.
- **유지 저평가**: 지식그래프는 build-once가 아니며, 검증 벤치마크 없이는 품질을 알 수 없고 사용자는 프로덕션에서 품질 문제를 발견한 뒤 신뢰를 잃고 이탈한다.
- **판별**: «전문성 부재»는 LLM이 상당 부분 대체하지만(§2.4), «과공학·목적 불명·검증 부재·유지 저평가»는 저작 주체와 무관한 설계 규율의 문제라 그대로 유효하다. 특히 dddjango는 이미 «규칙 준수율 향상»이라는 단일 목적과 결정적 검사기 27종(exemplar·오라클 후보)을 갖고 있어 처방 이행의 출발점은 좋은 편이다.

### 2.4 노동 경제의 역전 — LACE 분석과 LLMs4OL

- **3중 노동 장벽**: ①완전 스키마 선행 설계(수개월 워터폴 — 출시 전 폐기되거나 실데이터 접촉 즉시 진부화), ②시스템·테이블별 수작업 매핑, ③팩트당 시맨틱 판단(«판단 1분 × 1억 데이터 포인트»). 이를 감당한 것은 Google(Freebase), Wikipedia 규모의 자원봉사 공동체, 분석가 인건비를 청구하는 방산업체뿐이었다(LACE).
- **LLM이 바꾼 것**: 개방형 생성이 아니라 **경계지어진 분류로의 분해** — «파이프라인의 모든 원자적 결정은 결국 분류다»(이 스팬은 엔티티인가, "Azure"는 어느 기지 엔티티인가, 어떤 술어가 적용되는가). 결정론적 코드가 파싱·검증·중복제거 등 비시맨틱 연산을 전담하고 LLM은 통제된 어휘 안의 경계지어진, 감사 가능한 결정만 내릴 때 팩트당 비용이 ~$1 → ~$0.001로 떨어진다.
- **남는 조건**: 인간 판단은 데이터량이 아니라 **스키마 크기·예외 수에 비례**해 남는다. dddjango의 경우 «데이터»(규범 문장 3,217개)는 작지만 «스키마+예외»(판단 기준·예외 조항이 많은 규범 산문)가 크므로, 부담의 무게중심이 바로 인간(소유자) 리뷰가 남는 지점에 있다.
- **LLM의 온톨로지스트 대체 능력 실증**: LLMs4OL 챌린지(ISWC 2024 1회, 2025 2회)는 term typing·taxonomy discovery·비분류 관계 추출·Text2Onto에서 LLM 기반 파이프라인의 유의미한 성능을 보고했다. 최고 성능은 상용 LLM + 도메인 임베딩 + 파인튜닝의 하이브리드였고, 프롬프트 설계·RAG·앙상블이 관건이었다. LLM 온톨로지 공학 체계적 문헌 리뷰(SWJ)는 LLM이 SHACL 셰이프 생성까지 수행 가능하되, SHACL 신택스 검사 + 전문가 리뷰의 결합이 논리 일관성 확보에 필요하다고 정리한다.

### 2.5 LLM 소비자의 포맷 선호 — Turtle의 역설

- **KG-LLM-Bench**(2025): 그래프 추론 과제에서 structured JSON 평균 0.42, RDF Turtle 0.35, JSON-LD 0.34. 토큰 비용은 JSON-LD >13,000, Turtle ~8,000토큰/프롬프트로 최하위 2종. 원인: 네임스페이스·URI 인코딩 등 «완전·무모순 명세» 요건이 LLM에게는 파싱 부담이자 토큰 낭비.
- **LLM-KG-Bench 3.0**(2025–2026): Turtle·JSON-LD·RDF/XML·N-Triples 4종을 지원하는 시맨틱 기술 능력 벤치마크가 별도로 필요할 만큼, LLM의 RDF 처리 능력은 모델·포맷별 편차가 크다.
- **text-to-SPARQL 오류율**: zero-shot 정확도 4% 미만~54.2% 수준으로 낮고, 5-shot으로 30%, 온톨로지 기반 쿼리 검사(OBQC)+수리로 오류율 45.8%→19.44%, 파인튜닝 시 ROUGE-L 0.90까지 개선(Allemang & Sequeda; Instruct-to-SPARQL 등). 즉 LLM이 즉석에서 SPARQL을 생성하게 하면 그 자체가 오류원이며, 검증 루프가 필수다.
- **markdown 생태계의 선택**: llms.txt 규격은 XML류 구조 포맷 대신 markdown을 채택하며 그 이유를 «LLM과 에이전트가 읽을 것이기 때문»이라고 명시한다. 에이전트 대상 문서화 실무(2026)도 markdown이 현재 LLM이 가장 널리·쉽게 이해하는 포맷이라는 데 수렴한다.
- **판별**: «개발자에게 RDF가 어렵다»는 고전 경고는 «LLM에게도 Turtle 원문은 최적 소비 표면이 아니다»로 형태를 바꿔 유효하다. 단, 이는 정본 포맷의 문제가 아니라 **소비 시점 표면의 문제**다 — 그래프를 정본으로 두되 에이전트 주입 표면은 렌더된 markdown/JSON 투영으로 하면 회피된다.

### 2.6 MDA와 라운드트립 — «투영물 정본화»의 전례

- MDA는 «플랫폼 독립 모델에서 프로덕션 시스템을 자동 생성»을 약속했으나, 생성물의 수작업 튜닝이 불가피했고 **생성 코드가 모델에서 급속히 발산하거나 역공학 모델이 코드를 반영하지 못하는** 라운드트립 문제가 반복됐다(Wikipedia Round-trip engineering; Quora 실무 회고). 무거운 선행 모델링은 애자일 반복과 충돌했고, 더 채택하기 쉬운 대안(프레임워크·ORM·코드 생성기)이 고통점을 흡수했다.
- **판별**: dddjango의 «산문은 그래프에서 렌더된 투영물» 목표는 MDA와 동형이다. 차이를 만들 수 있는 조건은 ①렌더가 단방향·완전 자동일 것(투영물 직접 편집 금지 — 편집은 항상 그래프에), ②생성물이 «검사받는 대상»이 아니라 «소비 캐시»일 것, ③1인+LLM이라 «모델 팀 vs 코드 팀» 분열이 없을 것. 이 3조건이 깨지면 MDA의 발산이 재현된다.

### 2.7 OWA/CWA 갭과 OWL·SHACL 병행 유지

- OWL은 불완전 데이터에서의 추론을 위한 열린 세계 가정(OWA) + 고유명 가정(UNA) 부재 위에 서 있고, SHACL은 데이터를 완전한 것으로 보는 닫힌 세계 검증이다. 지배적 도구들이 어느 연산에 어느 가정이 적용되는지 선언하지 않은 채 둘을 섞어, 실무 혼선과 공학 마찰의 원천이 된다(The Ontologist; arXiv 2507.12286; «SHACL: A Description Logic in Disguise»).
- SPARQL 사용자도 사실상 CWA 기대로 조작한다(«결과 없음 = 그래프에 없음»). INDETERMINATE가 FALSE로 조용히 붕괴하는 것을 막으려면 의도적·비기본값 저작이 필요하다.
- K-CAP 2025 «Lessons Learned from the Combined Development of OWL and SHACL»이 별도 논문으로 나올 만큼, OWL과 SHACL의 병행 개발·유지 자체가 독립적 난제로 인정된다.
- **판별**: 규칙 집행(위반 검출·게이트)은 닫힌 세계 과제다. dddjango가 OWL 추론을 스택의 중심에 두면 이 갭을 통째로 수입하게 된다. RDFS 수준의 가벼운 어휘 + SHACL 셰이프 중심, OWL 추론은 명확한 필요가 실증된 뒤 국소 채택이 안전하다.

### 2.8 도구 생태계의 정체와 신규 스택의 미성숙

- W3C 시맨틱웹 도구 목록의 상당수는 방치 상태고, rdflib 같은 코어 라이브러리도 자원봉사 유지에 의존한다(«유지 도움은 언제나 환영» — RDFLib). 반면 rdflib·Apache Jena 등 코어 파서·스토어·SPARQL 엔진은 20년 이상 생존한 성숙 계층이기도 하다 — 생태계의 «가장자리»가 부패했지 «중심»이 죽은 것은 아니다.
- 신규 그래프+LLM 스택(GraphRAG)은 반대편 미성숙을 보여준다: 32,000단어 책 1권 인덱싱에 $7, NLP 기반 그래프 추출 오류율 15–20%, 갱신 곤란, 다중 홉 쿼리 지연으로 «프로덕션 부적합» 비판(2025). RAG 구현의 40–60%가 프로덕션에 도달하지 못한다는 맥락도 있다.
- **판별**: 1인 저장소에서 의존성 수명은 프로젝트 수명을 좌우한다. 완화 요인은 ①필요 표면이 좁다(Turtle 파싱 + SHACL 검증 + SPARQL 질의 — 모두 코어 성숙 계층), ②LLM이 얇은 유틸리티는 스스로 재작성·수리 가능. 반면 유행 프레임워크(GraphRAG류·신생 시맨틱 레이어 SaaS)에 의존하면 부패 위험을 정면으로 흡수한다.

### 2.9 LLM 시대의 재평가 논의 (2024–2026)

- **Latent Space «Ontologies Are So Back»**: 온톨로지는 에이전트의 «무한 루프에 대한 유한한 규칙 집합»(논리적 가드레일). 90–2000년대 시맨틱웹을 죽인 것은 유지 부담이었는데, ①기성 어휘가 이미 훈련 데이터에 있고 ②에이전트가 엣지 케이스를 만나며 정의를 갱신하는 «운영 중 유지»가 가능해져 계산이 달라졌다 — 단 유지가 쉬워진 것이지 사라진 것은 아니라는 단서를 단다. Neo4j는 «더 똑똑한 공유 온톨로지 레이어 위의 얇은 에이전트» 3층 구조를 민다.
- **Allemang & Sequeda (arXiv 2405.11706)**: 온톨로지를 LLM 출력의 검사기(OBQC)로 쓸 때 정확도 16%→54%→72%. 온톨로지의 가치가 «추론»이 아니라 «검증 가능한 제약»에서 나온다는 실증 — dddjango의 «규칙 준수율» 목표와 정확히 같은 구도다.
- **ISWC 2025·SEMANTiCS 2024**: OWL 기반 지식그래프를 신경기호 시스템의 기호 연역 엔진으로 쓰는 연구가 주류 트랙화. 지식그래프는 25년 전 시맨틱웹 아이디어의 현대적 실현으로 재정위된다.
- **균형추**: 같은 시기의 GraphRAG 비판(§2.8)과 Turtle 소비 벤치마크(§2.5)는 «그래프면 무조건 좋다»는 반동적 낙관도 기각한다. 유효한 수렴점은 «구조는 검증·게이트에, 산문/markdown은 소비 표면에».

---

## 3. 5개 경고 판정표

| 경고 | 판정 | 근거 요약 |
|---|---|---|
| ① 이중 정본 | **조건부 유효** | OSCAL(2025년 제출 0건)·MDA가 보여준 실패의 본체는 «양방향·수작업 동기화». 단방향·완전 자동 렌더 + 투영물 직접 편집 금지 + CI 동기화 검증이면 회피 가능. 가장 위험한 구간은 산문이 아직 정본인 **전환기** — 이 기간을 짧게, 명시적 정본 선언과 함께 관리해야 한다. LLM 소비 표면으로는 여전히 markdown 투영이 필요하므로 «이중 표현» 자체는 없앨 수 없고, 없애야 할 것은 «이중 편집점»이다. |
| ② 유지 부하 | **조건부 유효 (대폭 완화, 소멸 아님)** | LACE: 노동 비용 ~1/1000 역전, LLMs4OL: LLM의 온톨로지 작업 능력 실증. 그러나 «인간 판단은 스키마 크기·예외 수에 비례해 남는다» — dddjango 코퍼스는 판단 기준·예외가 많은 규범 산문이라 무게중심이 정확히 남는 쪽에 있다. 온톨로지 드리프트·검증 벤치마크 유지·거버넌스는 LLM 저작으로 사라지지 않으며, 거버넌스 없는 그래프는 «구조의 확신을 가진 오답»을 만든다. |
| ③ 도구 부패 (bit rot) | **여전히 유효 (부분 완화)** | 시맨틱웹 도구 생태계의 가장자리는 광범위하게 방치 상태(W3C 도구 목록·자원봉사 유지). 신규 그래프+LLM 스택은 반대편에서 미성숙(GraphRAG 고비용·오류율 15–20%). 완화: 코어(rdflib·Jena·pySHACL·SPARQL)는 20년 생존한 성숙 계층이고, 필요 표면이 좁으며, LLM이 얇은 유틸리티를 자가 수리할 수 있다. 결론: 코어 표준 계층에만 의존하고 유행 프레임워크 의존을 배제하면 관리 가능한 위험. |
| ④ 스키마 경직성 | **조건부 유효** | 과공학 온톨로지(«엔티티 3종·관계 5종이면 충분했다»)와 워터폴 스키마 선행 설계는 저작 주체와 무관한 설계 규율 문제라 유효. OWA/CWA 갭은 스택 자체의 의미론적 함정이라 유효 — OWL 추론 중심 설계를 피해야 한다. 무효화되는 부분: 스키마 변경 비용이 «조직 간 재협상»이 아니라 «리팩터링»이 되고, LLM이 대량 마이그레이션을 수행할 수 있어 진화적 스키마가 현실적으로 가능해졌다. 처방(유스케이스 먼저, SHACL 먼저, exemplar 검증)은 그대로 적용된다. |
| ⑤ 온톨로지스트 부재 | **대체로 무효화 (단서 있음)** | 폐기 프로젝트의 67%가 꼽은 «내부 그래프 전문성 부재»의 노동 측면은 LLM이 대체(LLMs4OL·SHACL 셰이프 생성·하이브리드 파이프라인 실증). 기성 어휘는 훈련 데이터에 이미 있다. 남는 단서: LLM은 온톨로지 **노동**을 대체하지만 **판정 소유**(경계 결정·품질 게이트·예외 승인)는 대체하지 못한다 — 1인 소유자가 «최종 온톨로지스트»이며 그 리뷰 대역폭이 새 병목이다. LLM 저작 온톨로지는 SHACL 신택스 검사 + 리뷰 결합이 필요하다는 것이 문헌의 수렴 결론. |

### 시맨틱웹 고전 실패 원인의 개별 판정 (보조)

| 고전 원인 | 판정 | 이유 |
|---|---|---|
| 메타데이터 거짓말·스팸·인센티브 부재 | **무효화** | 적대적 행위자가 없는 1인 폐쇄 코퍼스. 저작자와 소비자가 같은 파이프라인이라 가치 루프가 닫힘. |
| 공유 어휘 합의 실패·파편화 | **무효화** | 어휘 결정권자가 1인. 합의 비용이 0. |
| 생산자 부담 (추상화의 어려움) | **대체로 무효화** | 저작 노동은 LLM이 수행. 단 추상화 «판정»은 소유자에게 남는다. |
| 개발자 학습 장벽 (트리플·OWL) | **형태 변환 유효** | LLM도 Turtle 원문 소비에서 성능·토큰 페널티(KG-LLM-Bench). 소비 표면은 렌더된 투영으로 해결. |
| 웹 스케일 야심 | **해당 없음** | «작은 스케일에서는 유용하다»는 침체론의 단서 조항이 dddjango 스케일(3,217문장·606절)과 정확히 부합. |

---

## 4. dddjango v3 설계에 주는 함의

1. **이중 편집점 금지, 이중 표현 허용.** 그래프 정본화의 성패는 «산문 투영물을 누구도 직접 편집하지 않는다»는 불변식에 달려 있다(MDA·OSCAL 교훈). 렌더는 단방향·완전 자동·결정적이어야 하고, CI가 «투영물 == render(그래프)»를 결정적으로 검증해야 한다. 전환기(산문 정본 기간)는 명시적으로 짧게 설계하고, 어느 시점에 어느 파일이 정본인지 저장소 안에 선언한다.
2. **에이전트 소비 표면은 Turtle 원문이 아니라 렌더된 markdown/JSON 투영으로 한다.** KG-LLM-Bench의 성능·토큰 증거와 llms.txt 생태계의 수렴이 같은 방향을 가리킨다. 그래프는 검증·질의·렌더의 정본이고, 컨텍스트 주입물은 소비 최적화된 투영이다. 그래프 데이터의 컨텍스트 과적재(context-window stuffing)는 실패 패턴으로 명시돼 있다.
3. **RDFS + SHACL 중심, OWL 추론은 국소·후행 채택.** 규칙 집행은 닫힌 세계 과제이며 OWA/CWA 갭은 실증된 마찰원이다. «SHACL 먼저, 상위 온톨로지는 나중»이라는 실무 처방을 따르고, 추론이 필요한 지점이 실증되기 전에는 RDFS 수준의 어휘로 충분하다.
4. **규범 문장 본문은 산문 리터럴로 보존하는 하이브리드 모델을 택한다.** 완전 트리플화는 규범 산문의 판단 기준·예외·뉘앙스를 잃는다(형식화 손실). 구조화 대상은 메타데이터·관계(참조·위임·우선순위)·적용 조건·검사기 연결로 한정하고, 문장 본문 자체는 리터럴로 담아 렌더 시 산문으로 복원한다.
5. **LLM의 그래프 작업을 경계지어진 분류로 분해하고, 결정적 검사기가 게이트한다.** LACE의 비용 역전은 «통제된 어휘 안의 경계지어진, 감사 가능한 결정 + 결정론적 코드의 비시맨틱 연산 전담» 조건에서만 성립한다. 기존 결정적 검사기 27종을 SHACL 셰이프·골든 exemplar와 연결해 «구조의 확신을 가진 오답»을 차단한다. LLM 즉석 SPARQL 생성은 오류원이므로(zero-shot 4–54%) 사전 검증된 질의 카탈로그 또는 OBQC류 검사+수리 루프를 쓴다.
6. **의존성은 코어 성숙 계층(rdflib·pySHACL·표준 SPARQL)에 한정하고, 유행 프레임워크·SaaS 시맨틱 레이어 의존을 배제한다.** 1인 저장소에서 도구 부패는 여전히 유효한 경고다. 필요 표면을 좁게 유지하면 LLM의 자가 수리 가능 범위 안에 남는다.

---

## 5. 위험·한계

1. **전환기 이중 정본의 발산 위험.** 산문 정본 → 그래프 정본 전환이 길어지거나 부분적이면, OSCAL의 «Word와 OSCAL 병행 유지» 실패가 소규모로 재현된다. 특히 전환 중 긴급 수정이 산문 쪽에 직접 가해지는 순간부터 발산이 시작된다.
2. **소유자 리뷰 대역폭이라는 새 병목.** LLM이 노동을 대체해도 스키마·예외에 대한 판정은 1인에게 남는다. 3,217개 규범 문장의 구조화 판정(어느 관계·어느 적용 조건·어느 검사기 연결)이 리뷰 큐를 초과하면, 검증 없는 LLM 판정이 누적돼 드리프트한다.
3. **LLM의 시맨틱 포맷 처리 편차.** Turtle 저작·SPARQL 생성의 모델별 성능 편차가 크고(LLM-KG-Bench), 벤치마크는 빠르게 진부화된다. 파이프라인이 특정 모델의 RDF 능력에 암묵 의존하면 모델 교체 시 회귀한다.
4. **형식화 손실과 과공학의 상반 압력.** 구조를 얕게 하면 온톨로지의 검증 가치가 줄고, 깊게 하면 과공학 함정(사용되지 않는 완벽한 스키마)에 빠진다. «검사기가 실제로 소비하는 구조만 만든다»는 기준 없이는 균형점을 잃기 쉽다.
5. **조사 편향 한계.** OSCAL 비판의 일부는 상용 도구 벤더(Paramify·Platform28)의 자사 솔루션 홍보 맥락에서 나왔고, 기업 온톨로지 실패 회고 일부는 유료(paywall)라 전문 확인이 제한됐다(Vashishta). LACE 분석도 자사 플랫폼 정당화 서사와 결합돼 있어, 비용 역전 수치(~1/1000)는 방향성 증거로만 취급해야 한다.

---

## 6. 출처 URL 전체 목록

### 시맨틱웹 침체론·회고
1. https://twobithistory.org/2018/05/27/semantic-web.html — Whatever Happened to the Semantic Web? (역사적 회고)
2. https://news.ycombinator.com/item?id=20016256 — Ask HN: Why Did the Semantic Web Fail?
3. https://news.ycombinator.com/item?id=18023408 — HN: Whatever Happened to the Semantic Web? 토론
4. https://data-mining.philippe-fournier-viger.com/the-semantic-web-and-why-it-failed/ — The Semantic Web and why it failed
5. https://halfanhour.blogspot.com/2007/03/why-semantic-web-will-fail.html — Why the Semantic Web Will Fail (2007)
6. https://www.linkedin.com/pulse/why-semantic-web-has-failed-kurt-cagle — Kurt Cagle, Why the Semantic Web Has Failed

### OSCAL 채택 실패담
7. https://www.platform28.com/blog/oscal-implementation-guide — OSCAL 구현 가이드 (2025년 FedRAMP 제출 0건 실측)
8. https://www.paramify.com/blog/the-benefits-and-shortcomings-of-oscal — OSCAL의 이점과 결함
9. https://csrc.nist.gov/csrc/media/projects/open-security-controls-assessment-language/images-media/2025/oscal-mini-workshop-32-USAI/2.19.2025_USAI_SlideDeck.pdf — NIST OSCAL Implementer's Guide 워크숍 (세분성 불일치)
10. https://fedtechmagazine.com/article/2025/02/what-is-oscal-perfcon — What Is OSCAL? (FedTech)
11. https://pages.nist.gov/OSCAL/about — NIST OSCAL 공식

### 기업 온톨로지·지식그래프 실패 회고
12. https://laceplatform.com/blog/knowledge-graphs-labor-problem/ — Why Knowledge Graphs Failed (노동 문제·LLM 경제 역전)
13. https://ontologist.substack.com/p/why-knowledge-graph-projects-fail — Why Knowledge Graph Projects Fail (The Ontologist)
14. https://insilicom.com/?Blogs%2F129%2Fwhy-million-dollar-knowledge-graph-projects-fail-how-knowledge-graphs-are-really-built-9.html — Why Million-Dollar Knowledge Graph Projects Fail
15. https://improvado.io/blog/enterprise-knowledge-graph — Enterprise Knowledge Graph (67% 전문성 부재 서베이 인용)
16. https://vinvashishta.substack.com/p/why-most-enterprise-ontologies-and — Why Most Enterprise Ontologies & KGs Fail (paywall — 전문 미확인)
17. https://www.moderndata101.com/blogs/how-enterprise-ontologies-fail-and-how-to-stop-it — How Enterprise Ontologies Fail

### OWA/CWA·OWL·SHACL 마찰
18. https://ontologist.substack.com/p/the-open-worldclosed-world-conundrum — The Open World/Closed World Conundrum
19. https://arxiv.org/abs/2507.12286 — SHACL Validation in the Presence of Ontologies
20. https://arxiv.org/pdf/2108.06096 — SHACL: A Description Logic in Disguise
21. https://dl.acm.org/doi/10.1145/3731443.3771340 — Lessons Learned from the Combined Development of OWL and SHACL (K-CAP 2025)

### MDA·라운드트립 전례
22. https://en.wikipedia.org/wiki/Round-trip_engineering — Round-trip engineering
23. https://www.quora.com/Why-did-model-driven-architecture-development-fail — MDA 실패 실무 회고
24. https://www.sciencedirect.com/science/article/abs/pii/S2590118419300607 — Code generation using MDA: systematic mapping study

### LLM 시대 재평가 (2024–2026)
25. https://www.latent.space/p/ontologies-agentic-systems — Ontologies Are So Back: Why AI Agents Are Reviving the Semantic Web
26. https://arxiv.org/abs/2405.11706 — Allemang & Sequeda, Increasing the LLM Accuracy for QA: Ontologies to the Rescue! (16%→54%→72%)
27. https://journals.sagepub.com/doi/10.1177/29498732251320043 — OWL 기반 KG의 신경기호 시스템 활용 (2025)
28. https://ebooks.iospress.nl/volume/knowledge-graphs-in-the-age-of-language-models-and-neuro-symbolic-ai-proceedings-of-the-20th-international-conference-on-semantic-systems — SEMANTiCS 2024 프로시딩
29. https://dl.acm.org/doi/10.1007/978-3-032-09527-5_4 — Ontology-Enhanced KG Completion Using LLMs (ISWC 2025)

### LLM×온톨로지 능력·벤치마크
30. https://arxiv.org/html/2504.07087v1 — KG-LLM-Bench (Turtle 0.35 vs JSON 0.42, 토큰 비용)
31. https://arxiv.org/html/2505.13098 — LLM-KG-Bench 3.0
32. https://arxiv.org/pdf/2409.10146 — LLMs4OL 2024 Overview (ISWC)
33. https://www.tib-op.org/ojs/index.php/ocp/article/view/2913 — LLMs4OL 2025 Overview
34. https://www.semantic-web-journal.net/system/files/swj3864.pdf — LLMs for Ontology Engineering: Systematic Literature Review
35. https://dl.acm.org/doi/10.1145/3698204.3716476 — Instruct-to-SPARQL (text-to-SPARQL 데이터셋)
36. https://arxiv.org/pdf/2309.17122 — How Well Do LLMs Speak Turtle?

### GraphRAG 한계·도구 생태계
37. https://medium.com/@amrwrites/you-probably-dont-need-graphrag-0bc9cf671db1 — You probably don't need GraphRAG
38. https://unalarming.com/limitations-of-graphrag — Limitations of GraphRAG
39. https://www.falkordb.com/blog/vectorrag-vs-graphrag-technical-challenges-enterprise-ai-march25/ — VectorRAG vs GraphRAG 기술 과제 (2025-03)
40. https://github.com/rdflib/rdflib — RDFLib (자원봉사 유지)
41. https://www.w3.org/2001/sw/wiki/SemanticWebTools — W3C 시맨틱웹 도구 목록 (방치 다수)

### 에이전트 소비 표면·markdown 규약
42. https://llmstxt.org/ — llms.txt 규격 (markdown 채택 이유 명시)
43. https://dacharycarey.com/2026/02/26/llms-vs-agents-as-docs-consumers/ — LLMs vs. agents as docs consumers
