# 의미 있는 영구 테스트 생성 정책 수정 계획

> **구현 지침:** 이 계획이 사용자 승인을 받은 뒤 `superpowers:subagent-driven-development` 또는
> `superpowers:executing-plans`로 Task 단위 구현한다. 스킬 본문 변경은
> `superpowers:writing-skills`의 RED→GREEN→REFACTOR 검증을 적용한다.

**상태:** 사용자 검토 전 · 플러그인 구현 전 · 30차 적대 리뷰 closure 완료 · 최종 기록본

**문제·원인 기준선:** `workspace/design/2026-08-05-broccoli-server-unnecessary-test-audit.md`

**목표:** dddjango가 제품 의미를 보호하지 않는 영구 테스트를 새로 만들거나 강화하지 않게 한다.
framework·언어·private 구현·테스트 도구·Red 비계 자체를 검증하는 테스트와 같은 보장의 중복
테스트를 입장 단계에서 막고, 이미 승인된 제품 행동·응용 정책·도메인 불변식·DB 보장·경계 변환·
공개 Python 계약은 과잉 제거하지 않는다.

---

## 1. 원인과 해결책

감사 문서가 확인한 원인은 두 부류다.

| 원인 부류 | 확인된 원인 | 이번 수정의 방어층 |
|---|---|---|
| 왜 작성했는가 | Architect가 구현 세부와 framework mechanics를 test contract로 승격 | `discipline-tdd`의 중앙 영구 테스트 입장심사 |
| 왜 작성했는가 | Coordinator가 모든 내부 의무를 unit Red로 자동 변환 | `admit` row만 Red slice로 변환 |
| 왜 작성했는가 | 피라미드·이중 루프·knowledge 예시가 수량 압력으로 작동 | 관련 knowledge를 candidate signal/작성 recipe로 낮추고 중앙 decision으로 반송 |
| 왜 막지 못했는가 | G1에서 신규·변경 테스트 필요성이 숨음 | G1에 admit/covered-no-new-test/lifecycle-approved/terminate/reject/pending을 직접 표시 |
| 왜 막지 못했는가 | white-box·중복 금지가 선언뿐이고 필수 증거가 없음 | 독자적 failure mechanism·case partition·기존 권위 테스트 대조를 row 필수값으로 만듦 |
| 왜 막지 못했는가 | acceptance와 coder 사이 중복 재감사 없음 | owner/boundary 분리와 Phase 1·2 독립 감사 |
| 왜 막지 못했는가 | 첫 Green 뒤 Red 비계 정리 소유자 없음 | 사전 scaffold 등록, post-Green owner correction, 최종 diff 감사 |
| 왜 막지 못했는가 | stale 계약 종료 lifecycle이 약함 | `terminate` row와 changed/renamed/retired anchor의 한정 검색 |
| 왜 막지 못했는가 | checker/eval이 green·coverage만 봄 | 기존 checker는 유지하고, source-shaped negative pressure로 행동을 검증 |

핵심 흐름은 다음과 같다.

```text
변경 표면과 현재 계약
  → Architect가 영구 테스트 후보를 중앙 decision row로 판정
  → 활성 lens가 candidate만 제안
  → Phase 1 discipline reviewer가 최종 명세와 관련 테스트 evidence를 감사
  → G1에서 admission·no-new-test·lifecycle·종료·비자격·미확정을 사용자에게 공개
  → Coordinator가 admit된 row만 acceptance/coder Red slice로 변환
  → 첫 Green 뒤 원 owner가 Red 비계를 명시적으로 교정
  → Phase 2 discipline reviewer가 승인 연결·독자 보장·비계 0을 감사
  → G2
```

---

## 2. 범위와 비범위

### 2.1 수정 범위

- Claude 정본 `dddjango/`의 Coordinator, 역할 prompt, 관련 knowledge skill/reference
- Codex `codex-dddjango/`의 의미 미러
- `workspace/reference/spec.md`, README, timeline, DEVLOG
- 이번 정책을 검증하는 최소한의 비채점 pressure 자산

### 2.2 수정하지 않는 범위

- `/Users/hyun/Desktop/broccoli-server`의 테스트·프로덕션 코드
- 기존 19개 `dddjango/scripts/check-*.py`
- frozen `workspace/eval/**` v4 case·rubric·golden
- manifest version, tag, push, marketplace release
- 모든 기존 테스트의 전수 inventory·일괄 삭제·일괄 이동
- target Django 프로젝트에 배포되는 새 테스트 framework

### 2.3 과적합 방지 결정

형태만 보고 다음을 일괄 금지하지 않는다.

- introspection, exact field/signature/hierarchy
- 외부 테스트와 내부 테스트의 공존
- `StrEnum`, Pydantic, Ninja, ORM을 사용하는 모든 테스트
- migration이라는 이름을 가진 모든 테스트

별도 승인된 common `ErrorOut` shape, 공개 OHS, event union↔Enum 동기 계약,
`preserve-established` HTTP status/body/header/OpenAPI, 실제 repository round-trip처럼
권위 있는 계약과 독자 failure mechanism이 있으면 유지·admit할 수 있다. 특히 공통
`ErrorOut`의 멤버를 이 플러그인이 전역 상수로 고정하지 않는다. 프로젝트가 그 표면을
바꾸려면 기존 별도 사용자 승인 규칙을 그대로 따른다.

### 2.4 모든 reference 편집의 mirror gate

각 `dddjango/skills/*/references/final.md` 편집은 Task 번호와 무관하게 같은 순서를 강제한다.

1. 편집 전 `corpus_mirror_sync.py --check --format json` exit 0·11/11을 확인한다.
2. Claude 정본 하나를 편집한다.
3. 같은 check의 exit가 2이고 drift skill이 현재 대상 하나뿐이며 구조 오류가 0인지 확인한다.
4. 그때만 `--write`를 실행한다.
5. 다시 exit 0·11/11과 Claude↔Codex reference byte equality를 확인한다.

다른 skill drift가 섞이면 `--write`로 덮지 않고 중단한다.

---

## 3. 중앙 영구 테스트 입장 계약

### 3.1 허용되는 보호 계약

새로 만들거나 의미 있게 강화하는 영구 테스트는 정확히 하나 이상의 다음 분류를 가져야 한다.

1. `product-behavior`: 승인된 HTTP·이벤트·영속 wire·사용자 관찰 상태·보안/규제 계약
2. `application-policy-orchestration`: 원자성·부작용 순서·at-most-once·협력 실패 처리
3. `domain-invariant`: framework와 무관한 불변식·상태 전이·판정 경계
4. `db-guarantee`: 현재 constraint·transaction·rollback·race·멱등성·repository round-trip
5. `boundary-adapter-protocol`: domain↔wire 변환·정규화·fallback·known failure 번역
6. `approved-public-python-contract`: 승인 record 또는 실제 deployed consumer가 식별된 공개
   import path·field·signature·hierarchy

다음은 독립 근거 없이 영구 테스트 자격이 아니다.

- framework·표준 라이브러리의 기본 동작
- private helper·module 배치·source AST/import 형태·docstring·`slots`·monkeypatch seam
- 테스트 도구 호환을 위해 만든 production 의미
- import 가능 여부나 loader 성공만 보는 Walking Skeleton
- coverage·속도·피라미드 층수·디버깅 편의를 이유로 한 테스트 복제
- 구현 파일·함수·과거 model state 자체만 oracle인 migration mechanics
- `.dddjango` 문서를 읽거나 파싱하는 제품 pytest

### 3.2 중복 판정

- 후보는 자신만 잡는 구체 production defect/mutation을 적는다.
- 같은 owner/boundary·계약·failure mechanism에서 후보 전체 case partition이 기존 권위 테스트
  partition의 합집합에 포함되면 `covered-no-new-test`다.
- 일부만 겹치면 `covered-no-new-test` 부분과 uncovered 부분을 다른 row로 나눈다.
- domain 판정, application orchestration, DB bypass/race, adapter 변환, HTTP 직렬화처럼
  소유자나 failure mechanism이 다르면 여러 층이 함께 유효할 수 있다.
- 기존 테스트는 새 후보가 `covered-no-new-test`라는 이유만으로 삭제하지 않는다. 삭제·약화·이동·split은
  계약 종료 `terminate` 또는 계약 보존 `lifecycle-approved` row가 필요하다.
- 자격 있는 계약이 이미 완전히 보호되는 경우는 항상 `covered-no-new-test`이며 `reject:duplicate`로
  다시 분류하지 않는다. 권위 계약 자체가 없는 후보는 `reject:no-authoritative-contract`,
  framework/private mechanics면 해당 비자격 reason을 쓴다.

### 3.3 폐쇄형 decision 상태

| 상태 | 의미 | Phase 2 효과 |
|---|---|---|
| `admit` | 보호 계약·권위 근거·독자 보장·owner/boundary가 완비 | 해당 owner의 Red slice 생성 가능 |
| `covered-no-new-test` | 후보 전체가 기존 권위 partition으로 보호됨 | 새 test/path/support artifact 0, 기존 verification만 사용 |
| `lifecycle-approved` | 계약·oracle을 보존한 exact move/split/rename/consolidation이 별도 승인됨 | 열거된 artifact만 변경하고 전후 권위 partition 합집합을 검증; 새 의미·case 0 |
| `terminate` | 현재 계약 종료와 exact 기존 artifact/case가 별도 승인됨 | 해당 lifecycle owner만 삭제·약화 가능 |
| `reject` | framework/private/source/test-tool/no-authoritative-contract 등 비자격 | 테스트 slice 0, 적절한 code/type/checker/reviewer 검증으로 반송 |
| `pending` | 근거·owner·계약·정책이 미확정 | G1/G1′에서 중단, Phase 2 진입 금지 |

`decision`과 `lifecycle_action`은 직교하지만 허용 조합은 닫혀 있다. `admit`은 `add|semantic-update`,
`covered-no-new-test`는 `none|retain`, `lifecycle-approved`는 `move-preserving|split-preserving|
rename-preserving|consolidate-preserving`, `terminate`는 `delete|weaken`,
`reject|pending`은 `none`만 허용한다. `consolidate-preserving`은 별도 사용자 승인을 받은 exact 중복
artifact만 제거하며, 제거 전후 권위 partition 합집합과 failure mechanism이 같고 살아남는 counterpart가
명시돼야 한다. 기존 권위 테스트가 실제로 실패하면 `covered-no-new-test`여도 새 테스트를 만들지 않고
그 기존 테스트를 code slice의 Red anchor로 사용할 수 있다.

영구 decision/lifecycle과 이번 실행의 일시적 Red 비계는 섞지 않는다. Phase 2 진입 직전 Coordinator는
사용자가 이미 가진 tracked·untracked 변경을 포함한 accepted base tree manifest, index 상태, changed-path
목록을 고정하되 어떤 파일도 stage/reset하지 않는다. G1에서 승인된 exact test path의 존재/부재, path kind,
mode와 byte-exact preimage는 accepted manifest·G1 승인 digest에 결속한 unique `snapshot_generation`의
repo-external mode 0700 감사 snapshot에 O_EXCL로 보존한다. 이 snapshot은 3-way 표시와
accepted-base→final hunk 감사에만 쓰며 restore·inverse·작성자 판정에는 쓰지 않는다. G2 승인, 작업 중단,
또는 그 accepted base를 무효화하는 재기준선 중 먼저 온 terminal에서 exact snapshot directory를 폐기하고
결과를 보고한다. 사용자가 G2 전에 single-writer window를 닫아 편집을 재개하면 current G2 cycle은 중단되고
반드시 재기준선 terminal을 거친다. 재기준선은 이전 generation을 닫은 뒤 새 accepted manifest/G1 승인에
결속한 새 generation을 만들며 stale snapshot을 재사용하지 않는다.
이후 target tree의 모든 source/test/config 변경은
최종 diff 감사 대상이다. `.git` 내부만 비교 universe에서 제외하며, test 실행 부산물은
`PYTHONDONTWRITEBYTECODE=1`, pytest cache 비활성화 또는 repo-external cache 경로로 target tree 밖에 둔다.
formatter·package manager·test subprocess가 target tree를 바꾸려면 별도 승인된 code slice와 exact path가
필요하다. 그 밖의 새 path/delta는 출처를 추정하거나 지우지 않고 blocker로 사용자에게 보여 준다.

이 정책은 같은 UID의 role, Coordinator, subprocess, 사용자를 기술적으로 구별할 수 있다고 주장하지 않는다.
따라서 creator ID·mode 0700 journal·파일 단위 inverse를 작성자 증거로 쓰지 않고 자동 delete/rollback도 하지
않는다. G1에서 Coordinator는 Phase 2가 바꿀 exact test paths를 보여 주고, 그 paths에 대해 역할 dispatch가
끝날 때까지 사용자가 편집을 멈추는 명시적 single-writer window를 승인받는다. 승인받지 못하면 proposal만
보여 주고 target write/G2를 막는다. window 안에서는 test-path proposal과 적용을 순차 실행하며, 예상 밖
target delta가 보이면 작성자를 추정하지 않고 window를 닫아 사용자 보존·재기준선으로 반송한다.

`admit` 실행에 임시 import guard·skip/xfail·대체 decorator·loader helper가 정말 필요하면 owner는 쓰기 전에
`scaffold_id + parent_decision_id + owner + exact path/case + purpose + first-Green removal boundary`를 선언한다.
첫 Green 직후 Coordinator가 같은 owner에게 `owner-correction-required`를 보낸다. 별도 proposal-only 역할이나
존재하지 않는 per-dispatch sandbox를 주장하지 않는다. 기존 acceptance/coder가 자신의 Edit/Write/Bash 권한으로
직접 고치되, Coordinator가 첫 Green을 확인한 직후 accepted base와 구별되는 `correction checkpoint`로 각 exact
path의 current SHA를 고정해 owner에게 전달한다.
owner는 그 SHA의 current bytes를 다시 읽고 다음 tagged union 중 하나를 반환한다.

```text
applied-contextual:
  path + checkpoint/before/after SHA + exact applied hunk + removed scaffold IDs + retained decision IDs
checkpoint-drift:
  path + checkpoint/current SHA + write_count:0
conflict-awaiting-user:
  path + checkpoint/current/proposed SHA + byte-exact 재현 가능한 contextual patch 또는 whole-file proposal
  + removed/retained IDs + write_count:0
```

dispatch 직전 SHA가 correction checkpoint와 다르면 `checkpoint-drift`로 window를 닫고 사용자
보존·재기준선으로 반송한다. same-span conflict나 whole-file Write가 필요하면 owner는 쓰지 않고
`conflict-awaiting-user`로 돌아온다. Coordinator만 감사 snapshot·current bytes·proposal로 exact 3-way를
사용자에게 보여 주고 `current 유지 | proposal 채택 | 사용자 지정 merge | 중단` 중 명시적 선택을 받는다.
채택/merge이면 current SHA를 다시 확인해 새 correction checkpoint와 사용자가 고른 exact bytes/digest를 같은
owner에게 재-dispatch하고 owner가 직접 적용한다. 재확인 drift는 다시 write 0이며 owner가 직접 사용자에게
묻거나 Coordinator가 proposal을 대신 적용하지 않는다. `current 유지`가 scaffold를 남기면 승인이 cleanup을
면제하지 않으므로 G2는 계속 blocked이고 G1′ correction 또는 중단만 가능하다.

single-writer window에서는 acceptance/coder correction invocation을 하나씩만 실행한다. non-overlap contextual
Edit을 우선한다. owner 반환 직후 Coordinator가 target manifest를 직접 재해시하고 G2 직전
한 번 더 같은 digest를 확인한다. 사용자가 편집을 재개하려면 먼저 window를 명시적으로 닫고 새 checkpoint를
받아야 한다. 승인된 window를 어기는 외부 writer까지 기술적으로 격리한다고 주장하지 않으며, drift가
관찰되면 자동 merge/delete/restore하지 않는다. 파일·mutation 단위 inverse는 없다. 실제 프로젝트의
semantic 보존 oracle은 decision/hunk 대조와 관련 테스트이며, synthetic B12 fixture에서만 hidden expected
final digest를 쓴다.

Phase 2 reviewer는 감사 snapshot으로 재구성한 accepted base→final diff의 변경된 test hunk마다 정확히 하나의
영구 decision 또는 제거가 끝난 scaffold ID를 대조하고, owner tagged result·exact applied hunk·사용자 선택
artifact·before/after/current/final digest와 single-writer 승인 기록을 확인한다. 작업
전부터 있던 동일한 guard/skip/helper는 scaffold로 사후 등록할 수 없고,
그 bytes의 변경·삭제에는 `terminate` 또는 `lifecycle-approved(consolidate-preserving)`가 필요하다. G2에서는
scaffold와 decision 없는 test delta가 0이어야 한다. 구조화 산출의 `execution_action`은
`none|owner-correction-required`로 닫고, 영구 decision/lifecycle row는 항상 `execution_action:none`이다.

### 3.4 decision row 필수값

명세 어느 절에서든 영구 test file/case/assertion/fixture/snapshot/helper를 생성·추가·강화·기대 변경·
split·이동·삭제·약화하라고 지시하면 정확히 하나의 decision ID를 가져야 한다. 사전 등록되고 G2 전에
owner correction으로 제거된 current-run scaffold만 예외이며, 살아남는 순간 영구 artifact로 간주해
decision 누락 blocker가 된다.

```text
decision_id
candidate_or_exact_existing_artifact
decision + 허용된 lifecycle_action
protection_class 또는 ineligible/pending reason
authoritative_requirement/support/consumer evidence
owner + boundary
unique_defect_or_guarantee + full_case_partition
existing_authoritative_tests + overlap result
counterpart decision IDs(교체·split·이동·consolidation일 때)
```

owner/boundary 허용 조합도 중앙에서 고정한다.

```text
owner:acceptance-tester
  boundary:http-wire | published-event-wire | public-python-consumer-contract | observable-system
owner:coder
  boundary:application-policy | domain-invariant | db-guarantee | adapter-protocol
owner:non-test-owner
  boundary:not-applicable   # reject/pending
```

`covered-no-new-test`는 기존 권위 테스트의 owner/boundary를, `lifecycle-approved|terminate`는 대상 artifact의
기존 owner/boundary를 보존한다. 같은 ErrorOut surface의 public-Python exact shape와 mounted HTTP
wire는 하나로 합치지 않는다. 독립 consumer/승인 근거가 있는 public-Python row와 status/body/header/
OpenAPI wire row를 별도 partition으로 판정한다. Python 근거가 없으면 direct Schema 후보는 HTTP가
보호하는 범위에서 `covered-no-new-test`이거나 비자격이지만, Python 근거가 있으면 HTTP 테스트가 대신할 수 없다.

한 문장이 구현 결정을 설명할 뿐 영구 테스트를 지시하지 않으면 row를 만들 필요가 없다.
반대로 `Test criteria`, `response/OpenAPI/tests`, Risky Write, reviewer 제안, layout 규칙도
영구 artifact를 지시하는 순간 예외 없이 row가 필요하다.

### 3.5 migration 8분기

기존의 “migration history 자체는 자동 테스트하지 않는다” 정책은 유지하되 합법적인 legacy
계약을 의미 없음으로 소실하지 않는다.

| 분기 | 기본 결과 |
|---|---|
| `implementation-only` — migration module/function/과거 state/bytes/hash 자체만 oracle | current DB/repository 경계로 전환하거나 `reject` |
| `concrete-forward-transform` | `pending(reason:policy-conflict)` |
| `explicit-irreversible` | `pending(reason:policy-conflict)` |
| `reverse-required` | `pending(reason:policy-conflict)` |
| `reverse-undecided` | `pending(reason:policy-conflict)` |
| `time-bounded-compatibility` | `pending(reason:policy-conflict)` |
| `support-period-not-applicable` | `pending(reason:policy-conflict)` |
| `missing-policy-fact` | `pending(reason:policy-conflict)` |

뒤 일곱 분기는 fixture·reverse·지원 기간이 모두 있을 때만 인정하는 conjunctive 조건이 아니다.
구체 legacy transition fact 하나라도 있으면 별도 사용자 정책 승인 전 자동 admit/reject/test 생성
모두 금지한다. 승인 뒤에는 그 bounded migration contract를 일반 입장심사에 다시 넣는다.

---

## 4. 최소 pressure 검증 설계

### 4.1 영구 자산은 5개로 제한한다

| 파일 | 책임 |
|---|---|
| `workspace/pressure/meaningful-tests/README.md` | 범위·재실행 조건·raw-never-Git·퇴역 규칙 |
| `workspace/pressure/meaningful-tests/cases.jsonl` | 초기 case와 append-only holdout의 entrypoint role/stage/bundle mode, 중립 prompt, inline fixture, exact decision/file effect oracle |
| `workspace/pressure/meaningful-tests/schema.json` | 모델 구조화 응답과 tracked evidence enum schema |
| `workspace/pressure/meaningful-tests/evidence.jsonl` | ledger-header·case-register·attempt-start·terminal·commit-recovery·source-resolution·invalidate·review-closure typed event만 append |
| `workspace/tools/run_meaningful_test_pressure.py` | source bundle 조립, no-tools provider 호출, 임시 patch 적용, 채점, self-check |

별도 pytest, fixture tree, auth broker, secret scanner, action environment attestation, closure author/screener
프로토콜, custom Git ODB/index/ref 도구는 만들지 않는다. runner self-check는 third-party Python package 없이
stdlib와 executor의 사전 검증된 systemd/cgroup 명령만 사용하며, fake provider와 `mktemp -d` fixture를 실행
중에 만들고 종료 시 제거하는 일회 검증이다.

