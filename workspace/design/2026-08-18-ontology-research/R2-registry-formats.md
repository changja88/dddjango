# R2 — 레지스트리 형식 선례 조사 (D1 입력)

조사일: 2026-08-18 · 담당: 외부 자료 조사 레인 R2

## 조사 질문

«기계가 읽는 규칙 레지스트리»를 (a) YAML/JSON 자체 형식으로 구현한 선례와 (b) RDF/SHACL 표준을 채택한 선례를 비교한다. 각각의 실제 형식·필드 설계는 무엇이고, 성패는 어떠했는가. 특히:

1. 규칙 항목의 표준적 필드 구성(id·statement·owner·severity·enforcement·links)은 무엇으로 수렴하는가.
2. 소규모(수백 규칙·1인 심의)에서 표준(RDF/SHACL·OSCAL급) 채택이 이긴 사례와 진 사례는 무엇인가.

dddjango 맥락: 규범 문장 3,217개·606절·30문서, 규칙 단위 ID 부재, 번호 공간 5종 혼용, 검사기 27종 중 25종이 docstring으로 문서를 역지목(문서→검사기 방향 0), claude/codex 쌍둥이 19문서쌍, 소유자·심의자 1인. 블루프린트: 뼈대(ID·소유자·집행·쌍둥이)는 레지스트리 정본 + 산문은 스킬 문서 정본 + lint 양방향 대조. D1 = RDF/Turtle+SHACL vs YAML 자체 형식.

---

## A부. YAML/JSON 자체 형식 진영 — 발견들

### A-1. Semgrep 룰 형식 — «실행 가능 규칙 + 메타데이터 봉투»의 사실상 표준

[사실] Semgrep 룰은 YAML 1파일 = 1규칙 단위이며 최상위 필드는 `id`(기술어형 슬러그), `message`, `severity`(현행 LOW/MEDIUM/HIGH/CRITICAL, 구 ERROR/WARNING/INFO 하위호환), `languages`, `pattern(s)`, 그리고 자유 확장 `metadata` 맵이다. 공식 레지스트리에 기여하려면 모든 룰에 `metadata.technology`·`metadata.category`·`metadata.references`가 필수이고, `category: security`인 룰은 추가로 `cwe`·`owasp`·`confidence`·`likelihood`·`impact`·`subcategory`·`vulnerability class` 7종이 강제된다. 룰 id에는 `<language>/<framework>/<category>/...` 네임스페이스 관례가 있다.
- 출처: https://semgrep.dev/docs/writing-rules/rule-syntax , https://docs.semgrep.dev/contributing/contributing-to-semgrep-rules-repository
- [추론] 핵심 교훈은 «코어 스키마는 5필드로 최소, 나머지는 metadata 맵에 넣되 레지스트리 편입 시점에 lint로 필수화»라는 2단 구조다. 스키마를 처음부터 크게 만들지 않고 게이트에서 강제한다.
- «dddjango 시사점» 레지스트리 스키마는 최소 코어(id·statement·owner·enforcement)로 시작하고, 등급별 필수 필드(예: 집행형 규칙만 checker 링크 필수)를 lint 게이트로 강제하는 2단 설계가 검증된 패턴이다.

### A-2. Sigma 탐지 룰 명세 — 규칙 ID 수명주기·규칙 간 관계의 가장 정교한 선례

