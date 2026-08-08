# 의미 있는 영구 테스트 생성 정책 수정 계획

- 최초 작성: 2026-08-05
- 실행 교정: 2026-08-08
- 상태: 구현 기준선
- 근거: [Broccoli Server 불필요 테스트 전수 감사](../design/2026-08-05-broccoli-server-unnecessary-test-audit.md)

## 1. 목표

dddjango가 TDD를 수행하더라도 제품 계약을 보호하지 않는 영구 테스트를 새로 만들지 않게 한다.
테스트 수를 줄이는 것이 목표가 아니라, 새 테스트마다 다음 질문에 먼저 답하게 하는 것이 목표다.

1. 현재 승인된 어떤 제품 계약을 보호하는가?
2. 이 테스트만 잡는 구체적인 production failure는 무엇인가?
3. 기존 테스트가 이미 같은 계약과 failure를 보호하지 않는가?
4. 구현을 바꿔도 유지할 안정적인 public boundary의 oracle인가?

네 질문을 통과하지 못하면 테스트를 만들지 않는다. 단, 현재 도메인 불변식·application 정책·DB
보장·공개 wire/consumer 계약을 독자적으로 보호하는 테스트는 그대로 유지하거나 추가한다.

## 2. 확인된 원인

| 구분 | 원인 | 수정 |
|---|---|---|
| 왜 작성했는가 | Architect가 framework mechanics·private 구조·테스트 seam을 승인된 테스트 계약으로 승격 | 영구 테스트 입장 심사를 설계 앞단에 둔다 |
| 왜 작성했는가 | Coordinator가 모든 신규·변경 내부 의무를 unit Red로 자동 변환 | 입장 심사를 통과한 test decision만 Red로 dispatch한다 |
| 왜 작성했는가 | 피라미드·이중 루프·예제가 테스트 수량 압력으로 작동 | 작성 recipe와 테스트 필요성 결정을 분리한다 |
| 왜 막지 못했는가 | G1에 새 테스트의 필요성과 중복 여부가 직접 보이지 않음 | G1에 test decision table을 직접 표시한다 |
| 왜 막지 못했는가 | 일반적인 white-box·중복 금지가 구체 설계 명세보다 약함 | Architect·Coordinator·작성 역할·Reviewer가 같은 중앙 decision을 소비한다 |
| 왜 막지 못했는가 | 첫 Green 뒤 Red 전용 loader·dynamic import·availability 비계 정리 소유자가 없음 | 비계를 만든 역할이 첫 Green 직후 제거한다 |
| 왜 막지 못했는가 | checker와 전체 green은 의미를 판정하지 못함 | 의미 판정은 reviewer가 test diff와 decision을 대조한다 |

## 3. 중앙 영구 테스트 입장 규칙

### 3.1 허용되는 보호 대상

새로 만들거나 의미 있게 강화하는 영구 테스트는 최소 하나를 보호해야 한다.

- 외부 HTTP·이벤트·영속 wire·사용자 관찰 상태·보안/규제 계약
- application orchestration의 원자성·부수효과 순서·중복 방지·실패 처리
- framework와 무관한 도메인 불변식·상태 전이·판정 경계
- 현재 DB constraint·transaction·rollback·race·멱등성·repository round-trip
- boundary adapter의 변환·정규화·fallback·known failure 번역
- 승인 근거나 실제 consumer가 확인된 공개 Python 계약

다음은 그 자체로 영구 테스트 자격이 아니다.

- Python·Django·Pydantic·Django Ninja의 기본 동작
- validator 배치, ValidationError 위치, private helper, module 배치, source AST/import 형태
- production docstring, slots, monkeypatch seam, nominal inheritance만 확인하는 assertion
- 테스트 도구 호환을 위해 만든 production 의미
- import 가능 여부나 loader 성공만 확인하는 availability test
- coverage·피라미드 비율·디버깅 편의만을 이유로 한 테스트 복제
- migration 파일·함수·과거 state·적용 순서 자체를 oracle로 삼는 테스트
- .dddjango 문서를 읽거나 파싱해 통과하는 제품 pytest

