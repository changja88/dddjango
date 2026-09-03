# kkebi — root=/Users/hyun/Desktop/kkebi-server
- .py files scanned: 3952 (parse failures: 0) — skip dirs: ['.claude', '.codex', '.dddjango', '.dddjango-web', '.git', '.idea', '.mypy_cache', '.playwright-mcp', '.pytest_cache', '.ruff_cache', '.serena', '.superpowers', '.venv', '.worktrees', '__pycache__', 'migrations', 'node_modules', 'site-packages', 'venv']
- files using bare `Any` name without a typing import (heuristic counted anyway): 0

## D — always-raise functions by return-annotation kind
- total always-raise functions: 161 → NoReturn=2, None=40, missing=1, other=118
- `-> None` always-raise: 40 = core(helper-like, non-NotImplementedError) 23 + stub(NotImplementedError/abstract) 17

### D `-> None` core — per group (files | prod | test)
| group | files | core -> None | of which test | NotImpl/abstract -> None | -> NoReturn always-raise | -> missing always-raise |
|---|---|---|---|---|---|---|
| application/billing | 621 | 2 | 1 | 2 | 1 | 0 |
| application/product_observability | 212 | 1 | 1 | 0 | 0 | 0 |
| application/review | 194 | 2 | 2 | 0 | 0 | 0 |
| application/saju | 586 | 1 | 0 | 12 | 0 | 0 |
| application/share | 129 | 8 | 8 | 0 | 0 | 0 |
| application/tarot | 345 | 2 | 2 | 1 | 0 | 1 |
| application/top3 | 78 | 0 | 0 | 1 | 0 | 0 |
| framework/broker | 7 | 0 | 0 | 1 | 0 | 0 |
| scripts/import_legacy_tarot | 22 | 2 | 2 | 0 | 0 | 0 |
| scripts/import_legacy_top3 | 16 | 1 | 1 | 0 | 0 | 0 |
| scripts/import_product_observability | 11 | 0 | 0 | 0 | 1 | 0 |
| tests | 14 | 4 | 4 | 0 | 0 | 0 |

### D core list (`file:line func` — raised — test?)
- application/billing/driven_layer/adapter/external_system/toss/payment_processing_adapter.py:437 _raise_provider_error — raise PaymentContractViolation, PaymentOutcomeUnknown, PaymentRejected
- application/billing/test/integration/test_payment_confirmed_after_commit_dispatch.py:181 fail_listener — raise RuntimeError [test]
- application/product_observability/test/integration/test_manual_bug_report_persistence.py:42 append — raise BugReportAuditUnavailable [test]
- application/review/test/integration/test_process_account_deletions_use_case.py:190 remove_by_owner — raise RuntimeError [test]
- application/review/test/integration/test_process_account_merges_use_case.py:158 repoint_owner — raise RuntimeError [test]
- application/saju/domain_layer/saju_chart/saju_chart.py:76 __init__ — raise InvalidSajuChart
- application/share/test/unit/test_anticorruption_adapters.py:45 raise_published — raise CallerIdentityPublishedError [test]
- application/share/test/unit/test_anticorruption_adapters.py:54 raise_raw — raise raw_error [test]
- application/share/test/unit/test_anticorruption_adapters.py:84 raise_published — raise ProfileLookupPublishedError [test]
- application/share/test/unit/test_anticorruption_adapters.py:93 raise_raw — raise raw_error [test]
- application/share/test/unit/test_anticorruption_adapters.py:136 raise_published — raise SharedReadingSupplyPublishedError [test]
- application/share/test/unit/test_anticorruption_adapters.py:145 raise_raw — raise raw_error [test]
- application/share/test/unit/test_anticorruption_adapters.py:177 raise_published — raise SharedReadingSupplyPublishedError [test]
- application/share/test/unit/test_anticorruption_adapters.py:186 raise_raw — raise raw_error [test]
- application/tarot/test/integration/test_tarot_generation_transaction.py:244 fail_stage — raise error [test]
- application/tarot/test/integration/test_tarot_generation_transaction.py:283 fail_stage — raise error [test]
- scripts/import_legacy_tarot/test/test_tarot_import_rerun.py:1020 steal_before_complete — raise AssertionError [test]
- scripts/import_legacy_tarot/test/test_tarot_import_rerun.py:1164 reject_deck_replay — raise AssertionError [test]
- scripts/import_legacy_top3/test/test_legacy_top3_import.py:305 fail_after_first_write — raise RuntimeError [test]
- tests/test_web_profile_edit_contract.py:709 post — raise RuntimeError [test]
- tests/test_web_profile_edit_view.py:759 recalculate — raise SajuSelfChartClientError [test]
- tests/test_web_profile_edit_view_model.py:655 recalculate — raise SajuSelfChartClientError [test]
- tests/test_web_saju_detail_review_preview.py:29 _raise — raise ReviewClientError [test]

