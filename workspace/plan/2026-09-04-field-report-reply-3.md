# 현장 보고 회신 3 — django-stubs 제네릭 기저(S-1)·딕셔너리-레코드(S-4)·ninja `Status`(S-5) 처분 + spring_dream_server 안내 (2026-09-04)

대상 보고: `2026-09-04-field-report-spring-dream-django-stubs-generic-base.md`(발주자 세션 · v2.17.16 기준 · 원문은 증거로 보존). 절차: 추적표·결정 `2026-09-04-field-report-repair-3-issues.md` · 루브릭 `2026-09-04-field-report-repair-3-rubric.md` · 계획 `2026-09-04-field-report-repair-3-plan.md`(v2) · 증거 `workspace/eval/field-report-3/`. 구현 = 브랜치 `fix/field-report-3`(조각 1 56b27e1 · 조각 2 d701df8 + 정정 cad221b · ⑤-2 정정 30a2a24 · ⑥ 감사 «머지 가능» 192b886) · 릴리즈는 머지 뒤 별도(`make release` · 사용자 요청 시).

수치는 새 검사기(HEAD)를 격리 사본에 돌린 값이다(spring `7bfe1aa` · kkebi `6608fb0` · `application/`·`framework/` 루트만 · registry_gate 앵커 차분 전 전량).

## 1. 처분 표

| # | 보고 항목 | 판정 | 플러그인 처분 | 발주측 할 일 |
|---|---|---|---|---|
| S-1 | django-stubs 제네릭 기저(admin·form) 규칙 부재 — 레인 10개가 맨몸 13 / `# type: ignore[type-arg]` 17+1 / 별칭 9 로 갈림 | 성립 — 플러그인 예시 자체가 맨몸(`ArticleForm(forms.ModelForm)`) · kkebi 도 같은 형상(ignore 21 · 별칭 31) | 하우스룰 §4 신설 R-3458/R-3459(«기본값 없는 django-stubs 제네릭 기저는 모델 타입 인자 · `TYPE_CHECKING` 별칭 기본 · monkeypatch 채택 시 직접 · ignore 금지») · §6.1 R-3163 rev2(monkeypatch 는 전역 패치 — 레인이 도입하지 않음) · §4 R-3154 rev2(admin 선언 속성 면제 성문) · implementation-django **새 절 §18**(정본 예시 · mypy strict 검증) · django-web §2·§6 예시 별칭 정정 + R-3462 · 검사기 **#646**(맨몸·ignore 차단 · 별칭 3모양 통과 · 런타임 subscript ⓓ) · #493 별칭·subscript 기저 선언적 면제 회복 | §2 ②③ |
| S-2 | ignore 부착 검사기(선택) | S-1 에 흡수 | #646 ⓑ(헤더·속성 줄 `type: ignore[type-arg]`) | — |
| S-3 | 자기 BC 빼고 돌린 mypy «Success» | 발주측 | 로드맵 R-12 행에 반영 문구 추기(«mypy 증거는 자기 BC 경로 포함 필수») | §2 ① |
| S-4 | 딕셔너리-레코드(`dict/Mapping[str, object\|Any]` 1,110줄 · mypy 70) | 성립 — 예시 `dict[str, Any]`(architecture-ddd) · R-3448 «JSON 은 `Mapping[str, object]`» 가 반대 처방 · 강제 도구 0 | 하우스룰 §4 R-3447/R-3448 rev2(«값 자리 `Any` 는 어디든 차단 · `object` 는 입구(검증 도우미 매개변수·즉시 검증 지역 변수)만 · 반환/속성 누수 차단 · JSON 은 `TypeAdapter(그TypedDict)` 검증 파싱») + §4 레코드 규범 R-3451 + 결정표 6행 R-3452~R-3457 · implementation-python §1.5 R-2715 rev2 + 예시 · architecture-ddd 예시 `FieldValue` 정정 · 검사기 **#647**(차단·ⓓ) · **#650**(ⓓ · `json.load(s)` 무검증 흐름) · Coordinator R-0284 rev4/R-0345 rev3(ⓓ 동봉 범위 = 앵커 차분 신규분) · registry_gate ⓓ 앵커 차분(확장 ⓔ2) | §2 ④⑤ |
| S-5 | ninja `Status[A] \| Status[B]` · 오류 base 뭉뚱그림 · `Schema`+`RootModel` | ⓐⓒ 성립(상자 둘은 08-24 이후 레인 7개(첫 도입 커밋 기준 — 산식에 따라 6~9: 파일별 첫 도입 커밋 6 · 패턴 접촉 커밋 9 · ⑥ 감사 재현)에서 반복 · spring 7·kkebi 6 함수 · mypy red 는 그중 리딩 1레인) · ⓑ 는 기존 #63 이 이미 잡음(레인이 `auto` 프로필로 돌려 침묵) | ninja §2.2 R-3463(상자 하나 · #648)·R-3465(익명 union 금지) · §3.1 R-3464(`RootModel` 단독 · #649) · ninja SKILL R-3466 · architecture-api §5.2 R-3467(성공 union 은 discriminator 컴포넌트 하나) · 검사기 **#648/#649**(프로필 무관 트리 슬라이스) · openapi 검사기 stale 문면 2곳 정정 · Coordinator R-0331 rev2(확장 ⓔ1 — «무관» = 승인 12-slot 유무 · 12-slot 없이 오류 status 를 선언한 컨트롤러는 auto 금지·G1 반송) | §2 ⑥⑦⑧ |
| N-1 | notification `obj is None` 재검사 | R-3443(값 객체 안 선언 타입 재검사 금지) 취지의 admin 변종 — 규범 확장 없음 · 새 항목 아님 | 없음 | 발주측 처방대로 |
| N-2 | parler `# type: ignore[misc]` 6곳 | 정당(서드파티 미타입) | 없음 | 없음 |
| N-3 | 발주측 처리 계획 | — | — | 아래 §2 순서대로 |

