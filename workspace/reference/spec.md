# dddjango 제품 명세

이 문서는 `dddjango`의 canonical product spec이다. `workspace/reference/**/reference/final.md`는
각 스킬의 source reference corpus이고, 런타임 역할·workflow·완료 의미는 이 문서의 제품
경계를 따라야 한다.

## 제품 목표

`dddjango`는 기존 Django 프로젝트의 한 기능을 요구 정리 → DDD 설계 → 구현(TDD)으로
진행한다. Coordinator는 G0/G1/G2 사용자 게이트와 전문 역할 분리를 지키며, 현재 승인된
기능의 애플리케이션 코드와 테스트를 완성한다.

## Django DB migration lifecycle 비소유

`dddjango`는 최종 Django model 선언과 현재 애플리케이션 동작을 소유하지만, Django DB
migration lifecycle에는 참여하지 않는다.

- migration 파일을 생성·수정·삭제·이동·검토·테스트하지 않는다.
- `makemigrations`, `migrate`, `sqlmigrate`, `showmigrations`, squash, fake 등
  migration 전용 명령을 직접 호출하거나 실행 절차로 지시하지 않는다.
- migration history·graph·operation·DDL, `RunPython`/`RunSQL`, state-only operation,
  backfill, expand/contract, 운영 적용·롤백·모니터링을 설계하거나 검증하지 않는다.
- 기존 brownfield Django persistence app과 그 `migrations/`의 물리 위치를 touched 여부와
  무관하게 보존한다. 도메인 분리가 필요하면 기존 ORM을 repository/adapter 경계로 감싼다.
- 신규 앱에 framework/external owner가 만든 빈 `migrations/__init__.py` scaffold가 이미
  존재할 수 있으나, dddjango는 그 scaffold나 numbered migration을 생성하지 않는다.

Django는 migration 메커니즘을 제공할 뿐 rename·데이터 전환·운영 안전의 의미를 자동으로
책임지지 않는다. 생성·검토·적용·데이터 전환·배포 승인은 프로젝트의 외부 release/deployment
절차와 개발자가 소유한다.

플러그인은 schema-affecting model change의 유무만 최종 보고한다. operation·DDL·순서·backfill
계획을 담은 별도 handoff 문서는 만들지 않는다. schema 영향이 있으면 G2에서
application/model implementation과 deployment readiness를 분리하고, migration verification은
`범위 밖·미검증`, deployment readiness는 `외부 절차 대기`로 표시한다. 전환기
애플리케이션 동작은 외부 owner가 현재 계약으로 명시했을 때만 구현하며, 필요한 계약이 없으면
추측하지 않고 게이트로 반송한다.

플러그인이 프로젝트의 기존 테스트 명령을 변경 없이 실행했을 때 test runner가 테스트 DB 준비
과정이나 opaque 외부 테스트·test infrastructure를 통해 migration 동작을 간접 수행할 수 있다.
이는 외부 소유 부수 실행이며 migration 검증 증거가 아니다. `dddjango`는 내용을 해석하거나
성공·안전을 주장하지 않고, 이를 피하려고 `--no-migrations`나 전역 설정을 강제하지도 않는다.

유일한 기계적 관찰은 자기 무변경 약속을 확인하는 migration-boundary v11 opaque check다.
Coordinator는 프로젝트 내용을 의미적으로 Read/Grep/Glob하거나 `.dddjango`를 나열·생성하기
전에, 사용자 요청·프로젝트 지침이 이미 제공한 외부 소유 exact file을 canonical JSON으로 만들어
read-only `preflight`를 실행한다. preflight는 현재 저장소에서 다음 세 집합을 정렬된 canonical
`TARGET_DIR`-relative path로 확정한다.

- `migration_roots`: 정적으로 식별한 exact migration tree root
- `migration_alias_targets`: opaque hasher가 따라간 repo-internal migration symlink target
- `external_owned_opaque_paths`: 프로젝트/사용자가 외부 lifecycle 소유로 미리 선언한 exact file

