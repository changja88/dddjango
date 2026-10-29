# dddjango 개발 가이드 (메인테이너)

이 저장소에서 플러그인을 **고치고 검증하고 릴리즈하는 방법**을 담는다. 플러그인을 **쓰는** 방법은 [README](../README.md), 파이프라인이 실제로 어떻게 도는지는 [work_flow.html](work_flow.html)을 본다. 이 저장소에서 일하는 세션이 늘 지킬 규칙은 루트 [`CLAUDE.md`](../CLAUDE.md)에 있다 — 이 문서는 그 규칙을 실제로 수행하는 절차 · 명령 · 까닭이다.

온톨로지 도입(릴리즈 2.17.0, 2026-08-23) 이후 규범 문서의 수정 방식이 근본적으로 바뀌었다 — **스킬 md를 직접 고치는 시대는 끝났다**. 이 문서의 핵심은 그 새 방식이다.

---

## 1. 저장소 지도 — 무엇이 정본이고 무엇이 투영물인가

```
ontology/                 ← 규범 «정본» (그래프)
├── rules/*.ttl            30 문서 키 — 참조성 규범 548절·Work 3,720의 단일 출처
├── vocab/djr.ttl          어휘(RDFS) · shapes/  SHACL · wiring/  경로 글롭·alias 대장 등
├── ISSUED                 규범 ID 채번 대장 (append-only)
└── LEDGER.tsv             산문(prose) 절 기준선 원장 (append-only)

dddjango/                 ← Claude Code 설치본 (플러그인)
├── REQUEST_GUIDE.md       사람용 작업 요청 가이드 정본
├── commands/ agents/ skills/   md의 graph-owned 절 = 그래프의 «렌더 투영물»(입구 commands/refactor.md 는 산문 — 봉인 pipeline 등재)
└── scripts/               결정적 백스톱 27종 + rulepack.json(빌드타임 SPARQL «소성물»)

codex-dddjango/           ← Codex 설치본 미러 (scripts는 byte 동일을 verify가 강제)
└── REQUEST_GUIDE.md       dddjango/REQUEST_GUIDE.md의 byte 동일 미러

dddjango-web/             ← 자매 플러그인 (웹 표현계층 빌더 — /dddjango-web)
                           전 파일 «산문 정본» — 온톨로지 코퍼스 밖. graph-owned 절이 없고
                           md·py를 직접 수정한다. 픽스처는 `make verify-web`으로 직접 돈다
                           (2026-09-16 hyun 지시로 자동 경로에서 분리 — §5).
                           2.0.0(dddart화): Flutter 판 dddart와 같은 절차·구조 — 구현 기술만
                           Django·HTML·HTMX·JS(«dddart 와 다른 점»은 아래 지도 뒤 절).
                           판 기록: workspace/plan/2026-10-06-web-dddart/ — 2.0.0 스펙 mapping.md ·
                           그 뒤 판마다 plan-<판>.md(큰 판은 build-log-<판>.md 도)
├── REQUEST_GUIDE.md           사람용 작업 요청 가이드 정본(2.0.1부터 — 2.1.0에서 빚 정리 · 리팩토링 입구 · 외부 JS 줄을 더함)
├── commands/dddjango-web.md   Coordinator
├── commands/refactor.md       리팩토링 입구 /dddjango-web:refactor <대상 단위> — Coordinator 로 Skill 위임(동작 불변)
├── agents/*-web.md            에이전트 7 — architect · 리뷰어 4(ddd·ui·state·data) · coder · discipline-reviewer
├── skills/*/                  지식 스킬 12 — architecture-ddd·ui·state·data · discipline-cleancode·houserules·test
│                              · implementation-test·python·django·htmx·javascript
├── assets/sdk_boundary.js     외부 JS 경계 검사 보조(공식 SDK 승인 절차)
└── scripts/backstop.py        결정적 백스톱 — 검사 93종(ST·IM·NM·CY·TG·PJ·MD·PU·WV·SH·CS — SH·CS는 빚 스캔 밖 · TG4 브라우저 시험 꼴)
                               · 빚 모드 --debt-scan [--refactor] · --debt-residual · 치환 확인 --subst-check · 시험 범위 --test-scope
                               + refactor_audit.py(리팩토링 모드 판정) · sdk_vendor.py(공식 SDK 등재)
                               + 추출 도구 4(extract_contract·extract_design·extract_dc·fetch_images)
                               · 픽스처 scripts/test/run_fixtures.sh(백스톱 뒤 빚 · 치환 · SDK · 리팩토링 판정 · 추출 도구 픽스처를 이어 부른다)

codex-dddjango-web/       ← dddjango-web의 Codex 설치본 미러
                           지식 스킬 12종은 전부 `dddjango-web-<스킬>` 접두 폴더(dddart·dddjango Codex 판과
                           이름 충돌 회피) · 리팩토링 입구 `skills/dddjango-web-refactor/`($dddjango-web-refactor)
                           · references · scripts · assets는 byte 동일(scripts/test/ 제외 — verify-web이 대조)
                           · 동기 절차: codex-dddjango-web/README.md
└── REQUEST_GUIDE.md       dddjango-web/REQUEST_GUIDE.md의 byte 동일 미러

.claude-plugin/marketplace.json   ← Claude marketplace: dddjango · dddjango-web subdir
.agents/plugins/marketplace.json ← Codex marketplace: ./codex-dddjango · ./codex-dddjango-web subdir

workspace/                ← 메인테이너 전용 (배포되지 않음)
├── tools/                 검증 도구 사슬 · ontology-authoring.md(저작 규약 정본)
├── design/ plan/ eval/    설계·리뷰·실험 기록 (판정 판례 보존) — 파이프라인의 권위 있는 명세는
│                          design/2026-05-26-dddjango-plugin-pipeline-design.md
├── reference/             배포 reference(final.md)의 출처 · P1 메타데이터 소스 미러 — 배포 본문 정본은
│                          dddjango/skills/*/references/final.md 이고 corpus_mirror_sync.py --write 가 이곳과
│                          Codex reference 를 갱신한다
├── scratch/               운영자 임시 · 작업 파일(git 무시 · 사본 · 클론 · 재현 · 재개 기록)
└── hooks/                 pre-commit (훅 단일 루트)

docs/                     ← 공식 문서 (이 문서 · master.html — 통합 진입점(좌측 인덱스로 아래 네 문서 전환)
                           · work_flow.html — dddjango 동작 흐름(재생성 스펙 work_flow.spec.json)
                           · work_flow_web_guide.html — dddjango-web 동작 흐름(work_flow_web.html · 스펙을 싣는다)
                           · file_tree.html — dddjango 표준 트리(생성기 mkrev2.py)
                           · file_tree_web.html — dddjango-web 표준 트리)
```

