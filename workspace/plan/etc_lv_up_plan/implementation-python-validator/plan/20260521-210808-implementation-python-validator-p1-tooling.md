수정 대상: tooling

## 수정 이유

P1에서 보강한 `implementation-python` runtime surface가 후속 변경으로 사라지는 것을 최소한의 자동 검증으로 잡아야 한다. validator가 semantic quality를 완전히 판정할 수는 없지만, required topic artifacts와 핵심 phrase 존재는 smoke check로 보호할 수 있다.

## 수정 범위

- `workspace/scripts/validate_skill_docs.py`
  - `implementation-python` 전용 check 함수를 추가한다.
  - `SKILL.md`, `agents/openai.yaml`, bundled references가 required topics를 포함하는지 좁게 검사한다.
- `workspace/scripts/test_validate_skill_docs.py`
  - `implementation-python` topic omission을 잡는 focused unit test를 추가한다.

## 수정하지 말아야 할 범위

- source reference 내용을 validator에 장문으로 복제하지 않는다.
- 자연어 품질 전체를 validator가 판단하게 만들지 않는다.
- 다른 skill의 validator rule을 바꾸지 않는다.
- eval runner나 eval pack은 수정하지 않는다.

## 작업 체크리스트

- [x] validator에 `implementation-python` topic coverage check 추가
- [x] generated skill과 runtime cache 검증 경로 모두에서 해당 check 호출
- [x] focused unit test 추가
- [x] validator와 관련 tests 실행

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_skill_docs.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `implementation-python` required topic이 빠지면 validator test가 실패한다.
- 현재 skill 문서와 runtime cache는 validator를 통과한다.
- tooling 관련 Blocker 0, Major 0, 열린 Minor 0 상태를 재평가로 확인한다.

## 완료 확인

- `workspace/scripts/test_validate_skill_docs.py`가 required topic phrase와 metadata under-claim 회귀를 검증한다.
- `.venv/bin/python -B workspace/scripts/test_validate_skill_docs.py` 통과.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` 통과.
