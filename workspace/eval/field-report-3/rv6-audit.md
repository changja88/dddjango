# rv6 — ⑥ 독립 감사·재검 · 현장 보고 수리 3 (2026-09-04)

대상: 브랜치 `fix/field-report-3` HEAD **179017f**(감사 착수 직후 부모 세션이 루브릭 2행 커밋 — 위임 시점 30a2a24 + docs 1 · 코드·규범 무변) · main bbd1c9b 기점 커밋 17(조각 1 56b27e1 · 조각 2 d701df8 · 정직 정정 cad221b · ⑤-2 정정 30a2a24). ⓪~⑤-2 산출을 처음 보는 눈으로 재검했고 앞선 리뷰어 판정은 전제하지 않았다(재실측 우선). 저장소·규범·검사기·문서 **무수정** · git 쓰기 0 · 실행은 전부 `scratchpad/fr3/rv6/`(old = `git archive bbd1c9b` · new = `git archive HEAD` · 격리 사본 4 = spring 7bfe1aa·d2eaafe·f5ee428·kkebi 6608fb0 · 인터프리터 = 저장소 `.venv/bin/python` 3.14.7 — 사본에 `.venv` 가 없어 live venv 와 같은 버전인 저장소 venv 로 대체(검사기는 stdlib+동봉 모듈만 · lossless 판형과 결과 byte 동일로 대체 정당성 실증) · live 두 저장소 무접촉(mypy 1회만 live venv 의 인터프리터 파일을 cwd=사본으로 실행) · `make verify VERBOSE=1` 6/6 green(`rv6/verify.log`) 뒤 `git status --short` 공백). Serena: skipped — `.serena/project.yml` 부재.

## 1. 판정 표

