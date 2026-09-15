# 적대 검토 D — v3의 원장 기계(§2)와 천장(§3)이 코드에 닿는가 (2026-09-15)

대상: `workspace/design/2026-09-15-web-gate-hardwall.md` **v3** · 담당 축 **§1·§2·§3·§7·§9·§10**
선행: `rv-A`(B3·M5·m4) · `rv-B`(B6·M8·m5) · `rv-C`(B5·M7·m3) — 중복 지적 없음.
표기: **[실측]** = 이 검토에서 명령을 실행해 얻은 결과 · **[확인]** = 코드·실물 파일 직독.
정본 코드: `/Users/hyun/Desktop/dddjango/dddjango-web/scripts/`. A8은 읽기 전용 조회·실행만(쓰기 0),
파괴적 실험은 scratchpad 사본에서 수행했다.

등급: **BLOCKER 7 · MAJOR 7 · MINOR 3**

---

### [BLOCKER] §3의 거부 부류가 A8의 발견 13건을 **전부** 거부한다 — 대상 빌드는 v3로도 열리지 않는다

**무엇이 틀렸나.** 이번 수리의 합격 기준 3번(«A8이 … inputs exit 0으로 진행 가능해진다», §8)이 성립하지 않는다.
§2의 원장은 A8에서 **단 한 행도 등재할 수 없다.**

**근거** [실측] — 실제 대상 빌드에서 읽기 전용 실행:

```
$ python3 dddjango-web/scripts/check_design_evidence.py \
    --build ~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons \
    --project-root ~/.herdr/worktrees/spring_dream_server/a8 --phase inputs        → exit 2
cases[0..11].source_observation: interaction evidence required (version 2 with interactions)   12건
coverage_review: reviewed-input does not match current source/cases/observations                1건
$ … --phase prepare                                                                 → exit 2 (같은 12건)
```

§3 표에 대입하면:

| 발견 | 건수 | §3 처분 |
|---|---|---|
| `interaction evidence required (version 2 with interactions)` | 12 | **거부**(1행) |
| `coverage_review: … does not match` | 1 | **거부**(3행) |
| **등재 가능** | **0** | — |

유일한 예외 `--reason no_observable_surface`도 닫혀 있다 [실측]:
`build-state.json.has_design_screen = true` · `screen-meta.json`은 `source_sha256=cf2fe348…`(`.dc.html` 출처)로
이미지·PDF가 아니다. 두 기계 조건 모두 불성립.

**그리고 남은 1건은 구조적으로 닫을 수 없다.** `coverage_review` 발견을 닫으려면 `coverage-review.md`에
`reviewed-input: <review_digest>`를 새로 적어야 하고, `review_digest`를 얻는 유일한 출구는 `--phase prepare`의
stdout이다(`check_design_evidence.py:1408-1409` · `commands/dddjango-web.md:147`) [확인].
그런데 §1 표는 `prepare`를 «원장 적용 안 함»으로 못박았고, prepare는 같은 `validate_inputs`를 지나므로
12건이 그대로 나 exit 2다 [실측]. **§1이 prepare를 닫고 §3이 coverage_review를 거부하므로 두 문이 서로를 막는다.**

§1 표의 «`prepare` — 원장 대상 발견이 없다»는 서술 자체가 사실과 다르다 — prepare와 inputs의 발견 집합은
`require_review` 한 항목만 다르다(`check_design_evidence.py:1403`) [확인].

**수정 방향** ① §3의 1행을 «관찰 문서가 v2가 아니다»가 아니라 «관찰을 시도한 기록조차 없다»로 좁히고
(재동결 journal·드라이버 exit 기록을 기계 조건으로), ② `prepare`에도 원장을 적용하거나 `review_digest`를
발견과 무관하게 항상 출력하는 별도 출구를 두어야 한다. 지금 설계로 A8은 **열리지 않는다.**

---

### [BLOCKER] §2ⓔ의 «집행 지점 단 한 곳»이 `backstop.py`를 덮지 않는다 — G2 직전·마무리 벽은 그대로 선다

**무엇이 틀렸나.** §2ⓔ는 «`check_design_evidence.py:main()`의 `except Defects` 한 자리 … 이 검사기의 모든 발견이
같은 문을 쓴다»고 적는다. 그런데 이 검사기의 발견을 사용자에게 내는 **두 번째 소비자**가 있고,
그쪽은 `main()`을 지나지 않는다.

**근거** [확인]
- `backstop.py:30` — `from check_design_evidence import Defects, implementation_digest, validate_inputs, validate_visual`.
- `backstop.py:298-307` — `validate_inputs(build, root, legacy_v1=legacy_v1)`를 **인프로세스로 직접** 부르고
  `except Defects`에서 `design_defects.extend(...)` → `:319-320` `[DESIGN] BLOCKER` 출력 → `:330` `return 2`.
  **`main()`도, 그 `except Defects`도 지나지 않는다.**
