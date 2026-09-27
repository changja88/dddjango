판정: 수정 후 승인 — blocker 0 · major 2 · minor 7 — X3 처분 13건은 본문에서 닫혔다. ⑤ 실행 규칙은 현장 `testp` 에서 실제로 성립한다: 현장 HEAD 의 두 단계에 무관 실패 13건(postgres 1 · DB 없음 12)이 있다. 원 명령이면 첫 실패에서 멈추고 두 번째 단계는 돌지 않는다. 규칙대로 단계마다 끝까지 세면 새 수집 오류가 가려지지 않고, 무관 순서 의존 실패 1건은 요동 규칙으로 걸러진다. 남은 major 는 둘이다. 6a 에서 기능 슬라이스 뒤에 슬라이스 0 을 재개봉하면 ⑤ 가 기능 변경까지 슬라이스 0 의 새 실패로 센다. (나) 명세 참조 줄의 맨 이름 grep 은 다른 영역이 스스로 정의한 같은 이름 helper 를 편집 범위로 연다.

# 로드맵 6b 설계 v4 적대 재검토 X4 (2026-09-27)

- 대상: `workspace/eval/web-refactor-entry/design-v4.md`(이하 «설계» · 행 번호는 이 파일 기준) · 앞 검토 `review-X1..X3-*.md` · `diagnosis.md`. 플러그인 기준 HEAD 는 `c9fcadff` 다.
- 실측 환경: scratch `…/scratchpad/6b-review-X4/`
  - 현장 사본 `sds/`·`sds2/`(`git clone --shared` · 현장 HEAD `09a41129b`). `sds2` 의 실험 가지는 `x4-c` 다.
  - 합성: `rc/`·`rc2/`(pytest 동작) · `subst/`(설계 §7-2 문면 시제품 `subst_v4.py`).
  - 테스트는 현장 `.venv` 의 python(pytest 8.4.2 · xdist 3.8.0)을 `PYTHONDONTWRITEBYTECODE=1`·`-p no:cacheprovider` 로 사본 cwd 에서 돌렸다. `uv run` 은 쓰지 않았다(플래그 의미는 같다).
  - 현장 원본은 clone·읽기에만 썼다. 모델 호출 0 · 서브에이전트 0 · Serena·Graphify 미사용.
- 표기: [실측] = 명령·실험 결과 · [추정] = 확인하지 않은 판단.
- 원칙 필터
  - 이 검토의 권고에는 테스트 보강과 보호 장치 신설이 없다. 기존 테스트 **실행**(같은 명령의 재실행 포함)은 보강이 아니다.
  - 사용자 결정 질문은 0건이다.
  - X1~X3 에서 닫힌 항목은 다시 올리지 않았다.

## 설계자가 물은 5곳 — 짧은 답

