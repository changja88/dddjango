1. 평가 항목 선택
    - fail, blocked, hard gate failure 우선
    - 그다음 partial, delta가 낮거나 baseline과 차이가 없는 항목
    - 마지막으로 pass지만 응답 품질이 애매한 항목
2. 실패 원인 분류
    - eval/oracle 문제: 채점 기준이 틀렸거나 너무 모호함
    - public case 문제: 문제가 평가하려는 능력을 제대로 유도하지 못함
    - skill 문제: 트리거, 절차, progressive disclosure, handoff 지침 부족
    - plugin 문제: metadata, routing, cache/source, marketplace/package 불일치
    - reference 문제: 스킬이 읽어야 할 근거 문서가 부족하거나 찾기 어려움
    - 모델 한계: 스킬로 고칠 수 없는 일반 추론 실패
3. 수정 위치 결정
    - 반복 절차가 약하면 SKILL.md
    - 긴 도메인 지식이면 references/
    - 매번 같은 검증/동기화가 필요하면 scripts/
    - 트리거/노출/라우팅 문제면 plugin.json, agents/openai.yaml, marketplace/cache 쪽
    - 평가가 잘못됐으면 answer/*.yaml 또는 case 자체
4. 작게 수정
    - 한 번에 여러 bucket을 고치지 말고, 실패 family 하나만 고칩니다.
    - SKILL.md는 길게 만들지 말고 핵심 절차만 넣고, 자세한 기준은 reference로 빼는 게 맞습니다.
    - 평가 정답을 맞추기 위한 문구를 skill에 넣는 건 금지해야 합니다. 그건 overfit입니다.
5. 재평가
    - 수정한 항목 1개만 다시 실행
    - 같은 bucket의 인접 case 1~2개도 같이 실행해서 부작용 확인
    - 통과하면 전체 병렬 평가 또는 해당 bucket 전체 평가
6. 커밋
    - skill/plugin/source/eval case 수정만 커밋
    - runs/, report html, raw output 같은 개발 산출물은 커밋하지 않음

  1. workflow: subagent 책임 분리, 실제 실행 claim, fallback이 핵심이라 dddjango의 차별점에 직접 연결됨
  2. runtime / plugin: with-dddjango가 제대로 노출되고 baseline과 격리되는지 확인
  3. source: reference basis가 충분한지 확인
  4. response: 파일 수정 없는 판단 품질 개선
  5. code: 실제 구현 품질 개선. 비용이 크니 앞단이 안정된 뒤 하는 게 낫습니다