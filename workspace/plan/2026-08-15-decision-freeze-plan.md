# 계획 v0 — coder 사고 유발량 축소 (비병렬 속도 개선 · «결정 동결» 트랙)

2026-08-15 심야. 전제: 성능>속도(정보 손실 0·판정 무변) · 클린룸 유지 · 실행 개시=사용자 지시.
근거 실측·조사는 optimization-log.md 같은 날짜 절 + 조사 보고 3건(본 문서 §1에 요지 인용).

## 0. 문제 정의 (실측 요약)

- 레인 A(claude) coder 실동작 ≈3h09m 중 **생성 83%**(승인 11%·도구 5%). 생성은 71 tok/s
  디코드 한계 = 토큰량 병목이고, 출력 672,854 tok 중 **~83%가 thinking**.
- 레인 B(codex) child coder: 턴당 출력 ~73 tok에 32~37s = **턴 수×턴당 지연 병목**
  (reasoning 비중 39~45%·실제 도구 실행 소형).
- 사고 중 회피 가능분 3종: ⓐ 결정 재추론(spec 미확정을 coder 5~7명이 각자 해석 —
  S3 STOP 전 축이 spec 문면 해석) ⓑ 턴당 고정비(상황 재파악) ⓒ 재작업(레인 A coder 의
  ~16%·codex 몸통). ⓒ는 B0-1·preflight ⑻⑼⑽·spec patch 가 기수정 — 무수정 관측.
- 목표 문장: **«사고를 줄여라»가 아니라 «사고할 필요를 줄여라»** — 필요 사고(TDD 판단·
  설계 준수 검증)는 불가침.

## 1. 레버와 공식 근거 (조사 3건 요지)

| 레버 | 원리 | 공식 근거 |
|---|---|---|
| ① 확정표(결정 동결) | thinking 은 질의 복잡도에 자동 비례 — 미결정을 소거한 입력은 사고를 덜 유발. «결정을 다시 따지지 말라»는 Anthropic 공식 thinking 절감 샘플 프롬프트 | platform.claude.com «Prompting best practices» §Overthinking·«Steering thinking» §How Claude decides |
| ② 턴 다이어트 | codex 병목=턴 수×32s. claude 도 턴당 고정비 존재(402 API 메시지) | 실측 (본 문서 §0) |
| ③ effort 차등 | 문구보다 effort 가 «calibrated control»(공식). claude=agent frontmatter `effort`(low~max)·codex=`[agents] default_subagent_reasoning_effort`·spawn 명시값·`codex exec -c` | code.claude.com/docs/en/sub-agents · developers.openai.com/codex/config-* |
| (금지선) | 프롬프트 문면으로 effort 를 낮추는 공식 수단은 양쪽 다 없음 — 문구 조향은 wording-sensitive·품질 저하 경고 | 조사 ①·② 공통 |

**경계 조건(공식)**: 크고 복잡한 프롬프트는 thinking 을 오히려 늘린다. → 확정표는 «분량
추가»가 아니라 **«미결정의 소거»**로 설계 — 확정표가 덮는 산문은 같은 개정에서 걷는다
(정보 손실 0 은 검증 세트로 고정). 또한 처방적 step-by-step 사고 절차는 넣지 않는다
(공식 권고: 결정 «데이터»는 주되 사고 «절차»는 처방하지 않음).

## 2. 수정 대상과 개정 내용 (C0 — 플러그인 문면 개정 · 2.10.0 후보)

| # | 파일 | 개정 |
|---|---|---|
| 1 | agents/design-architect.md | 설계 명세 필수 산출에 **확정표 3종**(§3) 추가 + «확정표가 덮는 결정은 산문 반복 금지» |
| 2 | agents/design-review-{ddd,api,db}.md · discipline-reviewer.md(Phase 1) | 리뷰 노트에 **집행성 판정 1줄** 의무: «coder 가 추론 없이 칠 수 있나 — 막히면 어느 행인가» |
| 3 | agents/coder.md | ⓐ «확정표 밖 결정=현장 해석 금지·즉시 반환» ⓑ 결정 재방문 금지 문구(공식 문면 차용: choose and commit·새 정보 없으면 재방문 금지) ⓒ 턴 다이어트: 독립 확인·독립 편집은 한 턴에 묶기 |
| 4 | commands/dddjango.md | 02 게이트에 확정표 완전성 검사(열린 물음 0·배치표 전건 경로) + impl-notes 규율 명문화(**coder 직접 소비 금지 — architect 경유 개정만**) + 05 발주문에 «checker 리터럴 경로 호출» 1줄(B0-2 잔여 커버 ~75%) |
| 5 | codex-dddjango 미러 | SKILL.md·agents 동등 문면 byte/의미 동기 |

