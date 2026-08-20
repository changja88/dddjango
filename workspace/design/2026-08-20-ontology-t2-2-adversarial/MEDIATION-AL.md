# T2-2 선행 설계 리뷰(레인 AL — codex) 중재 (2026-08-20)

> 발견 15행 = **blocker 5 · major 5 · 반증 실패 5**. 중재: **채택 10 · 기각 0**.
> blocker 4건은 부모가 독립 재현으로 확증(§0). 판단표는 **v2 로 재작성**하고, 검사 ⑥·⑥′는 **전면 강화** 후
> 대장을 저작한다 — 즉 «적용 전 리뷰»가 거짓 alias 1건 유입과 검사 우회구 2개를 실제로 막았다.

## 0. 부모 독립 재현 (채택 근거)

| 주장 | 재현 결과 |
|---|---|
| AL-1 `#119` 는 합성 규칙(소유 + 재선언 금지) — 파일럿이 R-0075/R-0076 으로 원자 분리 | **확증**: `R-0076 a djr:Prohibition ; skos:prefLabel "framework 오류의 BC 전환·전역 handler 가로채기 금지"@ko`(implementation-django-ninja-final.ttl:605~606) 실재 |
| AL-2 `#488` 의 정확한 Work 는 R-0120 — 누락 | **확증**: `R-0120 a djr:Obligation ; skos:prefLabel "고정·재등장 칸의 빈 패키지 존속"@ko`(architecture-ddd-final.ttl:181~182) 실재 |
| AL-5 ⑥·⑥′ 의 `golden` 부분문자열 필터가 **생산 위반의 이름 기반 우회구** | **확증**: 합성 그래프에서 `alias-golden-bypass`+`alias-plain` 이 같은 `rule#700` 으로 다른 Work 를 가리키는데 `alias_errors()` → `[]` |
| AL-6 ⑥′ 의 «Work 폐포 안»은 해소 증명이 아님(미발행 bare Work 통과) | **확증**: `djr:not-issued-work a djr:Work` 를 가리키는 alias 에 대해 `alias_errors()` → `[]` |
| AL-7 §5 «교집합 0»이 문서 자신의 집합으로도 거짓(#488 양쪽 존재) | **확증**: 판단표 §5 가 나열한 T2-1 번호 집합에 `#488` 이 있고, 실제로 T2-1 매핑표는 `#488` 을 «36 귀속»이 아니라 **타 소유자 이관**(§3.2 V3 — layer-skeleton 소유)으로 분류(attribution-map:338·511·544) — **집합 구성 자체가 틀렸다** |

## 1. 처분표

| 출처 | 심각도 | 처분 | 반영 |
|---|---|---|---|
| AL-1 (#119) | blocker | **채택** — 등재 취소 | 판단표 v2: `#119` **미등재**(compound legacy rule — R-0075+R-0076 1:N 이라 함수적 alias 불가). `alias-unabsorbable` 전용도 기각(v2 유형 정의는 «비유일 준-ID»용) · compound/part-of 관계 설계는 T3 |
| AL-2 (#488) | blocker | **채택** — 신규 등재 | 판단표 v2: **`#488 → R-0120` unique 등재**. 후보 생성 절차 정정: basis 번호뿐 아니라 **같은 블록의 `statesNorm` Work 전수 + prefLabel 대조** |
| AL-5 (golden 우회) | blocker | **채택** | 생산 alias 검사는 `load_graph(with_golden=False)` 그래프에서 수행 — 이름 기반 필터 **전면 제거**. 우회 시나리오를 red fixture 로 고정 |
| AL-6 (⑥′ 해소 부실) | blocker | **채택** | ⑥′ 강화 4조건: ① `#R-\d{4}$` 형식 ② **ISSUED 등재** ③ `currentExpression` 정확히 1 ④ Expression 왕복(`prov:specializationOf` + `djr:revision`). WorkShape `currentExpression minCount 1` 추가는 **셰이프 개정**이라 별건(§3 백로그) |
| AL-7 (교집합 거짓) | blocker | **채택** | 판단표 v2 §5 전면 재작성 — «violatesWork 사실상 0» 주장 **삭제**. `rule#488→R-0120` 이 실조인이며 layer-skeleton 이 실발화하므로 **T2 범위에서 실값 적재 가능**. 집합 구분 신설: «T2-1 세 검사기 직접 귀속 36» ↔ «27종 전체 실발화 #N» |
| AL-3 (보류 4) | major | **채택** | #195·#257·#259·#260 **전건 미등재 확정** — 합성 Work 의 구성 절은 alias 가 아니다(v2 «다대일»은 여러 대체 식별자가 한 Work 로 해소된다는 뜻). 검사기도 #259·#260 을 별개 사건으로 발화(check-domain-model.py:271·394) |
| AL-4 (문법 미강제) | major | **채택** | ⑥″ 신설: `aliasText` 가 `^rule#[1-9][0-9]*$` 이고 그 번호가 **규칙 원장에 실재**해야 한다(rule-owner-map 538행 — 부재 시 재료 결손). 금지 문자열(`"#10"`·`"rule#010"`) red fixture 편입 |
| AL-8 (self-test 부실) | major | **채택** | `--root` 신설 + **end-to-end red-first 하네스**: 임시 정본 트리(rules+wiring+vocab)에 결함 fixture 를 넣고 **프로그램 exit** 를 단언(7종: duplicate·golden 이름 우회·bare Work·미발행 Work·문법 위반·leading-zero·정상 대조군) |
| AL-9 (수치 오명명) | major | **채택** | «23/446=5.2%» → **후보 발견률**로 정명하고, **확정 alias 조인률 3/446=0.7%** 병기. 446종·125/3,235=3.9% 는 유지(codex 가 AST 전수 파싱으로 독립 재확인) |
| AL-10 (처분 분리) | major | **채택** | «파일럿 Work 존재 + alias 판정 가능인데 미해소» = **fail-closed 결함**, «파일럿 Work 자체 부재» = T3 정상 상태로 분리. **T2 종료 전 `#488` 의 `violatesWork`/`violatesExpression` 레코드 1건 이상 end-to-end 실증**을 완료 기준에 편입 |
| AL-11 (R-0122 의 #490 오인용) | major | **채택(백로그)** | R-0122 본문의 «루트 평면은 #486·#490 위반» 중 `#490` 은 주어 스코프(`application/<bc>/**`) 밖이라 **기존 Work 본문의 잘못된 legacy 인용**이다. 다만 그래프 `djr:text` 는 산문 정본의 **verbatim 스팬**이라 그래프만 고치면 렌더 동기가 깨진다 → **산문 정본 개정 + 재이관 + E6 provenance** 필요. **표류 트랙 백로그 등재**(T3 이관 시 동반 처분) |
| AL-반증 실패 5 | — | 확인 | 등재 `#3→R-0124`·`#486→R-0118` 유지 · 미등재 16 중 나머지 유지 · 선결 판단 3건 유지(임시 사본 게이트 green 실증) · 저작 실물 7축(wiring 배치·render·gate 병합·mirror·ISSUED·LEDGER·계수) 유지 · 계수 **2→5 유지**(노드 집합만 교체) |

## 2. 확정 대장 (v2 — 등재 3건)

| aliasText | aliasFor | aliasType | 근거 |
|---|---|---|---|
| `rule#3` | `djr:R-0124` | `alias-unique` | «BC 경계는 관문으로만 넘는다»(SPEC:340) ↔ «컨텍스트 간 접근은 ACL·OHS로만» |
| `rule#486` | `djr:R-0118` | `alias-unique` | «어느 BC 를 열어도 골격이 그대로»(SPEC:812) ↔ «표준 트리 골격의 예외 없는 빈 패키지 실현» |
| `rule#488` | `djr:R-0120` | `alias-unique` | «고정 이름 칸은 부모가 있으면 반드시 있다 — 빈 파일»(SPEC:814) ↔ «고정·재등장 칸의 빈 패키지 존속» |

## 3. 백로그(본 중재 밖 — 별건 등재)

1. `WorkShape-currentExpression minCount 1` 추가(셰이프 개정 — 어휘 v1 봉인 §7 절차) · 계층 공리 외부 주입 차단.
2. R-0122 본문의 `#490` 오인용(AL-11) — 산문 정본 개정·재이관·provenance.
3. compound legacy rule(`#119` 류) 표현 설계 — alias 가 아닌 part-of 관계(T3).
4. 어댑터 구조 쟁점(`ViolationShape` minCount 1 ↔ D12) — `-t2-2-violation-adapter.md` 소유. **AL-10 이행으로 `#488` 조인분은 정상 적재 가능**해졌으므로 «변환 결과 0» 전제는 소멸(선행 계약·센티널 미조인분 처분만 남는다).
