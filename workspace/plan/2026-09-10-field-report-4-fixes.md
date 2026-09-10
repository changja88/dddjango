# 현장 보고 4차 추가 결함 수리 계획

승인 범위: 사용자의 “좋아 끝까지 진행해줘”. 문제 증거 → 문제 리뷰 3인 → 계획 리뷰 3인 → 회귀 Red → 구현 → 구현 리뷰 3인 → 최종 감사/검증 → 커밋 → make release 순서다. 현재 릴리즈는 dddjango 2.18.1(170fd77175a7736e619268200c7ca1b821342043).

## 증거와 판정

보고서: workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md. 조사 시작 사본 SHA-256 `8304ddfd396953f187f884b790cc9fa2692d1786457a55479f2b764d0b8f1a8a`, /tmp/dddjango-field-report-4-u678ff_3/source-report.md. 보고서의 갱신으로 F4-8까지 8항목과 #389 부속 후보, 총 9개를 대상으로 고정했다. 원 보고서와 사용자 프로젝트는 수정하지 않는다.

| 항목 | 판정 | 처분 |
|---|---|---|
| F4-1 #483 | 명시된 S5 한계. update OHS 신규 함수가 사본에 없음 | 신규 함수의 명시 전사로 S5 범위를 좁힌다 |
| F4-2 무응답 G1 | 기존 승인 원칙 위반을 막는 입력 실패 분기 공백 | 미결정 상태·대기·상위 도구 계약 fallback 명시 |
| F4-3 #456 | S5 한계. 최신 현장 보고는 이미 filtered | 신규 OHS 함수와 함께 명시 exception-map 전사 |
| F4-4 #107 | 빈/docstring API 골격을 실내용으로 세는 오탐 | 기존 skeleton_placeholder 판정을 적용 |
| F4-5 #93 exit | 결함 아님. helper 반환 None과 CLI 판정 혼동 | 변경 없이 종결. 실제 CLI 위반 2/정상 0 확인 |
| F4-6 무조건 삭제 | #195의 예외 아님. 현재 정책 배치 안내 공백 | 현재 항상 허용하는 삭제 정책도 루트 소유라는 좁은 안내 |
| F4-7 #571 Failure | 클래스 이름만으로 실패 반환 확정하는 오탐 | 이름만의 신호를 의미 리뷰 후보로 낮춤 |
| F4-8 앵커 | tree 조기종료로 baseline code-profile 진단 누락 | baseline 전용 완전 수집, 일반 실행 조기종료 보존 |
| #389 부속 | 첫 code span/file.py::case를 파일 키로 쓰는 숨은 제약 | 정확한 단일 artifact 파일 주소 식별 |