세 층의 관계를 항상 기억한다:

| 층 | 실체 | 수정 방법 |
|---|---|---|
| **정본** | `ontology/rules/*.ttl` (Turtle 그래프) | 직접 편집 — 유일하게 손대는 곳 |
| **투영물** | 스킬·에이전트 md의 graph-owned 절 | `ontology_render.py --apply`로 재생성만 |
| **소성물** | `dddjango/scripts/rulepack.json` | `make rulepack`으로 재소성만 |

설치본은 **표준 라이브러리만** 쓴다. rdflib·pySHACL·rdfcanon은 메인테이너 `.venv` 전용이며 플러그인 배포물에 침투하지 않는다(동결 E7).

### dddjango-web — dddart 와 다른 점 · 판의 내력

dddjango-web 은 2.0.0 부터 Flutter 판 dddart 와 같은 절차 · 구조(간소화 DDD 4층 + MVVM · G0/G1/G2 · 가정 계약 → tracer → 미니 게이트)에 구현 기술만 Django · HTML · HTMX · JS 로 바꾼 판이다. dddart 와 일부러 다르게 둔 것(지금 기준):

1. **구조 검사를 슬라이스가 끝날 때마다도 돈다**(2.2.0 · `backstop.py --slice-end`) — dddart 는 G2 직전에만.
2. **한 web 앱의 여러 제품**(2.3.0) — 선택형 제품 선언 `web/product_registry.json` 과 제품별 design_system 뿌리 · 문서 셸.
3. **지속 셸의 ‹뒤로›는 지나온 차례**(2.6.0) — 탭마다 따로 쌓지 않는다. 떠난 화면은 보관해 돌아오면 그대로다.
4. **시험 범위**(2.7.0) — coder-web 은 계층 중에는 새로 쓰거나 고친 시험만, 슬라이스 끝에는 러너 `backstop.py --test-scope --since` 가 낸 시험만 돌고, web 시험 전체는 G2 앞 한 번(web 밖 비시험 파일이나 web 전역 진입점을 바꾼 실행만 프로젝트 전체 한 번). 근거 시험은 슬라이스 끝 줄에 더하지 않고 단계 줄마다 따로 돈다(2.8.4).
5. **시험 입장 표**(2.8.0) — 설계자가 명세 `## 시험 입장 표` 에 행마다 판정(`add` · `update` · `reuse` · `reject`)과 걷음 칸을 적고 coder-web 은 `add` · `update` 행대로만 쓴다. render-smoke 필수 산출 없음 · 색 · 여백 · 글꼴은 `G2 화면 확인`. 갈래는 build-state `test_rule`.
6. **실행 끝 커밋은 합치지 않는다**(2.8.3) — core 처럼 실행이 만든 커밋을 그대로 둔다.

판마다 무엇이 바뀌었는지는 `docs/work_flow_web_guide.html` 의 «판마다 바뀐 것» 표(한 줄씩)와 판 기록 `workspace/plan/2026-10-06-web-dddart/plan-<판>.md`(문제 · 결정 · 고침 · 행동 변화 · 한계 · 검토 반영 · 검증)를 본다. 판 내력은 이 문서나 `CLAUDE.md` 에 쌓지 않는다.

### 사람용 작업 요청 가이드의 소유권

위 두 정본(`dddjango/REQUEST_GUIDE.md`·`dddjango-web/REQUEST_GUIDE.md`)은 runtime prompt나 ontology corpus가 아닌 사람용 문서다.
graph-owned marker·`ISSUED`·`LEDGER.tsv`의 대상이 아니며 `corpus_mirror_sync.py`도 갱신하지 않는다.
Claude 정본에 Claude와 Codex 시작 문법을 함께 적고, Codex 사본은 의미 미러가 아닌 byte 동일 미러로 유지한다.
루트 README는 정본 링크와 두 플러그인의 짧은 비교를 소유하고 상세 템플릿은 복제하지 않는다.
dddjango-web은 2.0.0(dddart화)에서 `REQUEST_GUIDE.md`를 뺐고, 2.0.1에서 2.0.0 동작 기준으로 새로 썼다.

편집 순서는 Claude 정본 편집 → Codex 파일에 byte 복사 또는 동일 patch → 아래 대상 비교다(가이드만 바뀌었으면 여기서 끝 · 다른 경로도 바뀌었으면 §5 «검사 고르기» 의 그 줄 검사).

가이드의 꼴은 사용자가 정했다(2026-10-12) — **번호 칸 틀과 실제 예만** 둔다.

- 설명 문단 · 절을 더하지 않는다. 꼭 필요한 것도 한 줄로 제안하고 먼저 묻는다(지운 내용을 되살리는 것은 반드시 묻는다).
- 원본 파일에 바로 고친다(사본을 만들지 않는다 — 커밋 · 배포는 따로).
- 나쁜 예는 실제로 실패한 발주서에서 가져온다(지어내지 않는다).
- 사용자가 가이드를 직접 고치기도 한다 — 쓰기 전에 지금 내용을 읽고, 내가 쓰지 않은 변경은 건드리지 않고 알린다.
- 플러그인 동작을 가이드에 적을 때는 런타임 글(커맨드 · 에이전트 · 스킬)의 해당 줄을 먼저 확인한다.

```bash
cmp -s dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
cmp -s dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
python3 workspace/tools/request_guide_contract.py --self-test
python3 workspace/tools/request_guide_contract.py
python3 workspace/tools/reverse_coverage.py
```

