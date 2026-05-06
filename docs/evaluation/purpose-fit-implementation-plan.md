# dddjango Purpose-Fit Evaluation Implementation Plan

이 문서는 `docs/evaluation/purpose-fit-evaluation-plan.md`를 실제 코드와 파일
구조로 구현하기 위한 작업 계획이다. 목표는 빠르게 실행 가능한 최소 평가
프레임워크를 만들고, 이후 케이스와 rubric을 확장할 수 있게 하는 것이다.

## 구현 목표

1. `dddjango` 목적 기반 평가를 데이터 파일로 선언한다.
2. 같은 케이스를 `without-dddjango`, `with-dddjango` 변형으로 실행할 수 있게 한다.
3. `baseline`은 사람이 정의한 기대 기준으로 저장한다.
4. 자동 gate와 rubric 점수를 분리한다.
5. 실행할 때마다 JSON 결과와 로컬 HTML 리포트를 생성한다.
6. HTML 리포트에서 케이스별 `baseline`, `without-dddjango`, `with-dddjango`를 한눈에 비교한다.
7. 평가가 틀렸을 때 스킬을 수정하기 전에 평가 자체의 근거를 먼저 검토할 수 있게 한다.

## 권장 디렉터리 구조

```text
evals/dddjango/
├── README.md
├── baselines/
│   ├── c01-drf-order-api.md
│   ├── c02-ninja-order-create.md
│   ├── c03-tdd-coupon-policy.md
│   ├── c04-order-state-domain.md
│   └── c05-inventory-reservation.md
├── cases/
│   ├── core-policy.json
│   ├── code-structure.json
│   ├── holdout-adversarial.json
│   ├── review-refactor.json
│   ├── trigger-usability.json
│   ├── subagent-workflow.json
│   └── reference-maximum.json
├── rubrics/
│   ├── dimensions.json
│   ├── gates.json
│   ├── release-gates.json
│   └── score-schema.json
├── scripts/
│   ├── run_evaluation.py
│   ├── score_outputs.py
│   ├── render_report.py
│   └── validate_eval_config.py
└── reports/
    └── .gitkeep
```

생성되는 실행 결과는 `workspace/codex-eval/` 아래에 둔다. 이 경로는 로컬 실행
산출물이므로 git에 올리지 않는다.

```text
workspace/codex-eval/purpose-fit/<run-id>/
├── outputs/
│   ├── c01-drf-order-api.without-dddjango.md
│   └── c01-drf-order-api.with-dddjango.md
├── scores/
│   ├── c01-drf-order-api.score.json
│   └── summary.json
├── artifacts/
│   ├── c01-drf-order-api.without-dddjango.html
│   └── c01-drf-order-api.with-dddjango.html
└── report.html
```

## 데이터 모델

### Case

각 케이스는 JSON으로 정의한다.

```json
{
  "id": "c01-drf-order-api",
  "phase": "core-policy",
  "title": "DRF 요청을 Django Ninja로 전환",
  "prompt": "DRF ViewSet으로 주문 생성 API를 만들어줘.",
  "required_dimensions": [
    "drf_rejection",
    "django_ninja_api",
    "usability"
  ],
  "baseline": "baselines/c01-drf-order-api.md",
  "expected_skills": [
    "implementation-django-ninja",
    "architecture-api"
  ],
  "forbidden_patterns": [
    "rest_framework",
    "ModelSerializer",
    "ViewSet",
    "APIView"
  ],
  "required_patterns": [
    "Router",
    "Schema",
    "response={"
  ],
  "critical_gates": [
    "no_drf",
    "django_ninja_for_api",
    "no_false_execution"
  ]
}
```

### Dimension

`rubrics/dimensions.json`은 평가 축과 가중치를 정의한다.

```json
{
  "drf_rejection": {
    "label": "DRF Rejection",
    "weight": 20,
    "max_score": 100,
    "description": "DRF 요청을 dddjango 정책에 따라 Django Ninja 대안으로 전환하는지 평가한다."
  }
}
```

### Gate

`rubrics/gates.json`은 평균 점수와 무관하게 실패해야 하는 조건을 정의한다.

```json
{
  "no_drf": {
    "severity": "critical",
    "fail_if_any": [
      "rest_framework",
      "ModelSerializer",
      "ViewSet",
      "APIView"
    ],
    "message": "DRF 패턴을 생성하거나 권장하면 실패한다."
  }
}
```

### Score

각 케이스 채점 결과는 다음 구조를 따른다.

