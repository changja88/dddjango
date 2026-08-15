# 트리 개정 명세 — 규칙 전수 **538**

> **이 문서는 «무엇이 참이어야 하나»만 적는다.** 지금 있는 플러그인도 `broccoli-server` 도 보지 않는다.
> 현행과의 대조는 **계획 5번**이 한다 — 규율 ①(원리로 짓고 기존 구현은 다 만든 뒤 대조)이 그 순서다.
> 근거는 전부 정본(`docs/file_tree.html` · 트리 **140행** · 결정 카드 **57장** · sha `a19a023a52b893bc`)에 있고, 이 문서는 그것을 **한 줄짜리 규칙**으로 편 것이다.

## 컬럼

| 컬럼 | 뜻 |
|---|---|
| **규칙** | 한 줄. 어겼는지 물을 수 있는 문장 |
| **자리** | 정본의 어디서 나왔나 — `트리 N행`(= 오른쪽 패널 `rd-N`) · `D-nn` · 1장 절 이름 |
| **판정** | `path` 경로만으로 · `ast` 파싱 필요 · `human` 의미 판정 |
| **근거** | `principle` 원리·원전 · `both` 원리가 세우고 실측은 크기만 · `measured` 실측이 근거에 들어갔다 |
| **3차** | 과적합 전수 판정 결과 (살아남은 `overfit` **0**) |
| **어겼을 때** | `blocker` · `면제` · `검사기` · `이행` — 아래 «어겼을 때» 절 |

## 진행 — 4번의 네 단계

| | 일 | 상태 |
|---|---|---|
| 0 | 정본의 세 슬롯 중복 정리 | ✅ 44칸 → 0 |
| **1** | **이 목록을 107행 트리에 다시 맞춘다** | ✅ 아래 «변환 기록» |
| **2** | **`어겼을 때` 컬럼 추가** | ✅ 아래 절 |
| **3** | **목록에 없는 규칙 회수** | ✅ **24건 추가 → 447 → 471** |
| **+** | **3차 적대적 리뷰 반영(기계 정정 갈래)** | ✅ 문면 정정 ~40건 · 재분류 34건 · **10건 추가 → 481** — 아래 «3차 리뷰 반영» 절 |
| **+** | **T26·T27 반영 (D39 신설)** | ✅ 정본 먼저(sha `1f3acf513ea0eb11`) → **4건 추가 → 485** · `#474` 확장 — 아래 «T26·T27 반영» 절 |
| **5** | **107행 → 138행 재매핑 · D40~D59 회수** | ✅ 자리 **289건** 재매핑 · 개명 **41종** 스윕 · 뒤집힌 규칙 **14건** 정정 · **110건 추가 → 595** — 아래 «D40~D59 회수» 절 |
| **6** | **5차 적대적 리뷰(14렌즈) 반영** | ✅ **14건 걷어냄** · **65건 정정** · **24건 추가 → 605** — 아래 «5차 회수»·«걷어낸 것» 절 |
| **7** | **C1·C2·C3 반영** | ✅ C1 — 정본 문면만(규칙 0) · C2 — 승격의 자를 «소유»로 · **4건 걷어냄** · **5건 추가 → 606** · 트리 **138 → 140행**(`framework/test/fake/`) · C3 — 독립 넷의 현황 + 엔진 교체를 `면제` 로 **1건 추가 → 607** |

## 변환 기록 — 08-07 판(102행)에서 무엇이 바뀌었나

**① 트리 행 번호 재매핑.** D37 이 트리를 102 → 107행으로 바꿨다. 참조 **272건**을 아래 자로 옮겼다.

| 옛 | 새 | |
|---|---|---|
| 1 ~ 71 | 그대로 | root · driving · application · domain · `driven_layer/` · `django_<bounded_context>/` 부분트리 |
| 72 · 73 | 74 · 75 | `repository/` · `<aggregate>_repository.py` — `adapter/persistence/` 아래로 내려갔다 |
| 74 | 77 | 옛 `repository/<capability>.py`(Thin Read) → `domain_bypass_query/<capability>_query.py` |
| 75 · 76 · 77 | 80 · 81 · 82 | `anticorruption_layer/` 부분트리 |
| 78 · 79 · 80 | 83 · 84 · 85 | `external_system/` 부분트리 |
| 81 | 87 | 옛 `driven_layer/<capability>.py`(파일) → `adapter/<capability>/<technology>_adapter.py` |
| 82 | 79 | 옛 `driven_layer/<boundary>_unit_of_work.py` → `adapter/persistence/unit_of_work/` 아래 |
| 83 ~ 102 | +5 | test · framework · project |

*새로 생겨 옛 번호가 없는 칸* — **72 `adapter/` · 73 `persistence/` · 76 `domain_bypass_query/` · 78 `unit_of_work/`.*

**② 개명 (D37).** `domain_bypass_query` → `domain_bypass_query` **20건** · `unit_of_work/` → `unit_of_work/` **7건** · `…QueryRepository` → `…DomainBypassQuery` **4건** · driven 경로 **5건**.

**③ 내용이 뒤집힌 규칙 8건.** 이름만 바꿔서는 거짓이 되는 것들이다.

| # | 옛 규칙 | 지금 |
|---|---|---|
| **320** | 「`driven_layer/` 안에 `adapter/` 폴더를 **만들지 않는다**」 | **정반대** — `adapter/` 가 생겼고 그 자식이 넷이다 |
| **371** | 「«나머지»는 `driven_layer/` 바로 아래 **파일**로 두고 폴더를 만들지 않는다」 | **폴더다** — `adapter/<capability>/<technology>_adapter.py` |
| **213** | 「포트의 판정은 «**바깥에 행위자가 있나**»이고 DB 는 아니다」 | 판정이 «**이 층 밖인가**»로 바뀌었다(F6) — DB 조회 계약도 `port/` 아래다 |
| **65 · 182** | `application_layer/` 직속 자식 **넷** | **둘** (`<area>/` · `port/`) |
| **318** | `driven_layer/` 자식 **넷** | **둘** (`django_<bounded_context>/` · `adapter/`) |
| **319** | 구동 대상 가르기 — 옛 경로 넷 | `adapter/` 아래 경로 넷으로 |
| **328** | 「`django_<bc>/` 를 import 하는 것은 `repository/` 뿐」 | `adapter/persistence/` 아래 전부 |

**④ 자리 오기 3건.** 424 · 425 · 426 은 `framework/test/` **폴더**의 규칙인데 그 안의 파일 행을 가리키고 있었다 → **트리 99행**(지금 번호로 **130행**)으로.

## 변환 기록 ② — 08-08 판(107행)에서 138행으로

**① 트리 행 번호 재매핑.** D40·D47·D53 과 T47·T48·T50·T53 이 트리를 107 → 138행으로 늘렸다. 자리 컬럼 참조 **289건**을 아래 자로 옮겼다.

| 옛 | 새 | |
|---|---|---|
| 1 | 1 | BC 루트 |
| 2 | 2 · 3 | `composition_root.py` 가 **폴더**가 됐다 — 「폴더 자체」는 2행, 「결선 내용」은 `dependency_wiring.py`(3행) |
| 3 ~ 11 | +4 | `driving_layer/` ~ `schema_out.py` — 앞에 `event_wiring.py`·`published_event/`·`<event>.py` 셋이 들어왔다 |
| 12 ~ 24 | +10 | `open_host_service/` ~ `<job>_cron_job.py` — 앞에 `webhook/` 부분트리 여섯이 들어왔다 |
| 25 ~ 28 | +13 | `application_layer/` ~ `<use_case>_use_case.py` — 앞에 `event_subscription/` 부분트리 셋이 들어왔다 |
| **29** | **소멸** | `<use_case>/dto/` 겹이 없어졌다 — 안의 둘이 유스케이스 폴더로 평평하게 올라왔다 |
| 30 · 31 | 42·43 · 44 | `dto_in.py` → `<use_case>_command.py` + `<use_case>_query.py` **둘** · `dto_out.py` → `<use_case>_result.py` |
| 32 ~ 35 | +13 | `port/` ~ `exception.py` |
| **36** | **49 · 50** | `<payload>.py` 하나가 방향으로 갈렸다 — `<data>_out.py` · `<data>_in.py` |
| 37 ~ 39 | +14 | `domain_bypass_repository/` → **`domain_bypass_query/`** 부분트리 |
| **40** | **54 · 55** | 같은 갈림 — `<payload>.py` → `<data>_out.py` · `<data>_in.py` |
| 41 ~ 43 | +15 | `exception.py` · `unit_of_work/` · `<boundary>_unit_of_work.py` |
| 44 ~ 53 | +15 | `domain_layer/` ~ `<aggregate>_repository.py` |
| **54** | **69 · 70** | 도메인 `exception.py` 가 **폴더 + `<exception>.py`** 로 갈라졌다(D40) |
| 55 ~ 71 | +16 | `shared_value_object/` ~ 어드민 템플릿 |
| 72 ~ 92 | +17 | `adapter/` ~ `factories/` |
| 93 ~ 101 | 112 · 120 · 121 · 125 · 126 · 127 · 130 · 131 · 132 | `framework/` 아래 — 사이에 `broker/` 일곱과 `exception.py`·`<data>_out.py`·`<data>_in.py`·`pure/` 가 들어왔다 |
| 102 ~ 107 | +31 | `<project>/` 부분트리 |

*새로 생겨 옛 번호가 없는 칸 **31개*** — `4 event_wiring.py` · `5 published_event/` · `6 <event>.py` · `16~21 webhook/` 여섯 · `35~37 event_subscription/` 셋 · `43 <use_case>_query.py` · `50 <data>_in.py` · `55 <data>_in.py` · `70 <exception>.py` · `88 templates/<bounded_context>/` · `110 fake/` · `111 <declaration>.py` · `113~119 broker/` 일곱 · `122 exception.py` · `123·124 <data>_out.py·<data>_in.py` · `128 pure/` · `129 <module>.py`.

**② 개명 41종.** `error_out.py` → `bc_error_schema.py` · `<feature>/` → `<area>/` · `dto_in`/`dto_out` → `<use_case>_command`/`<use_case>_result` · `<payload>.py` → `<data>_out.py`·`<data>_in.py` · `domain_bypass_repository` → `domain_bypass_query`(클래스 `…DomainBypassQuery` 포함) · `composition_root.py` → `composition_root/` · 접미사 다섯(`<capability>_port.py` · `<technology>_adapter.py` · `<request>_request.py` · `<job>_cron_job.py` · `<form>_form.py`).

**③ 내용이 뒤집힌 규칙 14건.** 이름만 바꿔서는 **거짓이 되는** 것들이다.

| # | 옛 규칙 | 지금 | 뒤집은 것 |
|---|---|---|---|
| **30** | 「자리표시자 이름의 파일에는 종류 접미사를 붙이지 않는다」 | **정반대** — `<request>_request.py`·`<job>_cron_job.py`·`<form>_form.py`·`<event>_subscription.py` | D41 |
| **174** | `cron_job/` 아래 「접미사를 붙이지 않는다」 | **`_cron_job` 이 필수** | D41 |
| **81** | BC 루트 자식 **여섯** | **일곱** — `published_event/` 가 섰다 | D40 |
| **90** | `driving_layer/` 자식 **셋** · 축은 «행위자» | **넷** — `event_subscription/` · 축은 **«전송»** | D40 · D53 |
| **92** | 잎 목록에 `webhook/`·`event_subscription/` 없음 | 넷 다 든다 | D53 · D40 |
| **105** | `api/` 자식은 `<feature>/` 뿐 | 자식 폴더가 **둘** — `<area>/` · `webhook/` | D53 |
| **17 · 478** | 「어댑터 칸의 1차는 **바깥 행위자**」 | 입구 1차는 **«어떤 전송으로»**, 어댑터 1차는 **«누구를 구동하나»** | D53 · D37 |
| **203** | 「DTO 에 살아 있는 자원 핸들을 싣지 않는다」 | 판정은 **「연 쪽이 «닫기»까지 하나」** — 업로드 알맹이는 `Iterator[bytes]` 로 통과한다 | T43 |
| **207** | 「`dto_in` 은 원시값과 id **로만**」 | 값 객체는 그대로 온다 — 못 담는 것은 **둘뿐** | T43 |
| **289 · 290** | 도메인 예외는 「폴더가 **아니라** 파일」 | **처음부터 폴더** — 「커지면 그때」 조건 자체가 결함이었다 | D40 |
| **353** | 「어댑터 파일 이름은 선언과 **똑같이** 쓴다」 | **선언을 «경로»가 가리킨다** — 이름이 같은 것은 `persistence/` 쪽뿐 | T48 |
| **465** | 「`_repository` 접미사를 **붙이지 않는다**」 | 접미사는 **`_query`** 이고 선언·구현이 함께 단다 | D41 |

**④ 회수 110건(486~595).** D40~D59 스무 장과 신설 칸 스물둘에서 뽑았다 — 아래 «D40~D59 회수» 절.

## C6 반영 — 2건 (트리 신설 0)

**「입구 자식이 늘어나는 것」을 두 행이 반대로 말하고 있었다.**

```
application/<bc>/driving_layer/websocket/chat/chat_controller.py

#90   자식은 api/ · open_host_service/ · cron_job/ · event_subscription/ «넷뿐»   → blocker
#486  골격에 없는 칸이다 (제1원칙)                                              → 반환
#516  「외부가 큐나 gRPC 로 보내면 그건 다른 전송이라 api/ 의 «형제가 는다»」     → 통과
```

