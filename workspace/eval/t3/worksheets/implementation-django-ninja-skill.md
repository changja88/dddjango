# T3 이관 검수표 — implementation-django-ninja-skill

- 원문: `dddjango/skills/implementation-django-ninja/SKILL.md` (56행 · 센서스 일치 · 마커 0 — 미이관 문서)
- spec: `workspace/eval/t3/specs/implementation-django-ninja-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-django-ninja-skill.spec.json` → **exit 0** (블록 40 · Work 64 · `--write` 미사용)
- 배선 전 `dddjango/scripts/check-*.py` **27종 docstring 선두 전수 실독** 완료(§16 L-F 의무 — 묶음 «django-skills» 3문서 공통 1회). 이 문서는 정본(`implementation-django-ninja-final`)이 이미 이관돼 있어 **정본 배선과의 일관성**을 배선 판단의 4번째 축으로 썼다.

## 1. census 대사 (절별 규범 수)

| 절 | 헤딩 | 발주서(센서스) | spec | 차 | 판정·사유 |
|---|---|---|---|---|---|
| s001 | (전문) | 2 | 2 | 0 | 일치 — description 3행 = 로드 조건 1 + 병렬 위임 1(4건 라우팅이 한 문장·한 축이라 1 Work). 주제 나열은 비계수 |
| s003 | 언제 쓰나 | 5 | 5 | 0 | 일치 — 로드 1 + 경계 불릿 4. 13행 괄호(«idempotency 저장소·retention은 `architecture-db`»)는 같은 불릿의 두 소유라 1 Work·소유 Agent만 2개 병기 |
| s004 | 핵심 운영 원칙 | 35 | 55 | **+20** | **센서스 과소** — 센서스는 문장 계수(내 재계수로 33문장, 센서스 35는 세미콜론·대시 분리 2건 차)이고 이 절은 정본 §1~§11 규칙의 **압축 요약 사본**이라 한 문장이 정본의 여러 Work를 삼킨다. 아래 불릿별 대조표가 정본 Work와 1:1로 붙는 것을 보인다(§13 해상도 처분은 바로 아래 절 참조) |
| s005 | 상세 레퍼런스 | 2 | 2 | 0 | 일치 — 40행(준거)·56행(한정 로드). 표 11행은 목차라 비계수 |
| **계** | | **44** | **64** | **+20** | 불일치 1절 = «센서스 과소» 판정 — 과대 산정 판정 0 |

### s004 불릿별 대조 (센서스 문장 ↔ spec Work)

| 행 | 불릿 주제 | 문장 | spec Work | 분리 사유(정본 대조) |
|---|---|---|---|---|
| 20 | Router thinness | 1 | 2 | 유지 의무 + 책임 4종 폐쇄 — 정본 s006-1.3은 b1(Obligation)·b3(Prohibition)로 이미 분리 |
| 21 | schema 분리·ModelSchema | 1 | 2 | 분리 의무 + 조건부 허용(Exception) — 정본 s012-3.1 b1 / s013-3.2 b1 |
| 22 | 봉투 discriminator | 2 | 4 | birth-enum 파생 / 버전 태그 동결 / admission 후보 / add·update 한정 검증 — 정본 s012-3.1 b7이 같은 4축 |
| 23 | 중앙 test admission | 3 | 6 | 후보 취급 / recipe 조건 / HTTP mount 검증 / OpenAPI 문서 검증 / 자격 부정 / 내부 unit test 금지 — 정본 s026-8 b2·s028-9.1 b1·b3·b5 |
| 24 | 공통 FrameworkErrorSchema | 5 | 5 | 문장=규범 1:1(정본 s023-6.2 b2·b4·b29 대응) |
| 25 | BC 오류 파일 | 2 | 3 | 단일 집약 / metadata 보존 / 금지 열거 — 정본 s023-6.2 b8~b14 |
| 26 | controller 오류 경로 | 4 | 6 | call 배치 / catch 형태 / Status 직접 반환 / 성공 변환 자리 / status property 비요구 / 우회 금지 — 정본 s023-6.2 b17(4 Work)+b29 |
| 27 | response= 선언·framework status | 3 | 4 | 선언 의무 / 변환·광고 금지 / body 계약 주장 금지 / OpenAPI 사후 변형 금지 — 정본 s023-6.2 b30·b34 |
| 28 | api.py·registrar·composition_root | 2 | 5 | API 인스턴스 / auto_import=False / registrar 노출 / urls.py 호출 / DI 한정 소유 — 정본 s010-2.3 b8(3 Work)·b9·b22 |
| 29 | auth·infra 실패 | 2 | 4 | 실패 반환 형태 / request.auth 금지 / 기본 500 / 승인 정규화 예외 — 정본 s023-6.2 b31(3 Work)·b33 |
| 30 | JSON 성공·carveout | 2 | 2 | 정본 s009-2.2 b14와 동수 |
| 31 | operation 문서화 | 1 | 2 | 문서화 / 반환 타입 — 정본 s009-2.2 b12·b13 |
| 32 | Idempotency-Key | 1 | 3 | endpoint 한정 / 정책 소유 / 저장소 소유 — 정본 s025-7 b1·b3·b8 |
| 33 | OpenAPI 확인 | 1 | 1 | 일치 |
| 34 | Ninja 목표·DRF 보조 | 1 | 2 | 목표(Obligation) / 보조 한정(Permission) — 정본 s001 **b1**의 둘째·셋째 규범(b2=[14,15]는 무규범 prose · W3 L7 수리) |
| 35 | 버전 핀 | 1 | 3 | 핀 추가 / 글로벌 설치 금지 / 표기 관례 — 정본 s008-2.1 b2가 같은 축 5 Work |
| 36 | 라우팅 선행 | 1 | 1 | 정본 s031-11 세 규범의 압축이지만 문면이 «각 소유 스킬 먼저» 한 문장이라 1 Work(소유 Agent만 합집합) |
| **계** | | **33** | **55** | |

#### §13 «문장 해상도» 조항 대비 처분 (W3 M2 수리 — 2026-08-22)

