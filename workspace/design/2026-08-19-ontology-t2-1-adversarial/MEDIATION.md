# T2-1 산출물 적대 검증 중재 기록 (2026-08-19)

> 대상: codex 4레인 — **L-P**(레코드 귀속 9) · **L-Q**(전략·동결 정합 7) · **L-R**(동작 보존 반증 4) · **L-S**(하네스 신뢰성 11) = **31건**.
> 방식: 확립 관례 — 발견 전건을 원문·실물 실측으로 대조 후 채택/부분/기각. ✔ = 이번 중재에서 재실측 확인.
> 결과: **채택 24 · 부분 채택 4 · 기각 0 · 범위 밖 등재 3** → 즉시 처분 6건 커밋(`f5dd51a`), 나머지는 아래 처분 계획대로.

## 즉시 처분 완료 (커밋 `f5dd51a`)

| 출처 | 결함 | 실측 | 처분 |
|---|---|---|---|
| R#1 (blocker) | `_emit` 무방비 `open()` — 레코드 경로 쓰기 실패 시 **27종 전부 즉사**(구판은 2종만). «라인 출력·exit 무변» 선언이 거짓이 됨 | ✔ 부모 부재 경로에서 exit 1·stdout 0·FileNotFoundError 재현 | **채택** — `OSError` 포착 → 프로세스 단위 sink 비활성+stderr 경고 1회. 수정 후 exit 2·stdout 4,395 byte 보존 실증(부모 부재·읽기 전용 양쪽) |
| P#6·R#2 (blocker/major) | `anchor_diff._run_lines`가 `DJR_FINDINGS_JSON`을 자식에 상속 → 부모 stdout에 없는 앵커 기준선 진단이 별도 run_id로 적재(기존분-only에서 정확히 2배) | 레인 실측 5종(62→124·5→10·3→6·10→20·20→40) | **채택** — 자식 env에서 제거. 내가 T2-1 중 «미처분 관찰»로 기록했던 항목의 독립 확인 |
| S#7 (major) | `checker_baseline_matrix`가 사용자 환경의 `DJR_FINDINGS_JSON`을 상속해 **사용자 실제 레코드 파일 오염**(544행·301KB append 실증) | 코드 확인(env 미지정) | **채택** — env 제거. 측정 도구가 관측 대상을 오염시키는 전형 |
| S#1 (blocker) | 두 하네스 `--emit-expected`가 검사 실패·레코드 전멸·앵커 파괴를 «새 정답»으로 출력하고 무조건 exit 0 | 변조 실증(`no-records`→`(2,0,0,…)` exit 0) | **채택** — red exit≠2 또는 레코드 0이면 생성 거부. 완전한 사유 강제(--reason-file)는 **부분**(운용 부담 대비 이득 낮음 — 커밋 메시지 규율 유지) |
| S#10 (major) | 로스터 완전성이 `assert`에만 의존 — `PYTHONOPTIMIZE=1`이면 소거돼 «26/26 일치» 세탁 가능. EXPECTED 잉여 키도 무시 | 변조 실증 | **채택** — 양방향 키 집합 런타임 검사+exit 1 |
| S#9 (major) | 두 하네스에 subprocess timeout 부재 → 검사기 정지 시 verify 무기한 정지 | watchdog 실증 | **채택** — 300초 timeout |
| Q#7·S#8 (blocker/major) | `findings_smoke.py`(라인↔레코드 1:1 재구성 오라클)가 **verify-base 미편입** — 더 강한 오라클이 존재하는데 release gate에서 안 돎 | ✔ Makefile 확인 | **채택** — verify-base 편입(D11 이행의 일부) |

## 설계 판단 — 수정 예정 (T2-1 보강 작업)

