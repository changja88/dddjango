# F4-200 설계 절 v2 — D 원소 정규화 + D 원소 넓힘(mock 키워드 · unittest 단언)

일꾼 B 본문을 운영자가 옮겨 적음(작성 2026-11-21 12:40 · 바탕 2.43.0 `3293b498`). v1 = `design-b-v1.md`. 수리판 v2 `repro-b/v2/scripts/behavior_guard.py`(`v2/apply_v2.py` 를 검토 T `fix3` 사본 `v2/fix3-behavior_guard.py` 위에) · diff 배포판 대비 `v2/v2-over-base.diff`(+405 −9) · fix3 대비 `v2/v2-over-fix3.diff`(+162 −13) · 장난감 · 출력 `v2/rt/` · 변이 `v2/mut_v2.py` · 러너 로그 `repro-b/fx-v2.log`.

요약(일꾼): 배포판 behavior_guard 러너 `--scripts v2` PASS · ✓ 줄 325 배포판과 글자까지 같음 · 차등 퍼즈 11,510 v2 = fix3 숫자 그대로 · «배포판 밖 D 확정» 0 · unittest 꼴 퍼즈 4,333 «값 다른데 D 확정 0» 0 · 새 ① · ② 사례 46 기대 어긋남 0 · 변이 15 모두 잡힘. 운영자 다시 돎: `op-probe/mock_kw_probe_v2.py` ①② 여섯 모두 확정 변화 · `d_probe` v2 = v1 수리판 글자 같음 · `t_ut.py` 46 어긋남 0 · `t_falsegreen.py` 수리판 «변화 없음» 0.

## 0. 범위

- 넣음 (가) 정규화: ① 값 → 이름 상수 ② 식 → 이름 상수 ③ 기대값 → 시험 안 지역 이름 ④ 순서 없는 묶음(집합 · 사전 표시)의 차례 + ①~③ 이 들인 이름 바꾸기 · 검토 반영 T1 지킴 셋(별표 import · 같은 파일 속성 대입/지움 · 키워드 인자 이름 + 클래스 메서드 parametrize) · T2 짝짓기(fix2) · T4 V 원소 고정 · G4 형식 매개변수.
- 넣음 (나) 사용자 결정 «나.»(11-21) — 지금 판 거짓 녹색 둘: ① mock 단언 키워드 이름을 열쇠에 ② unittest · Django 단언 메서드를 D 원소로.
- 안 넣음: 코드를 읽어야 아는 꼴(도움 함수 기대값 · `assertEqual` ↔ `assert ==` · 비교 좌우)을 리뷰어 판단으로 받는 길 · 덧감사 · 동결 규칙 · `_origins` fail-closed 그대로 · import 상수 · 열거형 멤버 상수(§1.6) · 길 C(§9) · assert 문의 기존 구멍 셋(§9 범위 밖 관찰).

## 1. 정규화 규칙

### 1.1 어디에

D 원소의 기대 쪽 식 — 비교 assert 의 비교 식 · bare assert 식 · `pytest.raises/warns` 식 · `except` 타입 · mock 단언 인자(키워드 값 포함) · `parametrize` 데코레이터 · unittest · Django 단언의 기대 인자(§2.2). 감싼 제어 흐름 머리 · 비교 왼쪽(주어)은 안 건드림.

### 1.2 펼치는 이름

- 모듈 이름(모두): 모듈 공간 묶기 1 · `tree.body` 바로 아래 `N = 값` / `N: T = 값` · 어느 함수에도 `global N` 없음 · 파일 안 문자열 상수가 `N` 이거나 `.N` 으로 끝나지 않음 · (T1) 별표 import 0(G1) · 파일 안 `Attribute(attr=N)` 대입 · 지움 0(G3b `request.module.N = …` · G3d `sys.modules[__name__].N = …`) · 키워드 인자 이름 `N=` 0(G3a `patch.multiple(__name__, N=…)` · G3c `globals().update(N=…)`) · (G4) 파일 안 형식 매개변수(`def f[N]()` · `class C[N]:`)에 그 이름 없음.
- 정의 자리: 시험 함수 몸에서 쓰는 모듈 상수는 정의 앞 · 뒤 상관없음(모듈을 다 읽은 뒤 시험) · 데코레이터 안 이름은 정의가 앞이어야 수집(뒤면 수집 NameError — 조용한 거짓 녹색 아님) · 클래스 몸 안 메서드의 parametrize 데코레이터는 안 펼침(클래스 이름 공간에서 풀림 — G2).
- 지역 이름(모두): 시험 함수 공간 묶기 1(매개변수 · 형식 매개변수도 묶기로) · 함수 몸 바로 아래 문장 · 원소가 든 문장보다 앞 · `global` · `nonlocal` 없음.
- 안 펼침: 매개변수 · fixture · import · 내장 이름 · 안쪽 함수 · 람다 · 클래스 몸 안 원소 · 내포 식 안 이름.

