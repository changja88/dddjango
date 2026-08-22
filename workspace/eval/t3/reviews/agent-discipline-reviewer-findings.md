# T3 적대 리뷰 — agent-discipline-reviewer (2026-08-22)

- 대상: `workspace/eval/t3/specs/agent-discipline-reviewer.spec.json` + `workspace/eval/t3/worksheets/agent-discipline-reviewer.md`
- 대조: 발주서 · T3-authoring-brief · 원문 `dddjango/agents/discipline-reviewer.md`(130행 실측 일치) · `dddjango/scripts/check-*.py` 27종 docstring 실독 · `ontology-authoring.md` §13~§16
- 기계 대조: 블록 90·Work 317·절 스팬 연속/비중첩/전량 커버·무소유 0·basis 공란 0 확인, `ontology_migrate.py` 검증 전용 exit 0 재현. 주요 docstring 인용(«validates the canonical…»·«add no new error-mapping semantics»·mechanism AND 게이트·choices-literal 면제 3)~5)·#129·#493/#69·#497·#105/#112/#511·#431 방출 문면·#532 실방출 문면 등) 축자 대조 — 대부분 실물과 일치했다. 아래는 반박이 성립한 전건.

## HIGH

### F1 [배선 · s007 b42(L108) ⓓ#82] enforcedBy가 자기 basis·worksheet와 정면 모순
- 주장: 스펙의 ⓓ#82 규범이 `enforcedBy: ["check-business-vocabulary.py"]`를 달고 있는데, 같은 규범의 basis가 «#82 담당 검사기 부재(27종 전수 grep 0)»라고 스스로 부정하고, worksheet §4-⑥도 «담당 검사기가 0건인 물음 3종(#82·#492·#316)은 delegatedTo 단독»이라고 명시한다. 실측(27종 전 파일 `#82` grep)도 0건 — check-business-vocabulary.py는 #82를 방출·담당하지 않는다(#628 «재료» 소유는 이 규범의 집행이 아니다). 스펙-스펙 내부 모순 + 스펙-worksheet 모순 + 실물 불일치 3중.
- 수정안: 해당 norm의 `enforcedBy`를 제거해 #492·#316과 동일하게 delegatedTo 단독으로 통일하고, worksheet §2 표 #256행의 `E:` 표기도 함께 걷는다.

## MEDIUM

