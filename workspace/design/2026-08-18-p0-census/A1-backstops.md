# A1 — 결정적 백스톱 인벤토리 (P0 센서스 · 구조 실사)

- 조사일: 2026-08-18
- 대상: `/Users/hyun/Desktop/dddjango/dddjango/scripts/` 파이썬 파일 전수 **33개** = 검사기(`check-*`) **27** + 보조 모듈 **6**
- 방법: 전 파일 모듈 docstring AST 추출 + 스킬명/`§`/규칙번호(`#nnn`) grep + `checker_registry.py`·`registry_gate.py`·`checker_target.py` 전문 정독. 대상 파일 수정 없음.

## 1. 검사기 27종 (로스터 순서 = `checker_registry.py` REGISTRY = `commands/dddjango.md` «순서 고정» 절)

«규칙 대응 기록»은 docstring·주석에 rule-owner-map/트리 개정 명세 규칙번호(`#nnn`) 또는 스킬 문서 `§` 참조가 있는가로 판정했다.

| # | 스크립트 | 역할 | 검사 대상 | 규칙 대응 기록 유무 |
|---|---|---|---|---|
| 1 | check-mechanism-ownership.py (337행) | DB 메커니즘 교체 + migrations 규율 백스톱 | ⑴ 프로덕션 DB 엔진의 트랜잭션·락 메커니즘을 커스텀 백엔드로 무승인 교체(AND 4조건) ⑵ migrations 4규칙(#336 자리·#337 이름·#338 domain import 금지·#593 손편집 금지) | ○ — #336·#337·#338·#593, 트리 80·81행, «트리 개정 명세» |
| 2 | check-error-centralization.py (4,692행) | code-profile FrameworkErrorSchema 스키마 계약 (AUTO) | 정본 common/BC FrameworkErrorSchema 모듈, 프로젝트 인벤토리 대응, wire-code 유일성, raw 문자열 판별식 (profile-gated: `dddjango-code-json`만 스키마 의미 적용) | ○ — 본문에 #114·#414·#417·#568·#572·#636 등, «트리 개정 명세» (docstring은 영어·요약형) |
| 3 | check-response-schema-bypass.py (1,016행) | 선언된 Ninja schema 우회 raw 반환 차단 | 선언된 schema 를 우회하는 raw 200–203 직접 반환(HttpResponse/JsonResponse). selector-free=touched 게이트, `--controller-module`=정확 선택 집합 | **«규칙 대응 미기록»** — 가드 규칙 #74·#78 뿐, 주 규칙의 번호·§·스킬명 없음 |
| 4 | check-layer-skeleton.py (346행) | 표준 파일트리 골격 «존재·폐쇄» 백스톱 | #486 BC 골격 상존 · #488 고정 칸 필수 · #489 자리표시자 · #490 트리 밖 경로 금지 · #81 BC 직계 7 · #429/#436 `<project>/` 폐쇄 · #58/#314/#393 금지 경로 · #395 framework 자식 다섯 | ○ — 제1원칙 #486~#491 등, «트리 개정 명세», standard_tree 도출 |
| 5 | check-openapi-error-declaration.py (3,426행) | OpenAPI 오류 계약 백스톱 (AUTO) | operation 이 직접 반환하는 BC 오류와 `response={status: <Bc>ErrorSchema}` 선언의 일치, 선택 API module 의 수동 OpenAPI 후처리 차단 | ○ — implementation-django-ninja §2.2, rule-owner-map, #131 등 |
| 6 | check-context-isolation.py (994행) | BC 경계·층 의존 방향 백스톱 (layer-skeleton 의 «방향» 짝) | 방향(#2·#9·#93~#95·#185·#186·#251·#288·#312·#322·#328) · 타 BC(#12·#13·#98·#102·#51) · OHS 구조/계약/명명(#146~#170·#453~#455·#472·#482~#484·#633·#634·#295) · ACL(#361·#363·#364·#450·#473) · 기타(#14·#110·#117·#291·#292·#431) | ○ — «트리 개정 명세» 규칙번호 약 40종 명기 |
| 7 | check-app-container.py (234행) | 앱 컨테이너 위치 백스톱 | `application/` **밖**(루트 평면·`src/` 등)에 방치된 작동하는 Django 앱 — 이주 미이행 회귀(smoke4·smoke6) | ○ — discipline-houserules §0-1, architecture-ddd §3.2 항-(2) |
| 8 | check-ninja-boundary-middleware.py (180행) | ninja 경계 미들웨어 백스톱 | BC `driving_layer/` 자가 정의 미들웨어의 전역 `settings.MIDDLEWARE` 자가등록(콘텐츠 협상 자작 회귀) | ○ — implementation-django-ninja §6(§6.3) |
| 9 | check-common-container.py (117행) | 횡단 framework/ 컨테이너 레벨 백스톱 | `application/framework/`·`application/common/` — 횡단 버킷을 BC 컨테이너 «안»에 넣는 오배치(정본은 루트의 `application/` 형제, 트리 112~134행) | ○ — 트리 112~134행, #49(검출)·D38 (스킬 § 은 없음) |
| 10 | check-idempotency-scope-creep.py (240행) | 멱등성 스코프크립(C3) 백스톱 | 태스크가 요청하지 않은 멱등성 산출물(전용 store·model·Idempotency-Key 처리)이 G1 채택 승인 없이 scope 밖에 추가됨 (scope.md 의 미요청 단정 ∧ 승인 배너 부재) | ○ — architecture-db §9.6, design-architect, DR-24 C3·DR-27 |
| 11 | check-public-surface-annotation.py (392행) | 타입 전면(«첫 대입에 타입») 백스톱 | #493 모든 이름 첫 대입에 타입(문법 없는 여덟 자리만 면제) · #358 Thin Read 반환의 QuerySet/Model 금지 · #456 OHS contract/exception 의 요청 검증 예외 금지 · #69 프로덕션 assert/isinstance 가드(후보) | ○ — #493·#358·#456·#69, «트리 개정 명세» |
| 12 | check-test-config.py (464행) | 테스트 규율 백스톱 | ⑴ pytest↔Django settings 바인딩(0 collected 침묵 실패) ⑵ `test/` 구조 #383~#392·#596(직계 다섯·unit DB 금지·integration DB 필수·e2e 입구 경유·factories 규율) ⑶ settings 환경축 | ○ — 트리 105~111행·D56, #383~#392·#596 |
| 13 | check-transient-overmapping.py (233행) | transient 인프라 예외 과잉매핑 백스톱 | `OperationalError`/`DatabaseError` 핸들러가 영구장애 분기 없이 클래스 통째를 retryable status(503/409)로 무조건 매핑(AND: 핸들러 타입+분기 부재+retryable 반환) | **«규칙 대응 미기록»** — maj1 회귀 ID·보완 레인 스킬명(design-architect·discipline-reviewer)뿐, 자기 규칙의 번호·§ 없음 |
| 14 | check-synthetic-infra-exc.py (209행) | 인프라 예외 합성 금지 백스톱 | ⑴ driven 층이 raw 인프라 DB 예외를 `from` 없이 새로 생성해 raise(ACL-EX2) ⑵ #129 catch-all(`except Exception` 등) 안에서 새 예외 생성 raise = 은폐 번역 | ○ — ACL-EX2, #129(D27), «트리 개정 명세» |
| 15 | check-api-error-controller-contract.py (6,891행) | controller 직접 오류 매핑 계약 (AUTO) | error-bc 소유 선택 controller · 선언된 error BC 의 정본 FrameworkErrorSchema 모듈 · controller 가 직접 import 하는 같은 소유자 presentation 모듈 (profile 선택형) | ○ — 본문에 #59·#62·#120~#126·#131·#132·#474, discipline-reviewer §6.2 (docstring은 영어·요약형) |
| 16 | check-composition-root.py (1,941행) | 컴포지션 루트(DI 배선) 위치 백스톱 | 정본 `composition_root/`(#84·#85) 이탈 구조 변종 3: V1 off-tree `composition/` 폴더 · V2 단일 파일 `composition_root.py` · V3 application 로직 있는 BC 의 정본 부재 (Q-7) | ○ — discipline-houserules §0, #84·#85, final.md, implementation-django-ninja §2.2 |
| 17 | check-db-table.py (584행) | driven_layer/django_<bc>/ 장고 앱 규율 백스톱 | 18규칙: 경로(#318·#324/#467 층 위장·#325·#334) · apps(#329~#332·#535~#538) · import 잎(#326) · 모델(#335 표=파일·#632 `<Name>Model`·#630 db_table·#631 타 BC FK 금지) | ○ — 트리 75~88행, «트리 개정 명세» 규칙번호 18종 |
| 18 | check-choices-literal-consumption.py (282행) | 선언된 choices 의 리터럴 소비 백스톱 | (a) 심볼-choices 필드 호출 안 `default="리터럴"` (b) 그 모델의 `objects.filter/exclude(<field>="리터럴")` — touched 라인 한정, migrations/테스트 면제 | ○ — discipline-cleancode §2.14, implementation-django §2.5/§10.4, implementation-test §15.4 |
| 19 | check-usecase-dto-placement.py (666행) | 유스케이스·경계 자료 계약 백스톱 | 트리 39~44행(+13~15행 schema): 구조(#182·#183·#188·#190/#193) · 자료 3파일(#201·#569~#571·#202/#207·#205·#189·#208·#567) · 진입점(#635·#211·#196) · 발행(#539~#541) · schema(#139·#142·#143/#144) | ○ — «트리 개정 명세»·rule-owner-map 규칙번호 다수 |
| 20 | check-transaction-boundary.py (524행) | 「한 트랜잭션 = 애그리거트 하나」(D50) 백스톱 | 11규칙: #4 응용층 django import 0 · #195 루트 경유 저장 · #197 읽기 유스케이스 UoW 금지 · #200 after_commit · #282/#283 리포지토리 파일 계약 · #285(후보) · #287 쓰기 인자=애그리거트 · #355 반환 타입 · #597 save/remove 접두 | ○ — rule-owner-map 총 11 |
| 21 | check-domain-model.py (850행) | 도메인 모델 백스톱 (D12·D13·D50) | 50규칙: #8 domain 밖 import 0 · #17/#18 1차 축 · #249~#267(애그리거트 폴더·루트 클래스·루트 경유 변경·엔티티 식별자·값 객체 불변·shared 승격) 등 | ○ — rule-owner-map 총 50 |
| 22 | check-port-adapter-pairing.py (858행) | 포트·어댑터·페이크 짝맞춤 백스톱 (D37·D44·D51·D57) | 83규칙: port/ 선언 계약(#457·#212·#215~#228·#573 등) · bypass query(#229~#239·#465·#475) · uow(#240~#246·#374·#376·#476·#566) · adapter(#460·#319·#349~#351 등) | ○ — rule-owner-map 총 83 |
| 23 | check-event-publish.py (607행) | 사실(이벤트) 발행·구독 백스톱 (D40·D59) | 16규칙: #7 응용층 import 넷 · #96 driving 잎 · #271 과거형 이름 · #279/#280 핸들러=유스케이스·어휘 번역 · #502~#504 published_event/ 표면 · #507/#508 구독·라우터 표 | ○ — rule-owner-map 총 16 |
| 24 | check-broker-contract.py (454행) | framework/broker/{internal,external} 축(D59) 백스톱 | 17규칙: #442~#444 celery.py·autodiscover 규율 · #518 업무 어휘 0 · #520 발행 뒤 걱정 금지 · #521/#523~#525/#527~#529 internal 브로커 구독표·발행·단일 인스턴스 | ○ — rule-owner-map 총 17 |
| 25 | check-missable-entrance.py (442행) | «놓칠 수 있는 입구» 백스톱 (D26·D53·D49) | 14규칙: #172~#175·#179~#181 cron_job 자리·껍데기·멱등은 유스케이스 · #451 답할 수 있으면 response · #512·#514 webhook 이름·도메인 예외 응답 | ○ — rule-owner-map 총 14 |
| 26 | check-naming.py (545행) | 이름 규율 백스톱 (D9·D21·D33·D41) | 32규칙: #28 약어 금지 · #30/#33/#34 접두·접미·스코프 · #36 정도 낱말 · #41/#43 패턴 낱말 · #87/#97 composition import · #118·#148·#169·#247·#309 등 + admin 가족(#343 이관) | ○ — rule-owner-map 총 32 |
| 27 | check-business-vocabulary.py (605행) | 업무 어휘·framework 격리 백스톱 (D24·D38·D47) | 61규칙: 구조(#393·#35·#19·#395·#396·#398·#401·#423·#620·#428·#434) · 이름(#402~#417·#584) · 격리(#46·#47·#52·#587·#615~#617·#426) · 계약(#585·#604·#606·#607·#618·#619) · test(#53·#425) | ○ — rule-owner-map 총 61 (#628 어휘 정의는 business_vocab.py 소유) |

## 2. 보조 모듈 6종

| 스크립트 | 역할 | 검사 대상 | 규칙 대응 기록 유무 |
|---|---|---|---|
| checker_registry.py (63행) | registry 27종 로스터 «단일 출처» — 순서 고정 튜플 + AUTO 플래그 + import 시 자기 검증 | (검사 안 함 — 데이터) | 해당 없음 (commands/dddjango.md 절 참조 명기) |
| registry_gate.py (224행) | 27종 전체 실행 «판정 차분» 게이트 — 이번 런이 위반을 «늘렸는가»만 판정 | (검사기 오케스트레이션) | 해당 없음 (#488 등은 설명 인용) |
| checker_target.py (75행) | 27종 공용 TARGET 호출 계약 — BC 폴더 모양 대상 «소리내어 거절» + 인터프리터 하한 게이트(requires-python 미달 실행 봉인) | (호출 계약) | 해당 없음 (#74 정신 인용 · 수기 소유 명기) |
| anchor_diff.py (298행) | scope-render 직접 실행 검사기 5종(registry 2·5·6·15·16번)용 판정 차분(N∖L) 공용 + git 스냅숏·빚 로더·빚 매칭 공용 | (진단 0 — 공용 로직) | 해당 없음 (registry_gate 동형 원리 명기) |
| business_vocab.py (127행) | #628 «업무 어휘» 데이터 모듈 — domain_layer 공개 심볼 토큰 집합 도출 + 불용어 | (진단 0 — standard_tree 와 같은 부류) | ○ — #628 명세, 소비자 8규칙(#47·#52·#372·#463·#518·#562·#587·#617) 명기 |
| standard_tree.py (209행) | 정본 트리(`docs/file_tree.html` 140행)의 기계 가독 사본 — 검사기 19종이 import 하는 유일한 트리 데이터. 손편집 금지(`tree_mirror_check --write` 재생성, `--check` 삼중 동기) | (진단 0 — 데이터) | ○ — #488·#489·#491(칸 유형), houserules final.md 삼중 동기 명기 |

## 3. 등록·게이트 구조 요약

### checker_registry.py — 로스터 단일 출처
- `REGISTRY: tuple[(스크립트명, auto), ...]` 27항목, **순서 고정** = `commands/dddjango.md` «정확한 checker registry와 소유권(순서 고정)» 절의 1~27.
- AUTO 플래그(True)는 API-error 3종뿐 — registry 2번 error-centralization · 5번 openapi-error-declaration · 15번 api-error-controller-contract. positional 기본 호출에 `--error-profile auto` 를 덧붙인다(«프로필 무관 선행 슬라이스» 실행용 — scope 별 정식 selector 렌더는 commands 절차 소유).
- **import 시점 자기 검증**: 로스터 집합 ≡ 같은 폴더의 `check-*.py` 실재 집합, 그리고 `len(REGISTRY) == 27` 을 assert — 산문 목록↔파일 드리프트를 기계가 막는다(검사기를 추가/삭제하면 로스터를 안 고치는 한 import 자체가 죽는다).
- `checker_argv(python, script, target, auto)` 가 표준 호출 argv 를 만든다 — 게이트·판정 도구·fixture 하네스가 같은 로스터·같은 호출형을 소비.

### registry_gate.py — 판정 차분 게이트 (귀속 = N∖L)
실행 흐름:
1. TARGET 검증 — `checker_target.bc_shaped_target_reason()` 으로 BC 폴더 모양 대상을 exit 1 로 거절(조용한 «표준 미채택 clean» 통과 차단).
2. 현재 working tree 를 임시 디렉터리에 비-git 사본으로 복사(`.git`·`.venv`·숨김 디렉터리 전부·build 산출물 제외 — 숨김 디렉터리는 도구·하네스 영역이라 검사 표면이 아님, F-C).
3. git 저장소면 `--anchor <ref>` **필수** — 앵커는 actor 가 고르지 않는다(라운드=대장 앵커·파이프라인=build-start 앵커). **앵커=HEAD ∧ clean 이면 exit 1**(「커밋 뒤 게이트」로 판정을 비우는 우회 차단). 앵커를 `git archive` 스냅숏으로 풀어 둔다.
4. 앵커 스냅숏·현재 사본 **양쪽**에서 로스터 27종 전부를 순서대로 실행. stdout+stderr 에서 `[#N] …` 형태 진단 라인만 정규식으로 수집, 절대경로 echo·라인번호를 정규화(경로 «파싱»은 하지 않음). 검사기가 red 인데 진단 라인 파싱 0이면 그 검사기 몫을 합성 귀속으로 남긴다(fail-closed).
5. 추가로 양쪽 스냅숏에 «파싱 불가 파일 pre-scan» — 이 인터프리터로 `ast.parse` 실패하는 파일을 합성 진단으로 넣어, 검사기의 SyntaxError→침묵 스킵(fail-open)을 차분 원리로 봉인(F-A).
6. 판정: 귀속 = N∖L. **귀속 있으면 exit 2, 0이면 exit 0** — 단 «귀속 0 ≠ 전체 clean»으로, legacy 잔존(L∩N)과 해소(L∖N)는 exit 에 안 들어가되 검사기별 집계로 항상 보고(침묵 금지). `--legacy-debt-file` 의 사용자 승인 목록(`#<규칙> <부분문자열>`)에 맞는 귀속은 exit 에서 빼되 «빚» 절로 반드시 보고.
7. 비-git TARGET 은 fail-closed — 차분 불능이므로 현재 위반 전량을 귀속으로 본다.

### 검사기 쪽 차분 — anchor_diff.py
- registry_gate(로스터 전체 차분)와 **같은 N∖L 원리**를 scope-render 직접 실행 계열 5종(registry 2·5·6·15·16번 = error-centralization·openapi-error-declaration·context-isolation·api-error-controller-contract·composition-root)에 검사기 내부 `--anchor` 옵션으로 제공 — full-tree/전역 슬라이스 검사기가 brownfield 잔존 위반으로 신규 산출물까지 막던 문제(S3-r2″ 레인 B 유효 정지)의 해소. `--anchor` 미지정이면 관여하지 않는다(현행 동작 보존).
- registry_gate 는 이 모듈의 git 헬퍼·앵커 스냅숏·빚 로더·빚 매칭을 import 해 같은 구현을 공유한다(복제 통합).

### 공용 호출 계약 — checker_target.py
- 27종 전부가 이 모듈을 거친다: ⑴ TARGET 은 저장소 루트(application/ 의 부모)여야 하며 BC 폴더·application/ 자체를 주면 소리내어 거절 ⑵ 대상 저장소의 `requires-python` 보다 낮은 인터프리터 실행을 봉인(3.12+ 문법 파일의 침묵 clean 오판 차단).

## 4. codex 판 scripts 대조

- 경로: `/Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango/scripts/`
- 파일 수: **33 : 33 일치** (파일명 목록 동일).
- `diff -q dddjango/scripts codex-dddjango/skills/dddjango/scripts` → **차이 0건, exit 0**.
- `cmp` 표본 5건(check-composition-root · check-error-centralization · checker_registry · registry_gate · standard_tree) → **전부 byte-identical**.
- inode 가 다르다(예: check-naming.py 1585378 vs 1585311) — 심볼릭/하드 링크가 아닌 **실사본 미러**이며, 유일하게 mtime 이 다른 `check-composition-root.py`(2026-08-17 22:47 개정)까지 양쪽에 동기돼 있다.
- 결론: **codex 미러 완전 일치**.

## 5. 관찰 사항

1. **규칙 대응 기록률 25/27** — 검사기 대부분이 docstring 에 담당 규칙을 rule-owner-map/트리 개정 명세 번호(`#nnn`)나 스킬 `§` 로 명기하는 관례(「담당 규칙 (rule-owner-map · 총 N)」 정형구)가 확립돼 있다. 예외 2종은 §1 표의 «규칙 대응 미기록» — check-response-schema-bypass(가드 #74·#78 외에 주 규칙 근거 무기록), check-transient-overmapping(maj1 회귀 ID 뿐).
2. **오류 가족 4종만 영어 docstring** — check-error-centralization·check-openapi-error-declaration·check-api-error-controller-contract·check-response-schema-bypass. 이 중 3종이 AUTO(profile 선택형)이고, 규칙 대응 미기록 1종(response-schema-bypass)도 이 가족이다. 나머지 23종은 한국어 «결정적 백스톱» docstring 관례로 통일돼 있다.
3. **#487 순서 긴장(관찰)** — check-layer-skeleton docstring 은 「이 검사는 다른 모든 검사보다 먼저 돌고, 걸리면 나머지를 돌리지 않는다(#487)」라 하나, 로스터 상 위치는 4번이고 registry_gate 는 단락(short-circuit) 없이 27종 전부를 항상 실행한다. #487 의 «먼저·중단» 집행은 commands 절차(라운드/파이프라인 호출 순서) 소유로 보이나, 게이트 코드에는 그 흔적이 없다 — 규정↔구현 대응을 확인할 지점.
4. **데이터·로직 분리 관례** — 트리 «값»은 standard_tree.py(기계 사본·검사기 19종 소비), 업무 어휘 «값»은 business_vocab.py 하나로 모으고 검사기엔 경로 문자열을 다시 적지 않는다(드리프트 봉쇄, T61 ⓑ). 정본은 `docs/file_tree.html`(140행)과 houserules final.md — 삼중 동기는 `workspace/tools/tree_mirror_check.py` 가 지킨다.
5. **규모 분포** — 오류 가족이 압도적으로 크다(api-error 6,891행 · error-centralization 4,692행 · openapi 3,426행). 27종 합계 약 29,000행, 최소는 check-common-container 117행.
