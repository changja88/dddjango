---
날짜: 2026-08-06
대상: docs/work_flow.html (수정안 · 트리 91행 · 결정 32)
증거: /Users/hyun/Desktop/broccoli-server @ HEAD (읽기 전용)
방식: 8개 렌즈 적대적 리뷰 → 렌즈별 독립 반박 → 종합 (에이전트 17)
원 발견 48건 → 반박 통과 42 → 중복 병합 26 (치명 2 · 중대 8 · 보통 12 · 사소 4)
진행 상태 (2026-08-06): R1~R8 + R12 닫힘 — `framework/` · D11 예외 둘 · D13 검사 면제 · `port/<capability>/` 폴더화와 `transaction/` 신설 · 플러그인 충돌 기록 · J6 은 「dto_out 은 «모양» 규칙」으로 닫음 · **J7 은 「주어가 그 애그리거트인가」로 축을 고치고**(Evans 가 요약값을 명시 허용 · Vernon 의 Use Case Optimal Query · Young/Millett 의 Thin Read Layer·Domain Reporting) **`application_layer/query_repository/<capability>/` 를 신설**했다(포트는 «바깥 행위자와의 대화»라 DB 조회가 갈 자리가 아니다). 실측 181:0 — 그 칸은 지금 비어 있다. **R9 는 `app_label` 논거를 「BC 이름이 곧 label · 유일성은 BC 가 형제 폴더라서 공짜」로 갈아끼우고**(실측 16/16 이 명시 선언 · 폴더 이름과 같은 앱 0) 자리표시자 `<app>` → `<bounded_context>` 를 정리했다(`<app>` 이 BC 와 장고 앱 두 뜻이었다). **R10 ⒟ 는 도메인 서비스 두 칸을 하나로 합쳤다** — 갈림길이 「몇 개 애그리거트를 건드리나」가 아니라 «누가 부르나»였고(참조 구현 넷 대조), 실측 응용 43 : 애그리거트 1 · 루트 메서드 후보 0/52. D28 결정②를 뒤집어 D13 원안으로 돌아갔다. **⒝ 는 D17 이 이미 준 「칸 바로 아래 파일」 자리를 트리에 그리고, 그중 «업무 어휘가 0인 계약»을 `framework/<capability>/`(계약+구현 한 폴더)로 올렸다** — Evans COHESIVE MECHANISM · Grzybek/eShop/IDDD 가 모두 공용 패키지에 계약과 구현을 함께 둔다. 판정은 이분법(실측 16 중 2). 트리 **102행**. **㉯(`Fake` 접두사)는 트리 변화 0 으로 닫았다** — 접두사가 없다는 건 자리도 없다는 뜻이었고 `driven_layer/` 다섯 칸이 이미 막고 있었다. Meszaros 의 다섯 갈래는 전부 테스트 어휘이고 실측 7개는 Stub 4 · Spy 3(Fake 0). 저장소가 이미 정답을 갖고 있었다 — `test/**/fakes.py` 5파일 38클래스 중 26이 포트 대역인데 7개만 어긋난다. 원인은 이름이 아니라 `settings.*_USE_REAL` 스위치이고, 그 결과 **알림톡 거짓 성공이 DB 에 배달 완료로 적히고 SMS 폴백을 막는 버그**가 돌고 있다 → 10번. **R11 은 `framework/test/` 의 판정 축을 고쳐 닫았다(칸 0)** — 옛 축 «몇 개 BC 가 쓰나»는 `login_session`(13 BC)을 올리라 하는데 그 본문이 `/v1/auth/social-login` 을 POST 한다. 새 축은 「BC 하나를 지웠을 때 이 파일이 바뀌나」이고 재측정 **199회 중 5종 57회만 올라간다**. BC 고유 131 + factory 11 은 각 BC 가 갖는다(중복이 답). 덤으로 **테스트가 타 BC 프로덕션을 161건 import** 하는 걸 처음 셌다 — 관문 115 정당 · **46 우회**. **R10 ⒞ 도 닫았다(칸 0)** — celery 소스를 직접 펴서 확인: Django fixup 이 넘기는 package 가 `AppConfig.name`(=`…driven_layer.django_<bc>`)이라 `related_name` 으로는 `driving_layer/cron_job/` 에 못 닿고, `imports=` 는 D25 의 «목록» 병이다. `packages` 를 콜러블로 주되 **`label` 로 도는 규칙**으로 짓는다(R9 가 「BC 이름이 곧 label」을 정해서 가능해졌다) + `cron_job/__init__.py` 재수출 한 줄. **R13 도 닫았다(칸 0) — 이걸로 R1~R13 전부 끝.** 규율 ⑤ 의 자를 「지금 실측에 쓰이나」에서 **「이 칸 자체에 결함이 있나」**로 좁혔고, 트리의 목표가 «앞으로 생길 상황을 이미 커버한다»이므로 **「나중에 생기면 그때 연다」로 끝나는 문장 자체가 결함**이라고 못박았다. 규율 ⑤ 를 쓴 자리 넷 중 D7·D34·D6 은 다른 근거가 지탱하고 **D26 의 넷째 칸 하나만 그 위에 서 있어** 근거를 「넣을 것이 없다」(D34 가 조각 다섯의 갈 곳을 다 짚었다)로 갈아끼웠다 — celery 가 와도 소비 task 는 `open_host_service/` 를 부르는 얇은 껍데기라 입구 셋이 다 받는다. **그리고 J1 의 수치 정정을 전부 끝냈다 — 이제 문서의 전 수치가 HEAD 한 코퍼스다**: 분모 15→**16** · 운영 의존성 **14** · 32/43→**41** · 예외 55파일·273클래스→**60·304**(BC 밑 11→12) · 「401 이 13개 feature 전부·422 는 11·503 은 9」→**401 23/23 · 422 20/23 · 503 19/23**(13 은 feature 가 아니라 BC 수였다) · 도메인 포트 선언 49·포트 67→**파일 54·클래스 70·선언 54** · schema 63/43/20→**101/70/31**. 정정마다 옛값과 왜 달랐는지를 `dim` 주석으로 같이 남겼다. **다음은 적용 단계 9(플러그인) → 10(코드).**
  D24 에 «③ 재결정» 절 추가 + 「루트 패키지 이름은 stdlib 모듈명과 겹치지 않는다」 규칙 신설.
  나머지 R2~R11 미정. 트래킹 표는 대화 답변 끝에.
---

# dddjango 수정안 × broccoli-server 현행 — 최종 대조 리포트