[사실] SigmaHQ의 Sigma 룰 명세(YAML 자체 형식, 보안 탐지 룰 수천 개 규모 커뮤니티 운영)는 규칙 단위 필드를 다음과 같이 규정한다: 필수 `title`(≤256자)·`logsource`·`detection`, 준필수 `id`(UUID v4, 전역 유일), `status`(5값: stable/test/experimental/deprecated/unsupported), `level`(심각도), `description`, `references`, `author`, `date`/`modified`(ISO 8601), `tags`, `falsepositives`, 그리고 규칙 간 관계 `related`(타입 5종: derived/obsolete/merged/renamed/similar + 상대 UUID). ID 재발급 규칙이 명문화되어 있다: «룰 로직이 달라지는 큰 변경, 기존 룰을 살려둔 채의 파생, 룰 병합 시에는 새 id로 작성하라».
- 출처: https://github.com/SigmaHQ/sigma-specification (specification/sigma-rules-specification.md)
- [추론] Sigma는 dddjango가 가진 문제 3개(규칙 단위 ID 부재, 규칙의 개정·파생·폐기 이력, 번호 재사용 혼란)에 대한 기성 답안을 모두 갖춘 유일한 선례다. 특히 «식별자(UUID·불변)와 제목(사람용·가변)의 분리», «status로 수명주기 표기», «related로 세대 교체 추적»이 핵심이다.
- «dddjango 시사점» 규칙 ID는 §번호·registry #번호 같은 위치·순서 기반 번호와 분리된 불변 식별자로 발급하고, status·related(derived/obsolete/renamed) 필드로 5종 번호 공간의 세대 교체를 흡수하는 것이 실전 검증된 설계다.

### A-3. Spectral 룰셋 — 레지스트리→문서 방향 링크(documentationUrl)의 선례

[사실] Spectral(OpenAPI lint) 룰셋은 YAML/JSON/JS로 쓰며, 룰 객체 필드는 `description`, `message`, `given`(JSONPath 선택자), `then`(적용 함수 = 집행 로직), `severity`(error/warn/info/hint 4단), `resolved`, `recommended`, `formats`, `documentationUrl`, `tags`이고, 룰셋 수준에는 `extends`(상속)·`overrides`·`aliases`·`functions`가 있다.
- 출처: https://docs.stoplight.io/docs/spectral/e5b9616d6d50c-rulesets , https://github.com/stoplightio/spectral/blob/develop/docs/guides/4-custom-rulesets.md
- [추론] 룰 항목 안에 «집행 로직(given/then)»과 «산문 문서 포인터(documentationUrl)»가 나란히 있다는 점이 중요하다. dddjango의 현황(검사기 docstring→문서 역방향만 존재, 문서→검사기 0)과 정반대로, 성숙한 lint 생태계는 규칙 정의 쪽이 문서를 가리키는 정방향 링크를 표준 필드로 갖는다.
- «dddjango 시사점» 레지스트리 항목에 `doc`(스킬 문서 § 앵커)과 `enforcement`(검사기 id 목록) 두 정방향 링크 필드를 두면, 기존 25종 docstring 역지목과 합쳐 lint 양방향 대조가 바로 성립한다.

### A-4. OPA Rego METADATA — 코드 내장 메타데이터(=dddjango 검사기 docstring 패턴)의 공식화

[사실] OPA는 정책 코드 위 주석 블록(`# METADATA` + YAML)으로 규칙 메타데이터를 붙인다. 필드는 `scope`(rule/document/package/subpackages), `title`, `description`, `related_resources`(URL 목록), `authors`, `organizations`, `schemas`, `entrypoint`, `custom`(자유 맵)이고, 런타임에 `rego.metadata.rule()`로 규칙 자신의 메타데이터를 읽어 위반 메시지에 심각도·설명을 실을 수 있다.
- 출처: https://www.openpolicyagent.org/docs/policy-language/#metadata
- [추론] dddjango 검사기 25종의 docstring 역지목은 OPA가 공식 기능으로 만든 것과 같은 방향(집행 코드에 규칙 신원 내장)이다. 즉 이 방향 자체는 건전하며, 부족한 것은 반대 방향과 그 대조뿐이다.
- «dddjango 시사점» 검사기 docstring의 규칙 지목을 자유 산문이 아니라 파싱 가능한 고정 표기(예: `Rule-ID:` 한 줄)로 승격하면, OPA처럼 코드 쪽 메타데이터를 lint가 기계적으로 수확해 레지스트리와 대조할 수 있다.

### A-5. ESLint 룰 meta — 1규칙 1문서 + meta.docs.url 관례

