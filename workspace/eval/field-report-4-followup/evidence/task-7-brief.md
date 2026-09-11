### Task 7: 통합 리뷰·검증·미처리 목록 정리

**Files:** 이 계획의 진행 상태, `workspace/eval/field-report-4-followup/`의 구현/리뷰/최종 증거, `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md`, 변경 시 `workspace/tools/manifest_seal.py`의 현행 봉인 산출물. 기존 harness 확장이므로 새 독립 test runner/Make target은 만들지 않는다.

- [ ] **Step 1:** 변경 코드/규범/미러와 테스트를 동결해 독립 구현 리뷰 3명에게 전달한다. A: 실제 검출·미탐 반례, B: 규범·입력/리포트 일치, C: 증거·scope·기존 진탐 보존. 자기 구현을 본인이 승인하지 않는다.
- [ ] **Step 2:** BLOCKER/MAJOR를 모두 수정하고 해당 변경을 재리뷰한다. 새 정책이 필요한 지적은 임의로 해결하지 않고 사용자에게 보고한다. 단순 기술 보완은 합의 범위 안에서 처리한다.
- [ ] **Step 3:** 12건 각각 actual checker/pregate/규범에 필요한 증거가 있는지 독립 최종 감사한다. 기능 테스트가 없는 항목, S1을 green으로 과장한 항목, 실제 해결이 없는 보고서 삭제는 실패다.
- [ ] **Step 4:** 완료한 항목만 원 보고서의 요약+본문에서 제거한다. 부분 미처리면 그 잔여를 ID 그대로 남기고 번호를 당기지 않는다. 원 보고서의 사용자 추가분이 변했는지 현재 SHA와 동결본을 비교해 새 내용을 보존한다. 완료 증거는 본 계획/리뷰 기록에 남긴다.
- [ ] **Step 5:** 봉인 대상 최종 수정 이후 봉인을 재발행하고 최종 필수 검증을 수행한다.

```bash
python3 workspace/tools/manifest_seal.py --write
make verify-mutation
make verify
git diff --check
```

verify 실패로 봉인 대상 파일을 고쳤으면 봉인→make verify를 다시 실행한다. 보고에는 마지막 실행 로그 경로와 그 수치만 사용한다. manifest/설치구조를 실제 변경했다면 `claude plugin validate dddjango --strict`도 실행한다. 버전은 이 계획에서 올리지 않는다.
- [ ] **Step 6:** 사용자에게 구현 결과, 의도적으로 남긴 지원 한계, 3리뷰/최종 감사·검증 결과, 미처리 수를 보고하고 종료한다. Serena/Graphify opt-in 부재를 한 줄 남긴다. 커밋·배포가 수행됐다고 말하지 않는다.

## 진행 기록

- 2026-09-11: 문제 리뷰 A/B/C 완료. BLOCKER 0, 추가 사용자 정책 결정 필수 0. MAJOR 구현 제약을 위 계획에 수용했다.
- 최초 계획 SHA-256 `bc3e95b7d0146e917ecbbe70ab5e69fee95cbfb26ed3020a9beb0e7dc5eccdad`에 계획 리뷰 A(0/2/0), B(0/3/0), C(0/2/4)를 받았다. 중복 지적을 합쳐 원본 레코드 운반/슬롯 식별, read-only 조건, 실제 admin 원형과 세 상태, 현행 술어/소유 전파, cache-only 직접 소비 지점을 보완했다. C의 minor 4도 반례와 CLI 검증 계약으로 반영했다.
- 개정 계획 재리뷰: A/B/C 모두 지적 ADDRESSED, 잔여 B/M/m 0/0/0. 추가 사용자 정책 결정 필수 0. 승인에 따라 구현 단계 진입.
- 기준 회귀 실행: `python3 -B workspace/tools/pregate_field_report_smoke.py` 15/15, `python3 -B workspace/tools/field_report_checker_smoke.py` 12/12 green. 신규 구현 검증 증거가 아닌 변경 전 기준선이다.

- 실행 위치: `/Users/hyun/.cache/dddjango-field4-followup-20260911` (기준 HEAD에서 분리한 detached worktree). Task1 구현 진행 중. 완료 후 검증된 요청 대상 변경만 primary로 옮기며 `docs/master.html`은 제외한다.

- Task2 검증 구체화: 기존 dirty update 본문은 pre-gate 앵커에 들어가 legacy이므로 그 자체로 새 exit2가 되지 않는다. 실제 checker/registry CLI의 clean anchor→bad current에서 exit2와 원본 record를 확보해 S1 분리 뒤 보존을 대조한다. dirty update의 기존 pregate exit0 경계도 보존하고, 생성 스텁·선언 확정+S1은 실제 pregate CLI로 검증한다. 앵커 정책 변경 없음.


## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시와 기존 render-sync가 요구하는 개정 graph 절의 기준선에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.


## Report and transfer boundary
Primary report received appended F4-20 during execution. Read current primary and compare against primary-report-with-new-F20.md before cleanup; preserve F4-20 and any later additions. Do not overwrite with stale worktree report. No task7 source edits or reviews before Task6 gate. Evidence must survive final transfer; no SDD deletion because no Git record was authorized. Protected primary docs/master.html hash is in primary-baseline.json/progress.md. Final required validation runs after source/norm/seal edits.
