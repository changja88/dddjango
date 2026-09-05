# 플러그인 작업 요청 가이드 재설계 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 사용자가 제품 결과와 접근 불가능한 외부 사실만 전달하고, 조사·설계·agent/skill·구현·테스트·검증 방법은 플러그인에 맡기도록 두 작업 요청 가이드를 재설계한다.

**Architecture:** `dddjango/REQUEST_GUIDE.md`와 `dddjango-web/REQUEST_GUIDE.md`가 각각 하나의 논리 문서 정본이며 Codex 설치본은 byte mirror다. 핵심 요청에는 사용자만 결정할 수 있는 외부 결과만 두고, 조사 가속 자료는 선택 입력, 내부 절차는 “플러그인이 하는 일”, 운영 한계는 짧은 후반 참고로 분리한다. 기존 runtime prompt·ontology·reference corpus는 변경하지 않는다.

**Tech Stack:** Markdown, JSON plugin manifests, Python 표준 라이브러리 검증기, GNU Make

**Spec:** `workspace/design/2026-09-05-plugin-request-guides-spec.md`

## Global Constraints

- 최종 사용자 문서는 플러그인별 한 개다. 선택 참고와 후반 안내도 각 `REQUEST_GUIDE.md` 안에 둔다.
- 정본은 `dddjango/REQUEST_GUIDE.md`, `dddjango-web/REQUEST_GUIDE.md`이고 각 `codex-*` 파일은 byte 동일 미러다.
- 각 가이드 도입부에는 설치된 `REQUEST_GUIDE.md`가 해당 runtime의 권위 있는 가이드라는 기존 배포 계약 문구를 유지한다.
- 핵심 요청에는 사용자가 원하는 외부 결과, 이미 정한 필수 규칙, 보존·변경·제외 범위만 둔다.
- 관련 코드·문서·테스트·OpenAPI·asset 위치는 알고 있을 때만 주는 선택 입력이다. 사용자가 자료의 권위·coverage·영향 범위를 분석하게 하지 않는다.
- agent·skill 선택, 아키텍처, 테스트 전략, gate, 내부 상태 토큰, source capability 분류, 측정·재개 절차는 사용자가 지시하지 않는다.
- 복사 가능한 요청 블록에는 `G0`, `G1`, `G1′`, `G2`, `pending`, `build_anchor`, `pre-gate`, `registry`, `slice`, `refreeze`, `재절단`, `재개봉`, `DIFF` 실행 지시를 넣지 않는다.
- `dddjango`는 업무 변화·불변식·실패 결과·보존할 외부 동작을 강조하고 DDD 배치와 테스트 설계는 맡긴다.
- `dddjango-web`은 기준 시안의 정확한 대상·필수 상태와 폭·의도적 차이를 강조하고 시안 분석·검증 방법·MVVM/HTMX 구조는 맡긴다.
- 시안 없음, 시안 접근 불가, API 위치 미확정은 모두 합법적인 시작 상태다. 플러그인이 조사하고 필요한 사용자 결정을 질문한다.
- `dddjango/commands`, `dddjango/agents`, `dddjango/skills`, `codex-dddjango/skills`, `dddjango-web/commands`, `dddjango-web/agents`, `dddjango-web/skills`, `codex-dddjango-web/skills`, `ontology/`와 reference corpus는 수정하지 않는다.
- 기존 guide 배포 위치·homepage·repository·byte mirror·검증기 계약은 유지한다. 새 의미 검증기를 만들지 않는다.

---

### Task 1: 설계 기준선 교정

**Files:**

- Modify: `workspace/design/2026-09-05-plugin-request-guides-spec.md`
- Modify: `workspace/plan/2026-09-05-plugin-request-guides-plan.md`
- Add: `workspace/plan/2026-09-05-plugin-request-guides-revision-plan.md`

**Interfaces:**

- Consumes: 2026-09-05 적대적 리뷰의 A=사용자 고유 정보, B=선택 가속 정보, C=플러그인 소유, D=운영 설명, E=삭제 후보 분류.
- Produces: Tasks 2~4가 따를 현재 가이드 정보 구조와 수용 기준.

- [ ] **Step 1: 설계 명세의 목적과 정보 분류를 교정한다**

  다음 원칙을 명세의 현재 기준선으로 만든다.

  - `A`만 최소 요청에 둔다. A도 최초 요청에서 모두 확정할 필요는 없다.
  - `B`는 “있으면 함께 주기”로 분리한다.
  - `C`는 플러그인이 조사·제안·결정하는 내용으로 설명한다.
  - `D`는 발주 입력과 분리된 짧은 후반 참고다.
  - `E`는 가이드에서 제거한다.

- [ ] **Step 2: 두 가이드의 새 목차와 최소 요청 계약을 명세한다**

  공통 골격은 `사용 범위 → 바로 시작 → 알려 주면 좋은 제품 정보 → 플러그인이 하는 일 → 조건부 선택 정보 → 수정·재개 → 짧은 완료 참고`다. backend와 web의 전문성은 Global Constraints대로 다르게 둔다.