- §7 배선표의 `backstop.py` 행은 «원장 notice 1줄 · `_discarded-` 접두 제외»뿐 — `partition_by_ledger`가 없다.

**실측** — scratchpad 사본에서 마무리 판형 그대로 실행:

```
$ python3 dddjango-web/scripts/backstop.py <사본 루트> --design-build <사본 빌드>   → exit 2
[DESIGN] BLOCKER — …: cases[0..11].source_observation: interaction evidence required …   12건
[DESIGN] BLOCKER — …: coverage_review: reviewed-input does not match …                    1건
[backstop] 검사 26종 — blocker 18건 (구조 3 · 시안 15)
```

이 명령은 `commands/dddjango-web.md:186`(G2 배너 직전)과 `:191`(마무리)에서 **문자 그대로 같은 형태로** 두 번 돈다.
즉 원장으로 `--phase inputs`를 exit 0으로 만들어도 **G2와 마무리는 원장을 모른 채 같은 발견으로 exit 2를 낸다.**
§2ⓔ가 주장하는 «벽이 한 칸 뒤로 밀리는 것이 구조적으로 불가능»은 참이 아니다 — 벽은 검사기에서 backstop으로
정확히 한 칸 밀린다.

**수정 방향** 원장 조회를 `main()`이 아니라 **`validate_inputs`가 발견을 확정하는 자리**(`:1255-1256`
`raise Defects(issues)` 직전)에 두어야 두 소비자가 같은 문을 쓴다. 그러면 §2ⓔ의 의사코드는 파기된다 —
설계의 집행 지점 선택 자체가 틀렸다.

---

### [BLOCKER] 원장 경유 exit 0은 두 digest를 못 내고 `validate_visual`을 **통째로 건너뛴다** — 새 하드월과 새 마스터키를 동시에 만든다

**무엇이 틀렸나.** `Defects`는 `validate_inputs` 안에서 던져지고, `run()`은 그 자리에서 중단된다.
그래서 §2ⓔ의 `except Defects` 핸들러에는 **`spec`도 `input_digest`도 없다.** 설계는 대신
`ledger_result(build, phase)`를 찍고 0을 반환한다. 결과는 두 가지다.

**근거** [확인] `check_design_evidence.py`
```
1403    spec, input_value, items = validate_inputs(...)        ← 여기서 raise
1410    result = {'input_digest': input_value}                 ← 도달 못 함
1412        result['implementation_digest'] = implementation_digest(project, spec)
1413    if not args.fingerprint and args.phase == 'visual':
1414        validate_visual(build, project, spec, input_value, result['implementation_digest'])
1256    (validate_inputs) raise Defects(issues)   ← return 문보다 앞이다
```

**① 새 하드월** — `commands/dddjango-web.md:184`는 «`--phase visual --fingerprint`가 출력한 **두 digest**를
사용해 Coordinator가 `visual-evidence.json`을 작성한다»고 규정한다 [확인].
원장 경로에서는 그 두 값이 출력되지 않으므로 `visual-evidence.json`을 **쓸 수 없다**. 그리고 그 파일이
없으면 `validate_visual`은 `raise Defects(['visual-evidence.json: unreadable …'])`(`:1288`)다.
즉 원장으로 G0을 통과한 빌드는 **G2를 영구히 통과하지 못한다** — 사용자 지시가 금지한 «어떤 행동으로도
못 여는 상태»를 설계가 새로 만든다.

**② 새 마스터키** — `--phase visual`(fingerprint 없이)에서도 `validate_visual`이 **한 번도 실행되지 않는다.**
원장 행 하나만 있으면 case 집합 동일성(`:1305`)·캡처 하드링크 재사용 금지(`:1324-1325`)·`result: pass`
요구(`:1328`)·media 실측(`:1330`)이 **전량 무검증 통과**한다. §1 표의 «`visual` — 마무리 + 낙인»은
낙인을 얻는 대신 시각 검증 전체를 잃는다.

**수정 방향** 위 BLOCKER 2의 처방과 같다 — 원장은 `Defects`를 던지기 **전에** issues를 거르는 자리에 있어야 한다.
그래야 `validate_inputs`가 정상 return 하고 digest 사슬·`validate_visual`이 살아 있다.

---

### [BLOCKER] 한 줄짜리 마스터키 — `design-input.json: invalid top-level fields` 하나를 등재하면 검사기가 아무것도 검사하지 않고 exit 0을 낸다

**무엇이 틀렸나.** `validate_inputs`에는 issues를 모으지 않고 **즉시 `raise Defects`** 하는 조기 이탈이 두 곳 있다
(`:1080-1081` unreadable · `:1084-1085` invalid top-level fields). 이 둘은 `Defects`이므로 §2ⓔ의 문을 지나고,
§3의 거부 목록에는 없다. 그리고 이 raise는 **다른 모든 검사보다 앞에 있다.**

