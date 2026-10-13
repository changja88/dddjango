# 2.5.0 짓기 기록 — dddjango-web 부품 CSS 실림·미검증 감수·상태 단언 뒤 완성 화면 그림

- 날짜: 2026-10-12. 사본 `<S>/web-f88`, `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`.
- 구현 기준: `<S>/f88/design-v2.md`·`design.md`의 규칙 문장/명세 표/갈무리 뼈대. 1단계 결과는 `<S>/f88/impl1.md`에서 받았다. 앞 배포판은 요청 가이드만 바꾼 2.4.2 예정, 목표는 2.5.0이며 이 실행에서 판 올림·커밋·push·배포는 하지 않았다.

## 진행
- 1단계는 이 작업 전에 구현·검증돼 있었다. CS 전용 검사기·러너 패밀리/ID·원인 파일 승인 유입·시험과 Codex scripts 미러가 작업 트리에 있었다. 이번 작업은 그 파일들의 바이트를 보존했다.
- 2단계는 Claude 정본 문구를 먼저 고쳤다. Coordinator에 G0 부품 CSS 점검, 미검증 목록·닫기 절차, G2 상태 단언 뒤 갈무리를 넣고 새 문단 표지 셋을 사용했다. architect는 부품 CSS 표와 완성 그림 행, ui 리뷰어는 두 대조, coder는 CSS 배선·갈무리·미검증 원문 보고, 감수는 미검증 판정 꼴·갈무리 상태 단언 대조를 맡게 했다.
- Django·하우스룰·HTMX·시험 표기·시험 규율 references 다섯을 고친 뒤 Codex로 파일째 복사해 byte 미러를 맞췄다. Coordinator·역할 넷·요약 둘은 기존 플랫폼 도구 이름·스킬 접두·경로 표기를 유지해 의미 미러로 맞췄다.
- 3단계는 Makefile의 종수·문단 표지 셋, AGENTS의 2.5.0 문장·검사 목록·기록 목록, README web 구성 절, 개발 가이드와 HTML의 종수·CS/G2 항목을 바꿨다. 흐름도 원본 `work_flow_web.spec.json`에 남아 있던 G2 전체 `84종`도 HTML의 `92종`·새 검증 항목과 맞췄다. HTML 구조·스타일·실행 코드는 바꾸지 않았다.

## 바꾼 자리
| 묶음 | 자리 | 내용 |
|---|---|---|
| 1단계 검사 | `scripts/src/check_component_css.py`·`backstop.py`·`src/{common,debt,inflow}.py`와 Codex byte 미러 | CS1·92종·원인 파일·단일 병합 증명·빚 밖 |
| 1단계 시험 | 새 `fixtures_patch250_component_css.py`·실행 목록·기존 기대값/종수 정규화 | A–J·U·115개 단언·F0 머리 link |
| Coordinator 두 벌 | 산출물·build-state·G0·G1·슬라이스 끝·G2·마무리 | `design_render`·`cs_unverified[]`·표지 셋·상태 단언 통과 때만 갈무리 보고 |
| 역할 넷 두 벌 | architect·ui 리뷰어·coder·감수 | 명세 표/그림 행·대조·배선·원문 보고·실림/빠짐/판정 못 함 |
| references 다섯 두 벌 | Django §10·하우스룰 §8·HTMX §10·implementation-test §4·discipline-test §4 | 실림 규칙·검사 출력·승인 유입·미검증·갈무리 |
| SKILL 요약 둘 두 벌 | implementation-django·implementation-test | 문서 머리 CSS·갈무리 상태 단언 |
| 저장소 | Makefile·AGENTS·README web 절·DEVELOPMENT·HTML 둘·workflow spec | 92/85·CS1·문단 대조 19·새 G2 항목 |
| 기록 | `plan-2.5.0.md`·이 파일 | 결정·정의·파일 목록·시험·한계·실행 증거 |

