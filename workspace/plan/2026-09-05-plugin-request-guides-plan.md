# dddjango · dddjango-web 작업 요청 가이드 구현 계획

> 설계 기준선: `workspace/design/2026-09-05-plugin-request-guides-spec.md`
>
> 실행 방식: 한 번에 한 구현자만 순차적으로 정본을 편집하고, 별도 검토자가 각 작업의 명세 준수와
> 품질을 승인한다. 각 단계의 검증이 실패하면 그 단계 안에서 고친 뒤 다음 단계로 이동한다.

**목표:** 두 플러그인의 강점을 살리는 작업 요청 가이드를 각 설치본에 포함하고, 진입 문서와
추천 prompt를 일치시키며, Claude/Codex 미러 drift를 영구 검증한다.

**문서 아키텍처:** Claude 설치본의 `REQUEST_GUIDE.md` 두 개가 정본이고 Codex 설치본의 같은 파일은
byte mirror다. 루트 README는 발견과 비교만 담당하고, `docs/DEVELOPMENT.md`와 Makefile이 소유권과
검증 규칙을 담당한다. 런타임 prompt·ontology는 변경하지 않는다.

**품질 원칙:** 사용자는 사실·결과·증거·미확정을 주고, 플러그인은 내부 설계를 판단한다.
`dddjango`는 불변식·실패 원자성·현행 계약·테스트 오라클을, `dddjango-web`은 시안 정본·상태·폭·
interaction·asset·실물 API·육안 비교를 우선한다.

---

## Task 1: 설계와 계획의 구현 가능성 적대 검토

**검토 대상:**

- `workspace/design/2026-09-05-plugin-request-guides-spec.md`
- `workspace/plan/2026-09-05-plugin-request-guides-plan.md`
- 관련 runtime command·agent·skill·script·manifest·Makefile

**Step 1: 독립 검토자 세 명을 병렬로 배정한다**

- dddjango runtime 사실 검토: 가이드 설계가 실제 G0/G1/G2, DDD/TDD, 계약·DB 조건과 충돌하는지 확인
- dddjango-web 충실도 검토: 시안 입력·OpenAPI·상태·render audit·재개 흐름과 자동화 한계를 확인
- 패키징/초보 사용자 검토: 설치본 포함, 링크, 정본·미러, 진입 경로, 계획 누락을 확인

각 검토자는 `BLOCKER / MAJOR / MINOR`와 파일·근거를 제시하고, 승인 또는 수정 후 승인 판정을 낸다.

**Step 2: 판정을 통합한다**

- 동일 사안을 중복 제거한다.
- runtime 근거와 충돌하는 설계는 설계 문서에서 고친다.
- 구현 상세 누락은 이 계획에서 고친다.
- 사용자 요청 범위 밖 runtime 결함은 잔여 위험으로 남기고 구현 범위에 몰래 포함하지 않는다.

**Step 3: 정적 검증 후 기준선을 커밋한다**

현재가 `main`이면 plugin payload를 바꾸기 전에 `git switch -c docs/request-guides`로 feature branch를
만든다. 이미 그 branch라면 그대로 진행한다.

Run:

```bash
set -euo pipefail
test "$(git branch --show-current)" = "docs/request-guides"
git diff --check
if rg -n 'TO[D]O|TB[D]|추후[ ]결정' workspace/design/2026-09-05-plugin-request-guides-spec.md workspace/plan/2026-09-05-plugin-request-guides-plan.md; then exit 1; fi
```

Expected: whitespace 오류 없음. 미결정 placeholder 없음.

Commit:

```bash
git add workspace/design/2026-09-05-plugin-request-guides-spec.md workspace/plan/2026-09-05-plugin-request-guides-plan.md
git commit -m "docs: 작업 요청 가이드 구현 계획 검증"
```

## Task 2: dddjango 작업 요청 가이드 작성

**Files:**

- Create: `dddjango/REQUEST_GUIDE.md`
- Create: `codex-dddjango/REQUEST_GUIDE.md`

**Step 1: 정본에 사용 경계와 빠른 시작을 쓴다**

