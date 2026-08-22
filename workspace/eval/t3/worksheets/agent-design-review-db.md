# T3 저작 검수표 — agent-design-review-db

- 원문: `dddjango/agents/design-review-db.md` (현재 44행 · 발주서·센서스와 일치 — 5절 전건 스팬 해시를 `ontology_migrate.py` 가 센서스 기준선과 대조해 통과 · **마커 미삽입 원문**이라 현재 행 = 센서스 행)
- spec: `workspace/eval/t3/specs/agent-design-review-db.spec.json` (REF 5절 · 블록 24 · Work 45)
- 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-design-review-db.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)
- 실독 이행: 발주서 · `T3-authoring-brief.md` · `ontology-authoring.md` §13~§16 · `ontology_migrate.py` 선두 docstring · 파일럿 판형 2건 · **`check-*.py` 27종 docstring 전수**(묶음 공통 1회). 데이터 축 쟁점 검사기는 docstring 전문(담당 규칙 목록·가드 계약)까지 다시 읽었다 — `check-transaction-boundary`·`check-db-table`·`check-mechanism-ownership`·`check-idempotency-scope-creep`·`check-event-publish`·`check-domain-model`.
- 판정 승계 출처: `workspace/eval/t3/worksheets/agent-design-review-api.md`(자매 리뷰어 문서 — §0 P-A/P-B/P-C 갈래 · 발견/권고 불릿의 «census 과소» 판정 · 경계 절 dash 병합) · `workspace/eval/t3/reviews/agent-design-review-api-findings.md`·`agent-coder-findings.md`(부분 커버 basis 의 한계 명시 의무 · 축 반대 검사기 배제 강도). 이 문서에는 코드 펜스·표·체크박스가 0이라 kind 는 norm/prose 2종뿐이다.

## 0. 배선 정책 (§16 4원 종합의 이 문서 적용판)

자매 문서 `agent-design-review-api` 검수표 §0 의 세 갈래를 이 문서에 맞춰 승계했다.

