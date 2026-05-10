# Case 101

Implement the requested change in the supplied fixture repository so the eval runner can capture actual code artifacts.

## Request

```text
orders/services.py의 create_order_summary 함수가 주문 total과 line count를 함께 반환하도록 구현해줘. 테스트가 있다면 함께 맞춰줘.
```

## Context

- This case is code-backed.
- The subject repository is selected by `workspace/develop/evals/cases/plugin/code-capture.json`.
- Do not read private evaluator files, rubrics, or prior run findings.

## Output To Save

- Final response transcript.
- Commands actually run.
- Not-run checks and reasons.
- Actual changed source files and diff captured by the operator runner.