### 3.2 최소 decision table

Architect는 새 테스트를 직접 의무화하기 전에 다음 표를 작성한다.

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|

decision은 다음 중 하나다.

- `add`: 새 영구 테스트가 필요하다.
- `update`: 승인된 계약 변경에 맞춰 기존 테스트의 의미를 바꾼다.
- `reuse`: 기존 테스트가 이미 보호하므로 새 테스트를 만들지 않는다.
- `retain`: 관련 기존 테스트의 현재 계약을 그대로 유지한다.
- `remove`: 계약 종료 근거에 따라 지정된 기존 assertion/test만 제거한다.
- `reject`: framework/private/test-tool/no-authoritative-contract 등 비자격 후보다.
- `pending`: 근거·계약·중복 여부가 불명확해 사용자 또는 설계 결정이 필요하다.

`pending`은 G1/G1′을 막는다. `reuse`와 `reject`는 새 test file/case/assertion/helper를 만들지 않는다.
`remove`는 새 명세의 침묵이나 현재 구현과의 불일치만으로 선택할 수 없다.

### 3.3 중복 판정

- 같은 계약·boundary·failure mechanism의 후보가 기존 권위 테스트에 포함되면 `reuse`다.
- domain 판정, application orchestration, DB race/constraint, adapter 변환, HTTP 직렬화처럼 실패
  mechanism이 다르면 여러 층의 테스트가 각각 유효할 수 있다.
- 상위 테스트에서 버그를 발견했다는 이유만으로 같은 failure를 unit test로 복제하지 않는다.
- 테스트 하나를 여러 개로 나누는 것은 가독성 recipe일 뿐 새 case의 근거가 아니다.
- 기존 테스트가 중복이라는 판단만으로 자동 삭제하지 않는다. 계약 종료 또는 의미 보존 통합 결정이 필요하다.

### 3.4 Red 전용 비계

임시 `find_spec`, dynamic import guard, 대체 decorator, skip/xfail, loader helper가 정말 필요하면
작성 역할이 임시임을 명시한다. 그 역할은 해당 surface의 첫 Green 직후 이를 제거하고 정상 import와
실제 행동 assertion만 남긴다. 작업 전부터 있던 비계를 이번 실행이 만들었다고 간주해 임의 삭제하지 않는다.

## 4. 파이프라인 배선

### Phase 1

- `discipline-tdd`가 영구 테스트 입장 규칙의 단일 소유자다.
- Architecture/implementation knowledge의 테스트 예시는 candidate signal 또는 입장 승인 뒤 작성
  recipe일 뿐 독립 의무가 아니다.
- Architect가 최소 decision table을 작성한다.
- API/DB reviewer는 자기 렌즈의 candidate와 위험을 제안할 수 있지만 decision 없이 테스트를 의무화하지 않는다. 도메인 candidate는 architect가 표에 넣고 필수 discipline reviewer가 입장 근거·중복을 독립 감사한다.
- Discipline reviewer가 G1 직전 protected contract, unique failure, 중복, framework/private 오라클을
  독립 감사한다.
- Coordinator는 G1에 `add/update/reuse/retain/remove/reject/pending`을 직접 보여 준다.

### Phase 2

- Coordinator는 `add/update`만 새·변경 Red로 dispatch한다.
- `reuse`는 기존 테스트를 검증 anchor로 사용하고 새 테스트를 만들지 않는다.
- `retain`은 현재 테스트를 건드리지 않는다.
- `remove`는 승인된 exact 대상만 기존 owner에게 보낸다.
- `reject`는 test 역할에 보내지 않고 code/type/checker/reviewer 등 적절한 검증으로 돌린다.
- Acceptance tester는 승인된 외부 계약 decision만 소유한다.
- Coder는 승인된 domain/application/DB/adapter decision만 소유한다.
- 모든 내부 구현 의무를 unit Red로 자동 변환하는 현재 Coordinator 규칙을 제거한다.
- 첫 Green 뒤 비계를 만든 역할을 다시 호출해 스스로 제거하게 한다.
- Phase 2 discipline reviewer는 새·변경 test hunk마다 G1 decision과 독자 failure가 있는지,
  `reuse/reject`에서 새 테스트가 생기지 않았는지, 비계가 남지 않았는지 감사한다.

