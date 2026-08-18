# R4 — 단일 정본 → 다중 렌더링 · 의미 등가성 검사

조사일: 2026-08-18 · 담당: 외부 자료 조사(레인 R4) · 방법: WebSearch/WebFetch 1차 출처 우선

## 0. 조사 질문

한 정본에서 두 플랫폼 변형(claude판/codex판)을 만들거나, 손으로 쓴 두 변형의 «의미 등가성»을 기계 검사하는 검증된 기법은 무엇인가?

P0 실측 맥락(전제):
- claude/codex 두 판 배포, 의미 미러 19문서쌍이 무방비 상태이고 규범 정면 충돌 표류 2건이 실증됨.
- 정규화(개명·표기 치환·전용 절 제외)만으로 7쌍 중 4쌍 잔차 0 — 정규화 기반 등가성 검사의 실전 운용 사례와 함정(정규화 규칙 자체의 표류)을 확인해야 함.
- 규칙 단위 ID는 아직 없음(§ 앵커 91%만 강함).

---

## 1. 발견

### 축 A — 단일 소스 → 다중 타깃 렌더링(조건부 콘텐츠)

**A-1. DITA 조건부 처리(profiling) + DITAVAL — 표준화된 단일 소스 다변형 기법** 〔사실〕
- OASIS DITA 1.3 표준은 `@audience`, `@platform`, `@deliveryTarget`, `@props` 등의 프로파일링 속성으로 요소 단위 조건을 달고, 처리 시점에 DITAVAL 프로파일 파일로 포함/제외/플래그를 결정하는 메커니즘을 명세한다. 기본값은 "미정의 조건 = include"이며 DITAVAL로 기본을 exclude로 뒤집을 수 있다.
- 출처: https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/condproc.html
- «dddjango 시사점» claude/codex 차이를 "다른 문서 2벌"이 아니라 "한 문서 + `platform=claude|codex` 속성"으로 표현하는 것이 테크니컬 라이팅 업계의 표준 답안이다 — 등가성 검사가 아예 필요 없어지는 구조.

**A-2. Asciidoctor `ifdef`/`ifndef`/`ifeval` — 경량 마크업에서의 같은 패턴** 〔사실〕
- 전처리 지시자로 문서 속성 존재/값에 따라 라인을 포함·제외한다. 파싱 전 단계라 문서 구조를 인식하지 못하며(verbatim 블록 안에서도 실행), 이스케이프 관리가 필요하다는 주의점이 공식 문서에 명시돼 있다.
- 출처: https://docs.asciidoctor.org/asciidoc/latest/directives/conditionals/
- «dddjango 시사점» 마크다운 스킬 문서에도 같은 패턴(예: 주석 마커 `<!-- claude-only -->` + 빌드 스크립트)을 자작으로 이식할 수 있으나, "구조 무인식 전처리"의 함정(코드 블록 내 오발동, 이스케이프)까지 따라온다.