- **철회한 전제**: 초판은 «사본의 해상도가 정본보다 낮으면 재진술 연결(웨이브 4 소급 패스)이 불가능해진다»를 +20 판정의 사유로 적었다. **기계 실물과 어긋나므로 철회한다** — `djr:restates`는 `ontology_migrate.py`(블록 루프 안 `for target in blk.get("restates", [])` → `b_iri djr:restates <상대 블록 IRI>`)가 세우는 **블록→블록** 링크라, 사본 블록이 Work를 몇 개 매달았는지는 소급 연결의 성립 조건이 아니다.
- **§13 문면과의 관계**: §13은 «‹문장 해상도› = Work 채번 단위가 문장 · ‹절 해상도› = 절의 규범 전체가 Work 1개»로 **해상도라는 말의 뜻**과 그 그래프 실현(블록 경계는 자연 단위 고정 · 한 블록의 여러 규범은 `djr:statesNorm` 다중 연결)을 규정한 조항이다. 두 해상도를 나란히 정의한 문면 자체가 채번 단위를 문서·절마다 고르는 것임을 보이므로, **«문장 하나당 Work 하나»를 상한으로 못 박은 조항은 계약에 없다**. 이 절이 33문장에 55 Work를 세운 것은 §13 위반이 아니라 아래 두 근거로 선택한 해상도다.
- **근거 ⑴ 기계 요건**: spec 스키마의 Work는 `class` 단일 값 + `enforcedBy`/`delegatedTo` 한 벌을 진다. 한 문장이 유형이 갈리는 두 명제(예: 22행 «중앙 test admission 후보이며 … `add/update`일 때만 검증한다» = Obligation + Exception)나 소유가 갈리는 두 명제(32행 = design-review-api / design-review-db)를 담으면, 병합은 유형·소유를 **손실**시킨다. 문장 단위 재병합은 이 손실을 대가로만 가능하다.
- **근거 ⑵ 정본 정합**: 불릿별 대조표대로 55 Work가 이미 이관된 정본 Work와 1:1로 붙는다. 사본이 정본보다 굵으면 소급 패스가 사본 Work 1개 ↔ 정본 Work 다수의 다대일 대조를 하게 되어 **재진술 축 판정이 흐려진다**(연결 자체는 블록→블록이라 성립하지만, Work 대 Work 대사는 못 한다).
- 남는 비용 기록: 이 처분은 «압축 사본의 채번이 정본 해상도를 따라간다»는 관행을 이 묶음에서도 이어간 것이다. 관행을 계약 문면으로 승격할지는 T3 전 웨이브 완료 후 §13 개정 절차(§7) 몫으로 남긴다.

계수 규율(과대 방지): 한 문장 안이라도 ⑴ 행위 대상이 다르거나 ⑵ 규범 유형 축(Obligation/Prohibition/Permission/Exception)이 갈릴 때만 분리했다. 같은 축의 부정면 재진술은 병합했다 — 예: 26행 «오류 tuple/raw Response·dict·helper/factory/…·generic response builder는 금지한다»는 대상이 8종이지만 한 축(우회 수단 금지)이라 1 Work(정본 s023-6.2 b29도 같은 처분). §N 좌표 안내(«(§2.2·§6.2)» 등)는 전부 비계수.

## 2. 배선 근거 표 (전 규범 64건)

> 표는 spec JSON에서 기계 생성 — 수리 시 재생성한다. 근거 기호 ①문면 역할명 ②검사기 docstring 인용 ③P0 커버 ④registry #N.
> 기본값: §16 «implementation-* → `agent-discipline-reviewer`». 이탈 병기 — 계약 shape·프로필 축 `agent-design-review-api`, 도메인 enum·구조 패턴 축 `agent-design-review-ddd`, 저장소 축 `agent-design-review-db`, G1 승인·절차 축 `command-dddjango`.

