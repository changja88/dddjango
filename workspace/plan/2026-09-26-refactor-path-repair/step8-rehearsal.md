# 로드맵 8 실전 리허설 — 계획과 기록 (2026-09-28 ~)

로드맵 v1 8행: «spring_dream_server 사본에서 배포 전 플러그인으로 끝까지 실행(원본 쓰기 0 · 결과물 폐기) — 리팩토링 커맨드 BC 1(service_policy) · 작은 기능 수정 1(빚 조사→정리→동작 보존) · web 작업 1 · G2 까지 → 리허설 보고».
범위 결정: 사용자 «계획대로 3종 G2까지»(09-28 02시대 · 추정 약 $250~350 · 5~7시간).

## 1. 하네스

- 사본: 레인마다 현장 원본의 새 `git clone --shared` → `git remote remove origin`(원본으로의 push 경로 차단) → `uv sync --frozen`. 원본에는 clone 읽기만.
- 실행: `claude -p --output-format stream-json --verbose --settings <설치본 dddjango·dddjango-web off> --plugin-dir <작업 트리 플러그인>` · `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0` · 턴마다 `--resume <session>`.
- 게이트 답: 운영 세션(이 세션)이 한다 — 첫 요청에 «운영 세션 대리 · 사용자가 이 리허설의 게이트 답을 위임» 을 밝힌다. 빚은 ⓐ. 리팩토링 «사용자 판단» 항목(대리 답 불가)은 사용자에게 질문을 그대로 전달하고, 사용자 답은 원문 그대로 파일(`scratch 8-rehearsal/user-answers.md`)에 적어 `사용자 원문 <파일:행>` 으로 넘긴다.
- 레인은 하나씩(무거운 실행 겹치지 않음). 스크립트·원 기록 = scratch `8-rehearsal/`.

## 2. 레인

| # | 입구 | 요청 | 보려는 경로 |
|---|---|---|---|
| R8-F | `/dddjango:dddjango` | 지갑 잔액 조회 응답에 `currency_code`(값 "KRW" 고정) 추가 · 기존 필드·상태 코드 유지 | 수정 모드 · 27종 빚 스캔 → wallet #490 ⓐ → 슬라이스 0(0C 창 · `behavior_guard` open/close) → 기능 슬라이스 → G2(잔존 · 동작 보존 · pre-gate 최신성) |
| R8-W | `/dddjango-web:dddjango-web` | 로그인 워드마크 로고를 새 파일로 교체(같은 크기·위치) | 트리비얼 → 손대는 단위 빚 → 수정 모드 승격 → ⓐ → 슬라이스 0 개명 3 + 참조(web/ 밖 테스트 포함) → 끝 green ①~⑤ → 교체 → G2 |
| R8-WR | `/dddjango-web:refactor web/home` | (불편 서술 없음) | web 리팩토링 입구 R1~R3 → G0 → Phase 1 슬라이스 0 → Phase 2 창 → 끝 green ①~⑤ → G2 — 사용자 추가 결정(09-28 22시대 «더한다 (권장)») · 사용자 제안(«다른 bc로 하면 같이 실행 할수 있는거 아니야?»)으로 R8-R 과 병행 착수(23시 · 앞 단계는 LLM 판단 위주라 무거운 전체 테스트는 R8-R 끝난 뒤에 올 예상) |
| R8-R | `/dddjango:refactor service_policy` | (불편 서술 없음) | R0~R3 → G0(사용자 판단 전달) → Phase 1 슬라이스 0 명세 → Phase 2 0T/0C 창 → G2(`M_c + M_m` · residual 확인 리뷰어) |

## 3. 기록

### R8-F (작은 기능 수정 · 사본 `8-rehearsal/sds-R8-F` · 원본 HEAD `5debeb89b` · 폴더 `.dddjango/20260928-0255-wallet-balance-currency-code/`)

