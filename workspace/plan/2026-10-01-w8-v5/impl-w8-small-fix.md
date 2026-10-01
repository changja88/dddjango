# W8 작은 판 수정 보고

작성: 2026-10-02 KST · 지시/리뷰: 2026-10-01 `fix-brief.md` · `review-impl-claude.md`.
작업 가지 `design/w8-v5` · 수정 기준 `676127ba` · 최종 HEAD `89ae4738`.

## 결과와 커밋

요청한 **M1·M2와 minor 4건을 모두 반영**했다. 최종 `make verify-web`은 fixture 파일 20개 실패 0개, W8 시험 35개 통과이며 `make verify`는 5/5 green이다. 봉인 드리프트를 포함해 남은 검증 실패는 없다.

| 커밋 | 변경 | 커밋 전 검증 |
|---|---|---|
| `9e7f39eb` | `fix(web): 정확값 토큰 정규화와 W8 시트 크기 수정` — M1 표현 정규화·서체 스택·수동 확인, M2 값 색인·속성 분류·표본 제한 | `make verify-web` exit 0, W8 25개 |
| `89ae4738` | `fix(web): W8 CLI 실패 처리와 관측 자료 보관 규칙 수정` — minor 4건, v4 속성 분류 보완, 실제 Chrome에서 확인한 float32 반올림 경계 보완 | 최종 `make verify-web` exit 0, W8 35개; `make verify` exit 0, 5/5 |

이 보고서는 두 수정 커밋 뒤 작성한 로컬 산출물이며 위 커밋에는 포함하지 않았다.

## 발견별 처분 — 위치·시험·수정 전후

아래 코드 위치는 Claude 정본 기준이며 대응 Codex 파일도 함께 고쳤다.

| 발견 | 고친 위치와 동작 | 수정 전 실패 → 수정 뒤 통과 |
|---|---|---|
| **M1: 있는 토큰을 신규 등록 필요로 표시** | `scripts/style_value_sheet.py`의 `color`, `serialized`, `TokenIndex.lookup`, 서체 정규화. sRGB 관측 정밀도·legacy rgba/hex alpha·sRGB color-mix·첫 서체를 처리하며 미해석 잠재 후보는 수동 확인 | 실제 P1 표현과 토큰을 넣은 `test_p1_serialized_colors_shadow_and_font_find_existing_tokens`에서 누락 재현 → 다섯 토큰 모두 출력. hex alpha 기존 불일치 단언을 관측 계약에 맞게 수정하고 통과. 미해석 색/단위와 near 값 시험도 통과 |
| **M2: 시트 크기·잡음·범주 무관 후보** | 같은 파일의 `value_rows`, `category`, `token_category`, `TokenIndex`, `render_sheet`. 기본값 제거, 값 색인, 속성별 토큰 색인, 구성원/관계 표본 제한 | 기본값·잘못된 토큰 후보·크기 상한 시험 실패 재현 → 모두 통과. P1 1,108,053B → 87,938B, P2 790,258B → 71,871B |
| **m1: 입력 오류 뒤 이전 report 잔존** | `scripts/compare_style_census.py`의 `clear_report`, `ReportParser.error`, `_main`. 입출력 경로 충돌을 거절하고 이전 보고를 먼저 제거 | 성공 보고 생성 → 없는 mapping case로 재실행 시 이전 파일이 남는 실패 재현 → exit 1·보고 파일 없음. 인자 오류도 경로가 파싱됐으면 제거. 일부 case 미실행은 새 진단 보고를 남기는 시험 통과 |
| **m2: 도구 결함까지 미실행으로 은폐** | 두 CLI의 `InputError` 입력 검증과 `_main`/`main` 경계. 파일·JSON·명시적 입력 오류는 1, 예상 밖 실행 결함은 traceback + 70 | 유효 입력에서 `KeyError`, `TypeError`, `AttributeError`, `IndexError`, `ValueError`를 비교/시트 핵심 호출에 주입한 10개 경우 모두 이전에는 exit 1로 은폐 → 모두 traceback·exit 70. 잘못된 JSON/인코딩/구조는 exit 1·traceback 없음 |
| **m3: G0 토큰 시점에 시트 고정** | `skills/implementation-ui/references/design-evidence.md` §3-2와 Coordinator 3-2 | 이전에는 G0 생성 지점만 있음 → 3-2 시작 시 같은 원본 census와 **현재** foundation으로 시트를 다시 생성하도록 명시. 문면·실행 순서와 양 런타임 미러를 직접 대조 |
| **m4: 큰 원자료가 빌드 커밋에 누적** | reference §W8 파일 표·보관 규칙, Coordinator의 보관/작성 권한과 G0/역할 전달 경로, architect/coder/감사 입력 경로 | 이전 `observations/` 기본 커밋 경로 → 큰 census·대조 JSON은 `private/w8/`와 좁은 ignore 예외. 임시 Git 저장소에서 해당 원자료만 ignore되고 mapping·시트·visual-check는 커밋 후보로 남는 것을 확인 |

