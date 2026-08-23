# dddjango 개발 가이드 (메인테이너)

이 저장소에서 플러그인을 **고치고 검증하고 릴리즈하는 방법**을 담는다. 플러그인을 **쓰는** 방법은 [README](../README.md), 파이프라인이 실제로 어떻게 도는지는 [work_flow.html](work_flow.html)을 본다.

온톨로지 도입(릴리즈 2.17.0, 2026-08-23) 이후 규범 문서의 수정 방식이 근본적으로 바뀌었다 — **스킬 md를 직접 고치는 시대는 끝났다**. 이 문서의 핵심은 그 새 방식이다.

---

## 1. 저장소 지도 — 무엇이 정본이고 무엇이 투영물인가

```
ontology/                 ← 규범 «정본» (그래프)
├── rules/*.ttl            30 문서 키 — 참조성 규범 539절·Work 3,400의 단일 출처
├── vocab/djr.ttl          어휘(RDFS) · shapes/  SHACL · wiring/  경로 글롭·alias 대장 등
├── ISSUED                 규범 ID 채번 대장 (append-only)
└── LEDGER.tsv             산문(prose) 절 기준선 원장 (append-only)

dddjango/                 ← Claude Code 설치본 (플러그인)
├── commands/ agents/ skills/   md의 graph-owned 절 = 그래프의 «렌더 투영물»
└── scripts/               결정적 백스톱 27종 + rulepack.json(빌드타임 SPARQL «소성물»)

codex-dddjango/           ← Codex 설치본 미러 (scripts는 byte 동일을 verify가 강제)

dddjango-web/             ← 자매 플러그인 (웹 표현계층 빌더 — /dddjango-web)
                           전 파일 «산문 정본» — 온톨로지 코퍼스 밖. graph-owned 절이 없고
                           md·py를 직접 수정한다. 픽스처는 make verify(verify-web)가 실행.
                           빌드 스펙 정본: workspace/design/2026-08-23-web-presentation-layer-spec.md

codex-dddjango-web/       ← dddjango-web의 Codex 설치본 미러

workspace/                ← 메인테이너 전용 (배포되지 않음)
├── tools/                 검증 도구 사슬 · ontology-authoring.md(저작 규약 정본)
├── design/ plan/ eval/    설계·리뷰·실험 기록 (판정 판례 보존)
└── hooks/                 pre-commit (훅 단일 루트)

docs/                     ← 공식 문서 (이 문서 · master.html — 통합 진입점(좌측 인덱스로 아래 3종 전환)
                           · work_flow.html · ontology-study-map.html
                           · file_tree.html — dddjango 표준 트리 · file_tree_web.html — dddjango-web 표준 트리)
```

세 층의 관계를 항상 기억한다:

| 층 | 실체 | 수정 방법 |
|---|---|---|
| **정본** | `ontology/rules/*.ttl` (Turtle 그래프) | 직접 편집 — 유일하게 손대는 곳 |
| **투영물** | 스킬·에이전트 md의 graph-owned 절 | `ontology_render.py --apply`로 재생성만 |
| **소성물** | `dddjango/scripts/rulepack.json` | `make rulepack`으로 재소성만 |

설치본은 **표준 라이브러리만** 쓴다. rdflib·pySHACL·rdfcanon은 메인테이너 `.venv` 전용이며 플러그인 배포물에 침투하지 않는다(동결 E7).

## 2. 환경 구축 (1회)

```bash
make ontology-env      # python3.14 .venv + rdflib·pySHACL·rdfcanon (버전 고정)
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

어휘(djr) 자체의 개정·블록 경계 규약·IRI 인코딩·롤백 등 깊은 규약은 전부 [`workspace/tools/ontology-authoring.md`](../workspace/tools/ontology-authoring.md)가 정본이다(§2 게이트, §5 채번, §7 어휘 개정, §13 블록 경계, §14 IRI·alias 공간, §17 롤백).

## 4. 검사기(백스톱)·도구 수정

- 검사기 27종은 `dddjango/scripts/check-*.py`가 원본이고 `codex-dddjango/…/scripts/`는 **byte 동일 미러**다 — 한쪽만 고치면 verify-base 마지막 단(`diff -rq`)이 red다. 둘 다 갱신한다.
- 측정 도구 일부는 manifest 봉인 대상이다(`workspace/tools/manifest_seal.py`의 글롭 목록 참조). 봉인 파일을 고치면 봉인 재발행이 필요하다.

## 5. 검증 명령

| 명령 | 언제 |
|---|---|
| `make verify` | **모든 커밋 전 기본** — 온톨로지 단(게이트·SHACL·렌더 동기·구조·질의 골든 12단) + 기존 검증 세트(검사기 매트릭스·미러·봉인 draft 등) |
| `make verify-mutation` | rulepack·selector를 건드린 커밋 |
| `make verify-firing` | 설치본 cache 발화 증명 (개발 중엔 `ALLOW_STALE=1`) |
| `make verify-runready` | 실런(A/B 평가) 진입 직전에만 — verify + 변이 + 발화 + 봉인 엄격 대조 |

## 6. 릴리즈

```bash
make release              # dddjango 릴리즈 — 대화형: current/patch/minor/major 선택
make release-web          # dddjango-web 릴리즈 — 같은 절차, 대상만 다름
make release DRY=1        # 미리보기 (변경 없음) — release-web DRY=1 도 동일
```

플러그인별 타깃이 대상 변수(manifest 2곳·태그 접두사)만 지정하고 공통 절차 `_release`를 부른다. main 브랜치·클린 worktree·origin 동기 상태에서만 진행된다. 두 마켓 manifest에 같은 버전을 기록하고, 커밋 → annotated 태그(`dddjango--vX.Y.Z` · `dddjango-web--vX.Y.Z`) → push → GitHub Release까지 한 번에 간다. 한 저장소에 두 릴리즈 시리즈가 태그 접두사로 나란히 쌓인다. 선택지 `0) current`는 버전 그대로 태그만 발행한다(첫 릴리즈·태그 누락 보완용 — manifest 무변경이면 커밋 없이 현재 HEAD에 태그).

## 7. 더 읽기

- [work_flow.html](work_flow.html) — 파이프라인 실동작·온톨로지 적용 지점·기술 스택 시각 지도 (재생성 스펙: `work_flow.spec.json`)
- [ontology-study-map.html](ontology-study-map.html) — RDF·RDFS·SHACL·SPARQL 등 채택 기술 학습 지도
- [`workspace/tools/ontology-authoring.md`](../workspace/tools/ontology-authoring.md) — 저작 규약 정본 (금지 목록·게이트·채번·롤백)
- `workspace/eval/t3/T3-REPORT.md` — 온톨로지 전량 이관(T3)의 총괄 기록
- `workspace/design/ontology-adoption-map.html` — 도입 여정 조감도
