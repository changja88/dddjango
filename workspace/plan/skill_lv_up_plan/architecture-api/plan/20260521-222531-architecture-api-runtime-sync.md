# Architecture API P2 Runtime Sync Plan

## 수정 이유

P2 source skill 수정 후 Codex runtime cache가 같은 내용을 가리켜야 한다. Source와 runtime cache가 달라지면 실제 skill 실행 시 P2 수정 결과가 반영되지 않는다.

## 수정 범위

- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/`

## 수정하지 말아야 할 범위

- Source reference와 eval material은 수정하지 않는다.
- 다른 skill runtime cache는 수정하지 않는다.
- Runtime cache에 source에 없는 파일이나 optional metadata를 추가하지 않는다.

## 작업 체크리스트

- [x] Source skill의 현재 내용을 runtime cache `architecture-api` 폴더에 동기화한다.
- [x] `diff -qr`로 source/runtime cache parity를 확인한다.
- [x] `validate_skill_docs.py --phase all --skills-dir dddjango/skills`로 runtime sync validator도 확인한다.

## 완료 결과

- Runtime cache sync를 완료했다.
- `diff -qr` 기준 source와 runtime cache 차이가 없다.
- Skill validator는 validation 통과, warning 0이다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/architecture-api /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api`

## 완료 조건

- Source skill과 runtime cache가 `diff -qr` 기준 동일하다.
- Skill validator가 architecture-api runtime sync 문제를 보고하지 않는다.
