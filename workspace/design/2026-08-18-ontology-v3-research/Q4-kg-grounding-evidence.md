# Q4 — LLM+지식 그래프 그라운딩의 품질 증거

- 조사일: 2026-08-18
- 레인: Q4 (온톨로지 v3 리서치)
- 질문: 지식 그래프 기반 그라운딩(KG-RAG·GraphRAG·SPARQL 검색)이 벡터 검색 대비 LLM 산출물 품질(정확도·규칙 준수·환각 감소)에 주는 효과의 실증 근거는 무엇인가. 구조화 제약 주입이 규칙 준수율을 바꾸는가. 코드 생성 파이프라인+지식 그래프 결합 사례와 뉴로심볼릭 검증 루프의 실효는 어디까지 재현됐는가.

---

## 1. 핵심 발견

**F1. 그래프 그라운딩은 "만능 업그레이드"가 아니라 조건부 이득이다 — 재현된 증거는 멀티홉·관계 추론 과제에 집중된다.**
2026 ICLR의 GraphRAG-Bench("When to use Graphs in RAG")와 KDD 2026의 체계 평가(RAG vs. GraphRAG)가 독립적으로 같은 결론에 도달했다. 단순 사실 조회에서는 텍스트 청크 60.9 vs 그래프 60.1로 사실상 무승부(또는 벡터 RAG 우세: NQ에서 RAG F1 64.78% vs GraphRAG 63.01%), 복잡 추론에서는 그래프 53.4 vs 청크 42.9로 +10pt대 이득, 멀티홉 QA에서 HippoRAG2 70.27% vs RAG 67.02%. 즉 "질문이 여러 조각을 가로질러 추론을 요구할 때"만 그래프가 값을 한다.

**F2. 가장 강하고 직접적인 증거는 "온톨로지 스키마 + 결정적 검사 + 위반 피드백 재생성" 3단 조합이다 — 정확도가 16.7% → 54.2% → 72.55%로 단계별로 뛴다.**
data.world의 보험 도메인 벤치마크(Sequeda·Allemang, "Ontologies to the Rescue")에서 GPT-4 zero-shot Text-to-SQL은 16.7%, OWL 온톨로지+R2RML 매핑 위의 Text-to-SPARQL은 54.2%, 여기에 OBQC(Ontology-Based Query Check — RDFS/OWL 의미론 기반 결정적 SPARQL 규칙으로 쿼리 위반을 탐지하고 자연어 설명을 만들어 LLM에 되먹여 최대 3회 수리)를 붙이면 72.55%다. 오류율은 83.3% → 45.8% → 19.44%. **온톨로지가 주는 이득과 검증 루프가 주는 이득이 분리 측정된 희귀한 사례**로, dddjango가 계획하는 "생성→심볼릭 검증→위반만 들고 재생성" 루프의 직접적 선행 증거다.

**F3. LLM의 자기 수정(intrinsic self-correction)은 외부 검증기 없이는 효과가 없거나 역효과라는 것이 반복 재현됐다 — 결정적 검사기가 루프의 심판이어야 한다.**
Huang et al.(ICLR 2024 "LLMs Cannot Self-Correct Reasoning Yet")과 Stechly·Valmeekam·Kambhampati(ICLR 2025 자기 검증 한계 연구)가 외부 피드백 없는 자기 비판은 성능을 오히려 깎을 수 있음을 보였고, LLM-Modulo 프레임워크(ICML 2024 포지션 페이퍼)는 "LLM은 후보 생성기, 건전한(sound) 외부 비평가가 판정" 구조로 여행 계획 과제에서 기준선 대비 6배 성능을 보고했다. 뉴로심볼릭 루프의 실효는 **피드백의 출처가 결정적·건전한 검증기일 때** 성립한다.

