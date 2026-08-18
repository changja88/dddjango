# A2 — workspace/tools 도구 생태 전수 실사 (P0 센서스)

- 조사일: 2026-08-18 · 대상: `/Users/hyun/Desktop/dddjango/workspace/tools/` 전 항목 21개
- 구성: Python 18 · HTML 1(생성물) · JSON 1 · MD 1
- 공통 관례(파이썬 검사 도구): docstring 첫 줄에 «메인테이너/빌드타임 — 런타임 게이트 아님» 부류 선언 반복. exit 규약 공유 — **0=clean/in-sync · 2=위반/drift · 3=구조 전제 깨짐(fail-CLOSED) · 1=usage/재료 결손**. 다수가 실행 전 합성 red/green **self-test 선행**(«검사를 좁혀서 green» 순환 차단)과 fail-CLOSED(파일 부재·파싱 실패 = exit 3)를 명문화.
- 블루프린트 3종(registry_lint / coverage_check / corpus_check)의 정의 문서는 이 저장소에서 발견되지 않았다(`grep` 0건 — workspace/design·plan 포함 전수). 따라서 아래 «블루프린트 대응» 열은 **전부 이름·기능 유사성 기반 추측**이며, 도구 쪽 사실(무엇을 검사하나)만이 확정 근거다.

## 전수 표

