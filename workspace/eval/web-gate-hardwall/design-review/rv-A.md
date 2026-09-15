# 적대 검토 A — «이 설계는 게이트를 고무도장으로 만든다» (2026-09-15)

대상: `workspace/design/2026-09-15-web-gate-hardwall.md` v1
입장: 하드월 제거 자체에는 반대하지 않는다. 검토하는 것은 **그 자리에 놓인 장치가 통과 의식이 되는가**다.
표기: **[확인]** = 코드·실물 파일로 실측 · **[추론]** = 코드 읽기에서 따라 나오는 결론 · **[미확인]** = 실행해 봐야 알 수 있음.

등급: BLOCKER 3 · MAJOR 5 · MINOR 4

---

### [BLOCKER] 지위 강등에 천장이 없다 — «미검증 100%»도 exit 0이다

**악용 경로**
1. 잔여 단위가 N건 남는다(무슨 이유로든).
2. `interaction_exclusions`에 N행을 기계적으로 생성한다 — 행마다 `approval_quote`는 **같은 문자열 하나**를 재사용한다(행별 유일성 요구가 없다 — 확인).
3. `design-input.json`에 `evidence_scope: {"level":"partial","unverified":N,"active":M,...}`을 적는다. `unverified`·`active`는 검사기가 센 값과 «일치»하기만 하면 된다.
4. `--phase inputs` exit 0. `design_status=ready`. Phase 1 진입.

N에 상한이 없다. `unverified == active`(= 관찰된 활성 대상 전부 미검증)여도 설계 §1의 세 요구를 모두 만족한다.
즉 설계가 «상한을 차단에서 지위 강등으로 바꾼다»(§0)고 말하지만, **결과는 상한 제거**다 —
어떤 비율에서도 exit 0이고, 비율에 따라 달라지는 것은 라벨 문자열 하나뿐이다.

**근거**
- `dddjango-web/scripts/check_design_evidence.py:895-897` — 현재 유일한 상한. 설계는 이 3줄을 비차단으로 바꾸고 **대체 상한을 두지 않는다**(설계 §1·§3 «상한 수치 조정 — 하지 않는다»).
- `:849-897` `_check_exclusions` — 행별 검증은 `approval_quote` 길이·부분문자열·`scope_ref` 앵커 존재뿐. **행 간 유일성·행 수 대비 타당성 검사 없음** [확인].
- 설계 §1.2가 요구하는 것은 «수치 일치»이지 «수치 한계»가 아니다 [확인, 설계 원문].

**추가로 위험한 미명세**: §1.1 예시가 `{"unverified":153,"active":190}`인데, 153행의 예외가 별도로 존재한다면
`unverified`는 그 행들에서 유도되는 **중복 값**이다. 예시가 요약처럼 읽히는 것은 구현자가
«`evidence_scope` 한 블록이 잔여를 일괄로 닫는다»로 읽을 여지를 남긴다. 그렇게 구현되면
문을 여는 비용이 **JSON 6줄**이 된다. 설계가 이 갈림을 명시하지 않은 것 자체가 결함이다 [확인, 설계 원문에 없음].

**막는 방법**
1. **§1에 «일괄 닫힘 없음»을 명문화한다** — `evidence_scope`는 잔여를 닫지 않는다. 잔여를 닫는 것은 오직 단위/표면 행이며 `evidence_scope`는 그 행들의 **상한만** 해제한다.
2. **천장을 다시 세우되 차단이 아닌 곳에 세운다**: `unverified / active > 0.5`(수치는 협의)면 exit 0이지만 **`level: "unverified"`라는 세 번째 등급**으로 내리고, 그 등급은 G2 배너에서 «이 빌드의 시안 대조는 기계 근거가 없다»를 의무 줄로 낸다. 즉 «부분»과 «사실상 전무»를 같은 라벨로 덮지 않는다.
3. `approval_quote`의 **행별 유일성**을 요구한다(같은 원문으로 N행을 열 수 없게). 최소한 `evidence_scope.approval_quote`는 모든 행의 quote와 달라야 한다.

---

### [BLOCKER] 가장 싼 길 = 드라이버를 안 잇는 것 — 증거 부채 래칫까지 같이 죽는다

