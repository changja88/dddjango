# F4-199 설계 절 v2(+ patch-d) — 다중 owner 원소의 닫힌 창 결속(길 A · 도구를 R-3633 문면에 맞춤 · 슬라이스로 owner 좁힘)

일꾼 A 본문을 운영자가 옮겨 적음(2026-11-21 12:13 기준). 수치는 `repro-a/` 안에서 잼. 수리판 v2 `repro-a/patch-c/` · diff `patch-c.diff`(2.43.0 대비) · `patch-c-over-b.diff`(v1 대비 +12 / −1 — 검토 T patchA2 와 같은 뜻 · 다른 점은 슬라이스를 못 읽을 때 결속 안 함). v1 = `design-a-v1.md`.

요약: 사례 초안 v2(`cases_draft2.py`) 16/16(운영자 다시 돎 — `op-cases2-c.txt` 불일치 0) · 2.43.0 에서 12 붉음 · v1 에서 4(W24 · 24b · 24c · 25) 붉음 · RD-W1 ~ W15 20/20 · 관련 묶음(changes · move_key · rename_row · g1_partial) 91/91 · 변이 여섯 모두 죽음 · 현장 사본 `changes --gate` exit 0 · `닫힌 창 기준선 66(w5) · red 0 · 최종 digest(생략)`(v1 과 같음 · 현장 V 모두 S1).

| 꼴(검토 T `t_f199.py`) | 2.43.0 | v1 | v2 |
|---|---|---|---|
| A1-0 | 2 | 0 | 2 |
| A1-1 | 2 | 2 | 0 |
| A1-2 | 2 | 2 | 0 |
| A2-1 | 0 | 2 | 0 |
| A3 | 2 | 2 | 2 |

## 0. v1 → v2

- 검토 T3: 같은 원소를 적은 V 의 슬라이스가 갈리면 가장 앞 슬라이스 V 만 «그 창에서 집행됨» 으로 결속. v1 은 V1(S1) · V3(S2)(A1)에서 아직 안 한 V3 를 집행으로 묶어 G1′ 에서 V3 인용을 고치면 보존 red(A1-1 · A1-2 exit 2) · 안 고치면 S2 close «바뀐 옛 원소가 «바뀌는 기대» 밖» — 길 없음 · plus(A2-1)는 2.43.0 green → v1 red 퇴행.
- 검토 P 사소 1: 근거 규범 R-3633(`commands/dddjango.md:318` · `command-dddjango.ttl:4905`) · R-3632 는 «불가 범주 반대 방향 규칙».

## 1. 바꿀 줄 (2.43.0 `dddjango/scripts/refactor_audit.py` · Codex 미러 byte 동일)

### 1-1. 결속 고리 `_closed_windows` `:3304-3314`

```python
        hits: dict = last["approved_hits"]
        executed: "dict[tuple, object]" = {}
        slice_no: "dict[str, int | None]" = {}
        for v in snap.get("V", []):
            sm = re.fullmatch(r"S(\d+)", _slice_id(str(v.get("slice", ""))))
            slice_no[v["id"]] = int(sm.group(1)) if sm else None
        for (kind, case, verb, o), owners in _window_elements(snap).items():
            if len({vid for vid, _e in owners}) > 1:
                nums: "list[int | None]" = [slice_no.get(vid) for vid, _e in owners]
                if None in nums:
                    continue                                 # 슬라이스를 못 읽는 V 가 낌 — 가를 수 없다 · 결속하지 않는다
                owners = [ow for ow, s in zip(owners, nums) if s == min(nums)]   # 슬라이스가 갈리면 가장 앞 슬라이스 V 만
            hit: dict = hits.get(case) or {}
            if kind == "plus":
                if len({vid for vid, _e in owners}) != len(owners):
                    continue                                 # 한 V 가 같은 케이스 기대 추가를 두 줄에 — 덧값을 V 하나에 둘 수 없다
                need: int = 1 if len(owners) == 1 else sum(int(e) for _v, e in owners)   # V 여럿 = 그 창이 덧값 합을 다 채움
                done: bool = int(hit.get("add", 0)) >= need
            else:                                            # 옛 원문 · add · remove — 적은 V 가 여럿이어도 원소 하나 · 한 번 집행
                done = ((kind == "old" and o in hit.get("old", [])) or (kind == "add" and case in last["cases_added"])
                        or (kind == "remove" and case in last["cases_removed"]))
            if done:
                for vid, extra in owners:
                    executed[(vid, kind, case, verb, o)] = extra
```

