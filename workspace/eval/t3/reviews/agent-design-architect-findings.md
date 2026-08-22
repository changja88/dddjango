# T3 적대 리뷰 — agent-design-architect (spec + worksheet)

- 대상: `workspace/eval/t3/specs/agent-design-architect.spec.json` · `workspace/eval/t3/worksheets/agent-design-architect.md`
- 대조: 원문 `dddjango/agents/design-architect.md`(96행 실측 일치) · 발주서 · T3-authoring-brief · `dddjango/scripts/check-*.py` 27종 docstring 전수 실독 · authoring §13/§16
- 리뷰어 자체 검증: `ontology_migrate.py`(--write 없이) 재실행 → exit 0 · 블록 56 · Work 204 (worksheet 주장과 일치)
- 계수 재검: s005 장문 불릿의 문장 단위 재계수(58행 14 · 59행 14 · 62행 26 · 64행 13)를 원문 대조로 확인 — worksheet census 대사의 «센서스 과소» 판정 3건(s002/s004/s005)은 지지된다. b24(65행) 관련 #526·#530·#563·#626 은 check-broker-contract(총 17)·check-missable-entrance(총 14) 담당 목록에 없음을 확인 — 기본값 위임은 도피가 아니라 문면 근거를 가진 정당 배선.

## 발견 (심각도순)

### F1 — medium · 규범식별 · s005 (58행, b17)

**주장**: 58행 composition 문장의 dash 절 «기존 BC 의 배선 실물(`*_api_router.py` 동형)은 배선 결정의 입력이 아니고, preserve 를 배선 답습의 근거로 명세에 박지 않는다»가 미채번이다. Work #93(«profile 무관 composition 표준»)의 label·basis, #99(«preserve 보존 — 보존 범위는 오류 wire 산출물까지» — 이는 뒤쪽 별도 문장의 괄호 절)에 모두 이 금지 축이 없다. 한 문장 안에서 Obligation(구성 표준)과 Prohibition(배선 답습 근거 금지 — 명세 저작 행위에 대한 별개 지시)의 성격이 갈리므로, spec 자신의 계수 규율(35행 저자명시/선반영금지 분리 · 59행 #109/#110 분리 · 62행 #127/#128 분리 선례)에 따라 분리 채번 대상이다.

**수정안**: s005 b17(58행)에 Prohibition Work 1건 추가 — 예: «기존 배선 실물의 결정 입력 배제와 preserve 배선 답습 근거 금지», delegatedTo `command-dddjango`·`agent-design-review-api`(같은 계약 축 — 심사판 병렬), basis ①문면 «2026-08-12 라운드 1′» + ②composition-root 는 registrar/URLconf provenance 실물만 검사(명세의 답습 근거 기재는 미커버 — 기본값). worksheet 배선 표·census 대사(s005 169→170)·총계(204→205) 동반 갱신.

### F2 — low · 규범식별 · s002 (22행, b5)

