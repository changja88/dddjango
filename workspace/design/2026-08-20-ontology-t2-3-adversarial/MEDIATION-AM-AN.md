# T2-3 선행 설계 리뷰 중재 — 레인 AM·AN + 저자 자체 발견 (2026-08-20)

> 대상: `2026-08-20-ontology-t2-3-design.md` v1(판단 L1~L9·C1~C4·B1~B12).
> 레인 AM(설계 판단표 반증·7과제) **16건** · 레인 AN(열린 스코프) **18건** · 저자 자체 발견(SF) **5건** = **39건**.
> 규약 R1′의 «전건 중재» 이행. 판정 분포: **채택 35 · 부분 채택 3 · 기각 0 · 사용자 상정 1**.

## 0. 검증 방법 — 채택 전 실물 재현

레인 근거를 그대로 믿지 않고 저자가 독립 재현했다. **결과: 근거 오기 1건(파일명)을 빼면 전건 사실.**

| 검증 | 방법 | 결과 |
|---|---|---|
| AM#2·AN#11 core 부재 | `dddjango/scripts/`·`codex-dddjango/…/scripts/`에서 regen·loop·owner-map 매칭 | **0건** — 확증 |
| AM#3·AN#3 sink 오염 | `registry_gate.py:96–100`(env 미지정 `subprocess.run`) ↔ `anchor_diff.py:148–155`(명시 `env.pop`) 대조 | 확증 — 게이트만 수리 미적용 |
| AM#10 배너 앵커 | 세션 3파일에서 assistant `message.id` 분할 계수 | **분할 최대 9 · 분할된 id 1,347/1,869(72%)** — 확증 |
| AM#13 파일 간 복제 | Ask `tool_use.id` 전수 대조 | `toolu_016d…`가 **`48c8a476:79`·`d1a53911:3532` 두 파일에 존재** · 복제 tool_result **88건** — 확증 |
| AM#12 `[Image:]` | 배제 태그 6종 적용 후 잔여 문자열 분류 | `[Image: original 1200x2610…]` **1건이 사람 메시지로 분류** — 확증 |
| AN#1 A암 종료 | `dddjango.md:139`·`:175` 원문 | «미해소 «귀속» red … 하나라도 남으면 **G2를 제시하지 않는다**» · «G2 blocker 는 위임되지 않는다 … **그 지점에서 정지**» — 확증 |
| AN#9 owner-map 라우팅 | 스냅숏 538행의 checker 값 ↔ `REGISTRY` 대조 | 고유값 **23종 중 registry 정확 일치 12 · 불일치 11**(«(신설)» 8 · workspace tool 3) — 확증 |
| **근거 오기** | AM이 인용한 `d1a75daf-89b2-433c-84f0-285e87fb14d6.jsonl` | **실재하지 않음**(홈 전역 검색 0). 다만 인용 «내용»은 `d1a53911…`에서 전건 재현됨 — 파일명 오기로 처분, 발견은 유효 |

## 1. 전건 중재 표

심각도는 레인 표기를 따르되, 저자 재현으로 승강한 것은 «→»로 표기했다.

### 1-1. 아키텍처·배포 (blocker 군)

