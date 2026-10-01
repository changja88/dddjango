# W8 작은 판 설계 — 보고판 + 막지 않는 정확값 시트

2026-10-01 · 가지 `design/w8-v5` · 기준 `impl-brief.md`, `review-claude.md` §3.

## 결론

v4 수집기와 대조기를 제품에 옮기고, 기존 원본/구현 캡처에 함께 실행한다. 대조 결과는 기존 독립 시각 감사의 수리 목록이다. 새 G0/G1/G2 기계 관문을 만들지 않는다. 발견의 `blocking`은 v4의 **차단 후보** 분류를 그대로 보존한 이름이며 이번 판의 종료 코드나 G2 통과 판정이 아니다. 실제 시안 불일치 T는 기존 품질 의무에 따라 G2 전에 고친다.

같은 원본 census로 정확값 시트를 만든다. 도구는 관측값과 정확히 같은 foundation 토큰 후보를 보여 주고 architect가 기존 시각 연결표에서 해석한다. 명세와 역할 입력에는 시트 경로만 추가한다. 입력 결속, G1 검사, 재렌더, exit 3, 영향 case 계산, freshness 검사, 재관찰 축소, 발주자 대조 축소, 그림자 관문은 이번 구현에 없다. 기존 검사와 발주자 G2는 유지한다.

## 데이터와 도구 계약

### 수집

`assets/style_census.js`는 scratch의 `style_census_dv4.js`를 기반으로 한다. `page.evaluate(source, options)` 인터페이스와 `{meta, records}` v4 판형, 기존 관측 의미를 유지한다. 인자는 `root`, `placeholders`, `exclude`, `routeSet`, `sdkGlobals`, `page`, `pageSize`, `budgetMs`. 호출부는 한 case의 원본/구현을 같은 viewport·루트 크기·상태로 수집하고 전체 높이 캡처도 남긴다. 명시한 루트가 0개/복수면 미실행이다. body 전체 관측의 기존 명시 상태는 보존한다.

빌드 폴더 `observations/style-census-design.json`과 `style-census-impl.json`에 `{case_id: census}`로 저장한다. 페이지를 나눴으면 전체 records를 순서대로 합친 뒤 비교한다. `partial`, 잘린 페이지, fonts 미정착, 실행 중 유한 animation, 루트·schema·SDK 상태 문제는 비교 성공으로 세지 않는다. 이미지 단독 등 DOM이 없으면 기존 `visual-check.md`에 W8 미대조 사유를 쓴다. 기존 빌드에 원본 census가 없으면 소급 관문을 만들지 않고 그 사실을 보고한다.

### 대조 CLI

```bash
python scripts/compare_style_census.py \
  --design BUILD/observations/style-census-design.json \
  --impl BUILD/observations/style-census-impl.json \
  --mapping BUILD/observations/style-cases.json \
  --sdk-scope BUILD/observations/style-sdk.json \
  --out BUILD/observations/style-report.json
```

- mapping은 `{원본_case: 구현_case}`. 원본/구현 case 이름이 같아도 명시한다. 빈 mapping·중복 구현 case·입력 case 누락은 성공 0건으로 숨기지 않는다.
- SDK scope는 구현 case별 `{files: [벤더 URL 경로], globals: [전역 이름]}`이고 SDK가 없으면 `{}`다. 정상 경로에서는 항상 전달해 교차 확인한다. 원본의 스키마는 바꾸지 않는다.
- 비교용 예시 데이터를 맞출 수 없는 case만 G0의 기존 스코프 기록에 사유를 남기고 `--declared-data-case CASE`로 지정한다. 선언은 형태 차이를 면제하지 않는다. CLI에 `ALL` 일괄 선언/legacy 우회 옵션을 새로 제공하지 않는다. 과거 보관 자료의 API 재생에서만 v4의 기존 전역 설정을 사용한다.
- 출력 `cases`·`groups`와 묶음/구성원 지문은 유지한다. CLI 요약에 전체 묶음·차단 후보·후보 구성원·미대조 case 수를 낸다. **정상 보고 exit 0(후보가 있어도 0), 사용법/입력 오류 또는 미실행 포함 exit 1**. exit 1도 W8 자동 차단이 아니라 기존 기록에 미실행 범위를 남긴다. exit 2/3은 없다.
- 정렬은 묶음 전체 키의 동점을 풀고 표본을 고르기 전에 구성원을 정렬한다. case·진단 목록도 결정적으로 출력한다. 매칭에서 집합/메모리 주소의 순서가 결과를 좌우하는 곳은 안정된 원본 순서로 고정하되, P1/P2 보관 묶음·구성원 결과가 달라지면 원인을 먼저 해결한다.

