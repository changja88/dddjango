# Q-6 current-contract 고정 시나리오와 oracle

> **상태**: v6 고정 입력(2026-07-13). 실행 자산 정본은 같은 디렉터리의
> `q6_fixture_builder.py`다. 아래 시나리오는 과거 fixture를 소급 채점하기 위한
> 기록이 아니라, 새 Claude/Codex 평가 런에 같은 순서·같은 답으로 적용하는 사전등록
> oracle이다. 결과를 본 뒤 기대를 바꾸지 않는다.

## 공통 실행 계약

다음 명령으로 비어 있는 출력 디렉터리에 A–G seed를 물질화한다.

```bash
python3 -B workspace/eval/tools/q6_fixture_builder.py /tmp/dddjango-q6-v6
```

생성물은 런타임 입력과 평가자 전용 control plane을 분리한다.

```text
/tmp/dddjango-q6-v6/
├── fixtures/<scenario>/                 # runtime에 보일 수 있는 seed만
└── evaluator-control/
    ├── EVALUATION-MANIFEST.json         # 버전·격리 계약
    └── <scenario>/
        ├── CRIB.json                    # 사용자 원문·게이트 답·runner·환경
        ├── ORACLE.json                  # 기대 inventory·조정표·완료 상태
        └── FIXTURE-MANIFEST.json        # runtime-visible seed의 SHA-256
```

`ORACLE.json`, fixture manifest, 본 문서와 builder source는 평가자만 보며 runtime에 제공하지
않는다. `CRIB.json`에도 기대 조정표나 기대 inventory가 없다. 조정자는 manifest를 검증한 뒤
선택한 `fixtures/<scenario>`만 출력 루트 밖의 격리된 fresh workspace로 복사한다. builder의
`stage_runtime_fixture()`는 runtime 경로가 fixture/control bundle 아래면 거부하고 seed만 복사한다. CRIB의 사용자
입력·게이트 답·runner·환경값만 대화/실행 환경으로 전달한다. 생성된 출력 트리 안에서 runtime을
직접 시작해 `../evaluator-control`을 읽을 수 있게 하면 해당 런은 무효다. Claude와 Codex에는
같은 CRIB 값과 byte-identical fixture를 준다. 이 path guard만으로 같은 host의 절대경로 접근을
막을 수는 없으므로 라이브 평가는 evaluator-control을 runtime process의 mount/readable sandbox
밖에 두고 control 접근이 실패함을 확인해야 한다. 그 격리가 없으면 builder 단위 테스트가
통과해도 라이브 런은 무효다.

라이브 런 전 후보 플러그인의 양 manifest version이 `EVALUATION-MANIFEST.json`과 같아야 하며,
설치/cache된 실제 로드 사본과 후보 worktree의 byte parity를 확인해 기록한다. source와 설치
cache의 version 문자열은 서로 다른 증거이며, 같은 version이어도 byte parity를 대신하지 못한다.
불일치하거나 로드 출처를 증명하지 못한 런은 채점하지 않는다. builder는 seed/control만 만들며 라이브
Claude/Codex 실행이나 채점을 완료했다고 주장하지 않는다.

각 seed에는 영향 테스트와 무관한 project-health sentinel이 하나 있어 targeted
`retain/update/add` 실행과 전체 suite 실행의 command/result/count를 서로 구별할 수 있다.
runtime이 만든 명세·current-obligation inventory·테스트 조정표·두 종류의 실제 실행 기록을
수집한다. builder는 fixture/control generator이지 이 산출물을 채점하는 executor가 아니다.
`ORACLE.json`의 evaluator-only `obligation_id`로 행을 안정적으로 식별하되 runtime 표에 그 열을
요구하지 않는다. status는 exact, evidence path는 경로 정규화 후 비교하고, 나머지 자유서술
열은 블라인드 의미 grader가 필요한 현재 사실의 포함 여부를 판정한다. 문구나 행 순서는 채점하지
않는다.

필수 inventory 열은 다음과 같다.

