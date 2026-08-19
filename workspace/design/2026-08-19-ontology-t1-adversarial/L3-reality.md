# L3 — 실물 정합(Repo Reality) 적대 리뷰: T1 세부 실행 계획

> 대상: `workspace/design/2026-08-19-ontology-t1-plan.md` (v1 초안)
> 렌즈: 계획의 전제(§1 실물 좌표)와 공정(§2)이 저장소 실물과 맞는가 — 전 항목 실물 직접 열람, 추정 0건. 게이트 동작 2건은 스크래치 트리 실험으로 실증.
> 작성: 2026-08-19 · 읽기 전용(이 파일만 생성)

## 0. 방법 — 확인한 실물 목록

| 부류 | 실물 |
|---|---|
| 계획·정본 | t1-plan 전문 · 블루프린트 v3.2(`2026-08-18-ontology-blueprint-v3.md` — E1~E8·§3·§8·§9·개정 1) · v2(`-blueprint-v2.md` §2·§4·§5·헤딩 전수) · t0-plan(A4·완료 기준) |
| P0 센서스 | `2026-08-18-ontology-p0-census.md` 전문 + `-p0-census/` E01·E06·E07(전문/절 표), A3(표류·개명 매핑) |
| 코퍼스 원본 | ninja `references/final.md`(헤딩 전수·§6.2 L501~826 문면), tdd final.md(헤딩 전수), architecture-ddd final.md(헤딩 전수·§3.2 L539~637), claude/codex `implementation-django/SKILL.md`, `dddjango/commands/dddjango.md` L11, `codex-dddjango/skills/dddjango/SKILL.md` |
| 30문서 계수 재현 | 스킬 11쌍+command+agents 7 경로를 직접 열거해 wc — **30문서 17,398행 정확 일치** |
| T0 산출물 | `ontology/`(ISSUED·prefixes·vocab/djr.ttl·shapes/djr-shapes.ttl 전문·golden 20벌) · `workspace/tools/ontology_gate.py` 전문 · `ontology_shacl_full.py` · `ontology_hierarchy_check.py` · `ontology-authoring.md` §5 · `workspace/eval/fixtures/ontology_gate/`(cases/·target-counts.json) · `workspace/hooks/pre-commit` · Makefile(verify-ontology·verify-base·release) |
| 미러 도구 | `corpus_mirror_sync.py`(docstring·스코프) · `corpus_lint.py`(collect_docs·검사 ①) |
| 기타 | `workspace/plan/2026-08-11-rule-owner-map.md` · git log(커밋 `91fae74` = HEAD 실재) |
| 실험 | 스크래치 트리(`scratchpad/gate-x`)에 vocab·shapes 복사 후 ontology_gate `--root` 실행 2건 — 교차 rules 파일 restates·wiring AliasEntry→rules Work |

## 1. 지적 요약

| # | 심각도 | 제목 |
|---|---|---|
| L3-1 | **blocker** | 게이트 ④(=pre-commit 훅)가 교차 파일 참조를 위양성 red — T1-2 재진술 규약·alias 귀속 검수와 정면 충돌(실험 실증 2건) |
| L3-2 | major | «606 재현 = 추출기 자기 검증»은 성립하지 않는다 — P0 절 분할은 문서마다 다른 편집 규약이고 기계 대조 가능한 절 키 형식이 없다 |
| L3-3 | major | wiring 저작의 조인 키 부재 — rule-owner-map # 공간과 파일럿 규범은 접점이 없고, NormShape는 전 규범에 배선을 강제하는데 비커버 규범의 기본값이 미정 |
| L3-4 | major | T0가 T1로 명시 이월한 의무 2건이 계획에 없다 — ISSUED↔rules 정합 검사기 · target-counts.json 기대표 갱신(파일럿 첫 커밋에서 verify [4] 기계적 red) |
| L3-5 | minor | ISSUED 채번 시작값 미정의(빈 대장 + «마지막 번호+1») · «최초 등재 문서 경로» 필드 값 모호 |
| L3-6 | minor | «v2 §85» 인용 오류 — v2에 §85는 없다(§0~§10). 층①·잔차 등급 정본은 v2 §5 |
| L3-7 | minor | «소스 미러 소비자 2종» 부정확 — corpus_lint는 workspace/reference/의 소비자가 아니다 |
| L3-8 | minor | 미러 스코프 처분 «도구 개작 최소» 과소평가 — corpus_mirror_sync 본문 대조는 절 개념 없는 전신 byte-exact |
| L3-9 | minor | 표류 ① 처분 문면 «fat-model 규범 제거»는 부정확 — 정합 목표는 claude판 조건화 문장으로의 교체 |
| L3-10 | minor | «검사기 3종이 문면상 배선 실재»는 과대 표현 — §6.2 문면의 실물은 역할명 2종+marker 2종, 스크립트명 0회 |
| L3-11 | minor | 30문서 목록의 단일 정본 파일 부재 — 도출은 가능(실측 재현 일치)하나 센서스 도구의 입력 확정 방식 미정 |
| L3-12 | minor | 공유 개체(Checker 27종·Agent) 선언 파일의 배치 규약 부재 — wiring «문서 키» 단위 구조와 안 맞는다 |

