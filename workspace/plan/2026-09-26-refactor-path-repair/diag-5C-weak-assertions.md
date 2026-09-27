# 진단 5C — 약한 단언 강화: 레인 안 (가) vs 별도 요청 (나) 결정 재료 (2026-09-27)

- 대상: spring_dream_server `main` = `495128e26`(2026-09-27 02:31). 읽기 전용으로만 봤다. 쓴 명령은 `git ls-tree` · `git cat-file --batch` · `git log` · `git show` 이고, 작업 트리와 pytest 는 건드리지 않았다.
- 스크립트·산출: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/diag5c/` (이하 `$S`). 표는 모두 `$S/out/*` 에서 옮겼다.
- 표기: **실측**은 스크립트 출력이나 원문 판독 결과다. **추정**은 표본 비율이나 가정으로 환산한 값이다.

## 0. 결정 브리프 초안

1. 질문(결정 2 Q3): «약한 단언 강화»를 (가) 리팩토링 레인의 0T(테스트 정리 창) 안에서 허용할지, (나) 별도 요청으로 뺄지.
2. 현장 규모(실측): 테스트 825파일 · 6,004함수 · 단언 22,324. BC 23곳의 4,040함수 가운데 단언이 전부 약한 함수는 넓은 정의로 757, 오탐 유형을 걷은 정밀 정의로 193이다. 표본으로 보정하면 실제로 강화할 만한 것은 약 110(2.7%)이다(추정).
3. 공개 API(실측): 53개 가운데 47개는 본문을 정확히 비교하는 테스트가 있다. 상태 코드만 보는 6개 중 5개는 성공 응답이 204(본문 없음)다. 그래서 «약한 보호뿐»인 엔드포인트는 1개다(`GET /api/fortune-calculation/places`).
4. 이력(실측·판독): 리팩터 커밋 68개에서 단언을 강화한 사례는 0이다. 약한 단언 때문에 결함이 새어 나간 사례도 0이다. 리팩터 직후 fix 후보 31쌍을 판독했고, 실제 유출 1건(`36258bbea`)은 기능 커밋에서 fake 배선 때문에 생긴 것이었다.
5. (가)의 대가(추정): 레인당 강화 편집은 중앙값 약 3건이다(최대 fortune_house 약 19). 0T 창이 하나 늘고, 레인당 약 +0.3~0.6h, 23레인 합계 약 7~14h다. behavior_guard 는 고칠 것이 없다. 규범은 3곳(Coordinator · coder · DR)과 Codex 미러를 고친다.
6. (나)의 대가(추정): 강화 레인이 먼저 착륙하지 않으면 리팩터 레인은 약한 보호 위에서 돈다. 대상은 엔드포인트 1개와 약한 테스트 약 110개이고, 강한 함수 안에 멤버십 단언이 섞인 208함수가 더 있다. 강화 레인은 소형 레인 선례(중앙값 1.6h)에 사용자 게이트가 붙고, 5개(차수당 1)~23개(BC당 1)가 필요해 약 8~37h다.
7. 권고(결정 아님): (가)로 하되 «ⓐ 항목이 옮기는 판정을 덮는 테스트»로 범위를 한정한다. 근거는 두 가지다. 편집 수가 작고 0T 판정기가 이 편집을 그대로 받는다. 그리고 리팩터 커밋이 스스로 강화한 선례가 0이라, 별도 요청으로 미루면 사실상 강화되지 않는다. 반대 근거는 유출이 0이고 API 보호가 이미 강하다는 점이다.

---

## 1. 테스트 전수 — BC별 규모와 단언 (실측)

- 명령: `python3 $S/measure.py && python3 $S/table.py` (`$S/out/functions.json` · `$S/out/table.md`).
- 수집 범위: 경로 조각에 `test`/`tests` 가 있고 파일명이 `test_*.py`/`*_test.py` 인 파일 825개. `.dddjango/` probe 4개는 뺐다.
- 테스트 함수: 모듈 최상위 `test*`, 그리고 `Test*` 클래스와 `*TestCase` 하위 클래스의 `test*` 메서드다.
- 단언 수는 테스트 함수 본문에 직접 쓴 것만 센다. 헬퍼 안의 단언은 함수 판정에만 합산한다(헬퍼 경유 함수 965개).
- parametrize 함수는 1,096개이고, 케이스로 펼치지 않았다.

| 버킷 | 파일 | 함수 | 단언 | E 정확 | 약한 단언 ①②④⑤⑥ | ③ 상태 | 약한 함수·넓은 | 좁은 | 정밀 | 정밀 중 e2e |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| fortune_house | 99 | 1051 | 5108 | 3743 | 1328 (26%) | 37 | 149 (14%) | 35 | 33 | 4 |
| accounts | 47 | 402 | 938 | 614 | 178 (19%) | 146 | 74 (18%) | 27 | 11 | 3 |
| fortune_teller | 75 | 388 | 979 | 650 | 200 (20%) | 129 | 70 (18%) | 24 | 21 | 4 |
| fortune_library | 44 | 383 | 1261 | 740 | 412 (33%) | 109 | 95 (25%) | 13 | 13 | 0 |
| chat_relay | 54 | 267 | 1163 | 792 | 262 (23%) | 109 | 33 (12%) | 15 | 14 | 6 |
| fortune_calculation | 36 | 194 | 470 | 363 | 105 (22%) | 2 | 43 (22%) | 20 | 19 | 1 |
| service_policy | 24 | 142 | 303 | 226 | 54 (18%) | 23 | 22 (15%) | 3 | 1 | 0 |
| fortune_catalog | 17 | 125 | 485 | 370 | 85 (18%) | 30 | 15 (12%) | 5 | 5 | 0 |
| fortune_content | 11 | 120 | 256 | 179 | 56 (22%) | 21 | 8 (7%) | 5 | 5 | 0 |
| decisive_fortune | 14 | 118 | 340 | 212 | 86 (25%) | 42 | 33 (28%) | 6 | 3 | 1 |
| media_library | 21 | 117 | 332 | 201 | 99 (30%) | 32 | 26 (22%) | 11 | 10 | 0 |
| llm_access | 13 | 110 | 473 | 353 | 120 (25%) | 0 | 13 (12%) | 2 | 2 | 0 |
| promotion | 26 | 103 | 228 | 161 | 44 (19%) | 23 | 18 (17%) | 1 | 1 | 0 |
| fortune_reading | 27 | 93 | 417 | 305 | 102 (24%) | 10 | 23 (25%) | 3 | 3 | 0 |
| fortune_record | 33 | 86 | 354 | 203 | 127 (36%) | 24 | 19 (22%) | 14 | 10 | 9 |
| fortune_employee | 17 | 55 | 151 | 118 | 21 (14%) | 12 | 8 (15%) | 3 | 1 | 0 |
| fortune_intent | 10 | 55 | 105 | 65 | 40 (38%) | 0 | 28 (51%) | 12 | 12 | 0 |
| text_library | 13 | 52 | 137 | 89 | 37 (27%) | 11 | 16 (31%) | 8 | 4 | 1 |
| wallet | 9 | 46 | 232 | 163 | 41 (18%) | 28 | 11 (24%) | 9 | 9 | 0 |
| notification | 8 | 40 | 70 | 37 | 27 (39%) | 6 | 22 (55%) | 5 | 3 | 2 |
| rag_service_library | 10 | 39 | 83 | 40 | 43 (52%) | 0 | 16 (41%) | 11 | 11 | 0 |
| product | 10 | 34 | 59 | 35 | 16 (27%) | 8 | 12 (35%) | 1 | 1 | 0 |
| query_translation | 7 | 20 | 94 | 77 | 17 (18%) | 0 | 3 (15%) | 1 | 1 | 0 |
| **BC 소계 (23)** | 625 | 4040 | 14038 | 9736 | 3500 (25%) | 802 | 757 (19%) | 234 | 193 | 31 |
| 공유: charging_test | 31 | 39 | 150 | 70 | 73 (49%) | 7 | 5 (13%) | 5 | 3 | 0 |
| 공유: framework | 1 | 4 | 6 | 3 | 0 | 3 | 0 | 0 | 0 | 0 |
| 공유: tests 루트 | 92 | 994 | 4203 | 2963 | 1238 (29%) | 2 | 101 (10%) | 67 | 67 | 0 |
| 공유: tests/web | 76 | 927 | 3927 | 2157 | 1591 (41%) | 179 | 249 (27%) | 143 | 136 | 0 |
| **공유 소계** | 200 | 1964 | 8286 | 5193 | 2902 (35%) | 191 | 355 (18%) | 215 | 206 | 0 |
| **전체** | 825 | 6004 | 22324 | 14929 | 6402 (29%) | 993 | 1112 (19%) | 449 | 399 | 31 |

- BC 층별(실측):

  | 층 | 파일 | 함수 | 약한 함수(넓은) |
  |---|--:|--:|--:|
  | unit | 325 | 2,439 | 586 |
  | integration | 231 | 1,271 | 105 |
  | e2e | 69 | 330 | 66 |

  넓은 정의의 약한 함수는 unit 에 몰려 있다. 대부분이 전용 예외 타입 raises 만 쓰는 함수다(§2).
- tests/web 은 약한 단언 비율이 41%로 가장 높다. 대부분 HTML 멤버십(①)이다(929건). HTML 은 본문 전체 비교가 비현실적이어서 멤버십이 정상 형태에 가깝다. 이 버킷은 dddjango-web 레인 소관이라 결정 2 의 대상 밖으로 본다.

## 2. 약한 단언 정의 · 한계 · 정밀도

### 2.1 정의 (`$S/classify.py`)

| 기호 | 범주 | 단언 단위 판정 규칙 |
|---|---|---|
| E | 정확 비교 | `==`(아래 ③④ 제외) · `is <값>` · `assert_called_once_with` · `assert_called_with` · `assert_not_called` · `raises(..., match=)` · `raises(...) as e` 뒤에 `e` 를 단언 · `math.isclose` |
| ① W1 | 멤버십만 | `in` / `not in` · `issubset` / `issuperset` · `assert_any_call` · `assert_has_calls` |
| ② W2 | 진릿값만 | `assert x` · `assert not x` · `is not` · `isinstance` · `all` / `any` · `startswith` · `re.match` · 그 밖의 호출 결과 · `or` · `assert_called` / `assert_called_once` |
| ③ W3 | 상태 코드 | `==` 의 한쪽에 `.status_code` |
| ④ W4 | 길이만 | `==` 의 한쪽이 `len(...)` |
| ⑤ W5 | 예외 타입만 | `pytest.raises(X)` 에 `match=` 가 없고 `as` 변수도 뒤에서 보지 않음. **W5g** = 범용 타입(ValueError · IntegrityError · pydantic/Django ValidationError · Exception · 튜플 등 22종) · **W5c** = 전용 예외 타입 |
| ⑥ W6 | 부등·범위 | `!=` · `<` · `>` · `<=` · `>=` |
| N | 중립 | `assert False` · `pytest.fail`. 판정에서 뺀다 |

함수 단위 판정은 직접 단언과 헬퍼 경유 단언을 합쳐서 한다. 판정은 네 가지다.

- 강함: E 가 하나라도 있다.
- 약함: E 가 없고 약한 단언이 하나 이상 있다.
- 단언0: 단언이 하나도 없다.
- 약함의 정의는 세 단계로 좁힌다.
  - **넓은** = 위 정의 그대로.
  - **좁은** = W5c(전용 예외 타입)를 정확으로 본다. 예외 이름이 곧 계약이기 때문이다.
  - **정밀** = 좁은 정의에서 두 유형을 뺀다(`$S/table.py`). ⓐ 상태 코드만 보고, 단언한 상태 리터럴이 전부 비 2xx 인 거부 관문(38). ⓑ `is_` / `has_` 술어의 진릿값만 보는 함수(3).

### 2.2 한계

- **오탐**(약함으로 셌지만 실제로는 충분한 것)
  - 전용 예외 raises. 넓은 정의의 약한 함수 1,112개 중 624개가 W5c 하나로만 약하다.
  - 권한·메서드·인증 거부 관문(403 · 405 · 401). 상태가 계약의 전부이고, 현장 규범 «framework error body 는 snapshot 하지 않는다»(§5 slot 12)가 이것을 의도로 적어 두었다.
  - bool 술어. `assert not x.has_...()` 는 `== False` 와 같다.
  - 속성 테스트. 길이로 서로 다름을 보이거나, 부분집합으로 덮음을 보이는 경우다.
  - 원소 자체가 정확한 문자열인 멤버십.
- **미탐**(강함으로 셌지만 약한 곳이 있는 것)
  - 필드 하나만 `==` 로 보는 부분 정확 비교.
  - 강한 함수 안에 섞인 멤버십 단언. BC 에서 **208함수**다(e2e 46 · integration 119 · unit 43).
  - R3 가 든 `test_decisive_fortune_chart_api.py:287-288` `"gender" in body["missing"]` 이 바로 이 유형이다. 함수 판정은 «강함»(E 1 · W1 1 · W3 1)이다.
- **해소 한계**
  - fixture 안의 단언과 동적 import 헬퍼는 보지 않았다.
  - parametrize 는 케이스로 펼치지 않았다.
  - `self.` 메서드와 `from 모듈 import 함수` 가 아닌 헬퍼는 따라가지 않았다.

### 2.3 표본 판독 (실측 판독 → 정밀도 추정)

판정 기준은 «T»다. T = 동작을 바꾼 리팩터가 이 테스트를 통과할 수 있고, 케이스를 늘리지 않고 본문만 고쳐 정확 비교로 바꿀 수 있다. 원문은 `$S/out/sample*.txt` 에 있다.

- **표본 1 — 넓은 정의 층화 10**(`$S/sample.py`, seed 5). T 3.5 / 10.

| # | 테스트 | 범주 | 판정 |
|---|---|---|---|
| 1 | `fortune_library/test/unit/test_answer_outline_invariants.py:141` | W5c | 오탐(전용 예외 = 계약) |
| 2 | `fortune_teller/test/unit/test_book_input_selection.py:117` | W5c | 오탐 |
| 3 | `tests/web/client/accounts/test_web_nickname_response.py:160` | W5c | 오탐 |
| 4 | `fortune_catalog/test/integration/test_fortune_type_admin.py:702` | W1 + W3 | 약하지만 HTML 이라 강화가 비현실 |
| 5 | `tests/web/related_persons/test_related_person_editor_page.py:355` | W1 + W3 | 약하지만 HTML 이라 강화가 비현실 |
| 6 | `tests/test_service_step4_build_vocabulary.py:89` | W2 | **T** — `any(... in f)` → 실패 목록 정확 비교 |
| 7 | `rag_service_library/test/unit/test_statement_rendering.py:54` | W1 | **T** — 렌더 결과 전체 문자열 |
| 8 | `accounts/test/e2e/test_accounts_csrf.py:177` | W3 | 오탐(docstring 이 «body snapshot 안 함»을 의도로 명시) |
| 9 | `fortune_intent/test/unit/test_message_split_generation_adapter.py:163` | W5g | **T** — ValidationError 에 `match=` |
| 10 | `fortune_calculation/test/unit/test_match_shinsal.py:807` | W2 + W4 | 경계(0.5) — 술어 헬퍼 |

- **표본 2 — 좁은 정의 BC 무작위 10**(`$S/sample2.py`, seed 11). T 3 / 10.
  - T: `notification/.../test_email_notice_service.py:69`(`len(sent)==1`) · `fortune_intent/...:163`(ValidationError) · `fortune_library/.../test_information_item_repository.py:317`(IntegrityError — 제약 이름 `match=` 가능).
  - 오탐 7:
    - 거부 관문 5: `text_library/.../test_prompt_admin.py:177` · `test_fixed_phrase_admin.py:107` · `:87` · `fortune_record/.../test_fortune_record_api_session.py:26` · `fortune_calculation/.../test_place_search_api.py:34`
    - 술어 1: `fortune_house/.../test_visit.py:3013`
    - 속성 1: `fortune_reading/.../test_rfc8785_adapter.py:41`
  - 이 표본의 오탐 5건(거부 관문) 때문에 정밀 정의의 ⓐ 규칙을 만들었다.
- **표본 3 — 정밀 정의 가운데 «기타» BC 무작위 10**(`$S/refine.py`, seed 23). T 5 / 10(T 4 + 경계 2 × 0.5).
  - T: `fortune_house/.../test_card_envelope.py:43` · `notification/...:69`(표본 2와 중복) · `fortune_intent/.../test_split_output_model_empty_sets.py:101` · `fortune_teller/.../test_prompt_set_draw_service.py:84`(ValueError × 2)
  - 경계: `fortune_library/.../test_calculation_value_registry.py:186`(`len == 114`) · `test_match_shinsal.py:734`
  - 오탐: `decisive_fortune/.../test_decisive_fortune_chart_api.py:190`(OpenAPI 존재만 — 의도) · `accounts/.../test_nickname_word_list.py:267`(속성) · `fortune_house/.../test_notice_phrase_resolver.py:66`(속성) · `fortune_intent/...:197`(원소가 정확한 문자열)

| 정의 | BC 함수 수 (실측) | 정밀도 (표본) | 실제 강화 대상 (추정) |
|---|--:|---|--:|
| 넓은 | 757 | W5c 단독 층 0/3 · 나머지 층화 3.5/7 | — |
| 좁은 | 234 | 3/10 | — |
| 정밀 | 193 | «기타» 180: 합산 표본 (5 + 3) / 14 ≈ 0.57 · «2xx 상태만» 13: 표본 없음, 진성으로 가정 | **≈ 110** (범위 약 70~140, 표본이 작다) |

## 3. 공개 표면 보호 — API 엔드포인트 (실측)

- 명령: `python3 $S/endpoints.py` (`$S/out/endpoints.json` · `$S/out/endpoints.md`).
- 엔드포인트: `driving_layer/api/**` 의 `@api_controller(prefix)` 와 `@route.<verb>(path)` 로 뽑았다. 53개이고, `git grep` 의 경로 데코레이터 수와 같다.
- 호출 대조: 테스트 함수(중첩 포함)와 응답을 돌려주는 헬퍼 안의 `.get` / `.post` / `.put` / `.patch` / `.delete` · `.generic(verb, path)` · `getattr(client, m)(path)` 를 찾는다. 경로는 상수 · f-string · URL 빌더 함수의 return 으로 풀고, 풀리지 않는 조각은 와일드카드로 둔다.
- 보호 수준: 응답을 받은 변수에서 흘러간 값을 본 단언으로 판정한다. 그 변수를 넘겨받은 헬퍼 안의 단언까지 본다(깊이 3).
- arrange 용으로만 부른 헬퍼 호출(예: `_login`)은 «미단언»으로 센다.

| BC | 엔드포인트 | 상태·헤더만 | 본문 약함뿐 | 본문 정확 ≥1 |
|---|--:|--:|--:|--:|
| accounts | 19 | 4 | 0 | 15 |
| fortune_teller | 9 | 1 | 0 | 8 |
| chat_relay | 6 | 0 | 0 | 6 |
| decisive_fortune | 6 | 0 | 0 | 6 |
| fortune_employee · fortune_record · media_library · wallet | 각 2 | 0 | 0 | 각 2 |
| fortune_calculation | 1 | 1 | 0 | 0 |
| fortune_reading · product · promotion · service_policy | 각 1 | 0 | 0 | 각 1 |
| **합계** | **53** | **6** | **0** | **47** |

- 호출 테스트가 없는 엔드포인트는 0이다.
- **상태·헤더만 6개의 내역**:
  - 5개는 성공 응답이 `204: None` 이다. 성공 계약이 상태뿐이라 보호가 약하다고 보지 않는다: `DELETE /api/accounts/sessions/current` · `POST /api/accounts/password-resets` · `POST /api/accounts/me/withdrawals` · `DELETE /api/accounts/me/related-persons/{id}` · `DELETE /api/fortune-teller/.../reviews/me`.
  - **«약한 보호뿐» 실질 1개**: `GET /api/fortune-calculation/places`. HTTP 테스트는 401 과 OpenAPI 존재만 본다. 200 본문은 `unit/test_place_search.py` 가 컨트롤러를 직접 불러 따로 본다(HTTP 경유 아님).
- **응답 코드 단위**(선언된 `response={코드: …}` × 가장 강한 보호):
  - 본문이 있는 코드는 131개다. 93개는 본문 정확 비교가 있고, 5개는 상태·헤더만, 33개는 그 코드를 단언한 테스트가 없다.
  - 정확 비교가 없는 38개 가운데 **성공 코드는 3개**다: `POST /api/accounts/sessions 200`(상태·쿠키만) · `GET /api/fortune-calculation/places 200` · `POST /api/fortune-readings/evidence-bundles 200`(HTTP 없음, `unit/test_evidence_api.py` 가 직접 호출).
  - 나머지 35개는 4xx/5xx 오류 본문이다. accounts 21 · chat_relay 10 · 그 밖 4.
- 한계:
  - 한 함수 안에서 응답 변수 이름을 다시 쓰면 호출이 섞인다.
  - HTTP 경유만 셌다. 컨트롤러 직접 unit 테스트 2개는 세지 않았다.
  - `tests/web/client/**` 는 HTTP 를 stub 해서 서버를 보호하지 않으므로 제외했다.
  - web 라우트 43개(`web/*/urls.py`)는 이번에 재지 않았다. dddjango-web 소관이다.

## 4. 이력 — 리팩터 커밋의 단언 강화와 결함 유출 (실측 · 판독)

- 명령: `python3 $S/history.py` · `python3 $S/history_all.py` (`$S/out/history*.{md,json}`).
- 리팩터 커밋 R 은 다음 세 조건을 모두 만족하는 커밋이다.
  - 비머지 커밋이다.
  - 메시지가 `^refactor` · 리팩터 · 리팩토링 · 슬라이스 0 · S0 · 골격 이관 · rename · 개명 · move · 이관 · 재배치 · 옮김 중 하나에 맞고, `feat` / `fix` / `test` / `docs` / `chore` / `style` 로 시작하지 않는다.
  - 제품 `.py` 를 1개 이상 바꾼다(테스트 쪽과 migrations 제외).

| 항목 | 값 |
|---|--:|
| main 비머지 커밋 | 3,329 |
| 리팩터 커밋 R | 68 |
| R 중 테스트 파일을 편집한 것 | 36 (파일 303 · 추가 함수 696 · 삭제 51) |
| R 에서 단언 범주가 바뀐 함수 | 8 |
| **R 에서 약함 → 강함(단언 강화)** | **0** |
| R 에서 강함 → 약함 | 1 — `74b3599d4` S0′ 응용 예외화. `result.outcome == "service_unavailable"` 가 `raises(TurnTemporarilyUnavailable)` 로 바뀌었다. 좁은 정의로는 약화가 아니다 |
| 기저율: 전체 커밋의 약함 → 강함 | 24함수 / 11커밋. 최다는 `836a7e592`(A7 확인 창 + 감사 잔여, 14) · 전부 기능·감사 커밋이고, 테스트만 바꾼 커밋은 1 |

- **리팩터 직후 fix**: R 뒤 72시간 안에 메시지가 `^fix` · 버그 · 결함 · 회귀 · 고침 · 바로잡에 맞고(mypy · typing · ruff 제외), R 이 바꾼 제품 `.py` 를 다시 바꾼 커밋을 찾았다. **31쌍**(고유 R 8 · 고유 F 21)이 나왔다.

| 묶음 | 쌍 | 판독 |
|---|--:|---|
| rag 런타임(`framework/technology/rag/**`, R `3adadb752` · `d8483fea4` · `b46536099` · `0bb6a942b`) | 27 | book factory G4/C11 기능 반복이다(F 가 새 계약을 집행한다). `5e3331623` 은 임시 경로 `resolve()`, `19d39c971` 은 스키마 세트 해석이라 리팩터 회귀가 아니다(diff 2건은 확인했고 나머지는 메시지 판독) |
| `19453f182` · `543170693` → `11b1e69ee` | 2 | 검사기 게이트 red(AUTH_USER_MODEL 어노테이션 · #493 격리)다. 동작 결함이 아니다 |
| `59d08c745`(fortune-catalog 슬라이스 0) → `b07567507` | 1 | 겹친 파일은 `settings/base.py` 뿐이다. web CSRF 배선 결함이라 원인이 아니다 |
| `ca5e41a66` → **`36258bbea`** | 1 | **유일한 실제 유출**이다. 원인은 기능 커밋 `585c9c6f0`(P4)이다. F 메시지 원문은 «테스트 전부 팩토리 fake라 미검출»이다. 원인은 보호 부재(fake 배선)이지 약한 단언이 아니다 |

- 결론(실측·판독):
  - **약한 단언 때문에 새어 나간 리팩터 결함: 0**
  - 리팩터가 원인인 유출: 0
  - 리팩터 커밋에서 단언을 강화한 사례: 0
  - 검토 G §6(레인 기록)의 결론과 같다. 전용 리팩터 레인에서 깨진 약 10건은 기존 테스트가 레인 안에서 잡았다.

## 5. 결정 재료

### 5.1 두 선택지의 대가

| | (가) 레인 안 — 0T 에서 본문만 강화 | (나) 별도 요청 |
|---|---|---|
| 편집 수(추정) | 레인당 정밀 중앙값 5 × 0.57 ≈ **3** · 최대 fortune_house 33 → **≈ 19** · BC 23곳 합 ≈ 110 · 1차 파동 K1(8 BC) 정밀 55 → ≈ 31 · K2(3 BC) 15 → ≈ 9 | 같은 110을 별도 레인에서 강화 |
| 레인 길이(추정) | 0T 창 +1(open/close) · 편집당 5~10분 가정(실측 없음) → 중앙값 레인 **+0.3~0.6h**, fortune_house +1.6~3.2h. K1 예산 2~10h · K2 5~15h(plan-v2 §7) 대비 중앙값 레인 약 +5~15% | 소형 레인 선례 1.1~2.8h(중앙값 1.6h — 09-09 skeleton 10레인) + 사용자 게이트(과거 평균 약 3.6/레인) × **5(차수당) ~ 23(BC당)** → 약 **8~37h** |
| 보호 공백(실측) | ⓐ 항목 경로는 레인 안에서 강화된 뒤 0C 가 돈다 | 강화 레인이 **먼저 착륙하지 않으면** 리팩터 레인은 엔드포인트 1개 · 성공 본문 3코드 · 오류 본문 35코드 · 약한 함수 ≈110 · 멤버십 섞인 강한 함수 208 위에서 돈다 |
| 장치·규범 변경 | behavior_guard 0T 판정은 그대로 green 이다(v4 §2.4: 제품 무변 · 케이스 이름 다중집합 동일 — 본문 강화는 둘 다 만족) → **스크립트 변경 0**. 문언 3곳을 바꾼다: coder «0T = ⓐ 수리 테스트 편집»에 강화 편집 추가 · DR «0T 편집 = 보호 동등 확인»을 «동등 또는 강화»로 · Coordinator 가 테스트 쪽 ⓐ 없이 강화만으로 0T 창을 여는 조건. Codex 의미 미러 3곳도 함께 | 플러그인 변경 0. 다만 현행 요청 틀(한 기능)에는 «테스트만 강화» 요청 유형이 없다(리팩토링 커맨드 설계 때 따로 정해야 한다) |
| 위험 | 현재 출력을 그대로 고정하는 방식(특성화)이라 현재 버그도 함께 고정된다(동작 보존 목적에는 맞다). 범위가 번질 수 있다 → «ⓐ 항목이 옮기는 판정을 덮는 테스트»로 한정하면 억제된다. 한쪽 고정 원칙(0T = 제품 동결) 덕분에 강화된 오라클은 리팩터 전 코드에 맞춰 잡혀서, R3 가 제기한 오라클 독립 우려도 줄어든다 | 순서 의존이 생긴다(강화 → 리팩터). 이력상 강화는 리팩터 커밋에서 한 번도 자발적으로 일어나지 않았다(0/68) → 미루면 사실상 안 할 가능성이 높다 |

### 5.2 권고 (결정 아님)

- **(가) 레인 안 허용 + 범위 한정(ⓐ 항목이 옮기는 판정을 덮는 테스트만)**.
- 근거:
  - 레인당 편집 수가 작다(중앙값 약 3).
  - 0T 판정기가 이 편집을 수정 없이 받는다.
  - (나)는 레인 고정비(약 1.6h + 게이트)를 5~23번 치르고, 먼저 착륙해야만 효력이 있다.
  - 강화가 리팩터 커밋에서 자발적으로 일어난 선례가 0이다.
- 반대 근거(선택을 바꿀 수 있는 사실):
  - 약한 단언 때문에 새어 나간 결함이 0이다.
  - 공개 API 는 이미 53개 중 47개가 본문을 정확히 비교한다(나머지 5개는 204).
  - 급하지 않은 것은 분명하다. 규범 표면을 최소로 두려면 (나)도 방어 가능하다.

## 부록 — 측정 파일

| 파일 | 역할 |
|---|---|
| `$S/gitload.py` | `git ls-tree` / `cat-file --batch` 적재 · 버킷 · 층 |
| `$S/classify.py` | 단언 분류기(§2.1) |
| `$S/measure.py` → `out/functions.json` | 함수별 기록 |
| `$S/summarize.py` → `out/summary.md` | 범주별 요약 |
| `$S/table.py` → `out/table.md` | §1 합본 표 |
| `$S/sample.py` · `sample2.py` · `refine.py` → `out/sample*.txt` | §2.3 표본 |
| `$S/endpoints.py` → `out/endpoints.{md,json}` | §3 |
| `$S/history.py` · `history_all.py` → `out/history*.{md,json}` | §4 |
