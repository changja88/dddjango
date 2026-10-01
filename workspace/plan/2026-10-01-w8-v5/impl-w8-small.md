# W8 작은 판 구현 보고 — 비차단 보고 + 정확값 참고 시트

2026-10-01 · 작업 가지 `design/w8-v5` · 기준 커밋 `78a731bd` · 구현 HEAD `676127ba`.

## 결과

`impl-brief.md`와 `review-claude.md` §3의 작은 판을 구현했다. 먼저 `design-w8-small.md`를 작성한 뒤 아래 세 커밋으로 도구, 시트, 기존 감사 연결을 차례로 반영했다. 각 커밋 전에 `make verify-web`을 통과했고, 마지막 `make verify`도 5/5 green이다. 봉인 드리프트를 포함해 최종 검증에서 남은 실패는 없다.

v4 수집·대조의 판정은 유지하면서 출력 순서를 결정적으로 만들었다. 정상 보고는 후보가 있어도 exit 0이다. 같은 원본 census로 정확히 같은 foundation 토큰 후보를 보여 주는 시트를 만들며, 새 입력 결속이나 G1 관문은 없다. G0 수집과 역할 입력 경로, 3-1 비교용 데이터, 3-2 독립 감사의 T/D/F/H 처분, G2 보고 행과 가벼운 측정을 기존 흐름에 연결했다.

P1/P2 보관 입력 6회차는 기존 묶음·후보·구성원 판정을 보존했고, P1 첫 제출 T **35/35**가 후보로 남았다. 실제 레인의 시간 절감과 놓침 수는 아직 미측정이다. 이번 구현 결과로 발주자의 손 전수 대조 축소를 결정하지 않았다.

## 커밋

| 커밋 | 내용 | 커밋 전 검증 |
|---|---|---|
| `21e70dfb` | `feat(web): W8 v4 비차단 보고 도구와 결정성 검증` — 작은 판 설계, v4 수집기·대조 CLI·합성/브라우저 fixture | verify-web exit 0, verify exit 0 |
| `cab38019` | `feat(web): v4 census 정확값 토큰 참고 시트 추가` — 시트 생성기와 정확 일치 회귀 시험 | verify-web exit 0, verify exit 0 |
| `676127ba` | `feat(web): W8 보고와 정확값 시트를 기존 시각 감사에 연결` — reference·Coordinator·기존 역할 입력/반환 연결 | verify-web exit 0, verify exit 0 |

구현 커밋은 이 작업 가지에만 기록했다. 이 최종 보고서는 세 구현 커밋 뒤 작성한 로컬 산출물이며 위 커밋에는 포함하지 않았다.

## 바꾼 파일

플러그인 파일 22개(아래 11쌍)와 설계 1개를 커밋했다. 이번 보고서는 별도로 작성했다.