m3·m4는 실행 코드를 바꾸는 항목이 아니므로 소스 문자열 존재만 검사하는 영구 시험을 만들지 않았다. 명령·경로·역할 간 연결을 대조하고, m4의 ignore 패턴은 실제 Git 명령으로 확인했다.

## M1 — 표현 정규화와 관측 한계

리뷰의 다섯 사례는 최종 P1 시트에서 다음 후보로 잡힌다.

| 관측 값 | 최종 후보 |
|---|---|
| `color(srgb 1 0.992157 0.976471 / 0.52)` | `--glass-tint-strong` |
| ink 색 두 층의 `0 2px 6px / 0.07`, `0 10px 28px / 0.1` shadow | `--shadow-2` |
| jade 색 `color(srgb 0.309804 0.541176 0.423529 / 0.14)` | `--success-soft` |
| ink 색 `color(srgb 0.121569 0.109804 0.0941176 / 0.06)` | `--surface-muted` |
| `Pretendard Variable` | `--font-sans` · **첫 서체 일치(스택 확인)** |

비교기의 시각 허용 오차는 사용하지 않는다. 토큰을 관측 형식으로 정규화해 비교한다. sRGB는 Chrome의 **float32 저장 후 유효숫자 6자리**, legacy rgb/rgba는 byte 채널과 alpha 표현으로 비교한다. `#01020380`과 `rgba(1,2,3,.5)`가 실제 Chrome에서 같은 문자열이 되는 점을 반영했다. 원래 선언 두 값의 무한 정밀도 동일성을 주장하는 것은 아니다.

단순 double `.6g`만 쓰면 채널 8·80·131·182에서 Chrome 출력과 달랐다. 실제 브라우저 재현값 `0.0313726`, `0.313726`, `0.513726`, `0.713726`을 영구 시험에 넣어 네 실패를 확인한 뒤 float32 단계를 반영했다. 최종 구현은 별도 브라우저 검증에서 **8bit RGB 채널 256개와 hex alpha 256개, 총 512개**를 모두 찾았다.

`color-mix(in srgb, …)`는 두 색의 비율과 premultiplied alpha를 계산하고 transparent 혼합도 처리한다. shadow의 층 수·순서는 유지한다. `0.1` 대 `0.11`, `26px` 대 `26.4px`, sRGB alpha `0.5005` 대 `0.5`, 뒤집힌 shadow 층은 계속 구별한다.

다른 색 공간, 지원 밖 색/함수, 문맥 단위, 다중 선언·순환/미해결 var 등 잠재 토큰을 해석하지 못하면 **수동 확인**이다. 잘린 관측값과 속성별 토큰 분류가 지원되지 않는 행도 신규 등록의 근거로 쓰지 않는다. 서체 스택은 첫 서체만 관측하므로 fallback 스택을 직접 확인해야 한다.

관련 영구 시험은 `scripts/test/test_style_census.py`의 다음 항목이다.

- `test_p1_serialized_colors_shadow_and_font_find_existing_tokens`
- `test_hex_alpha_matches_indistinguishable_browser_serialization` — 이전 `test_alpha_is_not_rounded_to_eight_bits`를 교체
- `test_chrome_float32_channel_rounding_boundaries_match`
- `test_srgb_visible_alpha_precision_is_not_collapsed`
- `test_unresolved_tokens_make_matching_property_manual`, `test_unsupported_named_color_is_not_reported_as_missing`
- 기존 exact/near·shadow 층·가상 요소·문자열 절단 회귀 시험

## M2 — 시트 크기와 생성 시간

| 자료 | 수정 전 | 최종 수정 후 | 크기 감소 | 생성 시간 전 → 후 |
|---|---:|---:|---:|---:|
| P1 시안, 10 case | 1,108,053B · 7,739줄 | **87,938B · 554줄** | **92.06%** | 45.949초 → **0.418초** |
| P2 시안, 36 case | 790,258B · 5,253줄 | **71,871B · 437줄** | **90.91%** | 37.323초 → **0.210초** |

