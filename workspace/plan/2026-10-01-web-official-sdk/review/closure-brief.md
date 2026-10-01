# 닫힘 확인 지시서 — web 2차 리뷰 지적 F1~F7 반영 확인 (2026-10-01)

너는 같은 독립 리뷰어다(앞 리뷰 `./review.md` 를 쓴 사람). **코드를 고치지 않는다.** 결과는 이 폴더의 `closure.md` 하나에만 쓴다. 한국어로 쓴다.

## 대상
- 구현자가 리뷰 대상 `d6d2878d` 위에 수정 커밋 2개를 올렸다(같은 저장소의 가지 `worktree-agent-a98990edf7b131c66`):
  - `ca53b20a` F1·F2·F3 — restore 사전 확인 · 첫 채택 gateway 경로 원문 · 운영자 문서 리다이렉트 최종 주소
  - `66781e89` F4·F5·F6·F7 — gateway 정규형 단일화 · WV8 문서 별칭 · 링크 단위 · K51 걸음 수 고정
  - `git diff d6d2878d..66781e89` · `git log d6d2878d..66781e89`
- 구현자 기록(읽기만 · 미추적 파일): `/Users/hyun/Desktop/dddjango/.claude/worktrees/agent-a98990edf7b131c66/workspace/plan/2026-10-01-web-official-sdk/impl-sdk.md` 의 «리뷰 반영» 절(발견별 수정 위치 · 픽스처 · 리뷰와 다르게 한 판단 4개).
- 실행은 `$TMPDIR` 에 `git clone --shared` 사본을 만들어 `66781e89` 를 체크아웃해서 한다. 이 워크트리의 체크아웃은 바꾸지 않는다.

## 볼 것
1. **F1~F7 하나씩** — 네가 앞 리뷰에서 쓴 재현(`probes.py` · `boundary-probes.cjs` 등)을 `66781e89` 에 다시 돌려 «닫힘 / 부분 / 안 닫힘»과 근거(명령 · 출력 · 파일:줄)를 적는다.
2. **수정이 만든 새 문제·남은 우회**
   - F4: 더 엄격해진 정규형이 정상 운영자 경로(카카오 등 실제 API 경로)를 막지 않나 · Python(`sdk_registry.normalize_gateway_url`)과 스니펫(`sdk_boundary.js normPath`)이 같은 답을 내나(표본을 네가 더 만들어 대조).
   - F5: 정상 코드 오탐(`logger.write` · `stream(document).write` 류)이 늘지 않았나 · 남은 우회를 시도한다 — 예: 구조 분해(`const {write} = document`) · 선택 연결(`document?.write`) · `Reflect.apply`/`.call`/`.apply` · 문자열 이어 붙인 키(`document['wr'+'ite']`) · `globalThis.document` · `window['document']`. 막지 못하는 꼴은 «설계 범위 밖(정적 검사 한계)»인지 «막아야 할 구멍»인지 설계 §5 WV8 정의로 가른다.
   - F6: 링크를 따라가지 않게 바꾼 것이 정상 등재 단위(링크 없음)의 판정을 바꾸지 않나.
   - F2 · F3: 새 거절이 정상 첫 채택 흐름을 막지 않나(구현자 픽스처 F2b · F3d · F3e 확인) · 후보 schema `/2` 변경의 파급.
3. **회귀** — SDK 없는 프로젝트의 기존 검사 · 빚 스캔 · `TOTAL_CHECKS` 가 그대로인가. `dddjango-web/scripts/test/fixtures_sdk.sh` 와 `run_fixtures.sh` 를 사본에서 돌린다(전체 `make verify-web` 은 운영자가 따로 돌리고 있으니 생략해도 된다).
4. **미러** — 바뀐 byte 미러 파일 `cmp` 전수(scripts · assets · houserules `final.md`).

## 보고 — `./closure.md`
1. 판정 한 줄: «닫힘(착지 가능) / 조건부 / 안 닫힘»
2. F1~F7 표: 닫힘 여부 · 근거
3. 새 발견: 등급(blocker · major · minor · nit) · 제목 · 파일:줄 · 재현 · 권고. blocker·major 는 재현 절차가 있어야 한다.
4. 구현자의 «리뷰와 다르게 한 판단» 4개 각각 «정당 / 재검토 필요»
마지막 줄에 `REPORT-DONE`.

## 금지
- 코드·문서를 고치지 않는다(이 폴더의 `closure.md` 만 쓴다). 커밋 · push 금지.
- `/Users/hyun/Desktop/spring_dream_server` · `~/.herdr/worktrees/spring_dream_server/**` · `~/.codex` · `~/.claude` · `/Users/hyun/Desktop/dddjango`(main 작업 폴더 · 그 아래 `.claude/worktrees/**` 포함)는 읽기만(쓰기 · `git status` 금지).
- 다른 프로세스를 죽이거나 건드리지 않는다. 네트워크는 쓰지 않는다. Serena · Graphify 를 쓰지 않는다.
- 판단이 막히면 추측하지 말고 질문한다.
