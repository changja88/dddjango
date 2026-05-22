# P7 Goal Prompt - Install Packaging

```text
너는 dddjango Codex 플러그인 재구축 계획의 P7 Install Packaging을 수행한다.

목표:
source plugin과 Codex install/cache가 일치하고, 설치된 runtime에서 high-risk user-like task가 의도한 skill을 로드하는지 최종 확인한다.

선행 조건:
- P6 integration eval이 complete다.

대상:
- dddjango/.codex-plugin/plugin.json
- dddjango/skills/**
- Codex local plugin install/cache
- workspace/plan/phases/p7-install-packaging/

허용 수정 범위:
- dddjango/.codex-plugin/plugin.json
- dddjango/skills/**는 설치/경로/cache parity 문제 해결에 필요한 narrow fix만
- workspace/plan/phases/p7-install-packaging/{analysis,plan,evidence,closure}/
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- .codex-plugin/ 아래에 plugin.json 외 파일을 추가하지 않는다.
- plugin root 밖 path traversal을 허용하지 않는다.
- source/cache diff가 있으면 complete 금지.
- installed-runtime user-like task 없이 설치 완료를 주장하지 않는다.

해야 할 일:
1. .codex-plugin/plugin.json의 skills path와 모든 manifest path field를 검증한다.
2. every manifest path field가 ./로 시작하고 plugin root 안에 머물며 required path가 존재하는지 확인한다.
3. Codex cache path, source/cache diff, skill count/name list를 evidence로 기록한다.
4. high-risk trigger family마다 설치된 Codex runtime에서 user-like task를 최소 1개 실행한다.
5. actual skill loaded, source/cache path, final answer/artifacts, false-trigger/exclusion behavior를 기록한다.
6. plugin-creator 관점으로 manifest/marketplace/cache update flow를 리뷰한다.
7. analysis/plan/evidence/closure와 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- manifest path validator 또는 동등한 parse/path check
- source/cache diff
- installed-runtime user-like task evidence
- 가능한 경우 plugin-creator validate_plugin.py 또는 동등 검증

완료 조건:
- Codex skill 목록에서 namespace가 의도대로 보인다.
- source/cache diff가 없다.
- plugin root 밖 runtime dependency가 없다.
- installed-runtime user-like task가 high-risk trigger family마다 의도한 skill을 로드했다.
- false-trigger/exclusion behavior가 usage card와 일치한다.

권한/승인:
- Codex plugin install/update/cache command, app-server, GUI/browser 접근이 필요하면 사용자 승인 요청 후 진행한다.
- 승인 후에도 policy가 막히면 complete 금지. infrastructure-blocked로 기록한다.

최종 응답:
- manifest/cache/install evidence 경로
- source/cache diff 결과
- installed-runtime user-like task matrix
- plugin-creator 리뷰 결과
- 검증 명령과 결과
- P7 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
