# 맹검 소급 전사 — fortune_reading G1 설계 명세 (e152e57, registry 정렬본)

- 원본: `git show e152e57:.dddjango/20260831-2331-fortune-reading/design-spec.md`
  → 로컬 사본 `spec-e152e57.md` (2094행). 아래 `sNNN`은 이 사본의 행 번호다.
- 유일 근거: 위 명세 원문 + 성문 형식 규범. 구현 코드·검사기·orders·violations는 열지 않았다.
- 문서 상태(s11): «P2 registry-contract 결정 A의 whole-G1 architect amendment 완료 …
  implementation registry proof PENDING»; registry amendment 8건 #13/#385/#216/#574/#473/#212/#551/#129.

---

## 블록 1 — file-plan

표기: `<태그><TAB><경로>  # sNNN[: 발췌]`. §6.2 트리(s580~s817) 발췌는 경로 문자열과 동일.
범위 판단은 ① 전사본과 동일 규칙(자백 참조): 순수 `__init__.py`·persistence/django 고정 slot 제외,
«없음/0-byte» 주석 슬롯은 `empty`, read-only/gate-only inventory(s1313~s1323)·registry gate 스크립트·
T18 audit block은 비전사. 파일 계획 내 와일드카드 0 → `# 미전개` 0.

```paths
# ── §6.2 신규 BC 트리 (s578 «다음이 신규 파일의 허용·계획 목록이다»)
add	application/fortune_reading/composition_root/dependency_wiring.py	# s585
empty	application/fortune_reading/composition_root/event_wiring.py	# s586: «event 0이므로 0-byte empty fixed file»
empty	application/fortune_reading/published_event/__init__.py	# s588: «published event 없음»
add	application/fortune_reading/driving_layer/api/api_router.py	# s593
add	application/fortune_reading/driving_layer/api/bc_error_schema.py	# s594 (s495 «단독 소유»)
add	application/fortune_reading/driving_layer/api/evidence/evidence_controller.py	# s597
add	application/fortune_reading/driving_layer/api/evidence/schema/schema_in.py	# s600: «HTTP request owner; …»
add	application/fortune_reading/driving_layer/api/evidence/schema/schema_out.py	# s601
empty	application/fortune_reading/driving_layer/api/webhook/__init__.py	# s603: «provider 없음»
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py	# s608
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/request/prepare_fortune_evidence_request.py	# s613
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/response/prepare_fortune_evidence_response.py	# s616
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_published_error.py	# s619
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_exception.py	# s620
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/citation_validation_service.py	# s623
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/request/validate_citations_request.py	# s628
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/validate_citations_response.py	# s631
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/get_cited_answer_schema_response.py	# s632
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/exception/citation_validation_published_error.py	# s635
empty	application/fortune_reading/driving_layer/cron_job/__init__.py	# s637: «jobs 없음»
empty	application/fortune_reading/driving_layer/event_subscription/event_router.py	# s640: «subscription 0이므로 0-byte empty fixed file»
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case.py	# s647
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_command.py	# s648
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_query.py	# s649
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_result.py	# s650
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_use_case.py	# s655
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_command.py	# s656
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_query.py	# s657
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_result.py	# s658
add	application/fortune_reading/application_layer/port/query_translation/query_translation_port.py	# s663
add	application/fortune_reading/application_layer/port/query_translation/translated_query_out.py	# s664
add	application/fortune_reading/application_layer/port/query_translation/exception.py	# s665: «두 local port exception의 단일 owner» (2d44743의 empty slot → 실소유 파일로 반전)
add	application/fortune_reading/application_layer/port/reading_bundle/reading_bundle_port.py	# s668
add	application/fortune_reading/application_layer/port/reading_bundle/pinned_reading_bundle_out.py	# s669
add	application/fortune_reading/application_layer/port/reading_bundle/exception.py	# s670 (s1878 ReadingBundleContractMismatch 소유)
add	application/fortune_reading/application_layer/port/evidence_retrieval/evidence_retrieval_port.py	# s673
add	application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_result_out.py	# s674
add	application/fortune_reading/application_layer/port/evidence_retrieval/exception.py	# s675
add	application/fortune_reading/application_layer/port/evidence_digest/evidence_digest_port.py	# s678
add	application/fortune_reading/application_layer/port/evidence_digest/exception.py	# s679 (s1878 «digest adapter normalization failure만 … 소유»)
empty	application/fortune_reading/application_layer/port/domain_bypass_query/__init__.py	# s681: «bypass query 없음»
empty	application/fortune_reading/application_layer/port/unit_of_work/__init__.py	# s683: «UoW 없음»
add	application/fortune_reading/domain_layer/shared_value_object/bundle_selection_mismatch.py	# s688
add	application/fortune_reading/domain_layer/shared_value_object/invalid_reading_request.py	# s689
add	application/fortune_reading/domain_layer/shared_value_object/book_usage_policy.py	# s690
add	application/fortune_reading/domain_layer/shared_value_object/work_rag_ref.py	# s691
add	application/fortune_reading/domain_layer/shared_value_object/reading_character.py	# s692
add	application/fortune_reading/domain_layer/shared_value_object/reading_request.py	# s693
add	application/fortune_reading/domain_layer/shared_value_object/calculation_output_contract_mismatch.py	# s694
add	application/fortune_reading/domain_layer/shared_value_object/pillar_view.py	# s695
add	application/fortune_reading/domain_layer/shared_value_object/four_pillars_projection.py	# s696
add	application/fortune_reading/domain_layer/shared_value_object/major_fortune_projection.py	# s697
add	application/fortune_reading/domain_layer/shared_value_object/pre_major_fortune_projection.py	# s698
add	application/fortune_reading/domain_layer/shared_value_object/annual_fortune_projection.py	# s699
add	application/fortune_reading/domain_layer/shared_value_object/table_ref_projection.py	# s700
add	application/fortune_reading/domain_layer/shared_value_object/calculation_trace_projection.py	# s701
add	application/fortune_reading/domain_layer/shared_value_object/calculation_projection.py	# s702
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_contract_ref.py	# s703
add	application/fortune_reading/domain_layer/shared_value_object/rag_release_ref.py	# s704
add	application/fortune_reading/domain_layer/shared_value_object/available_retrieval_entry.py	# s705
add	application/fortune_reading/domain_layer/shared_value_object/reading_constraints.py	# s706
add	application/fortune_reading/domain_layer/shared_value_object/pinned_reading_bundle.py	# s707
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target.py	# s708
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_plan.py	# s709
add	application/fortune_reading/domain_layer/shared_value_object/translation_term_set.py	# s710
add	application/fortune_reading/domain_layer/shared_value_object/translation_call_trace.py	# s711
add	application/fortune_reading/domain_layer/shared_value_object/translation_call_outcome.py	# s712
add	application/fortune_reading/domain_layer/shared_value_object/translation_disposition_kind.py	# s713
add	application/fortune_reading/domain_layer/shared_value_object/translation_disposition.py	# s714
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target_state.py	# s715
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target_trace.py	# s716
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target_outcome.py	# s717
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_disposition_kind.py	# s718
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_disposition.py	# s719
add	application/fortune_reading/domain_layer/shared_value_object/source_location.py	# s720
add	application/fortune_reading/domain_layer/shared_value_object/evidence_source.py	# s721
add	application/fortune_reading/domain_layer/shared_value_object/allowed_evidence.py	# s722 (WIP retain-and-trim s837)
add	application/fortune_reading/domain_layer/shared_value_object/evidence_digest_conflict.py	# s723
add	application/fortune_reading/domain_layer/shared_value_object/evidence_set.py	# s724
add	application/fortune_reading/domain_layer/shared_value_object/evidence_grouping.py	# s725
add	application/fortune_reading/domain_layer/shared_value_object/allowed_evidence_digest.py	# s726
add	application/fortune_reading/domain_layer/shared_value_object/evidence_set_digest.py	# s727
add	application/fortune_reading/domain_layer/shared_value_object/digested_allowed_evidence.py	# s728
add	application/fortune_reading/domain_layer/shared_value_object/retrieved_evidence.py	# s729
add	application/fortune_reading/domain_layer/shared_value_object/evidence_set_view.py	# s730
add	application/fortune_reading/domain_layer/shared_value_object/evidence_group_view.py	# s731
add	application/fortune_reading/domain_layer/shared_value_object/evidence_crosswalk_view.py	# s732
add	application/fortune_reading/domain_layer/shared_value_object/reading_method_view.py	# s733
add	application/fortune_reading/domain_layer/shared_value_object/evidence_bundle.py	# s734
add	application/fortune_reading/domain_layer/shared_value_object/abstention_reason.py	# s735
add	application/fortune_reading/domain_layer/shared_value_object/abstained.py	# s736 (exact 5-field 계약 s116~s124)
add	application/fortune_reading/domain_layer/shared_value_object/invalid_citation.py	# s737
add	application/fortune_reading/domain_layer/shared_value_object/citation_validation.py	# s738
add	application/fortune_reading/domain_layer/domain_service/validate_calculation_output.py	# s741
add	application/fortune_reading/domain_layer/domain_service/apply_reading_request_policy.py	# s742
add	application/fortune_reading/domain_layer/domain_service/plan_retrieval.py	# s743
add	application/fortune_reading/domain_layer/domain_service/classify_translation_outcome.py	# s744
add	application/fortune_reading/domain_layer/domain_service/fold_retrieval_outcome.py	# s745
add	application/fortune_reading/domain_layer/domain_service/assemble_evidence.py	# s746
add	application/fortune_reading/domain_layer/domain_service/validate_citations.py	# s747
add	application/fortune_reading/driven_layer/django_fortune_reading/apps.py	# s752 (s1274 exact class binding)
add	application/fortune_reading/driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py	# s762
empty	application/fortune_reading/driven_layer/adapter/external_system/__init__.py	# s764: «socket-opening external system adapter 없음»
add	application/fortune_reading/driven_layer/adapter/reading_bundle/rag_runtime_adapter.py	# s767
add	application/fortune_reading/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py	# s770
add	application/fortune_reading/driven_layer/adapter/evidence_digest/rfc8785_adapter.py	# s773
add	application/fortune_reading/test/unit/test_calculation_output_contract.py	# s783 (T01 s1477)
add	application/fortune_reading/test/unit/test_cited_answer_schema_equivalence.py	# s784 (T09 s1485)
add	application/fortune_reading/test/unit/test_reading_request.py	# s785 (T02 s1478)
add	application/fortune_reading/test/unit/test_reading_request_policy_service.py	# s786 (T02 s1478)
add	application/fortune_reading/test/unit/test_retrieval_planning_service.py	# s787 (T03/T04 s1479~s1480)
add	application/fortune_reading/test/unit/test_evidence_assembly_service.py	# s788 (T05/T07 s1481/s1483)
add	application/fortune_reading/test/unit/test_allowed_evidence.py	# s789 (T06 s1482)
add	application/fortune_reading/test/unit/test_citation_gate.py	# s790 (T08 s1484)
add	application/fortune_reading/test/unit/test_rag_runtime_reading_bundle_adapter.py	# s791 (T10 s1486)
add	application/fortune_reading/test/unit/test_query_translation_adapter.py	# s792 (T11 s1487)
add	application/fortune_reading/test/unit/test_prepare_fortune_evidence_use_case.py	# s793 (T10/T11 공유 coder evidence s1237)
add	application/fortune_reading/test/unit/test_translation_outcome_policy.py	# s794 (T11 s1487)
add	application/fortune_reading/test/unit/test_rag_runtime_evidence_retrieval_adapter.py	# s795 (T12/T13 s1488~s1489)
add	application/fortune_reading/test/unit/test_retrieval_outcome_policy.py	# s796 (T13 s1489)
add	application/fortune_reading/test/unit/test_rfc8785_adapter.py	# s797 (T28 s1504)
empty	application/fortune_reading/test/integration/__init__.py	# s799: «DB-backed test 없음; concrete integration test 0»
add	application/fortune_reading/test/e2e/test_active_bundle_matrix.py	# s802 (T14/T15 s1490~s1491)
add	application/fortune_reading/test/e2e/test_crosswalk_candidate_bundle.py	# s803 (T16 s1492)
add	application/fortune_reading/test/e2e/test_open_host_services.py	# s804 (T17/T18 s1493~s1494)
add	application/fortune_reading/test/e2e/typecheck_citation_ohs_consumer.py	# s805 (T18 non-pytest proof s271/s1494)
add	application/fortune_reading/test/e2e/test_evidence_api.py	# s806 (T19 s1495)
add	application/fortune_reading/test/e2e/test_evidence_openapi.py	# s807 (T20 s1496)
add	application/fortune_reading/test/e2e/test_evidence_provider_boundaries.py	# s808 (T21 s1497)
add	application/fortune_reading/test/e2e/test_evidence_bundle.py	# s809 (T22 s1498)
empty	application/fortune_reading/test/factories/__init__.py	# s811: «factory_boy class가 생길 때만 concrete module 허용»
add	application/fortune_reading/test/fake/fake_query_translation_port.py	# s814
add	application/fortune_reading/test/fake/fake_reading_bundle_port.py	# s815
add	application/fortune_reading/test/fake/fake_evidence_retrieval_port.py	# s816
# ── BC 트리 밖 framework owner
add	framework/pydantic/cited_answer_schema.py	# s819; §6.3 s1283~s1284
# ── §6.3 «실제 mutation inventory» (s1280) — 2d44743과 동일 목록, 행 번호만 이동
update	spring_dream_server/settings/base.py	# s1285~s1286
update	spring_dream_server/urls.py	# s1287~s1289
add	framework/technology/rag/runtime/service_runtime.py	# s1290~s1291: «신규 common consumption module…»
update	framework/technology/rag/runtime/ontology_service.py	# s1292~s1293
update	framework/technology/rag/runtime/ontology_c11.py	# s1294~s1295
update	framework/technology/rag/runtime/rag_builder/_contracts.py	# s1296~s1297 (add/update 문면 불명 — 자백)
update	framework/technology/rag/runtime/rag_builder/index.py	# s1298
update	framework/technology/rag/runtime/rag_builder/steps/__init__.py	# s1299
remove	framework/technology/rag/runtime/root_migration.py	# s1300: «# 후행 delete»
update	framework/technology/rag/runtime/views.py	# s1301; L3 «다른 live view가 있으면 파일은 유지»
remove	framework/technology/rag/runtime/yeonhae_retrieval.py	# s1302: «L3 ref 0 후 delete»
remove	framework/technology/rag/runtime/hybrid_retrieval.py	# s1303: «후행 ref 0 후 delete»
update	framework/technology/rag/runtime/yeonhae_authorized.py	# s1304: «stage 6·7 함수/lazy imports만 후행 delete»
update	tests/test_yeonhae_rag.py	# s1305: «L3 6 cases delete(L01~L06)» — 파일 삭제 여부 문면 부재
update	tests/test_yeonhae_retrieval.py	# s1306: «L3 4 cases delete(L07~L10)» — 동상
update	tests/test_hybrid_retrieval.py	# s1307 — «파일과 7 old tests» 긴장 동일(자백)
update	tests/test_yeonhae_authorized.py	# s1308~s1309
update	fabfile.py	# s1310: «L3 legacy env 3건 delete»
# ── §6.2 P1 WIP reconciliation 16행 (s833, s854) — 2d44743과 동일, 행 번호 이동
update	application/fortune_reading/domain_layer/shared_value_object/allowed_evidence.py	# s837: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/calculation_projection.py	# s838: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/evidence_bundle.py	# s839: retain-and-trim
remove	application/fortune_reading/domain_layer/shared_value_object/outcome.py	# s840: split-and-delete
update	application/fortune_reading/domain_layer/shared_value_object/pinned_reading_bundle.py	# s841: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/reading_request.py	# s842: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/retrieval_plan.py	# s843: retain-and-trim
remove	application/fortune_reading/domain_layer/domain_service/citation_gate.py	# s844: move-and-delete
remove	application/fortune_reading/domain_layer/domain_service/evidence_assembly_service.py	# s845: move-and-delete
remove	application/fortune_reading/domain_layer/domain_service/reading_request_policy_service.py	# s846: move-and-delete
remove	application/fortune_reading/domain_layer/domain_service/retrieval_planning_service.py	# s847: move-and-delete
remove	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/allowed_evidence.py	# s848: move-and-delete
remove	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/cited_answer.py	# s849: move-and-delete
remove	application/fortune_reading/test/factories/fortune_calculation_output_factory.py	# s850: delete
remove	application/fortune_reading/test/integration/test_calculation_output_contract.py	# s851: move-and-delete
remove	application/fortune_reading/test/integration/test_evidence_schema_equivalence.py	# s852: move-and-delete
# ── «G1 P2/P3/P4 WIP coder reconciliation의 exact mutation inventory» 26행 (s1239~s1268) — 이 판 신설
#     8행은 current/planned input artifact의 delete/terminal-0, 18행은 이미 계획된 파일의 terminal 계약 명시(update 태그·자백 5)
remove	application/fortune_reading/application_layer/port/reading_bundle/reading_bundle_in.py	# s1243: «delete; caller ref는 domain create만 소비하고 no-arg pin»
update	application/fortune_reading/application_layer/port/reading_bundle/reading_bundle_port.py	# s1244: «direct ABC/@abstractmethod, pin(self) -> PinnedReadingBundleOut, body ...»
update	application/fortune_reading/driven_layer/adapter/reading_bundle/rag_runtime_adapter.py	# s1245: «no-arg pin, catch-all 0, exact (TypeError, ValueError) normalization»
remove	application/fortune_reading/application_layer/port/query_translation/translate_query_in.py	# s1246: «delete; primitive keyword port signature로 대체»
update	application/fortune_reading/application_layer/port/query_translation/query_translation_port.py	# s1247: «six primitive keyword args»
remove	application/fortune_reading/application_layer/port/query_translation/invalid_translation_request.py	# s1248: «delete»
remove	application/fortune_reading/application_layer/port/query_translation/translation_contract_mismatch.py	# s1249: «delete»
update	application/fortune_reading/application_layer/port/query_translation/exception.py	# s1250: «InvalidTranslationRequest + TranslationContractMismatch 단일 owner»
update	application/fortune_reading/driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py	# s1251: «published base import, exact three-handler ordering»
remove	application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_request_in.py	# s1252: «terminal delete/0; eight primitive-keyword retrieve로 대체»
update	application/fortune_reading/application_layer/port/evidence_retrieval/evidence_retrieval_port.py	# s1253: «exact eight primitive-keyword args»
update	application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_result_out.py	# s1254: «primitive-only output 유지»
update	application/fortune_reading/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py	# s1255: «request-level fold 0»
remove	application/fortune_reading/application_layer/port/evidence_digest/evidence_digest_in.py	# s1256: «terminal delete/0»
remove	application/fortune_reading/application_layer/port/evidence_digest/evidence_source_in.py	# s1257: «terminal delete/0»
remove	application/fortune_reading/application_layer/port/evidence_digest/source_location_in.py	# s1258: «terminal delete/0»
update	application/fortune_reading/application_layer/port/evidence_digest/evidence_digest_port.py	# s1259: «module-private primitive tuple aliases, exact primitive digest_item/digest_set»
update	application/fortune_reading/driven_layer/adapter/evidence_digest/rfc8785_adapter.py	# s1260: «exact CAS object reconstruction/optional-key omission»
update	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case.py	# s1261: «no-arg pin + primitive translate/retrieve/digest calls»
update	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_use_case.py	# s1262: «primitive digest keywords로 전달; input class construction 0»
update	application/fortune_reading/test/unit/test_rag_runtime_reading_bundle_adapter.py	# s1263
update	application/fortune_reading/test/unit/test_query_translation_adapter.py	# s1264: «타 BC static import 0, dynamic published fixture»
update	application/fortune_reading/test/unit/test_prepare_fortune_evidence_use_case.py	# s1265
update	application/fortune_reading/test/unit/test_rag_runtime_evidence_retrieval_adapter.py	# s1266
update	application/fortune_reading/test/unit/test_rfc8785_adapter.py	# s1267
update	application/fortune_reading/test/e2e/test_evidence_bundle.py	# s1268
```

