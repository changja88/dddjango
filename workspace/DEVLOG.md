<!--
AI-OPTIMIZED DEVLOG. 이 문서는 dddjango 작업의 자기완결 정본이다.
읽는 규칙(AI):
  1) §0 Current State를 먼저 읽어라(지금 상태·베스트 구성·금지사항).
  2) 결정은 §2 Decision Records에서 상태태그(✅adopted/❌rejected/⏸blocked/✔verified)로 찾아라.
  3) 모든 수치·주장엔 증거 앵커(세션ID·커밋SHA·파일:라인)가 붙는다 — 추천 전 실재 확인하라.
  4) 개인 메모리(~/.claude)는 초기화될 수 있어 신뢰 못 함. 이 문서가 정본이다.
마지막 갱신: 2026-05-29
-->

# dddjango DEVLOG

`/dddjango` Claude Code 플러그인 파이프라인의 설계·구현·최적화 전체 여정 기록. AI가 읽는 자기완결 정본.

---

## §0 Current State (READ FIRST)

- **무엇**: 기존 Django 프로젝트에 한 기능을 DDD로 추가하는 Claude 전용 플러그인. 단일 진입 `/dddjango`. 코디네이터(메인 세션) + 서브에이전트 7 + 스킬 10, 게이트 G0/G1/G2.
- **브랜치**: `feat/dddjango-build` (main 미병합). **HEAD: `15ff62d`**.
- **현재 베스트 구성(검증됨)** = **커밋된 HEAD(`15ff62d`) + extended thinking OFF**. **smoke8(2026-05-28)이 최종 확인**: 코디 과금비용 **1.58M cost-unit(전 런 최저)**, 기계시간 **41분**, 테스트 **20/20**, §0/§4/ACL 전부 충족, 코더 토끼굴 0, architect 정정 재디스패치 0 — 역대 가장 깨끗, 회귀 없음. (smoke6도 동일 구성으로 1.98M·52분이었고, smoke8이 더 낮은 건 슬라이스 granularity 확률 변동.)
  - ⚠️ **thinking OFF는 코드가 아니라 사용자 세션 설정**(`Option+T` / `alwaysThinkingEnabled:false`). 플러그인에 못 박는다. 안 끄면 비용 ≈ 2.6M.
- **속도/비용 현실(닫힌 결론)**: 기계시간 ~41~60분은 "강한 모델 + 다단계 게이트 + TDD + 독립 리뷰" 품질우선 설계에 **내재**. 품질 손실 없이 큰 wall 단축하는 공짜 레버 없음. 통제 가능한 비용 레버는 이미 적용. 큰 비용 레버(컨텍스트 편집/compaction)는 업스트림 차단(§2 DR-11).
- **최적화 사이클: ✅ 종료** (2026-05-28, smoke8 합격). 다음 작업은 코드를 *실제로 바꿀 때*만 재개.
- **배포 상태**: Claude판 **v1.0.0 main 병합·릴리스** 완료(마켓플레이스 `changja88`). 그 후 **Codex 이식 착수** → **PoC 성공(§2 DR-12)**: `codex-dddjango/`(스킬 19, Claude `dddjango/` 무변경). 이어 **코드품질 1:1 평가(§2 DR-13)** → **결정성 2차 검증으로 결론 수정(§2 DR-14)**: N=2 결과 **1차 "claude>codex 13:2:5"는 상당 부분 N=1 분산**이었음. 핵심 신호(B1 도메인소유·stock≥0)가 양 런타임 모두 **비결정**. 2차 프레임워크 무관 코드 대등(codex가 일부 우위). **재현되는 진짜 차이 = 코드 우열이 아니라 게이트 노출 철학·스택 취향**. 표준준수 점수 추정 codex~70·claude~84(신뢰낮음, claude 분산>평균차). 평가 정본 `workspace/eval/`(`comparison-2.html`·`RUBRIC-conformance.md`).
- **B1-fix 표준 검증(§2 DR-15, 2026-05-29)**: DR-14가 남긴 B1 비결정 과제에 **일반화 표준 편집(architecture-ddd §3.2 단일출처 + design-review-ddd/discipline-reviewer 2층 탐지, 12파일 미커밋)**으로 대응 → 새 스모크(sample→clone)로 codex-4·claude-3 동시검증 = **양쪽 설계·코드 끝까지 B1 CLEAN(각 N=1)**. DR-13 빈혈·DR-14 죽은코드 부재. **표준 12파일 커밋(`98ebfd3`).** (claude-3 ninja 통제이탈은 수락; 프레임워크축 비교 무효.)
- **표준 빈칸 ③·④ 메움(§2 DR-16, 2026-05-29)**: DR-15 통제 비교가 드러낸 표준 두 빈칸(코드 버그 아님)을 메움 — ③ 기존 평면 코드에 도메인 판정 얹을 때 이주 기준을 **"판정·불변식 소유냐"**(레거시 아님)로 명문화(소유→`domain_layer` 이주/데이터 소스→평면 OK/컨텍스트 간 ACL·published만), ④ **API 스택을 design-architect 명세 1급 결정으로 승격**(기본 ninja·기존 존중)+ninja 버전핀 설치 규칙. **14파일 편집·미러 byte-identical·`plugin validate` PASS·서브에이전트 3렌즈 리뷰(정확성 2픽스 반영).** 정적까지 — 동적 검증 ⑥ 이연.
- **동적 검증 Tier 2·3 + ④ 보강(§2 DR-17, 2026-05-29)**: Claude(Tier 2) ③ **STRONG PASS**·④ inconclusive(ninja 편향). Codex 전체 스모크 ×3(Tier 3): ③ 완전이주 가능·Claude 수렴이나 **비결정**(t3 평면 유지). ④ 결과 = pre-boost plain(headless 무설치 보수성) → **`design-architect` 보강 후 Ninja+requirements 핀 수렴(t3c, 결정적)**. ④(e) 스택 설계승격 전파 **확정**. 산출 `workspace/eval/runs/{codex-5,6,7}`. 각 N=1(sanity).
- **스모크 방식 통일(§4)**: 마스터 `~/Desktop/dddjango-smoke-sample` + `git clone`으로 런타임별 타깃(`dddjango-{claude,codex}-index`). 구 reset.sh·E2E-SMOKE-METHOD.md 폐기.

---

## §1 What dddjango Is (architecture)

- **파이프라인**: 코디네이터가 작업을 역할로 분해 → 서브에이전트에 위임. 코디는 오케스트레이션·게이트·통합·검증보고만, 설계명세/인수테스트/구현코드는 직접 안 씀.
- **서브에이전트 7**: `design-architect`(통합 명세 작성·producer) · `design-review-{ddd,api,db}`(렌즈별 독립 리뷰·**병렬**·read-only) · `acceptance-tester`(블랙박스 인수테스트 Red) · `coder`(이중루프 TDD 구현) · `discipline-reviewer`(클린코드·TDD 규율 감사·read-only).
- **게이트**: G0 요구·스코프 → G1 설계 → G2 구현. 각 게이트는 사용자 승인(AskUserQuestion).
- **스킬 10**(서브에이전트 `skills:` frontmatter로 preload, `user-invocable:false`로 커맨드 전용): architecture-{ddd,api,db} · implementation-{django,django-ninja,django-web,python,test} · discipline-{cleancode,tdd,houserules}.
  - **코퍼스 altitude 위계**: ddd(프로젝트 전략) → db/api(측면 계약) → implementation-*(코드) → discipline-*(횡단 규율). test=메커니즘(구현측)·tdd=실천(규율측)이라 갈림.
