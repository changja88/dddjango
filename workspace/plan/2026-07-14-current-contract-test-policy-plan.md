# 현행 계약 테스트 정책 개정 계획 (3축 적대 리뷰 재검토 반영판 v3)

> 기준선: `dddjango--v1.0.8`과 동일한 롤백 커밋 `4333150`.
> 이 문서는 구현 승인을 받기 위한 계획이다. 승인 당시 변경은 이 계획 파일 1개뿐이었으며 플러그인 구현은 시작하지 않은 상태였다.

## Goal

`dddjango`가 만드는 테스트를 다음 네 규칙으로 한정한다.

1. Django migration 자체를 검증하는 테스트를 새로 만들거나 새 case/assertion으로 확장하지 않는다.
2. 과거에 존재했다는 이유만으로 과거 동작을 보존하는 영구 테스트를 만들거나 유지하지 않는다.
3. 영구 테스트의 오라클은 현재 구현이 아니라 **현재 승인된 요구·설계·지원 계약**이다.
4. 이번 기능의 변경 표면과 관련된 기존 테스트가 현행 계약과 어긋나면, 현행 보장을 보존하면서 갱신·분리·삭제한다.

## 비목표와 안전 경계

- 이 개정은 **테스트 생성·유지 정책**만 바꾼다. migration 파일 생성·수정·배치·검토, 이력 보존, 운영 rollout/backfill 지식과 `makemigrations --check`·`sqlmigrate` 같은 기존 검증 절차는 그대로 둔다.
- migration 전반을 불투명 영역이나 외부 비소유 영역으로 만들지 않는다. migration boundary, snapshot, receipt, write-once artifact, 전역/기능별 lock을 추가하지 않는다.
- 프로젝트 전체 테스트를 전수 inventory하거나 일괄 정리하지 않는다. 전체 suite 실행은 검증이지 편집 권한이 아니다.
- 새 런타임 백스톱이나 파일명/AST 판정 스크립트를 추가하지 않는다. 테스트의 존재 이유와 계약 상태는 의미 판정이라 저오탐 결정 검사로 안전하게 닫을 수 없다.
- 테스트 러너, 테스트 DB 준비 방식, `--no-migrations` 여부를 이 정책 때문에 바꾸지 않는다. 정상 Django 테스트가 DB 준비 중 migration을 내부 실행해도 migration 전용 테스트를 작성한 것이 아니다.
- 배포 버전과 manifest는 정책 구현 커밋에서 임의로 올리지 않는다. 릴리스 요청 시 별도 단계로 처리한다.

## 규범 용어와 우선순위

| 용어 | 판정 |
|---|---|
| **현재 계약** | 이번 사용자 승인 요구와 G1/G1′ 설계, 현재 도메인 불변식, 지원 중인 API/이벤트/영속 데이터 호환성, 유효한 보안·개인정보·규제·명시적 부재 의무 |
| **현재 구현** | 조사 증거일 뿐 오라클이 아니다. 구현이 현재 계약을 어기면 올바른 실패 테스트를 삭제하지 않고 구현을 고친다. |
| **관련 테스트** | 승인된 변경 계약을 직접 단언하거나 변경 코드 경로를 직접 검증하는 테스트. 전체 suite에서 실행·실패했다는 사실만으로 관련 테스트가 되지 않는다. |
| **migration 전용 테스트** | migration 파일·번호·dependency graph·operation·적용 순서·과거 model state·forward/reverse·DDL 자체가 오라클인 테스트. 예: `MigrationExecutor`로 두 migration state를 오가며 검증 |
| **현재 동작 테스트** | 현재 model/ORM/service/API/DB 불변식을 검증하는 테스트. DB-backed이거나 현재 constraint를 검증해도 migration history가 오라클이 아니면 허용 |
| **history-only 테스트** | 유일한 유지 근거가 과거 구현·종료된 계약·버그 번호·“예전에는 이랬다”뿐이고 현재 계약 근거가 없는 테스트 |
| **회귀 테스트** | 과거 버그에서 태어났어도 현재 계약을 계속 검증하면 유효하다. 이름이나 생성 시점은 삭제 근거가 아니다. |
| **특성화 테스트** | non-migration 레거시 구현을 파악하기 위한 임시 probe. migration 전용 테스트 금지를 우회할 수 없으며, 영구 테스트나 G2 완료 증거로 세지 않는다. |
| **pending** | 현재 지원/종료 여부가 불명확한 상태. retain이 아니며, 관련 기대라면 G1/G1′ 결정 전 조정과 G2 완료를 막는다. |

