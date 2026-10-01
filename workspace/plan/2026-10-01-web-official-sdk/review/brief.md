# 리뷰 지시서 — dddjango-web 2차 구현(W6m · 공식 SDK 개방) 독립 구현 리뷰 (2026-10-01)

너는 독립 리뷰어다. **코드를 고치지 않는다.** 이 워크트리(`/Users/hyun/.herdr/worktrees/dddjango/review-web-sdk`, 브랜치 `review/web-sdk`, HEAD `d6d2878d`)에서 읽고, 검증은 `$TMPDIR` 의 사본에서 돌린다. 결과는 이 폴더의 `review.md` 에 쓴다. 한국어로 쓴다.

## 대상
- 커밋 4개(기준 main `2fffcb22`): `b707c531` W6m · `4934e5be` SDK S1(검사기·도구) · `ef3cf78a` S2+S3(규범·역할) · `d6d2878d` S4(Coordinator·REQUEST_GUIDE). `git log 2fffcb22..HEAD` · `git diff 2fffcb22..HEAD`.
- 구현자 기록: `./impl-sdk.md`(이 폴더 · 설계와 달라진 점 13항 포함).

## 기준(설계 · 읽기만 — main 작업 폴더의 미추적 파일이다)
- 공식 SDK: `/Users/hyun/Desktop/dddjango/workspace/plan/2026-10-01-web-official-sdk/design-sdk.md` v3.3 동결 — 특히 §3(등재 목록) · §4(사본 자리·로드) · §5(검사기 WV1~WV13 · 기존 검사 변경 · 빚 스캔) · §6(Coordinator 흐름) · §7(규범 문안) · §8(Codex 미러) · §11(구현 계획·검증) · **§16 구현 단계 메모 ①~⑥**.
- W6m: `/Users/hyun/Desktop/dddjango/workspace/plan/2026-09-30-speed-improvement/design-W5-7.md` v3 §3-4 · §3-5.
- 저장소 지침: `AGENTS.md` · `docs/DEVELOPMENT.md`(dddjango-web 은 산문 정본 · Codex 미러는 scripts·assets·references 는 byte, 역할·Coordinator·SKILL 은 의미 미러).

## 볼 것
1. **§16 ①~⑥** — 하나씩 코드·픽스처에서 확인하고 «처리됨 / 부분 / 안 됨»과 근거(파일:줄 · 픽스처 이름)를 적는다.
2. **설계 정합** — 구현이 §3~§7 문안·판정과 맞는가. 구현자가 적은 «설계와 달라진 점» 13항은 하나씩 «정당 / 재검토 필요»로 판정한다.
3. **보안·우회** — WV8 싱크(srcdoc · createElement · document.write 별칭·괄호·호출 우회) · 운영자 호스트 차단·팝업 · `sdk_boundary.js` 가로채기(수명 함수 통과 · gateway 경로 정규형) · `sdk_vendor.py` 출처 검증(공식 도메인·integrity·최종 URL) · 목록 시대·강등 금지(WV13) · 얕은 이력 처리. 우회 가능한 경로를 찾으면 재현 절차를 적는다.
4. **회귀** — 기존 검사·빚 스캔·리팩토링 판정이 SDK 없는 프로젝트에서 바뀌지 않는가(기존 픽스처 · `TOTAL_CHECKS` · 사용법).
5. **미러** — byte 미러 `cmp` 전수 · Claude↔Codex 의미 미러(역할·Coordinator·SKILL)가 같은 뜻인가 · `Makefile` verify-web 대조 표지.
6. **W6m** — 문면 4쌍이 설계 §3-4 와 같은 뜻인가 · 동작·감사 구조를 바꾸지 않았나 · touched 정의가 W4(`static_delta.py`)와 같은가.
7. **검증 재실행** — `$TMPDIR` 에 `git clone --shared` 사본을 만들어 `make verify-web` 을 돌린다(가능하면 `make verify` 도 — 봉인 드리프트만 red 면 그 사실만 적는다). 시간이 너무 길면 픽스처 묶음 `dddjango-web/scripts/test/run_fixtures.sh` 만.

## 보고 — `./review.md`
1. 판정 한 줄: «승인 / 수정 후 승인 / 반려»
2. 발견 목록: 등급(blocker · major · minor · nit) · 제목 · 파일:줄 · 근거(재현·인용) · 권고. blocker·major 는 재현 절차가 있어야 한다.
3. §16 ①~⑥ 표 · 달라진 점 13항 판정 표 · 미러 결과 · 검증 결과
마지막 줄에 `REPORT-DONE`.

## 금지
- 코드·문서를 고치지 않는다(이 폴더의 `review.md` 만 쓴다). 커밋하지 않는다. push 금지.
- `/Users/hyun/Desktop/spring_dream_server` · `~/.herdr/worktrees/spring_dream_server/**` · `~/.codex` · `~/.claude` · `/Users/hyun/Desktop/dddjango`(main 작업 폴더)는 읽기만(쓰기·`git status` 금지).
- 다른 프로세스를 죽이거나 건드리지 않는다. 네트워크는 쓰지 않는다(카카오 원본이 필요하면 구현자 scratch `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/impl-web2/` 의 받아 둔 사본을 읽는다).
- Serena · Graphify 를 쓰지 않는다. 판단이 막히면 추측하지 말고 질문한다.
