# dddjango-web 테스트 규율 — 회귀 안전망·단언 FORM

> **출처:** 테스트 피라미드 정전(martinfowler.com — "many unit tests ... fewer broad-stack tests")·Django 테스트 문서(docs.djangoproject.com/en/stable/topics/testing — 테스트 클라이언트)·pytest(docs.pytest.org — `assert` 재작성·`pytest.raises`)·pytest-django(`client`·`live_server`)·Beautiful Soup(`select` CSS 선택자)·Playwright for Python(`get_by_test_id`·`to_have_count`)·Martin Fowler(Eradicating Non-Determinism·test behaviors not implementation)·업계 합의(SWE@Google·dcm.dev) — dddart 테스트 규율(2026-06-17 확인 · dddart 5차 양판 라이브런 FC-2 vacuity·FC-1/3 색충돌·codex 디코이 트리거)의 web 이식.
> 본문 속 `(검증 §N)`은 dddart 작업장 자료조사(`workspace/design/2026-06-17-test-strategy-design.md`)의 출처 표기이며 로드 대상이 아니다. Django·브라우저 테스트 메커니즘·결정성·더블은 implementation-test, 판정 소유는 architecture-ddd로 위임한다.

---

## 목차

- §1. 목적 — 회귀 안전망·무게중심·날짜 결정성
- §2. 오라클을 명세에서 끄는 법 — 비-vacuity 자가점검
- §3. 단언 FORM — 디코이-불가 4형 + 도메인 양갈래
- §4. 무엇을 생략하나
- §5. red일 때 — 반송·reviewer FORM-감사

---

## §1. 목적 — 회귀 안전망·무게중심·날짜 결정성

dddjango-web이 만드는 코드는 파이프라인이 이미 생성한다 — 테스트는 그 코드를 *짜는* 드라이버(TDD)가 아니라 **이미 생성된 명세-정확 코드를 차후 수정으로부터 지키는 회귀 안전망**이다. 실사용처는 *수정 모드*다: 누군가 나중에 이 코드를 고칠 때 명세가 정한 행위가 깨지면 red가 울려야 한다.

- **가두는 대상은 명세이지 현재 코드가 아니다.** 기대값을 *명세*에서 끌면 안전망, *구현*에서 베끼면 디코이(코드가 틀려도 같이 틀린 채 green)다. 버그 상태를 가두면 디코이, 아무것도 안 가두면 헛테스트(vacuous).
- **무게중심 = thick domain** (테스트 피라미드 정전: "많은 unit + 핵심을 덮을 만큼의 화면·브라우저 테스트" — unit이 maintenance·speed 우위). 비중 순서:
  - domain 판정·UseCase·Either 양갈래 — **두텁게**(가장 결정적·가장 싸다).
  - state·VM 상태 전이·정렬/필터/매핑 — 중간.
  - UI는 **핵심 행위만 얇게**(탭→이동·슬롯 표시) — 템플릿 마크업 *형태*는 테스트하지 않는다(§4).
- **정렬·구별은 도메인 판정이다** — VM 변환이 아니라 도메인에서 두드린다(판정 소유는 architecture-ddd §5). 목록 색 구별·날짜 정렬을 VM 테스트로만 덮으면 판정이 위층으로 샌 것을 테스트가 묵인한다.
- **날짜 결정성**: 도메인 판정은 *기준일을 인자로 받는 순수 함수*로 두고 테스트는 고정 날짜를 주입한다. `datetime.now()`·`timezone.now()` 실시각에 의존하는 테스트는 pre-commit에서 *무관한 날*에 깨진다(테스트 수행 시각에 통과 여부가 달라지면 안 된다). '지금'이 실제로 필요한 edge는 VM 생성 인자·함수 인자로 격리한다 — 주입 메커니즘은 implementation-test §5.

**영구 시험 재현성**: `web_test/`·호스트 시험 트리와 시험 지원 코드(`conftest.py`·`_support.py` 등)는 `.dddjango-web/`를 읽거나 쓰지 않고 프로젝트 루트 밖 머신 고정 고정물·기준판·캐시에 기대지 않는다. 기록 폴더(`.dddjango-web/`·`.dddjango/`)에 둔 시험 원문 사본은 영구 시험이 아니다 — 그 사본을 영구 시험으로 옮겨 오면 새 시험으로 본다. 고정물·기대 자료는 시험 트리에, 실행 기록은 `tmp_path` 등 임시 폴더에 둔다. 선택 도구 부재는 호스트 규칙대로 skip하고 설치된 도구의 고장은 실패로 남긴다. 레인 전용 환경 변수 존재 단언으로 실행 전제를 만들지 않는다 — 정상 환경 변수 행위 시험·필수 settings는 허용하며 환경 변수 의미 판정은 TG2 밖, discipline 감수와 G2 표준 실행이 확인한다.

