# dddart 전수 분석 A — 커맨드 & 에이전트 (2026-08-23)

> dddjango-web 4단계 계획의 2단계 산출물. 소스: 마켓 클론 `~/.claude/plugins/marketplaces/changja88-dddart/dddart/` (commands/dddart.md 214행 + agents 7종). 태그: [FLUTTER][BC][MODEL][STATE][TEST] = 차이 5축.
> 상세 원문은 원본 파일이 정본이다 — 이 문서는 절·행 단위 인벤토리 요약이다.

## 커맨드 dddart.md 핵심 인벤토리

- **frontmatter**: description·argument-hint·arguments(feature, api_url)·`disable-model-invocation: true`·allowed-tools(Agent, AskUserQuestion, TodoWrite, Read, Grep, Glob, Edit, Write, Bash, DesignSync)
- **역할 선언(L9)**: 오케스트레이션·게이트·산출물 통합·검증 보고만. 직접 쓰는 것 닫힌 목록 6종(스코프 메모·검증 보고·외부 진실 스냅샷·git 스냅샷·마무리 합치기·build-state.json)
- **산출물 폴더 판형(L18–32)**: `.dddart/<date +%Y%m%d-%H%M>-<en-kebab-slug>/` — 한 기능 한 폴더·재빌드는 재사용·`.dddart/`는 커밋 대상. 고정 파일: scope.md·design-spec.md·openapi-full.json·contract-paths.txt·server-contract.json·design-ref/·design-tokens.json·screen-meta.json·asset-manifest.json·build-state.json
- **config(.dddart/config.json, L34–36)**: openapi_url·design_source(엔진 포인터)·area_prefixes. **Coordinator만 읽고 씀** — 에이전트는 동결 스냅샷 경로만 받음
- **build-state.json(L38–61)**: phase·mode·slices[]{name,files,status,commit}·git_snapshot·pre_run_head·last_commit·g1_decisions[]·analyze_baseline·has_design_screen/tokens/images — 세션 사멸 후 재개 앵커
- **진행 가시성(L63–90)**: TodoWrite 4 task + 트래커 라인 `[✓ 스코프] → [▶ 설계] → [· 구현] → [· 마무리]` + **게이트 배너 4줄 골격**(구분선/`dddart · G{n} 승인`/방금 끝낸 것/승인 대기/다음에 할 것/구분선) — 게이트·마무리에서만 출력. 승인은 AskUserQuestion(권고=선택지·기타 자유입력 유지). 게이트 사이는 한 줄 상태 `dddart · {Phase} · {지금 하는 일}`. 산출물 중계는 경로+3~5줄 요지만
- **모드 삼분류(L92–102)**: 풀(신규 화면 삼총사·신규 애그리거트·신규 BC·라우트 추가) / 수정(기존 구조 안 추가·수정) / 트리비얼(신규 파일 0+비구조 diff). 구조 단위 기준·G0 배너 1급 항목. 모드축 ⊥ 배치축
- **Phase 0(L104–135)**: ①전제조건(git 여부·트리 청결·analysis_options 충돌) ②스코프 메모(+Y 항목 규약: «필요 시 설계가 G1에서 제안» 앵커) ③서버 계약 출처 해소(인자→config→가정 계약 폴백, **G0 승인 후 curl 원본 전체 동결 — 절단은 G1 직후 기계**) ④디자인 출처 해소([FLUTTER] — DesignSync 읽기 전용 4종·포인터 재사용 3분기·**화면 확인 게이트 MF-1~4**(무조건·screen-meta.json만 인용·조용한 유사 화면 집기 금지)·기계 추출 순서 고정(extract_design→extract_dc RMW)·플래그 3종 설정·해소 실패 표면화·**직수입 금지**) ⑤G0 배너(모드+디자인 1줄+BC 배치 3선택+area 질문+**산출물 폴더 ⓐ/ⓑ 선택(`ls -d` 목록·재동결 질문 합류)**)
- **Phase 1(L137–147)**: ①design-architect 호출(입력 9종·`dddart:` 한정 표기) ②리뷰어 4종 전부 병렬(활성 추론 금지·"해당 없음+근거" 의무·편향 방지) ③(선택) discipline-reviewer 경량 ④architect 재호출(반영·중재·Y는 기본 미적용 commit) ⑤G1 배너+결정 3분기(기본 수락/Y 채택→scope.md 갱신+좁은 재호출/Z 결정) ⑥**G1 직후 계약 기계 절단**(contract-paths.txt→extract_contract·exit1 stderr 2분기: path 부재=설계 반송/파싱 실패=G0 재해소)
- **Phase 2(L149–166)**: ①진입 준비(pre_run_head→산출물 커밋→git_snapshot→analyze 베이스라인) ②슬라이스 도출(기계 임계: 풀≤7 축퇴/≥8 세분·수정≤5/≥6, Model/View 2분할, tracer 선행 기계 플래그 2종) ③coder 순차 호출(입력 9종·green마다 커밋·반송 5종 처리) ④discipline-reviewer 리듬(G2 직전 홀리스틱+경계 경량+슬라이스≥3 시 슬라이스별) ⑤백스톱 러너 1회(exit 0/1/2 — 1은 미실행 취급) ⑥빌드+test 전수 확인+codegen 재생성 검증 [TEST][FLUTTER] ⑦미니 게이트(가정 계약 시 tracer 직후 1회·3분기) ⑧G2 배너(행위 체크리스트·디자인 시각 대조·실행 안내·합치기 고지)
- **Phase 3(L168–177)**: 검증 보고(실행한 것만) → **soft-reset 합치기**(가드 4종 AND·`--soft`만·실패 시 D+ 폴백 한 줄)
- **수정 모드(L179–190)**: G0 영향 파일 조사→스코프 기록, 리뷰어 touched-layer 기계 매핑 축소(ddd 항상), G1' 생략 조건(설계 변경 없음 AND 승인 명세 존재), 감사 touched 경량 1회, 빌드 조건부, 백스톱·마무리 동일
- **트리비얼(L192–194)**: 판정 배너 1회→Coordinator 직접 편집→touched 백스톱+analyze→보고. 승격 규칙(시그니처·State·라우트 건드리면 수정 모드로)
- **엣지(L196–205)**: 게이트 거부=해당 단계 재실행 / 리뷰어 충돌=architect 중재 / 반복 실패 3회 한도 / 행위 구현 불가=설계 반송 / 동결본에 엔드포인트 없음=재동결 vs 가정 승격 질문 / 설계 반송 재진입=diff 요구→슬라이스 재도출→영향만 재개봉+계약 재절단 / 세션 재개=build-state 복원
- **경계(L207–214)**: 직접 작성 금지·명세=단일 근거·한 주제 한 소유자·디자인 엔진 읽기 전용·승인 없이 게이트 미통과

