# rv-G — 설계 v4 적대 검토 (§0 집행 지점 이전 · §1 · §2 원장 · §3 천장 · §9 대조표)

등급: BLOCKER 7 · MAJOR 8 · MINOR 3

대상: `workspace/design/2026-09-15-web-gate-hardwall.md` **v4**
방법: 정본 `dddjango-web/scripts/`를 scratchpad로 복사해 **§0의 삽입을 실제로 구현**하고
(`scratchpad/g/scripts/check_design_evidence.py:1256-1259` + `ledger.py`), A8 사본 빌드
(`scratchpad/g/a8` — `refreeze-repair/a8-copy`의 복제)로 실측했다. **정본은 수정하지 않았다**
(`check_design_evidence.py` sha `c89d6b57…` · `backstop.py` sha `1ea3f69f…` — `git status` 무변경).
원형 `ledger.filter`는 §2ⓑ 정규화·§2ⓒ 규모·§3 거부 2종만 구현한 최소판이다.

---

## 0. 설계가 맞힌 것 — 구현자가 믿어도 되는 것

**①·②·③ §0의 세 주장은 전부 참이다.** 집행 지점을 `validate_inputs`의 `if issues:` 직전으로
옮기면 rv-D B2·B3가 **실제로** 해소된다.

| 주장 | 실측 |
|---|---|
| §0-1 backstop도 같은 문을 지난다 | `backstop.py "$R" --design-build "$B"` → stderr에 `notice(ledger/inputs)` 1줄 · 요약 `blocker 3건 (구조 3 · **시안 0**)` — design evidence 발견 0 |
| §0-2 digest 사슬이 산다 | `--phase visual --fingerprint` → `{"implementation_digest": "139187e7…", "input_digest": "1f264a37…"}` exit 0 |
| §0-3 `validate_visual`이 산다 | 같은 상태 `--phase visual` → `input_digest: stale` · `visual_check: sha256 mismatch` · `visual cases: exact unique design case set required` 3건을 **자기가 냈다** exit 2 |

**④ rv-D B4(`_note`) 공격은 실제로 죽었다.** `design-input.json`에 `"_note": 1`을 넣으면
발견은 `design-input.json: invalid top-level fields` 1건이고, **그 키를 원장에 등재해도 exit 2**다
(`:1086`의 조기 `raise`가 `ledger.filter`보다 앞). 원장으로 열리지 않는다 [실측].

**⑤ §3 천장이 A8 현행 13건을 전부 막는다.** 원장 0행/N행 모두 exit 2 —
12 × `cases[N].source_observation: interaction evidence required (version 2 with interactions)`(§3 1행 거부)
+ 1 × `coverage_review: reviewed-input does not match …`(§3 2행 거부). §8의 «A8은 원장만으로
열리지 않는다»는 참이다 [실측].

**⑥ §2ⓒ의 «첫 일치»에 오판정 메시지는 없다 — rv-D B5는 해소됐다.** `check_design_evidence.py`의
`issues.append` **183개를 전수**로 보면 `(\d+)\s*(건|행|개)`가 성립하는 메시지는 3종뿐이고
(`:672` `{count}개` · `:897` `{len(rows)}행` · `:974` `잔여 {len}건`), **세 종 모두 첫 일치가 곧
의도한 규모**다. `실행`·`manifest 행이 없다`처럼 단위 글자만 들어간 3종은 앞에 정수가 없어
정규식이 안 걸린다 [전수 확인].

**⑦ §2ⓑ의 `cases[N]` 보존이 rv-D B6의 12→1 붕괴를 막는다.**
`cases[3].source_observation: …` vs `cases[7]…` → 키 `9f729c2d…` ≠ `95627cdd…` [실측].

**⑧ §2ⓔ 자기검증의 «비용»은 문제가 아니다.** `--phase inputs` 0.88 / 0.88 / 0.89초,
`--phase visual --fingerprint` 0.91초 — 2회 실행해도 2초 미만이다 [실측 `/usr/bin/time -p`].

**⑨ §2ⓓ-2의 H2+ 요구는 A8에서 성립한다.** `scope.md` H1 1개 · H2+ 11개 [실측].

**⑩ §1의 «prepare에도 원장»은 교착을 실제로 푼다.** 원장 1행으로 `--phase prepare`가 exit 0을
내고 `{"review_digest": "8618ea74…"}`를 준다 [실측]. (다만 그 값이 오염된다 — BLOCKER 3.)

---

### [BLOCKER] §0-4의 «구조적 배제»가 거짓이다 — 한 줄 마스터키가 `issues` 묶음 **안에** 그대로 있다

