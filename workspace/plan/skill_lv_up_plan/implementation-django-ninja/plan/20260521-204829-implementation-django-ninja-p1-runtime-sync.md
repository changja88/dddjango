# implementation-django-ninja P1 runtime sync 계획

대상: implementation-django-ninja
생성 시각: 2026-05-21 20:48:29 KST
분석 문서: `workspace/plan/skill_lv_up_plan/implementation-django-ninja/analysis/20260521-204829-implementation-django-ninja-p1-runtime-sync.md`

## 수정 이유

Source skill 수정 후 runtime cache가 stale해지면 Codex runtime은 개선된 skill을 사용하지
못한다. P1 종료 조건은 source skill과 runtime cache 동기화 확인을 요구한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja/`

## 수정하지 말아야 할 범위

- 다른 runtime cached skill은 수정하지 않는다.
- source reference를 runtime cache에 복사하지 않는다.
- eval artifact는 수정하지 않는다.

## 작업 체크리스트

- [x] 수정 전 source/runtime diff를 확인한다.
- [x] source skill 수정 후 runtime cache에 동일 파일을 sync한다.
- [x] `diff -qr`로 source/runtime 차이가 없는지 확인한다.
- [x] validator를 실행해 source skill docs가 유효한지 확인한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-django-ninja /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-ninja`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- source skill과 runtime cache의 `SKILL.md`, `agents/openai.yaml`, `references/**`가 일치한다.
- runtime sync 관련 Blocker 0, Major 0, 열린 Minor 0이다.

완료 상태: 충족.
