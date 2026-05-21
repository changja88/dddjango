# source-reference-audit P1 reference 수정 계획

## 수정 이유

P1 평가와 독립 리뷰에서 `workspace/reference/source-reference-audit/reference/final.md`가 source/reference governance의 핵심 role/path/leakage 규칙은 제공하지만, DRF guardrail provenance, provisional/fallback source 판정, final/review/internal/external material precedence, metadata/runtime sync evidence, eval traceability coverage를 source decision으로 충분히 고정하지 못한다는 Major 2건이 발견됐다.

## 수정 범위

- `workspace/reference/source-reference-audit/reference/final.md`
  - reference material precedence와 missing supplemental material 보고 규칙 추가
  - source provenance/crosswalk evidence contract 추가
  - dedicated source, open gap, provisional/fallback 판정 규칙 추가
  - DRF guardrail audit decision과 source evidence 위치 추가
  - runtime metadata/frontmatter 및 cache sync evidence rule 추가
  - eval traceability와 validation coverage source rule 추가
  - completion gate 추가

## 수정하지 말아야 할 범위

- eval oracle, eval goal, public case, runner는 수정하지 않는다.
- `dddjango/skills/source-reference-audit/**`는 reference 수정 후 반영도 재평가에서 부족할 때만 수정한다.
- runtime cache는 source skill을 수정한 경우에만 별도 runtime-sync analysis/plan 후 동기화한다.
- 다른 skill/reference의 P1 변경과 섞지 않는다.

## 작업 체크리스트

- [ ] `final.md`에 final/review/internal/external material precedence를 추가한다.
- [ ] `final.md`에 dedicated/provisional/open-gap source 판정 규칙을 추가한다.
- [ ] `final.md`에 DRF guardrail audit source와 forbidden claim을 추가한다.
- [ ] `final.md`에 metadata/frontmatter, runtime cache, validation coverage, eval traceability evidence rule을 추가한다.
- [ ] reference 수정 후 `SKILL.md`, `agents/openai.yaml`, runtime cache 반영도를 재평가한다.
- [ ] 필요한 경우 skill analysis/plan을 작성하고 source skill 및 runtime cache를 수정한다.
- [ ] validators를 실행한다.
- [ ] 리뷰 결과를 Blocker 0, Major 0, 열린 Minor 0으로 재판정한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

필요 시 source eval pack 구조 확인용으로 다음을 실행한다.

```bash
.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket source
```

## 완료 조건

- `final.md`가 P1 reference 기준을 충분히 담고 있다.
- 독립 리뷰 Major 2건이 source reference 수정으로 닫힌다.
- eval duplicate 문제는 P1에서 수정하지 않고 후속 analysis로 분류되어 있다.
- validators가 통과한다.
- reference 재평가 후 남은 Blocker 0, Major 0, 열린 Minor 0이다.
