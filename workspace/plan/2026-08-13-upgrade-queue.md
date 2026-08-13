# 업그레이드 큐 (2026-08-13 — 라운드 2′ 중단 후·다음 라운드 전)

**발주**: 사용자 08-13 — 「라이브런 중단(billing 과대·소형 BC 재선정 예정). 그 전에
업그레이드: ① 사용자 input 요청 포맷 정규화 ② 구조적 속도 개선. 표로 관리, ①부터.」
플러그인 갈래는 **한 릴리즈로 묶는다**(①+②+③ — 스트릭 리셋 1회).

## 관리 표

| # | 항목 | 내용 | 상태 |
|---|---|---|---|
| 0 | 라운드 2′ 종결 처분 | stopped 태그 2종·수확 `workspace/eval/results/20260813-r2p-harvest.md`·대장 기입 | **완료(08-13)** |
| 1 | 입력 요청 포맷 정규화 | 아래 §1 — claude=AskUserQuestion 의무화·codex=request_user_input 우선+평문 fallback 2단 | **구현 완료(08-13) — 릴리즈는 ②·③과 묶음** |
| 2 | 구조적 속도 개선 | 아래 §2 — L4 병렬 메커니즘·L2 BC-범위+계측·L7 소폭 2건 (L1 이월·L3 후속 조사·L8 보류) | **구현 완료(08-13) — 검증 green** |
| 3 | 플러그인 명확화 동승 2건 | §5.4 «wire 계약≠구현 형태·RFC wire+표준 레시피=지원 조합» 명시·:23 완화·corpus 재동기 | **구현 완료(08-13)** |
| 4 | 라운드 재료·프로토콜 규율 4건 | ⓐ 스팩에 플러그인 프로필 «이름» 차용 금지(레시피는 풀어 쓴다) ⓑ 빚 파일은 경로×**발현 규칙 전수** 수록 — anchor-preflight 항목 추가 ⓒ 요청문 템플릿에 「정지 커밋 후 남긴 열린 질문은 종료 상태를 해치지 않는다」 한 줄(적대 B-1 처분) ⓓ RFC 9457 신규 범위의 profile 어휘·12-slot·checker 렌더 표현 — §5.4 선언과 slot 계약의 간극을 명시적 빚으로(적대 4렌즈 수렴) | 대기(다음 라운드 준비에 반영) |
| 5 | 새 BC 소선정 | 실측 게이트 크기 상한 하향 후 재추첨 | 업그레이드 후 |

## §1 입력 요청 포맷 정규화 (조사·설계)

### 문제 (라운드 2′ 실측)

- claude 레인: STOP·재개 질문이 **평문 텍스트**(A/B/C 자유 입력)로 나감 — AskUserQuestion
  호출 0 실측. 코디네이터 문서가 G0 빚 결정에만 AskUserQuestion 을 명시하고, STOP 절(H2)은
  «기록 형식»만 규정·«질문 채널»은 미규정이라 생긴 공백.
- codex 레인: 쌍둥이 SKILL 이 «게이트=평문 질문(binary 승인뿐)»으로 규정 — 번호 메뉴는
  자발 형식(1/2)이지 계약이 아님.

### claude 판 설계 (확정안)

코디네이터 문서에 신설: **「사용자 입력이 필요한 모든 닫힌 선택(게이트 결정·STOP 선택지·
배치/폴더 질문)은 AskUserQuestion 으로 제시한다 — 옵션 label=선택지, description=대가 한 줄.
STOP_FOR_USER_APPROVAL 은 기록·정지 커밋을 먼저 완료한 뒤(정본=기록 파일) 같은 선택지를
AskUserQuestion 으로 제시한다 — 커밋이 유효 종료 조건이고 질문은 입력 채널이다(사용자
부재면 무응답으로 남을 뿐).」** 자유 텍스트 답이 필요한 물음(사유 입력 등)만 평문 유지.

### codex 판 조사 결과 (0.147.0 실측 + 공개 자료)

