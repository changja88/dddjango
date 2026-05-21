# Source Reference Audit Reference

이 문서는 dddjango의 source/reference governance 감사 기준을 고정한다. 목적은 source 문서, runtime skill, public validation case, evaluator-only material, run artifact가 서로의 역할을 침범하지 않게 하는 것이다.

## 1. Artifact Roles

| 역할 | 예시 위치 | 허용되는 용도 | 금지되는 용도 |
|---|---|---|---|
| Source authoring | `workspace/reference/**` | 제품 결정, 설계 기준, source evidence, reference basis | runtime-facing allowed path로 제시, run 결과를 근거 없이 source truth로 승격 |
| Runtime skill | `dddjango/skills/**/SKILL.md`, `dddjango/skills/**/references/**`, `agents/openai.yaml` | 에이전트 실행 절차, runtime bundle-relative reference, skill-local guidance | source authoring 경로를 최종 runtime instruction으로 노출, private evaluation material 복사 |
| Public case/prompt | `workspace/develop/eval/*/cases/plugin/public/**`, public prompt input | 사용자에게 공개 가능한 task context, scenario label, validation conditions | evaluator-only material, non-public validation notes, prior run output, scoring notes |
| Evaluator-only material | `workspace/develop/eval/*/answer/**`, private checks, scoring notes | scoring decision, internal checks, traceability from public case to source basis | runtime/public/source wording으로 역류, public prompt에 field/schema 용어 노출 |
| Run artifact | `workspace/develop/eval/*/runs/**` | execution evidence, observed outputs, reportable diagnostics | source truth, runtime reference, future public answer의 정답 근거 |

## 2. Reference Material Precedence

Source reference 감사는 `final.md`를 기본 decision source로 삼는다. `review.md`, `internal.md`, `external.md`는 `final.md`가 모호하거나 source gap, conflict, provisional/fallback status를 판단해야 할 때 consulted evidence로 읽는다.

`workspace/reference/source-reference-audit/reference/`의 현재 source decision은 이 `final.md` 하나다. 이 area에 `review.md`, `internal.md`, `external.md`가 없으면 감사 결과에는 `not present` 또는 `not provided`로 적고, 존재하지 않는 material을 검토했다고 쓰지 않는다. Supplemental material 부재는 그 자체로 conflict-free 또는 complete coverage의 증거가 아니다.

다른 reference area를 감사할 때는 다음 순서를 따른다.

1. 해당 area의 `reference/final.md`가 있는지 확인한다.
2. `final.md`가 있으면 dedicated source reference 후보로 보고, 그 문서가 해당 skill의 범위와 결정을 실제로 다루는지 확인한다.
3. `review.md`, `internal.md`, `external.md`가 있으면 conflict, gap, unresolved decision, source provenance를 item-level로 대조한다.
4. `final.md`가 없거나 범위가 부족하면 open gap 또는 provisional/fallback으로 표시한다.
5. 읽지 않은 material은 `not run`, 없던 material은 `not present`, 제공되지 않은 외부 자료는 `not provided`로 구분한다.

## 3. Path Boundary Decisions

| 표면 | Source authoring path | Runtime bundle path | Eval/private path | Run path |
|---|---|---|---|---|
| Source audit answer | source evidence로 허용 | 비교 대상으로 허용 | 명시적으로 내부 eval-pack을 검토할 때만 허용 | 실행 증거로만 허용 |
| Runtime-facing guidance | 금지 | 허용 | 금지 | 금지 |
| Public case/prompt | 일반 사용자 맥락에 필요한 경우만 허용 | 일반 사용자 맥락에 필요한 경우만 허용 | 금지 | 금지 |
| Evaluator-only material | source basis로 허용 | 비교 대상으로 허용 | 허용 | 현재 평가 증거로만 허용 |
| Report/run analysis | 증거로 허용 | 증거로 허용 | evaluator-only report 안에서 허용 | 현재 run 내부 증거로 허용 |

Runtime-facing guidance는 skill-local 또는 runtime bundle-relative 형태를 사용한다. `workspace/reference/**`는 source evidence, source-authoring, cache/source parity, internal eval work에만 둔다.

## 4. Source Provenance And Crosswalk

Source provenance 감사는 runtime skill이나 bundled reference가 어떤 source decision을 반영하는지 추적한다. 최소 crosswalk row는 다음 evidence를 포함한다.

| Evidence | Required content |
|---|---|
| Source basis | `workspace/reference/<area>/reference/final.md` 또는 consulted `review/internal/external` material과 그 문서가 증명하는 decision |
| Runtime surface | `dddjango/skills/<skill>/SKILL.md`, `dddjango/skills/<skill>/references/*.md`, `agents/openai.yaml`, runtime cache 비교 대상 |
| Decision mapping | source decision이 runtime instruction, bundled reference, metadata trigger에 어떻게 반영됐는지 |
| Status | dedicated source, resolved conflict, open gap, provisional/fallback, out of scope, needs source decision |
| Allowed claim | 현재 source와 runtime evidence로 말할 수 있는 claim |
| Forbidden claim | source가 부족하거나 runtime이 반영하지 않아 말하면 안 되는 claim |
| Expected evidence | validation command, source diff, cache diff, review report, eval run artifact, manual crosswalk 중 필요한 증거 |