**F4. "구조화 포맷으로 바꾸면 준수율이 오른다"는 가정은 실증적으로 기각됐다 — 준수율을 결정하는 것은 인코딩 포맷이 아니라 제약의 설계와 집행이다.**
"Compact Constraint Encoding for LLM Code Generation"(11개 모델·16개 과제)은 장황한 산문 제약과 압축·구조화 헤더 제약 사이에서 제약 관련 토큰 약 71% 절감(전체 프롬프트 25–30%)을 얻었지만 **제약 만족률(CSR)에는 통계적으로 유의한 차이가 없었다**(Cliff's δ < 0.01). 대신 **모델 기본 성향과 반대되는(counter-intuitive) 제약은 인코딩과 무관하게 10–100% 실패**하고, 관례적 제약은 어떤 포맷이든 99%+ 준수됐다. 또 모델의 자기 평가는 실제 준수율을 체계적으로 과대평가했다. 함의: 규범을 Turtle로 저작하는 것 자체는 토큰·정합성 이득이지 준수율 이득이 아니며, 준수율은 (a) 위반을 잡는 결정적 검사와 (b) 모델 성향을 거스르는 규칙의 식별·강제에서 나온다.

**F5. SHACL 위반 리포트를 LLM에 되먹이는 수리 루프는 동작하며, "위반된 제약 + 핵심 맥락만 담은 간결한 프롬프트"가 최고 성능이라는 체계 평가가 있다.**
"Systematic Evaluation of Knowledge Graph Repair with LLMs"(VIO — 위반 유발 연산으로 위반을 체계 생성해 평가)는 위반 SHACL 제약과 그래프의 핵심 맥락만 담은 간결한 프롬프트가 최선임을 보고했다 — dddjango의 "위반 규칙 레코드만 들고 재생성" 설계를 문헌이 직접 지지한다. xpSHACL은 SHACL 위반 리포트(RDF)에서 다국어 인간 가독 설명을 생성하고, AutomationML+SHACL 사례 연구는 LLM이 위반 원인 식별·수리 제안은 잘 하지만 **LLM이 저작한 SHACL 셰이프 자체는 전문가의 경(輕)수정이 필요**했음을 보고했다(원인 대부분은 자연어 규칙의 과소 명세).

**F6. 코드 생산 파이프라인에 지식 그래프를 결합한 사례는 "코드 구조 그래프"에서 재현된 이득이 있다 — 단, 이는 검색 정밀도 이득이지 규범 준수 이득의 직접 증거는 아니다.**
CodexGraph(코드 저장소→그래프 DB, LLM이 그래프 질의로 탐색), KGCompass(이슈·PR·코드 엔티티를 잇는 저장소 그래프로 경로 유도 수리 — SWE-bench-Lite 45.67% 수리·51.33% 함수 위치 특정, 수리당 $0.20), KG 기반 저장소 수준 코드 생성(EvoCodeBench pass@1 36.36%로 CodexGraph 36.02% 소폭 상회) 등이 있다. 공통점: 그래프가 "어떤 코드가 관련 있나"의 검색을 정밀하게 만든다. **"규범 규칙을 그래프로 저장해 코드 생성 준수율을 높였다"는 직접 벤치마크는 발견하지 못했다** — 이 지점은 dddjango가 선행 사례 없이 조합해야 하는 영역이다.

**F7. 운영(프로덕션) 사례의 수치는 존재하지만 수가 적고, 대부분 QA·지원 도메인이다.**
LinkedIn 고객 지원 KG-RAG는 6개월 운영에서 이슈당 중앙값 해결 시간 28.6% 단축, 검색 MRR +77.6%를 보고했다(과거 이슈의 내부 구조·이슈 간 관계를 보존한 그래프가 핵심). 의료 도메인에서는 KG 결합이 온도 유발 출력 변동성을 53.94% 줄여 일관성을 높인 보고가 있다. 희귀 유전질환 표현형 QA 등 그래프 검색이 정밀도를 올린 의료 사례도 있다.

**F8. 과장과 재현의 경계: Microsoft GraphRAG 원 논문의 승리 지표는 LLM-as-judge 기반 comprehensiveness·diversity이며, 감사(audit) 연구들이 그 방법론의 편향을 지적했다.**
독립 감사에서 위치 편향(답 제시 순서 교체만으로 승률 30%+ 이동), 길이 편향(200토큰 답에서 25토큰 차이가 승률 50pt 스윙), 시행 편향이 확인됐고 보정 후 이점이 크게 줄었다. faithfulness 계열 지표에서 GraphRAG는 0.28/0.18로 커뮤니티 요약 과정의 사실 손실이 확인됐으며(사실형 질문 Context Recall 0.11), 인덱스 구축 비용(사례 기준 $47.9/코퍼스, 구축 시간 7,702초 vs RAG 135초)과 평균 2.3배 지연도 보고됐다. Microsoft 스스로 LazyGraphRAG로 비용 문제를 사실상 인정했다. KDD 체계 평가는 KG-GraphRAG의 그래프 구축 불완전성(HotpotQA 답 엔티티 커버리지 65.8% → 검색 정확도 39.2%)과 근거 부족 질문(Null query)에서의 환각 경향(정답률 19.27%)도 보고했다.

**F9. 주입 포맷의 미시 증거: 트리플의 단순 선형 직렬화가 충분하며, KG-to-Text 자연문 변환은 오히려 손해일 수 있다.**
KAPING(zero-shot KGQA에서 관련 트리플을 프롬프트에 전치, 최대 +48%p)은 (주어, 관계, 목적어) 연결 수준의 선형 언어화로 충분함을 보였고, Retrieve-Rewrite-Answer 계열 연구는 KG-to-Text 자유문 변환이 의미 비일관성을 낳아 답 생성에 도움이 안 되는 경우를 보고했다. 규칙 레코드를 주입할 때 정교한 산문 렌더링이 필수라는 근거는 없다.

---

## 2. 실무 증거 (사례별)

### 2.1 온톨로지+SPARQL+검증 루프 — data.world 벤치마크 (가장 직접적인 유사물)

- 설정: OMG 손해보험(P&C) 도메인의 "Chat with the Data" 벤치마크. 엔터프라이즈 SQL 스키마 위에 OWL 온톨로지+R2RML 매핑으로 가상 지식 그래프를 구성, GPT-4 zero-shot.
- 수치: Text-to-SQL 16.7% → Text-to-SPARQL(온톨로지 경유) 54.2% → OBQC 검사+수리 루프 72.55%. 오류율 83.3% → 45.8% → 19.44%.
- OBQC의 구조: RDFS/OWL 의미론(도메인·레인지·프로퍼티 방향)에 기반한 결정적 SPARQL 규칙으로 LLM이 만든 쿼리를 실행 전 검사 → 위반 시 자연어 설명 생성 → LLM 수리(최대 3회). 수리의 70%가 도메인 규칙(프로퍼티 방향) 위반이었다.
- 한계: 복잡도·스키마 범위가 모두 높은 질문에서는 여전히 오류율 30.97%. 클래스 배타성(disjointness)을 명시 공리 없이 가정하며, union·논리 결합이 많은 복잡 온톨로지는 검사 능력을 넘는다. 이론적 개선 여지의 약 55%만 달성.
- 재현성 평가: 단일 팀·단일 도메인 벤치마크라는 한계는 있으나, 단계별 어블레이션이 명확하고 Springer 채택본이 있다.

### 2.2 GraphRAG 계열의 체계 평가 — 이득의 경계선

- **KDD 2026 체계 평가(arXiv 2502.11371)**: 4계열 변종(LlamaIndex KG 기반, Microsoft 커뮤니티 기반 local/global, HippoRAG2, RAPTOR)을 공통 프로토콜로 비교.
  - RAG 우세: 단일 홉·세부 사실(NQ 64.78 vs 63.01, NovelQA 세부 55.28 vs 46.88), 요약(원문 청크가 정답에 더 근접).
  - GraphRAG 우세: 멀티홉(HotpotQA HippoRAG2 63.01 vs 60.04, MultiHop-RAG 70.27 vs 67.02, 비교형 질의 global 64.02 vs 57.59).
  - 실패 모드: 그래프 구축 불완전성(답 엔티티 커버리지 65.8%→검색 정확도 39.2%), global 검색의 세부 손실, Null query 환각(19.27%), 구축 비용(7,702s vs 135s), 구축 LLM 품질(GPT-4o vs 4o-mini)에 대한 민감성.
- **GraphRAG-Bench(ICLR 2026, arXiv 2506.05690)**: "언제 그래프를 쓰나"를 직접 겨냥. 단순 사실 조회 60.9(청크) vs 60.1(그래프) 무승부, 복잡 추론 53.4 vs 42.9 그래프 승, 멀티홉 70.3 vs 67.0. 결론: 그래프는 범용 업그레이드가 아니라 "여러 조각을 가로지르는 추론"에 특화된 업그레이드.
- **ORAN 도메인 벤치마크(arXiv 2507.03608)**: GraphRAG 0.59·하이브리드 0.58 vs 전통 RAG 0.55. 중·고난도 질문에서 그래프 우세, 단 평균 2.3배 지연.
- **법률 문서 KG-RAG 벤치마크(CEUR Vol-4079)**: 도메인 특화 평가의 예 — KG 기반이 근거 정합(그라운딩)에서 우세.

### 2.3 뉴로심볼릭 검증 루프 — 코드·형식 검증 도메인

- **NeuroInv(루프 불변식 생성)**: LLM이 최약 전제조건 계산·후보 불변식 생성·정제, OpenJML(심볼릭)이 검증하고 반례를 추출해 피드백 지향 수리. LLM 단독 대비 검증 성공률 향상.
- **ASE'24 "LLM Meets Bounded Model Checking"**: 결정적 심볼릭 불변식 합성 + 구조화된 검증기 피드백 기반 LLM 정제 루프.
- **G-code 정합 생성(separation logic)**: 심볼릭 필터가 오탐 0의 공간 충돌 신호를 구조화해 되먹임 → LLM이 빠르게 수렴, 검증 성공 시에만 종료(형식 증명 동반).
- **LLM-Modulo(ICML 2024 포지션 + 후속 실험)**: 생성-검사-비평 루프에서 건전성 보장은 전적으로 비평가(critic)의 건전성에서 나온다는 원칙. 여행 계획 과제 6배 개선. o1급 LRM도 "바닥은 올리지만 강건하지 않다" — 생성기가 좋아져도 외부 검증은 여전히 필요.
- **자기 수정의 한계(반증 측)**: Huang et al. ICLR 2024 — 외부 피드백 없는 자기 수정은 추론 과제에서 무효~역효과. Stechly et al. ICLR 2025 — LLM 자기 검증의 체계적 한계. → 루프의 판정자는 반드시 LLM 밖의 결정적 장치여야 한다는 것이 문헌의 합의에 가깝다.

### 2.4 SHACL×LLM — 규범 그래프 무결성과 수리

- **KG 수리 체계 평가(arXiv 2507.22419)**: 위반 유발 연산(VIO)으로 SHACL 위반을 체계 생성해 LLM 수리를 평가. 핵심: **위반된 제약 + 그래프의 핵심 맥락만 담은 간결한 프롬프트가 최고 성능** — 전체 그래프·전체 규범 주입보다 위반 스코핑이 낫다.
- **AutomationML+SHACL(arXiv 2506.10678)**: 자연어 제약→SHACL 셰이프 변환은 "대체로 정확하나 전문가 경수정 필요"(방향성·프리픽스·역관계 보정). 위반 발생 시 LLM이 원인 식별·해결 제안은 3/3 규칙 모두 정확. 교훈: 자연어 규범의 과소 명세가 병목 — 형식화 과정에서 규범 자체의 모호성이 드러난다.
- **xpSHACL(VLDB 2025 워크숍)**: SHACL 위반 리포트→정당화 트리+RAG+LLM으로 인간 가독 설명 생성. 위반 리포트가 RDF라서 기계 소비·재주입이 자연스럽다는 것이 실증됨.
- **OntoLogX(arXiv 2510.01409)**: 온톨로지 유도 KG 추출에서 생성 그래프를 자동 검증→반복 피드백으로 교정하는 전용 교정 단계 채택 — "생성→검증→교정" 패턴의 또 다른 적용례.

### 2.5 코드 생산 파이프라인 × 지식 그래프

- **CodexGraph(arXiv 2408.03910)**: 코드 심볼·관계를 그래프 DB로, LLM 에이전트가 그래프 질의로 저장소 탐색 — 시퀀스 기반 검색보다 정밀한 코드 조각 검색을 입증.
- **KGCompass(arXiv 2503.21710)**: 이슈·PR(저장소 아티팩트)과 파일·클래스·함수(코드 엔티티)를 한 그래프에 연결, 경로 유도 수리. SWE-bench-Lite 45.67% 수리(당시 SOTA), 함수 수준 위치 특정 51.33%, 수리당 $0.20. 후속 보고 58.3%(단일 LLM 오픈소스 최고).
- **KG 기반 저장소 수준 코드 생성(arXiv 2505.14394)**: 프로젝트 구조·의존성·코딩 스타일을 KG로 제공 — EvoCodeBench pass@1 36.36%(Claude 3.5 Sonnet)로 CodexGraph 36.02% 소폭 상회.
- **GraphCoder·RepoGraph 계열**: 제어 흐름·의존성 그래프가 코드 완성 문맥 예측에 기여.
- 평가: 모두 "코드 구조" 그래프다. dddjango의 대상인 "규범(코딩 규칙) 그래프→생성 준수율"을 직접 측정한 연구는 이번 조사에서 발견되지 않았다. 가장 가까운 것은 2.6의 제약 주입 연구다.

### 2.6 구조화 제약 주입과 준수율

- **Compact Constraint Encoding(arXiv 2604.07192)**: 11개 모델·16개 코드 생성 과제. 산문 vs 압축 구조화 헤더 — CSR 유의차 없음(δ<0.01), 토큰 71% 절감. **준수율 분산의 주원인은 제약 설계**: 모델 기본값 역행 제약 10–100% 실패, 관례적 제약 99%+. 자기 보고 준수율은 과대평가.
- **DeCRIM(arXiv 2410.06458)**: 다중 제약 지시를 분해→비평→정제하는 파이프라인으로 준수율 향상 — 실사용 요청의 약 30%가 다중 제약 포함. 제약을 원자 단위로 분해해 개별 검증하는 접근의 실효.
- **RECAST(arXiv 2505.19030)**: 검증 가능한 제약(규칙 기반 검증기 또는 LLM 검증기)을 명시적으로 붙인 학습 데이터 구성 — "제약마다 검증기"라는 설계 사상.
- **StructFlowBench·granular 벤치마크**: 형식(포맷) 제약이 최상위 모델에서도 가장 취약한 제약 유형으로 반복 확인.
- **KAPING(arXiv 2306.04136)**: 관련 트리플 선별 주입으로 zero-shot KGQA 최대 +48%p. 무관 트리플 주입은 소폭의 잡음 비용. 선별(스코핑)이 관건.

### 2.7 운영 사례

- **LinkedIn(arXiv 2404.17723)**: 과거 지원 이슈를 이슈 내부 구조(트리)+이슈 간 관계를 보존한 KG로 구축, 6개월 운영. MRR +77.6%, BLEU +0.32, 이슈당 중앙값 해결 시간 -28.6%. 텍스트 평탄화(청크화)가 구조를 파괴해 검색 정밀도를 떨어뜨린다는 것이 출발 진단이었다는 점이 dddjango의 "산문 절 실독" 대비 구조 보존 주입 논거와 닿는다.
- **의료**: KG 결합 RAG가 온도 유발 변동성 53.94% 감소(일관성↑), 희귀 유전질환 표현형 QA에서 그래프 검색 정밀도 이득.

---

## 3. dddjango v3 설계에 주는 함의

1. **가치의 무게중심을 "정본의 포맷 전환"이 아니라 "검증 루프"에 두라.** 문헌에서 품질(준수율·정확도) 이득이 가장 크고 재현성 있게 확인된 지점은 결정적 검사+위반 피드백 재생성(16.7→54.2→72.55%의 마지막 구간, LLM-Modulo, NeuroInv)이다. Turtle/SHACL/SPARQL 스택의 채택 이유를 "규칙 코퍼스의 기계 검증 가능성과 위반 레코드의 기계 소비 가능성 확보"로 명문화하는 것이 증거와 정합한다.

2. **위반 피드백 프롬프트는 "위반된 제약 + 핵심 맥락"만 간결하게 구성하라.** KG 수리 체계 평가의 직접 결론이며, dddjango의 "위반 규칙만 들고 재생성" 구상을 그대로 지지한다. 전체 규범 재주입은 성능·토큰 양면에서 열위다.

3. **주입 스코핑은 SPARQL의 정확 선별로, 주입 포맷은 단순 직렬화로.** KAPING류 증거상 선별 주입이 효과의 원천이고, 트리플의 선형 직렬화면 충분하며 정교한 산문 렌더링이 준수율을 더 올린다는 근거는 없다. 벡터 유사도 대신 작업 유형→규칙 절의 명시적 관계(SPARQL)로 스코핑하는 v3 방향은 "구조 보존 검색이 정밀도를 올린다"는 LinkedIn·CodexGraph 계열 증거와 정합한다.

4. **모델 기본 성향을 거스르는 하우스룰을 식별해 결정적 검사기 집행 대상으로 우선 편입하라.** 인코딩 포맷과 무관하게 counter-intuitive 제약은 10–100% 실패한다는 실증(2604.07192)이 있으므로, dddjango 고유 결정(예: base 클래스 금지, 표준 파일트리, 타입 어노테이션 전수)처럼 모델의 사전 학습 관성과 충돌하는 규칙은 주입만으로 준수를 기대하지 말고 검사기 27종의 확장 대상으로 삼아 루프에서 잡아야 한다. 온톨로지의 역할은 "규칙→검사기→위반 코드" 삼자를 잇는 배선이다.

5. **산문→SHACL/Turtle 형식화는 "규범의 과소 명세를 드러내는 공정"으로 설계하고, LLM 저작 셰이프에는 검수 게이트를 두라.** AutomationML 사례처럼 LLM의 셰이프 초안은 경수정이 필요하며 그 원인 대부분이 원문 규범의 모호성이다. 3,217개 규범 문장의 온톨로지화는 번역 작업이 아니라 규범 정제(disambiguation) 작업으로 계획하는 편이 실패를 줄인다.

6. **그래프가 약한 자리(단순 조회·요약)에는 그래프를 강요하지 말라.** 단순 사실형 소비(예: 규칙 원문 1개 절 실독)는 현행 방식 대비 그래프 경유의 이득이 없다는 것이 벤치마크의 일관된 결과다. v3에서도 "단건 조회는 렌더된 투영물 실독, 횡단 질문(이 변경에 걸리는 규칙 전부)은 SPARQL"의 이원 라우팅이 증거에 부합한다.

---

## 4. 위험·한계

1. **그래프 구축의 불완전성이 곧 검색 실패다.** 답 엔티티 커버리지 65.8%가 검색 정확도 39.2%로 직결된 사례처럼, 규범 문장 3,217개의 온톨로지 변환이 미완·부정확이면 SPARQL 스코핑이 규칙을 누락시키고, 누락은 벡터 검색과 달리 조용히(0건 반환) 일어난다. 변환 커버리지의 결정적 측정 장치가 선행돼야 한다.

2. **"구조화 = 준수율 향상"은 기각된 가정이다.** 포맷 전환 자체의 품질 이득을 약속하면 과장이 된다. 루프·스코핑·검사기 확장 없이 정본만 Turtle로 바꾸는 시나리오의 기대 이득은 토큰 절감(약 71%/제약 부분)과 정합성 관리에 국한된다.

3. **직접 증거의 공백: "규범 규칙 그래프 → 코드 생성 준수율" 벤치마크는 없다.** 본 조사의 수치는 QA(보험·법률·지원)·프로그램 수리·형식 검증에서의 외삽이다. v3는 자체 준수율 측정(현행 파이프라인 대비 A/B)을 설계에 포함해야 근거가 닫힌다.

4. **LLM-as-judge 기반 성과 주장은 편향이 크다.** GraphRAG의 comprehensiveness·diversity 승리는 위치·길이·시행 편향 보정 후 크게 줄었다. 도구 벤더 블로그의 "정밀도 35% 향상"류 수치는 재현 조건이 불명확하므로 설계 근거로 삼지 않는다. 사실 충실도에서는 커뮤니티 요약형 GraphRAG가 오히려 손실(faithfulness 0.28/0.18, Context Recall 0.11)을 보인 감사도 있다.

5. **비용·지연·유지보수는 실측된 세금이다.** 그래프 구축 시간 7,702초 vs 135초, 평균 2.3배 질의 지연, 인덱싱 비용, 구축 LLM 품질 민감성. dddjango는 코퍼스가 작고(606절) 변경 주기가 느려 상대적으로 유리하지만, 규범 개정마다 그래프·투영물·검사기 삼자의 동기화 비용이 상시화된다는 점은 동일하다.

---

## 5. 출처 URL 전체 목록

### 벤치마크·체계 평가 (GraphRAG vs 벡터 RAG)
1. https://arxiv.org/abs/2502.11371 — RAG vs. GraphRAG: A Systematic Evaluation and Key Insights
2. https://arxiv.org/html/2502.11371v3 — 동 논문 HTML(수치 상세)
3. https://dl.acm.org/doi/10.1145/3770855.3817575 — 동 논문 KDD 2026 채택본
4. https://arxiv.org/abs/2506.05690 — When to use Graphs in RAG (GraphRAG-Bench, ICLR 2026)
5. https://github.com/GraphRAG-Bench/GraphRAG-Benchmark — GraphRAG-Bench 공식 저장소
6. https://openreview.net/forum?id=i9q9xDMjG7 — 동 논문 OpenReview
7. https://arxiv.org/html/2507.03608v1 — ORAN 도메인 Vector/Graph/Hybrid RAG 벤치마크
8. https://ceur-ws.org/Vol-4079/paper6.pdf — 법률 문서 KG-RAG 벤치마크
9. https://venturebeat.com/orchestration/stop-graphing-everything-when-graphrag-actually-beats-vector-rag — GraphRAG LLM-judge 편향 감사·비용 실측(실무 분석)
10. https://medium.com/graph-praxis/graph-rag-in-2026-a-practitioners-guide-to-what-actually-works-dca4962e7517 — 2026 실무자 가이드
11. https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/ — LazyGraphRAG(비용 문제의 자인)

### 온톨로지·SPARQL 그라운딩
12. https://arxiv.org/pdf/2405.11706 — Increasing the LLM Accuracy for QA: Ontologies to the Rescue! (16.7→54.2%)
13. https://arxiv.org/html/2405.11706 — 동 논문 HTML(OBQC 72.55% 상세)
14. https://link.springer.com/chapter/10.1007/978-3-031-77847-6_18 — Springer 채택본
15. https://arxiv.org/html/2408.00800 — 도메인 표준 기반 온톨로지 챗봇 상호작용

### 뉴로심볼릭 검증 루프·자기 수정의 한계
16. https://arxiv.org/abs/2310.01798 — LLMs Cannot Self-Correct Reasoning Yet (ICLR 2024)
17. https://proceedings.iclr.cc/paper_files/paper/2025/file/f3c5e56274140e0420baa3916c529210-Paper-Conference.pdf — On the Self-Verification Limitations of LLMs (ICLR 2025)
18. https://proceedings.mlr.press/v235/kambhampati24a.html — LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks (ICML 2024)
19. https://arxiv.org/html/2411.14484 — Robust Planning with Compound LLM Architectures (LLM-Modulo 실험)
20. https://arxiv.org/html/2512.15816 — NeuroInv: 뉴로심볼릭 루프 불변식 생성
21. https://chentaolue.github.io/pub-papers/ASE24.pdf — LLM Meets Bounded Model Checking (ASE 2024)
22. https://arxiv.org/pdf/2605.10568 — Correct-by-Construction G-Code Generation (separation logic)
23. https://arxiv.org/html/2606.16886v1 — Neuro-Symbolic Software Verification

### SHACL × LLM
24. https://arxiv.org/pdf/2507.22419 — Systematic Evaluation of Knowledge Graph Repair with LLMs (VIO)
25. https://arxiv.org/abs/2507.08432 — xpSHACL: Explainable SHACL Validation (VLDB 2025 워크숍)
26. https://arxiv.org/html/2506.10678v1 — AutomationML 텍스트 제약의 LLM→SHACL 형식화·검증
27. https://link.springer.com/chapter/10.1007/978-3-031-19433-7_22 — ASP 기반 SHACL 위반 수리
28. https://arxiv.org/pdf/2510.01409 — OntoLogX: 온톨로지 유도 KG 추출+검증 루프

### 코드 파이프라인 × 지식 그래프
29. https://arxiv.org/html/2408.03910v2 — CodexGraph
30. https://arxiv.org/abs/2503.21710 — KGCompass (SWE-bench-Lite 45.67%)
31. https://arxiv.org/abs/2505.14394 — Knowledge Graph Based Repository-Level Code Generation
32. https://github.com/YerbaPage/Awesome-Repo-Level-Code-Generation — 저장소 수준 코드 생성 논문 모음

### 제약 주입·준수율
33. https://arxiv.org/pdf/2604.07192 — Compact Constraint Encoding for LLM Code Generation (포맷 무영향·counter-intuitive 제약 실패)
34. https://arxiv.org/html/2410.06458 — DeCRIM: 다중 제약 분해·비평·정제
35. https://arxiv.org/html/2505.19030v2 — RECAST: 검증 가능 제약 데이터
36. https://arxiv.org/pdf/2502.14494 — StructFlowBench(포맷 제약 취약성)
37. https://arxiv.org/pdf/2306.04136 — KAPING: 트리플 선별 주입 (+48%p)
38. https://arxiv.org/pdf/2309.11206 — Retrieve-Rewrite-Answer (KG-to-Text의 한계)
39. https://www.sciencedirect.com/science/article/pii/S0950705125001078 — LLM의 KG 이해(포맷 민감성)

### 운영 사례
40. https://arxiv.org/abs/2404.17723 — LinkedIn 고객 지원 KG-RAG (해결 시간 -28.6%)
41. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12375027/ — 희귀 유전질환 표현형 Graph-RAG(의료)
42. https://arxiv.org/html/2503.06567v2 — Human Cognition Inspired RAG with KG(복잡 문제 해결·자기 검증 모듈)
