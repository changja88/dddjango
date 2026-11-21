# F4-200 설계 v4 — v3(`design-b-v3.md`) 위에 검토 T 좁은 재확인 첫째 반영 — 바뀐 절만

일꾼 B 본문을 운영자가 옮겨 적음(작성 2026-11-21 14:34). 수리판 v4 `repro-b/v4/scripts/behavior_guard.py`(`v4/apply_v4.py` 를 v3 사본 위에) · diff v3 대비 `v4/v4-over-v3.diff`(+39 −11 · 5,484 → 5,514) · 배포판 대비 `v4/v4-over-base.diff`(+484 −13) · 장난감 `v4/rt/t_v4.py`(19 · 어긋남 0) · `v4/rt/t_d89.py`(검토 T 사본) · `v4/rt/t_fuzz_ut_rev.py`(새로) · 변이 `v4/mut_v4.py`(36 모두 잡힘) · 러너 `repro-b/fx-v4.log`.

운영자 다시 돎: `t_v4.py` 19 어긋남 0 · `t_v3.py` 38 어긋남 0(S1 · S3 기대 고침) · `t_d89.py` X1 ~ X4 · U1 확정 변화 · 0T · 0F red · 러너 ✓ 323 / 325(FAIL = v3 §7 둘).

## 2.3 «쪽 가름용 펼침» 단락 바꿈

- shape 에서 모듈 이름을 받는 조건: 모듈 최상위 단일 대입 하나로만 묶이고 다시 묶이지 않음(`_module_bound_once` — 묶기 수 1 · 어느 함수에도 `global` 없음 · 같은 파일에 그 이름 속성 대입 · 지움(`x.이름 = …` · `sys.modules[__name__].이름 = …`) 없음 — 검토 T v3b 와 같은 꼴) · 문자열 · 키워드 이름 · 별표 import · 형식 매개변수 지킴은 쪽 가름에서 안 봄.
- 불안정한 이름(새 · X6): 왼쪽이 shape 로는 글자 값인데 모든 지킴을 본 펼침(`slit`)으로는 아니면 두 쪽 열쇠(B) — 왼쪽이 불안정한 모듈 이름 덕에만 글자 값인 경우(같은 파일 `setattr(sys.modules[__name__], 'N', …)` · `monkeypatch.setattr('m.N', …)` 글자 · `N=` 키워드 · 별표 import) · `in` 도 같음(왼쪽만 글자 값 자리가 L 대신 B) · 오른쪽이 불안정한 이름이면 지금처럼 R.

## 2.5 (새) unittest 차례 비교 메서드의 첫 두 자리 쪽 가름(검토 T 중요)

대상: 맞대는 두 값을 받는 메서드 24(`_UT_ORDERED` — Equal 류 · CountEqual · Sequence/List/Tuple/Set/Dict/MultiLine · Greater/GreaterEqual/Less/LessEqual · Is/IsNot · AlmostEqual/NotAlmostEqual · URL/HTML/XML/JSON(Not)Equal · 별칭 같은 이름). 부르는 꼴 · 위치 인자 둘 이상이면 첫 자리만 글자 값이면 역할 `(e, s)` · 첫 자리가 불안정한 이름 덕에만 글자 값이면 `(e, e)` · 글자 값 가름은 §2.3 과 같음 · 열쇠는 자리 번호(`0=` · `1=`)로 지금 꼴과 갈림(`assertEqual(200, r)` ↔ `assertEqual(r, 200)` 확정 변화) · 형 · 정규식 · 응답 받는 메서드(IsInstance · Regex · Django Contains/Redirects/TemplateUsed/FormError/QuerySetEqual/Messages …)는 첫 자리가 늘 주어라 `s e` 그대로 · 키워드 꼴(`first=` · `second=`) · 컨텍스트 꼴 그대로.

## 6. 잰 것(v4)

