# Source Reference Audit Reference

이 문서는 dddjango의 source/reference governance 감사 기준을 고정한다. 목적은 source 문서, runtime skill, public validation case, evaluator-only material, run artifact가 서로의 역할을 침범하지 않게 하는 것이다.

## 1. Artifact Roles

| 역할 | 예시 위치 | 허용되는 용도 | 금지되는 용도 |
|---|---|---|---|
| Source authoring | `workspace/docs/**`, `workspace/reference/**` | 제품 결정, 설계 기준, source evidence, reference basis | runtime-facing allowed path로 제시, run 결과를 근거 없이 source truth로 승격 |
| Runtime skill | `dddjango/skills/**/SKILL.md`, `dddjango/skills/**/references/**`, `agents/openai.yaml` | 에이전트 실행 절차, runtime bundle-relative reference, skill-local guidance | source authoring 경로를 최종 runtime instruction으로 노출, private evaluation material 복사 |
| Public case/prompt | `workspace/develop/eval/*/cases/plugin/public/**`, public prompt input | 사용자에게 공개 가능한 task context, scenario label, validation conditions | evaluator-only material, non-public validation notes, prior run output, scoring notes |
| Evaluator-only material | `workspace/develop/eval/*/answer/**`, private checks, scoring notes | scoring decision, internal checks, traceability from public case to source basis | runtime/public/source wording으로 역류, public prompt에 field/schema 용어 노출 |
| Run artifact | `workspace/develop/eval/*/runs/**` | execution evidence, observed outputs, reportable diagnostics | source truth, runtime reference, future public answer의 정답 근거 |

## 2. Path Boundary Decisions

| 표면 | Source authoring path | Runtime bundle path | Eval/private path | Run path |
|---|---|---|---|---|
| Source audit answer | source evidence로 허용 | 비교 대상으로 허용 | 명시적으로 내부 eval-pack을 검토할 때만 허용 | 실행 증거로만 허용 |
| Runtime-facing guidance | 금지 | 허용 | 금지 | 금지 |
| Public case/prompt | 일반 사용자 맥락에 필요한 경우만 허용 | 일반 사용자 맥락에 필요한 경우만 허용 | 금지 | 금지 |
| Evaluator-only material | source basis로 허용 | 비교 대상으로 허용 | 허용 | 현재 평가 증거로만 허용 |
| Report/run analysis | 증거로 허용 | 증거로 허용 | evaluator-only report 안에서 허용 | 현재 run 내부 증거로 허용 |

Runtime-facing guidance는 skill-local 또는 runtime bundle-relative 형태를 사용한다. `workspace/docs/**`와 `workspace/reference/**`는 source evidence, source-authoring, cache/source parity, internal eval work에만 둔다.

## 3. Leakage Categories

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

## 4. Run Artifact Status

Run artifact는 “무슨 일이 실행되었는지”의 증거다. Run artifact는 source decision을 대체하지 않는다.

- 사용 가능: command evidence, exit status, raw output, report artifact, observed leakage finding.
- 사용 불가: source basis, runtime bundled reference, public case 정답, future eval expected answer.
- 이전 run 결과를 새 source 문서나 runtime skill에 반영하려면, 먼저 source reference나 product doc decision으로 일반화해야 한다.

## 5. Boundary Scan Evidence Contract

Boundary/leakage 감사는 다음 evidence를 분리해서 보고한다.

| Evidence | Required content |
|---|---|
| Review scope | 감사한 surface와 제외한 surface |
| Inspected surfaces | repo-relative artifact paths, commands, reports, or provided logs actually checked |
| Not-run surfaces | `not run` 또는 `not provided`로 표시하고 결론을 추정하지 않음 |
| Forbidden-category scan | private evaluation material, internal criteria, non-public validation notes, local path, run-as-source patterns |
| Path decision | source-authoring path와 runtime bundle-relative path를 context별로 구분 |
| Unsupported claim check | 실행하지 않은 command, scan, subagent, file inspection claim이 없는지 확인 |

## 6. Public Wording Rules

Public-facing 답변은 내부 eval-pack 용어를 사용자-facing 용어로 바꾼다.

| Internal concept | Public-facing wording |
|---|---|
| evaluator-only answer/oracle | private evaluation material |
| scoring note/check | internal criteria |
| private traceability field | source evidence or review scope |
| hidden validation string | non-public validation note |
| exact sentinel/token | redacted placeholder |

내부 eval-pack 파일 자체를 명시적으로 리뷰하는 요청에서는 내부 field name을 사용할 수 있다. 그 외 boundary/leakage 답변에서는 public-facing wording을 기본으로 한다.

## 7. Validation Expectations

Source reference audit 산출물은 다음을 구분해야 한다.

- resolved conflict, open gap, provisional/fallback, out-of-scope status
- source evidence와 runtime evidence
- allowed claim과 forbidden claim
- expected evidence와 unrun evidence
- cache/source parity evidence와 runtime-facing guidance

검증을 실행하지 않았으면 실행하지 않았다고 적는다. validator pass만으로 모든 surface가 안전하다고 확대 해석하지 않는다.
