# Design evidence file contract

This reference defines the machine-readable boundary used by
`check_design_evidence.py`. JSON files identify bytes and results. Put the
human comparison, differences, interactions checked, and any remaining doubt
only in `visual-check.md`.

## Command sequence and exits

Run from an installed plugin with explicit absolute or working-directory paths:

```bash
python scripts/check_design_evidence.py --build BUILD --project-root PROJECT --phase inputs
python scripts/check_design_evidence.py --build BUILD --project-root PROJECT --phase visual --fingerprint
python scripts/check_design_evidence.py --build BUILD --project-root PROJECT --phase visual
python scripts/backstop.py PROJECT --diff-base COMMIT --design-build BUILD
```

`--fingerprint` validates inputs and prints calculated `input_digest` and
`implementation_digest`; it never writes or updates an evidence file. Record
those printed values only for a new observation round. Exit 0 means the
declared phase is consistent, 1 means a usage/internal error prevented the
check, and 2 means a defect or insufficient evidence. `--phase visual` always
rechecks inputs. `backstop.py --design-build` joins the visual phase to the
existing 26 checks; `--only` cannot disable it. Without `--design-build`, the runner
discovers source-bearing builds under `PROJECT/.dddjango-web/` and validates all
of them. Git index/HEAD paths retain deleted source records as design signals;
deleted config/build-state records are read from the index and then HEAD.
An explicit build selects one discovered project build; an unrelated external
passing folder cannot replace it. External build locations remain supported when
there is no project-local source-bearing build. A `design_source` object of type
`PROJECT` (or a legacy Claude Design pointer without a type) without a discoverable
build requires an explicit build path. `DESIGN_SYSTEM` token pointers alone do not
signal a screen design.

A non-design run may omit `--design-build` without rechecking past design builds
only when its valid `--diff-base` resolves to exactly one current state's
`git_snapshot`, that state says `has_design_screen=false`, and its build has no
source markers. `.dddjango-web/config.json` must be unchanged since the base,
including deletion and an untracked copy. Past design builds are not judgment
input for this run: their phase, approval, slice status and record changes do not
block the skip. The runner prints a skip notice with the past build count;
missing or ambiguous conditions retain the full design check. Explicit build
selection still identifies the requested build; it does not infer or authenticate
the user's current scope from a folder name. The final blocker total
includes structural and design defects. Completion/CI uses the runner exit code,
never a filtered structural-only output line.

## `design-input.json` version 1

Evidence pointer paths and manifest-list paths are relative to `BUILD` and
remain confined there. `reference_root` is a directory relative to `BUILD`.
Every manifest's `files[].local_path`, `entrypoint`, and every case
`entrypoint.path` are relative to `reference_root`. This supports independently
frozen entrypoints in one unchanged source tree. `host_files`, when present, contains
approved paths relative to `PROJECT`; these bytes join the implementation
digest. Every pointer object has exactly `path` and the lowercase SHA-256 of
the referenced bytes.

```json
{
  "version": 1,
  "reference_root": "design-ref",
  "manifests": [
    "login-source-manifest.json",
    "profile-source-manifest.json"
  ],
  "scope": {"path": "scope.md", "sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
  "coverage_review": {"path": "coverage-review.md", "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
  "host_files": ["config/urls.py"],
  "cases": [
    {
      "id": "login/default",
      "screen": "login",
      "state": "default",
      "viewport": [1280, 720],
      "scope_refs": ["scope.md#login-default"],
      "entrypoint": {"path": "login/screen.html", "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},
      "reference_capture": {"path": "captures/login-original.png", "sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"},
      "media": [
        {
          "id": "hero-video",
          "kind": "video",
          "environment": "staging",
          "endpoint": "/api/media/hero",
          "identity_pointer": "/asset/id",
          "source_pointer": "/asset/src"
        }
      ]
    }
  ]
}
```

`cases` and `manifests` are nonempty. Case IDs are unique; viewport values are
positive integer `[width, height]`; `scope_refs` is a nonempty list. The
entrypoint path/hash must match a successful row in one listed manifest. Each static
manifest must be version 1, `source_ready: true`, have a nonempty successful
file list and a valid entrypoint. The checker compares every recorded path,
size and hash with local bytes and rescans supported static dependencies. A
reference capture must be a valid image container. A valid original image may
be both entrypoint and reference capture.

