# 적대 리뷰 — implementation-django-ninja-final (T3 이관 spec)

- 대상: `workspace/eval/t3/specs/implementation-django-ninja-final.spec.json` + `workspace/eval/t3/worksheets/implementation-django-ninja-final.md`
- 대조: 발주서 · T3-authoring-brief · 원문 final.md(현재 1021행, 마커 2행 제거 시 센서스 1019행 좌표 정합 확인) · `dddjango/scripts/check-*.py` 27종 docstring 실독 · `ontology-authoring.md` §13–§16 · `ontology_migrate.py` docstring · 파일럿 spec 2건
- 리뷰어 자체 검증: `ontology_migrate.py`(검증 전용) exit 0 재현 · 신규 채번 182 = 발주서 182 · 파일럿 2절(s022-6.1·s023-6.2) 바이트 동일 재수록 확인(도구 reuse 계약상 필수 — 스코프 위반 아님) · 21/21 절 census 대사 일치 재검증 · 원문 전 절 블록 경계·kind 원문 대조(표·체크박스 0건 실측 일치)
- 판정: **반송(수리 요망)** — medium 6건 · low 10건. 절 경계·계수·kind는 전수 통과. 결함은 배선 렌즈(축 불일치·병기 누락)와 재진술 렌즈(누락 링크·유예 좌표 오류)에 집중.

---

## Medium

### M1 [배선] s010-2.3/b20 norm2 (worksheet #75) — docstring이 명시 제외한 축을 enforcedBy로 주장

