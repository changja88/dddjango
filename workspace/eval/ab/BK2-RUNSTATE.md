# BK2 실행 상태 — O-5 delivery · claude 레인 (2026-08-21 준비 개시)

> **compact 대비 재개 좌표.** BK1 정본 = `BK1-RUNSTATE.md`·`BK1-RESULT.md`(측정 실패 블록 — 사용자 ⓑ«수리 후 잔여 15런» 결정).

## ⚡ 재개 요점 (최신이 맨 위)

**⏹ 실험 종결(08-22 13:1x — 사용자 결정 «지금 즉시 전부 중단» · AskUserQuestion 직접 선택).** 처분 = 사전 등록 v4: BK3 3런 Phase 2 중반 중단(판 wZ·w0·w11 닫음·발화 여부 미확인 처분)·잔여 9런 취소·유효 측정 0건인 채 종결. 채택 = **구조 이득 명시 채택 경로**: 그래프/정규화 실사용+점진 이관(운용 평가 전환)·**폐루프 기본 off 존치**. 메모리 복구 완료(tree_sha256 `b80b1b17…` 봉인 스냅숏과 완전 일치·10파일 — 기계 검증). 감시 전부 해제. **정리 대기(사용자 확인 필요)**: 타깃 워크트리 6개(`~/Desktop/t2ab-R04~09` — R04~06은 완주 산출물·R07~09는 미완) · 앵커 워크트리(ab-t2-delivery-anchor ~600M) · 테스트 DB 6개(test_broccoli_r04~09) · 미푸시 실험 커밋들은 push 됨(릴리즈 선례 범위 내).

**🚀 BK3 기동(08-22 오전 — 사용자 ⓐ 승인 «승인» 후).** 이행 완료: 동결 개정 10(`4ba4688` — 6′ 발화 지점 «귀속 red 의 모든 반송 전»·반송 메시지 6′ 결과 명기 의무) → 검증 전건(parity 정합·rulepack 변이 11·make verify green 393·발화 probe 11단언·cache 경고 0) → **2.16.0 릴리즈**(`b84a7bf`·태그 push·두 설치본 갱신·cache_parity ok) → BK3 기동. **codex 호출명 함정 해소**: `/dddjango:dddjango` 는 codex 에서 Unrecognized(2회 실증·오염 0) → 명시 호출은 **`$dddjango:dddjango`**(`$` 접두 — codex exec 실측) → 앵커 개정 커밋 `09ef01d6`(d869e211 기반·브랜치 ab/t2-delivery-anchor-codex) 로 타깃 재생성. **BK3 확정값**: R07=B(wZ:p1)·R08=A(w0:p1)·R09=C(w11:p1) · tree `83bed28daa95` · req `65493cc83625` · debt 5행 · 영수증 2.16.0 · DB test_broccoli_r07~09 · 제출 판형 = **pane send-text + enter**(agent prompt 는 페이스트만 됨·codex 에이전트 등록 지연으로 pane read 기반 감시 `bk3-watch.sh`). **발화 실측 게이트**: R07(snapshot)·R09(sparql) 에서 injection.jsonl 생성 여부 — 1런 후에도 0 이면 잔여 기동 전 정지·재상정(사전 등록 v3). **BK3 STOP ①(10:36 — R09)**: Phase 1 설계 리뷰가 외부 관측 행위 미결 5축(A 미구성 채널 처분·B 재클레임 지연·C 24h 후 멱등키·D 결과 미상 재전송·E ambient atomic)을 STOP 으로 올림 — 권고 전부 unavailable → 기록 규칙(스코프 불확대·첫 선택지+사후검증)으로 **A1·B1·C1·D1·E1·E1a** 답(10:43 재개 확인). R07·R08 도 같은 STOP 이 오면 **동일 답**(암 간 대칭 유지). **BK3 STOP ②(10:53 — R08)**: 같은 사안 단독 축(24h 후 멱등키 Option A/B) → **Option A**(=R09 C1 — 대칭+첫 선택지 이중 정합) 답·10:56 재개(«phone-expiry 만 G1 override 재리뷰» 경로). **BK3 STOP ③(11:03 — R09)**: E1 파급 — Accounts 소비처가 ambient transaction 안에서 mark finalize 호출(placement 충돌 F1~F4) → **F4**(ambient 내 호출 즉시 거절 — E1 대칭·F1 은 스코프 확대 배제) 답·11:10 재개(Phase 2 진입). **BK3 STOP ⑤(11:15 — R09·F4 교정)**: F4 가 완료 조건(Accounts 인바운드 무수정 green·anchor 신규 red 0)과 양립 불가 실증(현존 Accounts 명령이 mark_accepted 를 항상 atomic 안에서 호출) → **G2 = F2 로 교정**(ambient 참여 허용 — 현행 관측 동작 보존·게이트 실검사 규칙이 대칭 논리보다 우선. G4=스코프 확대·G3=계약 변경 폭·G1=발주 종료 최후 수단). E=E1(SMS 축)은 유지. **교훈: F류 STOP 은 완료 조건 양립성부터 검사(2ⓐ 우선) — 대가 문면이 화면에서 잘렸으면 반드시 STOP 파일 원문으로 확인**. **BK3 STOP ⑥(11:48 — R08)**: 표준 골격 필수 apps.py 가 자기 설계 allowlist(160path)에 누락 — 생성=목록 밖/미생성=골격 위반 딜레마 → **allowlist 1행 추가 승인**(스코프 확대 아님 — 필수 구성물의 저작 누락 교정·BK2 선례) 답·G1 override+최소 재리뷰 경유 Slice 1 재개. **BK3 STOP ④(11:05 — R07)**: spec §1.5 엄격 검증 ↔ frozen V1 계약 충돌(3택) → **1**(V1 사영 한정 §1.5 완화 — 2는 동결 파괴·3은 표면 확대 배제·첫 선택지 정합) 답·11:14 재개(STOP 결정 기록 커밋). 완주 시: O-5 인수(`bk2-acceptance.sh` 판형 — DB 이름만 r07~09) → ab_score 3회(앵커 59ee1333) → BK4(O-4·codex — **앵커 저작 필요**·판형 rebuild/standard-tree S3-r1·42a904ae 선례).