## 2. spring_dream_server 쪽 할 일 (설치본 갱신 뒤)

① **mypy 증거는 자기 BC 경로를 포함**한다(`--follow-imports=silent application/<bc>`). `spring_dream_server framework` 만 돌린 «Success» 는 증거가 아니다 — 발주서 G2 체크리스트가 이미 그렇고, R-12 발주 가이드에도 1줄로 들어간다.

② **monkeypatch 채택은 프로젝트 결정(발주측)**이다. 채택하려면 `django-stubs-ext` 를 **운영** `dependencies` 에 넣고 settings 최상단에서 `django_stubs_ext.monkeypatch()` 를 부른다 — 지금은 dev 전이 의존성뿐이라(`uv sync --no-dev` 배포에 없음) 넣지 않은 채로는 부팅이 깨진다. 채택했으면 레인은 `admin.ModelAdmin[Model]` 직접 표기, 아니면 지금처럼 `TYPE_CHECKING` 별칭(spring 22 · kkebi 31 은 이미 이 모양). 어느 쪽이든 `# type: ignore[type-arg]` 는 위반(#646)이다 — legacy 는 spring 18줄(16 파일 · 8 BC: fortune_intent 4 · accounts 3 · wallet 3 · media_library 2 · notification 2 · query_translation 2 · fortune_record 1 · promotion 1) · kkebi 21줄(4 BC: tarot 10 · billing 7 · share 2 · top3 2) — registry_gate 앵커 차분에서 legacy(L∩N · exit 불산입·보고만)라 손대기 전까진 exit 에 안 들어가고, 손대면(클래스 개명·기저 교체) 그 자리가 귀속(N∖L)된다.

③ admin 패널의 선언 속성(`model`·`inlines`·`list_display`·`readonly_fields` …)은 **주석을 달지 않는다**(R-3154 rev2 — 스텁 `ClassVar` 가 타입을 소유 · `inlines` 는 달면 불변성 red). 1288e4a 에서 붙인 주석은 허용(스텁 타입과 같고 그 타입에 `Any` 가 없을 때 — `inlines` 는 달 수 없다)이되 필수가 아니다. #493 이 별칭·subscript 기저의 admin 클래스를 다시 선언적으로 보므로 «기저를 별칭으로 바꾸면 #493 이 터진다» 는 현상은 사라진다.

④ **딕셔너리-레코드 legacy 규모(새 검사기 기준)**: spring #647 차단 594줄(그중 `framework/technology`(RAG 런타임) 449 · application 145 — fortune_character 27 · fortune_calculation 24 · chat_relay 17 · promotion 14 · fortune_reading 11 · product 10) · ⓓ 입구 255(framework 127 · fortune_reading 42 · llm_access 35 · chat_relay 19 · fortune_record 11) · 반환 자리표시 ⓓ 8 · #650 ⓓ 40(framework 32 · fortune_calculation 8). kkebi #647 차단 161(saju 54 · billing 36 · product_observability 23 · tarot 20 · share 11 · identity 7) · ⓓ 입구 253(billing 116 · product_observability 30 · tarot 27 · identity 26 · saju 21) · 자리표시 42(`pull_events -> list[object]` 16 등) · #650 1. 전부 legacy(앵커 차분 · exit 불산입) — 새 레인 산출물만 막힌다. 2차 정리(RAG 822줄)는 대장대로 별도 발주. `Form.clean -> dict[str, Any]` 18곳(spring 15 · kkebi 3)은 `dict[str, object]` 로 바꾸면 면제 — 손대는 커밋에서 같이.

⑤ 신규 3규칙(#646·#647·#650)은 **`application/`·`framework/` 루트만** 본다 — kkebi `web/`(dddjango-web 영역) 111줄·`scripts/` 218줄은 격리가 아니라 **대상 밖**이다. 기존 규칙(#493·#645)은 무변이라 `web/`·`scripts/` 의 #645 ⓓ nested(kkebi 155줄)는 그대로 남는다(기존 ⓓ · 신규 아님).

⑥ **오류 응답을 `response=` 에 선언한 컨트롤러의 G2 는 승인 12-slot 의 profile 로 돌린다**(spring 신규 Ninja 표면이면 `dddjango-code-json`) — `auto` 는 #63·#125 를 재운다(리딩 레인 «0건»의 원인). Coordinator 문면(R-0331 rev2)이 이제 «승인 12-slot 없이 오류 status 를 선언했으면 auto 금지 · G1 반송(error profile 미결정)» 으로 못 박았다. 리딩 400/503 base 선언(#63 2건)과 e2e 동결 단언 2개의 정정은 OpenAPI 문서 변경이라 발주측 승인 사안이다.

⑦ S-5 legacy: 상자 둘 spring 7 함수(accounts 6 · fortune_record 1) · kkebi 6(identity 2 · review 2 · saju 2) → #648 · kkebi `response=` base 선언 31자리(identity 16 · saju 9 · review 5 · image 1) → code-json 으로 돌리면 #63. 전부 legacy(앵커 차분 · exit 불산입).

⑧ 성공 응답이 두 모양이면 `class XOut(RootModel[Annotated[A | B, Field(discriminator="kind")]])` 단독 상속 — kkebi tarot `TarotCardOut` 이 선례(e2e 가 `oneOf`+discriminator 단언). `Schema` 를 같이 상속하지 않는다(#649). spring HEAD 는 이미 그렇게 갚았다(`4cfedb4`).

## 3. 효과 — 정직한 수치

| 항목 | 보고서 표현 | 실측(새 검사기) | 정직한 서술 |
|---|---|---|---|
| S-1 | «검사기 불요 · mypy 가 잡음» | 맨몸 13 클래스는 mypy 가 잡지만(레인이 자기 BC 를 안 돌림 = S-3) · ignore 17+1(spring)·21(kkebi)은 mypy 통과 | «1/10 레인의 mypy 26 + 8/10 레인의 은폐 18줄을 #646 이 예방 · 왕복 절감은 관측 0» |
| S-4 | «mypy 빚 70» | 70 중 레인 산출 3 · 67 은 `framework/technology` RAG(비레인) — #647 차단 594 중 449(76%)가 그쪽 | «레인당 값 `Any` 누수 ≈6(92줄/16 BC) · `object` 반환/속성 ≈3(53/16) 예방 · ⓓ 감수 ≈8/BC(kkebi ≈21 · ⓔ2 뒤 legacy 는 접히고 새 산출분만)» |
| S-5 | «`Status[A] \| Status[B]` = mypy strict red» | red 는 concrete 를 직접 넣을 때(리딩 1/7 레인) · 값 변수를 base 로 주석한 13 함수는 mypy 통과 | «형태 통일 규칙(상자 하나) · mypy 효과는 1/7 레인 · #648 은 형태 자체를 막는다» |

판단 기준 4 재분류: S-1 ① 맨몸 = 플러그인 예시 모양(문면 정정 4줄) · S-1 ② ignore = 검사가 못 잡는 반복(8 BC → #646) · S-1 monkeypatch = 발주측 · S-3 = 발주측 · S-4 `dict[str, Any]` = 플러그인 예시 + 반복(#647) · S-4 `Mapping[str, object]` 형상 = 레인 선택(문면 결정표 + ⓓ) · S-4 mypy 70 = 발주측 RAG 67/70 · S-5 ⓐ = 반복(7 레인 · #648) · S-5 ⓒ = 1레인(문면 + #649 · AST 만이라 싸다) · S-5 ⓑ = 검사가 잡음(#63 · 프로필 운용 안내).

## 4. 이월 (MINOR · 추적표에 기록)

- `implementation-django-web/SKILL.md` 의 web form 불릿에 `ModelForm` 타입 인자 언급 0 — SKILL 만 읽는 web 레인이 R-3462 를 못 본다(다음 배치).
- #63 auto 사각의 기계 봉합(tree 슬라이스에 `response=` base 판정 이식)은 이번 범위 밖 — R-0331 rev2 문면 + 위 ⑥ 안내로 대체.
- #647 반환 자리표시 ⓓ 물음의 오탐 후보(프레임워크 콜백 미러 · 이벤트 컬렉션 `list[<Bc>Event]`)는 문면에 예외로 적었으나 검사기는 구분하지 않는다(ⓓ 라 exit 무관).
- 타 모듈 import 별칭의 맨몸 여부는 #646 이 못 본다(같은 모듈 안만 · ⓑ 헤더 판정은 독립) — mypy 몫.
- `# type: ignore` 전반(코드 없는 것)은 ⓓ 후보로만.
- ⑥ 감사 권고(머지 뒤 소배치 · MINOR): 하우스룰 §4 R-3448 rev2 «면제는 둘» → 셋(`Field.deconstruct` 포함 · 검사기·등재와 일치시킴) · #646 ⓑ 메시지를 «제네릭 기저 ignore» 로 중립화 + R-3459/predicates 범위 문면 일치(ⓑ 는 모든 클래스 헤더를 본다 — 4사본 실측 비-django 0) · 검사기 docstring 한계 추기(`M = Mapping`·`Resp = Status[A] | Status[B]`·`_S = Schema` 같은 Assign 별칭 미추적 · `dict[str, object | None]` 값 union 침묵) · #650 물음에 «`JsonValue` 로 받았으면 통과» 갈래 · `evidence/impl/probe18-summary.md` origin 42→46.

## 5. 설치·관찰

머지·릴리즈 뒤 `/plugin` 에서 설치본을 갱신해야 반영된다(sha 캐시). 첫 레인에서 볼 것: #646/#647/#650 첫 발화 · registry_gate 보고의 «ⓓ 신규(N′∖L′)» 절(legacy 는 건수만) · Coordinator 가 오류 응답 선언 컨트롤러를 `auto` 로 돌리지 않는지.
