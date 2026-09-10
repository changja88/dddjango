# pre-gate 전사 결함 3종 수정 계획

> 실행: 승인된 단계 순서(문제 리뷰 → 계획 리뷰 3명 → 구현 → 구현 리뷰 3명 → 최종 감사·검증 → 커밋·make release)를 따른다.

**Goal:** dddjango 2.18.0의 remove 잔존 디렉터리, 보조 dataclass 데코레이터, TYPE_CHECKING admin 별칭 전사 손실을 고친다. 기존 27종 검사기의 규칙·면제 조건은 유지한다.
**Architecture:** `design_pregate.py`의 기존 file-plan/symbols 채널만 확장한다. 명세의 명시 재료를 scratch에 전사하며, 사용자 프로젝트를 수정하거나 산문에서 타입·데코레이터를 추론하지 않는다.
**Stack:** 배포 코드는 Python 표준 라이브러리, 규범 저작은 maintainer rdflib 도구, 회귀 검증은 기존 검사기와 임시 Git 저장소.
**Evidence:** `~/.claude/jobs/0d7b3328/tmp/plugin-reports/2026-09-10-dddjango-2.18.0-pregate-defects.md`; B0 원 블록 해시 `c9247080f931`, 예보 39건 중 세 전사 결함 38건. scratch에서 세 손실만 복구하면 1건(#376, 기존 S1 본문 사각) 남고 신규 진단 0. 별도 제보인 예외 배치 규범은 R-3449에 이미 있으므로 변경 대상이 아니다.

## 1. 삭제 실체화

- 대상: `dddjango/scripts/design_pregate.py:materialize` 및 byte 미러.
- 비후행 `remove` 경로의 부모부터 scratch 루트 직전까지를 정리 후보로 한정한다. 파일이 dirty overlay에서 이미 사라져도 후보는 남긴다. 다른 경로의 원래 빈 폴더는 건드리지 않는다.
- 모든 add/empty/remove 적용 후, 신규 BC 골격과 init 보강 전에 후보를 깊은 순서로 `rmdir`한다. 실제로 비어 있을 때만 제거한다. 살아 있는 파일(0B·`__init__.py`·미추적 파일 포함), add/empty, update 실물, 후행 remove 실물은 보호된다. symlink 디렉터리 또는 symlink 조상을 거쳐 정리하지 않는다.
- 신규 BC 골격 대상은 add/empty가 있는 BC로 한정한다. remove만 있고 dirty overlay로 BC가 전멸한 경우 골격을 다시 만들지 않는다.
- 성공한 디렉터리 제거는 별도 `pruned_dirs` 메타데이터로 기록하고 stdout/리포트에 병기한다. 파일 `materialized` 건수에는 넣지 않는다. overlay 선삭제 뒤 폴더만 정리한 경우 기존 실존 판정 후 skip(exit 4, 실존 결손이면 5)하고 registry를 호출하지 않는다. 후보가 비어 있지 않으면 보존하고, ENOTEMPTY/ENOENT 외 오류는 숨기지 않는다.
- 검증: 인스턴스 전량 제거(aggregate/usecase/admin), 일부만 제거, 미추적 파일·0B 파일·init 잔존, 같은 부모 add/empty, 후행 remove, overlay 선삭제, 무관한 빈 alien 디렉터리, symlink 경계, BC 전멸. 기존 path 진탐을 유지하며 세 제거 오탐 계열이 사라져야 한다.

## 2. symbols 데코레이터

- `Symbol.decorators: list[str]` 추가. 클래스 행 뒤 별도 `path.py::ClassName @dataclass(frozen=True, slots=True, kw_only=True)` 행을 허용한다. 복수 행은 명세 순서대로 클래스 바로 위에 렌더한다.
- 선행 클래스가 없거나 함수에 붙인 행은 형식 red. 식은 AST로 dotted name 또는 그 호출인지 검사하고 원문을 보존한다. import를 추론·삽입하지 않는다. `@dc(...)`, `@dc.dataclass(...)`는 boundary-imports의 실제 alias를 그대로 소비한다.
- physical-signals에서 base를 보충하는 Symbol 복사에도 decorators를 보존한다. 마이그레이션 정형 처리와 비-add/S′ 처리에서 새 재료가 유실·거짓 선언으로 바뀌지 않게 검증한다.
- 검증: 공개 보조 dataclass를 필드로 참조하는 response의 #160/#484 해소; 데코레이터 없음·참조 없음·가짜 dataclass import는 여전히 red. 옵션·alias·복수 데코레이터와 base 보충을 AST로 대조한다.

## 3. symbols 모듈 별칭

기존 symbols 펜스 안에 다음 행을 추가한다. 모듈별 별칭은 클래스/함수 행보다 먼저 적는다.

```symbols
path.py::alias _DirectBase = admin.ModelAdmin
path.py::alias[TYPE_CHECKING] _BookAdminBase: TypeAlias = admin.ModelAdmin[BookModel]
path.py::alias[else] _BookAdminBase: type[admin.ModelAdmin] = admin.ModelAdmin
path.py::BookAdmin(_BookAdminBase) {list_display = ("title",)}
```

- `ModuleAlias`는 이름·typing 또는 무조건 대입문·선택 runtime 대입문을 보존한다. 타입 분기 두 행은 같은 파일·같은 이름의 인접한 유효 행으로 짝을 이뤄야 한다. 무조건 alias는 단독이다.
- 대입문은 AST의 단일 Assign(Name 하나) 또는 값 있는 AnnAssign(Name)만 허용한다. RHS는 이름·속성·타입 첨자 및 그 안의 타입 표현식으로 한정하며 함수/클래스 정의나 여러 문장은 허용하지 않는다. 불완전한 분기·중복 alias·다른 이름의 else·클래스 뒤 alias는 형식 red.
- import 다음, 클래스 앞에 원문 대입을 렌더한다. 분기는 `if TYPE_CHECKING:` / `else:`를 그대로 보존한다. `TYPE_CHECKING`, `TypeAlias`, admin, 모델 등의 import는 boundary-imports에서 명시한다. 신규 채널·경로 기반 면제·런타임 코드 실행은 없다.
- alias 이름은 유효한 단일/쌍 선언이 완료된 경우에만 `declared`에 기록하여 update S′에서도 쓸 수 있게 한다. 데코레이터 행만으로는 이름이 선언되지 않는다.
- 검증: 직접 ModelAdmin·무조건 별칭은 기존 #646 맨몸 제네릭 위반을 유지하고, 무어노테이션 alias 자체도 #493 진탐이다. 타입 분기 별칭만 #493/#646 위반·후보 모두 0이다. 비admin Helper의 무어노테이션 필드는 기존 #493 유지. malformed 행/누락 분기는 parse 또는 compile 형식 red, 기존 문법은 그대로 통과한다. update의 유효 쌍만 S′로 기록하고, migration alias-only/빈 init의 미반영 재료는 채널 메모로 남긴다.

## 4. 구현과 규범 동기화

1. `workspace/tools/pregate_transcription_smoke.py`에 회귀 검증을 작성하고 수정 전 실패를 기록한다. 검사기 직접 실행과 실제 materialize를 사용하고 기대 규칙 ID/파일 존재/AST를 단언한다. 직접 수집은 Findings/Candidates defer=True, subprocess의 `DJR_FINDINGS_JSON`/`DJR_VIOLATIONS_DIR`는 임시 경로로 격리한다. Makefile verify-base-regen의 기존 pregate_fixture_run 바로 뒤에 연결하고, manifest_seal.py의 harness globs에 새 검증 파일을 명시한다.
2. 위 세 변경을 최소 구현하고 회귀 검증을 green으로 만든다. 기존 `pregate_fixture_run.py`도 실행한다.
3. `ontology/rules/agent-design-architect.ttl`의 R-3425(remove), R-3426(symbols)을 새 Expression revision으로 개정한다. 기존 Work ID와 5개 채널은 유지한다. `ontology_render.py --apply agent-design-architect`로 Claude 역할을 투영하고 렌더된 두 문단을 마커 없는 Codex 역할 대응 문단에 반영한다. graph-owned 본문을 손으로 수정하지 않는다. 새 Expression 2개에 따라 `workspace/eval/fixtures/ontology_gate/target-counts.json`의 ExpressionShape 기대값을 3607→3609로 갱신한다.
4. `design_pregate.py` 문법 헤더와 두 런타임 스크립트 byte 미러를 동기화한다. `make rulepack`으로 소성물과 미러를 재생성한다. 현재 checker 소스에서 이미 생성되는 @dataclass catalog는 규칙을 바꾸지 않는 한 그대로 둔다.
5. B0 명세를 임시 파일에 복사해 기존 remove@L2를 원 remove로 복원하고 두 response의 데코레이터 및 admin 별칭만 새 문법으로 명시한다. 원 사용자 프로젝트·명세는 변경하지 않는다. 같은 base에서 전체 registry 재실행: 원 39건 중 38건 소멸, #376 1건만 잔존, 신규 진단 0을 목표로 판정한다. 이 결과는 임시 재현 증거이며 사용자 명세를 자동 교정했다는 뜻이 아니다.

## 5. 독립 리뷰와 완료 조건

- 계획 리뷰 3명: 삭제 경계/구조 진탐, 문법·전사·검사기 상호작용, 규범·회귀·릴리즈 절차. BLOCKER/MAJOR 해결 후 구현한다.
- 구현 리뷰 3명: 동일 세 관점을 독립 검증한다. 발견 수정 후 필요한 검증을 다시 실행한다.
- 최종 감사: 변경 범위, checker 변경 0, Claude/Codex byte·규범 미러, 그래프 정본·소성물, 사용자 소스 불변, 회귀 음성 대조군 확인.
- `make verify-mutation`, manifest 봉인 재발행, 마지막 `make verify` green. 검증 뒤 파일을 다시 고치면 봉인/verify를 다시 수행한다. 최종 로그 경로와 결과만 완료 기록에 쓴다.
- 수정 커밋 후 `make release`의 patch 선택으로 dddjango 2.18.1 릴리즈. manifest 변경에 따른 plugin strict validate를 확인한다. 배포 결과(태그·GitHub Release·remote HEAD) 검증 후 종료한다.

## 진행 기록

- ⓪~①: 원 보고서·현 코드·scratch 반증 및 독립 문제 리뷰 3명 완료. 세 결함 확인, 경로 면제·전역 빈 폴더 정리 대안 기각.
- ②: 이 계획 작성. 아직 구현 전.
- 계획 리뷰: symbols 관점 통과. 삭제 관점 MAJOR(폴더 정리만 있을 때 공허 차분 충돌)를 별도 메타데이터/skip 유지로 해결. 규범 관점의 ExpressionShape +2 및 Codex 투영 문단 반영 방법을 명시.
- ③: 독립 계획 리뷰 3명 모두 통과. smoke sink 격리·봉인 등재도 반영.
- ④: 수정 전 14개 테스트에서 19개 subcase 실패를 확인(`/tmp/pregate-transcription-red.log`). 세 전사 수리 후 green. 기존 pregate fixture 전량도 통과(`/tmp/pregate-existing-fixtures.log`).
- ⑤: 독립 구현 리뷰 3명 완료. symbols 리뷰의 MAJOR 2건(compile 전용 오류가 update S′를 통과, 기존 alias 함수 문법 충돌)을 추가 회귀 8개 subcase의 red로 확인(`/tmp/pregate-review-red.log`)하고 수정. 재리뷰에서 모두 해소 판정. 최종 smoke 15개 green(`/tmp/pregate-transcription-green.log`). 삭제·규범 리뷰도 통과이며, 규범 리뷰의 메모리 변이 5종(전사 삭제·무조건 면제·분기 평탄화)은 모두 단언 실패로 검출.
- B0 실재현: 원 명세는 변경하지 않고 임시 사본에 명시 문법을 추가. 원 remove 복원 블록 `c9247080f931` → 새 문법 `d84ee924ad49`. base `b1e0b343f3a19715533ff2c3ed922b398cb91532`, 현재 overlay 85(레인 구현 진행 중, 원 보고서의 13과 다름), 파일 실체화 208·빈 부모 정리 11·실존 결손 0. 예보는 원 보고서 39건에서 #376의 기존 안정 ID `78ca0823d417` 1건만 잔존, 신규 ID 0. exit 2는 남은 S1 함수 본문 스텁 한계의 정상 결과다. 증거 `/tmp/pregate-b0-fixed-cs9ta_br/report.md`, stdout `output.log`, 원 명세 SHA 불변 확인 `source-hash.json`.
- ⑥ 최종 감사: 기존 check-*.py 변경 0, 그래프 Work·Block·Section 수 불변/Expression +2, Claude·Codex 두 규범 문단 동일 및 스크립트 byte 미러, 신규 테스트 make verify·봉인 연결 확인. `make verify-mutation` 11종 전건 red 검출(`/tmp/pregate-verify-mutation.log`). 최종 봉인·전체 verify 이후 수정 커밋과 patch release로 마감한다.
- 전체 verify 첫 실행(`/tmp/djr-verify.pWXwMg`)에서 graph-owned s005의 원장 baseline 불일치가 검출됐다. 그래프 렌더 자체는 일치했으나 LEDGER 재기준선 행이 빠져 있었다. `ontology/LEDGER.tsv`에 마커 제거 후 새 SHA와 R-3425/R-3426 개정 사유를 append했다. 봉인을 다시 발행하고 전체 verify를 처음부터 재실행하며, 이 중간 실행은 green 근거로 사용하지 않는다.
- ⑥ 완료: 원장 append 후 독립 재검토·렌더 동기(541절 red 0) 통과. 봉인 재발행 뒤 최종 `make verify` **6/6 green**, 200초, 전체 로그 `/tmp/djr-verify.QFEHd7`. 이 실행을 수정 커밋의 검증 근거로 사용한다.