### D stub list (NotImplementedError/abstract with -> None)
- application/billing/application_layer/port/payment_refund_restricted_evidence/payment_refund_restricted_evidence_port.py:10 stage [abstract]
- application/billing/application_layer/port/payment_settlement_restricted_evidence/payment_settlement_restricted_evidence_port.py:16 stage [abstract]
- application/saju/domain_layer/relationship_profile/relationship_profile_repository.py:11 save [abstract]
- application/saju/domain_layer/relationship_profile/relationship_profile_repository.py:19 remove [abstract]
- application/saju/domain_layer/relationship_profile/relationship_profile_repository.py:31 repoint_owner [abstract]
- application/saju/domain_layer/saju_billing_feed_cursor/saju_billing_feed_cursor_repository.py:15 save [abstract]
- application/saju/domain_layer/saju_chart/saju_chart_repository.py:21 save [abstract]
- application/saju/domain_layer/saju_merge_repoint_cursor/saju_merge_repoint_cursor_repository.py:15 save [abstract]
- application/saju/domain_layer/saju_product/saju_product_repository.py:9 save [abstract]
- application/saju/domain_layer/saju_reading/saju_reading_repository.py:10 save [abstract]
- application/saju/domain_layer/saju_reading/saju_reading_repository.py:35 repoint_owner [abstract]
- application/saju/domain_layer/saju_report_prompt/saju_report_prompt_repository.py:12 save [abstract]
- application/saju/domain_layer/self_saju_profile/self_saju_profile_repository.py:11 save [abstract]
- application/saju/domain_layer/self_saju_profile/self_saju_profile_repository.py:20 repoint_owner [abstract]
- application/tarot/application_layer/port/unit_of_work/tarot_reading_unit_of_work.py:22 after_commit [abstract]
- application/top3/test/unit/test_post_visibility_use_cases.py:54 save_all [test]
- framework/broker/external/external_broker.py:13 publish

### D always-raise with `-> NoReturn` (correctly typed)
- application/billing/driven_layer/adapter/external_system/toss/payment_processing_adapter.py:366 _raise_transport_failure — raise PaymentOutcomeUnknown, PaymentTemporarilyUnavailable
- scripts/import_product_observability/cli.py:21 error — raise ImportConfigurationError

### D always-raise with missing return annotation
- application/tarot/test/integration/test_tarot_generation_cas.py:99 execute — raise AssertionError [test]

## NoReturn / Never usage (import + annotation)
| group | imports | annotations |
|---|---|---|
| application/billing | 1 | 1 |
| scripts | 1 | 1 |
| scripts/import_product_observability | 1 | 1 |
- total: imports=3 annotations=3
  - application/billing/driven_layer/adapter/external_system/toss/payment_processing_adapter.py:366 _raise_transport_failure -> Never
  - scripts/import_legacy_billing.py:19 error -> NoReturn
  - scripts/import_product_observability/cli.py:21 error -> Never

