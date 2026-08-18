# A3 — 쌍둥이(claude/codex 양판) 표류 실측

P0 센서스 구조 실사 · 2026-08-18 · 실측 도구: `python3 corpus_mirror_sync.py --check`, `diff -q`, `wc -l`, 정규화 잔차 diff(개명·플랫폼 표기 치환 후 unified diff)

## 0. 요약

- 미러 도구가 지키는 영역(final.md 11쌍)은 **11/11 in-sync (exit 0)**, 스크립트 33쌍도 **전부 byte-identical**.
- 그러나 「의미 미러」로 선언된 19개 문서쌍(SKILL.md 11 + agents 7 + command 1)은 **어떤 도구도 쌍둥이 등가성을 검사하지 않으며**, 그 안에서 **내용 표류 2건 실증 + 경계 사례 1건**을 발견했다.
- 핵심 표류: codex판 `implementation-django/SKILL.md`가 **폐기된 「무조건 fat model」 규범**을 그대로 싣고 있다(claude판은 「4계층은 domain_layer 애그리거트 소유」로 갱신됨) — 규범 충돌.

## 1. 미러 도구 실측 (`corpus_mirror_sync.py --check`)

- 검사 스코프: `references/final.md` 11쌍 × 2불변식(①소스 본문≡배포 본문, ②배포 Claude≡배포 Codex byte-exact).
- 결과: **11/11 in-sync, exit 0** (2026-08-18 실행). 11개 스킬 전부 inv1=inv2=in_sync.
- 도구 자체 선언(docstring 17~18행): SKILL.md · agents/*.md · commands/*.md 는 「plugin-native 단일 파일, 소스 미러 없음」을 근거로 **스코프 밖**. 이 면제 근거는 불변식1(소스 stale 회귀)만 다루고 **불변식2(양판 표류)는 다루지 않는다** — 실제로 codex 대응물이 전부 존재하고 표류도 실측됐다(아래 §4).
- 스크립트 미러는 이 도구가 아니라 **Makefile release 단계의 `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts`** 가 검사한다(릴리즈 시점 한정 — 상시 검사 아님).

## 2. 개명 매핑 규칙 (실측 확인)

codex 쪽은 dddart 형제 플러그인과의 전역 이름 충돌 스킬만 `dddjango-` 접두로 개명했다:

| 부류 | claude 경로 | codex 경로 |
|---|---|---|
| 충돌 스킬 4종 | `dddjango/skills/<s>/` | `codex-dddjango/skills/dddjango-<s>/` (architecture-ddd · discipline-cleancode · discipline-houserules · implementation-test) |
| 비충돌 스킬 7종 | `dddjango/skills/<s>/` | `codex-dddjango/skills/<s>/` (무접두) |
| 에이전트 7종 | `dddjango/agents/<a>.md` | `codex-dddjango/skills/dddjango-<a>/SKILL.md` (전원 접두, 역할 스킬화) |
| 커맨드 | `dddjango/commands/dddjango.md` | `codex-dddjango/skills/dddjango/SKILL.md` (오케스트레이터 스킬화) |
| 검사기 스크립트 33종 | `dddjango/scripts/*.py` | `codex-dddjango/skills/dddjango/scripts/*.py` |

## 3. 양판 대응표 (실측)

판정 기호: ✓=identical(byte) · ≈=정당 차이(플랫폼 판별 표기) · ✗=내용 표류 의심 · △=경계 사례.

### 3.1 references/final.md — 11쌍 전부 identical

| 스킬 | codex 대응 | 판정 | 행수 |
|---|---|---|---|
| architecture-api | architecture-api | ✓ | 638 |
| architecture-db | architecture-db | ✓ | 736 |
| architecture-ddd | dddjango-architecture-ddd | ✓ | 2122 |
| discipline-cleancode | dddjango-discipline-cleancode | ✓ | 2548 |
| discipline-houserules | dddjango-discipline-houserules | ✓ | 242 |
| discipline-tdd | discipline-tdd | ✓ | 1122 |
| implementation-django | implementation-django | ✓ | 1789 |
| implementation-django-ninja | implementation-django-ninja | ✓ | 1019 |
| implementation-django-web | implementation-django-web | ✓ | 424 |
| implementation-python | implementation-python | ✓ | 2675 |
| implementation-test | dddjango-implementation-test | ✓ | 2754 |

### 3.2 SKILL.md — 11쌍 전부 diff, 10쌍 정당 · 1쌍 표류

공통 정당 차이 패턴(전 쌍): ⓐ claude 전용 frontmatter `user-invocable: false` 제거(행수 −1의 정체) ⓑ 충돌 스킬 상호참조를 `dddjango-*`로 개명 ⓒ `dddjango:<skill>` 플러그인 한정 표기 → codex 평면 이름.

| 스킬 | 행수(claude/codex) | 판정 | 차이 성격 한 줄 |
|---|---|---|---|
| architecture-api | 51/50 | ≈ | ⓐ+ⓑⓒ(description·위임 목록의 architecture-ddd 개명)뿐 |
| architecture-db | 47/46 | ≈ | ⓐ+ⓑ뿐 |
| architecture-ddd | 45/44 | ≈ | ⓐ+name 개명뿐 |
| discipline-cleancode | 56/55 | ≈ | ⓐ+name·상호참조 개명뿐 |
| discipline-houserules | 83/82 | ≈ | ⓐ+name·description·본문 상호참조 개명뿐 |
| discipline-tdd | 53/52 | ≈ | ⓐ+위임 목록 개명뿐 |
| **implementation-django** | 53/52 | **✗** | ⓐⓑ 외에 **핵심 요약 규범이 다르다**: claude 「비즈니스 로직은 뷰가 아니라 모델·도메인에 — 평면 Django 맥락은 fat model(§4.1), dddjango 표준 4계층은 `domain_layer` 애그리거트 소유(`architecture-ddd` §3.2)」 vs codex 「비즈니스 로직은 fat model에 두고 뷰·시리얼라이저는 얇게 (§4.1)」 — codex가 **구판 무조건-fat-model 문장**을 유지, dddjango 4계층 교리와 정면 충돌 |
| implementation-django-ninja | 56/55 | ≈ | ⓐ+ⓑⓒ뿐 |
| implementation-django-web | 50/49 | ≈ | ⓐ+ⓑ뿐 |
| implementation-python | 68/67 | ≈ | ⓐ+ⓑⓒ뿐 |
| implementation-test | 68/67 | ≈ | ⓐ+name 개명뿐 |

### 3.3 agents 7쌍 — 6쌍 정당 · 1쌍 경계

공통 정당 차이 패턴: frontmatter의 `tools:`/`skills:` 목록 제거 → 본문 「## 로드할 지식 스킬」 절로 이전, description에 spawn_agent·「사용자가 직접 호출하지 않는다」 추가, h1 「(서브에이전트 역할)」, Coordinator↔코디네이터 표기, Bash→「네이티브 셸」·Read/Grep/Glob→「네이티브 파일 탐색 도구」·Write 도구명 제거.

정규화(개명·표기 치환+frontmatter/로드절 제외) 후 잔차 diff 실측:

| 에이전트 | 행수(claude/codex) | 잔차 | 판정 | 차이 성격 한 줄 |
|---|---|---|---|---|
| acceptance-tester | 54/53 | 0행 | ≈ | 플랫폼 표기 외 본문 완전 일치 |
| **coder** | 71/67 | 9행 | **△** | claude 단판: 「검사기 확장 리터럴 경로」(도구 승인 매칭 — Claude Code 전용, 정당). **codex 단판: 「읽기 전용 확인은 한 턴에 묶는다(2026-08-15 · 왕복 다이어트)」 — 플랫폼 한정 근거 무표기의 단판 규범**(같은 날짜의 의도적 codex 최적화일 개연성이 높으나 문서상 판별 불가) |
| design-architect | 96/95 | 14행 | ≈ | 「산출물-우선 쓰기」 절이 양판 모두 존재(위치만 다름·claude판에 「codex 동형」 마커), 나머지는 도구 표기 |
| design-review-api | 84/86 | 0행 | ≈ | 플랫폼 표기 외 본문 완전 일치 |
| design-review-db | 44/46 | 0행 | ≈ | 상동 |
| design-review-ddd | 44/47 | 0행 | ≈ | 상동 |
| discipline-reviewer | 130/130 | 6행 | ≈ | subagent↔서브에이전트, 「커맨드 Phase 2」↔「dddjango SKILL의 Phase 2」 상호참조 적응뿐 |

### 3.4 커맨드(Coordinator 정본) 1쌍 — 표류 1건 실증

`dddjango/commands/dddjango.md`(176행) ↔ `codex-dddjango/skills/dddjango/SKILL.md`(201행). 정규화 잔차 178행 — 대부분 의도된 플랫폼 재저작:

- 정당(설계상 의미 미러): `$ARGUMENTS` 행(claude 전용) / codex 전용 「Codex 실행 모델」 절(spawn_agent·wait_agent·multi_agent config·대기 정책·결과 미수신 판정) / AskUserQuestion↔request_user_input+평문 fallback 절 / task 리스트(TodoWrite) 채널(claude 전용 — codex는 삭제) / `${CLAUDE_PLUGIN_ROOT}/scripts/…` 27개 경로 → `scripts/…` 상대 경로 / 병렬 정의(한 응답 다발 ↔ 전부 spawn 후 wait) / coder 입력의 플러그인 설치 루트 전달(claude 전용).
- **✗ 표류 실증 — 번호 공간 규약 문장 누락**: claude판 규약에 있는 「범위 표기 `#A~#B` 는 정본에서 걷힌 번호를 제외한 실재 번호만 가리킨다」 문장이 codex판에 없다(grep '범위 표기': claude 1 / codex 0). codex 본문은 `#A~#B` 범위 표기를 **9회 사용**하므로 이 판독 규칙의 부재는 실해가 있다. corpus_lint ②가 「commands 머리의 번호 공간 규약 문장이 사람 판별의 근거」라고 명시한 바로 그 문장의 반쪽이다.
- 사소 문면 표류(의미 동일, 기록만): 「scope에서」↔「scope에서는」, 「직접 쓰지 않는다」↔「직접 patch하지 않는다」, claude판 내 Coordinator/코디네이터 혼용.

### 3.5 스크립트 33쌍 + 매니페스트

- `dddjango/scripts/*.py` 33개 전부 codex 대응물 존재, **diff -q 전부 identical**.
- `dddjango/.claude-plugin/plugin.json` ↔ `codex-dddjango/.codex-plugin/plugin.json`: 형식·필드가 플랫폼별로 다름(정당). version **2.12.0 양판 일치**(Makefile release가 강제 검증).
- codex 단독 파일: `codex-dddjango/skills/dddjango/agents/openai.yaml`(인터페이스 메타) — claude 대응물 없음, 정당(플랫폼 전용 배선).

## 4. 표류 무방비 지대 (규범 문장 보유 + 쌍둥이 등가성 무검사)

보호 지도 실측: final.md 11쌍 = `corpus_mirror_sync`(릴리즈 게이트 포함) / 스크립트 33쌍 = Makefile release `diff -rq`(릴리즈 시점만) / **그 외 문서쌍 = 검사 도구 0**. corpus_lint(문면 위생)·anchor_integrity_check(§앵커 해소)는 codex 문서를 훑지만 **양판 등가성은 판정하지 않는다**. AGENTS.md는 이들을 「의미 미러」로 선언만 하고 집행 장치가 없다.

| # | 무방비 파일(쌍) | 규범성 | 비고 |
|---|---|---|---|
| 1 | SKILL.md 11쌍 | 트리거·위임 경계·핵심 규범 요약 | 실증 표류 1건(implementation-django) — 요약 규범이 final.md와 어긋나도 못 잡는다 |
| 2 | agents 7쌍 | 파이프라인 집행 규범 본체 | 경계 1건(coder 왕복 다이어트 단판) — 「플랫폼 정당 차이」와 「표류」를 가를 표기 규약이 없다 |
| 3 | commands/dddjango.md 쌍 | 파이프라인 정본(Coordinator) | 실증 표류 1건(번호 공간 규약 반쪽 누락) |
| 4 | (반무방비) 스크립트 33쌍 | 백스톱 판정 로직 | 릴리즈 사이 기간에는 어떤 도구도 안 봄 — `corpus_mirror_sync --check` 단독 실행으로는 미검사 |
| 5 | plugin.json 쌍 | 낮음(메타) | version만 검증, description·interface 문면은 무검사 |

구조적 관찰: 의미 미러는 byte 비교가 원리상 불가하지만, 이번 실측이 쓴 방법(개명 4종·플랫폼 표기 치환·frontmatter/플랫폼 전용 절 제외 후 잔차 diff)으로 **잔차 0~수 행까지 기계 축약이 가능**했다(7쌍 중 4쌍 잔차 0). 잔차 화이트리스트 방식의 결정적 검사가 성립할 여지가 있다.

## 5. 방법 기록

- 읽기 전용만 실행: `--check`(exit 0 확인), `diff -q`/`diff`, `wc -l`, python 정규화 diff(stdout 출력만). 조사 대상 파일 무수정.
- 정규화 규칙: codex→claude 방향으로 `dddjango-<name>`→`<name>`(11종), 코디네이터→Coordinator; claude→ `dddjango:<skill>`→`<skill>`; frontmatter·h1·「로드할 지식 스킬」 절 제외 후 unified diff.
- Serena: skipped — 문서 대조 실사라 기본 도구(diff·grep)로 충분.