### F2 [배선 · s002 b4(L20)] PROOF_REQUIRED 발행자 오인용 — §16 표는 1종, 실물은 3종, 스펙은 2종
- 주장: DYNAMIC 발동 조건 규범의 basis가 «§16 매핑 표 — 두 검사기가 PROOF_REQUIRED 공동 발행»이라 하나, §16 역할명 매핑 표는 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`(발행)를 controller-contract 단독으로 기재한다(인용 허위). 실측으로는 `check-api-error-controller-contract.py`·`check-error-centralization.py`에 더해 **`check-openapi-error-declaration.py`(L2404 등)도 이 marker를 발행**한다. «잔여 exit 1 진단 전부가 marker»라는 규범의 발동 조건상 발행자 전원이 배선 대상인데 1종이 빠졌다.
- 수정안: enforcedBy에 `check-openapi-error-declaration.py` 추가, basis를 «marker 발행 실측 3종(§16 표는 controller 단독 기재 — 표 자체가 실물 과소)»으로 정정.

### F3 [배선 · s006 b4(L61) ↔ s003 b1(L34) ↔ s008 b2(L129)] 동일 문형 «소유자 표시/소유 지목»의 위임 대상 비일관
- 주장: 같은 문형(문면이 타 역할을 소유자로 지목)의 조항이 갈래 없이 두 방식으로 갈린다 — s003/b1 n4(Phase 2 지적의 소유자 표시 3종 라우팅: acceptance-tester·coder·design-architect 지목) → `D: command-dddjango`, s008/b2 n2(구현 정확성=코더… 소유 배분) → `D: command-dddjango`인데, s006/b4 n3(OpenAPI/runtime 기술 정확성의 acceptance-tester/coder 소유 «표시») → `D: agent-acceptance-tester + agent-coder`, s008/b2 n9(동시성 적정성/정확성 타 소유) → `D: agent-acceptance-tester + agent-coder`. worksheet §0 P-C(«문면이 지목한 조항만 그 Agent로 위임»)를 s003 n4·s008 n2에는 적용하지 않고 s006 n3·s008 n9에는 적용했는데 구별 기준이 어디에도 기록돼 있지 않다 — 무근거 배선 분기.
- 수정안: 판별자를 명문화해 일관 적용(예: «표시 의무» 자체는 리포트 형식 절차 = Coordinator, «판정 소유» 선언은 지목 Agent)하고 네 조항을 그 자로 재배선; worksheet §0 P-C에 판별자 추가.

### F4 [재진술 · s008 b1(L128) ↔ s003 b1(L34) · s002 b11(L28) ↔ s006 b4(L61)] same-doc 재진술 후보 2쌍 미심의
- 주장: worksheet §4-⑤는 후보 ⑴(s001 desc ↔ s003)·⑵(s006/b4 ↔ s008/b2)만 심의하고 0건 판정했으나, ⓐ L128 «코드·테스트를 수정하지 않는다(읽기 전용). 반영은 코더가 한다» ↔ L34 «코드를 직접 고치지 않는다»(+ s001 desc까지 3중 — 같은 금지가 Work 3개로 각자 승격, §15 «정본 1곳만 Work 승격» 긴장), ⓑ L28 «HTTP 의미론·public code의 적정성·호환성은 API reviewer 소유이므로 중복 판정하지 않는다» ↔ L61 «API reviewer는 wire meaning…소유하므로 public-code 적정성을 중복 판정하지 않는다»는 심의 자체가 없다. 블록 단위 restates의 부작용(⑤의 논거)이 이 두 쌍에도 성립하는지는 판단 사항이지만, 후보 수집이 불완전한 것은 사실이다.
- 수정안: §4-⑤에 두 쌍 추가 심의를 기록하고, 축자성 인정 시 정본 선정 후 spec `restates` 기입(블록 부분 중첩이면 기존 유예 논리로 메모 유지).

## LOW

### F5 [배선 · s007 b22(L86) n9] 406/415 규범에 check-ninja-boundary-middleware 배선 과대
- 주장: 규범은 «class controller의 함수형 Router 전환·별도 API instance 격리 금지»인데, 검사기는 driving_layer 자가 미들웨어의 `settings.MIDDLEWARE` 자가등록만 검출한다(docstring 실독). 세 형태 중 어느 것도 검출 형태가 아니고 «동일 사건군» 주장은 docstring이 지지하지 않는다(별도 instance 복수는 이미 n5의 composition-root 몫).
- 수정안: delegatedTo 단독으로 내리거나 basis를 «인접 사건군 참고»로 강등.

### F6 [배선 · s007 b12(L76) n5] #249·#256은 평면 ORM 모델 위 판정 메서드를 못 본다
- 주장: 위반 현장은 domain_layer «밖»(models.py·driven_layer 모델)의 판정 메서드인데, #249·#256은 domain_layer «안» 골격(자식 구성·루트 파일) 검사라 이 금지를 집행하지 못한다. 이주 «목적지» 골격의 기계 절반이라는 논리라면 그 취지를 basis에 명시해야 한다.
- 수정안: enforcedBy 제거 또는 basis를 «목적지 골격 절반, 위반 검출은 전적으로 감수자»로 정밀화.

### F7 [배선 · s007 b47(L121) n1] human 판정 #254에 반대편 검사기 enforcedBy 병기
- 주장: 문면이 «검사기가 아예 없다(전적으로 네 몫)»인 규범에 check-domain-model을 배선했다. worksheet ⑥ 스스로 «기계 반대편 #546·#547»이라 자인 — §16 역도 성립 조항은 «담당 검사기 도피 금지»이지 반대편 커버 검사기의 병기 요구가 아니다. (부기: #547 docstring의 실물 방향은 «루트 비대→경계를 쪼갠다»라 원문 문면 «너무 갈린 쪽만 본다»와도 어긋난다 — 원문 결함 후보로 별도 채널 보고 가치.)
- 수정안: delegatedTo 단독. 원문 문면-검사기 방향 불일치는 빚 채널로 상신.

### F8 [배선 · s002 b8~b10(L24~27) · s003 b5(L41) n5] DYNAMIC 대체 증거 규범에 «분석 대상 동일» enforcedBy 병기
- 주장: 증거 4·5·6 수령과 «별도 승인과의 동일성 검증»은 검사기들이 PROOF_REQUIRED로 분석 불능을 자인한 자리의 대체 경로다. 그 검사기를 집행자로 배선한 근거가 «증거 대상 = 분석 대상 동일»뿐인데, 분석 대상 동일은 집행이 아니다(해당 실행에서 검사기는 이미 판정을 포기한 상태).
- 수정안: enforcedBy를 걷고 위임 단독으로 두거나, basis에 «집행 아님·대상 사상(寫像)임»을 명시하는 규약 결정을 소급 패스에 상신.

### F9 [배선 · s007 ⓓ 표(L98~105)] 다중 방출 검사기 병기 기준 비일관
- 주장: row #181은 쓰는-자리 방출자(broker-contract #532)를 병기했는데, row #595는 쓰는 자리 #512의 방출자 check-missable-entrance.py를, row #553은 쓰는 자리 #589의 방출자 check-naming.py를 병기하지 않았다. worksheet ⑦의 다중 소유 처리 기준(주 소유+병기)이 행마다 다르게 적용됐다.
- 수정안: 병기 자(주 소유 단독 vs 쓰는-자리 방출자 전부) 하나를 정해 8행 재적용.

### F10 [규범식별 · s003 b1(L34) n2] label에 타 절 문면 혼입
- 주장: label «코드 직접 수정 금지(반영은 코더)»의 괄호 보충은 L34에 없고 s008 L128의 문면이다. Work label이 자기 블록 문면 밖 내용을 지면 재진술 대조·정본 추적이 흐려진다.
- 수정안: label을 «감수 리포트 외 코드 직접 수정 금지»로 자기 문면 한정.

### F11 [배선 · s007 b7(L71) n1] pytest 관용구 규범에 check-test-config 배선 — 기계 절반이 실제로 없음
- 주장: 규범 본문은 관용구(함수형·assert·django_db 마커)인데 검사기 관할은 settings 바인딩·`test/` 구조 축이고 basis 스스로 «관용구 형태는 검사기 밖»이라 인정한다. 인접 관할을 «기계 절반»으로 승격한 배선.
- 수정안: enforcedBy 제거, 또는 규범을 (바인딩/구조 ↔ 관용구)로 분해해 앞쪽만 배선.

### F12 [규범식별 · s007 L71·L86·L92] Override class 0건 — 선행 규범 무효화 문면의 class 검토 흔적 부재
- 주장: 317 Work 중 Override 0건인데, «관례 존중 예외 없음»(L71)·«구 보존 문구는 걷었다 / preserve가 보존하는 것은 배선이 아니다»(L86)·«기존 배치 일치는 통과 사유가 아니다·명세 정당화는 면제 사유가 아니다»(L92)처럼 기성 규범·관행을 명시적으로 눌러 이기는 문면이 여럿이다. Prohibition/Obligation 분류가 방어 가능하더라도 worksheet에 Override 비채택 사유가 한 줄도 없다.
- 수정안: worksheet §4에 Override 판단 기준·비채택 사유 기록(class 변경은 후보 검토 후).

## 판정 요약

high 1 · medium 3 · low 8. 구조(경계·커버리지·계수)와 docstring 인용 대부분은 실물과 일치 — 반박의 중심은 배선 렌즈(자기모순 1·오인용 1·비일관 2·과대 배선 다수)와 same-doc 재진술 심의 누락이다.

## 처분 (수리자 판정 — 2026-08-22)

수리 대상: `workspace/eval/t3/specs/agent-discipline-reviewer.spec.json` + `workspace/eval/t3/worksheets/agent-discipline-reviewer.md` 2개. 원문 `dddjango/agents/discipline-reviewer.md`·`ontology/`·타 에이전트 산출물은 무수정(브리프 §금지). 제출 검증 `ontology_migrate.py`(검증 전용·`--write` 미사용) **exit 0** 재확인 — 블록 90·Work 317 불변(계수 무영향, 배선·분류·label만 변경).

| # | 처분 | 근거 한 줄 |
|---|---|---|
| F1 | **fixed** | 27종 전수 `#82` grep 0 재현 — business-vocabulary는 «재료»인 #628 토큰만 소유하고 #82를 방출·담당하지 않는다. enforcedBy 철회(#492·#316·#254와 동형 delegatedTo 단독) + worksheet §2 row 256·§4-⑥ 동반 정정. |
| F2 | **fixed** | `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED` 발행자 실측 3종 확인(controller-contract L1581·1590·1890 / error-centralization L2323 외 / **openapi-error-declaration L2404** — UsageError 발행). enforcedBy에 openapi-error-declaration 추가·basis를 실측 3종으로 정정. §16 매핑 표의 «controller 단독» 과소 기재는 원문 무수정 원칙상 §4-⑫에 빚 항목으로 상신. |
| F3 | **fixed** | 동일 «타 역할 지목» 문형의 배선 분기가 실재하고 판별자가 미기록임을 확인. §0 P-C에 판별자 ⒤(표시·라우팅 의무=절차→Coordinator) / ⑵(판정 소유 배분·중복 판정 배제 선언=지목 Agent)를 명문화하고 s006/b4-3 → `command-dddjango`, s008/b2-2 → `agent-coder+agent-design-architect+agent-acceptance-tester`로 재배선(s003/b1-4·s008/b2-9는 판별자상 기존 배선이 정답이라 유지). |
| F4 | **fixed(심의 추가·restates는 기각)** | 후보 수집 누락은 사실 — §4-⑤′에 두 쌍을 추가 심의했다. 다만 ⓐ는 술어·범위가 셋 다 다르고(코드 ↔ 코드+테스트·«읽기 전용»·반영 주체), ⓑ는 적용 모드(DYNAMIC 한정 ↔ Phase 1·2 scope)와 열거 집합이 달라 **축자 사본 불성립**이며, `djr:restates`가 블록 단위라 세 블록 모두 다중 Work가 정본을 잃는다(§15 부작용) → 기각 사유를 명기하고 spec `restates` 미기입 유지. |
| F5 | **fixed** | `check-ninja-boundary-middleware.py` docstring·판정부 실독 — 검출 대상은 «driving_layer 자가정의 미들웨어의 `settings.MIDDLEWARE` 자가등록» 한 형태뿐이고 규범의 세 형태(함수형 `Router` 전환·별도 API instance 격리)를 보지 못한다. enforcedBy 철회, basis를 «인접 사건군 참고·집행 아님»으로 정정. |
| F6 | **fixed** | #249(domain_layer 직계 파일 금지)·#256(애그리거트 폴더 골격)은 **domain_layer 안** 골격 검사라 위반 현장(그 밖 평면 ORM 모델의 판정 메서드)을 못 본다. `check-app-container` docstring도 «판정-소유 형태(빈혈) 같은 의미 변종은 범위 밖(discipline-reviewer 몫)»으로 자인. enforcedBy 철회 + basis 정밀화. |
| F7 | **fixed** | §16 «역도 성립»은 **담당** 검사기 도피 금지이지 반대편 검사기 병기 요구가 아니고, 문면 스스로 «#254는 검사기가 아예 없다»·«기계(#546·#547)는 너무 갈린 쪽만»이라 자인한다. enforcedBy 철회. 부기(#547 docstring 실물 방향이 원문과 어긋남)는 실물 대조로 확인 — 원문 무수정이라 §4-⑥에 빚 채널 상신으로 기록. |
| F8 | **fixed** | 네 조항 모두 검사기가 `PROOF_REQUIRED`로 **분석 불능을 자인한** 자리의 대체 증거 경로다(증거 4·5·6은 DYNAMIC 모드 입력, 별도 승인 동일성 검증은 사용자 승인 evidence 대조라 검사기 입력 밖). «증거 대상 = 분석 대상»은 대상 사상이지 집행이 아니므로 enforcedBy 4건 철회 + «집행 아님·대상 사상» 취급 규약을 §4-⑫에 소급 패스 상신 항목으로 남김. |
| F9 | **fixed** | 8행 재점검 결과 6행은 «주 소유 + 쓰는-자리 방출자 전부»를 따르고 2행만 이탈함을 확인(#595의 #512→missable-entrance, #553의 #589→naming 누락). 그 자로 단일화해 2행에 병기 추가하고 §4-⑦′에 자와 재적용 결과를 기록(#316은 담당 검사기 0이라 병기 대상 없음). |
| F10 | **fixed** | L34 문면은 «감수 리포트만 낸다. 코드를 직접 고치지 않는다»뿐이고 «반영은 코더»는 s008 L128 소유임을 원문 대조로 확인. label을 «감수 리포트 외 코드 직접 수정 금지»로 자기 문면 한정(F4-ⓐ 심의의 경계도 함께 선명해짐). |
| F11 | **fixed** | `check-test-config.py` docstring 3슬라이스(⑴ settings 바인딩 ⑵ `test/` 구조 ⑶ 환경축) 어디에도 «관용구 형태»가 없다 — basis 자신도 인정. 해당 norm만 enforcedBy 철회(같은 블록의 #392 factory_boy·#387 TestCase 조항은 실담당이라 병기 유지 — 규범 분해 대신 조항별 배선 유지가 문장 해상도 규약에 맞다). |
| F12 | **fixed(기준 기록 + class 2건 조정)** | 코퍼스 선례(implementation-django s015-2.5·s019-3.1 / architecture-ddd s042-6.1 / discipline-cleancode s092-12.2)로 Override 판단 기준을 세워 §4-⑪에 기록. 채택 2건(L86 preserve 배선 우선·L92 표준 트리 우선 → Obligation→Override), 비채택 3건(L71 «관례 존중 예외 없음»·L92 «명세 정당화는 면제 아님»·L60 격리 범위 한정 — 모두 호스트 규범에 붙은 부수 절이라 class 유지)과 사유를 명기. |

**기각 0건 · 반영 12건**(F4는 «심의 누락»이라는 지적 자체는 성립해 반영, 지적이 제안한 restates 기입은 축자성 불성립으로 미채택 — 사유를 §4-⑤′에 명기). 반박이 성립하지 않은 지적은 없었다.

**남은 상신(이 패스에서 고치지 않음 — 소유가 밖)**: ⑴ `ontology-authoring.md` §16 매핑 표의 PROOF_REQUIRED 발행자 과소 기재(1종 ↔ 실물 3종) ⑵ 원문 L121 «기계는 너무 갈린 쪽만» ↔ `check-domain-model.py` #547 docstring(«루트 비대 → 경계를 쪼갠다») 방향 불일치 ⑶ 블록 단위 `restates`의 «부분 중첩 사본·다중 Work 블록» 처리 규약(F4 두 쌍이 대기) ⑷ «집행 아님·대상 사상» enforcedBy 취급 규약(F8).
