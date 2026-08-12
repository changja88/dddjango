# 전수 fixture 실측표 — 검사기 × 위반 fixture × exit

생성: 2026-08-12 · `workspace/tools/fixture_matrix.py` 실행 산출물(손으로 고치지 않는다 — 재실행으로 재생성).

「백스톱 실측 0」(5차 리뷰)의 종결 기록 — 검사기마다 자기 위반 fixture 에서 exit 2.
eval v5 FROZEN — 실측은 이 fixture 결정 레인만.

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
| `check-test-config.py` | test_config_entrance/good | 0 | 0 | ✓ |
| `check-test-config.py` | test_config_entrance/bad_rules | 2 | 2 | ✓ |
| `check-event-publish.py` | event_publish_leaf/good | 0 | 0 | ✓ |
| `check-event-publish.py` | event_publish_leaf/bad_rules | 2 | 2 | ✓ |
| `check-db-table.py` | db_table_choices/good | 0 | 0 | ✓ |
| `check-db-table.py` | db_table_choices/bad_rules | 2 | 2 | ✓ |
| `checker_lint.py` | checker_lint/good | 0 | 0 | ✓ |
| `checker_lint.py` | checker_lint/bad_rules | 2 | 2 | ✓ |
| `check-layer-skeleton.py` | invocation/check-layer-skeleton.py | 1 | 1 | ✓ |
| `check-context-isolation.py` | invocation/check-context-isolation.py | 1 | 1 | ✓ |
| `check-usecase-dto-placement.py` | invocation/check-usecase-dto-placement.py | 1 | 1 | ✓ |
| `check-mechanism-ownership.py` | invocation/check-mechanism-ownership.py | 1 | 1 | ✓ |
| `check-synthetic-infra-exc.py` | invocation/check-synthetic-infra-exc.py | 1 | 1 | ✓ |
| `check-ninja-boundary-middleware.py` | invocation/check-ninja-boundary-middleware.py | 1 | 1 | ✓ |
| `check-transient-overmapping.py` | invocation/check-transient-overmapping.py | 1 | 1 | ✓ |
| `check-idempotency-scope-creep.py` | invocation/check-idempotency-scope-creep.py | 1 | 1 | ✓ |
| `check-common-container.py` | invocation/check-common-container.py | 1 | 1 | ✓ |
| `check-app-container.py` | invocation/check-app-container.py | 1 | 1 | ✓ |
| `check-public-surface-annotation.py` | invocation/check-public-surface-annotation.py | 1 | 1 | ✓ |
| `check-choices-literal-consumption.py` | invocation/check-choices-literal-consumption.py | 1 | 1 | ✓ |
| `check-test-config.py` | invocation/check-test-config.py | 1 | 1 | ✓ |
| `check-response-schema-bypass.py` | invocation/check-response-schema-bypass.py | 1 | 1 | ✓ |
| `check-composition-root.py` | invocation/check-composition-root.py | 1 | 1 | ✓ |
| `check-db-table.py` | invocation/check-db-table.py | 1 | 1 | ✓ |
| `check-transaction-boundary.py` | invocation/check-transaction-boundary.py | 1 | 1 | ✓ |
| `check-event-publish.py` | invocation/check-event-publish.py | 1 | 1 | ✓ |
| `check-broker-contract.py` | invocation/check-broker-contract.py | 1 | 1 | ✓ |
| `check-missable-entrance.py` | invocation/check-missable-entrance.py | 1 | 1 | ✓ |
| `check-naming.py` | invocation/check-naming.py | 1 | 1 | ✓ |
| `check-domain-model.py` | invocation/check-domain-model.py | 1 | 1 | ✓ |
| `check-business-vocabulary.py` | invocation/check-business-vocabulary.py | 1 | 1 | ✓ |
| `check-port-adapter-pairing.py` | invocation/check-port-adapter-pairing.py | 1 | 1 | ✓ |
| `check-error-centralization.py` | invocation/check-error-centralization.py (auto) | 1 | 1 | ✓ |
| `check-api-error-controller-contract.py` | invocation/check-api-error-controller-contract.py (auto) | 1 | 1 | ✓ |
| `check-openapi-error-declaration.py` | invocation/check-openapi-error-declaration.py (auto) | 1 | 1 | ✓ |

케이스 90 · 일치 90 · 불일치 0
