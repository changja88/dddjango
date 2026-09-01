# 맹검 소급 전사 — fortune_reading G1 설계 명세 (b5392f0)

- 원본: `git show b5392f0:.dddjango/20260831-2331-fortune-reading/design-spec.md`
  → 로컬 사본 `spec-b5392f0.md` (1007행). 아래 `sNNN`은 이 사본의 행 번호다.
- 유일 근거: 위 명세 원문 + 발주 프롬프트에 성문된 형식 규범. 다른 파일은 열지 않았다.
- fail-closed: 인용(행 번호 + ≤1행 발췌) 없는 행은 쓰지 않았다. 부재는 «부재»로 남겼다.

---

## 블록 1 — file-plan

표기: `<태그><TAB><경로>  # sNNN[: 발췌]`.
§6.2 트리 행(s436~s621)의 발췌는 경로 문자열 자체와 동일하므로 행 번호만 부기하고,
트리 주석이 있는 행은 주석을 발췌로 옮겼다. §6.3 행은 원문 발췌를 부기했다.

전사 범위 판단(자백 — 보고서 참조):
- 순수 `__init__.py` 패키지 마커·표준 고정 slot(persistence `repository/…` s581~s583,
  django `models/migrations/admin/__init__.py` s563~s565)은 «표준 트리 골격 비전사» 규칙으로 제외.
  단, 명세가 «…없음» 주석으로 명시적으로 빈 슬롯임을 계획한 5행은 `empty`로 전사.
- read-only/gate-only verification inventory(s658~s668, «permanent artifact write는 0»)는
  조치 태그가 성립하지 않아 file-plan에 넣지 않음(보고서에 목록).
- 파일 계획 내부에 와일드카드·placeholder 없음. `# 미전개` 대상 0.
  (참고: `application/fortune_reading/test/**` s877, `framework/technology/rag/runtime/**` s335는
  파일 계획이 아니라 실행/스캔 범위 표기라 전개하지 않음.)

