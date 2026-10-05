# 기계 판별 불가 18종 — 판별 절차·에이전트 배정

> **지위**: 백스톱(결정적 러너)이 못 보는 **의미 판별**의 단일 출처. 백스톱 = 사후 불변식(위반 검출), 이 문서 = 판별 절차(배치 결정). **1차 결정자와 검증자가 같은 이 파일을 적재한다** — 두 에이전트가 다른 기준으로 판정하면 반송 루프가 생긴다.
> **출처**: 본설계 §9(배정표)·파이널 리뷰 §6(목록)·제1 규약(절차 원문). 본문 속 `(규약 §N)`은 출처 표기다.
> 구성: §1~§13 = 배정표 13행, 판별 18종 — 행별 종수: §3=3종·§6=2종·§8=2종(domain_service "중심"·UseCase "도메인 개념 단위" — "domain 기본"은 판별이 아니라 전제)·§9=2종, 나머지 9행 각 1종, 합 18. 각 절 = 배정 → 절차 → 신호·판례.

| § | 판별 | 1차 결정 | 검증 |
|---|---|---|---|
| 1 | view/section ("VM이 필요한가") | architect (화면 분해) | ui → discipline-reviewer |
| 2 | "맥락" 판단 (section 화면 전속) | architect | ui |
| 3 | BC "어휘" 보유 · 귀속 tie-break · 조립 vs 다수 BC 투영 | architect (BC 배치) | ddd |
| 4 | "BC 어휘 없는 게이트" (root scaffold) | architect | ddd |
| 5 | handler 입장 ("2+ BC 분배") | architect | state |
| 6 | "거의 빈 VM" (root_vm) · 외부 진입 "정규화" 의미론 | architect | state → discipline-reviewer |
| 7 | common "살아있는 상태" | architect | state → discipline-reviewer |
| 8 | 판정·계산의 귀속 — domain 기본 · domain_service "중심" · UseCase "도메인 개념 단위" | architect | ddd → discipline-reviewer |
| 9 | "두 번째 개념" 식별 · "같은 개념 같은 철자" | architect (파일 목록 소유) | discipline-reviewer (coder는 구현 중 2차 발견자) |
| 10 | 과거형 사건명 (형태소) | architect (파일명은 명세 결정) | state → discipline-reviewer |
| 11 | `apps.py`·`urls.py` "최소형" | coder | discipline-reviewer |
| 12 | '계약 위험 행위' 표기 (신규 — tracer 앵커) | architect (명세 결정 항목) | data |
| 13 | 접두↔area — BC 이름 접두가 그루핑 축인가 도메인 어휘인가 (feedback-031) | Coordinator (G0 감지·**사용자 판정**) | ddd → discipline-reviewer |

---

## §1. view/section — "VM이 필요한가"

**절차** (규약 §3.5 판별 1): 그 UI 조각에 **자기 상태·로직**이 필요한가? 필요하면 — 전체 화면이든 임베드 조각이든 — **view**다: 삼총사(`_view`·`_vm`·`_state`)로 생성한다. 버튼 하나여도 동일하다(HaffHaff 선례: `chat_request_btn_view`+`chat_request_btn_vm`).

**신호**: section으로 두려는데 ⓐ include 인자·href가 비대해지고 ⓑ 부모 State에 그 조각 전용 필드가 늘고 ⓒ 조각이 자기 데이터를 스스로 불러야 해진다(VM 호출·자기 조각 응답 URL) → 승격 신호이지 예외가 아니다. 반대로 include 인자·href만으로 성립하면 view로 승격하지 않는다(불필요한 VM 양산 금지).

## §2. section "화면 전속" — "맥락"을 아는가

**절차** (규약 §3.5 판별 2): 그 화면의 **State 타입이나 맥락**(화면 고유 상황 가정)을 아는가? 알면 **section**(소속 화면 접두 필수), 모르면 — 엔티티·원시값·href만 받으면 — **widget** 후보(§3.5 판별 3: BC 도메인을 알면 widget, 그것도 모르면 design_system).

