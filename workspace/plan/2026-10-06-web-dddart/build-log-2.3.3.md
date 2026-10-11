# 2.3.3 짓기 기록 — dddjango-web 2.3.3 (판 확인 지문은 조정자가 정해진 두 자리에서만 · 역할은 재지 않는다)

- 시작 10-11(KST) · 구현자 Codex · 바탕 R main `0e4561bb`(web 2.3.2) · 사본 `<S>/web-sha-1` · 결정 · 판정 · 넣은 것: `plan-2.3.3.md` · 정본 설계 `<S>/sha-rule/design-v2.md` · 배경 점검 `check-v1-codex.md` · `check-v1-claude.md`.
- `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`.
- 목적: 역할의 입력 판 지문 재계산과 지문 영수증을 끊고, 조정자가 배너와 답 받음에서 작업 트리 명세 바이트를 대조해 승인 판을 확인한다. 지금 판과 다른 승인은 받지 않고 지금 판으로 다시 묻는다.

## 진행
- 설계 v2를 끝까지 읽고 v1의 Codex·Claude 점검 기록을 모두 읽었다. v1 점검의 차단은 배너 전 커밋/`pre_run_head` 이동 · 작업 트리 명세를 놓치는 비교 · 조건부 승인 재해석 · 플랫폼 문장 불일치였다. v2는 커밋 흐름 변경을 빼고 직접 파일 바이트 대조와 같은 글자로 닫는다.
- 결정 27: 일꾼은 지문을 재지 않는다. 결정 29(10-11 «가.»): 지문으로 묶인 답을 조정자가 받는 자리에서 현재 명세 지문을 한 번 재 대조한다 — 같으면 승인, 다르면 지금 판으로 재질문. 배너 직전 계산과 합쳐 두 자리만 둔다.
- 바탕 확인: 사본 HEAD는 `0e4561bbb009c822a2ab64873b6bfe5ef6adc44e`, 시작 작업 트리의 변경은 없었다. `docs/DEVELOPMENT.md`와 앞 판 `plan-2.3.2.md` · `build-log-2.3.2.md`의 꼴을 확인했다.
- 구현: E1 · E2는 두 Coordinator의 지정 자리, E3은 역할 7쌍의 config 경계 줄 뒤, E4는 discipline 0T 감수 구절, E5는 두 REQUEST_GUIDE에 넣었다. 새 문장은 설계 원문과 두 플랫폼 같은 글자로 두고 coder-web 덧붙임은 같은 줄 끝에 붙였다.
- `verify-web` 문단 대조에 표지 둘을 더하고 역할 7의 `grep -F`·`cmp` 고리를 이어 붙였다. AGENTS.md의 web 단락에 2.3.3 규칙 한 문장을 더했다. 판 올림과 봉인은 운영자 몫이다.

## 근거 측정
- `<S>/sha-rule/design-v1.md` §0이 `webspeed-1011/report.md` §5~§11에서 인용한 값: 지문 걸음 2,896 / 51,760 · 17.7h / 164.6h(10.8%) · 6-3-13 명세 지문 확인 822 걸음/6.3h · 기록 변조 발동 0 · web 끝 보고 대조 9건 불일치 0.
- 원 측정은 이번 사본에서 다시 실행하지 않았다. 효과 판정은 설계 v2의 A1/B1/N1 기준으로 별도 확인하며 시간 회수 비율은 추정하지 않는다.

## 바꾼 자리
| 묶음 | 파일 | 내용 |
|---|---|---|
| E1 · E2 | Claude Coordinator · Codex Coordinator | 명세 sha 배너/답 대조 · 두 자리 경계 |
| E3 | Claude 역할 7 · Codex 역할 SKILL 7 | 입력 판 확인 계산 금지 · coder 지문 영수증 금지 |
| E4 | discipline-reviewer-web 두 벌 | 0T 도구 기록을 읽어 대조 · 재계산 금지 |
| E5 | REQUEST_GUIDE 두 벌 byte 미러 | 배너의 지문을 옮겨 적는 승인 안내 |
| 검증 | Makefile | 문단 표지 2 · 역할 7 줄 대조 |
| 문서 | 계획 · 이 기록 · AGENTS.md | 목적 · 근거 측정 · 결정 27/29 · 변경 자리 · 검증 칸 |

