# T3 게이트 조항 — 선행 계약 6종 `contract_ref` Work 조인 (T2 이월분 처분)

> 대상: `T3-EXECUTION.md` 웨이브 4 «T3 게이트 조항 4건» 중 **«선행 계약 6종 contract_ref 조인»**.
> 이월 근거 = t2-plan v1.1 **D12**(L145) · 블루프린트 v3 **개정 4**(L184) — «선행 계약 6종의 Work 조인은
> T3 이월(contract_ref 적재 — 위반 그래프의 Work 조인은 규칙 발견 한정)».
> 판정: **조인 성립 — 7종 전건**(명목 6 + common-container). 기구는 alias 대장의 **둘째 번호 공간
> `contract#<검사기>`** 신설로 닫는다(어휘·셰이프 개정 불요).

## 0. 저자 판단 요약 (리뷰가 먼저 공격해야 할 곳)

1. **«6종»은 검사기 수이고, 조인 대상은 실제로 7종이다.** t2-plan L24 가 «선행 계약(rule=null) 7종 중
   1종(common-container) 개작 완료 — 잔여 6종»으로 세었고 D12·개정 4 가 그 «잔여 6»을 그대로 물려받았다.
   그러나 common-container 도 `rule=null + contract_ref` 로 방출하므로 **조인 축에서는 7종이 같은 상태**다.
   6 만 처분하면 7번째가 침묵으로 남는다 — 본 메모는 **7종 전건**을 처분하고 6/7 구분을 §1 에 명시한다.
2. **T3 전량 이관은 «선행 계약 문서»를 이관하지 않았다 — 그런데도 조인은 성립한다.** 코퍼스 30문서는
   플러그인 문서 전량이고(`corpus-manifest.tsv`), 계약 원문(`2026-08-03-api-error-management-design.md` 등)은
   그 밖이다. 조인이 성립하는 이유는 **그 계약의 규범 내용이 플러그인 정본에 이미 실려 있고 T3 가 그것을
   Work 로 만들었기 때문**이다(§2). 「계약 문서를 이관해야 조인된다」는 전제가 틀렸다.
