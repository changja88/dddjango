수정 대상: runtime-sync

# implementation-cleancode P1 runtime sync 분석

## 평가 기준

- source skill: `dddjango/skills/implementation-cleancode/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/`
- 비교 명령: `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`

## 현재 판정

source skill 수정 후 runtime cache가 source와 다르다.

차이 파일:

- `SKILL.md`
- `agents/openai.yaml`
- `references/responsibility.md`

## 원인

source skill에 Django/dddjango boundary smell 기준을 반영했지만 runtime cache는 아직 이전 버전이다.

## 영향

- runtime에서 `$implementation-cleancode`를 사용할 때 source skill의 최신 지침이 반영되지 않는다.
- P1 종료 조건의 "source skill과 runtime cache 동기화 여부 확인"을 만족하지 못한다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: real-subagent 결과와 메인 `diff -qr` 재검증을 통합했다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
- 초기 Major 1: source skill과 runtime cache가 달랐다.
- 재평가: runtime cache 동기화 후 `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`가 차이를 보고하지 않았다.

## 결론

source skill의 `implementation-cleancode` 디렉터리를 runtime cache의 동일 skill 디렉터리에 동기화한다. 다른 skill cache는 수정하지 않는다.
