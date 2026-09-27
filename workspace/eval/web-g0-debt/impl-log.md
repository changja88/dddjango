# 로드맵 6a 구현 기록 — dddjango-web 기능 요청 G0 빚 처리 (2026-09-27)

- 설계 정본 `design-v5.md` · 계획 `plan-v2.md` · 행동 시험 `behavior-tests.md` · 구현 리뷰 `review-Q-impl.md`.
- 사용자 구현 승인 2026-09-27(«승인 — 구현 시작»). 기준 HEAD `75645801`. 작업 트리에서 구현했다(브랜치 커밋 없음).
- 기준선: `make verify-web` green(픽스처 13파일 · 87초) · 현장 재생 사본 `spring_dream_server` `072253e8` (`git clone --shared` — 원본은 clone 읽기만).

## 1. 무엇을 바꿨나

| 몫 | 내용 |
|---|---|
| 러너 | `scripts/src/debt.py` 신설(우주 `git ls-files -co --exclude-standard` − 작업 트리 부재·바이트코드 · `DEBT_EXEMPT` 3종 · 키 `(검사, 경로)` · `C<n>` · JSON · `refactor-scope.md` 절 파서 · 잔존 M) · `backstop.py --debt-scan [--json]`·`--debt-residual <폴더>`(단독 모드 · 배타 위반 exit 1) · `common.py` `_project_pkgs`·`BackstopContext.from_files` · `check_purity.py` WP1 중복·WP2 async/defer 사유 상수 + 사유 끝 ` — <src 경로>` |
| 결정 16 | `current_nondesign_scope` — 과거 빌드 상태 루프·«다른 폴더» 변경 조건 제거, `config.json` 변경 조건만 · 알림 «과거 시안 빌드 N개의 visual 검사 생략(판정 입력 아님)» · `test_design_evidence.py` 반전(7 subtests + `stopped-folder`) |
| 픽스처 | `fixtures_debt.sh` 43 단언(D1~D18 — 계획 1~17 + 비git 실행 불능 D18 · dirty 판정 D1b/c · 폴더 경로 안전 D13f) |
| Coordinator | 68건 — 모드 판별(정리 요청 입구 정지 · 의미 정리 1행 · 불인정 지시) · Phase 0 질문 순서 · step 1 dirty `.dddjango-web/` 제외·비git 대가 · **step 4′**(스캔·단위·빚 목록·요구 키·개명·이동 묶음·빚 질문·결정 출처·충돌·dirty+ⓐ·기록 정형·G0 정지) · step 6 빚 1행 · Phase 1 architect 입력·DR 필수·재상정 STOP·G1 배너 앞 단위 확인 · Phase 2 ⑤ add 범위·슬라이스 0(`slices[0]`·끝 green 셋·참조 완전성)·반송 재승인·`--debt-residual`(M>0 G2 미제시)·G2 빚 3행 · Phase 3 재실행·합치기 보고 · 수정 모드 4′·G1′ 앞 확인·ⓐ 있으면 G1′ 생략 금지·`:219` · 트리비얼 ⓪ 스캔·승격 · 재개 입구 · 경계(위임 불가) · 라벨 14행 · 유령 `backstop-baseline.json` 3곳 · 산출물 위치·직접 쓰기 목록 · build-state `slice-0-debt` |
| 에이전트 4 | architect(입력·슬라이스 0 절) · coder(입력·슬라이스 0 집행·오탐 보고) · DR(경량 모드 슬라이스 0 점검 2항) · review(점검 11 슬라이스 0 절) |
| 스킬·가이드 | houserules SKILL §1 1번·§2·§4(«레거시는 빚» · 브라운필드 허용 규범 · «이동» 정의) · final §7(빚 모드) §8 · design-evidence(결정 16) · REQUEST_GUIDE §4·§6·§7·§8 |
| Codex | scripts byte · final·design-evidence·REQUEST_GUIDE byte · Coordinator 의미 미러(같은 68건을 Codex 표기로 변환 — `${SKILL_DIR}`·네이티브 셸·`request_user_input`·`$dddjango-web-refactor`) · 역할 SKILL 4 · houserules SKILL |
| 기타 | `Makefile` verify-web houserules final `cmp` · `AGENTS.md` 러너 플래그·verify-web 경로 문장 |