| Claude 정본 | Codex 미러 | 변경 |
|---|---|---|
| `dddjango-web/assets/style_census.js` | `codex-dddjango-web/skills/dddjango-web/assets/style_census.js` | 신규, v4 스니펫; byte 동일 |
| `dddjango-web/scripts/compare_style_census.py` | `codex-dddjango-web/skills/dddjango-web/scripts/compare_style_census.py` | 신규, v4 대조·결정적 정렬·비차단 CLI; byte 동일 |
| `dddjango-web/scripts/style_value_sheet.py` | `codex-dddjango-web/skills/dddjango-web/scripts/style_value_sheet.py` | 신규, 정확값 토큰 참고 시트; byte 동일 |
| `dddjango-web/scripts/test/fixtures_style_census.sh` | `codex-dddjango-web/skills/dddjango-web/scripts/test/fixtures_style_census.sh` | 신규, 기존 fixture 러너 연결; byte 동일 |
| `dddjango-web/scripts/test/test_style_census.py` | `codex-dddjango-web/skills/dddjango-web/scripts/test/test_style_census.py` | 신규, 최종 19개 시험; byte 동일 |
| `dddjango-web/scripts/test/style_census_browser.py` | `codex-dddjango-web/skills/dddjango-web/scripts/test/style_census_browser.py` | 신규, 기존 v4 브라우저 합성 시험 재사용; byte 동일 |
| `dddjango-web/skills/implementation-ui/references/design-evidence.md` | `codex-dddjango-web/skills/implementation-ui/references/design-evidence.md` | 수집·CLI·시트·처분·측정 상세 계약; byte 동일 |
| `dddjango-web/commands/dddjango-web.md` | `codex-dddjango-web/skills/dddjango-web/SKILL.md` | 짧은 G0/3-1/3-2 연결, 경로 전달, G2 한 행; 의미 미러 |
| `dddjango-web/agents/design-architect-web.md` | `codex-dddjango-web/skills/dddjango-web-design-architect-web/SKILL.md` | census·시트 입력 경로와 해석 소유; 의미 미러 |
| `dddjango-web/agents/coder-web.md` | `codex-dddjango-web/skills/dddjango-web-coder-web/SKILL.md` | 입력 경로·감사 수리 참조; 의미 미러 |
| `dddjango-web/agents/discipline-reviewer-web.md` | `codex-dddjango-web/skills/dddjango-web-discipline-reviewer-web/SKILL.md` | 기존 독립 시각 감사에 W8 입력과 T/D/F/H 반환 연결; 의미 미러 |

개발 산출물은 `workspace/plan/2026-10-01-w8-v5/design-w8-small.md`와 이 `impl-w8-small.md`다. 기존 brief·이전 설계·Claude 검토 파일은 수정하지 않았다. 기존 `Makefile`의 fixture 글롭과 미러 대조를 그대로 사용했다. 매니페스트·버전·봉인·기존 시험 fixture 데이터는 변경하지 않았다.

## 구현 동작과 경계

- 수집기는 스키마 v4, 루트 1요소, SDK 응답/전역/route 교차 확인을 보존한다. SDK 없는 case도 `{}` 기대값 파일을 명시한다. 누락·중복 mapping, 미완성 페이지, schema/root/SDK/정착 문제를 성공 0건으로 숨기지 않는다.
- 대조기의 묶음 전체 키·동점·구성원·표본 선정 순서를 고정했다. 지역 bucket의 메모리 주소 대신 안정된 원본 순서를 사용한다. 정상 보고 exit 0, 사용법·입력 오류 또는 미실행 포함 exit 1이다. exit 2/3이나 자동 G2 차단을 추가하지 않았다.
- 시트는 case/record·부모/자식·가상 요소 참조와 배경·테두리 네 면·반경·shadow 전 층·필터·글자/아이콘·padding/gap 등 census 원값을 보존한다. 같은 클래스라도 관측값이 다르면 묶음을 분리한다.
- 토큰 역조회는 허용 오차 없이 숫자·동일 색 표현·단순 var 별칭·축약 표현을 정규화한다. alpha를 8bit로 반올림하지 않고 shadow 층 순서를 보존한다. 근접값은 채택하지 않는다. 후보가 없으면 `신규 등록 필요`이며 토큰을 자동 생성하지 않는다.
- CSS 전체를 계산하는 도구는 아니다. 계산식·문맥 단위·해결할 수 없는 별칭·동일 이름의 상충 선언은 수동 확인 대상으로 남긴다. v4가 자른 문자열은 정확 일치 근거로 쓰지 않는다. 첫 font-family와 관측 rect/누적 opacity 등 v4의 관측 한계도 reference에 적었다.
- Coordinator는 수집·경로 전달을 맡고, architect가 기존 시각 연결표에서 해석한다. 기존 `discipline-reviewer-web` 감사가 T/D/F/H를 처분한다. T는 G2 전에 수리하고, D는 데이터→분기/variant→스타일의 인과 근거를 남기며 시안 예시 값으로 업무 동작을 고치지 않는다. F/H는 근거, H는 직접 확인 결과도 남긴다.
- 같은 공용 클래스·같은 원인의 T는 부품 단위 수리 1건으로 연결한다. G2의 N은 후보 묶음 수, a는 수리 수이므로 합산 등식으로 취급하지 않는다. 미실행·데이터 미대조·요구 case 중 mapping 밖인 범위는 사유와 함께 k에 기록한다. 실제 측정 전 수치는 `미측정`이다.