## 5. 직접 교정할 생성 압력

| carrier | 교정 |
|---|---|
| `discipline-tdd` | 중앙 admission, 중복, lifecycle, 비계 제거를 추가한다 |
| `implementation-test` | 80/15/5를 목표 비율에서 설명 예시로 낮추고, 상위 버그의 unit 복제·자동 split·framework mechanics 직접 테스트를 제거한다 |
| `architecture-ddd/db` | Outbox·Risky Write·event union 검증을 자동 test 의무가 아닌 candidate로 중앙 admission에 보낸다 |
| `implementation-django*` | TransactionTestCase·OpenAPI·Schema·render/helper 예시를 admission 뒤 mechanics recipe로 제한한다 |
| `discipline-houserules` | test 디렉터리는 실제 승인 테스트가 있을 때만 조직하며, 구조 규칙이 test file/case를 만들지 않게 한다 |
| Architect/API/DB reviewer | test criteria를 candidate로 제출하고 decision을 대신하지 않는다 |
| Coordinator | 모든 내부 의무→unit Red 변환을 제거하고 G1 decision별 dispatch로 바꾼다 |
| acceptance/coder | 자기 owner의 `add/update/remove`만 편집하고 `reuse/reject`에서는 test write 0 |
| discipline reviewer | G1 admission과 G2 test diff를 독립 감사한다 |

공통 `ErrorOut` property 목록은 plugin이 고정하지 않는다. 현재 승인 shape의 변경에는 별도 사용자 승인이
필요하지만, 그 사실이 Pydantic 내부 metadata·validator 배치·private hook을 자동으로 제품 pytest로
만드는 근거는 아니다. 공개 Python consumer 또는 HTTP/OpenAPI wire에서 실제로 관찰되는 승인 의미만
입장 심사를 통과시킨다.

## 6. 구현 순서

1. 수정 전 대표 RED를 서브에이전트로 재현한다.
2. 이 계획을 현재 목표에 맞게 교정한다.
3. `workspace/reference/spec.md`과 `discipline-tdd` 중앙 정책을 수정한다.
4. 분산 knowledge carrier의 직접 test mandate를 candidate/recipe로 낮춘다.
5. Architect·reviewer·Coordinator G1을 decision table에 연결한다.
6. Acceptance/coder/Coordinator Phase 2를 decision별 dispatch와 첫 Green 비계 제거에 연결한다.
7. Claude 정본 reference를 먼저 수정하고 `corpus_mirror_sync.py --write`로 workspace/Codex
   reference를 byte-exact 동기화한다.
8. Codex 역할 SKILL을 Claude 역할과 의미 미러로 맞춘다.
9. README·DEVLOG에 사용자 흐름과 변경 이유를 기록한다.
10. 수정 후 같은 대표 case와 독립 holdout을 새 서브에이전트가 다시 판정한다.
11. 별도 서브에이전트가 spec trace, corpus contradiction, overfit/effectiveness를 적대 리뷰한다.

## 7. 행동 검증

별도 provider CLI, Linux, systemd/cgroup, Git write/recovery runner는 만들지 않는다. 이번 정책을
검증하기 위해 두 번째 제품을 만드는 것이며 사용자 목표와 비례하지 않기 때문이다.

수정 전후에 dddjango 스킬을 읽은 서브에이전트가 다음 대표 case를 독립 판정한다.

