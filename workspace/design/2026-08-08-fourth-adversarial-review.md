# 4차 적대적 리뷰 — 2026-08-08

**대상** — 정본 `docs/work_flow.html` (sha `576279740d8c6a0e` · 371,227자 · 트리 117행 · 툴팁 44)
· 기록 `workspace/design/2026-08-07-decision-record.md` (266,628 B · 카드 44장 D3~D46)

**렌즈 12 병렬** — C(내부 모순) · O(과적합) · DDD · CA(클린) · HEX(헥사고날) · EDA · G(누락·오작성) · A(비대칭·안 적힌 전제) · CHK(검사 가능성) · S(스윕 누락) · PY(파이썬·장고 사실) · SC(시나리오)

**공통 규칙** — 파일 수정 금지 · 「좋아 보인다」 금지(충돌하는 두 문장을 둘 다 인용) · 실측을 근거로 삼지 말 것 · 못 찾으면 「못 찾았다」

---

## ③c HEX — 헥사고날 원전 정합 ✅ 도착

원전 둘을 직접 읽었다 — [alistair.cockburn.us/hexagonal-architecture](https://alistair.cockburn.us/hexagonal-architecture/) · [Budapest 2023 슬라이드 PDF](https://alistaircockburn.com/Hexagonal%20Budapest%2023-05-18.pdf) · 보조 [Garrido de Paz](https://jmgarridopaz.github.io/content/hexagonalarchitecture.html)

### HEX-1 · 1차 포트를 «바깥»에 배정했다 — **major**

**어디** — 정본 rd-40 `<capability>/` 의 dim 주석

> 원전의 포트는 구동하는 쪽에도 있다(1차 포트) — 이 트리는 폴더 낱말 `port/` 를 **구동되는 쪽에만** 쓰고, 1차 쪽 포트 노릇은 `driving_layer/` 의 계약(스키마·컨트롤러 시그니처)이 진다.

**원전** — *"Driving ports: **The app owns the interface** | Driven ports: The app owns the interface"* · *"B 'implements' the interface. **A owns the interface definition.**"* (slides 8·15·16)

**문제** — 어긋남을 «표기»한 것은 정직한데 **표기 내용이 틀렸다.** `schema_in/`·`schema_out/`·컨트롤러 시그니처는 **어댑터 쪽 물건**이라 「앱이 소유하는 인터페이스」가 아니다. 그리고 **트리는 이미 앱 소유 1차 계약을 갖고 있다** — `<use_case>_use_case.py`(진입점 하나) + `dto_in.py` + `dto_out.py` 가 정확히 Cockburn 의 provided interface 다.

**추가 결함** — 이 표기는 ⑴ 한 행의 `<span class="dim">` 안에만 있고 ⑵ `driving_layer/` 패널엔 **한 글자도 없고** ⑶ **결정 카드가 없다**(기록 전문에 「1차 포트」·「driving port」 **0건**). **44장 중 이 결정만 근거 없이 산다.**

### HEX-3 · 「한 포트 = 한 어댑터」로만 말한다 — **major**

문면이 **「1:1」 13종 + 「갈아 끼운다」**로만 쓰여 있고, **한 포트에 어댑터가 «동시에» 여럿 꽂히는 상태에 이름·규칙·예시가 0건**이다(「1:N」·「어댑터가 여럿」 정본 0건).

**원전** — Blue Zone 도해가 정확히 그 그림이다: `For obtaining rates` → **Test Double + File adapter**, `For paying` → **Test Double + Wallet Adapter**, `For using` 포트 하나에 **GUI 1 · GUI 2** 동시(slides 10·11·21). *"Given a port, there may be an adapter for each desired technology that we want to use."*

**정직한 단서** — 구조적으로는 막히지 않는다(`external_system/toss/` ↔ `external_system/stripe/`). 1:1 규칙이 **구현→선언 단방향**이라 N:1 을 안 막는다. 문제는 **문면이 반대로 읽히게 써 놨다**는 것.

### HEX-2 · 「Cockburn 의 2차 행위자 표준 예 = DB·시계」 — **시계를 못 찾았다** · major

**DB 는 축자 확인** — *"The natural test adapter to substitute for a secondary actor **such as a database** is a mock."*
**시계는 페이지·2023 슬라이드 어디에도 없다**(`clock`·`timer` 0건). 원전이 드는 예는 database · flat file · SQL adapter · coin box · medication dispensers.
**이 한 문장이 D37·F6 의 «유일한» 원전 근거로 다섯 자리에 복제돼 있다.**

### HEX-4 · 「갈아끼워도 앱이 안 바뀐다」의 검사가 `framework/` 에만 — minor

`framework/<technology>_adapter.py` 엔 「`composition_root` 밖에서는 아무도 import 하지 않는다」가 있는데 **`driven_layer/adapter/` 엔 없다**. 남는 구멍은 **어댑터↔어댑터**. **D45 자신의 기준(「약속 + 검출 기계가 한 세트」)을 이 자리엔 안 걸었다.**

### HEX-5 · `configurable dependency` 를 Cockburn 에게 귀속 — minor

Cockburn 페이지·슬라이드에 **0건**. 그 낱말을 정의로 갖고 있는 것은 **Garrido de Paz**. Cockburn 이 같은 것을 말하는 자리의 낱말은 **`configurator` (aka Composition Root)**(slide 15).

### HEX-6 · 「층 이름을 안 쓴다」는 자를 한쪽에만 댔다 — minor

`adapter_layer/` 는 「Cockburn 은 «어댑터»를 층 이름으로 쓰지 않는다」로 기각하면서 `driving_layer/` 는 「Cockburn 의 `driving` 이 정확하다」로 채택했다. **원전의 결합은 driving/driven *adapters* 이지 *layer* 가 아니다.**
**기록은 이미 실토하고 있다** — 「«driving adapter»가 Cockburn 의 결합이고 «driving layer»는 우리가 만든 결합이다」. **그 실토가 정본엔 없다.**

### 정합 확인 셋

- **★ D45 의 Cockburn 인용 넷이 전부 축자 일치** — Motivation 문단(말줄임 위치까지) · *converts … passes it to* · *converts … and vice versa* · *'the other side' of the application*. **「바꾸고·부르고·바꾼다」는 *converts … and vice versa* 의 정확한 번역이고 「약속+검출 기계」 독해도 저자의 진단 그대로다.**
- **`port/<capability>/` 를 «대화» 폴더로 만든 것** — *"A port identifies a purposeful conversation."* · *"We name the ports for their purpose: 'For_doing_something'."* · *"Each port can have multiple function calls."* **D46(이름에서 누가·언제·어떻게를 뺀다)까지 같은 방향.**
- **D44(계약은 ABC, 구현은 상속)는 헥사고날과 충돌하지 않는다** — *"A 'requires' this interface. **B implements it.** A owns the interface definition."* 갈아끼움을 해치는 것은 «구현이 계약을 아는 것»이 아니라 «앱이 구현을 아는 것»이고, 후자는 전역 제약 ①이 막는다.
- (보너스) D37/F6 의 **DB 정정 자체는 정합** — 「DB 는 바깥 행위자가 아니다」는 확실히 오독이었고 원문이 직접 반박한다.

---

## ① C — 내부 모순 ✅ 도착 (발견 17건)

### ★ C-1 · **D45 가 D14 를 정면으로 금지한다** — blocker

- 정본 `adapter/`(오늘 박음): **「도메인 예외를 던지면 위반」** *포트 예외로 «번역해서» 던진다*
- 정본 `unit_of_work/`: 「저장 실패는 여기 안 온다 — **업무 의미가 있으면 도메인 예외**, 재시도 판정은 `framework/`, 나머지는 선언하지 않는다」
- 기록 D14: 「업무 의미가 있다 — 중복 · 낙관적 락 충돌 → `domain_layer/<aggregate>/exception/` — **어댑터가 번역해서 던진다**」

**더 나쁜 점** — 번역할 «포트 예외»가 리포지토리에는 **존재하지 않는다.** 같은 D14 가 「`exception.py` 는 여기 두지 않는다」로 UoW·리포지토리 쪽 실패 선언 자리를 없앴다. **즉 오늘 박은 규칙은 지킬 수 있는 대상이 없다.**

**처분안 갈래** — ⓐ `persistence/repository/` 를 명시 예외로 ⓑ 리포지토리 실패 선언 자리를 열어 D14 표를 바꾼다

### ★ C-2 · 2장 흐름이 「사실을 무엇으로 실어 나를지 **아직 정하지 않았다**」 — blocker (규율 ⑤)

D40 이 정했는데 흐름 두 자리가 미정이라고 적고 있다(⑧ 스텝 + 유스케이스 코드 주석).

### ★ C-3 · driving 탭 산문이 한 문단 안에서 자기를 부정한다 — blocker

앞: 「자식은 **넷** — `api/`·`open_host_service/`·`cron_job/`·**`event_subscription/`**」
뒤: 「**셋**을 가르는 축은 «누가 나를 부르나» 하나다 … **넷째 입구가 필요해 보이는 순간은 … 새 칸이 아니라 «입구에 로직 금지» 위반이다**」

### C-4~C-9 (major)

| | 무엇 |
|---|---|
| **C-4** | `event/` 칸의 «규칙»(「소비자가 있나로 묻지 않는다」) ↔ «무엇이 오나»(「이 BC 안에서 **읽히는** 사실만」) |
| **C-5** | 기록 **D13** 이 「칸을 열지 않는다 · 자리가 없다」를 **반전 표식 없이** 결론으로 들고 있다(D34 엔 붙어 있는데) |
| **C-6** | 전역 제약 ③은 「관문 **또는 공표된 사실**」로 고쳐졌는데 **D34 툴팁**은 「누가 듣는지 모르는 채 발행 = 관문 없이 넘는 것 = **정의상 금지**」를 그대로 들고 있고, 반전 주석이 「바뀐 것은 …뿐」이라 **아직 유효하다고 독자에게 말한다** |
| **C-7** | BC 루트 패널 「**여섯** 가지만 온다 · 일곱째는 없다」 ↔ root 탭 「이 **일곱**이 전부다」 |
| **C-8** | `<capability>_port.py` 패널이 **D41 이전** 규칙(「파일 이름은 폴더와 같고」 · `email_sender.py`)을 그대로 |
| **C-9** | `<technology>_adapter.py` — «규칙»은 「**경로를 안 봐도 된다**」, «무엇이 오나»는 「**경로만으로 선다**」 |
| **C-10** | ★ 기록 **D33 의 «검사 ④»** — 「`Port`·`Adapter`·`Gateway` 는 **파일 이름에 나오지 않는다**」. 반전 주석은 산문 절에만 붙고 **집행 문장은 안 갔다.** 4번 명세가 카드의 «검사» 절을 긁는 구조라 **이 한 줄이 D41 전체를 되돌릴 수 있다** |
| **C-11** | 기록 **D14 결정 ①** 이 아직 형제 셋(`transaction/`) · 검사 한 줄도 옛 폴더 이름 |
| **C-12** | `framework/broker/` 가 **«계기» 없이 자격만으로** 섰는데, 계기 면제는 `<technology>/` 에만 있다. 101행 판정(「`*_port.py` 가 있으면 «능력»」)으로 재면 broker 는 «능력»이 되어 「자격만으로는 안 올린다」에 걸린다 |
| **C-13** | domain 탭 「밖으로 나가야 하는 알림이면 그건 처음부터 **Port** 다」 — D40 의 두 축(커맨드/사실) 이전 결론 |
| **C-14** | 2장 흐름 ⑤ 가 `exception.py`(파일)를 가리킨다 — T28 이 폴더로 뒤집은 자리. **D44 가 세운 「스윕은 2장 흐름까지」를 또 놓쳤다** |

### minor
- **C-15** 2장 예시의 경로(`order_already_canceled.py`)와 클래스(`OrderAlreadyShipped`)가 다른 사실 — 정본 예시가 자기 규칙(「이름이 곧 서술문」)을 어긴다
- **C-16** 기록 D40 의 `framework/broker/broker.py` — 트리는 `broker_port.py`
- **C-17** 3장 수치 — 4번 「471」 ↔ 5번 「447 개 중」 · 「결정 카드 32/38장」 ↔ 실제 툴팁 **44**

---

## ③b CA — 클린 아키텍처 원전 정합 ✅ 도착 (발견 9건)

**먼저 — T20 정정은 실제로 반영돼 있다.** 정본이 「이 문장은 Evans 의 것이다 · Martin 의 Use Cases 링은 반대로 «application-specific business rules» 가 이 층에 산다 · 이 트리는 **Evans 쪽을 채택**」으로 갈라 적었고 원전 대조도 통과. **다만 같은 병의 잔재가 넷 남았다.**

### ★ CA-1 · `framework/<capability>_port.py` — **의존 규칙이 반대로 걸려 있다** · blocker

- 정본: 「클린이 가장 바깥 링을 부르는 이름(**Frameworks & Drivers**)을 그대로 썼다」
- 같은 칸 규칙: 「**BC 의 유스케이스는 이 파일만 import 한다**」
- 원전: *"Nothing in an inner circle can know anything at all about something in an outer circle."*

**가장 안쪽(유스케이스)이 가장 바깥이라 선언한 칸을 import 하도록 «규칙으로» 강제한다.** `framework/broker/broker_port.py` 도 같은 모양.

**★ D37·D44 가 이 위에 논거를 쌓았다** — D37: 「어댑터만 올릴 수도 없다 — 포트를 상속해야 하니 «framework → application 0건»이 첫 줄에서 깨진다」. **클린 기준으로 그 «깨짐»이야말로 정상**(바깥이 안쪽을 안다). **D44 가 상속을 강제해 틀린 전제를 코드로 봉인했다.**

**처분 갈래** — ⓐ `framework/<capability>/` 의 포트를 BC 밖 «안쪽» 자리로 내리고 `framework/` 엔 구현만 ⓑ 「Frameworks & Drivers 링」 표기를 떼고 「링 밖의 공용 추상 패키지 · 여기서만 전역 제약 ①을 완화한다」를 **명시적 예외**로 적는다

### ★ CA-2 · 컨트롤러가 `composition_root` 의 `build_*` 를 부른다 — major

- 정본 D3(08-06 · R6): 「허용 목록에 **와이어링 예외** — 자기 BC 의 `composition_root` 에서 `build_` 로 시작하는 이름만」
- 원전 Ch26: *"Main is the ultimate detail—the lowest-level policy. **Nothing, other than the operating system, depends on it.**"*

**DI 가 아니라 서비스 로케이터다.** 「와이어링은 정의상 안팎을 동시에 안다」는 정당화가 `api_router.py` 엔 맞지만 **리프인 컨트롤러**엔 안 맞는다 — 트리 자신이 「규칙의 주어는 `driving_layer/` 의 리프 전부」라고 못 박았다.

### ★ CA-3 · 「컨트롤러 = Humble Object」인데 그 컨트롤러가 포매팅을 한다 — major

- 정본: 「컨트롤러는 **Humble Object** 여야 한다 … 요청을 DTO 로 바꾸고, Use Case 하나를 부르고, **결과를 응답으로 바꾼다**」
- 원전 Ch23: *"The **View** is the humble object that is hard to test… **The Presenter is the testable object.**"*

**Martin 의 23장에서 Controller 는 humble object 로 한 번도 지명되지 않는다**(리뷰어가 「지명한 문장을 못 찾았다」고 명시). 포매팅은 «테스트 가능한 쪽»인 Presenter 의 일이다 — **패턴 경계를 반대로 그었다.**

### CA-4~CA-9

| | 무엇 |
|---|---|
| **CA-4** | Main 인용 — 「가장 더러운」은 참, **「모든 것을 알아도 되는 «유일한» 조각」은 못 찾았고** Martin 은 *"many Main components"* 라 적었다. 「가장 바깥 원의 가장 바깥」도 원전이 **Main 을 22장 원 그림에 안 그렸다**고 명시 |
| **CA-5** | D14 「**원문이** package by layer 를 이름 들어 반대한다」 — Martin 의 Screaming Architecture 에 **그 낱말이 없다**. 이름 들어 비교한 것은 **34장이고 저자가 Simon Brown**. 게다가 **Brown 은 정적 분석을 낮게 보고 컴파일러 강제를 선호**한다 — 이 트리의 집행 수단이 정적 분석이라 **34장은 그 지점에서 반대편** |
| **CA-6** | 「두 링의 차이가 import 규칙의 차이로 나타난다」 — 실제로 나타나는 것은 **바깥으로 나가는 화살표 하나**(`repository/` → `django_<bc>/`). 배치는 Ch23(ORM 은 Humble Object 경계) 과 맞지만 **주장이 과하다** |
| **CA-7** | D45 「원전 셋 다 «판정»이라는 낱말이 없다」 — **침묵 논증이고 반례가 원전 안에 있다.** Martin 의 같은 링에 *"labels for buttons, if buttons should be disabled or not"* 를 **판정하는 Presenter** 가 산다. 결론은 옳지만 근거는 **우리 결정** |
| **CA-8** | 구역 배정표 「`application_layer/` → 클린」인데 **그 칸의 제1규칙만 Evans 에서 가져왔다** — 「구역 담당 계보의 어휘를 쓴다」가 여기서 깨진다 |
| **CA-9** | 94행 「**클린** 전역 제약 ②」 ↔ 목록 「② 안쪽은 구체 기술을 모른다(**헥사고날**)」 — 한 글자 |

### 정합 확인
- **T20 정정 반영됨** — «두 원전을 갈라 적고 채택한 쪽을 명시» 형식은 CA-5·CA-7 에도 그대로 쓸 틀
- **`adapter_layer/` 기각 근거가 원전 그대로** — *"The Presenters, Views, and **Controllers** all belong in here."*
- **프레젠터 생략의 «비용 잣대» 다리는 정당** — Ch25 *"the cost of implementation is less than the cost of ignoring"*. **다만 다른 다리(「제어 흐름이 뒤집힐 때만 필요한 장치」)는 Martin 이 한 적 없는 말** — 그의 근거는 흐름 방향이 아니라 Humble Object 테스트 가능성
- **D44 자체는 클린과 충돌하지 않는다** — DIP 는 «volatile **concrete** class 상속 금지»이지 추상 계약 상속을 막지 않는다. **문제는 D44 가 아니라 D44 를 `framework/` 에 적용한 자리**(CA-1)

---

## ② O — 과적합 ✅ 도착 (발견 15건)

**리뷰의 위치** — 3차 과적합 리뷰는 **08-07 · 102행 · 카드 32장** 기준이었다. 지금은 **117행 · 카드 44장**이고 **08-08 신설/개명 행이 52개**다. **그 52행은 과적합 축을 한 번도 안 지났다** — 발견의 절반이 거기서 나왔다.

**계수 하나** — 1장 본문의 `실측` **38회 중 처분 표식(「이관 규모」·「근거가 아니라」)이 붙은 것은 5회, 맨 것이 33회**. 3장 계획 2번이 「끝」으로 찍혀 있는데 그 단계의 「끝났다」의 자가 *「실측이 «정한» 규칙이 0 이거나, 남은 것마다 «왜 그래도 되는지»가 적혀 있다」* 다. **정본이 자기 완료 조건을 만족하지 않는다.**

### ★ O-1 · 「**실측이 정했다**」가 규칙의 이유 자리에 문자 그대로 있다 — blocker

> `error_out.py` 가 feature 밑이 아니라 BC 당 한 파일인 것도 **실측이 정했다** — 401 하나가 컨트롤러 보유 feature 23개 전부에 걸려 있어…

**3차 리뷰 `driving-27` 이 이미 판정했다** — 「BC 당 정확히 한 파일」은 실측이 아니라 **플러그인이 트리보다 먼저 못 박아 둔 계약을 옮겨 적은 것**. **그 편집이 정본에 반영 안 됐다.**
**깨지는 곳** — 401 을 앞단 게이트웨이가 내는 저장소, BC 당 feature 가 1~2개인 저장소 → **같은 자로 답이 「feature 밑」으로 뒤집힌다.**

### ★★ O-7 + O-6 + O-9 — **08-08 신설 축 셋이 전부 「우리에겐 0개」 위에 서 있다** · major 묶음

**R13 이 D26 에서 정확히 그 논법을 규율 ① 위반으로 폐기했다** — 「**실측 0 을 근거로 미루는 것이라 규율 ① 과 부딪히고**」. **그 폐기가 08-08 신설 52행엔 적용되지 않았다.**

| | 무엇이 「우리」에 매달렸나 |
|---|---|
| **O-7** (D42) | 「진행 상태는 적지 않는다 — 각 단계가 그 BC 의 도메인 상태를 바꾸는 한 이미 적혀 있다」 + *「Vernon 의 Process Manager 는 … **우리에겐 그런 것이 0개다**」*. **보상 사가가 필요한 결제·예약 도메인에서 「어디까지 갔나」는 어느 한 BC 의 도메인 상태가 아니다** — 그 파일이 갈 칸이 트리에 없고 `broker/` 가 «위반»으로 찍는다 |
| **O-6** (D43) | 「원전이 준 면제 넷 중 「메시징 수단이 없다」는 **우리가 못 쓴다**」 + 「**글로벌 트랜잭션·조회 성능도 우리 조건이 아니라** 살아남는 면제는 배치 하나뿐」. **표준의 blocker 가 «이 저장소가 브로커를 갖고 · XA 가 없고 · 조회 성능 문제가 없다»는 세 현재 사실 위에 선다.** 표준을 읽는 사람에게 「우리」는 자기 팀으로 읽힌다 |
| **O-9** (D40) | `broker_port.py` 검사 「**구독 등록은 메모리에만**」. 근거는 「트랜잭션을 나눌 이유가 **셋 다 아직 아니다**」. **Kafka/SQS 로 이미 잇는 팀의 정상 구현이 blocker 로 찍힌다.** 게다가 같은 카드가 Django signals 를 「전달 보장 0」으로 기각하고 **같은 성질의 인메모리 브로커를 강제하는 비대칭** |

### ★ O-5 · 문서가 «과적합»이라 자백한 문장이 아직 살아 있고, 옆 행과 정반대다 — major

3장: 「이 축에서 **하루에 세 번 걸렸다** — D34 · 트리 61행 · **D15**(마이그레이션이 비싸 보여 「`label` 은 안 바꾼다」로 정했다). 셋 다 실측을 보고 규칙을 만든 자리였다.」
- rd-69 `apps.py`: 「`label` 은 … **한 번 정하면 바꾸지 않는다.**」
- rd-68 `django_<bc>/`: 「**BC 이름이 바뀌면 `label` 도 같이 바꾼다.**」
**같은 결정 카드(D15)가 붙은 두 행이 서로를 위반으로 만든다.** 자백은 3장에, 병은 1장에 남았다.

### 나머지 major

| | 무엇 |
|---|---|
| **O-2** | 「`port/` 를 도메인이 아니라 여기 둔 것은 **실측이 강제했다**」(65건) — 65건은 «포트가 필요하다»의 근거는 되어도 «어느 층에 사나»를 못 정한다. **application 이 django 를 0번 부르는 신규 저장소면 근거가 0이 된다** |
| **O-3** | `test/` 자식 넷 — 이 파트가 세운 원리(「폴더 이름만 보고 DB 를 켜는지 알 수 있어야」)는 **둘밖에 못 낳고**, `e2e/`·`factories/` 의 근거는 실측뿐이다(문서가 스스로 「새로 정한 것이 아니라 이미 이렇게 나뉘어 있던 것」이라 적는다). **e2e 를 별도 저장소에서 돌리거나 `model_bakery` 를 쓰면 두 폴더가 영구히 빈다** — D7 이 `ninja/` 를 기각한 「빈 한 겹」에 스스로 걸린다 |
| **O-4** | 어드민 「**안은 자유**」 — 트리에서 **유일하게 안쪽 모양을 강제 안 하는 칸**의 정당화가 ⑴한 회사 방침 ⑵현재 측정치 ⑶**그 회사의 DB 트리거**다. `rd-74` 의 「면제 근거는 실측이 아니라 장고다」는 고쳐졌지만, **장고가 정당화하는 것은 리프 import·유스케이스 금지의 면제까지**이고 「안은 자유」는 장고가 강제하는 게 아니다 |
| **O-8** | celery 의 **임포트 동작**이 표준 두 행의 규칙이 됐다(`__init__.py` 재수출 · `autodiscover_tasks(packages=…)`). 전제(「celery 는 설치 0 · 코드 0 · 무산되면 이 칸이 무너진다」)는 **툴팁 안에만** 있다. django-q·huey·시스템 cron 이면 통째로 무의미 |
| **O-10** | DTO 「**검사하지 않는다** — 개발자면 테스트·**타입 체커**가 한다」 — 「타입 체커가 막는다」는 **mypy strict 가 CI 에서 도는 저장소에서만** 참인데 그 전제가 규칙 슬롯에 없다. 이 규칙은 **blocker 로 갈 예정**(백스톱 슬라이스 S1)이라 값이 크다 |

### minor 다섯
**O-11** `<entity>.py` 이름의 마지막 자가 「실측 접미사 0건」 · **O-12** 「기술 이름은 값이 하나뿐이라 축이 못 된다」(DRF↔Ninja 병행이면 반대 결론) · **O-13** 규칙 슬롯에 **한 저장소의 현재 파일 목록과 위반 건수**(rd-85·rd-108·rd-112) · **O-14** D46 의 «언제»·«어떻게»를 겪은 예시가 **이름 하나뿐** — *D39 에서 자기가 진단한 병(「예시가 갈래를 다 겪었나」)에 다시 걸렸다* · **O-15** 「`Main` 을 층에 넣어 보려 했지만 **실측이 막았다**」 — 그 사실은 장고·닌자가 컨트롤러를 만들어 주기 때문이고, 바로 다음 문장(Dependency Rule)이 이미 결론을 낸다

### 축 3(회사 고유 낱말) — **깨끗하다**
`자녀`·`기기`·`구독`·`child`·`device`·`lesson`·`turn`·`evict` 를 규칙 슬롯 117 · 이름 슬롯 117 에 전수로 걸었다. **규칙 문장 자체에 업무 낱말이 박힌 자리 0건** — 나온 것은 전부 예시 위치이고 2장이 「구체 이름은 **예시**다」라고 명시한다.

---

## ④b SC — 시나리오 태우기 ✅ 도착 (12개 중 blocker 4 · major 6 · 답 있음 2)

**명세 485행 키워드 전수** — `캐시` 0 · `업로드` 0 · `페이지` 0 · `정렬` 0 · `로케일` 0 · `배치` 0 · `웹훅` 0 · 인가 0. **시나리오 절반이 규칙 한 줄도 안 받고 있다.**

### ★★ SC-A · 대량 갱신 경로가 트리에 «없다» — blocker

`<aggregate>_repository.py` 「쓰기는 **`save()`·`remove()` 둘뿐**」(오늘 D43 이 박음) + 도메인 우회는 **조회 방향으로만** 열려 있다(`domain_bypass_query/`). `admin/feature/` 는 운영 화면, `scripts/` 는 D22 가 「임시·일회성」으로 못 박았다.
→ **100만 건 야간 잡을 규칙대로 짜면 애그리거트 100만 개를 메모리에 올려 100만 번 저장하는 코드가 나온다.** D43 은 그 트랜잭션을 「배치라 통과」시키는데 **통과시킨 코드가 돌지 않는다.**
**체크포인트(어디까지 처리했나)의 자리도 없다** — D42 는 「진행 상태는 각 BC 애그리거트가 자기 몫」이라 답하는데 배치 진행률은 어느 애그리거트의 불변식도 아니다.
**처분 갈래** — ⓐ `save_all()` 을 셋째로 열고 D43 검사에서 배치로 취급 ⓑ `domain_bypass_command/` 를 연다. **「쓰기는 둘뿐」은 D43 검사를 세우려고 닫은 것이라 여는 결정도 D43 과 같이 해야 한다.**

### ★★ SC-B · 「도메인 예외는 기저를 두지 않는다」가 **조용한 500** 을 만든다 — blocker

- `domain_layer/…/exception/` 검사: 「이 폴더 안 **어느 것도 다른 예외를 상속하지 않는다**」 — 근거는 「여기 것은 «타입»으로만 잡히므로 **묶을 대상이 없다**」
- 도메인에 불변식을 하나 더하면 → 컨트롤러의 어느 `except` 에도 안 걸림 → `<project>/api.py` 로 흘러 **500**. `api.py` 는 「도메인 예외 목록은 여기 없다」라 받아 줄 수도 없다.

**★ 문서가 «같은 실패»를 다른 칸에서 정확히 진단해 놓았다** — `contract/exception/<service>_published_error.py`: 「부르는 쪽이 칠 «**마지막 그물**»이 필요해서다 … 저쪽에 예외가 하나 늘면 … **컨트롤러는 자기 BC 의 도메인 예외만 아니까 매핑하지 못해 «조용히 500» 이 된다**」
**BC 사이에서는 이 논증으로 기저를 «필수»로 만들고, 같은 BC 안에서는 「묶을 대상이 없다」로 부정한다. 묶을 대상은 컨트롤러다.**
**처분안** — 애그리거트 기저 하나(`<Aggregate>InvariantViolated`) + 컨트롤러가 **마지막 절**로 잡아 «매핑되지 않은 불변식 위반» 코드로. 「타입만 쓴다」는 그대로 산다(속성을 안 읽으므로).

### ★★ SC-C · 화면이 BC 를 가로지르는 순간 답이 사라진다 — blocker (시나리오 1+3+4 가 여기서 만난다)

- `domain_bypass_query/` 는 **한 BC 안**으로만 열려 있다(구현이 자기 ORM 모델만 만진다) → BC 사이는 **ACL 두 번 + 파이썬 병합**뿐 → **정렬·페이지네이션이 안 선다**
- **그 화면을 소유할 BC 가 없다** — 루트 칸 「일곱째는 없다」 · `framework/` 는 `application/` 을 못 본다
- **인가**(「이 사용자가 이 주문을 볼 수 있나」) — 명세 **0건**. 컨트롤러는 세 줄, 유스케이스는 「판단은 애그리거트가」, 애그리거트는 「남의 BC 에 물어봐야 하면 **경계를 고쳐라**」 → **세 칸이 서로 다른 답을 주고 셋 다 성립 안 함**
- 공유 `Page`/`SortSpec` 타입 — `application_layer/` 자식은 「둘뿐」, `framework/` **두 갈래가 서로 다른 답**(능력 갈래는 「`*_port.py` 가 있나」로 탈락 · 기술 갈래는 「그 라이브러리 없이 말이 되나」로 탈락) → **개발자가 `framework/common/` 을 만들게 된다 — 이름 규칙이 금지한 그 자리**

### blocker 넷째 · SC-D · 파일 업로드 — 바이너리가 안쪽으로 갈 통로가 없다

`dto/` 「**살아 있는 자원 핸들도 안 된다**」 + D11 「컨트롤러 금지 목록에 `application_layer/port/**`」 → **전체를 `bytes` 로 읽어 `dto_in` 에 넣는 길 하나**(500 MB CSV 면 전량 메모리). `dto_out` 은 나가는 스트리밍만 열려 있고 **들어오는 스트리밍은 규정 자체가 없다**.
**처분안** — 「바이너리는 입구가 먼저 저장하고 dto 는 «키»만 든다」 → 그러려면 **D11 허용 목록을 한 줄 여는 결정**이 필요하다(웹훅 서명 검증과 **같은 결정 지점**).

### major 여섯

| | 무엇 |
|---|---|
| **SC-E** 웹훅 | `api/` 행은 「**외부(HTTP) 입구**」인데 설명 패널은 「**사람이** 부르면 `api/`」 — **두 규칙이 다른 답**. 게다가 그 열거가 **자식을 셋으로** 말한다(`event_subscription/` 누락). 딸린 공백 셋 — 서명 검증(세 줄 규칙과 충돌) · 멱등성 · 응답 형식(웹훅은 항상 200) |
| **SC-F** 캐시 | cache-aside 는 정의상 **판정**이라 오늘 박은 D45 에 정면으로 걸린다. 데코레이터 어댑터가 표준 해법인데 `adapter/` 네 갈래는 「내가 무엇을 구동하나」로 갈려 **«다른 어댑터를 구동하는 어댑터»의 자리가 없다** |
| **SC-G** 로케일 문구 | 알림·메일 본문을 빚는 자리가 **Presenter 인데 그 칸을 안 만들었다.** 그리고 뺀 근거가 「**이 저장소는 아직 안 뒤집혔다**」 — 규율 ① 이 금지한 형태 |
| **SC-H** 마이그레이션 | `RunPython` 에서 도메인을 못 import → **같은 도메인 규칙을 마이그레이션에 복제** → D30 이 진단한 병(「같은 위반이 두 채널로」)을 **트리가 강제한다** |
| **SC-I** 테스트 더블 | D44 의 **의도는** 「가짜도 상속한다」인데 **검사 범위가 테스트 밖**이고 규칙이 485행 어디에도 없다. 그리고 **강제 수단이 mypy 뿐**(ABC 는 런타임에 덕타이핑을 못 막는다) — 그 전제가 트리에 없다. **가짜가 살 칸도 없다**(`test/` 자식 넷 · `factories/` 는 factory_boy 만) |
| **SC-J** 공유 타입 | 위 SC-C 의 `Page` 문제 — `framework/` 두 갈래가 서로 되돌려 보낸다 |

### 답이 있는 것 둘 (다음 사람이 다시 안 뒤지게)
- **시나리오 11(남의 BC 조회 하나)** — 명확하다. 포트를 연다 · OHS 직접 호출 금지. **다만 조회 한 건에 7 파일**이 생긴다(포트+exception+ACL+상대 창구+request+response+published_error). **이게 «의도된 값»임을 칸에 한 줄 적어 두면 좋다**
- **시나리오 9(재시도)** — 도출된다. OHS 는 같은 프로세스라 타임아웃 대상이 아니다. **다만 그 전제가 암묵**이고, 상대 BC 가 자기 `external_system/` 에서 블록되면 내 쪽에서 서킷을 못 연다

### 파일 폭발 (문서 자신의 숫자)
`exception/` 파일→폴더 뒤집기로 **48 → 288 파일**(애그리거트 밑 48파일 · 288클래스) · `contract/` request+response 약 **150 파일** · `value_object/` **166**.
**안전판은 적혀 있다** — 「폴더는 채워질 때 만든다 — **빈 폴더는 위반**」(D40 시점 빈 폴더 154개 관측).

### 부수 — D31 카드의 예시가 자기 칸 규칙을 어긴다
카드 예시 `unit_of_work.entitlements.save(entitlement)` ↔ `<boundary>_unit_of_work.py` 칸 「**경계만 연다 — 리포지토리를 노출하지 않는다**」. **카드를 복사하면 위반이다.**

---

## ⑥ CHK — 검사 가능성 ✅ 도착 (blocker 5 · major 9 · minor 3)

**전제 하나** — **D40~D46 은 스펙 485행에 0건**(`grep D4[0-6]` → 0). 08-08 에 붙은 검사 **약 20문장**에 `ast`/`path`/`human` 세기 컬럼이 **아예 없다**. 정본 행에도 표식이 붙은 것은 **0개**(전체 117행으로는 위반 술어 57 중 **44가 무표기**).

### ★★ CHK-1+2 · D43 이 «무엇이 리포지토리인가»를 셀 수단이 없다 — blocker

카드가 「검사가 서려면 «무엇이 쓰기인가»를 기계가 알아야 한다」를 스스로 발견해 **메서드 이름은 닫아 놓고, 똑같이 필요한 «무엇이 리포지토리인가»는 안 닫았다.** 실제로 검사기를 돌린 결과:

| | 코드 | 결과 |
|---|---|---|
| **오탐** | `repo = self._order_repository; repo.save(a); self._order_repository.save(b)` | 걸림 — **같은** 리포지토리인데 배치 면제가 깨진다 |
| **오탐** | `self._audit_log.save(entry)` + `self._order_repository.save(order)` | 걸림 — 리포지토리가 아니다 |
| **오탐** | `self._order_repository.save(order)` + `order.lines.remove(line)` | 걸림 — 도메인 객체의 `remove()` |
| 미탐 | 루프 · 사설 메서드 경유 · `bulk_upsert` · `with` 없이 `uow.begin()` | 통과 |

**그리고 스펙 #255 와 정면 충돌** — 「위반이 **아니라** «트랜잭션 경계 검토 대상»이다 … **위반 술어가 없다 — 3차 T13**」. **3차 리뷰가 명시적으로 닫아 둔 항목을 뒤집으면서 기록을 안 남겼다.**

### ★★ CHK-3 · rd-80 의 1:1 검사가 **D41 이후 거짓**이다 — blocker

> 이 아래 모든 `.py` 는 «어떤 선언의 구현»이고 **파일 이름이 그 선언과 같다**

`email_sender_port.py` ≠ `email_sender_adapter.py`. **D41 카드는 스스로 인정했다** — 「어간이 같고 **접미사만 갈린다**(`_port`↔`_adapter`)」. **정본 규칙 문면만 «같다»로 남았다.** 이대로 구현하면 **모든 ACL·external·`<capability>` 어댑터가 위반으로 찍힌다.** 같은 병이 스펙 `#353`(`path`·blocker)에도.

### ★★ CHK-5 · D45 ②의 «근사» 고백이 «강제가 사는 자리»에 없다 — blocker

정직한 표기가 **D45 툴팁 안에만** 있다. **이 문서 자신의 규율이 「카드 본문은 정본에 안 들어간다 — 강제는 행/패널에」**이므로 **한계 표기가 카드에만 있는 것은 그 규율을 어긴 것.**

**반례 — 정상적인 애그리거트 재구성이 통째로 걸린다**
```python
def find(self, order_id) -> Order:
    order = Order(id=row.id)          # 생성자 — 허용
    for l in row.lines.all():
        order.add_line(Line(...))     # 재구성인데 «읽기 외의 도메인 메서드»  ← 위반으로 찍힌다
```
**그리고 ast 는 도메인 타입인지조차 모른다** — `row.recalculate_total()`(ORM · 정상)과 `order.mark_persisted()`(위반)의 **AST 모양이 같다**.

### ★★ CHK-7 · D42 의 «유일한 안전장치»에 검출이 0 — blocker

「되돌릴 수 없는 단계는 체인의 맨 끝에 둔다」 — **「되돌릴 수 없는」을 무엇으로 세는지가 문서 어디에도 없고 판정 물음도 없다**(D42 는 다른 두 자리엔 붙였다). **Cockburn 진단의 정확한 재현 — 약속만 있고 검출 기계가 없다.**
**처분안** — `human` 표기 + 판정 물음 「이 단계를 **되돌리는 창구가 상대 BC 의 `open_host_service/` 에 있나**」(있으면 끝에 안 둬도 된다) — 이건 `path`+`ast` 로 근사가 선다.

### ★★ CHK-10 · 「BC 하나를 지웠을 때 바뀌나」·「앞으로도 0인가」가 `ast`·blocker 로 적혀 있다 — blocker

**반사실과 미래는 파서가 세는 대상이 아니다.** 그리고 **같은 술어를 스펙 자신이 다섯 자리(#47·#372·#399·#400·#463)에서 `human` 으로 찍었다** — 표기가 내부에서 갈렸다.

### major

| | 무엇 |
|---|---|
| **CHK-4** | D44 「선언을 경로에서 유도」 — **유도 규칙이 넷**인데 카드는 하나만 적었다(`repository/` 는 선언이 **`port/` 밖**인 `domain_layer/`). 그리고 **중간 기저 클래스**를 허용하려면 전 저장소 클래스 그래프가 필요하다 — 「한 줄」이 아니다. *(부수: D44 의 `@abstractmethod`/`Protocol` 실측 주장은 **재현해 확인 — 카드가 맞다**)* |
| **CHK-6** | `framework` 「도메인 타입 0」은 rd-101(「`application/` 으로 나가는 import 0」)과 **같은 것을 두 번 세고**, 「판정 금지가 이 한 줄로 선다」는 **거짓**이다 — 덕 타이핑이면 `if payload.amount > 100_000` 이 이름 0글자로 산다 |
| **CHK-8** | `broker/` 두 검사 충돌 — 「단계·순서·보상을 기억하는 상태가 있으면 위반」 ↔ **브로커는 정의상 상태를 든다**(`self._subscribers`). 한정어를 `ast` 가 못 가른다 |
| **CHK-9** | 「쓰기는 `save()`·`remove()` 둘뿐」은 **닫힌 목록**으로만 선다 — **D46 이 바로 그 형식을 병으로 진단했다**. `bulk_upsert` 가 조용히 빠져나가 CHK-1 의 미탐이 된다. **처분안: 「`-> None` 인 추상 메서드는 전부 쓰기로 본다」로 판정 물음화** |
| **CHK-11** | 정본은 「BC 를 넘는 포트를 부르면 위반」을 **검사로 올렸는데** 스펙은 `human` ×3. **위반이 파일의 성질이 아니라 «와이어링의 성질»**이다 — 두 유스케이스의 코드가 완전히 같고 `dependency_wiring.py` 만 다르다 |
| **CHK-12** | **D41 이 뒤집은 규칙이 스펙에 «네 벌» 살아 있다**(#41·#223·#381·#410 — 「`Port`·`Adapter`·`Gateway` 는 파일 이름에 나오지 않는다」). **네 벌 전부가 지금 트리를 위반으로 찍는다.** 유사도 0.80↑ 중복 **27쌍**(4중복 1 · 3중복 1) — **485 라는 수치 자체가 신뢰할 수 없다** |
| **CHK-14** | rd-106(「대상은 `*_adapter.py` **전부**」 + 「같은 폴더의 `*_port.py` 를 상속」) ↔ rd-107(「`*_port.py` 가 있으면 위반」) — **만족 불가** |
| **CHK-15** | 런타임 성질을 정적 검사로 적었다 — `event_wiring.py` 「두 번 받아도 구독자가 둘이 안 된다」(**그 동작은 broker 구현에 있지 이 파일에 없다 — 제약이 엉뚱한 파일에 붙었다**) · 「같은 트랜잭션에 들어야」 · 「하나가 실패해도 나머지는 간다」 · 「타임아웃·재시도는 여기만」 |
| **CHK-16** | `ast` 규칙 다수가 **어노테이션에 얹혀 있는데 강제는 `#306` 한 곳뿐**. **처분안: 「선언·구현의 공개 시그니처는 어노테이션 필수」를 전역 제약으로** — 그러면 여러 `ast` 규칙이 실제로 선다 |

### minor
**CHK-13** 「이 아래 모든 `.py`」에 `__init__.py` 와 매퍼 모듈의 자리가 없다 · **CHK-17** **D46 은 이 렌즈 기준 «모범»**(세기 `human` 정직 표기 + 판정 물음 + 닫힌 목록 자진 기각) — 결함은 행에 표식이 없다는 것뿐. *(반면 rd-105 「`kind`·`mode`·`bc`·`is_…`」는 **D46 이 기각한 닫힌 목록 형식** — `tenant`·`variant` 가 빠져나간다)*

---

## ④ G — 누락·오작성 ✅ 도착 (blocker 5 · major 10 · minor 5)

### ★★ G-5 · **2장 도해의 클릭 링크 열 개가 전부 «옛 102행» 번호다** — blocker

「상자를 누르면 1장 트리의 그 행으로 간다」는 기능이 **매번 틀린 칸을 연다.**

| 도해 상자 | 간다고 적힌 곳 | 실제로 열리는 칸 | 정답 |
|---|---|---|---|
| `cancel_order_use_case.py` | 28행 | `<job>_cron_job.py` | 35 |
| `port/shipment_status/` | 33행 | `application_layer/<feature>/` | 41 |
| `anticorruption_layer/delivery/` | 76행 | `admin/<entity>/panel.py` | 90 |
| `order_repository.py` | 53행 | `<aggregate>.py` | 60 |
| `repository/order_repository.py` ×2 | 73행 | `0001_initial.py` | 83 |
| `order/order.py .cancel(...)` | 46행 | `<capability>_query.py` | 53 |
| `event/order_canceled.py` | 51행 | `domain_layer/` | 59 |
| `external_system/ses/` | 80행 | `adapter/` | 93 |
| `dto_out.py` | 31행 | `<event>_subscription.py` | 38 |

**손으로 쓴 12·14·15 만 맞다** — `fbox(..., r=)` 인자를 통째로 안 훑은 스윕 누락.
**파생** — 머리글 「**트리의 32칸을 지난다**」의 32는 생성기가 `data-r` 를 «세서» 낸 값이라 **오번호가 부풀린 것**. 실제는 **24칸**. **정답표는 이미 문서 안에 있다**(오른쪽 단계 목록은 전부 정확).

### ★★ G-1+2+3 · **D40 이 연 이벤트 축이 «상위 칸·패널·2장»에 하나도 안 내려갔다** — blocker

- **G-1** BC 루트 칸: 「**여섯 가지만 온다** … **일곱째는 없다**」 — `published_event/` 를 부정한다. `composition_root/` 도 `dependency_wiring.py` 한 파일로 적어 `event_wiring.py` 가 빠졌다
- **G-2** `driving_layer/` 칸: 자식을 **셋만** 센다 + 「새 종류의 행위자가 생기기 전에는 자식이 늘지 않는다」. 패널은 첫 줄만 「넷」으로 고쳐졌고 **뒤 세 문장이 D40 이전 그대로** — 「셋을 가르는 축」·행위자 셋 나열·「**넷째 입구는 새 칸이 아니라 위반이다**」
- **G-3** 2장이 **세 곳**에서 「무엇으로 실어 나를지 **아직 정하지 않았다**」(도해 상자 + 단계 ⑧ + 코드 주석) — **규율 ⑤ 정면 위반**
- **G-4** 2장 흐름이 **이벤트 축을 한 칸도 안 지난다**(`data-r` 에 4·5·6·29·30·31·102·103 전무). 부팅 절에도 `event_wiring.py` 가 없다

### ★★ G-9+10 · `framework/` 의 갈래 자가 **자기 자식을 못 담는다** — blocker

- 자: 「폴더 안에 **`*_port.py` 가 있으면 «능력», 없으면 «기술»**」(이분법)
- `framework/broker/` 는 `broker_port.py` 를 갖는다 → **«능력»으로 오판**되고 `rd-107` 이 그걸 「위반」이라 부른다. `test/` 는 어느 쪽도 아니다 — **C 가 갈 곳이 없다**
- 패널도 자식을 셋(`<capability>/`·`<technology>/`·`test/`)만 세고 **`broker/` 가 없다**. 「형제 **둘**의 축이 서로 다르다」로 못 박기까지 한다
- **G-10** `broker_port.py` 칸이 자기 안에서 모순 — 「**계약과 배달이 한 파일에**」 ↔ 「구현은 `<technology>_adapter.py` 로 **이 폴더 안에 나란히 온다**」. **그 «나란히 오는 파일»의 트리 행이 없다**

### ★ G-16 · **D34 툴팁의 `id` 필드에 본문 문단이 들어갔다 — 렌더링 버그** — major

`d34: { id: "<b>★ 08-08 — 이 결정은 뒤집혔다.</b> D40 이 …<br>D34", …}` 이고 렌더 코드가 `tId.textContent = data.id` 라 **작은 D 배지 자리에 `<b>` 태그가 글자 그대로 300자 가까이 찍힌다.** D34 핀은 두 칸에 붙어 있다.

### 닫히지 않은 칸 — 「무엇이 오나」는 **117/117 다 참** · 나머지 24칸이 빈다

**«규칙»(검사) 없는 칸 12** — 20 `contract/request/` · 33 `<feature>/` · 41 `<capability>_port.py` · 46·47 · 55 `<entity>.py` · 71 · 79 · **93 `external_system/<system>/<capability>_adapter.py`** · **95 `adapter/<capability>/…`** · 108 · 117
**★ 가장 센 것은 93·95** — 벤더 SDK·라이브러리를 잡는 유일한 자리인데 **«예외를 어디까지 번역하나»가 한 줄도 없다**(형제 90 ACL 어댑터는 「기저 예외를 반드시 잡는다」가 있다)

**«이름» 없는 칸 12** — **32 `application_layer/` · 51 `domain_layer/`**(형제 `driving_layer/`·`driven_layer/` 는 개명 근거를 이름 슬롯에 갖는다 — **네 층 중 둘만**) · 64 · **91 `external_system/`**(형제 셋은 다 있다) · 98·99·100 · 109·110·111 · 114·115

### 그 밖의 major
| | 무엇 |
|---|---|
| **G-6** | 2장 도해가 **폐기된 `transaction/`** 폴더 이름을 쓴다 |
| **G-7** | 2장 도해가 `email_sender.py` — **D44 가 「고쳤다」고 기록해 놓고 도해는 안 고쳤다**(경로에 `adapter/` 마디도 빠짐) |
| **G-8** | 도해·단계 ⑤ 가 `exception.py`(파일) — T28 이 폴더로 뒤집은 자리. 실패 절은 파일명 «취소됨» ↔ 클래스 «배송됨» |
| **G-11** | `port/` 「선언은 **여기 아래에만** 산다」인데 **반례가 둘**(`domain_layer/<aggregate>_repository.py` · `framework/*_port.py`) |
| **G-13** | 3장 규칙 수 **471 ↔ 447**, 명세 원본은 **485** |
| **G-14** | 4번이 「닫혔다」인데 그 자가 「**107**칸 전부가 인용된다」 — **D40 이 연 10칸이 명세에 없다** |
| **G-17** | domain 패널이 「밖으로 나가야 하는 알림이면 그건 처음부터 **Port** 다」 — D40 이전 결론 |
| **G-18** | **정본 트리 행에 `OHS` 약어**(rd-87) — 규율 ④ 위반. 문서 자신이 `uow/`·`acl/` 를 같은 자로 막았다 |
| **G-21** | `rd-52` 가 「**원전이 준 면제 넷**」을 인용하면서 **넷을 안 적는다** — 목록은 D43 툴팁에만. **강제되는 검사에 열지 않은 예외 구멍이 셋** |

### minor
**G-12** `rd-85` 규칙 슬롯이 검사가 아니라 상태(「지금은 비어 있다」) — *규율 ⑤ 위반은 아니다(조건과 자리를 준다)* · **G-15** 「결정 카드 38장」 ↔ 실제 44 · **G-19** 툴팁 산문에 `OHS` 13 · `ACL` 14 · `UoW` 9 · `EIP`·`DIP`·`CQRS` · **G-20** `<bc>` ↔ `<bounded_context>` 혼용 · **G-22** **D22 가 117행 어디에도 핀이 없다**(도달 불가) — `scripts/` 가 1장에 흔적이 없고, 본문의 `scripts/` 2건은 **다른 것**(플러그인 백스톱)을 가리킨다

### 규율 ⑤ 위반 판정 — **G-3 하나뿐**
「아직」이 나오는 다른 자리(3장 진행 배지 · 「이 저장소는 아직 안 뒤집혔다」)는 자리를 확정하고 있어 안 걸린다.

---

## ⑦ S — 스윕 누락·죽은 문면 ✅ 도착 (blocker 6 · major 11 · minor 6)

**★ 사실 하나가 이 렌즈 전체를 설명한다 — 2장은 자료구조가 «둘»이다.**
`FLOW`(SVG 도해) 와 `FLOWSTEPS`/`FLOWCODE`(단계 목록). **오늘 D44 가 잡은 「D41 이 2장을 안 훑었다」는 `FLOWSTEPS` 만 고쳤고 `FLOW` SVG 는 «한 번도» 안 훑었다.**

### ★★ S-1·2·3·5 · SVG 하나에 옛 이름 넷이 동시에 산다 — blocker

| 옛 이름 | 지금 | 어디 |
|---|---|---|
| `transaction/order_unit_of_work.py` | `port/unit_of_work/…` | SVG |
| `email_sender.py` | `email_sender_adapter.py` | SVG |
| `exception.py`(도메인) | `exception/<exception>.py` | SVG + 단계 ⑤ |
| `cancellation_notice.py` | `cancellation_notice_payload.py` | SVG + 단계 ⓑ |

### ★★ S-4+S-14+S-15 · **D41 이 개명한 «그 칸»의 «무엇이 오나»가 옛 규칙을 말한다** — blocker

`rd-41` 한 칸 안에서 두 줄이 정면으로 부딪힌다:
- **WHAT**: 「**파일 이름은 폴더와 같고** … `smtp_client.py` 가 아니라 **`email_sender.py`** 다」
- **NAMES**(바로 아래): 「**접미사 `_port` 가 «내가 계약이다»를 말한다**」

그리고 `rd-106` 이 그 **옛 자를 판정 근거로 인용**한다 — 「계약이 **폴더 이름과 같으니**(105행) 나머지가 구현이고」. **105행은 `<capability>_port.py` 라 폴더 이름과 같지 않다.**
**진단 — 개명 스윕이 「트리 행 이름」만 보고 «같은 행의 WHAT 슬롯»을 안 봤다.**

### ★★ S-13 · 2장에 이벤트 축 낱말이 **0회** — blocker

`published_event` 0 · `event_router` 0 · `broker` 0 · `event_wiring` 0 · `event_subscription` 0.
그런데 「무엇으로 실어 나를지는 **아직 정하지 않았다**」가 **SVG · 단계 ⑧ · 코드 주석 세 자리**에 산다.
**D40 은 「트리 107→117행」이라 자기 카드에 적어 놓고 그 10칸이 그려질 «유일한 화면»을 안 훑었다.**

### ★★ S-9+S-10 · **자동 계수가 오류를 «검증된 사실»로 승격시켰다** — blocker

SVG `data-r` **아홉 자리**가 옛 축이라 딴 칸을 연다(앞선 G-5 와 같은 발견, 여기선 원인까지). 그리고 머리글 「트리의 **32**칸을 지난다」는 생성기가 `FLOW + FLOWSTEPS + FLOWCODE` 의 `data-r` 를 **센 값**인데, **SVG 의 잘못된 8개가 단계 목록과 안 겹쳐 그대로 8칸 부풀었다.** 실제 **24**.
> **교훈 — 「센다」가 안전장치가 되려면 «세는 원본»이 정확해야 한다.**

### ★ S-17 · D40 카드의 「**43행이 막는다**」가 옛 축 번호 — major

43행은 지금 `<payload>_payload.py` 다. 실제로 막는 것은 **50행** `<boundary>_unit_of_work.py`. **같은 카드가 「트리 107 → 117행」이라 적어 놓고 자기 행 참조는 옛 축으로 남겼다.** (같은 카드의 58·59 참조는 맞다 — **전역 오프셋이 아니라 한 자리 누락**)
> **반전 스윕이 「칸을 열었나」만 보고 «내가 쓴 행 번호가 아직 그 행인가»를 안 물었다.**

### 그 밖

| | 무엇 |
|---|---|
| **S-6·S-7** | 툴팁 `d29`·`d30` 에 **`query_repository/`·`transaction/`·`<Capability>QueryRepository`** 가 살아 있다(「자식 **넷**」도) |
| **S-16** | 툴팁 `d29` 가 **자기 머리에서 「원전 오독이었다」고 폐기한 논증을 뒤에서 그대로 싣는다**. 기록 카드엔 경고가 붙어 있는데 **툴팁만 경고 없이** — 툴팁↔카드 불일치 |
| **S-11** | 링크 둘이 «파일»을 적고 «폴더 행»을 연다(`dependency_wiring.py`→2행 · `order_already_canceled.py`→61행) — **폴더화 개정이 행을 밀었는데 번호를 안 밀었다** |
| **S-12** | 실패 단계가 **존재할 수 없는 파일**을 예시로 든다(`order_already_canceled.py` ↔ `OrderAlreadyShipped`) |
| **S-18** | **툴팁 `d22` 만 핀이 0** — 정본에 실렸는데 아무 데서도 열 수 없는 사문 |
| **S-19** | D41 카드 코드 블록에 `cron_job/<job>_cron_job.py` 가 **두 번**(칸 수 16은 맞다) |
| **S-20** | 생성기 주석의 D8 수치가 옛값(26·9·16 ↔ 실제 13·25·18) — assert 는 맞다 |

### 수치 불일치 표

| 어디 | 적힌 값 | 실제 |
|---|---|---|
| 2장 머리글 | 32칸 | **24** |
| 3장 1번·4번 | 결정 카드 **38장** | **44** |
| 3장 4번 산출물 | 규칙 **471** · 103 KB | **485** · 114,153 B |
| 3장 4번 「끝났다」 | 「**107**행 재정합 … **107칸 전부**가 인용된다」 | 트리 **117** — **10칸이 안 덮인다** (blocker) |
| 3장 5번 | 「규칙 **447** 개 중 사람 `125`」 | 485 중 `human` **142**(blocker 121) |
| 툴팁 `d41` | 「**열여섯 칸**」 뒤 열거 | 열거한 갈래는 **10칸** — `_port`(2)·`_adapter`(4) 여섯이 빠졌다(카드 코드 블록엔 있다) |

**맞는 것으로 확인된 값** — 3장 6번의 `19종`/`11개`/`7`(실제 `scripts/check-*.py` 19 · `skills/` 11 · `agents/` 7) · D8 툴팁 13/25/18(assert 가 지킨다)

---

## ③d EDA — 이벤트 주도 원전 정합 ✅ 도착 (blocker 3 · major 4 · minor 4)

### ★★★ EDA-3 · 「커밋 직후 발행」은 **무기록 유실**을 만들고, outbox 를 접은 논증이 **문서에 아예 없다** — blocker

- 규칙: 「**발행 등록이 업무 트랜잭션과 «같은» 트랜잭션에 들어야 한다**」 · 「**구독 등록은 메모리에만**」
- **enqueue 가 메모리 안에서만 일어나므로 DB 트랜잭션과 «원자적이지 않다».** 커밋 성공 → 콜백 실행 전 프로세스 사망 → **사실이 로그 한 줄 없이 소멸.**
- 원전: *"Messages are guaranteed to be sent **if and only if** the database transaction commits"* — `on_commit` 은 **한쪽만** 준다(rollback ⇒ 미발행 ✔ / commit ⇒ 발행 ✘)
- D31 카드의 「커밋되면 실행 · 롤백되면 «안» 실행 — 감싸여도 같다」에 **「커밋됐는데 실행 안 됨」 갈래가 없다**

**★ 그리고 리뷰어가 확인한 것 — `outbox`/`아웃박스` 가 정본 0건 · 기록 0건이다.** 「같은 DB 라 dual-write 가 아니다」라는 문장 **자체가 두 문서에 없다**(2차 리뷰 문서에만 다른 논거로 있다). **그 논거도 안 선다** — dual-write 의 두 쓰기는 «DB 와 브로커»가 아니라 «영속 저장소와 **휘발성 없는 전달**»이고, **in-process 브로커의 메모리 큐는 DB 가 아니라 커밋 경계 밖**이다.
**처분 갈래** — ⓐ 발행 기록을 같은 트랜잭션의 DB 행으로(outbox) ⓑ **「이 트리의 사실 전달은 at-most-once 이며, 유실이 허용되지 않는 전파는 사실이 아니라 커맨드로 보낸다」를 규칙으로.** **어느 쪽이든 「나중에」는 규율 ⑤ 에 걸린다.**

### ★★ EDA-2 · **정본의 «유일한 실행 예시»가 D40 규칙 셋을 동시에 어긴다** — blocker

2장 ⑧ 이 ⑴ **내부** 도메인 이벤트(`domain_layer/…/event/`)를 그대로 「밖으로 내보내는 자리」로 보내고(규칙: 「BC 밖에서 import 하면 위반」) ⑵ **`published_event/` 로 옮겨 담는 단계가 없고** ⑶ **`with` 블록 «밖»**이라 「같은 트랜잭션」에 든 게 없다. **형제 ⓑ 는 `uow.after_commit(...)` 을 `with` 안에서 부르는데 ⑧ 만 그 짝이 없다.**

### ★★ EDA-8 · 「되돌릴 수 없는 단계는 맨 끝에」가 **pivot 의 절반만** 옮겼다 — major

- 원전 삼분법: pivot 이후 단계는 **retriable — 반드시 성공해야 한다**. **이 트리엔 재시도가 0**(EDA-4)
- **축이 다르다** — 문서는 「**되돌릴 수 없는** 단계」를 뒤로 밀고, 원전은 「**실패할 수 있는** 단계」를 앞으로 당긴다. 뒤로 밀어도 **그 앞 단계들에 대한 보상 의무는 그대로 남는다**
- **「오케스트레이터 없이 지킬 수 있는 «유일한» 안전장치」는 거짓** — Richardson 이 더 강한 것을 준다: *"You should structure the Saga so there are **no compensatable transactions**"*(실패 가능 단계를 맨 앞에 두어 보상을 아예 없앤다)

### ★ EDA-7 · **인용 참칭** — *"processing events (which function more like commands)"* 는 「원전 문면」이 아니다 — major

기록 **두 자리**(D40 기각 · D42 기각 ②)에서 「**원전 문면으로**」 표식을 달고 인용했는데, 리뷰어가 그 정확 문자열을 **책 어디서도 못 찾았다.** 유일한 출처는 ch.14 를 요약한 **제3자 블로그**다. **책의 실제 문면은 다르다** — *"processing events … are commands (things that need to happen) as opposed to events (things that have already happened)"*.
**★ 주장 «내용»은 맞다**(Richards 는 실제로 중재자의 processing event 를 커맨드라 부른다). **틀린 것은 인용의 형식**이고, 그 인용이 **기각 둘을 지탱한다.** 그리고 **정본에 `Mark Richards` 0회 · `processing events` 0회.**

### major 둘 더
| | 무엇 |
|---|---|
| **EDA-1** | 2장 전체가 D40 이전 상태(앞선 C-2·G-3·S-13 과 같은 자리 — 네 렌즈가 독립으로 잡았다) |
| **EDA-4** | **재시도·데드레터가 0**인데 「하나가 실패해도 나머지는 간다」로 실패를 삼킨다. `<event>_subscription.py` 에 **멱등 요구 없음**. 정본의 「멱등」 2건은 둘 다 이벤트 축이 아니고, 크론 카드의 「멱등성은 유스케이스가 이미 갖고 있다」는 **근거 없는 단언**(유스케이스 칸에 멱등 규칙이 없다) |
| **EDA-6** | **Fowler 의 네 갈래 중 셋이 침묵** — `Event Sourcing` 정본 0·기록 0 · `state transfer`/ECST 0·0 · `CQRS` 는 전부 «우리 축이 아니다»로 배제하는 맥락. **「이 경우는 안 다룬다」가 어디에도 없다.** 특히 **구독자가 더 많은 자료를 필요로 할 때 «되물어 가나 / 사실이 싣고 오나»가 두 규칙 사이에서 갈리는데 답이 없다.** *규율 ⑤ 는 「안 만든다」를 벌하지 않고 「말 안 한다」를 벌한다* |

### minor 넷
**EDA-5** 전달 «순서»에 한 줄도 없다(in-process 라 지금은 자연히 FIFO — 미표기) · **EDA-9** 커맨드 축을 «코레오그래피»라 부른 것(원전에서 코레오그래피는 **이벤트 발행**으로 정의 — 커맨드 사슬은 「조정자 없는 오케스트레이션」) · **EDA-10** 판정 자 둘이 **발신자 쪽만** 본다 — 수신자 축(**「받는 쪽이 무시해도 되나」**)이 없다. *Richards: "a command must be processed, whereas an event can be ignored"* · 정본에 `Richards` 0회 · `Dahan` 0회 · **EDA-11** 「구독자 0 은 **경고**」가 **D40 툴팁 안에만** 있고 어느 칸의 규칙 줄에도 안 내려왔다

### 정합 확인 셋
- **Fowler 의 비용을 원문 그대로 인용하고 «처방»까지 붙였다** — *"it can be hard to see such a flow as it's not explicit in any program text"* → D42 의 「기계가 매번 세게 한다」. **원전이 문제만 적고 끝낸 자리에 처방을 붙였다**
- **스키마 소유 방향으로 커맨드/사실 계약을 «물리적으로 다른 폴더»에 갈랐다** — Fowler 의 passive-aggressive event 를 **주의사항이 아니라 기계 검사**로 내렸다
- **「브로커는 지금은 아니다」의 판정 자가 원전과 같다** — 「**「안 쓰여서」가 아니라 「나눌 이유가 없어서」**」가 규율 ⑤ 를 정직하게 통과시키는 유일한 형태

---

## ⑧ PY — 파이썬·장고 사실 검증 ✅ 도착 (blocker 1 · major 4 · minor 5 · **맞다 39건**)

**실제로 설치해 돌렸다** — Python **3.12.13**(대조 3.9.6) · Django **6.0.8** · celery **5.6.3** · django-ninja **1.6.2** · ninja-extra **0.31.6** · firebase-admin · gunicorn.

### ★★ PY-1 · **D25 와 D27 이 동시에 참일 수 없다** — blocker

- **D25**: 「ninja 가 `OpenAPISchema.responses(operation)` 라는 **모든 operation 이 지나는 관문**을 주는데 … 규칙 20줄로 다시 짜 보니 **236/236**」
- **D27**: 「**`get_openapi_schema` override · monkeypatch · postprocessor 로 사후 변형하지 않는다**」

**실행 결과** — `ninja/openapi/schema.py` 의 `get_schema()` 가 `OpenAPISchema` 를 **하드코딩**한다. 서브클래스를 정의만 하면 `[200, 409]`(**무시됨**), `get_openapi_schema` 를 override 해야 `[200, 401, 409]`. `NinjaAPI.__init__` 에 스키마 «클래스» 주입 지점이 없고 `NinjaExtraAPI` 도 재정의하지 않는다.
→ **그 관문에 닿는 길은 D27 이 이름 들어 금지한 둘뿐이다.** 명세가 이 둘을 그대로 옮기면 **플러그인이 자기 규칙으로 자기 설계를 blocker 로 찍는다.**

### ★★ PY-4 · **D44 의 「계약이 바뀌면 같이 깨진다」는 절반만 참** — major

```
계약에 «새 메서드» 추가        → TypeError (깨진다)          ✅
계약의 «시그니처» 변경          → 낡은 구현이 그대로 인스턴스화 (런타임 무반응)
빈 껍데기 override (pass)      → 인스턴스화 됨
시그니처 불일치 override        → 인스턴스화 됨
```
**「«이름»에서 «내용»까지 내려간다」는 «이름 + 메서드 이름 집합»까지**이지 내용까지가 아니다. **시그니처 드리프트는 타입 체커가 강제 대상인데 트리에 그 자가 한 줄도 없다.**

### ★★ PY-2 · `models/` 와 `admin/` 의 **재수출 필수가 규칙에 없다** — major

Django 는 `<app>.models` 와 `<app>.admin` **한 모듈씩만** import 한다. 재수출을 빠뜨리면 **부팅 시 오류도 경고도 0건인 채 모델이 미등록**(실행으로 확인)되고, 나중에 `makemigrations` 가 **테이블 삭제를 제안**하거나 어드민이 텅 빈다.
**★ 같은 문장이 `cron_job/` 에는 이미 있다** — 「`__init__.py` 가 `<job>` 들을 재수출한다」. **한 축만 적고 두 축을 빠뜨린 비대칭.**

### ★ PY-3 · `app_label` 개명 비용 목록에서 **`django_content_type`·`auth_permission` 이 빠졌다** — major

`db_table` 명시라 **테이블은 안 움직인다는 건 맞다.** 그러나 `ContentType.app_label` 은 **저장된 값**이고 `Permission` 이 그것을 FK 로 잡는다. Django 는 **`RenameModel` 에만** `RenameContentType` 을 자동 주입하고 **`app_label` 개명은 아무도 안 따라온다** → ContentType 이 둘이 되고 **권한과 GenericForeignKey 가 조용히 끊긴다**. 「치르는 값 **셋**」이 다섯이어야 한다.

### ★ PY-5 · `@api_controller`·`@route` 는 ninja 가 아니라 **django-ninja-extra** — major

core 에 **없다**(출처 `ninja_extra.controllers`). 그런데 「기술 축의 값이 **하나뿐**(ninja 63 · 나머지 0)」·「라이브러리 하나 = 폴더 하나 — `django/`·`ninja/`」로 적혀 있다. **D24 자신이 `INSTALLED_APPS` 실측에서 `ninja_extra` 를 세고 있는데도.** 클래스 접두사 `Ninja…Controller` 도 실제 기술을 안 가리킨다.

### minor 다섯
**PY-6** `select_for_update` 「트랜잭션 밖이면 에러」는 **백엔드가 지원할 때만** — SQLite 는 *"an error isn't raised"*. 그리고 **`TestCase` 로는 이 가드를 검증 못 한다**(`TransactionTestCase` 필요) · **PY-7** 「기저를 상속하지 않으면 위반 — **AST 한 줄**」은 **이행 상속(`B(A)`, `A(ServiceError)`)을 위반으로 찍는다** — 상속 폐포가 필요해 한 줄이 아니다 · **PY-8** `sys.stdlib_module_names` 는 **3.10+** — 3.9 에서 검사기가 **AttributeError 로 죽는다**(fail-open 금지와 충돌) · **PY-9** 「`except … as e` 로 묶은 이름을 **이 파일 안에서** 참조하면 위반」 — 파이썬이 블록 끝에서 그 이름을 **암묵 `del`** 한다(문면이 넓다). 그리고 **`sys.exc_info()[1].field` 구멍**이 열려 있다 · **PY-10** 트리 2097행(「`label` 은 한 번 정하면 바꾸지 않는다」) ↔ D15 카드(「BC 이름이 바뀌면 `label` 도 바꾼다」) — **공식 문서는 2097행 편**(*"breaking changes"*)

### ★ 「맞다」로 확인된 39건 (요지)
- **D44 의 실측 주장 전부 재현** — `@abstractmethod` 없이 인스턴스화 됨 / 붙이면 `TypeError` / 상속 안 한 더블 통과 / **`Protocol` 이 `ABCMeta` 위**(3.9·3.12 동일)
- **`ready()` 축 전부** — `django.setup()` 3단계의 끝 · 「모든 앱 뒤」 훅 없음(Signal 0건) · DB 금지(공식 문서: *"`manage.py test` would still execute some queries against your **production** database!"*) · 멱등(공식 문서가 *"might be called more than once"*) · wiring 임포트는 `ready()` 안
- **`on_commit`** — 감싸여도 안전 · 롤백 시 폐기 · **중첩이면 savepoint 라 최외곽이 끝나야 진짜 커밋**
- **celery** — `autodiscover_tasks` 기본값으로 못 닿음(Django 가 넘기는 건 `AppConfig.name`) · 재수출 없으면 태스크 **0건** · `packages` 콜러블
- **stdlib 충돌** — `platform/` 을 루트에 두면 `firebase_admin.messaging` **ImportError** · `gunicorn.workers` **AttributeError** (실측 재현)
- **`raise X from exc` 금지해도 `__context__` 가 자동으로 붙는다** · **`except` 는 자식도 잡는다** · **`in.py` 는 SyntaxError**
- **D35 순환 import** — *"partially initialized module"* 문구 그대로 재현. **다만 `from X import Y` 형태일 때만 무조건 죽고, D34 가 그것을 «무조건»으로 축약했다**(minor)
- **`startapp` 산출물에 `label` 이 없다** — 「`app_label` 을 «명시» 선언」은 startapp 으로 만족되지 않는다

### 문서에 «미기재»인 사실 하나
**커밋 직후 프로세스가 죽으면 `on_commit` 콜백은 유실된다** — 콜백은 `connection.run_on_commit` **인메모리 큐**다(실행으로 확인). 공식 문서도 *"if your database connection is dropped because your process was killed … your rollback hook will never run"*. → **EDA-3 과 같은 자리**를 독립적으로 확인.

---

## ③a DDD — Evans·Vernon 원전 정합 ✅ 도착 (blocker 2 · major 4 · minor 4)

**원전 PDF 다섯을 직접 받아 전문 대조했다** — Evans Blue Book(2003 Final Manuscript) · DDD Reference 2015 · Vernon EAD Part I/II · **Vernon IDDD 전문** · Young CQRS Documents.

### ★★★ DDD-1 · **애그리거트 규칙 넷 중 «식별자로만 참조»가 통째로 없고, 그 탓에 D43 의 검사가 스스로 뚫린다** — blocker

- 문서: 「애그리거트 경계는 **규칙 셋**을 만든다 — **바깥에서는 루트만 참조한다** · …」
- **그건 Evans 의 문장**(*"allow external objects to hold references to the root only"*)이지 **Vernon 의 규칙 3 이 아니다**:
  > **"Rule: Reference Other Aggregates By Identity"** … *"Both the referencing aggregate and the referenced aggregate **must not be modified in the same transaction**."*
- 트리 전수 검색 결과 **0건**

**★ 왜 blocker 인가** — D43 의 검사는 「**서로 다른 리포지토리**에 쓰기가 둘」이다. 애그리거트가 남의 루트를 **객체로** 물고 있으면 **`order.customer.rename()` 이 리포지토리 하나만 건드리고 통과한다.** **그리고 그게 Django 의 기본값이다**(FK 접근 `order.customer` 가 곧 직접 객체 참조). **주 대상 프레임워크에서 가장 흔한 위반 경로가 사각지대다.**
**처분안** — `<aggregate>/` 에 「다른 애그리거트는 **식별자 값 객체로만** 문다 — 타입 힌트에 남의 애그리거트 클래스가 나오면 위반(**`ast` 로 판정 가능**)」 신설 + 1장 «규칙 셋»을 **넷**으로.

### ★★★ DDD-2 · **D42 가 존재하지 않는 「Vernon 의 Process Manager」에 존재하지 않는 성립 조건을 붙였다** — blocker

| 문서 | 원전(IDDD 전문 대조) |
|---|---|
| 「**Vernon 의 Process Manager**」 | **IDDD 에 `Process Manager` 0건.** Vernon 은 그 이름을 **의도적으로 피한다** — *"**In an attempt to avoid confusion and ambiguity, I have chosen to use the name Long-Running Process**"*. 「Process Manager」는 **Hohpe·Woolf EIP** 의 패턴이다 |
| 「진행 상태는 **적지 않는다**」 | Vernon 이 제시한 셋 중 **첫째가 «적는» 쪽이고 그가 «가장 두텁게» 다룬 것** — *"…tracked by an executive component that **records the steps and completeness** of the task using a **persistent object**. **This is the approach discussed most thoroughly here.**"* |
| 「절차를 애그리거트에 — **불가능**하다」 | Vernon 의 **권장 최단 경로** — *"merging the concepts of executive and tracker into a single object—**an Aggregate**—to be the simplest approach… **the most basic Long-Running Processes are best implemented just that way.**"* |
| 「워크플로는 업무 지식이라 `framework/` 에 못 온다」(D38 자격 미달) | Vernon 의 tracker 는 **업무 어휘가 아니다** — *"**the tracker is not part of the Core Domain. It is rather part of a technical Subdomain** that any SaaSOvation project can reuse."* **→ 기각 근거가 원전에 안 걸린다** |
| — | **상태를 안 적었을 때** — *"how would the executive know **which parallel process was ending**? … an improperly aligned Long-Running Process could be **disastrous**. The first step … is to assign a **unique Process identity** carried by each of the associated Domain Events."* **트리에 correlation/process id 0건** |

**공정하게** — 체인이 «단일 업무 개체를 따라가는 직렬»인 한 그 개체 id 가 상관자 노릇을 해서 병렬 조인 문제는 약하다. **그러나 D40 이 연 이벤트 축은 fan-out(0~N)이고**, D42 스스로 남긴 구멍(「c 가 실패하면 a 를 되돌려야 할 때… 그때 여는 것도 «순서를 소유한 유스케이스»」)은 **그 유스케이스가 이미 반환된 뒤라 주인이 없다.**
**처분안** — 이름을 「Hohpe·Woolf 의 Process Manager / Vernon 의 **Long-Running Process**」로 바로잡고 **성립 조건 문장을 삭제**, 규율 ⑤ 를 **«조건부»로 되돌린다** — 조건은 「**이벤트가 fan-out 하거나 보상이 요청 밖에서 일어나면 tracker 를 연다**」.

### ★★ DDD-3 · D45 의 「Evans 인용」이 **2007년 실무 보고서 초록**이다 — major

「원전 셋이 같은 낱말을 쓴다」의 Evans 다리 — *"encapsulated the translation… insulating the domain layer from knowing the existence of the other system"* 가 **Blue Book 전문에 0건**. 실제 출처는 **Peng & Hu, dddcommunity practitioner report(2007)** 이고 **과거형으로 자기네 프로젝트를 서술한 문장**이다.
**→ 「원전 셋이 합의한다」는 논증이 «둘 + 실무 보고서»로 내려앉는다.** **T20 에서 지적받은 병의 재발.**
**대체 문장이 있다** — Evans, DDD Reference 2015 p.34: *"Internally, the layer **translates** in one or both directions as necessary between the two models."* **수선 비용 한 줄.**

### ★★ DDD-4 · **「Vernon 의 QueryService」는 유령이고, D41 이 D29 의 «정확한» 인용을 덮어썼다** — major

IDDD 전문에 `QueryService` 는 **2건뿐, 둘 다 GemFire 캐시 API 호출**(`cache.getQueryService()`). Vernon 의 실제 개념은 **Use Case Optimal Query** 이고 **그는 그걸 리포지토리에 둔다** — *"design your **Repository** with finder query methods that compose a custom object as a superset of one or more Aggregate instances"*.
**→ 「원전 셋이 리포지토리라 부르지 않는다」가 Vernon 다리에서 «정반대»로 뒤집힌다.**
**★ 내부 모순이기도 하다 — D29 는 맞게 적어 뒀다**(「Vernon 「Use Case Optimal Query — DTO 가 아니라 값 객체」」). **08-08 의 D41 이 08-06 의 정확한 인용을 부정확한 것으로 덮어썼다.**

### ★★ DDD-5 · D45 가 **facade 와 adapter 의 역할을 맞바꿔 읽었다** — major

- 문서: 「**facade 는 «프로토콜을 감추는» 역할**」
- 원전: **프로토콜은 ADAPTER 의 일** — *"An **ADAPTER** is a wrapper that allows a client to use a different **protocol**"*. **FACADE 는** *"an alternative interface for a subsystem that **simplifies access**"* 이고 *"**The FAÇADE belongs in the BOUNDED CONTEXT of the other system.**"*

**결론(하나로 접기)은 산다** — Evans 자신이 *"**One way of organizing**…"* 이라 적었다. **문제는 근거가 틀린 것**이고, 이 문서는 「근거가 틀렸으면 결론이 맞아도 다시 연다」를 규율로 삼는다(D29 가 스스로 그렇게 했다).
**더 센 대체 근거** — 「facade 는 «지저분한 상대 인터페이스»를 간추리려고 있고 **상대 BC 에 속하는데**, 우리 상대는 트리가 이미 `open_host_service/` 계약으로 깎아 놓은 표면이라 **간추릴 것이 없다**」

### ★ DDD-6 · Reason One 은 «**생성**»에만 걸리는데 검사는 «수정»까지 통과시킨다 — major

원전의 면제는 *"**in order to create batches of them**"* · *"it would not matter whether these were **created** one at a time or in batch"* 로 **생성에 좁혀져** 있다. 문서의 자(「같은 리포지토리냐」)는 **이미 있는 N 개를 고치는 것**까지 통과시킨다 — **Vernon 이 면제한 적 없는 범주.** 계좌 이체를 「사람 판정으로 남긴다」고 적었지만 **실제로는 검사가 «통과»를 선언한다.** 「원전의 면제 ① 그대로」는 과장.

### minor 넷
| | 무엇 |
|---|---|
| **DDD-7** | 「애그리거트당 리포지토리 하나」를 **Evans 가 정했다**고 귀속했는데, Evans 는 «의무»가 아니라 «제한»으로 적었다 — *"**Only provide repositories for AGGREGATE roots that actually need direct access.**"* 트리는 **필수**로 둔다 |
| **DDD-8** | 「waving its hands」 인용의 `…` 이 **주어를 삼켰다** — 손 흔드는 주어는 «**아직 못 찾은 유비쿼터스 언어의 개념**»인데 「경계가 틀렸다」가 주어처럼 읽힌다. **잘린 절이 하필 «어느 쪽으로 고치나»의 답** |
| **DDD-9** | `save()`/`remove()` 근거가 뒤집혔다 — `add`/`remove` 는 **Evans 의 같은 문장에서 나온 한 쌍**(*"Provide methods to **add and remove** objects"*). **결론은 Django 에 정확히 맞지만**(자동 dirty tracking 없음) **진짜 판정 자가 안 적혔다** — Vernon: 저장 지향은 *"when your persistence mechanism doesn't implicitly or explicitly detect and track object changes"* |
| **DDD-10** | 「컨텍스트 맵 패턴을 **줄이지 않고** 쓴다」가 과장 — OHS 의 전제(*"When a subsystem has to be integrated with **many** others"*)와 **탈출구**(*"use a **one-off translator**… for that special case"*)가 둘 다 빠졌다. 컨텍스트 맵 인용 **1건, 그것도 2차 자료**(DDD Crew) |

### 정합 확인 셋
- **Evans 의 «요약값» 허용 인용 — 축자 일치**(*"can also return summary information, such as a count of how many instances meet some criteria"*), 용법도 원전 의도 그대로
- **★ Vernon 의 "Ask Whose Job It Is" — 인용·귀속·단서 «모두» 정확.** 리뷰어 평: **「이 문서에서 가장 잘 된 인용」** — *"Discussing this with Eric Evans revealed…"* 라는 귀속 방식까지 맞고, **마지막 단서(`but only by adhering to the other rules`)를 놓치지 않고 «이렇게 읽으면 안 된다»까지 적었다**
- **Specification 을 폴더로 안 만든 판단** — «정식 패턴이다»와 «구조 요소는 아니다»를 분리한 것이 원전의 위상과 맞다
- (추가 확인) batch/impunity 인용 축자 일치 · 「깨도 되는 이유 넷」 제목 열거 정확 · **Young 의 Thin Read Layer 인용 3건 전부 축자 일치**

---

## ⑤ A — 비대칭·안 적힌 전제 ✅ 도착 (blocker 3 · major 10 · 그 밖 5 · 개수 불일치 13)

### ★★ A-3 · 「컨트롤러는 `port/` 를 직접 잡지 않는다」가 **규칙 슬롯에 0**이고 트리 문구가 **오히려 허용**한다 — blocker

- **있는 쪽**(설명·카드): 「`port/` 를 직접 참조하는 것도 막는다 … 잡는 순간 «무엇을 어떤 순서로»를 컨트롤러가 정하게 된다」 · **D11 이 「구멍이 생겼다」고 자기 입으로 적었다** — 「D14 가 `application_layer/port/` 를 만들면서 «application_layer 만»에 **구멍이 생겼다**(컨트롤러가 `port/Clock` 을 잡아도 문구상 통과)」
- **없는 쪽**(규칙 슬롯): `driving_layer/` 규칙은 아직 「**`application_layer` 만 의존한다**」 — `port/` 가 `application_layer/port/` 라 **문면상 허용**

**3장 4번이 규칙을 «트리 117행의 규칙 문구»에서 뽑는다** → **반대 방향 규칙이 명세에 박힌다.**

### ★★ A-2 · 포트 예외에 «기저»가 없다 — 예외 갈래 셋 중 **둘만 침묵** — blocker

| 갈래 | 기저 |
|---|---|
| 창구 예외 | 「창구당 하나 · 상속 안 하면 **위반**(AST 한 줄)」 — 까닭까지(「조용히 500」) |
| 도메인 예외 | 「**기저를 두지 않는다**」 — 까닭까지(「묶을 대상이 없다」) |
| **포트 예외 · 우회조회 예외** | **0건** — 「필수다」와 「도메인 예외 상속 금지」뿐 |

ACL 어댑터가 「우리 실패로 바꿔 던진다」할 때의 «우리 실패»가 바로 이 파일인데, **어댑터가 포트 예외를 하나 늘리면 유스케이스·컨트롤러의 `except` 목록이 낡는다** — 「조용히 500」이 이 갈래에만 그물 없이 남는다.

### ★★ A-1 · `framework/<capability>/` 에 **«실패» 칸이 없다** — blocker

「대화 하나의 어휘 **셋**(계약·자료·실패)」이 형제 칸(`domain_bypass_query/`)에는 「**규칙이 하나도 늘지 않는다**」로 그대로 복제됐는데 **framework 에는 안 갔다**(framework 열한 칸 전문에 `exception` **0건**). 그런데 `<capability>_port.py` 는 「`port/<capability>_port.py` 와 **똑같이 생겼고 다른 것은 주인이 없다는 것뿐**」을 논거로 쓴다.
**유스케이스가 «직접 import 하는» 계약**이라, 42행이 지목한 「**어댑터가 번역할 대상이 없으면 django·SDK 예외가 안으로 샌다 — 전역 제약 ②가 여기서 깨진다**」가 그대로 성립한다.

### major 열

| | 무엇 |
|---|---|
| **A-4** | 화살표 규칙(D11)이 **입구 넷 중 둘에만** 달려 있다 — `open_host_service/`·`<service>_service.py`·`cron_job/`·`<job>_cron_job.py` 에 **D11 핀이 없고 규칙 슬롯에도 화살표가 0줄**. 탭으로 읽는 문서라 그 탭만 편 사람에겐 규칙이 화면에 없다 |
| **A-5** | driving 탭이 「자식은 **넷**」 바로 다음 문장에서 「**셋**을 가르는 축」 + 「넷째 입구는 **위반**이다」 (C-3·G-2 와 같은 자리, 세 렌즈가 독립으로) |
| **A-6** | 「리프 **전부**」라 해 놓고 목록은 셋(`event_subscription/` 리프 둘 누락). 64행도 「**입구 셋**에 걸린 규칙이 그대로」로 되받는다 |
| **A-7** | 「클린 여섯 중 **넷**만 가져왔다」인데 **칸에 있는 것은 셋** — **Input Boundary 는 칸도 규칙도 0**. 그런데 **A-3 의 논거가 「Controller → Input Boundary → Interactor」로 그 없는 요소에 기댄다** |
| **A-8** | D46 의 「누가·언제·어떻게」가 **한 칸에만**. `domain_bypass_query/<capability>/` 는 «누가» 하나뿐인데 「**같은 세 낱말 · 규칙이 하나도 늘지 않는다**」라 적혀 있고, `framework/<capability>/` 는 **이름 규칙이 아예 없다** → **`smtp_client/` 가 framework 에선 전부 통과.** *D46 의 값이 framework 에서 더 센데도*(유스케이스가 그 이름을 직접 import) |
| **A-9** | 메서드 이름의 자(「명령형 동사구 / 묻는 꼴 · `notify()` 위반」)가 **계약 칸 여섯 중 하나에만**. **D46 이 폴더 규칙을 넓힌 근거가 「메서드 쪽은 «이미» 같은 자를 쓰고 있었다」인데 그 «이미»가 여섯 중 하나** |
| **A-10** | 1:1 짝맞춤이 **한 방향만** — `adapter/` 는 「구현→선언」뿐이고 양방향은 `unit_of_work/` 한 칸(「짝 없는 것이 **한쪽에라도** 있으면 위반」). **선언만 있고 구현이 0인 포트는 어느 검사에도 안 걸린다** |
| **A-11** | **사실을 «발행하는» 자리가 1장 규칙에 0건.** 듣는 쪽은 칸 셋에 규칙 다섯인데 발행 쪽은 유스케이스 규칙에 «발행»이 한 글자도 없다 → **`broker_port.py` 의 「같은 트랜잭션」 검사는 주어가 없어 돌릴 수 없다** |
| **A-12** | framework 탭이 「안에서 다시 **둘**로 갈린다」·「형제 **둘**」인데 자식은 **넷**. **파트 본문 넷에 `broker` 0건** |
| **A-13** | **D44 가 「경로 넷 다 고쳤다」고 적었는데 도해(SVG)는 안 고쳤다** — 카드가 적은 «재사용할 점검»이 흐름 자료구조를 **하나**로 셌다(실제 둘) |
| **A-15** | 「바꾸고·부르고·바꾼다」가 **출구엔 «규칙», 입구엔 «설명»**. 명세는 규칙 슬롯에서 뽑으므로 **T18 이 고친 비대칭이 방향만 뒤집혀 남았다** |
| **A-16** | `broker/` 의 설명(「계약과 배달이 **한 파일에**」) ↔ 이름(「구현은 `<technology>_adapter.py` 로 **나란히 온다**」) ↔ D40 카드(`broker.py`) — **세 이름이 갈린다.** «한 파일»이면 `<technology>_adapter.py` 대상 검사가 **0건**이 되어 유스케이스가 `broker_port.py` 를 직접 잡아도 안 걸린다 |
| **A-17** | 와이어링 셋째(`api_router.py`)가 와이어링 폴더 밖에 사는 까닭이 규칙에 없다 (minor) |
| **A-18** | 「1차 폴더는 도메인 이름만」의 예외 목록이 **D37 이전**(`repository/` 는 이제 2차, `anticorruption_layer/`·`<capability>/` 누락) (minor) |

### 개수 불일치 표 (A 렌즈)
셋↔넷(입구 축) · 셋↔넷(리프 전부) · 넷↔셋(클린 요소) · 셋↔둘(framework 대화) · 둘↔넷(framework 자식) · 넷↔둘(D44 가 고쳤다는 경로) · 38↔**44**(카드) · 32↔**44**(`_record()` docstring) · 103↔**105**(`NAMES`) · **43행↔50행**(D40 카드의 UoW 참조) · 66~87행↔**74~79행**(어드민) · `repository/` 1차↔2차
**※ 이 중 `assert` 로 지켜지는 것은 D8 툴팁 세 수치뿐이다.**

---
---

# 통합 — 12렌즈 · 발견 약 150건

## 겹친 신호 (독립 렌즈가 같은 자리를 잡은 것 = 확실하다)

| 자리 | 잡은 렌즈 |
|---|---|
| **2장이 D40 이전 상태** | C · G · S · EDA · A **다섯** |
| **2장 도해의 행번호 9개가 옛 축** | G · S **둘** (그리고 「32칸」이 그 오류를 «센» 값) |
| **driving 탭이 자식을 셋으로 세고 넷째를 «위반»이라 함** | C · G · A **셋** |
| **`framework/` 갈래 자가 `broker/`·`test/` 를 못 담음** | C · G · A **셋** |
| **`framework/` 포트 방향 / 링 귀속** | HEX · CA **둘** |
| **커밋 직후 사망 = 무기록 유실** | EDA · PY **둘**(PY 는 `run_on_commit` 이 인메모리임을 실행으로 확인) |
| **D45 의 인용·근거** | CA(침묵 논증) · DDD(Evans 아님) · HEX(Cockburn 은 축자 일치) |
| **D43 검사가 못 섬** | CHK(오탐 3·미탐 4) · DDD(식별자 참조 구멍) · SC(대량 갱신) |

## 처분 갈래 — **사용자 결정이 필요한 것 (T32~T41)**

**T32 `framework/` 칸 통째 재검토** — ⓐ 포트를 BC 밖 «안쪽» 자리로 내리고 framework 엔 구현만 ⓑ 「Frameworks & Drivers 링」 표기를 떼고 **명시적 예외**로 적는다. 딸림: 갈래 자를 3단으로(고정 이름 → `*_port.py` → 기술) · `broker/` 한 파일 vs 두 파일 · `<capability>/` 에 `exception.py` 신설 · 이름 규칙 복제

**T33 이벤트 전달 보장** — ⓐ outbox 를 연다 ⓑ **「at-most-once 이며, 유실이 허용되지 않는 전파는 사실이 아니라 커맨드로 보낸다」를 규칙으로.** 딸림: 구독 핸들러 **멱등** 요구 · 실패 리스너 **기록** · 순서 보장 표기 · **Fowler 세 갈래를 «관할 밖»으로 명시**

**T34 D42 재개** — 「Vernon 의 Process Manager」는 **없는 패턴**이고, 내가 «불가능»이라 한 쪽이 Vernon 이 «가장 두텁게» 권한 설계다. ⓐ 이름·근거만 정정 ⓑ **tracker 자리를 조건부로 연다**(「이벤트가 fan-out 하거나 보상이 요청 밖에서 일어나면」) + **process identity** 규칙

**T35 D43 검사** — ⓐ 리시버 식별 규칙 신설(「유스케이스 생성자는 협력자를 **어노테이션으로** 받는다」) ⓑ **신호로 강등**(스펙 #255 로 되돌림). 딸림: **「다른 애그리거트는 식별자로만 문다」 신설**(Vernon 규칙 3 · Django FK 가 사각지대) · 면제를 «생성»으로 좁힘 · `save()`/`remove()` 근거 교체

**T36 D45 검사** — ⓐ 「근사」를 **행에** 표기 + 재구성 면제 ⓑ 사람 판정으로 강등. 딸림: **`persistence/repository/` 의 도메인 예외 예외 처리**(C-1 — 지금 규칙은 지킬 대상이 없다)

**T37 대량 갱신 경로** — ⓐ `save_all()` 셋째 ⓑ `domain_bypass_command/` 신설 ⓒ 「대량은 관할 밖」 명시

**T38 예외 기저 둘** — ⓐ 도메인 애그리거트 기저 + 컨트롤러 마지막 절 ⓑ 포트 예외 기저. **둘 다 「조용히 500」의 그물**

**T39 입구 규칙 둘** — ⓐ 컨트롤러가 `composition_root.build_*` 를 부르는 것(Martin Ch26 정면 충돌) ⓑ 컨트롤러가 `port/` 를 잡는 것(규칙 문구가 허용 중)

**T40 BC 가로지르는 읽기** — 화면 소유 BC · 정렬/페이지네이션 · **인가 규칙 0건** · 공유 `Page` 타입의 무주공산

**T41 D25↔D27** — ninja 관문에 닿으려면 D27 이 금지한 override 가 필요하다(실행 확인). ⓐ D27 에 예외 ⓑ D25 재설계

## 내가 그냥 하는 것 (문면·수치 — 결정 불필요)

**2장 전면 개수** — 개명 넷(SVG) · 행번호 아홉 · 이벤트 축 세 문장 · `exception.py`→폴더 · 실패 예시 파일명 · 「32칸」(고치면 자동 24)
**인용 정정** — Evans ACL(실무 보고서→DDD Reference) · Vernon QueryService 삭제 · facade/adapter 역할 · Richards 「원전 문면」 표식 · Cockburn 「시계」·configurable dependency · Main 「유일한」 · package by layer(Simon Brown) · 「waving its hands」 절 복원
**죽은 문면** — 툴팁 `d29`·`d30` 옛 이름 · D33 검사 ④ · D14 결정 ① · D13 반전 표식 · D34 툴팁 `id` **렌더링 버그** · domain 탭 「처음부터 Port」 · rd-41 WHAT · rd-106 WHAT · 「43행이 막는다」
**수치** — 카드 38→44 · 규칙 447/471→485 · `NAMES` 103→105 · 어드민 행 범위 · D8 주석
**비대칭 복제** — D11 핀 넷 · 「세 줄」을 입구 규칙 슬롯에 · 이름 규칙 셋 · 메서드 이름 자 · 1:1 양방향 · `models/`·`admin/` 재수출
**약어** — `OHS` (규율 ④)
**과적합** — 「실측이 정했다」·「실측이 강제했다」·「실측이 막았다」 근거 교체 · `label` 두 행 정반대 · 「우리」 → 조건 명시