## 검증 명령과 결과

명령은 이 워크트리에서 실행했다. Python bytecode 기록을 끄고, 임시 산출물은 허용 TMPDIR에 남겼다. 기존 로컬 Playwright와 Chromium을 사용했으며 새 의존성을 설치하지 않았다.

| 명령/검증 | 결과·exit |
|---|---|
| `make verify-web` — C1, C2, C3 각각 | 모두 **0**. 각각 fixture 파일 20개, 실패 0개. C1 W8 9개, C2/C3 W8 19개 통과. scripts/assets/references byte 미러·기존 역할 문면 self-test·요청 가이드 계약 통과 |
| `PYTHONDONTWRITEBYTECODE=1 make verify` — C1, C2, C3 각각 | 모두 **0**, 5/5 green. 최종 440초, ontology/core/cross/backstop/regen 모두 통과 |
| `claude plugin validate dddjango-web --strict` | **0**. 구조/플러그인 검증 통과 |
| `python3 -B dddjango-web/scripts/test/test_style_census.py` | **0**, 최종 19개 통과 |
| 기존 scratch 대조기를 대상으로 한 결정성 RED 확인 | 해시 시드 6개에서 출력 6종으로 실패 재현. 새 대조기는 동일 시험 통과 |
| 새 시트 CLI/경계 시험의 RED→GREEN | 미구현 시 CLI 실패 확인 후 구현. 다중 단어 서체·v4 문자열 절단 회귀도 실패를 확인하고 수리한 뒤 통과 |
| `W8_PYTHON -B dddjango-web/scripts/test/style_census_browser.py --chromium W8_BROWSER` | **0**. 실제 v4 수집·SDK 6상황·루트 0/복수 검증 통과. 모든 요청은 fulfill/abort로 가로챔 |
| `W8_PYTHON -B W8_EVIDENCE/sheet-browser.py W8_REPO W8_BROWSER` | **0**. 로컬 inline HTML census에서 radius/pad/ink/border/shadow/blur 6토큰과 `::before` 보존 확인; 네트워크 요청 차단 |
| `python3 -B dddjango-web/scripts/compare_style_census.py --design W8_EVIDENCE/sheet-browser-census.json --impl W8_EVIDENCE/sheet-browser-census.json --mapping W8_EVIDENCE/sample-map.json --sdk-scope W8_EVIDENCE/sample-sdk.json --out W8_EVIDENCE/live-self-report.json` | **0**. 실제 v4 census의 제품 CLI 경로: 묶음 0, 후보 0, 미대조 0, 미실행 0 |
| `PYTHONHASHSEED=<0,1,2,3 중 하나> python3 -B W8_EVIDENCE/replay.py W8_REPO W8_ARCHIVE` | 네 번 모두 **0**. 각 실행에서 6회차 저장 JSON 대조와 T35 검증 통과. 회차별 결과 파일 byte 동일 |
| `git diff --check`, `git diff --cached --check` | **0** |
| 새 Coordinator/역할 문면의 Claude/Codex 직접 대조 | 런타임 변수·셸 표기 정규화 뒤 동일. reference는 verify-web의 byte 비교 통과 |

표의 `W8_*`는 실제 실행 경로를 줄여 쓴 자리표시자다.

```text
W8_REPO=/Users/hyun/.herdr/worktrees/dddjango/design-w8-v5
W8_ARCHIVE=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/design-W8
W8_EVIDENCE=/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/w8-small-_cmokte6
W8_PYTHON=W8_ARCHIVE/venv/p2/bin/python
W8_BROWSER=/Users/hyun/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell
```

