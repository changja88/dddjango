# T3 이관 검수표 — architecture-api-skill

- 원문: `dddjango/skills/architecture-api/SKILL.md` (51행 · 센서스 일치 · 마커 0 — 미이관 문서)
- spec: `workspace/eval/t3/specs/architecture-api-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/architecture-api-skill.spec.json` → **exit 0** (블록 36 · Work 29 · `--write` 미사용 · 수리 루프 0회)
- 배선 준거: `check-*.py` **27종 docstring 선두 전수 실독**(§16 L-F 의무 · arch-skills 묶음 1회) 후 저작. 요약-복제 상대인 `architecture-api-final` 기이관 spec 의 정본 배선을 대조했다. **정본과 갈린 배선 0** — 24행은 F2 수리로 정본 s022-5.2/b1 배선을 승계했다.
- W3 적대 리뷰 수리 반영(2026-08-22): F2(24행 정본 배선 승계 + basis 준거 정정) · F6(분해 규율 우선순위 명문화) · F7(23행 W7·W8 채번 순서 교환) · F8(대사 사유 분리 서술) — 상세는 `workspace/eval/t3/reviews/w3-arch-skills-findings.md` «처분» 절.

## 1. census 대사 (절별 규범 수)

| 절 | 헤딩 | 발주서(센서스) | spec | 차 | 판정·사유 |
|---|---|---|---|---|---|
| s001 | (전문) | 2 | 2 | 0 | 일치 — `description` 2문(로드 조건 / 경계 위임 4종). 표기 혼재(«dddjango:architecture-ddd» 콜론 접두)는 문면 그대로 담았다 |
| s003 | 언제 쓰나 | 6 | 6 | 0 | 일치 — 로드 조건 1 + 위임 경계 불릿 5 |
| s004 | 핵심 운영 원칙 | 10 | 19 | **+9** | **⑴ 불릿 단위 센서스의 미해상(과소) + ⑵ 규약 내 하위 문장(독립 종결절) 분해** — 두 사유를 분리해 적는다. ⑴ 센서스는 8 불릿에 10을 배분했다(불릿 해상도 — 불릿 내부 재계수 없음). ⑵ 그 위에 spec 은 «독립 종결절» 규율로 **23행(에러 프로필)에서 9 Work** 를 냈다(한 불릿 → 9): 보존 / code-json 선택 / shape 승인 / RFC 조건부(Exception) / wire 혼합 금지(Prohibition) / 주어 한정(Prohibition) / 표준 controller 레시피 / preserve 관할 배제(Exception) / G1 표면화(STOP) — 채번 순 = 절 시작 등장 순(F7 수리 반영). 이 아홉은 `architecture-api-final` s024-5.4/b1~b6 의 Work 분해와 **1:1** 이다. 그 밖에 **22행 2(설계 규칙 ↔ 동사 금지 — 한 문장 → 2 · ⑵ class 상이 · 배타 표지 없음 → 아래 우선순위 규율)** · 24행 2(계약 기록 ↔ 체크리스트 검토) · 26행 2(문면이 §10·§11 을 명시 귀속). 21·25·27·28행은 1:1. **spec 이 옳다** |
| s005 | 상세 레퍼런스 | 2 | 2 | 0 | 일치 — 32행 라우팅 준거 1 + 51행 한정 독해 1. 표 16행(머리·구분 포함)은 매핑이라 미계수(P0 승계) |
| **계** | | **20** | **29** | **+9** | 불일치 1절 — 사유는 ⑴ 불릿 해상도 과소 + ⑵ 규약 내 하위 문장 분해의 합산 · 과대 산정 판정 0 |

**병합 단계 승계 요청(F8)** — «독립 종결절» 규율은 §13 «Work 채번 단위 = 문장»의 저작자 확장이다(한 문장 → 복수 Work: 이 문서 23행 9 · ddd 21·26행 각 4). 정본 final 분해와 1:1로 맞물려 방어되나 동결 센서스(REF 539절·3,235문장) 분모 대비 무비준 확산 시 기대표 드리프트가 누적된다. 병합 단계에서 ⓐ 규율의 T3 공통 비준(§13 부기 또는 `T3-EXECUTION.md` 기록) ⓑ 기대표 diff 사유에 **arch-skills 3문서 +23(ddd +9 · db +5 · api +9)** 내역 승계를 할 것. 저작 계약 «금지» 조항상 이 에이전트는 `ontology-authoring.md`·`T3-EXECUTION.md` 를 쓰지 않는다.

