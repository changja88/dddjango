# T3 이관 검수표 — implementation-django-ninja-final

- 원문: `dddjango/skills/implementation-django-ninja/references/final.md` (현재 1021행 · 센서스 기준 1019행)
- spec: `workspace/eval/t3/specs/implementation-django-ninja-final.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-django-ninja-final.spec.json` → **exit 0**(`--write` 미사용)
- 저작 범위: 발주서 REF 21절 · 규범 182. spec에는 파일럿 기이관 2절(s022-6.1·s023-6.2)을 **명세 선두에 원본 그대로 재수록**했다 — 아래 §4-⓪ 참조(도구 계약상 필수).

---

## 1. census 대사 (절별 발주서 규범 수 ↔ spec 규범 수)

| section_key | 센서스 행 | 발주서 규범 | spec 규범 | spec 블록 | 대사 | 사유 / 과소·과대 판정 |
|---|---|---|---|---|---|---|
| s001 | 1–15 | 3 | 3 | 2 | ○ | — |
| s004-1.1 | 35–48 | 1 | 1 | 2 | ○ | 책임 불릿 8항은 명사구(P0 승계)라 비계수 — 발주서 판정 유지 |
| s005-1.2 | 49–60 | 4 | 4 | 4 | ○ | — |
| s006-1.3 | 61–80 | 3 | 3 | 5 | ○ | 허용 5·금지 5는 명사구, 지배 문장 3만 계수 |
| s008-2.1 | 83–99 | 11 | 11 | 5 | ○ | 초안 12 → 「버전 값은 …규율을 따른다 — 기억 속/추정 버전을 쓰지 않는다」를 1 Work로 병합해 11. **발주서(과소 아님)가 옳다** — em-dash 뒤 절은 같은 의무의 부정 표현 |
| s009-2.2 | 100–191 | 25 | 25 | 18 | ○ | 초안 27 → b10 후행 문장(「`response=`가 …계약이다」)과 b13 후행 문장(「직접 반환하는 성공 Schema…표현한다」)은 각각 선행 의무의 근거·부연이라 병합. **발주서가 옳다** |
| s010-2.3 | 192–305 | 38 | 38 | 29 | ○ | b9(auto_import) 후행 문장은 목적절이라 병합 — 그 외 전 문장 1:1 |
| s012-3.1 | 308–341 | 17 | 17 | 8 | ○ | 선두 「`Schema`는 Pydantic 기반 contract다」는 순수 서술이라 비계수(그래야 17 정합) |
| s013-3.2 | 342–364 | 1 | 1 | 3 | ○ | 확인 4항은 의문형 목록(체크박스 아님)이라 kind=prose·비계수. 예제 주석 속 규칙(「노출할 필드를 명시한다」)은 code 블록 안이라 제외 |
| s014-3.3 | 365–372 | 2 | 2 | 2 | ○ | — |
| s016-4.1 | 375–391 | 9 | 9 | 8 | ○ | 선두 문단은 「기존 auth mechanism adapter 우선」 1문장만 계수(앞 2문장은 서술) |
| s017-4.2 | 392–406 | 5 | 5 | 7 | ○ | 선두 문단은 순수 정의라 kind=prose·0 Work |
| s019-5.1 | 409–440 | 7 | 7 | 9 | ○ | 예시 코드 앞 괄호 문장 포함(발주서 지시) · `FilterSchema`/`Query` 문장은 「높일 수 있다」 서술이라 비계수 |
| s020-5.2 | 441–468 | 7 | 7 | 9 | ○ | 「offset이 단순하다」 권고 산문 제외(P0 승계) · b5 두 문장 각각 계수 |
| s024-6.3 | 827–853 | 15 | 15 | 8 | ○ | 415 불릿의 「pre-body 경계 선택 + candidate 제출」은 한 문장 한 Work, 406/415 body 불릿의 「BC ErrorSchema… 광고하지 않는다」도 한 문장 한 Work로 잡아 15 정합 |
| s025-7 | 854–872 | 8 | 8 | 9 | ○ | — |
| s026-8 | 873–900 | 5 | 5 | 6 | ○ | candidate 10항 명사구 비계수 · 선두 2문장은 서술(kind=prose 블록) |
| s028-9.1 | 903–943 | 8 | 8 | 5 | ○ | candidate 8항 명사구 비계수 |
| s029-9.2 | 944–959 | 3 | 3 | 4 | ○ | 보고 재료 5항 명사구 비계수 |
| s030-10 | 960–984 | 4 | 4 | 5 | ○ | Migration checklist 10항 명사구 비계수 |
| s031-11 | 985–1000 | 6 | 6 | 7 | ○ | — |
| **합계** | — | **182** | **182** | **173** | ○ | 21/21 절 전량 일치 |

**드리프트 처리**: 발주서가 경고한 1019→1021행 드리프트의 정체는 파일럿 투영 마커 2행(현재 파일 472·503행 `<!-- graph-owned: … -->`)이다. `ontology_migrate.py`가 좌표 해석 전에 마커 라인을 제거해 **복원 원문(1019행) = 센서스 기준선**을 만들므로, spec의 `line_start`/`line_end`는 센서스 좌표를 그대로 쓴다(도구가 절 스팬 sha256으로 이 정합을 단언 — 23절 전량 통과). 마커 제거본에서 전 절의 헤딩 위치를 재확인했고 센서스와 어긋난 절은 0건이다.

---

## 2. 배선 근거 표 (전 규범 182)

소유 분포 — enforcedBy 단독 40 · delegatedTo 단독 116 · 병기 26 · **무소유 0**.
검사기 사용 14종/27종: `check-composition-root`14 · `check-api-error-controller-contract`13 · `check-usecase-dto-placement`12 · `check-context-isolation`8 · `check-business-vocabulary`6 · `check-openapi-error-declaration`5 · `check-ninja-boundary-middleware`5 · `check-test-config`4 · `check-response-schema-bypass`3 · `check-public-surface-annotation`2 · `check-naming`2 · `check-layer-skeleton`2 · `check-choices-literal-consumption`1 · `check-idempotency-scope-creep`1.
에이전트: `agent-discipline-reviewer`107 · `agent-design-review-api`24 · `agent-design-review-db`8 · `agent-design-review-ddd`7 · `command-dddjango`7.

> **적대 리뷰 수리 반영(2026-08-22)** — 위 분포는 적대 리뷰 배선 지적 9건 수리 후 값이다. 이동 내역: #28·#75 = enforcedBy 제거(검사기 docstring이 그 축을 명시 제외 — 오배선) · #152 = enforcedBy 제거(진단 방향 역방향) · #24·#76·#93·#123 = reviewer 병기 추가(부분커버) · #9·#31·#131·#148·#3 = 배선 불변, basis 인용·한계만 교정. 근거는 §5 처분 기록과 `workspace/eval/t3/reviews/implementation-django-ninja-final-findings.md` «처분» 절.

