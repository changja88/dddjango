# W3 적대 리뷰 — 묶음 «django-skills» 발견 전건

- 대상: `implementation-django-skill` · `implementation-django-ninja-skill` · `implementation-django-web-skill` (spec + worksheet)
- 리뷰 방식: 4렌즈 전수(경계·kind / 규범 식별 / 배선 / 재진술). 원문 3종 실독 · 발주서 3종 대조 · `check-*.py` 27종 docstring 실독 · 정본 spec(`implementation-django-final`·`-ninja-final`·`-web-final`·`architecture-ddd-final`) 실물 대조 · `ontology_migrate.py` 검증 전용 재실행(3종 모두 exit 0 재확인 · `--write` 미사용).
- 판정: **반려(수리 후 재제출)** — high 0 · medium 2 · low 12. 블록 분해·kind·재진술 유예 좌표는 대부분 실물 정합(표 판형=파일럿 s051-8, frontmatter=agent-coder 판례, 유예 표 좌표 전수 대조에서 web 1건 외 전부 일치)이나, §16이 금지한 «담당 검사기 오인» 실물 1건과 census 재계수 판정의 전제 부실이 남는다.

## medium

### M1. [배선] implementation-django-ninja-skill · s004/b1 — 규칙 #96 담당 검사기 오인 (basis 인용 허위)
- **주장**: «Router 책임의 4종 한정»(Prohibition)의 basis가 «#96 driving 잎은 domain_layer 애그리거트·리포지토리 선언·도메인 이벤트·port 선언을 import 하지 않는다»를 **check-context-isolation.py docstring**의 문면으로 인용한다. 실물 대조 결과 #96은 `check-event-publish.py` 소유다(«#96 [ast] driving_layer 잎은 domain_layer 의 애그리거트·엔티티·리포지토리 선언·도메인 이벤트와 port 선언을 import 하지 않는다» — check-event-publish.py docstring 11행). check-context-isolation.py에는 #96이 등장하지 않고 driving 잎 규칙은 #93/#94/#95뿐이다. §16 L-F 교훈(8종만 보고 9종 오배선)이 금지한 바로 그 유형이며, worksheet의 «27종 전수 실독 완료» 주장과 배치된다.
- **파급**: enforcedBy 목적지(check-context-isolation)는 정본 s006-1.3 b3와 일치해 우연히 유지되나, ① 근거 인용이 허위이고 ② #96의 실소유자 `check-event-publish.py`의 배선 병기 여부가 심사 자체가 안 됐다(§16 «담당 검사기의 docstring 근거가 있는데 빠뜨리면 오배선»의 역방향 미점검).
- **수정안**: basis를 #93/#94/#95(context-isolation 실물)로 교정하고, #96 소유자 `check-event-publish.py`의 enforcedBy 병기를 명시 심사(채택/기각 사유 기록). worksheet 배선표 재생성.

### M2. [규범식별] implementation-django-ninja-skill · s004 — census +20 재계수 판정의 전제 부실
- **주장**: census 35 → spec 55(+20)를 «센서스 과소»로 판정한 핵심 사유 «사본의 해상도가 정본보다 낮으면 재진술 연결(웨이브 4 소급 패스)이 불가능해진다»(worksheet §1)는 기계 실물과 어긋난다 — `djr:restates`는 **블록→블록** 링크다(`ontology_migrate.py` 176~183행). 사본 블록의 Work 해상도는 소급 연결의 성립 조건이 아니다. 또한 §13 «‹문장 해상도› = Work 채번 단위가 문장» 조항을 한 번도 다루지 않은 채, 자체 재계수 33문장을 넘는 55 Work(문장 이하 채번)를 세웠다.
- **완화 요소**: 불릿별 대조표의 ⑴행위 대상 ⑵규범 유형 축 판별자와 정본 Work 1:1 대응 기록은 충실하다. 결론 자체는 유지될 수 있다.
- **수정안**: 판정 사유에서 «연결 불가능» 전제를 제거하고, §13 문장 해상도 조항 대비 «문장 내 다규범의 분리 채번» 처분을 명시적으로 논급(계약 개정 없이 갈 수 있는 근거를 적거나, 문장 단위로 재병합). django·web worksheet의 동일 전제(«압축 사본의 해상도가 정본보다 낮을 수 없다»)도 함께 교정.