### 1.3 값 조건(검토 P 문안)

이름을 정의 식으로 되돌리면 옛 식과 같은 식(괄호 · 줄바꿈 · 주석만 다를 수 있음 — 값만 같은 식은 바뀜: `15` → `FIFTEEN = 3 * 5` · `5` → `5.0`) · 정의 식은 글자 값(숫자 · 문자열 · 참거짓 · `None`)과 그 묶음 · 연산으로만 끝까지 풀림(못 펼치는 이름 · 속성(열거형 멤버 포함) · 호출 · 첨자 · f-문자열이 남으면 안 펼침) · 깊이 16 · 순환 안 펼침 · 펼친 값 노드 1,000 까지.

### 1.4 고쳐 쓰기 판정

묶기 수 1 하나로 다시 대입 · 덧셈 대입 · del · 루프 · with · except 대상 · `:=` · 매개변수 그림자 · 따로 `global` · `nonlocal` · 같은 파일 monkeypatch · patch 글자 · T1 지킴 셋 · 바뀔 수 있는 값(목록 · 집합 · 사전 표시를 품은 값)은 이름의 다른 쓰임이 모두 «값을 바꿀 수 없는 자리»(비교 assert(`is` 없는) 양쪽 · mock 단언 인자 · unittest 같음 메서드 인자(§2.2)에서 표시만 거쳐 닿는 자리)일 때만 → `run(expected)` · `expected.add` · `for x in expected` · `len(expected)` 는 안 펼침.

### 1.5 ④ 차례

순서 없는 자리 = 비교(`is` · `is not` 빼고) · mock 단언 인자 · unittest 같음 메서드 기대 인자의 뿌리에서 표시만 거친 자리 · 집합 표시: 원소가 리터럴이거나 이름이면 정렬 · 사전 표시: `**` 없고 키가 리터럴이며 값으로 안 겹치고(`1` · `True` · `1.0` 겹치면 안 함) 값이 리터럴이거나 이름이면 정렬 · **새로 — mock · unittest 키워드 차례**: 이름으로 정렬(`**` 있으면 그대로 · mock 은 부른 키워드를 이름 → 값 사전으로 견줌 · unittest 키워드는 이름 붙은 인자).

### 1.6 다른 파일에서 import 한 상수 · 열거형 멤버 — 이번 판 밖

처분 단위가 파일 하나 · 상수 모듈이 함께 바뀌면 두 파일에 걸치고 다른 파일 고쳐 쓰기도 안 보임 → 공용 시험 모듈(`test/constants.py` · conftest)로 옮기는 정리 · 열거형 멤버 기대값 상수화는 기대 변화로 남음(0T update 행 + ⓐ).

### 1.7 V 원소 고정(T4)

0T · 0F close 에서 확정판 V «바뀌는 기대» 에 그 케이스의 옛 원소 원문이 있으면 그 원소는 정규화로 지우지 않음(글자 열쇠 분류 그대로). 출처: 0T = close 가 읽는 G1 확정판 스냅숏 `allow_table(snap)["approved_cases"]` 를 `forward_key` 로 앞 창 개명 · 이동에 맞춘 것 · 0F = open · rebind 때 동결한 허용 표의 `approved_cases`. 변경 창에는 안 씀 — C2(V 승인 케이스의 같은 뜻 고쳐 쓰기 = 승인 변경 미검출) 그대로.

## 2. D 원소 넓힘(사용자 결정 «나.»)

### 2.1 ① mock 단언 키워드 이름