**무엇이 틀렸나.** §0-4는 «`issues` 묶음이 아닌 조기 `raise` 5곳만 마스터키가 될 수 있고,
그 5곳은 구조적으로 원장 밖이라 열거식 거부 목록이 필요 없다»고 주장한다. 그 추론은
«`issues`에 들어온 것은 전부 **끝까지 검사된** 발견»이라는 전제 위에 서 있다. **그 전제가 거짓이다.**
`validate_inputs`에는 `issues.append` 직후 `continue`/`return`으로 **하위 검사 전체를 건너뛰는**
자리가 10곳 있다(`:1100 :1114 :1119 :1128 :1134 :1141 :1144 :1147 :1152 :1197`), 게다가
`cases`/`manifests`가 빈 목록이면 루프 자체가 돌지 않는다. 즉 **발견 1건이 검사되지 않은
부분트리 전체를 대신한다.** 원장이 그 1건을 지우면 계산조차 된 적 없는 검증이 통째로 사라진다.

**근거 [실측] — A8 사본, `design-input.json`의 `"cases"`를 `[]`로 바꾼 것 하나.**

```
원장 0행 · phase=inputs →  cases: nonempty list required
                           coverage_review: reviewed-input does not match …      (발견 2건)
원장 1행(`cases: nonempty list required`) 등재 후:
  --phase prepare  → exit 0  {"review_digest": "8618ea74f7e9addb…"}
  (그 digest 를 coverage-review.md 의 reviewed-input: 에 기입 — §3 2행이 «항상 닫힌다»고 적은 그 행동)
  --phase inputs   → exit 0  {"input_digest": "1f264a37b662d559…"}
  --phase visual   → exit 0  (visual-evidence.json 의 cases 도 [] 로)
  backstop.py --design-build … → "blocker 3건 (구조 3 · 시안 0)"   ← design evidence 발견 0
```

발견 13건 → **0건**. 원장 **1행**. 사라진 것: 12 case 전량의 `_source_observation`·
`validate_interactions`(`_check_document`·`_check_steps`·`_check_initial`·`_check_served_rows`·
`_check_residual`·`_check_surfaces`·`_check_bindings`·`_check_reached_by`)·`check_media_requirements`·
`archive_dependencies`, 그리고 `require_review` 블록의 `any(collection=='archive')`가 거짓이 되어
**coverage_review 검사 자체**(cases=[] 이면 manifest_records 는 남지만, 12 case가 없으니 검토 대상이 없다).
사용자가 보는 것은 «미검증 원장 1행 — cases: nonempty list required» 한 줄뿐이다.

비교 [실측]: 같은 목표를 다른 단락으로 노리면 더 비싸다 — `manifests: []` 25건 ·
`cases[0]`에 잡키 추가 13건 · `reference_root` 오염 49건. **`cases: []`가 압도적으로 가장 싸다.**

**수정 방향.** ① 원장은 «발견»이 아니라 «검사된 단위»에 걸어야 한다 — 최소한 `validate_inputs`가
**단락 없이 끝까지 돈 실행**에서만 원장을 적용한다(구조 실패가 하나라도 있으면 원장 정지).
② 구체적으로: `issues`를 `structural`(단락을 일으킨 것)과 `finding`(끝까지 검사된 것) 두 목록으로
나누고 `ledger.filter`는 `finding`만 받는다. 위 10곳의 `continue`·`cases/manifests` 빈 목록·
`validate_interactions`의 early `return`이 `structural`이다. ③ 그러면 §0-4의 «열거식 목록 불필요»가
비로소 참이 된다(구조 실패는 형태로 구분되므로).

---

### [BLOCKER] §3 천장이 열거식이라 «관찰을 안 했다»가 **다른 문구로** 그대로 통과한다

**무엇이 틀렸나.** §3 1행은 `… interaction evidence required (version N with interactions)` **하나만**
거부한다. 그런데 `_source_observation`은 **같은 상태**(관찰 미실시)를 최소 4가지 다른 문구로 낸다.
전부 `return None`이라 그 case의 상호작용 검증이 통째로 안 돈다:

| 도달 방법 | 메시지 | §3 거부? |
|---|---|---|
| 관찰 파일 삭제/개명 | `cases[N].source_observation.path: missing path (…)` (`:54`) | **아니오** |
| 관찰 파일 sha 불일치 | `cases[N].source_observation.path: sha256 mismatch` (`:74`) | **아니오** |
| JSON 깨뜨리기 | `cases[N].source_observation: invalid JSON` (`:1040`) | **아니오** |
| 필드 하나 추가 | `cases[N].source_observation: exact version 1 or 2 fields required` (`:1046`) | **아니오** |
| (§3이 겨눈 것) v1 관찰 | `… interaction evidence required …` (`:1049`) | 예 |