```paths
# ── §6.2 신규 BC 파일 목록 (s431 «다음이 신규 파일의 허용·계획 목록이다» → 전부 add)
add	application/fortune_reading/composition_root/dependency_wiring.py	# s440
add	application/fortune_reading/composition_root/event_wiring.py	# s441: «event 0을 명시하는 no-op registrar»
empty	application/fortune_reading/published_event/__init__.py	# s443: «published event 없음»
add	application/fortune_reading/driving_layer/api/api_router.py	# s448 (s282 «planned …api/api_router.py»)
add	application/fortune_reading/driving_layer/api/bc_error_schema.py	# s449 (s350 «단독 소유»)
add	application/fortune_reading/driving_layer/api/evidence/evidence_controller.py	# s452 (s282)
add	application/fortune_reading/driving_layer/api/evidence/schema/schema_in.py	# s455
add	application/fortune_reading/driving_layer/api/evidence/schema/schema_out.py	# s456
empty	application/fortune_reading/driving_layer/api/webhook/__init__.py	# s458: «provider 없음»
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py	# s463
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/request/prepare_fortune_evidence_request.py	# s468
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/response/prepare_fortune_evidence_response.py	# s471
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_published_error.py	# s474
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_exception.py	# s475
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/citation_validation_service.py	# s478
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/request/validate_citations_request.py	# s483
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/validate_citations_response.py	# s486
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/cited_answer.py	# s487
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/allowed_evidence.py	# s488
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/exception/citation_validation_published_error.py	# s491
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/exception/invalid_citation_exception.py	# s492
empty	application/fortune_reading/driving_layer/cron_job/__init__.py	# s494: «jobs 없음»
add	application/fortune_reading/driving_layer/event_subscription/event_router.py	# s497: «subscriptions 없음» (add/empty 경계 재량 — 보고서)
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case.py	# s504
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_command.py	# s505
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_query.py	# s506
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_result.py	# s507
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_use_case.py	# s512
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_command.py	# s513
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_query.py	# s514
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_result.py	# s515
add	application/fortune_reading/application_layer/port/query_translation/query_translation_port.py	# s520
add	application/fortune_reading/application_layer/port/query_translation/translated_query_out.py	# s521
add	application/fortune_reading/application_layer/port/query_translation/translate_query_in.py	# s522
add	application/fortune_reading/application_layer/port/query_translation/exception.py	# s523
add	application/fortune_reading/application_layer/port/reading_bundle/reading_bundle_port.py	# s526
add	application/fortune_reading/application_layer/port/reading_bundle/pinned_reading_bundle_out.py	# s527
add	application/fortune_reading/application_layer/port/reading_bundle/reading_bundle_in.py	# s528
add	application/fortune_reading/application_layer/port/reading_bundle/exception.py	# s529
add	application/fortune_reading/application_layer/port/evidence_retrieval/evidence_retrieval_port.py	# s532
add	application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_result_out.py	# s533
add	application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_request_in.py	# s534
add	application/fortune_reading/application_layer/port/evidence_retrieval/exception.py	# s535
empty	application/fortune_reading/application_layer/port/domain_bypass_query/__init__.py	# s537: «bypass query 없음»
empty	application/fortune_reading/application_layer/port/unit_of_work/__init__.py	# s539: «UoW 없음»
add	application/fortune_reading/domain_layer/shared_value_object/reading_request.py	# s544
add	application/fortune_reading/domain_layer/shared_value_object/calculation_projection.py	# s545
add	application/fortune_reading/domain_layer/shared_value_object/pinned_reading_bundle.py	# s546
add	application/fortune_reading/domain_layer/shared_value_object/bundle_selection_mismatch.py	# s547
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_plan.py	# s548
add	application/fortune_reading/domain_layer/shared_value_object/evidence_bundle.py	# s549
add	application/fortune_reading/domain_layer/shared_value_object/allowed_evidence.py	# s550
add	application/fortune_reading/domain_layer/shared_value_object/outcome.py	# s551
add	application/fortune_reading/domain_layer/domain_service/reading_request_policy_service.py	# s554
add	application/fortune_reading/domain_layer/domain_service/retrieval_planning_service.py	# s555
add	application/fortune_reading/domain_layer/domain_service/evidence_assembly_service.py	# s556
add	application/fortune_reading/domain_layer/domain_service/citation_gate.py	# s557
add	application/fortune_reading/driven_layer/django_fortune_reading/apps.py	# s562 (s623 exact class binding)
add	application/fortune_reading/driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py	# s572
add	application/fortune_reading/driven_layer/adapter/external_system/rag_runtime/trusted_bundle_adapter.py	# s577
add	application/fortune_reading/driven_layer/adapter/external_system/rag_runtime/hybrid_retrieval_adapter.py	# s578
add	application/fortune_reading/test/unit/test_reading_request.py	# s588 (s701 T02 add)
add	application/fortune_reading/test/unit/test_reading_request_policy_service.py	# s589 (s701 T02 add)
add	application/fortune_reading/test/unit/test_retrieval_planning_service.py	# s590 (s702/s703 T03·T04 add)
add	application/fortune_reading/test/unit/test_evidence_assembly_service.py	# s591 (s704/s706 T05·T07 add)
add	application/fortune_reading/test/unit/test_allowed_evidence.py	# s592 (s705 T06 add)
add	application/fortune_reading/test/unit/test_citation_gate.py	# s593 (s707 T08 add)
add	application/fortune_reading/test/integration/test_calculation_output_contract.py	# s596 (s700 T01 add)
add	application/fortune_reading/test/integration/test_evidence_schema_equivalence.py	# s597 (s708 T09 add)
add	application/fortune_reading/test/integration/test_trusted_bundle_adapter.py	# s598 (s709 T10 add)
add	application/fortune_reading/test/integration/test_query_translation_adapter.py	# s599 (s710 T11 add)
add	application/fortune_reading/test/integration/test_hybrid_retrieval_adapter.py	# s600 (s711/s712 T12·T13 add)
add	application/fortune_reading/test/integration/test_active_bundle_matrix.py	# s601 (s713/s714 T14·T15 add)
add	application/fortune_reading/test/integration/test_crosswalk_candidate_bundle.py	# s602 (s715 T16 add)
add	application/fortune_reading/test/integration/test_open_host_services.py	# s603 (s716/s717 T17·T18 add)
add	application/fortune_reading/test/e2e/test_evidence_api.py	# s606 (s718 T19 add)
add	application/fortune_reading/test/e2e/test_evidence_openapi.py	# s607 (s719 T20 add)
add	application/fortune_reading/test/e2e/test_evidence_provider_boundaries.py	# s608 (s720 T21 add)
add	application/fortune_reading/test/e2e/test_evidence_bundle.py	# s609 (s721 T22 add)
add	application/fortune_reading/test/factories/fortune_calculation_output_factory.py	# s612 (s267 «…factory.py에 … 소유한다»)
add	application/fortune_reading/test/factories/reading_request_factory.py	# s613
add	application/fortune_reading/test/factories/service_bundle_factory.py	# s614
add	application/fortune_reading/test/factories/evidence_factory.py	# s615
add	application/fortune_reading/test/fake/fake_query_translation_port.py	# s618
add	application/fortune_reading/test/fake/fake_reading_bundle_port.py	# s619
add	application/fortune_reading/test/fake/fake_evidence_retrieval_port.py	# s620
# ── §6.3 «실제 mutation inventory» (s627)
update	spring_dream_server/settings/base.py	# s630~s631: «INSTALLED_APPS에 FortuneReadingConfig 1줄»
update	spring_dream_server/urls.py	# s632~s634: «registrar import/call 2줄» + «L3에서 legacy v2 evidence path 제거»
add	framework/technology/rag/runtime/service_runtime.py	# s635~s636: «신규 common consumption module: trusted bundle/read-only retrieval load/search glue만 소유»
update	framework/technology/rag/runtime/ontology_service.py	# s637~s638: «Bundle/retrieval 제품 소비 glue를 분리하고 citation 제품 소비는 BC CitationGate로 대체»
update	framework/technology/rag/runtime/ontology_c11.py	# s639~s640: «private glue 대신 service_runtime import로 전환»
update	framework/technology/rag/runtime/rag_builder/_contracts.py	# s641~s642: «Embedder Protocol의 새 소유처» (add/update 문면 불명 — 보고서 자백)
update	framework/technology/rag/runtime/rag_builder/index.py	# s643 (s839 의존 전환)
update	framework/technology/rag/runtime/rag_builder/steps/__init__.py	# s644 (s839 의존 전환)
remove	framework/technology/rag/runtime/root_migration.py	# s645: «# 후행 delete» (s853 «삭제한다»)
update	framework/technology/rag/runtime/views.py	# s646: «L3 legacy view symbol/import delete»; s864 «다른 live view가 있으면 파일은 유지한다»
remove	framework/technology/rag/runtime/yeonhae_retrieval.py	# s647: «L3 ref 0 후 delete» (s866 «module을 삭제한다»)
remove	framework/technology/rag/runtime/hybrid_retrieval.py	# s648: «후행 ref 0 후 delete» (s840 «파일과 7 old tests를 제거한다»)
update	framework/technology/rag/runtime/yeonhae_authorized.py	# s649: «stage 6·7 함수/lazy imports만 후행 delete» (s841 «stage 3~5·8은 유지»)
update	tests/test_yeonhae_rag.py	# s650: «L3 6 cases delete(L01~L06)» — 파일 자체 삭제 여부 문면 부재(보고서)
update	tests/test_yeonhae_retrieval.py	# s651: «L3 4 cases delete(L07~L10)» — 파일 자체 삭제 여부 문면 부재(보고서)
update	tests/test_hybrid_retrieval.py	# s652 (주석 없음); s840 «파일과 7 old tests를 제거한다» — 테스트 파일 잔존 여부 문면 불명(보고서)
update	tests/test_yeonhae_authorized.py	# s653~s654: «stage6/7 cases delete; stage8 case의 fixture setup만 prebuilt output으로 변경»
update	fabfile.py	# s655: «L3 legacy env 3건 delete» (s867 env 3 이름)
```

