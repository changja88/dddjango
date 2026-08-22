# 기계 판별 불가 6종 — 판별 절차·에이전트 배정

> **지위**: 백스톱(결정적 러너)이 못 보는 **의미 판별**의 단일 출처. 백스톱 = 사후 불변식(위반 검출), 이 문서 = 판별 절차(배치 결정). **1차 결정자와 검증자가 같은 이 파일을 적재한다** — 두 에이전트가 다른 기준으로 판정하면 반송 루프가 생긴다.
> 구성: 배정표 6행 = 판별 6종. 각 절 = 배정 → 절차 → 신호.

| § | 판별 | 1차 결정 | 검증 |
|---|---|---|---|
| 1 | view/section — "상태 조립이 필요한가" | design-architect-web (화면 분해) | design-review-web → discipline-reviewer-web |
| 2 | section "화면 전속" — 화면 state의 맥락을 아는가 | design-architect-web | design-review-web |
| 3 | widget ↔ design_system — BC 어휘 보유 | design-architect-web | design-review-web → discipline-reviewer-web |
| 4 | 영역 귀속 — 화면이 어느 `<screen_area>`인가 | Coordinator (G0 — 경계 곤란 시 **사용자 판정**) | design-review-web → discipline-reviewer-web |
| 5 | "두 번째 개념" 식별 · "같은 개념 같은 철자" | design-architect-web (파일 목록 소유) | discipline-reviewer-web (coder-web은 구현 중 2차 발견자) |
| 6 | base "거의 빈" — base.html 입장 | design-architect-web | design-review-web → discipline-reviewer-web |

---

## §1. view/section — "상태 조립이 필요한가"

**절차**: 그 UI 조각에 **자기 표시 상태의 조립**(client 호출·표시 판정·상태 dataclass)이 필요한가? 필요하면 — 전체 페이지든 HTMX로 갈아 끼우는 조각이든 — **view**다: 삼총사(`_view.py`·`_view_model.py`·`_state.py`) + 페이지 템플릿으로 생성하고, fragment 진입점도 그 view가 소유한다. 필요 없으면 — 받은 state 렌더만으로 성립하면 — **section**이다.

**신호**: section으로 두려는데 ⓐ 템플릿 조건 분기가 표시 *판정*으로 자라고 ⓑ 부모 state에 그 조각 전용 필드가 늘고 ⓒ 자기 데이터 조회가 필요해진다 → view 승격 신호이지 예외가 아니다. 반대로 state 렌더만으로 성립하면 view로 승격하지 않는다(불필요한 삼총사 양산 금지). 승격·이동 절차는 architecture-web §5.

**판례 — 정적 화면**: 상태 조립이 필요 없는 독립 페이지(약관·안내)는 view+페이지 템플릿만으로 허용한다 — 빈 VM·빈 state 파일을 채우지 않는다(종류 4폴더 골격은 완비하되 파일은 만들지 않는다 — final.md §3·§4).

## §2. section "화면 전속" — 화면 state의 맥락을 아는가

**절차**: 그 조각이 소속 화면의 **state 필드나 맥락**(화면 고유 상황 가정)을 아는가? 알면 **section**(소속 view 접두 필수), 모르면 — 표시값·원시값만 받으면 — **widget 후보**다(§3으로).

**신호**: section이 **두 번째 화면**에서 필요해지면 화면 state 의존을 벗겨 widget으로 이동. widget이 화면 state를 통째로 받기 시작하면 section으로 오배치된 것.

## §3. widget ↔ design_system — BC 어휘 보유

**절차**: **import가 없어도** 이름·문자열·주석·컨텍스트 변수에 백엔드 BC의 도메인 개념이 등장하면 그 어휘를 "보유"한다. 보유하면 **widget**(영역 수준) — design_system 입장 불가. 보유하지 않으면 — 수식·변형만 남은 순수 시각 부품이면 — **design_system/component**다.

