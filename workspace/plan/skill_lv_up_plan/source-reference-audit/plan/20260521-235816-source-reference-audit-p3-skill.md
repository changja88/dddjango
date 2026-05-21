# source-reference-audit P3 skill 수정 계획

## 수정 이유

P3 기준은 skill 간 책임과 handoff가 겹치지 않고, `SKILL.md`는 핵심 절차와 routing 중심으로 유지하며, 세부 source-governance decision은 bundled reference에서 필요한 때만 로딩되도록 요구한다. 현재 구조는 대체로 충분하지만 frontmatter의 validation/eval trigger가 넓고 bundled reference가 기본 로딩처럼 안내되어 progressive disclosure가 약하다.

## 수정 범위

- `dddjango/skills/source-reference-audit/SKILL.md`
  - frontmatter `description`의 validation coverage/eval traceability trigger를 source/reference governance와 explicit eval-pack review 맥락으로 좁힌다.
  - Routing에 일반 test coverage/eval 실행/application behavior work handoff를 명확히 한다.
  - Source Loading에서 bundled reference를 필요한 세부 audit에만 읽도록 gate를 바꾼다.
  - validator-required boundary/leakage/path 문구는 유지하되 세부 decision source는 bundled reference로 안내한다.
- source 수정 후 필요한 runtime cache `source-reference-audit` 동기화

## 수정하지 말아야 할 범위

- `workspace/reference/source-reference-audit/**`는 수정하지 않는다.
- Neighboring skill reverse handoff 보강은 이번 target skill 수정 범위를 벗어나므로 수정하지 않는다.
- `workspace/scripts/**`, eval pack, answer oracle, generated run artifact는 수정하지 않는다.
- `agents/openai.yaml`은 의미상 불일치가 발견될 때만 좁게 수정한다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter trigger를 source/reference governance 중심으로 좁힌다.
- [x] Routing에 validation coverage/eval traceability의 handoff boundary를 명시한다.
- [x] Source Loading에서 bundled reference를 조건부 로딩으로 바꾼다.
- [x] `SKILL.md`가 validator-required 핵심 guardrail을 유지하는지 확인한다.
- [x] source 수정 뒤 runtime-sync 분석/계획을 작성하고 runtime cache를 동기화한다.
- [x] `diff -qr`로 source/runtime sync를 확인한다.
- [x] required validators를 실행한다.
- [x] P3 재평가에서 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit
```

## 완료 조건

- 직접 책임과 handoff 기준이 명확하다.
- 다른 skill과 책임이 충돌하거나 중복되지 않는다.
- `SKILL.md`는 핵심 절차 중심이고 bundled resource는 필요한 때 발견 가능하다.
- 불필요한 중복과 깊은 reference 연결이 없다.
- Source skill과 runtime cache가 diff 없이 일치한다.
- Required validators가 통과한다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 결과

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과.
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과.
- `diff -qr dddjango/skills/source-reference-audit /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/source-reference-audit`: 출력 없음.
