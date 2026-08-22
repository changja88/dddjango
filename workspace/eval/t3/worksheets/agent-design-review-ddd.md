# T3 저작 검수표 — agent-design-review-ddd

- 원문: `dddjango/agents/design-review-ddd.md` (현재 44행 · 발주서·센서스와 일치 — 5절 전건 스팬 해시를 `ontology_migrate.py` 가 센서스 기준선과 대조해 통과 · **마커 미삽입 원문**이라 현재 행 = 센서스 행)
- spec: `workspace/eval/t3/specs/agent-design-review-ddd.spec.json` (REF 5절 · 블록 24 · Work 37)
- 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-design-review-ddd.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)
- 실독 이행: 발주서 · `T3-authoring-brief.md` · `ontology-authoring.md` §13~§16 · `ontology_migrate.py` 선두 docstring · 파일럿 판형 2건 · **`check-*.py` 27종 docstring 전수**(묶음 공통 1회). 도메인 축 쟁점 검사기는 docstring 전문(담당 규칙 50·11·16개 목록)까지 다시 읽었다 — `check-domain-model`·`check-transaction-boundary`·`check-context-isolation`·`check-app-container`·`check-layer-skeleton`·`check-business-vocabulary`·`check-event-publish`.
- 판정 승계 출처: `workspace/eval/t3/worksheets/agent-design-review-api.md`(자매 리뷰어 문서 §0·§1·§4) · 같은 묶음의 `agent-design-review-db` 검수표(형식·계수 판별자 공유) · `workspace/eval/t3/reviews/agent-coder-findings.md`(R2-11 «4원 밖 근거 표기 금지» · R2-5 «인접 rationale 은 담당 술어가 아니다»). 이 문서에는 코드 펜스·표·체크박스가 0이라 kind 는 norm/prose 2종뿐이다.

## 0. 배선 정책 (§16 4원 종합의 이 문서 적용판)

