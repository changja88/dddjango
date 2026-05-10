# Eval Report Redesign Design

Date: 2026-05-10

## Goal

Replace the current eval report reading experience with a new report built around evaluation items. The report must make it immediately clear what was evaluated, how baseline performed, how with-dddjango performed, and where the detailed response and evaluation can be inspected.

Existing report layout and previous visual-explainability attempts are out of scope. Raw artifacts may be reused as data sources, but the new UI and data contract should be designed from the evaluation-item view first.

## Primary Screen

The report starts with a summary area, followed by filters and a single evaluation-item table.

The summary area contains type-specific summaries rather than one global score. It should support:

- Numeric score summary, when numeric score items exist.
- Pass/fail summary, when pass/fail items exist.
- Hard gate summary, when hard gate items exist.
- Narrative summary, when qualitative items exist.
- Short conclusion.
- Key risks.

The filter bar supports:

- All items.
- Numeric.
- Pass/fail.
- Hard gate.
- Narrative.
- Improved.
- Regressed.
- Unchanged.
- Text search.

The main table columns are:

- Evaluation item.
- Type.
- Baseline score.
- With dddjango score.
- Change.
- Baseline response/evaluation.
- With dddjango response/evaluation.

The first column must show the Korean test content or evaluation-item description, not only an internal case id. Long baseline and with-ddjango content must not be expanded inline inside the table. The table cells should show a concise summary or a detail button.

## Detail Modal

Clicking either response/evaluation cell opens one large comparison modal for that evaluation item. The modal always shows both baseline and with-ddjango together.

The modal header shows:

- Evaluation item title.
- Type.
- Change status.
- Baseline score.
- With dddjango score.

The modal body is a two-column comparison on desktop:

- Baseline score.
- Baseline evaluation summary.
- Baseline response.
- Baseline detailed evaluation.
- Baseline evidence.
- With dddjango score.
- With dddjango evaluation summary.
- With dddjango response.
- With dddjango detailed evaluation.
- With dddjango evidence.

On narrow screens, the two columns stack vertically.

The modal should use most of the viewport: `width: min(95vw, 1600px)` and `height: min(90vh, 1000px)`. Each comparison column should scroll internally when content is long, so long code in one side does not push the other side away. Code blocks in responses or evaluations should use readable monospace formatting and enough horizontal space for review.

## Data Contract

The renderer should produce a new report data shape centered on `evaluation_items`.

```json
{
  "summary": {
    "sections": [
      {
        "type": "numeric",
        "title": "정량 점수 항목",
        "metrics": [
          {
            "label": "baseline 평균",
            "value": "3.1/5"
          }
        ]
      }
    ],
    "conclusion": "이번 평가의 핵심 결론",
    "risks": ["남은 리스크"]
  },
  "evaluation_items": [
    {
      "id": "routing-accuracy",
      "title": "라우팅 정확도",
      "description_ko": "요청에 맞는 dddjango skill을 선택했는지 평가한다.",
      "score_type": "pass_fail",
      "baseline": {
        "score": "fail",
        "response_summary": "응답 요약",
        "response": "원문 응답",
        "evaluation_summary": "평가 요약",
        "evaluation": "상세 평가",
        "evidence": ["근거"]
      },
      "with_dddjango": {
        "score": "pass",
        "response_summary": "응답 요약",
        "response": "원문 응답",
        "evaluation_summary": "평가 요약",
        "evaluation": "상세 평가",
        "evidence": ["근거"]
      },
      "change": {
        "direction": "improved",
        "label": "개선"
      }
    }
  ]
}
```

Summary sections are generated from the `score_type` values present in `evaluation_items`. A type-specific summary section is omitted when the report has no items of that type.

`score_type` is explicit when available. If it is missing, the report renderer may infer it from score strings as a fallback:

- `3/5`, `8.2/10`, or similar: `numeric`.
- `pass`, `fail`, `partial`, or similar: `pass_fail`.
- hard gate failure language: `hard_gate`.
- Otherwise: `narrative`.

Score display is free-form per evaluation item. The UI must not force all items into one numeric scale.

## Generation Flow

The renderer reads raw eval results and any existing analysis data, then builds:

- `summary`.
- `evaluation_items`.

The static HTML report renders only from that structure. Existing raw artifacts, commands, events, diffs, and source captures may be linked from `evidence`, but they are supporting material rather than the primary reading path.

## Validation

Report validation should fail if:

- `summary` is missing.
- `evaluation_items` is missing or empty.
- An evaluation item lacks Korean test content or description.
- An evaluation item lacks baseline score, response, or evaluation.
- An evaluation item lacks with-ddjango score, response, or evaluation.
- An evaluation item lacks change direction.
- The HTML template lacks summary rendering, filters, the evaluation-item table, or the large comparison modal.

## Non-Goals

- Do not preserve the old report layout.
- Do not make raw artifact index pages the primary navigation surface.
- Do not require one global total score.
- Do not inline full long responses inside table cells.
- Do not implement nested cards or a marketing-style page.