## 설계와 구현이 달라 구현대로 적은 것
1. 승인 유입은 blob 등식뿐 아니라 기준 뒤 원인 파일을 바꾼 첫 부모 걸음이 같은 승인 병합 하나뿐이어야 한다. L 증명도 그 병합에서만 받는다. 두 병합의 누적 상류판이 원인 둘을 한 병합 몫으로 잘못 묶는 것을 막는 1단계 보강이다. 하우스룰 §8의 CS1 승인 유입과 이 계획에 적었다.
2. 동적 link 주소의 못 읽음은 살아 있는 머리 link만이다. 본문·죽은 link는 주소를 몰라도 머리 실림이 아니므로 그 미검증 후보 밖이다. Django §10·하우스룰 §8·HTMX §10에 적었다.
3. 1단계의 F0 정상 트리는 primary_button을 쓰므로 그 CSS link 한 줄을 셸에 더했다. 종수/실행 목록만 고친다는 설계 목록보다 넓지만 정상 트리의 뜻을 유지한 최소 보강이다. 이번 실행에서 시험을 다시 고치지 않았고 이 기록에만 그 사실을 적었다.

## 검증 — 1단계 보고에서 받은 값
| 명령·대조 | 결과 |
|---|---|
| `.venv/bin/python -B dddjango-web/scripts/test/fixtures_patch250_component_css.py`(구현 전) | PASS 9 / FAIL 93 — red |
| 같은 새 묶음(최종) | PASS 115 / FAIL 0 |
| `PATH="$PWD/.venv/bin:$PATH" bash dddjango-web/scripts/test/run_fixtures.sh` | exit 0 · 양수 FAIL 요약 0 |
| 마지막 묶음들 | static 공백 75/0 · 지속 셸 432/0 · 부품 CSS 115/0 · 빚 119/0 · 치환 196/0 · SDK 368/0 · 리팩토링 판정 309/0 |
| 호스트 사본 `--all --only cs` | exit 2 · 18문서 중 12문서·52빠짐 쌍 · 조건부 1 · 조각 뿌리 14(45 CSS 쌍) · 미검증 표시 15건 — 시제품과 같음 |
| 지문·상수 | `e49c83776ff9faf6 92 7` |
| scripts byte diff·diff check | 출력 없음 |

위 호스트 값은 받은 보고의 값이다. 이번 실행에서는 호스트나 기존 사본을 읽거나 실행하지 않았다.

## 검증 — 이번 실행
| 명령·대조 | 결과 |
|---|---|
| `make verify-web`(아래 실행 환경) | exit 0 · 17묶음 PASS 3,816 / FAIL 0 · 새 CS1 115/0 · self-test 두 자리·core 답 블록·입구·문단 19·역할 7·0T·scripts/assets·references 12 대조 모두 통과 |
| `diff -r -x test -x __pycache__ dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts` | 출력 없음 · exit 0 |
| `git diff --stat -- dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts` | 16 files changed, 106 insertions(+), 46 deletions(-) — 1단계와 같음(미추적 새 파일 셋은 stat 밖) |
| `.venv/bin/python -B -c "import sys; sys.path.insert(0,'dddjango-web/scripts'); from src import debt; import backstop; print(debt.scanner_stamp()['checks'], backstop.TOTAL_CHECKS, len(backstop.SLICE_END_DEFERRED))"` | `e49c83776ff9faf6 92 7` |
| `claude plugin validate dddjango-web --strict` | exit 0 · `✔ Validation passed` — 설정 위치를 TMPDIR 안 별도 폴더로 지정 |
| 1단계 파일 바이트 대조 | scripts·test 파일 80/80 바이트가 시작 때와 같음(`__pycache__` 제외) |
| 문단·미러 대조 | 새 표지 셋을 포함한 Coordinator 19/19 대조 통과·references 다섯 5/5 byte 같음·의미 미러 새 문장 대조(플랫폼 도구·입력·스킬 이름 차이는 유지) |
| 보호 범위·문서 형상 | REQUEST_GUIDE 두 파일·README 55–75·core/ontology 무변·HTML 둘의 script/style 블록 무변·workflow 원본 JSON 파싱 정상 |
| `git diff --check` | 출력 없음 |
| `grep -rn '91종\|84종' dddjango-web codex-dddjango-web README.md AGENTS.md Makefile docs` | `scripts/test/fixtures_subst.sh:1061–1062`만 — 비교 대상 HEAD 91/84를 현재 92/85와 함께 정규화하는 1단계 회귀 시험 문자열. 수정 금지 범위라 보존 |

