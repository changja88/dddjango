# 맹검 소급 전사 — fortune_reading G1 설계 명세 (2d44743, P2 승인 시점)

- 원본: `git show 2d44743:.dddjango/20260831-2331-fortune-reading/design-spec.md`
  → 로컬 사본 `spec-p2-time.md` (1868행). 아래 `sNNN`은 이 사본의 행 번호다.
- 유일 근거: 위 명세 원문 + 성문 형식 규범. 구현 코드·검사기·orders·violations는 열지 않았다.
- fail-closed: 전 행 provenance. 태그는 오직 명세 문면으로 판정.

---

## 블록 1 — file-plan

표기: `<태그><TAB><경로>  # sNNN[: 발췌]`. §6.2 트리 행(s558~s803)의 발췌는 경로 문자열과
동일하므로 행 번호만 부기, 트리 주석은 발췌로 옮김.

범위 판단(자백): 순수 `__init__.py` 패키지 마커·persistence 고정 slot(s760~s764)·django
models/migrations/admin `__init__.py`(s739~s741)는 표준 골격 비전사 규칙으로 제외. 이 판의
명세는 빈 슬롯을 «0-byte empty fixed file»/«없음» 주석으로 성문하므로 그 행들은 `empty`로 전사.
read-only/gate-only inventory(s1108~s1118, write 0)와 registry gate 스크립트(s1128~s1238,
gate-only·permanent artifact 0)는 file-plan 비전사. `# 미전개` 대상 와일드카드는 파일 계획 안에 0
(스캔 범위 `framework/technology/rag/runtime/**` s458, `application/fortune_reading/test/**` s1657,
`framework/pydantic/**` 추가 0 s805는 계획 아님·비전개).

