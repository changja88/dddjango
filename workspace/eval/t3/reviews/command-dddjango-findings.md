# T3 적대 리뷰 — command-dddjango spec/worksheet 발견 기록

- 대상: `workspace/eval/t3/specs/command-dddjango.spec.json` + `workspace/eval/t3/worksheets/command-dddjango.md`
- 리뷰 방법: 4렌즈 전수(경계·kind / 규범 식별 / 배선 / 재진술). 원문 `dddjango/commands/dddjango.md`(187행) 전문 실독, 27종 `check-*.py` docstring 선두 전수 실독, `checker_target.py`·`ontology_migrate.py`·`sections.tsv`·`LEDGER.tsv` 실물 대조, 독립 커버리지 검증 스크립트 실행.
- 판정: **pass = false** (medium 4건).

## 독립 검증으로 확인된 사실 (반박 불성립 — 기록)

- 블록 연속·비중첩·절 끝까지 전체 커버(1–187행) 성립, 무소유 규범 0, class 5종 전건 유효, kind 계수 norm 114·prose 5·code 1 = 블록 120 — 독립 스크립트로 재검증 완료.
- 절 경계 11개 전건이 현재 파일 헤딩과 정확 일치(드리프트 재확정 이행). s001~s006·s008~s011 스팬 해시가 센서스 기준선과 일치, s007 현재 스팬(86–151) 해시 = `faf21286…` = LEDGER 최신 rebaseline 행과 일치 — 워크시트 드리프트 표의 수치는 실측과 일치한다.
- census 대사: 발주서 314 ↔ spec 335 = +24(s007 6′ 신설 — 센서스 이후 드리프트분, LEDGER rebaseline 7행으로 상호 확인) −3(s010 line 176 재진술 사본 미승격 — §15 규약 그대로). s007 step별 합산(5+5+4+10+18+81+6)이 발주서 비고와 정확 재현됨을 확인.
- 재진술: same-doc 1건(s010 b7 [176,176] → `command-dddjango/s007/b46`)의 b46 지시가 실제 [137,137] «실행·종료 계약» 블록임을 블록 서수 재계산으로 확인 — 정확. 교차 문서 4건(발주서 재진술 열 전건)은 worksheet 유예 절에 전량 기재 — 누락 0, 유예 대상의 spec 혼입 0. 파일럿 판형(restates 보유·norms 0)과 동형.
- registry 27행(b18~b44)의 enforcedBy 27종 전건을 각 docstring과 대조 — 소유 불일치 0(단 #14 basis 인용 문제는 아래 F1). `#67` raise 금지의 check-usecase-dto-placement 소유는 구현부(`out.add("#67", …)`)로 실증. DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED 발행자 #2·#5·#15 3종 전건 구현부 실증. `error-bc ⊆ scope-bc` 검증은 #2·#5·#15 구현부에 실재. `--anchor` 수용 5종(#2·#5·#6·#15·#16) 구현부 실증.

## 발견 (심각도 내림차순)

### F1 [medium · 배선] s007 b31 (registry #14) — basis 인용 조작(허위 인용)

- **주장**: basis가 docstring 인용으로 제시한 «… 새 recognizer recipe 를 만들지 않는다»는 `check-synthetic-infra-exc.py` docstring(및 파일 전체)에 존재하지 않는다(`grep recognizer` 0건). 그 문구의 실물은 `check-transient-overmapping.py`(registry #13) docstring의 «새 handler/recognizer를 만들 근거가 되지 않는다»이고, 인용된 앞부분(⑴ 합성·⑵ #129)만 #14 docstring에 실재한다. 원문 line 121의 해당 절은 문서 자신의 registry 표 문면(①·④)이지 ② docstring 근거가 아니다.
- **수정안**: enforcedBy 타깃(`check-synthetic-infra-exc.py`)은 유지하되 basis를 실재 문면으로 재작성 — ②는 «⑴ 인프라 예외 합성(from 없는 raw 생성) ⑵ #129 전수 명시 매핑»까지만 인용하고, «새 recognizer recipe» 절은 ①문면(registry 표 행)+④로 귀속을 옮긴다.

### F2 [medium · 배선] s005 b7 «관찰 입력은 스택 정체뿐 — #105~#112» · s007 b15 «N/A 는 배선 표준 면제 아님» — basis ② 허위 출처

- **주장**: 두 norm의 basis가 «②check-composition-root.py docstring «api_router 결선(#105~#112)» 명시»라고 적었으나, 그 문구는 docstring에 없다 — `#105`는 docstring에 0회 등장하고, 해당 표현의 실물은 원문 dddjango.md line 123(registry #16 표 행 = ①문면·④)이다. 검사기 «구현부»가 #105·#107·#108·#109·#112를 실제 방출하므로(1948행 등) 배선 타깃 자체는 옳으나, 저작 계약(§16 «무근거 배선 금지 — 근거를 검수표에 기록»)이 요구하는 근거 기록이 허위 출처다.
- **수정안**: 두 norm의 basis를 «①registry #16 표 문면 «api_router 결선(#105~#112)» + ④registry #16 + ②docstring 실재 문구(«명시적 dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf 의 직접 import provenance…») + 구현부 #105~#112 방출 실측»으로 재작성.

### F3 [medium · 배선] s007 b12 «positional TARGET 도 루트(.)» — 기제 오설명 + 소유 검사기 임의 선정

- **주장**: enforcedBy를 `check-layer-skeleton.py`·`check-app-container.py` 2종에 걸고 basis에서 «루트 TARGET 이 아니면 채택 신호가 꺼져 사용 오류 exit 1»이라 했으나, 두 docstring의 채택신호-꺼짐 경로는 **exit 0(표준 미채택 clean)**이지 exit 1이 아니다(app-container: «G1 … 없으면 exit 0» / layer-skeleton: «0=clean(또는 표준 미채택)»). 원문이 말하는 «BC 폴더·application/ 컨테이너 TARGET → 사용 오류 exit 1 거절»의 실소유는 공유 모듈 `checker_target.py`다 — 그 docstring이 «27종 전부가 이 모듈을 거치므로 여기 한 곳이 직접 실행 채널까지 봉인한다»·«조용 통과 대신 소리내어 거절한다»라고 명시한다. 27종 공통 기제를 2종에만 귀속한 것은 임의 선정이고, 근거의 기제 서술은 두 인용 docstring과 모순된다.
- **수정안**: ⓐ (권장) 이 규범은 렌더 주체의 절차 규범으로 보아 `command-dddjango` 위임 기본값으로 되돌리고 basis에 «거절 집행 실물은 공유 checker_target.py(27종 전부 경유) — check-*.py 로스터 밖이라 enforcedBy 불가»를 기록하거나, ⓑ enforcedBy를 «27종 전수(공유 TARGET 계약)»로 확장 명기한다. 어느 쪽이든 «채택 신호 꺼짐 = exit 1» 서술은 삭제.

### F4 [medium · 경계kind] 제출 조건(`ontology_migrate.py` exit 0) 미충족 — 센서스 동결 좌표 충돌 (병합 전 재동결 필수)

- **주장**: 리뷰 시점 재실행으로 `[migrate] 검증 실패: s007: 좌표 불일치 — 센서스 86-140` exit 1을 재현했다. 원인 분석(센서스 동결 s007 86–140/`c1f0d29a` ↔ 현재 86–151/`faf21286`, LEDGER rebaseline 7행 존재·`sections.tsv` 미갱신)은 전건 실측으로 사실이며 spec 측 수리로 도달 불가라는 판정도 타당하다. 그러나 계약 문면상 제출 조건(exit 0)은 미충족 상태다 — 이 spec은 **`sections.tsv` 재동결(또는 `load_census_row()`의 LEDGER 최신 rebaseline 수용) 전에는 병합 투입 불가**라는 사실이 리뷰 판정으로 남아야 한다.
- **수정안**: 병합 preflight에서 `ontology_census.py`로 이 문서 좌표·해시를 재동결한 뒤 spec 무수정 재검증(exit 0 확인)을 선행 조건으로 못박는다(워크시트 해소 경로 ①). 재동결 없이 pass 처리 금지.

### F5 [low · 배선] s007 b46 «exit 의미론» — basis의 «전 로스터 동일 문면» 과장

- **주장**: 대표 3종으로 인용한 `check-error-centralization.py`·`check-api-error-controller-contract.py`의 docstring은 한국어 «종료코드: …» 문면이 아니라 영문 «Exit codes: 0=clean/N/A, 2=contract blocker, 1=usage or analysis error»다(#3도 영문). 종료코드 «의미론»은 27종 공통이 맞으나 «동일 문면» 주장과 대표 2종의 인용은 부정확하다.
- **수정안**: basis를 «공통 의미론(문면은 한/영 2형)»으로 고치고 대표는 한국어 문면 보유 검사기(#4·#6·#12 등)로 교체.

### F6 [low · 경계kind] s003 b9→b10 — 코드 펜스 후행 빈 줄(line 50)의 차행 블록 선두 귀속

- **주장**: §13 문면상 구분자 선두 귀속의 유일 예외는 «절 선두(선행 블록 없음)»인데, [40,49] 코드 펜스 뒤 빈 줄 50을 [50,52] 선두로 넘긴 것은 그 문면과 긴장한다. kind=code «펜스 정확 스팬» 규정과 파일럿 판형(architecture-ddd s017-3.2 b4/b5 동형) 선례로 정당화되고 byte 등가는 성립하므로 실해는 없다.
- **수정안**: §13에 code 블록 후행 구분자 처분(차행 선두 귀속)을 명문화하는 개정 제안을 소급 패스에 올려 문면-실무 간극을 닫는다. spec 수정 불요.

### F7 [low · 경계kind] worksheet §0 — 드리프트 커밋 열거 부정확(4건 표기, 실측 6건)

- **주장**: 워크시트는 «4커밋(3c03d81·bdf126c·e18433b·4ba4688)»이라 적었으나 `git log -- dddjango/commands/dddjango.md` 실측으로 센서스 동결 이후 `77691d8`(V2/V3 DI 이관 문면 동기 — LEDGER 938행 대응)과 `bbb8604`(T2-4 반증 레인 — 2줄 수정)도 원문을 수정했다(총 6커밋 — LEDGER rebaseline 7행과 정합). 드리프트 실체·해시 대조는 정확하므로 기록 정밀도 문제에 그친다.
- **수정안**: 워크시트 §0의 커밋 열거를 6건으로 정정(또는 «LEDGER rebaseline 7행이 정본» 한 줄로 갈음).

### F8 [low · 규범식별] s005 b8 «brownfield·legacy 는 면제가 아니라 아직 안 갚은 빚» — class=Prohibition 근거 미기록

- **주장**: 문면은 금지 명령형이 아니라 부정 선언(정의·재분류)이다. «면제로 취급 금지»로 읽으면 Prohibition, «빚으로 취급 의무»로 읽으면 Obligation — 양쪽 다 성립하는데 worksheet 경계 판단 메모 ⑺에 이 건의 판정 근거가 없다.
- **수정안**: class 유지 시 판정 근거 한 줄을 worksheet ⑺에 추가(«면제 취급을 금한다» 독법 채택 명기). 확신 없어 low.

### F9 [low · 배선] s006 b8 «slot 5 값 집합·slot 6 common shape 필수»(및 s007 b13 dedupe·b14 빈 골격 제외) — 문서 기재 의무를 코드 검사기에 enforcedBy

- **주장**: 12-slot은 design-spec «문서»의 기재 항목이고 `check-error-centralization.py`는 design-spec을 읽지 않는다 — 검사기가 무는 것은 코드 실물(canonical 모듈 shape·inventory 대응)이지 «slot 5가 reuse|create|approved-change여야 한다»는 문서 완전성이 아니다. 같은 블록의 이웃 slot 규범들은 `agent-design-review-api`로 위임된 것과 비대칭. 코드 대응물이 실재하므로(«슬롯 위반은 결국 코드에서 exit» 독법) 오배선 확정은 아니다 — low.
- **수정안**: 해당 norm들의 basis에 «검사 대상은 슬롯의 코드 대응물(문서 자체는 design-review-api/코디 소유)» 한 줄을 병기하거나, 문서-완전성 축을 `agent-design-review-api` 병기로 이원화.

## 처분 (수리자 판정 — 2026-08-22)

원문 `dddjango/commands/dddjango.md` 대조 + `dddjango/scripts/check-*.py` 27종 docstring·구현부 실측으로 9건을 하나씩 판정했다. **fixed 9 · rejected 0** — 다만 F4 는 «지적은 정당하나 spec 측 수리로 도달 불가» 라 *기록으로만* 처분했고, 그 결과 제출 게이트(`ontology_migrate.py` exit 0)는 여전히 미충족이다(아래 §제출 게이트 상태).

| # | 심각도·렌즈 | 처분 | 근거 한 줄 |
|---|---|---|---|
| F1 | medium·배선 | **fixed** | `grep -n recognizer check-synthetic-infra-exc.py` **0건**으로 허위 인용 확정 — basis ② 를 실재 문면(«⑴ 현행 관할 — 인프라 예외 *합성*(from 없는 raw 생성) · ⑵ 트리 개정 명세 몫 — #129 전수 명시 매핑»)까지로 줄이고, «새 recognizer recipe» 절은 ①문서 registry 표 문면 + ④registry #14 귀속으로 옮겨 ② 미성립을 명기했다(enforcedBy 타깃은 유지 — 지적대로 소유 자체는 옳다). |
| F2 | medium·배선 | **fixed** | `check-composition-root.py` docstring 에 `#105` **0회**(실물은 소스 line 1752 주석·1948 방출부) — «api_router 결선(#105~#112)» 의 출처는 원문 line 123 registry #16 표 행이다. s005 b7·s007 b15 두 basis 를 ①표 문면 + ④#16 + ②docstring 실재 문구(«명시적 dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf의 직접 import provenance…») + 구현부 방출 실측(#105·#107·#108·#109·#111·#112)으로 재작성. |
| F3 | medium·배선 | **fixed**(수정안 ⓑ 채택) | 두 docstring 의 채택신호-꺼짐 경로가 **exit 0** 임을 확인해 «채택 신호 꺼져 exit 1» 서술을 삭제했다. 거절 실물은 `checker_target.bc_shaped_target_reason()` 이고 **27종 전부가 이를 호출해 exit 1 로 끝낸다**(22종 `return 1` · 5종 `UsageError`)는 것을 전수 실측(`grep -L` 결과 공집합)으로 확인 — 문면의 주어가 «검사기» 이므로 위임 회귀(ⓐ) 대신 **enforcedBy 를 27종 전수로 확장**하고 basis 에 «집행 실물은 로스터 밖 공유 모듈, exit 를 내는 주체는 27종 각각» 을 기록했다. |
| F4 | medium·경계kind | **fixed(기록 처분 — spec 수리 불가)** | 재실행으로 `s007: 좌표 불일치 — 센서스 86-140` exit 1 재현. 원인 실측 정합(센서스 `86-140/c1f0d29a` ↔ 현재 `86-151/faf21286` · LEDGER rebaseline 7행 · `sections.tsv` 미갱신)이고 `load_census_row()` 가 `sections.tsv` 만 읽으므로 spec 측 도달 경로가 없다. **`sections.tsv` 재동결은 저작 계약(§금지 «쓰는 파일은 자기 spec + worksheet 2개뿐»)이 금한 병합 단계 직렬 소유자 몫**이라 손대지 않았고, 대신 워크시트 §0 에 «재동결 → spec 무수정 재검증 exit 0 전에는 병합 투입 불가 · 재동결 없이 pass 처리 금지» 를 선행 조건으로 못박았다. 재동결 시뮬레이션(읽기 전용)으로 **경로 ① 수행 시 spec 무수정 exit 0** 을 기계 확인해 함께 기록했다. |
| F5 | low·배선 | **fixed** | 27종 docstring 전수 파싱으로 **한국어 «종료코드:» 24종 · 영문 «Exit codes:» 3종**(registry #2·#3·#15) 확인 — «전 로스터 동일 문면» 은 과장이 맞다. basis 를 «의미론은 27종 공통 · 문면은 한/영 2형» 으로 고치고 대표를 3종→**5종**(#4·#6·#12 한국어 + #2·#15 영문)으로 늘려 두 문면형을 모두 포괄 인용했다. |
| F6 | low·경계kind | **fixed(개정 제안 등재 — spec 무수정)** | 지적대로 §13 의 명시 예외는 «절 선두» 하나뿐이라 code 후행 빈 줄의 차행 선두 귀속은 문면과 긴장한다. 파일럿 판형 동형·byte 등가 성립으로 실해가 없으므로 spec 은 그대로 두고, 워크시트 경계 메모 ⑴ 에 «§13 에 code 블록 후행 구분자의 차행 선두 귀속을 두 번째 명시 예외로 명문화» 개정 제안을 소급 패스 안건으로 등재했다. |
| F7 | low·경계kind | **fixed** | `git log -- dddjango/commands/dddjango.md` 실측 — 센서스 동결 커밋 `ceb3c6a`(2026-08-19) 이후 원문 수정은 `77691d8`·`bdf126c`·`3c03d81`·`bbb8604`·`e18433b`·`4ba4688` **6건**(초판은 `77691d8`·`bbb8604` 누락). 워크시트 §0 을 6건으로 정정하고 «열거의 정본은 LEDGER rebaseline 7행» 을 병기했다. |
| F8 | low·규범식별 | **fixed** | 양독 성립 지적이 타당 — 경계 메모 ⑺ 에 `Prohibition` 채택 근거 3줄을 명기했다: ⑴ 술어 초점이 «면제가 **아니다**» = 잘못된 처분의 배제(재분류 자체는 houserules §4 정본 소유) ⑵ 소비 지점이 line 71 «ⓑ 미룬다» 선택지 통제 = 특정 처분 차단 ⑶ 같은 절 이웃 규범 2건도 처분 배제형 `Prohibition`. class 는 유지. |
| F9 | low·배선 | **fixed(한정 병기)** | 검사기가 design-spec 문서를 읽지 않는다는 지적은 사실 — 다만 코드 대응물이 실재해 오배선 확정은 아니라는 리뷰 자체 판단에 동의해 enforcedBy 는 유지하고, s006 b8 slot5·6 / s007 b13 dedupe / s007 b14 빈 골격 세 basis 에 «검사 대상은 슬롯의 **코드 대응물**이고 문서 기재 완전성 축은 `agent-design-review-api`·코디 소유» 한정을 병기했다. |

### 반영 후 기계 재검증

```
[replay] 절 11 · 블록 120 · Work 335 · enforcedBy 127 · delegatedTo 282
로스터 27종 미등장: [] | 로스터 밖 오타: []
[replay] ALL ASSERTIONS PASS
```
블록 연속·비중첩·절 전체 커버·헤딩+블록 == 절 스팬(byte 등가)·class 5종·무소유 0 전건 유지. **Work 총수 335 불변**(배선 대상만 갈렸다) · enforcedBy 트리플 100→127(F3 +25 · F5 +2).

### 제출 게이트 상태 (정직 보고)

```
$ PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py \
    workspace/eval/t3/specs/command-dddjango.spec.json
[migrate] 검증 실패: s007: 좌표 불일치 — 센서스 86-140
EXIT=1
```
**exit 0 미달 — 잔여 사유는 F4 한 건뿐**이고 spec 결함이 아니다. F4 판정대로 `sections.tsv` 재동결(병합 preflight) 뒤 이 spec 을 **무수정** 재투입해야 하며, 재동결 없이 pass 처리하지 않는다.

## 렌즈별 무발견 확인

- **재진술(④)**: 발견 0 — same-doc 1건 spec 등재·교차 4건 전량 유예·유예 대상 spec 혼입 0, 비-재진술 판정 2건(«step6 그대로 적용» 역참조·s003↔s011 동축)도 원문 대조로 타당.
- **규범 식별(②)**: 총계·분포 대사 전건 설명 가능(과소/과대 판정 포함), 채번 순서 = 문장 등장 순 표본·핵심 블록(b46 14 Work) 전수 대조 일치. class Override 0건 판정 타당.