| 안 | 내용 | 근거·대가 |
|---|---|---|
| ⓐ **`request_user_input` 플래그** | codex 에 구조화 질문 도구 `request_user_input` 이 존재 — 기본은 **plan mode 전용**이고, feature flag `default_mode_request_user_input`(0.147.0 «under development»·기본 off)을 켜면 default mode 에서도 노출 | `codex features enable default_mode_request_user_input` 한 줄·되돌리기 가능(disable). 대가: under development 라 UI/안정성 미보증 → **스모크 테스트 후 채택**. 커뮤니티도 동일 요구(openai/codex #12694·#11892·discussion #11717) |
| ⓑ 텍스트 프로토콜 정규화 | 플래그 없이, 쌍둥이 SKILL 에 질문 «형식 계약» 신설: 닫힌 선택지 번호 목록+선택지마다 대가 한 줄+기본값 표시+「번호로만 답하라」 | 설정 무변경·항상 작동. 대가: 방향키 UX 없음 |
| ⓒ MCP elicitation | `tool_call_mcp_elicitation` stable 인 것을 이용해 질문 전용 MCP 서버 동봉 | 기각 — 플러그인에 서버 동반은 과설계(원칙 05) |

**권고**: ⓐ 스모크 → 성공 시 쌍둥이 규정을 «request_user_input 이 있으면 그것으로, 없으면
ⓑ 형식으로» 2단으로. 실패 시 ⓑ만. 어느 쪽이든 ⓑ 형식 계약은 신설한다(fallback 겸
claude AskUserQuestion 과 같은 구조 — 두 하네스가 같은 «선택지+대가» 구조를 보이게 된다).

### 스모크 실측 (08-13 — 1단계 완료)

- 플래그 enable 후 `codex exec` 프로브: **TOOL_PRESENT** — default mode 에 도구 노출 확인.
- 스키마 실측: `questions[]{header(≤12자)·id(snake_case)·question·options[]{label(1~5단어)·
  description(대가 한 문장)}}` · 선택지 2~3개·권장은 첫 번째+«(Recommended)»·"Other" 는
  클라이언트가 자동 추가 — **claude AskUserQuestion 과 구조 동형**. 쌍둥이 규정을 같은
  «선택지+대가» 구조로 쓸 수 있다(의도된 비대칭 불요).
- 남은 확인 1: 대화형 TUI 렌더(방향키 선택 UI) — exec 로는 검증 불가·사용자 1분 테스트.

### 스모크 2단계 (08-13 — 대화형 UI 실측·채택 확정)

- 1차 시도 실패 원인=**세션 나이**: 플래그 이전(15:16)에 시작된 열린 TUI 안에 명령을 입력 —
  도구 목록은 세션 시작 시 고정. exec 강제 호출로 배선 확증(`request_user_input is not
  supported in exec mode` — 도구 존재·비대화형만 차단).
- 2차(새 세션): **선택 UI 렌더 확인** — Question 1/1·방향키·(Recommended)·"None of the
  above"+notes(tab) — **default mode 에서 작동**(plan 모드 불요 — 사용자 확인 사항).
- **채택 대가**: codex 쪽은 사용자 config 의 feature flag `default_mode_request_user_input`
  ON 이 전제(현재 ON). 플래그 off·구버전이면 평문 fallback 이 자동 적용(2단 규정).

### 구현 기록 (08-13 — 완료·검증 green)

- claude `dddjango/commands/dddjango.md` :172 «게이트 질문·STOP 기록 형식»에 **입력 채널**
  규정 추가: 닫힌 선택=AskUserQuestion(label=선택지·description=대가)·STOP 은 **기록+정지
  커밋 후** 같은 선택지를 AskUserQuestion 으로(기록=정본·질문=입력 채널·무응답 유효).
- codex `codex-dddjango/skills/dddjango/SKILL.md` — ⑴ :195 쌍둥이 입력 채널 규정(도구 우선·
  평문 fallback·STOP 커밋-후-질문 동일) ⑵ 게이트 절 재정의 «구조화 질문 우선·평문
  fallback» ⑶ 감수 후보 제시 bullet 을 두 경로 대응으로.
- 검증: corpus 11/11·spec_lint·checker_lint·tree_mirror·reverse_coverage·fixture 90/90·
  gate smoke 6/6·bc_registry_smoke·scripts byte-copy·**backstop 675/675 무변** — 전부 green.
  STOP 리터럴 행 동수 6·6 유지.

### 스모크 절차 (사용자 1분)

```
codex features enable default_mode_request_user_input
cd <아무 폴더> && codex "테스트: request_user_input 도구가 보이면 그 도구로
'A 또는 B 를 고르라'는 선택지 질문을 제시하라. 없으면 '도구 없음'이라고 답하라."
```
선택 UI 가 뜨면 성공. 끝나면 `codex features disable …` 로 원복(채택 시 유지).

## §2 구조적 속도 개선 (08-13 — 사이클 완료·검증 green)

**대원칙(사용자 08-13)**: 성능(산출 품질)이 최우선 — 모든 레버는 «정보 손실 0·판정 기준
무변»일 때만 채택. 리뷰 렌즈·검사기·게이트 무접촉.

### 계측 (추측 최적화 방지 — 실측 2건이 가설을 기각)

- **중복 컨텍스트 가설 기각**: 레인 A 11개 디스패치의 prompt 실측 1.5k~8k자 — 명세는
  경로 전달·서브에이전트 자체 Read 가 이미 관행. L7 대형 다이어트(문서 절단·전문 전달
  제거)는 근거 없음 → 기각(성능 우선과도 일치 — 에이전트 정의 문서가 곧 품질 계약).
- **직렬 dispatch 확정**: 레인 A 병렬 Task 다발 0회(문면 «병렬» 무력) — L4 의 진짜 결함은
  «병렬»의 실행 정의 부재.

### 구현 (쌍둥이 대응 — 전 항목 판정 무변)

| 레버 | 수정 | 파일 |
|---|---|---|
| L4 | 병렬의 «실행 정의» 명문: claude=한 응답 Task 다발·codex=전부 spawn 후 wait + discipline lightweight 를 다발에 합류(모든 리뷰어 타 노트 미수신=순서 의존 0) | dddjango.md Phase1 2·3 / 쌍둥이 SKILL 2·3 |
| L2 | coder 내부 루프=BC-범위 pytest 한정·전역 스위트 내부 루프 금지(판정은 게이트 소유 불변) + 완료 보고에 pytest 호출 수·소요 계측 한 줄 | agents/coder.md / 쌍둥이 coder SKILL |
| L7 | 소폭 2건만: codex SKILL 본문 재독 금지(rollout 4회 적재 실측)·(①에서) 산출물 요지 전달 관행 유지 | 쌍둥이 SKILL :20 |
| ③ | §5.4 「이 절이 고르는 것은 wire 계약이지 구현 형태가 아니다·RFC 9457 wire+표준 레시피=지원 조합」+§6 주석+:23 요약 완화 — corpus 소스 재동기(--write) | architecture-api 양 쌍둥이+corpus |

- 처분: L1(G0 인터뷰)=운영 모드 재료로 이월 · L3(사전 lint)=조사 후속 · L8(병렬 coder)=
  **영구 레버로 재분류(08-13 사용자 지적 — 슬라이스 병렬은 운영 모드 상시 자산·L6 일괄
  국면은 1회성이라 그 재료가 아님)**: 이번 릴리즈 제외는 유지(귀속·통합 복잡도+테스트 DB
  격리 전제)하되 다음 라운드에서 파일-겹침·후반 병렬 여지 실측 → 별도 설계 트랙 ·
  L5(postgres 격리)=하네스 갈래 별도.
- 검증: corpus 11/11(재동기 후)·spec/checker/tree/coverage lint·fixture 90/90·smoke 6/6·
  bc_registry_smoke·byte-copy·**backstop 675/675 무변** — 전부 green.

## §3 적대 리뷰 4렌즈 (08-13 — 사용자 발주·병렬 다발 실행·33건 → 전량 처분)

렌즈: A 성능 회귀(7건)·B 문면 충돌(10건)·C Goodhart/게이밍(13건)·D 쌍둥이/동결(8건 —
FROZEN·리터럴·byte 는 all-clear). **기각 0** — 전 발견이 «문장의 주어·한정 부재» 유형이라
최소 문면 수정으로 수용. 상충 2쌍은 해소: ⑴ STOP 질문 «무조건 의무»(C⑦)↔«기록 후 종료»
계약(B1) → **실행 모드 분리**(대화형=기록→질문→반송·커밋 없음 / 자율=기록+커밋=유효
종료·질문은 발주가 종료를 계약했으면 생략 가능) ⑵ 재리뷰 병렬(C⑩)↔단독 재호출(B7) →
«둘 이상이면 다발·하나면 단독 정당».

### 반영 수정 (클러스터별)

| 클러스터 | 수정 |
|---|---|
| §5.4 문단(최다 피격 — C상①·B상2·A중·B중3·C중⑧·C하⑨·D×3) | 전면 재작성: 주어=**신규 범위** 명시(preserve-established 는 대상 아님 — 재작성 면허 차단)·«지원 조합»→«wire 규칙상 모순 아님»+G2 profile 열거 부재 명시·채택=G1 표면화(STOP 대상)·정지 서사 중립화·레시피 정본=구현 스킬(경계 획정). :23 요약·§6 주석·corpus 동기 |
| L2 coder(A상1·C상②③④·B하9·10) | BC-범위 «기본»+예외(BC 밖·타 BC 소비 표면·슬라이스 0=영향 소비자 경로 포함)·«관련 인수»의 자=입장 행+acceptance 전부·계측=형식 고정+관찰 전용 선언 · 코디네이터: 전체 suite 주어 명기+**무관/관련의 자=기준선 실측**(경로 아님) |
| ① 입력 채널(B상1·중5·6·C중⑥⑦·A중·D상·중·하) | STOP 실행 모드 분리·응답 수신=기록 추기 의무·fallback 술어 «호출 미지원 오류» 확장+진입 증거 의무·codex «게이트 평문 질문» 매달린 앵커 2곳 치환·자유 서술 예외 codex 병기·옵션 한도 초과=전체 목록 선출력 |
| L4 병렬(A중·C중⑤·하⑩⑬·B하7·8·D하) | 입력 준비가 다발보다 앞(Error scope tree/inventory)·적용 범위=둘 이상 부르는 모든 호출·누락=늦은 단독 교정 의무·도구명 중립(Task/Agent)·G1 배너 다발 크기 한 줄·codex 마감문 «(3 포함)»·실측 괄호 쌍둥이 이식 |
| L7 재독(A상2·C하⑫·B부기) | 금지의 주어=중복 적재 — 압축·유실 시 해당 절 재독이 우선 |
| 이월(#4 로) | 요청문 템플릿 «열린 질문은 종료 상태 무해» 한 줄(B상1 프로토콜 측)·RFC profile 어휘·12-slot 표현 빚(4렌즈 수렴) |

### 쌍둥이 행-대응표 (이번 사이클 신설·변경분)

| claude | codex | 성격 |
|---|---|---|
| dddjango.md «입력 채널» (AskUserQuestion) | SKILL.md «입력 채널» (request_user_input 2단) | 도구 치환 등가 |
| dddjango.md Phase1 2·3 병렬 정의(Task/Agent 다발) | SKILL.md 2·3(전부 spawn 후 wait) | 도구 치환 등가 |
| agents/coder.md L2 문단 | dddjango-coder/SKILL.md 동일 문단 | `Bash`↔`네이티브 셸` 외 동일 |
| dddjango.md 게이트 :47(기존) | SKILL.md 게이트 절(구조화 우선·fallback 술어·진입 증거·옵션 한도) | codex 측 확장 = 도구 특성(한도 2~3·exec 거부) 기인 — 의도된 비대칭 |
| (해당 없음 — 하네스가 로드 관리) | SKILL.md :20 재독 금지 | codex 고유 — claude 는 커맨드 로딩이 하네스 소관이라 부재 정당 |
| :92·:147 무관/관련 자·주어 명기 | :115·:170 동일 | 등가 |

- 재검증(수정 후): corpus 11/11·spec/checker/tree/coverage·fixture 90/90·smoke 6/6·
  bc_registry_smoke·byte-copy·backstop **675/675 무변**·STOP 리터럴 6·6·«게이트 평문 질문»
  잔존 0 — 전부 green.
