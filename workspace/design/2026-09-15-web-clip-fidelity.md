# 설계 v2 — 절단 충실도 (2026-09-15)

진단 정본: `workspace/eval/web-scroll-clip-fidelity/diagnosis.md`.
적대 검토 4건(rv-A 판정규칙 · rv-B 집행경로 · rv-C 범위비용 · rv-D 체계정합) 반영.
**v1 은 폐기한다** — v1 의 본 수리(브라우저 실측 확장)가 이 결함에 도달조차 못 한다는 것이
실증됐다. 내가 직접 재확인한 것은 `workspace/eval/web-scroll-clip-fidelity/design-review/verified.md`.

누적 BLOCKER 17 (A 5 · B 5 · C 3 · D 4). 그중 설계 방향을 바꾼 것은 아래 셋이다.

## 0. v1 이 틀린 지점 — 실증

**① 브라우저 실측은 결함에 도달하지 못한다** (rv-B B1 = rv-C C1 · 내가 재확인)

A8 실빌드의 두 실측을 직접 열었다.

| | url | texts | 다이얼로그 텍스트 |
|---|---|---|---|
| `render-audit-impl.json` | `127.0.0.1:8891/related-persons/` | 13 | **0** |
| `render-audit.json` | `…/관계인.dc.html` | 15 | **0** |

둘 다 **목록 페이지 한 장**이다. 결함 컨테이너 `.rpe-scroll` 은 HTMX swap 으로만 들어와
초기 DOM 에 없다 → `querySelectorAll` 0건 → exit 0 **green**.
v1 §3.1 이 시안측에 대해 쓴 바로 그 이유를 구현측에 적용하지 못했다.

**② 토큰 축은 고갈된 게 아니라 위반됐다** (rv-C C3 · 내가 재확인)

- A8 `design-spec.md:468` — **`--space-1`(=2px) 기각**, 사유 «미사용 space 단계».
- 그러나 동결 `관계인.dc.html` 인라인 선언에 **2px 가 4건**:
  `padding: 2px 4px 0` · `gap: 2px` · **`padding: 2px 2px 4px`** · `padding: 0 2px`.
- **기각 사유가 사실과 다르다.** 그리고 **토큰 처분을 검사하는 기계가 저장소에 0개**다.

v1 §1 의 «토큰 축을 넓혀도 못 잡는다»를 철회한다. 정반대다 — 기각 정당성 검사 하나면 G1 에서 잡힌다.

**③ 기하 판정 규칙 자체가 성립하지 않는다** (rv-A BLOCKER 5)

특히 «딱딱한 절단 축 = `scrollSize <= clientSize`»가 **`overflow:hidden`·`clip` 에서 정반대로 뒤집힌다** —
hidden 은 내용이 넘쳐도(`scrollSize > clientSize`) 스크롤이 불가능한 **가장 단단한 클립**인데
이 규칙은 그것을 soft 로 보고 면제한다. 그 밖에 `:checked` 링 미열거 · soft 축의 시작/끝 변
영구 절단 면제(시안이 준 하단 `4px` 의 근거를 못 잡는다) · 전역 대체 집합의 비가시 요소 오탐 ·
`blur+spread` 2배 과대 · `position:absolute` 의 클리핑 조상 오인 등.

## 1. 채택 — 수리 A: 토큰 처분 집행 검사 (필수)

**이것이 본 수리다.** 이 결함을 **G1 에서** 잡고, 브라우저·스키마 버전·새 산출물·기하가 전부 불요다.
rv-A 의 BLOCKER 5·MAJOR 10 은 전부 기하 규칙에 걸린 것이라 이 경로에는 **하나도 해당하지 않는다.**

`scripts/check_token_disposition.py` 신설:

```
python check_token_disposition.py --spec-only <design-spec.md> <design-tokens.json> <design-ref 경로>
```

검사 3종:
- **T1 전수성** — `design-tokens.json` 절단 풀의 모든 토큰이 채택/기각 어느 한쪽에 정확히 1회.
  (현재 이 전수성조차 기계가 안 본다 — 「크기 전수 연결」은 규범에만 있고 집행이 없다.)
- **T2 기각 정당성** — **기각한 토큰의 값이 동결 시안에 실제로 나타나면 red.**
  값 대조는 정규화 후 리터럴 일치(`2px` ↔ `padding: 2px 2px 4px`)와 `var(--토큰)` 인용 양쪽.
  이번 결함: `--space-1`(2px) 기각 + 시안 2px 4건 → **red**. 사유 문구는 보지 않는다(거짓말 방지).
- **T3 양방향** — 표에만 있고 풀에 없는 토큰 금지.

