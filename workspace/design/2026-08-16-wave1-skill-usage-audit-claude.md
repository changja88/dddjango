# 웨이브 1 스킬 사용 감사 — Claude 세션 (증거 문서)

> 2026-08-16 실시. broccoli-server-rebuild 웨이브 1에서 dddjango v2.11.0 플러그인이 의도한 대로
> 스킬·에이전트가 사용됐는지, Claude 쪽 세션 2건(child_settings 워커 · llm_meta 교차 리뷰어)의
> transcript 를 감사한 서브에이전트 보고 전문이다. 후속 개정(인용-실독 결합 · 순서 규정 정비)의
> 증거 앵커로 쓴다. 감사 대상 transcript:
> - child_settings 워커: `~/.claude/projects/-Users-hyun--paseo-worktrees-2ktg9lew-rebuild-child-settings/5deaf422-4921-4bf4-9086-4d43d7cde3ec.jsonl`
> - llm_meta XR: `~/.claude/projects/-Users-hyun--paseo-worktrees-2ktg9lew-rebuild-llm-meta/5e0907c9-4740-4135-82a8-5d1a26f7a0dd.jsonl`

---

## 0. 의도 기준(정본)에서 뽑은 기대치

정본: `~/.claude/plugins/cache/changja88-dddjango/dddjango/2.11.0/` (commands/dddjango.md, agents/*.md, skills/*/SKILL.md)

| 에이전트 | 필수 스킬(frontmatter) | 조건부/추가 로드 | 로드 방식 의도 |
|---|---|---|---|
| Coordinator(command) | 스킬 없음(Agent·Bash 등만) | Phase 0 빚 스캔·G2에서 27종 registry + `registry_gate.py --anchor` 직접 실행 | 서브에이전트 위임이 원칙, 명세·코드 직접 작성 금지 |
| design-architect | architecture-ddd·api·db, discipline-houserules, discipline-tdd | — | **houserules `references/final.md` §0·§1(140행)은 반드시 실독**해 명세에 박음. 나머지는 "필요한 절만"(전체 로드 불필요) |
| design-review-ddd | architecture-ddd | — | 스킬 절 인용 의무, references는 필요 절만 |
| design-review-api | architecture-api, discipline-tdd | — | 동일 |
| design-review-db | architecture-db, discipline-tdd | — | 동일(§9.6 Risky Write 8행 대조 등) |
| acceptance-tester | discipline-tdd, implementation-test, architecture-api, architecture-ddd, implementation-django-ninja | add/update 있을 때만 러너 셋업(§2.1) | tdd decision 먼저, implementation-test는 승인된 add/update의 mechanics로만 |
| coder | implementation-django·django-ninja·django-web·python, discipline-tdd, implementation-test, discipline-cleancode, discipline-houserules | "작업에 맞는 스킬을 골라" 사용(web은 서버렌더일 때만 등) | houserules final.md 골격 실현 의무, 검사기 호출은 확장 리터럴 경로 |
| discipline-reviewer | discipline-cleancode, discipline-tdd, implementation-test, discipline-houserules | — | final.md와 «직접» 대조(명세 부합만으로 통과 금지) |

로드 방식 실측 사실: **frontmatter의 `skills:` 목록은 하네스가 서브에이전트 기동 시 SKILL.md 전문을 초기 user 메시지로 자동 주입**한다(사이드체인 초기 user 메시지 수 = 스킬 수+1로 실증: coder 9=8+1, discipline 5=4+1, ddd 2=1+1, acceptance 6=5+1). 따라서 SKILL.md 수준의 누락/과잉은 구조적으로 발생 불가하고, 감사 실익은 **references/final.md 실독 여부·부분 적재 방식**에 있다. 또한 대상 저장소의 `rebuild/specs/discipline/` 5파일은 플러그인 스킬 파일과 **byte-identical**임을 diff로 확인했다(standard-tree-final.md = discipline-houserules `references/final.md`, houserules-skill.md = 그 SKILL.md, cleancode-skill/final = discipline-cleancode SKILL/references, architecture-db-final = architecture-db references). 즉 사본 참조 = 정본 값 참조다.

