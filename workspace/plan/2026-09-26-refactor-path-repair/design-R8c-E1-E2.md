# 설계 R8c — E1 residual 근거 판독 · E2 resolution 병합 표기 (2026-09-30)

기준: main HEAD 144e25e9 · 읽기 전용 진단(저장소 파일은 고치지 않음). 모의 실행은 scratchpad `r8c/`(sim.py·sim2.py·sim3.py)와 R8-R2 산출물 사본(`r8c/e2/f`)에서만 돌렸다.
표기: **[실측]** = 이번에 코드를 돌려 확인함 · **[추정]** = 코드 경로를 읽어 추론함(실행하지 않음).
작성: 진단·설계 서브에이전트(운영 세션이 결과를 옮겨 저장) · 사용자 결정 09-30 01시대 «E1 잔존 근거 판독 (권장), E2 병합 표기 (권장)».

## 0 요약

- **E1 뿌리**: `residual --finalize` 는 근거 칸 **전체**를 공백과 `·`로 잘라, `파일:행` 모양으로 읽히는 토큰을 모두 근거로 센다. 그래서 두 가지가 잔존을 만든다.
  - 맥락 위치(남은 자리·제외 범주·설계 근거)가 근거로 잡힌다.
  - 조사가 붙은 진짜 근거는 읽히지 않고 빠진다.
- 실패 4건(core M1·M18, web M10·M11)이 모두 이 두 모양이다 [실측].
- **E1 설계**: 셋을 조합한다. 핵심은 (나)와 (다)다.
  - (나) 근거 칸 판형을 정한다. ` — ` 앞(머리)만 근거로 읽고 뒤(꼬리)는 읽지 않는다. 머리는 모든 토큰이 `파일:행`이어야 한다.
  - (다) 새 상태 «근거 판형 아님»을 «잔존»과 따로 센다. Coordinator 는 코드를 다시 열지 않고, 같은 렌즈에 같은 시각으로 한 번 재기재를 받는다. 두 번째도 판형 아님이면 도구가 잔존으로 센다.
  - (가) 관용은 채택하지 않는다. 혼자서는 1/4 만 고친다 [실측].
- **E2 뿌리**: core `_scope` 의 `keys` 가 결정 줄 머리의 괄호 안까지 ⓐ 키로 읽는다(`refactor_audit.py:1372`).
  - 같은 파일의 다른 세 파서(:1291·:1328·:1443)는 괄호를 벗긴다. 여기만 다르다.
  - `residual` 도 같은 결함을 겪는다. 병합 키가 독립 항목으로 묶인다 [실측].
- **E2 설계**: `_scope` 가 G0 판정(verdict.md)에서 `병합`인 M 을 ⓐ 집합에서 뺀다. 표기 모양과 관계없이 흡수된다.
  - 괄호 벗기기는 쓰지 않는다. 괄호 안에 적힌 진짜 ⓐ 키를 조용히 지워 fail-open 이 된다.
- **web**: E1 은 같은 결함이라 같은 설계를 적용한다. E2 는 해당 없다. web 에는 `resolution` 이 없고, `의미 ⓐ 키:` 행이 괄호 표기를 크게 거부한다 [실측].

## 1 진단

### 1.1 E1 — 근거 칸 판독

**코드 뿌리**