42건을 중복 병합해 **26건**으로 정리했다(치명 2 · 중대 8 · 보통 12 · 사소 4). 수치는 전부 독립 재측정치(HEAD, `.venv/bin/python` 3.14)를 채택했고, 원 발견의 값과 갈리는 곳은 재측정치를 썼다.

---

## 치명 — 그대로 적용하면 결정 불가이거나 서비스가 죽는다

### C1. D11(입구는 도메인을 모른다)과 D27(입구가 도메인 예외를 «직접» 번역한다)이 동시에 참일 수 없다
**렌즈**: Hexagonal 정합 · 자리 없는 현행 (두 렌즈가 같은 충돌을 각각 발견)
**다시 열어야 할 결정**: **D11 결정③** (+ 트리 3행, PART1 [driving] 「안쪽으로는 application_layer «만»」)

- D11 결정③(revision.txt:240) — 「`api/<feature>/` · `open_host_service/<service>/` 아래는 `application_layer/<feature>/` 아래만 의존한다. domain_layer 도 … `application_layer/port/` 도 import 하지 않는다」
- D27 ②(:201) · 트리 20행(:76) — 「도메인 예외를 번역해서 던진다(raw 전파·재노출 금지) · 알려진 구체 예외의 **전수 명시 매핑**」
- D27 ③(:202) — 「controller 가 짧은 exception→concrete ErrorOut 매핑을 «직접» 소유한다 · helper·factory·handler 등록 decorator·global mapper **금지**」

구체 예외를 `except` 하려면 그 클래스를 import 해야 하고, D27 이 helper 위임까지 금지해 우회로가 없다. 응용 층이 대신 번역하는 길도 막혀 있다 — 계약 예외는 `driving_layer/open_host_service/<service>/contract/` 에 살고 D14 결정③이 「application_layer 는 driving_layer import 금지」다.

**실측 재현**(직접 확인):
```
$ grep -rn "^from application\..*\.domain_layer" application/*/presentation_layer application/*/published_service | grep -v /test/ | wc -l
133          # 58파일 · 16개 BC 전부
```
- 종류별: value_object 71 · exception 33 · entity/aggregate 23 · repository 선언 3 · **port 선언 2** · event 1
- 결정적 실물 — `/Users/hyun/Desktop/broccoli-server/application/notifications/published_service/notification_publish_service/_exception_translation.py:9-21` 이 `NotificationsError`·`InvalidNotificationPublication`·`NotificationSnapshotConflict` + **domain port 선언 2모듈의 예외 4개** 총 7심볼을 끌어와 `except (NotificationsError, DjangoDatabaseError)` 로 잡아 `*_v1` 계약 예외로 바꾼다. D27 ②가 명령한 «전수 명시 매핑» 그 자체다.
- `application/lessons/presentation_layer/api/lesson/lesson_controller.py:35` `from ...domain_layer.lesson.exception import InvalidLesson`
- 그리고 D13 이 `domain_layer/**/port/` 를 `application_layer/port/` 로 옮기면 위 예외 4개의 import 는 **D11 이 이름을 들어 금지한 `application_layer/port/` 직행**이 되어 더 나빠진다.

**제안**: D11 의 사정거리를 D6 가 `api_router.py` 에 한 것처럼 정확히 좁힌다 — 「입구는 domain_layer 의 «예외 모듈»만 import 할 수 있다. 애그리거트·엔티티·값 객체·리포지토리/포트 선언은 금지」. AST 한 줄로 검사되고(`domain_layer` import 중 `exception` 모듈만 허용), 실측 133건이 «허용 33 / 금지 100» 으로 기계 판정된다. 좁히지 않으려면 D27 ②③을 폐기하고 응용 예외로 한 겹 더 번역해야 하는데, 그 비용(도메인 예외 304클래스의 응용 미러)이 수정안에 계산돼 있지 않다.

---

### C2. `platform/` 이 파이썬 표준 라이브러리 `platform` 을 가려 부팅이 죽는다
**렌즈**: 이행 가능성
**다시 열어야 할 결정**: **D24 이름 결정**(common → platform) · 트리 80~85행

저장소 루트는 `manage.py`(sys.path[0])와 gunicorn(`gunicorn/app/base.py:90 sys.path.insert(0, cfg.chdir)`) 양쪽에서 sys.path 에 들어간다. 루트에 `platform/` 패키지를 만들면 stdlib `platform` 이 가려진다.

**실측**(직접 확인):
- `.venv/lib/python3.14/site-packages/firebase_admin/_utils.py:18` `from platform import python_version` ← 이 앱 자신의 운영 import 체인이다: `delivery/composition_root.py:34` → `infra_layer/adapter/firebase_fcm_push_gateway.py:9` → 위 줄에서 **ImportError**. 재현 시 `manage.py check` 가 RC=1.
- `.venv/lib/python3.14/site-packages/gunicorn/workers/workertmp.py:7 import platform` → 워커 로딩 자체 실패(RC=1).
- `deploy/broccoli-server.service.template:10,12` — `WorkingDirectory=/srv/broccoli-server/current` · `gunicorn --config deploy/gunicorn.conf.py`, 그 conf 에 `chdir` 지정이 없어 저장소 루트가 그대로 sys.path 에 들어간다.
- 덤 — 이 저장소는 이미 `Platform` 을 도메인 낱말로 쓴다: `application/pairing/domain_layer/value_object/platform.py`

수정안 전문(D24 · 트리 80~85행 · PART1 [platform])에 표준 라이브러리 이름 충돌을 다루는 문장이 **한 줄도 없다** — D24 는 common/framework/platform 셋을 «판정 가능성»으로만 견줬다.

**제안**: 루트 패키지 이름을 예약되지 않은 것으로 바꾼다(`foundation/` · `shared_platform/`). D24 의 근거(「바닥」·판정 가능성)는 이름을 바꿔도 그대로 산다. 그리고 「루트 패키지 이름은 stdlib 모듈명과 겹치면 안 된다」를 트리에 한 줄 넣어라 — 같은 함정이 `test/`·`types/`·`enum/`·`json/` 에도 있다.

---

## 중대 — 현행이 갈 곳이 없거나, 규칙이 검사 불가능하거나, 근거 수치가 사실과 다르다

### J1. 근거 수치가 두 코퍼스에서 섞여 나왔고, 규범 행(트리 91행)이 폐기된 값을 들고 있다
**렌즈**: 근거 수치 재측정 ×4 · 장고 현실 ×2 · 검사 가능성 ×2 · DDD 정합 · Clean 정합 (8개 렌즈 중 6개가 짚었다)
**다시 열어야 할 결정**: 없음 — **트리 행·PART1 수치 일괄 정정**(단, D28 의 37:6 은 기준 문구를 함께 고쳐야 한다)