**✅ BK2 종료(08-22 05:40) — 정본 = `BK2-RESULT.md`.** 3/3 완주(A=47cec94a·B=7e0d4a64·C=2433a20c)·인수 3/3 통과(각 4 failed=기존 lessons red만·스텁 16 전량 green 복귀)·**V 세 암 동일(0)**·**처치 발화 0 — BK1과 다른 원인**: 게이트 정상, 코디가 6′(regen_core)을 0회 실행(R06은 env on 실측·인지하고도 — 수시 게이트+즉시 반송 습성이 6′ 발화 지점을 선점). **BK3 기동 보류 — 자율 규약 정지 조건 ①(A/B 실패 분기) 상정, 아침 사용자 판정 대기.** 처분 3택(RESULT §5): ⓐ 6′ 발화 지점 수리 후 잔여 12런(권고·처치 정의 개정=사용자 승인 사항) ⓑ 강행(codex 습성 관찰값만) ⓒ 중단·§7. 인수 env 정본 판형 = bk2-acceptance.sh(.env.local 전체 source 금지 — DJANGO_SETTINGS_MODULE 오버라이드 함정). 채점 = score.json×3(앵커 59ee1333·allow-unsealed).

**🏁🏁 02:43 스냅숏(08-22): R04(C)도 완주 — HEAD `2433a20c` «rebuild(delivery): O5-ab-r1 — 클린룸 재구현».** 2/3 완주(R05 A=47cec94a·R04 C=2433a20c). 잔여 R06(B)만 — S4 Part C 재구현 → S5 → G2 → Phase 3(새벽 4~5시 전망). 02:10 세션 한도 정지 있었음 → 02:20 사용자 수동 «이어서 진행해»로 즉시 재개(운영 함정 ④: Limit reached 표시 중에도 프롬프트 제출로 즉시 재개됨 — 대기 금지). R04 특기: 잔존 red 4건은 lessons cursor 계열(앵커 baseline·main 공통 — delivery 무관 선언), env 인라인 주입(.env.local 부재). C암 주입 카운터 여전 0 — 채점 시 회전·용량 로그 판정 필수. **03:30~: 감시 v8 전환(한도 정지 자동 재개 — 정지 화면 고유 문면+유휴 시에만·질문 분기 통과 후라 STOP 자동 응답 위험 0 · 저장소 사본 941d0ab). R06은 S5(published 본문) 진입. 사용자 취침(03:30) — T5까지 자율 완주 지시, 정지는 자율 규약 4조건에서만.**

