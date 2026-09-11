# Final gate failure diagnosis — read-only stage

The three failed groups are stale derived expectations for approved changes. This diagnosis does not change source/tests/goldens or rerun suites. Existing verify logs and prior fixture stdout were read; HEAD/current RDF graphs and symbol-kinds payloads were compared in memory only. This report is the only written artifact.

## 1. Hierarchy target count: 31 retained-history revisions

Failure: `/tmp/djr-verify.IJVhDa/verify-ontology.log`, `[hierarchy] RED ExpressionShape: 기대 3617 → 실제 3648`. All 90 ontology authoring files and full SHACL passed before this count check.

Exact proposed literal: `workspace/eval/fixtures/ontology_gate/target-counts.json:4`, `"ExpressionShape": 3617` → `"ExpressionShape": 3648`. No other shape expectation changes are indicated by the failed run.

Independent in-memory RDF comparison loaded every `ontology/rules/*.ttl` from HEAD through `git show HEAD:<path>` and from current files through rdflib. Observed 3613 old Expression nodes, 3644 current nodes, exactly 31 additions and zero removals. All outgoing triples of every old Expression are still present. For each added node, assertions confirmed `prov:specializationOf` points to the same Work, `prov:wasRevisionOf` points to that Work's HEAD currentExpression, revision equals prior revision +1, and the Work's new currentExpression points to the added node. This independently proves retained revision history, not merely a count difference.

The verify command uses `--with-golden` (Makefile:116). The unchanged golden graphs add exactly four Expression nodes: `golden-expr-1`, `golden-expr-3`, `golden-expr-b1`, `golden-expr-p1`. Therefore full target totals are 3613+4=3617 and 3644+4=3648.

All added Expression identifiers end in `@2026-09-11`:

| Rules file | Revised Work IDs | Added |
|---|---|---|
| agent-design-architect.ttl | R-1617, R-3424, R-3425, R-3426, R-3427, R-3428, R-3429, R-3431 | 8 |
| agent-design-review-api.ttl | R-2677 | 1 |
| agent-discipline-reviewer.ttl | R-1037, R-1071, R-1104, R-1117, R-1118, R-1119 | 6 |
| command-dddjango.ttl | R-3432, R-3433, R-3434, R-3435, R-3436, R-3445 | 6 |
| discipline-houserules-final.ttl | R-3410, R-3468 | 2 |
| discipline-houserules-skill.ttl | R-3417, R-3447, R-3448, R-3451, R-3452, R-3457 | 6 |
| implementation-django-ninja-final.ttl | R-0084 | 1 |
| implementation-django-ninja-skill.ttl | R-2941 | 1 |

Do not remove old Expression nodes, weaken target-class closure, alter SHACL, or regenerate TTL to satisfy the count.

## 2. Baseline count: confirmed-to-candidate transitions

Failure: `/tmp/djr-verify.IJVhDa/verify-base-core.log`. Existing fixture matrix passed 104/104 before baseline matrix returned 71 matches / 2 mismatches / 0 pending over 73 lanes. Matrix implementation is `workspace/tools/checker_baseline_matrix.py`, not a file named count_golden.py. It counts `[#N]` as parsed and `[ⓓ#N]` as unparsed; candidate lines remain observed output.

Exact proposed literals:

```python
# workspace/tools/checker_baseline_matrix.py:262
"check-domain-model.py": (2, 50, 48, 15, False),
# workspace/tools/checker_baseline_matrix.py:263
"check-port-adapter-pairing.py": (2, 95, 92, 13, False),
```

Old values are `(2,51,49,14,False)` and `(2,96,93,12,False)`. Each transition removes one parsed raw / normalized unique violation and adds one unparsed candidate line; exit remains 2 and synthetic remains False. This is consistent with approved F4-14/F4-15 (brief.md rows and Task4 brief lines 30/36), which require uncertainty rather than false confirmation.

### Domain #546 exact event

Fixture: `workspace/eval/fixtures/domain_model/bad_rules/application/orders/application_layer/order/place_order/place_order_use_case.py`. `execute` starts at line 13; lines 17/18 write OrderRepository and LedgerRepository, and line 20 writes the order repository again. There is no with/atomic/decorator boundary in this fixture. The unchanged type-count basis finds exactly two aggregate kinds, `ledger` and `order`; current analysis leaves the transaction relationship unknown.

HEAD source at check-domain-model.py:813 emits this confirmed line unconditionally for two types:

```text
[#546] application/orders/application_layer/order/place_order/place_order_use_case.py:13: 서로 다른 애그리거트 리포지토리 ['ledger', 'order'] 에 쓰기 둘 — 한 트랜잭션은 애그리거트 «하나»를 바꾼다(D50 · 세는 대상은 타입이 <A>_repository.py 에서 온 것뿐)
```

Current source at check-domain-model.py:1053 emits the candidate below. Its exact stdout was already captured in `whole-fix-checker-fixtures.log:189`:

```text
[ⓓ#546] application/orders/application_layer/order/place_order/place_order_use_case.py:13: 서로 다른 애그리거트 쓰기 ['ledger', 'order'] 의 transaction 경계 불명 — 같은 트랜잭션인지 확인 필요 — 물음: 현재 함수의 lexical 구간 밖·불명 경계가 이 쓰기들을 묶는가
```

Stable raw-record identity remains checker=`check-domain-model.py`, rule=`#546`, file ending `place_order_use_case.py:13`, symbol=null. Severity changes violation→info and message becomes the full candidate text including ` — 물음: ...` (findings.py:280). This is source + existing stdout evidence, not a newly replayed complete multiset comparison.

### Pairing #557 exact event