Static collection supports HTML/CSS literal resources, `x-import`, literal ES
imports, literal dynamic imports, `export ... from`, and literal imports in
inline script/module bodies. Comments, quoted strings, inert template chunks,
and regular-expression bodies do not create imports. Imports inside template
interpolations are scanned; malformed/ambiguous template interpolation is
explicitly unsupported. Detected nonliteral imports, JSX `src`/`href`/`poster`
expressions, and bare module specifiers are blocked. There is no JavaScript executor, bundler,
import-map resolver, or claim of complete runtime dependency discovery.
Runtime-only resources require original-browser observation and independent
audit.

For multiple entrypoints, run each collection against the same reference root
and give it a distinct sibling manifest:

```bash
python scripts/freeze_design.py SOURCE/login.html --out BUILD/design-ref --manifest BUILD/login-source-manifest.json
python scripts/freeze_design.py SOURCE/profile.html --out BUILD/design-ref --manifest BUILD/profile-source-manifest.json
```

This is compatible with the existing sibling-manifest convention; no manifest
migration or rewritten `local_path` is required.

## Original engine source archives

For a dynamic design engine/export, follow `design-acquisition.md`. The archive
collector preserves the entire supplied tree without static dependency claims.
An archive manifest has `version: 1`, `collection: "archive"`,
`archive_ready: true`, `source_ready: false`, and the usual entrypoint/source_root/files.
The collector also records `dependencies` for its entrypoint: each row contains
`source_document`, `source`, `kind`, `local_path`, `status`, and `reason`. Status is
`ok` (local file present), `missing` (absent/escaping local path), `inline`,
`external`, or `runtime`. Missing literal local dependencies make collection exit 1;
the copied bytes and report remain available. `archive_ready` only describes byte
preservation. Remote/dynamic references still require original browser observations.
For every case, this checker recomputes local dependencies from frozen bytes, even
for old archives without this report. A matching partial inventory cannot hide a
missing component, stylesheet, script, or asset. Non-case archived screens are not
treated as required rendering entrypoints.
Use exactly one archive manifest for the entire reference_root; cases may point to
different original HTML/JSX rows in it. Do not mix or duplicate per-screen manifests
in the archive path. Its manifest lives outside reference_root. Its full file inventory (except
`.DS_Store`) must match reference_root after Unicode NFC normalization of both sides
(git checks names out as NFC, macOS unzip writes NFD; digests keep the manifest strings).
A name repeated after normalization on either side, two rows opening one file, symlinks
and changed/missing/extra files fail. The collector writes entrypoint, local_path and
archived file names in NFC. Empty non-entry files are preserved. This is an original source archive,
not a successful static source manifest with failures excused. Static manifests
retain every previous byte, type and dependency-closure requirement.

An archive case entrypoint must identify an original HTML/JSX row. Every such case
requires a `source_observation` path/sha256 pointer relative to BUILD. It points to:

```json
{
  "version": 1,
  "archive_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "entrypoint": {"path": "screen.dc.html", "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
  "case_id": "login/default",
  "screen": "login",
  "state": "default",
  "viewport": [390, 844],
  "url": "http://127.0.0.1:9000/screen.dc.html",
  "observed_at": "2026-09-07T03:30:00Z",
  "capture": {"path": "captures/login-original.png", "sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},
  "trace": {"path": "captures/login-original-observation.json", "sha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"}
}
```

The archive hash is the hash of the manifest bytes. Entrypoint, case ID, screen,
state, viewport and capture must match the case exactly. The trace is nonempty
actual browser output, not a Coordinator assertion that rendering passed. It
includes the observed URL, browser viewport, selected content boundary/crop,
state transition actions, DOM/style/resource observations and failed requests.
The case viewport describes the implementation comparison viewport; when an
engine canvas contains several screens, record its actual browser viewport and
content crop separately in the trace. Never silently equate them. The independent
reviewer checks the original URL/version, crop/state correspondence, resource
completeness, font fallback and visual content; JSON consistency cannot prove them.
All archive bytes and observation/trace/capture bytes enter the input digest.