세 집합과 repo-internal alias는 이후 모든 의미 탐색, subagent 입력, 일반 백스톱 순회와 diff
대상에서 **진입 전에** prune한다. external 목록은 G0에 이미 존재하는 non-symlink regular exact
file만 허용한다. 각 경로와 조상은 저장소 안에 있어야 하고 symlink일 수 없으며, portable
shell-safe 문자 `[A-Za-z0-9_./@+-]`만 사용한다. Django settings·표준 entrypoint·`apps.py`·
`models.py`·등록된 AppConfig 등 structural discovery source와 겹치거나 hardlink인 항목은
fail-closed G0 blocker다. 선언이 없을 때도 canonical `[]`를 전달하며, 그 의미는
`declared none; not proof none exist`다. 파일명으로 목록을 추정하거나 전수 의미 스캔하지 않는다.

v11 manifest는 정적 `INSTALLED_APPS` 등록 또는 실제 Django `AppConfig` 상속으로 식별한 로컬
앱의 exact `migrations` tree, 정적 direct `MIGRATION_MODULES` 대입 원문 line 범위와
repo-root/`src` custom package, 기존 app identity·등록, G0 application container와 layer issue를
기록한다. settings bootstrap은 repo-root/`src`의 `manage.py`와 두 lexical root의 직접
project-package `asgi.py`/`wsgi.py` 후보 전체를 구조적으로 한정해 읽고, 서로 다른 진입점이
선언한 settings module의 합집합을 사용한다. symlink entrypoint는 의미 읽지
않고 G0에서 fail-closed한다. Django settings·entrypoint 같은 structural discovery source와 custom migration root의
겸용은 선판별이 불가능한 이중 역할이므로 fail-closed한다. 이보다 깊은 비표준 entrypoint만으로
선택되는 settings는 정적 범위 밖이다. 구조 발견 source는 경계를 식별하는 데 필요한 범위에서만
정적으로 읽는다. migration
tree와 external exact file은 decode·AST parse·요약·의미 분류·review·LLM 입력을 금지하고,
path·종류·opaque byte SHA-256만 기록한다. Python interpreter가 재생성하는 `__pycache__/`
subtree만 제외하며 그 밖의 `.pyc`·`.pyo`는 추적한다.

settings bootstrap의 지원 문법은 의도적으로 좁다. literal collection/dict, 단일 대입된 정적
문자열·collection 이름, 문자열 `+`, collection `+`/`|`, 기존에 지원하던 top-level `+=`/`|=`
조합만 정적으로 푼다. direct mutable Name alias, method/subscript mutation, alias-container mutation,
조건부·중첩 대입, 재할당된 dependency, 함수 호출로 만든 값, 선택된 structural source의
syntax/encoding 오류·symlink·hardlink는 scope를 완전하게 확정할 수 없으므로 preflight exit 1이다.
이는 Python settings 의미론을 실행해 추측하는 대신 모호한 구성에서 작업을 시작하지 않는
fail-closed 호환성 제한이다.

repo-internal migration symlink target은 target byte를 opaque hash에 포함하고 canonical relative
target을 `migration_alias_targets`에 기록해 일반 도구도 같은 alias를 prune한다. repo-external
target은 내용을 읽지 않고 repo 쪽 symlink target 문자열과 `outside-root` marker만 동결한다.
opaque-owned regular file의 hardlink는 다른 경로 alias를 안전하게 prune할 수 없으므로
fail-closed한다. 다만 bind mount처럼 symlink도 hardlink도 아닌 filesystem alias는 이 경계가
식별하지 못한다.