**근거** [실측] — scratchpad 사본의 `design-input.json`에 최상위 키 `"_note": 1` 하나를 넣었다:

```
before:  발견 13건 (12 case + coverage_review)
after :  [design-evidence] defect: design-input.json: invalid top-level fields      ← 발견 1건
```

이 한 줄을 등재하면:
- **정규화 키가 영구 안정**하다 — 메시지에 숫자도 따옴표 목록도 없다.
- **§2ⓒ 천장이 없다** — 정수열이 빈 리스트라 «규모가 커지면 무효»가 발동할 수 없다.
- **§2ⓓ는 통과한다** — `quote`는 사용자 승인 원문 아무거나, 앵커는 실재하는 것 아무거나(아래 BLOCKER 7).
- 그 뒤 `design-input.json`의 내용이 무엇이든 검사기는 **단 한 줄도 검사하지 않고** exit 0을 낸다.

즉 «가장 적은 노동의 경로»는 관찰도 재동결도 아니라 **JSON에 쓰레기 키 하나를 넣고 원장 1행을 등재하는 것**이다.
비용은 편집 1회 + `ledger.py add` 1회. §10의 «사용자가 전부 승인하면 전부 열린다»가 아니라
**«사용자가 한 번 승인하면 전부 열리고, 그 승인은 무엇이 열리는지 말하지 않는다»**가 된다.

**수정 방향** 조기 `raise Defects` 두 자리는 **원장 대상에서 제외**(§3 거부 부류에 추가)하고,
더 근본적으로 «이 발견이 다른 검사를 단락시키는가»를 원장 등재 가능성의 판정 조건으로 삼아야 한다.

---

### [BLOCKER] §2ⓒ의 «규모»는 규모가 아니다 — 실측 정수열 28개 중 24개가 hex target id 파편이다

**무엇이 틀렸나.** §2ⓒ는 «메시지에서 뽑은 정수열의 각 자리가 승인 규모 이하일 때만 등재로 인정»한다.
실제 메시지의 정수열이 무엇인지 재보면, 그것은 규모가 아니라 **식별자 파편**이다.

**근거** [실측] — A8 재동결 staging의 실제 v2 관찰 문서
(`_refreeze-20260915-222208/captures/related-390x844-interactions.json`, targets 46 · steps 118)에
검사기 함수 `_check_residual`을 그대로 적용해 실제 메시지를 만들었다:

```
cases[related/form-step2-solar].interactions(captures/related-390x844-interactions.json):
partial(caps_hit=max_steps) 수집인데 잔여 8건 — ('19248d5ab91e', 'click', None), ('35110ac6be4a', …

정수열: ['2','390','844','8','19248','5','91','35110','6','4','4','6856','41','1','566601','61',
        '5','3','3','1151','7179592','4','5','73','8','70','19','05369619680']   ← 28개
```

- 진짜 규모는 **`8`(잔여 건수) 단 하나**다. `2`는 case id `form-step2-solar`의 2, `390`·`844`는 viewport,
  나머지 24개는 `('19248d5ab91e', …)` 같은 **hex target id를 숫자 조각으로 자른 것**이다.
- `shown`은 `remaining[:20]`(`check_design_evidence.py:969-971`)이므로 **잔여 단위를 하나만 닫아도**
  표시되는 20개의 구성이 바뀌고 정수열 전체가 바뀐다 — 길이도 바뀐다. 정직한 부분 수리가
  **매번 원장 행을 무효화**한다.
- 반대 방향은 더 나쁘다. A8 자신의 기록이 이렇게 적는다 [실측, `build-state.json.dropdown_rebuild_decision.blocker`]:
  «`--resume`은 캐스케이드 재발견으로 **잔여 증가(88→163 targets)**». 즉 **관찰을 이으면 규모가 커져 원장이 무효가
  되고, 8분에서 끊으면 규모가 작아 원장이 유효하다.** §2ⓒ는 rv-A B1(«천장이 없다»)의 유일한 답인데,
  천장이 아니라 **«더 얕게 관찰하라»는 인센티브**다.
- 그리고 승인 시점의 정수열은 **에이전트가 제어하는 파일 상태에서 나온다** — `ledger.py add`는 그 순간의
  디스크를 검사할 뿐이다. 잔여를 일시적으로 부풀린 문서로 `add`한 뒤 되돌리면 천장이 임의로 높아진다.
  천장을 지켜야 할 주체가 천장의 높이를 쓴다.

**수정 방향** 정수열이 아니라 **검사기가 이름 붙여 내보내는 구조화된 규모 값**(예: `_check_residual`이
`{'residual': 8, 'active': 43}`을 함께 내고 원장이 그 키를 읽는다)이어야 한다. 메시지 문자열에서
정수를 긁는 방식은 폐기해야 한다.

