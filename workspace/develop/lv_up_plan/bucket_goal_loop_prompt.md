# Bucket Goal Loop Prompt

```text
<bucket> bucket을 goal로 잡고, complete hard gate를 모두 통과할 때까지 `lv_up_plan` 루프로 개선해줘. blocker로 멈출 수는 있지만, blocker가 남아 있으면 goal을 complete 처리하지 마.

1. `create_goal`로 이번 bucket의 목표를 만든다.
   - 목표: "<bucket> bucket의 현재 평가 결과를 분석하고, complete hard gate를 모두 통과할 때까지 반복 개선한다."
   - goal은 현재 세션의 실행 핸들로만 쓰고, 중요한 판단은 파일에 기록한다.

2. 기준 평가 결과를 확인한다.
   - 최신 run 또는 지정된 run에서 fail, blocked, hard gate failure를 우선 확인한다.
   - 그다음 partial, 낮은 delta, baseline과 차이가 없는 항목을 확인한다.

3. 한 번의 try에서는 failure family 하나만 선택한다.
   - 사용자 명령 단위는 bucket 하나다.
   - 반복 기록 단위는 try 하나다.
   - 수정 단위는 failure family 하나다.

4. 분석 문서를 작성한다.
   - 위치: `workspace/develop/lv_up_plan/<bucket>/analysis/try-n-<short-topic>.md`
   - 원인을 분류한다.
     - eval/oracle 문제
     - public case 문제
     - skill 문제
     - plugin 문제
     - runtime/cache/source 문제
     - reference 문제
     - 모델 한계
   - overfit, private oracle leakage, eval-specific 문구 삽입 위험을 기록한다.

5. 수정 계획 문서를 작성한다.
   - 위치: `workspace/develop/lv_up_plan/<bucket>/plan/try-n-<short-topic>.md`
   - analysis와 plan은 같은 try 번호를 사용한다.
   - 목표, 실패 요약, 수정 대상, 수정하지 않을 대상, 검증 계획, 성공 기준, 실패 시 다음 try를 기록한다.
   - 이번 try가 몇 번째 skill 수정인지, 어떤 skill 파일을 왜 고치는지 기록한다.

6. 작게 수정한다.
   - 분석과 계획에 적은 failure family만 고친다.
   - eval case의 정답 문장, case id, private oracle 내용을 runtime skill, reference, plugin metadata, public prompt에 넣지 않는다.
   - 같은 skill을 다시 고치면 새 try 문서에 이전 수정과 이번 수정의 차이를 적는다.
   - 여러 skill을 한 try에서 고쳐야 하면, 왜 한 failure family 안의 같은 원인인지 설명한다.

7. 재평가한다.
   - 먼저 targeted case를 실행한다.
   - 그다음 같은 bucket의 adjacent regression case 1~2개를 실행한다.
   - 안정되면 필요할 때 bucket 전체 평가를 실행한다.
   - generated `runs/`, raw transcript, report html은 커밋하지 않는다.

8. 반복한다.
   - 문제가 남아 있으면 `try-n+1`로 analysis와 plan을 새로 작성하고 반복한다.
   - 새 try를 시작할 때 이전 try의 수정 파일, eval 결과, 남은 실패를 먼저 요약한다.
   - blocker가 나오면 멈추되, goal은 complete 처리하지 않는다.
   - 같은 failure family를 3번 이상 수정해도 개선이 없으면 blocker로 정리하고 complete 처리하지 않는다.

9. complete hard gate를 확인한다.
   - 최신 bucket 전체 평가에서 fail, blocked, hard gate failure, unscored, missing artifact가 없어야 한다.
   - 이번 goal에서 고친 모든 failure family의 targeted eval이 pass여야 한다.
   - adjacent regression eval이 pass여야 한다.
   - skill 문서 검증, eval bucket pack 검증, diff 검증이 통과해야 한다.
   - runtime/cache를 쓰는 평가라면 workspace source와 runtime cache의 반영 상태를 확인해야 한다.
   - overfit/leakage scan에서 case id, private oracle, eval-specific 정답 문구가 runtime skill/reference/plugin metadata/public prompt에 없어야 한다.
   - 최종 다방면 skill review를 통과해야 한다.
     - trigger/routing 적합성
     - progressive disclosure와 reference 분리
     - validation integrity와 overfit/leakage 방지
     - runtime/cache/source 일관성
     - 실제 eval behavior와 회귀 위험
   - `skill-creator` 기준 리뷰를 통과해야 한다.
     - SKILL.md는 간결하고 핵심 절차만 담아야 한다.
     - 상세 기준은 필요한 경우 references로 분리되어야 한다.
     - agents/openai.yaml이 SKILL.md와 어긋나면 안 된다.
     - 불필요한 README, changelog, quick reference 같은 보조 문서를 skill에 추가하면 안 된다.
     - 추가/수정한 scripts는 실행 검증되어야 한다.
   - 최종 리뷰에서 major, minor, nit 중 하나라도 open finding이 남아 있으면 goal을 complete 처리하지 않는다.
   - 어떤 검증이든 실행하지 못했으면 goal을 complete 처리하지 말고 blocker 또는 residual risk로 남긴다.

10. 완료 보고를 한다.
   - 작성한 try 문서
   - 수정한 source 파일
   - 총 try 횟수
   - skill별 수정 횟수
   - 실행한 eval과 결과
   - complete hard gate 통과 여부
   - 최종 다방면 skill review 결과
   - `skill-creator` 리뷰 결과
   - blocker 또는 residual risk
   - Serena 사용 여부 또는 생략 이유
```
