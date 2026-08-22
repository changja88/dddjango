# T3 적대 리뷰 — architecture-api-final (spec + worksheet)

> 대상: `workspace/eval/t3/specs/architecture-api-final.spec.json` · `workspace/eval/t3/worksheets/architecture-api-final.md`
> 대조: 발주서 `orders/architecture-api-final.md` · 원문 `dddjango/skills/architecture-api/references/final.md`(638행 실측 일치) · `check-*.py` 27종 docstring 실독 · 파일럿 spec 2건 실독 · `ontology_migrate.py` 검증 전용 재실행(exit 0 재확인 — 절별 Work 계수 32절 전부 발주서와 일치, 총 167).
> 검증 방식: 전수 절 4렌즈. 기계 단언 영역(커버리지·연속·byte 등가)은 도구 재실행으로, 판단 영역(kind·class·배선·재진술)은 원문·docstring·파일럿 실물 대조로 검사했다.

## 요약

- 전수 대사 결과 **절별 규범 수 32/32 일치·무소유 0·worksheet 배선 요약 수치는 spec 실측과 정확히 일치**(146/15/9/3/2/2/1/1/1 재계산 검증). 발주서 스코프 32절 전량 존재, 절 행 범위 전부 현재 파일 헤딩과 일치.
- 그러나 **같은 문서 안 재진술 쌍 3건이 spec `restates`에서 누락**됐다(medium 3). census restate 열(6쌍)만 옮기고, 브리프가 요구한 «같은 문서 안 쌍» 자체의 직접 확인이 census 표시분에 갇혔다.
- 경계·kind, class 판정, 배선 근거 표기에서 low 10건.

## 발견 (심각도순)

### M-1 · medium · 재진술 · s036-8.1

- **주장**: 표 행 355(`| 실패 시 | 서버가 401을 생성하면 적용 가능한 WWW-Authenticate challenge를 보냄 | … |`) = b5는 b8(359행 «RFC 9110 규칙: … challenge를 반드시 보낸다»)의 거의 축자 사본인데 b5에 `restates`가 없다. census가 이 절 규범을 3으로 계수하며 행 355를 미계수한 것 자체가 «사본—미승격» 판정이고, 그 형태의 정본-사본 관계 기록 수단이 §15의 `djr:restates`다(사본 블록에 restates·Work 없음 — 파일럿 ninja §6.2↔§2.2 처리와 동형). 미연결 시 소비층이 표 행의 규범 내용이 왜 Work가 아닌지 추적 불가.
- **수정안**: spec `s036-8.1` b5(355–356)에 `"restates": ["architecture-api-final/s036-8.1/b8"]` 추가. worksheet §3 같은-문서 목록에 1쌍 추가.

### M-2 · medium · 재진술 · s018-4.2

- **주장**: b20 W2(168행 «Retry-After를 공개하는 경우 **§5.4의 경계에 따라** controller가 그 헤더를 소유한다»)는 문면이 §5.4를 명시 지목하는 s026/b1 W3(«presentation controller가 직접 공개하는 retryable BC 오류는 승인된 Retry-After 헤더를 그 controller가 소유한다»)의 같은-문서 부분 재진술이다. 같은 검사기(`check-api-error-controller-contract.py`)·같은 파일럿 선례(ninja §6.1 b15)를 양쪽 basis가 인용하면서도 restates 미연결. 병렬 사례인 s056-12.4/b2→s026/b1은 연결돼 있어 취급이 비일관하고, spec s026 note의 부분 재진술 열거(s033-7.2·s036-8.1·s056-12.4)에도 b20이 빠져 있다. worksheet §3-2는 이 문장의 **교차 문서** 상대(ninja b15)만 기록했다 — 같은-문서 정본이 우선이다.
- **수정안**: spec `s018-4.2` b20에 `"restates": ["architecture-api-final/s026/b1"]` 추가(발주서 재진술 열 N은 census 누락 — worksheet census 대사에 판정 한 줄 추가). s026 note의 재진술 열거에 s018-4.2/b20 추가.

### M-3 · medium · 재진술 · s059-13.2