## E — explicit `Any` occurrences
- total: 1188 · bare=700 · bare_optional=5 · nested=483
- by site: sig-arg=403, sig-ret=144, sig-star=81, var-attr=2, var-class=33, var-local=522, var-module=3
- by site×kind: sig-arg/bare=248, sig-arg/bare_optional=2, sig-arg/nested=153, sig-ret/bare=59, sig-ret/nested=85, sig-star/bare=81, var-attr/bare_optional=1, var-attr/nested=1, var-class/bare=20, var-class/nested=13, var-local/bare=292, var-local/bare_optional=2, var-local/nested=228, var-module/nested=3

### E per group (sig = signature arg/star/ret · var = AnnAssign module/class/local/attr)
| group | files | sig bare(+opt) | sig nested | var bare(+opt) | var nested | total | of which in test files |
|---|---|---|---|---|---|---|---|
| (root) | 2 | 37(+0) | 1 | 7(+0) | 0 | 45 | 0 |
| application/billing | 621 | 58(+0) | 29 | 16(+0) | 36 | 139 | 138 |
| application/daily | 262 | 13(+0) | 18 | 9(+0) | 41 | 81 | 79 |
| application/identity | 397 | 7(+2) | 15 | 17(+0) | 15 | 56 | 54 |
| application/image | 144 | 0(+0) | 7 | 0(+0) | 6 | 13 | 11 |
| application/notification | 237 | 2(+0) | 11 | 0(+0) | 0 | 13 | 13 |
| application/product_observability | 212 | 10(+0) | 7 | 13(+0) | 1 | 31 | 17 |
| application/review | 194 | 39(+0) | 2 | 1(+0) | 1 | 43 | 41 |
| application/saju | 586 | 79(+0) | 32 | 47(+0) | 36 | 194 | 111 |
| application/share | 129 | 7(+0) | 3 | 27(+0) | 12 | 49 | 45 |
| application/tarot | 345 | 1(+0) | 1 | 23(+0) | 4 | 29 | 10 |
| application/top3 | 78 | 2(+0) | 2 | 13(+0) | 10 | 27 | 23 |
| scripts/import_legacy_daily | 58 | 23(+0) | 17 | 48(+3) | 37 | 128 | 43 |
| scripts/import_legacy_share | 18 | 0(+0) | 0 | 12(+0) | 0 | 12 | 12 |
| scripts/import_legacy_tarot | 22 | 2(+0) | 0 | 16(+0) | 2 | 20 | 17 |
| scripts/import_product_observability | 11 | 1(+0) | 1 | 0(+0) | 3 | 5 | 0 |
| scripts/seed_canonical_tarot_deck | 7 | 0(+0) | 1 | 0(+0) | 1 | 2 | 0 |
| tests | 14 | 54(+0) | 14 | 0(+0) | 15 | 83 | 83 |
| web/client | 50 | 49(+0) | 72 | 63(+0) | 22 | 206 | 0 |
| web/mypage | 53 | 2(+0) | 3 | 0(+0) | 2 | 7 | 0 |
| web/saju | 32 | 2(+0) | 2 | 0(+0) | 1 | 5 | 0 |

### E per top-level (application vs rest)
| top | files | sig bare(+opt) | sig nested | var bare(+opt) | var nested | total | in test files |
|---|---|---|---|---|---|---|---|
| (root) | 2 | 37(+0) | 1 | 7(+0) | 0 | 45 | 0 |
| application | 3463 | 218(+2) | 127 | 166(+0) | 162 | 675 | 542 |
| scripts | 195 | 26(+0) | 19 | 76(+3) | 43 | 167 | 72 |
| tests | 14 | 54(+0) | 14 | 0(+0) | 15 | 83 | 83 |
| web | 239 | 53(+0) | 77 | 63(+0) | 25 | 218 | 0 |