**문장 분해 규율(이 묶음 3문서 공통)** — 단위는 **독립 종결절**이고, ⑴행위 대상 상이 ⑵class 상이 ⑶문면이 서로 다른 §·규칙 번호를 명시 귀속 ⑷문면이 스스로 규칙 수를 선언 중 하나면 한 문장 안이라도 분리 채번했다. 반대로 같은 축의 **부정면 재진술**·**근거/결과 서술**·**열거 조각**·**같은 결정 대상의 기록 의무**는 병합했다.

**트리거 충돌의 우선순위(F6 수리 — 3문서 공통 명문화)** — ⑵(class 갈림 → 분리)와 «부정면 재진술»(→ 병합)이 한 문장에 동시에 걸릴 때는 **긍정절의 배타 표지(«만»·«한정»·«…뿐») 유무**로 가른다.

- 배타 표지가 **있으면 병합** — 부정절의 금지 대상이 «만»에 이미 배제돼 독자 위반 표면이 없다. 실물: ddd 24행 «흐름 제어와 트랜잭션 관리**만** 담당하고, 비즈니스 로직을 두지 않는다» → 1 Work.
- 배타 표지가 **없으면 ⑵ 우선 분리** — 부정절이 독자 금지 대상·독자 위반 표면을 갖는다. 실물: 이 문서 **22행** «URL은 명사·복수형·케밥케이스 리소스로 설계하고 동사 행위를 URL에 포함하지 않는다» → 배타 표지 0이고 `/orders/{id}/cancel` 처럼 세 형식 속성을 모두 지키면서 동사를 포함하는 URL 이 성립하므로 **2 Work**.
- 인용 판례와의 정합 — 정본 `architecture-api-final` s013-3.1/b2 는 «명사 사용 (동사 아님)»을 1 Work 로 접었으나 그것은 **좋은 예/나쁜 예 대조 표의 한 행**이고 괄호는 그 대조의 주석이다(독립 종결절 0). SKILL 22행은 «…포함하지 않는다»라는 독립 종결절이라 판형이 다르다 — 판례 이탈이 아니라 문면 형태 차이다. 따라서 22행 2 Work ↔ 정본 b2 1 Work 는 **1:다가 아니라 다:1 부분 재진술**이고 §3.2 유예 #1·#2 가 그대로 진다.

이 문서에서 병합한 자리 3건(과대 방지 실증): ⑴ 21행 콜론 뒤 «PUT 전체 교체 / PATCH 부분 수정 / POST non-idempotent» = 같은 축(메서드 의미론)의 구체화 조각 → 1 Work. ⑵ 25행 «선택하고 선택 기준을 명시한다» = 같은 결정 대상의 기록 의무 → 1 Work. ⑶ 28행 대시 뒤 «path·method·schema·… 빠짐없이 기술한다» = 같은 행위(OpenAPI 반영)의 구체화 → 1 Work. 또 23행의 «플러그인 기본 property 목록은 없으며» 는 **사실 전제**(플러그인이 목록을 주지 않는다)라 규범으로 세지 않고, 뒤따르는 «shape 변경은 별도 사용자 승인이 필요하다» 하나만 채번했다.

## 2. 배선 근거 표 (전 규범 29건)

> `enforcedBy` 는 «담당 검사기의 문면·docstring 근거가 실재하는가»로만 달았고, 없으면 §16 위임 기본값 표를 따랐다(기본값 이탈·기본값 도피 양쪽 다 근거 병기). 근거 기호 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N.
>
> **표는 spec JSON 에서 기계 생성한다**(전 열이 spec 실물의 사본 — agent-coder 검수표 R2-3 재발 방지 조치 승계). spec 을 고치면 이 표를 다시 생성한다.