**근거 [실측]** — A8 사본에서 `captures/related-list-source-observation.json` **한 개만 옮김**:
```
원장 0행: 13건 · cases[0] = ["cases[0].source_observation.path: missing path ([Errno 2] …)"]
원장 1행(그 키 등재): 12건 · cases[0] = []          ← rejected? False · magnitude None
```
`pointer`의 메시지는 경로가 홑따옴표 안이라 §2ⓑ가 지운다 → 키는 `cases[0].source_observation.path:
missing path ((…))` 한 개. **case당 1행 × 12 = 12행이면 A8 전체가 무관찰로 열린다.**
§3 1행이 지키려던 «드라이버 미연결이 가장 싼 길이 되면 안 된다»(rv-A B2)가 무너진다.
§0-4가 «열거식 거부 목록이 필요 없다(rv-D MAJOR도 같이 해소)»고 선언한 자리에서, 열거식 누락이
그대로 남았다.

**수정 방향.** 거부를 **메시지 문자열**이 아니라 **상태**로 판정한다 — `_source_observation`이
`None`을 반환한 case(= 관찰 증거 없음)와 `validate_interactions`가 early `return`한 문서는
발견 문구와 무관하게 원장 대상에서 제외한다. 이는 위 BLOCKER 1의 `structural` 분리와 같은 수술이다.

---

### [BLOCKER] 원장 경유 exit 0이 `review_digest`와 `input_digest`를 **오염**시킨다 — 독립 검토의 결속이 거짓이 된다

**무엇이 틀렸나.** §1은 «prepare에도 원장을 적용»한다. `prepare`의 반환값은 `review_digest` 하나이고,
그 값은 `digest_items`에서 계산된다. 그런데 위 단락 경로들은 **`digest_items.append`도 함께 건너뛴다**
(`:1156`의 source/ · `:1209`의 reference-capture/ · `_source_observation:1036`의 observation/ 등).
따라서 원장으로 연 `prepare`는 **증거가 빠진 입력 집합**의 digest를 낸다. 그 값이 `coverage-review.md`의
`reviewed-input:`에 박히고, `inputs`에서 같은 축소 집합으로 재계산돼 **일치한다**.
결과: 독립 검토 문서가 «현재 입력 전량을 검토했다»고 기계적으로 결속되지만 실제로는 절반이다.
`canonical_digest(digest_items)`로 만드는 `input_digest`도 같은 오염을 받고, 그것이
`visual-evidence.json`에 박힌다.

**근거 [실측]** — 같은 빌드, `cases`만 달리해 `validate_inputs`를 인프로세스 호출:
```
정상(cases 12): digest_items=49  {design-input 1, evidence 1, manifest 1, source 22,
                                  reference-capture 12, observation 12}  review_digest=3a4521cd…
공격(cases=[]): digest_items=25  {design-input 1, evidence 1, manifest 1, source 22}
                                                                        review_digest=8618ea74…
```
**24개 증거 항목이 결속에서 빠졌고, 출력에는 그 사실을 알리는 값이 하나도 없다**
(`{"review_digest": …}` 외에 항목 수도, 원장 표식도 없다).

**수정 방향.** ① 원장이 한 행이라도 적용된 실행의 `review_digest`/`input_digest`에는 **원장 상태를
섞는다**(예: `canonical_digest(items + [('ledger', 원장 바이트)])`). 그러면 원장을 지우거나 늘리는 순간
digest가 바뀌어 `coverage_review`가 red가 되고, §2ⓕ(«지우면 닫힌다»)가 digest 사슬로도 성립한다.
② `run()`의 `prepare`·`inputs` 결과 JSON에도 `unverified_ledger`를 넣는다(§1은 `visual`에만 넣었다).
③ 원장 행 수와 함께 **`digest_items` 개수**를 결과에 싣는다 — 축소를 사람이 볼 수 있어야 한다.

---

### [BLOCKER] §2ⓑ+ⓒ가 잔여의 «구성»을 못 본다 — 승인 38건 뒤에 **전혀 다른 30건**이 조용히 열린다

**무엇이 틀렸나.** §2ⓑ 표는 «`cases[3] … 잔여 38건` vs `잔여 51건` → 같은 키여야 한다»를 요구한다.
그 요구를 만족시키려면 정규화가 `{shown}`(잔여 단위 튜플 나열)을 **완전히 접어야** 한다.
접는 순간 키에 남는 식별 정보는 `label`(case id + 문서 경로)뿐이고, 남은 방어는 §2ⓒ의 **개수**
하나다. 그런데 §2ⓒ는 «현재 규모 ≤ 승인 규모»만 본다 — **구성이 전부 바뀌어도 수만 작으면 통과한다.**

**근거 [실측]** — §2ⓑ 규칙을 문자 그대로 구현(`scratchpad/g/norm2.py`)해 실제 `:974` 판형에 적용:
```
같은키 364172ec9042be0b  … 잔여 #건 — (…) 외 #건   ← ('t1','click',None) … 38건
같은키 364172ec9042be0b  … 잔여 #건 — (…) 외 #건   ← ('z9','select','A') … 30건  (겹치는 단위 0개)
```
시나리오: 사용자가 «드롭다운 재작성은 다음 슬라이스»라며 잔여 38건을 승인한다. 이후 코더가
드롭다운을 없애고 **완전히 새로운 모달의 미관찰 상호작용 30건**을 만든다 → 키 동일 · 규모 30 ≤ 38
→ **재승인 없이 통과**한다. §10이 «방어의 목표»라고 적은 «사용자 모르게 열리는 것»이 바로 이것이다.

