# 구현 지시서 — W8 작은 판: «W8 보고판 + 막지 않는 정확값 시트» (2026-10-01)

너는 앞서 `design-w8-v5.md` 를 쓴 설계자이고, 이제 구현자다. 한국어로 쓴다.

## 사용자 결정(2026-10-01 21시대 · 원문)
- W8 범위: «작은 판 먼저 (권장)» — W8 보고판 + 막지 않는 정확값 시트(약 4~5인일) → 다음 레인부터 G2 전 보고로 수리 → 1~2 레인 실측 뒤 차단·입력 결속·발주자 대조 축소를 판단.
- 발주자 손 전수 대조 축소: «결과 보고 정하기 (권장)» — 이번 구현에 넣지 않는다.
- 진행 방식: «Codex 구현 → Claude 리뷰 (권장)».
- 사용자 원칙: «목표는 속도 개선 · 퀄리티는 양보할 수 없다» · «새 결함은 배포 전에 고친다».

## 기준 문서
- 독립 적대 검토(Claude): `./review-claude.md` — 판정 «범위 축소 권고». **§3 «더 작은 첫 단계»가 이번 범위의 정본**이다. §2 의 발견(특히 B1 · M1~M7 · m5 결정적 정렬)을 읽고, 작은 판에 해당하는 것은 반영한다.
- 네 초안 `./design-w8-v5.md` 는 2단계 참고로만 쓴다(이번 범위 밖 장치를 넣지 않는다).
- v4 자료(scratch · 읽기만): `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/design-W8/`(`src/style_census_dv4.js` · `src/compare_census_v4.py` · 합성 시험 · `frozen-v4-*` · `judge-p1g2/`) · 동결 v4.1 `workspace/plan/2026-09-30-speed-improvement/design-W8.md`(§2-4 비교용 데이터 문면 등).
- 저장소 지침: `AGENTS.md` · `docs/DEVELOPMENT.md`(dddjango-web 은 산문 정본 · Codex 미러: scripts·assets·references 는 byte 동일, 역할·Coordinator·SKILL 은 의미 미러 · `Makefile` verify-web 의 byte 미러 대조 목록).

## 범위(검토 §3 «무엇» 1~4 그대로)
1. 도구 제품화: v4 스니펫·대조기를 거의 그대로 `dddjango-web/assets/style_census.js` · `dddjango-web/scripts/compare_style_census.py`(이름은 기존 관례에 맞게 조정 가능)로 넣고 Codex byte 미러. 고칠 것 = 결정적 정렬(동점 처리·묶음 정렬·표본 선택 전 구성원 정렬) · CLI · fixture(합성 시험 재사용 + 결정성 — 해시 시드를 바꿔도 출력 byte 동일). 유지 = 스키마 v4 · 루트 1요소 · SDK 교차 확인 · 모양 속성 fail-closed.
2. G0 원본 census + 정확값 시트: 원본 캡처 자리(이미 `render_audit.js` 를 도는 곳)에서 census 를 함께 저장하고, 같은 census 로 시트를 만든다(같은 모양 서명 묶음마다 대표값 · 프로젝트 `foundation/tokens.css` 에서 **값이 정확히 같은** 토큰 이름 · 없으면 «신규 등록 필요»). architect·coder 입력에는 경로만 더한다. **막지 않는다**(결속 블록·G1 검사 없음).
3. 비교용 데이터: 3-1 캡처 하네스(빌드 폴더 한정)에서 시안 예시 데이터에 맞춘다(v4.1 §2-4 문면). 기존 시험 fixture 는 바꾸지 않는다.
4. 3-1 뒤 보고·처분(비차단): 대조기 실행 → 기존 독립 시각 감사가 차단 후보 묶음을 T/D/F/H 로 처분. T 는 G2 전에 고친다 · D 는 근거 의무 + 시안 예시 값으로 «고치기» 금지 · F/H 는 한 줄 근거 · G2 배너 1급 행(«W8 보고: 후보 N · T 수리 a · D b · F c · H d · 미대조 case k») · 공용 클래스 서명이 여러 case 에 걸친 T 는 «부품 단위 1건».
5. 측정 기록(가볍게): 레인마다 검토 §3 «측정» 1~5 를 나중에 셀 수 있도록 빌드 폴더에 남긴다(새 의무 문서를 늘리지 말고 기존 기록·배너에 싣는다).
- **넣지 않음**: 차단 · 입력 결속 검사 · 재렌더 · exit 3 · 영향 case · 다항목 freshness · 재관찰 축소 · 발주자 대조 축소 · 그림자 관문.
- Coordinator 문서는 이미 크다 — 문단 하나·배너 한 줄 수준으로 짧게. 기계 계약은 도구·참조 문서가 소유한다.

## 순서
1. 먼저 `./design-w8-small.md`(짧게 · 15KB 안팎)를 쓴다: 결론 · 바꾸는 파일 목록(Claude · Codex byte/의미 미러) · 커밋 단위 · 검증 방법 · 검토 발견 처분 표(반영/2단계로/반박 + 까닭).
2. 구현한다. 이 워크트리 가지(`design/w8-v5`)에 작은 커밋으로 올린다. 커밋마다 `make verify-web` 이 green 이어야 한다(`.venv` 가 없으면 `ln -s /Users/hyun/Desktop/dddjango/.venv .venv` 로 심링크하고 커밋에 넣지 않는다). 매니페스트·구조를 바꾸면 `claude plugin validate dddjango-web --strict`.
3. P1·P2 보관 입력 재생으로 확인한다: 새 도구가 v4 와 같은 판정(P1 G2#1 T 35/35 차단 · 저장 JSON 과 묶음 일치 — 정렬 차이 외 동일)을 내는지, 결정성이 성립하는지.
4. 끝에 `make verify-web` 전체와 가능하면 `make verify` 를 돌린다(봉인 드리프트만 red 면 그 사실만 적는다 — **봉인 `manifest_seal.py --write` 는 하지 않는다**. 착지 때 운영자가 한다).
5. 보고 `./impl-w8-small.md`: 커밋 목록 · 바꾼 파일 · 검증 결과(명령 · exit) · 재생 결과 · 검토 발견 처분 · 설계와 달라진 점 · 남은 일. 마지막 줄에 `REPORT-DONE`.

## 금지
- push · main 변경 · 릴리즈 금지. 이 워크트리 밖에 쓰지 않는다($TMPDIR 사본 제외).
- `/Users/hyun/Desktop/dddjango`(main 작업 폴더) · `/Users/hyun/Desktop/spring_dream_server` · `~/.herdr/worktrees/spring_dream_server/**` · `~/.codex` · `~/.claude` 는 읽기만(쓰기 · `git status` 금지). scratch 자료는 읽기만.
- 서버 기동 · DB · 네트워크 금지(로컬 헤드리스 브라우저로 도는 기존 fixture 는 괜찮다). 다른 프로세스를 죽이거나 건드리지 않는다. Serena · Graphify 를 쓰지 않는다.
- 판단이 막히면 추측하지 말고 질문한다.