| # | 절/블록(행) | Work label | class | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b2 (3) | Router·Schema·API 어댑터 코드 작성·리팩터링 시 이 스킬 선로드 | Obligation | — | `agent-discipline-reviewer`·`command-dddjango` | ①문면 «…먼저 로드한다» — frontmatter description 은 스킬 로드 트리거(행 단위 norm) · ②27종 전수 — 스킬 로드·라우팅 술어 0 · §16 기본값 + 절차 층 Coordinator(스킬 부착 결정 주체) |
| 2 | s001/b2 (3) | REST 계약·도메인 규칙·ORM/트랜잭션·테스트 mechanics 의 소유 스킬 위임 | Obligation | — | `agent-design-review-api`·`agent-design-review-ddd`·`agent-discipline-reviewer` | ①문면 «…로 위임» 4건 · ②27종 — 위임 경계 술어 0 · §16 문서군 표(architecture-api→design-review-api · architecture-ddd→design-review-ddd · implementation-django/-test→discipline-reviewer) · ninja-final s005-1.2 b1~b4 동일 축 배선 |
| 3 | s003/b1 (10–12) | Django Ninja 어댑터 설계·작성 작업의 스킬 로드 조건 | Obligation | — | `agent-discipline-reviewer`·`command-dddjango` | ①문면 «…코드를 설계·작성할 때 로드한다» · ②27종 — 로드 판정 술어 0 · §16 기본값 + 절차 층 Coordinator · ninja-final s004-1.1 b1 동일 축 |
| 4 | s003/b2 (13) | REST 계약 요소의 architecture-api 위임(idempotency 저장소·retention 은 architecture-db) | Obligation | — | `agent-design-review-api`·`agent-design-review-db` | ①문면 두 소유 명시 «→ architecture-api (idempotency 저장소·retention은 architecture-db)» · ②27종 — 계약 결정 소유 술어 0 · §16 문서군 표 2행 · ninja-final s005-1.2 b1(계약 축)+s025-7 b8(저장소 축) 배선 종합 |
| 5 | s003/b3 (14) | 애그리거트·상태 전이·구조 패턴의 architecture-ddd 위임 | Obligation | — | `agent-design-review-ddd` | ①문면 «→ architecture-ddd» · ②27종 — 구조 패턴 채택 판정 술어 0 · §16 문서군 표 · ninja-final s005-1.2 b2 동일 배선 |
| 6 | s003/b4 (15) | ORM·셀렉터·서비스·트랜잭션·마이그레이션·캐시·보안 구현의 implementation-django 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-django» · ②27종 — 스킬 경계 술어 0 · §16 기본값(implementation-* → discipline-reviewer) · ninja-final s005-1.2 b3 동일 배선 |
| 7 | s003/b5 (16–17) | pytest 픽스처·팩토리·mock·동시성 테스트 구현의 implementation-test 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-test» · ②27종 — 동상 · §16 기본값 · ninja-final s005-1.2 b4 동일 배선 |
| 8 | s004/b1 (19–20) | Router operation 의 HTTP 어댑터 유지 | Obligation | — | `agent-discipline-reviewer` | ①문면 «Router는 HTTP 어댑터로 얇게»(§1.3) · ②27종 전수 — 어댑터 «두께» 의미 판정 술어 0 · §16 기본값 · ninja-final s006-1.3 b1 «Router operation = HTTP adapter»(E 없음·discipline-reviewer) 동일 배선 |
| 9 | s004/b1 (19–20) | Router 책임의 4종 한정 | Prohibition | `check-context-isolation.py` | `agent-discipline-reviewer` | ②check-context-isolation docstring «방향 … #93/#94/#95 driving 잎의 import 폭» — 실물 진단은 loc∈{api, driving, cron_job, event_subscription}에서 #93(application_layer/port import)·#94(driven_layer import)·#95(domain 에서 가져올 수 있는 것은 exception·값 객체뿐)라 어댑터 밖 책임 유입을 import 폭으로 결정적으로 문다 · ①문면 «요청 바인딩·auth hook·서비스 호출·응답 매핑만» · ninja-final s006-1.3 b3 동일 배선. #96 소유자 check-event-publish.py 병기는 심사 후 기각 — ⒜ #96 은 `api_router.py`를 잎에서 명시 제외하고(docstring «api_router.py·event_router.py 는 잎이 아니다 — #99» · `WIRING_FILES` 실물) ⒝ 남는 겹침면(controller 잎의 domain_layer·port 선언 import)은 위 #93·#95 가 같은 위반면을 이미 문다(저장소 «중복 진단 금지» 규약) |
| 10 | s004/b2 (21) | request/response schema 의 명시 분리 | Obligation | `check-usecase-dto-placement.py` | `agent-discipline-reviewer` | ②check-usecase-dto-placement docstring «#208 command 는 schema_in 과 같은 타입을 쓰지 않는다»·«#143/#144 schema_out 은 result 로 만든다 — 도메인·ORM 타입 노출 금지» — 요청/응답 계약 분리 축 커버 · ①문면 §3.1–§3.2 · ninja-final s009-2.2 b5·s012-3.1 b1 동일 배선 |
| 11 | s004/b2 (21) | ModelSchema 의 내부 구현 보호 확실 시 한정 사용 | Exception | `check-usecase-dto-placement.py` | `agent-discipline-reviewer` | ①문면 «ModelSchema는 내부 구현 보호가 확실할 때만» — 조건부 허용이라 Exception · ②동 docstring #143/#144(ORM 타입 노출 금지)가 위반면을 문다 · ninja-final s013-3.2 b1 «ModelSchema 사용 전 확인 4항» 동일 배선 |
| 12 | s004/b3 (22) | 발행 이벤트 discriminator 의 1종째 domain StrEnum·Literal 파생(birth-enum) | Obligation | — | `agent-design-review-ddd` | ①문면 «1종째부터 domain StrEnum + Literal[EventType.X] 파생(birth-enum)» · ②27종 — 봉투 discriminator 출처 판정 술어 0 · §16 문서군(도메인 enum 출처 = 설계 결정 → design-review-ddd) · ninja-final s012-3.1 b7 동일 배선 |
| 13 | s004/b3 (22) | 버전 태그의 리터럴 동결 | Obligation | — | `agent-design-review-ddd` | ①문면 «버전 태그는 리터럴 동결» · ②27종 — 계약 버전 태그 술어 0 · ninja-final s012-3.1 b7 «버전 태그(payload_schema_version)의 리터럴 동결 유지» 동일 배선 |
| 14 | s004/b3 (22) | union-enum 동기의 중앙 test admission 후보 취급 | Obligation | — | `agent-discipline-reviewer` | ①문면 «중앙 test admission 후보이며» · ②27종 — 영구 테스트 입장 심사 술어 0(check-test-config 는 배치·바인딩만) · §16 기본값 + rule-owner-map ⓓ(입장 감사 = discipline-reviewer) · ninja-final s012-3.1 b7 동일 배선 |
| 15 | s004/b3 (22) | 승인 공개 wire·독자 failure 의 add/update 한정 검증 | Exception | — | `agent-discipline-reviewer` | ①문면 «승인된 공개 wire와 독자 failure가 add/update일 때만 검증한다» — 조건부 허용 · ②27종 — decision 별 test action 술어 0 · ninja-final s012-3.1 b7 Exception 동일 배선 |
| 16 | s004/b4 (23) | Schema·framework 오류·OpenAPI·HTTP 검증의 중앙 test admission 후보 취급 | Obligation | — | `agent-discipline-reviewer` | ①문면 «중앙 test admission 후보다» · ②27종 — 입장 심사 술어 0 · §16 기본값 + rule-owner-map ⓓ · ninja-final s026-8 b2·s028-9.1 b1 동일 배선 |
| 17 | s004/b4 (23) | mechanics recipe 의 add/update 승인 뒤 한정 적용 | Exception | — | `agent-discipline-reviewer` | ①문면 «add/update 뒤에만 mechanics recipe를 적용하고» — 조건부 허용 · ②27종 — decision 별 적용 조건 술어 0 · ninja-final s028-9.1 b1 Exception 동일 배선 |
| 18 | s004/b4 (23) | 공개 HTTP 의 실제 URLconf mounted Django client 검증 | Obligation | `check-test-config.py` | `agent-discipline-reviewer` | ②check-test-config docstring ⑴ «pytest 설정은 존재하는데 pytest-django 를 Django settings 에 묶지 못하면 테스트 수집이 조용히 실패한다» — 무는 것은 pytest↔settings 바인딩이지 mounted 검증 자체가 아니다. 이 규범에 대해서는 «실행 전제의 백스톱»(바인딩이 깨지면 mounted client 검증이 0 collected 로 조용히 사라진다) · ①문면 «실제 URLconf에 mount된 Django client로» · ninja-final s028-9.1 b3(E=check-test-config) 동일 배선 |
| 19 | s004/b4 (23) | 공개 OpenAPI 의 mounted API 생성 문서 검증 | Obligation | `check-test-config.py` | `agent-discipline-reviewer` | ①문면 «공개 OpenAPI는 그 mounted API가 생성한 문서로 검증한다» · ②동 docstring ⑴(pytest↔settings 바인딩)은 생성 문서 확인의 «실행 전제»만 무는 백스톱이고 mounted 여부 자체를 판정하지 않는다 · ninja-final s026-8 b2(Exception E=check-test-config) 동일 배선 |
| 20 | s004/b4 (23) | 승인 공개 Python consumer 부재 시 validator 위치·loc·기본 직렬화·private 호출의 test 자격 부정 | Prohibition | `check-business-vocabulary.py` | `agent-discipline-reviewer` | ②check-business-vocabulary docstring «#53 HTTP 로만 구동(모델·팩토리 import 0)» — 공개 경계 밖 표면을 test 근거로 삼는 형태를 문다 · ①문면 «… test 자격이 아니며» · ninja-final s028-9.1 b5 동일 배선 |
| 21 | s004/b4 (23) | 오류 helper/handler 내부 unit test 생성 금지 | Prohibition | — | `agent-discipline-reviewer` | ①문면 «오류 helper/handler 내부 unit test는 만들지 않는다» · ②27종 — test «생성 근거» 판정 술어 0(check-test-config 는 자리·형태만) · §16 기본값 + rule-owner-map ⓓ · ninja-final s028-9.1 b5 둘째 규범 동일 배선 |
| 22 | s004/b5 (24) | 공통 FrameworkErrorSchema property 의 플러그인 기본값 부재 | Prohibition | — | `agent-discipline-reviewer` | ①문면 «dddjango는 공통 FrameworkErrorSchema property를 정하지 않는다» — 기본값 발명 금지 · ②27종 — «플러그인이 정한 바 없음»은 검사 대상 형태가 없다 · ninja-final s023-6.2 b2 «플러그인 공통 body property 부재» 동일 배선 |
| 23 | s004/b5 (24) | reuse 의 관찰 exact shape 보존 | Obligation | — | `agent-design-review-api` | ①문면 «reuse는 관찰된 exact shape를 보존한다» · ②27종 — 관찰 기준선 대조 술어 0 · §16 문서군(계약 shape 판정 → design-review-api) · ninja-final s023-6.2 b2 «기존 프로젝트의 관찰 shape 기준선 보존» 동일 배선 |
| 24 | s004/b5 (24) | create·approved-change 의 G1 slot 6 분리 명시 승인 | Obligation | — | `command-dddjango` | ①문면 «신규 G1 slot 6에서 … 일반 G1과 분리해 명시 승인받는다» · ②27종 — G1 승인 절차 술어 0 · §16 절차 층(승인 게이트 판정 = Coordinator) · ninja-final s023-6.2 b2 «신규 scope shape의 G1 slot 6 선제안·명시 승인» 동일 배선 |
| 25 | s004/b5 (24) | 공통 오류 모듈의 framework/ninja/framework_error_schema.py 단일 경로 | Obligation | `check-error-centralization.py` | — | ②check-error-centralization docstring «validates the canonical common/BC FrameworkErrorSchema modules, project inventory correspondence» — 단일 경로를 결정적으로 문다 · ①문면 «공통 오류 모듈은 framework/ninja/framework_error_schema.py 하나다» · ninja-final s023-6.2 b4 동일 배선 |
| 26 | s004/b5 (24) | 승인 common Schema hook 의 보존(HTTP 오류 변환·handler 금지 대상 제외) | Exception | `check-error-centralization.py` | — | ①문면 «보존 대상이며 아래 HTTP 오류 변환·handler 금지 대상이 아니다» — 금지의 예외 조문 · ②동 docstring(canonical common module 의 shape 검증) · ninja-final s023-6.2 b29 «승인 common Schema 자체 hook의 exact shape 보존» 동일 배선 |
| 27 | s004/b6 (25) | BC 오류 언어의 api/bc_error_schema.py 단일 파일 집약 | Obligation | `check-error-centralization.py` | — | ②check-error-centralization docstring «canonical common/BC FrameworkErrorSchema modules … wire-code uniqueness» · ④check-naming #118 «BC 오류 파일은 bc_error_schema.py» 로 파일명 축 보강 · ①문면 «하나에 … 를 둔다» · ninja-final s023-6.2 b8·b9·b10·b11 동일 배선 |
| 28 | s004/b6 (25) | BC·concrete 의 공통 annotation/nullability·Field metadata 보존 | Obligation | `check-error-centralization.py` | — | ②동 docstring(BC schema contract backstop) · ①문면 «공통 annotation/nullability·Field metadata를 보존하고» · ninja-final s023-6.2 b14 «BC base 식별자 field의 공통 metadata 보존» 동일 배선 |
| 29 | s004/b6 (25) | 추가 필드·validator·child model_config·URI/instance·다중 오류 schema 파일 금지 | Prohibition | `check-error-centralization.py` | — | ①문면 금지 열거 · ②동 docstring(정본 모듈 밖 shape 발명 차단) · ninja-final s023-6.2 b14 «concrete subclass의 신규 요소·drift 추가 금지»·«오류별 파일 분리·validation 전용 제2 schema 파일 금지» 동일 배선 |
| 30 | s004/b7 (26) | controller 의 좁은 try 에 application call 정확히 1개 배치 | Obligation | `check-api-error-controller-contract.py` | — | ②check-api-error-controller-contract docstring «Enforce direct controller-owned code-profile error mapping … analyzes only selected controllers owned by an error-bc» · ①문면 «정확히 한 application call만 좁은 try에» · ninja-final s023-6.2 b17 «exception path — try에 최외곽 application call 한 문장만» 동일 배선 |
| 31 | s004/b7 (26) | 구체 known exception 한정 catch | Obligation | `check-api-error-controller-contract.py` | — | ②동 docstring(controller 소유 오류 매핑 계약) · ①문면 «구체 known exception을 catch한다» · ninja-final s023-6.2 b17 둘째 규범 동일 배선 |
| 32 | s004/b7 (26) | concrete 오류 준비 후 Status 직접 반환 | Obligation | `check-api-error-controller-contract.py` | — | ②동 docstring · ①문면 «Status(<승인된 HTTP status 표현>, error)로 직접 반환하고» · ninja-final s023-6.2 b17·b15 동일 배선 |
| 33 | s004/b7 (26) | 성공 변환의 try 뒤 배치 | Obligation | `check-api-error-controller-contract.py` | — | ②동 docstring · ①문면 «성공 변환은 try 뒤에서 한다» · ninja-final s023-6.2 b17 «성공 변환의 try 뒤 배치» 동일 배선 |
| 34 | s004/b7 (26) | status body property 미요구 | Permission | — | `agent-discipline-reviewer` | ①문면 «status body property는 요구하지 않는다» — 비요구 조항이라 위반 형태가 없고 ②27종 전수에도 대응 술어 0(검사 대상 아님) · §16 기본값 — 오해 시정 판정은 discipline-reviewer |
| 35 | s004/b7 (26) | 오류 tuple·raw Response/dict·helper/factory/serializer/mapper·handler 등록·generic builder 금지 | Prohibition | `check-api-error-controller-contract.py` | — | ②동 docstring(직접 매핑 강제 = 우회 형태 차단) · ①문면 금지 열거 · ninja-final s023-6.2 b29 «오류 응답 helper·handler·builder 생성·호출 금지»·b18 «예외·catch·helper·mapping table 꾸며내기 금지» 동일 배선 |
| 36 | s004/b8 (27) | 직접 반환 BC 오류 status 의 response= 같은 BC base 선언 | Obligation | `check-openapi-error-declaration.py` | — | ②check-openapi-error-declaration docstring «선택된 operation이 직접 반환하는 BC 오류와 response={status: <Bc>ErrorSchema} 선언의 일치를 검증» — 문면 그대로 · ①문면 §6.2·§8 · ninja-final s023-6.2 b34 동일 배선 |
| 37 | s004/b8 (27) | framework-owned status 의 BC 오류 변환·광고 금지 | Prohibition | `check-business-vocabulary.py`·`check-openapi-error-declaration.py`·`check-api-error-controller-contract.py` | — | ②check-openapi-error-declaration(선언 일치)·check-api-error-controller-contract(controller 직접 매핑 계약) 양 docstring · ②·④check-business-vocabulary #119 «401·403·404·422·429·HttpError 는 framework 소유(BC 재선언 금지)» — 실물 진단이 «BC 클래스가 HttpError 를 상속»(재선언 형태)이라 «BC 오류로 변환» 축의 결정적 위반면 · ①문면 열거 · 이 규범은 정본 s023-6.2 b30 의 소유 선언(E=[check-business-vocabulary, check-api-error-controller-contract])·전환 금지(E=[check-api-error-controller-contract])·광고 금지(E=[check-openapi-error-declaration]) 세 규범을 한 문장에 접었으므로 세 검사기의 합집합으로 배선(§16 «담당 검사기 근거가 있는데 빠뜨리면 오배선») |
| 38 | s004/b8 (27) | framework body 의 정확한 code-profile 계약 주장 금지 | Prohibition | — | `agent-discipline-reviewer` | ①문면 «body를 정확한 code-profile 계약이라 주장하지 않는다» — 보고·주장 축이라 코드 형태가 없다 · ②27종 — 주장 술어 0 · ninja-final s023-6.2 b30 «framework body의 wire contract 주장 금지»(E 없음) 동일 배선 |
| 39 | s004/b8 (27) | openapi_extra 보충·OpenAPI override·monkeypatch·postprocessor 금지 | Prohibition | `check-openapi-error-declaration.py` | — | ②동 docstring «선택 API module의 수동 OpenAPI 후처리를 차단한다» — 문면 그대로 · ①문면 §8 · ninja-final s023-6.2 b34 «openapi_extra 보충·사후 변형 금지»·s009-2.2 b10 동일 배선 |
| 40 | s004/b9 (28) | 프로젝트 api.py 의 NinjaExtraAPI 단일 소유 | Obligation | `check-composition-root.py` | — | ②check-composition-root docstring «명시적 dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf의 직접 import provenance와 exactly-once 호출 관계를 함께 검사한다» · ①문면 «api.py가 NinjaExtraAPI 하나를 소유하고» · ninja-final s010-2.3 b8 동일 배선 |
| 41 | s004/b9 (28) | 명시 registrar 소유 controller 의 auto_import=False | Obligation | `check-context-isolation.py` | — | ②check-context-isolation docstring «#110 auto_import=False» — 규칙 번호로 직접 지목 · ①문면 «@api_controller(..., auto_import=False)로 … side effect를 끈다» · ninja-final s010-2.3 b9 동일 배선 |
| 42 | s004/b9 (28) | BC 의 side-effect-free register_<bc>_api(api) 노출 | Obligation | `check-composition-root.py` | — | ②동 docstring(canonical BC registrar 의 exactly-once 호출 관계) · ④check-context-isolation #431 «부작용 등록 금지» · ①문면 «side-effect-free register_<bc>_api(api)를 노출하고» · ninja-final s010-2.3 b8 동일 배선 |
| 43 | s004/b9 (28) | urls.py 의 registrar 명시 호출·mount | Obligation | `check-composition-root.py` | — | ②동 docstring(project URLconf 직접 import provenance·exactly-once) · ①문면 «urls.py가 registrar를 명시 호출·mount하며» · ninja-final s010-2.3 b8·b16 동일 배선 |
| 44 | s004/b9 (28) | composition_root/(dependency_wiring.py) 의 use-case DI 한정 소유 | Obligation | `check-composition-root.py` | — | ②check-composition-root docstring «DI 조립(컴포지션 루트)은 BC 루트의 composition_root/(결선은 dependency_wiring.py — 트리 2~4행·#84·#85)가 소유한다» — 문면 그대로 · ①문면 §2.3 · ninja-final s010-2.3 b22 «composition_root의 use-case DI 한정 소유» 동일 배선 |
| 45 | s004/b10 (29) | auth 실패의 None 반환 또는 framework AuthenticationError | Obligation | — | `agent-discipline-reviewer` | ①문면 «auth 실패는 None 또는 framework AuthenticationError이며» · ②27종 — auth hook 반환 형태 술어 0 · §16 기본값 · ninja-final s023-6.2 b31 «인증 실패 = None 반환 또는 AuthenticationError raise»(E 없음) 동일 배선 |
| 46 | s004/b10 (29) | request.auth 의 ErrorSchema 사용 금지 | Prohibition | — | `agent-discipline-reviewer` | ①문면 «request.auth에 ErrorSchema를 넣지 않는다» · ②27종 — 인증 결과 적재 술어 0 · ninja-final s023-6.2 b31 «request.auth·인증 결과의 ErrorSchema 사용 금지» 동일 배선 |
| 47 | s004/b10 (29) | raw infra 실패의 기본 500 | Obligation | — | `agent-discipline-reviewer` | ①문면 «raw infra 실패는 기본 500이고» · ②27종 — 기본 경로 술어 0(check-transient-overmapping 은 503/409 과잉매핑 형태만) · ninja-final s023-6.2 b33 «기본 경로 = framework 미식별 500» 동일 배선 |
| 48 | s004/b10 (29) | 승인된 안정 의미 한정 infra/ACL 의 자기 BC exception 정규화 | Exception | `check-synthetic-infra-exc.py`·`check-context-isolation.py` | `command-dddjango`·`agent-discipline-reviewer` | ①문면 «승인된 안정 의미만 … 정규화한다» — 조건부 허용 · ②check-synthetic-infra-exc docstring «driven 경계가 계산된 transient/경합을 신호하려고 raw 인프라 DB 예외를 from 없이 새로 생성해 raise 한 형태만 차단»·«#129 전수 명시 매핑»(합성 위반면) · ②check-context-isolation docstring «ACL #473 기저 예외를 잡는다»·«#291/#292 예외의 자리 셋»·«타 BC #12/#13»(자기 BC exception 이 아닌 것의 통과 위반면) · ninja-final s023-6.2 b33 은 Exception(D=command-dddjango) + 금지 규범(E=[check-synthetic-infra-exc, check-context-isolation])로 나뉘어 있고, SKILL 문면이 둘을 한 조문에 접었으므로 두 검사기를 합집합으로 배선 |
| 49 | s004/b11 (30) | 선언된 JSON 성공의 Schema/Status 반환 | Obligation | `check-response-schema-bypass.py` | — | ②check-response-schema-bypass docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» — 문면 그대로 · ①문면 «선언된 JSON 성공은 Schema/Status로 반환한다» · ninja-final s009-2.2 b14·s023-6.2 b35 동일 배선 |
| 50 | s004/b11 (30) | native 성공 carveout 4종 허용(오류 응답 우회 불허) | Permission | `check-response-schema-bypass.py`·`check-api-error-controller-contract.py` | — | ①문면 «FileResponse·StreamingHttpResponse·redirect·schema-less 204는 성공 native carveout이며 오류 응답 우회를 허용하지 않는다» · ②response-schema-bypass(성공 우회면)+api-error-controller-contract(오류 경로) 양 docstring · ninja-final s009-2.2 b14 Permission 동일 배선 |
| 51 | s004/b12 (31) | operation 의 summary·description·tags 문서화 | Obligation | — | `agent-discipline-reviewer` | ①문면 «summary·description·tags로 문서화하고» · ②27종 — 문서화 인자 술어 0 · §16 기본값 · ninja-final s009-2.2 b12 동일 배선 |
| 52 | s004/b12 (31) | 반환 타입 명시(object 금지) | Obligation | `check-public-surface-annotation.py` | `agent-discipline-reviewer` | ②check-public-surface-annotation docstring «#493 모든 이름은 «첫 대입»에 타입을 적는다 — 시그니처·속성·지역 변수에 예외가 없다»·«#358 … 이름 붙인 정적 타입뿐» — 반환 애너테이션 축 커버 · ①문면 «반환 타입을 명시한다(object 금지)» · ninja-final s009-2.2 b13 동일 배선 |
| 53 | s004/b13 (32) | Idempotency-Key 의 계약 정의 endpoint 한정 | Prohibition | `check-idempotency-scope-creep.py` | `agent-design-review-api` | ②check-idempotency-scope-creep docstring «태스크가 요청하지 않은 멱등성(Idempotency-Key 필수·전용 record 테이블·replay store)을 … silent 의무화해 코드로 구현하는 회귀를 차단» — 문면 그대로 · ①문면 «계약에 정의된 endpoint에만» · ninja-final s025-7 b1 동일 배선 |
| 54 | s004/b13 (32) | 키 정책(scope·replay·conflict)의 architecture-api 결정 | Obligation | — | `agent-design-review-api` | ①문면 «키 정책(scope·replay·conflict)은 architecture-api» · ②27종 — 정책 결정 소유 술어 0 · §16 문서군 표 · ninja-final s025-7 b3 동일 배선 |
| 55 | s004/b13 (32) | 저장소·retention(테이블·unique constraint·fingerprint)의 architecture-db 결정 | Obligation | — | `agent-design-review-db` | ①문면 «저장소·retention … 은 architecture-db가 결정» — 소유자를 architecture-db 하나로만 지목하므로 db 단독 위임 · ②27종 — 저장소 설계 술어 0(check-db-table 은 앱 규율만) · §16 문서군 표 · 정본 ninja-final s025-7 b8 은 D=[agent-design-review-db, agent-discipline-reviewer]이지만 그 문면이 implementation-django 축(«unique constraint·lock·transaction boundary»)을 함께 지목한 결과이고 SKILL 문면에는 그 축이 없다 — 목적지 일부 일치(«동일 배선» 아님) |
| 56 | s004/b14 (33) | 공개 OpenAPI add/update 후보의 mounted 생성 문서 확인 | Obligation | `check-test-config.py` | `agent-discipline-reviewer` | ①문면 «add/update이면 mounted API의 생성 문서를 확인한다»(§8) · ②check-test-config docstring ⑴ 바인딩(생성 문서 확인의 실행 전제) · ninja-final s026-8 b2(E=check-test-config)·s023-6.2 b34(D=discipline-reviewer) 종합 |
| 57 | s004/b15 (34) | 신규 API 의 Django Ninja 목표 | Obligation | — | `agent-discipline-reviewer` | ①문면 «신규 API는 Django Ninja 목표» · ②27종 — 프레임워크 선택 술어 0 · §16 기본값 · ninja-final s030-10 b1·s001 b1(«Django Ninja = greenfield API 구현 기본 목표») 동일 배선 — s001 b2 는 무규범 prose 라 앵커 아님 |
| 58 | s004/b15 (34) | DRF 의 legacy·migration 맥락 한정 보조 | Permission | — | `agent-discipline-reviewer` | ①문면 «DRF는 legacy·migration 맥락에서만 보조» — 한정 허용 · ②27종 — 술어 0 · ninja-final s001 b1 셋째 규범(Permission «DRF 자료의 보조 근거 한정 사용(legacy review·비교·migration)») 동일 배선 |
| 59 | s004/b16 (35) | 신규 도입 시 의존성 매니페스트 버전 핀 추가 | Obligation | — | `agent-discipline-reviewer` | ①문면 «의존성 매니페스트에 버전 핀으로 추가»(§2.1) · ②27종 — 매니페스트·핀 술어 0 · §16 기본값 · ninja-final s008-2.1 b2 동일 배선 |
| 60 | s004/b16 (35) | 글로벌 임의 설치 금지 | Prohibition | — | `agent-discipline-reviewer` | ①문면 괄호 «글로벌 임의 설치 금지» — 별개 행위(설치 경로) 금지 · ②27종 — 술어 0 · ninja-final s008-2.1 b2 동일 축 배선 |
| 61 | s004/b16 (35) | 핀 표기의 프로젝트 기존 관례 준수 | Obligation | — | `agent-discipline-reviewer` | ①문면 «핀 표기는 프로젝트 기존 관례» · ②27종 — 표기 관례 술어 0 · ninja-final s008-2.1 b2 «핀 표기의 프로젝트 기존 관례 준수» 동일 배선 |
| 62 | s004/b17 (36–37) | 라우팅 결정 전 계약·DB·도메인 미결의 소유 스킬 선행 | Obligation | — | `agent-design-review-api`·`agent-design-review-db`·`agent-design-review-ddd`·`agent-discipline-reviewer` | ①문면 «각 소유 스킬 먼저»(§11) · ②27종 — 결정 선후 술어 0 · §16 문서군 표 3종 병기 · ninja-final s031-11 b1(api)·b2(db+구현)·b3(ddd) 세 규범의 압축 사본이라 소유 Agent 를 합집합으로 배선 |
| 63 | s005/b1 (39–41) | 주제별 references/final.md 해당 절 준거 | Obligation | — | `agent-discipline-reviewer` | ①문면 «주제별로 … 해당 절을 따른다» · ②27종 — 참조 문서 준거 술어 0 · §16 기본값 |
| 64 | s005/b14 (56) | 절 단위 필요 항목 한정 로드 | Obligation | — | `agent-discipline-reviewer` | ①문면 «필요한 항목만 읽는다(전체 로드 불필요)» · ②27종 — 로드 범위 술어 0 · §16 기본값. 표 11행은 주제→절 매핑 목차라 규범 비계수(발주서 비고 승계) |

### 역할명→검사기 매핑 적용 (§16 실측 표)

- «schema checker» 계열(공통/BC ErrorSchema 형태) → `check-error-centralization.py` — 24·25행 5건.
- «controller checker» 계열(직접 매핑·우회 금지) → `check-api-error-controller-contract.py` — 26·27·29·30행 8건.
- «OpenAPI checker» 계열(response= 선언 일치·사후 변형) → `check-openapi-error-declaration.py` — 27행 3건.
- 27종 전수 실독으로 **정본이 안 붙였던 자리를 새로 붙인 것 0건, 정본과 어긋나게 뗀 것 0건** — 이 문서는 정본이 이미 이관돼 있어 배선 표류가 곧 재진술 쌍의 배선 불일치가 되므로 정본 배선을 우선 준거로 삼았다.
- 배선을 일부러 비운 자리: 26행 «status body property는 요구하지 않는다»(비요구 조항이라 위반 형태 자체가 없다), 27행 «body를 정확한 code-profile 계약이라 주장하지 않는다»(주장·보고 축 — 정본 s023-6.2 b30도 E 없음), 29행 앞 3건(auth 반환 형태 — 정본 s023-6.2 b31 전부 E 없음).

#### W3 수리 — 합문 규범의 «정본 E 합집합» 보정 (2026-08-22)

초판은 정본의 **여러 규범이 한 SKILL 문장에 접힌** 자리에서 그 규범들의 enforcedBy 합집합이 아니라 일부만 옮겨 «동일 배선»이라 적었다. 정본 실물 대조로 두 자리를 보정했다(둘 다 정본에 이미 있는 검사기라 신규 발명 0 · 표류 축소).

| 자리 | 접힌 정본 규범(E) | 초판 | 수리 |
|---|---|---|---|
| 27행 «framework-owned status 의 BC 오류 변환·광고 금지» | s023-6.2 b30 «framework 오류 소유»(E=[business-vocabulary, api-error-controller-contract]) + «BC 전환·전역 handler 가로채기 금지»(E=[api-error-controller-contract]) + «framework status 의 BC response= 광고 금지»(E=[openapi-error-declaration]) | openapi-error-declaration·api-error-controller-contract | **+ check-business-vocabulary.py**(#119 실물 진단 = «BC 클래스가 `HttpError` 상속» — 재선언 위반면) |
| 29행 «승인된 안정 의미 한정 infra/ACL 정규화»(Exception) | s023-6.2 b33 Exception(D=command-dddjango) + «인프라 예외 합성·타 BC exception 통과 금지»(E=[synthetic-infra-exc, context-isolation]) | synthetic-infra-exc | **+ check-context-isolation.py**(#473 ACL 기저 예외·#291/#292 예외의 자리·#12/#13 타 BC — «자기 BC exception 이 아닌 것의 통과» 위반면) |

- 32행 «저장소·retention 의 architecture-db 결정»은 반대 방향으로 보정했다: 정본 s025-7 b8 은 D=[design-review-db, discipline-reviewer]지만 그 병기는 정본 문면이 `implementation-django` 축(unique constraint·lock·transaction boundary)을 함께 지목한 결과다. SKILL 문면은 architecture-db 하나만 지목하므로 **db 단독 위임을 유지**하고 basis 표기를 «동일 배선» → «목적지 일부 일치»로 고쳤다.
- **#96 담당 검사기 심사(W3 M1)**: 20행 «Router 책임의 4종 한정» basis 가 인용했던 «#96 …»은 `check-context-isolation.py` 문면이 아니라 `check-event-publish.py` 소유다(docstring 11~13행). basis 를 context-isolation 실물(#93 app_port · #94 driven_layer · #95 domain 은 exception·값 객체만 — 진단 함수 `_apply_same_bc`의 `loc in ("api", "driving", …)` 분기가 Router 자리를 문다)로 교정했다. `check-event-publish.py` 병기는 **기각** — ⒜ #96 은 `api_router.py`를 잎에서 명시 제외하고(`WIRING_FILES` 실물 · #99) ⒝ 남는 겹침면(controller 잎의 `domain_layer`·port 선언 import)을 #93·#95 가 이미 같은 위반면으로 물어 병기가 «중복 진단»이 된다. 목적지(check-context-isolation)는 정본 s006-1.3 b3 과 그대로 일치.
- **배선 근거 서술 완화(W3 L10)**: 23행 두 mounted 검증 규범의 `check-test-config.py` 는 docstring ⑴ 이 pytest↔settings **바인딩**만 보므로 «결정적으로 문다» → «실행 전제의 백스톱»으로 근거 문장을 조정했다(목적지는 정본 s028-9.1 b3·s026-8 b2 와 동일하므로 배선 불변).

## 3. 재진술 유예 (교차 문서 쌍 — 전 웨이브 후 소급 패스가 연결)

같은 문서 안 쌍 1건은 spec `restates`로 넣었다: `s001/b2`(description, 3행) → `s003/b1`(11행)·`s003/b2`(13행)·`s003/b3`(14행)·`s003/b4`(15행)·`s003/b5`(16행). **발주서 재진술 열은 s001의 상대로 정본 s005-1.2만 지목했으나**, description의 4건 위임 목록이 «언제 쓰나» 경계 불릿 4건과 대상·순서까지 같은 사본이라 직접 확인 후 같은 문서 쌍으로 추가했다(브리프 «census restate 열 참고·직접 확인 후»).

아래는 타 문서 상대라 유예한다. 좌표는 **마커 제거본=센서스 기준**(상대 문서는 이미 이관돼 본문에 `graph-owned` 마커가 삽입돼 있다 — 현재 파일 행번호와 다르다). 상대 블록 서수는 병합된 `implementation-django-ninja-final.spec.json` 실물에서 확인했다.

| 사본 블록(행) | 상대 절/블록 (implementation-django-ninja-final) | 상대 행(센서스) | 확인 근거 |
|---|---|---|---|
| s001/b2 (3) | s005-1.2 b1·b2·b3·b4 · s004-1.1 b1 | 50–53 · 54–55 · 56–57 · 58–60 · 36–39 | description 위임 4건 = §1.2 위임 표 4행(3중 라우팅 표면의 첫째) |
| s003/b1 (10–12) | s004-1.1 b1 | 36–39 | 스킬 소유 범위 = HTTP adapter 구현 |
| s003/b2~b5 (13–16) | s005-1.2 b1·b2·b3·b4 | 50–60 | 경계 4행 = §1.2 위임 표(P0 «3중 라우팅 표면») |
| s004/b1 (19–20) | s006-1.3 b1·b3 | 62–64 · 71–72 | Router thinness |
| s004/b2 (21) | s012-3.1 b1 · s013-3.2 b1 | 309–313 · 343–346 | request/response 분리 · ModelSchema 조건 |
| s004/b3 (22) | s012-3.1 b7 | 323–336 | 봉투 discriminator birth-enum |
| s004/b4 (23) | s026-8 b2 · s028-9.1 b1·b3·b5 | 878–881 · 904–908 · 918–922 · 938–943 | 중앙 admission·mounted 검증·자격 부정 |
| s004/b5 (24) | s023-6.2 b2·b4·b29 | 507–514 · 534–537 · 767–775 | 공통 schema 기본값 부재·단일 경로·hook 보존 |
| s004/b6 (25) | s023-6.2 b8·b9·b10·b11·b14 | 560–562 · 563 · 564 · 565 · 593–603 | BC 오류 파일 단일 집약·metadata 보존 |
| s004/b7 (26) | s023-6.2 b17 · b29 | 616–620 · 767–775 | controller try/catch/Status 계약 |
| s004/b8 (27) | s023-6.2 b30 · b34 | 776–782 · 809–815 | framework status 소유 · response= 선언 |
| s004/b9 (28) | s010-2.3 b8 · b9 · b22 | 218–223 · 224–228 · 291–292 | API 인스턴스·auto_import=False·DI 소유 |
| s004/b10 (29) | s023-6.2 b31 · b33 | 783–786 · 802–808 | auth 실패 형태 · infra 정규화 |
| s004/b11 (30) | s009-2.2 b14 · s023-6.2 b35 | 129–132 · 816–819 | 성공 carveout |
| s004/b12 (31) | s009-2.2 b12 · b13 | 127 · 128 | 문서화 · 반환 타입 |
| s004/b13 (32) | s025-7 b1 · b3 · b8 | 855–859 · 862 · 868–870 | Idempotency-Key 소유 분할 |
| s004/b14 (33) | s026-8 b2 · s023-6.2 b34 | 878–881 · 809–815 | mounted 생성 문서 확인 |
| s004/b15 (34) | s030-10 b1 · s001 b1 | 961–965 · 2–13 | Ninja 목표·DRF 보조 |
| s004/b16 (35) | s008-2.1 b2 | 88–89 | 버전 핀 |
| s004/b17 (36–37) | s031-11 b1·b2·b3 | 986–987 · 988–989 · 990 | 라우팅 결정 트리 |

## 4. 경계 판단 메모

1. **frontmatter는 code가 아니라 행 단위 prose/norm**(웨이브 2 판례) — 1행 `---`는 절 헤딩(headingSnapshot), 2·4행은 prose, 3행 description만 norm, 5행 닫는 `---`는 6행 빈 줄과 함께 prose 블록.
2. **절 선두 빈 줄은 첫 블록 선두 귀속**(§13 유일 예외): s003 `b1=[10,12]`, s004 `b1=[19,20]`, s005 `b1=[39,41]`. 절 끝 빈 줄은 마지막 내용 블록 후행 스팬: s003 `b5=[16,17]`, s004 `b17=[36,37]`, s005 데이터 마지막 행 `[54,55]`.
3. **s004는 «한 불릿 = 한 블록»** — 문장이 여럿이어도 행을 쪼개지 않았다(§13 «행 중간 분할 불요 — 한 블록의 여러 규범 문장은 statesNorm 다중 연결»). 24·26행처럼 한 행에 Work 5~6개가 붙는 형태가 이 규약의 정상 산물이다.
4. **표는 행 단위 `table-row`** — 머리+구분행 한 블록(`[42,43]`), 데이터 11행 각 1블록, 마지막 행이 빈 줄 흡수(`[54,55]`).
5. **class 판정의 경계 3건**: ⑴ 26행 «status body property는 요구하지 않는다» → Permission(요구 면제이지 금지가 아니다). ⑵ 29행 «승인된 안정 의미만 … 정규화한다» → Exception(기본 500 규범의 조건부 예외). ⑶ 34행 «DRF는 legacy·migration 맥락에서만 보조» → Permission(정본 s001 **b1** 셋째 규범과 동일 판정 — W3 L7 좌표 수리). 24행 첫 문장 «공통 property를 정하지 않는다»는 «기본값을 발명하지 마라»는 금지로 읽어 Prohibition(정본 s023-6.2 b2와 동일).
6. **비계수 판정** — 각 불릿 말미의 «(§N·§M)» 좌표, 24행 괄호의 «`framework/ninja/`는 공유 `<technology>` 폴더 — 이 계약 밖 `<module>.py`와 공존»(정본 s023-6.2 b32가 Permission으로 이미 채번한 사실 진술이지만 SKILL 문면에서는 앞 규범의 부연이라 별도 Work를 세우지 않고 유예 표에서 정본 b4 상대로만 잇는다).

## 5. 소급 패스 이월 — 그래프 전역 결정 대기 (W3 적대 리뷰 반영 · 2026-08-22)

이 두 건은 **이 묶음 단독으로 처분할 수 없는** 판형 문제라 spec 을 고치지 않고 이월 기록만 남긴다. 전 웨이브 완료 후 소급 패스가 일괄 확정한다.

1. **§15 «정본 1곳만 Work 승격»의 적용 범위 — 스킬 전문(frontmatter description) 사본** (W3 L1 · 개별 수리 기각)
   - 현상: `s001/b2`(description)가 `djr:restates`(→ `s003/b1`~`b5`)와 **자기 Work 2건 승격**을 겸한다. 파일럿 사본 판형(ddd-final s017-3.2 b1 = restates + `norms` 0)과는 형태가 다르다.
   - 기각 근거: ⒜ §15 조항의 실물 스코프는 **축자 쌍**이다(조항이 예시로 든 파일럿이 «ninja §6.2↔§2.2 축자 쌍»). frontmatter description 은 축자 사본이 아니라 어휘·범위가 다른 압축 요약이라 «정본/사본»의 일방 지정 근거가 문서 안에 없다. ⒝ 발주서 센서스(adv 중재 2026-08-19 확정)가 s001 규범 수를 **2**로 못 박았고, 사본 판형(`norms` 0)으로 바꾸면 census 대사가 −2로 어긋난다. ⒞ T3 전 웨이브의 `*-skill` spec 8종이 전부 같은 형태라 이 3문서만 바꾸면 그래프 비일관이 오히려 커진다.
   - 이월: «스킬 전문 압축 사본의 Work 승격 허용 여부»를 §15 해석으로 확정할 것. 확정이 «불허»면 8종 + 이 3종을 한 번에 되돌려야 한다.
2. **로드 조건 규범의 위임 판형 불일치** (W3 L11 · 이 묶음 결함 아님 · 소급 정합 대상)
   - 실측 3판형: `architecture-api/db/ddd-skill` = `command-dddjango` + 해당 `design-review-*` · `discipline-tdd/cleancode/houserules-skill`·`implementation-python/test-skill` = `agent-discipline-reviewer` 단독 · 이 묶음(django·ninja·web) = `agent-discipline-reviewer` + `command-dddjango`.
   - 이 묶음의 처분 근거는 §16 위임 기본값 표 2행 병용(문서군 기본값 `implementation-*` → discipline-reviewer + «절차 층 → Coordinator»)이라 문면 근거는 성립한다. 다만 같은 규범 축이 그래프에서 세 판형으로 갈리는 것은 소급 패스가 일괄 정합해야 한다.
   - 파생 미정리 1건: 이 묶음은 `s005` 로드 범위 규범(«필요한 항목만 읽는다»)에는 Coordinator 를 붙이지 않았는데 `architecture-*-skill` 3종은 붙였다 — 같은 결정에 포함시킬 것.
