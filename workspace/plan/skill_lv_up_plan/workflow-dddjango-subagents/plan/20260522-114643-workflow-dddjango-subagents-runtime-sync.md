수정 대상: runtime-sync

# workflow runtime sync 계획

## 수정 순서

1. `dddjango/skills/workflow-dddjango-subagents/SKILL.md`를 runtime cache의 같은 상대 경로로 복사한다.
2. `dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md`를 runtime cache의 같은 상대 경로로 복사한다.
3. Skill docs validator를 실행해 cache/source drift가 사라졌는지 확인한다.

## 완료 조건

- Runtime cache와 workspace source의 두 변경 파일이 일치한다.
- Skill docs validator가 통과한다.
