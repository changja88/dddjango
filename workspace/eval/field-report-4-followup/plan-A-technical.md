# 현장 보고 4 후속 계획 — 독립 적대 리뷰 A(기술)

2026-09-11. 검토 대상은 `workspace/plan/2026-09-11-field-report-4-followup.md`의 최초 320행 판이다. 계획 SHA-256은 `bc3e95b7d0146e917ecbbe70ab5e69fee95cbfb26ed3020a9beb0e7dc5eccdad`, 코드 기준 HEAD는 `3355710dcbaf023a16856cb2f307aa2a03fc0996`이다. 계획 작성과 독립적으로 `brief.md`, 문제 리뷰 A/B/C, `docs/DEVELOPMENT.md`, 관련 현재 검사기·pre-gate·registry·검증 러너를 대조했다.

**판정: BLOCKER 0, MAJOR 2, MINOR 0.** 두 MAJOR의 최소 보완은 현재 승인 방향 안의 기술 보완이다. **새 사용자 정책·범위 결정은 필요하지 않다.** 최초 계획을 그대로 구현하면 생성 진단과 실제 코드의 구별에 필요한 위치 정보를 사용할 수 없으므로, 해당 계약을 계획에서 고친 뒤 구현에 진입해야 한다. 나머지 항목은 아래 지원 범위와 반대 대조를 지키는 조건으로 구현 가능한 계획이다. 이 판정은 구현 성공이나 기능 검증 완료가 아니다.

## MAJOR A-P1 — F12의 분리 함수가 행 번호를 이미 잃은 입력을 받는다

- **계획 위치:** 118행 `partition_generated_findings(attributed, generated_methods)` 인터페이스, 127~129행의 정확한 `path+line` 분리·보고 계약. 같은 전달 경로를 사용하는 F9의 161행에도 영향을 준다.
- **현재 코드:** `dddjango/scripts/design_pregate.py:1411`의 `run_gate`는 `introduced.json`의 `attributed_lines`만 읽고 반환한다(1427~1429행). `dddjango/scripts/registry_gate.py:149`의 `_normalize`와 239행은 진단 위치 행 번호를 `:N`으로 바꾼다. `_write_introduced`(256~301행)는 원래 위치를 가진 `records`, `unmatched_lines`, 선택형 `candidate_lines`/`candidate_records`도 이미 제공하지만 현재 `run_gate`가 이들을 버린다.
- **발생조건:** 생성 `after_commit`에서 #376이 하나라도 귀속될 때다. 계획의 함수에 도착하는 문자열은 `...books_unit_of_work.py:N: after_commit 구현이 ...`이므로 실제 메서드 시작·끝 행과 대조할 숫자가 없다. 계획대로 위치 불명을 유지하면 F12 오탐이 그대로 남고, 파일만 보고 제거하면 기존 실코드의 #376까지 제거할 수 있다.
- **독립 helper 증거:** 같은 파일의 5행과 15행에 있는 #376 두 레코드를 실제 `_write_introduced`에 넣으면 귀속 문자열은 **1개**, `records`는 **2개**다. 각 `record.file`에는 `...py:5`, `...py:15`가 보존된다. 별도 `lineno` 필드는 없다. 현재 `run_gate` 반환은 `(2, [':N으로 정규화된 문자열'], stdout)`뿐이었다.

**최소 기술 해결안:** `run_gate`의 반환 계약에 위 sidecar의 원본 레코드와 대응 없는 귀속 목록을 운반한다. registry의 기존 JSON 형식을 새로 만들 필요는 없다. 분리는 `_stable_id(rule+path)`가 아니라 **기존 registry의 전체 정규화 귀속 키**에 대응하는 원본 레코드 집합을 기준으로 한다. 모든 대응 레코드의 경로·행·규칙이 이번 렌더의 `after_commit` 범위에 정확히 속할 때만 그 귀속 키를 S1로 분리한다. 기존 실코드·다른 위치·해소 불명 레코드가 하나라도 섞이거나 대응 레코드가 없으면 귀속 키 전체를 유지한다. `unmatched_lines` 및 실행 불능은 생성 면제 근거가 아니다. #566은 계속 제외 대상 밖이다.