글자 열쇠 `mock:<메서드>|<위치 인자 덤프…>||<이름=값 덤프…>`(지금 판은 위치 · 키워드 값만 차례대로 → 이름 빠짐). v2 에서 확정 변화: `(x=1)` → `(y=1)` · `(a=1, b=2)` → `(b=1, a=2)` · `(1)` → `(x=1)`. 키워드 차례만 바꾼 것은 같은 뜻 — 정규화 열쇠에서 이름으로 정렬(지금 판은 값 차례가 바뀌어 확정 변화 = 거짓 red → v2 변화 없음) · `**` 섞이면 차례 그대로(평가 차례 · 겹침 TypeError) · `assert_has_calls([call(x=1)])` 안쪽 `call` 키워드 이름은 지금도 덤프에 있음(그대로).

### 2.2 ② unittest · Django 단언 메서드

- 받는 자: `self.` · `cls.`(이름 그대로) · `pytest_django.asserts` 함수 꼴(`from pytest_django.asserts import X [as Y]` · `import pytest_django.asserts as M; M.X` · `from pytest_django import asserts [as M]; M.X` · `import pytest_django.asserts; pytest_django.asserts.X` — 뒤 둘은 구현 검토 IT 중요 2) · 그 밖(`helper.assertEqual` · `tc = self; tc.…` · `super().…` · `TestCase.assertEqual(self, …)`)은 한계.
- 자리 역할: s = 주어(열쇠 밖 — 비교 assert 왼쪽과 같은 몫) · e = 기대(열쇠) · m = 메시지(밖) · c = 부를 것과 그 인자(밖 · 부르는 꼴에서 그 자리부터 뒤 모두) · 표 끝 뒤 위치 인자는 e · 키워드: `msg` · `msg_prefix` 는 m · c 를 가진 메서드의 표 밖 키워드는 부르는 꼴에서 c · 그 밖 키워드는 e(`places` · `delta` · `count` · `status_code` · `html` · `ordered` · `using` …).

| 메서드 | 위치 역할 |
|---|---|
| assertEqual · NotEqual · CountEqual · ListEqual · TupleEqual · SetEqual · DictEqual · MultiLineEqual · Greater(Equal) · Less(Equal) · Is · IsNot · IsInstance · NotIsInstance · Regex · NotRegex · Django URLEqual · HTMLEqual/NotEqual · XMLEqual/NotEqual · JSONEqual/NotEqual | s e m |
| assertSequenceEqual | s e m e(seq_type) |
| assertAlmostEqual · NotAlmostEqual | s e e(places) m e(delta) |
| assertTrue · assertFalse | e m(식 전체 — bare assert 와 같음) |
| assertIsNone · IsNotNone | s m(기대 = 메서드 이름) |
| assertIn · NotIn | e e m(멤버 · 그릇 둘 다 — 어느 쪽이 주어인지 쓰임마다 달라 둘 다 열쇠) |
| assertDictContainsSubset | e s m |
| assertRaises · assertWarns | e c… |
| assertRaisesRegex · WarnsRegex · Django RaisesMessage · WarnsMessage | e e c… |
| assertLogs · NoLogs | e e |
| Django assertNumQueries | e c…(키워드 `using` = e) |
| Django assertContains · Redirects | s e e e m e |
| Django assertNotContains | s e e m e |
| Django assertTemplateUsed / NotUsed | s e m e / s e m |
| Django assertFormError | s e e e(옛 서명 `response, form, field, errors` 에서도 오류 목록이 빠지지 않게) |
| Django assertFormSetError | s e e e e |
| Django assertInHTML / NotInHTML | e s e m / e s m(바늘 = 기대 · 더미 = 주어) |
| Django assertQuerySetEqual | s e e e m |
| Django assertFieldOutput | e e e e e e |
| Django assertMessages | s e e |

같은 뜻 별칭은 한 이름: assertEquals → assertEqual · Regexp* · ItemsEqual → CountEqual · QuerysetEqual · FormsetError.

