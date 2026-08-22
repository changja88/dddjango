# T3 적대 리뷰 — implementation-test-final (spec + worksheet)

- 대상: `workspace/eval/t3/specs/implementation-test-final.spec.json` · `workspace/eval/t3/worksheets/implementation-test-final.md`
- 리뷰 방법: 4렌즈 전수 — 49절 195블록 전 블록을 원문(`dddjango/skills/implementation-test/references/final.md`, 2754행)과 기계+육안 대조. 검사기 docstring은 27종 전수 실독분 중 배선·미부착 근거에 인용된 9종(check-test-config·check-mechanism-ownership·check-choices-literal-consumption·check-idempotency-scope-creep·오류 계약 4종 등)을 코드 수준까지 직접 재확인.
- 기계 확인 결과(참고): 절 스팬·행 커버리지 = migrate 도구 exit 0 재현. kind 표면 검사(펜스/표/체크박스/무소유 norm 블록) 0건. 과대 병합(비-code 블록 내부 빈 줄) 0건. prose 블록 내 규범 표지 0건(«pytest 스타일 (권장)» 라벨 1건은 P0 미계수 승계 — 정당). basis 공란 0건 · 무소유 0건. 배선 집계(E 7·D 173)·kind 분포(83/67/39/6)·restates 4블록 모두 worksheet 자기 신고와 일치. 재진술 사본↔정본 4쌍 원문 대조 성립. 교차 문서 유예 표본 3건(#1·#11·#18) 상대 문서 실물 확인 성립(#18의 1297행은 census 좌표계 기준 — 현행 파일 1350행, marker 63행 차감분과 정합).

## 발견 (심각도순)

### F1 · medium · 배선 · s099-19.4
- **주장**: b1 두 번째 Work(«DB 필요 테스트는 django_db·db·transactional_db 로 의도 명시»)에 `check-test-config.py`를 부착한 basis(«docstring ⑵ #389 … ‹의도 명시› 부재형을 표준 트리 integration 부분집합에서 결정 적출(부분 커버)»)가 과대 주장이다. 실물 대조: `check-test-config.py` `_db_signals`(246~250행)는 `.objects` 애트리뷰트 접근을 DB 신호로 계수하므로, 이 규범의 정규 위반형(«DB를 쓰는데 마커가 없다» — `.objects`는 쓰는데 `django_db` 마커 부재)은 #389를 **통과**한다. #389가 발화하는 유일 사건(신호 전무)은 검사기 자신의 위반 메시지가 «unit/ 자리다»라고 말하는 **배치** 사건이지 의도 명시 사건이 아니다. 발주서 P0 판정도 «check-test-config #387/#389와 인접하나 동일 규칙 아님»이며, worksheet가 이 판정을 transaction=True 선택 규범에만 한정 적용한 재해석(§4 메모 8)은 P0 문면에 근거가 없다.
- **수정안**: 해당 Work의 `enforcedBy` 제거(위임 기본값만 유지 — delegatedTo는 이미 있음). basis를 유지하려면 «신호 전무 사건에서의 우연 중첩»임을 명시하고 P0 ‹동일 규칙 아님› 판정 이탈 근거를 문면으로 별도 제시해야 한다.

### F2 · medium · 재진술 · s017-3.8
- **주장**: b2(312행 blockquote «시간 모킹의 경우 monkeypatch 직접 교체 대신 freezegun/time-machine 전용 라이브러리 사용을 권장한다. (10장 참고)»)는 s055-10 b1(1320행 «시간 모킹에는 전용 라이브러리를 사용한다. monkeypatch로 datetime을 직접 교체하는 방식은 … 비권장한다»)의 **같은 문서 안 재진술**인데 restates 미연결 + 양쪽 모두 Work 승격이다(§15 «정본 1곳만 Work 승격» 위반 — 같은 규칙에 Work 2개). 문면 자체가 «(10장 참고)»로 정본을 지목하고 발주서 비고도 «(§10 참조)»를 적시했다. worksheet가 s022-4.2·s099-19.4에서는 census 계수를 거슬러 사본을 흡수한 것과 같은 사안인데 여기만 누락 — 자기 기준(«규범 내용이 실제로 옮겨 적힌 것») 위반이다.
- **수정안**: s017-3.8/b2를 Work 미승격 + `restates: ["implementation-test-final/s055-10/b1"]`로 전환하고, census 대사에 s017-3.8 1→0(P0 과대 — 사본) 사유 행 추가(합계 173→172).

### F3 · medium · 재진술 · s076-15.2
- **주장**: b1 넷째 Work(«하나의 승인 행위를 검증하는 관련 assert 허용» — 1981행 «논리적으로 하나의 승인 행위를 검증하는 관련 assert는 허용한다»)와 b6 Work(«동일 Act 의 관련 assert 동거 허용» — 2004행 «논리적으로 하나의 행위를 검증하는 여러 assert는 같은 테스트에 둘 수 있다»)는 같은 규칙의 절 내 이중 서술인데 양쪽 모두 Permission Work로 승격됐고 restates 미연결이다. 저자가 s099-19.4에서 흡수한 사본(§20.3과의 paraphrase 수준 중복)과 같은 등급의 중복이다.
- **수정안**: 정본 1곳(핵심 규칙 3항 = b6가 규칙 진술, b1은 도입 요약 — 또는 그 역을 근거와 함께) 판정 후 사본 쪽 Work 미승격 + restates 연결, census 대사 사유 행 추가. 흡수하지 않는 선택을 유지하려면 두 문장이 별개 규범인 문면 근거(예: b1은 AAA 채택 조건절의 일부)를 worksheet §4에 명시할 것.

### F4 · low · 배선 · s098-19.3
- **주장**: b2 둘째 Work의 기본값 이탈(`agent-design-review-api`) 근거로 worksheet(76행)가 «문면이 다른 문서군을 **직접 지목**한 4건»에 포함시켰으나, 실제 문면(2477행)은 «권한/페이지네이션/필터링 계약이 불명확하면 API 설계를 먼저 확정한다»로 **문서명을 지목하지 않는다**(§20.1의 «architecture-api»·«architecture-db», §20.5의 «architecture-db §9.5»와 등급이 다르다). 이탈 자체는 «API 설계» = architecture-api 국면이라는 간접 추론으로 옹호 가능하나, «직접 지목» 서술은 부정확하다.
- **수정안**: worksheet 76행의 근거 서술을 «간접 지목(국면 지시)»로 정정하거나, 기본값(`agent-discipline-reviewer`) 복귀 후 소급 패스에서 재론.

### F5 · low · 배선 · s105-20.5
- **주장**: b6 «연결 튜닝은 stock OPTIONS 한정»(Obligation)에 부착한 `check-mechanism-ownership.py`는 인접 Work(«커스텀 DatabaseWrapper·DB 백엔드 구현 금지»)와 **같은 검사기 사건**(비-stock ENGINE + DatabaseWrapper 서브클래스 AND 게이트)의 재부착이다. 이 Work 고유의 위반형(커스텀 백엔드를 만들지 않고 stock OPTIONS 화이트리스트 밖 튜닝 — 예: conftest PRAGMA — 은 §4 메모 자인대로 conftest 운반체 미포착)은 ⑴이 잡지 못한다. 저자 스스로 총론 문장(b6 첫 Work)에는 «이중 계수 방지»로 미부착했으면서(메모 9) 이 Work에는 부착해 방침이 비일관하다. 다만 «stock/비-stock의 경계선이 문면과 같은 선»이라는 근거가 공개돼 있어 오배선 단정까지는 못 간다.
- **수정안**: 부착 유지 시 basis에 «인접 금지 Work와 동일 사건의 경계 공유»임을 명시, 또는 제거하고 위임 단독으로.

### F6 · low · 규범식별 · s029-6.2
- **주장**: class 부여 비일관 2계열. ① «권장» 문장: s017-3.8(«권장한다»)은 Obligation, s029-6.2 b5·b6(«권장»)은 Permission, s105-20.5 b5(«안정적이다» 권장 취지)는 Permission — 같은 연성 지침 표지가 절마다 다른 class다. ② 소유 절연문: s033-7 b1(«§7.1 불변 소유»)·s075-15.1 b9(«discipline-tdd가 다룬다»)는 Override, 동형의 s007-1.4 b1·s078-15.4 b3·s105-20.5 b4·s106-21 b1(«…가 소유한다/영역이다/참조한다»)은 Obligation. 브리프에 rubric이 없어 각 건은 방어 가능하나 문서 내 일관성이 없다.
- **수정안**: worksheet §4에 «권장→class»·«소유 절연문→class» 판정 기준 한 줄씩 명문화하고 그 기준으로 재대조(변경이 나오면 spec 반영).

### F7 · low · 규범식별 · s027-6
- **주장**: 말미 문장(538행 «핀 표기·매니페스트 위치는 implementation-django §3.1·implementation-django-ninja §2.1 소유»)을 «P0 계수 밖(소유 포인터)»으로 미계수했는데, 동형의 소유 포인터 문장이 s106-21(«implementation-python 스킬을 참조한다»)·s078-15.4 b3·s105-20.5 b4에서는 Work로 계수됐다. census 승계 자체는 계약 준수이나, worksheet는 census 과소 산정을 정정할 권한·의무가 있고(브리프 «과소/과대 어느 쪽이 옳은지 판정 포함») 이 비일관에 대한 판정이 없다.
- **수정안**: worksheet §1 s027-6 행에 «동형 문장 계수 비일관은 P0 유래 — 소급 패스 회부» 판정을 명기하거나, 4번째 Work로 계수하고 불일치 사유 행 추가.

### F8 · low · 배선 · s022-4.2
- **주장**: b1 넷째 Work(«테스트 의미군 위치의 단일 출처는 discipline-houserules §2»)에 `check-test-config.py` 부착 — 이 규범의 내용은 «출처 지정»(어느 문서가 정본인가)이지 트리 준수가 아니다. 검사기는 참조 **대상**(트리 105~111행)을 집행할 뿐 «단일 출처» 선언 자체의 위반형(예: 다른 문서에 트리를 중복 서술)은 판정 밖이다. P0 비고도 이 절 고유 규범을 «비커버»로 판정했다.
- **수정안**: enforcedBy 제거(위임 단독) 또는 basis에 «참조 대상 트리의 백스톱이지 출처 선언의 집행이 아님(간접 커버)»을 명시.

## 지적하지 않은 것 (검토 완료 — 무혐의 근거)

- **표 전체 1블록**(s004-1.1 b9·s008-2 b2·s034-7.1 b2): 브리프 «행 단위» 문면과 긴장이 있으나 wave-1 확립 판례(implementation-django-final §14.1·implementation-python-final s111-19.6) 계승으로 판단 — 파일럿 ddd s051-8(행별 의사결정 표)과는 사안이 다르다.
- **§15.4 8건 미부착**: `check-choices-literal-consumption` docstring 3) 면제 조항 실독으로 «인용≠집행» 판단 확인 — 정당한 오배선 방지.
- **§19.2.x 22건·§20 도입 D2**: 오류 계약 4종·idempotency-scope-creep의 docstring·코드(«프로덕션(test 제외)») 실물 확인 — 판정 축 불겹침 성립.
- **s022-4.2·s099-19.4 census 불일치 2건**: 사본 원문 대조로 재진술 흡수 판정 타당(P0 과대 산정 판정 동의).
- **s021-4.1 ⑴ 부착·s049-9.1 #391/#392 부착**: P0 커버 판정 + docstring 축 정확 일치.
- **기본값 이탈 s101-20.1 2건·s105-20.5 1건**: 문면이 문서명 직접 지목 — L-F 중재 준거 성립.
- **경계·kind 표면 전수**(펜스 2개 규칙·표 행·체크박스·blockquote 마커 귀속·절 말미 `---` 흡수·내부 빈 줄): 기계 검사 0건.

## 종합

행 커버리지·kind 표면·census 대사·배선 집계·재진술 4쌍은 전건 성립하고 worksheet의 자기 신고와 실물이 일치한다. 남는 결함은 판단 레인 3건(medium): #389 배선의 근거 과대(F1)와 같은 문서 안 재진술 2쌍 미연결(F2·F3). 셋 다 spec 국소 수리(enforcedBy 1건 제거·restates 2건 연결·census 사유 2행)로 해소 가능하다.

---

## 처분 (수리자 기록 — 2026-08-22)

수리 대상: `workspace/eval/t3/specs/implementation-test-final.spec.json` · `workspace/eval/t3/worksheets/implementation-test-final.md`. 자기 검증 `ontology_migrate.py`(--write 없음) **exit 0** 재확인 — Work 173 → **172**(재진술 흡수 −4 · 과소 산정 정정 +1) · restates 블록 4 → **6** · enforcedBy 링크 7 → **4**.

| # | 처분 | 근거 |
|---|---|---|
| F1 · s099-19.4 | **fixed**(제거) | 코드 실물 확인 — `_db_signals`(246~250행)가 `.objects` 를 DB 신호로 계수해 정규 위반형(`.objects` + 마커 부재)이 #389 를 통과하고, #389 발화 사건(신호 전무)의 검사기 자기 메시지는 «unit/ 자리다»(배치)다. 지적대로 «결정 적출» 주장이 성립하지 않으므로 `enforcedBy` 제거 + P0 «인접하나 동일 규칙 아님»을 절 전체에 승계(basis·worksheet 메모 8 재작성). |
| F2 · s017-3.8 | **fixed** | 312행 인용구는 §10 도입(1320행)의 재진술이고 문면 «(10장 참고)»·발주서 «(§10 참조)»가 정본을 지목한다 — b2 Work 미승격 + `restates:[…/s055-10/b1]`, census 1→0 «P0 과대» 사유 행 추가. |
| F3 · s076-15.2 | **fixed**(정본 = b6) | 1981행과 2004행은 같은 규칙의 절 내 이중 서술이 맞다. 정본은 **핵심 규칙 3항(b6)** — 1·2항이 각각 Work인 병렬 항목이고 도입 문장은 첫 문장이 예고한 세 기준의 요약이다. «승인» 한정은 b1 첫 Work(recipe 절연)가 이미 운반해 의미 손실이 없다. b1 Work 4→3 + `restates:[…/s076-15.2/b6]`, census 7→6 사유 행. |
| F4 · s098-19.3 | **fixed**(서술 정정·이탈 유지) | 2477행에 문서명이 없다는 지적이 맞다. worksheet 근거를 «직접 지목 4건»→«직접 3건 + 국면 지시(간접) 1건»으로 정정하고 spec basis에도 등급 차를 명시. 국면이 §16 표의 architecture-api 와 1:1이라 이탈 자체는 유지하고 등급 차는 소급 패스 재론 대상으로 기록. |
| F5 · s105-20.5 b6 | **fixed**(제거) | ⑴은 AND 게이트라 조건 3(DatabaseWrapper 서브클래스)이 서야 발화하므로 발화 사건은 인접 금지 Work의 위반형 그 자체이고, 이 Work 고유의 위반형(백엔드 비경유 비-stock 튜닝)은 미발화 — 저자 자신의 «이중 계수 방지»(메모 9) 방침대로 `enforcedBy` 제거. P0 «⑴ 부분 커버»는 인접 금지 Work에 계상돼 유지된다. |
| F6 · class 비일관 | **fixed**(rubric 명문화 + 재대조 2건 변경) | worksheet §4 메모 13에 두 rubric을 고정: «권장/고려»=Permission·«비권장»=Prohibition · 자기 범위 한정 주절=Obligation · 관할 이전 주절=Override · «따른다/참조한다»=Obligation. 재대조 결과 «권장» 계열은 F2로 유일 이탈(s017-3.8)이 사라져 spec 변경 0, 소유 계열은 s078-15.4 b3 경계②·s105-20.5 b4 를 Obligation→**Override**로 변경하고 s106-21 b1 라벨을 문면 동사(«참조한다»)에 맞춰 정정했다. |
| F7 · s027-6 | **fixed**(계수) | 동형 소유 이전문이 s078-15.4 b3·s105-20.5 b4·s106-21 b1 에서 계수된 이상, F6 rubric ⓑ를 적용하면 538행 말미 문장도 Work다 — «P0 과소 산정»으로 판정해 **4번째 Work(Override)** 신설 + census 불일치 사유 행 추가(회부 대신 정정 선택 — 브리프가 과소 산정 판정을 워크시트 의무로 두었다). |
| F8 · s022-4.2 | **fixed**(제거) | 검사기는 참조 **대상** 트리(#383~#392)를 집행할 뿐 «출처가 어디인가»의 위반형(다른 문서의 트리 중복 서술·타 출처 준거)은 판정 밖이고, 그 사건은 같은 블록 인접 Work에 이미 계상됐다 — 경유 커버라 `enforcedBy` 제거(P0 «이 절 고유 규범은 비커버»와도 정합). |

**rejected 0건.** 다만 F4·F5·F6·F7은 지적이 제시한 두 선택지 중 한쪽을 골랐고(F4 서술 정정·F5 제거·F6 rubric 명문화·F7 계수), F1·F5·F8의 공통 판단 기준은 worksheet §4 **메모 14(경유 커버 미부착 정책)**로 명문화해 다음 웨이브가 같은 선을 재현할 수 있게 했다. F3의 정본 방향은 지적이 «근거와 함께 판정»을 요구한 대로 b6으로 확정하고 근거를 §1·spec basis 양쪽에 남겼다.
