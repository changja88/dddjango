# T2-4 설계 판단표 v3 — SPARQL 규칙 팩 카탈로그 (C암 재료 ②)

> **상태**: 적용 **전**(구현 착수 직전). 적대 2레인(AP·AQ) → 중재 → **반증 레인 AR** → **사용자 결정 2건**을 모두 통과한 판이다.
>
> **이력**: v1 초판 → v2(리뷰 23건 + 자체 10건 — 핵심 설계 전복) → **v3(AR 4과제 전건 반박 성립 + 동결 개정 8·9)**.
>
> **증거 체인**: `…-t2-4-adversarial/` — PROMPT/log(AP·AQ·AR) · `SELF-FINDINGS.md` · `MEDIATION-AP-AQ.md` · `MEDIATION-AR.md`.
>
> **저자**: 자율 완주 모드(Claude). **일자**: 2026-08-20.

---

## §0. 이 문서가 정하는 것 / 정하지 않는 것

**정한다**: ⓐ 질의 카탈로그 4종의 입출력 계약과 파일 좌표 ⓑ 빌드타임(SPARQL) ↔ 런타임(무의존 조회) 경계 ⓒ **C암 selector의 자유도**(= C의 처치 정의) ⓓ B/C 공정 통제 ⓔ 폴백·계상 규약 ⓕ 골든·봉인·용량 로그 ⓖ 롤백 처분표.

**정하지 않는다**: 판정 산식(T2-0a 확정)·발주 선정(풀 등재 완료)·처치 A/B의 정의(개정 7 이후 불변)·규칙 팩의 T3 정본화(T2 게이트 후).

**동결 개정 = 2건 (사용자 승인 완료 · 2026-08-20 AskUserQuestion 직접 선택)**:
- **개정 8** «규칙 번호·명칭까지» — C 주입에 `<rules>` 블록(번호·명칭) 신설. 규범 본문은 미동봉(E8 무접촉). 블루프린트 §6·§12 기입 완료.
- **개정 9** «계수 후 유효 유지» — `rule=null`(선행 계약) 위반이 섞인 런은 유효 비교 유지·계수만. t2-plan §2 사전 등록 기입 완료.

v1이 상정했던 estimand 재작성(§4-R3 ⓑ — 본문 주입)은 **철회**했고, 그 자리를 개정 8이 최소 범위로 대체했다.

---

## §1. 실물 좌표 (2026-08-20 실측 · v2에서 M8·M9 정정)

기준 그래프 = `ontology/rules/*.ttl` + `ontology/wiring/*.ttl`(생산 그래프 — `shapes/golden/`은 픽스처이므로 제외). 엔진 = `.venv/bin/python` + rdflib 7.6.0.

| # | 실측 | 값 |
|---|---|---|
| **M1** | 생산 그래프 | Document 2 · Section 4 · Block **73** · Work 125 |
| **M2** | 파일럿 4절 | ddd `§3.2 엔티티` · ddd `§8 의사결정 요약` · ninja `§6.1 Status code mapping` · ninja `§6.2 dddjango-code-json 오류 프로필` |
| **M3** | 문면 커버리지 | Work 125 전건이 `statesNorm` 블록 보유 |
| **M4** | 검사기 배선 | `enforcedBy` 보유 Work **69/125(55.2%)** · `(w,c)` 쌍 **76** · 관여 검사기 **16종** · `delegatedTo` 보유 65 |
| **M5** | alias 조인 | `#N→Work` **3건 전량**(`rule#3→R-0124` · `rule#486→R-0118` · `rule#488→R-0120`) = 2.4% |
| **M5′** | T2-2 확정 격차 | 후보 발견률 5.2% ↔ **확정 조인률 0.7%** · 어댑터 실증 적재는 `#488` 7건 |
| **M6** | 경로 축 | `djr:pathGlob` 인스턴스 **0**(vocab 선언만) · SHACL 셰이프 **0**(`sh:path djr:pathGlob` 부재) |
| **M7** | 위반 레코드 | `schema·run_id·ts·record_id·rule·sentinel·contract_ref·checker·file·symbol·severity·message·expression` |
| **M8** | **검사기 축 실측(v2 정정)** | 텍스트 소유자는 **Block**이다. `check-api-error-controller-contract` = Work 31이지만 **고유 블록 14 · 5,306자**(Work 행 합계 13,303자는 **중복 포함 과대치**) · `check-error-centralization` = 고유 10블록 3,366자 · 검사기 도달 고유 블록 **총 30** |
| **M9** | **문면 분포(v2 정정)** | 규범 진술 **고유 블록 43** · min 30 · median **223** · p90 579 · max 1,658 · **합계 12,532자**(v1의 67,544자는 Work 행 중복 계상 — **5.4배 오기**) |
| **M9′** | 블록당 Work 분포 | 1개:17블록 · 2:6 · 3:6 · 4:7 · 5:3 · 6:1 · 7:1 · **11:2** — alias 3건은 **전부 같은 블록 `b9`**(11 Work 공동 진술) |
| **M10** | 절×검사기 교차 | §6.2 → api-error 28·error-central 19·openapi 5·기타 6 / §6.1 → api-error 3·ninja-boundary 2 / §3.2 → domain-model 3·layer-skeleton 3·기타 5 / §8 → layer-skeleton 1. 검사기 미연결 규범 §6.2 33·§3.2 11·§8 7·§6.1 5 |
| **M11** | 주입 코어 계약 | `regen_core.py` — `FIELDS=("rule","file","message")` 닫힘 · `select_records`의 변환은 **severity 필터·`rule is None` 제거·부분문자열 scope 3개뿐**(정렬·중복 제거·상한·우선순위 없음) · `payload`가 **입력 순서를 그대로 직렬화** |
| **M12** | **절차 정본의 금지**(v2 신설) | 「그 안에 들어가는 것은 위반의 `rule`·`file`·`message` 뿐이며 **규범 본문 정본은 재주입하지 않는다**」 — `commands/dddjango.md:143` · `codex-…/SKILL.md:166`(T2-3 저작·양 런타임 미러·`runtime_parity_check` 고정) |
| **M13** | 배포 경계(E7) | 규칙 팩 = 빌드타임 사전 렌더로 플러그인 동봉 · rdflib·pySHACL은 **설치본 침투 금지** |
| **M14** | 설치 cache 실측 | Claude `~/.claude/plugins/cache/…/2.11.0` · Codex `~/.codex/plugins/cache/…/2.11.0`(source 2.12.0) — 양쪽 모두 `findings.py`·`regen_core.py` **부재** |
| **M15** | 발주 | O-7(밀착·「재고 부족 409 거절 + 재고 차감 주문 생성 API」) · O-4(혼합) · O-5(비밀착·HTTP 표면 없음) |
| **M15′** | O-7 기록 실측 | 이력에서 복구 가능한 중간 red = `check-context-isolation.py`(rule `#3`) → **alias 정확 조인 성립**(폴백 0%). 나머지 검사기의 중간 red는 최종-green 기록만으로 복원 불가 |
| **M16** | 층화 비대칭 | C는 미이관 규칙에서 B와 동일 재료로 폴백 · C−B 대비는 밀착·혼합 층 한정 |
| **M17** | 스위치 값 공간 | T2-3 C3 **사용자 승인 확정** = `DJR_LOOP_ENABLED`(off/on) + `DJR_LOOP_SELECTOR`(**`snapshot`/`sparql`**). harness 실물은 현재 `snapshot` 한 값만 허용 |
| **M18** | 상시 검증 기준선 | `make verify` = exit 0 · **235.5초**(레인 AQ 실측) / **236초**(저자 실측) — 독립 2회 측정이며 3회 중앙값은 T2-4 전후 증분 계측 때 취한다 |
| **M19** | 커버리지 규율 | `reverse_coverage.plugin_files()`는 `rglob("*")` — **`.json`도 분류 대상**이며, 공용 모듈은 하드코딩 분기로 설명한다 |
| **M20** | 미결 이월 | `ViolationShape` minCount 1 ↔ D12 충돌(추인 목록) |

