# dddart 전수 분석 C — 스크립트·부속물 (2026-08-23)

> dddjango-web 2단계 산출물. 소스: 마켓 클론 dddart (전 50 파일 중 스크립트·매니페스트·부속). 태그 = 차이 5축.

## 백스톱 러너 판형 [FLUTTER 구현·판형은 중립]

- **backstop.dart(122행) 단일 엔트리**: `dart run backstop.dart <대상 루트> [--diff-base <commit>] [--all] [--only ...] [--update-baseline]`. 검사 60종 상수(ST12+IM23+NM17+CY1+TG1+PJ2+MD2+RV1+HV1). **종료코드 0=clean/1=사용·내부 오류/2=blocker(fail-fast 금지 — 일괄 출력)**. checkId→path→line 삼중 정렬. 비git 퇴화 notice. "스크립트는 파이프라인 상태를 모른다 — 컨텍스트는 전부 인자".
- **common.dart(570행)**: Finding 모델(심각도 BLOCKER 단일·위반/교정 2줄 출력) · 마스킹 스캐너(주석·문자열 상태머신) · import 파서 · 경로 클램핑 · **트리 데이터 코드 사본**(문서 §1의 3중 사본 — 값의 단일 출처는 문서로 선언) · git 게이트 4단(diff/status/ls-tree/added 줄 span) · added/touched/addedDir 술어 · 파일별 메모이즈.
- **게이트 의미론**: 구조·명명=added 파일/디렉터리 · import=touched의 added 줄 · 골격 완비=신규 단위 · 순환=전역+베이스라인 래칫(`.dddart/backstop-baseline.json` 커밋 대상) → **레거시 불발화**.

## 검사기 9패밀리

| ID | 축 | 태그 |
|---|---|---|
| ST 12종 | 구조·경로(직속 화이트리스트·계층 고정·구명칭 deny·골격 완비 ST4·design_system 7파일·오타 힌트) | [BC] |
| IM 23종 | import 방향(계층 매트릭스·교차 4채널·design_system 화이트리스트·main 화이트리스트 + 토큰 검사 병행) | [BC] 일부 [FLUTTER][STATE] |
| NM 17종 | 명명(접미사↔종류·삼총사 1:1:1·section 접두·시각 리터럴 금지·라우트 단일 출처·view-fat NM17) | 일부 [FLUTTER][STATE] |
| CY1 | BC 순환(Tarjan SCC+베이스라인 래칫) | [BC] |
| TG1 | 신규 BC 테스트 존재 | [TEST] |
| PJ2 | pubspec 토대(riverpod ≥3+codegen 3종) — **«토대 불변식 검사» 판형** | [FLUTTER][STATE] |
| MD2 | freezed 부착·수기 직렬화 금지 | [MODEL] |
| RV1 | 전역 재시도 OFF | [STATE] |
| HV1 | @HiveType 부착 | [MODEL] |

## 파이프라인 도구 5종 (게이트 아님·결정론 절단)

- **extract_design.dart(769행)**: 디자인 출처→토큰 절단 3모드(HTML tailwind-config / --from-theme / --from-ds-manifest[클로드 디자인]) → `design-tokens.json`{colors,spacing,borderRadius,typography,icons,arbitraryValues,unmappedIcons}. exit 1=파싱 실패·토큰 0.
- **extract_dc.dart(561행, claude 전용·codex 미러 없음)**: 클로드 디자인 PROJECT `.dc.html`의 **`.screen` 서브트리만** 절단(device-chrome 제외) → tokens RMW(아이콘·이미지 주입)+asset-manifest+screen-meta.json{title,subtitle,cards[]}(확인 게이트 MF-1 인용원).
- **extract_layout.dart(364행)**: 화면 구조 IR 절단 — **어디에서도 호출되지 않음**(소비처가 플러그인 밖 eval 도구).
- **fetch_images.dart(310행)**: 시안 `<img>` 전수 다운로드→`assets/images/`+토큰 부여, status ok/inline/failed/skipped fail-loud.
- **extract_contract.dart(193행)**: 명세 인용 paths를 OpenAPI 동결본에서 정확 일치 선별+`$ref` 전이 폐쇄→경량본. exit 1=인용 path 부재(+근사 후보 병기="그 자체가 발견")·파싱 실패·Swagger 2.0. "게이트 도구가 아니다".
- icon_map.json: Material Symbols→Flutter Icons 고정표 [FLUTTER].

## 픽스처 러너

run_fixtures.sh(899행): 백스톱·추출도구 **자기 회귀 픽스처**(F1~F27d·assert 43건·거의 전 케이스 positive-control 짝) — mkproj(임시 git 프로젝트)+run_backstop+assert 판형 [TEST 성격이지만 «검사기의 자기 검증» — 플러그인 대상 코드 테스트와 무관].

## 매니페스트·부속

- plugin.json 필드: name/displayName/version/description/author/license/homepage/repository/keywords. hooks·mcpServers·경로 오버라이드 미사용(규약 디렉터리 자동 탐지).
- hooks/·assets/·.mcp.json 부재 — 플러그인은 `.claude-plugin/·agents/·commands/·scripts/·skills/` 5디렉터리뿐.
- 런타임 생성물(대상 프로젝트): `.dddart/backstop-baseline.json`·`.dddart/config.json`(area_prefixes)·`assets/images/**`(외부 진실 동결의 명시적 예외).
- 마켓 레벨: `../.claude-plugin/marketplace.json` plugins[]에 등재 · Makefile 릴리스 게이트([1/7] validate --strict·[2/7] 미러 diff -q byte 동일 강제) · codex 미러엔 extract_dc 미포함(claude 전용).

## 실행 배선 패턴

- 스크립트 호출은 **전부 Coordinator가 Bash로** `dart run ${CLAUDE_PLUGIN_ROOT}/scripts/...` — "에이전트가 경로를 추측하지 않는다". 추출 순서 고정(MF-3)·확인 게이트는 산출 JSON만 인용(MF-1 — LLM 손추출 금지).
- undecidable.md 적재는 `${CLAUDE_PLUGIN_ROOT}/skills/.../references/undecidable.md` 경로 참조 6곳(architect·coder·discipline·리뷰어 4).

## 특이사항

1. extract_layout 미소비 2. HTML 토크나이저 3파일 의도적 국소 복제(미러 diff 동결 때문) 3. 트리 화이트리스트 코드 3중 사본(값 정본은 문서) 4. 검사 ID 네임스페이스 충돌 회피 관례 5. 백스톱 외부 의존 0 6. 보류 명시(HV2·HV3 등)