전체 실행 로그는 `W8_EVIDENCE/c1-verify-web.log`, `c2-verify-web.log`, `c3-verify-web.log`와 짝인 `c1-verify.log`, `c2-verify.log`, `c3-verify.log`에 있다. 최종 make verify 세부 로그는 `/tmp/djr-verify.cl8lJV/`다. 재생 스크립트·회차별 JSON·`replay-seed-0.log`~`replay-seed-3.log`, 실제 브라우저 census·시트·CLI 보고도 `W8_EVIDENCE`에 보존했다. 임시 경로의 파일은 저장소에 커밋하지 않았다.

## P1/P2 보관 재생

| 레인·보관 상태 | 전체 묶음 | 차단 후보 묶음 | 후보 구성원 | 결과 |
|---|---:|---:|---:|---|
| P1 `g2_6311` | 122 | 84 | 346 | 기존 판정 동일, 독립 라벨 T 35/35 포함 |
| P1 `g2_6311_r2` | 91 | 49 | 216 | 기존 판정 동일 |
| P1 `g2_6311_r7` | 60 | 31 | 114 | 기존 판정 동일 |
| P2 `g2_8b3_r2` | 104 | 56 | 110 | 기존 판정 동일 |
| P2 `g2_8b3_r3` | 67 | 28 | 46 | 기존 판정 동일 |
| P2 `g2_8b3_r4` | 63 | 24 | 42 | 기존 판정 동일 |

`run/cmp-dv4decl-*.json`의 묶음 id, 값, 구성원, 후보 구성원과 case 통계를 비교했다. 달라질 수 있는 것은 결정적 정렬에 따른 배열 순서와 구성원 정렬 후 대표 표본 선택뿐이다. 저장본의 미짝 텍스트 배열도 순서를 정규화해 내용과 통계를 대조했다. 시드 0·1·2·3의 **새 출력끼리는 파일 전체 byte가 동일**하다. 해시는 각 seed 로그에 있다.

보관 census에는 구형 schema 3 자료가 있어 과거 v4 대조기와 같은 API 재생 설정(`DECLARED={'ALL'}`, `ALLOW_LEGACY=True`, `SDK_SCOPE=None`)으로 검증했다. 원본의 version이나 메타데이터를 고치지 않았다. 이 결과를 제품 CLI가 구형 입력을 허용한다는 증거로 쓰지 않는다. 제품 CLI의 엄격한 v4·SDK 경로는 위 실제 브라우저 합성·자기 대조와 필수 fixture로 별도 검증했다. CLI에는 legacy 우회나 `ALL` 일괄 선언 옵션이 없다.

## Claude 검토 발견 처분

| 발견 | 처분 | 구현 결과·남긴 경계 |
|---|---|---|
| B1 | 반영 | 작은 판을 레인 안 비차단 보고로 연결. 속도 절감은 실측 뒤 판단하며 발주자 대조 축소는 미포함 |
| M1 | 반영 | W8·시트 모두 참고/보고. 봉인 그림자·입력 결속·새 G1 관문 없음 |
| M2 | 반영/2단계 | 놓침과 F 비율을 셀 재료를 기존 기록에 남김. 분모 관문과 자동 승격은 미구현 |
| M3 | 반영 | 기존 시각 연결표 사용. 도구가 만든 정확값과 정확 일치 토큰 후보만 추가 |
| M4 | 반영 | Coordinator 순증 Claude 2,115B, Codex 2,088B. 기계·처분 계약은 reference에 모으고 명세에는 경로만 전달 |
| M5 | 반영 | Coordinator는 실행·전달, architect는 해석. 출처 연결을 두 번 작성하지 않음 |
| M6 | 반영 | 공용 variant 추가와 부품 단위 수리를 기본으로 명시. 기존 기본값 변경은 사용자 결정 경로 유지 |
| M7 | 반영/2단계 | 수집 schema v4와 대조 의미 유지. 재렌더·exit 3·영향 case·freshness·결속 검사는 미구현 |
| m1 | 반영 | 큰 판 비용 추정을 확정값으로 사용하지 않음. 처분·반송·레인 시간을 실제 기록하도록 연결 |
| m2 | 반영 | 후보가 있어도 exit 0. 시트 부재/생성 실패를 새 G1 관문으로 만들지 않음 |
| m3 | 반영 | impl-brief의 작은 판 승인 범위만 실행. 그림자 비용 승인으로 확대하지 않음 |
| m4 | 반영 | 레이아웃 결속을 명세로 이전하지 않고 기존 원본·시각 연결표·출력 대조 사용 |
| m5 | 반영 | 묶음 동점·구성원·표본 정렬 수정. 합성 6시드, 보관 4시드 결정성 검증 |
| n1 | 반영 | 보고에 실제 작업 가지·기준/구현 커밋 기록. main 작업 폴더 상태 명령 미실행 |
| n2 | 반영 | 변경 표에 Claude/Codex 전체 경로 기재 |