| surface/version | consumer/support | persisted data/event | deprecation window | security/privacy/regulatory | negative/absence | evidence path | status(retain/end/unknown) |
|---|---|---|---|---|---|---|---|

`unknown`이 남은 채 G1을 통과하거나, "지원 종료"를 "관찰 가능한 부재 보장"으로 대신하면
그 시나리오는 FAIL이다. 기존 테스트·현재 구현·git history는 의무를 찾는 증거이지 단독
권위가 아니다.

## Q6-A — 명시적으로 종료된 의무

**Seed fixture**: evaluator ID `q6-01`. 공개 표면의 요소 X가 존재하고 이를 요구하는 영구 테스트가 있다. 승인 근거에는
지원 consumer 0, persisted data/event 의존 0, 진행 중 deprecation 0, 보안·규제 의무 0이
명시돼 있다. X의 부재를 새 계약으로 보장한다는 요구는 없다.

**verbatim 사용자 변경**: “X의 지원 계약만 종료한다. wire/state에 X가 남아 있어도 허용하며,
X의 부재를 새 계약으로 만들지 않는다.”

**PASS oracle**:

- inventory가 지원 종료와 absence 의무 없음(`negative/absence=none`)을 별도로 기록한다.
- X의 존재를 요구하던 stale test는 `delete`한다.
- X가 없다는 영구 negative test를 임의로 추가하지 않는다.
- 공개 API라면 근거 있는 same-surface break를 허용하고, 존재하지 않는 consumer를 위해 새
  버전·deprecation 절차를 발명하지 않는다.

지원 근거가 없는데 삭제하거나, absence test를 관성적으로 추가하거나, 무조건 새 버전을
발명하면 FAIL이다.

## Q6-B — 지원 중 v1과 변경되는 v2

**Seed fixture**: evaluator ID `q6-02`. v1 consumer와 지원 기간이 현재이고 v1 계약 테스트가 있다. v2도 지원 중이다. v1과 v2 email masking은 모두 현재 개인정보 의무이며 각 surface 테스트가 이를 관찰한다.

**verbatim 사용자 변경**: “v2의 display_name을 `CURRENT: Current Name`으로 변경하되 지원 중인
v1과 v1의 개인정보 마스킹 의무는 유지한다.”

**PASS oracle**:

- v1 계약·개인정보 마스킹 의무와 테스트는 `retain`, v2 영향 테스트는 display name만 `update`하면서 v2 masking assertion도 유지한다.
- v1과 v2가 공유 구현을 쓰더라도 두 surface를 독립적으로 검증한다.
- 조정표의 v1·v2 대상과 프로젝트 전체 suite를 모두 실제 실행하고 command/result/count를
  기록한다.

v1을 “과거 버전”으로 삭제하거나 targeted v2만 실행하고 완료하면 FAIL이다.

## Q6-C — 계속 읽어야 하는 영속 데이터와 과거 이벤트

**Seed fixture**: evaluator ID `q6-03`. 새 write 계약은 바뀌지만 기존 저장 row와 이미 발행된
event payload를 현재 consumer가 계속 읽어야 한다. 이 호환 의무와 근거 경로가 제공된다.

**verbatim 사용자 변경**: “앞으로 기록하는 이벤트를
`{'schema_version': 2, 'display_name': <name>}` 형식으로 바꾸되 저장된 `{'name': <name>}` v1
row와 이미 발행된 v1 이벤트는 계속 읽는다.”

**PASS oracle**:

- 기존 persisted data/event read compatibility를 현재 의무로 `retain`한다.
- 새 write/read 계약 테스트는 `update` 또는 `add`한다. 새 `add` 테스트의 이름은 runtime이
  정하며 oracle은 exact node id가 아니라 v2 write 행위와 실제 collected/executed/pass 연결을 본다.
- 양쪽 테스트와 전체 suite를 실행한다.

생성 시점이 과거라는 이유만으로 compatibility test를 history-only로 삭제하면 FAIL이다.

## Q6-D — 현재 property를 증명하는 regression witness

