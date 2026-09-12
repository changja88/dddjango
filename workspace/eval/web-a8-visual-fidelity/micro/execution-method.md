# 실행 방식

Baseline trial 1을 시작하기 전 codex exec --ephemeral --sandbox workspace-write --skip-git-repo-check --json --color never --output-last-message response.md 명령을 시도했다. 모델 호출 전 app-server client EPERM으로 exit 1. trial-01/stderr.log와 events.jsonl은 이 시작 실패의 로그이며 행동 표본이 아니다. 권한 확대나 설정/auth 변경 없이 단일 fresh-context subagent 방식으로 바꿨다.

실제 행동 표본은 collaboration.spawn_agent fork_turns="none"으로 한 번에 한 개씩 실행한다. trial-call-template.txt의 경로만 각 trial 디렉터리로 치환한다. 모델·추론 설정은 부모 기본값을 상속하며 override하지 않는다. child에게 diagnosis.md·oracle.md·다른 실행의 결과·candidate 지침은 제공하지 않는다. 각 호출은 해당 trial의 invocation.json에, 최종 반환 원문은 response.md에 보존한다. handoff.md는 역할의 자기 보고이고 소스 diff·구조 검사 결과와 수동으로 대조한다. 전체 도구 raw transcript는 이 collaboration 환경에서 별도 export되지 않으므로 raw CLI events로 가장하지 않는다.

이 실행은 전체 native /dddjango-web 호출이 아니며 inputs gate·Django 호스트·수집·Reviewer·Coordinator의 상호작용을 검증하지 않는다. browser unavailable은 정상 조건으로 고정했고 어떠한 trial의 시각 PASS도 요구하지 않는다.
