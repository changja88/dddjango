# P2 Goal Prompt - Skill Structure

```text
너는 dddjango Codex 플러그인 재구축 계획의 P2 Skill Structure를 수행한다.

목표:
각 skill이 Codex에서 발견 가능하고 과하게 로딩되지 않도록 SKILL.md, agents/openai.yaml, bundled resources 구조를 정리한다.

선행 조건:
- P1.5 usage cards가 complete다.

대상:
- dddjango/skills/*/SKILL.md
- dddjango/skills/*/agents/openai.yaml
- dddjango/skills/*/{references,scripts,assets}/
- workspace/plan/phases/p2-skill-structure/
- skill-creator reference: agents/openai.yaml 작성/검증 기준

허용 수정 범위:
- dddjango/skills/**
- workspace/plan/phases/p2-skill-structure/{analysis,plan,evidence,closure}/
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- workspace/reference/** 기준을 새로 발명하지 않는다. reference 부족이면 P1로 되돌리는 blocker로 기록한다.
- skill 내부에 README.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md, CHANGELOG.md를 만들지 않는다.
- SKILL.md에 과도한 reference 전문을 복사하지 않는다.
- 평가 case/runner는 수정하지 않는다.

해야 할 일:
1. P1.5 usage card를 기준으로 각 skill의 description 사용 조건/제외 조건을 검토한다.
2. SKILL.md frontmatter는 name, description만 사용하고 folder basename과 일치시킨다.
3. description은 120 words 목표, 180 words 또는 1200 chars hard limit로 관리한다.
4. SKILL.md body는 500줄 미만, 실행 절차와 resource navigation 중심으로 유지한다.
5. 상세 기준은 bundled references로 옮기되 SKILL.md에서 직접 링크한다.
6. agents/openai.yaml은 skill-creator의 openai_yaml 기준을 확인하고 SKILL.md와 일치시킨다.
7. plugin-creator 관점으로 .codex-plugin/plugin.json과 runtime path boundary를 확인한다.
8. stale/placeholder bundled resource를 제거하거나 issue로 기록한다.
9. analysis/plan/evidence를 작성하고 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- 가능한 경우 skill-creator quick validator 또는 동일 기준 local validator
- 가능한 경우 plugin-creator validate_plugin.py 또는 동일 기준 manifest/path validator
- git diff로 P2 허용 범위 밖 수정 여부 확인

완료 조건:
- 모든 skill이 frontmatter, description, body size, direct reference link 기준을 통과한다.
- agents/openai.yaml이 SKILL.md trigger 기대와 충돌하지 않는다.
- runtime files에 absolute local path, plugin root 밖 path traversal, source tree 의존이 없다.
- unknown Codex compatibility issue가 없다. 확인 불가하면 infrastructure-blocked 또는 blocked로 기록한다.
- validate_plan_governance.py가 통과한다.

권한/승인:
- 설치/cache/외부 command가 필요하면 먼저 사용자 승인 요청 후 진행한다.
- 권한 문제로 필수 검증이 막히면 complete 금지.

최종 응답:
- 수정한 skill/metadata 목록
- resource 이동/제거 요약
- plugin-creator 관점 리뷰 결과
- skill-creator 관점 리뷰 결과
- 검증 명령과 결과
- P2 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