```paths
# ── §6.2 신규 BC 트리 (s556 «다음이 신규 파일의 허용·계획 목록이다»)
add	application/fortune_reading/composition_root/dependency_wiring.py	# s563
empty	application/fortune_reading/composition_root/event_wiring.py	# s564: «event 0이므로 0-byte empty fixed file»
empty	application/fortune_reading/published_event/__init__.py	# s566: «published event 없음»
add	application/fortune_reading/driving_layer/api/api_router.py	# s571
add	application/fortune_reading/driving_layer/api/bc_error_schema.py	# s572 (s473 «단독 소유»)
add	application/fortune_reading/driving_layer/api/evidence/evidence_controller.py	# s575
add	application/fortune_reading/driving_layer/api/evidence/schema/schema_in.py	# s578: «HTTP request owner; private nested models keep existing explicit OpenAPI titles»
add	application/fortune_reading/driving_layer/api/evidence/schema/schema_out.py	# s579
empty	application/fortune_reading/driving_layer/api/webhook/__init__.py	# s581: «provider 없음»
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py	# s586
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/request/prepare_fortune_evidence_request.py	# s591
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/response/prepare_fortune_evidence_response.py	# s594
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_published_error.py	# s597
add	application/fortune_reading/driving_layer/open_host_service/evidence_provisioning/contract/exception/evidence_provisioning_exception.py	# s598
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/citation_validation_service.py	# s601
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/request/validate_citations_request.py	# s606
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/validate_citations_response.py	# s609
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/get_cited_answer_schema_response.py	# s610 (b5392f0 대비 신규; cited_answer.py/allowed_evidence.py는 트리에서 소멸 — WIP 표 s834~s835)
add	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/exception/citation_validation_published_error.py	# s613 (s840 «invalid_citation_exception.py는 만들지 않으며»)
empty	application/fortune_reading/driving_layer/cron_job/__init__.py	# s615: «jobs 없음»
empty	application/fortune_reading/driving_layer/event_subscription/event_router.py	# s618: «subscription 0이므로 0-byte empty fixed file»
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_use_case.py	# s625
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_command.py	# s626
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_query.py	# s627
add	application/fortune_reading/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_result.py	# s628
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_use_case.py	# s633
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_command.py	# s634
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_query.py	# s635
add	application/fortune_reading/application_layer/citation_validation/validate_citations/validate_citations_result.py	# s636
add	application/fortune_reading/application_layer/port/query_translation/query_translation_port.py	# s641
add	application/fortune_reading/application_layer/port/query_translation/translated_query_out.py	# s642
add	application/fortune_reading/application_layer/port/query_translation/translate_query_in.py	# s643
add	application/fortune_reading/application_layer/port/query_translation/invalid_translation_request.py	# s644 (신규 sole-owner 파일)
add	application/fortune_reading/application_layer/port/query_translation/translation_contract_mismatch.py	# s645 (신규 sole-owner 파일)
empty	application/fortune_reading/application_layer/port/query_translation/exception.py	# s646: «required fixed 0-byte empty slot; import/re-export 0»
add	application/fortune_reading/application_layer/port/reading_bundle/reading_bundle_port.py	# s649
add	application/fortune_reading/application_layer/port/reading_bundle/pinned_reading_bundle_out.py	# s650
add	application/fortune_reading/application_layer/port/reading_bundle/reading_bundle_in.py	# s651
add	application/fortune_reading/application_layer/port/reading_bundle/exception.py	# s652 (s1671 ReadingBundleContractMismatch 소유)
add	application/fortune_reading/application_layer/port/evidence_retrieval/evidence_retrieval_port.py	# s655
add	application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_result_out.py	# s656
add	application/fortune_reading/application_layer/port/evidence_retrieval/retrieval_request_in.py	# s657
add	application/fortune_reading/application_layer/port/evidence_retrieval/exception.py	# s658 (s1671 Retrieval* 3예외 소유)
add	application/fortune_reading/application_layer/port/evidence_digest/evidence_digest_port.py	# s661 (b5392f0 대비 신규 port 칸)
add	application/fortune_reading/application_layer/port/evidence_digest/evidence_digest_in.py	# s662
add	application/fortune_reading/application_layer/port/evidence_digest/evidence_source_in.py	# s663
add	application/fortune_reading/application_layer/port/evidence_digest/source_location_in.py	# s664
add	application/fortune_reading/application_layer/port/evidence_digest/exception.py	# s665 (s1671 «digest adapter normalization failure만 … 소유»)
empty	application/fortune_reading/application_layer/port/domain_bypass_query/__init__.py	# s667: «bypass query 없음»
empty	application/fortune_reading/application_layer/port/unit_of_work/__init__.py	# s669: «UoW 없음»
add	application/fortune_reading/domain_layer/shared_value_object/bundle_selection_mismatch.py	# s674
add	application/fortune_reading/domain_layer/shared_value_object/invalid_reading_request.py	# s675
add	application/fortune_reading/domain_layer/shared_value_object/book_usage_policy.py	# s676
add	application/fortune_reading/domain_layer/shared_value_object/work_rag_ref.py	# s677
add	application/fortune_reading/domain_layer/shared_value_object/reading_character.py	# s678
add	application/fortune_reading/domain_layer/shared_value_object/reading_request.py	# s679
add	application/fortune_reading/domain_layer/shared_value_object/calculation_output_contract_mismatch.py	# s680
add	application/fortune_reading/domain_layer/shared_value_object/pillar_view.py	# s681
add	application/fortune_reading/domain_layer/shared_value_object/four_pillars_projection.py	# s682
add	application/fortune_reading/domain_layer/shared_value_object/major_fortune_projection.py	# s683
add	application/fortune_reading/domain_layer/shared_value_object/pre_major_fortune_projection.py	# s684
add	application/fortune_reading/domain_layer/shared_value_object/annual_fortune_projection.py	# s685
add	application/fortune_reading/domain_layer/shared_value_object/table_ref_projection.py	# s686
add	application/fortune_reading/domain_layer/shared_value_object/calculation_trace_projection.py	# s687
add	application/fortune_reading/domain_layer/shared_value_object/calculation_projection.py	# s688
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_contract_ref.py	# s689
add	application/fortune_reading/domain_layer/shared_value_object/rag_release_ref.py	# s690
add	application/fortune_reading/domain_layer/shared_value_object/available_retrieval_entry.py	# s691
add	application/fortune_reading/domain_layer/shared_value_object/reading_constraints.py	# s692
add	application/fortune_reading/domain_layer/shared_value_object/pinned_reading_bundle.py	# s693
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target.py	# s694
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_plan.py	# s695
add	application/fortune_reading/domain_layer/shared_value_object/translation_term_set.py	# s696
add	application/fortune_reading/domain_layer/shared_value_object/translation_call_trace.py	# s697
add	application/fortune_reading/domain_layer/shared_value_object/translation_call_outcome.py	# s698
add	application/fortune_reading/domain_layer/shared_value_object/translation_disposition_kind.py	# s699
add	application/fortune_reading/domain_layer/shared_value_object/translation_disposition.py	# s700
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target_state.py	# s701
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target_trace.py	# s702
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_target_outcome.py	# s703
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_disposition_kind.py	# s704
add	application/fortune_reading/domain_layer/shared_value_object/retrieval_disposition.py	# s705
add	application/fortune_reading/domain_layer/shared_value_object/source_location.py	# s706
add	application/fortune_reading/domain_layer/shared_value_object/evidence_source.py	# s707
add	application/fortune_reading/domain_layer/shared_value_object/allowed_evidence.py	# s708 (WIP retain-and-trim s823 — 긴장 주석 참조)
add	application/fortune_reading/domain_layer/shared_value_object/evidence_digest_conflict.py	# s709
add	application/fortune_reading/domain_layer/shared_value_object/evidence_set.py	# s710
add	application/fortune_reading/domain_layer/shared_value_object/evidence_grouping.py	# s711
add	application/fortune_reading/domain_layer/shared_value_object/allowed_evidence_digest.py	# s712
add	application/fortune_reading/domain_layer/shared_value_object/evidence_set_digest.py	# s713
add	application/fortune_reading/domain_layer/shared_value_object/digested_allowed_evidence.py	# s714
add	application/fortune_reading/domain_layer/shared_value_object/retrieved_evidence.py	# s715
add	application/fortune_reading/domain_layer/shared_value_object/evidence_set_view.py	# s716
add	application/fortune_reading/domain_layer/shared_value_object/evidence_group_view.py	# s717
add	application/fortune_reading/domain_layer/shared_value_object/evidence_crosswalk_view.py	# s718
add	application/fortune_reading/domain_layer/shared_value_object/reading_method_view.py	# s719
add	application/fortune_reading/domain_layer/shared_value_object/evidence_bundle.py	# s720
add	application/fortune_reading/domain_layer/shared_value_object/abstention_reason.py	# s721
add	application/fortune_reading/domain_layer/shared_value_object/abstained.py	# s722
add	application/fortune_reading/domain_layer/shared_value_object/invalid_citation.py	# s723
add	application/fortune_reading/domain_layer/shared_value_object/citation_validation.py	# s724
add	application/fortune_reading/domain_layer/domain_service/validate_calculation_output.py	# s727
add	application/fortune_reading/domain_layer/domain_service/apply_reading_request_policy.py	# s728
add	application/fortune_reading/domain_layer/domain_service/plan_retrieval.py	# s729
add	application/fortune_reading/domain_layer/domain_service/classify_translation_outcome.py	# s730
add	application/fortune_reading/domain_layer/domain_service/fold_retrieval_outcome.py	# s731
add	application/fortune_reading/domain_layer/domain_service/assemble_evidence.py	# s732
add	application/fortune_reading/domain_layer/domain_service/validate_citations.py	# s733
add	application/fortune_reading/driven_layer/django_fortune_reading/apps.py	# s738 (s1069 exact class binding)
add	application/fortune_reading/driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py	# s748
empty	application/fortune_reading/driven_layer/adapter/external_system/__init__.py	# s750: «socket-opening external system adapter 없음»
add	application/fortune_reading/driven_layer/adapter/reading_bundle/rag_runtime_adapter.py	# s753
add	application/fortune_reading/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py	# s756
add	application/fortune_reading/driven_layer/adapter/evidence_digest/rfc8785_adapter.py	# s759
add	application/fortune_reading/test/unit/test_calculation_output_contract.py	# s769 (T01 add s1272)
add	application/fortune_reading/test/unit/test_cited_answer_schema_equivalence.py	# s770 (T09 add s1280)
add	application/fortune_reading/test/unit/test_reading_request.py	# s771 (T02 s1273)
add	application/fortune_reading/test/unit/test_reading_request_policy_service.py	# s772 (T02 s1273)
add	application/fortune_reading/test/unit/test_retrieval_planning_service.py	# s773 (T03/T04 s1274~s1275)
add	application/fortune_reading/test/unit/test_evidence_assembly_service.py	# s774 (T05/T07 s1276/s1278)
add	application/fortune_reading/test/unit/test_allowed_evidence.py	# s775 (T06 s1277)
add	application/fortune_reading/test/unit/test_citation_gate.py	# s776 (T08 s1279)
add	application/fortune_reading/test/unit/test_rag_runtime_reading_bundle_adapter.py	# s777 (T10 s1281)
add	application/fortune_reading/test/unit/test_query_translation_adapter.py	# s778 (T11 s1282)
add	application/fortune_reading/test/unit/test_prepare_fortune_evidence_use_case.py	# s779 (T10/T11 공유 coder evidence s1065)
add	application/fortune_reading/test/unit/test_translation_outcome_policy.py	# s780 (T11 s1282)
add	application/fortune_reading/test/unit/test_rag_runtime_evidence_retrieval_adapter.py	# s781 (T12/T13 s1283~s1284)
add	application/fortune_reading/test/unit/test_retrieval_outcome_policy.py	# s782 (T13 s1284)
add	application/fortune_reading/test/unit/test_rfc8785_adapter.py	# s783 (T28 s1299)
empty	application/fortune_reading/test/integration/__init__.py	# s785: «DB-backed test 없음; concrete integration test 0»
add	application/fortune_reading/test/e2e/test_active_bundle_matrix.py	# s788 (T14/T15 s1285~s1286)
add	application/fortune_reading/test/e2e/test_crosswalk_candidate_bundle.py	# s789 (T16 s1287)
add	application/fortune_reading/test/e2e/test_open_host_services.py	# s790 (T17/T18 s1288~s1289)
add	application/fortune_reading/test/e2e/typecheck_citation_ohs_consumer.py	# s791 (T18 non-pytest proof s251/s1289)
add	application/fortune_reading/test/e2e/test_evidence_api.py	# s792 (T19 s1290)
add	application/fortune_reading/test/e2e/test_evidence_openapi.py	# s793 (T20 s1291)
add	application/fortune_reading/test/e2e/test_evidence_provider_boundaries.py	# s794 (T21 s1292)
add	application/fortune_reading/test/e2e/test_evidence_bundle.py	# s795 (T22 s1293)
empty	application/fortune_reading/test/factories/__init__.py	# s797: «factory_boy class가 생길 때만 concrete module 허용»
add	application/fortune_reading/test/fake/fake_query_translation_port.py	# s800
add	application/fortune_reading/test/fake/fake_reading_bundle_port.py	# s801
add	application/fortune_reading/test/fake/fake_evidence_retrieval_port.py	# s802
# ── BC 트리 밖 framework owner
add	framework/pydantic/cited_answer_schema.py	# s805: «BC tree 밖 추가 제품 파일은 정확히 … 하나다»; §6.3 s1078~s1079
# ── §6.3 «실제 mutation inventory» (s1075)
update	spring_dream_server/settings/base.py	# s1080~s1081: «INSTALLED_APPS에 FortuneReadingConfig 1줄»
update	spring_dream_server/urls.py	# s1082~s1084: «registrar import/call 2줄» + «L3에서 legacy v2 evidence path 제거»
add	framework/technology/rag/runtime/service_runtime.py	# s1085~s1086: «신규 common consumption module…»
update	framework/technology/rag/runtime/ontology_service.py	# s1087~s1088
update	framework/technology/rag/runtime/ontology_c11.py	# s1089~s1090: «private glue 대신 service_runtime import로 전환»
update	framework/technology/rag/runtime/rag_builder/_contracts.py	# s1091~s1092: «Embedder Protocol의 새 소유처» (add/update 문면 불명 — 자백)
update	framework/technology/rag/runtime/rag_builder/index.py	# s1093 (s1616 의존 전환)
update	framework/technology/rag/runtime/rag_builder/steps/__init__.py	# s1094 (s1616)
remove	framework/technology/rag/runtime/root_migration.py	# s1095: «# 후행 delete» (s1631)
update	framework/technology/rag/runtime/views.py	# s1096; s1643 «다른 live view가 있으면 파일은 유지한다»
remove	framework/technology/rag/runtime/yeonhae_retrieval.py	# s1097: «L3 ref 0 후 delete» (s1645)
remove	framework/technology/rag/runtime/hybrid_retrieval.py	# s1098: «후행 ref 0 후 delete» (s1617)
update	framework/technology/rag/runtime/yeonhae_authorized.py	# s1099: «stage 6·7 함수/lazy imports만 후행 delete»
update	tests/test_yeonhae_rag.py	# s1100: «L3 6 cases delete(L01~L06)» — 파일 삭제 여부 문면 부재
update	tests/test_yeonhae_retrieval.py	# s1101: «L3 4 cases delete(L07~L10)» — 파일 삭제 여부 문면 부재
update	tests/test_hybrid_retrieval.py	# s1102; s1617 «파일과 7 old tests를 제거» — 테스트 파일 잔존 여부 불명(자백)
update	tests/test_yeonhae_authorized.py	# s1103~s1104: «stage6/7 cases delete; stage8 … setup만 … 변경»
update	fabfile.py	# s1105: «L3 legacy env 3건 delete» (s1646)
# ── §6.2 P1 WIP reconciliation closed set 16행 (s819 «closed move/split/delete plan», s840)
#     명세 어휘: retain-and-trim | split-and-delete | move-and-delete | delete → 태그 매핑은 자백 8 참조
update	application/fortune_reading/domain_layer/shared_value_object/allowed_evidence.py	# s823: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/calculation_projection.py	# s824: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/evidence_bundle.py	# s825: retain-and-trim
remove	application/fortune_reading/domain_layer/shared_value_object/outcome.py	# s826: split-and-delete → abstention_reason.py/abstained.py
update	application/fortune_reading/domain_layer/shared_value_object/pinned_reading_bundle.py	# s827: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/reading_request.py	# s828: retain-and-trim
update	application/fortune_reading/domain_layer/shared_value_object/retrieval_plan.py	# s829: retain-and-trim
remove	application/fortune_reading/domain_layer/domain_service/citation_gate.py	# s830: move-and-delete → validate_citations.py::CitationGate 등
remove	application/fortune_reading/domain_layer/domain_service/evidence_assembly_service.py	# s831: move-and-delete → assemble_evidence.py
remove	application/fortune_reading/domain_layer/domain_service/reading_request_policy_service.py	# s832: move-and-delete → apply_reading_request_policy.py
remove	application/fortune_reading/domain_layer/domain_service/retrieval_planning_service.py	# s833: move-and-delete → plan_retrieval.py
remove	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/allowed_evidence.py	# s834: move-and-delete → framework owner private nested models
remove	application/fortune_reading/driving_layer/open_host_service/citation_validation/contract/response/cited_answer.py	# s835: move-and-delete → cited_answer_schema.py::CitedAnswerSchema
remove	application/fortune_reading/test/factories/fortune_calculation_output_factory.py	# s836: delete — «T01/T02 owner-local fixture로 재작성»
remove	application/fortune_reading/test/integration/test_calculation_output_contract.py	# s837: move-and-delete → test/unit/
remove	application/fortune_reading/test/integration/test_evidence_schema_equivalence.py	# s838: move-and-delete → test/unit/test_cited_answer_schema_equivalence.py
```

