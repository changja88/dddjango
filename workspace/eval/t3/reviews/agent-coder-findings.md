# T3 적대 리뷰 — agent-coder (spec + worksheet) · 라운드 2 (수리 후 재검)

- 대상: `workspace/eval/t3/specs/agent-coder.spec.json` · `workspace/eval/t3/worksheets/agent-coder.md`
- 대조 재료: `workspace/eval/t3/T3-authoring-brief.md` · `workspace/eval/t3/orders/agent-coder.md` · `dddjango/agents/coder.md`(현재 71행 — 발주서·센서스 일치 실측) · `dddjango/scripts/check-*.py` 27종 docstring 전수 실독 + 쟁점 검사기 구현 grep 실측 · `workspace/tools/ontology-authoring.md` §13~§16 · 상대 문서(acceptance-tester 전문 실독·discipline-reviewer·design-review-api) 좌표 grep 실측
- 검사 방식: 4렌즈 전수 절 검사(표본 아님). 원문 71행 전 문장 독립 재계수 → spec 123 Work 대조 · migrate 검증 재실행(exit 0 재확인 — 블록 45·Work 123) · worksheet 배선 표 123행 ↔ spec 123 norm 기계 대조(스크립트) · 재진술 상대 문서 축자 grep.
- 판정: **fail** — high 1건 · medium 6건 · low 6건.

## 라운드 1 수리 상태 대사