같은 귀속 키의 두 레코드가 모두 생성인 경우, 생성과 실물이 섞인 경우, 좌표가 빠진 경우를 실제 CLI 대조에 추가해야 한다. 원 registry exit·원 귀속 수와 분리 뒤 잔여·S1 수는 별도로 보고한다. `raw exit 2 + 설명할 귀속 없음`을 RunError로 보존한다는 계획은 타당하다. 이 보완으로 귀속 identity 자체를 개편하거나 G2 검사기를 약화할 필요는 없다.

## MAJOR A-P2 — F9의 annotation 좌표와 현재 생산자 진단 좌표가 다르다

- **계획 위치:** 155행 annotation AST identity 인터페이스, 161행의 `provenance+해당 annotation 위치`에 한정한 생성 helper #645/#647 S1 처분, 173행의 실제 checker와 생성 스텁 차등 검증.
- **현재 코드:** `check-public-surface-annotation.py:773`은 모든 함수 매개변수·반환 타입 진단의 위치를 `FunctionDef.lineno`로 만든다. 775~781행은 실제 annotation 시작 행이 아니라 같은 함수 def 행을 넘긴다. 789~791행은 `symbol`을 지정하지 않으므로 구조화 레코드도 `symbol=None`이다.
- **발생조건:** 생성 admin helper에 여러 매개변수나 반환 주석이 있고 일부 슬롯만 S1 대상인 경우다. multiline signature면 annotation 시작 행 자체도 def 행과 다르다. A-P1을 고쳐 원본 레코드를 받는 것만으로는 개별 annotation 슬롯이 자동 식별되지 않는다. `set[int]`의 AST 객체 identity는 checker 프로세스 밖의 레코드 identity로 사용할 수 없다.
- **독립 helper 증거:** 3행에 정의한 `_render_failed_submission`의 `extra_context: dict[str, object]`는 5행, `data: dict[str, Any]`는 6행이고 반환 타입도 따로 있다. 현재 `_check_explicit_any`는 서로 다른 세 진단을 모두 `file=...feature.py:3`, `symbol=None`으로 낸다. `extra_context`는 후보, `data`와 반환 타입은 위반이다. 따라서 def 행만 일치하는 필터는 어느 슬롯의 근거를 옮겼는지 증명하지 못한다.

**최소 기술 해결안:** 공용 Findings 스키마를 바꾸지 않고도 구현 가능하다. 원본 `record.file`의 def 행으로 생성 AST의 메서드를 고른 뒤, **현재 생산자가 내는 정확한 메서드·매개변수 label 또는 반환 label**을 그 AST 슬롯에 일대일로 연결하는 계약을 계획에 명시한다. 현재 문면은 `` `method()` 매개변수 `label` `` 및 `` `method()` 반환 타입 ``을 구별하고, 지역 AnnAssign은 `` `target` 주석 ``을 제공한다. 이 알려진 생산자 형식만 지원하고, 임의 자유 문구에서 context 역할을 추측하지 않는다. 정확한 슬롯이 하나로 해소되지 않거나 annotation 형상이 S1 대상이 아니면 원 진단을 유지한다. A-P1과 마찬가지로 같은 귀속 키의 레코드 중 비생성·다른 슬롯·불명이 섞이면 키 전체를 유지한다.

검증에는 한 helper 안의 열린 context 주석과 유지할 다른 bare Any, multiline signature, 같은 이름의 두 클래스 메서드, 반환 타입·매개변수 동시 진단을 넣는다. 실제 코드의 좁은 `_admin_context_exemptions`와 생성 스텁의 S1 처분을 구별한다는 방향은 유지한다. 새 입력 채널이나 admin 전체 면제는 필요하지 않다.

## 12건 전체의 구현 가능성 및 보존 경계