**🏁 01:34 스냅숏(08-22): R05(A) 완주 — HEAD `47cec94a` «rebuild(delivery): O5-ab-r1 — 클린룸 재구현»(6h49m·배선 INSTALLED_APPS 1행·허용 경로 밖 변경 0 자기보고).** R04(C)는 G2 직전 마지막 수렴 사이클(coder Sh 9건 수리 → 절단 없는 registry_gate 앵커 차분 — 코디 문면 «이번 clean 아니면 수렴 정지 판단»: 수렴 정지 STOP 오면 G1 STOP 규칙으로 답). R06(B)는 S4 진행(S1~S3✓·S5·G2 남음) — 예상 완주 새벽 2~3시. **관찰(채점 필수 항목): C암 주입 카운터 여전히 0 — 귀속 다수 실재했으므로 완주 후 `.dddjango` 회전·용량 로그(uninjectable 포함)로 발화 여부·이유 판정.** 인수·채점은 절차대로 세 런 모두 완주 후 일괄(R05 단독 선행 금지 아님 — 단 DB 경합 피하려 세 타깃 순차 실행). 판 사용량: R05 97%(리셋 임박)·R04 86%·R06 81% — 크레딧 초과 사용 켜져 있어 정지 없음 전망.

**🚀 BK2 실행 중 — 21:00 스냅숏: 세 런 모두 Phase 2(구현).** R04(C) 구현·서브에이전트 2 병렬 · R05(A) 구현 [3/4] 슬라이스 5·S1 domain 착수 · R06(B) 구현 [4/4] — S1 백스톱 귀속 22건 → G1′ 설계 반송 사이클(정상 수렴 회로 — 반송 2회 초과 시에만 정지 규정). G1 설계 승인은 셋 다 통과(R04 는 19:53 «1 기본 승인(권장)» 답 — G1/G2 승인 질문은 항상 «기본 승인(권장)»=1 이 봉인 게이트 답과 정합). 사용량: 5h 창 57~70%(곧 리셋)·주간 11~14%·크레딧 초과 사용 켜짐.

**compact 후 재개 절차**: ① 이 절 읽기 ② 감시 3종 생존 확인 — `bk2-watch.sh` v7(백그라운드 task) · **Monitor 즉응**(`tail -f bk2-events.log | grep "질문 대기|API Error|…"` — compact 후 죽어 있으면 재장착) · ScheduleWakeup 30분 안전망 ③ 게이트/STOP 질문은 «STOP 라운드 1» 선례 + G1 규칙으로 답(메뉴=`herdr agent send-keys <a> <숫자>` · 텍스트=`herdr agent prompt <a> "<답>"` — 판 Enter 는 불응 사례 있음) ④ 완주(세 타깃 `rebuild(delivery)` 커밋) 시: O-5 인수(직렬 전수 `uv run pytest -q --tb=no -rEf --continue-on-collection-errors` — 기준선 = preflight ⑹ 20건·debt 확장 2행 반영) → `ab_score.py` 3회(RUN_ID 환경) → BK2 판 3개 닫기 → **BK3 기동**(codex·O-5: 타깃 t2ab-R07~09 를 `d869e211` 생성 → debt 2행 저자 추가(45996614 문면) → 리셋·영수증 → codex 기동은 판 셸에서 `codex` — launcher No·No·Keep · 모델 기본값이 이미 gpt-5.6-sol xhigh · 요청문 그대로 제출).

기동 기록(18:16): 세 판 [Opus 4.8 ◕ xhigh]·bypass·byte 동일 요청문(호출명 `/dddjango:dddjango`). 워크스페이스 정리(19:10 사용자 승인): BK1 계열 wH·wJ·wK·wM·wF 닫음 — 남은 실험 판 = wQ·wR·wS 뿐.

### STOP 라운드 1 — 재료 모순 (18:39~18:45 · 기록)

