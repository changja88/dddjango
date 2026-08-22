# T3 검수표 — implementation-django-web-final

- 원문: `dddjango/skills/implementation-django-web/references/final.md` (424행 · 센서스 좌표와 일치 — 드리프트 0)
- spec: `workspace/eval/t3/specs/implementation-django-web-final.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-django-web-final.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)
- 규모: REF 12절 · 블록 114 · Work 128(발주서 센서스 129 — 차이 1건은 §1 대사 참조)

## 1. census 대사

| 절 | 헤딩 | 발주서 규범 수 | spec Work 수 | 판정 |
|---|---|---|---|---|
| s001 | 머리말(Django Web 구현 가이드) | 2 | 2 | 일치 |
| s002-1 | §1 책임 범위와 handoff | 12 | 12 | 일치 |
| s003-2 | §2 TemplateView, Generic CBV, FBV 선택 | 11 | 11 | 일치 |
| s004-3 | §3 Context 준비와 표시 값 | 10 | 10 | 일치 |
| s005-4 | §4 Templates, base template, includes/components | 15 | 14 | **불일치 15→14** |
| s006-5 | §5 Static files, CSS, JavaScript | 10 | 10 | 일치 |
| s007-6 | §6 Web forms와 POST flow | 7 | 7 | 일치 |
| s008-7 | §7 HTMX fragment와 AJAX | 6 | 6 | 일치 |
| s009-8 | §8 CSRF, XSS, security setting | 12 | 12 | 일치 |
| s010-9 | §9 View auth와 permission | 6 | 6 | 일치 |
| s011-10 | §10 Render acceptance checks | 14 | 14 | 일치 |
| s012-11 | §11 서버렌더 에러 처리 | 24 | 24 | 일치 |
| **합계** | — | **129** | **128** | 차 1 |

**불일치 절 사유 (s005-4 — 1건)**

- 센서스 15 ↔ spec 14. §4 선두 문단(113행) 첫 문장 «Template은 presentation과 presentation-related branching을 맡는다»는 §1 말미(35행) «template은 presentation과 presentation-related branching만 담당한다»의 **문서 내 재진술**이다(센서스 restate 열 `Y:implementation-django-web-final/s002-1` · 비고 «템플릿 책임 규칙이 §1·skill s004와 3중»과 동일 인식).
- 판정: **센서스 15가 문장 계수로는 옳고, spec 14가 Work 계수로 옳다.** 센서스는 문장 단위 전수 계수라 사본 문장도 세지만, 이관 규약 §15는 «정본 1곳만 Work 승격 + 사본 블록에 `djr:restates`»를 명령한다. 정본은 §1 b10(책임 배분 선언의 원소재 — «만 담당한다» 한정 표지 보유)으로 잡고, §4 b1 은 restates 로 연결한 뒤 그 블록 고유 규범(가격 계산·상태 전이·permission policy·복잡한 data selection·hidden database work 의 template 배치 금지) 1건만 승격했다.
- 나머지 11절은 전 절 일치(과소·과대 산정 없음). 특히 발주서 비고가 예고한 보수 계수 지점(§2 «적합하다» 권고 1 · §1 스코프 선언 2 · §6 validation order 사실 진술 제외 · §7 정의문 제외 · §11 펜스 사이 산문 1)은 모두 예고대로 반영해 일치했다.

## 2. 배선 근거 표 (전 규범 128)

| # | 절/블록 | class | Work label | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b1 | Obligation | 모델·ORM·마이그레이션·트랜잭션·서비스 일반 구현의 implementation-django 소유 | — | `agent-discipline-reviewer` | ①문면 «`implementation-django` 스킬이 소유한다» 소유 위임 명시 · ②27종 docstring 에 문서 소유 판정 술어 없음 · ③P0 E09 머리말 행 ③백스톱 «불명» — §16 위임 기본값(implementation-* → discipline-reviewer) |
| 2 | s001/b1 | Obligation | REST API 계약·Ninja 구현의 architecture-api·implementation-django-ninja 기준 준거 | — | `agent-design-review-api`, `agent-discipline-reviewer` | ①문면이 두 스킬을 직접 지정(명시 문면 우선) — architecture-api 축은 §16 표 design-review-api, implementation-django-ninja 축은 implementation-* 기본값 · ②check-api-error-controller-contract·check-openapi-error-declaration 은 선택 controller/operation 분석이라 «어느 스킬 기준을 따르나» 판정은 비커버 |
| 3 | s002-1/b1 | Obligation | 서버 렌더링 웹 화면 구현의 implementation-django-web 담당 | — | `agent-discipline-reviewer` | ①스코프 선언 «담당한다»(P0 보수 포함 2건 중 첫째) · ②로스터 27종에 문서 관할 판정 술어 없음 — 위임 기본값 |
| 4 | s002-1/b1 | Obligation | 포함 범위 열거의 스코프 한정 | — | `agent-discipline-reviewer` | ①문면 «포함 범위는 …다» 열거(P0 보수 포함 둘째) · 검사기 비커버 — 위임 기본값 |
| 5 | s002-1/b2 | Obligation | 해당 상황의 타 reference·skill 이관 의무 | — | `agent-discipline-reviewer` | ①의무 표지 «넘긴다» · ②이관 판정 술어는 27종 docstring 어디에도 없음 — 위임 기본값 |
| 6 | s002-1/b4 | Obligation | REST resource·HTTP status·Problem Details·OpenAPI 계약의 architecture-api 이관 | — | `agent-design-review-api` | ①문면이 architecture-api 를 직접 지정 — §16 표 architecture-api → design-review-api(명시 문면·기본값 합치) |
| 7 | s002-1/b5 | Obligation | Django Ninja Router/Schema/API 구현의 implementation-django-ninja 이관 | — | `agent-discipline-reviewer` | ①문면이 implementation-django-ninja 지정 · implementation-* 기본값(동일 귀착) |
| 8 | s002-1/b6 | Obligation | 모델·QuerySet·Manager·migration·transaction 의 implementation-django 이관 | — | `agent-discipline-reviewer` | ①문면 지정 · ②check-db-table·check-transaction-boundary 는 표준 트리 driven_layer/application_layer 산출물 축이라 «어느 스킬로 넘기나» 판정은 비커버 — 기본값 |
| 9 | s002-1/b7 | Obligation | DB locking·isolation·index·rollout/backfill 의 architecture-db 이관 | — | `agent-design-review-db` | ①문면이 architecture-db 지정 — §16 표 architecture-db → design-review-db |
| 10 | s002-1/b8 | Obligation | pytest fixture·test double·테스트 mechanics 의 implementation-test 이관 | — | `agent-discipline-reviewer` | ①문면 지정 · ②check-test-config 는 pytest↔settings 바인딩·test/ 구조(#383~#392) 축이라 이관 판정 비커버 — implementation-* 기본값 |
| 11 | s002-1/b9 | Obligation | 도메인 상태 전이·정책·불변식의 architecture-ddd 선결정 | — | `agent-design-review-ddd` | ①문면 «화면 전에 도메인 규칙 결정이 필요할 때» = 설계 시점 — §16 표 architecture-ddd 설계 시점 행(design-review-ddd) |
| 12 | s002-1/b10 | Prohibition | 웹 view·template 의 domain behavior 비소유 | — | `agent-discipline-reviewer` | ①금지 표지 «소유하지 않는다» · ②check-domain-model **#257 확정 신호는 «응용·입구의 속성 접근 후 메서드 호출»(루트 우회)** 로 domain_layer 밖을 겨누지만, 판정 스캔이 BC `application_layer` 한정(`_check_application_side`)이고 표준 트리 driving_layer 칸은 api/·webhook/·open_host_service/·cron_job/·event_subscription/ 뿐이라(standard_tree.py 8~37행) 서버렌더 view 는 **트리 칸 부재로 대상 집합 밖**이다. 규범 폭(view·template 의 domain behavior 소유 일반 금지)도 신호보다 넓다 · check-business-vocabulary 는 framework/ 어휘 축이라 template 축 비커버 — 기본값 |
| 13 | s002-1/b10 | Obligation | view 의 조합 책임 한정(request handling·auth/permission·form/context orchestration·service 호출·rendering) | — | `agent-discipline-reviewer` | ①문면 «조합한다» · ②check-usecase-dto-placement #210(컨트롤러는 result 만 보고 응답 구성)은 표준 트리 driving_layer/api 축이라 서버렌더 view 비커버 — 기본값 |
| 14 | s002-1/b10 | Obligation | template 의 presentation·presentation-related branching 한정 담당 | — | `agent-discipline-reviewer` | ①한정 표지 «만 담당한다» · 검사기 비커버 — 기본값. §4 선두(s005-4/b1)가 같은 규범을 재진술하므로 §15 «정본 1곳» 규율에 따라 이 블록을 정본으로 채택 |
| 15 | s003-2/b1 | Permission | 읽기 전용·context 준비 주작업 페이지의 TemplateView 적합 | — | `agent-discipline-reviewer` | ①권고 표지 «적합하다»(P0 보수 포함 1건) — 강제가 아니라 허용 · 검사기 비커버 — 기본값 |
| 16 | s003-2/b1 | Obligation | 일반 CRUD·form flow 보일러플레이트의 Generic CBV 사용 | — | `agent-discipline-reviewer` | ①의무 표지 «사용한다» · 검사기 비커버 — 기본값 |
| 17 | s003-2/b1 | Obligation | 명시성이 앞서는 custom flow 의 FBV 선택 | — | `agent-discipline-reviewer` | ①조건 표지 «더 명시적이면 …선택한다» · 검사기 비커버 — 기본값 |
| 18 | s003-2/b4 | Obligation | read-only page — TemplateView·context_data 표시 값 준비 | — | `agent-discipline-reviewer` | ①표 행 권장+주의(행당 1규범 계수 규약) · 검사기 비커버 — 기본값 |
| 19 | s003-2/b5 | Obligation | 목록/상세 — ListView/DetailView·relationship traversal 의 select_related/prefetch_related 검토 | — | `agent-discipline-reviewer` | ①표 행 · ②N+1·query shape 판정 검사기는 로스터에 없음(check-db-table 은 모델 파일·db_table 축) — 기본값 |
| 20 | s003-2/b6 | Prohibition | 생성/수정 form — FormView/CreateView/UpdateView·form_valid() 에 durable invariant 몰기 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «몰아넣지 않는다» · ②check-transaction-boundary #195 는 표준 트리 유스케이스의 애그리거트 경유 축이라 Django form_valid() 축은 비커버 — 기본값 |
| 21 | s003-2/b7 | Obligation | method별 custom branch flow — FBV·request 첫 인자·GET/POST 흐름 명시 | — | `agent-discipline-reviewer` | ①표 행 · 검사기 비커버 — 기본값 |
| 22 | s003-2/b8 | Obligation | mixin 이 깊어지는 CBV — 재검토·한 관심사 한정·MRO 복잡 시 FBV/service boundary | — | `agent-discipline-reviewer` | ①표 행 «재검토» · 검사기 비커버 — 기본값 |
| 23 | s003-2/b9 | Obligation | view 의 thin adapter 유지 | — | `agent-discipline-reviewer` | ①의무 표지 «유지한다» · 검사기 비커버 — 기본값 |
| 24 | s003-2/b9 | Obligation | 반복 read logic·성능 민감 query shape 의 selector/QuerySet/Manager 이전 | — | `agent-discipline-reviewer` | ①의무 표지 «옮긴다» · 검사기 비커버 — 기본값 |
| 25 | s003-2/b9 | Obligation | 쓰기 유스케이스·다중 모델 동작의 service/usecase boundary 이전 | — | `agent-discipline-reviewer` | ①의무 표지 «옮긴다» · ②check-transaction-boundary 는 application_layer 내부 쓰기 규율(#195·#4·#197) 축이라 view→service 이전 여부 판정은 비커버 — 기본값 |
| 26 | s004-3/b1 | Prohibition | raw domain object 전달로 template 이 fallback·권한·query shape·domain rule 을 결정하게 만들기 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «만들지 않는다» · ②check-usecase-dto-placement #143/#144(schema_out 은 result 로 구성·도메인 노출 금지)는 ninja schema 축이라 template context 축 비커버 — 기본값 |
| 27 | s004-3/b1 | Obligation | view·context builder·selector·view-model helper 의 화면 언어 이름·표시 값 준비 | — | `agent-discipline-reviewer` | ①의무 표지 «준비한다» · 검사기 비커버 — 기본값 |
| 28 | s004-3/b3 | Obligation | optional field 표시 값의 project-standard placeholder 변환 후 context 적재 | — | `agent-discipline-reviewer` | ①의무 표지 «넣는다» · 검사기 비커버 — 기본값 |
| 29 | s004-3/b4 | Prohibition | template 의 domain field raw fallback 직접 결정 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «직접 결정하지 않는다» · 검사기 비커버 — 기본값 |
| 30 | s004-3/b5 | Obligation | optional display path 의 중앙 영구 테스트 입장 심사 candidate 취급 | — | `agent-discipline-reviewer` | ①문면이 «중앙 영구 테스트 입장 심사»(소유 discipline-tdd) 지목 · ②로스터에 입장 심사 검사기 없음 — §16 기본값 표 discipline-* 행 = discipline-reviewer |
| 31 | s004-3/b5 | Exception | 승인 표시 계약·독자 failure 의 add/update 한정 render/context 경계 확인·구조 규칙만의 테스트 생성 금지 | — | `agent-discipline-reviewer` | ①조건부 한정 «…이면 …하고, 그렇지 않으면 …만들지 않는다» · ②check-test-config 는 pytest 바인딩·test/ 구조 축이라 테스트 «내용» 판정 비커버 — 기본값 |
| 32 | s004-3/b5 | Obligation | None ↔ blank string 공개 구분 여부의 같은 입장 심사 판정 | — | `agent-discipline-reviewer` | ①문면 «같은 심사에서 판정한다» — 판정 주체 명시(P0 E09 §3 비고와 일치) · 기본값 귀착 |
| 33 | s004-3/b6 | Obligation | 목록 화면 relationship 순회의 view/query layer N+1 선검토 | — | `agent-discipline-reviewer` | ①의무 표지 «먼저 검토한다» · ②N+1 판정 술어는 27종 어디에도 없음 — 기본값 |
| 34 | s004-3/b7 | Obligation | template variable 이름의 화면 언어 정합 | — | `agent-discipline-reviewer` | ①의무 표지 «맞춘다» · ②check-naming 은 표준 트리 경로·클래스 이름 축(#28·#30·#33 등)이라 template 변수명 비커버 — 기본값 |
| 35 | s004-3/b7 | Permission | 내부 모델 필드 이름의 그대로 노출 불요 | — | `agent-discipline-reviewer` | ①문면 «노출할 필요는 없다» = 약한 허용 → Permission · 검사기 비커버 — 기본값 |
| 36 | s005-4/b1 | Prohibition | 가격 계산·상태 전이·permission policy·복잡한 data selection·hidden database work 의 template 배치 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «두지 않는다» · 검사기 비커버 — 기본값. 같은 블록 첫 문장(template 책임 한정)은 §1 b10 3번째 Work 의 재진술이라 §15 «정본 1곳만 Work 승격»에 따라 비승격하고 restates 로 연결 |
| 37 | s005-4/b3 | Obligation | template inheritance 채택 시 공통 document structure·navigation·global asset·공통 block 의 base template 배치 | — | `agent-discipline-reviewer` | ①조건부 의무 «…사용하면 …둔다» · ②표준 트리 templates 칸(트리 87~88행)은 check-db-table·check-layer-skeleton 의 경로 축이고 base template 구성 규칙은 비커버 — 기본값 |
| 38 | s005-4/b4 | Obligation | `{% extends %}` 의 첫 비주석 줄 배치 | — | `agent-discipline-reviewer` | ①의무 표지 «둔다» · 검사기 비커버(27종 중 템플릿 문법 검사 술어 0) — 기본값 |
| 39 | s005-4/b5 | Obligation | block 의 역할 드러나는 이름·block 이름으로 닫기 | — | `agent-discipline-reviewer` | ①의무 표지 «붙이고 …닫는다» · ②check-naming 은 Python 경로·클래스 이름 축이라 template block 이름 비커버 — 기본값 |
| 40 | s005-4/b6 | Obligation | page-specific CSS/JS 의 프로젝트 static convention block opt-in | — | `agent-discipline-reviewer` | ①의무 표지 «opt in 한다» · 검사기 비커버 — 기본값 |
| 41 | s005-4/b8 | Obligation | 반복·동시 변경 UI fragment 의 include/component 분리 | — | `agent-discipline-reviewer` | ①조건부 의무 «…때 분리한다» · 검사기 비커버 — 기본값 |
| 42 | s005-4/b9 | Obligation | include context 의 필요 변수 명시 전달 | — | `agent-discipline-reviewer` | ①의무 표지 «전달한다» · 검사기 비커버 — 기본값 |
| 43 | s005-4/b10 | Prohibition | 짧은 snippet 전부의 include 화 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «만들지 않는다» · 검사기 비커버 — 기본값 |
| 44 | s005-4/b10 | Exception | 재사용이 이해·일관성을 실제로 높일 때만 분리 | — | `agent-discipline-reviewer` | ①한정 표지 «…때만 분리한다» — 앞 금지의 예외 조건 · 검사기 비커버 — 기본값 |
| 45 | s005-4/b12 | Obligation | `{{ variable }}`·`{% tag %}` 안 한 칸 공백 | — | `agent-discipline-reviewer` | ①의무 표지 «둔다»([DCS] 근거) · 검사기 비커버 — 기본값 |
| 46 | s005-4/b13 | Obligation | 복수 template library load 의 알파벳순 유지 | — | `agent-discipline-reviewer` | ①의무 표지 «유지한다» · 검사기 비커버 — 기본값 |
| 47 | s005-4/b14 | Obligation | HTML template indentation 의 프로젝트 관례 준수 | — | `agent-discipline-reviewer` | ①의무 표지 «따르며» · 검사기 비커버 — 기본값 |
| 48 | s005-4/b15 | Obligation | `{% load static %}`·`{% static %}` 사용 | — | `agent-discipline-reviewer` | ①의무 표지 «사용한다» · 검사기 비커버 — 기본값 |
| 49 | s005-4/b16 | Exception | `\|safe`·`mark_safe()` 의 trusted/sanitized·의도·근거 한정 사용 | — | `agent-discipline-reviewer` | ①한정 표지 «…한해 …있을 때만 사용한다» — autoescape 기본(§8)의 예외 조건 · 검사기 비커버(XSS 축 정적 검사 술어 0) — 기본값 |
| 50 | s006-5/b1 | Obligation | static asset 의 기존 pipeline 준수 | — | `agent-discipline-reviewer` | ①의무 표지 «따른다» · 검사기 비커버 — 기본값 |
| 51 | s006-5/b1 | Obligation | app-specific asset 의 앱 근접 배치(프로젝트가 app/static/app_name 구조를 쓰는 경우) | — | `agent-discipline-reviewer` | ①조건부 의무 «…쓰는 경우 …둔다» · ②check-layer-skeleton #490(트리 밖 경로 금지)은 표준 트리 BC 하위를 보는데 이 문장은 «프로젝트 기존 관례»를 전제한 조건부라 트리 폐쇄 축과 대상이 다름 — 기본값(경계 판단은 검수표) |
| 52 | s006-5/b1 | Obligation | shared design-system·global asset 의 기존 shared static 위치 준수 | — | `agent-discipline-reviewer` | ①의무 표지 «따른다» · 검사기 비커버 — 기본값 |
| 53 | s006-5/b3 | Obligation | hardcoded static URL 대신 `{% static %}` 사용 | — | `agent-discipline-reviewer` | ①의무 표지 «사용한다» · 검사기 비커버 — 기본값 |
| 54 | s006-5/b4 | Obligation | page-specific CSS/JS 변경 시 같은 변경에서 rendered template 연결 | — | `agent-discipline-reviewer` | ①의무 표지 «연결한다» · 검사기 비커버 — 기본값 |
| 55 | s006-5/b5 | Obligation | 미참조 page-specific asset 의 unfinished work 판정 | — | `agent-discipline-reviewer` | ①판정 지시 «unfinished work 로 본다» · 검사기 비커버 — 기본값 |
| 56 | s006-5/b6 | Permission | inline script 의 작고 template-local 한정 허용 | — | `agent-discipline-reviewer` | ①허용 표지 «…일 때만 허용한다» · 검사기 비커버 — 기본값 |
| 57 | s006-5/b6 | Prohibition | domain data transformation 의 template JavaScript 배치 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «넣지 않는다» · ②check-business-vocabulary 는 framework/ 파이썬 모듈의 업무 어휘 축(#47·#52)이라 template JS 비커버 — 기본값 |
| 58 | s006-5/b7 | Obligation | STATIC_URL·STATIC_ROOT·STATICFILES_DIRS·storage backend·bundler·manifest hashing 의 기존 설정 준수 | — | `agent-discipline-reviewer` | ①의무 표지 «따른다» · ②check-test-config ⑶ 은 `<project>/settings/` 환경축(#445~#447) 축이라 static 설정 값 축은 비커버 — 기본값 |
| 59 | s006-5/b8 | Obligation | deployment asset resolution·manifest hashing 변경 시 collectstatic 실행·미실행 사유 보고 | — | `agent-discipline-reviewer` | ①의무 표지 «보고한다» · ③P0 E09 §5 행 «collectstatic 실행 또는 미실행 사유 보고 — 보고 의무이지 검사기 지목 아님» 명문 — 기본값 |
| 60 | s007-6/b1 | Obligation | form 의 input shape·presentation error·user-facing validation message 담당 | — | `agent-discipline-reviewer` | ①의무 표지 «담당한다» · 검사기 비커버 — 기본값 |
| 61 | s007-6/b1 | Obligation | durable domain invariant 의 model/service/DB boundary 보장 | — | `agent-discipline-reviewer` | ①의무 표지 «보장되어야 한다» · ②check-transaction-boundary #195/#287 은 표준 트리 유스케이스·리포지토리 쓰기 인자 축이라 «form 밖에서도 보장» 판정은 비커버 — 기본값 |
| 62 | s007-6/b4 | Obligation | `ModelForm.Meta.fields` 의 명시 나열 | — | `agent-discipline-reviewer` | ①의무 표지 «명시적으로 나열한다» · 검사기 비커버(로스터에 Django form AST 술어 0) — 기본값 |
| 63 | s007-6/b5 | Prohibition | `fields = "__all__"`·`exclude` 회피(프로젝트 명시 수용 시 예외) | — | `agent-discipline-reviewer` | ①금지 표지 «피한다» + 명시 수용 예외 조건 · 검사기 비커버 — 기본값 |
| 64 | s007-6/b6 | Obligation | form·model field 공통 input validation 의 custom validator 재사용 검토 | — | `agent-discipline-reviewer` | ①의무 표지 «검토한다» · 검사기 비커버 — 기본값 |
| 65 | s007-6/b7 | Obligation | 일반 web form 의 POST/Redirect/GET 기본 선택 | — | `agent-discipline-reviewer` | ①의무 표지 «기본 선택지로 둔다» · 검사기 비커버 — 기본값 |
| 66 | s007-6/b8 | Obligation | invalid POST 의 form error·입력 값 회복 가능 렌더링 | — | `agent-discipline-reviewer` | ①의무 표지 «렌더링한다» · 검사기 비커버 — 기본값(§11 b3 view-local 재렌더 규범과 같은 축이나 문장 주어가 form 경로라 별도 Work) |
| 67 | s008-7/b1 | Obligation | domain behavior 의 model/service/usecase boundary 배치와 view 의 조합 한정 | — | `agent-discipline-reviewer` | ①의무 표지 «두고 …조합한다»(선행 «HTMX view 는 web adapter다» 정의문은 P0 승계로 비계수) · 검사기 비커버 — 기본값 |
| 68 | s008-7/b3 | Obligation | HTMX fragment template 의 소형 유지·의도적 재사용 시에만 공통 fragment | — | `agent-discipline-reviewer` | ①의무 표지 «유지하고 …둔다» · 검사기 비커버 — 기본값 |
| 69 | s008-7/b4 | Obligation | state-changing HTMX/AJAX 의 non-HTMX POST 동급 auth·permission·CSRF 검증 | — | `agent-discipline-reviewer` | ①의무 표지 «적용한다» · ②check-ninja-boundary-middleware 는 BC driving_layer 자가정의 미들웨어의 전역 등록 축이라 CSRF 검증 적용 여부는 비커버 — 기본값 |
| 70 | s008-7/b5 | Obligation | non-JavaScript fallback 기대 시 progressive enhancement path 유지 | — | `agent-discipline-reviewer` | ①조건부 의무 «…기대하면 …유지한다» · 검사기 비커버 — 기본값 |
| 71 | s008-7/b6 | Obligation | resource contract·status matrix·schema·Problem Details 필요 시 ninja/architecture-api 이관 | — | `agent-design-review-api`, `agent-discipline-reviewer` | ①문면이 implementation-django-ninja·architecture-api 를 직접 지목 — architecture-api 축은 §16 표 design-review-api, ninja 축은 implementation-* 기본값 |
| 72 | s008-7/b7 | Prohibition | HTMX-specific header·response behavior 의 UI contract 취급·domain logic 혼합 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «섞지 않는다» · ②check-business-vocabulary #119(framework 소유 status 열거)는 ninja 오류 경계 축이라 HTMX 헤더 축 비커버 — 기본값 |
| 73 | s009-8/b1 | Obligation | `CsrfViewMiddleware` 유지(좁고 문서화된 예외 부재 시) | — | `agent-discipline-reviewer` | ①의무 표지 «유지한다» · ③P0 E09 §8 «커버»는 Django 내장 `check --deploy` 지목이고 플러그인 27종은 CSRF 미들웨어 축 술어 0 — 기본값 |
| 74 | s009-8/b1 | Obligation | POST form 의 `{% csrf_token %}` 사용 | — | `agent-discipline-reviewer` | ①의무 표지 «사용한다» · 검사기 비커버 — 기본값 |
| 75 | s009-8/b1 | Obligation | state-changing AJAX/HTMX 의 프로젝트 header·form pattern CSRF token 전송 | — | `agent-discipline-reviewer` | ①의무 표지 «보낸다» · 검사기 비커버 — 기본값 |
| 76 | s009-8/b1 | Exception | `@csrf_exempt` 의 대체 보호 명확한 작은 경계 한정 사용 | — | `agent-discipline-reviewer` | ①한정 표지 «…에서만 사용한다» — CsrfViewMiddleware 유지 규범의 예외 조건 · 검사기 비커버 — 기본값 |
| 77 | s009-8/b3 | Obligation | Django template autoescaping 기본 신뢰 | — | `agent-discipline-reviewer` | ①의무 표지 «신뢰한다» · 검사기 비커버 — 기본값 |
| 78 | s009-8/b4 | Prohibition | untrusted value 의 JavaScript context 직접 주입 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «주입하지 않는다» · 검사기 비커버 — 기본값 |
| 79 | s009-8/b4 | Obligation | 프로젝트 escaping pattern 준수 | — | `agent-discipline-reviewer` | ①의무 표지 «따른다» · 검사기 비커버 — 기본값 |
| 80 | s009-8/b5 | Obligation | `CSRF_COOKIE_HTTPONLY` 의 프로젝트 요구·Django caveat 병행 고려 | — | `agent-discipline-reviewer` | ①의무 표지 «함께 고려한다» · 검사기 비커버 — 기본값 |
| 81 | s009-8/b6 | Obligation | security·session·CSRF·auth·message·frame option 미들웨어 ordering 보존 | — | `agent-discipline-reviewer` | ①의무 표지 «보존한다» · ②check-ninja-boundary-middleware 는 settings.MIDDLEWARE 항목 중 BC driving_layer 경로만 적출(순서 축 아님) — 비커버, 기본값 |
| 82 | s009-8/b7 | Obligation | security setting 변경 시 `manage.py check --deploy` 실행·미실행 사유 보고 | — | `agent-discipline-reviewer` | ③P0 E09 §8 행 ③백스톱 «커버» — 다만 지목 대상이 Django 내장 결정적 검사이고 registry 개체(dddjango/scripts/check-*.py 27종) 밖이라 enforcedBy 불가 · 보고 의무 이행 판정은 §16 기본값 |
| 83 | s009-8/b8 | Prohibition | raw SQL 의 user input 보간 금지·parameterized query 사용 | — | `agent-discipline-reviewer` | ①금지 표지 «보간하지 말고» · 검사기 비커버(SQL 문자열 축 술어 0) — 기본값 |
| 84 | s009-8/b8 | Obligation | QuerySet/Manager 의 implementation-django·DB 성능 설계의 architecture-db 이관 | — | `agent-discipline-reviewer`, `agent-design-review-db` | ①문면이 두 문서를 직접 지목 — implementation-django 축은 implementation-* 기본값, architecture-db 축은 §16 표 design-review-db |
| 85 | s010-9/b1 | Obligation | protected page 의 render 전 view-level auth·permission 확인 | — | `agent-discipline-reviewer` | ①의무 표지 «확인한다» · 검사기 비커버(27종에 view 인가 술어 0) — 기본값 |
| 86 | s010-9/b1 | Prohibition | template 의 authorization decision 비소유(표시 숨김만 허용) | — | `agent-discipline-reviewer` | ①금지 표지 «소유하지 않는다» · 검사기 비커버 — 기본값 |
| 87 | s010-9/b3 | Obligation | FBV 의 프로젝트 표준 `login_required`·`permission_required`·method decorator 사용 | — | `agent-discipline-reviewer` | ①의무 표지 «사용한다» · 검사기 비커버 — 기본값 |
| 88 | s010-9/b4 | Obligation | CBV 의 `LoginRequiredMixin`·`PermissionRequiredMixin`·프로젝트 표준 mixin 사용 | — | `agent-discipline-reviewer` | ①의무 표지 «사용한다» · 검사기 비커버 — 기본값 |
| 89 | s010-9/b5 | Obligation | domain rule 결합 permission policy 의 architecture-ddd·application service boundary 선결정 | — | `agent-design-review-ddd` | ①문면이 architecture-ddd 를 지목하고 «먼저 결정한다» = 설계 시점 — §16 표 architecture-ddd 설계 시점 행(design-review-ddd) |
| 90 | s010-9/b6 | Obligation | unauthorized·forbidden·redirect 동작의 프로젝트 표준·테스트 기대 정합 | — | `agent-discipline-reviewer` | ①의무 표지 «맞춘다» · 검사기 비커버 — 기본값 |
| 91 | s011-10/b1 | Obligation | web 구현 완료 시 실행한 검증만 보고 | — | `agent-discipline-reviewer` | ①의무 표지 «보고한다» · ②로스터 27종은 산출물 정적 검사라 «보고 정직성» 판정 비커버 — 기본값 |
| 92 | s011-10/b1 | Obligation | render/browser/collectstatic/security check 미실행의 미실행 명시 | — | `agent-discipline-reviewer` | ①의무 표지 «명시한다» · 검사기 비커버 — 기본값 |
| 93 | s011-10/b1 | Obligation | test-shaped 증거의 비자동의무·중앙 입장 심사 candidate 또는 add/update 뒤 recipe 취급 | — | `agent-discipline-reviewer` | ①문면이 «중앙 입장 심사»(discipline-tdd 소유) 지목 · ②입장 심사 검사기 없음 — §16 기본값 표 discipline-* 행 |
| 94 | s011-10/b1 | Exception | 승인 계약·독자 failure 보호 테스트 허용·`reuse/reject` 의 신규 test artifact 생성 금지 | — | `agent-discipline-reviewer` | ①조건부 허용+금지 «허용하되 …만들지 않는다» · ②check-test-config 는 test/ 구조 축이라 artifact 생성 «승인 여부» 비커버 — 기본값 |
| 95 | s011-10/b4 | Obligation | template/context 변경 — add/update 뒤 render test·test client response·context assertion과 미실행 사유 보고 | — | `agent-discipline-reviewer` | ①검증 행렬 행(행당 1규범 계수 규약) · 검사기 비커버 — 기본값 |
| 96 | s011-10/b5 | Obligation | optional display value — 승인 None/blank/missing path 의 context/render assertion·raw fallback 은 unfinished | — | `agent-discipline-reviewer` | ①검증 행렬 행 · §3 b5 입장 심사 규범과 같은 축이나 여기는 증거·gap 기준을 운반 — 기본값 |
| 97 | s011-10/b6 | Obligation | static CSS/JS 변경 — rendered HTML static reference·참조 경로 존재·미참조 시 unfinished | — | `agent-discipline-reviewer` | ①검증 행렬 행 · 검사기 비커버 — 기본값 |
| 98 | s011-10/b7 | Obligation | form 변경 — GET·valid POST·invalid POST·redirect·form error assertion과 CSRF/auth 미확인 시 residual risk | — | `agent-discipline-reviewer` | ①검증 행렬 행 · 검사기 비커버 — 기본값 |
| 99 | s011-10/b8 | Obligation | HTMX 변경 — fragment response·method/auth/permission/CSRF·redirect/header 증거와 API-like 계약 시 handoff | — | `agent-discipline-reviewer`, `agent-design-review-api` | ①검증 행렬 행 + gap 열이 implementation-django-ninja/architecture-api handoff 를 지목 — API 계약 축은 §16 표 design-review-api 병기 |
| 100 | s011-10/b9 | Obligation | service 예외 처리(§11) — 도메인 예외 200 폼 재렌더·미식별/영구 handler500·transient 503+Retry-After·HTMX 에러 fragment 증거 | — | `agent-discipline-reviewer` | ①검증 행렬 행이 §11 을 참조 좌표로 지목 · ②검사기 축(transient-overmapping·synthetic-infra-exc)은 §11 정본 규범이 지고 이 행은 «증거·gap 기준»이라 리뷰어 판정 — 기본값 |
| 101 | s011-10/b10 | Obligation | security setting 변경 — `check --deploy` 또는 project-specific security check·미실행 사유 | — | `agent-discipline-reviewer` | ①검증 행렬 행 · ③§8 «커버» 지목은 Django 내장 검사라 registry 밖 — 기본값(§8 b7 과 동일 판단) |
| 102 | s011-10/b11 | Obligation | visible UI 변경 — browser check·screenshot·render test 증거와 browser 미실행의 실행 보고 금지 | — | `agent-discipline-reviewer` | ①검증 행렬 행(기대 증거 의무 + gap 열 허위 보고 금지) · 검사기 비커버 — 기본값 |
| 103 | s011-10/b12 | Obligation | 완료 보고의 실행 명령·테스트 대상·실패/미실행 분리 기재 | — | `agent-discipline-reviewer` | ①의무 표지 «분리해 적는다» · 검사기 비커버 — 기본값 |
| 104 | s011-10/b12 | Prohibition | 직접 커버 확인 없는 넓은 완료 주장 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «주장하지 않는다» · 검사기 비커버 — 기본값 |
| 105 | s012-11/b1 | Obligation | service/usecase 예외의 출처 분류 — 도메인 예외는 view-local 변환·인프라/프레임워크/미식별은 비포획 전파 | — | `agent-discipline-reviewer` | ①문면 «출처로 분류해 처리 자리를 가른다» · ②check-synthetic-infra-exc ⑵#129 는 driven 층 catch-all 번역 축이라 view 층 분류 규범 비커버 · ③P0 E09 §11 «커버»는 transient-overmapping·synthetic-infra-exc·error-centralization 대응을 뜻하고 이 분류 문장은 미대응 — 기본값 |
| 106 | s012-11/b1 | Prohibition | «사용자가 행동을 바꿔 풀 수 있나» 의 1차 분류 기준 사용 금지(2차 신호 한정) | — | `agent-discipline-reviewer` | ①금지 표지 «1차 분류 기준이 아니라 …2차 신호다» · 검사기 비커버 — 기본값 |
| 107 | s012-11/b1 | Prohibition | 이 절의 서버렌더 HTML 경로 한정 소유·JSON API 오류 표현 혼합 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «섞지 않는다» · ②check-error-centralization 은 profile-gated(dddjango-code-json)이고 대상이 canonical FrameworkErrorSchema 모듈·inventory 라 HTML 경로 혼합 판정은 소스 선택 밖 — 기본값 |
| 108 | s012-11/b3 | Obligation | 도메인 예외의 narrow except 포획·폼 재렌더(입력 보존·messages.error·200·PRG) | — | `agent-discipline-reviewer` | ①의무 표지 «재렌더한다·싣는다» · ②check-api-error-controller-contract 는 ninja controller 오류 매핑 축(JSON profile)이라 HTML view-local 재렌더 비커버 — 기본값 |
| 109 | s012-11/b3 | Prohibition | `except Exception` 광범위 catch 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «금지다» + 문면이 `discipline-cleancode` 구체적 예외 처리 지목 · ②check-synthetic-infra-exc ⑵#129 는 «driven 층»의 catch-all 뒤 새 예외 생성 형태만 차단이라 view(driving) 층 광범위 catch 는 대상 밖 — discipline-* 기본값 |
| 110 | s012-11/b4 | Prohibition | 사용자 에러의 `handler500` 회부 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «보내지 않는다»(나머지 두 문장은 빈 Context·시그니처 사실 서술이라 비계수) · 검사기 비커버 — 기본값 |
| 111 | s012-11/b5 | Obligation | 시스템 에러(미식별·영구장애)의 중앙 `handler500` 처리 — view 비포획 전파 | — | `agent-discipline-reviewer` | ①문면 «view 가 잡지 않고 전파하면» 처리 자리 지정 · ②check-transient-overmapping 은 handler 의 통째 retryable 매핑 축이라 handler500 경로 지정은 비커버 — 기본값 |
| 112 | s012-11/b5 | Obligation | custom handler view 의 `request` 인자 전용·`HttpResponseServerError` 반환 | — | `agent-discipline-reviewer` | ①의무 표지 «받고 …반환한다» · ②check-public-surface-annotation 은 «첫 대입 타입»(#493) 축이라 시그니처 «인자 구성» 판정은 비커버 — 기본값 |
| 113 | s012-11/b5 | Prohibition | `500.html` 의 프로젝트 단일 배치(view 별 에러 페이지 금지) | — | `agent-discipline-reviewer` | ①금지 표지 «만들지 않는다» · ②check-layer-skeleton #490(트리 밖 경로) 은 BC 하위 폐쇄 축이라 프로젝트 템플릿 개수 판정 비커버 — 기본값 |
| 114 | s012-11/b6 | Obligation | 재시도로 해소되는 경합의 `process_exception` 미들웨어 retryable(503+`Retry-After`) 매핑 | — | `agent-discipline-reviewer` | ①문면 «미들웨어가 유일한 중앙 자리다» · ②check-transient-overmapping 은 «분기 없는 통째 503» 차단 축이라 매핑 자리 지정은 비커버 · check-ninja-boundary-middleware 는 BC driving_layer 자가정의 미들웨어의 전역 자가등록 축이라 프로젝트 레벨 미들웨어와 무관 — 기본값 |
| 115 | s012-11/b6 | Obligation | retryable 판정의 Django HTML 미들웨어 private predicate 배치 | — | `agent-discipline-reviewer` | ①의무 표지 «둔다»(소비자 유일 조건 명시) · ②framework 승격 축 검사기(check-business-vocabulary #19·#395)는 표준 트리 framework/ 자식 구성만 보고 predicate 소유 자리는 비커버 — 기본값 |
| 116 | s012-11/b6 | Prohibition | predicate 의 승인 신호·SQLSTATE 한정 인식과 예외 원문·SQL·secret 의 응답·로그 노출 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «되돌려 주지 않는다» · ②check-transient-overmapping AND 조건 2 는 «영구장애 구별 분기 부재»만 보고 신호 목록·노출 금지는 비커버 — 기본값 |
| 117 | s012-11/b6 | Prohibition | 명시 `__cause__` 우선·`__suppress_context__` 거짓일 때만 `__context__` 추적(`from None` 원인 복원 금지) | — | `agent-discipline-reviewer` | ①금지 표지 «되살리지 않는다» · ②check-transient-overmapping 은 `__cause__`/`__context__` 접근을 «분기 있음»의 신호로만 읽고 추적 순서 규범은 비커버 — 기본값 |
| 118 | s012-11/b6 | Prohibition | 영구장애의 `None` 반환·handler500 전파 — OperationalError 클래스 통째 503 금지 | `check-transient-overmapping.py` (**부분 커버**) | `agent-discipline-reviewer` (주) | ②docstring «영구장애 변종을 구별하는 분기 없이 클래스 통째를 retryable status(503/409)로 무조건 매핑한 정확한 형태만 차단»가 금지형(AND 조건 2·3)과 대응하나 **AND 조건 1(핸들러 판별)의 발견 신호는 `@*.exception_handler(OperationalError\|DatabaseError)` 데코 또는 `exc: OperationalError\|DatabaseError` 어노테이션뿐**(구현 `_is_target_handler` 105~117행 — `process_exception`/middleware 언급 0)이고 docstring 이 대상을 «API 경계 … 핸들러»로 선언한다. **이 규범의 주형인 무어노테이션 `def process_exception(self, request, exception)` 은 신호 밖 → 기계 침묵**(docstring 이 «register-only+무어노테이션 핸들러는 일부러 잡지 않는다 — 저-recall» 로 자인). 실제 차단되는 것은 어노테이션형 변종뿐이고, 스캔 범위는 경로 무관 프로덕션 `*.py` 전량이라 HTML 경계에서도 그 변종은 잡힌다(= 배선 유지 근거) · ③P0 E09 §11 ③백스톱 «커버» 지목은 절 단위 대응 판정 · 저-recall 잔여 전부(무어노테이션 미들웨어 주형 포함)는 discipline-reviewer 몫 |
| 119 | s012-11/b6 | Prohibition | 미들웨어의 503 반환 한정·도메인 폼 `render` 금지(폼 재렌더는 view-local 몫) | — | `agent-discipline-reviewer` | ①금지 표지 «render 하지 않는다» · ②check-transient-overmapping 은 status 반환 형태만 보고 응답 본문 종류(폼 렌더)는 비커버 — 기본값 |
| 120 | s012-11/b6 | Prohibition | 공유 경계 2 이상일 때만 `framework/django/` 승격 검토·선행 공통 추상화 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «만들지 않는다» · ②check-business-vocabulary 는 framework/ 자식 구성(#395)·기술 축(#19) 집행이고 check-common-container 는 `application/framework\|common` 컨테이너 레벨 축이라 «승격 시점» 판정은 어느 쪽도 비커버 — 기본값 |
| 121 | s012-11/b7 | Prohibition | 계산된 transient 의 인프라 예외 합성 금지 — 도메인 transient 마커 raise·미들웨어 타입 매핑 | `check-synthetic-infra-exc.py` | `agent-discipline-reviewer` | ②docstring ⑴ «driven 경계가 계산된 transient/경합을 신호하려고 raw 인프라 DB 예외(OperationalError·DatabaseError·IntegrityError)를 from 없이 새로 생성해 raise 한 형태만 차단(ACL-EX2)» — ACL 축 정확 대응 · ③P0 E09 §11 «커버» 지목 3종 중 하나 · 검사기 대상이 `driven_layer` 한정이라 앱(application_layer) 소진 판정 축은 리뷰어 병기 · 문면 말미 «`discipline-houserules` §2» 참조는 P0 특이 발견 3 의 표류 의심 지점(현행 §2 = 충돌 중재/골격) |
| 122 | s012-11/b8 | Prohibition | retryable 판정·응답 표현의 JSON API 경로 공유 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «공유하지 않는다» · ②check-api-error-controller-contract 는 선택된 ninja controller·error-BC 모듈만 분석하므로 HTML 경계의 공유 여부는 소스 선택 밖 — 기본값 |
| 123 | s012-11/b8 | Prohibition | 서버렌더 transient 의 HTML 503 소유·JSON 오류 schema/helper/응답 객체의 HTML 경로 import 금지 | — | `agent-discipline-reviewer` | ①금지 표지 «import 하지 않는다» · ②check-error-centralization 은 canonical FrameworkErrorSchema 모듈·inventory 대응·wire-code 유일성 축이라 HTML 경로의 import 방향은 비커버 · check-context-isolation 은 BC·층 방향 축(#7·#12·#95)이라 profile 간 import 는 대상 밖 — 기본값(도피 아님: 두 docstring 모두 대상 집합을 명시) |
| 124 | s012-11/b9 | Obligation | HTMX 요청의 도메인 에러 fragment swap(전체 `500.html` 금지) | — | `agent-discipline-reviewer` | ①의무 표지 «swap 한다» · 검사기 비커버(HTMX 응답 형태 술어 0) — 기본값 |
| 125 | s012-11/b9 | Obligation | `HX-Request` 분기·에러 fragment(200/422)·HTMX 맥락 시스템 에러/503 의 명세 표면 처리 | — | `agent-discipline-reviewer` | ①의무 표지 «분기해 …내고 …처리한다» · 검사기 비커버 — 기본값 |
| 126 | s012-11/b10 | Obligation | 반복되는 `try → except <DomainError> → render` 의 단일 패턴·CBV `form_invalid()` 통합 | — | `agent-discipline-reviewer` | ①의무 표지 «묶는다» · 검사기 비커버 — 기본값 |
| 127 | s012-11/b10 | Obligation | 다수 도메인 예외의 공통 베이스 단일 except·메시지 매핑 테이블(난립 금지는 HTML 경계 한정) | — | `agent-discipline-reviewer` | ①의무 표지 «쓴다» + 괄호가 적용 범위를 HTML 경계로 한정 · ②반대 규율인 ninja §6.2(concrete catch·직접 mapping 반복)는 check-api-error-controller-contract 소관이며 이 문장의 주어는 HTML 경계라 배선 대상 아님 — 기본값 |
| 128 | s012-11/b13 | Obligation | middleware 테스트의 관찰 응답(503·status header·handler500 pass-through) 검증·private predicate 직접 고정 금지 | — | `agent-discipline-reviewer` | ①문면 «중앙 입장 심사 … mechanics» + «관찰 응답을 검증한다»(펜스 사이 산문 1 — P0 보수 포함) · ②check-test-config 는 pytest↔settings 바인딩·test/ 구조 축이라 테스트 «내용» 판정 비커버 — §16 기본값(discipline-tdd 축도 discipline-reviewer) |

### 2.1 배선 집계

- 전 규범 128건 — 무소유 0(도구 단언 통과).
- **enforcedBy 성립 2건**(둘 다 §11): `check-transient-overmapping.py`(영구장애 분기 없는 통째 503 금지) · `check-synthetic-infra-exc.py`(계산된 transient 의 인프라 예외 합성 금지). 두 건 모두 **검사기+리뷰어 병기** — docstring 이 스스로 저-recall 구간(헬퍼 무조건-True 위장·register-only / `driven_layer` 밖)을 명시하고 그 잔여를 discipline-reviewer 로 넘긴다.
- delegatedTo 분포: `agent-discipline-reviewer` 주(主) · `agent-design-review-api` 4건(머리말 1·§1 표 1·§7 1·§10 1) · `agent-design-review-db` 2건(§1 표 1·§8 1 병기) · `agent-design-review-ddd` 2건(§1 표 1·§9 1).
- **기본값 이탈 근거**: design-review-api/db/ddd 로 간 8건(중복 병기 포함)은 전부 ①문면이 상대 문서(architecture-api·architecture-db·architecture-ddd)를 축자 지목한 경우다(§16 «명시 문면이 기본값에 우선»). architecture-ddd 지목 2건은 둘 다 «화면 전에 …먼저 결정한다»는 **설계 시점** 문면이라 §16 표의 설계 시점 행(design-review-ddd)을 골랐다(구현 시점 행 discipline-reviewer 아님).
- **기본값 도피 방지 점검**: 로스터 27종 docstring 전수 실독 뒤, 이 문서의 규범과 표면이 겹칠 수 있는 8종(`check-transient-overmapping`·`check-synthetic-infra-exc`·`check-error-centralization`·`check-api-error-controller-contract`·`check-ninja-boundary-middleware`·`check-test-config`·`check-transaction-boundary`·`check-layer-skeleton`)을 개별 대조해 **대상 집합이 문면과 어긋나는 경우만** 기본값으로 보냈고, 그 어긋남을 basis 열에 매번 적었다(예: error-centralization 은 profile-gated + 선택 소스, ninja-boundary-middleware 는 BC `driving_layer` 자가등록 축).

## 3. 재진술 유예 (교차 문서 — 전량 spec 제외)

상대 문서 `implementation-django-web-skill`(`dddjango/skills/implementation-django-web/SKILL.md`)은 이번 웨이브 스코프 밖(웨이브 3)이라 **spec `restates` 에 넣지 않고** 여기에 유예 기록한다. 방향 판정은 «SKILL 이 final.md 의 요약 사본»(P0 특이 발견 4 — houserules 가 금지하는 값 복제의 실례)이므로 **정본 = final.md 블록 · 사본 = SKILL 블록**이다. 소급 패스는 SKILL 측 블록에 `djr:restates` → 아래 final 블록을 부착하면 된다.

| # | 내 블록(정본 후보) | 상대 문서/절 | 상대 문면(사본) | 확인 근거 |
|---|---|---|---|---|
| 1 | s002-1/b4 | implementation-django-web-skill/s003 | 13행 «REST 리소스·HTTP 상태·Problem Details·OpenAPI 계약 → `architecture-api`» | 센서스 restate 열 + SKILL 직접 실독 — 위임 6항 1:1 |
| 2 | s002-1/b5 | implementation-django-web-skill/s003 | 14행 «Django Ninja Router/Schema/API 어댑터 구현 → `implementation-django-ninja`» | 동상 |
| 3 | s002-1/b6 | implementation-django-web-skill/s003 | 15행 «모델·QuerySet·Manager·마이그레이션·트랜잭션 → `implementation-django`» | 동상 |
| 4 | s002-1/b7 | implementation-django-web-skill/s003 | 16행 «DB locking·isolation·index·rollout/backfill → `architecture-db`» | 동상 |
| 5 | s002-1/b8 | implementation-django-web-skill/s003 | 17행 «pytest 픽스처·테스트더블·상세 테스트 구현 → `implementation-test`» | 동상 |
| 6 | s002-1/b9 | implementation-django-web-skill/s003 | 18행 «도메인 상태 전이·정책·불변식 → `architecture-ddd`» | 동상 |
| 7 | s002-1/b10 | implementation-django-web-skill/s004 | 22행 «뷰는 얇은 어댑터: 요청 처리·auth/permission·form·context 조율·서비스 호출·응답 렌더링만 (§1)» | 사본이 «(§1)» 좌표를 자칭 — 내 b10 N2 와 열거 일치 |
| 8 | s003-2/b1 | implementation-django-web-skill/s004 | 23행 «TemplateView/Generic CBV/FBV 선택은 흐름 복잡도 기준 … (§2)» | «(§2)» 자칭 — 선택 3문장의 요약 |
| 9 | s003-2/b8 | implementation-django-web-skill/s004 | 23행 후단 «mixin이 깊어지면 재검토 (§2)» | 선택표 마지막 행(49행)의 축자 요약 |
| 10 | s004-3/b1 | implementation-django-web-skill/s004 | 24행 «context에는 표시 값만; 도메인 동작은 서비스/usecase boundary로 분리 (§3)» | «(§3)» 자칭 |
| 11 | s005-4/b1 | implementation-django-web-skill/s004 | 25행 «템플릿은 presentation과 presentation-related branching만 담당 (§4)» | **3중 중복의 셋째 꼭짓점** — 내 b1 은 이미 §1 b10 의 문서 내 사본이라 소급 패스는 §1 정본으로 이어야 한다 |
| 12 | s007-6/b8 | implementation-django-web-skill/s004 | 26행 «web form은 GET·valid POST·invalid POST·redirect·form error 경로를 모두 처리 (§6)» | «(§6)» 자칭이나 열거는 §10 검증 행렬 form 행(273행)과 더 정확히 일치 — 좌표 모호, 아래 행과 병기 |
| 13 | s011-10/b7 | implementation-django-web-skill/s004 | 26행(동일 문장) | 273행 «GET, valid POST, invalid POST, redirect, form error assertion» 축자 대응 — 소급 패스에서 둘 중 하나로 확정 필요 |
| 14 | s008-7/b4 | implementation-django-web-skill/s004 | 27행 «HTMX fragment는 method·auth·permission·CSRF를 function/class view와 동일하게 보호 (§7)» | 214행 «non-HTMX POST와 같은 수준의 auth, permission, CSRF» 축자 대응 |
| 15 | s009-8/b1 | implementation-django-web-skill/s004 | 28행 «CSRF·XSS 설정과 보안 헤더는 Django 보안 프리미티브로 유지 (§8)» | «(§8)» 자칭 — 240행 4문장의 압축 |
| 16 | s011-10/b1 | implementation-django-web-skill/s004 | 29행 «render acceptance 보고는 실제 실행한 검증만 기재, 미실행은 미실행으로 명시 (§10)» | 264행 첫 두 문장과 축자 대응 |
| 17 | s012-11/b1 | implementation-django-web-skill/s004 | 30행 «에러는 출처로 분류 … (§11)» | 283행 «출처로 분류해 처리 자리를 가른다» 축자 |
| 18 | s012-11/b3 | implementation-django-web-skill/s004 | 30행 «도메인 예외는 view-local 재렌더» | 287행 축자 |
| 19 | s012-11/b5 | implementation-django-web-skill/s004 | 30행 «시스템·미식별은 `handler500`» | 289행 축자 |
| 20 | s012-11/b6 | implementation-django-web-skill/s004 | 30행 «transient는 미들웨어 503» | 290행 축자 |

- 유예 총 **20건**(사본 블록 좌표 기준). 상대는 전부 `implementation-django-web-skill` — 이 문서에는 **다른 문서군과의 교차 재진술이 없다**(§11 이 언급하는 `implementation-django-ninja` §6.2 는 «반대 규율»을 명시한 대비 참조이지 재진술이 아니다).
- 문서 **내부** 재진술 1쌍은 spec 에 실었다: `s005-4/b1 → s002-1/b10`(§1 정본).
- **사본 커버리지 구멍(소급 패스 참고)**: SKILL «핵심 운영 원칙» 요약은 §5(Static)·§9(View auth) 두 절을 누락한다(P0 특이 발견 4·발주서 비고와 일치) — 이 두 절(s006-5·s010-9)은 유예 쌍이 **없는 것이 정상**이다.
- **추가 관찰(센서스 restate 열 미표기 · 계수 제외)**: SKILL YAML frontmatter(skill s001, 3행 description 말미)의 «Django 코어(모델·ORM·트랜잭션)는 implementation-django, JSON API 어댑터는 implementation-django-ninja, REST 계약 설계는 architecture-api로 위임»은 내 `s001/b1` 2규범과 같은 위임을 진술한다. frontmatter 를 규범 블록으로 볼지 자체가 미결(센서스가 skill s001 을 «서두 절 — P0 비계수»로 처분)이라 유예 쌍으로 세지 않고 관찰만 남긴다.

## 4. 경계 판단 메모

**⑴ 코드 펜스의 후행 빈 줄 귀속** — §13 은 «code 리터럴 = 여는 펜스~닫는 펜스 전체»와 «블록 간 구분자는 선행 블록 후행 귀속»을 함께 말한다. 절 끝·펜스 뒤 빈 줄에서 둘이 충돌하므로 **구분자 규칙을 우선**해 닫는 펜스 다음 빈 줄까지 code 블록에 넣었다(예 `s003-2/b10 = [53,98]`). 근거: 웨이브 1 기이관본의 실판형(implementation-django-final 의 code 블록이 모두 닫는 펜스+1행까지 포함)과 일치시켰고, 빈 줄만 담는 유령 블록을 만들지 않는다. `s012-11/b15 = [398,424]` 는 파일 끝이라 후행 빈 줄이 없다.

**⑵ 절 선두 구분자** — §13 유일 예외대로 헤딩 직후 빈 줄은 첫 블록 선두에 붙였다(전 12절 `line_start+1` 시작 — 도구 단언 통과).

**⑶ 머리말(s001) 인용 블록 분해** — 4~16행이 끊김 없는 blockquote 지만, 7행의 단독 `>` 가 인용 안의 문단 구분자다. 이를 경계로 `b1=[2,7]`(위임 2규범 보유 → kind=norm) / `b2=[8,17]`(출처 약어 8항 — 근거 표기 체계라 규범 0 → prose)로 갈랐다. 18~19행 `---` 은 별도 prose. 4행 «전용 source reference다»는 정의문이라 비계수(발주서 비고 승계).

**⑷ 표 운반 절의 kind** — 머리행+구분행을 한 `table-row` 블록으로, 데이터 행은 1행=1블록=1규범으로 잘랐다(P0 «표의 행은 행당 1규범» 계수 규약과 블록 해상도를 일치시켜 대사 가능성을 유지). §1 위임표 6행·§2 선택표 5행·§10 검증 행렬 8행 모두 동형.

**⑸ 규범 0 불릿의 kind=prose** — `s007-6/b3`(169행 «Django form validation order 는 … 순서다»)은 불릿이지만 사실 진술이라 규범 0이다. kind 정의(«norm = 규범 문장 포함 문단/불릿»)에 따라 prose 로 판정했다(발주서 «validation order 서술은 사실 진술로 제외» 승계). 역으로 `s008-7/b1` 은 정의문 «HTMX view 는 web adapter다»가 비계수여도 같은 문단에 규범 1문장이 있어 kind=norm 이다.

**⑹ §4 선두의 재진술 처분** — 1절 참조. 정본을 §1 로 잡은 근거: ①§1 문장이 «만 담당한다»는 한정 표지를 가진 책임 배분 선언이고 §4 선두는 그 배분을 받아 적은 절 도입부다 ②센서스가 재진술 쌍을 §4 행에 달고 상대로 §1 을 지목했다 ③§4 블록에는 §1 에 없는 고유 금지(가격 계산·상태 전이 등)가 있어 «사본 블록도 고유 규범은 승격»이라는 웨이브 1 판형에 맞는다. **반대 논거도 기록**: SKILL 25행이 같은 규칙에 «(§4)» 좌표를 달아 §4 를 소유자로 부르므로, 소급 패스가 정본을 §4 로 뒤집을 여지가 있다(그 경우 §1 b10 의 3번째 Work 를 사본으로 강등).

**⑺ §10 «service 예외 처리(§11)» 행을 §11 재진술로 승격하지 않음** — 275행은 §11 의 처리 규칙을 압축 인용하지만 그 행의 규범력은 «어떤 증거를 제출하고 무엇을 gap 으로 보고하나»(검증 행렬)이지 처리 규칙 자체가 아니다. 센서스 restate 열도 이 쌍을 잡지 않았다. 문면의 «(§11)» 은 좌표 참조로 그대로 둔다(byte 등가 불변).

**⑻ §5 static 배치와 표준 트리의 잠재 긴장** — 152행 «app-specific asset 은 프로젝트가 `app/static/app_name/...` 구조를 쓰는 경우 앱 가까이에 둔다»는, 표준 트리 채택 저장소에서 `check-layer-skeleton` #490(트리 밖 경로 금지)과 부딪힐 수 있다(트리 87~88행에 templates 칸은 있으나 static 칸은 없다). 문면이 «프로젝트가 …쓰는 경우»라는 기존 관례 조건부라 배선은 하지 않고 기본값으로 두되, 이 긴장은 T3 이후 규칙 정합 심의 재료로 남긴다.

**⑼ §8 의 P0 «커버»는 enforcedBy 가 될 수 없다** — P0 E09 §8 행은 백스톱 «커버»지만 지목 대상이 Django 내장 `manage.py check --deploy` 다. registry 개체는 `dddjango/scripts/check-*.py` 27종 + Agent 8종뿐이라 IRI 를 만들 자리가 없다. 따라서 §8·§10 의 보안 검사 관련 2규범은 delegatedTo 로 보내되 basis 에 «커버지만 registry 밖» 사유를 명시했다(도피가 아니라 개체 부재).

**⑽ §11 문면의 참조 표류 재확인** — 291행 말미 «(`discipline-houserules` §2)» 는 현행 houserules SKILL §2(충돌 중재)·references/final.md §2(골격 규칙) 어느 쪽과도 무관하다(두 문서 전문에 transient·마커 어휘 0 — 직접 확인). P0 특이 발견 3 과 동일 결론이며, **이관은 문면 그대로**(리터럴 verbatim) 두고 표류 정정은 별건 개정 사안으로 남긴다.
