# 규칙 글 최종 문안 — dddjango 2.44.0 (설계 확정 · 2026-11-21 · 운영자)

출처: 검토 P 첫 검토 «다듬은 문안»(`rev-p/REPORT.md`) · 재확인 첫째(`rev-p/RECHECK-1.md`) · 재확인 둘째(`rev-p/RECHECK-2.md`) · 검토 T 재확인 둘(`rev-t/RECHECK-1.md` · `RECHECK-2.md`) · 일꾼 B v4(`design-b-v4.md` §5) · 처분 `op-rev-DISPOSITION.md`. **이 파일이 구현 G 단위의 문안 정본**(계획 검토 P 가 셋째로 좁게 확인).

날짜 `<구현일>` = 구현 때 `date` 로 잰 날(2026-11-21 이후 · 기존 `@2026-11-20` IRI 와 안 겹치게).

## 1. R-3791 새 규범(Obligation) — `ontology/rules/command-dddjango.ttl` s012/b13 (wiring 은 `ontology/wiring/command-dddjango.ttl`) · R-3635 와 retain 재조직 정의 뒤 · `**개명 행**` 앞 · statesNorm b13 · wiring `delegatedTo a/command-dddjango ; enforcedBy c/behavior_guard.py` · ISSUED `R-3791<TAB><구현일><TAB>rules/command-dddjango.ttl`

> **같은 뜻 고쳐 쓰기**(<날짜>): 확정 기대 원소(위 «바뀌는 기대» 의 원소)의 기대 쪽 식을 ① 값을 이름 상수로 ② 식을 이름 상수로 ③ 기대값을 그 시험 함수의 지역 이름으로 옮기거나, ④ 비교 assert(`is` · `is not` 빼고) · mock 단언 · unittest 같음 메서드 인자에서 표시만 거쳐 닿는 집합 · 사전 표시의 차례와 키워드 인자 차례(`**` 없을 때)를 바꾸거나, ①~③ 이 들인 상수 · 지역 이름을 바꾼 편집(개명 행이 아니다)은 확정 기대 변화(D 확정)가 아니다. 그 이름은 같은 파일의 모듈 최상위 문장이나 그 시험 함수 몸 바로 아래 문장(그 원소보다 앞)에서 `이름 = 값` 하나로만 정하고, 다시 대입 · 덧셈 대입 · `del` · `global` · `nonlocal` · 매개변수 · 형식 매개변수 · 루프 · `with` 대상으로 다시 정하지 않으며, 같은 파일에 그 이름이거나 `.이름` 으로 끝나는 문자열 글자(`setattr` · `patch` · `setenv` 글자 · 사전 키 등) · 별표 import · 속성 대입 · 지움(`x.이름 = …` · `del x.이름`) · 키워드 인자 이름(`이름=…`)이 없고, 목록 · 집합 · 사전 값이면 비교 assert · mock 단언 · unittest 같음 메서드 인자 밖에서 쓰지 않는다(클래스 몸 안 메서드의 `parametrize` 안 이름은 펼치지 않는다). 이름을 정의 식으로 되돌리면 옛 식과 같은 식이어야 하고(괄호 · 줄바꿈 · 주석만 다를 수 있다 — `15` → `3 * 5` 처럼 값만 같은 식은 D 확정), 정의 식은 숫자 · 문자열 · 참거짓 · `None` 과 그 묶음 · 연산으로만 끝까지 풀려야 한다(이름 · 속성(열거형 멤버 포함) · 호출 · 첨자 · f-문자열이 남으면 D 확정). 다른 파일에서 import 한 상수 · 도움 함수로 만든 기대값 · `assertEqual` ↔ `assert ==` · 비교 좌우 바꾸기 · 목록 · 튜플 차례는 D 확정이다. 가르는 것은 `behavior_guard.py close` 다. 같은 뜻 고쳐 쓰기도 감사 키(요구 판정 `기대 의미 그대로`)로 처분된다 — 0T 는 `update` 행 없이 받고, 0F 는 `retain` 재조직 행 파일만, 0C 는 red 다(0C 는 대응표 치환만). V 의 «바뀌는 기대» 에 적은 원소는 0T · 0F close 가 같은 뜻 고쳐 쓰기로 보지 않는다(D 확정) — 그 원소의 이름 상수 · 지역 이름은 그 V 의 변경 슬라이스에서 새 기대와 함께 쓴다.