- **주장**: b4 W2(547행 «… HTTP status·응답 표현은 presentation이 소유한다(application·domain은 status를 만들지 않는다; **§13.3**)»)는 문면이 §13.3을 직접 지목하는 s060-13.3/b10(W3·W4)의 같은-문서 부분 재진술이다. spec의 b4 W2 basis 스스로 «§13.3 b10 과 같은 축»이라 적으면서 restates는 걸지 않았다 — 축 동일성을 인지하고도 미연결한 실증.
- **수정안**: spec `s059-13.2` b4에 `"restates": ["architecture-api-final/s060-13.3/b10"]` 추가.

### L-1 · low · 경계kind · s013-3.1 (외 표 보유 13절 공통)

- **주장**: 머리행+구분행을 한 table-row 블록으로 병합(예: s013-3.1 b1=[92,94], s018-4.2 b2=[142,143])했다. 파일럿 판형(ddd s051-8)은 구분행을 **단독 블록**([2061,2061])으로 뒀고, 브리프 kind 정의도 «table-row(머리행·구분행 포함 **행 단위**)»다. §13의 자연 단위 «표 행 묶음» 읽기로 방어 가능하고 byte 등가·계수(데이터 행만 산입)에는 영향이 없어 low.
- **수정안**: 파일럿 판형대로 구분행 분리, 또는 worksheet §4.1에 «파일럿 판형(구분행 단독 블록)에서 의도 이탈 — §13 표 행 묶음 근거» 명기(현재 기록은 이탈 사실을 밝히지 않음).

### L-2 · low · 경계kind · s065-14.3

- **주장**: 규범 없는 연속 불릿 9개를 한 prose 블록([600,609])으로 병합했는데, 같은 문서의 연속 무규범 불릿 s036-8.1 357·358행은 블록을 분리(b6·b7)했다 — 같은 형태에 두 규약. §13 자연 단위 열거에 «불릿»이 있어 병합 쪽이 더 방어가 필요하다.
- **수정안**: 병합/분리 중 하나로 통일(권장: 파일럿·타 절과 같은 불릿별 분리), 최소한 worksheet §4.1에 두 사례의 판정 차이 근거 병기.

### L-3 · low · 규범식별 · s033-7.2

- **주장**: 319행 «구체적인 것이 우선한다.»는 **우선** 서술인데 prose 미계수다. HTTP q값 협상의 프로토콜 동작 서술이라는 방어(P0 미계수 승계·worksheet note)가 있어 low로 두나, 콘텐츠 협상 설계 시 참조되는 우선 규칙이라 채번 여지가 있다.
- **수정안**: 현 판정 유지 시 종결 가능. census 소급 검토 목록에 후보로 기재.

### L-4 · low · 규범식별 · s029-6.2

- **주장**: 280행 «문제 유형 정의에서 추가 가능»은 확장 필드 추가 **허용**(Permission) 문면인데 미채번(블록 계수는 무시 의무 1만). RFC 서술의 인용이라는 방어 가능 — low.
- **수정안**: 현 판정 유지 시 종결 가능. census 소급 검토 후보로 기재.

### L-5 · low · 규범식별 · s066-14.4

- **주장**: b2(613행 «명세 작성 도구(Swagger Editor, Stoplight 등) 활용»)를 Permission으로 판정했으나 문면은 지시형 불릿이다 — 허용되는 것은 «어느 도구인가»뿐이고 «도구를 활용하라»는 의무 독해가 자연스럽다(Obligation 후보).
- **수정안**: class 재검토. 유지 시 worksheet §4.2 규약 표에 «지시형+선택지 병기 → Permission» 유형을 명시적으로 추가.

### L-6 · low · 규범식별 · s043-9.3

- **주장**: b3(419행 «페이지당 100-200개 결과 권장»)의 Obligation 판정 — «권장» 문면의 Obligation 승격은 worksheet §4.2 «단일 권장값=준수 대상» 규약으로 문서 내 일관되나, s042-9.2의 «권장» 열은 Permission이라 문면 층위에서 갈린다(매핑 표/단일 값 구분 규약은 이해 가능 — 이견 수준).
- **수정안**: 코퍼스 횡단 class 규약 확정 시 재검토 대상으로 태그. 현 판정 유지 가능.

### L-7 · low · 배선 · s022-5.2