**수정 방향.** 원장 행에 **단위 키 집합의 digest**를 박는다 —
`residual_sha256 = sha256(sorted(_unit_key(*u) for u in remaining))`. 조회 시 «현재 잔여 ⊆ 승인 잔여»면
유효, 새 단위가 하나라도 생기면 무효(fail-closed). `_check_residual`이 이미 `remaining`을 갖고 있으므로
검사기가 발견 줄에 그 digest를 실어 주면 `ledger.py`는 파싱만 하면 된다.

---

### [BLOCKER] §2ⓑ 정규화가 **서로 다른 발견을 한 키로** 묶는 조합이 새로 있다 — v4의 «cases[N] 보존» 수정이 닿지 않는 메시지군

**무엇이 틀렸나.** v4는 rv-D B6을 «`cases[N]` 인덱스 보존»으로 닫았다고 적었다. 그러나 붕괴의
진짜 원인은 인덱스가 아니라 **«따옴표 구간 → …»**이다. 검사기 메시지의 상당수가 식별 정보를
`{x!r}`로 감싸 넣는데(Python `repr`은 홑따옴표), 정규화가 **바로 그 부분만** 지운다.

**근거 [실측]** — 같은 `norm2.py`:

| 메시지군 | 두 발견 | 키 |
|---|---|---|
| `:960` 새 표면 | `새 표면 'dialog-settings'에 …` vs `'dialog-delete'에 …` | **같음** `87b1af4b…` |
| `:1221` archive 의존성 | `dependency absent from manifest: 'img/a.png' in 관계인.dc.html` vs `'img/b.png' in …` | **같음** `91a4eaee…` |
| `:196` manifest 폐포 | 같은 판형(`{reference!r} in {row["local_path"]}`) | **같음** |

`:960`이 특히 나쁘다 — `_check_surfaces`는 **문서 단위**로 돌기 때문에, 원장 1행이 그 관찰 문서의
**현재·미래의 모든 미도달 새 표면**을 연다. «다이얼로그 하나는 다음 슬라이스»라는 승인이
그 뒤에 추가되는 모든 다이얼로그에 자동으로 붙는다.

**수정 방향.** 정규화를 «따옴표 구간 **삭제**»가 아니라 «따옴표 구간 **해시 축약**»으로 바꾼다
(`'…' → ⟨sha8⟩`). 그러면 §2ⓑ 표의 «`partial(caps_hit=…)` 접두 유무 → 달라야»도 그대로 성립하고,
같은 발견의 재실행 안정성도 유지된다. 예외는 §2ⓒ가 다루는 계수와 §2ⓑ가 접기로 정한 잔여 튜플
나열뿐이며, 그 둘은 BLOCKER 4의 `residual_sha256`로 대체한다.

---

### [BLOCKER] `validate_visual`은 원장 밖이다 — visual 발견 전량이 하드월로 남고, §6 #19의 «원장이 대체 채널»은 거짓이다

**무엇이 틀렸나.** §0의 집행 지점은 `validate_inputs:1255` **한 곳**이다. `validate_visual`은 자기
`if issues: raise Defects(issues)`(`:1332`)를 따로 갖고 있고 §7 배선표에 그 줄이 없다. 따라서
**시안 대조 단계의 발견은 원장이 닿지 않는다.** 그런데 §6 #19는 «`visual-evidence.json`에 이탈 칸
없음 | 스키마 | **X — 원장이 대체 채널**»이라고 처분했다.

**근거 [실측]** — `cases=[]`+원장 1행 상태에서 `--phase visual`:
```
[notice(ledger/visual)] 미검증 등재분 — cases: nonempty list required
[defect] input_digest: stale or incorrect
[defect] visual_check: sha256 mismatch
[defect] visual cases: exact unique design case set required          → exit 2
```
원장이 적용된 실행인데도 이 3건은 그대로 남았다. 즉 `visual cases[N].result: pass required`(`:1329`)
— **사용자가 승인한 이탈**이 있어도 `result: "pass"`라고 쓰는 것 말고는 통과 방법이 없다.
«부정직한 길이 가장 싸다»의 정의다. 덧붙여 §0-4의 «조기 `raise` 5곳»도 실제로는 7곳이고
(`grep -n "raise Defects"` → `1082 1086 1266 1273 1277 **1291 1294**`), 빠진 2곳
(`visual-evidence.json: unreadable` · `exact version 1 schema required`)이 바로 이 하드월이다.

