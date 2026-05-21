# implementation-django-web P1 provenance 보완 계획

## 수정 이유

독립 P1 리뷰에서 dedicated source reference의 출처 약어가 adjacent Django reference보다 덜 추적 가능하다는 Minor가 발견됐다. P1 종료 조건의 source reference 충분성과 traceability를 강화하기 위해 URL을 추가한다.

## 수정 범위

- 수정: `workspace/reference/implementation-django-web/reference/final.md`
- 갱신: 관련 analysis 문서의 최종 재평가

## 수정하지 말아야 할 범위

- Reference 기능 범위를 새로 확장하지 않는다.
- Skill/runtime 문서는 provenance URL 보강 대상이 아니다.
- Eval pack은 수정하지 않는다.

## 작업 체크리스트

- [x] 출처 약어에 concrete URL을 추가한다.
- [x] Reference 충분성 최종 판정을 analysis 문서에 반영한다.
- [x] Required validators를 실행한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source reference가 P1 기능 범위와 provenance traceability를 모두 만족한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
