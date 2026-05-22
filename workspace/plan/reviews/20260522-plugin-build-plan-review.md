# plugin_build_plan 리뷰 기록

## 대상

- 입력 artifact: `workspace/plan/plugin_build_plan.md`
- 리뷰 일시: 2026-05-22
- 목적: `skill-creator` 기준과 과거 실패 재발 방지 기준으로 계획 자체의 빈틈을 검토한다.

## 범위 수정 기록

- 2026-05-22 사용자 확인에 따라 현재 계획 범위를 Codex 플러그인 재구축으로 고정했다.
- 다른 런타임 호환성은 P0-P8 완료 조건에서 제외했다.
- 아래 과거 리뷰의 다른 런타임 관련 항목은 당시 검토 이력일 뿐이며, 현재 active gate가 아니다.
- 현재 active plan은 Codex manifest, Codex skill discovery, Codex install/cache parity만 완료 조건으로 삼는다.

## 리뷰 1: skill-creator 원칙

- reviewer: subagent `Kepler`
- prompt 요약: skill-creator guidance 기준으로 concise skill design, progressive disclosure, bundled resource rules, validation integrity, forward-testing leakage를 검토한다.

초기 finding:

- Blocker 1: 계획 문서가 자체 리뷰 결과와 `Blocker 0, Major 0`을 주장해 자기 인증 구조를 만들었다.
- Major: 출처가 URL 없이 라벨로만 적혀 있었다.
- Major: P3 forward-testing이 fresh context, raw artifact, no answer leakage, cleanup을 요구하지 않았다.
- Major: P4가 eval protocol 없이 runner/scoring/report 구현으로 넘어갔다.
- Major: P4가 deterministic fixture를 충분히 요구하지 않았다.
- Major: P5/P6가 current-file evidence, `validate_eval_run`, score visibility, oracle artifact presence를 충분히 요구하지 않았다.
- Major: runtime cache 검증이 model-backed 검증보다 늦었다.

반영 상태:

- [x] 자체 인증 리뷰 결과 제거
- [x] 출처 Ledger에 URL, 조회일, 범위, 금지된 확대 해석 추가
- [x] P3 forward-test 규칙과 결과 schema 추가
- [x] P4 선행 eval protocol 추가
- [x] P4 mini-bucket fixture 추가
- [x] P5/P6 affected bucket clean, digest, raw artifact 기준 추가
- [x] P4.5 runtime parity precheck 추가

## 리뷰 2: eval/reliability

- reviewer: subagent `Planck`
- prompt 요약: targeted pass 오인, not scored, missing oracle JSON, stale report, expected_outcomes 충돌, validator false positive, local path leakage, model variance를 막는지 검토한다.

초기 finding:

- Blocker 3:
  - P5/P6가 full bucket 안정성 없이 완료될 수 있었다.
  - 현재 파일 기준 run evidence fingerprint가 없었다.
  - P4 single-case fixture로 full-run failure mode를 검증하려 했다.
- Major:
  - `not scored` 자동 판정 방식이 불명확했다.
  - missing oracle JSON이 variant 단위로 정의되지 않았다.
  - expected_outcomes schema 제약이 약했다.
  - validator false positive 대응이 fixture 기반이 아니었다.
  - local path leakage scan 범위가 약했다.
  - model variance 운영 기준이 약했다.
  - 외부 runner/권한 정책 실패 대응이 없었다.

반영 상태:

- [x] P5/P6 완료 조건을 affected bucket all-cases run pass로 강화
- [x] current-file digest/run metadata 일치 규칙 추가
- [x] P4 single-case를 mini-bucket suite로 변경
- [x] raw artifact primary truth 규칙 추가
- [x] `case x variant` oracle matrix 규칙 추가
- [x] baseline verdict 고정과 expected_delta completion gate 금지
- [x] validator evidence contract와 Korean negation fixture 추가
- [x] raw/report/local path scan 범위 추가
- [x] flaky/model-variance 분류 규칙 추가
- [x] infrastructure-blocked 상태와 complete 금지 규칙 추가

