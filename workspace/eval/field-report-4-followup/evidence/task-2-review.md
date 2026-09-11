### Spec Compliance

- ❌ Issues found: M1 — `dddjango/scripts/design_pregate.py:1855`와 byte 미러의 동일 행에서 생성 범위를 최종 합성 전에 기록한다. 동일 update에 OHS 함수 append와 marker 변경이 함께 있으면 `generated_methods`의 행 범위가 최종 AST와 달라져 Task 2의 정확한 생성 범위 반환 계약을 충족하지 못한다.
- ✅ 그 외 검토 범위는 부합한다. 전체 정규화 귀속 key별 모든 raw record 검증, mixed/missing/unmatched 유지, #376에만 한정한 S1 분리, #566 유지, raw RunError, declaration conjunction, S1 report/check-report, 두 실행 모드와 12조합 정책을 구현했다. 근거: `dddjango/scripts/design_pregate.py:1920`, `dddjango/scripts/design_pregate.py:1966`, `dddjango/scripts/design_pregate.py:2659`, `dddjango/scripts/design_pregate.py:2883`; `workspace/tools/pregate_field_report_smoke.py:433`, `workspace/tools/pregate_fixture_run.py:935`.
- ✅ 승인된 anchor clarification에 맞춰 dirty real update를 legacy로 유지하고 clean anchor→real bad body는 실제 registry CLI로 반대 대조한다. `workspace/tools/pregate_field_report_smoke.py:468`에서 실제 NotImplementedError/#376 및 robust 누락/#566를 유지하며 원문 보존을 확인한다. #566나 Task 1 source #197 필터 변경은 없다.
- ⚠️ Task 3 annotation provenance 후처리와 Task 6 최종 감사·make verify·seal/report 정리는 이 작업 밖의 후속 검증이다. 여기서는 Missing으로 판정하지 않는다.

### Strengths

- `dddjango/scripts/design_pregate.py:1966`: Findings 공용 line 변환과 registry 공용 정규화를 사용하고 모든 대응 raw 위치가 생성 class `after_commit` 안인 경우에만 분리한다. 숫자 없는 위치, 빈 cohort, unmatched, 다른 메서드, 다른 규칙이 green 근거로 쓰이지 않는다. `_stable_id`로 cohort를 축약하지 않는다.
- `workspace/tools/pregate_field_report_smoke.py:514`: 동일 key의 복수 생성 위치와 생성/실물 혼재, 행번호 없음, `:N`과 `file_raw` 우회, missing/unmatched 및 다른 메시지 key를 구별하는 테스트가 실제 partition 결과를 단언한다.
- `workspace/tools/pregate_field_report_smoke.py:433`: 실제 pregate CLI의 raw 2 / 귀속 1 / 유지 0 / S1 1 / 최종 0, 실제 check-report의 S1 보존, 선언 확정과 S1 동시 존재 시 exit 2를 대조한다. helper 호출만으로 CLI 결과를 대신하지 않았다.
- `dddjango/scripts/design_pregate.py:1920`: raw stdout과 sidecar 채널을 보존하면서 필수 자료 결손, 후보 채널 반쪽, raw exit 1 및 설명 없는 raw exit 2를 RunError로 차단한다.
- `workspace/tools/pregate_fixture_run.py:935`: 12조합 각각의 exit·모드·원인 문구·작업기록 안내·원본 보존을 실제 CLI로 검사한다. 기존 lifting 및 anchor 순서는 diff에서 유지된다.

### Issues

#### Critical (B — Must Fix)

- 없음.

#### Important (M — Should Fix)

- **M1 — 후속 marker 합성으로 생성 범위가 어긋난다.** `dddjango/scripts/design_pregate.py:1855` 및 `codex-dddjango/skills/dddjango/scripts/design_pregate.py:1855`. OHS append 결과에서 `generated_methods`를 수집한 뒤 `:1858`의 `_render_marker_update`가 module 앞에 import/pytestmark를 삽입하거나 여러 줄 대입을 한 줄로 바꿀 수 있다. 반환된 범위는 이 이동을 반영하지 않는다. parser가 수용하는 OHS `update`, 새 `new_query() -> str`, 동일 파일 owner의 `[markers: slow]` 입장 표로 scratch 재현한 결과, 기록은 `lineno=9, end_lineno=11`이지만 최종 AST는 `11, 13`이었다. 이 작업이 공개하는 provenance 범위 자체가 틀리며 다음 소비자가 정확한 위치 증명으로 사용할 수 없다. Task 3의 annotation 판정 변경을 요구하는 사항은 아니다. 이번 append가 추가한 함수 이름을 보존하고 마지막 marker 합성까지 완료한 AST에서 그 이름들만 재수집하도록 수정한다. 이 조합의 최종 AST 범위를 단언하는 focused 회귀 검증을 추가하면 충분하다.

#### Minor (m — Nice to Have)

- 없음.

### Assessment

**Task quality: Needs fixes.**