**신호**: section이 **두 번째 화면**에서 필요해지면 화면 State 의존을 벗겨 widget으로 이동. widget이 화면 State를 받기 시작하면 section으로 오배치된 것.

## §3. BC "어휘" 보유 · 귀속 tie-break · 조립 vs 다수 BC 투영

**어휘 보유** — import가 없어도 이름·문자열·주석에 BC의 도메인 개념이 등장하면 그 BC 어휘를 "보유"한다. 보유하면 common·design_system·root scaffold 입장 불가.

**화면 귀속 tie-break** (규약 §3.6 — 위에서부터, 처음 해당하는 것이 답):
1. VM이 호출하는 UseCase가 **한 BC** → 그 BC.
2. UseCase가 **둘 이상의 BC** → 그 화면(기능) 이름의 **일반 BC** (예: 피드 `home_view` → `home` BC).
3. UseCase **0개**(정적 화면) → import하는 도메인 어휘의 BC → 그것도 없으면 진입 URL을 소유한 BC.
4. 루트 스캐폴드·전 BC 배선·시동 → `root_*`.

**조립 vs 다수 BC 투영**: 탭 프레임·전역 게이트처럼 **BC 어휘 없는 프레임**만 root(조립)다. 여러 BC의 콘텐츠를 **그리는** 화면은 root가 아니라 자기 이름의 일반 BC — 도메인이 비어도 표준 골격 그대로 정상.

## §4. "BC 어휘 없는 게이트" — root scaffold 입장

**절차** (규약 §3.6): scaffold에 오는 화면은 **도메인 어휘가 0인 web 전역 차단 화면뿐**이다 — 점검 모드 류. 화면 문안·분기 조건·이동 목적지 어디에든 도메인 어휘가 보이면 BC로 보낸다.

**신호**: scaffold 화면이 특정 BC의 UseCase를 호출하기 시작하면 입장 오판 — 아니면 "정크드로어 셸"(HaffHaff `home`)이 scaffold라는 이름으로 재발한다.

## §5. handler 입장 — "2+ BC 분배"

**절차** (규약 §3.6): 그 이벤트가 **둘 이상의 BC(또는 URL 조립 전체)로 분배**되는가? 그렇다면 root handler(`root_<이벤트원>_handler`). **한 BC의 도메인 반응**이면 그 BC의 `application_layer/service/`다.

**판례** — 같은 알림이라도: 알림 링크 진입(목적지 분배) = `root_destination_handler` / 수신 처리(비화면 요청·시그널로 오는 알림의 저장 등) = 알림 BC의 service. 사후 근사: 그 코드가 import하는 BC 수를 세면 2+면 root 쪽 신호(근사일 뿐 — 1 BC import여도 URL 조립 전체 분배면 root). 경로 사실: root handler는 `root/handler/root_<이벤트원>_handler.py`(houserules final.md §1 트리).

## §6. "거의 빈 VM" (root_vm) · 외부 진입 "정규화"

**root_vm 절차** (규약 §3.6): root_vm은 **탭·뱃지·점검 안내 같은 web 전역 표시 상태만** 갖는다(탭별 마지막 경로는 `RootRequestHandler.process_view`가 세션 `root.tab_last`에 적고, root_vm은 그 기록으로 탭 href만 만든다 — 그보다도 가볍다. 탭 href 규칙은 architecture-state §10). 특정 도메인 기능이 자라기 시작하면 그 화면은 root가 아니다 — §3 tie-break로 재판정.

**외부 진입 정규화 절차** (규약 §3.6): 외부 진입 payload(알림 링크·외부 콜백의 목적지 정보)→**BC URL 변환**과 수신은 root_destination_handler 소유("어떤 payload가 어느 화면인가"는 전 BC 목적지 지식). 디스패치 수단은 그 URL로의 **redirect 하나** — 타 BC navigator 호출·BC service에서의 redirect는 위반. "정규화"의 판정 기준: 변환 결과가 **각 BC URL path 문자열**이면 정규화, BC별 분기·enum 스위치가 남아 있으면 미정규화.

