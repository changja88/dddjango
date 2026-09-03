# spring — root=/Users/hyun/Desktop/spring_dream_server
- .py files scanned: 2918 (parse failures: 0) — skip dirs: ['.claude', '.codex', '.dddjango', '.dddjango-web', '.git', '.idea', '.mypy_cache', '.playwright-mcp', '.pytest_cache', '.ruff_cache', '.serena', '.superpowers', '.venv', '.worktrees', '__pycache__', 'migrations', 'node_modules', 'site-packages', 'venv']
- files using bare `Any` name without a typing import (heuristic counted anyway): 0

## D — always-raise functions by return-annotation kind
- total always-raise functions: 49 → NoReturn=5, None=11, other=33
- `-> None` always-raise: 11 = core(helper-like, non-NotImplementedError) 9 + stub(NotImplementedError/abstract) 2

### D `-> None` core — per group (files | prod | test)
| group | files | core -> None | of which test | NotImpl/abstract -> None | -> NoReturn always-raise | -> missing always-raise |
|---|---|---|---|---|---|---|
| application/accounts | 234 | 0 | 0 | 2 | 0 | 0 |
| application/chat_relay | 331 | 1 | 1 | 0 | 0 | 0 |
| application/llm_access | 133 | 2 | 0 | 0 | 3 | 0 |
| application/product | 114 | 1 | 1 | 0 | 0 | 0 |
| application/promotion | 196 | 3 | 3 | 0 | 0 | 0 |
| framework/technology | 46 | 0 | 0 | 0 | 2 | 0 |
| tests | 39 | 2 | 2 | 0 | 0 | 0 |

### D core list (`file:line func` — raised — test?)
- application/chat_relay/test/integration/test_postgresql_turn_cas.py:261 fail_save_items — raise TemporaryPersistenceUnavailable [test]
- application/llm_access/domain_layer/generation_audit/generation_audit.py:56 __init__ — raise TypeError
- application/llm_access/domain_layer/generation_audit/value_object/serialized_audit_payload.py:464 __init__ — raise TypeError
- application/product/test/integration/test_product_transaction_boundary.py:48 fail_translation_save — raise RuntimeError [test]
- application/promotion/test/integration/test_campaign_transaction_boundary.py:45 _save_targets — raise RuntimeError [test]
- application/promotion/test/integration/test_record_campaign_usage_open_host_service.py:112 execute — raise _failure [test]
- application/promotion/test/unit/test_list_effective_prices_application.py:64 save — raise AssertionError [test]
- tests/test_ontology_c11.py:205 stop_after_data_only — raise StopAfterDataOnly [test]
- tests/test_rag_builder_steps.py:2470 fail_rename — raise OSError [test]

### D stub list (NotImplementedError/abstract with -> None)
- application/accounts/test/unit/test_authenticate_account_use_case.py:48 save_new [test]
- application/accounts/test/unit/test_authenticate_account_use_case.py:60 save [test]

### D always-raise with `-> NoReturn` (correctly typed)
- application/llm_access/application_layer/generation/stream_generation/stream_generation_use_case.py:358 _terminate_provider_failure — raise _provider_capability_failure
- application/llm_access/application_layer/generation/stream_generation/stream_generation_use_case.py:388 _terminate_internal_failure — raise UnexpectedGenerationFailure
- application/llm_access/domain_layer/generation_audit/value_object/serialized_audit_payload.py:141 _raise_validation — raise _PayloadValidationError
- framework/technology/rag/runtime/ontology_evidence_contract_c08.py:813 _fail_closed — raise EvidenceContractC08ValidationError
- framework/technology/rag/runtime/service_runtime.py:642 _fail — raise ServiceRuntimeContractError

### D always-raise with missing return annotation