| # | 블록 | class | Work label | enforcedBy(E)/delegatedTo(D) | 4원 근거 |
|---|---|---|---|---|---|
| 1 | s001/b1 | Obligation | REST 계약·ORM·테스트 세부의 source reference 위임 | D:`agent-design-review-api` · D:`agent-discipline-reviewer` | ①문면이 architecture-api·implementation-django·implementation-test를 «기준으로 한다»고 직접 지목 — ②③④ 담당 검사기 없음. §16 기본값(implementation-*→discipline-reviewer)에 API 계약 축만 design-review-api 병기(명시 문면 우선 — 파일럿 s022-6.1 b1 중재 선례) |
| 2 | s001/b1 | Obligation | Django Ninja = greenfield API 구현 기본 목표 | D:`agent-discipline-reviewer` | ④ registry 대응 검사기 없음(문면 역할명 0·docstring 무인용) — §16 위임 기본값 표 implementation-* 행 |
| 3 | s001/b1 | Permission | DRF 자료의 보조 근거 한정 사용(legacy review·비교·migration) | D:`agent-discipline-reviewer` | 동상 — 기본값(자료 사용 범위 판정은 정적 검사 밖). **class 판독 근거**(적대 L9): 주문면이 사용 «허가»이고 «때만»은 그 허가의 범위 제약이라 ODRL Permission+constraint 판형에 대응(djr:Permission의 rdfs:seeAlso) — 범위 밖 금지 축은 label의 «한정 사용»에 보존. 선행 문장(기본 목표)의 면제 조항이 아니라 별개 자료 사용 규범이라 Exception 부적합 |
| 4 | s004-1.1/b1 | Obligation | Django Ninja skill의 소유 범위 = HTTP adapter 구현 | D:`agent-discipline-reviewer` | ①문면 역할명 «adapter 구현을 다룬다» — 소유 경계 선언. ③P0 커버 판정 없음·④검사기 미대응 → §16 기본값(implementation-*) |
| 5 | s005-1.2/b1 | Obligation | REST 계약 요소의 architecture-api 결정 소유 | D:`agent-design-review-api` | ①문면이 «`architecture-api`가 결정한다»로 결정 주체를 명시 — §16 기본값 이탈 근거(명시 문면 우선) |
| 6 | s005-1.2/b2 | Obligation | 애그리거트·정책·구조 패턴 선택의 architecture-ddd 결정 소유 | D:`agent-design-review-ddd` | ①문면이 «`architecture-ddd`가 결정한다» 명시 — §16 위임 기본값 표 architecture-ddd 행(설계 시점 규범→design-review-ddd) |
| 7 | s005-1.2/b3 | Obligation | ORM·서비스·트랜잭션·마이그레이션 구현의 implementation-django 담당 | D:`agent-discipline-reviewer` | ①문면이 implementation-django 담당 명시 + §16 기본값 표 implementation-* 행 = discipline-reviewer(둘이 일치) |
| 8 | s005-1.2/b4 | Obligation | pytest fixture·test-double·동시성 mechanics의 implementation-test 담당 | D:`agent-discipline-reviewer` | 동상 — implementation-* 행 기본값 |
| 9 | s006-1.3/b1 | Obligation | Router operation = HTTP adapter | D:`agent-discipline-reviewer` | ①문면 역할명 «HTTP adapter» — 얇음 판정은 형태로 못 가르는 의미 레인(check-context-isolation docstring **실문면** «ast+ 후보 채널 (㉰ — exit 불산입, 마무리는 discipline-reviewer)» 준용 — 적대 L4로 인용 출처 교정: «의미 변종은 …몫» 계열 문장은 check-app-container·check-composition-root 소속이라 여기 인용은 부정확했다). ④ 지배 문장 검사기 0/27 → §16 기본값 |
| 10 | s006-1.3/b1 | Permission | Router 내부 허용 책임 5종 | D:`agent-discipline-reviewer` | 허용 목록은 명사구라 지배 문장만 계수 — 정적 검사 대상 아님(§16 기본값) |
| 11 | s006-1.3/b3 | Prohibition | Router·Schema·FilterSchema 금지 책임 5종 | E:`check-context-isolation.py` · D:`agent-discipline-reviewer` | ②check-context-isolation docstring «#93/#94/#95 driving 잎의 import 폭·#96 driving 잎은 애그리거트·리포지토리·도메인 이벤트 import 금지» = business rule/ORM 구성의 Router 유입을 구조로 차단. 의미 변종(외부 SDK orchestration·권한 정책)은 같은 docstring의 ㉰ 후보 레인 → reviewer 병기 |
| 12 | s008-2.1/b1 | Obligation | path operation 등록 수단 = NinjaAPI·Router | D:`agent-discipline-reviewer` | ④ 등록 수단 자체를 보는 검사기 없음(check-composition-root 는 registrar 합성 축) — §16 기본값 |
| 13 | s008-2.1/b1 | Obligation | 기존 API namespace·versioning 관례 준수 | D:`agent-discipline-reviewer` | ②check-composition-root docstring «§1.1 기존 확립 규약 존중» 철학과 동축이나 진단 없음 → 기본값 |
| 14 | s008-2.1/b2 | Obligation | 신규 도입 시 글로벌 임의 설치 금지·매니페스트 버전 핀 추가 | D:`agent-discipline-reviewer` | ④ 의존성 매니페스트를 보는 검사기 0/27(로스터 전수 실독 결과) — §16 기본값 |
| 15 | s008-2.1/b2 | Obligation | 핀 표기의 프로젝트 기존 관례 준수 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 16 | s008-2.1/b2 | Prohibition | 버전 값의 버전-핀 규율 준수(기억·추정 버전 금지) | D:`agent-discipline-reviewer` | 동상 — 기본값(한 문장의 «— 기억 속/추정 버전을 쓰지 않는다» 는 같은 의무의 부정 표현이라 1 Work) |
| 17 | s008-2.1/b2 | Obligation | 설치 시점 resolve 실버전을 호환 최신으로 핀 기록 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 18 | s008-2.1/b2 | Obligation | django-ninja·django-ninja-extra 동일 적용 | D:`agent-discipline-reviewer` | 동상 — 적용 범위 선언 |
| 19 | s008-2.1/b2 | Obligation | INSTALLED_APPS·NinjaAPI 인스턴스·URL 런타임 배선 동반 | E:`check-composition-root.py` · D:`agent-discipline-reviewer` | ②check-composition-root docstring «dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf의 직접 import provenance와 exactly-once 호출 관계를 함께 검사한다» — URL 등록·API 인스턴스 배선 축. INSTALLED_APPS 축은 검사기 밖 → reviewer 병기 |
| 20 | s008-2.1/b3 | Obligation | django-ninja-extra 설치·INSTALLED_APPS 'ninja_extra' 등록 | D:`agent-discipline-reviewer` | ④ INSTALLED_APPS 항목을 보는 검사기 없음(check-ninja-boundary-middleware 는 MIDDLEWARE 한정 — docstring 명시) — §16 기본값 |
| 21 | s008-2.1/b3 | Obligation | ninja-extra 핀 표기·버전 값 규율의 django-ninja 동일 적용 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 22 | s008-2.1/b4 | Obligation | 신규 Router 추가 시 확인 5항 수행 | D:`agent-discipline-reviewer` | 확인 목록은 명사구라 지배 문장만 계수 — 절차 준수 판정은 §16 기본값(implementation-*) |
| 23 | s009-2.2/b1 | Obligation | operation contract 구성 = decorator 선언 + typed parameters | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음 — §16 기본값(형태 서술이 곧 계약 구성 의무) |
| 24 | s009-2.2/b1 | Obligation | 다중 status 시 response={status: Schema} 성공/오류 schema 분리 | E:`check-openapi-error-declaration.py` · D:`agent-discipline-reviewer` | ②check-openapi-error-declaration docstring «선택된 operation이 직접 반환하는 BC 오류와 `response={status: <Bc>ErrorSchema}` 선언의 일치를 검증» — **오류** 선언 축만 실커버. 규범이 함께 요구하는 «성공 schema 분리» 축은 어느 검사기 표면도 아니라 reviewer 병기(적대 L1 — 부분커버 관례 정합) |
| 25 | s009-2.2/b2 | Obligation | 신규 표준 presentation 표면 = §2.3 ninja-extra 클래스 컨트롤러 | D:`agent-discipline-reviewer` | ④ 표면 형태 판정 검사기 없음 — §16 기본값 |
| 26 | s009-2.2/b2 | Permission | 기존 함수형 Router의 확립 표면 보존 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 27 | s009-2.2/b2 | Prohibition | 오류 응답 이유의 클래스→함수형 강등 금지 | D:`agent-discipline-reviewer` | 동상 — 기본값(§2.3 b1·§6.3 b5와 같은 축의 재진술 — 검수표 §3) |
| 28 | s009-2.2/b4 | Obligation | path·query·body 파라미터 명시 구분 | D:`agent-discipline-reviewer` | ④ path/query/body **출처 구분** 축을 보는 검사기 0/27(로스터 재실독 — #139는 «제약 «선언의 자리»(`schema_in.py`)» 규칙이라 이 규범의 축이 아니다) — §16 기본값 표 implementation-* 행. 적대 M2 수리: 축 불일치 인용에 근거한 usecase-dto-placement 단독 배선을 철회 |
| 29 | s009-2.2/b5 | Obligation | request body와 response body의 별도 schema 사용 | E:`check-usecase-dto-placement.py` | ②동 docstring «#143/#144 `schema_out` 은 result 로 만든다 — 도메인·ORM 타입 노출 금지» + #139 — in/out 분리 계약 |
| 30 | s009-2.2/b6 | Obligation | create 성공 201·Location header 계약 준수 | D:`agent-discipline-reviewer` | ④ status 값 자체를 보는 검사기 없음(check-business-vocabulary #119 는 framework 소유 5종 열거뿐) — §16 기본값 |
| 31 | s009-2.2/b7 | Obligation | delete·무본문 update의 204 사용·body 미반환 | E:`check-response-schema-bypass.py` · D:`agent-discipline-reviewer` | ②check-response-schema-bypass docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» — **표면 한계 명기**(적대 L2): 실커버는 delete가 raw 200-203+body 로 새는 변종뿐이고 schema-less 204는 carveout으로 «통과»시킨다. 「204를 쓴다」 의무의 불이행은 진단하지 않으므로 status 선택 축의 실소유는 reviewer 병기 |
| 32 | s009-2.2/b8 | Obligation | async operation의 Django async ORM 제약 확인 | D:`agent-discipline-reviewer` | ④ async ORM 제약을 보는 검사기 0/27 — §16 기본값 |
| 33 | s009-2.2/b9 | Obligation | 직접 반환 BC 오류 status의 BC base ErrorSchema 선언 | E:`check-openapi-error-declaration.py` | ②check-openapi-error-declaration docstring «직접 반환하는 BC 오류와 response={status: <Bc>ErrorSchema} 선언의 일치를 검증» |
| 34 | s009-2.2/b9 | Prohibition | framework 소유 status의 BC 직접 반환·BC ErrorSchema 광고 금지 | E:`check-business-vocabulary.py` · E:`check-openapi-error-declaration.py` | ②check-business-vocabulary docstring «#119 401·403·404·422·429·HttpError 는 framework 소유(BC 재선언 금지)» + OpenAPI 광고 축은 openapi-error-declaration(파일럿 s023-6.2 b30 배선과 동형) |
| 35 | s009-2.2/b10 | Prohibition | openapi_extra·override·monkeypatch·postprocessor 수동 선언/사후 변형 금지 | E:`check-openapi-error-declaration.py` | ②check-openapi-error-declaration docstring «선택 API module의 수동 OpenAPI 후처리를 차단» — 파일럿 s023-6.2 b34 «openapi_extra 보충·사후 변형 금지»와 동일 배선 |
| 36 | s009-2.2/b11 | Obligation | known exception의 구체 catch·no-arg concrete ErrorSchema Status 직접 반환 | E:`check-api-error-controller-contract.py` | ②check-api-error-controller-contract docstring «Enforce direct controller-owned code-profile error mapping» + §16 매핑 표 «controller checker» |
| 37 | s009-2.2/b11 | Prohibition | tuple·raw Response/dict·helper/factory/serializer/mapper·등록 handler 우회 금지 | E:`check-api-error-controller-contract.py` | 동상 — 문면이 §6.2를 직접 인용(파일럿 s023-6.2 b29 «추출 금지» 배선과 동형) |
| 38 | s009-2.2/b12 | Obligation | operation 문서화 — summary·description·tags decorator 인자 | D:`agent-discipline-reviewer` | ④ OpenAPI 문서 메타를 보는 검사기 없음(openapi-error-declaration 은 오류 선언 축 한정) — §16 기본값 |
| 39 | s009-2.2/b13 | Obligation | 반환 타입 명시(정보 없는 타입 금지·실제 흐름 표현) | E:`check-public-surface-annotation.py` · D:`agent-discipline-reviewer` | ②check-public-surface-annotation docstring «#493 모든 이름은 «첫 대입»에 타입을 적는다 — 시그니처·속성·지역 변수에 예외가 없다» — 반환 애너테이션 존재는 검사기, «정보 없는 타입» 의미 판정은 reviewer 병기 |
| 40 | s009-2.2/b14 | Obligation | 선언 JSON 성공의 Schema·Status 반환 | E:`check-response-schema-bypass.py` | ②check-response-schema-bypass docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» — 파일럿 s023-6.2 b35 배선과 동형 |
| 41 | s009-2.2/b14 | Permission | framework-native 성공 carveout 4종 허용·오류 우회 불허 | E:`check-response-schema-bypass.py` · E:`check-api-error-controller-contract.py` | 동상 + carveout의 오류 우회 축은 controller-contract(파일럿 s023-6.2 b35 3규범 배선 준용) |
| 42 | s009-2.2/b15 | Obligation | 10번 slot 승인 한 경로 선택 | D:`command-dddjango` | ①문면이 «10번 slot이 승인한» 절차를 지목 — §16 기본값 표 command+agents 행(절차 준수 판정 = Coordinator). 파일럿 s023-6.2 b16 동일 배선 |
| 43 | s009-2.2/b16 | Obligation | exception path — try에 최외곽 application call 한 문장만 | E:`check-api-error-controller-contract.py` | ②controller checker docstring — 파일럿 s023-6.2 b17 동일 규범의 §2.2 재진술 |
| 44 | s009-2.2/b16 | Obligation | 구체 exception·tuple만 catch·두 인자 Status 직접 반환 | E:`check-api-error-controller-contract.py` | 동상 |
| 45 | s009-2.2/b16 | Obligation | 성공 변환의 try 뒤 배치 | E:`check-api-error-controller-contract.py` | 동상 |
| 46 | s009-2.2/b17 | Obligation | Result/None path — call 정확히 1회·try 없는 failed branch 직후 배치 | E:`check-api-error-controller-contract.py` | ②controller checker docstring — 파일럿 s023-6.2 b18 동일 규범의 §2.2 재진술 |
| 47 | s009-2.2/b17 | Prohibition | 동일 ErrorSchema/header/Status 구성 직접 수행·예외·catch·helper·mapping table 꾸며내기 금지 | E:`check-api-error-controller-contract.py` | 동상 |
| 48 | s010-2.3/b1 | Obligation | 신규 표준 표면 = @api_controller 클래스 컨트롤러 | D:`agent-discipline-reviewer` | ④ 표면 형태 판정 검사기 0/27 — §16 기본값(implementation-*) |
| 49 | s010-2.3/b1 | Obligation | 함수형 Router operation의 레거시 취급·기존 형태 보존 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 50 | s010-2.3/b1 | Obligation | touched(신규·수정) 표면의 클래스 컨트롤러화 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 51 | s010-2.3/b1 | Prohibition | 406/415·오류 응답 이유의 함수형 Router 강등 금지 | D:`agent-discipline-reviewer` | 기본값 — §6.3 b5가 이 문장을 재진술(정본 = 본 절, 검수표 §3) |
| 52 | s010-2.3/b2 | Obligation | 클래스 컨트롤러의 함수형 계약 보존(response=·Status·오류 변환 순서) | E:`check-api-error-controller-contract.py` · D:`agent-discipline-reviewer` | ②controller checker docstring «direct controller-owned code-profile error mapping» — 오류 변환 순서 축. 계약 «보존» 판정 자체는 reviewer 병기 |
| 53 | s010-2.3/b2 | Obligation | 변경 범위의 형태 한정(prefix→클래스 데코레이터·self 메서드) | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음 — 기본값 |
| 54 | s010-2.3/b4 | Obligation | 클래스 데코레이터의 prefix·tag 소유와 메서드 데코의 상대 경로 | D:`agent-discipline-reviewer` | ④ 데코레이터 인자 배분을 보는 검사기 없음 — 기본값 |
| 55 | s010-2.3/b5 | Obligation | operation 메서드의 self 첫 인자 | D:`agent-discipline-reviewer` | ④ 미대응 — 기본값 |
| 56 | s010-2.3/b5 | Obligation | 메서드명의 동사구 유지 | D:`agent-discipline-reviewer` | ②check-naming docstring 담당 32규칙에 컨트롤러 메서드명 축 없음(#191 «use_case 이름은 동사» 는 usecase-dto-placement ⓓ 후보) — 기본값 도피 아님을 실독으로 확인 |
| 57 | s010-2.3/b6 | Obligation | response=·Status·controller-owned 오류 처리·반환 타입의 §2.2 동일 보존 | E:`check-api-error-controller-contract.py` · E:`check-public-surface-annotation.py` | ②controller checker(오류 처리·Status) + public-surface-annotation #493(반환 타입 명시) 두 축의 합 — 문면 열거가 그대로 두 검사기 표면에 대응 |
| 58 | s010-2.3/b7 | Prohibition | ControllerBase 직접 상속 금지 | D:`agent-discipline-reviewer` | ④ ninja-extra 기반 클래스 상속을 보는 검사기 0/27 — 기본값 |
| 59 | s010-2.3/b8 | Obligation | 프로젝트 api.py의 NinjaExtraAPI 인스턴스 1개 소유 | E:`check-composition-root.py` | ②check-composition-root docstring «dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf의 직접 import provenance와 exactly-once 호출 관계를 함께 검사한다» |
| 60 | s010-2.3/b8 | Obligation | BC의 side-effect-free register_<bc>_api(api)만 노출 | E:`check-composition-root.py` | 동상 — canonical BC registrar 축 |
| 61 | s010-2.3/b8 | Obligation | urls.py의 registrar 명시 1회 호출 후 mount | E:`check-composition-root.py` | 동상 — project URLconf exactly-once 호출 관계 |
| 62 | s010-2.3/b8 | Prohibition | BC 모듈 import만으로 registration 발생 금지 | E:`check-composition-root.py` · E:`check-context-isolation.py` | 동상 + ②check-context-isolation docstring «#431 부작용 등록 금지» |
| 63 | s010-2.3/b9 | Obligation | 명시 registrar 합성 controller의 auto_import=False | E:`check-context-isolation.py` | ②check-context-isolation docstring «기타 … #110 auto_import=False» — 규칙 번호 단위 정확 대응(4원 ①문면 «auto_import=False» 축자 일치) |
| 64 | s010-2.3/b14 | Obligation | registrar의 자기 BC controller 한정 import·함수 밖 등록 금지 | E:`check-composition-root.py` · E:`check-context-isolation.py` | ②composition-root(canonical registrar 계약) + context-isolation docstring «#98 타 BC composition_root 금지·#431 부작용 등록 금지» |
| 65 | s010-2.3/b15 | Prohibition | registrar의 config.api import·top-level register_controllers 호출 금지 | E:`check-composition-root.py` · E:`check-context-isolation.py` | 동상 — «직접 import provenance»(composition-root) + #431(context-isolation) |
| 66 | s010-2.3/b16 | Prohibition | urls.py 밖 registrar 호출·직접 controller 등록 금지 | E:`check-composition-root.py` | ②composition-root docstring «project URLconf의 직접 import provenance와 exactly-once 호출 관계» |
| 67 | s010-2.3/b17 | Permission | 소비자 의존 확립 API 인스턴스의 승인 별도 scope 보존 허용 | D:`agent-design-review-api` | ①문면 «독립 계약 surface»·«소비자가 의존» — 계약 surface 보존 판정은 API 설계 리뷰(파일럿 s023-6.2 b36 «승인된 wire 보존» 동일 배선) |
| 68 | s010-2.3/b17 | Prohibition | 보존 근거의 «소비자 의존» 한정(«먼저 작성돼 있음» 불인정) | D:`agent-design-review-api` | 동상 — 파일럿 b36 «보존 정당 근거 2종 한정» 준용 |
| 69 | s010-2.3/b17 | Prohibition | 신규 BC마다 API 인스턴스 생성 금지 | E:`check-composition-root.py` · D:`agent-design-review-api` | ②composition-root «선택 API object» 단일성 축 + 계약 scope 판정 병기 |
| 70 | s010-2.3/b18 | Prohibition | operation 본문의 Repository·Adapter 직접 생성 금지(Q-7) | E:`check-composition-root.py` | ②check-composition-root docstring 축자 «operation 본문에서 `Django…Repository()`/`…Adapter()`를 직접 생성하지 않는다(Q-7)» |
| 71 | s010-2.3/b18 | Obligation | DI 조립의 composition_root/dependency_wiring.py 소유·build_<uc>() 매요청 호출 | E:`check-composition-root.py` · E:`check-naming.py` | ②동 docstring «DI 조립은 BC 루트의 `composition_root/`(결선은 `dependency_wiring.py` — 트리 2~4행·#84·#85)가 소유한다» + check-naming «#97 driving 잎은 자기 composition_root 에서 `build_*` 만 import» |
| 72 | s010-2.3/b18 | Obligation | 이벤트 구독 결선의 event_wiring.py 분리 | E:`check-layer-skeleton.py` | ②check-layer-skeleton docstring «#488 고정(·재등장) 칸은 부모가 있으면 반드시 있다» — event_wiring.py 는 트리 고정 칸(파일 존재·자리 축). 내용 판정은 범위 밖 |
| 73 | s010-2.3/b18 | Exception | use-case 없는 순수 데이터소스 BC의 컴포지션 루트 생략 | D:`agent-discipline-reviewer` | 면제 판정은 형태로 못 가름 — check-composition-root docstring «형태로 못 가르므로 discipline-reviewer 의미 레인 몫» 준용 |
| 74 | s010-2.3/b20 | Prohibition | 컴포지션 루트의 단일 파일·BC당 1개(feature별 composition/ 분할 금지) | E:`check-composition-root.py` · E:`check-layer-skeleton.py` | ②composition-root docstring «#497 «파일이 아니라 폴더»» + «off-tree `composition/` 폴더 = #81 사건 … check-layer-skeleton 소유» — 두 소유자 병기(중복 진단 아님·소유 이관 문면) |
| 75 | s010-2.3/b20 | Prohibition | config/api.py·api_router.py에 컴포지션 루트 혼입 금지 | D:`agent-discipline-reviewer` | ②동 docstring이 이 변종을 커버에서 **명시 제외**한다 — «`config/api.py` 내장·`<app>_api_router.py` 접힘 같은 in-tree 파일 내장 변종은 그 파일이 적법히 존재해 형태로 못 가르므로 discipline-reviewer 의미 레인 몫이다». DI 레인은 단일 파일 `composition_root.py` 모양(#497)만, code-json 레인은 API object·registrar·URLconf provenance만 본다 → 담당 검사기 0. 적대 M1 수리: coverage 부인 문장을 소유 선언으로 오독한 배선을 철회하고 §16 기본값 단독 위임으로 교정 |
| 76 | s010-2.3/b21 | Obligation | 컨트롤러 메서드의 매요청 build_<uc>() 호출 | E:`check-composition-root.py` · D:`agent-discipline-reviewer` | ②composition-root docstring **서두의 정본 서술** «driving 층은 `build_<use_case>()` 팩토리를 매요청 호출만 하고». **레인 한계 명기**(적대 L5): 실검사 레인(DI = 단일 파일 #497 · code-json = API object·registrar·URLconf provenance)에 호출 빈도 진단이 없으므로 «매요청» 축의 실소유는 reviewer 병기(위반 형태인 모듈 레벨 전역 인스턴스는 같은 블록 norm2가 #431로 별도 배선) |
| 77 | s010-2.3/b21 | Prohibition | 모듈 레벨 전역 인스턴스 생성 금지(import 부작용) | E:`check-context-isolation.py` · D:`agent-discipline-reviewer` | ②context-isolation docstring «#431 부작용 등록 금지» 축 + 알리바이 변종은 composition-root docstring이 reviewer 몫으로 명시 → 병기 |
| 78 | s010-2.3/b22 | Obligation | 컴포지션 루트의 자기 BC infra/ACL 한정 import | E:`check-naming.py` · E:`check-context-isolation.py` | ②check-naming docstring «#87 composition_root 파일은 «자기 BC 의» composition_root 만 import» + context-isolation «#12 부를 수 있는 것은 OHS·published_event 둘·#13 OHS 소비는 ACL 뿐·#98 타 BC composition_root 금지» |
| 79 | s010-2.3/b22 | Prohibition | composition_root의 use-case DI 한정 소유(API instance·registration 미소유) | E:`check-composition-root.py` | ②composition-root docstring — DI 레인과 API object/registrar 레인의 소유 분리 문면 |
| 80 | s010-2.3/b23 | Obligation | ninja-extra의 INSTALLED_APPS 등록 필요 | D:`agent-discipline-reviewer` | ④ INSTALLED_APPS 항목 검사기 0/27(ninja-boundary-middleware 는 MIDDLEWARE 한정 — docstring 명시) — §16 기본값 |
| 81 | s010-2.3/b24 | Obligation | 새 operation 배치의 탐색 순서 준수 | D:`agent-discipline-reviewer` | ④ 배치 탐색 절차를 보는 검사기 없음 — 기본값 |
| 82 | s010-2.3/b25 | Obligation | ① driving_layer/api/의 @api_controller 클래스 grep | D:`agent-discipline-reviewer` | 동상 — 절차 단계(기본값) |
| 83 | s010-2.3/b26 | Obligation | ② 단일 컨트롤러 존재 시 그 메서드로 포함 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 84 | s010-2.3/b27 | Obligation | ③ 분할 시 리소스 일치 컨트롤러 포함·없으면 신규 리소스 컨트롤러 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 85 | s010-2.3/b28 | Obligation | ④ 컨트롤러 부재 시 <Aggregate>Controller 생성 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 86 | s012-3.1/b1 | Obligation | model 직노출 대신 API contract별 schema 분리 | E:`check-usecase-dto-placement.py` | ②check-usecase-dto-placement docstring «#143/#144 `schema_out` 은 result 로 만든다 — 도메인·ORM 타입 노출 금지» — model 직노출 차단 축 |
| 87 | s012-3.1/b2 | Obligation | request schema의 입력 형식·transport validation 한정 | E:`check-usecase-dto-placement.py` | ②동 docstring «#139 제약 선언은 `schema_in.py` 에» |
| 88 | s012-3.1/b3 | Obligation | response schema의 public field·type·nullable·enum 명시 | E:`check-usecase-dto-placement.py` | ②동 docstring «#143/#144 `schema_out` 은 result 로 만든다» |
| 89 | s012-3.1/b4 | Obligation | domain invariant의 service/model/DB boundary 보장 | E:`check-usecase-dto-placement.py` | ②동 docstring «#142 요청 스키마는 도메인 객체를 만들지 않는다» — 불변식 자리 이동 축 |
| 90 | s012-3.1/b5 | Obligation | field 제거·rename·type/required/status·error-shape 변경의 breaking change 취급 | D:`agent-design-review-api` | ①문면 «breaking change … version/deprecation 검토» — 하위 호환성·버전 판정은 architecture-api 소유(§1.2 위임 문면) |
| 91 | s012-3.1/b6 | Obligation | enum성 필드의 Literal·StrEnum 선언과 OpenAPI enum 노출 | D:`agent-design-review-api` · D:`agent-discipline-reviewer` | ①문면이 OpenAPI 계약 노출을 지목(API 계약 축) + 선언 형태 판정은 기본값 reviewer 병기 — 선언 «존재»를 보는 검사기 없음(check-choices-literal-consumption 은 «선언된 심볼의 소비» 한정 — docstring 명시) |
| 92 | s012-3.1/b6 | Obligation | 도메인 enum 파생·계약 안정성 필요 시 경계-로컬 Literal 고정 | D:`agent-design-review-ddd` | ①문면이 «published language — `architecture-ddd` §2.5»를 축자 지목 — §16 기본값 이탈 근거(명시 문면 우선) |
| 93 | s012-3.1/b6 | Prohibition | 응답 조립·비교의 원시 리터럴 확산 금지 | E:`check-choices-literal-consumption.py` · D:`agent-discipline-reviewer` | ①문면이 «`discipline-cleancode` §2.14 소비 규율» 축자 지목 ②docstring 표제 축자 «선언된 choices 값의 *리터럴 소비* 결정적 백스톱 (cleancode §2.14 소비 규율)». 다만 실커버는 (a) 심볼-choices 필드의 `default="리터럴"` (b) 직접 `<Model>.objects.filter(<field>="리터럴")` 둘뿐이고 같은 docstring이 «보지 않는 것(의미 레인 = discipline-reviewer 몫): 변수 우회·간접 queryset·비교식» 으로 규범의 «비교»·«응답 조립» 축을 명시 제외 → 잔여 축 reviewer 병기(적대 M3 — #31·#39·#109 부분커버 관례와 동형) |
| 94 | s012-3.1/b7 | Obligation | 발행 이벤트 봉투 discriminator의 1종째부터 domain StrEnum 파생 선언(birth-enum) | D:`agent-design-review-ddd` | ①문면이 «birth-enum — `architecture-ddd` §3.7» 축자 지목 — 기본값 이탈 근거 |
| 95 | s012-3.1/b7 | Obligation | Literal 파생이 discriminator의 유일 경로(평 Enum 불가) | D:`agent-design-review-ddd` · D:`agent-discipline-reviewer` | 동상 + Pydantic 표기 판정은 구현 시점 reviewer 병기 |
| 96 | s012-3.1/b7 | Prohibition | enum 파생·문자열 Literal의 OpenAPI 계약 동등(계약 안정성 논거 불성립) | D:`agent-design-review-ddd` | 동상 — §3.7 판정 축(논거 기각은 설계 리뷰 소유) |
| 97 | s012-3.1/b7 | Obligation | 버전 태그(payload_schema_version)의 리터럴 동결 유지 | D:`agent-design-review-ddd` | ①문면 «§3.7 짝 조항» 축자 지목 |
| 98 | s012-3.1/b7 | Obligation | union-enum 동기의 중앙 영구 테스트 입장 심사 candidate 취급 | D:`agent-discipline-reviewer` | ①문면이 «`discipline-tdd`» 중앙 입장 심사를 지목 — discipline-* 문서군 §16 기본값 = discipline-reviewer(일치) |
| 99 | s012-3.1/b7 | Exception | add/update 시 직렬화 경계 검증 한정 | D:`agent-discipline-reviewer` | 동상 — 조건부 한정(파일럿 s023-6.2 b3 «add/update 조건부» 계수 선례) |
| 100 | s012-3.1/b7 | Prohibition | 봉투 union의 페이지네이션 응답 직접 조합 금지(vitalik/django-ninja#1308) | D:`agent-discipline-reviewer` | ④ 외부 이슈 앵커 — 대응 검사기 0/27, 기본값 |
| 101 | s012-3.1/b8 | Prohibition | validator 위치·ValidationError.loc·기본 validation/직렬화의 영구 테스트 자격 부정 | D:`agent-discipline-reviewer` | ①문면이 discipline-tdd 입장 심사 축 — §16 기본값(discipline-*·implementation-* 모두 discipline-reviewer) |
| 102 | s012-3.1/b8 | Obligation | 공개 Python 계약의 중앙 심사 판정·공개 HTTP는 mount 경계 검증 | D:`agent-discipline-reviewer` | 동상 — 기본값(검증 절차 준수) |
| 103 | s013-3.2/b1 | Obligation | ModelSchema 사용 전 확인 4항 수행 | E:`check-usecase-dto-placement.py` · D:`agent-discipline-reviewer` | ②check-usecase-dto-placement docstring «#143/#144 `schema_out` … 도메인·ORM 타입 노출 금지» — 내부 필드 노출 축은 검사기, 의문형 확인 4항의 판정은 reviewer 병기 |
| 104 | s014-3.3/b1 | Obligation | computed field·resolver의 표현 mapping 한정 | E:`check-usecase-dto-placement.py` | ②check-usecase-dto-placement docstring «#210 컨트롤러는 result 만 보고 응답을 만든다(도메인 들여다보기 금지)» |
| 105 | s014-3.3/b1 | Obligation | DB 조회·권한 판단·domain decision의 selector/service 선처리 | E:`check-usecase-dto-placement.py` · D:`agent-discipline-reviewer` | 동상 + 계산 위치 의미 판정은 reviewer 병기 |
| 106 | s016-4.1/b1 | Obligation | 기존 auth mechanism adapter 우선 | D:`agent-discipline-reviewer` | ④ auth adapter 선택을 보는 검사기 0/27 — §16 기본값 |
| 107 | s016-4.1/b3 | Obligation | API credential의 header 기반 전달 우선 | D:`agent-design-review-api` · D:`agent-discipline-reviewer` | ①문면이 header 전달 계약 축 — architecture-api 소유(§1.2 «header … 는 architecture-api가 결정한다») + 구현 판정 reviewer 병기 |
| 108 | s016-4.1/b4 | Prohibition | secret의 query parameter 배치 금지 | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음 — 기본값 |
| 109 | s016-4.1/b5 | Obligation | 인증 실패·인증 필요의 401 응답 | E:`check-business-vocabulary.py` · D:`agent-discipline-reviewer` | ②check-business-vocabulary docstring «#119 401·403·404·422·429·HttpError 는 framework 소유(BC 재선언 금지)» — 401 의 소유 축. status 선택 자체는 reviewer 병기 |
| 110 | s016-4.1/b6 | Obligation | auth adapter의 성공 반환 = identity/principal | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음 — 기본값(파일럿 s023-6.2 b31 동일 규범 배선과 일치) |
| 111 | s016-4.1/b6 | Obligation | 인증 실패의 None 반환 또는 framework AuthenticationError raise | D:`agent-discipline-reviewer` | 동상 — 파일럿 b31 배선 일치 |
| 112 | s016-4.1/b7 | Prohibition | ErrorSchema의 auth 결과 반환·request.auth 저장 금지 | D:`agent-discipline-reviewer` | 동상 — 파일럿 s023-6.2 b31 «request.auth·인증 결과의 ErrorSchema 사용 금지» 배선 일치 |
| 113 | s016-4.1/b7 | Prohibition | framework 401의 BC 식별자 body 전역 변환 추가 금지 | E:`check-ninja-boundary-middleware.py` · E:`check-api-error-controller-contract.py` · D:`agent-discipline-reviewer` | ①문면이 §6.2를 직접 인용 ②check-ninja-boundary-middleware docstring «전역 `settings.MIDDLEWARE` 에 자가등록 … 적출» + controller-contract(전역 handler 경로) — 파일럿 s022-6.1 b17 «전역 변환 금지 축» 병기 배선 준용 |
| 114 | s016-4.1/b8 | Obligation | local development 제외 API traffic의 HTTPS 전제 | D:`agent-discipline-reviewer` | ④ 전송 계층 검사기 없음 — 기본값 |
| 115 | s017-4.2/b2 | Permission | 단일 endpoint 단순 gate의 adapter 연결 허용 | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음 — §16 기본값 |
| 116 | s017-4.2/b3 | Obligation | 다중 entry point 재사용 rule의 service/domain policy 이관 | E:`check-context-isolation.py` · D:`agent-discipline-reviewer` | ②check-context-isolation docstring «#93/#94/#95 driving 잎의 import 폭» — 정책이 driving 잎에 남는 구조 축 차단. 판정 소유 이동의 의미 변종은 reviewer 병기 |
| 117 | s017-4.2/b4 | Obligation | 권한 없는 authenticated caller의 403 응답 | E:`check-business-vocabulary.py` · D:`agent-discipline-reviewer` | ②check-business-vocabulary docstring «#119 … 403 … framework 소유» + status 선택 판정 reviewer 병기 |
| 118 | s017-4.2/b5 | Permission | 존재 은닉 resource의 계약상 404 사용 허용 | D:`agent-design-review-api` | ①문면 «API contract에 따라» — status 선택 계약은 architecture-api 소유(§1.2 문면) |
| 119 | s017-4.2/b6 | Obligation | object-level permission의 query shape·selector·prefetch 동반 검토 | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음(check-transaction-boundary 는 리포지토리 반환 축) — 기본값 |
| 120 | s019-5.1/b1 | Obligation | filtering·sorting·search parameter = public API contract | D:`agent-design-review-api` | ①문면 «public API contract다» — 계약 선언 소유는 architecture-api(§1.2 «filtering … 은 architecture-api» 축) |
| 121 | s019-5.1/b3 | Obligation | 허용 filter·sort key 명시 | D:`agent-discipline-reviewer` | ④ 허용 목록 명시를 보는 검사기 0/27 — §16 기본값 |
| 122 | s019-5.1/b4 | Prohibition | user-controlled ORM field name 직수용 금지 | E:`check-usecase-dto-placement.py` · D:`agent-discipline-reviewer` | ②check-usecase-dto-placement docstring «#139 제약 선언은 `schema_in.py` 에» — 입력 계약 자리 축. 값 출처 판정은 reviewer 병기 |
| 123 | s019-5.1/b5 | Prohibition | DB table/model 내부 구조의 public parameter 누출 금지 | E:`check-usecase-dto-placement.py` · D:`agent-discipline-reviewer` | ②동 docstring «#139 제약 선언은 `schema_in.py` 에» — filter/sort 파라미터는 **입력** 표면이라 선언 자리 축만 부분 대응(앞 규범 #122와 같은 축·같은 병기). ORM 필드명·테이블 구조가 public parameter 이름으로 새는 형태를 보는 검사기는 27종에 없고 #143/#144는 `schema_out` = **응답** 축이라 이 규범의 근거가 아니다(적대 M4 축 교정) → 누출 판정은 reviewer 병기 |
| 124 | s019-5.1/b6 | Obligation | reusable read logic·쿼리 최적화·N+1 방지의 implementation-django selector 위임 | D:`agent-discipline-reviewer` | ①문면이 implementation-django 를 직접 지목 + §16 기본값 표 implementation-* 행(일치) |
| 125 | s019-5.1/b7 | Obligation | 검색·sparse fieldset·복합 filter의 architecture-api 계약 선행 | D:`agent-design-review-api` | ①문면이 «`architecture-api`의 계약이 먼저 있어야 한다» 축자 지목 — 기본값 이탈 근거 |
| 126 | s019-5.1/b8 | Obligation | 신규 표면의 §2.3 클래스 컨트롤러 형태 적용(예시는 원생 함수형) | D:`agent-discipline-reviewer` | ④ 표면 형태 판정 검사기 없음 — 기본값(§2.3 b1과 같은 축) |
| 127 | s020-5.2/b1 | Obligation | pagination strategy의 API contract 결정 | D:`agent-design-review-api` | ①문면 «API contract가 결정한다» — §1.2 «pagination strategy … 는 architecture-api가 결정한다» 축자 대응 |
| 128 | s020-5.2/b3 | Obligation | 대규모·실시간·정합 민감 목록의 cursor/keyset 우선 검토 | D:`agent-design-review-api` | 동상 — strategy 선택 판정(§1.2) |
| 129 | s020-5.2/b4 | Obligation | page size 상한 설정 | D:`agent-design-review-api` | 동상 — 계약 파라미터 상한은 architecture-api |
| 130 | s020-5.2/b5 | Obligation | cursor/keyset의 stable indexed ordering 사용 | D:`agent-design-review-db` | ①문면 «stable indexed ordering» — 인덱스 정렬 안정성은 architecture-db 판정(§11 «DB consistency … 이면 architecture-db를 먼저 사용한다» 문면 근거·기본값 이탈) |
| 131 | s020-5.2/b5 | Obligation | timestamp+id 병용 관례 | D:`agent-design-review-db` | 동상 — 인덱스 설계 축. **class 판독 기록**(적대 L6): 문면이 «일반적으로 … 함께 쓴다»라는 기본 관례 서술이나 5종에 권고 class가 없고 «~한다» 평서 규범은 기본 의무로 읽는 것이 이 문서군 관례라 Obligation 유지(허용 축이 아니라 Permission 부적합) — 관례성 완화는 label의 «관례»에 보존 |
| 132 | s020-5.2/b6 | Obligation | 다음 페이지 요청 metadata의 response 포함 | D:`agent-design-review-api` | ①문면 응답 metadata = 계약 표면(§1.2 pagination 행) |
| 133 | s020-5.2/b7 | Obligation | framework pagination 기능 사용 시 strategy·response shape의 계약 정합 | D:`agent-design-review-api` · D:`agent-discipline-reviewer` | ①문면 «프로젝트 계약과 맞아야 한다» — 계약 판정 API + 구현 정합 확인 reviewer 병기 |
| 134 | s024-6.3/b1 | Obligation | 406/415 계약의 architecture-api §7.2 별도 승인 전제 | D:`agent-design-review-api` | ①문면이 «`architecture-api` §7.2에서 별도 승인» 축자 지목 — 기본값 이탈 근거(명시 문면 우선) |
| 135 | s024-6.3/b1 | Prohibition | 새 code-profile 전 endpoint 자동 강제 금지 | D:`agent-design-review-api` | 동상 — 계약 적용 범위 판정 |
| 136 | s024-6.3/b2 | Obligation | 406 — 승인된 Accept 협상 operation만 Ninja 경계 header 검사 | E:`check-ninja-boundary-middleware.py` | ②check-ninja-boundary-middleware docstring 축자 «대표 회귀는 406/415 콘텐츠 협상을 `request.path` 하드코딩한 전역 미들웨어로 자작한 것 — django-ninja 는 협상/임의 status 를 *경계 안* 에서 네이티브로 낸다(§6.3)» |
| 137 | s024-6.3/b2 | Obligation | 만족 표현 부재 시 framework HttpError(406) raise | E:`check-ninja-boundary-middleware.py` · E:`check-business-vocabulary.py` | 동상 + ②check-business-vocabulary «#119 … 일반 `HttpError` 는 framework 소유» |
| 138 | s024-6.3/b3 | Obligation | 415 — 별도 승인된 media type 제한 endpoint 한정 처리 | D:`agent-design-review-api` | ①문면 «계약이 별도 승인된 endpoint만» — 승인 계약 판정은 architecture-api(§7.2 지목의 짝) |
| 139 | s024-6.3/b3 | Obligation | Ninja-owned pre-body 경계 선택·공개 415 wire의 중앙 심사 candidate 제출 | E:`check-ninja-boundary-middleware.py` · D:`command-dddjango` | ②ninja-boundary-middleware(경계 안 처리 축) + ①문면 «중앙 입장 심사의 candidate로 제출» = 절차 층 → §16 기본값 표 command+agents 행 |
| 140 | s024-6.3/b3 | Obligation | add/update 시 mounted Django client의 415 wire 검증 | E:`check-test-config.py` · D:`agent-discipline-reviewer` | ②check-test-config docstring «#390 `test/e2e/` 는 입구를 거친다 — TestClient/Client·cron_job 신호» — 실제 mount 경유 검증 축. 조건부(add/update) 판정은 reviewer 병기 |
| 141 | s024-6.3/b4 | Obligation | 406/415의 framework HttpError body 그대로 사용 | E:`check-business-vocabulary.py` | ②check-business-vocabulary «#119 … 일반 `HttpError` 는 framework 소유(BC 재선언 금지)» |
| 142 | s024-6.3/b4 | Prohibition | BC ErrorSchema·code·helper·custom handler·raw response 생성 및 response= 광고 금지 | E:`check-api-error-controller-contract.py` · E:`check-openapi-error-declaration.py` | ②controller-contract(오류 helper/handler 생성 차단 — «direct controller-owned error mapping») + openapi-error-declaration(«미반환 framework status의 BC base 선언 금지» 축·파일럿 s023-6.2 b34 배선 동형) |
| 143 | s024-6.3/b5 | Prohibition | 415 이유의 클래스 컨트롤러 → 함수형 Router 변경 금지 | D:`agent-discipline-reviewer` | ④ 표면 형태 판정 검사기 0/27 — §16 기본값(§2.3 b1이 정본, 본 블록이 재진술) |
| 144 | s024-6.3/b5 | Prohibition | 오류 이유의 함수형 Router → 클래스 컨트롤러 자동 변환 금지 | D:`agent-discipline-reviewer` | 동상 — 역방향 조항(§2.3 미수록 고유분) |
| 145 | s024-6.3/b6 | Prohibition | request.body·json.loads 수동 본문 파싱 금지 | E:`check-usecase-dto-placement.py` · D:`agent-discipline-reviewer` | ②check-usecase-dto-placement «#139 제약 선언은 `schema_in.py` 에(컨트롤러의 Field·validator 는 위반)» — 선언적 수용 축의 뒷면. 수동 파싱 형태 자체는 reviewer 병기 |
| 146 | s024-6.3/b6 | Obligation | request body의 선언적 payload: Schema 수용 | E:`check-usecase-dto-placement.py` | 동상 — «#139» 선언 자리 계약 |
| 147 | s024-6.3/b7 | Prohibition | 전역 middleware·root URL wrapper·별도 dispatcher의 Ninja 밖 status 합성 금지 | E:`check-ninja-boundary-middleware.py` | ①문면 역할명 «Django 전역 middleware» ②check-ninja-boundary-middleware docstring 축자 «BC 의 driving 층에서 *자가 정의* 한 Django 미들웨어가 전역 `settings.MIDDLEWARE` 에 **자가등록** 되면 적출한다» ③P0 커버 판정 일치 |
| 148 | s024-6.3/b8 | Obligation | 승인 부재 시 framework 현재 협상/파싱 동작 보존·공개 계약 주장 금지 | D:`agent-discipline-reviewer` | ④ 계약 표명 판정은 정적 검사 밖 — §16 기본값(파일럿 s022-6.1 «framework body의 안정 공개 계약 주장 금지» 배선과 일치). **경계 기록**(적대 L10): 한 문장이 보존 의무 + 주장 금지 2축을 담아 문장 해상도 규약대로 1 Work로 세웠고 금지 축은 label 후반에 보존한다(파일럿 s022-6.1은 별문장이라 별도 Prohibition — 비대칭은 원문 문장 형태 차이) |
| 149 | s025-7/b1 | Prohibition | Idempotency-Key 정책의 API adapter 단독 처리 금지 | E:`check-idempotency-scope-creep.py` · D:`agent-design-review-api` | ②check-idempotency-scope-creep docstring «*태스크가 요청하지 않은* 멱등성(`Idempotency-Key` 필수·전용 record 테이블·replay store)을 … silent 의무화해 코드로 구현하는 회귀를 차단» — adapter 단독 신설 차단 축 ①문면 «API adapter만으로 처리하지 않는다» |
| 150 | s025-7/b1 | Obligation | contract·durable storage·transaction·concurrency의 공동 결정 | D:`agent-design-review-api` · D:`agent-design-review-db` | ①문면이 네 축의 동시 결정을 요구 — 계약 축 architecture-api·저장/동시성 축 architecture-db(§11 문면) |
| 151 | s025-7/b3 | Obligation | key 요구·TTL·scope·payload mismatch behavior의 API contract 배치 | D:`agent-design-review-api` | ①문면 «API contract에 둔다» — §1.2 «idempotency contract는 architecture-api가 결정한다» 축자 대응 |
| 152 | s025-7/b4 | Obligation | 첫 요청 결과의 durable storage 저장 | D:`agent-design-review-db` | ④ 저장 의무의 **불이행**을 보는 검사기 0/27 — check-idempotency-scope-creep은 표제가 «architecture-db §9.6 Idempotency storage 집행»이나 실동작은 «*태스크가 요청하지 않은* 멱등성 산출물의 G1 미승인 추가 차단»으로 **진단 방향이 반대**라 enforcedBy가 아니다(적대 L3 수리) → §16 기본값 이탈 근거(§11 «DB consistency … architecture-db») 위에 design-review-db 단독 위임 |
| 153 | s025-7/b5 | Obligation | 동일 key·동일 payload 재시도의 저장 첫 응답 반환 | D:`agent-design-review-db` | ①문면 재시도 의미론 — architecture-db §9.6 저장/재생 판정(위 docstring 인용의 짝) |
| 154 | s025-7/b6 | Prohibition | 가변 resource의 재조회 금지·첫 응답 snapshot 저장 | D:`agent-design-review-db` | 동상 — 저장 형상 판정(§9.6) |
| 155 | s025-7/b7 | Obligation | 동일 key·다른 payload의 conflict 처리 | D:`agent-design-review-api` | ①문면 payload mismatch behavior는 계약 항목(§1.2 idempotency contract 행) |
| 156 | s025-7/b8 | Obligation | unique constraint·lock·transaction boundary의 architecture-db·implementation-django 소유 | D:`agent-design-review-db` · D:`agent-discipline-reviewer` | ①문면이 두 참조를 축자 지목 — architecture-db 행 기본값(design-review-db) + implementation-django 행 기본값(discipline-reviewer) 병기 |
| 157 | s026-8/b2 | Obligation | OpenAPI 항목의 중앙 영구 테스트 입장 심사 candidate 취급 | D:`agent-discipline-reviewer` | ①문면이 «중앙 영구 테스트 입장 심사»(discipline-tdd) 지목 — §16 기본값 표 discipline-* 행 = discipline-reviewer |
| 158 | s026-8/b2 | Exception | add/update 항목의 mounted API 생성 문서 검증 한정 | E:`check-test-config.py` · D:`agent-discipline-reviewer` | ②check-test-config «#390 `test/e2e/` 는 입구를 거친다» — 실제 mount 경유 축. 조건부 한정 판정은 reviewer 병기 |
| 159 | s026-8/b2 | Prohibition | isolated Schema·미등록 Router/controller 문서의 공개 OpenAPI 증거 부정 | D:`agent-discipline-reviewer` | ④ 증거 출처 판정을 형태로 못 가름(check-test-config #390 은 TestClient 신호를 동일 취급 — docstring 실독 확인) — §16 기본값 |
| 160 | s026-8/b5 | Prohibition | 미실행 OpenAPI generation·schema diff의 실행 주장 금지 | D:`command-dddjango` · D:`agent-discipline-reviewer` | ①문면 주어가 검증 보고(절차 산출물) — §16 기본값 표 command+agents 행(절차 준수 판정 = Coordinator) + 구현 리뷰 병기 |
| 161 | s026-8/b5 | Obligation | DRF-to-Ninja migration의 schema 비교·차이 기록 | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음 — §16 기본값(implementation-*) |
| 162 | s028-9.1/b1 | Obligation | HTTP 항목의 discipline-tdd 중앙 입장 심사 선행 | D:`agent-discipline-reviewer` | ①문면이 «`discipline-tdd`의 중앙 입장 심사» 축자 지목 — §16 기본값 표 discipline-* 행 |
| 163 | s028-9.1/b1 | Exception | 승인 공개 HTTP 계약·독자 production failure의 add/update 한정 테스트 작성 | D:`agent-discipline-reviewer` | 동상 — 조건부 한정(파일럿 add/update 계수 선례) |
| 164 | s028-9.1/b1 | Obligation | business rule의 승인된 domain/service boundary 검증 | E:`check-test-config.py` · D:`agent-discipline-reviewer` | ②check-test-config «#387 `test/unit/` 은 DB 를 켜지 않는다·#389 `test/integration/` 은 진짜 DB 를 켠다» — 검증 자리 분리 축. 무게중심 판정은 reviewer 병기 |
| 165 | s028-9.1/b3 | Obligation | 공개 HTTP 계약의 실제 URLconf mount Django client 호출 | E:`check-test-config.py` | ②check-test-config docstring «#390 `test/e2e/` 는 입구를 거친다 — TestClient/Client·cron_job 신호가 없으면 위반» — mount 경유 증거 축 |
| 166 | s028-9.1/b3 | Prohibition | ninja/ninja_extra TestClient 직접 감싼 결과의 공개 HTTP 영구 증거 부정 | D:`agent-discipline-reviewer` | ④ #390 은 TestClient 신호를 구분하지 않음(docstring 실독) — 증거 자격 판정은 §16 기본값 reviewer |
| 167 | s028-9.1/b5 | Prohibition | framework 기본 body·기본 직렬화·validator 배치·private 직접 호출의 test 자격 부정 | E:`check-business-vocabulary.py` · D:`agent-discipline-reviewer` | ②check-business-vocabulary «#119 401·403·404·422·429·HttpError 는 framework 소유» — framework 소유 표면의 BC 계약화 차단 축 + 테스트 자격 판정 reviewer 병기 |
| 168 | s028-9.1/b5 | Prohibition | 근거 없는 오류 helper/handler 내부 unit test 작성 금지 | D:`agent-discipline-reviewer` | ④ 테스트 대상 선정 판정은 정적 검사 밖 — §16 기본값(discipline-tdd 입장 심사 축) |
| 169 | s028-9.1/b5 | Override | 승인 공개 status/body/header·wire Enum·security 계약의 mount 검증 허용 | D:`agent-discipline-reviewer` | 동상 — 금지 규칙의 범위 한정 조항(파일럿 «우선 규칙» Override 계수 선례) |
| 170 | s029-9.2/b1 | Obligation | 검증 보고의 실행 명령·검토 artifact 한정 | D:`command-dddjango` · D:`agent-discipline-reviewer` | ①문면 주어 «검증 보고» = 절차 산출물 — §16 기본값 표 command+agents 행(절차 준수 판정 = Coordinator) + 구현 리뷰 병기 |
| 171 | s029-9.2/b3 | Obligation | 미실행 mounted client·pytest·OpenAPI·compatibility check의 Not run 명시 | D:`command-dddjango` · D:`agent-discipline-reviewer` | 동상 — 보고 정직성 절차 |
| 172 | s029-9.2/b3 | Prohibition | Skill/reference loading command의 사용자 작업 검증 보고 금지 | D:`command-dddjango` | 동상 — 보고 수령·판정 주체는 Coordinator |
| 173 | s030-10/b1 | Obligation | greenfield DRF 요청의 Django Ninja 구현 전환 | D:`agent-discipline-reviewer` | ④ DRF 잔존을 보는 검사기 0/27 — §16 기본값(implementation-*) |
| 174 | s030-10/b1 | Obligation | legacy review·migration 시 DRF를 source behavior로 읽고 target 계약과 비교 | D:`agent-discipline-reviewer` | 동상 — 기본값 |
| 175 | s030-10/b4 | Prohibition | DRF-specific abstraction의 greenfield 표준 유지 금지 | D:`agent-discipline-reviewer` | ④ 대응 검사기 없음 — 기본값 |
| 176 | s030-10/b4 | Obligation | 필요 behavior의 Ninja Router/Schema·service validation·controller 오류 변환·mounted 검증 이관 | E:`check-api-error-controller-contract.py` · D:`agent-discipline-reviewer` | ②controller-contract(«controller-owned 오류 변환» 축자 대응) + 이관 판정 reviewer 병기 |
| 177 | s031-11/b1 | Obligation | REST contract 미결 시 architecture-api 선행 | D:`agent-design-review-api` | ①문면이 «`architecture-api`를 먼저 사용한다» 축자 지목 — §16 기본값 이탈 근거 |
| 178 | s031-11/b2 | Obligation | DB 정합·멱등 저장·lock·transaction 미결 시 architecture-db·implementation-django 선행 | D:`agent-design-review-db` · D:`agent-discipline-reviewer` | ①문면이 두 참조 축자 지목 — architecture-db 행(design-review-db) + implementation-* 행(discipline-reviewer) 병기 |
| 179 | s031-11/b3 | Obligation | 도메인 불변식·상태 전이 미결 시 architecture-ddd 선행 | D:`agent-design-review-ddd` | ①문면 축자 지목 — §16 기본값 표 architecture-ddd 행(설계 시점 규범 = design-review-ddd) |
| 180 | s031-11/b4 | Obligation | 계약 확정 후 Router/Schema 주작업의 implementation-django-ninja 사용 | D:`agent-discipline-reviewer` | ①문면 축자 지목 + §16 implementation-* 행 기본값(일치) |
| 181 | s031-11/b5 | Obligation | 테스트 세부 주작업의 implementation-test 사용 | D:`agent-discipline-reviewer` | 동상 — implementation-* 행 기본값 |
| 182 | s031-11/b6 | Obligation | risky domain work의 owning reference 동시 확인 | D:`command-dddjango` | ①문면이 4개 reference 동시 확인이라는 «절차»를 규정 — §16 기본값 표 command+agents 행(라우팅 절차 판정 = Coordinator) |

### 2.1 로스터 전수 실독 기록 (§16 L-F 의무)

`dddjango/scripts/check-*.py` **27종 전량**의 선두 docstring을 배선 전에 1회 실독했다(ast.get_docstring 일괄 추출 → 전문 통독). 실독 결과가 바꾼 판정 5건:

| 실독으로 교정된 판정 | 처음 떠올린 배선 | 실독 후 확정 | 근거 문면 |
|---|---|---|---|
| §2.3 `auto_import=False` | 배선 없음(«ninja 전용이라 검사기 없음»으로 도피할 뻔) | `check-context-isolation.py` | docstring 기타 행 «#110 auto_import=False» — 규칙 번호 단위 정확 대응 |
| §3.1 「원시 리터럴을 흩지 않는다」 | `agent-discipline-reviewer` 기본값 | `check-choices-literal-consumption.py` **+ reviewer 병기**(적대 M3 재수리) | docstring 표제 «선언된 choices 값의 *리터럴 소비* 결정적 백스톱 (cleancode §2.14 소비 규율)» — 원문 인용과 축자 일치. 단 같은 docstring의 «보지 않는 것» 절이 비교식·변수 우회를 제외하므로 단독 배선은 과잉이었다 |
| §2.2 「반환 타입을 명시한다」 | 기본값 | `check-public-surface-annotation.py` | «#493 모든 이름은 «첫 대입»에 타입을 적는다 — 시그니처…예외가 없다» |
| §9.1 「실제 mount된 Django client」 | 기본값 | `check-test-config.py` | «#390 `test/e2e/` 는 입구를 거친다 — TestClient/Client·cron_job 신호가 없으면 위반» |
| §2.3 컴포지션 루트 3불릿 | `check-composition-root.py` 단독 | +`check-layer-skeleton.py` 병기 | composition-root docstring이 «off-tree `composition/` 폴더 = #81 … check-layer-skeleton 소유»로 **소유 이관을 명시** — 단독 배선은 오배선 |

**기본값 도피 방지 역검**도 수행했다. 「검사기 없음」으로 판정한 규범 중 실독으로 근거를 굳힌 것:

- INSTALLED_APPS 등록(§2.1·§2.3): `check-ninja-boundary-middleware`는 docstring이 **`MIDDLEWARE` 한정**임을 명시 → INSTALLED_APPS 축은 검사기 0. 기본값 정당.
- 컨트롤러 메서드명 동사구(§2.3): `check-naming` 담당 32규칙에 컨트롤러 메서드명 축 없음(#191은 use-case 이름, `check-usecase-dto-placement` ⓓ 후보) → 기본값 정당.
- 의존성 매니페스트 버전 핀(§2.1 6 Work): 27종 어디에도 매니페스트/pin 검사 표면 없음 → 기본값 정당.
- ninja `TestClient(router)` 증거 부정(§9.1·§8): `check-test-config` #390은 `TestClient` 신호를 **구분 없이 수용** → 형태로 못 가름, 기본값 정당.

### 2.2 기본값 이탈 근거 (§16 — 이탈 32건의 축)

`implementation-*` 문서군 기본값은 `agent-discipline-reviewer`다. 이를 벗어난 위임은 전부 **문면이 소유 참조를 축자 지목한 경우**에 한정했다.

- `agent-design-review-api`(24): §1.2 「`architecture-api`가 결정한다」 · §5.1 「`architecture-api`의 계약이 먼저 있어야 한다」 · §5.2 「API contract가 결정한다」 · §6.3 「`architecture-api` §7.2에서 별도 승인」 · §7 「API contract에 둔다」 · §11 「`architecture-api`를 먼저 사용한다」 · §2.3 승인 wire 보존(파일럿 s023-6.2 b36 동일 배선).
- `agent-design-review-db`(8): §5.2 stable indexed ordering·timestamp+id(§11 「DB consistency … `architecture-db`」 문면) · §7 durable storage/재생/스냅숏(§9.6 저장소 소유 문면 — `check-idempotency-scope-creep` docstring 표제의 «architecture-db §9.6 Idempotency storage 집행»은 **위임처 지목의 문면 근거**일 뿐 enforcedBy 근거가 아니다. 그 checker의 진단은 «미요청 멱등성 산출물 차단» 역방향이라 저장 의무를 집행하지 못한다 — 적대 L3) · §11 b2.
- `agent-design-review-ddd`(7): §1.2 「`architecture-ddd`가 결정한다」 · §3.1 published language `architecture-ddd` §2.5 · birth-enum §3.7(3 Work) · §11 b3.
- `command-dddjango`(7): §2.2 「10번 slot이 승인한 한 경로」 · §6.3 중앙 심사 candidate 제출 · §8·§9.2 검증 보고(절차 산출물 — §16 기본값 표 command+agents 행) · §11 risky domain work 동시 확인.

---

## 3. 재진술 유예 (교차 문서 — 전 웨이브 소급 패스 대상)

`djr:restates`는 **같은 문서 안 쌍만** spec에 넣었다(아래 §3.1). 상대가 다른 문서인 쌍은 그래프 밖이므로 spec에서 생략하고 여기 유예 기록한다(§15 재진술 절 — T3 소급 연결). 상대 좌표는 센서스 restate 열이 아니라 `dddjango/skills/implementation-django-ninja/SKILL.md` **직접 확인**으로 확정했다(SKILL.md 56행 · s001 frontmatter 1–6 · s003 「언제 쓰나」 9–17 · s004 「핵심 운영 원칙」 18–37).

> **좌표 정정(적대 M6 · 2026-08-22)**: s003 경계 4불릿을 처음 12–15로 적었으나 `grep -n` 실측은 REST=**13**·애그리거트=**14**·ORM=**15**·pytest=**16**(12행은 「경계:」 문단 다음 빈 줄)이다. 해당 9행(#2·#4·#5·#6·#7·#33·#34·#35·#37)을 13–16 기준으로 정정했다. s004 참조 행(20–36)·s003 절 범위(9–17)·#36의 11행은 실측상 정확해 그대로 둔다.

| # | 내 블록 좌표 | 상대 문서/절 | 상대 좌표(행) | 관계 |
|---|---|---|---|---|
| 1 | s001/b1 | implementation-django-ninja-skill / s001 | frontmatter `description` 말미 「REST 계약 설계는 architecture-api … implementation-test로 위임」 | 위임 4축 요약 |
| 2 | s001/b1 | implementation-django-ninja-skill / s003 | 13–16 경계 4불릿 | 동상(3중 라우팅 표면의 2번째) |
| 3 | s001/b1 | implementation-django-ninja-skill / s004 | 34 「신규 API는 Django Ninja 목표, DRF는 legacy·migration 맥락에서만 보조 (§10)」 | greenfield 목표·DRF 한정 |
| 4 | s005-1.2/b1 | implementation-django-ninja-skill / s003 | 13 REST 리소스…→ `architecture-api` | 축자 대응 |
| 5 | s005-1.2/b2 | implementation-django-ninja-skill / s003 | 14 애그리거트…→ `architecture-ddd` | 축자 대응 |
| 6 | s005-1.2/b3 | implementation-django-ninja-skill / s003 | 15 ORM 쿼리…→ `implementation-django` | 축자 대응 |
| 7 | s005-1.2/b4 | implementation-django-ninja-skill / s003 | 16 pytest 픽스처…→ `implementation-test` | 축자 대응 |
| 8 | s006-1.3/b1 | implementation-django-ninja-skill / s004 | 20 「Router는 HTTP 어댑터로 얇게…(§1.3)」 | 요약 사본 |
| 9 | s006-1.3/b3 | implementation-django-ninja-skill / s004 | 20 동상(허용 목록 부분) | 요약 사본 |
| 10 | s008-2.1/b2 | implementation-django-ninja-skill / s004 | 35 「신규 도입 시 …버전 핀으로 추가(글로벌 임의 설치 금지) — 핀 표기는 프로젝트 기존 관례 (§2.1)」 | 요약 사본(6 Work 중 2) |
| 11 | s009-2.2/b9 | implementation-django-ninja-skill / s004 | 27 「직접 반환하는 모든 BC 오류 status는 …선언한다 …(§6.2·§8)」 | 요약 사본 |
| 12 | s009-2.2/b10 | implementation-django-ninja-skill / s004 | 27 「오류 선언의 `openapi_extra` 보충과 OpenAPI override…금지」 | 요약 사본 |
| 13 | s009-2.2/b11 | implementation-django-ninja-skill / s004 | 26 「controller는 …구체 known exception을 catch한다 …(§2.2·§6.2)」 | 요약 사본 |
| 14 | s009-2.2/b12 | implementation-django-ninja-skill / s004 | 31 「operation은 `summary`·`description`·`tags`로 문서화하고 (§2.2)」 | 요약 사본 |
| 15 | s009-2.2/b13 | implementation-django-ninja-skill / s004 | 31 「반환 타입을 명시한다(`object` 금지) (§2.2)」 | 요약 사본 |
| 16 | s009-2.2/b14 | implementation-django-ninja-skill / s004 | 30 「선언된 JSON 성공은 Schema/`Status`로 반환한다 …(§2.2·§6.2)」 | 요약 사본 |
| 17 | s009-2.2/b16 | implementation-django-ninja-skill / s004 | 26 「입력 준비 뒤 정확히 한 application call만 좁은 `try`에」 | 요약 사본 |
| 18 | s010-2.3/b8 | implementation-django-ninja-skill / s004 | 28 「프로젝트 `api.py`가 `NinjaExtraAPI` 하나를 소유하고 …(§2.3)」 | 요약 사본 |
| 19 | s010-2.3/b9 | implementation-django-ninja-skill / s004 | 28 「`@api_controller(..., auto_import=False)`로 auto-import…끈다」 | 요약 사본 |
| 20 | s010-2.3/b18 | implementation-django-ninja-skill / s004 | 28 「BC `composition_root/`(`dependency_wiring.py`)는 use-case DI만 소유한다」 | 요약 사본 |
| 21 | s012-3.1/b1 | implementation-django-ninja-skill / s004 | 21 「Request/Response schema는 명시적으로 분리 …(§3.1–§3.2)」 | 요약 사본 |
| 22 | s012-3.1/b7 | implementation-django-ninja-skill / s004 | 22 birth-enum 전문(§3.1) | 요약 사본(7 Work 중 4) |
| 23 | s012-3.1/b8 | implementation-django-ninja-skill / s004 | 23 「validator 위치·`ValidationError.loc`…test 자격이 아니며」 | 요약 사본 |
| 24 | s013-3.2/b1 | implementation-django-ninja-skill / s004 | 21 「ModelSchema는 내부 구현 보호가 확실할 때만 (§3.1–§3.2)」 | 요약 사본 |
| 25 | s016-4.1/b6 | implementation-django-ninja-skill / s004 | 29 「auth 실패는 `None` 또는 framework `AuthenticationError`이며 (§4·§6.2)」 | 요약 사본 |
| 26 | s016-4.1/b7 | implementation-django-ninja-skill / s004 | 29 「`request.auth`에 `ErrorSchema`를 넣지 않는다」 | 요약 사본 |
| 27 | s024-6.3/b3 | implementation-django-ninja-skill / s004 | 23 「`add/update` 뒤에만 mechanics recipe를 적용하고 …(§3·§6.3·§8·§9)」 | 요약 사본 |
| 28 | s025-7/b3 | implementation-django-ninja-skill / s004 | 32 「키 정책(scope·replay·conflict)은 `architecture-api` …(§7)」 | 요약 사본 |
| 29 | s025-7/b8 | implementation-django-ninja-skill / s004 | 32 「저장소·retention(테이블·unique constraint·fingerprint)은 `architecture-db`가 결정」 | 요약 사본 |
| 30 | s026-8/b2 | implementation-django-ninja-skill / s004 | 33 「공개 OpenAPI 변경 후보가 `add/update`이면 mounted API의 생성 문서를 확인한다 (§8)」 | 요약 사본 |
| 31 | s028-9.1/b3 | implementation-django-ninja-skill / s004 | 23 「공개 HTTP는 실제 URLconf에 mount된 Django client로」 | 요약 사본 |
| 32 | s030-10/b1 | implementation-django-ninja-skill / s004 | 34 「신규 API는 Django Ninja 목표, DRF는 legacy·migration 맥락에서만 보조 (§10)」 | 요약 사본 |
| 33 | s031-11/b1 | implementation-django-ninja-skill / s003 | 13 REST 계약 미결 축 | 3중 라우팅 표면 |
| 34 | s031-11/b2 | implementation-django-ninja-skill / s003 | 13·15 (idempotency 저장소는 `architecture-db` 괄호절 + ORM 불릿) | 3중 라우팅 표면 |
| 35 | s031-11/b3 | implementation-django-ninja-skill / s003 | 14 애그리거트·불변식 축 | 3중 라우팅 표면 |
| 36 | s031-11/b4 | implementation-django-ninja-skill / s003 | 11 「Django Ninja Router/Schema/Operation … 코드를 설계·작성할 때 로드한다」 | 3중 라우팅 표면 |
| 37 | s031-11/b5 | implementation-django-ninja-skill / s003 | 16 pytest 픽스처 축 | 3중 라우팅 표면 |
| 38 | s031-11/b1–b6 | implementation-django-ninja-skill / s004 | 36 「라우팅 결정 전 계약·DB·도메인이 미결이면 각 소유 스킬 먼저 (§11)」 | 절 전체의 1행 요약 |

**유예 총 38건.** 상대 문서 `implementation-django-ninja-skill`은 아직 미이관(그래프 밖)이라 `djr:restates`를 걸 대상 블록 IRI가 없다 — 전 웨이브 완료 후 소급 패스가 일괄 연결한다.

**발주서 대비 추가 발견**: 발주서 재진술 열은 `s001`·`s005-1.2`·`s031-11` 3절만 `Y:…-skill/s003`으로 표시했으나, SKILL.md **§s004「핵심 운영 원칙」(18–37행)이 §1.3·§2.1·§2.2·§2.3·§3.1·§3.2·§4·§6.3·§7·§8·§9.1·§10·§11의 요약 사본을 광범위하게 진다**(위 표 8–32·38). 센서스 restate 열이 s003만 잡은 것은 **과소 산정**이라 판정하고 직접 확인 결과를 우선했다.

### 3.1 spec에 실제로 실은 같은 문서 restates (13링크·11블록)

> 계수 정정: 초판 머리글의 「8링크·6블록」은 실물(11링크·9블록)과 어긋난 오기였다. 적대 M5·L7 수리로 2링크·2블록이 늘어 **13링크·11블록**이 실물이다(spec 재집계로 확인).

| 사본 블록 | → 정본 블록 | 근거 |
|---|---|---|
| s009-2.2/b2 | s010-2.3/b1 | 「형태 선택」 blockquote(106–108) 3문장 = §2.3 선두 문단(194–198)의 축약 사본 — 신규 표준 표면·기존 함수형 보존·오류 이유 강등 금지가 1:1 대응한다. 정본은 §2.3(신규 표준 표면 절), §2.2는 §2.3을 자기 문면에서 지목하는 사본. **적대 M5 수리** — 배선표 #25·#27 basis가 관계를 적어 놓고 링크·기록을 빠뜨렸다 |
| s009-2.2/b9 | s023-6.2/b34 · s023-6.2/b30 | 「직접 반환 BC status의 `response=` BC base 선언」+「framework 소유 status 금지」가 §6.2 「응답 선언과 OpenAPI」·「framework 오류 경계」의 축약 |
| s009-2.2/b10 | s023-6.2/b34 | `openapi_extra`·override·postprocessor 금지 — §6.2 b34 4번째 Work와 동일 규범 |
| s009-2.2/b11 | s023-6.2/b29 | 오류 helper/factory/serializer/mapper·등록 handler 우회 금지 — 문면이 「(§6.2)」로 자기 출처를 지목 |
| s009-2.2/b14 | s023-6.2/b35 | 선언 JSON 성공·carveout 4종 — §6.2 b35 3 Work의 축약 2 Work |
| s009-2.2/b16 | s023-6.2/b17 | exception path 3 Work — §6.2 b17과 거의 축자(§6.2가 status 표현 조항을 더 진 상세본) |
| s009-2.2/b17 | s023-6.2/b18 | failed Result/`None` path 2 Work — §6.2 b18의 축약 |
| s016-4.1/b6 | s023-6.2/b31 | auth adapter 성공·실패 반환 규칙 — §6.2 b31의 불릿판 |
| s016-4.1/b7 | s023-6.2/b31 · s023-6.2/b30 | `request.auth` ErrorSchema 금지(b31) + framework 401 전역 변환 금지(b30) |
| s010-2.3/b23 | s008-2.1/b3 | 「ninja-extra의 `INSTALLED_APPS` 등록」 — §2.3 설치 문단(293–294)이 §2.1(90행)의 같은 등록 의무를 반복한다. 정본은 설치·배선을 소유하는 §2.1(사본 쪽이 «의존성 매니페스트 핀은 §2.1과 동일»로 자기 출처를 지목). **적대 L7 수리** — 센서스 재진술 열이 양쪽 N이었으나 원문 대조상 같은 규범이라 링크. 핀 규율 자체는 §2.1 참조일 뿐 사본이 아니라는 발주서 판정은 유지(Work를 따로 세우지 않았다) |
| s024-6.3/b5 | s010-2.3/b1 | 「415 이유의 함수형 강등 금지」 — §2.3 b1이 신규 표준 표면의 정본, §6.3이 사본. §6.3의 역방향 조항(함수형→클래스 자동 변환 금지)은 §2.3에 없는 고유분이라 Work를 따로 세웠다 |

**Work 이중 채번을 남긴 이유(정직 기록)**: 블루프린트 §64는 「정본 1곳만 Work 승격」이지만, 위 사본 중 §6.2·§2.3 상대는 **파일럿에서 이미 채번돼 ISSUED에 append**됐고(R-0001~R-0097·append-only), 사본 쪽도 축약·조건이 달라 완전 사본이 아니다. 파일럿이 §6.1↔§6.2 동일 상황에서 **양쪽 Work + 검수표 「재진술 의심」 기록**을 선례로 남겼으므로(pilot spec basis 문자열 3건) 그 관례를 따랐다. 대신 블록 링크(`djr:restates`)를 걸어 소비층이 중복을 기계 식별할 수 있게 했다. 정본 단일화가 필요하면 T3 소급 패스에서 사본 쪽 Work를 tombstone 처리하는 편이 append-only 원장과 정합한다.

**적대 L8 처분(2026-08-22)**: 적대 리뷰도 같은 상충(§15 「정본 1곳만 Work 승격」)을 지적하되 «파일럿 선례·append-only·발주서 계수 정합을 들어 정직 기록했으므로 반송 사유 아님»으로 판정했다. 이번 수리에서 사본 측 Work를 지우지 않는다 — 지금 지우면 발주서 계수 182와 어긋나고 `load_issued()` 재사용 큐(97건)와도 충돌한다. **소급 패스 처분 대상 목록**을 여기 확정해 둔다: s009-2.2 b9·b10·b11·b14·b16·b17 · s016-4.1 b6·b7 · s024-6.3 b5 · (이번에 추가된) s009-2.2 b2 · s010-2.3 b23.

---

## 4. 경계 판단 메모

**⓪ 파일럿 2절 재수록(도구 계약)** — `ontology_migrate.py`의 `load_issued()`는 `rules/<doc_key>.ttl` 경로의 기존 rid 97건을 `reuse` 큐로 만들고 **명세 등장 순**으로 pop해 label·class 정합을 단언한다. 내 21절만 담은 spec은 첫 규범이 R-0001과 대조돼 즉시 exit 1이었다(실증). 또 `--write`는 `rules/<doc_key>.ttl`을 통째로 재작성하므로 파일럿 절이 빠진 spec은 기이관분을 삭제한다. 따라서 파일럿 spec(`workspace/design/2026-08-19-ontology-t1-migrate/spec-implementation-django-ninja-final.json`)의 2절을 **바이트 그대로·선두에** 실었다. 파일럿 산출물은 읽기만 했고 수정하지 않았다.

**① 절 선두 구분자** — §13대로 헤딩 직후 빈 줄은 **첫 블록의 선두 스팬**에 귀속시켰다(예: s001/b1 = 2–13행, 2·3행이 빈 줄). 그 밖의 블록 간 구분자는 전부 **선행 블록의 후행 스팬**에 넣었다. 결과적으로 각 절의 마지막 블록이 절 끝 빈 줄을 진다.

**② code 블록의 후행 빈 줄** — §13 문면은 code 리터럴을 「여는 펜스~닫는 펜스 전체 라인」이라 하지만, 무손실 커버 의무와 충돌하는 자리(펜스 다음 행이 빈 줄)가 있다. 파일럿 실물(s023-6.2 b5 = 538–543행 — 542가 닫는 펜스, 543이 빈 줄)이 **후행 빈 줄 포함**을 선례로 남겨 그대로 따랐다. 내 code 블록 8개(s009-2.2/b18, s010-2.3/b10·b11·b12·b19, s013-3.2/b3, s019-5.1/b9, s020-5.2/b8, s028-9.1/b4) 전부 동일 규약이다.

**③ 불릿 목록의 블록 분해 규칙** — 일관 규칙을 세웠다: **불릿마다 규범이 서면 불릿 1개 = 블록 1개**(Work↔문장 추적성), **목록 전체가 명사구면 목록 전체 = 블록 1개**(kind=prose). 후자에 해당한 목록: s004-1.1 책임 8항 · s006-1.3 허용 5·금지 5 · s008-2.1 확인 5항 · s013-3.2 확인 4항 · s026-8 candidate 10항 · s028-9.1 candidate 8항 · s029-9.2 보고 재료 5항 · s030-10 checklist 10항. 파일럿 s022-6.1이 단일행 불릿을 블록으로 쪼갠 관례와 정합한다.

**④ kind 판정이 애매했던 자리**

- **수평선 `---`**: 절 끝의 `---`는 규범도 코드도 아니므로 `prose`. 언제나 절 마지막 블록(예: s006-1.3/b5, s014-3.3/b2, s031-11/b7).
- **blockquote**: s001/b1(서두 인용문)·s009-2.2/b2(「형태 선택」)는 §13대로 `> ` 마커 포함 verbatim으로 **norm 블록**에 귀속시켰다(kind 확장 불요). 두 블록 모두 규범 문장을 실제로 진다.
- **번호 목록** s010-2.3/b25–b28(탐색 4단계): 명사구가 아니라 **명령문 4개**라 각각 norm 블록·1 Work. 같은 절의 「요점:」 불릿과 대칭.
- **체크박스**: 이 문서에 `- [ ]`/`- [x]` 형태는 **0건** — `checklist-item` kind 미사용(파일럿과 동일. §12 코퍼스 체크박스 0 실증과 정합).
- **표 행**: 이 문서에 마크다운 표 **0건** — `table-row` kind 미사용.
- **s017-4.2/b1·s026-8/b1**: 절 선두 문단이 순수 정의·사실 서술뿐이라 `prose`(0 Work). 같은 자리라도 규범 문장이 하나라도 있으면 `norm`으로 잡았다(s016-4.1/b1·s019-5.1/b1 등).
- **code 블록 안의 주석 규칙문**: s013-3.2/b3의 `# 노출할 필드를 명시한다 -- …`, s010-2.3/b19의 `# 구체 infra를 고르는 유일한 곳 …`, s019-5.1/b9의 `# 허용 filter key만 명시한다`는 규범문처럼 읽히지만 펜스 안이라 `code` 리터럴의 일부로 두고 Work를 세우지 않았다(발주서 s013-3.2 비고와 동일 판정).

**⑤ 문장 분해가 애매했던 자리(Work 계수)**

- s008-2.1/b2(88행, 한 행 5문장): 「한 행 다문장」 관례라 행 분할 없이 **1블록·6 Work 다중 `statesNorm`**으로 처리(§13 해상도 실현 층). em-dash 뒤 절이 같은 의무의 부정 표현이면 병합(「기억 속/추정 버전을 쓰지 않는다」), 독립 판정이 서면 분리(「핀 표기는 프로젝트의 기존 관례를 따른다」).
- s012-3.1/b7(323–335행, 13행 1불릿·7 Work): birth-enum 조항이 한 불릿에 7개 독립 의무를 담아 최대 밀도 블록이 됐다. 행 중간 분할 없이 다중 연결로 처리.
- s009-2.2/b14 vs 파일럿 s023-6.2/b35: 같은 규범을 §6.2는 3 Work, §2.2는 2 Work로 세웠다. §2.2 문면이 「carveout이며 오류 응답 우회를 허용하지 않는다」를 **한 문장**에 담아 분리 근거가 없기 때문이다(문장 해상도 규약 준수 — 사본이라고 상대 계수를 베끼지 않았다).

**⑥ 절 스팬 경계** — s024-6.3의 끝(853행)은 `---` 없이 빈 줄 2개로 §7과 붙는다. 센서스 스팬(827–853)을 그대로 받아 마지막 norm 블록 s024-6.3/b8이 850–853을 진다(문단 2행 + 빈 줄 2행). 도구의 헤딩+블록 연결 == 절 스팬 단언이 통과해 byte 등가를 확인했다.

---

## 5. 적대 리뷰 처분 기록 (2026-08-22 수리 라운드)

대상: `workspace/eval/t3/reviews/implementation-django-ninja-final-findings.md`(medium 6 · low 10). 처분 근거 한 줄씩은 그 파일 말미 «처분» 절이 정본이고, 여기에는 검수표에 실제로 반영된 변경만 요약한다.

| 지적 | 처분 | 검수표 반영 자리 |
|---|---|---|
| M1 s010-2.3/b20 norm2 | 반영 | §2 배선표 #75 — `check-composition-root.py` 제거·reviewer 단독 |
| M2 s009-2.2/b4 | 반영 | §2 배선표 #28 — `check-usecase-dto-placement.py` 제거·reviewer 단독 |
| M3 s012-3.1/b6 norm3 | 반영 | §2 배선표 #93·§2.1 실독 표 — reviewer 병기 |
| M4 s019-5.1/b5 | 반영 | §2 배선표 #123 — reviewer 병기·근거 축(#143/#144→#139) 교정 |
| M5 s009-2.2/b2 restates | 반영 | §3.1 새 행 + spec `restates` |
| M6 유예 표 좌표 | 반영 | §3 머리글 정정 노트 + 9행(13·14·15·16) |
| L1 #24 · L2 #31 · L3 #152 · L4 #9 · L5 #76 | 반영 | §2 배선표 해당 행(병기 추가 또는 표면·방향 한계 명기) |
| L6 #131 · L9 #3 | 부분 반영 | class는 유지(근거 명기), §2 배선표 해당 행에 판독 근거 기록 |
| L7 s010-2.3/b23 | 반영 | §3.1 새 행 + spec `restates` |
| L8 사본 Work 이중 채번 | 이월(반영 안 함) | §3.1 말미 — 소급 패스 처분 대상 목록 확정 |
| L10 s024-6.3/b8 | 반영(기록) | §2 배선표 #148 — 병합 경계·금지 축 보존 기록 |

**자기 검증 재실행**: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-django-ninja-final.spec.json` → **exit 0**(신규 채번 182 · 재사용 97 — 수리 전후 불변, `--write` 미사용).