**기존 시험 전환의 보존**: 슬라이스 0에서 시험을 바꾸더라도 전후에 **같은 계약 · 같은 실패**를 보호해야 한다. 메서드 이동은 승인 행에 적힌 함수의 해당 메서드 자리만 대응시키고 단언·입력·patch 대체값·옵션·대응 밖 AST는 보존한다(하우스룰 §8). 시험이 부르는 함수 자체를 바꿔야 하면 별도 본인 승인 뒤 제품을 고정한 0T에서 그 함수의 준비·호출·전용 import만 바꾼다 — 단언·decorator·parametrize·수집 조건·patch/mock의 순서와 위치는 고정한다. 대상은 web/ 밖 시험 파일의 최상위 함수다(클래스 안 시험·`with pytest.raises` 안의 행위·모듈 머리 import를 고쳐야만 도는 전환은 0T로 받지 못한다). 같은 단언을 유지한 채 응답을 직접 만들거나 mock 응답을 읽거나 입력을 바꿔 보호 분기를 건너뛰면 보존이 아니다. 보호 실패마다 보호 분기 안만 최소로 깨는 반례를 두고, 정상 제품의 새 시험과 옛 시험이 case마다 수집·실행·통과하며 같은 반례에서 옛/새 시험이 시험 함수 자신의 같은 순번 `assert` 문(k)에서 난 AssertionError로 실패해야 한다(`.assert_*()`·도움 함수·제품 안에서 난 AssertionError는 같은 단언 실패로 세지 않는다). 공통 부분만 깨는 반례로 새 시험의 관문·분기 우회를 숨기지 않는다. 수집/import 오류·skip·xfail·수집 0·시간 초과·요동은 미검증이며 통과가 아니다. 값 잎 보존은 동등성 증명이 아니고 입력 대응·같은 관문/분기·최소 반례·단언이 같은 객체를 읽는가는 감수가 확인한다. 결정적 도구 검증과 0T 감수 B 0 뒤에만 전환된 시험을 고정해 0C로 제품을 정리하며 실패하면 취소·ⓐ 재상정 STOP이다. 기존 실패를 새 판정이나 약한 단언으로 바꾸는 권한은 이 전환에 없다.

## §2. 오라클을 명세에서 끄는 법 — 비-vacuity 자가점검

**2단계 오라클**: ① 코드를 보지 않고 *명세*에서 기대값을 추출한다(이 화면은 날짜 오름차순·최고기온은 위 슬롯·탭하면 그 항목 날짜가 상세로). ② 그 기대값으로 단언한다. 구현을 열어 기대값을 베끼면 — LLM이 테스트를 생성할 때의 *구현-미러링* 경향(Fowler·업계 합의) — 코드의 버그가 그대로 오라클에 복사돼 디코이가 된다(dddart 5차 codex가 색 충돌을 "정답"으로 단언한 경로).

**비-vacuity 자가점검**(작성·검수 공통): "이 단언이 의존하는 로직을 머릿속으로 *한 곳* 깨봤을 때 red가 되는가?" — '아니오'면 단언이 행위를 안 두드린 헛테스트다. 존재(테스트 1개)만으론 닫히지 않는다 — §3의 디코이-불가 FORM으로 교체한다. (기존 implementation-django §7에 있던 "머릿속으로 깨봤을 때 red" 자가점검을 *FORM 선택 규율*로 격상한 것이다 — 그 §7 테스트 표기는 discipline-test·implementation-test로 이전됐다.)

## §3. 단언 FORM — 4형 + 도메인 양갈래(보강)

단언 *형태*로 디코이를 막게 고른다. **단 형태만으로 디코이가 *불가*한 건 §3.1(집합 크기)뿐이고, §3.2~§3.4·§3.6(매핑)은 coder가 이 형태를 쓰는지에 실효가 달린 *가이드*다**(§5·정직). 각 FORM은 dddart 5차 양판 실패 1건을 직격한다. **셋업은 dddjango-web no-DI seam을 따른다**(repo/usecase 주입 자리는 dddjango-web에 없다 — Repo·UseCase는 직접 생성): 판정(구별·정렬·도메인 양갈래)은 *순수 도메인 단위를 직접* 호출하고, view 행위(위치·탭)는 *VM 대체*로 통제된 State를 주입한다(seam·헬퍼 계약은 implementation-test §2·§7). 여기선 *단언 형태*가 초점이다.