- **주장**: b1 W1(«상태 코드별 본문 존재 여부·schema 분리 **정의**») enforcedBy `check-response-schema-bypass.py` — docstring 축은 «선언 schema를 우회하는 raw 200-203 반환 차단»(구현 백스톱)이라 계약 «정의» 의무의 정면 커버가 아니다. D(design-review-api) 병기와 파일럿 b35 선례 인용으로 완화돼 있어 low이나, 과배선 소지(검사기는 정의 존재를 검사하지 않고 우회만 차단).
- **수정안**: E 제거 또는 basis에 «부분 백스톱(정의 의무 자체는 위임 소유)» 한정을 명시.

### L-8 · low · 배선 · s024-5.4

- **주장**: b5 basis의 «① 문면 wire 필드» — 4원 ①은 «문면 **역할명**»(«schema checker» 류)인데 «wire 필드»는 역할명이 아니라 문면 어휘다. 실질 배선은 ②(§16 매핑 표 «schema checker»=check-error-centralization)+파일럿 b14 선례로 성립하므로 배선 자체는 유지 — 근거 슬롯 표기만 오용.
- **수정안**: basis에서 ① 표기를 제거하고 ②·④만 남긴다.

### L-9 · low · 규범식별 · worksheet §4.2

- **주장**: Prohibition 행의 «총 30건»은 spec 실측 Prohibition 24건과 불일치(실측: Obligation 122·Prohibition 24·Permission 15·Exception 5·Override 1 = 167). 24+Exception 5+Override 1=30이라 «비단순-의무 계열 합»이 혼입된 것으로 추정.
- **수정안**: worksheet 수치를 24로 교정(또는 셈 기준을 명시).

### L-10 · low · 재진술 · s060-13.3 / s039-8.4

- **주장**: 절 내 쌍 2건 미연결 — ⓐ s060-13.3 b5(560행 Replay 행) ↔ b10 W1(566행 Replay 재현 문단), ⓑ s039-8.4 b4(385행 insufficient_scope 행) ↔ b6 W2(388행 403+insufficient_scope 응답). 표 행=계약 항목, 문단=상세라는 «요약-상세» 독해가 가능해 재진술 단정은 어렵다 — low.
- **수정안**: 소급 패스에서 same-section 쌍 규약(요약-상세는 재진술 아님 등)을 정하고 그 기준으로 재판정.

## 검사했으나 반박 불성립(주요 무혐의)

- **행 번호·스코프**: 32절 헤딩 행 전부 현재 파일과 일치, 드리프트 없음. NAR 절 미포함.
- **계수 대사**: 절별 발주서 규범 수 ↔ spec 규범 수 32/32 일치(도구 절별 Work 출력으로 재확인). worksheet가 스스로 판정한 배분 갈림 3건(s024-5.4·s056-12.4·s060-13.3)은 원문 문장 실측과 부합.
- **배선 실물 대조**: `check-ninja-boundary-middleware.py`(406/415 전역 미들웨어 자작 회귀·settings.MIDDLEWARE 한정), `check-idempotency-scope-creep.py`(G0/G1 미요청 채택 차단), `check-error-centralization.py`(profile-gate·preserve는 schema semantics 미적용), `check-openapi-error-declaration.py`(openapi_extra.responses·response={status: ErrorSchema}) — basis 인용 전부 docstring 실물과 일치. `check-api-error-controller-contract.py`의 controller 소유·중앙 handler 차단·header 대입 검증(`_header_assignment_valid`)도 본문에서 실재 확인. 비커버 주장 3건(check-naming=파이썬 경로·심볼 축, check-transient-overmapping=과잉매핑 차단 역방향, check-transaction-boundary=UoW 축)도 docstring과 부합 — 기본값 도피·허위 basis 불검출.
- **기본값 이탈**: command-dddjango 9건·design-review-db 1건 전부 문면 근거(G0/G1·G2·12-slot·STOP·«DB 설계로 연결») 실재. `dddjango/agents/design-review-db.md` 실존 확인.
- **재진술 방향(발주서 6쌍)**: 전부 spec restates에 실연결·대상 블록 실존·교차 문서 상대는 spec 미기재(브리프 준수). worksheet §3 교차 문서 유예 9건의 좌표도 발주서 비고·검사기 docstring과 정합.
- **무소유 규범 0** · worksheet 배선 요약 9행 수치 전부 spec 재계산과 일치.

*리뷰어: T3 적대 검증 서브에이전트 · 2026-08-22 · spec/worksheet 무수정.*

