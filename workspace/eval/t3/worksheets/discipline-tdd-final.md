# T3 저작 워크시트 — discipline-tdd-final

> 원문 `dddjango/skills/discipline-tdd/references/final.md`(1122행 · 센서스 동결본과 일치, 드리프트 0) · spec `workspace/eval/t3/specs/discipline-tdd-final.spec.json`
> 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/discipline-tdd-final.spec.json` → **exit 0**(`--write` 미사용) · 절 44 · 블록 180 · Work 150.

## 1. census 대사

발주서(=센서스 E06) 규범 수 ↔ spec Work 수. **불일치 5절** 외 39절 전량 일치. 5건은 모두 같은 원인 — 같은 문서 안 §5.5/§7.6 정본의 **사본 문장 Work 미승격**(authoring.md §15 «정본 1곳만 Work 승격 + 사본 블록에 djr:restates»). 강등 총계는 −6(4절 1문장씩 + s058-12.1 2문장).

> **적대 리뷰 반영(F1·F2)**: 초판은 s015-4.2를 4→3, s058-12.1을 2→1로 잡았으나 원문 대조 결과 ⑴ 244행 둘째 문장 **뒷절**의 회귀 테스트 형태 의무는 §5.5에 없어 승격(→ s015-4.2 4=4 일치), ⑵ 957행은 **두 문장 전량**이 442행의 사본이라 추가 강등(→ s058-12.1 2→0)했다. 총계 150은 불변(+1−1).

| section_key | 헤딩 | 발주서 | spec | 블록 | 판정 |
|---|---|---|---|---|---|
| s001 | TDD 개발 방법론 가이드 | 2 | 1 | 1 | **불일치** — 사본 1문장 강등 |
| s006-2.1 | 2.1 기본 사이클 [테스트주도 개발] | 11 | 11 | 6 | 일치 |
| s012-3.4 | 3.4 실전 권고: 상황별 선택 | 1 | 1 | 8 | 일치 |
| s015-4.2 | 4.2 회귀 방지의 위상 [Khorikov] | 4 | 4 | 3 | 일치 |
| s018-4.5 | 4.5 세 가지 테스트 스타일 [Khorikov] | 2 | 1 | 7 | **불일치** — 사본 1문장 강등 |
| s021-5.1 | 5.1 테스트 후보 목록 | 10 | 9 | 4 | **불일치** — 사본 1문장 강등 |
| s022-5.2 | 5.2 한 단계 테스트 | 2 | 2 | 1 | 일치 |
| s023-5.3 | 5.3 시작 테스트 | 2 | 2 | 2 | 일치 |
| s024-5.4 | 5.4 설명 테스트 | 1 | 1 | 1 | 일치 |
| s025-5.5 | 5.5 영구 테스트 입장 심사와 현행 계약 수명 주기 | 57 | 57 | 48 | 일치 |
| s027-6.1 | 6.1 가짜로 구현하기 (Fake It) | 2 | 2 | 5 | 일치 |
| s028-6.2 | 6.2 삼각측량 (Triangulation) | 2 | 2 | 3 | 일치 |
| s029-6.3 | 6.3 명백한 구현 (Obvious Implementation) | 2 | 2 | 2 | 일치 |
| s031-7.1 | 7.1 테스트 격리 | 3 | 3 | 3 | 일치 |
| s032-7.2 | 7.2 AAA 패턴: Arrange-Act-Assert [Osherove] | 3 | 3 | 3 | 일치 |
| s033-7.3 | 7.3 테스트 데이터 | 3 | 3 | 3 | 일치 |
| s034-7.4 | 7.4 명백한 데이터 | 1 | 1 | 2 | 일치 |
| s035-7.5 | 7.5 테스트 명명 규칙 [Osherove] | 1 | 1 | 2 | 일치 |
| s036-7.6 | 7.6 Mock보다 출력·상태 검증을 우선한다 [Khorikov] | 4 | 4 | 1 | 일치 |
| s037-7.7 | 7.7 깨진 테스트 / 깨끗한 체크인 [테스트주도 개발] | 1 | 1 | 3 | 일치 |
| s038-8 | 8. 테스트 더블 분류 체계 | 1 | 1 | 2 | 일치 |
| s040-9.1 | 9.1 이중 루프 TDD (Double Loop TDD) | 2 | 1 | 3 | **불일치** — 사본 1문장 강등 |
| s041-9.2 | 9.2 Walking Skeleton [Freeman & Pryce - GOOS] | 3 | 3 | 3 | 일치 |
| s042-9.3 | 9.3 Mock Roles, Not Objects [Freeman, Pryce, Mackinnon, Waln | 3 | 3 | 1 | 일치 |
| s043-9.4 | 9.4 Tell, Don't Ask 원칙 [Freeman & Pryce - GOOS] | 1 | 1 | 3 | 일치 |
| s045-10.1 | 10.1 값 객체 (Value Object) | 1 | 1 | 2 | 일치 |
| s046-10.2 | 10.2 널 객체 (Null Object) | 1 | 1 | 2 | 일치 |
| s047-10.3 | 10.3 팩토리 메서드 (Factory Method) | 1 | 1 | 3 | 일치 |
| s049-11.1 | 11.1 차이점 일치시키기 | 2 | 2 | 1 | 일치 |
| s050-11.2 | 11.2 변화 격리하기 | 1 | 1 | 1 | 일치 |
| s051-11.3 | 11.3 데이터 이주시키기 | 6 | 6 | 8 | 일치 |
| s052-11.4 | 11.4 메서드 추출하기 | 1 | 1 | 2 | 일치 |
| s053-11.5 | 11.5 메서드 인라인 | 1 | 1 | 1 | 일치 |
| s054-11.6 | 11.6 인터페이스 추출하기 | 1 | 1 | 2 | 일치 |
| s055-11.7 | 11.7 메서드 옮기기 | 1 | 1 | 1 | 일치 |
| s056-11.8 | 11.8 메서드 객체 | 1 | 1 | 2 | 일치 |
| s058-12.1 | 12.1 행위 냄새 (Behavior Smells) | 2 | 0 | 11 | **불일치** — 과대 산정, 사본 2문장 강등 |
| s060-13 | 13. 레거시 코드 다루기 | 1 | 1 | 2 | 일치 |
| s061-14 | 14. Property-Based Testing | 1 | 1 | 2 | 일치 |
| s062-15 | 15. Mutation Testing | 1 | 1 | 2 | 일치 |
| s064-16.1 | 16.1 TDD와 BDD의 관계 | 1 | 1 | 11 | 일치 |
| s066-17.1 | 17.1 TDD as Prompt Engineering | 2 | 2 | 3 | 일치 |
| s069-17.4 | 17.4 dddjango Admission을 추가한 TDAID 6단계 | 6 | 6 | 2 | 일치 |
| s070-18 | 18. Python 테스트 생태계 심화 | 1 | 1 | 2 | 일치 |
| **합계** | | **156** | **150** | **180** | −6(사본 강등) |

**불일치 5절 사유 (전건 «발주서 과대 산정 — 사본 계수», spec 쪽이 옳다)**

| 절 | 강등한 문장 | 정본 | 근거 |
|---|---|---|---|
| s001 (2→1) | 5행 «`reuse`·`reject`에서는 새 test artifact를 만들지 않는다» | s025-5.5/b17 (418행 «`reuse`·`reject`에서는 새 test file·case·assertion·helper를 포함한 test artifact write가 0이다») | 발주서 비고가 스스로 «3중 사본(서문·skill s004·§5.5)의 하나»라고 판정. 남긴 1건(3~4행 «이 문서에서 … 모든 절은 … 전제로 한다»)은 §5.5에 없는 **문서 전역 스코프 Override**라 승격 유지 |
| s018-4.5 (2→1) | 302행 전단 «**출력 기반 > 상태 기반 > 통신 기반** 순으로 선호하라» | s036-7.6/b1 (601행 — 같은 규칙을 «소유»로 선언한 절) | 발주서 비고 «§7.6과 2중 규칙». 소유 선언이 §7.6 쪽에 있으므로 §7.6이 정본. 후단(«순수 함수로 추출하여 출력 기반 테스트를 극대화하라»)은 §7.6에 없어 승격 유지 |
| s021-5.1 (10→9) | 359행 3문 «각 후보는 §5.5의 영구 테스트 입장 심사를 통과한 `add`·`update`일 때만 Red가 된다» | s025-5.5/b2 (398행 심사 행 확정 의무) | 발주서 비고가 스스로 «전역 규칙 재진술 포함»이라 명시 |
| s040-9.1 (2→1) | 620행 말미 «각 영구 테스트 후보는 §5.5를 통과해야 한다» | s025-5.5/b2 | 발주서 비고 «후자는 전역 규칙 재진술» |
| s058-12.1 (2→0) | 957행 **두 문장 전량**(«여기서 분리는 … recipe다» + «분리 자체가 새 영구 case를 추가할 근거는 아니며, 새 case마다 §5.5의 독자적인 failure 판정이 필요하다») | s025-5.5/b35 (442행 말미 «테스트를 나누는 행위는 가독성 recipe일 뿐 새 case의 입장 근거가 아니다» = Work #65 + 중복 판정) | 초판은 전단을 «냄새 해결책이라는 적용 문맥 부가»로 승격 유지했으나, 문맥 부가는 **별개 실행위가 아니다** — 금지 내용(분리를 근거로 새 case 추가 금지)이 #65와 동일해 §15 «정본 1곳만 Work 승격» 위반. s012-3.4(표 강등 Override)·s066-17.1(신규 주절 Permission)의 유지 근거와 달리 s058에는 고유 실행위가 없어 2문장 모두 강등 |

**계수가 정확히 맞은 큰 절 2건(과소·과대 아님 확인)** — s025-5.5는 57=57, s006-2.1은 11=11로 재구성이 일치했다. 재구성 경로는 §4 경계 메모에 적었다.

**s015-4.2의 4=4 재구성(부분 재진술 절단면)** — 242행 2(설계 원칙 의무) + 244행 2. 244행 두 문장 중 첫 문장(«장애가 보고되면 먼저 §5.5의 candidate로 두고 … 확인한다»)은 §5.5에 없는 **트리거(장애 보고)+절차 배치**라 승격, 둘째 문장은 **절 단위로 갈린다**: 앞절(«기존 테스트가 같은 failure를 잡으면 `reuse`»)은 s025-5.5/b12(412행) 축자 재진술이라 미승격, 뒷절(«그 장애로 실패하고 통과하면 수정됐다고 볼 수 있는 테스트를 작성한다»)은 **회귀 테스트의 형태 기준**을 규정하는데 §5.5 b10 `add`(«독자적인 production failure를 보호할 새 영구 테스트를 만든다»)에도, 문서 어디에도 이 형태 기준이 없어(전문 grep — «장애로 실패»·«수정됐다» 유일 출현 244행) 승격했다. 블록 restates는 **부분 재진술 표시**로 유지하되, 적대 리뷰 N1 반영으로 **b12 + b2 2건 병기**다(첫 문장 = b2 심사 3열의 압축 재서술 · 둘째 문장 앞절 = b12 사본). Work 4=4·계수·byte 등가는 불변이고 갈리는 것은 restates 배열뿐이다(§13 블록 단위 restates의 알려진 해상도 한계 — §3.1 말미 자인과 동형).

## 2. 배선 근거 표 (전 규범 150)

무소유 0 — 150건 전건이 `delegatedTo`를 가진다. `enforcedBy`는 **0건**이다: `dddjango/scripts/check-*.py` **27종 docstring 선두를 배선 전 전량 실독**한 결과 discipline-tdd 규범을 지목하는 ①문면 역할명·②§ 인용·③P0 커버 근거가 한 건도 성립하지 않았다(실독 판정은 표 아래 참조). 근거 코드 범례는 표 끝에 있다.

| # | 절 | 블록 | Work label | class | enforcedBy | delegatedTo | 근거 |
|---|---|---|---|---|---|---|---|
| 1 | s001 | b1 | 문서 전역 — 테스트 작성·Red는 §5.5 add/update 결정을 전제 | Override | — | discipline-reviewer | T1 |
| 2 | s006-2.1 | b1 | Red — add/update 승인 테스트의 실패 확인 | Obligation | — | discipline-reviewer | T1 |
| 3 | s006-2.1 | b1 | Green — 통과를 위한 최소 코드 작성 | Obligation | — | discipline-reviewer | T1 |
| 4 | s006-2.1 | b1 | Refactor — 중복 제거와 코드 정리 | Obligation | — | discipline-reviewer | T1 |
| 5 | s006-2.1 | b3 | 상세 1단계 — 승인된 테스트 작성 | Obligation | — | discipline-reviewer | T1 |
| 6 | s006-2.1 | b3 | 오퍼레이션의 코드 표현 형태 선행 구상 | Obligation | — | discipline-reviewer | T1 |
| 7 | s006-2.1 | b4 | 상세 2단계 — 실행 가능하게 만들기 | Obligation | — | discipline-reviewer | T1 |
| 8 | s006-2.1 | b4 | 명백한 깔끔한 해법의 즉시 입력 | Obligation | — | discipline-reviewer | T1 |
| 9 | s006-2.1 | b4 | 수 분 소요 예상 시 적어 두고 초록 막대로 복귀 | Obligation | — | discipline-reviewer | T1 |
| 10 | s006-2.1 | b5 | 상세 3단계 — 올바르게 만들기 | Obligation | — | discipline-reviewer | T1 |
| 11 | s006-2.1 | b5 | 중복 제거 후 초록 막대 복귀 | Obligation | — | discipline-reviewer | T1 |
| 12 | s006-2.1 | b6 | 작동하는 것 우선 — 분할 정복 | Override | — | discipline-reviewer | T1 |
| 13 | s012-3.4 | b7 | 상황별 선택표의 배경 지식 강등 — 저장소 기본은 고전 학파·Mock은 외부 의존성 격리 한정 | Override | — | discipline-reviewer | T1 |
| 14 | s015-4.2 | b1 | 회귀 방지는 전 테스트의 설계 원칙 | Obligation | — | discipline-reviewer | T1 |
| 15 | s015-4.2 | b1 | 테스트 설계 시점의 회귀 방지력 고려 | Obligation | — | discipline-reviewer | T1 |
| 16 | s015-4.2 | b2 | 장애 보고 시 §5.5 candidate 선행 — 계약·독자 failure·기존 coverage 확인 | Obligation | — | discipline-reviewer | T1 |
| 17 | s015-4.2 | b2 | 회귀 테스트 형태 — 보고된 장애로 실패하고 수정 시 통과 | Obligation | — | discipline-reviewer | T1 |
| 18 | s018-4.5 | b6 | 비즈니스 로직의 순수 함수 추출로 출력 기반 테스트 극대화 | Obligation | — | discipline-reviewer | T1 |
| 19 | s021-5.1 | b1 | 착수 전 테스트 후보 목록 작성 | Obligation | — | discipline-reviewer | T1 |
| 20 | s021-5.1 | b1 | 후보 목록은 탐색 메모 — test artifact 작성 의무 아님 | Prohibition | — | discipline-reviewer | T1 |
| 21 | s021-5.1 | b1 | 테스트 코드의 대상 코드 직전 작성 권고 | Permission | — | discipline-reviewer | T1 |
| 22 | s021-5.1 | b2 | 후보 목록은 행위·정책 경계를 드러내는 검토 목록 | Obligation | — | discipline-reviewer | T1 |
| 23 | s021-5.1 | b2 | 사용자 제시 경계 예시 하나가 후보 범위를 닫지 않음 | Prohibition | — | discipline-reviewer | T1 |
| 24 | s021-5.1 | b2 | 결과가 바뀌는 경계와 가장 가까운 바깥 값·보완 상태 병기 | Obligation | — | discipline-reviewer | T1 |
| 25 | s021-5.1 | b3 | 결합 정책의 축별 허용·거부 사례 분리 | Obligation | — | discipline-reviewer | T1 |
| 26 | s021-5.1 | b3 | 한 축의 거부 사례가 다른 축의 거부 사례를 대신하지 않음 | Prohibition | — | discipline-reviewer | T1 |
| 27 | s021-5.1 | b3 | 포함형 유효 기간의 마지막 유효일·다음 날 양쪽 후보 등재 | Obligation | — | discipline-reviewer | T1 |
| 28 | s022-5.2 | b1 | 다음 테스트 선택 기준 — 새 지식·구현 확신 | Obligation | — | discipline-reviewer | T1 |
| 29 | s022-5.2 | b1 | 아는 것에서 모르는 것으로 진행 | Obligation | — | discipline-reviewer | T1 |
| 30 | s023-5.3 | b1 | 시작 테스트 — 아무 일도 하지 않는 경우 우선 | Obligation | — | discipline-reviewer | T1 |
| 31 | s023-5.3 | b1 | 가르침이 있으면서 빠르게 구현 가능한 테스트 선택 | Obligation | — | discipline-reviewer | T1 |
| 32 | s024-5.4 | b1 | 테스트를 통한 설명 요청과 설명 | Obligation | — | discipline-reviewer | T1 |
| 33 | s025-5.5 | b1 | 영구 테스트의 오라클은 현재 승인된 요구·설계·지원 계약 | Obligation | — | discipline-reviewer | T1 |
| 34 | s025-5.5 | b1 | 현재 구현·기존 테스트는 조사 증거에 불과 | Override | — | discipline-reviewer | T1 |
| 35 | s025-5.5 | b1 | 계약 위반 구현 앞에서 테스트 삭제·약화 금지 — 구현 수정 | Prohibition | — | discipline-reviewer | T1 |
| 36 | s025-5.5 | b2 | 영구 test artifact 변경 전 최소 심사 행 확정 | Obligation | — | discipline-reviewer | T1 |
| 37 | s025-5.5 | b2 | 후보 목록·피라미드·coverage·과거 버그·상위 실패는 심사 우회 근거 아님 | Prohibition | — | discipline-reviewer | T1 |
| 38 | s025-5.5 | b5 | protected contract/evidence 열 기재 | Obligation | — | discipline-reviewer | T1 |
| 39 | s025-5.5 | b6 | unique production failure 열 기재 | Obligation | — | discipline-reviewer | T1 |
| 40 | s025-5.5 | b7 | existing authoritative coverage 열 기재 | Obligation | — | discipline-reviewer | T1 |
| 41 | s025-5.5 | b8 | owner/path 열 기재 | Obligation | — | discipline-reviewer | T1 |
| 42 | s025-5.5 | b9 | decision의 일곱 값 완결 | Obligation | — | discipline-reviewer | T1 |
| 43 | s025-5.5 | b10 | decision `add` — 독자 production failure 보호 신규 영구 테스트 | Permission | — | discipline-reviewer | T1 |
| 44 | s025-5.5 | b11 | decision `update` — 승인된 계약 변경에 맞춘 기존 테스트 갱신 | Permission | — | discipline-reviewer | T1 |
| 45 | s025-5.5 | b12 | decision `reuse` — 기존 권위 테스트 중복 시 신규 테스트 금지 | Prohibition | — | discipline-reviewer | T1 |
| 46 | s025-5.5 | b12 | boundary가 달라도 조건 성립 시 reuse 판정 | Override | — | discipline-reviewer | T1 |
| 47 | s025-5.5 | b13 | decision `retain` — 기존 테스트의 현행 보호 의미 유지 | Obligation | — | discipline-reviewer | T1 |
| 48 | s025-5.5 | b14 | decision `remove` — 명시적 계약 종료 근거 하의 지정 assertion·test만 제거 | Permission | — | discipline-reviewer | T1 |
| 49 | s025-5.5 | b15 | decision `reject` — 비자격 후보의 영구 테스트 승격 금지 | Prohibition | — | discipline-reviewer | T1 |
| 50 | s025-5.5 | b16 | decision `pending` — 근거·계약·중복 불명확 시 사용자·설계 결정 요청 | Obligation | — | discipline-reviewer | T1 |
| 51 | s025-5.5 | b17 | pending의 G1/G1′ 승인·Phase 2 완료 차단 | Prohibition | — | command-dddjango | T4 |
| 52 | s025-5.5 | b17 | reuse·reject의 test artifact write 0 | Prohibition | — | discipline-reviewer | T1 |
| 53 | s025-5.5 | b17 | retain 재조직은 새 case·assertion·Red 없이 동일 계약·failure 보호 | Obligation | — | discipline-reviewer | T1 |
| 54 | s025-5.5 | b17 | 재조직이 없으면 기존 artifact 무수정 | Prohibition | — | discipline-reviewer | T1 |
| 55 | s025-5.5 | b17 | remove는 명세 침묵·구현 불일치만으로 선택 금지 | Prohibition | — | discipline-reviewer | T1 |
| 56 | s025-5.5 | b18 | 영구 테스트 보호 대상 목록(자격 화이트리스트) | Permission | — | discipline-reviewer | T1 |
| 57 | s025-5.5 | b25 | 영구 테스트 비자격 항목 목록(블랙리스트) | Prohibition | — | discipline-reviewer | T1 |
| 58 | s025-5.5 | b34 | meta/introspection 형식만을 이유로 한 일괄 금지 배제 | Exception | — | discipline-reviewer | T1 |
| 59 | s025-5.5 | b34 | 공개 Python 계약의 근거 택일 입장(승인 근거 또는 deployed consumer evidence) | Permission | — | discipline-reviewer | T1 |
| 60 | s025-5.5 | b34 | 두 근거의 충돌·불명확 시에만 pending | Exception | — | discipline-reviewer | T1 |
| 61 | s025-5.5 | b34 | 내부 Schema·helper 직접 호출 introspection의 공개 wire 대체 금지 | Prohibition | — | discipline-reviewer | T1 |
| 62 | s025-5.5 | b35 | 중복 판정 3요소 비교 — boundary 차이만으로 add 금지 | Prohibition | — | discipline-reviewer | T1 |
| 63 | s025-5.5 | b35 | 타 boundary 동일 failure·독자 mechanism 부재 시 reuse | Obligation | — | discipline-reviewer | T1 |
| 64 | s025-5.5 | b35 | 상위 테스트 버그 발견만을 이유로 한 unit test 자동 복제 금지 | Prohibition | — | discipline-reviewer | T1 |
| 65 | s025-5.5 | b35 | 층이 달라도 failure mechanism이 독립일 때만 각각 add | Exception | — | discipline-reviewer | T1 |
| 66 | s025-5.5 | b35 | 테스트 분리는 가독성 recipe — 새 case 입장 근거 아님 | Prohibition | — | discipline-reviewer | T1 |
| 67 | s025-5.5 | b36 | 이번 실행 Red 전용 비계의 첫 Green 직후 제거 | Obligation | — | discipline-reviewer | T1 |
| 68 | s025-5.5 | b36 | 정상 import·행동 assertion만 존치·기존 비계 임의 삭제 금지 | Prohibition | — | discipline-reviewer | T1 |
| 69 | s025-5.5 | b37 | 현재 계약의 범위 — 구 API·저장 데이터·발행 이벤트·보안/규제 의무 포함 | Obligation | — | discipline-reviewer | T1 |
| 70 | s025-5.5 | b37 | 과거 버그 출신이라도 현행 계약을 검증하면 유효 회귀 테스트 | Permission | — | discipline-reviewer | T1 |
| 71 | s025-5.5 | b37 | 유지 근거가 과거 구현·종료 계약·버그 번호뿐이면 history-only | Prohibition | — | discipline-reviewer | T1 |
| 72 | s025-5.5 | b38 | 새 명세의 침묵은 종료 승인 아님 | Prohibition | — | discipline-reviewer | T1 |
| 73 | s025-5.5 | b38 | 의무 종료의 설계 명시·호환성 근거 요건 | Obligation | — | discipline-reviewer | T1 |
| 74 | s025-5.5 | b38 | 충돌·불명확 시 pending 설계 반송 — 삭제·약화·구현 완료 차단 | Prohibition | — | command-dddjango · discipline-reviewer | T5 |
| 75 | s025-5.5 | b39 | 조정 대상은 변경 계약·코드 경로를 직접 검증하는 관련 테스트 한정 | Exception | — | discipline-reviewer | T1 |
| 76 | s025-5.5 | b40 | 조정 ⑴ 기대 동일 시 유지 | Obligation | — | discipline-reviewer | T1 |
| 77 | s025-5.5 | b41 | 조정 ⑵ 승인된 입력·결과 변경 시 assertion 갱신·올바른 Red 확인 | Obligation | — | discipline-reviewer | T1 |
| 78 | s025-5.5 | b42 | 조정 ⑶ 현행·종료 assertion 혼재 시 분리 또는 부분 갱신 | Obligation | — | discipline-reviewer | T1 |
| 79 | s025-5.5 | b42 | 파일 전체 삭제 금지 | Prohibition | — | discipline-reviewer | T1 |
| 80 | s025-5.5 | b43 | 조정 ⑷ 전 기대 명시 종료 시 테스트 삭제 | Obligation | — | discipline-reviewer | T1 |
| 81 | s025-5.5 | b43 | 부재가 계약이 아니면 관성적 404·필드 부재 테스트 대체 생성 금지 | Prohibition | — | discipline-reviewer | T1 |
| 82 | s025-5.5 | b44 | 조정 ⑸ 구현만 계약과 다르면 테스트 유지·구현 수정 | Obligation | — | discipline-reviewer | T1 |
| 83 | s025-5.5 | b45 | 조정 ⑹ suite 전체 실패 사실만으로 대상 확대 금지 | Prohibition | — | discipline-reviewer | T1 |
| 84 | s025-5.5 | b46 | migration 전용 테스트 신규 생성·확장 금지 | Prohibition | — | discipline-reviewer | T1 |
| 85 | s025-5.5 | b46 | 기존 migration 테스트의 유지·제자리 갱신·종료 시 삭제 | Permission | — | discipline-reviewer | T1 |
| 86 | s025-5.5 | b46 | 새 migration 시나리오 필요 부분은 테스트 발명 없이 검증 공백 보고 | Obligation | — | discipline-reviewer | T1 |
| 87 | s025-5.5 | b46 | 기술적 식별 예시의 `implementation-test` §1.4 위임 | Obligation | — | discipline-reviewer | T2 |
| 88 | s025-5.5 | b47 | 현행 model·ORM·service·API·DB constraint 검증 DB-backed 테스트 허용 | Permission | — | discipline-reviewer | T1 |
| 89 | s025-5.5 | b47 | 현재 model 테스트의 migration 검증 대체 주장 금지 | Prohibition | — | discipline-reviewer | T1 |
| 90 | s027-6.1 | b1 | 승인된 실패 테스트 후 첫 구현은 상수 반환 | Obligation | — | discipline-reviewer | T1 |
| 91 | s027-6.1 | b1 | 상수의 변수 수식 치환 | Obligation | — | discipline-reviewer | T1 |
| 92 | s028-6.2 | b1 | 예가 둘 이상일 때에만 추상화 | Obligation | — | discipline-reviewer | T1 |
| 93 | s028-6.2 | b3 | 추상화 방향이 불확실할 때의 삼각측량 사용 권고 | Permission | — | discipline-reviewer | T1 |
| 94 | s029-6.3 | b1 | 단순 연산의 즉시 구현 | Permission | — | discipline-reviewer | T1 |
| 95 | s029-6.3 | b1 | 구현 확신이 있을 때 명백한 구현 채택 권고 | Permission | — | discipline-reviewer | T1 |
| 96 | s031-7.1 | b1 | 테스트의 상호 독립·실행 순서 독립 | Obligation | — | discipline-reviewer | T1 |
| 97 | s031-7.1 | b1 | 독립성 달성 전략은 공유 상태 제거 | Obligation | — | discipline-reviewer | T1 |
| 98 | s031-7.1 | b2 | pytest fixture로 테스트별 독립 상태 생성 | Obligation | — | discipline-reviewer | T1 |
| 99 | s032-7.2 | b1 | 테스트 최종 코드 구조는 AAA 패턴 | Obligation | — | discipline-reviewer | T1 |
| 100 | s032-7.2 | b1 | 사고는 Assert First·최종 코드는 위에서 아래 순서로 정리 | Obligation | — | discipline-reviewer | T1 |
| 101 | s032-7.2 | b2 | Assert First 사고법 — 단언 역추적으로 필요한 설정 도출 | Obligation | — | discipline-reviewer | T1 |
| 102 | s033-7.3 | b1 | 읽기 쉽고 따라가기 좋은 테스트 데이터 사용 | Obligation | — | discipline-reviewer | T1 |
| 103 | s033-7.3 | b2 | 데이터 간 차이에는 의미 부여 | Obligation | — | discipline-reviewer | T1 |
| 104 | s033-7.3 | b3 | 동일 상수의 다의 사용 금지 | Prohibition | — | discipline-reviewer | T1 |
| 105 | s034-7.4 | b1 | 기대값·실제값의 관계 드러내기 | Obligation | — | discipline-reviewer | T1 |
| 106 | s035-7.5 | b1 | 테스트 명명 패턴 [단위]_[상태/조건]_[기대 행위] 준수 | Obligation | — | discipline-reviewer | T1 |
| 107 | s036-7.6 | b1 | 검증 방식 우선순위 — 출력 기반 > 상태 기반 > 통신 기반 | Obligation | — | discipline-reviewer | T1 |
| 108 | s036-7.6 | b1 | Mock은 외부 의존성 격리 한정·핵심 로직은 실제 객체 출력/상태 검증 | Obligation | — | discipline-reviewer | T1 |
| 109 | s036-7.6 | b1 | Mock 우선순위표·구체 사용법의 `implementation-test` §7 위임 | Obligation | — | discipline-reviewer | T2 |
| 110 | s036-7.6 | b1 | Mock 경계의 도구는 pytest-mock `mocker` 픽스처 — 고전 학파 기본 불변 | Override | — | discipline-reviewer | T1 |
| 111 | s037-7.7 | b2 | 팀 프로그래밍 — 테스트 성공 상태로 종료 | Obligation | — | discipline-reviewer | T1 |
| 112 | s038-8 | b1 | 테스트 더블 분류·Python 구현의 `implementation-test` 위임 | Obligation | — | discipline-reviewer | T2 |
| 113 | s040-9.1 | b1 | 이중 루프라는 이유만으로 양쪽 테스트가 자동 의무가 되지 않음 | Prohibition | — | discipline-reviewer | T1 |
| 114 | s041-9.2 | b1 | Walking Skeleton — 가장 얇은 실제 기능으로 빌드·배포·테스트 end-to-end 확인 | Obligation | — | discipline-reviewer | T1 |
| 115 | s041-9.2 | b2 | Walking Skeleton의 availability test 대체 금지 | Prohibition | — | discipline-reviewer | T1 |
| 116 | s041-9.2 | b2 | 관찰 가능한 얇은 end-to-end 행동이 있을 때만 영구 테스트 후보 | Exception | — | discipline-reviewer | T1 |
| 117 | s042-9.3 | b1 | Mock의 대상은 객체가 아니라 역할 | Obligation | — | discipline-reviewer | T1 |
| 118 | s042-9.3 | b1 | 프로덕션 코드의 역할(인터페이스) 의존·테스트의 역할 Mock | Obligation | — | discipline-reviewer | T1 |
| 119 | s042-9.3 | b1 | Protocol 정의·`mocker.Mock(spec=)` 구체 구현의 `implementation-test` §7 위임 | Obligation | — | discipline-reviewer | T2 |
| 120 | s043-9.4 | b1 | Tell, Don't Ask — 정보를 받아 계산하지 말고 객체에 지시 | Obligation | — | discipline-reviewer | T1 |
| 121 | s045-10.1 | b1 | 값 객체의 생성 후 불변 유지(별칭 문제 차단) | Obligation | — | discipline-reviewer | T1 |
| 122 | s046-10.2 | b1 | 널 객체의 정상 객체 동일 프로토콜 제공 | Obligation | — | discipline-reviewer | T1 |
| 123 | s047-10.3 | b1 | 팩토리 메서드로 생성 유연성 확보 | Obligation | — | discipline-reviewer | T1 |
| 124 | s049-11.1 | b1 | 합칠 두 코드를 단계적으로 닮아가게 수정 | Obligation | — | discipline-reviewer | T1 |
| 125 | s049-11.1 | b1 | 완전히 동일해지면 둘을 합치기 | Obligation | — | discipline-reviewer | T1 |
| 126 | s050-11.2 | b1 | 변경 대상 부분의 선행 격리 | Obligation | — | discipline-reviewer | T1 |
| 127 | s051-11.3 | b1 | 표현 양식 변경 시 데이터 일시 중복 | Obligation | — | discipline-reviewer | T1 |
| 128 | s051-11.3 | b3 | 이주 1단계 — 새 포맷 인스턴스 변수 추가 | Obligation | — | discipline-reviewer | T1 |
| 129 | s051-11.3 | b4 | 이주 2단계 — 기존 세팅 지점에서 새 변수 동시 세팅 | Obligation | — | discipline-reviewer | T1 |
| 130 | s051-11.3 | b5 | 이주 3단계 — 기존 변수 사용처의 새 변수 전환 | Obligation | — | discipline-reviewer | T1 |
| 131 | s051-11.3 | b6 | 이주 4단계 — 기존 포맷 제거 | Obligation | — | discipline-reviewer | T1 |
| 132 | s051-11.3 | b7 | 이주 5단계 — 새 포맷에 맞춘 외부 인터페이스 변경 | Obligation | — | discipline-reviewer | T1 |
| 133 | s052-11.4 | b1 | 길고 복잡한 메서드 일부의 별도 메서드 분리·호출 | Obligation | — | discipline-reviewer | T1 |
| 134 | s053-11.5 | b1 | 꼬이거나 산재한 제어 흐름의 메서드 인라인 | Obligation | — | discipline-reviewer | T1 |
| 135 | s054-11.6 | b1 | 두 번째 구현 추가 시 Protocol 인터페이스 추출 | Obligation | — | discipline-reviewer | T1 |
| 136 | s055-11.7 | b1 | 메서드를 어울리는 클래스로 이동하고 호출로 대체 | Obligation | — | discipline-reviewer | T1 |
| 137 | s056-11.8 | b1 | 복잡한 메서드의 메서드 객체화 | Obligation | — | discipline-reviewer | T1 |
| 138 | s060-13 | b1 | 레거시 코드 다루기의 `discipline-cleancode` 위임 | Obligation | — | discipline-reviewer | T3 |
| 139 | s061-14 | b1 | Property-Based Testing의 `implementation-test` 위임 | Obligation | — | discipline-reviewer | T2 |
| 140 | s062-15 | b1 | Mutation Testing의 `implementation-test` 위임 | Obligation | — | discipline-reviewer | T2 |
| 141 | s064-16.1 | b10 | pytest-bdd 구현 상세의 `implementation-test` 위임 | Obligation | — | discipline-reviewer | T2 |
| 142 | s066-17.1 | b2 | §5.5 입장 테스트에 한한 AI 코딩 도구 결합 허용 | Permission | — | discipline-reviewer | T1 |
| 143 | s066-17.1 | b2 | 기능 요구·AI 위험은 새 영구 테스트의 자동 승인 근거 아님 | Prohibition | — | discipline-reviewer | T1 |
| 144 | s069-17.4 | b1 | TDAID 1단계 Plan — 요구사항에서 테스트 candidate 도출 | Obligation | — | discipline-reviewer | T1 |
| 145 | s069-17.4 | b1 | TDAID 2단계 Admission — 계약·독자 failure·기존 coverage로 decision 확정 | Obligation | — | discipline-reviewer | T1 |
| 146 | s069-17.4 | b1 | TDAID 3단계 Red — add/update 승인 실패 테스트 작성 | Obligation | — | discipline-reviewer | T1 |
| 147 | s069-17.4 | b1 | TDAID 4단계 Green — 테스트를 통과하는 구현(AI 보조) | Obligation | — | discipline-reviewer | T1 |
| 148 | s069-17.4 | b1 | TDAID 5단계 Refactor — 코드 품질 개선(AI+개발자) | Obligation | — | discipline-reviewer | T1 |
| 149 | s069-17.4 | b1 | TDAID 6단계 Validate — AI 생성 코드의 정확성·보안·성능 최종 검증 | Obligation | — | discipline-reviewer | T1 |
| 150 | s070-18 | b1 | Python 테스트 도구 생태계의 `implementation-test` 위임 | Obligation | — | discipline-reviewer | T2 |

**근거 범례 (4원 = ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N)**

| 코드 | 4원 근거 | 건수 |
|---|---|---|
| T1 | ①역할명 0 · ②check-*.py 27종 docstring 선두 전수 실독 결과 § 인용 0 · ③P0 커버 0 — ④registry Agent 등재 + §16 위임 기본값 표(discipline-tdd → `agent-discipline-reviewer`). 기본값 «도피»가 아니라 근거 부재의 귀결 | 139 |
| T2 | ①문면이 `implementation-test`(§7·§1.4·스킬 전체)를 명시 위임처로 지목 · §16 표 implementation-* → `agent-discipline-reviewer`(**동일 기본값이라 이탈 아님**) · ②지목 검사기 0 | 8 |
| T3 | ①문면이 `discipline-cleancode` 스킬을 명시 위임처로 지목 · §16 표 discipline-cleancode → `agent-discipline-reviewer`(동일 기본값) · ②지목 검사기 0 | 1 |
| T4 | ①문면이 «G1/G1′ 승인과 Phase 2 완료를 막는다(… **Coordinator 게이트 명칭**)»로 절차 게이트를 직접 지목 · §16 표 command+agents(절차 층) → `command-dddjango` — **기본값 이탈, 문면 근거 보유**(파일럿 ninja «503/409 선택의 명세 §5/G1 소유» 선례와 동형) | 1 |
| T5 | T4 동상(«`pending`으로 설계에 반송») + 뒷절의 «테스트 삭제·assertion 약화와 구현 완료를 막는다»는 규율 심사라 본 문서군 기본값 `agent-discipline-reviewer` **병기** | 1 |

**로스터 전수 실독 결과(§16 L-F 의무)**: `dddjango/scripts/check-*.py` **27종**(api-error-controller-contract · app-container · broker-contract · business-vocabulary · choices-literal-consumption · common-container · composition-root · context-isolation · db-table · domain-model · error-centralization · event-publish · idempotency-scope-creep · layer-skeleton · mechanism-ownership · missable-entrance · naming · ninja-boundary-middleware · openapi-error-declaration · port-adapter-pairing · public-surface-annotation · response-schema-bypass · synthetic-infra-exc · test-config · transaction-boundary · transient-overmapping · usecase-dto-placement)의 docstring 선두를 배선 전 전량 실독했다. **discipline-tdd 를 지목한 검사기 0종**이다. 오배선 회피를 위해 특히 확인한 근접 3종:

- `check-test-config.py` — 이름이 «테스트 규율 검사기»지만 담당은 ⑴ pytest↔Django settings **바인딩**, ⑵ 트리 105~111행 `test/` **구조**(#383~#392), ⑶ `settings/` 환경축(#445~#447)이다. §7.1 «테스트 격리»의 규범(상호 독립·공유 상태 제거·fixture 사용)이나 §5.5 입장 심사를 보는 진단이 docstring에 없다 — 겹치는 것은 낱말뿐이라 배선하지 않았다.
- `check-composition-root.py` — docstring에 «TDD»가 나오지만 «테스트가 안 걸려 TDD Red로 안 잡힌다»는 *왜 결정적 백스톱인가*의 서술이지 TDD 규범 집행이 아니다.
- `check-mechanism-ownership.py` — migrations 규율 4규칙(#336 등)을 담당하지만 대상은 **마이그레이션 파일의 배치**이고, §5.5의 «migration 전용 테스트 금지»(459행)는 *테스트*의 오라클 자격 판정이라 대상이 다르다.

따라서 `enforcedBy` 0은 «검사기를 안 찾은 것»이 아니라 **로스터에 담당자가 없다**는 실독 판정이다. 반대 방향의 오배선(기본값 도피)도 T4·T5 2건에서 문면 근거로 이탈시켜 막았다.

## 3. 재진술 유예

### 3.1 spec에 넣은 같은-문서 restates (9블록)

센서스 E06 restate 열이 «Y:discipline-tdd-final/…»로 지목한 8절을 전건 연결했고, 열이 N인 s012-3.4 1건을 직접 확인해 추가했다. 정본 쪽(s036-7.6)에는 restates를 걸지 않았다(§15 «정본 1곳만 Work 승격 + **사본 블록**에 djr:restates»).

| # | 사본 블록 | 정본 블록 | 강등 | 근거 |
|---|---|---|---|---|
| 1 | s001/b1 (3–5행 서문 인용구) | s025-5.5/b17 (418행) | 1문장 | 센서스 열 지목. **b2 병기는 기각(적대 리뷰 N2 — 2026-08-22)**: 강등 문장 전반절 «요구·버그·피라미드·예제는 먼저 candidate일 뿐»은 b2 #37(«후보 목록·피라미드·coverage·과거 버그·상위 실패는 **이 행을 건너뛸 독립 근거가 아니다**»)과 **낱말 집합만 겹치고 실행위가 다르다** — #37은 심사 행 우회 금지라는 금지 실행위이고, 전반절은 그 금지를 진술하지 않고 «candidate 지위»만 선언한다(심사 행·우회 어휘 부재). 이 지위 선언은 같은 블록에 Work로 남긴 전역 Override(«…모든 절은 §5.5에서 add·update로 결정된 행을 전제로 한다»)가 이미 지고 있어, b2를 병기하면 §4 기준 «문장 단위 되풀이»가 취지 겹침으로 헐거워진다. 취지 겹침이라는 사실만 이 칸에 남긴다 |
| 2 | s015-4.2/b2 (244행) | s025-5.5/**b12**(412행 `reuse`) + **b2**(398행 심사 행) | 0 (Work 2 유지) | 센서스 열 지목. **부분 재진술 2건**(적대 리뷰 N1 반영 — 2026-08-22): ⑴ 첫 문장이 심사 3열(protected contract/evidence·unique production failure·existing authoritative coverage)을 «승인 계약·독자 production failure·기존 권위 coverage를 확인한다»로 압축한 b2 재서술 — §4 기준 ⑵(압축 행 재서술)이 s069-17.4/b1 Admission 행에 적용된 것과 동형이라 **b2 병기**. 트리거(«장애가 보고되면»)+절차 배치는 §5.5에 없어 Work 유지. ⑵ 둘째 문장 앞절만 b12 사본이고 뒷절(회귀 테스트 형태 의무)은 §5.5에 없어 승격 |
| 3 | s018-4.5/b6 (302행) | s036-7.6/b1 (601행) | 1문장 | 센서스 열 지목(양방향 선언 — 소유 선언이 있는 §7.6이 정본) |
| 4 | s021-5.1/b1 (359행) | s025-5.5/b2 (398행) | 1문장 | 센서스 열 지목 |
| 5 | s040-9.1/b1 (620행) | s025-5.5/b2 | 1문장 | 센서스 열 지목 |
| 6 | s058-12.1/b11 (957행) | s025-5.5/b35 (442행) | 2문장 (Work 0) | 센서스 열 지목. 블록 전량이 b35 말미 문장의 준축자 사본이라 **블록 전체 강등** — 이 문서에서 사본 블록의 Work가 0이 되는 유일 사례 |
| 7 | s066-17.1/b2 (1040행) | s025-5.5/b2 | 0 (Work 2 유지) | 센서스 열 지목. 첫 문장의 **조건절**만 §5.5 되풀이이고 주절(«AI 코딩 도구와 결합할 수 있다» — Permission)은 §5.5에 없어 강등하지 않았다 |
| 8 | s069-17.4/b1 (1087–1094행 펜스) | s025-5.5/b2 | 0 (Work 6 유지) | 센서스 열 지목. Admission 행은 §5.5의 압축 사본이지만 «TDAID 6단계 중 2단계»라는 **절차 배치 의무**가 §5.5에 없어 강등하지 않았다 |
| 9 | s012-3.4/b7 (211행) | s036-7.6/b1 | 0 (Work 1 유지) | **센서스 열은 N — 직접 확인으로 추가**. 문장의 두 규칙(«저장소 기본은 고전 학파»·«Mock은 외부 의존성 격리에만»)이 601행과 문면상 겹친다. 다만 이 문장의 실행위는 «이 표는 배경 지식이다»라는 **표 강등 Override**라 Work는 유지하고 겹침만 restates로 표시했다 |

블록 단위 restates라 «한 문장만 사본»인 상황이 블록 전체로 표현되는 한계는 그대로 자인한다(cleancode s028-3.1 선례와 동형).

### 3.2 유예 — 교차 문서 재진술 13건 (spec 미기재)

T3-EXECUTION §병렬 설계 «재진술 교차 문서 쌍은 전량 유예 → 전 웨이브 완료 후 소급 패스 1회가 일괄 연결» 결정에 따라 spec에 넣지 않는다. 센서스 restate 열은 이 문서 쪽에서 `discipline-tdd-skill/s004` 1건만 지목하지만, **상대 문서(skill) 쪽 census 열과 원문을 직접 대조**해 12건을 더 확정했다. 상대 `discipline-tdd-skill`은 웨이브 3 배정이라 저작 시점에 그래프 밖이다(§15 «상대 블록이 미이관 절이면 restates 생략 + 유예 기록»).

| # | 이 문서 좌표 | 상대 문서/절·행 | 유예 사유 |
|---|---|---|---|
| 1 | s025-5.5 (절 전체) | `discipline-tdd-skill`/s004 (24·25·26행) | **센서스 E06 restate 열이 지목한 유일 교차 쌍**. 심사 절차·자격·migration 3항의 압축 요약. 정본 방향(final 밀도판 vs skill 요약판)도 소급 패스가 판정 |
| 2 | s001/b1 (3–5행) | `discipline-tdd-skill`/s004 (24·25행) | 발주서 비고가 «3중 사본(서문·skill s004·§5.5)»이라 명시 — 그중 skill 쪽 상대 |
| 3 | s006-2.1/b1 (31–35행 사이클 펜스) | `discipline-tdd-skill`/s004 (21행 «Red-Green-Refactor 순서를 지켜라 … (§2.1)») | 압축 요약 |
| 4 | s012-3.4/b7 (211행) | `discipline-tdd-skill`/s004 (22행 «고전 학파(상태 검증)를 기본으로 …(§3.1–§3.4)») | 이 문서 안 정본은 s036-7.6이고 skill 22행은 그 요약 — 교차 방향은 소급 패스 |
| 5 | s021-5.1/b1 (359행) | `discipline-tdd-skill`/s004 (24행 «테스트 목록은 후보일 뿐이다») | 압축 요약 |
| 6 | s027-6.1·s028-6.2·s029-6.3 (469·492·508행) | `discipline-tdd-skill`/s004 (27행 «초록 막대 전략: 가짜로 구현하기 → 삼각측량 → 명백한 구현 (§6.1–§6.3)») | 3절을 한 행으로 압축 — 소급 패스가 팬아웃으로 연결 |
| 7 | s031-7.1·s032-7.2 (516·541행) | `discipline-tdd-skill`/s004 (28행 «테스트는 격리하고, AAA 패턴으로 구조화하라 (§7.1–§7.2)») | 동상(2절 팬아웃) |
| 8 | s036-7.6/b1 (601행) | `discipline-tdd-skill`/s004 (29행 «Mock보다 출력·상태 검증을 우선한다 (§7.6)») | 이 문서 정본의 skill 요약 |
| 9 | s040-9.1·s041-9.2 (620·675행) | `discipline-tdd-skill`/s004 (30행 «Outside-In 이중 루프도 … 자동 의무화하지 않는다. Walking Skeleton은 실제 얇은 E2E 행동이다 (§9.1–§9.2)») | 동상(2절 팬아웃) |
| 10 | s066-17.1·s069-17.4 (1040행·펜스) | `discipline-tdd-skill`/s004 (31행 «AI 보조 TDD에서 테스트는 명세다 … (§17.1–§17.4)») | 동상(2절 팬아웃) |
| 11 | s038-8/b1 (612행) | `discipline-tdd-skill`/s003 (13행 계열) | **상대 쪽 센서스 열이 «Y:discipline-tdd-final/s038-8»로 이 절을 지목**(내 절의 열은 N) — 직접 확인으로 등재 |
| 12 | s025-5.5/b46 n4 (459행 «기술적 식별 예시는 `implementation-test` §1.4를 따른다») | `discipline-tdd-skill`/s003 (16행 «migration 전용 테스트와 DB-backed … 기술적 식별 → `implementation-test`») | 같은 위임의 2중 진술 — 소급 패스가 재진술/위임 중 어느 층인지 판정 |
| 13 | s025-5.5/b17 n1 (418행 «`pending`은 G1/G1′ 승인과 Phase 2 완료를 막는다») | `discipline-tdd-skill`/s004 (25행 말미 «`pending`은 G1을 막고 …») | 게이트 차단 규칙의 skill 요약 — 배선(T4)이 같은 Coordinator라 소급 연결 시 소유 충돌 없음 |

#### 3.2.1 정본-측 참고 — 기저작 문서에 있는 §5.5 사본 (적대 리뷰 N5 반영 · 2026-08-22)

규약상 교차 재진술의 1차 책임은 **사본 측 문서**지만, 실측 결과 **양쪽 모두에서 빠진 쌍**이 있어 소급 패스 안전망으로 좌표만 기재한다. spec은 무변(같은 문서 쌍이 아니다). 상대 문서는 이미 저작됐고 그 워크시트의 유예 목록에도 이 다리가 없다 — `agent-discipline-reviewer` 워크시트 §3의 R4는 상대를 `agent-coder`/s004·`command-dddjango`/s007로만 지목해 `discipline-tdd-final` 쪽을 잡지 않았고, s007/b4는 유예 목록에 항목 자체가 없다.

| # | 이 문서(정본) 좌표 | 상대 문서/절(실독 좌표) | 관계 |
|---|---|---|---|
| C1 | s025-5.5/b36 (444행 «이번 실행 Red 전용 비계는 첫 Green 직후 제거 · 작업 전부터 있던 비계 임의 삭제 금지») | `agent-discipline-reviewer`/s005/b6 (spec 행 L54–55 = 현재 파일 L58–59 «첫 Green 비계» 불릿 — graph-owned 주석 삽입분 오프셋) | 감사 측 문면의 사본(«남아 있으면 blocker»로 판정어만 바뀜). 상대 워크시트 R4가 이 다리를 누락 |
| C2 | s025-5.5/b46 (459행 «migration 전용 테스트 신규 생성·확장 금지 …») | `agent-discipline-reviewer`/s007/b4 (spec 행 L68 = 현재 파일 L75 «신규·확장 migration 전용 테스트가 없는가 … 근거 `discipline-tdd` §5.5») | 상대 문면이 **근거로 §5.5를 명시 인용**하는 감사 측 사본. 상대 워크시트 유예 목록에 미등재 |
| C3 | s025-5.5/b17 (418행 «`pending`은 G1/G1′ 승인과 Phase 2 완료를 막는다 · `reuse`·`reject`는 test artifact write 0 · 일반 `retain` 무편집») | `dddjango/agents/design-architect.md` 83행 (`agent-design-architect` 입장 표 절) | 설계 측 압축 사본(«`pending`은 리뷰 뒤 0개여야 G1을 요청할 수 있고, `reuse`·`reject`는 test artifact write가 0이다») |
| C4 | s025-5.5/b17 + b10~b16 (decision 7값의 편집 허용 범위) | `command-dddjango`/s007 (Phase 2 — 현재 파일 L96 step 2 «decision을 다시 만들지 말고 다음대로 dispatch한다: `add/update`만 새·변경 Red와 test edit, `reuse`는 … write 0, 일반 `retain`은 무편집, … `pending`은 G1/G1′ 반송») | 절차 층 dispatch 사본군. 이 문서 배선의 T4(«`pending`은 G1/G1′을 막는다» → `command-dddjango`)와 같은 소유자라 소급 연결 시 소유 충돌 없음. 정본 방향·팬아웃 범위는 소급 패스가 확정 |

**재진술이 아니라 배선으로 처리한 «위임 포인터»**: `implementation-test` §7(s036-7.6·s042-9.3)·§1.4(s025-5.5 b46)·스킬 전체(s038-8·s061-14·s062-15·s064-16.1·s070-18), `discipline-cleancode` 스킬(s060-13). 이들은 같은 문장의 사본이 아니라 **소유 이전 명문**이므로 `delegatedTo` 근거(T2·T3)로만 쓰고 restates를 걸지 않았다(cleancode 워크시트 §3 말미 선례와 동일 처분).

## 4. 경계 판단 메모

- **공백 소유(§13) — 규약 문면을 채택**: 블록 간 구분자(빈 줄)를 **선행 블록의 후행 스팬**에 귀속시켰다(§13 명문). 절 선두 구분자(헤딩 직후 빈 줄)는 44/44절 전건 첫 블록 선두 귀속(§13이 명시한 유일 예외). 절 말미의 `---` 수평선은 **별도 prose 블록**으로 분리했다(s012-3.4 b8·s025-5.5 b48·s029-6.3 b2·s037-7.7 b3·s038-8 b2·s043-9.4 b3·s047-10.3 b3·s056-11.8 b2·s060-13 b2·s061-14 b2·s062-15 b2·s064-16.1 b11·s069-17.4 b2·s070-18 b2 — 14건). 코퍼스 실측을 먼저 했다: 웨이브 1의 7 spec + 파일럿 2 spec에서 블록 간 구분자는 lead 252 · trail 240으로 **혼재**해 단일 판형이 없었으므로(cleancode 워크시트 §5.1이 이미 상신한 «규약 §13 문면 vs 실측 판형» 사안), 판형을 흉내 내지 않고 규약 문면을 일관 적용했다. byte 등가는 도구의 «헤딩 + 블록 연결 = 절 스팬» 단언이 44/44절 통과로 보장한다.
- **kind 분포**: norm 103 · table-row 28 · code 26 · prose 23 = 180. `checklist-item`은 이 문서에 `- [ ]` 형태가 0건이라 미사용.
- **code 블록이 Work를 진술한 3건(s006-2.1 b1 · s035-7.5 b1 · s069-17.4 b1)**: 세 절 모두 규범 운반체가 펜스뿐이라 다른 자리가 물리적으로 없다. §2.1은 헤딩 다음이 곧 사이클 펜스(31–35행)이고, §7.5는 절 전체가 펜스 2개(581–583·585–597)이며, §17.4는 절 본문이 6단계 펜스(1087–1094) 하나다. 발주서도 각각 «코드 펜스 안 사이클 절차 지시 3»·«명명 패턴은 코드 펜스 형식 명세지만 규범 1 계수»·«6단계 코드 펜스 절차를 규범 계수»로 같은 판정을 미리 적었다. §13대로 kind는 code(리터럴 datatype `xsd:string`)를 유지했다 — cleancode 워크시트 §5.2가 상신한 «code 블록 Work 진술» 첫 사례에 이어지는 3건이다.
- **표의 Work 0 판정(28 table-row 블록 전건)**: §3.4 표는 바로 아래 인용구가 «이 표는 배경 지식이다»로 **강등**했고(실규범은 그 인용구가 진술), §4.5 스타일 표·§12.1 냄새 표·§16.1 TDD/BDD 비교표는 명사구 준규범이라 문장이 아니다(발주서 비고 «표 해결책 열 6칸은 명사구 준규범, 문장 아님(P0 승계)»). 머리행·구분행도 §13대로 kind=table-row로 실었고 계수에는 산입하지 않았다.
- **명사구 불릿 14개(§5.5 화이트 6항 422–427행 · 블랙 8항 431–438행)**: 지배문(420행·429행)에 Work 1씩만 걸고, 불릿 14블록은 **kind=norm·norms 0**으로 두었다. 발주서 비고 «명사구는 지배문 1씩만 계수»의 직역이고, 파일럿 `spec-implementation-django-ninja-final`의 s022-6.1 b2~b14(상태 코드 불릿) 판형과 같은 형태다.
- **s025-5.5의 57 재구성 경로**(발주서와 정확히 일치): 396행 3 + 398행 2 + 열 설명 불릿 4(403–406) + 408행 1 + decision 7값 8(`reuse` 412행만 2문장) + 418행 5 + 화이트 지배문 1 + 블랙 지배문 1 + 440행 4 + 442행 5 + 444행 2 + 446행 3 + 448행 3 + 450행 1 + 조정 6분기 8(454·455행만 2문장) + 459행 4 + 461행 2 = **57**. 심사표(400–401행)는 데이터 행이 0이라 0으로 두었다 — 표가 아니라 **열 설명 불릿 4개**가 스키마 규범을 진술한다고 봤고, 그래야 57이 닫힌다.
- **s006-2.1의 11 재구성 경로**(발주서와 일치): 펜스 3행(Red/Green/Refactor) 3 + 39행 2(«승인된 테스트를 작성한다» / «어떤 식으로 나타내길 원하는지 생각해보라» — «이야기를 써내려가는 것이다»는 비유라 제외) + 40행 3(«실행 가능하게 만든다» / «명백하면 입력하라» / «몇 분 걸릴 것 같으면 적어 두고 복귀» — «빨리 초록 막대를 보는 것이 가장 중요하다»는 가치 서술이라 제외) + 41행 2(«올바르게 만든다» / «중복을 제거하고 초록 막대로 되돌리자» — «죄악을 수습하자»는 앞 문장의 비유 반복) + 43행 1 = **11**. 애매 구간이라 제외 판정을 여기 남긴다(P0 «애매» 승계).
- **규범 vs 서술 경계**: ① s037-7.7의 «혼자 프로그래밍» 불릿(605행)은 «좋은 단서가 된다»는 서술이라 kind=prose·Work 0, «팀 프로그래밍»(606행)만 계수(발주서 «혼자 규칙은 서술형 제외»). ② s027-6.1의 «두 가지 효과» 불릿 2개(487–488행)는 효과 서술이라 prose. ③ s058-12.1의 925행(«테스트를 실행할 때 발생하는 문제들.»)·s064-16.1의 1015행(BDD 진화형 설명)·s066-17.1의 1038행(인용 경구)은 서술이라 prose. ④ s050-11.2 824행 후단(«격리 방법에는 … 등이 있다»)·s051-11.3 830행(«내부에서 외부로의 변화 단계:»)은 열거·지배 서술이라 Work 0.
- **class 판정**: Obligation 97 · Prohibition 29 · Permission 13 · Override 6 · Exception 5 = 150(적대 리뷰 N3·N4 반영 후 — 초판은 O97·Perm14·Ex4였고 #8 Perm→Obl·#60 Obl→Ex로 O가 −1+1 상쇄됐다). Permission은 «…하는 것이 좋다»류 권고(s021-5.1 «직전 작성»·s028-6.2 «감잡기 어려울 때»·s029-6.3 2건)와 decision `add`/`update`/`remove`(자격이 성립할 때의 허용), 화이트리스트, DB-backed 허용에 썼다. Override는 순위·강등·범위 재선언 6건(서문 전역 스코프·«작동하는 것부터 먼저»·«현재 구현은 조사 증거일 뿐»·boundary 무관 `reuse` 판정·§3.4 표 강등·§7.6 도구만 격상). Exception은 한정·면제 5건.
- **«…때만/…만 + 결과» 문형의 class 자(적대 리뷰 N3 반영 — 2026-08-22)**: 전건을 좁히는 한정 문형은 결과절이 의무형이어도 **Exception**으로 통일한다. ⑴ 이 문서의 형제가 이미 그렇다 — #75(450행 «…관련 테스트**만** 다음처럼 조정한다» — 결과가 의무형인데 Exception)·#65(442행 «…독립적일 **때만** 각각 `add`할 수 있다»)·#116(«…있을 **때만** 후보»). ⑵ 문형이 다른 «…**만으로** …하지 않는다» 계열은 배제 실행위라 Prohibition으로 갈린다(#62·#81·#83) — 두 계열은 형태로 구분된다. ⑶ 따라서 **#60(440행 «두 근거가 충돌하거나 어느 쪽도 명확하지 않을 때만 `pending`이다»)의 초판 Obligation을 Exception으로 고쳤다**. 부수 효과로 정합성이 하나 더 맞는다: Obligation 독법이면 #60은 b16 #50(«`pending` — 근거·계약·중복 불명확 시 결정 요청»)의 특례 반복이 되어 same-doc restates 후보가 되지만, 한정 독법이면 «한쪽 근거만 명확하면 pending 금지»라는 #59 적용 범위 한정이라 고유 실행위가 선다.
- **명령형 분기의 class 자(적대 리뷰 N4 반영 — 2026-08-22)**: Permission은 **권고·허용 문형**(«…하는 것이 좋다»·«…해도 된다»·decision 자격 허용)에만 쓰고, **명령형·청유형은 조건절이 붙어도 Obligation**(조건부 의무)으로 둔다. 40행의 두 분기는 «깔끔한 해법이 명백히 보인다면 **그것을 입력하라**»(명령형)와 «몇 분 걸릴 것 같으면 … **돌아오자**»(청유형)로 문형이 대칭인데 초판이 #8만 Permission으로 갈랐다 — **#8을 Obligation으로 고쳤다**. §6.2 504행 «사용하면 좋다»·§6.3 508행 «그렇게 하는 것이 좋다»는 권고형이라 Permission을 유지한다(초록 막대 전략의 선택지 맥락은 §6 쪽 문면이지 §2.1 40행의 문면이 아니다).
- **«…의무/근거가 아니다» 부정문의 class 관례(적대 리뷰 F3 — 미반영 판정)**: s021-5.1 359행 2문(«이 목록은 탐색 메모이지 test file·case·assertion·helper 작성 의무가 아니다» = #20)의 `Prohibition`을 유지한다. ⑴ 이 문장의 실행위는 «작성하지 않을 허용» 부여가 아니라 **추론 차단**(목록에 올랐다는 사실을 작성 근거로 삼지 말라)이다. ⑵ 같은 형태의 형제 규범이 이 문서에서 전건 Prohibition이다 — #23 «경계 예시 하나가 후보 범위를 닫지 않음»·#26 «한 축의 거부 사례가 다른 축을 대신하지 않음»·#37 «후보 목록·피라미드·coverage·과거 버그·상위 실패는 심사 우회 근거 아님»·#113 «이중 루프라는 이유만으로 자동 의무 아님»·#144 «기능 요구·AI 위험은 자동 승인 근거 아님». ⑶ 코퍼스 관례도 동일하다(`implementation-test-final`/s004-1.1 «상위 레벨 발견 버그는 자동 unit test 의무 아님» = Prohibition — 동형 문면. 이 계열에 Permission을 쓴 사례는 T3 전 spec에서 0건). ⑷ Override는 이 문서에서 **경합하는 상위 규칙의 순위·범위를 재선언**하는 6건에만 썼는데 359행에는 뒤집을 상위 규칙이 없다(§3.4 표 강등·서문 전역 스코프와 구조가 다르다). #20만 Permission/Override로 바꾸면 형제 5건과 어긋나므로 관례를 유지한다.
- **same-doc `restates` 기재 기준(적대 리뷰 F4 — 기준 명문화)**: 블록에 `restates`를 거는 조건은 **문장 단위 되풀이**다. ⑴ 정본 규범 문장을 통째로 다시 진술하거나(s001·s021-5.1·s040-9.1·s018-4.5·s058-12.1), ⑵ 정본 규범의 내용을 조건절·압축 행으로 재서술한 경우(s066-17.1 1040행 «§5.5에서 `add/update`로 입장된 테스트에는 …» — §를 명시 인용하며 심사 통과 요건을 되풀이하는 **문장 단위 조건절** · s069-17.4 1089행 «2. Admission : 계약·독자 failure·기존 coverage로 decision 확정» — 심사 3열+decision을 한 행으로 압축한 사본 · **s015-4.2 244행 첫 문장 «먼저 §5.5의 candidate로 두고 승인 계약·독자 production failure·기존 권위 coverage를 확인한다» — 같은 3열 압축이라 적대 리뷰 N1 수리로 b2 병기**)에 건다. 기준 ⑵의 판별점은 **정본 규범의 구성요소(열·요건·결정값)를 이름 그대로 되풀이하는가**이고, 낱말 집합만 겹치는 취지 중복은 대상이 아니다(s001 전반절 — §3.1 #1 근거란의 N2 기각 사유). 반대로 **결정값 낱말의 관형 수식구 재사용은 걸지 않는다**: s006-2.1/b1 32행 «`add/update`로 승인된 작은 테스트»와 s027-6.1/b1 469행 «`add/update`로 승인된 실패 테스트를 만든 후»는 §5.5의 결정값 어휘를 **전제로 참조**할 뿐 b2 규범(«영구 test artifact 변경 전 최소 심사 행 확정»)을 재진술하지 않고 §·요건도 인용하지 않는다. 이 전제 참조는 서문 s001/b1의 전역 Override(«이 문서에서 “테스트 작성”이나 Red를 말하는 모든 절은 … `add`·`update`로 결정된 행을 전제로 한다»)가 **문서 전역으로 이미 선언**했으므로 절마다 재기재하면 전역 선언과 중복된다. 기준 적용 결과 s006-2.1/b1·s027-6.1/b1은 비대상이라 restates를 추가하지 않았다 — s066·s069는 기준 ⑵로 이미 기재돼 있어 문서 안 처리는 갈리지 않는다.
- **배선 기본값 이탈 2건(T4·T5)**: §5.5 418행 «`pending`은 G1/G1′ 승인과 Phase 2 완료를 막는다(G1/G1′=파이프라인 설계 승인 게이트 · Phase 2=구현 국면 — **Coordinator 게이트 명칭**)»과 448행 «`pending`으로 설계에 반송하며 …»는 문면이 절차 게이트를 직접 지목하므로 §16 표의 «command+agents(절차 층) → `command-dddjango`»로 배선했다. 파일럿 ninja의 «503/409 선택의 명세 §5/G1 소유 → command-dddjango»와 동형 근거다. 448행은 뒷절(«테스트 삭제·assertion 약화와 구현 완료를 막는다»)이 규율 심사라 `agent-discipline-reviewer`를 병기했다. 나머지 148건은 기본값이며, **기본값 도피가 아님**은 §2 말미의 27종 전수 실독 판정이 증빙한다.
- **enforcedBy 0의 의미**: 이 문서는 코퍼스에서 드물게 결정적 검사기 담당이 **하나도 없는** 규범군이다. TDD 규율은 «입장 심사 판정»·«테스트 의미»처럼 정적 검사 밖의 의미 층이 대부분이고, 이름이 가장 가까운 `check-test-config.py`조차 담당이 pytest 바인딩·`test/` 트리 구조·settings 환경축이라 겹치지 않는다. T2-2 alias 대장(`ontology/wiring/aliases.ttl`)에 이 문서 몫 #N 조인이 생길 여지도 현재는 없다.