### §3.1 구별(distinctness) — 집합 크기 FORM  *(FC-1·FC-3 색 충돌 직격)*

충돌하면 집합이 줄어 **자동 red**. 디코이로 못 쓴다 — 충돌을 "정답"이라 단언하려면 길이를 N 미만으로 적어야 하는데 그건 명세 N과 어긋나 리뷰에서 드러난다(codex가 `clear == cloudy == secondaryContainer`를 "distinct"로 단언한 디코이가 *이 형태에선 작성 불가*).

```python
def test_condition_list_colors_are_distinct() -> None:
    colors: set[str] = {weather_list_color(condition) for condition in WeatherCondition}
    assert len(colors) == len(WeatherCondition)  # 충돌 → 집합 축소 → 자동 red
```

**판정단위는 명세/골든이 정한 구별 축(색·아이콘·코드·라벨 등) *단독* N-distinct로 고정한다**(예: weather는 색 단독 — 그래야 5차 색충돌을 형태로 막는다). **여기서 N은 case 수가 아니라 골든이 정한 *고유값* 수다** — 골든/디자인이 둘 이상의 case에 같은 값을 의도적으로 배정하면(예: 두 분류가 같은 색을 공유) 그 축의 N은 case 수보다 작다. 위 예제의 `len(WeatherCondition)`는 case마다 값이 다른 흔한 경우일 뿐이고, 값이 묶이면 묶인 만큼 작은 N으로 고정한다 — case 수를 N으로 박으면 *의도된* 값 공유를 red로 오판한다(이때 매핑 정확성은 §3.6이 따로 본다). **단 N을 case 수보다 낮추려면 골든/명세가 그 공유를 *명시*해야 한다** — 코드에서 같은 값이 관찰된다는 이유만으로 N을 낮추지 않는다(그건 5차식 *미의도* 충돌이며 §3.1이 자동 red로 잡아야 할 결함이다). 여러 축의 *쌍*(예 `(아이콘, 색)`)의 set으로 단위를 바꾸면 한 축이 충돌해도 다른 축이 달라 통과하는 우회가 생긴다 — 명세/골든이 단일 축을 정했으면 그 축만 set으로 모은다. 명세가 명시적으로 다축 쌍 단위를 정한 경우에만 튜플의 set을 쓴다(단위 *선택*은 별도 eval 트랙·grader A13).

색 매핑이 `ui_extension`에 살면(architecture-ui §5 — 색·아이콘 매핑의 *유일한 자리*) `weather_list_color`가 그 템플릿 필터 함수다 — 이 거주는 정당하므로 discipline-reviewer는 이를 판정 빈혈(§2 blocker)로 오판하지 않는다(UI 매핑 ≠ 도메인 판정).

### §3.2 순서(order) — 뒤섞은 입력 ≠ 기대 + 리스트 `==` + 양끝 echo  *(FC-2 M1 정렬 직격)*

리스트 `==`만으론 부족했다 — 이미 정렬된 fixture를 넣으면 *무정렬* 코드도 green(M1이 vacuous였던 이유)이다. 두 가지를 형태로 못박는다: ⓐ 입력 순서 ≠ 기대(뒤섞은 입력 — 하드룰) ⓑ 양끝 echo(정렬'됨' 흉내가 아니라 *어느* 순서인지 고정). **정렬은 도메인 판정이므로**(architecture-ddd §5) VM이 아니라 *정렬을 소유한 도메인 단위*(애그리거트 메서드·domain_service·specification)를 **직접 호출**한다(seam A — repo 주입 없음):

```python
def test_orders_scrambled_input_by_date_ascending() -> None:
    scrambled: list[ForecastSummary] = [fc(d(3)), fc(d(1)), fc(d(2))]  # ≠ 기대(하드룰)
    ordered: tuple[ForecastSummary, ...] = ForecastWeek(days=tuple(scrambled)).ordered_by_date  # 도메인 단위 직접
    dates: list[date] = [summary.date for summary in ordered]
    assert dates == [d(1), d(2), d(3)]  # 전체 순서
    assert dates[0] == d(1)  # 양끝 echo — '정렬됨' 흉내 차단
    assert dates[-1] == d(3)
```

