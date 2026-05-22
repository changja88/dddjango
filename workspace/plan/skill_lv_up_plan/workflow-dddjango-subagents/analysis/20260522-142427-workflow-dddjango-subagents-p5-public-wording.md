수정 대상: skill
원인 분류: skill

# workflow-dddjango-subagents P5 public wording 분석

## 문제

P5 skill-creator 관점 리뷰에서 runtime-facing `workflow-dddjango-subagents` guidance가 `validation-pack`, `scoring`, `report`, `run-variance` 같은 내부 eval 용어를 직접 노출한다고 지적했다. 이 skill은 사용자-facing workflow/handoff를 담당하므로, 내부 평가 패키지나 채점 구조를 runtime guidance처럼 보이게 하면 source-reference-audit와의 책임 경계가 흐려진다.

## 영향

P5 기준의 public leakage와 responsibility boundary에서 Major risk가 남는다. workflow skill은 validation evidence와 completion proof 문제를 발견했을 때 owning follow-up으로 넘기면 충분하며, 내부 eval schema나 scoring 어휘를 runtime 사용자에게 드러낼 필요가 없다.

## 조치 방향

- `SKILL.md` Runtime Rules의 내부 eval 용어를 public-facing validation evidence, review coverage, completion proof, run evidence wording으로 바꾼다.
- `references/integration-checklist.md`의 같은 follow-up 문구도 동일하게 정리한다.
- source-reference-audit handoff는 유지하되 내부 eval 구조를 직접 언급하지 않는다.

## 리뷰

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: `Herschel` subagent가 runtime skill public wording leakage risk를 Major로 보고했다.

skill-creator 리뷰: `Herschel` subagent가 skill-creator/runtime skill 관점에서 trigger, role boundary, public/internal wording을 검토했다. 메인 판단은 지적이 현재 codebase reality와 일치하므로 좁게 수정한다.
