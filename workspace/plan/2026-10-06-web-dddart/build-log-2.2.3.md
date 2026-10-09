# 2.2.3 짓기 기록 — dddjango-web 2.2.3 (승인 병합 유입 — 서버 방식 본뜸)

- 시작 10-09 00:16(KST) · 운영자 · 바탕 R main `793449ddd269d5bb3671c88dd91f64e523cb9d06`(배포된 2.2.2) · 사본 `<S>/web-223`(`git clone --shared` · push 막음) · 결정 · 판정 · 넣은 것: `plan-2.2.3.md` · 근거 기록 `<S>/web-223-notes/`
- `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`

## 진행
- 00:11 ~ 00:15 운영자 작은 끝까지 시험(배포판 도구 · `diff_probe.sh`): main 을 합친 두 레인의 지적이 main 쪽을 같은 기준으로 돌려도 같은 글로 나온다 · 레인이 심은 위반 셋은 레인에만.
- 00:17:47 ~ 00:27:35 넷째 안(상류 트리 전체 재검사 · `plan-2.2.3.draft.md`) 설계 점검(Codex · `review-design.md`): «반려 — blocker 5 · important 4» · 권고 접기 → 사용자에게 결정 4 물음(추천 «접는다»).
- 19:0x 사용자 물음 둘(서버 플러그인도 병합을 다루나 · 왜 web 만 안 하길 권하나) → 운영자: 서버 registry_gate 에 같은 장치가 09-03 부터 있음을 확인 · 권고를 «넣기 — 서버 방식 본뜸»으로 바꿈 · 사용자 «다.로해»(19:02:54 뒤 · 19:04:11 앞).
- 19:07:51 ~ 19:22:36 설계(`plan-2.2.3.md` — 서버 대응표) 점검(Codex · `review-design-2.md`): «반려 — blocker 3 · important 1 · nit 2» — 셋 다 «서버엔 없는데 web 으로 옮기며 생김 · 작은 규칙으로 닫힘»(부모 파싱 실패 비대칭 → 무효 · 부모 트리 링크 → 무효 · 새 git 호출 `GIT_OPTIONAL_LOCKS=0` + `sys.executable -B`) + 좁힌 archive · 캐시 + 픽스처 보강 → 계획에 반영.
- 19:27:19 ~ 20:10:48 구현(Codex 쓰기 · `prompt-impl.md` → `impl.md`): 픽스처 «I» 55 먼저(2.2.2 러너 PASS 15 / FAIL 40) → `inflow.py` · `backstop.py` → 미러 → 글 → 55/0 · web 전체 1,012/0 · verify-web exit 0.
- 20:11:35 ~ 20:24:57 구현 검토(Codex 읽기 · `impl-review.md`): «반려 — blocker 1 · important 1 · nit 1»(병합 확인 전 조회 실패 때 무병합 실행에 알림 한 줄 · 미뤄지는 NM4 · NM18 · NM19 · TG1 승인 병합 G2 사례 · I44 증명 SHA).
- 20:23:33 ~ 20:27:02 실제 레인 장면(`<S>/web-222-notes/real_check.sh` · 2.2.2 와 나란히): 승인 목록에 적으면 8-C-3 · admin-3-2 blocker 1 → 0 · 안 적으면 1 + 알림 · 심은 위반 그대로 · 병합 없는 넷은 출력 같음.
- 20:27:44 ~ 20:47:29 보완(Codex 쓰기 · `prompt-fix-1.md` → `fix-1.md`): 셋 고침 · 새 사례 I46 ~ I50 · I44 단언 강화 · 1,017/0.
- 20:47:44 ~ 20:59:01 운영자 `make verify-web`(사본) exit 0. 20:58:53 ~ 21:01:10 실제 장면 다시(보완 도구) — 앞과 같음(다른 것은 임시로 다시 만든 병합 커밋 번호뿐).

## 넣은 것
- 새 `scripts/src/inflow.py`(가름 전부) · `scripts/backstop.py`(출력 직전 한 번 · 절 · 요약 꼬리 · exit) — 두 벌 바이트 미러.
- 픽스처 `fixtures_subst.sh` «I» 60(136 → 196).
- 글: Coordinator 두 벌(승인 목록 · 슬라이스 끝 · 검사기 이의 · 슬라이스 0 · G2 직전 · G2 배너 · 수정 모드 · 재개 · 벤더 엣지) · 하우스룰 §8(두 벌 바이트 미러) · coder-web 두 벌.

## 안 한 것 · 남은 것
- 실제 에이전트 레인을 새로 돌리는 시험은 하지 않았다(결정적 러너 변경 — 실제 레인 커밋 위에서 러너로 확인). 첫 실전 = 다음에 main 을 합치는 web 레인.
- 못 본 것: 전역 설치본에서의 실제 갱신 · Codex 쪽 실행 · 발주자가 승인 목록에 적는 실제 장면.
- 받아들인 한계는 `plan-2.2.3.md` «받아들인 한계».