**수정 방향.** ① §6 #19를 **X에서 L로** 고치고 `validate_visual:1332` 직전에 같은
`ledger.filter(build, issues, 'visual')`를 넣는다. ② `backstop.py:304`가 `validate_visual`을 직접
부르므로 phase 인자 전달도 함께 배선한다(MAJOR 5). ③ 넣지 않을 거면 §6 #19의 처분 문구를
«별건 — 원장은 닿지 않는다»로 정직하게 고치고, 이탈 칸을 스키마에 여는 것을 별건 목록에 올린다.

---

### [BLOCKER] §2ⓓ가 앵커 **파일**을 못 박지 않았다 — 에이전트가 쓰는 문서의 앵커로 승인을 위조할 수 있다

**무엇이 틀렸나.** §2ⓓ는 «`scope_ref`의 앵커가 실재한다 / H2 이상 / 원문이 그 절 본문 안 /
절 본문 sha256»만 요구한다. **어느 파일인지는 말하지 않는다.** §2ⓔ의 CLI도 `--scope-ref "<경로>#<앵커>"`로
경로를 파라미터로 열어 뒀고, 기존 검사기의 `scope_ref`도 `confined(build, …)`라 **빌드 안 아무 파일**을
받는다(`:883-894`). 그런데 §2ⓖ(«재동결이 `scope.md`를 폐기한다 → 행이 무효가 된다»)와 §2ⓕ는
**scope.md 하나만** 전제하고 서 있다.

**근거 [실측]** — A8 사본 빌드의 `.md` 앵커 전수(`_anchors()` 그대로 호출):

| 문서 | 앵커 | H1 | H2+ | 저자 | `refreeze` FIXED_DISCARD_FILES |
|---|---|---|---|---|---|
| `scope.md` | 12 | 1 | **11** | 사용자/발주 | 폐기·재설치 |
| `design-spec.md` | 51 | 1 | **50** | architect | **없음(무풍)** |
| `visual-check.md` | 11 | 1 | **10** | coder/coordinator | **없음(무풍)** |
| `design-review.md` | 6 | 1 | **5** | reviewer | **없음(무풍)** |
| `coverage-review.md` | 5 | 1 | 4 | reviewer | 폐기·재설치 |

H2+ 앵커 **80개 중 65개가 재동결이 건드리지 않는 에이전트 저작 문서**에 있다.
에이전트는 `design-spec.md`에 H2 절을 하나 더 쓰고 그 안에 «…는 다음 슬라이스로 미룬다»를 적은 뒤
`--scope-ref design-spec.md#…`로 등재하면 된다 — §2ⓓ의 네 조건을 **전부** 만족하고, §2ⓖ의
무효화도 영원히 오지 않는다. §2ⓔ 제목 «위조 불가»가 성립하지 않는다.

**추가로**: `_anchors()`는 `<a id=…>`/`<a name=…>` 인라인 앵커도 수확한다(`:263`). 제목이 아닌
앵커에는 «H2 이상 깊이»도 «절 본문»도 정의되지 않는다 — `ledger.py`가 자체 파서를 가져야 하고
§2ⓓ가 그 규칙을 적지 않았다.

**수정 방향.** ① `scope_ref`의 파일을 **`scope.md`로 고정**한다(한 줄). ② 인라인 `<a id>` 앵커는
`add`가 거부한다(절 경계가 정의되지 않으므로). ③ 같은 앵커·같은 인용을 **두 행 이상이 공유하는 것을
금지**한다 — 현재 §2ⓓ는 인용↔발견 결속이 없어, 사용자 승인 1건이 무관한 발견 N건에 재부착된다
(rv-A B3이 `interaction_exclusions`에서 보인 것과 같은 구조가 원장으로 옮겨 온 것이다).

---

### [MAJOR] §2ⓔ의 «등재 후 재실행 자기검증»은 **동어반복**이라 rv-D의 서수 문제를 닫지 못한다

**무엇이 틀렸나.** §2ⓔ는 «등재 직후 다시 돌려 그 발견이 실제로 사라졌는지 확인하고, 사라지지
않으면 행을 철회한다 — (rv-D MAJOR «`--index`는 두 실행 사이의 서수») 자기 검증으로 닫는다»고 적었다.
그런데 `ledger.filter`는 **방금 등재한 그 메시지에서 뽑은 키**로 매칭한다. 재실행에서 그 발견이
사라지는 것은 **정의상 보장**되며(§3 거부 부류이거나 규모가 그 사이에 커진 경우를 빼면),
확인되는 것은 «filter가 동작한다»뿐이다. rv-D가 겨눈 위험 — **Coordinator가 사용자에게 보여 준 실행**과
`add`의 실행 사이에 발견 집합이 달라져 `--index N`이 다른 발견을 가리키는 것 — 은 재실행으로
탐지되지 않는다. 오히려 «잘못 가리킨 발견이 잘 지워졌다»를 확인해 줄 뿐이다.