정규화 cohort와 fail-closed 정책은 보수적으로 구현되어 있고, CLI 및 원본 보존 대조도 적절하다. 다만 M1은 새 공개 인터페이스가 실제 최종 소스와 다른 생성 범위를 반환하는 재현된 동작 결함이므로 Task 2를 통과시키기 전에 수정해야 한다.

### Review evidence

- `task-2-review-package.md` 1–1625행을 순차 1회 읽었다. Git 명령, broad suite 재실행, production/test/Git 변경은 하지 않았다.
- 공용 조인 계약 위험에 대한 focused 확인: `dddjango/scripts/registry_gate.py:149`, `:256`와 `dddjango/scripts/findings.py:286`. sidecar는 snapshot prefix를 file에서 제거하고 실제 숫자 행번호를 보존하며, partition이 동일 line 재구성과 정규화를 사용한다. 조인 불능은 유지 쪽으로 닫혀 있다.
- diff의 materialize hunk가 전체 합성 흐름을 포함하지 않아 생성 범위 이후 이동 위험을 확인했다. 읽은 unchanged helper는 `dddjango/scripts/design_pregate.py:1328`의 `_render_service_update`와 `:1409`의 `_render_marker_update`다. OHS append는 기존 bytes 뒤에만 추가하지만 marker 단계는 앞의 줄 수를 바꿀 수 있다.
- 재현 입력의 parser 도달 가능성은 `_parse_signals`의 owner-path 결합(`dddjango/scripts/design_pregate.py:752`)을 집중 확인했다. 실제 `parse_spec`도 동일 경로의 Signals(markers=['slow'], markers_explicit=True)를 errors 없이 생성했다.
- scratch focused probe 2회: 첫 번째는 직접 signals를 넣어 위치 이동을 확인했고, 두 번째는 정식 6열 입장 표와 `parse_spec`을 거쳐 동일 결과를 확인했다. 두 실행 모두 기록 9–11 / 최종 AST 11–13. 기존 fixture의 setUp/tearDown으로 임시 저장소만 사용했고 어떤 영구 테스트도 작성하지 않았다.
- 기존 `task-2-smoke-green.log`(32 tests / OK), `task-2-fixture-green.log`(12모드와 기존 bundle PASS), `task-2-static-green.log`(4 compile / byte mirror / diff check PASS), `task-2-raw-location-green.log`(1 focused test / OK)를 읽었다. 이들 현재 green 로그에 warning은 없으며, M1 조합은 기존 provenance 테스트가 다루지 않는다.
- Serena·Graphify: opt-in 없음에 따라 검색·로드·호출·초기화하지 않았다.

Review path: `.superpowers/sdd/2026-09-11-field-report-4-followup/task-2-review.md`


### Round 1 Scoped Re-review — Final Verdict

- ✅ **Spec compliance: Spec compliant. M1 ADDRESSED.** `dddjango/scripts/design_pregate.py:1851`에서 새 `(owner, method)` identity만 보관하고, `:1867`에서 marker까지 합성한 최종 AST로 해당 identity의 범위를 수집한다. Codex 미러 동일 변경이며 이전 조기 범위 기록은 제거되었다. 원래 Task 2 리뷰에서 남았던 정확한 생성 범위 계약의 결함이 해소되었다.
- ✅ **Task quality: Approved.** 남은 Critical B 0건 / Important M 0건 / Minor m 0건. 이번 scoped diff에서 새로 생긴 결함은 발견하지 못했다. 이 최종 verdict가 앞선 M1 OPEN / Needs fixes 판정을 대체한다.
- **Strength:** `workspace/tools/pregate_field_report_smoke.py:507`의 새 테스트는 parser→materialize 경로로 prefix 삽입과 multiline marker 축약을 모두 검증한다. 최종 AST 범위뿐 아니라 생성 identity가 새 `new_query` 하나뿐임, 기존 함수 본문 보존, 원본 source 보존을 단언한다. 기존 함수가 생성 provenance에 섞이는 방향의 수정을 막는다.
- **Scope preservation:** `task-2-fix1-review-package.md:1`부터 172행까지 한 번 읽었다. 변경은 양 runtime의 생성 범위 수집 시점과 한 회귀 테스트에 한정되며, #566·source #197·anchor·cohort·exit·report·12모드 정책을 변경하지 않는다. 별도 cross-file 탐색이나 테스트 재실행은 필요하지 않았다.
- **Evidence read:** `task-2-fix1-focused-green.log:1`은 두 subcase를 포함한 1 test OK, `task-2-fix1-smoke-green.log` 마지막 요약은 33 tests / 50.332s / OK, `task-2-fix1-static-green.log:1`은 4파일 compile·byte mirror·diff check PASS다. 구현자의 기존 증거를 읽었으며 whole suite를 반복하지 않았다.
- ⚠️ Task 3 annotation 후처리 및 Task 6 최종 감사·검증은 앞선 리뷰와 동일하게 deferred이며 이번 Task 2의 결손이 아니다.
- Serena·Graphify: opt-in 없음에 따라 사용하지 않았다. production/tests/Git는 수정하지 않았으며 이 리뷰 파일에만 결과를 append했다.