## 3. 확정표 3종 양식 (검증된 틀 차용)

- **㉮ 파일 배치표**: 행 = 새 파일 1개 — «경로(표준 트리 좌표) · 이름 · 슬라이스 · 근거 규칙#».
  완전성 규칙 = DMN Unique 차용: **한 파일=한 행, 겹침·공백=명세 결함**(리뷰 반려 사유).
- **㉯ 계약 확정표**: 행 = 공개 표면 1개 — «시그니처/스키마 모양 · 에러 코드 · 소비자».
  contract-first 관례: 이 표가 single source — 코드와 어긋나면 코드가 아니라 표를 먼저 본다.
- **㉰ 열린 물음 대장**: Rust RFC unresolved questions 3분류 축자 차용 —
  «설계 중 해소 / 구현 중 해소(impl-notes 경유 예정) / 스코프 밖». **02 승인 조건 =
  «설계 중 해소» 칸 0건.** 결정 문형은 Nygard 능동태 단문(«We will …») + MADR
  «Chosen: X, because Y».
- **freeze 규율**: 확정표는 02 승인 시점에 동결. 이후 변경은 coder 재량이 아니라
  impl-notes→architect 개정 경유만(GNOME freeze 예외 절차 동형).

## 4. ③ effort 차등 실험 (C2 — 옵션 · 사용자 결정 사안)

- claude: 기계 슬라이스(admin·스캐폴딩류) 한정 coder 변형 agent 에 `effort` 하향.
  codex: 기대 폭 소형(reasoning 39~45%)이라 보류. spawn 오버라이드 리그레션(공식 이슈
  #20077/#32031) 실측 선행 필요.
- **게이트**: 성능>속도 — ⑤ 3축·⑥a 판정 무변일 때만 채택. 기본은 «하지 않음».

## 5. 검증 계획

- 문서 개정 자체: 기존 검증 세트(13종) green 유지 + 정보 손실 0(걷은 산문은 확정표가
  전부 덮는지 대조 — 개정 diff 리뷰).
- 효과 실측(다음 실전 라운드 — 무비용 A/B·baseline=r2″ 실측):
  ① coder thinking 토큰(672,854·83% 대비) ② 모델 턴 수(claude 402·codex 662/395 대비)
  ③ coder 실동작(3h09m 대비) ④ 현장 해석·반환·STOP 건수 ⑤ 품질 무변(⑤ 3축·⑥a).
- 실패 판정: 품질 지표가 흔들리면 즉시 롤백(문면 개정은 docs-only 라 롤백 무비용).

## 6. 리스크와 반박

- «architect 부담 증가로 02 가 늘어난다» → 확정표는 이미 내린 결정의 기록. 02 실측
  1h17m 의 절반이 개정 왕복이었음 — 집행성 판정이 왕복을 앞당겨 오히려 줄일 가능성.
  02 시간도 계측 항목에 포함해 검증.
- «확정표가 틀리면 전 coder 가 같은 오류» → 리뷰 3관점+집행성 판정이 표를 직접 심사
  (산문보다 심사 가능성 높음 — 표는 겹침·공백이 기계적으로 드러남).
- «freeze 경직성» → 열린 물음 대장 «구현 중 해소» 칸 + impl-notes 경유 개정이 유연성
  채널(이미 r2″에서 작동 실증·재조정 3회).
- «분량 증가가 thinking 을 늘림(공식 경계)» → 산문 동시 걷어내기로 순증 0 설계.

## 7. 단계와 결정 지점

- C0 문면 개정(위 §2) → 검증 → 2.10.0 후보. ※ 2.9.0(B0)과 분리 유지.
- C1 다음 실전 라운드에서 §5 실측 — 추가 비용 0.
- C2 effort 실험 — 사용자 결정 사안(기본 보류).
- 착수 전 결정 필요: ⓐ 계획 리뷰 강도(경량 몇 렌즈 vs 생략) ⓑ C0 착수 시점
  (2.9.0 릴리즈와의 순서).
