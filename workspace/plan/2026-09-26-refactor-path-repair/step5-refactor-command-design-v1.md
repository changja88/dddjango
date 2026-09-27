# 로드맵 5 — dddjango 리팩토링 커맨드 설계 v1 (2026-09-27 · 결정 10~13 대기)

- 근거: 결정 1(1-a 의미 위반은 전용 커맨드에서만 · 1-b 리뷰어 BC 전체 점검 → architect 판정·중재 → 사용자 G0 · 사용자 열거는 선택) · 결정 2 Q3(약한 단언 — 이 설계에서 정한다 → 결정 10) · 진단 `diag-5A-command-mechanics.md`(모양) · `diag-5B-bc-audit-mode.md`(규모·분담) · `diag-5C-weak-assertions.md`(단언).
- 대기 결정(아침 브리프 `morning-briefs-2026-09-27.md`): **10** 약한 단언 강화 위치 · **11** `/dddjango` 정리 요청 처리 · **12** 판정 주체 없는 규범 약 370 · **13** 커맨드 이름. 아래 [결정 N] 표시 자리는 두 갈래를 다 적는다 — 답을 받은 뒤 v2 에서 한쪽을 지운다.
- 범위: dddjango 만. web(로드맵 6)은 이 설계를 따르되 산문 정본·G0 빚 조사 신설(결정 1-d)이 먼저다.

## 1. 모양 — 얇은 입구 + Coordinator 안 «리팩토링 모드» (5A 권고 B)