### 정확값 시트

```bash
python scripts/style_value_sheet.py \
  --census BUILD/observations/style-census-design.json \
  --tokens PROJECT/web/design_system/foundation/tokens.css \
  --out BUILD/observations/style-values.md
```

같은 record 종류·요소 클래스 서명·가상 요소·관측 style 값을 하나의 모양 묶음으로 삼는다. 동일 클래스라도 값이 다르면 별도 묶음으로 남긴다. 각 묶음에 case·대표 record·부모/조상·자식 효과 record 참조와 실제 관측값을 남긴다. 배경, 테두리 네 면, 반경, 그림자 전 층, 필터/흐림, 타이포, 아이콘, padding/gap, 치수/위치 제약을 census가 가진 범위에서 보여 준다. 묶음 대표만 남기면서 다른 case의 값을 덮지 않는다.

토큰은 지정한 프로젝트 파일의 custom property 선언만 읽는다. CSS 리터럴의 표현 차이(숫자 표기·공백·동일 색 표기, 단순 var 별칭)를 안전하게 정규화하되 허용 오차나 근접값 검색은 쓰지 않는다. 복합값 전체와 개별 면/모서리/틈 값의 일치는 구별한다. 그림자 전 층은 순서를 유지한다. 해결할 수 없는 var·계산식·문맥 의존 단위·동일 이름의 다른 선언은 정확 일치로 추측하지 않는다. 일치 후보가 없으면 `신규 등록 필요`로 표시하고 지원 밖 표현은 수동 확인 사유를 함께 남긴다. 토큰 자동 작성이나 채택 결정은 하지 않는다. 파일이 없으면 토큰 없음 사실과 신규 등록 필요를 표시한다.

원본 census의 URL/본문 전체를 시트에 복제하지 않는다. 생성 시각·실행 시간·절대 입력 경로 같은 가변값을 넣지 않아 같은 입력이면 byte 동일하다. 시트는 참고 자료이며 누락/생성 실패가 새 G1 검사로 연결되지 않는다.

## 흐름 연결과 소유권

G0의 기존 `render_audit.js` 캡처 자리에서 원본 census와 시트를 함께 남긴다. Coordinator는 실행·경로 전달만 맡고 요소/토큰 해석은 architect가 맡는다. 원본 소스와 기존 시각 연결표를 시트로 대체하지 않는다. G0/G1의 현재 입력·토큰 검사는 그대로다.

3-1 하네스는 빌드 폴더 `observations/` 또는 그 하네스 전용 모듈에서 시안 예시 글·시각을 맞춘다. 앱의 업무 데이터·기존 시험 fixture/factory/seed를 바꾸지 않는다. 긴 글 등 회귀 데이터는 그대로 별도 회귀 case로 확인하고 W8 비교 mapping에 넣지 않는다. 원본 census가 존재하는 새 레인에서 구현 census를 함께 수집하고 3-2에서 대조한다.

기존 독립 시각 감사가 `visual-check.md`에 후보 묶음 id와 T/D/F/H 처분을 남긴다. T=실제 스타일 불일치, D=데이터가 만든 정상 차이, F=도구 오탐, H=사람 확인. D는 실제 다른 데이터·분기/스타일의 인과 근거를 쓰며 시안 예시 값으로 업무 동작을 고치지 않는다. F/H는 한 줄 이유를 쓰고 H의 확인 결과를 함께 남긴다. 한 묶음에 판정이 섞이면 구성원 범위를 표시한다. 모든 후보가 T는 아니다. 비후보·미대조·도구가 못 보는 축도 기존 독립 시각 감사 범위에서 빠지지 않는다.

공용 클래스 서명이 여러 case에 걸친 T는 같은 원인의 **부품 단위 수리 1건**으로 연결한다. 원본 variant가 공용 부품에 없으면 공용 variant를 추가하고 기존 호출의 기본 동작을 보존한다. 기본값 변경은 사용자 결정과 영향 화면 목록을 따른다. 문서에 새 영향 case 계산기를 넣지 않는다.