심각도별: blocker 1 · major 3 · minor 8. §1 실물 좌표 표의 나머지 전 행은 재검증 통과(§3 말미 «검증 통과 목록»).

## 2. 상세

### L3-1 (blocker) 게이트 ④의 파일 단위 병합이 T1 공정의 필수 구조를 기계적으로 차단한다

- **실물**: `workspace/tools/ontology_gate.py:92-103` — ④ SHACL의 데이터 그래프 = **대상 파일 + vocab/ + wiring/** 병합. `rules/`는 어떤 경우에도 병합되지 않는다(전량 병합은 verify [3] `ontology_shacl_full.py:35`의 몫 — 그 docstring 자신이 «rules/ 파일 사이의 교차 참조가 있는 T1 이후에 파일 단위 게이트가 못 보는 것» 이라고 자인한다, `:3-4`).
- **충돌하는 셰이프**: `ontology/shapes/djr-shapes.ttl:57-60` `BlockShape-restates sh:class djr:Block` · `:12-17` `AliasEntryShape-aliasFor sh:class djr:Work`. sh:class는 대상 노드의 rdf:type이 **데이터 그래프 안에** 있어야 통과한다.
- **실험 실증** (스크래치 트리, `ontology_gate.py --root`):
  1. `rules/doc-a.ttl`의 블록이 `rules/doc-b.ttl`의 블록을 `djr:restates` → **RED** `Value does not have class djr:Block`.
  2. `wiring/alias.ttl`의 AliasEntry가 `rules/doc-c.ttl`의 Work를 `djr:aliasFor` → **RED** `Value does not have class djr:Work`.
- **계획과의 충돌**: T1-2 ②(계획 L40) 재진술 처리는 «SKILL 요약 블록 → `djr:restates` → 본문 정본 블록»을 규약으로 강제하고, SKILL.md와 final.md는 30문서 체계에서 **별개 문서** = 별개 `rules/<문서 키>.ttl`(계획 L47)이다. 게이트 2 검수 항목 #10(계획 L98)은 «재진술 병합·alias 귀속»을 T1 완료 기준으로 못박았다. 즉 공정이 만들라는 구조를 공정 단계 ⑤(4단 게이트)가 red로 되돌린다. `workspace/hooks/pre-commit:19`가 같은 게이트를 커밋 훅으로 돌리므로 **정당한 파일럿 저작 커밋 자체가 차단**된다.
- **T0가 이를 못 본 이유**: 골든 20벌은 전부 단일 파일 안에서 참조가 닫혀 있고(`golden/alias-valid.ttl`은 Work 선언을 같은 파일에 동봉), hierarchy_check는 전량 병합으로 돌기 때문.
- **처분 요구**: T1-2에 게이트 ④ 병합 규칙의 처분(예: rules/ 전량을 병합 대상에 추가, 또는 교차 참조 sh:class를 verify [3] 전용 셰이프로 분리, 또는 스킬 단위 1파일 규약으로 «문서 키» 재정의)을 **명시 결정**으로 넣어야 한다. 현행 문면(계획 L24 «이관 공정의 기계 기반(재작업 없음)»)은 실물과 다르다.

### L3-2 (major) 센서스 자기 검증 «606 재현»은 기본값이 실패다

- 계획 T1-1(L30): 헤딩 파싱 → «P0 절 수와 대조(606 재현 = 추출기 자기 검증)».
- **P0 절 분할은 기계 규칙이 아니라 담당자별 편집 규약이다** (실측):
  - E01(`E01-architecture-ddd.md`): final.md 45절로 계수. 실물 헤딩(펜스 인지)은 h2 10+h3 41+h4 4=55. 45가 되려면 ①h4 4개를 부모에 접고 ②«출처 종합»(h2)의 h3 자식 3개를 접고 ③내용 있는 h2만 «§N 서두» 절로 세우고(§1·§4·§5는 세우고 §2·§3·§6은 안 세움) ④SKILL frontmatter를 무헤딩 절로 추가 — 4중 편집 규칙이 필요하다.
  - E07: ninja final.md 24절 vs 실물 헤딩 31(비목차) — 목차·컨테이너 h2를 서두에 병합(«서두(제목·위임 안내·목차, L1–29)»).
  - E06: tdd final.md 59절 vs «h3 51+자식 없는 h2 6+서문 1=58» — 단순 규칙으로 1 어긋난다.
- **절 키 형식이 대조 불가**: E01~E10의 절 키는 «§3.2 엔티티», «[SKILL.md] frontmatter(description)», «서두(제목·위임 안내·목차, L1–29)» 같은 산문 라벨이다. 기계 추출 키와 1:1 조인할 정형 키가 어디에도 없다.
- **파서 함정 실증**: 순진한 `^#` 파싱은 코드 펜스 안 파이썬 주석에 오염된다 — ddd final.md에서 `# ` 행 46개가 h1로 잡힌다(실제 제목 1개). 계획 L30은 펜스 처리 요건조차 언급하지 않는다.
- 계획 §6(L112)이 «불일치 시 원인 규명 후 진행»을 두긴 했으나, 그 문면은 불일치를 예외로 상정한다 — 실물상 불일치가 **정상 상태**이므로 «자기 검증» 신호는 상시 소음이다. 처분: 606과의 대조는 «문서별 접기 규약 명문화 + 잔차 설명 표» 방식으로 재정의하거나, 게이트 1 검토 자료에 P0 대비 절 분할 차이 표를 필수 동봉해야 한다.
- (참고 — 통과분: E01~E10 절·문장 합계는 P0 §1 표와 완전 정합함을 재가산으로 확인. 606=49+115+37+103+74+63+28+39+40+58, 3,217도 일치.)

### L3-3 (major) T1-2 ③ «wiring 저작(rule-owner-map 참조)»은 그대로는 실행 불가

- **rule-owner-map의 키 공간**: `workspace/plan/2026-08-11-rule-owner-map.md`의 행 키는 무접두 `#N`(discipline-houserules/tree-revision-spec 공간, 538규칙)이고, 값 소유 정본은 houserules final.md라고 스스로 명시한다.
- **파일럿 규범엔 그 번호가 없다**: ninja final.md §6.2(L501~826) 문면에 `#N` 인용 **0건**(grep 실측). ddd §3.2가 인용하는 #486~#492 등은 houserules 규칙에 대한 **크로스 참조**이지 §3.2 자기 규범의 번호가 아니다. 따라서 map의 행과 파일럿 규범 문장을 잇는 조인 키가 존재하지 않는다.
- **실제 저작 근거의 실물**: ① §6.2 문면의 역할명 지목(«schema checker»·«controller/OpenAPI checker»·«owning controller checker», final.md L518~531)+marker 2종 ② 검사기 docstring의 § 인용 — 단 `check-openapi-error-declaration.py:3260`은 **§2.2**를 인용하고 3종 중 §6.2를 직접 인용하는 docstring은 확인되지 않았다 ③ E07의 «커버» LLM 판정 ④ `dddjango/commands/dddjango.md` registry 절의 검사기→#N 대응. 즉 enforcedBy 저작은 이 4원을 종합하는 **판단 작업**인데, 계획은 «rule-owner-map 참조» 한 구로 기계 참조처럼 서술한다.
- **비커버 규범의 강제 배선**: `djr-shapes.ttl:119-120` NormShape = (HasChecker ∨ HasDelegate) ∧ (유형 5종 중 1) — vocab에서 유형 5종 전부 `rdfs:subClassOf djr:Norm`(`djr.ttl:28~57`)이므로 **유형이 붙은 모든 파일럿 Work는 enforcedBy 또는 delegatedTo가 필수**다. ninja §6.2의 85문장 대부분은 검사기 3종에 안 걸린다 — 위임 대상 기본값(어느 Agent인가)을 계획이 정하지 않으면 SHACL red 또는 임의 저작이 된다. «비커버는 소유 규약대로»(L39)의 «소유 규약»이 무엇의 어느 절인지 특정돼 있지 않다.

### L3-4 (major) T0의 명시 이월 의무 2건이 계획에서 증발했다

- **ISSUED↔rules 정합 검사기**: `workspace/tools/ontology-authoring.md:42` — «ISSUED↔rules/ 정합 검사(v2 registry_lint 동형)는 채번이 시작되는 T1 산출물». t0-plan L61도 «**T1 산출물로 명시 이월**». T1 계획 전문에 이 검사기가 없다(grep 0건). 파일럿 ~100 Work 채번이 «최초 실사용»(L39)인데 대장-실물 정합은 무검사로 남는다.
- **target-counts.json 갱신 절차**: `ontology_hierarchy_check.py:7-9` — «T0 시점 rules/가 비어 있어 … **계수 기대표 실가동은 T1부터**», 기대표는 `workspace/eval/fixtures/ontology_gate/target-counts.json`(현행 BlockShape 4·SectionShape 4·WorkShape 9 등 — 골든 계수). 파일럿 이관 커밋마다 계수가 바뀌므로 **첫 커밋에서 verify [4]가 기계적으로 red**다. 갱신을 공정 절차서(⑤와 커밋 사이)에 넣지 않으면 배치마다 임기응변이 된다. 계획에 «target-counts/계수 회귀/기대표» 언급 0건(grep 실측).

### L3-5 (minor) ISSUED 첫 사용의 미결 2건

- `ontology/ISSUED`는 **0바이트**(등재 0건·헤더 없음). authoring §5(L41-42)의 절차는 «다음 번호 = 대장 마지막 번호+1»뿐 — 빈 대장에서 시작값이 미정의다. E6 «v2 DJR 번호 계승»(블루프린트 L40)의 계승 실체도 0건이다(v2는 미실행 설계 — v2 §3의 `DJR-0417`은 예시 표기). R-0001 시작이면 그렇게 명문화해야 «~100 Work» 채번이 결정적이다.
- 행 형식 TAB 3필드 자체는 T0 정본(authoring §5·t0-plan A4)과 정합 ✓. 단 3번째 필드 «최초 등재 문서 경로»가 **소스 md 경로냐 `rules/<문서 키>.ttl` 경로냐** 를 어느 문서도 확정하지 않았다(«행 append → 같은 커밋에서 rules/에 Work 노드 등장» 문면은 후자를 시사하나 단정 불가). 100행을 쓰기 전에 확정할 것.

### L3-6 (minor) «v2 §85»는 없는 앵커다

- 계획 L22: «정규화 층①(… — v2 §85)». v2 블루프린트의 절은 §0~§10이 전부다(헤딩 전수 확인). 층① 정의와 잔차 등급 값 공간은 **v2 §5 «쌍둥이 미러»**(파일 행 85~86)에 있다 — 행 번호가 절 번호로 둔갑했다. 내용 실재는 확인 ✓(등급 4값+N∖L 정의 문면 그대로). 온톨로지 프로젝트가 앵커 정밀성을 명분으로 삼는 만큼 자기 문서의 죽은 앵커는 교정할 것.

### L3-7 (minor) corpus_lint는 workspace/reference/의 «소비자»가 아니다

- 계획 L21: 소비자 = `corpus_lint.py`·`corpus_mirror_sync.py`. 실물: corpus_mirror_sync만 workspace/reference/를 입력으로 읽는다(불변식1 소스, docstring L8-13). corpus_lint의 대상은 **claude판 배포 코퍼스만**(`collect_docs`, L59-64 — codex판 미포함)이고, workspace/reference/와의 관계는 검사 ①이 배포 문서 안의 `workspace/…` 경로를 «죽은 경로»로 적발하는 것뿐이다. T1-4 스코프 처분 설계 시 두 도구의 처분 내용이 달라야 한다(전자는 절 스코프 제외, 후자는 사실상 무관).

### L3-8 (minor) «스코프 제외 마커/화이트리스트 방식(도구 개작 최소)»는 과소평가

- `corpus_mirror_sync.py`의 불변식1 대조는 «첫 비-P1 `## ` 헤딩 ~ EOF **byte-exact**»(docstring L11-13) — **절 개념이 없다**. 파일럿(ninja final.md·ddd final.md)의 일부 절만 그래프 소유로 바뀌면: 절 단위 제외는 본문 절단 파서 신설 = 실질 개작이고, 파일 단위 화이트리스트는 같은 파일의 **산문 소유 절 보호를 상실**해 동결 문면(«해당 절 스코프 제외» — 블루프린트 §9 처분표)과 어긋난다. 어느 쪽이든 T1-4의 작업량·방식을 지금 문면보다 구체화해야 «동일 커밋» 규율을 지킬 수 있다.

### L3-9 (minor) 표류 ① 처분 문면의 부정확

- claude판 `dddjango/skills/implementation-django/SKILL.md:22`는 fat model을 **폐기한 게 아니라 조건화**했다(«평면 Django 맥락은 fat model(§4.1), dddjango 표준 4계층은 domain_layer 애그리거트 소유»). L40에는 «모델 설계 (fat model·상속…)» 라우팅 행도 잔존한다. codex판 `:21`의 무조건 문장을 «제거»(계획 L66)하면 codex판만 fat-model 언급이 사라져 **새 표류**가 된다 — 처분은 claude판 문장으로의 **교체**로 적어야 한다. (표류 ② «#A~#B»는 실물 재확인 ✓ — 규약 문장은 `dddjango/commands/dddjango.md:11`에만 있고 codex Coordinator에 부재, codex 본문 `#N~#N` 범위 표기 9회 실측. 부수 효과도 무해 확인 ✓ — 두 파일 다 corpus_mirror_sync 스코프 밖(plugin-native), release byte-diff는 `dddjango/scripts↔codex …/scripts` 한정(Makefile L53), corpus_lint는 claude판만 대상.)

### L3-10 (minor) «검사기 3종이 문면상 배선 실재»의 과대 표현 (D7 전제 연동)

- §6.2 문면(L501~826)에 실재하는 것: 역할명 «schema checker»·«controller/OpenAPI checker»·«owning controller checker» + marker 2종. `check-` 스크립트명 등장 **0회**(grep 실측 — E07 특이 발견 2도 동일 진술: «스크립트 파일명은 문서에 한 번도 등장하지 않고»). 3종 파일명 특정(error-centralization·api-error-controller-contract·openapi-error-declaration)은 E07의 **추론 대응**이다. 3종 스크립트의 실재는 확인 ✓. D7의 파일럿 선정 논거 자체는 유지되나, SPARQL 왕복 ①(규칙→담당 검사기)이 «실물로 성립»하려면 역할명→파일명 매핑을 wiring 저작에서 누가 어떤 근거로 확정하는지(L3-3) 먼저 풀려야 한다. 나머지 D7 전제는 통과: 85문장·31%·소단락 10여 개·marker 2종(E07 L50·L73-74), tdd §5.5 57문장·검사기 연결 0(E06 — «E8 실측» 인용도 블루프린트 E8 문면에 «tdd 스킬 완전 공백» 실재로 유효), ddd §3.2에 판정·불변식 3단락 실재(final.md L94~98 — 단 헤딩명은 «엔티티 (Entity)»). D6 전제 통과: §3 트리에 비-Turtle ISSUED 선례 실재. D8 전제 통과: E01~E10 문서군 분담 실재.

### L3-11 (minor) 30문서 목록의 단일 정본 부재

- P0 §0(L9)은 구성 산식(«스킬 11쌍 + commands/dddjango.md + agents 7종 = 30문서»)만 주고, 명시적 경로 목록 파일은 없다. E01~E10 각각의 «파일별 요약» 표를 합치면 도출 가능하고, 본 리뷰가 그 목록으로 재계산해 **30문서 17,398행 정확 일치**를 확인했다 — 목록 자체는 건전하다. 다만 `ontology_census.py`가 목록을 하드코딩할지 E-파일에서 파싱할지 미정이며, 어느 쪽이든 «분모의 정본»이 도구 안 상수가 되는 것은 게이트 1(분모 동결)의 대상물로 명시해 두는 게 안전하다.

### L3-12 (minor) 공유 개체 선언 파일의 배치 규약 부재

- NormShape·ViolationShape가 요구하는 `djr:Checker`·`djr:Agent` **개체**(27종+에이전트들)는 vocab에 없다(vocab은 클래스·kind/owner 개체만). 계획의 wiring 배치는 `wiring/<문서 키>.ttl`(L47)인데 검사기 개체는 문서 횡단 공유물이다 — 공유 선언 파일(예: `wiring/checkers.ttl`) 규약이 없으면 문서별 중복 선언이나 누락 red가 된다(게이트 ④는 wiring 전량을 병합하므로 공유 파일이면 문제없음 — 규약 한 줄이면 풀린다).

## 3. 검증 통과 목록 (§1 실물 좌표 — 재검증 green)

- 30문서 17,398행 ✓(직접 재계산 일치) · 606절·3,217문장 ✓(E01~E10 재가산 일치) · §앵커 91% ✓(551/606)
- ninja §6.2 85문장·문서 최대 절 31%·소단락 10여 개·marker ID 2종 ✓ / tdd §5.5 57문장·7값 열거·백스톱 공백 ✓ / architecture-ddd SKILL 4절 18문장 + final 45절 237문장 ✓
- 표류 2건 문면 ✓(codex SKILL L21 fat-model 무조건 문장 잔존 · codex Coordinator 규약 문장 부재+범위 표기 9회 사용) · 판별 불가 1건 T4 이월 ✓(블루프린트 T4 진입 조건 문면 실재)
- T0 스택 ✓: 커밋 `91fae74` 실재(HEAD) · verify-ontology 6단(Makefile L21-37) · 골든 20벌 · kind 5종·owner 2종 개체 · meta 2층(meta-house.ttl) · fixture 레인 `ontology_gate/cases/` · pre-commit 훅 · `make verify` 편입과 롤백 한 줄 주석(Makefile L17-18)
- v2 이월 자산 문면 실재 ✓(층① 정준화·잔차 등급 4값·N∖L — v2 §5 L85-86, 절 키 규약 — v2 §4.2·E6) · codex 개명 매핑 A3 실재 ✓
- 게이트 2 항목 표(L87-98)는 블루프린트 §8 T1 완료 기준 전 항목을 포함 ✓(+계획 추가 2건 라벨 구분 적정) · T1의 wiring 저작이 §9 «wiring 정본화는 T2 A/B 뒤» 순서와 충돌하지 않음도 확인 ✓(정본화=배선 대조 축 재지정이지 저작 금지가 아님)
- verify [3](shacl_full)은 vocab+rules+wiring 전량 병합이라 교차 참조를 본다 ✓ — L3-1은 게이트 ④·훅 층의 문제로 한정됨

## 4. Overall — 자기 기각 검토 포함

**판정: 계획 기각 아님 — 조건부 진행.** §1 실물 좌표는 12행 중 좌표 자체가 틀린 행이 없고(표현 정밀도 지적 3건: L3-6·7·10), 계획의 뼈대(P0 인벤토리 재분류·파일럿 D7·게이트 2개·리스크 절)는 실물과 잘 맞물려 있다. 그러나 **공정이 첫 커밋·첫 검수에서 실물에 부딪히는 지점 4곳**(L3-1~4)은 T1-3 착수 전에 계획 문면으로 처분돼야 한다. 특히 L3-1은 «T0 스택 재작업 없음»(L24) 전제를 실험으로 반증한 것이므로, T1-2에 게이트 병합 규칙 처분 결정을 추가하지 않으면 공정 절차서 ⑤가 자기모순이다.

자기 기각 시도: ① L3-1이 blocker 과잉인가 — 파일럿 범위(D7: final.md 절만)에서는 restates가 안 나올 수 있다. 그러나 게이트 2 #10이 «재진술 병합·alias 귀속»을 완료 기준으로 요구하고, alias 귀속은 wiring↔rules 교차 참조를 즉시 만든다(실험 2). 완료 기준과 기계 게이트가 충돌하는 결함은 blocker가 맞다. 다만 수리 폭은 작다(병합 규칙 한 줄 또는 배치 규약) — «계획 전면 재작성»이 아니라 «T1-2에 결정 1건 추가»로 해소 가능하다. ② L3-2가 major 과잉인가 — 계획 §6에 불일치 대응 문면이 이미 있으니 minor라는 반론이 가능하다. 그러나 게이트 1(센서스 **동결**)의 검토 자료 신뢰성이 이 자기 검증에 걸려 있고, 실측상 «재현 성공»이 아니라 «전 문서 재현 실패+수동 대사»가 기본 경로다 — 동결 게이트의 재료 산출 방식이 바뀌는 문제이므로 major를 유지한다. ③ 본 리뷰의 한계 — 규범 문장 «개수»(85·57·237 등)는 LLM 계수라 독립 재계수하지 않았고 P0 문서 간 정합성만 확인했다. E02~E05·E08~E10 상세 파일은 합계 정합 확인에 그쳤다. 게이트 실험은 최소 트리플 구성이라 실제 파일럿 규모의 다른 셰이프 상호작용(예: closed BlockShape와 렌더용 추가 프로퍼티 수요)은 미탐색이다.