---

## 세션 1 — child_settings 리빌드 워커

(사이드체인 17개는 같은 폴더 `…/subagents/agent-*.jsonl`)

### (a) 파이프라인 골격 — 준수율 높음 (12개 규정 항목 중 9 준수 · 3 부분 이탈)

준수한 것:
- `/dddjango` 오케스트레이터를 Skill 도구로 정식 로드(L15) 후 Coordinator 역할 수행. 설계·테스트·코드는 전부 서브에이전트에 위임(직접 작성 0).
- 규정 에이전트만, 전부 `dddjango:` 한정 표기로 17회 디스패치. 비규정 에이전트 사용 0.
- Phase 1 리뷰 다발: ddd·api·db·discipline-lightweight 4종을 **한 응답 안의 다발**로 호출(L140·142·144·146) — "병렬 = 한 응답 안 다발" 규정 준수. 다발 전 project-wide tree 입력 준비도 선행(L134).
- G1 배너(L235)→조정자 승인 수신(L238) 후에만 Phase 2 진입. 승인 없는 게이트 통과 없음.
- `build_anchor`를 Phase 2 **첫 파견(acceptance-tester L251) 이전** L242에서 기록, "이미 있으면 재기록 금지" 가드까지 구현.
- G2: `registry_gate.py . --anchor`로 27종 전수 판정 차분(L384), 미이관 표준 경로 의존 발견 시 즉석 수리하지 않고 `STOP-G2-wiring-checker-conflict.md` 작성+배너 표면화(L425·429)→조정자 승인(L432) 후 `--legacy-debt-file` 격리 재실행(L447·453)·응답을 STOP 파일에 추기(L462) — STOP 절차 교과서적 준수.
- 전체 suite는 Coordinator가 직접 실행(make testp-fresh, L471).
- 수정 모드(교차리뷰 FAIL 반송, L493): architect 재호출(L510)→외부 계약=acceptance-tester(L522)/내부·구현=coder(L520) 소유별 라우팅→focused discipline 감사(L538)→registry_gate 재확인(L540). 두 병렬 역할의 편집 파일 겹침 0이라 "같은 파일 병렬 편집 금지"도 비위반.
- coder의 검사기 호출은 규정대로 확장 리터럴 절대 경로(사이드체인 4곳 확인), positional TARGET=루트.

부분 이탈:
1. **Phase 0 빚 스캔(27종 registry) 미실행** — 첫 check-* 실행이 G2 시점(L384)이다. 단 발주문(L6)이 "G0은 발주서 수용으로 갈음"을 계약했으므로 발주 종속 이탈로 분류.
2. **슬라이스 3개인데 S3 전용 경량 감사 생략** — 규정은 "슬라이스마다 경량 + 마지막 홀리스틱"인데 실측은 S1(L278)·S2(L297)·홀리스틱(L382)뿐. 홀리스틱이 S3 산출물 전량을 실독해 실질 공백은 없다. 부수적으로 S1 경량 감사와 S2 coder를 같은 메시지에 병렬 배차해 "감사→coder 반영" 순서 의도가 약화됐다.
3. **task 리스트(하네스 task 도구) 미사용** — 진행 가시성 보조 채널 규정(ⓐⓑⓒ) 위반. 1차 채널(게이트 배너·한 줄 상태)은 준수.

### (b) 스킬 로드 실태