| 사례 | 결과 |
|---|---|
| `t_v4.py` 19 | 어긋남 0 |
| 검토 T `t_d89.py` 사본(v4) | X1 ~ X4 · U1 · U2 확정 변화 · 0T · 0F red · U3 · R1 · J1 는 §7 한계 |
| `t_v3.py` 38(v4) | 기대 고친 것 2(S1 · S3 «같음» → 멈춤 · 받은 결정) · S2 그대로 «같음»(오른쪽 불안정 = R) · 36 그대로 · 어긋남 0 |
| t_ut 46 · t_falsegreen · t_lcs · t_pin · t_g4 · t_combo · `d_probe` | v3 와 출력 같음(`v4/cmp/`) |
| 지금 방향 퍼즈 `t_fuzz.py` 11,510 | v4 = v2 모든 셈 같음 |
| 좌우 섞은 퍼즈 `t_fuzz_rev.py` 11,510 | 거짓 녹색 v4 0 · 같은 값인데 D 확정 v3 32 → v4 295(«v4 만 멈춤» 263 모두 «다른 시험에 setattr 글자를 더함» S1 꼴 · «v3 만 멈춤» 0) |
| unittest 퍼즈(주어 먼저) 씨앗 1 · 2 | v4 = v3 바이트 같음 |
| 새 퍼즈 `t_fuzz_ut_rev.py`(짝수 번째 `assertEqual(<기대>, s[i])` · 씨앗 1 ~ 4 · 7,210) | 거짓 녹색 v3 760 → v4 0 · 같은 값인데 D 확정 v3 16 → v4 106(«v4 만 멈춤» 90 = setattr 글자 꼴 86 · 지역 사전 정의 글자 차례 4) |
| 변이 `mut_v4.py` 36 | 모두 잡힘 |
| 배포판 러너 `--scripts v4` | ✓ 323 / 325 · ✓ 줄 v3 와 글자 같음 · FAIL = v3 §7 둘 · 합계 216 + 183 · 자동 초록 0 |
| `one_rcase.py` 제안 a ~ d · 0F 창 여섯(v4) | 모두 기대대로 |
| 현장(같은 복사본을 v3 · v4 로) | 셈 같음 → 영향 0 |

t_v4 19: shape 지킴(X1 ~ X3 global 다시 묶는 `LAST` == · is · 부른 값 / X5 `sys.modules[__name__].LAST =` / X7 모듈에서 두 번 묶는 이름 → 확정 변화 · v3 변화 없음) · 거꾸로 global 세는 값(X4 `assert 2 == CALLS` 2 → 3 → 확정 변화 · 배포판 · v3 변화 없음) · 불안정한 이름(X6 `setattr(sys.modules[__name__], 'LAST', …)` → 두 쪽 · 확정 변화) · 주어만(X5s · X7s · A1s `calls = []` + append · A2s 다시 묶인 지역 → 같음) · unittest(U1 `assertEqual(200, r.status_code)` → 201 · U5 `assertGreater(10, …)` 확정 변화 / U4 주어만 · U8 `assertEqual(OK, r)`(OK = 200) → r2 같음 / U6 불안정한 첫 자리 → 두 자리 · 확정 변화 / U7 `assertIsInstance('x', str)` → int 확정 변화(안 바꿈) / U9 좌우 바꿈 확정 변화) · 0T · 0F 처분(X1 · X6 · U1 → red · U1 배포판은 개별 감사).

현장(읽기만 · 다시 복사해 v3 · v4 로 셈 · 셈 뒤 지움): `global` 든 시험 파일 0 · `setattr(sys.modules…)` 0 · `self.` · `cls.assert` 0 → v4 몫 영향 0 · 현장 나무가 일하는 중이라 비교 assert 25,696 → 25,699(13시 복사본 대비 · v3 §8 수는 그 시점 값).

## 7. 시험 · 변이 · 규모 · 한계(바꿈)

변이 36(v2 15 + v3 13 + v4 8): V4-1 shape 묶기 수(X7s) · V4-2 shape global(X4) · V4-3 shape 속성 대입(X5s) · V4-4 불안정한 이름 = 두 쪽 끔(X6 · S1 · S3) · V4-5 unittest 쪽 가름 끔(U1 · U4 · U5 · U8) · V4-6 불안정한 첫 자리 (e, e) → (e, s)(U6) · V4-7 대상을 모든 `s e` 메서드로 넓힘(U7) · V4-8 `_ut_parts` 역할 바꿈 끔(U1 등) · v3 의 V3-11(바뀔 수 있는 값 지킴) · V3-12(지역 묶기 수)는 B 안전망에 가려 거짓 녹색이 안 나 주어만 바꾼 사례 A1s · A2s 로 잡음(지킴이 없으면 B 가 되어 주어 편집이 멈춤).

러너 새 사례: v3 §7 목록 + `t_v4` 19 + 0F 창 X1 · X6 · U1(red) · U4(개별 감사). 규모(v3 대비 +39 −11): shape 지킴 · `_module_bound_once` 약 10 · `slit` · 불안정한 이름 두 쪽 약 12 · unittest 쪽 가름(`_UT_ORDERED` 8 · `ut_key` 5 · `_ut_parts` 3) 약 16.

