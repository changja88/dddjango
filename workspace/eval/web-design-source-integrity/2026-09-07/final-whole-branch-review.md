This is the final whole-branch review of the stated revision before the two new checker corrections. Source findings are preserved; subsequent correction/validation is recorded separately. File links were converted to the reviewed GitHub revision and trailing whitespace was normalized; the original private report SHA256 is `f1d566b0a8339b30bcfad25adbece69b56228be84bfc674b2226d9fb524dfa5e`.

Reviewed all 34 tracked changes in `147a59a8… → 2e4acdb0…`, including canonical files, runtime differences, and release evidence.

**Strengths**

- Both runtimes explicitly connect original sources/renders, independent scope review, current caller/coder admission, and final visual audit.
- Existing 26 backstop checks remain intact; `--only` cannot disable the added design gate.
- All 32 compared byte-mirror pairs match. The seven published fixture files match their recorded hashes.

**Issues — Critical:** None found.

**Important — NEW findings**

1. **Cross-case original screenshots bypass the file-reuse check.**
   [check_design_evidence.py:363](https://github.com/changja88/dddjango/blob/2e4acdb0e664084a9742efd0fd520d2f78beb1a9/dddjango-web/scripts/check_design_evidence.py#L363) compares each implementation capture only with that case’s original. With two cases, assigning A’s capture to B’s original and B’s capture to A’s original passes `validate_visual` without any implementation capture. I reproduced this using existing image files and in-memory evidence.
   **Impact:** violates the explicit same-file/inode prohibition. Independent auditing remains required, but this deterministic check is incomplete.
   **Correction:** compare every implementation capture against **all** original capture identities, including hardlinks; continue allowing independent files with identical bytes.

2. **Closure rescanning rejects complete nested-component inputs.**
   [check_design_evidence.py:160](https://github.com/changja88/dddjango/blob/2e4acdb0e664084a9742efd0fd520d2f78beb1a9/dddjango-web/scripts/check_design_evidence.py#L160) treats `source_document` as the HTML origin, although [freeze_design.py:88](https://github.com/changja88/dddjango/blob/2e4acdb0e664084a9742efd0fd520d2f78beb1a9/dddjango-web/scripts/freeze_design.py#L88) stores the immediate importer there. For `index.html → components/Outer.jsx → components/Inner.jsx`, an inner `<img src="images/logo.png">` is correctly collected relative to the HTML document, then incorrectly checked relative to `components/`. The in-memory reproduction produced `source_ready=True` followed by “dependency absent from manifest.”
   **Impact:** supported, complete inputs remain blocked in both runtimes.
   **Correction:** preserve or reconstruct the actual document origin for document-relative dependencies while retaining file-relative module imports.

**Already disclosed and accepted**

- [Claude r5:33](https://github.com/changja88/dddjango/blob/2e4acdb0e664084a9742efd0fd520d2f78beb1a9/workspace/eval/web-design-source-integrity/2026-09-07/claude-native-r5.md#L33): N1 blocking **PASS**, final option B **Important FAIL**. Future `inputs0` remained required; no executed bypass occurred.
- [Codex r5:26](https://github.com/changja88/dddjango/blob/2e4acdb0e664084a9742efd0fd520d2f78beb1a9/workspace/eval/web-design-source-integrity/2026-09-07/codex-native-r5.md#L26): actual evidence-destination **FAIL**, within its own app. The misleading output-directory description limits plugin-only attribution; subsequent moves do not erase the violation.
- Latest full positive/media coverage remains **incomplete**. Claude N4 was cancelled for upstream failure. Older r2 ten-case pixel equality remains revision-specific. These are coverage gaps, not additional demonstrated code defects.

**Minor:** None raised. The current release README distinguishes authorization from technical success; I found no credential/private-response exposure in the reviewed publication evidence.

**Assessment — Ready to merge? With fixes.** The two new Important checker defects prevent my technical approval as-is. The previously accepted limitations alone would not reverse the user’s shipping decision; these new findings require separate disposition.

No source/index/HEAD changes, native runs, subagents, or make suites were performed. Controller verification remains separate. Serena/Graphify were omitted because opt-in markers are absent.