동일 보관 census와 `/Users/hyun/Desktop/spring_dream_server/web/design_system/foundation/tokens.css`를 읽어 기준 `676127ba`의 시트 생성기와 최종 생성기를 비교했다. 파일 크기는 UTF-8 byte다. 시간은 같은 장비에서 각각 P1→P2 순서로 한 번 실행한 측정이며 성능 보장이나 레인 전체 시간 절감 수치가 아니다.

보관 시안은 schema 3이므로 **크기·시트 로직 측정용 메모리 사본에서만** `census_version=4`, `root_matched='body'`, `route_set=None`을 보충했다. 이는 리뷰의 측정 조건과 같다. scratch 원본을 바꾸거나 실제 v4 관측으로 승격하지 않았다. 엄격한 v4 경로는 별도의 실제 브라우저 관측으로 확인했다.

시트 앞에는 **속성 종류·값 → 후보·등장 묶음 수** 색인이 있다. 뒤의 모양 묶음은 값 ID를 참조한다. 기본값/키워드, census의 `bd` 합성 행, 관측 메타데이터를 줄였고, 네 면이 같으면 `bd.all`로 표현한다. 후보는 종류와 용도에 맞춰 좁히며 6개와 나머지 개수, 구성원·부모·자식은 개수와 첫 2개를 표시한다. 전체 원값·rect·관계는 원본 census에 남아 있다.

`op 1`의 z-index 후보, `lh 13px`의 font-size 후보, border 폭의 tracking 후보가 사라지는 시험을 넣었다. 실제 v4의 `tfc`는 색, `sw`는 테두리 폭, `w/h`는 치수로 분류하는 회귀도 고정했다. 토큰의 정규형은 관측 속성/표현별 색인으로 재사용해 매 행마다 모든 토큰을 다시 비교하지 않는다.

상한은 **100,000B**로 정했다. 최종 P1 87,938B에 여유를 둔 수십 KB 수준이며, 영구 시험 `test_lane_sized_sheet_bounds_lists_and_deduplicates_value_index`는 **240묶음·7,200 records와 여러 색·치수·shadow 값**으로 크기 폭증을 잡는다. 실제 출력의 값/묶음을 잘라 상한을 맞추는 기능은 없다.

## CLI와 보관 계약

대조기는 정상 보고에 후보가 있어도 exit 0이다. 입력 오류·미실행은 exit 1이다. **일부 case 미실행으로 새 보고가 생성된 exit 1**과 **입력 오류로 보고가 없는 exit 1**을 문면에서 구분했다. 입력과 출력이 같은 경로면 입력을 보존하고 거절한다. 입출력 경로를 파싱한 인자 오류도 이전 보고를 제거한다. 경로를 확정하지 못했거나 출력 정리 자체가 실패한 호출은 어떤 보고도 소비하지 않는다.

두 CLI의 예상 밖 실행 결함은 traceback과 **exit 70**이다. 70은 도구 결함을 드러내는 코드이며 스타일 차단·재렌더 판정이 아니다. exit 2/3, 입력 결속 검사, 재렌더, 새 품질 관문은 추가하지 않았다.

보관 정책의 근거는 기존 `design-evidence.md`의 로컬 private 증거와 `private/hero-response.json`·`private/hero-browser.json` 예시, Coordinator의 비공개 원문 커밋 제외 관례다. 이를 W8의 큰 기계 원자료에 한정해 적용했다.

| 빌드 폴더 안 위치 | 보관/커밋 |
|---|---|
| `private/w8/style-census-design.json`, `style-census-impl.json`, `style-report.json` 및 회차 사본 | 같은 레인의 감사가 읽을 수 있게 로컬 보존; 커밋 제외 |
| `observations/style-cases.json`, `style-sdk.json`, `style-values.md` | 기존 빌드 기록과 함께 커밋 |
| 기존 `visual-check.md`의 경로·T/D/F/H 처분·측정 | 기존대로 커밋 |
| 빌드 폴더의 `.gitignore` | Coordinator가 `/private/w8/` 한 행만 추가; 다른 기록을 통째로 무시하지 않음 |

이미 추적 중인 과거 원자료를 자동 삭제하거나 Git 이력을 고치지 않는다. 이번 작업은 플러그인의 규칙과 경로를 고친 것이며 타깃 Django 프로젝트의 파일이나 `.gitignore`를 직접 변경하지 않았다.

## 판정 보존과 결정성 재검증

