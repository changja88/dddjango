# R5 — LLM 에이전트 규칙 그라운딩 최신 실무 (2025~2026)

조사일: 2026-08-18 · 담당: 외부 자료 조사 서브에이전트 · 방법: WebSearch/WebFetch 1차 출처 우선

## 0. 조사 질문

2025~2026 현재, 코딩 에이전트에 «걸리는 규칙만» 공급하는 실무 기법과 도구 생태는 무엇인가?
— 규칙 파일 생태의 선별 주입 메커니즘, 정책 검색(retrieval over policies), GraphRAG/OG-RAG 규칙 적용,
온톨로지 제약 에이전트·구조화 출력, 위반 리포트 피드백 루프, diff/경로 기반 규칙 필터링 실제 구현,
규칙 파일 메타데이터 라우팅 관례(우리 SKILL frontmatter·ⓓ 채널과 비교).

---

## 1. 발견 A — 에이전트 규칙 파일 생태의 선별 주입 메커니즘

### A-1. Cursor rules(.mdc): 4가지 적용 모드 (사실)

Cursor 공식 문서 기준, 규칙은 4가지 모드로 주입된다: ① Always Apply(모든 세션),
② Apply Intelligently(에이전트가 `description`을 읽고 관련성 판단), ③ Apply to Specific Files
(`globs` 패턴 매칭 시 자동 첨부), ④ Apply Manually(`@rule-name` 명시 호출).
frontmatter는 `description`/`globs`/`alwaysApply` 3필드가 전부이며, `alwaysApply: true`면
globs·description은 무시된다. 서브디렉터리 `.cursor/rules`와 중첩 `AGENTS.md`를 인식하고
더 구체적인 경로가 우선한다. 규칙 1개당 500줄 이하 권장, 큰 규칙은 합성 가능한 모듈로 분할하고
중복 대신 외부 파일 참조를 권한다. 충돌 시 Team Rules → Project Rules → User Rules 순으로 앞선 출처가 이긴다.
- 출처: https://cursor.com/docs/rules (공식)
- «dddjango 시사점»: 업계 대표 구현의 라우팅 메타데이터는 «경로 glob + 자연어 description» 단 2축이다 — 우리 SKILL frontmatter의 description 기반 로드는 ②와 동형이고, 부족한 축은 ③(경로 기반)이다.

### A-2. GitHub Copilot `.instructions.md`: `applyTo` glob frontmatter (사실)

`.github/instructions/*.instructions.md` 파일은 frontmatter의 `applyTo` glob(`**/*.py`,
`src/api/**`, 콤마 다중 패턴)으로 적용 대상을 지정한다. 편집 중인 파일에 대해 모든
`.instructions.md`의 glob을 동시에 평가하여 매칭되는 파일들이 컨텍스트에 함께 쌓인다.
`applyTo`가 없으면 자동으로는 아무것도 하지 않는다.
- 출처: https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide (공식)
- «dddjango 시사점»: «편집 대상 파일 경로 → 규칙 부분집합» 매핑이 상용 제품에서 이미 표준 동작이다 — 표준 파일트리(BC 골격)를 가진 dddjango는 경로→BC/계층→규칙 라우팅을 더 정밀하게 기계화할 수 있는 위치다.

### A-3. Windsurf rules: 4 활성화 모드 + 하드 문자 제한 (사실)

`.windsurf/rules/*.md`는 활성화 모드 4종: Manual(@호출), Always On, Model Decision
(description을 읽고 Cascade가 판단), Glob. 전역 규칙 6,000자·워크스페이스 규칙 파일당
12,000자의 하드 제한이 있다.
- 출처: https://windsurf.com/university/general-education/creating-modifying-rules (공식)
- «dddjango 시사점»: Cursor·Copilot·Windsurf가 독립적으로 같은 4모드(항상/글롭/모델판단/수동)로 수렴했다(추론: 이 수렴은 설계 정답에 가깝다는 신호). 문자 제한의 존재는 «전량 주입은 예산 위반»이라는 업계 합의의 물증이다.

### A-4. AGENTS.md: 최근접 파일 우선(nearest-file precedence) (사실)