## low

### L1. [재진술] implementation-django-skill · s001 — 같은 문서 사본 블록의 Work 이중 승격 (3문서 공통 · 확신 없음)
s001/b2(description)가 `restates`(→s003 b1~b4)와 **자기 Work 2건 채번**을 겸한다. §15 «재진술: 정본 1곳만 Work 승격 + 사본 블록에 djr:restates»와 파일럿 사본 블록 판형(ddd-final s017-3.2 b1: restates+norms=0)에 어긋난다. 다만 T3 전 wave의 *-skill spec 전부(architecture-api·db·ddd·cleancode·tdd·python·test)가 같은 형태이고 census 규범 수(2)와도 정합이라, 개별 수리가 아니라 **§15 해석의 일괄 확정**(스킬 전문은 압축 사본이므로 축자 쌍 규율의 예외인가)이 필요하다. ninja·web 동형.

### L2. [규범식별] implementation-django-web-skill · s004 — +7 재계수와 adv 중재 판형의 긴장 미론급
이 발주서의 census는 adv 중재(2026-08-19)가 «문장 단위 재계수·병렬 위임은 1문» 판형으로 s001을 4→2로 동결한 산물인데, s004 30행 재계수(1문→4 Work)는 같은 병렬 열거를 반대로 처분한다. worksheet §1·§4의 술어 판별자(«술어가 항목마다 다르다»)는 기록돼 있으나 중재 판형과의 관계를 논급하지 않았다. 한 줄 보강 필요.

### L3. [규범식별] implementation-django-skill · s004 — +2 재계수 사유의 무근거 전제
«압축 사본의 해상도가 정본보다 낮을 수 없다»는 계약 문면 어디에도 없다(M2와 동근). 결론은 정본 s015-2.5 b2·b4·b5 / s021-3.3+s022-3.4 / s078-16.4 b1+b7 분리 채번 정합으로 독립 지지되므로 전제만 교정하면 된다.

### L4. [배선] implementation-django-ninja-skill · s004/b8 — check-business-vocabulary(#119) 인용하고 미배선
«framework-owned status 의 BC 오류 변환·광고 금지» basis가 ④로 check-business-vocabulary #119(«401·403·404·422·429·HttpError 는 framework 소유 — BC 재선언 금지»)를 인용하면서 enforcedBy에는 넣지 않았다. 정본 s023-6.2 b30의 동축 규범(«framework 오류 … framework 소유»)은 E=[check-business-vocabulary, check-api-error-controller-contract]다. 이 규범이 그 축을 접어 넣은 이상 «동일 배선» 표기가 부정확 — 병기하거나 제외 사유를 적어야 한다.

### L5. [배선] implementation-django-ninja-skill · s004/b10 — 정규화 Exception의 check-context-isolation 누락
정본 s023-6.2 b33의 합성 금지 면은 E=[check-synthetic-infra-exc, check-context-isolation]인데 skill은 synthetic-infra-exc만 배선했다. «동일 배선» 아님 — 병기 또는 사유 기록.

### L6. [배선] implementation-django-ninja-skill · s004/b13 — 저장소·retention 위임의 discipline-reviewer 누락
정본 s025-7 b8은 D=[agent-design-review-db, agent-discipline-reviewer]인데 skill 규범 «저장소·retention …의 architecture-db 결정»은 db만 배선. «동일 배선» 표기 부정확.

