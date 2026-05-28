<!--
AI-OPTIMIZED DEVLOG. 이 문서는 dddjango 작업의 자기완결 정본이다.
읽는 규칙(AI):
  1) §0 Current State를 먼저 읽어라(지금 상태·베스트 구성·금지사항).
  2) 결정은 §2 Decision Records에서 상태태그(✅adopted/❌rejected/⏸blocked/✔verified)로 찾아라.
  3) 모든 수치·주장엔 증거 앵커(세션ID·커밋SHA·파일:라인)가 붙는다 — 추천 전 실재 확인하라.
  4) 개인 메모리(~/.claude)는 초기화될 수 있어 신뢰 못 함. 이 문서가 정본이다.
마지막 갱신: 2026-05-28
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
- **smoke A/B 재현 레시피**:
  1. baseline 클론: `git clone <기존토이> <새토이>` (커밋 `0a9c2f5` = pristine Django 4.2.30 + ninja 1.6.2 + flat catalog Product; 생성물은 untracked라 안 따라옴).
  2. venv + `pip install django==4.2.30 django-ninja==1.6.2`, `manage.py migrate`, 시드(위젯 stock 10·가젯 stock 3).
  3. 프롬프트 = 현재 `dddjango/commands/dddjango.md`(frontmatter 제거, `$ARGUMENTS`→기능)로 `SMOKE_PROMPT.txt` 생성. 붙여넣기 방식(코디) + 서브에이전트는 플러그인 캐시 로드.
  4. **플러그인 캐시 최신 확인**: `~/.claude/plugins/installed_plugins.json`의 `gitCommitSha`가 현재 HEAD인지. 다르면 marketplace update→uninstall→install(버전 불변이라 update는 no-op).
  5. **thinking OFF**, G0 답변 고정(비교용: ①새 독립 영역 / 단일 상품+수량 / lens ddd·api·db).
  6. 끝나면 telemetry 파서로 분석.

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
- **향후(범위 밖)**: `/dddjango init`(uv + ruff·mypy strict·django-stubs·pydantic·pytest 부트스트랩, django-stubs만 코퍼스 공백) · OHS→Published Language DTO 전환 · Codex 품질평가·전체 smoke 루프.
- **개인 메모리 슬러그**(세션 회상용, 정본 아님): dddjango-rebuild-direction · dddjango-work-style · dddjango-audit-ledger · dddjango-standard-hardening-verification · dddjango-bc-boundary-nondeterminism · dddjango-cost-token-optimization. → **내용은 이 DEVLOG에 흡수됨**.