문서 이름만 나열하는 것은 provenance evidence가 아니다. 각 row는 그 문서가 어떤 decision을 증명하는지 적어야 한다.

## 5. Dedicated Source, Gap, And Provisional Status

Dedicated source reference는 해당 area의 `reference/final.md`가 존재하고, skill의 주요 판단 축을 source decision으로 다룰 때만 인정한다. 파일 존재만으로 dedicated-source-complete라고 판정하지 않는다.

다음은 open gap 또는 provisional/fallback으로 표시한다.

- `reference/final.md`가 없다.
- `final.md`가 있지만 해당 skill의 주요 routing, invariant, API/DB/runtime boundary, validation expectation을 다루지 않는다.
- `review.md`, `internal.md`, `external.md`에 unresolved conflict가 있고 `final.md`가 decision을 내리지 않았다.
- runtime skill이나 bundled reference가 source decision보다 강한 claim을 한다.
- eval oracle이나 run artifact만 있고 source decision이 없다.

Provisional/fallback row는 반드시 현재 allowed claim과 forbidden claim을 적는다. 예를 들어 “fallback 근거로 제한된 범위의 감사만 가능하다”는 allowed claim이 될 수 있지만, “dedicated source가 완성됐다”는 forbidden claim이다.

## 6. DRF Guardrail Source Decision

DRF guardrail 감사는 source-reference-audit area가 소유하는 governance decision이다. 실제 API 구현 기준은 `architecture-api`, `implementation-django-ninja`, `implementation-django` reference가 소유하지만, source audit은 아래 traceability를 확인해야 한다.

| Guardrail item | Source evidence | Audit decision |
|---|---|---|
| Greenfield REST API 구현 기본 목표 | `workspace/reference/implementation-django-ninja/reference/final.md` | 신규 `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`, `rest_framework` 구현 요청은 명시적 legacy/migration 문맥이 없으면 Django Ninja 구현으로 전환해야 한다. |
| API 계약 설계 | `workspace/reference/architecture-api/reference/final.md` | REST resource, method, status, error, pagination, versioning, idempotency는 framework-neutral API contract로 먼저 다룬다. |
| 기존 DRF 유지보수 | `workspace/reference/implementation-django/reference/final.md` | DRF 자료는 existing DRF maintenance, legacy migration review, compatibility comparison, 이미 DRF를 표준으로 채택한 프로젝트 안에서만 보조 근거로 사용한다. |
| Runtime routing | `dddjango/skills/implementation-django-ninja/SKILL.md`, `dddjango/skills/implementation-django/SKILL.md`, `dddjango/skills/architecture-api/SKILL.md` | runtime skill metadata와 routing이 greenfield DRF를 기본 권장하지 않는지 확인한다. |

허용 claim:

- DRF guardrail은 source audit에서 별도 row로 검증해야 한다.
- DRF는 legacy/migration/comparison 문맥에서만 보조 근거로 사용할 수 있다.
- greenfield API standard는 Django Ninja 구현과 framework-neutral API contract 기준으로 분리해 확인한다.

금지 claim:

- DRF runtime reference나 legacy 문서를 greenfield API implementation standard로 사용한다.
- eval oracle이나 previous run 결과만으로 DRF guardrail source decision을 대체한다.
- DRF guardrail과 provisional source gap을 한 row로 뭉개서 어느 source가 무엇을 증명하는지 숨긴다.

## 7. Runtime Metadata And Cache Sync

Runtime metadata 감사는 `SKILL.md` 존재와 `agents/openai.yaml` 존재만으로 완료하지 않는다. 다음을 함께 확인한다.

