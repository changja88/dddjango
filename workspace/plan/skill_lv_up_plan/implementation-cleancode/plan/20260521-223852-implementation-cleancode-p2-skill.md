# implementation-cleancode P2 skill 수정 계획

## 수정 이유

P2 기준에서 `implementation-cleancode`는 코드 리뷰뿐 아니라 사용자가 명시적으로 요청한 유지보수성 리팩터링도 처리한다. 현재 `SKILL.md` 본문은 이를 허용하지만 `agents/openai.yaml` default prompt는 review-only로 보일 수 있고, frontmatter exclusion은 tiny naming question을 직접 드러내지 않는다.

## 수정 범위

- `dddjango/skills/implementation-cleancode/SKILL.md`
  - frontmatter `description`을 trigger 중심의 `Use when` 문장으로 정리한다.
  - clean-code review/refactoring trigger와 주요 제외 조건을 같은 표면에 둔다.
  - 본문 첫 문장이 목적과 직접 refactor 처리 범위를 더 명확히 말하게 한다.
- `dddjango/skills/implementation-cleancode/agents/openai.yaml`
  - `short_description`을 review/refactor 양쪽 범위와 맞춘다.
  - `default_prompt`에 `$implementation-cleancode`를 유지하면서 review 또는 refactor 목적을 모두 담는다.

## 수정하지 말아야 할 범위

- `workspace/reference/**`는 source gap이 발견될 때만 별도 reference 계획으로 다룬다.
- bundled reference는 중복 설명을 늘리지 않는다.
- 다른 skill, eval pack, validator script는 수정하지 않는다.
- `agents/openai.yaml`에는 명시 요청 없는 `icon_small`, `icon_large`, `brand_color`, `dependencies`, `policy` 같은 optional field를 추가하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` frontmatter trigger/exclusion 문장을 수정한다.
- [x] `SKILL.md` 본문 첫 문장을 목적과 실제 사용 조건에 맞춘다.
- [x] `agents/openai.yaml`의 UI metadata를 `SKILL.md`와 맞춘다.
- [x] source 수정 후 `diff -qr`로 runtime cache drift를 확인한다.
- [x] drift가 있으면 별도 runtime-sync 분석/계획을 작성하고 cache를 동기화한다.
- [x] 검증 명령과 독립 리뷰를 실행해 Blocker 0, Major 0, 열린 Minor 0인지 재평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`

## 완료 조건

- `SKILL.md` 목적, trigger, 제외 조건이 frontmatter와 본문에서 같은 의미로 읽힌다.
- `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`와 충돌하지 않는다.
- optional interface field가 추가되지 않았다.
- source skill과 runtime cache 동기화가 확인된다.
- 검증 명령이 통과하고 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