지움: `:3306-3307` `if len(owners) != 1: continue  # … 모호 · 결속하지 않는다` · `vid, extra = owners[0]`. `_slice_id` 는 같은 파일 `:3589`.

- old · add · remove: 소비 조건 그대로(old = 그 창 마지막 close `approved_hits[case].old` 에 있음) · 같은 슬라이스 owner 모두 결속(허용 표 `behavior_guard.py:3709` · G2 verify `:4872-4880` 의 «원소 하나 · 한 번 집행» 과 같은 셈) · 결속은 그 창 결속 판(그 창 `g1_digest` 의 후보) owner 에만 → 뒤 G1′ 이 더한 V 는 결속 안 됨(RD-W3 · W20).
- 슬라이스 좁힘 까닭: 창 허용 표는 승인 V 전부를 슬라이스 구분 없이 합치고 창 기록에 «어느 슬라이스 몫으로 소비했나» 가 없음 · 슬라이스는 차례로 돌므로 먼저 소비한 몫은 가장 앞 슬라이스 V 로 봄 · 뒤 슬라이스 V 의 같은 원소는 «아직 집행하지 않은 원소» 로 남아 R-3633 «아직 집행하지 않은 원소의 수정 … 은 지금 절차 그대로» 대로 G1′ 에서 창 기준선 글로 고침(A1-1 · A1-2) · 고치기 전엔 그 낡은 인용이 G1′ 에서 red 로 드러남(A1-0 · v1 은 green 으로 숨겼다가 S2 close 에서 막힘).
- plus 합: 좁힌 owner(가장 앞 슬라이스 V 들)의 덧값 합 · 좁힌 owner 하나면 지금처럼 `≥ 1` · 같은 슬라이스에 V 여럿이면 `≥ 그들 덧값 합`(추가가 V 표시 없이 한 셈 — `approved_change` `:1890`) · A2(V1 S1 · 1 / V3 S2 · 2 · w5 추가 3) → owner V1 하나 → V1 만 결속 · V3 덧값은 G1′ 에서 고칠 수 있음(RD-W25 green) · V 하나도 `≥ k` 로 좁히지 않는 까닭: hits 가 창 단위라 두 창에 나눠 더한 한 V 의 plus 가 어디에도 결속 안 되는 퇴행.
- 슬라이스를 못 읽는 옛 후보(보수 쪽): 실제로 안 생김 — V 머리 줄 정규식(`:2311` `슬라이스\s+(S\d+)`)이 슬라이스 없는 V 를 안 받음 · 스냅숏 `"slice"` 칸은 4cd1999f 부터 · 후보 digest 가 그 칸을 묶어 손대면 `load_candidate` 가 못 찾아 그 창이 증거에서 빠짐. 그래도 닿으면 V 여럿 원소는 결속 안 함(2.43.0 과 같음 · red 가 보이는 쪽) · V 하나 원소는 슬라이스 무관 지금처럼. 러너 사례를 만들 수 없어(digest 가 막음) 변이 표에 안 넣음.
- T1f 덤 결함(한 V 가 같은 원소를 두 줄에): 좁힘 조건이 V id 를 세므로 통과 · old 는 같은 키라 하나로 · plus 에서 V 겹치면 지금처럼 결속 안 함.

### 1-2. 글만 바뀌는 곳(동작 무관)

