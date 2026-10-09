# dddjango 2.19.3 — scope 렌더 앵커 재실행이 앵커에 없는 BC 이름 selector 를 걷는다 (운영자 · 10-10)

## 바탕
- 바탕: R main `6090d3c5`(dddjango 2.19.2 + dddjango-web 2.2.4). 패치(검사기 27종 · 로스터 · 트리 · 규범 그래프 그대로).
- 사본 `<S>/core-2193`(가지 `core-2193`). `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 근거 기록 `<S>/core-2193-notes/`(진단 · 계획 · 설계 점검 · 구현 · 구현 검토 · 실제 장면) · 재현 사본 `<S>/f67/sd`(레인 커밋 `3dd7fe241`).
- 현장 보고 F4-67(10-10 · spring_dream 서버 레인 admin-4-1): main 합침 `32d6d6d00`(앵커에 없던 `fortune_tarot` 유입) 뒤 승인 inventory 로 렌더한 #15 `check-api-error-controller-contract --anchor de10a4ea6` = exit 2 · 신규분 11 · 기존분 7. 신규 11 은 모두 앵커부터 무변인 `review_controller.py`. 합치기 전 같은 렌더 = exit 0 · 기존분 18.
- 사용자(글자 그대로): admin-4-1 처분 «그럼 문제 보고서 적어줘. 그럼 내가 프로젝트에서 수정할게. 수정할때까지 멈춰있자.»(10-10 02:48:28 · 발주자 기록) · 운영자에게 «워크트리에서 발생한 오류 보고야 확인하고 절차대로 수정진행해서 배포해줘»(10-10 03:36:46 date 뒤 · 03:47:42 date 앞).

## 판정 — 뿌리
- `anchor_diff._baseline_argv` 가 앵커 재실행 argv 에서 앵커 트리에 없는 **경로** selector 만 걷고 **이름** selector `--scope-bc` · `--error-bc fortune_tarot` 은 남겼다 → #15 가 그 이름을 `application/fortune_tarot/driving_layer/api/bc_error_schema.py` 필수 source 로 풀어 «production source 없음» 사용 오류(exit 1) → `partition_exit` 가 positional/auto 기준선으로 강등 → code-profile 계약 진단 11 이 기준선에 없어 «신규».
- 배포판 2.19.2 로 같은 입력에서 재현(exit 2 · 신규 11 · 기존 7 · positional 강등) — 레인과 같음.
- registry_gate · design_pregate 는 이름 selector 를 넘기지 않아 같은 결함 없음. 상위 계약 R-0369 · R-0370 을 정상 작동시키는 구현 수리라 새 R 번호 · 재투영 · rulepack 없음.

## 넣은 것
- `anchor_diff._baseline_argv`: `--scope-bc` · `--error-bc`(분리형 · `=`형)의 이름 B 를, 앵커 스냅숏의 `application` 이 실제 디렉터리이고 `application/B` 의 lstat 이 FileNotFoundError 일 때만 걷는다. 빈 폴더 · 같은 이름 파일 · 링크(정상 · 끊어짐 · 순환) · 상위 이상(없음 · 파일 · 링크 · ENOTDIR · 권한 · 그 밖 OSError)은 유지 · 대소문자 보정 · area 탐색 없음 · 두 플래그 · 반복 출현에 같은 판정 · 순서 · 중복 보존.
- #2 · #5 · #15: `--anchor-baseline` 에서만 빈 `--scope-bc` 집합을 받는다(일반 실행 계약 · 이름 문법 · 중복 · 부분집합 무변 · 조기 반환 없음).
- docstring 보장을 «앵커에 없는 정규화 진단문은 신규로 남는다»로 좁힘.
- 소성물 `pregate_symbol_kinds.json` 재소성(검사기 source_sha) · Codex byte 미러 · 봉인 재발행.
- 시험 `anchor_diff_smoke.py` 30 사례(argv 전체 비교 · 링크 · 상위 이상 · 세 검사기 × 두 profile · 정상 tree 빈 scope 분석 · 분류 문자열 집합: 기존 BC 새 위반 · 새 BC 위반 · 첫 wire 충돌 · 공통 schema 변경 → 신규 · 알려진 한계 고정).

## 멈출 기준과 결과
| 기준 | 결과 |
|---|---|
| S1 실제 장면(사본 `3dd7fe241` · 레인 인자 그대로) #15 | 2.19.2 exit 2 · 신규 11 · 기존 7 · positional 강등 → **exit 0 · 신규 0 · 기존 18 · 빚 0 · «selector 렌더 재실행»** · 기존 18 = 고치기 전 신규 11 + 기존 7 과 글자 동일 · 차분 앞 출력 1 ~ 62행 byte 동일 |
| S2 같은 장면 레인 G2 명령 27종(2.19.2 ↔ 고친 판) | #15 만 exit 2 → 0 · 나머지 26종 종료 코드 · 출력 같음 |
| S3 시험 · 게이트 | anchor_diff_smoke 30/30 + 14/14 · registry_gate_smoke 24 + 42 · verify-base-cross 347행 차이 0 · verify-base-backstop 714/714 · `make verify` 5/5 green(370초) · `make verify-mutation` 12/12 |
| 설계 점검 · 구현 검토(Codex) | 설계 «보완 후 진행»(부재 판정 엄격화 · 보장 문구 · 시험 · 봉인 순서 · 릴리즈 창) 반영 · 구현 검토 «통과» |

## 알려진 한계
- 기존 wire 충돌에 소유자만 하나 더 붙어 #2 의 대표 진단문(첫 소유자 한 곳)이 같으면 그 추가 충돌은 기존분으로 남는다(시험으로 고정 · 소유자 · 멤버를 진단에 싣는 별도 수리 범위).
- 기존 BC 에 오류 스키마를 새로 들인 장면(BC 뿌리는 앵커에 있고 canonical 파일만 없음)은 이름을 걷지 않아 지금처럼 강등될 수 있다.
- 검사기를 직접 돌린 원 출력 · registry_gate 는 그대로다. 판을 올리면 `dddjango/scripts/` digest 가 바뀌어 진행 레인 pre-gate 가 «툴체인 stale» → 재예보.
- 릴리즈 창: DEVELOPMENT §6 은 G0 ~ G2 진행 레인이 있으면 보류지만, admin-4-1 이 이 판을 기다리며 멈췄고 사용자가 배포를 지시했다. 8-C-5 는 재예보가 든다.
- 미배포 2.20.0 패치: 새 R 번호를 쓰지 않아 번호 충돌은 더하지 않음(#2 · #15 · 봉인 · 소성물 파일은 겹침 — 다시 얹을 때 맞춤).