- 꼴과 열쇠: 컨텍스트 꼴(`with self.assertRaises(…)` · `assertNumQueries` · `assertTemplateUsed` · `assertLogs` …)은 원소 = with 문(pytest.raises 와 같음 · 한 머리에 단언 컨텍스트가 여럿이면 모두의 열쇠를 `&` 로 이음 — 구현 검토 IT 차단 1 · 승인 대조 옛 원문 = `with …:` 머리 · s 를 e 로 — 주어는 몸) · 부르는 꼴은 원소 = 부르는 식(옛 원문 = 그 식) · 열쇠 `ut:<메서드>[@with]|<자리=식…>` · 메서드 이름이 바뀌면(assertEqual → assertNotEqual) 확정 변화 · 별칭끼리는 같음 · 정규화: 기대 인자에 ①~④ · 같음 메서드(Equal 류 · CountEqual · In/NotIn · JSONEqual/NotEqual · DictContainsSubset)는 ④ 를 쓰고 §1.4 안전 자리(③ `expected = {…}; self.assertEqual(r, expected)` 펼쳐짐).
- 표 밖 `self.assert<대문자 · 밑줄>…` · `cls.assert…`(사용자 정의 도움 단언 · `self.assert_ok(r)` 같은 snake 꼴도 — 구현 검토 IT 사소 3): 보수적으로 받음 — 열쇠 = 메서드 이름 + 모든 위치 · 키워드 인자(메시지 포함 · `utx:`) · 까닭: 도움 단언의 뜻은 코드를 읽어야 앎(멈추는 쪽) · 대가: 도움 단언 부르는 자리의 주어만 바꿔도 D 확정(0T update 행 · 0F red).
- 다른 자리와의 관계: 0C 는 정규형 비교(`_compare_py`)가 먼저라 red 그대로(사유 글만 D 쪽으로 바뀔 수 있음) · 기능 모드 영향 없음 — `d_changes` 를 부르는 곳은 `dispose_test_file`(2.43.0 :3473 · :3494) → `judge_test_side`(:3596) → `_close_refactor`(:4147) 뿐 · 기능 모드 close 는 `:1232` 분기 밖 다른 길.
- 진행 중 실행(grep 읽기만 · `.venv` · `.git` 뺌 · 현장 저장소 일곱): `self.` · `cls.assert<대문자>` 0 · `pytest_django.asserts` · `TestCase` 0 → ② 영향 0 · mock 단언(①)은 한 저장소만 175곳(28파일) · 그중 키워드 든 줄 12 · 나머지 여섯 0 → 그 저장소 레인에서 mock 단언 키워드 이름을 바꾸는 편집은 새로 멈춤(지금 판은 거짓 녹색 · 0F red · 0T update 행 필요 · 0C red 그대로).

## 3. 지금 D 장치와 맞물림(짝짓기 = 검토 T fix2)

- LCS 는 글자 열쇠(지금 판 그대로) · equal 짝 지금 규칙(fixed → 확정 변화(지역 정의) · shared → 공유 정의 변화) · replace 짝 가운데 `nkey` 가 같고 V 고정(§1.7)이 아닌 짝만 정의 칸(`nfixed` · `nshared`)으로 — 둘 다 같으면 변화 없음 · 그 밖 replace · insert · delete 지금 그대로.
- 결과(v1 «상태 바뀜 없음» 문장 고침): 정규화 몫은 지금 판의 확정 변화를 지우기만 함 — 새 변화 · 상태 바뀜 없음(장난감 L1 ~ L4 · V1 ~ V4 배포판과 같음 · 퍼즈 «배포판 밖 D 확정» 0) · 대가: 같은 기대가 둘 이상인 함수에서 짝이 어긋나 풀릴 것이 안 풀림(퍼즈 «풀린 것» 1,013 · v1 1,032 보다 약 2% 적음 · 지금 판과 같은 red) · 넓힘 몫(①②)은 일부러 엄해짐(지금 판 «변화 없음» 이던 mock 키워드 이름 · unittest 단언 변화가 확정 변화) · mock 키워드 차례만은 지금 판 거짓 red 가 «같음» 으로.

## 4. 닿는 다른 자리