---

## 블록 2 — symbols

형식: `경로::Symbol(Base)`; published-language 칸은 `{field: type, ...}` 병기.
세 등급으로 나눈다 — **[A] 파일↔심볼 문면 명시**, **[B] 심볼·시그니처는 문면, 파일 결합은
§6.2 트리 파일명 일치(재량)**, **[C] 파일 결합이 자리 규약 추정(약함)**. B·C는 재량 자백 대상.

### [A] 파일↔심볼 문면 명시

- `application/fortune_reading/driving_layer/api/bc_error_schema.py::FortuneReadingErrorCode(StrEnum)`
  `{INVALID_REQUEST: "fortune_reading_invalid_request", REGISTRY_CONTRACT_MISMATCH: "fortune_reading_registry_contract_mismatch", TEMPORARY_ERROR: "fortune_reading_temporary_error", RESOURCE_LIMIT: "fortune_reading_resource_limit"}`
  — s354 «planned BC는 다음 단일 enum을 소유한다», s357~s361 코드 블록; 파일 귀속은 s350 «bc_error_schema.py가 이 BC의 HTTP error code와 concrete schema를 단독 소유».
- `…/api/bc_error_schema.py::FortuneReadingErrorSchema(FrameworkErrorSchema)` `{error: FortuneReadingErrorCode}` — s371~s372.
- `…/api/bc_error_schema.py::InvalidRequestErrorSchema(FortuneReadingErrorSchema)` `{error = INVALID_REQUEST, message: str = "Fortune reading request is invalid."}` — s374~s376.
- `…/api/bc_error_schema.py::RegistryContractMismatchErrorSchema(FortuneReadingErrorSchema)` `{error = REGISTRY_CONTRACT_MISMATCH, message: str = "Fortune reading evidence contract is unavailable."}` — s378~s380.
- `…/api/bc_error_schema.py::TemporaryErrorSchema(FortuneReadingErrorSchema)` `{error = TEMPORARY_ERROR, message: str = "Fortune reading evidence is temporarily unavailable."}` — s382~s384.
- `…/api/bc_error_schema.py::ResourceLimitErrorSchema(FortuneReadingErrorSchema)` `{error = RESOURCE_LIMIT, message: str = "Fortune reading evidence resource limit was exceeded."}` — s386~s388.
- `application/fortune_reading/domain_layer/shared_value_object/reading_request.py::InvalidReadingRequest` — s889 «`InvalidReadingRequest`는 `domain_layer/shared_value_object/reading_request.py`».
- `…/shared_value_object/calculation_projection.py::CalculationOutputContractMismatch` — s889.
- `…/shared_value_object/bundle_selection_mismatch.py::BundleSelectionMismatch` — s889.
- `…/domain_service/citation_gate.py::InvalidCitation` — s889 «`InvalidCitation`은 `domain_layer/domain_service/citation_gate.py`».
- `application/fortune_reading/application_layer/port/reading_bundle/exception.py::ReadingBundleContractMismatch` — s889 «…에는 adapter contract failure인 `ReadingBundleContractMismatch`만 둔다».
- `application/fortune_reading/application_layer/port/query_translation/exception.py::InvalidTranslationRequest` — s889.
- `application/fortune_reading/application_layer/port/query_translation/exception.py::TranslationContractMismatch` — s889.
- `application/fortune_reading/application_layer/port/evidence_retrieval/exception.py::RetrievalContractMismatch` — s889.
- `application/fortune_reading/application_layer/port/evidence_retrieval/exception.py::RetrievalTemporaryFailure` — s889.
- `application/fortune_reading/application_layer/port/evidence_retrieval/exception.py::RetrievalResourceLimit` — s889.
- `application/fortune_reading/driven_layer/django_fortune_reading/apps.py::FortuneReadingConfig`
  `{default_auto_field: str = "django.db.models.BigAutoField", name: str = "application.fortune_reading.driven_layer.django_fortune_reading", label: str = "fortune_reading"}`
  — s623 «apps.py의 exact class binding…», 클래스명은 s631 «INSTALLED_APPS에 FortuneReadingConfig 1줄». Base 문면 부재(괄호 생략).
