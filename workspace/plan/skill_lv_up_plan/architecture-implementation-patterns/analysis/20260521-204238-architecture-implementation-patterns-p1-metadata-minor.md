수정 대상: skill
원인 분류: metadata-discoverability-minor

# architecture-implementation-patterns P1 metadata Minor 분석

## 평가 요약

재리뷰 결과 Blocker와 Major는 없고 `agents/openai.yaml`의 `default_prompt`가 risky write/transaction-boundary entrypoint를 충분히 드러내지 않는 열린 Minor 1개가 남았다. `SKILL.md`와 `outbox-acl.md`의 runtime guidance는 이미 source reference와 일치하므로 source reference 또는 bundled guidance 수정은 필요하지 않고 metadata 보완만 필요하다.

## 근거

- `SKILL.md`는 `Risky Write Consistency Block`에서 transaction owner, side-effect timing, uniqueness/idempotency storage, API behavior handoff를 안내한다.
- `references/outbox-acl.md`는 risky write handoff 항목을 반복한다.
- `agents/openai.yaml` default prompt는 주요 패턴 이름을 나열하지만 risky-write transaction/side-effect/idempotency handoff entrypoint를 직접 드러내지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: real-subagent 재리뷰에서 발견된 열린 Minor 1개를 근거로 한다.

skill-creator 리뷰: `agents/openai.yaml`은 UI-facing metadata이므로 SKILL.md의 사용 표면을 과소대표하지 않아야 한다. `default_prompt`는 한 문장 제약을 유지하면서 risky-write entrypoint를 포함해야 한다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

## 완료 판정

`agents/openai.yaml` default prompt를 보완하고 runtime cache sync와 validator를 다시 실행해야 한다.