Phase 0은 artifact write/delete 전에 같은 external JSON으로 `.dddjango` artifact root를
preflight한다. 성공하면 timestamp+고엔트로피 suffix의 portable run-id를 만들고
`<feature>/.runs/<run-id>/`에 scope/design 작업본과 고유 write-once G0 baseline+receipt pair를
둔다. run-id는 충돌 방지 식별자이지 작성자·소유권 증명이 아니다. 정상 실행은 다른 run의 pair를
나열·열기·복구·삭제하지 않고 전역 coordinator lock을 사용하지 않는다. recursive `recover`는 다른
coordinator가 없다는 별도 확인 아래 정지 상태 유지보수 진단에만 사용한다.

한 내부 작업 사이클은 이 **단일 write-once G0 baseline**을 일반 감사 직전과 모든 read-only
백스톱·독립 감수 직후에 다시 비교한다. 내부 Red/Green·리뷰 반송·수정 때문에 새 snapshot을
만들어 변경을 흡수하지 않는다. 사전 verify 0은 `pre-audit-clean(pending final verify)`, 같은
baseline의 최종 verify 0만 `verified-clean`이다. exit 1은 baseline·receipt·I/O 검증 인프라
오류라 exact pair를 보존하고 새 기준선으로 우회할 수 없다. exit 2는 주체를 단정하지 않는
`invalidated` 상태다. 현재 generation을 폐기하고 중립적으로 보고한 뒤 exact-own pair와 current-run
임시 문서를 cleanup한다. 외부 작업 완료 확인 뒤 새 run-id로만 재개한다.

정상 조사 중 새 lifecycle test를 처음 발견하면 편집 전에 exact path만 반환하고 현재 manifest를
확장하지 않는다. 같은 baseline verify 뒤 현재 증거를 전부 stale 처리한다. exit 0/2이면 expected
run-id cleanup helper로 exact-own pair만 지우고, exit 1이면 pair를 보존한다. 외부 작업 완료 뒤
expanded list와 새 run-id의 preflight→snapshot부터 다시 시작한다. 외부 변경을 plugin 산출로
검토·수정·되돌리지 않으며 새 baseline도 migration의 정확성 승인이 아니다.

G0 test/config inventory는 runner 수집 root 또는 `test/`·`tests/`와
`test_*.py`·`*_test.py`·`tests.py` fallback을 사용한다. 원장 밖 최종 delta는 소유자를 추정하지
않고 `concurrent/unknown`으로 분류한다. 현재 의무 test/fixture/config와 겹치면 pass여도 final
generation을 stale 처리하고, 그 밖의 안정된 변경은 shared-generation dependency로 보고한다.
파일 변경 원장은 first-touch 직전 `check-working-tree-generation.py path-state TARGET_DIR PATH`가 반환한
`absent` 또는 SHA-256을 기록하고 자체 직렬화하지 않는다. 같은 path의 이후 행은
`next.before == previous.after`여야 한다. final generation 시작 직전 touched 각 path의 현재 path-state도
같은 helper로 다시 계산해 원장의 마지막 `after`와 같아야 하며, 다르면 create/delete/type/mode를
포함한 overlap blocker다. 이 원장은 독립 provenance 증명이 아니다.

