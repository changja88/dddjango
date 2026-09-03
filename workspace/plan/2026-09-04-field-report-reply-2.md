# 현장 보고 회신 2 — 제보 수정 단계(D·E·F·G·H) 처분 + spring_dream_server 수리 가이드 (2026-09-04)

대상 보고: `2026-09-03-field-report-spring-dream-typecheck.md` D·E·F·G·H(발주자 세션 + dddjango 측 추기). 절차: 루브릭 `2026-09-04-field-report-repair-2-rubric.md` · 계획 `2026-09-04-field-report-repair-2-plan.md` · 증거·리뷰 `workspace/eval/field-report-2/`. 브랜치 `fix/field-report-2`(main 로컬 머지 예정 · 릴리즈는 사용자 요청 시 `make release` — v2.17.17 후보).

## 1. 처분 표

| # | 보고 항목 | 판정 | 플러그인 처분 | 발주측 할 일 |
|---|---|---|---|---|
| D | 항상 raise 도우미 `-> None` | 성립(소) — 형상 n=2/2저장소 · spring `_fail` 은 발주측 96e8719 로 이미 수리 | R-3446 신설(implementation-python §4.4 «항상 `raise` 로 끝나는 도우미는 `-> NoReturn`») | 없음(완료) |
| E | `Any` 정책 부재 | 성립 — «주석 존재» 규범이 `x: Any` 로 충족됨 · 막는 도구 없음(ANN401 무효 · mypy 범위가 `application/` 제외) | R-3447/R-3448 신설(하우스룰 §4 «`Any` 는 검사 포기 — 어디에도 쓰지 않는다 · 경계는 `object`/정확 타입으로 받아 즉시 좁힘» 무조건형) + 검사기 **#645**(시그니처 bare `Any` = 차단 · 제네릭 안·변수 = ⓓ 후보 → 감사 입력 동봉) | **§3 참조** — 릴리즈 설치 후 application 시그니처 `Any` 10건(프로덕션 8 + factories 2) |
| F-1 | composition root 주입 callable 시그니처 불일치 | 1레인 특이(표본 외 27 BC 불일치 0) — 정적 검출 가능 | R-0719 rev2(django-ninja §2.3 «주입 callable ≡ 꽂히는 자리의 Protocol/`Callable` 시그니처 · 부족 인자는 팩토리 본문 안 `partial`/클로저») · 검사기 없음 | 없음(HEAD `partial` 배선 = 준수) |
| F-2 | 실배선 테스트 부재 | 부재가 기본 상태(BC 21/28) — «BC 마다 1개 강제» 는 quota 라 기각 | R-3450 신설(discipline-tdd §5.5 보호 대상 목록 «composition root 실배선 정합» — 자격 항목 · 강제·소급 없음) · `discipline-test` 스킬은 존재하지 않음(착지 정정) | 없음 |
| G | boundary-imports 블록에 잎→port 예외 import 결손(발견 ⑪) | 성립 — 잎→port 행 블록 0/7 · #93 실발화 5레인 · 뿌리 = R-3427 «경계» 미정의 | R-3427 rev4(경계 3분류 — BC 내부 층 경계 중 검사기 판정 항목도 행 의무) + **R-3449 신설**(architecture-ddd §3.6 «port 예외는 use case 가 도메인 예외로 번역 · 잎은 port 예외 **타입**에 의존하지 않는다 — 재수출 경유 포함») | **§2 참조** — 4 BC · 5파일 · except 13(규범 빚 · 차단 없음) |
| H | pre-content 골격 빈 파일 ↔ «클래스 하나» 상충(발견 ⑫) | 성립(재현 결정적 · «규범 간 모순» 은 과장) — 사용자 결정 «빈 파일 무검사» | #219/#635 가 내용 없는 골격 파일(0바이트·docstring/주석뿐)을 건너뜀 + R-3181 rev3(«빈 파일의 내용 규칙은 내용이 생긴 뒤 · 삭제로 red 해소 금지») | 없음(카탈로그 골격 상태 재실행 5→0) |

정정(원문 보존 · 현장 보고 «정정 추기» 참조): `discipline-test` 스킬 부재 · «테스트 26곳» 미재현(14+3) · «13건 증폭» 은 43e9628 시점 · «시그니처 `Any` 47 · application 0» 은 ANN401 기준(재집계 8/10) · «왕복 2회·≈14분» = 게이트 red 2회·파일 왕복 1회·13:42.

## 2. G 수리 가이드 — port 예외 재수출 경유 catch 4 BC (spring_dream_server 쪽)