전체 실행 명령은 `PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T make verify-web`이다. Python 실행은 이 venv를 쓰고 로그·임시 파일은 TMPDIR 안에 뒀다. 로그: `/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/f88-prose-verify-web.log`.

전체 검증의 마지막 출력(exit 0):

```text
fixtures_sdk.sh: fixtures_sdk: PASS=368 FAIL=0
fixtures_refactor_audit.sh: fixtures_refactor_audit: PASS=309 FAIL=0
[verify-web] refactor_audit self-test(Claude·Codex 두 자리 — 플랫폼 구조 판별) · 상시 답 블록 core 대조
요약: self-test claude · 점검 절 106 · 어구 27 · 극성 표본 18 · red 0
요약: self-test codex · 점검 절 106 · 어구 27 · 극성 표본 18 · red 0
[verify-web] 리팩토링 입구 표지 대조(입구 ↔ Coordinator)
[verify-web] 문단 Claude·Codex 대조(플랫폼 토큰 치환 뒤)
[verify-web] 역할 7 판 확인 지문 경계 줄 Claude·Codex 대조
[verify-web] codex 미러 byte 대조(scripts — test/ 픽스처는 Codex 에 싣지 않는다 · assets)
[verify-web] references byte 미러 대조(지식 스킬 12 — Codex 는 dddjango-web-<스킬> 접두 폴더)
```

## 안 한 것·운영자 확인
- 이번 실행은 scripts·test·REQUEST_GUIDE·README 요청 가이드 요약·core 두 플러그인·ontology·매니페스트·git 설정을 수정하지 않았다. 커밋·push·배포·새 패키지 설치도 하지 않았다.
- `make verify`·독립 검토·실제 web 화면의 브라우저 갈무리는 이번 범위 밖이다. 운영자는 요청 가이드 2.4.2 착륙 뒤 합친 판 검증과 2.5.0 배포를 맡는다. 실제 web 작업에서 상태 단언·captures 결과·브라우저 미실행 보고를 확인한다.
- Serena·Graphify는 사용자 금지에 따라 사용하지 않았다.

## 2026-10-12 코드 검토 반영 — 시험 먼저