### E top 10 files
-  78  scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py  (bare 34 / nested 44)
-  45  application/saju/domain_layer/domain_service/v3_reading_assembler.py  (bare 23 / nested 22)
-  45  fabfile.py  (bare 44 / nested 1)
-  41  application/billing/test/e2e/test_billing_payment_api.py  (bare 23 / nested 18)
-  33  application/saju/test/e2e/test_saju_reading_api.py  (bare 33 / nested 0)
-  31  scripts/import_legacy_daily/test/integration/test_legacy_daily_migration_run_contract.py  (bare 26 / nested 5)
-  31  tests/test_web_profile_edit_view_model.py  (bare 17 / nested 14)
-  29  tests/test_web_profile_edit_view.py  (bare 22 / nested 7)
-  28  application/daily/test/unit/test_daily_narrative_adapters.py  (bare 7 / nested 21)
-  27  application/share/test/e2e/test_share_api.py  (bare 14 / nested 13)

### E top 10 files — production only (non-test)
-  78  scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py  (bare 34 / nested 44)
-  45  application/saju/domain_layer/domain_service/v3_reading_assembler.py  (bare 23 / nested 22)
-  45  fabfile.py  (bare 44 / nested 1)
-  25  web/client/top3/response/post_response.py  (bare 13 / nested 12)
-  20  web/client/review/response/content_review_list_response.py  (bare 10 / nested 10)
-  18  web/client/billing/response/coupon_response.py  (bare 9 / nested 9)
-  18  web/client/billing/response/point_ledger_response.py  (bare 9 / nested 9)
-  16  web/client/identity/response/profile_response.py  (bare 7 / nested 9)
-  15  web/client/saju/response/saju_catalog_list_response.py  (bare 8 / nested 7)
-  15  web/client/tarot/response/tarot_deck_response.py  (bare 8 / nested 7)

### E nested shapes — top 12 (with up to 3 examples each: file:line site name @func/cls)
- 214  `dict[str, Any]`
    - application/image/driven_layer/django_image/admin/image/form/image_form.py:31 sig-ret  @ImageForm.clean
    - application/product_observability/driving_layer/api/analytics/analytics_controller.py:200 sig-arg request_schema @-._openapi
    - application/product_observability/driving_layer/api/bug_report/bug_report_controller.py:178 sig-arg request_schema @-._openapi
-  93  `Mapping[str, Any]`
    - web/client/billing/response/coupon_claim_response.py:9 sig-ret  @-._as_mapping
    - web/client/billing/response/coupon_claim_response.py:15 sig-arg payload @-._require
    - web/client/billing/response/coupon_claim_response.py:21 sig-arg payload @-._require_str
-  27  `list[dict[str, Any]]`
    - application/saju/application_layer/port/domain_bypass_query/catalog_read/saju_catalog_detail_out.py:24 var-class questions @SajuCatalogDetailOut.-
    - application/saju/domain_layer/domain_service/v2_reading_assembler.py:140 var-local existing_sections @V2ReadingAssembler.build_section_request
    - application/saju/domain_layer/domain_service/v2_reading_assembler.py:184 var-local existing_sections @V2ReadingAssembler.finalize_section
-  26  `tuple[Any, ...]`
    - application/saju/application_layer/port/domain_bypass_query/reading_read/reading_detail_out.py:24 var-class questions @ReadingDetailOut.-
    - application/saju/driven_layer/adapter/persistence/domain_bypass_query/reading_read_query.py:69 var-local exposed_questions @DjangoReadingReadDomainBypassQuery.get_owned_detail
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:166 sig-arg values @-._canonical_source_hash
-  25  `Callable[..., Any]`
    - application/billing/test/e2e/conftest.py:13 sig-ret  @-.make_coupon_campaign
    - application/billing/test/e2e/conftest.py:25 sig-ret  @-.make_coupon_entitlement
    - application/billing/test/e2e/conftest.py:37 sig-ret  @-.make_point_account