신뢰 경계도 여기서 닫는다. maintainer runner, 일반 Git, Linux systemd/cgroup v2 executor와 선택한 provider
adapter가 assigned phase cgroup을 벗어난 daemon을 만들지 않는다는 실행 계약은 신뢰하고 model/provider
출력은 신뢰하지 않는다. pressure 실행 prerequisite는 두 provider CLI를 실행할 수 있는 Linux executor,
systemd transient-unit manager, cgroup v2와 unit InvocationID/membership 조회·stop capability다. 현재 Darwin
host에서 이를 흉내 내지 않으며 사용자가 승인한 local Linux VM 또는 remote CI executor가 없으면 Task 0에서
중단한다. executor를 자동 provision하지 않고 exact command/flag는 구현 때 installed `--help`와 capability
self-check로 확정한다. adapter가 cgroup 계약을 제공하지 못하거나 descendant escape가 관찰되면 해당 runtime
pressure는 blocked다. 악의적인 maintainer, 같은 UID가 `.git/objects`를 직접 변조하는 공격, OS root 공격은 이번
테스트 정책 목표 밖이다. runner는 sequential이고 한 invocation 내부 transport retry는 0으로 유지한다.
허용된 infra 재시도도 새 tracked attempt로만 열며 callback/plugin/
concurrency framework를 만들지 않는다. 구현이 약 500 LOC를 넘기 시작하면 안전 규칙을 잘라내는
hard cap으로 쓰지 않는다. runner가 500 nonblank/non-comment physical lines를 넘거나 bundle loader·provider
supervision·Git evidence·patch scorer·schema reducer의 다섯 책임 밖 여섯 번째 책임이 생기면 Task 0을 멈추고
실제 LOC/책임표와 scope 축소안을 사용자에게 보여 명시적 승인을 받는다. 승인 없이 파일을 더 늘리거나 한
runner에 계속 밀어 넣을 수 없다.

### 4.2 모델은 파일을 직접 수정하지 않는다

- case는 임의 source path·heading 목록이 아니라 `entrypoint_role + stage + bundle_mode`를 지정한다.
  runner가 Claude role frontmatter의 `skills:`와 Codex 역할의 `로드할 지식 스킬` 선언을 직접 parse해
  role의 exact loader set을 계산한다. 핵심 admission/handoff case의 `loader-minimal` bundle은 실제 runtime이
  preload하는 role 본문과 선언된 모든 SKILL의 **전체 bytes**만 포함하며 reference를 편의상 주입하지 않는다.
  이 모드가 통과하지 않으면 중앙 정책이 실제 loader에 도달했다는 완료 증거가 아니다.
- reference carrier case의 `route-expanded` bundle은 case가 heading을 고르지 않는다. case는 닫힌
  `scenario_route_key`만 주고, runner가 SKILL 본문의 `상세 레퍼런스` 표·명시적 route에서 target path와
  heading을 유일하게 도출한다. 해당 heading과 하위 절 전체를 peer heading 전까지 넣고, SKILL이 whole-file
  read를 지시하면 전체 file을 넣는다. route가 없거나 둘 이상이거나 case 기대와 다르면 provider 전
  blocked다. 이 결과는 `bundle_mode:route-expanded`로 표시하며 실제 runtime의 선택적 Read를 관찰한 것처럼 과장하지
  않는다. Task 6의 full-corpus carrier inventory가 선택되지 않은 heading의 우회 명령 0을 별도로 증명한다.
- missing/extra/misdeclared skill·route는 provider 호출 전 실패한다. 두 mode 모두 canonical
  `role/stage/bundle_mode/path/length/SHA-256` manifest를 만들고 그 digest를 evidence에 남긴다.
- runner는 위에서 도출한 prompt/role/SKILL/reference bytes와 inline synthetic fixture만 입력한다.
- `candidate exact-source-tree`는 current Task가 연 exact plugin/corpus source allowlist의 path·mode·bytes
  canonical manifest다. pressure 5개 자산, repo-external raw/journal, target Django 프로젝트와 일반 사용자
  문서는 이 digest에서 제외한다. holdout/ledger append는 candidate source를 바꾸지 않으며 실제 role/SKILL/
  reference/Coordinator 변경만 source change가 된다. loaded bundle이 바뀌지 않는 allowlisted source 변화는
  아래 same-source-equivalent 심사를 그대로 받는다.
- model-visible projection은 중립 task text, synthetic fixture, source bundle, 이전 stage의 schema artifact,
  response schema만 포함한다. `case_id`와 B/P 접두사, baseline/development/holdout partition, repetition,
  logical-case/campaign/attempt ordinal과 invocation ID, expected decision/file effect, runner 전용
  `scenario_route_key`는 0이다. self-check는
  각 금지값에 canary를 넣고 provider stdin/prompt digest 직전 bytes 어디에도 나타나지 않음을 검증한다.
- Claude는 실제 설치본이 지원하는 tool/MCP/session 비활성 옵션을 사용한다. Codex CLI에 도구 전체를
  끄는 옵션이 없으면 빈 repo-external cwd, read-only sandbox, user config/rule 비활성화를 쓰고 실제
  tool event가 하나라도 생긴 invocation은 `blocked/non-comparable`로 처리한다. 이것으로도 경계를
  증명할 수 없으면 tool definition이 없는 별도 provider adapter를 사용하거나 Codex pressure를
  미완료로 보고한다. 존재하지 않는 flag를 발명하지 않는다.
- 모델은 JSON decision과 필요한 경우 whole-file replacement patch만 반환한다. behavioral network는
  금지하고 CLI 자체의 provider transport만 허용한다.
- runner가 patch를 repo 밖 임시 fixture에 적용하고 required/forbidden file effect를 채점한다.
- 실제 저장소와 `broccoli-server`를 provider cwd나 readable input으로 주지 않는다.
- installed dddjango plugin/cache와 자동 behavioral prompt를 비활성화할 수 없는 runtime 결과는
  `blocked/non-comparable`로 기록하며 반대 runtime 결과로 대체하지 않는다.
- 구현 시 `claude --help`, `codex exec --help`로 실제 비대화형·structured-output·plugin/config
  격리 option을 확인하고 기억한 flag를 발명하지 않는다.

다단계 case는 역할 문서를 한 prompt에 합치지 않는다. Architect, discipline reviewer, Coordinator를
각각 독립 invocation으로 실행하고, 앞 stage의 schema-validated artifact bytes와 digest를 다음 stage의
명시 입력으로 넘긴다. evidence는 `parent_stage_invocation_id + input_artifact_sha256 +
output_artifact_sha256`를 결속한다. 특히 B6는 Architect decision→Phase 1 review→Coordinator/G1 route
세 산출을 순서대로 검증해 중간 handoff에서 pending이 소실되는 버그를 잡는다.

이 방식은 B5의 “첫 Green 뒤 비계가 실제로 사라지는가”도 모델이 제안한 patch를 runner가
synthetic tree에 적용해 검증한다. model process에 repository write 권한을 주기 위한 VM/container,
PID namespace, snapshot은 필요하지 않다. 다만 provider process-tree 회수는 §4.3의 user-approved Linux
systemd/cgroup v2 executor prerequisite를 그대로 따른다.

patch는 unified diff나 실행 코드가 아니라 `path + create|replace|delete + base_sha256 + content_utf8`
배열이다. case별 exact 상대경로 allowlist만 허용하고 절대경로·`..`·symlink·binary·special file을
거부한다. replace/delete는 fixture의 base digest와 정확히 같아야 하며 file/response size cap을 둔다.
runner는 모델이 만든 Python·shell·test를 import하거나 실행하지 않고 최종 path set·raw content
digest·금지/필수 predicate만 정적으로 채점한다. hidden oracle과 expected bytes는 prompt projection에서
제외됐는지 self-check가 확인한다.

file-effect positive는 사전에 정의된 preserve/delete/move/split/scaffold-owner-correction 효과로 한정하고,
새 테스트의 실제 제품 정확성을 이 pressure가 인증한다고 주장하지 않는다. 이 검증은 동결된 prompt
source가 표적 admission/lifecycle 상황에서 어떤 decision과 patch를 내는지의 증거다. 실제 구현 테스트의
정확성은 target 프로젝트의 정상 Red/Green·관련 suite·discipline review가 별도로 소유한다.

### 4.3 provider raw는 Git에 넣지 않는다

```text
provider stdout/stderr
  → start-gated provider session + parent-owned capped pipes
  → repo-external mode 0700 attempt directory의 stdout/stderr O_EXCL raw file
  → durable launch marker → gate release → process-group/pipe EOF 회수 → provider-complete marker
  → schema parse 및 임시 fixture 채점
  → Git evidence에는 enum·ID·digest·정수 score만 재직렬화
```

- provider의 rationale, stdout/stderr, patch bytes, 자유 문자열은 tracked evidence에 넣지 않는다.
- runner는 exec-replace되지 않는 **phase supervisor 하나**와 parent-liveness pipe를 사용한다. fresh phase
  directory/input snapshot과 parent를 fsync한 뒤, parent가 provider/session spawn 전에 unique never-reused
  `phase_unit_name + phase_generation + boot ID`의 `phase-launch-intent`를 durable publish한다. Linux executor는
  supervisor를 그 이름의 manager-owned systemd transient **service**/cgroup v2에서 시작한다(`scope`는 쓰지
  않는다). service는 runner/recovery가 closure를 승인할 때까지 manager의 InvocationID와 terminal result를
  조회할 수 있게 유지한다. installed systemd에서 이 retention 의미를 제공하는 property/capability가 없으면
  Task 0에서 blocked다. runner가 manager의 exact unit
  InvocationID, cgroup path, supervisor birth를 조회해 `supervisor-ready` marker를 fsync→publish→phase/root
  parent fsync한 뒤에만 phase plan/attempt-start를 commit한다. intent 전에는 spawn 0이고, intent 뒤 ready 전
  crash도 unit name을 조회해 absent 또는 exact InvocationID/cgroup membership 0으로 닫을 수 있다.
- 각 invocation에서 parent는 spawn 전 `phase unit InvocationID + logical invocation key + launch generation`의
  `launch-intent`를 durable publish한다. supervisor가 만드는 gated launcher는 생성 순간부터 phase cgroup
  안에 있다. 그 뒤 provider exec 전 session/leader identities의 `launch-prepared` marker를 fsync→publish하고
  gate를 연다. spawn 직후 prepared 전 crash도 launch-intent의 phase unit을 stop/drain해 membership 0을
  증명한다. launcher는 gate와 supervisor-liveness를 함께 감시해 gate 전 liveness가 끊기면 semantic output
  0인 채 종료한다.
- provider stdout/stderr에는 raw file FD를 직접 주지 않는다. parent가 capped pipe를 읽어 O_EXCL mode 0600
  raw에 쓰는 유일한 writer다. timeout/size cap/정상 exit 모두 recorded session의 종료와 두 pipe EOF를 확인한
  뒤 raw를 fsync·rehash한다. descendant가 pipe를 잡고 있으면 bounded timeout 뒤 recorded session을 drain하고
  EOF까지 회수한다. parent가 죽으면 liveness EOF를 본 supervisor가 같은 절차를 수행하고, 가능한 경우
  `phase-exit-ready(exit_kind:parent-liveness-lost)`를 durable publish한 뒤 종료한다. parent crash 뒤에는
  provider가 raw를 더 쓸 수 없다. supervisor 자체가 이 marker 전에 죽는 경로는 아래 외부 recovery가 닫는다.
- recovery는 bare numeric PID/PGID/session ID를 signal하지 않고 `birth 확인→kill(pid)`도 금지한다. boot ID가
  달라졌으면 이전 process가 소멸한 것으로 본다. 같은 boot에서는 marker의 never-reused unit name과 manager
  InvocationID가 모두 일치할 때만 systemd unit stop으로 identity-bound cgroup 전체를 종료하고 membership 0을
  기다린다. unit이 absent면 membership 0, 이름은 같지만 InvocationID가 다르면 새 unit이므로 signal 0·blocker다.
  bounded unit stop/membership 0을 증명하지 못하면 terminal을 꾸미지 않고 phase를 막는다.
- provider exec 전 crash는 별도 prelaunch 경로다. attempt-start의 `phase-launch-intent|supervisor-ready`와
  invocation의 `launch-intent` digest를 기준으로 exact phase unit/cgroup을 닫는다. durable `launch-prepared`
  marker가 없고 gate가 열린 적 없으며 phase cgroup membership 0 또는 boot-changed, parent-owned raw의 semantic
  output length 0을
  함께 증명할 때만 `prelaunch-blocked(reason:runner-crash-before-launch|launch-setup-failure)`로 닫는다.
  이 증거가 부족한 same-boot 상태는 열린 recovery blocker로 남기며 새 attempt나 완료를 허용하지 않는다.
- 정상 종료도 명시적으로 닫는다. 모든 planned invocation terminal 뒤 runner는 `phase generation + unit
  InvocationID + terminal-set digest`의 `phase-close-intent`를 durable publish한 뒤 새 invocation 수락을 막고
  정상 shutdown을 요청한다. supervisor는 recorded session drain과 pipe EOF를 끝내고
  `phase-exit-ready(exit_kind:normal + intent digest + supervisor birth)`를 durable publish한 뒤 종료한다.
  supervisor는 systemd manager 소유이므로 runner가 direct-child라고 주장하거나 `waitpid`하지 않는다. runner
  또는 recovery가 retained unit의 exact InvocationID, manager result=`success`, cgroup membership 0과
  close-intent/exit-ready의 같은 generation·terminal-set을 대조해 `phase-manager-exit-observed`를 먼저 durable
  publish한다. 그 뒤 unit을 release/stop하고 inactive 또는 absent+never-reused-name과 membership 0을 확인해
  `phase-supervisor-closed`를 idempotent하게 fsync→publish→directory/parent fsync한다. 정상 exit 뒤 어느
  경계에서 runner가 죽어도 retained manager state 또는 exit-observed marker로 recovery가 같은 closed marker를
  완성할 수 있다.
- close-intent·정상 exit-ready·manager result=`success`의 generation/terminal-set 일치 tuple 중 하나라도 없거나
  supervisor가 SIGKILL·OOM·비정상 종료했다면 manager result가 success여도 정상 closed로 승격하지 않는다.
  unit이 이미 terminal이면 result의 성공/실패를 가르지 않고 실제 retained result, 누락·불일치한 tuple field,
  cause와 membership을 먼저 `phase-manager-terminal-observed(actual result + manager state +
  missing-normal-tuple digest)`에 fsync→publish→directory/parent fsync해 result가 사라지기 전에 결속한다.
  manager state가 inactive/absent가 아니거나 membership이 남아 있으면 `unit name + InvocationID + phase
  generation + cause + terminal-observed digest + manager transition`의 `phase-stop-intent`를 durable publish한
  뒤 exact unit에만 stop/release/reset-failed 중 installed manager가 제공하는 사전 검증된 전이를 실행한다.
  membership 0이면 process signal은 0이지만 failed/retained manager state를 inactive/absent로 옮기는 manager
  전이는 생략하지 않는다. 이미 inactive/absent이고 membership 0인 경우만 manager transition도 0이다.
  inactive 또는 absent+never-reused-name과 membership 0을 확인하고
  `phase-manager-exit-observed(exit_kind:abnormal-terminal + terminal-observed/transition-result digest)`를 durable
  publish한 뒤 공통 suffix의 `phase-supervisor-crash-closed`를 publish한다.
- unit이 active·wedged면 manager result를 선행 요구하지 않고 같은 형식의 `phase-stop-intent`를 durable publish한
  뒤에만 exact unit stop을 요청한다. recovery는 같은 intent/InvocationID에만 stop을 idempotently 재개한다.
  stop job/terminal result, inactive 또는 absent+never-reused-name, cgroup membership 0을 확인한 뒤
  `phase-manager-exit-observed(exit_kind:forced-stop + stop-intent/result digest)`를 durable publish하고 모든 abnormal
  하위 경로와 같은 `phase-supervisor-crash-closed` suffix를 완성한다. stop/result/observed/crash-closed 사이 어느
  crash도 stop-intent와 retained manager state로 복구하며, 이를 제공하지 못하는 executor는 Task 0에서 blocked다.
  marker가 이미 있으면 byte-exact 동일할 때만 인정하고 충돌하면 blocker다. crash-closed는 실패 phase를 닫을 뿐
  review-closure의 final PASS proof가 될 수 없다.
- invocation session drain과 완전 pipe 회수 뒤 exit class·stdout/stderr 각 length/SHA를 가진
  `provider-complete` temp marker를 O_EXCL로
  완성·fsync한 뒤 final marker로 atomic publish하고 directory를 fsync한다. 이 marker만 raw 완결성 증거다.
- 별도 patch raw file을 만들지 않는다. patch는 complete stdout JSON에서 매번 결정적으로 재도출해
  임시 fixture에만 적용하고 digest만 terminal에 쓴다.
- raw 보존은 구현 리뷰가 끝날 때까지다. 이후 삭제 여부는 사용자에게 보고하고 결정한다.
- secret 가능성이 있는 raw도 저장소 밖에 머물고 tracked row에는 commitment만 남는다.

runner는 attempt root가 repository와 `.git` 바깥인지 resolved path/common-path로 확인하고, symlink
component가 없는 fresh mode `0700` phase/attempt directory를 만든다. 생성 직후 각 directory와 그 parent를
fsync하며 input snapshot publish 뒤에도 attempt directory와 attempt-root parent를 다시 fsync한다. attempt ID
재사용·truncate·overwrite는 금지한다.
tracked schema는 event kind와 terminal subtype 각각에 `oneOf`와 `additionalProperties: false`를 쓴다.

최초 `ledger-header`는 `header_generation=1`, `supersedes_lineage_root_sha256:null`,
`campaign_lineage_root_sha256`, `semantic_correction_budget=2`, 초기 active case registry와
`evaluation_harness_sha256`을 먼저 고정한다. harness digest는 committed runner·schema와 그 안의 scoring rule
bytes를 canonical manifest로 결속한다. correction은 기존 header를 고치지 않고 `lineage-correction` commit에
generation+1의 새 `ledger-header`를 append한다. predecessor는 provider 호출 0인 abandoned root이거나 명시적
NO-GO+사용자 승인 root여야 하며 새 header의 `supersedes_lineage_root_sha256`가 이를 가리킨다. reducer는 이
유효 chain의 leaf header가 정확히 하나일 때만 그것을 active header로 사용하고 fork/복수 leaf는 blocker로
막는다. harness/case/infra correction header는 predecessor의 logical failure와 spent semantic-correction
counter를 상속해 family-wide budget 2를 reset하지 않는다. budget 소진 뒤 별도 정책 자체를 재설계하는 경우만
명시적 사용자 승인·새 family root·전체 baseline/final/holdout으로 분리한다. 각 case의 immutable
`logical_case_sha256`은 표시용 `case_id`가 아니라
canonical task text, synthetic fixture, hidden oracle, scenario route, entrypoint role, bundle mode, stage DAG의
digest다. 첫 provider 호출 뒤 기존 `cases.jsonl` prefix는 byte-immutable이고 새 holdout canonical line만
append할 수 있다. holdout은 provider 호출 전에 그 line과 typed `case-register`를 같은 `holdout-register`
commit으로 봉인한다. `case-register.registry_action`은
`append-holdout|supersede-defective-case|preserve-exposed-holdout`으로 닫는다.
`append-holdout|supersede-defective-case` register row는 prior cases prefix/blob digest, appended line digest,
resulting cases blob, logical-case digest를 결속한다. `supersede-defective-case`는 lineage-correction 안에서만 허용되고 old/new logical hash, defect evidence, 사용자 승인과
old=`inactive-defect`/new=`active` registry transition을 새 header에 결속한다. old line은 삭제·rewrite하지 않고
new canonical replacement line을 append하므로 history를 보존하며 ordinary holdout으로 세지 않는다.
`preserve-exposed-holdout`은 hook-failed holdout-register의 intended batch/cases line을 whole-batch recovery로
byte-exact 인증한 경우에만 old logical hash를 rewrite 없이 `active-development`로 재분류한다. 이 branch는
failed seal·그 seal의 recovered `append-holdout` row digest·recovery row digest·existing line/blob digest와
recovery 뒤 unchanged resulting cases blob을 결속하고 appended-line field를 금지한다. 이 row는 별도
preserve-only commit이나 다음 정상 register에 쓰지 않고, 해당 failed holdout-register 전용 `commit-recovery`
commit의 ordered event batch 마지막에 정확히 하나만 쓴다. 인증할 수 없으면 row·replacement를 만들지 않고
blocker다. 새 독립 holdout을 append하는 다음 정상 register, 이후 생기는 모든 header와 review-closure는
preserved old hash와 new holdout hash를 모두 active registry에 결속하고 전체 matrix는 둘 다 실행한다.