---

## §2-M. C암 처치의 확정 (**개정 8** — 2026-08-20 사용자 승인 «규칙 번호·명칭까지»)

### M0. 확정된 처치 (v3)

동결 §6은 C를 「SPARQL 선별 **규칙 팩**」으로 정의하는데 E8·절차 정본은 주입을 「위반의 `rule`·`file`·`message` 뿐」으로 닫아, **두 동결 문면이 충돌**했다(반증 레인 AR 과제 1 — 정지 조건 ② 성립·사용자 상정). 사용자 결정으로 다음이 확정됐다:

```
B(snapshot):  <violations>[{rule,file,message}, …]</violations>          ← T2-3과 byte 불변
C(sparql):    <violations>[{rule,file,message}, …]</violations>          ← 순서·구성은 그래프 선별
              <rules>[{rule|work, label}, …]</rules>                     ← 신설(번호·명칭만)
```

- **규범 본문(블록 리터럴)은 양 암 모두 미동봉.** E8의 「위반된 제약+핵심 맥락만 / 전체 규범 재주입 금지」와 「무접두 #N 축 = 번호+검사기 산출 발췌 한정」은 **무접촉·불변**이다.
- `label` = `skos:prefLabel`이며 E5가 「명칭만(정의는 블록 리터럴 소유)」으로 못박은 필드다. 명칭은 본문이 아니다.
- **개정 대상은 절차 정본 step 6′의 「rule·file·message 뿐」 문면 한 곳**이고, B의 프롬프트는 한 byte도 바뀌지 않는다.
- 용량: 최악 축(api-error 31규칙)의 명칭 합계 ≈ **1,200자** — 본문 주입안(5,306자)의 1/4이며 무관 문면 비중 문제(85.5%)의 노출도 그만큼 작다.

### M. 규범 **본문**은 주입하지 않는다 — v1 R3 철회 (유지)

v1은 C payload에 규범 전문(`norms` 배열)을 싣자고 했다. **철회한다.** 결정적 근거는 해석 논쟁이 아니라 **실물**이다(M12): 양 런타임의 절차 정본이 「규범 본문 정본은 재주입하지 않는다」를 명시하며, 이 문면은 T2-3에서 **저자가 직접 저작**해 미러·parity로 고정하고 T2-0b 봉인 대상으로 올려둔 것이다. E8의 「전체 규범 재주입 금지」도 축 독립 전칭 금지로 읽는 것이 옳다(AP-01).

보강 실측 2건:
- checker 축 전문 주입은 **85.5%가 무관 문면**이다(`#126` 위반 1건 기준 관련 5/31·1,930자 — AP-04). E8의 「위반된 제약+핵심 맥락만」과 정면 충돌한다.
- 다중 checker 합집합에서 v1의 상한(40/14,000)은 **120 검사기 쌍 중 8쌍에서 발동**하며 단위(자/bytes)도 미정이었다(AP-05).

### M′. 그래서 C는 무엇을 하는가 — selector 자유도

「엄격 해석이면 C가 공허하다」는 v1의 기각은 **틀렸다**(AP-02). `regen_core`가 현재 하지 않는 일이 곧 selector의 자유도다(M11):