- `approved_change` · V «바뀌는 기대»: 옛 원소 원문(`element_texts`)과 대조 — unittest 부르는 꼴 `self.assertEqual(r, 1)` · 컨텍스트 꼴 `with self.assertRaises(ValueError):`(장난감 확인) · C1 · C3 · C4 배포판과 같음 · C2: V 승인 케이스의 편집이 같은 뜻 고쳐 쓰기뿐이면 «승인 변경 미검출» — 2.44.0 으로 close · 재close 한 창에만(verify 는 저장된 close 기록) · 0C 는 red 그대로 · 사유 글만.
- T4 와 새 순서: 0T · 0F 에서 V 인용 원소를 ① 로 고쳐 쓰면 red(`rt/t_pin.py`: 0T «D 확정 … 밖 … 기대식» · 0F «D 확정(D 기대식 1)» · 같은 파일 V 밖 원소는 개별 감사) → «앞 창 고쳐 쓰기 → 뒤 변경 창 막힘»(T4 · C3 앞 단계)은 앞 창에서 멈춤 · C3(앞 창에서 상수를 들인 뒤 V 가 상수 값만 바꿈)는 지금 판과 같은 한계.
- 그 밖: `zero_t_fixed` · update 행 — D 확정 목록이 줄거나(정규화) 늚(①②) · 판형 그대로 · 감사 요청 글 키 · 요구 판정 · D 사유 갈래 그대로 · 열쇠 종류 `ut` · `utx` 를 `_EXPR_PART` 에(맥락만 · 기대식 가름) · refactor_audit 은 D 함수 안 씀(«바뀌는 기대 원문 실재» 는 글자 대조라 unittest 원문 인용도 그대로) · pre-gate 판정 그대로 · 실행 트리 digest 바뀜 → 도는 실행은 다음 G1′ · G2 전 재예보(검토 P 중요 6) · dddjango-web D 장치 없음.

## 5. 규칙 글(검토 P 문안 기준 + ② 몫)

- **Coordinator `command-dddjango` s012/b13 — 새 규범 R-3791**(Obligation · R-3635 · retain 재조직 정의 뒤 · `**개명 행**` 앞 · statesNorm b13 · wiring `delegatedTo a/command-dddjango ; enforcedBy c/behavior_guard.py`): 검토 P «다듬은 문안» 에 넷 — ④ 자리에 «mock 단언 · unittest 같음 메서드 인자 안 집합 · 사전 표시의 차례와 키워드 인자 차례(`**` 없을 때)» · 고쳐 쓰기 조건에 «별표 import · 같은 파일의 그 이름 속성 대입(`x.이름 = …`) · 키워드 인자 이름(`이름=…`) · 형식 매개변수» · 데코레이터 조건에 «클래스 몸 안 메서드의 parametrize 안 이름은 펼치지 않는다» · 끝에 «V 의 «바뀌는 기대» 에 적은 원소는 0T · 0F close 가 같은 뜻 고쳐 쓰기로 보지 않는다».
- **R-3633 revision 4**(amendment · `wasRevisionOf @2026-11-13`): b13 «바뀌는 기대» 문장의 확정 기대 원소 목록 → «확정 기대 원소 — 비교 assert · `pytest.raises/warns` 인자 · `except` 타입 · `parametrize` 인자 · mock 단언 인자(키워드 이름 포함) · unittest · Django 단언 메서드(`self.` · `cls.` · `pytest_django.asserts`)의 기대 인자(주어 · 메시지 인자 빼고 · 컨텍스트 꼴은 `with …:` 머리) — 의 원문».
- **coder R-3649 revision 3**(clarification · `wasRevisionOf @2026-11-20`): 검토 P 문안 + «기대에는 mock 단언 키워드 이름 · `self.assert…` 같은 unittest · Django 단언의 기대 인자도 든다».
- **architect R-3644 revision 3**(amendment · `wasRevisionOf @2026-11-13`): 검토 P 문안 그대로(0T ⓐ 시험 항목은 update 행 없이 0T · ⓐ 밖은 0F retain 재조직).
- **리뷰어 R-3647 revision 2**(clarification · `@2026-10-04` 다음): ⓔ 에 «들인 상수 · 지역 이름을 다른 파일(conftest · patch)이 고쳐 쓰는가»(검토 P 사소 6) · R-3646 · R-3686 무변.
- LEDGER 네 행: command-dddjango s012 · agent-coder s006 · agent-design-architect s002 · agent-discipline-reviewer s005.
- 그래프 수: ISSUED `R-3791<TAB><구현일><TAB>rules/command-dddjango.ttl` · target-counts NormShape 3799 → 3800 · WorkShape 3799 → 3800 · ExpressionShape 4504 → 4509(새 1 + 개정 넷) · render `--apply` 넷 · `make rulepack` · q4 골든 바뀌면 `--emit`.
- 미러: Coordinator b13 = Codex `dddjango/SKILL.md:335` 글자 대조(`runtime_parity_check`) · coder `:70` · architect `:26` · reviewer SKILL ⓔ 같은 뜻 · `codex-dddjango/skills/dddjango/scripts/behavior_guard.py` byte 동일.
- 문서: README `:321` 한 구 «값 · 식을 같은 파일 이름 상수 · 시험 안 변수로 옮기거나 집합 · 사전 · 키워드 차례만 바꾼 시험 고쳐 쓰기는 기대 그대로 · mock 단언 키워드 이름과 unittest · Django 단언도 기대로 본다» · `work_flow.spec.json` 2.44.0 줄 · 요청 가이드 «바뀔 것 없음».