planned invocation key는 `logical_case_sha256 × runtime × repetition_slot × stage × entrypoint_role ×
bundle_mode`이며 `repetition_slot`은 정확히 `1|2|3`이다. provider/infra 재시도 횟수는 별도
`attempt_ordinal`이고 새 repetition slot으로 위장할 수 없다. `case_id`는 사람이 보는 label일 뿐 reducer
identity가 아니다.
provider 전 runner는 candidate source bundle bytes와 canonical manifest, root prompt, downstream prompt
template을 repo-external attempt directory의 O_EXCL input snapshot으로 쓰고 fsync한다. `attempt-start`는
이 key 전부와 stage DAG, runner-generated invocation ID, current boot ID, phase/supervisor generation,
phase unit name/InvocationID, `phase-launch-intent|supervisor-ready` marker digests, candidate exact-source-tree manifest digest,
key별 `bundle_manifest_sha256`, runtime/version/isolation/adapter의 `evaluation_configuration_sha256`, root의
`prompt_sha256` 또는 downstream의 `prompt_template_sha256`, ledger와 같은 `evaluation_harness_sha256`을 고정한다.
B6 같은 downstream key는 parent invocation ID와 input source가 `parent-output`이라는 사실만 기록하고
아직 생기지 않은 artifact digest를 발명하지 않는다. terminal 공통 필드는 key, bounded runtime/version,
`candidate_source_tree_sha256`, `bundle_manifest_sha256`, `evaluation_configuration_sha256`,
`evaluation_harness_sha256`이며 terminal의 bundle/config/harness digest는 attempt-start의 같은 key 값과
같아야 한다. 실제 `input_artifact_sha256`와 final
`prompt_sha256`은 parent success 뒤 prompt가
만들어진 terminal branch에만 들어간다.
loader/route/schema parse와 초기 CLI capability preflight는 attempt-start 전에 전 invocation에 통과해야
하며, 여기서 실패하면 attempt를 열지 않는 pressure-infra 오류다. 다음 terminal은 유효 plan 뒤의
post-plan source와 snapshot digest가 다르거나 prompt 조립/launch가 실패하는 경우까지 표현한다.
terminal subtype은 다음으로 닫는다.

| terminal subtype | 가능한 증거 |
|---|---|
| `dependency-blocked` | reason oneOf: `parent-not-success`는 parent invocation/terminal digest, `campaign-selection-risk-stop`은 선행 unknown/complete-invalid terminal과 lineage digest; 두 branch 모두 launch/complete/raw/prompt field 없음 |
| `prelaunch-blocked` | `prompt_state=ready|not-built`별 oneOf. ready는 parent/input/prompt digest, not-built는 parent/input 또는 root null과 prompt field 부재. reason은 candidate-source-drift, plan-commit-hook-drift, input-snapshot-loss, input-snapshot-mismatch, prompt-build-failure, prompt-size-cap, isolation-drift, transport-drift, runner-crash-before-launch, launch-setup-failure의 닫힌 enum; launch-prepared/complete 없음(`launch-intent`는 crash branch에 허용), semantic output length=0, reason별 canonical resolution record/digest |
| `complete-success` | complete marker와 stdout/stderr commitments, `semantic_output_length>0`과 digest, schema-validated decision·`lifecycle_action`·`execution_action`·owner·boundary, parent/input/output artifact digest, patch/file-effect digest, `oracle_pass=true` |
| `semantic-output-fail` | complete marker와 stdout/stderr commitments, `semantic_output_length>0`과 digest, reason은 `malformed-json|schema-invalid|oracle-fail|refusal|tool-use` exact enum; 성공 semantic field 없음 |
| `provider-infra-fail-before-model-output` | complete marker와 stdout/stderr commitments, `semantic_output_length=0`과 canonical empty digest. reason은 `rate-limit|provider-unavailable|connect-failure|dns-failure|tls-failure|provider-timeout|credential-refresh-failure|auth-failure|model-not-found|endpoint-configuration-failure|adapter-bootstrap-failure|adapter-protocol-failure|adapter-exit-zero-output|terminated-by-signal|resource-oom|local-time-cap|local-size-cap|local-resource-exhausted` exact enum; decision/oracle/patch field 없음 |
| `unknown` | parent/input/prompt digest, durable launch-intent/prepared와 phase unit InvocationID digest, complete 없음, exact `phase-supervisor-crash-closed` 또는 boot-changed 증거, unknown reason enum; semantic output state는 unknown이고 불완전 raw를 성공·infra-retry 근거로 쓰지 않음 |
| `complete-invalid-before-terminal` | parent/input/prompt digest, complete marker는 있으나 terminal 전 raw 부재/불일치 reason enum과 complete-marker digest; 성공 semantic field 없음 |

`semantic_output_length`는 provider protocol의 model-answer channel만 센다. CLI 진단·HTTP error·stderr bytes는
raw commitment에는 포함되지만 semantic output으로 승격하지 않는다. 단 한 byte라도 model-answer channel에
도착하면 provider 장애 enum으로 강등할 수 없고 `semantic-output-fail` 또는 success parse 경로를 탄다.
`oracle_pass=false`, malformed JSON, schema failure도 모두 semantic 실패다.

root stage는 parent/input digest가 `null`인 success branch, downstream stage는 runner-generated parent ID와
input digest가 필수인 별도 success branch다. output artifact가 없는 terminal subtype에는 그 필드를 넣지
않는다. `event`, `phase`, `stage`, `entrypoint_role`, `bundle_mode`, `decision`, `lifecycle_action`,
`execution_action`, owner,
boundary, terminal subtype, reason은 사전 enum이다. attempt/invocation ID는 runner-generated restricted
regex/digest, version은 bounded normalized identifier다. 그 밖에는 digest·길이·boolean·bounded integer만
허용한다. provider가 정하는 arbitrary identifier, absolute/temp/raw locator, rationale, exception text,
patch body는 0이다.
이 폐쇄형 projection 때문에 provider credential set을 재구성하는 custom secret scanner는 필요하지 않다.

따라서 provider raw를 Git에 옮기기 위한 scanner/auth commitment, quarantine object,
`commit-tree`, index install, ref CAS, capsule audit은 전부 불필요하다.

### 4.4 선택적 성공 보고를 막는 작은 장치

tracked evidence event는 `ledger-header | case-register | attempt-start | terminal | commit-recovery |
source-resolution | invalidate | review-closure`의 폐쇄형 합이다. `source-resolution`은 아래
`repair-complete` 증명 전용이며 ordinary retry·source adoption에는 쓸 수 없다. bootstrap 뒤 각 pressure phase는 최소 세 개의 표준 Git commit으로
증거를 닫고, 새 holdout이 있는 phase는 먼저 별도 register commit을 더한다.

1. **holdout-register commit(해당할 때):** provider 호출 전 `cases.jsonl`의 기존 trusted prefix에 canonical
   holdout line만 append하고, prior/resulting cases blob·line·logical-case digest가 일치하는 `case-register`를
   함께 append한다. 이 multi-file commit의 exact post-commit 검증 전에는 해당 holdout plan을 열지 않는다.
   단, hook-failed register의 `preserve-exposed-holdout` row는 이 정상 경로가 아니라 §4.3의 전용 recovery
   batch에만 속하며 cases line을 새로 append하지 않는다.
2. **plan commit:** `attempt-start` row에 base HEAD, candidate exact-source-tree manifest digest, exact logical
   key·`repetition_slot=1|2|3`, stage DAG와 evaluation harness digest를 append한다.
3. **terminal commit:** 계획된 모든 invocation에 §4.3 terminal subtype 중 정확히 하나의 terminal
   row를 append한다. 누락·추가·중복이 있으면 phase는 완료가 아니다.
4. **review-closure commit:** 최종 리뷰 직전에 terminal subtype별 기대 외부 상태를 다시 감사하고
   logical case registry/cases blob, evaluation harness, attempt terminal-set, commit-recovery-set, invalidate-set,
   selection-risk-resolution-set과 unresolved selection-risk set,
   `phase-supervisor-closed|phase-supervisor-crash-closed|boot-changed` proof digest를 가진 closure row를 append한다.

runner는 외부 attempt journal과 tracked plan을 대조한다. crash 뒤 provider-complete와 raw가 유효하면
같은 bytes의 parse/score만 재개한다. complete는 있으나 terminal 전 raw가 없거나 다르면
`complete-invalid-before-terminal`로 닫는다. launch 뒤 crash는 §4.3의 recorded session을 verified drain한
뒤에만 `unknown`으로 닫고, drain을 증명하지 못한 same-boot 상태는 terminal이 아니라 전체 phase blocker다.
launch 전 crash는 gate unopened·semantic output 0·exact phase unit membership 0 증거가 모두 있을 때만
`prelaunch-blocked`로 닫는다. post-plan source/hook/prompt/isolation 실패는 root key를 launch 없는
`prelaunch-blocked`로, 실행 불가능해진 downstream key를 `dependency-blocked`로 닫는다. 실패 record를
지우거나 같은 invocation ID를 성공으로 재호출하지 않는다.

review closure는 terminal subtype별로 다르다. `dependency-blocked`는 reason별 parent terminal 또는 선행
selection-risk terminal/lineage digest와
launch-intent/prepared/complete/raw/prompt 부재, `prelaunch-blocked`는 launch-prepared/complete 부재와
semantic output 0(launch-intent가 있으면 exact unit membership 0),
`complete-success|semantic-output-fail|provider-infra-fail-before-model-output`은 complete marker와 exact raw
commitments 및 semantic output length/digest,
`unknown`은 durable launch/unit identity·complete 부재·phase-supervisor-crash-closed 또는 boot-changed
소멸 증거,
`complete-invalid-before-terminal`은 complete marker와 기록된 부재/불일치 상태를 확인한다. 모든 subtype에서
attempt-start의 immutable input snapshot과 key별 bundle/config/root-prompt 또는 downstream-template digest를
먼저 재검증하되, `prelaunch-blocked(reason=input-snapshot-loss|input-snapshot-mismatch)`만 기록된 부재/불일치를 대신
검증한다. terminal 뒤
raw/marker가 사라지거나 digest가 달라지면 기존 terminal을 고치지 않고 original terminal digest를
가리키는 `invalidate` row를 append한다. invalidated terminal은 closure가 raw를 다시 요구하지 않고
invalidate reason과 기대 부재/불일치를 감사하므로 실패 attempt도 닫을 수 있다.

terminal별 감사 뒤 phase-level process proof를 별도로 검증한다. 정상 phase는 exact unit InvocationID의
`phase-supervisor-closed` marker와 cgroup membership 0, crash phase는 `phase-supervisor-crash-closed` 또는
boot-changed가 필수다. selected final PASS는 정상 closed marker만 허용하며 crash/boot proof는 실패 phase를
closed로 만들 뿐 PASS로 승격하지 않는다.

`closed attempt`와 `effective PASS`를 분리한다. planned key마다 terminal 1개와 유효 closure 1개가 있으면
fail/blocked/unknown/invalidated attempt도 이력상 closed다. 다만 후속 호출은 아래 subtype별 규칙이 명시적으로
허용할 때만 시작할 수 있다. 선택한 final
attempt의 PASS는 planned=terminal exact, 모든 terminal=`complete-success`, 모든 `oracle_pass=true`,
dependency-blocked/semantic-output-fail/provider-infra-fail-before-model-output/prelaunch-blocked/unknown/
complete-invalid-before-terminal 0, exact `phase-supervisor-closed` 1, invalidate 0, 유효 review-closure 1일 때만
성립한다. 과거의 closed
실패·invalidated attempt는 지우지 않지만 아래 same-source reducer를 통과한 새 final attempt는 선택할 수 있다.
closure 뒤 사용자 승인으로 retention을 종료할 수 있지만 그 뒤 replay 가능성은 주장하지 않는다.

`semantic-output-fail | unknown | complete-invalid-before-terminal`은 공통 `selection-risk terminal`이다.
선택 final과 같은 candidate source-tree digest·겹치는 invocation key를 가진 **unresolved** 과거
selection-risk terminal이 있으면 우연한 새 model output을 고른 것으로 보아 PASS를 금지한다.
malformed JSON·schema/oracle 실패·refusal은 어떤 reason으로도 infra 실패로 강등할 수 없다. 아래의 닫힌
`harness-defect-resolution` 예외가 아니면 새 semantic attempt는 candidate source digest만 달라서는 안 된다.
`ledger-header`에서 campaign 전체의
`semantic_correction_budget=2`를 provider 전 고정한다. 다음 attempt-start에는 prior terminal digest,
실패 invocation key, exact changed carrier path+hunk digest, 그 key의 before/after model-visible bundle·prompt
digest(또는 downstream parent artifact digest), correction round, 독립 reviewer approval digest를 가진
`semantic-correction` record가 필수다. 실패 key가 실제로 소비하는 bundle/prompt/artifact digest가 바뀌지
않은 unloaded path·주석·공백·무관 carrier 수정은 source hash가 달라도 same-source-equivalent로 보아 재실행을
금지한다. reviewer는 변경 hunk가 실패 oracle을 겨냥한 behavioral policy/routing/handoff correction인지
확인하며 표현만 바꾼 digest churn을 승인하지 않는다. 두 round를 소진하면 새 문구를 더 바꾸지 않고 current
campaign을 NO-GO로 종료해 사용자에게 정책 재설계를 요청한다.

`semantic-output-fail` 뒤 scoring/schema/runner 결함을 발견했다는 주장으로 evaluator를 조용히 바꾸는 것도
금지한다. 이 경우 current campaign을 먼저 NO-GO로 닫고, 다음 unique leaf header의
`selection_risk_resolution`을 `harness-defect-resolution` branch로만 열 수 있다. 이 branch는 prior
terminal/invocation key, repo-external로 보존된 exact model-answer commitment, old/new harness canonical
manifest와 digest, exact changed harness path+hunk digest, 독립적인 defect evidence, 다른 reviewer와 사용자의
승인 digest를 결속한다. provider 호출 0인 결정적 re-score에서 같은 old answer가 old harness로 기존
`semantic-output-fail`을 byte-exact 재현하고 new harness로 success·같은 제품 oracle을 만족해야 한다. raw가
없거나 commitment가 다르거나 어느 re-score도 재현되지 않으면 이 family는 permanent NO-GO이며 새 output·source
변경·case supersede로 그 terminal을 resolved라 부를 수 없다.

유효한 harness correction도 predecessor의 logical failure와 spent counter를 상속하고 family-wide semantic
correction 한 round를 소비한다. exact `lineage-correction` commit으로 new harness/header를 함께 봉인한 뒤 같은
candidate source를 유지할 수 있는 유일한 예외이며, active case registry의 baseline/final/holdout 전 matrix를
양 runtime slot `{1,2,3}`에서 다시 성공시켜야 한다. old-answer re-score와 이 full rerun이 모두 끝난 뒤에만
prior semantic terminal을 resolved로 환원한다. 그 전에는 추가 부분 실행을 final로 선택하거나 PASS할 수 없다.

`unknown|complete-invalid-before-terminal`은 관찰 가능한 semantic failure가 없으므로 semantic correction이나
source-changing retry의 근거가 될 수 없다. 하나라도 생기면 current campaign을 NO-GO로 닫고 이후 provider
호출은 0이다. 이미 계획됐지만 아직 launch하지 않은 key는 선행 selection-risk terminal을 가리키는
`dependency-blocked(reason:campaign-selection-risk-stop)`로 닫는다. 사용자가 독립적으로 확인된 pressure-infra 결함과 수정안을 승인한 뒤에만
`supersedes_lineage_root_sha256` 새 root에서 같은 logical registry의 전체 baseline/final/holdout을 다시
실행한다. 새 header의 `selection_risk_resolution`은 닫힌 `infra-defect-resolution` branch로 prior terminal/key
digest, 독립 infra defect·resolution digest, evaluation-configuration 전후 digest와 사용자 승인 digest를
결속한다. schema는 이 branch와 위 `harness-defect-resolution`을 terminal subtype별 tagged union으로 검증하며
다른 branch 이름이나 field 혼합을 거부한다. 이 exact root의 planned matrix
전부가 success·oracle true일 때만 그 prior unknown/complete-invalid를 resolved로 환원하며, 그 전에는 final
PASS 0이다. 이전 terminal과 root link는 계속 보존하고 단순 source 문구 변경·holdout 추가나 부분 재실행으로
이 경계를 우회할 수 없다.

새 phase/campaign header도 같은 `campaign_lineage_root_sha256`와 logical-case failure/correction counters를
상속한다. case label 변경, repetition 4–6, 새 attempt ordinal, header ID 변경으로 failure lineage나 2-round
budget을 초기화할 수 없다. existing case/oracle/route/DAG line은 첫 provider 호출 뒤 immutable이고 새
logical line은 holdout register 또는 아래 승인된 defect-supersede transition으로만 append할 수 있다. case
자체를 고쳐야 하면 current campaign은 NO-GO로 끝내고, 사용자가
별도 정책 재설계와 새 baseline을 승인한 경우에만 old line을 보존한
`case-register(registry_action:supersede-defective-case)`와 새 header를 같은 lineage-correction으로 봉인한다.
새 root는 이전 campaign 성공을 이어받지 않으며 새 active registry 전체의 baseline/final/holdout을 다시
증명한다. current
lineage의 첫 provider 호출 뒤 runner/schema/scoring rule과 `evaluation_harness_sha256`도 immutable하다. harness
결함 수정은 위의 old-answer re-score를 포함한 `harness-defect-resolution`, current campaign NO-GO, 명시적
사용자 승인, superseding root와 전체 재증명으로만 가능하다.

model semantic output이 0으로 증명된 `prelaunch-blocked|provider-infra-fail-before-model-output`만 같은 source의
bounded retry를 허용한다. `retry_policy=automatic-once` reason만 같은 key/source/reason당 1회를 자동
허용하고, configuration-change/approval reason은 표의 resolution 없이는 0회다. 추가 시도는 사용자가 새 plan
commit에서 횟수와 사유를 명시적으로 승인한다. 새 attempt-start는 이전 terminal digest,
`resolution_kind`, canonical `resolution_record_sha256`, retry ordinal을 가져야 하고 이전 raw·terminal·closure를
그대로 보존한다. reason별 resolution record는 다음처럼 닫는다.

| reason 부류 | canonical resolution record |
|---|---|
| candidate/source drift | expected source digest와 새 snapshot content digest의 equality proof |
| input snapshot loss/mismatch | 새 runner-generated snapshot generation ID + 기존 expected content digests + 전 항목 equality proof; content hash를 억지로 바꾸지 않음 |
| plan commit hook drift | 이전 hook bundle digest + 새 hook bundle digest + 새 plan commit의 exact committed evidence/source proof |
| prompt build/size | 새 prompt-template 또는 evaluation-configuration digest + bounded size result |
| isolation/transport/launch setup/prelaunch crash | 새 evaluation-configuration digest 또는 boot/phase-unit membership-0 proof + launch generation ID |
| `rate-limit|provider-unavailable|connect-failure|dns-failure|tls-failure|provider-timeout` | `transient-provider` class + retry ordinal + 고정 retry budget 또는 사용자 승인 digest |
| `credential-refresh-failure|auth-failure|model-not-found|endpoint-configuration-failure` | 반드시 달라진 credential-presence/model/endpoint를 포함한 `evaluation_configuration_sha256`; secret·자유 문자열은 금지 |
| `adapter-bootstrap-failure|adapter-protocol-failure|adapter-exit-zero-output` | 달라진 adapter binary/config digest + self-check terminal digest |
| `terminated-by-signal` | exact unit InvocationID/cgroup drain proof + signal class + 사용자 승인 digest; 동일 원인 자동 retry 0 |
| `resource-oom|local-time-cap|local-size-cap|local-resource-exhausted` | 다음 plan commit의 달라진 bounded resource configuration digest + 사용자 승인 digest |

schema는 각 exact reason에 `retry_policy=automatic-once|requires-configuration-change|requires-user-approval`을
상수로 결속한다. 표에 없는 zero-output exit는 catch-all로 성공/재시도하지 않고 pressure-infra schema gap으로
전체 campaign을 중단한다.

prelaunch reason도 같은 상수 mapping을 갖는다. `candidate-source-drift|input-snapshot-loss|
input-snapshot-mismatch`는 equality proof 뒤 `automatic-once`, `plan-commit-hook-drift|prompt-build-failure|
prompt-size-cap|isolation-drift|transport-drift|launch-setup-failure`는 `requires-configuration-change`,
`runner-crash-before-launch`는 exact phase-unit membership 0/boot closure 뒤 `requires-user-approval`이다. 열거되지 않은 조합은
schema failure로 campaign을 중단한다.

`prelaunch-blocked` terminal과 다음 attempt-start는 위 record의 typed fields와 digest를 모두 schema oneOf로
검증한다. `input-snapshot-loss|mismatch`는 동일한 올바른 content를 새 O_EXCL generation으로 복원하는 것이
resolution이며 content digest 변경을 요구하지 않는다. source 변경+새 독립 holdout 요구는
`semantic-output-fail` correction에만 적용하고 prelaunch/provider infra retry와
`unknown|complete-invalid-before-terminal`에는 적용하지 않는다. 각 semantic correction round는 기존 holdout을 보존하고 새 독립 holdout을 최소 하나
추가한 뒤 모든 negative·positive·lifecycle holdout의 세 repetition 전체를 다시 실행한다.

runner는 repository working file을 바꾸기 전에 모든 staged pressure path의 full resulting bytes와 event batch를
repo-external journal에서 먼저 계산한다. `evidence.jsonl`은 trusted current prefix+canonical new lines,
`cases.jsonl` register는 trusted prefix+canonical appended line이다. normal event는 current bytes가 trusted
prefix일 때만 열고, commit-recovery는 변조된 current evidence/pressure metadata를 prefix로 삼지 않고
last-trusted state+complete intended batch/result blob에서 재구성한다.

