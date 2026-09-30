# 수리 R8c 구현 기록 — E1 residual 근거 판독 · E2 resolution 병합 표기 (로드맵 8c)

> **최종 상태는 §9(구현 리뷰 처분) 반영본이다.** §0–§7 은 1차 구현 기록이다. §9 가 바꾼 것: 동결 규칙(MJ1) · E2 차감 조건(mi1) · 판형 아님 이력 `redo`(mi2) · 산출물 루트(n1 — §3.8 방어 규칙 대체) · 판정 칸 판독(n4 — §0·§2.2 «잔존 정확 일치» 대체) · 문면 괄호 문구(n3) · 사례·변이·verify 수치.

- 작성: 2026-09-30 · 격리 워크트리 `.claude/worktrees/agent-a8e7f88b837713dae`(브랜치 `worktree-agent-a8e7f88b837713dae`)에서 구현했다. **커밋 0 · push 0** 이다. 변경은 미커밋 diff 로 남긴다.
- 입력
  - 설계: `design-R8c-E1-E2.md`(메인 체크아웃 · 미추적). **§7 «리뷰 처분»이 §0~§6 의 해당 문장을 대체한다** — 이 구현은 §7 최소안을 따랐다.
  - 적대 리뷰: `scratchpad/review-R8c/review-R8c.md`(수정 후 승인 · blocker 1 · major 4 · minor 5 · nit 2)
- 기준 커밋: 워크트리는 `acbfffda` 에서 시작했다. main `144e25e9`(설계 기준)의 조상(20 커밋 뒤)이라 `git merge --ff-only main` 으로 포인터만 앞당겼다(새 커밋 없음). 아래 diff 는 `144e25e9` 기준이다.
- Serena·Graphify 는 쓰지 않았다(지시). `make verify` 용 `.venv` 심링크(→ 메인 `.venv`)는 검증 뒤 지웠다.
- 로그·실험 도구 위치(scratch): `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/`(`r8c-*.log` · `r8c_*.py` · `webmut/`)
- 표기: **[실측]** = 이번에 돌려 확인함 · **[추정]** = 코드를 읽어 추론함.

## 0. 요약

- **E2(core)**: `_scope` 가 반환 직전 ⓐ 집합에서 `audit/<시각>/verdict-log.md` 마지막 exit 0 판(`_previous(...)[0]`)의 `병합→M`·`병합→C` 키를 뺀다. 로그가 없으면 빼지 않는다(fail-closed). :1372(키 읽기)는 그대로다.
- **E1(core·web)**: 해소 근거 칸을 `_ground` 로 읽는다. 머리(첫 `—` 앞)의 토큰이 전부 위치여야 하고, 꼬리는 읽지 않는다.
  - 새 상태 «근거 판형 아님»을 두고 `M_m` 에 넣는다(exit 2). 절대·`..` 경로 머리와 실재·행 범위 실패도 판형 아님이다.
  - 허용 집합에서 산출물 루트(`folder` 의 부모) 아래 파일을 뺀다(M2).
  - 파견 렌즈 가운데 답하지 않은 렌즈가 있으면 판단 불가다(M3).
  - 판정 칸은 `*`·백틱을 벗긴 뒤 `해소`·`잔존`·`판단 불가` 와 정확히 같아야 한다(m1).
  - 같은 시각 재확정은 **동결**한다(M1). `result.json` `"states"` 에서 앞 판이 판형 아님이나 답 없음인 M 만 다시 판정한다. 또 판형 아님이면 잔존(반복)이다.
  - result.md 행, 요약 계수, `요약:` 뒤 재기재 안내 행, 묶음 머리 판형 문장·예시를 더했다.
- **문면**: core R-3535 rev3(amendment · 절차 한 문장 + prefLabel)를 rdflib+canon 으로 편집했다. 이어서 게이트 → 재투영 → LEDGER 1행 → ExpressionShape +1 → rulepack 을 거쳤다. Codex core SKILL · web md · web Codex SKILL 은 손 미러다. 에이전트 md·그 Codex SKILL 은 바꾸지 않았다(§7 M4).
- **시험**
  - core 픽스처는 143 ✓ 에서 **180 ✓** 가 됐다(+37).
  - web 픽스처는 115 에서 **137 PASS** 가 됐다(+22).
  - 새 사례 가운데 HEAD 도구에서 red 인 것은 core 30건 · web 20건이다 [실측].
- **변이**: core 15/15 · web 13/13 을 잡았다(V1~V10, V5 는 a·b 로 나눔, 보강 X1~X5) [실측].
- **verify**
  - `make verify` 는 4묶음 green 이고, verify-base-core 만 RED 다.
  - 그 RED 는 봉인 드리프트 14건(모두 이번 변경 파일)뿐이다. 새로 뽑은 manifest 로 대조하면 green 이다 [실측 §6].
  - `make verify-web` 은 green 이다.

## 1. 바뀐 파일 (`git diff --numstat` · 144e25e9 기준)