계약 판정의 우선순위는 다음과 같다.

1. 사용자 승인 요구와 G1/G1′의 명시 결정
2. 현재 지원 문서·공개 계약·도메인 불변식·영속 데이터/이벤트·보안/규제 의무
3. 기존 테스트와 현재 구현의 관찰 증거

새 명세의 **침묵은 종료 승인이 아니다**. 관련 표면의 종료는 G1/G1′에 명시되고, 해당 표면에 적용 가능한 지원 소비자·deprecation/Sunset·rollout compatibility·영속 데이터/이벤트 의무가 남지 않았다는 근거가 있어야 한다. 근거가 충돌하거나 불명확하면 `pending`으로 반송한다.

## 테스트 조정 결정표

| 발견한 상황 | 조치 |
|---|---|
| 현재 계약과 기대가 일치 | 유지 |
| 의무는 유지되지만 승인된 입력·결과가 변경 | 해당 assertion/test를 갱신하고 올바른 Red를 확인 |
| 한 테스트에 현행 assertion과 종료 assertion이 혼재 | 현행 보장을 남기도록 분리/부분 갱신; 파일 통째 삭제 금지 |
| 모든 기대가 G1/G1′에서 명시적으로 종료 | 테스트 삭제; 파일이 비면 현행 테스트가 공유하지 않는 전용 dead fixture/helper만 제거 |
| 현재 구현만 계약과 불일치 | 테스트 유지, 구현 수정 |
| 지원/종료 여부가 불명확 | `pending`; 삭제·약화 금지, 한정된 설계 질문으로 반송 |
| 지원 중인 구 API·기존 영속 데이터·이미 발행된 이벤트 | 오래됐어도 현재 계약이므로 유지 |
| 과거 동작 제거, 부재 의무 없음 | 옛 성공 테스트 삭제; 관성적인 404/필드 부재 테스트를 새로 만들지 않음 |
| 과거 동작 제거, 부재/금지가 현재 계약 | 명세가 정한 관찰 경계에 negative test 유지/추가 |
| non-migration 특성화 probe | 현재 계약 확인 전 영구화도 삭제도 하지 않음; 결정 뒤 계약 테스트로 재작성하거나 제거 |

### 기존 migration 전용 테스트의 우선순위

- migration 테스트라는 **분류만으로** 삭제·수정하지 않는다.
- 이번 변경과 관련되고 현재 의무가 남으면 기존 테스트를 그대로 유지·실행하되 새 case/assertion을 추가하지 않는다.
- 모든 기대가 명시적으로 종료됐으면 삭제할 수 있으며 replacement migration test는 만들지 않는다.
- 현재 의무의 승인된 기대가 바뀌었으면 기존 관련 assertion을 제자리 갱신·축소할 수 있다. 새 파일·새 case·새 migration 시나리오·coverage 확장은 금지하며, 이를 요구해야만 검증 가능한 부분은 테스트를 발명하지 않고 검증 공백으로 보고한다.
- 불명확하면 `pending`으로 반송한다. 기존 suite 실패를 skip하거나 `--no-migrations`로 숨기지 않는다.

## 최소 설계 산출물: “테스트 계약 변화”

별도 inventory·manifest·artifact를 만들지 않는다. 기존 `design-spec.md` 안에 이번 변경 범위만 다루는 짧은 절을 둔다.

- **유지**: 변경 표면에서 계속 지켜야 할 현재 계약
- **변경/신규**: 이번 승인으로 바뀌거나 생기는 기대
- **종료**: 더는 지원하지 않는 기대와 support/deprecation/rollout/영속 의무 종료 근거
- **부재/금지**: 없음 자체가 현재 계약인지 여부
- **미확정**: G1에서 결정할 항목; G1 통과 뒤 0개여야 함

순수 구현 버그 수정이면 `테스트 계약 변화 없음` 한 줄이면 충분하다. 테스트 삭제·assertion 약화는 이 절의 명시적 **종료** 항목을 인용할 때만 허용한다. 7열 의무 inventory나 저장소 전체 계약 목록은 만들지 않는다.

## 런타임 흐름과 역할 소유권

### Phase 1