- `_closed_windows` docstring `:3226-3230` 끝: «집행 결속은 그 결속 판의 원소마다 — 옛 원문 · add · remove 는 그 창 마지막 close 가 소비했으면 그 원소를 적은 V 모두(V 여럿이 적어도 원소 하나 · 한 번 집행 — 허용 표 · G2 verify 와 같은 셈) · 기대 추가는 적은 V 가 하나면 그 창 추가 ≥ 1 · 여럿이면 그 창 추가 ≥ 덧값 합일 때 모두(못 채우거나 한 V 가 두 줄로 적었으면 결속하지 않는다). 적은 V 의 슬라이스가 갈리면 가장 앞 슬라이스의 V 만 owner 로 본다(그 창이 먼저 집행한 몫 — 뒤 슬라이스 V 의 같은 원소는 아직 안 한 원소로 남아 G1′ 에서 고친다 · 덧값 합도 그 V 들의 합) · 슬라이스를 못 읽는 V 가 끼면 결속하지 않는다.»
- `_semantic_reds` docstring `:3392`: «그 창 결속 판에서 모호하지 않고 그 창 마지막 close 가 소비함» → «그 창 결속 판에 있고 그 창 마지막 close 가 소비함 — `_closed_windows`».
- 도움말(동작 무관 · R-3642 · `:3393` «열린 창» 에 맞춤): `:21` · `:3964` `<창 open 기록>` → `<열린 창 open 기록>` · `:7136` → «열린 창의 open 기록(w<n>-open.json) — «바뀌는 기대» 실재를 그 창 기준선에서 본다(닫힌 창 기준선은 changes 가 창 기록으로 고른다)».
- 코드 · docstring 에 규범 번호를 쓰지 않음(R-3632 · R-3633 모두 없음 — grep).

### 1-3. (검토 P 재확인 중요 B) red 글 꼬리 — patch-d

수리판 `repro-a/patch-d/`(patch-c 위 +10 / −1 · `patch-d-over-c.diff` · 2.43.0 대비 약 +41 / −15). `_semantic_reds` 에서 `past_read` 앞에 슬라이스 차례 표와 도움 함수:

```python
    order: "dict[str, int]" = {v.vid: int(v.slice[1:]) for v in spec.v}

    def consumed_by(vid: str, case: str, verb: str, o: str) -> str:
        """이 V 인용이 결속 밖일 때 같은 원소를 앞 슬라이스 V 가 닫힌 창에서 소비했으면 고칠 길 한 구."""
        for w in reversed(past):
            for other in order:
                if order[other] < order[vid] and (other, "old", case, verb, o) in w.executed:
                    return f"(앞 슬라이스 {other} 이 닫힌 창 w{w.n} 에서 소비 — 이 V 인용은 창 기준선 원문으로)"
        return ""
```

red 줄(patch-c `:3486`) 꼬리 `+ (f"({where})" if key else "")` → `+ (f"({where})" if key else consumed_by(v.vid, t.case, t.verb, old))`. 예: `red: V3 시험 …::test_rule 바뀌는 기대 «assert True» 원문이 기준 판 케이스에 없다(앞 슬라이스 V1 이 닫힌 창 w5 에서 소비 — 이 V 인용은 창 기준선 원문으로)`. `v.slice` 는 V 머리 줄 정규식(`:2311`)이 보장. 같은 · 앞 슬라이스 새 V 에는 안 붙음. 기존 RD-W3 · RD-W9 red 줄에도 붙음(S2 V 가 S1 V1 이 소비한 원문을 적는 꼴 · 부분 글 대조라 통과). 사례 `cases_draft3.py`(RD-W24 줄 단언에 그 구) 16/16(운영자 다시 돎 `op-cases3-d.txt` 불일치 0) · RD-W1 ~ W15 20/20 · 관련 묶음 91/91 · 현장 사본 digest 그대로 · 변이 일곱(`mut3/` · 새 m7 «구 지움» 을 RD-W24 가 죽임 · 기존 여섯 그대로).