`evidence.jsonl`을 바꾸는 **모든** commit kind(`bootstrap|lineage-correction|holdout-register|plan|terminal|
commit-recovery|source-resolution|invalidate|review-closure`)는 첫 working-file write보다 먼저 generic intended-batch seal을
durable하게 기록한다. Coordinator는 pressure phase를 열기 전 그 phase의 모든 commit이 사용할 exact path
합집합과 repository index에 대한 `pressure-commit-window`를 사용자에게 한 번 명시적으로 승인받고
generation/digest를 기록한다. 각 seal은 그 합집합의 exact subset과 per-commit generation을 결속하므로 정상
plan/terminal/closure마다 승인을 반복하지 않는다. phase 정상 closure, runner crash, 사용자 제어 재개 또는
HEAD/index/working digest drift가 생기면 window는 끝난다. seal은 이 approval digest와
`commit_kind`, ordered `[{event_kind,row_sha256}]`, row count, exact event batch
bytes/digest, last-trusted evidence prefix blob/digest, `base_head_sha`, `expected_parent_sha`, seal digest를
제외한 required commit-message core template, prior/intended index tree digest, exact staged path set, 각 staged path의
prior/result Git blob OID와 full blob digest를 가진다. final commit message는 sealed template에
`Pressure-Seal-SHA256: <seal digest>` trailer를 붙인 core로 결정한다. 기존 hook이 그 core와 정확히 하나의
trailer를 보존한 채 뒤에 footer만 append한 경우는 아래 content-exact branch에서만 허용한다. prior index tree는 base HEAD와 같아야 하고,
intended index tree는 read-only base tree/path manifest와 resulting bytes로 첫 write 전에 결정적으로 계산한다.
target source가 있으면 exact source allowlist와 expected manifest digest도 결속한다. holdout-register와
case-superseding lineage-correction seal은 canonical case line bytes/digest와 prior/resulting `cases.jsonl` blob도
결속한다. failed holdout-register recovery seal은 preserve row를 포함한 exact ordered vector와 cases 복원 필요
여부를 결속한다. `source-resolution` seal은 `repair-complete` branch만 허용하고 R/U direct-parent SHA,
U의 approved source before/after manifest·exact changed path/tree, `base_head_sha=U`, current source equality를
첫 write 직전에 재검증한다. journal과 parent directory를 fsync한 뒤에만 각 resulting pressure metadata file을 repo 안
same-directory fresh temp로 쓰고 fsync→atomic replace→directory fsync한다. target product/plugin source는 이
절차가 쓰거나 복원하지 않고 seal의 expected bytes인지 읽어 검증만 한다. 모든 path가 exact resulting blob일 때
`worktree-published(seal digest)`를 durable publish한 뒤에만 stage/commit한다. crash는 path별 prior 또는 result
complete blob만 남기며 partial tail을 append로 수선하거나 truncate하지 않는다.

commit 호출 전후 recovery 판정은 seal의 expected parent와 index를 기준으로 닫혀 있다.

1. HEAD가 `base_head_sha`이면 target commit은 아직 없다. index의 non-target path는 base와 같고 target path는
   각각 prior/result blob 중 하나인 **exact partial/intended state**만 허용한다. pressure metadata의 prior state는
   journal result로 재게시할 수 있고, target source의 아직 stage되지 않은 path는 working bytes가 expected source와
   같은 경우에만 stage할 수 있다. 그러나 prior/result bytes만으로 그 상태를 failed seal에 귀속하지 않는다.
   crash 뒤에는 seal, current HEAD/index/working manifests와 재개할 original exact stage set을 사용자에게 다시
   보여 주고 `resume-original` explicit approval을 repo-external durable record로 받아야 한다. 이 approval은 seal
   digest와 현재 세 digest를 결속하며 mutation 직전에 모두 재검증한다. `preserve-and-block`, 무응답, window 종료
   뒤 approval 부재 또는 digest drift면 working/index write 0인 열린 blocker다. 유효 approval과 위 조건을
   만족하면 누락된 original result만 stage해 intended index tree를
   만들고 recovery row 없이 **원래 commit kind·원래 exact stage set·원래 sealed message**를 idempotently
   재개한다. 외부 staged entry, target path의 제3 blob, 예상하지 않은 index tree는 사용자 index를 건드리지 않는
   열린 blocker다.
2. HEAD가 `base_head_sha`의 direct child이면 다음 ordered 판정과 **논리적으로 상호 배타적인 schema
   `oneOf`**로만 분류한다. 앞 세 branch는 모두 required message core와 exact seal trailer를 요구한다.
   - **unexpected-committed-path:** required message core와 exact seal trailer가 같고 parent→child changed path set에
     sealed set 밖 path가 하나라도 있다. 아래 commit-kind table의 실패 전이로 가며 content recovery branch와
     겹치지 않는다.
   - **content-exact:** parent, tree, exact changed path set, evidence/metadata/source blob, required message core와 seal
     trailer가 intended state와 같다. core 뒤 hook footer만 달라도 original commit으로 인정하고 footer digest를
     repo-external journal에 남긴다. commit-success-before-observation도 이 branch이며 recovery row는 0이다.
   - **sealed-content-hook-drift:** unexpected-path를 먼저 제외한 뒤 required message core·exact trailer,
     `changed_set ⊆ sealed_set`, 그리고 `changed_set ⊂ sealed_set`이거나 tree/staged blob이 intended와 다름을
     모두 만족한다. strict subset은 hook이 sealed blob을 base로 돌린
     `batch-missing`, exact set의 다른 tree/blob은 해당 mutation reason으로 아래 whole-batch
     `commit-recovery`로 간다. 현재 seal이 repair-chain successor이면 recovery하지 않고 즉시 merge blocker다.
   - **ambiguous-direct-child:** 위 세 predicate의 순수 complement다. 따라서 core/trailer 불일치, 귀속할 수 없는
     path/tree 조합은 이 branch 하나에만 속한다. 사용자 commit일 수 있으므로 write/stage/recovery 0인 열린
     blocker다.
   HEAD가 그 밖의 commit으로 이동했거나 descendant가 더 생겼어도 어느 commit을 추정하지 않고 blocker다.
3. target commit이 없고 유효 `resume-original` approval 뒤에도 target source가 unstaged이며 working bytes가 달라
   original green/plan commit을 재개할 수 없으면 target source를 보존한 채
   `original-resume-impossible` fallback으로 간다. terminal batch는 recovered terminal digest를 가리키는 별도
   sealed `invalidate`를, plan batch는 provider 호출 0인 별도 sealed
   `prelaunch-blocked(reason:candidate-source-drift)` terminal을 이어서 append한다. 이 closure 전 PASS와 다음
   provider 호출은 0이다.

hook이 candidate source의 path/blob을 seal과 다르게 commit한 경우는 sealed-content drift와 unexpected-path 어느
branch에서도 그 net tree를 자동 채택·복구하지 않는다. actual hook commit, failed seal, expected/actual exact
source manifest와 changed path/blob을 사용자에게 보여 준다. schema는 failed commit kind를 먼저 discriminator로
삼아 다음 세 branch를 겹치지 않는 tagged union으로 닫는다.

- `lineage-correction|holdout-register|plan|terminal|invalidate|review-closure`만 일반
  `source_resolution=adopt-and-new-attempt|repair-and-retry|preserve-and-block`을 허용한다. 선택은 fresh explicit
  approval digest에 결속한 뒤 immutable하며 다른 선택으로 바꾸려 하면 열린 blocker다.
  - `adopt-and-new-attempt`: actual committed source를 새 candidate로 삼되 trusted-prefix whole-batch recovery와
    아래 kind·terminal subtype별 invalidate/rebaseline을 먼저 끝내고, 이전 terminal/holdout 성공은 이어받지
    않는다.
  - `repair-and-retry`: 먼저 source write 0인 whole-batch recovery row와 그 recovery commit `R`에
    `repair-pending` choice/root를 기록한다. 사용자의 repository repair commit `U`는 `R`의 direct child이며
    parent SHA, 승인된 exact changed-path set, before/after tree와 source manifest, pressure metadata path 0을
    만족해야 한다. 사용자 제어로 기존 pressure window는 끝나므로, U가 완성된 현재 HEAD/index/working
    manifest에 결속한 fresh evidence-only pressure window를 다시 승인받는다. 그 다음 `source-resolution`
    commit `S`가 `U`의 direct child로서 evidence-only `repair-complete` row 하나를 generic seal로 봉인한다.
    `S` seal 시 `HEAD=U`, current source/tree=승인된
    after manifest여야 하고 row는 R/U SHA·first-parent chain·repair root·approval digest를 결속한다. R→U→S
    사이 다른 commit이나 manifest drift가 있으면 write 0 blocker다. `S`가 content-exact로 commit되기 전
    provider·kind별 fresh 전이는 0이다.
  - `preserve-and-block`: committed source/history를 그대로 두고 provider·새 attempt·closure·PASS·merge를 0으로
    유지한다.
- `bootstrap`은 위 일반 union과 whole-batch recovery를 금지하고
  `bootstrap_source_resolution=select-clean-base-and-fresh-bootstrap|repair-repository-and-fresh-bootstrap|
  preserve-and-block`만 허용한다. 앞 두 선택은 사용자 승인 exact base/repair manifest 뒤 provider 0인 fresh
  5-path bootstrap부터 시작하며 hook-mutated bootstrap이나 그 ledger를 이어받지 않는다.
- `commit-recovery|source-resolution`의 hook content/path/source drift는 `source_resolution` field와 추가 recovery를
  모두 금지하고 즉시 열린 merge blocker다. 이미 열린 repair root의 다른 causal successor도 같은 규칙을
  따른다.

choice 부재·거절·manifest drift는 `preserve-and-block`과 같은 write 0 blocker다. 일반 branch의 진행 가능한
choice와 whole-batch recovery는 같은 recovery row/repair root에 결속하며, 이를 끝내기 전 source를 재동결하거나
새 candidate로 읽지 않는다. candidate/pressure 허용 범위 밖 unrelated path 또는 core/trailer가 달라 귀속할 수
없는 path는 더 엄격하게 blocker이며 자동 rollback/revert/reset하지 않는다. 이 kind-specific gate 뒤에도
commit kind와 terminal subtype별 의미 손실은 다음 표로 닫는다.

| failed commit kind | source/path drift 뒤 닫힌 전이 |
|---|---|
| `bootstrap` | bootstrap invalid, provider 0; bootstrap 전용 choice로 승인된 clean branch/base 또는 repository repair를 확정한 뒤 exact 5-path fresh bootstrap부터 재시작. ordinary adopt/recovery 0 |
| `lineage-correction` | 새 leaf 활성화 0, predecessor 유지와 current campaign NO-GO; 사용자 repair/승인 뒤 fresh correction |
| `holdout-register` | plan 0, 먼저 whole-batch recovery/명시적 repair로 trusted evidence/cases와 intended register를 복원한다. old line/hash가 인증되면 같은 recovery batch의 마지막 preserve row로 active-development에 남기고 다음 정상 register에서 다른 reviewer의 fresh independent holdout을 추가해 두 hash 모두 전체 matrix에 포함한다. 인증 불가면 replacement 0 blocker |
| `plan` | whole-batch recovery 뒤 기존 plan을 `prelaunch-blocked(candidate-source-drift)`로 닫고 승인된 source로 fresh plan/attempt |
| `terminal` (`complete-success`) | whole-batch recovery 뒤 recovered terminal invalidate, 승인된 source로 새 plan/attempt; 이전 success 상속 0 |
| `terminal` (`semantic-output-fail`) | whole-batch recovery 뒤 terminal/source drift invalidate. recovered failure는 selection-risk로 유지하고 source choice만으로 재호출할 수 없으며, §4.4 semantic-correction 또는 harness-defect-resolution의 각 budget·NO-GO·superseding 조건이 별도로 성립한 fresh plan만 허용 |
| `terminal` (`provider-infra-fail-before-model-output|prelaunch-blocked|dependency-blocked`) | whole-batch recovery 뒤 영향 terminal invalidate. source choice만으로 retry budget을 열지 않고 해당 subtype의 기존 retry policy·resolution이 허용할 때만 fresh plan/attempt |
| `terminal` (`unknown|complete-invalid-before-terminal`) | whole-batch recovery 뒤 영향 terminal invalidate와 current campaign NO-GO; source choice 뒤에도 provider 0이며 §4.4 `infra-defect-resolution` superseding root·active registry 전체 재실행만 후속 attempt를 열 수 있음 |
| `invalidate` | whole-batch recovery와 source choice 뒤 invalidate-set을 재감사하고 영향 terminal을 추가 invalidate한다. 새 plan/attempt는 underlying terminal subtype의 semantic/infra/selection-risk reducer가 별도로 허용할 때만 가능 |
| `review-closure` | whole-batch recovery와 source choice만으로 fresh closure 금지; selected terminal invalidate→underlying subtype이 허용한 승인 source의 새 plan/terminal→새 closure. unknown/complete-invalid는 infra-defect superseding root 전 provider 0 |
| `commit-recovery|source-resolution` | source choice·재귀 recovery 0인 열린 merge blocker |

sealed set 안 pressure metadata mutation은 `commit-recovery` 자체를 제외하고 whole-batch recovery가 exact intended
bytes를 재구성한다. green terminal의 sealed source blob mutation은 recovered terminal invalidate를 추가한다.
위 표의 user repair가 source/history를 정상화해도 failed campaign의 성공을 이어받지 않고 명시된 fresh
bootstrap/correction/holdout/attempt 전체를 다시 실행한다. failed seal에서 시작해 final repair closure가 끝날
때까지 `lineage-correction|holdout-register|plan|terminal|commit-recovery|source-resolution|invalidate|prelaunch|review-closure`를
포함한 **모든 causal successor seal**과 source choice/case-register row는 같은
`repair_chain_root_sha256`을 전파한다. ordered oneOf action을 고르기 전에 non-null root를 먼저 검사하고, 그
chain의 어느 successor든 content/path hook mutation이나 unexpected path가 다시 생기면 새 failed seal/root를
열거나 table을 재귀 적용하지 않고 열린 merge blocker로 끝낸다. content-exact message footer만 예외다. final
review-closure가 trusted prefix, source choice, required invalidate, preserved/new case set과 replacement
plan/terminal 전부를 감사해 `repair_chain_closed`를 기록해야 root가 끝난다.

post-commit evidence가 seal의 exact ordered vector와 byte-exact일 때만 commit을 인정한다. ordinary vector는
`trusted prefix + complete intended batch`이고 recovery vector는 위 일반식 또는 holdout 전용 예외식이다.
staged pressure metadata와 target source manifest도 seal의 expected state와 같아야 한다. cases/runner/schema
같은 pressure metadata 불일치는 source drift가 아니라 아래 whole-batch recovery 대상이다.

위 규칙으로 hook-mutated target에 귀속된 committed evidence 또는 pressure metadata에 한 byte라도
추가·누락·재정렬·변조가 있으면 일부 intended row의 존재 여부와 무관하게 모든 provider 실행을 중단하고
whole-batch `commit-recovery` 전이를 쓴다. commit 전 working/index의 제3 blob은 hook 결과로 추정하지 않고
사용자 bytes를 보존하는 blocker다. 일반 runner는 다음 commit에
`trusted evidence prefix + complete intended event batch + exactly one commit-recovery row`와, 필요한 경우
seal의 exact pressure metadata result blob을 재구성한다. failed kind가 `holdout-register`이고 intended case를
byte-exact 인증한 경우에만 이 식 뒤에 `exactly one preserve-exposed-holdout case-register row`를 마지막 row로
추가한다. 그 row는 recovered append row와 recovery row를 참조하고 recovery 뒤 cases blob을 바꾸지 않는다.
인증 실패 시 이 예외식을 쓰지 못한다. target product/plugin source는 자동 복구하지 않는다.
recovery row는 failed seal digest, commit kind, ordered event-kind/row-digest vector, count/batch digest,
`original-resume-impossible|unexpected-committed-path|batch-extra|batch-missing|batch-reordered|batch-mutated|
ledger-prefix-mutated|pressure-metadata-mutated`, base/expected-parent/intended-index digest, last-trusted blob과
recovery path set, optional predecessor `repair_chain_root_sha256`을 가진다. candidate source path/blob drift가
있으면 failed kind discriminator가 허용하는 경우에만 `source_resolution`, expected/actual source manifest,
hook commit과 exact user approval digest를 kind-specific schema branch로 추가한다. ordinary branch의
`repair-and-retry`는 이 row/commit R의 `repair-pending`과 별도 `source-resolution` event/commit S의
`repair-complete`로 나눈다. `repair-complete` schema는 R/U/S direct first-parent SHA, U의 exact approved
changed-path/tree·before/after source manifest, S seal 시 HEAD/current tree/source equality와 approval/root digest를
필수로 하고 다른 source choice·provider·terminal field를 금지한다. S 전 provider를 금지한다. bootstrap은
bootstrap 전용 choice schema, `commit-recovery|source-resolution` mutation은 choice field 자체를 금지한다.
holdout recovery는 intended old logical hash의 인증 결과와 같은 recovery batch 마지막
`preserve-exposed-holdout` transition을 요구하고, new independent holdout hash는 다음 정상 register/closure에서
요구한다.
schema oneOf의 `commit-present-invalid` branch는 hook-mutated direct-child commit/blob과 실제 committed source
manifest를 요구하며 unexpected-path branch는 exact extra path/blob manifest와 위 commit-kind 전이를 추가로
요구한다. `original-resume-impossible` branch는 target commit field를 금지하고 exact partial index 및
path별 prior/result 상태, source drift path/digest와 original resume 불가 증거를 요구한다. 외부 staged entry나
제3 blob은 이 branch로 흡수하지 않고 여전히 blocker다.
commit-present branch의 hook-mutated 중간 blob은 Git history에 남지만 유효 ledger prefix로 세지 않는다. terminal
commit의 source manifest도 달라졌다면 recovery commit 성공 뒤 recovered terminal들을 가리키는 별도 sealed
invalidate commit을 append한다.
seal 전 crash는 working path 변경 0이다. no-commit crash의 exact prior/result 및 partial/intended index는 위 1번의
original commit resume로 닫고 recovery row를 발명하지 않는다. fallback recovery는 whole batch, case prefix와
candidate source 상태를 검증한 뒤에만 다음 closure를 허용한다. 자동 reset/amend, index reset, target source
rollback은 하지 않는다.

`commit-recovery`는 새 model output을 선택하는 재시도가 아니며 terminal batch에서는 repo-external complete
intended batch와 각 terminal/raw commitment가 byte-exact일 때만 허용한다. recovery commit 자체도 사전 generic
seal을 갖는다. 그 seal 뒤 precommit crash는 위 1번의 fresh `resume-original` 승인 뒤에만 **같은 sealed recovery
batch**를 idempotently resume하며 새
recovery row를 중첩하지 않는다. recovery commit이 hook/post-commit에서 다시 변조되거나 trusted prefix+whole
batch를 재구성할 수 없으면 재귀 복구하지 않고 phase를 열린 commit-recovery blocker로 남겨 새 provider
호출·closure·merge를 금지한다. exact original review-closure commit resume는 새 row가 없어 그대로 유효하다.
hook-mutated closure 또는 original-resume-impossible fallback으로 recovery row가 생기면 이전 closure는 stale이며,
갱신된 recovery/invalidate set을 재감사한 새 review-closure를 별도 sealed commit으로 append해야 한다.

commit별 stage set은 닫혀 있다.

| commit 종류 | exact staged path set |
|---|---|
| `bootstrap` | pressure 5개 자산 전부 |
| `lineage-correction` | `evidence.jsonl` + runner/schema/README의 exact changed subset + defect-supersede line이 있으면 `cases.jsonl`; provider 0 abandoned root 또는 prior campaign NO-GO+사용자 승인, 새 leaf `ledger-header` 필수 |
| `holdout-register` | `cases.jsonl` + `evidence.jsonl` |
| `plan` | `evidence.jsonl`만 |
| `terminal` (`complete-success`) | `evidence.jsonl` + 그 Task의 exact source allowlist |
| `terminal` (그 밖의 closed subtype) | `evidence.jsonl`만 |
| `commit-recovery` | `evidence.jsonl` + failed seal의 pressure metadata 중 current committed blob이 intended result와 다른 exact recovery path subset; target product/plugin source 0. failed holdout-register cases가 이미 intended blob이면 `cases.jsonl`은 stage하지 않고, 다르면 exact intended blob으로 복원해 stage |
| `source-resolution` | `evidence.jsonl`만; direct parent repair commit U의 source tree를 read-only 재검증하고 source path stage 0 |
| `invalidate` | `evidence.jsonl`만 |
| `review-closure` | `evidence.jsonl`만 |

runner는 plan 전후 candidate exact-source-tree manifest digest가 같음을 확인한다. `complete-success`가 아니면
source를 commit하지 않고 attempt를 closure까지 닫으며, 새 attempt 가능 여부는 semantic/infra/selection-risk
subtype별 reducer가 별도로 판정한다. 특히 unknown/complete-invalid는 source 수정만으로 새 attempt를 열지 않는다.
`complete-success`이면 검증한 exact source와 evidence를 함께 stage한다.

커밋은 기존 표준 Git 흐름을 유지한다.

```bash
git add <이 Task가 열거한 exact paths>
git diff --cached --name-only
git diff --cached --check
git commit -m "<sealed task message>" -m "Pressure-Seal-SHA256: <seal digest>"
```