| 항목 | 계획과 현재 코드의 대조 판정 | 구현 검증에서 확인할 핵심 |
|---|---|---|
| F4-1 | **가능.** `PlanEntry`에 add/update 선언을 별도 보존하고 선택형 효과 블록을 도입하는 계약은 `_parse_symbols`의 update 클래스 유실과 `_parse_signals`의 비-add 폐기를 직접 다룬다. marker 무기재/빈 목록/완전 목록도 분리했다. | `main`까지 거쳐 update만 있어 실체화 0인 선언 모순이 exit 2·리포트에 남는지 확인한다. 단순 helper 결과만으로 이 분기를 증명하지 않는다. marker 추가·제거 후에도 class decorator/DB 증거는 유지하고, 무기재로 기존 module mark를 지우지 않는다. |
| F4-9 | **A-P2 보완 필요.** #493/#646/#650 유지, #645/#647의 framework 소유 슬롯·UI 조립·private 전달 helper 완화는 승인 범위와 맞는다. 실제 소비와 불명 escape는 면제하지 않는다. | 실제 override→private helper→UI 조립→render와 업무 소비를 함께 대조한다. 스텁은 흐름을 증명할 수 없으므로 근거가 해소된 슬롯만 S1에 남기고 G2가 실제 흐름을 재검사한다. |
| F4-10 | **가능.** 표준 composition import에서 반환 binding을 연결하고 builder 준비와 실제 execute를 구별하는 수정은 현행 문자열 계수 부위에 한정된다. | alias·inline builder·재대입·미호출 nested 정의·cursor와 실제 0/2회 실행을 대조한다. 정적 호출 수를 모든 분기의 실제 동적 실행 수로 설명하지 않는다. 별도 도메인 예외 속성 접근 #153은 유지한다. |
| F4-11 | **가능.** 직접 표준 Enum/StrEnum/IntEnum 출처와 닫힌 형태에 한해 #268 후보를 지우고 다른 VO 규칙을 계속 수행하는 범위가 명확하다. | `_missing_`·사용자 생성 동작·custom 기저/메타클래스·rebind·Flag는 여전히 후보다. 표준 출처를 이름만으로 대신하지 않는다. |
| F4-12 | **A-P1 보완 필요.** 생성 provenance만 S1로 옮긴다는 방향과 #566·기존 실코드 보존은 맞지만 현재 반환 인터페이스로는 정확한 위치 대조가 불가능하다. | 수정 후 실제 pre-gate/registry CLI에서 생성-only 0+S1, 실제 잘못된 본문 2+#376, 실제 robust 누락 #566을 확인한다. helper 증거로 CLI 완료를 대신하지 않는다. |
| F4-13 | **가능.** #555를 약화하지 않고 이미 잡은 IntegrityError의 내부 정규화와 외부 safe 500을 여섯 직접 문면에 같은 의미로 반영한다. | 일반 repository 실패의 domain 소유와 capability port 실패의 port 소유, 선언된 계약 예외의 재던짐을 보존한다. 새로운 catch-all·HTTP schema는 범위 밖이다. 코드 변경 없이 규범 시나리오 대조로 검증한다는 분류가 맞다. |
| F4-14 | **가능.** 지역적으로 식별한 표준 UoW·외부 atomic 구간, 중첩 합산, 비-UoW with·불명 경계의 후보 처분을 계획이 구별한다. 전역 트랜잭션 분석은 요구하지 않는다. | 확정 위반뿐 아니라 후보도 검사해 미지 경계를 조용히 통과시키지 않았는지 본다. 함수 단위 binding 수집도 nested scope를 침범하지 않아야 한다. 현행 `_repo_bindings`가 suffix 이름을 대리 지표로 쓰는 한계를 import 출처·인스턴스 identity 증명으로 광고하지 않는다. #550/#257 회귀 대조를 유지한다. |
| F4-15 | **가능.** 비교식의 left+comparators 전체를 대상으로 명시 domain/vendor/불명을 구별한다. 기존 왼쪽 속성명만의 #557을 정확히 겨냥한다. | domain 예외가 except에 묶여도 정상이어야 하고, vendor RHS·chained 비교는 확정이다. 재대입과 알 수 없는 외부 SDK/반환값은 후보다. 외부 모듈 전체를 vendor로 간주하지 않는다. |
| F4-16 | **가능.** #642 방출과 승격 술어의 50행 조건 자체를 폐지하고 #643/#644·다른 형태 규칙을 남긴다. registry identity 수리로 대체하지 않았다. | 1~49행 정상 부품의 #642 없음과 부품 0·본체 누락·중첩·정크드로어·201행의 기존 진단을 분리 검증한다. TTL·현재 대장·생성원·미러 전파가 계획에 있다. |
| F4-17 | **가능.** 캐시 흔적뿐인 선택적 인스턴스라는 술어, 숨김 실파일·symlink·읽기 오류의 보수 처리, 캐시 제거 전 snapshot 경계가 포함됐다. | 현재 `_snapshot_current`가 캐시를 지운 뒤 빈 부모를 남기는 경로도 대조한다. 실제 미추적 소스·빈 `__init__.py`와 고정 골격을 유지해야 한다. 빈 폴더 일반 면제·원본 삭제는 요구하지 않는다. |
| F4-18 | **가능.** `(절대 모듈, 심볼)` identity와 명시 imports/alias/실물 선언을 써 Result/Response에서 보조 DTO·컨테이너를 탐색한다. bare 동명 타입을 확정하지 않는다. | update 후상태·실체화 0에서도 직접/중첩 aggregate·entity 오염이 선언 채널에 남는지 확인한다. VO·동명 다른 DTO·Literal·TYPE_CHECKING 충돌·cycle의 반대 대조가 있다. DTO 소비만으로 OHS domain import를 합성하지 않는다. |
| F4-19 | **가능.** 기본 HEAD 초기 실행과 명시 `--base` 재예보의 현행 거절·lifting 정책을 그대로 두고 baseline 실존과 overlay 실존 오류를 나눈다. | 계획의 12조합은 exit뿐 아니라 실제 CLI·리포트의 모드/원인 문구를 대조해야 한다. 작업 기록의 역할을 안내하고 docs·비-Python 전부를 금지하거나 `--base HEAD`를 초기 실행의 무조건 우회 처방으로 만들지 않는다. |