## NoReturn / Never usage (import + annotation)
| group | imports | annotations |
|---|---|---|
| application/llm_access | 2 | 3 |
| framework/technology | 2 | 2 |
- total: imports=4 annotations=5
  - application/llm_access/application_layer/generation/stream_generation/stream_generation_use_case.py:358 _terminate_provider_failure -> NoReturn
  - application/llm_access/application_layer/generation/stream_generation/stream_generation_use_case.py:388 _terminate_internal_failure -> NoReturn
  - application/llm_access/domain_layer/generation_audit/value_object/serialized_audit_payload.py:141 _raise_validation -> NoReturn
  - framework/technology/rag/runtime/ontology_evidence_contract_c08.py:813 _fail_closed -> NoReturn
  - framework/technology/rag/runtime/service_runtime.py:642 _fail -> NoReturn

## E — explicit `Any` occurrences
- total: 951 · bare=194 · bare_optional=1 · nested=756
- by site: sig-arg=405, sig-ret=250, sig-star=14, var-attr=3, var-class=27, var-local=240, var-module=12
- by site×kind: sig-arg/bare=75, sig-arg/bare_optional=1, sig-arg/nested=329, sig-ret/bare=24, sig-ret/nested=226, sig-star/bare=14, var-attr/nested=3, var-class/nested=27, var-local/bare=81, var-local/nested=159, var-module/nested=12

### E per group (sig = signature arg/star/ret · var = AnnAssign module/class/local/attr)
| group | files | sig bare(+opt) | sig nested | var bare(+opt) | var nested | total | of which in test files |
|---|---|---|---|---|---|---|---|
| (root) | 3 | 9(+0) | 0 | 6(+0) | 0 | 15 | 0 |
| application/accounts | 234 | 4(+0) | 1 | 4(+0) | 7 | 16 | 12 |
| application/fortune_calculation | 180 | 0(+0) | 2 | 0(+0) | 4 | 6 | 0 |
| application/fortune_catalog | 102 | 0(+0) | 4 | 0(+0) | 3 | 7 | 7 |
| application/fortune_character | 262 | 10(+0) | 14 | 17(+0) | 9 | 50 | 14 |
| application/fortune_intent | 130 | 0(+0) | 2 | 0(+0) | 3 | 5 | 1 |
| application/fortune_reading | 185 | 9(+0) | 10 | 13(+0) | 5 | 37 | 37 |
| application/fortune_record | 145 | 1(+1) | 3 | 9(+0) | 8 | 22 | 18 |
| application/llm_access | 133 | 0(+0) | 1 | 0(+0) | 2 | 3 | 3 |
| application/media_library | 130 | 9(+0) | 2 | 1(+0) | 4 | 16 | 11 |
| application/notification | 92 | 0(+0) | 1 | 0(+0) | 1 | 2 | 0 |
| application/product | 114 | 1(+0) | 7 | 7(+0) | 3 | 18 | 3 |
| application/promotion | 196 | 2(+0) | 12 | 14(+0) | 17 | 45 | 23 |
| application/query_translation | 113 | 0(+0) | 4 | 0(+0) | 5 | 9 | 1 |
| application/service_policy | 275 | 4(+0) | 5 | 8(+0) | 4 | 21 | 7 |
| application/wallet | 176 | 0(+0) | 0 | 0(+0) | 1 | 1 | 1 |
| framework/technology | 46 | 59(+0) | 454 | 2(+0) | 118 | 633 | 0 |
| tests | 39 | 5(+0) | 33 | 0(+0) | 7 | 45 | 45 |

### E per top-level (application vs rest)
| top | files | sig bare(+opt) | sig nested | var bare(+opt) | var nested | total | in test files |
|---|---|---|---|---|---|---|---|
| (root) | 3 | 9(+0) | 0 | 6(+0) | 0 | 15 | 0 |
| application | 2799 | 40(+1) | 68 | 73(+0) | 76 | 258 | 138 |
| framework | 56 | 59(+0) | 454 | 2(+0) | 118 | 633 | 0 |
| tests | 39 | 5(+0) | 33 | 0(+0) | 7 | 45 | 45 |