정렬이 VM·view·템플릿의 `sorted()`·`dictsort`로 새 있으면 이 도메인 테스트가 *작성 불가*해진다 — 그 자체가 판정 누수 신호다(판정 소유 §5·reviewer #2). `fc()`=요약 값 빌더(implementation-test §7). 리스트와 튜플은 `==`로 같아지지 않는다 — 비교 양쪽을 리스트로 맞춘다.

### §3.3 위치(position) — `data-testid` 슬롯 선택자 + 비대칭·음수 fixture  *(FC-2 M3 기온 위치 직격)*

디코이 위험 = 대칭 fixture(high == low·둘 다 양수)면 슬롯 스왑·부호 누락이 통과한다. *비대칭 + 음수* + 슬롯 `data-testid`로 막는다. 슬롯 위치는 view 행위라 **VM 대체**로 통제된 State를 주입한다(seam B — implementation-test §2):

```python
def test_temperature_slots_hold_high_and_low(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    page: BeautifulSoup = get_detail(client, monkeypatch, detail_state(high=7, low=-3))  # 상세 VM 대체(implementation-test §7)
    high: list[str] = [tag.get_text(strip=True) for tag in page.select('[data-testid="temp-high"]')]
    low: list[str] = [tag.get_text(strip=True) for tag in page.select('[data-testid="temp-low"]')]
    assert high == [format_temp(7)]   # 정확 일치·정확히 1 — '7' in text 는 '17'·'27'에도 통과(금지)
    assert low == [format_temp(-3)]   # 음수: 슬롯 스왑·부호 누락 포착
```

high ≠ low(비대칭)·하나는 음수다. 대칭/양수 fixture는 스왑을 못 잡는다. **단언은 `[format_temp(7)]` 리스트 정확 일치**다 — 개수(정확히 1)와 글자를 함께 고정한다. `'7' in text`는 부분문자열이라 `'17'`·`'27'`에도 통과해 스왑을 놓친다. 슬롯은 `data-testid`로 고정한다(텍스트 위치 추정 금지) — 단언이 `data-testid="temp-high"`를 집으므로 *생성 템플릿이 그 표식을 달아야* 한다(짝 규약은 architecture-ui — keyed-slot 단언 대상 요소는 역할을 가리키는 안정 `data-testid` 부착). `format_temp`는 SUT 포맷터 재사용(implementation-test §7). **적용 범위**: 같은 수치 슬롯(기온·가격·수량 등)이 목록 타일·상세 등 *여러 화면에 반복*되면 *각 화면*에서 이 형태(`data-testid` 슬롯 + 비대칭·음수 fixture)를 적용한다 — 위 예제는 상세지만 그 슬롯이 사는 모든 화면이 대상이며, 한 화면만 덮고 다른 화면을 비우면 그 화면 슬롯 단언이 vacuous다.

### §3.4 탭→상세 인자 전달 — non-edge 탭 + 날짜-echo fake + 범위 안 정확 개수  *(FC-2 M4 탭날짜 직격 · codex 디코이의 정체)*

dddart 5차 codex M4 디코이 = `.first` 탭 + 날짜 무관 하드코딩 상세 fake + "적어도 1" finder(주간 화면에 잔존하는 날짜 텍스트를 흡수). 셋을 형태로 막는다: ⓐ non-edge 탭(`[2]` — `[0]`은 "아무거나"라 의도 아닌 항목을 탭할 수 있다·**리스트 ≥3 전제**) ⓑ 상세 VM이 *탭한(navigated) 날짜*를 echo ⓒ 상세 범위 안에서 정확히 1. 목록은 VM 대체로 통제하고 상세는 *날짜를 되울리는* fake VM을 쓴다(seam B — `get_list`가 둘 다 배선·implementation-test §7):

```python
def test_tap_passes_tapped_date_to_detail(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    week: list[ForecastSummary] = [fc(d(3)), fc(d(1)), fc(d(2)), fc(d(4))]  # ≥3([2] 전제)·뒤섞임
    page: BeautifulSoup = get_list(client, monkeypatch, week)  # 목록 VM=week·상세 VM=날짜 echo fake (implementation-test §7)
    target: Tag = page.select('[data-testid="forecast-tile"]')[2]  # non-edge([0] 금지·리스트 ≥3)
    tapped: date = date.fromisoformat(str(target["data-date"]))
    detail_page: BeautifulSoup = get_page(client, str(target["href"]))  # 탭 = 타일의 링크를 따라간다
    detail: list[Tag] = detail_page.select('[data-testid="forecast-detail-view"]')
    assert len(detail) == 1
    assert count_text(detail[0], format_date(tapped)) == 1  # 날짜-echo: 상세 VM이 탭한 날짜를 되울려야 통과
```

fixture는 **최소 3개**다(`[2]`가 3번째를 집으므로 2개 이하면 `IndexError`). `format_date`는 SUT 포맷터 재사용(별도 포맷을 만들면 디코이). 타일의 `data-date`·`href`는 타일이 받은 도메인 요약을 관찰 가능하게 노출한 것이다(짝 규약은 architecture-ui §3). 탭이 HTMX 교체면 타일의 `hx-get` 주소를 `get_fragment`로 받아 같은 단언을 하고, 탭이 UI JS 동작이면 같은 FORM을 브라우저 테스트로 쓴다(`get_by_test_id("forecast-tile").nth(2)` 클릭 → 상세 범위 안 `get_by_text(format_date(tapped), exact=True)`가 `to_have_count(1)` — implementation-test §4).

**`select_one`·`len(...) >= 1`·`text in html`(="적어도 1")은 쓰지 않는다** — 주변/중복 요소를 흡수해 "그 항목의 날짜"가 아니라 "어딘가 그 텍스트"를 통과시킨다(M4 디코이의 정체·검증 §B). 정확 개수는 `len(...) == 1`(정확히 1)·`== n`·`== 0`(0)으로 고정한다(`count_text`도 같다).

### §3.5 도메인 양갈래 — 판정의 두 결과를 도메인에서 직접  *(thick domain 무게중심 · 보강)*

판정은 *충족*과 *위반* 둘 다 두드려야 안전망이다 — 한쪽만 덮으면 다른 갈래의 회귀를 묵인한다. 판정은 도메인 단위라(architecture-ddd §5) 순수하게 직접 호출한다(seam A — VM 대체·network 불요):

```python
def test_forecast_is_stale_after_7_days() -> None:
    base: datetime = datetime(2026, 6, 17, tzinfo=UTC)                            # 고정 주입(§1 날짜 결정성)
    assert Forecast(updated_at=base).is_stale(base + timedelta(days=8)) is True   # 위반 갈래
    assert Forecast(updated_at=base).is_stale(base + timedelta(days=6)) is False  # 충족 갈래
```

UseCase의 `Either[BadRequestResponse, T]`를 *직접* 단언할 땐 양채널 단언이 `assert result == Right(value=expected)` / `assert isinstance(result, Left)`다(Left·Right는 frozen dataclass라 `==`가 갈래와 값을 함께 비교한다 — implementation-test §3). 단 **Left(`BadRequestResponse`)는 *네트워크/infra* 실패**라 통제하려면 ApiClient 목이 필요하고(seam C·통합·드물게), **도메인 규칙 위반은 State error 채널**(architecture-state §4)이지 `BadRequestResponse`가 아니다 — 그래서 도메인 양갈래의 1차는 위처럼 *도메인 판정을 직접* 두드리는 것이다. `isinstance(result, Right)`만 보고 값을 안 보면 vacuous에 가깝다(`== Right(value=expected)`로 분기 + 값을 함께 고정).

### §3.6 매핑(mapping) 정확성 — case별 값 핀(필터 함수 직접)  *(FC-2 M2 매핑 swap 직격)*

§3.1(집합 크기)이 green이어도 두 case의 표시값을 통째로 *맞바꾸면*(swap) 집합 크기는 불변이라 §3.1을 통과한다 — 이것이 M2(매핑 swap)의 정체다. **구별**(몇 개가 서로 다른가·§3.1)과 **정확성**(어느 case가 *어느* 값인가)은 별개 축이라, 분류 enum의 표시값 매핑은 case별 기대값을 *명세/골든 라벨표에서 끌어* 직접 단언한다(seam A — 필터 함수 직접·템플릿 미렌더):

```python
def test_each_condition_maps_to_spec_icon_and_color() -> None:
    # 기대값은 명세/골든 라벨표에서 — 구현(ui_extension)에서 베끼면 디코이(§2)
    assert weather_icon(WeatherCondition.CLEAR) == "sunny"
    assert weather_list_color(WeatherCondition.CLEAR) == "weather-clear"
    assert weather_icon(WeatherCondition.THUNDERSTORM) == "thunderstorm"
    # … 분류 enum의 *모든* case를, 매핑되는 *각 축*(아이콘·색·라벨 등)으로 전수
```

**전수가 핵심**이다 — 일부 case만 단언하면 안 덮인 case의 swap이 green 생존(vacuous)이고, 한 축(아이콘)만 핀하고 색을 비우면 색 swap이 통과한다. 매핑은 도메인 enum→표시값 필터 함수(ui_extension — architecture-ui §5 "매핑의 유일한 자리")라 **필터 함수를 직접 호출**한다 — VM 대체·`data-testid` 불요(seam A). keyed-slot(§3.3)과 달리 생성측 짝 규약이 없다(필터 거주가 §3.1·architecture-ui §5로 이미 정당).

이 FORM은 매핑을 *두드리는 테스트가 있는가*(FC-2 비-vacuity)를 닫는다 — 표시값이 시안과 *미관상* 일치하는지(FID·인간 오라클)나 서로 *구별되는지*(distinctness·§3.1)와는 **독립 축**이며 서로 대체하지 않는다(§3.1 green + 매핑 단언 부재 = M2가 빠져나가는 자리). M2 골든이 이 swap을 주입하므로, 이 FORM이 없으면 매핑이 깨져도 red가 0이다.

## §4. 무엇을 생략하나

자명하거나 구현을 미러링하는 테스트는 헛테스트를 부른다 — 행위와 공개 API만 테스트한다(Fowler·SWE@Google: "test only behavior and module public API"). 다음은 쓰지 않는다:

- **getter·조건 없는 위임** — 한 줄 통과·필드 반환은 행위가 없다(단 분류 enum의 case별 매핑 필터는 *case→값 결정* 분기라 행위가 있다 — §3.6 대상이지 생략 아님).
- **private 메서드**(`_` 접두) — 공개 행위를 통해 간접 검증된다(직접 테스트하려고 `_`를 떼지 않는다).
- **템플릿 마크업 *형태*** — "div 안에 span 2개" 같은 레이아웃 구조는 행위가 아니다(시각은 인간 오라클이 본다 — G2 배너).
- **시각 스타일·golden** — 같은 실행·같은 브라우저의 옛 판 ↔ 지금 판 이미지 비교도 비채택이며, 승인 명세나 시험 목록에 있어도 예외가 아니다. 사람 눈 확인용 갈무리는 그대로 유지한다.  색·폰트·여백의 픽셀 일치는 dddjango-web 비채택(시각=인간 오라클·스크린샷 비교는 폰트/플랫폼 비결정을 도구가 인정 — implementation-test §8).
- **프레임워크 내부** — Django·htmx·브라우저 자체 동작은 그들의 테스트 몫이다.

생략은 *대충*이 아니다 — 핵심 판정·정렬·매핑·분기·탭 전달은 §3 FORM으로 두텁게 덮는다.

## §5. red일 때 — 반송·reviewer FORM-감사

- **spec-anchored red = 코드가 틀린 것**: 명세에서 끈 단언이 red면 *코드를 고친다*. 테스트를 약화(단언 삭제·`>= 1`·`in` 포함 검사로 완화·기대값을 코드에 맞춤)하거나 삭제해 green을 만들지 않는다 — 그건 안전망을 스스로 끊는 것이다. 시도 한도 내(coder 3회 규율) green이 안 되면 보고한다(명세 가정 오류인지 구현 난점인지 구분).
- **discipline-reviewer 방법 채택·재현성·FORM 감사 렌즈**: 먼저 비채택 방법을 반송하고 영구 시험 재현성을 확인한 뒤 올바른 FORM을 확인한다 — 핵심 행위마다 §3 FORM을 썼는가 · 오라클이 *명세*에서 왔는가(구현-미러 아님) · 구별은 뒤섞은 입력 + 정확 개수(`len(...) == 1`)인가 · 단언이 충분히 좁은가(`>= 1`·`select_one`/대칭 fixture/`[0]`/한쪽 갈래만 같은 vacuity·디코이 형태가 있는가). 발견은 coder가 반영한다(reviewer는 코드를 고치지 않는다).
- **자가집행 FORM의 한계(정직)**: §3.1 집합-크기는 충돌 시 자동 red라 *작성 형태*가 디코이를 막지만, 나머지 FORM의 실효는 coder가 그 형태를 *쓰는가*에 달렸다(기계 강제 아님) — 그래서 reviewer FORM-감사가 짝이고, 재발 시 작성자 분리·정적 분석으로 승격한다(measure-first).