## 6. 장난감 수리판 v2 로 잰 것

| 사례 | 결과 |
|---|---|
| v1 사례 `fix/d_probe.py`: 같은 뜻 15 · 반례 25 · V1 ~ V4 · H11 | `v2/probe-v2.txt` = `fix/probe-fix.txt` 글자까지 같음 |
| `dispose_probe` H11 | 0T · 0F 개별 감사 · 키 3 · 여유 5 → 6 red |
| `approved_probe` C1 ~ C4 | v1 과 같음 |
| 검토 T 거짓 녹색 `rt/t_falsegreen.py` G1 · G2 · G3a ~ d · G4(7) | 모두 `확정 변화/기대식` · 0T · 0F red |
| G4 클래스 형식 매개변수 `rt/t_g4.py` | 확정 변화 |
| 짝 상태 `rt/t_lcs.py` L1 ~ L4 · 0T/0F/변경 창 | 배포판과 모두 «같음» |
| T4 `rt/t_pin.py` | V 인용 원소 0T · 0F red · V 밖 원소 개별 감사 |
| 새 ① · ② `rt/t_ut.py` | 46사례 기대 어긋남 0 |
| 운영자 탐침 `mock_kw_probe.py` · `d_probe.py` 를 v2 에 | ①② 여섯 모두 확정 변화 · 정규화 넷 «변화 없음» |
| 차등 퍼즈 `rt/t_fuzz.py` 씨앗 1 ~ 4 · 11,510 · `out-fuzz-v2.txt` | v2 = fix3 줄 단위 같음 · 배포판 밖 D 확정 0 |
| unittest 꼴 퍼즈 `rt/t_fuzz_ut.py` 씨앗 1 · 2 · 4,333 | 값 다른데 D 확정 0(공유 정의 변화 정책 밖) 0 · 같은 값인데 남은 멈춤 13 |
| 변이 `mut_v2.py` 15 | 모두 잡힘 |
| 배포판 러너 `--scripts v2/scripts` | PASS · ✓ 줄 325 배포판과 글자까지 같음 |

- t_ut 46 내역: 배포판 기준 unittest 38 · mock M1 ~ M3 «변화 없음»(지금 판 거짓 녹색) · M4(키워드 차례) · M8(키워드 값 → 상수) «확정 변화»(지금 판 거짓 red) / v2 — 주어만 · 메시지만 · 부르는 꼴의 부를 것 인자만 바꾼 것 · 별칭 · 집합/사전 차례 · ①③ «같음» · 예외 · 기대 글 · status_code · places · 템플릿 이름 · 로그 수준 · pytest_django 함수(별칭 포함) · 표 밖 도움 단언 · 목록 차례 «바뀜».
- 퍼즈 씨앗별 «값 다름 · 배포판 확정 · v2 확정 0» 5 · 8 · 6 · 3 — 모두 펼친 상수 값 바꿈이 «공유 정의 변화» 로 알려진 것(지금 판 정책).
- 변이 15: T4 고정(t_pin 3줄) · mock 키워드 이름(M1 · M2 · M3) · mock 키워드 차례(M4) · unittest 주어 빼기(U2 · U11 · U23) · 메시지 빼기(U3 · U21) · 컨텍스트 꼴 s → e(U22) · 부를 것 빼기(U14 · U18) · 표 밖 보수(U31) · 같음 메서드 안전 자리(U6) · 같음 메서드 순서 없음(U7 · U35) · G4(클래스 형식 매개변수) · T1 별표(G1) · T1 속성 · 키워드 이름(G3 넷) · T1 클래스 parametrize(G2) · T2 글자 열쇠 LCS(41줄).
- 배포판 러너: 기능 43 + 리팩토링 275 사례 · close 347회 · 399 = 215 + 184 · 자동 초록 0 · 21분 · 러너에 mock 키워드 이름 · unittest 단언 사례가 없어 ①② 가 기존 사례를 안 바꿈 — 새 사례 필요(§7).