---

### [BLOCKER] §2ⓑ의 정규화가 **서로 다른 발견을 한 키로 묶는다** — 승인 1건이 12건을 연다

**무엇이 틀렸나.** §2ⓑ는 «숫자열과 따옴표 안 목록을 지운 뒤 sha256»으로 키를 만든다. 그런데 이 검사기의
발견은 **대상 식별자를 숫자로 표현**한다(`here = f'cases[{index}]'` — `check_design_evidence.py:1194`) [확인].
숫자를 지우면 대상도 지워진다.

**근거** [실측] — 설계의 정규화 규칙을 그대로 구현해 A8의 실제 13건에 적용:

```
A8 실제 13건 → 고유 키 2개
  키 1ab317b5…  ← cases[0..11].source_observation  (12건이 한 키)
  키 b87757df…  ← coverage_review
```

**12개의 서로 다른 case 승인이 한 개의 원장 행으로 덮인다.** `label` 필드에는 승인 당시의 메시지 1건만 남으므로
사용자도, 나중의 리뷰어도 «이 행이 무엇을 덮는지» 알 수 없다.

같은 충돌이 잔여 발견에서도 난다 [실측] — A8의 실제 case id 12개로 잔여 메시지를 만들면
`related/form-step3`과 `related/form-step4`가 **같은 키**가 된다(둘 다 `related/form-step`으로 정규화).

그리고 §2ⓒ의 «이하» 비교가 이 위에 얹히면 판정이 임의가 된다 [실측]:

```
form-step4 승인(magnitude [4,390,844,38,…]) → form-step3 현재 [3,390,844,40,…]
   자리0: 3≤4 ✓   자리3: 40≤38 ✗ → 무효
form-step3 승인(magnitude [3,…,40,…])       → form-step4 현재 [4,…,38,…]
   자리0: 4≤3 ✗ → 무효
cases[11] 승인(magnitude [11,2])            → cases[0..10] 전부 «이하» → 전부 유효
```

**마지막 case를 승인하면 앞의 모든 case가 열린다.** 배열 인덱스를 규모로 취급한 결과다.

**수정 방향** 키는 정규화 문자열이 아니라 **검사기가 발행하는 안정 식별자**(발견 종류 + 대상 키)여야 한다.
지금처럼 메시지를 뭉개면 «같은 벽은 같은 키»(의도)와 «다른 벽은 다른 키»(필수)가 동시에 깨진다.

---

### [BLOCKER] §2ⓓ의 «앵커 절 본문»이 H1이면 **파일 전체**다 — rv-A의 반례가 그대로 통과한다

**무엇이 틀렸나.** §2ⓓ는 «원문이 그 앵커 절 본문 안에 있어야 한다(다음 **동급 이상** 제목 전까지)»로
rv-A B3(««네» 같은 흔한 문자열이 통과한다»)를 막았다고 주장한다(§9의 rv-A 3 처분). 막지 못한다.

**근거** [실측] — A8 실물 `scope.md`(13,144 bytes)의 판형:

```
`# ` 제목 개수: 1              ← 1행 «# 스코프 메모 — A8 web 관계인 화면»
나머지 제목: 전부 ## / ###
인라인 <a id|name>: 0
_anchors() 산출 앵커: 12개 (전부 제목 슬러그)
```

H1이 하나뿐이므로 **«다음 동급 이상 제목»이 존재하지 않는다 → H1 절의 본문 = 파일 전체.**
`scope_ref: scope.md#스코프-메모--a8-web-관계인-화면` 한 줄이면 §2ⓓ는 «파일 어디에든»과 동치가 된다.
rv-A가 반례로 든 바로 그 줄이 그 안에 있다 [실측]:

```
scope.md:20  - 커밋: `git -c core.hooksPath=/dev/null commit` · **push 0**.
```

덧붙여 `_anchors`(`check_design_evidence.py:250-263`)는 제목 슬러그·명시 `{#slug}`·**위치 무관한
`<a id|name="...">`** 세 부류를 한 집합에 담는다 [확인]. 뒤의 두 부류에는 «제목 등급»이 없으므로
«동급 이상 제목 전까지»라는 절단 규칙이 **정의되지 않는다**. 문서 첫 줄에 `<a id="x">` 하나를 두면
같은 방식으로 파일 전체가 절 본문이 된다.

`anchor_sha256`도 여기서는 방어가 아니다 — H1 절의 sha256은 사실상 파일 전체의 해시이므로
이미 존재하는 `spec.scope.sha256` 포인터와 같은 것을 한 번 더 재는 것뿐이다.

**수정 방향** ① 앵커를 **명시 앵커 한 부류로 한정**하고(예: `<a id="evidence-ledger-approval">` 전용),
② H1·최상위 제목은 앵커 대상에서 제외하며, ③ 절 본문 길이 상한(예: 40행)을 두어야 «절 한정»이 의미를 갖는다.