AGENTS.md는 Linux Foundation 산하 Agentic AI Foundation이 관장하는 공개 표준으로,
6만+ 공개 저장소가 채택(2026 기준), OpenAI Codex·Google Jules·Cursor·Copilot·Aider 등
25+ 도구가 지원한다. 모노레포에서는 패키지마다 AGENTS.md를 두고 «디렉터리 트리에서 가장
가까운 파일이 우선»한다(OpenAI 저장소는 중첩 AGENTS.md 88개). 형식 규칙은 «그냥 마크다운»
뿐 — frontmatter·메타데이터 표준이 없다. 사용자 채팅 프롬프트가 파일 지시를 오버라이드한다.
- 출처: https://agents.md/ (공식), https://github.com/agentsmd/agents.md
- «dddjango 시사점»: AGENTS.md의 선별 메커니즘은 «디렉터리 근접성» 하나뿐이다 — 규칙 단위 ID·트리거 메타데이터가 없어 우리의 규칙 코퍼스(3,217 규범 문장)를 담기엔 해상도가 부족하고, 배포 타깃(두 판 미러) 문제도 다루지 않는다.

### A-5. Anthropic Agent Skills: progressive disclosure 3단 로딩 (사실)

2025-12 공개된 Agent Skills 표준(SKILL.md)은 3단 로딩이다: ① 기동 시 name+description만
(스킬당 ~100토큰), ② 관련 시 SKILL.md 본문 활성화(5,000토큰 이하 권장), ③ 참조 파일은 실행
중 필요할 때만. description은 «무엇을 하는가 + 언제 쓰는가»를 모두 담아야 라우팅이 작동한다.
OpenAI·Google·Copilot·Cursor가 수 주 내 채택.
- 출처: https://anthropic.skilljar.com/introduction-to-agent-skills (공식 코스), 표준 사이트 agentskills.io
- «dddjango 시사점»: dddjango의 SKILL frontmatter + «~할 때 로드한다» 문구는 이 표준의 정석 사용이다 — 다만 라우팅 단위가 «문서(스킬) 전체»라서, 문서 내부 606절·3,217문장 수준의 세분 공급은 표준 밖의 자체 설계(레지스트리)가 필요하다.

### A-6. 수렴 패턴 정리 (추론)

2026 현재 업계 선별 주입은 사실상 2개의 라우팅 신호로 수렴했다:
**(a) 경로 glob** (Cursor globs, Copilot applyTo, Windsurf glob, AGENTS.md 근접성,
CodeRabbit path_instructions — §4-3), **(b) 자연어 description을 모델이 읽고 판단**
(Cursor Agent-Requested, Windsurf Model Decision, Agent Skills). **심볼 기반·phase 기반
라우팅은 어떤 상용 표준에도 없다.** 규칙 «단위»(문장/조항)로 라우팅하는 상용 도구도 없다 —
전부 «파일» 단위다.
- «dddjango 시사점»: 규칙 단위 ID + phase(파이프라인 단계) 라우팅은 업계 표준이 비워둔 자리다 — 도입하면 차별화지만, 선례가 없으므로 자체 lint로 검증 가능성을 함께 설계해야 한다.

---

## 2. 발견 B — 규칙 파일 효과의 실증 연구 (2025-12 ~ 2026-06)

### B-1. 컨텍스트 파일은 공짜가 아니다: 효과 0 ~ 미미, 비용 +20% (사실)

ETH SRI Lab «Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding
Agents?»(2026-02, arXiv 2602.11988): 실제 GitHub 이슈 수백 건에서 다수 에이전트·모델로 측정한
결과, 컨텍스트 파일은 과제 성공률을 개선하지 못하면서 추론 비용을 20%+ 올렸다.
LLM 자동 생성 파일은 평균 -3%(악화), 사람이 쓴 파일은 +4%(미미한 개선). 원인 분석: 자동 생성
파일은 README·설정 등 에이전트가 어차피 탐색으로 찾을 정보를 중복 선탑재한다(저장소 문서를
제거하면 자동 생성 파일이 +2.7%로 유효해짐).
- 출처: https://arxiv.org/abs/2602.11988, https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd
- «dddjango 시사점»: «걸리는 규칙만» 원칙의 강력한 실증 근거 — 가치는 에이전트가 스스로 발견할 수 없는 규범(하우스룰·금지 표면·판정 소유)에 집중되고, 저장소에서 유추 가능한 내용의 상시 주입은 순손실이다.