문제 리뷰: pregate_plan_remove(F1/F3/#389), pregate_plan_symbols(F4/F5/F7 및 F8 반증), pregate_problem_norms(F2/F6). F8 루트 최소 재현은 기존 tree #648 1건+code 3건을 가진 임시 Git 저장소에서 무해 변경만 추가: 현행 exit 2, 신규 3·기존 1(/tmp/dddjango-field-report-4-u678ff_3/f8-red-mixed-anchor.log). 기대는 신규 0·기존 4/exit 0. tree 없이 code만 있는 음성 대조는 현행도 기존 3/exit 0.

## 1. pregate 전사 범위

`design_pregate.py` 및 byte 미러. checker에 계획 이름을 주입하거나 규칙을 면제하지 않고 사본에 명시 재료를 전사한다.

- update 지원은 open_host_service의 실제 서비스 파일(표준 경로/승격된 실물 경로 확인)에 한정하고, symbols에 명시된 모듈 함수 중 현재 모듈에 없는 이름만 추가한다. 기존 함수·클래스·별칭·본문은 바꾸지 않는다. 파일 부재/승격된 다른 물리 경로/미명시 함수는 S5 미시뮬레이션으로 남긴다.
- 명시 boundary-imports는 이름 충돌 없이 추가 가능한 것만 허용한다. 기존 바인딩을 다른 출처로 덮거나 미래 import 위치를 깨지 않도록 한다. 안전하게 전사할 수 없는 entry는 전체 미시뮬레이션과 사유를 남기며 선언만으로 성공 처리하지 않는다. 합성 전체를 compile 검사한다.
- exception-map은 해당 update 서비스에 실제로 새 함수가 전사된 경우에만 기존 add와 같은 파일 수준 raise helper로 옮긴다. 함수별 raise 위치를 알아냈다고 주장하지 않는다(채널은 파일 주소뿐이다). 기존 함수 변경만으로 새 raise를 추론하지 않으며 contract 내부 raise 진탐은 남긴다. 충돌하는 helper 이름도 덮어쓰지 않는다.
- 새 함수가 없는 update, 기존 함수 signature/body 수정, decorator/alias/class update는 계속 S5다. materialized 목록에는 변경된 서비스 파일, unsimulated에는 남은 update 범위를 함께 기록한다. 실제 사용자 파일 byte는 불변.
- #389 owner/path 셀은 code span과 bare token에서 Python artifact 주소를 찾는다. `.py::case`의 파일 부분을 정확한 file-plan 키에 결합한다. 앞선 `add` 같은 span은 건너뛴다. 행에서 처음 나오는 Python 파일 주소가 그 행의 owner artifact라는 문법을 명시하고, 뒤의 support·coverage 주소에는 신호를 전파하지 않는다. 첫 주소가 미등재여도 뒤의 등재 파일로 건너뛰지 않는다. 이로써 기존 주 테스트+support 파일 셀의 첫 artifact 동작을 보존한다. 미등재/비-add/marker 없음은 계속 미반영.
- 회귀: 올바른 새 OHS operation으로 #483 해소, 틀린 이름/시그니처는 진탐; 명시 서비스 raise만 #456 해소, contract에서도 raise하면 진탐; 기존 본문/바인딩 보존, 동명/미명시/충돌/부재/승격/비OHS는 한계 보고; #389 bare·nodeid·선행 span·marker 양순서/주 artifact+support 주소/미등재 첫 주소/신호없음 대조.

## 2. 검사기 정확도

- F4-4 `check-composition-root.py`: `_has_concrete_api_surface`가 router/controller Python 파일에 skeleton_placeholder를 적용한다. webhook은 재귀하는 실제 Python 내용이 있을 때만 활성 신호로 쓴다. 실제 controller와 빈 router, 프로젝트가 registrar를 명시 사용한 경우의 #107은 유지한다. 경로 규칙을 전역 면제하지 않는다.
- F4-7 `check-usecase-dto-placement.py`: 공개 클래스 2개 이상이라는 기존 #571 blocker는 유지. Error/Failure/Exception 이름만은 Candidates로 이동하고 “도메인 명사인지 실제 실패 반환인지”를 discipline-reviewer가 판단하게 한다. error/code/outcome 필드 휴리스틱이나 범용 반환 분석기를 추가하지 않는다. 이름만으로 잡던 진탐도 후보가 되는 검출력 경계를 명시한다. tree-revision-spec의 #571 등급을 ast+로, 대응 술어에 후보·물음을 추가하고 소유 지도를 재생성한다. findings_count_matrix와 checker_baseline_matrix의 해당 출력/종류 골든만 갱신한다. 성공 RecordFortuneFailureResult와 단일 실제 OperationFailureResult 모두 blocker 0·후보 1, 공개 클래스 2개는 blocker 유지가 기대다.
- F4-8 `check-api-error-controller-contract.py`: Config 끝에 기본값 false인 anchor_baseline을 보존. baseline에서는 tree/code 모두 같은 selector와 overlap suppression으로 수집한다. baseline의 마지막 판정은 collected 유무에 따른 local 2/0, analysis 존재 시 1이며 partition_exit를 재귀 호출하지 않는다. 일반 무-anchor의 기존 tree 선점/출력/exit를 보존한다. git target에서 baseline flag 거절도 유지한다.
- F8 회귀: old tree+old code는 기존분만/exit 0, 새 code와 새 tree는 신규분/exit 2; tree-only/auto/code-only/empty baseline; selector 부재·분석 오류·git baseline 금지·빚 채널 보존. 실제 현장 로그와 같은 selector 재실행을 source 읽기 전용으로 대조한다.

## 3. 규범과 입력 채널

- F4-2 공통 graph-owned 승인 규범 R-0157/R-0450/R-0456 중 필요한 소유 문단만 개정하여 명시 사용자 응답 없이 종료된 unanswered/빈 답/timeout/auto-resolve/UI 닫기와 미제출 기본 선택은 결정이 아님을 명시한다. 실제 사용자가 기본 옵션을 확정한 응답은 유효하며 명시 거부·수정·작업 취소는 그 입력대로 처리한다. 유효한 명시 승인 또는 해당 게이트를 포함하는 사전 위임만 결정 근거다. 무응답 자체는 그 근거가 될 수 없다. 사전 위임도 R-0451/R-0452의 STOP·blocker·shape·사후 scope 개정 제외와 최신 사용자 범위의 적용을 받는다. Codex의 게이트/STOP 입력 절을 함께 정합화한다. 도구 목록 부재·이미 확인된 미지원·명시된 상위 승인용 사용 제한이면 호출 없이 평문으로 대기한다. 사용이 허용되고 미지원 근거가 없으면 정상 도구 경로를 쓰며, 실제 미지원 오류나 답 없는 종료가 발생하면 원인을 기록하고 fallback한다. 답 없이 도구가 닫혔으면 메인 대화에 미결정 상태를 알리고 실제 사용자 입력을 기다린다. TUI 타이머를 고쳤다고 주장하지 않는다.
- F4-6 architecture-ddd-final의 도메인 판정 소유 문단에 현재 삭제 정책의 명시적 소유 안내를 둔다. 애그리거트 쓰기 모델에서 load→부재 처리→삭제 정책 행위→remove(root). 제품 결정이 현재 항상 허용이면 그 정책도 표현할 수 있으나 미래 확장만을 위한 빈 메서드/새 조건/이벤트는 만들지 않는다. 정책 메서드의 단순 반환값만 확인하는 테스트를 일괄 요구하지 않는다. #195 자체의 예외/판정은 변경하지 않고 인접 Work를 #195 정본이라고 잘못 기록하지 않는다.
- F1/F3/#389는 agent-design-architect s005의 R-3426(symbols), R-3427(imports), R-3428/R-3429(physical signals), R-3430(exception-map) 중 변경 의미를 소유한 Work를 새 Expression revision으로 개정, Claude 재투영 및 Codex 의미 미러. references는 corpus_mirror_sync. 변경 절 LEDGER append, ExpressionShape 기대수와 rulepack 재소성.
- writing-skills 적용: 기존 현장 실패를 baseline 증거로 보존한다. 수정본을 적재한 독립 실행에서 다음 행동을 고르게 하고 원 출력과 dispatch 여부를 기록한다: 무응답+시간압박→대기, 실제 기본옵션 확정→진행, 명시 작업취소→중단, 상위 도구 승인용 금지→호출 0+평문, 위임된 일반 G1→범위 안 진행, 위임+STOP/shape 변경→정지. 삭제는 현재 항상허용 정책→루트 행위→remove, 실제 guard→보존, 검사 통과만 목적의 무관 메서드→거부를 대조한다. 정적 토큰 검사와 실제 다음 행동 선택의 증거를 구분하며 TUI timeout 자체 재현이나 장시간 대기 증명으로 보고하지 않는다.

## 4. 검증과 마감

- 기존 테스트 도구에 회귀 추가를 우선하며 필요한 묶음은 workspace/tools 아래 하나로 만들고 make verify 및 manifest 봉인에 연결한다. 수정 전에 각 결함의 실패를 기록한다. Findings/Candidates는 defer=True, subprocess sink는 temp 격리.
- 계획 리뷰 3인(전사·검사기·규범)에서 BLOCKER/MAJOR 해소 후 구현. 구현 리뷰 3인도 같은 원칙. 최종 감사는 독립 재검토로 범위/규범/진탐/미러/검증 증거 확인.
- 기존 pregate/API/anchor/fixture matrix를 포함한 관련 검증, make verify-mutation, 봉인 재발행 뒤 마지막 make verify green. 검증 실패 후 변경하면 봉인과 전체 verify 재실행.
- docs/master.html 등 무관한 시작 변경은 보존·커밋 제외. 원 현장 보고도 수정하지 않는다. 릴리즈의 clean 조건에 필요하면 정확한 경로만 임시 보관 후 byte 대조 복원한다.
- 수정 커밋 후 make release를 실행하고 1) patch를 선택해 2.18.2 발행(Claude plugin strict validate, 두 manifest 버전 정합 및 Codex manifest 구조 검증, remote HEAD/tag/GitHub Release 확인). 설치 cache를 몰래 갱신하지 않는다. 결과에서 수정/정상 동작/남은 S5 경계를 구분한다.