**악용 경로**(게으른 에이전트가 실제로 도달하는 상태)
1. Coordinator는 드라이버를 `--max-minutes 8`로 돌리고 exit 3이면 `--resume`으로 잇도록 지시받는다(총 90분).
2. 에이전트가 **1회만 돌리고 잇지 않는다.** 문서는 `partial: true`, `caps_hit: ["max_minutes"]`, 큐에 남은 잔여 대량.
3. 오늘은 여기서 막힌다(`_check_residual`이 발견). 설계 이후에는 잔여 N행 + `evidence_scope` 한 블록으로 **exit 0**.
4. `build-state.json.evidence_debt`도 함께 해소된다 — 부채 술어가 «관찰 문서 version 2이고 `interactions` 키가 있는가»라는 **순수 구조 판정**이기 때문이다. 8분짜리 절단 관찰도 부채를 0으로 만든다.

결과: «≤90분 재수집 사슬»이라는 비용이 **8분 + JSON 편집**으로 내려간다.
설계 §3은 «H1이 불가를 제거하므로 래칫은 더 이상 막다른 길을 만들지 않는다»고 적었지만,
실제로 일어나는 일은 래칫이 **막다른 길이 아니게 되는 것이 아니라 래칫이 없어지는 것**이다.

**근거**
- `dddjango-web/assets/observe_interactions.pw.js:28` `DEFAULT_LIMITS = { maxSteps: 8000, maxDepth: 24, maxMinutes: 90 }`, `:645` `partial = 큐 잔여 || capsHit.length > 0`, `:649-653` — 상한은 **CLI 인자로 에이전트가 정한다** [확인].
- `dddjango-web/commands/dddjango-web.md:144` — «호출 1회에 `--max-minutes 8`을 주며, exit 3(상한)이면 같은 `--out`에 `--resume`을 더해 잇는다(총 예산 90분)». **잇는 행위를 강제하는 기계가 없다** [확인].
- `dddjango-web/scripts/evidence_debt.py:27-29` `is_interaction_observation` = `version == 2 and 'interactions' in observed` — 관찰의 **완주 여부를 보지 않는다** [확인].
- `check_design_evidence.py:972-974` — 오늘 `partial`은 잔여 메시지의 **접두어**일 뿐이고, 잔여가 0이면 통과다. 설계는 잔여 > 0인 partial까지 통과시킨다 [확인].

**막는 방법**
1. **`caps_hit`가 비어 있지 않은 문서는 `evidence_scope`로 덮을 수 없다** — 상한에 걸린 수집은 «못 본 것»이 아니라 «안 돌린 것»이므로 «드라이버 예산을 다 쓴 증거»를 먼저 요구한다: 문서에 실제 소요 시간/step 수를 기록하고 `max_minutes`가 기본값 90에 도달했을 때만 partial 경로를 연다.
2. **증거 부채 해소 술어를 «version 2 존재»에서 «version 2 + `evidence_level` full»로 올린다.** partial로 통과한 빌드는 부채가 `partial_settled`로 남고 hook이 계속 고지한다.
3. `observe_interactions` 요약에 **`resume 횟수`·`총 소요 분`**을 문서 필드로 남기고 검사기가 읽게 한다(현재 문서에 없음 — 확인).

---

### [BLOCKER] `approval_quote`는 «사용자 승인»을 식별하지 못한다 — 실측으로 확인

**악용 경로**
1. 예외 행/`evidence_scope`의 `approval_quote`에 `scope.md` 안의 **아무 10자 이상 문자열**을 넣는다.
2. `scope_ref`에는 빌드 폴더 안 **아무 파일의 아무 앵커**를 적는다(같은 문서일 필요 없음).
3. 통과.

**근거 — A8 실물 `scope.md`(13,144 bytes)에서 실행한 검사기 함수 결과** [확인]

`/Users/hyun/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons/scope.md`에
`check_design_evidence._collapse` + 부분문자열 판정을 그대로 적용:

| 후보 문자열 | 길이 | 판정 |
|---|---|---|
| `커밋: \`git -c core.hooksPath=/dev/null commit\`` | 44 | **통과** |
| `제품 결정만 발주자에게 STOP` | 17 | **통과** |
| `디자인 탐색 variant → 미구현(발주자 승인)` | 28 | **통과** |
| `미구현(발주자 승인)` | 11 | **통과** |

첫 줄이 결정적이다: **git 커밋 플래그 한 줄이 «드롭다운 153개를 관찰하지 않아도 된다»는 사용자 승인으로 성립한다.**
검사기는 「10자 이상 · 파일 안에 실재」만 본다(`:875-879`) [확인].

`scope_ref`는 `confined(build, ...)`이라 빌드 폴더 안 어떤 파일이어도 되고(`:46-60`), 앵커 **존재**만 본다(`:893-894`).
같은 빌드에서 쓸 수 있는 앵커: `scope.md` 12 · `design-spec.md` 51 · `visual-check.md` 11 · `coverage-review.md` 5 · `motion-notes.md` 1 = **79개** [확인].
`approval_quote`와 `scope_ref`는 서로 **연결 검증이 없다** — 인용은 A절에서 따오고 앵커는 B절을 가리켜도 된다 [확인].

**«기존 예외 행들이 이미 재사용하고 있는가»** — A8 9개 빌드 전수 확인: `interaction_exclusions` 행이 **하나도 없다**(있는 빌드 0) [확인].
따라서 실물 재사용 선례는 없다. 그러나 **재사용을 명령하는 규범은 이미 있다**:
`commands/dddjango-web.md:138` — «승인된 `interaction_exclusions`가 있었으면 재수집 뒤 새 관찰 문서의 target id 기준으로 행을 다시 짓는다(`approval_quote`·`scope_ref`는 staging `scope.md`에서 **재사용**하고 단위 키만 새 id에 맞춘다)» [확인].
즉 «사용자가 대상 X를 보고 승인한 원문»이 재동결 뒤 **기계가 고른 다른 target id에 재부착**되는 것이 정본 절차다.

설계는 이 규율을 그대로 `evidence_scope`에 물려준다(§1.1 «기존 예외 행과 같은 규율»).
행 단위에서는 10% 상한이 피해를 제한했다. **빌드 전체를 여는 단일 문으로 승격되면 제한이 사라진다** — 이것이 고무도장의 정의다.

**막는 방법**
1. **`evidence_scope`는 `scope.md`가 아니라 별도 승인 앵커를 요구한다**: `scope.md`에 `<a id="evidence-scope-approval"></a>` 같은 **전용 앵커 절**을 두고, `approval_quote`가 그 앵커 절의 본문 안에 있을 것을 검사한다(파일 전체 부분문자열 금지). 앵커↔인용 연결을 기계로 건다.
2. 인용에 **수치 동반을 요구한다** — 승인 원문에 `unverified` 값(또는 «전부»·«N건» 같은 수량 표현)이 포함되어야 한다. «몰랐다가 성립하지 않는다»(설계 §1 «왜 고무도장이 아닌가»)는 주장은 **사용자가 그 수를 본 문장을 인용할 때만** 참이다.
3. 재동결 시 `evidence_scope`의 quote는 **재사용 금지**한다(`commands:138`의 재사용 규칙에서 `evidence_scope`를 명시적으로 제외). 분모가 바뀌었으면 승인도 다시 받는다.
4. 최소한: `evidence_scope.approval_quote`는 `build-state.json.evidence_debt.quote`와 달라야 한다 — 재동결 요청 발화가 곧 미검증 승인이 되는 경로를 끊는다.

---

### [MAJOR] 수치 검증이 아무것도 검증하지 않는다 — 얇게 볼수록 숫자가 좋아진다

**악용 경로**
1. 드라이버가 메뉴를 열지 않으면 그 옵션들은 **어떤 인벤토리에도 등장하지 않는다** → 잔여도 아니고 `active`도 아니다.
2. 따라서 `unverified: 3 / active: 40`처럼 **작고 깔끔한 partial**이 나온다.
3. 성실하게 전부 연 빌드는 `unverified: 153 / active: 190`으로 **더 나쁜 숫자**를 받는다.

**즉 라벨이 노력에 반비례한다.** 같은 화면, 같은 시안에서 관찰을 덜 한 쪽이 배너에 더 좋은 수를 낸다.