## 에이전트 7종 frontmatter

| 에이전트 | tools | skills |
|---|---|---|
| coder | Read, Grep, Glob, Edit, Write, Bash | implementation-dart/flutter/riverpod/test + discipline-cleancode/houserules/test (7) |
| design-architect | Read, Grep, Glob, Edit, Write | architecture-ddd/ui/state/data + discipline-houserules (5) |
| design-review-ddd/ui/state/data | Read, Grep, Glob | 각 lens 스킬 1개 |
| discipline-reviewer | Read, Grep, Glob | discipline-cleancode/houserules/test (3) |

## design-architect 핵심

- 단일 통합 작성자. 입력: 스코프·openapi 동결본·design-ref·design-tokens·asset-manifest·저장 경로·BC 배치 고정·G1 override·구현 반송 피드백 + **사전 조사 3종 의무**(디렉터리 구조·design_system 재사용 후보·기존 BC 트리)
- 명세에 담는 것: 도메인[BC][MODEL]/화면[FLUTTER](3단 판별+왜·토큰 박기 3회계·이미지 정형 목록·**형상 산문 금지**)/상태[STATE]/데이터(계약 정확 인용·Either)/행위 목록(경계값 3분할)[TEST]/판정 소유 라벨[MODEL]/계약 위험 표기/파일 목록·구조 결정(골격 완비 생략 금지)
- 리뷰 반영=해당 절 제자리 수정(메타 요약 블록 금지)·충돌 중재·Y 기본 미적용
- **자기모순 1회 스캔**(3회계 수량 대조) + **백스톱 정합 1회 스캔**(deny 직접 대조 — "대조 없는 일치 선언 무효")
- 경계: 코드 안 씀·명세 밖 기능 금지·한 주제 한 lens·config 접근 금지