## 진행 기록

- 문제 증거 및 독립 3인 리뷰 완료. 계획 초안 작성, 아직 구현 전.
- 계획 리뷰 반영: 무응답 UI와 명시 사용자 결정 구분, 사전 위임 제외 유지, 첫 Python artifact 주소 규약으로 기존 support 주소 호환 보존, #571 ast+ 소유 문서/골든, 독립 실제 행동 선택 검증 기준을 구체화했다. 검사기 관점 BLOCKER/MAJOR 0.

- 계획 리뷰 3인 최종 통과: 미해소 BLOCKER/MAJOR 0. 구현 진입. 프로젝트 절차에 맞춰 개발 기록은 이 계획에 보존하며 subagent별 중간 커밋 대신 최종 전체 verify 이후 통합 커밋한다.

- 구현: pregate 신규 회귀 11 tests에서 수정 전 21 subcase 실패 후 green. 승격 물리주소 전사는 scope 재확인에 따라 제외(해당 음성 대조 Red→Green). 기존 전사 15 tests와 pregate fixture 전체 통과. /tmp/dddjango-field-report-4-u678ff_3/task-1-report.md 및 task-1-red.log/task-1-green.log.
- 검사기 회귀 10 tests green. 현 HEAD 2.18.1 스크립트 사본으로 같은 최종 테스트를 실행해 11 subcase 실패를 확인(checker-red-verified.log), 수정본은 checker-green.log. 최초 실행의 helper 반환형/import경로·명시 registrar fixture의 urls.py 누락은 테스트 준비 오류로 바로잡았으며 결함 증거로 세지 않는다.
- F7 골든 변경은 단일 이름 기반 #571이 violation→candidate로 이동한 결과: 기존 위반 fixture violation 35→34, candidate 5→6. 실제 복수 클래스 blocker 유지. 명세/술어/소유 지도와 집계도 ast→ast+ 1건만 갱신했다(소유 지도 전체 재생성의 무관 잔차는 제외).
- F8 실전 검증: B0 동일 selector/앵커 b1e0b343f3a19715533ff2c3ed922b398cb91532에서 exit 0, 신규 0·기존 18. 원 보고의 신규 11·기존 7 오분류 해소. 해당 review_controller.py의 앵커/현재/실행 후 SHA256 모두 18e88e6aa7f6a634ab431c91ccbfa3a8a44485c79d04b3c2e1701727c11e6d35. f8-field-green.log/f8-field-proof.json.
- F2/F6 행동 적용: 수정본을 읽은 별도 모델 실행 2개가 G1 6조건·삭제 3조건의 다음 행동을 선택. 무응답 wait/실제 승인 dispatch/명시 취소 stop/상위 금지 시 호출 0·평문/일반 G1 위임 dispatch/shape STOP wait; 무조건 정책 행위 경유/실제 guard 보존/무관·미래전용 호출 거부 모두 기대 일치. gate-behavior-output.md/delete-behavior-output.md. 이 값은 시나리오의 행동 선택이며 실제 coder 호출·TUI 타이머·장시간 대기 실행 증거가 아니다.
- 정본 Expression 8개 개정, Work/Block 추가 없음. 3문서 재투영, Codex 의미/byte 미러, LEDGER 4절 append, rulepack 및 symbol kind 재소성, 렌더 sync 541절 red 0.
- 구현 리뷰 보완: 새 함수 기본값의 대입식이 기존 모듈 이름을 덮을 수 있다는 MAJOR를 발견하여 args/returns의 NamedExpr가 있으면 entry 전체를 S5로 유지한다. 회귀 Red 2 tests/5 assertion failures → pregate 13 tests green. 일반 None·정수·문자열 기본값은 통제된 fixture 실행에서도 보존(task-1-signature-red.log/task-1-signature-green.log).
- F6 리뷰 보완: hard delete로 범위를 명시하고, 현재 승인 계약에 유효한 guard만 보존하며 승인으로 종료된 옛 guard를 복구하지 않도록 교정했다. 종료된 guard가 코드에 남은 네 번째 독립 행동 조건도 기대 일치(delete-behavior-output.md §4).
- 규범 개정의 직접적인 동기화 장애도 수정했다. 최신 LEDGER baseline은 현재 렌더의 주소인데 corpus 동기화가 이를 동결 소스 원문의 주소로만 쓰고 있어 inv1 구조 오류가 발생했다. 기존 migrated_sha256과 최신 baseline의 해시 집합에서 소스 스팬이 정확히 하나일 때만 허용한다. 동결 원문/최신 기준선 원문/미승인 변형/복수 스팬 4조건의 회귀 Red→Green, 전체 checker 회귀 12 tests green(checker-final-green.log). workspace/reference 원문 변경 없이 Codex reference만 동기화했고 corpus 11/11, render-sync 541절 red 0. rulepack도 최종 문구로 재소성했다.
- 실제 명세 전체 registry 재실행: 원 레인 기준 커밋의 git archive를 임시 저장소로 만들고 현재 명세를 고정한 사본에서 실행했다. A9는 #483 소멸, #160/#484 2건 잔존(exit 2); 해당 명세의 symbols 채널에 보조 dataclass decorator가 없으므로 임의로 보충하지 않았다. A11/A12는 예보 0·계약 실존 결손 0(exit 0). 세 원 명세의 실행 전후 SHA256 일치(replay-A9/A11/A12 각 proof.json). 실제 작업 폴더의 미커밋 overlay를 섞은 실행은 아니며 원 소스에는 쓰지 않았다.
- 구현 리뷰 3인 및 수정 후 범위 제한 재리뷰 완료: pregate_plan_remove(전사), pregate_plan_symbols(검사 판정), pregate_problem_norms(규범/동기화) 모두 미해소 BLOCKER/MAJOR/MINOR 0. 별도 최종 감사와 마지막 전체 검증 진입.
- 최종 감사 추가 발견: class 본문의 global 선언이 실제 모듈 이름을 바인딩하는데 기존 표면 수집이 이를 놓쳤다. ClassDef 안에 Global이 있으면 entry 전체 S5로 보류한다. 직접/조건부 class-global 2건 Red→Green, 일반 class-local 동명은 정상 전사 유지. pregate 회귀 최종 15 tests green(task-1-class-global-red.log/task-1-class-global-green.log).
- 첫 전체 검증은 통과하지 못했다(/tmp/djr-verify.Rl4RkT). cross census의 skeleton×composition-root 옛 #107 1건이 의도한 F4-4 수정으로 사라졌다. 정확한 fixture의 router/controller/webhook 파일은 빈 골격이며 HEAD checker exit 2/#107 → 수정본 exit 0을 별도 사본으로 확인(cross-skeleton-proof.json). --emit-expected 재생성도 347행 무변·해당 1행 소멸만 보고하여 그 행만 제거했다. regen은 동시에 추가하던 class-global Red 회귀를 실행했으므로 첫 실행을 최종 검증으로 쓰지 않는다. 모든 수정과 재리뷰 완료 뒤 봉인 재발행 및 전체 검증을 처음부터 다시 실행한다.
- 별도 최종 감사 field4_final_audit 통과: 미해소 BLOCKER/MAJOR/MINOR 0. class-global 수정 회귀를 독립 재실행했고, corpus의 산문+Codex 동시 drift write에서도 동결 graph 원문 보존을 별도 확인했다. cross 1행 변경, 정본 Expression/미러, 현장·행동 증거의 한계도 승인. 이제 최종 재봉인 및 전체 검증을 진행한다.
- 최종 검증 완료: 재봉인 후 `make verify` exit 0, 6/6 green, 211초. **마지막 실행 로그** /tmp/dddjango-field-report-4-u678ff_3/final-verify-2.log, 전체 /tmp/djr-verify.6Sh3xE. 신규 회귀 pregate 15 + checker/corpus 12 = 27 tests 통과. `make verify-mutation`도 11종 전건 검출(final-mutation.log); 이후 팩/selector 변경 없음. 첫 실패 실행 수치를 완료 근거로 사용하지 않는다. 수정 커밋 및 make release 2.18.2로 진행한다.