---

## 블록 2 — symbols

이 판은 파일↔심볼 결합을 대부분 문면으로 성문한다(§6.2 s809~s817, §10 s1671, P2 exact 계약
s846~s1057). 표기: `경로::Symbol(Base)`; published-language 칸은 `{field: type}` 병기.
경로 접두 `AFR = application/fortune_reading`.

### OHS driving (published-language)

- `AFR/driving_layer/open_host_service/evidence_provisioning/evidence_provisioning_service.py::prepare_fortune_evidence_command(request: PrepareFortuneEvidenceRequest) -> PrepareFortuneEvidenceResponse` — s238 (함수; registry operation convention).
- `AFR/…/citation_validation/citation_validation_service.py::validate_citations_command(request: ValidateCitationsRequest) -> ValidateCitationsResponse` — s238.
- `AFR/…/citation_validation/citation_validation_service.py::get_cited_answer_schema_query() -> GetCitedAnswerSchemaResponse[CitedAnswerSchema]` — s238.
- (private) `citation_validation_service.py::_CitationSchemaInvalid` — s809, s1671 «private exception으로만 존재».
- `AFR/…/contract/request/prepare_fortune_evidence_request.py::PrepareFortuneEvidenceRequest`
  `{question: str, query_language: str, fortune_ref: str, requested_bundle_ref: str | None, work_rag_refs: tuple[WorkRagRef, ...], character: ReadingCharacter, calculation_output: Mapping[str, JSONValue] | None, previous_allowed_evidence: tuple[AllowedEvidence, ...]}`
  — s135(field set 공유)·s139~s146; frozen·slots·kw-only dataclass s135; 파일: s591 + s809 «파일명의 PascalCase `<Operation>Request` … 만 공개».