### B-2. 규칙 갱신은 준수율을 올린다 +22.99%p — 그리고 규칙의 77.78%는 «AI 오류 교정»으로 개정된다 (사실)

«Rule Taxonomy and Evolution in AI IDEs»(2026-06, arXiv 2606.12231): 83개 오픈소스
프로젝트에서 규칙 7,310개 추출, 5대분류·25소분류 택소노미. 규칙 진화 이벤트 1,540건 분석 —
갱신 동인은 맥락 확장(29.17%)·보강(26.59%)이 주이고, 규칙 갱신 후 산출물 평균 준수율이
22.99% 상승. 실무자 99명 설문: 개발자는 아키텍처 제약을 가장 중요하다고 답했으나 실제
저장소 규칙은 저수준 워크플로·포매팅 위주(중요도-내용 괴리). 규칙 수정 동기 1위는
«AI의 오류를 교정하기 위해»(77.78%).
- 출처: https://arxiv.org/abs/2606.12231
- «dddjango 시사점»: 위반 사례→규칙 개정 경로는 예외가 아니라 규칙 수명주기의 주 경로다 — 온톨로지에 «개정 이력·개정 사유(위반 케이스 링크)» 필드를 1급으로 두는 것이 실무와 부합한다.

### B-3. Cursor rules 실증: 규칙은 코드베이스와 어긋나며 낡는다 (사실)

«Beyond the Prompt: An Empirical Study of Cursor Rules»(arXiv 2512.18925, MSR 2026 채택):
규칙이 시간이 지나며 코드베이스와 desync되는 staleness가 핵심 문제로 실증됨. 유지보수
도구 지원(규칙-코드 정합 검사)을 권고.
- 출처: https://arxiv.org/abs/2512.18925, https://dl.acm.org/doi/10.1145/3793302.3793367
- «dddjango 시사점»: 우리의 «lint 양방향 대조»(레지스트리↔스킬 문서↔검사기)는 이 논문이 «필요하지만 없다»고 지적한 바로 그 도구다 — 문서→검사기 방향 0인 현재 상태가 전형적 staleness 진입로다.

### B-4. 실무자 거버넌스 파일의 37%는 구조적 미달 (사실)

«Structural Quality Gaps in Practitioner AI Governance Prompts»(2026-04, arXiv 2604.21090):
GitHub의 AGENTS.md 계열 거버넌스 파일 34개를 5원칙 프레임워크로 평가 — 파일-모델 쌍의
37%가 구조 완결성 임계 미달, 판정 기준(rubric)·분류 기준 누락이 빈번. 자동 정적 분석으로
탐지·교정 가능하다고 제안.
- 출처: https://arxiv.org/abs/2604.21090
- «dddjango 시사점»: 규칙 문서 자체를 정적 분석(lint)하는 방향이 학계에서도 «해야 하는데 안 되어 있는 일»로 지목됨 — 결정적 검사기 27종을 이미 가진 dddjango는 선행 사례에 해당한다.

### B-5. 가이드 파일 자체를 튜닝하는 피드백 루프: 25.5% → 33.0% (사실)

«Probe-and-Refine Tuning of Repository Guidance for Coding Agents»(2026-06, arXiv
2606.20512): 합성 버그픽스 프로브로 가이드 파일(AGENTS.md류)의 결함을 진단→LLM 호출로
패치→반복. SWE-bench Verified에서 무가이드 25.5% → 정적 가이드 28.3% → probe-and-refine
33.0%(p<0.001). 개선의 정체는 패치 품질이 아니라 **파일 위치 탐색(navigational)** 가치
(커버리지 +14.5%p, 정밀도 불변).
- 출처: https://arxiv.org/abs/2606.20512
- «dddjango 시사점»: 가이드의 실증된 1차 가치가 «어디를 봐야 하는가»라면, 표준 파일트리+배치 결정 순서를 가진 dddjango 하우스룰은 정확히 그 고가치 구간에 있다 — 그리고 규칙 파일도 «측정→개정» 루프의 대상이 될 수 있다.