- `framework/technology/rag/runtime/rag_builder/_contracts.py::Embedder` — s642 «Embedder Protocol의 새 소유처», s839 «`Embedder` Protocol을 `rag_builder/_contracts.py`로 이동». (Protocol은 base 아닌 종류 서술 — 괄호 생략.)
- `framework/technology/rag/runtime/views.py::yeonhae_japyeong_evidence` — s864 «`yeonhae_japyeong_evidence` symbol과 전용 imports만 제거한다» **[L3 제거 대상 심볼]**.

### [B] 심볼은 문면·파일 결합은 §6.2 파일명 일치(재량)

- `…driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py::EvidenceProvisioningService`
  — method `prepare(request: PrepareFortuneEvidenceRequest) -> PrepareFortuneEvidenceResponse` s202; 파일 s463.
- `…/open_host_service/citation_validation/citation_validation_service.py::CitationValidationService`
  — method `validate(...) -> ValidateCitationsResponse` s202; 파일 s478.
- `…/evidence_provisioning/contract/request/prepare_fortune_evidence_request.py::PrepareFortuneEvidenceRequest` (published-language)
  `{question: str, query_language: str, fortune_ref: str, requested_bundle_ref: str | None, work_rag_refs: tuple[WorkRagRef, ...], character: ReadingCharacter, calculation_output: Mapping[str, JSONValue] | None, previous_allowed_evidence: tuple[AllowedEvidence, ...]}`
  — s108 «공개 HTTP …와 OHS `PrepareFortuneEvidenceRequest`는 다음 field set을 공유한다», 필드 s112~s119; «frozen·slots·kw-only dataclass와 tuple» s108; 파일 s468.
- `…/evidence_provisioning/contract/response/prepare_fortune_evidence_response.py::PrepareFortuneEvidenceResponse` (published-language)
  — three-variant `EvidencePrepared | Abstained | EvidenceProvisionBlocked` s163·s202; 파일 s471. (변형 3종의 필드는 아래 [미명시] 목록에 병기 — 변형의 소속 파일 문면 부재.)
- `…/citation_validation/contract/request/validate_citations_request.py::ValidateCitationsRequest` (published-language)
  `{bundle_id: str, evidence_set_digest: str, allowed_evidence: tuple[AllowedEvidence, ...], cited_answer: CitedAnswer}` — s202 «네 required/non-null field의 closed dataclass»; 파일 s483.
- `…/citation_validation/contract/response/validate_citations_response.py::ValidateCitationsResponse` (published-language)
  — closed union `CitationsValid | CitationBlocked` s202; 파일 s486.
- `…/citation_validation/contract/response/cited_answer.py::CitedAnswer` (published-language)
  `{answer: str (non-empty), citations: tuple[AllowedEvidence, ...] (minItems=1)}` — s202·s236; 파일 s487.
- `…/citation_validation/contract/response/allowed_evidence.py::AllowedEvidence` (published-language, Pydantic)
  `{evidence_id, exact_quote, release_id, source: {source_url, source_locations: [{location_id, provider, provider_book_id, provider_chapter_id, provider_paragraph_id, page_nums?: tuple[int, ...], source_url?: str}] (minItems=1)}}`
  — s229 «`AllowedEvidence` Pydantic contract는 CAS 1.1.0과 exact 동치», 필드 s231~s234; 파일 s488. (top-level 4필드 외 타입 표기는 문면 부재.)
- `…domain_layer/shared_value_object/reading_request.py::ReadingRequest` — s85 «`ReadingRequest` constructor: …domain strict value로 만든다»; 파일 s544.
- `…/shared_value_object/calculation_projection.py::CalculationProjection` — s182 exact 7필드 표(§3.3), s87 «단일 §3.3 `CalculationProjection`으로 투영»; 파일 s545.
- `…/shared_value_object/pinned_reading_bundle.py::PinnedReadingBundle`
  — `create(bundle_id=…, requested_bundle_ref=…, rag_release_refs=…, glossary_refs=…, integration_scope_refs=…, available_entries=…)` s88; 파일 s546.