exit `0`=발견 0 · `2`=발견 ≥1(architect 반송 근거) · `1`=사용법·파싱(미실행 취급).
**판형 앵커 — 실측으로 정정한 것.** 기존 산문을 관용 파서로 읽으려 했으나 A8 실명세 9개에
관용 파서를 돌린 결과 **5개는 절 자체가 검출되지 않고** 커버리지가 0·24·87·100% 로 흩어졌다
(판형이 최소 3종: per-token 행 · per-axis 그룹 행 · `채택(n):` 산문 줄).
→ **byte 고정 헤더를 요구한다**(`check_motion_spec.py` 와 같은 판형):

```
| 축 | 처분 | 토큰 |
```

축 ∈ `colors|typography|spacing|borderRadius|shadows` · 처분 ∈ `채택|기각` · 토큰은 백틱 인용 목록.
**10행**(5축 × 2)이면 230 토큰이 전수로 덮인다 — 2026-09-09 빌드가 이미 사실상 이 모양으로 쓰고 있어
architect 의무 증가는 «형식 고정» 수준이다.
**헤더 미검출(레거시 산문 판형)은 `[warn]` + exit 0** — 합법 재빌드를 막지 않는다.

## 2. 채택 — 수리 B: 정적 클리핑 여유 검사 (권장·좁힘)

결함 *부류*를 G2 에서 막는다. 브라우저를 쓰지 않는다 — rv-A 의 기하 BLOCKER 를 전부 회피한다.

`scripts/check_clip_clearance.py` 신설: 소비 프로젝트 `web/` 트리의 **CSS 만** 읽는다.

1. 링 확장 수집 — 포커스/`:checked` 규칙의 바깥 `box-shadow` 를 파싱해 **최대 확장** S 를 얻는다.
   (`--focus-ring` 하드코딩 금지 — rv-A MAJOR. 색 함수·`#hex` 제거 후 순서 파싱, 단위 없는 `0`도 길이,
   확장 = `spread + blur/2`(rv-A MAJOR — `blur` 전체는 2배 과대).)
2. 클리핑 규칙 수집 — `overflow(-x|-y): auto|scroll|hidden|clip`. **A8 실측 34건.**
3. 각 규칙의 패딩이 S 미만인 축을 후보로 올린다. **A8 실측 27건.**
4. **노이즈 절단** — 후보 중 «그 셀렉터가 붙는 요소의 템플릿 서브트리에 링을 지는 요소
   (`input`·`button`·`select`·`a[href]`·`[tabindex]` 또는 링 보유 컴포넌트 include)가 있는 것»만
   발견으로 낸다. 나머지는 인벤토리로만 남긴다(아바타·텍스트 말줄임·sr-only 입력이 여기로 빠진다).

지위는 `compare_render_audit`·`check_motion_spec` 과 동급 — **판단 자료(비차단)·배너 1급 의무 표기**.
exit `0`/`2`/`1`.

**이 검사의 한계를 명시한다**: 템플릿 조인은 Django `include` 를 1단만 따라간다. 동적 클래스 부착은
못 본다. 그래서 **차단이 아니라 판단 자료**이고, 수리 A 가 일차 방어다.

## 3. 기각 — 수리 C: 브라우저 실측 확장 (v1 의 본 수리)

기각 사유 3가지, 전부 실증:
- **도달 불가** (§0 ①) — 판정이 도는 URL 에 결함 컨테이너가 없다. 부착점을 G2 case 순회
  (구현측 다이얼로그 캡처 12장이 실재한다)로 옮기면 도달은 되지만, 그 순회는 Coordinator 가
  case 마다 수행하는 경로라 rv-B 의 집행 취약점이 12배로 붙는다.
- **판정 규칙 불성립** (§0 ③) — rv-A BLOCKER 5.
- **파급 비용** (rv-D B1) — `audit_version` 3 상향은 `compare_render_audit.py:81·100·259` 술어와
  `:194` 리터럴에 걸리고 `fixtures_audit.sh` 5건을 red 로 만든다. v1→v2 선례(커밋 `72854ce3`)는
  새 버전 표본 +67줄을 함께 넣었다 — v1 설계는 이 작업을 통째로 빠뜨렸다.

정적 그림자(카드 drop-shadow) 판정도 하지 않는다 — 판정 대상이 12→63건이고 판정 규칙이 없다(rv-C).
v1 이 «후일 확대의 훅»으로 넣으려던 `static_shadows` 인벤토리도 **넣지 않는다**(미리 만든 확장 지점 — 원칙 05).

## 4. 규범·배선

