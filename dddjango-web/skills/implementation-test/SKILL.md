---
name: implementation-test
description: dddjango-web 테스트의 Django 메커니즘 표기 — pytest·pytest-django·Django 테스트 클라이언트와 HTML 단언·unittest.mock/monkeypatch 더블(추가 설치 0)·VM 대체·HTMX 요청 헤더·pytest-playwright 브라우저 테스트(UI JS 기능이 있을 때만)·날짜 주입·외부 이미지 고정·헬퍼 계약. 테스트 코드를 쓸 때 로드한다. 무엇을/오라클/단언 FORM은 discipline-test 소유.
user-invocable: false
---

# 테스트 표기법

dddjango-web 테스트의 **Django 메커니즘·결정성·더블 표기**가 여기 산다 — 격리(VM 대체)·요청·더블·시간·외부 이미지의 결정성. **무엇을 테스트할지·오라클·단언 FORM·생략은 discipline-test 소유**(이 문서는 그 FORM이 쓰는 셋업·요청·헬퍼만 표기한다). 표기 사실의 단일 출처는 `references/final.md`다.

## 언제 쓰나

테스트 코드를 작성할 때 — VM 격리, 페이지·조각 요청과 HTML 단언, 더블(mock/fake), 시간·브라우저·외부 이미지의 결정성 확보. 전문을 읽지 말고 아래 표로 필요한 절만 부분 적재한다. 경계:

- 무엇을/오라클/비-vacuity/단언 FORM(구별·순서·위치·탭) → `discipline-test`
- 테스트 파일 위치(web_test/ = web 미러·sparse) → `discipline-houserules`(§1·§3)
- VM·조각 응답·hx-* 규율 → `implementation-htmx`
- 요청 수명·템플릿·CSRF → `implementation-django` §6
- UI JS 동작의 검증 범위 → `implementation-javascript` §7

## 핵심 운영 원칙

- 실행은 **build-state의 `test_command`** 한 줄(G0가 settings 지정까지 확정 — 예 `pytest web_test --import-mode=importlib --ds=config.settings`) — Coordinator 전수 테스트·coder-web green 래칫과 같은 명령 (§1)
- 격리 seam은 셋 — **순수 도메인 직접**(판정)·**VM 대체**(view — view 모듈이 부르는 VM 이름을 `monkeypatch`로 바꾼다)·**ApiClient 목**(통합 드물게); repo·usecase 주입 자리는 dddjango-web에 없다(DI 없음) (§2)
- VM 단위는 VM을 직접 생성해 `build(...)`가 돌려준 State를 단언한다 — 조회 실패는 `pytest.raises`, 액션 실패는 State의 `error` 필드 (§2)
- 더블은 **표준 `unittest.mock` + pytest `monkeypatch`**(추가 설치 0): `MagicMock(return_value=…)`·`create_autospec`·`assert_called_once_with`·`ANY` — 바꿀 이름은 «찾는 자리»(쓰는 모듈)에서 바꾼다 (§3)
- 화면 테스트: Django 테스트 클라이언트로 GET(`reverse(<Bc>Routes.…)`) → `status_code == 200` → `BeautifulSoup(…, "html.parser").select(…)`로 정확 개수 단언 · 조각(HTMX) 요청은 `HX-Request: true` 헤더 · UI JS 동작만 pytest-playwright 브라우저 테스트(`live_server`·`expect` 자동 재시도·고정 대기 금지) (§4)
- **날짜 주입**: 도메인 판정은 기준일을 *인자로* 받는 순수 함수·'지금'은 view가 한 번 읽어 VM 인자로 격리·테스트는 고정 `datetime`을 주입한다(실시각 안 읽음·시계 고정 도구 없음) (§5)
- 외부 주소 이미지를 그리는 화면의 브라우저 테스트는 `page.route`로 그 요청을 고정 응답으로 돌린다 — 테스트 클라이언트 단언은 이미지를 받지 않아 미해당 (§6)
- 헬퍼 계약(`d()`·`fc()`·`detail_state`/`list_state`·`FakeListVM`/`FakeDetailVM`·`get_page`/`get_fragment`·`get_list`/`get_detail`·`count_text`·`format_date`/`format_temp`·`SCREEN_PROBES`)은 §7 단일 정의 — discipline-test FORM이 이 이름·계약을 쓴다. `SCREEN_PROBES`만 예외로 FORM이 아니라 **별도 render-smoke 테스트(`render_smoke_test.py`·§7)가 소비**하는 화면 진입점 맵이다(view·헬퍼 이름을 맵 안에 가둬 프로브가 BC 이름에 비의존·green 경로 강제) (§7)

- **영구 시험 재현성**: `web_test/`·호스트 시험 트리와 시험 지원 코드(`conftest.py`·`_support.py` 등)는 `.dddjango-web/`를 읽거나 쓰지 않고 프로젝트 루트 밖 머신 고정 고정물·기준판·캐시에 기대지 않는다. 기록 폴더(`.dddjango-web/`·`.dddjango/`)에 둔 시험 원문 사본은 영구 시험이 아니다 — 그 사본을 영구 시험으로 옮겨 오면 새 시험으로 본다. 고정물·기대 자료는 시험 트리에, 실행 기록은 `tmp_path` 등 임시 폴더에 둔다. 선택 도구 부재는 호스트 규칙대로 skip하고 설치된 도구의 고장은 실패로 남긴다. 레인 전용 환경 변수 존재 단언으로 실행 전제를 만들지 않는다 — 정상 환경 변수 행위 시험·필수 settings는 허용하며 환경 변수 의미 판정은 TG2 밖, discipline 감수와 G2 표준 실행이 확인한다.
- **이미지 비교 비채택**: 같은 실행·같은 브라우저의 옛 판 ↔ 지금 판 이미지 비교도 비채택이며, 승인 명세나 시험 목록에 있어도 예외가 아니다. 사람 눈 확인용 갈무리는 그대로 유지한다.

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 패키지 라인·왜 unittest.mock(vs pytest-mock)·실행 옵션 | [`references/final.md`](references/final.md) §1 |
| 격리 seam·VM 대체·VM 단위 | final.md §2 |
| 더블·단언 어휘(HTML 포함) | final.md §3 |
| 화면 테스트 결정성(테스트 클라이언트·HTMX 헤더·브라우저 테스트) | final.md §4 |
| 날짜·시간 결정성(주입) | final.md §5 |
| 외부 주소 이미지 고정(조건부) | final.md §6 |
| 헬퍼 계약 단일 정의 | final.md §7 |
| 안 쓰는 것(스크린샷 비교·외부 E2E 러너·pytest-mock·mutation) | final.md §8 |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
