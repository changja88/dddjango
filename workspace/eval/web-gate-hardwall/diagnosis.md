# 진단 — 관찰 게이트의 하드월: 어떤 행동으로도 못 여는 상태 (2026-09-15)

사용자 지시(구속력): **«재동결하라고 하고 차이점이 있으면 수정을 하게 하면 된다.
그리고 이게 애초에 무슨 이유로든 불가능해지는 거 자체가 말이 안 된다.»** → **«하드월 걷어내»**

## 증상

A8 관계인 빌드에서 «4개 드롭다운을 시안대로 커스텀으로 만들라»가 **«지금 빌드 자체가 불가»**로 보고됐다.
코드 변경 0·커밋 0. 사용자는 재동결→대조→수정이라는 단순한 요구를 했는데 파이프라인이 «불가»를 냈다.

## 벽의 정체 — 조합으로 생긴다

단일 검사가 아니라 **세 규칙의 곱**이다.

1. **잔여 게이트** (`check_design_evidence.py:963-975`)
   관찰 문서의 잔여 단위 `(identity, action, option)`가 하나라도 남으면 발견이다.
   단위는 «어느 인벤토리에서든 활성으로 관찰된» 것 전부다(`:297`).
2. **예외의 유일한 문** (`:849-897`)
   잔여를 닫는 길은 `interaction_exclusions` 뿐이고, 행마다 `scope.md`에 실재하는
   사용자 승인 원문(10자 이상·앵커 실재)을 요구한다. 여기까진 건전하다.
3. **하드월** (`:895-897`)
   ```python
   active = _active_targets(items)
   if len(rows) * 10 > active:
       issues.append(f'예외 {len(rows)}행은 활성 대상 {active}개의 10% 상한을 넘는다')
   ```
   **상한 위에는 문이 없다.** 사용자가 알고 승인해도 열리지 않는다.

여기에 Coordinator의 «**inputs exit 0일 때만 ready**»가 겹치면 Phase 진입이 막힌다.
즉 **에이전트가 취할 수 있는 행동이 0인 상태**가 실제로 성립한다.

### A8 실측 — 벽이 어떻게 섰나

- 시안 `관계인.dc.html`의 태어난 곳 캐스케이드: **시·도 17 + 시·군 153 = 170 옵션**
  (`REGIONS` 17 · `CITIES` 9개 도 합 153 — 시안 소스에서 직접 셈).
- 조작 상태 수집(ⓐ)이 **유보**돼 있었다 — 재동결 journal:
  `{'decision': 'defer', 'reason': '… 조작 상태 수집(ⓐ) 미요청 · **구현 재진입 시 ⓐ 필수**', 'cases': 12}`
- 구현 재진입 = 유보한 빚의 만기. 그 관찰이 170옵션짜리다.
- 드라이버가 못 닿는 축이 규범에 이미 명시돼 있다: **역캐스케이드**는 «드라이버 큐 순서로 발견되지
  않는다 — `--declared`와 독립 검토 책임이며 기계 보장이 아니다»(`design-evidence.md:347-350`) ·
  `state_hash`는 «face text는 같은데 옵션 목록이 다른 select/combobox 두 상태를 구별하지 못한다»(`:366`).
- 즉 **기계가 못 닫는 잔여가 구조적으로 남고**, 그걸 닫을 유일한 문(예외)은 10%에서 잠긴다.

수집기 자체 상한은 범인이 아니다 — `DEFAULT_LIMITS = { maxSteps: 8000, maxDepth: 24, maxMinutes: 90 }`
(`observe_interactions.pw.js:28`)로 170옵션은 여유 안이다.

## 왜 이게 설계 결함인가

플러그인에는 **«못 본 것을 기록하는» 어휘가 이미 있다** — `discovery_limits` · `declared_unmatched` ·
`caps_hit` · `partial`. 검사기가 이것들을 **스키마로 요구하고 검증까지 한다**(`:676`·`:702-717`).

그런데 그 어휘가 **게이트에 연결돼 있지 않다.** 기록은 남지만 문은 열리지 않는다.
결과적으로 파이프라인은 «무엇을 검증 못 했는지»를 말할 수 있으면서도 «그래서 못 간다»만 할 수 있다.

**원칙 위반**: 게이트는 **막는 장치가 아니라 비용을 기록하는 장치**여야 한다. 사용자가 사실을 알고
진행을 지시하면 길이 있어야 하고, 게이트의 역할은 «무엇이 미검증인지»를 지우지 못하게 남기는 것이다.

## 수리 방향 후보 (설계에서 확정)

- **H1 — 상한 위의 문**: 상한을 넘는 예외를 **포괄 승인 + 미검증 명시 기록**으로 통과시킨다.
  고무도장 방지는 «상한을 없앤다»가 아니라 «넘으면 비용을 영구히 기록한다»로 바꾼다 —
  `build-state.json` 항구 기록 · G 배너 1급 줄 · 마무리 보고 의무.
- **H2 — 부담 자체를 줄인다**: 데이터 변종 옵션 목록(시·도마다 갈리는 시·군)은 surface·단위를
  **접는다** — 같은 컨트롤의 데이터 변종을 한 단위로 본다.
- **H3 — 래칫 완화**: 증거 부채 유보를 «나중에 전량 필수»가 아니라 부분 상환 가능하게.

## 절차