| 도구 | 역할 (검사·생성·측정 + 출력) | 입력 | 분류 | 블루프린트 대응 |
|---|---|---|---|---|
| anchor_integrity_check.py | 스킬 § 앵커 무결성 검사 — 인용자 문서의 §앵커가 정본 코퍼스에서 해소되는지 판정(OK/MISSING/AMBIGUOUS/UNKNOWN/UNRESOLVED). 출력: 위반 목록+집계, exit 0/2/3 | 인용자: `dddjango/agents/*.md`·`dddjango/commands/*.md`·`dddjango/scripts/*.py`·codex 역할 스킬 8종 SKILL.md·codex `dddjango/scripts/*.py` / 해소 정본: `dddjango/skills/<skill>/{SKILL.md, references/final.md}` | 정본 무결성 검사 | corpus_check 로 흡수 가능(추측 — 코퍼스 문면 무결성 부류. 도구 docstring 스스로 «corpus_lint·spec_lint 와 같은 부류» 명시) |
| corpus_lint.py | 배포 코퍼스 문면 위생 6검사: ①죽은 workspace/ 경로 ②끊긴 번호(#N·registry #N·의사결정 #N·D카드) ③별칭 혼용(걷어낸 옛 이름) ④재량 낱말 ⑤같은-문서 중복 ⑥트리-밖 예시 경로. 출력: 위반 목록, exit 0/2/3 | `dddjango/skills/*/references/final.md`·`*/SKILL.md`·`agents/*.md`·`commands/dddjango.md`·`dddjango/scripts/*.py`(AST 문자열 상수 ≥20자) + 잣대: 명세(2026-08-08-tree-revision-spec.md, spec_lint 재사용)·`standard_tree.py` | 정본 무결성 검사 | corpus_check 의 중심 후보(추측 — 이름 직대응) |
| spec_lint.py | 명세(538규칙) 정합성 8검사: ①중복 ②끊긴 참조 ③트리 140행 커버리지 ④결정 카드 57장 커버리지 ⑤죽은 문면 ⑥술어 정합 ⑦등급 정합 ⑧소유자 매핑 1:1. `--emit-owner-map` 으로 매핑표 골격 **생성**도 함. 출력: 위반 목록/매핑표 파일, exit 0/2/3 | `workspace/design/2026-08-08-tree-revision-spec.md`·`2026-08-11-predicates.md`·`docs/file_tree.html`·`workspace/plan/2026-08-11-rule-owner-map.md` | 정본 무결성 검사 | 분해 흡수 가능(추측): ①②⑤→corpus_check 성격, ③④→coverage_check 직대응, ⑥⑦⑧→registry_lint 성격. 한 도구가 3종에 걸친다 |
| checker_lint.py | «검사기의 검사기» — `check-*.py` 21개 규칙 준수 검사(#74·#75·#78 가드, #591㉣ allowlist 로드 금지, #42·#79·#80·#99·#204·#357 대상선정 앵커, #495·#496 등) + 메타 지침 5개(#72·#449·#452·#494·#592)의 문면 자리. 출력: 위반 목록, exit 0/1/2 | `dddjango/scripts/check-*.py`(AST·문면) | 정본 무결성 검사 | registry_lint 직대응 후보(추측 — registry 27종 검사기 자체를 린트하는 유일 도구) |
| reverse_coverage.py | 역방향 커버리지 — 플러그인 **전 파일**마다 그 존재를 설명하는 규칙·근거가 있는지(미설명 0) + 매핑표가 가리키는 경로 실재(죽은 소유자 0). 출력: 전 파일 분류표, exit 0/1/2 | `dddjango/` 전 파일 rglob + `workspace/plan/2026-08-11-rule-owner-map.md`(ⓒ·ⓓ 컬럼) | 커버리지·대조 | coverage_check 직대응 후보(추측 — spec_lint ⑧ 정방향의 역방향 짝) |
| fixture_matrix.py | 전수 fixture 실측표 — 검사기 × 위반 fixture × 기대/실측 exit 90케이스(skeleton 3 + 23종×2 + auto 3종×2 + checker_lint 2 + 호출 계약 27 + 수정 사이클 4×2). «백스톱 실측 0» 종결 장치. 출력: 일치/불일치 표(`--emit` md), exit 0/1/2 | `workspace/eval/fixtures/*`(임시 사본, hermetic)·`dddjango/scripts/check-*.py`·`checker_registry.py`(로스터 assert) | 커버리지·대조 | coverage_check 로 흡수 가능(추측 — 단, 대상이 코퍼스가 아니라 «검사기 행동»이라 registry_lint 성격 겸유) |
| checker_cross_matrix.py | 교차 fixture 스캔 — 각 레인 good/ 을 registry 27종 «전부»에 실행해 (레인×검사기) census 를 EXPECTED 와 양방향 대조. 검사기 간 요구/금지 충돌(상류 드리프트) 감지. 사유 enum 닫힘: 가드-red/골격-부재/최소성/모순-이월(0건). 출력: 차이 목록(`--emit-expected`), exit 0/1/2 | `workspace/eval/fixtures/*/good`(임시 사본)·`checker_registry.py`·`fixture_matrix.py`(레인 목록 import)·소스 내 EXPECTED 표 | 커버리지·대조 | coverage_check 로 흡수 가능(추측 — 표류 방어 성격 겸유. 3종 어디에도 딱 맞지 않는 «검사기 간 상호작용» 축) |
| api_error_backstop_matrix.py | API-error 검사기 3종의 실행형 RED 매트릭스(407KB) — 인라인 소스 fixture 로 검사기 CLI 계약(인자 어휘 ARGUMENT_ARITY 포함)을 실행 검증하는 «실행 가능한 명세». 출력: 매트릭스 판정, exit 코드 | 소스 내장 fixture 텍스트 + `dddjango/scripts/` 검사기 서브프로세스 | 커버리지·대조 | 자연 대응 없음(사실) — coverage_check 에 욱여넣으면 «계약 실행 명세» 성격이 소실(추측) |
| bc_registry_smoke.py | bc_registry_run 의 로스터 계약 스모크 — 단일-BC 그림자의 #365 과탐 소멸(A)·진양성 보존(B) 2단언 고정. 출력: exit 0/2 | 합성 2-BC 미니 저장소(임시 생성) + `bc_registry_run.py` | 커버리지·대조 | 자연 대응 없음(사실 — 검사 대상이 하네스 자체) |
| registry_gate_smoke.py | registry_gate(판정 차분 게이트)의 계약을 공격 재현 7케이스(공허 차분·귀속 red·legacy-only·선커밋 공격·부재 위반·빚 채널·usage)로 고정. release 게이트 [2/7] 등록. 출력: exit 0/1/2 | `workspace/eval/fixtures/skeleton/good_bc` 사본으로 임시 git repo 합성 + `dddjango/scripts/registry_gate.py` | 커버리지·대조 | 자연 대응 없음(사실 — 게이트 행동 고정) |
| anchor_diff_smoke.py | anchor_diff(scope-render 직접 계열 판정 차분)의 계약을 13케이스(N·V·M·A·B·E·E2·S1~S3·T·C1·C2)로 고정. git 앵커가 재료라 fixture_matrix 와 분리. release 게이트 [2/7] 등록. 출력: exit 0/1/2 | fixture 사본 임시 git repo + `dddjango/scripts/anchor_diff.py`·검사기들 | 커버리지·대조 | 자연 대응 없음(사실 — 게이트 행동 고정) |
| openapi_shape.py | openapi.json 을 «이름 지운 모양»으로 정규화(리빌드 A축) — $ref 인라인, operationId/title/tags/summary/example/x-date-* 제거, `--success-only` 로 오류 축 제외. 모양 diff 0 = 스팩 등가의 기계 판정 재료 생성. 출력: 정규화 JSON(stdout), exit 0/1 | 인자로 받은 openapi.json 덤프 | 커버리지·대조 | 자연 대응 없음(사실 — 대상이 플러그인 코퍼스가 아니라 대상 저장소의 API 계약) |
| bc_registry_run.py | 결정적 백스톱 27종을 한 BC 에 일괄 실행(클린룸 리빌드 C축) — 대상 BC 만 담은 비-git «그림자 사본» hermetic 실행, 로스터 소비 2종(context-isolation·port-adapter-pairing)만 이웃 빈 스텁 two-pass. 출력: 종합 판정, exit 0/1/2 | 인자: 대상 저장소·BC 이름 / `checker_registry.py`(27종 단일 출처)·`checker_target.py` import | 기타(판정 실행 하네스) | 자연 대응 없음(사실 — 검사기가 아니라 실행기. 한계 명문: 이웃 «내용» 필요한 규칙은 registry_gate 몫) |
| corpus_mirror_sync.py | 코퍼스 미러 동기 검사·해소 — 불변식1: 소스 본문 ≡ 배포 본문(첫 비-P1 `## ` 이후 byte-exact) · 불변식2: 배포(Claude) ≡ 배포(Codex) 전체 byte-exact. `--write` 로 소스←배포·codex←배포 재동기. 출력: 스킬별 in_sync/drift/structure 표(text/json), exit 0/2/3 | 미러 쌍 11개(final.md 보유 스킬 전부): `workspace/reference/<skill>/reference/final.md` ↔ `dddjango/skills/<skill>/references/final.md` ↔ `codex-dddjango/skills/dddjango-<skill>/references/final.md` | 미러·표류 방어 | corpus_check 로 흡수 가능(추측 — 코퍼스 «복제 계층» 동기라는 별도 축임은 사실) |
| tree_mirror_check.py | 표준 트리 140행 삼중 동기 — A 정본 `docs/file_tree.html`(data-r) ≡ B `dddjango/scripts/standard_tree.py` ≡ C houserules final.md TREE 블록. kind 3종(fixed/placeholder/reappear, #491) 재도출 대조. `--write` 로 A→B·C 재생성. 출력: drift diff, exit 0/2/3 | `docs/file_tree.html`·`dddjango/scripts/standard_tree.py`·`dddjango/skills/discipline-houserules/references/final.md` | 미러·표류 방어 | corpus_check 로 흡수 가능(추측 — corpus_mirror_sync 와 같은 부류라고 docstring 자기 선언) |
| migration_gate.py | 리빌드 실측기 — 대상 저장소에 V1 옛 이름 폴더(presentation_layer·infra_layer·published_service·acl·옛 common/) 잔존 수 측정, 잔존 0 = 리빌드 완료. 옛 이름 목록은 «역사적 상수» 고정본. 출력: 잔존 목록, exit 0/1/2 | 인자로 받은 대상 저장소(들)의 `application/*/` 디렉터리 트리 | 미러·표류 방어 | 자연 대응 없음(사실 — 대상이 플러그인이 아니라 사용자 저장소의 이관 상태) |
| session_telemetry.py | 파이프라인 세션 텔레메트리 파서 — Claude Code 세션 jsonl 의 시간·토큰 분해(병렬 판정=실행 구간 겹침, 비용 가중 cache_read 0.1/output 5.0). «추측 말고 측정» 용. 출력: stdout 집계 | 세션 `*.jsonl`(인자 또는 `--smoke N`) | 관측·리포트 | 대응 없음(사실 — 검사 축 밖 관측 도구) |
| smoke_report.py | smoke1~8 비교 분석 HTML 리포트 생성기 — 세션 jsonl + 메모리 근거 서술 결합, 기계시간=wall−사람 대기 갭. 출력: `smoke_timeline.html` 생성 | `~/.claude/projects/` 아래 smoke 세션 jsonl + 소스 내 서술(NARR) | 관측·리포트 | 대응 없음(사실) |
| smoke_timeline.html | smoke_report.py 의 생성물 — self-contained 비교 분석 HTML(도구 아님, 산출물) | (생성물 — 입력 없음) | 관측·리포트 | 대응 없음(사실) |
| lane-claude-permissions.json | claude 레인 도구 승인 allowlist 정본(B0-2) — `permissions.allow` 7규칙(.venv python·env-prefix python·cat·sed -n·mkdir -p·touch·graphify query). 레인 저장소 `.claude/settings.local.json` 으로 복사해 쓰는 데이터 | (데이터 파일) | 기타(레인 운영 재료) | 대응 없음(사실 — 검사 축 밖) |
| lane-claude-permissions.md | 위 allowlist 의 복사 절차·실측 근거(r2″ 세션 승인 왕복 59회 분석)·잔여 한계·금지 확인 문서 | (문서) | 기타(레인 운영 재료) | 대응 없음(사실) |

## 지정 7종 코드 실사 상세

### anchor_integrity_check.py — 앵커 문법 6형(닫힌 목록)과 커버 범위
1. ① 표준형 `` `skill-name` §N[.M] `` — 백틱 스킬명 + 밖의 §(사이 40자 내 조사 허용)
2. ② 백틱 내장형 `` `skill-name §N[.M]` `` — 한 백틱 안
3. ③ 약칭형 `houserules §N`·`cleancode §N` — ALIASES 사전(→ discipline-houserules/-cleancode)으로 해소
4. ④ 무스킬명형 `final.md §N`·맨 `§N` — 같은 행의 직전 스킬 언급으로 귀속, 실패 시 UNRESOLVED(보고만·위반 아님)
5. ⑤ 하위 항·행 범위 — «항-(2)»·«제목» 동반 시 §N 절 실재 + «제목» 본문 실재까지 검증(항 번호 자체는 검증 밖)
6. ⑥ codex 접두형 — `dddjango-architecture-ddd` → `architecture-ddd` 로 접두 제거(①②의 변형)

연쇄 표기(`§3.2·§3.6`)는 직전 매치의 스킬을 승계. 판정 5종: OK / MISSING(스킬 실재·§부재) / AMBIGUOUS(houserules 류 이중 §공간의 «양쪽 다 있는» 충돌 번호만) / UNKNOWN(스킬명 자체 부재) / UNRESOLVED(④ 귀속 실패 — 보고만). §3.2 는 부모 §3 실재로도 해소(하위 구조는 보고 소관). 커버 문서(인용자): `dddjango/agents/*.md` · `dddjango/commands/*.md` · `dddjango/scripts/*.py` · codex 역할 스킬 8종(dddjango, -coder, -acceptance-tester, -design-architect, -design-review-ddd/-api/-db, -discipline-reviewer)의 SKILL.md · codex `dddjango/scripts/*.py`. 지식 스킬 SKILL.md 의 자기-§ 요약표는 의도적 대상 제외(명세 §1-A). self-test 11+1케이스 선행.

### corpus_lint.py — 6검사 실사
검사 대상 수집: skills 의 `*/references/final.md` 전부 + `*/SKILL.md` 전부 + `agents/*.md` + `commands/dddjango.md`(md 22), 스크립트는 `dddjango/scripts/*.py` 를 AST 로 파싱해 문자열 상수(≥20자)만. ② 는 spec_lint 의 `load_rules`·`LIVE_CARDS` 를 import 재사용해 생존 규칙 집합을 얻고, 번호 공간 4개(무접두 #N=생존 규칙 · registry #N=1..27 · 의사결정 #N=파일 내 선언 · D N=카드 57장)를 구문 위치로 가른다(무접두 registry 순번과 규칙 번호 충돌은 기계로 못 가름 — 한계 정직 기록). ③ 별칭 목록: presentation_layer · infra_layer · published_service · dto_in/out · ErrorOut · error_out · query_repository · `reference/final.md`(단수 오기) — 위치 기반 allowlist(파일 suffix·앵커 문면·건수 상한)만 허용, 문맥 휴리스틱 금지. ④ 재량 낱말(적절히·필요시·상황에 따라…9종)은 규범 4부류(houserules final.md·SKILL.md 전부·agents·commands)에만. ⑥ 은 `standard_tree.py` 를 잣대로 final.md 의 `application/…` 경로 주장(import 꼴·층 낱말 경유·.py 종결)을 트리 워크로 대조. self-test 는 bad/good 미니 코퍼스 합성 + 목록-밖 변형 검출 실증.

### corpus_mirror_sync.py — 미러 쌍 목록(실측 11쌍)
발견은 배포본 권위(`dddjango/skills/*/references/final.md` 보유 스킬): architecture-api · architecture-db · architecture-ddd · discipline-cleancode · discipline-houserules · discipline-tdd · implementation-django · implementation-django-ninja · implementation-django-web · implementation-python · implementation-test — **11개 전 스킬**. 각각 3자리: 소스 `workspace/reference/<skill>/reference/final.md`(P1 블록 보유 가능) ↔ 배포 `dddjango/skills/<skill>/references/final.md` ↔ codex `codex-dddjango/skills/dddjango-<skill>/references/final.md`(무접두 폴더는 하위 호환 fallback). 본문 경계 = 첫 비-P1 `## ` 헤딩~EOF, preamble 은 attribution 라인(h1·P1·blockquote·표·hr)만 허용(아니면 exit 3). 스코프 밖(설계상 면제): SKILL.md·agents·commands — plugin-native 단일 파일이라 R5 회귀 메커니즘 비해당.

### checker_cross_matrix.py
레인 = skeleton good_bc + fixture_matrix 의 PLAIN(23)+AUTO(3)+EXTRA(4) 쌍의 good/. 각 레인을 임시 사본(hermetic·비-git)으로 registry 27종 전부에 서브프로세스 실행, 자기 검사기는 exit 0 필수(아니면 재료 결손 exit 1), 타 검사기의 비-0 만 `(레인×검사기)→(exit, (규칙ID,건수)…)` census 로 수집해 소스 내 EXPECTED 와 양방향 대조(신규 red·기대 red 소멸·exit/규칙ID/건수 변화 전부 발화). EXPECTED 사유는 닫힌 enum(가드-red/골격-부재 #486~#490/최소성/모순-이월 0건), 무단 갱신은 «차분 세탁»으로 명문 금지. 한계 명문: 같은 (규칙ID×건수) 안 «의미»만 바뀌는 개정은 못 봄.

### reverse_coverage.py
분류 규칙: `scripts/check-*.py` 는 rule-owner-map ⓒ 규칙 ≥1 또는 PRIOR_CONTRACT_SCRIPTS 7종(선행 계약 소유), 인프라 6종(standard_tree·business_vocab·checker_target·checker_registry·registry_gate·anchor_diff)은 고정 사유. `agents/*.md` 는 ⓓ 규칙 또는 FLOW_DUTY(coder.md)/PIPELINE_ONLY 4종. skills 는 houserules(ⓐ정본/ⓑSKILL) + CORPUS_SKILLS 10(책 코퍼스). 어느 범주에도 없으면 «미설명» 위반, 매핑표가 가리키는 부재 경로는 «죽은 소유자» 위반.

### spec_lint.py
잣대 파일 4: 명세(tree-revision-spec)·predicates·`docs/file_tree.html`(140행 data-r)·rule-owner-map. 규칙 행 파싱은 7컬럼 계약 + 볼드 방어, 번호 중복 시 exit 3. 카드 정본 = 1..59 중 19·23 제외 57장. ⑧ 은 매핑표↔명세 1:1과 등급→소유자 모양·작업 값(재작성/치환/무변/신설) 검증. `--emit-owner-map` 은 검사가 아니라 매핑표 골격 **생성** 모드.

### tree_mirror_check.py
A(정본)는 생성기 ROWS 가 아니라 «생성된 HTML»의 data-r 140행을 읽음(파트 순서=명세 «트리 N행» 번호이기 때문). kind 는 조상이 연 `<토큰>` 집합으로 3종(fixed/placeholder/reappear) 재도출(#491 제1원칙). 불변식 A≡B(r·depth·name·kind)·A≡C(r·depth·name). `--write` 는 A 로부터 B 전체(모듈 코드 생성, SOURCE_SHA 각인)와 C 의 TREE:BEGIN/END 블록을 한 방향 재생성.

## 분류 집계

| 분류 | 수 | 항목 |
|---|---|---|
| 정본 무결성 검사 | 4 | anchor_integrity_check · corpus_lint · spec_lint · checker_lint |
| 커버리지·대조 | 8 | reverse_coverage · fixture_matrix · checker_cross_matrix · api_error_backstop_matrix · bc_registry_smoke · registry_gate_smoke · anchor_diff_smoke · openapi_shape |
| 미러·표류 방어 | 3 | corpus_mirror_sync · tree_mirror_check · migration_gate |
| 관측·리포트 | 3 | session_telemetry · smoke_report · smoke_timeline.html |
| 기타 | 3 | bc_registry_run(판정 실행 하네스) · lane-claude-permissions.json · lane-claude-permissions.md |

## 블루프린트 3종 대응 종합 (전부 추측 — 3종의 정의 문서가 저장소에 없음)

- **corpus_check ←** corpus_lint + anchor_integrity_check + corpus_mirror_sync + tree_mirror_check (+ spec_lint ①②⑤). 근거 사실: 이 넷은 docstring 에서 서로를 «같은 부류(registry 밖)»로 상호 지목하며 대상이 전부 배포 코퍼스 문면·복제 계층이다. 단 mirror 2종은 «검사+`--write` 해소»라는 쓰기 기능을 가져, 순수 check 로 흡수하면 해소 기능의 자리가 필요하다.
- **coverage_check ←** reverse_coverage + spec_lint ③④(트리·카드 커버리지) + fixture_matrix + checker_cross_matrix. 근거 사실: 넷 다 «X 마다 Y 가 있나/실측과 기대가 맞나»의 전수 대조 구조다. 단 fixture/cross 매트릭스의 대상은 코퍼스가 아니라 검사기 행동이다.
- **registry_lint ←** checker_lint + spec_lint ⑥⑦⑧(술어·등급·소유자 정합). 근거 사실: registry 27종 검사기 «자체»를 재는 도구는 checker_lint 가 유일하고, 로스터 값 정합은 spec_lint ⑧과 플러그인 쪽 checker_registry 자기 검증이 나눠 진다.
- **3종에 자연 대응이 없는 잔여(사실)**: 게이트·하네스 행동 고정 4종(bc_registry_run·bc_registry_smoke·registry_gate_smoke·anchor_diff_smoke)과 실행형 계약 명세(api_error_backstop_matrix), 대상-저장소 도구 2종(openapi_shape·migration_gate), 관측 3종, 레인 권한 2종. 이들을 3종에 욱여넣으려면 «판정 기계의 행동 고정(스모크)»이라는 네 번째 축이 필요하다(추측).
