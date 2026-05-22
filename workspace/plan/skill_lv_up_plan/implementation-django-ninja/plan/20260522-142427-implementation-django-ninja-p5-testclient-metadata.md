수정 대상: skill

# implementation-django-ninja P5 TestClient metadata 계획

## 수정 범위

- `dddjango/skills/implementation-django-ninja/agents/openai.yaml`
- runtime cache sync가 필요하면 같은 파일을 plugin cache에 동기화한다.

## 절차

1. short description을 Router/Schema/error/TestClient criteria 중심으로 바꾼다.
2. SKILL.md 본문은 이미 pytest mechanics를 `implementation-test`로 handoff하므로 수정하지 않는다.
3. skill docs validator와 response/plugin/runtime 관련 validator를 재실행한다.
4. runtime cache를 동기화한 경우 source/cache diff를 확인한다.

## 완료 조건

- UI metadata가 pytest/test implementation ownership을 overclaim하지 않는다.
- Django Ninja adapter 책임과 implementation-test 책임 경계가 유지된다.
- 관련 validator가 통과한다.
