Final independent review of the checker correction before mechanical commit. Original private report SHA256: `4ed62acf7b09c8e24398f124d63b0fb45f3f48fea0c0374b4601cbba72c3dee3`. Source links target the planned release containing these exact files.

**Spec PASS · Quality PASS · Technical ReadyToMerge: yes**, for this final checker correction. **Critical: 0 · Important: 0.**

1. **Cross-case original reuse remains addressed.** [check_design_evidence.py:364](https://github.com/changja88/dddjango/blob/dddjango-web--v1.1.5/dddjango-web/scripts/check_design_evidence.py#L364) gathers every original; line 390 applies `samefile` against that complete set. Independent equal-byte files remain accepted. The actual-file regressions cover cross-case direct reuse, hardlinks and copies at [test_design_evidence.py:371](https://github.com/changja88/dddjango/blob/dddjango-web--v1.1.5/dddjango-web/scripts/test/test_design_evidence.py#L371). Preservation verified statically; I did not rerun these filesystem tests.

2. **Nested document-base resolution remains correct.** [check_design_evidence.py:153](https://github.com/changja88/dddjango/blob/dddjango-web--v1.1.5/dddjango-web/scripts/check_design_evidence.py#L153) remembers only the nearest HTML. Reconstruction is invoked for document-relative script/component dependencies at line 183; file-relative module/CSS resolution retains the importing file. The collected fixture at [test_design_evidence.py:230](https://github.com/changja88/dddjango/blob/dddjango-web--v1.1.5/dddjango-web/scripts/test/test_design_evidence.py#L230) includes nested HTML, an asset available only beneath that nested document, and a source dependency back-edge.

3. **The remaining through-HTML ancestry failure is addressed.** [check_design_evidence.py:141](https://github.com/changja88/dddjango/blob/dddjango-web--v1.1.5/dddjango-web/scripts/check_design_evidence.py#L141) validates row values, detects repeated sources, follows importers beyond HTML, and returns only upon reaching the manifest entrypoint with an empty importer. Missing importers and premature termination raise `ValueError`. The traversal follows the collector’s first-discovery provenance at [freeze_design.py:84](https://github.com/changja88/dddjango/blob/dddjango-web--v1.1.5/dddjango-web/scripts/freeze_design.py#L84), so legitimate source dependency cycles remain accepted. Regressions cover 18 ancestry mutations at [test_design_evidence.py:270](https://github.com/changja88/dddjango/blob/dddjango-web--v1.1.5/dddjango-web/scripts/test/test_design_evidence.py#L270).

The prior exact reproduction now **exits 1 with `ValueError: cyclic document provenance`**, instead of returning HTML:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=dddjango-web/scripts python3 -c 'from check_design_evidence import _document_origin; h=dict(source="/s/index.html",source_document="/s/Inner.jsx",kind="html",status="ok"); c=dict(source="/s/Inner.jsx",source_document="/s/index.html",kind="component",status="ok"); print(_document_origin(c,{h["source"]:h,c["source"]:c},"index.html"))'
```

My additional `python3 -c` in-memory probe used the actual collector, scanner and closure code, replacing acquisition/writes/reads with dictionaries. It **exited 0**:

- Valid nearest-HTML resolution and cyclic source dependencies passed.
- **18/18** through-HTML ancestry mutations were rejected during actual reconstruction.
- **6/6** dependency-row deletions were rejected.
- Standalone component, script and CSS entrypoints passed, including file-relative imports/CSS assets.

The initial heredoc invocation was blocked by the shell before Python ran; the successful retry required no temporary files. These are **in-memory results**, not filesystem/CLI integration results.

These mirror comparisons and the whitespace check each **exited 0**:

```sh
cmp dddjango-web/scripts/check_design_evidence.py codex-dddjango-web/skills/dddjango-web/scripts/check_design_evidence.py
cmp dddjango-web/scripts/test/test_design_evidence.py codex-dddjango-web/skills/dddjango-web/scripts/test/test_design_evidence.py
cmp dddjango-web/scripts/freeze_design.py codex-dddjango-web/skills/dddjango-web/scripts/freeze_design.py
cmp dddjango-web/scripts/design_sources.py codex-dddjango-web/skills/dddjango-web/scripts/design_sources.py
cmp dddjango-web/scripts/asset_io.py codex-dddjango-web/skills/dddjango-web/scripts/asset_io.py
GIT_OPTIONAL_LOCKS=0 /Library/Developer/CommandLineTools/usr/bin/git diff --check
```

Scope remains exactly the four checker/test files. No source/index/HEAD mutations occurred; staged diff remains empty. No global validation of unused provenance is claimed. Existing scanner/JSON limits remain.

Owner-reported actual-file tests and the controller’s concurrent `make verify` are separate evidence, not my results. Accepted deployment limitations remain: **Claude r5 final-guidance FAIL, Codex r5 output-location FAIL, and incomplete latest native full-flow/media coverage**. No current full-flow success is claimed.

Serena/Graphify omitted as requested; no opt-in. No subagents, native apps, broad suites, installs or permission changes.