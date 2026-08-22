# T3 적대 리뷰 — 묶음 «small-agents» (agent-acceptance-tester · agent-design-review-db · agent-design-review-ddd)

- 대상: `workspace/eval/t3/specs/agent-acceptance-tester.spec.json`(+worksheet) · `agent-design-review-db.spec.json`(+worksheet) · `agent-design-review-ddd.spec.json`(+worksheet)
- 대조 재료: `T3-authoring-brief.md` · 발주서 3건 · 원문 3건(AT 54행·db 44행·ddd 44행 — 마커 미삽입 실측) · `ontology-authoring.md` §13~§16 · `ontology_migrate.py` docstring · `check-*.py` 27종 docstring 전수 실독 + 쟁점 검사기(app-container·business-vocabulary·db-table·mechanism-ownership·error-centralization·test-config·transaction-boundary·domain-model·layer-skeleton·context-isolation·event-publish·idempotency-scope-creep·response-schema-bypass·ninja-boundary-middleware·composition-root·api-error-controller-contract·openapi-error-declaration) grep 실측 · 선행 판례(`agent-coder-findings.md` R2-*·`agent-design-review-api-findings.md` F1~F10 처분) · 상대 원문(coder.md 마커 4~6행 좌표 환산·design-architect.md raw L61·L64 = 센서스 L56·L59) 실독.
- 검사 방식: 4렌즈 전수 절 검사(표본 아님). migrate 검증 3건 재실행(전건 exit 0 — AT 블록 35·Work 87 / db 블록 24·Work 45 / ddd 블록 24·Work 37, 검수표 주장과 일치). census 독립 재계수(문장·종결절 단위) 3건 전건 대조. 배선 basis 의 docstring 인용 전건 실물 대조(«27종 술어 0» 계열 — STOP_FOR_USER_APPROVAL·operationId·xfail·RFC 9457 grep 0 재확인). 재진술 byte-주장 실측(db↔ddd s002 스팬 sha256 `849bfc02…` 동일 · 발견/권고 2행 · s005 2행 · AT L45↔coder 센서스 L45 · AT L30 1문↔coder 센서스 L39 1문 — 전건 일치).
- 판정: **fail** — high 0건 · medium 5건 · low 3건. spec·worksheet 는 수정하지 않았다.

## 전수 검사 무결 축 (반박 시도 후 성립 확인)

- ① 경계·kind: 3문서 모두 코드 펜스·표·체크박스 0 실측 — norm/prose 2종 판정 타당. 전 절 `line_start+1` 개시·연속·비중첩·§13 공백 귀속(선행 블록 후행 스팬·절 선두 구분자는 첫 블록) — migrate exit 0 으로 기계 확인. 프론트매터 행 단위 분해(skills 키+목록 한 덩이 병합 포함)·description 행만 norm — coder R2 리뷰가 «타당» 확정한 판형과 동일. 블록 과대 병합 없음.
- ② 규범 식별: 독립 재계수 — AT 6/5/5/64/7=87 · db 4/2/8/28/3=45 · ddd 4/2/12/16/3=37, spec 과 전건 일치. 발주서 대비 초과분(AT +8·db +7·ddd +6)은 검수표 §1 이 자리별 전액 내역과 판별자(coder R2-9 반려·R2-10 수용으로 확정된 «독립 종결절+행위 대상 상이»)로 정당화했고, 발견/권고 불릿 승격은 api 판 선례(s004 b2·b3 각 1 Work)와 대칭이다. spec<census 절 0 — 누락 위험 없음. class 5종: Permission 1(AT b16-2)·Override 0 판정 전건 무리 없음.
- ③ 배선(무결분): 무소유 0건(도구 단언). check-test-config ⑴⑵·mechanism-ownership #336/#337/#593·db-table #329~#331/#630 가드 문면·domain-model #249/#256/#257/#264/#289/#290/#299/#304·transaction-boundary D50/#195/#197/#200/#287/#599·layer-skeleton #486/#488/#490·context-isolation #12/#13/#110·business-vocabulary #628/#119·event-publish 표제문·idempotency-scope-creep G0 · error-centralization preserve 문장·openapi-error-declaration 두 인용문·response-schema-bypass 표제+L1026 carveout — **인용 전건 실물 일치**. 축 반대·술어 부재 배제 심의(idempotency-scope-creep·event-publish·domain-model 이중 계상 회피·ninja-boundary-middleware R2-5 승계·composition-root provenance 한정) 전건 성립.
- ④ 재진술(무결분): spec `restates` 0 = 교차 문서 전량 유예 규약 준수. 발주서 restate 열 전건(AT s003·s004 / db s003·s004·s005 / ddd s003·s004·s005) 유예 절 수록. byte-축자 주장 실측 전건 일치(위 검사 방식 참조). 동축 3각의 restates 미기입 자체는 api F8 처분(§15 «사본 블록» 문면과 정합 — 존치)과 동일 판형으로 성립.