**근거 [확인]** — `ledger.filter`의 매칭 키는 `key_of(message)`이고 `add`가 등재하는 키도 같은
함수의 산출이다(§2ⓑ). 두 값이 같으므로 재실행의 결과는 입력과 무관하게 «사라짐»이다. 실측한
BLOCKER 1·2의 공격 전부가 이 자기검증을 **통과**한다.

**수정 방향.** `--index` 대신 **발견 텍스트(또는 그 키)를 인자로 받는다** — `--finding-key <16hex>`.
Coordinator가 사용자에게 제시한 배너에 키를 같이 찍고, `add`는 자기 실행의 발견 중 그 키가
**정확히 하나** 있을 때만 등재한다. 없거나 둘이면 거부한다. 서수가 사라지면 드리프트도 사라진다.

---

### [MAJOR] §2ⓒ의 규모 천장이 **183종 중 3종**에만 적용된다 — 나머지는 무제한·무기한 통행권이다

**무엇이 틀렸나.** §2ⓒ는 «규모가 없는 발견(`magnitude: null`)은 규모 판정 없이 키로만 산다»고
한 줄로 넘긴다. 그 «나머지»가 사실상 전부다.

**근거 [전수 확인]** — `issues.append` 183개 중 `(\d+)\s*(건|행|개)` 판형은 `:672`·`:897`·`:974`
**3종**. 즉 **180종은 `magnitude: null`**이고, §3 천장은 2종만 거부한다. 결과적으로
**≈178종의 발견이 «한 번 승인하면 규모·구성과 무관하게 영구 개방»**이다.
rv-A B1(«천장이 없다 — 미검증 100%도 exit 0»)이 §9에서 «§2ⓒ 규모 + §3»로 처분됐지만,
실측한 BLOCKER 1의 `cases: []`가 정확히 «미검증 100% · magnitude null · exit 0»이다.

**수정 방향.** 규모가 없는 발견에는 **시간 천장**을 건다 — 행에 `expires_at`(예: 등재 후 N일 또는
«다음 재동결까지») 을 필수로 넣고, 만료되면 무효(fail-closed). 사용자 승인의 유효 범위를
문서가 아니라 **행**이 스스로 말하게 한다. 또는 §2ⓒ를 «규모 없는 발견은 원장이 받지 않는다»로
뒤집고, 받아야 하는 부류만 검사기 메시지에 계수를 넣는다.

---

### [MAJOR] §3이 `coverage_review: independent review-result: pass required`를 연다 — 독립 검토의 «fail»이 원장 1행으로 꺼진다

**무엇이 틀렸나.** §3은 `coverage_review: … does not match`(기계적 불일치)를 **거부**하면서
`coverage_review: independent review-result: pass required`(`:1254` — 검토자의 실질 판정)는
거부 목록에 넣지 않았다. 비대칭이 거꾸로다: 전자는 §3 스스로 «재생성으로 항상 닫힌다»고 적었으니
거부해도 손해가 없지만, 후자는 **독립 검토자가 «불합격»이라고 쓴 사실 자체**다.

**근거 [실측]** — A8 사본의 `coverage-review.md`를 `review-result: fail`로 바꾸고 두 행을 등재:
```
[notice(ledger/inputs)] 미검증 등재분 — coverage_review: independent review-result: pass required
[defect] coverage_review: reviewed-input does not match …            ← §3이 거부(의도대로)
```
즉 **실질 판정만 열렸다.**

**수정 방향.** `:1254`를 §3 거부 목록의 3행으로 올린다. 검토자의 판정을 뒤집는 것은 «미검증 승인»이
아니라 «검토 자체의 무효화»이고, 그 길은 «검토를 다시 받는다»뿐이어야 한다.

---

### [MAJOR] §6 #4 «`approval_quote` 미검증 통과 | L | §2ⓓ가 오히려 조인다»는 거짓이다

**무엇이 틀렸나.** §6 #4는 `:876-880`(`interaction_exclusions[].approval_quote` 검증)을 **L**(원장이 연다)로
처분하면서 «§2ⓓ가 오히려 조인다»고 적었다. 두 진술은 양립하지 않는다. `approval_quote: scope 원문에
없다`가 원장으로 열리면 **검사기의 승인 원문 대조 자체가 꺼진다.** 그리고 그 원장 행을 여는 조건은
§2ⓓ뿐인데, §2ⓓ는 (BLOCKER 7대로) 빌드 안 아무 문서의 H2+ 절이면 된다. 순효과는 **완화**다:
행 단위로 걸려 있던 «사용자 원문 실재» 요구가 «빌드 안 어딘가의 절 본문» 요구로 내려간다.
`:894`(`scope_ref: 앵커가 실제로 없다`)도 같은 처지다.

