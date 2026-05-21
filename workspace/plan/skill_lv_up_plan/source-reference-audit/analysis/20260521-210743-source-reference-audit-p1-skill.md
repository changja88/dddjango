수정 대상: skill

# source-reference-audit P1 skill 반영 분석

## 평가 요약

Reference 보강 후 `dddjango/skills/source-reference-audit/SKILL.md`는 source/reference boundary, leakage, conflict/gap ledger, eval traceability, validation coverage, review output을 대체로 반영한다. 그러나 새 source decision 중 일부가 runtime procedure에 충분히 드러나지 않아 skill 반영 보완이 필요하다.

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 1

Subagent 리뷰/순차 fallback: skill-creator 관점 subagent와 독립 P1 subagent를 실행했다. 기존 skill 상태 기준으로 skill-creator 리뷰는 Blocker/Major 없음, optional Minor 1건을 보고했다. Reference를 보강한 뒤 메인 재평가에서 새 source decision 반영 부족을 Major 1건으로 판정했다.

skill-creator 리뷰: 목적, trigger description, progressive disclosure, metadata alignment는 충분하다. `agents/openai.yaml` semantic alignment는 manual review로 확인해야 한다는 optional Minor는 skill 문서 수정 후 재검토한다.

Final skill-creator 리뷰: source/runtime skill 목적과 leakage-safe wording은 충분하다고 보았지만, `agents/openai.yaml`의 `short_description`이 25-64자 guideline을 초과한다고 Minor 1건을 보고했다. 또한 `quick_validate.py`는 PyYAML 부재로 실행되지 않았으나, P1 prompt의 필수 validator는 `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`이며 해당 명령은 통과했다. 따라서 validation evidence는 필수 validator output으로 닫고, quick_validate 실패는 환경 의존 not-run/blocked evidence로만 기록한다.

## 근거

- Source reference는 material absence reporting, dedicated/provisional source 판정, DRF guardrail source evidence, metadata/cache sync evidence를 명시한다.
- 기존 `SKILL.md`는 `final.md` 기본 사용과 `review/internal/external` 필요 시 읽기를 말하지만, absent material을 `not present`로 보고하고 부재를 conflict-free 증거로 쓰지 말라는 규칙은 약하다.
- 기존 `SKILL.md`는 DRF guardrail audit을 trigger에 포함하지만, greenfield API standard, legacy DRF maintenance, owning source references를 분리해 대조하라는 절차가 없다.
- 기존 `SKILL.md`는 runtime metadata semantic alignment를 말하지만, default prompt leakage와 cache physical path boundary를 source reference 수준으로 충분히 연결하지 않는다.
- `agents/openai.yaml`의 기존 `short_description`은 의미상 맞지만 skill-creator metadata guideline의 64자 상한을 넘는다.

## 발견 사항

### Major 1. 보강된 source decision의 runtime procedure 반영 부족

Reference가 source material precedence, dedicated/provisional source 판정, DRF guardrail audit source, runtime metadata/cache evidence를 명시했으므로 runtime skill도 감사자가 같은 evidence를 수집하도록 안내해야 한다.

허용 claim:

- 기존 skill은 source-reference-audit의 핵심 목적과 많은 출력 규칙을 이미 반영한다.
- 보강 후에는 source decision을 runtime procedure에 더 명시적으로 연결해야 한다.

금지 claim:

- 기존 skill이 새 reference의 모든 P1 source decision을 충분히 반영한다고 주장한다.
- DRF guardrail을 단순 trigger 단어로만 두고 source evidence 대조 없이 닫는다.

### Minor 1. `agents/openai.yaml` short_description 길이 초과

`short_description`은 human-facing UI blurb이므로 25-64자 guideline을 지키는 것이 낫다. 기존 문구는 provenance, gaps, traceability, leakage, boundaries를 모두 담지만 64자를 넘는다.

허용 claim:

- metadata 의미는 skill 목적과 충돌하지 않는다.
- 길이 guideline에 맞게 더 짧은 문구로 줄여야 한다.

금지 claim:

- 길이 초과가 있는데 열린 Minor 0이라고 보고한다.

## 수정 필요 범위

- `dddjango/skills/source-reference-audit/SKILL.md`
  - source material absence reporting 추가
  - dedicated/provisional source criteria 추가
  - DRF guardrail source evidence 대조 추가
  - runtime metadata/cache evidence boundary 보강
- `dddjango/skills/source-reference-audit/agents/openai.yaml`
  - `short_description`을 25-64자 guideline 안에서 축약한다.

## 수정하지 말아야 할 범위

- Source reference 내용을 SKILL.md에 장문 복사하지 않는다.
- 새 bundled `references/*.md`는 만들지 않는다. 현재 body가 짧고 핵심 절차만 추가하면 충분하다.
- eval pack은 수정하지 않는다.

## 재평가 기준

- `SKILL.md`가 보강된 reference decision을 간결한 runtime procedure로 반영한다.
- `agents/openai.yaml`이 skill 목적과 충돌하지 않고 short description guideline을 만족한다.
- source skill과 runtime cache는 sync analysis/plan 후 동일하다.