- `AFR/…/contract/response/prepare_fortune_evidence_response.py::PrepareFortuneEvidenceResponse` — 3-variant `EvidencePrepared | Abstained | EvidenceProvisionBlocked` s199; variants exact fields s203~s205(union 구성 dataclass는 underscore-private — s238); 파일: s594 + s809.
- `AFR/…/citation_validation/contract/request/validate_citations_request.py::ValidateCitationsRequest`
  `{bundle_id: str, evidence_set_digest: str, allowed_evidence: tuple[Mapping[str, object], ...], cited_answer: Mapping[str, object]}` — s305 (b5392f0의 typed AllowedEvidence/CitedAnswer 필드에서 Mapping으로 변경); 파일 s606.
- `AFR/…/contract/response/validate_citations_response.py::ValidateCitationsResponse: TypeAlias` — private dataclass 2개의 exact union; valid variant `{kind: Literal["citations_valid"], bundle_id: str, evidence_set_digest: str, validated_citation_count: int(>0)}` s309; blocked variant `{kind: Literal["blocked"], reason: Literal["invalid_citation"], bundle_id: str, evidence_set_digest: str, trace: _CitationTrace}` s310; private `_CitationTrace{stage: Literal["citation"], target_count/completed_target_count/failed_target_count: int, failure_refs: tuple[str, ...]}` s311 — s307~s311; 파일 s609.
- `AFR/…/contract/response/get_cited_answer_schema_response.py::GetCitedAnswerSchemaResponse[T]`
  `{output_type: type[T]}` (sole field, required/non-null/no default; Pydantic/framework import 0) — s240; 파일 s610.

### framework owner

- `framework/pydantic/cited_answer_schema.py::CitedAnswerSchema` (Pydantic v2 `BaseModel`; `cited-answer-v1` 1.1.0 exact 동치) — s67·s340; 유일 공개 model, nested `_SourceLocationSchema`/`_EvidenceSourceSchema`/`_AllowedEvidenceSchema`·`_NonEmptyString: _TypeAlias` underscore-private — s340~s342; 필드 계약: answer non-empty·citations minItems=1(s349), CAS 4필드/소스/로케이션 s344~s347.

### domain_layer — value objects (파일 매핑 s810~s812 문면; 개별 필드는 성문 시만 병기)

- s810: `pillar_view.py::PillarView`, `four_pillars_projection.py::FourPillarsProjection`, `major_fortune_projection.py::MajorFortuneProjection`, `pre_major_fortune_projection.py::PreMajorFortuneProjection`, `annual_fortune_projection.py::AnnualFortuneProjection`, `table_ref_projection.py::TableRefProjection`, `calculation_trace_projection.py::CalculationTraceProjection`, `calculation_projection.py::CalculationProjection`, `calculation_output_contract_mismatch.py::CalculationOutputContractMismatch` — «각각 동명 snake_case VO 파일 하나에만 공개»; nested exact fields는 §3.3 표 s211~s218.
- s811: `invalid_reading_request.py::InvalidReadingRequest`, `book_usage_policy.py::BookUsagePolicy`, `work_rag_ref.py::WorkRagRef`, `reading_character.py::ReadingCharacter`, `reading_request.py::ReadingRequest`, `retrieval_contract_ref.py::RetrievalContractRef`, `rag_release_ref.py::RagReleaseRef`(P2: `language: str` 추가 — s873), `available_retrieval_entry.py::AvailableRetrievalEntry`, `reading_constraints.py::ReadingConstraints{calculation_required_fortune_refs: frozenset[str]}`(s876~s878), `pinned_reading_bundle.py::PinnedReadingBundle{bundle_id: str, constraints: ReadingConstraints, rag_release_refs: tuple[RagReleaseRef, ...], glossary_refs: tuple[tuple[str, str, str], ...], available_entries: tuple[AvailableRetrievalEntry, ...]}` + `create(cls, *, bundle_id, requested_bundle_ref, rag_release_refs, glossary_refs, integration_scope_refs: ReadingConstraints, available_entries) -> PinnedReadingBundle`(s881~s899), `retrieval_target.py::RetrievalTarget`(P2: `target_language: str` — s873), `retrieval_plan.py::RetrievalPlan`, `bundle_selection_mismatch.py::BundleSelectionMismatch`.
- s811(outcome VO): `translation_term_set.py::TranslationTermSet`, `translation_call_trace.py::TranslationCallTrace`, `translation_call_outcome.py::TranslationCallOutcome{term_sets: tuple[TranslationTermSet, ...], trace: TranslationCallTrace}`(s108), `translation_disposition.py::TranslationDisposition{kind: TranslationDispositionKind}`(s108), `retrieval_target_trace.py::RetrievalTargetTrace`, `retrieval_target_outcome.py::RetrievalTargetOutcome{state: RetrievalTargetState, retrieved_evidence: tuple[RetrievedEvidence, ...], trace: RetrievalTargetTrace}`(s109), `retrieval_disposition.py::RetrievalDisposition{kind: RetrievalDispositionKind}`(s110).
- closed-state enum 3파일 (s811, s108~s110, s72 결정 C — direct `from enum import StrEnum`):
  - `translation_disposition_kind.py::TranslationDispositionKind(StrEnum)` `{TRANSLATED="translated", NO_EVIDENCE="no_evidence"}`
  - `retrieval_target_state.py::RetrievalTargetState(StrEnum)` `{HEALTHY="healthy", DEGRADED="degraded", FAILED="failed"}`
  - `retrieval_disposition_kind.py::RetrievalDispositionKind(StrEnum)` `{EVIDENCE_AVAILABLE="evidence_available", NO_EVIDENCE="no_evidence", TEMPORARY_FAILURE="temporary_failure"}`