---

## 처분 (수리자 · 2026-08-22)

> 대조: 원문 `dddjango/skills/architecture-api/references/final.md` 실독 · 브리프 `T3-authoring-brief.md` · `ontology-authoring.md` §13·§15·§16 · 파일럿 spec 2건 · 형제 T3 spec 14건 실측.
> 재검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/architecture-api-final.spec.json` → **exit 0**(`--write` 미사용). 규모 REF 32절 · 블록 188→**196** · Work **167 불변**.
> 셈 기준: **fixed** = 지적이 가리킨 결함을 실제로 닫았다(spec 판정·표기 변경, 또는 지적이 «누락»이라 한 문서화를 채움). **rejected** = 지적된 판정을 원문 대조 끝에 **유지**했다(맹종 금지 — 근거를 남기고, 잃지 않도록 검수표 §4.5 소급 후보로 고정).
> 결과: **fixed 9 · rejected 4**. spec 변경은 medium 3 + low 4, 나머지는 검수표 문서화. **Work 167·절별 계수 32/32 는 전 처분에서 불변**이라 발주서 대사에 영향이 없다.

| # | 심각도 | 처분 | 근거 (한 줄) |
|---|---|---|---|
| M-1 | medium | **fixed** | 355행 «서버가 401을 생성하면 적용 가능한 `WWW-Authenticate` challenge를 보냄» ↔ 359행 «서버가 401 응답을 생성하면 … challenge를 반드시 보낸다» 는 조사·«반드시»만 다른 축자 근접이고 **b5는 Work 0(미승격 사본)** — §15의 «정본 1곳만 승격 + 사본 블록 `djr:restates`» 정면 케이스라 `s036-8.1/b5 → b8` 연결. |
| M-2 | medium | **fixed** | 168행이 «**§5.4의 경계에 따라** controller가 그 헤더를 소유한다»로 정본 절을 명시 지목하고 소유 절이 s026/b1 W3와 축자 근접 — 병렬 사례 `s056-12.4/b2→s026/b1`이 이미 연결돼 있어 미연결은 비일관. `s018-4.2/b20 → s026/b1` 연결 + s026 note 열거 보정 + census 재진술 열 `N`이 과소라는 판정을 검수표 §1에 기록. |
| M-3 | medium | **fixed** | 547행이 «…; **§13.3**»으로 직접 지목하고 «application·domain은 status를 만들지 않는다» ↔ b10 W4 «application·domain은 status를 catch·생성·저장하지 않는다»가 축자 근접 — basis가 스스로 «§13.3 b10 과 같은 축»이라 적고도 미연결한 것이 맞다. `s059-13.2/b4 → s060-13.3/b10` 연결. |
| L-1 | low | **fixed(문서화 분기)** · 재분할은 **반려** | 이탈 사실은 실재하므로 검수표 §4.1에 파일럿 판형 이탈과 §13 «표 행 묶음» 근거를 명기했다. **재분할은 반려** — ⓐ 파일럿도 «1행=1블록»이 아니고(빈 줄+머리행 `[2059,2060]` 병합) ⓑ 형제 T3 spec 실측이 병합 39·분리 24 로 코퍼스 관례 미확정 ⓒ byte 등가·데이터 행 계수 무영향 ⓓ 14절 전 절 재분할은 후속 서수를 밀어 `restates` 에지 10개 좌표를 흔든다(정정 이득 0·회귀 위험 有). 소급 후보로 §4.5에 고정. |
| L-2 | low | **fixed(분리 채택)** | 실측 확인: `s065-14.3/b2`가 이 문서에서 **유일한 다불릿 병합**이었다(나머지 전 절 1불릿=1블록). §13 자연 단위 열거가 «불릿»을 단위로 들고 같은 문서 357·358행은 이미 분리돼 있어 두 규약 공존이 맞다 — 9불릿을 블록으로 분리(절 마지막 블록이라 타 절 서수·`restates` 좌표 무영향, 블록 188→196). |
| L-3 | low | **rejected(판정 유지)** + 소급 후보 기재 | 319행의 주어는 설계자가 아니라 HTTP 협상 알고리즘이다(q값 예시 직후의 매칭 규칙 서술 — 수범자 없음). 승격 시 절 계수 7→8로 발주서와 어긋난다. 리뷰어 자신의 «현 판정 유지 시 종결 가능»에 따라 검수표 §4.5 소급 후보 1로 고정. |
| L-4 | low | **rejected(판정 유지)** + 소급 후보 기재 | 280행 «문제 유형 정의에서 추가 가능»은 RFC 9457 본문의 인용 서술이고 수범자가 이 파이프라인이 아니다(같은 문장의 «클라이언트는 … 무시해야 한다»만 의무로 채번). 승격 시 절 계수 1→2. §4.5 소급 후보 2. |
| L-5 | low | **fixed(class 교정)** | 지적이 옳다 — 613행은 지시형 불릿이고 괄호는 «도구를 쓰지 않을 자유»가 아니라 도구 *예시*다. 종전 판정은 이 문장을 «상황→선택지 매핑 **표**» 규약 행에 끼워 넣어 형태가 어긋났다. Permission→**Obligation**, §4.2 규약 표를 «산문 «권장»·지시형 단일 값»으로 정정(같은 절 b1·b3 및 s043-9.3 b3와 일관). |
| L-6 | low | **rejected(판정 유지)** + 소급 후보 기재 | 419행은 대안 없는 단일 값(«100-200개»)이고 s042-9.2는 상황별로 셋이 다 정당한 매핑 표다 — 문서 내 규약(§4.2 1·2행)으로 층위가 갈리는 근거가 성립한다. 리뷰어도 «이견 수준»으로 명시. 코퍼스 횡단 규약 확정 시 재검토하도록 §4.5 후보 3에 태그. |
| L-7 | low | **fixed(한정 명기)** · E 제거는 **반려** | docstring 실독 결과 축이 «선언 schema를 우회하는 raw 200-203 차단»인 것은 사실이라 basis에 «**부분 백스톱** — 정의 존재는 검사하지 않으며 정의 의무 자체의 소유는 위임»을 명기했다. **E 제거는 반려** — 같은 축(상태 코드별 선언 schema 경유)에 검사기 문면이 정면으로 닿는데 위임만 남기면 §16이 금지한 «기본값 도피»가 되고, D는 이미 병기돼 있다. |
| L-8 | low | **fixed** | §16의 4원 ①은 검사기를 가리키는 *역할명*(«schema checker» 류) 슬롯인데 «wire 필드»는 규범의 대상 어휘다 — 표기 오용이 맞다. basis에서 ① 주장을 철회(«역할명 없음»으로 정정)하고 ②(§16 매핑 표)+④(파일럿 b14)만 남겼다. 배선 자체는 불변. |
| L-9 | low | **fixed** | 재계산 확인: Obligation 122·Prohibition 24·Permission 15·Exception 5·Override 1=167. «30»은 24+5+1 혼입이 맞다 — 검수표 §4.2를 **24**로 교정하고 실측 분포 한 줄을 병기했다. |
| L-10 | low | **rejected(유예 유지)** + 규약 명문화 | 두 쌍 모두 **양쪽이 각자 Work로 승격**됐고 § 지목이 없으며, 표 행은 계약 항목·문단은 부정형 상세(«현재 상태 재조회가 아니다»)로 서로 다른 내용을 더한다 — 재진술로 연결하면 별개 채번 판정과 모순된다. 대신 §4.4에 판정 기준 표(ⓐ 미승격 사본→의무 · ⓑ 명시 지목+축자 근접→연결 · ⓒ 요약-상세→유예)를 명문화해 M-1~M-3와의 경계를 고정하고 §4.5 후보 4로 넘겼다. |

**반영 산출물**: `workspace/eval/t3/specs/architecture-api-final.spec.json`(restates 3 추가 → 사본 블록 9·에지 10 · s065-14.3 블록 분리 · class 1 교정 · basis 2 정정 · note 3 갱신) · `workspace/eval/t3/worksheets/architecture-api-final.md`(§1 재진술 판정 1 · §2 배선 표 3행 · §3 같은-문서 9쌍 표 신설 · §4.1 판형 근거 2 · §4.2 class 분포·규약 3 · §4.3 배선 한정 2 · §4.4 판정 기준 표 · §4.5 소급 후보 표 신설).

*수리자: T3 spec 수리 서브에이전트 · 2026-08-22 · 원문·`ontology/`·타 spec 무수정.*