### L7. [배선] implementation-django-ninja-skill · s004/b15 — 정본 앵커 블록 서수 오기
#57 basis «ninja-final s030-10 b1·**s001 b2**»·#58 «ninja-final **s001 b3** Permission»은 실물과 불일치 — 해당 3규범(위임/greenfield 목표/DRF Permission)은 전부 **s001 b1**([2,13])에 산다(b2=[14,15]는 무규범). worksheet 유예 표는 b1로 옳게 적어 자기모순. basis 좌표 교정.

### L8. [재진술] implementation-django-web-skill · s001 — worksheet 유예 표 상대 좌표 오기
§3 첫 행 «s001/b2 (3) | … s001 b1 | … 21–23»에서 web-final s001 b1의 센서스 행은 **2–7**이다(21–23은 s002-1 b1의 행). 좌표 교정.

### L9. [배선] implementation-django-web-skill · s004/b4 — #589 대상 오기술
basis «check-naming #589 는 후보 채널이고 **대상은 유스케이스·도메인의 문구 호출 축**»은 #588의 서술이다. #589의 실물은 «템플릿 업무 판정 후보 — {% if %} 조건의 비교 연산·업무 어휘(Q2)» — 정확히 이 규범(템플릿의 presentation 한정)의 위반면이며, 따라서 «술어 0» 주장도 부정확하다. 비배선 결론 자체는 후보 채널(ast+ · exit 불산입)+정본 s005-4 b1 E=None으로 유지 가능 — 근거 문장만 교정.

### L10. [배선] implementation-django-ninja-skill · s004/b4 — check-test-config 배선 근거의 과장
«공개 HTTP mounted client 검증»·«공개 OpenAPI 생성 문서 검증»에 붙인 check-test-config의 docstring ⑴은 pytest↔settings **바인딩**만 검사한다(실행 전제이지 mounted 검증 자체가 아님). «결정적으로 문다»는 과장. 배선 목적지는 정본 s028-9.1 b3·s026-8 b2와 일치하므로 유지하되 근거 서술을 «실행 전제의 백스톱»으로 조정.

### L11. [배선] implementation-django-skill · s003 — 로드 조건 Coordinator 병기의 wave 간 불일치
s001/s003 로드 조건에 command-dddjango를 병기한 처분이, 기이관 discipline-tdd-skill·implementation-python-skill(D=discipline-reviewer 단독)·architecture-db-skill(D=command-dddjango+design-review-db)과 제각각이다. 이 묶음 잘못이라기보다 그래프 전역 일관성 문제 — 소급 정합 대상으로 원장/worksheet에 표시 필요. ninja·web 동형.

### L12. [규범식별] implementation-django-skill · s004/b8 — 재진술 쌍의 class 차이 미기록
«settings 직접 접근 주의» Obligation vs 정본 s022-3.4 b1 «모듈 최상위 settings 접근 회피» Prohibition. SKILL 문면 «주의»가 약형이라 Obligation 판정 자체는 성립하나, 재진술 상대와의 유형 차이를 경계 판단 메모에 기록해야 소급 패스가 오판하지 않는다.

### L13. [배선] implementation-django-skill · s004/b5 — .value 평탄화 배선의 정본 이탈 (기록은 있음 · 잔여 확인)
#18 «default= 의 .value 평탄화»에 check-choices-literal-consumption을 배선했으나 정본 s015-2.5 b4의 동명 규범은 E=None이다. worksheet §2가 사유(SKILL 불릿이 두 축 합문)를 기록해 §16 절차는 지켰으나, docstring (a)가 무는 것은 «default=리터럴»(심볼 소비 위반면)이고 «.value 미평탄화(default=Enum.MEMBER)»는 5)에서 명시적으로 비대상(비-Constant 전부 정상)이다 — 커버 주장 범위를 «리터럴 위반면 한정»으로 한정 서술 권고.