| 파일 | +/− | 내용 |
|---|---|---|
| `dddjango/scripts/refactor_audit.py` | +88/−33 | `_ground` 신설(`_locations` 바로 뒤) · `_scope` E2 차감 + docstring · 묶음 머리 판형 문장·예시 · `--finalize` 판정 블록 재작성(렌즈 실은 결과 · 동결 · 산출물 루트 제외 · 렌즈 완전성 · 정확 일치 · 집계 · result.md/json · 요약 · 재기재 안내) |
| `codex-dddjango/skills/dddjango/scripts/refactor_audit.py` | +88/−33 | byte 미러 |
| `dddjango-web/scripts/refactor_audit.py` | +84/−34 | 같은 E1 변경(`_ground` 본문 core 와 byte 동일 · 판정에 `_repo_path` 유지 · web 예시) — E2 없음 |
| `codex-dddjango-web/skills/dddjango-web/scripts/refactor_audit.py` | +84/−34 | byte 미러 |
| `workspace/tools/refactor_audit_fixture_run.py` | +203/−7 | `residual_ground_cases`·`e2_cases` 신설 · `_fresh_stamp` 도우미 · `_res_folder(disc=)` · 기존 residual 사례 재구성(§4.1) |
| `dddjango-web/scripts/test/fixtures_refactor_audit.sh` | +59/−4 | §I 재구성: I2b·I2c · I3(단언 변경)·I3′~I3‴ · I3a~I3p · `OPEN`·`FIN` 도우미 |
| `codex-dddjango-web/skills/dddjango-web/scripts/test/fixtures_refactor_audit.sh` | +59/−4 | byte 미러 |
| `ontology/rules/command-dddjango.ttl` | +9/−3 | R-3535 prefLabel · currentExpression → `R-3535@2026-09-30`(rev 3 · amendment · wasRevisionOf `@2026-09-29`) · 블록 s012/b12 text 에 절차 한 문장 |
| `dddjango/commands/dddjango.md` | +1/−1 | `ontology_render.py --apply command-dddjango` 재투영(G2 문단 한 줄) |
| `ontology/LEDGER.tsv` | +1 | `command-dddjango s012 d8f15609…bec graph … rebaseline:2026-09-30 로드맵 8c R8c E1 — R-3535 rev3 …` |
| `workspace/eval/fixtures/ontology_gate/target-counts.json` | +1/−1 | ExpressionShape 3810 → 3811(`ontology_hierarchy_check.py --with-golden` green 확인) |
| `dddjango/scripts/rulepack.json` · Codex 미러 | +4/−4 | `make rulepack` 재소성(R-3535 라벨·개정) |
| `codex-dddjango/skills/dddjango/SKILL.md` | +1/−1 | G2 문단에 core 와 같은 절차 한 문장. core :253 과 Codex :269 줄은 diff 0 |
| `dddjango-web/commands/dddjango-web.md` · `codex-dddjango-web/skills/dddjango-web/SKILL.md` | +1/−1 씩 | G2 문단(:308 · :333)에 web 표현의 절차 한 문장 |
| 이 문서 | 신규 | |

바꾸지 않은 것
- core «상시 답 인식 블록»과 web 복사본은 그대로다. `sed` 로 뽑아 cmp 하면 동일하고, verify-web 의 대조도 green 이다.
- 공유 함수 `_parse_location`·`_locations` 는 그대로다.
- 에이전트 md 6종과 그 Codex SKILL, R-3544/3551/3559/3567, ISSUED 는 건드리지 않았다(새 채번 없음).

## 2. 구현 요점

### 2.1 E2 — `_scope` (core :1407-1409 · `_ground` core :590 · web :535)

```python
    kinds, _origin = _previous(folder / "audit" / m.group(1) / "verdict-log.md")
    merged: "set[str]" = {k for k, kind in kinds.items() if kind in ("병합→M", "병합→C")}
    return m.group(1), adopted - merged, removed, reductions, lines
```

- `_previous(log)` 는 `(M → 로그 판정 라벨, 원 행 → M)` 을 돌려준다. 파일이 없거나 exit 0 판이 없으면 `({}, {})` 이다. 로그 라벨은 `Verdict.label`(`병합→M`·`병합→C`)이다.
- 소비자 둘이 함께 고쳐진다. `cmd_resolution` 은 «판정 없음»·«범위 밖»을, `cmd_residual` 은 묶음·바닥을 이 집합으로 가른다.

### 2.2 E1 — `_ground` 와 판정

- `_ground(cell)` 은 `(위치 목록, 첫 불량 토큰)` 을 돌려준다.
  - 머리 = `cell.partition("—")[0]` 이다. 토큰 구분은 `[,·]` 와 공백이다.
  - 토큰이 없으면 `(머리 없음)` 을 돌려준다.
  - 위치로 읽히지 않는 토큰, 절대 경로, normpath 가 `..` 로 시작하는 토큰이 있으면 그 토큰을 불량으로 돌려준다.
- 행 판정은 다음 순서로 간다.
  - 판정 칸 정확 일치가 `해소` 면 `_ground` 로 읽는다. 불량 토큰이 있거나 위치 중 하나가 `_location_ok` 거짓이면 **판형 아님** 이다. 이유는 `경로:행[-행]` 으로 남긴다.
  - 그렇지 않고 모든 위치가 허용 집합 안이면 해소, 하나라도 밖이면 잔존이다.
  - 허용 집합은 (앵커 이후 바뀐 파일 − 산출물 루트 아래) ∪ 항목 감시 경로다.
  - web 은 위치를 `_repo_path` 로 저장소 경로로 바꾼 뒤 같은 판정을 한다.
- 항목 집계에서는 파견 렌즈 가운데 답이 없는 렌즈마다 `답 없음` 을 하나씩 더한다.
  - 전부 해소면 해소다.
  - 그 밖이면 우선순위는 잔존 > 판형 아님 > 답 없음 > 판단 불가 순이다.
  - 앞 판도 판형 아님이었는데 또 판형 아님이면 `잔존(반복)` 이다.
- 동결: 같은 `out_dir/result.json` 의 `"states"` 에서 `판형 아님`·`답 없음` 이 아닌 M 은 앞 판정을 그대로 쓴다. 앞 판이 해소면 앞 판 `solved` 지문도 유지한다. 새 시각에는 `"states"` 가 없어 전부 새로 판정한다. `_carried` 는 여전히 `solved` 만 읽는다.
- 출력
  - `요약: residual M_m=k(결정적 잔존 a · 리뷰어 잔존 b · 근거 판형 아님 c · 판단 불가 d) · 해소 …`
  - result.md 행은 `| M | 근거 판형 아님(<렌즈>) |`, `| M | 잔존(근거 판형 아님 반복) |` 이다. 판단 불가 행에는 답 없음도 포함된다.
  - 판형 아님이 있으면 `요약:` 뒤에 한 행을 낸다: `  근거 판형 아님: M2(ddd: \`고쳤다\`) — 그 행만 같은 렌즈 리뷰어에게 묶음 머리의 판형대로 다시 받아 result-<렌즈>.md 에 고쳐 쓰고 --finalize <시각> 한 번 더(코드 재개봉·새 시각 아님 · 다시 판형 아님이면 잔존)`
  - `result.json` 은 `{"stamp", "solved", "states"}` 이다. web 은 여기에 `"audit"`·`"snapshot"` 도 유지한다.