원인이 특정됐다. 트리 행은 **08-05 코퍼스**(llm_meta BC 이전, `1adf7b04^`), 결정 카드 일부는 **08-06 코퍼스**(`c7d9ac8d^` 이후)에서 쟀고, D25 의 08-06 정정이 트리 행에 반영되지 않았다.

| 자리 | 문서값 | HEAD 실측 |
|---|---|---|
| 트리 54·55·76·77행 | 「실측 15/15」 | **16/16** (BC 16 · apps.py 16 · models 16 · unit 16 · integration 16) |
| 트리 78·79행 | 「실측 10/15」 | **10/16** (e2e 없음 6 · factories 없음 6) |
| PART1 [driving] | 「15개 BC」 | **16** (D30·D34·D8 은 이미 16이라 적었다 — 한 문서 안에 분모 둘) |
| 트리 86행 · PART1 [project] | 「실측 위반 32건」 | **41건** (api.py 28 · urls.py 13). 32 = 43 − noqa 11 = 정정 전 값 |
| D25 ③ | 「43건 (… test 2)」 | **41건** — `broccoli_server/test/` 는 커밋 `4febcbfe`(08-05 21:52)로 삭제됨 |
| 트리 6행 · PART1 [driving] · D8 · D27 | 「401 이 13개 feature 전부 · 422 는 11 · 503 은 9」 | **13은 BC 수**. 컨트롤러 보유 feature 22 중 401 은 21(빠지는 것: `parental_controls/banned_keyword_settings`). 422 → BC 10 / ft 18, 503 → BC 12 / ft 17. **11·9 는 어느 시점 어느 단위로도 재현 안 됨** |
| 트리 44·50행 | 「실측 37」·「실측 6」 | **기준 미명시**. 독립 재측정 둘이 서로 다른 값을 냈다 — 전체 기준 28:16, 루트 기준 36:8, 엄격 기준 39:5. 37:6 이 나오는 계산법은 `c7d9ac8d^` 에서 하나뿐 |
| 트리 47행 | 「55파일 · 273클래스」 | **60파일 · 304클래스** (llm_meta 5파일·28클래스) |
| PART1 [domain] vs D32 ① | 「선언 49개·폴더 51개」 vs 「64」 | 폴더 51 · 파일 54 · **선언(ABC/Protocol) 54** · 클래스 70 |
| D8 08-06 재검 | 「schema 63 / 사용 43 / 미사용 20」 | BC층만 센 값. **전체 97 / 68 / 29** (feature 하위에 34클래스 더) |
| D29 | 「도메인 리포지토리 43개」 | llm_meta 포함값(제외하면 39) — 코퍼스 표시 필요 |
| D34 · D26 | 「운영 의존성 15개」 | **14** |

**왜 중대인가**: 이 트리는 「규칙은 실측이 정했다」를 논증의 뼈대로 쓴다. 규범 행 여섯이 폐기 수치를 들고 있으면 다음 사람이 재현에 실패하고, 특히 「32건」만 읽은 이관자는 D25 가 금지로 뒤집은 `# noqa: F401` 등록 11건을 남긴다. 방향은 대체로 논거를 «강화»한다(15/15 → 16/16 이라야 진짜 만장일치).

**제안**: 전 수치를 HEAD 한 커밋으로 다시 돌리고 각 값 옆에 «세는 명령»을 각주로 남겨라. 15 가 남은 자리 여섯 · 32 가 남은 자리 둘 · 401/422/503 세 자리 · 37:6 · 55파일 · 49/64 를 우선 고친다.

---

### J2. 도메인 내부 import 검사 두 줄(D13 검사 ②③)이 value_object·exception 을 면제하지 않아 켤 수 없다
**렌즈**: DDD 정합 ×2 · 검사 가능성 (같은 병을 두 칸에서 발견)
**다시 열어야 할 결정**: **D13 검사 ② ③**(revision.txt:250) · **트리 48행**(shared_value_object 잎) · **트리 50행**(도메인 서비스 루트만)

두 규칙이 같은 병을 앓는다 — 도메인 안에서 «값 객체와 예외를 만지는 것»을 금지 대상에 넣어 놓고, 트리 47행이 예외를 `<aggregate>/exception.py` 에 두고 D13 이 시그니처 타입을 강제한다.

**② shared_value_object 잎** — 이관 대상 39개 중 **26개가 자기 애그리거트의 exception 을 import** 한다(비-잎 총 29).
- `application/report/domain_layer/report_period/value_object/report_period.py:8` `from ..exception import InvalidReportPeriod` (24·44행에서 raise). ReportPeriod 를 쓰는 다른 애그리거트가 정확히 4개.
- `application/report/domain_layer/curriculum_codebook/value_object/curriculum_domain_cell.py:7` (raise 5회)
- `application/llm_meta/domain_layer/catalog_entry/value_object/model_ref.py:8,9`
- 예외 칸을 열 길도 막혀 있다 — D27 ①이 「도메인 예외의 표준은 애그리거트 밑 하나뿐」이라 BC 레벨 exception.py 를 못 만든다.

**③ domain_service 는 애그리거트 루트만 import** — 규칙이 적힌 칸(트리 50행, BC 레벨)의 **입주 예정자 5/5, 100% 가 문장대로면 위반**이다(household_membership_service → `child.exception` / function_call_pair_resolver / transcript_assembler / transcript_token_estimator / assignment_catalog_conformance). 44파일 전체에 걸면 25파일(57%) 위반이고 종류별로 value_object 36 · exception 16 · entity 1 · port 1 · 형제 domain_service 1 이다. 트리 48행의 shared_value_object 도 「애그리거트 루트」가 아니라 같은 문장에 걸린다.

**정정**: 원 발견이 「D32 의 pipeline 3파일이 100% 걸린다」고 한 것은 성립하지 않는다 — 그 파일들은 44행(애그리거트 레벨)에 앉고 그 행에는 import 조문이 없다. 다만 44행에 조문이 없다는 사실 자체가 「검사 ③을 어느 경로에 거나」를 문서로 판정 못 하게 한다.