원인은 **주어가 지워진 것**이다. `#516` 의 「는다」는 **정본 트리가 개정된다**는 뜻인데, 문면만 읽으면 **BC 가 스스로 늘린다**로 읽힌다. 그러면 BC 마다 트리가 달라져 **제1원칙(#486)이 무너진다.**

`#91` 이 「새 **전송**이 실제로 생기기 전에는 늘리지 않는다」로 절차의 절반을 이미 갖고 있었으므로, **늘리는 주체는 정본 트리다**를 잇는 것으로 닫힌다.

| # | 무엇을 고쳤나 |
|---|---|
| **516** | 후단을 「형제가 는다」 → 「**`webhook/` 에 넣으면 위반**이고 받을 칸은 **정본 트리 개정**으로만 생긴다」 |
| **91** | 「늘리는 주체는 «정본 트리»다 — 개정되면 그 전송을 안 쓰는 BC 도 그 칸을 «빈 채로» 갖는다」를 이었다 |

**WebSocket·gRPC 판정 자는 만들지 않는다** — 없는 전송에 칸이나 자를 미리 벼리는 것은 `#91` 자신이 금지한다. 「HTTP 인가」가 애매한 자리(WebSocket 은 HTTP 로 시작해 업그레이드한다)라 자를 미리 굳히면 틀린 채로 굳는다.

**SSE 는 이 물음 밖이다** — 전송이 HTTP 라 `api/` 안이고, 밀어내는 모양은 `<use_case>_result.py` 가 `Iterator[<UseCase>Result]` 를 돌려주는 것으로 이미 닫혔다(D40).

**「주어가 지워진 문장」은 이 문서에서 되풀이되는 병이다** — D14 의 `dto/`(연 쪽이 닫는다) · D49 의 「못 견딘다」(누가) 에 이어 **세 번째로 같은 모양**이다.

## C7 반영 — 2건 (트리 신설 0 · 규칙 신설 0)

**「감사 로그 칸」은 물음이 아니었다.**

`self._audit_log.save(entry)` 는 **4차 적대적 리뷰가 D43 검사기를 실제로 돌려 보려고 지은 코드**다 — 저장소에도 트리에도 감사 로그는 없다(이 문서에 「감사」라는 낱말이 0건). 정본이 그 사례를 오탐 표에 올리면서 **「리포지토리가 아니다」라고만 적고 «왜 아닌지»를 안 적어서**, 읽는 사람이 「그럼 무엇이냐 · 칸을 만들어야 하나」로 가게 만든 것이 결함이었다.

**★ 사용자가 진짜 자를 짚었다** — *「save 두번이 문제가 아니라 transaction 단위인 aggregate 즉 aggregate_repository에만 적용이 되는거 아니야?」*

```
지금  #546  검사는 「서로 다른 «리포지토리»에 쓰기가 둘」
고침  #546  검사는 「서로 다른 «애그리거트 리포지토리»에 쓰기가 둘」
            = 타입이 domain_layer/<aggregate>/<aggregate>_repository.py 에서 온 것만 센다
```

**「애그리거트 = 트랜잭션 경계」(D50)가 세는 대상을 이미 정하고 있었다** — 애그리거트를 안 가진 것은 셈에 들어올 이유가 없다. 이 한 줄로 **4차 리뷰가 blocker 로 올린 오탐 셋이 한꺼번에 빠진다.**

| 4차 리뷰 CHK-1+2 의 오탐 | 왜 빠지나 |
|---|---|
| `self._audit_log.save(entry)` | 타입이 `<aggregate>_repository.py` 에서 안 왔다 |
| `repo = self._order_repository` (별칭) | 타입이 «같아서» 같은 리포지토리로 센다 → 배치 면제가 산다 |
| `order.lines.remove(line)` | 도메인 객체지 리포지토리가 아니다 |

**근거는 이미 트리 안에 있었다** — `#465` 가 `domain_bypass_query/` 를 *「이 칸은 애그리거트를 안 거치므로 **리포지토리가 아니다**」* 로 스스로 뺐고, 술어 문서의 `#547` 도 `<A>_repository.py` 를 세고 있다.

**기각한 안 둘** — ㉠ `framework/audit/` 칸(감사 로그가 어디 사는지는 D38 이 이미 답한다 · 애초에 없는 것) · ㉡ 「리포지토리가 아니면 `save` 를 쓰지 마라」 역방향 이름 규칙(#546 의 주어를 좁히면 아무 일도 안 한다).

## C8 반영 — 6건 (트리 신설 0 · 신설 1 · 삭제 1)

**`webhook/` 은 「바깥 스펙을 그대로 받는 칸」인데, 그 칸에 «우리가 정한 규칙» 셋이 박혀 있었다.**

OAuth 콜백이 그 모순을 드러냈다 — 「우리 URL 을 바깥에 등록해 두고 그쪽이 부른다」는 **이 칸의 정의 그대로**인데, 걸려 있는 규칙 셋 중 어느 것도 참이 아니다.

| 옛 문면 | 왜 못 서나 |
|---|---|
| `#513` 유스케이스는 **멱등**해야 한다 | 발신자가 재시도할 때만 필요하다 — 브라우저는 한 번 온다 |
| `#515` **ack** 로 답한다 | 응답 형식은 발신자 스펙 (콜백은 리다이렉트다) |
| `#514` 4xx 면 며칠 **재시도**한다 · 「`cron_job/` 과 같은 갈래」 | **우리는 다시 부를 수단이 없다.** celery 는 우리 것이지만 발신자는 아니다 |

**★ 사용자가 넷을 연달아 짚었다** — *「oauth는 webhook이 맞는 거 아니야」* · *「멱등하게 만들 수 있다는 거지 반드시 멱등할 필요도 없는 거 아니야」* · *「webhook 호출하는 건 다른 서비스니 그 서비스 스펙에 맞춰야 하는데 ack 를 강제하는 게 이상하다」* · *「webhook 자체가 재시도가 불가능한 거 아니야」*.

### 걷어내면 «우리가 정할 수 있는 것»이 하나 남는다

```
#629  바깥이 부르는 입구는 «놓칠 수 있는» 입구다 —
      그 입구가 «와야만» 일이 되는 설계는 위반이고,
      빠진 것은 cron_job/ 이 발신자·주인에게 물어 메운다
```

`#629` 는 `ast+` 다 — **후보를 기계가 낸다**: `webhook/**`·`event_subscription/**` 이 부르는 유스케이스가 «쓰는» 애그리거트 집합 **A**, `cron_job/**` 이 부르는 집합 **B** → **A − B ≠ ∅ 이면 후보**(그 애그리거트는 바깥이 안 부르면 영영 안 채워진다). 사람이 답할 물음은 하나다 — 「이 입구가 «안 와도» 업무가 돌아가나」.

`event_subscription/` 은 이 문장을 패널에 이미 갖고 있었고 **`webhook/` 만 없었다.** 셋을 갈라 보면 `webhook/` 이 «우리가 손쓸 수단이 0»인 유일한 통로인데 규칙이 가장 없었다.

| 입구 | 유실되나 | 우리가 손쓸 수 있나 |
|---|---|---|
| `event_subscription/` ← internal | 된다(`#526`) | **된다** — 우리 코드이고 `#566` 이 막았다 |
| `event_subscription/` ← external | **트리는 모른다** — 보장이 «설정»에 있다(`#532`) | 미들웨어가 진다 |
| `webhook/` | 된다 | **못 한다** |

**★ `external` 을 예외로 빼려던 안은 기각했다** — 사용자가 *「external의 경우 재시도도 redis(외부)에서 하는 게 일반적이지 않아?」* 로 짚었고 사실이다. Redis Pub/Sub 도 Celery 기본값도 at-most-once 이고, at-least-once 는 **설정해야** 얻는다. **설정에만 있는 것을 트리가 보장으로 읽으면 안 된다**(T45 가 ORM 캐시에서 만난 모양).

### 정정한 것

| # | 무엇 |
|---|---|
| **513** | **삭제** — `#181`(「멱등성은 유스케이스가 갖는다」)이 흡수. 술어 문서의 **「멱등 물음 소유자」도 `#181` 로 옮겼다**(`#532`·`#603⑵` 가 그것을 참조한다 — ㉯ 가 `#367` 에서 겪은 「소유자를 잃는다」를 되풀이하지 않았다) |
| **514** | 「4xx 면 며칠 재시도」·「`cron_job/` 과 같은 갈래」 → 「**의도**는 우리가, **수단**은 발신자 스펙이」 |
| **515** | 「우리가 돌려주는 ack」 → 「우리가 돌려주는 **응답**」 |
| **511** | OAuth 콜백을 예시로 (「전송이 다르다」·「RFC 는 우리 것」 둘 다 기각) |
| **532** | 「반드시 도달을 **전제**한다」 → 「**요구**로 적되 보장은 설정에 산다」 |
| **629** | **신설** — 「놓칠 수 있는 입구」 |

## 판정 — 네 값

**이 컬럼은 「이 규칙을 검사하는 데 필요한 «최소 수단»」이다.** 「사람이 봐야 하나」가 아니다 — C5 초반에 그 뜻을 「판정 재료가 어디 있나」로 바꿔 읽는 바람에 재분류가 계속 어긋났고, ㉰ 에서 원뜻으로 되돌리면서 **`ast+` 를 신설했다.**

| 값 | 뜻 | 개수 |
|---|---|---|
| **`path`** | 경로·파일명만으로 판정된다. 파일을 안 열어도 된다 | **168** |
| **`ast`** | 파일 내용을 파싱하면 판정된다. **사람 판단 0** | **288** |
| **`ast+`** | **기계가 «후보»를 좁히고 사람이 «마무리»한다** — 검사기가 경고를 내고 리뷰어가 판단하는 자리 | **55** |
| **`human`** | 기계 술어가 아예 없다. 사람에게 «묻는» 수밖에 없다 | **27** |

### ★ `ast+` 가 왜 필요했나 — D45 를 값 하나로는 못 적는다

D45 축자가 *「기계가 후보를 좁히고 사람이 마무리한다」* 인데, 값이 셋뿐이라 그 모양이 전부 `human` 으로 눌려 **«전부 사람 몫»으로 읽혔다.**

```
#547  애그리거트 경계
      기계 — #546(서로 다른 리포지토리에 쓰기 둘)이 후보 목록을 낸다
      사람 — 「이 둘이 «항상 함께 옳아야» 하나?」 한 물음만
```

`ast+` 행은 **반드시 셋을 함께 적는다** — ⑴ 확정 위반 술어 ⑵ 후보 술어 ⑶ 사람이 답할 **한** 물음. 셋을 못 쓰면 그 행은 `ast+` 가 아니라 `human` 이다.

### human 158 → 27 (실질 11)

재분류의 규칙은 하나였다 — **「`ast`/`path`/`ast+` 로 내리려면 술어를 «실제로 써라». 못 쓰면 `human`」.** 술어 131건은 `workspace/design/2026-08-11-predicates.md` 에 있고 **6번(플러그인 개발)이 그대로 받는다.**

| | 158건이 어디로 갔나 |
|---|---|
| `path` 11 · `ast` 63 · `ast+` 57 | **131건이 `human` 을 벗었다** |
| `human` 27 | 그중 **16건은 `어겼을 때 = 면제`** 라 위반 주체가 없다 — 등급이 무의미하다 |

**실질 `human` 은 11건이고 네 갈래다.**

| Q | 건수 | # | 무엇을 묻나 |
|---|---|---|---|
| **Q3** | **4** | #526 · #530 · #563 · #626 | **유실·지연을 «누가» 못 견디나** — C4 가 연 물음이 마지막까지 남았다 |
| **Q0** | **5** | #72 · #449 · #452 · #494 · #592 | **주어가 «코드»가 아니다** — 판정하는 사람·검사기·규칙 문면에게 준 금지라 위반할 파일이 없다 |
| **Q2** | 1 | #316 | 이 조건이 업무 규칙인가 |
| **Q4** | 1 | #254 | 함께 옳아야 하나(애그리거트 경계) — 「너무 갈린 쪽」은 #546 이 잡고 「너무 묶인 쪽」에 기계 신호가 0이다 |

**★ Q0 다섯은 등급이 아니라 «자리»가 문제였고 08-11 에 옮겼다.** `blocker` 로 두면 반송할 파일을 지목할 수 없다 — **`#449`·`#452`·`#494` 셋을 `검사기` 로 옮겼다**(`#72`·`#592` 는 이미 `이행` 이었다 — ㉰ 이 다섯 모두를 `blocker` 로 «적었는데» 실측은 셋이었다). 코드 쪽 귀결은 각각 다른 행이 이미 `ast` 로 갖고 있다(#449→#372·#448 · #452→#451 · #494→#493·#495·#496).

### ★ 재분류가 드러낸 것 셋

1. **한 술어를 두 행이 나눠 갖고 한쪽만 `human` 이던 자리가 여럿이었다** — #179↔#509 · #207↔#202 · #269↔#270 · #259↔#260 · #213↔#229 · #389↔#387 · #617↔#518·#587. ㉯ 가 걷은 «중복»의 잔여다.
2. **`#628` 을 «쓰면 안 되는» 자리가 있다** — #228(포트 자료)의 금지선은 «어휘»가 아니라 **«정의 위치»**다. 토큰 검사를 걸면 「펴서 싣는」 `child_id` 가 전부 오탐이 된다. #518·#587(framework)은 업무 어휘가 0이어야 해서 토큰 검사가 서지만 포트 `<data>_*` 는 아니다.
3. **`#607` 도 잴 수 있다** — 규칙 자신이 「중립 이름으로 갈아입어도 어휘 집합이 못 잡는다」고 적지만, **`viewer_id` 로 갈아입어도 `if amount > 100_000` 의 «리터럴»은 못 갈아입는다.** 반환형 `bool`(#606 이 이미 가짐) + 조건식의 정책 리터럴 + 갈래마다 다른 반환값이 후보 술어다.

## 어겼을 때 — 네 값

**★ 이 트리에는 «어겨도 되는 규칙»이 없다.** `warning` 층을 만들려고 문면을 훑었지만, 완화 표현이 붙은 것은 **전부 「여기는 규정하지 않는다」**(관할 밖)였지 「어겨도 된다」가 아니었다. D10 이 그렇게 정해 놨다 — **트리는 «검사할 수 있는 데까지만» 규정하고, 규정한 것은 절대다.** 그래서 값이 이렇게 갈린다.

| 값 | 테스트 | 개수 |
|---|---|---|
| **`blocker`** | 어긴 것을 **파일 하나로 지목**할 수 있고, 어긴 채 두면 다른 규칙이 성립하지 않는다 | **479** |
| **`면제`** | 규칙 자체가 「여기는 규정하지 않는다」거나 «허가문»이라 위반 주체가 없다 | **22** |
| **`검사기`** | 어길 수 있는 것이 **코드가 아니라 검사기**다(검사 범위·채택 신호·fail-open·라우팅) | **20** |
| **`이행`** | 이관 절차 규칙 — 한 시점의 코드로는 참·거짓이 안 갈린다 | **10** |

**`판정` × `어겼을 때` — 5번이 쓸 표** *(C8 + Q0 이동 후 파일에서 재실측 — 2026-08-11)*

| 판정 | blocker | 검사기 | 이행 | 면제 | 계 |
|---|---|---|---|---|---|
| `path` | 150 | 9 | 4 | 5 | **168** |
| `ast` | 276 | 7 | 4 | 1 | **288** |
| `ast+` | 54 | 1 | 0 | 0 | **55** |
| `human` | 6 | 3 | 2 | 16 | **27** |
| **계** | **486** | **20** | **10** | **22** | **538** |

<span>*(3단계에서 24건이 들어와 447 → 471, 3차 리뷰 반영으로 10건이 들어와 481, T26·T27(D39) 반영으로 4건이 들어와 **485**, 그리고 **D40~D59 회수로 110건이 들어와 595** 가 됐다. 3차에서 허가문 9건이 blocker → `면제`, 검사 범위 6건이 → `검사기` 로 바로잡혔고, «파일 내용을 세는» path 9건이 `ast` 로, 크로스-BC·어휘 판정 4건이 `human` 으로, «두 번째 BC» 3건이 `human` → `ast` 로 옮겨갔다. 복합 제안(ast+human)은 상위 수단 하나로 적는다 — 판정 컬럼은 «충분한 최소 수단»이다. **회수분 110건의 갈림은 `ast` 57 · `human` 30 · `path` 23** 이다 — 신설 칸이 대부분 «파일 안의 모양»을 규정해서다.)*</span>

**읽는 법 — 6번이 만들 것이 세 덩어리다.**

| | 몇 | 무엇 |
|---|---|---|
| `path`+`ast` 의 blocker | **426** | **결정적 백스톱** — 기계가 혼자 판정하고 반송한다 |
| `ast+` 의 blocker | **54** | **후보를 좁히는 검사** — 경고를 내고 리뷰어가 마무리한다. 술어 셋(확정·후보·물음)이 `2026-08-11-predicates.md` 에 있다 |
| `human` 의 blocker | **6** | 기계 술어가 아예 없다 — `#254`·`#316`·`#526`·`#530`·`#563`·`#626` |

<span>08-11 · C5 ㉰ — **옛 문면의 「`human` blocker 148」은 «소거법»으로 매겨진 수였다.** 「기계가 못 하면 human」이라 성질이 다른 것이 한 칸에 뭉쳐 있었고, 전수 재분류로 **131건이 `human` 을 벗고 `ast+` 가 신설됐다**. 남은 실질 `human` 은 **11건**이고 그중 blocker 는 **6건**이다.</span>
**★ 그중 `#486~#492`(제1원칙)는 «다른 모든 검사보다 먼저» 도는 자리라 6번에서 별도 게이트로 뽑는다** — 골격이 어긋나면 나머지 **524개**를 돌릴 이유가 없다.

## 3단계 — 회수한 24건

목록은 **결정 카드가 32장일 때** 뽑혔다. 그 뒤에 선 넷(**D35 · D36 · D37 · D38**)의 규칙이 **하나도 없었다.** 카드를 다시 읽어 24건을 뽑아 넣었다(번호 **448~471**).

| 카드 | 뽑은 것 | 몇 |
|---|---|---|
| **D38** | 승격의 자는 **하나** — 「이 낱말의 뜻을 저장소 밖이 정하나」(**08-10 · C2 개정** — 옛 «자격 + 계기» 둘에서 «소유» 하나로 · 개수를 안 묻는다 · 예외 0) · **강등**(시그니처에 `kind`·`mode`·`bc`·`is_…` 가 나오면 위반 → 인라인해 돌려보낸다 — 절차가 아니라 «판정이 틀렸다»는 사후 신호) · `<capability>/<technology>.py` ↔ `<technology>/<module>.py` 판정 | **6** |
| **D37** | 선언은 전부 `port/` 아래 · 구현은 전부 `adapter/` 아래 · `adapter/` 아래 모든 `.py` 는 «어떤 선언의 구현»이고 이름이 같다 · **ORM 모델 import 는 `persistence/` 아래 셋뿐**(겹 폴더를 정당화하는 공통 규칙) · `<capability>/` 판정 3단 · `command`/`query` 로 안 가른다 · 접미사 · UoW 자리 · `adapter_layer/` 기각 | **10** |
| **D36** | 답을 낼 수 있으면 `response/`, 없을 때만 `exception/` · 판정은 **「이 창구가 «혼자서» 답을 만들 수 있나」** · 「없다」·「거절됐다」는 답이다 · 공개 예외는 «돌려줄 것이 아예 없는» 갈래뿐 · 사유는 «코드»로 | **6** |
| **D35** | **두 BC 가 서로의 `anticorruption_layer/` 에 들어 있으면 위반**(검사는 폴더 목록 두 번) | **1** |
| 트리 | 아무 규칙도 안 걸려 있던 칸 `56` | **1** |

**아무 규칙도 안 걸린 칸이 이제 0이다** — **트리 140행 전부**가 최소 한 줄에서 인용된다(넣기 전엔 `73 persistence/`·`76 domain_bypass_query/`·`78 unit_of_work/`·`56 <value_object>.py` 넷이 비어 있었다).

**정본 밖 명세는 이미 들어와 있었다** — 경로 계약(`#73`·`#74`·`#76`·`#77`·`#78`) · 응용 DTO 검증 차단(`#67`·`#204`). *(§0 「채워질 때 만든다」로 들어왔던 `#22` 는 **5차 리뷰가 걷어냈다** — D54 가 §0 항상-생성을 되살렸다.)*

## 4번은 여기서 끝난다

「끝났다」의 자 — **트리 140행 · 결정 57장 · 규칙 595 를 훑어 «스펙에 안 실린 규칙»이 0**<span>08-11 — 그 뒤 **㉯ 가 중복 71건을 걷어 531**이 됐고, C6~C8 이 신설 1·삭제 1 로 **531 을 유지**한다. 「스펙에 안 실린 규칙 0」은 그대로다.</span>. 다섯 단계가 다 닫혔다.

**측정 둘로 확인한다.**

| 자 | 값 |
|---|---|
| 트리 **140행** 중 규칙이 한 줄도 안 걸린 칸 | **0** *(회수 전 **22**)* |
| 결정 카드 **D1~D59** 중 인용 0건 | **0** *(회수 전 **D42~D59 의 16장**)* |

D40~D59 스무 장이 «하나도» 안 실려 있었고, 트리가 107 → 138행으로 늘며 생긴 칸 스물둘이 규칙 0건이었다. 둘 다 지금 0이다.

그다음이 **5번 — 이 명세를 «어떻게 구현할지»** 다. 그때 처음으로 현행을 연다.

**5번이 먼저 답해야 할 것** — 「**누가 파일을 만드나**」. 제1원칙(`#486~#492`)은 「부모가 있으면 자식은 빈 파일로라도 있다」를 요구하는데, 플러그인에는 **골격 «생성기»가 없다**(`scripts/` 는 전부 `check-*.py`). 검사만으로는 «빈 파일 138개»가 저절로 생기지 않는다.

---

판정 `how`: `path` 경로만으로 · `ast` 파싱 필요 · `human` 의미 판정
근거 `basis`: `principle` 원리·원전 · `both` 원리가 세우고 실측은 크기만 · `measured` 실측이 근거에 들어갔다
`final`: 3차 리뷰 판정(과적합 전수) — **살아남은 `overfit` 0**


## global — 67개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 1 | 트리의 모든 칸에서 의존(import)은 안쪽으로만 향한다. | 1장 «전역 제약 셋» + D5 | `ast` | principle |  | **blocker** |
| 2 | 안쪽 두 칸(domain_layer · application_layer)은 구체 기술을 모른다. | 1장 «전역 제약 셋» + D4 | `ast` | principle |  | **blocker** |
| 3 | BC 경계는 관문으로만 넘는다. | 1장 «전역 제약 셋» + D9 · D11 · D17 | `ast` | principle |  | **blocker** |
| 4 | application_layer/** 의 import 에 django 가 하나라도 있으면 위반이다 — **트랜잭션도 시각도 DB 예외도 포트를 거친다.** | D4+D31 | `ast` | principle |  | **blocker** |
| 5 | 안쪽 칸이 기술을 알아도 되는 예외 조문을 두지 않는다 — 필요한 것은 전부 port/ 뒤로 보낸다. | D4 | `ast` | principle |  | **blocker** |
| 7 | `application_layer` 는 `domain_layer` 와 자기 `port/` 를 import 한다 — **예외는 넷**이다: ⑴ 자기 BC 의 `published_event/`(#540 이 옮겨 담기를 강제한다) ⑵ `framework/broker/{internal,external}/*_broker_port.py`(#539 ③ 이 발행을 강제한다) ⑶ `framework/<capability>/` 의 계약·`exception.py`·`<data>_out.py`·`<data>_in.py`(#404) ⑷ `framework/pure/`. | D5+D40+D47+D59 | `ast` | principle |  | **blocker** |
| 8 | domain_layer 에서 밖으로 나가는 import 는 0 이다 — **django 도 다른 층도 다른 BC 도 모른다.** | D5 + D13 + D24 + 트리 59행 | `ast` | principle |  | **blocker** |
| 9 | `driven_layer` 는 `domain_layer` 와 `application_layer/port/` 만 import 한다 — 예외는 #13(`anticorruption_layer/` 의 타 BC 관문)과 **#535(`apps.py` 의 `ready()` 안에서 자기 BC 의 `composition_root/event_wiring.py`)** 둘이다. | D5+D20+D59 | `ast` | principle |  | **blocker** |
| 10 | 네 칸을 모두 아는 것은 composition_root 하나뿐이다. | D5 | `ast` | principle |  | **blocker** |
| 11 | 층 경계를 넘는 데이터에 엔티티도 DB 행도 실리지 않는다 — 못 싣는 것의 판정은 **「이 손잡이를 «연 쪽»이 «닫기»까지 하나」** 하나이고(T43), 장고 `HttpRequest` 가 닫는 업로드 알맹이는 `Iterator[bytes]` 로 흘려보내 통과한다. 이 판정은 `<use_case>_command.py` 뿐 아니라 포트·OHS 계약·`<data>_out/in.py` 에도 같이 걸린다. | D5+D14+T43 | `ast+` | principle |  | **blocker** |
| 12 | 타 BC 를 import 할 때 부를 수 있는 것은 **둘**이다 — 그 BC 의 `driving_layer/open_host_service/` 아래와 `published_event/` 아래. 나머지는 전부 위반이다. | D9+D11+D40 | `ast` | principle |  | **blocker** |
| 13 | 타 BC 의 open_host_service/ 를 import 하는 것은 driven_layer/adapter/anticorruption_layer/ 뿐이다. | D17 (전역 제약 ③ 출구 쪽 집행 지점)+D37 | `ast` | principle |  | **blocker** |
| 14 | `with unit_of_work:` 블록 «안»에서 크로스-BC 포트를 부르면 위반이다. | D17 «딸려 나온 검사 한 줄» + 2장 흐름 | `ast` | principle |  | **blocker** |
| 15 | 트리는 그 구분으로 규칙을 쓰거나 검사를 할 수 있는 데까지만 규정하고 그 아래는 작성자 재량이다. | D10 | `human` | principle |  | **면제** |
| 16 | 그 구분이 없으면 규칙을 못 쓰거나 검사를 못 할 때만 폴더로 못 박는다. | D10 | `human` | principle |  | **면제** |
| 17 | 폴더의 1차 축은 도메인 이름이고 종류는 2차이며 평면 나열은 금지된다(§0-4) — 무는 곳은 «도메인 것»을 나누는 칸(`<aggregate>/`·`<area>/`)이고, 입구 칸의 1차는 «어떤 전송으로 오나»(`api/`·`open_host_service/`·`cron_job/`·`event_subscription/` — D53)이고 어댑터 칸의 1차는 «누구를 구동하나»(`persistence/`·`anticorruption_layer/`·`external_system/`·`<capability>/` — D37)라 **검사 대상 밖이다**(트리 60·89행 — 이 뒷 절은 «검사기» 등급이다). | D7 근거① · D8 · D24 · D27 · D30 + 트리 60·89행+D53+D37 | `ast+` | principle |  | **blocker** |
| 18 | 종류 이름 폴더가 개념 이름 폴더와 형제로 나란히 오면 §0-4 위반이다 — 단 트리가 명문으로 세운 형제(domain_layer 의 `shared_value_object/`·`domain_service/`, application_layer 의 `port/`)는 위반이 아니다. | D30 판정표 + D27 + 트리 59행 | `ast+` | principle |  | **blocker** |
| 19 | 트리 전체에서 기술 이름을 1차 축으로 쓰는 자리는 framework/<technology>/ 하나뿐이다. | D7 근거① + D24 + 트리 126행 | `path` | principle |  | **blocker** |
| 20 | 값이 하나뿐인 축으로는 폴더를 만들지 않는다. | D7 근거② + D13(specification/) | `path` | principle |  | **blocker** |
| 21 | 어떤 종류가 하나뿐이면 폴더가 아니라 파일로 둔다. | D27 + D12 · D17 선례(unit_of_work.py · <aggregate>_repository.py · exception.py) | `path` | principle |  | **blocker** |
| 23 | 설계 근거는 DDD · 클린 · 헥사고날 셋에서만 끌어오고 broccoli-server 의 현재 모습을 설계 입력으로 쓰지 않는다(규율 ①). | 1장 warn-box «규율 — 원리로 짓고, 기존 구현은 다 만든 뒤에 대조한다» | `human` | principle |  | **면제** |
| 24 | 실측 숫자는 다 만든 뒤 대조에만 쓰고 그 전까지는 근거가 아니라 참고다(규율 ①). | 1장 warn-box | `human` | principle |  | **면제** |
| 25 | 한 겹은 칸·이름·화살표·앎의 범위 넷이 다 정해져야 닫히고, 하나라도 비면 다음 칸으로 넘어가지 않는다(규율 ②). | 1장 «한 겹이 «닫혔다»는 것은 넷이 다 정해진 것» + 2차 리뷰 「규율 ②(한 칸씩 닫고 넘어간다)」 | `human` | principle |  | **면제** |
| 26 | 칸을 열지 말지는 「지금 실측에 쓰이나」가 아니라 「이 칸 자체에 결함이 있나」로 판정한다(규율 ⑤ · R13 이 좁힌 자). | 1장 warn-box(08-07 · R13) | `human` | principle |  | **면제** |
| 27 | 「나중에 생기면 그때 연다」로 끝나는 문장은 그 자체가 결함이므로 근거로 쓰지 않는다. | 1장 warn-box(R13) + D24 «2차 리뷰 S2» + D26 | `human` | principle |  | **면제** |
| 28 | 원전 패턴 이름은 줄이지 않고 풀어 쓴다. | 1장 «명명 방침 — 08-04 확정» + D9 + D16 + D17 | `path` | principle |  | **blocker** |
| 30 | 자리표시자 이름의 파일도 «종류»를 접미사로 단다 — 가르는 자는 **「이름이 곧 서술문이거나 동사구인가」**다(D41). 그런 것만 접미사를 안 단다: `<aggregate>.py`·`<entity>.py`·`<value_object>.py`·`<event>.py`·`<exception>.py`·`<domain_service>.py`·`<migration>.py`·`<feature>.py`·`<declaration>.py`·`<module>.py`·`<environment>.py`. | D41 + D8 «이름» + 1장 «리프 이름 규칙» | `path` | both | `measured_ok` | **blocker** |
| 33 | 파일 이름의 접두는 자기가 속한 곳(부모·조상 폴더)을 가리키고, 자기가 살지 않는 옆 폴더 이름을 접두로 쓰지 않는다. | D27 «이름은 bc_error_schema.py» | `path` | principle |  | **blocker** |
| 34 | 같은 접두는 같은 스코프를 뜻한다 — `<use_case>_*`(`_command`·`_query`·`_result`)는 **유스케이스당**이고 `schema_*`(`schema_in`·`schema_out`)는 **`<area>/` 당**이다. <span>08-11 — 옛 문면의 `dto_*` 와 「feature 당」은 **개명 둘을 못 받은 죽은 문면**이었다(변환 기록 ②의 `dto_in`/`dto_out` → `<use_case>_command`/`_result` 와 `<feature>/` → `<area>/`). `feature` 는 지금 `admin/<entity>/feature/<feature>.py` 라는 **다른 뜻으로 살아 있어** 더 위험했다.</span> | D27 «이름은 bc_error_schema.py» | `path` | principle |  | **blocker** |
| 35 | 저장소 루트의 패키지 이름은 파이썬 표준 라이브러리 모듈명(`sys.stdlib_module_names`)과 겹치지 않는다. | D24 ③ 재결정 + 트리 112행 | `path` | both | `measured_ok` | **blocker** |
| 36 | 칸 이름은 「판정이 되는 물음」을 가져야 하고, 「공통이냐」처럼 정도로 재는 이름은 쓰지 않는다. | D24 ② + D30(«서랍» 방지) | `ast+` | principle |  | **blocker** |
| 39 | port/<capability>/<capability>_port.py 를 구현하는 클래스는 전부 …Adapter 로 끝난다. | D33 검사② + 트리 125행 | `ast` | principle | `principle` | **blocker** |
| 40 | 클래스 이름에서 자리 접미사를 뗀 나머지는 «능력을 말하는 쪽»(보통 파일 이름, 파일이 기술만 말하는 자리에서는 폴더 이름)의 CamelCase 를 **접미사로 포함**한다 — **«포함»이라 접두사가 열려 있다**(`DjangoClockAdapter` ✔ · 무접두 `ClockPort` ✔ — #403·#220 이 요구하는 모양이다). | D33 검사③ (08-07 2차 리뷰 S6 로 앵커가 둘이 됐다) + 트리 125행 | `ast` | principle |  | **blocker** |
| 41 | `Port`·`Adapter`·`Gateway` 는 **폴더** 이름에 나오지 않는다 — 파일은 접미사로 종류를 진다(`<capability>_port.py`·`<technology>_adapter.py`). | D33+D41 | `path` | principle |  | **blocker** |
| 42 | 접미사 검사의 대상은 «자리»가 정한다 — <capability>/<capability>_port.py 안의 클래스만 대상이고 같은 폴더의 exception.py·<data>_out.py·<data>_in.py 는 대상이 아니다. | D33 «검사 대상은 «자리»가 정한다» | `path` | principle |  | **검사기** |
| 43 | 패턴 이름(Gateway·Adapter·Port)은 자리가 대신 말하므로 능력 이름에 쓰지 않고, 동사에서 온 이름(Issuer·Generator·Sender)만 남긴다. | D33 «딸려 닫힌 것 ①» + D18 | `ast` | principle | `principle` | **blocker** |
| 44 | 도메인 서비스 이름이 같은 BC 의 값 객체와 겹치면 행위 이름으로 짓는다. | D33 «딸려 닫힌 것 ②» + D32 | `path` | principle |  | **blocker** |
| 46 | framework/ 에서 application/ 쪽으로 나가는 import 는 0 건이다. | D24 ④ + 트리 112행 + [framework] 파트 | `ast` | measured | `measured_ok` | **blocker** |
| 47 | framework/<capability>/ 에 들어오려면 계약의 이름에도 시그니처에도 어느 BC 의 업무 어휘가 한 글자도 없어야 한다. | D24 «판정이 이분법이어야 한다» + 트리 120행 | `ast` | both | `measured_ok` | **blocker** |
| 48 | 같은 4단 판정을 전역에서도 쓴다 — 「폴더 이름과 같은 파일이 있나」는 D41 이 **`*_port.py` 가 있나로 갈아끼웠다**. | D24+D41+트리 112행 | `path` | principle |  | **blocker** |
| 49 | BC 사이의 공유는 언제나 관문 + 번역으로 풀고 Shared Kernel 은 만들지 않는다. | D24 «shared_kernel/ 은 만들려다 접었다» | `ast` | principle |  | **blocker** |
| 51 | BC 테스트가 다른 BC 의 test 를 import 하면 위반이다. | D24 «⚠ 구현할 때 챙길 것» | `ast` | measured | `measured_ok` | **blocker** |
| 52 | BC 하나를 지웠을 때 바뀌는 파일은 공용 칸(framework/)으로 올리지 않는다. | D24 «새 축»(R11) + D25 ① + 트리 131행 | `ast` | measured | `measured_ok` | **blocker** |
| 53 | framework/test/ 는 HTTP 로만 시스템을 구동한다(모델 import 금지) — **팩토리도 그래서 여기 못 온다**(#392·#620). | D24 «규칙 둘» ① + 트리 130행 + [framework] 파트 | `ast` | principle |  | **blocker** |
| 54 | 규칙을 주소 목록으로 쓰지 않는다 — 목록은 빠뜨리고 규칙은 안 빠뜨린다. | D25 «왜 이 구역이 열려 있었나» + D26(imports= 기각) | `ast+` | measured | `measured_ok` | **검사기** |
| 56 | 트리 밖 구역(scripts/)은 이름도 화살표도 앎의 범위도 규정하지 않는다 — 예외가 아니라 관할 밖이다. | D22 «왜 scripts/ 는 규정 없이 안전한가» + D21 | `human` | principle |  | **면제** |
| 58 | application/**/management/commands/ 를 만들지 않는다. | D22 «결정 — 칸을 만들지 않는다» | `path` | measured | `measured_ok` | **blocker** |
| 59 | 전역 예외 핸들러나 catch-all mapper 로 오류를 가로채지 않는다. | D27 ③ HTTP 표면 + D25(api.py 위반) | `ast` | principle |  | **blocker** |
| 62 | except Exception 을 쓰지 않고, 폴백을 둘 경우 도메인·응용 base 단위 catch 로 한정한다. | D27 ③ 화살표(2차 리뷰 S11 로 조건절이 회복됐다) | `ast` | principle |  | **blocker** |
| 63 | 오류 응답은 operation 이 response={status: <Bc>ErrorSchema} 로 직접 선언하고 openapi_extra 보충·get_openapi_schema override·monkeypatch·postprocessor 로 사후 변형하지 않는다. | D27 «OpenAPI 도 같다» | `ast` | principle |  | **blocker** |
| 64 | 포트 예외(application_layer/port/<capability>/exception.py)는 도메인 예외를 상속하지 않는다. | D27 «08-06 보강(R4)» + 트리 48행 | `ast` | principle |  | **blocker** |
| 67 | application_layer/**/<use_case>_{command,query,result}.py 는 raise 하지 않는다 — 응용 DTO 는 검사하지 않는다. | D30 백스톱 S1 | `ast` | both | `measured_ok` | **blocker** |
| 68 | 검사 자리는 값이 온 곳이 정한다 — 바깥에서 온 값은 입구 schema_in 이, 저장소에서 온 값은 애그리거트가 막고, 우리가 방금 만든 값은 아무도 검사하지 않는다. | D30 «그래서 규칙» | `ast+` | both | `measured_ok` | **blocker** |
| 69 | 개발자 실수를 막는 검사는 런타임이 아니라 테스트·타입 체커의 몫이다. | D30 | `ast+` | principle |  | **blocker** |
| 71 | 도메인은 아무것도 불러오지 않는다 — 도메인 서비스는 포트를 부르지 않고 필요한 값을 인자로 받는다. | D32 + D13 | `ast` | principle |  | **blocker** |
| 72 | 이행은 플러그인 셋(검사 스크립트·리뷰어 지침·표준 문서)을 한 커밋에서 먼저 고치고 그 다음에 코드를 옮긴다. **[Q0]** | D32 «이행 순서 — 플러그인 먼저, 코드 나중» | `human` | principle |  | **이행** |
| 73 | 이관 기간에는 옛 층 이름과 새 층 이름을 둘 다 받는다(이중 수용). | D32 «㉠ 이중 수용» | `ast` | principle |  | **이행** |
| 74 | 저장소가 표준을 채택한 신호가 있는데 검사 대상이 0건이면 exit 2 로 막는다 — «대상 0건»의 낟알(검사기 전체인가 규칙별인가)은 여기서 규정하지 않고 5번(구현 계획)이 191줄 경로 계약과 함께 정한다(규칙별로 읽으면 §0 항상-생성과 충돌한다 — 3차 T16 · 그때 근거로 든 `#22` 는 5차가 걷어냈고 자리를 **#488** 이 잇는다). | D32 «㉡ 가드» | `ast` | measured | `measured_ok` | **검사기** |
| 75 | 그 가드는 touched 필터 «앞»에 둔다. | D32 «가드를 두는 «자리»가 결정적이다» | `ast` | principle |  | **검사기** |
| 76 | 이관이 끝나면 옛 층 이름을 지우고, 그것을 이관 완료 조건에 명시한다. | D32 «⚠ 이관이 끝나면 옛 이름을 지운다» | `ast` | principle |  | **이행** |
| 77 | port/ 자리 역전만은 이중 수용하지 않고 바로 반전한다. | D32 «이 카드의 port/ 역전만은 이중 수용이 「안 된다」» | `ast` | principle |  | **이행** |
| 78 | 검사 스크립트는 대상 목록을 층 폴더 이름 문자열 하나로만 만들지 않고 채택 신호를 둘 이상 쓴다. | D32 «발명이 아니다»(check-layer-skeleton 선례) | `ast` | measured | `measured_ok` | **검사기** |
| 79 | 애그리거트 코어 검사는 repository 를 폴더가 아니라 파일(<aggregate>_repository.py)로 검사한다. | D32 «딸려 나온 것» + 트리 68행 | `path` | principle |  | **검사기** |
| 80 | 필수 종류 폴더 목록에서 BC 레벨 schema/ 를 뺀다 — 이 트리에 BC 레벨 schema/ 는 존재 자체가 없다. | D32 «딸려 나온 것» + D27 + D8 | `path` | principle |  | **검사기** |
| 448 | `framework/` 로 올리는 자는 하나다 — 「이 낱말의 뜻을 **저장소 밖**(표준·프레임워크·OS·프로토콜)이 정하나」. 예면 `framework/`, 우리 업무가 정하면 그 BC 다. | D38 결정①(08-10 · C2 개정) | `ast+` | principle |  | **blocker** |
| 449 | 「몇 개 BC 가 쓰나」는 승격 판정에 넣지 않는다 — BC 가 하나여도 그 BC 것이 아니면 처음부터 `framework/` 에 만들고, 두 BC 가 같은 업무 규칙을 갖고 있어도 각자 갖는다. **[Q0]** <span>08-11 — 「어겼을 때」를 `blocker` → `검사기` 로 옮겼다. **이 행의 주어는 «코드»가 아니라 «판정하는 사람»이라 반송할 파일을 지목할 수 없다**(Q0). 코드 쪽 귀결은 다른 행이 이미 `ast` 로 갖는다.</span> | D38 결정①(08-10 · C2 개정) | `human` | principle |  | **검사기** |
| 450 | 두 BC 가 서로의 `anticorruption_layer/` 에 들어 있으면 위반이다 — 검사는 폴더 목록 두 번이다. | D35 결정㉯ | `path` | principle |  | **blocker** |

## root — 7개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 81 | `application/<bounded_context>/` 바로 아래에는 일곱 가지만 온다 — 층 폴더 넷(`driving_layer/` · `application_layer/` · `domain_layer/` · `driven_layer/`) · `test/` · `composition_root/` · `published_event/`. 여덟째는 없다. | 트리 1행+파트 root | `path` | principle |  | **blocker** |
| 82 | BC 폴더 이름은 장고 앱 이름이 아니라 업무 경계의 이름이다(accounts · billing · ai_chat). | 트리 1행 | `ast+` | principle |  | **blocker** |
| 83 | BC 폴더를 통째로 지웠을 때 그 업무만 사라지고 나머지 BC 는 그대로 돌아야 한다 — 다른 BC 의 import 가 깨지면 그건 경계가 아니다. | 파트 root | `ast` | principle |  | **blocker** |
| 84 | `composition_root/` 는 BC 루트에 두고 네 층 폴더 어디에도 두지 않는다. | 트리 2행+D6 | `path` | both | `measured_ok` | **blocker** |
| 85 | `composition_root/dependency_wiring.py` 에는 `build_<use_case>()` 팩토리만 온다 — 오는 것은 «만들기»와 «꽂기» 둘뿐이다. | 트리 3행+파트 root | `ast` | principle |  | **blocker** |
| 86 | `composition_root/dependency_wiring.py` 안에서 조건문이 업무를 가르거나 값을 계산하기 시작하면 그 코드는 유스케이스로 내려간다. | 트리 3행 | `ast+` | principle |  | **blocker** |
| 87 | `composition_root/` 아래 파일은 자기 BC 의 `composition_root` 만 import 한다 — import 경로의 BC 이름이 자기 BC 이름과 다르면 위반이다. | D6 | `ast` | both | `measured_ok` | **blocker** |

## driving — 85개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 88 | BC 의 입구 계층 폴더 이름은 `driving_layer/` 다 — `presentation_layer/` 를 쓰지 않는다. | 트리 7행+D3 | `path` | principle |  | **blocker** |
| 89 | 바깥 행위자가 BC 를 부르는 통로는 `driving_layer/` 뿐이다 — 다른 층에 입구를 두지 않는다. | 트리 7행 | `ast` | principle |  | **blocker** |
| 90 | `driving_layer/` 의 자식은 `api/` · `open_host_service/` · `cron_job/` · `event_subscription/` 넷뿐이고 **«어떤 전송으로 오나»로만** 갈린다 — HTTP · 같은 프로세스 함수 호출 · celery · 브로커. **「누가 부르나」(행위자)로 가르지 않는다.** | 트리 7행+D26+D40+D53 | `path` | principle |  | **blocker** |
| 91 | 새 **전송**이 실제로 생기기 전에는 `driving_layer/` 의 자식을 늘리지 않는다 — 「새 행위자」로는 늘리지 않는다(웹훅이 그 반례다: 결제사라는 새 행위자가 왔지만 전송이 HTTP 라 2차 축 `webhook/<provider>/` 로 들어갔다). **늘리는 주체는 «정본 트리»다** — 개정되면 #486 에 따라 **그 전송을 안 쓰는 BC 도 그 칸을 «빈 채로» 갖는다**. BC 가 스스로 만들면 BC 마다 트리가 달라져 **제1원칙이 무너진다**. <span>08-11 · C6 — 옛 문면은 「늘지 않는다」로 끝나 «누가 늘리나»가 비어 있었고, 그 빈자리를 #516 이 「BC 가 늘린다」로 채우고 있었다.</span> | 트리 7행+D26+D53+D54 | `path` | principle |  | **blocker** |
| 92 | `driving_layer/` 의 잎(`api/<area>/` · `api/webhook/<provider>/` · `open_host_service/<service>/` · `cron_job/<job>_cron_job.py` · `event_subscription/` 아래)은 `application_layer/<area>/` 아래만 의존한다 — 예외는 **넷**이다 — #95(도메인 exception·값 객체) · #97(`composition_root` 의 `build_`) · **#507(남의 `published_event/`)** · **`framework/<technology>/`·`framework/<capability>/` 의 계약·스키마(#420·#517 이 라우트 데코레이터에서 그 import 를 «요구»한다 — 안 열면 모든 컨트롤러가 blocker 다. `application_layer` 쪽은 #7 이 이미 열어 뒀다)**. | 트리 7행+D11+D40+D53 | `ast` | principle |  | **blocker** |
| 93 | `driving_layer/` 의 잎은 `application_layer/port/` 를 import 하지 않는다. | D11 | `ast` | principle |  | **blocker** |
| 94 | `driving_layer/` 의 잎은 `driven_layer/` 를 import 하지 않는다. | D11 | `ast` | principle |  | **blocker** |
| 95 | `driving_layer/` 의 잎이 `domain_layer` 에서 import 할 수 있는 것은 `exception` 모듈과 `value_object/`(및 `shared_value_object/`) 뿐이다. | D11 | `ast` | both | `measured_ok` | **blocker** |
| 96 | `driving_layer/` 의 잎은 애그리거트·엔티티·리포지토리 선언·도메인 이벤트·포트 선언을 import 하지 않는다. | D11 | `ast` | principle | `principle` | **blocker** |
| 97 | `driving_layer/` 의 잎은 자기 BC 의 `composition_root` 에서 `build_` 로 시작하는 이름만 import 한다. | D11+D6 | `ast` | principle |  | **blocker** |
| 98 | `driving_layer/` 의 잎은 타 BC 의 `composition_root` 를 import 하지 않는다 — 관문(OHS) 우회다. | D11+D6 | `ast` | principle |  | **blocker** |
| 99 | `api/` 바로 밑 결선 파일 `api_router.py` 는 잎이 아니므로 driving 화살표 검사의 대상이 아니다. | D11+D6 | `path` | principle |  | **검사기** |
| 100 | `driving_layer/` 는 구체 프레임워크를 알아도 된다 — 전역 제약 ②(안쪽은 구체 기술을 모른다)의 대상이 아니다. | D11 | `human` | principle |  | **면제** |
| 101 | BC 안쪽(application·domain·driven)과 `composition_root` 는 `driving_layer` 를 import 하지 않는다 — 예외가 없다(rd-2: composition_root 는 driving 을 한 번도 부르지 않는다). | D11+트리 2행 | `ast` | principle |  | **blocker** |
| 102 | 타 BC 는 `driving_layer` 중 `open_host_service/` 아래만 import 한다. | D11+D9 | `ast` | principle |  | **blocker** |
| 103 | 입구가 값 객체를 쓰는 폭은 쿼리 문자열을 값 객체로 파싱하고 되돌릴 때 다시 문자열로 굽는 데까지다. | D11 | `ast+` | principle |  | **blocker** |
| 105 | `api/` 바로 아래 «파일»은 `api_router.py` 와 `bc_error_schema.py` 둘뿐이고, 자식 «폴더»는 `<area>/` 와 `webhook/` 둘뿐이다. | 트리 8행+D6+D27+D53 | `path` | measured | `measured_ok` | **blocker** |
| 107 | `api/api_router.py` 는 `def register_<bc>_api(api)` 등록 함수 하나만 갖는다. | 트리 9행+D6+D27 | `ast` | principle |  | **blocker** |
| 108 | `api_router.py` 는 전역 API 객체를 import 하지 않고 인자로 받는다 — BC 가 프로젝트를 import 하지 않는다. | 트리 9행+D6 | `ast` | principle |  | **blocker** |
| 109 | 등록은 `register_<bc>_api(api)` 함수 안에서만 하고 module top-level 에서 `register_controllers` 를 부르지 않는다(부작용 등록 금지). | D6+D27 | `ast` | principle |  | **blocker** |
| 110 | 등록되는 컨트롤러는 `@api_controller(..., auto_import=False)` 로 자동 등록을 끈다. | D6+D27 | `ast` | principle |  | **blocker** |
| 111 | `api_router.py` 가 하는 일은 자기 BC 의 컨트롤러를 import 해 `api.register_controllers(...)` 를 부르고 경로 접두사·태그를 정하는 것뿐이다. | 트리 9행+D6 | `ast` | principle |  | **blocker** |
| 112 | 등록 파일 이름은 `api_router.py` 다 — `<bounded_context>_` 접두를 붙이지 않는다. | 트리 9행+D6 | `path` | principle |  | **blocker** |
| 113 | 등록 파일은 `driving_layer/` 바로 밑이 아니라 `api/` 바로 밑에 둔다 — `open_host_service/` 와 `cron_job/` 은 등록 함수를 갖지 않는다. | D27 | `path` | measured | `measured_ok` | **blocker** |
| 114 | `driving_layer/api/bc_error_schema.py` 는 BC 당 정확히 한 파일이고 **항상 있다** — HTTP 오류를 아직 안 여는 BC 에도 «빈 파일»로 있다(부모 `api/` 가 항상이기 때문이다). | 트리 10행+D27+D54 | `path` | measured | `measured_ok` | **blocker** |
| 117 | BC 안에 두 번째 ErrorCode 컨테이너를 두지 않는다. | D27 | `ast` | principle |  | **blocker** |
| 118 | BC 오류 파일 이름은 `bc_error_schema.py` 다 — `schema_bc_error_schema.py` 처럼 자기가 안 사는 옆 폴더 이름을 접두로 달지 않는다. | D27 | `path` | principle |  | **blocker** |
| 119 | 401·403·404·422·429·`HttpError`·미식별 500 은 `framework` 가 소유한다 — BC 가 이를 자기 오류 언어로 다시 선언하지 않는다. | D27 | `ast` | principle |  | **blocker** |
| 120 | `api/` 의 1차 축은 `<area>/` 다 — 기술 폴더(`ninja/`)를 만들지 않는다. | 트리 11행+D7 | `path` | principle |  | **blocker** |
| 121 | `api/<area>/` 의 이름은 안쪽 `application_layer/<area>/` 와 글자까지 같아야 한다. | 트리 11행 | `path` | principle |  | **blocker** |
| 123 | `api/<area>/` 의 진입점은 `<area>_controller.py` 파일 하나다. | 트리 12행+D10 | `path` | principle |  | **blocker** |
| 124 | 컨트롤러는 요청 하나당 메서드 하나를 갖는다. | 트리 12행 | `ast` | principle |  | **blocker** |
| 125 | 컨트롤러 메서드는 `schema_in`→`<use_case>_command` 변환 · 유스케이스 1회 호출 · `<use_case>_result`→`schema_out` 변환만 한다 — 입구에 로직을 두지 않는다. | 트리 12행+D11 | `ast+` | principle |  | **blocker** |
| 126 | 도메인 예외를 `ErrorSchema`·상태 코드로 바꾸는 매핑을 컨트롤러 메서드 안에 직접 쓴다 — helper·factory·serializer·handler 등록 decorator·global mapper 로 옮기지 않는다. | 트리 12행+D27 | `ast` | principle |  | **blocker** |
| 127 | 같은 예외→코드 매핑이 여러 컨트롤러에 반복되는 것은 **개수와 무관하게** 허용한다 — 추출은 #126 이 금지한다(그 교환은 D27 ③). | D27 ③ | `human` | principle |  | **면제** |
| 129 | 예외 번역은 알려진 구체 예외의 전수 명시 매핑으로 한다. | D27 | `ast` | principle |  | **blocker** |
| 131 | 기술 이름은 파일이 아니라 클래스에 붙는다 — `NinjaTurnController`. | 트리 12행+D7 | `ast` | principle |  | **blocker** |
| 132 | 라우트 데코레이터 · 인증 선언 · 상태 코드는 컨트롤러 파일에 온다. | 트리 12행 | `ast` | principle |  | **blocker** |
| 134 | 컨트롤러는 매 요청 `build_<use_case>()` 를 불러 유스케이스를 얻고, 유스케이스나 리포지토리 구현체·어댑터를 직접 만들지 않는다. | D11+D6 | `ast` | principle |  | **blocker** |
| 135 | `schema/` 는 `api/<area>/` 아래에 온다 — BC 층이나 최상위 형제로 두지 않는다. | 트리 13행+D8 | `path` | both | `measured_ok` | **blocker** |
| 136 | `schema/` 안의 파일은 `schema_in.py` · `schema_out.py` 둘뿐이고 방향으로만 갈린다 — 필드나 화면이 늘어도 파일 수는 늘지 않는다. | 트리 13행+D8+D10 | `path` | principle |  | **blocker** |
| 137 | `schema_in.py`·`schema_out.py` 안의 클래스 구성은 규정하지 않는다(작성자 재량). | 트리 13행+D10 | `human` | principle |  | **면제** |
| 139 | 요청의 본문·쿼리 파라미터·경로 파라미터의 필드와 타입, 필수 여부, 길이·범위 제약은 `schema_in.py` 에 선언한다. | 트리 14행 | `ast` | principle |  | **blocker** |
| 140 | 사용자 입력 검증의 첫 관문은 `schema_in.py` 의 선언이다. | 트리 14행 | `ast+` | principle |  | **blocker** |
| 141 | `schema_in.py` 는 도메인 값 객체를 import 해 문자열을 값 객체로 바꿀 수 있다. | 트리 14행+D11 | `ast` | principle |  | **면제** |
| 142 | 요청 스키마는 도메인 객체(애그리거트·엔티티)를 만들지 않는다. | D8 | `ast` | principle |  | **blocker** |
| 143 | `schema_out.py` 는 `<use_case>_result` 을 받아 만든다. | 트리 15행 | `ast` | principle |  | **blocker** |
| 144 | 응답에 애그리거트를 그대로 싣지 않는다 — 응답 스키마가 도메인 타입을 직접 노출하지 않는다. | 트리 15행+D8+D11 | `ast` | principle |  | **blocker** |
| 145 | 값 객체를 다시 문자열로 굽는 것은 허용된다. | 트리 15행 | `human` | principle |  | **면제** |
| 146 | 타 BC 입구는 `driving_layer/open_host_service/` 에 둔다 — 최상위 `published_service/` 칸을 만들지 않는다. | 트리 22행+D1 | `path` | both | `measured_ok` | **blocker** |
| 148 | 일반어가 된 약어는 풀어 쓰지 않는다 — `api` 를 `application_programming_interface` 로 쓰지 않는다. | D9 | `path` | principle |  | **blocker** |
| 149 | `open_host_service/` 는 HTTP 가 아니라 같은 프로세스 안의 함수 호출이다 — 라우팅·등록 함수를 두지 않는다. | 트리 22행+D27 | `ast` | measured | `measured_ok` | **blocker** |
| 150 | `open_host_service/` 의 1차 축은 `<service>/` 폴더다 — 바로 아래에 평면 `.py` 를 두지 않는다. | 트리 23행+D9 | `path` | principle |  | **blocker** |
| 151 | 창구 이름은 「무엇을 해 주는가」로 짓는다 — `child_lifecycle_service/` · `notification_publish_service/`. | 트리 23행 | `ast+` | principle |  | **blocker** |
| 152 | 창구 하나의 진입점은 `<service>/<service>_service.py` 파일 하나다. | 트리 24행+D9+D10 | `path` | principle |  | **blocker** |
| 153 | `<service>_service.py` 는 계약 타입을 응용 DTO 로 바꾸고, 유스케이스를 부르고, 결과를 계약 타입으로 되돌리는 일만 한다 — **#164 가 요구하는 «도메인 예외 → `contract/exception/` 번역»은 그 「되돌리는 일」에 들어간다**(거절도 답이다). 도메인 예외는 «타입»으로만 쓰고 속성을 읽지 않는다. | 트리 24행+D9 | `ast+` | principle |  | **blocker** |
| 154 | `<service>/` 안은 `<service>_service.py` 와 `contract/` 둘로 구성한다. | 트리 25행+D9 | `path` | both | `measured_ok` | **blocker** |
| 155 | `contract/` 는 `request/` · `response/` · `exception/` 셋으로 갈리고 잎까지 규정한다. | 트리 25행+D9+D10 | `path` | principle |  | **blocker** |
| 156 | `contract/request/` 에는 이 창구가 받는 타입만 둔다. | 트리 26행 | `ast` | principle |  | **blocker** |
| 157 | 요청 계약 타입 하나 = 파일 하나다. | 트리 27행+D10 | `ast` | both | `measured_ok` | **blocker** |
| 159 | `contract/response/` 에는 이 창구가 돌려주는 타입만 둔다. | 트리 28행 | `ast` | principle |  | **blocker** |
| 160 | 응답 계약 타입 하나 = 파일 하나다. | 트리 29행+D10 | `ast` | both | `measured_ok` | **blocker** |
| 162 | 응답 계약에 도메인 객체를 그대로 담지 않는다. | 트리 29행 | `ast` | principle |  | **blocker** |
| 163 | `contract/exception/` 은 연산 축이 아니라 서비스 스코프다. | 트리 30행+D27 | `path` | principle |  | **blocker** |
| 164 | 도메인 예외를 `contract/exception/` 의 타입으로 번역해서 던진다 — raw 로 전파하지 않는다. | 트리 30행+D27 | `ast` | principle |  | **blocker** |
| 166 | 서비스당 기저 예외 하나를 `<service>_published_error.py` 에 둔다. | 트리 31행+D27 | `path` | principle |  | **blocker** |
| 167 | 이 창구가 던지는 나머지 published 예외는 전부 그 기저 예외를 상속한다(중간층 경유 허용). | 트리 31·32행+D36 | `ast` | principle |  | **blocker** |
| 168 | published 예외는 클래스 하나당 1모듈이다. | 트리 32행+D10+D27 | `ast` | principle |  | **blocker** |
| 169 | 예외 계약 파일명은 주 클래스명의 snake_case 다. | D27 | `path` | principle |  | **blocker** |
| 170 | 예외 계약 파일·클래스에 `_v1` 접미를 붙이지 않는다. | 트리 32행+D27 | `path` | principle |  | **blocker** |
| 171 | 예외 이름은 「무엇이 안 됐는가」로 짓는다 — 부르는 쪽이 이름만 보고 분기할 수 있어야 한다. | 트리 32행 | `ast+` | principle |  | **blocker** |
| 172 | 예약 실행 입구는 `driving_layer/cron_job/` 에 `api/`·`open_host_service/` 와 나란히 둔다. | 트리 33행+D26 | `path` | principle |  | **blocker** |
| 173 | 폴더 이름은 역할(`cron_job/`)이고 기술(celery)은 파일 안에 있다 — `celery/` 폴더를 만들지 않는다. | 트리 33행+D26 | `path` | both | `measured_ok` | **blocker** |
| 174 | `cron_job/` 아래는 하위 폴더 없이 `<job>_cron_job.py` 파일 하나씩이고 `_cron_job` 접미사가 필수다. | 트리 33·34행+D26+D41 | `path` | both | `measured_ok` | **blocker** |
| 175 | `cron_job/__init__.py` 가 `<job>` 들을 재수출한다 — 재수출이 없으면 celery task 가 등록되지 않는다. | 트리 33행+D26 | `ast` | principle |  | **blocker** |
| 178 | 소비 task 가 껍데기를 넘어 조율을 시작하면 새 칸을 여는 것이 아니라 입구 로직 금지 위반을 고친다. | D26 | `ast` | principle |  | **blocker** |
| 179 | 예약 작업 하나 = 파일 하나이고, 그 파일은 유스케이스 하나를 부르는 것이 전부다. | 트리 34행+D26 | `ast` | both | `measured_ok` | **blocker** |
| 180 | `<job>_cron_job.py` 는 재시도와 주기를 모른다 — 둘 다 celery 설정이 갖고, 재시도 루프를 갖기 시작하면 입구에 로직이 생긴 것이다. | 트리 34행+D26 | `ast` | principle |  | **blocker** |
| 181 | 멱등성은 `cron_job/` 이 아니라 유스케이스가 갖는다 — **바깥이 부르는 입구 전부에 같다**(`webhook/` · `event_subscription/`). <span>08-11 · C8 — `#513`(「웹훅이 부르는 유스케이스는 멱등해야 한다」)을 흡수했다. 그 행은 「발신자가 재시도한다」를 근거로 삼았는데 **재시도 여부가 발신자 스펙에 달렸다** — OAuth 콜백처럼 브라우저가 한 번만 오는 상대도 `webhook/` 에 산다. 멱등이 «필요한지»는 저쪽이 정하고, «어디가 지는지»만 우리가 정한다.</span> | D26 | `ast+` | measured | `measured_ok` | **blocker** |
| 451 | 창구가 답을 낼 수 있으면 전부 `contract/response/` 로 가고, 낼 수 없을 때만 `contract/exception/` 으로 간다. | D36 결정㉮+트리 18·20행 | `ast+` | principle |  | **blocker** |
| 452 | 그 판정은 「이 창구가 «혼자서» 답을 만들 수 있나」다 — 「부르는 쪽이 그걸 받고 계속 하나」를 묻지 않는다(창구는 부르는 쪽을 모른다). **[Q0]** <span>08-11 — 「어겼을 때」를 `blocker` → `검사기` 로 옮겼다. **이 행의 주어는 «코드»가 아니라 «판정하는 사람»이라 반송할 파일을 지목할 수 없다**(Q0). 코드 쪽 귀결은 다른 행이 이미 `ast` 로 갖는다.</span> | D36 판정 축 교체+트리 28행 | `human` | principle |  | **검사기** |
| 453 | 「물건이 없다」·「이미 접수돼 있다」·「업무 규칙이 거절한다」는 예외가 아니라 답이다 — 빈 목록이거나 「못 했다 + 사유」다. | D36 결정㉮+트리 28행 | `ast` | principle |  | **blocker** |
| 454 | 공개 예외에 남는 것은 «돌려줄 것이 아예 없는» 갈래뿐이다 — 저장소가 죽었거나 우리가 부르는 바깥이 응답하지 않을 때다. | D36 결정㉮+트리 30행 | `ast` | principle |  | **blocker** |
| 455 | 못 해 준 사유는 «코드»로 담고 자유 문자열로 담지 않는다 — 문구를 다듬는 순간 남의 BC 가 깨진다. | D36 결정㉯+트리 28행 | `ast` | principle |  | **blocker** |
| 456 | 모양이 틀린 요청은 계약 위반이라 `contract/exception/` 이 아니라 테스트·타입 체커가 받는다. | D36 결정㉮ | `ast` | principle |  | **blocker** |

## application — 56개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 182 | `application_layer/` 의 직속 자식 폴더는 `<area>/` · `port/` **둘뿐**이다 — `domain_bypass_query/` 와 `unit_of_work/` 는 `port/` 안으로 들어갔다. | 트리 38행+D30+D14+D37 | `path` | both | `measured_ok` | **blocker** |
| 183 | `application_layer/` 아래에 `validation/` 폴더나 `*_validation.py` 파일을 두지 않는다. | 트리 38행+D30 | `path` | both | `measured_ok` | **blocker** |
| 185 | `application_layer` 는 `driven_layer` 와 `driving_layer` 를 import 하지 않는다. | D14 결정③ | `ast` | principle |  | **blocker** |
| 186 | `application_layer` 는 타 BC 를 직접 부르지 않고 자기 `port/` 를 거친다. | D14 결정③ | `ast` | principle |  | **blocker** |
| 187 | 포트 선언에 BC 최상위 칸을 만들지 않는다 — 애그리거트에 안 붙는 포트는 `application_layer/port/` 에만 산다. | D2 | `path` | principle |  | **blocker** |
| 188 | `application_layer/<area>/` 는 `driving_layer/api/<area>/` 와 같은 이름으로 1:1 대응한다. | 트리 39행+D14 | `path` | principle |  | **blocker** |
| 189 | `<use_case>/` 폴더 안 모듈은 그 유스케이스 소유다 — 다른 유스케이스가 그 안을 import 하면 위반이다. 함께 쓸 것이 생기면 «올리는» 것이 아니라 제자리로 보낸다: 업무 판정이면 `domain_layer/`(#194), 바깥 능력이면 `port/`, 기술이면 `framework/`, 어디도 아니면 각 유스케이스의 진입점 안에 중복해 둔다(성급한 공통화 금지). <span>08-11 · T61 ⓑ — 옛 처방부(«`<area>/` 바로 아래로 올린다»)는 트리 39행에 파일 칸이 없어 #490 과 모순인 죽은 처방이었고, 원전 조사(CA ch.16 우발적 중복 경고·Entities 정의·VSA «push into the domain» — 2026-08-11-cross-usecase-sharing-research.md)가 «공유는 옆이 아니라 아래로»를 확인해 개정.</span> | 트리 39·40행+D28 | `ast` | measured | `measured_ok` | **blocker** |
| 190 | 유스케이스 하나 = 폴더 하나 = 진입점 하나다. | 트리 40행+D14 | `path` | principle |  | **blocker** |
| 191 | `<use_case>/` 폴더 이름은 동사로 짓는다(`start_turn/` · `evict_child/`). | 트리 40행+D14 | `ast+` | principle |  | **blocker** |
| 192 | 절차가 길어도 `<use_case>/` 에 파일을 늘리지 않는다 — 조각은 `<use_case>_use_case.py` 안 `_` 사설 함수로 두고, `service/` 같은 종류 폴더도 만들지 않는다. 사설 조각이 자라면 도메인으로 내릴 판정이 남았다는 신호다(#194). <span>08-11 · T61 ⓑ 부속 — 옛 문면(«쪼갠 모듈도 폴더 안에»)은 트리 40행이 파일 넷으로 닫혀 있어 #490 과 모순(죽은 처방)이라 트리 정합으로 개정. #189 의 «중복해 둔다»가 설 자리도 이 문면이 정한다(진입점 안 사설).</span> | 트리 40행+D28 | `path` | measured | `measured_ok` | **blocker** |
| 193 | 유스케이스의 진입점 파일 이름은 `<use_case>_use_case.py` 다. | 트리 41행+D14+D28 | `path` | principle |  | **blocker** |
| 194 | 유스케이스는 업무 규칙을 갖지 않는다 — 조건문이 «무엇이 옳은가»를 가르기 시작하면 그 조건은 도메인으로 내려간다. | 트리 41행+파트 [application] 목표 | `ast+` | principle |  | **blocker** |
| 195 | 상태를 바꾸는 유스케이스는 애그리거트를 건너뛰지 않는다 — 건너뛸 수 있는 것은 조회 전용·순수 위임·외부 조회뿐이다. | D14 | `ast` | principle |  | **blocker** |
| 196 | Input Boundary · Output Boundary · Presenter 는 `application_layer` 에 넣지 않는다. | D14 결정① | `ast` | principle |  | **blocker** |
| 197 | 읽기 전용 유스케이스는 UnitOfWork 를 받지 않는다. | D14 | `ast` | principle |  | **blocker** |
| 200 | 커밋 뒤 부작용은 `unit_of_work.after_commit(...)` 에 맡긴다 — 응용이 `transaction.on_commit` 이나 `connection.in_atomic_block` 을 직접 부르지 않는다. | D31 | `ast` | both | `measured_ok` | **blocker** |
| 201 | 유스케이스가 주고받는 자료는 그 `<use_case>/` 바로 아래 세 파일(`<use_case>_command.py` · `<use_case>_query.py` · `<use_case>_result.py`)로 둔다 — `dto/` 겹을 만들지 않는다(파일 «이름»에서 `dto` 를 뗀 근거는 D55 이고, 산문에서 이 자료를 「응용 DTO」라 부르는 것은 그대로다). | 트리 40·42·43·44행+D14+D28+D55 | `path` | principle |  | **blocker** |
| 202 | DTO 에는 애그리거트도 엔티티도 ORM 행도 담기지 않는다. | 트리 42·44행+D14 | `ast` | principle |  | **blocker** |
| 204 | 응용 DTO 백스톱의 검사 대상은 `application_layer/**/<use_case>_{command,query,result}.py` 전부다 — 코드 쪽 규칙(#67 «raise 하지 않는다»)과 겹치던 중복 문면을 검사 범위 규칙으로 갈랐다(3차 T9). | 트리 42·43·44행+D30 | `path` | both | `measured_ok` | **검사기** |
| 205 | DTO 는 자기 유스케이스 폴더 안에서만 쓰인다 — 유스케이스끼리 DTO 를 돌려쓰지 않는다. | D14 | `ast` | principle |  | **blocker** |
| 206 | 유스케이스가 받는 값의 파일 이름은 `<use_case>_command.py` 다. | 트리 42·43행+D8+D14 | `path` | principle |  | **blocker** |
| 207 | `<use_case>_command` 의 기본형은 id 와 원시값이고 도메인 값 객체는 그대로 온다 — 못 담는 것은 둘뿐이다: 애그리거트·ORM 로우, 그리고 «안쪽이 바깥을 알게 만드는» 타입(`UploadedFile` 처럼 장고·닌자가 자기에게 편한 모양으로 빚은 것). 뒤엣것은 이 칸이 아니라 전역 제약 ②가 막는다. | 트리 42행+D14 | `ast` | principle |  | **blocker** |
| 208 | `<use_case>_command` 은 바깥 `schema_in.py` 와 짝이지만 같은 타입을 쓰지 않는다. | 트리 42행+D8 | `ast` | principle |  | **blocker** |
| 209 | 유스케이스가 내보내는 자료의 파일 이름은 `<use_case>_result.py` 다. | 트리 44행+D8+D14 | `path` | principle |  | **blocker** |
| 210 | 컨트롤러가 `<use_case>_result` 만 보고 응답을 만들 수 있어야 한다 — 값이 빠져 컨트롤러가 도메인을 들여다보게 되면 위반이다. | 트리 44행 | `ast` | principle |  | **blocker** |
| 211 | 흐름을 내보내는 유스케이스는 `Iterator[<use_case>Out]` 로 돌려주고 흐르는 알맹이가 `<use_case>_result` 이어야 한다 — `<use_case>_result` 은 개수를 규정하지 않는다. | 트리 44행+D14 | `ast` | principle |  | **blocker** |
| 212 | `port/` 에는 선언만 온다 — 구현은 한 줄도 없다. | 트리 45행+파트 [application] | `ast` | principle |  | **blocker** |
| 213 | DB 조회 계약도 `port/` 아래에 둔다 — 포트의 판정은 «바깥에 행위자가 있나»가 아니라 **«이 층 밖인가»**이고, 우리 DB 도 이 층 밖이다. | 트리 45행+트리 51행+D2+D29+D37 | `path` | principle |  | **blocker** |
| 214 | 애그리거트 리포지토리 선언은 `port/` 가 아니라 `domain_layer/<aggregate>/` 에 둔다. | 트리 45행+D2 | `path` | principle |  | **blocker** |
| 215 | `port/` 아래는 능력 하나 = 폴더 하나다 — 포트를 파일 하나로 두지 않는다. | 트리 46행+D14+D33 | `path` | principle |  | **blocker** |
| 216 | `port/<capability>/` 안에 오는 것은 계약(`<capability>_port.py`) · 자료(`<data>_out.py`·`<data>_in.py`) · 실패(`exception.py`) 셋이다. | 트리 46행+D14+D33 | `path` | principle |  | **blocker** |
| 218 | `port/<capability>/<capability>_port.py` 의 파일 이름은 그 폴더 이름과 같다. | 트리 47행+D33 | `path` | principle |  | **blocker** |
| 219 | `port/<capability>/<capability>_port.py` 에는 추상 메서드만 가진 인터페이스 클래스 하나가 들어 있다. | 트리 47행 | `ast` | principle |  | **blocker** |
| 220 | `port/<capability>/<capability>_port.py` 의 클래스는 `<Capability>Port` 로 끝난다 — **`port/` 의 다른 두 자식은 각자의 접미사를 따른다**(`domain_bypass_query/` → #235 · `unit_of_work/` → #247). | 트리 47행+D33 | `ast` | principle | `principle` | **blocker** |
| 221 | 접미사 검사의 대상은 `<capability>/<capability>_port.py` 안의 클래스뿐이고 같은 폴더의 `exception.py`·`<data>_out.py`·`<data>_in.py` 는 대상이 아니다. | D33 | `path` | principle |  | **검사기** |
| 225 | 포트 폴더마다 `exception.py` 를 둔다 — 필수다. | 트리 48행+D14+D27 | `path` | principle |  | **blocker** |
| 227 | 포트가 주고받는 자료는 `<data>_out.py`·`<data>_in.py` 에 두고, 인자나 반환이 원시값·값 객체로 안 될 때만 만든다. **여기서 «값 객체»는 표준 타입(`Decimal`·`UUID`·`Path`)이나 «이 포트 어휘로 된 타입»이지 `domain_layer/` 의 것이 아니다**(#228). | 트리 49·50행+D33 | `ast+` | principle |  | **blocker** |
| 228 | `<data>_out.py`·`<data>_in.py` 에는 유스케이스 입출력 DTO 도 도메인 값 객체도 오지 않는다 — **여기서 «정의»하지 않고, `domain_layer/` 의 값 객체를 «그대로 실어 보내지»도 않는다**. 까닭은 **이 BC 의 업무 어휘가 포트 밖으로 새면 안 되기 때문**이다(이 자료는 주인이 «바깥»이다 — 트리 49행). **«값 객체라는 모양»을 쓰는 것은 금지가 아니다**(#227) — 금지되는 것은 **그 정의가 `domain_layer/` 에 있는 것**이고, 필요한 값은 «펴서» 싣는다. | 트리 49·50행+D14 | `ast` | principle |  | **blocker** |
| 229 | 도메인을 우회하는 조회의 «계약»은 `application_layer/port/domain_bypass_query/` 에 둔다. | 트리 51행+D29 | `path` | principle |  | **blocker** |
| 231 | 애그리거트가 한 번도 안 나오는 조회 계약은 `domain_layer` 에 두지 않는다. | 트리 51행+D29 | `ast` | principle |  | **blocker** |
| 232 | `domain_bypass_query/` 아래는 능력 하나 = 폴더 하나이고, 안은 `port/<capability>/` 와 같은 세 낱말 — 계약(`<capability>_query.py`) · 자료(`<data>_out.py`·`<data>_in.py`) · 실패(`exception.py`) 다. | 트리 52행+D29+D33 | `path` | principle |  | **blocker** |
| 233 | `domain_bypass_query/<capability>/` 이름은 «무엇을 알고 싶은가»로 짓고 누가 그걸 주는지는 이름에 넣지 않는다. | 트리 52행 | `ast+` | principle |  | **blocker** |
| 234 | `domain_bypass_query/<capability>/<capability>_query.py` 는 계약 하나 = 파일 하나이고 파일 이름은 폴더 이름과 같다. | 트리 53행+D33 | `ast` | principle |  | **blocker** |
| 235 | `domain_bypass_query/<capability>/<capability>_query.py` 의 클래스는 `<Capability>DomainBypassQuery` 로 끝나고, 구현은 같은 접미사에 접두사로 갈린다(`Django<Capability>DomainBypassQuery`). | 트리 53행+D33 | `ast` | principle |  | **blocker** |
| 236 | `domain_bypass_query/` 가 내보내는 자료는 «이름 붙인 정적 타입» 하나다 — 도메인 타입도 ORM 로우도 `QuerySet` 도 넘기지 않는다(트리 54·55행은 이것을 DTO 라 부르지 않는다 — `<use_case>_command`/`<use_case>_result` 은 유스케이스의 입출력 어휘다). | 트리 54행+D29 결정④+D8 | `ast` | principle |  | **blocker** |
| 238 | `domain_bypass_query/<capability>/exception.py` 를 둔다 — 필수다. | 트리 56행+D27+D29 | `path` | principle |  | **blocker** |
| 239 | `domain_bypass_query/` 의 예외는 도메인 예외를 상속하지 않는다. | 트리 56행+D27 | `ast` | principle |  | **blocker** |
| 240 | UnitOfWork 선언은 `port/unit_of_work/` 에 둔다 — «괄호»라 대화 계약(`<capability>/`)과 형제로 갈리지만, «바깥에 있어야 하는 것의 선언»이라 `port/` 아래 산다. | 트리 57행+D14+D37 | `path` | principle |  | **blocker** |
| 241 | 바깥에 «업무를 시키는» 것은 `port/<capability>/` 로, 내 저장들을 «묶는» 것은 `port/unit_of_work/` 로 간다. | 트리 57행+D14+D37 | `ast` | principle |  | **blocker** |
| 242 | `unit_of_work/` 에는 `exception.py` 를 두지 않는다. | 트리 57행+D14 | `path` | both | `measured_ok` | **blocker** |
| 244 | 저장 경계 하나 = 파일 하나이고 이름은 `<boundary>_unit_of_work.py` 다. | 트리 58행+D14 | `path` | principle |  | **blocker** |
| 245 | UnitOfWork 의 계약은 셋이다 — 열기 · 닫기 · `after_commit(callback)`. | 트리 58행+D14+D31 | `ast` | principle |  | **blocker** |
| 246 | `unit_of_work/` 의 클래스는 리포지토리를 노출하지 않는다 — 리포지토리 타입을 반환하는 멤버를 갖지 않는다. | 트리 58행+D14 «검사 한 줄» | `ast` | principle |  | **blocker** |
| 247 | UnitOfWork 클래스 이름은 `<Bc>UnitOfWork` 이고 구현은 같은 이름에 접두사로 갈린다(`Django<Bc>UnitOfWork`). | D33+D31 | `ast` | principle |  | **blocker** |
| 248 | UnitOfWork 개수를 「BC 당 하나」로 못 박지 않는다 — 원자성이 갈린 저장소가 둘이면 경계도 둘이다. | 트리 58행+D14 | `human` | principle |  | **면제** |
| 457 | 선언은 전부 `application_layer/port/` 아래에 산다 — 이 층이 「바깥에 있어야 하는 것」을 적는 자리가 여기 하나다. | D37+트리 45행 | `path` | principle |  | **blocker** |

## domain — 56개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 249 | `domain_layer/` 의 자식은 애그리거트 폴더들과 `shared_value_object/` · `domain_service/` 뿐이다. | 트리 59행+D12+D13 | `path` | principle |  | **blocker** |
| 251 | `domain_layer` 로 들어오는 import 는 `application_layer`·`driven_layer`·`composition_root` 뿐이고 `driving_layer` 는 금지다 — 단 driving 잎이 `exception`·값 객체(`shared_value_object/` 포함)를 «자료로» import 하는 것(#95·#141)은 예외다. | D13 결정③ | `ast` | principle |  | **blocker** |
| 252 | `domain_layer/` 의 1차 폴더는 클래스 종류가 아니라 `<aggregate>/` 이고 `entity/`·`value_object/` 는 그 안으로 내린다. | 트리 60행+D12 | `path` | principle |  | **blocker** |
| 253 | `domain_layer/<A>/**` 는 `domain_layer/<B>/` 의 루트 모듈만 import 한다(대상은 애그리거트 구성원이고 `domain_service/` 는 해당 없다). | 트리 60행+D12+D13 검사① | `ast` | principle |  | **blocker** |
| 254 | 애그리거트 폴더는 «항상 함께 옳아야 하는 것» 한 묶음이어야 한다 — 폴더를 하나 더 만드는 것은 «이만큼은 따로 저장돼도 된다»는 선언이고 트랜잭션·저장·잠금·바깥 참조가 전부 그 단위로 움직인다. **[Q4]** | 트리 60행 | `human` | principle |  | **blocker** |
| 256 | 애그리거트 폴더에는 애그리거트 루트 클래스 하나가 폴더와 같은 이름의 `<aggregate>.py` 파일로 온다. | 트리 61행 | `ast` | principle |  | **blocker** |
| 257 | 애그리거트의 상태를 바꾸는 메서드는 전부 루트를 지나고, 각 메서드는 끝에서 자기 불변식이 여전히 참인지 확인한다. | 트리 61행 | `ast+` | principle |  | **blocker** |
| 258 | 애그리거트 바깥에서 붙잡을 수 있는 것은 루트 클래스뿐이고 `entity/` 안의 것은 직접 참조하지 못한다 — 언제나 루트를 거쳐 닿는다. | 트리 61행+47행+D13 검사① | `ast` | principle |  | **blocker** |
| 259 | `<aggregate>/entity/` 에는 루트가 아닌 엔티티만 오고, 판정은 «식별자를 갖고 안의 값이 바뀌어도 같은 것으로 취급되는가» 하나다. | 트리 62행+D12 | `ast+` | principle |  | **blocker** |
| 260 | `entity/` 안의 클래스는 식별자를 가진다. | D12 | `ast` | principle |  | **blocker** |
| 261 | 엔티티 하나 = 파일 하나다. | 트리 63행 | `ast` | principle |  | **blocker** |
| 262 | 엔티티 파일에 `_entity` 접미사를 붙이지 않는다. | 트리 63행 | `path` | both | `measured_ok` | **blocker** |
| 263 | 같은 BC 안에 이름이 같은 ORM 모델이 있으면 그쪽만 `_model` 을 달아 구분한다. | 트리 63행 | `path` | principle |  | **blocker** |
| 264 | `<aggregate>/value_object/` 안의 클래스는 불변이다 — 검사는 관례로 한다: `__init__` 밖에서 자기 속성 대입(`self.x = …`)이 없어야 한다. | 트리 64행+D12 | `ast` | principle |  | **blocker** |
| 265 | `<aggregate>/value_object/` 의 값 객체는 그 애그리거트 밖에서는 쓰이지 않는다. | 트리 64행+D12 | `ast` | principle |  | **blocker** |
| 266 | 다른 애그리거트가 그 값 객체를 쓰기 시작하는 순간 `shared_value_object/` 로 올린다. | 트리 64행+D12 | `ast` | principle |  | **blocker** |
| 267 | 값 객체 하나 = 파일 하나다(애그리거트 안이든 `shared_value_object/` 든 같은 규칙이고 다른 것은 사는 폴더뿐이다). | 트리 65행+56행 | `ast` | principle |  | **blocker** |
| 268 | 값 객체는 만들어지는 시점에 스스로 검증해 잘못된 값으로는 존재할 수 없어야 한다. | 트리 65행 | `ast+` | principle |  | **blocker** |
| 269 | `<aggregate>/event/` 에는 이 BC 안에서 읽히는 «일어난 사실»만 온다. | 트리 66행+D13 | `ast` | principle |  | **blocker** |
| 270 | 이 BC 안에서 읽는 사람이 없으면 그것은 이벤트가 아니라 «알림»이고 자리는 `application_layer/port/` 다. | 트리 66행+D13+D34 | `ast` | principle |  | **blocker** |
| 271 | 이벤트는 명령이 아니라 과거형 사실로 짓는다 — `ReduceInventory` 가 아니라 `OrderPlaced` 다. | D13 | `ast+` | principle |  | **blocker** |
| 272 | 애그리거트 루트는 이벤트를 기록만 하고(리스트에 append) 아무도 부르지 않는다 — 메시지 버스를 모르고 I/O 를 하지 않는다. | 트리 59행+51행+D13 | `ast` | principle |  | **blocker** |
| 275 | 과거형 사실 하나 = 파일 하나다. | 트리 67행 | `ast` | principle |  | **blocker** |
| 276 | 이벤트 클래스는 필드만 있는 자료구조이고 메서드가 없다. | 트리 67행 | `ast` | principle |  | **blocker** |
| 279 | 도메인 이벤트 핸들러는 도메인이 아니라 `application_layer` 의 또 하나의 유스케이스다. | D13 | `ast` | principle |  | **blocker** |
| 280 | 핸들러는 이벤트를 애그리거트 어휘로 번역해 부른다 — `inventory.reduce(sku, qty)` 이지 `inventory.apply(event)` 가 아니다. | D13 | `ast` | principle |  | **blocker** |
| 282 | 리포지토리 선언은 애그리거트당 하나라서 폴더가 아니라 `<aggregate>_repository.py` 파일이다. | 트리 68행+D12+D32 | `path` | principle |  | **blocker** |
| 283 | `<aggregate>_repository.py` 는 추상 메서드만 갖는다(구현이 아니라 계약이다). | 트리 68행 | `ast` | principle |  | **blocker** |
| 285 | 애그리거트 컬렉션을 세고 합친 요약값(`exists() -> bool` · `count() -> int`)은 반환형이 원시 타입이어도 리포지토리에 남는다. | 트리 68행+D29 | `ast+` | principle |  | **blocker** |
| 287 | 리포지토리는 애그리거트를 주고받는다(`get(id) -> Aggregate` · `save(aggregate)`) — **쓰기 인자는 «애그리거트(또는 그 목록)»이고 «조건·필드»면 위반이다**(`bulk_update(filter, fields)`·`update(id, status=…)`). 필드 단위 갱신 메서드(`update_status(id, status)`)를 두지 않는다 — **판정이 SQL 로 가면 같은 판정의 도메인 메서드가 죽은 코드가 된다.** | D12+트리 68행+D43+T37 | `ast` | principle |  | **blocker** |
| 288 | `<aggregate>_repository.py` 는 `domain_layer` 안에서 아무도 import 하지 않는다 — 부르는 것은 `application_layer`·`driven_layer`·`composition_root` 뿐이다. | D13 검사④ | `ast` | principle |  | **blocker** |
| 289 | 애그리거트 불변식이 깨졌을 때 던지는 예외는 `domain_layer/<aggregate>/exception/` **폴더** 아래 «깨진 불변식 하나 = 파일 하나»로 둔다 — 파일이 아니라 폴더다. | 트리 69·70행+D27 ①+D40+D12 | `path` | principle |  | **blocker** |
| 290 | `exception/` 는 «처음부터» 폴더다 — 「커져서 감당이 안 되면 그때」 같은 조건은 두지 않는다(기계로 못 재는 조건이라 D10 에 걸린다). | 트리 69행+D27+D40 | `path` | principle | `measured_ok` | **blocker** |
| 291 | BC 바로 밑 `domain_layer/exception.py` 를 두지 않는다 — 도메인 예외의 표준 자리는 애그리거트 밑 하나뿐이다. | D27 ① | `path` | principle |  | **blocker** |
| 292 | 예외의 자리는 셋으로 갈린다 — 업무 규칙을 어겼으면 `domain_layer/<aggregate>/exception/` · 남에게 공개하는 실패면 `open_host_service/…/contract/exception/` · 바깥 행위자가 죽었으면 `application_layer/port/<capability>/exception.py` 다. | D27 ① | `ast` | principle |  | **blocker** |
| 294 | «저장이 실패하는 방식»에는 넷째 예외 자리를 두지 않는다 — 업무 의미가 있으면 애그리거트 예외로, 재시도 판정이면 `framework/` 로 가고 그 밖은 선언하지 않는다. | D27 ① | `ast` | principle |  | **blocker** |
| 295 | 도메인 예외를 BC 밖으로 raw 로 전파하거나 재노출하지 않는다 — `__all__` 재노출도 금지다. | D27 ③ + 트리 30행 | `ast` | principle |  | **blocker** |
| 298 | `domain_layer/shared_value_object/` 는 같은 `shared_value_object/` 안과 `exception` 모듈 말고는 아무것도 import 하지 않는다 — `<aggregate>/value_object/`·애그리거트·리포지토리·포트·이벤트·프레임워크는 전부 금지다. | 트리 71행+D12 검사② | `ast` | both | `measured_ok` | **blocker** |
| 299 | 주인이 하나가 아닌 것은 업무 이름이 아니라 종류 이름으로 폴더를 짓는다(`shared_value_object/`·`domain_service/`) — 그 밖의 1차 폴더는 도메인 이름만 쓴다. | 트리 71행+D12+D13 | `path` | principle |  | **blocker** |
| 300 | 도메인 서비스는 BC 레벨 `domain_layer/domain_service/` 한 칸에만 살고 `<aggregate>/domain_service/` 를 두지 않는다. | 트리 73행+D28 ②(08-07 R10) | `path` | both | `measured_ok` | **blocker** |
| 301 | `domain_service/` 에는 루트 메서드로 표현할 수 없는 규칙만 온다 — 루트 메서드가 될 수 있으면 애그리거트로 가고, 못 하는 이유는 셋 중 하나다(애그리거트를 아예 안 받거나 · «없을 때»를 판정하거나 · 둘 이상을 한꺼번에 보거나). | 트리 73행+D13+D28 | `ast+` | principle | `principle` | **blocker** |
| 302 | 도메인 서비스는 무상태다. | 트리 73행+D13(Evans 3조건) | `ast` | principle |  | **blocker** |
| 303 | `domain_service/` 는 애그리거트 루트 · `value_object` · `exception` · 같은 폴더의 다른 도메인 서비스만 import 한다 — 내부 엔티티도 리포지토리 선언도 포트도 안 된다. | 트리 73행+D13 검사③ | `ast` | both | `measured_ok` | **blocker** |
| 304 | 도메인 서비스는 애그리거트를 인자로 받고 불러오거나 저장하지 않는다 — 불러오거나 저장하면 그건 유스케이스다. «불러오지 않는다»는 원전보다 좁힌 우리 확장이다 — Vernon 의 리포지토리 쓰는 도메인 서비스 실례는 이 트리에선 유스케이스로 간다(3차 T24). | 트리 73행+58행+D13 | `ast` | principle |  | **blocker** |
| 305 | 재료는 유스케이스가 모아 값으로 넘긴다 — 도메인은 협력이 필요해도 포트를 파라미터로 받아 부르지 않고 뽑힌 값을 받는다. | 트리 73행+D32 | `ast` | principle |  | **blocker** |
| 307 | 도메인 서비스 시그니처에는 원시 타입이 아니라 값 객체가 온다(`amount: Money`) — 인자를 `Decimal` 로 쓰면 그건 도메인 서비스가 아니라 계산 함수다. | 트리 74행+D13 | `ast` | principle |  | **blocker** |
| 308 | 도메인 서비스가 규칙 위반을 알리는 방법은 도메인 예외를 던지는 것이다. | 트리 74행 | `ast` | principle |  | **blocker** |
| 309 | 폴더 이름을 `service/` 로 줄이지 않고 `domain_service/` 를 그대로 쓴다. | D13 | `path` | principle |  | **blocker** |
| 310 | 무상태 규칙 하나 = 파일 하나다. | 트리 74행 | `ast` | principle |  | **blocker** |
| 311 | 도메인 서비스 파일 이름은 접미사를 붙이지 않고 «행위»로 짓되 주어가 되는 애그리거트 어휘를 담는다(`lesson_slot_policy.py`), 겹치면 행위로 짓는다(`settle_turn.py`). | 트리 74행+D28 ② | `ast+` | both | `measured_ok` | **blocker** |
| 312 | 업무가 종류별로 갈려서 만든 판정 인터페이스는 선언과 구현을 같은 `domain_layer/domain_service/` 에 두고, 바깥을 갈아끼우려는 인터페이스만 `application_layer/port/` 선언 + `driven_layer/` 구현으로 층이 갈린다 — 판정은 «구현이 `domain_layer` 밖을 import 하나» 다. | D32 결정① | `ast` | principle |  | **blocker** |
| 313 | `domain_layer/<aggregate>/port/` 를 두지 않는다 — 붙는 포트(리포지토리)는 `<aggregate>_repository.py` 로 자리가 났고 안 붙는 포트(시계·게이트웨이·알림)는 도메인 것이 아니다. | D13 ①+D32 | `path` | principle |  | **blocker** |
| 314 | `domain_layer/` 에 `specification/` 폴더를 두지 않는다. | D13 ① | `path` | principle |  | **blocker** |
| 315 | 복잡한 애그리거트 조립(Factory)은 그 애그리거트 폴더 안에 둔다. | D12 | `path` | principle |  | **blocker** |
| 316 | 재료를 한 번에 못 모으는 경우(판정 결과에 따라 다음 조회가 달라질 때)에도 규칙을 풀지 않고 판정을 두 조각으로 쪼갠다 — 도메인 판정 → 응용 조회 → 도메인 판정. **[Q2]** | D32 | `human` | principle |  | **blocker** |
| 459 | `shared_value_object/<value_object>.py` 는 애그리거트 안의 값 객체와 파일 규칙이 똑같고 다른 것은 사는 폴더뿐이다. | 트리 72행+D13 | `path` | principle |  | **blocker** |

## driven — 62개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 318 | `driven_layer/` 의 자식 폴더는 `django_<bounded_context>/` 와 `adapter/` **둘뿐**이다 — 앞은 장고가 자리를 강제한 것이고 뒤는 `port/` 의 약속을 지키는 것이다. | 트리 75행+D15+D37 | `path` | principle |  | **blocker** |
| 319 | `adapter/` 네 갈래는 이렇게 갈린다 — 우리 DB 면 `persistence/` · 우리가 만든 다른 BC 면 `anticorruption_layer/` · **계약이 저장소 밖이고 네트워크 너머라 런타임에 터지면** `external_system/`(우리가 운영하는 Redis·Kafka 도 여기다) · 그 밖이면 `<capability>/`. | 트리 89행+D17+D18+D37 | `ast` | principle |  | **blocker** |
| 322 | `driven_layer` 로 들어오는 화살표는 `composition_root` 뿐이다 — `application_layer`·`domain_layer`·`driving_layer` 는 `driven_layer` 를 import 하지 않는다. | D20+D5 | `ast` | principle |  | **blocker** |
| 323 | 전역 제약 ②(안쪽은 구체 기술을 모른다)는 `driven_layer` 에 걸지 않는다 — 이 칸은 django·ORM·HTTP·벤더 SDK·브로커를 전부 알아도 된다. | D20 결정④ | `path` | principle |  | **면제** |
| 324 | 이 칸의 이름은 `driven_layer/` 다 — `infra_layer/`·`infrastructure_layer/`·`driven_adapter/`·`secondary_adapter/` 를 쓰지 않는다. | 트리 75행+D16 | `path` | principle |  | **blocker** |
| 325 | ORM 모델·마이그레이션·어드민이 사는 폴더는 `driven_layer/django_<bounded_context>/` 이고 그 자체가 장고 앱이다 — 폴더 이름은 `django_` + BC 이름이다. | 트리 76행+D15 | `path` | principle | `principle` | **blocker** |
| 326 | `django_<bounded_context>/` 는 django 와 같은 폴더 안 말고 아무것도 import 하지 않는다 — `domain_layer` 도 금지다(잎). **예외(2026-08-12 D1′)**: 자기 BC domain VO(`value_object/`·`shared_value_object/`)의 **값 파생 전용** from-import 는 허용한다 — 나열·순회·멤버 참조까지이고, 호출(판정·행위)은 위반이다(`implementation-django` 「값 집합은 domain StrEnum 에서 파생」 요구와 정렬). | 트리 76행+D15 검사①+D20 검사② | `ast` | principle |  | **blocker** |
| 327 | `django_<bounded_context>/admin/**` 는 driven_layer 화살표 검사와 잎 import 검사의 대상에서 뺀다. | D15 검사①+D20 검사①②+D21 | `path` | measured | `measured_ok` | **검사기** |
| 328 | `django_<bounded_context>/` 를 import 하는 것은 `driven_layer/adapter/persistence/` 아래뿐이다. | D15 검사③+D20 검사③+D37 | `ast` | principle |  | **blocker** |
| 329 | `apps.py` 의 AppConfig 는 `label` 을 명시 선언한다 — 기본값에 기대지 않는다. | 트리 77행+D15 검사④ | `ast` | principle |  | **blocker** |
| 330 | `label` 값은 BC 이름과 같고, 폴더 이름은 그 값에 `django_` 를 붙인 것이다. | 트리 77행+D15 검사④ | `ast` | both | `measured_ok` | **blocker** |
| 331 | BC 이름은 설치된 다른 앱의 `label` 과 겹치지 않는다 — 목록은 고정 나열이 아니라 «그 저장소에 설치된 앱 전부»다(`admin`·`auth`·`sessions` …). | 트리 77행+D15 | `ast` | principle |  | **blocker** |
| 332 | `apps.py` 의 `name` 은 전체 점 경로로 적는다. | 트리 77행 | `ast` | principle |  | **blocker** |
| 334 | `models` 는 파일이 아니라 패키지(폴더)다. | 트리 78행 | `path` | both | `measured_ok` | **blocker** |
| 335 | ORM 모델은 표 하나 = 파일 하나로 `models/<entity>_model.py` 에 두고 `_model` 접미사가 필수다. | 트리 79행+D21 | `ast` | principle |  | **blocker** |
| 336 | 마이그레이션은 `django_<bounded_context>/migrations/` 에 산다 — 중앙 마이그레이션 폴더를 두지 않는다. | 트리 80행+D15 | `path` | principle |  | **blocker** |
| 337 | 마이그레이션 파일 이름은 사람이 정하지 않는다 — django 가 매긴 번호(`0001_initial.py` 꼴)를 그대로 쓴다. | 트리 81행 | `path` | principle |  | **blocker** |
| 338 | 마이그레이션 파일 안에서 도메인 모듈을 import 하지 않는다. | 트리 81행 | `ast` | principle |  | **blocker** |
| 339 | 어드민은 규정 밖 구역이다 — 자리(`django_<bounded_context>/admin/` · `django_<bounded_context>/templates/admin/<bounded_context>/`)와 이름만 규정하고 화살표·앎의 범위는 규정하지 않는다. | 트리 82행+D21 | `path` | measured | `measured_ok` | **면제** |
| 340 | `admin/` 아래는 모델 하나 = 폴더 하나(`admin/<entity>/`)다. | 트리 83행+D21 | `path` | both | `measured_ok` | **blocker** |
| 341 | `admin/<entity>/` 안의 파일에는 `_admin` 접미사를 붙이지 않는다 — 폴더가 «누구»를 말하니 파일은 «무엇»만 말한다. | 트리 83행+D21 | `path` | principle |  | **blocker** |
| 342 | ModelAdmin 클래스는 `admin/<entity>/panel.py` 에 하나 두고, 이 파일은 등록·목록 컬럼·검색·권한·django 훅만 담는다. | 트리 84행+D21 | `ast` | both | `measured_ok` | **blocker** |
| 343 | django 훅(`get_urls()`·`save_model`)은 `panel.py` 에 남기고 그 몸통은 `feature/` 로 내린다. | D21 | `ast+` | principle |  | **blocker** |
| 344 | 어드민 폼은 폼 하나 = 파일 하나로 `admin/<entity>/form/<form>_form.py` 에 둔다 — `form` 은 파일이 아니라 폴더다. | 트리 85행+D21 | `ast` | principle |  | **blocker** |
| 345 | 운영 기능 하나 = 파일 하나로 `admin/<entity>/feature/<feature>.py` 에 둔다. | 트리 86행+D21 | `ast` | measured | `measured_ok` | **blocker** |
| 346 | `admin/<entity>/feature/` 안은 유스케이스 형태(클래스 + Request DTO + Result DTO)를 지키지 않아도 된다 — 함수 하나로 짜도 된다. | 트리 86행+D21 | `human` | principle |  | **면제** |
| 347 | 사용자 API 와 공유하는 유스케이스는 `application_layer` 에 남기고 `feature/` 에는 화면만 둔다. | D21 | `ast+` | principle |  | **blocker** |
| 348 | 어드민 템플릿은 `django_<bounded_context>/templates/admin/<bounded_context>/<page>.html` 에 두고, 그 셋째 마디는 폴더 이름(`django_…`)이 아니라 `apps.py` 의 `label` 이고, **덮어쓰기 경로의 모델 마디는 모델 클래스명을 전부 소문자로 붙인 것(밑줄 없음)이다**. | 트리 87행+D21 | `ast` | principle |  | **blocker** |
| 349 | `repository/` 는 `django_<bounded_context>/` 안이 아니라 그 형제로 둔다 — 구현이 애그리거트와 ORM 모델을 동시에 import 해야 한다. | 트리 91행+D15 결정③ | `path` | principle |  | **blocker** |
| 350 | 드리븐에 `read_model/` 같은 폴더를 따로 만들지 않는다 — Thin Read 구현은 `adapter/persistence/domain_bypass_query/` 에 산다. | 트리 93·94행+D29 | `path` | measured | `measured_ok` | **blocker** |
| 351 | `domain_layer/<A>/<A>_repository.py` 선언마다 `driven_layer/adapter/persistence/repository/<A>_repository.py` 구현이 정확히 하나 있다. | 트리 92행+D15 검사② | `path` | principle |  | **blocker** |
| 352 | 리포지토리 구현은 폴더가 아니라 파일이다 — 애그리거트당 하나다. | 트리 92행+D15 | `path` | principle |  | **blocker** |
| 353 | `adapter/` 아래 모든 `.py` 는 «어떤 선언의 구현»이고 그 선언을 **경로**가 가리킨다 — 이름이 선언과 «같은» 것은 `persistence/` 쪽뿐이고(`repository/<aggregate>_repository.py` · `domain_bypass_query/<capability>_query.py` · `unit_of_work/<boundary>_unit_of_work.py`), `<capability>/` 아래는 «폴더가 선언을, 파일이 어느 기술인가»를 말한다(`<technology>_adapter.py`). | 트리 89행+D37+D57 | `path` | principle |  | **blocker** |
| 354 | 리포지토리 구현 클래스 이름은 `Django<Aggregate>Repository` 다 — `Repository`·`UnitOfWork`·`DomainBypassQuery` 는 구현에도 참인 역할 이름이라 선언과 공유하고 기술 접두사가 가른다. | 트리 92행+D33 | `ast` | principle |  | **blocker** |
| 355 | 조회가 `<aggregate>_repository.py` 에 남나 `port/domain_bypass_query/`+`persistence/domain_bypass_query/<capability>_query.py` 로 나가나는 «그 메서드의 주어가 그 애그리거트인가, 화면인가»로 가른다 — 그 애그리거트 얘기면 반환형이 `bool`·`int` 라도(개수·요약 포함) 남고, 화면 때문에 여러 애그리거트를 가로질러 표를 만드는 것만 나간다. | 트리 68·94행+D29 | `ast+` | principle |  | **blocker** |
| 356 | `driven_layer/adapter/persistence/domain_bypass_query/<capability>_query.py`(Thin Read Layer)는 `domain_layer` 를 import 하지 않는다. | 트리 94행+D29 결정③ | `ast` | principle |  | **blocker** |
| 357 | 그 `domain_layer` 미의존 검사는 `domain_bypass_query/` 아래에만 걸고 형제 폴더 `repository/` 아래에는 걸지 않는다 — 둘은 이제 같은 폴더가 아니라 형제 폴더다. | D29 결정③+D37 | `path` | principle |  | **검사기** |
| 358 | Thin Read 구현이 바깥으로 내보내는 것은 «이름 붙인 정적 타입»뿐이다 — ORM 로우도 `QuerySet` 도 응용에 넘기지 않는다. | D29 결정④ | `ast` | principle |  | **blocker** |
| 359 | Thin Read 구현 클래스 이름은 `Django<Capability>DomainBypassQuery` 다. | 트리 94행+D33 | `ast` | principle |  | **blocker** |
| 361 | `anticorruption_layer/` 아래는 상대 BC 하나 = 폴더 하나(`<bounded_context>/`)다. | 트리 97·98행+D17 | `path` | principle |  | **blocker** |
| 362 | `anticorruption_layer/<bounded_context>/` 아래의 구조는 규정하지 않는다. | 트리 98행+D17 | `path` | principle |  | **면제** |
| 363 | ACL 어댑터 클래스 이름은 `<Bc><Capability>Adapter` 다. | 트리 99행+D33 | `ast` | both | `measured_ok` | **blocker** |
| 364 | 어댑터는 «누구»(폴더 = 상대 BC·상대 시스템)로, 포트는 «필요»(파일 = capability)로 이름 붙는다 — 포트 파일 이름에 공급자 BC 이름을 넣지 않는다. | 트리 99행+D17 | `path` | principle |  | **blocker** |
| 365 | 우리가 못 고치고 계약이 저장소 밖에 있는 상대는 `external_system/` 아래 두고 `anticorruption_layer/` 에 넣지 않는다. | 트리 100행+D18 | `path` | principle |  | **blocker** |
| 366 | `external_system/` 판정선은 «남의 회사냐»가 아니라 «계약이 저장소 밖이고 네트워크 너머라 런타임에 터지나»다 — 우리가 운영하는 Redis 같은 인프라도 여기다. | D18 | `ast` | principle |  | **blocker** |
| 367 | `driven_layer/**` 안에서 **프로세스 밖으로 소켓을 여는 라이브러리**를 import 하는 것은 `external_system/<system>/<capability>_adapter.py` 안에서만 허용된다. **가르는 자는 「이 라이브러리가 소켓을 여나」 하나이고, 목록은 «예시»가 아니라 «저장소가 실제로 쓰는 의존성에 맞춰 유지하는 데이터»다** — `httpx`·`requests`·`boto3`·`openai`·`redis`·`kafka-python`·`pika`·`grpcio`·`smtplib` 처럼 **HTTP 만이 아니라 브로커·캐시·메일도 들어온다**. **이름을 나열해 «닫으면» 새 의존성이 들어올 때 검사가 조용히 통과한다** — 옛 문면이 목록을 셋(`httpx`·`boto3`·`openai`)으로 닫아 두어, **#319·#366 이 축자로 지목한 Redis·Kafka 를 이 검사가 못 잡고 있었다.** **`framework/` 는 이 규칙의 대상이 아니다**(주어가 `driven_layer/**` 다) — 그쪽 SDK 의 자리는 `framework/<technology>/`(#411·#415)와 `framework/<capability>/<technology>_adapter.py`(#405·#406·#408)다. <span>08-11 · ㉯ — 옛 문면이 「#400·#534 가 따로 연다」라 적었는데 **#400 은 배치 규칙이고 #534 는 파일 개수 규칙이라 둘 다 SDK 를 열지 않는다** — 인용이 처음부터 틀렸다.</span> | 트리 101·102행+D18+D20 | `ast` | principle |  | **blocker** |
| 368 | 타임아웃·재시도·회로차단·레이트리밋의 **«값»**(몇 초 · 몇 번 · 언제 열림)은 그 상대를 소유한 `external_system/<system>/` 어댑터가 정한다 — 그 **«기계»**(재시도 루프·백오프·차단기)는 `framework/` 가 주고(#556), 여기서 새로 구현하면 위반이다. **«다시 부르기»는 입구(`cron_job/`)의 몫이다.** | 트리 100행+D18+**D52** | `ast+` | principle |  | **blocker** |
| 369 | `external_system/` 아래는 벤더 하나 = 폴더 하나(`<system>/`)다. | 트리 101행+D18 | `path` | principle |  | **blocker** |
| 370 | 바깥 시스템 어댑터 클래스 이름은 `<System><Capability>Adapter` 다. | 트리 102행+D33 | `ast` | principle |  | **blocker** |
| 371 | 포트 구현 중 벤더도 타 BC 도 ORM 도 아니고 **네트워크 너머도 아닌** «나머지»(시계·난수·프로세스 내 락·스레드·파일시스템)는 `driven_layer/adapter/<capability>/<technology>_adapter.py` 에 둔다 — 네트워크 너머 락은 `external_system/` 이다(#366). | 트리 103·104행+D17+D18+D37 | `path` | principle |  | **blocker** |
| 372 | 그 «나머지»가 BC 안(`driven_layer/adapter/<capability>/<technology>_adapter.py`)이냐 `framework/<capability>/` 냐는 «계약의 이름에도 시그니처에도 어느 BC 의 업무 어휘가 한 글자라도 나오나»로 가른다 — 나오면 BC 안, 한 글자도 없으면 framework. | 트리 104행+D17+D24 | `ast` | both | `measured_ok` | **blocker** |
| 373 | 그 «나머지» 어댑터 클래스 이름은 `<기술><Capability>Adapter` 다. | 트리 104행+D33 | `ast` | principle |  | **blocker** |
| 374 | UnitOfWork 구현은 `driven_layer/adapter/persistence/unit_of_work/<boundary>_unit_of_work.py` 파일이고 경계 하나에 하나다. | 트리 96행+D14+D18 | `path` | principle |  | **blocker** |
| 375 | django 의 `connection`·`transaction` 을 아는 것은 `driven_layer`(UoW 구현·리포지토리 구현)까지다 — `application_layer` 는 `django.db` 를 import 하지 않는다. | 트리 96행+D31+D4 | `ast` | principle |  | **blocker** |
| 376 | 커밋 뒤 부작용은 UoW 의 `after_commit(callback)` 을 거치고, 그 구현은 `transaction.on_commit` 으로 채운다. | 트리 96행+D31 | `ast` | both | `measured_ok` | **blocker** |
| 382 | 클래스에 `Gateway` 접미사를 쓰지 않는다 — 계약이면 `Port`, 구현이면 `Adapter` 로 흡수한다. | D33 | `ast` | principle |  | **blocker** |
| 460 | 구현은 전부 `driven_layer/adapter/` 아래에 산다 — `django_<bounded_context>/` 만 그 밖이고, 그것은 «지키는 약속»이 없어서다. | D37+트리 89행 | `path` | principle |  | **blocker** |
| 462 | ORM 모델을 import 하는 것은 `adapter/persistence/` 아래 셋(`repository/`·`domain_bypass_query/`·`unit_of_work/`)뿐이다 — 이 공통 규칙 하나가 그 겹 폴더를 정당화한다. | D37+트리 90행 | `ast` | principle |  | **blocker** |
| 463 | `adapter/<capability>/` 인지의 판정은 3단이다 — ① 밖에 «상대»가 있나 → ② 없으면 «기술»이 필요한가 → ③ 계약에 업무 어휘가 있나. | D37+트리 103행 | `ast` | principle |  | **blocker** |
| 464 | `repository/` 를 `command`·`query` 로 가르지 않는다 — 가르는 축은 「도메인을 거쳤나」이고, 애그리거트 리포지토리도 `find_by_id`·`exists`·`count` 로 읽는다. | D37 기각+트리 91행 | `path` | principle |  | **blocker** |
| 465 | `domain_bypass_query/<capability>_query.py` 에 `_repository` 접미사를 붙이지 않는다 — 한 경로에 repository 가 두 번 나오고, 이 칸은 애그리거트를 안 거치므로 리포지토리가 아니다. 접미사는 `_query` 이고 선언·구현 양쪽이 함께 단다. | D37+D33+D41+트리 53·94행 | `path` | principle |  | **blocker** |
| 467 | `adapter_layer/` 를 층 이름으로 쓰지 않는다 — Cockburn 의 육각형에는 «층» 축 자체가 없고(어댑터는 층이 아니라 역할), Martin 의 Interface Adapters 는 입구까지 함께 담아 한쪽만 그렇게 부르면 거짓이 된다. | D37 기각+트리 75행 | `path` | principle |  | **blocker** |

## test — 9개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 383 | `test/` 는 계층이 아니라 «무엇을 켜고 도는가»로 나눈다 — 폴더 이름만 보고 이 테스트가 DB 를 켜는지 알 수 있어야 한다. | 트리 105행+파트 test | `path` | principle |  | **blocker** |
| 384 | `test/` 의 자식은 **다섯**이다 — `unit/`·`integration/`·`e2e/`(«테스트» — 안이 자유) · `factories/`·`fake/`(«테스트가 쓰는 재료» — 규칙이 그대로 산다). | 트리 105~111행+D56 | `path` | both | `measured_ok` | **blocker** |
| 385 | `application/<bounded_context>/test/` 에는 그 BC 의 테스트만 온다. | 트리 105행 | `path` | principle |  | **blocker** |
| 387 | `test/unit/` 은 DB 를 켜지 않는다 — 포트 자리에는 가짜 구현을 꽂는다. | 트리 106행+파트 test | `ast` | both | `measured_ok` | **blocker** |
| 388 | `test/unit/` 은 `factories/` 를 import 하지 않는다. | 트리 109행 | `ast` | principle | `principle` | **blocker** |
| 389 | `test/integration/` 은 진짜 DB 를 켜고 리포지토리와 HTTP 를 검사한다. | 트리 107행+파트 test | `ast` | both | `measured_ok` | **blocker** |
| 390 | `test/e2e/` 는 입구에서 출구까지 한 흐름을 통째로 본다 — **입구(TestClient·API·`<job>_cron_job`)를 안 거치면 위반**이다. <span>08-11 · ㉰ — 옛 문면의 「느린 대신 «수가 적어야» 한다」를 걷었다. 임계값이 없어 «정도»로 재는 문장이라 D10(「검사할 수 있는 데까지만 규정한다」)에 걸린다. 08-11 · Phase 0 린트 — 걷고 나니 술어가 «확정»만으로 서서 `ast+`→`ast`.</span> | 트리 108행 | `ast` | principle | `principle` | **blocker** |
| 391 | `factories/` 는 `integration/` 안이 아니라 그 형제로 둔다. | 트리 109행 | `path` | principle | `principle` | **blocker** |
| 392 | `factories/` 에는 `factory_boy` 픽스처만 온다. | 트리 109행+파트 test | `ast` | principle | `principle` | **blocker** |

## framework — 26개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 393 | `framework/` 는 저장소 루트에 두고 어느 BC 에도 속하지 않는다 — `application/<bc>/**` 아래에 `framework/` 가 있으면 위반이다. **«들어올지 말지»의 판정은 #448 이 진다**(「이 낱말의 뜻을 저장소 밖이 정하나」). <span>08-11 · ㉰ — 옛 문면의 「BC 가 하나도 없어도 이 파일이 존재하나」는 **C2 가 #448 로 갈아치운 옛 승격 자**다. 두 행이 같은 판정을 두 채널로 적고 있었다(D30).</span> | 트리 112행+D24+파트 framework | `path` | principle |  | **blocker** |
| 395 | `framework/` 의 자식은 **다섯**이다 — 고정 이름 셋(`broker/`·`test/`·`pure/`)과 `<capability>/`(계약 있음) · `<technology>/`(계약 없음). | 트리 112~132행+D24+D47+D59 | `path` | principle |  | **blocker** |
| 396 | 갈래 판정은 **4단**이고 사람이 필요 없다 — ① 고정 이름 셋이면 거기서 끝 ② 폴더 안에 `*_port.py` 가 있으면 `<capability>/` ③ 라이브러리 타입 없이 문장이 안 서면 `<technology>/` ④ 나머지는 `pure/`. | 트리 112행+D24+D41+D47 | `path` | principle |  | **blocker** |
| 398 | `framework/<capability>/` 는 «능력 하나 = 폴더 하나»다. | 트리 120행 | `path` | principle |  | **blocker** |
| 401 | `framework/<capability>/` 안에는 계약과 구현이 함께 산다 — 계약을 BC 에 두고 구현만 올리지 않는다. | 트리 120행+D24+파트 framework | `path` | principle |  | **blocker** |
| 402 | `framework/<capability>/` 의 계약 파일 이름은 폴더 이름과 같다(`clock/clock_port.py`). | 트리 121행+D24 | `path` | principle |  | **blocker** |
| 403 | `framework/<capability>/<capability>_port.py` 의 계약 클래스는 `<Capability>Port` 로 끝난다. | 트리 121행+D33 | `ast` | both | `measured_ok` | **blocker** |
| 404 | BC 의 유스케이스는 `framework/<capability>/` 에서 **계약 파일 · `exception.py` · `<data>_out.py` · `<data>_in.py`** 를 import 한다 — `<technology>_adapter.py` 만 `composition_root` 전용이다. | 트리 120~125행+D24+D47 | `ast` | principle |  | **blocker** |
| 405 | `framework/<capability>/` 안에서 폴더 이름과 «다른» `.py` 전부가 구현이다. | 트리 125행+D24 | `path` | principle |  | **blocker** |
| 406 | `framework/<capability>/<technology>_adapter.py` 는 `composition_root` 밖에서는 아무도 import 하지 않는다. | 트리 125행+D24 | `ast` | principle |  | **blocker** |
| 407 | 구현 파일 이름은 기술만 말한다(`clock/django_adapter.py`) — 폴더가 이미 능력을 말한다. | 트리 125행 | `path` | principle |  | **blocker** |
| 408 | `framework/<capability>/<technology>_adapter.py` 의 클래스는 `<기술><Capability>Adapter` 다(`DjangoClockAdapter`). | 트리 125행+D33 | `ast` | principle | `principle` | **blocker** |
| 411 | `framework/<technology>/` 는 «라이브러리 하나 = 폴더 하나»다(`django/` · `ninja/`). | 트리 126행 | `path` | principle |  | **blocker** |
| 412 | `framework/<technology>/` 안에는 폴더 이름과 같은 모듈을 두지 않는다(`django/django.py` 같은 것). | 트리 126행+D24 | `path` | principle |  | **blocker** |
| 413 | `framework/<technology>/` 는 그 기술을 아는 층만 부른다 — `domain_layer` 가 부르면 위반이다. | 트리 126행+D24 | `ast` | both | `measured_ok` | **blocker** |
| 414 | `framework/<technology>/` 아래는 `<module>.py` 파일이고, `response/` 같은 방향 축 하위 폴더를 두지 않는다. | 트리 127행+D24 | `path` | both | `measured_ok` | **blocker** |
| 415 | `framework/<technology>/<module>.py` 에는 «그 라이브러리의 타입 없이는 문장 자체가 성립하지 않는 코드»만 온다. | 트리 127행+D24 | `ast` | principle |  | **blocker** |
| 416 | 그 모듈은 어느 BC 에 놓아도 똑같이 동작해야 한다 — BC 를 다 지워도 그대로 남는다. | 트리 127행+파트 framework | `ast` | principle |  | **blocker** |
| 417 | 프레임워크가 내는 오류의 공통 응답 스키마는 `framework/ninja/framework_error_schema.py`·`framework_validation_error_schema.py` 에 둔다 — **`bc_` 접두를 쓰지 않는다**(#33·#426: framework 는 BC 를 모른다). BC 의 오류 언어는 `driving_layer/api/bc_error_schema.py` 로 따로 산다. | 트리 127행+D24+D27+D33 | `path` | principle |  | **blocker** |
| 420 | 인증은 «틀»(`BearerAuthentication(resolve)`)을 `framework/ninja/` 에 두고 토큰 «해석»은 각 BC 가 `open_host_service/` 로 공개한다 — BC 안에 인증 파일이 남지 않는다. 원리는 «틀/해석 분할»이고, Bearer 라는 방식·클래스명은 플러그인이 표준화한 채택 전제다(3차 T21). | D24 | `path` | measured | `measured_ok` | **blocker** |
| 423 | `framework/test/` 는 «공유 뼈대 하나 = 파일 하나»다. | 트리 131행 | `path` | principle |  | **blocker** |
| 425 | `framework/test/` 도 형제들과 «같은 자»를 받는다 — 이 재료의 뜻을 밖(HTTP·pytest·시간)이 정하면 여기, 우리 업무가 정하면(「로그인이 되는가」) 그 BC 의 `test/` 다. | 트리 130행+D24(08-10 · C2 개정) | `ast+` | principle |  | **blocker** |
| 426 | `framework/test/` 로 올라온 파일 안에는 특정 BC 이름이 나오지 않는다. | 트리 130행+D24 | `ast` | principle | `principle` | **blocker** |
| 428 | 뼈대 자신을 검사하는 테스트는 `framework/test/unit/` 에 두고 뼈대와 같은 폴더에 두지 않는다. | 트리 134행+D24 | `path` | principle |  | **blocker** |
| 470 | 강등은 매개변수를 더 받는 것이 아니라 **인라인해서 각 BC 로 돌려보내고 다시 뽑는** 것이다. | D38 결정② | `ast` | principle |  | **blocker** |
| 471 | `framework/<capability>/<technology>_adapter.py` 냐 `framework/<technology>/<module>.py` 냐는 「이 파일이 «어떤 계약의 구현»인가」로 가른다 — 예면 계약 폴더, 아니면 기술 폴더. | 트리 125·127행+D38 | `ast` | principle |  | **blocker** |

## project — 17개

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 429 | `<project>/` 에는 프레임워크가 «전역에 딱 하나»를 요구하는 것만 온다 — `api.py` · `urls.py` · `celery.py` · `settings/`. `celery.py` 항목은 D26 의 «celery 채택» 전제에 묶인 조건부다 — 전제가 무산되면 이 목록도 다시 선다(3차 T21). | 트리 135행+파트 project | `path` | principle |  | **blocker** |
| 430 | `<project>/` 는 `application/` 을 «등록»만 하고 «타입»으로 알지 않는다 — 문자열 경로는 등록이고 import 는 앎이다. | 트리 135행+D25 | `ast` | both | `measured_ok` | **blocker** |
| 431 | 부작용 등록(`# noqa: F401` import 등록)도 금지다 — 허용되는 것은 `urls.py` 의 `register_<bc>_api(api)` 명시 호출 하나뿐이다. | D25+D6 | `ast` | principle |  | **blocker** |
| 432 | `<project>/` 는 BC 가 늘어도 커지지 않는다 — 판정 물음은 「BC 하나를 통째로 지웠을 때 이 파일이 바뀌나」다. | 트리 135행+D25 | `ast` | both | `measured_ok` | **blocker** |
| 433 | `<project>/` 의 파일은 규칙을 «주소·예외 목록»으로 적지 않는다 — 목록으로 적으면 BC 가 하나 늘 때마다 이 파일이 바뀐다. | D25 | `ast` | measured | `measured_ok` | **blocker** |
| 434 | `<project>/` 에 `openapi_schema.py` 와 `response_policies.py` 를 두지 않는다 — 접힌 규칙 클래스는 `framework/ninja/` 로 간다. | D25 | `path` | measured | `measured_ok` | **blocker** |
| 435 | `<project>/` 에 `test/` 칸을 두지 않는다 — 전역 규칙의 테스트는 규칙을 따라 `framework/test/unit/` 으로 간다. | D25 | `path` | principle |  | **blocker** |
| 436 | `<project>/` 의 `health.py`·`home.py`·`asgi.py`·`wsgi.py` 는 표준 트리의 관할 밖이라 칸을 만들지 않는다. | D25 | `path` | principle |  | **면제** |
| 437 | `<project>/api.py` 에는 전역 API 객체 하나와 프레임워크 오류 핸들러만 온다 — **BC controller/registrar import · 도메인 예외 목록 · exception 매핑 · `ErrorSchema` 정의·생성은 전부 위반이다**(닫힌 허용 목록이라 열거 밖의 새 유형도 잡는다). | 트리 136행+D25+D27 | `ast` | principle |  | **blocker** |
| 440 | `<project>/urls.py` 는 라우터 «등록»만 한다 — 각 BC 의 `register_<bc>_api(api)` 를 명시적으로 부른다. | 트리 137행+D6+D25 | `ast` | both | `measured_ok` | **blocker** |
| 441 | `<project>/urls.py` 는 BC 안의 심볼을 import 해서 쓰지 않는다 — 예외는 #440 의 `register_<bc>_api` 명시 호출을 위한 그 함수 import 하나뿐이다(D25 «명시 호출 허용»). | 트리 137행+D25 | `ast` | both | `measured_ok` | **blocker** |
| 442 | `<project>/celery.py` 에는 Celery 인스턴스와 `autodiscover_tasks` 만 온다 — 경로 문자열만 쓰고 BC 안의 타입은 모른다. | 트리 138행+D25+D26 | `ast` | principle |  | **blocker** |
| 443 | `autodiscover_tasks` 는 `packages` 를 «콜러블»로 주고 `related_name=None` 으로 부른다 — 기본값으로는 `driving_layer/cron_job` 에 닿지 못한다. | 트리 138행+D26 | `ast` | principle |  | **blocker** |
| 444 | `packages` 는 «목록»이 아니라 «규칙»으로 짓는다 — 그 식에 BC 이름이 한 개도 나오지 않아야 한다. | 트리 138행+D26+D25 | `ast` | principle |  | **blocker** |
| 445 | `<project>/settings/` 에서 갈리는 축은 환경 하나뿐이다 — 기능별로 설정 파일을 쪼개지 않는다. | 트리 139행 | `path` | principle |  | **blocker** |
| 446 | `settings/` 는 «환경 하나 = 파일 하나»다 — `base` · `local` · `production` · `test`(규율 ④ 약어 금지 — `prod` 가 아니다). 넷은 예시다 — 트리 140행 `<environment>.py` 가 자리표시자라 목록은 닫지 않으며, 온전한 환경 이름(`staging` 등)은 허용하고 «약어»만 위반이다. <span>08-11 · T64 — 사용자 확정(열린 목록 유지).</span> | 트리 140행 | `path` | principle |  | **blocker** |
| 447 | 공통 설정은 `base` 에 두고 나머지 환경 파일은 그것을 가져와 덮어쓴다. | 트리 140행 | `ast` | principle |  | **blocker** |
## 3차 리뷰 반영 — 8개 (472~481)

카드·트리에 명문이 있는데 스펙이 빠뜨린 것(T10 셋 · T12 여섯)과 D9 의 이름 규칙(T6 하나)이다. 새 규칙이 아니라 **이미 정본에 있던 문장을 한 줄로 편 것**이다.

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 472 | `open_host_service/**/contract/` 의 계약 파일은 «표준 라이브러리»와 «같은 BC 의 다른 계약» 말고는 import 하지 않는다 — 이게 있어야 «계약 import 는 안전하다»가 참이 된다. | 트리 25행+D35 ㉮ | `ast` | principle |  | **blocker** |
| 473 | `anticorruption_layer/<other_bounded_context>/<capability>_adapter.py` 는 상대 창구의 «기저 예외»를 반드시 잡는다 — 구체 타입을 앞에 몇 개 잡든 자유, 마지막에 부모가 있어야 한다. 생산자 쪽 짝(#167)과 둘이 닫혀야 약속이 선다. | 트리 99행+D36 ㉰ | `ast` | principle |  | **blocker** |
| 474 | **바깥에 계약을 공개하는 입구 파일**(`<area>_controller.py` · `api/webhook/<provider>/<provider>_controller.py` · `open_host_service/**/<service>_service.py`)은 도메인 예외를 «타입»으로만 쓴다 — `except … as e` 로 묶은 이름을 그 파일 안에서 참조하면 위반이다. | 트리 12·18·24행+D39+D53 | `ast` | principle |  | **blocker** |
| 475 | `domain_bypass_query` 로 받은 자료는 도메인 규칙을 안 태운 «날것»이다 — 유스케이스가 그 값으로 업무 판정을 내리면 위반이다. | 트리 51행+D29+D37 | `ast+` | principle |  | **blocker** |
| 476 | `port/unit_of_work/` 의 선언 파일과 `adapter/persistence/unit_of_work/` 의 구현 파일은 1:1 이다 — 짝 없는 것이 한쪽에라도 있으면 위반, 검사는 폴더 목록 두 번이다. | 트리 95행+D37 | `path` | principle |  | **blocker** |
| 477 | `adapter/persistence/repository/` 아래 구현은 `domain_layer` 를 import 한다 — 하지 않으면 위반이다(번역자는 애그리거트와 ORM 모델을 동시에 알아야 한다). | 트리 91행+D29 결정③ | `ast` | principle |  | **blocker** |
| 480 | `port/<capability>/<data>_out.py·<data>_in.py` 와 `domain_bypass_query` 의 반출 타입을 DTO 라 부르지 않는다 — `<use_case>_command`/`<use_case>_result` 은 유스케이스의 입출력 어휘고, 여기는 «이름 붙인 정적 타입»이다. | 트리 54·55행+D29+D33 | `ast` | principle |  | **blocker** |
| 481 | 부모 폴더가 이미 말한 낱말을 **자식 «폴더»** 이름이 반복하면 위반이다(`request/request_contract/` ✗) — **파일**은 #30·#568 의 접두·접미 규칙이 지고 반복이 정상이다(`schema/schema_in.py` · `port/<capability>/<capability>_port.py`). | D9+D41 | `path` | principle |  | **blocker** |

## T26·T27 반영 — 4개 (482~485)

**08-08 대화에서 열린 D39 의 파생이다.** 물음은 「호출되는 쪽이 계약을 갖는 게 맞다면 `request/` 를 `command/` 로 바꿔야 하나」였고, 답은 **폴더는 그대로 두되 «의도»를 함수 이름이 지게 한다**였다. 정본을 먼저 고치고(트리 24행 · `NAMES` 14·17·19·28·34 · 트리 14행 note · `WHAT[13]` 예시 오류 · 2장 흐름 시그니처) 여기로 폈다.

**트리 변화 0** — 새 칸이 없고 리프 이름 규칙만 는다.

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 482 | `open_host_service/<service>/<service>_service.py` 의 공개 함수 이름은 `_command` 또는 `_query` 로 끝난다 — 상태를 바꾸면 커맨드, 안 바꾸면 질의다. 둘 중 무엇이냐는 사람 판정이지만 «접미사가 없다»는 위반이다. | 트리 24행+D39 결정① | `ast` | principle |  | **blocker** |
| 483 | 계약 파일 이름은 그 창구 함수 이름에서 접미사를 떼고 **종류 접미사를 단 것**이다 — `evict_child_command()` ↔ `contract/request/evict_child_request.py` · `list_children_query()` ↔ `contract/response/list_children_response.py`. | 트리 24·27·29행+D39+D41 | `path` | principle |  | **blocker** |
| 484 | 계약 클래스는 `<Operation>Request` / `<Operation>Response` 다 — `<Operation>Result` 로 짓지 않는다(`request` 의 짝은 `response` 이고 `result` 는 짝이 없는 «인과» 어휘라 방향 축이 깨진다 · 이 폴더는 「낼 수 있는 답 전부 — 거절도 답」이라 `Result` 는 정의를 좁힌다). | 트리 27·29행+D39+D41 | `ast` | principle |  | **blocker** |
| 485 | `port/<capability>/<capability>_port.py` 의 메서드 이름은 «의도»를 진다 — 시키면 명령형 동사구(`revoke_for_child()`), 물으면 묻는 꼴(`current_status()`·`has_shipped()`). `notify()`·`handle()`·`execute()` 처럼 무엇을 시키는지 안 말하는 이름은 위반이다. 창구와 달리 접미사는 붙이지 않는다(클래스가 이미 `<Capability>Port` 다). | 트리 47행+D39 결정③ | `ast+` | principle |  | **blocker** |

**«어겼을 때» 매트릭스 갱신** — 485 기준.

| 판정 | blocker | 검사기 | 이행 | 면제 | 계 |
|---|---|---|---|---|---|
| `path` | **141** | 10 | — | 4 | 155 |
| `ast` | **186** | 1 | — | 1 | 188 |
| `human` | **121** | 4 | 4 | 13 | 142 |
| **계** | **448** | 15 | 4 | 18 | **485** |

`path`+`ast` blocker **327** = 백스톱 몫 · `human` blocker **121** = discipline-reviewer 몫.

**같이 정한 것 — 어휘 충돌의 구분선.** `#28`(`<use_case>_use_case.py` 는 `_command`·`_query`·`_service`·`_app` 을 쓰지 않는다)과 `#482` 가 같은 낱말을 한쪽에서 금지하고 한쪽에서 강제한다. **파일 이름에는 «종류»가 오고 함수 이름에는 «의도»가 온다** — 자리가 다른 것이지 낱말이 뒤집힌 것이 아니다. 정본의 양쪽 «이름» 슬롯에 이 문장을 함께 박았다.

## D40~D59 회수 — 105개 (486~595)

**목록은 결정 카드가 39장일 때 뽑혔다.** 그 뒤에 선 스무 장(**D40~D59**)의 규칙이 **하나도 없었고**, 트리가 107행에서 138행으로 늘며 생긴 칸 **22개**가 규칙 0건이었다. 카드와 신설 칸을 다시 읽어 아래를 넣는다.

**맨 앞의 일곱(486~492)이 D54 = 제1원칙이다** — 이 검사가 «다른 모든 검사보다 먼저» 돌고, 걸리면 나머지를 돌리지 않고 반환한다.

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 486 | 어느 BC 를 열어도 이 트리의 골격이 «그대로» 있다 — 내용이 있든 없든 상관없다. 파일트리를 지키지 않는 구현·설계는 «반환»이다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
| 487 | 이 검사는 다른 모든 검사보다 «먼저» 돈다 — 걸리면 나머지 검사를 돌리지 않고 반환한다. | 트리 1행+D54 | `path` | principle |  | **검사기** |
| 488 | 고정 이름의 칸은 «부모가 있으면» 반드시 있다 — 폴더는 비어도 `__init__.py` 로, 파일도 비면 «빈 파일»로 만든다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
| 489 | `<…>` 가 붙은 자리표시자 칸만 그 개념이 실제로 생길 때 생긴다 — 그 외에 「이 BC 엔 없으니 뺀다」는 축소가 아니라 위반이다. | 트리 1행+D54 | `path` | principle |  | **blocker** |
| 490 | `application/<bounded_context>/**` 안에 트리에 없는 경로가 하나라도 있으면 위반이다(`utils/`·`common/`·`helpers/`). 폐쇄는 **칸**(폴더 + 트리가 이름을 준 파일)에만 걸리고, 트리가 리프로 닫은 폴더 «안»의 추가 모듈은 #15 의 재량이다. `framework/`·`<project>/` 는 이 원칙의 주어가 아니다(D54 축자: 「이 원칙의 주어는 «BC»다」). | 트리 1행+D54 | `path` | principle |  | **blocker** |
| 491 | 칸의 유형은 셋뿐이고 «조건부»는 없다 — ① 고정 이름 ② `<>` 첫 등장 ③ `<>` 재등장(조상이 이미 연 낱말이라 값이 이미 채워져 있어 ①과 같다). 「있을 수도 없을 수도」라고 적힌 칸은 셋 중 하나로 다시 분류한다. | 트리 1행+D54(T52) | `path` | principle |  | **blocker** |
| 492 | 「그 파일이 있어야 하나」는 트리가 정하고 「그것을 어떻게 쓰나」는 스킬이 정한다 — 트리에 조건을 적어 두 채널로 만들지 않는다. | D54+D10+D30 | `ast+` | principle |  | **blocker** |
| 493 | 모든 이름은 «첫 대입»에 타입을 적는다 — 시그니처·속성·지역 변수에 예외가 없다. 빠지는 것은 **문법이 없는 여덟 자리뿐**이다: `for x in xs:` · `with … as f:` · `except … as e:` · `a, b = pair` · `a = b = 0` · `x += 1` · walrus · 컴프리헨션. 그리고 **재대입**(첫 바인딩이 아니다)과 **선언적 클래스 본문**(ORM 모델 필드·ninja Schema 필드)은 면제다. | D58+§4 | `ast` | principle |  | **blocker** |
| 494 | 「자명하니까 면제」를 두지 않는다 — 조건을 하나라도 열면 「어디까지가 자명한가」가 되돌아와 규칙이 무너진다. **[Q0]** <span>08-11 — 「어겼을 때」를 `blocker` → `검사기` 로 옮겼다. **이 행의 주어는 «코드»가 아니라 «판정하는 사람»이라 반송할 파일을 지목할 수 없다**(Q0). 코드 쪽 귀결은 다른 행이 이미 `ast` 로 갖는다.</span> | D58 | `human` | principle |  | **검사기** |
| 495 | mypy strict 는 「구성돼 있으면」이 아니라 «항상» 돈다 — 이 게이트가 타입 규칙의 결정적 백스톱이고, 없으면 강제가 0이다. | D58+§4 | `ast` | principle |  | **검사기** |
| 496 | 타입 검사의 `tests.*` 면제를 두지 않는다 — `test/`·`fake/` 가 면제되면 페이크의 리스코프 위반이 그대로 통과한다. | D58+D56 | `ast` | principle |  | **검사기** |
| 497 | `composition_root/` 는 파일이 아니라 폴더이고 «결선 하나 = 파일 하나»다 — 지금은 `dependency_wiring.py` 와 `event_wiring.py` 둘이다. | 트리 2·3·4행+D40+D6 | `path` | principle |  | **blocker** |
| 498 | `event_wiring.py` 는 `event_router` 를 브로커에 «꽂는» 것만 한다 — 표를 여기서 만들지 않는다. | 트리 4행+D40 | `ast` | principle |  | **blocker** |
| 500 | 구독으로 넘기는 것은 «모듈 최상단에 정의된 이름 있는 함수»뿐이다 — 람다·`functools.partial`·지역 정의 함수를 넘기면 매번 «다른 객체»라 멱등이 성립하지 않는다. 검사는 브로커가 아니라 «넘기는 자리»에 선다. | 트리 4행+D59 | `ast` | principle |  | **blocker** |
| 501 | `event_wiring.py` 에서 DB 를 만지면 위반이다 — 모든 관리 명령에서 도는 자리다. | 트리 4행+D59 | `ast` | principle |  | **blocker** |
| 502 | `published_event/` 는 남의 BC 가 import 해도 되는 «유일한» 사실 표면이다 — 스키마 주인이 «보내는 쪽»이라 `open_host_service/contract/` 와 같은 폴더에 못 들어간다. | 트리 5행+D40+D34 | `path` | principle |  | **blocker** |
| 503 | `published_event/<event>.py` 에는 필드만 오고 도메인 타입이 0이다 — 도메인 타입이 실리면 남이 내 `domain_layer` 를 알게 된다. | 트리 6행+D40+D34 | `ast` | principle |  | **blocker** |
| 504 | 공표 사실은 «과거형 사실 하나 = 파일 하나»다. | 트리 6행+D40 | `ast` | principle |  | **blocker** |
| 505 | `domain_layer/<aggregate>/event/<event>.py` 는 «내부용»이라 BC 밖에서 import 하면 위반이다 — 밖으로 알릴 것은 유스케이스가 `published_event/` 로 «옮겨 담는다». | 트리 67행+D13+D40 | `ast` | principle |  | **blocker** |
| 506 | 발행 장치(레지스트리·dispatch·signal)는 `domain_layer/` 에 살지 않는다 — 배달은 `framework/broker/` 몫이다. | 트리 67행+D40 | `ast` | principle |  | **blocker** |
| 507 | `event_subscription/` 아래는 남의 `published_event/` 말고 어느 BC 도 import 하지 않는다. | 트리 35행+D40+D11 | `ast` | principle |  | **blocker** |
| 508 | `event_router.py` 는 「어느 사실 → 어느 핸들러」 «표»다 — `api_router.py` 와 같은 자리이고, 꽂는 것은 `event_wiring.py` 다. | 트리 36행+D40 | `ast` | principle |  | **blocker** |
| 509 | `<event>_subscription.py` 는 유스케이스 하나만 부른다 — `cron_job/` 의 껍데기와 같은 규칙이다. | 트리 37행+D40+D11 | `ast` | principle |  | **blocker** |
| 511 | `api/` 의 2차 축은 «계약을 누가 소유하나»다 — 우리 계약이면 `<area>/`, 바깥이 소유하면 `webhook/<provider>/` 다. **OAuth 콜백도 `webhook/<provider>/` 다** — 「우리 URL 을 바깥에 등록해 두고 그쪽이 부른다」가 이 칸의 정의 그대로이고, 파라미터도 프로바이더가 정한다. <span>08-11 · C8 — 「전송이 브라우저 리다이렉트라 다르다」·「RFC 표준이라 우리 것에 가깝다」는 **둘 다 기각**했다. 앞엣것은 D53 이 이미 폐기한 «행위자» 축이고, 뒤엣것은 프로바이더마다 파라미터가 달라 사실이 아니다.</span> | 트리 8·16행+D53 | `ast+` | principle |  | **blocker** |
| 512 | `webhook/<provider>/` 의 폴더 이름은 «보내는 쪽이 자기를 부르는 이름» 그대로다(`toss/`·`stripe/`) — `payment_gateway/` 처럼 역할로 지으면 둘째 결제사가 들어올 때 이름이 거짓말이 된다. | 트리 17행+D53 | `ast+` | principle |  | **blocker** |
| 514 | 웹훅 컨트롤러는 도메인 예외를 잡아 **「다시 보내지 마라」로 읽히는 응답**을 준다 — 업무 규칙 위반은 다시 받아도 영원히 같다. **무엇이 그 응답인지는 «발신자 스펙»이 정한다**(대개 2xx ack 이지만 리다이렉트인 상대도 있다) — 우리가 고르는 것은 «영구 실패를 다시 보내게 하지 않는다»는 **의도**까지다. <span>08-11 · C8 — 옛 문면의 「4xx 로 답하면 며칠 재시도한다」와 「`cron_job/` 과 같은 갈래다」를 걷었다. **후자는 틀렸다** — celery 는 우리 것이라 재시도를 우리가 설정하지만, 여기는 부르는 쪽이 바깥이라 **우리가 다시 부를 수단이 아예 없다**.</span> | 트리 16·18행+D53+D27 | `ast` | principle |  | **blocker** |
| 515 | `webhook/<provider>/schema/` 겹이 «온다» — 바깥이 보내는 모양과 **우리가 돌려주는 응답**이 각각 `schema_in.py`·`schema_out.py` 로 산다 — **돌려주는 것이 ack 라는 보장은 없다**(OAuth 콜백이면 «빈 몸통 + `Location`»이다). <span>08-11 · C8 — 옛 문면이 「ack」로 닫아 두어 리다이렉트로 답하는 상대가 이 칸에 못 들어왔다.</span> | 트리 19·20·21행+D53+D55 | `path` | principle |  | **blocker** |
| 516 | `webhook/` 에 오는 것은 HTTP 로 오는 것뿐이다 — 외부가 큐나 gRPC 로 보내면 그건 «다른 전송»이라 **`webhook/` 에 넣으면 위반**이다. **받을 칸은 정본 트리를 «개정»해야 생긴다**(#91) — BC 가 스스로 `driving_layer/` 의 형제를 늘리지 않는다(#90·#486). <span>08-11 · C6 — 옛 문면이 「`api/` 의 형제가 «는다»」로 끝나 **주어가 지워져 있었다**. 「정본 트리가 개정된다」는 뜻인데 「BC 가 늘린다」로 읽혀 **#90(「자식은 넷뿐」)과 정면으로 부딪혔다** — `driving_layer/websocket/` 하나를 #90·#486 은 blocker 로, 이 행은 «통과»로 판정하고 있었다.</span> | 트리 16행+D53 | `ast` | principle |  | **blocker** |
| 629 | **바깥이 부르는 입구는 «놓칠 수 있는» 입구다** — `webhook/<provider>/` 와 `event_subscription/` 둘 다, **그 입구가 «와야만» 일이 되는 설계는 위반이다**. 네트워크가 끊기거나 우리가 배포 중이면 그것은 영영 안 오고, **부르는 쪽이 바깥이라 우리가 다시 부를 수단이 없다**. 빠진 것은 `cron_job/` 이 시각에 깨어나 발신자·주인에게 «물어» 메운다(#626). 「빨리 알려 주는 길」이지 «유일한 길»이 아니다. <span>08-11 · C8 — `event_subscription/` 은 이 문장을 패널에 갖고 있었고 **`webhook/` 만 없었다**. 셋을 갈라 보면 `webhook/` 이 «우리가 손쓸 수단이 0»인 유일한 통로인데 규칙이 가장 없었다.</span> | 트리 16·33·35행+D53+D49 | `ast+` | principle |  | **blocker** |
| 517 | 서명 검증은 `framework/<technology>/` 의 인증 틀로 라우트 데코레이터에 선언한다 — 컨트롤러 본문에 검증 절차를 쓰지 않는다. | 트리 16·18행+D53+D24 | `ast` | principle |  | **blocker** |
| 518 | `framework/broker/` 아래에는 어느 BC 의 업무 어휘도 나오지 않는다. | 트리 113행+D59+D38 | `ast` | principle |  | **blocker** |
| 520 | 사실을 보내 놓고 그 결과를 «걱정하고» 있으면 위반이다 — Fowler 가 «passive-aggressive command» 라 부른 함정이고, 그건 사실이 아니라 «지시»였어야 한다. | 트리 113행+D59+D48 | `ast+` | principle |  | **blocker** |
| 521 | `broker/internal/` 은 바깥 미들웨어 «없이» 배달한다 — 네트워크도 저장도 별도 프로세스도 두지 않는다. | 트리 114행+D59 | `ast` | principle |  | **blocker** |
| 522 | `internal/` 의 한계는 계약이 말한다 — 같은 «프로세스» 안에서만 들린다. 워커가 여섯이면 브로커도 여섯이고 다른 프로세스에서 일어난 일은 영원히 안 들린다. | 트리 114행+D59+D49 | `human` | principle |  | **면제** |
| 523 | `internal_broker_port.py` 의 구독 등록은 «메모리에만» 한다 — 구독표가 「사실 이름 → 파이썬 함수」라 DB 에 담을 수 없다. 경로 문자열로 넣고 import 로 되살리면 D40 이 반려한 signals 보다 나쁘다. | 트리 115행+D59+D40 | `ast` | principle |  | **blocker** |
| 524 | 구독표는 «사실 → 리스너 집합»이라 같은 짝이 두 번 와도 하나다 — 리스트로 두면 `ready()` 가 두 번 돌 때 두 번 발화한다. 멱등은 부르는 쪽 예의가 아니라 «계약»이 진다. | 트리 115행+D59 | `ast` | principle |  | **blocker** |
| 525 | 발행은 리스너마다 하나씩 넘기고, 하나가 실패해도 나머지는 간다 — 대신 실패한 리스너를 «삼키면» 위반이다. | 트리 115행+D59+D49 | `ast` | principle |  | **blocker** |
| 526 | `internal` 통로에 「반드시 도달」을 기대는 코드가 붙으면 위반이다 — 보장은 «롤백되면 발행 안 됨» 한쪽뿐이고, 커밋됐다고 반드시 나가지는 않는다(at-most-once). **처방은 «누가» 못 견디나로 갈린다** — 보내는 쪽이면 애초에 «지시»였고(#520), 받는 쪽이면 #626 이 받는다. **[Q3]** | 트리 115행+D59+D49 | `human` | principle |  | **blocker** |
| 527 | `InternalBroker()` 를 `internal_broker.py` «밖»에서 만들면 위반이다 — 인스턴스는 이 파일 안에 하나로 두고 「한 번」은 파이썬 모듈 캐시가 보장한다. `composition_root/` 는 BC 마다 있어 거기서 만들면 BC 수만큼 생기고 «남의 사실»이 영원히 안 들린다. | 트리 116행+D59 | `ast` | principle |  | **blocker** |
| 528 | 구독표가 «인스턴스 속성»이 아니면 위반이다 — 모듈 레벨 «가변 전역»에 두면 걸린다. 인스턴스가 모듈에 «사는» 것과는 다르다. | 트리 116·119행+D59 | `ast` | principle |  | **blocker** |
| 529 | `broker/external/` 인지를 가르는 물음은 하나다 — 「듣는 쪽이 «다른 배포 단위»에 있나」. 「멀다」·「느슨하다」 같은 «정도»가 아니라 예/아니오다. | 트리 117행+D59 | `ast+` | principle |  | **blocker** |
| 530 | 내구성·백프레셔·재시도를 이유로 `external/` 을 열면 위반이다 — 셋 다 «워커»의 일이라 `cron_job/` 이 이미 받는다(D48 ②). 보존·재생은 관할 밖(Event Sourcing)이다. **[Q3]** | 트리 117행+D59+D48 | `human` | principle |  | **blocker** |
| 531 | `external_broker_port.py` 는 `internal_broker_port.py` 와 «다른 계약»이다 — 같은 계약의 다른 구현이 아니다. 보장이 달라서 약속이 갈린다. | 트리 118행+D59 | `ast` | principle |  | **blocker** |
| 532 | `external` 계약은 「반드시 도달」을 **요구로** 적고 «두 번 올 수 있다»를 함께 말한다(at-least-once) — 받는 쪽 멱등이 필수가 된다. **다만 그 도달 보장은 «미들웨어 설정»에 살아 트리가 확인할 수 없다** — Redis Pub/Sub 도 Celery 기본값도 at-most-once 다. 그러니 **받는 쪽은 「안 왔을 때」를 여전히 메워야 하고**(#629), 보장 자체는 `#603` 의 딸림 ⑷ 가 진다. <span>08-11 · C8 — 옛 문면의 「전제한다」가 «보장된다»로 읽혀 `external` 을 「놓칠 수 있는 입구」에서 빼는 근거로 쓰일 뻔했다. **설정에만 있는 것을 트리가 보장으로 읽으면 안 된다**(T45 가 ORM 캐시에서 만난 같은 모양).</span> | 트리 118행+D59+D49 | `ast+` | principle |  | **blocker** |
| 533 | `external` 계약은 «봉투»를 요구한다 — 두 번 온 것을 알아볼 식별자(CloudEvents 의 `source`+`id`) 없이는 멱등을 지킬 수단이 없다. | 트리 118행+D59 | `ast` | principle |  | **blocker** |
| 534 | `broker/internal/`·`broker/external/` 각 폴더의 `.py` 는 «계약 하나 · 구현 하나» 둘뿐이다 — 양방향으로 건다. | 트리 114·117·119행+D59+D37 | `path` | principle |  | **blocker** |
| 535 | `apps.py` 의 `ready()` 본문은 «한 줄»이다 — 자기 BC 의 `composition_root/event_wiring.py` 를 부른다. | 트리 77행+D59+D15 | `ast` | principle |  | **blocker** |
| 536 | 그 import 가 `ready()` «밖»에 있으면 위반이다 — 부팅 1단계에서는 모델을 못 읽는다. | 트리 77행+D59 | `ast` | principle |  | **blocker** |
| 537 | `ready()` 에서 DB 를 만지면 위반이다 — 원전 축자: *“`manage.py test` would still execute some queries against your **production** database”*. | 트리 77행+D59 | `ast` | principle |  | **blocker** |
| 538 | `apps.py` 의 모듈 최상단 import 는 django 것뿐이다 — 리스너를 여기서 «정의»하면 위반이고, 이 한 줄이 부모의 리프 규칙(django 말고 import 0)의 «유일한» 면제다. | 트리 77행+D59 | `ast` | principle |  | **blocker** |
| 539 | 사실 발행은 «세 걸음»이고 «순서»가 규칙이다 — ① **유스케이스가** 애그리거트에서 `pull_events()` 를 부른다 ② 저장 ③ 옮겨 담아 `uow.after_commit(…)` 으로 브로커에. **리포지토리 구현이 `pull_events()` 를 부르면 위반**이다(그것이 D59 가 근거 셋으로 기각한 «저장 경계 자동 수거»다). | 트리 41·92행+D59 | `ast` | principle |  | **blocker** |
| 540 | 도메인 사실을 «그대로» 브로커에 넘기면 위반이다 — 타입이 다르고 1:1 도 아니다. 옮겨 담는 일은 유스케이스가 한다. | 트리 41행+D59+D40 | `ast` | principle |  | **blocker** |
| 541 | 커밋 «전»에 발행하면 위반이다 — 그 부작용이 같은 트랜잭션에 들어간다는 뜻이라 「한 트랜잭션 = 애그리거트 하나」(D43)와 정면으로 부딪힌다. | 트리 41행+D59+D43 | `ast` | principle |  | **blocker** |
| 542 | 사실은 «애그리거트»가 만든다 — 상태를 바꾼 그 메서드 안에서 기록한다. 유스케이스가 지어내면 「불변식에 걸려 안 바뀌었는데 사실은 나가는」 경우가 생기고, 같은 메서드를 부르는 유스케이스가 둘이 되면 한쪽이 빠뜨려도 아무도 모른다. | 트리 61행+D59+D12 | `ast` | principle |  | **blocker** |
| 543 | 꺼내는 창구는 `pull_events()` 하나이고 «꺼내면 비운다» — `events` 프로퍼티처럼 «안 비우고 읽는» 길을 함께 두면 위반이다. | 트리 61행+D59 | `ast` | principle |  | **blocker** |
| 545 | 리포지토리 구현 `save()` 는 애그리거트에 «안 꺼낸 사실»이 남아 있으면 **예외를 던진다** — 검사는 「그 가드가 구현 안에 있나」다. <span>08-15 · 인정 형태 명문화 — 그 가드가 애그리거트의 `_events` 를 **비소모로 읽는**(꺼내지 않고 남았는지만 보는) 형태는 인정 형태다(검사기가 이미 수용하는 형태의 명문화 — 검사기 무변).</span> | 트리 92행+D59+D50 | `ast` | principle |  | **blocker** |
| 546 | 한 트랜잭션은 애그리거트 «하나»를 바꾼다 — 검사는 「서로 다른 **애그리거트 리포지토리**에 «쓰기»가 둘」이다. **세는 대상은 타입이 `domain_layer/<aggregate>/<aggregate>_repository.py` 에서 온 것뿐이다** — 「애그리거트 = 트랜잭션 경계」(D50)라 **애그리거트를 안 가진 것은 애초에 대상이 아니다**: `domain_bypass_query/`(#465 가 「애그리거트를 안 거치므로 리포지토리가 아니다」로 이미 뺐다) · 도메인 객체의 메서드(`order.lines.remove`) · 이름만 `save` 인 남의 포트. <span>08-11 · C7 — 옛 문면은 주어가 그냥 「리포지토리」라 **4차 리뷰가 오탐 셋으로 blocker 를 냈다**(CHK-1+2). 주어를 좁히면 셋이 한꺼번에 빠진다 — 별칭(`repo = self._order_repository`)은 **타입이 같아 «하나»로** 세어지고, 나머지 둘은 타입이 그 파일에서 안 온다. 시그니처 어노테이션(#547 전제)은 그 **타입을 «읽을 수 있게» 하는 앞 단계**이지 이 술어 자체가 아니다.</span> | 트리 60행+D43+D50 | `ast` | principle |  | **blocker** |
| 547 | 애그리거트는 «정의상» 트랜잭션 경계다 — 서로 «다른 일»을 하는 두 사용자가 이 경계 때문에 충돌하면 그건 업무 규칙이 아니라 개발자가 만든 제약이다. 트랜잭션을 늘리지 말고 «경계를 쪼갠다». | 트리 60행+D50 | `ast+` | principle |  | **blocker** |
| 548 | 다른 애그리거트는 «식별자 값 객체»로만 문다 — 타입 힌트에 남의 애그리거트 클래스가 나오면 위반이다. 면제는 하나, 조회가 실제로 느려 직접 참조가 필요할 때(원전 Reason Four)다. | 트리 60행+D50+D12 | `ast` | principle |  | **blocker** |
| 549 | 수정하려고 꺼내는 조회는 캐시를 «우회한다» — 선은 애그리거트가 아니라 «트랜잭션»이고, `select_for_update` 를 캐시하면 DB 락이 무용지물이 된다. | 트리 60·92행+D50 | `ast` | principle |  | **blocker** |
| 550 | 배치 면제는 «생성»에만 걸린다 — 이미 있는 것을 여럿 «고치는» 것은 면제가 아니다. | 트리 60행+D43 | `ast` | principle |  | **blocker** |
| 551 | 계약은 `ABC` 를 상속하고 메서드는 전부 `@abstractmethod` 다 — 미구현은 인스턴스화에서 `TypeError` 로 잡힌다. | 트리 47·68·115·121행+D44 | `ast` | principle |  | **blocker** |
| 552 | 구현은 그 계약을 «상속»한다 — 상속만 하면 미구현을 런타임이 잡으므로 강제할 것은 「상속했나」 하나다. | 트리 92·99·102·104·125행+D44 | `ast` | principle |  | **blocker** |
| 553 | 어댑터가 하는 일은 «바꾸고 · 부르고 · 바꾼다» 셋뿐이다 — 도메인에 «시키면» 위반이고, 업무 판정을 여기서 하면 위반이다. | 트리 89행+D45 | `ast+` | principle |  | **blocker** |
| 554 | 어댑터는 «계약이 선언한 실패»로 바꿔 내보낸다 — 계약이 어디 사느냐가 답을 정한다: 리포지토리(도메인)면 도메인 예외, 능력 포트면 포트 예외다. 어댑터는 결정하지 않고 «이름만» 바꾼다. | 트리 89·92행+D51 | `ast` | principle |  | **blocker** |
| 555 | 어댑터가 벤더·django 예외를 «그대로» 위로 흘리면 위반이다 — 그러면 전역 제약 ②가 자료의 모양이 아니라 «실패의 모양»으로 깨진다. | 트리 89행+D51 | `ast` | principle |  | **blocker** |
| 556 | 재시도의 «판정»은 driven 이 지고, «기계»만 `framework/` 가 지며, «다시 부르기»는 입구가 한다 — 셋을 한 낱말로 뭉쳐 한 칸에 두면 위반이다. | 트리 89·112행+D52 | `ast` | principle |  | **blocker** |
| 557 | 일시 실패(transient)의 정규화는 그 인프라를 «소유한» 어댑터가 한다 — 위층이 벤더 오류 코드를 보고 판정하면 위반이다. | 트리 89행+D52+D51 | `ast` | principle |  | **blocker** |
| 558 | `framework/` 는 «링»이 아니다 — 링은 폴더가 아니라 «파일»이 진다. `framework/` 아래 파일도 각자 자기 링의 규칙을 따른다. | 트리 112행+D47 | `ast` | principle |  | **blocker** |
| 559 | `framework/pure/` 에는 순수 계산과 그 계산이 주고받는 «순수 자료»가 온다 — 판정이 곧 이름이다: 「이 파일이 순수한가」. | 트리 128행+D47 | `ast` | principle |  | **blocker** |
| 560 | `framework/pure/` 는 그 **밖의** 저장소 파일을 import 하지 않는다 — 같은 `pure/` 안의 순수 자료 모듈(`Page`·`SortSpec`)은 예외다. 표준 라이브러리는 #561 이 따로 건다. | 트리 128·129행+D47 | `ast` | principle |  | **blocker** |
| 561 | `pure/` 에 부작용이 있으면 위반이다 — `datetime`·`time`·`random`·`secrets`·`uuid`·`os`·`io` 가 나오면 그건 «2차 행위자»라 `<capability>/` 다. 목록은 예시이고 **판정은 「같은 인자로 두 번 불러 같은 답이 나오나」**다(ast 근사). | 트리 128·129행+D47 | `ast` | principle |  | **blocker** |
| 562 | `pure/` 아래에 `*_port.py`·`*_adapter.py` 가 있으면 위반이고, **업무 어휘가 한 글자라도 나오면 위반**이다 — 뒤엣것이 이 트리에서 Shared Kernel 을 막는 기계다. | 트리 128·129행+D47+D24 | `path` | principle |  | **blocker** |
| 563 | BC 를 가로지르는 단계는 물음 «둘»로 갈린다 — ① 「실패하면 내가 할 일이 있나」(예: 지시 / 아니오: 사실) ② 「응답을 기다리게 해도 되나」(예: 요청 / 아니오: 워커). **[Q3]** | D48+D42 | `human` | principle |  | **blocker** |
| 564 | 진행 상태를 기억하는 «진행표»를 만들지 않는다 — 순서는 유스케이스가 지고, 중재자는 «칸»이 아니라 «패턴»이다. | D48+D42 | `ast+` | principle |  | **blocker** |
| 565 | BC 가 «단계»를 도메인에 들려면 업무가 그 단계 이름을 «입으로 부를 때»만이다 — 아니면 워크플로를 도메인 어휘로 위장한 것이라 자리는 유스케이스다. | 트리 60행+D42 | `ast+` | principle |  | **blocker** |
| 566 | 사실 발행 콜백은 앞 콜백의 실패로 «통째로» 사라질 수 있는 자리에 두지 않는다 — 장고 `on_commit` 의 기본값이 그 모양이다. | 트리 96행+D49 | `ast` | principle |  | **blocker** |
| 567 | `schema` 는 «기술 실물»의 이름이라 `dto` 로 부르지 않는다 — `dto` 는 Fowler 의 «프로세스 사이» 패턴 이름이고 우리 것은 같은 프로세스다. | 트리 13·42·44·49행+D55 | `ast` | principle |  | **blocker** |
| 568 | 이름의 자는 «폴더 안이면 접두, 폴더 밖이면 접미»다 — `schema/schema_in.py` ↔ `api/bc_error_schema.py`. | 트리 10·13·14행+D55 | `path` | principle |  | **blocker** |
| 569 | `<use_case>_command.py` 와 `<use_case>_query.py` 는 «둘 다» 온다 — 고르는 것은 이름이 아니라 «어느 쪽에 클래스를 두느냐»이고, 안 쓰는 쪽은 빈 파일이다. | 트리 42·43행+D55+D54 | `ast` | principle |  | **blocker** |
| 570 | `<use_case>_result.py` 는 커맨드 쪽도 갖는다 — 돌려줄 것이 정말 없으면 «빈 파일»이다. | 트리 44행+D55 | `path` | principle |  | **blocker** |
| 571 | `<use_case>_result.py` 에는 «성공했을 때의 모양 한 벌»만 온다 — 실패는 여기 오지 않고, 갈래가 여럿이면 그것은 유스케이스가 둘이라는 신호다. | 트리 44행+D55 | `ast` | principle |  | **blocker** |
| 572 | `bc_error_schema.py` 에는 응답 본문 클래스 `<Bc>ErrorSchema` 와 오류 코드 `<Bc>ErrorCode` 가 함께 온다 — 코드는 스키마의 `code` 필드 «타입»이라 떼면 둘이 따로 늘어난다. <span>08-15 · 승인 예외 — BC base 가 공통 스키마의 «식별자 field» 하나를 자기 `<Bc>ErrorCode` 로 정확히 좁히면서 공통의 default 를 잃어 required 가 되는 모양은 canon 이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 면제 — 그 밖의 required/default 의미 변경은 계속 위반 · 레인 2 BC × 양 레인 수렴 실물의 사용자 승인).</span> | 트리 10행+D55+D27 | `ast` | principle |  | **blocker** |
| 573 | `port/<capability>/<data>_out.py`·`<data>_in.py` 의 방향 기준점은 «우리 안쪽»이다 — 우리에게 들어오면 `_in`, 나가면 `_out` 이다. | 트리 49·50행+D55+D33 | `path` | principle |  | **blocker** |
| 574 | `<data>_in.py` 타입을 «만드는» 것은 어댑터뿐이다 — 유스케이스가 생성하면 위반이다. 여기 오는 것은 «바깥이 답한 것»이라 우리가 지어낼 수 없다. **`port/` 쪽과 `framework/` 쪽 둘 다에 걸린다.** | 트리 50·124행+D55+D33 | `ast` | principle |  | **blocker** |
| 575 | 포트의 «가짜 구현»은 `test/fake/` 에 산다 — `factories/` 의 형제이고, 안에 숨겨 두면 다른 의미군이 무심코 가져다 써 「무엇을 켜고 도는가」가 조용히 깨진다. | 트리 110행+D56 | `path` | principle |  | **blocker** |
| 576 | `test/fake/<declaration>.py` 는 짝이 될 «선언»이 없으면 위반이다 — 검사는 «한 방향»뿐이고, 반대(선언이 있는데 페이크가 없다)는 걸지 않는다. 걸면 모든 포트에 페이크가 강제된다. | 트리 110·111행+D56+D37 | `path` | principle |  | **blocker** |
| 577 | 페이크는 그 선언 클래스를 «상속»하고 파일 이름이 선언과 «같다» — 여기는 «선언당 하나»라 이름이 같고, 기술이 여럿일 수 있는 `adapter/` 쪽과 갈리는 지점이다. | 트리 111행+D56+D44 | `ast` | principle |  | **blocker** |
| 578 | 페이크가 기술을 만지면 위반이다 — DB·네트워크·파일·시계가 나오면 그건 페이크가 아니라 어댑터다. | 트리 111행+D56 | `ast` | principle |  | **blocker** |
| 579 | `application/`·`framework/` 의 «프로덕션» 코드가 페이크를 import 하면 위반이다 — 배포에 실리는 순간 가짜가 진짜 자리에 선다. | 트리 111행+D56 | `ast` | principle |  | **blocker** |
| 580 | 프로덕션에서도 쓰면 그건 페이크가 아니다 — 가르는 자는 「테스트에서만 쓰나」이고, 로컬 개발·기능 플래그로 켠다면 진짜 어댑터라 `adapter/<capability>/` 에 산다. | 트리 110행+D56 | `ast` | principle |  | **blocker** |
| 581 | `test/fake/` 아래에 겹을 더 만들지 않는다 — 평평하다. 선언 쪽 겹을 따라 하면 경로만 길어진다. | 트리 111행+D56 | `path` | principle |  | **blocker** |
| 582 | 한 포트에 어댑터가 «동시에 여럿»일 수 있다 — 그래서 `adapter/<capability>/` 아래 파일 이름은 폴더를 되풀이하지 않고 «어느 기술인가»를 말한다(`<technology>_adapter.py`). | 트리 103·104행+D57+D37 | `path` | principle |  | **blocker** |
| 583 | 기본은 «파일 하나 = 선언 하나» 한 방향이고, 1:1 을 «양방향»으로 거는 자리는 셋뿐이다 — `repository/` · `unit_of_work/` · `domain_bypass_query/`(각 폴더). `broker/` 의 「계약 하나 · 구현 하나」는 #534 가 따로 진다. | 트리 91·93·95행+D57+D37 | `path` | principle |  | **blocker** |
| 584 | `framework/<capability>/` 의 폴더 이름은 `port/<capability>/` 것을 그대로 받는다 — 「무엇이 필요한가」로 짓고 «누가·언제·어떻게»는 넣지 않는다. `smtp_client/`·`redis_cache/` 는 위반이다. | 트리 120행+D57+D46+D24 | `ast+` | principle |  | **blocker** |
| 585 | `framework/<capability>/exception.py` 는 필수이고 도메인 예외를 상속하지 않는다 — 이 칸은 도메인을 아예 모른다. 번역할 대상이 없으면 django·SDK 예외가 유스케이스로 «샌다». | 트리 122행+D24+D27 | `ast` | principle |  | **blocker** |
| 587 | `framework/<capability>/<data>_in.py` 검사 **둘** — 애그리거트가 오면 위반 · 업무 어휘 0. **생성 주체(어댑터뿐)는 #574 가 진다.** | 트리 124행+D24+D33 | `ast` | principle |  | **blocker** |
| 588 | 사람이 읽을 문구(메일 본문·문자 문안·푸시 제목)는 `django_<bounded_context>/templates/<bounded_context>/<capability>/<template>.html` 에 살고, 이 파일을 여는 것은 «어댑터»뿐이다 — 유스케이스나 도메인이 `render_to_string`·`gettext` 를 부르면 위반이다. | 트리 88행+D21+D14 | `ast` | principle |  | **blocker** |
| 589 | 템플릿에 «업무 판정»이 들어오면 위반이다 — 「환불이 되나」를 `{% if %}` 로 다시 쓰면 같은 규칙이 두 채널이 된다(D30). 여기 오는 것은 «이미 정해진 값»뿐이다. | 트리 88행+D21+D30 | `ast+` | principle |  | **blocker** |
| 590 | `Presenter` 는 «칸»이 아니라 «경계 모양»이다 — 문구를 빚는 자리를 따로 만들지 않고, 안쪽은 코드·번호·수량·`locale` 까지만 실어 경계 밖으로 넘긴다. | 트리 88·123행+D14 | `ast+` | principle |  | **blocker** |
| 591 | brownfield 은 «면제»가 아니라 «아직 안 갚은 빚»이다 — 규칙이 바뀌어 위반이 된 코드에 예외를 주지 않는다. 리팩터링 대상은 기존 검사기가 내는 «위반 그 자체»이고 새 백스톱을 따로 만들지 않는다. | D30+§1.1 | `ast` | principle |  | **이행** |
| 592 | 이관을 미루려면 `AskUserQuestion` 으로 사용자 판단을 받는다 — 「가만 있어도 해로운가」로 catch-all 은 못 미룬다. **[Q0]** | §1.1 | `human` | principle |  | **이행** |
| 593 | `migrations/` 안은 사람이 «직접 손대지» 않는다 — 하나라도 손수 편집하면 위반이고, 필요한 변경은 모델을 고쳐 다시 생성한다. **주어는 «사람»이다** — `makemigrations`·`squashmigrations` 처럼 **도구가 만들고 도구가 지우는 변경은 「손수 편집」이 아니다**(압축은 커밋된 파일을 지우고 새로 쓴다). | 트리 80·81행+D15 | `ast` | principle |  | **blocker** |
| 594 | `port/<capability>/` 의 폴더 이름은 「무엇이 필요한가」로 짓고 «바뀔 수 있는 것» 셋을 넣지 않는다 — **누가**(공급자) · **언제**(계기) · **어떻게**(전달 수단). **`smtp_client/` 가 아니라 `email_sender/` 다** — 파일 이름은 #218 이 폴더에 묶는다. | 트리 46행+D46 | `ast+` | principle |  | **blocker** |
| 595 | 이름 판정은 하나다 — 「그것이 바뀌어도 이 이름이 그대로인가」. `smtp_client/`·`redis_cache/`·`nightly_sync/` 는 전부 위반이다. | 트리 46·120행+D46 | `ast+` | principle |  | **blocker** |

## 5차 리뷰가 걷어낸 것 — 14건

**전부 «뒤집힌 카드에서 나온 규칙»이거나 «축자 사본»이다.** 4번의 회수가 110건을 «더하기»만 하고 삭제를 0 했고, 「뒤집힘 14건」 스윕이 사본을 안 훑어 생겼다. 번호는 **재사용하지 않는다**(상호참조 17건이 깨진다).

| 걷어낸 # | 무엇이었나 | 왜 | 대신 |
|---|---|---|---|
| **177** | 「통합 이벤트용 넷째 입구 칸을 만들지 않는다」 | D34 를 **D40 이 뒤집었다** — `event_subscription/` 이 트리 35행에 실재한다. 이걸 두면 **모든 BC 가 골격만으로 blocker** | #90 · #507~#509 |
| **176** | 「주기가 아닌 비동기 작업이 생겨도 칸은 안 는다」 | 같은 이유 | #90 |
| **22 · 317** | 「채워질 때 만든다」 | **D54 가 §0 항상-생성을 되살렸다.** D55 가 *「그대로 뒀으면 §0 을 뒤엎을 뻔했다」*고 이미 경고했고, #317 은 #27(「「나중에 그때」로 끝나는 문장은 그 자체가 결함」)을 **자기가 어겼다** | #488 · #489 |
| **115** | 「HTTP 오류를 안 여는 BC 에는 만들지 않는다」 | **D54 가 「하나 있던 조건부 노드를 지웠다」고 이름까지 댔다** | #488 · #114 |
| **45 · 461** | 「어댑터 파일 이름 = 선언 파일 이름」 | **T48/D57 이 뒤집었다** — `<capability>/` 아래는 `<technology>_adapter.py` 라 이름이 다르다. 뒤집힘 표에 **#353 만 올렸다** | #353 · #582 |
| **158 · 161** | 「`_request`·`_response` 를 붙이지 않는다」 | **D41 이 필수로 만들었다** — 트리 27·29행이 `<request>_request.py`·`<response>_response.py` | #30 · #483 |
| **32** | 「접미사는 이름이 충돌할 때만」 | 같은 결정을 **다른 자**로 재서 같은 파일에 반대 판정을 냈다 — 자는 하나여야 한다 | #30 |
| **255** | 「리포지토리 둘은 위반이 아니라 검토 대상」 | 근거가 *「위반 술어가 없다」*였는데 **D43·D50 이 술어를 만들었다** → 같은 코드에 `검사기` 와 `blocker` 가 동시에 났다 | #546 |
| **223 · 381 · 410** | 「`Port`·`Adapter`·`Gateway` 는 파일 이름에 안 나온다」 ×3 | **#41 과 «글자까지» 같은 사본.** 사본이 있으면 정정이 한 자리에서만 일어나지 않는다 — 이번 병의 원인 그 자체다 | #41(폴더명 금지로 정정) |

**★ 이 병을 다시 안 만들려면 자가 하나 더 필요하다** — 지금까지의 완료 판정 둘(「규칙 0건인 칸 0」·「인용 0건인 카드 0」)은 **«빠진 것»만 세고 «남아 있으면 안 되는 것»은 안 센다.** 셋째 자: **「뒤집힌 카드를 근거로 든 규칙이 0인가」**.

## C2 반영 — 5개 (620~624)

**`framework/test/fake/` 칸 신설**(트리 138 → 140행). 승격의 자가 «소유»가 되면서 framework 포트의 페이크가 **첫 BC 때부터** framework 에 사는데, 그 칸이 없어 진짜 계약과 같은 평면에 놓여 있었다(5차 · L10 F2 · L14 F11 두 렌즈 수렴).

| # | 규칙 | 나온 자리 | 판정 | 근거 | 실측 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 620 | `framework/test/` 의 자식은 셋이다 — `<module>.py`(뼈대) · `fake/` · `unit/`. | 트리 130행+D24+D56 | `path` | principle |  | **blocker** |
| 621 | `framework/<capability>/` 포트의 페이크는 `framework/test/fake/` 에 산다 — BC 의 `test/fake/` 에 두면 짝이 층을 가로지른다. | 트리 132행+D56 | `path` | principle |  | **blocker** |
| 622 | `framework/test/fake/<declaration>.py` 는 선언 파일과 «같은 이름»이고, 안의 클래스는 `framework/<capability>/<capability>_port.py` 의 선언을 상속한다. | 트리 133행+D56 | `ast` | principle |  | **blocker** |
| 623 | `framework/test/fake/` 와 `framework/<capability>/` 의 선언은 1:1 이다 — 선언에 없는 이름이 여기 있으면 위반이다. | 트리 133행+D37 | `path` | principle |  | **blocker** |
| 624 | `framework/test/fake/` 안에서 DB·HTTP·파일을 만지면 위반이다 — 그러면 페이크가 아니라 `framework/<capability>/` 의 어댑터다. | 트리 133행+D56 | `ast` | principle |  | **blocker** |

## C3 반영 — 1개 (625)

| # | 규칙 | 나온 자리 | 판정 | 근거 | 실측 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 625 | DB 엔진·웹 프레임워크 교체는 이 트리의 «관할 밖»이다 — Clean 의 독립 넷 중 Frameworks·Testable·UI 는 서지만 Database 는 절반만 선다(업무 규칙은 DB 에 안 묶이되 엔진은 못 갈아끼운다). **규정이 아니라 한계다.** | 트리 76행+D15+D47 | `human` | principle |  | **면제** |

**「버린 것」이 아니라 「안 산 것」이다.** Martin 의 *Independent of Frameworks* 축자는 *「프레임워크를 **도구로** 쓰고 시스템을 그 제약에 **욱여넣지 않는다**」* 이지 교체 가능성이 아니라서, BC 를 장고 앱으로 만든 것은 **원문이 허용하는 쪽**이다. 안 산 값(엔진 교체) 대신 산 것이 둘 — **BC 경계를 장고가 강제해 준다**(`django_order/` 가 `django_billing/` 를 import 못 한다) · **테스트에서 고정할 수 있다**(D47: 「포트가 필요한 이유는 갈아끼움이 아니라 테스트에서 «고정»하기 위해서」).

## C4 반영 — 2개 (626~627)

**「못 견딘다」에 «누가»가 빠져 있었다.** D49 가 「그 손실을 못 견딘다면 처음부터 ①의 «있다»였다」로 닫았는데, 그 문장은 **보내는 쪽**에만 참이다. **받는 쪽**이 못 견디는 경우(결제 완료 → 정산 일일 마감)는 ①로 판정하면 정직하게 «사실»이고, 그런데 알림이 하루 한 건만 사라져도 정산이 안 맞는다 — 처방대로 «지시»로 바꾸면 **보내는 쪽이 남의 실패를 져야 해서** 어느 칸으로도 못 갔다. **축도 칸도 늘리지 않고 갈래 하나를 이었다.**

| # | 규칙 | 나온 자리 | 판정 | 근거 | 실측 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 626 | 사실이 유실됐을 때 «못 견디는 쪽»이 **받는 쪽**이면, 그 자료를 브로커 통로에 기대는 설계 자체가 위반이다 — 받는 쪽이 `cron_job/` 으로 **시각에** 깨어나 주인의 `open_host_service/` 에 «묻는다». 「그럼 지시였어야 한다」(#526)는 **보내는 쪽**이 못 견딜 때만 성립한다. **[Q3]** | 트리 22·33·115행+D49+D48 | `human` | principle |  | **blocker** |
| 627 | 구독으로 받은 사실의 payload 를 자기 쪽 저장소에 «장부»로 적립·집계하면 위반이다 — 그건 사본(Event-Carried State Transfer)이라 이 트리의 **관할 밖**이다. 상세가 필요하면 주인의 `open_host_service/` 에 되묻는다. | 트리 6·35행+D49 | `ast` | principle |  | **blocker** |

**답은 트리가 이미 그은 선 «안쪽»에 있었다.** D49 가 *「이 트리가 다루는 사실은 **Event Notification** 하나」* 라고 못 박았고, 그 패턴의 정의가 *상세를 안 싣고 「필요하면 소스에 되묻는다」* 이다. **사실은 «깨우는» 것이지 «나르는» 것이 아니다** — 알림이 사라져도 장부는 남는다. 둘을 함께 써도 된다(구독으로 깨어나되 자료는 물어서 얻는다).

**리뷰가 든 예시도 화살표가 틀렸다** — 「결제 완료 → 정산 마감」이라 그렸지만 마감을 부르는 것은 결제 완료가 아니라 **«자정»**이다. 결제가 1,000건 일어나도 마감은 한 번 돈다 — **알림과 1:1 이 아니다.**

**딸려 갈린 것 하나** — `#127` 계열의 「창구는 잘라서 «식별자»만 돌려준다」는 **화면용 목록**의 이야기다. 대사(하루치 맞춤)는 «기간이 곧 조건»이라 대조에 필요한 값까지 실어 준다 — 안 가르면 C4 가 연 길을 창구가 다시 막는다(트리 24행에 반영).

## C2 가 걷어낸 것 — 5건

승격의 자를 «공유(수)»에서 «소유(뜻을 누가 정하나)»로 바꾸면서 **개수를 세던 규칙이 통째로 없어졌다.** 번호는 재사용하지 않는다.

| # | 걷어낸 규칙 | 왜 |
|---|---|---|
| **50** | 「공유 뼈대는 두 번째 BC 가 같은 것을 필요로 할 때 올린다」 | 근거가 **실측 한 줄**(`jpatch` 7벌)이었고, 수는 소유를 검증하지 못한다 |
| **424** | 「공유 뼈대는 처음부터 `framework/test/` 에 만들지 않는다」 | **정확히 반대가 됐다** — 뜻을 밖이 정하면 첫 BC 때부터 여기 만든다 |
| **449**(옛) | 「자격만 참일 때는 올리지 않는다」 | «계기»가 없어져 「자격만」이라는 상태가 사라졌다 (번호는 새 규칙이 잇는다) |
| **468** | 「`<technology>/` 는 «계기»가 면제된다」 | 면제할 계기가 없다. **예외 0** |
| **605** | 「자격을 **삽입 방향**으로 잰다」 | 그것도 **«공유» 질문**이라 같은 구멍이 남는다 — 두 BC 의 「요청시간 판정」을 올려도 새 BC 를 붙일 때 그 파일은 안 바뀐다 |

**원전 대조** — 수를 말하는 유일한 원전은 Roberts/Fowler(*"The **second** time … you **do the duplicate thing anyway**. The **third** time … you refactor."*)이고 그건 **「셋」**이다. Metz·Grzybek·Evans 셋은 **수를 안 적는다**. 「셋」으로 올리는 안도 기각했다 — 같은 지식인 줄 알면서 두 벌을 «더 오래» 유지하라는 뜻이라 DRY 와 부딪힌다.

## C5 ㉮ 가 걷어낸 것 — 8건

**등급을 매기기 전에 «규칙끼리 반대말을 하거나 같은 말을 두 번 하는 것»부터 걷었다.** 적대적 리뷰(R1·R3)가 찾았고 전수 대조로 확인했다. 번호는 재사용하지 않는다.

| # | 걷어낸 규칙 | 왜 |
|---|---|---|
| **106** | BC 전체에 걸리는 것만 `api/` 바로 밑에 두고, 한 area 에만 갇힌 것은 전부 `<area>/` 아래로 내린다. | #105 가 `api/` 직속을 «파일 둘·폴더 둘»로 닫아 판정 대상이 0 |
| **122** | 값이 하나인 축으로는 폴더를 만들지 않는다. | #20 과 같은 문장(「하나뿐인」/「하나인」 차이뿐) |
| **199** | `with unit_of_work:` 블록 «안»에서 크로스-BC 포트를 부르지 않는다. | #14 와 자구 동일(근거 D17 을 #14 로 병합) |
| **224** | `port/<capability>/<capability>_port.py` 를 구현하는 클래스는 전부 `…Adapter` 로 끝난다. | #39 와 자구 동일 — #39 의 자리 표기가 더 완전(트리 125행 포함) |
| **333** | BC 이름이 바뀌면 `label` 도 같이 바꾼다 — 한쪽만 바꾸지 않는다. | #330(「label 값은 BC 이름과 같다」)이 «항상» 참이면 자동 충족되는 시제 표현 |
| **378** | `with unit_of_work:` 블록 안에서 크로스-BC 포트를 부르면 위반이다. | #14 와 자구 동일(근거 D17 을 #14 로 병합) |
| **469** | `framework/<capability>/<capability>_port.py` 의 시그니처에 «BC 를 가르는 인자»(`kind`·`mode`·`bc`·`is_…`)가 나오면 위반이다. | #606 이 「강등 신호는 인자 «이름»에 의존하지 않는다」로 **명시 폐기**했다 |
| **586** | `framework/<capability>/<data>_out.py` 검사 넷 — 애그리거트가 오면 위반 · 업무 어휘가 한 글자라도 나오면 위반 · `locale` 이 바꾸는 값과 채널 설정은 안 담는다 · 원시값·값 객체로 되면  | #616·#617·#618·#619 로 «완전 분해»되어 있다 — 한 행이 넷을 덮는 병 |

**★ `#469` 만 성질이 다르다** — 나머지 일곱은 «중복»이지만 이것은 **정면 충돌**이었다. `#469` 는 인자 «이름»(`kind`·`mode`·`bc`·`is_…`)으로 강등을 재는데, 5차가 신설한 `#606` 이 *「강등 신호는 인자 «이름»에 의존하지 않는다」*로 그 방식을 명시적으로 폐기하고 대체 신호 셋(반환형 `bool` · 인자 수 증가 · 대상은 BC 둘 이상이 import 하는 framework 파일 전부)을 세웠다. **`#606` 을 신설하면서 `#469` 를 안 걷은 것**이다.

**★ `#586` 은 이 문서의 고질병의 또 한 사례** — 검사 «넷»을 한 행에 뭉쳐 놓고, 5차 회수가 그 넷을 `#616`~`#619` 로 다시 적었다. 같은 검사가 `ast` 1행 + `human`/`ast` 4행으로 흩어져 «등급이 갈렸다».

## C5 ㉮ 가 고친 것 — 5건

**걷어낸 8건과 달리 이쪽은 «규칙이 살아 있는데 문장이 틀린 것»이다.** 넷은 다른 규칙과 부딪혀 **준수 코드를 blocker 로 만들고** 있었고, 하나는 검사가 **조용히 통과**하고 있었다.

| # | 무엇이 틀렸나 | 어떻게 고쳤나 |
|---|---|---|
| **368** | **`#556`(D52)과 정면 충돌** — 옛 문면 「재시도는 `external_system/` 에서만」과 D52 의 「«기계»만 `framework/`」를 **둘 다 켜면 재시도 기계가 살 자리가 0**이 된다. D52 가 세 갈래로 가른 뒤 이 행을 안 걷었다 | **D52 의 세 갈래를 이 행에 반영** — «값»은 소유 어댑터 · «기계»는 `framework/` · «다시 부르기»는 입구 |
| **367** | **목록이 «닫혀» 있는데 셋뿐** — `#319`·`#366` 이 축자로 「우리가 운영하는 **Redis·Kafka** 도 `external_system/`」이라 적는데 `redis`·`kafka` 가 목록 밖이라 **검사가 0건을 돌려주고 «통과»로 읽힌다**. `requests`·`pika`·`smtplib`·`grpcio` 도 같다 | **열거를 «자»로** — 「소켓을 여나」 하나로 가르고, 목록은 **저장소 의존성에 맞춰 유지하는 데이터**로 |
| **593** | 「손수 편집 금지」의 **주어가 안 적혀** 있어, 도구가 만드는 변경까지 막는 것으로 읽힌다 — 그러면 **`squashmigrations` 가 blocker** 가 되는데 사용자가 이 규칙을 요청한 이유가 축자로 「압축하는 경우도 있기 때문」이다 | **주어를 «사람»으로 명시** — 도구가 만들고 도구가 지우는 변경은 손수 편집이 아니다 |
| **153** | 「바꾸고·부르고·되돌리는 **일만** 한다」가 `#164`(도메인 예외를 계약 타입으로 **번역해 던진다**)를 **밖으로 밀어낸다** — 둘을 동시에 만족하는 창구 구현이 존재하지 않아 **준수 BC 가 전부 blocker** | 예외 번역이 **「되돌리는 일」에 들어간다**고 명시(거절도 답이다) |
| **14** | `#199`·`#378` 을 흡수하며 자구를 통일 | — |

**★ 다섯 중 넷이 «나중 결정이 앞 행을 안 걷은 것»이다** — D52·5차 회수·D27 이 각각 새 문장을 세우면서 옛 문장을 그대로 뒀다. 「C2 가 걷어낸 것」·「C5 ㉮ 가 걷어낸 것」 과 **같은 병**이고, 5차 리뷰가 「110건 «더하기»만 하고 삭제 0」이라 진단한 그것이다.

## ㉯ 가 걷어낸 것 — 71건 (중복·포함)

**5차 리뷰가 「110건 «더하기»만 하고 삭제 0 · 축자 사본 20~31쌍」이라 진단한 것의 실물이다.** 전수 스캔이 낸 69쌍 후보를 네 갈래로 나눠 **7컬럼 전부**를 대조하고, 쌍마다 「한쪽만 위반인 코드를 제시하라」는 반박 과제를 함께 걸었다. **판정: 중복 35 · 포함 25 · 다름 10 · 모순 2.** «다름»으로 살아남은 열 쌍은 그대로 둔다.

**남긴 쪽을 고르는 자 셋** — 이 문서가 이미 쓰던 것이다.
1. **트리 앵커를 가진 쪽**(#224 선례: *「#39 의 자리 표기가 더 완전(트리 125행 포함)」*)
2. **기계 판정(`ast`/`path`)이 붙은 쪽**(#586 선례: *「같은 검사가 흩어져 «등급이 갈렸다»」*)
3. **다른 행이 번호로 부르는 쪽**(참조 무결성이 1·2보다 우선한다)

| 남은 것 | 걷어낸 것 | 규칙(요약) |
|---|---|---|
| **#4** | #184 | `application_layer/` 는 django 를 하나도 import 하지 않는다 — 트랜잭션도 시각도 DB 예외도 포트를 거친다. |
| **#8** | #250 | `domain_layer/` 안의 어떤 파일도 자기 층 밖으로 나가는 import 를 갖지 않는다 — django 도 다른 층도 다른 BC 도 모른다. |
| **#9** | #321 | `driven_layer/**` 는 `domain_layer` 와 `application_layer/port/` 만 의존한다 — import 에 `drivin |
| **#11** | #203 | `<use_case>_command.py` 에 실을 수 없는 것은 «연 쪽이 닫기까지 하는 손잡이»다 — 판정은 「이 손잡이를 «연 쪽»이 «닫기»까지 하나」 |
| **#13** | #360 | 타 BC 를 import 하는 것은 `anticorruption_layer/` 아래에서만 허용되고, 그것도 상대의 `open_host_service/` 아래만 |
| **#15** | #138 | 트리는 그 구분으로 규칙을 쓰거나 검사를 할 수 있는 데까지만 폴더·파일을 못 박고 그 아래는 작성자 재량이다. |
| **#17** | #478 | §0-4(1차 폴더는 도메인 이름) 검사가 무는 범위는 «도메인 것»을 나누는 칸(`<aggregate>/`·`<area>/`)이다 — 입구 칸의 1차는 «어 |
| **#28** | #147 | 원전 패턴 이름은 줄이지 않고 그대로 쓴다 — `open_host_service/`. |
| **#35** | #397 | 저장소 루트의 패키지 이름은 파이썬 표준 라이브러리 모듈명(`sys.stdlib_module_names`)과 겹치지 않는다. |
| **#40** | #37 · #222 · #380 · #409 | 클래스 이름은 접두사(누구·기술) + 파일 이름 CamelCase + 자리 접미사로 짓는다. |
| **#46** | #394 | `framework/` 에서 `application/` 쪽으로 나가는 import 는 0이다. |
| **#47** | #399 | `framework/<capability>/` 에 들어오는 문은 하나다 — 계약의 «이름에도 시그니처에도» 어느 BC 의 업무 어휘가 한 글자도 나오지 않아야 |
| **#49** | #421 | `framework/` 에 `shared_kernel/` 칸을 두지 않는다 — BC 사이의 공유는 언제나 관문 + 번역으로 푼다. |
| **#51** | #386 | BC 의 테스트는 다른 BC 의 `test/` 를 import 하지 않는다. |
| **#53** | #422 · #427 | `framework/test/` 는 HTTP 로만 시스템을 구동한다 — 모델 import 금지다. |
| **#59** | #128 | 전역 예외 핸들러나 catch-all mapper 를 두지 않는다. |
| **#62** | #130 · #296 | 폴백을 둘 경우 도메인·응용 base 단위 catch 로 한정하고 `except Exception` 은 쓰지 않는다. |
| **#63** | #133 · #419 | 오류 응답은 `response={status: <Bc>ErrorSchema}` 으로 operation 이 직접 선언한다 — `openapi_extra` 보충이 |
| **#64** | #226 · #293 | 포트 예외는 도메인 예외를 상속하지 않는다. |
| **#74** | #612 | 검사기는 저장소가 표준을 채택한 신호(`application/`·`framework/`·`<project>/`)가 있는데 검사 대상이 0건이면 **exit 2 |
| **#90** | #510 | 입구 넷을 가르는 1차 축은 «어떤 전송으로 오나»다 — HTTP `api/` · 같은 프로세스 함수 호출 `open_host_service/` · celer |
| **#92** | #6 | driving_layer 는 application_layer 만 import 한다 — 예외는 #95(도메인 exception·값 객체를 «자료로»)와 #97( |
| **#119** | #418 | 프레임워크 오류(401·403·404·422·429·`HttpError`·미식별 500)는 `framework` 가 소유하고, 전역 handler 나 catc |
| **#126** | #60 | 컨트롤러가 exception→ErrorSchema 매핑을 직접 소유하고 helper·factory·serializer·핸들러 등록 decorator·globa |
| **#148** | #29 | 일반어가 된 약어(api)는 그대로 둔다. |
| **#182** | #65 | `application_layer/` 의 직속 자식은 `<area>/` · `port/` **둘뿐**이다. |
| **#183** | #66 | application_layer/ 아래에 validation/ 폴더나 *_validation.py 를 두지 않는다. |
| **#220** | #38 | `port/<capability>/<capability>_port.py` 의 계약 클래스는 전부 …Port 로 끝난다 — port/ 의 다른 두 자식은 각자의 |
| **#236** | #237 | 질의 결과를 동적 타입 그대로 흘려보내지 않는다 — 나가는 모양은 이름 붙인 자료여야 한다. |
| **#246** | #377 | UnitOfWork 는 리포지토리를 노출하지 않는다 — `unit_of_work/` 의 클래스는 리포지토리 타입을 반환하는 멤버를 갖지 않는다(모양 B 금지) |
| **#247** | #379 | UnitOfWork 클래스 이름은 선언이 `<Bc>UnitOfWork` · 구현이 `Django<Bc>UnitOfWork` 다 — 접두사가 가른다. |
| **#266** | #297 | 애그리거트 둘 이상이 함께 쓰는 값 객체는 애그리거트 형제 자리인 `domain_layer/shared_value_object/` 에 둔다. |
| **#279** | #198 | 이벤트 핸들러는 새 칸을 만들지 않고 «하는 일»로 이름 붙인 보통 유스케이스로 둔다. |
| **#287** | #598 | 쓰기 메서드의 인자는 «애그리거트(또는 그 목록)»다 — 인자가 «조건·필드»면 위반이다(`bulk_update(filter, fields)`·`update( |
| **#294** | #243 | 저장이 실패하는 방식은 응용에 선언하지 않는다 — 업무 의미가 있으면 `domain_layer/<aggregate>/exception/`, 재시도 판정은 `f |
| **#295** | #61 · #165 | 도메인 예외를 raw 로 전파하거나 __all__ 로 재노출하지 않고, 알려진 구체 예외의 전수 명시 매핑으로 번역한다. |
| **#312** | #70 | 인터페이스가 있는 «이유»로 자리가 갈린다 — 바깥을 갈아끼우려는 것은 application_layer/port/ 선언 + driven_layer/ 구현이고, |
| **#319** | #320 | `driven_layer/adapter/` 의 자식은 «내가 무엇을 구동하나»로 갈린 넷이다 — 우리 DB 면 `persistence/` · 다른 BC 면 ` |
| **#339** | #57 | 어드민은 자리와 이름만 규정하고 화살표·앎의 범위는 규정하지 않는다. |
| **#348** | #479 | 어드민 템플릿 덮어쓰기 경로의 셋째 마디는 폴더 이름(`django_…`)이 아니라 `apps.py` 의 `label` 이고, `<model>` 마디는 모델  |
| **#355** | #230 · #284 | 조회의 주어가 그 애그리거트면 `domain_layer/<aggregate>/<aggregate>_repository.py` 에, 화면이면 `domain_by |
| **#372** | #400 | 어댑터의 계약에 업무 어휘가 한 글자라도 있으면 BC 안 `driven_layer/adapter/<capability>/<technology>_adapter. |
| **#374** | #466 | UnitOfWork 구현은 `adapter/persistence/unit_of_work/` 아래에 살고 경계 하나에 파일 하나다. |
| **#420** | #104 | `driving_layer/api/` 에 인증 클래스 파일(`authentication.py`)을 두지 않는다 — 틀은 `framework/`, 해석은 관문이 |
| **#430** | #55 | 저장소 루트 조립 구역은 application/ 의 BC 를 «등록»만 하고 «타입»으로 알지 않으며 부작용 등록(# noqa: F401)도 금지다. |
| **#437** | #438 · #439 | `<project>/api.py` 에 도메인 예외 목록을 두지 않는다. |
| **#464** | #286 | 리포지토리를 `command/`·`query/` 폴더로 가르지 않는다. |
| **#481** | #31 | 폴더가 종류를 말하면 **자식 폴더**는 그 종류를 반복하지 않는다 — 파일은 #30 이 진다. |
| **#487** | #608 | 검사 러너는 제1원칙 게이트(#486~#492)를 **1순위로** 돌리고 걸리면 나머지를 돌리지 않고 반환한다 — 지금 `commands/dddjango.md |
| **#493** | #306 | 도메인 서비스 시그니처는 파라미터 타입을 명시한다 — 타입 힌트가 없으면 리포지토리를 import 없이 파라미터로 받는 우회가 열린다. |
| **#505** | #273 · #277 | 다른 BC 는 도메인 이벤트를 직접 받지 못한다 — 도메인 이벤트와 통합 이벤트는 다른 물건이고 경계는 관문으로만 넘는다. |
| **#506** | #278 · #544 | 발행 장치(핸들러 레지스트리·`dispatch_…()`·`register_…_handler()`)는 `event/` 에 살지 않는다 — 밖으로 나갈 일이면 애 |
| **#524** | #499 | 같은 짝(사실 → 리스너)을 두 번 받아도 구독자가 둘이 되지 않는다 — 원전이 「한 번」을 보장하지 않는다(*“in tests … `ready` might  |
| **#540** | #274 | 도메인 이벤트를 «그대로» BC 밖으로 내보내지 않는다 — 밖으로 알릴 것은 유스케이스가 `published_event/` 로 옮겨 담고(#540), 받는 쪽 |
| **#541** | #281 | 도메인 이벤트 발행은 유스케이스가 커밋 뒤에 한다. |
| **#564** | #519 | 브로커에 단계·순서·보상을 «기억하는» 상태가 있으면 위반이다 — 그건 «중재자»이고 중재자는 칸이 아니다. 순서는 유스케이스가 진다. |
| **#572** | #116 | `bc_error_schema.py` 에는 응답 본문 클래스 `<Bc>ErrorSchema` 하나와 이 BC 가 쓰는 오류 코드 목록이 온다. |
| **#582** | #458 | `port/` 아래 선언 하나에 `adapter/` 구현이 여럿일 수 있다 — «필요»는 하나인데 «누가 해 주나»는 여럿일 수 있다. |
| **#594** | #217 | 포트 폴더와 파일 이름은 «무엇이 필요한가»로 짓고 구현자(기술·공급 BC)를 이름에 넣지 않는다 — `smtp_client.py` 가 아니라 `email_s |

### ★ 걷다가 나온 «모순» 둘 — 삭제와 별개로 지금 깨져 있던 것이다

| # | 무엇이 깨져 있었나 |
|---|---|
| **6** | 예외를 「#95·#97 **뿐**」이라 적어 **#507(남의 `published_event/`)이 빠졌다** — 문면대로 켜면 `event_subscription/` 이 통째로 blocker 다. 게다가 주어가 «층 전체»라 #111 이 요구하는 `api_router.py` 의 컨트롤러 import 까지 문다(#99 의 면제는 주어가 «잎»인 #92 에만 걸린다). **#92 를 남기고 #6 을 걷었다** — 변환 기록 ③ «내용이 뒤집힌 규칙» 표가 #92 만 올려 스윕했고 #6 은 안 받았다 |
| **37** | 클래스 이름 앵커를 «파일»로만 잡아, **#408 이 요구하는 `DjangoClockAdapter` 를 위반으로 찍는다**(앵커가 폴더여야 한다). 같은 절의 #40 이 자리 컬럼에 *「08-07 2차 리뷰 S6 로 앵커가 둘이 됐다」*라 적는데 #37 은 그 스윕을 안 받았다 |

### ★ 딸려 나온 구멍 — **#92 의 예외 목록에 `framework/` 가 없었다**

#420·#517 이 **driving 잎의 라우트 데코레이터에서 `framework/ninja/` import 를 «요구»**하는데, #6 도 #92 도 예외에 `framework/` 를 안 적었다. 문면 그대로면 **모든 컨트롤러가 blocker** 다. 「프레임워크」라는 낱말이 «라이브러리»(#100 이 허용)와 «폴더 `framework/`»(허용 규정 0)를 함께 덮은 것이고, `application_layer` 쪽은 #7 이 이미 넷으로 열어 뒀는데 driving 쪽만 안 열려 있었다. **#92 의 예외를 셋 → 넷으로 고쳤다.**

### 함께 고친 것

| 종류 | 무엇 |
|---|---|
| **참조** | #9 「예외는 **#360**」 → **#13** (#360 은 `published_event/` 를 빠뜨려 걷었다) · #490 「#15·**#138**」 → #15 · #628 의 재료 목록에서 #399·#400 제거(열 → 여덟) · #220 에 #38 이 갖고 있던 #235·#247 포인터 이전 |
| **등급** | #129 `human`→`ast` · #504 `path`→`ast` · #348 `path`→`ast` · #119 `human`→`ast` — **전부 `ast` 사본을 걷으면서 강등될 뻔한 것**이다 |
| **자리 오기** | #64 「트리 40행」 → **48행**(40행은 `<use_case>/` 이고 포트 `exception.py` 는 48행이다) |
| **문면** | #287 에 「(또는 그 목록)」 — 단수로 두면 #599(`save_all()` 개방)와 어긋난다 · #40 에 「«포함»이라 접두사가 열려 있다」 — 조합형(#222·#380)으로 읽으면 #403·#220 이 요구하는 무접두 `ClockPort` 가 위반이 된다 |

**★ 딸려 드러난 «틀린 인용» 하나 — #367 의 「`framework/` 쪽 SDK 는 #400·#534 가 따로 연다」.** #400 을 걷으며 소유자가 빈 줄 알았는데, 대조해 보니 **#400 은 배치 규칙(업무 어휘로 BC/framework 를 가른다)이고 #534 는 파일 개수 규칙(계약 하나·구현 하나)이라 둘 다 SDK 를 «열지» 않는다** — 인용이 처음부터 틀렸다. 게다가 #367 의 주어는 `driven_layer/**` 라 **`framework/` 는 애초에 대상 밖**이다. 실제 소유자는 `framework/<technology>/`(#411·#415)와 `framework/<capability>/<technology>_adapter.py`(#405·#406·#408)이고, 그렇게 고쳤다. **규칙 신설 0.**

## C7′ 반영 — 1개 (628)

**「업무 어휘가 한 글자라도 나오면 위반」이라 적은 규칙이 열한 개인데, «업무 어휘»가 무엇인지 정한 자리가 없었다.** 검사기는 임시로 `domain_layer/` 의 **폴더 이름**을 대용으로 쓰고 있었고, 그래서 `Money`(`shared_value_object/money.py`)를 `framework/` 로 올려도 **통과한다**.

**원전이 그 범위를 직접 센다.** Evans 축자 — *「**The core of such a language comes from the domain model.**」* 이고, 처방이 바꿀 대상을 셋으로 든다 — *「refactor the code, **renaming classes, methods and modules** to conform to the new model.」* **클래스·메서드·모듈** 셋이므로 **폴더만 보는 것은 원전 기준으로도 반쪽**이다.

| # | 규칙 | 나온 자리 | 판정 | 근거 | 실측 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 628 | 이 BC 의 **«업무 어휘»는 `domain_layer/**` 아래 공개 심볼(모듈·클래스·함수·Enum 값) 이름의 토큰 집합**이다 — 폴더 이름만이 아니다. `#47`·`#228`·`#372`·`#463`·`#518`·`#562`·`#587`·`#617` 여덟이 이 집합 하나를 재료로 쓴다. 별도의 «용어집 파일»은 두지 않는다. **불용어 목록도 «저장소가 유지하는 데이터»다** — `Id`·`Status`·`Name`·`Item`·`Type`·`Value` 처럼 어느 BC 에나 나오는 낱말을 안 빼면 `framework/` 계약이 대량 오탐을 낸다. 목록을 «닫지» 않고 데이터로 두는 방식은 #367 이 이미 채택했다. | 트리 1·59행+D24 | `ast` | principle |  | **blocker** |

**용어집 파일을 안 여는 근거도 원전에 있다.** *「a document **shouldn't try to do what the code already does well**. The code already supplies the detail.」* · *「Keeping it up to date through sheer will and discipline **wastes effort**, if the document isn't playing an important role.」* 베껴 적은 사전은 도메인이 자랄 때마다 손으로 고쳐야 하고 **안 고쳐도 아무 일이 안 일어나** 죽는다. D30 의 «두 채널»에도 걸린다 — `domain_layer/` 를 재료로 쓰면 채널이 하나다. 사람이 읽는 용어집(Vernon 이 권한다)은 만들어도 되지만 **그것은 검사 재료가 아니다**.

**★ 적대적 리뷰(R3)의 진단 둘을 고쳤다.**

| 리뷰 | 실제 |
|---|---|
| *「정본에서 "유비쿼터스"·"용어집"·"glossary" 검색 → **0건**」* | **`Ubiquitous` 를 안 검색했다** — BC 루트 패널이 *「이 안에서만 하나의 Ubiquitous Language 가 통한다」*로 **뿌리에 이미 적고 있다**. 없던 것은 «용어집 파일»이지 «보편 언어»가 아니다 |
| *「`#17`·`#18`·`#47`·`#82`·`#299`·`#372`·`#607` **일곱이 한 물음**」* | **셋이 다른 물음이다** — `#18` 은 예외 목록이 «닫혀» 있어 사전이 필요 없고, `#82` 는 BC 이름을 «짓는» 일이며, **`#607` 은 규칙 자신이 「중립 이름으로 갈아입어도 판정은 판정」이라 적어 어휘 집합으로는 못 잡는다** |

**★ 이 한 줄로 열 규칙의 판정이 `human` 을 벗는다** — 「사람이 사전을 채워 달라」가 아니라 **「이미 채워져 있고 기계가 읽는다」**가 된다.

## C5 ㉠′ 가 고친 것 — 3건

**한 문장 안에서 「값 객체」가 두 번 나오고 «가리키는 것이 반대»였다.**

```
트리 49행 (옛)   원시값·값 객체로 안 될 때만 생긴다.  DTO 도 값 객체도 아니다
                              ↑ 써도 되는 것              ↑ 오면 안 되는 것
```

`#227` 이 「값 객체로 **되면** 파일을 만들지 마라」라 하니 **값 객체를 «쓰라»는 뜻**인데, `#228` 이 「값 객체를 **두지** 않는다」라 하니 나란히 놓으면 **정면충돌로 읽힌다**. 적대적 리뷰(R1)가 정확히 그렇게 읽고 *「`Address` 를 편 것을 고칠 방법이 트리 안에 없다 — framework 에 값 객체 칸이 필요하다」*(C7″)로 갔다. **없는 문제였다.**

**갈림선은 「정의냐 사용이냐」가 아니라 «그 값 객체가 누구 어휘냐»다.** 트리 49행이 이미 자를 갖고 있었다 — *「갈림선은 «누구의 어휘냐»다 … 이건 **주인이 «바깥»**이다」*. 도메인 값 객체를 그대로 실으면 주인이 도메인으로 넘어가 그 자를 깬다. 그래서 **정의도 사용도 막히고, `Address` 를 `street`·`city`·`zip` 로 «펴는» 것이 정답**이다.

| # | 무엇이 틀렸나 | 어떻게 고쳤나 |
|---|---|---|
| **227** | 「값 객체」가 무엇을 가리키는지 안 적어 `#228` 과 충돌하는 것처럼 읽힌다 | **표준 타입이나 «이 포트 어휘로 된 타입»**이라고 못 박았다 |
| **228** | 「두지 않는다」가 «정의»만인지 «사용»까지인지 안 갈리고, **까닭이 없다** | **둘 다 닫고 까닭을 달았다** — 이 BC 의 업무 어휘가 포트 밖으로 새면 안 된다 |
| **619** | 트리 123행이 *「BC 의 것과 «같은 것»이다. 담기는 것도, 안 담기는 것도 같다」*라 못 박아 **차이를 지웠다** — 리뷰가 C7″ 로 간 **직접 경로** | **`framework/` 는 `domain_layer/` 를 못 보므로 `#228` 이 자동 성립**하고 이 자리의 값 객체는 **표준 타입뿐**임을 적었다 |

**★ 세 번째로 같은 병이다** — [[C5 ㉮ 가 고친 것]] 의 다섯 중 넷과 마찬가지로 **한 낱말이 둘을 덮었다**. 다만 앞선 것들은 «나중 결정이 옛 문장을 안 걷은 것»이고, 이것은 **처음부터 같은 줄 안에서 낱말이 두 뜻으로 쓰인 것**이다. 정본 세 곳(49행 note · 123행 note · 123행 패널)도 함께 고쳤다 — **트리 신설 0 · 규칙 신설 0 · 삭제 0**.

## Phase 1 리뷰 회수 — 7개 (630~636)

Phase 1 산출물 리뷰(렌즈③ «잃은 값»)의 회수다. **유실 확정 2건**(#630·#631 — 옛 houserules 가 정해 검사기까지 갖고 있었는데 회수 스윕이 놓친 것)에 더해, «애매» 7건 중 **다섯을 사용자 승인(T60 · 2026-08-11)으로 복원**했다(#632~#636). 남은 둘은 «보류»로 닫았다 — T60-6(응용 입출력의 `@dataclass` 형태 강제 — 형태 자유가 해롭지 않다) · T60-7(애그리거트 폴더 단수형 — 옛 문면 스스로 «권장·백스톱 없음»).

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 630 | 신규 ORM 모델은 `Meta.db_table` 을 명시하고 값은 `<app_label>_<entity_snake>` 다 — 클래스명에서 `Model` 을 떼고 snake_case(`ProductModel` → `catalog_product`). `abstract`·`proxy`·`managed=False` 는 면제, 기존 모델의 테이블명은 보존한다(개명 강제 아님). Django 기본값 `<app>_<name>model` 의 `model` 군더더기를 막는다. <span>08-11 · Phase 1 렌즈③ — 옛 houserules §4 가 정하고 검사기가 절반(존재만) 강제하던 것을 복원.</span> | 트리 79행 | `ast` | principle |  | **blocker** |
| 631 | 타 BC 의 모델을 ORM 관계 필드(`ForeignKey`·`OneToOneField`·`ManyToManyField`)로 참조하지 않는다 — 문자열 참조(`"billing.OrderModel"`)도 같다. 타 BC 는 ID «값»으로만 참조하고 존재 검증은 OHS·ACL 로 한다. 같은 BC 안 FK 는 정식이다. import 축 규칙(#8·#12)이 못 보는 통로다 — 장고 FK 는 import 없이 BC 를 가로지른다. <span>08-11 · Phase 1 렌즈③ — 옛 houserules §2 컨텍스트 간 통신 조문의 복원.</span> | 트리 79행 | `ast` | principle |  | **blocker** |
| 632 | ORM 모델 클래스 이름은 «상시» `<Name>Model` 이다 — 도메인 쪽이 bare(`Order`), ORM 쪽이 `OrderModel` 로 늘 갈린다. «이름이 충돌할 때만»이 아니다 — alias import 로 충돌을 피해도 규칙은 남는다(파일 축은 #335 가 진다). <span>08-11 · T60-1 복원(사용자 승인).</span> | 트리 79행 | `ast` | principle |  | **blocker** |
| 633 | `<service>_service.py` 의 공개 함수는 인자로 그 연산의 request 계약 **하나**만 받는다 — 맨 스칼라·다중 인자는 위반이고, 인자 0개는 입력 없는 `_query` 만 허용한다. <span>08-11 · T60-2 복원(사용자 승인).</span> | 트리 24행 | `ast` | principle |  | **blocker** |
| 634 | `<service>_service.py` 의 공개 표면은 모듈 수준 «함수»뿐이다 — 공개 클래스를 두지 않는다(계약 클래스는 `contract/` 에 산다 · `_` 사설은 자유). <span>08-11 · T60-3 복원(사용자 승인).</span> | 트리 24행 | `ast` | principle |  | **blocker** |
| 635 | `<use_case>_use_case.py` 의 진입점은 클래스 하나이고 실행 메서드는 `execute` 하나다 — 자기 `<use_case>_command.py`/`_query.py` 의 계약 객체 하나를 받아 `<use_case>_result.py` 의 result(스트림이면 `Iterator[<UseCase>Result]` — D40)를 돌려준다. <span>08-11 · T60-4 복원(사용자 승인).</span> | 트리 41행 | `ast` | principle |  | **blocker** |
| 636 | `bc_error_schema.py` 의 `<Bc>ErrorCode` 는 `StrEnum` 이다 — `Literal`·맨 문자열 상수 모음으로 대신하지 않는다(#572 가 정한 동거의 «타입» 축). <span>08-11 · T60-5 복원(사용자 승인).</span> | 트리 10행 | `ast` | principle |  | **blocker** |

## 5차 적대적 리뷰 회수 — 20개 (596~619)

**14개 렌즈(29148·Smells·모순·중복·DDD·Clean·Hexagonal·pub/sub·ATAM·인지차원·Connascence·SAAM·백스톱·framework 승격)가 연 구멍을 메운다.**

앞선 정정에서 **규칙 14건을 걷어냈고**(뒤집힌 카드에서 나온 것 · 축자 사본) **65건의 문면을 고쳤다** — 그 목록은 아래 «걷어낸 것» 절에.

| # | 규칙 | 자리 | 판정 | 근거 | 3차 | 어겼을 때 |
|---|---|---|---|---|---|---|
| 596 | `test/unit/`·`test/integration/`·`test/e2e/` 아래는 폐쇄(#490)의 대상이 아니다 — 파일 이름을 pytest 가 소유한다. `conftest.py` 도 여기 산다. `factories/`·`fake/` 는 «재료»라 폐쇄가 그대로 걸린다. | 트리 105~111행+D56 | `path` | principle |  | **면제** |
| 597 | **애그리거트 리포지토리**의 «쓰기» 메서드 이름은 `save`·`remove` 로 시작한다 — BC 마다 `add`/`store`/`persist` 로 갈리면 「한 트랜잭션 = 애그리거트 하나」(#546)의 검사가 **아예 못 선다**. **거꾸로 리포지토리가 «아닌» 것이 `save` 라는 이름을 써도 #546 은 안 문다** — 세는 대상이 «이름»이 아니라 «타입»으로 갈리기 때문이다. <span>08-11 · C7 — 이름 규칙을 양방향으로 만드는 안(「리포지토리가 아니면 `save` 를 쓰지 마라」)은 **기각**했다. #546 의 주어를 좁히면 그 이름이 어디서 나오든 셈에 안 들어와서, 새 금지가 **아무 일도 안 한다**.</span> | 트리 68행+D43+T37 | `ast` | principle |  | **blocker** |
| 599 | `save_all()` 은 열려 있고 조건이 셋이다 — ㉠ 트랜잭션을 열지 않는다(`with unit_of_work:` 안에서만 불린다) ㉡ 경합 가드를 유지한다(맨 `bulk_update` 로 구현하면 위반 — `WHERE` 가 `pk IN` 뿐이라 「내가 읽은 뒤 남이 바꿨다」를 못 잡는다) ㉢ 크기는 «부르는 쪽»이 정한다. `add_all` 은 열지 않는다. | 트리 68행+T37 | `ast` | principle |  | **blocker** |
| 600 | 공표 사실의 «순환»을 만들지 않는다 — A 가 발행 → B 가 듣고 발행 → A 가 듣는 고리가 있으면 위반이다. 검사는 `published_event/<event>.py` 와 `event_subscription/<event>_subscription.py` 로 **BC 간 방향 그래프**를 그려 사이클을 본다(ACL 폴더 목록만 보는 #450 은 이 경로에 안 닿는다). | 트리 5·35~37행+D35+D40+D59 | `ast` | principle |  | **blocker** |
| 601 | 구독 껍데기가 부른 유스케이스는 발행자의 `on_commit` 콜백 «안에서 같은 스레드로» 돈다 — 그 안에서 다시 사실을 발행하면 재귀가 열린다. 발행은 «한 겹»까지만 허용하고, 두 겹이 필요하면 그것은 사실이 아니라 워커의 일이다(D48 ②). | 트리 37·113행+D48+D59 | `ast` | principle |  | **blocker** |
| 602 | 실패한 리스너의 기록이 «가는 곳»을 지정한다 — `robust=True` 가 잡은 예외는 장고 기본 설정에서 `django.db.backends.base` 로거로 가고 `DEFAULT_LOGGING` 의 두 핸들러가 **둘 다 안 받는다**(`require_debug_true` · `ADMINS=[]`). 그러므로 `framework/` 가 그 로거에 핸들러를 붙이거나 브로커가 직접 관측 포트로 내보내야 하고, 둘 다 없으면 「삼키면 위반」(#525)이 실효가 0이다. | 트리 96·115행+D49+D59 | `ast` | principle |  | **검사기** |
| 603 | `broker/external/` 에 «내용»이 들어오는 순간 딸림 일곱이 함께 선다 — **하나라도 빠지면 위반**이다: ⑴ outbox(커밋과 발행을 한 트랜잭션에) ⑵ 소비자 멱등 ⑶ 봉투(`source`+`id`) ⑷ 재시도·데드레터 ⑸ 순서 보장 여부의 명시 ⑹ 직렬화 형식 ⑺ 스키마 진화 규칙. 「그건 나중에」가 이 칸에는 없다. <span>08-11 · Phase 0 린트 — 사람 몫 ⑵(소비자 멱등)는 #181 소유라 이 행에는 기계 여섯만 남는다 — `ast+`→`ast`.</span> | 트리 117행+D59 | `ast` | principle |  | **blocker** |
| 604 | `framework/` 의 계약은 «더하기»만 한다 — 기존 메서드의 시그니처·반환형을 바꾸거나 지우면 위반이다. 새 모양이 필요하면 **새 메서드를 더하고 옛 것을 남긴 뒤** 강등 절차로 걷는다. Evans 의 *“shouldn't be changed without consultation”* 을 사람의 협의가 아니라 «가산만 허용»이라는 기계 규칙으로 옮긴 것이다. | 트리 112·121행+D24+D38 | `ast` | principle |  | **blocker** |
| 606 | 강등 신호는 인자 «이름»에 의존하지 않는다 — ⑴ `framework/` 계약 메서드의 반환형이 `bool` 이면 «판정»이라 반송 ⑵ 인자 수 증가·기본값 있는 인자 등장을 센다 ⑶ 대상은 `<capability>_port.py` 하나가 아니라 **BC 가 둘 이상 import 하는 framework 파일 전부**다. | 트리 112~132행+D38 | `ast` | principle |  | **blocker** |
| 607 | `framework/` 에서 업무 판정을 하면 위반이다 — 어댑터에 건 #553 의 쌍둥이다. 중립 이름(`viewer_id`·`resource_id`)으로 갈아입어도 판정은 판정이다. **#628 의 어휘 집합으로는 «잡히지 않는다»** — 이 행이 묻는 것은 「업무 낱말이 나오나」가 아니라 「**판정을 하나**」이고, 규칙 자신이 그 사실을 축자로 적고 있다(중립 이름으로 갈아입어도). `#553` 과 같은 술어를 쓴다. | 트리 120~125행+D38+D45 | `ast+` | principle |  | **blocker** |
| 609 | 트리 140행의 «기계 판독 정의»는 `dddjango/` 아래 데이터 파일 하나가 소유하고, 문서 생성기(`docs/mkrev2.py`)가 **그것을 읽는다** — 지금은 반대로 생성기 안에 산다. 화이트리스트(#490)와 필수 목록(#488)이 같은 데이터에서 나온다. | #486~#492+D54 | `path` | principle |  | **이행** |
| 610 | 합성 경로 넷(`form/<form>_form.py` · `feature/<feature>.py` · `templates/admin/…` · `templates/<bounded_context>/…`)은 화이트리스트로 쓰기 전에 마디를 편다 — 한 행에 여러 마디가 눌려 있어 깊이가 안 맞는다(실제 노드 145개). | 트리 85~88행+D54 | `path` | principle |  | **이행** |
| 611 | 칸 유형 ③(`<>` 재등장)은 **이름만으로 못 가른다** — 같은 `<event>.py` 가 세 곳에 있다. 데이터에 «조상 스코프»를 함께 실어야 #488(고정은 항상)과 #489(`<>` 는 늦게)가 갈린다. | #491+D54 | `path` | principle |  | **이행** |
| 613 | 검사기는 `.git` 이 없다는 이유로 검사를 건너뛰지 않는다 — 지금 네 곳은 전면 면제, 세 곳은 전면 검사로 정반대이고, brownfield 면제를 폐기한 #591 과 어긋난다. | #591 | `ast` | principle |  | **검사기** |
| 614 | `framework/` 아래 각 파일은 «어느 링인가»(안쪽/바깥쪽)를 데이터로 표시한다 — 정본의 계보 컬럼(DDD/Clean/Hex/고유)은 «누가 이름 붙였나»이지 «방향»이 아니고, `framework/` 열여덟 줄에서 둘이 겹치지 않는다. D47 이 링을 파일 단위로 내린 뒤로는 이 표시가 있어야 #558 을 기계로 옮길 수 있다. | 트리 112~132행+D47 | `path` | principle |  | **이행** |
| 615 | `framework/<capability>/` 의 계약·`exception.py`·`<data>_out.py`·`<data>_in.py` 는 프레임워크 타입을 쓰지 않는다 — `from ninja import Schema` 한 줄이면 유스케이스가 그 타입을 «반환값으로» 받게 되고, `#4`(직접 import 목록)는 그것을 한 글자도 안 잡는다. Martin 축자: *“the name of something declared in an outer circle must not be mentioned by the code in an inner circle.”* | 트리 121~124행+D47+D5 | `ast` | principle |  | **blocker** |
| 616 | `framework/<capability>/<data>_out.py` 에 애그리거트가 오면 위반이다. | 트리 123행+D24 | `ast` | principle |  | **blocker** |
| 617 | `framework/<capability>/<data>_out.py` 에 업무 어휘가 한 글자라도 나오면 위반이다. | 트리 123행+D24 | `ast` | principle |  | **blocker** |
| 618 | `<data>_out.py`·`<data>_in.py` 에 `locale` 이 바꾸는 값과 채널 설정은 안 담는다. | 트리 123·124행+D24 | `ast+` | principle |  | **blocker** |
| 619 | `<data>_out.py`·`<data>_in.py` 는 원시값·값 객체로 되면 만들지 않는다. **`framework/` 는 `domain_layer/` 를 import 하지 않으므로 #228 이 여기서는 «자동으로» 성립한다 — 이 자리의 «값 객체»는 표준 타입뿐이다.** | 트리 123·124행+D24 | `ast+` | principle |  | **blocker** |