## 2. 규칙 글 — R-3633 · R-3642 그대로

- **(검토 P 재확인 중요 B 로 바꿈)** F4-199 몫은 R-3633 rev4 의 한 구 — «같은 옛 원문을 슬라이스가 다른 V 여럿이 적었으면 결속은 가장 앞 슬라이스 V 몫뿐이다 — 뒤 슬라이스 V 의 그 인용은 아직 집행하지 않은 원소라 G1′ 에서 창 기준선 원문으로 고친다»(§B 와 같은 판 · 그래프 비용 0 · 문안 `rev-p/RECHECK-1.md`) · R-3642(`:320`)는 이미 «그 열린 창의 open 기록» → 그 밖 글 변경 없음.
- «닫힌 창 open 을 `--baseline` 으로 주지 않는다» 한 구 · 도구 가드는 넣지 않음(v1 과 같음 — 우회 까닭은 이 결함뿐 · 현장 사본 우회 · 수리판 같은 digest · 마지막 close 가 audit 인 창도 감사 «다름» → V 로 G1′(`:312`) → rebind → 다시 close 흐름이 있어 가드가 막을 수 있음 · 그 흐름에서 레인이 무엇을 주는지는 안 잼).

## 3. 러너 사례(초안 `repro-a/cases_draft2.py`)

새 함수 `closed_window_shared_cases(fails, td)` · `main` 에서 `closed_window_cases` 뒤 · 변이도 이 함수만. 공통 꼴: `test_rule`(`assert True`) · V1 · V3 «assert True» update · V2 `test_gone` add · 해소 표 M1 V 칸 `V1 · V3` · G1 확정 → w5 집행(`assert 1 == 1`) → close audit · 슬라이스를 밝히지 않은 사례는 V 모두 S1.

| 사례 | 꼴 | 기대 | 2.43.0 | v1 |
|---|---|---|---|---|
| RD-W16 | 같은 슬라이스 V1 · V3 · 창 사이 `changes`(F4-199) | 0 · `닫힌 창 기준선 3(w5)` | ✗ | ✓ |
| RD-W16b | 같은 꼴 · w6 연 채 `--gate --baseline w6`(현장 꼴) | 0 · `red 0 · gate` | ✗ | ✓ |
| RD-W17 | V1 혼자 같은 원소 두 줄(T1f) | 0 | ✗ | ✓ |
| RD-W18 | V1 · V3 를 지금 글로 다시 씀(R7 · 2.43.0 green 으로 샘) | 2 · 보존 줄 V1 · V3 | ✗ | ✓ |
| RD-W19 | V3 만 지움 | 2 · 보존 줄 V3 · V1 원문 red 없음 | ✗ | ✓ |
| RD-W20 | 새 V9(S2) 가 소비 원문을 다시 적음 | 2 · V9 줄만 | ✗ | ✓ |
| RD-W21 | plus V1(1) · V3(2) 같은 슬라이스 · w5 추가 1 · G1′ 이 V3 를 3으로 | 0 | ✓ | ✓ |
| RD-W22 | 같은 꼴 · w5 추가 3(합) · 뒤에 케이스 지움 | 0 · `닫힌 창 기준선 3(w5)` | ✗ | ✓ |
| RD-W22b | 같은 꼴 · w5 추가 2 · 케이스 지움 | 2 · V1 · V3 `케이스가 기준 판에 없다(지금 시험)` | ✓ | ✓ |
| RD-W23 | 닫힌 change 창 둘(w5 V1 · V3 / w7 G1′ 이 더한 V4 · V5) · 창 사이 | 0 · `닫힌 창 기준선 5(w5, w7)` | ✗(준비부터) | ✓ |
| RD-W23b | 같은 꼴 · `--baseline w7-open` | 0 | — | ✓ |
| RD-W24 | V1(S1) · V3(S2) 같은 원소 · 명세 그대로(T3 A1-0) | 2 · V3 원문 red 만 · V1 red 없음 | ✗ | ✗ |
| RD-W24b | G1′ 이 V3(S2) 를 창 기준선 글로(A1-1) | 0 · `닫힌 창 기준선 2(w5)` | ✗ | ✗ |
| RD-W24c | 같은 꼴 · w6 연 채 `--baseline w6`(A1-2) | 0 | ✗ | ✗ |
| RD-W25 | plus V1(S1 · 1) · V3(S2 · 2) · w5 추가 3 · G1′ 이 V3 를 2 → 1(A2-1) | 0 · V3 보존 줄 없음 | ✓ | ✗ |
| RD-W26 | 같은 슬라이스 · G1′ 이 V3 만 지금 글로(A3 · 현장 꼴) | 2 · 보존 줄 V3 · V1 red 없음 | ✗ | ✓ |

