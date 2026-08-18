# 온톨로지 도입 블루프린트 v2.2 + 실행 절차서 (동결 후보 — 2026-08-18)

> 근거 사슬: P0 센서스(실측 14건) → ② 자료 조사(출처 182건) → ④ 적대 리뷰 6렌즈 54건 전건 중재 반영(`2026-08-18-ontology-adversarial/MEDIATION.md`) → 검증 패스 2종(반영 대조 54/54 착지 · 신선한 눈 9건 반영).
> 상태: 사용자 심의(⑤) 대기 → 동결. 동결의 의미는 §9로 정의된다.

## 0. 한 줄 설계

**규칙의 뼈대(ID·소유·집행·쌍둥이)를 YAML 레지스트리로 형식화하되, 정본 지위는 실적으로 증명된 뒤에만 승격한다.** 산문 본문은 지금처럼 스킬 문서가 정본이며, 온톨로지는 그 위의 좌표계·검증 층이다. 신설되는 모든 기계 장치는 이 저장소의 기존 관례 수준(빚 채널의 승인 목록+전량 보고, import-시 자기 assert, self-test 선행)을 하한으로 한다 — 성실한 소유자를 전제하는 honor-system 장치는 두지 않는다.

## 1. 확정 결정

| 결정 | 내용 | 근거 |
|---|---|---|
| **D1 형식** | **YAML 자체 형식 확정.** JSON Schema + 자체 lint로 제약 집행. RDF/Turtle 투영은 가역 옵션. 필드 어휘는 **표준의 의미론을 차용하되 값 어휘는 자체**로 명시: status 5값(COSS 개명+complete), severity(SHACL 실무 관행 — 명세의 severity는 적합성 무영향 주석이므로 «관행» 차용임을 명기), 승계 관계(RFC Obsoletes/Updates의 의미론, 표기는 supersedes/updates), deprecated·replaced_by(OBO) | R2·R3·R5·R7 + L1 출처 정정 |
| **D2 부위별 단계** | 축 등급 숫자는 **학습 지도의 의미 스펙트럼 단계**(②=통제 어휘·ID 확립, ⑤=제약·등가성 검증)다. 참조 축 ⑤ 유지 · ID 축 ② 신설(승격 사다리) · 미러 축 ⑤ 신설(최우선) · 분류 축 보류(소비자 확인 전 금지) · **재진술 축(SKILL 요약↔본문↔체크리스트 3중 사본) 보류** — 사유: 판내 등가성 검사는 미러 축과 별개 표면이며 처방 미성숙. 재개 조건: S3 등재 규칙에 한해 quote 대조를 요약 사본까지 확장 검토(S4 평가 항목) | P0 §7 + L3 |
| **D3 범위** | 소급 전면 등재 금지. ID 발행은 신규·개정 규칙부터. 기존 번호 5종은 alias 흡수(재번호 금지) | R1·R7 |
| **D4 쌍둥이** | 과도기: 대조(fuzzy 모델) — **fuzzy 잔존은 커밋 비차단·릴리즈 게이트에서 잔량 0 요구**(배치 해소). 정본 폴백은 과도기 미채택(렌더 장치 부재 — 수렴기 조건부 렌더 도입 시 재검토를 명시 기록). 수렴기: 잔차 0 안정 쌍부터 단일 정본+조건부 렌더 | R4 + L6·L1 |

## 2. ID 체계

- **형식**: `DJR-NNNN`(접두 1종+불투명 4자리 순번). 의미는 전부 레코드 필드로. CURIE 호환 — 단 접두→URI 바인딩 등록(`djr:` → 네임스페이스 선언 1행)이 전제임을 명기.
- **발행 대장**: `registry/ISSUED`(append-only). **신규 발행은 대장 경유만 허용**. registry_lint가 «대장 등재 ID의 레코드 부재»·«대장 밖 ID의 레코드 등장»을 exit 2 — checker_registry의 import-시 로스터↔실재 assert와 동형. 레코드 파일 삭제로 번호가 재발행되는 경로를 기계 차단.
- **개정 3분류 경계**(OBO P19와 OFT revision의 접합부 명문화):
  1. **지시 대상 변경**(다른 규칙이 됨) → 새 ID + 구 레코드 `deprecated`+`replaced_by`(자동 추종) 또는 `consider`(사람 심의 필요 — 1:N·부분 승계).
  2. **지시 대상 유지 + 규범 강도·범위 개정** → `revision` +1.
  3. **명확화·오탈자** → revision 불변(무의미 변경 사유 등기).
  S3 등재 심사 체크리스트에 이 3분류를 포함한다.
