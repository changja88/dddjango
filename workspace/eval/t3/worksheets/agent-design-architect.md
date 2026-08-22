# T3 이관 검수표 — agent-design-architect

- 원문: `dddjango/agents/design-architect.md` (96행 · 센서스 일치)
- spec: `workspace/eval/t3/specs/agent-design-architect.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-design-architect.spec.json` → **exit 0** (블록 56 · Work 205 · `--write` 미사용 · 2026-08-22 적대 리뷰 처분 반영본)

## 1. census 대사 (절별 규범 수)

| 절 | 헤딩 | 발주서(센서스) | spec | 차 | 판정·사유 |
|---|---|---|---|---|---|
| s001 | (전문) | 3 | 3 | 0 | 일치 — description 3문(호출 트리거·통합 명세 작성/중재·코드 금지). 13행 본문은 역할 서술이라 prose 판정 |
| s002 | 입력 | 6 | 8 | +2 | **센서스 과소** — 22행 불릿이 4문(고정 배치 존중·명세 명시·미고정 판단·G1 재고 상신)이고 25행이 2문(«조사한다» / «결과 제약에 쓴다»)이다. 문장 해상도(§13 «Work 채번 단위가 문장») 기준 spec 이 옳다 |
| s003 | 산출 | 3 | 3 | 0 | 일치 |
| s004 | 명세에 담는 것 | 9 | 10 | +1 | **센서스 과소** — 35행 «권고를 적으려면 … 저자를 명시하고, 권고는 결정이 아니다 — … 선반영하지 않는다»는 한 문장 안에서 Obligation/Prohibition 이 갈려 2 Work 로 분리 |
| s005 | Error response contract 12-slot | 149 | 170 | +21 | **센서스 과소** — 센서스 값이 P0 «명세에 담는 것» 158 을 기계 경계(31~36/37~81)로 나눈 잔여치라 절 내부 재계수가 없다. 장문 불릿에서 «한 행 다규범»이 크게 벌어짐: 58행 15 · 59행 14 · 62행 26 · 64행 13. spec 이 옳다 (58행은 적대 리뷰 F1 처분으로 14→15 — composition 문장 dash 금지절 분리 채번) |
| s006 | 리뷰 반영·충돌 중재 | 7 | 7 | 0 | 일치 |
| s007 | 경계 | 4 | 4 | 0 | 일치 |
| **계** | | **181** | **205** | **+24** | 불일치 3절 전부 «센서스 과소 산정» 판정 — 과대 산정 판정 0 |

계수 규율(과대 방지): 한 문장 안에서 의무·금지의 **성격이 갈릴 때만** 분리 채번했고, 같은 의무를 dash/colon 으로 되풀이한 재진술(59행 «8행으로 … 박는다 — … 8행을 채운다», 64행 «소유한다 → 박는다»)은 1 Work 로 합쳤다. 근거 문장(«*왜* — …»)·열거 조각(19·21행 입력 목록)은 규범으로 세지 않았다.

계수 규율의 경계 사례 3건(적대 리뷰 F1·F2 처분 — 기준 비대칭 해소 기록):