- 묶음 머리(`review-<렌즈>.md`)
  - 결과 표 형식 줄 뒤에 판형 문장을 둔다: ` — ` 앞에는 저장소 루트 기준 새 위치만 · 위치마다 경로:행을 전부(`:16`·`15·16` 줄임 없이) · 구분 ` · ` · 맥락 위치는 ` — ` 뒤에만 · 판형이 아니면 다시 요청받는다.
  - 예시도 한 줄 둔다. core 예시는 `application/<bc>/…`, web 예시는 `web/<영역>/<화면>/view_model/…` 이다.

### 2.3 문면

- core Coordinator(graph-owned · R-3535 rev3)에 G2 문단의 «…곧 판정이다).» 뒤로 한 문장을 넣었다: «확정 요약에 `근거 판형 아님` 이 있으면 residual 시각마다 한 번 — 반송·STOP 판단 전에 — 그 행만 같은 렌즈 리뷰어에게 묶음 머리의 판형대로 다시 받아 같은 `result-<렌즈>.md` 에 고쳐 쓰고 같은 시각으로 `--finalize` 를 한 번 더 돈다(코드 재개봉·새 시각이 아니다 · 다시 판형 아니면 잔존이다).»
  - prefLabel 에서 «근거 없는 해소는 잔존» 을 «해소 근거 = ` — ` 앞 새 위치 · 근거 판형 아님은 시각마다 같은 렌즈 재기재 1회 뒤 잔존» 으로 바꿨다.
  - 편집 전에 현행 ttl 의 rdflib 왕복이 byte 동일함을 확인했다 [실측].
  - 게이트 90/90 green → `--apply command-dddjango`(변경 1줄) → LEDGER 1행 → 계수 +1 → `make rulepack` 순서로 진행했다. q4 골든은 verify-ontology 가 green 이라 `--emit` 하지 않았다.
- web(산문 정본) :308 과 Codex :333 에는 같은 취지 문장을 web 표현(«재개봉·STOP 판단 전에» · «슬라이스 0 재개봉·새 시각이 아니다»)으로 넣었다.

## 3. 설계·§7 대비 이탈과 이유

1. **기준 커밋 앞당김**: 워크트리는 `acbfffda`(main 의 20 커밋 전)에서 시작했다. 설계 기준 `144e25e9` 로 fast-forward 했다(포인터만 이동).
2. **`_ground` 모양**: 설계 §2.1 의 `zip`·`next` 대신 첫 불량 토큰에서 바로 돌아가는 반복문으로 썼다. 의미는 같다.
   - m2(절대·`..`)도 `_ground` 안에서 판정한다. 두 도구가 같은 함수를 byte 동일하게 쓰게 하려는 것이다.
3. **«답 없음» 내부 상태**: §7 M1 의 «답 행 부재인 M 만 재판정»과 M3 렌즈 완전성을 한 장치로 구현했다.
   - `states` 에는 `답 없음` 으로 기록하고, 출력(result.md·요약)에는 `판단 불가` 로 셈한다.
   - 리뷰어가 명시한 `판단 불가` 는 동결 대상이다(재판정하지 않는다).
4. **집계 순서**: 설계의 «해소 → 잔존 → 판형 아님 → 판단 불가» 에 답 없음을 판형 아님 뒤에 넣었다. 판형 아님은 재기재로 풀 수 있는 쪽이라 먼저 안내한다.
5. **요약 계수**: `근거 판형 아님 c` 를 0 일 때도 항상 낸다. 설계 §2.1 형식 그대로다. 기존 «리뷰어 잔존 1» 같은 부분 문자열 단언은 그대로 맞는다.
6. **리뷰어 잔존 행 이름**: 기존 `잔존(리뷰어 · 근거 없는 해소 포함)` 을 유지했다. «근거 없는 해소»는 이제 머리 위치가 허용 밖인 해소를 뜻한다. 반복은 `잔존(근거 판형 아님 반복)` 이다.
7. **E2 라벨 비교**: 리뷰 권고는 `kind.startswith("병합")` 이었다. 구현은 `kind in ("병합→M", "병합→C")` 로 정확히 비교한다. exit 0 판에는 `병합(대상 없음)` 이 남지 않는다(`--final` 이 채택으로 바꾼다) [추정]. 그래도 정확 비교가 fail-open 여지를 없앤다.
8. **산출물 루트 방어**
   - `folder` 가 프로젝트 바로 아래(부모가 프로젝트 루트)면 루트 대신 `folder` 자체를 뺀다.
   - `folder` 가 프로젝트 밖이면 빼지 않는다. 그 경로는 바뀐 파일 목록에 들어올 수 없다.
9. **web 문면의 `build_anchor` 치환**: §7 최소안 문장에는 앵커 표현이 없어 치환할 것이 없었다. 대신 반송을 web 용어 «재개봉»으로 바꿔 적었다.
10. **변이 V5 분할**
    - V5a 는 동결을 제거한다. «잔존 뒤집기»와 «N6 3차»가 red 가 된다.
    - V5b 는 반복 → 잔존을 제거한다. «N6 2차»가 red 가 된다.
11. **시험 보강**
    - 설계 목록 밖에 양성 짝을 더했다.
      - core: N6b «판형 아님 → 같은 시각 판형대로 고침 → 해소» · `**`해소`**` 벗김 → 해소 · «같은 시각 해소 항목 지문 유지» · 렌즈 답을 채운 재확정 → 해소
      - web: I3‴ · I3n(N3 짝) · I3o(N7 짝) · I3p(N4 짝)
    - 이 짝은 V3·V6·V7 의 web 변이 검출용이다.
    - web 에도 산출물 폴더(I3h) · 절대 경로(I3i) · 대시 변형(I3j) · 정확 일치(I3k) · 렌즈 완전성(I3l)을 넣었다.
12. **web 시각 파싱**: `STAMP=$(ls … | sort | tail -1)` 을 출력의 `--finalize <시각>` 파싱으로 바꿨다. 같은 분 안에서 `-10` 이상이 되면 사전식 정렬이 틀린다. 이번 재구성으로 같은 분에 시각을 20개 가까이 연다.

## 4. 사례 결과 [실측]

### 4.1 core — `python3 workspace/tools/refactor_audit_fixture_run.py` → PASS · ✓ 180(기존 143)