## 보완(운영자 · 사본 `<S>/web-sha-2` — web-sha-1 의 복제)
- 설계 v2 Claude 재점검(`<S>/sha-rule/check-v2-claude.md` · 차단 0 · 중요 4) → `8de06bca`: 대조는 그 배너의 명세 승인 답만 · SDK 지문 · `candidate_token` · 출처 커밋은 명세 판 지정이 아님 · 같은 배너의 다른 문항 답은 다시 재지 않음 · 소문자 대조 · `G1'` 도 같음 · 대조할 배너 줄이 없으면 판정 불가 → 배너 다시 냄 · 경계 도구 목록에 백스톱 · 시험 명령 · SDK 임시 사본 재해시(dry-run 몫) · discipline 0T 감수 증거는 받은 `evidence.json` · coder «git이면» · Makefile 에 discipline 0T 줄 대조. 봉인 chore `e18fc247`.
- 구현 검토 둘(`<S>/sha-rule/review-impl-codex.md` · `review-impl-claude.md` · 모두 보완 후 배포 · 차단 0) → `45a3756d`: «배너 줄 없음» 판정 불가를 지문 없는 승인으로 한정(Codex I1) · 다시 낸 배너도 그 값으로 `G1 배너:` 줄을 새로 적고 배너 행은 지금 명세에서 다시 뽑음(Claude I1 — 지문 없는 «승인» 끝없는 재질문 차단) · `g1_decisions` 스키마 · 갱신 시점에 배너 · 승인 판 줄 · 이미 받은 명세 승인의 되풀이는 다시 재지 않음 · 지문 명령 둘 다 없으면 `python3` `hashlib` · 0T 복구 증거 = 도구가 되돌린 뒤에만 쓰는 `evidence.json` · AGENTS.md 정본 목록. 봉인 무변(`--check --draft` green).
- 리팩토링 «상시 답»(Claude `:330`)의 «받지 않은 답에는 적지 않음» 구는 self-test 표지 구간이라 넣지 않았다(Claude 구현 검토 N4 · 뒤 절이 앞 절을 대체해 실해 작음).

## 검증
| 실행 | 결과 | 증거 |
|---|---|---|
| `python3 workspace/tools/request_guide_contract.py` | PASS | `45a3756d` 운영자 실행 |
| Makefile 문단 대조 · 새 역할 cmp 고리 · discipline 0T 줄 | 같음(문단 14 · 역할 7 · 0T 1) | `make verify-web` 안 |
| Claude·Codex `refactor_audit.py --self-test` | 둘 다 red 0(점검 절 106 · 어구 27 · 극성 표본 18) | 운영자 실행 |
| `make verify-web` 전체(`45a3756d`) | rc 0 · 15:03:36 ~ 15:24:26 | `<S>/sha-rule/verify-web-3.log` |
| `make verify`(`45a3756d`) | 6/6 green · 598초 | `<S>/sha-rule/verify-3.log` |
| 봉인 | `c2688d66`(93bdbf7a 뒤) · `e18fc247`(8de06bca 뒤) · 45a3756d 뒤 `--check --draft` green | 운영자 실행 |
| 독립 검토 | 설계 v2 재점검(Claude) 차단 0 · 구현 검토 Codex · Claude 차단 0 — 중요는 위 보완으로 닫음 | `<S>/sha-rule/` |
| A/B · 음성 | 아래 표 — 모두 통과 | `<S>/sha-ab/out/` |