각 가이드는 설치본 안에서 독립적으로 읽을 수 있어야 한다. 네 installed guide source(두 플러그인 × Claude·Codex) 어디에도
상대 목적지처럼 보이는 Markdown inline/image·reference definition·HTML `href`/`src` 구문을 넣지 않는다.
Scheme URI와 `#fragment`만 허용하며 code span·fence·HTML comment·escape·예시도 예외가 아니다.
설치된 플러그인 루트의 사본이 해당 runtime의 권위 있는
가이드임을 상단에 밝힌다. README와 manifest homepage는 발견 경로이며, `main`의 공개 homepage는 최신
온라인 가이드이므로 설치 버전 정본을 대신하지 않는다. 두 플러그인 모두 두 manifest homepage와 Codex
`interface.websiteURL`은 각자 Claude 정본의 공개 URL을, `repository`는 모두 저장소 루트를 가리킨다.
두 marketplace의 정확한 경로는 위 지도와 같고 네 source는 각각의 설치 subdir와 `ref: main`을 유지한다.

## 2. 환경 구축 (1회)

```bash
make ontology-env      # python3.14 .venv + rdflib·pySHACL·rdfcanon (버전 고정)
make probe-env         # python3.14 .venv-probe + pytest·xdist·Django·pytest-django·greenlet (버전 고정 — B0 픽스처 전용)
make ontology-hooks    # core.hooksPath = workspace/hooks (pre-commit 게이트)
```

## 3. 규범 수정 — 표준 루프

md에서 `<!-- graph-owned: … -->` 마커가 붙은 절은 **직접 수정 금지**다. 고치면 pre-commit 훅과 `ontology_render_sync`가 red로 잡는다. 대신:

1. **정본 수정** — `ontology/rules/<doc_key>.ttl`에서 해당 Work의 리터럴을 고친다. 새 절·새 규범이면 `ontology/ISSUED`에 채번을 append한다(절차: authoring §5).
2. **게이트** — 커밋 시 pre-commit이 4단 저작 게이트(파스 → 정본 직렬화 diff=0 → RDFC 해시 → SHACL)를 자동으로 돈다. 수동 실행:
   ```bash
   PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_gate.py
   ```
3. **렌더 재투영** — 투영물을 그래프에서 다시 생성한다:
   ```bash
   PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render.py --apply <doc_key>
   ```
4. **rulepack 재소성** — 그래프가 바뀌었으면 `make rulepack` (팩의 `built_from` 해시가 그래프에 묶여 있어 생략하면 verify red).
5. **검증** — `make verify`.

**산문(NAR) 절**은 md가 여전히 정본이다 — md를 직접 고치되, `ontology/LEDGER.tsv`에 재기준선 행(같은 doc_key·section_key, 새 SHA-256, 사유)을 append한다. 훅이 해시 불일치를 알려 주므로 잊어도 커밋 단계에서 잡힌다.

### 개정 체크리스트 — 빠뜨리면 verify 가 단계마다 다른 red 를 낸다

1. **편집** — rdflib 구조 편집 뒤 `ontology_canon.canon_turtle(g, load_prefix_registry(), allow_lists=False)` 로 재직렬화한다(먼저 현행 ttl 왕복이 byte 동일인지 확인 · `PYTHONPATH=workspace/tools .venv/bin/python`). 리비전 = 새 Expression `<djr#R-NNNN@YYYY-MM-DD>`(`prov:specializationOf` · `prov:wasRevisionOf` 이전 · `djr:revision` n+1 · `djr:revisionKind` redefinition|clarification|amendment) + Norm 의 currentExpression · prefLabel 교체. 신설 = Norm + Expression(revision 1) + `ontology/ISSUED` append + Block statesNorm + wiring enforcedBy/delegatedTo(소유자 없는 Norm 은 구조 검사 red). 같은 판 안의 문장 맞춤은 새 Expression 없이 그 판 Expression 글을 고친다.
2. `ontology_gate.py` green → `ontology_render.py --apply <doc_key>`(바뀐 문서마다).
3. **LEDGER 재기준선** — 재투영된 graph 절마다 `sha256(strip_marker(span))` 행을 덧붙인다(`ontology_render_sync.strip_marker` · `ontology_census.parse_sections` · 사유 `rebaseline:<날짜> <사유>` · migrated 칸은 그 절 최근 행 값을 잇는다).
4. **계수표** `workspace/eval/fixtures/ontology_gate/target-counts.json`(NormShape/WorkShape = ISSUED 수 · ExpressionShape += 신설 + 리비전 수 · 새 Work 면 계층 계수도 +1) · **q4 골든** `query_golden_check.py --emit` · `make rulepack`(소성물은 함께 커밋).
5. **final.md 소스 미러** — `corpus_mirror_sync` 는 LEDGER 기준선 해시로 소스 절을 찾는다. graph 절을 개정했으면 `workspace/reference/<skill>/reference/final.md` 의 옛 절을 새 절로 손으로 바꾼 뒤 `--write` → `--check`.
6. **Codex 의미 미러** — 스킬 `SKILL.md` · 조정자 · 에이전트(Codex 에서는 `codex-dddjango/skills/dddjango-<역할>/SKILL.md`)를 같은 뜻으로 손으로 고친다. `corpus_mirror_sync` 는 final.md 만 보므로 이 어긋남은 어떤 검사도 잡지 못한다. Codex 파일의 스킬 참조 이름은 접두(`dddjango-<스킬>`)가 붙어 바꿀 글자가 배포본과 다를 수 있다.
7. **검사기 규칙 번호를 새로 내면** — 트리 개정 명세(`workspace/design/2026-08-08-tree-revision-spec.md`) 행 · 집계표 · 규칙 소유 지도(`workspace/plan/2026-08-11-rule-owner-map.md`) 행 · 귀속 매핑표 행(`spec_lint.py` 가 잡는다).
8. **검사기를 고치면** — Codex byte 미러 → 골든 · EXPECTED 갱신(`findings_count_matrix` · `checker_baseline_matrix` · `checker_cross_matrix --emit-expected` · `construct_drift_report --emit-expected` · `gen_pregate_symbol_kinds`) → 봉인(§4 · §6) → `make verify`. 구현을 맡기면 이 목록을 지시문에 그대로 넣는다.