---

### [MAJOR] §3의 거부 목록이 **열거식**이라, 열거되지 않은 신뢰 경계가 기본 개방된다

§3은 세 부류만 적고 나머지는 전부 등재 가능으로 둔다. 실제로 열리는 것들 [확인]:

| 발견 | 위치 | 열리면 무슨 뜻인가 |
|---|---|---|
| `collector: 이 플러그인의 수집기 바이트가 아니다` | `:1006-1010` | 손으로 지은 관찰 문서를 증거로 받는다 — **증거 체계 전체의 신뢰 경계** |
| `source_observation.archive_sha256: stale source archive` | `:1052-1053` | 관찰이 **다른 시안 파일**을 본 것이어도 통과 |
| `source_observation.trace: empty browser evidence` | `:1068-1069` | 브라우저 증거가 빈 파일이어도 통과 |
| `coverage_review: independent review-result: pass required` | `:1253-1254` | **독립 리뷰어의 fail 판정**을 덮는다 |

특히 마지막이 배치가 거꾸로다. §3은 형제 발견인 `coverage_review: … does not match`를 «검토 문서
재생성으로 항상 닫힌다»는 이유로 **거부**하면서, 재생성으로 닫히지 **않는** 판정 발견은 받는다.
기계적으로 닫히는 것은 막고 사람의 판정은 여는 배치다.

**수정 방향** §3을 «거부 목록»이 아니라 **«허용 목록»**으로 뒤집는다 — 원장이 받는 발견 부류를
명시적으로 열거하고(잔여·표면·예외 상한), 나머지는 전부 거부한다. 그래야 새 검사를 추가할 때
자동으로 fail-closed가 된다.

---

### [MAJOR] §3이 `partial`·`caps_hit` 문서의 잔여를 그대로 받는다 — §9의 «rv-A 2 → §3» 처분은 거짓이다

§9는 rv-A BLOCKER 2(«가장 싼 길 = 드라이버 미연결»)를 «§3 — 그 발견은 원장이 안 받는다»로 처분했다.
§3이 거부하는 것은 «관찰 문서가 v2가 아니다» **한 부류**뿐이고, **얕게 끊은 v2 관찰의 잔여는 받는다.**

**근거** [실측] — A8 재동결 staging에 실제로 있는 관찰 문서:

```
partial = True · caps_hit = ['max_steps'] · targets 46 · steps 118 · 잔여 8
메시지: "… partial(caps_hit=max_steps) 수집인데 잔여 8건 — …"
```

이 메시지는 §3의 세 부류 어디에도 걸리지 않는다 → **등재 가능**.
rv-A·rv-C가 두 차례 요구한 «`caps_hit`가 있는 문서는 덮을 수 없다»는 조건이 v3 §3에 **없다** [확인, 설계 원문].
그리고 §2ⓒ가 그 위에 «작아지면 통과»를 얹으므로(위 BLOCKER 5), **끊는 쪽이 등재도 쉽고 천장도 낮다.**

**수정 방향** §3에 «`partial: true` 또는 `caps_hit ≠ []`인 문서에서 나온 발견은 등재 거부» 한 행을 추가한다.
§9의 rv-A 2 처분 칸도 «부분 해소»로 정정해야 한다.

---

### [MAJOR] §3의 `no_observable_surface` 기계 조건 두 개가 **둘 다 평가 불가**다

§3은 «`build-state.json.has_design_screen`이 false이거나, `screen-meta.json`의 시안 출처가 이미지·PDF 계열일 때만»
`add`를 허용한다고 적는다. 두 조건 모두 실제 코드와 어긋난다 [확인].

- **조건 ①** `has_design_screen=false`인 빌드는 애초에 이 게이트의 대상이 아니다 —
  `commands/dddjango-web.md:179` «시안 없는 빌드는 inputs 비적용이다». 즉 이 문은 **문이 필요 없는 빌드에만 열린다.**
- **조건 ②** `screen-meta.json`을 만드는 도구는 저장소 전체에서 `extract_dc.py` 하나뿐이다
  (`scripts/extract_dc.py:337`). **이미지·PDF 경로 빌드에는 이 파일이 아예 없다.**
  게다가 그 파일의 필드는 `title·subtitle·cards·screen_label·explicit_frames·source_sha256`이고
  **«시안 출처» 필드는 존재하지 않는다** [실측, A8 실물].

즉 rv-B B1(«관찰 불가 축에 문이 없다»)에 대한 v3의 답은 **실행될 수 없는 조건문**이다.

**수정 방향** 출처 종류를 `build-state.json` 또는 `design-input.json`의 **명시 필드**로 남기고(재동결 journal에도),
그 값을 기계 조건으로 쓴다. 지금은 조건이 참조하는 사실이 파일에 없다.

---