Before the independent coverage review, use `--phase prepare`. This validates
source/observation connections and returns a `review_digest` that excludes the
coverage review pointer/content to avoid a circular hash. `coverage_review` may
be null during preparation. **Prepare success never authorizes implementation.**
Give the digest and all actual inputs to the independent reviewer. Preserve their
returned report verbatim with these two standalone lines:

```text
reviewed-input: <review_digest from the preparation command>
review-result: pass
```

A failed independent review returns `review-result: fail`; do not rewrite it.
After preserving the review and updating its pointer, run the actual `inputs`
phase. Archive inputs require a matching reviewed-input and pass result, as well
as the original browser evidence. Changed source/cases/observations require fresh
preparation and independent review. A fingerprint is not a new observation.
The prepare command is usable before web/ implementation exists. The existing
`--fingerprint` behavior still requires valid inputs and web/ implementation.

## `visual-evidence.json` version 1

```json
{
  "version": 1,
  "input_digest": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "implementation_digest": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
  "visual_check": {"path": "visual-check.md", "sha256": "1111111111111111111111111111111111111111111111111111111111111111"},
  "cases": [
    {
      "id": "login/default",
      "url": "http://127.0.0.1:8000/login/",
      "viewport": [1280, 720],
      "capture": {"path": "captures/login-implementation.png", "sha256": "2222222222222222222222222222222222222222222222222222222222222222"},
      "result": "pass",
      "media": [
        {
          "requirement_id": "hero-video",
          "response": {"path": "private/hero-response.json", "sha256": "3333333333333333333333333333333333333333333333333333333333333333"},
          "browser": {"path": "private/hero-browser.json", "sha256": "4444444444444444444444444444444444444444444444444444444444444444"}
        }
      ]
    }
  ]
}
```

The visual case set and viewport values must exactly match `design-input.json`;
each case needs a nonempty URL, valid capture, and `result: "pass"`. The URL
is the document URL the browser loaded, as `location.href` reports it; media
sources are resolved against it. The
original and implementation captures may have identical bytes after a perfect
match, but they must not be the same file or hardlink. Independent creation is
confirmed from the browser trace by the final auditor.

The implementation digest covers every path and byte under `PROJECT/web`, plus
the declared `host_files`. It includes additions and reflects deletions. The
only exclusions are directories `__pycache__`, `.pytest_cache`, `.mypy_cache`,
`.ruff_cache`; files `*.pyc`, `*.pyo`, and `.DS_Store`. Directory symlinks under
`web/` are rejected; the checker does not traverse them. There is no caller
exclude option.

## Media observations

A media requirement has exactly `id`, `kind` (`image` or `video`),
`environment`, `endpoint`, `identity_pointer`, and `source_pointer`. Pointers
use RFC 6901 path form beginning with `/`, including `~0` for `~` and `~1` for
`/`. Array selectors are canonical nonnegative decimal tokens: `0` or a
nonzero digit followed by digits. Object keys retain literal token semantics.
Pointers must resolve in the response `body` to a nonempty identity and source URL.
When the identifier in `endpoint` exists only after observation (for example a
record created during the case), name that path segment `{name}` (ASCII
letters, digits, `_`; not starting with a digit) before any `?` or `#`. The
observed endpoint must equal the requirement with each `{name}` replaced by one
nonempty segment without `/`, `?`, `#`, or whitespace, other than `.` or `..`;
a repeated name must take the same value. Everything else, including any
`{name}` in a query or fragment, compares literally.

Response evidence has exactly:

```json
{"observed_at":"2026-09-06T12:00:00Z","environment":"staging","endpoint":"/api/media/hero","status":200,"body":{"asset":{"id":"hero-42","src":"https://cdn.example/hero.mp4"}}}
```

Browser evidence for video has exactly:

```json
{"observed_at":"2026-09-06T12:00:01Z","current_src":"https://cdn.example/hero.mp4","status":206,"loaded":true,"playback_start":0.0,"playback_end":1.25}
```

For an image, omit `playback_start` and `playback_end`. Observation timestamps
are timezone-aware ISO 8601 strings. API and browser statuses must be 2xx, `loaded` must be
true, response source resolved against the case `url` (RFC 3986 reference
resolution of a relative source such as `/media/a.png`, with no further
normalization; a document `<base>` is not applied) must equal `current_src`,
and video playback values must
be finite numbers with end greater than start. Media observation rows must
match requirements exactly, without omissions, additions, or duplicate IDs.