- `…/shared_value_object/retrieval_plan.py::RetrievalPlan` — s89·s129; 파일 s548.
- `…/shared_value_object/evidence_bundle.py::EvidenceBundle` — s676 (FR-3 소유 위치), 용어 s73; 파일 s549.
- `…/domain_service/reading_request_policy_service.py::ReadingRequestPolicyService`
  — `validate_calculation_requirement(request, pinned_constraints, calculation_projection)`, `validate_question_limit(request, retrieval_plan)` s86; 파일 s554.
- `…/domain_service/retrieval_planning_service.py::RetrievalPlanningService` — s89; 파일 s555.
- `…/domain_service/evidence_assembly_service.py::EvidenceAssemblyService` — s90; 파일 s556.
- `…/domain_service/citation_gate.py::CitationGate` — s91; 파일 s557.
- `…application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case.py::PrepareFortuneEvidenceUseCase`
  — s674; `execute(query)` s409 «result: PrepareFortuneEvidenceResult = prepare_fortune_evidence_use_case.execute(query)»; 파일 s504.
- `…/prepare_fortune_evidence/prepare_fortune_evidence_query.py::PrepareFortuneEvidenceQuery` — s408 «query: PrepareFortuneEvidenceQuery = ...»; 파일 s506.
- `…/prepare_fortune_evidence/prepare_fortune_evidence_result.py::PrepareFortuneEvidenceResult` `{provision: EvidencePrepared | Abstained}` — s162~s163 «`provision: EvidencePrepared | Abstained`만 가진다»; 파일 s507.
- `…application_layer/citation_validation/validate_citations/validate_citations_use_case.py::ValidateCitationsUseCase` — s674; 파일 s512.
- `…/validate_citations/validate_citations_result.py::ValidateCitationsResult` — s247 «성공 `ValidateCitationsResult(CitationsValid)`를 반환한다»; 파일 s515.
- `…application_layer/port/reading_bundle/reading_bundle_port.py::ReadingBundlePort` — `pin()` s88 «`ReadingBundlePort.pin()`이 primitive-only …을 반환하면»; 파일 s526.
- `…application_layer/port/reading_bundle/pinned_reading_bundle_out.py::PinnedReadingBundleOut` — s88; 문면에 등장한 부분 필드: `bundle_id`(s155 «out.bundle_id»), `available_entries`(s129); 파일 s527. (port DTO — published-language 아님, 전체 필드 병기 의무 없음.)
- `…driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py::QueryTranslationAdapter` — s133; 파일 s572.
- `…driven_layer/adapter/external_system/rag_runtime/trusted_bundle_adapter.py::TrustedBundleAdapter` — s677·s898; 파일 s577.
- `…driven_layer/adapter/external_system/rag_runtime/hybrid_retrieval_adapter.py::HybridRetrievalAdapter` — s89 «그 유일한 contract-mismatch owner는 `HybridRetrievalAdapter`다», s209; 파일 s578.

### [C] 파일 결합이 자리 규약 추정(가장 약함 — 재량)

- `…driving_layer/api/evidence/schema/schema_in.py::PrepareFortuneEvidenceRequestSchema` — 심볼 s108; 파일 s455 (이름 불일치 — in-스키마 자리 규약 추정).
- `…driving_layer/api/evidence/schema/schema_out.py::EvidenceProvisionResponseSchema` — 심볼 s163 «HTTP 200 `EvidenceProvisionResponseSchema`도 같은 discriminator union»; 파일 s456 (자리 규약 추정).

### 파일 미명시 심볼 (심볼·필드는 문면, 소유 파일 결합 불가 — 부재로 남김)