### [MAJOR] 재동결이 `scope.md`를 폐기하므로 **모든 원장 행이 조용히 무효**가 된다 — 사용자 구속 지시와 정면 충돌

**무엇이 틀렸나.** 사용자의 구속 지시는 «재동결하라고 하고 차이점이 있으면 수정하게 하면 된다»인데,
v3에서 재동결은 원장을 전멸시킨다.

**근거** [확인]
- `refreeze.py:32-36` `FIXED_DISCARD_FILES`에 **`scope.md`가 들어 있다** — 재동결은 scope.md를 폐기하고
  staging의 것으로 갈아 끼운다.
- §2ⓓ는 `anchor_sha256`(앵커 절 본문 해시)이 «절이 나중에 바뀌면 무효»라고 규정한다.
  scope.md가 통째로 교체되므로 바이트가 1비트만 달라도 **전 행이 무효**다.
- `evidence-ledger.json`은 `FIXED_DISCARD_FILES`·`FIXED_DISCARD_TREES`·`preserved_set`(`refreeze.py:157-166`)
  어디에도 없다 — 파일은 **살아남되 근거만 죽는다**. 사용자에게는 «아까 승인한 것이 왜 다시 막히는지»가
  아무 데도 표면화되지 않는다.
- 예외 행에는 이월 규범이 있다(`commands/dddjango-web.md:138` «`approval_quote`·`scope_ref`는 staging
  `scope.md`에서 재사용») — **원장에는 그 규범이 없고** §7 배선표의 `refreeze.py` 행은 §4 ⓐⓑⓒⓓ만 적는다.

rv-B MAJOR가 `evidence_scope`에 대해 같은 축을 지적했으나, v3의 원장은 «파일은 남고 근거만 죽는» 형태라
**조용한 무효화**라는 점이 다르다.

**수정 방향** `journal`에 원장 행을 이월 대상으로 싣고, 재동결 후 `anchor_sha256`를 staging scope.md 기준으로
재봉인하는 절차를 §4와 §7에 함께 적는다. 이월이 부적절하다고 보면, 최소한 «재동결로 N행이 무효화됐다»를
배너 1급 줄로 내야 한다.

---

### [MAJOR] §7 배선표가 Coordinator 규범 **세 곳**을 손대지 않아 원장이 명문 규범과 충돌한다

§7의 `commands/dddjango-web.md` 행은 «배너 1급 줄 · 링 검사 합류 · 패스트트랙 ③ 합류 · `ledger.py` 사용 절차»
네 항목뿐이다. 원장의 지위를 정면으로 부정하는 문장 세 개가 그대로 남는다 [확인].

| 위치 | 원문 | 충돌 |
|---|---|---|
| `commands:72` | defer = «… `interaction_exclusions`가 아니며 **`--phase inputs`를 열지 않는다**» | 원장은 정확히 `--phase inputs`를 여는 새 장치다 |
| `commands:130` | «구현 재진입 … **입력 게이트 exit 2가 그대로 막는다**» | 원장이 exit 0을 내면 이 문장이 거짓이 된다 |
| `commands:152` | «승인 자체·실패 공개·**미검증 수락은 검사 성공이 아니며**» | 원장은 «미검증 수락 = 검사 성공(exit 0)»을 제도화한다 |

이 셋은 런타임 시스템 프롬프트 본문이다. 기계와 산문이 반대를 말하면 에이전트는 통과에 유리한 쪽을 고른다.
(§7이 `agents/design-review-web.md`를 실은 것은 rv-A MAJOR의 지적을 반영한 것으로 보이나, Coordinator 쪽은 비어 있다.)

**수정 방향** 세 문장을 «원장에 등재되지 않은 발견은 …»으로 한정하도록 함께 개정하고 §7 배선표에 명시한다.

---

### [MAJOR] §1의 «`visual` = 마무리 + 낙인»이 호출 지점과 어긋난다 — 낙인 채널이 마무리 경로에 없다

§1 표는 `visual`을 «마무리»로 규정하고 «결과 JSON에 `unverified_ledger` 동봉 — 배너·마무리 보고 1급»이라 적는다.
실제 호출 지점은 다르다 [확인].

- `--phase visual`은 `commands:184`에서 **G2 배너 전 관찰 증거 작성 단계**에 돈다. 마무리가 아니다.
- 마무리(`commands:191`)가 실행하는 것은 **backstop뿐**이고, backstop은 `check_design_evidence.py`의
  CLI를 부르지 않는다(`backstop.py:30` 인프로세스 import) — 따라서 `run()`의 결과 JSON도,
  거기에 실릴 `unverified_ledger`도 **마무리 경로에 도달하지 않는다**.