Do not record request credentials or headers. Keep raw responses containing
sensitive signed URLs in local private evidence; do not commit them to a public
repository. These JSON checks establish correspondence, not the authenticity
of the browser/tool environment or the meaning of the media. HTTP failure,
identity/source mismatch, stopped playback, a seed, or a sample substitute
cannot support `pass`.

## W8 — 비차단 스타일 보고와 정확값 시트

W8는 기존 시각 감사의 판단 자료다. `check_design_evidence.py`의 입력/visual 계약,
G1 토큰 검사, 기존 브라우저 확인과 발주자 G2는 그대로 수행한다. W8 파일의 부재나
후보 수로 새 기계 관문을 만들지 않는다. 원본 census가 없는 기존 빌드, DOM 없는
이미지 시안, 수집 실패는 `visual-check.md`에 미수행/미대조 사유로 남긴다.
구버전 관측값의 version만 바꿔 v4로 취급하지 않는다.

### G0: 같은 원본 캡처에서 수집·시트 생성

원본 `render_audit.js` 수집 자리에서 같은 렌더 상태의 각 case에
`assets/style_census.js` 본문을 `page.evaluate(source, options)`로 실행한다.
콘솔 실행이면 `(<스니펫 본문>)(options)`다. 새 브라우저 드라이버를 만들지 않는다.
원본/구현 모두 글꼴과 유한 animation이 정착한 같은 viewport·루트 크기에서 수집하고,
판정자가 화면 아래도 볼 수 있는 전체 높이 스크린샷을 함께 보존한다.

```javascript
// root는 해당 case의 비교 틀 한 요소. SDK 없는 case의 routeSet은 null이다.
{root: "#app", placeholders: [], exclude: [], routeSet: null,
 sdkGlobals: [], page: 0, pageSize: 100000, budgetMs: 5000}
```

`placeholders`는 원본이 실제 placeholder로 정의한 영역, `exclude`는 기존 스코프에서
비교 밖으로 정한 영역만 쓴다. 결함을 숨기기 위해 배경·자식 효과·SDK 영역을 제외하지
않는다. root selector는 정확히 한 요소여야 한다. 전체 body를 명시적으로 관측하는
기존 v4 상태(`root:null`, `root_matched:"body"`)도 보존되지만, root 실패의 대체값은 아니다.

출력은 v4 `{meta, records}` 그대로다. `meta.census_version`, `root_matched`,
`route_set`과 실제 `vendor` 응답·`sdk_globals`를 수집기가 기록한다. SDK case는
운영자 호스트 차단만 있는 표준 상태(`routeSet:["operator-hosts"]`)에서 수집하고,
해당 등록의 SDK 전역 이름을 `sdkGlobals`로 전달한다. SDK 파일 차단 같은 전용 실패
시험은 기존 SDK 확인으로 남기며 W8의 미실행을 정상 스타일 일치로 바꾸지 않는다.

아래 경로는 빌드 폴더 기준이다. census는 기계 반환값을 저장하며 값을
손으로 보정하지 않는다. `pages>1`이면 같은 상태에서 모든 페이지를 받아 `i` 순으로
records를 합치고 `records_total` 개수와 맞춘다. `partial`은 페이지 합치기로 해소되지
않으므로 수집 실패로 기록한다.

| 파일 | 내용 |
|---|---|
| `private/w8/style-census-design.json` | `{원본_case_id: v4 census}` |
| `private/w8/style-census-impl.json` | 3-1에서 같은 방식으로 수집한 `{구현_case_id: v4 census}` |
| `observations/style-cases.json` | `{원본_case_id: 구현_case_id}`. 비교 대상마다 하나, 구현 id 중복 없음 |
| `observations/style-sdk.json` | 등록 목록에서 옮긴 `{구현_case_id: {"files":[벤더 URL 경로], "globals":[전역 이름]}}`. SDK 없음은 `{}` |
| `observations/style-values.md` | 원본 census와 프로젝트 foundation으로 생성한 참고 시트 |
| `private/w8/style-report.json` | 3-2 대조 출력. 회차는 기존 기록에서 구별하며 첫 보고와 처분 결과를 덮어 잃지 않는다 |

