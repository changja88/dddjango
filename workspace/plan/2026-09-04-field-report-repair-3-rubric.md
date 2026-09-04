# 현장 보고 3 — 수리 절차·적대 리뷰 루브릭 (S-1·S-4·S-5 · 2026-09-04 사용자 «착수»)

- 대상: `2026-09-04-field-report-spring-dream-django-stubs-generic-base.md`(원문 · 증거로 보존)의 S-1(django-stubs 제네릭 기저 — 문면 §4 + 검사기 #646 · S-2 흡수)·S-4(딕셔너리-레코드 금지 — §4 결정표 + R-3447 개정 + 검사기 #647 · `json.load` ⓓ 후보)·S-5(ninja `Status` 상자 하나 · base 뭉뚱그림 집행 · `RootModel` 단독 — ninja 문면 2 + architecture-api 계약 1 + 검사기 3). S-3은 R-12 행 추기로 종결(9a258bf). 추적표·결정 정본 = `2026-09-04-field-report-repair-3-issues.md` §2-A~D.
- 성격: 그래프 정본 문면(8 doc_key: houserules-skill · implementation-django-final(말미 새 섹션) · django-web-final(예시 정정) · python-final · ddd-final(예시 정정) · ninja-final · api-final · command-dddjango) + 검사기 규칙 5(두 파일 · byte 미러 · 픽스처·매트릭스·등재 3문서). 실행기(`design_pregate.py`) 무접촉 예정.
- 판형: ⓪ 증거 → ① 문제 리뷰 ×3 → ② 계획 → ③ 계획 리뷰 ×3 → ④ 구현 → ⑤ 구현 리뷰 ×3 → ⑥ 독립 감사·재검. 매회 독립 서브에이전트 3기(A 기술·B 규범·C 증거/표본 외) · 3축(코퍼스 정합·일반화·무손실) · 심각도(BLOCKER/MAJOR/MINOR/검증됨). **이번 배치의 손질 3**(사용자 09-04 동의): ⓐ 범위는 결정 완료 상태로 착수 — ⓪·①에서 확정 방향과 어긋나는 사실이 나오면 진행을 멈추고 브리프 하나로 되돌아온다(조용한 방향 전환 금지) ⓑ ④ 구현·⑤ 리뷰를 두 조각(조각 1 = S-1+S-5 · 조각 2 = S-4)으로 나눈다(릴리즈는 하나) ⓒ 산출에 회신 3 포함 · 원문은 다시 쓰지 않는다(추적표 + 회신 3이 정본).
- 결정 게이트: ⑥ 뒤 «머지 진행» 하나. 릴리즈·push 없음(사용자 요청 시 `make release`).
- 브랜치: `fix/field-report-3`(main bbd1c9b 기점). 산출: `workspace/eval/field-report-3/`(⓪ `evidence/{S1,S4,S5,map}` · rv1 · rv3 · rv5 · rv6). 격리 사본: scratchpad `fr3/`(spring HEAD 7bfe1aa · d2eaafe · c20f525 · f5ee428 · kkebi HEAD 6608fb0). 커밋은 경로 명시.

## ⓪ 조사자 검증 결과 (2026-09-04 — 리뷰어는 이 전제를 공격한다)

조사자 3기(S-1 / S-4 / S-5) 독립 실측 + 코디 직접 확인(지도 `evidence/map/summary.md`). 증거 원문 `evidence/<항목>/summary.md`(스크립트·jsonl 동봉). 두 저장소 읽기 전용 · 검사기·mypy는 `git clone`+`checkout --detach`(+ 사본 안 worktree) 격리 사본에서 · mypy는 spring venv 인터프리터를 사본 cwd로.

### ⓪ 요약 (2026-09-04 · 조사자 3기 완료 — 상세는 evidence/<항목>/summary.md)

- **보고자 수치는 전부 재현**: S-1 39클래스(보고 40 · parler 1 혼입) · 맨몸 13/ignore 17+1/별칭 9 · mypy 26 ✓ · S-4 1,110/828/281 · mypy 70(P1 61+P2 9) ✓ · S-5 mypy 9 ✓ · OpenAPI 200 컴포넌트 f5ee428↔HEAD 바이트 동일 ✓. spring HEAD(7bfe1aa)는 발주측이 빚을 다 갚은 상태(mypy 0).
- **kkebi 표본 외**: S-1 67클래스(ignore 21 · 별칭 31 · TC 분기 안 중간 ClassDef 15 — 제3의 모양 · monkeypatch 0) · S-4 431줄(값 `object` 417 : `Any` 157 — R-3448 형상이 지배) · S-5 상자 둘 6함수 + base 뭉뚱그림 31자리 + `RootModel` 단독 선례(tarot).
- **확정 방향과 어긋나는 사실**(진행 정지 · 브리프 사유): S-1 ⑦ 11건(핵심: `django-stubs-ext`는 dev 전이 의존성 → monkeypatch는 운영 의존성 추가 없이는 부팅 실패 · 현장 68클래스가 전부 별칭 · 제3의 모양 · 보고자 `inlines` 예시 mypy red · #493 선언적 면제 상실 · CBV 코퍼스 예시 3줄 · naming 픽스처 교차 매트릭스) · S-4 ⑧ 13건(핵심: `Form.clean()` 오버라이드 대체 주석 없음 · `Mapping[str, object]` 입구 매개변수 103곳 전부 정당 · `json.load` ⓓ 오라클 정당 형상 100% 포착 · #645 이중 보고 100% · good 픽스처 red · R-3448이 대상) · S-5 ⑧ 7건(핵심: ⓑ ≡ 기존 #63 · ⓐⓒ는 프로필 무관 트리 슬라이스 자리 · ⓐ 근거 문장 과대 · openapi 검사기 문면 stale).
- **어긋나지 않는 것**: S-1 monkeypatch가 23/23 기저를 덮음(상속) · CBV 현장 0 · S-4 코퍼스 모순 2줄뿐(SKILL.md:76 · ddd:1618) · S-5 코퍼스 모순 0 · architecture-api 계약 문면 0(중복 없음) · 픽스처 ⓐⓑⓒ 0.
- 지도(`evidence/map/summary.md`): 8 doc 좌표 · 채번 빈 자리(R-3451~ · #646~) · 섹션 말미 추가 선례 9ef6c4f · 같은 날 2차 개정 IRI `@2026-09-04b` 선례.


## ① 공격 질문 (항목마다 필답 · 판정 병기)

- S-1-1 규모·일반화: 보고자 n(BC 10 · 40클래스 · 14/17+1/9)이 재실측과 맞는가 · kkebi에 같은 형상이 있는가(n=2?) · django-web이 만드는 **CBV 제네릭**(`DetailView[M]` 등)도 같은 함정인가 — 그렇다면 규칙 문장과 #646 기저 집합을 admin·form 너머로 넓혀야 하는가.
- S-1-2 처방의 실효: «기본 = monkeypatch»는 settings·운영 의존성이 레인 허용 경로 밖이라 발주측 전제다 — 양 저장소 monkeypatch 0인 지금 실제 기본은 별칭이 된다. 문면을 «둘 다 적법 · ignore만 금지»로 쓰는 것이 맞는가 · monkeypatch가 네 기저(+CBV)를 상속으로 다 덮는가(patch 목록 실증) · 별칭 방식이 #493(첫 대입 타입)·#645·pre-gate(`TYPE_CHECKING` 최상위 바인딩 계수)와 충돌하지 않는가.
- S-1-3 #646 결정성·무손실: 별칭 해소 범위(같은 모듈 `TYPE_CHECKING` 분기만? 타 모듈 import 별칭은 표면 밖?) · 다중 상속(parler `TranslatableAdmin` + `admin.ModelAdmin`) · 여러 줄 클래스 헤더의 `# type: ignore[type-arg]` · `inlines` 속성 줄 · 오탐(기저 집합 밖 서드파티) · 픽스처 충돌 · 소급(legacy 31클래스 → 앵커 격리 · 브라운필드 update 잎이 그 클래스를 손대면 귀속되는 비용).
- S-1-4 규범 정합: §4 «모든 이름에 타입»(R-3148~3150)·R-3154(프레임워크 선언 면제)·R-3447(프레임워크 오버라이드는 `object`)·R-3163(§6.1 셋업) 과 새 문장의 모순 여부 · S-1g(`inlines: … TabularInline[Any, Parent]` 의 `Any`)가 #645에서 ⓓ 후보로만 남는지 실행으로 확인 — 별도 면제 문장이 필요한가 · «셋업은 발주측»을 어디에 적는가(§6.1 b1 확장 vs §4 b8 한 문장 vs R-12).
- S-1-5 배치: implementation-django **말미 새 섹션**(선례 9ef6c4f · s080-17) vs s038-7 블록 append · django-web s007-6/b9 예시 정정만으로 django-web 레인이 배우는가(§6 산문 한 문장 필요?) · Codex 미러 범위(SKILL.md hand 미러 · final.md byte).
- S-4-1 규모·실현 가능성: 1,110/281 재실측 · kkebi n · HEAD에서 발주측이 실제로 `TypedDict`/`TypeAdapter`로 갚았는가(규칙 실현 증거) · `TypedDict`로 못 옮기는 형상(키가 동적 · 값이 진짜 이질)의 비율과 결정표의 «조회표 `dict[K, 구체 V]`»·«`JsonValue`» 행이 그것을 덮는가.
- S-4-2 «무조건 금지»의 사각: `Mapping[str, object]`/`dict[str, Any]`가 정당하거나 불가피한 자리 — 프레임워크 오버라이드 시그니처(`Form.clean() -> dict[str, Any]` 등 스텁이 `Any`인 곳) · `json.dumps` 입력 · 로깅 `extra` · `TypeAdapter` 입력 자체 · `**kwargs` — mypy strict에서 대체형이 항상 있는가(있으면 무엇) · R-3447 개정 후 «경계 입력은 `object`로 받아 즉시 좁힌다»(cleaned_data·request.user·무스텁 서드파티)는 유지되고 JSON만 `TypedDict`로 갈리는가 — 그 경계선이 레인에게 결정적으로 읽히는가.
- S-4-3 #647 결정성·중복·소급: #645 ⓓ 후보(`dict[str, Any]`)와 같은 줄 이중 보고 처리(#647이 그 자리를 «소유»하고 #645는 건너뛰는가) · 중첩(`list[dict[str, Any]]`·`Optional[…]`) 포함 여부 · 문자열 주석·`Dict`·`typing.Mapping`·`collections.abc` 별칭 · 픽스처 충돌 규모(good 픽스처 정리 목록) · 코퍼스 예시 모순 목록(산문·펜스) — 개정 범위가 «예시 정정 2곳»을 넘는가 · 소급 1,110줄은 앵커 격리되나 브라운필드 update 잎이 손대면 귀속 → 비용 추정.
- S-4-4 `json.load` ⓓ 후보: 오탐률(즉시 좁힘·통과 저장 등 정당 사용 비율) · R-0284 감사 입력 목록 배선 · 감수자가 실제로 집행할 수 있는 형태인가(후보 메시지에 파서 후보를 제시하는가).
- S-4-5 규범 정합: architecture-ddd DTO/VO(§3.x·§4.x)·R-3443(«경계가 좁힘»)·implementation-python 1.12 TypeIs·12 pydantic strict와 결정표의 모순 여부 · HTTP body는 ninja `Schema`(pydantic)가 이미 검증하므로 «외부 JSON은 `TypeAdapter`» 규칙의 대상은 그 밖(파일·타 시스템·`json.loads`)임을 문면이 가르는가 · `TypedDict` vs pydantic 모델 선택 기준이 레인에게 결정적인가 · 결정표 형식(SKILL.md table-row 선례 있음 · houserules-skill엔 0).
- S-5-1 규모·성격: 형상 n(리딩 BC 1 · 5+2+2) 재실측 · kkebi 0? · «플러그인이 만든 모양»인가(예시는 전부 상자 하나) — 1레인 특이면 문면 1문장으로 족한가, 그래도 검사기 ⓐ가 싼가(AST만).
- S-5-2 ⓑ 오탐: R-0681/R-0682 «명시값으로 채운 base 인스턴스면 base» 정당 사례를 AST가 구분할 수 있는가(못 하면 규칙을 «하위 클래스를 가진 base이면서 컨트롤러가 그 base 인스턴스를 직접 반환하지 않음»으로 좁혀야) · 기존 #120~#132·#571과의 겹침 · 리딩 e2e 동결 단언(발주측 OpenAPI 변경)과 검사기 도입 순서.
- S-5-3 ⓒ·계약: `RootModel` 단독 응답을 ninja가 정상 지원하는가(런타임·OpenAPI 컴포넌트 실측) · `Schema` 없는 `schema_out.py` 클래스가 다른 검사기(response-schema-bypass·openapi-* · «응답은 ninja Schema» 류 규칙)와 충돌하는가 · 오류 응답은 `Union[...]` 허용(R-0681)인데 성공 200만 익명 union 금지 — 그 비대칭을 문면이 설명하는가(discriminator 표기·컴포넌트 이름 계약 = architecture-api s022-5.2).
- S-5-4 배치: 문장 1 = R-0687 확장 vs 신설 R · 문장 2 위치(s009-2.2 말미 vs 스키마 절) · architecture-api s022-5.2 계약 문장 · acceptance-tester(OpenAPI 스냅숏 계약)에 미치는 영향.
- MAP-1 지도: 읽는 이·집행 배선이 wiring 선례(houserules → discipline-reviewer+coder · ninja → design-review-api+discipline-reviewer · api → design-review-api)와 맞는가 · 새 섹션 s080-17 렌더가 implementation-django-final에서도 동작하는가(9ef6c4f는 houserules-final) · 8 doc 렌더·미러·rulepack·LEDGER 비용 · 두 조각 분할이 매트릭스 EXPECTED 갱신을 두 번 만드는 비용.
- ⓒ 효과 전체: 5건을 고치면 무엇이 줄어드는가(레인당 왕복·mypy 빚) · 소급 비용 총합(legacy 격리 · 브라운필드 귀속) · «플러그인이 만든 모양 / 검사가 못 잡는 반복 / 발주측» 재분류.

## 3·5단계 3축 · 심각도

수리 2 루브릭 준용. 코퍼스 정합 = 건드리는 IRI·검사기·문법 성문 전수 열거(§4 블록 추가 시 R-3148~3150·R-3447/R-3448과의 관계 · 검사기 추가 시 docstring·registry(R-0345)·rulepack·등재 3문서·픽스처 삼중 등재). 일반화 = Claude/Codex 동일·프로젝트 플래그 비의존·kkebi 대조. 무손실 = 검사기 검출 집합 변화는 «추가만»(#646·#647·ninja 3 — 기존 규칙의 발화 라인 byte 동일 증명 · 두 저장소 retro) · 게이트 강도 불변 · 픽스처 정리는 «새 규칙 때문에만».

## 1단계 결과 (2026-09-04 — 적대 리뷰 3기 A 기술·B 규범·C 증거 · 산출 `workspace/eval/field-report-3/rv1/`)

BLOCKER 0 · MAJOR A 4·B 7·C 3 · 나머지 검증됨/MINOR. 수치는 세 축 모두 조사자와 일치(S-1 39/13/17/9 · S-4 1,110/281·mypy 124 · S-5 상자 둘 8/7/6 · #63 2건).

| 축 | MAJOR | ② 처분 |
|---|---|---|
| A-17 / B-3·B-4 | 지도 좌표 오류 — implementation-django §17(Django 5.x) 실존 · LEDGER 마지막 s093 | 새 절 = **s094-18 «## 18. Django admin·폼 타이핑 — django-stubs 제네릭 기저»**(말미 · 9ef6c4f 동형) · doc_key +1(`implementation-django-skill` 상세 레퍼런스 표 b18) · s038-7 append 기각(`---` 규약) |
| A-2 | #646 ⓑ가 기저 해소에 종속 → 타 모듈 별칭이면 mypy·#646 동시 침묵 | ⓑ 헤더 판정은 **모든 ClassDef**에 기저 해소와 독립 |
| A-11 | `json.load` ⓓ 오라클 «반환» 조건이 `-> object` 정당형을 잡고 구체 주석 무검증을 놓침 | refined 오라클(주석≠object · 반환주석≠object · 컴프리헨션 · 직접 접근 · 리터럴 컨테이너 · 호출 인자 제외) — spring 41·kkebi 8 · 정당형 0 · **ⓓ 전용 번호 #650**(B MINOR-5 · 1행 1술어) |
| A-13 / B-10 | #63 auto 사각 미봉합 — Coordinator R-0331 «Error response와 무관한 G2는 auto»의 «무관» 판정식 부재 | **확장 1**: R-0331 rev2(«무관 = 승인 12-slot 유무 · 12-slot 없이 BC 오류 status를 `response=`에 선언했으면 auto 금지·G1 반송») + 회신 3 안내 |
| B-1 | «monkeypatch는 §6.2 소관이라 발주측» 근거 오류 — §6.2·ninja §2.1은 레인이 의존성을 넣는 선례 | 근거 = «전역 런타임 패치 = 관찰 축 ④(§6.1 R-3134~3137 닫힌 목록)» → 조건문은 **§6.1 b1 R-3163 rev2** · §4 새 블록은 참조 · R-12 문구 |
| B-2 | §2-A 수정 1 ⑤ «`Any` 조건부 구절» 불필요·모순 — `Any` 0 정본 예시가 strict 통과(탐침 A·B·E) | ⑤ **철회** · 대신 **R-3154 rev2**(admin 선언 속성·폼 필드 = 프레임워크 선언 면제 성문 — 검사기 `DECLARATIVE_BASE_NAMES`와 문면 일치) |
| B-5 | R-0349(registry #15 소개행) 개정 누락 | R-0349 rev2에 #648·#649 |
| B-7(MINOR-1) | 결정표 6행 «자리표시 object 금지»가 «입구 object 허용»과 충돌 | «입구 밖» 한정 · 반환 주석의 `object`(루트·컨테이너 원소)는 #647 **ⓓ 후보**(C-1의 `tuple[object,…]` 19건 뿌리 — 실측 spring 8·kkebi 34 형상 · 차단은 안 건다) |
| C-5·C-6 | «P1 뿌리 = 속성·반환 누수 → #647 차단» 22/61 · «mypy 빚 70» 중 67은 발주측 RAG | 회신 3 효과 서술 정직화 · 결정표 6행은 문면+ⓓ |
| C-8 | ⓓ 채널에 앵커 격리 없음(`registry_gate._FINDING_RE`가 `[ⓓ#…]` 미파싱) — kkebi billing ⓓ 127 매 레인 재동봉 | **확장 2**: registry_gate가 ⓓ 라인도 N∖L로 갈라 «ⓓ 신규/legacy»를 보고·sidecar → R-0284 «해당 범위 실행분» = «앵커 차분 신규분» |

기타 반영: A-4 «naming 픽스처 교차 등재» 주장 철회(cross는 good만) · A-19 조각 = **{S-1+S-4} / {S-5+Coordinator+openapi}**(검사기 파일 기준 · 매트릭스 regen 최소) · B-15 규칙 범위 «타입 매개변수에 기본값 없는 django-stubs 제네릭 기저»(`View`·`TemplateView`·`RedirectView` 제외) · B-9 ninja 문장 2를 2a(§3.1 새 b9 `RootModel` 단독)·2b(§2.2 b1 익명 union 금지)로 분리 · B-11 openapi 검사기 stale 문면 + 등재 행 2곳 · C-4 좁히기 도우미 형태(`TypeIs` 면제 + 호출부 ⓓ / `TypeAdapter`) 문면.

### ① 결론

세 항목 모두 **진행**(확정 방향 유지 · 기술 수정만). 결정 밖 «확장» 2건(R-0331 rev2 · registry_gate ⓓ 앵커 격리)은 ⑥ 감사 고지 항목이며 사용자에게 예고한다. 철회 1(§2-A 수정 1 ⑤). ② 계획 = `2026-09-04-field-report-repair-3-plan.md`.

## 2·3단계 결과 (2026-09-04 — 계획 `2026-09-04-field-report-repair-3-plan.md` · ③ 리뷰 3기 A 기술·B 규범·C 증거 · 산출 `workspace/eval/field-report-3/rv3/`)

BLOCKER 0 · MAJOR A 5(#650 오라클 정당형 · ⓔ2 smoke/sidecar 조건 · 등재 집계 셀 · 정본 예시 red 1 · good 픽스처 배치 cross 신규 쌍) · B 6(django-skill b18 실존 → b17 확장 · 정본 예시 · 절차 sha 산식 · #650 문면 · prefLabel 9 · sectionNumber) · C 3(무손실 판형 미명세 · 기대 계수 루트 필터 전 값 · ⓔ2 smoke) — 전부 계획 v2 델타 Δ1~Δ15 로 반영. 세 축 공통 실측: 정본 예시 셋째 인자 생략 → strict green(코디 탐침 포함 3회 독립 확인) · #493 수리 검출 집합 불변(6 대상 0/0) · «HEAD=앵커 → ⓓ 신규 0» 두 저장소 · 구현 전 무손실 판형 `VERDICT: LOSSLESS`. ④ 착수(조각 1 = S-1+S-4).

## 4단계 구현 기록 — 조각 1(S-1 + S-4) (2026-09-04 · 브랜치 `fix/field-report-3` · 커밋 56b27e1 · 계획 v2 Δ1~Δ15 집행)

상세 = `workspace/eval/field-report-3/evidence/impl/piece1-summary.md`(실측표·픽스처·등재·온톨로지·검증 · 스크립트 사본 동봉). 요약: 검사기 #646/#647/#650 + #493 수리 + registry_gate ⓔ2 · 실측 = 기대(rv3-C 루트 필터 뒤 값)와 전 항목 일치(spring #646 18 · #647 594/255+8 · #650 40 · kkebi 21 · 161/253+42 · 1 · #645 위반 byte 동일 · ⓓ#645→#647 1:1) · 온톨로지 신설 12·개정 7·새 절 §18 · target-counts(2917/546/3471/3587) · verify 6/6 · 무손실 12/12(+main 픽스처 9/9) · gate 앵커 «ⓓ 신규 0·귀속 0» 양 저장소. 계획 대비 조정 2: Δ9 good `invoice/panel.py`(ⓓ ②)는 하네스 green 축 «레코드 0» 요건으로 bad 로 이동 · good `order_form.py`·`place_order_use_case.py` 를 ⓓ-free 로 정정. ⑤-1 리뷰 3기 대상.

## 5단계 결과 — 조각 1 (2026-09-04 · ⑤-1 리뷰 3기 A 기술·B 규범·C 증거 · 산출 `workspace/eval/field-report-3/rv5/rv5-{A,B,C}.md`)

BLOCKER 0 · **MAJOR 1**(A N-1 — `_alias_defs` 가 `TYPE_CHECKING` 중간 ClassDef 의 첫 기저만 기록해 mixin-first 형에서 #646 오탐 · 현장 0건 잠복) · MINOR 18(A 8 · B 5 · C 5). 세 축 공통 실측: 4사본 계수 전 셀 재현 · `[#645]` byte 동일 · ⓓ#645→#647 슬롯 키 1:1 · #493 lost/gained 0 · smoke 33/33 · gate «ⓓ 신규 0·귀속 0» · 정본 예시 mypy strict green · ③ 완성 문안과 글자 대조 동일. 정정 = 조각 2 커밋에 합침(A N-1~N-9 코드 · B MINOR-1~5 문안 in-place + codex 이름 · C M1·M4 · 무손실 판형 슬롯 키).

## 4단계 구현 기록 — 조각 2(S-5 + ⓔ1) + ⑤-1 정정 (2026-09-04 · 브랜치 `fix/field-report-3`)

상세 = `workspace/eval/field-report-3/evidence/impl/piece2-summary.md`. 요약: 검사기 #648/#649(트리 슬라이스 · 프로필 무관) + openapi stale 문면 2 · 픽스처 payment 세트(good 상자 하나 두 허용형 · RootModel 단독 / bad 상자 둘 · Schema+RootModel) · 온톨로지 신설 R-3463~R-3467 · 개정 R-0349/R-0331 rev2(auto «무관» 판정식) · 렌더 5 doc · 등재 #648/#649 + #63 stale 정정 · target-counts(2919/546/3476/3594) · ⑤-1 정정 전부 반영(#493 이 별칭 정의 전부를 따라가도록 `_resolved_bases` 신설 포함) · 무손실 12/12(슬롯 키) · gate kkebi ⓓ 신규 0 · smoke 33/33 · 대표 byte 골든 재생성. 커밋 d701df8 — **정직 기록**: 그 커밋 메시지의 «verify 6/6» 은 당시 2차 verify 가 base-core RED(봉인 후 골든 파일 변경 — 봉인 재발행 순서 착오)였으므로 거짓이다 · 봉인 재발행 뒤 **3차 verify 6/6 green**(`evidence/impl/verify4.log`) · 정정 커밋 = `cad221b`(봉인 manifest·기록·루브릭). ⑤-2 리뷰 3기 대상 = d701df8 + 정정 커밋.

## 5단계 결과 — 조각 2 (2026-09-04 · ⑤-2 리뷰 3기 A 기술·B 규범·C 증거 · 산출 `workspace/eval/field-report-3/rv5/rv5-2-{A,B,C}.md`)

BLOCKER 0 · **MAJOR 1**(B — `predicates.md` #648/#649 등재 누락 · `spec_lint ⑥` 이 `ast+` 만 강제하는 도구 사각으로 조각 2 verify 가 안 잡음) · MINOR 14(A 5 · B 5 · C 4). 세 축 공통 실측: #648/#649 4사본 파일·줄까지 재현 · public-surface 6항목 전 셀 동일 · 무손실 12/12 행 단위 동일 · main 픽스처 9/9 · gate kkebi 로그·sidecar byte 동일 · smoke 33/33 · 정직 기록(cad221b) 사실 정확·은폐 없음. 정정 = 조각 2 정정 커밋(아래 추기 · 기록 `evidence/impl/piece2-summary.md` «⑤-2 정정»). 이월: `spec_lint ⑥` 의 `ast` 규칙 predicates 등재 강제(도구 개선 후보).


**⑤-2 정정 커밋 = `30a2a24`**(2026-09-04 · 정정 36경로 · 봉인 재발행 마지막 → `make verify` green 6/6 = `evidence/impl/verify5.log` · 다른 세션 파일 무접촉). 브랜치 커밋 8(56b27e1 · 06fef51 · d701df8 · cad221b · b541870 · f863ce6 · 9578c59 · 30a2a24) — 다음 = ⑥ 독립 감사 + 재검(산출 `workspace/eval/field-report-3/rv6-audit.md`).

## 6단계 결과 — 독립 감사 + 재검 (2026-09-04 · 감사자 1기 · 산출 `workspace/eval/field-report-3/rv6-audit.md`)

감사(HEAD 179017f 대상): **조건부 머지 가능** — 결정 정합 전 문장 좌표 확인 · 무손실 판형 재실행 verdict 첫 37행이 증거와 byte 동일(저장소 12/12 · 슬롯 1:1 655/642/661/55 · 픽스처 RED 4 = 의도) · 회신 3 legacy 수치 전 셀 재현 · kkebi gate 귀속 0·ⓓ 신규 0·exit 0 · 프로브 18파일·기대 69 → 불일치 0(MINOR 사각 4 문서화) · 규범·미러·등재 집계 일치 · `make verify` 6/6 · d701df8 정직 기록 잔존 확인 · 더럽힌 경로 없음. **C1 2**(산문 — issues.md §2-A 수정 1 ⑤ 철회 표기 · 로드맵 18행·§8 stale) → 반영 커밋 `192b886`. **C2 고지 5**(ⓔ1 R-0331 rev2 · ⓔ2 registry_gate ⓓ 앵커 차분 · #646 ⓑ 전 클래스 헤더 · 기술 조정 2(⑤ 철회 · ddd 예시 `FieldValue` 닫힌 union) · #647 면제 셋) → «머지 진행» 브리프. 권고(머지 뒤 소배치)는 회신 3 §4 이월에 합류. **재검(192b886)**: 5항목 전부 ✓ · 남은 C1 0 → **머지 가능**(rv6-audit.md §6). 다음 = 사용자 브리프 «머지 진행».
