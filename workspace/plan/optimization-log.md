# 최적화·속도 개선 로그 (로그본 — 작업용 · append-only)

[`optimization-board.md`](optimization-board.md)(요약본)의 근거 로그. 시간순으로만 덧붙인다
(수정 금지 — 정정도 새 항목으로). 2026-08-15 이전 상세는 프로토콜 §4 대장·§5.3 성적표
·메모리 `round3-liverun-approvals.md`가 정본이고 여기로 이관하지 않는다.

## § 문서 체제 전환 (2026-08-15)

- 12:5x 사용자 지시: 「거의 이틀동안 최적화 및 속도 개선이 전혀 이루어지고 있지 않아.
  방식을 바꿔야 할거 같아」 — 요약본(표)+로그본 2문서 체제 승인. 이후 진행 관리는
  이 두 문서에만 기입(프로토콜 §4/§5.3은 동결·이중 기입 중단).
- 소급 기입 결과(요약본 표): 최적화 작업=매 버전 존재 / **속도 개선=2.5.0·2.7.0 두 번뿐**,
  2.6.0~2.8.0 플러그인 측 «없음» 3연속 — 사용자 진단과 일치.

## § S3-r2″ (products · v2.8.0 · 앵커 5630e2f2 · 기동 HEAD e29b1059)

### 기동·경과 (02:34 ~ )

- 02:34:13 레인 A 기동(lane-a-r2c·wT:pZ·Opus 4.8) · 02:34:18 레인 B 기동(lane-b-r2c·
  wT:p0·gpt-5.6-sol xhigh·파일-경유 전달).
- 레인 B 정지 3회 전부 정박 대리 재개(판단 개입 아님 — 정박 규율 내):
  - 04:54 G1 STOP Z1(55P03)·Z2(OpenAPI 헤더) → spec §3 문면 정박으로 해소(선택지 확장 없이).
  - 05:45 수렴 회로 오탐 ①(admin +3 = 표준 강제 물리 소유 정정) → 1회 한정 해제.
  - 07:01 수렴 회로 오탐 ②(슬라이스 중간 registry 스냅숏 0→7) → 적용 축 정정으로 해제
    («G1 재설계 반복 비교» 축이지 «미완 슬라이스 중간 스냅숏» 아님 — #597 add/delete→save/remove 등
    7건은 (b) 자가 수리로 재분류).
- **사고: 하네스 감시 방치 4h33m**(07:56~12:28) — 승인 직후 연속 다이얼로그(blocked→blocked)를
  상태-전환 감지 Monitor가 놓침. 수정: Monitor v2(정지 상태 60s 하트비트·task b9mw8jab2).
  속도 개선 항목으로 분류(하네스 측·대기 감축).
- 레인 A 승인 왕복 ~45회(전부 read-only/허용 경로 도구 승인 — 판단 개입 0). **속도 병목 1순위**.

### 상태 스냅숏 (12:55)

- 레인 A: working — G2 말미. S1~S5 슬라이스 완료·make test 6834 green 신규 red 0·
  귀속 잔여 자가 수리→백스톱 재검 반복 중. STOP 0. 12:49·12:53 blocked/done 신호는
  수 초 내 자체 해소(transient).
- 레인 B: working — Slice 5 완주 후 검증 단계. unit+persistence 124 green(병렬 중 테스트 DB
  생성 경쟁 1건 → 단독 재실행으로 판정 확정)·api 7 green·mypy 146파일 clean·
  makemigrations --check 무변 → registry 실행 계획 중. 귀속 0 유지.

### 종결 시 절차 (예정)

⑤ 3축 재실측(A shape --success-only diff·B make test 앵커 6705+1 skip·C bc_registry_run+
migration_gate+registry_gate --anchor 5630e2f2 — 레인 .venv 3.14·정본 dddjango/scripts)
→ ⑥a grader 2인 → **요약본 표 2행 갱신 + 이 로그에 실측 기입** → 분석·개선 사이클.

### 레인 A 완주·⑤ 재실측 (13:31~13:38)

- 13:31:02 레인 A 완주 커밋 `41935cfd`(rebuild(products): S3-r2″ — 클린룸 재구현) ·
  13:33:32 done 확정(working tree clean 실측). 벽시계 10h58m(판 표시 «Cooked for 10h 58m»).
