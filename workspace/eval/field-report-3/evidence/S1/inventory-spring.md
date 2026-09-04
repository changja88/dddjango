## spring — root=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3/spring subdir=application

### family=admin_form 클래스 39 (테스트 파일 0)
| BC | ①bare | ②ignore | ③alias | ④direct | ④direct(TC) | 기타 | 합 |
|---|---|---|---|---|---|---|---|
| accounts | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| fortune_character | 0 | 0 | 13 | 0 | 0 | 0 | 13 |
| fortune_intent | 0 | 4 | 0 | 0 | 0 | 0 | 4 |
| fortune_record | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| media_library | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| notification | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| promotion | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| query_translation | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| service_policy | 0 | 0 | 9 | 0 | 0 | 0 | 9 |
| wallet | 0 | 3 | 0 | 0 | 0 | 0 | 3 |
| **합** | 0 | 17 | 22 | 0 | 0 | 0 | 39 |

파일별:
- application/accounts/driven_layer/django_accounts/admin/account/panel.py: ②ignore=2
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/discount_rule_inline_form.py: ③alias=1
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/media_inline_form.py: ③alias=2
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/operating_hours_rule_inline_form.py: ③alias=1
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/work_reference_inline_form.py: ③alias=1
- application/fortune_character/driven_layer/django_fortune_character/admin/character/panel.py: ③alias=4
- application/fortune_character/driven_layer/django_fortune_character/admin/media_kind/form/media_kind_form.py: ③alias=1
- application/fortune_character/driven_layer/django_fortune_character/admin/media_kind/panel.py: ③alias=1
- application/fortune_character/driven_layer/django_fortune_character/admin/prompt_set/form/prompt_set_form.py: ③alias=1
- application/fortune_character/driven_layer/django_fortune_character/admin/prompt_set/panel.py: ③alias=1
- application/fortune_intent/driven_layer/django_fortune_intent/admin/intent_generation_configuration/form/intent_generation_configuration_form.py: ②ignore=1
- application/fortune_intent/driven_layer/django_fortune_intent/admin/intent_generation_configuration/panel.py: ②ignore=1
- application/fortune_intent/driven_layer/django_fortune_intent/admin/non_fortune_definition/form/non_fortune_definition_form.py: ②ignore=1
- application/fortune_intent/driven_layer/django_fortune_intent/admin/non_fortune_definition/panel.py: ②ignore=1
- application/fortune_record/driven_layer/django_fortune_record/admin/fortune_record/panel.py: ②ignore=1
- application/media_library/driven_layer/django_media_library/admin/media_asset/form/media_asset_form.py: ②ignore=1
- application/media_library/driven_layer/django_media_library/admin/media_asset/panel.py: ②ignore=1
- application/notification/driven_layer/django_notification/admin/email_notice_template/form/email_notice_template_form.py: ②ignore=1
- application/notification/driven_layer/django_notification/admin/email_notice_template/panel.py: ②ignore=1
- application/promotion/driven_layer/django_promotion/admin/campaign_usage/panel.py: ②ignore=1
- application/query_translation/driven_layer/django_query_translation/admin/query_translation_configuration/form/query_translation_configuration_form.py: ②ignore=1
- application/query_translation/driven_layer/django_query_translation/admin/query_translation_configuration/panel.py: ②ignore=1
- application/service_policy/driven_layer/django_service_policy/admin/action_kind/form/action_kind_form.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/action_kind/panel.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/limit_rule/form/limit_rule_form.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/limit_rule/panel.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/suspension/form/suspension_form.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/suspension/panel.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/suspension_reason/form/suspension_reason_form.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/suspension_reason/panel.py: ③alias=1
- application/service_policy/driven_layer/django_service_policy/admin/usage_record/panel.py: ③alias=1
- application/wallet/driven_layer/django_wallet/admin/ledger_entry/panel.py: ②ignore=1
- application/wallet/driven_layer/django_wallet/admin/reservation_ticket/panel.py: ②ignore=1
- application/wallet/driven_layer/django_wallet/admin/wallet/panel.py: ②ignore=1

속성 줄 `type: ignore[type-arg]`: 1 [('application/accounts/driven_layer/django_accounts/admin/account/panel.py', 83)]
기저별: {'StackedInline': 1, 'ModelAdmin': 18, 'ModelForm': 15, 'BaseInlineFormSet': 1, 'TabularInline': 4}