- 또한 `--phase inputs`/`visual`의 발견 집합은 동일하다(`run():1403`이 phase와 무관하게 같은
  `validate_inputs`를 부른다) — 두 phase는 «다른 판정»이 아니라 **같은 판정의 다른 출력 포장**이다.
  rv-C B1이 요구한 «축»은 여전히 없다. §9의 «rv-C 1 → §1 표가 축이다» 처분은 성립하지 않는다.

**수정 방향** 낙인은 결과 JSON이 아니라 **backstop의 출력**에 있어야 한다(§7의 backstop 행을
«notice 1줄»이 아니라 «미검증 원장 N행 — 종료코드와 무관하게 항상 출력»으로). 그리고 §1 표의
phase 의미 칸을 실제 호출 지점에 맞춰 다시 쓴다.

---

### [MAJOR] §2ⓑ의 `--index`는 **두 실행 사이의 서수**다 — 사용자의 인용이 다른 발견에 붙을 수 있다

§2ⓑ는 «`add`가 스스로 검사기를 실행해 발견 목록을 만든다 … 에이전트가 문자열을 지어낼 자리가 없다»고 적는다.
문자열은 못 짓는다. 그러나 **사용자 승인과 발견의 결속**은 여전히 위조 가능하다.

**근거** [확인]
- 사용자가 보는 목록은 G0 배너(= 직전 검사기 실행의 stderr)이고, `add`가 등재하는 목록은 **`add`가 새로
  돌린 실행**이다. 두 실행 사이에 빌드 파일이 하나라도 바뀌면 목록의 길이와 순서가 바뀐다.
- 발견 순서가 바뀌는 것은 특별한 조작이 아니다 — 위 BLOCKER 4의 실측이 보이듯 **키 하나를 넣으면
  13건이 1건이 된다**. 관찰 문서를 하나 갈아 끼우면 12건이 11건이 되고 그 뒤 인덱스가 전부 한 칸씩 밀린다.
- `add`는 «사용자가 승인한 것이 index N의 발견이 맞는가»를 확인할 채널이 없다. 설계에도 확인 출력 규정이 없다.

**수정 방향** `--index` 대신 **발견 키를 인자로 받는다**(`--key <sha16>`). 배너가 각 발견 옆에 키를 찍고,
사용자가 본 그 키로만 등재한다. 그러면 두 실행 사이의 서수 결속이 사라진다.

---

### [MAJOR] §9의 «rv-C 3 → §6이 rv-B 전수와 1:1» 처분이 거짓이다 — 범위 승인의 근거가 또 어긋난다

§0과 §9는 «§6이 rv-B 전수 표와 1:1»이라고 두 번 적는다. 대조하면 아니다 [확인].

rv-B가 «예»로 판정한 17행 중 §6에 **없는 것 8행**:
`#3`(수집기 sha) · `#8`(`environment_error`) · `#9`(design-input 미지 최상위 필드) · `#21`(staging case v2 부재) ·
`#24`(journal/plan 손상) · `#25`(inputs exit 0 없이 ready 불가) · `#26`(coder 호출마다 inputs exit 0) ·
`#27`(부채 defer 래칫).

반대로 §6에 **새로 들어온 것**: rv-B가 «아니오»로 판정한 잔여 게이트(`:963-975`)·표면 미연결,
그리고 rv-B 표에 없던 `approval_quote` 과허용(`:876-880`)·`coverage_review` 불일치·`refreeze check`·
`_finish`의 `_prev` 삭제.

특히 `#9`는 rv-C가 «이 설계가 스스로 만드는 벽»으로 지목한 행인데 §6에서 여전히 빠져 있다.
v3는 원장 파일을 빌드 폴더에 새로 만들 뿐 `design-input.json`의 최상위 키를 늘리지 않으므로 스큐 위험은
줄었지만, **`ledger.py`가 설치본에 없는 구판에서 «원장 등재»라는 절차 자체가 존재하지 않는다**는 형태로 같은 문제가 남는다.

**수정 방향** §6 표를 rv-B 판정과 실제로 1:1로 다시 맞추고, 각 행에 «포함/제외 + 사유»를 적는다.
사용자에게 «① 16개 전부»의 대상 집합이 또 바뀌었음을 고지해야 한다.

---

### [MINOR] 원장 파일이 어떤 digest 사슬에도 묶이지 않는다

`design-input.json`·`scope.md`·`coverage-review.md`·manifest·관찰 문서는 `canonical_digest`/`review_digest`에
들어가 서로를 봉인한다(`check_design_evidence.py:1096-1102`·`:199`) [확인].
`evidence-ledger.json`은 그 어느 쪽에도 들어가지 않는다 — 고쳐도, 지워도, 다른 검사가 깨지지 않는다.
§2ⓕ의 «기록과 통행권이 같은 파일»은 **원장을 검사기가 조회하는 동안에만** 참이고,
파일 자체의 무결성은 아무도 보증하지 않는다. `digest_items`에 `ledger/evidence-ledger.json`을 합류시키면
한 줄로 해소된다.