### E top 10 files
- 104  framework/technology/rag/runtime/rag_builder/steps/__init__.py  (bare 20 / nested 84)
-  68  framework/technology/rag/runtime/release_store.py  (bare 15 / nested 53)
-  64  framework/technology/rag/runtime/ontology_control.py  (bare 0 / nested 64)
-  44  framework/technology/rag/runtime/rag_builder/source_projection.py  (bare 0 / nested 44)
-  40  framework/technology/rag/runtime/rag_builder/coordinates.py  (bare 1 / nested 39)
-  29  application/fortune_reading/test/unit/test_query_translation_adapter.py  (bare 22 / nested 7)
-  25  framework/technology/rag/runtime/glossary.py  (bare 1 / nested 24)
-  23  framework/technology/rag/runtime/registry_snapshot.py  (bare 2 / nested 21)
-  22  framework/technology/rag/runtime/yeonhae_ontology.py  (bare 0 / nested 22)
-  21  framework/technology/rag/runtime/ontology_evidence_contract_c08.py  (bare 0 / nested 21)

### E top 10 files — production only (non-test)
- 104  framework/technology/rag/runtime/rag_builder/steps/__init__.py  (bare 20 / nested 84)
-  68  framework/technology/rag/runtime/release_store.py  (bare 15 / nested 53)
-  64  framework/technology/rag/runtime/ontology_control.py  (bare 0 / nested 64)
-  44  framework/technology/rag/runtime/rag_builder/source_projection.py  (bare 0 / nested 44)
-  40  framework/technology/rag/runtime/rag_builder/coordinates.py  (bare 1 / nested 39)
-  25  framework/technology/rag/runtime/glossary.py  (bare 1 / nested 24)
-  23  framework/technology/rag/runtime/registry_snapshot.py  (bare 2 / nested 21)
-  22  framework/technology/rag/runtime/yeonhae_ontology.py  (bare 0 / nested 22)
-  21  framework/technology/rag/runtime/ontology_evidence_contract_c08.py  (bare 0 / nested 21)
-  21  framework/technology/rag/runtime/yeonhae_authorized.py  (bare 0 / nested 21)

### E nested shapes — top 12 (with up to 3 examples each: file:line site name @func/cls)
- 351  `dict[str, Any]`
    - application/fortune_calculation/driven_layer/adapter/lunisolar_calendar/packaged_table_adapter.py:50 var-local payload @PackagedTableLunisolarCalendarAdapter.__init__
    - application/fortune_calculation/driven_layer/adapter/place_directory/packaged_table_adapter.py:41 var-local city_payload @PackagedTablePlaceDirectoryAdapter.__init__
    - application/fortune_calculation/driven_layer/adapter/place_directory/packaged_table_adapter.py:44 var-local country_payload @PackagedTablePlaceDirectoryAdapter.__init__
- 148  `Mapping[str, Any]`
    - framework/technology/rag/runtime/glossary.py:206 sig-arg glossary_ref @-.verify_glossary_ref
    - framework/technology/rag/runtime/glossary.py:386 sig-arg translated_query @-.translated_query_digest
    - framework/technology/rag/runtime/glossary_coverage.py:101 sig-arg descriptor @-._artifact_ref
-  91  `list[dict[str, Any]]`
    - application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/character_writer.py:121 sig-ret  @-._valid_rows
    - application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/character_writer.py:122 var-local rows @-._valid_rows
    - framework/technology/rag/runtime/ditian_sui.py:44 sig-arg resources @-.validate_snapshot_resources
-  36  `Sequence[Mapping[str, Any]]`
    - framework/technology/rag/runtime/rag_builder/coordinates.py:223 sig-arg paragraphs @-._shidian_paragraph_identifiers
    - framework/technology/rag/runtime/rag_builder/crosswalk.py:54 sig-arg rows @-._validate_seed_rows
    - framework/technology/rag/runtime/rag_builder/crosswalk.py:122 sig-arg legacy_crosswalk_rows @-.derive_source_text_crosswalk_seed
-  20  `dict[str, dict[str, Any]]`
    - application/query_translation/driven_layer/adapter/glossary_translation/rag_adapter.py:109 var-local translated @RagGlossaryTranslationAdapter._translate_verified_glossary
    - framework/technology/rag/runtime/glossary.py:362 sig-ret  @-.translate_question_by_language
    - framework/technology/rag/runtime/glossary_coverage.py:136 sig-ret  @-._snapshot_entries