## §7. common "살아있는 상태"

**절차** (규약 §6): common은 호출당하는 도구이지 행위자가 아니다. 상태 동작(시그널 수신·세션 쓰기) 금지는 백스톱 proxy일 뿐 — proxy가 못 잡는 **가변 모듈 전역**(세션 키 보관자 류)도 ⓐ 변경 통지·구독을 노출하거나 ⓑ BC가 그 변화를 "듣기" 시작하면 common 실격. 정체를 따져 제자리로: BC 어휘가 있으면 그 BC `shared_state/`, 전 BC 배선이면 root handler.

**신호**: common 코드에 Django `Signal`·콜백 리스트·`HX-Trigger` 발행이 자라남 / "변경 시 알림" 요구 등장. 단순 read/write(요청 단위 contextvar·전역 설정 읽기)는 합법 — 듣는 자가 생기는 순간이 경계다.

## §8. 판정·계산의 귀속 — domain 기본 · domain_service "중심" · UseCase "도메인 개념 단위"

**전제** (규약 §3.3 — 반송 시 인용 조문): **도메인 어휘로 진술되는 판정·계산은 1곳째부터 domain이 기본**이다 — VM의 일은 변환이지 판정이 아니며, VM 소유를 주장하려면 *왜*를 적는다. 판정 소유·강등 규칙의 상세는 architecture-ddd §5 소유 — 이 절은 domain 안에서의 *귀속처* 판별만 다룬다.

**domain_service 귀속 절차** (규약 §3.2): **한 애그리거트 안**의 판정·계산은 그 애그리거트의 메서드가 기본이다. **여러 애그리거트에 걸치는 순수 판정·계산**은 판정 대상(주어) 애그리거트의 `domain_service/`에 귀속한다 — 판정형("X가 ~할 수 있는가")과 계산형("X의 ~은 얼마인가") 모두 동일하며, 주어는 그 규칙이 **누구의 속성·정책인가**로 식별한다(등급별 할인율이면 할인 정책의 주체인 등급·멤버십 쪽). **흐름 조율**(여러 판정·호출의 순서)은 UseCase의 일 — 공용 위치 없음. specification 동일 규칙.

**UseCase 명명 절차** (규약 §7.1-4): UseCase는 화면이 아니라 **도메인 개념 단위** — 여러 VM이 하나의 UseCase를 공유한다. 신호: `<화면>_use_case.py`가 생기거나, 같은 도메인 개념의 UseCase가 화면 수만큼 늘면 오판. 화면 1개 전용 흐름이어도 이름은 개념으로 짓는다(소비처 수는 명명 근거가 아니다).

## §9. "두 번째 개념" 식별 · "같은 개념 같은 철자"

**절차** (규약 §4): application·presentation_layer에서 **두 번째 개념**이 등장하는 시점에 개념 1차로 분할한다. "개념"의 단위는 애그리거트·feature 묶음이다 — 파일 수가 아니라 **다른 도메인 묶음의 등장**이 트리거. 분할 시 기존 직속 종류 폴더는 동결(신규 파일 금지). 같은 개념은 계층이 달라도 같은 철자(어순 포함).

**배정 특칙**: 1차 결정은 **architect**(명세의 파일 목록 소유 — 자기모순 스캔에 포함). **coder는 구현 중 2차 발견자** — 명세에 없던 두 번째 개념을 발견하면 임의 분할하지 말고 디렉터리 대조 후 보고한다.

## §10. 과거형 사건명 (형태소)

**절차** (규약 §3.3·§8): `shared_state/` 파일·클래스명에 **과거형 사건 형태소**(`*_added`·`*_completed`·`*_received` 류) 금지 — 상태로 위장한 이벤트다(HaffHaff `comment_added_bridge` 실측: DateTime 핵·센티널 초기값·autoDispose 유실). 공유 **상태**는 명사 관심사(`<관심사>_shared_state`)로 짓는다.