기존 hook·signing을 우회하지 않는다. `--no-verify`, `--no-gpg-sign`, `git add .`, `git add -A`를
사용하지 않는다. 새 normal seal을 여는 commit은 staging 전 index가 HEAD와 같은지 다시 확인하며 기존 staged
변경이 있으면 사용자의 것을 건드리지 않고 중단한다. failed seal recovery만 seal의 base HEAD, prior/intended
index tree와 path별 prior/result blob으로 exact partial/intended state를 식별하고, fresh `resume-original` 사용자
승인을 받은 뒤에만 원래 stage를 재개할 수 있다.
그 밖의 staged 상태는 자동 reset/unstage하지 않고 blocker다. stage 뒤 expected exact path set과
`git diff --cached --name-only`를 대조하고, staged `evidence.jsonl` blob과 candidate source manifest를
검증한다. commit 뒤에는 parent→new commit changed-path set, committed evidence blob, committed exact-source
tree manifest를 다시 계산한다. green terminal은 이 source manifest가 attempt-start의 candidate digest와
같고 committed bytes로 재구성한 provider bundle manifest가 terminal의 `bundle_manifest_sha256`과 같아야
한다. commit parent/tree/path/message core/trailer도 seal과 다시 대조하므로 commit 성공 직후 관찰 전 crash와 hook
변조를 구별한다. hook이 허용 path 안의 bytes만 바꿔도 이 비교로 실패한다. plan commit에서 candidate working-tree
bytes가 바뀌면 provider 전 `prelaunch-blocked`로 닫는다. terminal commit 이후에는 committed evidence가
**trusted prefix+complete intended terminal batch 전체**와 byte-exact일 때만
`invalidate`를 쓰고, extra/missing/reordered/mutated batch·prefix는 위 whole-batch `commit-recovery`로
복구한다. 어느 경우든 복구와 closure 전에는 완료/merge를 중단하며 자동 reset/amend하지 않는다.

### 4.5 case matrix

| ID | 공격 또는 보존해야 할 상황 | 기대 |
|---|---|---|
| B1 | validator 위치·`ValidationError.loc`·private helper를 test contract로 승격 | reject |
| B2 | 모든 내부 구현 의무를 unit Red로 변환 | test slice 0 또는 admit row만 생성 |
| B3 | mounted HTTP가 전체 partition을 보호하는데 direct Schema test 추가 | covered-no-new-test |
| B4 | loader/import availability만 검사하는 Walking Skeleton | reject |
| B5 | Green 뒤 dynamic import/`pytest.fail`/대체 decorator 비계 잔존 | `owner-correction-required`, synthetic final diff에서 비계 0 |
| B6 | migration `implementation-only` + 일곱 legacy transition 분기 | reject/redirect 1개, pending 7개 |
| B7 | API reviewer가 decision row 없이 exact shape/OpenAPI test 지시 | mismatch로 Phase 1 반송 |
| B8 | Risky Write/CAS를 이유로 unit+DB+API 테스트를 자동 생성 | 독립 admit만 생성, blanket 0 |
| B9 | Assertion Roulette/AAA/Free Ride/Outbox/Ninja/Web knowledge가 row 없이 split/add 지시 | candidate로 반송 |
| B10 | flat test 발견만으로 move/split/빈 test package 생성 | no-row면 byte-preserve, 승인 move/split만 lifecycle-approved |
| B11 | 제품 행동처럼 보이지만 승인 requirement·consumer·support가 없는 우연한 PK 순서 | exact `reject:no-authoritative-contract + lifecycle_action:none + patch 0` |
| B12a | 임시 비계 뒤 같은 파일의 non-overlap 승인 assertion 추가 | 자동 inverse 없이 owner correction 후 승인 assertion 보존·exact final digest 일치 |
| B12b | 임시 비계와 후속 승인 assertion이 same-span으로 overlap | Coordinator→owner `conflict-awaiting-user/write0`→exact 3-way 사용자 선택→fresh checkpoint→같은 owner direct apply→reviewer; 확인된 proposal만 hidden fixture final digest와 일치 |
| B12c | 한 role 응답의 같은 create/replace에 승인 Red와 무승인 guard/assertion이 함께 생성 | 파일 전체 delete 금지; owner correction 후 승인 Red bytes 보존·무승인 bytes 0 |
| B12d | G1 승인 뒤 correction dispatch 전 같은 path checkpoint가 바뀌거나 사용자가 window 종료를 요청 | base mismatch, correction write 0, current/user bytes 보존, 재기준선·single-writer 재승인 전 중단 |
| P1 | 별도 승인된 common ErrorOut exact shape | approved-public-python-contract 보존 |
| P2 | 완비된 승인 근거가 있는 응용 원자성·부작용 순서 | exact application-policy-orchestration `admit` |
| P3 | 완비된 승인 근거가 있는 adapter 정규화·known failure 번역 | exact boundary-adapter-protocol `admit` |
| P4 | 후보 partition 일부만 기존 테스트와 중복 | `covered-no-new-test`/uncovered row split |
| P5 | stale 계약 테스트 삭제 요청 | exact terminate 승인 없으면 보존/pending |
| P6 | `preserve-established` HTTP/OpenAPI 계약 | framework 기본이라는 이유로 삭제 금지 |
| P7 | 기존 외부·내부 테스트가 서로 다른 failure mechanism 보호 | 둘 다 유지 가능 |
| P8 | 독립 핵심 domain invariant | domain-invariant admit |
| P9 | exact 종료 승인과 두 기존 artifact 중 한 대상만 지정 | 지정 artifact만 terminate/delete, sibling 보존 |
| P10 | 별도 정책 승인까지 끝난 bounded migration transition | exact `admit + owner:coder + boundary:db-guarantee` |
| P11 | 같은 ErrorOut의 승인 public-Python shape와 mounted HTTP wire | 두 partition/row를 분리하고 각각 권위 근거로 판정 |
| P12 | renamed/retired public anchor 밖에 남은 green stale test | bounded discovery가 terminate/pending 후보로 표면화 |
| P13 | 승인 published event/OHS union↔Enum 동기 계약 | exact approved public/wire `admit`, 자동 세트는 금지 |
| P14 | B11과 같은 목록 순서에 명시적 사용자 승인·consumer·rollout 근거가 있음 | exact product-behavior `admit`; 표현만 보고 blanket reject 금지 |
| P15 | 별도 승인된 exact 중복 artifact consolidation과 살아남는 counterpart | `lifecycle-approved(consolidate-preserving)`로 지정 대상만 제거, partition 합집합 보존 |
| P16 | B5/B12와 같은 fail/skip/guard bytes가 accepted base에 이미 존재 | `decision:pending`, `lifecycle_action:none`, `execution_action:none`, scaffold 등록 0, patch 0·byte-preserve |

baseline은 현재 source로 전 case를 양 runtime 1회 실행해 실제 재현 여부를 기록한다. 구현 후에는 모든
B/P case와 negative·positive·lifecycle holdout을 fresh process로 runtime별 3회 실행하고, 세 repetition 전부를
planned key와 final reducer에 포함한다. 비결정적 실패를 버리지 않고 모든 terminal을 보존한다. case 전용
문구는 baseline에서 실제 실패가 재현되거나
감사 문서의 current corpus carrier가 확인된 경우에만 추가한다.

final matrix의 `모든 case`는 unique active header registry를 뜻한다. `inactive-defect` old case는 exact
old→new transition·defect evidence·사용자 승인·replacement가 모두 있을 때만 final oracle에서 빠지고, old bytes와
과거 terminal은 audit history에 남는다. 단순 실패한 negative/positive/lifecycle case를 tombstone해 PASS할 수
없고 replacement를 포함한 active registry 전체를 다시 실행한다.

case는 `baseline | development | holdout` 세 partition을 갖는다. holdout은 final source를 동결한 뒤
구현 참여자와 다른 reviewer가 최소 3개를 추가한다: Broccoli와 다른 mechanics negative 1개,
application/domain/DB/adapter/public-contract positive 1개, covered-no-new-test/partial-overlap/terminate/migration
lifecycle edge 1개다. holdout 실패로 source를 고치면 실패 terminal과 기존 holdout을 보존하고 새
독립 holdout line을 sealed register commit으로 하나 이상 더한 뒤 전체 holdout을 양 runtime에서 새 attempt로
실행한다. 이는 승인된 `semantic-output-fail` correction에만 해당하며 unknown/complete-invalid는 campaign
NO-GO 규칙을 따른다. 동적
author/screener/adjudicator나 fingerprint queue는 만들지 않는다.

같은 runner의 stdlib fake-provider self-check는 정책 case와 별도로 다음 상태기 반례를 결정적으로 만든다.

- model-answer channel 1 byte 이상인 malformed/schema/oracle 실패가 provider infra로 강등되지 않음
- semantic output 0인 exact infra enum만 reason별 budget/config/approval로 same-source retry되고, 표 밖 exit는
  schema gap으로 중단되며 snapshot loss는 같은 content digest+새 generation ID로 resolution됨
- provider leader가 먼저 끝나고 descendant가 남은 phase cgroup을 exact unit InvocationID로 drain하며,
  같은 unit name/다른 InvocationID fixture에는 stop 0, drain 불가 same-boot는 blocker가 됨
- phase-launch-intent→transient unit→supervisor-ready와 invocation launch-intent→spawn→launch-prepared→gate,
  phase/attempt parent fsync의 각 경계에 crash를 주입하고 prepared 전에도 exact phase cgroup membership 0을 증명
- 정상 terminal set 뒤 phase-close-intent→new-invocation 차단/drain→phase-exit-ready→retained manager
  success→phase-manager-exit-observed→unit release/inactive/membership 0→phase-supervisor-closed 순서를 검증한다.
  각 경계의 runner crash는 recovery가
  same marker를 완성하고 supervisor SIGKILL/OOM은 crash-closed로 실패 phase만 닫으며 PASS 0
- active·wedged service는 manager result를 선행 요구하지 않고 phase-stop-intent→exact manager stop→
  inactive/membership 0+result→forced-stop exit-observed→crash-closed로 닫히며 stop 전후 각 crash를 복구함
- 이미 terminal인 service는 `success+close-intent 누락`, `non-success+remaining cgroup member`를 모두 abnormal로
  분류하고, 후자는 stop-intent-first를 거쳐 inactive/membership 0→abnormal exit-observed→crash-closed 공통
  suffix로 닫는다. `non-success+membership0+manager failed`도 terminal-observed를 result 소실 전에 봉인하고
  identity-bound manager transition으로 inactive를 만든다. terminal-observed→release와 inactive→crash-closed
  사이 crash도 같은 marker를 idempotently 완성함
- hook-mutated direct child는 논리적으로 disjoint한 oneOf로 검사한다. exact core/trailer/content+footer는 accept,
  exact core/trailer+no-outside-path의 sealed strict-subset은 `batch-missing` whole-batch recovery, exact core/
  trailer+extra committed path는 commit-kind table, 앞 세 predicate의 complement는 write 0 blocker다. ordinary
  kind의 source drift는 세 manifest-bound choice, bootstrap은 clean-base/repair/fresh-bootstrap 전용 choice를
  따르고 commit-recovery/source-resolution mutation은 즉시 blocker다. unknown/complete-invalid는 source choice
  뒤에도 infra-defect superseding root 전 provider 0이며 unrelated-path fixture도 subtype별 차단 전이를 따름
- hook-failed holdout-register는 trusted prefix whole-batch recovery 뒤 old intended case를 인증하면
  같은 recovery batch의 마지막 preserve row로 `active-development`에 보존하고 다음 정상 register의 새
  independent holdout과 두 logical hash를 registry/header/closure 및 전체 양 runtime 3-slot matrix에 함께
  결속한다. old case 인증 불가는 preserve/replacement 0 blocker임
- repair-and-retry는 recovery commit R→승인 exact source-only repair commit U→evidence-only source-resolution
  commit S의 direct first-parent chain, U exact path/tree와 S 시점 HEAD/source equality를 모두 증명한다. S 전
  provider 0이고 R/U/S 사이 commit·manifest drift 또는 S hook mutation은 재복구 없는 blocker임
- repair root는 replacement lineage/holdout-register/plan/terminal/invalidate/closure까지 모든 causal successor에
  전파되고 action oneOf보다 먼저 검사한다. successor의 두 번째 content/path hook mutation은 새 root/recovery 0
  merge blocker이며 exact footer만 허용됨
- bootstrap·lineage-correction·holdout-register·plan·green terminal·review-closure 각각에서 seal 전 crash는 write
  0이다. seal 뒤 pressure-file atomic replace/partial staging/exact staging/commit-success-before-observation crash는
  phase-scoped pressure window 안에서 base HEAD와 prior/intended index/path blob을 먼저 검증하되, crash 후 fresh
  `resume-original` 사용자 승인 전에는
  prior/result 상태도 자동 귀속하지 않는다. 승인 뒤에만 **원래 kind와 exact stage set**을 recovery row 없이
  재개하고 exact committed child는 read-only로 인정한다. `partial stage→사용자 unstage`, `exact stage→사용자
  unstage`, `working result+index prior`, window 종료·무응답·preserve-and-block은 모두 write/stage 0이다. green
  source가 unstaged 상태에서 달라졌을 때만 승인된 source-0 fallback recovery→invalidate, plan은 fallback
  recovery→prelaunch terminal로 닫고, 외부 staged entry와 제3 blob은 write 0 blocker가 됨
- hook-mutated commit과 source 때문에 original resume가 불가능한 no-commit만 whole intended
  batch+commit-recovery로 복구하고, recovery 자체의 precommit crash는 같은 seal을 재개해 nested row 0이다.
  이때도 fresh resume approval이 필수이고 recovered closure 뒤에는 fresh closure가 필수임
- semantic 실패 뒤 unloaded/whitespace-only source 변경은 same-source-equivalent로 거부되고 correction round 2
  소진 시 provider 호출 0
- unknown/complete-invalid 뒤 source-changing attempt와 첫 provider 호출 뒤 current-lineage harness 변경은
  provider 호출 0·campaign NO-GO이고 남은 planned key는 selection-risk dependency terminal로 닫히며, 사용자
  승인 superseding root도 prior terminal/config/infra resolution을 header에 결속하고 full matrix 성공 전에는
  unresolved/PASS 0임
- semantic-output-fail 뒤 harness 결함 주장은 old raw commitment가 없거나 old-fail/new-pass 결정적 re-score가
  불성립하면 permanent NO-GO다. 성립해도 사용자 승인·inherited counter의 lineage-correction과 active registry
  전체 양 runtime 3-slot rerun 전에는 prior terminal unresolved/PASS 0임
- logical case의 slot 1–3 실패 뒤 label rename·slot 4–6·새 campaign ID로 재계획해도 같은 lineage로 거부되고,
  attempt ordinal만 별도로 증가함
- append-only holdout line과 case-register가 같은 sealed commit이 아니거나 prefix가 바뀌면 provider 호출 0
- B12a/B12b/B12c/B12d와 P16 fixture에서 자동 파일 delete/inverse가 0이고 B12b는 conflict/write0→
  Coordinator 사용자 선택→fresh checkpoint→same-owner apply를 거쳐 승인·동시·pre-existing bytes가 보존됨

---

## 5. 변경 대상과 책임

### 5.1 중앙 정책

| 정본 | 변경 |
|---|---|
| `workspace/reference/spec.md` | 상위 current-contract 테스트 정책에 admission/lifecycle 경계 추가 |
| `dddjango/skills/discipline-tdd/references/final.md` | §3 전체의 단일 규범 owner |
| `dddjango/skills/discipline-tdd/SKILL.md` | 역할이 참조할 압축 요약·반송 조건 |
| workspace/Codex mirror | `corpus_mirror_sync.py --write`와 Codex SKILL 의미 미러 |

`discipline-tdd`만 테스트 자격을 정의한다. 다른 knowledge skill은 이 enum이나 금지 목록을 복제하지
않고 중앙 decision을 가리킨다. 역할이 reference를 추가로 읽지 않아도 판정할 수 있도록 여섯 상태,
권위 근거·독자 보장·중복의 핵심 admission과 반송 조건은 `discipline-tdd/SKILL.md` preload 본문에
완결하고, reference는 상세 예시·근거만 확장한다.

### 5.2 mechanics·knowledge carrier

다음 Claude reference/SKILL의 직접 test 생성 문구를 찾아 admission 전 candidate signal 또는
admit 뒤 작성 recipe로 낮춘다. reference는 항상 Claude
`dddjango/skills/*/references/final.md`를 먼저 편집하고 mirror tool로 workspace/Codex reference를
갱신한다.

| skill | 수정할 압력 |
|---|---|
| `discipline-tdd` | 중앙 admission과 함께 §7 Assertion Roulette의 “테스트 분리”를 자동 case 증식이 아닌 readability candidate로 교정 |
| `implementation-test` | 80/15/5 quota, 상위 버그의 unit 복제, AAA split, Free Ride, mutation, framework mechanics, layout. event union↔Enum은 승인 public/wire 근거가 있을 때의 유효 candidate로 보존 |
| `architecture-ddd` | Outbox/§6.8 테스트 층·빈 test package의 직접 의무 |
| `architecture-db` | Risky Write Test criteria와 CAS spy의 blanket test 의무 |
| `implementation-django` | TransactionTestCase/Outbox/Risky Write mechanics의 자동 test 생성 |
| `implementation-django-ninja` | direct Schema/helper/OpenAPI/framework error test carrier. event/OHS union↔Enum은 자동 세트가 아니라 승인 계약 candidate로 중앙 반송 |
| `implementation-django-web` | render/private helper test carrier |
| `discipline-houserules` | 기존 flat test의 무승인 move/split과 support package 생성. OHS wire Literal union 동기 계약은 승인 consumer/wire 근거가 있으면 보존 |

`discipline-cleancode`, `architecture-api`, `implementation-python` 등 나머지 knowledge도 Task 6 inventory에서 검색하되,
실제 독립 carrier가 없으면 “일관성을 위해” 수정하지 않는다.

### 5.3 Phase 1 역할과 G1

| 파일 | 변경 |
|---|---|
| `dddjango/agents/design-architect.md` | 모든 영구 test obligation을 decision row로 폐쇄 |
| `dddjango/agents/design-review-api.md` | API candidate를 제안하되 row 없이 의무 생성 금지 |
| `dddjango/agents/design-review-db.md` | DB/Risky Write candidate를 중앙 row로 반송 |
| `dddjango/agents/discipline-reviewer.md` | G1 직전 최종 명세·bounded related-test evidence 독립 감사 |
| `dddjango/commands/dddjango.md` | 최종 lens 반영 뒤 Phase 1 audit, G1 여섯 상태 직접 표시 |
| 대응 Codex 역할 SKILL | 플랫폼 형식을 유지한 의미 미러 |

DDD reviewer는 `architecture-ddd`의 수정된 candidate 규칙을 실제로 소비하는지 검증한다. 별도 역할
문구가 독립 의무를 만들고 있을 때만 수정한다.

최종 Phase 1 discipline reviewer의 declared loader는 Claude/Codex 모두
`discipline-cleancode, discipline-tdd, discipline-houserules, implementation-test`가 되게 한다.
Architect·acceptance·coder의 기존 loader에서 `discipline-tdd`가 실제 제공되는지도 source bundle로
확인한다. 검증 편의를 위해 역할이 선언하지 않은 skill을 pressure prompt에 몰래 추가하지 않는다.

Coordinator는 Architect 최종 decision 전과 Phase 2 dispatch 전에 같은 bounded lifecycle 검색을
소유한다. 입력 anchor는 changed/renamed/retired URL·public import path·OHS operation·event tag·error
code·model/constraint와 명세에 열거된 old→new identifier다. 이 anchor를 import/reference/test name/
fixture에서 찾고, hit test의 직접 helper/fixture 1-hop까지만 확장한다. 산출은
`anchor → hit path::test → 현재 보장 후보 → stale/retain/unknown → proposed decision id` 표다.
전체 suite inventory나 관련 없는 green test 편집으로 넓히지 않는다. renamed/retired anchor에 걸린
green stale 후보를 명세에서 누락하면 Phase 1 reviewer가 blocker로 반송하며, 종료 근거가 없으면
자동 delete가 아니라 pending/retain이다. P12가 이 discovery 경로를 검증한다.

G1은 최소 다음을 직접 보여 준다.

```text
새로 만들거나 강화할 영구 테스트(admit)
기존 테스트가 이미 보호해 새로 만들지 않는 후보(covered-no-new-test)
계약을 보존한 exact move/split/rename/consolidation(lifecycle-approved)
계약 종료로 삭제·약화할 기존 테스트(terminate)
비자격이라 테스트로 만들지 않고 다른 owner로 반송할 후보(reject)
정책·근거가 미확정돼 구현을 막는 후보(pending)
```

각 그룹이 비었으면 `없음`을 표시한다. reject는 구현을 막지는 않지만 어떤 설계 지시가 테스트가 아닌
다른 검증으로 바뀌었는지 사용자가 볼 수 있어야 한다. pending만 G1 통과를 막는다.
G1은 이어서 Phase 2가 수정할 exact existing test paths와 새 test paths를 열거하고, 그 경로의
single-writer window 승인 여부도 묻는다. 이 승인은 기능/테스트 decision 승인을 대신하지 않으며, 거절되면
설계는 승인할 수 있어도 target write와 G2만 보류한다.

### 5.4 Phase 2 역할과 첫 Green 뒤 owner correction

| 파일 | 변경 |
|---|---|
| `dddjango/commands/dddjango.md` | 모든 내부 의무→unit Red 변환 제거, admit owner별 dispatch |
| `dddjango/agents/acceptance-tester.md` | owner:acceptance admit과 승인 lifecycle/terminate만 실행, 첫 Green 뒤 자기 scaffold 정리 |
| `dddjango/agents/coder.md` | owner:coder admit과 승인 lifecycle/terminate만 실행, 외부↔내부 중복 재대조 |
| `dddjango/agents/discipline-reviewer.md` | Phase 2 의미 감사 |
| 대응 Codex 역할 SKILL | 의미 미러 |