- 기존 단언 수정은 `residual_cases` :382-392 한 묶음이다.
  - «`고쳤다`» 행: «리뷰어 잔존 1» 에서 «리뷰어 잔존 0 · 근거 판형 아님 1» 과 재기재 안내로 바뀌었다. 설계 §4.1 대로다.
  - T_LOC 행과 C_LOC 행은 사례마다 새 시각을 연다(`_fresh_stamp(clear=True)`). 동결 뒤에는 같은 시각에서 잔존을 해소로 뒤집을 수 없기 때문이다(§7 M1). 이렇게 해도 마지막 시각이 M2 해소로 끝나 :407 «해소 유지 1» 전제는 그대로다.
- 새 `residual_ground_cases`(✓ 26)
  - O2 · G1 · O1 · N6b
  - G2 · G3 · G4
  - N1 · N2 · N3 · N4a · N4b · N5
  - 대시 변형 · m2 절대 · m2 `..` · M2 산출물 폴더
  - m1 «해소 안 됨» · m1 강조 벗김 · N7
  - N6 2차(잔존 반복) · N6 3차(동결) · 잔존 뒤집기(동결) · 해소 지문 유지
  - M3 렌즈 완전성(판단 불가) · 같은 시각 채움 → 해소
- 새 `e2_cases`(✓ 11)
  - E2-0 로그 없음 → 차감 없음(«M4 판정 없음»)
  - 준비: check-verdict exit 0
  - E2-1 · E2-2 · E2-3 · E2-4 · E2-5
  - 준비: 사슬 병합 red → `--final` 이 M4 를 채택으로 재분류
  - E2-6
  - E2-7 residual «결정적 잔존 2» · E2-7 resolution «M4 판정 없음»
- 같은 사례를 **HEAD 도구**로 돌리면 새 사례 가운데 30건이 red 다.
  - HEAD 에서도 green 인 것: N3 · E2-0 · E2-4 · E2-7×2 · 렌즈 채움 → 해소. 이들은 설계안(verdict.md 출처·괄호 벗기기)의 fail-open 을 막는 가드다.

### 4.2 web — `bash dddjango-web/scripts/test/fixtures_refactor_audit.sh` → PASS=137 FAIL=0(기존 115)

- 기존 단언 수정: I3 은 «M_m=1(결정적 잔존 0 · 리뷰어 잔존 1» 에서 «…리뷰어 잔존 0 · 근거 판형 아님 1 · 판단 불가 0)» 으로 바뀌었다.
- 새 단언: I2b·I2c(묶음 머리) · I3′·I3″(재기재 안내) · I3‴ · I3a~I3p(I3g′ 포함).
- 마지막 시각은 I3m(M9 해소)으로 끝난다. I4 «해소 유지 1 · M10 없음» 전제는 유지된다.
- I3l 은 `verdict-final.md` 의 M10 원 행에 `discipline-01#1` 을 더하고 `discipline-01.md` 에 행을 쓴다. 끝나면 두 파일 모두 백업본으로 되돌린다.
- HEAD web 도구로 돌리면 FAIL 20 이다.
  - I3j(en dash) 는 HEAD 에서 **exit 0 해소**로 새어 나갔다(`–`·낱말을 버리고 앞 위치만 읽었다). 새 도구에서는 판형 아님이다.

## 5. 변이 결과 [실측]

- 방식
  - core 는 작업 트리 `dddjango/scripts/_mut_ra.py` 에 변이 사본을 두고 러너의 `run()` 기본 tool 을 바꿔 `residual_cases`·`residual_ground_cases`·`e2_cases` 를 돌렸다. 끝나면 사본을 지웠다.
  - web 은 scratch `webmut/scripts` 전체 사본의 도구를 바꿔 픽스처를 돌렸다.
  - 도구: scratch `r8c_mutate_core.py`·`r8c_mutate_web.py`·`r8c_run_with_tool.py`. 저장소에는 남기지 않았다.

| 변이 | core (red 난 사례) | web (red 난 사례) |
|---|---|---|
| V1 머리·꼬리 분리 제거(칸 전체 관용) | CAUGHT — N1(해소로 새어 나감)·G3 포함 red 11 | CAUGHT — I3e·I3c 포함 red 7 |
| V2 머리 관용(비위치 낱말 버림) | CAUGHT — N5 포함 red 5 | CAUGHT — I3a·I3 포함 red 5 |
| V3 머리 all→any | CAUGHT — N3 | CAUGHT — I3n |
| V4 판형 아님을 M_m 에서 뺌 | CAUGHT — G1·기존 «고쳤다»(red 2) | CAUGHT — I3·I3a 포함 red 8 |
| V5a 동결 제거 | CAUGHT — 잔존 뒤집기·N6 3차 | CAUGHT — I3g′·I3m |
| V5b 반복 → 잔존 제거 | CAUGHT — N6 2차 | CAUGHT — I3g |
| V6 집계 순서(판형 아님 먼저) | CAUGHT — N7 | CAUGHT — I3o |
| V7 실재 실패를 판형 아님에서 뺌 | CAUGHT — N4a·N4b | CAUGHT — I3p |
| V8 병합 차감 제거 | CAUGHT — E2-1·E2-2·E2-5·E2-6 포함 red 5 | 해당 없음(web E2 없음) |
| V9 차감 대신 괄호 벗기기 | CAUGHT — E2-2·E2-4 포함 red 3 | 해당 없음 |
| V10 병합 출처를 verdict.md 로 | CAUGHT — E2-7×2·E2-0 | 해당 없음 |
| X1 산출물 루트 제외 제거(M2) | CAUGHT — M2 산출물 폴더 | CAUGHT — I3h |
| X2 렌즈 완전성 제거(M3) | CAUGHT — M3 렌즈 완전성 | CAUGHT — I3l |
| X3 판정 칸 접두어 판독(m1) | CAUGHT — m1 «해소 안 됨» | CAUGHT — I3k |
| X4 절대·`..` 경로 허용(m2) | CAUGHT — m2 절대·`..` | CAUGHT — I3i |
| X5 `_repo_path` 없이 판정 | — | CAUGHT — I3d |

- core 는 15/15, web 은 13/13 이다. web BASE(무변이) 사본은 PASS=137 이다.
- 변이 도중 한 번 발견한 점이 있다. V2 가 기존 residual 사례에서 M2 를 해소시키자, 다음 시각이 M2 를 이월해 묶음이 안 열렸다. 그러자 러너가 red 가 아니라 예외로 끝났다.
- 그래서 `_fresh_stamp` 가 안 열린 시각 폴더도 만들고(뒤 단언이 red 로 드러난다), residual 사례가 앞 시각을 지우고 열게 고쳤다. 그 뒤 15/15 다.