3. **`enforcedBy` 역참조를 그대로 조인으로 쓰면 안 된다.** T3 배선은 7종 각각에 12~19개 Work 를 걸었다
   (§3 표) — `ViolationShape-violatesWork maxCount 1` 과 정면 충돌이고, 그 안에는 alias 판단표 v2 §2 가
   **미등재 사유로 못박은 «집행 축 인용»**(registry #N 행)이 섞여 있다. 조인은 **문면 대조 1건 선별**이어야 한다.
4. **자신 없는 것 3가지**(§8): ⓐ 재진술 소급 패스가 아직 안 돌아 `restates` 간선이 0건이라 «정본 vs 재진술»
   선택 2건이 잠정이다 ⓑ transient-overmapping 의 소유 문서가 스킬 정본이 아니라 에이전트 문서다
   ⓒ 혼성 3종(api-error·composition-root·error-centralization)의 계약 레인은 본 처분 **범위 밖**이다(§7).

## 1. «선행 계약 6종» 실물 특정

정본 목록은 `workspace/tools/reverse_coverage.py:49–57` `PRIOR_CONTRACT_SCRIPTS` 다(538 매핑표 ⓒ 규칙 0건 —
`grep -c` 실측 7종 전건 0). 적대 리뷰 `L-P.md:15` 가 «반증 실패»로 같은 7종을 재확인했다.

| # | 검사기 | `CONTRACT_REF`(모듈 상수) | owner-map 행 | 6/7 구분 |
|---|---|---|---|---|
| 1 | `check-response-schema-bypass.py` | 선행 계약(08-04 API-error) 소유 | 0 | **잔여 6** |
| 2 | `check-transient-overmapping.py` | 선행 계약(08-04 API-error) 소유 | 0 | **잔여 6** |
| 3 | `check-ninja-boundary-middleware.py` | 선행 계약(08-04 API-error) 소유 | 0 | **잔여 6** |
| 4 | `check-idempotency-scope-creep.py` | 선행 계약(architecture-api §13 멱등 스코프) 소유 | 0 | **잔여 6** |
| 5 | `check-choices-literal-consumption.py` | 선행 계약(2026-07-06 상수 승격) 소유 | 0 | **잔여 6** |
| 6 | `check-app-container.py` | 선행 규약(표준 트리 전신 — application/ 컨테이너 위치) 소유 | 0 | **잔여 6** |
| 7 | `check-common-container.py` | 선행 규약(D38 승격/강등 — 루트 framework/ 배치) 소유 | 0 | T0 개작 완료분 |

**레코드 실물**: `findings.py:380–401` `ContractFindings` — `rule=None` · `sentinel=None` ·
`contract_ref=<검사기 상수>` · `checker=<파일명>`(`findings.py:205–219` 레코드 판형). 즉 **한 레코드가
가진 유일한 판별자는 `checker`** 이고 `contract_ref` 는 검사기 상수라 그 아래로 못 쪼갠다
(08-04 API-error 하나가 3종에 공유된다 — 위 표).

**발화 사건 유형 전수**(`.add()` 호출 사이트 실측 — 이 수가 조인 함수성을 결정한다):

| 검사기 | 사건 유형 | 메시지 문면 |
|---|---|---|
| app-container:249 | 1 | Django 앱이 `application/` 밖 평면에 있다(houserules §0-1) |
| choices-literal:266 · :273 | 2 | ⓐ 심볼 choices 선언 필드의 `default="리터럴"` · ⓑ `.filter/exclude(field=리터럴)` |
| common-container:115 | 1 | 횡단 버킷이 `application/` 안에 있다 |
| idempotency-scope-creep:243 | 1 | 미요청 멱등성 산출물 추가 — G1 채택 승인 없이 accepted scope 밖 |
| ninja-boundary-middleware:182 | 1 | BC driving 층 미들웨어가 전역 `MIDDLEWARE` 에 자가등록 |
| response-schema-bypass:1011 | 1 | 선언 200–203 schema 를 raw Django response 로 우회 |
| transient-overmapping:223 | 1 | 영구장애 구별 분기 없이 `OperationalError/DatabaseError` 통째 retryable |

→ **총 8 사건 유형 / 7 검사기**, 그리고 choices 의 2 유형은 같은 Work 가 축자 포섭한다(§3) —
따라서 **검사기 → Work 가 함수(functional)** 다. `contract_ref` 아래 category 표가 필요 없다.

## 2. T3 전량 이관 전수 대조 — 무엇이 생겼고 무엇이 안 생겼나

**불성립 축(계약 문서 자체)**: 코퍼스 = `corpus-manifest.tsv` 30문서(플러그인 skills/agents/commands) 뿐.
계약 원문 4종 — `2026-08-03-api-error-management-design.md` · `2026-07-06-constant-promotion-rule-design.md` ·
D38(`2026-08-07-decision-record.md`) · 표준 트리 전신 — 은 **전건 코퍼스 밖**이라 T3 로 Work 가 생기지 않았다.
「계약 문서에 채번한다」는 경로는 **지금도 불성립**이고, 그 경로를 되살리려면 코퍼스 확장(블루프린트 §8 밖)이
선행한다. 본 메모는 그 경로를 **기각**한다.

**성립 축(계약의 규범 내용)**: 2026-08-12 겹침 재검토(`2026-08-12-prior-contract-overlap-review.md:22`)가
«7종의 문면 소유는 각 선행 계약 문서 **+ registry 설명문(`commands/dddjango.md`)**이 진다»고 적었는데,
T3 는 그 `commands/dddjango.md` 와 **7종의 규범 내용을 실제로 진술하는 스킬·에이전트 정본**을 전량 이관했다.
실측: 7종 전건에 대해 `djr:enforcedBy <djr#c/<검사기>>` 간선이 생산 그래프에 실재한다.

| 검사기 | T3 이후 `enforcedBy` Work 수 | 그중 스킬·에이전트 정본 소유 |
|---|---|---|
| app-container | 17 | 15 |
| choices-literal-consumption | 15 | 13 |
| common-container | 3 | 1 |
| idempotency-scope-creep | 13 | 11 |
| ninja-boundary-middleware | 14 | 12 |
| response-schema-bypass | 19 | 17 |
| transient-overmapping | 12 | 10 |

(나머지는 `commands/dddjango.md` 소유 2종 — 각 검사기의 registry #N 행 1개 + 전 27종 나열 행 `R-0302`.)

**T2 전제와의 차이 정명**: 어댑터 설계 노트 §1 은 «선행 계약 발견은 **애초에 Work 가 없다**»라고 적었다.
T3 이후 그 문장은 **거짓**이다 — Work 는 있고, 없던 것은 «어느 Work 인가»를 고르는 **대장**이다.

## 3. 조인안 — 판정표 (문면 대조 · 판단표 v2 §2 기준 승계)

판정 기준은 alias 판단표 v2 §0-2 를 그대로 쓴다: *«검사기가 막는 사건과 Work 의 규범 내용이 같은 사건을
금지·의무화한다 — 주어·양상·술어 일치»*. 부분 겹침·상위 구간 인용·**집행 축(어느 검사기가 미는가) 인용은
미등재**.

| 검사기 | **조인 Work** | 유형 | Work 문면 | 소유 절 | 판정 사유 |
|---|---|---|---|---|---|
| `check-app-container.py` | **R-0122** | Prohibition | 루트 평면 `<app>/` 금지 | architecture-ddd-final §3.2 | 주어(루트 평면 앱)·양상(금지)·술어(`application/` 밖 배치) 일치. 이 검사기가 **유일 집행자**(`enforcedBy` 단독) |
| `check-choices-literal-consumption.py` | **R-1186** | Obligation | choices·Enum 필드 값의 심볼 참조 의무 | implementation-django-final §2.5 [DCS] | 문면이 «비교·분기·`.filter()`·대입·**`default`**는 반드시 심볼로 참조» — 사건 ⓐ·ⓑ **둘 다 축자 포섭**(`.filter(status="pending")` 금지가 예시로 실려 있다) |
| `check-common-container.py` | **R-3191** | Obligation | 최상위는 셋뿐 — `application/<bounded_context>/` · `framework/` · `<project>/` | discipline-houserules-final §1 | `framework/` 의 **자리**를 진술하는 유일 Work(라벨 전수 검색 실측). 「`application/` 안 버킷」은 이 의무의 부정형 |
| `check-idempotency-scope-creep.py` | **R-1662** | Prohibition | 미요청 멱등성의 silent 필수 서브시스템화 금지 | agents/design-architect.md `### Error response contract 12-slot`(원문 L64 «데이터(db)» 불릿 — §8 ⓔ) | 주어(미요청 멱등성)·양상(금지)·술어(silent 빌드) 일치. 검사기 메시지 «G1 채택 승인 없이 accepted scope 밖»과 문면의 «G1 에서 채택을 택하면…» 대칭 |
| `check-ninja-boundary-middleware.py` | **R-0795** | Prohibition | 전역 middleware·root URL wrapper·별도 dispatcher 의 Ninja 밖 status 합성 금지 | implementation-django-ninja-final §6.3 | 검사기 메시지가 **§6.3 을 직접 인용**하고 근거 문면(«협상·임의 status 는 ninja 경계 안에서 낸다»)이 이 Work 의 술어 |
| `check-response-schema-bypass.py` | **R-0091** | Obligation | 선언 JSON 성공의 Ninja validation/serialization 경유 | implementation-django-ninja-final §6.2 | 검사기 근거 문면 «must own **validation and serialization**» 과 술어 축자 일치. **재진술 3중 미확정 — §8 ⓐ** |
| `check-transient-overmapping.py` | **R-1040** | Prohibition | 영구장애의 retryable 확대 금지 | agents/discipline-reviewer.md `## Phase 2 점검 항목` | 검사기 docstring «G1 에서 이미 승인된 `preserve-established` brownfield handler 가 인프라 오류 전체를 retryable 로 넓히지 않게 지키는 방어선» = 이 Work 문면 축자. 주어(brownfield preserve handler) 일치 |

**기계 검증 실측** — 7행 전건이 판단표 v2 §4 의 ⑥′ 해소 4조건 + `enforcedBy` 간선을 만족한다:

| checker | Work | ISSUED 발행 | `currentExpression` 1 | Expression 왕복 | `enforcedBy` 간선 |
|---|---|---|---|---|---|
| app-container | R-0122 | ✓ | ✓ | `R-0122@2026-08-19` | ✓ |
| choices-literal | R-1186 | ✓ | ✓ | `R-1186@2026-08-22` | ✓ |
| common-container | R-3191 | ✓ | ✓ | `R-3191@2026-08-22` | ✓ |
| idempotency | R-1662 | ✓ | ✓ | `R-1662@2026-08-22` | ✓ |
| ninja-boundary | R-0795 | ✓ | ✓ | `R-0795@2026-08-22` | ✓ |
| response-schema | R-0091 | ✓ | ✓ | `R-0091@2026-08-19` | ✓ |
| transient-overmapping | R-1040 | ✓ | ✓ | `R-1040@2026-08-22` | ✓ |

### 3.1 명시 미등재 — registry #N 행 7종 (침묵 탈락 금지)

T3 는 `commands/dddjango.md` 의 27종 registry 표를 이관해 **검사기당 1:1 Work** 를 만들었다:
`R-0337`(#3 response-schema) · `R-0341`(#7 app-container) · `R-0342`(#8 ninja-boundary) ·
`R-0343`(#9 common-container) · `R-0344`(#10 idempotency) · `R-0347`(#13 transient) ·
`R-0352`(#18 choices). 함수성이 완벽해 **가장 유혹적인 조인 후보**지만 **전건 미등재**한다:

- 문면이 «이 검사기는 무엇을 검사한다»(집행 축)이지 «무엇이 금지·의무다»(규범 축)가 아니다 —
  판단표 v2 §2 가 `#10`·`#20`·`#21` 을 **«집행 축 인용»으로 미등재**한 바로 그 사유다.
- 그 정보는 이미 `djr:enforcedBy` 간선이 진다. registry Work 를 `violatesWork` 로 쓰면 **위반이 규범이 아니라
  집행 좌표를 가리키게 되고**, C암 규칙 팩의 «어느 규범이 몇 번 깨졌나» 질의가 전건 registry 로 접힌다.
- `R-0302`(27종 전부 나열 행)도 같은 사유 + 다중 집행자라 미등재.

### 3.2 명시 미등재 — 인접 후보 4건

| Work | 문면 | 인접 검사기 | 미등재 사유 |
|---|---|---|---|
| R-2367 | 영구장애의 `None` 반환·handler500 전파 — `OperationalError` 클래스 통째 503 금지 | transient-overmapping | **술어는 축자 일치하나 주어 상이** — 이 Work 의 주어는 Django HTML `process_exception` 미들웨어(implementation-django-web §11)이고 검사기의 주어는 `@*.exception_handler` API 경계다 |
| R-2091 | dddjango 파이프라인 채택의 G0/G1 사용자 결정·미요청 기본 미적용 | idempotency-scope-creep | `contract_ref` 가 명시하는 **architecture-api §13.4 좌표 본인**이지만 유형이 `djr:Override` — 위반의 대상은 우선 규범이 아니라 금지 규범(R-1662)이다. 면제 판정(`_user_adopted`)의 근거로만 인용 |
| R-3191 | 최상위는 셋뿐 | app-container | 같은 Work 가 두 사건을 묶은 **합성 규범**(3칸) — app-container 는 더 좁은 R-0122 가 있으므로 그쪽. common-container 는 대체 Work 가 없어 R-3191 채택(비대칭은 의도) |
| R-0112 / R-0741 / R-2886·R-2887 | 값 집합 소비 관련 | choices-literal | R-0112 는 architecture-ddd §3.2 의 상위 원칙(주어=도메인 enum 선언), R-0741 은 OpenAPI 응답 조립 축, R-2886·R-2887 은 SKILL 재진술 — **§8 ⓐ 재확인 대상** |

## 4. 조인 기구 — 3안 비교와 권고

`violation_adapter.py:44–62` `load_alias_map()` 은 `aliasText` 가 `"rule#"` 로 시작하는 것만 읽고(L60),
`convert()` L112–119 는 `rule is None` 이면 `tally["contract"]` 만 올리고 **`continue`** 한다.

| 안 | 내용 | 비용 | 위험 |
|---|---|---|---|
| **A. alias 대장 둘째 번호 공간**(권고) | `aliasText "contract#<검사기 파일명>"` 7건을 `wiring/aliases.ttl` 에 추가 | ⑥″ 문법 정규식 확장 + 원장 실재 축 분기 · 어댑터 접두 파싱 · 기대표 5→12 | 「검사기 이름이 규범의 별칭인가」라는 의미론 늘림 — **완화**: 값은 «이 검사기 계약 레인이 집행하는 유일 규범»이고 ⑥ 함수성 검사가 그 유일성을 문다 |
| B. 어휘 신설 `djr:contractLaneWork` | Checker → Work 프로퍼티 신설 | **어휘 v1 봉인 개정**(authoring §7) + 셰이프 신설 + 구조 검사 확장 + 어댑터 2경로 | 봉인 개정 폭이 A 의 몇 배인데 얻는 것은 이름뿐 |
| C. `enforcedBy` 역참조 직결 | 배선을 그대로 조인으로 | 0 | **불성립** — 1:12~19 이라 `maxCount 1` 위반, 집행 축 Work 혼입(§3.1) |

**권고 = A.** 근거: ⓐ `AliasEntry` 는 이미 «이 문자열이 저 Work 를 가리킨다»는 **지시 대장**이고, 필요한 불변식
(한 문자열 → 한 Work)이 ⑥ 함수성 검사와 **정확히 같다** ⓑ 어휘·셰이프 무개정이라 D12 가 승인한 «contract_ref
적재»의 문면 안에서 닫힌다 ⓒ 어댑터가 대장 하나만 읽는 현행 구조(재구현 금지 규율)를 유지한다.

**아니오라고 말한 것**: `contract_ref` 문자열 자체를 키로 쓰지 않는다 — «선행 계약(08-04 API-error) 소유»
하나가 3종(+혼성 2종)에 공유돼 **함수가 아니다**(§1 표 실측).

## 5. 이행 절차 (직렬 · 각 단계 실측 확인)

1. **`ontology/wiring/aliases.ttl`** — 7 노드 추가. IRI 규약은 authoring L143 `alias-<공간>-<번호>` 승계:
   ```
   djr:alias-contract-app-container a djr:AliasEntry ;
       djr:aliasFor djr:R-0122 ;
       djr:aliasText "contract#check-app-container.py" ;
       djr:aliasType djr:alias-unique .
   ```
   (동형 6건: `-choices-literal-consumption`→R-1186 · `-common-container`→R-3191 ·
   `-idempotency-scope-creep`→R-1662 · `-ninja-boundary-middleware`→R-0795 ·
   `-response-schema-bypass`→R-0091 · `-transient-overmapping`→R-1040)
2. **`workspace/tools/ontology_structural_check.py`** — ⑥″ 확장.
   - L57 `_ALIAS_TEXT_RE` → 두 공간 허용: `^(rule#[1-9][0-9]*|contract#check-[a-z0-9-]+\.py)$`
   - L99–101 원장 실재 검사 **축 분기**: `rule#` 은 현행대로 rule-owner-map 538행, `contract#` 은
     `reverse_coverage.PRIOR_CONTRACT_SCRIPTS` 7종 실재 + **`enforcedBy` 간선 실재**를 함께 요구
     (§3 기계 검증표를 fail-closed 로 고정 — 배선 없는 계약 조인 금지).
   - L164–175 self-test fixture **+3**: 「contract 문법 통과」·「PRIOR_CONTRACT 미실재 검사기」·
     「`enforcedBy` 간선 부재」 → 9/9 → **12/12**.
3. **`workspace/tools/violation_adapter.py`** —
   - `load_alias_map()` L60–61: `rule#` 하드코딩 제거, `aliasText` **원문 키**로 반환.
   - `convert()` L110–124: `rule is None and contract_ref` 이면 `alias.get("contract#" + r["checker"])`
     조회 → 성립 시 조인분과 **같은 경로**로 적재.
   - `tally` L107: `"contract"` → `"contract_joined"` / `"contract_unjoined"` **2분**(혼성 3종은 후자로
     남는다 — 침묵 탈락 금지 규율 유지). L209–211 보고 문면 동반 갱신.
   - `self_test()` L160–179: 합성 계약 레코드 1건(`rule=None`·`contract_ref`·`checker=check-app-container.py`)
     추가 단언 — 「R-0122 왕복」.
4. **`workspace/eval/fixtures/ontology_gate/target-counts.json`** L2 — `AliasEntryShape` **5 → 12**
   (골든 2 + rule 3 + **contract 7**). 사유 병기(authoring §15 ⑤ 무규율 갱신 금지).
5. **검사기 docstring 7건 «그래프 좌표(T2-2)» 블록** — «조인 확정: 없음(대장 미등재 — T3 이월)» 을
   «조인 확정: `contract#<파일명>` → `djr:<Work>`(대장 등재 · T3 게이트 조항 처분)» 로 교체.
   좌표(실측): app-container:40–43 · choices-literal:34–37 · common-container:30–33 ·
   idempotency-scope-creep:41–44 · ninja-boundary-middleware:25–28 · response-schema-bypass:13–16 ·
   transient-overmapping:43–46. (codex 쌍둥이 byte 동기 동반)
6. **`workspace/tools/ontology-authoring.md` L143** — alias 번호 공간이 둘임을 1행 신설
   (`rule#N` = 규칙 원장 · `contract#<검사기>.py` = 선행 계약 레인 · 후자는 `enforcedBy` 간선 동반 의무).
7. **검증**: `ontology_gate.py --write` → `structural_check --self-test`(12/12) → `--emit` 대조 →
   issued/ledger check → `make verify-ontology` 10/10 → 어댑터 `--self-test` → **계약 레코드 실물
   end-to-end 1건**(어느 한 검사기를 설치 표식 있는 임시 프로젝트에서 red 로 돌려 sink → ttl → pySHACL
   `conforms: True`) — T2-2 §4 가 남긴 실증 판형 그대로.

## 6. 부수 발견 — `violation_id` 산식에 검사기 축이 없다 (예방 처분 권고)

`violation_adapter._vid()` L95–98 의 키는 `(Work, 경로, 심볼[, 실런])` 인데 `ViolationShape-byChecker` 는
`minCount 1 · maxCount 1`(shapes L218–223)이다. **서로 다른 검사기가 같은 Work·파일·심볼에서 발화하면
둘째 블록이 L131–134 `seen` 에서 버려지고 살아남은 노드는 앞 검사기만 주장한다.** 오늘의 대장으로는 도달
불가(조인 7 + 3 이 전부 서로 다른 Work)지만, R-3191 처럼 **다중 집행자 Work** 가 이미 대장에 들어왔으므로
사거리 안이다. T2-4 리뷰 AQ-02 가 실런 축을 접미로 넣은 것과 **같은 형태의 결함**이다.
권고: 실런과 동형으로 **검사기 축을 접미 추가**(있을 때만 — 기존 노드 IRI 불변). T3 게이트 조항 처분과 같은
커밋에 넣지 말고 별건으로 분리한다(리팩터링·기능 변경 혼합 금지).

## 7. 범위 밖 — 혼성 3종의 계약 레인 (T3 이후 이월 명시)

`check-api-error-controller-contract.py:7107` · `check-composition-root.py:2201` ·
`check-error-centralization.py:4840` 은 **규칙 레인 + 계약 레인 겸용**(owner-map 행 11·18·4)이고, 그 계약
레인은 category 가 이질적이라(**api-error 는 규칙 범주 23 중 11이 이 형태** — t2-plan L49) 검사기 단위 상수
조인이 **성립하지 않는다**. 처분에는 `category → Work` 표가 선행하며, 그 표는 T2-1 귀속 매핑표
(`2026-08-19-ontology-t2-1-attribution-map.md`)의 후속이다. 본 메모는 이들을 `contract_unjoined` 로
**계수 보고**하도록 §5-3 에서 못박는다(침묵 탈락 금지).

## 8. 자인 약점

ⓐ **재진술 미확정 2건.** 웨이브 4 «재진술 소급 패스»가 아직이라 생산 그래프의 `djr:restates` 간선은
**0건**(실측)이다. 그래서 ① response-schema-bypass 의 R-0091(§6.2 오류 프로필) ↔ R-0688(§2.2 Operation
선언) ↔ R-2942(SKILL) ② choices 의 R-1186(§2.5) ↔ R-2886·R-2887(SKILL) ↔ R-0112(architecture-ddd §3.2)
가 **어느 쪽이 정본인지 그래프가 아직 말하지 않는다**. 본 메모는 검사기 자신의 근거 문면과 축자 일치하는
쪽을 골랐다. **재진술 패스 직후 이 2행을 재대조하고, 정본이 다르면 대장을 재지정한다** — 이 재확인을
웨이브 4 완료 기준에 넣어야 한다.

ⓑ **소유 문서 층위 불균질.** 7건 중 2건(R-1662·R-1040)의 소유 절이 스킬 정본이 아니라 `agents/*.md` 다.
에이전트 문서도 코퍼스 정본이고 Work 를 갖지만, 「규범의 집」으로는 스킬 정본이 더 자연스럽다. 특히
transient-overmapping 은 술어가 축자 일치하는 스킬 정본(R-2367)을 **주어 불일치로 기각**했다 — 이 판단이
과보수면 조인이 한 층 얕아진 것이다.

ⓒ **`check-common-container` 는 합성 Work 에 붙었다.** R-3191 은 세 칸을 한 문장에 묶은 규범이고, 판단표 v2
는 `#119` 를 «합성 규칙이라 함수적 alias 불가»로 **등재 취소**한 전례가 있다. 여기서는 방향이 반대(N 사건 →
1 Work)라 함수성은 깨지지 않지만, 「framework/ 자리」만 진술하는 원자 Work 가 정본에 없다는 사실은
**정본 결손 신호**일 수 있다(코퍼스 개정 후보).

ⓓ **`contract#<파일명>` 은 파일 이름을 규범 좌표에 넣는다.** 검사기 파일명이 바뀌면 대장이 조용히 끊긴다.
⑥″ 의 `PRIOR_CONTRACT_SCRIPTS` 실재 검사가 그 순간 red 를 내도록 §5-2 에 넣었지만, 이름을 좌표로 삼는 설계
자체의 부채는 남는다(대안: registry #N 순번 — 그것도 표 개정에 취약해 더 낫지 않다고 판단했다).

ⓔ **R-1662 의 절 좌표가 오독을 부른다.** 소유 절이 `### Error response contract 12-slot` 로 잡히는데
Work 자체는 멱등성 스코프 가드다 — 원문 `agents/design-architect.md` 가 그 `###` 아래(L41–86)에 일반 명세
항목 불릿(L64 «데이터(db)»)까지 담고 있어서다. **T3 저작 결함이 아니라 원문 제목 스코프의 결함**이지만,
그래프만 보는 소비자에게는 좌표가 거짓말처럼 읽힌다. 코퍼스 개정 후보로 등재한다.