## 2. 계획 대비 편차

- 요약 1행을 `스캔 파일 f` 로 적었다(계획 `파일 f` — 발견 파일 수와 헷갈리지 않게 스캔 우주 크기임을 밝힘).
- 트리비얼은 폴더 유무와 무관하게 `--json` 을 쓰지 않는다(설계 «폴더가 없으면 JSON 없이»의 단순화 — 빚 ≥1 이면 어차피 수정 모드로 승격해 step 4′ 가 동결한다).
- 라벨 14행 교체에 딸려 ⓕ 를 가리키던 `:9`·`:180`·houserules final `:104`·`:211` 도 `(6)` 으로 고쳤다(계획 목록 밖 · 일관성).
- REQUEST_GUIDE §6 의 «동작 유지 정리» 예시를 걷었다 — 이제 입구 정지 대상이다. 입구 사용법 문단은 6b 가 쓴다.
- `AGENTS.md` 의 «`make verify` 의 `verify-web`» 문장은 09-16 자동 경로 제외 뒤 낡은 문장이라 함께 고쳤다.
- 픽스처는 계획 1~17 에 D18(비git) 등 3건을 더했다(러너 신설 계약의 exit 1 경로 고정 — 테스트 보강이 아니라 새 러너의 계약 픽스처).

- **행동 시험 뒤 문면 수정 2건**(양 런타임): ① W-T1 1차 불합격 → step 4′ 빚 질문에 «질문 도구가 없으면 같은 선택지와 대가를 평문으로 내고 이 턴을 끝낸다 — 뒤 단계 질문과 묶지 않는다» · «빚 답(빚 0이면 그 확인)을 받기 전에는 step 5를 시작하지 않는다» · step 5-1 «step 5의 맨 먼저 — step 4′ 빚 답 뒤» (재시험 합격) ② Codex 시험의 ⓐ′ 오제시(빚 단위 1인데 슬라이스 0 규모 «3단위»를 빚 단위로 읽음) → ⓐ′ 조건을 «빚 목록 키의 경로가 속한 단위가 2개 이상 — 개명·이동 참조 파일 단위와 슬라이스 0 규모의 단위 수는 세지 않는다»로 명시.

## 3. 검증

- `fixtures_debt.sh` 43/43 · `run_fixtures.sh` 14파일 실패 0 · `test_design_evidence` 33 OK(옛 테스트로 돌리면 `:646` 7 subtests 만 실패 — 계획 §3 대조 일치).
- 현장 사본 `--debt-scan`: 키 3(WN8 `static/images` 3건) — 검토 W3 원형 `sds.g0.json` 과 같다.
- `make verify-web` green(1분 43초) · `claude plugin validate dddjango-web --strict` 통과 · 토큰 11종 Claude/Codex 수 일치.

## 4. 구현 리뷰 Q 처분 (`review-Q-impl.md` — 수정 후 승인 · blocker 1 · major 3 · minor 10)