| 출처 | 결함 | 판정 | 처분 계획 |
|---|---|---|---|
| **P#2·3·4 + Q#1** (blocker×4) | **code-profile 레인을 통째로 `ContractFindings`(rule=null)로 처분해 실소유 규칙의 조인을 잃었다** — api-error `#62`(bare/broad catch)·`#126`(helper/factory/serializer) · error-central `#572` · composition `#107·#108·#109·#111·#440`. Q#1이 뿌리를 정확히 지목: 전략이 **«규칙 ID의 존재»와 «규칙 술어의 전 사건 커버리지»를 혼동**했다(#497의 단일 `composition_root.py` 사건·#63의 직접 선언 누락은 tree-slice에 도달하지 않고 rule-null 레인에만 존재) | **채택**(가장 무거운 발견) | category→rule 매핑표를 검사기별로 저작해 해당 category를 `SliceFindings(rule)`로 승격. 매핑 근거는 규칙 문면(tree-revision-spec)+owner-map 행을 전건 인용해 코드 주석에 남긴다. 진짜 계약 전용 category만 `ContractFindings` 존치. **계수 골든 EXPECTED 갱신은 검사기별 사유와 함께** |
| P#8 + Q#4 (major×2) | `symbol`에 실제 심볼이 아니라 category/사유 표지를 넣음(4종). 스키마는 «위반 심볼 이름»으로 정의 | **채택** | category는 `message`로만. 심볼을 아는 경우(함수·클래스명)만 `symbol`, 모르면 null |
| P#9 + Q#4 (major) | error-central 구조 blocker가 실제 경로가 있는데 `file="(code-profile)"` 고정 → 위반 그래프의 대상 파일 소실·regen `--filter-file` 침묵 제외 | **채택** | blocker를 파일·행 단위 레코드로 분해. 분류 표지는 target이 아닌 별도 자리로 |
| P#7 (major) | `check-synthetic-infra-exc`·`check-public-surface-annotation`이 행 번호를 `msg` 앞에 둬 `where`가 파일까지만(stdout은 `경로: :행`) | **채택** | `where=f"{rel}:{lineno}"`·msg에서 행번호 제거. stdout 보존이 필요하면 `SliceFindings(line=…)` 경유 |
| P#5 (blocker) | 21종의 대상-0 `#74` 가드가 stdout만 내고 **레코드 0**(조기 return이 공용 모듈보다 앞). 게다가 `#74`의 owner는 `checker_lint.py`라 target 검사기가 `#74`로 자기 위반을 내는 것 자체가 오귀속 소지 | **채택** | 공용 helper로 통일하고 **비수치 센티널**(예: `대상0`)로 레코드화 — `#74` 부여는 하지 않는다(오귀속 회피) |
| Q#5 (major) | `regen_loop_prototype`이 `--severity info`를 허용하면서 프롬프트는 ⓓ 후보를 «규칙 위반·수정·0 수렴 대상»으로 표현 | **채택** | 자동 수리 경로는 `violation` 고정(argparse choices 제한), info는 별도 검토 프롬프트로 분리 |
| Q#6 + S#2 (major×2) | 계수 골든이 전략 전환 위험 레인을 검증 못 하고, 필수 의미 필드(message·checker·expression·run_id/record_id/ts)를 위조해도 green. **line↔record 교차 불변식 부재** | **채택** | ① 레인 단위 픽스처 추가(#59 code·composition 단일 파일·openapi 직접 선언 누락·error-central code) ② canonical record payload 전건 단언+run_id 단일·record_id 유일·순서 ③ stdout↔record 대응 단언 |
| S#3 (major) | «violation_id 집합»이 집합도 ID도 아님 — 정렬 리스트라 중복 보존(8종에서 중복 실재), 동일 튜플 위반 교체가 탐지 불가 | **채택** | «multiset fingerprint»로 정명하고 occurrence 축(message 포함·서수) 추가 |
| S#4 (major) | baseline의 `parsed`가 registry_gate의 **실제 귀속 수**를 재현 못 함(게이트는 정규화 후 set 중복 제거 — 7/27에서 129→121로 축약) | **부분 채택** | 기대표에 «게이트 정규화 후 집합 크기» 열을 추가(현 raw 계수는 개작 회귀 검출 목적이라 존치). «registry_gate가 findings/0을 주 채널로 소비» 제안은 T2-3 루프 배선과 함께 재론 — **T2-3 등재** |
| S#6 (major) | 두 하네스가 **비-git 레인만** 검증 — clean git 저장소에서 7/27이 다른 exit/레코드 수 | **채택** | git 레인(clean tracked·modified·untracked)을 하네스에 추가하고 골든 분리 |
| S#5 (major) | `checker_cross_matrix`의 `FIND_ID`가 violation `[#N]`과 info `[ⓓ#N]`을 구분 안 함 → info를 규칙 위반으로 계수(13종에서 차이) | **채택** | 정규식 분리·충돌 판정은 violation만. **T2-1 범위 밖 기존 도구 결함이나 계수 의미 통일이 T2 측정 재료에 직결하므로 이번 보강에 포함** |
| R#3 (minor) | `check-usecase-dto-placement`의 uncaught `PermissionError` traceback이 행 이동으로 stderr byte 변경(exit는 양쪽 1) | **부분 채택** | traceback byte까지 계약에 넣지 않는다고 보존 주장 범위를 명시(문서). `_entries()` OSError를 «분석 오류» 문면으로 고정하는 것은 별도 개선으로 등재 |
| R#4 (minor) | 레코드 1건마다 open/close — 8,000건에서 2.428배(FD 누수는 없음) | **부분 채택** | 실런 규모(픽스처 수십~수백 건)에서 영향 미미하므로 T2-1에서는 미변경. **T2-5 대량 적재 전 lazy-open writer로 전환** 등재 |
| S#11 (minor) | 하네스에 검사기 사본 주입점(`--scripts-dir`) 없어 mutation test가 저장소 전체 복제 필요 | **채택** | `--scripts-dir`·`--fixtures-dir` 옵션 추가(변조 검증의 상시화 재료) |