| R1 | 상태 | 근거 |
|---|---|---|
| F-1 (#40 enforcedBy 허위) | **spec 수리됨 · worksheet 미수리** | spec #40 enforcedBy 공란 + basis «비커버 증거» 명기 ✓ — 그러나 worksheet 표 #40행은 여전히 `check-test-config.py` 배선 + 커버 취지 basis(→ R2-3) |
| F-2 (#117 과대) | 미수리 | spec 불변(→ R2-6) |
| F-3 (#88·#105 오배선) | 미수리 | spec 불변(→ R2-5) |
| F-4 (#73 공백 미기록) | 미수리 | spec 불변(→ R2-7) |
| F-5 (#14·#37 ⓓ 병기) | **#14만 spec 수리 · worksheet 미수리 · #37 방치** | spec #14 ⓓ 병기 + basis 확장 ✓ — worksheet 표 #14행은 구판(→ R2-3), #37은 spec도 그대로(→ R2-8) |
| F-6~F-10 (low 5건) | 미수리 | 전부 잔존(→ R2-10·R2-12·R2-13 등) |

## 검증 통과 확인 (전수 검사 무결 축)

- ① 경계·kind: 원문 코드 펜스·표·체크박스 0 실측 — norm/prose 2종 판정 타당. 전 절 `line_start+1` 개시·연속·비중첩·후행 공백 귀속(§13) — migrate 재실행 exit 0으로 기계 재확인. 프론트매터 행 단위 분해(`skills:` 키+목록 8행 1블록 병합 포함)·description(3행)만 norm 처분·s001 headingSnapshot=1행 `---` 처분 모두 타당. 블록 과대 병합 없음.
- ② 규범 식별: 독립 재계수 s001=4·s002=2·s003=4·s004=97·s005=4·s006=12 = **123, spec과 전건 일치**. 발주서 105(s004=82·s006=9)는 과소가 맞다는 worksheet 판정에 동의(§13 문장 해상도). Permission 1(50행)·Override 4(40·49·56×2행) 자리 부합. 잔여 쟁점은 R2-9·R2-10(low).
- ③ 배선(무결 확인분): #106의 «#107·#108·#109·#111 = check-composition-root 실장» — `rule="#10x"` 태그 실측 ✓. #110(check-context-isolation docstring 기타 군) ✓. #116 인용(coder 명시 지목·4-AND) 축자 ✓. #30·#47의 오배선 회피(검사 공백 판정) — 해당 docstring 실독으로 지지 ✓. #74의 «무인자 생성 축»은 docstring 문면엔 없으나 **구현 실측으로 성립**(`check-error-centralization.py` L3564 «concrete field must have a no-arg default» — R1 F-8은 실질 해소, 근거 표기만 ②→실장 확인으로 고치면 족함). #84 carveout — `check-response-schema-bypass.py` L1025 «File/stream/redirect and schema-less 204 paths remain framework-native carve-outs» 실측 ✓. #92·#77·#98의 header/two-arg Status 술어 — controller-contract 구현(`_header_assignment_valid`·L7126) 실측 ✓. #123 한정 커버 문면 ✓. «27종 술어 0» 계열 전건 — 27종 전수 대조 반증 없음 ✓.
- ④ 재진술(무결분): spec `restates` 0 = 교차 문서 전량 유예 계약(브리프·T3-EXECUTION) 준수 ✓. 발주서 재진술 열 3건 전부 유예 절 수록 ✓. 8·9번(기이관 상대) 유예 동반 처분도 T3-EXECUTION 결정 준수 ✓. 기존 13건의 상대 좌표 실측 일치 ✓. 단 **목록 완결성이 깨져 있다** — R2-1·R2-2.

## 발견 (심각도순)

### R2-1 [high · 재진술] s004/b13 (45행) — acceptance-tester 45행과의 **전 불릿 byte-축자 사본** 쌍 유예 누락

- **주장**: coder 45행 «이번 실행의 Red만 위해 만든 loader/dynamic import guard/대체 decorator/skip/xfail/helper는 해당 surface의 첫 Green 직후 네가 제거한다. 작업 전부터 있던 비계를 이번 실행이 만든 것으로 간주해 임의 삭제하지 않는다.»는 `agent-acceptance-tester` 45행과 **두 문장 전체가 문자 단위로 동일**하다(grep 실측 — 마커·기이관 없음, 현재 행=센서스 행). 파일럿이 재진술의 전형으로 삼은 «축자 쌍»의 최상급 사례인데 worksheet «재진술 유예» 절(13건)에 없다. 유예 목록은 T3 소급 연결 패스의 유일한 재료라 누락 = 그래프 연결 영구 누락 위험이다.
- **수정안**: 유예 목록에 «s004/b13 (45행) → agent-acceptance-tester/s004 (45행) — 전 불릿 축자 사본(2문)» 추가.

### R2-2 [medium · 재진술] s004·s006 — acceptance-tester 상대 병렬 4건 추가 누락 + item 13 좌표 미기재

- **주장**: 상대 문서 전문 실독 결과 유예 목록에 빠진 병렬 쌍이 더 있다. ⑴ coder 39행 2문 «지원 중인 구 API·영속 데이터·발행 이벤트·회귀 불변식은 보존한다» ↔ AT 31행 «…오래됐다는 이유로 삭제하지 않는다» — 동일 4항 열거의 긍정/부정면(item 6은 39행 1문↔30행만 수록). ⑵ coder 46·47행 12-slot preflight·`STOP_FOR_USER_APPROVAL` ↔ AT 37행(«일반 G1과 분리된 명시적 사용자 shape-승인 evidence … STOP_FOR_USER_APPROVAL로 반송» 공유) — item 7이 «3자 병렬»(architect↔api↔coder)로 적었으나 실제 4자다. ⑶ coder 55행 mounted full client OpenAPI 검증·controller-only 대체 금지 ↔ AT 41행. ⑷ coder 53·56행 «함수형 Router 발명/신규 강제 금지» ↔ AT 46행 «함수형 `Router`를 강제하지 않는다». 덧붙여 item 13은 상대 좌표를 «(경계 절)»로만 적어 행 좌표 규약(자기 선언)을 어겼다(실측: AT 49행).
- **수정안**: 유예 목록에 4건 추가, item 7을 4자 병렬로 정정(AT/s004 37행 병기), item 13에 행 좌표(49행) 기입.

### R2-3 [medium · 배선] worksheet 배선 근거 표 #14·#40행 — 수리된 spec과 불일치(구판 잔존)

- **주장**: 기계 대조(표 123행 ↔ spec 123 norm) 결과 두 행이 spec 실물과 다르다. **#40**: 표는 enforcedBy=`check-test-config.py`·delegatedTo=command 단독·basis «검사기가 같은 관례 경계를 명시 취급»(커버 취지)인데, spec은 enforcedBy 공란·ⓓ 병기·basis «비커버 증거» — 정반대 서술. **#14**: 표는 delegatedTo=command 단독인데 spec은 ⓓ 병기 + basis 확장. R1 수리가 spec에만 반영되고 검수표가 방치된 형태다. 브리프가 요구하는 «배선 근거 표 — 전 규범»은 wiring의 저작 근거 기록인데, 실물과 다른 기록은 감사 기능을 잃는다.
- **수정안**: worksheet 표 #14·#40행을 spec 현행 값·basis로 갱신(§1 census 대사·§4 메모의 관련 서술도 함께 — «기본값 이탈 근거 3계열» 항의 40행 서술 포함).

### R2-4 [medium · 배선] s004/b17·b21 (49·53행) — #70·#89 basis의 «profile 무관 실행» 주장이 check-composition-root lane 계약과 모순

- **주장**: check-composition-root docstring은 «**명시적 `dddjango-code-json` lane**은 선택 API object, canonical BC registrar, project URLconf의 직접 import provenance와 exactly-once 호출 관계를 함께 검사한다. **preserve/auto에서는 이 의미 검사를 적용하지 않되**…»라고 명시한다 — 즉 registrar provenance·exactly-once(#107~#109·#440) 검사는 code-json lane 한정이고, positional/preserve 실행에서 profile 무관으로 도는 것은 DI 레인(#497 단일 파일 모양)뿐이다. 그런데 #70 basis는 «④네 축 소유 검사기가 profile 무관 실행: … **#107~#109(composition-root)** …», #89 basis는 «composition-root 의 registrar/URLconf provenance·exactly-once 검사와 #110/#431 이 **profile 무관 실행**되어 답습 산출물이 곧 위반»이라 적었다. 두 규범 모두 preserve 맥락 규범이라(«preserve 가 보존하는 것은…»·«preserve native 범위…») 정확히 그 lane에서 백스톱이 꺼지는데 켜져 있다고 주장한 셈이다. 같은 spec의 #85 basis가 lane-gated 인용문을 그대로 싣고 있어 자기 모순이기도 하다. (#110·#431의 context-isolation 절반과 layer-skeleton·test-config 절반은 실제 profile 무관 — 주장 전체가 아니라 composition-root 레그가 허위.)
- **수정안**: #70·#89 basis에서 composition-root 레그를 «code-json lane 한정 — preserve 실행은 DI 레인(#497)만»으로 정정하고 preserve 면 부분 공백을 명기(enforcedBy 유지 여부는 정정된 근거로 재판단 — context-isolation·layer-skeleton·test-config 레그는 유지 가능).

### R2-5 [medium · 배선] s004/b21·b24 (53·56행) — #88·#105 «함수형 Router 발명·강제 금지»의 check-ninja-boundary-middleware 오배선 (R1 F-3 잔존)

- **주장**: 이 검사기의 유일 술어는 «driving 층 자가 정의 미들웨어의 전역 `settings.MIDDLEWARE` 자가등록»이다(docstring 판정 절 실독 — Router 관련 술어 0). 함수형 `Router`의 발명·강제는 MIDDLEWARE를 건드리지 않으므로 이 술어에 **구조적으로 발화 불가**하다. basis의 docstring 인용(«django-ninja 는 협상/임의 status 를 경계 안에서 네이티브로 낸다 §6.3»)은 rationale 문장이지 담당 술어가 아니며, «같은 축»은 동기 공유이지 §16이 요구하는 집행 커버가 아니다. 미커버 병기도 없다.
- **수정안**: #88·#105 enforcedBy 제거(§16 기본값 + design-review-api 병기 유지), 또는 basis에 «미들웨어 자작 변종 한정 인접 커버 — Router 형태 자체는 검사 공백» 명기.

### R2-6 [medium · 배선] s006/b3 (69행) — #117 «stock OPTIONS 한정»의 enforcedBy 과대 (R1 F-2 잔존)

- **주장**: check-mechanism-ownership ⑴의 AND-1은 «DATABASES **ENGINE**이 stock이 아님» — 커스텀 백엔드 교체형 한 가지만 관찰한다. 문면이 같은 위반으로 열거한 형태(`OPTIONS.init_command` 주입·`isolation_level` 조작·`connection_created` 시그널·몽키패치·conftest 패치)는 ENGINE이 stock인 채 일어나 전부 통과한다(구현 grep 재실측: OPTIONS/init_command 술어 0 — `isolation_level`은 커스텀 백엔드 모듈의 마커 목록에만, L171 «stock OPTIONS 로만 튜닝한다»는 위반 메시지 문구). «연결 튜닝의 stock OPTIONS 한정» 의무 자체는 기계 미커버인데 basis는 «stock 이탈 축을 결정적으로 집행»이라 주장한다.
- **수정안**: basis를 «ENGINE 교체형 한정 부분 커버 — OPTIONS 의미 주입·시그널·패치 형태 미커버»로 정정(#116 basis가 이미 같은 한계를 명기한 판형 준용), 또는 enforcedBy 제거.

### R2-7 [medium · 배선] s004/b17 (49행) — #73의 preserve 면 검사 공백 미기록·병기 누락 (R1 F-4 잔존)

- **주장**: enforcedBy 두 검사기 모두 이 규범의 본거지(preserve 불릿)에서 자기 비집행을 문면 선언한다 — transient-overmapping 인용문 «이 checker가 발화하지 않아도 새 handler/recognizer를 만들 근거가 되지 않는다»는 «내 비발화를 근거로 삼지 마라»는 비집행 선언이고, controller-contract는 preserve 실행에서 «add no new error-mapping semantics»다. code-json 면에서만 presentation-helper 차단이 걸리는데 basis에 preserve 면 공백 병기가 없고, 같은 불릿의 preserve 규범들과 달리 delegatedTo가 command 단독이다.
- **수정안**: basis에 «preserve 면 검사 공백 — code-json 면만 controller-contract 커버» 명기 + `agent-design-review-api` 병기.

### R2-8 [low · 배선] s004/b8 (40행) — #37 delegatedTo ⓓ 미병기 (R1 F-5 잔여 반쪽)

- **주장**: R1 F-5의 #14는 수리됐으나 #37(«factory_boy 기본·VO/dataclass 직접 생성»)은 여전히 command 단독이다. basis의 커버(#392·#388)는 재료 «배치» 축뿐이고 «ORM 영속 픽스처엔 factory_boy가 기본»이라는 선택 규율 축은 미커버 — 같은 불릿의 #35·#36·#38·#39는 전부 ⓓ 병기다.
- **수정안**: #37 delegatedTo에 `agent-discipline-reviewer` 병기, 또는 단독 처분 근거를 basis에 명기.

### R2-9 [low · 규범식별] s005/b2 (61행) ↔ s006/b2 (68행) — 동형 «금지+보고» 쌍의 비대칭 채번

- **주장**: 61행 «임의로 고치지 않고 보고한다(인수테스트/설계로 반송)»는 1 Work로 병합했는데, 68행 «설계 명세를 바꾸지 않는다 — 필요하면 보고한다»는 2 Work(#114·#115)로 분리했다. 둘 다 한 행의 «금지 + 별개 행위(보고/반송)» 구조로, worksheet 자신의 분리 기준 ⑵(규범 유형이 갈릴 때 분리)를 적용하면 61행도 분리 대상이고, 병합 판형(63행 «보고 정직성 한 축»)을 적용하면 68행도 병합 대상이다. s006 census 초과분(+3) 중 1건이 이 분리에 기댄다. 어느 쪽이든 방어 가능해 low.
- **수정안**: 두 자리 처분 통일(분리 또는 병합) + census 대사 사유 갱신. 분리 시 s005=5로 대사표 정정.

### R2-10 [low · 규범식별] s004/b10 (42행) — «관찰 전용이며 판정·평가에 쓰지 않는다» 미채번 (R1 F-6 잔존)

- **주장**: pytest 수치의 «판정·평가 사용 금지»는 #50(기재 의무)·#51(수치 축소 생략 금지)과 행위 주체·대상이 갈리는 금지면이다. 수취인이 Coordinator 측이라 #50의 한정어로 병합한 처분도 방어 가능해 low 유지.
- **수정안**: Prohibition 1건 추가 채번, 또는 계수 규율 절에 병합 사유 한 줄.

### R2-11 [low · 배선] s004/b18~b20 (50~52행) — basis의 «②파일럿 §6.2 동형»은 4원 밖 근거 유형

- **주장**: #75·#76(부분)·#77·#78·#79·#80·#81 basis가 파일럿 spec 판형과의 동형성을 ②(docstring § 인용) 자리에 적었다. 4원은 ①문면 역할명 ②docstring ③P0 커버 ④registry #N이고 «파일럿 선례»는 어디에도 없다. 실물 커버 자체는 구현 실측으로 성립한다(controller-contract의 constructor keyword·two-arg `Status`·`_header_assignment_valid` 술어 실재)이라 배선 유지에는 지장이 없고 표기 문제만 남는다.
- **수정안**: 해당 basis의 근거 유형 표기를 실장 확인(또는 §16 «controller checker» 역할명 = ①)으로 정정.

### R2-12 [low · 배선] s004/b23 (55행) 등 — #98 장식성 enforcedBy·심사판 병기 스타일 불일치 (R1 F-7·F-9 잔존)

- **주장**: #98은 자기 축(«mounted client 도달의 테스트 증명»)이 전부 미커버라 basis가 자인하는데 enforcedBy를 달았고(동종 #44는 공란), #81·#83은 «동상» 근거인데 #78·#82와 달리 review-api 병기가 빠진다. 실질 오배선은 아님.
- **수정안**: 전 축 미커버 시 enforcedBy 공란으로 통일하거나 병기 기준을 §4 메모에 명문화.

### R2-13 [low · 재진술] 33↔69행·53↔56행 same-doc 병렬 쌍의 비-재진술 사유 미기록 (R1 F-10 잔존)

- **주장**: 69행이 «구조 결정이 빠졌을 때와 똑같이»로 33행을 명시 준용하고 53↔56행이 강제 전파 금지의 자기판단/명세복종 두 채널로 대칭인데, «비-재진술로 판정해 뺀 것» 목록에 두 쌍이 없다. 별개 규범 판정 자체는 타당해 보여 low.
- **수정안**: 비-재진술 목록에 두 쌍 사유 한 줄씩 추가.

## 종합

경계·kind와 계수는 재검에서도 견고했다(123 Work 독립 재계수 일치 · migrate exit 0 재확인). 이번 라운드의 새 결함은 두 갈래다: ⑴ **재진술 유예 목록의 완결성 붕괴** — byte-축자 전 불릿 사본(45행↔AT 45행)을 포함해 acceptance-tester 상대 5건이 빠졌다(R2-1·R2-2). 라운드 1의 «유예 좌표 실측»이 표본 확인에 그쳐 놓친 자리다. ⑵ **수리의 반쪽 반영** — spec만 고치고 검수표를 방치했고(R2-3), R1 medium 3건(R2-5·R2-6·R2-7)은 수리되지 않은 채 남아 있다. 추가로 composition-root lane 계약과 모순되는 «profile 무관» basis 2건을 새로 확인했다(R2-4). spec·worksheet는 수정하지 않았다.

## 처분 (수리자 기록 · 2026-08-22)

- 반영 대상: `workspace/eval/t3/specs/agent-coder.spec.json`(Work 123 → **124**) · `workspace/eval/t3/worksheets/agent-coder.md`
- 재검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-coder.spec.json` → **exit 0**(블록 45 · Work 124 · `--write` 미사용)
- 집계: **fixed 12 · rejected 1**
- **번호 규약**: 아래 표의 `#N` 은 이 리뷰가 쓴 **수리 전 123 채번** 기준이다. R2-10 으로 42행에 1건이 삽입돼 수리 후 검수표에서는 구 #51 이후가 전부 +1 이동한다(구 #81→#82 · 구 #83→#84 · 구 #98→#99 · 구 #116→#117 · 구 #117→#118). 구 #50 이하(#14·#35·#37·#44 등)는 불변이다.

| R2 | 처분 | 근거 |
|---|---|---|
| R2-1 (high · 45행 축자 사본 유예 누락) | **fixed** | `[ "$(awk NR==45 coder.md)" = "$(awk NR==45 acceptance-tester.md)" ]` 로 문자 단위 동일 실측 확인 — 유예 표 14번으로 추가 |
| R2-2 (AT 상대 병렬 4건·item 7·item 13) | **fixed**(좌표 1건 정정 후) | ⑴39행 2문↔AT 31행 ⑶55행↔AT 41행 ⑷53·56행↔AT 46행을 15·16·17번으로 추가 · ⑵item 7 을 4자 병렬로 정정(AT/s004 37행 병기 — 46·47행 양쪽에 걸침). **item 13 좌표는 지적의 «AT 49행»이 아니라 51행이 맞다** — 49행은 s005 헤딩 라인이고 표의 다른 항이 모두 «규범 행»을 적으므로(AT s003=21행 등) 규범 행 51행으로 기입 |
| R2-3 (worksheet #14·#40 구판 잔존) | **fixed** | 두 행이 spec 실물과 불일치함을 기계 대조로 확인. 개별 행 수정 대신 **§2 표 전체를 spec JSON 에서 기계 생성**하도록 바꿔 재발 경로를 닫았다(생성 결과 ↔ spec 124 norm byte 일치 확인) · §4 «기본값 이탈 3계열»·«오배선 회피» 항의 관련 서술도 현행화 |
| R2-4 (#70·#89 «profile 무관» 허위) | **fixed** | docstring «preserve/auto 에서는 이 의미 검사를 적용하지 않되» + 구현 실측(`main()` 이 `config.profile == "dddjango-code-json"` 일 때만 `_composition_semantics` 호출)으로 지적 성립. 두 basis 의 composition-root 레그를 «DI 레인(#497)만 profile 무관 · provenance/exactly-once(#107~#109·#111·#440)는 code-json 한정 → preserve 면 부분 공백»으로 정정. 나머지 세 레그는 유지 — `check-layer-skeleton`·`check-test-config` 는 `--error-profile` 인자 자체가 없고 `check-context-isolation` 은 docstring 이 «수용하되 무시»라 실제로 profile 무관(실측) |
| R2-5 (#88·#105 ninja-boundary-middleware 오배선) | **fixed** | 구현·docstring 실독 — 유일 술어는 `driving_layer` 자가 정의 미들웨어의 `settings.MIDDLEWARE` 자가등록이고 Router 술어 grep 0. 인용문은 rationale 이지 담당 술어가 아니므로 **enforcedBy 제거**(§16 기본값 + `agent-design-review-api` 병기 유지) 후 basis 에 «미들웨어 자작 변종 한정 인접 커버 — Router 형태는 검사 공백» 명기 |
| R2-6 (#117 stock OPTIONS 과대) | **fixed** | grep 재실측 — `OPTIONS`/`init_command` 술어 0, `isolation_level` 은 AND-3 커스텀 백엔드 모듈의 `SEMANTIC_MARKERS` 목록에만, L171 은 위반 «메시지» 문구. basis 를 «ENGINE 교체형 한정 부분 커버 — OPTIONS 의미 주입·시그널·몽키패치·conftest 패치 미커버»로 정정(#116 판형 준용, enforcedBy 는 유지) |
| R2-7 (#73 preserve 면 공백 미기록) | **fixed** | transient-overmapping 인용문이 비집행 선언이고 그 주어가 `dddjango-code-json` 임을 확인 · controller-contract 는 preserve 에서 «add no new error-mapping semantics». basis 에 «preserve 면 검사 공백 — code-json 면만 커버» 명기 + `agent-design-review-api` 병기 |
| R2-8 (#37 ⓓ 미병기) | **fixed** | #392·#388 커버는 픽스처 «재료 배치» 축뿐이고 «ORM 영속 픽스처의 기본이 factory_boy 인가»라는 선택 규율 축은 27종 미커버 — 같은 불릿 #35·#36·#38·#39 와 동일하게 `agent-discipline-reviewer` 병기 |
| R2-9 (61행 ↔ 68행 비대칭 채번) | **rejected** | **두 자리는 동형이 아니다.** 61행 «임의로 고치지 않고 보고한다»의 «-지 않고»는 연결어미로 물린 **방식 한정 부사절**이라 종결절이 1개고, 68행 «바꾸지 않는다 — 필요하면 보고한다»는 **독립 종결절 2개**에 행위 대상까지 갈린다(명세 변경 ↔ 보고). §13 «Work 채번 단위가 문장»을 종결절 기준으로 적용하면 61행 1 · 63행 1(종결절 2지만 같은 축 = 보고 정직성, 병합 사유 기록됨) · 67행 2 · 68행 2 가 **전부 정합**한다. 따라서 제안된 «통일»(61행 분리 또는 68행 병합) 어느 쪽도 반영하지 않았고, s005=4 · s006=12 census 도 그대로다. 다만 지적이 드러낸 **판별자 미기록**은 타당하므로 §1 에 «분리/병합의 1차 판별자» 절을 신설해 네 자리의 정합을 명문화했다 |
| R2-10 (42행 «관찰 전용» 미채번) | **fixed** | R2-9 를 반려하며 세운 판별자(독립 종결절 + 행위 대상 상이)를 그대로 적용하면 «관찰 전용이며 판정·평가에 쓰지 않는다»는 채번 대상이다 — 앞 Work 는 수치의 «기재», 이 절은 수치의 «사용»으로 대상이 갈린다. Prohibition 1건을 문장 등장 순 자리(기재 의무 뒤·실행 생략 금지 앞)에 추가 → s004 97→98 · 계 123→**124** · census 사유 갱신 |
| R2-11 («파일럿 §6.2 동형»이 4원 밖) | **fixed** | 지적대로 §16 4원에 «파일럿 선례»는 없다. 배선 자체는 구현 실측으로 성립하므로(constructor keyword L1357·L1822 · 무인자 판정 L1368 · `_status_call`+`len(args)<2` L2851·L3553 · `_header_assignment_valid` L3082·L3158 · `_literal_error_status_call` L3563 · 메시지 L7126) 유지하고, 근거 유형만 **①§16 «controller checker» 역할명 + 실장 확인**으로 다시 적었다. docstring 원문 인용이 성립하는 자리는 ② 를 함께 남겼다 |
| R2-12 (#98 장식성 enforcedBy · 병기 스타일) | **fixed**(전반부는 판정 달리함) | **#81·#83 병기 누락은 지적이 옳다** — 오류 계약 축이므로 `agent-design-review-api` 를 병기했다. **#98 의 enforcedBy 는 유지한다** — 이 문서의 병기 기준은 «자기 축 전 국면 미커버 → 공란 / 일부 국면에 결정적 술어가 닿으면 enforcedBy + 미커버 범위 병기»이고, #98 은 header 대입 형태를 `_header_assignment_valid` 가 집행하는 **부분 커버**라 #35·#100 과 같은 판이다. 반면 동종으로 지목된 #44(«Bash 로 실행해 Green 확인»)는 실행 «사실»에 닿는 술어가 **하나도 없는** 자리라 공란이 맞다 — 둘은 동종이 아니다. 지적이 제시한 두 번째 수정안(«병기 기준을 §4 메모에 명문화»)을 택해 판별 기준을 §4 에 신설했다 |
| R2-13 (33↔69 · 53↔56 비-재진술 사유 미기록) | **fixed** | 별개 규범 판정은 유지하고 §3 «비-재진술» 목록에 두 쌍의 사유를 기록했다 — 33↔69 는 처분 방식의 명시 준용이되 규범 대상이 구조 결정 ↔ 메커니즘 결정으로 갈리고, 53↔56 은 같은 «강제 전파 금지»의 자기판단 채널 ↔ 명세복종 거부 채널(후자만 Override·`TREE_CONTRACT_MISMATCH`)이라 사본이 아니라 두 채널이다 |

수리 범위 준수: 쓴 파일은 자기 spec · 자기 worksheet · 이 처분 절 3곳뿐이다. 원문 `dddjango/agents/coder.md`·`ontology/`·다른 에이전트 산출물은 건드리지 않았고 `--write` 도 쓰지 않았다.