Coordinator dispatch는 상태별로 고정한다. `admit(add|semantic-update)`만 새 Red를 만들고,
`covered-no-new-test`는 기존 권위 테스트가 실패하면 그 test만 Red anchor로 재사용한다.
`lifecycle-approved`는 열거된 artifact의 의미 보존 move/split/rename/consolidation 전후 같은
권위 partition을 실행하되 새 Red/case를 발명하지 않는다. `terminate`는 기존 owner에게 exact
delete/weaken만 보낸다. `reject`는 test 역할에 보내지 않고 `pending`은 Phase 2 전체를 막는다.

acceptance와 coder는 임시 import guard, skip/xfail, 대체 decorator, loader helper, availability test를
쓰기 **전** parent decision과 scaffold intent를 선언한다. 해당 surface의 첫 Green 직후, 늦어도 G2 전에
각 owner를 exact-path single-writer window 안에서 순차 재호출해 자기 correction을 직접 적용하게 한다.
Coordinator는 dispatch 전 current SHA와 반환 뒤 after SHA를 독립 확인한다. Coordinator/reviewer는 accepted
base→final diff와 decision/scaffold 표를 대조할 뿐 작성자를 추정하거나 inverse/delete를 자동 적용하지
않는다. 작업 전부터 존재한 artifact는 scaffold로 등록하거나 주변 정리로 삭제하지 않는다.

Coordinator·acceptance-tester·coder·Phase 2 discipline-reviewer의 현재 “새 migration case/coverage 금지”는
`implementation-only`와 승인 전 policy-conflict에 대해서만 유지하도록 모두 교정한다. 별도 사용자
migration 정책 승인과 bounded transition contract를 가진 row가 일반 admission을 통과해
`admit + owner:coder + boundary:db-guarantee`가 되면 Coordinator가 acceptance를 경유하지 않고 그 exact
transition만 coder의 DB integration Red로 직접 dispatch한다. 승인 사실 없이 이름만 바꾼 migration
mechanics는 계속 반송한다. P10은 `Coordinator → coder → Phase 2 discipline-reviewer → G2` actual bundle에서
승인 범위 밖 과거 state가 추가되지 않고 reviewer blanket ban이 재발하지 않는지 검증한다.

Phase 2 discipline audit는 다음 여덟 항목을 모두 본다.

1. 새·강화된 영구 test/assertion/support artifact마다 승인된 `admit`가 있는가
2. owner/boundary와 실제 테스트 위치·oracle이 일치하는가
3. 후보가 기존 권위 partition과 중복되지 않고 독자 failure mechanism을 가지는가
4. `covered-no-new-test/reject/pending`에서 새 test/path가 생기지 않았는가
5. 계약 종료 삭제·약화에 `terminate`, 계약 보존 move/split/rename 및 중복 artifact 제거에
   `lifecycle-approved`가 있는가; 기존 bytes에 current-run 예외를 사후 적용하지 않았는가
6. 사전 등록 scaffold가 owner correction으로 모두 제거됐고 accepted base→final의 모든 changed test hunk가
   승인 decision에 결속되며, single-writer 승인과 owner tagged result/applied hunk, conflict 사용자 선택,
   before/after/current/final digest가 일치하고
   mixed/overlap/concurrent correction에서 승인·사용자 bytes가 보존됐는가
7. framework/private/source/test-tool mechanics가 다른 이름으로 재유입되지 않았는가
8. migration policy-conflict pending이 Phase 2로 넘어오지 않았고 승인된 P10은 coder와 최종 reviewer에서
   blanket reject되지 않았는가

한 항목이라도 실패하면 G2가 아니라 G1′/Phase 2 correction으로 반송한다.

### 5.5 사용자 문서

| 파일 | 변경 |
|---|---|
| `README.md` | 사용자 언어로 admission, no-new-test, lifecycle, terminate, reject/pending, owner correction 설명 |
| `workspace/flow/dddjango-timeline.html` | Phase 1 audit→G1→admit-only Red→post-Green owner correction→G2 흐름 |
| `workspace/DEVLOG.md` | 원인, 중앙 owner, no-checker/no-eval, 합법 예외, pressure 결과 |

문서에는 내부 field 전체를 복사하지 않는다. checker 수는 19로 유지한다.

### 5.6 exact path matrix

구현 허용 경로는 다음으로 닫는다. brace 표기는 계획의 축약이며 실제 stage에서는 경로를 하나씩
열거한다.

```text
상위 정책
  workspace/reference/spec.md

Claude knowledge 정본
  dddjango/skills/discipline-tdd/{SKILL.md,references/final.md}
  dddjango/skills/implementation-test/{SKILL.md,references/final.md}
  dddjango/skills/architecture-ddd/references/final.md
  dddjango/skills/architecture-db/{SKILL.md,references/final.md}
  dddjango/skills/implementation-django/{SKILL.md,references/final.md}
  dddjango/skills/implementation-django-ninja/{SKILL.md,references/final.md}
  dddjango/skills/implementation-django-web/{SKILL.md,references/final.md}
  dddjango/skills/discipline-houserules/{SKILL.md,references/final.md}

Claude runtime prompt
  dddjango/commands/dddjango.md
  dddjango/agents/{design-architect,design-review-api,design-review-db,
                   acceptance-tester,coder,discipline-reviewer}.md

Codex semantic mirror
  codex-dddjango/skills/{discipline-tdd,implementation-test,architecture-db,
                         implementation-django,implementation-django-ninja,
                         implementation-django-web,discipline-houserules}/SKILL.md
  codex-dddjango/skills/{dddjango,dddjango-design-architect,
                         dddjango-design-review-api,dddjango-design-review-db,
                         dddjango-acceptance-tester,dddjango-coder,
                         dddjango-discipline-reviewer}/SKILL.md

mirror tool 생성물
  workspace/reference/<changed-skill>/reference/final.md
  codex-dddjango/skills/<changed-skill>/references/final.md

사용자 문서·pressure
  README.md
  workspace/flow/dddjango-timeline.html
  workspace/DEVLOG.md
  workspace/pressure/meaningful-tests/{README.md,cases.jsonl,schema.json,evidence.jsonl}
  workspace/tools/run_meaningful_test_pressure.py
```

`design-review-ddd`, `discipline-cleancode`, `architecture-api`, `implementation-python`과 그 Codex 대응 파일은 carrier
inventory의 verify-only 대상이다. 역할 자체에 중앙 row를 우회하는 직접 명령이 실제로 발견될 때만
같은 Task의 수정 허용 경로로 승격하고, 그 이유와 pressure case를 plan/evidence에 먼저 기록한다.

---

## 6. 구현 순서

### Task 0 — 승인 기준선과 RED pressure

- [ ] 사용자에게 감사 문서와 이 계획의 final diff를 보여 주고 승인받는다.
- [ ] 승인된 감사·계획만 별도 planning commit으로 동결한다.
- [ ] 사용자가 승인한 Linux systemd/cgroup v2 executor에서 두 provider CLI, manager-owned transient service
  InvocationID/result retention, membership 조회/stop, phase-unit escape 0과
  close-intent→exit-ready→exit-observed→release/inactive 정상 closure 및
  stop-intent→forced-stop→crash-closed, failed/retained terminal result-observed→manager
  stop/release/reset→inactive self-check를 통과시킨다. Darwin host 결과로 대체하지 않는다.
- [ ] pressure 5개 자산을 만들고 runner fake-provider/self-check를 통과시킨다.
- [ ] runner LOC·다섯 책임표를 보고하고 §4.1 임계 초과 시 사용자 scope 재승인 전 구현을 멈춘다.
- [ ] provider를 한 번도 호출하기 전에 5개 exact path를 bootstrap commit한다. `evidence.jsonl`은
  lineage root·2-round budget·초기 logical case registry·evaluation harness digest를 가진 canonical
  `ledger-header`만 두며 generic batch seal로 5개 resulting blob을 결속하고,
  staged/committed runner로 header/schema/self-check를 다시
  검증한다. working-tree runner/schema/cases로 baseline을 시작하지 않는다.
- [ ] 각 pressure phase 전 그 phase의 exact stage-path 합집합/index에 대한 `pressure-commit-window`를 한 번
  승인받아 phase의 각 seal subset/generation에 결속한다. crash 뒤에는 window를 자동 종료하고 current
  HEAD/index/working manifest를 보여 준 fresh
  `resume-original` 승인 없이는 prior/result partial state도 재-stage/commit하지 않는다.
- [ ] current Claude/Codex source로 B/P case baseline을 실행한다.
- [ ] baseline에서 실제 재현된 실패와 이미 막힌 사례를 분리한다.

bootstrap 뒤 runner/schema/cases/README를 고쳐야 하면 **current lineage provider 호출 이력이 0**이고 열린
attempt도 0인지 확인한 뒤 old root를 `abandoned-no-provider`로 닫고, self-check를 통과한 exact changed subset과
generation+1 새 active `ledger-header`를 하나의 sealed `lineage-correction` commit으로 봉인한다. defective case는
old line을 rewrite하지 않고 old→new case-register+replacement line으로 supersede한다.
첫 provider 호출 뒤 existing case/oracle/route/DAG와 logical hash, runner/schema/scoring rule은 current
lineage에서 immutable하다. 새 holdout은 기존 cases prefix를 보존한 append-only line+case-register sealed
commit으로만 추가한다. 기존 attempt의 provider input/oracle을 소급 변경하거나 case rename·repetition slot
추가로 새 key를 만들지 않는다. case 결함은 current campaign NO-GO와 사용자 승인을 먼저 기록하고
case-register supersede와 새 unique leaf header를 같은 lineage-correction으로 봉인한 뒤 전체 active registry를
다시 실행한다. harness 결함은 여기에 더해 prior semantic-output-fail의 exact old answer를 old-fail/new-pass로
결정적 re-score하는 `harness-defect-resolution`이 성립해야 하며, raw 부재·digest mismatch·re-score 불성립이면
current family를 permanent NO-GO로 둔다. 성립해도 inherited counter를 소비하고 전체 active registry의
baseline/final/holdout을 다시 실행하기 전에는 prior selection-risk를 resolved로 세지 않는다.

**중단 조건:** raw가 저장소 안에 생성됨, provider tool/file access를 비활성화할 수 없음,
planned invocation이 누락됨, 반대 runtime으로 대체하려 함.

### Task 1 — 중앙 `discipline-tdd` admission

- [ ] `workspace/reference/spec.md`과 Claude discipline reference/SKILL을 수정한다.
- [ ] loader-minimal 중앙 판정 projection으로 B1/B3/B4/B6/B11과 P1–P11/P14/P15의 decision만
  RED→GREEN으로 만든다. 역할 dispatch·discovery·file effect까지 Task 1 GREEN이라고 주장하지 않는다.
- [ ] §2.4의 0→target-only 2→write→0 gate로 reference를 갱신한 뒤 Codex SKILL 의미 미러를 맞춘다.
- [ ] Task의 plan/terminal/review-closure evidence와 exact source allowlist만 각 단계의 규칙대로 commit한다.

### Task 2 — 분산 knowledge carrier 반송

- [ ] `implementation-test`의 quota·자동 split·framework mechanics·layout 압력을 수정한다.
- [ ] 실제 확인된 architecture/implementation/house-rule의 직접 test mandates를 중앙 row로 반송하고,
  clean-code는 verify-only inventory 결과를 기록한다.
- [ ] 실제 carrier가 없는 skill은 수정하지 않고 inventory에 “verify-only”로 남긴다.
- [ ] route-expanded B8/B9/B10/P13과 합법 DB/application/adapter 보존 case를 양 runtime에서 검증한다.
- [ ] reference별로 편집 전 `--check --format json` exit 0을 확인한다. Claude 정본 편집 뒤 exit 2와
  drift skill이 현재 대상뿐임을 확인한 다음에만 `--write`하고, 다시 exit 0·11/11을 확인한다.
- [ ] exact changed paths만 commit한다.

### Task 3 — Architect·reviewer·G1 배선

- [ ] Architect decision table과 자기모순 검사를 추가한다.
- [ ] Coordinator가 changed/renamed/retired anchor의 bounded lifecycle 검색표를 만들고 Architect와
  Phase 1 reviewer에게 전달하게 한다.
- [ ] API/DB reviewer proposal이 row 없이 test obligation이 되지 않게 한다.
- [ ] Phase 1 discipline review를 모든 실제 변화에서 G1 직전 필수로 둔다.
- [ ] Coordinator G1에 admit/covered-no-new-test/lifecycle-approved/terminate/reject/pending 여섯 상태를 표시한다.
- [ ] B2/B6/B7/P11/P12를 design-architect→discipline-reviewer→Coordinator loader-minimal 다단계 bundle로
  검증한다.

### Task 4 — admit-only Red와 post-Green owner correction

- [ ] Coordinator의 모든 내부 의무→unit Red carrier를 제거한다.
- [ ] acceptance/coder를 owner별 admit 실행으로 제한한다.
- [ ] Coordinator·acceptance·coder·discipline-reviewer의 migration blanket carrier를 승인 전 차단과
  승인 후 bounded db-guarantee 재입장으로 분기한다.
- [ ] Coordinator의 accepted-base/final-diff audit, 사전 scaffold 표, 첫 Green 뒤
  owner 직접 `owner-correction-required`, exact-path single-writer 승인, 별도 correction checkpoint mismatch의
  write 0, `applied-contextual|checkpoint-drift|conflict-awaiting-user` tagged handoff, conflict 시
  Coordinator 사용자 선택→fresh checkpoint→same-owner 재호출을 추가하고
  자동 inverse/delete/rollback은 두지 않는다.
- [ ] Phase 2 eight-point audit와 G1′ 반송을 추가한다.
- [ ] B2/B3/B5/B10/B12a/B12b/B12c/B12d 및 lifecycle P4/P5/P7/P9/P10/P15/P16을 실제 Coordinator→owner→Phase 2 reviewer
  loader-minimal handoff와 synthetic patch로 양 runtime에서 검증한다.

### Task 5 — 문서 정합화

- [ ] README, timeline, DEVLOG를 runtime prompt와 맞춘다.
- [ ] “모든 unit test 금지”, “기존 테스트 자동 삭제”, “20번째 checker 추가”로 오해될 문구가 없는지 본다.
- [ ] 배포 완료와 source 구현 완료를 분리해 기록한다.

### Task 6 — 전체 검증과 독립 리뷰

- [ ] 관련 skill/reference/role/Coordinator의 test-mandate carrier를 다시 전수 검색한다.
- [ ] 중앙 owner를 우회하는 직접 의무가 0인지 named carrier 표로 확인한다.
- [ ] core case가 loader-minimal에서 통과하고 route-expanded path/heading은 case가 아니라 SKILL 표에서
  유일하게 도출되며, unselected heading의 직접 우회 명령이 0인지 확인한다.
- [ ] Claude/Codex reference mirror와 역할 의미 parity를 검증한다.
- [ ] final B1–B12(B12a–d)/P1–P16/holdout matrix를 양 runtime 3회 실행하고 선택 final attempt의
  planned=terminal exact, terminal 전부 complete-success, oracle true, invalidate 0, 유효 review-closure 1을
  확인한다.
- [ ] 세 독립 reviewer가 spec trace, corpus contradiction, overfit/effectiveness를 검토한다.
- [ ] Blocker/Important 0과 세 reviewer GO 전에는 완료를 주장하지 않는다.

### Task 7 — release 인계

- [ ] source 구현 완료 시 현재 두 manifest version과 cache drift 여부를 보고한다.
- [ ] version/tag/push/marketplace update는 별도 사용자 승인으로 남긴다.
- [ ] release 승인 시 공식 절차와 설치 cache 갱신을 플랫폼별로 검증한다.

---

## 7. 정적·행동 검증

### 7.1 코퍼스와 플러그인

```bash
python3 workspace/tools/corpus_mirror_sync.py --check
python3 -m json.tool dddjango/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool codex-dddjango/.codex-plugin/plugin.json >/dev/null
claude plugin validate dddjango --strict
python3 -m py_compile workspace/tools/corpus_mirror_sync.py workspace/tools/run_meaningful_test_pressure.py
python3 workspace/tools/run_meaningful_test_pressure.py self-check
git diff --check
git status --short
```

추가 확인:

- Claude 11개 `references/final.md`와 Codex 대응 파일 byte-exact 11/11
- 두 manifest의 name이 `dddjango`이고 version이 서로 같음
- checker 수 19, `dddjango/scripts` tracked/untracked 변경 0
- `workspace/eval` tracked/untracked 변경 0
- pressure raw·patch·provider stdout/stderr가 tracked/untracked repo path에 0
- unrelated `docs/`, tree-vocabulary HTML 등 사용자 파일 보존

### 7.2 corpus carrier inventory

다음 의미의 문구를 관련 11 knowledge skill/reference와 7개 역할, 양 Coordinator에서 찾고 한 행씩
`owner | current carrier | preload 또는 SKILL-derived route | final disposition | pressure case`로 기록한다.

```text
unit Red / 내부 의무 / acceptance criteria / Test criteria
AAA split / Free Ride / Assertion Roulette / mutation
Walking Skeleton / availability / find_spec / import_module
Pydantic / ValidationError.loc / Schema / OpenAPI helper
StrEnum / coercion / direct model
docstring / slots / AST / inspect / private helper / monkeypatch seam
migration / historical state / MigrationExecutor / seed
Risky Write / CAS / Outbox / TransactionTestCase
test package / unit-integration-e2e directory / move / split
```

검색 hit를 기계적으로 수정하지 않는다. 실제로 영구 테스트를 직접 명령하는 carrier만 수정하고,
설명·예외·이미 중앙 row를 요구하는 문구는 보존한다. 각 SKILL의 상세 reference 표가 가리키지 않는
heading에도 중앙 row를 우회하는 직접 명령이 0인지 full-file로 확인하고, route-expanded case의 path/heading이
SKILL에서 유일하게 도출되는지도 별도 열로 증명한다.

### 7.3 행동 성공 조건

- baseline과 final은 candidate source-tree digest가 다르고 모든 attempt가 terminal/closure로 닫혀야 한다.
- 선택 final attempt는 planned key 전부가 complete-success·oracle true이고 semantic/infra fail,
  blocked/unknown/invalid/invalidate와 열린 process/commit recovery blocker가 0이며 exact
  `phase-supervisor-closed` marker가 있다.
- final B1/B2/B3/B4/B7/B8/B9/B10/B11/B12a/B12b/B12c/B12d에서 비자격 테스트 생성 또는 무승인 delta 잔존이 0이다.
- B5 synthetic tree에서 이번 Red scaffold가 0이다.
- B6는 `implementation-only` 1개와 pending 7개를 정확히 보존한다.
- P1–P16의 합법적 테스트·lifecycle·migration 재입장과 기존 artifact를 blanket reject/delete하지 않는다.
- active registry의 모든 logical B/P/negative·positive·lifecycle holdout의 양 runtime slot `{1,2,3}`가 전부 terminal
  success·oracle true이고 attempt ordinal/label/campaign 변경으로 실패 lineage를 우회하지 않는다.
- 모든 dynamic holdout canonical line이 byte-immutable cases prefix에 append되고 같은 sealed
  holdout-register의 case-register digest와 일치하며, ledger/attempt/closure의 evaluation harness digest가 같다.
  hook-failed register의 인증된 old logical case는 recovery commit의 exact 마지막 preserve row로
  active-development에 남아 다음 정상 register의 fresh independent holdout과 함께 전체 matrix에 포함되고,
  인증 불가 case를 replacement로 버리지 않는다.
- lineage correction은 unique active leaf header 하나만 만들고 defective case old line을 보존한 old→new
  registry transition과 full rerun을 결속하며, abandoned/NO-GO predecessor 성공을 이어받지 않는다.
- Claude/Codex 양 runtime이 같은 decision/route 의미를 가진다.
- 핵심 admission/handoff는 reference를 주입하지 않은 loader-minimal bundle에서 통과한다.
- runner/parser 실패, blocked runtime, schema mismatch를 scorer PASS로 세지 않는다.
- terminal 뒤 review-closure 전 raw가 사라지거나 commitment가 다르면 새 호출로 덮지 않고 invalidate한다.
- evidence를 바꾸는 모든 commit의 generic seal이 exact event-kind/row vector와 staged path blob을 결속한다.
  no-outside strict-subset은 batch-missing whole recovery, sealed set 밖 path는 commit-kind table의 fresh
  baseline/invalidate/blocker 전이를 따른다. hook source는 failed kind discriminator가 허용한 exact
  manifest-bound 선택 전 새 candidate가 아니다. ordinary kinds만 세 source choice를, bootstrap은 clean-base/
  repair/fresh-bootstrap choice를 허용하고 commit-recovery/source-resolution mutation은 즉시 blocker다.
  repair branch는 R→U→S direct first-parent와 exact tree/path/source equality가 없으면 진행하지 않으며, closure
  recovery 뒤 필요한 subtype별 terminal 재실행을 생략한 fresh closure로 untested source를 merge하지 않는다.
  repair root는 causal holdout/plan/terminal/closure 전부에 전파되고 두 번째 mutation은 새 chain 0 blocker다.
  semantic output 1 byte 이상은 infra retry로 강등하지 않는다.