**A-3. 단일 소스 + 조건 태그의 유지보수 비용** 〔사실(업계 보조 출처) + 추론〕
- 조건 태그가 산재한 콘텐츠는 오류에 취약해지고, 조건 로직 파싱 층이 늘수록 오독 위험이 커진다는 것이 단일 소싱 실무 문헌의 공통 경고다(보조 출처: Paligo/Archbee 등 벤더 블로그, https://paligo.net/blog/content-reuse/what-is-single-source-of-truth-ssot/ ).
- 추론: 조건 분기가 문서의 소수 지점(P0 실측: "전용 절 제외"가 정규화 규칙의 한 축이었다는 점에서 전용 절은 국소적)에 몰려 있으면 단일 소스가 유리하고, 두 판의 차이가 문서 전반의 어조·구성까지 번져 있으면 단일 소스 전환 비용이 급등한다.
- «dddjango 시사점» P0에서 "정규화만으로 4/7쌍 잔차 0"이면 차이가 국소적이라는 증거 — 이 4쌍은 단일 정본 + 조건부 렌더링으로 즉시 전환 가능한 후보다.

### 축 B — 손으로 쓴 두 변형의 동기화: i18n 번역 동기화 모델 (가장 성숙한 선례)

**B-1. GNU gettext의 msgid↔msgstr 단위 쌍 + `msgmerge` + fuzzy 플래그** 〔사실〕
- gettext는 원문(msgid)과 번역(msgstr)을 "메시지 단위"로 쌍 지운다. 원문이 바뀌면 `msgmerge`가 새 템플릿(POT)과 기존 PO를 병합하면서, 살짝 바뀐 msgid에 대해 옛 번역을 짝지어 주되 **fuzzy 플래그**를 찍는다. fuzzy는 "이 번역은 더 이상 정확하지 않을 수 있음"의 기계 판정이고, 최종 판단(수정 후 플래그 제거)은 사람 몫이다.
- 출처: https://www.gnu.org/software/gettext/manual/html_node/Fuzzy-Entries.html , https://www.gnu.org/software/gettext/manual/html_node/msgmerge-Invocation.html
- «dddjango 시사점» "소스가 바뀌면 미러를 기계적으로 stale 판정하고, 등가성 회복 확인은 사람이 한다"는 40년 검증된 분업 — 단, 이 모델은 **단위 수준 쌍(ID)이 존재해야만 성립**한다.

**B-2. mdbook-i18n-helpers(Google, Comprehensive Rust 운영) — fuzzy 시 원문 폴백** 〔사실〕
- mdbook 번역 워크플로: `mdbook-xgettext`로 원문 추출 → `msgmerge --update`로 갱신 → **fuzzy로 표시된 항목은 렌더링 시 번역을 버리고 원문을 그대로 출력**한다. 즉 "확인 안 된 미러는 배포하지 않고 정본으로 폴백"이 기본 동작이다. Comprehensive Rust가 18개 언어 번역을 이 체계로 운영 중.
- 출처: https://github.com/google/mdbook-i18n-helpers/blob/main/i18n-helpers/USAGE.md , https://github.com/google/mdbook-i18n-helpers
- «dddjango 시사점» codex판의 어떤 절이 stale 판정되면 "낡은 codex 절을 그대로 배포"하지 말고 "claude 정본 절로 폴백"하는 안전 기본값을 설계할 수 있다.

**B-3. mdbook-i18n-normalize — «정규화 규칙 자체의 표류»의 실증 사례와 해법** 〔사실〕
- 도구 버전이 바뀌며 메시지 추출 규칙이 바뀌자(0.1.0: 리스트 전체가 1개 msgid → 0.2.0: 항목별 msgid), 기존 PO 파일의 메시지가 렌더러가 기대하는 형태와 더 이상 일치하지 않게 됐다. 프로젝트는 이를 위해 **전용 마이그레이션 도구 `mdbook-i18n-normalize`**를 만들어 기존 번역을 보존한 채 새 형식으로 1회 변환하게 했다.
- 출처: https://github.com/google/mdbook-i18n-helpers/blob/main/i18n-helpers/USAGE.md
- «dddjango 시사점» P0가 우려한 "정규화 규칙의 표류"는 실재하는 운영 문제이며, 검증된 대응은 (1) 정규화 규칙을 버전 관리하고 (2) 규칙이 바뀔 때 기존 자산을 새 규칙으로 일괄 이관하는 마이그레이션 도구를 함께 배포하는 것이다.

**B-4. Kubernetes 문서 로컬라이제이션 — git 추적 스크립트 + 결정적 triage(2026)** 〔사실〕
- Kubernetes는 `upstream_changes.py`(특정 파일의 원문 변경 확인), `diff_l10n_branches.py`(로컬라이제이션 브랜치의 outdated 파일 목록화) 스크립트와 lastmod 경고로 표류를 추적해 왔고, "git만으로는 원문 변경 중 무엇을 번역에 반영해야 하는지 알 수 없어 병합 순간부터 사실상 unsupported가 된다"는 문제를 공식적으로 인정한다. 원칙은 upstream(영문)-first: 오류는 원문에서 먼저 고치고 미러에 반복 적용.
- 2026-06 컨트리뷰터 블로그(LFX 멘토십 결과): **결정적(deterministic) 마크다운 인식 triage 스크립트**가 번역 페이지와 영문 소스를 비교해 구조 신호(제목·코드 블록·앵커 누락)와 기술 신호(버전 참조·API 값·기능 상태 차이)를 뽑아 `Orphan / Strong signal / Moderate signal / No signal` 4단계로 분류한다. AI는 "검토 맥락 요약" 보조에만 쓰고 최종 결정은 사람 리뷰어가 한다. 원칙 문구: *"Automation should protect reviewer attention, not consume it."*
- 출처: https://github.com/kubernetes/website/blob/main/content/en/docs/contribute/localization.md , https://www.kubernetes.dev/blog/2026/06/26/human-centered-automation-kubernetes-localization-ai-era/ (2026-06-26)
- «dddjango 시사점» 대규모 프로젝트조차 "완전 자동 등가성 판정"을 포기하고 「결정적 신호 추출 → 등급 분류 → 사람 결정」으로 수렴했다 — dddjango의 미러 lint도 pass/fail 이분법보다 신호 등급 리포트가 현실적 종착점이다.

**B-5. Docusaurus + Crowdin — 플랫폼 위임형 동기화와 그 함정** 〔사실〕
- Docusaurus 공식 문서는 Crowdin 연동 시 "번역이 소스 파일과 항상 일치하도록 유지되어 out-of-date 번역을 다룰 필요가 없다"고 안내한다(플랫폼이 소스 갱신→재번역 큐를 관리). 단, Crowdin이 MDX의 JSX를 내장 HTML로 오파싱해 다운로드된 번역이 빌드를 깨는 함정도 같은 문서에 명시돼 있다.
- 출처: https://docusaurus.io/docs/i18n/crowdin , 워크플로 참고: https://www.sphinx-doc.org/en/master/usage/advanced/intl.html (Sphinx도 동일한 gettext 카탈로그 모델)
- «dddjango 시사점» 동기화를 외부 플랫폼/도구에 위임해도 "파서가 소스 형식을 오해하는" 계층에서 새 표류가 생긴다 — 미러 검사기가 마크다운을 어떻게 파싱하는지 자체가 검증 대상이다.

### 축 C — 구조적/의미적 diff 도구

**C-1. difftastic / diffsitter — 구문 인식 diff, 그러나 의미 판정은 아님** 〔사실 + 추론〕
- difftastic은 tree-sitter로 30여 언어를 구문 트리로 파싱해 비교하므로 포매팅·개행 변화는 변경으로 보고하지 않는다. diffsitter도 AST 위에서 diff를 계산해 공백류 차이를 무시한다. 단 difftastic 매뉴얼 스스로 트리 diff의 한계를 논한다: 구조가 다르면(`"foo"` vs `["foo"]`) 의미가 비슷해도 전혀 다른 것으로 취급하고, 최소 diff 보장·성능 문제가 있다.
- 출처: https://difftastic.wilfred.me.uk/ , https://difftastic.wilfred.me.uk/tree_diffing.html , https://github.com/afnanenayet/diffsitter
- 참고(2024 논문): AST diff 도구의 정확도 벤치마크와 리팩토링 인지 diff 연구 — https://arxiv.org/pdf/2403.05939
- «dddjango 시사점» 구조적 diff는 "표기 잡음 제거"까지만 해주는 정규화의 일종이며, 의미 등가성 판정기가 아니다 — 미러 잔차를 사람이 읽기 좋게 줄여주는 프레젠테이션 계층으로 쓰는 것이 올바른 위치다.

**C-2. oasdiff — "파싱 → 모델 정렬 → diff"의 도메인 특화 성공 사례** 〔사실〕
- OpenAPI 명세 2벌을 비교해 509종의 변경(breaking/non-breaking)을 분류한다. 핵심 설계: 텍스트가 아니라 파싱된 모델을 비교하고, 비교 전에 **`--flatten-allof`로 allOf를 병합 등가형으로 정규화**해 거짓 양성을 줄이며, 이름이 바뀐 path parameter도 정렬(align) 후 대응시킨다.
- 출처: https://github.com/oasdiff/oasdiff , https://github.com/oasdiff/oasdiff/blob/main/docs/ALLOF.md
- «dddjango 시사점» "정규화 후 비교 + 변경을 유형 분류(파괴적/비파괴적)"는 규칙 코퍼스에도 그대로 이식 가능한 틀 — 미러 잔차를 '규범 충돌(파괴적)/표현 차이(비파괴적)'로 분류하는 lint가 목표 형태다.

**C-3. Pandoc AST — 마크다운의 실용적 정준형(canonical form)** 〔사실〕
- Pandoc은 모든 입력을 공통 AST로 파싱하며 `pandoc -t native`/JSON으로 그 정준 표현을 얻을 수 있다. AST는 의도적으로 "최소 공통분모"라 포매팅 세부는 버려진다 — 즉 마크다운 표기 차이를 지운 구조 비교의 기성 도구로 쓸 수 있다.
- 출처: https://pandoc.org/using-the-pandoc-api.html , https://pandoc.org/MANUAL.html
- «dddjango 시사점» 자작 정규화 파이프라인의 앞단(표기·공백·강조 문법 차이 제거)을 Pandoc AST 직렬화로 대체하면 정규화 규칙 자작분을 줄일 수 있다.

### 축 D — 정규화 후 비교(canonicalization) 표준

**D-1. W3C Canonical XML(C14N) — "정규화 후 octet 비교 = 논리 등가"의 원형** 〔사실〕
- C14N의 명시적 목적이 바로 "XML 문서 쌍의 논리적 등가성 판정": 속성 순서·공백·엔티티 확장·네임스페이스 선언 등 비의미적 차이를 제거한 정준형을 만들고, 두 정준형이 octet 단위로 같으면 (일부 예외를 제외하고) 논리적으로 등가로 본다. 디지털 서명의 기반.
- 출처: https://www.w3.org/TR/xml-exc-c14n/ , https://en.wikipedia.org/wiki/Canonical_XML , https://www.xml.com/pub/a/ws/2002/09/18/c14n.html
- 주의〔사실〕: C14N 자체가 1.0(2001)/1.1(2008)/Exclusive(2002)/2.0(초안) 여러 버전으로 갈라졌다 — 정준화 규칙도 표류한다는 표준계의 실증.
- «dddjango 시사점» "정규화 잔차 0 → 등가 판정"은 표준계가 승인한 방법론이되, 등가의 정의가 정규화 규칙 버전에 종속된다는 점까지 세트로 받아들여야 한다.

**D-2. RFC 8785 JCS(2020) — JSON 정준화** 〔사실〕
- 키 정렬(UTF-16 코드유닛 순)·공백 제거·수 표현 정규화로 바이트 동일 출력을 보장, 해시·서명·비교의 기반. 
- 출처: https://www.rfc-editor.org/info/rfc8785/
- «dddjango 시사점» 레지스트리를 YAML/JSON 자체 형식으로 가면(D1의 B안) 정준화·해시를 JCS류로 자작 구현해야 한다 — 작지만 우리가 소유해야 할 부품이 하나 늘어난다.

**D-3. W3C RDF Dataset Canonicalization(RDFC-1.0) — 2024년 5월 W3C Recommendation** 〔사실〕
- RDF 데이터셋의 정준 직렬화 알고리즘이 2024-05-21 W3C 권고로 확정됐다. 그래프 비교·서명·해시가 목적이며 TypeScript/Rust/Ruby 등 다수 구현이 적합성 리포트에 등재. 단, RDF 그래프 정준화는 그래프 동형(graph isomorphism) 문제 난이도라 입력에 따라 계산 시간이 폭증할 수 있음이 명시돼 있다(blank node가 원인; 실무 규모에선 대부분 문제없음 — 이 마지막 절은 추론).
- 출처: https://www.w3.org/news/2024/rdf-dataset-canonicalization-is-a-w3c-recommendation/ , https://www.w3.org/TR/2024/PR-rdf-canon-20240326/
- «dddjango 시사점» D1에서 RDF/Turtle(A안)을 채택하면 뼈대(레지스트리)의 등가성·해시·diff가 2024년 확정 표준과 기성 구현으로 즉시 해결된다 — 단 이는 뼈대에만 해당하고, 산문 미러 등가성과는 무관하다.

**D-4. gofumpt의 포매팅 패키지 vendoring — 정규화 동작을 버전에 고정하는 기법** 〔사실〕
- gofumpt는 Go 표준 포매팅 패키지의 사본을 vendoring해 "Go 버전이 바뀌어도 같은 gofumpt 버전은 항상 같은 출력"을 보장한다 — 정규화기(포매터)의 동작 표류를 의존성 고정으로 차단한 사례.
- 출처: https://github.com/mvdan/gofumpt/blob/36b4fbb15b1a2e154e137d1005b25deccc02d488/CHANGELOG.md (v0.5.0 항목)
- «dddjango 시사점» 미러 lint의 정규화 규칙(개명 사전·치환 표·제외 절 목록)은 lint 코드와 같은 저장소에서 같이 버전되고, 규칙 변경은 코드 리뷰를 타야 한다.

### 축 E — LLM 기반 의미 등가성 판정 (2025–2026)

**E-1. IDRAAK(arXiv 2608.08801, 2026-08) — 요구사항 문서의 semantic drift 탐지** 〔사실〕
- 다국어 기술 요구사항에서 수치·단위·극성·양식·조건·시간·임계값·개체·관계·예외·생략·추가·용어·범위·참조의 **15개 드리프트 범주**를 정의하고, 요구사항을 언어 독립 구조 성분(SRR)으로 분해해 비교한다. 흥미로운 결과: 8개 전문 에이전트 파이프라인보다 **few-shot 예제 6개를 넣은 단일 LLM 호출이 우수**(MCC=0.888, F1=0.983) — "에이전트 복잡성 증가가 개선을 보장하지 않는다".
- 출처: https://arxiv.org/html/2608.08801 (2026)
- «dddjango 시사점» 규범 문장 쌍의 의미 대조를 LLM으로 한다면 15개 범주 같은 **드리프트 유형 체계 + 구조 분해 후 비교 + 단순한 단일 호출**이 현재 검증된 형태다.

**E-2. LLM 판정의 위치: 게이트가 아닌 triage 보조** 〔사실 + 추론〕
- ConsistencyChecker(arXiv 2506.12376, 2025)류의 LLM 등가성 평가 연구가 활발하나, 기존 방법이 다단 변환에서 의미 드리프트를 놓친다는 보고가 병존한다. Kubernetes 2026 사례(B-4)도 AI를 요약 보조에 한정했다.
- 추론: LLM 판정은 비결정적이라 CI 게이트(머지 차단)의 단독 근거로 삼으면 재현 불가 실패가 생긴다. 결정적 정규화 잔차가 게이트, LLM은 잔차의 의미 해설·우선순위 매김.
- 출처: https://arxiv.org/pdf/2506.12376 (2025), https://www.kubernetes.dev/blog/2026/06/26/human-centered-automation-kubernetes-localization-ai-era/ (2026)
- «dddjango 시사점» 소유자 1인 체제에서 리뷰어 주의력이 최희소 자원 — "자동화는 리뷰어 주의력을 보호해야지 소모시키면 안 된다"는 원칙이 그대로 적용된다.

---

## 2. 반례·주의

1. **정규화 규칙 자체의 표류는 실재하며, 두 겹으로 온다.** (a) 규칙 개정으로 과거 판정과 비호환(mdbook 0.1→0.2 실증, B-3), (b) 정준화 표준 자체의 버전 분열(C14N 1.0/1.1/Exclusive/2.0, D-1). 검증된 대응: 규칙의 버전 관리 + 1회성 마이그레이션 도구 + 정규화기 동작 고정(D-4). 〔사실〕
2. **잔차 0 ≠ 의미 등가.** 정규화-비교는 "정규화가 지운 차이는 비의미적"이라는 가정 위의 구조 등가 판정이다. 특히 "전용 절 제외" 같은 제외 규칙은 커질수록 검사를 스스로 무력화한다(제외된 영역 안의 규범 충돌은 영원히 안 보임). 제외 목록 자체를 별도 자산으로 심의·상한 관리해야 한다. 〔추론 — C14N도 "일부 예외 제외" 단서를 단다는 점에서 방증〕
3. **역방향 함정: 잔차 ≠ 충돌.** P0의 잔차 3쌍이 모두 규범 충돌이라는 보장도 없다 — oasdiff처럼 잔차를 파괴적/비파괴적으로 분류하는 두 번째 층이 없으면 잔차 리포트가 늑대소년이 된다. 〔추론〕
4. **구조적 diff 도구는 의미 판정기가 아니다.** difftastic 스스로 구조 상이=상이로 처리하는 한계를 문서화한다(C-1). 〔사실〕
5. **단위 쌍(ID) 없는 등가성 검사는 선례가 없다.** gettext·Crowdin·Kubernetes triage 전부 "문장/메시지/파일 단위의 대응 관계"가 먼저 있고 그 위에서 stale을 판정한다. 자유 산문 두 벌을 통짜로 놓고 의미 등가성을 기계 보증하는 검증된 시스템은 이번 조사에서 발견하지 못했다(LLM 연구는 있으나 결정성이 없음). 〔사실(부재의 확인) + 추론〕
6. **조건부 단일 소스의 비용.** 태그 산재·전처리기의 구조 무인식(A-2, A-3)·차이가 전면적일 때의 전환 비용. 19쌍 전부를 일괄 단일 소스화하는 빅뱅은 위험하다. 〔추론〕

---

## 3. dddjango 시사점 정리

1. **이 문제는 번역 동기화 문제와 동형이다.** claude판=원문, codex판=번역으로 보면 gettext 모델이 그대로 맞는다. 그리고 그 모델의 전제는 **규칙 단위 ID(=msgid)**다. R4의 결론이 R1(규칙 단위 ID 부여)을 선행 조건으로 강제한다: ID 없이는 어떤 검증된 동기화 기법도 착지할 곳이 없다.
2. **2단 전략이 선례와 일치한다.** (과도기) 손으로 쓴 두 판을 유지하되, 레지스트리의 쌍둥이 필드에 「대응 절 ID + 정규화-본문 해시」를 기록하고, claude판 갱신 시 codex판을 자동 fuzzy(stale) 판정 — 사람이 확인 후 해제. (수렴기) 정규화 잔차 0이 안정적으로 유지되는 쌍부터 단일 정본 + 조건부 렌더링(DITA식 platform 속성)으로 전환해 검사 자체를 소멸시킨다. P0 실측상 4/7쌍이 즉시 수렴기 후보.
3. **정규화 파이프라인은 3층으로.** ①기성 정준화(Pandoc AST 또는 그에 준하는 마크다운 파서)로 표기 잡음 제거 → ②자작 규칙(개명 사전·치환 표·전용 절 제외)은 lint 코드와 함께 버전 관리 + 골든 쌍 회귀 테스트 + 규칙 개정 시 마이그레이션 절차(mdbook-i18n-normalize 패턴) → ③잔차를 oasdiff처럼 「규범 충돌/표현 차이」로 분류해 등급 리포트(Kubernetes 2026의 Strong/Moderate/No signal 패턴).
4. **게이트는 결정적으로, LLM은 보조로.** CI 차단 근거는 정규화 잔차·해시 불일치 같은 결정적 신호만. LLM은 잔차의 의미 해설과 우선순위 매김(15개 드리프트 범주 같은 유형 체계 + few-shot 단일 호출)에 한정 — 소유자 1인의 리뷰 주의력 보호가 설계 목표.
5. **stale 판정 시 안전 기본값은 정본 폴백.** mdbook-gettext처럼, codex판 절이 fuzzy면 낡은 codex 절 배포 대신 claude 정본 절을 그대로 내보내는 옵션을 검토할 가치가 있다(규범 문서에서 "낡은 규범"은 "미번역"보다 해롭다).
6. **D1 연계.** RDF/Turtle 채택 시 뼈대(레지스트리)의 정준화·해시·비교는 RDFC-1.0(2024 W3C 권고)과 기성 구현으로 공짜로 얻는다. YAML 자체 형식이면 JCS류 정준화를 자작해야 한다. 단 어느 쪽이든 **산문 미러의 등가성은 형식 선택과 무관하게 위 1~5의 파이프라인 문제**로 남는다 — D1 결정이 R4를 대신 풀어주지 않는다.

---

## 인용 출처 목록

1. https://docs.oasis-open.org/dita/dita/v1.3/os/part1-base/archSpec/base/condproc.html — OASIS DITA 1.3, 조건부 처리
2. https://docs.asciidoctor.org/asciidoc/latest/directives/conditionals/ — Asciidoctor 조건부 지시자
3. https://paligo.net/blog/content-reuse/what-is-single-source-of-truth-ssot/ — 단일 소싱 실무(보조)
4. https://www.gnu.org/software/gettext/manual/html_node/Fuzzy-Entries.html — GNU gettext fuzzy
5. https://www.gnu.org/software/gettext/manual/html_node/msgmerge-Invocation.html — msgmerge
6. https://github.com/google/mdbook-i18n-helpers/blob/main/i18n-helpers/USAGE.md — mdbook i18n 워크플로·normalize
7. https://github.com/google/mdbook-i18n-helpers — 저장소
8. https://github.com/kubernetes/website/blob/main/content/en/docs/contribute/localization.md — K8s 로컬라이제이션 가이드·스크립트
9. https://www.kubernetes.dev/blog/2026/06/26/human-centered-automation-kubernetes-localization-ai-era/ — K8s 결정적 triage(2026)
10. https://docusaurus.io/docs/i18n/crowdin — Docusaurus×Crowdin
11. https://www.sphinx-doc.org/en/master/usage/advanced/intl.html — Sphinx i18n
12. https://difftastic.wilfred.me.uk/ 및 https://difftastic.wilfred.me.uk/tree_diffing.html — difftastic·트리 diff 한계
13. https://github.com/afnanenayet/diffsitter — diffsitter
14. https://arxiv.org/pdf/2403.05939 — AST diff 정확도 벤치마크(2024)
15. https://github.com/oasdiff/oasdiff 및 https://github.com/oasdiff/oasdiff/blob/main/docs/ALLOF.md — oasdiff·allOf 정규화
16. https://pandoc.org/using-the-pandoc-api.html — Pandoc AST
17. https://www.w3.org/TR/xml-exc-c14n/ — Exclusive XML C14N
18. https://en.wikipedia.org/wiki/Canonical_XML — C14N 개요·버전(보조)
19. https://www.xml.com/pub/a/ws/2002/09/18/c14n.html — C14N 해설(보조)
20. https://www.rfc-editor.org/info/rfc8785/ — RFC 8785 JCS(2020)
21. https://www.w3.org/news/2024/rdf-dataset-canonicalization-is-a-w3c-recommendation/ — RDFC-1.0 권고(2024)
22. https://www.w3.org/TR/2024/PR-rdf-canon-20240326/ — RDFC-1.0 명세
23. https://github.com/mvdan/gofumpt/blob/36b4fbb15b1a2e154e137d1005b25deccc02d488/CHANGELOG.md — gofumpt vendoring
24. https://arxiv.org/html/2608.08801 — IDRAAK(2026)
25. https://arxiv.org/pdf/2506.12376 — ConsistencyChecker(2025)