| 자유도 | B(`snapshot`) | C(`sparql` — 그래프 경유) |
|---|---|---|
| **순서** | 검사기 방출 순서 | **문서 경로 → 절 번호 → 블록 서수 → Work ID** |
| **묶음** | 없음 | **같은 Work를 진술하는 위반끼리 인접**(블록 단위 아님 — M‴) |
| **중복 제거** | 없음(exact 중복도 남음) | `identity()` 단위 |
| **우선순위** | 없음 | tier 1 alias 정확 조인 → tier 2 검사기 조인 → tier 3 미조인 |
| **재료** | `<violations>`만 | `<violations>` + **`<rules>`(번호·명칭)** — 개정 8 |
| **범위** | 부분문자열 scope | (T2-4에서는 미사용 — §3-Q1) |

`<violations>` 배열의 필드는 `(rule,file,message)` **불변**이고, `payload`가 입력 순서를 그대로 직렬화하므로 순서·구성 차이가 실제 byte 차이로 나타난다. `<rules>`는 **C에만 존재하는 두 번째 블록**이며, `<violations>` 블록의 형상(최상위 배열)은 손대지 않으므로 **B의 출력은 구조적으로 byte 불변**이다.

### M‴. 묶음 키는 **Work**다 — 블록이 아니다 (반증 레인 AR 과제 3)

v2는 「같은 블록을 건드린 위반끼리 인접」이라 썼다. **틀렸다.** 블록 `b9`는 11개 Work를 함께 진술하는데 그 11개는 한 문단의 원자 분해가 아니라 **이질 규범**이다 — Obligation 5 · Exception 4 · Prohibition 2이며, R-0124(컨텍스트 간 접근 ACL·OHS)와 R-0118(빈 패키지 실현)은 주제도 다르다. 따라서 묶음·정렬 키는 **Work**로 내리고, 블록은 `order_key`의 한 성분(`block_order`)으로만 쓴다. 이질 블록이 26개(최대 11 Work) 존재한다는 사실을 자인 목록에 남긴다(W11′).

### M″. 한정 문구 (리포트 내장 의무 · v3 갱신)

C의 처치는 **선별 층 + 선별 결과의 번호·명칭 제시**이며 **규범 본문 제공이 아니다**. C−B가 무효과로 나와도 그것은 「그래프 재료가 무용하다」의 증거가 아니라 **「선별과 명칭 제시만으로는 부족하다」**의 증거다. 이 문장을 A/B 리포트와 T2 종료 게이트 보고에 그대로 싣는다.

---

## §2. 판단 P — 규칙 팩의 구조

### P1. SPARQL은 빌드타임 전용, 런타임은 무의존 조회 — 유지

E7 배포 경계(M13)와 설치 cache 실행(M14) 때문이다. 팩은 커밋되는 산출물이고 T2-0b에 봉인된다. `make rulepack`은 `$(VENV_PY)`를 쓴다.

### P2. 설치본 팩 = **인덱스 + 명칭**(본문 미동봉) — v3 개작

- 경로: `dddjango/scripts/rulepack.json` + **codex 미러** `codex-dddjango/skills/dddjango/scripts/rulepack.json`(`make verify`의 `diff -rq`가 강제).
- **문면(`text`)은 싣지 않는다. 명칭(`label` = `skos:prefLabel`)은 싣는다**(개정 8 — `<rules>` 블록 재료). 팩에 블록 리터럴이 **존재하지 않으므로** M12의 본문 금지가 구조적으로 지켜진다: 코드가 실수해도 실을 본문이 없다.
- 스키마 `rulepack/1`:
  ```
  { "_generated": "ontology_rulepack.py — 직접 편집 금지",
    "schema": "rulepack/1",
    "built_from": [{"path": <저장소 상대>, "sha256": …}],
    "works":    { "R-NNNN": {"label","document","section","section_number","block","block_order",
                             "expression","checkers":[…],"aliases":[…]} },
    "by_alias":   {"#488": "R-0120"},
    "by_checker": {"check-….py": ["R-…", …]},
    "by_path":    [{"glob": …, "section": …, "works": […]}],
    "order_key":  {"R-NNNN": [document, section_number_natural, block_order, "R-NNNN"]} }
  ```
- **배열 정렬 키 전수 고정**(AQ-11 — `sort_keys`는 배열을 정렬하지 않는다): `built_from`=경로 사전순 · `checkers`/`aliases`=문자열 사전순 · `by_checker[*]`/`by_section works`=`order_key` 순 · `by_path`=glob 사전순.
- 직렬화: `json.dumps(…, ensure_ascii=False, indent=2, sort_keys=True)` + 말미 개행.

### P3. 팩은 **투영물**이다 — v2 신설

E1의 투영물 규율(직접 편집 금지·CI가 «투영물==render(그래프)» 검증)이 그대로 붙는다. `_generated` 표지 + V2 재현성 검사가 그 이행이다.

### P4. 생성·검증의 2단 — 유지·정밀화

- `make rulepack` = 재생성. `make verify`에는 **임시 경로 재생성 후 diff 0** 검사만(읽기 전용 유지).
- **상시 verify = V1~V4·V6·V8~V10 / 변이 V5·발화 probe V7 = 별도 타깃**(AQ-10). 기준선 235.5초(M18) 대비 증분을 T2-4 전후 동일 명령 3회 중앙값으로 기록한다.

### P5. `expression` 병기 — 유지 (E6)

### P6. 미연결 규범 56건 — 팩에는 싣되 selector 진입로 없음. **생성 리포트에 계수 명시**(침묵 탈락 금지)

### P7. 팩은 파일럿 범위만 — 유지. 팩 밖 규칙은 tier 3(폴백)