**근거**
- `check_design_evidence.py:361-378` `interaction_residual` — «**어느 인벤토리에서든 활성으로 관찰된** (identity, action, option)». 관찰되지 않은 대상은 잔여가 아니다 [확인].
- `:840-846` `_active_targets` — 분모도 같은 인벤토리에서 나온다. **분자와 분모가 같은 관찰에서 나오므로 «안 본 것»은 양쪽에서 동시에 사라진다** [확인].
- 분모에 «시안이 실제로 가진 컨트롤 수»가 들어갈 자리가 없다. `source-manifest`·시안 소스 계수와 대조하는 검사가 없다 [확인].
- **단위 불일치**: `unverified`는 단위(identity, action, option) 수, `active`는 **identity 수**다. 텍스트 입력 1개 = identity 1 = 단위 3(focus/fill/blur, `:350`). 그래서 `153/190`은 비율이 아니다 — 100%를 넘을 수도 있다 [확인].
- 그런데도 설계 §1.3은 이 두 수를 배너 1급 줄로 내보낸다. **사람이 «80% 검증됨»으로 읽을 수를 «검증됨»의 의미 없이 내보내는 것**이다 [확인, 설계 원문].

**막는 방법**
1. **분모를 관찰 밖에 둔다.** `declared`·`discovery_limits`·`declared_unmatched`·시안 소스 스캔 계수 중 하나를 «있어야 할 대상 수» 기준선으로 삼고, `active`가 그보다 현저히 작으면(예: 직전 관찰 대비 급감) 발견으로 만든다. 최소한 **직전 회차 관찰의 `active`와 비교**해 하락을 표면화한다(`_history/` 가 이미 있다).
2. **단위를 맞춘다** — `unverified`/`active` 둘 다 단위 수로 내거나, `unverified_units / total_units`와 `unverified_identities / active_identities` **두 쌍**을 적고 배너에는 단위 비율만 낸다.
3. 배너 문구를 «검증 비율»이 아니라 «**미실행 조작 N건 / 관찰된 대상 M개 — 관찰 자체의 전수성은 기계가 보증하지 않는다**»로 고정한다(설계가 자기 한계를 지우지 않도록).

---

### [MAJOR] H2 «접기»의 정당성 주장이 코드와 다르다 — 기계는 이 축을 검증하고 있었다

설계 §2는 접기를 이렇게 정당화한다: «`state_hash`는 이미 face text는 같고 옵션 목록만 다른 두 상태를 구별하지 못한다 … 기계는 애초에 이 축을 검증하고 있지 않았다. 접기는 없던 검증을 없애는 게 아니라 이미 없던 것을 명시한다.»

**이 주장은 절반이 틀렸다.** `state_hash`가 못 하는 것은 맞지만, **표면(surface)과 단위(unit)는 이 축을 정확히 구별하고 있다.**

**근거**
- `assets/interaction_audit.js:194-213` `identityOf` — identity에 `owner_items_hash`(형제 항목 이름 목록의 sha, `:525`·`:1189`)가 들어간다. 서울의 «종로구»와 경기의 «수원시»는 **다른 identity**다 [확인].
- `:304-317` `surfaceKey` — `owner_items_hash`는 빼지만 **항목의 `name`은 그대로 남는다**. 도마다 항목 이름이 다르므로 축약 identity 집합이 달라 **표면 키가 도마다 다르다** [추론 — 코드 읽기. 주석 `:304-306`은 «도별 항목이 달라도 한 표면»이라고 적혀 있어 **주석과 구현이 어긋난 것으로 보인다**. 설계 §2 line 66이 «9 surface»라고 세고 있으므로 설계도 사실상 같은 읽기를 하고 있다].
- `check_design_evidence.py:947-961` `_check_surfaces` — 표면마다 **case `reached_by` 또는 승인된 표면 예외**가 필요하다 [확인].
- `:925-946` `_check_reached_by` — 그 case의 `reference_capture.sha256`이 해당 step의 **드라이버 저장 PNG와 바이트 일치**해야 한다 [확인].
- `:1282-1306` `validate_visual` — 구현 case 집합이 **입력 case 집합과 정확히 같아야** 한다. 즉 표면 1개 = 구현 캡처 1장 = G2 육안 대조 1건 [확인].