- **P-A 절차·산출 형식 규범**(호출·입력 격리·리뷰 노트 형식·집행성 판정·«판정 없음» 갈음·무효 선언·경계) → `command-dddjango`. 근거 = §16 위임 기본값 표 «command+agents(절차 층) → Coordinator». 27종 전수 실독 — 이 갈래를 보는 검사기는 0이다.
- **P-B 심사 대상(architect 명세의 도메인 결정) 규범** → `agent-design-review-ddd`. 근거 = ①심사형 술어(«…맞는가»·«…대조한다»·«…확인한다») + ④§16 위임 기본값 표 **architecture-ddd 행의 «설계 시점 규범 → `agent-design-review-ddd`»**. s004 전량과 s003 b6-2 가 여기 든다.
- **P-C 타 소유 명시** → 문면·docstring 이 다른 역할을 판정 소유자로 지목한 자리: s003 b1-2(architect) · s004 b3-2(discipline-reviewer — **검사기 docstring 이 «판정-소유 형태(빈혈) 같은 «의미» 변종은 범위 밖(discipline-reviewer 몫)»이라 명시 이양**) · s005 b2(api·db 리뷰어).
- **P-D 기계 절반 + 의미 잔여** — 이 문서는 세 리뷰어 중 `enforcedBy` 가 가장 많이 서는 판이다(9 Work). 이유는 §16 «역도 성립»이다: `check-app-container` docstring 이 **이 문서와 같은 조문(`architecture-ddd` §3.2 «판정 소유→구조 이주» 항-(2) 2026-06-08 개정)을 이름으로 인용**하고, `check-context-isolation` 이 문면이 인용한 §2.5 축(#12·#13)을 그대로 집행하며, `check-domain-model`·`check-transaction-boundary` 가 빈혈·경계의 코드 형태를 문다. 이런 자리에서 기본값으로 도피하면 오배선이므로 병기하고 미커버 범위를 basis 에 적었다.
  - **경계선 기준 ⑴ — «절제 선언 ≠ 커버»**: docstring 이 «나는 이 축을 보지 않는다/적용하지 않는다»고 선언한 문장은 근거가 아니다. 병기가 서려면 위반 표면에 닿는 **긍정 술어**가 있어야 한다(같은 묶음 acceptance-tester 판 W3-2 처분과 같은 선).
  - **경계선 기준 ⑵ — 한 검사기의 복수 규범 병기**: 두 규범이 **같은 기계 축**을 공유하면 같은 검사기가 양쪽에 서도 이중 계상이 아니다(b3-2 항-(1)·b3-3 항-(2)는 «위치»라는 한 축을 공유한다). api F5 가 벌한 이중 계상은 **축이 어긋난** 병기이지 축을 공유한 병기가 아니다. 반대로 §16 «역도 성립»(docstring 이 조문을 이름으로 인용)은 **인용된 그 조문의 Work 에서만** 근거가 된다 — b3-3 이 그 자리다.
  - **경계선 기준 ⑶ — 간접 커버의 한계 표기 의무**: 검사기 술어가 규범 술어와 «인접»할 뿐이면(예: b5 의 «일관 사용» ↔ #628 «정의 단일 출처») 병기하되 basis 에 **«그 축 자체의 술어는 0»** 을 명기한다. 명기 없는 인접 병기는 과장 basis(형제 판례 R2-4·R2-6)다.
- **enforcedBy 절제(과잉 배선 방지)** — 심의하고 **배제한** 자리:
  - `check-event-publish`(s004 b7 «도메인 이벤트 채택 여부 판단») — 담당 16규칙이 전부 «사실은 과거형·표면은 `published_event/` 하나·구독은 껍데기»의 구조·명명 축이고 «채택할 것인가»의 판단 술어가 0.
  - `check-domain-model`(s004 b4 «상태 전이가 도메인 규칙과 맞는가») — #257 은 상태 변경의 **루트 경유 형태**만 보고 전이 «내용»의 도메인 적합성 술어가 없다. 형태 축은 이미 b1-2·b2-1 에 정배선돼 있어 여기 병기하면 이중 계상이다.
  - `check-context-isolation`(s004 b6-1 «컨텍스트 경계가 적절한가») — 이미 그어진 경계의 침범만 보고 «경계 선택의 적절성» 술어가 0. 같은 검사기를 자기 축 규범(b6-2 ACL/OHS 한정)에만 뒀다.
  - `check-composition-root`·`check-usecase-dto-placement` — 구조 축 인접 후보였으나 이 문서의 어느 규범도 DI 배선·DTO 배치를 심사 대상으로 삼지 않는다.
- 무소유 0건(도구가 단언).

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

**채번 판별자(1차)**: Work 단위 = 종결절(문장). 한 문장 안이라도 ⑴ 심사 대상이 갈리거나 ⑵ 소유자(배선)가 갈리면 분리하고, ⓐ 같은 축의 긍정·부정면(«도메인에 배정됐는가 — 인프라에 두지 않았는가») ⓑ dash 뒤 rationale ⓒ 술어 없는 출처 표기(«근거 `architecture-ddd` §3.2·§3.6.»)·역할 선언은 병합·무규범으로 둔다.

| 절 | 헤딩 | 발주서 | spec | 차 | 사유·판정 |
|---|---|---|---|---|---|
| s001 | (전문) | 4 | 4 | 0 | 조성 일치 — description 3문 + 본문 L9 3문 중 규범 1문(1문째 역할 선언·3문째 근거 서술은 무규범). adv 중재 정정(norm 2→4) 반영값과 동수 |
| s002 | 입력 | 2 | 2 | 0 | 조성 일치 — `agent-design-review-db`/s002 와 **절 스팬 해시가 같은** 완전 축자 사본이라 그 판정과 동일하게 2 Work(1문째는 입력 사실 서술) |
| s003 | 산출 | 9 | 12 | +3 | census 9 = L17 3 + L22 1 + L24 2 + L26 3 (**발견/권고 불릿 미계수**). 초과 3건 전액: ⓐ·ⓑ 두 불릿(동형 4중의 다른 판이 각 1 Work 로 채번된 선례 대칭) +2 ⓒ L26 첫 문장의 이질 축 분리(대조 표 «작성» ↔ 응용·인프라 잔류 판정의 «blocker 상신» — 후자에만 코드 측 검사기 커버가 붙는다) +1 → **census 과소** |
| s004 | 점검 항목 (도메인 lens만) | 13 | 16 | +3 | 독립 재계수한 종결절 수는 12(L30 1·L31 2·L32 2·L33 1·L34 1·L35 2·L36 1·L38 2)로 census 13 보다 1 적다 — census 는 L31 말미의 «근거 `architecture-ddd` §3.2·§3.6.» 조각이나 L32 의 dash 절 하나를 문장으로 센 것으로 보인다(이 spec 은 술어 없는 출처 표기를 무규범으로 둔다). spec 16 은 판별자 ⑴ 적용 결과이고 내역은: ⓐ L30 두 심사 대상 분리(애그리거트 경계 ↔ 불변식 보장 위치) +1 ⓑ L32 의 세 요구 분리(«값»의 §3.2 소유 지시 / 항-(1) 평면 모델 잔류 대조 / 항-(2) 데이터소스 면제 범위 대조) +2 ⓒ L33 분리(전이 적합성 ↔ 누락 규칙·엣지) +1 → **census 과소**(하한 대비 +4, 발주서 값 대비 +3) |
| s005 | 경계 | 3 | 3 | 0 | 조성 일치 — 불릿 3개 ↔ 3 Work. L44 의 dash 뒤 절은 같은 금지의 긍정면이라 1 Work(자매 문서 판정 승계) |
| **합계** | | **31** | **37** | **+6** | 과대 산정 0건 판정. spec < census 인 절이 0이라 **누락 위험 지점 없음** |

## 2. 배선 근거 표 (전 규범 37건)

표기: `E:` = enforcedBy · `D:` = delegatedTo. 근거의 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N·위임 기본값 표 는 §16 4원. **이 표는 spec JSON 에서 기계 생성했다**(표 37행 ↔ spec 37 norm 순서·값 일치 — 수리 시 재생성 의무).

| # | 절/블록 | Work label | 유형 | 배선 | 4원 근거 |
|---|---|---|---|---|---|
| 1 | s001/b2 (L3) | Phase 1 설계 단계의 Coordinator 호출 대상 | Obligation | D: command-dddjango | ①문면 — 프론트매터 description 이 Coordinator 라우팅 트리거 · ④§16 위임 기본값 표(command+agents 절차 층→Coordinator) · ②check-*.py 27종 docstring 선두 전수 실독 — 에이전트 호출·라우팅 술어 0 |
| 2 | s001/b2 (L3) | architect 설계 명세의 도메인 관점(애그리거트 경계·불변식·도메인 이벤트) 단일 lens 독립 리뷰와 리뷰 노트 산출 | Obligation | D: command-dddjango | ①문면 «…도메인 관점으로만 독립 리뷰하고 리뷰 노트를 낸다» · ④절차 층 기본값 — lens 수행 여부 판정 주체는 리뷰 노트를 수납하는 Coordinator(리뷰어 3종 동형 배선) |
| 3 | s001/b2 (L3) | 명세·코드 직접 수정 금지 | Prohibition | D: command-dddjango | ④절차 층 기본값 — 읽기 전용 계약 위반은 절차 위반이고 코드 산출물 대상 검사기 27종의 관할 밖(s005 b1 과 동축 — 검수표 §4 재진술 의심) |
| 4 | s001/b6 (L9–10) | 도메인 관점 단일 lens 의 읽기 전용 독립 비평 수행 | Obligation | D: command-dddjango | ①문면 «*도메인 관점 하나로만* 독립적으로 비평하는 읽기 전용 리뷰어다» · ④절차 층 기본값 — 첫 문장은 역할 선언 서술, 셋째 문장은 근거 서술이라 무규범(agent-design-review-api/s001 판정 승계) |
| 5 | s002/b1 (L12–14) | 명세 한정 열람 — 타 리뷰어 노트·구현 코드 열람 금지(편향 방지) | Prohibition | D: command-dddjango | ④절차 층 기본값 — 입력 묶음 공급·독립성 보장 주체가 Coordinator · ②27종 전수 실독 — 리뷰 입력 격리를 보는 검사기 0(agent-design-review-db/s002 와 **절 스팬 해시 동일**한 축자 사본 — 교차 문서라 restates 유예 §3) |
| 6 | s002/b1 (L12–14) | 로드한 스킬 본문·references 참조의 제한 밖 인정 | Exception | D: command-dddjango | ①문면이 제한 대상을 «타 리뷰어의 노트·구현 코드»로 자기 한정 · ④동상 |
| 7 | s003/b1 (L16–18) | 도메인 리뷰 노트 한정 산출 | Obligation | D: command-dddjango | ④절차 층 기본값 — 산출물 종류 계약(리뷰어 3종 동형)이고 수납 주체가 Coordinator |
| 8 | s003/b1 (L16–18) | 명세 직접 수정 금지(반영은 architect 소유) | Prohibition | D: command-dddjango · agent-design-architect | ①문면 «반영은 architect의 몫» — 판정 소유 배분 지목(P-C) · ④절차 층 기본값 · s001 b2 3번째 Work 와 동축(재진술 의심 — 검수표 §4) |
| 9 | s003/b1 (L16–18) | 발견 다수 시 심각도 순(blocker→important→nit) 번호 나열 | Obligation | D: command-dddjango | ④절차 층 기본값 — 리포트 형식 계약(리뷰어 3종+discipline 4중 동형) |
| 10 | s003/b2 (L19) | 발견 항목 형식(문제+근거 위치 인용+심각도 3단계) | Obligation | D: command-dddjango | ④절차 층 기본값 — 산출 형식 계약(agent-design-review-api/s004 b2 의 같은 불릿 1 Work 채번 선례 승계) |
| 11 | s003/b3 (L20–21) | 권고 항목 형식(변경 방법 제시) | Obligation | D: command-dddjango | ④동상 — 동형 4중 |
| 12 | s003/b4 (L22–23) | 무결 시 «도메인 관점 이상 없음» 명시 | Obligation | D: command-dddjango | ④절차 층 기본값 — 무발견 보고의 명시 계약(침묵과 무결의 구분이 게이트 판정 재료) · b6 의 «대조 표 없는 이상 없음 무효»가 이 선언의 성립 조건을 좁힌다 |
| 13 | s003/b5 (L24–25) | 집행성 판정 1행 기재(가능=명세 확정 결정 3곳 인용·불가=막히는 절·문장 지목) | Obligation | D: command-dddjango | ④절차 층 기본값 — 리포트 형식 계약이고 판정 수납자가 Coordinator(리뷰어 3종+discipline 4중 동형) · ②27종에 집행성 술어 0 |
| 14 | s003/b5 (L24–25) | 인용 없는 «집행 가능» 판정 무효 | Prohibition | D: command-dddjango | ④절차 층 기본값 — 무효 선언의 판정자는 판정을 수납·집행하는 Coordinator |
| 15 | s003/b6 (L26–27) | 판정-소유 대조 표 기재(명세의 비즈니스 판정·불변식마다 «판정 → 배정 위치(애그리거트·도메인 서비스 메서드)» 1행 대조) | Obligation | D: command-dddjango · agent-design-review-ddd | ④절차 층 기본값(산출 형식 수납 주체) + §16 기본값 표 architecture-ddd 설계 시점 행 — 대조 «행위» 자체는 도메인 lens 심사 · ①문면이 기준을 architecture-ddd references §3.6 원문으로 지정 · command-dddjango/s006 구문검사와는 계약 쌍(사본 아님 — 검수표 §3) |
| 16 | s003/b6 (L26–27) | 응용 서비스·인프라 경로 잔류 판정 행의 blocker 상신 | Obligation | E: check-domain-model.py · check-transaction-boundary.py / D: agent-design-review-ddd | ②check-domain-model #257 «상태 변경은 루트를 지난다 — 확정: 응용·입구의 «속성 접근 후 메서드 호출»» + check-transaction-boundary #195 «상태를 바꾸는 유스케이스는 애그리거트를 건너뛰지 않는다» — 판정이 응용·인프라에 남은 «코드 형태»를 결정적으로 집행하는 부분 커버(설계 단계 대조 표 판정은 미커버) · ①문면 «그 행을 blocker로 올린다» · ④기본값 표 ddd 행 · 앞 절과 행위 대상(표 작성 ↔ blocker 판정)이 갈려 분리 채번 |
| 17 | s003/b6 (L26–27) | 비즈니스 판정·불변식 0건 시 «판정 없음» 1행 갈음(빈 표 반송 방지) | Exception | D: command-dddjango | ①문면 «표 대신 «판정 없음» 1행으로 갈음한다(빈 표 반송 방지)» 조건 한정 · ④절차 층 기본값(반송 판정 소유) |
| 18 | s003/b6 (L26–27) | 대조 표(또는 «판정 없음» 1행) 없는 «도메인 관점 이상 없음» 무효 | Prohibition | D: command-dddjango | ④절차 층 기본값 — 무효 선언의 판정자는 산출을 수납하는 Coordinator(b4 의 무결 보고 계약과 쌍) |
| 19 | s004/b1 (L29–30) | 애그리거트 경계의 일관성 단위 적합성 점검 | Obligation | E: check-domain-model.py / D: agent-design-review-ddd | ②docstring #249 «domain_layer 자식 = 애그리거트들 + shared_value_object + domain_service»·#256 «애그리거트 폴더엔 폴더와 같은 이름의 <aggregate>.py + 루트 클래스»·#299 애그리거트 꼴 — 경계의 «형태»를 결정적으로 집행하는 부분 커버(경계 «선택»이 일관성 단위로 옳은가는 미커버) · ①심사형 술어 + ④§16 기본값 표 architecture-ddd 설계 시점 행 |
| 20 | s004/b1 (L29–30) | 불변식의 애그리거트 내부 보장 점검 | Obligation | E: check-domain-model.py / D: agent-design-review-ddd | ②#257 상태 변경의 루트 경유·#264 «값 객체 불변 — __init__/__post_init__ 밖 self 대입 금지»·#289/#290 불변식 예외의 exception/ 폴더 — 불변식 «자리» 축 집행(부분 커버: 불변식 내용의 충분성은 미커버) · ④동상 · 한 문장 안 두 심사 대상(경계 ↔ 불변식)이라 분리 채번 |
| 21 | s004/b2 (L31) | 각 비즈니스 판정·불변식의 도메인 애그리거트·도메인 서비스 메서드 배정과 응용 서비스 프로덕션 경로 실행 명세 확인(인프라 배치 부재 포함) | Obligation | E: check-domain-model.py · check-transaction-boundary.py / D: agent-design-review-ddd | ②#257(응용·입구의 속성 접근 후 메서드 호출 = 확정 위반)·#304 «도메인 서비스는 리포지토리를 받지도 부르지도 않는다» + transaction-boundary #195·#287 «쓰기 인자는 애그리거트다 — update_* 필드 갱신·조건/필드 인자면 위반» — 빈혈·조건부 UPDATE 누수의 코드 측 축 집행(부분 커버: 명세 단계 배정 확인은 미커버) · ①문면이 근거로 architecture-ddd §3.2·§3.6 지목 · ④기본값 표 ddd 행 · 긍정면(도메인 배정)과 부정면(인프라 배치 금지)은 같은 축이라 1 Work |
| 22 | s004/b2 (L31) | 경합 시나리오의 경합 가드(version/CAS)와 비즈니스 판정 실행 지점 분리 기재 확인 | Obligation | E: check-transaction-boundary.py / D: agent-design-review-ddd | ②#599 «save_all() 조건 셋 — ㉡맨 bulk_update(경합 가드 없음)면 위반» — 경합 가드 부재의 한 형태만 집행하는 부분 커버(조건부 UPDATE 누수 일반·명세 기재 축은 미커버) · ④기본값 표 ddd 행 |
| 23 | s004/b3 (L32) | 판정·불변식 이주와 데이터소스 골격 실현 «값»의 architecture-ddd references §3.2 항-(1)·항-(2) 소유 | Obligation | D: agent-design-review-ddd | ①문면이 값 정본을 §3.2 항-(1)·항-(2)로 지정 · ②check-app-container docstring 이 같은 항을 인용(«`architecture-ddd` §3.2 «판정 소유→구조 이주» 항-(2) 2026-06-08 개정») — 다만 «값의 소유처 지시» 자체는 기계 집행 대상이 아니라 미배선 · ④§16 기본값 표 ddd 행 |
| 24 | s004/b3 (L32) | 평면 모델 위 판정 잔류 금지(항-(1)) 대조 | Obligation | E: check-app-container.py / D: agent-design-review-ddd · agent-discipline-reviewer | ②check-app-container docstring 의 긍정 선언 «이 좁은 결정적 그물이 «위치» 한 축을 모델 무관하게 집행한다» + 회귀 표본 «smoke4·smoke6: 기존 `catalog/` 가 루트 평면 + 새 마이그레이션/판정 적재인데 `application/` 로 이주 안 함» — 이 규범의 주술어(판정을 얹는 코드가 평면에 «남는다»)와 같은 위치 축을 결정적으로 집행하는 부분 커버 · 한계 ⑴ G2(신규 디렉터리이거나 `D/migrations/` 아래 신규 마이그레이션)가 없으면 «판정 메서드만 얹은» 국면엔 미발화 ⑵ 같은 docstring 이 판정-소유 «형태»(빈혈) 의미 변종을 범위 밖(discipline-reviewer 몫)으로 명시 이양하므로 그 잔여를 ⓓ 로 병기 ⑶ 명세 대조 축(설계 단계)은 전건 미커버 · §16 «역도 성립»(docstring 이 §3.2 항-(2)를 이름으로 인용)은 이 Work 가 아니라 같은 블록 항-(2) Work 에서 서므로 여기 근거로 쓰지 않는다 — 두 Work 가 같은 검사기를 공유하는 것은 항-(1)·항-(2)가 «위치»라는 한 기계 축을 공유하기 때문이고, 축이 어긋난 병기를 벌한 api F5 의 이중 계상과는 형이 다르다(경계선 기준 검수표 §0 P-D) · ④기본값 표 ddd 행 + ⓓ |
| 25 | s004/b3 (L32) | 데이터소스 사유의 위치·4계층·빈 애그리거트 골격 실현 면제 금지(항-(2) — 실내용 면제는 판정 .py 코드 한정·깊이 면제 폐지) | Obligation | E: check-app-container.py · check-layer-skeleton.py / D: agent-design-review-ddd | ②check-app-container «데이터소스 면제는 *판정 실내용(.py)* 에 한정하고 위치·4계층·애그리거트 골격은 무조건이다; 이 스크립트는 그중 *위치* 한 축만 본다» + check-layer-skeleton #486 «어느 BC 를 열어도 골격이 그대로»·#488 고정 칸 필수·#490 트리 밖 경로 위반 — 위치·골격 두 축을 결정적으로 집행 · ①문면이 houserules final.md §0·§1 을 칸의 값 정본으로 인용 · ④기본값 표 ddd 행 |
| 26 | s004/b3 (L32) | 판정 기준의 «판정·불변식 소유» 고정(«레거시냐»가 기준 아님) | Obligation | D: agent-design-review-ddd | ①문면 «기준은 "레거시냐"가 아니라 "판정·불변식 소유냐"다» — 독립 종결절의 판정 기준 규정 · ②검사 공백(레거시 여부는 코드 형태에 안 나타남) · ④기본값 표 ddd 행 |
| 27 | s004/b4 (L33) | 상태 전이의 도메인 규칙 적합성 점검 | Obligation | D: agent-design-review-ddd | ①심사형 술어(«맞는가») + ④기본값 표 ddd 행 · ②27종 전수 — 상태 전이 «내용» 판정 술어 0(check-domain-model 은 루트 경유 «형태»만 본다) |
| 28 | s004/b4 (L33) | 누락 규칙·엣지 부재 점검 | Obligation | D: agent-design-review-ddd | ④동상 — 규칙 완결성 판정은 의미 레인(검사 공백) · 한 문장 안 두 심사 대상(전이 적합성 ↔ 누락)이라 분리 채번 |
| 29 | s004/b5 (L34) | 유비쿼터스 언어의 명세 전반 일관 사용 점검 | Obligation | E: check-business-vocabulary.py / D: agent-design-review-ddd | ②docstring «업무 어휘·framework 격리 검사기 — «이 낱말의 뜻을 누가 정하나»(D24·D38·D47) … 업무 어휘의 정의(#628)는 business_vocab.py(공유 데이터 모듈)가 진다» — 코드 측 어휘 소유·격리 축 집행 · 한계(경계선 사례): «같은 낱말이 같은 뜻으로 쓰였는가»라는 **일관성 자체의 술어는 27종에 0**이고, 여기서 인정하는 것은 #628 단일 출처 강제가 코드에서 뜻의 분기를 원천 차단하는 **간접 커버** 하나뿐이다(#47·#52 의 framework 격리는 이 규범의 축이 아니라 배제) · 명세 문면의 어휘 «일관» 사용 판정은 전건 미커버 — 존치 판단의 경계선 기준은 검수표 §0 P-D · ④기본값 표 ddd 행 |
| 30 | s004/b6 (L35) | 컨텍스트 경계 적절성 점검 | Obligation | D: agent-design-review-ddd | ①심사형 술어 + ④기본값 표 ddd 행 · ②경계 «선택»의 적절성 판정 술어는 27종에 0(check-context-isolation 은 이미 그어진 경계의 침범만 본다) |
| 31 | s004/b6 (L35) | 컨텍스트 간 접근의 ACL/open_host_service 한정 명세 확인(타 컨텍스트 domain_layer/driven_layer 직접 import 금지) | Obligation | E: check-context-isolation.py / D: agent-design-review-ddd | ②docstring 타 BC 군 «#12 부를 수 있는 것은 OHS·published_event 둘 · #13 OHS 소비는 ACL 뿐» — 문면이 인용한 architecture-ddd §2.5 축을 코드에서 결정적으로 집행 · 명세 «기재» 확인 축은 미커버(부분 커버) · ④기본값 표 ddd 행 |
| 32 | s004/b7 (L36–37) | 도메인 이벤트 채택 여부 판단(과채택/누락) 타당성 점검 | Obligation | D: agent-design-review-ddd | ④기본값 표 ddd 행 · ②배제 심의 — check-event-publish 는 «사실은 과거형이고, 표면은 published_event/ 하나이고, 구독은 껍데기다»라는 구조·명명 축이라 «채택할 것인가»의 판단 술어가 0(전수 실독) |
| 33 | s004/b8 (L38–39) | 도메인 lens 대상 항목의 통째 누락 자체를 발견으로 상신 | Obligation | D: agent-design-review-ddd | ①문면 «그 누락 자체를 발견으로 올린다» + ④기본값 표 ddd 행 |
| 34 | s004/b8 (L38–39) | architecture-ddd 스킬 절 인용 근거 제시 | Obligation | D: agent-design-review-ddd | ④동상 — 인용 대상이 architecture-ddd 스킬이라 같은 lens 소유 |
| 35 | s005/b1 (L41–42) | 코드·명세 수정 금지(읽기 전용) | Prohibition | D: command-dddjango | ④절차 층 기본값 — 읽기 전용 계약 위반은 절차 위반(s001 b2 3번째 Work 와 동축 재진술 의심 · 검수표 §4) |
| 36 | s005/b2 (L43) | 계약(상태코드·멱등성)·데이터(인덱스·트랜잭션) 관심사의 api/db 리뷰어 이관과 도메인 집중 | Obligation | D: agent-design-review-api · agent-design-review-db | ①문면이 두 lens 를 소유자로 직접 지목(P-C) + ④§16 위임 기본값 표 architecture-api / architecture-db 행 · agent-design-review-db/s005 와 서로를 지목하는 거울 문장(교차 문서 유예 §3) |
| 37 | s005/b3 (L44) | 스코프 확대 권고 금지(스코프 의문은 발견으로만 상신) | Prohibition | D: command-dddjango | ④절차 층 기본값 — 스코프 승인·확대 판정은 G0/G1 소유 Coordinator · dash 뒤 절은 같은 금지의 긍정면이라 1 Work(agent-design-review-api 판정 승계) · 축자 동일 4중(교차 문서 유예 §3) |

## 3. 재진술 유예 (교차 문서 — spec 미기입 · T3 소급 패스 대상)

spec 의 `restates`·`restates_paths` 는 0건이다(같은 문서 안 축자 블록 쌍 0건 — §4-④).

> **좌표 규약**: `design-architect.md`(마커 7행)·`design-review-api.md`(7행)·`discipline-reviewer.md`(8행)·`commands/dddjango.md`(11행)는 마커가 삽입돼 raw 행이 센서스와 어긋난다. 아래 상대 좌표는 **마커 제거본(센서스) 번호**이며 전건 실독 확인했다. 기이관 스킬 문서(`architecture-ddd-final`)는 절 키로 지시한다.

| # | 이 문서 좌표 | 내용 | 상대 문서/절(센서스 행) | 관계 판정 |
|---|---|---|---|---|
| R1 | s001/b2 (L3) | description 3문 | `agent-design-review-db`/s001 (L3) · `agent-design-review-api`/s001 (L3) | lens 낱말·괄호 열거만 다른 동형 3중 |
| R2 | s001/b6 (L9) | «… 관점 하나로만 독립적으로 비평하는 읽기 전용 리뷰어» | `agent-design-review-db`/s001 (L10) | **낱말 2개 빼고 축자 동일** |
| R3 | s002 전절 (L11–14) | 명세만 열람 + 스킬 본문·references 예외 | `agent-design-review-db`/s002 (L12–15) · `agent-design-review-api`/s003 b1 (L21) | **절 스팬 sha256 동일**(`849bfc02…`) = db 판과 완전 축자 사본 · api 판은 모드 한정어 추가 |
| R4 | s003/b1 (L17) | 리뷰 노트만 · 명세 수정 금지 · 심각도 순 나열 | `agent-design-review-db`/s003 (L18) · `agent-design-review-api`/s004 (L34) · `agent-discipline-reviewer`/s003 (L34) | lens 낱말 치환 4중 |
| R5 | s003/b2·b3 (L19–20) | 발견·권고 항목 형식 | `agent-design-review-db`/s003 (L20–21) · `agent-design-review-api`/s004 (L36–37) · `agent-discipline-reviewer`/s003 (L36–37) | **db 판과 2행 byte-축자 동일**(실측) |
| R6 | s003/b4 (L22) | 무결 시 «… 관점 이상 없음» | `agent-design-review-db`/s003 (L23) · `agent-design-review-api`/s004 (L39) · `agent-discipline-reviewer`/s003 (L39) | lens 낱말 치환 4중 |
| R7 | s003/b5 (L24) | 집행성 판정 1행 + 인용 없는 «가능» 무효 | `agent-design-review-db`/s003 (L25) · `agent-design-review-api`/s004 (L41) · `agent-discipline-reviewer`/s002 (L18 말미) | 동형 4중(발주서 «집행성 판정 동형» 비고의 실체) |
| R8 | s003/b6 (L26) | 판정-소유 대조 표 | `command-dddjango`/s006 (L78 — 리뷰어 병렬 호출 절의 대조 표 요구·구문검사) | **계약 쌍(사본 아님)** — 발주서 비고 그대로. 소급 패스에서 `restates` 대신 참조 관계로 처분할 자리 |
| R9 | s004/b2 (L31) | 판정 소유(빈혈 차단) — 도메인 배정·인프라 배치 금지·경합 가드 분리 | `agent-design-architect`/s005 (**L59** 데이터 lens 항 말미 — «`WHERE`엔 경합 가드만 담고 비즈니스 판정(예: `stock>=qty`)은 인프라로 옮기지 않는다 — 판정·불변식은 도메인 애그리거트(또는 도메인 서비스)가 소유하고 프로덕션 경로에서 실행 … repo는 결과만 저장(판정을 SQL·ORM으로 복제하면 빈혈)») · `agent-discipline-reviewer`/s007 (L76 «죽은 도메인 메서드·판정 인프라 누수(빈혈)») · `architecture-ddd-final` §3.2·§3.6(s017-3.2·s023-3.6 — 정본) | 설계 시점 ↔ 구현 시점 병렬(사본 아님) + 값 정본 참조. [adv W3-5 처분] architect leg 추가 — 이 문서 b2 의 세 요구(도메인/도메인서비스 배정 · 인프라 배치 금지 · 경합 가드↔판정 지점 분리)가 architect 문면과 **구문 수준 거울**인데 초판이 빠뜨렸다 |
| R10 | s004/b3 (L32) | 판정 소유 → 구조 이주(항-(1)·항-(2)) | `agent-design-architect`/s005 (L64 «판정 소유 → 구조 배치» 작성판) · `agent-discipline-reviewer`/s007 (L76) · `architecture-ddd-final` §3.2(s017-3.2 — **기이관 정본**) · `discipline-houserules` final §0·§1(칸의 값 정본) | 작성판 ↔ 심사판 ↔ 감수판 3중 병렬 + 값 정본 참조. 발주서 비고 «architect s005·discipline s007과 병렬» 확인 |
| R11 | s004/b6 (L35) | 컨텍스트 간 접근의 ACL/OHS 한정 | `architecture-ddd-final` §2.5(s011-2.5 — 정본) · `agent-design-architect`/s005 | 값 정본 참조(문면이 §2.5 를 직접 인용) |
| R12 | s004/b8 (L38) | 항목 통째 누락의 발견 상신 + 스킬 절 인용 | `agent-design-review-db`/s004 (L38) · `agent-design-review-api`/s006 (L78) | 축자 근접(lens·스킬명만 치환) |
| R13 | s005/b1 (L42) | 코드·명세 수정 금지(읽기 전용) | `agent-design-review-db`/s005 (L42 — **축자 동일**) · `agent-design-review-api`/s007 (L82) · `agent-discipline-reviewer`/s008 (L128) | 근접 4중 |
| R14 | s005/b2 (L43) | 타 lens 이관과 도메인 집중 | `agent-design-review-db`/s005 (L43) · `agent-design-review-api`/s007 (L83) | **거울 3각** — 셋이 서로를 지목 |
| R15 | s005/b3 (L44) | 스코프 확대 권고 금지 | `agent-design-review-db`/s005 (L44) · `agent-design-review-api`/s007 (L84) · `agent-discipline-reviewer`/s008 (L130) | **축자 동일 4중**(실측) |
| R16 | s004/b1 (L30) | 애그리거트 경계·불변식 심사 | `agent-design-architect`/s005 (L56 도메인 lens 항의 «**애그리거트 경계와 불변식**» leg) | 작성 ↔ 심사 병렬 |
| R17 | s004/b4 (L33) | 상태 전이의 도메인 규칙 적합성·누락 규칙/엣지 점검 | `agent-design-architect`/s005 (L56 도메인 lens 항의 «**상태 전이**» leg) | 작성 ↔ 심사 병렬 — [adv W3-5 처분] R16 과 **같은 불릿의 다른 leg** |
| R18 | s004/b5 (L34) | 유비쿼터스 언어의 명세 전반 일관 사용 점검 | `agent-design-architect`/s005 (L56 도메인 lens 항의 «**유비쿼터스 언어**» leg) | 작성 ↔ 심사 병렬 |
| R19 | s004/b7 (L36) | 도메인 이벤트 채택 여부 판단(과채택/누락) 타당성 점검 | `agent-design-architect`/s005 (L56 도메인 lens 항의 «**관련 도메인 이벤트 채택 여부와 근거**» leg) | 작성 ↔ 심사 병렬 — architect 는 «근거와 함께 결정», 이 문서는 «그 판단이 타당한가» |

**유예 총 19건**. 상대 좌표는 마커 제거 후 실독으로 확정했다.

> **[adv W3-5 처분]** 초판은 architect 도메인 lens 불릿(센서스 L56)의 네 legs 중 b1 하나만 R16 으로 짝지었다. 그 한 줄이 «애그리거트 경계와 불변식, 상태 전이, 유비쿼터스 언어, 관련 도메인 이벤트 채택 여부와 근거»를 열거하므로 b4·b5·b7 도 같은 작성↔심사 병렬이다 — R17·R18·R19 로 등재했다. 함께 지적된 R9 의 architect leg 누락(데이터 lens 항 L59 의 판정 소유 문구 ↔ b2)도 R9 행에 병기했다. 근거는 형제 판례 R2-2(병렬 쌍 추가 누락)·api F2(architect 병기 비대칭)의 완결성 기준이고, 유예 목록이 소급 패스의 유일 입력이라는 점이다.

## 4. 경계 판단 메모

- **① (전문) 절의 프론트매터 처리**: 헤딩 라인 = `---`. 블록은 `name:`(b1) · `description:`(b2 · 규범 3) · `tools:`(b3) · `skills:` 키+1행(b4) · 닫는 `---`+빈 줄(b5) · 본문+빈 줄(b6 · 규범 1). 펜스가 없어 kind=code 미사용(웨이브 2 판례).
- **② 블록 간 구분자 귀속**: §13 대로 빈 줄은 선행 블록 후행 스팬(s003 b3 = L20–21 · b6 = L26–27), 절 선두 구분자만 첫 블록 선두(s003 b1 = L16–18). byte 등가 기계 확인.
- **③ s003 의 6블록 분해**: 문단(L17) · 불릿 2(L19·L20) · 문단 3(L22 «이상 없음» · L24 집행성 판정 · L26 판정-소유 대조 표). 마지막 문단은 **이 문서에만 있는 조항**(자매 리뷰어 2종에 없음)이라 census restate 열이 N 인 것과 정합한다.
- **④ 같은 문서 안 재진술 판정(spec `restates` 0건)**: 세 쌍 심의. ⑴ s001 b2-3 ↔ s003 b1-2 ↔ s005 b1 «수정 금지» 동축 3각 — 블록 사본 아님(프론트매터 한 줄 / 산출 문단 / 독립 불릿). ⑵ s003 b4(«도메인 관점 이상 없음» 명시) ↔ s003 b6-4(«대조 표 없는 «도메인 관점 이상 없음»은 무효») — **성립 조건을 좁히는 관계**라 사본이 아니라 한정 쌍이고, 두 Work 의 basis 에 서로를 가리키는 표시를 남겼다. ⑶ s004 b2(판정 소유) ↔ s004 b3(판정 소유 → 구조 이주) — 같은 §3.2 계열이나 대상이 «판정의 자리» ↔ «코드의 자리»로 갈린다.
- **⑤ L32 를 4 Work 로 둔 근거**: 이 불릿은 «값의 소유처 지시»(정본 위임) + «항-(1) 대조» + «항-(2) 대조» + «판정 기준 고정»의 네 층이고, 셋째 층에만 두 검사기(`check-app-container`·`check-layer-skeleton`)의 결정적 커버가 붙는다 — 한 Work 로 접으면 부분 커버 표기가 «전체를 집행한다»는 과장이 된다(형제 문서 적대 리뷰 R2-4·R2-6 이 벌한 형태). 반대로 첫 층(값 소유 지시)은 기계 집행 대상이 아니라 `enforcedBy` 를 비웠다.
- **⑥ class 판정 기준**: 조건 한정·갈음은 `Exception`(s002 b1-2 스킬 참조 예외 · s003 b6-3 «판정 없음» 갈음), 금지 술어는 `Prohibition`(s003 b5-2·b6-4 무효 · s001 b2-3 · s005 b1·b3), 나머지는 `Obligation`. `Permission`·`Override` 는 0건.
- **⑦ 부분 커버 배선의 한계 표기**: 9건의 `enforcedBy` 전부에 미커버 범위를 적었다 — `check-domain-model`(경계·불변식의 «형태»만 · 선택의 타당성 미커버) · `check-transaction-boundary`(#195·#287 쓰기 인자 축 · #599 ㉡ 경합 가드 한 형태만) · `check-app-container`(위치 한 축 · G2 미성립 국면 미발화 · 의미 변종은 docstring 이 discipline-reviewer 로 이양) · `check-layer-skeleton`(#486·#488·#490 골격 축) · `check-business-vocabulary`(#628 정의 단일 출처의 **간접** 커버 하나 · 일관성 자체의 술어 0 · 명세 문면 판정 미커버) · `check-context-isolation`(#12·#13 타 BC 관문 축 · 명세 «기재» 확인 미커버). 근거 유형 표기는 §16 4원 안에서만 썼다(형제 문서 적대 리뷰 R2-11 — «파일럿 선례»는 4원 밖이라 근거 자리에 쓰지 않음).
- **⑧ [adv W3-3 처분] b3-2(Work #24 · 항-(1)) `check-app-container` 병기는 유지**: 지적은 ⓐ docstring 이 축을 명시 부인 ⓑ 실제 술어가 항-(2) 축이라 #25 와 이중 계상 ⓒ 전형 위반에 미발화 셋을 들어 철회를 요구했으나, 원문 대조 결과 **ⓐ는 절반만 성립**한다 — 인용 문장은 «이 좁은 결정적 그물이 «위치» 한 축을 모델 무관하게 집행한다»는 **긍정 선언**과 «판정-소유 형태(빈혈) 같은 의미 변종은 범위 밖»이라는 **범위 한정**이 한 문장에 붙은 꼴이고, 부인되는 것은 이 규범의 괄호 주석(형태)이지 주술어가 아니다. 이 Work 의 주술어는 «판정을 얹는 코드를 평면 모델에 **남기지** 않았는가» = 위치이고, 검사기 회귀 표본이 정확히 «기존 `catalog/` 가 루트 평면 + 새 마이그레이션/**판정 적재**인데 `application/` 로 이주 안 함» — 항-(1) 이주 실패 그 자체다. **ⓑ도 기각** — 위치는 항-(1)·항-(2)가 공유하는 한 기계 축이고, api F5 가 벌한 것은 축이 **어긋난** 병기이지 축을 공유한 병기가 아니다(§0 P-D 경계선 ⑵ 로 명문화). **ⓒ는 수용** — G2 미성립 국면의 미발화를 basis 한계에 신설했다. 다만 basis 의 «§16 역도 성립» 원용은 지적대로 자리를 잘못 잡았으므로(docstring 이 이름으로 인용한 조문은 항-(2) = b3-3) 그 문구를 이 Work 에서 빼고 b3-3 소관임을 명기했다. 이 판정은 W3-2 의 철회와 정합한다 — 거기엔 긍정 술어가 0이고 대상 산출물(테스트)이 검사기 스캔 밖이었다.
- **⑨ [adv W3-8 처분] b5(Work #29) `check-business-vocabulary` 병기는 존치 + basis 강화**: 규범은 «명세 전반의 일관 사용», 검사기 술어는 «어휘 정의의 단일 출처(#628)·framework 격리(#47·#52)»로 경계선 사례가 맞다. 존치 근거는 #628 이 «같은 낱말이 여러 곳에서 다른 뜻을 갖는 것»을 코드에서 원천 차단하는 **유비쿼터스 언어의 기계 실현**이라는 점이고, 인정 범위를 **#628 한 축의 간접 커버**로 좁히면서 «일관성 자체의 술어는 27종에 0»을 basis 에 명기했다(#47·#52 격리 축은 배제로 강등). 판정 기준은 §0 P-D 경계선 ⑶ 에 신설했다.