- **파일트리 표준**(출처: 사용자 실프로젝트 HaffHaff, DDD 4계층): `application/<app>/{domain_layer,application_layer,infra_layer,presentation_layer}/`. `_layer` 접미사가 컨테이너 `application/`과 응용계층 이름충돌 해소. 단일 출처 = `discipline-houserules` final.md **§0 불변식**.
- **2부 코퍼스 동기화 규칙**: 스킬 지식은 배포본 `dddjango/skills/<s>/references/final.md` + 소스 미러 `workspace/reference/<s>/reference/final.md` 양쪽에 존재. **본문 byte-identical** 유지(소스엔 `## P1 Source Sufficiency` 헤더만 더 붙을 수 있음). houserules·agents·commands는 plugin-native라 미러 없음(단일 파일).
- **BC 배치는 G0에서 사람이 결정**(§2 DR-07): ① 새 독립 영역 / ② 기존 영역 포함 / ③ architect가 정함.
- **작업 방식(사용자 선호)**: 논의 우선·작은 단위. 큰 플랜 직행 거부. **코어 텍스트(agents/*.md·final.md) 변경은 구현 전 서브에이전트 리뷰**(skill-creator·plugin-creator·근본원인 렌즈) 필수.

---

## §2 Decision Records (status-tagged, evidence-anchored)

### DR-01 ✅ Claude 전용 재구축 + 단일 진입
Codex로 먼저 만들었으나 품질 낮아 Claude Code 전용 재구축. `/dddjango` 단일 커맨드 진입. Codex 호환은 P9 이월. 진짜 자산 = `workspace/reference/<skill>/reference/final.md`(소스 코퍼스). 2026-05-25 Codex 산출물·거버넌스 삭제, reference만 보존.

### DR-02 ✅ 소스 코퍼스 전수 감사·정화 (6 클러스터 A~F)
2026-05-25. 중복 소유권 제거: A(test↔tdd 재배치 `fc1d9ce`) · B(cleancode↔python `bb5b751`) · C+D(outbox 3층 + ddd de-SQLAlchemy `50559c3`) · E1(django→web 표현계층 이관 `c57e2da`) · E2(ninja 코드밀도 `defc54d`) · F(잔여 공백 `76aa30a`). 원칙=**한 주제 한 소유자**. dangling 0.

### DR-03 ✅ 빌드: 스킬 10 + 에이전트 7 + 커맨드
2026-05-26. SKILL.md(≤500줄 운영본문) + final.md 번들. 스킬 10/10·에이전트 7/7·커맨드 완성, `plugin validate --strict` 통과. 설계 스펙 `329748e`. 주요 커밋: 08ad561(커맨드)·910aab4(에이전트 5)·64ccad7(AGENTS.md 재작성).

### DR-04 ✅ 파일트리 표준 확정 (HaffHaff 기반)
2026-05-26~27, 커밋 `27dfacd`→`e2cb989`→`5925ce1`. 적응형 결정알고리즘 대신 **단일 표준 트리**로 전환. houserules를 소스 코퍼스 1급 시민으로 승격(`workspace/reference/discipline-houserules/reference/final.md` = 단일 출처). 명명=HaffHaff 원본, 테스트=의미군(`<app>/test/{unit,integration,e2e}/`), 적용=고정 기본값(기존 확립 규약은 존중).

### DR-05 ✅ 표준 강화: §0 불변식 · §4 명명 · ACL 레이어 · ninja
2026-05-27, 커밋 `6d7720d`(§0/§4/ACL) · `ad86443`(ninja) · `1f1ea7e`(design-architect §4 명명 + 정합성 MINOR 2건).
- **§0 불변식**: `application/` 컨테이너(단일 앱이어도)·4계층·개념1차/**종류2차 폴더 전체**(비어도 생성)·Django 앱은 `infra_layer/django_<app>/`(`startapp`·루트 `models.py` 금지)·ORM 클래스명 `<Name>Model`(도메인은 bare). YAGNI·"단일기능"으로 생략 금지.
- **§4 명명**: 추상=개념+역할접미사(`OrderRepository`·`ProductLockPort`), 구현=기술한정자 접두+base 일치(`DjangoProductLockPort`), `Interface`/`Impl` 금지, 파일명 약어 금지(`order_repository.py`).
- **ACL 분리**: 외부 컨텍스트 통합은 domain `<agg>/port/` + infra `acl/`, `repository/`에 안 섞음. 통합 없는 앱엔 미생성(조건부).

### DR-06 ✔ 코더 메커니즘-대체 가드레일 (smoke2 토끼굴 → smoke3 검증)
커밋 `f9ea088`. **문제(smoke2)**: 명세가 동시성 메커니즘을 정확히 박았는데(sqlite `select_for_update` no-op이니 두고 `CheckConstraint`로 방어, race→409) coder가 "sqlite도 진짜 락 필요"라 **자기 판단**해 명세에 없던 커스텀 `BEGIN IMMEDIATE` 백엔드를 33분간 자작 → 홀리스틱 감사가 잡아 제거(순수 손실, 164분 느린 런의 주범). **처방**: (A) `coder.md` — 명세가 정한 기술 메커니즘(락·동시성·격리·저장)은 architect 설계 결정, 임의 대체 금지·부족하면 설계 반송. (B) `implementation-django §16.4` — sqlite no-op·커스텀 백엔드 우회 금지·`CheckConstraint` 최종방어. **검증(smoke3)**: sqlite 데드락 마주치자 coder가 우회 안 만들고 설계 반송, 최장 슬라이스 5.7분(토끼굴 소멸). **한계**: LLM은 확률적 → 완화책이지 결정론적 차단 아님.

### DR-07 ✔ BC 경계 비결정성 수정 (smoke4 관측 → smoke5 검증)
커밋 `15ff62d`. **문제**: 같은 프롬프트인데 architect가 BC 배치를 런마다 다르게 정함 — smoke3=별도 `order` 앱(+ACL, 무거움), smoke4=`catalog` 내부(경량, 빠름 27~50분), 재현 불가. **수정**: G0에서 "이 기능 둘 자리"를 사용자에게 묻고 고정(①새 독립/②기존 포함/③architect) + 규칙4 가드(architect.md: ddd §3.3 규칙4["동일 DB 단순 케이스 복수 애그리거트 한 트랜잭션 용인"]는 *애그리거트 경계* 완화이지 BC 합병·ACL 생략 허가 아님). **검증(smoke5)**: §0에 배치 박힘, 규칙4 가드 준수, 동적검증 PASS. **주의**: smoke4가 가장 빨랐던 건 비결정이 *경량* 쪽에 떨어진 것 — 올바른 경계를 친 게 아니라 생략한 것(부채). 수정은 "가볍게"가 아니라 "결정론적+사람 선택".

### DR-08 ✅ extended thinking OFF = 비용 레버 (A/B: smoke5 vs smoke6)
동일 토이·프롬프트·G0, **thinking만 변수**. thinking 21→0블록, 코디 output cost −50%, 총 cost **2.62M→1.98M (−24%)**, 품질 완전 유지(테스트 35개). **사용자 세션 설정**이라 플러그인에 못 박음 — `/dddjango` 운영 시 thinking OFF 권장. 측정 정정: 추측 "thinking=output의 90%"는 틀림, 실측 ~55%.

### DR-09 ❌ 서브에이전트 모델 다운그레이드 = 역효과·금지 (A/B: smoke6 vs smoke7)
가설: architect만 Opus, 나머지(coder·리뷰어·테스터·discipline) Sonnet으로 wall↓. **결과: 시간·비용 둘 다 악화** — 기계시간 +14%, 과금비용 **1.98M→2.91M (+47%)**. 원인: 약한 coder가 게이트 첫 통과 실패로 반송 폭증(coder 2→6회·discipline 1→3회). 품질은 게이트가 끝까지 되돌려 유지됐지만 그게 곧 느리고 비싼 이유. **원복 완료. 특히 coder 다운그레이드 금지.**

### DR-10 ✅ 5 실행시간 레버 (이미 smoke6에 활성)
커밋 `fac248b`. (1)명세 다이어트 (2)architect 자기리뷰(초안 전 절간 모순 1회 스캔) (3)db 엔진 분기 지식(architecture-db: sqlite no-op·DEFERRED 데드락) (4)호출 병합(같은 파일군 슬라이스 묶음) (5)오케스트레이션 경량화(트래커·배너 게이트 한정·서브에이전트 산출물 "경로+3~5줄만"·전문 재출력 금지). **중요**: 커밋 시각(22:58)이 smoke6/7(15:41/17:17)보다 늦지만 **워킹트리·캐시엔 이미 있어 smoke6이 이걸 다 쓰고 돌았다**(forensic 확인: smoke6 design-spec이 §9.5 엔진지식 인용 + architect 서브에이전트 로그에 자기리뷰 시스템프롬프트 존재). → 커밋 타임스탬프로 "실행 시점 코드"를 추론하지 말 것.

### DR-11 ⏸ 공식문서 조사 — 새 저위험 레버 없음 / compaction 업스트림 차단
2026-05-28. Anthropic/OpenAI 공식문서 조사 결론:
- **wall ≠ cost**: 지연은 output 토큰이 지배, 입력 토큰 절감은 지연 1~5%만 개선(OpenAI Latency 가이드). 우리 토큰 88%(cache_read)는 *비용* 문제지 wall 문제 아님.
- **통제 가능 비용 레버는 이미 적용**(오케스트레이션 경량화 = DR-10).
- **compaction/tool-result clearing은 Claude Code가 자동 수행**(막힌 게 아님)이나 **세밀 설정 미노출** — GitHub anthropics/claude-code **#26215**는 메인테이너 거부가 아니라 봇 stale 자동종료. Opus 4.7 **[1M] 창**이라 ~95% 트리거에 한참 못 미쳐 91턴 누적이 통째 실림(cache_read 9.64M의 정체).
- **`/compact`는 모델·훅으로 자동화 불가**(Skill 도구 invokable 내장명령에서 명시 제외, PreCompact/PostCompact 훅은 관찰용). 수동만 가능, 실익 제한(cache_read 0.1x·wall 무영향).

### DR-12 ✅ Codex 이식 PoC 성공 (메커니즘 검증; 품질평가 미실시)
2026-05-28. DR-01에서 P9로 이월했던 **Codex 호환을 PoC로 재개·검증**. 조사 정본 = `workspace/design/2026-05-28-codex-port-research.md`.
- **사전조사 반전**: 현행 **Codex CLI 0.134.0**은 네이티브 서브에이전트(`spawn_agent`/`wait_agent`/`close_agent`, 피처 `multi_agent`=**stable·기본 true**)·Skills(SKILL.md)·Plugins(`.codex-plugin/plugin.json`)·`codex exec`·MCP를 **GA**로 제공. 과거 Codex 폐기(`911cd22`)는 *메커니즘 부재*(당시 `workflow-dddjango-subagents`가 "real subagent 미실행→sequential fallback" 자백) 탓이었고 **그 원인이 해소됨**. obra/**superpowers**가 동일한 멀티런타임 문제를 이미 풀어 패턴 차용(런타임별 매니페스트 공존·`Task→spawn_agent` 어댑터·Codex 플러그인은 skills/assets만 적재·스킬이 spawn으로 디스패치).
- **빌드**: `codex-dddjango/`(별도 디렉터리, **Claude `dddjango/` 무변경**). 코디네이터=`/dddjango` 진입 스킬, 7역할=스킬(코디가 `spawn_agent`로 띄우며 `dddjango-<role>` 역할스킬 인라인 로드 — 플러그인은 named agent 번들 불가), 지식11=스킬(코퍼스 Claude 배포본에서 복사·본문 일치). 매니페스트 `.codex-plugin/plugin.json`(v1.0.0) + 루트 `.agents/plugins/marketplace.json`(로컬 소스). **스킬 19개**.
- **어댑터**(superpowers `codex-tools.md` 근거): `Agent`→`spawn_agent`/`wait_agent`/`close_agent`, `AskUserQuestion`→**평문 게이트**(Codex 승인은 binary뿐), `TodoWrite`→`update_plan`, `Skill`→네이티브 로드. Codex 플러그인은 `commands/`·`hooks/` 미적재 → 커맨드는 스킬로.
- **설치(검증된 명령)**: `codex plugin marketplace add <레포루트>` + `codex plugin add dddjango@dddjango-local`. ⚠️ **캐시 함정**: 옛 0.1.10 스냅샷이 `~/.codex/plugins/cache/dddjango-local`에 잔존→`codex plugin remove dddjango@dddjango-local` + `rm -rf` 캐시 + marketplace 재등록 + 재설치. **`codex-dddjango/` 수정 때마다 재설치+Codex 세션 재시작** 필요.
- **PoC 검증**(`/Users/hyun/Desktop/dddjango-smoke` 재현 = Django 4.2.30 + `config` + `catalog.Product`; "재고 있을 때만 주문 생성·차감"): **3가정 전부 통과** — ⓐ `spawn_agent` 역할분리(규율감수가 테스트 오배치 지적→coder 반영 왕복 관측 = sequential 아님) ⓑ 평문 G0/G1/G2 ⓒ 설치·`multi_agent`. end-to-end **16 tests OK**·check OK·migrations 정합. **메커니즘만 검증 — 코드품질·결정성·Claude대비 평가는 다음 단계(반복 smoke).**
- **품질단계로 넘길 개선 과제 2**: (1) **평면 catalog**(`catalog/{models,services,exceptions}.py`, `application/` 4계층 아님) — §1 기존관례 vs §0 불변식 충돌, **§3-7 catalog 미정합과 동일·Claude·Codex 공통**(포트 버그 아님). (2) **coder 메커니즘-대체 가드레일이 Codex에서 약하게 작동** — sqlite 락 우회를 자작(반송했어야 = DR-06과 동일 실패축). 규율감수가 잔여권고로 표면화는 함.

### DR-13 ⏳ Codex 포트 코드품질 1:1 평가 (claude-1 > codex-2; N=1, 결정성 미확정)
2026-05-28. DR-12가 미룬 **코드품질 평가**를 통제 1:1로 실행. 산출 정본 = `workspace/eval/`(`comparison.html` 시각 보고 · `RESULTS.md` · `codex-2-analysis.md` · `claude-1-analysis.md` · `runs/{codex-2,claude-1}/` 산출물 보존 · `baseline/`+`reset.sh`+`PROTOCOL.md`+`RUBRIC.md`).
- **방법(통제)**: 같은 baseline(`Product(name,price,stock)`, Django 4.2.30) + 같은 프롬프트("재고 부족 409·충분 시 차감·주문 생성 **API**") + **같은 게이트 결정**(G0=기존 catalog / **순수 Django JsonResponse** / **Django 기본 test**). 프레임워크·러너 변수를 제거해 *같은 최소 스택 위 코드품질만* 비교. **Claude 비교군은 별 프로젝트**(`/Users/hyun/Desktop/dddjango-smoke-claude`, 별 venv)로 만들어 Codex 산출(`dddjango-smoke`)과 나란히 보존(리셋 아님). **산출물 정적 평가** + **서브에이전트 2종 독립 리뷰**(표준준수 감사 / 코드품질·DDD).
- **프롬프트 정정**: 정확한 Claude smoke 원문은 PoC가 쓴 "…기능"(도메인 전용, api off)이 아니라 **"…API"**(api lens 켜짐). 이 차이로 PoC(codex-1, 평면 catalog)와 달리 **codex-2는 완전한 §0 4계층을 생성** — 즉 DR-12의 개선과제(1) "평면 catalog"는 *프롬프트가 API였으면* 재현 안 됨. 단 PoC codex-1은 중간 재설치 이력 있어 참고용, 클린 비교는 codex-2.
- **결과(서브에이전트 합산 20항목)**: **claude-1 13 · codex-2 2 · 동등 5**. 표준준수 감사 6:1:3, 코드품질 7:1:2 — 두 에이전트 독립 실행이 같은 결론 수렴.
- **핵심 격차 = 구조 생성력 아님, 리뷰·감사 깊이**: ① **빈혈 도메인** — codex `Product.reserve()`가 프로덕션 미호출(죽은 코드), 규칙이 인프라 SQL에만 존재(자체 명세와 모순). claude는 DDD 리뷰가 [blocker]로 잡아 `Product.deduct()`를 흐름에 배선. ② **stock≥0 CHECK** — codex 누락(명세엔 있으나 미구현), claude 집행. ③ **race available_stock** — codex 처음부터 정확(DB 재조회), claude 1차 버그였으나 discipline-reviewer가 [important]로 잡아 수정. → **감사 방향 일관(claude가 더 깊음)**.
- **서브에이전트 신규 발견(codex)**: 포트가 `ABC` 아닌 **`Protocol`**, impl 파일명이 포트와 **충돌**(`product_repository.py` 양쪽), **`domain_service/event/specification` §0 종류폴더 누락**, 포트 **tuple 누수**, `_is_database_busy` **문자열매칭+복붙**, quantity 검증 **이중화**. claude 결함: 정상경로 2쿼리(경미).
- **codex 우위 2항목**: API Problem Details(`type` 안정 URI·415/422/503 분기), 예외 계층화(단 DB 문자열매칭 취약 동반).
- **결론**: 포트 메커니즘 충실도(DR-12)는 별개로 입증됨. **코드품질은 같은 스택에서 claude-1 > codex-2이며 원인은 감사/리뷰 깊이**(codex 감사가 빈혈·CHECK누락을 통과시킴). 단 **N=1** — 결정성 미확정.
- **미해소·다음**: codex 2~3회 반복으로 감사 격차 재현성 확인(빈혈·stock≥0을 매번 놓치는지). 재현 시 개선 과제 = **codex `discipline-reviewer`/`design-review-ddd` 스킬 본문 보강**(도메인 죽은 코드·설계-코드 제약 누락 포착) — **공통 코퍼스라 Claude·Codex 양쪽 반영**. 평가 하니스(`reset.sh`·`baseline/`·`PROTOCOL.md`)는 재사용 가능. → **DR-14에서 실행·결론 수정됨.**

### DR-14 🔁 결정성 2차 검증 — DR-13 결론 대폭 수정 (N=2; 격차는 대부분 분산)
2026-05-29. DR-13의 다음 과제(codex 반복)를 실행하되 **claude도 1회 더** 돌려 각 N=2. 산출 `workspace/eval/`(`comparison-2.html` · `codex-3-analysis.md` · `claude-2-analysis.md` · `gate-questions.md`(게이트 질문 1:1 원문) · `RESULTS.md` 결정성 섹션 · `RUBRIC-conformance.md` · `runs/{codex-3,claude-2}`). 깨끗한 새 프로젝트 `dddjango-codex`·`dddjango-claude`(Py3.9.6·Django4.2.30, baseline+venv+git).
- **⚠️ 2차 통제 이탈**: claude-2가 프레임워크/러너 게이트 미노출로 **Ninja+pytest**, 구조는 G1에서 옵션 B(최소변경) 선택으로 **평면**. codex-3=plain Django+Django test+완전 §0 4계층. → 구조·프레임워크·테스트수 **비교 불가**, 프레임워크 무관 신호만 유효. (옵션 B는 내 프로토콜 "최소 변경" 답이 유도 + houserules §0/§1.1 "기존 규약 존중" 예외가 명문 허용 — **claude 규칙 위반 아님, 선택 문제**. design-spec §5.1~5.2가 예외 인용. 단 claude-1은 §1.2 읽고 full tree 기본권장 ↔ claude-2는 §1.1 읽고 옵션B 권장 = 같은 표준 텍스트 정반대 해석=진짜 분산.)
- **세 신호 결정성**: B1 도메인 소유 = **비결정**(claude-1 `deduct()` 배선✓ ↔ claude-2 `deduct_stock()` 미배선·죽은코드✗·docstring "권위는 인프라"; codex 양차 미흡). stock≥0 = **비결정**(codex-2 누락 ↔ codex-3 명시 CHECK+마이그 음수행 가드+state-safe 리네임). race = 대등.
- **결론(DR-13 수정)**: **1차 "claude>codex 13:2:5"는 상당 부분 N=1 분산**이었음(비결정 신호가 우연히 모두 claude 정렬). 2차 프레임워크 무관 코드 **대등**(codex-3가 DB제약·`<Name>Model` 네이밍·오류처리폭 우위; claude-2가 포트 도메인타입 반환·409 available 우위; claude-2에 죽은 도메인코드 1건). **"런타임 결정적 감사 깊이 격차" 가설 약화** — codex-3 DB감사가 claude-2보다 날카로웠음. **재현되는 진짜 차이 = 코드 우열이 아니라 게이트 노출 철학(claude가 결정 ~3배 노출·근거/추천 동반)·기본 스택 취향(claude→Ninja/pytest, codex→plain)**(1·2차 모두 재현).
- **표준준수 점수(추정·신뢰낮음)**: 가중 루브릭 100점(`RUBRIC-conformance.md`) — codex-2/3=**64/76**(평균70·폭12), claude-1/2=**97/70**(평균84·폭27). claude 분산(27)>평균차(14)라 순위 단정 불가. 점수 변동의 거의 전부가 C2 도메인소유(20점) 한 축.
- **서브에이전트 검증 주의**: 코드품질 서브에이전트가 "claude-2 stock CHECK 거짓 테스트"라 단언 → **오판**(PositiveIntegerField가 SQLite에 `CHECK(stock>=0)` 자동생성; 스키마·테스트 4/4 PASS로 메인이 반증). **서브에이전트 강한 주장도 경험적 검증 후 채택**.
- **미해소·다음(측정 방법론)**: 진짜 성능차 측정엔 (a) 모든 게이트 답 고정(구조 옵션A·동일 프레임워크/러너로 교란 제거) (b) 런타임당 **N≥5~10**(분포 비교) (c) 기계검증 객관 루브릭 **블라인드 채점**(단 정적 grep만으론 오판—스키마/테스트 실행 필요) (d) 태스크 1개론 부족=형태 다른 여러 기능. **자동 채점 스크립트 단독은 병목(런 생성)을 못 풀어 효과 제한** — 루브릭 *정의*가 가치 80%. **DR-13의 "codex 스킬 보강" 과제는 재고**(결정적 격차 아님; 보강 시 양 런타임 ddd 리뷰가 'infra 집행=도메인 소유' 합리화를 일관 반려하도록, 공통 코퍼스라 Claude도 영향).

### DR-15 ✔ B1-fix 표준 검증 (codex-4 + claude-3 · 각 N=1 · 양쪽 B1 CLEAN)
2026-05-29. DR-14가 남긴 "B1 도메인소유가 양 런타임 비결정" 과제에 대응해, **B1을 일반 원칙 + 리뷰어 탐지로 구조화한 표준 편집(12파일, 미커밋)**을 새 통일 스모크 방식(§4 sample→clone)으로 동시 검증. 산출 `workspace/eval/`(`comparison-3.html` 시각보고 · `gate-questions-3.md` 게이트 1:1 원문+B1 판정 · `runs/{codex-4,claude-3}/` 산출물 보존).
- **편집 요지**: 판정·불변식 소유 원칙을 `architecture-ddd §3.2` **단일출처**로 승격(db §9.5는 동시성 *메커니즘*만 소유·ddd 인용) + **리뷰어 2층 탐지**(`design-review-ddd` 설계단계·`discipline-reviewer` 코드단계). `stock>=qty`는 "예:"로 강등해 일반화(잔액·좌석 등 모든 판정에 적용). 1·2차 과적합 지적 반영.
- **검증 전제**: 양 런타임 플러그인 캐시를 워킹트리와 **전체 트리 바이트 동일 동기화**(diff 0) + 라이브 프로브로 로드 확인 후 실행.
- **결과(각 N=1)**: **양 런타임 설계·코드 끝까지 B1 CLEAN.** codex-4 = 판정 `Order.create`(orders 도메인)·프로덕션 호출(`create_order_app.py:51`)·SQL 누수 0·version CAS·`stock>=0` 백스톱. claude-3 = 판정 `Product.deduct_stock`(catalog 소유자)·프로덕션 호출(`catalog_acl.py:30`→`place_order_app`, retry3)·누수 0. 둘 다 `§3.2`·`§9.5`·`§9.6` 인용. **DR-13 codex-2 빈혈(`reserve()` 죽은코드)·DR-14 claude-2 죽은코드(`deduct_stock` 미배선) 둘 다 부재.** 독립 검증(메인 직접): 16 OK / 43 OK(skip1)·check clean·oversell 0.
- **통제 이탈**: claude-3가 plain Django 아닌 **django-ninja** 사용(프레임워크 게이트 미노출 → 고정답 강제 불가, **DR-14 재현**). 사용자 "이대로 수락" 결정 → 프레임워크-의존 코드·테스트수(16 vs 43) 비교 무효, B1·판정소유·동시성철학·노출철학만 유효.
- **재현되는 차이**: 게이트 노출 **≈ 9:3**(클로드 G0 4분할+G1 4분할 / 코덱스 각 단일), 스택 취향(클로드 ninja / 코덱스 plain), 오류분류(클로드 503 분리). 1·2·3차 일관 = **코드 우열 아니라 제품철학·기본값**.
- **정직 경계**: 각 N=1 → "표준 발화·작동" sanity이지 B1 빈도 감소 통계 아님(N≥5 블라인드 필요). **표준 12파일 미커밋 — 검증 통과, 커밋 대기.**
- **방법론 교훈 2**: ① Claude 프레임워크 통제는 게이트 답이 아니라 **프롬프트 본문**에 박아야(Claude 미게이팅). ② 스모크 방식 **통일 = 마스터 `dddjango-smoke-sample` + git clone**(§4 정본; 구 reset.sh·E2E-SMOKE-METHOD.md 폐기).
- **발화 테스트(B2 메커니즘 검증, 추가)**: 편집된 `discipline-reviewer` 3회 독립 실행 = **2 clear + 1 fire**. 중립 B1-양성 픽스처 `workspace/design/b1-firetest/`(도메인 `Product.deduct` 죽은코드 + repo `filter(stock__gte=qty).update`)에 **[blocker] 판정 인프라 누수+죽은 도메인 메서드** 정확 발화(인용 `architecture-ddd §3.2`·`discipline-cleancode §15.1·§8.1/§8.5·§9.1`, 레인 준수="쿼리 정확성 아님"). codex-4·claude-3은 blocker 0·B1 명시 클린(별건 important만: codex quantity DRY 죽은분기, claude 테스트결합) = **B1 오탐 0이면서 다른 진짜 결함은 잡음(판별력)**. → **탐지 메커니즘이 설계(DR-15 본문)·코드 양 층에서 작동 확정.** 정직: 여전히 생성 N=1, 빈도통계 아님.

### DR-16 ✅ 표준 빈칸 ③·④ 메움 (BC 판정-소유 구조 규칙 + ninja 설계 승격·설치 규칙)
2026-05-29. DR-15 통제 비교(claude-3 vs codex-4)가 드러낸 **표준의 두 빈칸**(코드 버그 아님 — 표준이 결정을 안 내려 런타임마다 갈림)을 사용자 논의 후 메움. (DR-15 표준 12파일은 `98ebfd3`로 커밋 완료, 본 항목은 그 위 ③·④ 추가.)
- **③ 구조 배치 빈칸**: 스코프가 기존 평면 코드에 도메인 판정을 얹을 때 표준 4계층 트리로 이주할지 미규정. 실측: claude-3=평면 `catalog/Product.deduct_stock`에 판정 얹음·실행, codex-4=catalog는 순수 데이터·판정은 `Order`(orders) 소유 — 둘 다 B1 CLEAN이나 **BC 분할이 갈림**(=BC경계 비결정 [[dddjango-bc-boundary-nondeterminism]]). **결정**: 이주 기준을 *"레거시냐"가 아니라 "판정·불변식 소유냐"*로 명문화 — (1)소유→`domain_layer` 애그리거트 이주(평면 모델에 판정 메서드 금지), (2)단순 상류 데이터 소스(필드·CHECK만)→이주 불필요·ACL/포트 통합·평면 OK, (3)컨텍스트 간 접근은 ACL/`published_service`만(직접 import 금지). brownfield 기존 규약 §1.1 존중·판정 얹히는 코드에 한정.
- **④ 스택 전파 빈칸**: "greenfield 신규 API=Django Ninja 기본"이 coder 구현스킬에만 묻혀(design-architect 미로드) 설계 전파 안 됨 → codex-4 plain Django 이탈(DR-14·15 재현). **결정**: design-architect가 명세에 **"API 스택"을 1급 결정**으로 기록(기본 ninja, 기존 스택 존중) → 양 런타임 결정론적 수렴 + ninja 신규도입 시 requirements **버전 핀** 설치 규칙. architecture-api(계약 전용)·coordinator 불가침.
- **편집 14파일(미러 byte-identical)**: `architecture-ddd §3.2` 확장(소스+Claude+Codex 3벌) + `design-review-ddd`·`discipline-reviewer` 2층 탐지 보강(각 Claude .md+Codex SKILL 2벌) + `design-architect` ③배치·④API스택 불릿(2벌) + `implementation-django-ninja` final.md 설치규칙(3벌)+SKILL.md(2벌).
- **서브에이전트 리뷰 3렌즈**: plugin-creator=**양호**(미러·매니페스트·런타임 대칭 PASS) / 의도충실성=④충실·③ IMPORTANT 2건 **수정**(`discipline-houserules §2`→`references/final.md §2` 한정자 + 빈혈 적발 괄호를 앱루트 bare 모델까지 확장) / skill-creator=조건부(verbosity 지적 — dddjango "명시=결정성" 가치와 충돌, **현행 유지** 결정; ④ ref위임은 architect 미로드라 거부).
- **검증(정적)**: 미러 byte-identity·`claude plugin validate` PASS·인용 정합.
- **동적 검증 Tier 1 — 리뷰어 발화(2026-05-29)**: 편집된 `discipline-reviewer`(워킹트리 — 캐시는 ③ 미반영 stale 확인)를 중립 픽스처·실측 캡처 4건에 "rubric대로 감사"만 시켜(③ 미언급, 편향 방지) 발화 여부 관찰. **③ 판별 정확**: ⓥ `placement-firetest`(판정이 ORM `ProductModel`에 — 표준트리 존재)→**blocker 발화**(§3.2 "ORM≠도메인"→`domain_layer` 이주), ⓧ `crosscontext-firetest`(ordering이 catalog `domain_layer` 직접 import)→**blocker 발화**(`references/final.md` §2), codex-4(catalog 순수 데이터)→**무발화**("§3.2 case2 정상", 오탐0·보너스로 실측 FK cross-import는 important로 잡음), claude-3(실측)→§3.2↔§1.1 긴장을 **important로 표면화·설계결정 반송**(brownfield 과발화 방지; deduct_stock 프로덕션 호출돼 빈혈/죽은코드 아님 정확 구분). → **발화·무발화·모호처리 3모드 의도대로 작동.** 픽스처 `workspace/design/{placement,crosscontext}-firetest/`(중립·메타0). 각 N=1.
- **이연**: Tier 2(캐시 재설치 + design-architect가 명세에 ③ 이주·④ ninja 박는지) · Tier 3(양 런타임 수렴) · N≥5 빈도통계. → **Tier 2·3 + ④ 보강은 DR-17에서 실행·해소.**

### DR-17 ✅ 동적 검증 Tier 2·3 + ④ 보강 (Codex 스모크 ×3 — ④ 결과 수렴 달성)
2026-05-29. DR-16 ③·④ 편집의 동적 검증(Tier 2·3)을 실행하고, Tier 3가 드러낸 **④ 결과-수렴 실패**를 표준 보강으로 해소. 산출 `workspace/eval/runs/{codex-5,codex-6,codex-7}/`.
- **Tier 2 (Claude `design-architect` spec, 캐시 재설치본)**: ③ **STRONG PASS** — 평면 catalog를 `application/catalog/` 표준트리로 이주 + §1.1 vs §1.2 구분 명시("§1.1 존중=확립 규약이지 미조직 평면 답습 아님 → §1.2 적용") + 판정 도메인 `Product` 소유. ④ **inconclusive** — ninja 쓰나 Claude가 원래 ninja 편향이라 ④ 편집 효과 분리 불가 → 결정적 ④ 테스트는 Codex(원래 plain).
- **Tier 3 (Codex 전체 `/dddjango` headless `codex exec` · framework 미강제 · reserve-stock 스코프 · 평면 catalog fixture · 각 N=1)**:

  | 런 | 조건 | ④ 스택 | ④f requirements | ③ 구조 | tests |
  |---|---|---|---|---|---|
  | codex-5(t3) | pre-boost·no-net | plain | — | 평면(판정 ORM `catalog.models.Product.reserve`) ✗ | 12 OK |
  | codex-6(t3b) | pre-boost·ninja설치 | plain | — | `application/catalog/` 이주·판정 도메인 ✓ | 24 OK |
  | **codex-7(t3c)** | **POST-boost·ninja설치** | **Ninja ✓** | **`django-ninja==1.6.2` ✓** | **완전이주(판정 bare 도메인 + ORM→`infra_layer/django_catalog/ProductModel` db_table 보존 + `catalog/models.py` shim) ✓** | 22 OK |

  - **④ 실패 진단(t3·t3b)**: Codex가 *"adding Django Ninja requires installation not guaranteed in this environment"*로 plain 다운그레이드 — **headless 무설치 보수성**. 단 **④(e) 전파는 확정**: 양 런 모두 "API Stack Decision"을 1급 기록 + *"overrides the dddjango default of Django Ninja"* 명시(codex-4 무자각 plain과 대비). ninja 사전설치해도 architect가 `requirements.txt`만 보고 venv 미확인 → 핑계 유지.
  - **③**: codex가 표준대로 **완전 이주 가능**(t3b·t3c) + Tier 2(Claude)와 수렴. 단 **비결정**(t3 평면 "승인된 설계 예외") — BC경계 런변동 [[dddjango-bc-boundary-nondeterminism]]. t3c는 `db_table="catalog_product"` 보존 + 마이그레이션 이주로 t3가 핑계삼은 *"테이블 연속성 ≠ 코드 이주 불가"*를 정면 입증.
- **④ 보강 (`design-architect` 2미러 byte-identical)**: t3·t3b 실패 추론("requirements에 없음 → 설치 불가 → plain")을 직격 — "신규라 의존성 없다는 사실만으로 plain 안 낮춤 / 채택=매니페스트 버전핀(`implementation-django-ninja` §2.1)이지 라이브 설치 아님 / 확보 불가가 *구체 근거로 확인*된 때만 명세 기록 후 예외". **서브에이전트 리뷰 3건 반영**(출처 §2.1-only 정확화[houserules §6는 "(보류)"라 인용 회피] · escape hatch "막연한 우려 아닌 구체근거+명세기록"으로 루프홀 차단 · 2문장 분리). **효과=결정적**: pre-boost 2런 plain → **post-boost(t3c) Ninja+핀+Ninja Router**, 22 tests green.
- **결론**: ③ = 표준 작동(Codex 완전이주 가능·Claude 수렴) **단 비결정**. ④(e) 전파 = **확정**. **④ 결과 수렴 = 보강으로 달성**(headless에서도 Ninja+핀; (f/g) 설치규칙 t3c 발동). 인터랙티브 ④ 런은 보강이 *더 어려운* headless를 통과해 **선택사항(미실행)**.
- **정직 경계**: 각 N=1(sanity, 빈도 아님). ③ 비결정 미해소(N≥5 별도). 보강은 `design-architect`에만(coder는 §2.1 기보유).

---

## §3 DO-NOT-RETRY (검증된 실패·헛다리 — 미래 에이전트는 반복 금지)

1. **서브에이전트 모델 다운그레이드**(특히 coder→Sonnet) — 게이트 반송 폭증으로 net 느리고 비쌈(DR-09).
2. **코더가 architect의 기술 메커니즘 대체** — 커스텀 락 백엔드 자작 등 33분 토끼굴(DR-06).
3. **"오케스트레이션 서술 줄여 비용절감"** — 헛다리. 서술은 비용 ~4%. 비용 1위는 코디 output(×5 가중)이고 cache_read는 0.1x(싸다).
4. **커밋 타임스탬프로 "그 smoke가 쓴 코드" 추론** — 워킹트리/캐시는 커밋보다 앞설 수 있음. 세션 로그·design-spec·서브에이전트 시스템프롬프트로 검증하라(DR-10).
5. **machine-time = wall − (user행으로 끝나는 큰 갭)** = 버그. 서브에이전트 반환은 `attachment` 행으로 끝나 오분류됨. **올바른 정의**: `machine = wall − Σ(서브에이전트 실행구간에 안 걸치는 >120s 갭)`(§4).
6. **BC 배치를 사람 선택 제거로 "결정론화"** — 아님. G0에서 선택지를 *표면화*하는 게 정답(DR-07).
7. **catalog 같은 기존 startapp 앱을 표준 트리로 강제 이주** — 스코프 초과·기존 소비자 위협. 결정 = 조치 없음(A), 표준 변경 없음(2026-05-27).

---

## §4 Methodology & Tools

- **telemetry 파서**: `workspace/tools/session_telemetry.py` — 세션 jsonl에서 서브에이전트 시간/토큰 + 코디 토큰을 raw vs cost로 분해. `--smoke 3 4 5`.
- **리포트 생성기**: `workspace/tools/smoke_report.py` → `smoke_timeline.html`(전 smoke 비교표 + smoke별 단계 타임라인).
- **주의사항**:
  - 서브에이전트 디스패치 도구명 = **`Agent`**(Task 아님).
  - 병렬 판정 = 같은 턴이 아니라 **실행구간 겹침**(설계 리뷰 3종은 이미 병렬 — 레버 아님).
  - cost 가중(입력1 기준): cache_read 0.1 · cache_creation 1.25 · input 1.0 · output 5.0.
  - **machine-time 정의**(사람 대기 제외): `wall − Σ(서브에이전트 실행구간에 안 걸치는 >120s 갭)`. 항상 machine ≤ wall.
  - 서브에이전트 내부 턴은 별도 파일 `<session>/subagents/agent-<id>.jsonl`(`message.model` 포함).
### 스모크 테스트 방식 (정본 — 2026-05-29 통일, 이전 방식 전부 폐기)

표준(스킬/에이전트)을 바꾼 뒤 "**실제 파이프라인이 결함 없는 동작 코드를 만드는가**"를 end-to-end 검증하거나 런타임을 1:1 비교하는 **단일 절차**. (과거 `git clone 토이` 레시피·`reset.sh 인플레이스 리셋`·`E2E-SMOKE-METHOD.md`는 이걸로 대체됨.)

**핵심: 마스터 1개 + 복제 N개.** 데스크탑에 마스터 템플릿 `~/Desktop/dddjango-smoke-sample` 하나만 두고(여기서 직접 런 안 함), `git clone` 으로 런타임별 타깃을 뜬다 → 추적 코드 **바이트 동일**(검증: 세 폴더 `git ls-files | xargs shasum` 동일 해시), venv·DB·시드는 핀(`requirements.txt`)+`setup.sh`로 **결정적 동일** ⇒ 두 런이 같은 시작점에서 출발.

- `~/Desktop/dddjango-claude-index` = Claude `/dddjango` 타깃 · `~/Desktop/dddjango-codex-index` = Codex `dddjango` 스킬 타깃. (회차 구분 필요하면 접미사만 바꿈.)

**마스터 구성**(= baseline + 고정입력 + 셋업):
```
config/ catalog/(Product만) manage.py     # = workspace/eval/baseline/
requirements.txt   # Django==4.2.30
PROMPT.md          # 고정 기능 프롬프트 + 고정 게이트 답 + 시드 정의(아래)
setup.sh           # venv 생성 + 의존성 + migrate + 시드 + check (멱등)
.gitignore         # .venv/ db.sqlite3 __pycache__/ .dddjango/
```
**생성·복제(분실 시 재현)**:
```bash
S=~/Desktop/dddjango-smoke-sample
cp -R workspace/eval/baseline/{config,catalog} workspace/eval/baseline/manage.py "$S"/   # + PROMPT/setup/requirements/.gitignore
(cd "$S" && git init -q && git add -A && git commit -qm baseline && bash setup.sh)        # 마스터 = 실행가능
git clone "$S" ~/Desktop/dddjango-claude-index && bash ~/Desktop/dddjango-claude-index/setup.sh
git clone "$S" ~/Desktop/dddjango-codex-index  && bash ~/Desktop/dddjango-codex-index/setup.sh
# 리셋 = 폴더 삭제 후 재클론(인플레이스 reset.sh 아님).
```

**고정 입력**(마스터 `PROMPT.md` — 양 런타임 동일하게 답해야 차이가 "런타임 차이"로 읽힘; DR-14 교훈: 프레임워크·러너·구조옵션 미고정 시 비교 불가):
- 프롬프트(토씨 그대로): `재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.`
- 고정 게이트: BC=**① 새 독립 영역**(완전 §0 4계층·평면 교란 제거) · lens=**ddd+db+api** · 스코프=제안대로 · **plain Django** · **Django 기본 test** · G1/G2 무수정 승인 · **thinking OFF**(DR-08).
- 시드(테스트 DB 비오염 위해 마이그레이션 아닌 런타임 데이터로 db.sqlite3에만): Widget stock=10·price=1000, Gadget stock=3·price=2000.

**⚠️ 플러그인 캐시 신선도(표준 편집 시 필수)**: 서브에이전트는 **설치된 플러그인 캐시**에서 스킬/에이전트를 로드(워킹트리 아님). `/reload-plugins`는 캐시를 **재복사하지 않음**(기존 캐시 재독). 반영 = 편집 파일을 캐시에 직접 `cp`(Claude `~/.claude/plugins/cache/changja88/dddjango/<ver>/` · Codex `~/.codex/plugins/cache/dddjango-local/dddjango/<ver>/`) 또는 uninstall→install. 풀런 전 `grep -c "<신문구>" <캐시>/…/final.md`(=1) + 프로브 서브에이전트 1개로 검증. 보조: `~/.claude/plugins/installed_plugins.json` `gitCommitSha`가 의도 HEAD인지.

**합격 기준**:
- (A) `manage.py check` clean · migrate 정합 · `test` 전부 green(201·409·404·**동시성 oversell 없음** 커버).
- (B) 역사적 결함 부재(grep+리뷰): **B1(빈혈/판정 인프라 누수)** — `grep -rn "stock__gte\|balance__gte" application --include=*.py | grep -v test | grep -v "stock__gte=0"` =0, 도메인 판정 메서드(`.deduct(` 등)가 **프로덕션 호출처** 보유, repo CAS의 `WHERE`엔 version 경합가드만(판정 SQL 없음; `stock>=0`은 CHECK 불변식 백스톱이라 OK). **§0 파일트리·§4 명명**. (권장) `discipline-reviewer` 서브에이전트 홀리스틱 감사 blocker/important 0.

**캡처·기록**: 산출물 → `workspace/eval/runs/<run>/`(rsync, `.venv/.git/db.sqlite3/__pycache__` 제외) · 한 줄 → §5 Ledger · 분석 `workspace/tools/session_telemetry.py --smoke N` → `smoke_report.py`. 게이트 질문 1:1 원문은 비교 시 `workspace/eval/gate-questions*.md`에 양쪽 기록.

**정직 경계**: 1회 = 통합 sanity("만들 수 있다"+"게이트 작동"). 확률적 결함(B1·BC비결정)의 *빈도 감소* 증명은 같은 입력 **N≥5 블라인드** + 루브릭(`workspace/eval/RUBRIC*.md`) 필요(별도 작업). 커밋 타임스탬프로 "그 런이 쓴 코드" 추론 금지(DR-10).

> 레거시: `workspace/eval/reset.sh`·구 `~/Desktop/dddjango-smoke*` 타깃은 §5의 **과거 런(smoke1~8·codex/claude 1~4)** 재현용 흔적이다. **새 런은 위 sample→clone 절차만 사용**한다.

---

## §5 Smoke Run Ledger

machine = 사람 대기 제외 기계시간(§4 정의). cost = 코디 과금 가중단위(M). 상세·단계 타임라인은 `workspace/tools/smoke_timeline.html`.

| smoke | 세션 | machine/wall(m) | 코디 raw/cost(M) | 개선·검증한 가설 | 결과 |
|---|---|---|---|---|---|
| 1a | smoke/a4ef25ae | 47/78 | 12.1/2.71 | 최초 풀 파이프라인 + ninja(JSON·415) 어댑터 | 베이스라인 |
| 1b | smoke/655f2453 | 50/82 | 16.0/3.55 | 주문 베이스라인 | 안정 |
| 1c | smoke/7e71310d | 50/82 | 9.1/2.76 | 주문 베이스라인(G2 정정 패턴 첫 관측) | 안정 |
| 2 | smoke/d3eb9734 | 114/164 | 18.9/5.60 | coder 메커니즘 토끼굴 노출(33분) | 🔴 느린 런(DR-06 동기) |
| 3 | smoke3/a0d03aed | 85/88 | 10.7/3.35 | coder 가드레일 + 표준강화 검증 | 🟢 PASS |
| 4 | smoke4/4cc77948 | 50/50 | 8.1/2.39 | BC 비결정성 노출(catalog 내부 경량) | DR-07 동기 |
| 5 | smoke5/5494f4d0 | 60/60 | 8.1/2.62 | BC 고정 + 규칙4 가드 검증 | 🟢 PASS(`15ff62d`) |
| 6 | smoke6/17a0b9b6 | 52/79 | 8.0/**1.98** | thinking OFF A/B | 🟢 **베스트(−24%)** |
| 7 | smoke7/1a5c44a8 | 60/629 | 9.0/2.91 | 모델 다운그레이드 A/B | 🔴 역효과(+47%, 원복) |
| 8 | smoke8/25fd3ae4 | 41/41 | 7.2/**1.58** | 커밋 HEAD 최종 확인(thinking off) | 🟢 **합격·회귀0**(cost 최저) |

**smoke8 합격 결과**(2026-05-28): 테스트 **20/20 OK**(201·409·404·422·동시성 전부 커버) · 별도 BC `orders`+ACL(port/+acl/, catalog import는 ACL에만) · §0 불변식 전부(application/ 컨테이너·4계층·빈 종류폴더·`infra_layer/django_orders`·`OrderModel`) · §4 명명(`ProductStockPort`←`DjangoProductStockAcl`·`OrderRepository`) · **coder 토끼굴 0**(최장 6.5분) · **architect 정정 재디스패치 0**(2회) · 프로덕션 시그니처 타입. 역사적 결함(루트 models.py·ORM 오명명·ACL 혼입·토끼굴·BC 비결정) **전부 부재**. → 최적화 사이클 종료.

---

## §6 Pointers

- **핵심 커밋**(feat/dddjango-build): `5925ce1`(파일트리 표준) · `6d7720d`/`ad86443`/`1f1ea7e`(표준 강화) · `f9ea088`(coder 가드레일) · `fac248b`(5 레버) · `15ff62d`(BC 수정, HEAD).
- **설계·로그 문서**: `workspace/design/` (파이프라인 설계·커맨드 설계·필트리 초안·스모크 피드백 로그들).
- **도구·리포트**: `workspace/tools/{session_telemetry.py, smoke_report.py, smoke_timeline.html}`.
- **AGENTS.md**: Claude 전용 파이프라인 구조 설명.
- **Codex 이식**(§2 DR-12): 조사 `workspace/design/2026-05-28-codex-port-research.md` · 빌드 `codex-dddjango/`(스킬 19) · 로컬 마켓플레이스 `.agents/plugins/marketplace.json` · 테스트 픽스처 `/Users/hyun/Desktop/dddjango-smoke`(git 아님, =codex-2 런).
- **코드품질 1:1 평가**(§2 DR-13): 정본 `workspace/eval/` — `comparison.html`(1차 시각 보고) · `RESULTS.md` · `codex-2-analysis.md` · `claude-1-analysis.md` · `runs/{codex-1,codex-2,claude-1}/`(산출물 보존) · 하니스 `baseline/`+`reset.sh`+`PROTOCOL.md`+`RUBRIC.md`. Claude 비교군 `/Users/hyun/Desktop/dddjango-smoke-claude`(git 아님). 1차 결과 claude-1>codex-2(13:2:5), N=1.
- **결정성 2차 검증**(§2 DR-14, 결론 수정): `workspace/eval/` — `comparison-2.html`(2차 시각 보고) · `codex-3-analysis.md` · `claude-2-analysis.md` · `gate-questions.md`(게이트 질문 1:1) · `RUBRIC-conformance.md`(100점 루브릭+점수) · `RESULTS.md`(결정성 N=2 섹션) · `runs/{codex-3,claude-2}/`. 2차 깨끗한 프로젝트 `/Users/hyun/Desktop/dddjango-{codex,claude}`(Py3.9.6·Django4.2.30). 결과: 1차 우위는 대부분 분산, 코드 대등, 진짜 차이=게이트 철학·스택. 점수 codex~70/claude~84(신뢰낮음). **2차 통제 이탈**(claude-2=Ninja+pytest+옵션B평면, codex-3=plain+§0).
- **B1-fix 검증 3차**(§2 DR-15): `workspace/eval/` — `comparison-3.html`(3차 시각보고) · `gate-questions-3.md`(게이트 1:1 + B1 판정) · `runs/{codex-4,claude-3}/`. 타깃 `~/Desktop/dddjango-{codex,claude}-index`(`dddjango-smoke-sample`에서 git clone·바이트 동일). 결과: **양쪽 B1 CLEAN(설계·코드, 각 N=1)**, 게이트 노출 9:3, claude-3 ninja 통제이탈(수락). 표준 12파일 커밋(`98ebfd3`).
- **표준 빈칸 ③·④ 메움**(§2 DR-16): 14파일 편집 — `architecture-ddd §3.2` 확장(3벌)·`design-review-ddd`/`discipline-reviewer` 2층 탐지(각 2벌)·`design-architect` ③배치+④API스택(2벌)·`implementation-django-ninja` final.md 설치규칙(3벌)+SKILL(2벌). 정적 검증·`plugin validate` 통과, 동적 ⑥ 이연.
- **동적 검증 Tier 2·3 + ④ 보강**(§2 DR-17): Tier 2 = Claude `design-architect` spec(③ migrate + §1.1/§1.2 명시·④ inconclusive). Tier 3 = Codex 전체 스모크 ×3 `workspace/eval/runs/{codex-5(t3·평면·plain), codex-6(t3b·이주·plain), codex-7(t3c·POST-boost·Ninja+핀)}`. 보강 = `design-architect` 2미러(headless의 "설치 불확실→plain" 직격 → t3c Ninja 수렴). fixture `~/Desktop/dddjango-codex-{t3,t3b,t3c}`(git 아님)·인터랙티브 미실행 fixture `~/Desktop/dddjango-codex-interactive`. 각 N=1.
- **향후(범위 밖)**: `/dddjango init`(uv + ruff·mypy strict·django-stubs·pydantic·pytest 부트스트랩, django-stubs만 코퍼스 공백) · OHS→Published Language DTO 전환 · Codex 품질평가·전체 smoke 루프.
- **개인 메모리 슬러그**(세션 회상용, 정본 아님): dddjango-rebuild-direction · dddjango-work-style · dddjango-audit-ledger · dddjango-standard-hardening-verification · dddjango-bc-boundary-nondeterminism · dddjango-cost-token-optimization. → **내용은 이 DEVLOG에 흡수됨**.