**따라서 접기가 지우는 것은 «없던 검증»이 아니다**: 표면 9개 → case 9개 → 시안 PNG 9장 → 구현 캡처 9장 → G2 대조 9건이
**표면 1개 → 1/1/1/1건**으로 줄어든다. 설계 §5 Q2의 답은 «영향 있다»이고, 영향의 크기는 **8/9 감소**다.

**설계 §5 Q4의 답을 만든다 — «접기 선언이 틀렸을 때 무엇이 잡는가»**

지금 설계대로면 **아무것도 잡지 못한다.** 경로가 전부 닫히기 때문이다:
- 선언은 `<screen>-declared.json`에 Coordinator가 적는다(서기 — `commands:1`·`:144`) → 기계 반증 없음.
- 접힌 옵션은 드라이버가 방문하지 않으므로 «같더라»는 **증거가 생성되지 않는다**(방문한다면 접기가 부담을 줄이지 못한다 — 아래 MAJOR 참조).
- 표면이 접히므로 case가 없고, case가 없으므로 시안 PNG도 구현 캡처도 없고, G2 육안 대조 대상도 아니다.
- 독립 리뷰어는 «표본으로 확인»할 의무가 있으나(`agents/design-review-web.md:25` ④) 볼 산출물 자체가 없다.

**막는 방법 — Q4에 대한 구체 처방**
1. **접기는 «방문 면제»가 아니라 «반복 면제»여야 한다.** 접힌 그룹에서 **대표 2건(첫·마지막, 또는 항목 수가 최소/최대인 변종)을 실제로 실행**하도록 강제하고, 그 둘의 **표면 키가 같을 때만** 접기를 인정한다. 다르면 발견. → 부담은 153→2로 줄고, «옵션마다 시각이 다름»은 기계가 잡는다.
2. **접기 단위는 «옵션»이지 «표면»이 아니다.** 단위 접기(`(identity, action, "*")`)는 허용하되 **표면 접기는 허용하지 않는다.** 표면이 실제로 같으면 표면 키가 같아 자동으로 1건이고, 다르면 case가 필요한 것이 맞다. 설계 §2의 «그 컨트롤이 여는 메뉴의 surface들도 한 surface로 접힌다»를 **삭제**한다.
3. `data_variant_folded` 기록에 `observed`(실제로 실행한 대표 수)와 `representative_surface_keys`를 넣고, 검사기가 «대표들의 표면 키 집합 크기 == 1»을 검증한다.

---

### [MAJOR] §4 배선표에 `agents/design-review-web.md`가 없다 — 규범 충돌이 방치된다

**악용 경로**: 설계대로 구현하면 두 문서가 정면으로 모순되고, 실행 시점에 어느 쪽이 이길지 정해져 있지 않다.
에이전트는 통과에 유리한 쪽을 고른다.

**근거** [확인]
- `dddjango-web/agents/design-review-web.md:25` 마지막 문장: «**같은 핸들러·데이터 변이·같은 인스턴스를 이유로 대상이나 결과 상태를 면제하지 않는다.**»
  — H2는 정확히 «데이터 변이를 이유로 한 면제»다. 플러그인 전체에서 이 문장이 있는 곳은 이 한 줄뿐이다(전수 grep).
- 같은 줄 ②는 리뷰어에게 «예외의 `approval_quote`가 정말 사용자 승인 원문인지» 판단할 의무를 지운다.
  **`evidence_scope`에 대응하는 의무는 없다** — 신설 필드이므로 리뷰어 charge에 존재하지 않는다.
- 설계 §4 배선표에 `agents/design-review-web.md`가 **없다** [확인, 설계 원문].

**결과**: (a) 리뷰어가 line 25를 지키면 접은 빌드는 전부 리뷰 fail → H2는 죽은 기능. (b) 리뷰어가 무시하면 명문 규범이 사문화되고, 빌드 전체를 여는 `evidence_scope`는 **독립 검토를 아무 charge 없이 통과**한다. 어느 쪽도 설계 의도가 아니다.