## 7. 시험 · 변이 · 규모 · 한계

- 시험: `behavior_guard_fixture_run.py` 에 `norm_checks()` — 단위(같은 뜻 15 · 반례 25 · V1 ~ V4 · H11 2 · 검토 T 반례 일곱 · L1 ~ L4 · combo(t_combo · t_pin) · ①② 46) + 창 사례(0T H11 → 개별 감사 · 0F H11 → 개별 감사 · 0F 값 바꿈 → red · 0T · 0F V 인용 원소 ① → red · 변경 창 ①만 → 승인 변경 미검출 · 0F mock 키워드 이름 바꿈 → red · 0T unittest 기대 바꿈 · update 행 없음 → red · 변경 창 V 가 `self.assertEqual(…)` 인용 → 승인 변경 감사).
- 변이: 위 15 를 `--mutation-test` 에(v1 의 8 과 겹치는 것은 하나로).
- 규모: behavior_guard.py 배포판 대비 +405 −9(주석 · 문서 포함 — v1 정규화 +283 · 검토 반영 약 +10 · v2 몫 +162 −13: unittest 표 · 자리 역할 약 90 · mock 키워드 약 15 · T4 고정 약 25 · G4 3 · 안전 자리 5) · 러너 +약 250 · 글: 새 규범 1 · 개정 넷 · LEDGER 넷 · Codex SKILL 넷(Coordinator 글자 대조) · byte 미러 1 · 검사 `make verify` + `make verify-mutation`.
- 받아들일 한계: §1.6 import · 열거형 상수 · 안쪽 함수 · 람다 · 클래스 몸 안 원소 · 내포 식 안 이름 · 다른 파일(conftest)의 고쳐 쓰기(리뷰어 ⓔ 가 받침) · 사용자 정의 `__eq__` · 집합 `{1, True}` 정렬 · 짝 어긋남으로 덜 풀림 약 2% · unittest(`self` · `cls` · pytest_django 밖 받는 자 · `assertEqual(기대, 실제)` 거꾸로 쓴 꼴은 첫 인자가 주어로 빠짐(assert 문 좌우와 같은 몫) · assertIn 은 두 쪽 다 열쇠라 주어만 바꿔도 멈춤 · 표 밖 도움 단언은 주어만 바꿔도 멈춤 · `self.fail` 은 원소 아님 · assertTrue 안 비교식의 지역 이름은 안전 자리가 아니라 안 펼침) · mock `**` 섞인 키워드 차례는 바뀜 · C3.

## 8. 진행 중 실행(노트 «도는 실행» 몫)

정규화(가): red 가 개별 감사로 풀리고 green → red 는 C2 하나(2.44.0 close · 재close 한 창) · T4: 0T · 0F 에서 V 인용 원소를 ①~④ 로 고친 편집은 red 그대로(지금 판도 red) · ①: 진행 중 레인 하나의 mock 키워드 이름 편집이 새로 멈춤 · ②: 현장 0 · pre-gate 재예보 · 옛 창 기록 꼴 무변.

## 9. 길 C · 범위 밖 관찰

- 길 C: v1 §7 그대로 안 넣음.
- 범위 밖 관찰(지금 판 assert 문에도 있는 거짓 녹색 · 두 판 모두 «변화 없음» · 작업 리스트 후보): `assert 'x' in r` → `'y' in r`(왼쪽이 기대인 `in`) · `assert 200 == r` → `201 == r`(좌우 거꾸로) · `pytest.raises(E, f)` 부르는 꼴 예외 바꿈(원소 아님).

## 남긴 것

`repro-b/v2/`: `scripts/`(v2 수리판) · `fix3scripts/` · `fix3-behavior_guard.py` · `apply_v2.py` · `v2-over-base.diff` · `v2-over-fix3.diff` · `probe-v2.txt` · `rt/`(harness · t_* · out-*) · `mut_v2.py` · `op/` · 러너 로그 `repro-b/fx-v2.log` · `__pycache__` · 임시 변이 지움 · 프로세스 모두 끝 · 커밋 없음.