| 출처 | 심각도 | 요지 | 판정 | 처분 |
|---|---|---|---|---|
| AM#2·AN#11 | blocker | 루프 core가 `workspace/tools`에만 있어 **설치본 셸 B가 호출 불가** | 채택 | core를 `dddjango/scripts/regen_core.py`로 신설·codex byte 미러. `workspace/tools/regen_loop_prototype.py`는 그 core를 import하는 저장소 측 wrapper로 강등. `make verify`에 미러 diff + **설치 cache 실행 probe** 추가 |
| AM#3·AN#3 | blocker | `registry_gate`가 anchor·current 양쪽에 sink env를 상속 → 「red 직후 레코드 수집」이 **legacy+current 혼합** 또는 0건 | 채택 | `registry_gate`에 **L/N 분리 sink**를 내부에서 열고, 정규화 차분 후 **N∖L에 해당하는 current 레코드만** sidecar JSON으로 반환. `DJR_FINDINGS_JSON`·`DJR_VIOLATIONS_DIR` **둘 다** 격리. synthetic fail-closed 귀속도 같은 구조로 반환. **기존 도구의 실결함이므로 T2-3에서 수리** |
| AN#10 | blocker | **실험 run namespace가 데이터 모델에 없다** — findings `run_id`는 검사기 프로세스 ID(`checker+UTC+pid`)이지 A/B 런 ID가 아니다 | 채택 | manifest가 발급한 불변 `experiment_run_id`를 검사기·turn log·수집 raw에 전달. 기존 프로세스 `run_id`는 별도 필드 유지. 소비자는 experiment ID 부재 시 **fail-closed**. T2-4의 «현재 런 한정» 질의의 선결 조건 |
| AM#15 | blocker | T2-3 산출물이 **T2-0b 봉인 목록 밖** | 채택 | T2-3이 **manifest fragment**를 산출(core·selector·프롬프트 골든·turn-log schema·계수기·픽스처 SHA·셸 B 실행 봉투·환경 스위치). T2-0b가 이를 포함해 봉인 |
| AN#12 | major | Claude Coordinator만 개작하면 **Codex 런타임이 의미 미러에서 이탈** | 채택 | 같은 커밋에서 `codex-dddjango/skills/dddjango/SKILL.md` 대응 절차를 의미 미러로 개작 + 양 런타임 **행동 parity 검사**(같은 red 픽스처 → 발화·예산·최종 결과 비교) |

### 1-2. 처치 정의·측정 타당성

| 출처 | 심각도 | 요지 | 판정 | 처분 |
|---|---|---|---|---|
| AM#1 | major | 「프롬프트 byte 동일 = 같은 처치」 **불변식이 거짓** — 셸 A/B는 모델·시스템 프롬프트·도구·권한·문맥이 전부 다르고, C2가 슬라이스 문맥을 더하므로 최종 입력조차 다르다 | 채택 | L1 교체: **「core renderer 1벌 + 비인과적 component harness(셸 A) + 실제 처치 셸(B)」**. 셸 A는 selector·상태기계·프롬프트 회귀에만 쓰고 **A/B 효과 증거에서 제외**. 처치 동일성은 B/C의 실행 봉투 전체(모델·시스템 프롬프트·도구·권한·문맥·core/selector SHA)가 같고 selector만 다른 것으로 봉인 |
| AM#6 | major | 셸 A가 발화 검사기만 재실행해 **거짓 수렴** — 실측: `bad_rules` 한 파일에 `check-domain-model` 12줄 + `check-public-surface-annotation` 1줄로 **검사기 2종이 겹침** | 채택 | 셸 A도 **종료 직전 27종 full audit**. 회전 중에는 발화 검사기 + 변경 파일과 겹치는 검사기 재실행. 최종 full audit red면 수렴 취소 |
| AM#7·AN#5 | blocker(→승격) | **「범위 밖 위반 집합 불변」 ≠ 「범위 밖 코드 불변」** — `acceptEdits`는 저장소 전체 편집 권한이고, 검사기가 안 보는 테스트·설정·타 BC 변경은 delta 0으로 통과 | 채택 | 회전 전후 **tracked·untracked git diff**로 편집 허용목록 검사. 허용 scope 밖 변경은 관측치가 아니라 **기술 실패·런 무효**로 즉시 중단·triplet 청정 재시작. 위반 delta는 보조 진단으로만 유지 |
| AN#4 | blocker | 재생성 후 **규율 감사·테스트 증거가 낡는다** — step5(감사·테스트) 뒤 step6(게이트) red → 재호출 coder가 테스트를 약화해도 같은 검사기만 green이면 옛 증거로 G2 제시 | 채택 | 재생성 편집 1회마다 **step 5 이후 증거 전부 무효화**. 최종 편집 뒤 focused/holistic 감사·관련 테스트·전체 스위트·직접 selector 레인·registry 차분을 **모두 재실행한 결과만** G2 허용 |
| AN#2 | blocker | 루프 발화점이 **게이트의 절반만** 본다 — G2에는 ① scope별 직접 실행 ② auto `registry_gate` 두 레인이 있고, 직접 레인만 red면 루프 미발화 | 채택 | 두 레인 모두에서 **실패 receipt**(`checker + exact argv + anchor + profile + scope + exit + record IDs`)를 구조화하고, 루프는 **그 정확한 호출**을 재실행. 직접 레인 red 전용 회귀 픽스처 추가 |
| AN#9 | major | **owner-map을 재검사 라우팅에 쓰면 실행 불능·오귀속** — 23종 중 11종이 registry 밖(«(신설)» 접미·workspace tool), #393/#395는 소유자 충돌 | 채택 | owner-map은 **주입 대상 선별에만**. 재검사는 실패 receipt의 **실제 검사기 + exact argv**. #393/#395 중복 발화 픽스처로 고정. (L7 자인 W6의 «이름 어긋남»이 실은 실행 결함이었음) |
| AM#11 | major | gate 표본 0 + 무수정 승인 고정 → bounce가 구조상 0 | **부분 채택** | 계수기를 **프로토콜 불변식 검사**로 재규정(기대 0·비0이면 invalid run 경보) = 채택. 별도 `pre_gate_repair_cycles` 신설 = **회전 레코드로 갈음**(중복 저작 방지) — 대신 **A암도 회전 0 레코드를 남긴다**로 확장해 처치 발화량을 3암 비교 가능하게 한다 |

