# implementation-django-web P3 runtime-sync 계획

## 수정 이유

P3 skill 수정으로 source skill과 runtime cache의 `SKILL.md`가 달라졌다. dddjango plugin runtime이 같은 지침을 사용하도록 cache를 source와 동기화해야 한다.

## 수정 범위

- source: `dddjango/skills/implementation-django-web/SKILL.md`
- target: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/SKILL.md`

## 수정하지 말아야 할 범위

- 다른 skill runtime cache는 건드리지 않는다.
- `agents/openai.yaml`과 bundled references는 source에서 변경하지 않았으므로 불필요하게 복사하지 않는다.
- source reference와 plan 문서는 runtime cache에 복사하지 않는다.

## 체크리스트

- [x] source `SKILL.md`를 runtime cache `SKILL.md`로 복사한다.
- [x] `diff -qr`로 source/runtime parity를 확인한다.
- [x] validators를 실행한다.
- [x] 검증 실패가 있으면 target 관련 실패인지, 기존 다른 skill drift인지 분리한다.

## 검증 명령

```bash
diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

## 완료 조건

- `diff -qr` 출력이 없다.
- runtime cache는 source skill의 P3 수정과 동일하다.
