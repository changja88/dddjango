# Naming Convention

## Canonical Filename Grammar

Use this format for new work item files:

```text
<YYYYMMDD-HHMMSS>-<phase>-<scope>-<topic>-<kind>.md
```

Example:

```text
20260522-201530-p2-skill-implementation-django-trigger-boundary-analysis.md
20260522-201530-p2-skill-implementation-django-trigger-boundary-plan.md
20260522-201530-p2-skill-implementation-django-trigger-boundary-evidence.md
20260522-201530-p2-skill-implementation-django-trigger-boundary-closure.md
```

The shared prefix is the work item id:

```text
<YYYYMMDD-HHMMSS>-<phase>-<scope>-<topic>
```

## Allowed Phase Values

- `p0`
- `p1`
- `p1-5`
- `p2`
- `p3`
- `p4`
- `p4-5`
- `p5`
- `p6`
- `p7`
- `p8`
- `p9`

## Allowed Scope Values

- `plugin`
- `skill`
- `reference`
- `eval`
- `runtime`
- `install`
- `review`
- `governance`
- `goal`
- `workflow`

Use a more specific topic for the target, for example
`implementation-django-trigger-boundary` or `mini-bucket-oracle-missing`.

## Allowed Kind Values

- `analysis`
- `plan`
- `evidence`
- `closure`
- `prompt`
- `review`
- `raw`
- `decision`
- `index`
- `fixture`
- `inventory`
- `protocol`

## Directory Placement

- Phase work goes under `phases/<phase-name>/`.
- Goal prompts go under `goals/<phase-name>/`.
- Durable raw review output goes under `reviews/raw/`.
- Review summaries go under `reviews/summaries/`.
- Governance rules go under `governance/`.
- Accepted decision records go under `decisions/`.
- Superseded files go under `archive/superseded/<phase>/` after indexing.

## Timestamp Rules

- Use Asia/Seoul local time.
- Use seconds precision: `YYYYMMDD-HHMMSS`.
- If two files are part of the same work item, reuse the exact same timestamp.
- If two independent work items start in the same second, append a short
  kebab-case disambiguator to the topic, not to the timestamp.

