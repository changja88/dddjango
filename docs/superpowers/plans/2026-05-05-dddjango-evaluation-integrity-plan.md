# dddjango Evaluation Integrity Plan

**Goal:** 스킬 개선 전에 dddjango 평가가 실제 목적을 제대로 측정하도록 보정한다.

**Evaluation Purpose:** dddjango는 일반 답변 점수보다 Django/DDD/Django Ninja/TDD/DB 컨벤션 준수를 유도하는 플러그인이다. 평가는 설치 유효성, trigger 정확도, 컨벤션 준수, 실사용성, 비용 대비 효과를 분리해서 봐야 한다.

## Phase 1: Generation Leakage 제거

- [x] `dddjango` variant에만 들어가던 `scoring_focus` 기반 `Focus on:` 지시를 기본 비활성화한다.
- [x] legacy 디버깅용으로만 `--allow-generation-hints`를 둔다.
- [x] positive/negative/ambiguous/conflict trigger 케이스에서 `trigger_type` 기반 정답 행동 주입을 기본 제거한다.

## Phase 2: Skill-unit과 Plugin-real 분리

- [x] `standard` variant set은 `baseline` vs local `dddjango` skill-unit 평가로 유지한다.
- [x] `plugin-real` variant set을 추가해 `baseline` vs `dddjango-plugin`을 생성한다.
- [x] `dddjango-plugin` 실행은 local `SKILL.md` path와 case-specific instruction을 주입하지 않는다.
- [x] `make eval-plugin-real`을 추가한다.

## Phase 3: Grader 보수화

- [x] dddjango positive trigger에 주던 자동 점수 보너스를 제거한다.
- [x] `items/meta`, migration verification, Result Type, query-pattern-first 규칙을 단순 단어 탐지보다 구조적으로 검증한다.
- [ ] API/DB/TDD별 구조 검증 규칙을 더 넓힌다.

## Phase 4: 실사용성 평가 확대

- [ ] `real-repo` fixture를 최소 12개로 확대한다.
- [ ] diff 적용, `manage.py check`, pytest 결과를 HTML report 상단 gate로 노출한다.
- [ ] 실패 케이스 10개 이상은 수동 리뷰 notes를 작성한다.

## Phase 5: Gate 재정의

- [ ] high-baseline suite에는 +15% lift gate 대신 absolute conformance gate를 적용한다.
- [ ] release gate는 `make eval-conformance`와 `make eval-plugin-real`을 모두 요구한다.
- [ ] Claude 평가는 결제 또는 API key 준비 후 같은 목적 체계로 추가한다.

## Current Decision

현재까지의 dddjango 점수는 스킬 유효성 신호로는 참고하되, 최종 배포 성능 판단은 보정된 `plugin-real` 평가 이후에 한다.