- 출발 CS 시험은 115/0이었다. R 재현 58개 가운데 50개 RED를 코드 수정 전에 확인했고, 최종은 R 58/0·CS 합계 173/0이다. RED 로그는 `red.log`(42)·`red-followup.log`(3)·`red-modes.log`(2)·`red-target-blob.log`(1)·`red-alias-scope.log`(2)다.
- F1 원본 `--full-tree` 시도를 포함한 첫 전체 실행은 기존 CS 미검증 알림 때문에 `fixtures_patch230`의 byte 비교 세 칸이 실패했다(953/3). 원본 시도 때문인 차이는 아니다. «기존 기대 변경 없음» 조건에 따라 common 원본 시도는 되돌리고 CS 전용 목록을 기준점 트리·변경 파일·이동 세 곳에 썼다. common·inflow는 이 라운드 시작 바이트 그대로다.
- 기존 기대 변경은 `fixtures_patch230.py:both`의 `U 게이트(--diff-base)`·`U --slice-end`·`U --all` 세 byte 비교다. 새 CS 미검증 줄·요약과 그 묶음이 남긴 빈 줄 하나만 빼고 기존 발견·exit·종수 정규화 비교를 그대로 유지했다. 다른 기존 기대는 바꾸지 않았다.
- `PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 bash dddjango-web/scripts/test/run_fixtures.sh`는 종료 0·17묶음 3,872/0이었다(CS 171/0인 시점). 직후 F6 with 별칭 두 시험을 추가해 RED→GREEN 173/0을 확인했다. 최종 `PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 make verify-web`는 그 두 시험까지 포함해 종료 0·17묶음 **3,874/0**이다. 마지막 묶음은 SDK 368/0·refactor_audit 309/0이고 Claude/Codex self-test 106절·27어구·18극성 표본·red 0, 문단·역할 경계·scripts/assets·references 미러 대조도 통과했다.
- 지문·상수 명령의 끝줄은 `e49c83776ff9faf6 92 7`이다. scripts `diff -r -x test -x __pycache__ ...`는 출력 없이 종료 0이다. runtime references 셋은 byte 미러, Coordinator·감수 항목 12는 양 플랫폼 문단 대조로 확인했다. `git diff --check`도 출력 없음이다.
- 보존한 `git archive HEAD dddjango-web/scripts` 도구와 표준 fixture·호스트 TMP 사본을 대조했다. 기존 검사 출력은 종수 글자만 정규화해 byte 동일, 호스트 빚 스캔은 169줄 byte 동일이다. 하위 폴더의 pre-existing ST0 `web/legacy`도 최종은 그대로다. F1 원본 시도에서만 잘못된 새 폴더 ST0가 사라졌으며, 최종은 CS 옛 누락을 차단에서 기존 알림으로 바꿨다(`ctx.base_files=0`, CS 목록 74).
- 처음 성능 트리는 600개 생성 페이지 외 기본 빈 문서 1개가 있어 중간값 0.811초였다. 정확히 600문서인 새 트리에서 보존한 출발 도구 **0.705초**·최종 **0.902초**(각 3회 중간값), **1.28배**·exit 0이다. 처음 0.811초의 두 배 안에도 든다.
- 바꾼 문장은 하우스룰 §8의 실림·대입·키·거름·판독 실패·이동 생략·own 부재 교정·한계, Django/HTMX §10의 새 판독 사유, Coordinator와 감수 12의 확인 대상뿐이다. 계획의 «코드 검토 반영»·한계를 더했다. 요청한 한계들은 구현을 넓히지 않고 감수 대상으로 적었다.
- 호스트 원본에서 실행하지 않았고 clone/TMPDIR 밖에는 쓰지 않았다. core 두 플러그인·ontology·REQUEST_GUIDE·README·manifest·git 설정은 이 라운드에서 변경하지 않았다. 커밋·push·stash·배포·패키지 설치·Serena·Graphify·네트워크는 쓰지 않았다. 실제 브라우저·Python 3.9 실행은 하지 않았으며 HTML reader의 None 반환은 지정 venv에서 주입해 검증했다.

검증 로그·재현·성능·앞뒤 출력은 `/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/f88-repair-6eotdmu1`에 있다. 최종 검증 로그는 `verify-web.log`, CS 로그는 `cs-last173.log`·`r-58-last.log`, byte 대조는 `comparison-end.log`, F1 앞뒤는 `f1-evidence.log`, 정확한 600쪽 시간은 `perf-start-exact.log`·`perf-end.log`다.


## 2026-10-12 산문 수리 — 두 리뷰의 모든 지적
- A 차단 1·2와 사소 1~14, B 차단 1~5와 사소 1을 D1–D6으로 합쳐 Claude 정본부터 고치고 Codex 의미 미러를 맞췄다. 겹친 지적은 한 규칙으로 썼고 런타임에는 검토 이력을 넣지 않았다.
- «이번 요청 몫» 정의는 Coordinator의 «부품 CSS 미검증»에 한 번 두었다. 범위 밖·승인 병합 유입·사용자 미커밋 원문은 보고만 하고, 이번 명세가 받는 기존 조각은 표·G0 목록으로 감수에 잇는다. 공유 조각은 받는 문서 전부의 근거가 있어야 실림이다.
- 리팩토링의 표/그림 행 제외·기존 누락/미검증 보고만·새 blocker 구조 검사 처분을 Coordinator·architect·UI 리뷰어·coder·감수 12에 적었다. 못 읽음의 변수 템플릿·동적 CSS 주소·새 판독 실패 사유도 역할과 하우스룰에서 함께 확인한다.
- G2 목록 정리·작은 수정 길·G0 배너·G1 두 선택·갈무리 반송/재감수·PNG 쓰기/매번 이동/tmp 지움·2배 시안·coder 토대·UI 중복·CS 빚 제외를 고쳤다. Codex 상태 판독 비보장 문구는 문단 대조 밖의 세 의무에 넣었다.
- 코드 fix1의 거름·못 읽음 출력·이동 대응 생략 출력은 현재 코드를 다시 읽어 확인했다. 하우스룰의 거름 설명과 이동 info 예시는 이미 맞아 보존했고, 못 읽음 예시는 사유별 실제 꼴로 구체화했다. 이동 대응 생략의 설계 반송/재실행 문장을 Coordinator에 넣었다.
- references 다섯은 Claude 파일을 Codex에 byte 복사했다. 스크립트 diff 시작값은 `16 files changed, 113 insertions(+), 47 deletions(-)`이다. scripts·core 두 벌·ontology·REQUEST_GUIDE·README 55–75를 시작 바이트로 기록해 끝에 대조한다. 새 시험·스크립트 변경·커밋·push·stash·설정 변경·Serena·Graphify·네트워크는 이 라운드 범위 밖이다.