1. **분리(58행 composition 문장 — F1 반영)**: dash 절 «기존 BC 의 배선 실물은 배선 결정의 입력이 아니고, preserve 를 배선 답습의 근거로 명세에 박지 않는다»는 앞 절(구성 표준 = 산출물 «형태» 의무)과 **주어가 다르다** — 뒤 절의 주어는 *명세 저작 행위*(어떤 근거를 명세에 기재하는가)이고, 특히 «preserve 를 근거로 쓰지 마라»는 별개 규범(#90 preserve 채택)과의 상호작용을 금지하는 축이다. 성격이 갈리므로 #21/#22·#110/#111·#128/#129 선례대로 분리해 Work 94(Prohibition)를 채번했다.
2. **병합(22행 «존중한다 — 암묵 재결정하지 않는다» — F2 기각 후 기록)**: 이 dash 는 **같은 축의 부정면 재진술**이다. 근거 — 같은 행 뒤쪽이 그 의무를 «*재결정 금지 ≠ 재고 불가*»라는 **한 낱말**로 되받아 부르므로 문면 자신이 두 절을 한 결정으로 취급한다. s004 35행(#21/#22)은 «저자를 명시한다»(기재 행위)와 «권고 방향을 선반영하지 않는다»(별개 산출물 상태)로 **행위 대상이 다른** 케이스라 분리했다 — 기준은 «성격이 갈리는가»로 일관되고, 22행은 그 기준을 통과하지 못해 1 Work 로 남긴다.
3. **병합(62행 «표준 파일트리다(기존 레이아웃은 트리 결정의 입력이 아니다)» — #126)**: 괄호절이 앞 의무의 입력 배제면을 되풀이하는 재진술이라 1 Work. 58행 dash 절과 달리 «preserve 를 근거로 기재 금지» 같은 **별개 규범과의 상호작용 축**이 없다 — 두 자리의 처분이 갈리는 이유가 이것이다.

## 2. 배선 근거 표 (전 규범 205건)

| # | 절/블록(행) | Work label | class | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b2 (3) | Phase 1 설계 단계의 Coordinator 호출 대상 | Obligation | — | `command-dddjango` | ①문면 — 프론트매터 description 은 Coordinator 라우팅 트리거 · §16 위임 기본값 표(command+agents 절차 층 → command-dddjango). 검사기 27종 docstring 전수에 에이전트 호출·라우팅 술어 없음 |
| 2 | s001/b2 (3) | 승인 스코프 기반 통합 설계 명세 작성과 리뷰 노트 반영·중재 | Obligation | — | `command-dddjango` | 동상 — 산출 계약의 절차 준수 판정 주체는 Coordinator(G1 게이트) |
| 3 | s001/b2 (3) | 코드 미작성 | Prohibition | — | `command-dddjango` | 동상 — 산출물 종류 제한은 절차 판정(코드 산출은 agent-coder 소유) |
| 4 | s002/b3 (20) | 비활성 lens 항목의 명세 제외 | Prohibition | — | `command-dddjango` | §16 기본값(절차 층) — lens 활성 목록은 Coordinator 가 공급하므로 준수 판정도 같은 주체. 27종 docstring 에 lens 범위 술어 없음 |
| 5 | s002/b5 (22) | 고정된 BC 배치 존중과 암묵 재결정 금지 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | §16 기본값 + ①문면 «ddd 리뷰어가 배치를 부적절하다 지적하면» — BC 경계 타당성 판정 주체를 문면이 design-review-ddd 로 지목 |
| 6 | s002/b5 (22) | 고정 BC 배치의 명세 컨텍스트 절 명시 | Obligation | — | `command-dddjango` | §16 기본값 — ①문면 «하위는 스코프 메모가 아니라 명세만 읽으므로»로 기재 누락 판정이 게이트 몫임을 지목 |
| 7 | s002/b5 (22) | 미고정 시 배치 판단과 근거 기록 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | 동상 — 배치 판단의 타당성은 ddd lens 심사 |
| 8 | s002/b5 (22) | ddd 리뷰어 지적의 G1 배너 재고 상신 | Obligation | — | `command-dddjango` | ①문면 «G1 배너 옵션으로 사용자에게» — 배너 운용 주체는 Coordinator |
| 9 | s002/b6 (23–24) | G1 override 재호출의 해당 절 제자리 갱신(전체 재작성 금지) | Obligation | — | `command-dddjango` | ①문면 «Coordinator가 G1 override 입력으로 너를 재호출» — 좁은 재호출 계약의 판정 주체 |
| 10 | s002/b7 (25–26) | 명세 착수 전 기존 소스·테스트 구조 현황 조사 | Obligation | — | `command-dddjango` | §16 기본값 — 술어가 «조사»라 코드 산출물 검사 대상이 아님(트리 표준 자체는 check-layer-skeleton 소관이나 이 문장은 조사 행위 규범) |
| 11 | s002/b7 (25–26) | 조사 결과(이관 빚·배선 복원 지점·기존 test artifact 위치)의 결과 제약 반영 | Obligation | — | `command-dddjango` | 동상 |
| 12 | s003/b1 (28–30) | 통합 설계 명세 1건의 지정 경로 Write 작성 | Obligation | — | `command-dddjango` | ①문면 «Coordinator가 지정한 경로» — 산출물 존재·경로 판정 주체 · §16 기본값 |
| 13 | s003/b1 (28–30) | 그 밖 산출물 생성 금지 | Prohibition | — | `command-dddjango` | 동상 |
| 14 | s003/b1 (28–30) | 코드·테스트 미작성(구현은 coder·인수 테스트는 acceptance-tester) | Prohibition | — | `command-dddjango` | 동상 — 역할 분리 판정은 파이프라인 소유(Coordinator) |
| 15 | s004/b1 (32–34) | 활성 lens 항목 한정 수록 | Obligation | — | `command-dddjango` | §16 기본값 — lens 활성 목록 공급자와 같은 판정 주체 |
| 16 | s004/b2 (35–36) | Ninja 오류 계약 스코프의 12-slot 계약 적용 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 병렬 심사판 존재(agent-design-review-api «Error response contract 12-slot») — 적용 여부 판정은 계약 lens 리뷰어와 게이트 |
| 17 | s004/b2 (35–36) | 신규 Ninja scope 기본 error profile 은 dddjango-code-json | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②check-error-centralization·check-api-error-controller-contract 는 `--error-profile` 을 «입력»으로 받는 profile-gated 구조라 profile 선택 자체를 판정하지 않음 — 기본값 도피가 아니라 검사 공백 |
| 18 | s004/b2 (35–36) | evidence 확인 또는 명시 승인 시 preserve-established 채택 | Exception | — | `command-dddjango`·`agent-design-review-api` | 동상 — profile 선택 조건의 판정은 심사판(design-review-api slot 3) |
| 19 | s004/b2 (35–36) | 두 종류 evidence 동시 요구 금지와 미해결·충돌 시에만 STOP | Exception | — | `command-dddjango` | §16 기본값 — STOP 게이트 판정 주체는 Coordinator(command-dddjango s011 반송 계약과 쌍) |
| 20 | s004/b2 (35–36) | STOP 기록의 닫힌 선택지별 대가 한 줄 병기 | Obligation | — | `command-dddjango` | 동상 — 기록 형식 불비 판정은 게이트 |
| 21 | s004/b2 (35–36) | 권고의 산출물·리뷰 노트 인용 저자 명시 | Obligation | — | `command-dddjango` | 동상 |
| 22 | s004/b2 (35–36) | 권고 방향의 명세·기본값 선반영 금지 | Prohibition | — | `command-dddjango` | 동상 — 권고와 결정의 분리는 절차 규범 |
| 23 | s004/b2 (35–36) | 외부 관찰 결과가 갈리는 물음의 STOP 의무(완성 논증도 생략 근거 아님) | Obligation | — | `command-dddjango` | 동상 |
| 24 | s004/b2 (35–36) | 매니페스트 의존성 부재·파일명에 의한 API stack·profile 강등 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-api` | 동상 + ①문면 병렬 심사판(design-review-api slot 3 «파일명이나 dependency 유무는 근거가 아니다») |
| 25 | s005/b1 (38–40) | 12개 slot 의 지정 순서·정확 label 작성 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 병렬 심사판(design-review-api s006 «아래 12개 slot이 이 순서로 존재하고») — 명세 문서 검사 술어는 27종 docstring 어디에도 없음 |
| 26 | s005/b1 (38–40) | 12-slot carrier 자체의 code profile artifact 비강제 | Exception | — | `command-dddjango` | §16 기본값 — carrier 한계 조항(형식 규범) |
| 27 | s005/b1 (38–40) | slot 5–12 의 선택 profile 조건부 기록 | Obligation | — | `command-dddjango`·`agent-design-review-api` | 동상 — 심사판 «Slots 5–12의 code-profile constraint는 dddjango-code-json에만 적용» |
| 28 | s005/b1 (38–40) | preserve scope 에 code-profile module·Enum·base·direct-Status 혼입 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-api` | ②check-error-centralization·check-api-error-controller-contract docstring — preserve 실행은 «add no new error-mapping semantics»라 혼입을 차단하지 않음(검사 공백을 심사판이 받음 — 도피 아님) |
| 29 | s005/b1 (38–40) | slot 누락·모호·상충 시 STOP 과 G1 미완료 | Obligation | — | `command-dddjango` | §16 기본값 — 게이트 완료 판정 주체 |
| 30 | s005/b2 (41) | slot 1 — contract scope inventory 열거 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 1 병렬 — 명세 기재 검사 술어 없음 |
| 31 | s005/b2 (41) | slot 1 — repository·greenfield artifact 경로 표기와 부재 항목 명시 | Obligation | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 32 | s005/b2 (41) | slot 1 — planned 경로의 신규 산출물 한정(기존은 관찰 경로·타 BC 표준 경로 금지) | Prohibition | — | `command-dddjango`·`agent-design-review-api` | 동상 — 2026-08-13 정정 문면 |
| 33 | s005/b3 (42) | slot 2 — repository 행의 project-relative 경로·관찰 기록 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 2 병렬 |
| 34 | s005/b3 (42) | slot 2 — external evidence 식별자·planned 경로 입증 허용 | Permission | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 35 | s005/b3 (42) | slot 2 — 동일 profile common/error 재사용의 단일 행 dedupe | Obligation | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 36 | s005/b3 (42) | slot 2 — STOP 조건의 모호·상충·불완전 한정 | Exception | — | `command-dddjango` | §16 기본값 — STOP 판정 주체 |
| 37 | s005/b3 (42) | slot 2 — external·planned 사유만의 중단 금지 | Prohibition | — | `command-dddjango` | 동상 |
| 38 | s005/b3 (42) | slot 2 — 표준 트리 불일치의 관찰 기록 취급(이동 지시 금지) | Prohibition | — | `command-dddjango` | §16 기본값 — 기존 코드 처분은 G0 빚 결정 소관(Coordinator)이라 골격 검사기(check-layer-skeleton)로 배선하면 오배선 |
| 39 | s005/b4 (43) | slot 3 — scope 별 error profile 과 선택 근거 기록 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 3 병렬 |
| 40 | s005/b4 (43) | slot 3 — RFC 9457 wire 의 preserve 보존 허용(파일명·dependency 는 근거 불가) | Permission | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 41 | s005/b4 (43) | slot 3 — preserve scope 의 code-profile artifact 격리 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②profile-gated 검사기는 preserve 에 schema 의미를 적용하지 않아 격리 자체는 미집행 — 심사판 몫 |
| 42 | s005/b5 (44) | slot 4 — compatibility/rollout 항목 기록 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 4 병렬 |
| 43 | s005/b5 (44) | slot 4 — 승인 없는 기존 계약의 종료·변경 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 44 | s005/b6 (45) | slot 5 — code-json 의 common FrameworkErrorSchema action 3값 한정(none 금지) | Obligation | `check-error-centralization.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «dddjango-code-json validates the canonical common/BC FrameworkErrorSchema modules, project inventory correspondence» + §16 매핑 표 «schema checker» = check-error-centralization.py |
| 45 | s005/b6 (45) | slot 5 — approved-change 의 명시 사용자 승인 evidence 병기와 부재 시 STOP | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 5 — 승인 evidence 존재 판정은 게이트 |
| 46 | s005/b6 (45) | slot 5 — preserve 의 profile-native action 기록과 common ErrorSchema 강제 금지 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②동 checker 는 preserve 에 schema 의미 미적용 — 심사판 몫 |
| 47 | s005/b7 (46) | slot 6 — code-json common ErrorSchema shape 기록(기준선·field set·canonical path) | Obligation | `check-error-centralization.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «validates the canonical common/BC FrameworkErrorSchema modules … wire-code uniqueness» + §16 매핑 표 «schema checker» |
| 48 | s005/b7 (46) | slot 6 — 신규 shape 생성·기준선 변경의 별도 명시 사용자 승인 | Obligation | — | `command-dddjango` | §16 기본값 — 일반 G1 승인과 분리된 승인 획득은 게이트 절차 |
| 49 | s005/b7 (46) | slot 6 — 변경 시 slot 5 approved-change 와 별도 승인 evidence 의 G1 완료 조건 | Obligation | — | `command-dddjango` | 동상 |
| 50 | s005/b7 (46) | slot 6 — preserve 의 profile-native wire/shape·승인 evidence 기록 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 6 병렬 |
| 51 | s005/b7 (46) | slot 6 — 관찰 RFC/schema/handler 보존 허용과 새 recipe 일반화 금지 | Permission | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 52 | s005/b8 (47) | slot 7 — code-json 의 error-BC 별 side-effect-free module 경로·common import 기록 | Obligation | `check-error-centralization.py` | `command-dddjango`·`agent-design-review-api` | ②docstring — canonical common/BC FrameworkErrorSchema 모듈과 project inventory correspondence 검사(§16 «schema checker») |
| 53 | s005/b8 (47) | slot 7 — preserve 의 profile-native module 기록과 BC error module 비강제 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②preserve 는 schema 의미 미적용 — 심사판 몫 |
| 54 | s005/b9 (48) | slot 8 — code-json 의 error-BC 별 단일 string Enum·최소 public code 기록 | Obligation | `check-error-centralization.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «wire-code uniqueness, and narrow direct raw-string discriminator forms» — public code 축 집행(§16 «schema checker») |
| 55 | s005/b9 (48) | slot 8 — preserve 의 profile-native code taxonomy 기록과 BC ErrorCode 비강제 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②preserve 는 schema 의미 미적용 — 심사판 몫 |
| 56 | s005/b10 (49) | slot 9 — code-json 의 BC base ErrorSchema(식별자 field 좁힘)·경로 기록 | Obligation | `check-error-centralization.py` | `command-dddjango`·`agent-design-review-api` | ②docstring — canonical BC FrameworkErrorSchema 모듈 검사(§16 «schema checker») |
| 57 | s005/b10 (49) | slot 9 — 좁힌 식별자 field 의 required canon 인정 | Exception | — | `command-dddjango`·`agent-design-review-api` | ①문면 «식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15» + 심사판 slot 9 동일 문장 |
| 58 | s005/b10 (49) | slot 9 — preserve 의 profile-native schema 기록과 BC ErrorSchema 비강제 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②preserve 는 schema 의미 미적용 — 심사판 몫 |
| 59 | s005/b11 (50) | slot 10 — code-json prepared error mapping chain 의 표 기록 | Obligation | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «Enforce direct controller-owned code-profile error mapping» + §16 매핑 표 «controller checker» = check-api-error-controller-contract.py |
| 60 | s005/b11 (50) | slot 10 — internal failure type 과 output object 의 구분 | Obligation | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | 동상 — 선택 controller 의 direct mapping 형태 검사가 같은 축 |
| 61 | s005/b11 (50) | slot 10 — 복수 internal failure 의 단일 public ErrorCode 수렴 허용 | Permission | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 8 «여러 internal failures는 한 code를 공유할 수 있고» |
| 62 | s005/b11 (50) | slot 10 — raw infra failure 의 기본 500 과 승인된 public meaning 한정 정규화 | Obligation | `check-transient-overmapping.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «② design-architect 생산자 예방(명세에 «transient 변종만 retryable»)» — raw 인프라 예외의 무조건 retryable 매핑 차단이 같은 축 |
| 63 | s005/b11 (50) | slot 10 — preserve 의 profile-native mapping 기록과 code-profile chain 비강제 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②preserve 실행은 error-mapping 의미 미적용 — 심사판 몫 |
| 64 | s005/b12 (51) | slot 11 — code-json 의 두 path 중 하나 명시 | Obligation | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «dddjango-code-json analyzes only selected controllers owned by an error-bc» + §16 매핑 표 «controller checker» |
| 65 | s005/b12 (51) | slot 11 — exception path 의 단일 application call·narrow try·승인 예외 한정 catch | Obligation | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | 동상 |
| 66 | s005/b12 (51) | slot 11 — outcome path 의 인위적 try/catch 금지와 직후 직접 분기 | Prohibition | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | 동상 |
| 67 | s005/b12 (51) | slot 11 — 승인 ErrorSchema 생성·header 설정 후 2인자 Status 직접 반환 | Obligation | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | 동상 — direct controller-owned mapping 집행 |
| 68 | s005/b12 (51) | slot 11 — status body property 발명 금지 | Prohibition | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | 동상 |
| 69 | s005/b12 (51) | slot 11 — error helper/handler/factory/serializer·mapping 추출 금지 | Prohibition | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | 동상 — «direct» 계약의 반대면 |
| 70 | s005/b12 (51) | slot 11 — preserve 의 profile-native controller mapping 기록과 direct Status 비강제 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②preserve 는 새 error-mapping 의미를 더하지 않음 — 심사판 몫 |
| 71 | s005/b13 (52–53) | slot 12 — code-json 의 status/body/header mapping·OpenAPI 후보 기록과 입장 표 행 참조 | Obligation | `check-openapi-error-declaration.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «선택된 operation이 직접 반환하는 BC 오류와 response={status: <Bc>ErrorSchema} 선언의 일치를 검증» + §16 매핑 표 «OpenAPI checker» |
| 72 | s005/b13 (52–53) | slot 12 — Pydantic private metadata·validator 위치·기본 직렬화의 자동 영구 테스트 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 slot 12 — 테스트 입장 판정은 입장 표(기계 술어 없음) |
| 73 | s005/b13 (52–53) | slot 12 — 공개 Python consumer 계약의 HTTP 와 별도 행 심사 | Obligation | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 74 | s005/b13 (52–53) | slot 12 — preserve 의 profile-native media type·schema·test/OpenAPI evidence 기록 | Obligation | — | `command-dddjango`·`agent-design-review-api` | 동상 |
| 75 | s005/b13 (52–53) | slot 12 — framework 오류 smoke·auth/header 검증의 승인 계약·독자 failure 한정 입장 | Exception | — | `command-dddjango`·`agent-design-review-api` | 동상 — exact framework body snapshot 요구 금지 포함 |
| 76 | s005/b13 (52–53) | slot 12 — native download/stream/redirect·schema-less 204 의 선언 Schema carveout | Exception | `check-response-schema-bypass.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» — carveout 은 그 규칙의 예외면이라 같은 검사기 소관 |
| 77 | s005/b14 (54–55) | framework-owned 오류의 BC ErrorSchema 변환·response 광고 금지 | Prohibition | `check-business-vocabulary.py`·`check-openapi-error-declaration.py` | `command-dddjango`·`agent-design-review-api` | ④rule-owner-map #119 «401·403·404·422·429·HttpError 는 framework 소유(BC 재선언 금지)» = check-business-vocabulary 담당 · 광고 축은 check-openapi-error-declaration 의 response 선언 일치 검사 |
| 78 | s005/b14 (54–55) | 인증 실패의 None 반환 또는 framework AuthenticationError raise | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 + 심사판 불릿 «인증 실패는 None을 return하거나 framework AuthenticationError를 raise해야 한다» — 27종 docstring 에 인증 실패 반환형 술어 없음 |
| 79 | s005/b14 (54–55) | AuthenticationError·ErrorSchema 반환과 request.auth 저장 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-api` | 동상 — 심사판이 blocker 로 판정 |
| 80 | s005/b14 (54–55) | 406·415 의 별도 사용자 승인과 Ninja 경계 내 구현 한정 | Exception | `check-ninja-boundary-middleware.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «대표 회귀는 406/415 콘텐츠 협상을 request.path 하드코딩한 전역 미들웨어로 자작한 것 — django-ninja는 협상/임의 status를 경계 안에서 네이티브로 낸다(§6.3)» |
| 81 | s005/b14 (54–55) | preserve 의 framework error body·협상 behavior 기록과 code-profile artifact 미도입 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②preserve 실행은 새 의미 미적용 — 심사판 몫 |
| 82 | s005/b15 (56) | 도메인(ddd) lens 항목의 명세 수록 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | ①문면 lens 귀속 + §16 위임 기본값 표(architecture-ddd 설계 시점 규범 → agent-design-review-ddd)와 정합 |
| 83 | s005/b16 (57) | 계약(api) lens 항목의 명세 수록 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 lens 귀속 + §16 기본값 표(architecture-api → agent-design-review-api) |
| 84 | s005/b16 (57) | 저장·전달 보장 등 데이터 측면의 db lens 위임 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 «db lens로 넘긴다» — 수임 lens 를 문면이 지목 |
| 85 | s005/b16 (57) | 유한 재시도·CAS 실패 outcome 의 prepared error mapping 포함 | Obligation | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | ②docstring — controller-owned direct error mapping(승인 status·slot-6 body·header)의 실물 축이 같음(§16 «controller checker») |
| 86 | s005/b16 (57) | retryable 503·409 선택의 G1 상신과 임의 확정 금지 | Prohibition | `check-transient-overmapping.py` | `command-dddjango`·`agent-design-review-api` | ②docstring 「② design-architect 생산자 예방(명세에 «transient 변종만 retryable»)」 — 검사기가 architect 를 명시 지목(기본값 도피 금지 조항 적용) |
| 87 | s005/b16 (57) | public meaning 없는 raw infra·미식별 예외의 framework 500 유지 | Obligation | `check-transient-overmapping.py` | `command-dddjango`·`agent-design-review-api` | 동상 — 무분기 클래스 통째 retryable 매핑 차단의 반대면 |
| 88 | s005/b16 (57) | application·domain 의 HTTP status/body 생성 금지 | Prohibition | `check-transaction-boundary.py`·`check-domain-model.py` | `command-dddjango`·`agent-design-review-api` | ④**domain 축 전면** — #8 domain_layer 의 밖으로 나가는 import 0(서드파티 포함·check-domain-model). **application 축은 부분** — #4 는 `application_layer/**` 의 **django import 만** 문다(check-transaction-boundary docstring) 라 `ninja`/`ninja_extra` 의 `Status` 등 비-django HTTP 산출은 미커버이고, #7(check-event-publish)도 «층 역참조(driving/driven import)와 framework 비계약 모듈만» 물어 미봉이다(실물 `_check_application_imports` 확인) — 그 공백은 게이트·api lens 심사판 몫 |
| 89 | s005/b17 (58) | 새 HTTP/JSON API surface 의 stack 1급 결정 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 «lens 무관, 새 API 표면이 생기면 항상 결정» + §16 기본값 표(api) |
| 90 | s005/b17 (58) | 확립 DRF·plain 계약 보존과 부재 시 Django Ninja 적용 | Obligation | — | `command-dddjango`·`agent-design-review-api` | 동상 — 계약 profile 축 판정은 api lens 심사 |
| 91 | s005/b17 (58) | manifest 의존성 부재만의 plain 강등·preserve 전환 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-api` | 동상 — s004 동형 문장과 같은 축 |
| 92 | s005/b17 (58) | 새 Ninja surface 의 NinjaExtraAPI·class controller 와 profile 별 단일 project API instance | Obligation | `check-composition-root.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «명시적 dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf의 직접 import provenance와 exactly-once 호출 관계를 함께 검사한다» — **API instance·registrar 축 한정**. `NinjaExtraAPI`/`@api_controller` class controller 의 «형태» 축 술어는 27종 어디에도 없다(`check-context-isolation` #110 은 *이미 붙은* `@api_controller` 의 `auto_import=False` 여부만 문다 — 형태 요구가 아니다) → 형태 축은 검사 공백으로 심사판 몫 |
| 93 | s005/b17 (58) | profile 무관 composition 표준(auto_import=False registrar·명시 호출·import-time 등록 금지) | Obligation | `check-context-isolation.py`·`check-composition-root.py` | `command-dddjango` | ④#110 auto_import=False · #431 부작용 등록 금지(check-context-isolation) + ②composition-root 의 registrar/URLconf provenance·exactly-once 검사 |
| 94 | s005/b17 (58) | 기존 배선 실물의 결정 입력 배제와 preserve 의 배선 답습 근거 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-api` | ①문면 «기존 BC 의 배선 실물(`*_api_router.py` 동형)은 배선 결정의 입력이 아니고, preserve 를 배선 답습의 근거로 명세에 박지 않는다»(2026-08-12 라운드 1′) — ②`check-composition-root`·`check-context-isolation` 은 registrar/URLconf provenance·`auto_import` 실물만 검사해 «명세에 답습 근거를 기재하는» 축은 미커버(검사 공백) → §16 기본값(절차 층) + 계약 profile 축 심사판 병기 |
| 95 | s005/b17 (58) | 승인 스코프 밖 기존 파일의 이동·개명·재배선 결정 금지 | Prohibition | — | `command-dddjango` | ①문면 «기존 코드의 처분은 G0 빚 결정(ⓐ/ⓑ)이 확정» — 처분 권한 주체를 Coordinator 로 문면이 지목(구조 검사기로 배선하면 오배선) |
| 96 | s005/b17 (58) | G0 ⓐ 승인 항목만 슬라이스 0 으로 전재 | Obligation | — | `command-dddjango` | 동상 |
| 97 | s005/b17 (58) | BC composition_root 의 DI 단독 소유 | Obligation | `check-composition-root.py`·`check-port-adapter-pairing.py` | `command-dddjango` | ②composition-root docstring «DI 조립은 BC 루트의 composition_root/(결선은 dependency_wiring.py — 트리 2~4행·#84·#85)가 소유» + ④#134 컨트롤러는 build_* 만(check-port-adapter-pairing) |
| 98 | s005/b17 (58) | controller 의 예외 catch·ErrorSchema 생성 후 direct Status 반환 | Obligation | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «Enforce direct controller-owned code-profile error mapping»(§16 «controller checker») |
| 99 | s005/b17 (58) | internal failure/output 구분과 error handler·helper·factory·serializer 추출 금지 | Prohibition | `check-api-error-controller-contract.py` | `command-dddjango`·`agent-design-review-api` | 동상 — slot 11 과 같은 축(문서 내 병렬 서술) |
| 100 | s005/b17 (58) | preserve 의 profile-native controller/handler/schema 보존과 code-profile recipe 미도입 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ②preserve 실행은 새 error-mapping 의미 미적용 — 심사판 몫(보존 범위는 오류 wire 산출물까지라는 문면 한정 포함) |
| 101 | s005/b17 (58) | 성공 응답의 선언 2xx response schema 반환과 선언적 payload 입력 | Obligation | `check-response-schema-bypass.py` | `command-dddjango`·`agent-design-review-api` | ②docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» |
| 102 | s005/b17 (58) | 406/415 승인 시에도 Ninja 경계 path 사용과 함수형 Router 강제·raw body 수동 파싱 금지 | Prohibition | `check-ninja-boundary-middleware.py` | `command-dddjango`·`agent-design-review-api` | ②docstring — 406/415 를 전역 미들웨어로 자작한 회귀 차단(§6 집행) |
| 103 | s005/b17 (58) | server-render HTML view 의 예외 출처별 책임 명세(view-local 재렌더·handler500·process_exception 503) | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 «implementation-django-web §11» 인용 — 27종 docstring 에 서버렌더 예외 경로 술어 없음(check-transient-overmapping 은 API 경계 handler 한정) |
| 104 | s005/b18 (59) | 데이터(db) lens 항목의 명세 수록 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 lens 귀속 + §16 기본값 표(architecture-db → agent-design-review-db) |
| 105 | s005/b18 (59) | Risky Write 의 §9.6 Consistency Block 8행 명세 기재(번호 인용 대체 금지) | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 + 병렬 심사판(agent-design-review-db «점검 항목» — 8행 의미적 충족 심사) · 설계 문서 검사 술어는 27종에 없음 |
| 106 | s005/b18 (59) | 각 행의 결정 기재와 해당 없음의 근거 병기 미적용 | Obligation | — | `command-dddjango`·`agent-design-review-db` | 동상 |
| 107 | s005/b18 (59) | 미요청 멱등성의 silent 필수 서브시스템화 금지 | Prohibition | `check-idempotency-scope-creep.py` | `command-dddjango`·`agent-design-review-db` | ②docstring «미요청 멱등성 금지 가드는 이미 design-architect(§9.6 Idempotency storage 행)에 산문으로 있으나 … 이 백스톱은 코드를 봐서 집행한다» — 검사기가 이 문장을 명시 지목 |
| 108 | s005/b18 (59) | 기본 미적용 현재 상태 commit 과 배너 override 항목 산출(미해결 옵션 블록 금지) | Obligation | `check-idempotency-scope-creep.py` | `command-dddjango`·`agent-design-review-db` | ②동 docstring — 면제 조건 (4) 가 G1 사용자-승인 채택 배너라 배너 산출이 검사 대상 축 |
| 109 | s005/b18 (59) | G1 채택 시 override 재호출 경로의 architecture-api §13 구현 | Obligation | — | `command-dddjango` | §16 기본값 — 재호출 트리거 주체는 Coordinator(문면 «Coordinator가 G1 override 입력으로 너를 재호출») |
| 110 | s005/b18 (59) | 미요청 멱등성의 명세 silent 의무화 금지(스코프 초과) | Prohibition | `check-idempotency-scope-creep.py` | `command-dddjango`·`agent-design-review-db` | ②동 docstring — DR-24 C3·DR-27 회귀 차단이 이 문장의 코드 측 백스톱 |
| 111 | s005/b18 (59) | scope.md 가 범위 밖으로 명시한 견고성 결정의 동일 처리(미적용 commit + 배너 항목) | Obligation | — | `command-dddjango` | ②검사기 커버는 멱등성 산출물 한정(docstring 한계 «이름 회피는 v1 패턴이 놓칠 수 있다»)이라 일반 견고성 축은 미커버 — 기본값 |
| 112 | s005/b18 (59) | Test criteria 행의 동시성 검증 기준 포함 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 + 심사판(db «Risky Write·outbox·제약의 Test criteria는 candidate signal») |
| 113 | s005/b18 (59) | 엔진별 확정에 의한 Consistency Block 대체 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-db` | 동상 — 블록 충족 심사 주체 |
| 114 | s005/b18 (59) | 락·동시성 Risky Write 의 개발·운영 엔진별 동작 차이 명세 확정 | Obligation | `check-mechanism-ownership.py` | `command-dddjango`·`agent-design-review-db` | ②docstring ⑴ «코더가 프로덕션 DB 엔진의 트랜잭션·락·격리 메커니즘을 명세 승인 없이 커스텀 백엔드로 교체한 정확한 형태만 차단»(4-AND 고정밀) — **커스텀 백엔드 교체 축 한정**의 코드 측 짝이다. 라벨 축인 «엔진차 명세 확정» 의무 자체(repo 수준 자작 락·엔진차 미확정 명세)는 이 검사기가 발화하지 않으므로 db lens 심사(`agent-design-review-db`)가 실집행자다 |
| 115 | s005/b18 (59) | 비즈니스 판정의 인프라 이전 금지(WHERE 는 경합 가드만) | Prohibition | `check-domain-model.py`·`check-transaction-boundary.py` | `command-dddjango` | ④#257 상태 변경은 루트를 지난다(check-domain-model) · #195 save 인자는 루트 메서드 호출을 받은 객체(check-transaction-boundary) — 파일럿 ddd §3.2 «판정 SQL 이동» 동일 축 선례 |
| 116 | s005/b18 (59) | 판정·불변식의 도메인 소유와 프로덕션 경로 실행(응용은 조회→도메인→영속화·repo 는 저장만) | Obligation | `check-domain-model.py`·`check-transaction-boundary.py` | `command-dddjango` | 동상 — ④#257·#195·#287 쓰기 인자는 애그리거트 |
| 117 | s005/b18 (59) | 직렬화 필요 시 begin 모드 명시 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 §9.5 인용 — 명세 기재 규범(기계 술어 없음) |
| 118 | s005/b19 (60) | 영구 테스트의 DB 보장·독자 failure·기존 coverage 3축 개별 판정 | Obligation | — | `command-dddjango`·`agent-design-review-db` | ①문면 + 심사판(db 불릿 «DB 후보마다 … 감사한다») |
| 119 | s005/b19 (60) | Test criteria 행에 의한 add 자동 결정 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-db` | 동상 — 심사판 «candidate signal이지 자동 add가 아니다» |
| 120 | s005/b20 (61) | 외부 계약 candidate 목록 명시 | Obligation | — | `command-dddjango`·`agent-design-review-api` | ①문면 — 외부 관찰 계약 축(api lens) |
| 121 | s005/b20 (61) | 입장 표 통과 후에만 인수 테스트·슬라이스 전환 | Exception | — | `command-dddjango` | §16 기본값 — 슬라이스 전환은 파이프라인 절차(Coordinator) |
| 122 | s005/b20 (61) | 외부 관찰을 가르는 수치·비교 판정의 미달·정확값·초과 candidate 구분과 개별 심사 | Obligation | — | `command-dddjango` | 동상 — 입장 표 심사 절차 |
| 123 | s005/b20 (61) | 생성자·입력 가드와 동시성·transient 경계의 예시만에 의한 테스트 의무 부정 | Exception | — | `command-dddjango` | 동상 |
| 124 | s005/b20 (61) | 유효 경계 계약 누락 금지와 목록·경계값 recipe 의 add 근거 사용 금지 | Prohibition | — | `command-dddjango` | 동상 |
| 125 | s005/b21 (62) | 소스 물리 배치와 테스트 디렉터리 조직의 명세 결정 | Obligation | — | `command-dddjango` | §16 기본값 — 결정 수행 여부는 게이트 판정 |
| 126 | s005/b21 (62) | 소스 파일트리의 dddjango 표준 준수(기존 레이아웃은 결정 입력 아님) | Obligation | `check-layer-skeleton.py`·`check-app-container.py` | `command-dddjango` | ④#486 어느 BC 를 열어도 골격 그대로·#490 트리 밖 경로 위반(check-layer-skeleton) · §0-1 앱은 application/<app>/ 아래(check-app-container) |
| 127 | s005/b21 (62) | 표준 트리 문장의 신규 산출물 한정(스코프 밖 기존 배치 이동 지시 아님) | Exception | — | `command-dddjango` | ①문면 «§API스택의 처분-권한 문구와 같은 한계» — 기존 배치 처분은 G0 빚 결정 소관 |
| 128 | s005/b21 (62) | houserules final.md §0 불변식·§1 고정·재등장 칸의 명세 기재 | Obligation | `check-layer-skeleton.py` | `command-dddjango` | ④#488 고정(·재등장) 칸은 부모가 있으면 반드시 있다 — 폴더는 비어도 __init__.py 로 |
| 129 | s005/b21 (62) | final.md 소유 값의 명세 복사 금지 | Prohibition | — | `command-dddjango` | §16 기본값 — 값 단일 출처 유지 규범(문서 서술 축·기계 술어 없음) |
| 130 | s005/b21 (62) | YAGNI·단순성 사유의 불변식 생략·축소 금지 | Prohibition | `check-layer-skeleton.py` | `command-dddjango` | ④#486 «내용 유무 무관»·#488 «비면 빈 파일로» — 생략을 결정적으로 차단 |
| 131 | s005/b21 (62) | 접어야 할 실질 사유의 G1 트레이드오프 상신 | Obligation | — | `command-dddjango` | §16 기본값 — G1 상신 수임 주체 |
| 132 | s005/b21 (62) | 빈 계층의 관심사 실제 부재 한정 | Exception | `check-layer-skeleton.py` | `command-dddjango` | ④#489 «<…> 자리표시자 칸만 그 개념이 생길 때 생긴다» |
| 133 | s005/b21 (62) | HTTP/CLI 진입 보유 BC 의 컨트롤러 메서드·schema 실현 | Obligation | — | `command-dddjango` | ②check-layer-skeleton 은 «존재·폐쇄»만 보고 내용 판정은 Phase 3 편입분(docstring 명시) — 표현 유무 판정은 미커버라 기본값 |
| 134 | s005/b21 (62) | 표현 부재 판단의 근거 1줄 기재 | Obligation | — | `command-dddjango` | 동상 — 명세 서술 규범 |
| 135 | s005/b21 (62) | 빈 골격의 표현 검토 완료 신호화 금지 | Prohibition | — | `command-dddjango` | 동상 |
| 136 | s005/b21 (62) | 입장 표 승인 test artifact 의 의미군 배치 한정 | Exception | `check-test-config.py` | `command-dddjango` | ④#383/#384 test/ 직계 자식은 다섯(unit·integration·e2e·factories·fake) — 의미군 배치 축 집행 · 승인 여부 자체는 입장 표(미커버) |
| 137 | s005/b21 (62) | 구조 규칙만에 의한 test file·case·assertion·helper·빈 test package 생성 금지 | Prohibition | — | `command-dddjango` | §16 기본값 — 생성 근거 판정은 입장 표 절차 |
| 138 | s005/b21 (62) | 표준 트리 적용·ORM 명명·Django 앱 위치·리포지토리/포트 §3 명명의 명세 기재 | Obligation | `check-db-table.py`·`check-app-container.py` | `command-dddjango` | ④#329~#332 label·name·#335·#632 모델 파일·클래스명·#630 db_table(check-db-table) · §0-1 앱 위치(check-app-container) |
| 139 | s005/b21 (62) | 포트·리포지토리·어댑터 명명 규약의 구체 이름만 결정(타입표식·파일명 약어 금지) | Obligation | `check-naming.py`·`check-port-adapter-pairing.py` | `command-dddjango` | ④#28 원전 패턴 약어 금지·#41·#43 패턴 낱말(check-naming) · #218 파일명=폴더명·#220 <Capability>Port·#370 <System><Capability>Adapter(check-port-adapter-pairing) |
| 140 | s005/b21 (62) | 이름 결정의 설계 단계 확정(사후 교정 유예 금지) | Obligation | — | `command-dddjango` | §16 기본값 — 시점 규범(어느 단계에서 정하는가)은 절차 판정 |
| 141 | s005/b21 (62) | BC 간 통신의 OHS 우선·ACL 분리·도메인 이벤트 선택 결정 | Obligation | `check-context-isolation.py`·`check-port-adapter-pairing.py` | `command-dddjango`·`agent-design-review-ddd` | ④#12 부를 수 있는 것은 OHS·published_event 둘·#13 OHS 소비는 ACL 뿐(check-context-isolation) · #319 타 BC→acl 갈래·#365(check-port-adapter-pairing) |
| 142 | s005/b21 (62) | 업스트림 모델·예외 번역의 ACL 격리 명세(presentation·application 의 타 BC 예외 직접 catch 금지) | Prohibition | `check-context-isolation.py` | `command-dddjango` | ④ACL 군 #473 기저 예외를 잡는다 · OHS 군 #164 도메인 예외 번역 |
| 143 | s005/b21 (62) | OHS 노출·수정 스코프의 open_host_service 내부 구조 1급 결정 | Obligation | `check-context-isolation.py` | `command-dddjango` | ④OHS 군 #152/#154/#155 service·contract 구조 · #156/#157/#159/#160 계약 1타입=1파일 |
| 144 | s005/b21 (62) | 공개 함수 request/response 계약 시그니처와 예외 번역표 결정 | Obligation | `check-context-isolation.py` | `command-dddjango` | ④문면이 #633 을 직접 인용 — «#633 인자는 request 하나»가 check-context-isolation 담당(OHS 군) |
| 145 | s005/b21 (62) | LLM 일반지식에 의한 계약 재분류 금지 | Prohibition | — | `command-dddjango` | §16 기본값 — 명세 기재 누락의 결과(coder 즉흥 산출) 방지 규범 |
| 146 | s005/b21 (62) | 포트 선언 자리의 final.md §1·§2 소유 준수 | Obligation | `check-transaction-boundary.py`·`check-port-adapter-pairing.py` | `command-dddjango` | ④문면이 #282·#187·#365 를 직접 인용 — #282 리포지토리 선언은 <aggregate>_repository.py 파일(check-transaction-boundary) · #457 선언은 application_layer/port/ 아래뿐·#365 acl 자리(check-port-adapter-pairing) |
| 147 | s005/b21 (62) | 재분류에 의한 트리 밖 port 칸 생성 금지 | Prohibition | `check-usecase-dto-placement.py`·`check-layer-skeleton.py` | `command-dddjango` | ④#182 application_layer 직계는 <area>/·port/ 둘뿐(check-usecase-dto-placement) · #490 BC 안 트리 밖 경로 위반(check-layer-skeleton) |
| 148 | s005/b21 (62) | 규칙4 의 ACL 생략 허가 오용 금지 | Exception | — | `command-dddjango`·`agent-design-review-ddd` | ①문면 «애그리거트 레벨 규칙을 컨텍스트 레벨 결정에 오용 금지» — 컨텍스트 경계 판정은 ddd 설계 lens(§16 기본값 표와 정합) |
| 149 | s005/b21 (62) | BC 배치·ACL 생략의 유비쿼터스 언어·소유 경계 판단 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | 동상 |
| 150 | s005/b21 (62) | 타 BC 참조의 ID 값+ACL/OHS 명세와 BC 경계 ORM FK 금지 | Prohibition | `check-db-table.py`·`check-context-isolation.py` | `command-dddjango`·`agent-design-review-ddd` | ④#631 타 BC 모델을 FK·O2O·M2M 으로 참조 금지(문자열 참조 포함 — check-db-table) · #12 타 BC 접근 경로 한정(check-context-isolation) |
| 151 | s005/b22 (63) | 유스케이스의 연산 객체 명세(트리 39~44행 값 준거·execute 규약) | Obligation | `check-usecase-dto-placement.py` | `command-dddjango` | ④문면이 #635 를 직접 인용 — «#635 클래스 하나·execute 하나·계약 객체 하나 → result»·#190/#193 유스케이스 하나=폴더 하나=진입점 하나 |
| 152 | s005/b22 (63) | 연산 모듈의 공개 자료 클래스 인라인 명세 금지 | Prohibition | `check-usecase-dto-placement.py` | `command-dddjango` | ④#201 자료는 세 파일(_command·_query·_result) · #205 DTO 는 자기 유스케이스 폴더 안에서만 |
| 153 | s005/b22 (63) | dto 낱말 사용 금지 | Prohibition | `check-usecase-dto-placement.py` | `command-dddjango` | ④문면이 #567 을 직접 인용 — «#567 dto 라는 이름을 쓰지 않는다» |
| 154 | s005/b22 (63) | presentation 의 schema_in 변환 한정과 operation 본문 인프라 어댑터 직접 생성 금지 | Prohibition | `check-port-adapter-pairing.py`·`check-composition-root.py` | `command-dddjango` | ④#134 컨트롤러는 build_* 만(check-port-adapter-pairing) · ②composition-root docstring «operation 본문에서 Django…Repository()/…Adapter()를 직접 생성하지 않는다(Q-7)» |
| 155 | s005/b22 (63) | DI 조립의 composition_root 소유와 presentation 매요청 호출 위치 기재 | Obligation | `check-composition-root.py` | `command-dddjango` | ②동 docstring «DI 조립은 BC 루트의 composition_root/ … #84·#85 가 소유» |
| 156 | s005/b22 (63) | domain_bypass_query 채택 여부의 명세 결정 유지 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | ①문면 «명세 결정으로 남긴다» — 채택 판단은 설계 lens(구조 자리 검사는 check-port-adapter-pairing bypass 군이나 채택 여부는 미커버) |
| 157 | s005/b23 (64) | §3.2 규정 준거의 이주·골격 결정 결과 제약 기재 | Obligation | `check-app-container.py`·`check-layer-skeleton.py` | `command-dddjango`·`agent-design-review-ddd` | ②check-app-container docstring «이주 여부는 architect 설계 단계 결정이고(design-architect 판정 소유→구조 배치)»·«architecture-ddd §3.2 항-(2) 2026-06-08 개정» 명시 지목 + ④#486~#490(check-layer-skeleton) |
| 158 | s005/b23 (64) | 이주 지시의 판정 적재 코드 한정 | Exception | `check-app-container.py` | `command-dddjango` | ②동 docstring G2 «이번 변경이 D 에 새 도메인 작업을 더했다» — 한정 축을 검사기가 그대로 집행 |
| 159 | s005/b23 (64) | 데이터소스 실내용 면제의 touched 코드 한정(무관 앱 불이동) | Exception | `check-app-container.py` | `command-dddjango` | ②동상 — «무관 레거시의 단순 수정은 새 마이그레이션이 없어 스킵»(§1.1 존중) |
| 160 | s005/b23 (64) | 애그리거트 1차 폴더명의 ORM 모델명 도출 | Obligation | `check-layer-skeleton.py`·`check-db-table.py` | `command-dddjango`·`agent-design-review-ddd` | ④#632 클래스명 <Name>Model(check-db-table)·#486 골격 존재(check-layer-skeleton) — 파일럿 ddd §3.2 «데이터소스 BC 배치» 동일 축 선례 |
| 161 | s005/b23 (64) | area 부재 BC 의 application_layer 빈 계층 폴더 유지 | Obligation | `check-layer-skeleton.py` | `command-dddjango` | ④#488 고정 칸은 비어도 __init__.py 로 |
| 162 | s005/b23 (64) | 고정·재등장 칸 전부의 빈 패키지 존속 | Obligation | `check-layer-skeleton.py` | `command-dddjango` | ④#488 — 파일럿 ddd §3.2 «고정·재등장 칸의 빈 패키지 존속» 동일 배선 |
| 163 | s005/b23 (64) | test artifact 의 입장 표 승인 행 한정 생성 | Exception | — | `command-dddjango` | §16 기본값 — 입장 심사 승인 판정은 절차(파일럿 ddd 동형 문장도 검사기 미지목) |
| 164 | s005/b23 (64) | 루트 평면·골격 생략의 G1 트레이드오프 상신(명세 자가 결정 금지) | Obligation | `check-app-container.py` | `command-dddjango` | ②docstring — 루트 평면 앱은 결정적 blocker(G1∧G2∧G3)라 명세가 자가 승인할 수 없음 |
| 165 | s005/b23 (64) | touched 데이터소스 앱 루트 평면의 답습 금지 | Prohibition | `check-app-container.py` | `command-dddjango` | ②docstring 회귀 «기존 catalog/ 가 루트 평면 + 새 마이그레이션/판정 적재인데 application/ 로 이주 안 함»이 이 문장의 실증 |
| 166 | s005/b23 (64) | 이주 지시 시 마이그레이션 이력 보존 결과 제약 기재(label·db_table·0001) | Obligation | `check-db-table.py`·`check-mechanism-ownership.py` | `command-dddjango`·`agent-design-review-db` | ④#329 label 명시·#630 «기존 테이블명 보존(개명 강제 아님)»(check-db-table) · #337 파일 이름은 django 번호 꼴·#593 migrations 손편집 금지(check-mechanism-ownership) |
| 167 | s005/b23 (64) | 이주 배타성 결과 제약 기재(옛 루트 migrations 완전 삭제·INSTALLED_APPS 등록 제거) | Obligation | `check-app-container.py`·`check-mechanism-ownership.py` | `command-dddjango`·`agent-design-review-db` | ②app-container G3 «application/ 하위에 D 의 실질 이주 대응 앱이 없다» + ④#336 마이그레이션은 django_<bc>/migrations/ 에 산다 |
| 168 | s005/b23 (64) | 옛 루트 migrations 잔존·MIGRATION_MODULES 지시의 미완 이주 금지 | Prohibition | `check-app-container.py`·`check-mechanism-ownership.py` | `command-dddjango`·`agent-design-review-db` | 동상 — 앱이 두 곳에 존재하는 형태를 두 검사기가 각각 위치·migrations 축으로 문다 |
| 169 | s005/b23 (64) | §10.4 정의 밖 이력 보존 대안의 명세 발명 금지 | Prohibition | — | `command-dddjango`·`agent-design-review-db` | ①문면 «이력 보존 메커니즘은 §10.4가 소유» — 대안 발명 여부는 명세 심사(기계 술어 없음) |
| 170 | s005/b24 (65–66) | BC 가로지르는 단계마다 물음 넷의 답 명세 기재 | Obligation | — | `command-dddjango` | ①문면 «검사기 없음 · G1 설계 판정 · ⓓ»·«기계 술어가 없는 human 판정이라 네 명세가 유일한 기록» — 기본값이 문면 근거를 가짐 |
| 171 | s005/b24 (65–66) | #563 물음 둘에 의한 채널 구분(지시/사실·요청/워커) | Obligation | — | `command-dddjango` | 동상 — check-broker-contract 는 #520·#529·#532 를 ast+ «후보»로만 내고 판정은 명세(docstring ⓓ 후보 exit 불산입) |
| 172 | s005/b24 (65–66) | #526 internal 브로커 통로의 도달 보장 기대 금지 | Prohibition | — | `command-dddjango` | 동상 — #521·#525 는 코드 형태만 물고 «누가 유실을 못 견디나» 판정은 미커버 |
| 173 | s005/b24 (65–66) | #626 받는 쪽이 유실을 못 견디는 자료의 브로커 통로 의존 금지 | Prohibition | — | `command-dddjango` | 동상 — check-missable-entrance #629 는 집합 차 «후보»만 산출 |
| 174 | s005/b24 (65–66) | #626 받는 쪽 cron_job 의 OHS 질의 경로 명세 | Obligation | — | `command-dddjango` | 동상 — ①문면 «경로 실현 여부는 path 검사가 잰다»(실현만 기계·명세는 human) |
| 175 | s005/b24 (65–66) | #530 내구성·백프레셔·재시도 사유의 external 브로커 개설 금지 | Prohibition | — | `command-dddjango` | 동상 — check-broker-contract #529 는 후보 채널 |
| 176 | s005/b25 (67–68) | 각 결정의 왜 한 줄 기재 | Obligation | — | `command-dddjango` | §16 기본값 — 명세 서술 형식 규범(기계 술어 없음) |
| 177 | s005/b25 (67–68) | 로드한 스킬 절 인용에 의한 판단 정당화 | Obligation | — | `command-dddjango` | 동상 |
| 178 | s005/b26 (69–70) | 명세의 일괄 최종 쓰기 금지 | Prohibition | — | `command-dddjango` | ①문면 «파일의 존재·성장이 코디네이터가 볼 수 있는 유일한 진행 신호» — 진행 가시성 판정 주체는 Coordinator |
| 179 | s005/b26 (69–70) | 조사 직후 지정 경로 파일 생성과 절 단위 증분 작성 | Obligation | — | `command-dddjango` | 동상 |
| 180 | s005/b26 (69–70) | 전량 작성 후 전체 일관성 정리와 완료 보고 | Obligation | — | `command-dddjango` | 동상 — 완료 보고 수신자 |
| 181 | s005/b27 (71–72) | 명세의 현재 결정 상태 한정 수록 | Obligation | — | `command-dddjango` | §16 기본값 — 결정 이력은 Coordinator 대화·게이트 배너 소유(문면 지목) |
| 182 | s005/b27 (71–72) | 과거 비교·게이트 이력 서술 금지 | Prohibition | — | `command-dddjango` | 동상 |
| 183 | s005/b27 (71–72) | 축소 대상의 이력 한정(§0 불변식·§3 명명·종류 폴더 범위 불축소) | Exception | — | `command-dddjango` | §16 기본값 — 이 문장의 술어는 «명세 서술의 한계»라 골격 검사기 대상이 아님(§0/§3 실체는 check-layer-skeleton·check-naming 이 별도 규범에서 집행 — 도피 아님) |
| 184 | s005/b28 (73–74) | 영구 테스트 입장 표의 후보별 한 행 판정 | Obligation | — | `command-dddjango`·`agent-design-review-api`·`agent-design-review-db` | ①문면 «lens 무관, 항상 작성» + 병렬 심사판 2종(design-review-api s006·design-review-db 점검 항목)이 입장 표 행을 감사 |
| 185 | s005/b28 (73–74) | 입장 표 최소 열 구성(candidate·protected contract/evidence·unique production failure·existing authoritative coverage·decision·owner/path) | Obligation | — | `command-dddjango`·`agent-design-review-api`·`agent-design-review-db` | ①문면 «다음 최소 열로 한 행씩 판정한다» — 규범 문장의 실주소가 73행이라 §13 «블록 내 문장→Work 대응»대로 b28 에 귀속(적대 리뷰 F6 처분 — 머리행 b29 는 무규범 table-row). 열 구성 심사는 병렬 심사판 2종 |
| 186 | s005/b31 (78–79) | decision 의 일곱 값 한정 | Obligation | — | `command-dddjango` | §16 기본값 — 표 형식 규범(기계 술어 없음) |
| 187 | s005/b31 (78–79) | pending 0 조건의 G1 요청과 reuse·reject 의 test artifact write 0 | Obligation | — | `command-dddjango` | 동상 — G1 요청 가부 판정 주체(command-dddjango s011 «영구 테스트 입장 미확정» 반송 계약과 짝) |
| 188 | s005/b31 (78–79) | retain 무편집과 승인된 의미 보존 재조직의 계약·failure 동일 보호 기록 | Obligation | — | `command-dddjango` | 동상 |
| 189 | s005/b31 (78–79) | remove/weaken 의 종료 근거와 exact target 기재 | Obligation | — | `command-dddjango`·`agent-design-review-api`·`agent-design-review-db` | ①문면 + 심사판 2종이 remove/weaken 행의 종료 evidence·exact target 을 감사하고 미제시 시 pending 반송 |
| 190 | s005/b31 (78–79) | framework/private/test-tool mechanics 의 reject 방향과 migration 파일·과거 state 의 인수 기준화 금지 | Prohibition | — | `command-dddjango` | §16 기본값 — 입장 판정 규범. check-mechanism-ownership 은 migrations 손편집 형태만 물고 인수 기준화는 미커버 |
| 191 | s005/b31 (78–79) | 기존 테스트·현재 구현의 현재 계약 대체 금지 | Prohibition | — | `command-dddjango` | 동상 |
| 192 | s005/b31 (78–79) | 후보 부재 시 열 유지 빈 표와 후보 없음 기재 | Obligation | — | `command-dddjango` | 동상 |
| 193 | s005/b32 (80–81) | 입장 표와 별도의 계약 유지·변경·종료·부재 의무 설명(행 근거 추적성) | Obligation | — | `command-dddjango` | §16 기본값 — 명세 서술 규범 |
| 194 | s005/b32 (80–81) | 순수 구현 버그 수정의 reuse/retain/add 기록과 심사 생략 금지 | Obligation | — | `command-dddjango` | 동상 — «테스트 계약 변화 없음» 생략 차단은 게이트 판정 |
| 195 | s006/b2 (86) | 타당한 리뷰 지적의 해당 절 제자리 반영 | Obligation | — | `command-dddjango` | ①문면 «Coordinator가 독립 리뷰어 노트를 모아 전달하면» — 반영 여부 판정 주체 · §16 기본값 |
| 196 | s006/b2 (86) | 게이트별 메타 요약 블록의 명세 덧쌓기 금지 | Prohibition | — | `command-dddjango` | ①문면 «결정 이력은 Coordinator 대화·게이트 배너가 가짐» — 소유 주체를 문면이 지목 |
| 197 | s006/b3 (87) | 리뷰어 간 충돌의 중재와 결정·근거 명시 | Obligation | — | `command-dddjango` | ①문면 + command-dddjango 문면 «리뷰어 충돌(api↔db 등): architect가 중재해 명세에 결정을 명시한다» — 절차 소유 |
| 198 | s006/b4 (88–89) | 미해소 트레이드오프의 명세 옵션 잔존과 G1 제시 | Obligation | — | `command-dddjango` | ①문면 «Coordinator가 G1에서 사용자에게 제시하게 한다» — 배너 운용 주체 |
| 199 | s006/b5 (90–91) | 완료 인계 전 절 간 자기모순 1회 스캔 | Obligation | — | `command-dddjango` | §16 기본값 — 인계 전 절차 규범(27종 docstring 에 설계 문서 정합 술어 없음) |
| 200 | s006/b5 (90–91) | 발견 모순의 인계 전 해소 | Obligation | — | `command-dddjango` | 동상 — 미해소 시 G1' 설계 반송 판정 주체 |
| 201 | s006/b5 (90–91) | 독립 리뷰어에 의한 자기점검 대체 금지 | Prohibition | — | `command-dddjango` | 동상 — 역할 분담 판정 |
| 202 | s007/b1 (93–94) | 코드 미작성 | Prohibition | — | `command-dddjango` | §16 기본값 — 경계 규범의 준수 판정은 파이프라인 소유(구현 산출은 agent-coder) |
| 203 | s007/b1 (93–94) | 구조·계약·스키마·배치 결정까지의 책임 한계 | Obligation | — | `command-dddjango` | 동상 — 역할 경계 배분 주체 |
| 204 | s007/b2 (95) | 명세에 없는 기능 추가 금지(스코프 고수) | Prohibition | — | `command-dddjango` | 동상 — 스코프 초과 판정은 G0 승인 스코프 소유자(Coordinator). check-idempotency-scope-creep 은 멱등성 산출물 한정이라 일반 스코프 초과는 미커버 |
| 205 | s007/b3 (96) | 한 주제의 단일 lens 소유와 스킬 경계 준수 | Obligation | — | `command-dddjango` | 동상 — lens 배분·경계 판정 주체 |

## 3. 재진술 유예 (교차 문서 — spec 미기입, T3 소급 패스 재료)

브리프 §«재진술»에 따라 **다른 문서 상대는 spec `restates` 에 넣지 않았다**(같은 문서 안 축자 사본 쌍은 0건). 아래는 센서스 restate 열을 직접 확인해 확정한 유예 목록이다.

| # | 사본/병렬 블록(이 문서) | 상대 문서/절(행) | 관계 |
|---|---|---|---|
| 1 | s004/b2 (35행) | `command-dddjango`/s011 (175행 «Contract mismatch 일반(Error response contract 포함)») | STOP 기록·반송 계약 쌍(센서스 Y) |
| 2 | s005/b1 (39행) | `agent-design-review-api`/s006 (56행) | 12-slot 서두 — 작성판↔심사판 병렬 |
| 3 | s005/b2 (41행) | `agent-design-review-api`/s006 (58행) | slot 1 contract scope |
| 4 | s005/b3 (42행) | `agent-design-review-api`/s006 (59행) | slot 2 scope evidence |
| 5 | s005/b4 (43행) | `agent-design-review-api`/s006 (60행) | slot 3 error profile |
| 6 | s005/b5 (44행) | `agent-design-review-api`/s006 (61행) | slot 4 compatibility/rollout |
| 7 | s005/b6 (45행) | `agent-design-review-api`/s006 (62행) | slot 5 common action |
| 8 | s005/b7 (46행) | `agent-design-review-api`/s006 (63행) | slot 6 shape/approval |
| 9 | s005/b8 (47행) | `agent-design-review-api`/s006 (64행) | slot 7 BC error module |
| 10 | s005/b9 (48행) | `agent-design-review-api`/s006 (65행) | slot 8 BC ErrorCode |
| 11 | s005/b10 (49행) | `agent-design-review-api`/s006 (66행) | slot 9 BC ErrorSchema — «required 여도 canon» 문장은 축자 동형 |
| 12 | s005/b11 (50행) | `agent-design-review-api`/s006 (67행) | slot 10 prepared error mapping |
| 13 | s005/b12 (51행) | `agent-design-review-api`/s006 (68행) | slot 11 controller mapping |
| 14 | s005/b13 (52행) | `agent-design-review-api`/s006 (69행) | slot 12 response/OpenAPI/tests |
| 15 | s005/b14 (54행) | `agent-design-review-api`/s006 (71~73행) | framework-owned 오류·인증 실패·406/415·carveout |
| 16 | s005/b18 (59행) | `agent-design-review-db`/s004 (32행) | Risky Write 의미 분류·Consistency Block 충족 심사 |
| 17 | s005/b23 (64행) | `agent-design-review-db`/s004 (35행) | 기존 앱 이주의 `db_table`·`label`·`0001` 보존 결과 제약 |
| 18 | s005/b23 (64행) | `architecture-ddd-final`/s017-3.2 (632~637행 블록군 — 파일럿 기이관) | 판정 소유→구조 이주 항-(1)·항-(2) 정본 참조 |
| 19 | s005/b28·b29 (73·75행) | `agent-design-review-api`/s006 (74행) · `agent-design-review-db`/s004 (36행) | 영구 테스트 입장 표 행 감사 |
| 20 | s005/b31 (78행) | `agent-design-review-api`/s006 (74행) · `agent-design-review-db`/s004 (36행) | remove/weaken 종료 evidence·`pending` 반송 |

**유예 총 20건.** 18번만 상대가 이미 그래프 안(파일럿 이관 완료)이라 즉시 연결이 기술적으로 가능하나, T3-EXECUTION §병렬 설계 «교차 문서 쌍은 전량 유예» 결정에 따라 함께 유예했다.

비-재진술로 판정해 목록에서 뺀 것: 62·63·64행이 `discipline-houserules` final.md §0·§1·§3, `architecture-ddd` §3.3 규칙4, `implementation-django` §10.4 를 가리키는 대목은 **값 소유 인용(준거 지시)**이지 규범 사본이 아니다 — 이 문서의 규범은 «그 규정을 읽고 결과 제약으로 박아라»라는 별개 의무다.

## 4. 경계 판단 메모

- **블록 경계 규약 적용**: 블록 = 내용 행 + 후행 빈 줄(§13 «블록 간 구분자는 선행 블록의 후행 스팬에 귀속»). 절 첫 블록만 헤딩 직후 빈 줄을 선두에 흡수(§13 유일 예외). 도구가 연속·비중첩·전량 커버와 «헤딩+블록 = 절 스팬» byte 등가를 단언했고 exit 0.
- **s001 헤딩**: 무앵커 선두 절이라 headingSnapshot 이 프론트매터 개시 구분자 `---`(1행)다. 블록은 2~14행이며 YAML 키 단위로 분해하되 `skills:` 는 키+목록 6행(5~10)을 한 블록으로 묶었다 — 들여쓴 목록이 키에 종속된 자연 단위이기 때문. 종결 `---`(11행)은 후행 빈 줄과 함께 prose 블록.
- **kind 판정**: 이 문서에 코드 펜스 0·체크박스 0이라 norm/prose/table-row 3종만 썼다. 프론트매터는 펜스가 아니므로 code 가 아니다(§13 «code = 여는 펜스~닫는 펜스 전체 라인»).
- **입장 표(구속 운반체) — 규범 귀속 정정(적대 리뷰 F6 처분)**: 73~81행 표는 머리행(75)·구분행(76)만 있고 데이터 행이 0이다. 초판은 센서스 carriers=`table` 판정을 살리려 «입장 표 최소 열 구성» Work 를 머리행 블록(b29)에 귀속했으나, 그 규범을 **서술하는 문장**(«…다음 최소 열로 한 행씩 판정한다»)의 실주소는 73행이다. §13 «블록 내 문장→Work 대응(문장 등장 순=채번 순)»은 Work 를 **문장**에 매다는 규약이고, 같은 웨이브 전 spec 이 표 머리행·구분행을 예외 없이 규범 0 으로 두었으므로(architecture-ddd s051-8·discipline-cleancode s042-4.3 등 — 규범은 데이터 행이 진다) 머리행 단독 귀속은 판형 이탈이다. 따라서 #184·#185 를 모두 b28(73~74행)에 귀속하고 b29(머리행)·b30(구분행+빈 줄)은 **무규범 table-row 블록**으로 남겼다. 블록 자체는 그대로 남아 carriers=`table` 의 실물 근거(열 이름의 «값»을 운반)와 byte 등가는 불변이고, §13 «계수 2축에서는 데이터 행만 산입» 관례와도 충돌하지 않는다.
- **들여쓴 하위 문단**: 78·80행은 `- **영구 테스트 입장 표**` 불릿의 연속이지만 빈 줄로 끊긴 별개 문단이라 각각 norm 블록으로 분해했다(마커·들여쓰기 포함 verbatim).
- **문서 내부 부분 중복 — restates 미부여**: 58행 Controller 문장군 ↔ 51행 slot 11, 58행 «internal failure/output 구분» ↔ 50행 slot 10, 62행 «신규 산출물 한정» ↔ 58행 처분-권한 한계는 의미가 겹친다. 그러나 `djr:restates` 는 **블록 단위 사본 관계**이고 이들은 블록 전체가 사본이 아니라 부분 중첩이라 각각 Work 를 채번했다. 정본/사본 승격은 T3 소급 패스의 판단 재료로 남긴다.
- **배선 기본값의 정당성**: 이 문서의 규범은 대부분 «설계 명세에 무엇을 박는가»이고, `check-*.py` 27종 docstring 전수 실독 결과 **design-spec 문서를 읽는 술어를 가진 검사기는 없다**(check-idempotency-scope-creep 만 G1 채택 배너 문자열을 면제 조건으로 읽는다). 따라서 §16 위임 기본값 표의 «command+agents(절차 층) → `command-dddjango`»가 정당한 기본값이다.
- **기본값 이탈(enforcedBy 병기) 근거 3계열**:
  1. **검사기 docstring 이 design-architect 를 명시 지목** — `check-app-container.py`(«이주 여부는 architect 설계 단계 결정이고(design-architect 판정 소유→구조 배치)»), `check-idempotency-scope-creep.py`(«미요청 멱등성 금지 가드는 이미 design-architect(§9.6 Idempotency storage 행)에 산문으로 있으나»), `check-transient-overmapping.py`(«② design-architect 생산자 예방»). §16 «역도 성립» 조항상 이 셋을 기본값으로만 두면 오배선이다.
  2. **문면이 규칙 번호를 직접 인용** — #633(OHS 인자 1개→check-context-isolation), #635·#567(→check-usecase-dto-placement), #282(→check-transaction-boundary), #365·#187(→check-port-adapter-pairing), #631(→check-db-table), #119(framework 소유→check-business-vocabulary), #85(→check-composition-root).
  3. **§16 역할명→검사기 매핑 표** — «schema checker»=`check-error-centralization.py`(slot 5~9), «controller checker»=`check-api-error-controller-contract.py`(slot 10·11·58행), «OpenAPI checker»=`check-openapi-error-declaration.py`(slot 12·54행). 성공 응답 축은 `check-response-schema-bypass.py`, 406/415 축은 `check-ninja-boundary-middleware.py` 가 docstring 문면으로 확정된다.
- **기본값 유지를 문면이 지지하는 자리**: 65행 «BC 가로지르는 채널»은 문면 자체가 «검사기 없음 · G1 설계 판정 · ⓓ»·«기계 술어가 없는 human 판정이라 네 명세가 유일한 기록»이라고 못박는다. `check-broker-contract`(#520·#529·#532)·`check-missable-entrance`(#629)는 ast+ **후보**만 내고 exit 에 불산입하므로 enforcedBy 를 달지 않았다 — 도피가 아니라 문면 근거를 가진 기본값.
- **preserve-established 계열 규범의 배선**: profile-gated 검사기 4종은 preserve 실행에서 «add no new error-mapping semantics»라 preserve 쪽 의무를 집행하지 않는다. 그래서 preserve 문장들은 enforcedBy 없이 `command-dddjango` + `agent-design-review-api` 로만 위임했고, basis 에 «검사 공백»임을 명시했다(도피와 구분).
- **lens 리뷰어 병기**: 12-slot·계약(api)·데이터(db)·도메인(ddd) 축은 상대 문서(`agent-design-review-api`/`-db`/`-ddd`)가 같은 항목을 심사판으로 갖는 것이 문면·센서스로 확인돼 `delegatedTo` 에 병기했다. 절차·형식·게이트 규범은 `command-dddjango` 단독이다.
- **오배선 회피 기록**: 42행 «inventory 와 표준 트리의 불일치는 이동 지시가 아니라 관찰 기록»과 58행 «승인 스코프 밖 기존 파일 처분 금지»는 표면상 트리 규범이지만, 기존 배치 **처분 권한**은 G0 빚 결정 소관이라 `check-layer-skeleton`/`check-app-container` 로 배선하면 반대 의미가 된다 — 기본값 유지.