### 1-3. 동일성·레코드·상태

| 출처 | 심각도 | 요지 | 판정 | 처분 |
|---|---|---|---|---|
| AM#8·AN#8·SF-2 | major | **동일성 키가 T2-2 어댑터와 같다는 주장이 거짓** — raw는 `rule="#N"`·`file="path[:line]"`, 어댑터는 Work IRI×file×symbol. alias 3개뿐이라 B3의 #302~#310 전부 미조인. 행 이동·절대경로로 hash가 바뀜(실측 3종) | 채택 | **canonical identity 신설**: `Work IRI 또는 명시 unknown-rule 네임스페이스 × 타깃 상대 정규화 경로(라인 제거) × 안정 심볼`. locator를 `{path, line, column}`로 분리. `no_progress`·범위 밖 delta·어댑터가 **같은 canonicalizer** 호출. T2-2 identity 골든·drift 골든 재기준선 동반 |
| AM#9·AN#15 | major | 회전 레코드로 **재현·감사 불가** + `stop_reason`이 전부 terminal이라 진행 중 회전을 표현 못 함 | 채택 | schema/version 도입·비종료 회전 `stop_reason:null`. 필드 보강: experiment/build anchor·current commit·dirty diff hash·변경 경로 전후 hash·모델/시스템/도구/권한 hash·core/pipeline/selector/snapshot SHA·검사기별 exit·canonical added/removed ID 집합·gate 귀속·프롬프트 artifact URI·stderr/timeout·예산 |
| AN#6 | major | **오류·타임아웃 뒤 부분 편집의 처분 없음** — 실패한 처치의 편집을 다음 런이 상속 | 채택 | 회전별 pre-edit tree hash 기록 + `error`·scope 위반 시 **pre-turn 복원**. triplet 재실행은 발주 baseline에서 재materialize 후 동등성 해시 검사. 셸 B의 coder 실패에도 동일 계약 |
| AM#5·SF-3 | major | **anchor 수명 규칙 문면 부재**(독립 재발견) | 채택 | 초기·반복 게이트에 **동일한 최초 `build_anchor`** 고정. 회전 중 커밋 허용하되 앵커 미갱신. exit 1/empty diff는 재생성 대상이 아니라 **계측 실패로 중단**. anchor·commit·dirty hash를 turn log에 |
| AM#4 | major | 모든 G2 red를 coder에 재호출하는 것은 **소유권 계약 위반** | 채택 | red를 `coder-owned / acceptance-owned / design-contract / out-of-scope / measurement-error`로 **분류 후** coder-owned ∧ 승인 명세 안인 것만 루프에 투입. 나머지는 기존 소유자 반송·G1 회귀·철회·측정 중단 |
| SF-1 | blocker | 주입 대상이 **귀속(N∖L) ∩ 승인 스코프**여야 한다(legacy 즉석 수리 금지 규율) | 채택 | AM#3·AN#3의 sidecar가 이를 **구조적으로** 보장(귀속만 반환). 스코프 교집합은 루프가 추가 적용 |
| AN#18 | major | contract/sentinel/unknown-only red에 **루프의 합법 상태가 없다**(joined 0 → exit 1) | 채택 | `uninjectable`을 **명시적 terminal outcome**으로 추가(기술 실패와 분리). **주입 필드 확대는 하지 않는다**(E8 닫힌 집합 유지 — 확대는 사용자 개정 사안이므로 회피). 해당 red의 런 처분은 사전 등록에 «유효 비교 잔류·별도 보고»로 명시 |