F1/F18의 선언 확정·선언 후보는 실제 registry 차분과 별도 근거이므로 리포트에서 합산 근거를 드러내고 `--check-report`가 누락된 확정 처분을 통과시키지 않아야 한다. 같은 rule+path의 여러 선언 근거를 묶어 모두 보존하고 후보를 `filtered` 처분과 섞지 않는다는 계획이 이를 다룬다. 새 효과 블록이 없을 때 종전 hash 알고리즘을 보존하고, 있을 때 새 원문을 포함한다는 계약도 현재의 캐시 입력과 맞는다.

F14의 외부 호출자·ATOMIC_REQUESTS·간접 helper 전체를 추가로 증명해야 한다는 요구는 하지 않는다. 계획이 명시한 국소 정적 지원과 불명 후보를 그대로 유지하면 된다. F18에서도 별도 import 없는 OHS 소비에 확정 #95/#96을 추가하거나 전체 Python 타입 시스템을 구현할 필요는 없다.

## 증거와 수행 한계

- scratch: `/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/dddjango-f4-plan-A-o69m9x_6/`.
- `reviewed-plan.md`는 위 SHA의 최초 계획 사본이다. `probe.py`, `introduced.json`, `results.json`은 A-P1/A-P2의 독립 helper 증거다.
- `python3 -B .../probe.py` exit 0. 진단 정규화·sidecar 집합·반환 운반 대조 7개, annotation 좌표 대조 5개, 읽은 원본 스크립트 4개의 byte 해시 보존 대조 1개가 통과했다.
- `_write_introduced`와 `_check_explicit_any`는 실제 helper를 실행했다. `run_gate`는 반환 데이터 운반만 확인하려고 `subprocess.run`을 고정 응답으로 대체했다. **전체 registry CLI, pre-gate CLI, make verify를 실행한 증거가 아니다.** 계획 리뷰에 필요한 위치 계약만 재현했다.
- 실제 spring_dream_server에서 검사기·테스트·코드를 실행하지 않았다. 코드·규범·영구 테스트·계획·원 보고서는 수정하지 않았고 추가 위임도 하지 않았다. 유일한 영구 출력은 이 리뷰 파일이다.
- Serena/Graphify는 opt-in 부재 지시에 따라 검색·로드·초기화·호출하지 않았다.

