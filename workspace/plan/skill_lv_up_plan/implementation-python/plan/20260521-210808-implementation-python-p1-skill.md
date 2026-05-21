수정 대상: skill

## 수정 이유

source reference가 충분해진 뒤 runtime-facing skill surface도 같은 범위와 경계를 보여야 한다. 현재 skill 문서는 required topics를 일부 담고 있지만 설명문 언어, metadata scope, tooling/async 세부 판단이 P1 기준에 부족하다.

## 수정 범위

- `dddjango/skills/implementation-python/SKILL.md`
  - 설명문과 runtime rule을 한글 중심으로 전환한다.
  - trigger description의 영문 기술어와 routing skill id는 유지한다.
- `dddjango/skills/implementation-python/agents/openai.yaml`
  - `short_description`과 `default_prompt`를 `X | None`, built-in generics, `Enum/StrEnum`, pydantic v2 boundary, async/concurrency, exceptions, Ruff, mypy, pyright까지 반영하도록 보정한다.
- `dddjango/skills/implementation-python/references/*.md`
  - 한글 중심 reference로 전환한다.
  - source basis를 짧게 표시한다.
  - Ruff/mypy/pyright, `TaskGroup`/`ExceptionGroup`/`except*` guidance를 보강한다.

## 수정하지 말아야 할 범위

- source reference 전체를 bundled reference로 복제하지 않는다.
- unresolved domain/API/DB/Django/test decision을 `implementation-python`이 흡수하지 않는다.
- 불필요한 새 reference 파일을 추가하지 않는다.
- runtime cache는 source skill 수정 후 별도 runtime-sync analysis/plan을 남기고 동기화한다.

## 작업 체크리스트

- [x] `SKILL.md` 한글 중심 전환 및 routing 유지
- [x] `agents/openai.yaml` metadata scope 보정
- [x] `typing.md` tooling guidance 보강
- [x] `dataclasses-enums.md` `Enum/StrEnum` 기준 한글화
- [x] `protocols-boundaries.md` async/exception guidance 보강
- [x] `pydantic-v2.md` boundary rule 한글화
- [x] source skill과 runtime cache 차이 확인
- [x] runtime-sync 필요 시 별도 analysis/plan 후 cache sync
- [x] validator 실행

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- skill 문서 설명문이 한글 중심이고 영문 기술어는 trigger vocabulary로만 남는다.
- `SKILL.md`, bundled references, `agents/openai.yaml`이 source reference와 충돌하지 않는다.
- required dimensions가 runtime skill에서 discoverable하다.
- skill reflection에 대한 Blocker 0, Major 0, 열린 Minor 0 상태를 재평가로 확인한다.

## 완료 확인

- `dddjango/skills/implementation-python/**` 설명문을 한글 중심으로 보정했다.
- bundled references와 metadata가 required dimensions를 노출한다.
- source skill과 runtime cache를 동기화했다.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` 통과.