[사실] ESLint 룰은 구현 객체 안에 `meta`를 내장한다: `type`(problem/suggestion/layout), `docs.description`, `docs.url`(규칙 전용 문서의 안정 URL), `docs.recommended`, `fixable`, `schema`(옵션 스키마). 코어 규칙은 규칙당 문서 페이지 1개가 안정 URL로 존재하고 코드가 그 URL을 가리킨다.
- 출처: https://eslint.org/docs/latest/extend/custom-rules
- «dddjango 시사점» «규칙마다 안정된 문서 주소(§ 앵커) 1개 + 집행 코드가 그 주소를 지목»은 lint 생태계 공통 관례다 — § 앵커 91%인 dddjango는 이 관례의 전제 조건을 이미 충족한다.

### A-6. Vale — 산문 스타일 규칙의 YAML화 선례

[사실] Vale(문서 산문 linter)은 스타일 = YAML 룰 폴더로 운영한다. 각 룰은 `extends`(existence/substitution 등 12개 확장점 중 1개), `message`, `level`(suggestion/warning/error), `scope`(heading/sentence 등 적용 범위 선택자), 패턴으로 구성된다.
- 출처: https://vale.sh/docs , https://github.com/errata-ai/vale (vale-cli/vale)
- [추론] «산문으로 쓰인 규범 문장 중 일부는 형식 규칙으로 강등 가능하다»는 것을 대규모로 증명한 사례다. 단 Vale도 판단이 필요한 규칙은 YAML화하지 않고 사람 리뷰에 남긴다.
- «dddjango 시사점» 규범 문장 3,217개 전부를 레지스트리에 넣으려 하지 말고, Vale처럼 «기계 집행 가능 부분집합»만 구조화 대상으로 삼는 선별 기준이 필요하다 — 블루프린트의 뼈대/산문 분업과 정합한다.

### A-7. Backstage catalog-info.yaml — owner 필수·관계 자동 유도 봉투

[사실] Backstage 카탈로그는 Kubernetes풍 봉투(`apiVersion`/`kind`/`metadata`/`spec`)를 쓴다. `metadata.name`은 kind+namespace 안에서 유일(1–63자, 문자 집합 제한), `uid`는 시스템 발급이며 외부 참조 금지, `spec.owner`는 필수(«궁극 책임을 지는 단일 주체»), `spec.dependsOn`류 선언에서 역방향 관계(ownedBy/ownerOf)를 시스템이 자동 유도한다. 자유 확장은 `labels`/`annotations`(네임스페이스 접두 키)/`tags`/`links`(href+title+icon+type)로 분리한다.
- 출처: https://backstage.io/docs/features/software-catalog/descriptor-format/
- «dddjango 시사점» 소유자 1인이어도 `owner` 필드는 명시 필수로 두는 것이 표준이며(향후 검사기·에이전트가 «책임 주체» 필드를 소비), 관계는 한쪽만 선언하고 역방향은 lint가 유도·대조하는 편이 이중 기재 표류를 막는다 — 쌍둥이(claude/codex) 필드에 그대로 적용 가능.

### A-8. Cursor .mdc / AGENTS.md — «머리는 구조·몸통은 산문» 하이브리드와 무스키마 극단

[사실] Cursor 프로젝트 룰은 `.cursor/rules/*.mdc` 파일로, YAML frontmatter(`description`·`globs`·`alwaysApply`) + 마크다운 본문 구조다. frontmatter가 없는 일반 .md는 무시된다(구조 머리가 활성화 조건). 반대편 극단인 AGENTS.md는 «필수 필드가 없는 표준 마크다운»임을 명시한 무스키마 관례로, 6만+ 저장소·20+ 에이전트 도구가 채택했고, 중첩 시 «편집 대상 파일에 가장 가까운 AGENTS.md가 이긴다»는 우선순위만 정한다.
- 출처: https://cursor.com/docs/rules , https://agents.md/
- [추론] 에이전트 소비용 규칙 문서의 실전 스펙트럼은 «완전 무스키마(AGENTS.md, 채택 최대·기계 대조 0)»에서 «frontmatter 하이브리드(.mdc, 활성화 조건만 구조화)»까지이며, 어느 쪽도 규칙 단위 ID·집행 연동은 제공하지 않는다. dddjango 블루프린트(뼈대 레지스트리 분리)는 이 스펙트럼보다 한 단계 위의 요구이고, 그 요구를 채운 선례는 A-1·A-2(Semgrep·Sigma)처럼 «규칙 파일 자체가 레지스트리 항목»인 쪽이다.
- «dddjango 시사점» 스킬 문서에 frontmatter식 머리(문서 id·쌍둥이 짝·담당 § 목록)를 얹는 것만으로도 .mdc 수준의 기계 가독은 확보되며, 규칙 단위 뼈대는 별도 레지스트리가 맡는 분업이 선례상 자연스럽다.

