수정 대상: answer
원인 분류: answer

## 배경

`case-code-web-detail`은 Django Web 구현 산출물에서 context/display fallback, template presentation boundary, static reference, render verification을 검증하는 code-backed case다.

## 문제

- answer oracle의 `reference_basis`가 `workspace/develop/eval`과 `dddjango/skills/source-reference-audit/SKILL.md`처럼 넓거나 잘못된 path를 사용한다.
- source reference인 `workspace/reference/implementation-django-web/reference/final.md`와 target skill의 `SKILL.md`, bundled references를 직접 가리키지 않아 P4의 source-reference 기반 검증 증거가 약하다.
- coverage tag가 `implementation-django-web` 직접성을 충분히 표시하지 않는다.

## 수정 방향

- `case-code-web-detail.yaml`의 reference basis를 Django Web source/reference/runtime artifact로 좁힌다.
- target behavior와 coverage tag에 direct Django Web implementation 기준을 보강한다.
- public case는 이미 private oracle을 누설하지 않으므로 유지한다.

## 리뷰 기록

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 수정 후 reviewer로 확인한다.