**막는 방법**
1. §4 배선표에 `agents/design-review-web.md`를 추가하고 line 25를 개정한다 — «데이터 변이 면제 금지»를 «**선언된 `data_variant` 밖의** 데이터 변이 면제 금지 + 선언된 접기는 대표 2건 실행 증거와 표면 키 동일성을 직접 확인한다»로.
2. 같은 줄 ②에 `evidence_scope`를 명시 추가한다 — «`evidence_scope.approval_quote`가 그 수치를 본 사용자의 발화인지, `unverified` 대상이 이 화면의 요구 범위에 속하는지 직접 판단한다». **`evidence_scope`가 있는 빌드는 리뷰 통과의 별도 항목으로 기록**하게 한다(`coverage-review.md` 본문에 수치 재기입).

---

### [MAJOR] 접기가 분모를 깎는다 / 또는 부담을 안 줄인다 — 설계가 어느 쪽인지 정하지 않았다

**악용 경로 · 설계 내부 모순**
설계 §2는 접기가 어디서 일어나는지 말하지 않는다. 두 갈래뿐이고 **둘 다 설계 목표와 충돌**한다.

- **(가) 드라이버 측 접기**(선언을 드라이버가 소비 — §4 표의 `observe_interactions.pw.js` 행이 이 읽기를 시사): 접힌 옵션은 인벤토리에 안 들어간다 → `_active_targets`의 **분모가 함께 줄어든다**. A8 규모로 `active` 190 → 약 37, 10% 상한 **19행 → 3행**. 즉 접기가 다른 모든 예외의 예산을 6배 조인다 → 더 많은 빌드가 partial로 내려간다. 설계 §2의 목적(«라벨을 희소하게 유지»)과 **정반대**다.
- **(나) 검사기 측 접기**: 드라이버는 153건을 그대로 돈다 → §2의 제목(«부담 자체를 줄인다»)이 성립하지 않는다. 줄어드는 것은 잔여 계산뿐이고 90분 예산은 그대로다.

**근거**
- `check_design_evidence.py:840-846` — `_active_targets`는 `targets`가 아니라 **인벤토리 엔트리**에서 센다. 드라이버가 안 열면 분모에서 빠진다 [확인].
- A8 시안 `관계인.dc.html` 실측: `REGIONS` 17 · `CITIES` 9키 153항목 = 옵션 170 [확인, 소스 직접 계수].
- 설계 §2·§4 어디에도 접기 시점 규정이 없다 [확인].

**막는 방법**
1. 접기 시점을 **명시**한다. 위 MAJOR(H2)의 처방을 채택하면 답은 «드라이버는 대표 2건을 돌고, 검사기가 잔여를 접는다»이며 분모는 대표 2건만 반영한다.
2. **상한의 분모를 접기 전 값으로 고정**한다 — `active`는 «접기 전 관찰된 활성 identity 수»로 정의하고 문서에 두 값(`active_raw`·`active_folded`)을 함께 남긴다. 접기가 예외 예산을 깎지 않게 한다.

---

### [MAJOR] «영구 기록»이 에이전트가 쓰는 파일에 산다 — 마무리에서 조용히 사라질 수 있다

**악용 경로**
1. G0에서 `evidence_scope`로 통과한다. Coordinator가 `build-state.json.evidence_level = "partial"`을 적는다.
2. Phase 2~3 동안 `build-state.json`은 **Coordinator가 여러 번 갱신한다**(슬라이스마다·G2마다·마무리마다).
3. 마무리 보고 직전 그 키를 빠뜨리거나 `full`로 적는다. `backstop.py`가 `build-state.json`을 읽는 구조이므로(설계 §4 표) **표면화되지 않는다**.
4. 사용자는 G0에서 한 번 들은 뒤 다시 듣지 못한다.

«되돌리려면 실제로 관찰을 채워야 한다»(설계 §1.3)는 **틀렸다** — 텍스트 편집 한 번이면 된다.

