# implementation-test P1 Skill Plan

## 수정 이유

보강된 source reference가 Django Ninja `TestClient`, pytest-django transaction 선택, idempotency/concurrency tests를 포함하므로 runtime skill도 이 범위를 구체적으로 안내해야 한다. 현재 `SKILL.md`와 `coverage-mutation.md`의 한 줄 언급만으로는 실제 테스트 작성 작업에서 충분하지 않다.

## 수정 범위

- `dddjango/skills/implementation-test/SKILL.md`
- `dddjango/skills/implementation-test/references/django-api-concurrency.md`
- `dddjango/skills/implementation-test/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-test/**`는 이미 reference gap 보강을 마친 뒤 재평가 대상으로만 본다.
- `workspace/develop/eval/**`는 수정하지 않는다.
- 다른 skill 디렉터리와 다른 runtime cache는 수정하지 않는다.
- 기존 bundled reference 내용을 대규모 재편하지 않는다.

## 작업 체크리스트

- [x] Django API/idempotency/concurrency 전용 bundled reference를 추가한다.
- [x] `SKILL.md` Reference Loading에 새 reference 파일을 연결한다.
- [x] Runtime Rules에 API contract, idempotency, transaction/concurrency 테스트 선택 기준을 보강한다.
- [x] `agents/openai.yaml`을 skill scope와 맞게 갱신한다.
- [x] source skill과 runtime cache 차이를 확인하고 필요하면 runtime-sync 분석/계획 후 동기화한다.
- [x] validator와 독립 리뷰를 실행한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Skill이 source reference의 테스트 구현 범위를 충분히 반영한다.
- Bundled references가 progressive disclosure 원칙에 맞게 로드 대상을 분리한다.
- `agents/openai.yaml`이 `SKILL.md` 목적과 충돌하지 않는다.
- Source skill과 runtime cache sync 여부가 확인된다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