- s812: `source_location.py::SourceLocation`, `evidence_source.py::EvidenceSource`, `allowed_evidence.py::AllowedEvidence`, `evidence_digest_conflict.py::EvidenceDigestConflict`, `evidence_set.py::EvidenceSet{items: tuple[DigestedAllowedEvidence, ...], groupings: tuple[EvidenceGrouping, ...], excluded_previous_evidence_count: int}`(s113), `evidence_grouping.py::EvidenceGrouping{evidence_digest: AllowedEvidenceDigest, work_id: str, rag_id: str, source_evidence_id: str | None}`(s112), `allowed_evidence_digest.py::AllowedEvidenceDigest`(+`create(value: str)` s118), `evidence_set_digest.py::EvidenceSetDigest`(+`create(value: str)` s118), `digested_allowed_evidence.py::DigestedAllowedEvidence{evidence: AllowedEvidence, digest: AllowedEvidenceDigest}`(s111), `retrieved_evidence.py::RetrievedEvidence{digested_evidence: DigestedAllowedEvidence, work_id: str, rag_id: str, source_evidence_id: str | None}`(s111), `evidence_set_view.py::EvidenceSetView`, `evidence_group_view.py::EvidenceGroupView`, `evidence_crosswalk_view.py::EvidenceCrosswalkView`, `reading_method_view.py::ReadingMethodView`, `evidence_bundle.py::EvidenceBundle`, `abstention_reason.py::AbstentionReason`, `abstained.py::Abstained`, `invalid_citation.py::InvalidCitation`, `citation_validation.py::CitationValidation`.

### domain_layer — stateless rules (s813 문면 exact)

- `domain_service/validate_calculation_output.py::CalculationOutputContract` — s810/s813; 검증 계약 s105.
- `domain_service/apply_reading_request_policy.py::ReadingRequestPolicyService` — `validate_calculation_requirement(request, pinned_constraints, calculation_projection)`, `validate_question_limit(request, retrieval_plan)` s104.
- `domain_service/plan_retrieval.py::RetrievalPlanningService` — s107.
- `domain_service/classify_translation_outcome.py::TranslationOutcomePolicy` — `classify(*, outcomes: tuple[TranslationCallOutcome, ...]) -> TranslationDisposition` s108.
- `domain_service/fold_retrieval_outcome.py::RetrievalOutcomePolicy` — `fold(*, outcomes: tuple[RetrievalTargetOutcome, ...]) -> RetrievalDisposition` s110/s326.
- `domain_service/assemble_evidence.py::EvidenceAssemblyService` — `select_evidence(*, retrieved_evidence, previous_evidence, current_release_ids: frozenset[str]) -> EvidenceSet` s114; `assemble(*, selected_evidence, evidence_set_digest, bundle_id, request, calculation_projection, translation_traces, retrieval_traces) -> EvidenceBundle` s115.
- `domain_service/validate_citations.py::CitationGate` — `validate(citations: tuple[DigestedAllowedEvidence, ...], allowed_evidence: tuple[DigestedAllowedEvidence, ...]) -> CitationValidation` s359; s813.

### application_layer — port·operation (P2 exact 계약 코드 블록)

- `AFR/application_layer/port/reading_bundle/reading_bundle_in.py::ReadingBundleIn` `{requested_bundle_ref: str | None}` — s849~s852.
- `…/reading_bundle/pinned_reading_bundle_out.py::PinnedReadingBundleOut` `{bundle_id: str, rag_release_refs: tuple[tuple[str, str, str], ...], glossary_refs: tuple[tuple[str, str, str], ...], calculation_required_fortune_refs: tuple[str, ...], available_entries: tuple[tuple[str, str, str, str, str, int], ...]}` — s855~s862 (원소 의미 s871).
- `…/reading_bundle/reading_bundle_port.py::ReadingBundlePort(ABC)` — `pin(request: ReadingBundleIn) -> PinnedReadingBundleOut` — s865~s868; s814.
- `…/query_translation/translate_query_in.py::TranslateQueryIn` `{question, query_language, target_language, glossary_id, glossary_version, glossary_digest: 전부 str}` — s938~s946.
- `…/query_translation/translated_query_out.py::TranslatedQueryOut` `{target_language: str, query_terms_by_language: tuple[tuple[str, tuple[str, ...]], ...], glossary_ref: tuple[str, str, str], dictionary_matches: …, llm_concepts: …, discarded_llm_concepts: tuple[str, ...], llm_status: Literal["ok","failed","timeout"], unregistered_language: bool}` — s949~s963 (원소 의미 s972).
- `…/query_translation/query_translation_port.py::QueryTranslationPort(ABC)` — `translate(query: TranslateQueryIn) -> TranslatedQueryOut` — s966~s969.
- `…/query_translation/invalid_translation_request.py::InvalidTranslationRequest(ValueError)` — s990~s992.
- `…/query_translation/translation_contract_mismatch.py::TranslationContractMismatch(RuntimeError)` — s995~s997.
- `…/evidence_retrieval/evidence_retrieval_port.py::EvidenceRetrievalPort` — s814 (메서드 시그니처 문면 부재).
- `…/evidence_digest/evidence_digest_port.py::EvidenceDigestPort(ABC)` — `digest_item(self, item: EvidenceDigestIn) -> str`, `digest_set(self, items: tuple[EvidenceDigestIn, ...]) -> str` — s118; s814.
- `…/evidence_digest/evidence_digest_in.py::EvidenceDigestIn{evidence_id, exact_quote, release_id, source}`, `…/evidence_source_in.py::EvidenceSourceIn{source_url, source_locations}`, `…/source_location_in.py::SourceLocationIn{location_id, provider, provider_book_id, provider_chapter_id, provider_paragraph_id, page_nums, source_url}` — s118·s815 «각각 하나씩 공개».
- `AFR/application_layer/evidence_provisioning/prepare_fortune_evidence/prepare_fortune_evidence_command.py::PrepareFortuneEvidenceCommand` `{request: ReadingRequest}` — s1003~s1006.
- `…/prepare_fortune_evidence_result.py::PrepareFortuneEvidenceResult` `{provision: EvidenceBundle | Abstained}` — s1009~s1012 (s199).
- `…/prepare_fortune_evidence_use_case.py::PrepareFortuneEvidenceUseCase` — `__init__(*, reading_bundle_port: ReadingBundlePort, query_translation_port: QueryTranslationPort, continue_translated_retrieval: _ContinueTranslatedRetrieval)`; `execute(command: PrepareFortuneEvidenceCommand) -> PrepareFortuneEvidenceResult`; module-private `_ContinueTranslatedRetrieval(Protocol)`(P2-only seam, P3에서 ref 0 제거 — s1061) — s1015~s1056.
- `…/validate_citations/validate_citations_use_case.py::ValidateCitationsUseCase` — s1246 (FR-1 행; 시그니처 문면 부재).