G0에는 `promote-run-artifacts.py seed`가 짧은 feature-local lock 안에서 canonical scope/design
pair를 함께 읽어 current-run 작업본에 exact bytes로 seed하고 각 `absent|SHA-256` anchor를 반환한다.
각 run은 작업본만 수정한다. G1 승인 뒤 같은 helper의 `commit`이 같은 짧은 lock 안에서 두 anchor와
current-run source를 확인하고, 교체 뒤 source/canonical bytes를 재확인해 둘 다 같을 때만 성공한다.
교체 전 transaction marker와 교체 후 receipt를 fsync해 process crash의 torn pair는 다음 명령에서
fail-closed한다. marker가 없을 때 receipt는 canonical 소유권을 갖지 않으므로 branch checkout·외부
canonical 변경을 막지 않고, marker의 previous pair가 그대로면 교체 전 crash로 안전 회수한다.
달라졌으면 아무 canonical도 쓰지 않고 `rebase`가 current 작업본을 보존한 별도 exact
base pair로 최신 canonical을 받아 architect rebase·영향 lens review·G1 승인을 반복한다. Phase 2
진입·final generation 시작·G2 승인 후에는 `check`와 fingerprint의 byte-equality 전제를 다시 검사하고,
불일치는 같은 rebase/G1/Phase 2 재실행 경로로 보낸다. 이 lock은 canonical pair의 read/commit/check
순간에만 있고 G0·설계·구현·테스트 실행 전체를 소유하거나 직렬화하지 않는다. 종료 cleanup은
`cleanup TARGET_DIR STATE_FILE RUN_ID` helper가 filename/receipt/root를 검증한 exact-own pair에만
허용하며 foreign pair와 glob 삭제는 금지한다. terminal run은 current-run의 exact scope/design과 존재하는 exact rebase base pair만 더
삭제하고 directory가 비었을 때만 제거한다. `waiting-concurrent`와 승인 대기는 pair·작업본을 보존하고,
run 종료나 exit 0/2 invalidation은 cleanup하며 exit 1은 pair·작업본을 보존한다.

G2는 독립 patch Green이 아니라 한 shared working-tree generation의 증거다.
`check-working-tree-generation.py TARGET_DIR BOUNDARY_STATE CURRENT_RUN_DIR`가 boundary state/current run의
exact run-id 결박과 current-run/canonical scope/design byte equality를 먼저 확인한 뒤, 검증된 boundary
receipt, HEAD·exclusion-filtered index와 non-opaque dirty/untracked path의 path·lstat kind·mode·regular
bytes·symlink payload·submodule state를 길이 태그 canonical hash로 계산한다. current-run과 canonical
scope/design은 포함하고 staged 상태까지 foreign `.runs/*`, exact epoch pair, `.git`, cache, 세 opaque 집합은 제외한다. 이 fingerprint를
현재 의무 테스트·전체 suite·17종·layer·독립 reviewer·final boundary verify 전후에 비교한다.
다르면 전 증거를 버리고 한 번 재실행하며 다시 변하면 `waiting-concurrent`다. G2 승인 대기 뒤에도
cleanup 전에 same-baseline verify와 같은 fingerprint를 다시 확인하고, 달라졌으면 승인과 증거를
stale 처리해 새 generation과 G2 승인을 거친다.
별도 patch의 독립 적용 가능성은 Git worktree에서 검증해야 한다.

이 검사와 final generation fingerprint는 관찰한 endpoint의 동일성만 보장한다. 지원 문법 밖의 직접 구성은 exit 1로 막지만,
import side effect·별도 모듈·함수 내부 global mutation처럼 선택된 source의 정적 assignment에
드러나지 않는 Python 실행 의미까지 완전하게 증명하지는 않는다. AppConfig field가 참조한 별도 symbol의 runtime 값,
외부 환경에서만 선택되는 settings, 정적 신호가 없는 앱, bind mount alias,
`MIGRATION_MODULES` 대입 원문 범위 밖 settings 편집, migration 전용 명령 실행, 중간 생성 후
원복, permission·owner·xattr, baseline과 receipt의 동시 제거·변조, DB-only side effect,
마지막 scan 직후 race, fingerprint 중간 변경 후 원복(ABA), ignored file, 공유 DB/cache/port와
외부 프로세스 상태까지 증명하지 못한다. 특히 최초 preflight와 Phase 0 snapshot 사이의 의미
조사 동안 외부 owner가 새 migration root나 lifecycle test를 동시에 만들면 최초 prune 집합에
없어 의미 읽기가 먼저 일어날 수 있다. 그러므로 이 구간의 외부 동시 변경·quiescence는 경계가
보장하지 않는다. 동적 custom test collection도 runner/config와
fallback에 드러나지 않으면 inventory가 놓칠 수 있고 transcript·원장은 실행 주체의 완전한
보고를 전제로 한다. 따라서 기계 검사가 clean이어도 `migration verification=범위 밖·미검증`
상태와 외부 deployment migration 책임은 바뀌지 않는다.