---

## 3. 발견 C — 정책 검색·온톨로지 기반 규칙 공급 연구

### C-1. OG-RAG(EMNLP 2025 main): 온톨로지 그라운딩 검색으로 사실 재현율 +55% (사실)

Microsoft OG-RAG(arXiv 2412.15235, EMNLP 2025): 도메인 문서를 온톨로지로 그라운딩한
하이퍼그래프로 표현, 하이퍼엣지=온톨로지에 근거한 사실 클러스터. 4개 LLM에서 정확 사실
recall +55%, 응답 정확도 +40%. 코드 공개(github.com/microsoft/ograg2).
- 출처: https://arxiv.org/abs/2412.15235, https://aclanthology.org/2025.emnlp-main.1674/
- «dddjango 시사점»: 온톨로지의 검증된 효용은 «검색 단위를 규범 있는 클러스터로 재편»하는 데 있다 — 규칙 3,217문장을 606절 그대로가 아니라 «규칙 단위+메타데이터»로 재편하면 같은 효과 경로를 탄다.

### C-2. RuleRAG: 규칙이 검색을 인도하면 Recall@10 +89.2% (사실)

RuleRAG(arXiv 2410.22353, 2024-10): 기호적 규칙을 ICL 데모로 넣어 검색기를 규칙 방향으로
인도(RuleRAG-ICL)하고 생성도 같은 규칙으로 귀속시킴 — 5개 벤치마크 평균 Recall@10 +89.2%,
EM +103.1%. 파인튜닝판(RuleRAG-FT)은 추가 개선.
- 출처: https://arxiv.org/abs/2410.22353
- «dddjango 시사점»: 규칙은 검색의 «대상»만이 아니라 «질의 확장기»로도 쓸 수 있다 — 예: diff에서 걸린 규칙의 상위/관련 규칙(레지스트리 링크)을 함께 공급하는 설계 근거.

### C-3. 정책 컴플라이언스에는 KG 증강이 유효 — 단, «형식 온톨로지 ≤ LLM 발견 스키마» (사실·중요)

«Knowledge Graph Representations for LLM-Based Policy Compliance Reasoning»(2026-04,
arXiv 2604.27713): AI 리스크 정책 3종을 형식 온톨로지 스키마 vs LLM이 발견한 개방 스키마
2가지로 KG화, 5개 모델·42개 정책 QA 과제 평가 — KG 증강은 5개 모델 전부 점수를 올렸고,
**LLM-발견 스키마가 형식 온톨로지와 대등하거나 우세**했다. 유사 계열로 GraphCompliance
(arXiv 2510.26309, 2025-10)는 정책 그래프와 실행 맥락 그래프의 정렬로 규제 준수를 판정.
- 출처: https://arxiv.org/abs/2604.27713, https://arxiv.org/pdf/2510.26309
- «dddjango 시사점»: D1에 직접 근거 — LLM 소비자 관점에서는 형식 온톨로지(RDF/OWL급 엄밀함)의 한계 효용이 낮다. 구조화 자체(KG化)가 이득의 원천이고 형식주의는 아니다.

### C-4. PolicyKG(2026-08): 기관 정책→디온틱 FOL→SHACL 파이프라인의 실제 비용 (사실)

PolicyKG(arXiv 2608.09028, 2026-08-10): 정책 PDF를 4단계 LLM 파이프라인(문장화→
의무/허용/금지 분류 86.9%→1차 디온틱 논리화 79.2% 수율→SHACL 생성)으로 변환.
SHACL 매핑은 LLM이 아니라 **결정적 규칙**으로 수행(감사 가능성): 의무→`sh:minCount 1`+
`sh:Violation`, 허용→`sh:Info`, 금지→`sh:maxCount 0`, 예외는 `deontic:overrides`.
어휘 그라운딩은 **YAML 레지스트리**(클래스·프로퍼티 열거)+폐집합 선택 프롬프트+사후 정준화
— 도메인 이전은 레지스트리 교체만으로. 한계: FOL 폴백률 20.8%, 외부 검증(LexDeMod)에서
permission F1=.038(어휘 사전확률 불일치), 단일 기관 평가.
- 출처: https://arxiv.org/html/2608.09028
- «dddjango 시사점»: 최신 SHACL 채택 사례조차 ① 어휘 통제는 YAML 레지스트리로, ② LLM↔형식 표현 변환부가 최대 실패 지점, ③ 의미 매핑은 결정적 규칙으로 — 3가지 모두 «YAML 뼈대 정본 + 결정적 lint» 설계를 지지한다. 단 «의무/허용/금지→심각도» 매핑 관례는 YAML 스키마에 차용할 가치가 있다.