**제안**: 두 규칙을 같은 낱말로 다시 쓴다 — 「**자기 애그리거트 폴더 안 + 자기 BC 의 shared_value_object/ 만** import 한다」(도메인 서비스), 「**자기 BC 의 domain_layer 밖을 import 하지 않는다**」(shared_value_object). 여전히 grep 한 줄이고, 원래 목적(타 애그리거트 차단·리포지토리 차단)은 그대로 지켜지며 실측 위반이 25 → 5 수준으로 떨어진다. 그리고 검사 ③이 44행에도 걸리는지 50행에만 걸리는지를 트리 행에 적어라.

---

### J3. 포트가 «던지는 실패»와 «주고받는 자료구조»에 칸이 없다
**렌즈**: Clean 정합 · 자리 없는 현행
**다시 열어야 할 결정**: **트리 25행**(application_layer 자식은 둘뿐) · **트리 32·33행**(port/ 칸) · **D27 ①** · **D33**

⒜ `/Users/hyun/Desktop/broccoli-server/application/usage_quota/application_layer/persistence_exception.py` — 6클래스(`UsageQuotaPersistenceError` 기저 + Transient/RecordUniqueConflict/BucketUniqueConflict/CasConflict/Internal). 생산자 5파일이 **driven**(`infra_layer/repository/{usage_record_repository, family_usage_quota_repository, usage_quota_unit_of_work, persistence_error_normalizer}.py` + `infra_layer/acl/entitlements_family_usage_limit_adapter.py`), 소비자 4파일이 응용이다. 바인딩이 기계적으로 닫힌다 — driven 이 import 해야 하므로 D20 결정③에 따라 `port/` 밖에 못 가는데, 트리 32·33·34행이 port/ 에 주는 행은 `<capability>.py` 와 `unit_of_work.py` 둘뿐이고 D27 은 예외의 자리를 «애그리거트 불변식»과 «BC 경계 계약» 둘로만 닫았다. D27 ③은 «응용 base» 를 전제로 폴백 규칙을 쓰는데 그 파일이 사는 행이 트리에 없다.

⒝ `domain_layer/**/port/` 54파일·70클래스 중 **ABC 도 abstractmethod 도 없는 것이 16개**(페이로드 12 + 예외 4). D32 가 이 54파일을 통째로 `application_layer/port/` 로 옮기므로 16개가 따라 들어가고, D33 의 「클래스 이름 = 접두사 + 파일 이름 CamelCase + 자리 접미사. **AST 한 줄로 검사된다**」를 문자 그대로 켜면 전부 오탐이다. 실물: `notification_dispatch_port.py::{NotificationDispatchTemporarilyUnavailable, NotificationDispatchFailed, NotificationDispatchPlan}`, `family_member_directory_port.py::{…, FamilyMemberIds}`, `fcm_push_gateway.py::FcmPushPayload`, `purchasable_product_port.py::PurchasableProduct`, `social_auth_gateway.py::VerifiedSocialIdentity` 외.
게다가 그 예외 4개는 `NotificationsError` 를 상속하므로 D27 ①에 걸려 **파일째 옮길 수 없다** — 분해 비용이 49에도 64에도 안 잡혀 있다.

**제안**: port/ 칸에 두 줄을 더한다 — ①「포트가 던지는 실패와 포트가 주고받는 자료구조는 그 `<capability>.py` 안에 함께 산다(도메인 예외를 상속하지 않는다)」 ②「여러 포트가 공유하는 실패 어휘는 고정 이름 파일 하나(`port/<bc>_persistence_error.py`)로 둔다」(선례 `unit_of_work.py`). 동시에 **D33 의 접미사 검사 대상을 「ABC 또는 abstractmethod 를 가진 클래스」로 좁혀 적어라** — 안 그러면 D25 가 진단한 「규칙을 목록으로 썼다」 병이 예외 목록으로 재발한다.

---

### J4. 도메인 포트를 응용으로 올리는 결정이 플러그인의 결정적 blocker 와 정면 반대인데, 결정 카드에 그 인식이 없다
**렌즈**: 검사 가능성
**다시 열어야 할 결정**: **D13 결정①**(port/ 를 도메인에서 아예 없앤다) · **D32 결정①** · **D27 「어긋나던 셋」 목록**

`/Users/hyun/Desktop/dddjango/dddjango/scripts/check-layer-skeleton.py:106`
```python
FOREIGN_PORT_LAYERS = ("application_layer", "infra_layer")
```
이 층 하위 `port/` 에 비-`__init__` .py 가 있으면 **exit 2 = blocker**(main() 337행). 현행은 `application_layer/**/port/` 실파일이 0개라 통과하지만, D2·D14·D29·D32 가 `application_layer/port/<capability>.py` 를 필수 칸으로 만들고 `domain_layer/**/port/` 실파일 54개가 그리로 이동하는 순간 **54건 blocker**다.
문서 쪽도 같은 편이다 — `final.md:156·194` 「도메인은 협력 포트(`domain_layer/<aggregate>/port/`)로 의존」, `agents/discipline-reviewer.md:82` 「협력 포트가 `application_layer/<feature>/port/`에 배치 … **blocker — 명세 정당화는 면제 사유가 아님·설계 반송**」.

**중요한 정정**: 「D27 이 셋이라 세고 넷을 빠뜨렸다」는 D27 오독이다 — D27 이 센 셋은 `final.md:67` 의 «rename·move 금지 경로 다섯» 중 트리가 건드린 부분집합이고, 우선순위도 이미 적혀 있다(revision.txt:203 「구현에 들어갈 때 플러그인 문서·백스톱을 트리에 맞춘다」). 그래서 `LAYER_DIRS`·`REQUIRED_KIND_DIRS`·`AGG_CORE_KIND_DIRS` 셋(개명·접기)은 그 한 줄이 덮는다. **덮이지 않는 것은 `FOREIGN_PORT_LAYERS` 하나** — 이건 이름 문제가 아니라 «협력 포트의 소유자가 도메인이냐 응용이냐»라는 설계 역전이고, reviewer 조문이 여기에만 「설계 반송」을 걸어 놨다. revision.txt 에서 «플러그인»이 나오는 D6·D27·D28·D30·D34 중 이 조항을 언급하는 곳이 **0곳**이다.

**제안**: D13/D32 에 「플러그인은 협력 포트를 도메인 소유로 blocker 로 못박고 있다 — 이 트리가 이기려면 `final.md` §2·§3 표와 `discipline-reviewer.md:82`, `check-layer-skeleton.py:106` 이 같은 커밋에서 바뀌어야 한다」를 한 줄 적고, 순서(플러그인 먼저 → 트리 적용)를 이행 규칙으로 못박아라. 이관 규모를 문서가 실제보다 작게 잡고 있다.

---

