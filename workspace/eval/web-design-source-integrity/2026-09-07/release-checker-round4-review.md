Historical review of the first release-checker correction, based on uncommitted diff SHA256 `49d0ce84d3d10db27ea6c0d7386a01bb7843aa94beef7d7f00f84997efc2ea14`. Later corrections are recorded separately. Absolute local file links are rendered as source path references; no verdict is changed.

**Spec FAIL · Quality FAIL · Technical ReadyToMerge: no.** Critical: 0. Important: 1 remaining required-contract failure.

1. **Original finding 1 — addressed.** `dddjango-web/scripts/check_design_evidence.py:363` collects every original; line 389 compares each implementation capture against all originals using `samefile`. Independent equal-byte files remain allowed. Actual-file/CLI regressions cover direct reuse, hardlinks and independent copies at `dddjango-web/scripts/test/test_design_evidence.py:279`.

2. **Original finding 2 — not fully addressed.** Origin reconstruction fixes the reported nested-component resolution and preserves file-relative imports/CSS. However, `dddjango-web/scripts/check_design_evidence.py:152` returns immediately upon reaching HTML, accepting cyclic or missing HTML ancestry. The tests at `dddjango-web/scripts/test/test_design_evidence.py:205` exercise component cycles only.

**Remaining Important:** reject invalid/cyclic provenance through HTML as required. This exact read-only reproduction exits **0**, printing `/s/index.html` despite `Inner.jsx → index.html → Inner.jsx`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=dddjango-web/scripts python3 -c 'from check_design_evidence import _document_origin; h=dict(source="/s/index.html",source_document="/s/Inner.jsx",kind="html",status="ok"); c=dict(source="/s/Inner.jsx",source_document="/s/index.html",kind="component",status="ok"); print(_document_origin(c,{h["source"]:h,c["source"]:c},"index.html"))'
```

A separate `gate.run()` probe using existing fixture bytes and in-memory JSON also accepted HTML self-cycles, HTML↔script cycles and an unknown HTML importer. Its missing-dependency control correctly rejected the input. These were read-only probes, not filesystem/CLI integration tests.

Changed scope is exactly four files: `check_design_evidence.py` and `test/test_design_evidence.py` beneath both `dddjango-web/scripts/` and `codex-dddjango-web/skills/dddjango-web/scripts/`. No collector, dependency-helper, backend or runtime-prompt changes.

Validation:

- `cmp` on both changed mirror pairs and the corresponding `freeze_design.py`, `design_sources.py`, `asset_io.py` pairs: **all exit 0; byte-identical**.
- `GIT_OPTIONAL_LOCKS=0 /Library/Developer/CommandLineTools/usr/bin/git diff --check`: **exit 0**.
- `PYTHONDONTWRITEBYTECODE=1 python3 dddjango-web/scripts/test/test_design_evidence.py -v EvidenceTests.test_nested_component_document_assets_and_file_relative_imports_pass`: **exit 1 in setup**, because the sandbox provides no writable temporary directory. No assertion ran; the owner’s reported GREEN was not independently reproduced.
- HEAD remains `2e4acdb0e664084a9742efd0fd520d2f78beb1a9`; staged diff empty. Controller’s final full `make verify` remains separate.

Known, deployment-accepted limitations remain disclosed: **Claude r5 final-guidance failure, Codex r5 output-location failure, and incomplete latest full-native matrix**. No current full-flow success is claimed.

No source/index/HEAD changes, subagents, native evaluation or broad suites performed. Serena/Graphify omitted as requested; no opt-in.