### A-9. OpenControl — 자체 YAML의 성공과 한계 (역사적 사례)

[사실] OpenControl(compliance-masonry)은 OSCAL 이전 세대의 규정 준수 자체 YAML 스키마로, cloud.gov 등이 실사용했다. 공식 문서 스스로 «OSCAL의 초점은 정밀성, OpenControl 스키마의 초점은 사용성»이라 대비했고, OSCAL로의 흡수·대체가 논의됐으나 기존 채택 벤더의 이전 비용이 걸림돌로 기록됐다. 프로젝트는 이후 사실상 정체 상태다.
- 출처: https://open-control.org/faq/ , https://github.com/opencontrol/schemas , https://isimluk.com/posts/2020/12/gocomply-with-oscal-fedramp-introduction-to-opencontrol/ , https://github.com/usnistgov/OSCAL/issues/72
- [추론] 자체 YAML은 사용성으로 이기지만, 표준의 제도적 지원 없이는 생태계 유지가 어렵다는 사례. 단 dddjango는 외부 생태계 호환이 목표가 아니라 1인 저장소 내부 정합성이 목표이므로 이 실패 축(제도적 지원 부재)은 해당 없다.
- «dddjango 시사점» 자체 YAML의 진짜 위험은 «형식이 조악해서»가 아니라 «외부 표준과의 교환 요구가 생겼을 때의 이전 비용»이며, 이는 ID 안정성만 지키면 후일 기계 변환으로 흡수 가능하다.

---

## B부. 표준(OSCAL·RDF/SHACL) 채택 진영 — 발견들

### B-1. NIST OSCAL 카탈로그 모델 — 규칙 레지스트리 필드 설계의 참조 표준

[사실] OSCAL catalog는 통제(control) 집합의 기계가독 표현으로 XML/JSON/YAML 3표기를 제공한다. control은 `id`·`class`·`title`·`params`(문서 여러 곳에서 참조되는 매개변수)·`props`(name/value 구조화 주석)·`parts`(statement/guidance 등 산문의 논리 분할, 임의 중첩)·`links`(href+rel)·중첩 `controls`(통제 강화)로 구성되고, `group`으로 가족 단위 묶음을 만든다. OSCAL이 공식 지원하지 않는 데이터는 `prop`/`link`로 주석하라고 명시한다. 파일 변경 시 루트 UUID 재발급·last-modified 갱신이 규정이다.
- 출처: https://pages.nist.gov/OSCAL/learn/concepts/layer/control/catalog/ , https://pages.nist.gov/OSCAL-Reference/models/v1.1.2/catalog/json-reference/ , https://github.com/usnistgov/OSCAL
- [추론] OSCAL의 «산문은 part로 구조 안에 남기고, 기계 확장은 prop/link로 연다»는 설계는 필드 어휘로서 훌륭하며, 채택 여부와 무관하게 자체 YAML을 설계할 때의 필드 이름·의미 사전으로 쓸 가치가 있다.
- «dddjango 시사점» 레지스트리 항목의 확장 필드는 OSCAL처럼 «범용 prop(name/value) + link(rel/href)» 두 개의 열린 슬롯으로 통일하면 스키마 개정 없이 준-ID(D50·birth-enum·날짜 스탬프)류를 수용할 수 있다.

### B-2. OSCAL 채택 실측 — 표준의 무게가 만든 채택 공백 (2025)

