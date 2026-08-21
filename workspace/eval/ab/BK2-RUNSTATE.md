# BK2 실행 상태 — O-5 delivery · claude 레인 (2026-08-21 준비 개시)

> **compact 대비 재개 좌표.** BK1 정본 = `BK1-RUNSTATE.md`·`BK1-RESULT.md`(측정 실패 블록 — 사용자 ⓑ«수리 후 잔여 15런» 결정).

## ⚡ 재개 요점 (최신이 맨 위)

**단계: 앵커 완성 — 기동 준비 완료. 남은 선행 = 메모리 대피(사용자 한 줄)뿐.**

| 확정값 | |
|---|---|
| 게이트 앵커 | `59ee1333` (앵커 커밋 — BC 116파일 삭제·스켈레톤 42·배선 1행) |
| 기동 HEAD | `c5ee05a0` (요청문 커밋 — 해시 순환 규약) |
| 발주문 | `docs/rebuild/delivery/request.md` (리터럴 게이트 1·1·0 ✅) |
| baseline | 직렬 전수 6,962 passed · 기존 red 4(main 동일·lessons) · **스텁 기인 red 16**(전수 = preflight ⑹·부속서) |
| 리셋 명령 | `git -C <타깃> reset --hard c5ee05a0 && git -C <타깃> clean -fdx -e .venv` — **`rm -rf .dddjango` 금지**(broccoli 는 .dddjango 일부가 git 추적 — rm 이 추적 트리를 깬다·실증됨). 재현 해시 `ad0aa0c5…` 2회 ✓ |
| 타깃 3개 | `~/Desktop/t2ab-R04·R05·R06` (브랜치 `ab/t2ab-R0N`, `c5ee05a0`) — 생성됨 |
| DB 분리 | 기동 env 에 `POSTGRES_TEST_DB=test_broccoli_r0N` (settings/test.py 지원 실측) — 동시 테스트 조건(O-4.md §2) |
| 클린룸 | graphify 훅 재빌드 후 옛 구현 언급 **0** 실측 · pycache 소거 · 부속서(O-5) 실측 병합 완료 |
| baseline 판형 주의 | `make test` 는 --maxfail=1, 병렬(-n auto)은 main 에서도 대량 에러(환경) — **판정·baseline 은 직렬 전수** `uv run pytest -q --tb=no -rEf --continue-on-collection-errors` |

**기동 직전 체크리스트**: ① 메모리 대피 확인(`ls …/memory` 부재) ② 각 타깃 리셋 명령 실행+`--tree-hash` 로 `ad0aa0c5…` 확인 ③ 암 영수증(`<설치본 2.15.1 scripts>/regen_core.py --arm-receipt <타깃>/arm.json` — env 3종 실은 채) ④ REQUEST = request.md 그대로(3판 byte 동일 확인) ⑤ herdr 워크스페이스 env = `DJR_LOOP_ENABLED`·`DJR_LOOP_SELECTOR`·`DJR_EXPERIMENT_RUN_ID`·`POSTGRES_TEST_DB` ⑥ claude 기동 = `claude --model claude-opus-4-8 --dangerously-skip-permissions`(전자동 — launcher 질문 No·No·Keep) ⑦ 감시 v6 판형 재기동(에이전트 t2ab-r04·r05·r06).

수리 3건 + 2.15.1 재릴리즈 완료(BK1-RESULT 수리 목록 전건 종결).

| 항목 | 상태 |
|---|---|
| 배정 | BK2 = **R04(C)·R05(A)·R06(B)** · O-5 · claude · 병렬(§11.1) |
| 봉투(개정 5) | herdr 워크스페이스 · **claude = Opus 4.8 + 전자동(auto mode)** · (codex 레인은 BK3부터 = sol·xhigh) |
| 앵커 워크트리 | `~/.herdr/worktrees/broccoli-server/ab-t2-delivery-anchor` (브랜치 `ab/t2-delivery-anchor`, main=8b70c471 에서 분기) — **생성됨·저작 진행 중** |
| 메모리 대피 | **사용자 실행 대기** — 분류기가 mv 차단(2회·우회 안 함). 대피 전 실측 = 봉인 스냅숏 `b80b1b17` 과 **정확히 일치**(무변·10파일). 명령: `mv ~/.claude/projects/-Users-hyun-Desktop-broccoli-server/memory ~/.claude/projects/-Users-hyun-Desktop-broccoli-server/memory.t2ab-evacuated`. **대피 없이 기동 금지**(부속서 exists=false 요구) |
| 러너 환경 | postgresql@18 started · uv ok · 원본 .venv ok |
| 봉인 | T2-0b manifest 는 **draft**(BK1 도 --allow-unsealed 채점) — O-5 부속서 실측(--measure-annex) 후 갱신 |