### driven_layer — adapters (s814 pairing 문면)

- `AFR/driven_layer/adapter/reading_bundle/rag_runtime_adapter.py::RagRuntimeReadingBundleAdapter(ReadingBundlePort)` — `__init__(*, repository_root: Path, data_root: Path, load_json_object: _JsonObjectLoader, validate_terminal_active_service_bundle: _TerminalActiveBundleValidator)`; `pin(request: ReadingBundleIn) -> PinnedReadingBundleOut`; module-private `_JsonObjectLoader(Protocol)`, `_TerminalActiveBundleValidator(Protocol)` — s904~s933.
- `AFR/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py::RagRuntimeEvidenceRetrievalAdapter` — s320 «유일 mismatch owner», s814. (b5392f0의 `HybridRetrievalAdapter` 개명.)
- `AFR/driven_layer/adapter/evidence_digest/rfc8785_adapter.py::Rfc8785EvidenceDigestAdapter` — `rfc8785.dumps(...)` canonical bytes + `hashlib.sha256(...).hexdigest()` 단독 소유 — s118; s814.
- `AFR/driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py::QueryTranslationAdapter(QueryTranslationPort)` — `__init__(*, translate_command: _TranslateCommand)`; `translate(query) -> TranslatedQueryOut`; private `_TranslateCommand(Protocol)` — s974~s985.
- `AFR/driven_layer/django_fortune_reading/apps.py::FortuneReadingConfig` `{default_auto_field: str = "django.db.models.BigAutoField", name: str = "application.fortune_reading.driven_layer.django_fortune_reading", label: str = "fortune_reading"}` + 첫 statement docstring `"""fortune_reading Django 애플리케이션 설정."""` — s1069 (base 문면 부재).

### API·기타

- `AFR/driving_layer/api/bc_error_schema.py::FortuneReadingErrorCode(StrEnum)` `{INVALID_REQUEST…RESOURCE_LIMIT}` — s477~s485; s473 «단독 소유».
- `…/bc_error_schema.py::FortuneReadingErrorSchema(FrameworkErrorSchema)` {error: FortuneReadingErrorCode} — s494~s495; concrete 4종 `InvalidRequestErrorSchema/RegistryContractMismatchErrorSchema/TemporaryErrorSchema/ResourceLimitErrorSchema(FortuneReadingErrorSchema)` (각 error/message default) — s497~s511.
- `AFR/driving_layer/api/evidence/schema/schema_in.py::PrepareFortuneEvidenceRequestSchema` — 심볼 s135; 파일 s578 «HTTP request owner» (결합 재량 약간 — 자백).
- `AFR/driving_layer/api/evidence/schema/schema_out.py::EvidenceProvisionResponseSchema` — 심볼 s199; 파일 s579+s816 «`schema_out.py`도 nested models를 private로» (재량).
- `AFR/test/e2e/typecheck_citation_ohs_consumer.py::validate_generated_citations(...)` — 전체 exact source 성문 — s253~s301.
- `framework/technology/rag/runtime/rag_builder/_contracts.py::Embedder` — s1092·s1616.
- `framework/technology/rag/runtime/views.py::yeonhae_japyeong_evidence` — s1643 [L3 제거 대상].
- 파일 미명시: `register_fortune_reading_api(api)` (s433; registrar 호출처 urls.py s406/s1083), `CACHE_CONTROL_HEADER: dict[str, object]` 상수(s536), port DTO `RetrievalTargetResultOut`(s324 — retrieval_result_out.py 명명 유사하나 문면 결합 부재), wire variants `EvidencePrepared/Abstained/EvidenceProvisionBlocked`(s203~s205 — response 파일 private 구성이라는 s238 언명만).
- 역방향 부재: `evidence_retrieval_port.py`의 메서드, `retrieval_result_out.py`/`retrieval_request_in.py`/`reading_bundle_in.py`(→ ReadingBundleIn은 성문됨)/command·query 파일 일부(`prepare_fortune_evidence_query.py`는 s531 «OHS schema-query `PrepareFortuneEvidenceQuery`는 HTTP controller 입력 타입이 아니다»로 심볼명만 등장), published_error 2파일 심볼 부재.

---

## 블록 3 — boundary-imports

| 소비 파일 | import 대상 모듈 | provenance |
|---|---|---|
| `AFR/driving_layer/api/bc_error_schema.py` | `framework/ninja/framework_error_schema.py` (공통 class import·상속) | s465 «공통 class를 import하고», s469, s494 |
| `spring_dream_server/urls.py` | fortune_reading registrar 모듈(경로 미명시; `register_fortune_reading_api(api)` 호출) | s1083, s433, s406 |
| `AFR/…/citation_validation_service.py` | `framework/pydantic/cited_answer_schema.py::CitedAnswerSchema` | s240 «service module이 …를 import해», s313 «framework owner를 직접 사용» |
| `AFR/test/e2e/typecheck_citation_ohs_consumer.py` | `application.fortune_reading…citation_validation_service`(2심볼) · `…validate_citations_request` · `…validate_citations_response` · **타 BC** `application.llm_access…generation_service` · `…generate_structured_request` · `…generate_text_request`(2심볼) — exact 7 `ImportFrom`/9 names | s242~s249, 코드 s256~s275 |
| composition root(파일 미명시) | `ontology_canonical.load_json_object` · `ontology_service.validate_terminal_active_service_bundle` 명시 주입 | s935 |
| composition root(파일 미명시) | 타 BC `query_translation...translation_service.translate_command` 명시 주입 | s987 |
| `framework/technology/rag/runtime/ontology_c11.py` | `framework/technology/rag/runtime/service_runtime.py` | s1090 |
| `framework/technology/rag/runtime/ontology_service.py` | `service_runtime.py` (제품 consumption helper 전환) | s1629 |
| `ontology_c11.py` · `rag_builder/index.py` · `rag_builder/steps/__init__.py` | `rag_builder/_contracts.py` (`Embedder`) | s1616 |
| `AFR/driven_layer/adapter/evidence_retrieval/rag_runtime_adapter.py` | common `search_hybrid_index` (소유 모듈 문면 미명시) | s1591 «새 adapter는 common `search_hybrid_index`를 호출» |
| P3 산출물(소비 파일 문면 미명시) | `rag_builder.index` re-export `Embedder` | s1592 |
| `AFR/driven_layer/adapter/anticorruption_layer/query_translation/query_translation_adapter.py` | 타 BC query_translation published OHS (`TranslateRequest`/`TranslateResponse`/`GlossaryReferenceData`, published exceptions 6종) | s127, s978, s987 |