```json
{
  "case_id": "c01-drf-order-api",
  "variant": "with-dddjango",
  "total_score": 88,
  "gate_status": "pass",
  "dimension_scores": {
    "drf_rejection": 100,
    "django_ninja_api": 85,
    "usability": 80
  },
  "gate_results": [
    {
      "gate": "no_drf",
      "status": "pass",
      "evidence": []
    }
  ],
  "rationale": "DRF를 거부하고 Django Ninja Router/Schema 대안을 제시했다.",
  "artifact": "outputs/c01-drf-order-api.with-dddjango.md"
}
```

## 실행 방식

### 1. 설정 검증

```bash
python3 evals/dddjango/scripts/validate_eval_config.py
```

검증 항목:

- 모든 case id가 고유한가
- baseline 파일이 존재하는가
- required dimension이 `dimensions.json`에 정의되어 있는가
- critical gate가 `gates.json`에 정의되어 있는가
- forbidden/required pattern이 문자열 배열인가

### 2. 평가 실행

```bash
python3 evals/dddjango/scripts/run_evaluation.py --variant with-dddjango --case c01-drf-order-api
python3 evals/dddjango/scripts/run_evaluation.py --variant without-dddjango --case c01-drf-order-api
```

초기 구현에서는 runner가 프롬프트 파일과 실행 명령을 생성하는 것까지만 안정화한다.
Codex CLI 자동 실행은 마지막에 붙인다. 이렇게 해야 설치 상태, 플러그인 활성 상태,
CLI 옵션 차이 때문에 평가 프레임워크 자체가 흔들리는 문제를 줄일 수 있다.

### 3. 채점

```bash
python3 evals/dddjango/scripts/score_outputs.py --run-id <run-id>
```

초기 채점은 deterministic gate와 pattern 기반 신호만 자동화한다.
정성 rubric judge는 이후 확장 단계에서 추가한다.

### 4. HTML 리포트 생성

```bash
python3 evals/dddjango/scripts/render_report.py --run-id <run-id>
```

리포트는 다음을 반드시 포함한다.

- 전체 평균과 release gate 상태
- 케이스별 `baseline`, `without-dddjango`, `with-dddjango` 비교 표
- 평가 축별 평균
- critical gate 실패 목록
- release gate `needs_review` 상태와 수동 검토 필요 케이스
- reference rule 및 project structure 구조 검사 결과
- 원본 출력 HTML 변환본 링크
- 개선 우선순위

## Makefile 계획

현재 Makefile은 release 관련 명령만 남겨 둔 상태다. 새 평가는 검증 가능한 최소
명령만 추가한다.

```makefile
.PHONY: release test-release eval-dddjango eval-report

# dddjango 목적 기반 평가 설정을 검증하고 핵심 케이스를 실행한다.
eval-dddjango:
	python3 evals/dddjango/scripts/validate_eval_config.py
	python3 evals/dddjango/scripts/run_evaluation.py --suite core-policy
	python3 evals/dddjango/scripts/score_outputs.py --latest
	python3 evals/dddjango/scripts/render_report.py --latest

# 가장 최근 dddjango 평가 결과를 HTML 리포트로 다시 렌더링한다.
eval-report:
	python3 evals/dddjango/scripts/render_report.py --latest
```

자동 실행이 안정화되기 전에는 `eval-dddjango`가 dry-run 또는 fixture 기반으로
동작하게 하고, 실제 Codex 실행은 명시 옵션으로 분리한다.

```bash
python3 evals/dddjango/scripts/run_evaluation.py --suite core-policy --mode live
```

## 테스트 계획

`tests/test_purpose_fit_evaluation.py`를 추가한다.

필수 테스트:

1. case 파일 schema 검증.
2. baseline 파일 누락 검출.
3. gate가 forbidden pattern을 탐지하는지 검증.
4. required pattern 누락이 점수에 반영되는지 검증.
5. summary score가 variant별로 집계되는지 검증.
6. HTML report에 `baseline`, `without-dddjango`, `with-dddjango` 컬럼이 존재하는지 검증.
7. markdown artifact가 HTML로 변환되어 링크되는지 검증.

## 단계별 작업 계획

### Phase A: 평가 정의 골격

- [x] `evals/dddjango/README.md` 작성
- [x] `rubrics/dimensions.json` 작성
- [x] `rubrics/gates.json` 작성
- [x] `rubrics/release-gates.json` 작성
- [x] `rubrics/score-schema.json` 작성
- [x] `validate_eval_config.py` 구현
- [x] 설정 검증 테스트 작성

완료 기준:

- `python3 evals/dddjango/scripts/validate_eval_config.py` 성공
- `python3 -m unittest discover -s tests` 성공

### Phase B: 핵심 정책 케이스 C01-C05

- [x] `cases/core-policy.json` 작성
- [x] C01-C05 baseline 작성
- [x] 케이스별 required/forbidden pattern 정의
- [x] core-policy 케이스 검증 테스트 작성

