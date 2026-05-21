수정 대상: skill

# architecture-implementation-patterns P2 skill 수정 계획

## 수정 이유

`SKILL.md` 본문과 source reference가 risky write consistency handoff를 주요 사용 조건으로 다루지만 frontmatter description에는 해당 사용자 표현이 충분히 없다. Skill trigger 판단이 frontmatter에서 시작되므로, risky write와 workflow/subagent 제외 조건을 description에 반영해 본문-only trigger를 없앤다.

## 수정 범위

- `dddjango/skills/architecture-implementation-patterns/SKILL.md` frontmatter `description`

## 수정하지 말아야 할 범위

- `agents/openai.yaml`은 이미 `display_name`, `short_description`, `default_prompt`가 SKILL.md와 정렬되어 있고 optional interface field가 없으므로 수정하지 않는다.
- Bundled references는 source reference와 일치하므로 수정하지 않는다.
- Source reference는 부족하지 않으므로 P2에서 억지로 수정하지 않는다.
- eval pack과 validator는 수정하지 않는다.

## 작업 체크리스트

- [ ] `description`에 risky write, 결제/재고/예약/환불/권한/ledger, transaction owner, side-effect timing, idempotency storage handoff 표현을 추가한다.
- [ ] `description`의 workflow handoff 문장에 subagents, role decomposition, parallel review, dddjango workflow 제외 조건을 명시한다.
- [ ] `description`이 과도한 구현 지침이나 본문 중복으로 길어지지 않도록 trigger 중심으로 유지한다.
- [ ] Source skill 수정 후 runtime cache diff를 확인한다.
- [ ] Runtime cache가 다르면 별도 runtime-sync 분석/계획을 작성하고 동기화한다.
- [ ] Validator와 `diff -qr`를 실행한다.
- [ ] 재리뷰에서 Blocker 0, Major 0, 열린 Minor 0을 확인한다.

## 검증 명령

- `diff -qr dddjango/skills/architecture-implementation-patterns /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Frontmatter description과 본문 routing/runtime rule 사이에 숨은 trigger 차이가 없다.
- `agents/openai.yaml`이 SKILL.md와 충돌하지 않는다.
- Source skill과 runtime cache가 동일하다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
