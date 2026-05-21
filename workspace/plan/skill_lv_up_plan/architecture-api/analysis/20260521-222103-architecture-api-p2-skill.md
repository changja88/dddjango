수정 대상: skill
원인 분류: P2 metadata-routing-source alignment gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# Architecture API P2 Skill Analysis

## 평가 범위

- Source skill: `dddjango/skills/architecture-api/SKILL.md`
- Bundled references: `dddjango/skills/architecture-api/references/*.md`
- Metadata: `dddjango/skills/architecture-api/agents/openai.yaml`
- Source reference: `workspace/reference/architecture-api/reference/final.md`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api/`
- OpenAI metadata 기준: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`

## P2 기준별 평가

1. 실제 사용자 표현과 사용 예시는 REST API 계약 설계 목적과 대체로 일치한다. 다만 `subagents`, `서브에이전트`, `역할 분해`, `병렬 검토`, `책임 분배`, `dddjango workflow` 같은 workflow handoff 표현이 본문에만 구체적으로 있고 frontmatter에는 약하다.
2. Frontmatter `description`은 REST 계약 설계의 긍정 trigger를 충분히 담지만, source reference의 non-REST 제외 범위와 workflow 한국어 trigger를 더 직접적으로 드러낼 필요가 있다.
3. 본문에만 숨은 trigger 규칙이 일부 있다. workflow handoff 표현과 non-REST 제외 범위를 frontmatter에도 반영해야 한다.
4. `agents/openai.yaml`은 기본 구조와 optional field 제약을 지키지만, `default_prompt`가 request/response contracts, content negotiation, deprecation을 명시하지 않아 `SKILL.md`의 핵심 범위를 조금 덜 반영한다.
5. `agents/openai.yaml`은 `display_name`, `short_description`, `default_prompt`만 포함하고, 명시 요청 없는 icon/brand/dependencies/policy field를 추가하지 않았다.
6. Source skill과 runtime cache는 현재 `diff -qr` 기준 동일하다. Source 수정 후 runtime cache sync가 필요하다.

## 독립 리뷰 통합

### skill-creator 관점 리뷰

- Blocker: 없음.
- Major: Source reference는 모든 API 통신에 HTTPS 사용을 요구하지만 bundled runtime reference는 민감 정보나 credential을 다루는 API로 한정해 더 약한 지침을 제공한다.
- Minor: source reference의 GraphQL, gRPC, SOAP, WebSocket, HATEOAS, API Gateway 제외가 runtime trigger metadata와 본문에 충분히 드러나지 않는다.
- Minor: workflow/subagent 한국어 trigger가 body-only routing에 가깝다.
- Note: 목적 명확성, progressive disclosure, `agents/openai.yaml` 기본 제약은 양호하다.

### 독립 source/runtime alignment 리뷰

- Blocker: 없음.
- Major: 없음.
- Minor: workflow/subagent routing 표현이 body-only에 가깝다.
- Minor: `agents/openai.yaml`이 request/response contracts, deprecation, content negotiation을 덜 드러낸다.
- Note: source/runtime cache parity와 optional interface field 제약은 양호하다.

## 최초 통합 판정

- Blocker: 0
- Major: 1
- 열린 Minor: 2

## 수정 필요 범위

- `dddjango/skills/architecture-api/SKILL.md` frontmatter에 workflow/subagent 한국어 trigger와 non-REST 제외 범위를 보강한다.
- `dddjango/skills/architecture-api/SKILL.md` 본문 routing에도 non-REST 제외 범위를 명시해 source reference와 runtime body가 같은 경계를 말하게 한다.
- `dddjango/skills/architecture-api/references/rest-contracts.md`의 HTTPS 지침을 source reference처럼 모든 API 통신에 적용되도록 수정한다.
- `dddjango/skills/architecture-api/agents/openai.yaml` default prompt에 request/response contracts, content negotiation, deprecation을 반영한다.

## 수정하지 말아야 할 범위

- `workspace/reference/architecture-api/reference/final.md`는 이번 P2에서 부족하다고 판정하지 않았으므로 수정하지 않는다.
- Django Ninja 구현, pytest fixture, DB 저장 방식, DDD aggregate 판단을 architecture-api skill로 끌어오지 않는다.
- `agents/openai.yaml`에 icon, brand color, dependencies, policy 같은 optional interface field를 추가하지 않는다.
- Runtime cache는 source 수정 후 동일 내용으로만 동기화한다.

## 수정 후 재평가

- `SKILL.md` frontmatter에 `subagents/서브에이전트`, `역할 분해`, `병렬 검토`, `책임 분배`, `dddjango workflow`를 반영해 workflow handoff trigger가 본문에만 남지 않게 했다.
- `SKILL.md` frontmatter와 routing 본문에 GraphQL, gRPC, SOAP, WebSocket, HATEOAS, API Gateway 제외 범위를 반영했다.
- `rest-contracts.md`의 HTTPS 지침을 모든 API 통신에 적용하도록 source reference와 맞췄다.
- `agents/openai.yaml` default prompt에 request/response contracts, content negotiation, deprecation을 추가했고 optional interface field는 추가하지 않았다.
- Source skill 수정 후 runtime cache sync 분석/계획을 별도로 작성하고 runtime cache를 동기화했다.

## 검증 결과

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`: 통과.
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`: 통과.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`: 통과, warning 0.
- `diff -qr dddjango/skills/architecture-api /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api`: 차이 없음.

## 최종 판정

- Blocker: 0
- Major: 0
- 열린 Minor: 0
- 남은 검증 이슈: 없음.