- generic seal이 base HEAD·expected parent·prior/intended index tree·path별 prior/result blob과 commit trailer를
  결속한다. 정상 phase는 한 번 승인된 phase-scoped pressure window의 subset을 쓰고, no-commit partial/exact
  index와 commit-success-before-observation은 원래 commit kind/stage set을
  식별하되 crash 뒤 fresh `resume-original` 사용자 승인 없이는 prior/result 상태도 쓰지 않는다. 승인 뒤에만
  idempotently 재개하며 exact committed child는 읽기 전용으로 인정한다. source 불일치 fallback 외에는 recovery
  row를 발명하지 않고 사용자 unstage와 외부 staged 변경을 자동 reset하지 않는다.
- semantic correction은 실패 key의 model-visible bundle/prompt가 실제로 바뀌고 독립 승인된 최대 2 round만
  허용하며, 무관 source digest churn은 provider 전 차단한다. unknown/complete-invalid와 post-call harness
  변경은 current campaign을 NO-GO로 닫는다. harness 변경은 exact old-answer old-fail/new-pass re-score와 명시적
  superseding lineage full rerun이 모두 없으면 prior selection-risk를 해소하거나 재호출하지 않는다.
- user-approved Linux systemd/cgroup v2 executor에서 phase/invocation intent, unit InvocationID, membership 0과
  close-intent/exit-ready/manager-success 기반 정상 supervisor closure 및 crash-closed 실패 분기가 검증되며
  terminal-success/missing-close, terminal-non-success/remaining-member와 membership0/manager-failed도 result-first
  durable observation→identity-bound manager inactive 전이→abnormal common suffix로 닫힌다.
  Darwin 결과로 양 runtime pressure를 대체하지 않는다.

---

## 8. 완료 기준

1. `discipline-tdd`가 영구 테스트 자격의 유일한 owner다.
2. 다른 skill/reference는 candidate signal·작성 mechanics·위치 recipe만 소유한다.
3. 모든 영구 test obligation은 정확히 한 decision row에 연결된다.
4. G1은 admit/covered-no-new-test/lifecycle-approved/terminate/reject/pending을 사용자에게 직접 보여 준다.
5. Coordinator는 `admit`만 Red slice로 만든다.
6. acceptance/coder가 같은 보장을 복제하지 않고 owner/boundary를 지킨다.
7. 첫 Green 뒤 이번 실행의 scaffold가 owner correction으로 0이고 accepted base→final의 모든 test hunk가
   승인 decision에 결속되며, repo-external 감사 preimage·single-writer 승인·owner tagged hunk·Coordinator의
   conflict 사용자 선택·fresh checkpoint/write-0 규칙으로 사용자·승인 bytes가 보존된다.
8. G2 전 Phase 2 eight-point audit가 통과한다.
9. migration 승인 전 1+7은 Architect→reviewer→Coordinator에서 보존되고 승인 후 P10은
   Coordinator→coder→Phase 2 reviewer→G2로 재입장한다.
10. 승인된 ErrorOut/public Python/preserve-established/application/domain/DB/adapter 계약을 과잉 제거하지 않는다.
11. 계약 종료 목적의 기존 테스트 삭제·약화는 exact `terminate`, 계약 보존 move/split/rename과 승인된
    중복 artifact 제거는 exact `lifecycle-approved(consolidate-preserving)`로만 일어나며 current-run
    scaffold 예외가 accepted base의 기존 artifact에 쓰이지 않는다.
12. reference mirror 11/11, Claude/Codex 역할 의미 parity, strict plugin validation이 통과한다.
13. 기존 checker 19개와 frozen eval은 변경되지 않는다.
14. 선택 final pressure attempt의 planned/terminal key가 같고 terminal 전부 complete-success·oracle true,
    invalidate와 열린 recovery blocker 0, `phase-supervisor-closed` 1·최신 recovery/invalidate set을 결속한 유효
    review-closure 1이며(stale historical closure는 PASS에서 제외) active registry의 모든 logical B/P/holdout
    양 runtime slot `{1,2,3}`가 통과한다. cases append/register와 evaluation harness
    digest가 전 단계에서 일치하고 unresolved selection-risk 0, unique active lineage leaf와 모든 evidence commit이
    base HEAD/index/path blob까지 가진 generic seal로 닫힌다. harness-defect resolution은 old-answer re-score와
    full matrix 재실행을 둘 다 증명한다. open pressure-commit window, resume/source choice 대기,
    unexpected-path 및 ambiguous-direct-child blocker가 0이고 commit-kind·terminal subtype별 hook failure 전이가
    모두 끝났다. repair root는 exact R→U→S first-parent 증명 뒤 closure에서 closed이고, failed holdout recovery의
    마지막 preserve row와 다음 정상 register의 new holdout hash 및 replacement plan/terminal을 모두 포함한다.
15. pressure 인프라는 5개 자산을 넘지 않고 provider raw·patch를 Git에 저장하지 않으며, runner가 §4.1 임계를
    넘으면 LOC·책임표와 scope 재설계에 대한 명시적 사용자 승인이 있고 Linux systemd/cgroup v2 executor
    prerequisite가 실제 capability self-check를 통과한다.
16. 독립 적대 리뷰의 Blocker/Important가 0이고 모든 reviewer가 GO다.
17. 플러그인 구현과 Broccoli 테스트 정리, source release와 runtime 배포를 각각 별도 작업으로 유지한다.

---

## 9. 적대 리뷰 기록

### 9.1 17차 동결본

- SHA-256: `03302cd0caaf0c798d4fd5c4d08518fd5f17a4b850da22eecddafdfe67fe00af`
- 2,516행, code fence 160
- spec trace: GO
- overfit/effectiveness: NO-GO, Important 3
- merge/execution: NO-GO, Blocker 2 / Important 1

### 9.2 17차 finding의 처리

| finding | 처리 |
|---|---|
| action live proof의 attempt binding 누락 | model file action 자체를 제거하고 no-tools structured response로 전환 |
| quarantine에서 existing OID를 처리하지 못함 | custom quarantine ODB/index/ref 설계 전체 제거 |
| raw를 Git에 넣기 위한 보안 인프라가 목표 대비 과함 | raw-never-Git 채택, 37개 자산을 5개로 축소 |
| capsule 생성과 실행이 두 process라 stale swap 가능 | capsule/action supervisor 설계 제거 |
| ref CAS 뒤 audit 실패 상태·HEAD 재독 TOCTOU | custom commit/ref CAS/final dual audit 제거, 표준 Git과 기존 hook 사용 |

### 9.3 18차 축소본 동결 리뷰

- SHA-256: `6c2806b0cc7f3c85afb6aeee1cda4e231880e304a978b0b10c938acd085915ac`
- 650행, code fence 16
- spec trace: NO-GO, Blocker 1 / Important 4
- overfit/effectiveness: NO-GO, Important 3 / Nit 3
- merge/execution: NO-GO, Blocker 2 / Important 2

### 9.4 18차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec | covered와 `reject:duplicate`, 계약 종료와 보존 이동이 겹침 | duplicate는 covered로 단일화하고 `lifecycle-approved`를 `terminate`와 분리; G1에 여섯 상태 모두 표시 |
| spec | Assertion Roulette carrier 오귀속, event/OHS 보존 경로 누락 | Assertion Roulette를 `discipline-tdd`로 바로잡고 implementation-test·Ninja·house-rule의 승인 event/OHS를 명시적 candidate와 P13으로 보존 |
| spec | owner/boundary가 자유 필드이고 ErrorOut Python/HTTP가 혼합됨 | owner별 폐쇄형 boundary 조합을 정의하고 같은 surface를 public-Python P11과 HTTP wire P11의 별도 partition으로 판정 |
| spec | green stale test discovery가 실행 변경과 연결되지 않음 | Coordinator의 changed/renamed/retired anchor 한정 검색, 1-hop 확장, 표 산출, P12를 추가 |
| spec | migration 승인 후 역할의 blanket ban과 충돌 | 승인 전 pending과 승인 후 일반 `db-guarantee` admission 재입장을 분리하고 P10으로 검증 |
| effectiveness | case가 실제 loader와 달라도 통과하고 역할 handoff를 합침 | role 선언에서 exact loader set을 계산하고 required heading과 대조; 각 stage artifact bytes/digest를 다음 독립 invocation에 결속 |
| effectiveness | domain·terminate·승인 후 migration 양성 폐쇄가 없음 | P8 domain admit, P9 exact terminate, P10 migration 재입장 양성을 추가 |
| effectiveness | success terminal 뒤 raw 소실을 append-only로 무효화 불가 | `invalidate`와 `attempt-review-closure` event를 추가하고 effective PASS에 closure·invalidate 조건을 결속 |
| effectiveness | pressure가 미래 모든 생성 테스트를 증명하는 것으로 과장될 수 있음 | 동결 source의 표적 decision/file-effect 증거로 범위를 제한하고 실제 테스트 정확성은 정상 TDD/reviewer가 소유 |
| execution | 최초 5개 자산과 verifier가 uncommitted 상태로 baseline 가능 | provider 전 5개 자산 bootstrap commit과 correction-before-attempt 규칙을 추가 |
| execution | raw completeness·부분 patch·post-terminal loss 상태가 없음 | launch/provider-complete marker, stdout 기반 patch 재도출, atomic evidence batch, invalidate를 추가 |
| execution | evidence 문자열 필드가 닫히지 않음 | event별 `oneOf`, enum/runner ID 제한, `additionalProperties: false`, provider 자유 필드 0으로 폐쇄 |
| execution | mirror 0→target-only drift→write→0이 Task 1에 없음 | 모든 reference Task에 적용하는 전역 mirror gate로 승격 |
| 비례성 | 축소 뒤에도 보안 인프라가 되살아날 위험 | 5개 자산, no-tools structured response, raw-never-Git, 표준 Git을 유지하고 action/VM/custom ODB를 계속 제외 |

### 9.5 19차 동결 리뷰

- SHA-256: `0aa518ff8a9b6238276c58ef9b39f977e7ff001a13216bbf68c98ae56b5a05a4`
- 798행, code fence 18
- spec trace: NO-GO, Blocker 1 / Important 3
- overfit/effectiveness: NO-GO, Important 2 / Nit 3
- merge/execution: NO-GO, Blocker 2 / Important 1

### 9.6 19차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec | scaffold와 무승인 current-run artifact를 합법적으로 원복할 전이가 없음 | 영구 lifecycle과 분리한 exact current-run ledger, `cleanup-current-run`, `rollback-unapproved-current-run`을 정의; 기존 artifact에는 사용 금지 |
| spec | `covered-no-new-test`와 `covered` literal 혼용 | enum·G1·dispatch·audit·completion을 `covered-no-new-test` 하나로 통일 |
| spec | migration P10이 acceptance를 경유하고 Coordinator/final reviewer blanket ban이 남음 | Coordinator가 coder로 직접 dispatch하고 Phase 2 reviewer/G2까지 actual chain을 검증; 네 carrier 모두 교정 |
| spec | Task 1이 뒤 Task 소유 case까지 GREEN이라고 주장 | Task 1은 중앙 decision projection만, Task 2/3/4는 각 carrier·handoff·file effect, Task 6은 전체 end-to-end로 분리 |
| effectiveness | case-selected heading이 actual loader를 우회 | core는 role+declared SKILL 전체 bytes의 loader-minimal로 검증; reference route는 SKILL 표에서만 도출하고 unselected full-file carrier 0을 별도 감사 |
| effectiveness | `reject:no-authoritative-contract` 행동 case 없음 | 승인 없는 우연한 PK 순서 B11과 같은 표면의 승인 positive P14를 쌍으로 추가 |
| effectiveness | positive가 `admit 가능`, PASS reducer, Task 4 case가 느슨함 | P2/P3/P13 exact admit, 모든 terminal success·oracle true reducer, Task 4에 B10/P9/P10/P15 추가 |
| execution | blocked/unknown/invalidated attempt를 closure로 닫지 못함 | start gate·parent-owned pipe·process group 회수와 terminal subtype별 oneOf/closure를 정의; closed와 PASS를 분리 |
| execution | B6 stage identity·artifact digest가 evidence schema로 표현 불가 | invocation key에 stage/role/mode와 DAG를 넣고 success branch에 parent/input/output/bundle digest를 결속 |
| execution | hook이 같은 허용 path bytes를 바꿔도 post-commit path 검사 통과 | commit별 exact stage matrix와 committed source/bundle digest 재검증; mismatch invalidate·merge 중단 |
| 비례성 | 수정이 다시 보안 플랫폼으로 커질 위험 | 같은 5개 자산·stdlib runner·표준 Git 안에서만 보강하고 action/VM/custom ODB는 추가하지 않음 |

### 9.7 20차 closure 재검 기준

현재 본문의 정확한 hash를 동결한 뒤 같은 세 reviewer가 서로 독립적으로 다음을 다시 검토한다.

1. **spec trace:** 영구 lifecycle/current-run cleanup 분리, canonical literal, Task별 case 소유와 P10 chain이 닫혔는가
2. **overfit/effectiveness:** loader-minimal과 SKILL-derived route, B11/P14, exact positive/PASS가 과적합 없이 실효적인가
3. **execution/corpus:** terminal subtype·stage DAG·closure·commit digest gate가 5개 자산과 표준 Git 안에서 실행 가능한가

세 리뷰가 동일 동결본에 대해 모두 Blocker/Important 0, GO일 때만 상태를 “적대 리뷰 closure 완료”로 바꾼다.

### 9.8 20차 동결 리뷰

- SHA-256: `05b34600bd1b8cd8f5f8695e6c37ad3d14b4603cd375af31112cc367415d7044`
- 922행, code fence 18
- spec trace: NO-GO, Blocker 1 / Nit 1
- overfit/effectiveness: NO-GO, Important 1 / Nit 2
- merge/execution: NO-GO, Blocker 2

### 9.9 20차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec/effectiveness | cleanup provenance가 model self-declared이고 unapproved delta에는 parent/scaffold가 없음 | Coordinator가 role write 전 run-base/preimage를 고정하는 별도 mutation journal을 소유; cleanup과 rollback의 근거를 분리 |
| spec/effectiveness | 기존 identical scaffold와 같은 파일의 후속 승인 변경을 안전하게 보존하지 못함 | forward/inverse delta·pre/post digest·creator slice를 기록하고 non-overlap만 원복; B12/P16 쌍을 추가 |
| spec | completion의 terminate와 consolidation 제거가 문자상 충돌 | 계약 종료 삭제와 승인 중복 consolidation 제거를 별도 문장으로 구분 |
| effectiveness | B/P·partition·route key가 model-visible 대리 신호가 될 수 있음 | provider input에서 모든 runner ID/oracle/route key를 제외하고 canary self-check로 0을 증명 |
| effectiveness | 같은 source의 실패를 새 attempt ID 성공으로 선택 가능 | semantic failure 동일 source 재선택 금지; prelaunch 환경 변화만 configuration digest 변경 시 예외 |
| execution | numeric PID/PGID reuse로 무관 process signal 또는 closure 고착 가능 | non-exec supervisor, parent-liveness, boot/birth identity, supervisor-reaped를 결속하고 bare numeric signal 금지 |
| execution | plan commit 중 candidate source가 바뀌면 terminal 전 invalidate도 못하고 attempt가 열림 | pre-plan external immutable input snapshot과 key별 bundle/root prompt digest를 기록하고 prompt-state별 prelaunch/dependency terminal로 closure |
| 비례성 | 보강이 별도 영구 시스템으로 커질 위험 | 기존 runner의 run-local marker/journal과 기존 cases/schema만 사용; 영구 자산은 5개 유지 |

### 9.10 21차 closure 재검 기준

1. **spec trace:** Coordinator-owned mutation provenance가 기존 artifact·후속 승인 delta를 보존하며 cleanup 우회를 막는가
2. **overfit/effectiveness:** B12/P16, model-visible canary, 동일 source 재선택 규칙이 blanket preserve/delete 없이 실효적인가
3. **execution/corpus:** boot/birth/reaped identity와 pre-plan input snapshot·prelaunch oneOf가 crash/hook 뒤에도 모든 attempt를 닫는가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.11 21차 동결 리뷰

- SHA-256: `647a2bcd53b224d19303ce71d3827955696af8573179b0869e4954523cb0741b`
- 1,012행, code fence 20
- spec trace: NO-GO, Blocker 2 / Important 1
- overfit/effectiveness: NO-GO, Important 1 / Nit 1
- merge/execution: NO-GO, Blocker 2 / Important 1

### 9.12 21차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec | 파일 mutation 하나에 승인 Red와 무승인 scaffold가 섞이면 inverse가 승인 bytes까지 지움 | creator/inverse 자동 rollback 설계를 제거; accepted base→final hunk audit와 explicit owner correction으로 전환하고 B12a/b/c로 non-overlap·overlap·co-created mixed를 각각 검증 |
| spec | 같은 UID의 role·사용자·subprocess를 creator ID/mode 0700으로 구별할 수 없음 | 기술적 writer provenance 주장을 제거; 모든 unexplained delta는 보존한 채 blocker로 표면화하고 자동 delete/reset을 금지; test 부산물은 repo 밖으로 보냄 |
| spec | `local-refactor`, `retire-replacement`가 dispatch/audit/completion/case에 닫히지 않음 | 불필요한 두 action을 폐쇄 enum에서 제거; 의미 보존은 move/split/rename/consolidate, 종료는 delete/weaken으로 축소 |
| effectiveness | post-launch이지만 model output 전인 provider 장애가 semantic failure와 합쳐짐 | `semantic-output-fail`과 `provider-infra-fail-before-model-output`을 semantic bytes 존재 여부로 분리; semantic 실패 same-source 재선택 금지와 infra bounded retry를 함께 정의 |
| effectiveness | B12가 non-overlap만 통과하고 same-span/co-created mixed를 놓칠 수 있음 | B12a non-overlap, B12b same-span, B12c co-created mixed와 exact final digest oracle을 추가 |
| execution | provider leader가 먼저 죽은 same-session descendant 및 launch 전 crash의 closure가 없음 | boot+session+birth identity와 member별 재검증 drain을 추가; drain 불가 same-boot는 phase blocker, gate 전 crash는 semantic 0+verified-gone일 때만 prelaunch terminal |
| execution | hook이 terminal row 자체를 없애면 invalidate가 가리킬 원 terminal이 없음 | intended terminal 존재 시 invalidate, 누락·변조 시 trusted prefix+intended terminal의 별도 `commit-recovery` 전이로 분기 |
| execution | prelaunch same-source resolution digest가 reason별 schema로 닫히지 않음 | reason별 canonical resolution record와 typed digest, snapshot generation/equality proof, 고정 retry budget, config 변경 규칙을 schema oneOf로 고정 |
| 비례성 | 안전 보강이 새 시스템·자산으로 늘어날 위험 | 기존 5개 자산과 한 stdlib runner 안에서만 상태기를 보강하고 자동 mutation journal/rollback을 제거해 제품 정책을 더 단순화 |

### 9.13 22차 closure 재검 기준

1. **spec trace:** accepted-base/final-diff와 owner correction이 shared workspace에서 승인·사용자 bytes를 지우지
   않으면서 scaffold/unapproved test delta 0을 실제로 강제하는가; 폐쇄 lifecycle enum이 전 경로에서 같은가
2. **overfit/effectiveness:** B12a/b/c·P16과 semantic-bytes terminal 분리가 blanket delete/preserve나
   의미 없는 source 변경 없이 합법 negative/positive를 가르는가
3. **execution/corpus:** session drain/prelaunch blocker, canonical resolution retry, terminal hook
   commit-recovery가 모든 성공·실패 이력을 보존하며 5개 자산·표준 Git 범위에서 실행 가능한가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.14 22차 동결 리뷰

- SHA-256: `8e584e0d13747eb433422ba4febc6e0d5b189cba935d9fb1fd2a30cd8b387780`
- 1,117행, code fence 18
- spec trace: NO-GO, Blocker 1 / Important 1 / Nit 1
- overfit/effectiveness: NO-GO, Important 2 / Nit 1
- merge/execution: NO-GO, Blocker 3 / Important 1

### 9.15 22차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec | owner가 correction base를 읽은 뒤 사용자 same-path 편집을 whole-file write로 잃을 수 있음 | G1 exact-path single-writer 승인, proposal-only owner, apply 직전 base/current SHA mismatch write 0, conflict 사용자 3-way 선택, post/G2 digest 재검과 B12d 추가 |
| spec | 축소한 lifecycle의 `local refactor`·`retire`가 상태표에 잔존 | 상태표에서도 제거해 move/split/rename/consolidate와 delete/weaken만 전 경로에 유지 |
| spec | P16의 `byte-preserve/pending` oracle이 decision/file effect를 혼합 | decision/lifecycle/execution/scaffold/file-effect 축을 exact literal로 분리 |
| effectiveness | 무관 source/공백 변경으로 semantic 실패 이력을 우회할 수 있음 | 실패 key의 실제 model-visible bundle/prompt change+hunk+prior terminal+독립 승인 record를 요구하고 campaign semantic correction을 최대 2 round로 고정 |
| effectiveness | negative 3회, positive 1회라 과잉 제거 회귀 검출이 비대칭 | 모든 B/P/negative·positive·lifecycle holdout을 양 runtime 3회로 통일하고 전 repetition을 reducer에 포함 |
| effectiveness | 5개 파일 제한이 거대한 단일 runner를 막지 못함 | 500 nonblank/non-comment LOC 또는 여섯 번째 책임에서 Task 0 중단, LOC·책임표와 scope 축소의 명시적 사용자 재승인을 완료 기준에 추가 |
| execution | birth/SID check 뒤 numeric kill 사이 PID reuse TOCTOU | numeric signal을 금지하고 pidfd/job object/동등한 stable process handle로만 signal; capability 없으면 phase plan 전 blocked |
| execution | launch marker 전 crash를 복구할 durable supervisor identity와 parent-dir fsync가 없음 | phase supervisor-ready를 provider/session 전에 durable publish하고 plan에 결속; per-invocation launch-prepared 2단 gate, phase/attempt parent fsync 추가 |
| execution | hook recovery가 multi-row terminal batch 일부 변조·extra를 닫지 못함 | count+ordered row digests+whole batch digest를 precommit 봉인하고 byte 차이 하나라도 whole-batch recovery; exact batch일 때만 invalidate |
| execution | zero-output signal/OOM/adapter/resource exit reason과 retry가 열려 있음 | 18개 exact reason enum과 transient/config/adapter/signal/resource별 resolution·retry policy를 폐쇄; 표 밖 reason은 campaign blocker |

