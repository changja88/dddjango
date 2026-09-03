
## pre-gate 예보 — 2026-09-03T04:15:00Z · spec_final_19b27df.md

- 기준선 SHA: `80431d9480f79e7c33cdc13b3f8892adced53089` (--base 80431d9480f79e7c33cdc13b3f8892adced53089) — «스텁 제외 현재 상태» · 프로필: auto · 모드: 관찰(observe) · 실행기: design_pregate.py · dddjango v2.17.16 · 블록 해시 a89de0574a0e
- 예보는 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤 형태로도 대체·축약하지 않는다.
- 커버: P/S/I급 결정 계약 표면(보수 추정 — 유일한 판정자는 백테스트·관찰 실측이다). C급·④형은 표면 밖.
- 판정: 예보 red — P/S/I급 결정 계약 위반 예보 4건 · 계약 실존 결손 0건(권고·비차단)

### 예보 항목 (4건 · 안정 ID = sha256(규칙#+경로)[:12])

- `92767435ca49` check-composition-root.py :: [#107] application/fortune_reading/driving_layer/api/api_router.py: `def register_fortune_reading_api(api)` 등록 함수 «하나»만 갖는다(지금 함수 2개)
- `c6a24a79acf9` check-context-isolation.py :: [#157] application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/request/prepare_fortune_evidence_request.py: 계약 타입 하나 = 파일 하나다 — 공개 클래스가 2개다(주 계약이 어노테이션으로 참조하는 보조 dataclass 만 예외)
- `c6c72f30f720` check-port-adapter-pairing.py :: [#219] application/fortune_reading/application_layer/port/evidence_retrieval/evidence_retrieval_port.py: 공개 클래스 2개 — 추상 인터페이스 «하나»가 온다
- `c9586d218922` check-usecase-dto-placement.py :: [#635] application/fortune_reading/application_layer/evidence_provisioning/validate_citations/validate_citations_use_case.py: 진입점은 클래스 «하나»다 — 공개 클래스가 2개다

### 계약 실존 (boundary-imports 3단 · 결손 0건 · 안정 ID = e-sha256(모듈+이름)[:12])

- 집계: 행 17 · 이름 판정 17 · 실존 확인 15 · 자기 add 해소 0 · 자기 update 해소 1 · 저장소 밖(검사 밖) 1 · 판정 불능 0 · 결손 0(항목 0)
- (없음) — 명세가 선언한 경계 import 계약 전건 실존(저장소 밖 1건은 검사 밖·자기 add 0건은 symbols 채널 소관·자기 update 1건은 update 칸 symbols 선언)

### already-built (3건) · 미시뮬레이션 (92건)

- already-built: empty(기실현): application/fortune_reading/composition_root/event_wiring.py
- already-built: empty(기실현): application/fortune_reading/driving_layer/event_subscription/event_router.py
- already-built: empty(기실현): application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/exception/citation_validation_published_error.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/pydantic/cited_answer_schema.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/domain_layer/shared_value_object/evidence_source.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/port/evidence_digest/evidence_digest_port.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driven_layer/adapter/evidence_digest/rfc8785_adapter.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_cited_answer_schema_equivalence.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_allowed_evidence.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_citation_gate.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_evidence_assembly_service.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_rfc8785_adapter.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/service_runtime.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/port/evidence_retrieval/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/port/evidence_retrieval/evidence_retrieval_port.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_result_out.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/port/evidence_retrieval/exception.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driven_layer/adapter/evidence_retrieval/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_prepare_fortune_evidence_use_case.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_rag_runtime_evidence_retrieval_adapter.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_retrieval_outcome_policy.py
- 미시뮬레이션: remove(실존 없음): application/fortune_reading/test/e2e/test_crosswalk_candidate_bundle.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_crosswalk_candidate_bundle.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/domain_layer/shared_value_object/reading_request.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_reading_request.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/api/evidence_provisioning/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/api/evidence_provisioning/evidence_provisioning_controller.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/api/evidence_provisioning/schema/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/api/evidence_provisioning/schema/schema_in.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/api/evidence_provisioning/schema/schema_out.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/api/api_router.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/api/bc_error_schema.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/request/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/request/prepare_fortune_evidence_request.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/response/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/response/prepare_fortune_evidence_response.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_published_error.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_exception.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/citation_validation/citation_validation_service.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/request/validate_citations_request.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/validate_citations_response.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): application/fortune_reading/application_layer/citation_validation/__init__.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): application/fortune_reading/application_layer/citation_validation/validate_citations/__init__.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_use_case.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_command.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_query.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_result.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/evidence_provisioning/validate_citations/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/evidence_provisioning/validate_citations/validate_citations_use_case.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/evidence_provisioning/validate_citations/validate_citations_command.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/evidence_provisioning/validate_citations/validate_citations_query.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/application_layer/evidence_provisioning/validate_citations/validate_citations_result.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/composition_root/dependency_wiring.py
- 미시뮬레이션: remove(실존 없음): application/fortune_reading/test/e2e/test_active_bundle_matrix.py
- 미시뮬레이션: remove(실존 없음): application/fortune_reading/test/e2e/test_open_host_services.py
- 미시뮬레이션: remove(실존 없음): application/fortune_reading/test/e2e/typecheck_citation_open_host_service_consumer.py
- 미시뮬레이션: remove(실존 없음): application/fortune_reading/test/e2e/test_evidence_api.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/e2e/test_evidence_openapi.py
- 미시뮬레이션: remove(실존 없음): application/fortune_reading/test/e2e/test_evidence_provider_boundaries.py
- 미시뮬레이션: remove(실존 없음): application/fortune_reading/test/e2e/test_evidence_bundle.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_active_bundle_matrix.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_open_host_services.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/typecheck_citation_open_host_service_consumer.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_evidence_api.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_evidence_provider_boundaries.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/unit/test_evidence_bundle.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/fake/query_translation_port.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/fake/reading_bundle_port.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): application/fortune_reading/test/fake/evidence_retrieval_port.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): spring_dream_server/settings/base.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): spring_dream_server/urls.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/rag_builder/_contracts.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/rag_builder/index.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/rag_builder/steps/__init__.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/yeonhae_authorized.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): tests/test_yeonhae_authorized.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): framework/technology/rag/runtime/hybrid_retrieval.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): tests/test_hybrid_retrieval.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/ontology_service.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/ontology_c11.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): tests/test_ontology_c11.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): tests/test_ontology_service.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): tests/test_ontology_evidence_contract_c11.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): framework/technology/rag/runtime/root_migration.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): framework/technology/rag/runtime/views.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): framework/technology/rag/runtime/yeonhae_retrieval.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): tests/test_yeonhae_rag.py
- 미시뮬레이션: 후행 remove(@Ln — G1 승인 시점 상태 유지): tests/test_yeonhae_retrieval.py
- 미시뮬레이션: update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): fabfile.py
- 채널 메모: symbols 고아 행(file-plan 미등재 — 미반영): application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case/prepare_fortune_evidence_use_case.py::PrepareFortuneEvidenceUseCase
- 채널 메모: symbols 고아 행(file-plan 미등재 — 미반영): application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case/prepare_fortune_evidence_use_case.py::PrepareFortuneEvidenceUseCase.execute(command: PrepareFortuneEvidenceCommand) -> PrepareFortuneEvidenceResult
- 채널 메모: symbols 고아 행(file-plan 미등재 — 미반영): application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case/prepare_fortune_evidence_failure.py::PrepareFortuneEvidenceFailureCategory(StrEnum) {INVALID_REQUEST="invalid_request", REGISTRY_CONTRACT_MISMATCH="registry_contract_mismatch", TEMPORARY_ERROR="temporary_error", RESOURCE_LIMIT="resource_limit"}
- 채널 메모: symbols 고아 행(file-plan 미등재 — 미반영): application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case/prepare_fortune_evidence_failure.py::PrepareFortuneEvidenceFailure(Exception) {phase: Literal["pre_pin", "post_pin"], bundle_id: str | None, category: PrepareFortuneEvidenceFailureCategory, stage: Literal["input", "pin", "translation", "retrieval", "assembly"], cause: InvalidReadingRequest | BundleSelectionMismatch | CalculationOutputContractMismatch | InvalidTranslationRequest | ReadingBundleContractMismatch | TranslationContractMismatch | RetrievalContractMismatch | EvidenceDigestConflict | RetrievalTemporaryFailure | RetrievalResourceLimit}
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/api/api_router.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/application_layer/port/evidence_retrieval/evidence_retrieval_port.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/test/fake/evidence_retrieval_port.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/test/fake/query_translation_port.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/test/fake/reading_bundle_port.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/test/unit/test_crosswalk_candidate_bundle.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): tests/test_ontology_c11.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/application_layer/evidence_provisioning/validate_citations/validate_citations_use_case.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/application_layer/evidence_provisioning/validate_citations/validate_citations_use_case.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/api/evidence_provisioning/evidence_provisioning_controller.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/api/evidence_provisioning/evidence_provisioning_controller.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/api/evidence_provisioning/evidence_provisioning_controller.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/api/evidence_provisioning/evidence_provisioning_controller.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py
- 채널 메모: boundary-imports 스텁 미반영(비-add `update` 칸 — 실존 판정에는 포함): application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py