1. `design-architect`가 “테스트 계약 변화” 절을 작성한다.
2. API lens가 활성화됐으면 `design-review-api`가 지원 버전·deprecation/Sunset 종료 근거를 확인한다.
3. DB lens가 활성화됐으면 `design-review-db`가 rollout compatibility·기존 영속 데이터/이벤트 의무 종료 근거를 확인한다.
4. 침묵이나 근거 충돌은 종료로 중재하지 않고 G1 질문으로 올린다.
5. G1/G1′ 승인 배너는 “종료”, “부재/금지”, “미확정”을 직접 나열하고 항목이 없으면 `없음`이라고 표시한다. `미확정`이 남아 있으면 승인 입력을 Phase 2 진입으로 해석하지 않는다.

### Phase 2

1. Coordinator가 승인된 변경 표면의 URL, public symbol/use case, event/model/constraint명과 기존 테스트 구조를 앵커로 **한정 검색**한다. 검색된 관련 테스트 경로를 역할에 전달하며 전체 suite를 discovery 대용으로 쓰지 않는다.
2. `acceptance-tester`는 외부 관찰 계약 assertion을 소유한다. API 통합 테스트도 외부 계약을 단언하면 이 역할 소유다. 관련 테스트를 `retain/update/split/delete/add/pending`으로 조정하고 새·변경 의무는 Red를 확인한다.
3. Coordinator는 새 Red뿐 아니라 승인된 `update/split/delete`와 구현 제거에서도 슬라이스를 만든다. 부재 의무 없는 removal-only 슬라이스에는 가짜 negative Red를 만들지 않는다.
4. `coder`는 내부 불변식·협력·repository assertion을 소유하고 같은 조정을 적용한다. 외부 인수 테스트는 계속 임의 수정하지 않는다.
5. 같은 파일에 두 소유권이 섞였으면 Coordinator가 두 역할을 **순차 호출**하고 다음 역할은 최신 파일을 다시 읽는다. 병렬 편집하지 않는다.
6. `discipline-reviewer`는 승인 명세의 “테스트 계약 변화”, 관련 테스트 조정 목록, 테스트 diff와 실행 결과를 필수 입력으로 받는다. 계약을 새로 결정하지 않고 다음만 감사한다.
   - 신규/확장 migration 전용 테스트가 없는가
   - 삭제·약화가 명시적 종료 근거에 연결됐는가
   - 혼합 테스트의 현재 계약 assertion이 살아남았는가
   - 현재 구현에 맞추려고 올바른 failing test를 삭제하지 않았는가
7. reviewer 지적은 무조건 coder가 아니라 해당 assertion 소유 역할로 반송한다.
8. 관련 테스트와 프로젝트의 기존 전체 suite를 실행한다.
   - 관련 실패: 결정표에 따라 해결하거나 `pending`으로 반송한다.
   - 무관 실패: 편집하지 않고 별도 보고한다. 전체 suite green을 주장할 수는 없지만, 관련 검증 결과와 함께 G2에서 사용자 판단에 명시적으로 제시할 수 있다.

각 작성 역할은 별도 영구 artifact 대신 현재 응답에 `path::test | action | 근거가 된 명세 항목 | 변경 후 현행 보장 위치`를 관련 테스트 단위로 반환한다. 모든 assertion의 장부나 SHA-256 원장은 만들지 않는다.

### 수정 모드

- 같은 한정 검색·테스트 조정·소유자 라우팅·관련+전체 suite 검증을 적용한다.
- 순수 구현 버그 수정이고 `테스트 계약 변화 없음`이면 G1′을 생략할 수 있으며 올바르게 실패하는 기존 테스트를 유지한다. 이 경우 기존 `design-spec.md`를 고치지 않고 Coordinator 호출 문맥 또는 기존 scope 작업본에 `테스트 계약 변화 없음`을 기록한다.
- 지원 종료, expected result 변경, 테스트 삭제·assertion 약화가 하나라도 있으면 G1′을 생략하지 않는다.
- 기존 테스트를 update/split/delete하면 수정 모드에서도 최소 1회 focused discipline review를 실행한다.

## 코퍼스 소유권과 변경 파일 계획

### Task 1 — 제품 정책 정본

**Modify:** `workspace/reference/spec.md`

- [x] 네 정책, 현재 계약 우선순위, 관련 범위, 기존 migration test 우선순위를 짧게 고정한다.
- [x] migration 구현 비소유나 boundary protocol로 확장하지 않는다.

### Task 2 — 보편 테스트·레거시 코퍼스 정합화

**Modify deployment master:**