## 범위 밖 등재 (T2-1 회귀 아님 — 별도 처분)

| 출처 | 사실 | 처분 |
|---|---|---|
| P#1 (blocker) | `check-layer-skeleton`이 `#393`·`#395`를 방출하는데 owner-map은 `check-business-vocabulary` 소유로 지정 — **양쪽이 같은 규칙을 낸다** | ✔ **개작 전(`ca5635d`)에도 동일** 실측(198·227행) → T2-1 회귀 아님. 소유권 정정은 owner-map·중복 검사 제거·양 검사기 픽스처를 함께 바꾸는 작업이라 **별도 트랙 등재**(레코드 채널이 드러낸 기존 결함 — 위반 그래프 이중 계수 원인이 되므로 T2-5 실런 전 처분 권고) |
| Q#2 (blocker) | `SliceFindings`가 동결 E8의 «통일 수단은 재저작이다 — 어댑터 한 줄이 아님» 봉인에 위배. 라인 재저작을 T3로 이월했는데 동결 T3 행에 그 작업이 없음 | **사용자 상정**(§6) |
| Q#3 (blocker) | 계획 편차가 §10-2 «충돌 시 작업 중단→개정 먼저» 대상. 개정 4는 수량 27종·선행 계약 이월만 승인했고 line caller-ownership은 미승인 | **사용자 상정**(§6) |
| Q#7 (blocker) 잔여 | D11의 «byte 골든 대표 8종»·«구판/신판 construct drift 리포트» 미이행 상태에서 T2-1 완료 선언 | **채택** — 완료 선언 철회. findings_smoke를 8종으로 확장+drift 리포트 생성 후 재선언 |

## 부록: 개정 5 반증 레인(L-T) 중재 — **개정 기각** (2026-08-20 · 자율 규약 R2 집행)

레인 T 12건(blocker 4·major 8) 전건 중재: **채택 10·부분 2·기각 0 → 개정 5 문안 기각·E8 무개정 유지·라인 채널 공용 포매터 재저작을 T2 안에서 완료**.

