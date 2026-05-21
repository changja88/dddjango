# implementation-test P2 Skill Plan

## 수정 이유

P2 기준은 `SKILL.md` 목적, trigger, 제외 조건이 frontmatter와 본문에서 충돌 없이 드러나고 `agents/openai.yaml` metadata와 일치하는지 확인한다. 현재 본문 Routing에는 production code와 test ownership을 나누는 조건, 작은 pytest 관련 질의는 직접 답하라는 조건이 있지만 frontmatter에는 같은 수준으로 드러나지 않는다. 또한 UI metadata는 test review 목적을 약하게 표현한다.

## 수정 범위

- `dddjango/skills/implementation-test/SKILL.md`
- `dddjango/skills/implementation-test/agents/openai.yaml`
- source 수정 후 필요한 runtime cache `implementation-test` 동기화

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-test/**`는 이번 P2에서 부족하다고 판정하지 않았으므로 수정하지 않는다.
- `dddjango/skills/implementation-test/references/*.md`는 P2 목적/trigger/metadata gap의 직접 원인이 아니므로 수정하지 않는다.
- 다른 skill, eval pack, validator는 수정하지 않는다.
- `agents/openai.yaml`에 icon, brand color, dependencies, policy 같은 optional interface field를 추가하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter에 production code handoff와 test ownership boundary를 반영한다.
- [x] `SKILL.md` frontmatter에 작은 assertion, fixture, import ordering, typo, pytest command explanation 직접 응답 예외를 반영한다.
- [x] `agents/openai.yaml`에 test review 목적을 반영한다.
- [x] source 수정 뒤 runtime-sync 분석/계획을 작성하고 runtime cache를 동기화한다.
- [x] `diff -qr`로 source/runtime sync를 확인한다.
- [x] required validators를 실행한다.
- [x] P2 재평가에서 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`

## 완료 조건

- `SKILL.md` frontmatter와 본문 Routing이 같은 목적, trigger, 제외 조건을 가리킨다.
- `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`의 test implementation/review 목적과 일치한다.
- `agents/openai.yaml`은 openai_yaml 기준을 지키고 optional interface field를 추가하지 않는다.
- Runtime cache와 source skill이 일치한다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 결과

- `diff -qr dddjango/skills/implementation-test /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test`: 통과, 출력 없음
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과
