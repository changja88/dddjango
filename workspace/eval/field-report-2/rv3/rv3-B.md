# 현장 보고 수리 2 — ③ 계획 리뷰 · 리뷰어 B(규범 축 — 문면·착지·개정 종류·채번·미러 표면) (2026-09-04)

독립 리뷰. 읽은 것: ② 계획 → 루브릭(⓪·①·결정 1·2) → rv1-B → `ontology/rules/{implementation-python-final,discipline-houserules-skill,discipline-houserules-final,implementation-django-ninja-final,discipline-tdd-final,agent-design-architect,architecture-ddd-final,command-dddjango}.ttl` · `ontology/wiring/*` · `ISSUED` · `LEDGER.tsv` · `vocab/djr.ttl` · `shapes/djr-shapes.ttl` · authoring §5·§13·§14·§16 · DEVELOPMENT §3 · 선례(`git diff 36e9f11 191842a` · f2d4df0 · 9ef6c4f · 4699d7e · b5f226a) · 메모리 레시피 · 도구(`ontology_render.py`·`ontology_structural_check.py`·`corpus_mirror_sync.py`·`spec_lint.py`). 저장소 무수정(이 파일만 신규).

## 1. 판정 표

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| D 문면 R-3446 | **MINOR** | 규범 무모순(R-2720 은 «반환 경로 있음» 이라 대상 밖). «`__init__` … `-> None` 이 문법이라» 는 사실 오류(문법이 아니라 타입 규약 — mypy 가 `__init__` 반환을 `None` 으로 강제). `Never`(3.11+) 병기 누락. 형식은 §4.4 b1 «> dddjango 경계 단서:» 와 같은 blockquote 관용이 자연(출처 태그 절의 플러그인 단서 관용 — final 4문서 각 1건) |
| D 착지·채번 | **검증됨** | `s032-4.4` b1·b2 → **b3 = 다음 미사용 서수 = order 3(말미 append · 밀림 0)** ✓. Obligation ✓. wiring 은 계획에 **부재**(아래 §4) |
| E R-3447/R-3448 문면 | **MAJOR(순서)** + MINOR | 문면 자체는 R-3148/R-3149/R-3150·R-3443·§4.1 R-3158 과 무모순(무조건형 = R-3150 정합). 단 «집행 문장(R-3447 귀속)» 을 **R-3448 문장 뒤** 에 두면 §13 «문장 등장 순 = 채번 순» 위반 — R-3447 문장군 안으로 옮기거나 블록을 둘(b7 R-3447 · b8 R-3448)로 쪼갠다. «§1.12» 는 문서 미지정(SKILL.md 안에서 타 스킬 절 참조) → «implementation-python §1.12». «받는 즉시 좁힌다» 와 R-3443 «값 객체를 부르기 전 경계» 는 «어디서» 의 이중 성문 위험 → R-3443 참조로 소유 분리 |
| E 착지 b7 | **검증됨** | `s007-4` b6 이 절 말미 → b7 = order 7 ✓(§4.2 신설보다 작다 — Section·headingSnapshot·LEDGER 행 0). 무조건형 문면이 b6 «표준 문서군 예시 면제» 바로 뒤에 오는 독서 흐름 무리 없음 |
| E R-0345 amendment | **검증됨** | `s007/b28` 단일 Work·rev1 → rev2 amendment(레지스트리 소개행에 규칙 추가 = 확장) ✓. «ⓓ#645» 표기는 md 선례 0(검사기 docstring 관용) → md 관용 «ⓓ 후보(#645)» |
| E wiring | **MAJOR** | 계획 «R-3448 delegatedTo **a/agent-coder** · R-3148 배선 복제» 는 이중 오류 — §4 Work 중 agent-coder 위임 0(전부 discipline-reviewer 또는 enforcedBy public-surface) · R-3148 은 enforcedBy 만(검사기가 «좁힘» 을 못 보므로 복제하면 오배선 · §16 «기본값 이탈은 문면 근거 필요»). 정답: R-3448 `delegatedTo a/agent-discipline-reviewer`(R-3156/R-3157 형) · R-3447 `delegatedTo a/agent-discipline-reviewer ; enforcedBy c/check-public-surface-annotation.py`(R-3150/R-3158 형 — ⓓ 후보는 감수자 집행이므로 둘 다) |
| F-1 R-0719 amendment | **MAJOR(위치)** + MINOR | amendment ✓(의무 확장 · rev2). 그러나 **b18 «말미» 추가는 §13 위반** — b18 = R-0718(s1)·R-0719(s2)·R-0720(s3)·R-0721(s4) 순이라 R-0719 문장을 s4 뒤에 두면 «등장 순 = 채번 순» 이 깨진다 → «(매요청 조립).» 직후·«이벤트 구독 결선은…» 앞에 삽입. «어댑터가 선언한 Protocol» 은 «꽂히는 자리(생성자 인자)가 선언한 Protocol·`Callable`» 이 정확(증거 F 의 대조 기준). «#85» 인용은 ninja final.md 에 #85 성문 0 이나 검사기 번호 인용 선례(§4.4 b1 «#453·#454·#571» — houserules final.md 에 성문 0) 로 적법 |
| F-2 R-3450 착지 | **BLOCKER(좌표)** | **`s025-5.5/b26` 은 실존 블록**(«- Python·Django·Pydantic·Django Ninja 등 framework/stdlib 의 기본 동작» — **비자격 블랙리스트 첫 항**, 최대 서수 b48). 계획대로 «b26» 에 쓰면 IRI 충돌 또는 반대 의미 목록에 착지. 더구나 **코퍼스 2,901 블록 전부 서수 = order 이고 블록 신설 커밋 9건 전부 order 재배열 0(말미 append 만 · 9ef6c4f «밀림 0» 명시)** — 목록 중간 삽입 선례 자체가 없다. 렌더러(`ontology_render.py:76`)·구조검사 ③(`:274`) 은 order 1..n 연속만 요구하므로 «b49 + order 25 + b25~b48 order +1» 은 기계적으로 가능하나 선례 0·서수≠order 24건 발생 → 기각. **정합 해법 = b24 텍스트 확장**(b24 는 Work 0 불릿 — «- 별도 사용자 승인 … 공개 Python 계약\n- composition root …\n\n» 2불릿 1블록 · s038-5.3/b3 다불릿 선례 · f2d4df0 이 기존 블록 말미를 in-place 편집한 선례) + b24 `statesNorm R-3450`. Block +4 → **+3** |
| F-2 문면·양태 | MINOR | Permission ✓(R-2155/R-2158 과 동형). «**실배선 1경로**» 는 quota 어조(rv1 기각 사유 재유입) → 대상 명사구로. 괄호 «대체하지 못한다» 는 Permission 안의 금지 어조 → «이 대상의 보호가 아니다»(정의문). 모델링 선택 병기: 화이트리스트 항목 6개가 전부 Work 0(R-2155 «목록» 이 Work) 이라 «항목마다 Work» 는 목록 모델과 어긋남 — 대안 = Work 없는 불릿 + **R-2155 amendment rev2**(목록 +1). 어느 쪽이든 기록 |
| G R-3427 rev4 | **MINOR(종류·참조)** | 문면은 #93 정의(`port/**` 전체)·R-3425 태그 의미론·R-3436·S3 문면과 무모순. 종류: vocab 은 라벨만(clarification=«명확화» · amendment=«규범 개정» · redefinition=«지시 대상 변경») · 도구 소비 0 · 선례 4699d7e(R-3443 rev2 «범위를 닫음» = clarification) 로 «경계 정의를 닫음» 은 clarification 통용 가능. 그러나 실전 독법 ⓑ(2/2) 에서 새 행 의무가 생기고 소급 형식 red 2 → 정직한 분류는 **amendment**(redefinition 아님 — 지시 대상 «경계 import» 불변). «(S3)» 은 architect 문서에 S-id 언급 0(Coordinator 만 «S7» 1회) → «실행기 사각 S3(pregate-report 헤더)» 로 풀어 쓴다. «#92~#96·#185/#186» 인용은 architect md 규칙 번호 17종 선례로 적법 |
| G R-3449 착지 | **MAJOR(좌표)** + 착지 재검토 | **`s038-5.3/b6` 실존**(«어댑터 배치 기준» R-0592~0594) → 신설은 **b7 = order 7(말미)** 만 가능(«b5 뒤·b6 앞» 은 중간 삽입 = 선례 0). «한 주제 한 소유자» 로는 **§3.6 응용 서비스 `s023-3.6/b3` «응용 서비스의 책임» 불릿 +1**(«- 결과를 리턴한다» 뒤 · b3 텍스트 확장 · statesNorm += R-3449 · 밀림 0) 이 더 정확 — «port 예외 번역» 은 헥사고날 «채택 조건/포트 작성/어댑터 배치»(§5.3) 가 아니라 응용 서비스의 책임이다. §5.3 b7 도 허용(둘 중 하나 ④ 확정). 문면 «자기 실패(예외)» 는 칸을 박는다: `application_layer/<area>/exception.py`(트리 48행 — #92 가 잎에 허용하는 유일한 예외 칸) |
| H R-3181 rev3 | **MINOR(종류·어휘)** | «내용 규칙은 내용이 생긴 뒤부터 선다 · 검사기는 건너뛴다 · 삭제로 red 를 푸는 것은 #488 위반» 은 **새 시점 규칙 + 새 금지** → clarification 이 아니라 **amendment**(rev2 09-01 도 amendment). 양태가 R-3181(Obligation) 과 달라 새 Exception Work(같은 b3 · b1 «3 Work 혼합형» 선례) 도 정당 — 결정 2 «규범 1줄» 과 양립. «registry #2» 는 houserules final.md 에 «registry» 어휘 0 → «Coordinator 의 빈 모듈 inventory 제외(R-0319)» 로. «(`skeleton_placeholder`)» 함수명은 md 선례 0 → «검사기의 «내용 없는 골격» 판정(0바이트·docstring/주석뿐)». R-ID 직접 인용은 선례 있음(ddd §3.1 «(R-3442)»·«(R-3443)» · command «R-3434») |
| 채번 R-3446~3450 | **검증됨** | ISSUED 는 append-only·문서 간 순서 무관(R-3442/3443 ddd 가 R-3441/3444 command 사이에 끼는 선례). 한 블록 안 순서만 규약(§13) — E b7 의 R-3447→R-3448 순 ✓ |
| 공백 규약 | 검증됨(조건부) | b24 `\n\n`→`\n` 이관은 **블록 신설 시** 규약(§13 · f2d4df0 b7→b8 실증). b24 확장형을 택하면 이관 없음(b24 말미 `\n\n` 유지 · 두 불릿 사이 `\n`) |
| 미러 표면 | **MAJOR(누락)** | 계획 «ttl 5문서·render ×5·final.md 4·SKILL.md 2» → 실제 **doc_key 8 · LEDGER 재기준선 8행 · final.md 5(+houserules final) · codex 손 미러 3(+`dddjango-discipline-houserules/SKILL.md`)** · spec_lint 표면 3(+`2026-08-11-predicates.md` · 집계표/읽는 법 수치) — §5 |

## 2. 문면별 상세 · 대체 문면

### D — R-3446 (`s032-4.4` 새 b3 · order 3)

- (a) 모순·중복: §4.4 b1 R-2720(«부재·거절은 답» — 결과 분기·조회 `None`) 은 «반환 경로가 있는» 함수의 규범, 새 문장은 «정상 반환이 없는» 함수의 선언 규범 → 서로소. §1.2 R-2712/R-2713(Optional 값), §15(예외 설계), §23.3(`assert_never` — exhaustiveness) 어디에도 중복 없음. 코퍼스 `NoReturn`/`Never` 0 재확인.
- 사실 오류 1: «`__init__` 의 생성 차단 가드는 `-> None` 이 **문법**이라» — Python 문법은 `__init__` 반환 어노테이션을 제한하지 않는다. mypy/pyright 타입 규약(«The return type of "__init__" must be None»)이다.
- (d) 표기: `possibly-undefined` 는 mypy 선택 오류 코드(`enable_error_code`) — 표기는 무방(R-3158 «mypy strict 는 …» 도구 동작 언급 선례).
- **대체 문면**(b3 · kind-norm · statesNorm R-3446 · 말미 `\n\n` · b1 관용의 blockquote):
  > «> dddjango 단서: 본문의 모든 경로가 `raise` 로 끝나 정상 반환이 없는 함수는 `-> None` 이 아니라 `-> NoReturn`(3.11+ 는 `Never` 동치)으로 선언한다 — `-> None` 이면 호출부의 흐름 분석(도달 불가·미정의 가능 `possibly-undefined`)이 깨진다. `__init__` 의 생성 차단 가드는 타입 규약이 `-> None` 을 강제하므로 대상이 아니다.»
- wiring(계획 부재): `wiring/implementation-python-final.ttl` — `djr:R-3446 djr:delegatedTo <…a/agent-discipline-reviewer> .`(위임 기본값 표 implementation-* · R-2712/R-2713 동형). 무소유 Norm 은 구조검사 red(레시피 1).

### E — R-3447 · R-3448 (`s007-4` 새 b7 · order 7) + R-0345 rev2

- (a) 모순: R-3148 «타입을 적는다» 는 존재 규범 → «`Any` 는 타입이 아니다» 는 R-3148 의 «타입» 을 좁히는 독립 Prohibition — 중복 아님. R-3150(조건부 면제 금지) 과 무조건형 정합 ✓. R-3154(프레임워크 선언 면제) 는 «달면 오작동» 자리(모델 필드·Meta·enum 멤버) 라 시그니처 `Any` 와 무관 ✓. R-3156(표준 문서군 예시 면제) 이 Knowledge Level 예제 `dict[str, Any]` 를 덮음 ✓(치환은 선택). §4.1 R-3158 «mypy strict 는 시그니처만 강제 → 나머지는 백스톱과 감수자» 를 집행 문장이 인용 — 정합. R-3443(`s016-3.1` — «`object`/`Any`/JSON 입력의 타입 좁히기는 값 객체를 부르기 **전** 에 경계(Data Mapper·요청 Schema·폼)가 담당») 과 R-3448 «받는 즉시 좁힌다» 는 «어디서» 를 두 문서가 각자 말하는 형 → R-3448 은 «무엇으로 받는가 + 즉시» 만 말하고 위치는 R-3443 을 가리킨다.
- (b) 순서: 계획 = R-3447(s1~s3) → R-3448(s4·s5) → 집행 문장(R-3447 귀속). §13 «블록 내 문장→Work 대응(문장 등장 순 = 채번 순)» 위반. 두 해법: ⓐ 집행 문장을 s3 뒤로(권고 — 블록 1) ⓑ b7(R-3447+집행)·b8(R-3448) 2블록(Block +5).
- (c) 양태: R-3447 s3 «우리 쪽 선언은 `object` 로 **쓴다**» 는 Obligation 문장이 Prohibition Work 에 든다 — 다문장 Work 선례(R-3427) 로 허용. R-3448 Obligation ✓.
- (d) «#645» — SKILL.md §1/§3 규칙 번호 7회·«후보 채널(ⓓ)» 1회 선례 → 적법. «ⓓ#645» 합성 표기는 md 선례 0(검사기 docstring 만) → «ⓓ 후보(#645)».
- 결정 1 정합: «`*args/**kwargs` 도 예외 없음» 이 s2 에 명시 ✓ · E-c(ruff `allow-star-arg-any` 관례와 다름) 는 R-3157 «주류와 다른 선택임을 숨기지 않는다» 형으로 한 구 병기 권고.
- **대체 문면**(b7 · statesNorm R-3447, R-3448 · 말미 `\n\n`):
  > «**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다 — 별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다. 시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ 후보(#645)로 표시된다 — 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자» 와 같은 분담). 경계 입력(JSON·폼 `cleaned_data`·`request.user`·무스텁 서드파티)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — implementation-python §1.12 · 좁히는 자리는 architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전). JSON 문서는 `Mapping[str, object]`.»
  (문장 1~4 = R-3447 · 5~6 = R-3448.)
- R-0345 rev2(`s007/b28` · amendment · `@2026-09-04`): «… 타입 전면(#493 — …)·**명시 `Any`(#645 — 시그니처는 차단·변수/제네릭 안은 ⓓ 후보)**·Thin Read 반환(#358)·계약 검증 토큰(#456).» — 렌더 `commands/dddjango.md:133` · codex `codex-dddjango/skills/dddjango/SKILL.md:150` 손 미러(경로 표기 `scripts/…`).

### F-1 — R-0719 rev2 amendment (`s010-2.3/b18`)

- (a) «매요청 조립» 과 정합(partial 도 팩토리 본문에서 매요청 생성) · R-0725(모듈 전역 인스턴스 금지)·b21 «테스트 오버라이드 회피» 와 정합 · #85(`check-composition-root.py:1849~1880` — 최상단 `Assign` 도 red) 와 정합은 «본문 안에서» 조건이 지킨다 ✓.
- (b) 삽입 위치: b18 의 Work 순 R-0718→R-0719→R-0720→R-0721. R-0719 문장은 **«…호출만 한다(매요청 조립).» 바로 뒤** 에 넣는다(말미 금지).
- **대체 문면**(R-0719 문장 s2 뒤 삽입 1문장):
  > «`build_<use_case>()` 가 어댑터 생성자에 꽂는 callable(함수·메서드·`partial`)은 **꽂히는 자리가 선언한 Protocol·`Callable` 시그니처와 같아야 한다** — 실물 함수가 더 많은 인자(경로·모델·설정)를 요구하면 그 인자는 팩토리 **본문 안에서** `functools.partial`/클로저로 묶어 넘기고 어댑터·use case 는 모른다(모듈 최상단 대입은 #85 위반 · 시그니처가 다른 함수를 그대로 꽂는 것은 «꽂기» 가 아니라 미완성 배선이다).»
- Expression: `<djr#R-0719@2026-09-04>` revision 2 · revisionKind amendment · prefLabel 에 «주입 callable ≡ 수신 시그니처·부족 인자는 본문 partial» 추가.

### F-2 — R-3450 (`s025-5.5`)

- 좌표 사실: b19~b24 = 화이트리스트 6불릿(전부 statesNorm 0 · R-2155 Permission «목록» 이 b18 에), b25 = R-2156 «다음 항목은 … 자격이 아니다», **b26~ = 블랙리스트**, 최대 b48. restates 가 b35·b37·b46 을 4곳에서 가리킨다(IRI 개명 불가).
- 선례: 블록 신설 9커밋 전부 order 재배열 0 · 9ef6c4f «문서 말미 s018-5(밀림 0)» · f2d4df0 는 §3 «신호 +1행» 을 절 말미 b8 로 append(Work 0·restates). 목록 «중간» 에 블록을 끼운 선례 0.
- **해법(권고)**: b24 텍스트를 «- 별도 사용자 승인 근거 … 공개 Python 계약\n- composition root 의 실배선 정합 — …\n\n» 으로 확장(다불릿 1블록 = s038-5.3/b3 형 · §13 «불릿 묶음 — 행 범위» 허용) · b24 `statesNorm djr:R-3450` · 블록 신설 0 · 공백 이관 0. Block +4 → +3(target-counts 2905 → 2904).
- 모델링 병기: 항목 Work 0 이 목록 관례라면 «Work 없는 불릿 + R-2155 amendment rev2(«목록 +1» · Expression +1 · Norm +0)» 도 정합 — ④ 에서 하나를 택해 검수표에 기록. R-2158(«공개 Python 계약 근거 택일» Permission) 이 불릿이 아니라 b34 설명 문단에 걸린 선례로 보아 «불릿 자체에 Work» 는 신규 관행이 된다.
- **대체 문면**(불릿 1행 · Permission):
  > «- composition root 의 **실배선 정합** — 진짜 `build_<use_case>()` 가 실 어댑터에 꽂는 callable 의 시그니처 일치(fake 는 외부 I/O 경계뿐) · 팩토리를 통째 monkeypatch 한 테스트는 이 대상의 보호가 아니다»
- wiring(계획 부재): `wiring/discipline-tdd-final.ttl` — `djr:R-3450 djr:delegatedTo <…a/agent-discipline-reviewer> .`(R-2155/R-2158 동형).
- SKILL 미러: `discipline-tdd/SKILL.md` 에 화이트리스트 재진술 0 → SKILL 손 미러 불요 ✓.

### G — R-3427 rev4 + R-3449

- R-3427 (a) 무모순: #93 = `application_layer/port/**` 전체(exception 한정 아님 · `check-context-isolation.py` docstring «#93/#94/#95 driving 잎의 import 폭») 와 ⑵ 문면 정합 · R-3425 태그 의미론 무관(행은 태그를 바꾸지 않음) · R-3436(블록 부재·공허 = 형식 red) 과 무관 · S3 문면(«산문에만 적힌 경계 import 는 표면 밖») 을 문면이 재진술 — Coordinator 소유 보고 문면을 architect 규범이 한 구 반복하는 것은 허용(«예보 표면 밖» 은 사실 서술). 하우스룰 #92 성문 = `houserules-final s003-…` R-3206(final.md:206) · **#93 은 코퍼스 어디에도 성문 0**(검사기 docstring·원장뿐) — 인용은 검사기 번호 인용 선례로 적법.
- (b)(c) 단일 Work 블록 · Obligation 유지 ✓. 개정 종류: §3 참조.
- **대체 문면**(«경계만 성문한다(그 밖의 import 는 구현 재량).» 을 아래로 치환):
  > «**경계란 세 가지다** — ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ BC 안의 층 경계 중 **층 규율 검사기가 금지·예외 항목으로 판정하는 것**(driving 잎 → `application_layer/port/**` · domain → 상위 층 등 #92~#96·#185/#186 의 항목) — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다(적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(실행기 사각 S3 — pregate-report 헤더의 사각 목록).»
- R-3449 문면 (a): #92(R-3206)·R-2720(«use case 실패는 예외 · `<use_case>_result.py` 엔 성공 한 벌 #571») 의 귀결을 성문 — 중복 아님(코퍼스 «번역 책임» 0 · ≥4레인 재유도). «재수출» 을 인정하지 않는 «번역» 어휘 ✓.
- **대체 문면**(R-3449 · Obligation · 착지 §3.6 b3 불릿 +1 또는 §5.3 b7):
  > «- port 예외를 **자기 영역의 예외**(`application_layer/<area>/exception.py`)로 번역한다 — driving 잎(컨트롤러·OHS)은 `application_layer/port/**` 를 import·catch 하지 않고(#92/#93) 그 번역된 실패만 분기한다(`<use_case>_result.py` 엔 성공 한 벌 · #571)»
  (§5.3 b7 형이면 머리말 «**port 예외의 번역은 use case 가 진다.**» 로 시작하는 문단형.)
- wiring: `wiring/architecture-ddd-final.ttl` — `djr:R-3449 djr:delegatedTo <…a/agent-design-review-ddd> ; djr:enforcedBy <…c/check-context-isolation.py> .` — §16 4원: ① 문면 역할명 «#92/#93» ② docstring «#93 driving 잎의 import 폭» ③ 커버(잎→port import 를 잡음 — 번역 부재의 결과 검출) ④ registry 대응. 설계 시점 규범이라 delegatedTo 는 design-review-ddd(위임 기본값 표 architecture-ddd) — 계획은 enforcedBy 만 적어 위임 누락.

### H — R-3181 rev3 (`s003-0/b3`)

- (a) 모순: R-2499(coder — 빈 파일 실현)·R-3188/R-3189(실현 주체·검사기)·R-0319(«내용이 생긴 뒤부터 검사» — registry #2 한정 Prohibition) 과 정합 · «하나»(#219/#635) 는 Work 0 이라 그래프 충돌 없음 ✓.
- (b)(c) 단일 Work 블록이라 순서 문제 없음. 양태: 추가 문장 1·2 = 유예(Exception 형) · 3 = 금지(Prohibition 형) — Obligation R-3181 에 넣어도 다문장 Work 선례로 통과하나, 새 규칙 성격이 뚜렷해 **같은 b3 에 새 Work(Exception) 1** 이 더 정직(b1 «R-3148·R-3149·R-3150 혼합형»). 결정 2 «규범 1줄» 과 양립(Norm +1 → ISSUED R-3451).
- (d) 어휘: «registry #2» — houserules final.md 에 «registry» 0회 → «Coordinator 의 빈 모듈 inventory 제외(R-0319)». R-ID 인용 선례 ✓. «`skeleton_placeholder`» — md 에 검사기 내부 함수명 인용 선례 0.
- **대체 문면**(#488 말미 추가):
  > «빈 파일로 실현된 칸의 **내용 규칙**(진입점·포트 «하나» 등)은 내용이 생긴 뒤부터 선다 — Coordinator 가 빈 모듈을 error inventory 에서 제외하는 것(R-0319)과 같은 시점이며, 검사기는 내용 없는 골격 파일(0바이트·docstring/주석뿐)을 내용 규칙에서 건너뛴다. 빈 파일을 지워 red 를 푸는 것은 #488 위반이다.»

## 3. 개정 종류 · 착지 · 채번 판정

- **종류 정의**: `vocab/djr.ttl:195~202` 는 라벨뿐(amendment «규범 개정» · clarification «명확화» · redefinition «지시 대상 변경») · authoring·DEVELOPMENT 에 정의 문면 0 · 도구 소비 0(`grep revisionKind workspace/tools/*.py` = 0). 실전 용례: clarification = 문면 명료화·범위 «닫기»(4699d7e R-3443 rev2 · f2450ad R-3436 rev2 · R-0287/0419/0442 rev3) · amendment = 의무 추가(R-3427 rev2/rev3 · R-3181 rev2 · R-3417 rev2) · redefinition = 지시 대상/유형 변경(R-1645·R-0180 · Permission→Obligation).
  - R-0719 amendment ✓ · R-0345 amendment ✓.
  - R-3427: 지시 대상(«경계 import») 불변 → redefinition 아님. 두 독법 중 하나를 닫는 «명확화» 로 볼 수 있으나 실전 독법 ⓑ 명세가 형식 red 가 되고 architect 에 새 행 의무가 생긴다 → **amendment 권고**(clarification 을 고수하면 LEDGER 사유에 «독법 ⓑ 명세 소급 red 2» 를 병기).
  - R-3181: 내용 규칙 시점·검사기 유예·삭제 금지 3문장은 #488 의 기존 뜻을 풀어 쓴 것이 아니라 새 규칙 → **amendment**(또는 새 Exception Work).
- **착지**: D §4.4 b3 ✓(§1.2 는 Optional «값» — 주제 이탈). E s007-4 b7 ✓(§4.2 신설 불요). F-2 = b24 확장(위치 «목록 마지막» 유지 — 맨 앞은 b19 확장이 되어 «와이어·보안» 첫 항의 무게를 흐림). G R-3449 = §3.6 b3(권고) 또는 §5.3 **b7**(계획 «b6» 은 충돌) — §6 구현 패턴(6.1~6.8 = 패키지·Data Mapper·UoW·Saga·라우팅)은 주제 이탈 · 하우스룰 #92/#93 자리(final.md:206 #92 만 성문 · #93 0)는 «import 폭» 규칙이지 «번역 책임» 규칙이 아니므로 착지 아님. H R-3181 ✓(R-0319 amendment 는 «registry #2 한정» Prohibition 을 일반화하는 것이라 Coordinator 문서에 하우스룰 시점 규칙을 두는 소유 위반 — 계획 선택이 맞다).
- **채번·IRI·공백**: R-3446~3450 문서 간 배정 순서 규약 없음(ISSUED append-only · §5) ✓. «다음 미사용 서수» 는 §14 절 규약이고 블록은 «서수 = order 말미 append» 가 실질 규약(전수 2,901 · 신설 커밋 9) — 계획의 «IRI 다음 미사용 서수 + order 로 중간 삽입» 은 s007/b59 선례와 **다르다**(b59 = order 59 말미 append · order 재배열 0). 필수 술어(BlockShape): `inSection`·`kind`·`order`·`text`(+`statesNorm`/`restates` 선택) · 새 Section 없음이라 `headingSnapshot`/`inDocument`/`sectionNumber`/`sectionOwner` 무접촉. 공백: 신설 시 선행 블록 말미 `\n\n`→`\n` · 확장형이면 이관 없음.
- **계수**: Block +3(또는 +4) · Norm/Work +5(+1 if H Exception) · Expression +9(+1 if R-2155 amendment) · LEDGER 재기준선 **8행**(s032-4.4 · s007-4 · command s007 · s010-2.3 · s025-5.5 · architect s005 · s038-5.3 또는 s023-3.6 · s003-0).

## 4. wiring 판정 (§16)

| Work | 계획 | 판정 | 정정 |
|---|---|---|---|
| R-3446 | 미기재 | **누락** | `wiring/implementation-python-final.ttl` delegatedTo a/agent-discipline-reviewer |
| R-3447 | enforcedBy public-surface | 부분 | + delegatedTo a/agent-discipline-reviewer(ⓓ 후보 감수자 집행 — R-3150/R-3158 형) |
| R-3448 | delegatedTo **a/agent-coder** · «R-3148 배선 복제» | **오배선** | delegatedTo a/agent-discipline-reviewer 만(검사기 미커버 — enforcedBy 금지) |
| R-3449 | enforcedBy context-isolation | 부분 | + delegatedTo a/agent-design-review-ddd(설계 시점 기본값) |
| R-3450 | 미기재 | **누락** | `wiring/discipline-tdd-final.ttl` delegatedTo a/agent-discipline-reviewer |

Checker IRI 는 `wiring/registry.ttl:49`(context-isolation)·`:88`(public-surface) 기선언 ✓. rulepack `by_checker` 는 dict(파일명 → R-ID 목록 · 현재 public-surface = R-1066·R-1098·R-0302·R-0345·R-3148…) 이라 `make rulepack` 이 R-3447·R-3449 를 자동 편입 · 양 rulepack.json 동시 갱신(191842a stat 선례). 검수표에 4원 근거 기록 의무.

## 5. 미러 표면 누락 목록

1. **doc_key 8**(계획 «5문서 · render ×5»): implementation-python-final · discipline-houserules-skill · command-dddjango · implementation-django-ninja-final · discipline-tdd-final · agent-design-architect · architecture-ddd-final · discipline-houserules-final.
2. **final.md 5**(계획 4): + `discipline-houserules/references/final.md`(H). 각각 레시피 5(workspace 소스 span 수동 교체 → `corpus_mirror_sync --write` → codex byte) — 소스 미러 5개 실존 확인.
3. **codex 손 미러 3**(계획 2): + `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md`(§4 = SKILL.md 그래프 절 · `corpus_mirror_sync` 스코프 = final.md 11 뿐 · `ontology_render` 대상은 Claude SKILL.md 만) — 빠뜨리면 두 런타임의 `Any` 규범이 갈린다(레시피 6).
4. **spec_lint 표면**: `2026-08-08-tree-revision-spec.md` 는 «1행» 이 아니라 규칙 행 + 집계표·읽는 법 수치(⑦ — 선례 b5f226a 9행 변경) · `2026-08-11-rule-owner-map.md` 1행(⑧) · **`2026-08-11-predicates.md`**(⑥ — #645 가 위반+ⓓ 후보 = `ast+` 등급이면 «후보·물음» 술어 행 필수). spec_lint 는 md 규범 문면의 «#N» 실존을 검사하지 않는다 · `tree_mirror_check` 무관(트리 행 무변).
5. 실행기 S3 문면 → `design_pregate.py` byte 미러 + `manifest_seal --write` ✓(계획 기재).

## 6. 현장 보고 정정 추기(§2-5) 제안

파일 `workspace/plan/2026-09-03-field-report-spring-dream-typecheck.md` — 원문 무수정 · «## 수정 우선순위 · 판단 기준» 절 직전(또는 처분 상태 표 아래)에 G·H 추기와 같은 형식의 blockquote 1개:

> **정정 추기(dddjango 측 · 2026-09-04 · ② 계획)** — 원문은 보존한다. ① L29·L120·L240 «`discipline-test`» 스킬은 존재하지 않는다 — 무엇을 보호하는가는 `discipline-tdd` §5.5 소유(F-2 착지) · 메커니즘은 `implementation-test`. ② L34·L234 «테스트 26곳» 은 미재현 — 실측 `build_*` monkeypatch 14 + llm_access 3(증거 F). ③ L32·L47·L202 «D 13건» 은 43e9628 시점 수치 — HEAD 는 발주측 96e8719 로 `_fail -> NoReturn` 이라 0. ④ L211~L213 «시그니처 `Any` 47 · application 0» 은 ANN401(별표 인자 면제) 기준 — 재집계 application 프로덕션 시그니처 bare `Any` = spring 8 · kkebi 10(미러 13 · 실질 5 · 증거 DE).

처분 상태 표에는 D·E·F 행 상태 열만 갱신(«R-3446 착지» 등) — 정정 본문은 위 추기 1곳에 모은다.

## 7. 미확인

- `#645` 의 등급(ast+/path/human)과 predicates.md 필수 여부는 ④ 의 검사기 형상(ⓓ 채널 유무)으로 확정 — 본 리뷰는 «ⓓ 후보 있음 → ast+» 로 추정.
- R-2155 amendment 형을 택할 때 q4 골든(`query-golden.json distinct_works`) 변동 여부 — `--emit` 으로 확인.
- 계획 G «S3 문면 병기» 의 실행기 문자열이 R-3427 rev4 문면과 어휘 일치하는지(«전사는 add 소비자 스텁만» vs «예보 표면 밖») — A 축.
- codex `dddjango-discipline-houserules/SKILL.md`(91행) 가 Claude SKILL.md(102행) 와 이미 드리프트인지(줄 수 차 11) — 이번 배치 손 미러 시 §4 만이 아니라 전체 대조 권고.

Serena: skipped — 읽기 전용 규범 리뷰(코드 편집 없음)라 기본 도구로 충분.