## 2. R-3633 revision 4(amendment · `wasRevisionOf @2026-11-13`) — b13 의 ««바뀌는 기대»는 … 지금 절차 그대로다.» 를 바꿈 · wiring `enforcedBy c/refactor_audit.py , c/behavior_guard.py`

> «바뀌는 기대»는 그 케이스에서 바뀔 옛 원소의 원문을 기준 판(열린 창 중 G1′ 이면 그 창 기준선 · 그 밖은 지금 시험)에서 그대로 옮긴다 — 원소와 옮길 원문은 비교 · bare assert 는 그 assert 문, mock 단언 · unittest · Django 단언(`self.` · `cls.` · `pytest_django.asserts`)과 문장 자리 `pytest.raises/warns(E, f, …)` 는 그 부르는 식(대입 꼴은 그 줄도), `with pytest.raises/warns(…)` · 단언 컨텍스트 꼴 · `except` 는 그 머리(`:` 까지), `parametrize` 는 그 데코레이터 식이다. 변경 창 close 는 바뀐 원소의 옛 원문이 여기 정확히 있을 때만 승인 변경으로 센다. 원소가 바뀌었는지는 그 기대 쪽으로 본다 — 비교는 이어진 비교면 모든 쪽, `in` · `not in` 은 글자 값 쪽(두 쪽 다 글자 값이거나 다 아니면 두 쪽), 그 밖은 왼쪽만 글자 값이면 왼쪽(`assert 200 == r`) 아니면 오른쪽이고, 맞대는 두 값을 받는 unittest 단언(`assertEqual` · `assertGreater` 류)의 첫 두 위치 인자도 같다(`assertEqual(200, r.status_code)` 는 첫 인자). 글자 값은 숫자 · 문자열 · 참거짓 · `None` 과 그 묶음 · 연산이다 — 같은 파일 모듈 최상위에서 한 번만 묶고 다시 묶지 않는(`global` · 속성 대입 · 지움 없는) 상수와 한 번 묶인 시험 안 지역 이름은 펼쳐 보고, 값을 바꾸는 쓰임이 있는 목록 · 집합 · 사전 이름은 글자 값이 아니며, 같은 파일에서 그 이름이거나 `.이름` 으로 끝나는 문자열 글자(`setattr` · `patch` · `setenv` 글자 · 사전 키 등) · 키워드 인자 이름 · 별표 import 가 가리킬 수 있는 상수(흔들리는 상수)가 끼면, 오른쪽(둘째 인자)이 글자 값이 아닌데 왼쪽(첫 인자)이 흔들리는 상수 덕에만 글자 값이거나, 두 쪽이 다 글자 값인데 오른쪽(둘째 인자)이 흔들리는 상수 덕에만 글자 값일 때 두 쪽(두 인자)이 다 기대다. raises 부르는 꼴은 E, mock 단언은 키워드 이름까지 모든 인자, unittest · Django 단언은 메서드 이름, 그리고 주어 · 메시지 · 부를 것과 그 인자를 뺀 인자다(`assertIn` · `assertNotIn` 은 두 인자 · 키워드로 준 인자는 모두 기대이고 위치 인자 하나에 `second=` 를 준 꼴은 첫 인자도 기대 · 같은 뜻 별칭은 같은 이름 · 표 밖 `self.assert…` 도움 단언은 모든 인자) — 주어만 바꾼 편집은 원소를 바꾸지 않는다. 닫힌 변경 창에서 집행이 결속된 원소(케이스 · 옛 원문)는 지금 원문으로 다시 쓰지 않는다 — 그 원소는 그 창의 기준선에서 확인된다(`changes` 가 창 기록으로 고른다). 같은 옛 원문을 슬라이스가 다른 V 여럿이 적었으면 결속은 가장 앞 슬라이스 V 몫뿐이다 — 뒤 슬라이스 V 의 그 인용은 아직 집행하지 않은 원소라 G1′ 에서 지금 기준 판(열린 창이 있으면 그 창 기준선, 없으면 지금 시험) 원문으로 고친다. 아직 집행하지 않은 원소의 수정 · 승인 안 된 V 의 삭제 · 창 rebind 는 지금 절차 그대로다.