- 영구 사례로 안 남김: 닫힌 창 `--baseline` 우회(R5a ~ R5c · T1c · T1e) · A2-0(명세 무변 — 세 판 모두 0이라 가르는 힘 없음).
- RD-W23 은 G1′ 절을 덧붙여 씀(앞 확정 줄을 남겨야 w5 결속 판이 되살아남 · `CwLane.confirm` 은 scope 를 덮어씀) · 준비 실패는 `fails.append`(`_mutant` 는 러너가 깨지면 «생존» `:7127-7128`).

변이(`_S1_MUTATIONS` 꼴 · 대상 `closed_window_shared_cases` · `repro-a/mut2/` · 옛 글은 v2 에 정확히 한 번):

| 변이 | 바꿈 | 죽이는 사례 |
|---|---|---|
| m1 되돌림(`len(owners) != 1`) | `hit: dict = …\n            if kind == "plus":` 앞에 `if len(owners) != 1: continue` | W16 · 16b · 17 · 18 · 19 · 20 · 22 · 23 · 26 (9) |
| m2 plus 합 → `>= 1` | `need: int = 1 if len(owners) == 1 else sum(…)` → `need: int = 1` | W21 · 22b (2) |
| m3 plus 여럿 결속 안 함 | `done: bool = int(hit.get("add", 0)) >= need` → `len(owners) == 1 and …` | W22 (1) |
| m4 첫 owner 만 | `for vid, extra in owners:` → `owners[:1]` | W16 · 16b · 18 · 19 · 20 · 22 · 23 · 26 (8) |
| m5 슬라이스 좁힘 걷음 | `owners = [ow for ow, s in zip(owners, nums) if s == min(nums)]  …` → `owners = owners` | W24 · 24b · 24c · 25 (4) |
| m6 가장 뒤 슬라이스로 | 같은 줄 `min(nums)` → `max(nums)` | W24 · 24b · 24c · 25 (4) |

«슬라이스 못 읽음 → 결속 안 함» 줄은 닿을 길이 없어 변이 안 넣음(넣으면 생존).

## 4. 진행 중 실행 영향