- `register_fortune_reading_api(api)` — s310 «endpoint 등록은 … `register_fortune_reading_api(api)` 호출로 한다»; 정의 파일 문면 부재(호출처는 urls.py — s282 «registrar는 `spring_dream_server/urls.py`», s633).
- `EvidencePrepared` `{kind: Literal["evidence_prepared"], bundle_id: str, fortune_ref: str, question: str, query_language: str, calculation_projection: CalculationProjection | None, translation_traces: tuple[TranslationCallTrace, ...], retrieval_traces: tuple[RetrievalTargetTrace, ...], evidence_sets_by_work: tuple[EvidenceSetView, ...], evidence_groups_by_rag_id: tuple[EvidenceGroupView, ...], reading_method: ReadingMethodView, allowed_evidence: tuple[AllowedEvidence, ...], evidence_set_digest: str}` — s167.
- `Abstained` `{kind: Literal["abstained"], reason: Literal["no_candidate","no_evidence","insufficient_evidence"], bundle_id: str, release_reservation: Literal[True], trace: ProvisionTrace}` — s168.
- `EvidenceProvisionBlocked` (OHS-only) `{kind: Literal["blocked"], reason: Literal["invalid_request","registry_contract_mismatch","temporary_error","resource_limit"], bundle_id: str | None, trace: ProvisionTrace}` — s169.
- `CitationsValid` `{kind: Literal["citations_valid"], bundle_id: str, evidence_set_digest: str, validated_citation_count: int}` — s202.
- `CitationBlocked` `{kind: Literal["blocked"], reason: Literal["invalid_citation"], bundle_id: str, evidence_set_digest: str, trace: ProvisionTrace}` — s202.
- `WorkRagRef` `{work_id: str, rag_id: str}` — s123.
- `ReadingCharacter` `{character_id: UUID, book_usage_policy: Literal["single","source_and_commentary","compare"], work_ids: tuple[str, ...]}` — s124.
- `CalculationOutputContract` — s87 (불변식 소유자; 소유 파일 문면 부재 — s889는 예외 `CalculationOutputContractMismatch`의 파일만 명시).
- `RetrievalTargetResult` — s213 «`RetrievalTargetResult(state="failed", hits=(), successful_channels=(), failed_channels=…, failure_reason="temporary_error")»; 파일 문면 부재.
- §3.3 nested public types(파일 전건 문면 부재): `PillarView`(s175), `FourPillarsProjection`(s176), `MajorFortuneProjection`(s177), `PreMajorFortuneProjection`(s178), `AnnualFortuneProjection`(s179), `TableRefProjection`(s180), `CalculationTraceProjection`(s181), `GlossaryRefView`(s183), `TermsByLanguageView`(s184), `DictionaryMatchTraceView`(s185), `LlmConceptTraceView`(s186), `TranslationCallTrace`(s187), `RetrievalContractRefView`(s188), `RetrievalTargetTrace`(s189), `EvidenceSetView`(s190), `EvidenceGroupView`(s191), `EvidenceCrosswalkView`(s192), `ReadingMethodView`(s193), `ProvisionTrace`(s194).
- `CACHE_CONTROL_HEADER: dict[str, object] = {"required": True, "schema": {"type": "string"}, "example": "no-store"}` — s413; 모듈 상수(클래스·함수 아님)·파일 문면 부재 → symbols 본 목록 제외.
- 역방향 부재: `outcome.py`(s551)·domain `allowed_evidence.py`(s550)·port in/out 파일 다수(s521~s522, s528, s533~s534)·command/query/result 일부·published_error 2파일(s474, s491)·`invalid_citation_exception.py`(s492)는 파일은 계획됐으나 공개 심볼명이 문면에 없음.

---

## 블록 3 — boundary-imports

문면이 명시한 소비만. 소비 파일 또는 대상 모듈이 문면에 없으면 «미명시»로 남겼다.

| 소비 파일 | import 대상 모듈 | provenance |
|---|---|---|
| `application/fortune_reading/driving_layer/api/bc_error_schema.py` | `framework/ninja/framework_error_schema.py` (공통 `FrameworkErrorSchema`) | s342 «공통 class를 import하고 BC base error schema가 상속», canonical path s346, 상속 s371 |
| `spring_dream_server/urls.py` | fortune_reading registrar 모듈 — **모듈 경로 미명시** (`register_fortune_reading_api(api)` 호출) | s633 «registrar import/call 2줄», s310, s282 |
| `framework/technology/rag/runtime/ontology_c11.py` | `framework/technology/rag/runtime/service_runtime.py` | s640 «private glue 대신 service_runtime import로 전환» |
| `framework/technology/rag/runtime/ontology_service.py` | `framework/technology/rag/runtime/service_runtime.py` (제품 consumption helper 전환) | s851 «Bundle load/retrieval 제품 consumption helper를 `service_runtime.py`로 전환한다» |
| `framework/technology/rag/runtime/ontology_c11.py` | `framework/technology/rag/runtime/rag_builder/_contracts.py` (`Embedder`) | s839 «세 의존을 전환한다» |
| `framework/technology/rag/runtime/rag_builder/index.py` | `rag_builder/_contracts.py` (`Embedder`) | s839 |
| `framework/technology/rag/runtime/rag_builder/steps/__init__.py` | `rag_builder/_contracts.py` (`Embedder`) | s839 |
| `…driven_layer/…/rag_runtime/hybrid_retrieval_adapter.py` | common `search_hybrid_index` — **소유 모듈 문면 미명시** | s817 «새 adapter는 common `search_hybrid_index`를 호출», s149 «common runner 실행» |
| **소비 파일 문면 미명시** (P3 산출물 type boundary) | `rag_builder.index`가 re-export하는 `Embedder` | s818 «`rag_builder.index`가 현재 re-export하는 `Embedder`를 사용해 `hybrid_retrieval` 직접 참조를 새로 늘리지 않는다» |
| `…driven_layer/…/query_translation/query_translation_adapter.py` (파일 결합은 명명일치) | 타 BC `query_translation` published OHS — **모듈 경로 문면 미명시** | s100 «published OHS만 synchronous ACL adapter로 소비한다», s133 |
| `application/fortune_reading/test/integration/test_calculation_output_contract.py` | `application/fortune_reading/test/factories/fortune_calculation_output_factory.py` | s700 «fixture owner …factory.py; test …test_calculation_output_contract.py», s267 |
| citation_validation contract 칸 (`allowed_evidence.py`·`cited_answer.py` 등) | 서드파티 `pydantic` | s229 «`AllowedEvidence` Pydantic contract», s236 «Pydantic 모델은 missing sentinel/field-set 기반…», s244 |

부재/비전사 메모:
- `spring_dream_server/settings/base.py`의 `INSTALLED_APPS` `FortuneReadingConfig` 1줄(s631)은 등록이지 import 문면이 아니라 전사하지 않음.
- `TrustedBundleAdapter`↔pin capability는 «`assert_trusted_current_bundle` 상당»(s155)으로만 서술 — import 대상 모듈 부재.
- 그 밖의 테스트→fake/factory 결합(예: s804 «fake retrieval port»)은 파일 대 파일 import 문면이 없어 전사하지 않음.

```text
# 금지 명시(참고 — import 부정 계약, 문면 그대로)
- domain → application/port DTO import 0                       # s88 «domain import graph에서 …참조는 0», s665, s882
- domain이 framework Schema·HTTP Status·pathlib·environment·Service Bundle JSON dict·search engine class 직접 인지 금지  # s93
- `ontology_c11.py` private function import 금지                # s210
- BC 안 LLM provider import/call 0, SPARQL 0, 개별 RAG active.json read 0  # s882, s216
- `fortune_catalog`/`fortune_character` private import 금지     # s99, s919
- framework가 application BC를 역-import하지 않음               # s851
- `hybrid_retrieval` 직접 참조 신규 증가 금지                    # s818
```

---

## 블록 4 — physical-signals

대상: §8 영구 test artifact 입장 표의 add 22행 (update 0 — s770 «update | 0»).
명세 전문에 새 테스트의 DB 마커·베이스 클래스·test client 사용 문면이 **한 건도 없다** → 전건 «부재».
방증: DB lens 비활성 «영속 상태·ORM 모델·migration…을 만들지 않는다»(s9), Slice V forbidden scan «DB model/migration 0»(s882).

| row | 테스트 경로 | markers | base | client | provenance |
|---|---|---|---|---|---|
| T01 | `application/fortune_reading/test/integration/test_calculation_output_contract.py` | 부재 | 부재 | 부재 | s700 |
| T02 | `application/fortune_reading/test/unit/test_reading_request.py`, `…/test_reading_request_policy_service.py` | 부재 | 부재 | 부재 | s701 |
| T03 | `application/fortune_reading/test/unit/test_retrieval_planning_service.py` | 부재 | 부재 | 부재 | s702 |
| T04 | `application/fortune_reading/test/unit/test_retrieval_planning_service.py` | 부재 | 부재 | 부재 | s703 |
| T05 | `application/fortune_reading/test/unit/test_evidence_assembly_service.py` | 부재 | 부재 | 부재 | s704 |
| T06 | `application/fortune_reading/test/unit/test_allowed_evidence.py` | 부재 | 부재 | 부재 | s705 |
| T07 | `application/fortune_reading/test/unit/test_evidence_assembly_service.py` | 부재 | 부재 | 부재 | s706 |
| T08 | `application/fortune_reading/test/unit/test_citation_gate.py` | 부재 | 부재 | 부재 | s707 |
| T09 | `application/fortune_reading/test/integration/test_evidence_schema_equivalence.py` | 부재 | 부재 | 부재 | s708 |
| T10 | `application/fortune_reading/test/integration/test_trusted_bundle_adapter.py` | 부재 | 부재 | 부재 | s709 |
| T11 | `application/fortune_reading/test/integration/test_query_translation_adapter.py` | 부재 | 부재 | 부재 | s710 |
| T12 | `application/fortune_reading/test/integration/test_hybrid_retrieval_adapter.py` | 부재 | 부재 | 부재 | s711 |
| T13 | `application/fortune_reading/test/integration/test_hybrid_retrieval_adapter.py` | 부재 | 부재 | 부재 | s712 |
| T14 | `application/fortune_reading/test/integration/test_active_bundle_matrix.py` | 부재 | 부재 | 부재 | s713 |
| T15 | `application/fortune_reading/test/integration/test_active_bundle_matrix.py` | 부재 | 부재 | 부재 | s714 |
| T16 | `application/fortune_reading/test/integration/test_crosswalk_candidate_bundle.py` | 부재 | 부재 | 부재 | s715 |
| T17 | `application/fortune_reading/test/integration/test_open_host_services.py` | 부재 | 부재 | 부재 | s716 |
| T18 | `application/fortune_reading/test/integration/test_open_host_services.py` | 부재 | 부재 | 부재 | s717 |
| T19 | `application/fortune_reading/test/e2e/test_evidence_api.py` | 부재 | 부재 | 부재 | s718 |
| T20 | `application/fortune_reading/test/e2e/test_evidence_openapi.py` | 부재 | 부재 | 부재 | s719 |
| T21 | `application/fortune_reading/test/e2e/test_evidence_provider_boundaries.py` | 부재 | 부재 | 부재 | s720 |
| T22 | `application/fortune_reading/test/e2e/test_evidence_bundle.py` | 부재 | 부재 | 부재 | s721 |

(참고: legacy 표의 클래스 경로 표기 — `YeonhaeEvidenceApiTests` s732~s737, `ImmutableReleaseTests` s754~s757 — 는 add/update 행이 아니라 본 표 비대상.)

---

## 블록 5 — exception-map

### 5a. 정의·소유 파일 (s889 «concrete exception의 단일 소유 경로는 다음과 같다» — 전건 문면 명시)

| published 예외 | raise 창구(파일) — 소유 경로 | provenance |
|---|---|---|
| `InvalidReadingRequest` | `application/fortune_reading/domain_layer/shared_value_object/reading_request.py` | s889 |
| `CalculationOutputContractMismatch` | `application/fortune_reading/domain_layer/shared_value_object/calculation_projection.py` | s889 |
| `BundleSelectionMismatch` | `application/fortune_reading/domain_layer/shared_value_object/bundle_selection_mismatch.py` | s889 |
| `InvalidCitation` | `application/fortune_reading/domain_layer/domain_service/citation_gate.py` | s889 |
| `ReadingBundleContractMismatch` | `application/fortune_reading/application_layer/port/reading_bundle/exception.py` | s889 «adapter contract failure인 …만 둔다» |
| `InvalidTranslationRequest` | `application/fortune_reading/application_layer/port/query_translation/exception.py` | s889 |
| `TranslationContractMismatch` | `application/fortune_reading/application_layer/port/query_translation/exception.py` | s889 |
| `RetrievalContractMismatch` | `application/fortune_reading/application_layer/port/evidence_retrieval/exception.py` | s889 |
| `RetrievalTemporaryFailure` | `application/fortune_reading/application_layer/port/evidence_retrieval/exception.py` | s889 |
| `RetrievalResourceLimit` | `application/fortune_reading/application_layer/port/evidence_retrieval/exception.py` | s889 |

### 5b. raise 주체(§10 failure 표 s891~s913 — 주체는 클래스/역할 문면; 파일 열은 추가 결합하지 않고 명명일치 부기만)

| published 예외 | raise 주체(문면) → 파일 부기 | provenance |
|---|---|---|
| `InvalidReadingRequest` | `ReadingRequest` (→ reading_request.py, s889 일치) | s893 |
| `InvalidReadingRequest` | `ReadingRequestPolicyService.validate_calculation_requirement`(plan 전) (→ reading_request_policy_service.py 명명일치) | s894 |
| `InvalidReadingRequest` | `ReadingRequestPolicyService.validate_question_limit(request, RetrievalPlan)`(non-empty plan 뒤) | s895 |
| `CalculationOutputContractMismatch` | `CalculationOutputContract`(fortune 분류 전) — 소유 파일 문면 부재 | s896 |
| `BundleSelectionMismatch` | `PinnedReadingBundle.create` domain invariant (→ pinned_reading_bundle.py 명명일치) | s897 |
| `ReadingBundleContractMismatch` | `TrustedBundleAdapter` (→ trusted_bundle_adapter.py 명명일치); missing/non-positive limit는 «DTO 정규화 owner» | s898, s129 |
| `InvalidTranslationRequest` / `TranslationContractMismatch` | ACL adapter (upstream published exception 번역) | s901 |
| `RetrievalContractMismatch` | retrieval adapter — «유일 mismatch owner» `HybridRetrievalAdapter` | s902, s908, s209 |
| `RetrievalTemporaryFailure` | retrieval adapter request fold — 모든 selected target failed일 때만 | s907 |
| `RetrievalResourceLimit` | retrieval adapter — explicit memory/capacity guard 정규화 | s909, s214 |
| `InvalidCitation` | citation gate (→ citation_gate.py, s889 일치) | s912 |

부재 메모:
- OHS `Blocked(...)`/`CitationBlocked`는 예외가 아니라 published 응답 변형(s163, s202) — 본 표 비대상.
- `evidence_provisioning_published_error.py`(s474)·`citation_validation_published_error.py`(s491)의 심볼명↔예외 매핑 문면 부재.
- unexpected programming exception은 framework 500 «BC schema로 은폐하지 않음»(s913) — BC 예외 아님.
- HTTP status 매핑(400/503)과 OHS Blocked reason 매핑은 s397~s400·s893~s913에 성문 — 본 블록 형식(2열) 밖이라 provenance로만 부기.

---

## 충돌·긴장 기록

- **양립 불가 충돌: 0건.** §8.3 집계(add 22/reuse 2/retain 14/remove 19/reject 2, s769~s776)와
  §8.1~§8.2 행 전수(T01~T22, T23~T24, T25+L18~L29+L32, L01~L17+L30~L31, T26~T27)가 일치함을 계수로 확인.
- 긴장 1 — `tests/test_hybrid_retrieval.py`: s652(주석 없는 mutation 목록) vs s840 «파일과 7 old tests를 제거한다»
  — «파일»이 production `hybrid_retrieval.py`인지 테스트 파일 포함인지 문면 불명. update로 전사, remove 가능성 병기.
- 긴장 2 — `views.py`: s646 «L3 legacy view symbol/import delete» vs s864 «다른 live view가 있으면 파일은 유지한다»
  — 충돌 아닌 세목화로 판단, update.