- `dddjango/skills/discipline-tdd/references/final.md`
- `dddjango/skills/discipline-tdd/SKILL.md`
- `dddjango/skills/discipline-cleancode/references/final.md`
- `dddjango/skills/discipline-cleancode/SKILL.md`
- `dddjango/skills/implementation-test/references/final.md`
- `dddjango/skills/implementation-test/SKILL.md`

**Manually mirror SKILL summaries:**

- `codex-dddjango/skills/discipline-tdd/SKILL.md`
- `codex-dddjango/skills/discipline-cleancode/SKILL.md`
- `codex-dddjango/skills/implementation-test/SKILL.md`

- [x] `discipline-tdd`가 현재 계약 오라클, 유지/분리/삭제, negative test 조건, pending 우선순위를 **단일 소유**한다.
- [x] `discipline-cleancode` §16.5는 non-migration 특성화 테스트를 임시 probe로 한정하고 `discipline-tdd`로 넘긴다.
- [x] `implementation-test`에는 migration 전용 테스트와 허용 DB-backed 현재 행위 테스트의 **기술적 식별 예시와 handoff만** 둔다. 테스트 lifecycle 정책을 중복하지 않는다.
- [x] 기존 `test_full_migration()` 마커 예시는 migration과 무관한 DB 통합 예시로 교체한다.
- [x] final.md는 배포본 수정 후 `corpus_mirror_sync.py --write`로 source·Codex에 전파한다.
- [x] `architecture-api` 하위호환/deprecation, `architecture-db` rollout, `implementation-django` migration 구현 절은 수정하지 않는다.

### Task 3 — 설계 생산자와 역할 배선

**Modify Claude runtime:**

- `dddjango/commands/dddjango.md`
- `dddjango/agents/design-architect.md`
- `dddjango/agents/design-review-api.md`
- `dddjango/agents/design-review-db.md`
- `dddjango/agents/acceptance-tester.md`
- `dddjango/agents/coder.md`
- `dddjango/agents/discipline-reviewer.md`

**Mirror semantically in Codex runtime:**

- `codex-dddjango/skills/dddjango/SKILL.md`
- `codex-dddjango/skills/dddjango-design-architect/SKILL.md`
- `codex-dddjango/skills/dddjango-design-review-api/SKILL.md`
- `codex-dddjango/skills/dddjango-design-review-db/SKILL.md`
- `codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md`
- `codex-dddjango/skills/dddjango-coder/SKILL.md`
- `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`

- [x] `acceptance-tester`에 기존 테스트 갱신·분리·삭제용 `Edit` 권한을 추가하고 블랙박스 구현 비열람 경계는 유지한다.
- [x] Coordinator에 한정 검색, 조정 목록, removal-only 슬라이스, assertion 소유자 반송, 수정 모드 규칙을 배선한다.
- [x] G1/G1′ 승인 배너에 종료·부재/금지·미확정 항목을 직접 펼치고, 미확정이 남은 Phase 2 진입을 막는다.
- [x] reviewer의 필수 입력과 좁은 감사 책임을 반영한다.
- [x] 기존 19개 결정적 백스톱의 수·코드·실행 방식은 바꾸지 않는다.

### Task 4 — 사용자 문서와 결정 기록

**Modify:** `README.md`, `workspace/DEVLOG.md`

- [x] README에는 현재 승인 계약만 테스트하고 migration 자체 테스트를 새로 만들지 않는다는 사용자 관점 요약만 추가한다.
- [x] DEVLOG에는 목표, 좁은 경계, v1.1.1 boundary/lock 재도입 거부, 적대 리뷰 중재와 최종 검증 결과를 기록한다.

### Task 5 — 미러·정적 검증

- [x] `python3 workspace/tools/corpus_mirror_sync.py --write` 1회 후 `--check` → 11/11 in-sync.
- [x] Claude/Codex 공통 SKILL 3쌍과 역할 프롬프트 7쌍의 신규 정책 문단을 의미 대조한다.
- [x] 변경 대상인 implementation-test 3미러 안에서만 옛 migration marker 예시가 0인지 확인한다. 계획·DEVLOG는 검색 대상에서 제외한다.
- [x] `git diff --name-status -- dddjango/scripts codex-dddjango/skills/dddjango/scripts`에서 새·수정 runtime script가 0인지 확인한다.
- [x] `claude plugin validate dddjango --strict` 또는 설치 CLI가 지원하는 동등 strict validation을 실행한다.
- [x] `git diff --check`와 변경 파일 전수 diff review를 통과한다.
- [x] 정적 검증과 기존 19개 백스톱은 의미 정책 준수의 증거라고 과장하지 않는다.