-  10  `tuple[Mapping[str, Any], ...]`
    - framework/technology/rag/runtime/rag_builder/crosswalk.py:35 var-class rows @CrosswalkProjection.-
    - framework/technology/rag/runtime/rag_builder/crosswalk.py:42 var-class rows @CrosswalkSeed.-
    - framework/technology/rag/runtime/rag_builder/index.py:34 var-class passages @HybridIndex.-
-  10  `Iterable[Mapping[str, Any]]`
    - framework/technology/rag/runtime/rag_builder/source_projection.py:94 sig-arg passages @-._unique_passages
    - framework/technology/rag/runtime/rag_builder/source_projection.py:282 sig-arg passages @-.project_source_locations
    - framework/technology/rag/runtime/rag_builder/source_projection.py:351 sig-arg passages @-.validate_source_location_projection
-   7  `Mapping[str, Mapping[str, Any]]`
    - framework/technology/rag/runtime/rag_builder/steps/__init__.py:1726 sig-arg fixture_outcomes @-._aggregate_fixture_observations
    - framework/technology/rag/runtime/rag_builder/steps/__init__.py:2802 sig-arg gate_payloads @-._gate_result_refs
    - framework/technology/rag/runtime/rag_builder/steps/__init__.py:2817 sig-arg fixture_outcomes @-._fixture_results_bytes
-   4  `dict[str, Any] | None`
    - framework/technology/rag/runtime/service_runtime.py:210 var-local preflight @-._validate_v2_materialization_refs
    - framework/technology/rag/runtime/service_runtime.py:211 var-local build @-._validate_v2_materialization_refs
    - application/llm_access/test/unit/test_generation_audit.py:332 var-local json_schema @-._request_payload
-   4  `tuple[dict[str, Any], ...]`
    - framework/technology/rag/runtime/ontology_control.py:2758 sig-ret  @-._runtime_contract_fixture_specs
    - tests/test_ontology_c11.py:870 var-local projection_rows @-.test_shadow_v2_uses_public_glossary_and_common_retriever_without_provider
    - tests/test_ontology_c11.py:1834 var-local projection_rows @-.test_data_canary_replays_sparql_and_translated_retrieval_without_provider
-   3  `dict[str, list[dict[str, Any]]]`
    - framework/technology/rag/runtime/ditian_sui.py:368 sig-ret  @-.build_dual_passages
    - framework/technology/rag/runtime/ontology_evidence_contract_c08.py:199 var-module APPROVED_ARTIFACT_CHILDREN @-.-
    - framework/technology/rag/runtime/yeonhae_authorized.py:96 sig-ret  @-.parse_authorized_source
-   3  `list[tuple[int, dict[str, Any], str]]`
    - framework/technology/rag/runtime/glossary.py:247 sig-ret  @-._find_matches
    - framework/technology/rag/runtime/glossary.py:276 var-local matched @-._find_matches
    - framework/technology/rag/runtime/glossary.py:305 sig-arg matches @-._build_translated_query

### E nested — outermost container tally
dict=393, Mapping=160, list=106, tuple=43, Sequence=39, Iterable=10, Callable=2, ClassVar=1, MappingProxyType=1, admin.ModelAdmin=1

### E nested — enclosing function-name tally (top 15, production only)
<module/class>=38, clean=30, materialize_guide_release=7, create_release=7, get_actions=6, build_passages=6, _project_wikisource=6, project_source_evidence_crosswalk=6, _observe_c05_fixtures=6, _evaluation_summary_payload=6, _build_change_set=6, _find_matches=5, _verify_registry_rags_and_glossary=5, _project_shidian=5, project_source_locations=5