- **P-A 절차·산출 형식 규범**(호출·입력 격리·리뷰 노트 형식·집행성 판정·경계) → `command-dddjango`. 근거 = §16 위임 기본값 표 «command+agents(절차 층) → Coordinator». s001~s003·s005 가 여기 든다. 이 갈래에 `enforcedBy` 가 0인 것은 도피가 아니라 실독 결과다 — 27종 중 «에이전트 호출·리뷰 입력 격리·노트 형식·집행성 판정»을 보는 검사기가 0이다.
- **P-B 심사 대상(architect 명세의 데이터 결정) 규범** → `agent-design-review-db`. 근거 = ①문면 술어가 심사 행위(«…맞는가»·«…확인한다»·«감사한다») + ④§16 위임 기본값 표 **architecture-db 행 → `agent-design-review-db`**. s004 가 여기 들고, 같은 축을 코드에서 집행하는 검사기가 실재하면 `enforcedBy` 를 병기해 «기계 절반 + 의미 잔여»를 분업시켰다.
- **P-C 타 소유 명시** → 문면이 다른 역할을 판정 소유자로 지목한 조항만 그 Agent 병기: s003 b1-2(architect — «반영은 architect의 몫») · s004 b4-10(discipline-reviewer·acceptance-tester — «후자는 discipline-tdd·acceptance-tester 몫») · s004 b5-5·b8-2(Coordinator — `pending` 의 G1 blocker 효과·반송) · s005 b2(ddd·api 리뷰어).
- **enforcedBy 절제(과잉 배선 방지)** — 심의하고 **배제한** 검사기와 사유:
  - `check-idempotency-scope-creep` — docstring 자기 선언이 «태스크가 요청하지 않은 멱등성을 architect 단계에서 silent 의무화해 코드로 구현하는 회귀를 차단»(G0=확장금지)이라 **축이 반대**다. 이 문서의 s004 b4-5(«치명적이면 §9.6 블록 8행을 확인한다»)·b6(«필요한 경우 설계됐는가»)는 «필요한 블록을 요구»하는 방향이라 이 검사기가 발화하면 오히려 반대 판정이 된다. 자매 문서가 같은 검사기를 «축 반대»로 배제한 강도를 그대로 적용했다.
  - `check-event-publish` — outbox 전달 보장(b6)의 인접 후보였으나 담당 규칙 16개가 전부 «과거형 이름·`published_event/` 표면·구독 껍데기»의 구조·명명 축이고 **전달 보장 술어가 0**이다.
  - `check-domain-model` — b1-2(«모델링이 도메인을 정확히 담는가»)의 인접 후보였으나 애그리거트 «구조» 축은 s005 b2 가 ddd 리뷰어로 이관한 관심사다. 여기 병기하면 같은 기계 커버를 두 lens 에 이중 계상하게 되므로 배제했다(자매 문서의 «오용-차단 축은 부분 커버로 인정하지 않는다» 경계선과 같은 취지).
  - `check-db-table` 의 제약·유니크 축 — #630 은 신규 모델의 `db_table` «값»만, #631 은 타 BC FK 금지만 본다. b3(«제약·유니크·중복 방지가 불변식을 DB 레벨에서 보장하는가»)의 술어가 없어 배제하고, 같은 검사기는 자기 축 규범(b7-3 이주 보존)에만 뒀다.
  - **«절제 선언 = 커버» 금지선(W3-7 처분으로 명문화)**: 검사기 docstring 의 **가드 문면**(«…는 보지 않는다»)은 그 축을 집행한다는 근거가 **아니다** — 규범이 요구하는 상태를 검사기가 «강제하지 않는다»는 사실은 위반 표면에서의 침묵이지 커버가 아니다. b7-3(Work #37)의 `check-db-table` 가드 인용을 커버 근거 자리에서 빼고 배제 심의로 옮긴 근거다.
- 무소유 0건(도구가 단언). `enforcedBy` 는 **3 Work**(검사기 부착 4건 — b4-1·b7-2 각 1종 + b7-3 이 2종)에만 붙였고 전부 부분 커버 한계를 병기했다. [초판은 부착 수를 Work 수로 잘못 적어 «4 Work» 였다 — spec 실물 대조로 정정]

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

**채번 판별자(1차)**: Work 단위 = 종결절(문장). 한 문장 안이라도 ⑴ 심사 대상이 갈리거나 ⑵ 소유자(배선)가 갈리는 독립 요구는 분리하고, ⓐ 같은 행위의 상·하한(«제안하되 대신하지 않고») ⓑ dash 뒤 rationale ⓒ 술어 없는 역할 선언·근거 서술은 병합·무규범으로 둔다.

| 절 | 헤딩 | 발주서 | spec | 차 | 사유·판정 |
|---|---|---|---|---|---|
| s001 | (전문) | 4 | 4 | 0 | 조성 일치 — description 3문 + 본문 L10 3문 중 규범 1문(1문째 역할 선언·3문째 «너의 독립성이 …» 근거 서술은 무규범). adv 중재 정정(norm 2→4) 반영값과 동수 |
| s002 | 입력 | 2 | 2 | 0 | 조성 일치 — L14 3문 중 규범 2(1문째 «Coordinator가 … 준다»는 뒤 두 문장의 주어를 세우는 입력 사실 서술 · 자매 문서 `agent-design-review-api`/s003 b1 의 동일 판정 승계) |
| s003 | 산출 | 6 | 8 | +2 | census 6 = L18 3 + L23 1 + L25 2 (**발견/권고 불릿 미계수**). 두 불릿은 각각 «발견 항목이 갖출 3요소»·«권고 항목의 내용»을 독립 지시하고, 동형 4중의 다른 판(`agent-design-review-api`/s004 b2·b3 · `agent-discipline-reviewer`/s003)이 이미 각 1 Work 로 채번된 선례가 있어 대칭을 맞췄다 → **census 과소** |
| s004 | 점검 항목 (데이터 lens만) | 23 | 28 | +5 | **census 23 = 8불릿+마무리 문단의 종결절 수 합계와 정확히 일치**(독립 재계수 확인) — 문장 단위 하한이다. spec 28 의 초과 5건 전액: ⓐ L29 두 심사 대상 분리(스키마 정규화·역정규화 ↔ 도메인 모델링) +1 ⓑ L32 첫 문장의 이질 축 분리(경계·격리·락 적합성 심사 ↔ 중복·race 치명성의 «의미» 분류) +1 ⓒ L33 마지막 문장의 `pending` 절 분리(소유자가 `agent-design-review-db` → `command-dddjango` 로 갈린다 — 자매 문서 적대 리뷰 F1 «한 문장 안의 이질 축은 분리» 승계) +1 ⓓ L35 첫 문장의 세 심사 대상 분리(무중단 순서·rollout/backfill ↔ expand/contract·이력 불변 ↔ 이주 시 `db_table`·`label`·`0001` 보존 기재) +2 → **census 과소** |
| s005 | 경계 | 3 | 3 | 0 | 조성 일치 — 불릿 3개 ↔ 3 Work. L44 의 dash 뒤 절(«스코프 의문은 발견으로만»)은 같은 금지의 긍정면이라 1 Work 로 접었다(자매 문서 판정 승계) |
| **합계** | | **38** | **45** | **+7** | 과대 산정 0건 판정. spec < census 인 절이 0이라 **누락 위험 지점 없음** |

## 2. 배선 근거 표 (전 규범 45건)

표기: `E:` = enforcedBy · `D:` = delegatedTo. 근거의 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N·위임 기본값 표 는 §16 4원. **이 표는 spec JSON 에서 기계 생성했다**(표 45행 ↔ spec 45 norm 순서·값 일치 — 수리 시 재생성 의무).

| # | 절/블록 | Work label | 유형 | 배선 | 4원 근거 |
|---|---|---|---|---|---|
| 1 | s001/b2 (L3) | Phase 1 설계 단계의 Coordinator 호출 대상 | Obligation | D: command-dddjango | ①문면 — 프론트매터 description 이 Coordinator 라우팅 트리거 · ④§16 위임 기본값 표(command+agents 절차 층→Coordinator) · ②check-*.py 27종 docstring 선두 전수 실독 — 에이전트 호출·라우팅 술어 0 |
| 2 | s001/b2 (L3) | architect 설계 명세의 데이터 관점(인덱스·제약·트랜잭션·마이그레이션 안전) 단일 lens 독립 리뷰와 리뷰 노트 산출 | Obligation | D: command-dddjango | ①문면 «…데이터 관점으로만 독립 리뷰하고 리뷰 노트를 낸다» · ④절차 층 기본값 — 어느 lens 를 수행했는지의 판정 주체는 리뷰 노트를 수납하는 Coordinator(agent-design-review-api/s001 동형 배선) |
| 3 | s001/b2 (L3) | 명세·코드 직접 수정 금지 | Prohibition | D: command-dddjango | ④절차 층 기본값 — 읽기 전용 계약 위반은 절차 위반이고 코드 산출물 대상 검사기 27종의 관할 밖(s005 b1 과 동축 — 검수표 §4 재진술 의심) |
| 4 | s001/b6 (L10–11) | 데이터 관점 단일 lens 의 읽기 전용 독립 비평 수행 | Obligation | D: command-dddjango | ①문면 «*데이터 관점 하나로만* 독립적으로 비평하는 읽기 전용 리뷰어다» · ④절차 층 기본값(독립성 보장 주체가 Coordinator) — 첫 문장은 역할 선언 서술, 셋째 문장은 근거 서술이라 무규범 |
| 5 | s002/b1 (L13–15) | 명세 한정 열람 — 타 리뷰어 노트·구현 코드 열람 금지(편향 방지) | Prohibition | D: command-dddjango | ④절차 층 기본값 — 입력 묶음 공급·독립성 보장 주체가 Coordinator · ②27종 전수 실독 — 리뷰 입력 격리를 보는 검사기 0(agent-design-review-api/s003 b1 과 축자 동일 3중 — 교차 문서라 restates 유예 §3) |
| 6 | s002/b1 (L13–15) | 로드한 스킬 본문·references 참조의 제한 밖 인정 | Exception | D: command-dddjango | ①문면이 제한 대상을 «타 리뷰어의 노트·구현 코드»로 자기 한정 · ④동상 |
| 7 | s003/b1 (L17–19) | 데이터 리뷰 노트 한정 산출 | Obligation | D: command-dddjango | ④절차 층 기본값 — 산출물 종류 계약(리뷰어 3종 동형)이고 수납 주체가 Coordinator · ②27종에 리뷰 노트 술어 0 |
| 8 | s003/b1 (L17–19) | 명세 직접 수정 금지(반영은 architect 소유) | Prohibition | D: command-dddjango · agent-design-architect | ①문면 «반영은 architect의 몫» — 판정 소유 배분 지목(P-C) · ④절차 층 기본값 · s001 b2 3번째 Work 와 동축(재진술 의심 — 검수표 §4) |
| 9 | s003/b1 (L17–19) | 발견 다수 시 심각도 순(blocker→important→nit) 번호 나열 | Obligation | D: command-dddjango | ④절차 층 기본값 — 리포트 형식 계약(리뷰어 3종+discipline 4중 동형) |
| 10 | s003/b2 (L20) | 발견 항목 형식(문제+근거 위치 인용+심각도 3단계) | Obligation | D: command-dddjango | ④절차 층 기본값 — 산출 형식 계약(agent-design-review-api/s004 b2 가 같은 불릿을 1 Work 로 채번한 선례 승계) |
| 11 | s003/b3 (L21–22) | 권고 항목 형식(변경 방법 제시) | Obligation | D: command-dddjango | ④동상 — 동형 4중 |
| 12 | s003/b4 (L23–24) | 무결 시 «데이터 관점 이상 없음» 명시 | Obligation | D: command-dddjango | ④절차 층 기본값 — 무발견 보고의 명시 계약(침묵과 무결의 구분이 게이트 판정 재료) |
| 13 | s003/b5 (L25–26) | 집행성 판정 1행 기재(가능=명세 확정 결정 3곳 인용·불가=막히는 절·문장 지목) | Obligation | D: command-dddjango | ④절차 층 기본값 — 리포트 형식 계약이고 판정 수납자가 Coordinator(리뷰어 3종+discipline 4중 동형 · P0 특이 발견) · ②27종에 집행성 술어 0 |
| 14 | s003/b5 (L25–26) | 인용 없는 «집행 가능» 판정 무효 | Prohibition | D: command-dddjango | ④절차 층 기본값 — 무효 선언의 판정자는 판정을 수납·집행하는 Coordinator |
| 15 | s004/b1 (L28–29) | 스키마 설계의 정규화/역정규화 판단 적합성 점검 | Obligation | D: agent-design-review-db | ①문면 술어가 심사 행위(«…맞는가») + ④§16 위임 기본값 표 architecture-db 행 → agent-design-review-db · ②27종 전수 — 정규화·역정규화 판정 술어 0 |
| 16 | s004/b1 (L28–29) | 모델링의 도메인 정확 반영 점검 | Obligation | D: agent-design-review-db | ④동상 — 애그리거트 «구조» 축의 기계 집행(check-domain-model)은 ddd lens 소유라 여기서 병기하지 않는다(s005 b2 의 lens 이관 조항과 정합 · 이중 계상 회피) |
| 17 | s004/b2 (L30) | 인덱스의 쿼리 패턴 커버(복합·커버링·부분)와 과잉·누락 부재 점검 | Obligation | D: agent-design-review-db | ①심사형 술어 + ④기본값 표 db 행 · ②27종 grep 실측 — 인덱스·쿼리 계획 술어 0(검사 공백) |
| 18 | s004/b3 (L31) | 제약·유니크·중복 방지의 DB 레벨 불변식 보장 점검 | Obligation | D: agent-design-review-db | ④기본값 표 db 행 — check-db-table 은 앱 규율(#329 label·#630 db_table 값·#631 타 BC FK 금지)만 보고 제약·유니크 «설계 충분성» 술어는 0(전수 실독) |
| 19 | s004/b4 (L32) | 트랜잭션 경계·격리 수준·락의 정합성·동시성 적합성 점검 | Obligation | E: check-transaction-boundary.py / D: agent-design-review-db | ②docstring 「한 트랜잭션 = 애그리거트 하나」(D50)·#195 «상태를 바꾸는 유스케이스는 애그리거트를 건너뛰지 않는다»·#197 읽기 전용 UoW·#200 after_commit — 코드 측 «경계» 축 집행(부분 커버: 격리 수준·락 «선택»의 적합성 술어는 0) · ④기본값 표 db 행 |
| 20 | s004/b4 (L32) | 이 쓰기의 중복·race 치명성 의미 분류('Risky Write' 라벨·§9.6 인용 유무가 아닌 연산 성격 기준) | Obligation | D: agent-design-review-db | ①문면 «의미로 분류한다» — 앞 절(경계 적합성 심사)과 행위 대상이 갈려 분리 채번 · ②검사 공백(의미 분류 술어 0) · ④기본값 표 db 행 |
| 21 | s004/b4 (L32) | 주문·결제·재고·예약·환불·권한·ledger 신호의 자동 판정 불인정(실제 중복·이중적용·동시성 위험 있을 때만 블록 요구) | Exception | D: agent-design-review-db | ①문면 «…신호이지 자동 판정이 아니다 — … 있을 때만 블록을 요구한다» 조건 한정 · ④동상 |
| 22 | s004/b4 (L32) | 라벨·인용 부재 시에도 돈·재고·권한·원장 변경 연산의 Risky Write 직접 재분류 | Obligation | D: agent-design-review-db | ①문면 «리뷰어가 직접 Risky Write로 재분류한다» — 심사 주체를 문면이 자기 지목 · ④기본값 표 db 행 |
| 23 | s004/b4 (L32) | 치명적 쓰기의 architecture-db §9.6 Risky Write Consistency Block 8행 존재·각 행 처리 확인 | Obligation | D: agent-design-review-db | ①문면이 8행(Transaction owner·Locking strategy·Rule ownership·Idempotency storage·API handoff·Side-effect timing·Isolation/retry·Test criteria)을 리터럴로 규정 · ②check-idempotency-scope-creep 은 «태스크가 요청하지 않은 멱등성의 silent 의무화» 차단(G0=확장금지)이라 «필요한 블록이 채워졌는가»와 축이 반대 → 배제 심의 · ④기본값 표 db 행 |
| 24 | s004/b4 (L32) | 각 행의 결정 내용 또는 근거 있는 '미적용' 기재 시 충족 인정(빈칸·무언급만 미기재) | Exception | D: agent-design-review-db | ①문면 «…적혀 있으면 충족 — 빈칸·무언급만 미기재다» — 충족 판정의 한정 조항 · ④동상 |
| 25 | s004/b4 (L32) | 블록 부재(§9.6 번호 인용만)·8행 누락·어느 행 미기재의 blocker 판정 | Obligation | D: agent-design-review-db | ①문면 «…면 blocker.» · ④기본값 표 db 행(발견 상신은 리뷰어 소유, 게이트 수납은 s003 b1 계열 Work 가 진다) |
| 26 | s004/b4 (L32) | 블록 존재의 «의미적 충족» 판정(리터럴 '§9.6' 문자열 불요·다른 제목·표 아닌 행 나열 허용) | Obligation | D: agent-design-review-db | ①문면 «리터럴 '§9.6' 문자열이 아니라 8행의 *의미적 충족*으로 판정한다» — 판정 기준 규정 · ②검사 공백(명세 문면 판정) · ④동상 |
| 27 | s004/b4 (L32) | 중복·race 비치명 논증 시 블록 불요와 트집 금지 | Exception | D: agent-design-review-db | ①문면 «블록 불요 — 트집잡지 않는다» 조건 한정(같은 축의 상·하한이라 1 Work) · ④동상 |
| 28 | s004/b4 (L32) | 심사 범위의 8행 구조 완전성 한정(Test criteria 의 동시성 충분성은 discipline-tdd·acceptance-tester 몫) | Obligation | D: agent-discipline-reviewer · agent-acceptance-tester | ①문면 «후자는 discipline-tdd·acceptance-tester 몫» — 판정 소유 배분 직접 지목(P-C) · ④§16 위임 기본값 표 discipline-tdd 행 → agent-discipline-reviewer + 문면 지목의 acceptance-tester 병기 |
| 29 | s004/b5 (L33) | 영구 테스트 입장 표 DB 후보별 감사(현재 DB 보장·rollout/consumer evidence·독자 constraint/transaction/race failure·기존 권위 coverage) | Obligation | D: agent-design-review-db | ①문면 술어 «감사한다» + ④기본값 표 db 행 — 입장 표는 명세 산출물이라 코드 검사기 관할 밖(27종 전수 실독) |
| 30 | s004/b5 (L33) | Risky Write·outbox·제약 Test criteria 의 candidate signal 한정(자동 add 불인정) | Prohibition | D: agent-design-review-db | ①문면 «candidate signal이지 자동 `add`가 아니다» · ④동상 |
| 31 | s004/b5 (L33) | migration mechanics·DB/framework 기본 동작 재검증·독자 failure 없는 계층 복제의 reject/reuse 방향 | Obligation | D: agent-design-review-db | ①문면 «…는 `reject/reuse` 방향이다» — 후보 유형별 기본 판정 방향 · ④동상 |
| 32 | s004/b5 (L33) | 위험·candidate 제안 허용과 중앙 decision 대체 금지 | Prohibition | D: agent-design-review-db | ①문면 «제안하되 중앙 decision을 대신하지 않고» — 같은 행위(제안)의 상·하한이라 1 Work · ④동상 |
| 33 | s004/b5 (L33) | pending 의 G1 blocker 상신 | Obligation | D: command-dddjango | ①문면 «`pending`은 G1 blocker로 올린다» — 게이트 통과 판정 소유는 Coordinator(agent-design-review-api 의 같은 조항 판정 승계) · 한 문장 안의 이질 축 분리 채번 |
| 34 | s004/b6 (L34) | 멱등성 저장소·outbox 전달 보장 필요 시 설계 여부 점검 | Obligation | D: agent-design-review-db | ④기본값 표 db 행 · ②배제 심의 — check-idempotency-scope-creep 은 «미요청 멱등성의 silent 도입» 차단이라 «필요한데 설계됐는가»와 축이 반대(agent-design-review-api 의 같은 배제 판정과 동일 강도) · check-event-publish 는 발행 «표면·과거형·구독 껍데기» 구조 축이라 전달 보장 술어 0 |
| 35 | s004/b7 (L35) | 무중단 순서·rollout/backfill 계획 확인 | Obligation | D: agent-design-review-db | ①심사형 술어 «확인한다» + ④기본값 표 db 행 · ②27종 — 배포 순서·backfill 술어 0 |
| 36 | s004/b7 (L35) | 생성될 마이그레이션 연산의 expand/contract·이력 불변 준수 확인 | Obligation | E: check-mechanism-ownership.py / D: agent-design-review-db | ②docstring ⑵ #593 «`migrations/` 안은 사람이 직접 손대지 않는다 — 도구 산출물 모양의 허용 목록 밖은 전부 위반»·#337 «파일 이름은 django 가 매긴 번호 꼴» — 이력 불변 축의 코드 측 집행(부분 커버: expand/contract 순서 «설계» 판정은 미커버) · ④기본값 표 db 행 |
| 37 | s004/b7 (L35) | 기존 앱 표준 구조 이주 명세의 기존 db_table·label·0001 보존(클래스 rename 은 state-only) 기재 확인 | Obligation | E: check-db-table.py · check-mechanism-ownership.py / D: agent-design-review-db | ①문면이 implementation-django §10.4 를 메커니즘 출처로 인용 · ②커버 근거는 «보존»에 실제로 닿는 세 술어뿐이다 — check-db-table #329(`label` 명시 의무 · §10.4 step 1 «label 은 기존 값을 유지한다»의 기계 짝: 명시가 없으면 폴더 이동으로 label 이 재계산돼 `(label, migration)` 이력이 끊긴다)·#630(신규 파일로 떨어진 이주 산출물의 `db_table` 명시 존재 — §10.4 자신이 «보존 db_table 을 *명시*했으면 통과한다»로 이 백스톱을 지목) + check-mechanism-ownership #593 «`migrations/` 안은 사람이 직접 손대지 않는다»(기존 `0001` 이력 불변 국면) · 배제 심의(커버 근거 자리에서 제외) — 같은 검사기의 가드 문면 «기존(추적된) 모델의 db_table 은 신규가 아니므로 보지 않는다»는 비검사 선언이라 추적 모델의 db_table 개명에 미발화하고, #330(label=BC 이름)·#331(중복 금지)은 표준값 술어라 오히려 기존 label 보존과 긴장하며, #336(위치)·#337(번호 꼴)은 파일 자리·이름 꼴 술어지 보존 술어가 아니다 · «명세에 박혔는지»라는 설계 기재 축은 전건 미커버(부분 커버) · ④기본값 표 db 행 |
| 38 | s004/b7 (L35) | 누락 시 brownfield DB 위험의 blocker 판정 | Obligation | D: agent-design-review-db | ①문면 «누락이면 brownfield DB 위험이므로 blocker.» — 독립 종결절 · ④동상 |
| 39 | s004/b8 (L36–37) | 입장 표 remove/weaken 행의 영속 데이터·발행 이벤트·rollout/backfill 기대에 대한 실제 계약 종료 evidence·exact target 제시 심사 | Obligation | D: agent-design-review-db | ①심사형 술어(«제시하는가») + ④기본값 표 db 행 — 종료 evidence 판정은 명세 산출물 심사 |
| 40 | s004/b8 (L36–37) | 새 스키마 기술·현행 코드 경로 소멸만을 이유로 한 종료 승인 금지와 pending 반송 | Prohibition | D: agent-design-review-db · command-dddjango | ①문면 «…이유만으로 종료를 승인하지 않고 `pending`으로 반송한다» — 반송 처리 주체 Coordinator 병기(«pending 은 G1 blocker»와 동축) · ④기본값 표 db 행 |
| 41 | s004/b9 (L38–39) | 데이터 lens 대상 항목의 통째 누락 자체를 발견으로 상신 | Obligation | D: agent-design-review-db | ①문면 «그 누락 자체를 발견으로 올린다» + ④기본값 표 db 행 |
| 42 | s004/b9 (L38–39) | architecture-db 스킬 절 인용 근거 제시 | Obligation | D: agent-design-review-db | ④동상 — 인용 대상이 architecture-db 스킬이라 같은 lens 소유 |
| 43 | s005/b1 (L41–42) | 코드·명세 수정 금지(읽기 전용) | Prohibition | D: command-dddjango | ④절차 층 기본값 — 읽기 전용 계약 위반은 절차 위반(s001 b2 3번째 Work 와 동축 재진술 의심 · 검수표 §4) |
| 44 | s005/b2 (L43) | 도메인 경계·애그리거트의 ddd 리뷰어·계약·상태 코드·멱등성 키 정책의 api 리뷰어 이관과 데이터 집중 | Obligation | D: agent-design-review-ddd · agent-design-review-api | ①문면이 두 lens 를 소유자로 직접 지목(P-C) + ④§16 위임 기본값 표 architecture-ddd / architecture-api 행 |
| 45 | s005/b3 (L44) | 스코프 확대 권고 금지(스코프 의문은 발견으로만 상신) | Prohibition | D: command-dddjango | ④절차 층 기본값 — 스코프 승인·확대 판정은 G0/G1 소유 Coordinator · dash 뒤 절은 같은 금지의 긍정면이라 1 Work(agent-design-review-api 판정 승계) · 리뷰어 3종+discipline 4중 동형(교차 문서 유예 §3) |

## 3. 재진술 유예 (교차 문서 — spec 미기입 · T3 소급 패스 대상)

spec 의 `restates`·`restates_paths` 는 0건이다(같은 문서 안 축자 블록 쌍 0건 — §4-④).

> **좌표 규약**: `design-review-api.md`(마커 7행)·`design-architect.md`(7행)·`discipline-reviewer.md`(8행)·`commands/dddjango.md`(11행)는 마커가 삽입돼 raw 행이 센서스와 어긋난다. 아래 상대 좌표는 **마커 제거본(센서스) 번호**이며 전건 실독 확인했다. 이 문서와 `design-review-ddd.md` 는 마커 미삽입이라 환산이 없다.

| # | 이 문서 좌표 | 내용 | 상대 문서/절(센서스 행) | 관계 판정 |
|---|---|---|---|---|
| R1 | s001/b2 (L3) | description 3문(호출 대상·단일 lens 독립 리뷰·직접 수정 금지) | `agent-design-review-ddd`/s001 (L3) · `agent-design-review-api`/s001 (L3) | lens 낱말·괄호 열거만 다른 동형 3중 |
| R2 | s001/b6 (L10) | «… 관점 하나로만 독립적으로 비평하는 읽기 전용 리뷰어» | `agent-design-review-ddd`/s001 (L9) | **낱말 2개(데이터↔도메인) 빼고 축자 동일** |
| R3 | s002 전절 (L12–15) | 명세만 열람·타 리뷰어 노트/구현 코드 금지 + 스킬 본문·references 예외 | `agent-design-review-ddd`/s002 (L11–14) · `agent-design-review-api`/s003 b1 (L21) | **절 스팬 sha256 동일**(센서스 실측 `849bfc02…`) = ddd 판과 완전 축자 사본. api 판은 모드 한정어만 추가된 3중 |
| R4 | s003/b1 (L18) | 리뷰 노트만 산출 · 명세 직접 수정 금지 · 심각도 순 번호 나열 | `agent-design-review-ddd`/s003 (L17) · `agent-design-review-api`/s004 (L34) · `agent-discipline-reviewer`/s003 (L34) | lens 낱말 치환 4중 |
| R5 | s003/b2·b3 (L20–21) | 발견·권고 항목 형식 | `agent-design-review-ddd`/s003 (L19–20) · `agent-design-review-api`/s004 (L36–37) · `agent-discipline-reviewer`/s003 (L36–37) | **ddd 판과 2행 byte-축자 동일**(실측) · discipline 판은 근거 표기만 «파일:라인»으로 다름 |
| R6 | s003/b4 (L23) | 무결 시 «… 관점 이상 없음» 명시 | `agent-design-review-ddd`/s003 (L22) · `agent-design-review-api`/s004 (L39) · `agent-discipline-reviewer`/s003 (L39) | lens 낱말 치환 4중 |
| R7 | s003/b5 (L25) | 집행성 판정 1행 + 인용 없는 «가능» 무효 | `agent-design-review-ddd`/s003 (L24) · `agent-design-review-api`/s004 (L41) · `agent-discipline-reviewer`/s002 (L18 말미) | 동형 4중(P0 특이 발견 · 발주서 «리뷰어 3종+discipline 4곳 동형» 비고의 실체) |
| R8 | s004/b4 (L32) | Risky Write §9.6 Consistency Block 8행 심사 | `agent-design-architect`/s005 (L59 — «Risky Write … §9.6 Consistency Block을 *8행으로* 명세에 박는다» 작성 계약) · `architecture-db-final` §9.6(절 키 `s043-9.6` — 같은 웨이브 이관 대상) | **작성판 ↔ 심사판 병렬**(축자 사본 아님 — 술어가 «박는다» ↔ «확인한다»). 발주서 restate 열 Y 의 실체 |
| R9 | s004/b5 (L33) | 영구 테스트 입장 표 DB 후보 감사 | `agent-design-review-api`/s005 (L52) · `agent-design-architect`/s005 (L60·L73) · `agent-discipline-reviewer`/s005 (L49–52) | 병렬(감사 대상만 DB/API 로 갈림) |
| R10 | s004/b8 (L36) | 입장 표 `remove/weaken` 종료 evidence·`pending` 반송 | `agent-design-review-api`/s006 (L74) · `agent-design-architect`/s005 (L78) · `agent-discipline-reviewer`/s005 (L52) | 거울 문장(«API 기대» ↔ «영속 데이터·발행 이벤트·rollout/backfill 기대») |
| R11 | s004/b9 (L38) | 항목 통째 누락의 발견 상신 + 스킬 절 인용 | `agent-design-review-ddd`/s004 (L38) · `agent-design-review-api`/s006 (L78) | 축자 근접(«데이터 lens»/`architecture-db` ↔ «도메인 lens»/`architecture-ddd` 만 치환) |
| R12 | s004/b7 (L35) | 마이그레이션 안전(무중단 순서·rollout/backfill) | `agent-design-architect`/s005 (L59 선두 열거의 «마이그레이션 안전(rollout/backfill)» leg) | 작성 ↔ 심사 병렬 |
| R16 | s004/b1 (L29) | 스키마 설계의 정규화/역정규화 적합성 · 모델링의 도메인 반영 | `agent-design-architect`/s005 (L59 선두 열거의 «**스키마 변화**» leg) | 작성 ↔ 심사 병렬 — [adv W3-4 처분] R12 와 **같은 불릿의 다른 leg** 이라 별항으로 등재 |
| R17 | s004/b2·b3 (L30·L31) | 인덱스의 쿼리 패턴 커버·과잉/누락 · 제약·유니크·중복 방지의 DB 레벨 불변식 보장 | `agent-design-architect`/s005 (L59 선두 열거의 «**인덱스·제약**» leg) | 작성 ↔ 심사 병렬 — 한 leg 이 이 문서 두 불릿으로 갈린 1:2 분산 |
| R18 | s004/b4 (L32) 첫 문장 | 트랜잭션 경계·격리 수준·락의 정합성·동시성 적합성 심사 | `agent-design-architect`/s005 (L59 선두 열거의 «**트랜잭션 경계·격리·락 전략**(`architecture-db` §9.5·§9.6 Risky Write)» leg + 같은 불릿 말미의 엔진별 락·동시성 확정 문단) | 작성 ↔ 심사 병렬 — R8(같은 불릿의 Risky Write **8행 블록** leg)과 국면이 다르다 |
| R19 | s004/b6 (L34) | 멱등성 저장소·outbox 전달 보장의 «필요한 경우 설계됐는가» | `agent-design-architect`/s005 (L59 Risky Write 블록의 `Idempotency storage` 행 + ⚠ 스코프 가드) | **부분 병렬 — 심의 후 판정**: 멱등성 저장소 leg 만 작성↔심사 쌍이고, architect 쪽은 «미요청이면 기본 '미적용'으로 commit»(스코프 가드) 방향이라 사본이 아니라 **상보 계약**이다. `outbox 전달 보장` leg 는 architect s005 에 상대 문면이 없어 **비-재진술** — 정본 후보는 `architecture-db-final` §9.7(Commit 후 메시지 전달과 Outbox)이니 소급 패스는 스킬 문서 쪽에서 잇는다 |
| R13 | s005/b1 (L42) | 코드·명세 수정 금지(읽기 전용) | `agent-design-review-ddd`/s005 (L42 — **축자 동일**) · `agent-design-review-api`/s007 (L82) · `agent-discipline-reviewer`/s008 (L128) | 근접 4중(api 판은 «두 모드 모두», discipline 판은 «코드·테스트» 로 대상이 다름) |
| R14 | s005/b2 (L43) | 타 lens 이관과 자기 lens 집중 | `agent-design-review-ddd`/s005 (L43) · `agent-design-review-api`/s007 (L83) | **거울 3각** — 셋이 서로를 지목한다 |
| R15 | s005/b3 (L44) | 스코프 확대 권고 금지 | `agent-design-review-ddd`/s005 (L44) · `agent-design-review-api`/s007 (L84) · `agent-discipline-reviewer`/s008 (L130) | **축자 동일 4중**(실측 — 자매 문서 검수표 R15 와 같은 판정) |

**유예 총 19건**. 상대 좌표는 마커 제거 후 실독으로 확정했다.

> **[adv W3-4 처분]** 초판은 architect 데이터 lens 불릿(센서스 L59)의 병렬 legs 중 R8(Risky Write 8행)·R12(마이그레이션 안전) 둘만 등재했다. 같은 불릿 선두가 «스키마 변화, 인덱스·제약, 트랜잭션 경계·격리·락 전략, 마이그레이션 안전»을 한 줄로 열거하므로 이 문서 s004 의 b1·b2·b3·b4 첫 문장이 전부 작성↔심사 병렬인데 빠져 있었다 — R16·R17·R18 로 등재했고, 미심의였던 b6 ↔ `Idempotency storage` 행은 R19 로 심의·판정을 기록했다(부분 병렬 + outbox leg 비-재진술). 유예 목록이 소급 패스의 유일 입력이라는 형제 판례 R2-1·R2-2·api F2 의 완결성 기준을 적용한 결과다.

## 4. 경계 판단 메모

- **① (전문) 절의 프론트매터 처리**: 헤딩 라인 = `---`(도구가 `djr:headingSnapshot` 으로 가져간다). 나머지는 §13 자연 단위 — `name:`(b1) · `description:`(b2 · 규범 3) · `tools:`(b3) · `skills:` 키+2행(b4) · 닫는 `---`+빈 줄(b5) · 본문+빈 줄(b6 · 규범 1). 펜스가 없으므로 kind=code 를 쓰지 않았다(웨이브 2 판례 — 프론트매터는 행 단위 prose/norm).
- **② 블록 간 구분자 귀속**: §13 대로 빈 줄은 선행 블록의 후행 스팬(s003 b3 = L21–22 · b4 = L23–24 · b5 = L25–26), 절 선두 구분자만 첫 블록 선두(s003 b1 = L17–19). 도구의 byte 등가 단언 통과.
- **③ s003 의 문단·불릿 혼재 절**: 문단(L18)·불릿 2(L20·L21)·문단 2(L23·L25)를 각각 독립 블록으로 잘랐다 — 불릿은 부모 문장 «각 항목은 다음 형식으로 쓴다:» 의 형식 규정이지만 **각자 술어를 가진 완결 지시**(«무엇이 문제인지 + 근거 + 심각도» / «어떻게 바꾸면 되는지»)라 규범으로 채번했다(자매 문서 §1 의 같은 판정).
- **④ 같은 문서 안 재진술 판정(spec `restates` 0건)**: 두 쌍을 심의했다. ⑴ s001 b2-3(«명세나 코드를 직접 수정하지 않는다») ↔ s003 b1-2(«명세를 직접 고치지 않는다 — 반영은 architect의 몫») ↔ s005 b1(«코드·명세를 수정하지 않는다(읽기 전용)») — **동축 3각**이나 블록 사본이 아니다(프론트매터 한 줄 / 산출 문단 / 독립 불릿). ⑵ s004 b5-5(«`pending`은 G1 blocker») ↔ s004 b8-2(«`pending`으로 반송») — 같은 상태 값의 다른 국면(상신 ↔ 반송). 세 Work 의 basis 에 동축 표시를 남겨 소급 패스가 찾게 했다.
- **⑤ L32(Risky Write 불릿)를 10 Work 로 둔 근거**: 이 한 불릿이 s004 규범의 3분의 1이다. 분해는 종결절 9개 + 첫 문장의 이질 축 1 = 10이고, 각 Work 가 서로 다른 판정 국면을 진다 — ⓐ 경계·격리·락 적합성(코드 축 부분 커버 있음) ⓑ 치명성 의미 분류 ⓒ 신호≠자동 판정 ⓓ 라벨 부재 시 직접 재분류 ⓔ 8행 존재·처리 확인 ⓕ '미적용' 기재의 충족 인정 ⓖ 부재·누락의 blocker ⓗ «의미적 충족» 판정 기준 ⓘ 비치명 논증 시 불요 ⓙ 심사 범위의 구조 완전성 한정(타 소유 지목). ⓙ 만 `delegatedTo` 가 리뷰어가 아닌 `agent-discipline-reviewer`·`agent-acceptance-tester` 로 갈린다.
- **⑥ class 판정 기준**: 조건 한정·충족 인정·carveout 은 `Exception`(b4-3 신호 자동판정 부인 · b4-6 '미적용' 기재 충족 · b4-9 비치명 논증), 금지 술어는 `Prohibition`(b5-2 자동 `add` 부인 · b5-4 중앙 decision 대체 금지 · b8-2 종료 승인 금지 · s003 b5-2 무효 · s005 b1·b3), 나머지는 `Obligation`. `Permission`·`Override` 는 0건 — 이 문서에는 재량 허용문도 우선 무효화문도 없다.
- **⑦ 부분 커버 배선의 한계 표기**: `check-transaction-boundary`(코드 측 «한 트랜잭션 = 애그리거트 하나» 경계 축만 — 격리 수준·락 «선택»의 적합성 술어 0) · `check-mechanism-ownership`(#593 손편집 금지·#337 번호 꼴로 «이력 불변» 축만 — expand/contract 순서 설계 판정은 미커버) · `check-db-table`(#329 `label` 명시 의무 + #630 이주 산출물의 `db_table` 명시 존재 — 명세 «기재» 확인은 미커버). 세 자리 모두 basis 에 미커버 범위를 문장으로 적었다. **[adv W3-7 처분]** b7-3(Work #37)의 basis 는 초판이 «기존(추적된) 모델의 db_table 은 … 보지 않는다» **가드 문면**과 #330·#331·#337 을 커버 근거 자리에 두었다 — 가드는 비검사 선언이라 추적 모델의 db_table 개명에 미발화하고, #330(label=BC 이름 강제)은 오히려 기존 label 보존과 긴장하며 #337 은 파일명 꼴 술어다. 배선은 **유지**하되(«보존»에 실제로 닿는 긍정 술어가 셋 있다 — #329 는 §10.4 step 1 «label 은 기존 값을 유지한다»의 기계 짝이고, #630 은 §10.4 자신이 «보존 db_table 을 *명시*했으면 통과»로 지목한 백스톱이며, #593 은 기존 `0001` 손편집을 막는다), 가드·표준값·파일명 꼴 술어는 배제 심의로 내렸다. 이 판정은 W3-2 의 철회와 모순되지 않는다 — 거기엔 긍정 술어가 **0**이고 대상 산출물(테스트)마저 검사기 스캔 밖이었다.
