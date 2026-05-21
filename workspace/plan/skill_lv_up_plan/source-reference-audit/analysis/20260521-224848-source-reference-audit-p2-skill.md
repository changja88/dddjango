수정 대상: skill

# source-reference-audit P2 skill 분석

## 평가 요약

`dddjango/skills/source-reference-audit/SKILL.md`는 source/reference governance, leakage, provenance, validation coverage, eval traceability, 제외 조건을 대체로 명확히 담고 있다. 그러나 P2 기준의 "본문에만 숨은 trigger 규칙이 없는지"를 엄격하게 적용하면 일부 구체 trigger가 frontmatter `description`에 충분히 드러나지 않는다.

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰/순차 fallback: real-subagent 2개를 실행했다. skill-creator 관점 리뷰는 body-only trigger Major 3건과 metadata/default prompt 관련 Minor를 보고했다. 독립 P2 리뷰는 broad frontmatter가 충분하다는 반대 판단과 `openai_yaml.md` repo-local 미확인 Minor를 보고했다.

skill-creator 리뷰: `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md` 기준으로 frontmatter `description`이 skill invocation의 핵심 근거이므로, 본문에 있는 `DRF guardrails`, `source/runtime cache sync`, `packaging sync`, `runtime wrong-routing`, `role map`, `reference routing`을 description에 명시하는 쪽이 안전하다고 통합 판단했다.

## 평가 근거

- `SKILL.md` frontmatter는 source/reference governance, metadata/frontmatter trigger routing, provenance, source gap, validation coverage, eval traceability, boundary/leakage review를 포함한다.
- `SKILL.md` 본문 Routing/Source Loading/Dedicated Source 섹션은 DRF guardrail, cache/package sync, wrong-routing/role-map/reference-routing 감사 절차를 더 구체적으로 포함한다.
- `workspace/reference/source-reference-audit/reference/final.md`는 Runtime Metadata And Cache Sync, DRF Guardrail Source Decision, Source Provenance And Crosswalk를 first-class 감사 축으로 둔다.
- `agents/openai.yaml`은 필수 interface field만 포함하며 optional icon/brand/dependency/policy field를 추가하지 않았다.
- `agents/openai.yaml` default_prompt는 private evaluation material, internal criteria, non-public validation notes를 노출하지 않지만, P2 수정 후 frontmatter에 추가될 cache/metadata/wrong-routing 축과 더 맞춰도 된다.

## 발견 사항

### Major 1. DRF guardrail trigger가 frontmatter에 명시되지 않음

본문 13행과 56-58행은 DRF guardrail audit을 명시하지만 frontmatter description에는 DRF guardrail 표현이 없다.

허용 claim:

- DRF guardrail은 source-reference governance의 하위 감사 축이다.
- 본문 절차는 source reference와 충돌하지 않는다.

금지 claim:

- DRF guardrail trigger가 frontmatter에서 충분히 명시되어 있어 body-only trigger risk가 없다고 말한다.

### Major 2. cache/package sync trigger가 frontmatter에 명시되지 않음

본문 24행은 source/runtime cache sync, packaging sync, provenance audit evidence를 다루지만 frontmatter description은 cache/package parity를 직접 말하지 않는다.

허용 claim:

- runtime bundled references와 source/runtime boundary 표현이 넓은 범위에서는 관련된다.

금지 claim:

- P2 기준에서 cache/package sync trigger가 숨은 trigger가 아니라고 단정한다.

### Major 3. wrong-routing/role-map/reference-routing trigger가 frontmatter에 명시되지 않음

본문 26행은 role map, skill description, reference routing을 함께 비교하는 wrong-routing audit을 요구한다. frontmatter의 `skill metadata/frontmatter description trigger routing`만으로는 role-map wrong-routing 감사가 충분히 드러나지 않는다.

허용 claim:

- wrong-routing/role-map audit은 source/reference governance와 workflow boundary 검토의 일부다.

금지 claim:

- role-map/reference-routing trigger가 frontmatter에 명시되어 있다고 말한다.

### Minor 1. default_prompt가 P2 보강 후 전체 scope와 약간 어긋날 수 있음

현재 default_prompt는 provenance, conflict/gap/provisional, boundary/leakage, validation/eval gate를 잘 담지만 runtime metadata/cache sync와 wrong-routing evidence를 직접 언급하지 않는다.

### Minor 2. repo-local `openai_yaml.md` 미확인 보고

독립 리뷰는 repo 내부에서 `openai_yaml.md`를 찾지 못했다고 보고했지만, P2 입력은 `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`를 기준으로 명시했다. 메인 에이전트가 해당 파일을 읽어 확인했으므로 열린 문제로 보지 않는다.

### Major 4. runtime-facing SKILL.md가 source-authoring path를 직접 loading instruction으로 제시함

Post-patch skill-creator 관점 리뷰에서 `SKILL.md` Source Loading이 source-authoring path를 runtime-facing instruction처럼 직접 제시한다고 지적했다. Source reference는 source-authoring path를 source evidence나 cache/source parity evidence로 사용할 수 있게 하지만, runtime-facing allowed reference나 final runtime instruction으로 제시하지 말라고 한다.

허용 claim:

- source-authoring artifacts는 source audit evidence로 inspect할 수 있다.
- source-authoring path는 source evidence 또는 parity evidence로만 보고해야 한다.

금지 claim:

- source-authoring path를 runtime-facing allowed reference나 bundled runtime source path로 제시한다.

## 수정 필요 범위

- `dddjango/skills/source-reference-audit/SKILL.md`
  - frontmatter `description`에 DRF guardrail, wrong-routing/role-map/reference-routing, source/runtime cache/package sync, runtime metadata/openai.yaml audit trigger를 명시한다.
  - Source Loading에서 source-authoring path를 evidence-only로 제한하고 runtime-local bundled reference를 먼저 읽게 한다.
- `dddjango/skills/source-reference-audit/agents/openai.yaml`
  - `default_prompt`를 보강된 skill scope와 맞추되, optional interface field는 추가하지 않는다.
- `dddjango/skills/source-reference-audit/references/source-governance.md`
  - source-reference-audit source decision을 runtime-local summary로 제공한다.

## 수정하지 말아야 할 범위

- `workspace/reference/source-reference-audit/reference/final.md`는 P2 현 평가에서 충분하므로 수정하지 않는다.
- source reference의 장문을 그대로 복사하지 않고 runtime-local summary만 추가한다.
- eval pack, 다른 skill, 다른 reference area는 수정하지 않는다.

## 재평가 기준

- frontmatter `description`과 본문 trigger 사이에 숨은 body-only trigger가 남지 않는다.
- `agents/openai.yaml`이 `SKILL.md`와 의미상 일치하고 openai_yaml.md의 필수 interface field 제약을 지킨다.
- private evaluation material, internal criteria, non-public validation notes가 runtime/public metadata에 노출되지 않는다.
- source skill과 runtime cache가 동기화된다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 최종 재평가

Post-patch real-subagent 리뷰 2차례를 실행했다. 첫 post-patch 리뷰는 frontmatter trigger, metadata, runtime cache parity를 문제 없음으로 판정했지만, skill-creator 관점 리뷰가 runtime-facing `SKILL.md`의 source-authoring path loading instruction을 Major 1건으로 지적했다. 이에 `SKILL.md` Source Loading을 source-authoring evidence-only wording으로 보정하고, runtime-local bundled reference `references/source-governance.md`를 추가했다.

최종 focused review는 이전 path-boundary/runtime-surface Major가 닫혔고, 새 bundled reference가 hidden trigger, metadata alignment, optional field, leakage, runtime-facing source-authoring path exposure 문제를 만들지 않았다고 판정했다.

최종 판정:

- Blocker 0
- Major 0
- 열린 Minor 0

검증 evidence:

- `diff -qr dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit`: 출력 없음
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과