기존 로컬 private 증거 관례를 따라 큰 census·대조 JSON은 `private/w8/`에 보존한다.
Coordinator는 빌드 폴더의 `.gitignore`에 **`/private/w8/` 한 행만** 추가한다.
다른 빌드 기록을 통째로 제외하지 않는다. mapping/SDK 입력·작아진 시트·기존
`visual-check.md`의 경로/처분/측정은 커밋 대상이다. 첫 회차 원자료도 이 제외 폴더에
보존해 같은 레인의 독립 감사가 읽게 한다. 이미 추적 중인 원자료를 자동 삭제하거나
Git 이력을 재작성하지 않는다.

아래 `TOOL_ROOT`는 전달받은 실제 도구 루트다(Claude: 플러그인 루트,
Codex: 설치된 `skills/dddjango-web/`). `BUILD`와 `PROJECT`도 실제 경로로 치환한다.

```bash
python TOOL_ROOT/scripts/style_value_sheet.py \
  --census BUILD/private/w8/style-census-design.json \
  --tokens PROJECT/web/design_system/foundation/tokens.css \
  --out BUILD/observations/style-values.md
```

시트는 종류·클래스 서명·가상 요소·비기본 style 값이 같은 묶음의 대표값을 낸다.
앞의 «값 → 토큰» 색인은 값·후보·등장 묶음 수를 한 번만 싣고, 뒤의 묶음 표가 값 ID를
참조한다. 기본값(none/auto/normal/0/transparent 등)·메타데이터·bd 합성 행은 생략한다.
네 면이 같은 border는 `bd.all`로 묶는다. 다른 variant는 별도 묶음이며 구성원·부모·자식은
개수와 첫 2개만 싣는다. 전체 값·rect·관계는 원본 census의 case#record로 확인한다.
`bd` 네 면과 색/폭, `rad` 네 모서리, `pad`·`gap`, `sh` 전 층, `bf`·`fil`,
글자·아이콘 값은 census에 있는 범위에서 읽는다. rect·누적 opacity는 관측값이고
CSS 선언 자체라는 뜻은 아니다. v4의 `ff`는 첫 서체만이며 fallback 전체를 보증하지 않는다.

시트는 비교기의 허용 오차를 사용하지 않는다. 관측 직렬화 형식에 맞춰 숫자·RGB/hex/sRGB
색, 단순 var 별칭, padding/radius/gap 축약, shadow 색 위치·생략된 0을 정규화한다.
sRGB는 Chrome의 float32 저장 후 6자리 유효숫자, legacy rgb/rgba는 byte 채널·alpha 표현에서 비교한다.
따라서 `#01020380`과 `rgba(1,2,3,.5)`처럼 관측 문자열이 구별하지 못하는 선언은 같은 후보며
선언 원값의 무한 정밀도 동일성을 주장하지 않는다. sRGB에 남아 있는 alpha 정밀도는 보존한다.
`color-mix(in srgb, …)` 두 색의 비율과 alpha를 계산하며 transparent 혼합도 지원한다.
shadow 층 수·순서는 보존한다. 서체 스택은 **첫 서체 일치(스택 확인)** 후보로 표시한다.
색·길이·shadow 등 값 종류와 fs/fw/lh/자간/반경 등 이름의 용도로 후보를 좁히고, 후보는
짧은 이름순 6개와 나머지 개수만 싣는다(전체는 tokens.css 확인). 해석 가능한 후보가 없고
해당 행에 걸릴 미해석 토큰도 없을 때만 **신규 등록 필요**다. 다중 선언·순환/미해결 별칭·
계산식·문맥 단위·지원 밖 색 등 잠재 후보가 있으면 **수동 확인 — 해석 못 한 토큰 N개**다.
잘린 관측값도 수동 확인이며 신규 등록의 근거가 아니다.
P1 규모 회귀의 시트 상한은 100,000B다. 실제 레인의 개별 값/묶음을 잘라 통과시키는
상한이 아니며, 큰 시트는 앞 색인부터 읽고 원자료에서 필요한 묶음을 확인한다.
토큰 파일 부재도 정상 참고 시트로 출력한다. 시트 CLI는 생성 0, 미실행/사용법 오류 1,
예상 밖 도구 결함은 traceback과 exit 70이다. 어느 쪽도 새 G1 관문이 아니다.