- 기존 Django 프로젝트의 한 기능에 쓰는 도구임을 명시한다.
- 파일 상단에 설치본의 이 사본이 해당 runtime에 대한 권위 있는 가이드이고 manifest homepage는
  latest-online 발견 경로라고 명시한다.
- 화면 구현은 `dddjango-web`, 프로젝트 bootstrap이나 막연한 전면 재설계는 대상이 아님을 밝힌다.
- Claude `/dddjango ...`와 Codex `dddjango를 사용해 ...` 시작 예시를 함께 둔다.
- 긴 작업에서 질문과 승인 게이트가 사라지지 않는다고 명시한다.

**Step 2: 최소·권장 요청 템플릿을 쓴다**

- 30초 템플릿: 사용자/목적, 시작 행동, 성공 상태, 핵심 규칙, 실패 상태, 보존 계약, 핵심 용어·
  사실 소유 영역, evidence, 범위, 미확정
- 권장 템플릿: 상태 전이, 경계값, 원자성, retry/duplicate/concurrency, 도메인 언어·소유권,
  즉시·지연 외부 효과, 제품 계약, 조사 evidence·기존 coverage, 필수 제약·선호·미확정
- 승인된 제품 계약과 기존 코드·테스트를 같은 것으로 취급하지 않는다. 계약의 종료·약화에는
  support 종료·rollout·저장 데이터·발행 이벤트 처리 근거를 받는다.
- 빈칸을 거짓으로 채우지 않게 조건부 항목에는 `해당 없음` 또는 `미확정`을 허용한다.

**Step 3: 설계자에게 맡길 결정을 쓴다**

- aggregate/BC/class/filetree/repository/port, 구체 락, 유행 패턴, 테스트 수·coverage quota를 정답처럼
  지시하지 않는다.
- 실제 환경 제약이면 이유와 관찰 가능한 완료 조건을 제공한다.

**Step 4: 위험별 보충과 게이트 검토법을 쓴다**

- API: 소비자, method/path, request/response/error, compatibility
- DB·동시성: 불변식, 경쟁 상황, duplicate/retry 결과, 원자성
- 외부 연동: 응답 전에 끝나야 할 효과, 지연 허용 효과, 실패·재시도·중복·event consumer 결과
- brownfield: 보존할 실제 계약과 evidence path
- 신규·변경 API 오류 shape의 초기 요청은 승인 자체가 아니며 별도 명시 승인될 수 있음을 알린다.
- G0에서 lens, 기존 기능 폴더, 새/기존 영역 배치, 선행 위반 정리·연기 결정을 확인한다.
- G1에서 규칙·소유권·계약과 테스트 입장표의 근거·고유 failure·중복·`pending=0`을 확인한다.
- G2에서 구현·회귀뿐 아니라 pre-gate, registry, 테스트 green이 각각 증명하지 못하는 범위를 설명한다.

**Step 5: 수정·재개와 예시를 쓴다**

- 수정은 바뀔 규칙과 보존할 계약을 나눈다.
- 재개 요청자는 `.dddjango/...` 폴더와 마지막 승인 위치, 이후 코드·스키마·dependency·merge,
  expected result·지원 계약·move/split/rename/remove/weaken 변경을 알려 준다.
- Coordinator가 기존 폴더의 `build_anchor`를 읽어 유지하며, 사용자에게 새 anchor를 선택·제공하게
  하지 않는다.
- 마지막 승인은 탐색 힌트일 뿐 재사용 허가가 아니며, Coordinator가 현행 design-spec·contract evidence·
  관련 test admission을 다시 확인해 G1′ 생략 여부를 정한다고 명시한다.
- 나쁜 요청→좋은 요청 예시를 최소 네 종류 넣는다.

**Step 6: Codex mirror를 만들고 내용 계약을 검사한다**

정본을 `apply_patch`로 만든 뒤 같은 patch로 mirror를 만든다. 그 뒤:

```bash
set -euo pipefail
cmp -s dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
rg -q "설치된.*권위 있는" dddjango/REQUEST_GUIDE.md
rg -q "실패.*그대로" dddjango/REQUEST_GUIDE.md
rg -q "미확정" dddjango/REQUEST_GUIDE.md
rg -q "도메인 언어" dddjango/REQUEST_GUIDE.md
rg -q "사실.*소유" dddjango/REQUEST_GUIDE.md
rg -q "제품 계약" dddjango/REQUEST_GUIDE.md
rg -q "기존 coverage" dddjango/REQUEST_GUIDE.md
rg -q "G0" dddjango/REQUEST_GUIDE.md
rg -q "G1" dddjango/REQUEST_GUIDE.md
rg -q "G2" dddjango/REQUEST_GUIDE.md
rg -q "pending" dddjango/REQUEST_GUIDE.md
rg -q "귀속" dddjango/REQUEST_GUIDE.md
rg -q "legacy" dddjango/REQUEST_GUIDE.md
rg -q "동시" dddjango/REQUEST_GUIDE.md
rg -q "저장소 전체.*아니" dddjango/REQUEST_GUIDE.md
! rg -n "^(질문 없이 끝낸다|승인 없이 진행한다|테스트 (100개|100%)를 보장한다|저장소 전체가 clean(이다|입니다))[.!]?$" dddjango/REQUEST_GUIDE.md
```

Expected: `cmp` 성공, 필수 신호 존재, 긍정형 과장 단정 없음.

Commit:

```bash
git add dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
git commit -m "docs: dddjango 작업 요청 가이드 추가"
```

## Task 3: dddjango-web 작업 요청 가이드 작성

**Files:**

- Create: `dddjango-web/REQUEST_GUIDE.md`
- Create: `codex-dddjango-web/REQUEST_GUIDE.md`

**Step 1: 사용 경계와 충실도의 운영 정의를 쓴다**

- web 표현계층 화면용이며 backend 기능을 구현하지 않는다고 명시한다.
- 파일 상단에 설치본의 이 사본이 해당 runtime에 대한 권위 있는 가이드이고 manifest homepage는
  latest-online 발견 경로라고 명시한다.
- 구현 완료, 자동 측정 완료, 시각 수용 완료를 분리한다.
- 시각 수용 완료는 승인한 state×viewport 행렬의 전체 스크롤·동작을 사람이 비교했을 때만 쓴다.
- 필수 행렬이 남으면 `충실도 미검증` 또는 `조건부 인계`로 표시한다.

**Step 2: 디자인 증거 준비법을 쓴다**

- Claude Design `.dc.html`, live reference page, local/static reference HTML, screenshot/image-only,
  no-design을 구분하고 동결·추출과 render audit 능력을 별도 표로 둔다.
- `.dc.html`은 DesignSync·token/meta/image·동봉 PNG를 쓸 수 있지만 원본 브라우저 audit은 불가하다.
- live/local HTML은 브라우저 실행·접근 조건이 맞을 때만 audit할 수 있다.
- 정확한 screen/frame/route, 증거 우선순위, 의도적 차이, 접근 가능 여부를 요구한다.
- 시안이 있으나 접근 불가한 경우를 no-design으로 처리하지 않게 한다.
- screenshot/image-only는 수동 증거이고 현재 자동 동결·token·render audit의 일급 채널이 아님을 알린다.

**Step 3: 최소·권장 요청 템플릿을 쓴다**

- 30초 템플릿: 화면, 디자인 정본과 자동·수동 증거 구분, 검수 환경·viewport, 필수 상태·interaction,
  asset/font, API, 허용 차이, 검수자
- 권장 템플릿: route/navigation, OS·browser/version·zoom·DPR·locale/theme/reduced-motion, 폭별 반응,
  상태표와 full URL·role·fixture/seed·loading/error 유발·ready 조건, motion/pinned, 대표 데이터,
  OpenAPI 3.x JSON, state×viewport×evidence×재현×검수자×자동·육안 완료 행렬
- DOM/CSS/내부 view model 설계를 요구 필드에 넣지 않는다.