| 턴 | 내용 | 시간·비용 |
|---|---|---|
| t00 | 수정 모드(기존 `GET /api/wallet/balance` 국소 변경) · 27종(루트 TARGET · auto 5종) · wallet 빚 C1 `#490 …/clock/system_adapter.py` · 질문 폴더 → 빚 ⓐ(Recommended)/ⓑ(대리라 원문 필수 고지) → 배치 → 스코프·lens(ddd·api) · 평문 질문 뒤 턴 종료 | 13분 · $1.87 |
| t01 | 운영 답(새 기능 · ⓐ · ② 기존 wallet · 승인) → 폴더·실행 줄 → architect 초안 → pre-gate green → 리뷰 3종(ddd·api·discipline lightweight) → **api blocker: `currency_code "KRW"` 가 잔액 단위(원보)·기존 `price_unit: "service_currency"` wire 와 충돌** → `STOP_FOR_USER_APPROVAL`(stop-01 · ⓐ 단위 통화 / ⓑ 판매 통화 / ⓒ G0 / 중단 · 권고 불가 · «운영 세션이 대신 정할 수 없음» 명시) | 53분 · $19.34 |
| t02 | 사용자 답 «ⓐ»(운영 세션 AskUserQuestion) → `8-rehearsal/user-answers.md:3` 원문 기록 → `사용자 원문` 출처로 전달 → architect 반영 · pre-gate green · 재리뷰 2종 + api 재호출 → **G1′ 배너**(pre-gate 1행 `귀속 0 · 실존 결손 0 · 커버 P/S/I · 기준선 5debeb89b785` · 입장 표 16행 pending 0 · 슬라이스 0 = 시계 어댑터 표준 골격 이동 0C · T14 import 1줄 retain) | 21분 · $7.93 |
| t03 | 운영 답 «G1′ 승인(nit 후보 미반영)» → Phase 2: 기준선 테스트(`--postgresql-exec …`) · `build_anchor` 기록 · `behavior_guard.py open --kind code` → 슬라이스 0 coder(0C 이동 완료 · 제품·테스트 로직 변경 0) → `behavior_guard.py close` → wallet 54 passed → S1 acceptance-tester(T1 update · `currency_code` 부재로만 Red) → S1 coder(Green · ruff·mypy 깨끗 · registry_gate 귀속 0) → discipline-reviewer Phase 2(발견 0) → 전체 suite·27종을 **백그라운드**로 띄우고 턴 종료 | 60분 · $12.46 |
| t04 | 운영 알림 «`-p` 하네스에선 백그라운드 Bash 가 턴을 넘기지 못함 — 포그라운드로 재실행 후 G2»(고아 postgres 는 운영 세션이 `pg_ctl stop -m immediate`) → 27종 포그라운드(exit 1 = 0건 · scope 렌더 5종 신규분 0) · registry_gate **귀속 0**(해소 2 · legacy 잔존 4214 별도 보고) · 전체 suite PG 2453/1 fail · DB 없음 7667/12 fail — 실패 13건 전부 `tests/test_service_*` 로 앵커 스냅숏에서 같은 사유 재현(무관) · `manage.py check`·`makemigrations --check` 앵커와 같음 → **G2 배너**: `G0 ⓐ 1건 중 잔존 0` · `동작 보존: green · 창 1(0T 0 · 0C 1) · 열린 창 0` · `pre-gate 최신성: 블록 해시 = 리포트 · green` · `승인 유입 0` · 입장 decision 결과 표(update T1 Red→Green · reuse/retain green · reject write 0 · pending 0) | 43분 · $2.16 |
| t05 | 운영 답 «G2 승인(무관 실패 13건 범위 밖)» → 실행 줄 `G2 승인 20260928-0555` · 커밋 2개(`04944c588` 슬라이스 0 · `cf33ab0b7` 기능 + 산출물) · 마무리 보고(STOP-1 사용자 결정의 대가 = product 가격 규칙·`price_unit` 불일치를 명세 §12 후속으로 남김) | 1분 · $0.41 |

R8-F 합계: 6턴 · 3시간 15분(02:41~05:56) · **$44.17**(`total_cost_usd` 는 재개 세션 누적값 — 턴 비용 = 차분) · **플러그인 결함 0** · 기대 경로(수정 모드 → 27종 → ⓐ → 슬라이스 0 0C 창 → 기능 슬라이스 → G2 잔존·동작 보존·최신성) 전부 통과.