### J5. 컨트롤러가 인터랙터를 얻는 길이 표준에 없다 — 48파일이 규칙 밖에서 결정된다
**렌즈**: 이행 가능성
**다시 열어야 할 결정**: **D6**(결선) · **D11 결정③**

- `presentation_layer + published_service`(테스트 제외) → `composition_root` import **59건 / 48파일**(고유 팩토리 심볼 102개). D11 결정③은 이 경로를 금지한다.
- 역방향은 0건이다 — `application/*/composition_root.py` 어디에도 presentation/published_service import 가 없다. 즉 **결선이 컨트롤러를 꽂아 주는 길이 현행에 존재하지 않는다.**
- D6 는 `api_router.py` 의 이름·방식(`def register_<bc>_api(api)`)만 정하고 「컨트롤러가 인터랙터를 어떻게 얻나」를 어디에도 적지 않았다.
- 대표: `application/lessons/presentation_layer/api/lesson/lesson_controller.py:27-33` `build_*` 6개.

**제안**: D11 에 «결선 주입 경로» 한 줄을 추가한다 — 컨트롤러가 composition_root 의 팩토리를 잡는 것을 허용하든(D6 가 api_router 에 이미 낸 예외의 확장), ninja-extra DI 로 생성자 주입을 규정하든 **둘 중 하나를 명시**해야 한다.
(덧: 같은 발견의 「133건에 대체 수단이 없다」는 과장이다 — D11 이 「필요한 dto_in·dto_out 은 `<use_case>/dto/` 에 있다」고 적었고 D8 이 「응답 스키마가 도메인 타입을 직접 노출하는가」를 검사 대상으로 세웠다. 비싼 것이지 수단이 없는 것은 아니다. → 10번 목록.)

---

### J6. D14 의 전제(「밀어낼 일이 없다」)가 SSE 로 반증되고, `TurnEventSubscription` 이 세 자리에서 다 걸린다
**렌즈**: Clean 정합 ×2 · 이행 가능성 · 자리 없는 현행 (4개 렌즈)
**다시 열어야 할 결정**: **D14**(Boundary 둘 제외의 전제) · PART1 [application] 「이 모양이 된 까닭」

- D14 는 「요청 하나에 응답 하나인 API 에는 밀어낼 일이 없다 / **밀어내는 출력이 생기면 그때 꺼낸다**」로 Output Boundary + Presenter 를 뺐다. 그 트리거가 이미 충족돼 있다.
- 선언 `application/ai_chat/application_layer/turn_streaming/service/turn_event_subscription.py:8 class TurnEventSubscription(ABC)`, driven 구현 `infra_layer/adapter/thread_turn_exhaust_executor.py:136 _QueueTurnEventSubscription`(:59 가 반환), dto 운반 `dto/start_turn_result.py:16` · `dto/resume_turn_stream_result.py:18` `subscription: TurnEventSubscription`, driving 소비 `presentation_layer/api/turn/turn_controller.py:43,201,219` · `sse/sse_stream_renderer.py:18,67`.
- 세 자리가 다 막힌다 — `port/` 에 두면 D11 결정③, `<feature>/` 밑에 두면 driven 어댑터가 `application_layer/<feature>/` 를 import 해 D20 검사①, `dto_out` 에 남기면 트리 29행(「엔티티도 DB 행도 넘기지 않는다」).
- 같은 폴더에 `turn_event_sink.py`(ABC, docstring 「소진 루프가 이벤트를 흘려보내는 출구」) · `turn_streaming_service.py`(877줄) 가 있고, Presenter 자리의 `sse/sse_stream_renderer.py`(108줄)가 `domain_layer.turn.value_object.{stream_event, stream_event_type, turn_deadline}` 을 직접 import 해 D11 도 함께 어긴다.

**정정**: 방향은 아직 뒤집히지 않았다 — 렌더러가 `subscription.next()` 를 «당겨오고»(`:67 render(subscription) -> Iterator[bytes]`), 컨트롤러가 `StreamingHttpResponse` 로 감싼다(`:226-227`). 그래서 「배치 불가(치명)」가 아니라 **결정 카드의 전제가 사실과 다르다(중대)** 이다.

**제안**: D14 에 「이 저장소에는 밀어내는 출력이 하나 있다(ai_chat SSE) — 지금은 당겨오는 모양이라 Presenter 를 세우지 않지만, 구독 핸들이 경계를 넘는 것은 트리 29행 위반이다」를 적고, ⒜ 출력 포트를 `application_layer/port/` 에 허용하고 D11 에 「driving 은 **출력 포트에 한해** port/ 를 참조할 수 있다」는 좁은 예외를 명시하거나 ⒝ dto_out 을 `turn_id` 만 싣는 자료구조로 되돌리고 렌더러에 Presenter 자리를 주거나 — **둘 중 하나를 골라 적어라**.

---

### J7. Thin Read Layer 의 판정 축이 반환형·오류 계약과 어긋나고, 「나갈 11개」에 오분류가 있다
**렌즈**: DDD 정합
**다시 열어야 할 결정**: **D29 결정①③④** · 「58:11」 재산출 · 트리 67행

D29 는 판정 축을 «애그리거트 루트를 돌려주느냐»로 잡고 구현 검사를 «domain_layer 를 import 하지 않는다»로 걸었는데, 「나간다」고 직접 지목한 반환형이 전부 도메인 타입이다.
- `PricePeriod` — 선언 `llm_meta/domain_layer/price_schedule/repository/price_schedule_repository.py:34`, 정의 `…/value_object/price_period.py:13`(도메인 VO)
- `CurrentUsageBuckets` — `usage_quota/…/family_usage_quota_repository.py:47`, 정의 `…/value_object/current_usage_buckets.py:17` — **UsageBucket 엔티티를 담고 `__post_init__` 불변식까지 있다**
- `NotificationRecordPage` — `notifications/…/notification_record_repository.py:19-21` `records: tuple[NotificationRecord, ...]` + `next_cursor` = **애그리거트 루트의 컬렉션**. D29 자신의 판정 기준으로 재면 «남아야» 하는데 나가는 목록에 있다.
- `UsageQuotaDecision` — HEAD 에 도메인 타입으로 **존재하지 않는다**(migrations 0001/0005 에만 남은 삭제 모델).
- 반환형 외에 **오류 계약**도 갈 자리가 없다: `find_effective_at` 은 `ModelPriceNotFound`·`LlmMetaInternal`(도메인 예외)을 던지는 것이 계약이고 현행 구현이 그것을 import 한다(`llm_meta/infra_layer/repository/price_schedule_repository.py:12`).
- `usage_quota/…/read_usage_admission_query.py:88` 은 `find_current_buckets` 결과로 `FamilyUsageQuota` 루트를 재조립해 `admission_check`(93행)를 부른다 — 애초에 «도메인 우회 조회»가 아니다.
- 전수: 추상 메서드 178 · 전원 애너테이션 · 루트 클래스명을 담은 것 99 · `-> None` 36 · 비루트·비None 43.