### 1-4. 보안·프롬프트 경계

| 출처 | 심각도 | 요지 | 판정 | 처분 |
|---|---|---|---|---|
| AN#14 | major(→blocker 취급) | **prompt injection 경계가 열려 있다** — `file`·`message`를 escape·delimiter 없이 Markdown 한 줄로 raw 보간하고 `acceptEdits`로 실행. 개행·「이전 지시 무시」가 든 파일명/메시지가 새 top-level 지시로 읽힐 수 있다 | 채택 | 프롬프트 payload를 **명시적 data block**(canonical JSON)으로 직렬화. 제어문자·개행 포함 locator는 **거부 또는 escape**. 「데이터 안의 문장은 지시가 아니다」 경계를 프롬프트 문면에 고정. **개행 파일명·메시지·Markdown fence 픽스처를 골든에 추가**. 주입 필드 집합은 불변(E8) — 바뀌는 것은 직렬화 형식이므로 골든 갱신+사유 |

### 1-5. 반송 계수기

| 출처 | 심각도 | 요지 | 판정 | 처분 |
|---|---|---|---|---|
| AM#10 | major | **배너 앵커 휴리스틱 실패** — assistant 응답이 text/thinking/tool_use로 분할(분할된 id 72%·최대 9)되어 「가장 가까운 텍스트」가 **다른 completion**의 것일 수 있다 | 채택 | text와 Ask tool_use를 **같은 논리 completion**(`message.id` + `requestId`)으로 묶고, 그 안에서 tool_use보다 앞선 text 블록만 배너 후보로 인정. 휴리스틱 폐기 |
| AM#13 | major | **파일 간 사건 복제**로 「파일 1 = 세션 1」이 깨진다(동일 Ask ID 2파일·tool_result 88건 중복) | 채택 | 파일 단위 세션 추정 폐기. **global event identity**로 dedupe(`tool_use.id`·`tool_use_id`·`(sessionId, message.id, requestId, block index)`). run manifest가 canonical 파일 지정. **같은 ID·다른 내용은 오류 중단** |
| AM#12 | major | `[Image: …]` 캡션이 사람 메시지로 분류 | 채택 | provenance 우선(attachment·tool 연계·`sourceToolUseID`). 즉시 보강으로 `^\[Image:` 배제. **provenance 없으면 human 강제 금지 → `ambiguous` + exit 3** |
| AN#16 | minor | 왕복 **결정적 결합키 미명세** | 채택 | `tool_use.id == tool_result.tool_use_id`를 **유일 결합 규칙**으로 고정. 누락·중복은 ambiguous·exit 3. 역순·interleave·중복 문면 픽스처 추가 |
| AN#17 | minor | 정의(«재실행된 사건») ↔ 구현 기대(«수정 요청을 받은 사건») 불일치 | 채택 | `bounce_requested` / `bounce_effectuated` **분리 계상**. 공식 반송은 같은 G단계 재진입 확인 후 확정. 픽스처 P2를 두 값으로 분리 |
| AM#14 | minor | 존재하지 않는 «§7» 참조 | 채택 | **§7 측정 부록** 신설(표본 파일·추출 시각·행 수·해시·질의 고정) |

### 1-5b. 순서·절차