- 최종 검증: `PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T make verify-web` 종료 0 · 17묶음 PASS 3874 / FAIL 0 · CS1 173/0. Claude/Codex self-test는 각 106절·27어구·18극성 표본·red 0이며 문단 19·역할 경계·scripts/assets·references 12 대조도 통과했다. 마지막 산문 교정은 G1 완성 그림 행 확인의 리팩토링 제외다.
- references 다섯의 직접 `cmp`는 `cmp: 5/5 byte 동일`·종료 0이다. `CLAUDE_CONFIG_DIR=/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/f88-prose-round-p2m6ykdu/claude-config DISABLE_AUTOUPDATER=1 TMPDIR=/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T claude plugin validate dddjango-web --strict`는 `✔ Validation passed`·종료 0이다(설정 위치는 TMPDIR 안).
- CS1 출력 틀·고정 문구·못 읽음 사유 28개를 `rg -n -F`로 검사기·러너·공통 출력 코드에서 대조했다. 경로·숫자 자리값을 제외한 불일치는 0이다. 보호 파일·README 구간 329개는 시작 바이트와 같고 스크립트 stat 끝줄도 `16 files changed, 113 insertions(+), 47 deletions(-)`로 시작과 같다. `git diff --check`는 출력 없이 종료 0이다.
- 이번 라운드 증거: `/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/f88-prose-round-p2m6ykdu`의 `verify-web.log`·`plugin-validate.log`·`messages.log`·`audit-final.log`. 닫지 못한 지적과 코드 변경이 필요한 지적은 없다.


