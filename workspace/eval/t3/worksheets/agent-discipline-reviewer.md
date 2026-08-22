# T3 저작 검수표 — agent-discipline-reviewer

- 원문: `dddjango/agents/discipline-reviewer.md` (130행 · 센서스와 일치 — 8절 전건 스팬 해시 재검증 OK, 드리프트 0)
- spec: `workspace/eval/t3/specs/agent-discipline-reviewer.spec.json` (REF 8절 · 블록 90 · Work 317)
- 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-discipline-reviewer.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)
- **적대 리뷰 수리 패스(2026-08-22)**: `workspace/eval/t3/reviews/agent-discipline-reviewer-findings.md` 12건 판정 — **반영 12 · 기각 0**(F4는 «심의 누락» 지적을 반영해 두 쌍을 추가 심의했고, 지적이 제안한 `restates` 기입만 축자성 불성립으로 미채택 — 사유 §4-⑤′). 고친 Work 17건 — enforcedBy 철회 9 · 추가 3 · 위임 대상 재배선 2 · class 조정 2(Obligation→Override) · label 교정 1. **Work 수 317·블록 90 불변**(계수 무영향 — 배선/분류만 변경). 처분 상세는 리뷰 파일 «처분» 절.

## 0. 배선 정책 (문서 전역 — §16 4원 종합의 이 문서 적용판)

이 문서는 «절차 층»(command+agents) 소속이지만 내용은 두 층이 겹친다. 그래서 위임 기본값 표를 다음 두 갈래로 갈라 적용했고, 갈래마다 문면 근거를 §2 표에 남겼다.

- **P-A 절차·입출력 규범**(호출·모드·입력 계약·리포트 형식·반송 라우팅·승인/게이트) → `delegatedTo: command-dddjango`. 근거 = §16 위임 기본값 표 «command+agents(절차 층) → Coordinator(절차 준수 판정 주체)». s001~s004·s008 대부분과 s005~s007의 반송·승인 조항이 여기 든다.
- **P-B 감사 대상(코드·테스트 산출물) 규범** → `delegatedTo: agent-discipline-reviewer`. 근거 = 문면이 판정자를 «네가 본다»·«네 몫»·«이 줄의 판정자는 너 하나다»로 **명시**(기본값 이탈의 문면 근거) + 위임 기본값 표의 discipline-*·implementation-* 행. 담당 검사기가 있으면 `enforcedBy` 병기(기계 절반 + 의미 잔여 분업).
- **P-C 타 소유 명시** → 문면이 API reviewer·acceptance-tester·coder·design-architect를 소유자로 지목한 조항 중 **아래 판별자에 드는 것만** 그 Agent로 위임(§16 «기본값 이탈은 문면 근거»). 적용 결과: s002 b11-3, s006 b4-2, s008 b2-2·b2-7·b2-9.
  - **판별자(적대 리뷰 F3 수리 — 2026-08-22 명문화)**: 같은 «타 역할 지목» 문형이 두 종류라 갈래를 자로 고정한다.
    - ⒤ **감수자 리포트의 표시·라우팅 의무**(술어가 «…로 표시한다»·«…로 반송한다» — 주어가 감수자의 산출물 형식) → `command-dddjango`. 준수 판정 주체는 리포트를 수납·라우팅하는 Coordinator이고, 지목된 Agent는 그 표시가 제대로 됐는지 볼 자리에 없다. 해당: s003 b1-3(Phase 1 반송)·b1-4(Phase 2 소유자 표시 3종)·**s006 b4-3**(OpenAPI/runtime 기술 정확성 «소유로 표시한다» — 종전 acceptance-tester+coder에서 재배선).
    - ⑵ **판정 소유 배분·중복 판정 배제 선언**(술어가 «…가 책임진다»·«…몫이다»·«… 소유이므로 중복 판정하지 않는다» — 감수자 행위 형식이 아니라 판정 자체의 귀속) → 지목 Agent. 배제된 판정을 실제로 수행·판정하는 주체가 그 Agent이기 때문. 해당: s002 b11-3·s006 b4-2·s008 b2-7(→ agent-design-review-api), s008 b2-9(→ acceptance-tester+coder), **s008 b2-2**(«구현 정확성은 코더…, 명세 부합은 설계·인수 테스트가 책임진다» → coder+design-architect+acceptance-tester로 재배선).
    - registry Agent 8종 밖 개체(implementation-* 스킬·그레이더 FC-2)는 배선 대상에서 빼고 근거 문자열에만 남긴다.