| 출처 | 심각도 | 요지 | 판정 | 처분 |
|---|---|---|---|---|
| AM#16 | major | 구현 문면 검증 전에 **append-only LEDGER 재기준선** | 채택 | 순서 교체: `구현 diff → 프롬프트 골든·의미 정합 리뷰 → 픽스처·full gate → LEDGER append → append 재검증`. 코퍼스 정본·LEDGER 변경은 **별도 커밋** |
| AN#7 | major | `no_progress`가 동결 N=3을 **N≤2 적응형 처치로 변질** | **부분 채택** | 실런에서는 `no_progress`를 **진단 플래그로만** 기록하고 `zero` 또는 정확히 N=3까지 실행(동결 정합 — 개정 불요). 셸 A(비인과 harness)에서는 조기 종료 허용. → **사용자 상정 불필요** |
| AN#13 | blocker | T2-0b가 **신선하지 않은 설치 cache**를 봉인할 수 있다(설치 서브에이전트는 cache에서 로드) | **부분 채택** | 지금: manifest 선행조건에 «source tree ↔ Claude cache ↔ Codex cache 파일목록·해시 동등성 + loop probe 성공»을 **설계로 등재**. 실제 설치본 갱신은 **비가역·외부 행위(R3-3)** 이므로 **T2-0b 시점에 사용자 요청** — T2-3에서는 실행하지 않는다 |

## 2. 사용자 상정 — 1건 (규약 R3-2 방향 변경형)

### AN#1 — A암은 귀속 red가 있으면 유효 런으로 끝날 수 없다 (blocker)

**사실관계(저자 재현 확증)**:
- `dddjango.md:139` — «Red … **미해소 «귀속» red** … 가 하나라도 남으면 **G2를 제시하지 않는다**»
- `dddjango.md:175` — «게이트 위임 지시가 있어도 위임되는 것은 승인 입력뿐 — **G2 blocker는 위임되지 않는다**: 산출물에 기록하고 **그 지점에서 정지**»
- `t2-plan:43` — «산출물 미완성·STOP·인수 게이트 불통과 = **판정 실패**(0위반 산입 금지)»

**따라서**: A암(`loop_enabled=off`)에서 귀속 red가 남으면 G2 배너가 발화하지 못하고 파이프라인이 정지 → 그 런은 **판정 실패**. 그런데 A/B가 보려는 것은 바로 «A는 위반이 더 많다»이므로, **A가 나쁠수록 측정에서 탈락**한다. W8이 자인한 단순 교락이 아니라 **비교군 선택 소실**이다.

**처분 선택지**(어느 쪽이든 사전 등록 개정 = 판정 기준 변경 → R3-2):

| 안 | 내용 | 대가 |
|---|---|---|
| **가** | A암에 «관측 종료점»을 별도 정의 — 게이트 실행·결과 기록까지를 런의 끝으로 삼고 G2 승인은 채점에 요구하지 않는다 | 세 암의 종료점이 달라짐(A는 게이트 후, B/C는 G2 후) — 비교 단위를 «게이트 시점 위반 수»로 통일하면 해소되나, 인수 게이트 규약(§T2-0a)의 문면 개정 필요 |
| 나 | A암도 게이트 red 시 **기존 반송 1회**를 허용(루프 아님·주입 재료는 게이트 진단 전문) | 「A = 재생성 0」이라는 사전 등록 문면과 충돌. estimand가 «폐루프 번들»에서 «규격화·선별 주입의 효과»로 바뀜 |
| 다 | A암의 판정 실패를 그대로 수용하고 유효 발주에서 제외 | 유효 발주가 줄어 D9(rate 중앙값 ≥15%) 판정 재료가 고갈될 수 있음 — 18런의 상당수가 무효화 |

**저자 권고 = 가**. 이유: 판정 스칼라가 이미 «결정적 검사기 위반 수»(§T2-0a)이고 그 수는 **게이트 시점에 확정**된다. G2 승인은 사용자 절차이지 측정량이 아니므로, 측정 종료점을 게이트로 통일하면 세 암의 비교 단위가 오히려 정확해진다. 나는 처치 정의를 바꾸고, 다는 표본을 잃는다.