## 발견 (심각도순)

### W3-1 [medium · 재진술] agent-acceptance-tester — 검수표 §4-④ 의 «각 Work basis 에 동축 표시를 남겼다» 주장이 spec 실물과 불일치 (0건)

- **절**: s001·s002·s004 (검수표 §4-④ 의 세 쌍)
- **주장**: 검수표 §4-④ 는 같은 문서 안 세 쌍(⑴ s001 b2-4 ↔ s003 b1-4 ↔ s005 b1-1 «구현 코드 금지» 3각 · ⑵ s001 b2-3 «블랙박스» ↔ s002 b1-5 «프로덕션 코드 열람 금지» · ⑶ s004 b13 STOP 조항 ↔ b19 preserve)을 심의하고 «`djr:restates` 는 블록 대 블록 관계라 미기입하고, **대신 각 Work 의 basis 에 동축 표시를 남겨** 소급 패스가 찾을 수 있게 했다»고 적었다. 그러나 spec 에서 `동축` 문자열은 **0건**이다(grep 실측 — db 판 4건·ddd 판 3건과 대조적). ⑵의 Work #3·#11, ⑶의 Work #47·#61 은 **어느 방향으로도 상호 참조가 없고**, ⑴은 P-C 소유자 지목(«s005 b1 (coder의 몫)»)만 있어 재진술 의심 표지가 아니다. api 판 F8·F10 처분이 세운 기준(전 꼭짓점 태그 + 소급 통합 후보 기록)과 coder R2-3 판례(«실물과 다른 기록은 감사 기능을 잃는다»)에 걸린다 — 소급 패스가 이 검수표 문장을 믿으면 ⑵·⑶ 쌍을 영구히 놓친다.
- **수정안**: Work #3↔#11 · #47↔#61 · #4/#15/#81 3각의 basis 에 동축(재진술 의심) 표시를 실제로 추가하고 §4-④ 말미에 api 판형대로 «소급 패스 통합 후보» 행을 남기거나, 아니면 §4-④ 문장을 실물대로(«심의 기록은 이 검수표 §4-④ 가 유일하게 진다») 고쳐 허위 서술을 제거한다.

### W3-2 [medium · 배선] agent-acceptance-tester s004/b19 (L43) — Work #63 «code-profile shape 혼입 강제 금지» 의 check-error-centralization enforcedBy 는 비집행 선언을 커버로 오독