-  17  `list[tuple[Any, ...]]`
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:632 var-local column_rows @LegacyDailyDatabaseDailySourceAdapter.get_source_inventory
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:650 var-local catalog_rows @LegacyDailyDatabaseDailySourceAdapter.get_source_inventory
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:753 var-local rows @LegacyDailyDatabaseDailySourceAdapter.measure_fortunes_after
-  13  `dict[str, Any] | None`
    - application/image/driven_layer/django_image/admin/image/panel.py:67 sig-arg extra_context @ImageAdmin.changeform_view
    - application/saju/domain_layer/domain_service/v3_reading_assembler.py:405 var-local llm_graphics @-._parse_chapter_response
    - application/saju/domain_layer/domain_service/v3_reading_assembler.py:417 sig-arg llm_graphics @-._merge_graphics
-   7  `dict[str, dict[str, Any]]`
    - application/daily/test/unit/test_daily_engine_provenance.py:34 var-local by_name @-._fortune_pillars
    - application/daily/test/unit/test_daily_engine_provenance.py:165 var-local artifacts @-.test_manifest_is_the_canonical_raw_hash_owner_for_both_oracles
    - application/daily/test/unit/test_daily_engine_provenance.py:205 var-local manual @-.test_manual_fortune_oracle_locks_r1_r2_r4_and_gender_bug_compatibility
-   7  `list[Any]`
    - application/saju/domain_layer/domain_service/v3_reading_assembler.py:278 var-local value_list @-._evaluate_condition
    - application/saju/domain_layer/domain_service/v3_reading_assembler.py:742 sig-arg sinsal_list @-._apply_sinsal_variables
    - application/saju/driven_layer/adapter/persistence/domain_bypass_query/reading_read_query.py:60 var-local product_questions @DjangoReadingReadDomainBypassQuery.get_owned_detail
-   6  `type[Any]`
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:425 sig-arg expected_type @-._validate_measurements
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:539 sig-arg expected_type @-._validate_measurement_collection
    - scripts/import_product_observability/apply.py:195 sig-ret  @-._model_class
-   5  `Callable[[], dict[str, Any]]`
    - application/notification/test/e2e/conftest.py:28 sig-ret  @-.issue_caller
    - application/notification/test/e2e/conftest.py:49 sig-arg issue_caller @-.caller
    - application/notification/test/e2e/test_notification_settings_api.py:93 sig-arg issue_caller @-.test_patch_by_one_caller_does_not_affect_another_caller
-   5  `tuple[Any, ...] | None`
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:640 var-local fortune_count_row @LegacyDailyDatabaseDailySourceAdapter.get_source_inventory
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:641 var-local compatibility_count_row @LegacyDailyDatabaseDailySourceAdapter.get_source_inventory
    - scripts/import_legacy_daily/adapter/legacy_daily_database/daily_source_adapter.py:644 var-local reltuples_row @LegacyDailyDatabaseDailySourceAdapter.get_source_inventory

### E nested — outermost container tally
dict=241, Mapping=93, list=54, tuple=53, Callable=33, type=6, ClassVar=3

### E nested — enclosing function-name tally (top 15, production only)
from_json=18, <module/class>=13, _as_mapping=13, clean=11, _require=11, _require_str=10, _require_int=7, get_source_inventory=5, _require_bool=5, _require_optional_str=5, _parse_chapter_response=4, _merge_graphics=4, fetch_fortunes=4, finalize_section=3, finalize_content=3

