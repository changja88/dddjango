# Eval Report Redesign Design

Date: 2026-05-10

## Goal

Replace the current eval report reading experience with a new report built around evaluation items. The report must make it immediately clear what was evaluated, how baseline performed, how with-dddjango performed, and where the detailed response and evaluation can be inspected.

Existing report layout and previous visual-explainability attempts are out of scope. Raw artifacts may be reused as data sources, but the new UI and data contract should be designed from the evaluation-item view first.

## Primary Screen

The report starts with a summary area, followed by filters and a single evaluation-item table.

The summary area contains type-specific summaries rather than one global score. It should include one section for each normalized score type present in the report:

- Numeric score summary, when numeric score items exist.
- Pass/fail summary, when pass/fail items exist.
- Hard gate summary, when hard gate items exist.
- Narrative summary, when qualitative items exist.
- Short conclusion.
- Key risks.

Each section has at least one metric. Numeric sections show baseline aggregate, with-ddjango aggregate, and delta when scores are parseable. Numeric aggregation uses normalized `value/max` ratios; raw numeric scores without a maximum are aggregated only when the item declares a compatible scale. Pass/fail sections show pass, partial, and fail counts per variant. Hard gate sections show failure counts per variant. Narrative sections show item counts and representative conclusion/risk text rather than a forced numeric aggregate.

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

Type filters are mutually exclusive. Change filters are mutually exclusive. Text search combines with the active type and change filters. Search matches evaluation item title, Korean test content, baseline summary, with-ddjango summary, and score text. Filter controls show counts for the currently available result set. If no rows match, the table shows an empty state instead of disappearing.

The main table columns are:

- Evaluation item.
- Type.
- Baseline score.
- With dddjango score.
- Change.
- Baseline response/evaluation.
- With dddjango response/evaluation.

The first column must show the original Korean test content, with an optional shorter Korean description below it. It must not show only an internal case id. Long baseline and with-ddjango content must not be expanded inline inside the table. The response/evaluation cells show a concise summary plus a visible button labelled `상세 보기`. Both buttons open the same comparison modal for that row.

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

The modal is an accessible dialog. It has `role="dialog"`, `aria-modal="true"`, a visible heading referenced by `aria-labelledby`, a visible close button, Escape-to-close behavior, focus trapping while open, and focus returns to the triggering `상세 보기` button after close.

## Data Contract

The renderer should produce a new report data shape centered on `evaluation_items`.

An evaluation item is one row that has a single baseline response/evaluation and a single with-ddjango response/evaluation. For the current eval artifacts, this usually maps to one case-level evaluator judgment because existing scores and good/poor judgments are case-level. If a future evaluator emits per-request, per-rubric, hard-gate, or artifact-check judgments with both variant evaluations, the renderer may emit those as separate rows. The row must declare its source granularity.