- 무소유 0건(도구가 단언). `enforcedBy` 배선은 **check-*.py 27종 docstring 선두 전수 실독** 뒤에 했고, 규칙 번호 대응은 27종 전 파일 정규식 대조(#N 소유자 grep)로 확인했다 — §16 L-F 교훈(8종만 보고 9종 오배선) 대응.

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

| 절 | 헤딩 | 발주서 | spec | 차 | 사유·판정 |
|---|---|---|---|---|---|
| s001 | (전문) | 4 | 5 | +1 | 발주서 4 = description 3문 + 본문 1(E10-recon §4 «본문은 P0 h2 계수 승계»). 본문 문단은 실제로 규범 2문(읽기 전용 독립 감수 / 체크포인트 단발 감사)이고 첫 문장(역할 선언)만 서술이다 — **census 과소** |
| s002 | 입력 | 16 | 27 | +11 | ⑴ DYNAMIC 증거 6항이 각자 «독자 행»이라 L-G 관례(부모 «다음 묶음만 받는다»가 의무 동사 공급·항목별 독립 검사 가능)로 개별 채번 +6 ⑵ 복합문의 이질 의무 분리 +5(미수령↔혼동 금지, change inventory 확인↔G1 전 상신, 판정 형식↔무효 선언 등 — 파일럿 §6.1 «503/409 선택 ↔ raw 분류 금지» 한 문장 2 Work 판형과 동형). **census 과소** |
| s003 | 산출 | 11 | 14 | +3 | 반송처 4종 라우팅은 1 Work로 접고(한 의무 동사의 목적어 열거), DYNAMIC 토큰 문단(L41)의 5의무(토큰 3조건 한정·blocker 근거+토큰 미발행·이유만의 거부 금지·별도 승인 동일성 검증·shape 승인/독립 확인 갈음 금지)를 분리해 +3. **census 과소** |
| s004 | 감사 빈도 (적응형) | 3 | 5 | +2 | 문장 3 ↔ 명제 5. scope별 추가 점검(조건 분기)과 재량 상향 «허용»(Permission)이 독립 조항이라 분리. **census 과소** |
| s005 | 영구 테스트 입장 감사 | 18 | 22 | +4 | 불릿 6개 ↔ 22 Work. 여섯 열/일곱 값, 3요소 요구/금지 조항처럼 **판정 기준이 갈리는 절**만 분리했고 열거는 접었다. **census 과소(경미)** |
| s006 | Phase 1·2 API 오류 scope·소유권 점검 | 13 | 15 | +2 | 거의 일치. code-profile 불릿에서 reuse/create·approved-change의 evidence 요구가 **승인 주체가 다른** 두 조항이라 분리(전자=감수자 관찰·후자=Coordinator 승인). **census 근사 일치** |
| s007 | Phase 2 점검 항목 | 163 | 216 | +53 | 전액 설명 가능: ⑴ **ⓓ 개별 물음 43문 + 표 8행을 문장 해상도로 개별 채번**(census는 «13줄+8행» 단위 추정 — +30) ⑵ 나머지 +23은 긴 불릿의 이질 의무 분리(b13 상수 승격 14·b22 배선 12·b28 파일트리 15). ⓓ 물음은 **물음마다 #N 소유자와 방출 검사기가 갈려**(예 #257 domain-model / #285 transaction-boundary / #512 missable-entrance) 줄 단위로 접으면 배선이 손실된다 — 블루프린트 «문장 해상도 = Work 채번 단위가 문장»의 정면 적용. **census 과소** |
| s008 | 경계 | 9 | 13 | +4 | «A는 보되 B는 보지 않는다» 문형 4쌍을 각 2 Work(포함 선언 + 배제 선언)로 분리 — 포함/배제의 소유자가 서로 다르다(감수자 ↔ API reviewer·coder). **census 과소** |
| **합계** | | **237** | **317** | **+80** | 과대 산정 0건 판정. 접은 자리(열거의 단일 채번)는 §4에 전건 기록 |

**전역 판정**: 8절 전부 spec ≥ census이고, 초과분은 ⑴ 독자 행 열거의 L-G 개별 채번 ⑵ 소유자가 갈리는 복합문의 절 분리 ⑶ ⓓ 물음의 문장 해상도 — 세 규칙으로 남김없이 환원된다. 반대 방향(spec < census)은 0절이라 **누락 위험 지점 없음**. census 계수는 P0 h2 단위 승계값(E10-recon §4)이라 이 문서에서는 하한으로만 쓴다.

## 2. 배선 근거 표 (전 규범 317건)

표기: `E:` = enforcedBy(검사기 파일명) · `D:` = delegatedTo(에이전트 doc_key). 근거의 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N 은 §16 4원.

| # | 절/블록 | Work label | 유형 | 배선 | 4원 근거 |
|---|---|---|---|---|---|
| 1 | s001/b1 (L2–10) | 3모드 호출 트리거(Phase 1 경량·Phase 2 구현 게이트·동적 shape 증명) | Obligation | D: command-dddjango | ① 문면 역할명 «Coordinator가 … 호출한다» + ④ 위임 기본값 표(command+agents 절차 층→Coordinator) — 27종 로스터 전수 실독 결과 에이전트 디스패치를 집행하는 검사기 0 |
| 2 | s001/b1 (L2–10) | 지정 모드 산출물의 독립 규율 감사·리포트 산출 | Obligation | D: command-dddjango | ④ 위임 기본값 표(절차 층) — 감사 수행 여부 판정은 호출·수납 주체인 Coordinator |
| 3 | s001/b1 (L2–10) | 감수자의 코드 직접 수정 금지 | Prohibition | D: command-dddjango | ④ 위임 기본값 표(절차 층) — 읽기 전용 계약 위반은 절차 위반이고 코드 대상 검사기 관할 밖 |
| 4 | s001/b2 (L11–13) | 읽기 전용 독립 감수(클린코드·TDD·현행 계약 렌즈) | Obligation | D: command-dddjango | ④ 위임 기본값 표(절차 층) · 문면이 감사 렌즈 3종을 스킬 위임으로 고정 |
| 5 | s001/b2 (L11–13) | 체크포인트 단발 감사(실시간 감시 아님) | Obligation | D: command-dddjango | ④ 위임 기본값 표(절차 층) — 호출 시점 결정은 Coordinator 소유(s004와 동축) |
| 6 | s002/b1 (L15–17) | 호출 시 3모드 중 하나의 명시 | Obligation | D: command-dddjango | ① 문면 주어가 Coordinator + ④ 위임 기본값 표(절차 층) |
| 7 | s002/b2 (L18–18) | Phase 1 일반 scope 입력 수령(명세 초안·6열 최소 입장 표) | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 입력 공급 주체가 Coordinator |
| 8 | s002/b2 (L18–18) | Error response contract scope의 project-wide production tree/inventory 추가 수령·독해 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 조건부 입력 공급 계약 |
| 9 | s002/b2 (L18–18) | 추가 evidence의 표면 전량 포함(module·API instance·profile·scope-bc/error-bc membership) | Obligation | D: command-dddjango | ④ 절차 층 기본값 · s006 inventory 대조의 전제 입력 — 완결성 판정은 Coordinator handback 축 |
| 10 | s002/b2 (L18–18) | Phase 1 미수령 4종(구현 diff·테스트 조정 목록·실행 결과·슬라이스) | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 모드별 입력 경계 |
| 11 | s002/b2 (L18–18) | production tree evidence와 Phase 2 implementation diff 혼동 금지 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 모드 혼선 방지 절차 규범 |
| 12 | s002/b2 (L18–18) | 입장 결정의 완결성·근거·중복·testability·단순성 점검 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — Phase 1 산출(입장 표) 감사 이행 여부는 Coordinator가 G1에서 확인 |
| 13 | s002/b2 (L18–18) | 명세 change inventory의 승인 스코프(+G0 ⓐ 빚 항목) 내포 확인 | Obligation | D: command-dddjango | ① 문면이 G0/G1 승인 스코프를 지목 + ④ 절차 층 기본값(스코프 승인 소유=Coordinator) |
| 14 | s002/b2 (L18–18) | 스코프 밖 기존 파일 이동·재배선의 G1 전 발견 상신 | Obligation | D: command-dddjango | ① 문면 «G1 전에 발견으로 올린다» — 게이트 절차 소유 Coordinator |
| 15 | s002/b2 (L18–18) | 리포트 말미 집행성 판정 1행 기재 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 리포트 형식 계약(리뷰어 3종 동형) |
| 16 | s002/b2 (L18–18) | 집행성 판정 근거 형식(가능=확정 결정 3곳 인용·불가=막히는 항목 지목) | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 산출 형식 계약 |
| 17 | s002/b2 (L18–18) | 인용 없는 «가능» 집행성 판정 무효 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 무효 선언의 판정자는 판정을 수납하는 Coordinator |
| 18 | s002/b3 (L19–19) | Phase 2 입력 전량 수령(코드·테스트·승인 입장 표·조정 보고·diff·실행 결과·슬라이스) | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 입력 공급 계약 |
| 19 | s002/b3 (L19–19) | 코드·테스트 직접 독해로 구현 감사 수행 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 감사 수행 이행 판정은 Coordinator |
| 20 | s002/b4 (L20–20) | DYNAMIC 모드 발동 조건(잔여 exit 1 진단 전부가 DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED) | Exception | E: check-api-error-controller-contract.py + check-error-centralization.py + check-openapi-error-declaration.py · D: command-dddjango | ② marker 발행 실측 3종(controller-contract L1581·1590·1890 / error-centralization L2323 외 / openapi-error-declaration L2404) — 발동 조건이 «잔여 exit 1 전부가 marker»라 발행자 전원 배선 · §16 매핑 표는 controller 단독 기재라 표 자체가 과소(별도 상신) + ④ 모드 발동 판정은 Coordinator 절차 |
| 21 | s002/b4 (L20–20) | Coordinator의 DYNAMIC 모드 명시 의무 | Obligation | D: command-dddjango | ① 문면 주어 Coordinator + ④ 절차 층 기본값 |
| 22 | s002/b4 (L20–20) | 동일성 증명 묶음 한정 수령 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 입력 한정 계약(하위 6항이 목록) |
| 23 | s002/b5 (L21–21) | 증거 1 — 12-slot과 action별 기준 evidence(reuse=관찰 baseline·create/approved-change=분리 승인) | Obligation | D: command-dddjango | ④ 절차 층 기본값 · L-G 관례(부모 «다음 묶음만 받는다»가 의무 동사 공급·항목별 독립 검사 가능) |
| 24 | s002/b6 (L22–22) | 증거 2 — 모든 checker의 exact command·exit·diagnostic | Obligation | D: command-dddjango | ① 문면이 checker 실행 산출을 입력으로 지목 + ④ 검사기 실행 소유=Coordinator(Phase 2 step 6) |
| 25 | s002/b7 (L23–23) | 증거 3 — target dependency pin | Obligation | D: command-dddjango | ④ 절차 층 기본값 · L-G 관례(항목별 독립 검사 가능) |
| 26 | s002/b8 (L24–24) | 증거 4 — common/BC model의 Field metadata·model_config·hook inventory·wire 직렬화 introspection | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 이 증거는 error-centralization이 그 자리에서 PROOF_REQUIRED로 «분석 불능»을 자인했을 때의 대체 경로라 «증거 대상=검사기 분석 대상 동일»은 집행이 아니다(enforcedBy 미병기) · 공급 주체는 Coordinator |
| 27 | s002/b9 (L25–25) | 증거 5 — direct BC-base 생성문별 승인 key·ErrorCode member·exact dump | Obligation | D: command-dddjango | ④ 절차 층 기본값 — controller-contract가 그 생성문에서 PROOF_REQUIRED를 발행한 자리의 대체 증거 경로라 대상 사상(寫像)일 뿐 집행 아님(enforcedBy 미병기) · 공급 주체 Coordinator |
| 28 | s002/b10 (L26–27) | 증거 6 — mount의 endpoint status/body/header와 generated OpenAPI | Obligation | D: command-dddjango | ④ 절차 층 기본값 — openapi-error-declaration도 이 표면에서 PROOF_REQUIRED를 발행(L2404)해 대체 증거를 부르는 쪽이라 집행 아님(enforcedBy 미병기) · 공급 주체 Coordinator |
| 29 | s002/b11 (L28–29) | API reviewer 노트·확인 토큰 미수령(두 리뷰 독립) | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 독립성 보장은 입력 공급 주체 소유 |
| 30 | s002/b11 (L28–29) | DYNAMIC 모드 감사 범위 한정(증거 완결성·재현성·기준선 동일성·canonical 소유권·helper 우회 부재) | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 모드별 감사 범위 계약 |
| 31 | s002/b11 (L28–29) | HTTP 의미론·public code 적정성·호환성의 중복 판정 금지(API reviewer 소유) | Prohibition | D: agent-design-review-api | ① 문면이 소유자를 API reviewer로 명시 — 기본값 이탈의 문면 근거(§16 역도 성립 조항) |
| 32 | s002/b12 (L30–31) | 타 감수 노트 비열람 독립성(비작성자 근거) | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 독립 감수 배치는 Coordinator 소유 |
| 33 | s003/b1 (L33–35) | 감수 리포트만 산출 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 산출물 계약 |
| 34 | s003/b1 (L33–35) | 감수 리포트 외 코드 직접 수정 금지 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 역할 경계 위반은 절차 판정(label을 자기 문면 L34 «코드를 직접 고치지 않는다» 한정으로 교정 — «반영은 코더» 보충은 s008 L128 소유) |
| 35 | s003/b1 (L33–35) | Phase 1 지적의 design-architect 반송 | Obligation | D: command-dddjango | ① 문면이 반송처를 지목 + ④ 라우팅 실행 소유 Coordinator |
| 36 | s003/b1 (L33–35) | Phase 2 지적의 소유자 표시 3종 라우팅(외부 계약 assertion·내부 assertion/구현·명세 구조 결정) | Obligation | D: command-dddjango | ① 문면이 acceptance-tester·coder·design-architect를 소유자로 지목 + ④ 라우팅 판정 Coordinator |
| 37 | s003/b1 (L33–35) | 설계 오류의 Coordinator G1/G1' 반송 | Obligation | D: command-dddjango | ① 문면 주어가 Coordinator·게이트 절차 |
| 38 | s003/b1 (L33–35) | 발견 다수 시 심각도 순(blocker→important→nit) 번호 나열 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 리포트 형식 계약 |
| 39 | s003/b2 (L36–36) | 발견 항목 형식(문제+근거 파일:라인+심각도 3단계) | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 산출 형식 계약(리뷰어 3종 동형) |
| 40 | s003/b3 (L37–38) | 권고 항목 형식(변경 방법 제시) | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 산출 형식 계약 |
| 41 | s003/b4 (L39–40) | 무결 시 «규율 관점 이상 없음» 명시 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 무발견 보고의 명시 계약 |
| 42 | s003/b5 (L41–42) | RESOLVED 확인 토큰 발행의 3조건 한정(전 증거 동일·canonical 소유권/helper 금지 준수·타 exit 부재) | Obligation | D: command-dddjango | ① 문면의 토큰이 게이트 해소 절차 재료 + ④ marker 해소 절차는 Coordinator 소유(파일럿 판형 동축) |
| 43 | s003/b5 (L41–42) | 누락·불일치·미승인·기준선 변동 시 blocker+정확 근거 제출·토큰 미발행 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 토큰 미발행 판정은 게이트 소유 Coordinator |
| 44 | s003/b5 (L41–42) | create\|approved-change라는 이유만의 거부 금지 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 승인 경로 존중 규범 |
| 45 | s003/b5 (L41–42) | 별도 승인과의 동일성 검증 | Obligation | D: command-dddjango | ④ 승인 evidence(사용자 shape 승인 문서) 대조는 검사기 입력 밖이고, 이 조항이 서는 자리는 검사기가 PROOF_REQUIRED로 분석 불능을 자인한 DYNAMIC 모드라 집행 아님(enforcedBy 미병기) · 승인 절차 소유 Coordinator |
| 46 | s003/b5 (L41–42) | 이 산출의 shape 승인·API reviewer 독립 확인 갈음 금지 | Prohibition | D: command-dddjango | ① 문면이 API reviewer 독립 확인을 별도 요건으로 지목 + ④ 이중 확인 절차 소유 Coordinator |
| 47 | s004/b1 (L44–46) | 감사 범위·시점의 Coordinator 결정과 받은 범위 한정 감사 | Obligation | D: command-dddjango | ① 문면 주어 Coordinator + ④ 절차 층 기본값 |
| 48 | s004/b1 (L44–46) | Phase 1 lightweight의 전 scope 필수(G1 직전 입장 표 독립 감사) | Obligation | D: command-dddjango | ① 문면 «G1 직전 … 필수» — 게이트 절차 소유 Coordinator |
| 49 | s004/b1 (L44–46) | Error response contract scope의 12-slot·project-wide surface·ownership 추가 점검 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — scope별 감사 범위 계약(s006 본문과 짝) |
| 50 | s004/b1 (L44–46) | 슬라이스 경량·홀리스틱 발동 기준의 파이프라인 정본 소유(커맨드 Phase 2 step 4·5) | Obligation | D: command-dddjango | ① 문면이 커맨드 Phase 2 step 4·5를 정본으로 역참조 — 값 소유 위임의 명시 사례 |
| 51 | s004/b1 (L44–46) | 여러 슬라이스에서의 재량 상향 호출 허용 | Permission | D: command-dddjango | ④ 절차 층 기본값 — 호출 재량 주체가 Coordinator |
| 52 | s005/b1 (L48–49) | 영구 test artifact 후보 전건의 여섯 열 행 등재 확인 | Obligation | D: agent-discipline-reviewer | ① 문면 «본다»의 주어가 감수자 + 로스터 27종에 입장 표 형식 집행 검사기 0(테스트 산출물 규율은 discipline-* 기본값) |
| 53 | s005/b1 (L48–49) | decision 값의 일곱 값(add/update/reuse/retain/remove/reject/pending) 한정 확인 | Obligation | D: agent-discipline-reviewer | ① 감수자 주어 · 검사기 비커버(입장 표는 문서 산출물) |
| 54 | s005/b1 (L48–49) | 누락 열·미분류 후보·pending의 blocker 판정 | Obligation | D: agent-discipline-reviewer | ① 문면이 심각도까지 규정 — 판정 주체 감수자 |
| 55 | s005/b1 (L48–49) | 일반 retain의 무편집 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 대상이 테스트 산출물 · 검사기 비커버 |
| 56 | s005/b1 (L48–49) | 명시 승인된 의미 보존 move/split/rename/reorganization만 무-Red 계약 보존 인정 | Permission | D: agent-discipline-reviewer | ① 조건부 허용의 판정 주체가 감수자 · 검사기 비커버 |
| 57 | s005/b2 (L50–50) | add/update의 3요소 제시 확인(승인 계약·독자 failure mechanism·기존 권위 coverage 차이) | Obligation | D: agent-discipline-reviewer | ① 감수자 주어 · TDD 입장 규율은 검사기 비커버(§16 기본값 discipline-*) |
| 58 | s005/b2 (L50–50) | boundary 차이·recipe·피라미드·coverage 목표만의 add 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 59 | s005/b2 (L50–50) | 같은 제품 failure·독자 failure 부재 시 reuse(write 0) | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 60 | s005/b2 (L50–50) | 공개 Python 후보의 사용자 승인 또는 deployed consumer evidence 요구 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 승인 evidence 확인은 감사 렌즈(승인 자체는 Coordinator 소유 절차와 구분) |
| 61 | s005/b3 (L51–51) | 비자격 후보 목록의 add 근거 불인정 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(테스트 입장 규율) |
| 62 | s005/b3 (L51–51) | 승인 public contract·독자 failure 부재 시 reject 또는 reuse 방향 반송 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 반송 대상 결정은 감사 렌즈 산출 |
| 63 | s005/b3 (L51–51) | 입장 행 없는 테스트 신규 의무화 금지 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 리뷰어 자기 산출(테스트 의무 발명)의 감독 주체는 Coordinator |
| 64 | s005/b4 (L52–52) | remove/weaken의 3요소 요구(계약 종료 근거·exact target·남는 현행 보호 위치) | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 65 | s005/b4 (L52–52) | 명세 침묵·구현 불일치·중복 추정만의 삭제 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 66 | s005/b4 (L52–52) | migration 전용 테스트의 유지·제자리 갱신·종료 시 제거 수명 주기 보존 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(migration 전용 테스트 판별은 의미 판정) |
| 67 | s005/b5 (L53–53) | 전 test diff hunk의 승인 행·독자 failure 대조 | Obligation | D: agent-discipline-reviewer | ① 감수자 주어 · 검사기 비커버 |
| 68 | s005/b5 (L53–53) | decision별 편집 허용 범위(add/update만 Red·edit / reuse·reject write 0 / retain 무편집 / remove·weaken 승인 target) | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 69 | s005/b5 (L53–53) | implementation-test의 적용 시점 한정(입장 승인 뒤 mechanics·assertion 품질) | Obligation | D: agent-discipline-reviewer | ① 문면이 스킬 적용 순서를 규정 — 감수자 자기 렌즈 운용 규범 |
| 70 | s005/b5 (L53–53) | recipe로 입장 결정 신설 금지 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 입장 결정 소유는 Phase 1 게이트(Coordinator·architect) |
| 71 | s005/b6 (L54–55) | 첫 Green 뒤 잔존 비계(loader·guard·대체 decorator·skip/xfail·helper)의 blocker 판정 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(비계 판별은 의미 판정) |
| 72 | s005/b6 (L54–55) | 비계를 만든 같은 역할의 즉시 제거 | Obligation | D: command-dddjango | ① 문면이 «만든 같은 역할»(coder·acceptance-tester)을 주체로 지목 — 역할 라우팅 소유 Coordinator |
| 73 | s005/b6 (L54–55) | 기존 비계의 이번 실행 산출 간주·임의 삭제 유도 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 한정(거짓지적 방지 규범) |
| 74 | s006/b1 (L57–58) | 12-slot과 현재 project-wide production tree/inventory 대조 | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring «project inventory correspondence» 검증 축 + ① 문면이 Phase 1 필수 대조로 지정 — 기계 대조의 의미 잔여는 감수자 |
| 75 | s006/b1 (L57–58) | 전 표면의 project-wide 확인(API/controller/URLconf/registrar module·instance·namespace/version·scope·scope-bc/error-bc·profile·module sharing) | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring project inventory correspondence · ① 문면 «project-wide로 확인한다» |
| 76 | s006/b1 (L57–58) | inventory 누락·중복 module·profile 혼합 공유·API instance 복수의 blocker 및 Coordinator 승인 handback | Obligation | D: command-dddjango | ① 문면 «checker가 추론하지 못해도 blocker이며 Coordinator의 승인 handback 대상» — 기본값 이탈의 명시 문면 근거 |
| 77 | s006/b2 (L59–59) | canonical common path·공통 FrameworkErrorSchema 하나·common 내 BC concrete 부재·slot 5/6 확인 | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring «validates the canonical common/BC FrameworkErrorSchema modules» — 기계 커버 + 승인 evidence 대조는 감수자 |
| 78 | s006/b2 (L59–59) | reuse의 관찰된 기존 exact-shape evidence 요구 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 — evidence 관찰성은 형태 밖(검사기는 자기 입력 inventory를 전제·파일럿 순환 배선 교훈) |
| 79 | s006/b2 (L59–59) | create·approved-change의 분리된 명시적 사용자 shape 승인 evidence 요구(부재 시 blocker) | Obligation | D: command-dddjango | ① 문면이 일반 G1과 분리된 사용자 승인을 지목 — 승인 절차 소유 Coordinator |
| 80 | s006/b2 (L59–59) | public 오류 BC의 canonical bc_error_schema.py 단일 소유(ErrorCode·ErrorSchema·concrete 전부) | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring canonical BC module 검증 + ④ #114 귀속(rule-owner-map ⓒ 4규칙 — error-centralization 소유) |
| 81 | s006/b2 (L59–59) | public 오류 없는 BC의 오류 선언 선제작 금지(빈 bc_error_schema.py는 고정 칸) | Prohibition | E: check-layer-skeleton.py + check-error-centralization.py · D: agent-discipline-reviewer | ④ 문면이 #114·#488을 인용 — #488 고정 칸은 layer-skeleton docstring 소유·#114는 error-centralization 소유 |
| 82 | s006/b2 (L59–59) | Phase 2의 direct core 재선언·exact 복제·미승인 local Schema·inner-layer 의존·tree mismatch 미반송의 blocker | Obligation | E: check-error-centralization.py + check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 두 docstring의 canonical 소유권·controller 계약 축 + ① 문면이 미반송까지 blocker로 지정(의미 잔여는 감수자) |
| 83 | s006/b3 (L60–60) | preserve-established scope의 승인 artifact evidence대로 유지 | Obligation | D: agent-discipline-reviewer | ② error-centralization·controller-contract docstring이 preserve profile에 schema semantics 미적용을 명시 — 기계 밖 보존 판정은 감수자 |
| 84 | s006/b3 (L60–60) | RFC 9457 artifact 사유의 code-profile 이주·두 profile 한 module 혼합 금지 | Prohibition | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring project inventory correspondence(mixed-profile shared module) + ① 문면 금지 명문 |
| 85 | s006/b3 (L60–60) | 격리 범위의 한정(오류 응답 표면까지 — 파일트리·배선/등록·import 방향·테스트 규율은 profile 무관 표준) | Obligation | E: check-layer-skeleton.py + check-context-isolation.py · D: agent-discipline-reviewer | ① 문면이 #105~#112 등 표준 대조를 지목 + ④ 트리·배선 판정은 layer-skeleton(#486~#490)·context-isolation(#110·#431) 소유 |
| 86 | s006/b4 (L61–62) | discipline reviewer 소유 5종(physical placement·forbidden extraction/circumvention·import direction·controller structure·scope completeness) | Obligation | D: agent-discipline-reviewer | ① 문면이 소유자를 직접 선언 — 위임 대상의 명문 근거 |
| 87 | s006/b4 (L61–62) | public-code 적정성의 중복 판정 금지(API reviewer 소유) | Prohibition | D: agent-design-review-api | ① 문면이 wire meaning·public code catalog·HTTP semantics·compatibility 소유를 API reviewer로 지목 — 기본값 이탈의 문면 근거 |
| 88 | s006/b4 (L61–62) | OpenAPI/runtime 구현 기술 정확성의 acceptance-tester/coder·implementation-* 소유 표시 | Obligation | D: command-dddjango | ① 문면 술어가 «…소유로 표시한다»(감수자 리포트의 표시 의무) — P-C 판별자 ⒤ 표시·라우팅 의무는 리포트 수납 주체 Coordinator + ④ 절차 층 기본값(s003/b1 반송·표시 조항과 동일 자) |
| 89 | s007/b1 (L64–65) | 구현 체크리스트의 Phase 2 implementation 한정 적용 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 모드별 적용 범위 계약 |
| 90 | s007/b1 (L64–65) | Phase 1·DYNAMIC 모드에서 묶음 미수령을 이유로 한 항목 실패 처리 금지 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 모드별 거짓지적 방지 절차 |
| 91 | s007/b2 (L66–66) | 승인 add/update 행 한정 Red→Green→Refactor 흔적·행위 검증 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · TDD 규율은 검사기 비커버(§16 기본값 discipline-tdd→discipline-reviewer) |
| 92 | s007/b2 (L66–66) | reuse/retain/reject 사유의 새 Red·case·assertion 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 93 | s007/b3 (L67–67) | 행위중심 테스트·과도 mock의 리팩토링 내성 침해 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(mock 과다는 의미 판정) |
| 94 | s007/b3 (L67–67) | AAA 구조·격리·좋은 테스트 4대 특성 점검 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 95 | s007/b4 (L68–68) | 신규·확장 migration 전용 테스트 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(discipline-tdd §5.5 인용) |
| 96 | s007/b4 (L68–68) | 삭제·assertion 약화의 승인 remove/weaken 종료 근거·exact target 연결 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 97 | s007/b4 (L68–68) | 혼합 테스트 현행 assertion의 잔존 확인 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 98 | s007/b4 (L68–68) | 현재 구현에 맞추려는 올바른 failing test 삭제 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 99 | s007/b4 (L68–68) | pending의 retain·완료 위장 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 100 | s007/b5 (L69–69) | 현재 model·API 테스트의 migration forward/reverse 안전 대체 증거 주장 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 101 | s007/b5 (L69–69) | suite green·무관 실패의 테스트 삭제·편집 확대 단독 근거 사용 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 102 | s007/b6 (L70–70) | 승인 행의 계약·boundary·failure mechanism 동시 비교 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 103 | s007/b6 (L70–70) | 독자 failure 없는 인수↔단위 복제의 입장 위반 판정 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 104 | s007/b6 (L70–70) | 다른 failure mechanism을 가진 별도 add 행의 유효 인정 | Permission | D: agent-discipline-reviewer | ① 감수자 판정 · 거짓지적 방지 허용 조항 |
| 105 | s007/b6 (L70–70) | 리뷰 중 발견 엣지의 즉석 테스트 의무화 금지(후보 설계 반송) | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 설계 반송 라우팅 소유 Coordinator |
| 106 | s007/b7 (L71–71) | pytest 관용구 준수(함수형·assert·django_db 마커) | Obligation | D: agent-discipline-reviewer | ② check-test-config 관할은 ⑴ settings 바인딩·⑵ test/ 구조·⑶ 환경축뿐이라 관용구 «형태»는 전 슬라이스 밖 — 기계 절반이 없어 enforcedBy 미병기(같은 블록의 #392·#387 조항만 병기 유지) · ④ 위임 기본값(implementation-test §7→감수자) |
| 107 | s007/b7 (L71–71) | mock 도구의 mocker 사용(raw unittest.mock 패치 폴백 위반) | Prohibition | D: agent-discipline-reviewer | ① 감수자 명시 판정 · 검사기 비커버(implementation-test §7 인용) |
| 108 | s007/b7 (L71–71) | 정당 import(create_autospec·ANY/call/PropertyMock)의 거짓지적 금지 | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외 — 감수자 판정 한정 |
| 109 | s007/b7 (L71–71) | ORM 영속 픽스처의 factory_boy 사용 | Obligation | E: check-test-config.py · D: agent-discipline-reviewer | ④ #392 factories/에는 factory_boy 픽스처만(test-config docstring 담당 규칙) — 자리 밖 픽스처는 감수자 |
| 110 | s007/b7 (L71–71) | 정확 필드 행·VO 직접 생성·objects.create 스파이의 정당 인정 | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외(implementation-test §20.5 인용) |
| 111 | s007/b7 (L71–71) | Django TestCase 회귀 금지(새 테스트는 무조건 pytest·관례 존중 예외 없음) | Prohibition | E: check-test-config.py · D: agent-discipline-reviewer | ④ #387 test/unit/의 django.test TestCase 금지(test-config 담당) + ② 바인딩 슬라이스 — 자리 밖 TestCase는 감수자 |
| 112 | s007/b7 (L71–71) | over-mock(협력자까지 mock)의 raw-폴백 동급 이상 취급 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(§16.1 Mockery) |
| 113 | s007/b8 (L72–72) | Risky Write·outbox·constraint·concurrency criteria의 자동 테스트 의무화 금지 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(criteria는 candidate signal) |
| 114 | s007/b8 (L72–72) | 승인 입장 행의 protected contract·독자 failure 실제 행사 감사 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 115 | s007/b8 (L72–72) | add/update의 결정적 CAS 충돌·동시 요청 또는 동등 테스트 요구 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(동시성 실현은 의미 판정) |
| 116 | s007/b8 (L72–72) | 구조 가드만·순차 루프 경합 위장의 실패 판정 | Prohibition | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 117 | s007/b8 (L72–72) | 다른 boundary 권위 테스트가 같은 failure를 잡을 때 reuse 유효(신규 요구 금지) | Permission | D: agent-discipline-reviewer | ① 거짓지적 방지 허용 조항 — 감수자 판정 |
| 118 | s007/b8 (L72–72) | criteria 있고 입장 행 없을 때 테스트 발명 금지·Phase 1 입장 누락 반송 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — Phase 1 반송 라우팅 소유 Coordinator |
| 119 | s007/b9 (L73–73) | 동치 암묵 가드 공존 + 구별 단언 부재 테스트의 important 판정(The Liar) | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버(implementation-test §16.1) |
| 120 | s007/b9 (L73–73) | 다층 방어 병행의 정상 인정(제약 제거가 아니라 테스트 귀속을 본다) | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외(architecture-db §9.5 백스톱 병행 권장) |
| 121 | s007/b9 (L73–73) | near-mutation 판정의 그레이더 FC-2 소유·정적 신호 한정 관찰 | Obligation | D: agent-discipline-reviewer | ① 문면이 판정 범위를 정적 신호로 한정 — 감수자 자기 렌즈 한정 규범(FC-2는 registry 밖 개체) |
| 122 | s007/b10 (L74–74) | 정확 경계값의 입장 표 candidate 선행 | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 123 | s007/b10 (L74–74) | 승인 행이 특정한 경계의 입력·구별 단언 실제 행사 확인(계층 불문) | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 124 | s007/b10 (L74–74) | 다른 승인 권위 테스트가 같은 failure를 행사하면 reuse 유효(단위 부재 지적 금지) | Permission | D: agent-discipline-reviewer | ① 거짓지적 방지 허용 조항 |
| 125 | s007/b10 (L74–74) | 입장 행 부재·recipe만 있을 때 새 경계 테스트 요구 금지·설계 반송 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 설계 반송 라우팅 소유 |
| 126 | s007/b10 (L74–74) | 항진 단언·경합 위장·The Liar의 mechanics 위반 지적(즉석 처방 금지) | Obligation | D: agent-discipline-reviewer | ① 감수자 판정 · 검사기 비커버 |
| 127 | s007/b11 (L75–75) | 클린코드 6렌즈 점검(네이밍 정확성·함수 크기/단일 책임·캡슐화·DRY·오류 처리·SOLID) | Obligation | D: agent-discipline-reviewer | ④ 위임 기본값 표(discipline-cleancode→discipline-reviewer) · 트리·명명 «값» 축은 houserules 백스톱 소유라 여기서는 일반 렌즈만 |
| 128 | s007/b12 (L76–76) | 도메인 판정 메서드의 프로덕션 호출처 확인(테스트 전용=죽은 코드) | Obligation | D: agent-discipline-reviewer | ② check-app-container docstring «판정-소유 형태(빈혈) 같은 의미 변종은 범위 밖(discipline-reviewer 몫)» — 명시 위임 |
| 129 | s007/b12 (L76–76) | 판정의 인프라 복제(repo SQL WHERE·update() kwargs·우회 서비스 분기)로 도메인 메서드 무력화 금지 | Prohibition | D: agent-discipline-reviewer | ② 동상(app-container docstring 의미 변종 위임) · architecture-ddd §3.2 판정 소유 인용 |
| 130 | s007/b12 (L76–76) | C형 빈혈(도메인 규칙 메서드 0개·판정이 인프라에만 존재)의 blocker 판정 | Obligation | D: agent-discipline-reviewer | ① 문면 «전적으로 너의 의미 점검 몫» — 결정적 백스톱 부재 자인 |
| 131 | s007/b12 (L76–76) | C형 빈혈 적출의 3점 확인(domain_layer 규칙 메서드 0개·외부 배치·이름 위장 변종) | Obligation | D: agent-discipline-reviewer | ① 문면이 백스톱 부재를 명시(형태 매칭 FP/FN 양립 불가) |
| 132 | s007/b12 (L76–76) | 판정·불변식 보유 도메인 메서드의 평면 ORM 모델 직접 부착 금지(domain_layer 이주) | Prohibition | D: agent-discipline-reviewer | ④ #249·#256(domain-model)은 «이주 목적지» domain_layer 안 골격만 보아 위반 현장(domain_layer 밖 평면 ORM 모델의 판정 메서드)을 못 본다 — 집행 아님(enforcedBy 미병기) · ② check-app-container docstring «판정-소유 형태(빈혈) 같은 의미 변종은 범위 밖(discipline-reviewer 몫)» + ① 판정 소유→구조 이주(architecture-ddd §3.2)는 감수자 전담 |
| 133 | s007/b12 (L76–76) | 판정 없는 순수 데이터 소스(필드·CheckConstraint만)의 평면 허용 | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외 — 데이터소스 면제 문면 |
| 134 | s007/b12 (L76–76) | 책임 배치·죽은 코드 규율 한정(쿼리 정확성 비판정) | Obligation | D: agent-discipline-reviewer | ① 문면 «네가 본다» + 소유 경계 선언(s008 경계와 짝) |
| 135 | s007/b13 (L77–77) | touched 코드 한정 관찰(untouched 기존 리터럴 grandfather 면제) | Exception | E: check-choices-literal-consumption.py · D: agent-discipline-reviewer | ② docstring 1) «touched인 파일만 본다 … 기존 리터럴은 grandfather» 동일 게이트 |
| 136 | s007/b13 (L77–77) | ① 닫힌 집합 원소의 원시 리터럴 산재 important(1곳째부터 승격) | Obligation | D: agent-discipline-reviewer | ② docstring «보지 않는 것(의미 레인 = discipline-reviewer 몫): … 닫힌 집합의 미승격» — 명시 위임(cleancode §2.14) |
| 137 | s007/b13 (L77–77) | ①의 DRY 사안 중복 분류 금지(이중 계상 금지) | Prohibition | D: agent-discipline-reviewer | ① 문면의 분류 배타 규범 — 감수자 자기 분류 규율 |
| 138 | s007/b13 (L77–77) | ② 선언된 Enum/choices의 리터럴 소비 important — 백스톱 사각 4변종(변수 우회·간접 queryset·비교식·__in) 직독 | Obligation | E: check-choices-literal-consumption.py · D: agent-discipline-reviewer | ① 문면이 결정적 백스톱 check-choices-literal-consumption을 직접 지목 + ② docstring 직접형 (a)(b) 한정·의미 레인 위임 일치 |
| 139 | s007/b13 (L77–77) | 심볼 치환의 판정 소유 위반 면책 금지(복합 판정은 빈혈 불릿 단일 분류) | Prohibition | D: agent-discipline-reviewer | ① 문면의 분류 배타 규범 |
| 140 | s007/b13 (L77–77) | ③ domain의 models.TextChoices 역참조 important(값 집합 단일 출처=domain enum) | Obligation | D: agent-discipline-reviewer | ② choices-literal docstring «계층 역참조»는 보지 않는 것(의미 레인) — 명시 위임(implementation-django §2.5) |
| 141 | s007/b13 (L77–77) | ③의 구조 이주 사안 중복 분류 금지(값 집합 소유만 여기) | Prohibition | D: agent-discipline-reviewer | ① 문면의 분류 배타 규범 |
| 142 | s007/b13 (L77–77) | ④ 외부 관찰 계약 기댓값의 프로덕션 Enum·상수 역수입 important(자기참조 오라클) | Obligation | D: agent-discipline-reviewer | ② choices-literal docstring 3) 테스트 경로 면제(«테스트 기댓값 리터럴은 §15.4가 허용») — 기계 밖 오라클 자기참조는 감수자 |
| 143 | s007/b13 (L77–77) | ⑤ 발행 이벤트 봉투 discriminator의 domain StrEnum 미파생 important(birth-enum) | Obligation | D: agent-discipline-reviewer | ① 문면 «대응 백스톱 없음 … 위치 판정은 전적으로 네 몫» — 백스톱 부재 자인(architecture-ddd §3.7) |
| 144 | s007/b13 (L77–77) | union-enum 동기 후보의 승인 입장 행 한정 mechanics 감사 | Exception | D: agent-discipline-reviewer | ① 조건부 한정 — 감수자 판정 |
| 145 | s007/b13 (L77–77) | 입장 행 부재 시 동기 테스트 즉석 요구 금지·candidate 설계 반송 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 설계 반송 라우팅 소유 |
| 146 | s007/b13 (L77–77) | ⑤의 제외 4종(버전 태그·상류 중계 소비 태그·데이터소스 BC·OHS contract wire Literal) | Exception | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ OHS contract 무의존 규칙 #472(context-isolation 담당) + ① 제외 목록의 판정은 감수자 |
| 147 | s007/b13 (L77–77) | ①과 ⑤의 배타 분류(한 사건은 하나로만) | Prohibition | D: agent-discipline-reviewer | ① 문면의 분류 배타 규범 |
| 148 | s007/b13 (L77–77) | 거짓지적 방지 목록(테스트 심볼 단언·사람 대상 서술·정의부 우변·.value 파생·Literal 잠금·외부 프로토콜 문자열·설정 키·마이그레이션 historical value·pass-through·한 파일 로컬·다른 지식 동일 값) | Exception | E: check-choices-literal-consumption.py · D: agent-discipline-reviewer | ② docstring 3)~5) 면제(마이그레이션 historical value·.value 평탄화·테스트 경로)와 문면 목록이 동축 |
| 149 | s007/b14 (L78–78) | 엔진·연결 트랜잭션/락/격리 메커니즘의 설계 소유(명세 승인 없는 의미 변경 금지) | Prohibition | E: check-mechanism-ownership.py · D: agent-discipline-reviewer | ② docstring ⑴ «프로덕션 DB 엔진의 트랜잭션·락·격리 메커니즘을 명세 승인 없이 커스텀 백엔드로 교체한 정확한 형태만 차단» — 축자 일치 |
| 150 | s007/b14 (L78–78) | 메커니즘 레드 플래그 9종의 blocker 판정(형태 불문 동일 위반) | Obligation | E: check-mechanism-ownership.py · D: agent-discipline-reviewer | ② docstring AND 게이트는 ENGINE 교체·DatabaseWrapper만 커버 — 몽키패치·시그널·init_command·미들웨어·conftest 패치는 형태 밖(감수자) |
| 151 | s007/b14 (L78–78) | stock OPTIONS·안전 PRAGMA 화이트리스트·명세 명시 승인 메커니즘의 통과 | Permission | D: agent-discipline-reviewer | ① 거짓지적 방지 허용 목록 — 감수자 판정 |
| 152 | s007/b14 (L78–78) | 이번 diff 신규 변경 한정 관찰(기존 코드 존중) | Exception | E: check-mechanism-ownership.py · D: agent-discipline-reviewer | ② docstring 4) «(git 레포면) 이번 변경에서 추가/수정됨» 동일 게이트 |
| 153 | s007/b14 (L78–78) | 프로덕션 경로 미배선 테스트 격리 전용 설정의 통과 | Exception | E: check-mechanism-ownership.py · D: agent-discipline-reviewer | ② docstring 1) «프로덕션(비테스트) settings» 한정과 동축 |
| 154 | s007/b14 (L78–78) | 책임 배치·소유권 규율 한정(ORM/쿼리 정확성 비판정) | Obligation | D: agent-discipline-reviewer | ① 문면 «네가 본다» + 소유 경계 선언(s008과 짝) |
| 155 | s007/b15 (L79–79) | canonical common module의 승인 shape 단일 소유·BC concrete 부재 | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring «validates the canonical common/BC FrameworkErrorSchema modules» — schema checker 축(§16 매핑 표) |
| 156 | s007/b15 (L79–79) | 공통 shape 신설·변경 시 G1과 분리된 사용자 shape 승인 evidence 부재의 blocker | Obligation | D: command-dddjango | ① 문면이 일반 G1과 분리된 명시 승인을 지목 — 승인 절차 소유 Coordinator |
| 157 | s007/b15 (L79–79) | public 오류 BC의 canonical bc_error_schema.py 단독 소유(ErrorCode·ErrorSchema·concrete 전부) | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring BC schema 구성·wire-code uniqueness 검증 + ④ #114 귀속 |
| 158 | s007/b15 (L79–79) | import 부재만으로 불충분(inner layer 계층 소유 판정 강화) | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ #2 «안쪽 두 칸은 구체 기술을 모른다»(context-isolation 담당)가 import 축을 커버 — 그 밖 운반 판정은 감수자 |
| 159 | s007/b15 (L79–79) | import-free DTO·VO의 HTTP status/code 의미 inner layer 운반 blocker | Prohibition | D: agent-discipline-reviewer | ① 문면이 import 없는 의미 운반을 지목 — 형태 밖(검사기 사각) 자인 |
| 160 | s007/b15 (L79–79) | 정당 도메인 status의 구별 기준(값 의미·소비 경로가 HTTP 선택과 무관) | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외 — 감수자 판정 |
| 161 | s007/b16 (L80–80) | code-profile managed surface의 오류 helper/handler/factory/serializer/mapping 생성·호출 금지 | Prohibition | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② docstring «direct controller-owned code-profile error mapping» 집행 — presentation helper 차단 축(파일럿 판형 동일) |
| 162 | s007/b16 (L80–80) | controller의 짧은 failure→prepared error→Status mapping 반복의 DRY 면책 | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외(의도된 명시성) — 감수자 판정 |
| 163 | s007/b16 (L80–80) | 성공 Schema·download·streaming·redirect·schema-less 204의 오류-helper 금지 밖 | Exception | E: check-response-schema-bypass.py · D: agent-discipline-reviewer | ② docstring framework-native 성공 carveout 구현(파일럿 L-F 실측 — carveout 4종은 response-schema-bypass 소관) |
| 164 | s007/b16 (L80–80) | 승인 preserve-established handler의 범위 한정 보존(새 code-profile 정당화 재사용 금지) | Prohibition | D: agent-discipline-reviewer | ② controller-contract docstring «preserve-established … add no new error-mapping semantics» — 보존 판정은 기계 밖 |
| 165 | s007/b17 (L81–81) | 10번 slot 승인 path와 코드의 대조 | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② docstring controller 선택·계약 검증 + ① slot 승인 evidence 대조는 감수자 |
| 166 | s007/b17 (L81–81) | exception path의 좁은 try(준비는 밖·try 안에 최외곽 application call 한 문장) | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② docstring controller 계약 집행(파일럿 b-616~620 판형 동일) |
| 167 | s007/b17 (L81–81) | try 안 branch·성공 변환·logging 동거 금지 | Prohibition | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 동상 — controller 계약 |
| 168 | s007/b17 (L81–81) | 같은 owning BC의 승인 concrete 예외 또는 concrete만 든 tuple 한정 catch | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 동상 — controller 계약 |
| 169 | s007/b17 (L81–81) | bare/Exception/BaseException·raw DB/SDK/framework·cross-BC·재수출 alias·비-concrete 혼합 tuple의 blocker | Prohibition | E: check-api-error-controller-contract.py + check-context-isolation.py · D: agent-discipline-reviewer | ② controller-contract #62 «except Exception 금지» + ④ 타 BC 예외 축은 context-isolation(#12·#13) 소유 |
| 170 | s007/b17 (L81–81) | 자기 raise 즉시 catch·HttpError forwarding·re-raise·handler forwarding 금지 | Prohibition | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 동상 — controller 계약(파일럿 b-652~656 판형) |
| 171 | s007/b17 (L81–81) | Result/None/outcome path의 1회 호출·인위적 try 없는 직후 branch 직접 mapping | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 동상 — controller 계약(파일럿 b-621~625 판형) |
| 172 | s007/b17 (L81–81) | ACL/OHS의 승인 upstream failure 번역과 controller cross-BC catch의 구별 | Exception | E: check-context-isolation.py + check-synthetic-infra-exc.py · D: agent-discipline-reviewer | ④ #13 OHS 소비는 ACL뿐·#164 도메인 예외 번역(context-isolation) + #129 전수 명시 매핑(synthetic-infra-exc) |
| 173 | s007/b18 (L82–82) | 승인 concrete의 fixed value class default 제공·무인자 생성 가능 | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring schema contract backstop(파일럿 «concrete 오류의 무인자 생성» 동일 판형) |
| 174 | s007/b18 (L82–82) | class default의 직접 선언·승인 base 상속 택일(불필요 재선언 불요구) | Permission | E: check-error-centralization.py · D: agent-discipline-reviewer | ② 동상 — 재선언 metadata 축 |
| 175 | s007/b18 (L82–82) | 승인된 direct BC-base 생성의 keyword 명시 범위(required 전부+승인 optional만) | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② docstring constructor keyword 집합 검증(파일럿 L-F 실측 — controller-contract 소관) |
| 176 | s007/b18 (L82–82) | catch·failed branch의 두 인자 Status 직접 반환 | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 동상 — controller 계약 |
| 177 | s007/b18 (L82–82) | plugin의 status body property 요구 blocker | Prohibition | D: agent-discipline-reviewer | ② 파일럿 L-F 중재 — 검사기는 자기 입력(inventory)을 전제하므로 순환 배선 해소·기본값 비채택 판정은 감수자 |
| 178 | s007/b18 (L82–82) | 승인 response header의 주입된 temporal HttpResponse 기입 | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 동상 — controller 계약(파일럿 b-733~737 판형) |
| 179 | s007/b18 (L82–82) | 오류 tuple·raw Response/JsonResponse/HttpResponse·dict body·factory/serializer/helper indirection의 blocker | Prohibition | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② 동상 — controller 계약 |
| 180 | s007/b19 (L83–83) | 직접 반환 BC 오류 status의 response= 같은 BC base 선언 | Obligation | E: check-openapi-error-declaration.py · D: agent-discipline-reviewer | ② docstring «직접 반환하는 BC 오류와 response={status: <Bc>ErrorSchema} 선언의 일치를 검증» |
| 181 | s007/b19 (L83–83) | mapping tuple·runtime 반환·generated OpenAPI 3자의 완전·동일 | Obligation | E: check-openapi-error-declaration.py · D: agent-discipline-reviewer | ② 동상 — OpenAPI checker |
| 182 | s007/b19 (L83–83) | framework-owned status(401·403·route 404·422·429·HttpError·500)의 BC 오류 직접 반환·BC base 광고 금지 | Prohibition | E: check-openapi-error-declaration.py + check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② OpenAPI 선언 축(openapi-error-declaration) + provenance 제한(controller-contract) — 파일럿 §6.2 판형과 동축 |
| 183 | s007/b19 (L83–83) | auth backend 반환 계약(성공=identity/principal·실패=None 또는 AuthenticationError) | Obligation | D: agent-discipline-reviewer | ① 문면 지목 · 파일럿 판형에서도 auth adapter 계약은 위임 기본값(검사기 비커버) |
| 184 | s007/b19 (L83–83) | truthy FrameworkErrorSchema/Schema의 request.auth 주입 금지 | Prohibition | D: agent-discipline-reviewer | ① 문면 지목 · 검사기 비커버(s007 사각 목록 (g)와 동축) |
| 185 | s007/b19 (L83–83) | framework-established header dependency 은닉·명세 밖 header 날조 금지 | Prohibition | D: agent-discipline-reviewer | ① 문면 지목 · 검사기 비커버(숨은 의존은 형태 밖) |
| 186 | s007/b19 (L83–83) | status→BC base 선언만으로 subset 증명 불인정(runtime mapping case 검증 생략 금지) | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② docstring controller 계약(실제 mapping case) + ① 생략 금지 판정은 감수자 |
| 187 | s007/b20 (L84–84) | 오류 1~5축의 active dddjango-code-json scope 한정 적용 | Obligation | E: check-api-error-controller-contract.py + check-error-centralization.py · D: agent-discipline-reviewer | ② 두 docstring 공통 «The checker is deliberately profile-gated / profile- and source-selected» |
| 188 | s007/b20 (L84–84) | preserve-established scope의 승인 native forwarding·handler·body/return form·mapping 보존 | Obligation | D: agent-discipline-reviewer | ② docstring «preserve-established … add no new error-mapping semantics» — 보존 판정은 기계 밖 |
| 189 | s007/b20 (L84–84) | 5축을 이유로 한 code-profile 이주 금지 | Prohibition | D: agent-discipline-reviewer | ① 문면 금지 명문 · 검사기 비커버 |
| 190 | s007/b20 (L84–84) | profile 경계의 범위 한정(배선·등록은 profile 무관 규율 소유) | Exception | D: agent-discipline-reviewer | ① 문면이 아래 배선 규율로 소유를 넘김 — 이중 계상 방지 규범 |
| 191 | s007/b21 (L85–85) | checker exit 0의 semantic compliance 증거 불인정 | Prohibition | D: agent-discipline-reviewer | ① 문면 «exit 0이어도 증거가 아니다» — 백스톱 사각 전담 선언 |
| 192 | s007/b21 (L85–85) | checker 사각 7종(a~g)의 직독 의무 | Obligation | D: agent-discipline-reviewer | ① 문면이 사각 목록을 감수자 직독 대상으로 지정 — 정의상 검사기 비커버(한 의무 동사의 목적어 열거라 단일 채번) |
| 193 | s007/b22 (L86–86) | contract scope마다 project api.py의 API instance 단독 소유 | Obligation | E: check-composition-root.py · D: agent-discipline-reviewer | ④ #105/#112 api/ 직계·등록 파일 규칙(composition-root 담당) + ① 문면 scope 단위 단일 instance |
| 194 | s007/b22 (L86–86) | BC api_router의 side-effect-free 자기 controller 한정 등록 | Obligation | E: check-composition-root.py · D: agent-discipline-reviewer | ④ #107 «def register_<bc>_api(api)» 시그니처 축자 검사(composition-root 담당) |
| 195 | s007/b22 (L86–86) | project urls.py의 registrar 명시 1회 호출 후 API mount | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ #431 «허용은 urls.py의 register_<bc>_api(api) 호출»(context-isolation 담당) |
| 196 | s007/b22 (L86–86) | controller의 auto_import=False | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ #110 auto_import=False(context-isolation docstring 담당 규칙) |
| 197 | s007/b22 (L86–86) | project API import·module-top-level 등록·dynamic registrar·import-time side effect·scope 내 API 복수의 blocker | Prohibition | E: check-context-isolation.py + check-composition-root.py · D: agent-discipline-reviewer | ④ #431 부작용 등록 금지(context-isolation) + composition-root DI 레인 — dynamic 변종은 사각(b21 (b))으로 감수자 |
| 198 | s007/b22 (L86–86) | HTTP registrar와 DI-only composition_root/의 혼합 금지 | Prohibition | E: check-composition-root.py · D: agent-discipline-reviewer | ② docstring «DI 조립은 BC 루트의 composition_root/가 소유» + #497 단일 파일 변종 차단 |
| 199 | s007/b22 (L86–86) | root-local catalog/mapping·registrar/composition lookalike의 직접 확인 | Obligation | D: agent-discipline-reviewer | ② docstring «in-tree 파일 내장 변종은 discipline-reviewer 의미 레인 몫» — 명시 위임 |
| 200 | s007/b22 (L86–86) | controller 형태의 승인 presentation 계약 보존 | Obligation | D: agent-discipline-reviewer | ① 문면 지목 · 검사기 비커버(승인 계약 대조) |
| 201 | s007/b22 (L86–86) | 406/415 대응 사유의 class controller 함수형 전환·별도 API instance 격리 금지 | Prohibition | D: agent-discipline-reviewer | ② check-ninja-boundary-middleware docstring의 406/415 언급은 «driving_layer 미들웨어의 settings.MIDDLEWARE 자가등록» 한 형태만 판정 대상이라 이 규범의 세 형태(함수형 Router 전환·별도 API instance 격리)를 검출하지 못한다 — 인접 사건군 참고일 뿐 집행 아님(enforcedBy 미병기) · ① 승인 presentation 계약 보존 판정은 감수자 |
| 202 | s007/b22 (L86–86) | preserve-established scope의 registration/composition 표준 대조(보존 대상은 오류 wire 산출물) | Override | E: check-composition-root.py + check-context-isolation.py · D: agent-discipline-reviewer | ① 문면이 preserve 보존 원칙을 배선 축에서 눌러 이기는 우선 규칙(«preserve 가 보존하는 것은 … 배선이 아니다» — 구 문구 철회 명문·2026-08-12 라운드 1′ 실증)이라 class=Override(코퍼스 선례 implementation-django s015-2.5) + ④ 배선 규칙 소유 검사기 2종 |
| 203 | s007/b22 (L86–86) | 배선 표준화의 오류 profile 이주 함의 금지(오류 산출물은 slot 승인대로) | Prohibition | D: agent-discipline-reviewer | ① 문면 배타 규범 — 이중 계상·오적용 방지 |
| 204 | s007/b22 (L86–86) | Phase 1 project-wide inventory·mixed-profile sharing 점검의 profile 무관 유지 | Obligation | E: check-error-centralization.py · D: agent-discipline-reviewer | ② docstring project inventory correspondence + ① profile 무관 명문 |
| 205 | s007/b23 (L87–87) | raw DB/SDK/network exception의 safe framework 500 유지 | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② docstring controller 계약(raw 예외 catch 차단) — 파일럿 §6.2 «기본 경로 = framework 미식별 500» 동축 |
| 206 | s007/b23 (L87–87) | global recognizer·retryable handler·문자열/SQLSTATE 분류 요구·신설 금지 | Prohibition | E: check-transient-overmapping.py · D: agent-discipline-reviewer | ② docstring «dddjango-code-json에서는 custom handler/recognizer 자체가 … 위배 … 이 checker가 발화하지 않아도 근거가 되지 않는다 … ③ discipline-reviewer 의미 체크가 담당» |
| 207 | s007/b23 (L87–87) | G1 명시 승인 시에만 owning infra/ACL의 정규화 후 controller 직접 흐름 mapping | Exception | D: command-dddjango | ① 문면이 G1 승인 조건을 지목 — 승인 절차 소유 Coordinator(파일럿 판형 동일) |
| 208 | s007/b23 (L87–87) | raw infrastructure exception 합성·controller 직접 catch 우회 금지 | Prohibition | E: check-synthetic-infra-exc.py + check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② synthetic-infra-exc docstring ⑴ 합성 금지(ACL-EX2) + controller-contract raw 예외 catch 차단 |
| 209 | s007/b24 (L88–88) | brownfield handler의 기존 permanent/retryable 구분 보존 | Obligation | E: check-transient-overmapping.py · D: agent-discipline-reviewer | ② docstring «G1에서 이미 승인된 preserve-established brownfield handler를 보존할 때 … 지키는 방어선» |
| 210 | s007/b24 (L88–88) | 영구장애의 retryable 확대 금지 | Prohibition | E: check-transient-overmapping.py · D: agent-discipline-reviewer | ② docstring AND 게이트 2)3) — 분기 부재+retryable 반환 차단(헬퍼 무조건-True 위장은 저-recall로 감수자 몫) |
| 211 | s007/b24 (L88–88) | preserve compatibility 점검의 범위 한정(code-profile handler/recognizer 요구·허용 레시피 아님) | Prohibition | D: agent-discipline-reviewer | ① 문면 배타 규범 + ② docstring 동일 취지 |
| 212 | s007/b25 (L89–89) | unknown failure의 framework 500 경로 유지 | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② docstring controller 계약(미식별 실패의 framework 소유) — b23 n1과 동축 |
| 213 | s007/b25 (L89–89) | 배포 설정 확인(DEBUG=False·traceback/민감정보 비노출·BC 변환 부재) | Obligation | D: agent-discipline-reviewer | ① 감수자 직독 · 27종 로스터에 배포 설정 보안 검사기 0(test-config는 환경 축 분할만) |
| 214 | s007/b25 (L89–89) | framework-owned body의 code/profile 형식 고정·exact-format 테스트 요구 금지 | Prohibition | D: agent-discipline-reviewer | ① 거짓지적 방지 금지 조항 — 감수자 판정 |
| 215 | s007/b26 (L90–90) | 복구 가능한 도메인·애플리케이션 오류의 view-local 재렌더·messages.error 보존 | Obligation | D: agent-discipline-reviewer | ① 문면 «reviewer가 직접 본다» + ④ 위임 기본값(implementation-django-web §11→discipline-reviewer) |
| 216 | s007/b26 (L90–90) | 인프라·미식별 시스템 오류의 중앙 handler500/500.html 경로 | Obligation | D: agent-discipline-reviewer | ① 동상 — 서버렌더 독립 판정 |
| 217 | s007/b26 (L90–90) | 서버렌더 레드 플래그 4종(시스템 오류 삼킴·사용자 오류 500화·permanent/retryable 미구별 5xx·broad except 둔갑)의 important | Obligation | D: agent-discipline-reviewer | ② transient-overmapping docstring은 API 경계 exception_handler 한정 — HTML local middleware는 그 밖(감수자 직독) |
| 218 | s007/b26 (L90–90) | invalid POST 재렌더·승인 transient의 503 분류·HTMX error fragment의 정상 인정 | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외 — 감수자 판정 |
| 219 | s007/b26 (L90–90) | 서버렌더 규율의 독립성(API error profile·handler 유무 무관) | Obligation | D: agent-discipline-reviewer | ① 문면 «reviewer가 직접 본다» — 소유 선언 |
| 220 | s007/b27 (L91–91) | 외부 식별자·수치 입력 필드의 상한 미선언 important(5xx 오분류 방지) | Obligation | E: check-usecase-dto-placement.py · D: agent-discipline-reviewer | ④ #139 제약 선언은 schema_in.py에(usecase-dto-placement 담당 — 자리 축만) + ① 상한 유무 판정은 감수자(architecture-api §5.1) |
| 221 | s007/b27 (L91–91) | 판정 기준의 상한 선언 유무 한정(구체 경계값 강요 금지) | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외 — 값은 필드·DB 타입 몫 |
| 222 | s007/b28 (L92–92) | 트리·배치·명명 값의 houserules final.md 단일 소유(이 문서에 값 미보유) | Obligation | D: agent-discipline-reviewer | ① 문면이 값 정본을 §0~§4로 위임(값 사본 금지) — 판정 주체는 감수자 |
| 223 | s007/b28 (L92–92) | ① 코드와 final.md의 직접 대조 | Obligation | E: check-layer-skeleton.py · D: agent-discipline-reviewer | ④ #486~#490 골격 백스톱(layer-skeleton 담당)이 존재·폐쇄 축을 커버 · ① 직접 대조는 감수자 |
| 224 | s007/b28 (L92–92) | 명세 부합만의 통과 금지 | Prohibition | D: agent-discipline-reviewer | ① 문면 금지 명문 — 감수자 판정 규율 |
| 225 | s007/b28 (L92–92) | 명세 자체의 §0 불변식·§2 골격·포트/칸 위치 위반 시 발견 상신(설계 반송) | Obligation | D: command-dddjango | ① 문면 «설계 반송» — 반송 라우팅 소유 Coordinator |
| 226 | s007/b28 (L92–92) | 레이아웃 대조 기준의 표준 트리 고정(기존 배치 일치는 통과 사유 아님) | Override | E: check-layer-skeleton.py · D: agent-discipline-reviewer | ① 문면 «소스 트리에 «기존 규약 존중» 케이스는 없다·기존 배치와의 일치는 통과 사유가 아니다»가 houserules §1.1 기존 규약 존중을 눌러 이기는 우선 규칙이라 class=Override(코퍼스 선례 implementation-django s015-2.5 «기존 배치는 입력이 아니다») + ② docstring «채택 저장소에서는 application/ 직계 전부가 BC» 고정 기준 |
| 227 | s007/b28 (L92–92) | 승인 test artifact의 기존 테스트 위치(§1.2) 예외 대조 | Exception | E: check-test-config.py · D: agent-discipline-reviewer | ④ #383~#392 test/ 구조(test-config 담당) + ① 승인 위치 예외 판정은 감수자 |
| 228 | s007/b28 (L92–92) | 대조 대상의 이번 diff(승인 스코프 산출물) 한정 | Obligation | D: agent-discipline-reviewer | ② 다수 검사기 docstring의 touched 한정 게이트와 동축 · 판정은 감수자 |
| 229 | s007/b28 (L92–92) | 범위 밖 legacy 잔존의 발견 불산입(빚 보고 채널·수리/이동 지시 금지) | Prohibition | D: command-dddjango | ① 문면이 빚 보고 채널(G0 ⓐ)을 지목 — 빚 채널 소유 Coordinator |
| 230 | s007/b28 (L92–92) | 승인 스코프 밖 기존 파일 이동·재배선 자체의 발견 판정(표준 트리 일치는 통과 사유 아님) | Obligation | D: command-dddjango | ① 문면 «설계 반송»(2026-08-13 라운드 2 실증) — 반송 라우팅 소유 |
| 231 | s007/b28 (L92–92) | ② 경로·AST 판정의 registry 백스톱 소유·재판정 금지(이중 계상 금지) | Prohibition | E: check-layer-skeleton.py · D: command-dddjango | ① 문면이 commands/dddjango.md registry 표를 소유자로 지목 — registry 실행 소유 Coordinator · ④ 트리 판정 대표 백스톱 layer-skeleton(#487 최우선 등록) |
| 232 | s007/b28 (L92–92) | 백스톱 exit 0의 의미 준수 증거 불인정 | Prohibition | D: agent-discipline-reviewer | ① 문면 «exit 0을 의미 준수의 증거로 읽지 않는다» — 사각 전담 선언 |
| 233 | s007/b28 (L92–92) | 형태 밖 의미 변종(개명 폴더·빈-정본 위장·변수 우회·간접 재수출·이름 위장 클래스·모듈/lazy 싱글톤 공유) 직독 | Obligation | D: agent-discipline-reviewer | ② check-composition-root docstring «형태로 못 가르므로 discipline-reviewer 의미 레인 몫» — 명시 위임 |
| 234 | s007/b28 (L92–92) | ③ 옛 이름 재등장의 트리 밖 칸 위반 판정(면제 불인정) | Prohibition | E: check-layer-skeleton.py · D: agent-discipline-reviewer | ④ 문면이 #81·#490을 인용 — 둘 다 layer-skeleton docstring 담당 규칙 |
| 235 | s007/b28 (L92–92) | ④ 주석·docstring 언어의 프로젝트 관례(없으면 한국어) 일치 확인 | Obligation | D: agent-discipline-reviewer | ① 문면 «기계 밖» 자인 + ④ 위임 기본값(discipline-houserules→discipline-reviewer) |
| 236 | s007/b28 (L92–92) | ⑤ 타입 규율의 기계 전면 소유와 감수자 몫 한정(ⓓ#69 후보·역방향 어노테이트 오류) | Obligation | E: check-public-surface-annotation.py · D: agent-discipline-reviewer | ① 문면이 check-public-surface-annotation을 직접 지목 + ② docstring #493 전면 집행·#69는 ⓓ 후보(마무리는 discipline-reviewer) |
| 237 | s007/b29 (L93–93) | known failure 집합의 ACL 전수 번역(raw 통과 시 blocker) | Obligation | E: check-synthetic-infra-exc.py · D: agent-discipline-reviewer | ② docstring ⑵ #129 «예외 번역은 알려진 구체 예외의 전수 명시 매핑» — 축자 동축 |
| 238 | s007/b29 (L93–93) | import 없는 propagation·helper·재수출 우회의 직독 | Obligation | D: agent-discipline-reviewer | ① 문면 «기계 밖이라 네가 직접 읽는다» — 사각 자인 |
| 239 | s007/b29 (L93–93) | 광범위 except Exception 요구 금지 | Prohibition | E: check-synthetic-infra-exc.py · D: agent-discipline-reviewer | ② docstring #129 catch-all 번역 금지와 같은 축(요구도 금지) |
| 240 | s007/b29 (L93–93) | ACL·upstream repository 안에서 승인 concrete로 소진된 실패의 누수 불인정 | Exception | D: agent-discipline-reviewer | ① 거짓지적 방지 예외 — 감수자 판정 |
| 241 | s007/b29 (L93–93) | raw DB/SDK/network unknown failure의 전수 집합 제외(safe framework 500 기본) | Exception | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ② controller-contract docstring raw 예외 provenance 제한 · b23과 동축 |
| 242 | s007/b30 (L94–95) | ⓓ 후보 줄의 출력 계약(경로: 사실 — 물음 · exit 불산입) | Obligation | D: command-dddjango | ① 문면이 검사기 출력 계약을 규정 + ④ 검사기 실행·출력 수납 소유 Coordinator(registry 표) |
| 243 | s007/b30 (L94–95) | ⓓ 후보 판정자의 단독 귀속(감수자) | Obligation | D: agent-discipline-reviewer | ① 문면 «이 줄의 판정자는 너 하나다» — 위임 대상의 명문 근거 |
| 244 | s007/b30 (L94–95) | 후보별 답변·발견(심각도·근거·규칙 번호) 또는 기각 사유 1줄 기재 | Obligation | D: agent-discipline-reviewer | ① 문면 형식 규정 — 판정자 소유 |
| 245 | s007/b30 (L94–95) | ⓓ 후보 무응답 금지 | Prohibition | D: agent-discipline-reviewer | ① 문면 «무응답 금지 — 후보를 흘리면 그 규칙은 판정자가 없다» |
| 246 | s007/b30 (L94–95) | 검사기 미방출 자리에도 동일 물음 적용(코드 직독 시 목록 사용) | Obligation | D: agent-discipline-reviewer | ① 문면 확대 적용 명문 — 사각 전담 |
| 247 | s007/b30 (L94–95) | 규칙 번호 정본성과 방출 검사기 매핑의 rule-owner-map 소유 | Obligation | D: command-dddjango | ① 문면이 매핑표(rule-owner-map)를 소유자로 지목 — registry·매핑표 소유 Coordinator |
| 248 | s007/b33 (L98–98) | ⓓ#181 멱등 물음(두 번 와도 결과가 같나) | Obligation | E: check-missable-entrance.py + check-broker-contract.py · D: agent-discipline-reviewer | ④ #181 담당=missable-entrance docstring(«멱등 물음의 소유자») · broker-contract가 #532에서 같은 물음 인용 — 후보 마무리는 감수자 |
| 249 | s007/b34 (L99–99) | ⓓ#595 이름 안정 물음(공급자·계기·수단이 바뀌어도 이름이 그대로인가) | Obligation | E: check-business-vocabulary.py + check-port-adapter-pairing.py + check-missable-entrance.py · D: agent-discipline-reviewer | ④ 병기 자 = 주 소유 + 쓰는-자리 방출자 전부(§4-⑦) — #595·#584=business-vocabulary · #594=port-adapter-pairing · #512=missable-entrance(docstring «#512 [ast+] webhook/<provider>/») · 후보 마무리는 감수자 |
| 250 | s007/b35 (L100–100) | ⓓ#553 업무 규칙 물음(Q2) | Obligation | E: check-port-adapter-pairing.py + check-business-vocabulary.py + check-naming.py · D: agent-discipline-reviewer | ④ 병기 자 = 주 소유 + 쓰는-자리 방출자 전부(§4-⑦) — #553·#475=port-adapter-pairing · #607=business-vocabulary(같은 술어 공유 docstring 명문) · #589=naming · #316은 담당 검사기 부재(grep 0)라 감수자 단독 |
| 251 | s007/b36 (L101–101) | ⓓ#565 단계 이름 물음(업무가 이 단계 이름을 입으로 부르나) | Obligation | E: check-domain-model.py + check-event-publish.py · D: agent-discipline-reviewer | ④ #565 담당=domain-model(도메인 Enum 값 ∩ 유스케이스 이름 후보) · #564 진행표 후보는 event-publish 소유(표의 쓰는 자리) |
| 252 | s007/b37 (L102–102) | ⓓ#590 문구 물음(이 값이 사람이 읽을 문구인가) | Obligation | E: check-naming.py + check-business-vocabulary.py · D: agent-discipline-reviewer | ④ #590 담당=naming(문구의 자리 — docstring #588·#589·#590) · #618 locale/채널 후보는 business-vocabulary가 #590 물음 소유로 인용 |
| 253 | s007/b38 (L103–103) | ⓓ#628 업무 어휘 물음(도메인 공개 심볼 토큰 집합) | Obligation | E: check-business-vocabulary.py · D: agent-discipline-reviewer | ④ docstring «업무 어휘의 정의(#628)는 business_vocab.py가 진다» — 재료 실체까지 문면 일치 |
| 254 | s007/b39 (L104–104) | ⓓ#11 손잡이 물음(연 쪽이 닫기까지 하나) | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ docstring «#11(경계 애너테이션의 Model/QuerySet은 확정, 그 외 후보)» — 후보 마무리는 감수자 |
| 255 | s007/b40 (L105–106) | ⓓ#355 주어 물음(애그리거트인가 화면인가) | Obligation | E: check-transaction-boundary.py · D: agent-discipline-reviewer | ④ docstring #355 [ast+] 확정/후보 분업 명문 — bool·int 잔여 후보의 판정은 감수자 |
| 256 | s007/b42 (L108–108) | ⓓ#82 BC 폴더 이름 물음(업무의 낱말인가·유사 변형 반송 후보) | Obligation | D: agent-discipline-reviewer | ④ #82 담당 검사기 부재(27종 전수 `#82` grep 0 — business-vocabulary도 미방출) · 재료 #628 토큰 소유는 집행이 아니라 재료 공급이라 enforcedBy 미병기(#492·#316과 동형) · 판정은 houserules §3 대조로 감수자 |
| 257 | s007/b42 (L108–108) | ⓓ#36 정도 낱말 칸 물음(예/아니오로 답하는 물음이 붙나) | Obligation | E: check-naming.py · D: agent-discipline-reviewer | ④ docstring #36 [ast+] 확정/후보 — naming 담당 |
| 258 | s007/b42 (L108–108) | ⓓ#17·#18 1차 축 이름 물음(Q1) | Obligation | E: check-domain-model.py · D: agent-discipline-reviewer | ④ #17/#18 담당=domain-model(naming은 «#17/#18(domain-model) 소유 — 중복 진단 금지» 명문) |
| 259 | s007/b43 (L109–109) | ⓓ#151 창구 이름 물음(무엇을 해 주는가를 말하나) | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ OHS 명명 규칙군(#482~#484 등) 담당=context-isolation · 후보 마무리는 감수자 |
| 260 | s007/b43 (L109–109) | ⓓ#153 계약↔응용 DTO 변환 물음 | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ ACL/OHS 축 담당=context-isolation(#12·#13·#152~#155) |
| 261 | s007/b43 (L109–109) | ⓓ#171 예외 이름 분기 가능성 물음 | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ docstring «#171(접미사뿐인 예외 이름)» 후보 — context-isolation 담당 |
| 262 | s007/b43 (L109–109) | ⓓ#347 사용자 API 동시 수행 물음(admin feature) | Obligation | E: check-context-isolation.py · D: agent-discipline-reviewer | ④ docstring «#347(admin feature의 …)» 후보 방출 — context-isolation 담당 |
| 263 | s007/b44 (L110–110) | ⓓ#68 검사 값의 출처 물음(Q2) | Obligation | E: check-usecase-dto-placement.py · D: agent-discipline-reviewer | ④ #68 담당=usecase-dto-placement(검증 자리 규칙군 #139·#183과 같은 판) |
| 264 | s007/b44 (L110–110) | ⓓ#103 되돌려 굽기 여부 물음 | Obligation | E: check-usecase-dto-placement.py · D: agent-discipline-reviewer | ④ #103 담당=usecase-dto-placement |
| 265 | s007/b44 (L110–110) | ⓓ#140 검증 위치 이탈 물음(Q2) | Obligation | E: check-usecase-dto-placement.py · D: agent-discipline-reviewer | ④ #140 담당=usecase-dto-placement(#183 validation 금지와 동축) |
| 266 | s007/b44 (L110–110) | ⓓ#191 판정이 되는 물음 이름(Q1) | Obligation | E: check-usecase-dto-placement.py · D: agent-discipline-reviewer | ④ #191 담당=usecase-dto-placement |
| 267 | s007/b44 (L110–110) | ⓓ#194 판정 주인이 유스케이스인가(Q2) | Obligation | E: check-usecase-dto-placement.py · D: agent-discipline-reviewer | ④ #194 담당=usecase-dto-placement |
| 268 | s007/b44 (L110–110) | ⓓ#69 런타임 검사 대신 테스트·타입 체커 몫 물음 | Obligation | E: check-public-surface-annotation.py · D: agent-discipline-reviewer | ④ docstring «#69 (ast+ · ⓓ 후보) … 마무리는 discipline-reviewer» — 축자 위임 |
| 269 | s007/b45 (L111–111) | ⓓ#86 분기가 업무를 가르는가 물음(유스케이스 강등) | Obligation | E: check-composition-root.py · D: agent-discipline-reviewer | ④ docstring «#85/#86(ⓓ) dependency_wiring.py는 build_* 팩토리만 · 조건/계산은 후보» |
| 270 | s007/b45 (L111–111) | ⓓ#511 입구 계약의 외부 소유 물음(OAuth 콜백=webhook 자리) | Obligation | E: check-composition-root.py · D: agent-discipline-reviewer | ④ docstring «#511(ⓓ) api/ 2차 축 — 계약 소유 … 후보» |
| 271 | s007/b45 (L111–111) | ⓓ#125 입구가 변환·1회 호출을 넘는 로직 보유 물음 | Obligation | E: check-api-error-controller-contract.py · D: agent-discipline-reviewer | ④ docstring «ⓓ#125는 route 함수 def 행 좌표» — controller-contract가 방출 소유 |
| 272 | s007/b46 (L112–112) | ⓓ#257 루트 메서드 뒤 불변식 물음(Q4) | Obligation | E: check-domain-model.py · D: agent-discipline-reviewer | ④ docstring «#257 [ast+] … 후보: 끝에 불변식 확인 없는 루트 메서드(Q4)» |
| 273 | s007/b46 (L112–112) | ⓓ#259 값인가 엔티티인가 물음(Q4) | Obligation | E: check-domain-model.py · D: agent-discipline-reviewer | ④ docstring «#259 [ast+] … 후보: id를 가진 value_object» |
| 274 | s007/b46 (L112–112) | ⓓ#268 타입 조합만으로 잘못된 값이 불가능한가(Q2) | Obligation | E: check-domain-model.py · D: agent-discipline-reviewer | ④ #268 담당=domain-model(값 객체 축) |
| 275 | s007/b46 (L112–112) | ⓓ#301 «없을 때» 판정의 루트 메서드 표현 가능성 | Obligation | E: check-domain-model.py · D: agent-discipline-reviewer | ④ #301 담당=domain-model |
| 276 | s007/b46 (L112–112) | ⓓ#311 이름이 규칙 행위를 말하나 | Obligation | E: check-domain-model.py · D: agent-discipline-reviewer | ④ #311 담당=domain-model |
| 277 | s007/b46 (L112–112) | ⓓ#547 동시 발생 차단·두 사용자 충돌 물음(Q4) | Obligation | E: check-domain-model.py · D: agent-discipline-reviewer | ④ #546/#547 담당=domain-model(«너무 갈린 쪽»만 기계) — 반대편은 s007 human 판정 #254 |
| 278 | s007/b47 (L113–113) | ⓓ#271 이름이 이미 일어난 사실을 말하나 | Obligation | E: check-event-publish.py · D: agent-discipline-reviewer | ④ docstring «#271 [ast+] 사실 이름은 과거형 — 확정/후보» |
| 279 | s007/b47 (L113–113) | ⓓ#564 패턴이 아니라 진행표인가(단계 물음) | Obligation | E: check-event-publish.py · D: agent-discipline-reviewer | ④ docstring «#564 [ast+] 진행표 금지 — 후보» |
| 280 | s007/b48 (L114–114) | ⓓ#285 수가 애그리거트 컬렉션을 세거나 합친 것인가 | Obligation | E: check-transaction-boundary.py · D: agent-discipline-reviewer | ④ docstring «#285 [ast+] … bypass query 포트의 bool/int 반환 메서드는 ⓓ 후보» |
| 281 | s007/b49 (L115–115) | ⓓ#520 사실이 안 나가면 내가 할 일이 있나 | Obligation | E: check-broker-contract.py · D: agent-discipline-reviewer | ④ docstring «#520 [ast+] … passive-aggressive command 후보» |
| 282 | s007/b49 (L115–115) | ⓓ#529 듣는 쪽이 따로 배포되나 | Obligation | E: check-broker-contract.py · D: agent-discipline-reviewer | ④ docstring «#529 [ast+] external을 가르는 물음» |
| 283 | s007/b49 (L115–115) | ⓓ#532 받는 쪽이 안 왔을 때·두 번 왔을 때를 메우나 | Obligation | E: check-broker-contract.py · D: agent-discipline-reviewer | ④ 실방출 문면 일치(«받는 쪽이 「안 왔을 때」와 「두 번 왔을 때」를 메우고 있나(#181·#629)») |
| 284 | s007/b50 (L116–116) | ⓓ#451 창구가 혼자서 답을 만들 수 있나 | Obligation | E: check-missable-entrance.py · D: agent-discipline-reviewer | ④ docstring «#451 [ast+] … 후보: OHS 서비스가 if 분기에서 계약 예외를 raise» |
| 285 | s007/b50 (L116–116) | ⓓ#512 보내는 쪽 문서가 자기를 이 이름으로 부르나 | Obligation | E: check-missable-entrance.py · D: agent-discipline-reviewer | ④ docstring «#512 [ast+] webhook/<provider>/ … 확정/후보» |
| 286 | s007/b50 (L116–116) | ⓓ#629 이 입구가 안 와도 업무가 돌아가나 | Obligation | E: check-missable-entrance.py · D: agent-discipline-reviewer | ④ docstring «#629 [ast+] 후보(집합 차)» — missable-entrance 담당 |
| 287 | s007/b51 (L117–117) | ⓓ#343 운영 기능인가 장고 배선인가 | Obligation | E: check-naming.py · D: agent-discipline-reviewer | ④ docstring «#343은 admin 가족이라 keyword 오배정을 이관받았다»(transaction-boundary가 이관 명문) |
| 288 | s007/b51 (L117–117) | ⓓ#589 조건이 업무 판정인가(Q2) | Obligation | E: check-naming.py · D: agent-discipline-reviewer | ④ #589 담당=naming(#588·#589·#590 문구의 자리 블록) |
| 289 | s007/b52 (L118–118) | ⓓ#227 자료를 원시값 인자로 펴서 넘길 수 있나 | Obligation | E: check-port-adapter-pairing.py · D: agent-discipline-reviewer | ④ docstring «#227[ast+] 자료는 원시값으로 안 될 때만(후보)» |
| 290 | s007/b52 (L118–118) | ⓓ#233 무엇을 알고 싶은가가 이름에 있나(Q1) | Obligation | E: check-port-adapter-pairing.py · D: agent-discipline-reviewer | ④ docstring «#233[ast+] 「무엇을 알고 싶은가」(확정: 기술·BC 토큰)» |
| 291 | s007/b52 (L118–118) | ⓓ#368 기계인가 값인가 | Obligation | E: check-port-adapter-pairing.py · D: agent-discipline-reviewer | ④ #368 담당=port-adapter-pairing |
| 292 | s007/b52 (L118–118) | ⓓ#475 이 판정이 업무 규칙인가(Q2) | Obligation | E: check-port-adapter-pairing.py · D: agent-discipline-reviewer | ④ docstring «#475[ast+] 날것으로 업무 판정(후보)» |
| 293 | s007/b52 (L118–118) | ⓓ#485 이름이 무엇을 시키는지 말하나 | Obligation | E: check-port-adapter-pairing.py · D: agent-discipline-reviewer | ④ docstring «#485[ast+] 메서드는 의도(확정: notify·handle·execute… / 후보: 동사 아님)» |
| 294 | s007/b53 (L119–119) | ⓓ#425 재료의 뜻을 밖(HTTP·pytest·시간)이 정하나 | Obligation | E: check-business-vocabulary.py · D: agent-discipline-reviewer | ④ #425 담당=business-vocabulary(#628 물음의 쓰는 자리로 문면 명시) |
| 295 | s007/b53 (L119–119) | ⓓ#448 낱말의 뜻을 저장소 밖이 정하나 | Obligation | E: check-business-vocabulary.py · D: agent-discipline-reviewer | ④ #448 담당=business-vocabulary |
| 296 | s007/b53 (L119–119) | ⓓ#607 조건이 업무 규칙인가(Q2) | Obligation | E: check-business-vocabulary.py · D: agent-discipline-reviewer | ④ docstring «#607 [ast+] 업무 판정 후보(Q2 — #553 술어 공유)» |
| 297 | s007/b53 (L119–119) | ⓓ#619 이것이 원시값 하나로 되나 | Obligation | E: check-business-vocabulary.py · D: agent-discipline-reviewer | ④ docstring «#619 [ast+] 원시값 하나로 되는 자료 클래스 후보» |
| 298 | s007/b54 (L120–120) | ⓓ#492 정본 문서 행이 «있어야 하나»인가 «어떻게 쓰나»인가 | Obligation | D: agent-discipline-reviewer | ④ #492 담당 검사기 부재(27종 전수 grep 0 — 주어가 코드가 아니라 정본 문서) · ⓓ 판정자 단독 귀속 문면 |
| 299 | s007/b55 (L121–121) | human 판정 #254 — 너무 묶인 애그리거트 경계의 가짜 불변식 발견(설계 반송) | Obligation | D: agent-discipline-reviewer | ① 문면 «검사기가 아예 없다(전적으로 네 몫)» + ④ #254 담당 검사기 부재(27종 전수 grep 0) — 반대편 #546·#547(domain-model)은 다른 규칙이라 병기하지 않는다(§16 역도 성립은 «담당» 검사기 도피 금지이지 반대편 병기 요구가 아님 · #547 docstring 실물 방향 불일치는 빚 채널 상신) |
| 300 | s007/b55 (L121–121) | human 판정 #316 — 재료 미수집 시에도 규칙 불해체(도메인→응용 조회→도메인 분절 직독) | Obligation | D: agent-discipline-reviewer | ① 문면 «검사기가 아예 없다» + ④ #316 담당 검사기 부재(27종 전수 grep 0) |
| 301 | s007/b56 (L122–123) | 면제 조문 16종의 문면 정본 위임 | Obligation | D: command-dddjango | ① 문면 «문면은 정본 명세 소유» — 규칙 번호 정본 소유 Coordinator(registry·rule-owner-map 축) |
| 302 | s007/b56 (L122–123) | 면제 조문 번호로 새 검사·새 의무 신설 금지 | Prohibition | D: agent-discipline-reviewer | ① 문면 금지 명문 — 감수자 자기 판정 규율 |
| 303 | s007/b56 (L122–123) | 면제에 정확히 드는 후보·발견의 번호 인용 기각 | Obligation | D: agent-discipline-reviewer | ① 문면 형식 규정 — ⓓ 판정자 소유 |
| 304 | s007/b57 (L124–125) | 로드 스킬 4종(cleancode·tdd·implementation-test·houserules) 절의 근거 인용 | Obligation | D: agent-discipline-reviewer | ① 문면 인용 의무 + ④ 위임 기본값 표(discipline-*·implementation-*→discipline-reviewer) |
| 305 | s008/b1 (L127–128) | 코드·테스트 수정 금지(읽기 전용) | Prohibition | D: command-dddjango | ④ 위임 기본값 표(command+agents 절차 층) — 역할 경계 위반 판정은 Coordinator |
| 306 | s008/b1 (L127–128) | 반영 주체의 코더 귀속 | Obligation | D: command-dddjango | ① 문면이 coder를 반영 주체로 지목 + ④ 역할 라우팅 소유 Coordinator |
| 307 | s008/b2 (L129–129) | 기술 특화 구현 정확성 비판정(규율 렌즈 한정) | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 렌즈 경계 위반(월권)은 리포트 수납 주체가 판정 |
| 308 | s008/b2 (L129–129) | 구현 정확성=coder·implementation-*, 명세 부합=설계·인수 테스트의 소유 배분 | Obligation | D: agent-coder + agent-design-architect + agent-acceptance-tester | ① 문면 «…가 책임진다»는 판정 소유 배분 선언(감수자 행위 지시 없음) — P-C 판별자 ⑵로 지목 Agent 3종에 위임(implementation-* 스킬은 registry Agent 8종 밖이라 배선 제외) · s008/b2 n9와 같은 자 |
| 309 | s008/b2 (L129–129) | 구조 규율·책임 배치 규율·메커니즘-소유권 규율의 관찰 유지 | Obligation | D: agent-discipline-reviewer | ① 문면 «보되» — 감수자 렌즈 포함 선언(s007 b12·b14와 짝) |
| 310 | s008/b2 (L129–129) | 기술 구현 정확성(쿼리·ORM 관용구) 비관찰 | Prohibition | D: agent-discipline-reviewer | ① 문면 «여전히 보지 않는다» — 감수자 렌즈 배제 선언 |
| 311 | s008/b2 (L129–129) | 메커니즘-소유권의 소유권 축 한정(기술 정확성 판정 아님) | Obligation | D: agent-discipline-reviewer | ① 문면이 소유권/정확성을 명시 구분 — 감수자 렌즈 한정 |
| 312 | s008/b2 (L129–129) | API 오류의 direct mapping·physical placement·forbidden extraction/circumvention·scope completeness 관찰 유지 | Obligation | D: agent-discipline-reviewer | ① 문면 «보되» — s006 소유 경계와 동축 |
| 313 | s008/b2 (L129–129) | public wire code·HTTP semantics·compatibility·ninja 기술 정확성의 타 소유(API reviewer·coder·implementation-*) | Prohibition | D: agent-design-review-api | ① 문면이 API reviewer 소유를 지목 — 기본값 이탈의 문면 근거 |
| 314 | s008/b2 (L129–129) | Risky Write 동시성 기준 실현(TDD 커버리지) 관찰 유지 | Obligation | D: agent-discipline-reviewer | ① 문면 «보되» — s007 b8과 짝 |
| 315 | s008/b2 (L129–129) | 동시성 시나리오 적정성·기술 정확성 비관찰(명세·acceptance-tester / coder·implementation-*) | Prohibition | D: agent-acceptance-tester + agent-coder | ① 문면이 전자=명세·acceptance-tester, 후자=코더·implementation-*로 소유 지목 |
| 316 | s008/b3 (L130–130) | 스코프 확대 권고 금지 | Prohibition | D: command-dddjango | ④ 절차 층 기본값 — 스코프 소유 Coordinator(G0/G1) |
| 317 | s008/b3 (L130–130) | 스코프 의문의 발견 상신 한정 | Obligation | D: command-dddjango | ④ 절차 층 기본값 — 발견 수납·스코프 결정 소유 Coordinator |

## 3. 재진술 유예 (교차 문서 — spec 미기입·소급 패스 대상)

브리프 §spec 작성 규칙에 따라 **다른 문서 상대는 spec `restates`에 넣지 않았다**. 아래는 census restate 열을 단서로 상대 문서를 직접 실독해 좌표를 확정한 유예 목록이다(전 웨이브 완료 후 소급 패스가 연결).

| # | 이 문서 사본 블록 | 문면 요지 | 상대 문서/절(확인한 원문 행) | 관계 |
|---|---|---|---|---|
| R1 | s002/b2 (L18 말미) | 집행성 판정 1행 — «가능»이면 확정 결정 3곳 인용·인용 없는 «가능»은 무효 | `agent-design-review-db`/s003 (L25) · `agent-design-review-api`/s004 (L41) | 동형 4중(P0 특이 발견 6-ⓕ) — 정본 후보는 리뷰어 3종 공통 문면. 이 문서는 lens 한정어(«규율 lens 범위 한정 · 입장 표·구조 결정이 대상»)만 다름 |
| R2 | s003/b2·b3 (L36–37) | 발견/권고 항목 형식 + 심각도 3단계 | `agent-design-review-db`/s003 (L20–21) · `agent-design-review-api`/s004 (L36–37) | 축자 근접 사본(근거 표기만 «파일:라인» ↔ «명세 절 제목·인용») |
| R3 | s003/b5 (L41) | RESOLVED 확인 토큰 발행 3조건·미발행 조건 | `agent-design-review-api`/s004 (L38–41 `DYNAMIC_ERROR_SHAPE_PROOF_REVIEW` 토큰 절) | 대칭 이중 확인(둘 다 있어야 해소) — 사본이 아니라 «대칭 쌍»이라 소급 패스에서 restates 여부 재판단 필요 |
| R4 | s005/b6 (L54) | 첫-Green 비계 즉시 제거·기존 비계 임의 삭제 금지 | `agent-coder`/s004 (L45) · `command-dddjango`/s007 (L91 step 4) | 4중 사본(P0 특이 발견 6-ⓐ. acceptance-tester 판 포함) — 감사 측/실행 측 문면 |
| R5 | s006/b1 (L58) | 12-slot ↔ project-wide production tree/inventory 대조 | `command-dddjango`/s007 (Phase 2) · 입력 준비는 `command-dddjango`/s006 (L78 «discipline 에 줄 project-wide tree·inventory 를 먼저 구성해 동봉») | census는 s007 지목 — 실독 결과 **입력 준비 문면은 s006에도 있어 둘 다 후보**. 소급 패스에서 정본 절 확정 필요 |
| R6 | s007/b14 (L78) | 메커니즘-소유권 — 레드 플래그 열거·출처 불문 동일 위반 | `agent-coder`/s006 (L69, 경계) | 감사 측 ↔ 실행 측 쌍(P0: coder 경계 = registry #1 `check-mechanism-ownership.py` 대응) — 열거 목록이 축자 근접 |
| R7 | s007/b22 (L86) | 배선·등록은 profile 무관 표준 · preserve가 보존하는 것은 오류 wire 산출물이지 배선이 아님 | `agent-coder`/s004 (L49·L53) · `command-dddjango`(registry #16 행 L123) · `agent-design-architect` | 4중 사본(P0 특이 발견 6-ⓓ) — 날짜 스탬프 «2026-08-12 라운드 1′»가 사본 표지 |
| R8 | s007/b12·b13 (L76–77) | 판정 소유→구조 이주 · 값 집합 단일 출처(domain enum) | `agent-design-review-ddd`/s004 (점검 항목 — 설계 시점 빈혈 차단) | 시점 분업 쌍(설계/구현) — 같은 규범의 두 시점 판(P0 E10 비고 명시) |
| R9 | s008/b3 (L130) | 스코프 확대 권고 금지 — 의문은 발견으로만 | `agent-design-review-api`/s007 (L84) · `agent-design-review-db`/s005 (L44) | 축자 동일 문장(3중) |

**같은 문서 안 쌍은 0건으로 판정**(spec `restates` 미사용). 근거는 §4-⑤(최초 후보 2쌍) + §4-⑤′(적대 리뷰 F4로 추가 심의한 2쌍 — 둘 다 기각·2026-08-22). 심의한 후보 총 4쌍, 채택 0.

## 4. 경계 판단 메모

① **절 스팬 소유(§13) 적용**: 8절 전부 «헤딩 다음 행부터»가 첫 블록 시작이고 헤딩 직후 빈 줄은 첫 블록 선두에 귀속했다. 블록 간 빈 줄은 선행 블록 후행 스팬 귀속 — 절 말미 빈 줄(L13·L31·L42·L46·L55·L62·L125)도 마지막 블록이 물었다. 도구의 «헤딩+블록 연결 = 절 스팬» 단언이 8절 모두 통과(byte 등가).

② **(전문) 절의 frontmatter 취급**: L2–10(YAML)을 kind=norm 한 블록으로 묶고 description 3문만 Work로 올렸다. `tools:`/`skills:` 목록은 문장이 아닌 기계 설정 값이라 계수하지 않았다(E10-recon §1 규약과 동일). L1(`---`)은 헤딩 라인 자리라 headingSnapshot 소유 — 이 문서는 무앵커 문서라 절 키가 s001이고 «헤딩»이 `---`인 유일 케이스다.

③ **ⓓ 물음 표(L96–105)의 kind**: §13 «표 머리행·구분행도 kind=table-row» 그대로 머리행(L96)·구분행(L97)을 각각 별도 table-row 블록으로 뒀고 Work 0. 데이터 8행은 행마다 블록 1 + Work 1(발주서 비고 «표 8행=구속 운반체» 준수). 데이터 행이 규범을 지는 표라 kind=table-row + norms 병기가 성립한다(datatype은 도구가 xsd:string으로 — §16 kind↔datatype 정합).

④ **열거를 접은 자리 / 편 자리의 자**: 접음 = 한 의무 동사의 목적어 열거이고 소유자·판정 기준이 같을 때(s003 반송처 4종, s007/b21 사각 (a)~(g), s007/b26 레드 플래그 (a)~(d), s005 decision별 편집 허용 범위). 폄 = 항목이 독자 행을 차지하거나(§s002 L21–26) 항목마다 #N 소유자·방출 검사기가 갈릴 때(ⓓ 물음 43문). 이 자는 파일럿 두 판형(ninja 상태코드 13불릿=Work 0 ↔ ninja L563–565 3행=Work 3, L-G 중재)에서 그대로 끌어왔다.

⑤ **같은 문서 안 재진술을 0으로 판정한 근거**: 후보는 ⑴ s001 description «코드를 직접 수정하지 않는다» ↔ s003 «코드를 직접 고치지 않는다» ⑵ s006/b4 리뷰 소유권 경계 ↔ s008/b2 소유권/정확성 구분. 둘 다 **축자 사본이 아니고**(어휘·범위가 다름), 특히 ⑵는 s008 블록이 9 Work를 지는 복합 경계 선언이라 블록 단위 `djr:restates`를 걸면 나머지 8 Work가 정본을 잃는다(§15 «정본 1곳만 Work 승격»의 부작용). 따라서 restates 미기입 + 이 메모로 남긴다 — 소급 패스에서 «부분 중첩 사본»의 처리 규약이 서면 재검토 대상.

**⑤′ 후보 2쌍 추가 심의(적대 리뷰 F4 수리 — 2026-08-22)**: 최초 심의가 후보 수집을 덜 했다. 아래 두 쌍을 추가로 심의하고 **둘 다 기각**(restates 미기입)한다 — 기각 사유는 «축자성 불성립 + 블록 다중 Work 정본 상실» 두 축이고, ⑤ 본문과 같은 자다.
- **ⓐ s003/b1(L34) «코드를 직접 고치지 않는다» ↔ s008/b1(L128) «코드·테스트를 수정하지 않는다(읽기 전용). 반영은 코더가 한다» ↔ s001 desc(L3) «코드를 직접 수정하지 않는다»** — 같은 금지가 3곳에서 각자 Work로 섰다(§15 «정본 1곳만 Work 승격»과 긴장). 그러나 ⑴ 셋의 술어·범위가 다르다(고치다/수정하다 · 코드 ↔ 코드+테스트 · s008만 «읽기 전용» 자격과 «반영 주체» 보충을 지님 — 축자 사본 불성립) ⑵ `djr:restates`는 **블록 단위**라 s003/b1(6 Work)·s008/b1(2 Work)·s001/b1(3 Work) 어디에 걸어도 나머지 Work가 정본을 잃는다. **기각 — 문장 단위 restates 규약이 서면 재검토**(F10 수리로 s003 label의 «반영은 코더» 혼입은 걷어 세 문면의 경계는 선명해졌다).
- **ⓑ s002/b11(L28) «HTTP 의미론·public code의 적정성·호환성은 API reviewer 소유이므로 중복 판정하지 않는다» ↔ s006/b4(L61) «API reviewer는 wire meaning·public code catalog 판단·HTTP semantics·compatibility를 소유하므로 여기서 public-code 적정성을 중복 판정하지 않는다»** — 근접 사본이나 ⑴ 적용 모드가 다르고(전자=DYNAMIC 모드 한정 · 후자=Phase 1·2 API 오류 scope) ⑵ 열거 집합이 다르다(전자 3항 · 후자 4항 + 소유 5종 선언 동반) ⑶ 두 블록 모두 다중 Work(3·3). **기각 — 같은 규범의 «모드별 재선언»이지 사본이 아니다.** 소급 패스가 문장 단위 restates를 도입하면 ⓐ와 함께 1순위 후보로 올린다.

⑥ **ⓓ 물음의 배선 형상(가장 어려웠던 판단)**: 문면은 «후보는 exit 불산입 — 아직 위반이 아니다»라 검사기가 *집행*하지 않는다. 그러나 §16의 «역도 성립»(담당 검사기의 문면·docstring 근거가 있는데 기본값으로 도피하면 오배선) 때문에 기본값 단독 배선은 오배선이다. 그래서 **enforcedBy = 그 #N을 담당·방출하는 검사기(확정 몫) + delegatedTo = agent-discipline-reviewer(후보 마무리)** 이중 배선으로 갔다. 27종 전 파일 #N grep으로 소유자를 확정했고, 담당 검사기가 **0건인 물음은 delegatedTo 단독**이다 — #82·#492 · human 판정 #316·#254 **4종**(2026-08-22 수리 전 표기는 «3종»이었고 #82에 business-vocabulary, #254에 domain-model을 병기해 자기 basis와 모순이었다 — 적대 리뷰 F1·F7 인용).
  - **#82 수리(F1)**: 27종 전수 `#82` grep 0. business-vocabulary가 소유하는 것은 «재료»인 #628 토큰 집합이지 #82 규칙이 아니고, 재료 공급은 집행이 아니다 → enforcedBy 철회.
  - **#254 수리(F7)**: §16 «역도 성립»은 «**담당** 검사기의 근거가 있는데 기본값으로 도피하면 오배선»이지 «반대편 검사기를 병기하라»가 아니다. #546·#547은 별개 규칙(문면 스스로 «기계 반대편»이라 자인)이라 병기 근거가 못 된다 → enforcedBy 철회.
  - **원문 결함 후보(빚 채널 상신 — 원문 수정 금지라 기록만)**: 원문 L121은 «기계(#546·#547)는 «너무 갈린 쪽»만 본다»고 하나, `check-domain-model.py` #547 docstring 실물은 «루트가 비대(엔티티 3+·컬렉션 필드) … 경계를 쪼갠다»로 **묶인 쪽**을 후보로 낸다 — 문면과 검사기 방향이 어긋난다. T3 이관은 문면대로 옮기고, 실물 대조 결과를 빚 항목으로 올린다.

⑦ **다중 소유 #N 처리**: #17·#18(naming docstring이 «domain-model 소유 — 중복 진단 금지» 명문 → domain-model 단독), #181(missable-entrance가 «멱등 물음의 소유자» → 주 소유 + broker-contract 병기), #343(transaction-boundary가 «check-naming 이관» 명문 → naming), #590(business-vocabulary가 «후보 물음은 #590 소유» → naming 주 소유 + 병기), #553/#595(두 검사기가 술어 공유·둘 다 실방출 → 병기), #628(business_vocab.py가 정의 소유 → business-vocabulary).

**⑦′ 병기 자의 단일화(적대 리뷰 F9 수리 — 2026-08-22)**: ⓓ 물음 표 8행의 병기 기준이 행마다 흔들렸다(#181은 쓰는-자리 방출자 broker-contract를 병기했는데 #595는 #512 방출자, #553은 #589 방출자를 빠뜨림). **자를 «주 소유 + 그 행 «쓰는 자리»에 열거된 #N의 방출 검사기 전부»로 고정**하고 8행에 재적용했다. 재적용 결과(27종 `#N` grep 재확인):
  - #181 → missable-entrance(주) + broker-contract(#532·#603) ✔ 기존 유지 · #565 → domain-model(주) + event-publish(#564) ✔ · #590 → naming(주) + business-vocabulary(#618) ✔ · #628 → business-vocabulary(#425·#448·#47·#617 전부 자기 소유) ✔ · #11 → context-isolation(쓰는 자리 #11 하나) ✔ · #355 → transaction-boundary(#355·#285 둘 다 자기 소유) ✔
  - **#595 → +check-missable-entrance.py**(쓰는 자리 #512 방출자) · **#553 → +check-naming.py**(쓰는 자리 #589 방출자) — 2행 수정. #553의 쓰는 자리 #316은 담당 검사기 0(grep 0)이라 병기 대상이 없고 감수자 단독이다.
  - 반대 자(«주 소유 단독»)를 택하지 않은 이유: 표의 «쓰는 자리» 열이 곧 그 물음이 실제로 방출되는 좌표라 방출자를 빼면 후보 줄과 규범 사이의 조인이 끊긴다(⑥의 이중 배선 취지와 같은 자).

⑧ **파일트리 불릿(L92) ②의 배선**: «경로·AST 판정은 registry 백스톱이 소유»의 소유자는 문면상 `commands/dddjango.md`의 registry 표라 delegatedTo=command-dddjango로 두고, 대표 백스톱으로 `check-layer-skeleton.py`(#487 «다른 모든 검사보다 먼저 돌고 걸리면 나머지를 돌리지 않는다»)를 enforcedBy에 병기했다. 27종 전부를 나열하는 배선은 registry 표의 사본이 되어 «값 사본은 썩는다»(같은 불릿의 자기 규범)를 어긴다고 판단.

⑨ **P-A/P-B 경계에서 흔들린 3건**: s005/b3-3(입장 행 없는 테스트 의무화 금지)·s005/b5-4(recipe로 입장 결정 신설 금지)·s007/b8-6(입장 누락 반송)은 대상이 «리뷰어 자신의 산출»이라 P-A(Coordinator)로 보냈다 — 판정 대상이 코드가 아니라 리포트·반송이기 때문. 반대로 s007/b9-3(FC-2 그레이더 소유·정적 신호 한정)은 그레이더가 registry 밖 개체(Agent 8종에 없음)라 감수자 자기 렌즈 한정 규범으로 보고 P-B에 뒀다.

⑩ **s002 b11-3 / s006 b4-2 / s008 b2-2·7·9의 기본값 이탈**: 문면이 소유자를 «API reviewer 소유이므로 중복 판정하지 않는다»·«구현 정확성은 코더와 implementation-* 스킬이 … 책임진다»로 **명시**해 §16 «기본값 이탈은 문면 근거 필요»를 충족한다. implementation-* 스킬은 registry Agent 8종에 없는 개체라 배선 대상에서 빼고 근거 문자열에만 남겼다. **2026-08-22 수리(F3)**: 같은 «타 역할 지목» 문형이 갈래 없이 두 방식으로 갈려 있었다 — §0 P-C에 판별자 ⒤(표시·라우팅 의무=절차→Coordinator) / ⑵(판정 소유 배분·중복 판정 배제 선언=지목 Agent)를 명문화하고 **s006 b4-3 → command-dddjango**, **s008 b2-2 → agent-coder+agent-design-architect+agent-acceptance-tester**로 재배선했다(s003 b1-3·b1-4와 s008 b2-9는 판별자 적용 결과 기존 배선 그대로).

⑪ **Override class 심의(적대 리뷰 F12 수리 — 2026-08-22)**: 최초 저작은 Override 0건이었고 검토 흔적도 없었다. 코퍼스 선례(`implementation-django-final` s015-2.5 «기존 배치는 입력이 아니다 — 규약이 아니라 빚» · s019-3.1 «배경 강등» · `architecture-ddd-final` s042-6.1 «권위 이양» · `discipline-cleancode-final` s092-12.2 «…는 예외가 아니라 답»)를 자로 삼아 **판단 기준**을 세우고 후보 5건을 심의했다.
  - **기준**: Override = 그 **Work 문장 자체가** 다른 규범·권위·기성 관행을 눌러 이기거나 권위를 이양하는 조항일 때. 호스트 의무·금지 문장에 **붙은 예외 배제 괄호**는 호스트 class를 유지한다(별도 Work 승격은 문장 해상도 규약상 독립 문장일 때만 — §13).
  - **채택 2건(Obligation→Override)**: ⑴ s007/b22 «preserve-established scope의 registration/composition 표준 대조»(L86) — 문장 자체가 preserve 보존 원칙을 배선 축에서 무효화하고 구 문구 철회를 명문화한다. ⑵ s007/b28 «레이아웃 대조 기준의 표준 트리 고정»(L92) — houserules §1.1 «기존 확립 규약 존중»을 눌러 이기는 우선 규칙(선례 s015-2.5와 동형).
  - **비채택 3건(class 유지 + 사유)**: ⓐ s007/b7-6 «Django TestCase 회귀 금지(관례 존중 예외 없음)»(L71) — 주 명제가 금지이고 괄호는 그 금지의 범위 확인이라 Prohibition 유지. ⓑ s007/b28-3 «명세 부합만의 통과 금지»·b28-4 «명세 위반 시 발견 상신»(L92) — «명세 정당화는 면제 사유가 아니다»는 상신 의무의 부수 절이라 Prohibition/Obligation 유지. ⓒ s006/b3-3 «격리 범위의 한정»(L60) — 범위 한정이지 우선 선언이 아니라 Obligation 유지(같은 취지의 우선 선언은 L86 쪽이 진다 — 이중 계상 회피).
  - class 조정은 **계수 무영향**(Work 317·블록 90 불변).

⑫ **enforcedBy 철회 9건의 단일 자(적대 리뷰 F1·F5~F8·F11 수리 — 2026-08-22)**: §16 ②는 «검사기 docstring의 § 인용»이지 «주제가 겹치는 검사기의 병기»가 아니다. 아래 세 형태를 **집행 아님**으로 확정하고 delegatedTo 단독으로 내렸다(무소유 0 유지).
  - **㈎ 인접 관할의 승격**: 검사기가 규범의 어느 형태도 검출하지 못하는데 동기·주제가 닿는다는 이유로 병기한 것 — s007/b22-9 406/415(ninja-boundary-middleware는 `settings.MIDDLEWARE` 자가등록 한 형태만 본다 · F5), s007/b12-5 평면 ORM 부착(domain-model #249·#256은 **이주 목적지** domain_layer 안 골격만 본다 — 위반 현장은 그 밖 · F6), s007/b7-1 pytest 관용구(test-config 3슬라이스 어디에도 «관용구 형태»가 없다 · F11), s007/b42 ⓓ#82(재료 소유 ≠ 규칙 소유 · F1), s007/b55-1 human #254(반대편 규칙 · F7).
  - **㈏ 분석 불능 자인 자리의 대체 증거**: DYNAMIC 모드는 검사기가 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`로 **분석 불능을 자인한** 뒤 열리는 경로다. 그 자리의 «증거 수령» 의무에 같은 검사기를 다는 것은 «증거 대상 = 검사기 분석 대상»이라는 **대상 사상**이지 집행이 아니다 — s002/b8·b9·b10(증거 4·5·6)·s003/b5-5(별도 승인 동일성 검증) 4건 철회(F8). 이 취급 규약(«집행 아님 · 대상 사상»)은 소급 패스에 상신 대상으로 남긴다.
  - **㈐ 반대 방향(추가 3건)**: 같은 자를 반대로 적용해 **빠진 발행자·방출자**는 채웠다 — s002/b4 DYNAMIC 발동 조건에 `check-openapi-error-declaration.py`(L2404 실측 발행 · F2), ⓓ#595에 missable-entrance, ⓓ#553에 naming(F9).
  - **원문·정본 결함 후보(빚 채널 상신 — 이 패스에서 고치지 않음)**: `ontology-authoring.md` §16 역할명 매핑 표가 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED` 발행자를 controller-contract **단독**으로 적어 실물 3종(controller-contract·error-centralization·openapi-error-declaration)에 못 미친다 — 표 자체의 과소 기재.