[[web-repair-procedure]]대로: 이 진단 → 설계 → 독립 적대 검토 → 계획 → 계획 리뷰 → 구현 →
행동 시험 → 독립 구현 리뷰 → `make verify` → 승인 후 커밋·`make release-web`.
A8은 읽기 전용([[a8-final-testbed]]).

---

## 재조준 (2026-09-15 밤 · 실측 후)

앞 절의 «벽» 서술은 **한 겹만 봤다.** 실측하니 벽은 **두 겹이고 순차적**이다.

### 겹 1 — 지금 실제로 막는 것 (실측)

```
$ python3 check_design_evidence.py --build <A8 빌드> --project-root <A8> --phase inputs
[design-evidence] defect: cases[0..11].source_observation: interaction evidence required (version 2 with interactions)   ← 12건
[design-evidence] defect: coverage_review: reviewed-input does not match current source/cases/observations              ← 1건
```
**13건 전부가 «관찰을 아직 안 했다»다.** 잔여도 10% 상한도 표면도 **발화조차 하지 않는다.**
앞 절이 «벽»으로 지목한 `:895-897`은 지금 A8에서 **도달되지 않는 코드**다.

### 겹 2 — 겹 1을 지나면 나오는 것 (A8 자신의 기록)

`build-state.json.dropdown_rebuild_decision.blocker` 원문:
> «v2 interaction-evidence: 시·군 캐스케이드 Select(17 시·도×~150 시·군) 전수 관찰 불가 —
> **잔여 66 menuitem > active150의 10% 예외상한 15**. `--resume`은 캐스케이드 재발견으로
> 잔여 증가(88→163 targets). surface 예외는 unit 잔여 미포함. inputs exit 0 불가 → coder 게이트 차단.»

내가 A8 시안 사본에 드라이버를 직접 돌린 결과(12분 상한·미완주):
`targets 114 · executed 123 · residual 38 · surfaces 19 · partial true · capsHit ["max_minutes"]`
→ 잔여 38 > 상한 11. **겹 2는 실재하고, 관찰을 완주해도 열리지 않는다.**

### 교훈

설계 v1·v2는 겹 2만 겨눴다. 그래서 «설계대로 고쳐도 A8은 안 열린다»가 참이었다.
**두 겹을 한 문으로 다뤄야 한다** — 설계 v3 §2의 «벽을 세지 않는 단일 집행 지점»이 그 답이다.

## 합격 기준의 출처 — A8 실물 결함 2건 (2026-09-15)

사용자가 A8 화면에서 발견한 결함 2건을 **이번 수리의 합격 기준으로 삼는다.**

### 결함 1 — 포커스 링 좌우 절단

`related_persons.css:393-400`의 `.rpe-scroll`에 `overflow-y: auto`만 있고 padding이 없다.
한 축이 `visible`이 아니면 다른 축도 `auto`로 계산되므로 가로로도 자르고, 좌우 여유가 0px다.
링 확장은 3px(`--focus-ring: 0 0 0 3px`)라 좌우가 통째로 잘린다.

**v1.1.16이 이미 잡는다** — `check_clip_clearance.py`가 A8에서 `.rpe-scroll` 4변 확정 포함 12건.
수리 대상이 아니라 **회귀 확인용**이다.

### 결함 2 — 직각 이중 링

`base.css:88-91`의 전역 `:focus-visible { box-shadow: var(--focus-ring) }`가 native `<select>`에
그대로 걸린다. `.select-field__select`는 `border-radius` 선언이 없어 `0px`라 **직각 링**이고,
`.select-field__control:focus-within`의 둥근 링과 **겹쳐 그려진다**.
Chrome 실측: 마우스 클릭만으로 `<select>`가 `:focus-visible`을 매치한다(`focusVisible: true`).

`.input-field__input`은 `components.css:323`에 억제(`box-shadow: none`)가 있어 면제된다 —
**select만 누락된 한 줄**이다.

시안에는 없다: 시안 번들 `styles.css`에 `focus` 0건, 시안 `Select`는 native `<select>`를 안 쓰고
(`createElement("select")` 0건) `Dropdown` 트리거 한 요소에만 `borderRadius`+`focus-ring`을 얹는다.

**현재 어떤 검사도 못 잡는다.** `render_audit.js:196-197`은 `:focus` **셀렉터 이름만** 모으고,
`compare_render_audit.py:45-46`은 그것을 `MOTION_LIST_FIELDS`로 **문자열 목록 비교**만 한다.
이름이 같으면 통과한다 — A8은 시안과 같은 토큰을 같은 이름의 규칙에 썼으니 그대로 지나간다.
→ 설계 v3 §5가 이 구멍을 메운다.

## 별건 대기 목록 (이번 사이클 제외 · 설계 v3 §6의 X 5건)

대상 빌드에서 발화하지 않고 이번 합격 기준에 닿지 않아 제외한다. 안 쓰는 문을 여는 것은
게이트 완화이지 수리가 아니다.

1. 재동결이 `.dc.html` 경로 전용 — 다른 출처 빌드의 «재동결하라»가 영구 불가 (rv-B B3)
2. 설계 빌드 0 + `config.json` 有 → `backstop` 영구 BLOCKER (rv-B MAJOR)
3. `implementation_digest`의 `web/` 필수가 비시안 실행에서 BLOCKER (rv-B MINOR)
4. 진행 중 설계 빌드가 같은 프로젝트의 다른 실행을 막음 (rv-B MINOR)
5. `archive_files` 4096 파일 상한에 승인 문이 없음 (rv-B MINOR)