참고(범주 밖·명면 성문된 서드파티 — 자백 11):
- `framework/pydantic/cited_answer_schema.py` → pydantic underscore aliases(`_BaseModel`·`_ConfigDict`·`_Field`·`_StringConstraints`·`_Annotated`·`_TypeAlias`) + exact `from pydantic.experimental.missing_sentinel import MISSING as _MISSING` — s342.
- `AFR/driven_layer/adapter/evidence_digest/rfc8785_adapter.py` → `rfc8785`(dumps)·`hashlib`(sha256) — s118, s351.

```text
# 금지 명시(참고)
- domain outward import 0 · domain `rfc8785` direct import 0 · domain→framework/application import 0   # s118, s846
- contract/의 Pydantic/framework import·re-export 0                                                     # s313, s816, s1117
- OHS service→API sibling import 0 · composition-root→driving 0                                        # s313, s67
- consumer source import는 fortune_reading OHS + llm_access OHS로 닫힘; framework/API 직접 import 0     # s129, s251
- unit→test/factories/acceptance fixture import 0                                                      # s1832(#388), s1273
- T01은 actual fortune_calculation OHS response dataclass import 0 (owner-local Mapping fixture)        # s393
- `ontology_c11.py` private function import 금지                                                        # s321
- BC-module-origin `StrEnum` consumer import/re-export/`__all__` workaround 0                            # s72, s811
- fortune_catalog/fortune_character private import 0 · LLM provider/SPARQL/개별 active.json read 0      # s126, s1662, s1703
- framework가 application BC 역-import 0                                                                # s1629
- `hybrid_retrieval` 직접 참조 신규 증가 0                                                              # s1592
```

---

## 블록 4 — physical-signals

add 23행(T01~T22, T28)·update 0 (s1533~s1534). §8 전제: «DB lens가 비활성이므로 concrete
DB-backed integration test는 0 … DB 신호를 가장한 marker/fixture를 추가하지 않는다»(s1266).
새 테스트의 DB 마커·베이스 클래스·client 사용 문면 전무 → 전건 «부재». 일부 행은 «DB 신호 0»을
명시적으로 성문(값으로 부기).

| row | 테스트 경로 | markers | base | client | provenance |
|---|---|---|---|---|---|
| T01 | `AFR/test/unit/test_calculation_output_contract.py` | 부재 («DB 신호 0» 명시) | 부재 | 부재 | s1272 |
| T02 | `AFR/test/unit/test_reading_request.py`, `test_reading_request_policy_service.py` | 부재 | 부재 | 부재 | s1273 |
| T03 | `AFR/test/unit/test_retrieval_planning_service.py` | 부재 | 부재 | 부재 | s1274 |
| T04 | `AFR/test/unit/test_retrieval_planning_service.py` | 부재 | 부재 | 부재 | s1275 |
| T05 | `AFR/test/unit/test_evidence_assembly_service.py` | 부재 | 부재 | 부재 | s1276 |
| T06 | `AFR/test/unit/test_allowed_evidence.py` | 부재 | 부재 | 부재 | s1277 |
| T07 | `AFR/test/unit/test_evidence_assembly_service.py` | 부재 | 부재 | 부재 | s1278 |
| T08 | `AFR/test/unit/test_citation_gate.py` | 부재 | 부재 | 부재 | s1279 |
| T09 | `AFR/test/unit/test_cited_answer_schema_equivalence.py` | 부재 («DB 신호 0» 명시) | 부재 | 부재 | s1280 |
| T10 | `AFR/test/unit/test_rag_runtime_reading_bundle_adapter.py` + `test_prepare_fortune_evidence_use_case.py` | 부재 («DB 신호 0» 명시) | 부재 | 부재 | s1281 |
| T11 | `AFR/test/unit/test_query_translation_adapter.py` + `test_prepare_fortune_evidence_use_case.py` + `test_translation_outcome_policy.py` | 부재 | 부재 | 부재 | s1282 |
| T12 | `AFR/test/unit/test_rag_runtime_evidence_retrieval_adapter.py` | 부재 | 부재 | 부재 | s1283 |
| T13 | `AFR/test/unit/test_rag_runtime_evidence_retrieval_adapter.py` + `test_retrieval_outcome_policy.py` | 부재 | 부재 | 부재 | s1284 |
| T14 | `AFR/test/e2e/test_active_bundle_matrix.py` | 부재 | 부재 | 부재 | s1285 |
| T15 | `AFR/test/e2e/test_active_bundle_matrix.py` | 부재 | 부재 | 부재 | s1286 |
| T16 | `AFR/test/e2e/test_crosswalk_candidate_bundle.py` | 부재 | 부재 | 부재 | s1287 |
| T17 | `AFR/test/e2e/test_open_host_services.py` | 부재 | 부재 | 부재 | s1288 |
| T18 | `AFR/test/e2e/test_open_host_services.py` + non-pytest `typecheck_citation_ohs_consumer.py` | 부재 | 부재 | 부재 | s1289 |
| T19 | `AFR/test/e2e/test_evidence_api.py` | 부재 | 부재 | 부재 | s1290 |
| T20 | `AFR/test/e2e/test_evidence_openapi.py` | 부재 | 부재 | 부재 | s1291 |
| T21 | `AFR/test/e2e/test_evidence_provider_boundaries.py` | 부재 | 부재 | 부재 | s1292 |
| T22 | `AFR/test/e2e/test_evidence_bundle.py` | 부재 | 부재 | 부재 | s1293 |
| T28 | `AFR/test/unit/test_rfc8785_adapter.py` | 부재 | 부재 | 부재 | s1299 |

---

## 블록 5 — exception-map

### 5a. 정의·소유 파일 (s1671 — 전건 문면 명시; b5392f0 대비 소유 파일 재배치)

| published 예외 | raise 창구(파일) — 소유 경로 | provenance |
|---|---|---|
| `InvalidReadingRequest` | `AFR/domain_layer/shared_value_object/invalid_reading_request.py` | s1671 |
| `CalculationOutputContractMismatch` | `AFR/domain_layer/shared_value_object/calculation_output_contract_mismatch.py` | s1671 |
| `BundleSelectionMismatch` | `AFR/domain_layer/shared_value_object/bundle_selection_mismatch.py` | s1671 |
| `EvidenceDigestConflict` | `AFR/domain_layer/shared_value_object/evidence_digest_conflict.py` | s1671 (신설 예외) |
| `InvalidCitation` | `AFR/domain_layer/shared_value_object/invalid_citation.py` | s1671 (b5392f0의 citation_gate.py에서 이동) |
| `ReadingBundleContractMismatch` | `AFR/application_layer/port/reading_bundle/exception.py` | s1671 |
| `InvalidTranslationRequest` | `AFR/application_layer/port/query_translation/invalid_translation_request.py` (sole public) | s1671, s990 |
| `TranslationContractMismatch` | `AFR/application_layer/port/query_translation/translation_contract_mismatch.py` (sole public) | s1671, s995 |
| `RetrievalContractMismatch` | `AFR/application_layer/port/evidence_retrieval/exception.py` | s1671 |
| `RetrievalTemporaryFailure` | `AFR/application_layer/port/evidence_retrieval/exception.py` | s1671 |
| `RetrievalResourceLimit` | `AFR/application_layer/port/evidence_retrieval/exception.py` | s1671 |
| digest adapter normalization failure (예외 심볼명 문면 부재) | `AFR/application_layer/port/evidence_digest/exception.py` | s1671 «digest adapter normalization failure만 … 소유» |
| (private) `_CitationSchemaInvalid` | `AFR/driving_layer/open_host_service/citation_validation/citation_validation_service.py` | s1671, s305 |