## 2026-10-13 2차 검토 반영 — 마지막 고침
- 출발 CS 시험 173/0, `git diff --stat -- dddjango-web/scripts | tail -n 1`은 `12 files changed, 72 insertions(+), 35 deletions(-)`였다. 처음부터 있던 사용자 변경은 보존했다.
- 시험을 먼저 추가해 고유 RED 53개를 확인했다. 첫 P5b fixture는 Git 유사 rename이 되지 않아 검토 원문의 줄 배치로 고쳐 실제 R100 아닌 rename과 잘못된 기존 누락 판정을 재현했다. 그 준비 실패는 RED 53에 넣지 않았다. 로그의 첫 선별 실행은 137/45, P5b 보정 뒤 s/v는 54/27이었다. CSS 링크 대상 부재, byte 동일(권한/index), 목록 판독 실패, own의 불필요한 flat 입력은 각각 추가 RED를 확인한 뒤 고쳤다.
- CS 시험은 125개 늘어 최종 298개다. 기존 기대 변경은 `B static as` 0→1, `R F6 별칭 순서대로 재대입` 0→2, `R F6 with 안 실제 static 대입` 0→1, `H 같은 제품 지속 셸 SH4 초록` 0→1이다(뒤의 P1′로 0으로 되돌림). 모두 P1의 변수/별칭 주소 금지이며 H는 href의 변수 버전 꼬리도 읽지 않는 까닭이었다. 나머지 F6의 미검증/누락 기대와 겹따옴표·따옴표 없는 static·`block.super|safe`의 초록은 유지했다. M6은 기대를 바꾸지 않고 시험 이름만 현재 skip 규칙에 맞췄다.
- B n2b는 별칭 기준점 자체가 P1에서 미충족임을 `--all` blocker로 고정했다. 그 별칭을 제거한 gated 결과는 같은 CSS의 기존 누락이다. A P1과 H의 동적 줄이 기준점에도 있으면 알림을 재출력하지 않는다 — 새 blocker와 literal 교정은 그대로다.
- 지운 것은 `_STATIC_AS`, `_HREF_VAR`, `Template.static_as`, `aliases` 목록·`alias()` 해석 함수·static 대입 이벤트와 공용 `ctx.rename_pairs`다. CSS/템플릿의 판정 입력 변경만 따로 읽고, 권한만 바뀌거나 index에서 빠져도 실제 바이트가 같은 현물은 새 발견으로 만들지 않는다. 형식 T는 링크 해소 결과가 달라질 수 있어 변경이며, 기준점 목록 오류를 빈 목록으로 확정하지 않는다.
- P2 입력은 모든 렌더 템플릿(extends·include·block 출처), literal link CSS와 읽는 import 닫힘의 내용, 필요한 CSS의 존재 여부(own이 없을 때 flat fallback 포함), 제품 선언이다. V 묶음은 41/0으로 모든 변경의 재판정과 그대로/무관한 변경/필요 CSS 내용만 변경/권한/index/목록 실패/불필요 flat 변경의 건너뛰기를 고정한다. 미검증은 여전히 변경 파일 거름 없이 키만 비교한다.
- 없는 CSS·web 밖 템플릿·없는 include/extends·없는 CSS 링크 대상은 기준점 판독 실패가 아니다. 실제 git show·UTF-8·링크 형식 실패의 누락은 기존으로 확정하지 않는다(P2는 유지). 이동은 R100·슬라이스 0 경로 행만 받으며 unstaged 이동은 한계로 적었다.
- 기존 검사는 `git archive HEAD dddjango-web/scripts | tar -x -C <TMP>/base` 도구와 표준/제품 지속 셸 fixture의 all·gated 출력, 빚 출력/JSON이 같았다. 호스트 독립 사본은 기존 검사 339줄·blocker 83건이 종수만 정규화해 byte 같았고, Git을 붙인 별도 임시 사본의 빚 출력 169줄·JSON도 같았다. 처음 같은 사본을 순차 실행한 비교는 CY 기준선 생성 때문에 달라져 독립 사본으로 다시 비교했다.
- 600페이지와 A의 정확한 1,355-template 사본을 모두 TMP에서 측정했다. 초기 동시 실행은 25~55초로 흔들렸으므로 단독으로 다시 쟀다. CSS 읽기 공유 전 600페이지 9회 중간값은 0.801515→0.833827초로 성능 조건을 못 채웠다. 같은 Tree의 CSS 읽기만 공유한 뒤 R/T/V 131/0, 600페이지 9회(호출 순서 교대) 중간값은 0.736920→0.706687초(0.959배), 1,355개 3회 중간값은 11.639374→8.357206초(0.718배)로 모두 이전 라운드보다 빠르다. 두 Tree의 캐시는 나뉘며 파일·템플릿 해석 범위는 늘리지 않았다.
- CSS 읽기 공유까지 포함한 코드 관문 `PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 make verify-web`는 종료 0·17묶음 3,999/0·CS 298/0이다. 지문은 `e49c83776ff9faf6 92 7`, scripts mirror diff와 `git diff --check`는 무출력이다. 기존 19문단·역할 7·references 12·scripts/assets 대조도 통과했다.
- 산문은 Claude부터 조정자·설계자·UI·coder·감수 5개와 house/Django/HTMX reference 3개를 고치고 Codex 의미/byte 미러를 맞췄다. 공유 조각의 범위 밖 받는 문서까지 전수 확인·문서별 제품 CSS·게이트 새 줄 기본 귀속·슬라이스 미커밋/화살표 양쪽·리팩토링 초기 미확인 입력·playwright 수집 실패의 미실행 우선·hx-get/임베드의 G1′ 조건을 반영했다. CS1 고정 문구·틀·사유 39개를 `rg -n -F`로 checker/common/inflow에서 확인했다(불일치 0).
- 새로 확인한 충돌은 P1과 SH4였다. P1은 href의 `?v={{ root_state.shell_rev }}`도 읽지 않고 SH4는 그 꼬리를 요구한다. P1′(운영자)로 CS1이 정확한 SH4 꼬리 하나만 떼고 읽게 고쳤다 — 시험 H 기대 0 복귀 · 새 시험 6(정확한 꼬리 · 공백 없는 꼴은 실림, 다른 변수 · `|upper` · `&x=` 덧붙음 · `?w=` 는 동적) · 고치기 전 코드에서 꼬리 시험 셋 붉음. 규칙 글 다섯 자리(Claude · Codex 같은 글). 실제 브라우저·최종 독립 검토·배포는 실행하지 않았다.
- core 두 플러그인·ontology·REQUEST_GUIDE·README 보호 구간 등 249개 항목은 시작 바이트와 같다. Serena·Graphify·네트워크·패키지 설치·commit/push/stash·git 설정 변경은 하지 않았다(시험의 Git 저장소/커밋은 TMP 합성 fixture뿐이다).
- 증거 폴더: `/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/f88-last-ge0q1jli` — `logs/red-names.log`(53)·`logs/verify-code-final.log`·`logs/comparison-final.log`·`logs/perf600-cache-nine.log`·`logs/perf1355-cache.log`·`logs/messages-final.log`. 산문 적용 뒤 최종 검증 결과는 아래에 이어 적는다.