### Task 6 — 최종 역할 프롬프트 행동 검증

새 런타임 하니스나 lock을 만들지 않고, 최종 역할 프롬프트를 독립 subagent에게 실제로 적용해 아래 시나리오의 `판정 근거 | action | owner/handoff | Red 또는 removal-only 근거 | 검증 명령`을 평가한다.

| # | 시나리오 | 기대 행동 |
|---|---|---|
| S1 | 새 migration의 forward/reverse 테스트 요구 | migration 테스트를 만들지 않음. 분리 가능한 현재 app 행위만 app 테스트로 검증하고 migration 안전은 미검증으로 보고 |
| S2 | 승인 계약은 201, 구현과 기존 테스트는 200 | 테스트를 201로 갱신해 Red 확인 후 구현 수정 |
| S3 | endpoint 지원 종료, absence 의무 없음 | 성공 테스트 삭제, 404 테스트 발명 금지, removal-only 슬라이스 생성 |
| S4 | 과거 버그 witness가 현재 불변식을 검증 | 회귀 테스트 유지 |
| S5 | 지원 중 v1 API·기존 row·이미 발행된 이벤트 | 현재 계약으로 유지 |
| S6 | snapshot에 현행 assertion과 종료 assertion 혼재 | 분리/부분 갱신, 현행 계약 보장 위치 보고 |
| S7 | 특성화 probe가 구현 버그를 고정하고 계약 근거 불명 | 삭제/영구화하지 않고 pending으로 G1 반송 |
| S8 | 현재 DB constraint를 정상 model 저장으로 검증 | migration history 테스트가 아니므로 허용 |
| S9 | 기존 migration test의 기대가 명시 종료/현재 동일/현재 변경/불명 | 각각 삭제/변경 없이 유지/기존 assertion만 제자리 갱신·축소/pending; 새 case·시나리오·replacement 추가 금지 |
| S10 | migration 특성화 probe를 임시로 만들자는 제안 | 임시라는 이유로 허용하지 않음 |
| S11 | historical backfill만 검증 가능 | 현재 model 테스트가 대체 증거라고 주장하지 않고 migration 검증 공백 보고 |
| S12 | 전체 suite의 무관 테스트 실패 | 관련 범위로 확장해 수정하지 않고 별도 보고; 전체 green 주장 금지 |
| S13 | 수정 모드의 순수 버그 수정 vs 계약 변경 | 전자는 G1′ 생략+기존 failing test 유지, 후자는 G1′ 필수 |
| S14 | 같은 파일에 API status assertion과 repository 내부 assertion이 있고 reviewer가 API assertion의 잘못된 삭제를 발견 | Coordinator가 최신 파일을 다시 읽게 하며 acceptance-tester→coder 순으로 호출; API 지적은 acceptance-tester에 반송하고 내부 assertion은 coder가 소유 |

합격 기준:

- [x] 독립 실행이 모든 시나리오에서 위 기대와 같은 결정을 내리고 근거를 현재 계약 우선순위에서 찾는다.
- [x] 단순 키워드 복창이 아니라 관련 역할의 실제 output/action/handoff를 평가한다.
- [x] migration 현재 행위 테스트가 migration forward/reverse 안전을 증명한다고 과장하지 않는다.
- [x] 전체 suite 실행이나 green이 테스트 삭제의 단독 근거가 되지 않는다.

### v2 집중 재검토와 v3 폐쇄 확인

같은 3개 reviewer가 v2에서 자신의 1차 지적 해소 여부와 새 회귀만 다시 검토했다.

- 코퍼스 정합성·모순: 1차 지적 5건 모두 해소, 새 발견 0건.
- 과적합·자기모순: blocker 1, nit 1. 기존 migration 테스트의 현재 기대 변경 경로와 종료 근거의 적용 범위를 v3에 반영했다.
- 실효성: blocker 0, important 2, nit 1. G1 직접 노출, 혼합 소유권·반송 S14, G1′ 생략 시 기록 위치를 v3에 반영했다.

재검토 지적은 새 artifact·장부·스크립트 없이 기존 설계 절, 승인 배너, 역할 시나리오만 보강했다. v3 반영 뒤 해당 리뷰어가 수정 구간을 다시 확인했고 과적합 blocker·nit와 실효성 important 2건·nit가 모두 `PASS`로 닫혔다. 잔여 blocker/important/nit는 없다.