### 5b. raise 주체 (§10 표 s1675~s1697 + §5.10 s520~s523)

| published 예외/결과 | raise 주체(문면) | provenance |
|---|---|---|
| `InvalidReadingRequest` | `ReadingRequest`(s1675); `ReadingRequestPolicyService.validate_calculation_requirement`(plan 전, s1676); `.validate_question_limit`(non-empty plan 뒤, s1677) | s1675~s1677 |
| `CalculationOutputContractMismatch` | `CalculationOutputContract`(fortune 분류 전) | s1678 |
| `BundleSelectionMismatch` | `PinnedReadingBundle.create` domain invariant | s1679 |
| `ReadingBundleContractMismatch` | `driven_layer/adapter/reading_bundle/rag_runtime_adapter.py::RagRuntimeReadingBundleAdapter` (terminal admission/digest/ref failure; `ServiceActivationError` 등 raw 오류 번역 포함) | s1680, s935 |
| `InvalidTranslationRequest` / `TranslationContractMismatch` | `QueryTranslationAdapter` external-contract owner (upstream published 예외 6종+malformed response 번역) | s1683, s987 |
| `RetrievalContractMismatch` | `RagRuntimeEvidenceRetrievalAdapter` external-contract owner | s1684, s1690 |
| `RetrievalTemporaryFailure` | domain `RetrievalOutcomePolicy.fold`→`TEMPORARY_FAILURE`; **application만 exception으로 조율** | s1689 |
| `RetrievalResourceLimit` | retrieval adapter (explicit memory/capacity guard) | s1691, s325 |
| `EvidenceDigestConflict` | domain `EvidenceAssemblyService.select_evidence`; application/OHS/controller가 existing `registry_contract_mismatch`(503/Blocked)로 번역 — 새 public reason 0 | s1694, s114, s521 |
| `InvalidCitation` | domain `CitationGate.validate` (schema-valid parsed membership mismatch) → OHS `Blocked(invalid_citation)` | s1696, s360 |
| `_CitationSchemaInvalid` (private) | citation OHS (schema-invalid; application/domain 호출 0; counters `0/0/0/()`) → 같은 public `Blocked(invalid_citation)` | s1695, s311, s357 |
| unexpected programming exception | framework 500, «BC schema로 은폐하지 않음» | s1697 |

HTTP mapping(§5.10): 400 tuple=`(InvalidReadingRequest, BundleSelectionMismatch, CalculationOutputContractMismatch, InvalidTranslationRequest)` s520; 503 registry tuple=`(ReadingBundleContractMismatch, TranslationContractMismatch, RetrievalContractMismatch, EvidenceDigestConflict)` s521; temporary s522; resource s523.

---

## 충돌·긴장 기록

- **충돌 1 — P2 focused review pending**: s11 «P2 executability focused amendment review PASS … pending 0 … P2 Red/Green 집행이 승인됐다» · s1546 «DDD·discipline focused review는 모두 PASS» vs s1860 «이번 P2 executability CHANGES_REQUIRED 반영분은 **pending 1**» · s1862(동일 pending 1) · s1866 «P2 amendment DDD+discipline focused re-review pending 2(각 1) … 두 focused review가 모두 PASS하기 전 P2 Red/Green을 시작하지 않는다». `# 충돌: s11·s1546행 vs s1860·s1862·s1866행` — both 전사.
- 긴장 1 — §6.2 트리(전건 «신규 파일» add, s556) vs WIP reconciliation(동일 경로 6건 retain-and-trim, s823~s829): 같은 파일이 add와 기존-수정 양쪽 서술. 두 블록 모두 전사, 태그는 각 문면대로.
- 긴장 2 — `tests/test_hybrid_retrieval.py`: s1102(무주석) vs s1617 «파일과 7 old tests를 제거» — 파일 잔존 여부 문면 불명 → update 전사.
- 집계 검산: §8.3 add 23/update 0/reuse 2/retain 14/remove 19/reject 2/pending 0=60 (s1533~s1540) ↔ 행 전수(T01~T22+T28=23, L01~L17+L30~L31=19, L18~L29+L32+T25=14, T23~T24=2, T26~T27=2) 일치. WIP 16행 closed set(s840) ↔ 표 16행 일치.

## 재량 자백 (①)

1. `__init__.py`·표준 고정 slot 제외, 단 주석 성문된 빈 슬롯(11건)은 `empty` — «0-byte empty fixed file»/«없음» 문면을 `empty` 태그의 의미로 해석.
2. §6.3 태그: delete 주석→remove, 그 외→update; `_contracts.py` «새 소유처» add/update 불명→update.
3. legacy 테스트 3파일: case-level delete만 성문 → update(파일 삭제 여부 부재).
4. WIP reconciliation 어휘 매핑: retain-and-trim→update, split-and-delete/move-and-delete/delete→remove (명세 원어를 주석에 보존).
5. 심볼 파일 결합: 이 판은 대부분 문면 명시(s809~s815, s1671, 코드 블록). 재량 결합은 `schema_in.py/schema_out.py`↔HTTP Schema 2건과 OHS request/response 파일↔`<Operation>Request/Response`(s809의 일반 규칙 적용)뿐.
6. `FortuneReadingConfig` base 미기재 — 문면 부재로 괄호 생략. `Embedder` Protocol 표기 동일.
7. physical-signals의 «DB 신호 0» 명시 행은 markers 칸에 부기 — 규범의 '값' 해석 재량.
8. exception-map 5a의 «digest adapter normalization failure»는 예외 클래스명이 문면에 없어 서술 그대로 전사(부재 표기).
9. boundary-imports: framework owner→pydantic, rfc8785_adapter→rfc8785/hashlib는 성문 범주(타 BC/framework 공통/domain·contract 서드파티/테스트→factories) 밖이라 본표 밖 «참고»로 격리.
10. composition root 주입(s935, s987)은 소비 파일이 문면 미명시(dependency_wiring.py 추정 금지)로 «파일 미명시» 표기.
11. registry gate 인라인 스크립트(s1128~s1238)와 T18 audit block(s1322~s1490)은 gate-only(permanent artifact 0 성문)라 file-plan·symbols에 비전사.