- **주장**: 「config/api.py·api_router.py에 컴포지션 루트 혼입 금지」를 `check-composition-root.py` enforcedBy로 배선했으나, 그 docstring은 정확히 이 변종을 검사 범위 **밖**으로 선언한다: «`config/api.py` 내장·`<app>_api_router.py` 접힘 같은 *in-tree 파일 내장* 변종은 그 파일이 적법히 존재해 형태로 못 가르므로 discipline-reviewer 의미 레인 몫이다». basis는 이 문장을 「검사기 소유 선언」으로 읽었지만 문면은 소유 **부인**(coverage disclaimer)이다. DI 레인은 단일 파일 `composition_root.py` 모양(#497)만 차단하고, code-json lane은 API object·registrar·URLconf provenance 축이라 어느 레인도 이 사건에 발화하지 않는다. §16 «담당 검사기가 없는데 enforcedBy 주장 = 오배선(그 역)» 해당.
- **수정안**: 해당 norm에서 `enforcedBy` 제거, `delegatedTo: [agent-discipline-reviewer]` 단독 + basis를 「docstring이 in-tree 내장 변종을 reviewer 의미 레인 몫으로 명시」로 교정.

### M2 [배선] s009-2.2/b4 (worksheet #28) — #139 인용 축 불일치·단독 배선

- **주장**: 「path·query·body 파라미터 명시 구분」(원문 112행)을 `check-usecase-dto-placement.py` **단독** enforcedBy로 배선하며 «#139 제약 선언은 `schema_in.py` 에»를 근거로 인용. #139는 *제약 선언의 자리*(컨트롤러 Field·validator 금지) 규칙이지 path/query/body **출처 구분** 축이 아니다. 27종 어디에도 파라미터 종류 구분을 보는 표면이 없으므로(실독 확인) 이 규범의 실표면은 기계 비커버인데 delegatedTo 공백이라 그래프 소비층이 위반을 검사기로 오라우팅한다.
- **수정안**: enforcedBy 제거(또는 축소) + `delegatedTo: [agent-discipline-reviewer]`(§16 implementation-* 기본값). basis 재작성.

### M3 [배선] s012-3.1/b6 norm3 (worksheet #93) — 검사기 명시 제외 영역(비교식·조립)인데 reviewer 병기 누락

- **주장**: 「응답 조립·비교의 원시 리터럴 확산 금지」를 `check-choices-literal-consumption.py` 단독 enforcedBy. 표제 인용(«cleancode §2.14 소비 규율»)은 축자 일치가 맞으나, 같은 docstring이 «**보지 않는 것(의미 레인 = discipline-reviewer 몫)**: 변수 우회, 간접 queryset, **비교식(`x.status == "…"`)** …»으로 규범 문면의 «비교» 축과 «응답 조립» 축 대부분을 명시 제외한다. 검사기 실커버는 (a) `choices=` 심볼 필드의 `default="리터럴"` (b) 직접 `objects.filter(field="리터럴")` 두 형태뿐. 이 spec의 자기 관례(부분 커버 시 reviewer 병기 — #31·#39·#109 등)와도 비대칭.
- **수정안**: `delegatedTo: [agent-discipline-reviewer]` 병기 + basis에 «비교식·변수 우회는 docstring이 reviewer 몫으로 명시» 추가.

### M4 [배선] s019-5.1/b5 (worksheet #123) — 응답 축(#143/#144) 인용으로 입력 축 규범을 단독 배선

- **주장**: 「DB table/model 내부 구조의 public **parameter** 누출 금지」(원문 419행 — filter/sort 파라미터 = 입력 표면)를 `check-usecase-dto-placement.py` 단독 enforcedBy로 배선하며 «#143/#144 `schema_out` 은 result 로 만든다»를 인용. #143/#144는 **응답(schema_out)** 축이고, 입력 파라미터에 ORM 필드명·테이블 구조가 새는 형태(FilterSchema·schema_in의 이름 누출)를 보는 규칙은 27종에 없다. 바로 앞 규범(#122)은 같은 검사기에 reviewer를 병기했는데 #123만 단독이라 실커버 공백.
- **수정안**: `delegatedTo: [agent-discipline-reviewer]` 병기(또는 enforcedBy 제거 후 기본값 단독) + basis 축 교정.

### M5 [재진술] s009-2.2/b2 ↔ s010-2.3/b1 — same-doc 사본인데 spec restates·검수표 §3 양쪽 누락

- **주장**: b2 blockquote(원문 106–108 「형태 선택」: 신규 표준 = §2.3 클래스 컨트롤러 · 기존 함수형 보존 · 오류 이유 강등 금지)는 s010-2.3/b1(194–198)의 3문장 축약 사본이다. 검수표 배선표 #25·#27 basis 스스로 «§2.3 b1·§6.3 b5와 같은 축의 재진술 — 검수표 §3»이라 적어 관계를 인지했으면서, spec의 b2에 `restates` 링크가 없고 검수표 §3.1(8링크)에도 미등재다. brief §재진술 「같은 문서 안 쌍은 spec restates에 넣는다」 위반.
- **수정안**: spec s009-2.2/b2에 `restates: ["implementation-django-ninja-final/s010-2.3/b1"]` 추가 + 검수표 §3.1에 행 추가. (같은 논리로 s019-5.1/b8 괄호 문장도 검토 — L계 참조.)

### M6 [재진술] 검수표 §3 유예 표 — SKILL.md s003 경계 4불릿 좌표 오프바이원 (9행)

- **주장**: 유예 표가 «직접 확인으로 확정»했다는 상대 좌표 중 s003 경계 불릿 참조 행(#2 「12–15」·#4 「12」·#5 「13」·#6 「14」·#7 「15」·#33 「12」·#34 「12·14」·#35 「13」·#37 「15」)이 전부 1행씩 이르다. 실측(`grep -n`): REST 불릿=**13**, 애그리거트=**14**, ORM=**15**, pytest=**16** (12행은 빈 줄). s004 참조 행(20·21·…·36)과 s003 절 범위 「9–17」 자체는 정확 — 불릿 좌표만 계통 오류. T3 소급 패스가 이 좌표로 restates를 걸므로 오연결 위험.
- **수정안**: 검수표 §3 해당 9행의 상대 좌표를 13·14·15·16(및 「13–16」)으로 정정.

---

## Low

### L1 [배선] s009-2.2/b1 norm2 (#24) — 성공/오류 schema 분리 의무의 «성공» 축 비커버·병기 누락

`check-openapi-error-declaration.py`는 «직접 반환 BC 오류 ↔ `response={status: <Bc>ErrorSchema}` 선언 일치» 축만 검증한다(docstring). 규범은 성공 schema 분리까지 포괄하므로 reviewer 병기가 자기 관례에 정합. (검사기가 오류 절반을 실커버하므로 low.)

### L2 [배선] s009-2.2/b7 (#31) — response-schema-bypass는 204 «의무»의 집행자가 아님

docstring 표면은 «raw 200-203 차단»이고 schema-less 204는 carveout으로 **통과**시킬 뿐, 「delete는 204 사용·body 미반환」 의무 위반(예: delete가 200+body)을 진단하지 않는다. reviewer 병기가 이미 있어 라우팅은 성립 — enforcedBy가 표면 초과 주장이라는 기록.

### L3 [배선] s025-7/b4 (#152) — 역방향 게이트를 저장 의무의 enforcedBy로 주장

`check-idempotency-scope-creep.py`는 «미요청 멱등성 산출물 차단» 게이트라(docstring: G1 승인 없는 추가를 막는 데 한정) 「첫 요청 결과 durable storage 저장」 의무의 **불이행**을 진단하지 못한다. 인용(«§9.6 Idempotency storage 집행»)은 표제 실문이나 진단 방향이 반대. design-review-db 병기가 있어 low.

### L4 [배선] s006-1.3/b1 norm1 (#9) — 인용 문면 부재

basis가 check-context-isolation docstring 인용이라며 «의미 변종은 discipline-reviewer 몫»을 제시 — 그 docstring에 해당 문면 없음(실재 문면: «ast+ 후보 채널 (㉰ — exit 불산입, 마무리는 discipline-reviewer)»; «의미 변종…몫» 계열 문장은 check-app-container·check-composition-root 소속). 취지는 동일하나 인용 출처 표기 부정확.

### L5 [배선] s010-2.3/b21 norm1 (#76) — «매요청 호출» 빈도 축은 두 레인 어디에도 없음

인용문(«driving 층은 `build_<use_case>()` 팩토리를 매요청 호출만 하고»)은 docstring **서두의 정본 규칙 서술**이고, 실검사 레인(단일 파일 #497 · code-json lane의 object/registrar/URLconf provenance)에 호출 빈도 진단은 없다. 위반 형태(모듈 레벨 전역 인스턴스)는 같은 블록 norm2가 context-isolation #431 + reviewer로 따로 배선돼 있어 실해는 제한적.

### L6 [규범식별] s020-5.2/b5 norm2 (#131) — «일반적으로 timestamp와 id를 함께 쓴다»의 Obligation 과승격 의심

관례 서술(«일반적으로»)을 Obligation으로 승격. 발주서 계수 7에 묶여 계수 자체는 불변이므로 class 재고만 제안(Permission 또는 basis에 관례 성격 명기).

### L7 [재진술] s008-2.1/b3 ↔ s010-2.3/b23 — INSTALLED_APPS 'ninja_extra' 등록 규범의 same-doc 반복 미링크

§2.1(원문 90행)과 §2.3 설치 문단(293–294행 — «핀은 §2.1과 동일»이라 자기 출처 지목)이 같은 등록 규범을 반복. 센서스 재진술 열이 양쪽 N이라 확신 낮음(low) — 소급 패스 검토 대상으로 기록.

### L8 [재진술] 사본 Work 이중 채번 — §15 «정본 1곳만 Work 승격» 문면과 상충

같은 문서 안 사본 블록(s009-2.2 b9·b10·b11·b14·b16·b17, s016-4.1 b6·b7, s024-6.3 b5)에 restates 링크와 **함께** Work도 채번했다. 검수표 §3.1이 파일럿 선례·append-only 원장·발주서 계수 정합을 들어 정직하게 사유를 기록했고 소급 tombstone 처분까지 제안했으므로 반송 사유로 삼지 않되, T3 소급 패스 처분 필요 항목으로 남긴다.

### L9 [규범식별] s001/b1 norm3 — DRF 한정 사용의 class Permission 판독 여지

«DRF 자료는 …때만 보조 근거로 사용한다»는 허용+범위 제한 복합 문면 — Permission 단독보다 Exception(한정) 또는 Prohibition(밖 사용 금지) 판독 여지. 확신 낮음.

### L10 [경계kind·규범식별] s024-6.3/b8 — 이질 class 2개의 1 Work 병합

«…동작을 보존하고, …주장하지 않는다»(한 문장)를 Obligation 1 Work로 병합. 파일럿 s022-6.1은 병렬 조항(«안정 공개 계약 주장 금지»)을 별도 Prohibition으로 세웠다(그쪽은 별문장이라 방어 가능). 문장 해상도 규약상 적법하나 class 소실(주장 금지 축)이 label에만 남는 점 기록.

---

## 전수 검사 통과 확인 (지적 없음 축)

- **경계·kind**: 21절 전 블록의 행 범위를 원문(마커 제거 좌표)과 대조 — 연속·비중첩·무손실 성립, 첫 블록 선두 빈 줄 귀속·구분자 선행 귀속·code 후행 빈 줄(파일럿 선례) 일관. 표 0·체크박스 0 실측 일치, table-row/checklist-item 미사용 정당. 명사구 목록 8곳 prose 처리와 발주서 비고 일치. blockquote 2곳 norm 귀속 적정.
- **규범 계수**: 21/21 절 발주서 대사 일치(182), 병합 판정(s008-2.1 6W·s009-2.2 b10/b13·s010-2.3 b9)은 검수표에 사유 기록 존재.
- **배선 실물 대조 표본 외 전수**: #119(business-vocabulary)·#493(public-surface-annotation)·#390/#387/#389(test-config)·#110/#431/#98/#93–96(context-isolation)·#97/#87(naming)·Q-7/#497/code-json lane(composition-root)·#488/#81(layer-skeleton)·#139/#142/#143/#144/#210(usecase-dto-placement)·406/415(ninja-boundary-middleware)·idempotency-scope-creep 인용 전건 docstring 실재 확인. 무소유 규범 0. check-naming에 컨트롤러 메서드명 축 부재(#191은 usecase-dto-placement ⓓ) — 검수표 기본값 도피 방지 역검 4건 전부 실측 재확인.
- **재진술**: 발주서 재진술 열 7절 전건 처리 확인(같은 문서 → spec restates·교차 문서 → 유예 표). 유예 표의 s004 «핵심 운영 원칙» 추가 발견(센서스 과소 판정)은 실측상 타당 — s004 참조 좌표(20–36) 전건 정확.
- **파일럿 재수록**: s022-6.1·s023-6.2는 파일럿 spec과 바이트 동일·선두 배치 — reuse 계약(load_issued 등장 순 재사용) 충족, 스코프 위반 아님.

---

## 처분 (수리 라운드 — 2026-08-22)

수리자: T3 이관 spec 수리 에이전트. 대조 정본은 원문 `dddjango/skills/implementation-django-ninja/references/final.md`(마커 제거 복원본 좌표)·`dddjango/scripts/check-*.py` docstring 실물·`workspace/tools/ontology-authoring.md` §15·§16·`dddjango/skills/implementation-django-ninja/SKILL.md` 실측.
표기 — **반영**: 지적대로 spec/검수표 수정 · **기각**: 지적의 핵심 주장을 불수용(근거 병기).
합계: **반영 13 · 기각 3**(L6·L8·L9). 수리 후 자기 검증 `ontology_migrate.py`(--write 미사용) **exit 0** 재현 — 신규 채번 182·재사용 97 불변.

| # | 지적 | 처분 | 근거 한 줄 |
|---|---|---|---|
| M1 | s010-2.3/b20 norm2 «config/api.py 혼입 금지»의 composition-root enforcedBy | **반영** | docstring 원문 대조 결과 해당 문장은 «형태로 못 가르므로 discipline-reviewer 의미 레인 몫»이라는 **커버 부인**이 맞다 — enforcedBy 제거, reviewer 단독 위임으로 교정(§16 「검사기 부재인데 enforcedBy 주장 = 오배선」). |
| M2 | s009-2.2/b4 «path·query·body 구분»의 #139 인용 | **반영** | #139는 «제약 선언의 자리(schema_in.py)» 규칙이고 27종 docstring 재grep에도 파라미터 출처 구분 표면이 없다 — enforcedBy 제거 후 §16 기본값 reviewer 단독. |
| M3 | s012-3.1/b6 norm3 리터럴 확산 금지의 reviewer 병기 누락 | **반영** | 같은 docstring이 «보지 않는 것 … 비교식·변수 우회»로 규범의 비교·조립 축을 명시 제외하고 실커버는 `default=` / 직접 `objects.filter()` 둘뿐 — 병기 추가·basis에 제외 문면 명기. |
| M4 | s019-5.1/b5 입력 축 규범에 #143/#144(응답 축) 인용 | **반영** | 419행은 filter/sort **입력** 파라미터 표면이라 `schema_out` 축 인용이 어긋난다 — basis를 #139(입력 계약 자리·부분 대응)로 교정하고 이름 누출 판정은 reviewer 병기(직전 #122와 동형). |
| M5 | s009-2.2/b2 ↔ s010-2.3/b1 same-doc 사본 미링크 | **반영** | 106–108 3문장이 194–198의 1:1 축약임을 원문 대조로 확인 — spec `restates` 추가 + 검수표 §3.1 행 추가(정본 = §2.3). |
| M6 | 유예 표 SKILL.md s003 불릿 좌표 오프바이원 9행 | **반영** | `grep -n` 실측 13·14·15·16(12행은 빈 줄) 확인 — 9행 전부 정정하고 정정 사유를 §3 머리글에 남겼다(s004 20–36·#36의 11행은 정확해 불변). |
| L1 | s009-2.2/b1 norm2 «성공/오류 schema 분리» 병기 누락 | **반영** | openapi-error-declaration docstring은 오류 선언 일치 축만 명시 — 성공 분리 축 몫으로 reviewer 병기(부분커버 관례 정합). |
| L2 | s009-2.2/b7 «204 의무»의 표면 초과 | **반영**(basis) | 다만 «delete가 raw 200-203+body로 새는 변종»은 이 검사기가 결정적으로 잡는 실커버라 enforcedBy는 존치하고, 204 의무 불이행은 진단 못 한다는 표면 한계를 basis에 명기(지적이 제시한 두 선택지 중 후자). |
| L3 | s025-7/b4 «저장 의무»에 역방향 게이트 enforcedBy | **반영** | idempotency-scope-creep은 «미요청 멱등성 산출물 차단»이라 저장 불이행에 발화 가능한 경로가 0 — enforcedBy 제거, design-review-db 단독(표제 인용은 위임처 지목의 문면 근거로 강등). |
| L4 | s006-1.3/b1 norm1 basis의 인용 문면 부재 | **반영** | check-context-isolation docstring에 «의미 변종은 …몫» 문장이 없음을 실독 확인 — 실문면 «ast+ 후보 채널(㉰ … 마무리는 discipline-reviewer)»로 인용 교체(배선 자체는 불변). |
| L5 | s010-2.3/b21 norm1 «매요청» 빈도 축 비커버 | **반영** | 인용문은 docstring 서두 정본 서술이 맞으나 두 실검사 레인(#497 단일 파일·code-json provenance) 어디에도 호출 빈도 진단이 없다 — reviewer 병기 + 레인 한계 basis 명기. |
| L6 | s020-5.2/b5 norm2 «일반적으로 …쓴다»의 Obligation 과승격 | **기각**(부분 반영) | class 5종에 권고 항이 없고 «~한다» 평서 규범을 기본 의무로 읽는 것이 이 문서군 관례다(허용 축이 아니므로 Permission은 오히려 약독) — class 유지. 지적이 대안으로 제시한 «관례 성격 명기»만 basis에 반영. |
| L7 | s008-2.1/b3 ↔ s010-2.3/b23 INSTALLED_APPS 반복 미링크 | **반영** | 90행과 293–294행이 같은 등록 의무를 반복하고 사본 쪽이 «핀은 §2.1과 동일»로 자기 출처를 지목 — `restates`(b23→b3) 추가. 핀 규율은 참조일 뿐이라는 발주서 판정은 유지(Work 신설 없음). |
| L8 | 사본 측 Work 이중 채번(§15 상충) | **기각**(이월) | 상충 지적 자체는 성립하나 지금 사본 Work를 지우면 발주서 계수 182와 `load_issued()` 재사용 큐 97과 어긋난다 — 지적의 fix 문면대로 소급 패스 소관이라 이번 라운드 미반영. 대신 처분 대상 블록 목록을 검수표 §3.1 말미에 확정 기록. |
| L9 | s001/b1 norm3 Permission 판독 여지 | **기각**(부분 반영) | «…때만 …사용한다»는 주문면이 사용 허가이고 «때만»은 그 허가의 제약이라 ODRL Permission+constraint 판형에 대응한다(djr:Permission의 rdfs:seeAlso). 선행 의무의 면제 조항이 아니라 별개 자료 사용 규범이므로 Exception 부적합 — class 유지, 판독 근거만 basis에 기록. |
| L10 | s024-6.3/b8 이질 class 병합 | **반영**(기록) | 한 문장이라 문장 해상도 규약상 1 Work가 맞고 금지 축은 label 후반에 이미 보존돼 있다 — 지적대로 병합 경계·금지 축 보존을 basis에 명시(파일럿 비대칭은 원문 문장 형태 차이라는 사유 포함). |

**수리로 바뀐 배선 요약**: enforcedBy 단독 45→40 · delegatedTo 단독 113→116 · 병기 24→26 · 무소유 0(불변). 검사기 사용 `check-composition-root`15→14 · `check-usecase-dto-placement`13→12 · `check-idempotency-scope-creep`2→1 · `check-choices-literal-consumption`1(병기화) · `agent-discipline-reviewer`102→107. same-doc restates 11링크·9블록 → **13링크·11블록**(초판 머리글의 「8링크·6블록」은 오기였음을 함께 정정).