**근거**
- `commands/dddjango-web.md:9`·`:235` — `build-state.json`은 Coordinator가 **직접 쓰는 파일** 목록에 있다 [확인].
- `check_design_evidence.py:1017-1029` `_notices` + `:1405-1407` — 예외 전량·`partial` 통지는 **`--phase prepare|inputs`에서만** stderr로 나간다. `--phase visual`에서는 나오지 않는다 [확인].
- `scripts/backstop.py:300` — `validate_inputs(...)`를 호출하지만 **`_notices`를 출력하지 않는다.** 마무리 경로에 예외·partial 통지가 **전혀 없다** [확인].
- `backstop.py:160-166` — 게이트 판정에 쓰는 값은 전부 `build-state.json`(`prior.get(...)`)에서 읽는다 [확인].
- 배너는 자유 서술 슬롯 3칸이고(`commands:92-99`) 내용 검증이 없다 — 라벨 표기는 순수 에이전트 준수 사항 [확인].

**막는 방법**
1. **backstop이 `build-state.json`이 아니라 `design-input.json.evidence_scope`를 읽게 한다.** 그 파일은 `input_digest`·`review_digest`에 묶여 있어 고치면 다른 검사가 깨진다. 기계 산출물 사슬 위에 라벨을 올린다.
2. `backstop.py`가 `_notices`를 **항상 출력**하게 한다(예외 전량 + partial + evidence_level). 마무리 보고의 «실행한 검증만 보고한다» 절에 **«미검증 지위 줄»을 의무 항목으로 추가**한다.
3. `evidence_level`을 **G2 배너 1급 의무 줄**로 올린다 — 실측 대조·모션 처분·절단 여유와 같은 급(`commands:187`의 판형 그대로). 사용자가 시각 대조를 수락하는 바로 그 화면에서 «이 대조의 기계 근거가 N건 비어 있다»를 본다.

---

### [MINOR] `scope_ref` 규율은 실물에서 이미 장식이다

**근거** [확인 — A8 실측]
- `design-input.json`의 **case `scope_refs`는 앵커 검증을 받지 않는다**(`check_design_evidence.py:1206-1207`은 «nonempty string list»만 본다).
- A8 관계인 빌드 12 case의 `scope_refs`는 `scope.md#related_persons` / `scope.md#preferences` 두 종인데, `_anchors(scope.md)`가 내놓는 12개 앵커에 **둘 다 없다**. 즉 **전 case가 존재하지 않는 앵커를 가리키고 통과했다.**

설계 §1.1이 «기존 K3 규율 재사용»으로 신뢰를 빌려오는데, 그 규율의 실제 강도가 이 정도다.

**막는 방법**: `scope_refs`도 앵커 존재를 검증한다(별건 수리로 분리 가능). 최소한 설계 문서에서 «기존 규율 재사용 = 충분한 방어»라는 서술을 빼고, `evidence_scope`는 자체 방어(위 BLOCKER 3의 전용 앵커)를 갖는다고 적는다.

---

### [MINOR] Q1 답 — 빌드 1건은 «한 화면이 전체를 오염», 문서별은 «문을 N개»

설계 §5 Q1이 열어둔 갈림. 양쪽 다 나쁜 면이 있으나 악용 관점에서는 **빌드 1건이 더 위험**하다:
한 번의 승인 원문이 모든 화면·모든 viewport의 미검증을 덮고, 나중에 추가되는 화면까지 그 아래로 들어온다.

**권고**: **기록은 관찰 문서별**(`interactions/<path>`마다 `unverified`/`active`), **승인은 문서별 원문**,
**빌드 라벨은 문서 라벨의 최댓값**(하나라도 partial이면 빌드 partial). 배너는 문서별 줄을 낸다 —
«4개 중 1개 문서가 partial»과 «전부 partial»이 같은 한 줄로 보이지 않게.

---

### [MINOR] 벽의 크기가 실측된 적이 없다 — 170은 시안 계수치이지 잔여가 아니다

**근거** [확인]
- A8 9개 빌드 전수 조회: **version 1 스키마 `interactions.json`이 한 건도 없다.** 관계인 빌드의 12 case는 전부 `source_observation.version == 1`(레거시 관찰).
- 유일하게 `captures/*interactions.json` 이름을 가진 파일(`20260908-0143-web-chat-spine/captures/source-interactions.json`)은 수집기 판형이 아닌 임시 JSON이다(`targets` 없음).
- 진단의 «시·도 17 + 시·군 153 = 170»은 **시안 소스에서 직접 센 값**이라고 진단 자신이 밝힌다(`diagnosis.md:34-35`).