| 보관 회차 | 전체 묶음 | 후보 묶음 | 후보 구성원 | 결과 |
|---|---:|---:|---:|---|
| P1 `g2_6311` | 122 | 84 | 346 | 기존 동일 · 독립 라벨 **T 35/35** 후보 유지 |
| P1 `g2_6311_r2` | 91 | 49 | 216 | 기존 동일 |
| P1 `g2_6311_r7` | 60 | 31 | 114 | 기존 동일 |
| P2 `g2_8b3_r2` | 104 | 56 | 110 | 기존 동일 |
| P2 `g2_8b3_r3` | 67 | 28 | 46 | 기존 동일 |
| P2 `g2_8b3_r4` | 63 | 24 | 42 | 기존 동일 |

각 회차를 `PYTHONHASHSEED=0,1,2,3`에서 재생했다. 저장 JSON의 묶음 id·값·구성원·후보 구성원과 case 통계를 대조했고, 새 출력은 네 시드에서 **파일 전체 byte 동일**이다. 해시도 수정 전 제품판과 같다.

```text
P1 g2_6311     f400faf33805e3d66fd5643820075cc41c171c4799afcd5e6c780ef70b2eb2f3
P1 g2_6311_r2  2264fc165a21b30edcb6bdb097a7fcaba2fccfd82f4d0cfa74f3d06cfa3383b1
P1 g2_6311_r7  395fbf2a8ebebf8259548788e5da6382ec8c3ab785430750998a633be7a52b75
P2 g2_8b3_r2   951e5621cb5d1f2d0caabcd6d3fca6e1cca5944bc523856d8015264bed97e232
P2 g2_8b3_r3   f979ce89c0b4d98fe1b1d5d1cee7295a8363c5e5e6a6e7434383de201611b380
P2 g2_8b3_r4   868aec09ed4e5159cf328af040f76189aaa7358db70066f65464eb3a2fa7e41d
```

보관 재생은 이전 검증과 같은 API 설정 `DECLARED={'ALL'}`, `ALLOW_LEGACY=True`, `SDK_SCOPE=None`을 사용했다. 보관 원본 메타데이터를 수정하지 않았고 제품 CLI에 legacy 우회 옵션을 추가하지 않았다. 원본 v4와의 비교에서 허용한 차이는 기존 결정적 정렬에 따른 배열 순서와 대표 표본 선택뿐이며, 이번 수정 전후 제품 출력끼리는 byte가 같다.

## 검증 명령·exit와 증거