---

## 블록 2 — symbols

경로 접두 `AFR = application/fortune_reading`. 2d44743판과의 차이 중심으로 전건 기재.
파일↔심볼 결합은 대부분 문면 명시(§6.2 s823~s831, §10 s1878, G1 exact 계약 s858~s1235).

### OHS driving (published-language)

- `AFR/…/evidence_provisioning_service.py::prepare_fortune_evidence_command(request: PrepareFortuneEvidenceRequest) -> PrepareFortuneEvidenceResponse` — s258.
- `AFR/…/citation_validation_service.py::validate_citations_command(request: ValidateCitationsRequest) -> ValidateCitationsResponse` — s258.
- `AFR/…/citation_validation_service.py::get_cited_answer_schema_query() -> GetCitedAnswerSchemaResponse[CitedAnswerSchema]` — s258.
- (private) `citation_validation_service.py::_CitationSchemaInvalid` — s823, s1878.
- `AFR/…/request/prepare_fortune_evidence_request.py::PrepareFortuneEvidenceRequest` `{question: str, query_language: str, fortune_ref: str, requested_bundle_ref: str | None, work_rag_refs: tuple[WorkRagRef, ...], character: ReadingCharacter, calculation_output: Mapping[str, JSONValue] | None, previous_allowed_evidence: tuple[AllowedEvidence, ...]}` — s153, 필드 표 s157~s164(행 번호 ±1 표 내), 파일 s613+s823.
- `AFR/…/response/prepare_fortune_evidence_response.py::PrepareFortuneEvidenceResponse` — 3-variant s217; variants exact fields s221~s223; 파일 s616+s823.
- `AFR/…/request/validate_citations_request.py::ValidateCitationsRequest` `{bundle_id: str, evidence_set_digest: str, allowed_evidence: tuple[Mapping[str, object], ...], cited_answer: Mapping[str, object]}` — s325; 파일 s628.
- `AFR/…/response/validate_citations_response.py::ValidateCitationsResponse: TypeAlias` — private dataclass 2개 union(valid/blocked + private `_CitationTrace`) — s327~s333; 파일 s631.
- `AFR/…/response/get_cited_answer_schema_response.py::GetCitedAnswerSchemaResponse[T]` `{output_type: type[T]}` — s260; 파일 s632.