- core `dddjango/scripts/refactor_audit.py`
  - `_parse_location`(:564-569): `` `?([^\s`:]+):(\d+)(?:-(\d+))?`? `` fullmatch.
  - `_locations`(:586-587): `[,·]`·공백으로 자르고 `:` 가 든 토큰만 남긴다.
  - 판정(:1893-1896): `locs = [l for l in (…) if l]`. 파싱 실패는 **조용히 버린다**. 파싱된 위치가 **전부** 실재하고 허용 집합 안이어야 해소다.
- web `dddjango-web/scripts/refactor_audit.py`
  - :523-532 는 core 와 같은 두 함수다.
  - 판정(:1705-1709)도 같다. `_repo_path` 로 `web/` 을 보정하는 것만 다르다.
- 기원: core 는 f985347d(로드맵 5, 09-27), web 은 3c3f0e8f(6b, 09-28). 둘 다 8b 이전이다 [실측 blame].

**결과는 두 갈래다**

- (a) 문장 속 맥락 토큰이 `파일:행`으로 읽히면 실재·허용 검사에서 떨어져 **잔존**이 된다.
- (b) 조사·괄호·마침표가 붙은 진짜 근거는 fullmatch 에서 떨어져 **버려진다**. 남은 위치가 0 이면 잔존이다.

**실패 4건의 토큰 판독** [실측 — `r8c/sim.py`, 현 코드 함수를 그대로 불러 레인 저장소에 적용]

| 레인·시각 | M | 실패 토큰 | 판독 | 계열 |
|---|---|---|---|---|
| R8-R2 0045 discipline | M1 | `judge_action_admission.py:35` («뺀 요지 #5 의 몫» 설명) | 맨 파일 이름 → 실재 안 함 → 잔존 | 맥락 위치 |
| R8-R2 0045 db | M18 | `test_save_limit_rule.py:82`·`test_admin_rejection.py:130` («처음부터 제외한 범주») | 맨 파일 이름 → 실재 안 함 → 잔존 | 맥락(제외) 위치 |
| R8-WR2 2036 discipline | M10 | `return(:46` | 경로 `return(` → 잔존 | 괄호 |
| R8-WR2 2036 discipline | M11 | `…home_view_model.py:15의`·`:16의`·`:22의` | 전부 버려짐 → 위치 0 → 잔존 | 조사 |

- **M1 은 M18 과 같은 계열이다** [실측].
  - ddd 행은 맥락 문구를 «같은 파일 :35»로 적었다. 경로가 없어 파싱되지 않았고, 우연히 해소로 통과했다.
  - discipline 행만 `judge_action_admission.py:35` 로 적어 잔존이 됐다.
- **브리프 정정** [실측]: M10 의 토큰은 `(:46` 이 아니라 `return(:46` 이다(경로 `return(`). `design-spec.md:103에` 는 조사 때문에 버려져서 판정에 들어가지 않았다.
- 재실행에서 해소된 두 판 [실측]
  - 0100 M18: 위치만 적었다.
  - 2039 M10·M11: 판형을 명시해 받았다(`위치 · 위치 — 설명`).
  - 판형을 명시하면 리뷰어가 따른다는 근거다.
- **(가) 관용만 넣으면** [실측 `sim3.py`: 칸 전체에서 조사·괄호를 너그럽게 읽는 경우]
  - M11 만 해소된다.
  - M1·M18 은 그대로 잔존이다.
  - M10 은 원인만 `design-spec.md:103` 로 바뀌어 여전히 잔존이다.
  - 관용은 맥락 위치를 근거로 **더 많이** 끌어들인다.

### 1.2 E2 — 결정 줄 병합 표기

**코드 뿌리** [실측]

- core `_scope`(:1336-1387)의 :1372 `keys = set(re.findall(r"\bM\d+\b", dm.group(1)))` 가 괄호를 벗기지 않는다.
- 같은 줄의 `DecisionLine`(:1328) 은 벗긴다. 주석은 «`M1(+M44)` 의 괄호 = 병합 항목 표기(줄의 키가 아니다)».
- `_reduction`(:1291)·`_resolution_table`(:1443)도 벗긴다. `_scope` 만 파일 관례와 다르다.
- blame: :1372 는 f985347d(8b 이전), red 를 내는 `cmd_resolution`(:1665-1667)은 079b8c49(8b).

**재현** [실측]

- R8-R2 산출물 사본에서 81행을 원래 표기 `- M1(+M27) · M2 · M3(+M28) · … · M7(+M9) · …` 로 되돌리고 HEAD 코드로 `resolution` 을 돌렸다.
- 결과: `red: M9 판정 없음 · M27 판정 없음 · M28 판정 없음` — 레인 t01 기록과 같다.

**`_scope` 의 다른 소비자 `residual`** [실측 — 같은 사본, 빈 `--candidates` 로 실행]

- 묶음에 `### M9`(review-ddd)·`### M27`·`### M28`(review-discipline) 이 독립 항목으로 들어간다. 리뷰어 확인 대상이 27 이 된다.
- 결과 행이 없으면 판단 불가, 파일이 무변이면 결정적 잔존으로 M_m 이 부풀려진다.
- M9 는 병합 대상 M7 이 재상정으로 전체 제외됐는데도 따로 확인된다.

**역방향 모순** [추정]

- 괄호 표기 결정 줄에서는 M27 이 ⓐ 로 들어가 표 행이 **허용**된다.
- 그런데 red 힌트(:1669)는 «병합 항목은 병합 대상 `M<n>` 의 요지로 적는다»라고 한다. 현 상태는 두 방향이 서로 어긋난다.

**web** [실측]

- web 에는 `_scope`·`resolution` 이 없다.
- `residual_m_sets`(`src/debt.py:312`)는 `의미 ⓐ 키:` 값을 `^M[1-9]\d*$` 토큰으로 엄격하게 읽는다. `M1(+M27)` 는 DebtError → 실행 불능(크게 드러나는 실패)이다.
- `_scope_decisions`(:1860)는 이미 `(\+…)` 를 벗긴다. E2 는 web 에 해당 없다.

## 2 설계

### 2.1 E1 — (나) 판형 + (다) 판형 아님 분리. (가)는 채택하지 않는다

**판형(근거 칸 계약)**

- 모양: `<새 파일:행[-행]>[ · <새 파일:행[-행]>…] — <무엇이 어떻게 사라졌는지 한 구>`.
- 8b 해소 판정 표의 «막는 것»(Coordinator `dddjango.md:247`, 도구 `partition("—")` :1543)과 같은 모양이다.
- 머리 = 첫 `—` 앞이다. `—` 가 없으면 칸 전체가 머리다. 위치만 쓴 기존 행(`C_LOC`)은 그대로 통과한다.
- 꼬리(남은 것·제외 범주·설계 근거 위치)는 **읽지 않는다**. 이것이 «제외·맥락 위치를 근거로 세지 않는 방법»이다.

**새 함수 `_ground(cell)`** — `_locations` 바로 뒤에 둔다. 공유 함수 `_parse_location`·`_locations` 는 바꾸지 않는다(다른 소비자 :825·:1084·:1095·:1544·:1819 영향 0).

```python
def _ground(cell: str) -> "tuple[list[tuple[str, int, int]], str]":
    """해소 근거 칸 `<새 파일:행>[ · …] — <한 구>` 의 머리 위치와 첫 불량 토큰(비면 판형) — ` — ` 뒤는 읽지 않는다."""
    toks: "list[str]" = [t for t in re.split(r"\s*[,·]\s*|\s+", cell.partition("—")[0].strip()) if t]
    locs = [_parse_location(t) for t in toks]
    bad: str = "(머리 없음)" if not toks else next((t for t, l in zip(toks, locs) if l is None), "")
    return [l for l in locs if l], bad
```

- 머리는 **모든 토큰이 위치여야** 한다. 산문·조사가 한 토큰이라도 섞이면 판형 아님이다. `_locations` 처럼 조용히 버리지 않는다.

**판정** — 리뷰어가 «해소»라고 한 답 하나마다 아래 순서로 가른다.

| 조건 | 판정 |
|---|---|
| `bad` 가 있음, 또는 위치가 실재하지 않음 / 행 범위 밖(`_location_ok` 거짓) | **근거 판형 아님** (인용 결함 — 코드를 다시 열어도 못 고친다) |
| 형식·실재는 맞지만 하나라도 허용 집합(바뀐 파일 ∪ 감시 경로) 밖 | **잔존** (현행 `all` 규칙 유지) |
| 그 밖 | 해소 |

- 항목(M) 집계 순서: 전부 해소 → 해소 / 잔존이 하나라도 → 잔존 / 판형 아님이 하나라도 → 판형 아님 / 그 밖 → 판단 불가.
  - 잔존이 판형 아님보다 먼저다. 진짜 잔존 주장은 어차피 반송이 필요하기 때문이다.
- `M_m` = 결정적 잔존 + 리뷰어 잔존 + 판형 아님 + 판단 불가. 판형 아님도 `M_m` 에 들어가므로 exit 2 다 — fail-closed.

**재기재 1회 상한** (도구가 강제)

- 확정 때 `result.json` 에 `"unformatted": {M: [렌즈…]}` 를 **누적**해서 쓴다(앞 판 ∪ 이번 판).
- 같은 시각을 다시 확정할 때 앞 판에 판형 아님으로 있던 M 이 또 판형 아니면 «잔존(근거 판형 아님 반복)»으로 센다.
- 고쳐 온 행은 정상 판정을 받는다.
- `_carried` 는 `solved` 만 읽으므로 이월 동작은 변하지 않는다.

**출력**

- result.md 행: `| M11 | 근거 판형 아님(discipline) |` · `| M11 | 잔존(근거 판형 아님 반복) |`
- 요약: `M_m=k(결정적 잔존 a · 리뷰어 잔존 b · 근거 판형 아님 c · 판단 불가 d)`
- `요약:` 뒤 한 행(판형 아님이 있을 때만): `  근거 판형 아님: M11(discipline: `…:15의`) — 그 행만 같은 렌즈 리뷰어에게 판형대로 다시 받아 result-<렌즈>.md 에 고쳐 쓰고 --finalize <시각> 한 번 더(코드 재개봉 아님 · 다시 판형 아님이면 잔존)`
  - 결과를 줄 단위로 읽으려면 `results` 에 렌즈를 싣는다(core :1881 · web :1693 튜플에 lens 추가).
- 묶음 머리 문장(core :1849 · web :1667)을 판형으로 바꾸고 예시 한 줄을 더한다.
  - core 예: `M3 | 해소 | application/<bc>/domain_layer/x/x.py:12-18 · application/<bc>/application_layer/y/y_use_case.py:40 — 판정을 루트 메서드 한 곳으로 옮겼다`
  - web 예: `web/<영역>/<화면>/view_model/<화면>_view_model.py:15-16 — 탭 키 철자를 정의부 한 곳에만 둔다`

**절차 (다)**

- Coordinator 는 판형 아님이 있으면 coder 반송·재개봉 **전에** 그 행만 같은 렌즈에 같은 시각으로 재기재를 받는다.
- 새 residual 시각을 열지 않는다. 모든 렌즈를 다시 파견하게 되기 때문이다(WR2 가 이 경로로 갔다).

**4건 효과** [실측 `sim2.py` — 구 지시로 쓴 행에 엄격한 머리 판독을 적용]

- M10 은 곧바로 해소다.
- M1·M18·M11 은 잔존이 아니라 판형 아님이 되어 재기재 경로로 간다.
- 코드 재개봉과 불필요한 coder 반송이 사라진다.

**버린 대안**

| 대안 | 버린 이유 |
|---|---|
| (가) 관용만 | 1/4 만 고친다(1.1) |
| 실재·허용 위치만 세고 나머지는 무시 | 머리·꼬리 구분 없이 틀린 위치를 버리면, 안 바뀐 파일을 근거로 든 해소가 새어 나간다(fail-open) |
| «`/` 가 든 경로만 위치» 휴리스틱 | 실측 4건은 고치지만, 저장소 상대로 쓴 맥락 위치는 다시 잔존이 된다. 계약 없이 모양 추측에 기댄다 |
| (나)만(판형 아님 = 잔존 유지) | 표기 실수 1회가 여전히 재개봉·반송으로 간다(R8-R2 경로) |
| 머리 관용(위치 아닌 낱말을 버림) | 머리 산문 속 맥락 위치가 다시 근거가 되고, 판형 실수를 잔존으로 보낸다 |

### 2.2 E2 — G0 판정의 병합으로 흡수(표기와 무관). 괄호 벗기기는 채택하지 않는다

core `_scope` 의 반환 직전(:1387)을 이렇게 바꾼다. :1372 는 그대로 둔다.

```python
    merged: "set[str]" = {v.mid for v in _load_verdicts(folder / "audit" / m.group(1)) if v.kind == "병합"}
    return m.group(1), adopted - merged, removed, reductions, lines
```

docstring(:1337)에 «G0 판정 병합 항목(→M·→C)은 대상 항목을 따르므로 결정 줄 표기와 무관하게 뺀다»를 더한다.

**이유**

1. 병합 여부의 단일 출처는 verdict.md 다. `_origins`(:1465)도 같은 출처로 병합 원 행을 대상 M 에 접는다.
2. `M1(+M27)` · `M27→M1` · `M1+M27` · 명시한 `M27` 등 모든 모양을 흡수한다.
3. 소비자 두 곳(`cmd_resolution` :1657 · `cmd_residual` :1789)이 한 번에 고쳐진다.
4. 역방향이 일관된다. 병합 키는 판정 표 **요구 대상이 아니면서** 표 행을 적으면 «범위 밖» red(:1668-1669)다. 힌트 문구와 맞는다.
5. 병합→M 대상은 check-verdict 가 «채택 항목이어야 한다»고 이미 강제한다(:1137-1142).
- 전제: 도구 절차상 verdict.md 는 `_scope` 소비자가 어차피 곧바로 읽는다. 실패 모드가 새로 생기지 않는다.

**버린 대안**

- (A) :1372 를 `DecisionLine.mkeys`(괄호 벗김)로 바꾸기
  - 괄호 없는 모양은 여전히 실패한다.
  - `M2(M3 는 … ⓐ)` 처럼 괄호 안에 적힌 진짜 ⓐ 키가 조용히 사라져 resolution·residual 확인에서 빠진다(fail-open).
- (C) 결정 줄 병합 표기 규칙을 정해 엄격 파싱하기(web 방식)
  - graph-owned 규범이 새로 필요하다.
  - 위반은 크게 드러나지만 한 회차를 쓴다.
  - B 는 절차 문면 변경이 0 이다.

## 3 바꿀 곳

### 3.1 코드 (필수)

| 파일:행 | 변경 | 판정 |
|---|---|---|
| `dddjango/scripts/refactor_audit.py:586-587` 뒤 | `_ground` 신설 | 코드 · «상시 답 인식 블록»(:159-193) 밖 |
| 같은 파일 :1337 · :1387 | E2 병합 차감 + docstring (:1372 불변) | 코드 |
| 같은 파일 :1849 | 묶음 머리 판형 문장 + 예시 | 코드 |
| 같은 파일 :1876-1919 | 결과에 렌즈 · `_ground` 판정 · 집계 · 반복 상한 · result.md/json · 요약과 뒤 행 | 코드 |
| `dddjango-web/scripts/refactor_audit.py:531-532` 뒤 · :1667 · :1688-1733 | E1 같은 변경(`_repo_path` 유지). E2 없음 | 코드 · 블록(:1739-1773) 밖 |
| `codex-dddjango/skills/dddjango/scripts/refactor_audit.py` | core 를 byte 복사 | byte 미러(verify-base-core `diff -rq` Makefile:178) |
| `codex-dddjango-web/skills/dddjango-web/scripts/refactor_audit.py` · `…/scripts/test/fixtures_refactor_audit.sh` | web 을 byte 복사 | byte 미러(verify-web Makefile:105) |

### 3.2 core 문면 — 전부 graph-owned (md 직접 수정 금지)

| md:행 | 절/블록 | ttl 정본 | 규범 |
|---|---|---|---|
| `dddjango/commands/dddjango.md:253` | s012/b12 (마커 :223) | `ontology/rules/command-dddjango.ttl:4859`(블록) · :3732(노드) | R-3535 개정 rev3(amendment) |
| `dddjango/agents/design-review-ddd.md:63` | s006/b6 (마커 :51) | `agent-design-review-ddd.ttl:607` · :349 | R-3544 rev2 |
| `dddjango/agents/design-review-db.md:63` | s006/b6 (마커 :51) | `agent-design-review-db.ttl:670` · :413 | R-3551 rev2 |
| `dddjango/agents/design-review-api.md:106` | s008/b6 (마커 :94) | `agent-design-review-api.ttl:1381` · :917 | R-3559 rev2 |
| `dddjango/agents/discipline-reviewer.md:156` | s009/b6 (마커 :144) | `agent-discipline-reviewer.ttl:3452` · :2725 | R-3567 rev2 |

- 새 규범은 없다 → `ISSUED` 채번 없음. R-3536(반송) 라벨은 «판형 아님 해소 뒤 M>0» 에도 참이라 두고 바꾸지 않는다.
- Coordinator 문면
  - 현: «(새 `파일:행` 근거 없는 해소는 잔존 · 리뷰어 확인 대상이 0 이면 첫 호출이 곧 판정이다)»
  - 새: «(해소 근거 칸은 `<새 파일:행>[ · <새 파일:행>…] — <한 구>` 이고 ` — ` 앞 위치만 근거로 센다 — 그 위치가 `build_anchor` 이후 바뀐 파일·항목 감시 경로 밖이면 잔존, 머리가 위치만이 아니거나 위치가 실재하지 않으면 «근거 판형 아님» · 리뷰어 확인 대상이 0 이면 첫 호출이 곧 판정이다). «근거 판형 아님»이 있으면 반송 전에 그 행만 같은 렌즈 리뷰어에게 판형대로 다시 받아 같은 `result-<렌즈>.md` 에 고쳐 쓰고 같은 시각으로 `--finalize` 를 한 번 더 돈다(코드 재개봉·새 시각이 아니다 · 두 번째 확정에서도 판형 아님이면 도구가 잔존으로 센다).»
- 리뷰어 문면
  - 현: «해소의 근거는 새 `파일:행` 이다(근거 없는 해소는 잔존으로 처리된다).»
  - 새: «해소의 근거 칸은 `<새 파일:행[-행]>[ · <새 파일:행[-행]>…] — <무엇이 어떻게 사라졌는지 한 구>` 다 — ` — ` 앞에는 저장소 루트 기준 새 위치만(조사·괄호·설명 없이), 남은 것·제외 범주·설계 근거 같은 맥락 위치는 ` — ` 뒤에만 적는다(앞 위치만 근거로 센다 · 판형이 아니면 그 행을 다시 요청받는다).»
- prefLabel 을 같은 취지로 고친다. R-3535: «근거 없는 해소는 잔존» → «해소 근거 = ` — ` 앞 새 위치 · 판형 아님은 같은 렌즈 재기재 1회 뒤 잔존».
- 딸린 작업(memory 레시피 순서)
  - rdflib + canon 재직렬화 → `ontology_gate.py` → `ontology_render.py --apply` × 5 doc_key.
  - `ontology/LEDGER.tsv` 재기준선 행 × 5: command-dddjango s012 · agent-design-review-api s008 · -ddd s006 · -db s006 · agent-discipline-reviewer s009.
  - `workspace/eval/fixtures/ontology_gate/target-counts.json` ExpressionShape +5(3810→3815 [추정], 게이트가 확정).
  - `make rulepack`(core + codex rulepack.json). q4 골든은 verify 가 red 일 때만 `--emit`.
- Codex 의미 미러(손으로)
  - `codex-dddjango/skills/dddjango/SKILL.md:269`
  - `codex-dddjango/skills/dddjango-design-review-ddd/SKILL.md:61`
  - `…-design-review-db/SKILL.md:60`
  - `…-design-review-api/SKILL.md:101`
  - `…/dddjango-discipline-reviewer/SKILL.md:148`

### 3.3 web 문면 — 전부 산문 정본 (LEDGER 대상 아님)

- `dddjango-web/commands/dddjango-web.md:308`
  - «(새 `파일:행` 근거 없는 해소는 잔존이다)»를 위 Coordinator 문면으로 바꾼다(`build_anchor` → `git_snapshot`).
  - «M>0 이면 해당 항목만 슬라이스 0 을 1회 재개봉» 앞에 판형 아님 재기재 문장을 넣는다.
- `dddjango-web/agents/discipline-reviewer-web.md:46` · `design-review-web.md:41`: 리뷰어 문면(예시 경로는 `web/…`).
- Codex 의미 미러
  - `codex-dddjango-web/skills/dddjango-web/SKILL.md:333`
  - `…/dddjango-web-discipline-reviewer-web/SKILL.md:47`
  - `…/dddjango-web-design-review-web/SKILL.md:44`
- G2 문단은 verify-web cmp 목록(Makefile:103 — `**Phase 1~2**`·`**상시 답**`) 밖이다. 손으로 맞춘다.

### 3.4 봉인

- `refactor_audit.py`·`commands/dddjango.md`·codex Coordinator SKILL.md 는 pipeline 봉인 대상이다. `agents/*.md`·`ontology/**`·rulepack 도 봉인 대상이다.
- 커밋 뒤 별도 chore 커밋으로 `manifest_seal.py --write` 한다(DEVELOPMENT §6).

## 4 시험

### 4.1 core — `workspace/tools/refactor_audit_fixture_run.py`

- 새 함수 `residual_ground_cases` 는 새 td 에서 `_res_folder` 를 쓴다. M1=P_LOC(무변), M2=C_LOC(바꿈), 결정 줄 `- M1, M2 · 결정 = ⓐ`.
- 괄호 안 «현행»은 HEAD 코드의 결과다.

**재현 (양성)**

| ID | 근거 칸 | 기대 | 현행 |
|---|---|---|---|
| G1 조사, 판형 아님 (WR2 M11 모양) | `이 파일의 리터럴은 {C_LOC}의 정의 한 곳` | «근거 판형 아님 1 · 리뷰어 잔존 0», exit 2 | 리뷰어 잔존 1 |
| G2 조사가 꼬리 | `{C_LOC} — 리터럴은 {C_LOC}의 정의 한 곳` | 해소 | — |
| G3 괄호 (WR2 M10 모양) | `{C_LOC} — 남은 두 return(:46 · :49)은 표기 반복(design-spec.md:103에 이유)` | 해소 | 잔존 |
| G4 맥락·제외 위치 (R2 M18·M1 모양) | `{C_LOC} — 남은 리터럴 thing_controller.py:3·5 는 처음부터 제외한 범주 · policy.py:9 문구는 뺀 요지 몫` | 해소 | 잔존 |

**fail-closed (음성)**

| ID | 근거 칸 | 기대 |
|---|---|---|
| N1 꼬리에만 위치 | `— 남은 리터럴 {C_LOC} 는 제외 범주` | 판형 아님(해소가 아니다) |
| N2 허용 밖 머리 | `{T_LOC} — …` | 리뷰어 잔존 1(판형 아님이 아니다) |
| N3 섞인 머리 | `{C_LOC} · {T_LOC} — …` | 잔존 |
| N4 실재 안 함 | `thing_controller.py:7 — …` 와 `…thing_controller.py:999 — …` | 판형 아님 |
| N5 머리에 산문 | `{C_LOC} 에서 고침 — …` | 판형 아님 |
| N6 반복 상한 | N1 확정 → 같은 시각 재확정 | «잔존(근거 판형 아님 반복)» · 리뷰어 잔존 1 → 세 번째에 G2 행이면 해소 |
| N7 집계 | 같은 M 두 행 `잔존` + `해소 \| 고쳤다` | 리뷰어 잔존 1 · 판형 아님 0 |

**출력**

- O1: G1 출력에 `근거 판형 아님: M2(ddd` 와 `--finalize <stamp>`.
- O2: `review-ddd.md` 에 `` ` — ` 앞에는 `` 문장과 예시.

**기존 단언 수정**: :382-384 («고쳤다» → 리뷰어 잔존 1)는 «근거 판형 아님 1 · 리뷰어 잔존 0» 으로 바꾼다. :386-392 는 그대로 둔다.

**E2** (`resolution_cases` · `residual_cases` 확장. verdict 에 M4 병합→M1, M5 병합→M2 가 이미 있다)

| ID | 입력 | 기대 | 현행 |
|---|---|---|---|
| E2-1 | 결정 줄 `- M1(+M4), M2, M3 · 결정 = ⓐ` + RES_ROWS | `red 0` | «M4 판정 없음» — 실측 재현과 같은 모양 |
| E2-2 | `- M1, M2, M3, M4 · 결정 = ⓐ`(명시) | `red 0` | — |
| E2-3 역방향 | E2-1 결정 줄 + 표에 M4 행 | «M4 범위 밖» red | — |
| E2-4 괄호가 진짜 키를 지우지 않음 | `- M1, M2(M3 는 사용자 판단 뒤 ⓐ) · 결정 = ⓐ` + 표에서 M3 행 뺌 | «M3 판정 없음» red | — |
| E2-5 residual | 결정 줄 `C1, M1, M2(+M5), M3` | «결정적 잔존 1» · 묶음에 `### M5` 없음 · `(병합 M5)` 는 M2 아래 | 결정적 잔존 2 [추정 — M5 파일 policy.py 무변 바닥] |

### 4.2 web — `dddjango-web/scripts/test/fixtures_refactor_audit.sh` §I (:351-388)

- I3(:369-371): `M10 | 해소 | 이유만 적음` 의 단언을 «리뷰어 잔존 1» → «리뷰어 잔존 0 · 근거 판형 아님 1» 로 바꾼다.
- 새 사례 I3a~g (같은 STAMP 에 result-screen.md 를 고쳐 쓰며 재확정)

| ID | 근거 칸 | 기대 |
|---|---|---|
| I3a 머리에 조사 (M11 모양) | `…home_view.py:2의 정의` | 판형 아님 |
| I3b 꼬리에 조사 | `web/home/home/view/home_view.py:2 — …:1의 정의 한 곳` | 해소 |
| I3c 괄호·설계 근거 (M10 모양) | `…:1-2 — 남은 두 return(:46 · :49)은 표기(design-spec.md:103에)` | 해소 |
| I3d `web/` 없는 머리 | `home/home/view/home_view.py:2 — …` | 해소(`_repo_path` 유지) |
| I3e 꼬리에만 위치 | — | 판형 아님 |
| I3f 무변 파일 머리 | `web/base/base.html:1 — …` | 잔존 |
| I3g 반복 상한 | 같은 시각 재확정 | 잔존(반복) |

- I4(:378-379)는 «M9 확정 해소 이월» 이 전제다. 마지막 재확정은 M9 해소 행으로 끝낸다.

### 4.3 변이 검출

구현 중 작업 트리에서 한 줄씩 되돌려 red 를 확인하고 복원한다. 커밋에 넣지 않는다. core·web 둘 다 한다.

| 변이 | 잡는 사례 |
|---|---|
| V1 머리·꼬리 분리 제거(칸 전체 `_locations`) | G3·G4 red · N1 이 해소가 됨(fail-open 검출) |
| V2 머리 관용(비위치 낱말 버림) | N5 · G1 |
| V3 머리 `all`→`any` | N3 |
| V4 판형 아님을 M_m 에서 뺌 | G1·N1 exit 2 기대 |
| V5 반복 상한 제거 | N6 · I3g |
| V6 집계 순서(판형 아님 먼저) | N7 |
| V7 실재 실패를 잔존으로 | N4 |
| V8 병합 차감 제거 | E2-1·E2-2·E2-5 |
| V9 차감 대신 괄호 벗기기(`DecisionLine.mkeys`) | E2-2 · E2-4(fail-open 검출) |

## 5 위험과 한계

1. **판형 미준수**
   - 8b 에서 구 지시로 쓴 해소 행 33개 가운데 27개가 엄격한 머리 판독에서 판형 아님이다 [실측 `sim2.py`].
   - 새 묶음 머리·예시·에이전트 문면이 전제다. 판형을 명시한 2039 는 2/2 준수했다 [실측].
   - 대량 미준수는 재기재 1회 → 잔존 → 반송으로 이어져 비용이 든다. 한도는 있다.
2. **꼬리를 읽지 않아 잃는 것**
   - 현행 `all` 규칙은 «해소라 하면서 안 바뀐 파일의 남은 자리를 문장에 언급»한 경우를 우연히 잡았다. 꼬리로 가면 보지 않는다.
   - 머리 위치가 항목과 무관한 바뀐 파일이어도 통과하는 점은 현행과 같다. 의미 판정 틈은 E3 범위다.
3. **반복 상한의 범위**: 같은 시각 재확정에만 걸린다. 새 시각을 열면 새로 센다. 절차 문면이 막는다.
4. **E2 의 기준**: verdict.md 원 판정 기준이다. `_origins` 와 같은 출처라 일관된다. verdict-log 재분류가 병합을 바꾸는 경로가 있는지는 확인하지 않았다 [추정: 없음].
5. **web 의 명시 병합 키**: `의미 ⓐ 키:` 에 병합 키를 명시하는 가상 경우는 web 이 막지 않는다. 관찰된 적 없어 범위 밖이다.
6. **남는 괄호 벗기기**: `DecisionLine.mkeys`·`_reduction` 의 괄호 벗기기(상시 답·요지 축소 줄)는 그대로다. 이론상 같은 종류의 누락이 있다. 범위 밖이다.
7. **막는 것 파서와의 차이**: resolution «막는 것» 머리는 여전히 `_locations` 로 너그럽게 읽는다(비위치 낱말 버림). residual 의 엄격한 머리와 다르다. 통일은 후속이다.
8. **릴리즈 창**: `dddjango/scripts/` 가 바뀌면 pre-gate digest 가 stale 이 된다. 진행 중인 G1~G2 레인이 착륙한 뒤 릴리즈한다(DEVELOPMENT §6).
9. **상시 답 블록**: 건드리지 않는다. core 블록 :159-193 · web 블록 :1739-1773. Makefile:102 cmp 가 그대로 green 이어야 한다.

## 6 구현 순서

1. **E2 core**: `_scope` 차감 + E2-1~5 사례 → `python3 workspace/tools/refactor_audit_fixture_run.py` → V8·V9 변이 확인.
2. **E1 core**: `_ground` · 판정·집계·상한 · 머리 문장·요약 → G·N·O 사례와 기존 :382-384 수정 → V1~V7.
3. **E1 web**: 같은 변경 → §I 수정과 I3a~g → `bash dddjango-web/scripts/test/run_fixtures.sh` → 변이 확인.
4. **byte 미러**: core 스크립트, web 스크립트, web 픽스처를 codex 로 복사.
5. **온톨로지**
   - R-3535 rev3 · R-3544/3551/3559/3567 rev2 (rdflib + canon) → `ontology_gate.py` → `ontology_render.py --apply` × 5.
   - LEDGER 재기준선 × 5 → target-counts → `make rulepack`.
6. **의미 미러**: core Codex SKILL.md 5곳 · web md 3곳 · web Codex SKILL.md 3곳.
7. **검증**: `make verify`(ontology · base-core · base-cross · base-backstop · base-regen) 와 `make verify-web`. 두 로그 경로를 남긴다.
8. **커밋**: 사용자 승인 뒤 커밋한다. 봉인 재발행은 별도 chore 커밋으로 한다. 이후 재리허설 또는 현장 레인 1개에서 residual 1회차 해소를 관찰한다.

## 7 리뷰 처분 (09-30 · 운영 세션 — 이 절이 §0~§6 의 해당 문장을 대체한다)

적대 리뷰 scratch `review-R8c/review-R8c.md` — «수정 후 승인» · blocker 1 · major 4 · minor 5 · nit 2. 전건 수용(아래). 사용자 결정 범위(E1·E2) 안이고 자명한 처분이라 사용자에게 묻지 않는다.

| 리뷰 | 처분 |
|---|---|
| B1 E2 병합 출처 | **수용** — `_scope` 차감 출처를 verdict.md 가 아니라 `audit/<시각>/verdict-log.md` 마지막 exit 0 판(`_previous(...)[0]`)으로. 로그가 없으면 빼지 않는다(fail-closed). §2.2 이유 1·5 와 §5.4 는 틀렸다. 시험 E2-7 · 변이 V10 추가 · E2 픽스처는 check-verdict 를 먼저 돌려 로그를 만든다. |
| M1 재확정 상한 | **수용 — 동결** — `result.json` 에 `"states": {M: 판정}` · 같은 시각 재확정은 앞 판 `판형 아님`(또는 답 행 부재)인 M 만 다시 판정 · 나머지 판정·`solved` 지문 유지 · 다시 판형 아님이면 잔존(반복) 동결. §2.1 «재기재 1회 상한»(`unformatted` 누적)을 대체. N6 기대 = 3차도 잔존 · 새 사례 «같은 시각 잔존 행 뒤집기 → 잔존 유지» · 기존 core :382-392 · web I3a~g 는 사례마다 시각을 새로 연다. |
| M2 산출물 폴더 | **수용** — 머리 허용 집합에서 산출물 루트(`folder` 의 부모 · project 상대) 아래를 뺀다 · core·web · 시험 1. |
| M3 렌즈 완전성 | **수용** — 파견 렌즈 중 답하지 않은 렌즈가 있으면 판단 불가 · core·web · 시험 1. |
| M4 범위 | **수용 — 최소안** — 에이전트 규범 R-3544/3551/3559/3567 개정과 에이전트 md·Codex 12곳을 뺀다(§3.2 표 2~5행 · §3.3 에이전트 줄 삭제). 문면은 core Coordinator R-3535 rev3(절차 한 문장 + prefLabel) · Codex `SKILL.md:269` · web `dddjango-web.md:308` · web Codex `SKILL.md:333` 만. 판형 정의는 도구 묶음 머리 한 곳. 온톨로지 = 1 doc_key(render · LEDGER 1 · ExpressionShape +1 · rulepack). |
| m1 상태 정확 일치 | **수용** — `*`·백틱 벗긴 뒤 `해소`·`잔존`·`판단 불가` 정확 일치만, 그 밖은 판단 불가. |
| m2 절대·`..` 경로 | **수용** — 판형 아님. |
| m3 흔한 모양 | **수용(예시 명시만)** — 묶음 머리에 «위치마다 경로:행을 전부 적는다(`:16`·`15·16` 줄임 없이) · 구분은 ` · `». 맨 `:N` 경로 이어받기는 넣지 않는다(단순성 · 관찰 뒤 판단). |
| m4 절차 문면 | **수용** — «residual 시각마다 한 번 — 반송·STOP 판단 전에». R-3536 그대로. |
| m5 시험 누락 | **수용** — E2-6 · E2-7 · V10 · 대시 변형 1 · 절대 경로 · 렌즈 완전성 · 산출물 폴더 · 상태 정확 일치 · 동결. |
| n1 | 정정 — 구 지시 33행 중 **28행** 판형 아님. |
| n2 core `_origins` verdict.md | 범위 밖 — 후속 후보로 기록(web 은 `verdict-final.md`). |
