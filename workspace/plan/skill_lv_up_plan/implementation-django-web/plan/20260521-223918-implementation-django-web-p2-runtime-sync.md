# implementation-django-web P2 runtime sync 계획

## 수정 이유

P2 source skill 수정으로 `dddjango/skills/implementation-django-web/`와 runtime cache가 달라졌다. goal 종료 조건은 source skill과 runtime cache가 같은 내용을 가리키는 것이므로 runtime cache sync가 필요하다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/agents/openai.yaml`

## 수정하지 말아야 할 범위

- 다른 runtime skill cache는 수정하지 않는다.
- Runtime cache에 source에 없는 optional metadata나 임시 파일을 추가하지 않는다.
- Source reference와 plan 문서는 runtime cache로 복사하지 않는다.

## 수정 순서

1. Source `SKILL.md`와 `agents/openai.yaml`을 runtime cache 동일 경로에 복사한다.
2. `diff -qr`로 source/runtime parity를 확인한다.
3. 필수 validator를 실행한다.

## 체크리스트

- [x] Runtime `SKILL.md`가 source `SKILL.md`와 같다.
- [x] Runtime `agents/openai.yaml`이 source `agents/openai.yaml`과 같다.
- [x] Source/runtime `diff -qr`가 무출력이다.
- [x] 다른 cache 경로를 수정하지 않았다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache가 일치한다.
- P2 최종 검증 명령과 리뷰 결과가 최종 보고에 남는다.

## 실행 결과

- Runtime cache sync 완료.
- `diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web`: passed, no output