## A/B 결과(같은 `snapG1` · Codex gpt-6.1-sol xhigh · 시험대 스킬 사본 · 설치본 끔)
| 갈래 | 판 | 보낸 답 | 결과 | Hw | Hc(자리마다) | 승인 줄 · 진행 |
|---|---|---|---|---|---|---|
| A1 | 옛 2.3.2 | 64자 지문 승인 | 재현 유효 · 1277초 · 에이전트 29.8분 | **6** | 2 | G2 |
| B1 | 93bdbf7a | 64자 지문 승인 | 통과 · 1296초 · 25.6분 | 0 | 1 | `G1 승인: 명세 sha e30c513f04fd` · 4 슬라이스 · 시험 61 passed · 구조 검사 blocker 0 |
| N1 | 93bdbf7a | 명세 한 줄 몰래 바꾼 뒤 옛 지문 | 통과 · 78초 | 0 | 1 | 승인 줄 0 · 일꾼 0 · 지금 판 `1b3f57592655` 로 다시 물음 |
| B1b | 45a3756d | 64자 지문 승인(옛 판 배너 · 배너 줄 없음) | 통과 · 1915초(N1b 와 동시) | 0 | 1 | `G1 승인: 명세 sha e30c513f04fd` · 다시 묻지 않음 · 시험 95 passed · blocker 0 |
| N1b | 45a3756d | 1턴 옛 지문 → 2턴 «G1 승인.»(지문 없음) | 통과 · 78초 + 1824초 | 0 | 턴마다 1 | 1턴 승인 줄 0 · `G1 배너: 명세 sha 1b3f57592655` 줄 · 2턴 `G1 승인: 명세 sha 1b3f57592655` · 다시 묻지 않음 · 시험 78 passed · blocker 0 |
- 기준(실행 전 고정): `plan-2.3.3.md` «A/B 판정 기준» · 2차는 `<S>/sha-ab/criteria-round2.md`. Codex 과제 글은 암호라 R(평문)은 잴 수 없어 Hw · R_use(일꾼이 스스로 쓴 글의 지문) 0 으로 판정했다. A1 은 일꾼 10/10 이 부모 대화를 물려받아 승인 지문을 이미 본다(R_inh — 규칙으로 못 막음).
- 받는 자리의 한 번은 복합 명령이라 측정기가 «도구 실행 안 · 셈 밖»으로 분류한 경우가 있어 원문으로 셌다(B1 · B1b · N1b 2턴).
- 시간은 n = 1 · 일꾼 수가 달라 참고만 — 이 작은 일감에서는 지문 계산 시간이 원래 짧다. 확인한 효과는 «일꾼 지문 재계산 6 → 0» 이다. Claude 판 C1(옛 판 · 참고)은 사용자 터미널에서 돈다.

## 커밋
| 커밋 | 내용 |
|---|---|
| `93bdbf7a` | E1~E5 런타임 글 · Makefile 대조 · AGENTS.md |
| `c2688d66` | 봉인 chore |
| `8de06bca` | 설계 v2 재점검 보완 |
| `e18fc247` | 봉인 chore |
| `45a3756d` | 구현 검토 보완 |
| 이 문서 커밋 | 계획 · 이 기록 |
| `make release-web` | 판 올림 · 태그 · Release |

## 안 한 것 · 남은 것
- references · scripts · plugin.json · build-state 스키마 · `pre_run_head` · Phase 2 진입 · G2는 고치지 않았다. git 쓰기 · `manifest_seal` · 릴리즈를 실행하지 않는다.
- 이번 구현 검증은 브라우저 없이 가능한 범위만 한다. git 쓰기를 실행하는 임시 저장소 픽스처와 Chrome·브라우저 시험, `make verify-web` 전체는 운영자가 돌릴 것. 검증 결과 칸은 요청대로 비워 둔다.
- 설계 v2 §5의 A/B 실행과 측정 스크립트 변경은 이 구현 범위 밖이며 효과 측정은 아직 없다. 재현 실패/후보 실패/음성 갈래 실패 처분은 계획의 판정 기준을 따른다.
- 작업 폴더 밖 보고 파일 `sha-rule/impl-report.md`는 쓰지 않고 최종 답에 구현 보고를 남긴다.
