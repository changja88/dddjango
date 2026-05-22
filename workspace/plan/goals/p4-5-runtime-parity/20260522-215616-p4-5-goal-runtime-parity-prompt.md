# P4.5 Goal Prompt - Runtime Parity

```text
너는 dddjango Codex 플러그인 재구축 계획의 P4.5 Runtime Parity Precheck를 수행한다.

목표:
model-backed P5/P6 실행 전에 source plugin과 실제 Codex runtime/cache plugin이 같은지 확인하고, 설치/캐시/발견 증거를 현재 파일 기준으로 고정한다.

선행 조건:
- P4 eval skeleton이 complete다.

대상:
- dddjango/
- dddjango/.codex-plugin/plugin.json
- Codex local plugin install/cache
- workspace/plan/phases/p4-5-runtime-parity/

허용 수정 범위:
- workspace/plan/phases/p4-5-runtime-parity/{analysis,plan,evidence,closure}/
- 설치/cache sync가 필요할 때만 dddjango plugin install/cache 관련 command 실행
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- runtime parity 확인 없이 P5/P6 model-backed eval을 실행하지 않는다.
- source/cache diff가 있는데 complete 금지.
- plugin root 밖 파일을 runtime dependency로 인정하지 않는다.

해야 할 일:
1. Codex local install/cache path와 marketplace/source enabled state를 기록한다.
2. .codex-plugin/plugin.json parse 결과와 manifest path validation 결과를 저장한다.
3. installed/cache plugin path, skill count/name list, source/cache diff 결과를 저장한다.
4. 가능한 Codex discovery evidence를 raw output으로 남긴다: /plugins transcript/screenshot, app-server plugin/list/read JSON, skills/list, codex plugin CLI output 중 실제 가능한 것.
5. installed cache에서 representative bundled script 실행이 필요한 경우 PLUGIN_ROOT가 cache root를 가리키는 상태로 실행한다.
6. evidence와 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- source/cache diff check
- manifest path validation
- 최소 1개 Codex discovery smoke

완료 조건:
- source/cache diff가 없다.
- plugin root 밖 reference 의존이 없다.
- Codex discovery smoke가 최소 1개 skill에서 통과한다.
- model-backed P5/P6 실행 전 설치/cache/discovery raw evidence가 현재 파일 기준으로 존재한다.

권한/승인:
- Codex install/cache command, app-server, GUI/browser 접근이 필요하면 사용자 승인 요청 후 진행한다.
- 승인 후에도 policy가 막으면 complete 금지. infrastructure-blocked로 기록한다.

최종 응답:
- install/cache path
- source/cache diff 결과
- discovery raw evidence 경로
- manifest validation 결과
- 검증 명령과 결과
- P4.5 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