어휘(djr) 자체의 개정·블록 경계 규약·IRI 인코딩·롤백 등 깊은 규약은 전부 [`workspace/tools/ontology-authoring.md`](../workspace/tools/ontology-authoring.md)가 정본이다(§2 게이트, §5 채번, §7 어휘 개정, §13 블록 경계, §14 IRI·alias 공간, §17 롤백).

## 4. 검사기(백스톱)·도구 수정

- 검사기 27종은 `dddjango/scripts/check-*.py`가 원본이고 `codex-dddjango/…/scripts/`는 **byte 동일 미러**다 — 한쪽만 고치면 verify-base 마지막 단(`diff -rq`)이 red다. 둘 다 갱신한다.
- `workspace/tools/request_guide_contract.py`는 가이드 존재·byte 미러·marketplace name/path/ref와 subdir 내용·manifest homepage/repository·Codex websiteURL/defaultPrompt·설치본 권위 문구를 검사한다. 링크 검사는 canonical source surface의 drift backstop이다. 가이드 계약(README token·guide 존재·byte 미러·권위 문구·homepage/websiteURL=가이드 URL)은 `GUIDE_PLUGINS`(dddjango·dddjango-web — web은 2.0.1부터)에, marketplace·manifest name/repository·Codex defaultPrompt(각 prompt가 플러그인 이름을 부른다) 계약은 `PLUGINS`(dddjango·dddjango-web) 모두에 건다. 가이드가 없는 플러그인이 생기면 그 homepage·websiteURL은 저장소 루트여야 한다. README의 `## 작업 요청 가이드`부터 다음 `## ` heading 직전과 전체 README source에 `[dddjango 작업 요청 가이드](dddjango/REQUEST_GUIDE.md)`와 `[dddjango-web 작업 요청 가이드](dddjango-web/REQUEST_GUIDE.md)`가 각각 정확히 한 번 있어야 한다(README의 다른 절에서는 가이드를 링크 없이 글로만 부른다). 두 guide에는 위 상대 목적지 구문 금지 규칙을 적용한다. CommonMark 문맥이나 실제 rendered/clickable 동작·렌더러 등가성은 판정하지 않으며 README의 코드·주석 안 token도 센다. `--self-test`는 실제 두 heading 구조의 tempfile 정상 fixture와 독립 변이의 `validate` 결과를 literal 기대값으로 검사한다. 계약을 바꾸면 해당 검출력 fixture도 함께 유지한다. 표준 라이브러리만 쓰고 네트워크나 공개 URL 생존성은 검사하지 않는다. `verify-base-core`는 dddjango pair 비교 → self-test → 실제 계약을 실행한다(dddjango-web pair의 byte 미러는 실제 계약이 대조한다).
- `workspace/tools/reverse_coverage.py`의 닫힌 분류표는 dddjango 루트 `REQUEST_GUIDE.md`를 사람용 사용자 가이드로 명시한다. 새 설치 파일의 존재 근거를 유지하되 이 가이드에 런타임 규칙 소유권을 부여하지 않는다.
- 측정 도구 일부는 manifest 봉인 대상이다(`workspace/tools/manifest_seal.py`의 글롭 목록 참조). 봉인 파일을 고치면 봉인 재발행이 필요하다.
- **봉인은 두 번 한다** — ① 커밋 직전 `manifest_seal.py --write` 뒤 검사 ② 그 커밋(배포면 배포 커밋) 뒤 `--write` 를 다시 해 `sealed_commit` 을 고정하는 chore 커밋(§6 · §7.4). ①만 하면 strict `--check` · `verify-runready` 가, ②만 하면 «봉인 후 변경» 이 붉다(`make verify` 의 `--draft` 대조는 ① 뒤면 통과해 놓치기 쉽다).
- **봉인은 커밋 직전 마지막 단계다** — `make verify` 가 RED 여서 봉인 대상(측정 도구·byte 골든 EXPECTED·매트릭스)을 다시 고쳤으면 `manifest_seal.py --write` 를 다시 발행하고 `make verify` 를 처음부터 다시 돈다. 커밋 메시지·기록의 verify 수치는 **마지막 실행 로그**(evidence 경로 병기)의 것만 적는다 — 중간 실행의 green 을 옮겨 적지 않는다(2026-09-04 `d701df8` «verify 6/6» 거짓 표기 · 정정 `cad221b`).

## 5. 검증 명령

| 명령 | 언제 |
|---|---|
| `make verify` | core 플러그인 · 그래프 · 도구 · 픽스처 · Makefile 을 바꾼 커밋(아래 «검사 고르기») — 온톨로지 단(게이트·SHACL·렌더 동기·구조·질의 골든 12단) + 기존 검증 세트(검사기 매트릭스·미러·봉인 draft 등) + B0 픽스처 단(`verify-base-probe` — pytest 탐침·지원 확인·증거 실행을 장난감 저장소에서 실제 pytest 로 · `.venv-probe` 없으면 RED → `make probe-env`) |
| `make verify-mutation` | rulepack·selector를 건드린 커밋 |
| `make verify-firing` | 설치본 cache 발화 증명 (개발 중엔 `ALLOW_STALE=1`) |
| `make verify-runready` | 실런(A/B 평가) 진입 직전에만 — verify + 변이 + 발화 + 봉인 엄격 대조 |
| `make verify-web` | dddjango-web 픽스처(백스톱·빚·치환·SDK·리팩토링 판정·추출 도구)·refactor_audit self-test·상시 답 블록 core 대조·리팩토링 입구 표지 대조·Codex 미러 대조(scripts·assets·지식 스킬 12 references) — **수동 전용**(2026-09-16 `VERIFY_TARGETS`에서 제외) |

### 검사 고르기 — 바뀐 경로로 정한다(2026-10-29)

`make verify` 는 16~25분, `make verify-web` 은 1시간 가까이 걸린다. 바뀐 경로(`git diff --name-only <기준>` — 커밋 전이면 작업 트리 · staged)를 아래 표에 대 보고 걸리는 줄의 검사를 모두 **한 번** 돈다. 문서 · 기록만이면 커밋 전에, 플러그인을 바꾼 커밋은 **커밋한 뒤 push 전에** 돈다(옛 판 대조가 `HEAD` 에 묶인 시험처럼 커밋 뒤에야 드러나는 결함을 잡는다 — 커밋 전에 따로 한 번 더 돌지 않고, 붉으면 고침 커밋을 더해 다시 돈다). **표에 없는 경로가 하나라도 있거나 애매하면 `make verify` 전체**를 돈다.