- 산문·미러·기록 적용 뒤 최종 `PATH="$PWD/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 make verify-web`도 종료 0 · 17묶음 PASS 3,999 / FAIL 0 · CS 298/0이다. P1′ 적용 뒤(운영자) 다시 돌린 값은 CS 304/0 · 17묶음 4,005/0 · 종료 0이다(`f88/fix4-checks.log`). SDK 368/0·refactor_audit 309/0, 양 플랫폼 self-test 각 106절·27어구·18극성 표본·red 0이며 조정자 문단 19·역할 7·scripts/assets·references 12 대조를 모두 통과했다. 끝줄은 `[verify-web] references byte 미러 대조(지식 스킬 12 — Codex 는 dddjango-web-<스킬> 접두 폴더)`다. 로그는 `logs/verify-final.log`.
- `CLAUDE_CONFIG_DIR=<증거 폴더>/claude-config DISABLE_AUTOUPDATER=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 claude plugin validate dddjango-web --strict`는 종료 0 · `✔ Validation passed`다(`logs/plugin-validate.log`). 별도 문단 19 대조·이번 reference 3 byte 대조도 통과했다.

## 2026-10-13 3차 검토 반영 (사용자 «가.» 12:25 · 운영자)
- 3차 검토 둘(Codex 차단 4 · Claude 차단 1 · 사소 6)의 차단 다섯과 회귀 소음 하나를 고쳤다. 시험 묶음 W 를 먼저 적어 고치기 전 코드에서 11개 붉음을 확인했다(제품 소속 1 · HTML 기호 2 · literal + SH4 꼬리 2 · super 필터 3 · CSS 아닌 link 3).
- 제품 소속: `judged` 에 «기준점과 제품 소속이 다른 문서» 를 더했다(`old.product != a.product`). 렌더 입력이 같아도 area 판별이 바뀌면 필요 CSS 뿌리가 바뀐다.
- HTML 기호: `Template.tokened` 가 원문 Django 토큰이 있던 속성만 기록한다. static 태그 · 동적 토큰 판정은 그 속성에만 하고, `&#123;` 등을 풀어 생긴 글자는 글자 주소로 읽는다.
- literal 경로 + SH4 꼬리: 동적 판정도 꼬리를 뗀 href 로 한다.
- `block.super` 필터: 부모 block 을 inert 로 걸어 부품 요구는 세고 link 는 실림으로 세지 않는다. 머리의 `block.super 필터 판독 불가` 는 그대로다.
- rel 이 글자이고 stylesheet 가 아닌 link 는 동적 판정 앞에서 건너뛴다(뒤의 중복 stylesheet 거름은 지웠다).
- 글: Claude · Codex 조정자 G0 3번의 G1′ 생략 조건(hx-get · 임베드 자리를 더하거나 바꾸면 표가 있어도 생략 안 함) · houserules §CS1 · implementation-django §10 네 문장(Codex references byte 복사).
- 정리: `common.py` 의 `ctx = …; return ctx` 군더더기를 되돌렸고, V 의 헛단언 이름을 «필요 CSS 삭제는 요구가 사라짐» 으로 바꿨다.
- 검증: CS 326/0(304 + W 22) · 빚 지문 `e49c83776ff9faf6 92 7` · scripts 미러 diff 무출력 · references 12 cmp 같음 · `git diff --check` 깨끗. 증거 `S/f88/fix5/`.