| # | 절/블록(행) | Work label | class | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b2 (3) | 로드 조건 — REST/HTTP 계약(엔드포인트·상태 코드·에러 프로필·버전/하위 호환성·OpenAPI)의 신규 정의·변경 시 선행 로드 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 «…새로 정의하거나 변경할 때 먼저 로드한다» + 센서스 E08 s001 비고 «frontmatter = 라우터 트리거(애매→포함)» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드·라우팅 술어 0 · §16 위임 기본값 표(architecture-api→agent-design-review-api) + 스킬 배분 소유 Coordinator 병기(agent-coder s004 선례) |
| 2 | s001/b2 (3) | 경계 위임 — JSON 직렬화·라우터, 서버렌더 표현계층, 도메인 모델·애그리거트, 데이터 신뢰성·트랜잭션의 타 스킬 이양 | Obligation | — | `agent-discipline-reviewer`·`agent-design-review-ddd`·`agent-design-review-db` | ①문면이 implementation-django-ninja·implementation-django-web·architecture-ddd·architecture-db 를 수임처로 직접 지목 — §16 표의 수임 문서군 기본값 병기(implementation-*→discipline-reviewer · architecture-ddd→design-review-ddd · architecture-db→design-review-db) · ②27종 docstring 에 스킬 간 위임 술어 0 · ninja s022-6.1 판례 준거 |
| 3 | s003/b1 (10–12) | 로드 조건 — REST API 계약 결정·변경 시 로드 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 «…결정하거나 변경할 때 로드한다» — s001 description 의 정본 진술(사본 = s001/b2) · ②27종 전수 — 스킬 로드 술어 0 · §16 기본값 + 스킬 배분 Coordinator 병기(s001/b2 와 동일 처분) |
| 4 | s003/b2 (13) | JSON 직렬화·Router·Schema 구현의 implementation-django-ninja 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면이 화살표로 수임처를 직접 지목 · §16 표 implementation-*→agent-discipline-reviewer(기본값 일치) · ②27종 전수 — 스킬 관할 배분 술어 0(오류 계약 4종은 profile·selector 계약 축이지 스킬 경계 축이 아니다) |
| 5 | s003/b3 (14) | 서버렌더 표현계층(템플릿·폼·HTMX)의 implementation-django-web 위임 | Obligation | — | `agent-discipline-reviewer` | 동상 — ①문면 지목 · §16 표 implementation-*→discipline-reviewer |
| 6 | s003/b4 (15) | 도메인 전략·애그리거트·경계 설계의 architecture-ddd 위임 | Obligation | — | `agent-design-review-ddd` | ①문면이 architecture-ddd 를 수임처로 직접 지목 · §16 표 architecture-ddd→agent-design-review-ddd(설계 시점) |
| 7 | s003/b5 (16) | 데이터 신뢰성·트랜잭션·outbox 전달의 architecture-db 위임 | Obligation | — | `agent-design-review-db` | ①문면이 architecture-db 를 수임처로 직접 지목 · §16 표 architecture-db→agent-design-review-db |
| 8 | s003/b6 (17–18) | Django ORM·서비스 레이어 구현의 implementation-django 위임 | Obligation | — | `agent-discipline-reviewer` | 동상 — ①문면 지목 · §16 표 implementation-*→discipline-reviewer. 이 블록은 s001 description 에 대응 문면이 없어 restates 대상 밖 |
| 9 | s004/b1 (20–21) | RFC 9110 의미론 우선 — 메서드 안전성·멱등성 준수와 PUT/PATCH/POST 의미 구분 | Obligation | — | `agent-design-review-api` | ①문면 역할명 0 · ②27종 docstring 전수 실독 — HTTP 메서드 안전성·멱등성 술어 0(오류 계약 4종은 error wire·status 축) · §16 위임 기본값 표(architecture-api→design-review-api). 발주서·P0 비고대로 final §2 에는 대응 규범이 0이라 이 지시력은 SKILL 고유 — 검수표 §3 에 기록 |
| 10 | s004/b2 (22) | URL 리소스 설계 — 명사·복수형·케밥케이스 | Obligation | — | `agent-design-review-api` | ①문면 역할명 0 · ②check-naming docstring 은 저장소 파이썬 경로·심볼 이름 축(#28·#30·#33·#41)이라 REST URL 명명은 비커버(final s013-3.1/b2 basis 와 동일 실측) · §16 기본값 |
| 11 | s004/b2 (22) | URL 의 동사 행위 포함 금지 | Prohibition | — | `agent-design-review-api` | 동상 — 금지 형식 문면 · 검사 공백 → 기본값 |
| 12 | s004/b3 (23) | 확립 배포 계약의 우선 보존 | Obligation | — | `agent-design-review-api` | ①문면 «기존 배포 계약을 먼저 보존하고» · ②check-error-centralization docstring «auto·preserve-established 는 schema semantics 미적용»(profile gate) — 보존 판정은 검사기 밖 · §16 기본값(final s024-5.4/b2 배선과 동일) |
| 13 | s004/b3 (23) | 신규 dddjango Ninja 범위의 dddjango-code-json 선택 | Obligation | — | `agent-design-review-api` | ①문면 «…을 선택한다» — 프로필 «선택» 판정은 API 계약 설계(final s024-5.4/b1·b3 배선 · ninja s023-6.2 «오류 프로필 선택의 architecture-api §5.4 위임» 판례) · ②검사기는 선택 «후» 실현만 본다 |
| 14 | s004/b3 (23) | shape 변경의 별도 사용자 승인 — 플러그인 기본 property 목록 부재 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 «별도 사용자 승인이 필요하다» — 승인 evidence 존재 판정은 G1 게이트 소유(Coordinator · final s024-5.4/b6 «G1 표면화(STOP)»→command-dddjango 판례) · 12-slot·shape 계약 심사판은 design-review-api 병기 · ②27종 전수 — 사용자 승인 evidence 술어 0. 앞선 «기본 property 목록은 없으며»는 사실 전제라 미채번 |
| 15 | s004/b3 (23) | RFC 9457 Problem Details 의 별도 요구 시 한정 선택 | Exception | — | `agent-design-review-api` | ①문면 «별도 요구가 있을 때만» = 조건 한정(L-E 유형) · §16 기본값(final s024-5.4/b4 Exception 과 동형) |
| 16 | s004/b3 (23) | 두 프로필 wire 필드의 한 범위 혼합 금지 | Prohibition | `check-error-centralization.py` | — | ②§16 역할명→검사기 매핑 표 «schema checker» = check-error-centralization · docstring «dddjango-code-json validates the canonical common/BC FrameworkErrorSchema modules, project inventory correspondence, wire-code uniqueness» 가 wire 필드 혼입을 집행(final s024-5.4/b5 배선과 동일) |
| 17 | s004/b3 (23) | 혼합 금지의 주어 한정 — 구현 레시피의 프로필 편입 금지 | Prohibition | — | `agent-design-review-api` | ①문면 «혼합 금지의 주어는 wire 필드다» = 금지 범위 해석 규칙(구현 레시피는 프로필 소속이 아니다) · 해석 판정은 API 설계 리뷰(final s024-5.4/b6 동명 Work 와 같은 축·class) |
| 18 | s004/b3 (23) | 신규 범위의 RFC 9457 wire 채택 시에도 표준 controller 레시피 구현 | Obligation | `check-api-error-controller-contract.py` | — | ②§16 매핑 표 «controller checker» = check-api-error-controller-contract · docstring «Enforce direct controller-owned code-profile error mapping … analyzes only selected controllers owned by an error-bc» — 표준 레시피(controller 소유·직접 매핑)가 검사기 계약 그 자체(final s024-5.4/b6 배선과 동일) |
| 19 | s004/b3 (23) | preserve-established 범위의 관할 배제 — native 보존 관할 | Exception | — | `agent-design-review-api` | ①문면 괄호 «preserve-established 범위는 native 보존 관할 — 이 문장의 대상 아님» = 적용 범위 한정 · ②check-error-centralization·check-api-error-controller-contract docstring «auto and preserve-established … add no new error-mapping semantics» profile gate 와 정합(final s024-5.4/b6 Exception 동형). 채번 위치: 이 괄호 조문은 자기를 감싼 레시피 절 **뒤에** 시작하므로 §13 «문장 등장 순 = 채번 순»대로 레시피 Work 다음(F7 수리) |
| 20 | s004/b3 (23) | profile 미열거 조합 채택 시 G1 표면화(STOP) | Obligation | — | `command-dddjango` | ①문면이 «G2 게이트 취급 … profile 열거에 없어 채택 시 G1 표면화(STOP) 대상» 이라 게이트 절차를 지목 — 절차 소유는 Coordinator(§16 기본값 이탈의 문면 근거 · final s024-5.4/b6 동일 배선) |
| 21 | s004/b4 (24) | 요청/응답 계약의 상태 코드별 body·header·schema 명시 기록 | Obligation | `check-response-schema-bypass.py` | `agent-design-review-api` | ②check-response-schema-bypass docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» — 성공 2xx 의 «선언 schema 경유» 부분 백스톱이라 정본 architecture-api-final s022-5.2/b1(«상태 코드별 본문 존재 여부·schema 분리 정의» — 같은 검사기·같은 부분 백스톱 논거) 배선을 승계한다(§16 «역도 성립»). 커버 범위는 **성공 2xx schema 우회 1축 한정**이고 header 표면·오류 표면·«명시 기록» 행위 자체(정의 존재 여부)는 검사 공백 → §16 기본값 병기. 준거 정정: s021-5.1 은 b1~b8 전건 기본값(E 0)이라 «계열 배선과 동일»이 성립하지만, s022-5.2 는 b1=check-response-schema-bypass·b5=check-openapi-error-declaration 이라 기본값 계열이 아니다(b5 의 오류 표면 축은 이 Work 가 아니라 28–29행 OpenAPI Work 가 진다) |
| 22 | s004/b4 (24) | 엔드포인트 변경마다 계약 체크리스트(Resource·Method·Request·Response·Error·Auth·Compatibility·OpenAPI) 검토 | Obligation | — | `agent-design-review-api` | ①문면 역할명 0 · ②③④ 지목 0 → §16 기본값(final s023-5.3/b1 «엔드포인트 설계·변경 시 계약 체크리스트 병행 검토» 배선과 동일) |
| 23 | s004/b5 (25) | 데이터 특성(정렬 안정성·실시간성·딥 페이지) 기반 페이지네이션 방식 선택과 기준 명시 | Obligation | — | `agent-design-review-api` | ①문면 역할명 0 · ②27종 전수 — 페이지네이션 술어 0 · §16 기본값(final s042-9.2 선택 기준 표 배선과 동일) |
| 24 | s004/b6 (26) | 버전 전략(URL·헤더·쿼리파라미터)의 API 변경 전 결정 | Obligation | — | `agent-design-review-api` | ①문면 §10 귀속 · ②27종 전수 — 버전 전략 술어 0 · §16 기본값(final s047-10.3/b1 «단일 버전 전략의 일관 적용» 배선과 동일) |
| 25 | s004/b6 (26) | 하위 호환성·Deprecation 프로세스의 API 변경 전 결정 | Obligation | — | `agent-design-review-api` | ①문면 §11 귀속 · ②breaking 판정을 계산하는 검사기 없음(final s049-11.1 basis 실측) · §16 기본값(final s049-11.1·s050-11.2 배선과 동일) |
| 26 | s004/b7 (27) | duplicate-sensitive 요청의 Idempotency-Key 정책(scope·replay·conflict 계약) 확정 | Obligation | — | `agent-design-review-api` | ①문면 역할명 0 · ②check-idempotency-scope-creep 은 «G1 승인 없는 미요청 멱등성 추가 금지»(G0) 축이라 «정책을 정한다» 의무는 비커버(final s021-5.1/b6 basis 와 동일 논거 · 도피 아닌 실측 기본값) · §16 기본값(final s060-13.3/b1 배선과 동일) |
| 27 | s004/b8 (28–29) | 모든 계약 결정의 OpenAPI 반영 — path·method·schema·response·security·header 전수 기술 | Obligation | `check-openapi-error-declaration.py` | `agent-design-review-api` | ②check-openapi-error-declaration docstring «positional/auto/preserve 실행은 기존 openapi_extra.responses 저장소 전수 검사를 보존 … dddjango-code-json 은 operation 이 직접 반환하는 BC 오류와 response={status: <Bc>ErrorSchema} 선언의 일치를 검증» — 오류 표면 한정 부분 커버 · 나머지 표면(path·method·security·header)은 검사 공백이라 §16 기본값 병기(final s065-14.3/b1 배선과 동일) |
| 28 | s005/b1 (31–33) | 주제별 라우팅 준거 — references/final.md 해당 절 준수 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 «해당 절을 따른다» — 준거 문서 로드·인용 축 · ②27종 docstring 에 문서 로드·인용 술어 0 · §16 기본값 + 로드 절차 소유 Coordinator 병기(agent-design-architect s005 선례) |
| 29 | s005/b18 (51) | 필요 항목 한정 독해 — 전체 로드 불필요 | Exception | — | `command-dddjango`·`agent-design-review-api` | ①문면 괄호 «(전체 로드 불필요)» = 전량 로드 의무의 면제 조문이라 Exception(agent-design-review-api s003 판례) · ②27종 docstring 에 로드 범위 술어 0 · §16 기본값 + 로드 절차 Coordinator 병기 |

## 3. 재진술

### 3.1 같은 문서 안 쌍 — spec `restates` 에 반영(유예 아님)

| 사본 블록 | 정본 블록 | 판정 |
|---|---|---|
| s001/b2 (3행 `description`) | s003/b1(10–12) · b2(13) · b3(14) · b4(15) · b5(16) | 발주서 s001 비고 «위임 문면 s003 중복» 의 실물. §15 대로 **사본(frontmatter) → 정본(본문 절)** 단일 방향, 부분 재진술이라 양쪽 Work 유지. **s003/b6(17–18 `implementation-django` 위임)은 연결하지 않았다** — description 에 대응 문면이 없다(수임처 4종만 열거) |

### 3.2 교차 문서 유예 (T3-EXECUTION «교차 문서 쌍 전량 유예» 결정 — 소급 패스 재료)

좌표는 **마커 제거본(센서스) 기준**이다(`architecture-api-final` 은 기이관 문서라 현재 파일에는 마커가 삽입돼 있다).

| # | 사본(이 문서) | Work | 상대 정본(센서스 좌표) | 비고 |
|---|---|---|---|---|
| 1 | s004/b2 (22) | URL 리소스 설계(명사·복수형·케밥케이스) | `architecture-api-final` s013-3.1/b3 (96) · b4 (97) | 정본은 명사/복수/케밥을 3 Work 로 분해 — 1:다 |
| 2 | s004/b2 (22) | URL 의 동사 행위 포함 금지 | 동 s013-3.1/b2 (95 — «명사 사용(동사 금지)») | |
| 3 | s004/b3 (23) | 확립 배포 계약의 우선 보존 | 동 s024-5.4/b2 (225) | |
| 4 | s004/b3 (23) | 신규 범위의 dddjango-code-json 선택 | 동 s024-5.4/b3 (226) · b1 (222–224 — 우선순위 단일 선택) | |
| 5 | s004/b3 (23) | shape 변경의 별도 사용자 승인 | 동 s024-5.4/b3 계열(226) | 정본에 «별도 승인» 문면이 접혀 있어 소급 패스에서 부분 재진술 여부 재확인 필요 |
| 6 | s004/b3 (23) | RFC 9457 의 조건부 선택 한정 | 동 s024-5.4/b4 (227–228) | class Exception 일치 |
| 7 | s004/b3 (23) | 두 프로필 wire 필드 혼합 금지 | 동 s024-5.4/b5 (229–230) | class Prohibition 일치 |
| 8 | s004/b3 (23) | 혼합 금지의 주어 한정 | 동 s024-5.4/b6 (231–232 — «혼합 금지의 주어는 wire 필드») | |
| 9 | s004/b3 (23) | preserve-established 관할 배제 | 동 s024-5.4/b6 (231–232 — «wire 계약 한정» Exception) | |
| 10 | s004/b3 (23) | 신규 RFC wire 의 표준 controller 레시피 | 동 s024-5.4/b6 (231–232 — 동명 Obligation) | |
| 11 | s004/b3 (23) | 미열거 조합의 G1 표면화(STOP) | 동 s024-5.4/b6 (231–232 — 동명 Obligation) | 배선도 `command-dddjango` 로 일치 |
| 12 | s004/b4 (24) | 요청/응답 계약의 상태 코드별 명시 기록 | 동 s022-5.2/b1 (194–195) · s021-5.1/b2 (185) | F2 수리 후 배선(`check-response-schema-bypass.py` + design-review-api)도 정본 b1 과 일치 |
| 13 | s004/b4 (24) | 계약 체크리스트 검토 | 동 s023-5.3/b1 (203–205) | |
| 14 | s004/b5 (25) | 페이지네이션 방식 선택·기준 명시 | 동 s042-9.2/b2~b4 (411–414 — 선택 기준 표) | 정본 3 Work(Permission)와 1:다 · class 는 SKILL 이 Obligation(«선택하고 … 명시한다») |
| 15 | s004/b6 (26) | 버전 전략의 변경 전 결정 | 동 s047-10.3/b1 (444–445) | |
| 16 | s004/b6 (26) | 하위 호환성·Deprecation 프로세스 결정 | 동 s049-11.1 (455–468 breaking 판정 Work 군) · s050-11.2/b1~b6 (470–480) | 1:다 |
| 17 | s004/b7 (27) | Idempotency-Key 정책 확정 | 동 s060-13.3/b1 (553–555) | |
| 18 | s004/b8 (28–29) | 모든 계약 결정의 OpenAPI 반영 | 동 s065-14.3/b1 (597–599) | 배선(`check-openapi-error-declaration.py` + design-review-api)도 일치 |

**유예 18건.**

**재진술 없음(SKILL 고유 지시력) 1건** — s004/b1(21행 «RFC 9110 HTTP 의미론 우선 …»). 발주서 비고와 센서스 E08 이 «final §2 = 0(속성 표·PATCH 뉘앙스 전부 사실 서술 · 지시력은 api-skill s004)» 이라고 기록했고, `architecture-api-final` spec 에도 s008-2·s009-2.1·s010-2.2·s011-2.3 이 **NAR 로 빠져 있음을 실물 확인**했다. 따라서 이 Work 는 사본이 아니라 **코퍼스 유일 정본**이다 — 소급 패스가 상대를 찾다가 «누락»으로 오판하지 않도록 명시해 둔다.

비-재진술로 판정한 것: s001/b2·s003/b2~b6 의 «→ `implementation-django-ninja` / `implementation-django-web` / `architecture-ddd` / `architecture-db` / `implementation-django`» 는 **관할 지시(준거 포인터)** 지 규범 사본이 아니다. 역방향 짝(ninja s022-6.1 «상태 코드 의미의 architecture-api 위임» 등)이 다른 문서에 있으나, 그것은 **수임처를 반대편에서 가리키는 별개 의무**다.

## 4. 경계 판단 메모

- **블록 경계 규약**: 후행 빈 줄은 선행 블록 귀속, 절 첫 블록만 헤딩 직후 빈 줄을 흡수(§13). s005 의 마지막 데이터 행이 후행 빈 줄(50)을 물어 [49,50]이고 51행이 독립 norm 블록이다. 도구가 byte 등가·무손실을 단언했고 **exit 0**(수리 루프 0회).
- **s001 헤딩 = 1행 `---`** · frontmatter 는 code 가 아니라 행 단위 prose/norm(웨이브 2 판례). 규범을 지는 것은 `description`(3행) 하나이고, `name`·`user-invocable`·종결 `---` 은 메타다.
- **kind 판정**: 코드 펜스 0 · 체크박스 0 — norm/prose/table-row 3종. s005 라우팅 표는 머리·구분행 포함 행 단위 `table-row`, 데이터 14행은 규범 미계수(P0 승계 · db 판과 동일 패턴).
- **23행의 경계 판단(이 문서 최대 난소)**: 한 불릿이 «에러 프로필 선택 계약» 전체를 접고 있다. 블록은 §13 자연 단위(불릿 1개 = 블록 1개) 그대로 두고 `djr:statesNorm` **다중 연결 9건**으로 처리했다(행 중간 분할 없음 — byte 등가 불변). 대시·콜론 뒤의 «신규 범위는 … 구현하고(…), 이 조합의 G2 게이트 취급은 …»는 **행위 주체·대상이 갈리는 독립 종결절 2개**라 각각 채번했고, 괄호 «(preserve-established 범위는 native 보존 관할 — 이 문장의 대상 아님)»는 적용 범위 한정 조문이라 Exception 으로 별도 채번했다(정본 b6 의 Exception 과 동형).
- **23행 채번 순서 규칙(F7 수리 · 2026-08-22)**: §13 «문장 등장 순 = 채번 순»의 단위는 **절(clause)의 시작 위치**다. 괄호 삽입 조문은 자기를 감싼 절이 먼저 시작하므로 **그 절 뒤에** 채번한다. 수리 전에는 preserve-established Exception(구 W7)이 자기를 감싼 레시피 절(«신규 범위는 … 구현하고» — 괄호는 그 뒤에 열린다)보다 앞서 채번돼 있었다. 수리 후 최종 순: 보존 → code-json 선택 → shape 승인 → RFC 조건부 → wire 혼합 금지 → 주어 한정 → **표준 controller 레시피 → preserve 관할 배제** → G1 표면화(STOP).
  - **정본과의 순서 관계 정정**: 이 순서가 «같은 방향»인 것은 정본 `s024-5.4` 의 **블록 진행 b1→b6**(우선순위 선택 → 보존 → code-json → RFC → wire 혼합 → b6 묶음)이다. 정본 **b6 내부**의 Work 순서(preserve 배제 → native 이전 근거 불인정 → 레시피 → G1 → 주어 한정)와는 다르다 — b6 는 여러 조문을 한 블록에 접은 자리라 내부 순서가 SKILL 문면의 절 순서와 대응하지 않는다. 오독 방지를 위해 «b1→b6 진행»이 블록 간 진행임을 명기한다.
- **class 판정**: `Prohibition` 3곳(22행 URL 동사 금지 · 23행 wire 혼합 금지 · 23행 주어 한정 = 구현 레시피의 프로필 편입 금지). `Exception` 3곳(23행 RFC 조건부 선택 · 23행 preserve 관할 배제 · 51행 «(전체 로드 불필요)»). **Override 0** — «우선»이라는 낱말이 21행에 있으나(«RFC 9110 의미론 우선») 그것은 준거 표준의 우위 선언이지 이 코퍼스의 다른 규범을 눌러 이기는 조문이 아니라 Obligation 으로 두었다(final 이 §2 를 NAR 로 둔 것과도 정합).
- **기본값 이탈(enforcedBy 병기) 근거**: ⑴ **§16 역할명→검사기 매핑 표 직접 적용** — «schema checker» = `check-error-centralization.py`(23행 wire 혼합 금지), «controller checker» = `check-api-error-controller-contract.py`(23행 표준 레시피), «OpenAPI checker» = `check-openapi-error-declaration.py`(28행). ⑵ **정본 배선 승계** — 네 자리 모두 `architecture-api-final` s024-5.4/b5·b6·s065-14.3/b1·**s022-5.2/b1**(24행 — F2 수리) 의 배선과 동일하다. ⑶ **커버 범위 명기** — 28행 OpenAPI 는 docstring 실측상 **오류 표면(`openapi_extra.responses`·`response={status: <Bc>ErrorSchema}`)만** 커버하고, 24행 `check-response-schema-bypass` 는 **성공 2xx 의 «선언 schema 우회» 1축만** 커버하므로(header·오류 표면·«기록» 행위 자체는 공백) 두 자리 다 커버 범위를 basis 에 적고 기본값을 병기했다.
- **24행 배선의 수리 경위(F2 · 2026-08-22)**: 수리 전 basis 는 «final s021-5.1·s022-5.2 계열 배선과 동일»이라며 기본값 단독으로 내렸으나, 실물 대조 결과 s022-5.2 는 **b1=`check-response-schema-bypass.py`·b5=`check-openapi-error-declaration.py`** 라 «계열 = 기본값»이 성립하지 않았다(s021-5.1 만 b1~b8 전건 기본값). 유예표 #12 가 정본으로 지목한 b1 에 docstring 근거 있는 담당 검사기가 실재하므로 §16 «역도 성립»에 따라 병기하고 basis 의 준거 문구를 정정했다.
- **오배선 회피 기록 3건**:
  1. **22행 URL 명명** — `check-naming.py` 는 저장소 파이썬 경로·심볼 이름 축(#28 약어·#30 접미·#33 폴더 토큰·#41 Port/Adapter)이라 **REST URL 문자열을 보지 않는다**(final s013-3.1 basis 의 실측 승계). 달면 다른 대상을 집행하게 되므로 비웠다.
  2. **27행 Idempotency-Key 정책** — `check-idempotency-scope-creep.py` 는 «G1 승인 없이 accepted scope 밖에 멱등성 산출물이 추가됐는가»(G0 확장 금지)만 AND 게이트로 차단한다. 이 규범은 반대로 «필요한 곳에 정책을 정하라»는 의무라 검사기 술어와 방향이 다르다 — 실측 근거를 가진 기본값이다.
  3. **21행 메서드 의미론** — 오류 계약 4종(`check-api-error-controller-contract`·`check-error-centralization`·`check-openapi-error-declaration`·`check-response-schema-bypass`)은 error wire·status·schema 축이고, 메서드 안전성·멱등성 자체를 무는 술어는 27종 어디에도 없다(전수 실독 결과).
- **로드·라우팅·위임 경계 규범의 소유**: ddd·db 판 검수표와 동일 처분 — 로드 조건·라우팅 준거는 문서군 기본값(`agent-design-review-api`) + `command-dddjango`(스킬 배분 소유 · agent-coder s004·agent-design-architect s005 선례), «X → skill-y» 불릿은 **수임 문서군 기본 Agent**(implementation-*→`agent-discipline-reviewer` · architecture-ddd→`agent-design-review-ddd` · architecture-db→`agent-design-review-db`).
- **23행 «shape 변경 승인»의 Coordinator 병기**: 사용자 승인 evidence 의 존재 판정은 G1 게이트 소유라 `command-dddjango` 를 병기했다(기본값 이탈 · final s024-5.4/b6 «G1 표면화(STOP)»→`command-dddjango` 판례와 같은 근거). 12-slot·shape 계약 심사판은 `agent-design-review-api` 가 그대로 진다.
