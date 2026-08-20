# STOP_FOR_USER_APPROVAL — G1 (기록이 정본 · 질문은 입력 채널)

기능: 주문 생성(재고 확인·차감) API · 폴더 `.dddjango/20260820-2338-order-placement/`
발생 시점: Phase 1 G1 제시 직전 (architect 반영·중재 완료 후)
실행 모드: **대화형 세션** → 기록 파일을 쓴 뒤 같은 선택지를 AskUserQuestion 으로 제시한다. 임의 정지 커밋을 만들지 않는다.

## 왜 이것이 위임되지 않는가

발주문은 «G1 / G2: 무수정 승인»으로 **일반 게이트 승인 입력**을 위임했다. 그러나 위임되는 것은 승인 입력뿐이며 `STOP_FOR_USER_APPROVAL`·shape 승인·이관 빚 목록 승인은 위임되지 않는다. 그리고 «설계 전체에 대한 일반 G1 승인은 shape 변경 승인을 대신하지 않는다». 아래 넷은 **밖에서 보이는 결과 또는 게이트 판정 방식이 갈리는** 물음이므로, 논증이 완성돼 있어도 STOP 이다(완성된 논증은 STOP 을 생략할 근거가 아니라 STOP 기록에 인용할 재료다).

---

## 물음 ⑴ — 오류 응답의 exact body shape 와 code 집합

제안(명세 §4.3 slot 6·8·9): media type `application/json` · 본문 `{"code": <literal>, "message": <문장>}` 두 필드 고정 · code 집합 6종(`product_not_found` · `insufficient_stock` · `invalid_request` · `invalid_product_id` · `invalid_quantity` · `stock_contention`) · `message` 문면은 계약이 아님 · 값 범위 위반 400 · 파싱 실패 400.

| # | 닫히는 선택지 | 그 선택의 대가 |
|---|---|---|
| 1-A | **제안 그대로 승인** | 아래 대안들이 주는 것(표준 형식·세분 필드·status 이원화)을 이번에 얻지 않는다. 소비자 0 인 지금 굳히는 계약이므로 이후 변경은 breaking 이다 |
| 1-B | RFC 9457 Problem Details(`application/problem+json` · `type`/`title`/`status`/`detail`) | 소비자가 0인 신규 표면에 wire 필드 5종과 `type` URI 운영 부담을 미리 지고, 별도 요구가 없는 형식을 표준으로 굳힌다 |
| 1-C | 본문에 `detail`·`errors[]`·`field` 추가 | 필요를 확인할 소비자가 아직 없는 필드를 계약에 넣고, 넣은 뒤에는 하위 호환 때문에 빼기 어렵다 |
| 1-D | 오류 본문 없이 status 만(빈 body) | 400 이 «본문을 못 읽음»인지 «수량 범위 위반»인지 소비자가 구분할 수 없어 조치·재시도 판단이 불가능해진다 |
| 1-E | code 집합을 3종으로 접기(입력 위반 전부 `invalid_request`) | 소비자가 «본문 형식을 고친다/`product_id` 를 고친다/`quantity` 를 고친다»를 구분하지 못해 §4.2 가 주장한 구분이 wire 에서 사라진다 |
| 1-F | 값 범위 위반을 **422** 로 가르기(파싱 400 / 의미 422) | status 축과 code 축에 같은 구분을 이중으로 싣게 되어 소비자가 두 축을 함께 해석해야 하고, 이후 모든 필드 검증에 그 경계를 일관 적용할 의무가 생긴다 |
| 1-G | `message` 문면을 계약으로 승격 | 문구 수정이 breaking change 가 되고 §7 A-행이 문자열 동등 단언으로 굳어 리팩터링 내성이 떨어진다 |

**권고**: 1-A. 저자 = design-architect(명세 §8.2 ⑴ «제안»). 근거는 명세가 적은 그대로이며 코디네이터가 새 근거를 제조하지 않았다.

---

## 물음 ⑵ — profile 라벨과 그 라벨이 부르는 slot 5–12 constraint set

이 표면은 **신규인데 Ninja 가 아니고 wire 는 프로젝트 고유 JSON code 계약**이라 열거된 두 값(`dddjango-code-json` | `preserve-established`) 어디에도 정확히 앉지 않는다. api 리뷰어가 blocker F-1 로 올렸고 `architecture-api` §5.4 마지막 문단이 이 조합을 STOP 대상으로 지정한다.

