## kkebi — root=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3/kkebi subdir=application

### family=admin_form 클래스 67 (테스트 파일 0)
| BC | ①bare | ②ignore | ③alias | ④direct | ④direct(TC) | 기타 | 합 |
|---|---|---|---|---|---|---|---|
| billing | 0 | 7 | 0 | 0 | 0 | 0 | 7 |
| consultation | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| daily | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| identity | 0 | 0 | 4 | 0 | 0 | 0 | 4 |
| image | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| notification | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| review | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| saju | 0 | 0 | 15 | 0 | 15 | 0 | 30 |
| share | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| tarot | 0 | 10 | 0 | 0 | 0 | 0 | 10 |
| top3 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| **합** | 0 | 21 | 31 | 0 | 15 | 0 | 67 |

파일별:
- application/billing/driven_layer/django_billing/admin/coupon_campaign/panel.py: ②ignore=1
- application/billing/driven_layer/django_billing/admin/coupon_entitlement/panel.py: ②ignore=1
- application/billing/driven_layer/django_billing/admin/import_issue/panel.py: ②ignore=1
- application/billing/driven_layer/django_billing/admin/import_run/panel.py: ②ignore=1
- application/billing/driven_layer/django_billing/admin/payment_order/panel.py: ②ignore=1
- application/billing/driven_layer/django_billing/admin/point_account/panel.py: ②ignore=1
- application/billing/driven_layer/django_billing/admin/point_ledger_entry/panel.py: ②ignore=1
- application/consultation/driven_layer/django_consultation/admin/chat_message/panel.py: ③alias=1
- application/consultation/driven_layer/django_consultation/admin/chat_session/panel.py: ③alias=1
- application/consultation/driven_layer/django_consultation/admin/quota_refill_receipt/panel.py: ③alias=1
- application/daily/driven_layer/django_daily/admin/compatibility_results/panel.py: ③alias=1
- application/daily/driven_layer/django_daily/admin/fortunes/panel.py: ③alias=1
- application/daily/driven_layer/django_daily/admin/migration_audits/panel.py: ③alias=1
- application/identity/driven_layer/django_identity/admin/account/panel.py: ③alias=2
- application/identity/driven_layer/django_identity/admin/account_merge/panel.py: ③alias=1
- application/identity/driven_layer/django_identity/admin/profile/panel.py: ③alias=1
- application/image/driven_layer/django_image/admin/image/form/image_form.py: ③alias=1
- application/image/driven_layer/django_image/admin/image/panel.py: ③alias=1
- application/notification/driven_layer/django_notification/admin/marketing_consent/panel.py: ③alias=1
- application/notification/driven_layer/django_notification/admin/notification_event/panel.py: ③alias=1
- application/notification/driven_layer/django_notification/admin/push_token/panel.py: ③alias=1
- application/review/driven_layer/django_review/admin/review/panel.py: ③alias=1
- application/saju/driven_layer/django_saju/admin/bundle_item/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/relationship_profile/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_billing_feed_cursor/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_category/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_chart/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_chart_snapshot/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_content_category/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_merge_repoint_cursor/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_product/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_reading/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_reading_history/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_reconciliation/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_report_generation_event/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/saju_report_prompt/panel.py: ③alias=1, ④direct(TC)=1
- application/saju/driven_layer/django_saju/admin/self_saju_profile/panel.py: ③alias=1, ④direct(TC)=1
- application/share/driven_layer/django_share/admin/content_share/form/content_share_form.py: ②ignore=1
- application/share/driven_layer/django_share/admin/content_share/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_card/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_category/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_completion_notification_intent/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_generation_audit_record/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_prompt_backup/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_prompt_definition/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_reading/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_reading_version/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_spread/panel.py: ②ignore=1
- application/tarot/driven_layer/django_tarot/admin/tarot_topic/panel.py: ②ignore=1
- application/top3/driven_layer/django_top3/admin/post/form/post_form.py: ②ignore=1
- application/top3/driven_layer/django_top3/admin/post/panel.py: ②ignore=1