## 3. R-3649 revision 3(amendment · `wasRevisionOf @2026-11-20`) — `agents/coder.md:80` «(그 밖 확정 기대 변화는 red 다)» 뒤

> 기대 쪽 식의 값 · 식을 같은 파일에서 한 번만 정한 이름(모듈 최상위 상수 · 그 시험 함수 몸 앞쪽 지역 이름 — 정의 식은 숫자 · 문자열 · 참거짓 · `None` 과 그 묶음 · 연산뿐이고 되돌리면 옛 식과 같은 식)으로 옮기기, 비교 assert · mock 단언 · unittest 같음 메서드 인자에서 표시만 거쳐 닿는 집합 · 사전 표시의 차례와 키워드 인자 차례 바꾸기, 그 이름 바꾸기는 기대 변경이 아니어서 `update` 행 없이 한다(꼴은 close 가 가른다 — import 한 상수 · 열거형 멤버 · 도움 함수 기대값은 기대 변경이다 · 0C 에서는 하지 않는다 · 명세 V 의 «바뀌는 기대» 원소는 0T · 0F 에서 고쳐 쓰지 않는다). 기대는 비교의 글자 값 쪽이다(글자 값 쪽이 없으면 오른쪽) — `assert 200 == r` · `assert 'x' in body` · `self.assertEqual(200, r.status_code)` 는 첫 쪽이고, 주어(응답 · 결과 이름과 그것을 꺼내는 식)만 바꾼 편집은 기대 변경이 아니다(비교 · `assertEqual` 류에 흔들리는 상수 — 같은 파일 문자열 글자 · 키워드 인자 이름 · 별표 import 가 가리킬 수 있는 상수 — 가 끼어 기대 쪽이 갈리거나 `assertIn` · 키워드 꼴이면 모든 쪽이 기대) · 글자 값 쪽이 없는 `x in y`(`item.id in resp.ids` 도) 와 이어진 비교는 모든 쪽이 기대 · `pytest.raises(E, f, …)` 는 E 가 기대 · 기대에는 mock 단언 키워드 이름과 `self.assert…` 같은 unittest · Django 단언의 기대 인자도 들고, 표 밖 `self.assert…` 도움 단언은 모든 인자가 기대다.

같은 단락 0F 절 «기대 원소를 바꾸면 red 다» → «기대 원소를 바꾸면(위 같은 뜻 고쳐 쓰기 밖) red 다».

## 4. R-3644 revision 3(amendment · `wasRevisionOf @2026-11-13`) — `agents/design-architect.md:29` «0T 에서 기대를 고치는 ⓐ 시험 항목은 … 적는다.» 뒤

> 파견 입력 «바뀌는 것 목록» 문단의 «같은 뜻 고쳐 쓰기» 는 기대를 고치는 것이 아니다 — 0T 의 ⓐ 시험 항목이면 `update` 행 없이 0T 에 두고, ⓐ 밖이면 0F `retain` 재조직 행(`재조직 — <무엇을 어디로>`)으로 적는다(V 로 올리지 않는다). V 의 «바뀌는 기대» 에 적은 원소는 0T · 0F 의 고쳐 쓰기 대상에 넣지 않는다 — 그 원소의 이름 상수는 그 V 의 «전 → 후» 에 적어 변경 슬라이스에서 쓴다.

## 5. R-3647 revision 2(amendment · `wasRevisionOf @2026-10-04`) — `agents/discipline-reviewer.md:67` ⓔ 목록에

> 들인 상수 · 지역 이름을 다른 파일(conftest · patch)이 고쳐 쓰는가

## 6. 이름표(prefLabel) — 개정 다섯 모두(DEVELOPMENT §3 체크리스트 1 · 검토 P 셋째 안 · IP 가 확인)