**제안**: 판정 축을 「**domain_layer 타입을 하나라도 돌려주느냐**」로 옮기면 검사 ③과 판정 기준이 같은 말이 된다. `NotificationRecordPage` 는 «남는다»로 재분류하고 `UsageQuotaDecision` 은 빼며, 「58:11」을 그 기준으로 다시 내라. 옮기는 것들의 «불변식 소멸»(`CurrentUsageBuckets.__post_init__`)과 오류 계약 처리도 같이 적어야 한다.

---

### J8. 「폴더 이름이 곧 app_label」은 실측 0/16 이고, D15 의 ImproperlyConfigured 논거를 이 저장소가 반증한다
**렌즈**: 이행 가능성 · 장고 현실
**다시 열어야 할 결정**: **트리 54행** · **D15 결정②**

- 16/16 이 `apps.py` 에서 `label` 을 **명시 선언**하고, 그 값이 폴더 이름과 같은 곳은 **0건**이다. `application/accounts/infra_layer/django_accounts/apps.py:11-12` `name="application.accounts.infra_layer.django_accounts"` / `label="accounts"` (ai_chat:13-14, billing:7-8, llm_meta:14-15, pairing:38-39, parental_controls:11-12 … 16/16 이 `label = 폴더명.removeprefix("django_")`).
- D15 결정②의 논거(「orm/ 으로 두면 BC 마다 label 이 겹쳐 ImproperlyConfigured 가 난다 · 폴더 이름이 곧 label 이라 유일성이 공짜」)는 «label 을 선언하지 않을 때만» 참이다.
- 라벨에 매달린 것: `broccoli_server/settings/base.py:196 AUTH_USER_MODEL = "accounts.ParentModel"`, 마이그레이션 cross-app dependencies, `apps.get_model(` 89건, `templates/admin/usage_quota/…`.
- 트리 64행이 「`<app>` 은 폴더가 아니라 `apps.py` 의 label」이라고 **정반대로 정밀하게** 적어 두어, 54행만 읽은 사람과 64행을 읽은 사람이 다르게 읽는다.

**제안**: 54행을 「app_label 은 `apps.py` 가 **명시** 선언한다 — 폴더 = `django_` + label. 값은 BC 이름이다(실측 16/16)」로 고치고, D15 의 유일성 논거를 「모델은 설치된 앱 패키지 안에 있어야 해서 이 폴더가 곧 장고 앱이다」로 다시 세워라(그쪽은 실제로 참이다). 그리고 「이관 시 label 은 절대 바꾸지 않는다 — 폴더 경로(AppConfig.name)는 바꿔도 안전하다」를 이행 규칙으로 못박아라.
(재앙 시나리오는 규칙의 강제가 아니라 오독의 파생이므로 심각도는 중대.)

---

## 보통 — 사람마다 다르게 배치할 여지가 크다