한계(v3 목록 바꿈): v3 한계 6(unittest 거꾸로) 지움(넣음) · 한계 4 덧붙임 «모듈에서 다시 묶이는 이름(묶기 2 · `global` · 속성 대입/지움)은 이제 글자 값 아님» · 새 7 불안정한 이름 두 쪽(같은 파일 글자(`setattr` · `patch` 글자) · 키워드 인자 이름 · 별표 import 가 가리킬 수 있는 상수를 왼쪽(첫 인자)에 둔 비교는 두 쪽 열쇠 — 주어만 바꿔도 멈춤(S3) · 다른 시험에 그런 글자를 더하기만 해도 멈춤(S1 · 퍼즈 263 · 86) · 멈추는 쪽) · 새 8 assertFormError · FormSetError 넷째 · 다섯째 위치(Django 5 `msg_prefix`)도 기대로 셈(메시지만 바꿔도 멈춤 · U3 · 옛 서명 몫) · 새 9 지금 판과 같은 구멍(`pytest.raises(E, f).match(…)` 이어 부른 꼴 원소 아님 R1 · pytest-django 픽스처 `django_assert_num_queries` · `django_assert_max_num_queries` 받는 자 밖 J1 · 작업 리스트 후보) · 새 10 unittest 쪽 가름은 위치 인자 첫 두 자리만(키워드 꼴 · 형/정규식/응답 메서드는 `s e` 그대로) · «넣지 않은 선택지» 에서 unittest 줄 지움(대칭 연산 좌우 바꿈 줄만).

## 5. 규칙 글 — 최종 문안 목록(바꿈)

- **R-3791** — `rev-p/RECHECK-1.md` «합친 한 덩어리» 그대로(v4 몫 없음).
- **R-3633 revision 4**(amendment · `wasRevisionOf @2026-11-13` · b13 ««바뀌는 기대»는 … 지금 절차 그대로다.» 를 바꿈):

> «바뀌는 기대»는 그 케이스에서 바뀔 옛 원소의 원문을 기준 판(Phase 2 전이면 지금 시험 · 열린 창 중 G1′ 이면 창 기준선)에서 그대로 옮긴다 — 원소와 옮길 원문은 비교 · bare assert 는 그 assert 문, mock 단언 · unittest · Django 단언(`self.` · `cls.` · `pytest_django.asserts`)과 문장 자리 `pytest.raises/warns(E, f, …)` 는 그 부르는 식(대입 꼴은 그 줄도), `with pytest.raises/warns(…)` · 단언 컨텍스트 꼴 · `except` 는 그 머리(`:` 까지), `parametrize` 는 그 데코레이터 식이다. 변경 창 close 는 바뀐 원소의 옛 원문이 여기 정확히 있을 때만 승인 변경으로 센다. 원소가 바뀌었는지는 그 기대 쪽으로 본다 — 비교는 이어진 비교면 모든 쪽, `in` · `not in` 은 글자 값 쪽(두 쪽 다 글자 값이거나 다 아니면 두 쪽), 그 밖은 왼쪽만 글자 값이면 왼쪽(`assert 200 == r`) 아니면 오른쪽이고, 맞대는 두 값을 받는 unittest 단언(`assertEqual` · `assertGreater` 류)의 첫 두 위치 인자도 같다(`assertEqual(200, r.status_code)` 는 첫 인자). 글자 값은 숫자 · 문자열 · 참거짓 · `None` 과 그 묶음 · 연산이다 — 같은 파일 모듈 최상위에서 한 번만 묶고 다시 묶지 않는(`global` · 속성 대입 · 지움 없는) 상수와 한 번 묶인 시험 안 지역 이름은 펼쳐 보고, 값을 바꾸는 쓰임이 있는 목록 · 집합 · 사전 이름은 글자 값이 아니며, 같은 파일의 `setattr` · `patch` 글자 · 키워드 인자 이름 · 별표 import 가 가리킬 수 있는 상수 덕에만 왼쪽(첫 인자)이 글자 값이면 두 쪽(두 인자)이 다 기대다. raises 부르는 꼴은 E, mock 단언은 키워드 이름까지 모든 인자, unittest · Django 단언은 메서드 이름과 주어 · 메시지 · 부를 것과 그 인자를 뺀 인자(표 밖 `self.assert…` 도움 단언은 모든 인자)다 — 주어만 바꾼 편집은 원소를 바꾸지 않는다. 닫힌 변경 창에서 집행이 결속된 원소(케이스 · 옛 원문)는 지금 원문으로 다시 쓰지 않는다 — 그 원소는 그 창의 기준선에서 확인된다(`changes` 가 창 기록으로 고른다). 같은 옛 원문을 슬라이스가 다른 V 여럿이 적었으면 결속은 가장 앞 슬라이스 V 몫뿐이다 — 뒤 슬라이스 V 의 그 인용은 아직 집행하지 않은 원소라 G1′ 에서 창 기준선 원문으로 고친다. 아직 집행하지 않은 원소의 수정 · 승인 안 된 V 의 삭제 · 창 rebind 는 지금 절차 그대로다.