## 현재 계약 기반 테스트

영구 테스트의 기대 결과는 현재 승인된 요구·설계 결정·도메인 불변식·지원 중인 공개/영속
계약·보안/개인정보/규제 의무에 추적 가능해야 한다. 테스트·현재 구현·과거 관찰은 그 자체로
권위가 아니다. 출처가 충돌하거나 지원 여부가 불명확하면 구현이나 테스트 삭제 전에 G1로
반송한다.

G1 전에 `current-obligation inventory`를 만들고 최소한 다음을 근거 경로와 함께 확인한다.

- surface/version
- consumer와 support 상태
- persisted data/event 계약
- deprecation window
- security/privacy/regulatory 의무
- negative/absence 의무
- `retain`/`end`/`unknown` 결정

`unknown`은 G1 blocker다. "지원 의무 종료"와 "새 계약이 이전 요소의 관찰 가능한 부재를
보장함"은 별도 결정이며, 어느 하나를 다른 하나로 추정하지 않는다. inventory와 근거는 설계
reviewer, acceptance tester, coder, discipline reviewer가 같은 입력으로 사용한다.

명세나 계약이 바뀌면 같은 변경에서 의미상 영향받는 기존 테스트를 다음으로 조정한다.

- `retain`: 현재 의무와 기대가 그대로다.
- `update`: 의무는 남지만 승인된 입력·결과·지원 범위가 바뀌었다.
- `delete`: 테스트의 유일한 의무가 명시적으로 종료됐고 호환·영속·보안·부재 의무도 없다.
- `add`: 새 의무 또는 현재 미검증 의무가 생겼다.

새 명세의 침묵은 제거 승인이 아니다. 지원 중인 구버전·consumer·deprecation 기간·기존
영속 데이터·과거 이벤트·보안/규제 의무·명시적 금지/부재는 모두 현재 계약이다. 반대로
과거 동작·버그 번호·현재 구현 관찰만을 이유로 영구 테스트를 유지하거나 추가하지 않는다.
회귀 테스트와 property counterexample은 현재 의무/속성이 남아 있는 동안만 유효하다.

레거시 조사·리팩터링 중 특성화 테스트를 임시 안전망으로 사용할 수 있으나, G2 전에는 현재
의무에 추적 가능한 영구 테스트로 승격하거나 제거한다. migration lifecycle 테스트는 외부
owner의 자산이므로 `dddjango`가 작성·수정·삭제하지 않는다. 외부 owner가 lifecycle 전용으로
식별한 테스트는 current-obligation evidence나 영향 조정 대상으로 삼아 의미를 검토하지 않고,
G0→최종 전체 테스트 path/hash 자기감사에서 경로·바이트 변화만 확인한다.

G2 전에는 두 테스트 조정표의 모든 `retain`·`update`·`add` 항목과 프로젝트가 선언한 전체
suite를 실제로 실행하고 명령·결과와 러너가 입증한 collected/executed/pass/fail/skipped 개수를 기록한다. collection과 execution을 따로 보고하지 않는 러너는 입증 가능한 값만 기록하고 추정하지 않는다. 실행할 수 없는 현재 의무는 완료로
주장하지 않는다. 외부 소유 migration lifecycle test의 실패는 그대로 보고하되, 테스트를
바꾸거나 `--no-migrations`로 수집·환경을 우회하지 않는다.

## 권위와 평가

현재 제품 의무의 우선순위는 사용자 승인 요구/G1 설계 → 지원 중인 공개·영속·보안 계약 →
테스트와 구현의 관찰 증거 순이다. 제품 테스트와 별도로 평가는 원 사용자 요구와 적용 표준에서
독립 오라클을 사전등록한다. 계약이 바뀌면 과거 결과를 소급 재채점하지 않고 새 평가 버전을
동결한다.