**진행 처분**: 이 결정은 **T2-0b(구현 동결) 전까지** 필요하다. T2-3의 나머지 구현은 이 결정과 독립이므로 **멈추지 않고 계속한다**. 다만 C3·C4의 A암 분기 문면만 «미결·상정 중»으로 표기하고 확정하지 않는다.

## 3. 판단표 v2 반영 지시 (요약)

- **L1** → core 1벌 + **비인과 harness(A)** + 처치 셸(B). 셸 A는 A/B 증거에서 제외.
- **L2** → 재검사는 실패 receipt의 exact argv. 종료 직전 27종 full audit.
- **L3** → 회전 레코드 전면 재설계(schema version·experiment_run_id·앵커·tree hash·identity 집합·receipt hash).
- **L4** → `no_progress`는 실런에서 **진단 플래그만**. `uninjectable` terminal 추가.
- **L5** → 범위 밖 검증을 **git diff 기반 편집 허용목록**으로 교체. 위반 delta는 보조.
- **L6** → stdin 입력·`--output-format json`·`--model` 고정. 실패 시 **pre-turn 복원**.
- **L7** → selector는 «선별»로 정명. owner-map은 라우팅에서 **퇴출**.
- **L8** → sink 격리는 게이트가 소유(sidecar). 루프는 그 결과만 소비.
- **L10(신설)** → 루프는 커밋하지 않는다.
- **L11(신설)** → 프롬프트 payload는 canonical JSON data block — **injection 경계 고정**.
- **C1** → 편입점 = **G2 pre-banner**(step 6). 기존 반송 경로의 주입 재료 규격화. red 5분류 선행.
- **C2** → 재생성 후 **step 5 이후 증거 전부 무효화·재실행**.
- **C3** → A암 분기는 **사용자 상정 중**으로 표기(확정 보류).
- **C5(신설)** → Codex `SKILL.md` 의미 미러 + 행동 parity 검사.
- **B1** → 반송을 `requested`/`effectuated` 분리.
- **B2** → 배너 앵커를 **논리 completion**(`message.id`+`requestId`) 안으로 한정.
- **B7** → provenance 우선 · `^\[Image:` 배제 · 미상은 ambiguous.
- **B9** → 파일 단위 세션 추정 폐기 → **global event identity dedupe** + run manifest.
- **B13(신설)** → 결합키 = `tool_use.id ↔ tool_result.tool_use_id` 단일 규칙.
- **§5 순서** → LEDGER append를 **문면 검증 후**로 이동. 코퍼스·LEDGER는 별도 커밋.
- **§7(신설)** → 측정 부록(표본·해시·질의 고정).
- **§8(신설)** → **T2-0b manifest fragment** 명세.

## 4. 부분 채택 3건의 사유 (반증 회부 대상)

규약 R1′의 «기각·부분 채택 건은 그 사유를 codex 반증 레인에 회부» 이행 — 아래 3건을 다음 레인(AO)의 반증 과제로 넣는다.

1. **AM#11의 `pre_gate_repair_cycles` 신설을 회전 레코드로 갈음** — 별도 계수기를 만들지 않고 A암까지 회전 레코드를 확장하는 것으로 충분한가? A암에 «회전»이 없는데 0 레코드를 남기는 것이 의미 있는 관측인가?
2. **AN#7을 «실런에서 진단 플래그만»으로 처분** — 셸 A에서만 조기 종료를 허용하는 비대칭이 harness와 처치의 동작 분기를 만들어 회귀 검출력을 떨어뜨리지 않는가?
3. **AN#13의 설치본 갱신을 T2-0b로 이연** — T2-3에서 «설치 cache 실행 probe»를 만들되 실행하지 않는 것이 blocker의 실질 해소인가, 아니면 검증되지 않은 설계를 T2-0b로 미루는 것인가?

---
*좌표: `PROMPT-AM.md`·`log-AM.txt`(16건) · `PROMPT-AN.md`·`log-AN.txt`(18건) · `SELF-FINDINGS.md`(5건). 저자 재현 검증은 §0.*