| 바뀐 경로 | 검사 | 시간 |
|---|---|---|
| `CLAUDE.md` · `docs/` 의 md · html(아래 둘 빼고) · `workspace/plan/` · `workspace/design/` · `workspace/scratch/` | `PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --check --draft` | 몇 초 |
| `docs/file_tree.html` · `docs/mkrev2.py` | 위 + `workspace/tools/tree_mirror_check.py` · `workspace/tools/spec_lint.py` | 1분 안 |
| `README.md` · `*/REQUEST_GUIDE.md`(플러그인 폴더 안에 있어도 이 줄 — 런타임이 읽지 않는 사람용 문서) | 위 + §1 «사람용 작업 요청 가이드» 의 대상 명령(cmp · `request_guide_contract.py` · `reverse_coverage.py`) | 1분 안 |
| `dddjango-web/` · `codex-dddjango-web/` 의 md 만 | `make verify-web` 레시피의 `run_fixtures.sh` 뒤 줄들(self-test · 표지 · 문단 대조 · 미러 대조 — 따로 떼어 돈다 · 별도 타깃은 아직 없다) | 1분쯤 |
| `dddjango-web/scripts/` · `assets/`(+ Codex 짝) | `make verify-web` 전체 | 약 1시간 |
| `dddjango/` · `codex-dddjango/` · `ontology/` · `workspace/tools/` · `workspace/eval/` · `workspace/hooks/` · `Makefile` | `make verify` 전체(rulepack · selector 면 + `make verify-mutation`) | 16~25분 |

`make release` · `make release-web` 안의 core `make verify` 는 배포 관문이라 그대로 돌고(`verify-web` 은 돌지 않는다), 배포 뒤 봉인 chore 는 봉인 파일만 바꾸므로 봉인 대조(`--check --draft`)로 확인한다 — 배포 사본에서 전체 검사를 한 번 더 돌지 않는다.

Finder 가 만든 `.DS_Store` 가 플러그인 폴더 · `ontology/` 에 생기면 `verify-base-core`(설치본 파일 설명 — «미설명: `.DS_Store`») · 봉인 대조가 붉다. 지우고 다시 돈다(git 은 무시하지만 두 검사는 디스크를 본다). 병렬 일꾼 둘이 `make verify` 를 동시에 돌리면 임시 파일 경합으로 한 칸 흔들릴 수 있다 — 그 칸만 단독으로 다시 돌려 가른다.


## 6. 릴리즈

```bash
make release              # dddjango 릴리즈 — 대화형: current/patch/minor/major 선택
make release-web          # dddjango-web 릴리즈 — 같은 절차, 대상만 다름
make release DRY=1        # 미리보기 (변경 없음) — release-web DRY=1 도 동일
```

플러그인별 타깃이 대상 변수(manifest 2곳·태그 접두사)만 지정하고 공통 절차 `_release`를 부른다. main 브랜치·클린 worktree·origin 동기 상태에서만 진행된다. 두 마켓 manifest에 같은 버전을 기록하고, 커밋 → annotated 태그(`dddjango--vX.Y.Z` · `dddjango-web--vX.Y.Z`) → push → GitHub Release까지 한 번에 간다. 한 저장소에 두 릴리즈 시리즈가 태그 접두사로 나란히 쌓인다. 선택지 `0) current`는 버전 그대로 태그만 발행한다(첫 릴리즈·태그 누락 보완용 — manifest 무변경이면 커밋 없이 현재 HEAD에 태그).

`make release-web`도 `make release`처럼 대상 변수만 정하고 `_release`로 간다 — `_release` 는 core `make verify` 를 돌고 `verify-web` 은 돌지 않는다. 2026-09-16 hyun 지시로 `verify-web`을 `VERIFY_TARGETS`에서 뺐다(막아 세운 결함 0 · 실제 결함은 전부 A8 실사용이 잡았다). 같은 배치에서 **실패한 브라우저 관찰 서브시스템(1.1.13~1.1.19)을 전량 철거**했다 — `verify-web-browser`(K3)·`observe_interactions`·`evidence_debt`·`refreeze.py`·`ledger.py`와 그 계약·hook을 지우고 검사기를 v1.1.12 정적 형태로 되돌렸다(정본: workspace/design/2026-09-16-web-strip-observation-subsystem.md). 웹 쪽 검증이 필요하면 `make verify-web`을 직접 돈다. **release-web 에서 사라진 보증은 Codex byte 미러 대조다** — `codex-dddjango-web/`가 어긋나도 릴리즈가 막지 않으므로, 검사기나 references를 고치면 미러를 손으로 맞춘다(해소 명령은 `codex-dddjango-web/README.md` «동기 절차» · `make verify-web`이 `diff -rq`로 잡는다).

2.0.0(dddart화)은 1.x의 시안 기계 검사 전부(렌더 숫자 대조·모션·포커스 링·토큰 처분·정체 감사 등)·정확값 토큰 규칙·시각 연결표·`REQUEST_GUIDE.md`·빚 정리·리팩토링 입구·외부 JS 승인 절차를 뺐다(스펙: `workspace/plan/2026-10-06-web-dddart/mapping.md`). 가이드는 2.0.1에서 2.0.0 동작 기준으로 새로 썼다(API 위치 세 꼴 — `http(s)://` 주소·로컬 파일 경로·이 프로젝트 안 path — 와 함께). 2.1.0에서 빚 정리·리팩토링 입구(대상 단위 = BC · root · common · design_system · static 칸 · 옛 배치 최상위 폴더 등)·외부 JS 승인 절차를 새 구조에 맞춰 다시 넣었다(스펙: `workspace/plan/2026-10-06-web-dddart/plan-2.1.0.md`). 시안 기계 검사·정확값 토큰은 되살리지 않는다. 2.2.0에서 구조 검사(백스톱)를 슬라이스가 끝날 때마다도 돌게 했다(`backstop.py --slice-end` — dddart는 G2 직전 한 번 · 스펙: `workspace/plan/2026-10-06-web-dddart/plan-2.2.0.md`). web `refactor_audit.py`의 «상시 답 인식 블록»은 core `dddjango/scripts/refactor_audit.py`와 byte 동일해야 한다 — `make verify-web`이 대조한다(core 블록을 바꾸면 표지 주석째 web·Codex 에 복사).