**Step 4: backend handoff와 재개 흐름을 쓴다**

- endpoint 부재, 계약 충돌, backend 업무 규칙이 필요한 경우 `dddjango`가 먼저임을 명시한다.
- OpenAPI는 비대화형 fetch 가능한 OpenAPI 3.x JSON URL·로컬 파일만 받으며 YAML·Swagger 2.0은
  사전 변환한다고 명시한다. 문서와 실제 응답의 일치는 자동 증명되지 않는다.
- backend 완료 후 기존 `.dddjango-web/.../build-state.json` 폴더, 마지막 승인, 이전·신규 OpenAPI,
  변경 method/path/shape, 완료 slice의 영향 후보를 알린다.
- 자동 stale 감지를 약속하지 않고 G0 refreeze → 필요 시 G1′ → contract 재절단 → 영향 slice 명시
  재개봉을 요청하게 한다.
- project wiring과 backend feature의 차이를 설명한다.

**Step 5: 최종 육안 검토와 자동화 한계를 쓴다**

- full scroll, 폭·상태, typography/color/spacing/layout, hover/focus/loading/swap, motion/pinned을 사람이 확인
- render audit를 DIFF/exit 2 / warn·info / 수집만 / 미수집·수동 표로 나눈다. comparator DIFF는
  G2 판단 자료이지 구조 백스톱처럼 자동 차단하는 결과가 아님을 명시한다.
- 단일 현재 상태·단일 viewport pair, text 200·pinned 20 상한, 미조인 비차단, 폭 mismatch warn-only,
  높이·font family·정확 간격·image/background·border/radius/shadow·실제 motion·pinned anchor 미비교를 명시한다.
- query/hash 제거, lazy/scroll 상태 누락 가능성, image fetch의 CSS background/srcset/dynamic 한계를 적는다.
- 자동 결과 green과 시각 완료를 동일시하지 않는다.
- browser·functional·accessibility 자동 테스트를 새로 작성하지 않는다고 알린다.
- HTML/CSS 직수입은 설계 선택이 아니라 금지이며, custom JS가 필요한 gesture/parallax는 한계·범위 조정
  대상이라고 알린다.

**Step 6: 예시와 mirror 계약을 검사한다**

- screenshot 한 장만 준 요청, inaccessible URL, desktop-only, missing API, 내부 HTML/CSS 지시,
  기존 화면 수정·trivial 수정 사례를 포함한다.

Run:

```bash
set -euo pipefail
cmp -s dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
rg -q "설치된.*권위 있는" dddjango-web/REQUEST_GUIDE.md
rg -q "exact screen" dddjango-web/REQUEST_GUIDE.md
rg -q "viewport" dddjango-web/REQUEST_GUIDE.md
rg -q "상태 재현" dddjango-web/REQUEST_GUIDE.md
rg -q "OpenAPI 3.x JSON" dddjango-web/REQUEST_GUIDE.md
rg -q "전체 스크롤" dddjango-web/REQUEST_GUIDE.md
rg -q "충실도 미검증" dddjango-web/REQUEST_GUIDE.md
rg -q "build-state.json" dddjango-web/REQUEST_GUIDE.md
rg -q "DIFF / exit 2" dddjango-web/REQUEST_GUIDE.md
rg -q "text 200" dddjango-web/REQUEST_GUIDE.md
rg -q "dddjango" dddjango-web/REQUEST_GUIDE.md
! rg -n "^(픽셀 동일을 보장한다|모든 상태를 자동 검증한다|원본 HTML/CSS를 복사한다|백스톱 검사 24종)[.!]?$" dddjango-web/REQUEST_GUIDE.md
```

Expected: byte 동일, 필수 신호 존재, 과장·낡은 사실 없음.

Commit:

```bash
git add dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
git commit -m "docs: dddjango-web 작업 요청 가이드 추가"
```

## Task 4: README 진입면과 실제 동작의 정합성 수정

**Files:**

- Modify: `README.md`

**Step 1: 첫 화면과 플랫폼 표현을 고친다**

