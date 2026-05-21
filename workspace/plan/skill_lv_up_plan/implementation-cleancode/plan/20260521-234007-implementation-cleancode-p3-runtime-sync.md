# implementation-cleancode P3 runtime sync 계획

## 수정 이유

P3 skill 수정으로 source `SKILL.md`가 변경되었고 runtime cache가 이전 내용을 유지하고 있다. 런타임에서 같은 guidance가 노출되려면 cache를 source와 맞춰야 한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/SKILL.md`
  - canonical source `dddjango/skills/implementation-cleancode/SKILL.md`와 동일하게 동기화한다.

## 수정하지 말아야 할 범위

- `agents/openai.yaml`, `references/*.md`는 diff가 없으면 수정하지 않는다.
- 다른 skill과 runtime cache는 수정하지 않는다.
- source reference와 eval pack은 수정하지 않는다.

## 작업 체크리스트

- [x] canonical source와 runtime cache 차이를 확인한다.
- [x] source `SKILL.md`를 runtime cache `SKILL.md`에 복사한다.
- [x] `diff -qr`로 전체 target skill parity를 확인한다.
- [x] required validation commands를 실행한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- target skill source와 runtime cache의 `diff -qr` 출력이 없다.
- plan constraints와 skill docs validators가 통과한다.
- runtime-sync 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