| # | 문제 | 근거 | 손볼 자리 |
|---|---|---|---|
| B1 | **잎 규칙에 stdlib 면제선이 없다** | `models/**` 47파일의 비-django import 154건 중 stdlib 33건이 회피 불가(`typing` 31 · `uuid` 1 · `collections.abc` 1). `usage_record_model.py:4 import uuid`. (`__future__` 42는 ruff 가 강제하지 않고 `**/models/**` 를 린트에서 제외까지 한다. `enum` 5는 도메인 import 를 끊으면 같이 사라진다) | 트리 53행 · D20 검사① — 「django·표준 라이브러리·같은 폴더 말고」로 고쳐 쓴다 |
| B2 | **잎 규칙의 진짜 비용은 「값 두 번 적기」가 아니라 「조용한 괴리」** | 모델 47개 중 31개(66%)가 domain_layer 를 import. `ai_chat/…/turn_model.py:22-23` `max(len(kind.value) for kind in TurnActorKind)` · `:90 condition=Q(status__in=[status.value for status in TurnStatus])`. 파일 `:19-21` 주석이 「choices·CHECK 값의 단일 출처는 도메인 enum 이다 — 리터럴을 재선언하지 않는다」. import 를 끊으면 enum 을 고쳐도 모델이 안 변해 **makemigrations 가 아무것도 감지하지 못한다** | D15 「치르는 값」에 실패 양상과 「도메인 enum 값 집합 == ORM choices/constraint 값 집합」 테스트를 BC 마다 하나 두라고 적는다 |
| B3 | **애그리거트 루트가 없는 폴더 7개의 해체 방침이 없다** | 애그리거트꼴 48개 중 7개에 루트 없음 — `report/{child_conversation, child_lesson_fact, child_profile, curriculum_codebook, report_period}` · `managed_copy/copy_item_policy` · `delivery/phone_verification_sms`. 예: `child_profile/` = exception.py + VO 1 + port 1 셋뿐 | 트리 36행에 「루트가 없으면 애그리거트가 아니다 — 해체한다」와 목적지를 적는다 |
| B4 | **「트랜잭션은 애그리거트 하나를 넘지 않는다」가 실측 6건에서 거짓** | `accounts/…/add_child_command.py:51`(Family·Parent·Child) · `pairing/…/claim_pairing_command.py:115` · `pairing/…/cleanup_evicted_child_command.py:48` · `lessons/…/record_lesson_proposal_command.py:63,77` · `usage_quota/…/record_usage_command.py:186`. UoW 3/3 이 리포지토리를 속성으로 노출(billing:19 · products:15 · usage_quota:17-18, 독스트링 「기록과 bucket 을 아우르는 원자적 영속화 경계」) | 트리 36행 근거에 처리 방침을 적거나 「넘으면 결정 카드에 근거를 남긴다」로 낮춘다. D14 의 「uow.orders 방식을 안 씀」은 D31 예시(`unit_of_work.entitlements.save`)·현행 3/3 과 어긋나므로 문구 정정 |
| B5 | **fake 어댑터에 `<system>` 값이 없다** | 트리 71·72행이 external_system 을 «네트워크 너머 남의 시스템 · 벤더 하나 = 폴더 하나»로 정의. fake 3벌(fcm·sms·social)이 갈 곳이 없고 D33 접두사 목록(누구·기술)에 «Fake» 가 없다. 프로덕션 배선이다 — `settings/base.py:262·273·282` 가 `*_USE_REAL` 을 **기본 False**, `delivery/composition_root.py:76-88` 이 자격증명 누락·초기화 예외에서 FakeFcmPushGateway 폴백. 파일명 충돌은 실제로 1건(`OtpCodeGenerator`: Secure/Fake, `accounts/composition_root.py:168-173`) | 트리 71·72행 정의를 넓히거나 D33 에 「한 포트에 구현이 둘 이상이면 한 파일에 클래스를 나란히 둔다」를 적는다. `GoogleAppleSocialAuthGateway` 처럼 한 어댑터가 두 벤더를 처리하는 경우의 폴더명 규칙도 한 줄 |
| B6 | **한 어댑터가 두 BC 를 쓰면 폴더가 안 정해진다 + Callable 별칭 포트가 D33 검사의 사각** | `lessons/infra_layer/adapter/parent_registration_notifier.py` L24·27(accounts OHS) + L30·33·36·39(notifications OHS), **클래스 0건**·공개 표면은 L48 모듈 함수. 짝 포트도 클래스가 아니다 — `register_lesson_command.py:54 _PublishParentRegistration = Callable[..., None]`(composition_root.py:151 이 꽂는다). Callable 별칭 포트 7건(전부 lessons)이고 D26 이 그 배선을 「살아있는 예」로 인용했다 | 트리 69행에 「어댑터는 상대 바깥을 하나만 안다 — 둘 이상이면 상대별로 쪼개고 엮는 순서는 유스케이스가 갖는다」, D33 에 「포트·어댑터는 클래스로 선언한다(Callable 별칭 금지)」 |
| B7 | **api 가 아예 없는 BC 3개에서 D14 의 유일한 근거가 공전** | application_layer feature 44 · 파일 있는 api feature 22 · 이름 일치 19. api 0인 BC: delivery·llm_meta·report(app feature 15개). 이름 불일치 3(turn↔turn_streaming, checkout↔payment, product_catalog↔product) | D14 에 「1:1 은 api 가 있는 feature 에 한한다 · api 가 없는 feature 의 1차 축은 OHS `<service>` 또는 어드민이 정한다 · 이름은 어느 쪽으로 통일한다」를 적는다 |
| B8 | **표현 전용 모듈에 잎 이름이 없다** | `ai_chat/presentation_layer/sse/sse_stream_renderer.py`(108줄) · `lessons/…/lesson_list_cursor_codec.py` · `notifications/…/notification_cursor_codec.py` · OHS `{delivery,notifications,report}/published_service/*/_exception_translation.py` 3개. (path_params 2개는 schema_in 자리, `*_openapi.py` 2개는 D27 이 없애기로 한 것) | D28 이 application_layer 에 단 「쪼갠 모듈도 이 안에 둔다」 노트를 `api/<feature>/` 와 `open_host_service/<service>/` 에도 대칭으로 단다 |
| B9 | **celery 는 `related_name` 으로 `cron_job/` 에 닿지 못한다** | `find_related_module` 이 `import_module(f'{package}.{related_name}')` 를 부르는데 package = AppConfig.name = `application.<bc>.driven_layer.django_<bc>` 라 위로 못 올라간다. `packages=`(콜러블 허용)·`imports=` 만 유효. 또 `cron_job/` 은 패키지라 `<job>.py` 가 `__init__.py` 재수출 없이는 import 되지 않는다 | D22·D26 ①의 「`autodiscover_tasks(related_name=…)`·imports 로 우리가 정한다」를 「packages= 콜러블 또는 imports= 로 정한다」로 정정하고, 트리 89행에 재수출 한 줄 |
| B10 | **ChatPipeline 이 D32 「그대로 둔다」와 D13 검사① 사이에 낀다** | `ai_chat/domain_layer/turn/value_object/chat_pipeline.py:5,8,11` 이 포트 3개를 필드로 갖고, 그중 `conversation_summarization` 은 conversation_room 소속 → D32 적용 후 `turn/value_object/` → `conversation_room/domain_service/` 라는 애그리거트 횡단 비루트 import 가 남는다 | D32 의 「ChatPipeline 은 그대로다」를 재검토 — 세 협력자를 한 값 객체로 묶는 이상 그 값 객체는 애그리거트에 속할 수 없다 |
| B11 | **schema 63 은 BC층만 센 값** | 깊이1 63 / 깊이2+ 34 / 합 97. 사용 68 · 미사용 29. feature 하위 폴더를 이미 가진 BC 6개(ai_chat·billing·entitlements·managed_copy·parental_controls·usage_quota) | D8 08-06 재검에 측정 범위를 명시. 결론(2개 이상 공유 0건)은 97개로 넓혀도 안 바뀐다 |
| B12 | **ACL 이관이 상대 BC 의 OHS 개설에 선행 의존** | `delivery/infra_layer/acl/pairing_push_endpoint_directory_adapter.py:12` 가 pairing ORM 을 직접 읽고(docstring 이 「기존 미이주 패턴」이라 자백) L18-22 가 포트 3개를 한 클래스로 구현. `ls application/pairing/published_service/` = `__init__.py` 뿐. 포트 여럿을 한 파일이 구현하는 곳은 **2개**다(+ `ai_chat/infra_layer/acl/usage_quota_metering_adapter.py`) | 규칙은 D20 검사④·D15 검사③이 이미 잡는다. 이관 «순서»를 부채 목록에 올리고, 한 어댑터가 여러 포트를 만족할 때의 이름 규칙 한 줄 |

---

## 사소

- **S1** — `driven_layer/<capability>.py` 행이 91행 표에서 빠졌다. 규칙은 네 곳에 있다(PART1 [driven] · D17 · D18 판별법 4번 · D33). `infra_layer/adapter/` 30파일 중 벤더 SDK 를 쓰는 9개만 external_system 행이 있고 21개가 이 행을 필요로 한다. → 74행 위에 한 행 추가.
- **S2** — BC 레벨 `exception.py` 12개는 «표류»라는 D27 ①의 명시 판정이 이미 있다(11 vs 12 는 llm_meta 커밋 시차). 남는 것은 D27 ③의 「폴백은 도메인 base 단위 catch」가 애그리거트 base 단위로 잘게 갈린다는 문구상 긴장뿐(비테스트 catch 8건).
- **S3** — D4 는 65, D24 는 55, D25 는 43, D31 은 13을 셌는데 **D11 만 이관 비용 수치가 없다**. 실측: driving→domain 133건/58파일 · dto_out 이 없는 유스케이스 28개 · 애그리거트 루트를 잡는 driving 14파일(schema_out 11 + OHS 3).
- **S4** — `AUTH_USER_MODEL` 을 소유하는 BC 는 PART1 [root] 의 「폴더를 지우고 부팅해 본다」가 문자 그대로는 불가능하다(참조 11건은 전부 accounts 안이고 밖은 `settings/base.py:196` 하나라 판정 문장 자체는 통과한다). 표현 보완.
- **S5** — feature 를 가로지르는 공유물 3건(lessons)은 27행 노트로 닫히지만, D14 의 「DTO 는 자기 폴더 안에서만 쓰인다」와 어긋난다. 문구 정정.

