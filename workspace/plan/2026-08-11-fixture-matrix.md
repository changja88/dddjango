# 전수 fixture 실측표 — 검사기 × 위반 fixture × exit

생성: 2026-08-12 · `workspace/tools/fixture_matrix.py` 실행 산출물(손으로 고치지 않는다 — 재실행으로 재생성).

「백스톱 실측 0」(5차 리뷰)의 종결 기록 — 검사기마다 자기 위반 fixture 에서 exit 2.
eval v4 FROZEN — 실측은 이 fixture 결정 레인만.

| 검사기 | fixture | 기대 | 실측 | 판정 |
|---|---|---|---|---|
| `check-layer-skeleton.py` | skeleton/good_bc | 0 | 0 | ✓ |
| `check-layer-skeleton.py` | skeleton/bad_legacy_flat | 2 | 2 | ✓ |
| `check-layer-skeleton.py` | skeleton/bad_missing | 2 | 2 | ✓ |
| `check-context-isolation.py` | context_isolation/good | 0 | 0 | ✓ |
| `check-context-isolation.py` | context_isolation/bad_rules | 2 | 2 | ✓ |
| `check-usecase-dto-placement.py` | usecase_dto/good | 0 | 0 | ✓ |
| `check-usecase-dto-placement.py` | usecase_dto/bad_rules | 2 | 2 | ✓ |
| `check-mechanism-ownership.py` | mechanism_ownership/good | 0 | 0 | ✓ |
| `check-mechanism-ownership.py` | mechanism_ownership/bad_rules | 2 | 2 | ✓ |
| `check-synthetic-infra-exc.py` | synthetic_infra_exc/good | 0 | 0 | ✓ |
| `check-synthetic-infra-exc.py` | synthetic_infra_exc/bad_rules | 2 | 2 | ✓ |
| `check-ninja-boundary-middleware.py` | ninja_boundary_middleware/good | 0 | 0 | ✓ |
| `check-ninja-boundary-middleware.py` | ninja_boundary_middleware/bad_rules | 2 | 2 | ✓ |
| `check-transient-overmapping.py` | transient_overmapping/good | 0 | 0 | ✓ |
| `check-transient-overmapping.py` | transient_overmapping/bad_rules | 2 | 2 | ✓ |
| `check-idempotency-scope-creep.py` | idempotency_scope_creep/good | 0 | 0 | ✓ |
| `check-idempotency-scope-creep.py` | idempotency_scope_creep/bad_rules | 2 | 2 | ✓ |
| `check-common-container.py` | common_container/good | 0 | 0 | ✓ |
| `check-common-container.py` | common_container/bad_rules | 2 | 2 | ✓ |
| `check-app-container.py` | app_container/good | 0 | 0 | ✓ |
| `check-app-container.py` | app_container/bad_rules | 2 | 2 | ✓ |
| `check-public-surface-annotation.py` | public_surface/good | 0 | 0 | ✓ |
| `check-public-surface-annotation.py` | public_surface/bad_rules | 2 | 2 | ✓ |
| `check-choices-literal-consumption.py` | choices_literal/good | 0 | 0 | ✓ |
| `check-choices-literal-consumption.py` | choices_literal/bad_rules | 2 | 2 | ✓ |
| `check-test-config.py` | test_config/good | 0 | 0 | ✓ |
| `check-test-config.py` | test_config/bad_rules | 2 | 2 | ✓ |
| `check-response-schema-bypass.py` | response_schema_bypass/good | 0 | 0 | ✓ |
| `check-response-schema-bypass.py` | response_schema_bypass/bad_rules | 2 | 2 | ✓ |
| `check-composition-root.py` | composition_root/good | 0 | 0 | ✓ |
| `check-composition-root.py` | composition_root/bad_rules | 2 | 2 | ✓ |
| `check-db-table.py` | db_table/good | 0 | 0 | ✓ |
| `check-db-table.py` | db_table/bad_rules | 2 | 2 | ✓ |
| `check-transaction-boundary.py` | transaction_boundary/good | 0 | 0 | ✓ |
| `check-transaction-boundary.py` | transaction_boundary/bad_rules | 2 | 2 | ✓ |
| `check-event-publish.py` | event_publish/good | 0 | 0 | ✓ |
| `check-event-publish.py` | event_publish/bad_rules | 2 | 2 | ✓ |
| `check-broker-contract.py` | broker_contract/good | 0 | 0 | ✓ |
| `check-broker-contract.py` | broker_contract/bad_rules | 2 | 2 | ✓ |
| `check-missable-entrance.py` | missable_entrance/good | 0 | 0 | ✓ |
| `check-missable-entrance.py` | missable_entrance/bad_rules | 2 | 2 | ✓ |
| `check-naming.py` | naming/good | 0 | 0 | ✓ |
| `check-naming.py` | naming/bad_rules | 2 | 2 | ✓ |
| `check-domain-model.py` | domain_model/good | 0 | 0 | ✓ |
| `check-domain-model.py` | domain_model/bad_rules | 2 | 2 | ✓ |
| `check-business-vocabulary.py` | business_vocabulary/good | 0 | 0 | ✓ |
| `check-business-vocabulary.py` | business_vocabulary/bad_rules | 2 | 2 | ✓ |
| `check-port-adapter-pairing.py` | port_adapter_pairing/good | 0 | 0 | ✓ |
| `check-port-adapter-pairing.py` | port_adapter_pairing/bad_rules | 2 | 2 | ✓ |
| `check-error-centralization.py` | error_centralization/good (auto) | 0 | 0 | ✓ |
| `check-error-centralization.py` | error_centralization/bad_rules (auto) | 2 | 2 | ✓ |
| `check-api-error-controller-contract.py` | api_error_controller/good (auto) | 0 | 0 | ✓ |
| `check-api-error-controller-contract.py` | api_error_controller/bad_rules (auto) | 2 | 2 | ✓ |
| `check-openapi-error-declaration.py` | openapi_error_declaration/good (auto) | 0 | 0 | ✓ |
| `check-openapi-error-declaration.py` | openapi_error_declaration/bad_rules (auto) | 2 | 2 | ✓ |
| `checker_lint.py` | checker_lint/good | 0 | 0 | ✓ |
| `checker_lint.py` | checker_lint/bad_rules | 2 | 2 | ✓ |

케이스 57 · 일치 57 · 불일치 0