**최종 집계: B/M/m = 0/2/0. 추가 사용자 결정 필요 없음.** 두 보완의 기술적 해결 가능성은 확인했으며, 개정 계획에 반영됐다는 최종 판정은 개정본을 다시 읽은 뒤에만 할 수 있다.

## 2026-09-11 개정 계획의 A-P1/A-P2 재대조

재대조한 계획 SHA-256은 `a3b0ebb2b309f901afc20d48adee8252e46b1f9cb7ab363c3503b64f82b317c8`이다. 최초 계획 대비 diff와 개정본 114~179행을 읽고, 위 두 지적의 반영 및 그 변경이 만든 모순만 확인했다. 다른 리뷰의 변경을 새로 전수 심사하거나 구현을 실행한 결과가 아니다.

| 지적 | 처분 | 개정본의 근거 |
|---|---|---|
| A-P1 — 정규화 뒤 위치 정보 유실 | **ADDRESSED** | 120행이 `attributed_lines`와 원본 `records`·`unmatched_lines`·candidate 채널을 raw exit/stdout과 함께 운반하며 `record.file` 끝의 숫자 행을 사용하도록 정했다. 122·131행은 전체 registry 정규화 키의 모든 레코드를 대조하고, 혼재·불명·무대응·unmatched이면 키 전체를 유지한다. 132~133행은 실행 불능과 원 결과·S1 보고를 보존하며, 148행에 생성-only/혼재/행 누락 대조가 있다. |
| A-P2 — annotation 슬롯과 def 행 혼동 | **ADDRESSED** | 159행이 AST identity를 같은 checker 프로세스의 정책에 한정한다. 166행은 원본 def 위치와 생산자의 정확한 method/param/return 또는 AnnAssign label을 생성 AST 슬롯에 일대일로 결합한다. 해소 실패·다른 슬롯·비생성 혼재는 유지하고, 원래 candidate_records도 S1 근거를 report/check-report에 남긴다. 169행에 multiline·별도 payload/bare Any·동명 메서드·반환+인자의 CLI 반대 대조가 있다. |

A-P1의 원본 레코드 운반과 A-P2의 슬롯 식별은 서로 연결되며, 함수 def 행을 annotation 시작 행으로 오인하거나 프로세스별 AST identity를 외부 식별자로 사용하는 모순이 개정본에 남지 않았다. 후보를 확정 위반으로 올리거나 생성 진단 전체를 파일 단위로 면제하는 새 계약도 이 수정에서 발견하지 않았다. 공용 Findings 스키마나 기존 귀속 identity 개편 없이 구현할 수 있는 최소 보완이다.

**현재 미해결 B/M/m = 0/0/0. A-P1/A-P2 모두 ADDRESSED. 추가 사용자 정책·범위 결정 필요 없음.** 최초 리뷰의 0/2/0은 이력으로 보존한다. 이 재대조는 계획 단계의 두 지적을 닫은 것이며, 계획에 적힌 CLI·처분·진탐 보존 검증은 구현 단계에서 수행해야 한다. 코드·규범·영구 테스트·계획·원 보고서는 수정하지 않았고, 이 파일 끝에만 결과를 추가했다. Serena/Graphify는 opt-in 부재로 사용하지 않았다.