## 앵커 판형 (선례 = parent_settings 라운드 3 `3f14e4f1` — O-5.md §3 이 인용한 그 장치)

1. `docs/rebuild/delivery/spec.md` — §1 도메인 §2 API(비적용 한 줄) §3 저장(스키마 동결 — db_table 3종·`models` 경로/클래스명 동결) §4 published 계약 동결 22심볼+스텁 기본값 시맨틱 §5 상류 §6 복원 지점(base.py 1행) §7 검증
2. **OHS 동결 스켈레톤** — BC 삭제하되 `published_service/` 계약 파일 존치 + 서비스 모듈 2개를 기본값 스텁으로 교체(도메인 import 0)
3. `legacy_debt.txt` — pairing 축(`#12/#385/#389 application.pairing` 판형)
4. `api_shape_pre.json` — HTTP 없음 비적용 파일
5. BC 삭제(계약 스켈레톤 제외 전부·migrations 포함) + 배선 걷기 = **`broccoli_server/settings/base.py:159` 1행뿐**(urls.py·api.py 참조 0 실측)
6. baseline 실측 — **`uv run pytest` maxfail 없이 전수**(make test 는 --maxfail=1 이라 baseline 용도 불가) + **스텁 기인 red 전수 열거**(소비자 테스트 20파일/6 BC — 그중 12파일이 `django_delivery.models` 직접 import라 collection 부터 red)
7. anchor-preflight.md + request.md(템플릿 빈칸: bc=delivery · 배선=base.py 행 축자 · 앵커 해시 · 라운드 표기 `AB-r1`) → 앵커 커밋
8. **리셋 앵커 실증 1회**(D10 조건 — 실패 시 O-5 반복성 재판정 무효): 리셋 명령·`manifest_seal.py --tree-hash` 재현·미추적 잔여 0

## delivery 실측 요점 (Explore 2026-08-21)

- 비-test 139파일 3,848 LOC · hub BC — 프로덕션 인바운드 3파일(accounts ACL·notifications ACL·lessons sender) 전부 published_service 경유·22심볼
- 타 BC **테스트 20파일/6 BC** 인바운드(12파일은 모델 직접 관통 — 전부 스텁 기인 red 예상)
- `deliver_notification` 은 in_atomic_block 거부(계약 조항) · FakeAlimtalkGateway 거짓 성공은 **요구로 옮기지 않음**(O-5.md §6)
- hard stop: **A = 기계 8h·과금 20M · B/C = 16h·40M**(사전 등록 §5)

## 기동 절차 (앵커 커밋 후)

1. 메모리 대피 확인(`ls ~/.claude/projects/-Users-hyun-Desktop-broccoli-server/memory` → 없어야 함)
2. 타깃 워크트리 3개: 앵커 브랜치에서 각 런 독립 브랜치(`ab/t2ab-R04` 등)로 `git worktree add`. `POSTGRES_TEST_DB` 분리(O-4.md §2 — 동시 테스트 조건)
3. 런 시작 체크리스트(orders/README §«런 시작 체크리스트») — 리셋·`.dddjango/` 제거·봉인 대조·**암 영수증**(`regen_core.py --arm-receipt <타깃>/arm.json` — env 3종 실은 채)
4. REQUEST = `docs/rebuild/delivery/request.md` 그대로(byte 동일 3회 확인) · 게이트 답은 BK1-RUNSTATE «게이트 답» + O-5 판형
5. herdr 워크스페이스 3개(--env `DJR_LOOP_ENABLED`·`DJR_LOOP_SELECTOR`·`DJR_EXPERIMENT_RUN_ID=t2ab-R0N`), claude 기동 = **Opus 4.8·전자동** — launcher 질문은 No·No·Keep
6. 감시 = `bk1-watch.sh` v6 판형 재사용(에이전트 이름·타깃 경로만 교체)
7. 완주 → `ab_score.py`(게이트 시점에 RUN_ID) + O-5 인수(I1·I3·I4 — O-5.md §5) → BK3

## 암 배정 (봉인 배정표)

| 런 | 암 | env |
|---|---|---|
| R04 | **C** | `ENABLED=on · SELECTOR=sparql · RUN_ID=t2ab-R04` |
| R05 | **A** | `ENABLED=off · RUN_ID=t2ab-R05` |
| R06 | **B** | `ENABLED=on · SELECTOR=snapshot · RUN_ID=t2ab-R06` |