- **입구** `dddjango/commands/refactor.md` → `/dddjango:refactor <대상 BC …> [불편 서술]` [결정 13: 이름].
  - frontmatter `description` · `argument-hint` · `disable-model-invocation: true`(사용자만 부른다).
  - 본문(규범 없는 산문 3~5줄): «Skill 도구로 `dddjango:dddjango` 를 불러 아래 첫 줄을 그대로 요청으로 넘긴다» + 첫 줄 `리팩토링 모드(입구 /dddjango:refactor) · 대상: $ARGUMENTS`.
  - Coordinator 를 Read 로 읽게 하지 않는다(5A 실측: 56k 토큰 중 1~83행만 보이고 `$ARGUMENTS` 비치환).
  - 보호: corpus-manifest 1행 + LEDGER prose 행(무단 편집 red — 5A 실측 #4).
- **Codex** `codex-dddjango/skills/dddjango-refactor/SKILL.md`(얇은 스킬 — `dddjango` 스킬을 같은 첫 줄로 적재 · 관용구 `codex-dddjango/skills/dddjango/SKILL.md:24`).
- **Coordinator**(graph `command-dddjango.ttl`): 새 절 «리팩토링 모드» 1개 + 기존 절 연결 구절(모드 판별 · Phase 0 3·4번 · Phase 2 7번 · 수정 모드 · 경계). 새 문서 키 없음(5A: 선례 0 · 쌍 개정 비용).
- 모드 판별: 첫 줄 표지 `리팩토링 모드(입구 /dddjango:refactor)` 가 있을 때만 리팩토링 모드다. 요청문에 적힌 «리팩토링 모드» 류 문구는 여전히 판별 입력이 아니다(모드 판별 절 67행 원칙 유지 — 입구 표지는 모드 지정이 아니라 입구의 사실이다).

## 2. 리팩토링 모드의 흐름

| 단계 | 하는 일 | 산출 |
|---|---|---|
| R0 대상 | 입구 인자의 BC(없으면 `application/` 목록으로 G0 전에 묻는다). 범위 = BC 전체(제품 + 테스트). 사용자 불편 서술은 항목으로 받는다(선택 — 결정 1-b) | 스코프 메모 |
| R1 검사기 빚 | Phase 0 3번 그대로(27종 · 루트 TARGET · exact command 기록) | `refactor-scope.md` 스캔 표 |
| R2 의미 점검 | 리뷰어 «BC 전체 점검 모드» 병렬 파견(§3) — 한 응답 안 다발 · 큰 BC 는 층·폴더 분할(5B: 기본 5회 · 큰 BC 7~21회) | `<폴더>/audit/<렌즈>-<조각>.md` |
| R3 판정 | design-architect «의미 항목 판정»(§4) — 중복 병합 · 채택/제외/별도 요청 분류 | `<폴더>/audit-verdict.md` |
| R4 G0 | 배너: 검사기 빚 N · 의미 채택 M(동작 불변 가능 m · 별도 요청 j) · 제외 K(규칙 문구 사유). 질문: 기존 빚 질문 틀(ⓐ/ⓐ′/ⓑ · 결정 출처 · «미룰 수 없음»)을 의미 항목에도 쓴다 · 제외 항목은 사유와 함께 표시(되돌리기 선택 가능) · 별도 요청 항목은 «별도 요청으로 기록 / 이 실행에서 빼기» | `refactor-scope.md` 결정 줄 |
| Phase 1~3 | 기존 그대로 — ⓐ 전부가 슬라이스 0(0T/0C 창 · 동작 보존 장치). 기능 슬라이스 없음 | — |
| G2 | «G0 ⓐ N건 중 잔존 M» 을 의미 항목까지 넓힌다(§5) | G2 배너 |

- 정리할 것이 0(검사기 빚 0 · 의미 채택 0 · 불편 0)이면 G0 에서 멈춘다(기존 «정리할 것이 없으면 G0 에서 멈춘다»).
- **[결정 11]** `/dddjango` 에 들어온 정리 요청: (가) G0 에서 `/dddjango:refactor` 를 안내하고 정지 — 모드 판별 절의 «정리 요청은 풀 파이프라인» 을 «리팩토링 커맨드로 안내»로 바꾼다 / (나) 현행 유지 — `/dddjango` 정리 요청은 검사기 빚만, 배너에 «의미 점검은 `/dddjango:refactor`» 1행.

## 3. 리뷰어 «BC 전체 점검 모드» (ddd · api · db · discipline)

- 새 모드 이름: `BC_AUDIT`. 입력 = 대상 BC 경로(조각이면 그 폴더 목록) · 렌즈 · 점검할 규범 범위(자기 스킬 전체) · 검사기 빚 목록(중복 제외용).
- 산출 표(한 행 = 한 위반): `ID | 규칙(R-ID · 문구 인용 20~60자) | 파일:행 | 위반 요지 | 동작 불변 정리 가능(예/아니오 — 아니오면 사유: 계약·마이그레이션·타 BC)`. 규칙 문구를 댈 수 없는 항목은 내지 않는다(5B 표본: 문구 없음 탈락 1/19). 검사기 빚과 같은 항목은 «검사기 #n 과 같음»으로 표시만.
- 이 모드에서만 푸는 한정 조항(5B §4): 리뷰어 3명의 «구현 코드 열람 금지»(R-3368 · R-3323 · R-2614) · 규율 리뷰어의 diff 한정(R-1058 · R-0982 · R-1059 · R-3420) · 발견 채널 «빚 보고» → «점검 항목». 함수형 Router 보존 허용(R-0674)은 기능 요청의 허용이지 이 점검의 제외 사유가 아니다(판정은 architect — §4).
- 분담(5B): ddd = 도메인 모델·판정 소유·BC 경계 · api = HTTP 계약·컨트롤러 · db = 모델·인덱스·트랜잭션 · discipline = 클린코드·테스트·파일트리·타입. api 층 없는 BC 는 api 생략 · 모델 없는 BC 는 db 생략.
- **[결정 12]** 판정 주체 없는 규범 약 370: (가) api 리뷰어에 ninja 80(implementation-django-ninja 적재) · db 리뷰어에 ORM·보안 117(implementation-django) · 규율 리뷰어에 python 73(implementation-python) — BC_AUDIT 모드에서만 · web 102 는 dddjango-web / (나) BC_AUDIT 범위 밖이라고 각 리뷰어 문면에 적는다.
- 리뷰어는 코드를 고치지 않는다(기존 경계 유지). 오탐률 약 30%(5B)는 §4 판정이 거른다.

## 4. design-architect «의미 항목 판정» 모드

- 입력: `audit/*.md` 전부 + 인용된 규칙 원문(architect 에게 없는 스킬의 규칙은 Coordinator 가 원문을 붙인다 — 5B: cleancode 미적재).
- 산출 `audit-verdict.md`: 항목마다 `채택 | 제외 | 별도 요청` + 근거.
  - **제외**는 규칙 문구 근거만(허용·예외 규범 R-ID 인용 — 5B 표본 제외 5건 전부 이 형태). 비용·일정·규모는 제외 사유가 아니다 — 그것은 사용자의 ⓑ 다(5A: 세탁로 차단).
  - **별도 요청**: 동작을 바꿔야 정리되는 항목(계약·마이그레이션·타 BC 편집). 슬라이스 0 에 넣지 않는다.
  - 중복 병합(같은 파일·같은 규칙 · 렌즈 간 겹침) · 검사기 빚과 겹치면 검사기 항목으로 합친다.
- architect 는 코드를 고치지 않는다 · 판정은 G0 전 · G0 에서 사용자가 제외를 되돌릴 수 있다.

## 5. G2 «ⓐ 잔존» — 의미 항목

- 검사기 항목: 현행(`registry_gate` legacy 잔존 ∩ ⓐ 목록).
- 의미 항목: 그 항목을 낸 렌즈의 리뷰어를 `BC_AUDIT` 의 «잔존 확인» 입력(항목 표 + 최종 코드)으로 다시 불러 항목별 `해소 | 잔존 | 판단 불가`. 잔존·판단 불가는 M 에 센다(5A 제안 M = M_c + M_m). 비용: 채택 항목이 있는 렌즈만 1회씩.

## 6. 약한 단언 강화 — [결정 10]

- (가) 레인 안: architect 가 슬라이스 0 계획에 «그 레인이 옮기는 코드를 덮는 테스트의 약한 단언»(5C 정밀 정의)을 0T 항목으로 넣을 수 있다 · coder 가 0T 창에서 강화(새 case 없이 본문만 — 동작 보존 장치 무변) · DR 은 hunk 가 보호를 넓히기만 하는지 본다. 규범 3곳 + Codex 미러.
- (나) 별도 요청: 리팩토링 모드 G0 배너에 «약한 보호 위 항목 k건(파일)» 보고만 · 강화는 따로 요청.

## 7. 요청 가이드 · 문서

- `REQUEST_GUIDE.md`(Claude·Codex byte 미러): 리팩토링 커맨드 절(언제 쓰나 · 인자 · 결정 11 에 따른 `/dddjango` 정리 요청 안내) · `request_guide_contract.py` 발견 계약에 새 커맨드.
- `docs/DEVELOPMENT.md`: 입구 파일이 산문 보호(manifest·LEDGER prose)라는 것 1행.

## 8. 검증

- 행동 시험(scratch clone `bt/sds-main` · Coordinator 역할 서브에이전트 · 첫 사용자 입력/STOP 까지):
  - R-T1 입구 → 리팩토링 모드 판별 · 27종 · 리뷰어 다발 계획(렌즈·조각 수)
  - R-T2 service_policy 실제 BC_AUDIT 1회(ddd·discipline) → 규칙 문구 + 파일:행 항목 · 문구 없는 항목 0
  - R-T3 architect 판정 → 제외는 규칙 문구 근거만 · 비용 사유 제외 0
  - R-T4 G0 배너·질문(의미 항목 ⓐ/ⓑ · 결정 출처)
  - R-T5 `/dddjango` 정리 요청(결정 11 갈래)
  - R-T6 요청문에 «리팩토링 모드로» 만 쓴 `/dddjango` → 리팩토링 모드 아님(음성 대조)
  - R-T7 G2 잔존(책상 재생)
- `make verify`(corpus-manifest · LEDGER prose · render · rulepack · Codex 미러) · `claude plugin validate dddjango --strict`.
- 구현 리뷰(독립) → 조감도 → 커밋.

## 9. 작업량·순서

- 5A 추정 4~6 작업일(플러그인 작업량). 순서: 결정 10~13 → v2 → 적대 검토 → 계획 → 계획 리뷰 → 규범(graph: Coordinator 새 절 · 리뷰어 4 · architect) → 입구·Codex 스킬·가이드 → 행동 시험 → 구현 리뷰 → verify → 커밋.