### 2.1 무엇이 문제인가

- 규범(R-3449 · architecture-ddd §3.6): **port 예외의 번역은 use case 가 진다.** use case 는 port 예외를 잡아 **도메인 예외**(`domain_layer/<aggregate>/exception/<exception>.py` 칸)로 번역하고, driving 잎(컨트롤러·OHS)은 그 도메인 예외만 분기한다. 잎은 port 예외 **타입**에 의존하지 않는다 — 직접 import(#93 발화)든 **use case 모듈의 `__all__` 재수출 경유**든 같다(#93 은 import 경로만 보므로 재수출은 검사기가 못 본다 · 그래서 규범만 있고 차단은 없다).
- 현재 4 BC 는 use case 모듈이 port 예외를 `__all__` 로 재수출하고 OHS 가 그것을 `except` 한다. import 경로만 use case 를 거칠 뿐 OHS 가 port 예외 타입에 묶여 있다 — port 가 예외 이름·계층을 바꾸면 OHS 가 같이 깨지고, «use case 는 실패를 잡지 않고 전파한다» 는 docstring 이 곧 «번역 책임 방기» 다.
- 두 명세(notification-bc · fortune_calculation-2)가 이 방식을 «#93 을 피하는 합법 창구» 로 명문화했다 → 명세 문구도 함께 고친다(아래 2.4).

### 2.2 대상 전수 (⑤ C 실측 · HEAD f5ee428)

| BC | OHS(잎) — except 자리 | use case 재수출 모듈 | 재수출 이름 |
|---|---|---|---|
| query_translation | `driving_layer/open_host_service/translation/translation_service.py` :89·91·93·95·97·99 (6) | `application_layer/translation/translate/translate_use_case.py` `__all__` | `Glossary*` ×4 · `TranslationConfiguration*` ×2 |
| fortune_intent | `driving_layer/open_host_service/request_understanding/request_understanding_service.py` :86·127·160 (3) | `application_layer/request_understanding/classify_counter_message/classify_counter_message_use_case.py` | `IntentGenerationConfigurationFailed` |
| fortune_calculation | `driving_layer/open_host_service/chart_calculation/chart_calculation_service.py` :170·172 (2) | `application_layer/chart_calculation/calculate_chart/calculate_chart_use_case.py` | `LeapMonthAbsent` · `PlaceCodeUnknown` |
| fortune_calculation | `driving_layer/open_host_service/place_directory/place_directory_service.py` :54 (1) | `application_layer/place_directory/confirm_place_code/confirm_place_code_use_case.py` | `PlaceCodeUnknown` |
| notification | `driving_layer/open_host_service/email_notice/email_notice_service.py` :40 (1 · 2이름) | `application_layer/email_notice/send_email_notice/send_email_notice_use_case.py` | `EmailNoticeRenderingError` · `EmailNoticeTransportError` |

kkebi-server 12 BC 는 0(해당 없음).

### 2.3 고치는 모양 — 저장소 안 정답 선례 = accounts

`accounts/application_layer/verification_code/request_verification_code/request_verification_code_use_case.py` :113~117 이 정답이다.

```python
# use case — port 예외를 잡아 도메인 예외로 번역한다
from application.accounts.application_layer.port.verification_email.exception import VerificationEmailDeliveryFailed
from application.accounts.domain_layer.verification_code.exception.verification_notice_undeliverable import VerificationNoticeUndeliverable

try:
    self._email.send(...)
except VerificationEmailDeliveryFailed as delivery_failure:
    raise VerificationNoticeUndeliverable("Verification notice could not be delivered.") from delivery_failure
```

```python
# 잎(컨트롤러·OHS) — 도메인 예외만 안다 (verification_code_controller.py :55·:127)
from application.accounts.domain_layer.verification_code.exception.verification_notice_undeliverable import VerificationNoticeUndeliverable
try:
    use_case.execute(command)
except VerificationNoticeUndeliverable:
    raise <published 예외>() from None
```

BC 마다 절차는 셋이다.

1. **도메인 예외 칸에 번역 대상 예외를 둔다** — `domain_layer/<aggregate>/exception/<exception>.py`(트리 69~70행 · 파일 하나에 클래스 하나 · 이름은 도메인 어휘로 — «렌더 실패»가 아니라 «통지를 보낼 수 없다» 식). 예: notification → `domain_layer/email_notice/exception/email_notice_undeliverable.py :: EmailNoticeUndeliverable`. 이미 있는 도메인 예외가 뜻이 같으면 재사용한다.
2. **use case 가 잡아 번역한다** — `execute()` 안에서 port 호출을 `try/except <port 예외>` 로 감싸 도메인 예외를 `raise … from` 한다. `__all__` 의 port 예외 이름을 **지운다**(top-level ClassDef 하나 · #635 그대로). docstring 의 «실패는 잡지 않고 전파한다» 도 함께 고친다.
3. **잎은 도메인 예외만 분기한다** — OHS/컨트롤러의 `except (port 예외…)` 를 `except <도메인 예외>` 로 바꾸고 published 예외로 번역한다. use case 모듈에서 port 예외를 import 하는 줄을 지운다.

port 예외가 여러 개면 «잎이 다르게 반응해야 하는 것» 만큼만 도메인 예외를 나눈다(query_translation 6개가 전부 같은 published 예외로 접히면 도메인 예외 1~2개면 된다).

### 2.4 함께 고칠 것

- **명세 2건**: `.dddjango/20260902-1458-notification-bc/design-spec.md`(«use_case 모듈이 합법 창구») · fortune_calculation-2 명세(«재수출 선례»)의 해당 문구를 «use case 가 도메인 예외로 번역 · 잎은 도메인 예외만 분기» 로 개정한다 — 개정하면 Phase 1 pre-gate 를 재실행하는 것이 규칙이나, 이 수리는 코드 변경이 먼저이므로 **수리 발주의 G1 명세에서 boundary-imports 블록에 잎→도메인 예외 import 행을 적는다**(R-3427 rev4 — 도메인 예외 import 는 #92/#95 허용 칸이라 예보 green).
- **테스트**: OHS 단위 테스트가 port 예외를 던지는 fake 로 published 예외를 검증하고 있으면, fake 는 그대로 두고 기대 경로가 «port 예외 → 도메인 예외(use case) → published 예외(OHS)» 로 바뀐 것만 반영한다. 도메인 예외 번역은 use case 단위 테스트가 보호한다(§5.5 «boundary adapter 의 … known failure 번역» 자격).
- **순서·규모**: 4 BC 를 한 발주(리팩터링 슬라이스 · 기능 변화 없음)로 묶어도 되고 BC 별로 나눠도 된다. 예상 = BC 당 파일 3~4개(도메인 예외 +1~2 · use case · OHS) · 테스트 갱신. 릴리즈 v2.17.17 설치 후 발주해야 R-3449·R-3427 rev4 가 레인에 실린다(설치 전에는 리뷰어가 옛 규범으로 본다).

### 2.5 하지 말 것

- OHS 에서 port 예외를 직접 import(#93 차단) · use case 모듈 `__all__` 재수출 유지(규범 위반) · `except Exception` 으로 뭉개기(#69 계열·정확 타입 원칙) · `application_layer/<area>/exception.py` 신설(**트리에 없는 칸 — #490 red**).

## 3. E 안내 — 릴리즈 설치 후 `Any` 정리 (spring_dream_server 쪽)

- 검사기 #645 는 **함수 시그니처(인자·`*args/**kwargs`·반환)의 bare `Any`** 만 차단한다(`Optional[Any]`·`Any | None`·문자열·별칭·`typing.Any`·`Any` 가 섞인 합집합·`Annotated[Any, …]` 포함). 제네릭 안(`dict[str, Any]`)·변수·클래스 속성의 `Any` 는 ⓓ 후보(exit 불산입 · 감사 입력)다.
- 소급 대상(application/* · HEAD): **10건** — Django 스텁 오버라이드 미러 8(Form `__init__(*args: Any, **kwargs: Any)` 6 · Model `update(**kwargs)`/`delete(using)` 2) + `test/factories` 2(`translations(**kwargs: Any)`). 전부 `object` 로 바꾸면 mypy strict 가 override 호환으로 통과한다(django-stubs 플러그인 구성 상태에서 실측). 기존 파일은 G2 귀속(N∖L)이라 손대지 않는 한 red 가 아니다 — Phase 0 빚 스캔에 잡히고, 그 파일을 `update` 하는 레인부터 red.
- 변수 `Any`(`account_user: Any = request.user` · admin `cleaned.get()` 값 · JSON 순회)는 후보 채널이다 — 규범은 «`object`/정확 타입으로 받아 받는 즉시 좁힌다(`TypeIs`·`isinstance`·`type() is`) · JSON 은 `Mapping[str, object]`» 다. 강제 아님 · 감수자 판단.
- ruff `ANN401` 이 select 뒤 ignore 로 무효화돼 있다(양 저장소) — 플러그인 검사와 독립이지만, 켜면 같은 방향이다.
