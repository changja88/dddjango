# 진단 — 관찰 드라이버가 상한을 넘겨 무한 정지한다 (2026-09-16 · v1.1.20)

## 실증

A8 세션이 `설정.dc.html` 관찰을 `--max-steps 200 --max-minutes 5`로 돌렸다.

```
PID 12556  node observe_interactions.mjs
  경과 8시간 52분 · CPU 0.0% · 상태 S(sleep)
  마지막 파일 쓰기 03:22:13 · 확인 시각 12:12
  --max-minutes 5 는 발화하지 않았다
```

A8 세션은 그 명령이 끝나기를 기다리며 멈춰 있었고, Playwright Chromium도 함께 9시간 떠 있었다.
**«완료도 실패도 아닌» 상태**라 어떤 회수 경로도 작동하지 않는다.

## 원인 — 상한은 감시견이 아니라 협조적 점검이다

`observe_interactions.pw.js:652-656`:

```js
function capHit(ctx, run) {
  if (run.steps.length >= ctx.limits.maxSteps) return 'max_steps';
  if (Date.now() - run.startedAt >= ctx.limits.maxMinutes * 60000) return 'max_minutes';
  return null;
}
```

호출 지점은 넷(`:629`·`:1320`·`:1365`·`:1430`) 전부 **루프의 항목 사이**다. 루프가 어떤 `await`에
갇히면 `capHit`은 영영 호출되지 않는다.

**그리고 나는 이것을 이미 알고 있었다.** `:38-41` 주석:

> 조작·이동 타임아웃 — 상한(--max-steps/--max-minutes)은 **항목 사이에서만 재므로**,
> 한 조작이 기본 30s를 끌면 도구 상한(600초) 분할 실행이 무너진다.

그래서 `page.setDefaultTimeout(OPERATION_TIMEOUT_MS=5000)`을 걸었다. 즉 **개별 조작을 묶는 것이
협조적 상한을 안전하게 만드는 기제**였다. 구멍은 그 기제가 닿지 않는 호출이다.

## 닿지 않는 호출 — 22곳

Playwright의 `setDefaultTimeout`은 액션·내비게이션·대기 API에만 적용된다. 다음 둘은 **타임아웃
인자 자체가 없다**:

| API | 사이트 수 | 비고 |
|---|---|---|
| `page.evaluate` · `handle.evaluate` · `frame.evaluateHandle` | **18** | 페이지 JS가 스핀하면 영영 반환 안 함 |
| `cdpSession.send` | **4** | 렌더러가 막히면 응답이 오지 않음 |

전부 `observe_interactions.pw.js` 한 파일 안이다.

가장 유력한 정지 지점은 `waitStable`(`:1869`)이다. in-page Promise가 `setTimeout(finish, max)`로
**자기 상한을 갖지만**, 그 타이머는 페이지 JS 루프가 살아 있어야 돈다. 렌더러가 스핀하면
자기 상한도 안 돌고 `page.evaluate`도 안 돌아온다 — 이중으로 막힌다.

다만 **정확히 어느 사이트였는지는 확정하지 않는다.** 그게 이 진단의 요점이다(아래).

## 설계 — 사이트를 열거해 막지 않는다. 보증을 한 지점에 둔다

v1.1.17에서 배운 것과 같은 모양이다: **거부 목록은 완전할 수 없다.** «막힐 수 있는 await를 전부
찾아 고친다»는 접근은 다음 편집 한 줄로 다시 열린다.

세 겹으로 간다.

### ① `withDeadline()` — 22곳을 묶는다

`Promise.race`로 `OPERATION_TIMEOUT_MS` 초과 시 거부한다. 초과는 **기존 경로 그대로**
«조작 예외 → 그 step failed → 탐색 계속»이 된다(`:38-41`이 이미 규정한 동작). 새 의미를
만들지 않는 것이 핵심이다.

### ② 하드 워치독 — 종료를 보증한다

`maxMinutes + 유예` 시점에 프로세스를 **반드시** 끝낸다. 단 **문서를 쓰지 않는다** —
stderr에 진단을 내고 `exit 1`이다.

문서를 쓰지 않는 이유가 중요하다. 워치독이 도는 시점에 다른 async 작업이 `run.steps`를
덧붙이거나 캡처 PNG를 flush 중일 수 있다. 그 상태로 문서를 쓰면 **sha가 실물과 어긋난 문서**가
나오고, 그건 «막힌 것»보다 나쁘다 — 막힘은 보이지만 어긋난 문서는 조용히 통과한다.
`exit 1`은 계약상 이미 «미실행»이고 백스톱이 통과로 세지 않는다.

### ③ 정적 검사 — 다시 열리지 않게 한다