```json
{
  "schema_version": "eval-report-v2",
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
      "source_granularity": "case",
      "source_case_ids": ["case-001"],
      "test_content_ko": "요청에 맞는 dddjango skill을 선택했는지 평가한다.",
      "description_ko": "요청에 맞는 dddjango skill을 선택했는지 평가한다.",
      "score_type": "pass_fail",
      "score_type_source": "explicit",
      "higher_is_better": true,
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

Summary sections are generated from the normalized `score_type` values present in `evaluation_items`. A type-specific summary section is omitted when the report has no items of that type.

`score_type` is the canonical normalized type used by the summary, filters, table `Type` column, and modal `Type` label. Allowed values are:

- `numeric`
- `pass_fail`
- `hard_gate`
- `narrative`

When source data has an explicit type, the renderer copies it into `score_type` and sets `score_type_source` to `explicit`. When source data lacks a type, the renderer infers the type, writes the inferred canonical value into `score_type`, and sets `score_type_source` to `inferred`.

- `3/5`, `8.2/10`, or similar: `numeric`.
- `pass`, `fail`, `partial`, or similar: `pass_fail`.
- hard gate failure language: `hard_gate`.
- Otherwise: `narrative`.

Score display is free-form per evaluation item. The UI must not force all items into one numeric scale.

`source_granularity` allowed values are `case`, `request`, `rubric`, `hard_gate`, and `artifact_check`. `score_type_source` allowed values are `explicit` and `inferred`. `higher_is_better` defaults to `true` and only affects numeric comparison.

`change.direction` is also canonical. Allowed values are:

- `improved`
- `regressed`
- `unchanged`
- `mixed`
- `not_comparable`

Numeric scores are compared by normalized ratio when both sides are parseable as compatible `value/max` scores; `higher_is_better` controls direction. Pass/fail scores are compared using `fail < partial < pass`. Hard gate items compare failure count, where fewer failures is better. Narrative items use an explicit evaluator-provided change direction when available; otherwise they are `not_comparable`. Multi-part rows with both improvements and regressions are `mixed`.

The canonical variant data keys are `baseline` and `with_dddjango`. Raw artifact filenames may still use the variant slug `with-dddjango`; the renderer is responsible for mapping that slug into the canonical JSON key. The old `caseStories`, `evaluationFlow`, and `withDddjango` keys are not required for `schema_version: "eval-report-v2"`.

Variant fields are required for both `baseline` and `with_dddjango`: `score`, `response_summary`, `response`, `evaluation_summary`, `evaluation`, and `evidence`. If a focused run was intentionally not scored, the renderer still emits honest values such as `score: "not scored"` and `evaluation: "평가를 실행하지 않은 artifact capture smoke run입니다."` rather than omitting the field.

## Generation Flow

The renderer reads raw eval results and existing evaluator analysis data, then builds:

- `summary`.
- `evaluation_items`.

For current artifacts, response fields come from raw variant responses, score fields come from evaluator scores or verdicts, and evaluation fields are assembled from evaluator judgment fields such as strengths, gaps, score notes, hard gate results, and analysis artifacts. Existing raw artifacts, commands, events, diffs, and source captures may be linked from `evidence`, but they are supporting material rather than the primary reading path.

The static HTML report renders only from `schema_version: "eval-report-v2"`, `summary`, and `evaluation_items`. Existing report structures may remain in old generated reports, but the redesigned template and validator should treat v2 as a separate contract rather than requiring old fields.

## Validation

Report validation should fail if:

- `schema_version` is not `eval-report-v2`.
- `summary` is missing.
- `summary.sections` is missing or empty.
- `summary.conclusion` is missing.
- `summary.risks` is missing.
- A normalized `score_type` present in `evaluation_items` has no matching summary section.
- `evaluation_items` is missing or empty.
- An evaluation item lacks `id`, `title`, `source_granularity`, `test_content_ko`, `score_type`, or `score_type_source`.
- An evaluation item uses an unsupported `source_granularity` or `score_type_source`.
- An evaluation item uses an unsupported `score_type`.
- An evaluation item lacks baseline `score`, `response_summary`, `response`, `evaluation_summary`, `evaluation`, or `evidence`.
- An evaluation item lacks with-ddjango `score`, `response_summary`, `response`, `evaluation_summary`, `evaluation`, or `evidence`.
- An evaluation item lacks `change.direction` or uses an unsupported direction.
- The HTML template lacks required anchors: `#report-summary`, `#evaluation-filters`, `#evaluation-items-table`, and `#comparison-modal`.
- Browser acceptance checks cannot open the comparison modal from both baseline and with-ddjango detail buttons.
- The opened modal does not show both baseline and with-ddjango columns for the same evaluation item.
- The opened modal does not expose close/Escape behavior or focus return to the triggering button.

## Non-Goals

- Do not preserve the old report layout.
- Do not make raw artifact index pages the primary navigation surface.
- Do not require one global total score.
- Do not inline full long responses inside table cells.
- Do not implement nested cards or a marketing-style page.