원본 census·시트의 **경로만** architect와 coder에게 준다. 값·행 id를 명세에 펼쳐
결속하지 않는다. architect가 원본과 기존 시각 연결표에서 후보의 적용 selector·용도·
조합을 해석하며, Coordinator가 같은 해석을 다시 만들지 않는다. `신규 등록 필요`는
토큰 자동 추가 지시가 아니다. 원본/토큰의 표현 한계를 확인하고 기존 등록 규율을 따른다.

### 3-1: 비교용 예시 데이터

시안 case를 렌더할 때 쓰는 데이터는 **시안 예시 글을 재현한다(시각 고정 포함)**.
자리는 캡처 하네스(빌드 폴더 `observations/`) 또는 그 하네스만 쓰는 전용 모듈뿐이다.
기존 시험이 쓰는 fixture·factory·시드 데이터는 바꾸지 않는다. 회귀 시험용 데이터
(긴 출생지 등)는 그대로 두고 별도 회귀 case로 확인하며 W8 비교 mapping에는 넣지 않는다.
비교용 대체 데이터는 실제 API 자산/업무 동작 증거나 사용자 프리뷰로 보고하지 않는다.
구현 census도 이 캡처에서 함께 수집한다. 같은 시안 예시를 만들 수 없는 case는 G0의
기존 스코프 기록에 이유를 남기고 아래 `--declared-data-case`로 개별 지정한다.

### 3-2: 보고 실행·독립 감사·수리

시작할 때 같은 원본 census와 **현재** foundation `tokens.css`로 위 시트 생성 명령을 다시 실행해 G1·Phase 2의 토큰 등록을 반영한다.

```bash
python TOOL_ROOT/scripts/compare_style_census.py \
  --design BUILD/private/w8/style-census-design.json \
  --impl BUILD/private/w8/style-census-impl.json \
  --mapping BUILD/observations/style-cases.json \
  --sdk-scope BUILD/observations/style-sdk.json \
  --out BUILD/private/w8/style-report.json
# G0에서 데이터 미대조를 선언한 구현 case만: --declared-data-case CASE (반복 가능)
```

SDK 기대값은 비어도 `{}` 파일을 전달한다. SDK case는 표준 route 집합, 기대 파일의
200/304, 전역 존재를 교차 확인한다. SDK가 없는 case의 vendor 로드/route 집합도
미실행이다. schema·루트/틀 크기·글꼴/animation·예산·잘린 페이지 문제를 성공 0건으로
세지 않는다. 빈/중복 mapping과 없는 입력 case도 미실행이다.

출력 `cases`는 짝/영역 수·진단·미짝 텍스트, `groups`는 v4 묶음 id·종류·속성·양쪽 값·
공용 클래스 서명·case·구성원·차단 후보 구성원·대표 사례다. `blocking:true`는 **차단 후보**
표시이며 이번 판은 **후보가 있어도 보고 exit 0**이다. **exit 1은 미실행/입력 오류**로
범위와 이유를 기록한다. CLI는 입력 경로와 출력이 다른지 확인하고 실행 전 이전 report를
지운다. **exit 1 + 새 report 있음**은 일부 case 미실행을 담은 이번 보고이며 나머지 case는
사용할 수 있다. 입력 오류로 새 report가 없으면 미수행이다. 인자 오류도 입출력 경로를
파싱했으면 이전 보고를 지운다(입력과 같은 경로는 보존·거절). 출력 정리 불가를 알린 호출이나
입출력 경로를 확정하지 못한 인자 오류에서는 어떤 report도 읽지 않는다. 예상 밖 도구 결함은 traceback과 **exit 70**으로
구별하며 해당 실행 결과를 사용하지 않는다. 70은 스타일 차단 판정이 아니다.
exit 2/3, 처분 결속 검사, 재렌더, 영향 case 계산, freshness 검사는 없다.

v4의 의미를 유지한다: 색 premultiplied 채널 2/255·alpha 3/255, px 0.5,
기하 1px, opacity 0.02, 텍스트 일치율 0.85. 낮은 일치율은 미선언 case에서 미실행,
G0 선언 case에서 데이터 미대조다. **선언/내용 차이로 모양 속성 후보를 숨기지 않는다**.
가림·무한 animation·읽지 못한 자산 등 기계 한계와 비후보도 기존 시각 감사가 확인한다.
`meta.assets` 바이트 지문이 없는 이미지의 내용 동일성을 파일명 비교만으로 주장하지 않는다.