### C-5. xpSHACL: SHACL 위반 리포트를 RAG+LLM으로 설명 (사실)

xpSHACL(arXiv 2507.08432, 2025-07): SHACL 검증 위반 리포트는 기계용이라 사람이 읽기
어렵다는 문제를, 위반→RAG로 규칙 맥락 검색→LLM 자연어 설명 생성으로 해결.
- 출처: https://arxiv.org/pdf/2507.08432
- «dddjango 시사점»: 위반 리포트에 «규칙 원문 링크(ID 앵커)»를 붙여 에이전트에게 되먹이는 설계의 학술 대응물 — 규칙 단위 ID가 있어야 이 경로가 열린다.

### C-6. Knowledge Activation(2026-03/06): 스킬을 «기관 지식 원자 단위»로 (사실+추론)

arXiv 2603.14805: 기관 지식(아키텍처 결정·절차·컴플라이언스 정책)을 Atomic Knowledge
Unit(AKU)로 구조화해 스킬 표준 위에 얹고, AKU들이 합성 가능한 지식 그래프를 이뤄 에이전트가
실행 중 순회. Yahoo 배치 사례(엔지니어 67명 설문): 주당 2.6시간 절감, NPS +35.
- 출처: https://arxiv.org/abs/2603.14805
- «dddjango 시사점»: «스킬 문서(산문 정본) + 그 위의 원자 단위 그래프(레지스트리 정본)» 2층 구조가 독립적으로 같은 결론에 도달한 사례 — dddjango 블루프린트의 분업 구도와 동형이다(추론).

---

## 4. 발견 D — 위반 리포트 → 에이전트 피드백 루프 실무

### D-1. Claude Code hooks: 결정적 차단·주입 (사실)

PreToolUse 훅이 차단 상태로 종료하면 모델 의도와 무관하게 도구 호출이 차단되고, PostToolUse
훅은 파일 쓰기 후 린터를 돌려 오류를 additionalContext로 에이전트 컨텍스트에 재주입한다.
«훅은 보증하고, 프롬프트는 제안한다»가 실무 정식화다. 18+ 이벤트(Stop·SubagentStop·
SessionStart 등).
- 출처: https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html, https://dotzlaw.com/insights/claude-hooks/ (보조; 공식 문서는 code.claude.com/docs 하위)
- «dddjango 시사점»: 이미 27종 결정적 검사기를 가진 dddjango는 집행층이 성숙 — 병목은 «검사기가 어느 규칙을 집행하는가»의 역방향 링크(문서→검사기 0)이며, 이것이 레지스트리가 채울 자리다.

### D-2. Semgrep × Cursor hooks(2025): 위반 0이 될 때까지 재생성 루프 (사실)

Semgrep 공식 블로그(2025): 에이전트 루프 종료 시 stop 훅이 변경 파일 전체를 Semgrep 스캔
→ 발견 사항 remediation을 프롬프트로 강제 → **위반이 모두 해소될 때까지 코드 재생성**.
«MCP는 도구를 노출할 뿐 사용을 보장하지 않는다 — 결정적 실행이 빠진 조각»이라고 명시.
- 출처: https://semgrep.dev/blog/2025/cursor-hooks-mcp-server/ (공식 블로그)
- «dddjango 시사점»: 위반 리포트 피드백 루프의 2026 표준형은 «훅(결정적 트리거)+스캐너(규칙 집행)+재생성(수렴 조건: 위반 0)»이다 — dddjango 검사기 27종을 이 3요소 루프에 정렬하면 된다.