### 9.16 23차 closure 재검 기준

1. **spec trace:** exact-path single-writer+proposal/base SHA/write-0 conflict가 실제 역할 권한과 handoff 안에서
   동시 사용자·승인·pre-existing bytes를 보존하고, lifecycle/P16 literal이 전 경로에서 같은가
2. **overfit/effectiveness:** semantic correction record·2-round cap·전 positive/negative 3회가 digest churn과
   optional stopping을 막으면서 합법 계약을 같은 강도로 보존하는가; runner 범위 gate가 실질적인가
3. **execution/corpus:** stable handle, supervisor-ready/launch-prepared/parent fsync, whole-batch recovery,
   zero-output exact enum이 crash·PID reuse·hook partial mutation을 5개 자산 안에서 닫는가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.17 23차 동결 리뷰

- SHA-256: `9ae49388ff39d43c4fcac482211474abbf53a6fc1e0ab37b0142494f61bbf5c9`
- 1,217행, code fence 18
- spec trace: NO-GO, Blocker 1
- overfit/effectiveness: NO-GO, Important 1
- merge/execution: NO-GO, Blocker 2 / Important 1

### 9.18 23차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec | proposal-only correction을 실제 Claude/Codex capability가 강제하지 않음 | 존재하지 않는 read-only dispatch 주장을 제거; G1 exact-path single-writer를 명시적으로 승인받고 기존 owner가 순차 direct correction, Coordinator pre/post SHA 독립 감사로 단순화 |
| effectiveness | case rename·rep 4–6·새 campaign ID로 same-source reducer와 2-round budget 우회 | case ID가 아닌 immutable logical-case hash, exact slot `{1,2,3}`, 별도 attempt ordinal, campaign lineage root/counter 상속, first-call 이후 case immutability와 typed holdout register 추가 |
| execution | launcher spawn 뒤 launch-prepared 전 crash에 durable containment identity가 없음 | Linux systemd/cgroup v2 phase unit을 provider보다 먼저 만들고 invocation launch-intent도 spawn 전 봉인; prepared 전 crash도 exact unit InvocationID membership 0으로 닫음 |
| execution | 정상 완료 시 장수 phase supervisor shutdown/reap 증거가 없음 | terminal set 뒤 new invocation 차단→drain→shutdown→unit inactive/membership 0→`phase-supervisor-closed`를 review closure/PASS에 결속 |
| execution | Darwin host에는 계획의 identity-bound signal backend가 없어 양 runtime 완료 경로가 없음 | user-approved Linux systemd/cgroup v2 executor와 두 CLI를 Task 0 prerequisite로 고정; Darwin 대체·자동 provisioning 금지, installed capability self-check 필수 |

### 9.19 24차 closure 재검 기준

1. **spec trace:** proposal-only 허구 없이 exact-path single-writer 승인과 실제 owner direct correction/pre-post
   digest가 B12a–d/P16 및 shared workspace 보존 규칙을 실행 가능하게 닫는가
2. **overfit/effectiveness:** immutable logical case, slot 1–3, attempt ordinal, lineage root/counter, append-only
   holdout registry가 label/slot/campaign churn을 막고 semantic correction 2-round를 우회하지 못하게 하는가
3. **execution/corpus:** Linux systemd/cgroup v2 phase unit의 pre-spawn intent, InvocationID, normal
   phase-supervisor-closed와 whole-batch/terminal schema가 crash·정상 종료 모두에서 실행 가능한가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.20 24차 동결 리뷰

- SHA-256: `78d4e5fe85737844b53368231f5ec6b9fa6246b40bc37801a9bb12e07ef0a908`
- 1,302행, code fence 18
- spec trace: NO-GO, Blocker 1
- overfit/effectiveness: NO-GO, Important 2 / Nit 1
- merge/execution: NO-GO, Blocker 3

### 9.21 24차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec | digest-only owner correction으로 dirty/untracked preimage, exact 3-way와 hunk 감사를 재구성할 수 없음 | 승인 exact path의 repo-external byte preimage를 감사 전용으로 보존하고 correction result를 `applied-contextual|checkpoint-drift|conflict-awaiting-user`로 폐쇄; conflict는 owner write 0→Coordinator 사용자 선택→fresh checkpoint→same-owner direct apply |
| effectiveness | 첫 provider 결과 뒤 runner/schema를 바꾸면 holdout oracle을 관찰한 evaluator drift가 가능 | ledger/attempt/closure에 evaluation-harness digest를 결속하고 current lineage 첫 호출 뒤 runner/schema/scoring을 동결; 수정은 campaign NO-GO+사용자 승인 superseding root+전체 재실행만 허용 |
| effectiveness | unknown/complete-invalid 뒤 source를 바꾸는 경로가 semantic 2-round budget과 분리됨 | 두 subtype은 semantic correction 근거가 아니므로 current campaign NO-GO·추가 호출 0; 독립 infra 결함 승인 뒤 superseding root full rerun만 허용 |
| effectiveness/execution | dynamic holdout의 task/fixture/oracle bytes를 5개 자산 안에 영구 저장할 경로가 없음 | `cases.jsonl` 기존 prefix immutable+holdout line append-only, `{cases.jsonl,evidence.jsonl}` holdout-register commit과 multi-file seal 추가 |
| execution | supervisor 자체 crash와 정상 exit→closed marker 사이 crash를 자기 작성 marker/direct-child wait로 닫을 수 없음 | manager-owned transient service로 topology 고정; close-intent→exit-ready→retained manager result→exit-observed→release/inactive→idempotent closed, 비정상은 recovery-authored crash-closed로 실패 phase만 종료 |
| execution | intended-batch seal이 plan/terminal에만 있어 header/recovery/invalidate/closure hook mutation을 놓침 | 모든 evidence commit kind에 generic seal과 ordered event vector/staged blob을 적용; whole-batch recovery 및 recovered closure 뒤 fresh closure를 강제 |

### 9.22 25차 closure 재검 기준

1. **spec trace:** actual owner 권한 안에서 tagged conflict/write-0→Coordinator 사용자 선택→same-owner apply와
   repo-external preimage 감사가 B12a–d/P16의 사용자·승인 bytes를 자동 restore 없이 보존하는가
2. **overfit/effectiveness:** append-only holdout register, frozen evaluation harness, selection-risk NO-GO와
   superseding-root full rerun이 evaluator/case/source churn을 닫으면서 positive·lifecycle을 과잉 제거하지 않는가
3. **execution/corpus:** manager-owned service의 retained result/exit-observed 정상·crash closure와 모든 event
   commit의 generic multi-file seal/recovery가 crash·hook 변조 뒤에도 5개 자산 안에서 실행 가능한가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.23 25차 동결 리뷰

- SHA-256: `537096de2e8a5f7ffeb640191dd68bb7e918e89daa9bf911e71676c03423506c`
- 1,426행, code fence 20
- spec trace: NO-GO, Important 1 / Nit 1
- overfit/effectiveness: GO
- merge/execution: NO-GO, Blocker 3

### 9.24 25차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec/execution | superseding correction이 generic commit enum/path matrix에 없고 defective case를 immutable prefix 안에서 고칠 수 없음 | provider 전·후 correction을 단일 `lineage-correction` kind로 통합; unique active header chain, old→new case-register/tombstone+replacement append, exact staged paths와 full rerun을 결속 |
| spec | audit snapshot이 G2 이전 abort/rebaseline에서 stale·잔존할 수 있음 | accepted manifest/G1 digest-bound generation을 만들고 G2 승인·중단·window 종료·재기준선 terminal에서 폐기; rebaseline은 fresh generation만 사용 |
| execution | active/wedged service는 terminal result가 stop 뒤 생기는데 result-first crash closure가 stop을 막음 | result가 있으면 observe-first, active면 durable phase-stop-intent-first→exact stop→result/inactive/membership0→forced-stop observed→crash-closed로 분기 |
| execution | evidence-changing correction commit이 generic seal enum에서 누락 | `lineage-correction`을 closed commit kind·ordered vector·stage/self-check 전 경로에 추가 |
| execution | multi-file working replace 전 seal 순서와 no-commit crash recovery가 없음 | full results 계산→seal/parent fsync→path별 atomic replace→worktree-published→stage/commit 순서; precommit/no-commit oneOf와 idempotent whole-result recovery 추가 |

### 9.25 26차 closure 재검 기준

1. **spec trace:** unique active lineage leaf와 versioned case supersede, generation-bound audit snapshot lifecycle,
   tagged owner correction이 실제 역할·G1/G2·path matrix에서 모순 없이 닫히는가
2. **overfit/effectiveness:** correction header가 prior failure/counter를 상속하고 defective case/harness를
   관찰 후 조용히 교체하거나 positive/lifecycle을 누락할 수 없는가
3. **execution/corpus:** active/wedged stop-intent-first closure와 full-result→pre-write seal→multi-file publish→
   no-commit recovery가 모든 crash 경계에서 진행 가능하며 generic commit enum/stage set이 같은가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.26 26차 동결 리뷰

- SHA-256: `188e4bd987ab428fafb4bd9ae15f68fa363eac6aab055d29f39d93649d3264e1`
- 1,512행, code fence 20
- spec trace: NO-GO, Important 1
- overfit/effectiveness: GO
- merge/execution: NO-GO, Blocker 2

### 9.27 26차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec | post-call harness-only correction이 같은 candidate/key의 prior semantic-output-fail을 영원히 unresolved로 남김 | `harness-defect-resolution` tagged branch를 추가하고 prior terminal/key·old/new harness·exact hunk·독립 승인·old-answer old-fail/new-pass re-score·inherited counter·전체 active matrix rerun을 모두 만족한 뒤에만 resolved; raw/re-score 불성립은 permanent NO-GO |
| execution | 정상 closure tuple이 없는 terminal-success와 remaining-member terminal-non-success가 crash-closed까지 닫히지 않음 | manager result 성공/실패와 무관한 abnormal-terminal branch, missing tuple 결속, 필요 시 stop-intent-first, inactive/membership 0→abnormal observed→공통 crash-closed suffix와 세 crash fixture 추가 |
| execution | no-commit recovery가 Green source+terminal 원자 commit을 evidence-only recovery로 바꾸고 partial index/commit-success-before-observation을 판별하지 못함 | seal에 base/parent/prior·intended index/path blob/message trailer를 결속; exact no-commit은 원래 kind/stage set을 recovery row 없이 resume, exact committed child는 인정, hook-mutated 또는 source-resume-impossible만 source-0 recovery+invalidate/prelaunch로 분기 |

### 9.28 27차 closure 재검 기준

1. **spec trace:** harness correction이 old output을 보고 evaluator를 튜닝하는 우회로가 아니라 exact
   old-fail/new-pass re-score, inherited budget, unique lineage와 full active-registry rerun으로만 prior semantic
   selection-risk를 해소하며 기존 source-correction/infra-resolution과 tagged union으로 분리되는가
2. **overfit/effectiveness:** permanent NO-GO 실패 경계와 positive·lifecycle 3-slot 보존이 유지되고, 새 recovery와
   supervisor 분기가 특정 Broccoli fixture 이름이 아닌 semantic-output/manager/index 상태에 일반화되는가
3. **execution/corpus:** terminal-success/missing-close와 remaining-member terminal, exact/partial index,
   green-source precommit, commit-success-before-observation, hook mutation이 각각 closed branch를 가지며 원래
   commit atomicity·사용자 index/source·bootstrap/lineage/holdout/closure 의미를 보존하는가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.29 27차 동결 리뷰

- SHA-256: `f67f0061847379476a03edcc4187b2a3bde9563f8d784c663db61e0933d6cd5f`
- 1,623행, code fence 20
- spec trace: GO
- overfit/effectiveness: GO
- merge/execution: NO-GO, Blocker 3

### 9.30 27차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| execution | terminal+membership0이 failed/retained manager state에 남고 inactive 전이 전에 result가 소실될 수 있음 | actual result/missing tuple의 terminal-observed를 선행 봉인; membership과 별개로 manager state가 남으면 identity-bound stop/release/reset intent·전이, inactive/membership0 뒤 observed→crash-closed |
| execution | prior/result partial index가 crash 산출인지 사용자의 의도적 unstage인지 byte로 구별 불가 | seal 전 pressure-commit-window 승인, crash 시 window 종료; current HEAD/index/working/stage set을 결속한 fresh `resume-original` 사용자 승인 전에는 prior/result도 write/stage 0 |
| execution | hook의 source·비봉인 path가 bootstrap/lineage/holdout/closure 등에서 유효화되거나 message-only accept/recovery가 겹침 | direct child를 unexpected-path/content-exact/sealed-content-drift/ambiguous ordered oneOf로 분리; commit-kind별 fresh bootstrap·leaf/register 차단·prelaunch·invalidate·new attempt·merge blocker 전이와 unrelated path 자동 rollback 0을 추가 |

### 9.31 28차 closure 재검 기준

1. **spec trace:** pressure recovery 승인과 hook failure table이 중앙 admission·역할 권한·사용자 변경 보존 규칙을
   침범하지 않고 live contract의 commit enum/stage/reducer/completion에 같은 의미로 반영되는가
2. **overfit/effectiveness:** crash 뒤 사용자 unstage를 failed state로 사칭하거나 hook source를 새 candidate로
   조용히 채택할 수 없고, fresh baseline/holdout/full matrix가 실제 positive·lifecycle 보존을 유지하는가
3. **execution/corpus:** membership0/manager-failed result-first closure, fresh resume approval, ordered hook oneOf와
   bootstrap부터 recovery까지 commit-kind별 전이가 사용자 index/source를 덮지 않으면서 모든 branch를
   PASS·NO-GO·blocker 중 정확히 하나로 닫는가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.32 28차 동결 리뷰

- SHA-256: `4784d90681abf1d97994e163f8bdfbf42ecd600803c11c0a95f399d1bab17c75`
- 1,715행, code fence 20
- spec trace: NO-GO, Important 1
- overfit/effectiveness: NO-GO, Important 1 / Nit 1
- merge/execution: NO-GO, Blocker 3

### 9.33 28차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| execution | hook이 sealed blob을 base로 돌린 strict-subset changed set이 귀속 가능한 batch-missing인데 ambiguous blocker로 감 | unexpected-path 우선 뒤 exact trailer·no outside·`changed_set ⊆ sealed_set`·not-content-exact를 sealed drift로 정의하고 strict subset을 batch-missing recovery로 연결; repair successor는 즉시 blocker |
| spec/execution | sealed/extra hook source를 holdout/invalidate/closure 등에서 exact-byte 사용자 승인 없이 새 candidate로 채택하고 holdout trusted prefix가 복구되지 않음 | 모든 kind/두 drift branch 공통 `source_resolution` oneOf와 expected/actual/repaired manifest-bound 승인 gate 추가; whole-batch recovery 뒤에만 kind별 rebaseline/prelaunch/invalidate/new attempt, 거절·부재는 preserve-and-block |
| effectiveness | failed holdout-register의 이미 봉인된 case를 버리고 새 holdout만 골라 optional case churn 가능 | intended old case를 인증하면 `preserve-exposed-holdout`으로 active-development에 보존하고 새 independent holdout과 두 hash를 registry/header/closure/full matrix에 함께 결속; 인증 불가는 replacement 0 blocker |
| execution | repair root가 recovery/invalidate에만 있고 replacement holdout/plan/terminal은 새 chain을 열 수 있음 | final repair closure까지 lineage/holdout-register/plan/terminal/recovery/invalidate/prelaunch/closure 모든 causal seal과 source/case row에 같은 root 전파; action oneOf 전 검사하고 두 번째 mutation은 새 root 0 blocker |
| effectiveness | 정상 plan/terminal/closure마다 별도 user window 승인을 반복 | exact path 합집합의 phase-scoped 승인 1회와 per-seal subset/generation으로 축소; crash·control return·digest drift 때만 fresh resume 승인 |

### 9.34 29차 closure 재검 기준

1. **spec trace:** hook source의 세 사용자 선택이 모든 commit kind와 sealed/extra drift에 공통 적용되고,
   preserved exposed holdout·source choice·repair root가 schema/registry/closure에서 누락 없이 같은가
2. **overfit/effectiveness:** old holdout을 adaptive discard하거나 hook source를 silent adopt할 수 없고,
   phase-scoped window가 정상 실행 마찰을 낮추면서 crash 뒤 사용자 unstage 보존은 약화하지 않는가
3. **execution/corpus:** strict-subset batch-missing, trusted-prefix holdout recovery, causal successor root propagation과
   kind별 rebaseline/invalidate/new-attempt가 정확히 하나의 진행·NO-GO·blocker branch로 실행 가능한가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.35 29차 동결 리뷰

- SHA-256: `ddce6e42cb98a0559a6c51882e84bf2698f5cf52082c6496745ebfe444eb35d6`
- 1,795행, code fence 20
- spec trace: NO-GO, Important 1
- overfit/effectiveness: GO
- merge/execution: NO-GO, Blocker 2 / Important 2

### 9.36 29차 finding의 처리

| 검토 축 | finding | 처리 |
|---|---|---|
| spec/execution | `preserve-exposed-holdout`은 unchanged cases를 요구해 정상 register에 못 들어가고 generic recovery 식에도 허용되지 않아 기록 경로가 없음 | failed holdout-register 전용 recovery vector를 `trusted prefix + intended batch + recovery row + preserve row`로 닫고, preserve row는 recovered append/recovery digest와 unchanged cases를 결속; cases stage는 실제 blob 복원이 필요할 때만 포함하고 새 independent holdout은 다음 정상 register에서 append |
| execution | `repair-complete`가 repair commit의 ancestry·exact path/tree·현재 HEAD/source와 결속되지 않고 event/commit 위치도 없음 | tracked `source-resolution` event와 evidence-only commit kind를 추가; recovery R→승인 source-only repair U→repair-complete S의 direct first-parent, U exact path/tree/manifest, S 시점 HEAD/source equality를 schema·seal·stage table에 결속 |
| execution | 모든 kind의 공통 source choice가 fresh bootstrap 및 재귀 recovery 금지와 충돌 | failed kind discriminator tagged union으로 분리; ordinary kind만 3-choice, bootstrap은 clean-base/repair/fresh-bootstrap 전용, commit-recovery/source-resolution mutation은 choice field 없이 즉시 blocker |
| execution | hook oneOf가 ordered reducer로는 동작하지만 core-changed commit이 drift와 ambiguous schema를 동시에 만족 | 앞 세 branch 모두 exact core/trailer를 요구하고 ambiguous를 앞 세 predicate의 순수 complement로 정의 |
| spec/execution | terminal fail 통합 행이 unknown/complete-invalid에도 source choice만으로 새 attempt를 허용 | terminal subtype 행을 분리; unknown/complete-invalid는 invalidate/source choice 뒤에도 provider 0이고 기존 infra-defect superseding root·전체 registry rerun만 후속 attempt를 허용. invalidate/closure도 underlying subtype reducer를 상속 |

### 9.37 30차 closure 재검 기준

1. **spec trace:** exposed holdout의 append→recovery→preserve→fresh holdout 순서가 exact event vector·conditional
   stage set·registry/header/closure에서 실행 가능하고, 중앙 admission·역할·mirror 범위는 바뀌지 않았는가
2. **overfit/effectiveness:** failed holdout adaptive discard와 silent source adoption은 계속 막으면서 bootstrap/
   recovery를 ordinary choice에 억지로 끼우거나 unknown output을 골라 재실행하는 우회가 없는가
3. **execution/corpus:** disjoint hook predicate, kind-specific choice, R→U→S ancestry와 terminal subtype reducer가
   schema/event/commit enum/stage set/self-check/completion에 같은 의미로 닫히며 각 branch가 정확히 하나의
   진행·NO-GO·blocker 결과를 갖는가

동일 hash에서 세 리뷰 모두 Blocker/Important 0, GO일 때만 closure를 완료한다.

### 9.38 30차 동결 리뷰 결과

- 리뷰 대상 SHA-256: `f644d25ef3c03e4ec2eac2e13c50cc9699fc9018fc4cb4eb217bc852a54de1b0`
- 1,872행, code fence 20
- spec trace: GO, Blocker 0 / Important 0 / Nit 0
- overfit/effectiveness: GO, Blocker 0 / Important 0 / Nit 0
- merge/execution: GO, Blocker 0 / Important 0 / Nit 0
- corpus mirror 11/11, checker 19개, plugin/corpus/eval 변경 0, diff check clean

이 결과와 상태 헤더를 기록한 변경은 live 실행 계약을 바꾸지 않는 메타데이터다. 기록본 자체의 exact hash는
세 reviewer가 read-only로 재확인하고, 자기 참조식 hash 변경을 피하기 위해 그 확인 결과는 최종 handoff에 남긴다.
