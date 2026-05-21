# dddjango 플러그인 개발 프로세스

| 체크 | 단계 | 목표 |
|---|---|---|
| [ ] | P1. 스킬의 reference 반영도 점검 | 각 skill이 source reference와 필요한 bundled resources를 빠짐없이 반영하는지 확인한다. |
| [ ] | P2. `SKILL.md` 목적 명확성 점검 | 각 skill의 실제 사용 예시, 목적, trigger, 제외 조건과 agents/openai.yaml metadata가 일치하는지 확인한다. |
| [ ] | P3. skill 책임 경계 점검 | skill 간 책임과 handoff가 겹치지 않고 progressive disclosure가 유지되는지 확인한다. |
| [ ] | P4. 개별 skill 평가 점검 | 각 skill이 reference 기준을 반영해 동작하는지 validation integrity를 지키는 평가 항목, case, answer가 준비되어 있는지 확인한다. |
| [ ] | P5. skill 연계와 플러그인 평가 점검 | skill 연계와 subagent workflow를 검증하되 각 skill의 책임과 progressive disclosure를 유지하는지 확인한다. |
| [ ] | P6. 평가 실행 | 준비된 validator, 개별 skill 평가, 플러그인 연계 평가, eval-all/bucket 평가를 분리 실행해 실제 결과를 생성한다. |
| [ ] | P7. HTML report 최신성 점검 | 실행 run id와 latest/latest-valid HTML report가 일치하는지 확인한다. |
| [ ] | P8. 평가 실패 원인 분류와 반복 수정 | 평가 실패와 eval-all/bucket 차이를 정해진 수정 대상 기준으로 먼저 분류하고 해당 대상만 좁게 수정한다. |

## 프로세스별 체크리스트

### P1. 스킬의 reference 반영도 점검

- [ ] 대상 skill이 참조해야 하는 source reference의 기준 파일과 범위를 확인한다.
- [ ] `SKILL.md` 본문과 bundled references가 source reference의 핵심 규칙을 누락하지 않았는지 확인한다.
- [ ] source reference와 skill 내용 사이에 충돌하거나 과장된 규칙이 없는지 확인한다.
- [ ] `scripts/`, `references/`, `assets/`가 필요한 작업인지 확인하고, 필요한 bundled resources가 skill에서 발견 가능하게 연결되어 있는지 확인한다.
- [ ] 실제 사용자 예시나 생성/검증된 예시별로 필요한 `scripts/`, `references/`, `assets/`가 도출됐고, 필요 없는 resource directory나 placeholder가 남지 않았는지 확인한다.
- [ ] fallback 또는 provisional source를 사용하는 경우 상태와 한계를 명확히 기록했는지 확인한다.

### P2. `SKILL.md` 목적 명확성 점검

- [ ] 실제 사용 예시와 사용자 표현이 skill의 목적과 일치하는지 확인한다.
- [ ] frontmatter `description`에 사용 조건, trigger, 제외 조건이 충분히 들어 있는지 확인한다.
- [ ] 본문에만 있는 trigger 규칙이 없는지 확인한다.
- [ ] `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`와 어긋나지 않는지 확인한다.
- [ ] `agents/openai.yaml`은 `references/openai_yaml.md` 기준을 반영하고, `display_name`, `short_description`, `default_prompt`를 결정적으로 생성/갱신했으며, 명시 요청 없는 optional interface field를 추가하지 않았는지 확인한다.
- [ ] source skill과 runtime cache skill이 같은 내용을 가리키는지 확인한다.

### P3. skill 책임 경계 점검

- [ ] 각 skill의 책임과 다른 skill로 넘겨야 하는 handoff 기준을 확인한다.
- [ ] 두 skill 이상이 같은 문제를 서로 다른 기준으로 해결하도록 겹치지 않는지 확인한다.
- [ ] architecture, implementation, test, source audit, workflow 역할이 서로 침범하지 않는지 확인한다.
- [ ] `SKILL.md`는 핵심 절차만 담고 세부 reference는 필요한 때만 로딩되도록 구성되어 있는지 확인한다.
- [ ] `SKILL.md`가 500줄 미만의 핵심 절차 중심인지, 세부 자료는 1단계 reference로 직접 연결되는지, 긴 reference에는 목차나 검색 힌트가 있는지 확인한다.
- [ ] 같은 정보가 `SKILL.md`와 bundled reference에 중복 저장되어 컨텍스트 낭비나 불일치 위험을 만들지 않는지 확인한다.
- [ ] reference 연결이 너무 깊거나 숨겨져 있어 에이전트가 필요한 자료를 찾지 못하는 구조가 아닌지 확인한다.