[사실] 2025년 FedRAMP는 Rev5 인가 100건 이상을 처리했으나 OSCAL 제출은 0건이었고, FedRAMP 20x Phase One 파일럿 공식 참가자 중 기계가독 자료를 OSCAL로 구조화한 곳도 없었다. FedRAMP 20x의 Key Security Indicators는 단순 JSON 검증기 노선으로 출발했고, OSCAL Foundation이 사후에 이를 OSCAL 카탈로그로 재표현하는 형국이다. 한편 RFC-0024는 2026년 9월까지 기계가독 패키지를 의무화하는 일정을 걸어 두었다.
- 출처: https://securityboulevard.com/2025/12/regscale-open-sources-oscal-hub-to-further-compliance-as-code-adoption/ (2025-12), https://www.fedramp.gov/20x/ , https://secureframe.com/blog/fedramp-20x , https://github.com/FedRAMP/community/discussions/3
- [추론] 표준을 만든 기관의 앞마당(연방 인가)에서조차, 의무화 압력 없이는 대형 조직도 OSCAL을 안 쓴다. 원인으로 지목되는 것은 대형 OSCAL 파일 관리의 복잡성이다. 1인 심의 체제에서 이 무게는 치명적이다.
- «dddjango 시사점» «표준이라서 채택»은 소비자(에이전트·검사기·lint·1인 심의자)가 그 표준을 직접 소비할 때만 정당화된다 — dddjango 소비자 중 OSCAL/RDF를 네이티브로 읽는 주체는 0이다.

### B-3. compliance-trestle — «정본 JSON + 사람용 마크다운 생성·재조립» 워크플로의 실증

[사실] compliance-trestle(CNCF 샌드박스, IBM 기원, oscal-compass 커뮤니티 유지)은 OSCAL JSON/YAML을 정본으로 두고, 큰 OSCAL 구조를 사람이 편집 가능한 마크다운/CSV 조각으로 분해 생성(generate)한 뒤, 편집 결과를 검증하며 OSCAL로 재조립(assemble)하는 왕복 워크플로를 제공한다. 목적은 «규정 준수 산문 유지보수를 DevOps(Git·PR 리뷰) 영역으로 가져오는 것»이다.
- 출처: https://github.com/oscal-compass/compliance-trestle
- [추론] dddjango 블루프린트(뼈대는 레지스트리 정본·산문은 문서 정본·lint 양방향 대조)와 가장 구조가 가까운 실증 사례다. 단 trestle은 산문까지 OSCAL 정본에 넣고 마크다운을 파생물로 삼는 «단일 정본+생성» 모델이라, dddjango의 «이중 정본+대조» 모델보다 정합성은 강하지만 전용 도구 의존이 크고 산문 저작 경험이 나빠진다(그래서 도구가 필요해졌다).
- «dddjango 시사점» 산문까지 레지스트리에 넣는 단일 정본 노선은 trestle급 전용 도구를 스스로 만들 각오가 필요하므로, 산문은 스킬 문서 정본에 남기는 블루프린트의 분업이 1인 체제에 맞다 — 대신 trestle이 증명한 «재조립 시 검증» 지점을 lint 양방향 대조가 맡아야 한다.

### B-4. SHACL로 규제 요건을 모델링한 성공 사례 (2023)

[사실] Heimsbakk·Torkelsen(2023, arXiv:2309.02723)은 공공 부문의 복잡한 규제 요건(복수 대안 요건 포함)을 SHACL 제약으로 표현했다. 닫힌 세계 가정이 규정 준수 검증에 OWL보다 적합했고, 온톨로지 경험이 없는 도메인 전문가도 모델을 유지보수할 수 있었으며, SHACL 엔진으로 인스턴스 데이터의 적합성 검증이 실용적이었다고 보고한다.
- 출처: https://arxiv.org/abs/2309.02723
- [추론] SHACL이 «규칙 레지스트리»로 작동한 실증이지만, 전제가 다르다: 검증 대상이 RDF 인스턴스 데이터였고(즉 데이터 파이프라인 전체가 이미 RDF), 셋업을 이끈 저자들이 시맨틱 웹 전문 컨설턴트다. dddjango의 검증 대상은 마크다운 문서·Python 검사기·git 저장소이고 RDF 인스턴스가 아니다.
- «dddjango 시사점» SHACL의 승리 조건은 «검증 대상 데이터가 이미 그래프»일 때다 — dddjango가 SHACL을 쓰려면 문서·검사기·쌍둥이 관계를 먼저 RDF로 승격하는 선행 공사가 필요하며, 그 공사 자체가 D1의 실질 비용이다.