| 물음 | 답 | 항목 |
|---|---|---|
| §7-1 ⑤ 실행 규칙이 현장 `testp`(xdist · postgres)에서 성립하는가(요동 포함) | **성립한다** [실측]. `make -n testp` 는 `&& \` 로 이은 두 줄을 낸다. 떼어 낼 fail-fast 는 두 단계의 `--maxfail=1` 뿐이다(`addopts` 는 `--strict-markers` 만). 현장 HEAD 에서 DB 없는 단계(7,702건 · `-n auto`)를 규칙대로 돌리면 **무관 실패 12건 · 7,690 통과 · exit 1 · 351초**다. postgres 단계(2,520건 · `-n0`)도 무관 실패 1건 · 788초다. 원 명령 `testp` 였다면 postgres 단계 첫 실패에서 `--maxfail=1` 로 멈추고 `&&` 때문에 DB 없는 단계는 돌지도 않는다 — X3 B1 이 말한 가림이 현장 HEAD 에 실재하고, 단계 분리·fail-fast 떼기가 그것을 푼다. 같은 단계에 모듈 머리 import 파손(`x4-c`)을 넣으면 차집합이 셋이다. 수집 오류 `ERROR <모듈 경로>` 2건은 새 실패이고, 모듈 단독 재실행에서도 재현된다. 나머지 `FAILED tests/test_deployment_config.py::test_application_command_passes_special_environment_values_as_data` 1건은 개명과 무관하다(사본의 `.venv/bin/python` 부재 FileNotFoundError). 이 1건은 노드 단독 재실행에서 통과해 «요동»으로 떨어진다. 요동 규칙이 현장에서 실제로 일하는 모습이다. xdist 에서는 `--continue-on-collection-errors` 가 없어도 수집 오류로 멈추지 않는다. `-n0` 인 postgres 단계에는 이 플래그가 필요하다. 틈은 둘이다. `-r` 은 마지막 것만 먹는다(m1). DB 가 뜨지 않으면 모든 테스트가 setup ERROR · exit 1 로 «성립»한다(m2). 비용 수치도 틀렸다(m3) | m1 · m2 · m3 |
| §7-2 바인딩 적용이 `as`·상대 import·`__init__` 재수출에서 오판하는가 | **거짓 green 은 없다**(⑤ 가 덮는 1형 제외) [실측 `subst_v4.py` 11사례]. `as` 별칭 유지 · 상대 import 무변 · 재수출 경유 이름 치환 · `mocker.patch` 문자열은 green 이다. 거짓 red 는 넷이다: `from N import new as old` · 재수출 경유 → 정의 모듈 직접 · `import M as vm` · `from pkg import m`. 모두 fail-closed 이고, 현장 테스트에는 이 모양이 0이다(web import 의 `as` 0 · 상대 import 0 · web `__init__` 재수출 0 · `import web.` 는 부수효과 1건). 구현이 접두 쌍을 성분 경계 없이 적용하면 `web.a.q` 쌍이 `web.a.q2` 를 삼켜 거짓 green 이 난다 — 문면에 성분 경계를 적는다 | m7 |
| §3-3 (나) 맨 이름 grep 이 무관 적중을 편집 범위로 여는가 | **연다** [실측]. 플러그인 자신의 «반복 > 상속» 규칙 때문에 영역마다 같은 이름의 비공개 helper 를 따로 둔다. `_render_page` 는 intake·related_persons 가 각자 정의하고, `_PAGE_TEMPLATE` 은 3영역 5파일, `_BG_SESSION_KEY` 는 2영역 3파일이다. intake 의 `_render_page` 이동(X2 의 대표 사례)에서 (나) 는 `related_person_list_view.py:57·67` 을 «참조 문자열 치환» 줄로 연다 | M2 |
| §4-4 API 계약 «근거 칸 리터럴 결속»이 우회되는가 | **구조적으로 가르지 못한다** [실측]. 현장 `response/` 의 `속성=…"키"` 한 줄 대입 167행 중 166행이 속성 이름 = JSON 키다. 속성 이름 정리 항목을 그 행에 걸고 근거 칸에 `"birth_date"` 를 적으면 결속이 선다. 첫 관문은 리뷰어의 «아니오 — API 계약»이고, 새는 몫은 G0 별도 요청 목록에 보인다 | m6 |
| §7-3 e 6a ⑤ 추가가 6a W-T1~T9 결론과 모순인가 | **W-T 결론과는 모순이 없다.** W-T1~T8 은 G0 전 정지이고, W-T9 은 끝 green ①~③ 책상 재생이다. ⑤ 는 확인을 하나 더할 뿐이다(`tests/test_settings_profiles.py:131·148` 은 `storages[…].url()` 문자열 조립이라 개명 뒤에도 통과한다 — 그 파일이 필요한 것은 ③ 때문이다). **설계 안에는 모순이 있다**: 6a 에서 기능 슬라이스 뒤의 슬라이스 0 재개봉은 기능 변경이 든 HEAD 를 슬라이스 0 전 기준선과 비교한다 | M1 |

---

## X3 처분의 실효 (볼 것 1)

왼쪽 칸은 X3 의 항목 번호이고, 판정 칸의 M·m 번호는 이 검토(X4)의 항목이다.

| X3 | 설계 v4 | 판정 |
|---|---|---|
| **B1** 수집 오류·fail-fast | §7-1 :285-292 · §8 :348 · W6-T13 | **닫힘**(현장 실측 — 위 표). 남은 틈은 명령 조립의 세부(m1)와 성립 조건의 빈칸(m2)이다 |
| M1 ast 적용 순서 | §7-2 :307-313 | **닫힘.** 문면 순서(원문 파싱 → 바인딩에 쌍 적용 → import 밖은 텍스트 역치환)대로 옮긴 시제품에서 설계 W6-T8 의 정의 이동 사례가 green 이다. 성분 경계는 m7 |
| M2 끝 green 뒤 재확인 | §7-1 :293 · §8 :348 | 리팩토링 모드는 **닫힘.** 6a 확장 문장이 새 모순을 만든다(M1) |
| M3 편집 줄 키 전체 편입 | §3-2 4 :119-121 | **닫힘** |
| M4 6a 에도 ⑤ | §7-3 e :326 · §7-4 | **닫힘.** 재개봉 시점은 M1 |
| M5 (나) 명세 참조 줄 | §3-3 :134-139 · §3-4 · §4-4 :198·:202 | **순환은 닫힘.** 무관 적중과 편집 종류 문면은 M2 |
| m1 활용형 오적중 · self-test | §5-3 :236-243 · §5-2 :224·:229 | **닫힘**(`:174`·`:176`·`design-review-web.md:46` 셋 다 무효 [실측 `polarity4.py`]). 조건절 «할 수 있다면»은 m5 |
| m2 괄호 부속절 예외 | §5-3 :248 ⑤ | **닫힘.** v4 규칙으로 렌즈 문서의 괄호 허용 문장은 4개다(`architecture-web/SKILL.md:27` · houserules `final.md:130·139` · implementation-ui `final.md:204`). 예외가 여는 몫은 G0 목록의 «위반 인용 ↔ 제외 인용» 나란히 표시로 보인다 |
| m3 §4-4 현장 모양 | §4-4 :196-197 | **대체로 닫힘.** 외부 동작 ④ 는 현장 Django `render(` 호출 29개 중 26개(모듈 상수)에 맞는다. API 계약 결속은 m6 |
| m4 배선 적용 | §2-2 :73 | 진입 준비 ③·step 1 은 **닫힘.** Phase 2 반송 처리의 배선 경로(web `:212` (가))는 m4 |
| m5 · m6 · m7 | §7-1 :292 · §11 · §7-2 :299 | **닫힘** |

---

## Major

### M1. 6a 에서 기능 슬라이스 뒤 슬라이스 0 을 재개봉하면, ⑤ 가 기능 슬라이스가 깬 기존 테스트를 슬라이스 0 의 새 실패로 센다 (§7-1 :293 · §7-3 e :326 · §8 :348)

- **문면**(:293): «6a 기능 요청에서는 기능 슬라이스가 뒤따르므로 ⑤ 는 **슬라이스 0 끝과 슬라이스 0 재개봉 때만** 다시 돌고(기능 슬라이스의 의도된 동작 변경은 ⑤ 판정 밖)».
- **왜 모순인가**
  - 기준선은 Phase 2 진입 준비 ④ 직후 한 번 잡는다(:276). 기능 슬라이스 전이다.
  - 6a 의 슬라이스 0 재개봉은 기능 슬라이스 **뒤**에 일어난다. G2 직전 홀리스틱 감사 반영(web `:216` — 감사 범위에 슬라이스 0 파일이 든다) · 백스톱 diff 게이트 반송(`:217`) · Phase 3 `--debt-residual` 재실행(`:222`)이 그 경로다.
  - 그때 HEAD 에는 기능 슬라이스가 들어 있다. «지금 실패 − 기준선 실패»에는 기능이 깬 기존 테스트가 그대로 들어온다. 괄호 속 «⑤ 판정 밖»은 이 비교로는 성립할 수 없다.
- **결과**
  - 처분 규칙(:292)은 새 실패를 «슬라이스 0 이 동작 불변으로 고친다(테스트 단언을 고쳐 맞추지 않는다)»로 보낸다. 기능 변경이 원인이면 두 길밖에 없다. 하나는 G2 직전의 거짓 `ⓐ 재상정` STOP 이다. 다른 하나는 coder-web 이 슬라이스 0 재개봉에서 기능 동작을 되돌려 옛 테스트를 맞추는 것이다.
  - 현장에서 드문 경우가 아니다 [추정]. `tests/web` 에는 화면 구조를 통째로 단언하는 테스트가 있다. 예를 들어 `tests/web/preferences/test_settings_profile_wonbo.py:148` 은 설정 메뉴 그룹 목록 전체(`["상담", "사주", "결제 · 계정", "앱 정보"]`)를 단언한다. 설정 화면에 그룹 하나를 더하는 수정 모드 요청은 이 단언을 깬다.
  - 리팩토링 모드에는 기능 슬라이스가 없으므로 해당하지 않는다.
- **고칠 말**(:293 괄호 뒤 1문장 — 새 장치 없음, 같은 명령을 한 번 더 돈다)
  - «6a 에서 기능 슬라이스 커밋 뒤의 슬라이스 0 재개봉은, 재개봉 편집 **직전** HEAD 에서 같은 ⑤ 명령을 한 번 돌려 그 실패 집합을 그 재개봉의 기준선으로 쓴다(새 실패 = 재개봉 뒤 − 재개봉 직전). §8 G2 배너의 기존 테스트 행에는 두 기준선의 HEAD 를 함께 적는다.»
  - W6-T14 에 «기능 슬라이스가 기존 테스트 1건을 깬 뒤 슬라이스 0 재개봉 → 재기준선으로 새 실패 0» 1가지를 더한다(책상 재생 · 모델 호출 없음).

### M2. (나) 명세 참조 줄의 맨 이름 grep 이 다른 영역의 같은 이름 helper 를 편집 범위로 연다 — 편집 종류 문면도 grep 과 어긋난다 (§3-3 :134 · :141 · §3-4 :147-149)

- **실측**(현장 web/ · 6a 참조 완전성 pathspec · 단어 경계)

| 옛 이름 | 적중 파일(web/) | 스스로 정의하는 영역 |
|---|---|---|
| `_render_page` | `web/intake/user_info/view/user_info_view.py:68·76` · `web/related_persons/related_person_list/view/related_person_list_view.py:57·67` | intake · related_persons 둘 다 `def _render_page(` |
| `_PAGE_TEMPLATE` | auth 2파일 · intake 1 · related_persons 2 | 5파일 모두 각자 모듈 상수 |
| `_BG_SESSION_KEY` | auth 2파일 · intake 1 | 3파일 모두 각자 모듈 상수 |
| `redirect_if_employee_unset` | 정의 1 + 소비 VM 6(모두 `from <정의 모듈> import redirect_if_employee_unset`) | employee_choice 만 |

- **원인**: 영역마다 같은 이름의 비공개 helper 를 두는 것은 우연이 아니다. dddjango-web discipline-cleancode 의 «반복 > 상속 — base 클래스·공용 헬퍼 금지»가 만드는 정형이다. 그리고 M 항목의 전형(X2 `x2-c`)이 바로 이 비공개 helper 의 이동·개명이다.
- **결과**
  - intake 실행이 `_render_page` 를 옮기거나 개명하면 related_persons 의 `_render_page` 정의·호출 줄이 (나) 목록에 든다.
  - 그 줄에 WI·WP 발견이 있으면 편집 줄 키가 된다. 키 전체 편입(§3-2 4)으로 related_persons 파일의 다른 발견 줄까지 끌려와 `## G0 재승인` 질문에 오른다. 무관한 질문이다.
  - coder-web 은 `refactor-scope.md` 에서 그 줄을 «옛 이름 → 새 이름 치환 대상»으로 읽는다 [추정]. related_persons 의 목록 화면 helper 를 `render_user_info_page` 로 바꾸면 이름이 틀린 것이 된다. §3-3 확인 항목(«(나) 줄은 참조 문자열 치환뿐»)과 §3-4 대조는 이것을 통과시킨다.
- **편집 종류 문면**(같은 곳의 짝 결함): (나) 의 grep 은 옛 이름 적중 — 소비 파일의 **호출 줄** 포함 — 을 여는데, 허용 편집은 «참조 문자열 치환만(import 줄의 모듈·이름 · 템플릿 이름 문자열 · `{% static %}` 경로)»으로 호출 줄 이름 치환이 목록에 없다. 개명(끝 성분이 다름)이면 소비 VM 6개의 호출 줄(`chart_view_model.py:232` 등)을 고칠 수 없다. 이렇게 읽히면 교차 단위 개명은 끝나지 않는다.
- **고칠 말**(:134 — 새 장치 없음, 같은 grep 의 적중을 좁히고 편집 종류를 grep 과 맞춘다)
  - «옛 이름 적중은 그 이름을 **스스로 정의하지 않는** 파일의 줄만 든다(같은 이름의 `def`·`class`·모듈 수준 대입이 있는 파일은 뺀다 — 영역마다 같은 이름의 비공개 helper 를 두는 정형 때문이다).»
  - 편집 종류 괄호에 «그 파일 안 옛 이름 참조(호출·속성 참조)의 이름 치환»을 더한다.
  - W6-T5 또는 W6-T0 에 «intake `_render_page` 이동 명세 → (나) 에 related_persons 줄 없음» 1사례를 더한다(plan 러너 사례 · 모델 호출 없음).

---

## Minor

- **m1 `-rfE` 를 «붙인다»만으로는 부족하다 — pytest 는 마지막 `-r` 만 쓴다** [실측 `rc/`] (§7-1 :288)
  - 현장 단계 줄에는 `-rF` 가 이미 있다. `-rfE … -rF` 순서면 `ERROR` 줄이 사라진다. 수집 오류가 식별자 없이 빠져 X3 B1 의 주 사례가 다시 샌다. `-rF … -rfE` 순서면 나온다.
  - 고칠 말: «원문의 `-r<문자>` 는 떼고 `-rfE` 를 줄 **끝**에 붙인다(pytest 는 마지막 `-r` 하나만 쓴다).»
- **m2 DB 가 뜨지 않은 단계는 exit 1 로 «성립»한다 — §11 의 «판정 불가» 기대와 어긋난다** [실측 `rc2/` 합성] (§7-1 :290 · §11 :407)
  - 세션 fixture(DB 기동)가 실패하면 테스트마다 `ERROR … at setup` 이 나오고 exit 1 이다. 성립 조건(«pytest 0·1»)상 판정 가능이다. 기준선 실패 = 단계 전부, 뒤 실행도 전부라 «새 실패 0»이 된다.
  - §11 은 «postgres 단계는 가능한 환경에서만 — 불가면 «판정 불가 단계» 표기 확인이 합격»이라고 적었다. 문면대로 구현하면 그 표기가 나오지 않는다.
  - 고칠 말(:290 성립 조건에 1구): «기준선 실행에서 통과가 0(수집된 테스트 전부가 실패·에러)인 단계도 판정 불가다.»
- **m3 비용 수치가 틀렸다 — DB 없는 단계는 95초가 아니라 약 6분이다** [실측] (§7-3 :329 · §11 :407 · §13 :439)
  - 95초는 X3 가 `tests/web` 만 돌린 값이다. `testp` 의 DB 없는 단계는 testpaths 전체 7,702건이고 `-n auto` 로 351초다. postgres 단계는 2,520건 직렬(`-n0`)로 **788초(13분)**다. 한 번 돌리는 데 약 19분이다.
  - ⑤ 는 기준선·끝에 더해 끝 green 뒤 재호출마다 다시 돈다(:293). 슬라이스 0 이 있는 기능 요청마다 최소 약 38분(기준선 + 끝)이고, 재확인 1회마다 19분이 더 든다.
  - 고칠 말: §7-3 비용 문장과 §13 «보고할 것»의 사용자 알림 문장에 이 벽시계를 적는다(결정 17 번복을 알릴 때 비용이 사용자 판단 재료다).
- **m4 Phase 2 반송 처리의 배선 경로(web `:212` (가))가 두 모드에서 ④ 와 부딪힌다** (§2-2 :73 · §7-1 :293)
  - 리팩토링 모드: §2-2 는 step 1 과 진입 준비 ③ 만 뺐다. 슬라이스 0 중 coder-web 이 «web/ 밖 수정 필요»를 보고하면 `:212` (가)가 «승인 하 직접 적용»으로 settings·루트 urls 를 바꾼다. `git_snapshot` 뒤라 ④ 가 «테스트 밖 web/ 밖 파일»로 red 가 되어 끝 green 이 영영 서지 않는다.
  - 6a: 기능 슬라이스 중 같은 경로로 배선을 적용하면 G2 직전 ④(`git_snapshot..HEAD`)가 같은 이유로 red 다.
  - 고칠 말: 리팩토링 모드는 §2-2 끝에 «`:212` (가) 배선 경로도 쓰지 않는다 — 그 항목은 `ⓐ 재상정`» 1구. 6a 는 §7-3 a 에 «G2 직전 ④ 는 `:212` (가)로 적용한 배선 파일을 뺀다(배선 6종 대상 파일)» 1구.
- **m5 조건절 «할 수 있다면»이 유효 허용으로 남는다** [실측 `polarity4.py`] (§5-3 :240·:242)
  - `discipline-cleancode/references/final.md:333·391` «다른 함수를 추출할 수 **있다면**, 그 함수는 여러 작업을 하고 있다»는 위반 판별 기준인데, 무효 접미(`는`·`고`·`라는`·`라고`)에 `면` 이 없어 허용 술어로 남는다. 같은 문서의 서술문 5개(`:1057·1144·1355·2221` · `:625`)도 `할 수 있다` 로 적중한다.
  - 고칠 말: 무효 접미에 `면` 을 더하고, self-test 극성 표본에 «할 수 있다면 → 무효»를 넣는다. 서술문은 계획의 «규범 문서 한정» 목록이 가른다(discipline-cleancode 가 렌즈 문서이므로 그 목록에서 `(쓸|둘|할) 수 있다` 적용 여부를 명시한다).
- **m6 API 계약 리터럴 결속은 속성 이름과 키가 같은 행에서 가르지 못한다** [실측] (§4-4 :197)
  - 현장 `web/client/*/response/*.py` 의 `속성=…"키"` 한 줄 대입 167행 중 166행이 속성 이름 = 키다(`birth_date=_optional_str(payload, "birth_date")`). 문면의 목적(«상수·필드·속성 이름의 정리는 client 내부 정리라 빠지지 않는다»)이 이 행에서는 서지 않는다.
  - 새는 몫은 G0 «별도 요청» 목록에 보이고, 리뷰어 «아니오 — API 계약»이 첫 관문이다. 그래서 minor 다.
  - 고칠 말(선택 — 그대로 두어도 된다): «그 리터럴 값이 같은 행 대입 대상 이름과 같으면 API 계약 근거가 서지 않는다 — 속성 이름 정리로 풀린다.» web 표준이 백엔드 계약 키 자체를 바꾸라고 요구할 일은 드물다. 그래서 이 좁힘이 참 계약 항목을 막을 일도 드물다 [추정]. 막히더라도 fail-closed(채택 → 사용자 ⓑ)다.
- **m7 경로·폴더 점 경로 쌍의 «접두»에 성분 경계를 적는다** [실측 `subst_v4.py` C8] (§7-2 :310)
  - 쌍 `web.a.q → web.a.m` 을 문자열 접두로 적용하면 무관한 `web.a.q2.z` 가 `web.a.m2.z` 로 바뀐다. 기준에 `web.a.m2.z` 가 있으면 거짓 green 이다. 텍스트 역치환은 «단어 경계»가 적혀 있지만 바인딩 접두 적용에는 없다.
  - 고칠 말: «접두는 점 성분 경계로만(`N` 과 같거나 `N.` 으로 시작)» 1구 · W6-T8 에 1사례.

## v4 가 새로 들인 것 (볼 것 3)

| 곳 | 판정 |
|---|---|
| 리팩토링 모드 배선 미적용(§2-2 · 도11) | step 1 · 진입 준비 ③ 은 맞다. 반송 처리 배선 경로가 남는다(m4) |
| `의 예외` 적중 좁힘(§5-3 :238) | 맞다. `commands/dddjango-web.md:176` 무효 [실측]. `의 (명시 )?예외(…)` 는 앞 항 `(명시 )?예외(…)` 에 포함돼 중복이나 해는 없다 |
| 괄호 부속절·`예외:` 뒤 ⑤ 예외(§5-3 :248) | 맞다. 렌즈 문서 4문장에만 걸리고, 여는 몫은 G0 목록에 보인다 |
| §4-4 `render(` 호출 구간 ast · 모듈 상수 해석 | 맞다 [실측 `render_scan.py`]. 현장 Django `render(` 호출 29개(VM `.render()` 메서드 5개 제외) 중 26개가 같은 파일 모듈 상수다. 남는 3개는 `_render_fragment` 의 튜플 언팩 지역 이름 2(`user_info_view.py:144` · `related_person_editor_view.py:110`)와 조건 대입 지역 이름 1(`conversation_view.py:41`)이다. 이 셋은 근거가 서지 않아 채택으로 떨어진다(fail-closed). 그 fragment 라우트는 `urls.py` `path(` 행(①)으로 근거를 댈 수 있으므로 문면을 바꿀 필요는 없다 |
| `--subst-check` 바인딩 적용(§7-2) | 위 «설계자가 물은 5곳» 2행 · m7 |
| 6a ⑤(§7-3 e) | W-T 결론과 모순 없음 · 재개봉 시점은 M1 |

## 새 장치 과잉 · fail-open (볼 것 4)

| 곳 | 판정 |
|---|---|
| fail-open | M2(무관 영역 줄 편집 허용) · m1(`-r` 순서로 수집 오류 누락) · m2(DB 불가 단계 «새 실패 0») · m5 · m6 · m7 |
| 늦은 정지(fail-closed) | M1(6a 재개봉 거짓 STOP) · m4(배선 경로 ④ red) · §7-2 거짓 red 4형(현장 0) · §4-4 지역 이름 템플릿 인자 |
| 과한 장치 | 없음. 권고는 모두 문면 1~2구이고, M1 은 같은 명령을 한 번 더 돌리는 것이다 |

## 실측 기록 (scratch `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/6b-review-X4/`)

- `make -n testp`(사본): 두 줄 · `&& \` 연결 · 두 단계 모두 `-rF … --maxfail=1 --strict-markers`. `pyproject.toml` `addopts = "--strict-markers"` 뿐.
- `stage2-base.out`: DB 없는 단계를 ⑤ 규칙대로(`--maxfail` 뗌 · `--continue-on-collection-errors` · 끝에 `-rfE`) 돌렸다. `12 failed, 7690 passed in 351.16s` · exit 1 · `FAILED` 12줄(`tests/test_service_step*_*.py` 계수 단언 — 커밋된 HEAD 의 무관 실패). 실행 뒤 사본 `git status` 무변.
- `stage1-base.out`: postgres 단계(2,520건 · `-n0`)를 같은 규칙으로 돌렸다. `1 failed, 2477 passed, 42 skipped in 787.83s` · exit 1 · 무관 실패 1건(`tests/test_service_snapshot_db_seed.py::test_rows_snapshot_lists_every_seeded_object_with_the_declared_fields_of_models_md`). **원 명령 `testp` 는 이 1건에서 `--maxfail=1` 로 멈추고, `&&` 때문에 DB 없는 단계는 아예 돌지 않는다.** 설계의 «단계마다 따로 · fail-fast 떼기»가 없으면 현장 HEAD 에서 ⑤ 는 postgres 단계 1건만 보는 셈이다.
- `stage2-x4c.out`(`sds2` 가지 `x4-c`): `signup_view_model._BG_SESSION_KEY` 개명(테스트 무변) 뒤 DB 없는 단계를 같은 규칙으로 돌렸다. `13 failed, 7666 passed, 2 errors in 337.80s` · exit 1. 기준선 대비 차집합은 3이다. `ERROR tests/web/auth/password_reset/test_password_reset_view_model_background_video.py` · `ERROR tests/web/auth/signup/test_signup_view_model_background_video.py`(수집 오류 · 모듈 단독 재실행에서 재현) · `FAILED tests/test_deployment_config.py::…special_environment_values_as_data`(무관 · 단독 재실행 통과 = 요동). 원 명령(`-rF`)이었다면 `ERROR` 두 줄은 요약에 나오지 않는다.
- `rc/`: `-rF -n0 --maxfail=1` 에 수집 오류 → exit 1 + `stopping after`(성립 조건의 `stopping after` 규칙이 필요한 이유) · `-rF -n0` → exit 2 `Interrupted` · `-n 3` 은 플래그 없이도 수집 오류로 멈추지 않음 · `-rfE … -rF` → `ERROR` 줄 없음 · `-rF … -rfE` → 있음.
- `rc2/`: 세션 fixture 실패 → 테스트마다 `ERROR … RuntimeError` · exit 1(m2).
- `subst/subst_v4.py`·`cases.py`: 설계 §7-2 문면 시제품 11사례(설계자 물음 2행 · m7).
- `polarity4.py`·`polarity4.out`: v4 긍정 술어·부정형·무효 접미 규칙으로 web 코퍼스 유효 문장 46 · 부정 단서 동석 12(모두 섞인 문장 — ⑤ 몫) · v3 오적중 3 해소 확인 · 조건절 2(m5).
- `render_scan.py`: 현장 web `.py` 의 `render(` 템플릿 인자 분류(Django `render` 29 = 모듈 상수 26 · 지역 이름 3 · 그 밖 5는 VM `.render()` 메서드).
- 현장 grep: 맨 이름 적중(M2 표) · 테스트 import 모양(`as` 0 · 상대 0 · `import web.` 1) · web `__init__` 재수출 0 · `response/` 한 줄 대입 167행 중 속성 = 키 166행(m6).
- 저장소에 쓴 파일은 이 검토 1개다. 커밋·push 없음. 현장 원본에는 쓰지 않았다.