## 6. verify [실측]

- `make verify`(병렬 5묶음 · 로그 scratch `r8c-verify-1.log` · 원 로그 `/tmp/djr-verify.H1dCWg`)
  - verify-ontology · verify-base-backstop · verify-base-cross · verify-base-regen 은 green 이다. regen 에는 refactor-audit 픽스처가 들어 있다.
  - **verify-base-core RED**: `manifest_seal.py --check --draft` 가 지적 14건을 냈다. 전부 봉인 대상 파일 변경 탓이다.
    - pipeline: `codex-dddjango/skills/dddjango/SKILL.md`·`dddjango/commands/dddjango.md`·`dddjango/scripts/refactor_audit.py` 봉인 후 변경 + tree 드리프트
    - plugin_payload: Codex SKILL + tree
    - packs: `rulepack.json` + tree
    - graph: `LEDGER.tsv`·`command-dddjango.ttl` + tree
    - `script_trees[source-claude/codex]` `ee6e9a19…` → `8ba60e4d…`
    - initial_state(그래프·LEDGER)
  - 드리프트만인지 확인했다. `manifest_seal.py --emit` 으로 뽑은 실측 manifest 에 `--check --draft --manifest <그 파일>` 을 대면 green 이다(그룹 10 · 봉인 파일 266).
  - RED 로 멈춘 뒤 base-core 의 나머지 단계를 따로 돌렸다.
    - `manifest_seal --self-test`: 변이 M1~M8 은 전부 red 를 탐지했다. M0 무변이 대조만 «위양성»이다. 같은 드리프트 탓이며 봉인 재발행 뒤 green 이 될 것이다 [추정].
    - `ab_score --self-test`: 5/5
    - `diff -rq dddjango/scripts ↔ codex`: 무차이
    - REQUEST_GUIDE cmp: 같음
    - `request_guide_contract --self-test`: 157/157
    - 계약: PASS
  - `manifest_seal.py --write` 는 하지 않았다(지시 — 커밋 단계에서 운영 세션이 한다).
- `make verify-web`(로그 scratch `r8c-verify-web-1.log`)은 **green** 이다.
  - fixtures_refactor_audit 137/0을 포함해 각 픽스처 FAIL 0 이다.
  - self-test claude·codex 는 red 0 이다.
  - 상시 답 블록 core 대조, 문단(`**Phase 1~2**`·`**상시 답**`) 대조, codex byte 미러 대조, REQUEST_GUIDE, 요청 가이드 계약이 모두 통과했다.
- `claude plugin validate dddjango --strict` 는 돌리지 않았다(매니페스트 무변 · 지시).

## 7. 남은 한계 · 후속

1. **이식 순서**(DEVELOPMENT §4·§6)
   - 이 diff 를 커밋한다.
   - 그 뒤 별도 chore 커밋으로 `manifest_seal.py --write` 봉인을 재발행한다. 이어서 `make verify` 를 다시 돌린다.
   - `dddjango/scripts/` 가 바뀌었으므로 진행 중인 G1~G2 레인이 착륙한 뒤 릴리즈한다(pre-gate digest stale).
2. **리뷰어 문면 무변(§7 M4)**
   - 리뷰어 md 에는 여전히 «해소의 근거는 새 `파일:행` 이다(근거 없는 해소는 잔존으로 처리된다)»만 있다.
   - 판형은 묶음 머리 한 곳으로만 전달된다. 첫 residual 에서 판형 준수율은 관찰 대상이다(설계 §5.1 · 구 지시 33행 중 28행이 판형 아님 — n1).
3. **동결 범위**: 같은 시각에만 걸린다. 새 시각을 열면 모든 행을 새로 판정한다. 절차 문면(«새 시각 아님»)이 이를 막는다.
4. **꼬리 비판독**: 머리 위치가 항목과 무관한 바뀐 파일이어도 통과한다. 이 점은 현행과 같다(설계 §5.2 · E3 범위).
5. **n2(범위 밖)**: core `_origins` 는 여전히 verdict.md 를 읽는다.
   - 그래서 `--final` 로 새 번호를 받은 M 이 ⓐ 면 residual 이 «ⓐ 항목 … verdict.md 에 없다»로 실행 불능이 된다(fail-closed).
   - `--final` 이 병합을 채택으로 바꾼 M(E2-7 모양)은 verdict.md 상 병합 대상 쪽 묶음에도 원 행이 실린다. 이중 확인이 되고 fail-closed 다.
   - web 은 `verdict-final.md` 를 읽는다. 후속 후보로 둔다.
6. **resolution «막는 것» 파서**: 여전히 `_locations` 의 관용 판독이다(설계 §5.7). residual 의 엄격한 머리 판독과 통일하는 것은 후속이다.
7. **web 의 병합 명시 키**: `의미 ⓐ 키:` 에 병합 키를 적는 가상 경우는 막지 않는다. 관찰된 적이 없다(설계 §5.5).

## 9. 구현 리뷰 처분 (2026-09-30 · 운영 세션 결정 — 전건 수용)

입력: 독립 구현 리뷰 `scratchpad/review-R8c-impl/review-R8c-impl.md`(수정 후 승인 · blocker 0 · major 1 · minor 3 · nit 5)와 재현 스크립트(`exp_core.py` · `exp_web.sh` · `mut_run.py`). 같은 워크트리에서 이어서 작업했다. 커밋 0 · push 0 이다.

### 9.1 처분별 결과