### L14. [경계kind] implementation-django-ninja-skill · s001 — 발주서 재진술 열 초과 수록의 근거 기록 위치
발주서 s001 재진술 열은 교차 문서(ninja-final s005-1.2)만 지목하는데 spec은 같은 문서 restates(→s003 b1~b5)를 추가했다. worksheet §3이 «직접 확인 후 추가»를 기록해 브리프 절차(«census restate 열 참고·직접 확인 후»)는 지켰다 — 발견이라기보다 소급 패스가 참조할 이본 기록. 처분 불요 판단이면 명시 각하로 종결 권고.

## 검증 각서 (반박 실패 항목 — 기록만)

- 블록 연속·무손실·센서스 해시: 3 spec 모두 `ontology_migrate.py` 검증 전용 exit 0 재확인(블록 37/40/34 · Work 25/64/27 — worksheet 자기 보고와 일치).
- 표 판형(머리+구분행 1블록·데이터 행 각 1블록·마지막 행 빈 줄 흡수): 파일럿 s051-8 실물([2059,2060] 병합)과 일치 — 반박 불성립.
- frontmatter 행 단위 prose/norm 분해: agent-coder s001 판례와 동형 — 반박 불성립.
- 재진술 유예 표 좌표: ninja 20행·django 9행·web 17행 전수 대조 — web s001 1건(L8) 외 전부 정본 spec 실물과 일치.
- 인용 docstring 실물 대조: transaction-boundary(#200)·broker-contract(#603·#529)·choices-literal-consumption((a)(b)·5))·test-config(⑴⑶ #445~#447)·context-isolation(#93~#95·#110·#431)·usecase-dto-placement(#208·#143/#144)·business-vocabulary(#53·#119)·error-centralization·api-error-controller-contract·openapi-error-declaration·composition-root·synthetic-infra-exc·response-schema-bypass·public-surface-annotation(#493·#358)·idempotency-scope-creep·transient-overmapping·mechanism-ownership(#336~#338·#593)·app-container(«위치 한 축»)·naming(#118·#588/#589)·ninja-boundary-middleware — M1(#96)·L9(#589) 외 전부 실물 일치.
- «술어 0» 공백 주장: 27종 로스터 대조에서 마이그레이션 무중단 순서·N+1·뷰 두께·CSRF 설정·폼 경로·로드 조건 등의 결정적 술어 부재 확인 — 반박 불성립.
- django #22(설정 환경 분리→check-test-config ⑶) 신규 배선: docstring 문면 정합·§16 도피 금지 조항 적용 타당 — 반박 불성립.

## 처분 (수리자 · 2026-08-22)

- 수리 범위: `implementation-django-skill` · `implementation-django-ninja-skill` · `implementation-django-web-skill`의 spec 3 + worksheet 3. 원문 md·`ontology/`·타 에이전트 산출물 **무변경**(git status 확인).
- 제출 검증: 3 spec 모두 `ontology_migrate.py` **검증 전용 exit 0** 재확인(`--write` 미사용) — django 블록 37·Work 25 / ninja 블록 40·Work 64 / web 블록 34·Work 27(수리 전후 계수 불변 — 배선·근거 문면만 변경).
- 판정 요약: **fixed 13 · rejected 1**(L1). 아래는 각 건의 처분과 근거 한 줄.

| # | 처분 | 근거 · 반영 위치 |
|---|---|---|
| **M1** 배선 · ninja s004/b1 «#96 담당 검사기 오인» | **fixed** | 지적 성립 — `check-context-isolation.py` docstring에 #96은 없고(#93/#94/#95뿐) #96은 `check-event-publish.py` 소유(docstring 11–13행) 실물 확인. basis를 context-isolation 실물(#93 `application_layer/port` · #94 `driven_layer` · #95 domain은 exception·값 객체만 — 진단 함수 `_apply_same_bc`의 `loc in ("api", "driving", …)` 분기가 Router 자리를 문다)로 교정. **#96 소유자 병기는 명시 심사 후 기각** — ⒜ #96은 `api_router.py`를 잎에서 제외하고(`WIRING_FILES` 실물 · #99) ⒝ 남는 겹침면(controller 잎의 `domain_layer`·port 선언 import)은 #93·#95가 이미 같은 위반면을 물어 병기가 중복 진단이 된다. 목적지는 정본 s006-1.3 b3과 그대로 일치. ninja worksheet §2 배선표 spec에서 재생성 + 심사 기록 추기 |
| **M2** 규범식별 · ninja s004 «+20 판정 전제 부실» | **fixed(부분 반박 병기)** | «해상도 낮으면 재진술 연결 불가» 전제는 지적대로 오류 — `ontology_migrate.py` 블록 루프가 `djr:restates`를 **블록→블록**으로만 세우는 실물 확인 후 **철회**. §13 대비 처분을 새 하위 절로 명시(근거 ⑴ Work가 `class` 단일값 + 소유 한 벌을 지므로 유형·소유가 갈리는 문장을 병합하면 손실 ⑵ 정본 Work와 1:1 대사 유지). **다만 «§13이 문장 이하 채번을 금지한다»는 함의는 기각** — 같은 조항이 «절 해상도»를 나란히 정의해 채번 단위가 문서·절 선택임을 보이므로 상한 조항은 계약에 없다. 관행의 문면 승격은 §7 개정 절차로 이월 |
| **L1** 재진술 · 3문서 s001 «사본 블록 Work 이중 승격» | **rejected**(spec 불변 · 이월 기록) | ⒜ §15 재진술 조항의 실물 스코프는 «축자 쌍»(조항이 파일럿 «ninja §6.2↔§2.2 축자 쌍»을 예시로 못 박음)인데 frontmatter description은 어휘·범위가 다른 압축 요약이라 일방을 «정본»으로 지정할 근거가 문서 안에 없다 ⒝ 발주서 센서스(adv 중재 확정)가 s001 규범 수 2를 명시해 사본 판형(`norms` 0)은 census 대사를 −2로 깬다 ⒞ 전 웨이브 `*-skill` 8종 동형이라 3문서만 되돌리면 비일관 확대. 리뷰 자신의 «개별 수리 말고 일괄 확정» 결론과도 일치 — 3 worksheet §5에 일괄 확정 대상으로 이월 |
| **L2** 규범식별 · web s004 «+7과 adv 중재 판형 긴장 미론급» | **fixed** | 지적 성립(판별자 기록은 있으나 중재와의 관계 미론급). web §1에 한 문단 보강 — 중재가 병합한 s001 위임 열거는 술어 하나·목적어 셋, 30행 열거는 항마다 술어가 다름(재렌더/`handler500`/503)이라 **같은 판별자의 반대편 적용**이고, 정본 s012-11 b1·b3·b5·b6이 이미 4 Work(b6만 E=`check-transient-overmapping.py` — 병합 시 배선 손실) |
| **L3** 규범식별 · django s004 «+2 무근거 전제» | **fixed** | 지적 성립 — «압축 사본의 해상도가 정본보다 낮을 수 없다»는 계약 문면에 없어 삭제. 사유를 «정본 분리 채번 정합(s015-2.5 b2·b4·b5 / s021-3.3+s022-3.4 / s078-16.4 b1+b7 / s024-4.1+ddd §3.2) + 병합 시 유형·소유 손실»로 교체 |
| **L4** 배선 · ninja s004/b8 «#119 인용하고 미배선» | **fixed** | 지적 성립 — 이 규범은 정본 b30의 세 규범(소유 E=[business-vocabulary, api-error-controller-contract] · 전환 금지 · 광고 금지)을 한 문장에 접었고 #119 실물 진단이 «BC 클래스의 `HttpError` 상속»(재선언 위반면)이라 §16 «도피 금지» 적용. `check-business-vocabulary.py` **병기**(E 3종) |
| **L5** 배선 · ninja s004/b10 «context-isolation 누락» | **fixed** | 지적 성립 — 정본 b33의 금지 규범 E=[synthetic-infra-exc, context-isolation]. 이 Exception이 허용면·금지면을 한 조문에 접었으므로 `check-context-isolation.py` **병기**(#473 ACL 기저 예외 · #291/#292 예외의 자리 · #12/#13 타 BC = «자기 BC exception이 아닌 것의 통과» 위반면) |
| **L6** 배선 · ninja s004/b13 «discipline-reviewer 누락» | **fixed(단독 유지 · 사유 기록)** | «동일 배선» 표기는 지적대로 부정확 — 정본 s025-7 b8의 discipline-reviewer 병기는 **정본 문면이 `implementation-django` 축(unique constraint·lock·transaction boundary)을 함께 지목**한 결과이고 SKILL 문면은 architecture-db 하나만 지목한다. 위임은 db 단독 유지(①문면 근거), basis를 «목적지 일부 일치»로 교정 |
| **L7** 배선 · ninja s004/b15 «정본 앵커 서수 오기» | **fixed** | 지적 성립 — ninja-final `s001 b1`([2,13])에 3규범이 있고 `b2`([14,15])는 무규범 prose임을 정본 spec 실물로 확인. basis 2건을 `s001 b1`로 교정하고 worksheet 대조표·경계 메모의 같은 오기도 함께 수리(자기모순 해소) |
| **L8** 재진술 · web §3 «상대 좌표 오기» | **fixed** | 지적 성립 — web-final `s001 b1` = 센서스 [2,7], 21–23은 `s002-1 b1`. 유예 표 첫 행 좌표를 **2–7**로 교정 |
| **L9** 배선 · web s004/b4 «#589 대상 오기술» | **fixed** | 지적 성립 — 인용된 «유스케이스·도메인의 문구 호출 축»은 #588 서술이고 #589는 «템플릿 업무 판정 후보 — `{% if %}` 조건의 비교 연산·업무 어휘(Q2)». «술어 0» 주장도 철회. 비배선 결론은 유지하되 근거를 «ast+ 후보 채널 — exit 불산입 · 마무리 discipline-reviewer + 정본 s005-4 b1 E=None»으로 교체(spec basis + worksheet 둘 다) |
| **L10** 배선 · ninja s004/b4 «test-config 근거 과장» | **fixed** | 지적 성립 — docstring ⑴은 pytest↔settings 바인딩만 본다. «결정적으로 문다» → «실행 전제의 백스톱(바인딩이 깨지면 mounted 검증이 0 collected로 조용히 사라진다)»으로 두 규범의 근거 서술 조정. 목적지는 정본 s028-9.1 b3·s026-8 b2와 동일하므로 배선 불변 |
| **L11** 배선 · 로드 조건의 wave 간 불일치 | **fixed(기록 · 배선 불변)** | 실측 3판형 확인(`architecture-*`=Coordinator+design-review-* / `discipline-*`·`implementation-python`·`-test`=discipline-reviewer 단독 / 이 묶음=discipline-reviewer+Coordinator). 이 묶음의 처분은 §16 기본값 표 2행 병용으로 문면 근거가 성립하므로 배선은 그대로 두고, 3 worksheet §5에 **소급 정합 대상**으로 이월(파생 미정리 1건 — `s005` 로드 범위 규범의 Coordinator 병기 여부도 같은 결정에 포함) |
| **L12** 규범식별 · django s004/b8 «class 차이 미기록» | **fixed** | 지적 성립 — 정본 s022-3.4 b1은 Prohibition, 사본은 Obligation. spec basis와 worksheet 경계 메모 6번에 «문면 «주의»=약형이라 Obligation · 소유는 정본과 동일 · 소급 패스가 배선 표류로 오판하지 말 것»을 명시 기록 |

- 이 처분에 포함하지 않은 항목: 원 리뷰의 **L13**(`.value` 평탄화 커버 범위 한정 서술)·**L14**(발주서 재진술 열 초과 수록의 각하 여부)는 이번 수리 발주 findings(14건)에 포함되지 않아 손대지 않았다 — 원 리뷰 본문에 그대로 남는다.