기존 `discipline-reviewer-web`의 독립 시각 감사에 원본/구현 census·report 경로를 전달한다.
새 감사 회차를 별도로 만들지 않는다. 감사는 실제 원본/구현과 대조해 후보마다 아래
처분을 반환하고 Coordinator가 기존 `visual-check.md`에 보존한다. 혼합 묶음은 해당
구성원 범위를 표시한다. 기계의 `variant` 표시나 내용 차이만으로 D를 결정하지 않는다.

| 처분 | 기존 감사 반환과 후속 처리 |
|---|---|
| T — 실제 스타일 차이 | 원본 대비 실제 결함·수리 부품/원인과 관련 묶음 id. coder가 G2 전에 고치고 기존 절차로 재확인한다 |
| D — 데이터가 만든 정상 차이 | 어느 데이터가 다른지(양쪽 값/출처) → 실제 분기·variant → 해당 스타일 값의 인과 근거. 시안 예시 값으로 업무 동작/스타일을 **고치지 않는다** |
| F — 도구 오탐 | 원본/구현에 실제 차이가 없다는 한 줄 근거 |
| H — 사람 확인 | 기계 한계의 한 줄 이유와 직접 확인 결과(미확인이면 그대로). 확인 못 한 범위는 기존 미검증 규율을 따른다 |

공용 클래스 서명이 여러 case에 걸친 같은 원인의 T는 **부품 단위 수리 1건**으로 묶는다.
공용 부품에 원본 variant가 없으면 공용 variant 추가를 기본으로 하고 기존 호출의 기본값은
보존한다. 기본값 변경은 사용자 결정과 영향 화면 목록을 따른다. 소유 슬라이스 밖 수정은
기존 재개봉/설계 반송 경로로 보내며 화면별 지역 수식 클래스를 반복 복제하지 않는다.

### G2와 레인 측정 — 기존 기록에 합류

G2 배너에 항상 한 행을 둔다: **`W8 보고: 후보 N · T 수리 a · D b · F c · H d · 미대조 case k`**.
N은 해당 보고의 후보 묶음 수, a는 고친 부품/원인 수, b/c/d는 처분 묶음 수다.
T 묶음 수와 수리 수는 다르며 혼합 처분은 겹쳐 셀 수 있으므로 합산 등식으로 검증하지 않는다.
k는 미실행·데이터 미대조 및 요구 case 중 비교 mapping 밖인 것의 중복 없는 합이며 이유를
함께 적는다. W8 자체를 수행하지 못했으면 숫자 0 대신 `W8 보고: 미수행 — 사유`다.
기존 모든 검사와 발주자 대조는 유지한다.

새 의무 문서를 만들지 않고 `visual-check.md`의 회차 기록에 다음을 붙인다.
첫 보고의 JSON과 처분은 재실행으로 덮어 잃지 않게 회차 이름/기존 기록으로 보존한다.

| 측정 | 남길 값 |
|---|---|
| 첫 3-1 뒤 보고 | T/D/F/H **묶음 수**, 처분 시작/끝과 소요 분, report 경로 |
| 첫 제출 | 시트 사용 여부·경로, 첫 제출 T 묶음 수(과거 P1 35는 참고 기준선) |
| G2 시각 반송 | 회차별 시작/끝·사유·소요 분; 가능한 경우 레인/발주자 시간을 구별 |
| 놓침 | 발주자가 먼저 판정한 항목 중 W8 비교 case에 있었지만 첫 보고에 없던 항목 수·대응 case |
| 레인 벽시계 | G0 시작·G2 종료 시각 및 경과 분. 종료 전에는 진행 중 |

아직 발주자 판정/시간 근거가 없으면 `미측정`으로 남겨 0과 구별한다. 발주자가 먼저
판정하고 나중에 보고를 여는 것은 운영 절차다. 플러그인이 별도 봉인 관문을 만들거나
발주자의 전수 대조를 줄이지 않는다. 1~2 레인 실측 뒤의 차단/입력 결속/대조 축소는
이번 판 밖의 사용자 결정이다.