| 처분 | 코드(core·web 같은 모양) | 시험 | 변이 |
|---|---|---|---|
| **MJ1** 동결은 좋아지는 쪽만 막는다 | 같은 시각의 앞 판이 `해소`·`판단 불가` 인데 이번 행에 `잔존`(접두어)이 있으면 `잔존` 으로 내린다. 그 밖(행 없음 포함)은 앞 판 판정과 해소 지문을 유지한다. `잔존`·`잔존(반복)` 은 그대로 둔다. `판형 아님`·`답 없음` 은 종전대로 다시 판정한다 | core: 1차 구현의 :515 기대를 뒤집음(«해소 → 잔존으로 고쳐 씀 → 잔존») · 짝 «행 없음 → 해소 유지» / web: I3r · I3s | Y1(강등 제거) · Y2(해소 동결 해제) — core·web 모두 red |
| **mi1** E2 차감 조건 | 차감 = verdict.md 의 `병합` 행 가운데 (로그 마지막 exit 0 판이 `병합→M`/`병합→C`) ∧ (대상 `M` 이면 대상이 ⓐ 키 · 대상 `C` 면 ⓐ 결정 줄의 `\bC\d+\b` 에 있음). 로그가 없으면 빼지 않는다(verdict.md 도 읽지 않는다) | x3(드리프트) · x4(고아 병합 M) · x5(고아 병합 C) 모두 HEAD 와 같은 잔존으로 돌아온다 · x5 짝(결정 줄에 C1 → 뺌) | Y3a(교집합·대상 조건 제거 = 1차 구현) → x3·x4·x5 red · Y3b(대상 조건만 제거) → x4·x5 red |
| **mi2** 반복 상한 우회 | `result.json` 에 `"redo": [M…]`(판형 아님 이력)을 `states` 와 따로 누적한다. 이력 있는 M 이 다시 판형 아님이면 `잔존(반복)` 이다 | x2 순서: 판형 아님 → 행 삭제(답 없음) → 판형 아님 → 잔존(반복) → 판형대로 고쳐도 잔존 유지 / web I3t | Y4(redo 대신 앞 판 판정) red |
| **mi3** 해소 지문 유지 시험 | 코드 변경 없음(`kept` 는 `_same_stamp` 가 돌려준다) | 같은 시각 1차 해소 → 파일 편집 → 2차 재확정 → 새 시각이 이월 없이 다시 묶는다(core · web I3w — web 은 편집을 되돌려 K1 전제를 지킨다) | Y5(kept 제거) red |
| **n1** 산출물 루트 둘 다 | `OUTPUT_ROOTS = (".dddjango/", ".dddjango-web/")`(모듈 상수 · 프로젝트 상대 접두 비교). §3.8 의 `folder` 부모 계산을 대체한다 | core: `.dddjango-web/…` 머리 → 잔존 · web I3u: `.dddjango/…` 머리 → 잔존 | Y6c · Y6w red |
| **n2** result.json 모양 | `_same_stamp(path)` — dict 가 아니거나, states 가 str→str 가 아니거나, redo 가 str 목록이 아니거나, solved 가 dict 의 dict 가 아니면 ToolError(«실행 불능» exit 1). 손상 JSON 은 종전대로 ValueError → 실행 불능 | core n2 · web I3v(`states` 가 list) | Y7(검사 제거 → 트레이스백) red |
| **n3** 문면 모순 | R-3535 rev3 **같은 Expression 안에서**(새 rev 없음 · ExpressionShape 3811 유지) 블록 s012/b12 의 «(새 `파일:행` 근거 없는 해소는 잔존 · …)» 를 «(머리 위치가 바뀐 파일·감시 경로 밖인 해소는 잔존 · …)» 로 바꿨다. 이어서 재투영 · Codex :269(core md :253 과 diff 0) · web :308 · web Codex :333 에 «(머리 위치가 바뀐 파일·감시 경로 밖인 해소는 잔존이다)» 를 넣었다 · rulepack 재소성 | 5곳 모두 «근거 없는 해소는 잔존» 0건 [실측 grep] · verify-ontology green | — |
| **n4** 판정 칸 비대칭 판독 | `_answer_state(cell)`: `*`·백틱을 벗긴 뒤 `해소`·`판단 불가` 는 정확히, `잔존` 은 접두어(`잔존(일부)`), 그 밖은 판단 불가 | x9: ddd «잔존(일부)» + discipline 판형 아님 → 잔존 · 같은 시각 2차에 두 렌즈 해소로 고쳐도 잔존 / web I3q·I3q′ | Y8(정확 일치로 되돌림) red · X3(해소 접두어) red |
| **n5** 튜플 · 빈 시각 가드 | `unformatted: dict[M, list[(렌즈, 토큰)]]`. result.md·안내 행은 튜플에서 만든다 | web `OPEN` 이 비면 `(열리지 않음)` 을 내고 `FIN` 이 exit 9 로 red. core `_fresh_stamp` 는 열리지 않으면 residual **밖** 자리표시를 돌려준다(뒤 `--finalize` 가 실행 불능 exit 1 로 red — residual 안에 폴더를 만들어 우연히 통과하던 여지를 없앰) | — |

- **LEDGER 판단(n3)**: 기존 행을 교체하지 않고 새 행을 append 했다(`ede6b5ba…` · 사유 «구현 리뷰 n3»). 근거는 LEDGER 관례다 [실측].
  - 같은 doc·section·날짜에 여러 행이 있는 경우가 35건이다.
  - 같은 doc·section·사유 문구가 겹치는 행은 0건이다.
  - 079b8c49 는 한 커밋에서 s012 를 같은 날 3행 append 했다.
  - 따라서 «같은 날 다른 사유 = append» 가 관례이고, «교체» 선례는 없다. 1차 행(`d8f15609…`)은 이력으로 남는다(마지막 행이 유효 기준선).
- **§2.2 대체 문장**: 판정 칸 판독은 «정확 일치 셋» 에서 «해소·판단 불가 정확 · 잔존 접두어» 로 바뀌었다. 동결 목록은 «판형 아님·답 없음이 아닌 M 은 앞 판 그대로» 에서 MJ1 규칙으로 바뀌었다. `result.json` 은 `{"stamp", "solved", "states", "redo"}`(web 은 + `"audit"`·`"snapshot"`)이다.
- 공유 도우미 `_ground`·`_answer_state`·`_same_stamp` 는 core·web byte 동일이다 [실측 diff]. 상시 답 블록 cmp 도 동일하다.

### 9.2 사례 [실측]

- **core** `refactor_audit_fixture_run.py`: **PASS · ✓ 192**(1차 구현 180).
  - :515 한 건을 뒤집었고, 새 단언은 13건이다: MJ1 2 · mi3 1 · mi2 2 · n1 1 · n2 1 · n4 2 · mi1 4.
  - HEAD 도구로 돌리면 새 사례 포함 red 가 38건이다.
  - HEAD 에서도 green 인 새 사례는 x3·x4·x5(HEAD 동작 회귀 단언)와 MJ1 강등(HEAD 는 동결이 없다)이다.