| # | 판정 | 요지 |
|---|---|---|
| T1 | 채택 | E8 원 처방(리뷰 G)은 «단일 출력 계약»이지 «지역 클래스 개수 0»이 아님 — SliceFindings는 그 본지를 회피 |
| T2 | 채택 | «재료 완성» 전제가 자기 문서(본 MEDIATION의 귀속 상실·#74 레코드 0·교차 불변식 부재 채택)와 모순 |
| T3 | 채택 | «T3 IRI 병기로 어차피 라인이 바뀐다»는 범주 오류 — E8의 IRI 재저작 대상은 **docstring**이지 stdout 라인이 아님(동결 어디에도 stdout IRI 요구 없음) |
| T6 | **채택(결정타)** | ✔ 재실측: (나) 비용의 «17,966행»은 파일 LOC 합계 오용 — 실제 5종 편입 diff 합계 ~372행·red 픽스처 출력 비공백 47줄. (나)는 소규모 작업 |
| T7 | 채택 | ✔ «앵커 스냅숏 재승인» 비용 실물 부재 — registry_gate는 같은 검사기를 양 트리에 대칭 실행(계수 기준선뿐·byte 스냅숏 없음) |
| T8 | 채택 | ✔ backstop은 `expected_fragment in output` 부분문자열 단언(674·6544행) — rule·메시지 보존 시 0/679 파손 |
| T9 | 채택 | §6 B암 고정은 rule-owner-map 스냅숏이지 stdout byte가 아님 — 포매터를 **T2-0b 동결 전** 통일하면 3암 공통 적용이라 교란 없음. T3 이월이야말로 A/B 검증 생산자↔최종 생산자 drift |
| T4·T5 | 채택 | T3 이월은 게이트·산정 없이 «작업 이름 추가»뿐이라 누락 재발 구조 — 기각으로 무의미화 |
| T10·T11 | 채택 | §8/§9와의 내부 충돌·§12 절차 미비 — 기각으로 무의미화 |
| T12 | 부분 채택 | 구현 클래스명을 동결 규범에 넣지 않는다(기각으로 자동 충족). 생산자 계약 정의 `{구조화 입력→단일 포매터→stdout+record 동시 산출}`는 **출력 계약 설계의 목표로 채택** |
| E7 | 반증 실패 | 배포 경계는 어느 쪽에도 차별 근거 아님 |

**처분**: ① AMENDMENT-5-DRAFT는 기각 기록으로 보존(발효 없음 — 블루프린트 무변) ② T2-1 보강에 **«공용 포매터 재저작» 단계 추가** — 출력 지점이 구조화 입력을 만들고 공용 포매터가 라인+레코드를 동시 산출(SliceFindings·ContractFindings의 line 인자 표면은 과도기 후 제거). stdout 문면 변경은 원계획 취지(접두 신설이 목적)이며 실측 비용: 기준선 EXPECTED 갱신(사유 동반)·backstop 0건·앵커 재승인 0건 ③ 포매터 출력 계약 설계는 귀속 매핑표와 **함께 선행 리뷰**(같은 판단표 묶음).

**자기 평가 기록(규약 취지)**: 개정 5는 저자가 자기 전략을 소급 정당화하려던 문안이었고, 반증 레인이 비용 과장(T6~T8)과 무근거 전제(T3·T9)를 기계 실측으로 깨뜨렸다 — R2(개정도 반증을 통과해야 발효)가 설계 의도대로 작동한 첫 사례.

## ~~사용자 상정 사항~~ → 자율 규약(개정 6) 발효 후 처분 완료

1. **T2-1 «완료» 선언 철회** — 유지. 공용 포매터 재저작+귀속 복원+하네스 보강+D11 후 재선언.
2. ~~동결 개정 5 상정~~ → **R2 절차로 처분 완료(2026-08-20)**: (가) 문안을 반증 레인 T에 회부 → 반증 성립(비용 과장·전제 무근거 실증) → **기각·(나) 채택**. 단 (나)의 실측 비용은 상정문의 «17,966행 재작업»이 아니라 **출력 지점 ~50곳·diff 수백 행 규모**임이 레인 T에서 확정됨(상정문의 비용 표기가 틀렸던 것). 상세 = 위 부록.