## 3축 적대 리뷰 중재 기록

초안 v1에 대해 독립 reviewer 3명이 파일을 수정하지 않고 검토했다.

- 코퍼스 정합성·모순: blocker 1, important 4
- 과적합·자기모순: blocker 2, important 6, nit 2
- 실효성: blocker 5, important 5

### 채택

- Codex 공통 SKILL 3개 수동 미러 누락 보완.
- 관련 테스트 정의와 전체 suite 비확장 규칙.
- 기존 migration test와 history-only 삭제의 우선순위.
- 명세 침묵≠종료, pending의 G2 차단.
- migration characterization 우회 금지.
- acceptance `Edit`, assertion 의미 기반 소유권, 해당 소유자 반송.
- removal-only 슬라이스와 수정 모드 배선.
- API/DB reviewer의 지원·rollout 종료 근거 점검.
- `implementation-test`는 기술 식별만, lifecycle은 `discipline-tdd` 단일 소유.
- 검색 범위를 좁힌 정적 검증과 mixed scenario 확장.

### 축소 채택

- reviewer가 제안한 7열 current-obligation inventory는 기존 `design-spec.md`의 5항목 “테스트 계약 변화” 절로 축소했다. 저장소 전체 inventory와 별도 artifact는 만들지 않는다.
- assertion별 전후 장부·SHA-256 원장·상세 실행 count 강제는 관련 테스트 단위 조정 목록과 기존 runner 결과 보고로 축소했다. 의미 보존에는 필요한 연결을 남기되 v1.1.1식 증거 machinery는 재도입하지 않는다.
- 반복 가능한 개발용 eval harness는 이번 구현의 필수조건으로 두지 않고 독립 subagent forward-test로 검증한다. 실증에서 반복 실패가 확인될 때만 별도 설계한다.

### 기각

- 새 runtime script, migration boundary, opaque path inventory, snapshot, receipt, lock은 목표와 무관하고 병렬 실행을 해치므로 채택하지 않는다.
- 전체 저장소 테스트 의무 inventory와 모든 retain assertion의 장부화는 관련 범위 원칙을 깨고 비용 대비 실효가 낮아 채택하지 않는다.

## 구현 후 적대 리뷰·폐쇄 기록

- 역할 프롬프트 전진 테스트: S1~S14 **14/14 PASS**. Claude/Codex 의미 결정은 같고 플랫폼 도구 표기만 달랐다.
- 1차 구현 리뷰: 코퍼스 정합성 important 1·nit 1, 과적합 important 1·nit 1, 실효성 blocker 1·important 2·nit 1.
- 채택 수정: 외부 결과가 0이어도 내부 의무·관련 테스트로 coder 슬라이스 생성, 수정 모드 G1′ 직접 노출·전체 suite, Phase 1/2 reviewer 모드 분리, 비테스트 구현·설계 지적의 완결 라우팅, README 사용자 관점 축소, DEVLOG 결정 기록, 계획 시점 명시.
- 폐쇄 중 정합성 important 2건(수정 모드 reviewer 모드·필수 입력, Phase 2 비테스트 지적 소유권)을 추가 발견해 반영했다.
- 최종 폐쇄: 코퍼스 정합성·과적합·실효성 모두 **blocker 0 / important 0 / nit 0**.
- 이 검증은 실제 대상 Django 프로젝트의 라이브 실행이 아니라 배포될 최종 역할 프롬프트의 독립 행동 시뮬레이션이다. 정적 검증 통과와 의미 동작 검증을 구분해 해석한다.

## 완료 기준

- migration 전용 테스트 신규/확장 금지와 migration 구현 작업 금지가 혼동되지 않는다.
- 이번 기능과 관련되고 계약 상태가 확정된 history-only 테스트만 제거된다.
- 지원 중인 회귀·호환성·영속 데이터/이벤트 테스트는 보존된다.
- 현재 구현이 틀렸을 때 테스트를 구현에 맞춰 삭제·약화하는 경로가 없다.
- 혼합 테스트의 **현재 계약 보장**이 다른 test/assertion으로 추적된다.
- full/migration/수정 모드 모두 같은 정책을 적용한다.
- Claude/Codex 양 런타임과 source/deployment corpus가 동기화된다.
- 새 runtime script, boundary artifact, snapshot, receipt, lock이 0개다.
- S1~S14 역할 forward-test와 정적 검증을 통과한 뒤에만 구현 완료로 보고한다.