| case | 기대 |
|---|---|
| mounted HTTP가 이미 허용/거부를 보호하는데 validator 위치·exact loc 테스트가 제안됨 | `reuse/reject`, unit test write 0 |
| 실제 예외 행동은 보호되는데 docstring·slots·자기 타입 검사가 제안됨 | `reject`, 기존 행동 테스트 retain |
| loader import 성공만 보는 Walking Skeleton과 Red import guard | availability test reject, 첫 Green 뒤 guard 제거 |
| 승인된 도메인 불변식의 경계가 아직 보호되지 않음 | coder `add`, 가장 작은 유효 boundary Red |
| DB uniqueness/race가 HTTP 성공/실패와 다른 failure mechanism을 가짐 | coder `add` 가능, DB-backed contract로 설명 |
| 공개 wire Enum literal과 `isinstance(StrEnum, str)`가 함께 제안됨 | literal contract만 admit/reuse, Python mechanics reject |
| .dddjango 문서 경로 존재 여부를 pytest로 검사하려 함 | reject, 문서 추적은 제품 pytest 밖 |

검증 결과는 새 영구 runner/evidence ledger가 아니라 이 작업의 review 기록과 DEVLOG에 요약한다.
비결정성이 실제로 관찰될 때만 같은 case를 반복한다.

## 8. 정적 검증

```bash
python3 workspace/tools/corpus_mirror_sync.py --check --format json
claude plugin validate dddjango --strict
python3 -m json.tool dddjango/.claude-plugin/plugin.json
python3 -m json.tool codex-dddjango/.codex-plugin/plugin.json
python3 -m py_compile dddjango/scripts/check-*.py workspace/tools/corpus_mirror_sync.py
git diff --check
```

추가로 다음을 직접 확인한다.

- reference mirror 11/11
- 기존 checker 수 19 유지
- 새 pressure runner/checker/eval asset 0
- Claude/Codex 역할 의미 parity
- 모든 직접 test mandate가 중앙 admission을 우회하지 않음
- 수정 후 대표 case와 독립 negative/positive/lifecycle holdout 통과
- 독립 리뷰의 Blocker/Important 0

## 9. 비범위

- Broccoli Server의 기존 테스트 삭제·수정
- 기존 19개 checker에 의미 판정 로직 추가
- 새 test-value checker 또는 prompt pressure framework
- Linux executor provisioning
- Claude/Codex CLI process supervision
- provider raw·patch·Git evidence ledger
- 전체 기존 테스트 inventory와 무관 green test 정리

## 10. 완료 기준

1. 새·강화 영구 테스트는 최소 decision table의 `add/update` 없이는 생성되지 않는다.
2. 기존 테스트가 같은 계약·failure를 보호하면 `reuse`이고 새 test artifact가 0이다.
3. framework/private/source/test-tool mechanics는 `reject`되고 test 역할에 dispatch되지 않는다.
4. 유효한 domain/application/DB/adapter/public contract test는 금지되지 않는다.
5. 첫 Green 뒤 이번 실행이 만든 Red 비계가 남지 않는다.
6. G1에서 사용자가 새 테스트, 새로 만들지 않는 후보, 제거, reject, pending을 볼 수 있다.
7. G2 reviewer가 test diff를 decision table과 대조한다.
8. Claude/Codex reference·역할 의미 미러가 일치한다.
9. checker는 19개로 유지하고 새 pressure 자산을 만들지 않는다.
10. 정적 검증과 수정 후 서브에이전트 행동 검증, 독립 적대 리뷰가 모두 통과한다.

## 11. 계획 교정 기록

초기 계획은 Linux systemd/cgroup supervisor, provider process recovery, Git seal/ledger와 수백 회
pressure invocation을 구현 선행조건으로 두었다. 구현 preflight에서 Linux 실행기가 없다는 사실보다
더 근본적으로, 이 인프라는 확인된 생성 원인을 고치지 않으며 “불필요한 테스트를 막기 위해 불필요한
검증 시스템을 만드는” 자기모순임을 확인했다.

사용자는 별도 CLI 대신 dddjango 스킬을 사용하는 서브에이전트 검증이 가능하다고 지적했다. 이에 따라
Linux/provider CLI 요구를 제거하고, 실제 원인인 corpus·역할·Coordinator 수정과 수정 전후 decision/file
effect 비교를 구현 기준으로 삼는다.