- Claude Code 전용 제목을 Claude Code·Codex 지원으로 바꾼다.
- 설치 다음, 빠른 시작 앞에 `작업 요청 가이드` 섹션을 둔다.
- 두 가이드 링크, 각 플러그인에 줘야 하는 핵심 입력, 서로 넘기는 조건을 짧게 설명한다.
- Claude와 Codex의 시작 예시를 나란히 둔다.

**Step 2: 조사에서 확인한 사용자-facing 오류만 고친다**

- Codex list 예시의 고정 과거 version 제거
- 기존 구조 우선의 과도한 문장 수정
- 규율 적용 범위를 승인 스코프의 신규 파일과 기존 파일에 추가·변경하는 코드로 한정하고,
  스코프 밖 기존 배치 이동·개명·재배선을 별도 G0 결정 없이 하지 않는다고 명시
- 부분 수정 G1 skip 조건 한정
- pytest 설정 자동 생성 표현 수정
- web API의 dddjango provenance 제한 제거
- web backstop 24종 숫자 제거
- backstop의 증명 범위 한정

**Step 3: 링크와 잔존 오류를 검사한다**

Run:

```bash
set -euo pipefail
test -f dddjango/REQUEST_GUIDE.md
test -f dddjango-web/REQUEST_GUIDE.md
rg -n "REQUEST_GUIDE|Claude Code|Codex" README.md
! rg -n "1\.0\.5|실물 API 계약만 소비|검사 24종|항상.*pytest.*갖춰" README.md
```

Expected: 링크 대상 존재, 두 플랫폼 발견 가능, 낡은 문구 없음.

Commit:

```bash
git add README.md
git commit -m "docs: 작업 요청 가이드 진입점 정리"
```

## Task 5: 정본·미러 유지보수 규칙과 영구 검증 추가

**Files:**

- Modify: `docs/DEVELOPMENT.md`
- Modify: `Makefile`
- Modify: `workspace/tools/reverse_coverage.py`
- Create: `workspace/tools/request_guide_contract.py`
- Later regenerate: `workspace/eval/ab/T2-0b-manifest.json`

**Step 1: 개발 가이드에 소유권을 기록한다**

- 저장소 지도에 각 `REQUEST_GUIDE.md` 정본·mirror 관계를 추가한다.
- runtime graph corpus와 별개인 사람용 문서임을 밝힌다.
- 수정 순서: Claude 정본 편집 → Codex byte 복사/동일 patch → targeted compare → `make verify`
- 설치본 내부 문서의 source에는 상대 목적지처럼 보이는 구문을 코드·주석·예시에도 넣지 않는
  보수적 규칙을 추가한다. Scheme URI와 `#fragment`는 허용한다.
- 실제 Codex marketplace 경로가 `.agents/plugins/marketplace.json`임을 기록한다.
- `reverse_coverage.py`의 dddjango 설치본 닫힌 분류표에 루트 `REQUEST_GUIDE.md`를 사람용 사용자
  가이드로 등록한다. runtime rule owner인 것처럼 속이지 않는다.

**Step 2: 기존 verify target에 최소 비교를 추가한다**

- `verify-base-core` 끝에 dddjango guide `cmp -s`와 명확한 failure message
- `verify-web` 끝에 web guide `cmp -s`와 명확한 failure message
- 표준 라이브러리 validator는 두 pair, 두 marketplace의 name/path/ref와 subdir 내용,
  네 manifest homepage/repository, 두 Codex websiteURL, guide 상단 권위 문구,
  Codex defaultPrompt 문자열 배열과 plugin 이름을 검사한다.
- README의 `## 작업 요청 가이드` source heading부터 다음 `## ` heading 직전까지
  `[dddjango 작업 요청 가이드](dddjango/REQUEST_GUIDE.md)`와
  `[dddjango-web 작업 요청 가이드](dddjango-web/REQUEST_GUIDE.md)`라는 exact source token을 각각
  한 번 요구한다. 전체 README source에서도 각각 한 번이어야 한다.
