---
name: dddjango-web-architecture-state
description: dddjango-web 상태 아키텍처 — ViewModel 3변종(VM·SharedState·Service)과 State 계약, 에러 2채널, keepAlive(세션·프로세스 수명) 결정, 합성 루트의 상태 동작 규율. 들어온 데이터가 web 안에서 화면들 사이에 어떻게 살아 있는가를 결정·검수할 때 로드한다.
user-invocable: false
---

# 상태 아키텍처

## 언제 쓰나

VM·State·SharedState·Service를 설계·작성·검수할 때, 에러 표시 경로·상태 수명·공유 범위를 결정할 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 파일·폴더·명명·import 매트릭스·4채널 닫힌 열거 **사실** → `dddjango-web-discipline-houserules`
- 데이터가 web 바깥과 오가는 방식(Either 계약·safe_api_call) → `dddjango-web-architecture-data`
- view/section/widget 3단 판별·dumb 규율 → `dddjango-web-architecture-ui`
- UseCase 명명·판정 소유·강등 → `dddjango-web-architecture-ddd`
- VM·HTMX 갱신·frozen dataclass **표기법** → `dddjango-web-implementation-htmx`·`dddjango-web-implementation-python`

**keepAlive 경계**: 수명 *결정*(어느 변종·언제 세션·프로세스 수명인가)은 이 스킬 소유, 세션 보관·시그널 연결 *표기법*은 dddjango-web-implementation-htmx 소유.

## 핵심 운영 원칙

- ViewModel 3변종은 *상태의 수명*과 *구동원*으로 가른다: VM=화면 1개·View 요청, SharedState=화면 N개·여러 VM/View, Service=web 전역·비화면 이벤트(시그널·비화면 요청) (§1)
- VM·SharedState·Service는 Model 방향으로 UseCase만 호출한다 — Repo·DataSource·SDK 직접 호출 금지, 위임 한 줄짜리 UseCase도 정상 (§1)
- VM은 도메인 엔티티·패키지 타입을 직노출하지 않고 항상 자기 frozen dataclass State를 노출한다 — 액션 전용 VM도 error 필드 1개짜리 최소 State (§3)
- 에러는 2채널뿐: 조회 실패는 build()가 raise(→ view가 잡아 같은 section을 `load_error`·`retry_href` 맥락으로 — 루트 id 유지), 액션 실패는 State의 error 필드 + 그 응답 조각이 `is_show` 존중해 표시 — error를 세션에 남기지 않는다(응답 하나가 소비 단위) (§4)
- base VM·공용 헬퍼를 만들지 않는다 — §4 정식 예제를 그대로 반복한다 (§2·§4)
- `HttpRequest` 보유 금지(전환은 navigator 경유 href)·요청 입력 읽기는 View 소유(값은 VM 메서드 인자) (§2)
- SharedState는 세션 수명(keepAlive 자리)+명시적 reset, 과거형 사건명(`_added` 류) 금지 — 상태로 위장한 이벤트다 (§5)
- 타 BC SharedState·VM 접근 금지 — 필요하면 그 BC UseCase 호출 또는 view 임베드. root만 면제 (§7)
- 교차 갱신 버스(전역 갱신 이벤트 류)는 폐지 — 데이터 변화는 그 BC SharedState(`HX-Trigger`), 요청·세션 수명발 갱신은 root handler→BC service (§8)
- root_vm은 "거의 빈 VM"(context processor), handler들은 Service 변종(Django 연결 지점에 등록), initializer는 부수효과만 — 시동 질문은 root_vm이 UseCase 재조회 (§10)

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 이 상태는 VM·SharedState·Service 중 어디인가, data와의 경계는 | [`references/final.md`](references/final.md) §1 |
| VM이 해도 되는 일·금지(HttpRequest·입력 읽기·DI) | final.md §2 |
| State 모양 — frozen dataclass 계약·최소 State·직노출 금지 | final.md §3 |
| 에러를 어떻게 표시하나 — 2채널·정식 예제 | final.md §4 |
| 화면 간 공유 상태 — 세션 수명·reset·사건명 금지 | final.md §5 |
| 비화면 이벤트를 받는 코드 — 능동/수동·알림 분업 | final.md §6 |
| 타 BC의 상태가 필요할 때 | final.md §7 |
| 화면 갱신·스크롤톱 요구가 올 때 | final.md §8 |
| keepAlive(세션·프로세스 수명)를 쓸지 결정 | final.md §9 |
| root_vm·handler·initializer·게이트의 상태 동작 | final.md §10 |
| 판별이 갈리는 경계 사례(handler 입장·거의 빈 VM·common 상태·과거형 사건명) | 공유 reference `undecidable.md` §5·§6·§7·§10 (dddjango-web-discipline-houserules 동봉) |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