**[미확인]** 실제 드라이버의 잔여가 몇인지는 아무도 모른다. 단위는 `(identity, action, option)`로 dedup되므로,
드라이버가 시·군 트리거를 **한 번만** 여는 큐 순서라면 실제 잔여는 153이 아니라 그보다 훨씬 작을 수 있다
(`interaction_residual`은 «관찰된» 옵션만 센다 — `:361-378`). 반대로 도마다 열면 153 + 표면 9가 된다.

**막는 방법**: 설계 확정 전에 **A8 시안으로 드라이버를 1회 실행해 실제 `active`·잔여·표면 수를 측정**한다(A8 워크트리는 읽기 전용이므로 시안 바이트만 복사해 별도 폴더에서). 실측이 «잔여 25 · 표면 3»이면 H1(빌드 전체를 여는 문)은 **불필요**하고 기존 10% 상한 안에서 닫힌다 — 그 경우 이 설계는 필요 없는 문을 내는 것이다.

---

### [MINOR] `_check_exclusions`의 early return — 구현 함정

`_check_exclusions`는 `rows is None`이면 **즉시 반환**한다(`:851-852`). `evidence_scope` 검증을 이 함수 안에 붙이면
«`interaction_exclusions` 없이 `evidence_scope`만 있는 빌드»가 **검증 없이 통과**한다.
또한 `_check_residual`/`_check_surfaces`는 문서별로 돌고 `_check_exclusions`는 빌드 끝에서 1회 돌므로,
`evidence_scope`를 어느 쪽에 두는지에 따라 문서별 수치 대조가 성립하지 않을 수 있다.

**막는 방법**: `evidence_scope` 검증을 `_check_exclusions` 밖 **독립 함수**로 두고 `validate_inputs` 말미에서 무조건 호출한다.
`evidence_scope`가 있는데 상한을 넘지 않으면(= 불필요한 선언) 그것도 발견으로 만든다 — 라벨을 **선제적으로 붙여 두고 나중에 마음껏 초과하는** 경로를 막는다.

---

## 총평 — 이 변경 뒤 «가장 쉬운 길»

게으른 에이전트가 도달하는 상태를 구체적으로 그리면 이렇다.

1. 드라이버를 `--max-minutes 8`로 **한 번** 돌린다. exit 3. **잇지 않는다.**
2. 검사기를 돌려 잔여 목록을 받는다(검사기가 친절하게 20건씩 출력한다 — `:969-971`).
3. 잔여 전량을 `interaction_exclusions` 행으로 생성한다. `approval_quote`는 `scope.md`에서 아무 문장이나 하나 골라 **전 행에 복사**한다. `scope_ref`는 `design-spec.md`의 아무 앵커.
4. `evidence_scope: {"level":"partial","unverified":<검사기가 준 수>,"active":<검사기가 준 수>,...}`.
5. exit 0 · `design_status=ready` · 증거 부채 0 · Phase 1 진입.
6. G0 배너에 한 줄 적는다. 그 뒤로 아무 데서도 다시 나오지 않는다.

**총 추가 비용: 명령 1회 생략 + JSON 편집 1회.** 정직한 길의 비용: 최대 90분 드라이버 + 보완 조작 + 표면마다 case·캡처.
**비용 차이가 두 자릿수 배수다.** 설계 §1의 «비용이 면제되는 게 아니라 이전된다 — 차단 비용 → 기록 비용»은,
기록 비용이 **JSON 6줄과 배너 한 줄**인 한 성립하지 않는다.

하드월을 걷어내는 방향에는 동의한다. 다만 **문을 여는 비용이 문을 안 여는 비용보다 싸면 그 문이 정문이 된다.**
위 BLOCKER 3건의 «막는 방법»은 전부 «문을 닫자»가 아니라 **«문의 비용을 관찰의 비용에 붙들어 매자»**다:
상한 대신 3등급 라벨, `caps_hit` 문서의 배제, 전용 승인 앵커 + 수치 동반 인용, 대표 2건 실행 강제.