- 네 installed guide source에서 Markdown inline/image destination·reference definition destination·
  HTML `href`/`src`처럼 보이는 구문을 검사해 scheme URI·`#fragment` 외 목적지를 거부한다.
  Code span·fence·HTML comment·escape·예시를 예외로 두지 않는다.
- 링크 검사는 canonical source surface의 drift backstop이다. CommonMark 문맥이나 실제
  rendered/clickable 동작, 렌더러 등가성을 증명하지 않는다. README의 코드·주석 안 exact token도
  source count에 포함하며 실제 표시와 가독성은 문서 검토로 확인한다.
- `--self-test`의 정상 README fixture를 실제 `## 작업 요청 가이드` → `## 업데이트` 구조로 맞춘다.
  Production 변경 전에 같은 path의 잘못된 label, 섹션 밖 token 이동, 코드·주석·중첩 상대 목적지 변이가
  기대 오류 없이 통과하는 RED를 관찰한다. 구현 뒤에는 `validate` 결과를 literal 기대값과 대조하여
  이 거부 동작과 inline/image/reference/HTML의 scheme URI·fragment 허용을 확인한다.
- Mirror drift, guide 누락, marketplace path/ref 오염, subdir manifest 누락, homepage/repository 혼동,
  websiteURL 오염, guide 권위 문구 삭제, defaultPrompt 잘못된 타입·빈 문자열·plugin 이름 누락의
  독립 변이 검출력은 유지한다.
- 네트워크 접근이나 공개 URL 생존성 검사는 하지 않는다.
- `verify-base-core`에서 validator `--self-test`와 실제 저장소 검사를, `verify-web`에서 실제 저장소
  검사를 실행한다. 평상시 `make verify`가 validator의 비공허성과 README·marketplace·homepage·
  defaultPrompt drift를 함께 차단한다.

**Step 3: 봉인에 독립적인 targeted 계약만 실행한다**

Run:

```bash
set -euo pipefail
cmp -s dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
cmp -s dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
python3 workspace/tools/request_guide_contract.py --self-test
python3 workspace/tools/reverse_coverage.py
```

Expected: 두 pair green, 모든 self-test mutation이 검출됨, reverse coverage의 미설명 파일 0.
실제 저장소 전체 request-guide 계약은 homepage가 바뀌는 Task 6에서 처음 실행한다.

주의: `verify-base-core`는 stale draft manifest를 검사하므로 Makefile 변경 뒤 Task 8 재발행 전에는
실행하지 않는다. `verify-web`과 전체 verify도 Task 8에서 함께 실행한다.

Commit:

```bash
git add docs/DEVELOPMENT.md Makefile workspace/tools/request_guide_contract.py workspace/tools/reverse_coverage.py
git commit -m "test: 작업 요청 가이드 배포 계약 검증"
```

## Task 6: 설치 후 발견 경로와 Codex 추천 시작 prompt 개선

**Files:**

- Modify: `dddjango/.claude-plugin/plugin.json`
- Modify: `dddjango-web/.claude-plugin/plugin.json`
- Modify: `codex-dddjango/.codex-plugin/plugin.json`
- Modify: `codex-dddjango-web/.codex-plugin/plugin.json`

**Step 1: 네 manifest에 canonical guide 발견 경로를 둔다**

- dddjango homepage와 Codex websiteURL은
  `https://github.com/changja88/dddjango/blob/main/dddjango/REQUEST_GUIDE.md`
- web homepage와 Codex websiteURL은
  `https://github.com/changja88/dddjango/blob/main/dddjango-web/REQUEST_GUIDE.md`
- 네 repository는 `https://github.com/changja88/dddjango`를 유지한다.
- `main` homepage는 latest-online 발견 경로이고 설치본의 `REQUEST_GUIDE.md`가 해당 runtime에 대한
  권위 있는 사본임을 guide 상단에서 명시한다.

**Step 2: dddjango prompt 세 개를 교체한다**

- 상태 전이·불변식·실패 원자성 예시
- brownfield 계약 보존·근거 경로 예시
- 고위험 항목을 `미확정`으로 표시하는 예시