- R-3791: «같은 뜻 고쳐 쓰기 — 확정 기대 원소 기대 쪽의 값·식 → 같은 파일 한 번만 정한 이름 상수·시험 안 지역 이름(되돌리면 같은 식 · 글자 값 식 · 다시 정함·global·nonlocal·이름 문자열 글자·별표 import·속성 대입/지움·키워드 이름 없음 · 바뀔 수 있는 값은 단언 인자 밖 쓰임 없음) · 비교·mock·unittest 같음 인자에서 표시만 거친 집합·사전·키워드 차례 · 그 이름 바꾸기 = D 확정 아님(감사 키 기대 의미 그대로 · 0T update 행 없이 · 0F 허용 파일만 · 0C red) · import 상수·열거형·도움 함수·assertEqual↔assert·좌우·목록 차례 = D 확정 · V 바뀌는 기대 원소는 0T·0F 에서 D 확정»
- R-3633: 지금 이름표의 «바뀌는 기대(기준 판 옛 원소 원문 · 기대 추가 k)» → «바뀌는 기대(기준 판 = 열린 창 G1′ 이면 창 기준선 · 그 밖 지금 시험 · 원문 = assert 문·단언 부르는 식·with/except 머리·parametrize 식 · 기대 추가 k · 바뀜 = 기대 쪽 — 비교 글자 값 쪽·in 두 쪽·흔들리는 상수·unittest 첫 두 자리·raises 부르는 꼴 E·mock 키워드 이름·unittest 메서드 이름 · 주어 편집 아님)» · 닫힌 창 구 뒤에 «· 슬라이스가 갈리면 앞 슬라이스 V 만 결속 · 뒤 슬라이스 인용은 G1′ 에서 지금 기준 판 원문으로».
- R-3649: 끝에 «· 같은 뜻 고쳐 쓰기·주어만 바꿈은 기대 변경 아님(update 행 없이 · 0C 안 함 · V 바뀌는 기대 원소는 안 고침) · 기대 = 비교 글자 값 쪽·mock 키워드 이름·unittest 기대 인자·도움 단언 모든 인자».
- R-3644: 끝에 «· 같은 뜻 고쳐 쓰기 = 0T ⓐ 면 update 행 없이 0T · ⓐ 밖은 0F retain 재조직 · V 바뀌는 기대 원소는 0T·0F 고쳐 쓰기 밖(이름 상수는 V 전 → 후)».
- R-3647: «… D 사유·v4 목록·<file> 키)» 의 v4 목록 뒤에 «(들인 상수·지역 이름을 다른 파일이 고쳐 쓰는가 포함)».

## 7. 그 밖

- LEDGER 네 행: command-dddjango s012 · agent-coder s006 · agent-design-architect s002 · agent-discipline-reviewer s005.
- target-counts: NormShape · WorkShape 3799 → 3800 · ExpressionShape 4504 → 4509 · BlockShape · SectionShape 그대로.
- Codex: Coordinator b13 = `codex-dddjango/skills/dddjango/SKILL.md:335` **글자 그대로**(`runtime_parity_check`) · coder `dddjango-coder/SKILL.md:70` · architect `dddjango-design-architect/SKILL.md:26` · reviewer SKILL ⓔ 는 같은 뜻.
- README `:321` 한 구: «값 · 식을 같은 파일 이름 상수 · 시험 안 변수로 옮기거나 집합 · 사전 · 키워드 차례만 바꾼 시험 고쳐 쓰기는 기대 그대로 · mock 단언 키워드 이름과 unittest · Django 단언도 기대로 보고, `assert 200 == r` · `assert 'x' in body` 처럼 왼쪽에 쓴 기대 · 이어진 비교 · `pytest.raises(E, f)` 부르는 꼴 · unittest 에서 기대를 먼저 쓴 단언(`assertEqual(200, r.status_code)`)도 기대로 본다».
- `work_flow.spec.json` 기준 판 2.44.0 줄 · `master.html` 기준 판 · 요청 가이드 «바뀔 것 없음».
