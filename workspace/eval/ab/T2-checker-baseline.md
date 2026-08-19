# T2 검사기 출력 기준선 — 27종 × 자기 red fixture

생성: 2026-08-19 · `workspace/tools/checker_baseline_matrix.py --emit` 산출물(손으로 고치지 않는다 — 재실행으로 재생성).

T2-1 개작(공용 findings 모듈 편입)의 anchor diff 기대 기준선 — 계수 정의·갱신 규율은 도구 docstring.

| 검사기 | exit | parsed | unparsed | synthetic | 판정 |
|---|---|---|---|---|---|
| `check-mechanism-ownership.py` | 2 | 6 | 1 | — | ✓ |
| `check-error-centralization.py` | 2 | 5 | 1 | — | ✓ |
| `check-response-schema-bypass.py` | 2 | 0 | 3 | 1건 | ✓ |
| `check-layer-skeleton.py` | 2 | 10 | 1 | — | ✓ |
| `check-openapi-error-declaration.py` | 2 | 3 | 1 | — | ✓ |
| `check-context-isolation.py` | 2 | 58 | 6 | — | ✓ |
| `check-app-container.py` | 2 | 0 | 4 | 1건 | ✓ |
| `check-ninja-boundary-middleware.py` | 2 | 0 | 4 | 1건 | ✓ |
| `check-common-container.py` | 2 | 0 | 4 | 1건 | ✓ |
| `check-idempotency-scope-creep.py` | 2 | 0 | 3 | 1건 | ✓ |
| `check-public-surface-annotation.py` | 2 | 10 | 4 | — | ✓ |
| `check-test-config.py` | 2 | 13 | 2 | — | ✓ |
| `check-transient-overmapping.py` | 2 | 0 | 3 | 1건 | ✓ |
| `check-synthetic-infra-exc.py` | 2 | 1 | 2 | — | ✓ |
| `check-api-error-controller-contract.py` | 2 | 9 | 3 | — | ✓ |
| `check-composition-root.py` | 2 | 18 | 4 | — | ✓ |
| `check-db-table.py` | 2 | 26 | 2 | — | ✓ |
| `check-choices-literal-consumption.py` | 2 | 0 | 6 | 1건 | ✓ |
| `check-usecase-dto-placement.py` | 2 | 35 | 7 | — | ✓ |
| `check-transaction-boundary.py` | 2 | 13 | 3 | — | ✓ |
| `check-domain-model.py` | 2 | 48 | 14 | — | ✓ |
| `check-port-adapter-pairing.py` | 2 | 79 | 10 | — | ✓ |
| `check-event-publish.py` | 2 | 20 | 5 | — | ✓ |
| `check-broker-contract.py` | 2 | 22 | 6 | — | ✓ |
| `check-missable-entrance.py` | 2 | 17 | 5 | — | ✓ |
| `check-naming.py` | 2 | 29 | 6 | — | ✓ |
| `check-business-vocabulary.py` | 2 | 48 | 7 | — | ✓ |

검사기 27 · 일치 27 · 불일치 0