### R8-W (web 작업 · 사본 `8-rehearsal/sds-R8-W` · 준비 = 기존 워드마크 색만 바꾼 600×300 `new_logo.png` 커밋 · 폴더 `.dddjango-web/20260928-0558-login-logo-swap/`)

| 턴 | 내용 | 시간·비용 |
|---|---|---|
| t00 | 트리비얼 판정 → 손대는 단위(`web/static/images/`) 빚 스캔 exit 2 → **수정 모드 승격**(G1′ 경유) · 위반 3건 WN8(C1 교체 대상 자체 · C2 · C3) · 슬라이스 0 규모(항목 3 · 단위 3 · 파일 6 · web/ 밖 테스트 `tests/test_settings_profiles.py` 포함) · «다른 변경 없음»은 쓰기 범위 조건이지 ⓑ 가 아님 고지 · 선택지 ⓐ(권장)/순서 조정(`/dddjango-web:refactor web/static/images`)/출처 있는 ⓑ(대리라 사용자 원문 필수) | 5분 · $2.45 |
| t01 | 운영 답 «1(ⓐ)» → G0 배너: 스코프(교체 대상 새 경로 `chunmong_logo_v2.png` · 템플릿·CSS·py 무변) · 수정 모드(승인 명세 없음 + ⓐ → G1′ 필수) · 배선 6종 결손 0 · offline OpenAPI 동결(46 paths) · 시안 없음(DesignSync 미호출) · 빚 줄 `ⓐ 3 · ⓑ 0 · 요구 0` · 배치 질문(② 기존 auth 해당 표시) | 1분 · $0.33 |
| t02 | 운영 답 «② · G0 승인» → architect 초안(슬라이스 0 = 개명 3 + 참조 · 기능 = 새 경로 바이트 교체) → **리뷰 전 정지 — 슬라이스 0 재상정 STOP**: 끝 green ④ `--subst-check <git_snapshot> HEAD` 는 누적 구간의 `git diff -M` 개명 탐지로만 짝을 찾는데(`scripts/src/subst.py:92-106`), C1 은 슬라이스 0 개명 뒤 기능 슬라이스에서 바이트가 통째로 바뀌어 `D`+`A` 로 보임(실측 · `-M20%` 도 같음 · C2 는 `R100`) → `tests/test_settings_profiles.py:131,148` 치환이 짝을 잃어 G2 exit 2 확정 = **검사기 오탐 예견** · 선택지 ① C1 제외·처분 플러그인 결함(권장) ② C1 제외·별도 요청 ③ 출처 있는 ⓑ ④ 중단 · «대리 위임에서 빠짐 — 사용자 본인 답» | 13분 · $4.06 |
| t03 | 사용자 답 «1 C1 빼고 진행 · 플러그인 결함 (권장)»(운영 세션 AskUserQuestion · `user-answers.md:4` 13:15) → `사용자 원문` 출처로 전달 → `## ⓐ 재상정` · architect 재호출 → design-review-web(blocker 0 · important 3·nit 3 전부 반영) · discipline 경량(발견 0) → **G1′ 배너**: 슬라이스 0 = C2·C3 개명 + 참조 4곳(web/ 밖 치환 0 · 정형 행 `경로:` 2 · `이름:` 0) · 기능 = 옛 이름 그대로 내용만 교체(sha256 고정) · 교체 전 렌더 기준(3 뷰포트 · `StaticFilesStorage`) · 이탈 D1(동결 시안 로고와 달라짐 · 요청 원문) · CDN 캐시 공개 · Y/Z 0 · 스캔 단위 확인(G0 범위 안) | 20분 · $9.23 |
| t04 | 운영 답 «G1′ 승인(D1 수락)» → 교체 전 렌더(3 뷰포트) · 기존 테스트 기준선 → 슬라이스 0(`760ff8015` · R100 ×2 · 참조 완전성 exit 1) → 슬라이스 1 로고 바이트 교체(`e66a854f0`) → 전후 브라우저 대조 · 규율 감사 0 · 백스톱 exit 0 → **G2 배너**: 빚 줄 `G0 ⓐ 3건 중 잔존 0 · 재상정 제외 1 · legacy 잔존 0` · 기존 테스트 `기준선 실패 13 · 새 실패 0 · 요동 0`(슬라이스 0 끝 PG deadlock 13 은 노드 재실행 통과 → 요동) · `--subst-check exit 0` · S3·S4 미검증(로그인 세션 필요 · 대체 근거) · 합치기(`reset --soft`) 동의 겸함 · 경계 보고 2(`.playwright-mcp/` · `/tmp/_x`) · **리허설 관찰 3**(subst-check 누적 개명 · `extract_contract.py` 인용 0 exit 1 · ⑤ 재실행 규칙 겹침 ≈22분) | 86분 · $15.22 |
| t05 | 운영 답 «G2 승인(합치기 동의)» → 마무리: `reset --soft` 합치기 → 18파일 스테이징(커밋은 사용자 몫 안내) · 미검증 목록 · 관찰 3 재기재 | 1분 · $0.52 |