드라이버에서 `.evaluate(`·`.evaluateHandle(`·`.send(`가 `withDeadline`으로 감싸이지 않은 채
나타나면 픽스처가 red다. 원장이 «지우면 길이 닫힌다»로 자기집행이듯, 이것도 **기제로** 지킨다.

## 범위 밖

«동질 집합 표본 갈음» 규칙(메뉴 항목 150개 중 하나를 눌러보면 나머지를 면제)은 별건이다.
hyun이 제기했고(«그걸 왜 다클릭해 하나만 클릭해서 어떻게 변하는지 보면되는거 아니야?») 타당하나,
승인 가능한 예외 행 종류를 새로 만드는 설계라 이번 수리와 섞지 않는다.
A8의 `scope.md`에 «표본 규칙 부재 때문에 미검증으로 남긴다»가 기록되므로 근거는 보존된다.

---

# 진단 2 — 루트 셀렉터와 크롭 규칙이 서로를 막는다 (같은 배치)

## 실증

A8이 v2 관찰을 조립하다 막혔다. 10 case 전부 같은 발견:

```
cases[…].interactions(…).content_crop: 루트 크롭 390x877이 case viewport [390, 844]와 다르다
```

## 원인 — 두 규칙이 동시에 만족될 수 없다

| 자리 | 요구 |
|---|---|
| `check_design_evidence.py:777-780` | `root.selector` == `[data-screen-label="<label>"]` (동등) |
| `:765-767` | `content_crop{w,h}` == `case.viewport` = `[390, 844]` |

A8의 design-ref 사본을 띄워 라벨 루트를 세 뷰포트에서 쟀다:

```
viewport 390x844   →  root rect {x:0,   y:40, w:390, h:877}
viewport 560x1040  →  root rect {x:85,  y:40, w:390, h:877}
viewport 768x1024  →  root rect {x:189, y:40, w:390, h:877}
```

**항상 877이다.** 뷰포트 문제가 아니다 — 내가 처음 세운 «캔버스 뷰포트로 다시 돌려라» 가설을
이 측정이 기각했다(A8의 20분짜리 재관찰을 한 번 막았다).

구조:
```
[data-screen-label="관계인"]      390x877  y=40    ← --crop-root 가 잡는 것
  └ <span data-dc-tpl="16">      19px             "관계인 · 설정 › 사주"  ← 디자인 툴 이름표
  └ … > *:nth-child(2) > div     390x844  y=73    ← 진짜 AppFrame
```

즉 디자인 툴이 라벨 요소 **안에** 화면 이름표를 함께 내보낸다. 루트를 내리면 앞 규칙에,
그대로 두면 뒤 규칙에 걸려 **어떤 행동으로도 v2 관찰을 만들 수 없었다.**

v1 빌드가 390x844로 통과했던 것은 그 빌드가 **legacy v1 관찰**(interactions 없음)이라 이
경로를 타지 않았기 때문이다. v2를 요구하는 순간 벽이 된다.

## 택하지 않은 길 — 캡션 자동 제거

`extract_dc.py:15`·`:84`가 이미 선을 그어 뒀다:

> explicit_frames (only root/direct-child fixed px sizes; **no inferred viewport or
> chrome classification**) · source frames are evidence, **never inferred chrome**

캡션을 «chrome» 으로 추론해 벗기는 수리는 이 입장을 뒤집는다. 하지 않는다.

## 수리 — 근사를 풀고 진짜 보증을 남긴다

`_anchored_root(selector, expected)`: 루트는 선언된 화면**이거나 그 안으로 내려간** 셀렉터면
된다(`rest[0] in ' >+~'`). 프레임은 **에이전트가 명시**하고, 검사기는 앵커 여부만 본다.

완화가 안전한 이유가 따로 있다 — **좁게 내려가 대상을 숨기는 우회는 이 규칙이 아니라
`outside_root.count > 0`이 막는다**(`:680-685` · 선언 유무와 무관한 결함). 그게 원래 보증이고
셀렉터 동등은 그 근사였다. 근사를 풀고 보증을 남긴 것이지 문을 연 것이 아니다.

실측으로 확인: 캡션 `<span>`은 `role·onclick·tabindex` 없고 `cursor:auto`라 조작 대상이
아니다 → 루트를 844 프레임으로 내려도 `outside_root.count`는 0이다.

## 시험

- `_anchored_root` 단위 9종(동등·공백/자식/클래스 후손 통과 · `[…]x`·`div […]`·다른 라벨·
  `None`·비문자열 거부)
- `test_interaction_evidence`에 회귀 2건 추가(후손 3종 통과 · 비앵커 3종 거부)
- 기존 40+32 테스트 무손상 · `run_fixtures` 17파일 0실패 · Codex byte 동일