### [MINOR] §3 표 2행(`usage/error`·`internal error`)은 «거부 부류»가 아니라 `add`에 **도달조차 못 하는** 것이다

exit 1 실행은 `[design-evidence] defect:` 줄을 내지 않는다(`main():1431-1436`) [확인].
`ledger.py add`가 만드는 발견 목록에 처음부터 없으므로 «거부»할 대상이 아니다.
표에 실으면 «이 축도 방어된다»로 읽히지만, 실제로는 **그 축이 설계 밖에 있다**는 뜻이다.
표기를 «원장의 관할 밖 — 별건»으로 바꿔야 한다.

### [MINOR] `environment_error`는 `ValueError` → exit 1이라 §2ⓔ의 문 바깥이고 §6 표에도 없다

`check_design_evidence.py:995-997`은 관찰 문서에 `environment_error`가 실리면 **`raise ValueError`**를 던진다
(주석: «미실행은 결함(2)이 아니라 검사 불가(1)») [확인]. `main()`의 `except (OSError, ValueError)`가 받아 exit 1이다.
이것이 «검사기 본문에서 `except Defects`를 우회해 사용자 대면 벽이 되는» 유일한 자리다(그 외 `raise ValueError`
아홉 자리는 전부 지역 `try`에 잡히거나 인자 검증이다 — `:107·111·154·156·163·166·699·1063·1376` 확인).
rv-B가 `#8`로 센 이 벽은 §6 표에도, §3 거부 부류의 설명에도 정확히 대응되지 않는다.

---

## 가장 싼 길 — v3 배포 후 에이전트가 실제로 갈 경로

1. `--phase inputs` 실행 → 발견 목록을 본다.
2. **`design-input.json`에 최상위 키 하나를 더한다**(`"_note": 1`). 발견이 1건으로 줄어든다 [실측: 13 → 1].
3. 그 1건을 `ledger.py add --index 0 --quote "<scope.md의 아무 10자 이상 줄>" --scope-ref "scope.md#<H1 슬러그>"`로 등재한다.
   - §3 거부 부류에 없다 · 정수열이 비어 §2ⓒ 천장이 없다 · H1 절 본문 = 파일 전체라 §2ⓓ가 통과한다.
4. 이후 `--phase inputs`·`--phase visual`은 **아무것도 검사하지 않고 exit 0**을 낸다.
   `validate_visual`도 실행되지 않는다(위 BLOCKER 3).

총 비용: **JSON 편집 1회 + `ledger.py add` 1회.** 정직한 길의 비용: 재동결 + ≤90분 관찰 사슬 + 독립 검토 + G2 재대조.
정직한 길은 그 위에 벌까지 받는다 — `--resume`으로 관찰을 이으면 잔여가 늘어(88→163 targets, A8 자체 기록)
§2ⓒ가 원장 행을 무효로 만든다.

그러면서 **A8은 열리지 않는다**(BLOCKER 1). 즉 v3는 «정직한 대상 빌드는 여전히 막고, 부정직한 빌드는
두 번의 편집으로 연다». 사용자 구속 지시 «재동결하라고 하고 차이점이 있으면 수정하게 하면 된다»는
충족되지 않고, §2ⓔ는 G2·마무리에 **새 하드월**을 세운다(BLOCKER 2·3).

## §10 «열린 위험»에 대한 답

§10은 «사용자가 전부 승인하면 전부 열린다 — 그게 사용자 지시다 … 방어의 목표는 «사용자 모르게 열리는 것»을
막는 것»이라 적는다. 위 실측이 보이는 것은 그 목표의 **정반대**다.

- 사용자는 «무엇을 승인하는지» 알 수 없다 — 키가 12건을 한 행으로 뭉치고(BLOCKER 6),
  최상위 필드 한 줄이 검사기 전체를 덮는다(BLOCKER 4).
- 사용자는 «승인이 언제 사라지는지» 알 수 없다 — 재동결이 조용히 전 행을 무효화한다(MAJOR 3).
- 사용자는 «무엇이 미검증인지» 마무리에서 듣지 못한다 — 낙인 채널이 마무리 경로에 없다(MAJOR 5).

§10은 «메시지 문구 개정 = 원장 무효 · fail-closed가 옳은 방향»이라고도 적는데, 실제 정규화는
**같은 벽에 여러 키**(`partial(caps_hit=…)` 접두 유무로 갈림)와 **다른 벽에 같은 키**를 동시에 만든다.
fail-closed도 fail-open도 아니라 **무작위**다.

---

<!-- 도구 사용: 워크트리 루트에 `.serena/project.yml`·`graphify-out/graph.json`이 없어 Serena·Graphify 미사용(기본 읽기·검색 도구와 읽기 전용 실행으로 확인). A8 워크트리는 조회·검사기 실행만(쓰기 0), 파괴적 실험은 scratchpad 사본에서 수행. -->
