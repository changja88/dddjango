수정 대상: process

# P5 plugin manifest cache sync 계획

## 수정 범위

- canonical source: `dddjango/.codex-plugin/plugin.json`
- runtime cache: installed `dddjango-local` cache의 `.codex-plugin/plugin.json`

## 절차

1. canonical manifest를 runtime cache manifest로 복사한다.
2. `cmp`로 두 manifest가 일치하는지 확인한다.
3. 관련 validators를 재실행한다.

## 검증

- `cmp -s dddjango/.codex-plugin/plugin.json <runtime-cache>/.codex-plugin/plugin.json`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`

## 완료 조건

- manifest cache/source drift가 사라진다.
- P5 final review에서 cache/source sync Major가 남지 않는다.