**릴리즈 창**(core): 배포 전에 타깃 저장소들의 진행 레인(G0 승인 뒤 G2 승인 전)을 센다. 배포를 미루거나 시점을 묻지 않고(2026-10-11 사용자 결정 — 그 전에는 레인 착륙까지 보류했다), 배포 보고에 «pre-gate 재예보 필요» 와 그 레인을 적는다. 특히 `dddjango/scripts/` 가 바뀐 릴리즈는 pre-gate 실행 트리 digest 를 바꾸므로, 진행 중 레인의 마지막 예보가 `--check-report` 에서 «툴체인 stale»이 되어 재예보를 요구한다 — Phase 1 레인은 싼 재실행으로 끝나지만 G1~G2 레인은 Phase 2 재발화가 든다(2026-09-27).

**문서 현행화**: 사용자에게 보이는 동작이 바뀐 판은 릴리즈 전에 `README.md` 와 `docs/master.html` 이 싣는 네 문서(work_flow.html · work_flow_web_guide.html(work_flow_web.html 포함) · file_tree.html · file_tree_web.html)를 그 판 기준으로 고치고, master.html 아래쪽 «기준 판» 줄도 함께 올린다. web 판은 work_flow_web_guide.html 의 «판마다 바뀐 것» 표에 한 줄을 더한다(§1 dddjango-web). docs/ 에는 master.html 이 싣는 문서와 그 원본(스펙 · 생성기), 이 개발 문서만 둔다(사용자 로컬 파일 빼고). **요청 가이드**(`dddjango/REQUEST_GUIDE.md` · `dddjango-web/REQUEST_GUIDE.md`)는 판마다 확인한다 — 사용자가 요청에 쓰는 칸 · 좋은 예 · 나쁜 예 · 플러그인이 스스로 하거나 묻는 일이 바뀌었으면 §1 «사람용 작업 요청 가이드» 규칙대로 고치고(Codex 짝은 byte 복사), 아니면 «바뀔 것 없음» 을 배포 보고에 적는다.

봉인 ②(§4 «봉인은 두 번»): 판 올림은 마켓 매니페스트(봉인 대상)를 바꾸므로 배포 커밋 **뒤에** 별도 chore 커밋으로 재발행한다 — 변경 · 배포 커밋 안에 든 봉인(①)만으로는 `sealed_commit`이 그 커밋 이전을 가리켜 strict `--check`가 RED가 된다(`make verify`의 `--draft` 대조는 통과하므로 놓치기 쉽다).


## 7. 작업 진행 관례 — 개발 · 현장 보고 수리

이 저장소에서 일하는 세션(운영자)이 플러그인을 고치는 순서와 꼴이다. 지킬 규칙은 [`CLAUDE.md`](../CLAUDE.md) §3 에 있고, 여기는 그 규칙을 실제로 하는 법 · 예다. 사람은 넷이다 — **사용자**(방향 · 규칙 목적의 결정) · **운영자**(조사 · 설계 · 구현 지시 · 검증 · 배포) · **서브에이전트**(검토 · 구현 · Claude) · **발주자**(대상 프로젝트의 세션 — 현장 보고를 장부에 적는다).

### 7.1 하는 법 · 예

- **작업 자리** — 일마다 `workspace/scratch/<일 이름>/` 을 만들어 사본 · 클론 · 재현 · 검토 산출 · 재개 기록을 모은다. 대상 저장소 사본처럼 큰 것은 일이 끝나면 지우고 크기를 보고한다. 옛 지침 사본을 남길 때는 `.txt` 로 바꾼다. 새 도구가 `workspace/` 를 훑는다면 `scratch/` 를 뺀다.
- **재현 표** — 결함마다 한 줄: `재현됨/안 됨 · 생기는 조건 · 생기면 무슨 일 · 누가 찾았나(검토 · 구현 담당 · 실레인) · 운영자가 직접 본 정도`. 재현은 장난감 저장소나 사본에서 작은 스크립트로(지우는 명령 없이). 실레인에서 본 것이 아니면 «실제 작업에서 본 것은 아님» 이라고 적는다.
- **«플러그인이 막는다» 는 보고** — 수리 설계 전에 ① 막힌 요구의 출처(사용자 원문 / 발주자 도출 / 플러그인 규정) ② 기존 규칙 · 호스트 선례로 그 요구를 규칙 안에서 채우는 길부터 본다. 그 길이 있으면 수리가 아니라 그 답을 보고한다.
- **묻는 꼴** — 첫 줄 «정할 것 N개(어느 플러그인에 몇 개)», 그다음 결정 하나만: 배경 한 줄 → 실제로 있었던 일(수치 · 작은 실례) → 선택지와 비용 차이 → 추천과 까닭. 코드 규칙 결정은 번호 붙인 문제 상황과, 현장 코드를 줄인 조각(어느 줄이 어느 규칙에 걸리는지 주석)으로 보인다. 사용자에게 익숙한 기준(예: 일반 앱 동작)이 있으면 그것을 실례로 먼저 댄다.
- **사용자 할 일 꼴** — 보고 끝에 따로: «지금 할 일»(보통 하나 · 정확한 명령이나 답할 글자) → «다음 차례» → «나중». 이미 끝난 것은 확인해(예: 설치본 판 번호) 목록에서 뺀다.
- **시각** — 쓰기 직전에 `date` 를 잰다. 사용자 메시지 시각은 «앞 date 뒤 · 뒤 date 앞» 경계 꼴로 적고, 분을 모르면 시각을 빼고 «앞 행 뒤» 처럼 순서로 적는다.
- **개선 효과 재기** — 같은 작은 일감을 옛 판 · 새 판으로 끝까지 돌려 레인 시간 · 결과를 비교한다. 멈출 기준(몇 번 실패면 접음 · 효과 몇 % 미만이면 접음)은 시작할 때 정한다. 조각 실험을 합산한 전망은 추정이라 결정 근거로 쓰지 않는다. 자원 개선은 사본에서 «시간 같거나 줄어듦» 을 먼저 잰다(예: 시험 일꾼 수만 줄이는 방법은 느려지므로 고르지 않는다).