### D-3. CodeRabbit path_instructions: 경로 glob으로 라우팅되는 LLM 리뷰 규칙 (사실)

`.coderabbit.yaml`의 `reviews.path_instructions`는 minimatch glob별로 자연어 리뷰 지침을
달아, 리뷰 대상 파일 경로에 매칭되는 지침만 LLM 리뷰어에 공급한다.
- 출처: https://docs.coderabbit.ai/configuration/path-instructions (공식)
- «dddjango 시사점»: «diff 경로 → 규칙 부분집합 → LLM» 라우팅이 리뷰 도구에서도 상용 표준 — 작성 시점(Cursor/Copilot)과 리뷰 시점(CodeRabbit) 양쪽 모두 경로 glob이 라우팅 키다.

### D-4. 루프의 확장: 코드가 아니라 «규칙 파일»을 고치는 루프 (사실)

B-5의 probe-and-refine은 위반/실패 신호로 코드가 아니라 가이드 파일 자체를 개정하는
루프이며, B-2의 설문(규칙 수정 동기 77.78%가 AI 오류 교정)은 실무에서 이 루프가 수동으로
이미 돌고 있음을 보여준다.
- «dddjango 시사점»: 피드백 루프는 2단으로 설계할 것 — ①위반→코드 재생성(단기), ②반복 위반→규칙 개정 제안(장기, 소유자 1인 심의 큐로).

---

## 5. 반례·주의

1. **컨텍스트 파일 회의론(B-1)**: 규칙 공급 자체가 성공률을 올린다는 보장이 없다 — 자동
   생성 규칙은 오히려 -3%, 비용 +20%. «더 많은 규칙 주입»이 아니라 «저장소에서 유추
   불가능한 규범만 정밀 주입»이 이득 구간이다. (2026-02)
2. **형식 온톨로지의 한계 효용(C-3)**: LLM 소비자 기준, LLM-발견 스키마가 형식 온톨로지와
   대등 이상 — RDF/OWL/SHACL 전면 도입의 근거로 «LLM이 더 잘 따른다»를 쓸 수 없다. (2026-04)
3. **SHACL 파이프라인의 실비용(C-4)**: 최신 사례도 FOL 폴백 20.8%, 도메인 밖 이전 시
   급락(F1=.038) — 1인 소유 코퍼스에 변환 계층을 얹는 비용은 과소평가하기 쉽다. (2026-08)
4. **규칙 staleness(B-3)**: 라우팅 메타데이터(glob·description)도 코드와 함께 낡는다 —
   라우팅 자체를 lint 대상으로 삼지 않으면 «걸리는 규칙만»이 «걸렸어야 할 규칙 누락»으로
   변질된다.
5. **중요도-내용 괴리(B-2)**: 개발자는 아키텍처 제약을 원하면서 저수준 규칙을 쓴다 —
   레지스트리 설계 시 규칙 분류축(아키텍처/워크플로/포매팅)을 두지 않으면 같은 함정에 빠진다.
6. **미러 일관성의 공백(추론)**: claude/codex 두 판 배포의 의미 미러 검증에 대응하는 업계
   표준·연구를 이번 조사에서 찾지 못했다(AGENTS.md는 단일 파일 지향, 도구별 파일 중복 시
   정합은 사용자 책임). 19문서쌍 대조는 자체 lint로 풀어야 할 dddjango 고유 문제로 보인다.

---

## 6. dddjango 시사점 정리