**주장**: 22행 첫 문장 «…주어진 제약으로 존중하고 그 안에서 애그리거트·통합 패턴을 설계한다 — 배치를 암묵 재결정하지 않는다»에서 Obligation(존중·설계)과 Prohibition(암묵 재결정 금지)이 갈리는데 1 Work(#5, class Obligation)로 병합됐다. s004 의 동형 케이스(저자 명시/선반영 금지)는 분리한 것과 비대칭. 다만 «존중=재결정 금지»를 같은 의무의 양면(dash 재진술)으로 본 판정도 성립 가능해 low.

**수정안**: 분리 채번하거나, worksheet 계수 규율 절에 이 병합을 «같은 축 dash 재진술 1 Work» 사례로 명시해 s004 분리 선례와의 기준 차이를 기록.

### F3 — low · 배선 · s005 (57행, b16 — Work #88)

**주장**: #88 «application·domain 의 HTTP status/body 생성 금지»의 basis가 «④#4 application_layer 의 django import 0 … HTTP 산출물 생성 축을 결정적으로 차단»이라 주장하나 과장이다. domain 측은 #8(밖으로 나가는 import 0 — 서드파티 포함, check-domain-model)로 전면 커버되지만, application 측 #4(check-transaction-boundary)는 **django import 만** 문다 — ninja `Status`/`http` 등 비-django 경로의 HTTP 산출물 생성은 비커버(#7 check-event-publish 도 층 역참조·framework 비계약 모듈만 묻는다고 docstring이 명시). 배선 자체(두 검사기 병기)는 유지 가능하나 «결정적 차단» 문구가 허위 근거에 가깝다.

**수정안**: basis를 «domain 축은 #8 전면 · application 축은 #4 의 django 경로 한정(비-django HTTP 산출은 검사 공백 — 심사판/게이트 몫)»으로 정정.

### F4 — low · 배선 · s005 (59행, b18 — Work #113)

**주장**: #113 «락·동시성 Risky Write 의 개발·운영 엔진별 동작 차이 명세 확정»에 enforcedBy=check-mechanism-ownership 병기. 그 검사기 docstring 관할은 «프로덕션 DB 엔진 메커니즘을 커스텀 백엔드로 교체한 정확한 형태만»(4-AND 고정밀)이라, 라벨 축(엔진 차이의 **명세 확정** 의무)은 미집행이다 — 예: repo 코드 수준의 자작 락·엔진차 미확정 명세는 발화하지 않는다. «코드 측 짝» 관례로 옹호 가능하나 축 일치가 가장 느슨한 병기.

**수정안**: basis에 «커스텀 백엔드 교체 축 한정 — 명세 확정 자체는 db lens 심사 몫» 한계를 명시하거나 enforcedBy 를 내리고 위임 단독으로 전환.

### F5 — low · 배선 · s005 (58행, b17 — Work #92)

**주장**: #92 «새 Ninja surface 의 NinjaExtraAPI·class controller 와 profile 별 단일 project API instance» enforcedBy=check-composition-root. docstring의 code-json lane은 «선택 API object·canonical BC registrar·URLconf provenance·exactly-once»만 명시 — 단일 API instance 축은 커버하나 **NinjaExtraAPI/`@api_controller` class-controller 형태 축**의 검사 술어는 없다(27종 어디에도 없음). 부분 커버 미명시.

**수정안**: basis에 «API instance·registrar 축 한정 — controller 형태 축은 검사 공백(심사판 몫)» 병기.

### F6 — low · 경계kind · s005 (75행, b29)

**주장**: Work #184(«입장 표 최소 열 구성»)를 표 머리행 블록(75행, kind=table-row)에 귀속했으나, 그 규범을 서술하는 문장 «다음 최소 열로 한 행씩 판정한다»의 실주소는 73행(b28)이다. §13 «블록 내 문장→Work 대응(문장 등장 순=채번 순)» 규약상 문장 없는 블록의 Work 귀속은 변칙이고, §13 «계수 2축에서는 데이터 행만 산입» 관례와의 정합도 worksheet 자기 주장뿐이다. 파일럿(spec-architecture-ddd-final)에 table-row+norms 선례가 있고 census carriers=table 판정을 살리려는 의도가 기록돼 있어 blocker는 아니다.

**수정안**: 유지한다면 worksheet 경계 메모에 «73행 문장이 규범 원천·머리행은 구속 운반체로서의 귀속»임을 이미 적었으니 T3 소급 패스에서 재진술/계수 처리 시 이 블록을 특례로 다루도록 표기. 대안: #183·#184 를 모두 b28에 귀속하고 b29는 무규범 table-row로 두는 편이 §13 문면에 더 충실.

## 통과 확인 (지적 아님 — 검증 기록)

- ①경계: 전 절 연속·비중첩·전량 커버(도구 단언 + 원문 행 대조). 프론트매터 prose 처리(§13 code=펜스 한정), s001 3규범(발주서 adv 중재 정정 반영) 정합. 과대 병합 없음.
- ②규범: s004(10)·s002(8)·s005(169) 재계수 지지. class 5종 오판 확증 건 없음(Exception 다용은 한정 조항 문면과 부합·Override 0건 타당).
- ③배선: «schema/controller/OpenAPI checker» 매핑(§16 표) 실물 대조 일치. design-architect 를 명시 지목하는 검사기 3종(app-container·idempotency-scope-creep·transient-overmapping) 전부 enforcedBy 병기됨 — 기본값 도피 0건 확인. 42행·58행 처분-권한 문구의 골격 검사기 오배선 회피는 정당(문면 «G0 빚 결정» 지목). b24 브로커 4문의 기본값 유지 정당(#526·#530·#563·#626 은 어느 검사기 담당 목록에도 없음 — 실독 확인).
- ④재진술: same-doc 축자 쌍 0건 판정 지지(51↔58행 등은 부분 중첩 — restates 블록 사본 관계 아님). 발주서 재진술 열 2건(command-dddjango/s011·design-review-api/s006) 모두 worksheet 유예 절에 등재. 유예 20건의 상대 좌표 표본 대조(api/s006 56·58~69·71~74행, cmd 175행, db/s004 32·35~36행) 일치. 유예 대상의 spec 혼입 0건(spec 에 restates 필드 부재 확인).

**요약**: medium 1 · low 5. F1 반영 시 Work 1건 증가(204→205)로 spec·worksheet·census 대사 동반 갱신 필요.

## 처분 (수리자 판정 — 2026-08-22 · 원문 `dddjango/agents/design-architect.md` 및 검사기 실물 대조)

| # | 처분 | 근거 한 줄 |
|---|---|---|
| F1 | **fixed** | 58행 dash 절의 뒤 반절(«preserve 를 배선 답습의 근거로 명세에 박지 않는다»)은 주어가 *명세 저작 행위*이고 #90(preserve 채택)과의 상호작용을 금지하는 별개 축이라 #93·#99 어디에도 없음을 확인 — b17 에 Prohibition 1건(Work 94 «기존 배선 실물의 결정 입력 배제와 preserve 의 배선 답습 근거 금지») 추가, delegatedTo `command-dddjango`·`agent-design-review-api`, s005 169→170·총 204→205 동반 갱신. |
| F2 | **rejected**(spec 미변경 · 기준 기록만 반영) | 22행 dash 는 같은 축의 부정면 재진술이다 — 같은 행 뒤쪽이 그 의무를 «*재결정 금지 ≠ 재고 불가*» 한 낱말로 되받아 문면 자신이 두 절을 한 결정으로 취급하고, s004 #21/#22 는 «저자 명시»(기재 행위)와 «권고 방향 선반영»(별개 산출물 상태)로 **행위 대상이 다른** 케이스라 비대칭이 아니다. 분리 채번은 기각하고 worksheet §1 «계수 규율의 경계 사례» 1·2·3 에 병합/분리 기준(«별개 규범과의 상호작용 축 유무»)을 기록. |
| F3 | **fixed** | 실물 확인 — `check-transaction-boundary` #4 는 `application_layer/**` 의 **django import 만** 물고, `check-event-publish` `_check_application_imports` 는 자기 driving/driven 역참조와 `framework.*` 비계약 모듈만 판정한다(서드파티 `ninja` 경로 미커버). «결정적 차단» 문구는 domain 축(#8)에만 성립하므로 basis 를 «domain 전면 / application 은 django 경로 한정 — 비-django HTTP 산출은 검사 공백»으로 정정하고, 공백 수임자와 정합하도록 delegatedTo 에 `agent-design-review-api` 병기. |
| F4 | **fixed**(수정안 A 채택 — enforcedBy 유지) | `check-mechanism-ownership` docstring ⑴ 은 4-AND 커스텀 백엔드 교체 형태만 차단하고 ⑵ 는 migrations 규율이라, 라벨 축인 «엔진차 명세 확정» 자체는 미집행이 맞다. 코드 측 짝으로서의 병기는 유지하되 basis 에 «교체 축 한정 — 명세 확정은 db lens 심사(`agent-design-review-db`)가 실집행자» 한계를 명시. |
| F5 | **fixed** | 27종 재검색 결과 `NinjaExtraAPI`/`@api_controller` **형태 요구** 술어는 없음을 확증 — `check-context-isolation` `_check_api_controllers` 는 *이미 붙은* `@api_controller` 의 `auto_import=False` 여부(#110)만 문다. basis 에 «API instance·registrar 축 한정 · 형태 축은 검사 공백(심사판 몫)» 병기. |
| F6 | **fixed**(대안 채택 — #184·#185 를 b28 로) | 규범 문장 «다음 최소 열로 한 행씩 판정한다»의 실주소는 73행이고, 같은 웨이브 전 spec 이 표 머리행·구분행을 예외 없이 규범 0 으로 두었다(architecture-ddd s051-8·discipline-cleancode s042-4.3 — 규범은 데이터 행이 진다). 데이터 행이 0인 이 표에서 머리행 단독 귀속은 판형 이탈이라 두 Work 를 b28 에 귀속하고 b29·b30 은 무규범 table-row 로 남김(블록 존치 — carriers=`table`·byte 등가 불변). |

- 재검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-design-architect.spec.json` → **exit 0** (블록 56 · Work 205 · `--write` 미사용).
- 수정 파일: `workspace/eval/t3/specs/agent-design-architect.spec.json` · `workspace/eval/t3/worksheets/agent-design-architect.md` · 이 리뷰 파일의 본 절뿐(원문·`ontology/`·타 에이전트 산출물 무변).