### framework owner

- `framework/pydantic/cited_answer_schema.py::CitedAnswerSchema` — s360; underscore-private `_SourceLocationSchema`/`_EvidenceSourceSchema`/`_AllowedEvidenceSchema`/`_NonEmptyString`, exact `_MISSING` sentinel import — s362; CAS 필드 s364~s367.

### domain_layer (파일 매핑 s824~s826 문면; §2.2 필드 성문)

- s824: `pillar_view.py::PillarView` … `calculation_projection.py::CalculationProjection`, `calculation_output_contract_mismatch.py::CalculationOutputContractMismatch` — 각 동명 파일; nested exact fields §3.3 표 s231~s246.
- s825: `invalid_reading_request.py::InvalidReadingRequest`, `book_usage_policy.py::BookUsagePolicy`, `work_rag_ref.py::WorkRagRef`, `reading_character.py::ReadingCharacter`, `reading_request.py::ReadingRequest`, `retrieval_contract_ref.py::RetrievalContractRef`, `rag_release_ref.py::RagReleaseRef`(`language: str` — s884), `available_retrieval_entry.py::AvailableRetrievalEntry`, `reading_constraints.py::ReadingConstraints{calculation_required_fortune_refs: frozenset[str]}`(s887~s889), `pinned_reading_bundle.py::PinnedReadingBundle{bundle_id, constraints, rag_release_refs, glossary_refs, available_entries}` + `create(cls, *, bundle_id, requested_bundle_ref, rag_release_refs, glossary_refs, integration_scope_refs: ReadingConstraints, available_entries)`(s892~s910), `retrieval_target.py::RetrievalTarget`(`target_language: str` — s884), `retrieval_plan.py::RetrievalPlan`, `bundle_selection_mismatch.py::BundleSelectionMismatch`; outcome VO 7종(`translation_term_set.py::TranslationTermSet` 등 동명 파일).
- **`abstained.py::Abstained`** `{reason: AbstentionReason, bundle_id: str, release_reservation: Literal[True], translation_traces: tuple[TranslationCallTrace, ...], retrieval_traces: tuple[RetrievalTargetTrace, ...]}` — exact dataclass s116~s124 (이 판 신설 5-field trace carrier; 외부 wire 불변 s227).
- closed-state enum 3파일 (s825, s126~s128): `translation_disposition_kind.py::TranslationDispositionKind(StrEnum)`{TRANSLATED, NO_EVIDENCE}, `retrieval_target_state.py::RetrievalTargetState(StrEnum)`{HEALTHY, DEGRADED, FAILED}, `retrieval_disposition_kind.py::RetrievalDispositionKind(StrEnum)`{EVIDENCE_AVAILABLE, NO_EVIDENCE, TEMPORARY_FAILURE}.
- s826: `source_location.py::SourceLocation` … `citation_validation.py::CitationValidation` (19심볼 각 동명 파일; `EvidenceSet`/`EvidenceGrouping`/`DigestedAllowedEvidence`/`RetrievedEvidence` 필드는 s129~s131).
- stateless rules (s827): `validate_calculation_output.py::CalculationOutputContract`, `apply_reading_request_policy.py::ReadingRequestPolicyService`(두 메서드 s110), `plan_retrieval.py::RetrievalPlanningService`, `classify_translation_outcome.py::TranslationOutcomePolicy`(`classify` s126), `fold_retrieval_outcome.py::RetrievalOutcomePolicy`(`fold` s128), `assemble_evidence.py::EvidenceAssemblyService`(`select_evidence` s132·`assemble` s133), `validate_citations.py::CitationGate`(`validate(...) -> CitationValidation` s381).