| # | 닫히는 선택지 | 그 선택의 대가 |
|---|---|---|
| 2-A | `preserve-established` 라벨을 carrier 로 차용 | 보존할 관찰 계약이 0인데 «보존» 라벨을 쓰므로 slot 5–12 의 «관찰된 native artifact 또는 evidence 있는 none» 규칙이 공전하고, 실제로 채택한 module·Enum·좁힘 base 가 라벨이 부르는 constraint set 밖에 놓여 감사 때마다 라벨↔실물 불일치가 반복 지적된다 |
| 2-B | `dddjango-code-json` 라벨 채택 + Ninja 전용 항목 명시 면제 | 이 라벨은 «새 dddjango **Ninja** 범위의 기본»으로 정의돼 있어 스택 전제가 어긋나고, Ninja 전용 계약 문장(`Status(...)`·`response=` 광고·framework-owned 422/429 목록)이 대응 없이 걸려 면제 목록을 사람이 유지해야 한다. 반면 slot 5–12 의 실물은 **이미 이 라벨의 constraint set 과 일치**한다 |
| 2-C | 열거 밖 제3 라벨을 만든다(예: `dddjango-code-json (plain Django)`) | G2 게이트·12-slot 표기 도구가 모르는 값이라 이후 모든 판정이 사람 판단에 의존하고, 다음 기능이 같은 이름을 재발명할 위험이 생긴다 |

**권고**: 2-B. 저자 = design-architect(명세 §8.2 ⑵ B 항의 «slot 5–12 의 실물이 이미 이 라벨의 constraint set 과 일치»). 코디네이터의 판단이 아니다.

---

## 물음 ⑶ — 그 조합의 G2 게이트 취급

| # | 닫히는 선택지 | 그 선택의 대가 |
|---|---|---|
| 3-i | code-profile 게이트 계약을 적용하되 Ninja 전용 항목만 «해당 없음»으로 명시 면제 | 면제 목록을 사람이 유지해야 하고, 면제가 늘어날수록 게이트가 실질적으로 무력해진다 |
| 3-ii | preserve 게이트 계약(관찰 native 보존 검사)만 적용 | 보존할 관찰물이 0이라 게이트가 사실상 아무것도 검사하지 않는다(무검사 통과) |
| 3-iii | 이 표면을 «신규 profile 조합 · 사람 판정»으로 표시하고 G2 에서 12-slot 문면 대조만 한다 | 자동 백스톱이 없어 회귀 탐지가 감수자 주의력에 의존한다 |

**권고 불가** — 명세가 셋을 대등하게 놓고 우열 근거를 적지 않았고, 리뷰 노트도 셋 중 하나를 지목하지 않았다. 코디네이터가 즉석에서 설계 근거를 제조하지 않는다(갈림길 표면화 경계).

---

## 물음 ⑷ — `config/settings.py` 미이관에 따른 «이관 빚» 목록 승인 (Z-1)

`application/` 컨테이너를 처음 채택하면 표준 트리 검사기가 켜지면서 `[#429] config/settings.py` 한 건이 앵커 차분에 **«신규 귀속»으로 잡힌다**. 규정상 «미이관 표준 경로 의존이 유일한 잔존 귀속이면 임의 수용하지 않고 `STOP_FOR_USER_APPROVAL` 로 표면화»해야 하고, 승인되면 사용자 승인 «이관 빚» 목록(`registry_gate.py --legacy-debt-file`)으로 기록·격리한다.

| # | 닫히는 선택지 | 그 선택의 대가 |
|---|---|---|
| 4-A | 기본 — 그대로 두고 `#429 config/settings.py` 한 줄을 승인 이관 빚 목록에 넣어 G2 를 돌린다 | 표준 `<project>/settings/<environment>.py` 채택이 미완으로 남고, 그 사실이 빚 목록으로 계속 보고된다 |
| 4-B | 이관 — `settings/base.py`+`settings/development.py` 로 분할 | `manage.py`·`wsgi.py`·`asgi.py` 세 곳의 `DJANGO_SETTINGS_MODULE` 갱신, `BASE_DIR` 한 단계 보정(잘못하면 `db.sqlite3` 를 다른 위치에서 찾는다), 그리고 G0 가 «미룰 수 있음»으로 판정한 `[#493]` 17건이 새 경로로 옮겨 붙어 그 17개 모듈 변수 타입 달기까지 한 묶음으로 끌려온다(스코프 확장 = G0 재승인 사안) |

**권고**: 4-A. 저자 = design-architect(명세 §8.3 Z-1 기본 «이 파일은 이번 승인 스코프의 산출물 목록 밖이라 명세가 이동을 결정으로 박지 않는다»). 규정도 스코프 확장을 G0 재승인 사안으로 둔다.

---

## 위임된 것 (이 STOP 의 대상이 아님 — 발주문 «G1 무수정 승인»으로 기본값 수락)

Y-ⓐ 멱등성 미적용 · Y-ⓑ 인증·인가 미적용 · Z-2 재고 확보 실패의 공개 의미(503+`Retry-After: 1`) · Z-3 catalog 이주 미적용 · Z-4 재시도 3회 · Z-5 UoW 안 크로스-BC 포트 호출 채택 · Z-6 테스트 DB 파일 고정.

---

## 응답 기록

(응답 수신 시 선택지·시각을 여기에 추기하고 재개 첫 커밋에 포함한다.)