### B-5. SHACL의 비용 실측 — 학습 곡선·검증기 성능·실사용 제약의 단순성

[사실] MuleSoft Labs의 json-ld-schema 프로젝트는 존재 이유로 «SHACL은 강력하지만 쓰기와 배우기가 어렵고, SHACL 검증기 성능은 구문적 JSON Schema 검증기에 크게 못 미친다»를 명시하며, JSON Schema 문법으로 SHACL 의미론을 흉내 내는 우회로를 제안했다. SHACL 리뷰 논문(arXiv:2112.01441)은 실사용 프로젝트 13개를 조사해 가장 흔한 제약이 cardinality·class·datatype·disjunction 수준임을 보고한다 — 즉 실무는 SHACL 표현력의 단순한 부분집합만 쓴다.
- 출처: https://github.com/mulesoft-labs/json-ld-schema , https://arxiv.org/pdf/2112.01441 , https://book.validatingrdf.com/bookHtml011.html
- [추론] 실무 SHACL 사용의 대부분(카디널리티·타입·필수 필드)은 JSON Schema/자체 lint로 동등하게 표현 가능하다. SHACL만의 차별력(그래프 경로 제약·추론 연계)이 필요해지기 전까지는 표준 채택의 편익이 학습·도구 비용을 못 넘는다.
- «dddjango 시사점» dddjango 레지스트리에 필요한 제약(ID 유일성·필수 필드·참조 무결성·쌍둥이 대칭)은 전부 SHACL의 «단순 부분집합»에 속하므로, JSON Schema + 자체 lint로 손실 없이 구현된다.

### B-6. schema.org — RDF/Turtle 정본이 소규모 편집 체제에서 굴러가는 반대편 실증

[사실] schema.org는 어휘 정본을 Turtle 파일로 GitHub 저장소에서 편집하며(«editorial work is conducted in Turtle format», RDF Schema 기반), 스테이징 사이트를 거치는 주기적 릴리스 절차를 운영한다.
- 출처: https://schema.org/docs/developers.html , https://github.com/schemaorg/schemaorg
- [추론] RDF 정본이 소규모 편집 체제에서 지속 가능함을 보이는 사례지만, 결정적 차이가 있다: schema.org의 산출물 자체가 RDF 어휘이고 소비자가 RDF 도구다. 형식과 소비자가 일치할 때 표준이 이긴다.
- «dddjango 시사점» 소비자가 RDF-네이티브가 아닌 한 Turtle 정본의 이점(외부 도구 재사용)은 발생하지 않는다 — 단, YAML 레지스트리의 ID·관계 설계를 깨끗이 해 두면 후일 Turtle 투영(YAML→RDF 기계 변환)은 일방향 파생물로 언제든 추가할 수 있다.

---

## C부. 필드 설계 수렴 — 시스템 횡단 비교

[추론·종합] 위 시스템들을 겹치면 규칙 항목 필드는 다음으로 수렴한다(괄호는 근거 시스템):