| 역할 | SKILL.md(자동 주입) | references/정본 값 실독 | 판정 |
|---|---|---|---|
| architect(초안) | 5종 전량 | standard-tree-final.md 전문 + houserules-skill.md(주입분과 중복 — 무해한 과잉) | **준수** — houserules final.md 실독 의무 이행(사본 경유·byte-identical) |
| ddd 리뷰어 | 1종 | 없음 | **요주의 — 최종 노트에 §3.2·§3.7 등 12개 절 인용을 남겼으나 references 실독 0회**(주입된 SKILL.md 요약표+자기 지식 기반 인용) |
| api 리뷰어 | 2종 | 없음 | 중도 소멸로 판정 불가(아래 (c)) |
| db 리뷰어 | 2종 | architecture-db-final.md를 `[o=380,l=160]`·`[o=255,l=130]` **2회 부분 적재**(§9.5~§9.7 영역) 후 §9.6 8행 대조 | **모범 사례** — 부분 적재 의도 그대로 |
| discipline(경량·S1·S2·홀리스틱·수정) | 4종 | standard-tree-final.md 실독(경량·S1·홀리스틱; S2는 `[o=75,l=65]` 부분) + 코드 직접 대조 | **준수** — "final.md와 직접 대조" 의무 이행 |
| acceptance-tester | 5종 | 없음(명세·wire 정본·auth 실코드로 대체) | 허용 범위 — pytest Red 실행·러너 확인·비계 규율·보고 형식 모두 이행 |
| coder S1/S2/S3 | 8종 전량 | standard-tree-final.md(S1·S3 전문, S2 부분) | **준수+특이** — S1은 검사기 소스를 직접 Read해 골격 확정(정본과 동일 값이라 무해), S3는 implementation-django-ninja references 대신 설치된 ninja `site-packages` 소스를 직접 확인(대체 경로) |

- 누락: SKILL.md 수준 0(하네스 보장). references 수준에서는 architecture-ddd·api·tdd·cleancode·implementation-* 계열 references/final.md 실독이 전 역할 통틀어 0회 — 다만 SKILL.md가 "필요한 항목만(전체 로드 불필요)"이라 규정하므로 기계적 위반은 아니고, 요약 주입 + 실코드/명세 대체가 실제 운용 패턴이었다.
- 과잉: architect의 houserules-skill.md 재독 1건(주입분 중복) — 무해.
- 방식 위반: 전문 통째 로드는 0건. 부분 적재(offset/limit·grep) 관행이 정착돼 있다.

### (c) 특이 사항

