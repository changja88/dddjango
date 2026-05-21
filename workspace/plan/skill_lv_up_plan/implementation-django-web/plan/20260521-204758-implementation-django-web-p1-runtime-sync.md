# implementation-django-web P1 runtime sync 계획

## 수정 이유

Source skill과 runtime cache가 다르면 Codex runtime이 stale provisional guidance를 계속 사용할 수 있다. P1 종료 조건은 source skill과 runtime cache 동기화 여부 확인을 요구하므로 cache를 source와 동일하게 맞춘다.

## 수정 범위

- 동기화 대상: `dddjango/skills/implementation-django-web/`
- 동기화 위치: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/`
- 검증: source와 runtime cache의 recursive diff

## 수정하지 말아야 할 범위

- 다른 runtime cache skill은 수정하지 않는다.
- Source skill을 runtime cache에 맞춰 되돌리지 않는다.
- eval pack과 validator script는 수정하지 않는다.

## 작업 체크리스트

- [x] source skill 디렉터리 내용을 runtime cache skill 디렉터리에 복사한다.
- [x] `diff -ru`로 source/cache 차이가 없는지 확인한다.
- [x] 검증 validator를 실행한다.
- [x] analysis 문서에 최종 리뷰 결과를 갱신한다.

## 검증 명령

- `diff -ru dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache의 recursive diff가 없다.
- Runtime cache가 dedicated Django Web guidance를 포함한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