G2에 `W8 보고: 후보 N · T 수리 a · D b · F c · H d · 미대조 case k`를 1급 행으로 표시한다. N과 D/F/H는 묶음 수, a는 고친 부품/원인 수다. 따라서 합산 등식으로 취급하지 않는다. 혼합 묶음은 라벨별로 겹쳐 셀 수 있음을 기존 기록에 밝힌다. 미실행은 k에 포함하되 원인도 보여 준다. W8가 없으면 미수행+사유를 쓴다.

측정은 새 의무 문서 없이 기존 `visual-check.md`의 회차 기록과 G2 배너에 넣는다: 첫 보고 T/D/F/H 묶음 수와 처분 분, 시트 사용 여부·첫 제출 T, G2 시각 반송 회차/분, G0 시작~G2 끝 시각/벽시계, 발주자 판정 후 대조한 놓침 수. 아직 판정하지 않은 값은 `미측정`으로 남겨 0과 구별한다. 발주자 선판정→보고 열람은 운영 절차이며 플러그인이 발주자의 대조 범위나 도구 사용을 줄이지 않는다.

## 바꾸는 파일과 미러

| Claude 정본 | Codex 미러 | 변경·소유 |
|---|---|---|
| `dddjango-web/assets/style_census.js` | `codex-dddjango-web/skills/dddjango-web/assets/style_census.js` | 신규 · v4 수집 · byte 동일 |
| `dddjango-web/scripts/compare_style_census.py` | `codex-dddjango-web/skills/dddjango-web/scripts/compare_style_census.py` | 신규 · v4 대조+CLI · byte 동일 |
| `dddjango-web/scripts/style_value_sheet.py` | `codex-dddjango-web/skills/dddjango-web/scripts/style_value_sheet.py` | 신규 · 정확값 시트 · byte 동일 |
| `dddjango-web/scripts/test/fixtures_style_census.sh` | `codex-dddjango-web/skills/dddjango-web/scripts/test/fixtures_style_census.sh` | 신규 · 기존 글롭 러너 참여 · byte 동일 |
| `dddjango-web/scripts/test/test_style_census.py` | `codex-dddjango-web/skills/dddjango-web/scripts/test/test_style_census.py` | 신규 · 합성/CLI/결정성/시트 · byte 동일 |
| `dddjango-web/scripts/test/style_census_browser.py` | `codex-dddjango-web/skills/dddjango-web/scripts/test/style_census_browser.py` | 신규 · v4 브라우저 합성 재사용 · byte 동일 |
| `dddjango-web/skills/implementation-ui/references/design-evidence.md` | `codex-dddjango-web/skills/implementation-ui/references/design-evidence.md` | W8 상세 계약·실행 예시·감사/측정 · byte 동일 |
| `dddjango-web/commands/dddjango-web.md` | `codex-dddjango-web/skills/dddjango-web/SKILL.md` | G0 짧은 연결·경로 전달·3-2 한 문단·배너 한 행 · 의미 미러 |
| `dddjango-web/agents/design-architect-web.md` | `codex-dddjango-web/skills/dddjango-web-design-architect-web/SKILL.md` | 입력 경로·기존 표에서 해석 · 의미 미러 |
| `dddjango-web/agents/coder-web.md` | `codex-dddjango-web/skills/dddjango-web-coder-web/SKILL.md` | 입력 경로와 감사 수리 참조 · 의미 미러 |
| `dddjango-web/agents/discipline-reviewer-web.md` | `codex-dddjango-web/skills/dddjango-web-discipline-reviewer-web/SKILL.md` | 기존 Phase 2 독립 시각 감사의 처분 참조 · 의미 미러 |

`Makefile`은 기존 `fixtures_*.sh` 자동 실행 및 assets/scripts/reference byte 비교를 그대로 이용하므로 수정하지 않는다. 매니페스트·버전·릴리즈·봉인은 변경하지 않는다. 설계·최종 구현 보고는 요청한 `workspace/plan/2026-10-01-w8-v5/`에만 쓴다. 사용자 brief/review/이전 설계는 보존한다.

## 커밋 단위와 검증