- frontmatter `description`이 trigger vocabulary, scope, negative routing을 충분히 포함하는지
- `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 skill 목적과 충돌하지 않는지
- default prompt가 private evaluation material, internal criteria, non-public validation notes를 노출하지 않는지
- source skill과 runtime cache가 `diff` 또는 `cmp` 기준으로 일치하는지
- validation command output과 manual semantic review 중 무엇을 실행했는지

Runtime cache path는 source/runtime parity evidence로만 보고한다. Runtime-facing guidance나 public prompt에는 physical cache path를 allowed runtime reference처럼 제시하지 않는다.

## 8. Leakage Categories

Public/runtime/source-facing material에는 다음 범주를 직접 복사하지 않는다.

- private evaluation material
- internal criteria
- non-public validation notes
- private sentinel/token
- answer-only schema field names
- prior run output or conclusion
- scoring notes
- local absolute paths, temporary workspace paths, runtime cache physical paths

필요한 경우 정확한 내부 문자열 대신 `[private-eval-sentinel]`, `[internal-criteria]`, `[non-public-validation-note]` 같은 redacted placeholder나 제품-facing 범주를 사용한다.

## 9. Run Artifact Status

Run artifact는 “무슨 일이 실행되었는지”의 증거다. Run artifact는 source decision을 대체하지 않는다.

- 사용 가능: command evidence, exit status, raw output, report artifact, observed leakage finding.
- 사용 불가: source basis, runtime bundled reference, public case 정답, future eval expected answer.
- 이전 run 결과를 새 source 문서나 runtime skill에 반영하려면, 먼저 source reference나 product doc decision으로 일반화해야 한다.

## 10. Boundary Scan Evidence Contract

Boundary/leakage 감사는 다음 evidence를 분리해서 보고한다.

| Evidence | Required content |
|---|---|
| Review scope | 감사한 surface와 제외한 surface |
| Inspected surfaces | repo-relative artifact paths, commands, reports, or provided logs actually checked |
| Not-run surfaces | `not run` 또는 `not provided`로 표시하고 결론을 추정하지 않음 |
| Forbidden-category scan | private evaluation material, internal criteria, non-public validation notes, local path, run-as-source patterns |
| Path decision | source-authoring path와 runtime bundle-relative path를 context별로 구분 |
| Unsupported claim check | 실행하지 않은 command, scan, subagent, file inspection claim이 없는지 확인 |

## 11. Public Wording Rules

Public-facing 답변은 내부 eval-pack 용어를 사용자-facing 용어로 바꾼다.

| Internal concept | Public-facing wording |
|---|---|
| evaluator-only answer/oracle | private evaluation material |
| scoring note/check | internal criteria |
| private traceability field | source evidence or review scope |
| hidden validation string | non-public validation note |
| exact sentinel/token | redacted placeholder |

내부 eval-pack 파일 자체를 명시적으로 리뷰하는 요청에서는 내부 field name을 사용할 수 있다. 그 외 boundary/leakage 답변에서는 public-facing wording을 기본으로 한다.

## 12. Eval Traceability

Eval traceability 감사는 public case, evaluator-only answer, source basis, coverage label, leakage boundary가 같은 case 단위로 이어지는지 확인한다. Internal eval-pack을 명시적으로 검토하는 요청에서만 private answer path와 field name을 그대로 다룬다.

최소 traceability evidence:

- public case path와 사용자-facing task context
- answer oracle path와 `case_id`
- `reference_basis`가 가리키는 source 문서와 그 basis 설명
- `coverage_tags`가 source eval goal의 scenario label과 맞는지
- required checks, forbidden behavior, leakage checks
- run artifact 또는 manual review output이 있다면 해당 case와 연결되어 있는지

Public case에는 private answer material, scoring note, hidden validation string을 넣지 않는다. Answer oracle은 source basis를 가질 수 있지만, source reference나 runtime skill로 역류하지 않는다.

## 13. Validation Coverage Expectations

Source reference audit 산출물은 다음을 구분해야 한다.

- resolved conflict, open gap, provisional/fallback, out-of-scope status
- source evidence와 runtime evidence
- allowed claim과 forbidden claim
- expected evidence와 unrun evidence
- cache/source parity evidence와 runtime-facing guidance

검증을 실행하지 않았으면 실행하지 않았다고 적는다. validator pass만으로 모든 surface가 안전하다고 확대 해석하지 않는다.

Validation coverage 감사는 다음 first-class dimension을 확인한다.

- DDD
- implementation patterns
- DB
- API
- Django
- Django Ninja
- Django Web
- Python typing
- Clean Code
- TDD
- Test
- Workflow
- negative cases
- validation honesty
- runtime/source boundaries

Coverage matrix에는 scenario 또는 dimension, source evidence, review scope, expected evidence, gap/residual risk, negative/honesty check를 포함한다. Expected evidence는 validator, eval run artifact, source crosswalk, manual review report처럼 구체적이어야 한다.

## 14. Completion Gate

Source-reference-audit P1 또는 유사한 source governance 감사는 다음을 모두 만족해야 완료 후보가 된다.

- source reference가 material precedence, role/path boundary, provenance, source gap, provisional/fallback, DRF guardrail, leakage, validation coverage, eval traceability, runtime metadata/cache sync를 판단할 수 있다.
- skill `SKILL.md`와 `agents/openai.yaml`이 source decision과 충돌하지 않는다.
- bundled references가 있으면 source basis와 runtime-facing boundary가 분리되어 있다.
- source skill과 runtime cache sync 여부를 실제 diff 또는 cmp evidence로 확인했다.
- 실행한 validators, subagent, review, eval만 실행했다고 보고한다.
- Blocker 0, Major 0, 열린 Minor 0 상태이며, eval-pack 자체 문제는 P1에서 수정하지 않고 eval follow-up analysis로 분류한다.
