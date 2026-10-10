# 2.3.0 짓기 기록 — dddjango-web 2.3.0 (한 web 앱의 화면 제품마다 design_system 뿌리와 문서 셸 · F4-71)

- 시작 10-10 14:25(KST · 결정 15 뒤) · 운영자 · 바탕: 구현은 R main `1e4344a6`(2.2.5)에서 시작해 `f19ced8b`(2.2.6) 위로 옮김 · 사본 `<S>/web-230`(검사기) · `<S>/web-230b`(글) · `<S>/web-230c`(검사기 보완) · `<S>/web-230i`(합침) · `<S>/web-230j`(검토 보완) · `<S>/web-230k`(재검토 보완) · 결정 · 판정 · 넣은 것: `plan-2.3.0.md` · 근거 기록 `<S>/web-230-notes/`
- `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`

## 진행
- 13:53:15 진단(Codex · `<S>/web-226-notes/diagnose-b.md` — 2.2.6 진단 때 같이): F4-71 실제 문제 · 규약이 뿌리 하나 · 틀 하나만 상정 → 손님 쪽 옛 파일 넷이 «옮길 자리가 없는 빚».
- 14:24:09 date 뒤 · 14:25:02 date 앞 사용자 결정 15 «가.»(제품마다 디자인 묶음 · 화면 틀).
- 사전 설계 둘을 한꺼번에: Claude(`design-claude.md` · 14:45:04 끝) · Codex(`design-codex.md` · 14:27:13 ~ 14:55:01) → 운영자가 합쳐 `plan.md`.
- 14:57:58 ~ 15:09:59 설계 점검(Codex · `check-230.md`): «보완 후 진행» — 운영자 판정 여섯은 «되돌릴 근거 없음» · 선언 오류 목록 · 공통 사전 점검 · 혼입 게이트의 «새 줄만» · 착륙 묶음 등을 보탬.
- 구현 둘을 한꺼번에(15:13 ~ 15:14 지시): 검사기 · 픽스처(Claude · `<S>/web-230` · `impl-scripts.md` · 커밋 `039e7282` 16:17:58) · 글(Codex · `<S>/web-230b` · 15:57:12 ~ 16:36:08 · `impl-docs.md` · 커밋 `d2468893` 16:36:27).
- 구현 검토: 검사기 — Codex(16:18:46 ~ 16:33:58 · `review-scripts-codex.md` · 차단 3) · Claude(~ 16:50:21 · `review-scripts-claude.md` · 차단 2 — 선언 없는 프로젝트의 2.2.5 대비 차이는 합성 1,032 대조 0) / 글 — Codex(16:36:57 ~ 16:50:11 · `review-docs-codex.md` · 차단 3).
- 검사기 보완 1(Claude · `<S>/web-230c` · `fix-scripts-1.md` · 커밋 `14c2c0e5` 17:37:03): IM13 경로 정규화 · 선언 조사 불능 = 판정 불가 · BC 성분 검증 · 무변 픽스처의 판 올림 알림 · 선언된 골격 · 셸 부재 «미룰 수 없음».
- 17:40:55 2.2.6(`f19ced8b`) 위로 세 커밋을 옮겨 합침(`<S>/web-230i`) → 합치기 마무리(Claude · `integrate.md` · ~ 18:20): 선언 파일을 참조 grep 판정 밖 · 2.2.6 이 넘긴 한계 둘(수신 증명 링크 조사 범위 · PU2 ③ 점 뒤 낱말) · 글 검토 차단 셋 · 호스트 장면 사본 `<S>/f71/host`(decl · skeleton · step1) · 커밋 `c0bfe026` 18:22:00 · 2,451 실패 0 · verify-web exit 0.
- 18:23:53 ~ 18:38 운영자 실측(`measure-operator.md` · 원문 `host-measure/`): 장면 여덟 2.2.6 과 byte 동일 · 호스트 사본 선언 전 2.2.6 과 같음 · 1단계 뒤 옛 키 넷 사라짐 · 치환 확인 통과(2.2.6 은 막음) · 깨진 선언 16 꼴 × 입구 모두 판정 불가 · 6-3-33 동결본 «판 경계» 0 · 6-3-13 이 선언 든 main 을 받은 장면.
- 합친 판 구현 검토: Codex(18:23:44 ~ 18:36:48 · `review-final-codex.md` · 차단 4 — 운영자 재현: 꼬리 안 `/../` 혼입 놓침 · 숫자 리터럴 점 과보고 · 선언 없을 때 오류 문구 · 넷째 조사 불능은 의도된 차이) · Claude(18:23 ~ · `review-final-claude.md` · 실해 차단 0 · 문면 차단 2 = 같은 둘 · 고치면 좋음 다섯).
- 18:42 ~ 19:45 검토 보완(Claude · `<S>/web-230j` · `fix-final.md`): 일곱(꼬리 먼저 떼고 경로 풀기 · 숫자 리터럴 한 토큰 · 오류 문구 · 주석 · 예 이름 · 그릇 이름 BC 거절 · §8 머리말 · private 이름) · 2,604 실패 0 · verify-web exit 0 · 커밋 `0039cf00` 19:46:13.
- 19:47:10 ~ 19:53:55 운영자 재측정(`host-measure/v230b/`): 장면 여덟 2.2.6 과 byte 동일 · 호스트 시점 넷 앞 후보와 같음 · 꼬리 안 `/../` 혼입 이제 IM13 · 오류 문구 2.2.6 과 같음 · 깨진 선언 18 꼴(그릇 이름 둘 더) × 입구 8 모두 exit 1 · 6-3-33 · 6-3-13 장면 앞 후보와 같음.
- 보완 재검토: Codex(19:46:50 ~ 19:58:26 · `rereview-codex.md` · 차단 1 — 필터가 붙은 `{% static %}` 인자를 실제 파일로 확정해 과보고 · 운영자 재현) · Claude(19:46 ~ 20:02 · `rereview-claude.md` · «배포 가능 · 차단 0»).
- 20:03 ~ 20:41 재검토 보완 둘째(Claude · `<S>/web-230k` · `fix-2.md`): 필터 · 변수가 붙은 `{% static %}` 인자는 혼입 판정 밖(닫는 따옴표 바로 뒤가 `(as 이름) %}` 일 때만 확정) · 하우스룰 §8 한 구 · `refactor_audit.py` 주석 · 픽스처 M11 · 2,607 실패 0(20:04:00 ~ 20:20:48) · verify-web exit 0(~ 20:40:56) · 커밋 `7ae360dc` 20:41.
- 결정 16(사용자 «2.3.0은 끝나는 대로 배포하자» — 20:12 date 뒤 · 20:13:19 date 앞): 검증이 끝나면 묻지 않고 배포.
- 20:42:29 ~ 20:48:37 운영자 재측정(최종 판 · `host-measure/v230c/` · `s2-*-v230c.log`): 장면 여덟 2.2.6 과 byte 동일 · 호스트 시점 넷 앞 후보와 같음 · 필터 꼴 IM13 0 · `./` · 꼬리 안 `/../` 꼴 IM13 1 · 오류 문구 · 6-3-33 · 6-3-13 그대로.
- 둘째 보완 재검토: Codex(20:42:07 ~ 20:48:52 · `rereview2-codex.md` · «배포 가능 · 차단 0») · Claude(20:42 ~ 20:51 · `rereview2-claude.md` · «배포 가능 · 차단 0» · 고치면 좋음 — 닫는 따옴표 뒤 공백 + 다른 토큰 꼴의 새 놓침(정상 코드에 안 나옴 · 다음 판) · docstring 글자).
- 배포 조건(결정 16 — 픽스처 · verify-web · 실제 장면 · Codex · Claude 검토 차단 0) 모두 통과 → 배포.
- 20:51:24 배포 직전 현장 보고 장부 재확인: 마지막 항목 F4-76 · 마지막 덧붙임 19:32:05(파일 수정 19:32:16) — 2.3.0 계획에 없는 새 항목 없음(F4-75 · G0 처분 · F4-76 은 다음 판으로 이름을 적음). 봉인 대조(`manifest_seal.py --check --draft`) green.
- 같은 때 F4-75 · G0 처분은 진단 · 재현 · 사전 설계 둘까지(`<S>/web-231-notes/` — 다음 web 판).