| 파일 | 변경 | 근거 |
|---|---|---|
| `commands/dddjango-web.md` | G1 승인 직후 `check_token_disposition.py --spec-only` 실행 + 반송 · G2 `check_clip_clearance.py` + 배너 표기 | rv-B B4·B5 |
| `agents/design-architect-web.md` | 기각 사유의 사실성 의무(«미사용»을 쓰려면 시안에 없어야 한다) | §0 ② |
| `agents/design-review-web.md` | 기각 정당성 리뷰 항목 | rv-B |
| `agents/discipline-reviewer-web.md` | **기존 `:61` sticky/fixed 조상 overflow 대조 트리거를 «바깥 링/그림자» 축으로 넓힌다** — 이미 blocker 등급이 선 유일한 차단 경로다(rv-B 부수 발견, 규범 한 문단 비용) | rv-B |
| `skills/architecture-web/references/final.md` | §8 「크기 전수 연결」에 기각 정당성 1문장 + 집행 검사기 명시 | §0 ② |
| `Makefile` | `verify-web` 픽스처는 글롭 자동(추가 배선 불요·rv-D 부수 확인) — **`Makefile` 변경이 없으면 봉인 재발행도 불요** | rv-D B3 |
| `docs/DEVELOPMENT.md` §1 | 새 스크립트 2종 등재 | rv-D |

**새 산출물이 없다** → `refreeze.py` 폐기 집합·`web_refreeze_contract.py` D1·`backstop.py` 마커·
`build-state.json` 플래그를 **건드리지 않는다**(rv-D B4 · rv-B B3 소멸).
**`audit_version` 을 올리지 않는다** → 픽스처 5건 파급 소멸(rv-D B1 소멸).
**`.mjs` 신설이 없다** → 글롭 문제 소멸(rv-D B2 소멸). 픽스처는 `fixtures_token_disposition.sh` ·
`fixtures_clip_clearance.sh` 2종(파일을 두면 `run_fixtures.sh` 글롭이 자동 수집).

Codex 미러: `scripts/` 는 `Makefile:96` `diff -rq` 가 자동으로 누락을 잡는다. 커맨드·에이전트·
references 는 수동 의무(references 3종은 `cmp -s` byte 미러 — rv-D MAJOR).

## 5. 남긴 위험

- **W1** — 수리 B 의 템플릿 조인이 1단 include 만 따라가므로 깊은 include 사슬의 링을 놓친다. 비차단 지위로 수용.
- **W2** — 수리 A 의 값 대조는 리터럴 일치라, 시안이 `0.125rem` 로 쓰고 토큰이 `2px` 면 못 잇는다.
  rem→px 환산(16 기준)을 넣되 그 외 단위는 «미대조»로 발화한다.
- **W3** — A8 진행 중 재동결(`_refreeze-20260915-200029`)은 이 배포 전에 v2 로 끝난다. 새 검사는
  다음 G1 부터 적용된다. `audit_version` 을 안 올리므로 레거시 충돌은 없다.
- **미착수** — `:checked` 링(rv-A B1)은 수리 B 의 1단계 «포커스/`:checked` 규칙»에 포함한다.
  soft 축 시작/끝 변 절단(rv-A B3)은 정적 검사가 축 구분을 하지 않으므로 자동 포함된다.

## 5.5 구현에서 확정된 것 (적대 검토 6기 · 누적 BLOCKER 25건 반영)

- **판정 확장 = `spread + |offset|`** — blur 제외. 실측(Chrome 픽셀): `0 0 20px 0` 의 페인트 확장은
  **29px**(≈ `spread + 1.45×blur`)로 `spread+blur/2`(10)도 `spread+blur`(20)도 아니다. blur>0 은 인벤토리 고지만.
- **축 전파 필수** — 한 축이 `visible` 이 아니면 다른 축도 `auto` 로 계산된다. 이 전파가 결함의 기전이다.
- **콤마 목록은 멤버별로** 처리한다(마지막 하나만 보면 A8 실 CSS 판형에서 미탐).
- **패딩은 셀렉터별 캐스케이드**로 읽고, `calc()`·미해소 `var()` 는 **0 이 아니라 «미해석»** 이다
  (0 으로 보면 멀쩡한 빌드를 «확정» 으로 반송한다).
- **토큰 풀은 중첩 dict 를 벗긴다** — A8 typography 50개가 전부 `{"size": …}` 판형이라 그대로 두면 영구 미대조다.
- **처분 표 파서는 연속 블록만** 먹는다(선례 `check_motion_spec.parse_tables`).
- **탈출구 가드의 절 제목 앵커(«토큰 전수 처분»)를 규범에 성문화**했다 — 안 그러면 가드가 공전한다.

## 6. 범위 브리프 (승인 게이트용)

| | 수리 A 단독 | 수리 A+B |
|---|---|---|
| 이번 결함 | **G1 에서 잡는다** | G1+G2 |
| 새 스크립트 | 1 | 2 |
| 규범 편집 파일 | 5 | 7 |
| 브라우저·버전 올림·새 산출물 | 없음 | 없음 |
| 적대 검토 BLOCKER 잔여 | 0 | 0 |
| 규모 | 수리 1(v1.1.14) 이하 | 수리 1 급 |

**권고: A+B.** A 가 이 결함을 직접 막고, B 가 «구현이 스스로 만든 절단»(시안에 없던 클립)을 막는다 —
A 는 시안↔명세 축이라 그 경우엔 침묵한다. 둘 다 v1 대비 대폭 축소됐고 브라우저를 안 쓴다.
