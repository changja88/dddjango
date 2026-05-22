# Failure Taxonomy

Use this taxonomy before editing skill, reference, evaluator, runner, or report
code.

| Class | Meaning | Default Action |
|---|---|---|
| `reference-gap` | Source reference lacks necessary basis or has weak provenance. | Fix reference first. |
| `skill-trigger` | `description` or handoff causes wrong skill selection. | Fix skill metadata/body. |
| `skill-runtime` | Runtime skill bundle differs from source or needs unavailable paths/tools. | Fix install/cache/runtime parity. |
| `case-gap` | Eval case does not represent the intended user behavior. | Fix case only after P4 is trusted. |
| `answer-gap` | Oracle/answer criteria miss required observations or allow overclaim. | Fix answer criteria. |
| `evaluator-undercheck` | Evaluator lets incomplete/bad output pass. | Fix evaluator and add fixture. |
| `evaluator-overcheck` | Evaluator flags valid output due to false positive. | Fix evaluator and add regression fixture. |
| `runner-artifact` | Runner failed to produce required raw/oracle/report artifacts. | Fix runner before adding cases. |
| `report-stale` | HTML/latest report does not reflect current raw artifacts. | Regenerate/fix report path logic. |
| `scoring-incomplete` | `not scored`, missing oracle, malformed oracle, or partial matrix. | Fix scoring/oracle pipeline. |
| `leakage` | Local path/private field appears in raw or persisted artifact. | Fail run; fix source of leak. |
| `variance` | Recent pass/fail disagreement without classification. | Record flake history and rerun/classify. |
| `infrastructure-blocked` | Permission, sandbox, external runner policy, or service access blocks validation. | Do not complete; request approval or record blocked. |

Rules:

- Do not expand eval cases while `runner-artifact`, `scoring-incomplete`, or
  `report-stale` is open.
- Do not edit a skill when the failure is only `answer-gap` or
  `evaluator-undercheck`.
- Do not complete a phase with open `infrastructure-blocked` unless that phase's
  gate explicitly allows blocked exit. P5-P8 do not allow blocked completion.