---

## 갈래 — 무엇을 다시 열고, 무엇을 목록에 넣나

### A. 결정을 다시 열어야 하는 것 (10건)
| 결정 | 왜 |
|---|---|
| **D11 결정③** | C1 — D27 과 동시에 참일 수 없다. 사정거리를 「예외 모듈만」으로 좁힐지 D27 을 폐기할지 |
| **D24 이름** | C2 — `platform/` 이 stdlib 를 가려 부팅이 죽는다 |
| **D13 검사 ②③ + 트리 48·50행** | J2 — value_object·exception 면제가 없어 켤 수 없다 |
| **트리 25·32·33행 + D27 ① + D33** | J3 — 포트 실패 어휘·페이로드의 칸과 검사 대상 범위 |
| **D13 결정① · D32 결정①** | J4 — 포트 소유자 역전이 플러그인 blocker 와 정면 반대. 「어느 쪽이 정본인가」를 결정 카드로 |
| **D6 / D11** | J5 — 결선 주입 경로가 없다 |
| **D14** | J6 — 「밀어낼 일이 없다」 전제가 SSE 로 반증. 출력 포트 예외를 열지 말지 |
| **D29 결정①③④** | J7 — 판정 축을 「domain_layer 타입을 돌려주느냐」로. 「58:11」 재산출 |
| **트리 54행 · D15 결정②** | J8 — app_label 논거 재작성 |
| **D32(ChatPipeline) · 트리 71·72행(fake) · D22·D26(celery packages=)** | B5·B9·B10 — 각 한 줄 정정 |

### B. 10번(코드 고칠 목록)에 추가하면 되는 것
1. `broccoli_server/` → `application.*` **41건**(api.py 28 · urls.py 13) → `register_<bc>_api(api)` 명시 호출. urls.py 의 `# noqa: F401` 11줄 포함
2. driving→domain **133건/58파일** — ①28개 유스케이스에 dto_out 신설 → ②schema_out 14파일의 `from_domain` → `from_result` → ③D11 검사 켜기 (순서 명시)
3. 컨트롤러 48파일의 composition_root 직행 → 결정된 주입 방식으로 치환
4. ACL 이관 순서 — pairing·accounts 가 OHS 를 먼저 연다(delivery ACL 1 · pairing ACL 2 · parental_controls ACL 1)
5. `parent_registration_notifier.py` 를 포트 둘로 분해, 엮는 순서는 `register_lesson_command` 로
6. Callable 별칭 포트 7건(lessons) → 클래스 선언
7. 도메인 포트 54파일 이동 시 **동거 클래스 16개 분해**(값 객체 12는 domain 잔류, 예외 4는 D27 ① 재판정 필요)
8. `usage_quota/domain_layer/usage_reservation/` 빈 껍데기 3디렉터리 삭제
9. 애그리거트 아닌 개념 묶음 7폴더 해체 + `delivery/phone_verification_sms` 폴더 개명
10. **0번 PR**: 마이그레이션의 소스 모듈 참조 제거 — `delivery/…/migrations/0001_initial.py:3-4,49`(도메인 enum 을 리터럴로 동결) · `accounts/…/0001_initial.py:3,42`(ParentManager 인라인). 층 이름 변경 전에
11. `lesson_openapi.py` · `lesson_list_openapi.py`(openapi_extra 보충) 제거 — D27 이 이미 금지
12. 미사용 schema **29클래스** 정리 판정
13. BC 마다 「도메인 enum 값 집합 == ORM choices/constraint 값 집합」 테스트 1개
14. 다중 애그리거트 트랜잭션 6건의 처리(경계 재검 또는 근거 기록)
15. OHS `_exception_translation.py` 3파일 · SSE 렌더러 · 커서 코덱 2 의 최종 자리 확정

### C. 문서 수치 정정만 (결정 불변 — 어느 쪽에도 안 들어가서 따로 뗀다)
J1 의 표 12줄. 트리 91행 중 **최소 10행**과 PART1 4개 절, D8·D25·D29·D34 의 수치가 대상이다. 정정 후 각 값 옆에 «세는 명령»을 붙여라 — 이 문서는 수치가 곧 논거라 재현 불가가 곧 논거 붕괴다.

---

## 총평

방향 자체는 살아남았다. 애그리거트 1차 축, driving/driven 이름, port 를 응용으로 올린 것, error_out 을 BC 당 한 파일로 둔 것 — 이 큰 판단들은 8개 렌즈 어느 쪽에서도 무너지지 않았고, 오히려 재측정이 논거를 강화한 곳이 여럿이다(15/15 → 16/16, 37:6 → 어느 기준으로도 두 층 배치를 지지).

무너진 것은 «규칙 문장의 정밀도» 두 층이다. 첫째, 안쪽 규칙 셋(D11 의 「만」, D13 검사 ②③의 「루트만/아무것도」)이 **너무 세게 쓰여** 자기가 지키려던 다른 결정(D27 의 예외 번역, 트리 47행의 애그리거트 예외)을 스스로 위반으로 찍는다 — 여기는 문장을 좁히는 일이고, 좁혀도 검사는 여전히 grep·AST 한 줄이다. 둘째, «포트의 소유자»(D13/D32 vs 플러그인 §2)와 «platform 이라는 이름»은 좁히기로 안 되고 결정을 다시 내려야 한다.

가장 급한 것은 C2 다 — 이름 한 줄이 첫 배포에서 서비스를 세운다. 그다음이 C1 이다. 이 둘 말고는 전부 세부이고, 열어야 할 결정 10건 중 8건은 «한 줄을 좁히거나 한 줄을 더하는» 규모다. 트리를 다시 그릴 이유는 발견되지 않았다.

Serena: skipped — 저장소 읽기 전용 대조·문서 종합이라 기본 도구(Read/Grep/Bash)로 충분했다.