- [ ] **Step 3: 배포·정본·미러·검증 계약을 보존한다**

  기존 파일 위치, manifest homepage, Codex websiteURL, README 링크, byte mirror, `request_guide_contract.py` 책임은 바꾸지 않는다.

- [ ] **Step 4: 기존 구현 계획을 역사 문서로 표시한다**

  기존 계획 상단에 이 계획으로 대체되었으며 기존 내용의 gate·evidence·검수 행렬 요구를 현재 수용 기준으로 사용하지 않는다는 짧은 고지를 추가한다. 과거 실행 기록 본문은 재작성하지 않는다.

- [ ] **Step 5: 정적 자기 검토를 실행한다**

  Run:

  ```bash
  git diff --check
  rg -n '상태: 구현 기준선|A — 사용자|B — 선택|C — 플러그인|E — 삭제' workspace/design/2026-09-05-plugin-request-guides-spec.md
  rg -n '대체|revision-plan' workspace/plan/2026-09-05-plugin-request-guides-plan.md
  ```

  Expected: whitespace 오류가 없고 새 분류·대체 고지가 존재한다.

- [ ] **Step 6: 변경을 커밋한다**

  ```bash
  git add workspace/design/2026-09-05-plugin-request-guides-spec.md workspace/plan/2026-09-05-plugin-request-guides-plan.md workspace/plan/2026-09-05-plugin-request-guides-revision-plan.md
  git commit -m "docs: 작업 요청 가이드 기준선 재설계"
  ```

### Task 2: dddjango 작업 요청 가이드 재작성

**Files:**

- Modify: `dddjango/REQUEST_GUIDE.md`
- Modify: `codex-dddjango/REQUEST_GUIDE.md`

**Interfaces:**

- Consumes: Task 1의 A/B/C/D/E 정보 구조와 dddjango 전문성 계약.
- Produces: 업무 결과 중심의 단일 dddjango 사용자 가이드와 byte mirror.

- [ ] **Step 1: 도입과 바로 시작을 작성한다**

  기존 Django 프로젝트의 한 기능이 대상임을 밝히고 Claude `/dddjango`와 Codex 자연어 호출 예시를 제공한다. 한 기능과 원하는 변화만으로 시작할 수 있고 플러그인이 조사·질문한다는 약속을 최소 템플릿 바로 뒤에 둔다.

- [ ] **Step 2: 최소 요청을 네 판단 이내로 줄인다**

  최소 요청은 기능·대표 성공 결과·이미 정한 핵심 업무 규칙과 실패 결과·보존/변경/제외 범위만 포함한다. 업무 행위자와 목적은 결과가 달라질 때만 선택적으로 적게 한다. 규칙 개수, evidence, 기존 영역 소유권, coverage, 내부 gate를 요구하지 않는다.

- [ ] **Step 3: 선택 정보와 플러그인 소유를 분리한다**

  관련 자료 위치, 경계 사례, 동시성, 외부 효과, 호환 변경은 해당할 때만 주는 선택 정보로 둔다. BC·aggregate·repository·API/DB 구현 수단·테스트 구조와 수량·agent/skill·검증 절차는 플러그인이 결정한다고 평이하게 쓴다.

- [ ] **Step 4: 수정·재개와 완료 참고를 압축한다**

  재개 시 사용자는 이전 작업이라는 사실, 바꿀 결과, 보존할 동작, 세션 밖에서 바뀐 외부 사실만 알리도록 한다. `pending`, `build_anchor`, 입장표 decision, pre-gate, registry 상세는 제거한다. 완료 참고는 구현한 업무 사례, 실행한 검증, 남은 미확정만 확인하도록 쓴다.

- [ ] **Step 5: 정본을 byte mirror로 동기화하고 검증한다**

  Run:

  ```bash
  cp dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
  cmp -s dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
  git diff --check
  python3 workspace/tools/request_guide_contract.py
  ```

  Expected: byte mirror와 배포 계약이 green이다.

- [ ] **Step 6: 변경을 커밋한다**

  ```bash
  git add dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
  git commit -m "docs: dddjango 요청 가이드를 결과 중심으로 개편"
  ```

### Task 3: dddjango-web 작업 요청 가이드 재작성

**Files:**

- Modify: `dddjango-web/REQUEST_GUIDE.md`
- Modify: `codex-dddjango-web/REQUEST_GUIDE.md`

**Interfaces:**

- Consumes: Task 1의 A/B/C/D/E 정보 구조와 dddjango-web 충실도·코드 품질 계약.
- Produces: 시안 대상과 외부 결과 중심의 단일 dddjango-web 사용자 가이드와 byte mirror.

- [ ] **Step 1: 도입과 세 정상 시작 경로를 작성한다**

  시안 있음, 시안 없음, 시안 접근 불가를 모두 정상 입력으로 보여 준다. Claude `/dddjango-web`과 Codex 자연어 호출 예시는 대상 화면과 디자인 위치만으로 완결되게 한다.