### P8. 생성기는 저장소 전용 · 조회 모듈은 무의존 — 유지

`workspace/tools/ontology_rulepack.py`(rdflib) / `dddjango/scripts/rulepack.py`(stdlib·python3.9·양 런타임 미러).

### P9. `reverse_coverage` 등재 — v2 신설 (AQ-06)

`rulepack.py`·`rulepack.json` 둘 다 하드코딩 분류 분기에 존재 근거를 등재한다(M19). 미등재 시 `make verify` **확정 red**.

---

## §3. 판단 Q — 사전 검증 질의 카탈로그 4종

질의 원문은 `workspace/tools/queries/*.rq`에 파일로 둔다.

### Q1. 경로/디렉터리 → 적용 규범 — **처치 밖 분석 카탈로그**로 명시 (AP-08)

- **파일**: `q1-path-to-norms.rq` · **입력**: 저장소 상대 POSIX 경로 · **출력**: `[{work, section, checkers[]}]`(`order_key` 정렬).
- **처치 미사용 선언**: T2-4의 C selector는 경로 축을 쓰지 않는다. Q1은 횡단 조회용이며 **C 효과 주장에 사용하지 않는다**. 사유: 위반 레코드가 이미 `checker`를 운반하므로 경로 축은 selector에 추가 정보를 주지 않는데, 처치에 넣으면 O-7 사후 맞춤 의혹만 떠안는다.
- **글롭은 기계 유도**(수기 저작 금지 — AP-08): 검사기 로스터의 대상 경로 선언에서 유도해 `ontology/wiring/paths.ttl`로 저작하고, 유도 스크립트와 입력을 커밋한다. 유도 입력은 O-7 산출물과 무관하며 **암 산출물 관측 전** 봉인한다.
- **문법 폐쇄 정의**(AP-09·AQ-07 — 저작 **선행** 조건): 값은 `xsd:string` 단일 · 저장소 상대 POSIX 경로 · 절대 경로·`\`·`..` 금지 · `*`=한 세그먼트 내 임의, `**`=0개 이상 세그먼트 · 전체 일치(prefix 일치 아님) · case sensitive.
- **검증 선행 — 두 게이트를 분리한다**(AR 4-4 — AQ-07과 AP-09는 같은 축이 아니다):
  - **정적 무결성 게이트**(AP-09): ⓐ SHACL 셰이프(주어 클래스=`djr:Section` 한정·datatype·pattern) ⓑ 구조 검사(중복·포함 관계·전역 glob 충돌·검사기 대상 경로와의 coverage/overlap) ⓒ valid/invalid 골든 쌍.
  - **런타임 matcher conformance 게이트**(AQ-07): 조회 모듈의 매칭 구현이 위 문법 정의와 **행동으로 일치**함을 케이스 표로 고정한다. 정적 셰이프가 통과해도 matcher가 다르게 동작할 수 있다.
  - **둘 다 green이기 전에는 `paths.ttl`을 생산 그래프에 넣지 않는다.**
- **골든**: 양성 2(도메인 층·API 층) + **음성 2**(유사하나 매칭되면 안 되는 경로).

### Q2. 위반 이력 → 관련 규범 (**실험 런 한정**) — 실물 배선을 T2-4 범위로 편입 (AQ-02)

- **파일**: `q2-violations-to-norms.rq` · **입력**: `experiment_run_id` 필수 바인딩(미바인딩 = exit 1, fail-closed) · **출력**: `[{work, violation_count, checkers[]}]`.
- **현 실물의 결함 2종**(재현 확인):
  - `findings/0` 레코드에 `experiment_run_id`가 **없다**. `run_id`는 「검사기명+시각+pid」인 **프로세스 ID**이고 어댑터가 그대로 `djr:runId`로 옮긴다.
  - 어댑터 노드 ID가 `(Work,파일,심볼)`뿐이라 **런이 달라도 같은 위반이면 뒤 런을 버린다**(실측: `joined 2` → Violation 노드 1 · `runId "exp-A"`만 잔존).
- **처분**: ⓐ `findings.py`에 `experiment_run_id` 필드 신설(env `DJR_EXPERIMENT_RUN_ID`·미지정 시 null) → sidecar → 수집기 → 어댑터 전 사슬 운반 ⓑ 어댑터 사건 노드 = `hash(experiment_run_id, canonical identity)` — **런 안에서는 중복 제거, 런 간 재발은 별개 사건** ⓒ 27종 계수 골든이 레코드 필드 집합을 비교하면 `--emit-expected` 1회 기계 갱신(T2-1 전례).
- **골든**(AQ-05 — 공허 통과 방지): 같은 픽스처에서 **`query(A)=기대 Work·계수(양성)` ∧ `query(B)=0`(음성)** 동시 단언 · 동일 identity가 A·B 양쪽 재발 시 **양쪽 1건** · `$RUN` 미바인딩 exit 1 · FILTER 제거 변이 = cross-run leakage red · always-empty 변이 = red.

### Q3. 절/문서 단위 묶음

- **파일**: `q3-section-bundle.rq` · **입력**: 절 IRI 또는 절 번호 · **출력**: `{section, heading, blocks:[{order, kind, text, states_norms[]}]}`(블록 순서 보존·**블록 1개당 1행**, Work 행 복제 금지 — AQ-01).
- **용도**: 투영 렌더·분석. **주입 재료 아님.**
- **골든**: ninja §6.1(17블록) 1건.

### Q4. 주입 조립 — **정렬 키 질의**로 정명 (v2 개작)

- **파일**: `q4-injection-order.rq` · **입력**: Work 집합 또는 검사기 집합 · **출력**: `[{work, order_key:[document, section_number, block_order, work], block, checkers[]}]`.
- v1은 이 질의가 「번호+발췌」를 낸다고 했으나, E8의 「발췌」는 **검사기 산출 발췌**(`message`)이고 그것은 이미 위반 레코드가 운반한다. 따라서 Q4의 실제 산출은 **팩의 `order_key`/`by_checker` 물질화**다.
- **결정성 의무**: 같은 입력 → 같은 순서. 이것이 팩 byte 재현성의 근거다.
- **골든**: `check-openapi-error-declaration.py` 1건(Work 5·고유 블록 2).

---

## §4. 판단 R — C암 배선과 공정 통제

### R1. selector 파이프라인 — 순서 고정 (SF-4)

```
① 게이트 sidecar(--introduced-json) = 귀속 N∖L        + companion sidecar(rule=null 계수)
② select_records(records, scope, severity="violation")      ← B·C 공통·무변경
③ [C만] 팩 조회로 tier·order_key·work 부여
④ [C만] identity() 단위 중복 제거
⑤ [C만] (tier, order_key, identity) 정렬 — Work 단위 묶음은 정렬의 자연 결과
⑥ [C만] <rules> 재료 조립 — 등장한 Work 집합 → {rule|work, label}(order_key 정렬·중복 제거)
⑦ assemble_prompt(records, rules=None|[…])                  ← 조립기 확장(B는 rules=None)
```
- 팩 조회는 **②의 출력만** 입력으로 받는다(전체 findings 아님) — 귀속 밖 위반이 새지 않는다.
- **B 경로는 ③~⑥을 건너뛰고 ⑦에 `rules=None`을 넘긴다.** `rules=None`이면 `assemble_prompt`는 T2-3과 **byte 동일한 문자열**을 낸다(V3 골든이 고정).
- **`<rules>` 항목의 출처**: tier 1은 그 Work 1건, tier 2는 그 검사기가 집행하는 Work 전량, tier 3은 없음. 무관 규칙 비중(AP-04 실측 85.5%)은 명칭 수준에서 노출되며, 이 한계를 헤더에 **정직하게** 쓴다 — 「아래 `<rules>`는 위반한 검사기가 **집행하는** 규칙 목록이며 전부가 이번 위반은 아니다」.

### R2. tier 정의

| tier | 조건 | 정렬 키 |
|---|---|---|
| 1 | `by_alias[rec.rule]` 적중 | 그 Work의 `order_key` |
| 2 | `by_checker[rec.checker]` 적중 | 그 검사기 집행 Work들의 **최소** `order_key` |
| 3 | 어느 축도 미적중(팩 밖) | 정렬 키 없음 — tier 2 뒤에 **원래 순서 보존**으로 배치 |

tier 3이 곧 **폴백**이며 B와 같은 상대 순서를 유지한다(M16 층화 비대칭의 기계적 실현).

### R3. 상한 — **두지 않는다** (v2 개작 · AP-05 채택 결과)

주입 재료가 B와 동일해졌으므로 C만 상한을 두면 그 자체가 비대칭 처치가 된다. 또 발동하지 않는 상한은 검증되지 않는 죽은 코드다(v1 W5의 함정). `prompt_bytes`는 **노출량 공변량**으로 기록만 한다. 상한이 필요해지면 T3에서 사전 등록 후 도입한다.

### R4. 조립기 — **최소 확장 + B byte 불변** (v3 · AP-06·SF-2 반영)

- `payload()`는 **무변경**(최상위 배열 유지).
- `assemble_prompt(records, rules=None)`로 인자 하나만 연다. `rules=None`이면 반환 문자열이 **T2-3과 byte 동일**하다 — 헤더·푸터·`<violations>` 블록 어디도 조건부 공백이 끼지 않게 «rules가 있을 때만 뒤에 두 요소를 덧붙이는» 형태로 구현하고, V3 골든이 이를 고정한다.
- `<rules>` 블록도 같은 canonical JSON + `<`·`>` 유니코드 escape를 적용한다(`</rules>`가 명칭 안에 들어가도 경계가 깨지지 않는다 — V4).
- **필드 계약 갱신**: `RULE_FIELDS = ("rule", "label")`. 이 집합이 계약이며 늘리려면 개정이 선행한다(개정 8이 정한 범위 = 번호·명칭).

### R5. 계상 의무 — v3 (개정 9 반영)

- **`uninjectable_n`**(AP-03·AR 과제 2): `ContractFindings`(`rule=null`)는 `[#N]` 표식이 없어 **게이트 sidecar에 애초에 들어가지 않는다** — 「필드 이름만 추가하면 된다」는 v2의 처분은 셀 원자료가 없었다. **companion sidecar**(`--contract-json`)를 신설해 검사기별 `rule=null` 레코드 수를 step 6′까지 운반한다.
- **처분은 사전 등록됨**(2026-08-20 사용자 승인 «계수 후 유효 유지»): 이런 런은 **유효 비교에 그대로 남긴다.** 제외 문턱을 두지 않는다. 사유: 세 암이 같은 조건이라 편향이 없고, n=2에서 제외 규칙은 유효 표본만 줄인다. 런마다 계수하고 리포트에 비율을 병기한다.
- **`fallback_n`**(tier 3) · **`hit_ratio = (tier1+tier2)/전체`** = 처치 dose.
- **유효성 문턱 사전 등록**(AP-10): 밀착·혼합 층에서 `hit_ratio = 0`인 런은 **uninformative**로 분류해 C−B 유효쌍 분모에서 제외한다(처치가 정확히 0인 런). `hit_ratio < 0.5`는 **희석 런**으로 분리 보고하고 전 구간 sensitivity를 병기한다. — 이 문턱은 `rule=null` 처분(위)과 **별개 축**이다.
- **레코드별 provenance 보존**(AP-X1 · AR 4-3): 집계치만으로는 재현이 안 된다. 위반마다 `{record_id, join_type, work, block, order_key, group_key, priority, drop_reason}`을 남긴다.

### R6. 스위치 = `DJR_LOOP_SELECTOR` ∈ {`snapshot`, `sparql`} — **원복** (AQ-04)

v1의 `plain|rulepack`은 T2-3 C3에서 **사용자 승인으로 확정된 값 공간**(M17)을 저자가 임의 표류시킨 것이다. 원복한다. 미지정 = `snapshot`. 값 공간 밖 = **즉시 실패**(조용한 폴백 금지).

### R7. 팩 부재·손상 = fail-closed — 유지. 단 §8의 선행 게이트로 «cache probe green 전 실런 금지»를 둔다(AP-07)

### R8. 어댑터 canonicalizer 단일화 — v2 신설 (AQ-03)

`violation_adapter._vid()`가 `regen_core.identity()`를 쓰지 않고 raw `file`을 해시한다(실측: `a.py:3`↔`a.py:4`가 identity로는 동일인데 어댑터는 **노드 2개** 생성). 경로 정규화 + canonical identity를 공용 함수로 승격해 루프·어댑터·scorer가 같은 구현을 호출한다. 줄 이동·절대/상대 경로·`symbol=null` 조합을 공통 골든으로 고정한다.

---

## §5. 판단 V — 검증 자산

| # | 자산 | 검출 대상 | 상시/별도 |
|---|---|---|---|
| **V1** | 질의 골든 4쌍(Q1 양성 2·음성 2 포함·Q2 양성+음성) | 질의 변조·정렬 비결정성·공허 통과 | 상시 |
| **V2** | 팩 재현성(임시 재생성 → byte diff 0) | 팩 노후·수기 편집 | 상시 |
| **V3** | **B 경로 byte 회귀**(`snapshot` 출력이 T2-3 골든과 동일) | 공정 통제 파손 | 상시 |
| **V4** | injection self-test(기존 유지) | 주입 경계 | 상시 |
| **V5** | **변이 자가검사 8종** — ① 정렬 키 제거 ② tier 우선순위 무시 ③ alias 축 무시(**골든에 `#488` 필수**) ④ 중복 제거 제거 ⑤ 폴백 침묵 처리 ⑥ 배열 역순 삽입에도 팩 byte 동일 ⑦ selector 무시(항상 `snapshot` 동작) ⑧ `<rules>` 블록 누락. **비용 계측 동반**(AR 4-2): 동일 환경·동일 명령으로 변경 **전/후 각 3회 median**, 절대·비율 증분, 실패 문턱을 함께 기록 | 검출력 | 별도 타깃 |
| **V6** | 커버리지 리포트(도달 불가 규범·미배선 검사기·alias 수) + 로스터 정합 | 침묵 탈락·검사기 이름 표류 | 상시 |
| **V7** | **발화 증명 probe**(AQ-04 — 「가장 위험한 단일 결함」) | 아래 별항 | 별도 타깃 |
| **V8** | `reverse_coverage` 등재 확인 | 새 파일 미분류 red | 상시 |
| **V9** | 어댑터 canonicalizer 공통 골든 | R8 회귀 | 상시 |
| **V10** | 배열 정렬 결정성(입력 순서 셔플 → 팩 byte 동일) | AQ-11 | 상시 |

### V7 — 발화 증명 probe (신설·최중요)

`plugin_loop_probe.py`를 확장해 **acceptance matrix = {materialized Claude 트리, materialized Codex 트리, Claude 설치 cache, Codex 설치 cache} × {아래 5 단언}**을 전건 실행한다(AR 4-1 — 이름만 남기고 축약하지 않는다). 동일 red 픽스처를 쓴다.

1. `snapshot`은 T2-3 프롬프트 byte를 그대로 낸다.
2. `sparql`은 **같은 위반 집합**에 대해 **다른 순서/구성 + `<rules>` 블록**을 낸다(byte 상이 · `<violations>` 집합 동일 · `<rules>` 비어 있지 않음).
3. 두 런타임의 `sparql` 프롬프트 해시와 `tier/hit/fallback` 로그가 **일치**한다.
4. 미지 selector 값·손상 팩은 **nonzero** 종료.
5. selector를 고의로 무시하는 변이가 **red**가 된다.

**사유**: 팩·코드·문서 parity가 모두 green이면서도 실제 셸 B가 여전히 `snapshot`만 조립할 수 있고, 그러면 18런이 `B=B′` 비교가 되어 **전량 무효**가 된다. 「파일이 존재한다」는 「처치가 발화했다」가 아니다.

---

## §6. 측정 부록 — 회전 로그 (v2 개작)

```
schema: "injection-capacity/2"
{ run_id, experiment_run_id, selector, rotation,
  violations_n, rules_n, prompt_bytes,
  tiers: {t1: n, t2: n, t3: n}, hit_ratio,
  deduped_n,
  uninjectable: {total: n, by_checker: {<checker>: n}},      # companion sidecar 유래
  records: [{record_id, identity, join_type, work, block,
             order_key, group_key, priority, drop_reason}] } # 레코드별 provenance(AR 4-3)
```

- 회전마다 1행 · 경로 = 런 산출물 폴더(run namespace).
- `arm` 필드는 **두지 않는다**(발주 봉인의 arm 비노출 — SF-7). arm 대응은 채점 측이 allocation 표로 조인한다.
- **한계 문구 내장**: 토큰 매칭 estimand 분리는 규모상 미실시. `prompt_bytes`는 공변량이지 통제 변수가 아니다.

---

## §7. 자인 약점 (v2)

| # | 약점 |
|---|---|
| **W1′** | **C의 처치가 여전히 약할 수 있다.** 정렬·묶음·중복 제거·우선순위 + 규칙 **명칭** 목록이 위반 수를 줄인다는 직접 증거는 없다. 명칭이 coder에게 실제로 유용한지는 미검증이며, 무관 규칙이 명칭 수준으로 섞인다(tier 2에서 최대 31건 중 관련 5건 — AP-04). 무효과가 나와도 「그래프 재료 전반이 무용」을 뜻하지 않는다(§2-M″). |
| **W11′** | **이질 블록이 26개**(최대 11 Work)다. 묶음 키를 Work로 내려 정렬은 정확해졌지만, `order_key`의 `block_order` 성분은 여전히 이질 블록을 한 자리에 모은다 — R-0124(ACL·OHS)와 R-0118(빈 패키지)이 인접 정렬된다. 이 인접이 모델에 잘못된 연관을 시사할 수 있다. |
| **W12′** | `<rules>` 헤더가 「전부가 이번 위반은 아니다」를 밝히지만, **모델이 그 경고를 따를지는 통제 불가**다. 무관 규칙을 «준수»하려다 범위 밖 수정이 나면 `scope_violation`으로 잡히지만(T2-3), 범위 **안**의 불필요 수정은 잡히지 않는다. |
| **W2′** | alias 축이 2.4%라 tier 1은 사실상 3건에서만 발동한다. C의 실질 축은 tier 2(검사기)이고, 그 정렬 키는 **검사기 집행 Work들의 최소 order_key**라는 거친 대리값이다. |
| **W3′** | tier 2 정렬은 같은 검사기의 위반을 전부 같은 위치로 보내므로, **한 검사기 안의 세부 규범 차이를 구분하지 못한다**. |
| **W4′** | Q1을 처치 밖으로 선언했으므로 「경로 → 규범」 축은 T2에서 시험되지 않는다. 카탈로그에는 있으나 처치에는 없다는 비대칭을 리포트에 명시해야 한다. |
| **W5′** | `paths.ttl` 저작은 여전히 새 데이터다. 기계 유도로 독립성을 확보했지만 **유도 규칙 자체**가 저자의 판단이다. |
| **W6′** | AQ-02 처분(`experiment_run_id` 전 사슬 신설)은 `findings/0` 스키마를 건드린다. 27종 계수 골든이 깨지면 기계 갱신하지만, **갱신 자체가 T2-1 산출물을 다시 여는 일**이다. |
| **W7′** | 팩은 T2-0b에 봉인되지만 그래프는 T3에서 계속 바뀐다. 봉인 후 그래프 변경 시 V2가 red를 내는데, **실런 도중이면 처분이 애매**하다(T2-0b에서 확정). |
| **W8′** | `by_checker` 키가 검사기 파일명이라 이름 변경 시 조용히 tier 3으로 흘러간다. V6가 로스터 정합을 보지만 이름 변경은 T2 동결 중 금지 사항이라 방어가 약하다. |
| **W9′** | 팩은 T2 파일럿 한정 설계다. T3 전량 이관 시 단일 JSON 구조는 유지 불가하다. |
| **W10′** | C 패배 시 원인이 ⓐ 선별 층 무용 ⓑ tier 2 대리값 조악 ⓒ 커버리지 부족(tier 3 다수) 중 무엇인지 **판정 산식으로는 구분되지 않는다**. `tiers`/`hit_ratio` 사후 층화 보고를 사전 등록해 구분을 **시도**하되, 표본상 신호는 기대하지 않는다(탐색적·판정 산입 금지). |

---

## §8. 구현 순서

0. **선행 게이트**: T2-0b의 cache probe(source ↔ Claude cache ↔ Codex cache 버전·tree SHA·팩 SHA)가 green이기 전에는 **C 실런을 시작하지 않는다**(AP-07·M14).
1. Q1 **두 게이트**(정적 무결성 · 런타임 matcher conformance) → 통과 후 글롭 **기계 유도** → `ontology/wiring/paths.ttl` 저작.
2. 질의 4파일 + 골든(양성·음성) 저작 — **구현보다 먼저**.
3. AQ-02 실물 배선: `findings.py` `experiment_run_id` → sidecar → 수집기 → 어댑터 런별 사건 노드. **R8(canonicalizer 단일화)** 동반.
4. **companion sidecar**(`registry_gate --contract-json`) — `rule=null` 레코드 계수를 step 6′까지 운반(개정 9).
5. `workspace/tools/ontology_rulepack.py`(생성기·리포트·`--check`) + `make rulepack`.
6. `dddjango/scripts/rulepack.py`(무의존 조회) + **양 런타임 미러**(`.py`·`.json` 둘 다).
7. `regen_core`: `assemble_prompt(records, rules=None)` 인자 1개 확장 + `RULE_FIELDS`. **V3 골든(B byte 불변) 먼저.**
8. selector 배선(`sparql` — R1 ③~⑥) + 회전 로그(레코드별 provenance) + 양 런타임 step 6′ 개정 8 문면.
9. `reverse_coverage` 등재(P9) → V1~V10 + `make verify` 편입(상시/별도 분리) → **변경 전/후 3회 median** 증분 계측.
10. 사후 산출 1레인 → 중재 → 조감도 HTML 갱신 → 커밋.

---

## §9. T2-0b manifest fragment (v2 — provenance/최종 분리)

- `parent_scripts_tree_sha256`(**provenance 전용**) = `51f0f9f075863a7d41745da9bb27fd7726d06c7e3142c7f76fa54bb88fd1dc91`(T2-3 완료 시점). **검사 기준값이 아니다**(AP-X2·AQ-08).
- **최종 봉인**(T2-4 완료 후 재계산): source Claude/Codex scripts tree sha256 · **양 설치 cache** tree sha256 · `rulepack.json` sha256(양쪽) · `rulepack.py` sha256(양쪽) · `regen_core.py` sha256.
- 질의 4파일 sha256 · `paths.ttl` sha256 + 유도 스크립트·입력 sha256 · 골든 sha256 · 변이 스크립트 sha256.
- `DJR_LOOP_SELECTOR` 값 공간 단언(`snapshot|sparql`) · 미지정 기본값 · `DJR_EXPERIMENT_RUN_ID` 전달 경로.
- 회전 로그 schema/version(`injection-capacity/2`) · `hit_ratio` 유효성 문턱(0 = uninformative · <0.5 = 희석).
- **설치본 신선도 ⓓ**(T2-0b 선행조건 추가): 양 cache에 `rulepack.json`·`rulepack.py` 실재 + source 해시 동등 + 스키마 파싱 성공 + V7 probe green.

---

## §10. 롤백 처분표 (v2 신설 · AQ-09)

| 자산 | C 승리 | C 패배 | 판정불능 |
|---|---|---|---|
| `paths.ttl` · 질의 4종 | 유지 → T3 정본화 | **유지**(분석 카탈로그 — 처치 밖) | 유지 |
| `ontology_rulepack.py` | 유지 | 유지(저장소 도구) | 유지 |
| `rulepack.json`(설치본·양 런타임) | 유지 | **제거** | 보류(tombstone 표기) |
| `rulepack.py`(설치본·양 런타임) | 유지 | **제거** | 보류 |
| selector `sparql` 분기 · `<rules>` 블록 | 유지 | **제거**(값 공간을 `snapshot`으로 축소 · `assemble_prompt`의 `rules` 인자 제거) | 비활성(값은 남기되 fail-closed) |
| 절차 정본 step 6′의 개정 8 문면 | 유지 | **원복**(「rule·file·message 뿐」) — 양 런타임 미러 | 유지 |
| companion sidecar(`rule=null` 계수) | 유지 | **유지**(실험 무관 관측 자산) | 유지 |
| 회전 로그 | 유지 | 유지(관측 자산) | 유지 |
| `experiment_run_id` 사슬 · R8 canonicalizer | 유지 | **유지**(실험 무관 결함 수리) | 유지 |
| 양 런타임 step 6′ | 무변경 | 무변경 | 무변경 |
| Make 타깃 | 유지 | `rulepack` 제거 | 유지 |

**롤백 검증 의무**: C 패배 처분 후 ⓐ B 프롬프트가 V3 골든과 다시 byte 동일 ⓑ 설치본에서 `sparql` 발화가 **불가능**함을 probe로 확인한다.

---

## §11. 개정 이력

- **v1 (2026-08-20)**: 초판.
- **v3 (2026-08-20)**: **반증 레인 AR 4과제 전건 «반박 성립»** + **사용자 결정 2건** 반영. ① **개정 8**(사용자 «규칙 번호·명칭까지») — C 주입 = `<violations>` + **`<rules>`(번호·명칭)**, 본문은 여전히 미동봉·E8 무접촉. 동결 §6과 절차 정본의 충돌을 사용자가 절차 정본 개정으로 해소 ② **개정 9**(사용자 «계수 후 유효 유지») — `rule=null` 런은 유효 비교 유지·companion sidecar로 계수만 ③ 묶음 키를 블록 → **Work**로 정정(AR 과제 3 — `b9`의 11 Work는 원자 분해가 아니라 이질 규범: Obligation 5·Exception 4·Prohibition 2) ④ `uninjectable_n`은 필드 추가로 안 되고 **companion sidecar 신설**이 필요함을 확인(AR 과제 2 — 저자의 「docstring 계약」 주장은 **사실관계 오류**였다: 실물은 1줄 구현 주석이고 호출자 미이행) ⑤ V7을 **4트리 × 5단언 acceptance matrix**로 복원(AR 4-1) ⑥ V5에 변경 전/후 3회 median 비용 계측 편입(AR 4-2) ⑦ 로그에 **레코드별 provenance** 복원(AR 4-3) ⑧ AQ-07(런타임 matcher)과 AP-09(정적 셰이프)를 **별도 게이트**로 유지(AR 4-4) ⑨ W11′·W12′ 자인 신설.
- **v2 (2026-08-20)**: 적대 2레인(AP·AQ) 23건 + 자체 10건 반영 — 채택 21·부분 채택 2·기각 0. **핵심 전환**: ① 규범 문면 주입 철회(AP-01 — 절차 정본 M12가 결정적) ② C 처치를 selector 자유도로 재정의(AP-02) ③ 설치본 팩을 인덱스 전용으로(문면 미동봉) ④ 상한·강등 사슬 폐기(AP-05) ⑤ `assemble_prompt` 무변경 확정(AP-06) ⑥ 스위치 값 공간 원복(AQ-04) ⑦ M8·M9 수치 정정(AQ-01 — 블록 43·12,532자) ⑧ `experiment_run_id` 사슬·어댑터 canonicalizer를 범위 편입(AQ-02·AQ-03) ⑨ Q1을 처치 밖으로 명시 + 글롭 기계 유도·셰이프 선행(AP-08·AP-09) ⑩ V7 발화 증명 probe·V8~V10 신설 ⑪ 롤백 처분표 신설(AQ-09).