- **web** `fixtures_refactor_audit.sh`: **PASS=145 FAIL=0**(1차 구현 137).
  - 새 단언: I3r·I3s·I3t·I3u·I3v·I3w·I3q·I3q′.

### 9.3 변이 [실측] — 목록은 scratch `r8c_mutants.py` 하나를 core·web 러너가 함께 쓴다

- **core 24/24 CAUGHT**
  - V1~V10(V5a·V5b) · X1~X4 · Y1 · Y2 · Y3a · Y3b · Y4 · Y5 · Y6c · Y7 · Y8
  - 로그: scratch `r8c-mut-core-2.log`
  - 끝난 뒤 `_mut_ra.py` 는 지웠다.
- **web 20/20 CAUGHT**(무변이 BASE 145/0)
  - V1 · V2 · V3w · V4 · V5a · V5b · V6 · V7w · X1~X5 · Y1 · Y2 · Y4 · Y5 · Y6w · Y7 · Y8
  - 로그: `r8c-mut-web-2.log`
  - V8~V10 · Y3 은 web 에 E2 가 없어 해당 없음이다.

### 9.4 verify [실측]

- **`make verify`**(scratch `r8c-verify-2.log` · 원 로그 `/tmp/djr-verify.LYXGVW`)
  - ontology · base-backstop · base-cross · base-regen 은 green 이다.
  - **base-core 는 봉인 드리프트 14건으로만 RED** 다. 대상 파일은 1차와 같은 목록이고, script_trees 는 `ee6e9a19…` → `ca003aa3…` 이다.
  - `--emit` 실측 manifest 로 `--check --draft --manifest` 를 돌리면 green 이다(그룹 10 · 봉인 파일 266).
  - base-core 의 나머지 단계를 따로 돌린 결과
    - `manifest_seal --self-test`: M1~M8 이 red 를 탐지했다. M0 은 «위양성» 이다. M0 은 코드상 정본 manifest 에 대한 `--check --draft` 그 자체이므로 같은 드리프트다 [실측 — 코드 :1256-1263 확인].
    - ab_score: 5/5
    - scripts Codex 미러: 무차이
    - REQUEST_GUIDE: cmp 같음
    - 요청 가이드 self-test: 157/157
    - 계약: PASS
  - `--write` 는 하지 않았다.
- **`make verify-web`**(`r8c-verify-web-2.log`) **green**
  - refactor_audit 145/0 과 각 픽스처 FAIL 0 이다.
  - self-test claude·codex 는 red 0 이다.
  - 상시 답 블록 core 대조 · 문단 대조 · codex byte 미러 · REQUEST_GUIDE · 계약이 통과했다.

### 9.5 diff (144e25e9 기준 · 16 files · +915/−161)

| 파일 | +/− |
|---|---|
| `dddjango/scripts/refactor_audit.py` · Codex | +113/−32 씩 |
| `dddjango-web/scripts/refactor_audit.py` · Codex | +105/−33 씩 |
| `workspace/tools/refactor_audit_fixture_run.py` | +277/−7 |
| `dddjango-web/scripts/test/fixtures_refactor_audit.sh` · Codex | +89/−4 씩 |
| `ontology/rules/command-dddjango.ttl` | +9/−3 |
| `ontology/LEDGER.tsv` | +2 |
| `rulepack.json` ×2 | +4/−4 씩 |
| Coordinator md 4곳(core 재투영 · Codex · web · web Codex) | +1/−1 씩 |
| `target-counts.json` | +1/−1 |

### 9.6 남은 한계(§7 에 더함)

- ~~MJ1 강등은 `잔존` 행만 본다~~ → §9.7 에서 닫았다(강등 일반화).
- E2 의 대상 `C` 조건은 ~~ⓐ 결정 줄 원문(괄호 포함)의 `C<n>` 을 본다~~ → §9.8 mi-B 에서 괄호를 벗기고 읽는다. 재상정으로 그 `C<n>` 을 뺀 경우는 따지지 않는다. `M` 대상도 재상정 전 ⓐ 키로 판정한다. 그래야 E2-6(대상이 재상정으로 빠지면 병합 항목도 함께 빠짐)이 유지된다.

### 9.7 강등 일반화 (운영 세션 결정 — §9.6 첫 한계를 닫는다)

- **규칙**(core·web 같은 모양 · `cmd_residual` 판정 반복문)
  - 같은 시각 앞 판이 `판형 아님`·`답 없음` 이면 종전대로 다시 판정한다(redo 이력 규칙 그대로).
  - 그 밖에 이번에 그 M 의 행이 **없으면** 앞 판 판정과 지문을 유지한다.
  - 행이 **있으면** 이번 판정 `now` 를 쓴다(판형 아님 + redo 이력이면 잔존(반복)).
  - 단, 앞 판이 `잔존`·`잔존(반복)`·`판단 불가` 이고 `now` 가 그 셋 밖(`해소`·`판형 아님`·`답 없음`)이면 앞 판을 유지한다.
  - 따라서 앞 판 해소의 강등(잔존·판단 불가·판형 아님·답 없음)은 모두 받는다. 판형 아님으로 강등되면 redo 이력에 들어간다.
- **운영 지시 대비 이탈 1건**: 지시 문면은 «이번 판정이 해소이고 앞 판이 해소가 아니면 유지»다. 구현은 판형 아님·답 없음으로 가는 것도 막는다.
  - 이유: 문면대로면 잔존 → (판형 아님 행) → 판형 아님 → (다음 재확정에서 다시 판정) → 해소 로 두 번에 좋아지는 우회가 열린다.
  - 이는 «좋아지는 쪽만 막는다» 원칙의 우회다.
  - 변이 Y9(문면 그대로 = 해소만 막음)는 «앞 판 잔존 → 판형 아님 → 잔존 유지» 사례를 red 로 만든다.
- **사례** [실측]: core ✓ 196, web PASS=149 FAIL=0 이다. 새 사례 넷(core 4 · web I3x·I3y·I3z·I3z′):
  - 앞 판 해소 → 이번 판단 불가 → 판단 불가(exit 2)
  - 앞 판 해소 → 이번 판형 아님 행 → 판형 아님(exit 2 · 재기재 안내)
  - 앞 판 판단 불가 → 이번 해소 → 판단 불가 유지
  - 앞 판 잔존 → 이번 판형 아님 행 → 잔존 유지
  - 기존 MJ1·mi2·mi3·n4·N6·잔존 뒤집기 사례는 그대로 green 이다.
