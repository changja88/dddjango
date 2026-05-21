수정 대상: runtime-sync

# source-reference-audit P1 runtime sync 분석

## 평가 요약

`dddjango/skills/source-reference-audit/SKILL.md`와 `agents/openai.yaml`을 수정했으므로 runtime cache가 source skill과 달라졌다. P1 종료 조건은 source skill과 runtime cache 동기화 확인을 요구한다.

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 수정 전 독립 P1 리뷰는 runtime cache가 source와 sync 상태라고 확인했다. Source skill 수정 후에는 메인 재평가에서 runtime cache stale을 Major로 판정한다.

skill-creator 리뷰: 수정 전 metadata alignment는 충분하다고 보았다. Runtime sync 후 source skill과 cache의 `SKILL.md`가 동일해야 같은 runtime behavior가 보장된다.

## 근거

- source skill: `dddjango/skills/source-reference-audit/SKILL.md`, `dddjango/skills/source-reference-audit/agents/openai.yaml`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit/`
- source skill 수정으로 Source Loading과 Dedicated Source And DRF Guardrail section, metadata short_description 축약이 cache에 반영되어야 한다.

## 발견 사항

### Major 1. Runtime cache stale

Source skill이 보강된 reference decision을 반영했지만 runtime cache는 아직 이전 내용을 제공한다.

허용 claim:

- source skill 수정 후 runtime sync가 필요하다.

금지 claim:

- cache를 복사하기 전 source와 runtime이 동기화됐다고 말한다.

## 수정 필요 범위

- source의 `dddjango/skills/source-reference-audit/SKILL.md`와 `agents/openai.yaml`을 runtime cache의 동일 파일에 복사한다.

## 수정하지 말아야 할 범위

- runtime cache에 source와 다른 임의 내용을 추가하지 않는다.
- 다른 cached skill은 수정하지 않는다.
- `workspace/reference/**`를 runtime cache에 복사하지 않는다.

## 재평가 기준

- `diff -ru dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit` 출력이 없다.
- validators가 통과한다.