완료 기준:

- 모든 core-policy case가 schema 검증 통과
- baseline과 gate 연결이 모두 유효

### Phase C: 채점기

- [x] `score_outputs.py` 구현
- [x] deterministic gate 평가 구현
- [x] required/forbidden pattern 평가 구현
- [x] dimension별 부분 점수 계산 구현
- [x] `summary.json` 생성 구현
- [x] scoring 테스트 작성

완료 기준:

- fixture output을 넣으면 score JSON이 안정적으로 생성됨
- DRF 포함 출력은 critical fail 처리됨

### Phase D: 리포터

- [x] `render_report.py` 구현
- [x] markdown output을 HTML artifact로 변환
- [x] summary table 구현
- [x] variant comparison table 구현
- [x] dimension table 구현
- [x] fail-fast gate table 구현
- [x] artifact link 검증 테스트 작성

완료 기준:

- `report.html`을 브라우저에서 열면 표가 보임
- artifact 클릭 시 다운로드가 아니라 HTML 페이지가 열림

### Phase E: Runner

- [x] `run_evaluation.py` dry-run 모드 구현
- [x] fixture/manual output 입력 모드 구현
- [ ] live Codex 실행 모드 설계
- [x] run-id 생성과 출력 경로 관리 구현
- [x] 실행/채점/리포터 CLI 옵션 구현

완료 기준:

- live 실행 없이도 fixture 기반 end-to-end 리포트 생성 가능
- 이후 live Codex 실행을 붙일 수 있는 인터페이스가 있음

### Phase F: Makefile 통합

- [x] `eval-dddjango` 추가
- [x] `eval-report` 추가
- [x] 각 명령에 한국어 주석 추가
- [x] release 명령과 평가 명령의 책임 분리 유지

완료 기준:

- `make eval-dddjango`가 최소 평가를 실행하고 HTML 리포트를 생성
- `make eval-report`가 최신 결과를 다시 렌더링

### Phase G: Live 평가 확장

- [x] `without-dddjango` 실행 절차 문서화
- [x] `with-dddjango` 실행 절차 문서화
- [x] Codex CLI live 실행 옵션 연결
- [x] 동일 prompt/동일 case 비교 보장
- [x] 결과 재현성 메타데이터 저장

완료 기준:

- 같은 케이스를 두 variant로 실행하고 한 리포트에서 비교 가능

### Phase H: 확장 케이스

- [x] review-refactor 케이스 추가
- [x] trigger-usability 케이스 추가
- [x] subagent-workflow 케이스 추가
- [x] subagent 역할 분해, skill mapping, handoff, 실행 계획, 통합 검증,
  허위 claim 방지 평가 보강
- [x] reference-maximum 케이스 추가
- [x] release gate 기준 재검토

완료 기준:

- 전체 목적 기반 평가가 한 번에 실행 가능
- 낮은 축을 기준으로 다음 스킬 개선 작업을 선정 가능

## 우선순위

바로 구현할 1차 범위는 Phase A-D까지다.

이유:

1. 평가 정의, gate, scoring, HTML report가 먼저 있어야 이후 live 실행 결과를
   흔들림 없이 비교할 수 있다.
2. live Codex 실행은 플러그인 설치 상태와 CLI 옵션에 영향을 받으므로 마지막에
   붙이는 편이 안정적이다.
3. 지금 가장 중요한 문제는 “평가 자체가 맞는가”이므로, 먼저 fixture 기반으로
   평가 체계의 타당성을 검증해야 한다.

## 1차 구현 완료 기준

1차 구현은 다음 조건을 만족하면 완료로 본다.

- `evals/dddjango/` 아래에 rubric, case, baseline, scripts가 생성됨
- C01-C05 핵심 정책 케이스가 정의됨
- fixture output을 대상으로 채점 가능
- HTML 리포트가 생성됨
- 리포트에 `baseline`, `without-dddjango`, `with-dddjango` 비교 표가 있음
- `python3 -m unittest discover -s tests` 통과
- `git diff --check` 통과

## 이후 개선 기준

1차 구현 후 실제 `with-dddjango` 결과가 기대보다 낮으면 바로 스킬을 고치지
않는다. 먼저 다음 순서로 확인한다.

1. 케이스 프롬프트가 목적을 제대로 자극하는가?
2. baseline이 너무 추상적이거나 과도하지 않은가?
3. gate가 단순 문자열 때문에 오탐하지 않는가?
4. 스킬 reference의 중요한 규칙이 rubric에 빠지지 않았는가?
5. 그래도 낮으면 해당 스킬의 `SKILL.md` 또는 reference를 수정한다.