**신호**: 이름이 "무엇이 일어났다"를 서술 / 값이 시각·카운터 핵 / 소비자가 값을 읽지 않고 변화 자체에만 반응. 이벤트형 요구가 진짜면 설계 반송(도메인 이벤트는 dddjango-web 비채택 — 트리거 시 재논의 항목). 개명 가이드: 소비자가 **읽는 현재 상태**를 명사로 — 좋아요·댓글 반응이면 `<대상>_interaction`, 필터면 `<대상>_filter` 류. 유일 정답일 필요는 없다 — 과거형 형태소만 없으면 적법(검증 가능·생성 비결정 허용).

## §11. `apps.py`·`urls.py` "최소형"

**절차** (규약 §3.6): `web/apps.py`는 `WebConfig.ready()`의 `root_initializer` 시동, `web/urls.py`는 `root_router`의 urlpatterns 내보내기 **만**. 위반 신호: 시동 로직 직접 수행(→ `root_initializer`), URL 분기 조립(→ `root_router`), 전역 인스턴스 보유(logger → common), BC import, **전역 에러를 `root_error_handler`로 위임하지 않고 침묵 삼키는 빈 핸들러**(`except Exception: pass` 류·final.md §7 반송표). 1차 판정자가 **coder**인 유일한 행 — 엔트리포인트는 명세가 아니라 구현 단계에서 자라기 때문이다.

## §12. '계약 위험 행위' 표기 — tracer 앵커

**절차** (본설계 §5-2·§9): 스냅샷(동결된 서버 계약)·기존 DataSource 패턴으로 **확인 불가한 의미 가정**이 걸린 행위를 명세에 `계약 위험`으로 표기한다 — 예: 문서에 없는 필드 의미 추정, 페이지네이션 방식 가정, 에러 코드 의미 가정. 이 표기는 tracer(가장 위험한 경로 선행 구현) 발동의 **기계 앵커**다.

**판정 기준**: "이 행위가 틀렸다는 것을 컴파일·백스톱·스냅샷 대조 중 무엇도 못 잡는가?" — 그렇다면 계약 위험. 검증자는 **data 리뷰어**: 명세의 행위 목록을 훑어 표기 누락(가정인데 미표기)과 과잉(스냅샷에 있는데 표기)을 본다.

## §13. 접두↔area — 그루핑 축인가 도메인 어휘인가

**절차** (feedback-031 — area 규칙 본문은 houserules final.md §1 area 핵심 사실): 동일 접두(BC명의 첫 `_` 앞 토큰 — `_` 없으면 BC명 전체) BC가 2개 이상이면 그 접두는 area 후보다. 그러나 접두가 **역할·서브도메인 축**(예: `driver_*`/`rider_*` — web 셸이 갈리는 사용자 역할)인지 **도메인 어휘**(예: `chat`/`chat_request` — 한 기능 군집의 개념 연쇄)인지는 기계가 못 가른다. **판정은 사용자가 한다**: Coordinator가 G0 배너 직전 결정적으로 감지해(기존 BC 목록 조회 + `.dddjango-web/config.json`의 `area_prefixes` 기판정 스킵) G0 배너에 질문으로 표면화하고, 판정을 `area_prefixes`에 `"<접두>": "area" | "not-area"`로 영속한다 — `not-area`는 자동 감지의 재질문만 억제하고 사용자 명시 선언은 항상 우선한다. 에이전트는 area를 자기 판단으로 발명하지 않는다.

**신호**: area 쪽 — 접두 그룹별로 root 라우팅에서 별도 셸이 분기 · 접두가 사용자 역할/web 모드와 일치. 도메인 어휘 쪽 — 접두 BC 하나가 다른 접두 BC의 UseCase를 상시 호출(한 기능의 개념 연쇄) · 접두가 명사구의 수식어(`order`/`order_return`).

**검증**: architect는 스코프 메모의 판정을 명세 파일 경로에 그대로 반영하고(스스로 뒤집지 않는다), ddd 리뷰어·discipline-reviewer는 "판정 없는 area 경로" 또는 "판정과 어긋난 경로"를 반송한다.