- **⑤ 하네스 재실측(레인 A·앵커 5630e2f2)**:
  - **A축 ✅**: openapi 덤프→shape --success-only→`api_shape_pre_success.json` 대비 **diff 0**.
  - **C축 ✅(green)**: registry_gate `--anchor 5630e2f2` **귀속(N∖L) 0·exit 0** ·
    migration_gate 잔존 53=전부 타 BC(products 0) · bc_registry_run: products 실발화=
    **#12 accounts authentication import 1건뿐=승인 빚 목록 내**(S3-r1 동형)·ⓓ 물음 5건
    (#69 프로덕션 assert 4·#153 유스케이스 호출 2회 1 — exit 불산입·⑥a 재료)·나머지
    전부 타 BC 기존분(#431 urls 등 — 차분 0 이 귀속 0 으로 실증).
  - **B축 ✅(13:42)**: `make test` **6834 passed·1 skipped·red 0**(143.54s·exit 0) — 앵커
    baseline 6705+1 대비 +129 전부 green·자기보고와 정확 일치. 1 skip=entitlements 구
    products 경로(infra_layer) importorskip 유래 pre-existing(spec §J retain·무편집).
  - **⑤ 3축 전부 green** → 13:44 ⑥a 독립 채점자 기동(결과지
    `workspace/eval/results/20260815-1339-pdrebuildlive-claude.md` 예정).
- 구현 중 설계 교정(외부 계약 불변·impl-notes.md): TransientRetryPort+driven 어댑터(#245·#7),
  SaleReferenceDate VO(#307), find_by_id_for_update 비관 락, ProductsUnitOfWork(#247),
  use_case 4파일(#19), name CHECK ≤100, admin validate_unique no-op.

### 레인 A ⑥a 종결 (13:59)

- 결과지 `workspace/eval/results/20260815-1339-pdrebuildlive-claude.md`(독립 채점자 1인·v5 frozen).
- **치명 0 · Q 상**(WEAK 1=Q-7 테스트 모듈 무어노테이션·parent/child 동형 지속) ·
  2차원 라벨 (정적: 준수 — FC ⏸️)×(라이브: 미검증).
- **r2′ 충돌 4축 재발 0 실증**: OHS 명명 `_query`·계약 V-접미 0·답 갈래 outcome·admin #462 칸
  전부 표준형 실현·귀속 0 — spec 개정+v2.8.0+preflight ⑽ 의 목적 달성.
- 자기보고 «설계 교정 7건» 전건 독립 검증 통과(비위임 침범 0)·자기 해석 2 정당·자가 승인 0·STOP 0.
- ⓓ 물음 5건 마무리: #69 assert 4건=타입 좁힘 정당·#153 호출 2회=표준형 정당.
- 잔여 결점(이월): FC-1 골든 행위표 4라운드 연속 공백 · `_events` 사적 읽기 canon 3회째.
- **레인 A 확정 기록**: 실동작 ~6h02m(벽시계 10h56m49s − 대기 4h55m17s) · 요약본 기입 완료.
  스트릭 판정(S3-r1 잠정 1 + 이번 통과 → N=2 도달 여부)은 **사용자 몫** — S4 진입도 사용자 확인 사안.

### 레이어별 실행 시간 실측 — 레인 A (14:1x · 사용자 지시로 신설)

- 방법: 레인 A 세션 기록(`~/.claude/projects/-Users-hyun-Desktop-broccoli-rebuild/09566ef7….jsonl`)
  에서 하위 agent 호출 시각 전수 추출 → 시각 사이 구간을 도식(01~06) 층에 귀속.
  방치 4h32m(07:56~12:28) 제외. 승인 대기 ~22m 는 구간들 안에 분산(±10m 오차).
- 구간 원자료(KST): 02:34 기동→02:49 G0 종료 · 02:49~03:24 설계 초안 · 03:24~03:39 리뷰
  4인 병렬 배차(03:24:57~03:26:27 4건 연속 기동 실측 — 병렬) · 03:39~03:52 반영·중재 ·
  03:52~04:00 규율 focused 재검+G1 · 04:00~04:20 인수 Red · 04:20~04:47 S1 ·
  04:47~05:00 설계 focused 개정 · 05:00~05:13 S1 수리 · 05:13~06:03 S2 · 06:03~06:35 S3 ·
  06:35~07:07 S4 · 07:07~07:55 S5 · 07:55 #7 이전 시작(→방치)→12:28~12:55 마무리+중간 검증 ·
  12:55~13:11 설계 최종 재조정 · 13:11~13:21 G2 홀리스틱 감사 · 13:21~13:31 인수 치환·커밋.
- 귀속 결과: 01 ~30m · 02 ~1h17m · 03 ~23m(벽시계 — agent-시간은 4배) · 04 ~25m ·
  **05 ~3h37m(~60%)** · 06 ~10m(+기계 검사는 슬라이스 내장). 합 ≈ 6h22m ≈ 실동작+분산 대기.
- **속도 개선 시사**: 최대 덩어리는 05 구현(S2 50m·S5 48m) — L8 병렬 coder 레버의 표적.
  둘째는 02 설계(4회 왕복 1h17m — 개정 3회가 절반).

### 개선 후보 큐 (r2″ 종결 후 사이클 재료)

1. **승인 왕복 해소**(최대 레버): 레인 settings 허용 규칙 사전 등록/permission-mode 조정 —
   r2″ 실측 ~45회·회당 감시 지연 포함 수 분.
2. 수렴 회로 조항 문면(적용 축 명시) — r2″ 오탐 2회 실증.
3. codex 재개 대기 자동화.
4. 미투입 플러그인 속도 레버: L8 병렬 coder·L1 G0 인터뷰·L3 사전 lint(속도 정본
   `2026-08-13-speed-plan-v0.md`) — §5.6 편성 규칙상 «결점 라운드 수정 사이클 동승».

### 레인 B(codex) 종결 — 유효 정지 (14:34 STOP · 14:40 done)

- 중단 커밋 `164332d`(rebuild(products): stopped — G2 direct scope checker blocker) ·
  working tree clean 실측. codex 실동작 계기 7h33m11s(레이어 분해는 codex 기록 형식상 불가).
- **하네스 재실측**: registry_gate(정본 dddjango/scripts·앵커 5630e2f2·codex .venv) →
  **exit 0 · 귀속 0 · legacy 잔존 5,406 · 해소 1** — codex 자기보고와 정확 일치.
- codex 자기보고(재실측 안 한 축): make test 6,857 passed·1 skipped / products 152 passed /
  strict mypy 3,199파일 / 최종 규율 감사 blocker 0 / makemigrations --check 무변.
- **STOP 4축**(STOP_FOR_USER_APPROVAL.md «G2 direct-scope checker blocker» 절):
  - #2 check-error-centralization **exit 1** — legacy child/parent 동적 StrEnum wire 값을
    정적 해석 불가·일반 분석 오류. `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED` 토큰이 아니라서
    2-리뷰어 runtime proof 경로도 못 탄다(토큰 커버리지 구멍).
  - #5 check-openapi-error-declaration **scope-render exit 2** — spec §3·Z2가 요구한
    framework-소유 401·503 선언을 checker가 «직접 BC error 반환 없는 광고»로 분류 +
    full-tree #63 slice가 legacy `api.py::get_openapi_schema` override 차단.
  - #6 check-context-isolation **scope-render exit 2** — checker가 selector를 받고도
    의도적으로 전역 스캔 → legacy 위반 + **승인 이관빚 #12(ParentAuth)까지** 직접 차단
    (빚 파일은 registry_gate 전용이라 직접 계열엔 무효).
  - #16 check-composition-root **scope-render exit 2** — profile-independent full-tree
    slice가 legacy `api.py` #437·`urls.py` #441 차단(Placement 밖·수리 불가).
- **판정: 유효 정지(정박 소진)** — 프로토콜 Phase 2 step6 «직접 실행 계열 exit 1 전부와
  scope-렌더 exit 2는 차분에 종속되지 않는 직접 G2 blocker» 문면을 축자 적용한 결과이고,
  해소 경로(검사기 계약 개정·Placement 확장·프로토콜 문면 개정)가 전부 비위임이라
  정박 재료로 재개 답이 서지 않는다. 구현·테스트·차분 게이트는 전부 green인 채의 정지.
- **쌍둥이 갈림 실증**: 같은 legacy 상존(5,406) 아래 레인 A는 같은 게이트를 통과(G2 완주),
  레인 B는 문면 축자로 정지 — «scope-render 직접 blocker» 규정이 brownfield 전역-슬라이스
  검사기와 근본 충돌함을 두 레인의 판정 분기로 실증. G1 정박 대리 2건(Z1 55P03·Z2 OpenAPI
  헤더)과 수렴 오탐 해제 2건은 기존 기록대로.
- 개선 후보 큐 추가(아래 ⑤): 검사기 scope 계약·프로토콜 직접 계열 차분 확장·#2 토큰 커버리지.
- 스트릭 판정(레인 A 통과 + 레인 B 유효 정지 = r1 동형 패턴)·S4 진입은 사용자 몫.

### 개선 후보 큐 추가 (레인 B 종결 후)

5. **G2 직접 실행 계열의 brownfield 계약**(퀄리티+속도 겸용): ⓐ #5·#6·#16의 full-tree/전역
   slice에 앵커 차분 또는 legacy 분류 도입 ⓑ 프로토콜 step6 문면에 «진단 전건이 앵커 기존분인
   scope-render exit 2» 처리 명문화 ⓒ #2의 legacy 동적 Enum 분석 불가에 PROOF 토큰 발화 —
   방치 시 모든 brownfield 라운드가 G2에서 같은 정지를 재생산한다(레인 A류 «해석 통과»는
   레인마다 갈리는 비결정).

### 레인 B ⑥a 채점 종결 (15:06 기동 · 15:15 완료 — 사용자 지시 「평가지 rubric 보고 만들고 보드에도 넣어」)

- 결과지 `workspace/eval/results/20260815-1506-pdrebuildlive-codex.md`(독립 채점자 1인·
  v5 frozen·클린룸 — 타 레인 클론·결과지 열람 0). ⑤ 봉인 값: A diff 0 · B 6,857+1skip
  (하네스 재실측 172.56s) · C 귀속 0(재실측)·#12 빚 내·ⓓ#153 물음 1.
- **치명 0 · Q 상**(WEAK 1 = NJ-4 — spec §3 «401·503 선언» ↔ 검사기 #5 문면의 «재료 축»
  결정FAIL∧의미PASS — 산출물 흠이 아니라 재료 충돌로 판정) · 실질성 degenerate 0 ·
  FC-1·FC-2 ⏸️(골든 행위표 공백 지속 + read-only 채점).
- **r2′ 충돌 4축 재발 0/4**: `get_purchasable_product_query`(#482) · V-접미/`_v1` grep 0 ·
  답 갈래 code Literal 3종+자연 전파 · admin panel/form/feature+#462 — respin 목적 달성이
  양 레인에서 교차 실증됨.
- **STOP 질 상**: G2 최종 (a)=4·(b)=0 분류 실물 대조 정확 · 과대 프레임 재발 0(r2′ 레인 B
  ~50건 과대 프레임과 대조) · 자가 승인 0 · 07:08 재분류분(#597 등 7건) 전건 수리 완수 실증.
- 자기보고 4건(152 테스트·#597 save/remove·설계 반영·Placement) 전건 실물 검증 통과.
- 잔여 결점 이월: FC-1 골든 공백(5라운드째) + **신규 관측: entitlements 가드 테스트가 구
  products 경로 importorskip 로 V1 경로를 영구 skip**(양 레인 공통 — 재료 후속 검토 후보).
- 보드 기입: codex 행 퀄리티 칸 = 통과(기계 3축·치명 0·Q 상 — 정지 라운드 명시). r2″ 종결
  국면 완료 — 남은 것은 사용자 결정(스트릭·S4·검사기 5종 수정 사이클 편성).

### 정정 + 레인 B 레이어별 실행 시간 실측 (15:4x · 사용자 지시)

- **정정**: 앞 절의 「codex 실동작 계기 7h33m」은 오독 — codex 판의 «Worked for 7h 33m»은
  **마지막 재개(07:08 수렴 오탐 해제) 이후 경과**였다. 세션 기록(rollout 22파일·활동 분)
  실측: 02:35~14:40 벽시계 12h05m에서 10분 이상 활동 공백 0 — 대기는 정박 지시 3회
  (04:54·05:45·07:01 → 각 6m·3m·7m ≈ 16m)뿐. **실동작 ≈ 11h49m**. 보드 정정 완료.
- 방법: `~/.codex/sessions/2026/08/15/rollout-*.jsonl` 22파일 — 타임스탬프(UTC→KST) 분 단위
  집계 + fork 경계(병렬 리뷰 3파일이 03:54:58~03:55:33 동시 시작 실측)로 구간 귀속.
  코덱스는 역할 서브에이전트 없이 fork 로 병렬 리뷰만 분리 — 그 경계가 레이어 전환점.
- 귀속(01~06 — claude 행과 같은 기준):
  - 01 지휘 ~27m: G0·빚 스캔(02:35~02:50) + 게이트·STOP 기록·중단 커밋 창
  - 02 설계 ~1h53m: 초안 64m(02:50~03:54) + 리뷰 반영 30m + Z 결정 반영 10m + 교정 9m
  - 03 리뷰 ~1h20m(벽시계): 병렬 4 회람 29m + 재리뷰·감사 32m + 재감사·G1 닫기 19m
  - 04 ➖: 단일 세션이 슬라이스마다 Red·구현을 섞어 분리 불가(05에 포함)
  - **05 구현 ~8h00m(≈68%)**: 06:16~14:28 − 게이트 9m − 검사기 실행 분
  - 06 검사 ~13m: 최종 감사(14:28~14:38)+G2 검사기 공식 실행(검사기 자체는 분 단위로 빠름 —
    함수 호출 실측 6m)
- **속도 시사**: 양 레인 동형 — 최대 덩어리는 05 구현(claude 60%·codex 68%). codex 총계가
  claude(6h02m)의 약 2배인 주요 축도 05(3h37m vs 8h00m)와 02+03(1h40m vs 3h13m — 정지
  3회의 재작업 포함). 병렬 coder 레버의 표적이 양 레인에서 재확인됨.

## 속도 개선 사이클 — coder 병렬화 자료조사 (08-15 저녁)

- 사용자 아이디어 접수: coder 병렬 실행 + 전체 설계도를 가진 coordinator 중재 + 슬라이스
  중첩 최소화·사전 합의 + 실무 관행(영역 분할·중첩 처리·미구현 의존=interface 약속) 조사.
- 검토 판정: **동의** — 실측 병목(05) 정중앙·직렬 강제 문면은 «의존 bottom-up»·«같은 파일
  동시 편집 금지» 둘뿐이라 step 4 편성 개정만으로 열림.
- 자료조사 3축 병렬 수행(WebSearch agent 3) → 종합 정본:
  **`2026-08-15-parallel-coder-research.md`**. 뼈대 수치:
  - 병렬 폭 실증 최적 **2~4, 8부터 하락**(CAID) · DORA 문턱 = 동시 미통합 작업선 ≤3.
  - **분할 품질=성패**: 응집 기반 분할일 때만 wall-clock 1.81~2.10x + 품질 동반 상승
    (Co-Coder), naive 파일 분할은 speedup 0·cost +44~60%, 조정 없는 2-agent는 success
    −30%(CooperBench — 통신 늘려도 안 풀림 → 중첩은 사전 분할로 제거).
  - **물리 격리 필수**: soft isolation은 single-agent보다도 나쁨(CAID 55.5<57.2) → worktree.
  - 계약은 산문 아닌 기계 실행물(mypy+ABC 시그니처가 우리의 등가물) · 합류는 wave마다
    (big-bang 금지) · conflict는 유발 coder 귀속 · fresh-context 감사 구조는 현행 유지 지지.
- 설계 초안(2.9.0 후보 L8) 6골자를 연구 문서 §4에 기록: wave 편성(wave 0=공유층 직렬 →
  wave 1+=무의존 슬라이스 2~3 병렬)·worktree+테스트 DB 분리·restricted 파일(migrations
  병렬 중 생성 금지→합류 후 일괄)·wave별 merge+green 관문·검증 2단 무변·구조화 배차 명세.
- 성능>속도 게이트: 검사기·리뷰 렌즈·감사 범위·게이트 문면 전부 무변(실행 편성만 개정),
  합류 검증은 추가 — 정보 손실 0·판정 무변 충족.
- 다음 결정(사용자): ① step 4 개정(2.9.0) 착수 ② 검사기 5종 수정(개선 후보 ⑤)과 동일
  릴리즈로 묶을지 ③ 첫 적용 BC.

### 보강 조사 2차 — Claude Code 생태계 실물 (08-15 저녁·사용자 지시)

- 요청: «superpowers 등 유명 플러그인·스킬의 병렬 방식 조사로 보강». 3축 병렬 수행
  (설치본 superpowers 원문 판독·생태계 레포 원문 대조·swarm 및 worktree 도구+실사용 후기)
  → 연구 문서 §5로 기입.
- 최대 발견: **superpowers는 구현 병렬화를 명문 금지**("Never dispatch multiple
  implementation subagents in parallel (conflicts)") — 병렬은 독립 조사·리뷰 한정.
  생태계 전체 수렴: 동시 write 실물=예외 없이 분할 소유(worktree/배타 파일 집합)·
  합류 자동화 도구 0(순차 통합 또는 충돌 시 정지)·과장 다수 판명(SuperClaude·
  wshobson·claude-flow placeholder 이슈·Roo 순차 재귀·Agent Teams «자동 격리» 오보).
- 실사용 유효 병렬 폭 3±2 — 논문(2~4)·DORA(≤3)와 삼중 일치. 병목 1위=합류 리뷰 처리량
  (우리는 기계 게이트라 완화 — 단 경량 감사 파이프라인화가 전제).
- 설계 초안 보정(§5.4): ⑹ 배차 명세에 Interfaces(Consumes/Produces 시그니처) 블록
  +소유 파일 배타 검증 ⑺ 충돌 시 자동 해소 금지·정지+귀속 판정 ⑻ 조정 장부 파일화.
  채택 안 함: 공유 디렉터리 swarm·자동 merge·런타임 자율 분해. best-of-N은 후보 큐만.

### 수정 계획 v0→적대 리뷰 9렌즈→v1 (08-15 밤·사용자 지시)

- 렌즈 로스터: 프레임워크 조사(premortem·ATAM·FMEA·HAZOP·red team·PRR·10th man·
  MAST·대규모 조직 실무) 후 «중복 최소·커버리지 최대» 8개+프로젝트 특화(정본 정합성) 1개
  = 9렌즈 병렬 독립 리뷰. 산출: `2026-08-15-parallel-coder-review.md`(군집 18·채택 15).
- 치명 7: 정본 충돌 4(coder.md 인수 Green 의무↔부분 Red·master 좌석 정의·migrations↔
  django_db 래칫·계약 개정=자가 승인) + 재료 결함 출구 부재(원인 배정에 STOP 접속 없음)
  + FMEA 탐지 불가 2(계약 mid-wave 무추적 변경·중복 통합의 의미 치환).
- 9렌즈 수렴 2축: ⑴ master 좌석이 규율 그물 밖 ⑵ 장부·기대 집합·계약이 «기록»이지
  «증거·유효 조건»이 아님. 강점 판정도 일치: 순차 합류=bisect·물리 격리·단계 게이트.
- 10th man: 이득 천장 45~90m/라운드(Amdahl) vs 승인 왕복·재료 재작업 풀이 3~10배
  → v1에 **B0 선행 트랙**(검사기 5종+승인 allowlist)으로 흡수·순서는 사용자 상신.
- v1 반영: Phase B 3단 분리(직렬 무해분→wave 0+master 직렬→병렬 폭)·Phase A 참조
  그래프+비용 차감 재설계·Phase C noise floor+토큰 문턱+드릴 2건·master 좌석 규율 절·
  증거 장부 스키마·원인 배정 ⓪~⑤(재료 결함=STOP 접속)·배타 술어 재정의·
  wave 0 스키마 전량 선확정·어휘 정정(«원인 배정»). 계획 v1=`-plan.md` 전면 개정.

### 사용자 결정 6건 + Phase A 실측 + codex 병렬 조사 (08-15 밤)

- 결정(08-15): ① 2.9.0=B0(검사기 5종+승인 allowlist) 선행·병렬=2.10.0 ② Phase A 즉시
  ③ 문턱=총 실행시간 ≥30% 단축·토큰 무관 ④ 실전 BC=products(2.8.0 동일 비교)
  ⑤ codex 병렬=조사 ⑥ 최소 BC 한계 수용.
- **codex 병렬 = 공식 지원 확인**: `multi_agent` stable·기본 on(로컬 0.147.0 충족)·
  `spawn_agent`/`wait_agent`·폭 `[agents] max_concurrent_threads_per_session`(V1 6·V2 4)·
  지시문만으로 위임 유도 공식 명시·자동 승인 상속·rollout child thread 증적 유지.
  제약: subagent별 worktree 없음(공유 트리=soft isolation) — 방식 선택(내장 subagent
  vs worktree+exec 다중 프로세스)은 잠정 보류.
- **Phase A 소급 분석(레인 A r2″ 실측) → 게이트 중단 권고**: 편집 공유 12%·참조 포함
  58% — 실측 의존 S1→S2→S3→S4→S5 완전 직렬(레이어 축 슬라이스=사슬 일치)·실효 폭
  1.00(최대 가정 1.67<2)·총 단축 최대 +10.3%(낙관)≪30%·중재 2~5회면 역효과·교차 삭제
  2건 실증. **병렬 coder(2.10.0) 게이트 중단 — 구현 착수 전 조기 판정으로 비용 0 회피.**
  B-①(배차 명세·증거 장부 직렬 무해분)만 후보 존치·B0는 확정대로.

### B0 착수 (08-15 사용자 지시 「1,2번까지 진행하고 보고」) + 후보 ⑥ 등재

- B0-1(검사기 5종)·B0-2(승인 allowlist) 병렬 착수. 커밋·릴리즈는 사용자 지시 대기.
- 개선 후보 큐 ⑥ 신설(사용자 발제): **프로토콜·지시서 문장 최적화** — 병렬 편성 없이
  문면 자체를 압축·AI 이해 친화 언어로 개정해 토큰·왕복·오독을 줄이는 축.
  전제: 성능>속도(정보 손실 0·판정 무변) — 리뷰 렌즈·검사기·문서 절단 금지·계측 근거 필수.

### B0 완료 (08-15 심야 — 로컬 수정+검증까지·미커밋)

- **B0-1 검사기 5종**: 공용 `anchor_diff.py` 신설(registry_gate 동형 N∖L 차분·공허 차분 exit 1
  세탁 차단) — #5·#6·#15·#16에 `--anchor`+빚 채널 결선(무-anchor 시 byte-identical 하위 호환),
  #2 동적 Enum 3유형 PROOF 토큰화(억제는 members_dynamic 정밀 한정 — backstop 2건 회귀
  발견→복원), step6·수정 모드 문면 개정, codex 미러 byte-copy 동기.
  검증: 릴리즈 세트 12종 전건 green(fixture 95/95·anchor smoke 9/9·backstop 675/675 —
  **메인 세션 독립 재실행으로 재확인**). 실전(앵커 5630e2f2·양 레인): #6 2→0(기존분 153
  보고·빚 #12 작동)·#16 2→0(기존분 39)·#5 legacy override 강등·#2 토큰 발화 —
  **r2″ STOP 4축 중 검사기 귀책분 소멸·양 레인 판정 동일화(비결정 해소)**. 잔여 red는
  재료 축 2건(#5 NJ-4=spec §3↔#5 광고 규칙·#2 base type required canon+빈 placeholder
  렌더 논점) = 사용자 결정 사안으로 이월.
- **B0-2 승인 allowlist**: 레인 A 세션 실측 — 승인 왕복 59회·대기 4.99h(4h33m 방치 1건=
  read-only cat 루프). 관찰 패턴 한정 7규칙(`settings.local.json`+정본
  `workspace/tools/lane-claude-permissions.{json,md}`) — 커버 ~34회(58%)·변수 경유 ~15회는
  발주문 «리터럴 경로 호출» 1줄로 추가 커버 가능(문서 기재). 포괄 허용·파괴·push 배제.
- 다음: 2.9.0 릴리즈(커밋·태그·설치본 갱신)=사용자 지시 대기 · 재료 축 2건 결정 대기.

### 재료 축 3건 반영 완료 (08-15 심야 — 2.9.0 릴리즈 준비 마감분·미커밋)

- **ⓐ spec §3 개정(401·503 wire 한정)**: 정본 spec 이 레인 저장소 두 곳에만 실재(«레인
  수정 금지» 우선) → apply-ready patch 로 준비
  `workspace/plan/2026-08-15-products-spec-401-503-respin.patch`(4 hunk — §3 선언 집합·§9
  오류 스키마·부록 A 주석·preflight ⑽ 8→9표면). 양 레인 `git apply --check` 통과.
  **레인 적용(docs-only respin 앵커 커밋)=사용자 지시 대기.**
- **ⓑ-1 #2 anchor 결선**: 4종과 동형(`--anchor`+빚 채널·무-anchor byte-identical 실측) —
  PROOF 토큰·분석 오류 exit 1 경로 무접촉(`pending_analysis` 관례 — 전건 강등에도 토큰-only
  는 proof 경로 유지). 교리 판정(base `type` required canon)은 코드 무결정 — 기존분 보고
  채널로만 표면화(이월 유지). step6 문면 «#2 제외» 삭제·codex SKILL.md 동등.
- **ⓑ-2 렌더 빈 골격 제외**: inventory 는 Coordinator 문면이 만듦 → commands 100행에 제외
  조항 추가 + 검사기에 `_skeleton_placeholder_module`(빈 모듈/docstring-only 만·파싱 불능
  fail-closed) 신설로 union 대응 의무 정합(#2 규칙 본문 무접촉·하위 호환 유지).
- 검증: **세트 13종 전건 green — 메인 세션 독립 재실행 재확인**(fixture 95/95·anchor smoke
  9→**11/11**(C1 강등+placeholder 제외·C2 신규·기존 분리 추가)·registry_gate 6/6·backstop
  675/675 mismatch 0·byte-copy OK). 실전(앵커 5630e2f2·양 레인): #2 exit 2(findings 4)→
  **exit 1**(신규 0·기존분 2 강등·잔여=PROOF 토큰 2 — proof 경로) 양 레인 동일. #5 는
  신규분 2씩 잔존=정상(코드에 선언 실재 — 개정 spec 재구현 라운드에서 해소되는 축).
- 상태: **2.9.0 릴리즈 준비 완료** — 실행(수정분 커밋 선행→`make release` 대화형 minor)=
  사용자 지시 대기.

### coder 내부 시간 분해 실측 (08-15 — «병렬 외 속도 개선» 주제 착수 재료)

- 방법: 새 테스트런 불요 — 봉인 r2″ 레인 A 원장(세션 09566ef7 subagent jsonl 20본)을
  연속 레코드 delta 귀속으로 분해(스크립트 scratchpad `speed/coder_profile.py`).
  B0-2 prompted 휴리스틱 재사용. 방치 사고 4h33m(재시도 agent 의 cat 루프)은 별도 계상.
- **coder 7 agent 실동작 ≈3h09m 분해: 모델 생성 2h37m(83%) · 승인 대기 21m33s(11%) ·
  도구 실행 ≈10m(5% — 테스트 5m37s·검사기 2m28s·마이그레이션 22s)**. 편집·Read 도구
  자체는 초 단위(합 1분 미만).
- 생성의 정체: coder 출력 672,854 tok(API 메시지 402·중복 제거)·생성 9,420s → **71.4 tok/s
  = 디코드 속도 상당(왕복 지연 아님·토큰량 병목)**. 가시 출력은 394k chars(코드 53%·보고
  산문 23%·Bash 커맨드 17%·Edit 원문 재타이핑 4%)≈110k tok 뿐 — 원장에 thinking 본문이
  signature-only 로 벗겨져 있어 차분으로 확정: **출력의 ~83%가 thinking(사고) 토큰**.
- 슬라이스별: S1 97%·S2 84%·S3 89%·S5 80% 생성 — S4(배선)만 승인 29%(8m46s — B0-2 가
  이미 공격). 02 설계(architect 1h10m)도 99.5% 생성·270,890 tok 로 같은 축.
- 함의: 병렬·도구·승인이 아니라 **«사고 토큰 유발량»이 병목의 정체** — 후보 ⑥(문면
  최적화·결정 완결성 높은 spec/발주문)이 정공. effort 하향은 성능>속도 원칙과 충돌
  위험 — 기계 슬라이스 한정 실험 후보로만. 검증은 다음 실전 라운드 tok 실측 비교(무비용).

### 레인 B(codex) coder 시간 분해 실측 (08-15 — 레인 A와 병목 구조 상이)

- 방법: r2″ 레인 B rollout(주 스레드+child thread 다수 — multi_agent 구조 실증)을 같은
  walker로 분해. 주 스레드 «도구 실행» 9.5h의 정체=`wait_agent`(자식 폴링 300s 블록)라
  주 스레드 시간은 자식과 중복 — 순수 worker 스레드 2본으로 재실측.
- **child coder 실측(06-16·06-40)**: 생성 5.9h/4.1h · 도구 0.6h/0.3h · **모델 턴 662/395 ·
  턴당 생성 32~37s · 처리율 2.3~2.4 tok/s · reasoning 비중 39~45%**. 실제 shell 실행은
  974회 0.7h(주 스레드)로 소형.
- 함의: **레인 A=출력 토큰량 병목(71 tok/s 디코드 한계·사고 83%) vs 레인 B=턴 수×턴당
  왕복 지연 병목(턴당 73 tok 출력에 32s — prefill 11~12M/스레드+지연 지배)**. 양 레인 공통
  레버=① 결정 재추론 제거(확정표 — claude 는 사고 토큰↓·codex 는 심의 턴↓)·② 턴 구조
  다이어트(codex 에 특히 큼). ③ effort 하향은 claude 는 agent frontmatter `effort` 필드로
  공식 가능(low~max — 조사 1 확정·code.claude.com/docs/en/sub-agents)·codex 는 조사 2 대기.

### 표적 조사 3건 완료 + 계획 v0 (08-15 — «결정 동결» 트랙)

- 조사 ①(Claude Code): subagent frontmatter `effort`(low~max) 공식 존재 — 슬라이스별
  차등 가능. thinking budget 수치 제한·호출 시점 동적 조정·사고 억제 공식 문구는 없음.
- 조사 ②(codex): child별 effort 오버라이드 공식 3경로(`[agents]` 기본값·spawn 명시·
  `codex exec -c`)·`/model` 턴 경계 전환. `[profiles.X]` 문법은 0.134.0 폐지 주의.
  spawn 오버라이드 리그레션 이슈(#20077/#32031) — 실측 선행 필요.
- 조사 ③(Anthropic 지침+양식): thinking 은 질의 복잡도 자동 비례·«결정 재방문 금지»가
  공식 절감 샘플·복잡한 프롬프트는 thinking 증가(경계 조건)·effort 가 문구보다 우선
  레버(calibrated control). 양식은 Nygard/MADR(한 문장 결정)·DMN Unique(한 항목=한 결정)·
  Rust RFC(reference-level 상세+unresolved 3분류)·freeze 예외 절차 차용.
- **계획 v0 작성**: `workspace/plan/2026-08-15-decision-freeze-plan.md` — C0 문면 개정
  (확정표 3종·집행성 판정·coder 반환 규율·impl-notes 규율·턴 다이어트 — 2.10.0 후보)
  · C1 다음 라운드 무비용 실측(baseline=r2″) · C2 effort 실험(옵션·기본 보류).
  결정 대기: 리뷰 강도·C0 착수 시점(2.9.0 과의 순서).

### 2.9.0 릴리즈 실행 완료 (08-15 — 사용자 지시)

- 선행 커밋 2건(03b9760 기능분·590f626 문서분) → `make release` minor: 검증 세트 전건
  green 재실행 → release 커밋 732b39b · 태그 dddjango--v2.9.0 · push · GitHub Release 생성.
- gh 계정 changja88 전환 후 push·릴리즈, 직후 changhyun-hue 원상 복구.
- 설치본 갱신: claude(`plugin update dddjango@changja88-dddjango` → 2.9.0)·
  codex(`plugin marketplace upgrade` → 2.9.0) — 양쪽 scripts byte-identical 확인.
- 결정 동결 계획 v0 경량 적대 리뷰 3렌즈(정합성·premortem·10th man) 병행 기동 — 결과
  도착 시 v1 반영 예정.

### 경량 리뷰 3렌즈 + 선행 프록시 실측 → 계획 v1 (08-15 심야)

- 리뷰 수렴 2축: ① ⓐ(결정 재추론)의 크기 실측 0 — 선행 프록시 요구(premortem 1위·
  10th man 반론 1·4) ② coder 재추론=품질 장치(재료 결함 3회 검출 주체)·freeze 왕복
  비용 역전 ~2h·impl-notes 신설=무게이트 명세 수정 채널(정합성 치명 1·2).
- **프록시 실측 2건(기존 원장·무비용)**: ⓐ-1 coder 간 중복 재조회 — 명세·표준류는
  design-spec 1종 11회뿐(표준 final.md 도구 조회 0 — 스킬 로드 상주=prefill 축).
  ⓐ-2 codex reasoning 요지 1,633건 전수 분류 — **결정·해석류 9.4% · 검증·조사·읽기
  52.2%** · 구현 16% · 계획 8.5% · 기타 13.8%.
- **판정: v0 핵심 전제(사고 몸통=결정 재추론) 실측 기각 → v1 개정** —
  확정표 3종+freeze+반환 규율 **보류**(천장 ~10%대·치명 2·비용 역전) ·
  **C0′ 저위험 문면 3건**(집행성 판정+증거 1행 / 재방문 금지+표준 충돌 면제 /
  발주 리터럴 경로 — 2.10.0 후보) · **C3 컨텍스트 다이어트를 본선 후보로 피벗**
  (검증·조사 52%·cache_read 73.8M·prefill 11~12M 직격 — 다음 사이클 조사) ·
  C2 effort=사용자 결정 유지. 계획 정본 `2026-08-15-decision-freeze-plan.md` v1 갱신.

### C0′ 저위험 문면 3건 반영 완료 (08-15 심야 — 로컬 수정+검증·미커밋 · 2.10.0 후보)

- ① 집행성 판정+증거 1행: design-review-{ddd,api,db}(api 는 DESIGN_CONTRACT_REVIEW 한정)·
  discipline-reviewer(Phase 1 규율 lens 한정) — «가능=명세 확정 결정 3곳 인용·불가=막히는
  절 지목·인용 없는 가능 판정 무효».
- ② 결정 재방문 금지+면제 1줄: coder·acceptance-tester — «명세↔정본 표준 충돌 발견=새
  정보 → 기존 반송 축으로 즉시 보고»(재추론의 결함 검출 기능 보존 — 10th man 면제 반영).
- ③ 검사기 확장-리터럴 호출: coder 규율 신설+Coordinator step4 입력에 플러그인 설치 루트
  추가(B0-2 잔여 승인 ~15회 커버 — 부분 실행 비게이트·TARGET=`.`·렌더 기록 `${CLAUDE_
  PLUGIN_ROOT}` 표기 정본 불변 병기).
- 의도적 비대칭: ③은 claude 한정(승인 매칭 실측 근거가 claude 레인) · 턴 묶기(읽기 전용
  확인 한정·TDD 사이클 제외)는 codex coder 한정(턴 수 병목이 codex 실측).
- 미러: codex dddjango-{coder,acceptance-tester,design-review-×3,discipline-reviewer}
  SKILL.md 동등 문면. 검증 세트 13종 전건 green 재실행 확인.
- C3 선행 조사(컨텍스트 구성·발췌 단위·안전망) 백그라운드 진행 중.

### C3 선행 조사 결과 — 보류 판정 + 스킬 오주입 결함 발견 (08-15)

- 실측(coder 7세션): 기동 ~39k 중 스킬 stub 7.3k(19%) · **final.md 126.7k 는 기동
  미주입·세션 Read 2건 1.9k 뿐** · 턴당 재소비 171k 중 스킬 몫 4.3% · 발췌 상한
  stub 3개 2.2k/턴(~1.3%). 재소비 몸통=소스 Read 22.5%·Bash 출력 21%·spec 재독
  18.8%·에코 15.7%·시스템/도구 고정 ~30k.
- **C3 보류**(전제 «스킬 재료=재소비 몸통» 실측 기각 — v0 확정표와 같은 방식으로 조사
  게이트가 구현 전에 죽임·비용 0). 재개 조건 2건 계획 §3 기록.
- 안전망 확인: 기계 검출 456(84.8%)/ⓓ 82 — ⓓ 판정 소유는 reviewer 72·architect 4·
  coder 0. 경계 성립.
- **부수 발견(독립 수리)**: coder frontmatter 동명 스킬 3종이 **dddart 1.1.1 로
  오주입**(원장 Base directory 실측 — Django coder 가 Flutter 하우스룰 stub 수령·
  r2″ 는 그럼에도 귀속 0 완주 = 표준은 design-spec+검사기가 나름). 한정 표기 문법
  공식 확인 후 dddjango agents 전수 수리 예정.

### 스킬 오주입 결함 수리 (08-15 — dddjango agents 전수·미커밋)

- 공식 문법 확인(code.claude.com/docs/en/sub-agents — qualified syntax): agent frontmatter
  `skills:` 의 무한정 이름은 동명 충돌 시 해석이 비결정(자기 플러그인 우선 규칙 없음).
- 수리: 7 agents 전수의 skills 항목을 `dddjango:<skill>` 한정 표기로 일괄 개정(오주입
  실측 3종만이 아니라 전 항목 — 미래 충돌 원천 차단).
- 검증: 세트 13종 전건 green + `claude plugin validate dddjango --strict` 통과.
- 주의: 설치본 2.9.0 캐시는 무한정 표기 그대로 — **다음 라운드 전 2.10.0 릴리즈+설치본
  갱신이 있어야 실전에 반영**된다(그 전 라운드는 종전과 동일한 비결정 해석).

### 2.10.0 릴리즈 실행 완료 (08-15 — 사용자 지시)

- 선행 커밋 2건(a9c158b 기능분·4432368 문서분) → make release minor: 검증 전건 green →
  release 커밋 5fec35a·태그 dddjango--v2.10.0·push·GitHub Release. 계정 전환→복구 동일.
- 설치본: claude 2.10.0(한정 표기 8건 반영·scripts byte-identical 확인)·codex 2.10.0.
- 이로써 C0′+스킬 한정 표기가 실전 반영 가능 상태 — 다음 라운드 검증 항목: ① 스킬
  Base directory 전건 changja88-dddjango ② 승인 왕복 수 ③ 집행성 판정 실효 ④ thinking
  비율(r2″ 대비).

### 파이널 리뷰 5렌즈 완료 — 발견 종합 (08-15 심야)

- 렌즈: ①통합 표면 ②미러 동기 ③죽은 참조 ④하네스 계약 ⑤이월 결점 + ⑥설치본 드리프트
  (직접 — 양쪽 byte-identical·드리프트 0). 상세는 각 agent 보고(본 절은 색인).
- 치명 4: ①C1 codex 지식 스킬 4종 dddart 충돌(무한정 로드가 유일 경로) ·
  ②codex SKILL.md:120 `${CLAUDE_PLUGIN_ROOT}` 잔존(게이트 호출 해소 불능) ·
  ②#82 유사 변형 보강 codex 누락 · ④F1 빚 파일 이중 파서 코퍼스 불일치(gate=정규화·
  검사기=원문 — 현 실물은 우연 일치).
- 중요 다수: ①I1 commands 디스패치 무한정 7곳(dddart 동명 4종) · ④F2 clean 시 앵커
  검증 침묵 생략 · F3 usage exit 드리프트(gate·#6=2·나머지=1) · F4 build_anchor 축약
  실물 · ③참조 끊김 4(architect §2/§4/§0-1·discipline §2 OHS)·걷힌 번호 범위 4·proof
  주체 서술·정본 비동봉 29종 · ②codex 축약 3(감사 빈도·테스트 보존·G2 배너 증거) ·
  ⑤#5 태그 부재(빚 채널 원리 봉쇄)·#2 출력 문구 오독.
- 안심: 전 발견이 fail-closed 방향 — 거짓 green 구멍 0. 12-slot 라벨 3곳 완전 일치·
  registry 순서 27종 일치·토큰 고아 0.
- 보드에 2.9.0·2.10.0 행 기입(누락 소급).

### 파이널 리뷰 A 배치 — 문면·개명 스트림 완료 (08-15 심야 · 코드 스트림 병행 중)

- claude commands: 디스패치 8곳 `dddjango:` 한정(+한정 표기 규약 1줄)·houserules 인용 한정·
  범위 표기 단서·proof 주체 일반화(registry #2·#5·#15)·registry # 접두 2곳·mismatch 표제
  일반화·build_anchor 축약 수용 명시·후보 초과 처리 이식·G1′/첫-Green 표기 통일.
- claude agents: architect 오참조 4건(§4→§3 ×2·§2 통신→§1 트리 22~32행·§0-1→django §10.4)
  +OHS 주해 정정+산출물-우선 쓰기 이식 · discipline OHS 참조 교정 · coder/acceptance
  재방문 절에 «행 확인은 재방문 아님» 보강 · acceptance frontmatter에 ninja 추가(§2.1
  셋업 의무의 도달 경로 확보).
- codex 미러: `${CLAUDE_PLUGIN_ROOT}` 잔존 치환+scripts 위치 해소 문장·#82 유사 변형
  보강·축약 3건 복원(감사 빈도·테스트 보존·G2 배너 profile 증거)·architect 동일 오참조
  5건·description 정합·예시/트래커/표기 복원 — 전건 claude 동등.
- **codex 지식 스킬 4종 개명**(dddart 충돌 소멸): `dddjango-{architecture-ddd,discipline-
  cleancode,discipline-houserules,implementation-test}` — frontmatter name·SKILL.md 참조
  82건 치환·corpus_mirror_sync 접두 우선 매핑. claude 스킬 description 충돌 4이름도
  `dddjango:` 한정(M1).
- 검증(문서 계열): corpus_mirror·corpus_lint·spec_lint·tree_mirror·reverse_coverage·
  plugin validate --strict 전건 green. 코드 스트림(F1·F2·F3·#5 태그 등) agent 완료 후
  전체 13종 재실행 예정.

### A 배치 코드 스트림 완료 + B 결정 8건 확정·집행 개시 (08-15 심야)

- **A 코드 스트림(agent) 완료·메인 독립 재검증 전건 green**: F1 빚 매칭 정규화 통일
  (debt_match 공용·registry_gate import) · F2 앵커 재료 선검증(5종·clean 침묵 통과 봉쇄) ·
  F3 usage exit 1 통일(gate·#6) · S1·S2·S4·S6(복제 3벌→공용) · #5 findings `[#63]` 태그
  (빚 채널 개통) · #2 출력 문구 조건화. smoke 14/14·gate 7/7·fixture 95(무-anchor
  byte-identical)·backstop 675·byte-copy·validate --strict. 잔여 논점: #2·#15 render
  무태그(복수 규칙 소유 — 빚 채널 봉쇄 잔존·후속 후보) · S2 잔여(`#12x` 실재 대조 밖).
- **B 결정(사용자 · 08-15)**: ① base `type` canon **승인(b)** ② 401·503 patch+선언 제거+
  entitlements repoint **묶음 수리 사이클 승인** ③ FC-1 골든=**라운드 준비 필수 산출물
  명문화**(다음 기동 전 하네스 작성→사용자 확인) ④ **스트릭 N=2 확정·S4 진입·다음 BC=
  billing 재도전** ⑤ C2 effort 실험 **동승 승인 — 단 billing 라운드 제외·그 다음부터**
  (변형 agent 는 그 시점에 생성·릴리즈) ⑥ dddart 는 사용자 직접 수리 — 점검 프롬프트
  전달(`workspace/plan/2026-08-15-dddart-name-isolation-prompt.md`) ⑦ #545 `_events` 가드
  읽기 명문화 승인 ⑧ 정본 비동봉=현상 유지+문구 정정.
- 집행: ①⑦⑧=교리 수리 agent · ②=레인 수리 agent(편집·검증까지 — 커밋은 메인) 병렬 기동.

### ② 레인 묶음 수리 사이클 완료 (08-15 심야 — 양 레인 커밋 봉인)

- 레인 A: docs fe4389f5(spec §3·§9·부록 A·preflight 9표면) + code 6969ef85(401·503 선언
  2행 제거·선언-단언 e2e 동반 갱신·entitlements repoint) — **전체 6835 passed·skip 0**
  (종전 6834+1skip — P15 스냅샷 생존 pass 전환). pre-commit(ruff·mypy strict) 전건 통과.
- 레인 B: docs f3a10be + code 13c79a6(product_catalog controller — 실경로 확인 수정·openapi
  선언 테스트 동반 갱신·repoint) — **전체 6858 passed·skip 0**(종전 6857+1skip).
- #5 재실측(설치본 2.10.0·앵커 5630e2f2·빚 파일): 양 레인 exit 2·신규분 2 → **exit 0·
  신규분 0**(기존분 1=api.py get_openapi_schema override 보고 채널 무변). #2 무변(exit 1·
  기존분 2·PROOF 토큰 2 — ① canon 수리가 반영되면 기존분 2도 소멸 예정).
- wire 무접촉 실증: 중앙 401/503 wire 테스트 전건 green 유지. 이월 결점 1(entitlements
  영구 skip)·5(401·503 잔존·patch 미적용) **종결**.

### 교리 수리 ①⑦⑧ 완료 — B 집행 전건 종결·2.11.0 릴리즈 준비 완료 (08-15 심야)

- ① canon: 검사기 `narrowed_required_canon` 면제(3조건 동시 — 식별자 field·ErrorCode 좁힘
  정확 일치·공통 default→required. 드리프트·역방향·타 field 는 계속 위반) · 정본 #572 예외
  1문장 · slot 9 병기 8곳(ninja final.md 3벌 포함 — corpus --write 로 소스 splice) ·
  backstop 양방향 4케이스 신설(675→**679**) · 레인 A #2 재실측: base-canon 기존분 2 →
  **0 소멸**·PROOF 토큰 2·exit 1 유지.
- ⑦ #545 «_events 비소모 읽기 인정» 명문화(spec :867·검사기 무변) · ⑧ 비동봉 문구 4곳.
- 메인 독립 재검증: **전체 세트+validate 전건 green**(fixture 95·smoke 14/7·backstop 679·
  byte-copy·corpus 11/11). **2.11.0 릴리즈 준비 완료 — 실행 대기.**
- 이월 결점 현황: 1(entitlements)·5(401/503)·6(canon)=**종결** · 2(_events)=명문화 완료 ·
  3(FC-1)=다음 라운드 절차화 · 잔여 비차단: #2/#15 render 무태그·S2 `#12x`류·C2(billing
  다음)·dddart(사용자 직접).
