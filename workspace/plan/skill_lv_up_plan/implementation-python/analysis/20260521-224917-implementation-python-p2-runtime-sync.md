수정 대상: runtime-sync

# implementation-python P2 runtime sync 분석

## 평가 기준

- source skill: `dddjango/skills/implementation-python/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/`
- 비교 명령: `diff -qr dddjango/skills/implementation-python /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python`

## 현재 판정

P2 skill 수정으로 source `SKILL.md` frontmatter와 `agents/openai.yaml` metadata가 변경되었다. runtime cache는 아직 이전 내용을 가지고 있으므로 source skill과 runtime cache가 같은 내용을 가리켜야 한다는 종료 조건을 만족하지 못한다.

## 차이

- `SKILL.md`: frontmatter `description`에 `workflow-dddjango-subagents` routing이 source에만 추가됨.
- `agents/openai.yaml`: `short_description` 길이 보정이 source에만 반영됨.
- `references/*.md`: runtime-facing bundled reference의 source-authoring path 제거가 source에만 반영됨.

## 수정 필요 범위

- source skill의 현재 내용을 runtime cache의 같은 상대 경로로 동기화한다.
- `implementation-python` skill 디렉터리 밖은 수정하지 않는다.

## 수정하지 않는 범위

- runtime cache에서 source에 없는 별도 파일을 만들지 않는다.
- 다른 skill cache는 수정하지 않는다.
- source reference는 추가 수정하지 않는다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: P2 skill 리뷰와 함께 source/runtime cache parity를 확인하도록 real-subagent 리뷰 2건을 실행했다.
- 리뷰 결과는 P2 skill analysis 재평가에 함께 통합했다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 완료 조건

- runtime cache가 source skill과 동일하다.
- `diff -qr`가 차이를 보고하지 않는다.
- validators가 통과한다.