각 문장은 Codex UI에 적절한 길이를 유지하고 완전한 권장 요청서 대신 좋은 첫 문장을 보여 준다.

**Step 3: web prompt 세 개를 교체한다**

- exact design target·viewport·state 예시
- 실물 API·대표 데이터 예시
- 접근 불가·의도적 차이·검수 범위를 명시하는 예시

**Step 4: manifest를 검증한다**

Run:

```bash
set -euo pipefail
python3 -m json.tool codex-dddjango/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool codex-dddjango-web/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool dddjango/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool dddjango-web/.claude-plugin/plugin.json >/dev/null
python3 workspace/tools/request_guide_contract.py
claude plugin validate dddjango --strict
claude plugin validate dddjango-web --strict
```

Expected: JSON parse, guide contract, 두 Claude plugin validation 성공. Codex에는 별도 `plugin validate`
명령을 가정하지 않고 validator가 `defaultPrompt`의 non-empty string array와 plugin 이름을 검사한다.

Commit:

```bash
git add dddjango/.claude-plugin/plugin.json dddjango-web/.claude-plugin/plugin.json \
  codex-dddjango/.codex-plugin/plugin.json codex-dddjango-web/.codex-plugin/plugin.json
git commit -m "docs: 설치본 작업 요청 가이드 연결"
```

## Task 7: 구현 후 독립 품질 검토

**검토 대상:** 전체 worktree diff와 설계 명세

**Step 1: 세 관점으로 병렬 검토한다**

- dddjango 발주자/architect 관점: 템플릿이 설계·테스트 품질을 실제로 높이는지, runtime 사실이 맞는지
- web 디자이너/구현자 관점: 시안 충실도 입력과 visual oracle이 충분하며 코드 내부를 과지시하지 않는지
- 배포/적대적 관점: 네 설치본, 링크, mirror, README·manifest 정합성, 과장·모순·누락 확인

필수 수용표에는 dddjango의 도메인 언어·소유권, 제품 계약/기존 coverage 분리, G0 부채·배치,
G1′ `pending=0`, pre-gate/귀속 green 한계와 web의 screenshot-only 강등, 상태 재현, OpenAPI 3.x JSON,
명시적 slice 재개봉, DIFF/warn/수집/수동 측정표를 각각 포함한다.

각 검토자는 설계 수용 기준별 PASS/FAIL과 `BLOCKER / MAJOR / MINOR` findings를 근거와 함께 낸다.

**Step 2: finding을 처리한다**

- BLOCKER·MAJOR는 모두 수정하거나 설계 비범위라는 명확한 근거를 남긴다.
- MINOR는 사용자 이해나 사실 정확도에 영향을 주면 수정한다.
- 수정 후 해당 targeted 검증을 다시 실행한다.

**Step 3: review 수정분을 커밋하고 clean HEAD를 확인한다**

finding 수정자는 변경한 in-scope 파일만 명시적으로 stage하고 covering 검증을 보고한 뒤
`docs: 작업 요청 가이드 검토 반영` commit을 만든다. 그 뒤:

```bash
set -euo pipefail
test -z "$(git status --porcelain)"
git diff --exit-code HEAD --
```

Expected: 출력 없음. Task 8 draft manifest는 이 clean HEAD에서만 재발행한다.

**Step 4: 계획 준수 diff를 자체 감사한다**

```bash
git diff --name-status fcd4d0d..HEAD
git status --short
git diff --check
```

작업 시작 commit `fcd4d0d` 이후 전체 diff로 확인한다. 변경 파일이 설계 목록에 없으면
필요성을 증명하거나 되돌리지 말고 사용자 변경 여부를 먼저 확인한다.

## Task 8: draft manifest 재발행과 최종 검증

**Files:**

- Regenerate: `workspace/eval/ab/T2-0b-manifest.json`

**Step 1: draft manifest를 마지막으로 재발행한다**

Run:

```bash
python3 workspace/tools/manifest_seal.py --write
```