### application_layer — port·operation (G1 exact Python contract s858~s1235)

- `AFR/application_layer/port/reading_bundle/pinned_reading_bundle_out.py::PinnedReadingBundleOut` `{bundle_id: str, rag_release_refs: tuple[tuple[str, str, str], ...], glossary_refs: tuple[tuple[str, str, str], ...], calculation_required_fortune_refs: tuple[str, ...], available_entries: tuple[tuple[str, str, str, str, str, int], ...]}` — s863~s870 (원소 의미 s882).
- `…/reading_bundle/reading_bundle_port.py::ReadingBundlePort(ABC)` — **no-arg** `pin(self) -> PinnedReadingBundleOut` — s873~s880 (caller ref는 pin input 아님 s112·s913). `ReadingBundleIn` 심볼 소멸(s1243).
- `…/query_translation/translated_query_out.py::TranslatedQueryOut` — 필드 s949~s963 (2d44743과 동일 shape).
- `…/query_translation/query_translation_port.py::QueryTranslationPort(ABC)` — `translate(self, *, question: str, query_language: str, target_language: str, glossary_id: str, glossary_version: str, glossary_digest: str) -> TranslatedQueryOut` (six primitive keywords; `TranslateQueryIn` 소멸) — s966~s981.
- `…/query_translation/exception.py::InvalidTranslationRequest(ValueError)` + `::TranslationContractMismatch(RuntimeError)` — **한 파일 공동 소유** — s1030~s1040 (#216).
- `…/evidence_retrieval/retrieval_result_out.py::RetrievalResultOut` `{state: Literal["healthy","degraded","failed"], hits: tuple[…6-원소 tuple…], successful_channels/failed_channels: tuple[Literal["lexical","vector"], ...], failure_reason: Literal["temporary_error"] | None}` — s1045~s1073; hit exact order `(evidence_id, exact_quote, release_id, source_url, source_locations, source_evidence_id)` s1096.
- `…/evidence_retrieval/evidence_retrieval_port.py::EvidenceRetrievalPort(ABC)` — `retrieve(self, *, work_id, rag_id, release_id, target_language, retrieval_contract_id, retrieval_contract_version, retrieval_contract_digest: str, query_terms: tuple[str, ...]) -> RetrievalResultOut` (eight primitive keywords) — s1076~s1093 (이 판에서 최초 성문).
- `…/evidence_digest/evidence_digest_port.py::EvidenceDigestPort(ABC)` — `digest_item(self, *, evidence_id: str, exact_quote: str, release_id: str, source_url: str, source_locations: tuple[_SourceLocationValue, ...]) -> str`; `digest_set(self, *, items: tuple[_EvidenceItemValue, ...]) -> str`; module-private `_SourceLocationValue`/`_EvidenceItemValue` TypeAlias — s1103~s1146. `EvidenceDigestIn`/`EvidenceSourceIn`/`SourceLocationIn` 심볼 소멸(s136, s1256~s1258).
- `…/prepare_fortune_evidence/prepare_fortune_evidence_command.py::PrepareFortuneEvidenceCommand` `{request: ReadingRequest}` — s1153~s1156.
- `…/prepare_fortune_evidence_result.py::PrepareFortuneEvidenceResult` `{provision: EvidenceBundle | Abstained}` — s1159~s1162.
- `…/prepare_fortune_evidence_use_case.py::PrepareFortuneEvidenceUseCase` — P2 constructor `(reading_bundle_port, query_translation_port, continue_translated_retrieval)` + private `_ContinueTranslatedRetrieval(Protocol)` s1165~s1206; **P3 terminal constructor** `(reading_bundle_port, query_translation_port, evidence_retrieval_port, evidence_digest_port)` s1218~s1231; execute 순서 s1213.
- `…/validate_citations/validate_citations_use_case.py::ValidateCitationsUseCase` — `EvidenceDigestPort` 하나만 주입 — s1235.

### driven_layer — adapters (pairing s828: 4 port ↔ 4 adapter 문면)

- `AFR/driven_layer/adapter/reading_bundle/rag_runtime_adapter.py::RagRuntimeReadingBundleAdapter(ReadingBundlePort)` — `__init__(*, repository_root: Path, data_root: Path, load_json_object, validate_terminal_active_service_bundle)`; **no-arg** `pin(self) -> PinnedReadingBundleOut`; private `_JsonObjectLoader`/`_TerminalActiveBundleValidator` — s915~s943; 번역 shape `except ReadingBundleContractMismatch: raise` + `except (TypeError, ValueError)` — s946 (#129).
- `AFR/driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py::QueryTranslationAdapter(QueryTranslationPort)` — `__init__(*, translate_command: _TranslateCommand)`; six-keyword `translate`; exact 3-handler catch ordering(invalid concrete → six concrete tuple → `TranslationPublishedError` base) — s986~s1028 (#473).
- `AFR/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py::RagRuntimeEvidenceRetrievalAdapter` — 유일 mismatch owner — s340; s828.
- `AFR/driven_layer/adapter/evidence_digest/rfc8785_adapter.py::Rfc8785EvidenceDigestAdapter` — primitive tuple→exact CAS object 복원 + `rfc8785.dumps`/`hashlib.sha256` — s136, s1146; s828.
- `AFR/driven_layer/django_fortune_reading/apps.py::FortuneReadingConfig` `{default_auto_field/name/label: str}` + docstring `"""fortune_reading Django 애플리케이션 설정."""` — s1274.

### API·기타

- `AFR/driving_layer/api/bc_error_schema.py::FortuneReadingErrorCode(StrEnum)` — s502~s507; s495 «단독 소유». `::FortuneReadingErrorSchema(FrameworkErrorSchema)` + concrete 4종 — s516~s533.
- `AFR/driving_layer/api/evidence/schema/schema_in.py::PrepareFortuneEvidenceRequestSchema` — 심볼 s153; 파일 s600 (재량 결합).
- `AFR/driving_layer/api/evidence/schema/schema_out.py::EvidenceProvisionResponseSchema` — 심볼 s217; 파일 s601+s830 (재량).
- `AFR/test/e2e/typecheck_citation_ohs_consumer.py::validate_generated_citations(...)` — exact source s273~s321 (함수 s298).
- `framework/technology/rag/runtime/rag_builder/_contracts.py::Embedder` — s1296~s1297.
- `framework/technology/rag/runtime/views.py::yeonhae_japyeong_evidence` — L3 제거 대상 (①과 동일 절; §9 L3).
- 파일 미명시: `register_fortune_reading_api(api)` (s455), `CACHE_CONTROL_HEADER: dict[str, object]` 상수(s558).

---

## 블록 3 — boundary-imports

| 소비 파일 | import 대상 모듈 | provenance |
|---|---|---|
| `AFR/driving_layer/api/bc_error_schema.py` | `framework/ninja/framework_error_schema.py` | §5.5 reuse — s488 «공통 class를 import하고», , s516 상속 |
| `spring_dream_server/urls.py` | fortune_reading registrar 모듈(경로 미명시; `register_fortune_reading_api(api)`) | s1288, s455 |
| `AFR/…/citation_validation_service.py` | `framework/pydantic/cited_answer_schema.py::CitedAnswerSchema` | s260, s325 |
| `AFR/test/e2e/typecheck_citation_ohs_consumer.py` | fortune_reading OHS 3모듈 + **타 BC** `application.llm_access…` 3모듈 — exact 7 `ImportFrom`/9 names | s262~s269, 코드 s276~s295 |
| `AFR/driven_layer/…/query_translation_adapter.py` | 타 BC query_translation published OHS: `TranslateRequest`/`TranslateResponse`/`GlossaryReferenceData` + **`TranslationPublishedError`와 일곱 concrete published exception static import** | s1008 «ACL은 …을 static import하되», s1011~s1025, s76 |
| `AFR/test/unit/test_query_translation_adapter.py` | own BC adapter/output/`exception.py`만 static import; published request/response/base/seven concrete은 `importlib.import_module(<literal string>)` runtime fixture (static `application.query_translation` import 0) | s77, s831, s1237, s1487 (#13/#385) |
| composition root(파일 미명시) | `ontology_canonical.load_json_object` · `ontology_service.validate_terminal_active_service_bundle` 명시 주입 | s946 |
| composition root(파일 미명시) | 타 BC `query_translation...translation_service.translate_command` 명시 주입 | s1008 |
| `framework/technology/rag/runtime/ontology_c11.py` | `service_runtime.py` | s1295 |
| `framework/technology/rag/runtime/ontology_service.py` | `service_runtime.py` (L2 전환) | §9 L2(①과 동일 문면) |
| `ontology_c11.py` · `rag_builder/index.py` · `rag_builder/steps/__init__.py` | `rag_builder/_contracts.py` (`Embedder`) | §9 L1 step 1(①과 동일 문면), s1296 |
| `AFR/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py` | common `search_hybrid_index` (모듈 미명시) | s1798 |
| P3 산출물(소비 파일 미명시) | `rag_builder.index` re-export `Embedder` | s1799 |

참고(범주 밖 성문 서드파티): framework owner→pydantic underscore aliases + `_MISSING` exact import (s362); `rfc8785_adapter.py`→`rfc8785`/`hashlib` (s136, s1146); `evidence_digest_port.py`→`from typing import TypeAlias as _TypeAlias` (s1105 — port 파일의 typing alias import 성문).

```text
# 금지 명시(참고)
- domain outward/rfc8785/framework/application import 0                       # s136, s860
- G1 전 슬라이스 port `<data>_in.py` 0 · application_layer 전체 `<data>_in` import/construction 0 (#574)  # s860, s1270, s1322
- contract/ Pydantic import·re-export 0 · OHS→API sibling 0 · composition-root→driving 0  # s360, s830, s325
- fortune_reading test의 static `application.query_translation` import 0 (#13/#385)      # s1322, s77
- reading adapter catch-all(`Exception`/`BaseException`/bare) 0 — exact `(TypeError, ValueError)`만 (#129)  # s946, s78
- `ontology_c11.py` private function import 금지                              # s341
- BC-module-origin `StrEnum` consumer import/re-export/`__all__` 0            # s74, s825
- fortune_catalog/fortune_character private import 0 · LLM/SPARQL/개별 active.json 0  # s144, s1868(V), s1910
- framework가 application BC 역-import 0                                      # §9 L2
- `hybrid_retrieval` 직접 참조 신규 증가 0                                     # s1799
```

---

## 블록 4 — physical-signals

add 23행(T01~T22, T28)·update 0 (s1738~s1740; §8 전제 «DB lens 비활성… DB 신호를 가장한
marker/fixture를 추가하지 않는다» s1471). 새 테스트의 DB 마커·베이스 클래스·client 문면 전무 → 전건 «부재».

| row | 테스트 경로 | markers | base | client | provenance |
|---|---|---|---|---|---|
| T01 | `AFR/test/unit/test_calculation_output_contract.py` | 부재 («DB 신호 0» 명시) | 부재 | 부재 | s1477 |
| T02 | `AFR/test/unit/test_reading_request.py`, `test_reading_request_policy_service.py` | 부재 | 부재 | 부재 | s1478 |
| T03 | `AFR/test/unit/test_retrieval_planning_service.py` | 부재 | 부재 | 부재 | s1479 |
| T04 | `AFR/test/unit/test_retrieval_planning_service.py` (exact `Abstained` 5-field value equality fixture 갱신) | 부재 | 부재 | 부재 | s1480 |
| T05 | `AFR/test/unit/test_evidence_assembly_service.py` | 부재 | 부재 | 부재 | s1481 |
| T06 | `AFR/test/unit/test_allowed_evidence.py` | 부재 | 부재 | 부재 | s1482 |
| T07 | `AFR/test/unit/test_evidence_assembly_service.py` | 부재 | 부재 | 부재 | s1483 |
| T08 | `AFR/test/unit/test_citation_gate.py` | 부재 | 부재 | 부재 | s1484 |
| T09 | `AFR/test/unit/test_cited_answer_schema_equivalence.py` | 부재 («DB 신호 0» 명시) | 부재 | 부재 | s1485 |
| T10 | `AFR/test/unit/test_rag_runtime_reading_bundle_adapter.py` + `test_prepare_fortune_evidence_use_case.py` | 부재 («DB 신호 0» 명시) | 부재 | 부재 | s1486 |
| T11 | `AFR/test/unit/test_query_translation_adapter.py` + `test_prepare_fortune_evidence_use_case.py` + `test_translation_outcome_policy.py` | 부재 | 부재 | 부재 | s1487 |
| T12 | `AFR/test/unit/test_rag_runtime_evidence_retrieval_adapter.py` | 부재 | 부재 | 부재 | s1488 |
| T13 | `AFR/test/unit/test_rag_runtime_evidence_retrieval_adapter.py` + `test_retrieval_outcome_policy.py` (+ 기존 `test_prepare_fortune_evidence_use_case.py` P3 전환) | 부재 | 부재 | 부재 | s1489 |
| T14 | `AFR/test/e2e/test_active_bundle_matrix.py` | 부재 | 부재 | 부재 | s1490 |
| T15 | `AFR/test/e2e/test_active_bundle_matrix.py` | 부재 | 부재 | 부재 | s1491 |
| T16 | `AFR/test/e2e/test_crosswalk_candidate_bundle.py` | 부재 | 부재 | 부재 | s1492 |
| T17 | `AFR/test/e2e/test_open_host_services.py` | 부재 | 부재 | 부재 | s1493 |
| T18 | `AFR/test/e2e/test_open_host_services.py` + non-pytest `typecheck_citation_ohs_consumer.py` | 부재 | 부재 | 부재 | s1494 |
| T19 | `AFR/test/e2e/test_evidence_api.py` | 부재 | 부재 | 부재 | s1495 |
| T20 | `AFR/test/e2e/test_evidence_openapi.py` | 부재 | 부재 | 부재 | s1496 |
| T21 | `AFR/test/e2e/test_evidence_provider_boundaries.py` | 부재 | 부재 | 부재 | s1497 |
| T22 | `AFR/test/e2e/test_evidence_bundle.py` | 부재 | 부재 | 부재 | s1498 |
| T28 | `AFR/test/unit/test_rfc8785_adapter.py` | 부재 | 부재 | 부재 | s1504 |

---

## 블록 5 — exception-map

### 5a. 정의·소유 파일 (s1878 — 전건 문면; 2d44743 대비 query_translation 2예외가 exception.py 단일 소유로 반전)

| published 예외 | raise 창구(파일) — 소유 경로 | provenance |
|---|---|---|
| `InvalidReadingRequest` | `AFR/domain_layer/shared_value_object/invalid_reading_request.py` | s1878 |
| `CalculationOutputContractMismatch` | `AFR/domain_layer/shared_value_object/calculation_output_contract_mismatch.py` | s1878 |
| `BundleSelectionMismatch` | `AFR/domain_layer/shared_value_object/bundle_selection_mismatch.py` | s1878 |
| `EvidenceDigestConflict` | `AFR/domain_layer/shared_value_object/evidence_digest_conflict.py` | s1878 |
| `InvalidCitation` | `AFR/domain_layer/shared_value_object/invalid_citation.py` | s1878 |
| `ReadingBundleContractMismatch` | `AFR/application_layer/port/reading_bundle/exception.py` | s1878 |
| `InvalidTranslationRequest` | `AFR/application_layer/port/query_translation/exception.py` (**공동 소유**; «split owner/re-export shim은 0») | s1878, s1030~s1040 (#216) |
| `TranslationContractMismatch` | `AFR/application_layer/port/query_translation/exception.py` | s1878, s1036 |
| `RetrievalContractMismatch` / `RetrievalTemporaryFailure` / `RetrievalResourceLimit` | `AFR/application_layer/port/evidence_retrieval/exception.py` | s1878 |
| digest adapter normalization failure (예외 심볼명 문면 부재) | `AFR/application_layer/port/evidence_digest/exception.py` | s1878 |
| (private) `_CitationSchemaInvalid` | `AFR/driving_layer/…/citation_validation_service.py` | s1878 |

### 5b. raise 주체 (§10 표 s1880~s1904 + §5.10 s541~s545)

| published 예외/결과 | raise 주체(문면) | provenance |
|---|---|---|
| `InvalidReadingRequest` | `ReadingRequest`; `ReadingRequestPolicyService.validate_calculation_requirement`; `.validate_question_limit` | s1882~s1884 |
| `CalculationOutputContractMismatch` | `CalculationOutputContract`(fortune 분류 전) | s1885 |
| `BundleSelectionMismatch` | `PinnedReadingBundle.create` domain invariant (adapter는 caller ref를 받지도 않음 — no-arg pin) | s1886, s913 |
| `ReadingBundleContractMismatch` | `RagRuntimeReadingBundleAdapter` — «`OntologyArtifactError`/`ServiceActivationError`와 own shape failure를 exact `(TypeError, ValueError)`로만 translate, catch-all 0» | s1887, s946, s78 |
| `InvalidTranslationRequest` | `QueryTranslationAdapter` — upstream `InvalidTranslationRequestException` 번역(첫 handler) | s1890, s1013~s1014 |
| `TranslationContractMismatch` | `QueryTranslationAdapter` — six concrete tuple + unknown/new `TranslationPublishedError` final catch + malformed response 직접 raise | s1890, s1015~s1028 |
| `RetrievalContractMismatch` | `RagRuntimeEvidenceRetrievalAdapter` external-contract owner | s1891, s1897 |
| `RetrievalTemporaryFailure` | domain `RetrievalOutcomePolicy.fold`→`TEMPORARY_FAILURE`; application만 exception 조율 | s1896 |
| `RetrievalResourceLimit` | retrieval adapter (explicit memory/capacity) | s1898, s345 |
| `EvidenceDigestConflict` | domain `EvidenceAssemblyService.select_evidence`; existing `registry_contract_mismatch` 503/Blocked 번역 | s1901, s132, s543 |
| `InvalidCitation` | domain `CitationGate.validate` → OHS `Blocked(invalid_citation)` | s1903, s382 |
| `_CitationSchemaInvalid` (private) | citation OHS (counters `0/0/0/()`) → 같은 `Blocked(invalid_citation)` | s1902 |
| `Abstained(insufficient_evidence)` | **future-only**: «별도 승인된 fixed retrieval/evaluation contract가 제공할 때 application이 재판정 없이 전달; current P2/P3 producer·assembler 판정 0 … 현재 branch/fixture 0» | s1900 |
| unexpected programming exception | framework 500 | s1904 |

HTTP mapping(§5.10): 400 tuple s542; 503 registry tuple(EvidenceDigestConflict 포함) s543; temporary/resource s544~s545(①과 동일 문면·행 이동).

---

## 충돌·긴장 기록 (②)

- 양립 불가 충돌: **0건.** ①에 있던 «P2 focused review pending» 충돌(①s11↔①s1860대)은 이 판에서 s11·B7(s1984)·handoff(s2092)가 «focused review 3종 PASS / coder terminal registry proof PENDING»으로 정합화되어 해소됨.
- 긴장 1 — §9 P1 preamble s1751 «…API 재리뷰는 불필요하다» vs handoff s2087 «API focused re-review … PASS» / s2078: P1 시점 서술의 잔존과 whole-G1 재리뷰 수행 기록이 병존. `# 긴장: s1751행 vs s2087행` — both 전사.
- 긴장 2 — B7 표제 s1979 «focused review·implementation proof pending» vs 본문 s1984 «focused review는 각각 PASS … coder proof는 PENDING»: 표제가 본문보다 넓게 읽힘.
- 긴장 3 — §6.2 트리(add) vs WIP retain-and-trim 6경로 vs G1 coder inventory update 18경로: 동일 경로 다중 서술(각 문면대로 전사).
- 긴장 4 — `tests/test_hybrid_retrieval.py` 파일 잔존 여부 문면 불명(①과 동일).
- 집계 검산: add 23/update 0/reuse 2/retain 14/remove 19/reject 2/pending 0=60 (s1738~s1745) ↔ 행 전수 일치. design disposition 23/23 = 11+2+1+1+8 (s2069) 산술 일치. WIP 16행 closed set(s854) 일치. G1 coder inventory 26행(s1243~s1268) 전수 전사.

## 재량 자백 (②)

1~4. ① 전사본의 자백 1~4와 동일 적용(`__init__.py`/고정 slot 제외·empty 태그 해석·§6.3 태그 부여·legacy 테스트 3파일 update).
5. **G1 coder mutation inventory(26행)의 태그 매핑** — «delete»/«terminal delete/0» → remove(8행), 그 외 terminal 계약 서술 → update(18행). update 18행은 §6.2 트리 add와 동일 경로의 이중 서술이라 file-plan에 add·update 양쪽 행이 공존한다(문면 그대로 전사, 통합하지 않음).
6. `port/query_translation/exception.py`: 트리 주석 «두 local port exception의 단일 owner»(s665)에 근거해 empty가 아닌 add로 판정 — 2d44743판(0-byte empty slot)과 정반대이므로 태그 반전을 명시.
7. 심볼→파일 재량 결합은 schema_in/schema_out 2건뿐(①과 동일). 나머지는 문면 명시.
8. `Abstained`는 domain VO이면서 §3.3 외부 wire 표(s222)에 동명 variant가 존재 — 심볼 블록에는 domain `abstained.py::Abstained`(5-field)로 전사하고 외부 wire `Abstained`(trace: ProvisionTrace)는 파일 미명시 variant로 분리(내외 구분은 s227 문면).
9. boundary-imports의 T11 행은 «static import 0 + importlib runtime load»라는 부정+동적 계약이라 통상 import 행과 다름을 부기하고 전사.
10. §5 절 다수(±22행 이동 구간)는 ①과 문면 동일함을 diff로 확인하고 ②의 행 번호로 재인용; 표 내부 개별 필드 행(§3.1 s157~s164 등)은 표 시작 행 기준 부기.
11. physical-signals «DB 신호 0» 명시 행 부기 재량(① 자백 7과 동일).
12. exception-map «digest adapter normalization failure» 심볼명 부재 전사(① 자백 8과 동일).