| 필드 축 | 수렴 형태 | 근거 |
|---|---|---|
| id | 불변·전역 유일. 위치/순서 번호와 분리. UUID(Sigma) 또는 경로 네임스페이스 슬러그(Semgrep·ESLint·OSCAL `ac-2`) | A-1, A-2, B-1 |
| statement | title(짧은 사람용) + description/message(위반 시 보일 문장) 분리 | A-1, A-2, A-3, A-4 |
| severity/level | 3~4단 고정 어휘 (error/warn/info·LOW~CRITICAL) | A-1, A-3, A-6 |
| status(수명주기) | stable/test/experimental/deprecated/unsupported | A-2 |
| owner | 필수 명시(1인 조직이어도), 시스템이 역방향 관계 유도 | A-7 |
| enforcement | 규칙 쪽에서 집행기를 지목(given/then 내장 또는 검사기 id 참조) + 코드 쪽 역지목의 쌍 | A-3, A-4, A-5 |
| links | rel+href 구조(문서 § 앵커·외부 참조), 규칙→문서 방향이 표준 필드 | A-3, A-5, B-1 |
| related(규칙 간) | 타입 있는 관계(derived/obsolete/merged/renamed/similar) | A-2 |
| 확장 슬롯 | 자유 맵 1개(metadata/custom/prop+annotations)로 격리, 필수화는 lint 게이트에서 | A-1, A-4, A-7, B-1 |

모든 성공 사례가 공유하는 3원칙:
1. 코어 스키마는 작게, 확장은 격리된 자유 슬롯으로 (Semgrep metadata·OPA custom·OSCAL prop·Backstage annotations).
2. 식별자와 사람용 이름의 분리 + ID 재발급 규정 명문화 (Sigma).
3. 규칙↔집행↔문서의 링크를 양방향 모두 표준 필드화하고 도구가 대조 (Spectral documentationUrl + OPA rego.metadata + ESLint meta.docs.url).

---

## D부. 반례·주의

1. **표준 채택이 이긴 조건은 「소비자가 그 표준의 네이티브」일 때뿐이다.** schema.org(B-6)와 Heimsbakk 사례(B-4)는 산출물·검증 대상이 애초에 RDF였다. 반대로 OSCAL은 만든 기관의 앞마당에서도 의무화 전까지 제출 0건(B-2)이었다. [사실+추론]
2. **자체 YAML의 실패 축은 형식이 아니라 생태계다.** OpenControl(A-9)은 사용성으로 이기고 제도적 지원 부재로 정체했다. 1인 내부 저장소인 dddjango에는 이 실패 축이 없지만, 반대로 «외부와 교환할 일이 생기면 이전 비용이 있다»는 잔여 위험은 남는다 — ID 안정성이 그 보험이다. [추론]
3. **frontmatter·AGENTS.md류의 가벼움을 과신하지 말 것.** 채택은 넓지만 규칙 단위 ID·집행 연동·수명주기를 전혀 제공하지 않으므로(A-8), dddjango의 요구(3,217문장·검사기 27종 연동)는 이 급으로는 못 채운다. [추론]
4. **단일 정본(산문까지 레지스트리) 노선은 도구 비용이 크다.** trestle(B-3)은 그 노선을 성립시키기 위해 CNCF 프로젝트 하나가 필요했다. 1인 체제가 흉내 낼 규모가 아니다. [추론]
5. **Sigma의 UUID id는 grep 가독성이 나쁘다.** dddjango 소비자에 사람·에이전트가 포함되므로, Sigma의 수명주기 규정은 가져오되 id 표기는 Semgrep/OSCAL식 의미 있는 슬러그가 더 맞을 수 있다 — 단 슬러그는 개명 유혹이 생기므로 «개명은 related.renamed로만」 규정을 함께 가져와야 한다. [추론]
6. **본 조사의 한계.** 검색 요약 중 «FedRAMP 2025 OSCAL 제출 0건»은 2차 보도(Security Boulevard, 2025-12) 기반으로 원자료를 직접 검증하지 못했다. 또한 «수백 규칙·1인 심의» 규모에서 RDF/SHACL을 채택했다가 명시적으로 철회한 공개 기록은 찾지 못했다(부재의 증거이지 증거의 부재일 수 있음). [사실(한계 고지)]

---

## E부. dddjango 시사점 정리 (D1 판단 재료)