| Q | 처분 | 반영 |
|---|---|---|
| B1 git 이 web/ 을 못 보면 «빚 0» fail-open | 수용 | `debt_universe`: `web` 심볼릭 링크 → exit 1 · git 우주가 비었는데 web/ 에 실재 파일 → exit 1 · 픽스처 D19a·b(+ 대조 c) |
| M1 첫 실행(web/ 부재)이 G0 blocker | 수용 | git 확인 뒤 web/ 부재면 빈 우주 · `[info] web/ 없음 — 첫 실행(… 빚 0)` exit 0(비git D18 은 그대로 exit 1) · 4′ 문면 · houserules final §7 · 픽스처 D20a·b |
| M2 재승인 절이 요구 키를 떨어뜨림 | 수용(러너 쪽) | `residual_sets` = 마지막 `## G0` 절부터 순서대로 G0·재승인 절의 ⓐ·요구를 더하고 재상정을 뺀다(재상정 뒤 재승인이 다시 적으면 되살아남) · 기록 정형 «재승인 절은 새로 정한 키만 적어도 된다» · G2 설명 · final §7 · 픽스처 D21a·b·c |
| M3 ⑤ add 범위가 config.json 을 뺌 | 수용 | ⑤ add 대상 = 이번 실행 폴더 산출물 + 이번 실행이 step 3·5 에서 바꾼 `config.json` · 경로 명시(민감 raw 제외) |
| m1(가) 앞 요청 G0 절로 판정 | 수용 | 마지막 `## G0` 시각 < `debt-g0.json` `scanned_at`(분 · 로컬) → exit 1 «이번 요청의 G0 절 없음» · 기록 정형 «재사용 폴더라도 새 `## G0` 절» · 픽스처 D22a·b · 기존 픽스처의 고정 시각을 `@NOW@`(스캔 뒤 분)로 |
| m1(나) 코드 펜스 안 머리 | 수용 | `parse_scope` 가 펜스 안 줄을 건너뜀 · 픽스처 D23a·b |
| m2 4′ 기록 시점·배너 exact command | 수용 | 4′ «스캔 직후·빚 질문 전에 `## 빚 스캔 <시각>` 절(command 원문·exit·단위·표·빚 단위 수 → ⓐ′ 대상 여부)» · 배너 빚 1행 = `--debt-scan exit <값>(명령 원문: refactor-scope.md 스캔 기록 절)` · G0 절은 결정 줄·정형 행(스캔 기록은 스캔 절) |
| m3 평문 폴백·대가 정의 | 수용 | 폴백 «배너 1행·선택지·대가 줄» · 대가 ⓐ 규모 / ⓑ 사유·출처 + G2 legacy 잔존·다음 스캔이 다시 물음 / ⓐ′ G0 정지·착륙 뒤 재시작 |
| m4 ⓐ′ 조건 문장 | 수용 | «빚 목록 키들의 경로가 2개 이상의 단위에 걸칠 때만 — 슬라이스 0 규모의 단위 수로 판정하지 않는다» + 스캔 기록 절의 `빚 단위 수 n → ⓐ′ 대상|비대상` 행 |
| m5 묶음 항목 단위 | 수용 | «개명·이동 대상 파일(폴더 발견이면 그 폴더)마다 묶음 한 항목» |
| m6 coder-web «URL 불변» | 수용 | «페이지·fragment 라우트 URL 불변 — 정적 자산 경로는 참조를 함께 치환하면 바뀌어도 된다»(양 런타임) |
| m7 «첫 슬라이스» 중의 | 수용 | «첫 기능 슬라이스 선두(슬라이스 0이 아니다)» |
| m8 리뷰어 입력에 ⓐ 목록 없음 | 수용 | design-review-web · DR 경량 입력에 «(G0 ⓐ가 있으면) 스코프 메모 슬라이스 0 줄·`refactor-scope.md` 경로» |
| m9 빚 모드 WS5 notice | 수용 | 빚 모드에서 notice 를 «WS5(골격 완비) 빚 모드 제외 — 기존 단위의 골격 미비는 빚이 아니다(…)»로 바꿔 싣는다 · 픽스처 D4a 문자열 |
| m10 문면 틈 3건 | 수용 | (가) G1 재승인의 새 ⓐ → architect 재호출로 슬라이스 0 절에 더한 뒤 G1 배너 (나) 슬라이스 0 끝 exit 1 = green 아님 (다) G2 빚 행 전이 표기 `빚: 해당 없음(규칙 이전 G0)` |

- 새 red 픽스처 8건(D4a 문자열 · D19a·b · D20a·b · D21a · D22a · D23a)은 옛 러너(Codex 쪽 수정 전 사본)에서 전부 실패하고 새 러너에서 통과한다 — `fixtures_debt.sh` 55/55.
- 재검증: `make verify-web` green · `claude plugin validate dddjango-web --strict` 통과 · byte 미러 `cmp` 일치 · 문면 토큰 10종 Claude/Codex 수 일치.
- 4′ 문면이 바뀌어 W-T1(Claude)·Codex 를 한 번씩 다시 돈다(`behavior-tests.md` 끝 행).