**근거 [확인]** `:876-880`·`:883-894`가 `issues`에 들어가므로 §0의 집행 지점이 전부 받는다.
§6 #4가 스스로 **L**이라고 적었다.

**수정 방향.** `interaction_exclusions`의 `approval_quote`·`scope_ref` 검증 실패는 §3 거부 부류로
올린다(원장과 같은 신뢰 기제를 검사하는 검사이므로 원장으로 열면 순환이다).

---

### [MAJOR] §7 배선표가 `backstop.py`에 `phase`를 주지 않는다 — 게이트 간 판정이 갈릴 수 있다

**무엇이 틀렸나.** `backstop.py:301`은 `validate_inputs(build, root, legacy_v1=legacy_v1)`로
**phase 없이** 호출하고, 이어서 `implementation_digest`·`validate_visual`을 직접 부른다(`:303-304`).
§2ⓔ의 `add`는 `--phase <prepare|inputs|visual>`을 **필수**로 받는다. 행이 phase를 갖고 조회에서
걸러진다면 backstop은 어떤 phase로 조회해야 하는지 정의되지 않았고, 걸러지지 않는다면 §2ⓔ의
`--phase`는 무엇을 위한 값인지 정의되지 않았다. §7의 backstop 행은 «원장 notice 1줄 · 잔존물 3가지»뿐이다.

**근거 [실측]** 원형에서 기본값 `phase='inputs'`를 주어야 backstop이 원장을 지났다
(그 값 없이는 `TypeError`). 설계에는 그 결정이 없다.

**수정 방향.** ① 행은 phase를 **기록만** 하고 조회에서는 쓰지 않는다(= `add`의 `--phase`는 «어느
명령으로 발견을 재현했는가»의 감사 정보)라고 §2ⓔ에 명시하거나, ② backstop 호출에
`phase='inputs'`/`'visual'`을 배선하고 §7에 적는다. 어느 쪽이든 **적어야** 한다 —
지금은 구현자가 고르면 두 게이트의 판정이 갈린다.

---

### [MAJOR] §0-4의 «조기 `raise` 5곳»이 실제로는 7곳이다 — 누락된 2곳이 곧 visual 하드월이다

**근거 [실측]** `grep -n "raise Defects" check_design_evidence.py` →
`1082 · 1086 · 1259(묶음) · 1266 · 1273 · 1277 · **1291** · **1294** · 1335(묶음)`.
§0-4가 센 5곳은 `1082·1086·1266·1273·1277`이고, `1291`(`visual-evidence.json: unreadable`)과
`1294`(`exact version 1 schema required`)가 빠졌다. 이 둘은 `validate_visual` 안이라
**BLOCKER 6과 같은 하드월**이다.

**수정 방향.** §0-4의 표를 7곳으로 고치고, `1291`·`1294`를 §6의 별건 목록(또는 BLOCKER 6의
`validate_visual` 배선)으로 옮긴다.

---

### [MAJOR] §2ⓓ의 «H2 이상 깊이»·«절 본문»이 `_anchors()`의 수확 범위와 맞지 않는다

**무엇이 틀렸나.** §2ⓓ는 «앵커가 실재한다»를 기존 판정(`_anchors()`)으로 하겠다는 뜻으로 읽히지만,
`_anchors()`는 ⓐ `#{1,6}` 제목 슬러그 ⓑ `{#명시앵커}` ⓒ `<a id=|name=>` 세 종류를 **한 집합으로
평탄화**한다(`:250-265`). ⓑ·ⓒ에는 «깊이»가 없고, ⓒ에는 «절 본문»의 시작·끝이 없다.
§2ⓓ-2/-3/-4는 세 경우 각각에 대해 답이 달라야 하는데 설계는 하나도 적지 않았다.

**근거 [실측]** A8 `scope.md`: 제목 줄 12개 = H1 1 + H2+ 11이고 `_anchors()` 산출도 12개
(인라인 `<a id>`가 0개라 우연히 일치한다). `motion-notes.md`는 H2+ 0개인데 앵커 1개(H1 슬러그뿐) —
§2ⓓ-2대로면 그 문서에는 등재 가능한 앵커가 **하나도 없다**. 설계는 이 상태를 언급하지 않는다.

**수정 방향.** §2ⓓ에 «앵커는 `##`~`######` **제목 줄**에서만 인정한다(명시 `{#…}` 포함,
인라인 `<a id>` 제외)»를 명문화하고, 절 본문의 끝을 «`#` 개수가 그 제목 **이하**인 다음 제목 줄
직전»으로 숫자로 못 박는다 — §2ⓓ-3의 «같은 수준 이상»은 H2 절 안의 H3를 본문에 포함하는지가
읽는 방향에 따라 갈린다.

---

### [MAJOR] §9 대조표의 거짓 행 — 29건 중 최소 5행