Fixture: `workspace/eval/fixtures/port_adapter_pairing/bad_rules/application/orders/application_layer/order/place_order/place_order_use_case.py:12`: `if exc.status_code == 429:`. `exc` is explicitly annotated object at line 8. It has no proven vendor/contract origin. The fixture imports only BoardDomainBypassQuery and ReplyIn. An attribute spelling cannot establish vendor provenance.

HEAD source at check-port-adapter-pairing.py:1169 emits:

```text
[#557] application/orders/application_layer/order/place_order/place_order_use_case.py:12: 벤더 오류 코드를 위층이 판정한다 — 일시 실패의 정규화는 그 인프라를 «소유한» 어댑터가 한다
```

Current source at check-port-adapter-pairing.py:1216 emits this candidate, previously captured in `task-4-fix3-fixtures.log:14` and `task-4-fixtures.log:154`:

```text
[ⓓ#557] application/orders/application_layer/order/place_order/place_order_use_case.py:12: code/errno/status_code 수신자 출처 불명 — 벤더 코드인지 계약 값인지 확인 필요 — 물음: 이 값의 실제 선언과 정규화 소유자는 어디인가
```

Stable raw-record identity remains checker=`check-port-adapter-pairing.py`, rule=`#557`, file ending `place_order_use_case.py:12`, symbol=null. Severity changes violation→info, and message changes to the full candidate text. No event should be deleted from the total rule distribution. Confirmed vendor controls and independent raw comparisons were already covered by the Task4/fix smoke suite; this diagnosis does not rerun them.

## 3. pregate_symbol_kinds: source hashes only

Failure: `/tmp/djr-verify.IJVhDa/verify-base-regen.log`. Read generator implementation and called only its read-only `build_payload(root)` and `render(payload)` functions in memory. Compared resulting payload and bytes with the current canonical JSON. Schema is identical and all 56 kinds are exactly identical (base/checkers/rules/import_hint included). Only six entries of `source_sha` differ:

| source_sha key | Stored | Current rendered |
|---|---|---|
| check-context-isolation.py | 6ee97a89c6cc5a81 | bb68853338db1326 |
| check-domain-model.py | 810f941cffe36aa0 | ded715d2026c7556 |
| check-layer-skeleton.py | f2bdf8e26f9e4846 | 32810abb897f3dfc |
| check-port-adapter-pairing.py | 1900f109da8eea73 | 9fe24b4df8df90a6 |
| check-public-surface-annotation.py | 788c9b1513ebab27 | b94b4101403d5992 |
| check-usecase-dto-placement.py | e2fec2b3edb3f740 | 4a51b80b722d516c |

These are approved changed checker inputs (F4 provenance/admin/size-floor and earlier DTO corrections). Generator computes sha256(raw checker bytes)[:16] for all 27 checkers at gen_pregate_symbol_kinds.py:476; even a description-only change affects its checksum. No kind extraction change or new base rule is indicated.

After the current verify ends and coordinator authorizes the fix, use the normal generator, not a hand patch:

```sh
python3 -B workspace/tools/gen_pregate_symbol_kinds.py
```

It writes exactly `dddjango/scripts/pregate_symbol_kinds.json` and `codex-dddjango/skills/dddjango/scripts/pregate_symbol_kinds.json`. Expected byte diff is six source_sha substitutions per file; all other fields and 56 kinds should remain identical.

## 4. Likely downstream expectations and required bounded proof

Makefile:152 runs findings_count_matrix after checker_baseline_matrix; current attempt stops before it. Static inspection shows two additional stale rows in `workspace/tools/findings_count_matrix.py`:

- line 119 domain-model: `(exit, violation, info)` must change `(2,51,13)` → `(2,50,14)` if the bounded record replay confirms the single transition. Rule/sentinel distribution should remain identical because #546 still exists once. Raw violation-ID hash, canonical-locator violation-ID hash, and all-record fingerprint must change (fingerprint includes message, not severity).
- line 129 pairing: `(2,96,11)` → `(2,95,12)` under the corresponding #557 transition. Distribution likewise retains #557×1. All three hashes must be measured from exact raw records and compared with HEAD before updating.
- Context-isolation changed #153 candidate message (Task4): baseline counts can stay identical while its all-record fingerprint changes. Inspect its default red lane during bounded replay; do not assume the two count failures exhaust downstream hash differences.
- Other changed checker default lanes (public-surface, dto, skeleton) merit bounded record comparisons because semantic counts alone cannot exclude message/hash drift. Do not blanket-regenerate the entire EXPECTED map.

Exact new fingerprint literals have deliberately not been invented from count deltas. A full HEAD/current raw-record multiset comparison has not been executed during the active verify. Existing output proves the two precise source events above; a bounded isolated replay after the run ends is needed before claiming these are the only changed records or updating downstream hashes.

`manifest_seal.py` statically covers findings_count_matrix.py in the harness group (line 165) and canonical pregate_symbol_kinds.json in input material (line 106). The coordinator must re-seal after the final approved gate repair and then restart full verify, per docs/DEVELOPMENT.md. No hand edit to manifest hashes is appropriate. A search for the exact stale hierarchy/count/hash literals in current tool/fixture files found the named expectation locations; no additional hierarchy literal was found. This is bounded static inspection, not a claim that every unrun downstream suite is green.

## Boundary

No source/test/golden/TTL/primary/.git/master/F20 edits, suite/checker replay, or seal was performed in this diagnosis stage. In-memory RDF parsing used read-only git show, not checkout or Git mutation. Serena/Graphify were not used (no opt-in). Waiting for coordinator to finish the current verify and authorize the minimum gate repair with raw-record replay.