- **절**: s004 (Work #63)
- **주장**: basis 인용문 «Positional-only, `auto`, and `preserve-established` invocations do not apply schema semantics»는 검사기가 preserve 실행에서 **스스로 schema 의미를 적용하지 않는다**는 자기 한정 선언이다. 이 규범의 위반 주체는 tester(인수 «테스트»가 preserve scope 에 code-json shape 를 강제 단언)인데, 이 검사기는 프로덕션 오류 모듈만 보고 테스트 파일을 보지 않으므로 이 규범의 위반 표면에서 **구조적으로 발화 불가**하다. «검사기의 자기 절제가 곧 규범의 기계 실현»이라는 논리는 coder R2-7 처분(transient-overmapping «비집행 선언» → 검사 공백 명기)과 api F9 처분(비발화-불근거 선언 검사기의 E 병기 기각)이 이미 벌한 형태이고, R2-12 가 세운 병기 기준(«일부 국면에 결정적 술어가 닿으면 병기 / 전 국면 미커버면 공란»)에서 이 자리는 술어가 닿는 국면이 0이다. 인용된 «api 판 preserve 계열 배선과 동형»도 오독이다 — api 판의 preserve 규범들은 심사 대상이 코드 산출물이라 검사기 술어가 같은 산출물에 실제로 닿지만, 이 규범의 대상은 테스트다.
- **수정안**: Work #63 의 enforcedBy 철회(D: command-dddjango·agent-design-review-api 유지), 검사기 사실은 basis 의 배제 심의(«preserve 경로 schema 의미 미적용은 플러그인 측 사실 — 테스트 측 강제 금지의 술어는 27종에 0»)로 이동. 검수표 §2 #63 행·§4-⑦ 재생성.

### W3-3 [medium · 배선] agent-design-review-ddd s004/b3 (L32) — Work #24 «항-(1) 평면 모델 위 판정 잔류 금지» 의 check-app-container enforcedBy 는 자기 부인 축 + 이중 계상

- **절**: s004 (Work #24)
- **주장**: basis 가 그대로 인용한 docstring 문장이 «판정-소유 형태(빈혈) 같은 *의미* 변종은 **범위 밖**(discipline-reviewer 몫)»이라고 이 규범의 축(판정이 평면 모델 위에 남는 형태)을 **명시 부인**한다. 검사기의 실제 술어(G1~G3 AND: `application/` 밖 앱 + 신규 마이그레이션/미추적 + 이주 대응 부재)는 항-(2)의 «위치» 축이고, 그 축은 같은 블록의 Work #25 가 이미 check-app-container+check-layer-skeleton 으로 정배선했다 — 같은 기계 커버를 두 Work 에 얹은 이중 계상이다. db 판 검수표 §0 이 check-domain-model 을 «이중 계상 회피»로 배제한 자기 기준, api F5 처분(«같은 검사기를 자기 축 규범에만 두어 커버리지 이중 계상 제거»)과 정면 충돌한다. 판정 메서드만 얹고 마이그레이션이 없는 위반(항-(1)의 전형)에는 G2 가 성립하지 않아 발화하지도 않는다. basis 의 «§16 역도 성립» 원용은 docstring 이 인용하는 조문이 항-(2)라서 이 Work 가 아니라 #25 에서 성립한다.
- **수정안**: Work #24 의 enforcedBy 철회(D: agent-design-review-ddd + agent-discipline-reviewer 유지 — docstring 명시 이양은 delegatedTo 근거로만 사용), basis 를 배제 심의로 재작성. 검수표 §0 P-D·§2 #24·§4-⑦ 동반 갱신.

### W3-4 [medium · 재진술] agent-design-review-db §3 유예 목록 — architect 데이터 lens 항(센서스 L59)의 병렬 legs 미등재

- **절**: s004 (b1·b2·b3, 부분적으로 b4-1·b6)
- **주장**: 발주서 restate 열이 s004 전체를 `agent-design-architect`/s005 와 짝지었고, 상대 실물(design-architect.md raw L64 = 센서스 L59 — api 처분 좌표 실측과 정합)은 한 불릿에서 «**스키마 변화, 인덱스·제약, 트랜잭션 경계·격리·락 전략**(§9.5·§9.6 Risky Write), **마이그레이션 안전**(rollout/backfill)»을 열거해 이 문서 s004 의 b1(스키마·모델링)·b2(인덱스)·b3(제약)·b4-1(트랜잭션 경계·격리·락)과 전부 작성↔심사 병렬이다. 유예 목록은 같은 상대 행에서 R8(Risky Write 8행)·R12(마이그레이션 안전)만 수록했다 — 같은 불릿의 나머지 legs 3~4건이 빠졌다. Idempotency storage 행 서술 ↔ b6(멱등성 저장소 설계 여부)도 미심의다. coder R2-2(병렬 쌍 추가 누락 = medium)·api F2(architect 병기 비대칭 = medium) 판례와 같은 결이고, 유예 목록은 소급 연결 패스의 유일 재료라 누락 = 연결 영구 누락 위험이다.
- **수정안**: R12 를 «architect/s005 (L59) 데이터 lens 항 전열(스키마·인덱스·제약·트랜잭션/락·마이그레이션 안전) ↔ 이 문서 b1·b2·b3·b4-1·b7» 로 확장하거나 legs 별 항을 추가하고, b6↔Idempotency storage 행은 심의 후 판정(등재 또는 비-재진술 사유)을 기록한다.

### W3-5 [medium · 재진술] agent-design-review-ddd §3 유예 목록 — architect 도메인 lens 항(센서스 L56)·데이터 항의 판정 소유 문구 legs 미등재

- **절**: s004 (b4·b5·b7·b2)
- **주장**: R16 은 architect 도메인 lens 항(센서스 L56 — raw L61 «애그리거트 경계와 불변식, **상태 전이, 유비쿼터스 언어, 관련 도메인 이벤트 채택 여부와 근거**») 을 b1(L30)과만 짝지었다. 같은 상대 행이 b4(L33 상태 전이)·b5(L34 유비쿼터스 언어)·b7(L36 도메인 이벤트 채택)과도 병렬인데 세 legs 가 유예 목록에 없다. 또 architect 데이터 항(raw L64)의 «비즈니스 판정(예: stock>=qty)은 인프라로 옮기지 않는다 — **판정·불변식은 도메인 애그리거트(또는 도메인 서비스)가 소유하고 프로덕션 경로에서 실행** … WHERE 엔 경합 가드만»은 b2(L31 판정 소유·경합 가드/판정 지점 분리)와 구문 수준 거울인데, R9 는 discipline-reviewer·ddd-final 만 적고 architect leg 를 뺐다. coder R2-2·api F2 판례에 걸리는 완결성 공백이다.
- **수정안**: R16 을 «L30·L33·L34·L36 ↔ architect/s005 (L56)» 으로 확장하고, R9 상대 열에 `agent-design-architect`/s005 (L59) 를 병기한다.

### W3-6 [low · 배선] agent-acceptance-tester s004/b13 (L37) — Work #44 basis 의 «④파일럿 … adv 중재 정정 승계»는 4원 밖 근거 유형 표기

- **절**: s004 (Work #44)
- **주장**: coder R2-11 처분이 «§16 4원(①문면 역할명 ②docstring ③P0 ④registry #N·기본값 표)에 '파일럿 선례'는 없다»로 확정했고 이 검수표 자신이 그 판례를 승계 출처로 선언했는데, Work #44 basis 는 파일럿 ninja §6.2 의 중재 정정 승계를 ④ 표지 아래 적었다. D-only 배선 자체(순환 배선 회피)는 타당하므로 표기 문제만 남는다.
- **수정안**: 근거 유형을 ①(문면이 shape 정본을 6번 slot 으로 고정) + ④(위임 기본값 표·12-slot 심사판)로 재표기하고 승계 사실은 유형 표지 없이 부기. 검수표 §2 #44 행 재생성.

### W3-7 [low · 배선] agent-design-review-db s004/b7 (L35) — Work #37 의 두 검사기 enforcedBy 는 «보존» 위반 표면에 발화 불가

- **절**: s004 (Work #37)
- **주장**: 규범 축은 «기존 `db_table`·`label`·`0001` **보존**이 명세에 박혔는지»다. basis 가 인용한 check-db-table 가드 문면(«기존(추적된) 모델의 db_table 은 신규가 아니므로 **보지 않는다**»)은 비검사 선언이라 기존 보존이 깨진 코드(추적된 모델의 db_table 개명)에 발화하지 않고, #329~#331 은 label «존재·값=BC 이름» 술어라 보존 축과 다르며(#330 의 표준 label 강제는 기존 label 보존과 오히려 긴장 관계), check-mechanism-ownership #337 은 파일명 «꼴» 술어지 기존 0001 보존 술어가 아니다. 미커버 명기는 정직하나 W3-2 와 같은 «절제 선언 = 커버» 혼동 소지가 있다. 다만 #593(손편집 금지)이 기존 마이그레이션 개변의 일부 국면에 실제로 닿아(이력 불변 인접) 판단 여지가 있어 low.
- **수정안**: E 를 공란으로 하고 두 검사기를 배제 심의(«가드는 비검사 선언·label/번호 술어는 보존 축 상이»)로 옮기거나, 유지한다면 basis 에서 가드 문면 인용을 커버 근거 자리에서 제외하고 #593 의 이력 불변 국면만 남긴다.

### W3-8 [low · 배선] agent-design-review-ddd s004/b5 (L34) — Work #29 check-business-vocabulary 의 «일관 사용» 축 인접성

- **절**: s004 (Work #29)
- **주장**: 규범은 유비쿼터스 언어의 «명세 전반 **일관** 사용» 점검인데, 검사기 술어는 어휘의 «소유·격리»(#628 정의 단일 출처·#47/#52 framework 어휘 격리)다. 단일 출처 강제가 일관성을 기계적으로 뒷받침한다는 독법(부분 커버 문구도 정직)과, «같은 낱말이 같은 뜻으로 쓰였는가»를 재는 술어는 0이라는 독법(api F5 «오용-차단 축은 부분 커버로 인정하지 않는다» 경계선) 사이의 경계 사례라 low 로 둔다.
- **수정안**: 존치한다면 basis 에 «일관성 자체의 술어는 0 — 단일 출처(#628) 축의 간접 커버» 명기 강화, 철회한다면 배제 심의로 이동. 어느 쪽이든 §0 P-D 에 경계선 기준 1행 추가.

## 종합

경계·kind(①)와 규범 식별(②)은 전수 재계수에서 견고했다 — 3문서 전건 spec 일치·판별자 정합·과대 산정 0. 결함은 두 갈래다. ⑴ **배선의 «절제 선언=커버» 혼동**(W3-2·W3-3, 잔향 W3-7·W3-8): 검사기가 «나는 이 축을 안 본다/안 한다»고 선언한 문장을 그 축의 기계 실현으로 뒤집어 읽은 자리들로, 선행 판례(R2-7·F5·F9)가 이미 그은 선의 재발이다. ⑵ **재진술 유예·기록의 완결성**(W3-1·W3-4·W3-5): AT 검수표는 spec 에 없는 동축 표시를 있다고 적었고, db·ddd 는 architect lens 항의 열거 legs 를 부분 수록했다 — 유예 목록이 소급 패스의 유일 입력이라는 R2-1 교훈이 선 자리다. spec·worksheet 는 수정하지 않았고 `--write` 도 쓰지 않았다.

## 처분 (수리 라운드 — 2026-08-22)

| # | 처분 | 근거 |
|---|---|---|
| W3-1 (medium · AT §4-④ 동축 표시 0건) | **fixed** | 성립 — `동축` grep 실측 AT 0건 / db 4건 / ddd 3건으로 같은 묶음 안 비대칭 확인. 검수표 문장을 실물에 맞춰 낮추는 대신 **실물을 문장에 맞췄다**: 세 쌍의 **일곱 꼭짓점 전건**(⑴ #4·#15·#81 ⑵ #3·#11 ⑶ #47·#61) basis 에 동축 표시를 기입(grep 0→7)하고 §4-④ 에 api F8·F10 판형의 «소급 패스 통합 후보» 3행을 신설. §2 표는 spec 에서 재생성(87행 일치). |
| W3-2 (medium · AT #63 error-centralization) | **fixed(E 철회)** | 성립 — 인용문은 검사기의 **자기 비집행 선언**이고, 실장 `_is_production_path`(L491–499)가 `test`/`tests`·`test_*`·`*_test.py`·`conftest.py` 를 전수 배제해 이 규범의 위반 표면(tester 의 «테스트»)에 구조적으로 발화 불가임을 코드 실독으로 확인. 인용된 «api 판 preserve 계열 동형»도 오독 — api spec 의 **같은 축** 규범(s006/b1-4 «preserve scope 의 code-profile 혼입 금지»)은 E 공란이고, 그쪽에서 E 가 선 preserve 자리는 심사 대상이 코드 산출물인 slot 규범뿐이다. `enforcedBy` 철회 후 basis 를 배제 심의로 재작성, §0 절제 목록에 등재, §4-⑦ 갱신. 부수 효과로 «enforcedBy 7 Work» 선언과 실물(8)의 계수 불일치도 해소됐다. |
| W3-3 (medium · ddd #24 app-container) | **rejected(핵심 처분 기각) · basis 정밀화만 반영** | 세 논거 중 둘이 원문 대조에서 무너진다. ⓐ **절반만 성립** — 인용 문장은 «이 좁은 결정적 그물이 «위치» 한 축을 모델 무관하게 집행한다»는 **긍정 선언** + «판정-소유 형태(빈혈) 같은 의미 변종은 범위 밖»이라는 범위 한정의 합성이고, 부인되는 것은 이 규범의 괄호 주석(형태)이지 주술어가 아니다. 이 Work 의 주술어는 «판정을 얹는 코드를 평면 모델에 **남기지** 않았는가» = 위치이며, 검사기 docstring 의 회귀 표본이 정확히 «기존 `catalog/` 가 루트 평면 + 새 마이그레이션/**판정 적재**인데 `application/` 로 이주 안 함» — §3.2 항-(1) 이주 실패 그 자체다(references/final.md L645 항-(1) 대조). ⓑ **기각** — «위치»는 항-(1)·항-(2)가 공유하는 한 기계 축이고, api F5 가 벌한 이중 계상은 **축이 어긋난** 병기이지 축을 공유한 병기가 아니다. ⓒ **수용** — G2 미성립 국면의 미발화를 한계로 신설. 또 지적대로 «§16 역도 성립» 원용은 자리를 잘못 잡았으므로(docstring 이 이름으로 인용한 조문은 항-(2) = b3-3) 이 Work 에서 빼고 b3-3 소관임을 명기. §0 P-D 에 경계선 ⑵ 를 명문화하고 §4 에 ⑧ 처분 기록 신설. W3-2 와의 정합: 거기엔 긍정 술어가 0이고 대상 산출물마저 스캔 밖이었다. |
| W3-4 (medium · db 유예 legs 누락) | **fixed** | 성립 — architect 원문 raw L64(= 센서스 L59 · 마커 7건 중 선행 5건 차감으로 환산 확인) 선두가 «스키마 변화, 인덱스·제약, 트랜잭션 경계·격리·락 전략(§9.5·§9.6 Risky Write), 마이그레이션 안전»을 한 줄로 열거하므로 b1·b2·b3·b4 첫 문장이 전부 작성↔심사 병렬인데 R8·R12 둘만 등재돼 있었다. **R16(b1)·R17(b2·b3)·R18(b4 첫 문장)** 을 신설하고 R12 의 상대 좌표도 leg 단위로 정밀화. 미심의였던 b6 은 **R19** 로 심의·판정 기록 — 멱등성 저장소 leg 만 상보 병렬(architect 는 «미요청이면 기본 '미적용' commit» 방향)이고 **outbox 전달 보장 leg 는 architect s005 에 상대 문면이 없어 비-재진술**(정본 후보 `architecture-db-final` §9.7 실독 확인). 유예 총 15→19건. |
| W3-5 (medium · ddd 유예 legs 누락) | **fixed** | 성립 — architect 도메인 lens 항(센서스 L56)이 «애그리거트 경계와 불변식, 상태 전이, 유비쿼터스 언어, 관련 도메인 이벤트 채택 여부와 근거»를 열거하는데 R16 이 b1 하나만 짝지었다 → **R17(b4)·R18(b5)·R19(b7)** 신설. 데이터 lens 항(L59) 말미의 «판정·불변식은 도메인 애그리거트(또는 도메인 서비스)가 소유하고 프로덕션 경로에서 실행 … `WHERE`엔 경합 가드만»이 b2 와 구문 수준 거울임도 실물 확인 → **R9 상대 열에 `agent-design-architect`/s005 (L59) 병기**. 유예 총 16→19건. |
| W3-6 (low · AT #44 근거 유형) | **fixed** | 성립 — §16 4원에 «파일럿 선례»는 없고(R2-11 확정) 이 검수표가 그 판례를 승계 출처로 선언한 터라 자기모순이었다. D-only 배선 자체(순환 배선 회피)는 유지하고 근거 유형만 **①(문면이 shape 정본을 6번 slot 으로 고정) + ④(위임 기본값 표·12-slot 심사판) + ②(27종에 shape 정본 판정 술어 0)** 으로 재표기, 파일럿·자매 spec 의 같은 결론은 «부기(근거 유형 아님)»로 표지 없이 남겼다. 3 spec 전체에서 «①~④ + 파일럿» 꼴 표지 **0건** grep 재확인. §2 #44 행 재생성 · §4 에 ⑨ 신설. |
| W3-7 (low · db #37 두 검사기) | **fixed(제시 대안 ⑵ 채택 — E 유지 + basis 수정)** | 지적의 절반이 성립한다 — 가드 «기존(추적된) 모델의 db_table 은 … 보지 않는다»는 **비검사 선언**이라 추적 모델의 db_table 개명에 미발화하고, #330(label=BC 이름)은 기존 label 보존과 오히려 긴장하며 #337·#336 은 파일명 꼴·위치 술어다 → 셋 다 커버 근거 자리에서 **배제 심의로 강등**. 다만 «보존»에 실제로 닿는 **긍정 술어가 셋** 있어 E 는 유지했다: #329(`label` 명시 의무 — implementation-django §10.4 step 1 «label 은 기존 값을 유지한다»의 기계 짝으로, 명시가 없으면 폴더 이동에 `(label, migration)` 이력이 끊긴다) · #630(이주 산출물의 `db_table` 명시 존재 — §10.4 자신이 «보존 db_table 을 *명시*했으면 통과한다»로 이 백스톱을 지목) · #593(기존 `0001` 손편집 차단). §4-⑦ 동반 갱신. |
| W3-8 (low · ddd #29 business-vocabulary) | **fixed(제시 대안 ⑴ 채택 — 존치 + basis 강화 + §0 경계선)** | 경계선 사례라는 진단에 동의한다. 존치 근거는 #628(업무 어휘 정의의 단일 출처)이 «같은 낱말이 여러 곳에서 다른 뜻을 갖는 것»을 코드에서 원천 차단하는 유비쿼터스 언어의 기계 실현이라는 점이고, 인정 범위를 **#628 한 축의 간접 커버**로 좁히면서 «일관성 자체의 술어는 27종에 0»을 basis 에 명기했다(#47·#52 격리 축은 이 규범의 축이 아니므로 배제로 강등). §0 P-D 에 경계선 ⑶(«간접 커버는 병기하되 그 축 자체의 술어 0 을 명기»)을 신설하고 §4 에 ⑨ 처분 기록. |

**집계: fixed 7건 · rejected 1건**(W3-3 — 핵심 처분인 `enforcedBy` 철회는 기각하고 지적 중 성립한 두 갈래(G2 한계 미기록 · «역도 성립» 오원용)만 basis 에 반영). spec 변경은 **11 norm**(AT 8 — #3·#4·#11·#15·#47·#61 basis 동축 태그 · #44 basis 근거 유형 · #63 배선 철회+basis / db 1 — #37 basis / ddd 2 — #24·#29 basis)이고 **배선 값이 바뀐 자리는 AT #63 하나뿐**이다. Work 채번·블록 경계·kind 는 3문서 전건 불변. `enforcedBy` 총계는 AT 8→7 · db 3(불변) · ddd 9(불변).

**검증**: 3 spec 각각 `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py <spec>` → **전건 exit 0**(검증 전용 · `--write` 미사용). 세 검수표의 §2 배선 근거 표는 spec JSON 에서 **기계 재생성**해 87/45/37 행 ↔ spec norm 순서·값 일치를 재확인했다(R2-3 «수리의 반쪽 반영» 재발 경로 차단).