R8-W 합계: 6턴 · 약 2시간 20분(실행 시간 · 사용자 답 대기 7시간 제외) · **$31.80** · 플러그인 결함 1(subst-check 누적 개명 짝 — 사용자 «플러그인 결함» 처분) + 문면 구멍 후보 1(`extract_contract.py` 인용 0 → exit 1 · Coordinator L200 의 exit 1 가르기에 없음) · 관찰 1(⑤ 이중 실행 ≈22분 — 슬라이스 0 격리 + 최종 HEAD 확인이라 의도된 설계).

### R8-R (리팩토링 커맨드 · 사본 `8-rehearsal/sds-R8-R` · 폴더 `.dddjango/20260928-1504-refactor-service-policy/`)

| 턴 | 내용 | 시간·비용 |
|---|---|---|
| t00 | `/dddjango:refactor service_policy` + 운영 메모 → R0~R2(감사 `audit/20260928-1517` · 1차 check 63행 중 인용 불일치 1 → R2′ 재인용) → R3 판정(check-verdict exit 0 · red 0) → **G0 배너**: 검사기 빚 13 · 의미 채택 39 · 사용자 판단 2(M3 상태 전이 애그리거트 행위 ↔ CRUD 과설계 · M43 CQS ↔ 거절은 답) · 별도 요청 4 · 제외 3 · 오탐 1 · 병합→C 3 · 인용 불일치 1 · 규칙 근거 없는 불편 0 · 슬라이스 0 규모(ⓐ 52 · 파일 65) · 문서 층 변경(OpenAPI M13~M15) 고지 · M17·M22·M40 은 설계에서 «동작 불변 불가 STOP» 가능 고지 · 사용자 판단은 대리 불가(본인 직접 · 사용자 원문만) · 셸 인용 실수로 5종 exit 1 → 재실행(기록 둘 다 보존) | 61분 · $40.66 |
| t01 | 사용자 답 M3 «허용 — 뺌» · M43 «허용 — 뺌»(운영 세션 AskUserQuestion · 상황 설명 요청 뒤 · `user-answers.md:5-6` 17:58) → `사용자 원문` 출처로 전달 + 빚 전건 ⓐ · 스코프 승인(대리) → architect 초안 → 리뷰 4종 + pre-gate → 반영 38 → 재리뷰 2종(«집행 불가»였던 api·discipline) → 2차 반영 6 → **G1 배너 + ⓐ 재상정 STOP**: pre-gate `귀속 0 · 실존 결손 0 · 커버 P/S/I · 기준선 de0845fd7a93` · 슬라이스 0 = 0T 1창(테스트 11) + 0C 6창 · 정리 C1~C13 + M 29 · file-plan 68행(BC 안) · 입장 표 39행(retain 13 · reuse 18 · reject 8 · add/update/remove/pending 0) · **슬라이스 0 제외 10**(외부 관찰 동작 변경 M17·M22·M40·M7 · 테스트 본문 동반/보호 부족 M4·M2·M6·M21·M59 · 스코프 밖 편집 M50) — 대리 불가 | 2시간 10분 · $58.57 |
| t02 | 사용자 답(상황 설명 뒤) 9건 «별도 요청 (권장)» · M50 «ⓑ 미룸 (권장)»(`user-answers.md:7-8` 20:09 · 질문 원문 포함) → `사용자 원문` 출처 전달 + G1 승인(대리) → Phase 2: 기준선 전체 테스트 → S1 0T(`open --kind test` · 테스트 11 · 87+111 passed = 기준선 · close · `26de92aea` · 경량 감사 0) → S2 0C-1(`ad07e55f6`) → S3 0C-2(`168bd3847` · nit 2) → S4 0C-3 편집 끝(관련 87+111 · 소비 BC 계약 61 · mypy strict green) → **STOP(검사기 오탐 의심)**: `check-transaction-boundary` #195 가 M8(씨앗 값 도메인 단일 출처) 결과 `for kind in ActionKind.seed_catalog(): save(kind)` 2곳을 새 위반으로 잡음 — 검사기 문면(33-38행)이 «팩토리로 태어남» 전파를 `[F(..) for ..]` 원소식 컬렉션에만 인정해 컬렉션 반환 도메인 팩토리를 모름(운영 세션이 문면 확인 · 옛 응용 직접 생성은 clean 인 비대칭) · 선택지 ① M8 카탈로그 부분만 제외 ② M8 전체 제외 ③ 중단 · 대리 불가 + file-plan 밖 낡은 docstring 3줄(대리 가능 · G1′ 소개정 / 잔존 기록) · S4 창 열린 채 대기 | 78분 · $19.47 |
| t03 | 사용자 답(상황 설명 뒤) «① 카탈로그 부분만 빼고 진행 (권장)»(`user-answers.md:9`) → `사용자 원문` 출처 전달 + docstring G1′ 소개정(대리) → architect G1′ 소개정(리뷰 다발 생략 — 사용자 STOP 결정으로 항목 빼기 + docstring 1행이라 계약·데이터·판정 소유 불변) → pre-gate 재발화 green → **G1′ 배너**: M8 을 한도 씨앗 부분으로 축소(M47 미해소 §12) · «M36 후속» docstring 1행 추가(w4) · ③ architect 해석 확인 요청(사용자 선택지 문면 «씨앗 2개와 도메인 seed_catalog만 되돌립니다» 를 #195 와 무관한 M54 docstring 은 유지로 해석) · file-plan 67 · 입장 표 40(reject 9) · (자동 모드 판정 서버 장애로 운영 세션이 재개를 못 해 사용자가 `!` nohup 으로 재개) | 12분 · $5.67 |
| t04 | 운영 답 «G1′ 승인(③ 해석 그대로 — 선택 ① 의 뜻 = 오탐에 걸린 부분만 빼기)» → w4 마무리(카탈로그 철회 · docstring · `a76efd75b`) → S5 0C-4(`ad3f1d08c`) → S6 0C-5 admin → S7 0C-6 → 창 7 green · `behavior_guard verify` green(열린 창 0) → registry_gate 귀속 2 red(#390 — M58 이 e2e 에 자기 BC `driven_layer` ORM 모델을 `TYPE_CHECKING` import) → 설계 계약 결함으로 분류 · architect 반송 → **G1′ 배너**(M58 새 형태 = `django.db.models.Model` 주석 · 새 0T 창에서 파일 1) | 64분 · $27.06 |
| t05 | 운영 답 «G1′ 승인(M58 새 형태)» → 새 0T 창 → 조각별·홀리스틱 감사(blocker·important 0 · nit 4 · ⓓ 신규 15 전부 기각) → 27종(exit 1 0) · registry_gate 귀속 0(해소 14 = C1~C13 포함) · residual 리뷰 → coder 1회 반송 → 전체 suite 실패 집합 = 기준선 · 창 9 green → **G2 전 STOP(잔존 `M_m` 3 = M1·M37·M55 — 부분 정리 · 나머지는 테스트 본문 변경 필요)** · 처분 무엇이든 부분 정리 철회 + G1′ 소개정 | 88분 · $26.82 |
| t06 | 사용자 답 «별도 요청 (권장)»(M1·M37·M55 · `user-answers.md:12` 00:50) → 처분 기록 → architect G1′ 소개정(새 §4.7 철회 절 · 제품 9파일 철회 · 얽힘 판정: `applies_to` 는 M8 몫으로 유지 · 0T 철회 불필요) → pre-gate 재발화 green → **G1′ 배너**(file-plan 64 · 입장 표 38) | 19분 · $9.19 |
| t07 | 운영 답 «G1′ 승인» → 0C-R 철회 창(w10 · 테스트 무편집) → 창 diff 감사(통과) → 재검증 일괄 → **G2 배너**: `G0 ⓐ 52건 중 잔존 0(M_c 0 · M_m 0)` · 재상정 제외 13 + 부분 1(M8 카탈로그 — 플러그인 결함) · `동작 보존: green · 창 10(0T 2 · 0C 8) · 열린 창 0` · pre-gate 최신성 블록 해시 = 리포트 · registry_gate 귀속 0(툴체인 v2.18.4 digest 기록) · 27종 exit 1 0 · 전체 suite 실패 집합 = 기준선 · mypy strict 417 green · 입장 표 add/update/remove/pending 0 · 문서 층 OpenAPI 허용 6키만 · 감수 nit 5(수정 후보) · 커밋 9 | 41분 · $7.60 |
| t08 | 운영 답 «G2 승인(nit 5 보고만)» → 실행 줄 `G2 승인 20260929-0150` · 산출물 커밋 `d3b90d1a3` · 마무리 보고 | 1분 · $0.58 |

R8-R 합계: 9턴 · 15:02~01:51(사용자 답 대기 포함) · **$195.64** · 사용자 질문 5회(G0 사용자 판단 M3·M43 · 재상정 10건 · 검사기 오탐 M8 · G2 잔존 3건) · **플러그인 결함 1(D2 #195)** · G2 게이트가 설계 결함 1건(M58 e2e import)을 잡아 반송 — 의도대로.

관찰(R8-R · 개선 후보): Phase 1 이 «슬라이스 0 규칙 안에서 끝까지 해소 가능한가» 를 판정하지 않아 부분 해소 항목이 G2 직전 residual 에서야 드러났다(M1·M37·M55) · 동작 보존이 확인된 부분 개선까지 철회하는 규칙이라 한 바퀴(철회 창 + G1′)가 헛돈다.

### R8-WR (web 리팩토링 · 사본 `8-rehearsal/sds-R8-WR` · 폴더 `.dddjango-web/20260928-2252-refactor-home/` · R8-R 과 병행)

| 턴 | 내용 | 시간·비용 |
|---|---|---|
| t00 | `/dddjango-web:refactor web/home` → R1 검사기 빚 스캔(범위 안 0) · R2 의미 점검(리뷰어 2) · R2′ 인용 19/19 · R3 `check-verdict` exit 0 → **빚 질문 먼저**(G0 배너와 안 묶음): 의미 채택 5(M3 세션 API 예외 500 · M5 form · M17 내비 규칙 되풀이 · M18 · M19) · 사용자 판단 1(M7 `@login_required` ↔ 실물 API 계약만) · 별도 요청 12(경계 교차) · 범위 밖 키 C1~C3 WN8 · M3 ⓐ 는 Phase 1 «동작 불변 불가» 가능 고지 · 대리 ⓑ 불가 · plan.md 소비자 누락(`login_view.py`) 관찰 | 30분 · $12.60 |
| t01 | 운영 답 빚 5 전부 ⓐ(대리) + 사용자 답 M7 «위반 — 정리»(`user-answers.md:10` 23:21) → **G0 배너**: 리팩토링 모드(표지 정확) · 범위 파일 13 · 배선 6종 결손 0(보고만) · 계약·디자인 해당 없음 · 의미 ⓐ 6(M7 출처 줄 실재 확인) · 슬라이스 0 = 파일 3 · M3·M7 은 Phase 1 «동작 불변 불가» 가능 고지 · 영향 화면에 로그인 GET 추가 | 1분 · $0.33 |
| t02 | 운영 답 «G0 승인» → `## G0` 기록 → architect 슬라이스 0 초안 → **동작 불변 불가 STOP**(리뷰 전): M3 홈·로그인 GET 500 → 200 재시도(상담 VM 비공개 함수 필요 · 경계 교차) · M5 VM 서명 변경 → `tests/web` 호출 인자 4곳(치환 규칙 밖 · `--subst-check` 차단) · M7 `302 /login/` → `302 /accounts/login/?next=/`(`LOGIN_URL` 미설정 · 그 경로 web 에 없음 · settings 는 web/ 밖) · Coordinator 가 두 곳 직접 확인 · 남는 슬라이스 0 = M17·M18·M19(파일 2 · 서명·이름 유지) | 10분 · $3.85 |
| t03 | 사용자 답 «별도 요청으로 (권장)»(M3·M5·M7 · `user-answers.md:11` 23:34) → `## ⓐ 재상정`(원문 줄 확인) → design-review-web · discipline 경량 병렬 → 반영(important 2 — 재상정 근거 명시 · 분기 병합 철회로 제어 흐름 변경 0 · nit 6 · 기각 0) → G1 스캔 단위 확인(`plan --names` 쌍 0 · 편집 줄 키 0) → **G1 배너**: 슬라이스 0 = M17·M18·M19 · 파일 2 · 개명·이동·참조 치환·web/ 밖 편집 0 · 행위 목록 H1~H10·L1·L2 · 기계 점검 3종 해당 없음 | 15분 · $5.39 |
| t04 | 운영 답 «G1 승인»(다른 레인 전체 테스트 병행 · 요동은 노드 재실행) → 진입 준비(check · 테스트 기준선 · 수정 전 렌더 · 산출물 커밋) → coder-web 슬라이스 0(`f68c1b755` · 파일 2) → 끝 green ①~⑤ → 규율 감사 → **G2 배너**: 전후 렌더 9 시나리오 byte 동일(status · Location · Cache-Control · client 요청 순서 · 본문) · 빚 `G0 ⓐ 6건 중 잔존 0 · 재상정 제외 3` · `--debt-residual` 0 · residual M_m 0 · 기존 테스트 `기준선 실패 13 · 새 실패 0 · 요동 0` · `--subst-check` exit 0 · 백스톱 26종 blocker 0 · 브라우저 확인 생략(HTML byte 동일 · `.env.local` 없음) · 경계 이탈 2 기록(`/tmp` 임시 파일 · 삭제) · nit 후보 1(주석 144자) | 76분 · $8.42 |
| t05 | 운영 답 «G2 승인(합치기 동의 · nit 미반영)» → 마무리(백스톱 재검 blocker 0 · 빚 잔존 0 · 치환 exit 0 · 합치기) | 1분 · $0.45 |

R8-WR 합계: 6턴 · 약 2시간 15분(22:50~01:06 · 사용자 답 대기 포함) · **$31.05** · **플러그인 결함 0** · 사용자 질문 2회(G0 사용자 판단 M7 · 동작 불변 불가 STOP M3·M5·M7) · 기대 경로(R1~R3 → 빚 질문 → G0 → 재상정 → G1 → 창 → 끝 green ①~⑤ → G2) 전부 통과.

관찰(R8-F · 09-28 새벽): 플러그인 결함 0. 하네스 제약 1 — 비대화형 `-p` 는 턴 종료 때 백그라운드 Bash 를 끊는다(대화형 세션엔 해당 없음 · 플러그인 결함 아님). 리뷰가 운영 세션이 지어낸 요청의 실제 의미 모순을 잡아 STOP 으로 올렸고, 위임된 운영 세션의 대리 답을 거부했다(규범대로). 하네스: 한 `-p` 호출 안에서 백그라운드 리뷰어가 돌아오면 턴이 여러 번 이어진다(`[result]` 여러 개 — 마지막이 게이트).

## 4. 리허설 보고 (09-29 02시)

| 레인 | 결과 | 시간·환산 | 사용자 질문 | 결함 |
|---|---|---|---|---|
| R8-F core 기능 요청 | G2 · 커밋 | 3시간 15분 · $44.17 | 1 (요청 의미 STOP) | 0 |
| R8-W web 기능 요청 | G2 · 합치기 | 약 2시간 20분 · $31.80 | 1 (슬라이스 0 재상정) | D1 · D3 |
| R8-R core 리팩토링 `service_policy` | G2 · 커밋 | 약 10시간 50분 · $195.64 | 5 | D2 |
| R8-WR web 리팩토링 `web/home` | G2 · 합치기 | 약 2시간 15분 · $31.05 | 2 | 0 |

- 기대 경로 전부 통과: 수정 모드 빚 스캔 → ⓐ → 슬라이스 0 창(`behavior_guard`) → G2 `동작 보존:`·잔존·pre-gate 최신성 · web 트리비얼 → 수정 모드 승격 · 리팩토링 R0~R3 → G0 → 재상정 → 창 → G2 · 대리 불가 항목은 전부 사용자에게 올라옴(대리 답 거부 · 사용자 원문 파일 출처 확인).
- **결함 3 → 수리·커밋**: D1 web `--subst-check` 누적 개명 짝 · D3 web 계약 인용 0 갈래 · D2 core #195 도메인 컬렉션 팩토리. 진단 → 워크트리 수리 → 독립 리뷰 2회씩 → 작업 트리 적용 → make verify 5/5 · verify-mutation 12/12 · verify-web green → `4908c113` · `810041b9` · 봉인 `fcf051fd`.
- **개선 후보(수리 안 함 · 다음 배치)**: ① Phase 1 이 «슬라이스 0 규칙 안에서 끝까지 해소 가능한가» 를 판정하지 않아 부분 해소가 G2 직전 residual 에서야 드러남(R8-R M1·M37·M55) ② 동작 보존이 확인된 부분 개선까지 철회하는 규칙(한 바퀴 헛돎) ③ 리팩토링 한 BC 당 사용자 질문 5회 — 전 BC 일괄(캠페인 3단계) 전에 질문 묶음·순서 설계 필요 ④ 인자 받는 도메인 컬렉션 팩토리·스칼라 채널 세탁(`next(iter(repo.list_all()))`) — #195 범위 밖 백로그 ⑤ web: Codex step 6 토큰 처분 문장 부재 · 미실행 정지의 scope.md 기록.
- 하네스 관찰: 비대화형 `-p` 는 턴 종료에 백그라운드 Bash 를 끊음 · 재개 세션 `total_cost_usd` 는 누적값 · 자동 모드 판정 서버 장애로 셸이 막힌 구간(21시대) — 플러그인 무관.
- 배포 창(09-29 02시 점검): 현장 G1 승인 뒤 갱신 중 레인 3(`lane-6-2-2` · `restore-old-a7642` · `lane-6-3-6`) → 아직 창 아님.

### 재개 좌표(09-29 02시 · compact 전 — 로드맵 8 끝)

- 로드맵 8 끝: 4레인 G2 완주(§3 · 보고 §4) · 결함 3 수리 커밋 `4908c113`(core #195) · `810041b9`(web D1·D3) · 봉인 `fcf051fd` · push 없음 · 에이전트 워크트리 제거 · 백그라운드 작업 0.
- 다음 = 로드맵 9 배포: 현장 G0~G2 레인 0 확인(`git -C /Users/hyun/Desktop/spring_dream_server worktree list` → 각 워크트리 최신 `.dddjango*/2026…` 폴더의 `G2 승인` 유무 · 09-29 02시엔 `lane-6-2-2` · `restore-old-a7642` · `lane-6-3-6` 이 G1 뒤) → 창이 열리면 기록 커밋(step7·step8·diag·progress·조감도·`docs/refactor-plan.html` — 사용자 파일 4 제외) → `work_flow.html` 재생성 필요 여부 → `make release` · `make release-web` → 사용자 `/plugin`(+Codex) → 봉인 재발행 chore → 10 관찰.
- 개선 후보(§4)는 사용자에게 «테스트 드라이브에서 데이터를 더 본 뒤 캠페인 계획 v3 와 함께 정하는 편이 낫다» 고 제안 → 사용자 «오케이 그럼 우선 compact 준비해줘».
- 사용자 확인용 진행표 = `docs/refactor-plan.html`(dddjango/web 좌우 · ✓▶○ · 간결 — 사용자 요청) — 상태가 바뀌면 갱신.
- 리허설 산출물(scratch · 세션 한정): `8-rehearsal/`(lane.sh · summ.py · 사본 4 · `user-answers.md` 12행) · 진단·리뷰 `diag-D2/` · `review-D1/` · `review-D2/` · `review-D2b/` · 패치 `impl-D2/r8-d2.patch` · `web-repair.patch`.