### 7.2 개발 — 새 기능 · 규칙 변경

1. **조사** — 문제 · 자료(필요하면 문헌 · 선례) · 대상 코드 지도. 대상 저장소는 읽기만 하고, 사본은 `workspace/scratch/` 에 만든다.
2. **방향 결정** — 규칙 목적에 닿는 선택만 사용자에게 묻는다.
3. **설계** — 문제 · 결정 · 규칙 문장 · 검사기 동작 · 한계.
4. **설계 독립 검토** — 적대 · 과적합 · 다른 코퍼스와의 모순 · 런타임 실현성 관점을 한 바퀴에 함께 본다. 지적은 재현해 처분하고(받음/받지 않음과 까닭), 고친 뒤에는 차단 · 중요 지적이 닫혔는지만 좁게 다시 본다(전체 재검토를 다시 하지 않는다 · 좁은 확인이 셋째에도 차단을 못 닫으면 멈추고 사용자에게 묻는다).
5. **계획** — 단위 · 맡은 파일 · 확인 명령 · 행동 시험 · 멈출 기준. 큰 판은 계획도 독립 검토를 받는다.
6. **구현** — 정본(그래프 §3 또는 산문 md) · 렌더 · 미러 · 픽스처. 구현을 맡기면 7.5 지시문을 쓴다.
7. **행동 시험** — 장난감 저장소나 현장 사본에서 옛 판과 새 판을 나란히 돌린다(옛 판은 배포 커밋 SHA 로 고정 — `HEAD` 금지).
8. **구현 독립 검토** → 지적 재현 → 고침.
9. **검사** — §5 «검사 고르기» 대로. 봉인 대상을 바꿨으면 §4 «봉인은 두 번».
10. **문서 · 요청 가이드 확인**(§6 «문서 현행화») → **커밋 · 배포**(7.4) → **보고**(7.6).

### 7.3 현장 보고 수리

**장부** — `workspace/eval/field-report-4/` 의 현장 보고 장부에 발주자가 항목을 덧붙인다(`F4-<번호>` · 등록 시각 · 본 것 · 바라는 결과 · 처분). 번호는 다시 쓰지 않는다. 운영자는 처분 줄만 덧붙인다 — `처분 갱신(<시각> · 운영자): 수리됨 = <플러그인> <판>(<배포 시각> · 태그) — <무엇을 고쳤나>`. 장부의 로컬 변경은 커밋하지 않는다.

1. **읽기** — 장부 항목과 레인 기록(읽기만). 읽은 때의 마지막 F4 번호 · 마지막 «덧붙임» 시각을 적어 둔다.
2. **재현 · 뿌리** — 배포판(마지막 배포 태그 — scratch 에 클론해 태그로 체크아웃하거나 `git show <태그>:<경로>`)으로 작게 재현하고 원인을 확정한다: 어느 규칙 · 도구의 어느 줄 · 같은 꼴의 다른 자리 · 자매 플러그인 · 영향 받는 실행.
3. **방향** — 고침이 규칙 목적에 닿으면 재현 표와 함께 사용자에게 묻고, 아니면 진행한다. 레인 쪽 사정(요구 출처 · 기존 규칙으로 풀림)이면 수리가 아니라 그 답을 보고한다(7.1).
4. **고침 설계 · 검토** — 큰 수리는 7.2 의 3~5 단계. 작은 수리(글 몇 줄 · 검사기 10줄 급)는 설계 검토를 따로 두지 않고 7 의 독립 검토 한 번에 과적합 · 모순 관점을 넣는다.
5. **구현 + 되돌아옴 막기** — 고침과 함께 다시 들지 않게 하는 장치를 둔다(검사기 픽스처 · verify 계약 줄 — «걷은 말 없음» · Claude · Codex 문단 대조).
6. **행동 시험** — 옛 판은 결함을 재현하고 새 판은 해소하는 것을 같은 장난감에서 보인다.
7. **독립 검토** → 지적 재현 → 모두 처분.
8. **판 기록** — `plan-<판>.md`(문제 · 고침 · 행동 변화 · 행동 시험 · 한계 · 검토 반영 · 검증 · web 은 `workspace/plan/2026-10-06-web-dddart/` · core 는 `workspace/plan/<날짜>-<일 이름>/`). 계획을 확정할 때 장부를 다시 읽어 1 에서 적은 번호 · 시각 뒤에 새 항목이 붙었는지 본다 — 새 항목은 이번 판에 넣거나 계획 · 노트에 «다음 판» 으로 이름을 적는다. 긴 구간이면 진행 기록을 고칠 때마다 장부의 바뀐 시각도 본다.
9. **검사**(§5) → **문서 · 요청 가이드 확인**(§6) → **배포 직전 장부 다시 읽기**(8 과 같은 방법).
10. **배포**(7.4) → 장부에 처분 줄 → **보고**(7.6).

### 7.4 커밋 · 배포

- **커밋** — 경로를 하나씩 `git add` 한다. 메시지 첫 줄은 `fix(web): … — F4-<번호> (<판> 후보)` · `feat: …` 꼴, 본문은 고친 것 · 검사 · 검토. 공개 글에 쓰지 않는 것은 `CLAUDE.md` §3 «공개 저장소» 목록 하나만 따른다.
- **배포 절차**:
  1. 플러그인을 바꾼 커밋을 만든 뒤 push 전에 §5 «검사 고르기» 표의 검사를 돈다(web scripts · assets 면 `make verify-web` 전체 · web md 만이면 그 표의 줄들). 녹색이면 main 을 push 한다 — 배포에 딸린 push 라 묻지 않는다.
  2. push 한 main 을 `workspace/scratch/release-<판>/CL` 로 새로 클론하고 `.venv` · `.venv-probe` 를 원본으로 링크한 뒤 두 이름을 `.git/info/exclude` 에 적는다(안 적으면 «worktree dirty» 로 멈춘다).
  3. `make release` / `make release-web` — 안에서 core `make verify` 를 돈다.
  4. `gh release edit <태그> --notes-file <노트>` — 노트는 «바뀐 것 · 도는 실행에 미치는 것 · 받아들인 한계», 파일은 `workspace/scratch/release-<판>/` 에 둔다.
  5. 원본에서 `git pull --ff-only` → `PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --write` → 바뀌면 `chore: manifest 봉인 재발행 — <플러그인> <판> 매니페스트(판 올림) 뒤 정렬` 커밋 · push → `--check --draft` 로 확인(§4 «봉인은 두 번»). 클론 `CL` 은 보고 뒤 지운다(7.1 «작업 자리»).