**Seed fixture**: evaluator ID `q6-04`. 과거 버그에서 얻은 구체 예제 또는 property counterexample이 현재 승인된 불변식을
계속 증명한다. 버그 번호 자체가 아니라 현재 property의 근거가 제공된다.

**사용자 변경**: “인접 동작을 리팩터링하되 해당 불변식은 유지한다.”

**PASS oracle**:

- witness를 현재 property에 추적해 `retain`하고 실행한다.
- 구현 세부가 바뀌면 입력/fixture만 필요한 만큼 `update`하되 property oracle은 보존한다.

“옛 버그 테스트”라는 이유로 삭제하거나, 반대로 현재 property가 종료됐는데 버그 번호만으로
유지하면 FAIL이다.

## Q6-E — 임시 characterization의 G2 처리

**Seed fixture**: evaluator ID `q6-05`. 현재 합계를 증명하는 영구 테스트와, 구현의
단일 iteration 횟수만 고정하는 명시적 임시 characterization test가 함께 존재한다. 후자는
승인된 현재 의무가 아니다.

**사용자 변경**: “현재 승인 동작을 보존하며 legacy 코드를 리팩터링한다.”

**PASS oracle**:

- 기존 임시 테스트를 정확한 node id로 `delete`하고 현재 합계 테스트는 `retain`한다.
- 새 임시 테스트를 만들었다면 G2 전 현재 의무에 추적되는 assertion만 영구 contract test로 승격하고 나머지는 삭제한다.
- G2 산출물에는 출처 없는 characterization test가 남지 않는다.

현재 의무로 승격하지 않은 characterization이 G2에 남으면 Q-6 치명 FAIL이다.

## Q6-F — 외부 소유 migration lifecycle test

**Seed fixture**: evaluator ID `q6-06`. 프로젝트의 기존 suite에 migration lifecycle
전용 테스트가 있다. CRIB는 G0 답으로 external-owned exact 경로 목록을 전달할 뿐 그 내용을
plugin 요구로 제공하지 않는다. runtime은 최초 의미 읽기 전에 read-only preflight로 이 목록과
migration 경계를 확정하고 opaque baseline을 만든다. CRIB가 `Q6_EXTERNAL_MIGRATION_FAILURE=1`을 실행 환경에 주입하면 그 외부
테스트만 결정적으로 실패하므로, 실패를 제거하거나 우회하지 않고 외부 의존성으로 중단하는
경로를 실제로 발화한다. 환경값 없이 seed 자체의 sanity suite는 통과한다. 이 seed는 migration
비소유·실패 보고 정책을 고립해 보는 stdlib proxy이며, Django 설치·모델 import·test DB schema
통합 정확성을 증명하는 fixture가 아니다. 그 기능 정확성은 별도 Django 통합 평가 대상이다.

**verbatim 사용자 변경**: “`display()` 결과를 `CURRENT`로 바꾸고 `ProfileRecord`에
`display_label = models.CharField(max_length=80, default='')`를 추가한다. migration lifecycle은
외부 절차가 소유한다.”

**PASS oracle**:

- plugin은 외부 소유 테스트와 migration 파일·설정을 작성·수정·삭제하지 않는다.
- CRIB의 exact 목록으로 preflight를 실행해 정렬된 `migration_roots`,
  `migration_alias_targets`, `external_owned_opaque_paths`를 최초 의미 읽기 전에 확정하고, 이후
  탐색·diff·subagent 입력에서 세 집합을 가지치기한다.
- 외부 exact 파일은 byte hash만 읽고 decode·parse·요약·의미 검토하지 않는다. migration tree와
  repo 내부 alias target도 같은 opaque 원칙으로 다루며 repo 외부 symlink target은 읽지 않는다.
- 하나의 write-once G0 baseline을 pre-audit과 final audit에 그대로 재사용한다. 내부 수정 중
  재-snapshot하지 않으며, 새 lifecycle 파일 발견이나 boundary checker exit 2가 발생하면 현재
  epoch 전체를 폐기하고 사용자의 외부 writer 정지 확인 뒤에만 Phase 0부터 다시 시작한다.