- 옛 기록(2.42.0 · 2.43.0 창 open · close · 후보) 꼴 그대로 · 읽는 쪽만 · `_same_allow` 무관 · 2.42.0 이 연 현장 w5 도 되살아남(55 → 66).
- red → green: 같은 슬라이스 다중 owner old · add · remove 소비(F4-199 · 현장 red 5 → 0) · T1f · 같은 슬라이스 plus 합 채운 뒤 케이스 사라짐 · 슬라이스가 갈린 꼴은 앞 슬라이스 owner 만 green · 뒤 owner 의 낡은 인용은 red 로 남음(2.43.0 은 둘 다 red · G1′ 에서 그 인용을 고치면 green).
- green → 보존 red: 2.43.0 아래에서 이미 G1′ 이 «가장 앞 슬라이스 owner» 의 소비된 원소를 지금 글로 다시 썼거나 덧값을 바꾼 실행(W18 · W26 꼴) — 다음 G1′ 에서 옛 원문 · 덧값으로 되돌림 · 뒤 슬라이스 owner 를 고친 것은 red 안 됨(W24b · W25 · v1 퇴행 없어짐).
- 그대로: 닫힌 창 `--baseline` 우회로 확정한 실행(그 창이 `upto` 로 빠짐) · 다중 owner 없는 실행 · G2 verify.
- 새 실행 불능 가능: 결속된 원소가 다중 owner 뿐이던 창은 이제 그 창 기준선을 읽음 — head 를 못 읽으면 실행 불능(`_past_reader` 기존 규칙).
- 현장 실행 사본(`repro-a/field-proj/` — 대상 `.git/objects` · 트리 일부 복사 · env · CLAUDE.md · .venv 제외 · 레인 끝 커밋 `3e7e364` 트리 · 대상 폴더에서 명령 안 씀): `changes .dddjango/20261120-0414-refactor-chat-stream --gate` → 2.43.0 exit 2 · red 5(V1 · V3 · V6 ×2 · V7) · `닫힌 창 기준선 55(w5)` / v2 exit 0 · `닫힌 창 기준선 66(w5) · red 0 · gate · 최종 digest(생략)`(현장 마지막 G1 확정 줄 `refactor-scope.md:190` · 2.43.0 + `--baseline w5-open` 우회와 같음) · 마지막 명세는 w5 집행 원소 66 모두 지님(`field_keep.py` · 빠짐 0) · 현장 V1 ~ V8 모두 S1 이라 슬라이스 좁힘 영향 없음.

## 5. 남는 한계

1. 같은 원문이 한 케이스에 두 번 · 같은 슬라이스 V 들이 서로 다른 자리를 노렸어도 한 번 소비로 모두 집행 — 인용 바꾸면 보존 red · 그대로면 green(close 가 원문으로만 가림 · G2 verify 도 같음).
2. 슬라이스가 갈린 owner 에서 «가장 앞 슬라이스가 먼저 소비» 는 추정(창 기록에 창의 슬라이스 없음) — 뒤 슬라이스 창이 먼저 소비했으면(차례 밖 실행 · 수리 창) 집행 표시가 앞 V 에 붙고 뒤 V 인용이 red 로 드러나 G1′ 에서 고치거나 시험 줄을 뺌 — 틀린 쪽은 red(거짓 green 아님).
3. 다중 owner plus 를 여러 창에 나눠 더하면(각 창 < 합) 결속 안 됨(2.43.0 과 같음).
4. 한 V 가 같은 케이스 plus 를 두 줄 → 결속 안 함(지금과 같음).
5. 이론상: 한 케이스에 add 동사 V 의 기대 추가와 update plus 가 함께 → hits.add 에 섞임(현장 · 러너에 없음).
6. 슬라이스 못 읽는 갈래는 닿을 길이 없어 시험 못 함.
7. 닫힌 창 `--baseline` 우회는 여전히 가능(가드 없음).

## 6. 규모

- 도구: 2.43.0 대비 +31 / −14(v1 대비 +12 / −1 · 동작 순증 약 13) · 140자 넘는 줄 수 그대로(2) · Codex 미러 byte 동일.
- 러너: 사례 16 단언(W16 ~ W26 · 약 95줄) + 변이 여섯(약 18줄) · 열두 프로세스로 함께 돌려 187초.
- 검사: `make verify` 전체 + `make verify-mutation` · 규칙 글 · 그래프 · rulepack · REQUEST_GUIDE 바뀔 것 없음.

남긴 것(repro-a/): `patch-c/` · `patch-c.diff` · `patch-c-over-b.diff` · `mut2/` · `cases_draft2.py` · `t_f199_copy.py` · `out-cases2-*.txt` · `out-t3-*.txt` · `out-cw-patch-c.txt` · `out-groups-patch-c.txt` · `out-field-gate-patch-c.txt` · **`field-proj/`(대상 코드 · git 객체 사본 — 일 끝에 꼭 지움)**.