반박한 발견은 없다. 2단계 항목은 구현 확장 지점으로 미리 만들지 않았다.

## 설계와 달라진 점

큰 범위 변경은 없다. 기존 Phase 2 독립 시각 감사의 실제 소유자는 `discipline-reviewer-web`이므로 해당 역할에 연결했고, 설계 파일도 첫 커밋 전에 그 경로로 확정했다. `design-review-web`에 새 감사 역할을 만들지 않았다.

누락 case·불완전한 페이지를 정상 0건으로 보지 않도록 CLI 입력 검사를 구체화했다. 결정성은 묶음 정렬뿐 아니라 매칭 bucket 순서도 고정해야 해서 메모리 주소 의존을 제거했다. 정확값 시트에는 실제 브라우저 표현을 확인하며 다중 단어 서체와 잘린 문자열의 오매칭 방지를 추가했다. 모두 요청한 판정 보존·정확값·결정성을 위한 범위다.

설계의 보관 API/CLI 재생 표현은 실제 자료의 schema를 확인한 뒤 구분했다. 보관본은 원래 legacy API 설정으로 판정 보존을 확인하고, 새 v4 브라우저 산출물로 제품 CLI를 확인했다. 구형 자료를 v4로 가장하지 않았다.

브라우저 합성 시험은 별도 실행 파일로 두었다. `make verify-web`의 새 필수 fixture는 표준 라이브러리 19개이며 Playwright 설치 여부에 따라 건너뛰는 시험이 없다. 실제 브라우저 검증도 이번 작업에서는 별도로 실행해 통과했다.

## 남은 일과 작업 상태

1. 사용자가 선택한 다음 순서는 독립 Claude 리뷰다. 이번 구현자가 별도 리뷰 서브에이전트를 실행하지 않았다. 검토에서 새 결함이 나오면 배포 전에 고쳐야 한다.
2. 다음 1~2 실제 레인에서 첫 T/D/F/H·처분 시간, G2 반송 회차/시간, 놓침 수, 시트 사용 후 첫 T, G0~G2 벽시계를 측정해야 한다. 현재 값은 미측정이며 시간 절감을 주장하지 않는다.
3. 차단 승격·입력 결속·재렌더·재관찰 축소·발주자 대조 축소는 그 결과를 본 후의 사용자 결정이다. 이번 구현과 승인 범위에 포함하지 않았다.
4. 착지·봉인·릴리즈는 운영자 후속 작업이다. push, main 변경, release, `manifest_seal.py --write`를 실행하지 않았다.

추적 중인 제품 파일의 미커밋 변경은 없다. `.venv`는 지시한 기존 venv를 가리키는 미추적 심링크이며 커밋에서 제외했다. 원래 미추적 입력 4개와 이 최종 보고서는 로컬에 남아 있다. 서버·DB·외부 네트워크와 다른 프로세스 조작은 수행하지 않았다. scratch는 읽기만 사용했다.

Serena·Graphify는 이번 요청의 명시적 금지에 따라 사용하지 않았다.

REPORT-DONE
