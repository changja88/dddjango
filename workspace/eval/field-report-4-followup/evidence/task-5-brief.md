### Task 5: 캐시뿐인 선택적 인스턴스와 50행 폐지 (F4-16/F4-17)

**Files:** `dddjango/scripts/checker_target.py`, `check-layer-skeleton.py`, `check-port-adapter-pairing.py`, `check-domain-model.py`, `check-usecase-dto-placement.py`, `check-context-isolation.py`, `registry_gate.py`와 byte 미러. Test: `workspace/tools/field_report_checker_smoke.py`, `registry_gate_smoke.py`의 snapshot 경계.

**Interfaces:** `checker_target.cache_only_instance(path: Path) -> bool`. 재귀 실제 작업 트리 검사에서 `__pycache__`와 그 아래 캐시 파일 흔적이 적어도 하나 있고 그 밖의 파일이 전혀 없어야 True. 빈 하위 디렉터리는 허용하지만 캐시 흔적 없는 완전 빈 폴더는 False. `.py`/빈 `__init__.py`/기타 실파일·숨김 비캐시 파일·symlink·읽기 오류가 있으면 False. Git tracking은 판정 재료가 아니다.

```python
if is_optional_instance_slot and checker_target.cache_only_instance(child):
    continue
```

- 적용 소유 지점은 skeleton의 optional `<instance>` 열거, pairing의 capability/adapter 인스턴스 열거, domain-model의 `_aggregate_dirs/_check_layout`, DTO의 usecase 인스턴스 열거 및 `_check_use_case` 진입, context-isolation의 `_check_ohs` 서비스 인스턴스 열거다. 동일 상대경로 선택 슬롯을 snapshot에서도 사용한다. 필수 BC/layer/port/adapter 고정 부모·골격 요구는 필터하지 않으며 전역 `_entries` 전체 제외로 대체하지 않는다.
- registry `_snapshot_current`는 copytree ignore가 캐시를 없애기 **전 원 작업 트리에서** 동일 술어로 선택적 인스턴스의 상대 경로 집합을 구한다. 사본의 해당 인스턴스만 제외한다. 고정 경로·다른 부모를 따라 지우지 않으며 원 작업 트리 파일은 삭제하지 않는다. 직접 checker와 snapshot gate가 같은 결과를 낸다.
- pre-gate가 이미 가진 계획 remove의 부모 정리 정책과 섞지 않는다.
- skeleton에서 `PROMO_PART_MIN_LINES`와 #642 방출을 제거한다. `_phys_lines`와 #644 200행 후보 및 #638/#639/#640/#641/#643는 유지한다. 규범 삭제는 Task6에서 완성한다. registry 진단 identity를 이 문제 때문에 고치지 않는다.

- [ ] **Step 1:** cache-only 직접/중첩, untracked 실제소스/빈init, cache 없는 빈폴더, source+cache, symlink, 필수고정골격 누락, snapshot 경계 테스트를 추가한다. aggregate 캐시의 #299/#256, usecase 캐시의 #193/#570/#569, OHS 캐시의 #152를 직접 checker CLI와 snapshot gate 양쪽에서 대조하고 실소스 혼재 시 기존 진단 유지도 확인한다. 원본 파일 목록/bytes를 보존 비교한다. 1~49행 부품은 #642 없음, 부품0/본체누락/중첩/정크드로어/201행은 기존 진단 유지.

```python
self.assertTrue(checker_target.cache_only_instance(cache_only))
self.assertFalse(checker_target.cache_only_instance(untracked_python))
self.assertNotIn("#642", violations(short_valid_component))
self.assertIn("#643", violations(no_component))
```

- [ ] **Step 2:** RED 확인 후 제한된 술어·열거·snapshot 경계를 구현한다.
- [ ] **Step 3:** `python3 -B workspace/tools/field_report_checker_smoke.py`와 `python3 -B workspace/tools/registry_gate_smoke.py`를 실행한다. fixture 기대값 변경은 실제 폐지 진단에만 한정한다.
- [ ] **Step 4:** byte 미러·작업 리뷰를 완료한다.


## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.


## Start gate and ownership
Do not implement before explicit coordinator dispatch after Task4 review. Preserve preceding Task1–4 behavior. Task4 touches domain-model/context/pairing and checker smoke; coordinator will snapshot their final bytes only after that gate. Test files here are workspace/tools/field_report_checker_smoke.py and workspace/tools/registry_gate_smoke.py. Existing skeleton fixtures are workspace/eval/fixtures/skeleton (not layer_skeleton). fixture_matrix.build_cases expects good_promoted0/bad_promoted2 and broad checker fixture exits; do not update unrelated expectation rows. Task6 owns #642 retirement in norms and current docs; this task owns removal of actual checker condition only.
Cache-only means genuine cache traces with no actual other files: noncache hidden/source files and symlinks remain visible; plain empty directories without cache trace are not cache-only. Preserve fixed required skeleton paths and actual source bytes; never delete user tree cache directories. #195/F4-20 is a new report item outside current12; no transaction-boundary changes.
