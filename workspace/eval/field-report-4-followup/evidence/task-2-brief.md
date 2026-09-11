### Task 2: 생성 메서드의 미검증 분리와 실행 모드 안내 (F4-12/F4-19)

**Files:**
- Modify/Mirror: 양 runtime `design_pregate.py`.
- Test: `workspace/tools/pregate_field_report_smoke.py`, `workspace/tools/pregate_fixture_run.py`.

**Interfaces:** materialize report에 `generated_methods`를 추가한다. 구조는 `dict[path, list[{owner, method, lineno, end_lineno}]]`이며 **이번 렌더가 만든 AST에서만** 기록한다. 기존 `materialized`/`unsimulated` 등 key는 보존하고 구조화 필드를 담는 반환 타입으로 맞춘다. `run_gate`는 기존 `introduced.json`의 `attributed_lines`, `records`, `unmatched_lines`, `candidate_lines`, `candidate_records`와 raw exit/stdout을 함께 반환한다. `record.file`의 끝 `:숫자`가 원본 행이며 정규화 문자열의 `:N`에서 행을 복원하지 않는다.

후처리 `partition_generated_findings(gate_result, generated_methods) -> (retained, deferred)`는 **registry 전체 정규화 귀속 key → 그 key에 대응하는 원본 레코드 전부**를 결합한다. `_stable_id(rule+path)`로 cohort를 만들지 않는다. 기존 sidecar payload와 공용 정규화/레코드 line 변환을 쓰며 Findings 스키마·귀속 identity를 개편하지 않는다.

```python
if rule == "#376" and location_matches_generated_after_commit:
    deferred.append("S1: 생성한 after_commit 본문 — on_commit 구현 미검증")
else:
    retained.append(line)
```

- 같은 귀속 key에 대응하는 **모든** 원본 record의 path+line이 정확한 생성 `after_commit` 내부인 #376일 때만 그 key를 S1로 분리한다. 생성파일의 다른 메서드·다른 규칙, 기존 update 실코드, 단순 `raise NotImplementedError` 실물은 제외 근거가 아니다. 비생성·다른 위치·불명 record가 하나라도 섞이거나 대응 record가 없거나 unmatched이면 key 전체를 유지한다. #566은 이 분리에 넣지 않는다.
- raw registry exit 1/자료 결손은 계속 RunError이며 분리로 green을 만들지 않는다. registry의 확정 귀속 항목을 분리한 후 남은 항목과 Task1 선언 확정으로 최종 exit를 정한다. raw exit2에 설명할 귀속 항목이 없으면 RunError로 fail-closed한다.
- 화면/리포트에는 ‘원 registry 결과’와 ‘생성 본문 S1 미검증’을 구분한다. S1을 verified/적용 불가/filtered로 표현하지 않는다. `--check-report`에서 미검증 정보가 보존되며 실제 G2 checker는 수정하지 않는다.
- 실행 모드는 `초기 예보(기준선 기본 HEAD)` / `명시 재예보(--base X)`로 표시한다. baseline 실존 add와 baseline 부재+overlay 실존 add를 다른 오류로 안내한다. update가 기준선에 없을 때 add라는 말만 내지 말고 초기/재예보의 적용 목적을 함께 적는다.
- 기존 12조합(add/empty/update × 기준선 실존/부재 × 초기/명시) exit 정책과 기실현 lifting을 유지한다. 초기 add를 자동 허용하지 않는다. commit/stash/기준선 이동을 자동 실행하거나 무조건 처방하지 않는다.
- file-plan은 승인 제품 변경의 경로, coordinator 작업 기록·gate report·임시 로그는 계획 재료 밖임을 안내한다. docs/**나 비-Python 파일을 일괄 금지하지 않는다. 당시 작업기록 오편입 사례를 설명하되 파일명만으로 자동 삭제하지 않는다.

- [ ] **Step 1:** 실제 CLI에서 생성 after_commit/#376 S1, 기존 잘못된 본문/#376 유지, 실제 robust 누락/#566 유지를 반대 대조한다. 기존 fixture builder를 사용하고 original bytes를 비교한다.

```python
self.assertEqual(generated_exit, 0)  # 해당 규칙 외 위반이 없는 최소 fixture
self.assertIn("S1", generated_report)
self.assertEqual(real_bad_exit, 2)
self.assertIn("[#376]", real_bad_output)
self.assertIn("[#566]", robust_missing_output)
```

추가: 동일 정규화 key의 두 위치가 모두 생성/생성+실물 혼재/행번호 누락, 가짜 stub 텍스트, 자료 결손·unmatched, 선언확정과 deferred 동시, 기존 12조합의 exit/원인문구/모드, report-check. raw 귀속 수와 retained/deferred 수를 별도로 대조한다.
- [ ] **Step 2:** 실패 테스트 실행·원인 기록 후 provenance를 생성 시점에 연결하고 후처리/메시지를 구현한다.
- [ ] **Step 3:** `python3 -B workspace/tools/pregate_field_report_smoke.py`와 `python3 -B workspace/tools/pregate_fixture_run.py`를 실행한다. helper 결과만으로 CLI exit를 증명하지 않는다.
- [ ] **Step 4:** byte 미러와 작업 리뷰를 완료한다.


## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.


## Task 1 integration boundary
Task 1 already implemented full declarations/declaration_aliases, effects syntax/hash, check_declarations, marker update, DTO graph and report/check-report declaration channels. Preserve them. Current materialize returns materialized/already_built/unsimulated/pruned_dirs; extend without replacing keys. main calls declarations before zero-materialization skip and combines declaration count into exit2. run_gate currently tuple(exit,attributed,stdout); this task changes it. Read Task1 report only if a concrete interface question remains.
Task1 source#197 direct execute(uow) probe is outside standard #635 Command/Query input contract; no new #197 source filter was authorized or assigned to Task2. Standard constructor UoW injection is clean. Combined declaration-confirmed + generated S1 actual CLI coverage is this task's explicit responsibility.
Preserve Task1 marker fixes: prefix list has pytest binding before evaluation; subscript mutation retains original bytes with S5. Current smoke baseline26 green. No norms/report cleanup/seal/master changes in this task.

### Task2 fixture clarification — anchor semantics preserved
The existing pregate overlays dirty source before creating its pre-materialization anchor. Consequently unchanged bad update bodies (#376/#566, including real NotImplementedError) are legacy, not newly attributed, and pregate exit0 is expected absent other new violations. The plan real_bad_exit2 counterexample is satisfied by actual checker/registry CLI (clean anchor→real bad source), exact introduced raw records, and partition retaining the full key. Also cover the dirty-update pregate legacy boundary. Generated-only and declaration-confirmed+S1 still require actual pregate CLI end-to-end. This refines the fixture, never changes anchor policy.