### family=cbv 클래스 0 (테스트 파일 0)
| BC | ①bare | ②ignore | ③alias | ④direct | ④direct(TC) | 기타 | 합 |
|---|---|---|---|---|---|---|---|
| **합** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

파일별:

속성 줄 `type: ignore[type-arg]`: 0 []
기저별: {}

### lenient-only(attr 이름만 일치 · 정본 경로 아님): 0

### 파일 전체 `type: ignore[type-arg]` 줄 합: 18
- application/accounts/driven_layer/django_accounts/admin/account/panel.py: 3
- application/fortune_intent/driven_layer/django_fortune_intent/admin/intent_generation_configuration/form/intent_generation_configuration_form.py: 1
- application/fortune_intent/driven_layer/django_fortune_intent/admin/intent_generation_configuration/panel.py: 1
- application/fortune_intent/driven_layer/django_fortune_intent/admin/non_fortune_definition/form/non_fortune_definition_form.py: 1
- application/fortune_intent/driven_layer/django_fortune_intent/admin/non_fortune_definition/panel.py: 1
- application/fortune_record/driven_layer/django_fortune_record/admin/fortune_record/panel.py: 1
- application/media_library/driven_layer/django_media_library/admin/media_asset/form/media_asset_form.py: 1
- application/media_library/driven_layer/django_media_library/admin/media_asset/panel.py: 1
- application/notification/driven_layer/django_notification/admin/email_notice_template/form/email_notice_template_form.py: 1
- application/notification/driven_layer/django_notification/admin/email_notice_template/panel.py: 1
- application/promotion/driven_layer/django_promotion/admin/campaign_usage/panel.py: 1
- application/query_translation/driven_layer/django_query_translation/admin/query_translation_configuration/form/query_translation_configuration_form.py: 1
- application/query_translation/driven_layer/django_query_translation/admin/query_translation_configuration/panel.py: 1
- application/wallet/driven_layer/django_wallet/admin/ledger_entry/panel.py: 1
- application/wallet/driven_layer/django_wallet/admin/reservation_ticket/panel.py: 1
- application/wallet/driven_layer/django_wallet/admin/wallet/panel.py: 1

### `type: ignore[misc]` 줄 합: 14
- application/chat_relay/driven_layer/adapter/persistence/repository/conversation_room_repository.py: rooms = rooms.filter(selected_activity_id__isnull=False)  # type: ignore[misc]
- application/chat_relay/driven_layer/adapter/persistence/repository/conversation_room_repository.py: rooms.order_by(  # type: ignore[misc]
- application/fortune_catalog/test/unit/test_fortune_type.py: fortune_type.fortune_id = "changed"  # type: ignore[misc]
- application/fortune_character/driven_layer/django_fortune_character/admin/character/form/character_form.py: class CharacterForm(TranslatableModelForm):  # type: ignore[misc]
- application/fortune_character/driven_layer/django_fortune_character/admin/character/panel.py: class CharacterAdmin(TranslatableAdmin):  # type: ignore[misc]
- application/fortune_character/driven_layer/django_fortune_character/models/character_model.py: class CharacterModel(TranslatableModelMixin, models.Model):  # type: ignore[misc]
- application/llm_access/test/unit/test_environment_adapter.py: second.api_key = "changed"  # type: ignore[misc]
- application/media_library/test/unit/test_asset_slug.py: key.value = "changed"  # type: ignore[misc]
- application/product/driven_layer/django_product/admin/product/form/product_form.py: class ProductForm(TranslatableModelForm):  # type: ignore[misc]
- application/product/driven_layer/django_product/admin/product/panel.py: class ProductAdmin(TranslatableAdmin):  # type: ignore[misc]
- application/product/driven_layer/django_product/models/product_model.py: class ProductModel(TranslatableModelMixin, models.Model):  # type: ignore[misc]
- application/promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py: class CampaignForm(TranslatableModelForm):  # type: ignore[misc]
- application/promotion/driven_layer/django_promotion/admin/campaign/panel.py: class CampaignAdmin(TranslatableAdmin):  # type: ignore[misc]
- application/promotion/driven_layer/django_promotion/models/campaign_model.py: class CampaignModel(TranslatableModelMixin, models.Model):  # type: ignore[misc]