### E bare(+optional) — production list, by site (top 40)
- application/accounts/driving_layer/api/account/account_controller.py:357 var-local account_user `Any` @AccountController.change_password
- application/accounts/driving_layer/api/account/account_controller.py:396 var-local account_user `Any` @AccountController.get_my_profile
- application/accounts/driving_layer/api/account/account_controller.py:445 var-local account_user `Any` @AccountController.update_my_profile
- application/accounts/driving_layer/api/account/account_controller.py:511 var-local account_user `Any` @AccountController.withdraw_account
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/character_writer.py:71 var-local model `Any` @-._assemble_command
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/character_writer.py:115 var-local language `Any` @-._editing_language
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/character_writer.py:132 var-local media_kind `Any` @-._to_media_data
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/character_writer.py:133 var-local file_value `Any` @-._to_media_data
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/character_writer.py:166 var-local row_id `Any` @-._row_id
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/time_rule_gate.py:24 var-local period_start `Any` @-.build_time_rule_from_row
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/time_rule_gate.py:25 var-local period_end `Any` @-.build_time_rule_from_row
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/time_rule_gate.py:28 var-local recurring_start `Any` @-.build_time_rule_from_row
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/time_rule_gate.py:29 var-local recurring_end `Any` @-.build_time_rule_from_row
- application/fortune_character/driven_layer/django_fortune_character/admin/character/feature/time_rule_gate.py:30 var-local recurring_timezone `Any` @-.build_time_rule_from_row
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/character_form.py:40 var-local default_language_value `Any` @CharacterForm.clean
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/character_form.py:49 var-local text_value `Any` @CharacterForm.clean
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/media_inline_form.py:67 var-local media_kind `Any` @MediaInlineFormSet._iter_present_media
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/media_inline_form.py:70 var-local file_value `Any` @MediaInlineFormSet._iter_present_media
- application/fortune_character/driven_layer/django_fortune_character/admin/prompt_set/form/prompt_set_form.py:49 var-local weight_value `Any` @PromptSetForm.clean
- application/fortune_character/driven_layer/django_fortune_character/admin/prompt_set/form/prompt_set_form.py:55 var-local structure_value `Any` @PromptSetForm.clean
- application/fortune_record/driven_layer/django_fortune_record/models/fortune_record_model.py:15 sig-star kwargs `Any` @_FortuneRecordQuerySet.update
- application/fortune_record/driven_layer/django_fortune_record/models/fortune_record_model.py:95 sig-arg using `Any | None` @FortuneRecordModel.delete
- application/fortune_record/driving_layer/api/record_archive/record_archive_controller.py:59 var-local account_user `Any` @FortuneRecordController.list_fortune_records
- application/fortune_record/driving_layer/api/record_archive/record_archive_controller.py:100 var-local account_user `Any` @FortuneRecordController.get_fortune_record
- application/media_library/driven_layer/django_media_library/admin/media_asset/feature/media_asset_writer.py:27 var-local upload `Any` @-._assemble_command
- application/product/driven_layer/django_product/admin/product/form/product_form.py:58 var-local language_value `Any` @ProductForm._editing_language
- application/product/driven_layer/django_product/admin/product/form/product_form.py:67 var-local name `Any` @ProductForm._validate_name
- application/product/driven_layer/django_product/admin/product/form/product_form.py:81 var-local amount `Any` @ProductForm._validate_service_currency_amount
- application/product/driven_layer/django_product/admin/product/form/product_form.py:90 var-local currency `Any` @ProductForm._validate_list_price
- application/product/driven_layer/django_product/admin/product/form/product_form.py:91 var-local amount `Any` @ProductForm._validate_list_price
- application/product/driven_layer/django_product/admin/product/panel.py:55 var-local language_value `Any` @ProductAdmin.save_model
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:100 sig-star args `Any` @CampaignForm.__init__
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:100 sig-star kwargs `Any` @CampaignForm.__init__
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:155 var-local language_value `Any` @CampaignForm._editing_language
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:164 var-local raw_name `Any` @CampaignForm._validated_name
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:196 var-local raw_kind `Any` @CampaignForm._validated_target
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:214 var-local raw_kind `Any` @CampaignForm._validated_discount
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:215 var-local raw_value `Any` @CampaignForm._validated_discount
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:262 var-local raw_condition `Any` @CampaignForm._validated_campaign
- application/promotion/driven_layer/django_promotion/admin/campaign/panel.py:60 var-local language_value `Any` @CampaignAdmin.save_model