**신호**: component 파일명·변수명에 도메인 명사(order·member 류)가 등장 → widget으로. widget에서 도메인 어휘가 빠지고 수식·변형만 남으면 component 승격 후보(절차는 architecture-web §5).

## §4. 영역 귀속 — 화면이 어느 `<screen_area>`인가

**절차**: 영역은 **내비게이션 단위**다 — 화면이 전역 내비에서 어느 묶음으로 노출되는가로 귀속한다(도메인 경계·백엔드 BC 경계가 아니다). 경계가 곤란하면(후보 영역 2+ 또는 전역 내비 미노출) **Coordinator가 G0 배너에서 배치축 3선택을 평이한 말로 표면화해 사용자가 판정한다**: ① **새 영역 신설** / ② **기존 〈영역〉에 포함** / ③ **모르겠다 — 설계자가 정함**. 에이전트는 영역을 자기 판단으로 발명하지 않는다. **③ 판정 시에는 설계자 결정이 곧 판정이다** — design-architect-web이 영역을 정해 명세에 명시하고, 검증자는 이를 판정 부재로 취급하지 않는다.

**검증**: design-architect-web은 판정을 명세의 파일 경로에 그대로 반영하고(스스로 뒤집지 않는다 — ③ 위임 시에는 자신의 결정을 명세에 명시한다), design-review-web·discipline-reviewer-web은 "G0 판정(③ 위임 포함) 없는 새 영역 경로" 또는 "판정과 어긋난 경로"를 반송한다.

**신호**: 영역 쪽 — 전역 내비에 독립 진입 묶음이 생긴다. 기존 영역 쪽 — 기존 영역 화면의 흐름 안에서만 도달한다(목록→상세·수정 류).

## §5. "두 번째 개념" 식별 · "같은 개념 같은 철자"

**절차**: "개념"의 단위는 **화면**이다 — 파일 수가 아니라 **다른 화면 개념의 등장**(별도 진입 URL·별도 표시 상태 묶음)이 트리거다. 같은 개념은 위치가 달라도 **같은 철자(어순 포함)** — `.py`·템플릿·urls name 전부에서 동일하다(`order_list` ↔ `list_order` 혼용 금지). 등장으로 판별된 개념의 배치 사실(새 `<view>/` 폴더 — 기존 화면 폴더 증축 아님)은 final.md §2 소유다.

**배정 특칙**: 1차 결정은 **design-architect-web**(명세의 파일 목록 소유 — 자기모순 스캔에 포함). **coder-web은 구현 중 2차 발견자** — 명세에 없던 두 번째 개념을 발견하면 임의 분할하지 말고 디렉터리 대조 후 보고한다.

**신호**: 한 화면 폴더의 section들이 서로 다른 진입 URL에서만 쓰인다 / state가 무관한 두 묶음으로 갈라진다 / 한 view 파일이 두 페이지 진입점을 소유하기 시작한다.

## §6. base "거의 빈" — base.html 입장

**절차**: base.html에 오는 것은 **공통 문서 골격**(head·tokens.css·vendored htmx 로드)·**내비 셸**·**전역 게이트**(전 화면 공통 차단·안내 요소 — 점검 배너 류)뿐이다. **화면 어휘 금지** — 특정 화면·특정 BC의 이름·문자열·분기가 base에 보이면 그 조각은 base 소속이 아니다: 화면 전속이면 그 화면 section, 영역 재사용이면 widget, 순수 시각이면 design_system/component.

**신호**: base.html에 특정 화면에서만 참여하는 블록·조건 분기가 는다 / base가 특정 화면의 state를 전제한다 / 내비에 도메인 데이터 표시(뱃지·카운트 류)가 필요해진다 — base가 조회하지 말고 그 데이터를 소유할 view를 정해 HTMX 조각으로 끼운다.

**판례 — 전역 게이트**: 전 화면 공통 차단·안내(점검 배너 류)만 base의 전역 게이트다. 특정 영역·특정 화면에서만 요구되는 차단은 그 화면의 view가 소유한다 — base에 화면별 분기를 얹지 않는다.