| # | 항목 | 판정 | 한 줄 근거 |
|---|---|---|---|
| 1 | 결정 정합(§2-A~D + 수정 1 ↔ 검사기·규범·등재·회신) | **검증됨 + 고지 5**(§3) | 결정 문장 전부가 좌표를 가진다(§2.1 표). 결정 밖 = 예고된 확장 ⓔ1·ⓔ2 + 결정 문면과 다른 기술 조정 3(§2-A 수정 1 ⑤ 구절 **철회**·R-3154 rev2 대체 — issues.md 정본에 철회 미표기 · ddd 예시 `TypedDict`→`FieldValue` 닫힌 union · #647 면제 3번째 `deconstruct`×Field) + #646 ⓑ 가 **모든 클래스 헤더**를 본다(계획 A-2 · 규범 문면은 django-stubs 기저 주어) |
| 2 | 무손실 재검(옛↔새 검사기 · 4사본 × 3검사기 · 픽스처) | **검증됨** | `rv6/out/verdict.txt` 첫 37행이 `evidence/impl/lossless3-verdict.txt` 와 **byte 동일**(`diff` 공백) — 저장소 12/12 OK · 비허용 차분 0/0 · ⓓ#645→#647 슬롯 1:1 655/642/661/55 · unmatched 0 · #493 3216/3225/3225/173 불변 · B∖A = {#646,#647,#648,#649,#650} 만 · 픽스처 OK 98 · RED 4 = 옛 #493 이 신설 파일에 낸 8건(`admin/order/panel.py` 7 · `stub_generic_bad.py:26` 1 — 수정 1 ④ 의 의도) + openapi bad 레인 #63 **문면만** 4줄(같은 좌표·같은 규칙) → «의도» 설명 사실 · 회신 3 legacy 수치 **전 셀 재현**(§2.2) |
| 3 | 검사기 결정성·사각(#646/#647/#650/#648/#649 · #493 수리) | **검증됨 + MINOR ×4** | 프로브 18파일·기대 69건(`rv6/probes/gen_and_run.py` · `out.txt`) — 기대 불일치 0. MINOR: #646 ⓑ 가 비-django 제네릭 기저의 ignore 에도 «django-stubs 제네릭 맨몸을 덮었다» 로 발화(p09) · `-> dict[str, object \| None]` 은 #647·ⓓ 어디에도 안 잡힘(p06b) · Assign 별칭(`M = Mapping`·`Resp = Status[A] \| Status[B]`·`_S = Schema`)은 import 별칭과 달리 미추적(p04c·q01 f3·q06 X3 — docstring «import 바인딩」만 명시) · `x: JsonValue = json.loads()` 가 ⓓ#650(물음 문면에 `JsonValue` 갈래 없음 · p13a) |
| 4 | 규범 정합(신설 17·개정 9·등재·미러·도구) | **검증됨 + MINOR ×3** | 문면↔검사기↔등재↔회신 모순 0(§2.4) · ISSUED 3467행=R-3467 결번·중복 0 · LEDGER +17 · issued/ledger check 위반 0 · gate 전 ttl green · render-sync 541 red 0 · 계수 2919/546/3476/3594 = target-counts · rulepack «팩 == render(그래프)» · byte 미러 6파일 `cmp` 동일 + `diff -rq` 0 · final.md 7종 byte 동일 · codex hand 4 문장 존재 확인. MINOR: houserules §4 b7 «면제는 둘» ↔ 검사기·spec 행 647 «`Field.deconstruct` 포함 3» · `evidence/impl/probe18-summary.md` «forms 5 · 42 origin» ↔ 검사기 forms 9(46 · django-stubs 6.1.0 `.pyi` 실측 9 맞음) · R-3459 문면 주어(django-stubs 기저) ↔ ⓑ 실제 범위(전 클래스 헤더) |
| 5 | 효과 정직성·문서 | **MINOR ×4** | d701df8 거짓 표기의 정직 기록 **잔존**(piece2-summary:25 · 루브릭:82 · DEVELOPMENT.md:82 — 지우지 않음 ✓) · 30a2a24 메시지 수치 = verify5.log 6/6 ✓ · 불일치: 로드맵 18행 커밋 목록·§8 «⑤-2 진행 중» 가 30a2a24 이전(stale) · issues.md §2-A 수정 1 ⑤ 철회 미표기 · 회신 S-5 «레인 7개» 산식 미병기(재현 6~9) · gate legacy 518↔519(±1 · 비관건) |
| 6 | 회귀 위험(main → 이 배치) | **MINOR ×2** | 결정 밖 변동 0 — #493 lost/gained 4사본 0(사라진 지적은 픽스처 8건뿐 · 수정 1 ④) · #645 위반 라인 byte 동일 · api-error exit 0→2 는 legacy 상자 둘(spring 7·kkebi 6)뿐 → 앵커 차분 격리 · ⓔ1 소급 반송은 문면상 «이번 산출물» 한정 · #646 ⓑ 전 클래스 헤더(§2.6) |
| 7 | 머지 판정 | **조건부 머지 가능** | C1 2(문서 정정 · 브랜치 안 수리 가능 · 규범·검사기 무접촉) + C2 고지 5(§3·§4) |

## 2. 상세

### 2.1 결정 정합(1:1 표 · 좌표 = HEAD)

| 결정 문장 | 검사기 | 규범(렌더) | 등재·회신 |
|---|---|---|---|
| §2-A ① 기저 타입 인자 · ignore 금지 · 수정 1 ① 별칭 기본/monkeypatch 채택 시 직접(발주측) | — | houserules SKILL.md:89(R-3458/R-3459) · :106(R-3163 rev2 «전역 패치 · 레인 도입 금지») · django final:1854-1913 §18(R-3460·예시·R-3461) · web final:65-67·:217-229(R-3462) · django-skill:56 표 행 | spec:1175 · owner-map:559 · 회신 §1 S-1·§2 ② |
| §2-A ② #646 ⓐ 맨몸 ⓑ ignore · 별칭 3모양 통과 · AST | public-surface:134-155(집합 admin5·forms9·CBV32) · :799-836 `_classify_base` · :872-928 · ⓑ 헤더 = **모든 ClassDef**(:899-913 · 계획 Δ5·A-2) | predicates:245 ⑴⑵ | fixtures good 3·bad 2 · 회신 §2 ② legacy 18/21 |
| §2-A ③ 픽스처 삼중 등재 · 3문서 | fixture 104/104 · baseline·count 73/73 · cross 348/348 (verify.log) | — | spec·predicates·owner-map 행 ✓ |
| §2-A ④ S-2 흡수 · S-1g 별도 → 수정 1 ⑤ «`Any` 조건부 구절» | — | **철회** → R-3154 rev2(SKILL.md:72 admin 선언 속성 면제 성문 · rv1 B-2) — issues.md:136 은 여전히 ⑤ 를 결정으로 적음 | 루브릭:66 «철회 1» 만 기록 → C1-1 |
| 수정 1 ② 세 모양 통과 · ⓐ+ⓑ 1건 · 타 모듈 별칭 표면 밖 | :899-913(접기) · docstring :38-40 | SKILL.md:89 | 회신 §4 이월 4 |
| 수정 1 ③ 코퍼스 예시 4줄 정정 | — | web :66-67·:217-223 · django §13.4(LEDGER prose s065-13.4) | — |
| 수정 1 ④ #493 별칭·subscript 기저 면제 회복 | :317-373(`_alias_defs`·`_resolved_bases`·`_is_declarative_class`) | — | 프로브 r01 · 4사본 #493 불변 |
| §2-C ① 레코드 규칙 + 결정표 6행 · R-3447 «Mapping[str, object]» 대체 | — | SKILL.md:76(R-3447/R-3448 rev2 — «TypeAdapter 검증 · object 는 입구만») · :78-87(R-3451 + 표 R-3452~R-3457) | spec:1176 · 회신 §1 S-4 |
| §2-C ② ddd `values: dict[str, Any]` → `TypedDict` · python §1.5 확장 | — | ddd final:1598-1623 = `dict[str, FieldValue]` **닫힌 union**(키 동적 → 결정표 «조회표」 행 적용 · 계획 §1.6) · python final:109-158(R-2715 rev2 + `TypeAdapter`·`JsonValue` 예시) | 결정 문면과 다름(기술 조정 · §3-4) |
| §2-C ③·수정 1 ①② #647 매트릭스(Any 전 자리 차단 · object 반환/속성 차단 · 매개변수/변수 ⓓ) | :652-680 `_record_value` · :732-757 `judge` | SKILL.md:76 · spec:1176 · predicates:246 | 프로브 p01~p07·p15~p18 전부 기대대로 |
| 수정 1 ③ 면제 2(`Form.clean -> dict[str, object]` · `TypeIs/TypeGuard`) | :163-166·:702-712 — **3번째 `deconstruct`×Field**(rv1 A-9·Δ6) · TypeIs 면제는 `object` 만(:740-745 · `TypeIs[dict[str, Any]]` 차단 = 픽스처 record_leak:20) | SKILL.md:76 «면제는 둘»(deconstruct 없음) · spec:1176 «Form.clean·Field.deconstruct» | §2.4 MINOR |
| 수정 1 ④ `json.load(s)` ⓓ 오라클 | :935-1017 #650 · 기대 spring 40·kkebi 1 재현 | spec:1179 · predicates:247 | 회신 §2 ④ |
| 수정 1 ⑤ #645 배타 · R-0284/R-0345 문면 | :756(`not blocked647`) · 슬롯 1:1 실측 | dddjango.md:108(R-0284 rev4) · :133(R-0345 rev3) | — |
| 수정 1 ⑥ R-3448 redefinition · R-3447 amendment(`@2026-09-04b`) | — | ttl revisionKind 실측(§2.4) | — |
| 수정 1 ⑦ 루트 필터 이월 | → 구현으로 대체: `RULE_ROOTS`(:156·:644) 신규 3규칙만 | R-0345 rev3 문면 «application/framework 루트만» | 회신 §2 ⑤ |
| §2-D ① 문장 2 + 예시 | — | ninja final:141(R-3463 · 예시 :186 `-> Status[OrderOut \| …]`) · :367(R-3464 · tarot 인용 — 인라인 예시) · :111-112(R-3465) · ninja SKILL:34(R-3466) · api final:208(R-3467) | spec:1177-1178 |
| §2-D ② ⓐⓒ 검사기 · 수정 1 ①② ⓑ 철회·트리 슬라이스 #648/#649 | api-error:7115-7117·7166-7195·7230-7242(프로필 무관) · openapi stale 5곳 diff(docstring·헤더·조치·주석·#63 메시지) | dddjango.md:137(R-0349 rev2) · :127 | predicates:248-249(⑤-2 정정) · owner-map:61·561-562 · spec:387 #63 08-25 span |
| §2-D ④ 발주측 OpenAPI 변경 | — | — | 회신 §2 ⑥ |
| §2-B R-12 추기 | — | — | 로드맵:52 «반영 문구» ✓ |

### 2.2 무손실 재검(실측)

명령: `rv6/lossless_rv6.sh bbd1c9b HEAD`(rv3C 판형 그대로 · 인터프리터만 저장소 venv) → `rv6/out/verdict.txt`. 결과 = 증거와 byte 동일(`diff <(head -37 rv6/out/verdict.txt) <(head -37 evidence/impl/lossless3-verdict.txt)` 공백). `scripts-diff` 6파일(검사기 3·registry_gate·pregate json·rulepack) = 이번 변경 전부 → 나머지 24 검사기 byte 동일.

| 사본 · 검사기 | old→new | A∖B | B∖A |
|---|---|---|---|
| spring / d2eaafe / f5ee428 / kkebi · public-surface | 4097→4537 / 4083→4543 / 4112→4562 / 851→1291 (exit 2→2) | ⓓ#645 655/642/661/55 — 전량 #647 슬롯 1:1(unmatched 0) | #646 18/31/18/21 · #647 v 733/722/742/166(레코드 · 줄 594/—/—/161) · ⓓ#647 304/311/311/307 · ⓓ#650 40/38/40/1 |
| 같은 4사본 · api-error(auto) | 7→14 / 6→15 / 7→16 / 27→33 (exit 0→2) | 0 | #648 7/8/8/6 · #649 0/1/1/0 |
| 같은 4사본 · openapi(auto) | 0→0 | 0 | 0 |

회신 3 수치 재현(`rv6/out/*.new.*.jsonl` 서로 다른 줄 계수): spring #646 **18**(ignore 18줄 · 16파일 · fortune_intent 4·accounts 3·wallet 3·media_library 2·notification 2·query_translation 2·fortune_record 1·promotion 1) · #647 차단 **594**(framework/technology 449 · fortune_character 27·fortune_calculation 24·chat_relay 17·promotion 14·fortune_reading 11·product 10) · ⓓ 입구 **255**(framework 127·fortune_reading 42·llm_access 35·chat_relay 19·fortune_record 11) · 자리표시 **8** · #650 **40**(framework 32·fortune_calculation 8) · `Form.clean -> dict[str, Any]` **15** / kkebi #646 **21**(tarot 10·billing 7·share 2·top3 2) · #647 **161**(saju 54·billing 36·product_observability 23·tarot 20·share 11·identity 7) · ⓓ 입구 **253**(billing 116·product_observability 30·tarot 27·identity 26·saju 21) · 자리표시 **42** · #650 **1** · clean 3 / #648 spring **7**(accounts 6·fortune_record 1) · kkebi **6**(identity 2·review 2·saju 2) — 회신 §2 ②④⑦·§3 과 전 셀 일치. 회신 §2 ⑤ 「web 111·scripts 218·#645 ⓓ nested 155」: 루트 필터를 `web`·`scripts` 로 넓힌 검사기 사본(`rv6/probes/nofilter/`)으로 **111·218** 재현(web = #647 v104+ⓓ7 · scripts = v39+ⓓ186+#650 1) · nested 155 재현(전 ⓓ#645 240 중).
registry_gate ⓔ2(kkebi 사본 · `--anchor HEAD` + 무해 파일 1 · `rv6/gate-kkebi.log`): **귀속 0 · ⓓ 신규 0 · legacy ⓓ 1,269 · exit 0** · sidecar 키 `candidate_lines`/`candidate_records`(빈 목록) 실재 — 증거 gate2-kkebi.log 와 legacy 위반 519↔518(business-vocabulary 3↔2 · 프로브 파일명 차이 · 비관건) 외 동일. §18 정본 예시 3변형(`evidence/impl/{canonical,direct,tc_class}_admin.py`) mypy strict(spring venv · django-stubs 6.1.0 · cwd=사본): **Success 4 files** — 주장 재현.

### 2.3 검사기 결정성·사각(프로브 18파일 · 기대 69 · `rv6/probes/tree/` · 결과 `out.txt`)

| 프로브 | 형상 | 실제 | 판정 |
|---|---|---|---|
| p01·p03 | `from __future__ import annotations` · `-> "dict[str, Any]"` · `dict[str, "Any"]` | #647 v ×3 | 문자열 재파싱 ✓ |
| p02 | `from myproj.compat import Any` + `dict[str, Any]` | 무발화(ⓓ 도 없음) | #645 와 같은 기존 사각(fr2 rv6 p08) — 신설 아님 |
| p04 | `Mapping as _M` · `t.Mapping[str, t.Any]` / `M = Mapping` | v · v / **ⓓ#645 nested 로 강등** | import 별칭 ✓ · Assign 별칭 미추적(docstring :41 «import 별칭 해소」 — MINOR 문서화) |
| p05·p06 | `Optional[dict[str, Any]]` · `dict[str, Any] \| None` · `dict[str, dict[str, Any]]` · `list[dict[str, object]]` / `-> dict[str, object \| None]` | v ×4 / **무발화** | 중첩·union 안 ✓ · 값이 union 이면 `object` 도 침묵(docstring :42 는 `Any` 만 «#645 몫» 이라 적음 — MINOR 사각) |
| p07·p18 | `TypedDict(total=False)` 필드 · `@dataclass` 필드 · ninja `Schema` 필드의 `dict[…, object/Any]` | v ×4 | class-attr 차단 ✓ |
| p13 | `x: JsonValue = json.loads` / `-> object` / `-> dict[str, object]` / 무주석 / `TypeAdapter(...).validate_python(json.loads)` / `_j.loads`·`from json import loads` | ⓓ#650 / ⓓ#647 자리표시만 / v#647+ⓓ#650 / #493 만 / 무발화 / ⓓ·무발화(리터럴 원소 object)·무발화 | 오라클 ✓ · `JsonValue` 수신이 ⓓ 로 남음(물음에 갈래 없음 — MINOR) |
| p14 | 별칭 기저 `clean -> dict[str, object]` / `Form.clean -> dict[str, Any]` / `CharField.deconstruct` / 비-Form `clean` | 면제 / v / 면제(자리표시 ⓓ 도 0) / v | N2-1 `_resolved_bases` ✓ |
| p15·p16·p17 | `TypeIs[dict[str, Any]]` / `x: dict[str, Any], **kw: dict[str, Any] -> Any` / 모듈·지역 `dict[str, object]` | v / #647 ×2 + #645 bare 1 + ⓓ#645 0 / ⓓ ×2 | 배타 ✓ · variable 사이트 ⓓ ✓ |
| p08 | TC else 직계 `class _Base(admin.ModelAdmin)` / `@admin.register` 맨몸 / 데코 + 헤더 ignore / `class R(_Base)` | 무발화 / ⓐ v(:17 class 줄) / ⓑ v 1건 / 통과 | N-2·좌표·접기 ✓ |
| **p09** | `class X(Repo):  # type: ignore[type-arg]`(비-django 제네릭) | **ⓑ v «django-stubs 제네릭 맨몸을 덮었다»** | 계획 A-2 의도(전 클래스 헤더)이나 문면이 기저를 단정 — MINOR |
| p10·p11·p12 | 같은 파일 별칭 2회 정의(TC 앞/뒤) / `[misc, type-arg]` 여러 줄 · `[misc]` · code 없음 / `import … as dj_admin`·`options import ModelAdmin as MA`·`ListView`·`TemplateView` | 통과 ×2 / ⓑ · ⓐ · ⓐ(ⓓ 대신 — bare 우선) / ⓐ ×3 · 무발화 | 뒤 정의·코드 분해·origin ✓ |
| r01 | 별칭 기저 / 비선언 별칭 / 런타임 subscript / mixin-first TC ClassDef / 별칭 사슬 5 | #493 0 / #493 v / #493 0 + ⓓ#646 / #493 0 · #646 0 / #493 v · #646 0 | 수정 1 ④·N-1 ✓ · depth≤4 문서대로 |
| q01 | `Status[A] \| Status[B]` · 문자열 · `Union[…]` · `Optional[…] \| …` · `responses.Status`·`ninja.Status`·`S2` / 별칭 `Resp` / `list[Status[A]] \| Status[B]` / 상자 하나 2형 | #648 ×6 / **무발화** / 무발화 / 무발화 | origin·평탄화 ✓ · Assign 별칭 사각(MINOR) |
| q06 | `Schema, RootModel[…]` · 역순 `_Schema` · `ninja.Schema, pydantic.RootModel` · `root_model.RootModel` · 데코 클래스 / `_S = Schema` / 단독 | #649 ×5 / **무발화** / 무발화 | ✓ · Assign 별칭 사각(MINOR) |

결정성: 파일 집합·출력 정렬(:787)·exit 규약 무변 · git 비의존 · 루트 필터는 상대 경로 성분(:644).

### 2.4 규범 정합

- 신설 17 문면 ↔ 검사기 ↔ 등재 ↔ 회신: R-3458/R-3459(SKILL:89) ↔ #646(:872-928) ↔ spec:1175·predicates:245 ↔ 회신 S-1 — 일치. R-3447/R-3448 rev2·R-3451~R-3457(SKILL:76-87) ↔ #647/#650 매트릭스(:732-757·:935-1017) ↔ spec:1176·1179·predicates:246-247 ↔ 회신 S-4 — 일치. R-3463~R-3467 ↔ #648/#649(:7182-7195) ↔ spec:1177-1178·predicates:248-249(⑤-2 MAJOR-1 반영 실재) ↔ 회신 S-5 — 일치. R-3460/R-3461(§18)·R-3462(web)·R-3466(ninja SKILL) restates 정합. MINOR ①: SKILL:76 «면제는 둘 — `forms.Form` 하위 `clean()`·`TypeIs/TypeGuard`」 vs 검사기 `FRAMEWORK_OVERRIDE_EXEMPT`(:163-166 `deconstruct`×Field 포함 · `ModelForm`/`BaseModelForm` 도 clean 면제) vs spec:1176 «`Form.clean`·`Field.deconstruct`» — 그래프 문면이 검사기보다 좁다. MINOR ②: R-3459 문면 주어는 django-stubs 기저인데 ⓑ 는 전 클래스 헤더(p09) — predicates:245 ⑵ 는 «클래스 헤더」 라 넓게 적어 등재끼리도 어긋남. MINOR ③: `evidence/impl/probe18-summary.md` «admin 5+forms 5+CBV 32 = 42» ↔ 검사기 docstring·predicates «forms 9(46)」 — django-stubs 6.1.0 `forms/models.pyi:57-313`·`formsets.pyi:30` 실측 9 가 맞고 증거 문서가 stale.
- 저작 규약: ISSUED 3467행(R-3467 = 3467번째 행 · 중복 0 · 결번 0) · LEDGER 17행(graph 15 · baseline 1 · prose 1 · 사유 기재) · 개정 9 = `prov:wasRevisionOf` + rev 번호(R-3447 rev2 amendment `@2026-09-04b` · R-3448 rev2 **redefinition** `@b` · R-3154/R-3163/R-2715 rev2 · R-0284 rev4 `@b` · R-0345 rev3 `@b` · R-0349 rev2 · R-0331 rev2 `@2026-09-04` — 계획 Δ4 그대로) · 신설 17 = rev 1 · wiring: R-3448·R-3451·R-3452·R-3455·R-3458·R-3459·R-3461 enforcedBy public-surface · R-3463·R-3464 enforcedBy api-error · delegatedTo 계획 §1 표대로(R-3464 design-review-api · R-3465·R-3466 둘 다 · R-3467 design-review-api).
- 도구(`rv6/verify.log` · 6/6 green): ontology-gate 전 ttl green · meta-SHACL·SHACL · hierarchy 9종 불일치 0 · golden 23 · gate-smoke 12 · **issued-check 위반 0 · ledger-check 위반 0** · render-sync 541 red 0 · structural 12/12 · query-golden 7종 · corpus_mirror 11/11 in-sync · spec_lint 위반 0 ×3 · tree 140행 in-sync · fixture 104/104 · baseline 73/73 · count 73/73 · findings_smoke 15/15 · drift 8/8 · anchor-smoke 14/14 · rulepack «팩 == render(그래프) · 양 런타임 미러 동일» · manifest green draft(sealed_commit 9578c59 = HEAD 봉인 관례) · cross 348/348 · registry_gate_smoke 33/33 · web green. target-counts 2919/546/3476/3594 는 hierarchy `--with-golden` 이 재계산 대조(불일치 0).
- 미러: `cmp` 6파일(검사기 3·registry_gate·pregate json·rulepack) 동일 · `diff -rq -x __pycache__ dddjango/scripts codex-…/scripts` exit 0 · final.md 7종 byte 동일 · codex hand: houserules SKILL 본문 = 마커·이름 접두 차뿐(기존 «(위)/(아래)» 1자 차는 이 배치 밖) · Coordinator «무관» 판정식·ⓓ 신규·#648·신규 3규칙 문장 4종 양쪽 1회 · ninja SKILL:34 동일 · django SKILL §18 행 양쪽.
- 등재 집계 재계수(`spec` 558행 grep): ast 293 · ast+ 60 · human 27 · path 172 = 552 · blocker ast 281·ast+ 59·path 154·human 6 = 500 · path+ast blocker 435 — 표 :218-221·:274-280·:287 과 일치.

### 2.5 효과 정직성·문서 불일치 목록

| # | 위치 | 기재 | 실물 | 심각도 |
|---|---|---|---|---|
| 1 | 로드맵 `2026-09-03-improvement-roadmap.md:28` 18행 커밋 셀 «56b27e1 · d701df8 · cad221b» · «⑤ 리뷰 6(⑤-1 MAJOR 1 정정)» · `:111` «⑤-2 3기(진행 중)» | ⑤-2 이전 상태 | ⑤-2 MAJOR 1(predicates 누락) + 정정 30a2a24 완료 · 루브릭:89 는 반영됨 · 조감도 :638 «⑥ 감사 대기」 는 맞음 | MINOR(C1-2) |
| 2 | issues.md `:136` §2-A 수정 1 ⑤ «`Any` 조건부 구절» | 사용자 확인된 수정 1 의 일부 | ① B-2 로 **철회**·R-3154 rev2 대체(루브릭:56·:66) — 결정 정본에 철회 표기 0 | MINOR(C1-1 · 결정↔구현 추적성) |
| 3 | 회신 3 `:15` «레인 7개(첫 도입 커밋 기준)» | 7 | 재현: 파일별 첫 도입 커밋 6(spring accounts 06346ff·fortune_record eda6b96 · kkebi cb3f4ad·c2b2bfd·fb14fa2·65c1ffd) · 패턴 접촉 커밋 9 — 산식에 따라 6~9 | MINOR(산식 병기 권고) |
| 4 | `evidence/impl/probe18-summary.md` «42 origin» · cce542d 메시지 | 42 | 검사기 46(forms 9) — §2.4 ③ | MINOR(증거 stale) |
| — | d701df8 «verify 6/6» 거짓 표기 | — | piece2-summary:25 · 루브릭:82 · DEVELOPMENT.md:82 세 곳에 **정직 기록 잔존** · cad221b 정정 hunk 실물 확인 · 30a2a24 메시지 «verify 6/6(verify5.log)» = 로그 6/6 209초 | 검증됨 |
| — | 회신 §2 ②④⑤⑦ · §3 수치 · 루브릭 ⑤-2 · piece 표 | — | §2.2 전 셀 재현(111·218·155 포함) | 검증됨 |

### 2.6 회귀 위험

- **#493 면제 회복**: 4사본 집합 불변(3216/3225/3225/173 · lost 0 gained 0) → 사라지는 기존 지적은 픽스처 8건뿐(수정 1 ④ 결정 안) · 새 면제는 별칭·subscript·mixin-first 기저가 선언적 이름으로 풀릴 때만(:364-373) — 비선언 별칭은 그대로 red(r01 Q).
- **#645**: 위반 라인·메시지 byte 동일(4사본) · nested ⓓ 감소분은 전량 #647 슬롯으로 이동(1:1) · `web/`·`scripts/` ⓓ 잔존 240(nested 155)은 기존 그대로.
- **#648/#649 exit 0→2**(4사본 api-error): 전부 legacy(앵커 차분 L∩N) — 신규 산출물만 귀속 · 기존 승인 레인의 G2 재실행에서는 registry_gate 가 격리(kkebi 실측 귀속 0). 단 **루트 직접 실행**(Phase 0 빚 스캔)에는 spring 7·kkebi 6 함수가 새 빚으로 뜬다(회신 ⑦ 기재 ✓).
- **#646 ⓑ 전 클래스 헤더**: 비-django 제네릭 기저에 `type: ignore[type-arg]` 를 단 기존 코드가 있으면 새 빚(4사본 실측 0 — spring 18·kkebi 21 전부 django 기저) · 문면이 django-stubs 를 단정하므로 오탐 시 오해 소지(§2.3 p09).
- **ⓔ1 R-0331 rev2**: 문면 «이번 산출물의 컨트롤러가 … 선언했으면» — 기존 레인의 승인 «auto» 는 소급 반송 대상이 아님(dddjango.md:119) · 리딩 BC 는 발주측 OpenAPI 승인 사안(회신 ⑥).
- **ⓔ2 registry_gate**: exit 산식 무접촉(diff · `cand_*` 는 보고·sidecar 만) · ⓓ 0 인 저장소는 payload byte 무변(smoke P0′) · legacy ⓓ 는 매 레인 건수만 — kkebi 1,269 를 감수자 입력에서 뺀다.

## 3. 사용자 고지 항목(결정 밖 — 머지 브리프에 실을 것 · 각 2줄 쉬운 말)

1. **ⓔ1 Coordinator R-0331 rev2**(dddjango.md:119): 「오류 응답을 `response=` 에 적은 컨트롤러를 만들었는데 승인된 에러 프로필(12-slot)이 없으면, 검사기를 `auto` 로 돌려 넘어가지 않고 G1 로 되돌려 프로필부터 정한다」. 리딩 레인처럼 #63 이 `auto` 에서 잠들어 «0건» 이 되던 구멍을 문면으로 막는 것 — 기존 승인 레인은 소급 안 됨.
2. **ⓔ2 registry_gate ⓓ 앵커 차분**(registry_gate.py:98·:295-300·:761-763·:804-812): 「감수자에게 주는 ⓓ 후보도 위반처럼 앵커(이전 커밋)와 비교해 **새로 생긴 것만** 넘긴다 · 옛 후보는 건수만」. kkebi 1,269건 같은 legacy 후보가 매 레인 감수 입력에 다시 실리지 않게 하는 것 — exit 판정은 안 바뀐다.
3. **#646 ⓑ 범위**: ignore 판정은 django 기저를 못 풀어도(타 모듈 별칭) 잡기 위해 **모든 클래스 헤더**의 `# type: ignore[type-arg]` 를 본다(계획 A-2) — 비-django 제네릭에 단 ignore 도 걸리며 문면은 django-stubs 를 단정한다(4사본 실측 0).
4. **결정 문면과 다른 기술 조정 2**: §2-A 수정 1 ⑤ «`Any` 조건부 구절» 철회(정본 예시가 `Any` 0 으로 strict 통과 → R-3154 rev2 로 대체) · ddd 예시는 `TypedDict` 가 아니라 `dict[str, FieldValue]` 닫힌 union(키가 동적인 Knowledge Level 이라 결정표 «조회표」 행).
5. **#647 면제 3번째** `deconstruct`×`*Field`(스텁 `Field.deconstruct -> …dict[str, Any]` 강제 · rv1 A-9) — SKILL §4 문면은 «면제는 둘」 이라 적혀 있어 문면·검사기가 어긋난다(§4 권고).

## 4. 조건 목록

| # | 조건 | 성격 | 수리 위치 |
|---|---|---|---|
| C1-1 | issues.md §2-A 수정 1 ⑤(:136)에 «철회 — ① B-2 · R-3154 rev2 대체(rv1-B)» 1구 추기 — 결정 정본이 구현과 다른 문장을 «확정» 으로 남기지 않게 | 결정↔구현 추적성 | `workspace/plan/2026-09-04-field-report-repair-3-issues.md` 1행 · 산문 |
| C1-2 | 로드맵 18행(:28) 커밋 셀에 30a2a24 · «⑤-2 MAJOR 1(predicates 등재) 정정」 · §8(:111) «⑤-2 3기(진행 중)» → 완료·⑥ 로 갱신(조감도 :638 은 ⑥ 뒤 한 번에) | 문서 정직성 | `workspace/plan/2026-09-03-improvement-roadmap.md` 2행 · 산문 |
| C2 | 머지 브리프(10줄 이하)에 §3 고지 1~5 를 실어 사용자 확정 뒤 머지 — 1·2 는 예고된 확장, 3~5 는 기술 조정의 사후 확인 | 결정 게이트 | 브리프 |
| 권고(머지 뒤 소배치) | R-3448 rev2 b7 «면제는 둘」 → «셋(`deconstruct`×Field 포함)」(ttl→렌더→LEDGER→미러) · #646 ⓑ 메시지를 «제네릭 기저 ignore」 로 중립화 + R-3459/predicates 범위 문면 일치 · public-surface docstring 검출 한계에 «Assign 별칭(`M = Mapping`) 미추적 · `dict[…, object \| None]` 값 union 침묵」 · api-error docstring에 «`Status`/`Schema` Assign 별칭 미추적」 · #650 물음에 «`JsonValue` 로 받았으면 통과」 갈래 · probe18-summary 42→46 · 회신 «레인 7」 산식 병기 | MINOR | 별도 |

## 5. 머지 판정

**조건부 머지 가능** — C1-1·C1-2(산문 2파일 3행 · 규범·검사기·미러 무접촉) 브랜치 안 반영 + C2(§3 고지 5 를 실은 브리프에 사용자 확정) 뒤 main 로컬 머지. 규범·검사기·미러·도구 전부 green 이고 무손실이 byte 동일 재실측으로 닫혔으며 회신 3 수치가 전 셀 재현됐다. 남은 것은 결정 정본·로드맵의 문서 정직성 2건과 결정 밖 항목의 고지뿐이다.

## 더럽힌 경로

없음 — `make verify` 뒤 `git status --short` 공백(아래). 실행 부산물은 전부 scratchpad(`fr3/rv6/{scripts-old,scripts-new,out,probes,verify.log,lossless_rv6.log,gate-kkebi.log,gate-kkebi-introduced.json,mypy_cache}` · 사본 4곳의 untracked `.dddjango/violations/*.jsonl` 누적 · spring 사본 `mp_probe_rv5b/` 는 rv5-B 잔재 · 내 `mp_probe_18/`·`rv6_probe.md` 는 삭제). live 두 저장소 무접촉.

`git status --short` (HEAD 179017f · 감사 종료 시점): (공백)
