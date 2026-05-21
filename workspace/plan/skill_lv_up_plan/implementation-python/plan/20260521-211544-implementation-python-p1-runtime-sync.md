수정 대상: runtime-sync

## 수정 이유

source skill 변경 후 runtime cache가 stale하면 실제 Codex runtime에서 수정된 `implementation-python` guidance를 사용하지 못한다. P1 종료 조건은 source skill과 runtime cache 동기화 확인을 요구한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/`
  - source `dddjango/skills/implementation-python/`와 같은 파일 내용으로 동기화한다.

## 수정하지 말아야 할 범위

- 다른 skill runtime cache는 수정하지 않는다.
- source reference나 validator는 runtime sync 작업에서 추가 수정하지 않는다.
- runtime cache에 source에 없는 임시 파일을 추가하지 않는다.

## 작업 체크리스트

- [x] source skill directory를 runtime cache로 복사
- [x] `diff -qr`로 parity 확인
- [x] `validate_skill_docs.py --phase all`로 runtime/source parity 확인

## 검증 명령

- `diff -qr dddjango/skills/implementation-python /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `diff -qr` 출력이 없다.
- runtime-sync 관련 Blocker 0, Major 0, 열린 Minor 0 상태를 재평가로 확인한다.

## 완료 확인

- active runtime cache가 source skill과 동일하다.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` 통과.