### E bare(+optional) — production list, by site (top 40)
- application/daily/driven_layer/adapter/external_system/openai/compatibility_narrative_generation_adapter.py:101 var-local completion `Any` @OpenaiCompatibilityNarrativeGenerationAdapter.generate
- application/daily/driven_layer/adapter/external_system/openai/fortune_narrative_generation_adapter.py:64 var-local completion `Any` @OpenaiFortuneNarrativeGenerationAdapter.generate
- application/identity/driven_layer/django_identity/admin/account_merge/panel.py:48 sig-arg obj `Any | None` @AccountMergeAdmin.has_change_permission
- application/identity/driven_layer/django_identity/admin/profile/panel.py:39 sig-arg obj `Any | None` @ProfileAdmin.has_change_permission
- application/product_observability/driving_layer/api/analytics/analytics_controller.py:130 sig-arg decision `Any` @-._accepted_rate_limit_or_none
- application/product_observability/driving_layer/api/analytics/analytics_controller.py:327 var-local decision `Any` @AnalyticsController.record_client_event
- application/product_observability/driving_layer/api/analytics/analytics_controller.py:354 var-local use_case `Any` @AnalyticsController.record_client_event
- application/product_observability/driving_layer/api/analytics/analytics_controller.py:423 var-local decision `Any` @AnalyticsController.record_page_session
- application/product_observability/driving_layer/api/analytics/analytics_controller.py:457 var-local use_case `Any` @AnalyticsController.record_page_session
- application/product_observability/driving_layer/api/analytics/schema/schema_in.py:25 var-class event_name `Any` @PageVisitSessionIn.-
- application/product_observability/driving_layer/api/analytics/schema/schema_in.py:29 var-class referrer `Any` @PageVisitSessionIn.-
- application/product_observability/driving_layer/api/bug_report/bug_report_controller.py:141 sig-arg decision `Any` @-._accepted_rate_limit_or_none
- application/product_observability/driving_layer/api/bug_report/bug_report_controller.py:267 var-local decision `Any` @BugReportController.create_bug_report
- application/product_observability/driving_layer/api/bug_report/bug_report_controller.py:339 var-local use_case `Any` @BugReportController.create_bug_report
- application/product_observability/driving_layer/api/bug_report/bug_report_controller.py:374 var-local decision `Any` @BugReportController.record_runtime_bug_report
- application/product_observability/driving_layer/api/bug_report/bug_report_controller.py:441 var-local use_case `Any` @BugReportController.record_runtime_bug_report
- application/review/driven_layer/adapter/persistence/domain_bypass_query/public_content_reviews_query.py:60 var-local raw `Any` @DjangoPublicContentReviewsDomainBypassQuery._average
- application/saju/domain_layer/domain_service/v2_reading_assembler.py:395 var-local saju `Any` @-._parse_boundary_saju
- application/saju/domain_layer/domain_service/v2_reading_assembler.py:396 var-local ilju_value `Any` @-._parse_boundary_saju
- application/saju/domain_layer/domain_service/v2_reading_assembler.py:398 var-local ilgan_obj `Any` @-._parse_boundary_saju
- application/saju/domain_layer/domain_service/v2_reading_assembler.py:403 var-local sinsal_list `Any` @-._parse_boundary_saju
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:265 sig-arg condition `Any` @-._evaluate_condition
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:266 var-local raw `Any` @-._evaluate_condition
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:274 var-local key `Any` @-._evaluate_condition
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:275 var-local value `Any` @-._evaluate_condition
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:408 var-local raw_graphics `Any` @-._parse_chapter_response
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:424 var-local key `Any` @-._merge_graphics
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:425 var-local llm_data `Any` @-._merge_graphics
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:427 var-local data `Any` @-._merge_graphics
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:438 var-local meta `Any` @-._build_graphic_instruction
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:439 var-local x_axis `Any` @-._build_graphic_instruction
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:448 sig-arg x_axis `Any` @-._graphic_schema
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:667 var-local ilgan `Any` @-._build_saju_variables
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:674 var-local saju `Any` @-._build_saju_variables
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:691 var-local ohaeng `Any` @-._build_saju_variables
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:700 var-local sipseong_raw `Any` @-._build_saju_variables
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:711 var-local unseong_raw `Any` @-._build_saju_variables
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:716 var-local sinsal_raw `Any` @-._build_saju_variables
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:719 var-local relations_raw `Any` @-._build_saju_variables
- application/saju/domain_layer/domain_service/v3_reading_assembler.py:726 var-local unjagyong `Any` @-._build_saju_variables