## 리뷰어 4종 공통 판형

정체(lens 하나로만 독립 비평·읽기 전용) / 입력(명세 초안만·타 노트 금지) / 산출(blocker→important→nit 번호·발견[근거+심각도]+권고) / **무결 시 "이상 없음+근거 한 줄" 의무** / undecidable 대조(같은 파일 적재→절차 어긋남 표면화) / 누락 자체가 발견 / 경계 4(읽기 전용·타 lens 이관·스코프 확대 금지·config 금지)

- **ui 점검 7항**: 화면 분해 적정성(과/미분해)·design_system 재사용 누락(Grep 대조)·내비 흐름·view 수동성·design-ref 대조·**충실도 4항(has_design_screen 발동: 색 토큰/spacing·임의값/아이콘/부재 요소·inline-style)**·행위 맞물림
- data 점검: 가정 계약 명시성(출처 없는 서술=발견)·실계약 대조(동결본에 없는 인용=blocker)·계약 위험 표기 양방향·Either·DataSource 분해·hive

## coder 핵심

- 명세의 집행자(구조·계약·메커니즘 새로 결정 금지). **형상만 예외 — design-ref 시안이 근거**(직수입 금지·`.screen` 내부만)
- 입력 9종(명세·슬라이스·계약 경량본·design-ref·asset-manifest·기존 트리 요약·골격 플래그(무기억)·analyze 베이스라인·감사 발견 목록)
- 산출: 코드+행위 검증 테스트(FORM 규율)+screenProbes [TEST — 전부 테스트 의존]
- 방식: bottom-up·층별 green 래칫·codegen 규약·스킬 부분 적재
- **반송 5종**: 구조 결정 부재/하우스룰 괴리/계층 밖 수정 필요/기존 복제 발견/3회 한도
- 경계: 명세 변경 금지·메커니즘 대체 금지(출처 불문)·버전 훈련 기억 금지·미실행 보고 금지·config 금지

## discipline-reviewer 핵심

- 백스톱과 분업: 기계 판별(러너 60종) vs **의미 변종 전담**("이름은 맞되 실체가 틀린 것·자리는 맞되 책임이 틀린 것")
- 입력 3종 필수(코드·명세·**슬라이스 계획+완료 범위** — "아직 안 만든 것"과 "누락" 구별)
- Phase 1 경량 모드(명세만·과분해/과추상만)
- 점검 8종: ①행위↔코드 대조 ②판정 소유 대조(빈혈 blocker)[MODEL] ③에러 2채널[STATE] ④view 수동성·분해 실현 ⑤클린코드(이름-위장 전담) ⑥구조·명명 의미 변종 8하위(골격 위장·책임 월경·두 철자·area·main 최소형·DI seam·시각 토큰 오버라이드·어휘 보존·에러 역할계약) ⑦판별 검증(2차·종심) ⑧테스트 FORM 감사[TEST]
- 경계: 기술 구현 정확성은 비관할(규율만)·시각 측면=G2 사용자 눈

## 판형 요약 (이식 관점)

- 게이트 3(G0/G1/G2)+마무리·배너 4줄·트래커·AskUserQuestion 승인·한 줄 상태·미니 게이트(조건부)
- 산출물 폴더(날짜-슬러그·한 기능 한 폴더·ls 목록 선택·재동결 질문)·build-state 재개
- 재호출 루프 7종(리뷰 반영/G1 override/감사 반영/백스톱 반송/coder 반송/설계 반송 재진입/게이트 거부)
- 기계 플래그: 모드 삼분류·디자인 3플래그·슬라이스 임계·tracer 2종·touched-layer 매핑·백스톱 exit 3분기·합치기 가드 4종