## 리뷰 3: Codex / 다른 런타임 / OpenAPI 호환성

- reviewer: subagent `James`
- prompt 요약: Codex, 다른 런타임, OpenAPI/source-doc use 관점에서 manifest/path/install/cache/discovery assumptions를 검토한다.
- 현재 상태: Codex-only 범위로 축소되면서 다른 런타임 관련 완료 게이트는 active plan에서 제거했다.

초기 finding:

- Blocker 0
- Major:
  - 다른 런타임 manifest 전략이 확정되지 않았다.
  - Codex와 다른 런타임 manifest/path 규칙을 같은 것으로 취급할 위험이 있었다.
  - cache 검증이 source/cache diff에 치우쳐 plugin root 밖 reference 의존을 막지 못했다.
  - cross-runtime frontmatter contract가 약했다.
  - `agents/openai.yaml`의 Codex 전용 의미가 분리되지 않았다.
  - OpenAPI source boundary가 약했다.
  - 공식/외부 source claim이 URL 없이 주장됐다.

반영 상태:

- [x] 범위 재조정 후 P0-P8에서 다른 런타임 manifest 전략 결정을 제거했다.
- [x] P2/P7을 Codex manifest와 Codex install/cache 검증으로만 제한했다.
- [x] P2/P4.5/P7에 plugin root 밖 path 참조 금지 추가
- [x] P2에서 Codex `SKILL.md` frontmatter 기준만 완료 조건으로 유지했다.
- [x] `agents/openai.yaml`은 Codex UI metadata로만 검증한다고 명시
- [x] OpenAPI boundary를 REST/HTTP API contract로 제한
- [x] 출처 Ledger에 URL/조회일/범위/금지된 확대 해석 추가

## 현재 open issue

- Blocker: 0
- Major: 최종 재리뷰 1차에서 5개 발견, 반영 완료
- Minor: 최종 재리뷰 1차에서 7개 발견, 반영 완료
- 최종 재확인: Blocker 0, Major 0, open Minor 0
- 상태: 계획 확정 후보

## 재리뷰 1차 결과

입력 artifact:

- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/reviews/20260522-plugin-build-plan-review.md`

리뷰 prompt:

- skill-creator 관점: 수정된 계획과 리뷰 기록에서 concise skill design, progressive disclosure, bundled resource rules, validation integrity, forward-testing evidence, self-certification 방지를 재검토한다.
- eval/reliability 관점: targeted-only completion, not scored, missing/malformed oracle, stale report, expected_outcomes conflicts, validator false positives, local path leakage, full-run instability, model variance, stale current-file evidence를 재검토한다.
- Codex/OpenAPI 관점: manifest strategy, path/cache/install/discovery, frontmatter compatibility, `agents/openai.yaml`, OpenAPI boundary, source ledger를 재검토한다.

주요 finding:

- Major: 리뷰 evidence 파일이 raw artifact 수준이 아니다.
- Major: shared runner/validator 변경 시 affected bucket 범위가 불명확하다.
- Major: skill bundled script 검증 게이트가 빠져 있다.
- Major: current-file evidence digest 범위에 report renderer, protocol, manifest/cache가 빠져 있다.
- Major: `expected_outcomes` 금지가 baseline verdict와 expected_delta에만 치우쳐 있다.
- Major: 다른 런타임 manifest 전략 결정 기준이 약하다.
- Major: install/cache/discovery 검증이 재현 가능한 command contract 수준이 아니다.

반영 상태:

- [x] 리뷰 파일 raw evidence 요구를 계획에 강화했다.
- [x] affected bucket 정의를 추가했다.
- [x] shared eval infrastructure 변경 시 모든 bucket affected 규칙을 추가했다.
- [x] bundled script 실행 검증 게이트를 추가했다.
- [x] digest 범위에 report renderer, template/static asset, eval protocol, plugin manifest, install/cache metadata를 추가했다.
- [x] report는 현재 renderer로 재생성한 뒤 raw artifact와 대조하도록 추가했다.
- [x] expected outcome 고정 verdict/delta 금지 범위를 baseline/with-plugin/pass-or-pass-limited/expected_delta로 확장했다.
- [x] `expected_outcomes` 허용 필드를 criterion coverage, required observations, forbidden overclaim로 제한했다.
- [x] 이후 범위 수정에서 다른 런타임 manifest 전략을 P0-P8 active gate에서 제거했다.
- [x] install/cache/discovery command evidence contract와 raw output 저장 위치를 추가했다.
- [x] P3 forward-test artifact 저장 위치와 사용자형 prompt 원칙을 추가했다.
- [x] `agents/openai.yaml` stale 비교 기준을 추가했다.
- [x] 이후 범위 수정에서 manifest version gate를 Codex manifest/install cache로 제한했다.
- [x] OpenAI Codex Agent Skills canonical URL을 Ledger에 추가했다.

## 최종 재리뷰 1차 결과

입력 artifact:

- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/reviews/20260522-plugin-build-plan-review.md`