- **릴리즈 창**(core) — 진행 레인은 배포 보고에 «pre-gate 재예보 필요» 와 그 레인을 적는다(§6).

### 7.5 서브에이전트 지시문

검토 · 구현을 맡길 때 지시문에 늘 적는 것:

- 작업 폴더 `workspace/scratch/<일 이름>/` · `/tmp` 금지. 병렬 일꾼은 맡은 파일이 겹치지 않게 나누고, 커밋 메시지 · 임시 파일도 자기 폴더에만.
- 맡은 파일과 맡지 않은 파일 목록. 지시문에 «이 폴더 아래 아무것도 만들지 말라» 와 «답은 이 폴더의 파일에» 를 함께 쓸 때는 «답 파일 하나만 예외» 로 적는다. «문서만 고침» 일이면 실행 0 을 적는다.
- 임시 사본에 플러그인 폴더를 심볼릭 링크로 걸지 않는다(픽스처의 변이 시험이 원본을 덮어쓴다). 고치기 전 붉음은 사본 밖에 잠깐 복사해 잰다. 받은 뒤 운영자는 시작 시각 뒤 바뀐 파일 목록을 예상 목록과 대조한다.
- 옛 판 대조는 배포 커밋 SHA 상수로(`HEAD` 금지). 구현 검토 질문에 «커밋 뒤에도 같은 결과인가» 를 넣는다.
- 검사기를 고치는 일이면 §3 체크리스트 8 을 그대로 넣는다.
- 대상 저장소는 읽기만 — 그 폴더에서 `cd` · `git -C` · 명령 금지, 절대 경로로만 읽는다. env 파일 · 비밀 키 · 도구 설정 파일 · 대화 기록 폴더는 열지 않는다.
- Codex 는 미러 글만 — Codex 로 띄우는 시험은 하지 않는다. 사용자가 청한 분석 더블 체크로 Codex 를 띄우면 그 지시문에 읽기만 · env 열지 않음 · `/tmp` 금지를 직접 적는다(Codex 는 이 저장소의 `CLAUDE.md` 를 읽지 않는다).
- **프로세스 신호** — 신호(KILL · TERM · STOP)는 그 일꾼이 직접 띄우고 pid · 시작 시각을 기록한 프로세스에만 보낸다. 새 판정 방식은 먼저 신호 없는 탐침으로 «띄우지 않은 프로세스에서 판정 0» 을 확인한 뒤에만 신호 단계로 간다. 신호 고리에는 대상 수 상한과 앞뒤 `ps` 를 둔다. 사용자 앱 본체가 사라지면 멈추고, 앱 확장 · 도우미 · 시스템 · 다른 세션 프로세스가 사라진 것은 우리 신호가 0 이면 기록만 하고 계속한다.
- **브라우저 · 페이지 조작 실험** — 바깥 앱을 여는 열기(LaunchServices)를 막은 울타리 안에서만 하고, `mailto:` · `tel:` · 앱 링크는 누르지 않는다.
- **셸 스크립트** — 빈 변수를 거부한다(`set -u` · `"${S:?}"`). `cd` 대신 절대 경로를 쓰고 홈 전체를 훑지 않는다.
- 끝 보고: 고친 파일과 `git diff --stat` · 돌린 명령과 결과 · 붉음 → 녹색을 본 것 · 지시와 다르게 한 것과 까닭 · 남은 걱정.
- 검토자에게는 운영자의 결론이 아니라 코드 · 사실 · 재현 자리를 준다. 받은 보고는 diff 와 재현으로 다시 확인한다.
- 세션이 끝나면 배경 일꾼도 멈추고 끝 알림이 오지 않는다 — 오래 걸리는 일꾼은 답 파일 · 산출물이 생기는지 보는 감시를 함께 건다. 재개 뒤 «didn't finish before the previous session ended» 알림이 오면 그 일꾼에게 처음부터 다시 시킨다.

### 7.6 기록 · 보고

- 판 기록(설계 · 계획 · 검토 · `plan-<판>.md`)은 저장소에 커밋한다. 운영자의 재개 기록 · 진행 메모는 `workspace/scratch/`(커밋 안 함). 사건(배포 · 결정 · 단계 끝)마다 진행표 둘(`workspace/plan/2026-09-26-refactor-path-repair/progress.md` · `workspace/design/ontology-adoption-map.html` — 사용자 로컬 파일)을 갱신한다.
- **배포 보고 꼴**: 판 · 담긴 수리(장부 번호) · 검토 · 검사 결과(마지막 실행 수치) · 받아들인 한계 · 레인 영향(core 는 «pre-gate 재예보 필요» 레인 · web 은 도는 레인이 언제부터 새 판을 따르나) · 요청 가이드(«고침» 또는 «바뀔 것 없음») · 사용자 할 일(설치본 갱신 `/plugin marketplace update changja88-dddjango` → `/reload-plugins`).

## 8. 더 읽기

- [master.html](master.html) — 아래 네 문서를 한 화면에서 고르는 통합 진입점
- [work_flow.html](work_flow.html) — dddjango 파이프라인 실동작·온톨로지 적용 지점·기술 스택 시각 지도 (재생성 스펙: `work_flow.spec.json`)
- [work_flow_web_guide.html](work_flow_web_guide.html) — dddjango-web 동작 흐름 (지도 `work_flow_web.html` · 스펙 `work_flow_web.spec.json`)
- [`workspace/tools/ontology-authoring.md`](../workspace/tools/ontology-authoring.md) — 저작 규약 정본 (금지 목록·게이트·채번·롤백)
- `workspace/eval/t3/T3-REPORT.md` — 온톨로지 전량 이관(T3)의 총괄 기록
- `workspace/design/ontology-adoption-map.html` — 도입 여정 조감도