## 2026-10-13 4차 검토 반영 (사용자 «가.» · 운영자)
- 4차 검토 둘(Codex 차단 3 · Claude 차단 1 · 사소 3 — 겹침 빼고 차단 3)의 지적과 세지 않은 한 건(맨 앞 `/` 없는 경로)을 고쳤다. 고침안은 따로 만든 사본에서 먼저 시험했다 — 새 시험 9 가 4차 코드에서 붉고 고친 코드에서 초록.
- `Template.parts`: 속성마다 (원문 토큰인가, 글자) 조각을 남기고 `_href` 가 조각으로 static 태그 · SH4 꼬리 · 동적 토큰을 가린다(속성 단위 `tokened` 를 대신함).
- `/` 로 시작하지 않는 글자 주소는 실림이 아니다. 기존 기대 둘을 바꿨다(S «literal 경로» 0→1 · W «SH4 꼬리 + literal 경로» 0→1).
- 제품 소속 비교를 판정 입력 변경 조건 밖으로 옮기고 기준점 판독 실패 문서를 뺐다. 제품만 바뀐 문서의 원인에 그 area 아래 생성·삭제를 더했다(승인 유입 가름).
- 글: houserules §CS1 네 문장(/static/ 주소 · 조각별 토큰 출처 · 제품 소속 비교와 작업 트리 area 한계 · 승인 유입 원인) · implementation-django §10 한 문장(Codex references byte 복사).
- 검증: CS 333/0 · 빚 지문 `e49c83776ff9faf6 92 7` · scripts 미러 같음 · `git diff --check` 깨끗.

## 2026-10-13 5차 검토 반영 (사용자 «가.» · 운영자)
- 5차 검토 둘(Codex 차단 4 · Claude 차단 1 · 사소 1 — 사소는 Codex 둘째와 같음)을 따로 만든 사본에서 고친 뒤 옮겼다. 새 시험 6 이 5차 코드에서 붉고 고친 코드에서 초록(W 끝).
- `_href`: 떼어 낸 SH4 꼬리 앞 · static 태그 뒤 공백을 주소 안 글자로 둔다. `moved_product`: 기준점 제품이 None 인 판독 실패만 뺀다. 원인 보탬은 `not causes` 일 때만. `inflow.py` CS1 가름: HEAD 에 없는 원인이 작업 트리에 있으면 거절.
- 글: houserules §CS1 · implementation-django §10 의 literal 주소 문장(Codex references byte 복사).
- 검증: CS 340/0 · 빚 지문 `e49c83776ff9faf6 92 7` · scripts 미러 같음.

## 2026-10-13 배포 사본 통합 (2.4.4 위)
- 배포된 2.4.4(F4-91 · `6e339a5b`) 위에 얹었다 — 패치 충돌 0. F4-91 의 Z9(2.4.3 러너와 SH1 밖 출력 대조)는 CS1 이 2.5.0 에 생긴 검사라 대조식에서 CS1 줄 · 검사 종수를 뺐다(`without_sh1`).
- 6차는 사용자 결정대로 새 탐색 없이 5차 반례의 재현만 다시 돌렸다(Claude).
