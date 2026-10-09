# 2.2.4 짓기 기록 — dddjango-web 2.2.4 (브라우저 시험은 샌드박스 밖에서)

- 시작 10-10 02:50(KST) · 운영자 · 바탕 R main `c9016872`(배포된 2.2.3) · 사본 `<S>/web-224`(`git clone --shared` · push 막음) · 결정 · 판정 · 넣은 것: `plan-2.2.4.md` · 근거 기록 `<S>/web-224-notes/`
- `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`

## 진행
- 02:50:41 ~ 02:56 운영자 진단(읽기): 충돌 기록 79건 분류(전체 Chrome `_RegisterApplication` abort · headless shell V8 SIGTRAP) · 레인 Codex 기록에서 02:49 충돌 pid 4235 를 lane-6-3-21 브라우저 시험 출력으로 확인 · 레인 정책(주 세션 on-request + workspace-write · 일부 하위 세션 never + read-only).
- 02:53:11 ~ 02:54:51 운영자 재현(`<S>/cft-probe/` · 운영자가 띄운 pid 만): 셸에서는 두 브라우저 정상 · `codex sandbox -c sandbox_mode="workspace-write"` 안에서 전체 Chrome exit 134 · headless shell exit 133 + `bootstrap_check_in … MachPortRendezvousServer …: Permission denied`.
- 02:58:15 `diagnose.md` · 02:58:54 `plan.md`.
- 02:59:22 ~ 03:07:54 설계 점검(Codex 읽기 · `check-1.md`): «보완 후 진행» — 빠진 실행 자리(SDK 후보 열거 · 경계 확인 · 골격 · 렌더 확인 · 수정 모드 전수 테스트) · 승격 범위(브라우저를 띄우는 단계만 · `never` 면 요청 안 함 · 거절이면 되풀이 · 넓힘 없음) · 승격 불가 coder 인계 · 반송 문장 · ⑤ 문장 · 시험은 고친 파일을 실제로 읽히고 원본 도구 호출로 판정.
- 03:00:28 ~ 03:01:18 작은 끝까지 시험 옛 판(`e2e-old`): 첫 `./run_tests.sh` 가 샌드박스 안 → `browserType.launch: Target page, context or browser has been closed` → 승격해 통과.
- 03:07:54 뒤 ~ 03:10:44 구현(운영자 · 사본): Coordinator 두 벌 «브라우저 실행 환경» 공통 문단 · step 6 · 수정 모드 step 5 · ⑤ · coder-web 두 벌 · implementation-test §4(두 벌 byte). 점검과 다르게 정한 곳 하나(표지로 원인을 가르지 않고 밖 재실행 결과로 판정 — `plan-2.2.4.md`).
- 03:10:52 ~ 03:11:48 작은 끝까지 시험 새 판(`e2e-new` · 사본의 고친 coder-web 파일을 읽힘 · sha256 `5730393d389e`): 첫 `./run_tests.sh` 가 `require_escalated` · 사유 «브라우저 테스트 단계 — Codex 샌드박스 안에서 Chrome이 시작하지 못함» · 통과 · 새 크롬 충돌 0(원본 rollout 호출 인자로 확인).
- 03:10:52 ~ 03:18:17 `make verify-web`(사본) exit 0.
- 03:12:54 ~ 03:20:38 구현 검토(Codex 읽기 · `impl-review.md`): «고칠 것 2» — ① 처음부터 밖 실행 의무를 관측 환경(macOS 샌드박스)으로 한정 · 그 밖 환경은 정책이 허용하는 환경 ② 수정 시도 한도 예외를 샌드박스 안 시작 불능 · 밖 실행 불가 · 거절로 한정(밖에서도 재현되면 실제 실패). 점검과 다르게 정한 곳은 «통과».
- 03:20:42 뒤 ~ 03:21:39 보완 반영(사본 · 두 벌 byte 동일 유지) · `make verify-web` 다시 03:21:39 ~ 03:29:16 exit 0(픽스처 FAIL 0 · 문단 대조 · references byte 미러 통과).

## 넣은 것
- 글만: Coordinator 두 벌 · coder-web 두 벌 · implementation-test references §4(두 벌 byte 동일). 검사기 · 도구 · 픽스처 · 매니페스트 구조 무변.

## 안 한 것 · 남은 것
- 실제 레인에서 다시 돌린 시험은 없다 — 첫 실전 = 2.2.4 를 받은 다음 web 레인.
- 승격 불가 · 거절 · 밖에서도 실패하는 분기는 문장으로만 넣었다(시험 안 함).
- 받아들인 한계는 `plan-2.2.4.md` «알려진 한계».