- **R-3633 wiring**: `delegatedTo a/command-dddjango ; enforcedBy c/refactor_audit.py , c/behavior_guard.py`.
- **coder R-3649 revision 3**(amendment · `wasRevisionOf @2026-11-20` · `coder.md:80` «(그 밖 확정 기대 변화는 red 다)» 뒤):

> 기대 쪽 식의 값 · 식을 같은 파일에서 한 번만 정한 이름(모듈 최상위 상수 · 그 시험 함수 몸 앞쪽 지역 이름 — 정의 식은 숫자 · 문자열 · 참거짓 · `None` 과 그 묶음 · 연산뿐이고 되돌리면 옛 식과 같은 식)으로 옮기기, 비교 assert · mock 단언 · unittest 같음 메서드 인자 안 집합 · 사전 표시의 차례와 키워드 인자 차례 바꾸기, 그 이름 바꾸기는 기대 변경이 아니어서 `update` 행 없이 한다(꼴은 close 가 가른다 — import 한 상수 · 열거형 멤버 · 도움 함수 기대값은 기대 변경이다 · 0C 에서는 하지 않는다 · 명세 V 의 «바뀌는 기대» 원소는 0T · 0F 에서 고쳐 쓰지 않는다). 기대는 비교의 글자 값 쪽이다(글자 값 쪽이 없으면 오른쪽) — `assert 200 == r` · `assert 'x' in body` · `self.assertEqual(200, r.status_code)` 는 첫 쪽이고, 주어(응답 · 결과 이름과 그것을 꺼내는 식)만 바꾼 편집은 기대 변경이 아니다 · 둘 다 이름인 `x in y` 와 이어진 비교는 모든 쪽이 기대 · `pytest.raises(E, f, …)` 는 E 가 기대 · 기대에는 mock 단언 키워드 이름과 `self.assert…` 같은 unittest · Django 단언의 기대 인자도 들고, 표 밖 `self.assert…` 도움 단언은 모든 인자가 기대다.

  + 같은 단락 0F 절 «기대 원소를 바꾸면 red 다» → «기대 원소를 바꾸면(위 같은 뜻 고쳐 쓰기 밖) red 다».
- **architect R-3644 revision 3**(amendment · `wasRevisionOf @2026-11-13`): `rev-p/REPORT.md` «다듬은 문안» 설계자 줄 그대로.
- **리뷰어 R-3647 revision 2**(amendment · `wasRevisionOf @2026-10-04`): ⓔ 에 «들인 상수 · 지역 이름을 다른 파일(conftest · patch)이 고쳐 쓰는가» · R-3646 · R-3686 무변.
- **README `:321`** 구절: «`assert 200 == r` · `assert 'x' in body` 처럼 왼쪽에 쓴 기대 · 이어진 비교 · `pytest.raises(E, f)` 부르는 꼴 · unittest 에서 기대를 먼저 쓴 단언(`assertEqual(200, r.status_code)`)도 기대로 본다».
- 그래프 수 · LEDGER · ISSUED v2 그대로(NormShape · WorkShape 3799 → 3800 · ExpressionShape 4504 → 4509 · LEDGER 네 행 · revisionKind 만 R-3649 · R-3647 amendment).

## 8. 진행 중 실행(덧붙임)

v4 몫 현장 영향 0(같은 복사본 셈 같음 · global · `setattr(sys.modules…)` · unittest 단언 0 파일) · 2.44.0 으로 다시 close 할 때 바뀌는 것은 v3 §8 그대로.

## 남긴 것

`repro-b/v4/`: `scripts/` · `apply_v4.py` · `v3-behavior_guard.py` · `v4-over-v3.diff` · `v4-over-base.diff` · `probe-v4.txt` · `mut_v4.py` · `one_rcase.py` · `cmp/` · `cmp-field-v3.txt` · `cmp-field-v4.txt` · `rt/`(harness fix = v4 · fix2 = v2 · v3 = v3 · 새 `t_v4.py` · `t_d89.py` · `t_fuzz_ut_rev.py` · `t_fuzz_rev_cls.py` · 고침 `t_v3.py` · `t_fuzz_rev.py` · 출력 `out-fuzz-v4.txt` · `out-fuzz-rev.txt` · `out-fuzz-ut-rev.txt`) · `repro-b/fx-v4.log` · 현장 복사본 `field-scan/` 두 번 다 지움 · 도는 프로세스 0 · 커밋 없음.