reviewer prompt 전문:

```text
최종 재리뷰만 수행하세요. 파일 수정 금지. 대상은 /Users/hyun/Desktop/dddjango/workspace/plan/plugin_build_plan.md 와 /Users/hyun/Desktop/dddjango/workspace/plan/reviews/20260522-plugin-build-plan-review.md 입니다.

관점: skill-creator 원칙 / eval-reliability / Codex-OpenAPI-source 호환성 중 지정된 관점으로 검토하세요.

출력 형식:
- Verdict: Blocker N / Major N / Minor N
- Findings: 각 항목은 severity, 파일/섹션, 문제, 왜 실제 실패로 이어지는지, 수정 제안
- Open questions
- 통과 판단이 가능하면 그 근거

중요: 100% 성공 보장은 불가능하므로 그런 표현은 쓰지 마세요. 남은 Blocker/Major/open Minor를 찾는 것이 목적입니다.
```

raw reviewer output 저장 위치:

- skill-creator 관점: historical conversation ID `019e4f8b-bebd-7fc3-a295-60d1d3333b4e` (non-durable; not completion evidence)
- eval/reliability 관점: historical conversation ID `019e4f8b-c0f5-70b2-adee-8f70ffc000b6` (non-durable; not completion evidence)
- Codex/OpenAPI 관점: historical conversation ID `019e4f8b-c32a-7c33-85ce-ef3d67c22c61` (non-durable; not completion evidence)

주요 finding:

- Major: P3 fresh subagent forward-test가 선택 사항처럼 남아 있다.
- Major: P2에 `skill-creator/scripts/quick_validate.py` 또는 동등 validator 실행 게이트가 없다.
- Major: model-backed run digest 범위에 model id, runner destination, prompt assembly/template, tool/sandbox policy, oracle/scoring config가 없다.
- Major: P0에서 다른 런타임 manifest 생성 전략과 inventory-only 수정 게이트가 충돌한다.
- Major: P7 Codex install/cache/discovery evidence가 재현 가능한 command/API contract 수준이 아니다.
- Minor: 100줄 초과 bundled reference TOC/search-keyword 요구가 없다.
- Minor: `agents/openai.yaml` 생성/수정 시 `openai_yaml.md` 확인과 deterministic generation/update 증거가 없다.
- Minor: model-backed 2회 실행 규칙이 완료 게이트에 직접 들어가 있지 않다.
- Minor: 리뷰 파일 자체가 아직 재리뷰 필요 상태로 남아 있다.
- Minor: OpenAPI source가 version-pinned URL 없이 `latest`만 사용한다.

반영 상태:

- [x] P3 fresh isolated subagent/user-like forward-test를 필수 matrix와 완료 게이트로 올렸다.
- [x] P2에 `skill-creator/scripts/quick_validate.py <skill-folder>` 또는 동등 local validator 실행 증거를 추가했다.
- [x] P2에 100줄 초과 bundled reference TOC/search-keyword 요구를 추가했다.
- [x] P2에 `skill-creator/references/openai_yaml.md` 확인과 `generate_openai_yaml.py` 사용 증거 또는 미사용 사유를 추가했다.
- [x] run metadata에 model id/version, runner destination, prompt assembly source, system/developer prompt template, tool/sandbox policy snapshot, oracle model/config, scoring prompt/config를 추가했다.
- [x] P5/P6 완료 게이트에 model-backed 신규/수정 case 2회 pass와 single-pass provisional 완료 근거 금지를 추가했다.
- [x] 이후 범위 수정에서 P0은 Codex inventory만 허용하도록 다시 좁혔다.
- [x] 이후 범위 수정에서 P0 허용 수정 범위를 inventory로 제한했다.
- [x] P7 Codex discovery evidence를 `/plugins` transcript/screenshot, app-server `plugin/list`/`plugin/read` JSON, `skills/list`, `codex plugin --help` 기반 CLI output 중 가능한 raw evidence로 구체화했다.
- [x] OpenAPI Ledger에 version-pinned URL `https://spec.openapis.org/oas/v3.2.0.html`을 추가했다.

## 최종 재확인 결과

입력 artifact:

- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/reviews/20260522-plugin-build-plan-review.md`

reviewer prompt 전문:

```text
최종 재확인만 수행하세요. 파일 수정 금지. 대상은 /Users/hyun/Desktop/dddjango/workspace/plan/plugin_build_plan.md 와 /Users/hyun/Desktop/dddjango/workspace/plan/reviews/20260522-plugin-build-plan-review.md 입니다.

관점: skill-creator 원칙 / eval-reliability / Codex-OpenAPI-source 호환성 중 지정된 관점으로 검토하세요. 방금 반영된 수정이 남은 Blocker/Major/open Minor 없이 충분한지 검토하세요.

출력 형식:
- Verdict: Blocker N / Major N / Minor N
- Findings: 남은 항목만. 각 항목은 severity, 파일/섹션, 문제, 실제 실패 가능성, 수정 제안
- 통과 판단 근거

100% 성공 보장은 불가능하므로 그런 표현은 쓰지 마세요.
```

raw reviewer output 저장 위치:

- skill-creator 관점: historical conversation ID `019e4f90-b2ad-7fd0-9493-f2b3b6b1a3ca` (non-durable; not completion evidence)
- eval/reliability 관점: historical conversation ID `019e4f90-fe5e-7603-ae60-9fa13a7a0f31` (non-durable; not completion evidence)
- Codex/OpenAPI 관점: historical conversation ID `019e4f91-007e-7102-b092-482fcc8037c0` (non-durable; not completion evidence)

결과:

- skill-creator 관점: Blocker 0, Major 0, Minor 0
- eval/reliability 관점: Blocker 0, Major 0, Minor 1
- Codex/OpenAPI 관점: Blocker 0, Major 0, Minor 1

남은 Minor 처리:

- 두 Minor는 모두 이 리뷰 파일이 최종 재확인 결과를 아직 기록하지 않았다는 문서 상태 문제였다.
- 이 섹션에 최종 재확인 prompt, raw output 저장 위치, 결과, 반영 상태를 기록해 닫았다.

최종 상태:

- Blocker: 0
- Major: 0
- Open Minor: 0
- 판정: 이 판정은 아래 Codex-only 재리뷰 2차 이전 상태다. 최신 판정은 문서 마지막 섹션을 따른다.

## Codex-only 재리뷰 2차

입력 artifact:

- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/reviews/20260522-plugin-build-plan-review.md`

raw reviewer output:

- skill-creator 관점: `workspace/plan/reviews/raw/20260522-codex-only-skill-creator-review.md`
- eval/reliability 관점: `workspace/plan/reviews/raw/20260522-codex-only-eval-reliability-review.md`
- Codex official docs 관점: `workspace/plan/reviews/raw/20260522-codex-only-official-docs-review.md`

결과:

- skill-creator 관점: Blocker 0, Major 5, Minor 2
- eval/reliability 관점: Blocker 0, Major 2, Minor 1
- Codex official docs 관점: Blocker 0, Major 4, Minor 1

