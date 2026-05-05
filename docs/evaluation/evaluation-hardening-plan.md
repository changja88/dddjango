# dddjango Evaluation Hardening Plan

이 문서는 `dddjango` 평가 체계를 실제 플러그인 성능 평가로 사용하기 전에 반드시
완성해야 하는 기준과 작업 순서를 정의한다.

## 결론

현재 `evals/dddjango` 구현은 목적 기반 평가의 시작점이지만, 아직 실제 성능
평가가 아니다. 현재 fixture 결과는 평가 파이프라인이 파일을 만들고, 채점하고,
HTML 리포트를 렌더링할 수 있는지만 보여준다.

따라서 다음 원칙을 적용한다.

1. fixture 결과는 플러그인 가치 판단에 사용하지 않는다.
2. live Codex 실행 전에는 release gate를 통과/실패로 선언하지 않는다.
3. 평가 자체가 목적에 맞는지 검증하는 테스트를 먼저 만든다.
4. 문자열 기반 자동 점수는 낮은 신뢰도의 signal로만 사용한다.
5. 최종 판단은 baseline criteria, 구조적 검사, manual/judge rationale이 함께 있어야 한다.

## 완성 기준

평가 체계가 "사용 가능"하다고 보려면 아래 조건을 모두 만족해야 한다.

| 영역 | 완료 기준 |
| --- | --- |
| Scope coverage | core policy, review/refactor, trigger/usability, subagent workflow, reference maximum suite가 존재한다 |
| Fixture isolation | fixture/smoke run은 실제 성능 평가와 명령어, 리포트 문구, release gate가 분리된다 |
| Live execution | 동일 prompt를 `without-dddjango`, `with-dddjango`로 실제 실행하고 metadata를 저장한다 |
| Missing output | 누락된 case/variant output은 조용히 제외하지 않고 실패로 처리한다 |
| Gate quality | DRF 금지 설명과 DRF 코드 생성을 구분한다 |
| TDD quality | RED/GREEN/REFACTOR 문자열뿐 아니라 실패 테스트, 최소 구현, 리팩터링 근거를 본다 |
| Korean-first | 한글 존재 여부가 아니라 한국어 비율과 사용자 실행 가능성을 본다 |
| Structural checks | Django Ninja import, Router decorator, Schema class, response mapping을 구조적으로 확인한다 |
| Baseline use | baseline criteria가 리포트 표시뿐 아니라 채점/검토 근거로 연결된다 |
| Release gate | release gate가 계산되고 실패 시 non-zero exit를 낸다. 단, live mode에서만 적용한다 |
| Auditability | prompt, output, score, gate evidence, metadata, artifact link가 모두 남는다 |
| Calibration | 좋은/나쁜/경계 샘플이 기대 score/gate 범위로 평가된다 |

## 수정 우선순위

### Phase 0: 오해 방지

- [x] fixture 평가는 smoke test로 격리한다.
- [x] `make eval-dddjango`가 fixture 점수를 실제 성능처럼 만들지 않게 한다.
- [x] 문서에 fixture 결과는 성능 평가가 아니라고 명시한다.
- [x] README의 평가 상태 설명을 현재 구현 상태와 맞춘다.

### Phase 1: 평가 스펙 보강

- [x] `required_patterns`, `expected_skills`, `baseline`, `reference_usage`가 실제 채점에 어떻게 쓰이는지 정의한다.
- [x] release gate를 live 전용으로 정의한다.
- [x] automatic signal, structural check, manual/judge score를 분리한다.
- [x] 각 dimension에 "좋은 답변의 여러 허용 경로"를 정의한다.

### Phase 2: Gate 오탐 줄이기

- [x] DRF 코드 생성과 DRF 금지 설명을 구분한다.
- [x] `no_false_execution`에서 모순 문장을 실패로 잡는다.
- [x] `korean_first`를 한글 포함 여부에서 한국어 중심성 검사로 바꾼다.
- [x] `tdd_red_first`가 한국어 표현도 인정하게 한다.
- [x] `select_for_update`, `@dataclass` 같은 구현 취향을 필수 gate에서 제거한다.

### Phase 3: Missing/Release 판단

- [x] 누락된 output을 실패 score로 생성한다.
- [x] release gate evaluator를 구현한다.
- [x] fixture mode에서는 release gate를 실행하지 않거나 항상 "not applicable"로 표시한다.
- [ ] live mode에서 release gate 실패 시 non-zero exit를 낸다.

### Phase 3.5: 평가 항목 캘리브레이션

- [x] 좋은 DRF 거부 답변이 DRF gate 오탐 없이 통과한다.
- [x] 실제 DRF 코드 생성 답변은 실패한다.
- [x] 한국어 TDD 표현도 TDD gate를 통과한다.
- [x] FastAPI 요청에 dddjango 오염이 없으면 통과한다.
- [x] FastAPI 요청에 Django Ninja를 섞으면 실패한다.
- [x] Problem Details reference maximum 샘플이 통과한다.

### Phase 4: Coverage 확장

- [x] review-refactor suite 추가.
- [x] trigger-usability suite 추가.
- [x] subagent-workflow suite 추가.
- [x] reference-maximum suite 추가.
- [x] Django web/template/API error standard 케이스 추가.

### Phase 5: Live 실행

- [x] live runner를 구현한다.
- [x] plugin version, Codex version, command, model, prompt, timeout, stderr, exit status를 metadata에 저장한다.
- [x] `without-dddjango`, `with-dddjango`가 같은 prompt와 같은 격리 workspace에서 실행되는지 검증한다.
- [x] live 결과를 HTML에서 fixture와 명확히 구분한다.

## 다음 작업

다음 구현은 Phase 1부터 진행한다. 즉, 케이스를 더 많이 만들기 전에 평가 데이터
모델과 채점 구조를 먼저 고친다.

권장 작업 순서:

1. scoring 결과에 `score_kind`를 추가한다: `signal`, `structural`, `manual_required`.
2. `required_patterns`를 채점에 반영하되, hard fail이 아니라 signal로 둔다.
3. missing output 실패 처리를 구현한다.
4. DRF/TDD/Korean gate 오탐을 먼저 줄인다.
5. release gate evaluator를 live 전용으로 추가한다.