1. **v4 도구 제품화**: 이 설계 + 수집기/대조기 + 합성·CLI·결정성 fixture. 기존 v4 정렬 오류가 fixture에서 재현되는지 먼저 확인하고 최소 수리한다. 보관 원본/구현의 6회차를 메모리/API 및 CLI로 재생해 저장 JSON과 비교한다. 각 묶음 id·값·구성원·차단 후보 동일, 표본 선정·배열 순서만 달라질 수 있다. P1 첫 제출 독립 라벨 T 35개의 id가 모두 차단 후보로 남아야 한다. `make verify-web` green 뒤 커밋.
2. **정확값 시트**: 먼저 exact/near 값 구분, 별칭·복합 shadow·4면·pseudo/자식 효과·다른 variant 분리·missing tokens·결정성 fixture를 추가해 실패를 확인한다. 최소 시트 생성기를 구현하고 byte 미러한다. `make verify-web` green 뒤 커밋.
3. **파이프라인 연결**: 위 기존 문서만 짧게 연결하고 상세 계약은 design-evidence에 둔다. Claude/Codex 동작 의미와 경로를 직접 대조한다. `make verify-web`, `claude plugin validate dddjango-web --strict`, 마지막 `make verify` 결과를 남긴 뒤 커밋한다. 봉인 drift만 red이면 지시대로 기록하며 `manifest_seal.py --write`는 실행하지 않는다.
4. **마지막 보고**: 커밋 목록·파일·명령/exit·재생/결정성·발견 처분·설계 차이·남은 일을 `impl-w8-small.md`에 적고 마지막 줄 `REPORT-DONE`을 확인한다.

검증은 네트워크·서버·DB 없이 표준 라이브러리와 보관 JSON으로 수행한다. 실제 브라우저 합성은 설치된 로컬 Playwright/Chromium이 있는 경우 그 실행 경로를 명시하고 모든 요청을 route fulfill/abort하여 외부 통신 없이 수행한다. 브라우저 dependency는 설치하지 않는다. 필수 순수 Python fixture는 선택적으로 건너뛰지 않는다. 브라우저 실행이 불가능하면 그 제한을 구별해 보고한다. `.venv`는 지시된 main `.venv`의 심링크만 만들고 커밋하지 않는다. Python bytecode는 끄고 임시 쓰기는 워크트리 또는 허용 TMPDIR에 한정한다.

## 검토 발견 처분

| 발견 | 처분 | 이번 반영 또는 2단계 이유 |
|---|---|---|
| B1 | 반영 | 작은 판의 레인 안 보고로 즉시 수리. 속도 절감은 단정하지 않고 측정한다. 발주자 축소는 결과를 보고 사용자 결정. |
| M1 | 반영 | W8는 비차단 보고, 시트도 참고. 입력 결속/G1 신규 관문을 넣지 않는다. |
| M2 | 반영/2단계 | 놓침과 F 비율의 재료를 남긴다. 분모 관문·승격 자동화는 없다. |
| M3 | 반영 | 기존 시각 연결표 재사용, 기계 관측값과 정확 일치 토큰만 추가. |
| M4 | 반영 | Coordinator에는 짧은 접속 문면, 상세는 reference 하나. 새 명세 블록 없음. |
| M5 | 반영 | 실행은 Coordinator, 해석은 architect. Coordinator 출처 재연결 없음. |
| M6 | 반영 | 공유 variant와 부품 단위 수리. 기본값 변경은 기존 사용자 결정 경로. |
| M7 | 반영/2단계 | v4 유지. 재렌더·exit 3·영향/freshness·결속은 측정 뒤 별도 결정. |
| m1 | 반영 | 큰 판 비용 추정을 이번 확정 비용처럼 쓰지 않는다. 실시간을 기록. |
| m2 | 반영 | 도구 후보가 있어도 정상 보고 exit 0, 시트의 새 기계 관문 없음을 명시. |
| m3 | 반영 | impl-brief의 명시적 작은 판 승인을 사용. 그림자 비용 승인으로 확장하지 않음. |
| m4 | 반영 | A/B 원인 집계는 참고, 명세에 레이아웃 결속을 옮기지 않음. |
| m5 | 반영 | 동점·구성원·표본·묶음 정렬을 고치고 여러 hash seed 출력 byte 비교. |
| n1 | 반영 | 실제 작업 가지와 커밋을 최종 보고에 기록. main 상태 명령 없음. |
| n2 | 반영 | 파일 표의 Claude/Codex 전체 경로 명시. |

반박하는 발견은 없다. Serena·Graphify는 이번 명시 지시대로 사용하지 않는다. 독립 Claude 리뷰는 사용자가 선택한 후속 검토이며 이번 구현자가 별도 에이전트를 파견하지 않는다.

REPORT-DONE