### 사각 목록(상시 병기)

- C급(함수 본문·행위 규칙): 스텁 본문이 `...` 뿐이라 예보 표면 밖이다.
- ④형(명세 내부 의미 모순·규범 과잉결정): 검출 대상이 아니다.
- BC 내부 계층 의존 오설계(#92/#93류): 유도 삽입은 정의상 규약 준수형 — 원리적 예보 불가.
- 앵커·상태 축: 예보 기준선은 «스텁 제외 현재 상태»다 — G2 build_anchor 차분과 다르며, HEAD 판형 게이트 결과의 G2 증거 유용은 차분 세탁으로 금지된다.
- 미시뮬레이션: update 계획·후행 remove(@Ln)는 실체화하지 않는다 — 위 목록 병기.
- 정형 보충(apps.py name/label·모델 Meta.db_table·마이그레이션 칸): 결손 시 규약 유도값을 합성한다 — 기계 블록 전사가 있으면 전사 우선이지만, «산문»으로만 규약 밖 값을 계획한 일탈은 예보 표면 밖이다.
- 기실현 add(`--base` 명시 시 — 명시 `--base HEAD` 포함): 사본 = 기준선 트리 + (worktree−HEAD) 오버레이 — 기준선 이후 커밋분은 사본에 없다. 오버레이 실존 add 는 앵커 커밋 전에 걷어내고 스텁으로 실체화해 예보하므로(앵커 스냅숏 무오염·실물 판정 혼입 0 — 커밋된 add 와 같은 ID·exit) 실물이 스텁과 다른 위반은 예보 표면 밖이고, 유일 판정자는 G2 앵커 차분이다.
- 계약 실존(boundary-imports 3단): 판정 기준은 **이 브랜치**의 격리 사본(기준선 + dirty overlay + 이 명세의 add — `--base` 명시 시 기준선 이후 커밋분은 사본에 없다: 재발화 판형)이다 — 다른 워크트리·미머지 브랜치의 실물은 보지 않는다(부재 = 결손 · 상류 소유 계약의 선행 대기는 `deferred` 처분으로 명세가 소유 레인·해소 조건을 명시한다). 자기 add 대상의 이름 정의(⑶)는 symbols 채널 소관이라 생략하고, update 대상은 symbols 선언 이름을 자기 update 해소로 본다(표면은 이 명세 이후 상태). 결손은 권고·비차단(exit 5)이며 G0 선행 조건 확인·상류 머지 판단을 대체하지 않는다.
- 계약 실존 표면 밖·판정 경계(결과별): 판정 불능 U = `import *`(소비 행·재수출 표면)·`__getattr__` 표면·네임스페이스 폴더의 비서브모듈 이름·AST 파싱 실패·문법 불량 행·소비자 remove·update 대상의 미선언·미실존 이름 / 관대 K(미탐 방향) = `TYPE_CHECKING` 가드 안 바인딩(런타임 부재여도 최상위 바인딩으로 센다)·update 대상의 현재 표면 이름(update 가 지우는 경우) / 검사 밖 X = 저장소 밖 패키지(표준·서드파티) / 결손 ⑴ 방향 = gitignore 된 실물(사본 밖 — 이 브랜치 추적 기준)·사본에 부재한 `update` 대상(update 는 파일을 만들지 않는다 — 선언·미선언 무관) / 행 자체가 없다 = 동적 import(`importlib` 리터럴).
