# dddjango 플러그인 개발 프로세스

| 체크 | 단계 | 목표 |
|---|---|---|
| [ ] | P1. 스킬의 reference 반영도 점검 | 각 skill이 source reference 기준을 빠짐없이 반영하는지 확인한다. |
| [ ] | P2. `SKILL.md` 목적 명확성 점검 | 각 skill의 목적, trigger, 제외 조건이 명확한지 확인한다. |
| [ ] | P3. skill 책임 경계 점검 | skill 간 책임과 handoff가 겹치지 않는지 확인한다. |
| [ ] | P4. 개별 skill 평가 점검 | 각 skill이 reference 기준을 반영해 동작하는지 검증할 평가 항목, case, answer가 준비되어 있는지 확인한다. |
| [ ] | P5. skill 연계와 플러그인 평가 점검 | skill 연계와 subagent workflow를 검증하되 각 skill의 책임과 progressive disclosure를 유지하는지 확인한다. |
| [ ] | P6. 평가 실행 | 준비된 개별 skill 평가와 플러그인 평가를 실행해 실제 결과를 생성한다. |
| [ ] | P7. HTML report 최신성 점검 | 실행한 평가 결과가 항상 최신 HTML report로 일관되게 출력되는지 확인한다. |
| [ ] | P8. 평가 실패 원인 분류와 반복 수정 | 평가 실패가 발생했을 때 원인을 먼저 분류하고 해당 대상만 좁게 수정한다. |