속성 줄 `type: ignore[type-arg]`: 0 []
기저별: {'ModelAdmin': 63, 'TabularInline': 1, 'ModelForm': 3}

### family=cbv 클래스 0 (테스트 파일 0)
| BC | ①bare | ②ignore | ③alias | ④direct | ④direct(TC) | 기타 | 합 |
|---|---|---|---|---|---|---|---|
| **합** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

파일별:

속성 줄 `type: ignore[type-arg]`: 0 []
기저별: {}

### lenient-only(attr 이름만 일치 · 정본 경로 아님): 0

### 파일 전체 `type: ignore[type-arg]` 줄 합: 22
- application/billing/driven_layer/django_billing/admin/coupon_campaign/panel.py: 1
- application/billing/driven_layer/django_billing/admin/coupon_entitlement/panel.py: 1
- application/billing/driven_layer/django_billing/admin/import_issue/panel.py: 1
- application/billing/driven_layer/django_billing/admin/import_run/panel.py: 1
- application/billing/driven_layer/django_billing/admin/payment_order/panel.py: 1
- application/billing/driven_layer/django_billing/admin/point_account/panel.py: 1
- application/billing/driven_layer/django_billing/admin/point_ledger_entry/panel.py: 1
- application/share/driven_layer/django_share/admin/content_share/form/content_share_form.py: 1
- application/share/driven_layer/django_share/admin/content_share/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_card/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_category/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_completion_notification_intent/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_generation_audit_record/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_prompt_backup/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_prompt_definition/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_reading/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_reading_version/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_spread/panel.py: 1
- application/tarot/driven_layer/django_tarot/admin/tarot_topic/panel.py: 1
- application/tarot/driving_layer/api/catalog/catalog_controller.py: 1
- application/top3/driven_layer/django_top3/admin/post/form/post_form.py: 1
- application/top3/driven_layer/django_top3/admin/post/panel.py: 1

### `type: ignore[misc]` 줄 합: 18
- application/billing/test/factories/coupon_campaign_model_factory.py: class CouponCampaignModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/billing/test/factories/coupon_entitlement_model_factory.py: class CouponEntitlementModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/billing/test/factories/point_account_model_factory.py: class PointAccountModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/billing/test/factories/point_ledger_entry_model_factory.py: class PointLedgerEntryModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/billing/test/unit/test_billing_event_stream.py: result.event.payment_id = 42  # type: ignore[misc]
- application/billing/test/unit/test_billing_event_stream.py: hydrated.journal = ()  # type: ignore[misc]
- application/billing/test/unit/test_billing_reconciliation_policy.py: classification.classifier_version = "changed"  # type: ignore[misc]
- application/billing/test/unit/test_billing_reconciliation_policy.py: fact.value_text = '"changed"'  # type: ignore[misc]
- application/billing/test/unit/test_billing_reconciliation_policy.py: finding.severity = BillingImportIssueSeverity.INFO  # type: ignore[misc]
- application/billing/test/unit/test_billing_reconciliation_policy.py: issue.source_key = "changed"  # type: ignore[misc]
- application/billing/test/unit/test_legacy_billing_classifier.py: evidence.owner_resolved = False  # type: ignore[misc]
- application/billing/test/unit/test_legacy_billing_classifier.py: classification.fulfillment_id = None  # type: ignore[misc]
- application/review/test/factories/review_model_factory.py: class ReviewModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/review/test/unit/test_nickname_snapshot.py: snapshot.value = "이**"  # type: ignore[misc]
- application/saju/test/factories/saju_product_model_factory.py: class SajuProductModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/saju/test/factories/saju_reading_model_factory.py: class SajuReadingModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/saju/test/factories/saju_report_prompt_model_factory.py: class SajuReportPromptModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
- application/saju/test/factories/self_saju_profile_model_factory.py: class SelfSajuProfileModelFactory(factory.django.DjangoModelFactory):  # type: ignore[misc]