1. **D1은 YAML 자체 형식이 우세하다.** 근거: (a) dddjango 소비자 4종(에이전트·검사기·lint·사람) 중 RDF 네이티브가 0 (B-2·B-6의 승리 조건 불충족), (b) 필요한 제약 전부가 SHACL 단순 부분집합 = JSON Schema/자체 lint로 등가 구현 가능(B-5), (c) 1인 심의 체제에서 표준의 도구·학습 비용이 편익을 초과(B-2·B-3), (d) 성공한 규칙 레지스트리 실례(Semgrep·Sigma·Spectral·Vale)가 전부 자체 YAML(A부).
2. **단, «표준에서 어휘를 훔쳐 오는» 절충이 최선이다.** OSCAL의 prop/link 확장 슬롯(B-1), Sigma의 id·status·related 수명주기(A-2), Spectral의 documentationUrl(A-3), Backstage의 owner 필수·관계 자동 유도(A-7)를 자체 YAML 필드로 이식한다.
3. **ID 설계가 5종 번호 공간 문제의 해법이다.** 규칙 ID는 §번호·순서와 분리된 불변 슬러그로 발급하고, § 앵커는 ID의 속성(위치 링크)으로 강등한다. 기존 번호들(registry #1~27·의사결정 #N 등)은 related/링크로 매핑해 흡수한다.
4. **양방향 lint의 형태가 선례로 확정된다.** 레지스트리→검사기(`enforcement` 필드) + 검사기→레지스트리(docstring의 파싱 가능한 `Rule-ID:` 표기) + 레지스트리→문서(`doc` § 앵커 링크)를 lint가 삼각 대조. 현재 0인 문서→검사기 방향은 레지스트리를 경유해 자동으로 생긴다.
5. **RDF 문은 닫는 게 아니라 미루는 것이다.** ID·관계를 깨끗이 설계한 YAML은 후일 Turtle/SHACL 투영을 기계 변환으로 추가할 수 있다(B-6). 지금 SHACL을 채택하면 선행 공사 비용을 즉납, YAML로 시작하면 그 비용을 필요 시점까지 이연 — 되돌리기 어려운 결정이 아니게 된다.
6. **산문은 레지스트리에 넣지 않는다.** trestle(B-3)의 교훈: 산문까지 단일 정본화하려면 전용 도구가 필요하다. 블루프린트의 «뼈대 레지스트리 + 산문 스킬 문서» 분업이 선례 지형과 정확히 부합한다.

---

## 인용 출처 목록 (23)

1. https://pages.nist.gov/OSCAL/learn/concepts/layer/control/catalog/
2. https://pages.nist.gov/OSCAL-Reference/models/v1.1.2/catalog/json-reference/
3. https://github.com/usnistgov/OSCAL
4. https://www.openpolicyagent.org/docs/policy-language/#metadata
5. https://docs.stoplight.io/docs/spectral/e5b9616d6d50c-rulesets
6. https://github.com/stoplightio/spectral/blob/develop/docs/guides/4-custom-rulesets.md
7. https://semgrep.dev/docs/writing-rules/rule-syntax
8. https://docs.semgrep.dev/contributing/contributing-to-semgrep-rules-repository
9. https://github.com/SigmaHQ/sigma-specification
10. https://agents.md/
11. https://cursor.com/docs/rules
12. https://backstage.io/docs/features/software-catalog/descriptor-format/
13. https://eslint.org/docs/latest/extend/custom-rules
14. https://vale.sh/docs
15. https://securityboulevard.com/2025/12/regscale-open-sources-oscal-hub-to-further-compliance-as-code-adoption/
16. https://www.fedramp.gov/20x/
17. https://secureframe.com/blog/fedramp-20x
18. https://github.com/oscal-compass/compliance-trestle
19. https://arxiv.org/abs/2309.02723
20. https://github.com/mulesoft-labs/json-ld-schema
21. https://arxiv.org/pdf/2112.01441
22. https://schema.org/docs/developers.html (+ https://github.com/schemaorg/schemaorg )
23. https://open-control.org/faq/ (+ https://github.com/opencontrol/schemas , https://isimluk.com/posts/2020/12/gocomply-with-oscal-fedramp-introduction-to-opencontrol/ )
