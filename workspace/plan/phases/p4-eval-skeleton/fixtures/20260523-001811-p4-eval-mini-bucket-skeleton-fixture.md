# P4 Mini-Bucket Fixture Matrix

Raw fixture source:
`workspace/develop/eval/fixtures/mini-bucket/`

| case | baseline expected | with-plugin expected | primary proof |
|---|---:|---:|---|
| `p4-pass` | pass | pass | all claims and structured loaded skill match |
| `p4-partial` | partial | partial | one of two required claims is missing |
| `p4-fail` | fail | fail | required claim is absent |
| `p4-missing-oracle` | pass | not-scored | with-plugin oracle file is absent |
| `p4-malformed-oracle` | not-scored | pass | baseline oracle JSON is malformed |
| `p4-stale-report` | fail | fail | deterministic `stale-report` failure is injected |
| `p4-local-path-leak` | fail | fail | pre-redaction and persisted local-path markers are detected |
| `p4-sanitizer-only-leak` | fail | fail | pre-redaction local-path marker fails despite clean persisted text |
| `p4-private-field-leak` | fail | fail | pre-redaction and persisted private-field markers are detected |
| `p4-expected-outcomes-conflict` | not-scored | not-scored | conflicting `expected_outcomes` stops scoring |
| `p4-korean-negation-false-positive` | pass | pass | negated prose skill mention is ignored; structured field is used |
| `p4-prompt-only-command-claim` | fail | fail | command claim has no structured command/tool event |

Expected full-run status counts:

| status | count |
|---|---:|
| pass | 6 |
| partial | 2 |
| fail | 12 |
| not-scored | 4 |

The full mini-bucket run is expected to have run status `fail`. That is the
required P4 behavior because `partial`, `fail`, and `not-scored` are not success
states.