## 넣은 것
- 검사기: 새 `src/products.py` · `check_structure.py` · `check_naming.py` · `check_imports.py` · `check_purity.py` · `inflow.py` · `subst.py` · `common.py` · `backstop.py` · `debt.py` · `refactor_audit.py` — 두 벌 byte 미러. 픽스처 `fixtures_patch230.py`(새) · `fixtures_patch226.py` · `fixtures_sdk.sh` · `fixtures_refactor_audit.sh` · `run_fixtures.sh`.
- 글: 하우스룰 · architecture-ui · implementation-django references 두 벌 byte · Coordinator 두 벌 · 역할 넷 두 벌 · REQUEST_GUIDE 두 벌 · 지식 요약 · AGENTS.md · README.

## 안 한 것 · 남은 것
- 실제 에이전트 레인을 새로 돌린 시험은 없다 — 실제 레인의 고정 장면과 호스트 main 사본에서 백스톱으로 확인.
- F4-75(NM17 ↔ 치환 확인) · G0 빚 질문의 «플러그인 수리 대기» 정형 처분은 다음 web 판(진단 중 — 운영자가 2.2.6 진단 뒤 장부에 붙은 것을 늦게 봄) · F4-73 · F4-76(서버)은 dddjango 2.20.0.
- 받아들인 한계는 `plan-2.3.0.md` «알려진 한계».