- **api·discipline 리뷰 사이드체인 중도 소멸 → Coordinator 인라인 대체**: 두 사이드체인은 04:23~04:31 실질 조사를 수행하다 최종 노트 없이 끊겼다. 2시간 뒤 조정자 개입(L202) 지시에 따라 Coordinator가 추가 조사 없이 기존 컨텍스트로 인라인 감사를 선언(L211). 리뷰 독립성·"Coordinator는 리뷰를 직접 하지 않는다"는 의도가 이 지점에서 훼손됐다(조정자 지시에 따른 장애 복구라는 정상 참작 있음).
- **네 API-error checker(registry #2·#15·#5·#6)의 scope-렌더(--error-profile preserve-established) 미확인** — scope-렌더는 #16 `check-composition-root`(L398) 1건뿐. 명령서 기준 error-response 관련 scope면 네 checker도 각각 렌더 대상이다(경미~중간, 12-slot 승인 내용에 따라 면책 가능).
- coder S2 에이전트를 SendMessage로 재개해 stale docstring nit를 원작성자에게 반송(L440) — "만든 역할이 고친다" 의도에 부합하는 모범 사용.
- 각 역할 완료 보고에 `pytest N회 · 총 M초` 관찰 라인, Serena 생략 사유 한 줄, `TREE_CONTRACT_MISMATCH` 무발생 확인 등 규정 보고 형식 이행.

### 종합 판정: **의도대로 사용함 (경미한 부분 이탈 동반)**

골격·게이트·백스톱·STOP 절차·역할 소유권이 높은 충실도로 이행됐다. 이탈은 S3 경량 감사 생략, task 리스트 미사용, 리뷰 2종 인라인 대체(장애 복구), scope-렌더 부분 미실행 정도이며 산출물 품질에 실질 구멍을 낸 항목은 확인되지 않았다.

---

## 세션 2 — llm_meta 교차 리뷰어(XR)

### (a) 파이프라인 골격 — 해당 없음(구조적으로 파이프라인 밖)

발주문(L6)이 이 세션을 dddjango 파이프라인이 아니라 **단독 적대적 감사자**로 설계했다(산출물은 xreview 보고서 1건, 렌즈 5종, 실측 3종). Agent 디스패치 0·Skill 호출 0은 발주 설계상 의도된 형태로, dddjango 에이전트 생략을 위반으로 보지 않는다. 다만 플러그인 관점에서 이 리뷰는 discipline-reviewer 에이전트의 관할 업무를 세션 본체가 대행한 구조다.

### (b) 스킬(정본 규율) 로드 실태 — 발주 정본 5파일 중 3만 접근

| 발주 정본(= 플러그인 스킬 사본) | 접근 | 방식 |
|---|---|---|
| standard-tree-final.md (= houserules references/final.md) | O | 전문 Read(L90) |
| houserules-skill.md (= houserules SKILL.md) | O | 전문 Read(L97) |
| architecture-db-final.md (= architecture-db references) | 부분 | grep만(§9.6·Risky Write 앵커, L106) — 부분 적재 의도 부합 |
| **cleancode-skill.md** (= discipline-cleancode SKILL.md) | **X** | Read·Bash 접근 0회 |
| **cleancode-final.md** (= discipline-cleancode references) | **X** | Read·Bash 접근 0회 |

- **누락(핵심 발견)**: 렌즈 ③이 "클린코드"를 명시하고 발주문·scope.md가 cleancode 2파일을 정본으로 실명 지정했는데 **한 번도 읽지 않고** 클린코드 판정을 수행, 최종 보고서(L436 Write)에는 정본 5파일 목록을 그대로 인용했다 — 클린코드 렌즈를 자기 지식으로 진행한 정황이 명확하다.
- design.md도 전문 정독 대신 헤더 grep(L49)·타깃 grep(L54)·부분 Read(L346)로 처리 — targeted 적재로는 우수하나 발주문의 "정독" 요구 대비로는 절충.
- 과잉 로드: 없음(오히려 부족 방향).

### (c) 특이 사항

- **플러그인 백스톱 재발명**: 타입 어노테이션 전수 점검을 플러그인 registry #11 `check-public-surface-annotation.py`(사용 가능 상태) 대신 자작 AST 스캐너 3본(`/tmp/annscan*.py`, L296·302·308)으로 수행. 발주문이 "AST 수준 점검"만 요구했으므로 위반은 아니나 결정적 백스톱과의 판정 동형성이 보장되지 않는다.
- 실측 의무 3종은 전부 이행(ⓐ OpenAPI export+diff L67~80, ⓑ collect-only L80·86, ⓒ not-django_db L86), 금지 사항(make testp·brew 조작·django_db 실행)도 준수. ruff·graphify 보조 실행, Serena 미부착 사실을 규정대로 한 줄 보고.
- 대상 BC 소스·테스트 약 60파일을 전량 실독한 뒤 PASS(blocker 0) 판정 — 검증 자체의 성실성은 높다.

### 종합 판정: **부분 이탈**

파이프라인 밖 단독 감사라는 구조는 발주 설계이므로 문제 삼지 않되, 지정 정본 5규율 중 클린코드 2파일 완전 미독 상태로 클린코드 렌즈 판정을 내고 보고서에 정본 목록을 인용한 것은 "스킬(정본) 대신 자기 지식" 이탈의 실증 사례다.

---

## 두 세션 공통 패턴

1. **SKILL.md는 하네스 주입·사본 지정으로 도달이 보장되지만, references/final.md(값 본문)는 houserules·architecture-db 외에는 실독이 거의 없고 절 번호 인용이 실독 없이 이뤄지기도 한다** — "필요한 절만 읽는다"가 실제로는 "요약만으로 진행"으로 기우는 경향.
2. **정본 유통이 플러그인 캐시가 아니라 저장소 스냅샷(`rebuild/specs/discipline/`) 경유로 일원화**돼 있다 — 현재는 byte-identical이라 무해하나, 플러그인 갱신 시 사본 부패가 두 세션 모두의 단일 실패 지점이 된다.
3. **백스톱·게이트 메커니즘(registry_gate·anchor·STOP·legacy-debt)은 규정 초과 수준으로 충실히 쓰이는 반면, 사람-순서 규정(슬라이스별 감사·task 리스트·정본 정독)은 효율을 이유로 생략되는 비대칭**이 공통적이다.