| P0 실측 문제 | 외부 근거 | 함의 |
|---|---|---|
| 규칙 단위 ID 없음, 번호 공간 5종 혼용 | A-6(업계는 파일 단위 라우팅뿐), C-5(위반→규칙 앵커 링크), C-6(AKU) | 규칙 단위 ID는 업계 표준이 비워둔 자리이며, 위반 피드백·검사기 역링크·미러 대조 모두의 전제조건 — 레지스트리 정본에서 단일 번호 공간으로 발급 |
| 문서→검사기 방향 0 | D-1·D-2(집행층은 성숙), B-3(staleness는 링크 부재에서 시작) | 레지스트리에 rule→checker 필드를 두고 lint로 양방향(25종 역지목과 대조) 검증 — 블루프린트의 «뼈대는 레지스트리 정본» 지지 |
| 두 판 미러 19쌍 무방비 | 반례 6(업계 공백) | 선례 없음 — 쌍둥이 필드(twin: claude↔codex)를 레지스트리 뼈대에 넣고 자체 lint로 대조하는 수밖에 없다 |
| «걸리는 규칙만» 공급 | A-1~A-6(경로 glob+description 2축 수렴), B-1(전량 주입은 순손실), D-3(리뷰 시점도 경로 키) | SKILL frontmatter(description 축)는 이미 정석 — 부족한 경로 축은 표준 파일트리를 이용해 «경로 glob → BC/계층 → 규칙 ID 집합» 매핑을 레지스트리에 기록, ⓓ 채널(파이프라인 단계 주입)은 업계에 없는 phase 축으로 유지·명문화 |
| D1: RDF/Turtle+SHACL vs YAML | C-3(형식 온톨로지 우위 없음), C-4(SHACL 사례도 어휘는 YAML, 매핑은 결정적 규칙, 변환부가 실패 지점), B-4(문서 정적 분석이 실효) | YAML 자체 형식 + 결정적 lint가 실무 스윗스팟 — SHACL에서는 심각도 매핑 관례(의무→Violation/허용→Info/금지→차단)만 어휘로 차용 |
| 소유자 1인 심의 | B-2(규칙 개정의 주 동인은 AI 오류 교정 77.78%), D-4 | 위반 통계→규칙 개정 제안을 자동 생성하되 심의는 1인 큐로 — 개정 사유·위반 케이스 링크를 레지스트리 필드로 |

---

## 7. 출처 목록 (21)

**공식 문서·표준**
1. Cursor Rules 공식 문서 — https://cursor.com/docs/rules
2. GitHub Copilot repository custom instructions — https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide
3. Windsurf rules(활성화 모드) — https://windsurf.com/university/general-education/creating-modifying-rules
4. AGENTS.md 공식 — https://agents.md/ · https://github.com/agentsmd/agents.md
5. Anthropic Agent Skills 공식 코스 — https://anthropic.skilljar.com/introduction-to-agent-skills
6. CodeRabbit path-based review instructions — https://docs.coderabbit.ai/configuration/path-instructions

**논문(연도 명시)**
7. OG-RAG (2024-12, EMNLP 2025 main) — https://arxiv.org/abs/2412.15235 · https://aclanthology.org/2025.emnlp-main.1674/
8. RuleRAG (2024-10) — https://arxiv.org/abs/2410.22353
9. Evaluating AGENTS.md (2026-02, ETH SRI) — https://arxiv.org/abs/2602.11988
10. Beyond the Prompt: Cursor Rules (2025-12, MSR 2026) — https://arxiv.org/abs/2512.18925 · https://dl.acm.org/doi/10.1145/3793302.3793367
11. Rule Taxonomy and Evolution in AI IDEs (2026-06) — https://arxiv.org/abs/2606.12231
12. Structural Quality Gaps in Practitioner AI Governance Prompts (2026-04) — https://arxiv.org/abs/2604.21090
13. Probe-and-Refine Tuning of Repository Guidance (2026-06) — https://arxiv.org/abs/2606.20512
14. Knowledge Activation: AI Skills as Institutional Knowledge Primitive (2026-03/06) — https://arxiv.org/abs/2603.14805
15. KG Representations for LLM-Based Policy Compliance Reasoning (2026-04) — https://arxiv.org/abs/2604.27713
16. GraphCompliance (2025-10) — https://arxiv.org/pdf/2510.26309
17. PolicyKG (2026-08) — https://arxiv.org/html/2608.09028
18. xpSHACL (2025-07) — https://arxiv.org/pdf/2507.08432

**실무 사례(보조 포함)**
19. Semgrep × Cursor Hooks (2025, 공식 블로그) — https://semgrep.dev/blog/2025/cursor-hooks-mcp-server/
20. Claude Code Hooks Complete Guide (보조) — https://hidekazu-konishi.com/entry/claude_code_hooks_complete_guide.html
21. Claude Code Hooks: Deterministic Control Layer (보조) — https://dotzlaw.com/insights/claude-hooks/