- **변이** [실측]: core **26/26**, web **22/22** CAUGHT 이다. web 무변이 기준은 149/0 이다.
  - Y1 «강등을 잔존 행만»(§9 1차 규칙): 앞 두 사례가 red(core 2 · web I3x·I3y)
  - Y1b «강등 전부 제거»: MJ1 잔존 강등까지 red
  - Y9 «판형 아님 경유 허용»: 잔존 유지 사례가 red
  - V5a(좋아지는 쪽 막기 제거): 이제 «판단 불가 → 해소 유지» 사례도 잡는다
  - Y2(행 없음 유지 제거)·V5b·Y4: 패턴 위치만 옮겼다
- **verify** [실측 · 전체 재실행 · scratch `r8c-verify-3.log` · `/tmp/djr-verify.s7oZya`]
  - ontology·backstop·cross·regen 은 green 이다.
  - base-core 는 봉인 드리프트 14건으로만 RED 다. 대상은 §9.4 와 같고 script_trees 만 `193f781a…` 로 바뀌었다.
  - `--emit` 으로 뽑은 실측 manifest 로 대조하면 green 이다.
  - base-core 나머지 단계: ab_score 5/5 · 미러 무차이 · 요청 가이드 157/157 · 계약 PASS.
  - `make verify-web` 은 green 이다(refactor_audit 149/0). byte 미러는 다시 복사했고 무차이다.
- 이번 절에서 바뀐 것은 도구 2개와 그 Codex 미러, 픽스처 2개와 web 픽스처의 Codex 미러뿐이다. 문면·ttl·LEDGER·rulepack 은 그대로다.

### 9.8 재검토 처분 (재검토 «승인» · minor 2 · nit 3 — 운영 세션 결정 · 커밋 전 반영)

| 처분 | 바뀐 곳 | 시험 | 변이 |
|---|---|---|---|
| **mi-A** «답 없음» 경유 이탈 | 코드 변경 없음(§9.7 `held` 가 이미 막는다) | core: M3(ddd+discipline). 1차 ddd 잔존·discipline 해소 → 잔존. 2차 ddd 행 삭제 → 잔존 유지. 3차 두 렌즈 해소 → 잔존 유지. web: I3q″·I3q‴(I3l 두 렌즈 준비 재사용) | Z2(`held` 에 답 없음 허용) → core «mi-A 3차» · web I3q‴ red |
| **mi-B** 괄호 안 C | core `_scope`: `adopted_c \|= set(re.findall(r"\bC\d+\b", re.sub(r"\([^)]*\)", "", dm.group(1))))` — C 키만 괄호를 벗겨 읽는다(fail-open 방향을 닫음) | core: `M4 병합→C1`(로그 확정) · `- M1, M4(C1 은 ⓑ 로 미룸) · 결정 = ⓐ` · M4 무변 → 결정적 잔존 1(HEAD 와 같음) | Z4(벗기기 제거) red |
| **n-A** 문면 용어 | 괄호 안 «머리 위치가 …» 를 «` — ` 앞 위치가 바뀐 파일·감시 경로 밖인 해소는 잔존» 으로 바꿨다(prefLabel 과 같은 말). R-3535 rev3 같은 Expression 안에서(새 rev 없음) ttl → 게이트 90/90 → 재투영 → LEDGER append(`fb660fe9…` · 사유 «재검토 n-A» · §9.1 의 append 관례 근거 그대로) → rulepack → Codex :269 · web :308 · web Codex :333 손 미러 | 5곳 모두 새 문구 1건, 옛 «머리 위치가» 0건 [실측 grep] · core md :253 ↔ Codex :269 diff 0 | — |
| **n-C** `_same_stamp` | 항목별 타입 검사를 `try: … except (TypeError, AttributeError, ValueError): raise ToolError(…) from None` 로 줄였다. 문자열 아닌 값의 `.strip`, dict 아닌 값의 `.items`, 목록 아닌 redo 의 `+ []` 가 실패한다. 손상 JSON 도 같은 ToolError 다. core·web byte 동일(`_ground`~`_same_stamp` diff 0) | n2 · web I3v 그대로 green | Y7 을 `except ZeroDivisionError` 로 바꿨다(검사 제거 → 트레이스백) → red |
| **n-B** | 기록만(운영 세션 결정 · 코드·시험 변경 없음). 내용(운영 세션 보충 · 재검토 원문): 앞 판이 해소인 여러 렌즈 항목에서 한 렌즈 행만 빠지면 답 없음으로 강등되고, 행이 전부 빠지면 해소가 유지된다 — 둘 다 fail-closed 거나 설계 의도라 무해(코드 판독) | — | — |

- **사례** [실측]
  - core `refactor_audit_fixture_run.py`: **PASS · ✓ 199**(§9.7 196 + mi-A 2 + mi-B 1)
  - web: **PASS=151 FAIL=0**(§9.7 149 + I3q″·I3q‴)
- **변이** [실측]
  - core **28/28** CAUGHT(Z2 · Z4 포함)
  - web **23/23** CAUGHT(Z2 포함 · 무변이 BASE 151/0)
  - `_mut_ra.py` 는 지웠다.
- **byte 미러**: 다시 복사했고 `diff -rq` 무차이다.
- **verify** [실측]
  - `make verify`(전체 재실행 · scratch `r8c-verify-4.log`): ontology·backstop·cross·regen 은 green 이다.
  - base-core 는 봉인 드리프트 14건으로만 RED 다. 봉인 후 변경·tree·script_trees `5bd5a45a…`·initial_state 가 전부이고, 그 밖 ✗ 는 0 이다.
  - `--emit` 으로 뽑은 실측 manifest 대조는 green 이다.
  - base-core 나머지 단계: ab_score 5/5 · 미러 무차이 · 요청 가이드 157/157 · PASS.
  - `make verify-web` 은 green 이다(refactor_audit 151/0).
- **§9.6 둘째 한계 갱신**: E2 의 대상 C 조건은 이제 괄호를 벗긴 ⓐ 줄 C 키를 본다. «재상정으로 뺀 C 는 따지지 않음»은 그대로다.