### P4. 개별 skill 평가 점검

- [ ] 각 skill의 목적과 reference 기준을 검증하는 평가 case가 준비되어 있는지 확인한다.
- [ ] positive case와 negative case가 skill의 사용 조건과 제외 조건을 모두 검증하는지 확인한다.
- [ ] public case가 answer oracle이나 의도한 정답을 누설하지 않는지 확인한다.
- [ ] answer oracle이 reference 기준보다 과도하거나 부족한 판정을 요구하지 않는지 확인한다.
- [ ] case, answer, evaluator가 같은 skill 목적을 검증하도록 서로 일치하는지 확인한다.

### P5. skill 연계와 플러그인 평가 점검

- [ ] 여러 skill이 함께 필요한 시나리오에서 역할 분해와 handoff가 자연스럽게 동작하는지 확인한다.
- [ ] subagent workflow가 각 skill의 책임을 보존하고 불필요한 병렬화나 역할 중복을 만들지 않는지 확인한다.
- [ ] critical path 작업과 sidecar 작업이 구분되는지 확인한다.
- [ ] 실제 실행하지 않은 subagent, 검증, 도구 사용을 실행한 것처럼 주장하지 않도록 평가가 잡아내는지 확인한다.
- [ ] forward-testing/subagent 검증은 fresh thread에서 사용자 요청과 유사한 prompt로 실행하고, raw artifact만 전달하며 기대 답, 의도한 수정, 이전 결론을 노출하지 않는지 확인한다.
- [ ] 반복 검증 사이에 subagent 산출물이 다음 실행의 힌트로 남지 않도록 정리했는지 확인한다.
- [ ] 플러그인 단위 평가가 개별 skill 품질 문제와 연계 문제를 구분해 드러내는지 확인한다.

### P6. 평가 실행

- [ ] 평가 전에 `validate_skill_docs.py`, 필요한 bucket의 `validate_eval_bucket_pack.py`, `validate_plan_constraints.py`를 실행하고 결과를 기록한다.
- [ ] 개별 skill targeted 평가를 먼저 실행하고 결과를 확인한다.
- [ ] 개별 skill targeted 평가와 별도로 플러그인 연계/subagent workflow 평가를 실행하고, 개별 skill 품질 문제와 연계 문제를 구분해 기록한다.
- [ ] bucket 평가와 eval-all 평가를 분리 실행해 차이가 생기는지 확인한다.
- [ ] 각 실행의 run id, bucket, case, variant, 실패 위치를 기록한다.
- [ ] 평가 실행 후 생성된 run artifact에는 `validate_eval_run.py`를 실행해 raw output, stderr, evaluator 결과, local path, oracle schema 보존 상태를 확인한다.
- [ ] 실패가 발생하면 수정 전에 raw output, stderr, evaluator 결과를 보존하고 원인 분류로 넘긴다.

### P7. HTML report 최신성 점검

- [ ] 최신 run id와 HTML report에 표시된 run id가 일치하는지 확인한다.
- [ ] `latest`와 `latest-valid`가 의도한 최신 실행을 가리키는지 확인한다.
- [ ] report가 bucket별 pass/fail, case별 결과, variant별 차이를 확인할 수 있게 출력되는지 확인한다.
- [ ] 실패한 case의 raw output, stderr, evaluator 근거로 이동할 수 있는지 확인한다.
- [ ] 이전 run의 report를 최신 결과로 오인할 수 있는 stale pointer가 없는지 확인한다.

### P8. 평가 실패 원인 분류와 반복 수정

- [ ] 실패를 수정하기 전에 `reference`, `skill`, `case`, `answer`, `evaluator`, `runtime-sync`, `report`, `model-variance`, `process`, `cleanup`, `tooling`, `none` 중 하나로 먼저 분류한다.
- [ ] bucket 단독 실행과 eval-all 실행의 차이가 있으면 runner, report, latest pointer, 병렬 실행 영향 중 어디인지 먼저 확인한다.
- [ ] 원인 분석은 해당 범주의 `analysis/` 아래에 작성하고 첫 줄에 `수정 대상:`을 적는다.
- [ ] 개선 계획은 분석 이후 같은 대상의 `plan/` 아래에만 작성한다.
- [ ] 수정은 분류된 대상에만 좁게 적용하고, targeted 평가, bucket 평가, eval-all 순서로 재검증한다.
- [ ] 수정 후 `skill-creator` 관점을 포함한 독립 리뷰 또는 순차 fallback 리뷰를 다시 수행해 Blocker/Major/Minor가 0개인지 확인하고, 남은 항목이 있으면 원인 분류부터 반복한다.