Expected: Makefile과 기존에 drift한 manifest digest를 포함해 필요한 값이 갱신된다. 이 파일의 status는
draft이고 run-ready seal이 아니며 `sealed_commit`은 재발행 시점의 HEAD를 가리킨다. 생성 diff를 검토한다.

**Step 2: 문서 계약 검사를 한 번에 실행한다**

Run:

```bash
set -euo pipefail
cmp -s dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
cmp -s dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
python3 workspace/tools/request_guide_contract.py
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool dddjango/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool dddjango-web/.claude-plugin/plugin.json >/dev/null
python3 -m json.tool codex-dddjango/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool codex-dddjango-web/.codex-plugin/plugin.json >/dev/null
git diff --check
```

Expected: 전부 exit 0.

**Step 3: 전체 저장소 검증을 실행한다**

Run:

```bash
set -euo pipefail
make verify-base-core
make verify-web
make verify
```

Expected: targeted targets와 모든 병렬 verify target green. RED면 실패 target의 전체 로그를 읽고 동일 단계에서 원인을 고친다.
봉인 대상 파일을 다시 고쳤다면 Step 1부터 반복한다.
로그에서 `verify-base-core`의 validator self-test+실제 검사와 `verify-web`의 실제 검사가 실행됐는지 확인한다.

**Step 4: 변경 범위와 수용 기준을 최종 대조한다**

```bash
set -euo pipefail
test "$(git branch --show-current)" = "docs/request-guides"
git status --short
git diff --stat fcd4d0d
git diff --name-only fcd4d0d
git diff --check fcd4d0d
```

확인 항목:

- 두 논리 가이드/네 물리 파일 존재 및 byte 동일
- README와 manifest homepage에서 발견 가능
- 실제 runtime과 충돌하는 보장 없음
- dddjango 설계·TDD 품질 입력과 web 시안 충실도·코드 품질 입력이 구별됨
- ontology·runtime prompt·rulepack·LEDGER 무변경
- 전체 verify green

**Step 5: draft manifest를 커밋하고 tree 포함을 증명한다**

```bash
set -euo pipefail
git add workspace/eval/ab/T2-0b-manifest.json
git commit -m "chore: 작업 요청 가이드 검증 봉인 갱신"
test "$(git branch --show-current)" = "docs/request-guides"
git cat-file -e HEAD:dddjango/REQUEST_GUIDE.md
git cat-file -e HEAD:codex-dddjango/REQUEST_GUIDE.md
git cat-file -e HEAD:dddjango-web/REQUEST_GUIDE.md
git cat-file -e HEAD:codex-dddjango-web/REQUEST_GUIDE.md
git diff --exit-code HEAD --
test -z "$(git status --porcelain)"
```

커밋 훅이 변경을 만들거나 검증이 RED면 커밋 완료로 간주하지 않고 diff를 검토한 뒤 Step 1~4를 반복한다.
후속 release가 manifest version을 바꾸면 draft manifest도 다시 재발행해야 한다.

## Task 9: 최종 인계

사용자에게 다음만 간결하게 보고한다.

- 두 가이드가 각각 어떤 강점을 강화하는지
- 주요 파일 링크
- README·Codex prompt·mirror 검증에 반영한 내용
- 적대 검토에서 해소한 주요 위험과 별도 범위로 남긴 기존 runtime 불일치
- 실행한 targeted 검증과 `make verify`의 최종 결과
- commit hash
- `docs/request-guides` branch를 단일 plugin release target으로 그대로 push하지 말아야 하는 이유와
  후속 coordinated release 필요성
- Serena: opt-in 표식이 없어 생략
- Graphify: opt-in 그래프가 없어 생략

릴리즈·push는 이번 요청 범위가 아니므로 수행하지 않는다. 두 marketplace가 모두 `main`을 보면서
plugin별 버전·태그는 독립이므로, 이 합본 branch를 단일 plugin release target으로 push하면 다른
plugin의 payload가 이전 버전으로 노출될 수 있다. 후속 작업은 두 버전을 같은 공개 시점에 반영하는
coordinated release 또는 plugin별 landing·release 분리를 먼저 설계한다.