| 명령/검증 | 결과 |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 make verify-web` — C1 | **exit 0** · fixture 파일 20개 실패 0 · W8 25개 · byte 미러/기존 self-test 통과 |
| 같은 명령 — 최종 C2 | **exit 0** · fixture 파일 20개 실패 0 · W8 **35개** · scripts/assets/references/REQUEST_GUIDE 및 self-test 통과 |
| `PYTHONDONTWRITEBYTECODE=1 make verify` — 최종 | **exit 0** · **5/5 green**, 263초 · 봉인 드리프트 없음 |
| `python3 -B dddjango-web/scripts/test/test_style_census.py` | **exit 0**, 최종 35개 |
| `W8_PYTHON -B dddjango-web/scripts/test/style_census_browser.py --chromium W8_BROWSER` | **exit 0**, 실제 v4 SDK 6상황·루트 0/복수 통과 |
| `W8_PYTHON -B W8_EVIDENCE/sheet_browser.py W8_REPO W8_BROWSER` | **exit 0**, 실제 v4 census에서 다섯 P1 토큰+hex alpha·구별 가능한 near alpha 제외 확인 |
| `W8_PYTHON -B W8_EVIDENCE/precision_matrix.py W8_REPO W8_BROWSER` | **exit 0**, 실제 Chromium 256 채널 + 256 alpha = **512개 통과** |
| `python3 -B dddjango-web/scripts/compare_style_census.py --design W8_EVIDENCE/sheet_browser.json --impl W8_EVIDENCE/sheet_browser.json --mapping W8_EVIDENCE/browser-mapping.json --sdk-scope W8_EVIDENCE/browser-sdk.json --out W8_EVIDENCE/browser-report.json` | **exit 0**, 실제 v4 제품 CLI 경로: 묶음/후보/미대조/미실행 모두 0 |
| `PYTHONHASHSEED=<0,1,2,3 각각> python3 -B W8_EVIDENCE/replay.py W8_REPO W8_ARCHIVE` | 네 번 모두 **exit 0**, 6회차 대조·T35·byte 결정성 통과 |
| `python3 -B W8_EVIDENCE/measure.py <기준 또는 최종 생성기> <출력 접두사>` | **exit 0**, 위 크기·시간 측정 |
| 임시 저장소 `git check-ignore --no-index --stdin` | **exit 0**, raw census/report만 매치; mapping/시트/visual-check 제외되지 않음 |
| `git diff --check`, `git diff --cached --check` | **exit 0** |
| Coordinator 3-2·역할 W8 입력 경로 직접 대조 | 런타임 변수/셸 표기 정규화 후 동일; reference는 byte 동일 |

`W8_*`는 표에서 줄여 쓴 실제 경로다.

```text
W8_REPO=/Users/hyun/.herdr/worktrees/dddjango/design-w8-v5
W8_EVIDENCE=/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/w8-small-fix-2s84ihrw
W8_ARCHIVE=/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/design-W8
W8_PYTHON=W8_ARCHIVE/venv/p2/bin/python
W8_BROWSER=/Users/hyun/Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell
```

실패 재현 로그는 `sheet-red.log`, `sheet-edge-red.log`, `sheet-named-red.log`, `sheet-v4-categories-red.log`, `sheet-precision-red.log`, `cli-red.log`, `cli-encoding-red.log`, `cli-args-red.log`다. 실패 재현 명령의 exit 1은 의도한 RED 결과이며, 최종 green과 구별한다.

최종 로그는 `final-unit.log`, `final-verify-web.log`, `final-verify.log`다. C1 커밋 전 로그는 `c1-verify-web.log`다. 중간 C2 전체 검증도 통과했지만 float32 경계 보완 뒤 최종 검증을 다시 실행했다. 최종 make verify의 상세 로그는 `/tmp/djr-verify.xg4A5T/`다.

`measure-before.log`, `measure-final.log`, `before-p1.md`·`before-p2.md`, `final-p1.md`·`final-p2.md`, 재생 스크립트·시드 로그·JSON, 브라우저 관측 JSON/시트와 512개 직렬화 관측도 `W8_EVIDENCE`에 보존했다. 임시 증거를 저장소에 커밋하지 않았다. 브라우저는 기존 로컬 실행기를 사용했고 모든 요청을 abort/fulfill로 가로챘으며 서버·외부 네트워크를 사용하지 않았다.

## 변경 파일과 남은 일

수정 파일은 플러그인 **16개, 8쌍**이다.

| Claude 정본 | Codex 미러 |
|---|---|
| `dddjango-web/scripts/style_value_sheet.py` | `codex-dddjango-web/skills/dddjango-web/scripts/style_value_sheet.py` |
| `dddjango-web/scripts/compare_style_census.py` | `codex-dddjango-web/skills/dddjango-web/scripts/compare_style_census.py` |
| `dddjango-web/scripts/test/test_style_census.py` | `codex-dddjango-web/skills/dddjango-web/scripts/test/test_style_census.py` |
| `dddjango-web/skills/implementation-ui/references/design-evidence.md` | `codex-dddjango-web/skills/implementation-ui/references/design-evidence.md` |
| `dddjango-web/commands/dddjango-web.md` | `codex-dddjango-web/skills/dddjango-web/SKILL.md` |
| `dddjango-web/agents/design-architect-web.md` | `codex-dddjango-web/skills/dddjango-web-design-architect-web/SKILL.md` |
| `dddjango-web/agents/coder-web.md` | `codex-dddjango-web/skills/dddjango-web-coder-web/SKILL.md` |
| `dddjango-web/agents/discipline-reviewer-web.md` | `codex-dddjango-web/skills/dddjango-web-discipline-reviewer-web/SKILL.md` |

scripts/reference는 byte 미러, Coordinator/역할은 의미 미러다. 수집 스니펫, 기존 비교 판정 알고리즘, Makefile, 매니페스트·버전·봉인은 변경하지 않았다.

요청한 M1·M2·minor 4건의 미해결 항목은 없다. 남은 순서는 독립 Claude 재검토와 실제 1~2 레인의 처분·반송·놓침·벽시계 측정이다. 시트 생성 시간 개선을 레인 전체 속도 개선으로 바꾸어 주장하지 않는다. 차단·입력 결속·재렌더·발주자 대조 축소는 이번 범위 밖이다.

리뷰 nit n1~n3는 이번 수정 지시의 대상이 아니므로 별도 확장하지 않았다. n3의 브라우저 fixture는 기존 수동 실행 구조를 유지하되 이번에도 실제 실행해 통과했다.

push·main 변경·릴리즈·`manifest_seal.py --write`는 실행하지 않았다. 다른 프로젝트와 scratch 원본에는 쓰지 않았다. 기존 `.venv` 심링크·사용자 입력·이전 보고서는 보존했다. 구현 수정은 모두 커밋했으며 이 최종 보고서는 로컬 파일로 남겼다.

Serena·Graphify는 명시적 금지에 따라 사용하지 않았다.

REPORT-DONE