| 출처 | v4 처분 | 판정 |
|---|---|---|
| rv-A 1 «천장 없음 — 미검증 100%도 exit 0» | §2ⓒ 규모 + §3 | **거짓** — `cases: []` + 1행으로 미검증 100% exit 0 [실측]. 규모 천장은 183종 중 3종에만 적용 |
| rv-A 2 «가장 싼 길 = 부정직» | §3 1행 | **거짓** — §3은 문구 하나만 막고, 관찰 파일 1개 삭제가 더 싸게 같은 상태를 만든다 [실측] |
| rv-A 3 «`approval_quote`가 승인을 식별 못 한다» | §2ⓓ | **부분 거짓** — §2ⓓ가 «절 안»은 걸었으나 **인용↔발견 결속**도 **파일 고정**도 없다. §6 #4는 그 검증을 오히려 원장으로 연다 |
| rv-D 4 «한 줄 마스터키» | §0-4 구조적 배제 | **거짓** — 마스터키가 `issues` 묶음 안에 그대로 있다 [실측] |
| rv-D 6 «12건이 한 키» | §2ⓑ [실측] | **부분 거짓** — `cases[N]`군은 고쳐졌으나 `:960`·`:1221`·`:196`에서 같은 붕괴가 새로 성립 [실측] |

(참인 행도 확인했다: rv-B 6 → §0 [실측 — 상한 `:897`·잔여 `:974` 둘 다 `issues` 묶음],
rv-D 2·3 → §0 [실측], rv-D 5 → §2ⓒ [전수 확인], rv-D 7 → §2ⓓ-2.)

**수정 방향.** §9는 «처분»이 아니라 «처분 + 처분이 성립하는 조건»을 적어야 한다. 위 5행은
BLOCKER 1·2·5·7과 MAJOR 4의 수리가 들어간 뒤에만 참이 된다.

---

### [MINOR] §2 예시와 §2ⓑ 실측표의 메시지 판형이 실제 검사기 출력과 다르다

§2ⓐ·ⓑ는 `cases[3].interactions: 잔여 38건 — …`을 쓴다. 실제 `_check_residual`의 `label`은
`cases[{case.get("id")}].interactions({path})`이다(`:981`+`:986`) — **인덱스가 아니라 case id이고,
문서 경로가 붙는다.** 또 `_check_residual`·`_check_surfaces`는 **문서당 한 번**만 돌아
(`:999` `if all(existing != name …)` → `:1011-1012`) 그 문서를 처음 참조한 case의 id가 붙는다.
구현자가 §2ⓑ 표를 그대로 회귀 픽스처로 옮기면 «실측 검증 완료»가 재현되지 않는다.

**수정 방향.** §2ⓐ·ⓑ의 예시를 실제 출력에서 복사한 문자열로 교체한다.

---

### [MINOR] §8-4(«원장만 토글»)는 A8에서 측정할 수 없다 — 분리 측정이 합성 빌드 전용이다

A8 현행 13건이 전부 §3 거부이므로 «관찰을 바꾸지 않고 원장만 토글»하면 **항상 exit 2**다 [실측].
설계도 «합성 빌드(`test_ledger.py`)로 측정한다»고 적었으므로 모순은 아니지만, 그 결과
**«A8에 닿는다»의 증명이 전부 배포 후(§8 마지막 절)로 미뤄진다** — §8 표의 5개 기준 중 어느 것도
A8이 실제로 열리는지를 red/green으로 말하지 못한다.

**수정 방향.** §8에 «A8 재검증 전까지 이 수리는 미검증»을 명시하고, 합성 빌드 픽스처가
**BLOCKER 1·2의 공격 3종**(`cases: []` · 관찰 파일 삭제 · manifest 단락)을 red 단언으로 포함하게 한다.

---

### [MINOR] 잔여 키가 20건 경계에서 바뀐다

`_check_residual`은 `len(remaining) > 20`일 때만 `외 {N}건`을 덧붙인다(`:969-972`). 따라서
잔여 21건과 20건은 정규화 후에도 다른 키다(`… (…) 외 #건` vs `… (…)`). 승인 후 잔여가 그 경계를
넘나들면 행이 죽었다 살아난다. fail-closed 방향이라 위험하진 않으나, «규모가 줄었는데 다시
승인을 요구한다»는 혼란이 생긴다 — §2ⓒ 옆에 한 줄 적어 두는 편이 낫다.

---

## 재현 자료

- 원형: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/5d88d7d2-4bb6-412e-83fa-56580ac7b33b/scratchpad/g/scripts/`
  (`check_design_evidence.py` §0 삽입판 + `ledger.py` 최소 구현)
- 정규화 실측: `.../scratchpad/g/norm2.py`
- 빌드 사본: `.../scratchpad/g/a8`(원본 `.../scratchpad/refreeze-repair/a8-copy`는 무변경)
- 정본 `dddjango-web/scripts/check_design_evidence.py`·`backstop.py`는 수정하지 않았다.