주요 finding과 반영 상태:

- [x] raw reviewer output을 대화 notification ID가 아니라 `workspace/plan/reviews/raw/` 파일로 저장하도록 변경했다.
- [x] 설치된 Codex runtime에서 high-risk trigger family별 user-like task가 실제 skill을 로드했다는 증거를 P7/P8 gate에 추가했다.
- [x] P1.5 usage cards 단계를 추가해 실제 사용자 prompt와 exclusion prompt를 skill trigger/body 설계 전에 고정하게 했다.
- [x] `description` 길이, `SKILL.md` body word budget, 중복 금지, detailed domain material reference 이동 규칙을 추가했다.
- [x] forward-test를 prior `workspace/plan/**`과 eval artifacts를 볼 수 없는 clean temp workspace에서 실행하도록 강화했다.
- [x] 100줄 초과 bundled reference는 반드시 상단 TOC를 갖도록 강화했다.
- [x] stale/placeholder bundled resource 제거 gate를 추가했다.
- [x] redaction 전 ephemeral raw scan과 redaction 후 persisted artifact scan을 분리했다. redaction 전 누출은 redaction 성공 여부와 무관하게 실패로 정의했다.
- [x] `flake_history` 또는 variance status를 run metadata와 P8 gate에 추가했다.
- [x] `agents/openai.yaml`을 Codex optional metadata로 보고 `interface`, invocation `policy`, `dependencies`를 검증하도록 수정했다.
- [x] runtime boundary scan 범위를 plugin root 전체로 확장했다.
- [x] P4.5에 P7 수준의 install/cache/discovery raw evidence contract를 선행 gate로 추가했다.
- [x] local plugin cache version은 `local`로 기록하고 manifest `version`은 source/installed `plugin.json` 값 비교로 분리했다.
- [x] manifest path field 전체에 `./`, plugin-root-relative, plugin-root-contained, existence validation을 추가했다.

현재 상태:

- Blocker: 0
- Major: 0
- Open Minor: 0
- 판정: Codex-only 재리뷰 2차 finding 반영과 read-only 재확인 완료. 단, `100% 성공 보장`이 아니라 false-completion을 막는 계획 확정 후보이다.

## Codex-only 재확인 2차

입력 artifact:

- `workspace/plan/plugin_build_plan.md`
- `workspace/plan/reviews/20260522-plugin-build-plan-review.md`
- `workspace/plan/reviews/raw/*.md`

raw reviewer output:

- `workspace/plan/reviews/raw/20260522-codex-only-final-recheck.md`

결과:

- skill-creator 관점: Blocker 0, Major 0, Minor 0
- eval/reliability 관점: Blocker 0, Major 0, Minor 0
- Codex official docs 관점: Blocker 0, Major 0, Minor 0

재확인 근거:

- durable raw review artifacts: `workspace/plan/reviews/raw/*.md`로 보존됨.
- installed Codex runtime user-like usability gate: P7/P8에 반영됨.
- P1.5 usage cards: P2 trigger/body 수정 선행 조건으로 반영됨.
- concision / progressive disclosure gates: P2에 반영됨.
- clean-temp forward-test contamination control: P3에 반영됨.
- two-phase pre-redaction leakage gate와 sanitizer-only failure fixture: 증거 규칙과 P4에 반영됨.
- `flake_history`와 unresolved flaky P8 gate: 증거 규칙과 P8에 반영됨.
- `agents/openai.yaml` interface/policy/dependencies, plugin-root boundary scan, P4.5 install/cache/discovery evidence, local cache version semantics, manifest path validation: P2/P4.5/P7에 반영됨.
- Codex-only scope와 OpenAPI REST/API contract boundary: 전제, Ledger, P1, P9에 반영됨.

최종 상태:

- Blocker: 0
- Major: 0
- Open Minor: 0
- 판정: Codex-only 계획 확정 후보. 단, `100% 성공 보장`이 아니라 false-completion을 막는 실행 계획이다.