- [ ] **Step 2: 최소 요청을 다섯 판단 이내로 줄인다**

  화면·기준 시안과 정확한 대상·반드시 맞아야 할 상태/폭/동작·의도적 차이·데이터 연동 의도만 둔다. OS/browser/zoom/DPR, source capability 분류, 검수자, 완료 행렬, asset/font 전수 준비를 요구하지 않는다.

- [ ] **Step 3: 충실도를 높이는 선택 자료와 플러그인 소유를 분리한다**

  상태별 시안, 동작 영상, 별도 asset/font, 대표 데이터, OpenAPI 위치, 인증·접근 제약은 있을 때만 주는 자료다. 시안 채널 판정·동결/추출·폰트/asset 조사·상태 및 검증 계획 구성·API 계약 분석·MVVM/HTMX/HTML/CSS 구조는 플러그인이 맡는다고 쓴다.

- [ ] **Step 4: 수정·재개와 완료 참고를 압축한다**

  사용자는 바뀐 화면 결과와 새 디자인/API 위치만 전달한다. refreeze, G1′, contract 재절단, slice 재개봉, trivial 판정과 검사 exit 상세를 제거한다. 자동 측정과 최종 시각 확인의 차이는 발주 필드가 아니라 짧은 결과 해석으로만 남긴다.

- [ ] **Step 5: 정본을 byte mirror로 동기화하고 검증한다**

  Run:

  ```bash
  cp dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
  cmp -s dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
  git diff --check
  python3 workspace/tools/request_guide_contract.py
  ```

  Expected: byte mirror와 배포 계약이 green이다.

- [ ] **Step 6: 변경을 커밋한다**

  ```bash
  git add dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
  git commit -m "docs: dddjango-web 요청 가이드를 시안 중심으로 개편"
  ```

### Task 4: 진입 문서와 추천 프롬프트 정합화

**Files:**

- Modify: `README.md`
- Modify if needed: `codex-dddjango/.codex-plugin/plugin.json`
- Modify if needed: `codex-dddjango-web/.codex-plugin/plugin.json`

**Interfaces:**

- Consumes: Tasks 2~3의 최종 사용자 언어와 최소 요청 계약.
- Produces: 저장소 진입표와 설치 UI 추천 prompt가 가이드와 충돌하지 않는 상태.

- [ ] **Step 1: README 비교표를 선택 정보 구조로 고친다**

  dddjango는 원하는 업무 변화·핵심 규칙·보존할 동작·범위를, web은 대상 화면·기준 시안·필수 상태/폭·의도적 차이를 핵심으로 설명한다. 자료 위치는 알고 있을 때만 주며 한 기능 또는 한 화면만으로 시작할 수 있다고 쓴다.

- [ ] **Step 2: Codex defaultPrompt를 같은 원칙으로 점검한다**

  내부 gate·검증·재개 절차를 지시하는 prompt가 있으면 결과 중심으로 고친다. dddjango는 실패 후 보존 상태와 기존 동작, web은 정확한 시안 대상과 필요한 상태·폭을 보여 주는 예시를 유지한다. 시안 없음과 접근 불가도 합법적인 예시로 남긴다.

- [ ] **Step 3: 배포 계약과 전체 검증을 실행한다**

  Run:

  ```bash
  python3 workspace/tools/request_guide_contract.py --self-test
  python3 workspace/tools/request_guide_contract.py
  cmp -s dddjango/REQUEST_GUIDE.md codex-dddjango/REQUEST_GUIDE.md
  cmp -s dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
  git diff --check
  make verify
  ```

  Expected: self-test, 실제 배포 계약, 두 byte mirror와 `make verify` 6개 계열이 모두 green이다.

- [ ] **Step 4: 변경을 커밋한다**

  ```bash
  git add README.md codex-dddjango/.codex-plugin/plugin.json codex-dddjango-web/.codex-plugin/plugin.json
  git commit -m "docs: 요청 가이드 진입 프롬프트 정합화"
  ```

## 최종 품질 게이트

- 서로 독립적인 dddjango runtime reviewer, dddjango-web runtime reviewer, 인간요인 reviewer가 각 가이드의 모든 사용자-facing 필드를 A/B/C/D/E로 다시 분류한다.
- 복사 블록에 C/E가 있거나 A와 B가 필수처럼 섞였으면 해당 가이드 작업으로 반송한다.
- 최소 기능, 복잡한 backend, 시안 있음, 시안 없음·접근 불가, 기존 작업 재개의 다섯 시나리오에서 요청문이 내부 절차를 지시하지 않고 필요한 외부 결과만 전달하는지 확인한다.
- 최종 whole-branch reviewer는 runtime·ontology·reference corpus가 변경되지 않았는지와 설계 명세·가이드·README·추천 prompt의 일관성을 검토한다.
- 모든 리뷰 반영 후 `make verify`를 새로 실행하고 결과를 직접 확인한다.