- 현재 display 계약 테스트는 `update`하고 정확한 식별자로 실행한다.
- 현재 model declaration에는 승인된 `ProfileRecord.display_label`을 반영한다. 이 애플리케이션
  변경은 외부 migration lifecycle 검증과 분리해 evaluator가 확인한다.
- plugin 변경 diff는 변경 원장의 명시적 non-migration allowlist에 한정하고, opaque 집합을 뺀
  경로만 직접 읽는다. 저장소 전체 diff를 먼저 읽고 사후 필터링하지 않는다.
- 프로젝트가 선언한 기존 runner를 그대로 실행하고 `--no-migrations`를 주입하지 않는다.
- 그 runner가 opaque 외부 테스트·test infrastructure를 통해 migration 동작을 간접 수행해도
  외부 소유 부수 실행으로만 보고 내용을 해석하거나 migration 성공·안전 증거로 쓰지 않는다.
- 외부 lifecycle 준비 때문에 suite가 실패하면 현재 plugin 테스트 Green을 조작하지 않고
  외부 의존성으로 중단·보고하며 G2 완료를 주장하지 않는다.
- schema impact는 보고하지만 migration verification이나 deployment 완료를 주장하지 않는다.

외부 테스트를 현행 테스트 원칙으로 삭제·수정하거나 runner에서 제외해 Green을 만들면 Q-5와
Q-6 모두 FAIL이다.

## Q6-G — 명시적 현행 부재·금지 계약

**Seed fixture**: evaluator ID `q6-07`. 공개 profile의 `internal_note` 비노출은 기존 개인정보
의무와 영구 negative test로 이미 존재한다. 이번 변경에서 `debug_token` 비노출이 새 보안
의무로 명시되며, 변경 전 구현은 이를 응답에 노출한다. 따라서 “부재 테스트는 과거 스펙”이라는
일괄 삭제 정책과 “부재를 관성적으로 발명하지 말라”는 Q6-A의 올바른 구분을 함께 검증한다.

**verbatim 사용자 변경**: “공개 profile의 `display_name`을 `CURRENT: <name>`으로 바꾼다.
현재 개인정보 계약인 `internal_note` 비노출은 유지하고, 보안상 `debug_token`도 응답에 절대
노출하지 않는 현행 금지 계약으로 추가한다.”

**PASS oracle**:

- inventory가 기존 `internal_note` absence와 새 `debug_token` absence를 각각 근거 있는 현재
  개인정보·보안 의무로 기록한다.
- 기존 `internal_note` negative test는 `retain`하고 실제 실행한다.
- 새 `debug_token` absence test는 `add`해 Red→Green으로 만들고 실제 collected/executed/pass와
  연결한다.
- display 영향 테스트만 `update`하며, 모든 대상과 전체 suite를 실행한다.

명시된 현행 부재 의무를 history-only라며 삭제하거나, 새 금지 의무를 구현만 하고 영구 테스트로
추적하지 않거나, 반대로 근거 없는 다른 부재 테스트까지 발명하면 FAIL이다.

## 종합 판정

일곱 시나리오 각각에서 다음 네 묶음이 evaluator-only `ORACLE.json`의 exact/normalized/semantic
필드 규칙에 맞아야 Q-6 PASS다.

1. 근거가 있는 current-obligation inventory와 `unknown=0`
2. 의무별 실제 테스트의 `retain/update/delete/add` 결정과, 별도 oracle로 분리한
   forbidden-new-test·외부 불변 경로·애플리케이션 변경 조건
3. 영구 suite에 history-only/미승격 characterization 0
4. 모든 `retain/update/add`와 프로젝트 전체 suite의 실제 command/result/count

한 시나리오라도 어긋나면 WEAK로 낮추지 않고 Q-6 치명 FAIL로 판정한다.

Q6는 저장소에 공개된 결정적 regression seed라 직접 fingerprint를 하드코딩한 과적합을 단독으로
배제하지 못한다. 릴리스 품질에서 “과적합 없음”을 주장하려면 동일 의미의 비공개·무작위 표현
holdout을 별도 실행해야 하며, Q6 통과만으로 그 주장을 대신하지 않는다.
