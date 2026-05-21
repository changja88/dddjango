# Implementation Django Ninja P2 Runtime Sync Plan

## 수정 이유

P2 source skill 수정 후 Codex runtime cache가 같은 내용을 가리키도록 동기화해야 한다. Source만 수정하면 실제 runtime에서 로드되는 skill이 stale해져 P2 종료 조건의 source/runtime 동기화가 깨진다.

## 수정 범위

- Source: `dddjango/skills/implementation-django-ninja/`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/`

## 수정하지 말아야 할 범위

- 다른 skill의 source/runtime cache는 수정하지 않는다.
- Runtime cache에 source skill에 없는 파일을 추가하지 않는다.
- `workspace/reference/**`와 `workspace/develop/eval/**`는 수정하지 않는다.

## 작업 체크리스트

- [x] Source skill 수정 범위를 확인한다.
- [x] Runtime cache를 source skill과 같은 내용으로 동기화한다.
- [x] `diff -qr`로 source/runtime parity를 확인한다.
- [x] skill validator를 실행해 source skill 문서 유효성을 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-django-ninja /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja`

## 완료 조건

- Source skill과 runtime cache가 `diff -qr` 기준 동일하다.
- Runtime cache sync가 다른 skill을 건드리지 않는다.
- 최종 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

## 완료 결과

- Runtime cache sync를 완료했다.
- Source/runtime diff는 차이 없음으로 확인했다.