세 런이 **같은 재료 모순**을 적발: spec §3/§6 «옛 모델 경로(infra_layer/django_delivery) 동결»(타 BC 12테스트 실측 기인) ↔ legacy_debt.txt 는 pairing 축만 등재 — infra_layer 존재만으로 목록 밖 귀속 **#81·#324**(R04 가 registry_gate 앵커 차분으로 실증). R05(A) 21m·R04(C) 27m 도달, R06(B)은 도달 시 같은 답.

**답 = ⓐ 빚 확대**(`#81·#324 application.delivery.infra_layer` 2행 — 저자 승인): 규칙 2ⓐ(게이트 실검사 유지·빚 채널은 «미이관 경로 의존»의 정규 용도 그대로) + 2ⓑ(ⓑ 는 타 BC 12파일 스코프 확장). **자인**: 이 모순은 재료 저작 결함 — 저작 검수에서 «경로 동결 ↔ 표준 트리 검사기» 충돌을 못 잡았다. 세 런이 독립 적발(G0 방어 작동 관측). 사전 등록 «STOP=판정 실패» 축과의 긴장은 BK1 선례(저자 답 재개·사후 검증 등재)와 동형 처리 — 채점 시 STOP 이력 병기.

**운영 함정**: R05 판 Enter 불응(입력창 에코 혼동) → **`herdr agent prompt <에이전트> "<답>"`** 채널이 확실하다. codex 실측(BK3 준비 완료): `dddjango:dddjango` 메인 스킬 로드 확인 · 기본 모델 **gpt-5.6-sol xhigh**(봉투 그대로) · launcher 3질문 동일(No·No·Keep) · probe 는 R04 타깃 오염 0.

### STOP 라운드 1 후속 — 빚 파일 편집 주체 (18:48 · 기록)

R04 가 후속 확인을 올림: canonical `legacy_debt.txt` 는 발주가 «가필=승인 위조»로 봉인 — ⓐ(내용 확대)와 별개로 «누가 편집하나». 처분: **저자(하네스) 직접 편집** — 세 타깃에 같은 2행(`#81`·`#324` **슬래시 경로 형** — R04·R05 가 독립적으로 같은 형식 실측)을 추가. R05 는 코디가 이미 같은 2행을 자기 주석과 함께 등재해 둔 상태(«등재하고 진행» 답의 집행 — 점→슬래시 변환까지 스스로 옳게) → 저자 중복 블록은 걷고 코디 판 존치. **실효 debt 행은 세 타깃 동일**(주석 문면만 상이 — 게이트 입력은 `#행`뿐이라 무영향). R04 답 = «2. 사용자 직접 편집»(행 실재 확인 후 진행). 앵커 브랜치 기록 커밋 `45996614`. **BK3 대칭 절차**: codex 타깃도 `d869e211` 생성 후 같은 2행을 저자가 추가(앵커 새 HEAD 로 생성하지 않는다 — claude 레인과 출발 조건 동일 유지).

- 메모리 대피 완료(사용자 명령 불발 → 직접 입력 승인 근거로 재시도 성공 · annex exists=false)
- **기동 개정 2건(런 전·기록)**: ⓐ 요청문 호출명 `/dddjango` → **`/dddjango:dddjango`**(현행 claude 는 plugin:skill 정식명만 유효 — 첫 두 제출이 «Unknown command»로 불발·산출물 오염 0 확인 후 리셋) ⓑ 그에 따라 **기동 HEAD = `d869e211`** · 리셋 재현 해시 = **`c75e6671`**(재실증 완료·부속서 재병합). 게이트 앵커는 불변 `59ee1333`
- 판 실측: 세 판 모두 **[Opus 4.8 ◕ xhigh] · bypass permissions on** · 스킬 기동(Context 적재·Unknown 없음) · 에이전트명 t2ab-r04/r05/r06
- 기동 경로 함정(재발 방지): `herdr pane run` 직접 실행 세션은 플러그인이 안 잡힌다 — **판 대화형 셸에서 기동**해야 한다. 입력창 클리어는 Escape/C-u 불가·**backspace 키**만 유효
- codex 레인(BK3~) 이월 확인: codex 의 스킬 호출 구문 별도 실측 필요

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
