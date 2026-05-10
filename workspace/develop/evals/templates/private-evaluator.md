# Private Evaluator Template

Keep this material private from forward-test agents.

## Case ID

- Public packet:
- Scenario family:
- Evaluation mode:
- Scenario tags:

## Expected Observation

- Expected route or skill combination:
- Required evidence:
- Must-not-do:

## Applicable Gates And Dimensions

- Plugin hard gates:
- Common hard gates:
- Scored dimensions:

## Artifacts

- Raw output:
- Command output:
- Source/cache evidence:
- Leakage evidence:

## Finding Classification

For each finding, record:

- severity: `blocking`, `major`, or `minor`
- defect type: `skill trigger`, `instruction`, `reference`, `workflow`, `runtime packaging`, `cache sync`, or `eval protocol`
- case id
- artifact path
- failed hard gate or scored dimension
- rerun scope

## Pass Criteria

- No hard gate failure.
- No blocking, major, or minor finding.
- Required evidence exists, or the case is marked not-run as a blocker.
- Any accepted exception links to the source gap, owner, expiry or revisit condition, and follow-up.