- **revision 전파의 기계화**: 인용 측은 `Rule-ID: DJR-NNNN@rN`으로 **revision을 핀**하고, 레코드에 `doc_hash`(대상 절 본문의 정규화 해시 — 미러 lint 정규화 층①과 같은 자산)를 둔다. lint 규칙: ① 레코드 revision > 인용 핀 → 해당 인용 Outdated 판정(갱신으로 해제) ② **quote·doc_hash 변경 ∧ revision 미증가 → exit 2**(3분류-③ 주장 시 사유 등기로만 통과) — «updates 미기록» 고장 모드의 기계 차단.
- **alias(legacy 흡수)**: 문법은 **네임스페이스 한정형만 허용** — `reg#7`(registry 1~27) · `rule#538`(무접두 #N — 트리 개정 명세 소유) · `ddd:결정#3`(스킬별 의사결정 대장) · `slot#6`(Error response contract 12-slot) · `architecture-ddd§3.2«판정 소유→구조 이주»`(§+볼드 라벨 2단 앵커 — anchor_integrity_check ⑤형 문법 재사용). 이로써 P0의 번호 공간 5종(§·무접두 #·registry #·12-slot·의사결정 #)이 전부 흡수 경로를 갖는다. 비한정 «#N»·맨 «§N.M» 등재 금지. 유형 3종: 유일 별칭 / 문맥 한정 별칭(문서+절 스코프) / **흡수 불가 명시**(비유일 준-ID — 날짜 스탬프 등 — 사유 첨부 제외 대장). lint 요구는 «**유일 해소(함수성) + 미흡수 잔여 0**»(«전단사» 표현 폐기 — alias:ID는 다대일).
- **무접두 #N(538규칙 명세 — 최대 번호 공간)**: 파생원은 `tree-revision-spec`(모노레포 층)임을 명기. 흡수는 `rule#N` alias로. **배포본에서는 비해소**(본문 미동봉 — 2026-08-15 명문 유지)를 선언하고, 배포본 소비자는 번호·발췌·판정 물음만 받는 현행 구조를 유지한다.

## 3. 레지스트리 스키마

```yaml
# registry/rules/DJR-0417.yaml  (예시 — 실측값. quote는 원문 verbatim)
id: DJR-0417
type: rule                # rule | decision (아래 «레코드 유형» 참조)
title: "판정·불변식의 도메인 소유 (빈혈 차단)"   # 표시 전용 — anchor 헤딩과의 괴리는 advisory 리포트
revision: 1
status: active            # draft | active | deprecated | retired | complete
severity: gate-blocking   # gate-blocking | advisory | info
owner: architecture-ddd
doc:
  kind: prose             # prose | table-row | checklist-item | code-comment
  anchor: "architecture-ddd/references/final.md §3.2 «판정·불변식은 도메인이 소유하고 프로덕션 경로에서 실행된다»"
  quote: "판정·불변식은 도메인이 소유하고 프로덕션 경로에서 실행된다(빈혈 차단)."
  doc_hash: "…"           # 대상 절 본문 정규화 해시 — revision 미증분 검출용 (§2)
deprecated: null          # {since, reason} — status: deprecated일 때 필수
enforcement:
  - type: agent           # checker | agent | human
    ref: "design-review-ddd (판정-소유 대조 표 — 존재 구문 검사로 결속)"
    attested_revision: 1  # 인용 핀 — 레코드 revision과 대조해 Outdated 판정 (§2)
coverage: delegated       # 값 공간·유도 규칙은 §4.2 — enforced/delegated는 재계산 대조, todo/informative는 명시 선택
twins:
  codex: "codex-dddjango/skills/dddjango-architecture-ddd/references/final.md §3.2"
  norm_hash: "…"
  fuzzy: false
aliases: ["architecture-ddd§3.2«판정 소유→구조 이주»"]   # 문맥 한정형
related: []               # {type: supersedes | updates | replaced_by | consider | renamed | similar, id}
                          # renamed=ID 개명 이력(Sigma 차용 — ID 불변 원칙 하에서 title 개명 기록)
                          # similar=참고 연결(lint 무검사). 대칭 검사: supersedes·replaced_by는
                          # 역방향 대칭 필수, updates·consider는 단방향 허용
ext: {}
```

- **레코드 유형 2종**: `type: rule`(기본 — 위 스키마)과 `type: decision`(ADR형 — 본 블루프린트·의사결정 등재용). decision형은 doc.anchor=문서 경로, quote·twins·스킬-owner **면제**. **필수 필드**: rule형 = id·type·title·revision·status·severity·owner·doc{kind·anchor·quote}·coverage / decision형 = id·type·title·revision·status·doc{anchor}. status: deprecated면 deprecated 블록 필수. 나머지는 선택.

- **비산문 운반체**(P0 횡단4): `doc.kind`가 prose가 아니면 anchor는 «§ + 행/항 좌표», quote는 «셀 값·항목 텍스트·코드 주석» 지문 — 표 행·체크리스트 항(ninja §6.2 55+항)·코드 블록 주석 규범을 등재 가능하게 한다.
- **산문은 넣지 않는다**: quote는 대조용 verbatim 인용(개행·공백은 정규화 층① 규칙으로 매칭)이지 본문 이관이 아니다.
- lint 집행: 필수 필드 · ID 유일성(+ISSUED 정합) · 참조 무결성 · 쌍둥이 대칭 · quote↔원문 대조 · coverage 재계산 대조 · 승계 역방향 대칭 · revision 규칙(§2).

## 4. 트레이서빌리티

1. **역방향 — 현행 체계 존중 위에 승격**: rule-owner-map은 이미 `spec_lint --emit-owner-map`이 트리 개정 명세에서 생성·1:1 검증(⑧)하는 파생물이다 — **이 파생 경로는 유지**하며 강등·대체하지 않는다. 승격의 실체는 검사기 docstring의 `Rule-ID:` 표기 통일이다. 실물 분포(L2 실측): 통일 정형구 8~10종·이형 3계열·무기록 2종 — 즉 **27종 전수 재저작 작업**이며(무기록 2종 docstring 보수 선행), 표기 값 공간은 `rule#N`(legacy)과 `DJR-NNNN@rN`을 모두 허용한다. 목표 상태는 **docstring ↔ rule-owner-map ↔ 명세의 삼각 대조**(spec_lint ⑧의 확장). human 판정 규칙(#15·#16·#23~#27 등)의 소유 출처는 명세 등급임을 명시 — docstring에 존재하지 않는 것이 정상이다.
2. **순방향 — 커버리지 원장(반자동)**: «파생 뷰»가 아니라 **신설 등기 원장**임을 자인한다. **4값 정의**: `enforced`(결정적 검사기가 집행) · `delegated`(에이전트·사람 위임 — 사유 필수) · `todo`(집행 예정 — 추적 필수) · `informative`(규범 구속 없음·집행 불요). **유도 규칙**(§3 coverage와의 관계 확정): enforcement에 checker 존재→enforced, agent|human만→delegated — 이 두 값은 registry_lint가 재계산·대조한다. enforcement가 빈 레코드·절은 todo|informative 중 **명시 선택 필수**(빈 채 enforced/delegated 기입은 exit 2) — 이 절반은 소유자 정책 판단이라 기계 파생이 불가하다는 뜻이다. 완화 장치: ① 절 키 규약 — «경로 + 헤딩 경로 + 서수», 무앵커 절은 헤딩 서수, 전문은 `(전문)` 고정 키, **행번호 금지** ② 절 단일값 = **worst-of** + 예외 문장 명시 등기(혼합 절은 복수 항목 허용 — ninja §6.2·tdd §5.5의 해상도 문제 대응) ③ **단계화**: 1차 등기는 {기계 파생 가능분(docstring 조인 성립) + 명문 위임(blind spot (a)~(g)·human 판정 둘·빈혈 조항) + 밀집 클러스터(E10 절차·tdd §5.5·ninja §6.2·12-slot)}만 확정하고, 잔여 절은 `informative-잠정` 자동 표기 후 개정이 닿을 때 확정(D3 원칙의 등기 적용) ④ 심의 배치 상한: 회당 ≤50절 ⑤ 원장 재생성 시 직전 스냅샷 대비 **신규 절 = 미등기 exit 2**(자동 todo 금지 — 4값 명시 선택으로만 green) ⑥ 스냅샷 하향 수정에는 사유 블록 의무(사유 없는 하향 diff = exit 2 — registry_gate 빚 채널 관례 이식).
3. **래칫의 집행 지점**(CI 부재 실측 대응): `make verify` 타깃 신설(미러 lint·커버리지 대조·registry_lint 묶음) + Makefile release [2/7] 검증 세트 편입. 상시 트리거는 수동 `make verify`+릴리즈 게이트의 2점 — 커밋 훅은 도입하지 않으며 그 사이 무검사 창은 **의도적 수용**으로 기록한다(1인 저장소 마찰 최소화).
4. **검사기 자기 검증 — 기존 자산이 본체**: `fixture_matrix.py`(90케이스)+`workspace/eval/fixtures` 34가족(good/bad 짝)이 제4축의 본체다. 신규 의무는 «새 검사기·검사기 개정 시 good/bad 짝을 이 레인에 추가»로 한정하고, `ruleid:/ok:` 인라인 표기는 **신설하지 않는다**(이중 픽스처 체계 방지). 검사기→규칙 단위 해상도 상향은 S3 이후 선택 과제로 보류.

## 5. 쌍둥이 미러 (S1 — 레지스트리 독립)

- **대상**: 의미 미러 문서쌍 19 + **스크립트 33쌍 byte-diff 편승**(검사 1행 비용). 실행 시점은 §4.3의 2점(make verify·릴리즈 게이트) — 릴리즈-사이 창은 «상시»가 아니라 **verify 실행 시점으로 축소**되는 것이며, 그 사이 잔여 창은 §4.3의 의도적 수용과 같다.
- **판별 자산 3종**(전부 독립 버전 자산·전량 보고):
  1. **플랫폼 한정 표기 규약 제정** — 문서 내 «platform-only: 사유» 마커. 기존 전용 절 소급 마킹 + coder «왕복 다이어트» 1건 판정(의도 최적화면 마커 부착, 아니면 3건째 표류로 발주)을 S1 작업에 포함.
  2. **승인 잔차 화이트리스트** — 항목별 {파일, 지문, 사유, 날짜} 필수. 매 실행 전량 보고(registry_gate 빚 채널 동형), 항목 수 임계 초과 시 심의, S4에서 전수 재심.
  3. **정규화 파이프라인 3층**(층 번호는 이 정의가 정본 — §2 doc_hash·§3 quote 매칭이 층①을 공유): **층① 표기 정준화**(개행·공백·구두점·유니코드 정규화 — 기성 규칙) → **층② 자작 규칙**(개명 사전·플랫폼 표기 치환·마커 절 제외 — lint 코드와 동일 저장소에서 버전 관리 + 골든 쌍 회귀 + 개정 시 마이그레이션 절차) → **층③ 잔차 분류**(아래 등급).
- **잔차 등급 값 공간**: `일치`(잔차 0) · `정당`(화이트리스트 등재 또는 platform-only 마커) · `신규-표현`(표기 차이로 추정 — 비차단 리포트) · `신규-규범`(규범 충돌 의심 — 비차단이되 최우선 리포트). **N∖L 표기의 정의**: N=이번 실행의 잔차 집합, L=화이트리스트 승인 집합 — «신규 잔차»란 N∖L(registry_gate의 앵커 차분 표기 차용).
- **신호 체계 확정**(문언 충돌 해소): verify 차단 = **이진 신호만**(미러 파일 부재·스크립트 byte 불일치·**신규 잔차 N∖L 존재**). 잔차 등급·fuzzy 는 비차단 리포트 적재. **릴리즈 게이트 = fuzzy·신규 잔차 잔량 0 요구**(배치 해소 — 편집 동기 게이트 금지로 개정 속도 보호). fuzzy 해제는 같은 커밋의 codex 쌍 갱신 또는 «정당 차이» 사유 기록 동반 시에만 green.
- **골든 픽스처 특정**: A3 실측의 잔차 0 4쌍(acceptance-tester·design-review-api/db/ddd) = green 고정, 표류 실증 2건 = red 고정(처분 전 스냅샷을 회귀 재료로 동결).
- LLM은 잔차 해설·우선순위 보조에 한정(비결정 판정을 게이트에 넣지 않는다).
- 표류 실증 2건(fat-model 충돌·#A~#B 누락)의 수정 자체는 본 설계 밖 — 별도 수정 건으로 사용자 발주.

## 6. 그라운딩

- 현행 3중 정적 선별 + ⓓ 채널 유지·명문화(업계 부재 차별점). 전량 상시 주입 금지는 lint로 보증.
- **경로 glob 라우팅 축 추가** — 값 공간은 «DJR ∪ rule#N(rule-owner-map 경유)»로 명시(D3 하 초기 레지스트리의 ID 공급 부족 대응). 경로→계층은 standard_tree.py가 이미 기계화 — 신설분은 계층→규칙 연결.
- **2단 피드백 루프**: ① 위반 리포트에 규칙 ID 앵커(DJR 또는 rule#) → 재생성 ② 반복 위반 규칙 → 개정 제안 큐(1인 심의).

## 7. 거버넌스

- 편집자 1인(사용자) 명문화 — 상태 전이 권한 독점. 합의 의식 없음(그 자리는 lint).
- **«등재된 규칙의 상태·의미 변경은 lint를 통과한 레코드 변경으로만»** — 한정어 명시: 미등재 산문 개정은 기존 corpus lint 체계만 적용(이중 장부 세금 방지).
- 동결 이원화: 의사결정(ADR형) 동결+supersede 양방향 / 산문 스킬 문서 Active형 지속 개정.
- **draft 레코드는 어떤 소비자도 규범으로 삼지 않는다**(S3 진입 시점부터 규정).
- 자기 등록: **S3 개시 시** 이 문서를 소급 등재(첫 레코드) — 동결 시점(S1 이전)에는 ID 체계가 없으므로.
- 배포: 과도기에는 현행 corpus_mirror_sync 불변식이 유효. «배포본=무버전 정본의 날짜 스냅샷 파생물»은 **수렴기(조건부 렌더 전환 후) 모델**임을 한정. 레지스트리의 배포 동봉 여부(+미동봉 시 발췌 유통 방식)는 S3 완료 기준에서 결정하고, 스냅샷 파생 절차는 S5 산출물로 배정.

## 8. 실행 절차 (승격 사다리)

> Stage 사이 전부 사용자 게이트. 각 Stage 산출물은 독립 가치(중도 중단 시 처분 절차 §8-일몰 참조).

| Stage | 내용 | 산출물 | 완료 기준 | 기존 도구 처분 |
|---|---|---|---|---|
| **S1 미러 lint** | §5 전체 — 19쌍+스크립트 33쌍, 표기 규약 제정·화이트리스트·정규화 3층 | corpus_check 1차 + 표류 리포트 + 판별 자산 3종 | 골든 픽스처 green/red 재현(잔차 0 4쌍·표류 2건) · 19쌍 전수 등급 판정 · coder 1건 판정 완료 | corpus_mirror_sync·tree_mirror_check·anchor_integrity_check·corpus_lint **존치**(corpus_check는 신설 쌍 대조 모드만 — 통합은 S4 이후 검토) |
| **S2 파생·원장** | §4.1 docstring 27종 Rule-ID: 재저작(무기록 2종 보수 선행) + §4.2 커버리지 원장 1차(단계화) + make verify 신설 | coverage_check 1차 + 커버리지 스냅샷 + verify 타깃 | 1차 등기분(기계 파생+명문 위임+밀집 클러스터) 등기 완료 · 삼각 대조(docstring↔map↔명세) green · 배치 상한 준수 기록 | reverse_coverage·spec_lint③④⑧·fixture_matrix **존치·확장**(coverage_check는 이들의 조합 리포트) |
| **S3 레지스트리 개시** | §2·§3 — ISSUED 대장 가동, ID 발행(신규·개정분부터), alias 역인덱스 lint | registry/ + registry_lint | 첫 등재분 삼각 대조 green · 등재 심사 체크리스트(3분류) 운용 · **배포 동봉 여부 결정** · 본 문서 DJR 소급 등재 | anchor_integrity_check ⑤형 문법을 alias 해소에 재사용 |
| **S4 승격 게이트** | 실적 평가 — **기산점: S3 첫 등재일, 시한: T=3개월(등재 건수 불문 진입)** | 실적 리포트 + 승격/축소 결정 + 화이트리스트 전수 재심 + **재진술 축 재개 검토(D2)** | 사용자 결정 | — |
| **S5 그라운딩·루프** (승격 시에만) | §6 + 잔차 0 쌍 조건부 렌더 전환 개시 + 스냅샷 파생 절차 | 파이프라인 개정 + 렌더 도구 | 첫 실런 관측 1회 | corpus_mirror_sync는 렌더 전환 쌍부터 렌더 검증으로 대체 |

- **S4 지표**(발화 가능하도록 재설계 — 층위 혼동 제거):
  1. **레지스트리 고유 가치 건수** — 미러 lint 단독으로는 못 잡았을 문제를 ID 조인·revision 전파·alias 해소가 잡은 건수(lint 리포트에서 자동 계수).
  2. **등재 행위 밖 ID 참조 건수** — 위반 리포트 앵커·문서 크로스 인용·세션 중 질의 등 등재자가 아닌 소비자의 참조(자동 계수).
  3. **유지 부하 프록시** — fuzzy 해제·등재/개정 레코드·화이트리스트 변경 건수(전부 git 계수) × 건당 표준 시간 추정식. 사람 시간 자가 회고는 쓰지 않는다.
- **일몰(축소) 처분 절차**: 전 레코드 `status: retired` 일괄 전이(+사유) → docstring·문서의 DJR 참조는 제거 또는 tombstone 표시 → quote·doc_hash·삼각 대조 lint 스코프 종료 선언 → alias 역인덱스는 죽은 ID 참조 방지 검사로만 존치 → S1(미러 lint)·S2(커버리지 원장) 산출물은 레지스트리와 무관하게 유지. S3 중단 시에도 동일 절차 적용.

## 9. 동결·해동 절차

1. 사용자 심의(⑤) 통과 시 동결. 동결 = «아래 개정 절차 없이는 수정 금지».
2. 개정: 사유·diff·영향 Stage를 기록한 개정 블록을 말미에 추가 + 사용자 승인. Stage 진행 중 발견 사실이 설계와 충돌하면 작업을 멈추고 개정 먼저.
3. Stage 세부 실행 계획은 진입 시 별도 문서(동결 대상 아님) — 본 문서의 완료 기준을 변경할 수 없다.
4. 적대 리뷰 반영은 동결 전 자유 개정 — §10에 기록.

## 10. 개정 기록

- v2 (2026-08-18): 원안 대비 승격 사다리·D1~D4 확정·ID/스키마/거버넌스 구체화. 근거: P0 + R1~R7.
- **v2.1 (2026-08-18)**: 적대 리뷰 6렌즈 54건(blocker 3·major 31·minor 20) 전건 중재 반영 — 중재 기록 `2026-08-18-ontology-adversarial/MEDIATION.md`. 주요 변경: ① rule-owner-map 파생 경로 존중(삼각 대조로 재정의) ② S4 일몰 지표 전면 교체(발화 가능화) ③ S2 완료 기준 단계화(실행 가능화) ④ S1 신호 체계 확정(화이트리스트 자산화·릴리즈 배치 해소) ⑤ revision 3분류 경계+@rN 핀+doc_hash(honor-system 제거) ⑥ ISSUED 발행 대장 ⑦ alias 네임스페이스 문법 ⑧ 무접두 #N 흡수 경로 ⑨ 비산문 운반체 스키마 ⑩ 기존 도구 처분표·fixture_matrix 본체 인정 ⑪ 일몰·중단 처분 절차 ⑫ 예시 실측값 교체.
- **v2.2 (2026-08-18)**: 검증 패스(V1 반영 대조: 54건 전건 착지 확인 / V2 신선한 눈: major 3·minor 6) 반영 — ① `slot#N` alias 추가(12-slot 흡수 — 5종 완결) ② 커버리지 4값 열거+유도 규칙 확정(§3↔§4.2 상충 해소) ③ 레코드 유형 rule|decision과 필수 필드 목록(자기 소급 등재 실행 가능화) ④ 차단 지점 어휘 통일(verify)·byte-diff 시점 정정 ⑤ 정규화 3층 번호 정의 ⑥ 잔차 등급 값 공간·N∖L 정의 ⑦ related enum 의미·대칭 범위 확정 ⑧ S4 산출물에 재진술 축 재개 검토 ⑨ D2 축 등급 숫자의 정의처 명시.
