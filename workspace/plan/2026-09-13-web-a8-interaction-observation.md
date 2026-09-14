# A8 원본 조작 상태 관찰 교정 계획

> 실행: 승인된 1번 문제만 순차 수행한다. 계획과 최종 변경은 독립 적대 검토한다.

**목표:** 요청한 시안 화면에서 클릭·입력 가능한 요소와 조작 후 나타나는 요소를 원본에서 발견·관찰하고, 미관찰 상태가 입력범위 검토에서 통과하지 않도록 한다.

**기준:** dddjango-web 1.1.7 내용으로 복원된 현재 작업 트리. manifest 버전은 미배포 1.1.12 그대로다. 사용자와 합의한 1번 요구가 명세이며, 구현 재현/보더 수정인 2번은 제외한다.

## 기존 실패와 수정 가설

- 실제 A8 build: `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons`.
- 기존 `coverage-review.md`는 화면의 sc-if 분기와 12개 case를 맞춰 통과했다. step1 trace는 폼을 여는 동작까지이며 관계 메뉴 열기·이름 focus는 없다.
- native Coordinator transcript `54754273-a334-4a58-bdd0-88a043c4010c.jsonl:3741`의 reviewer 호출은 sc-if 목록에 대조를 한정하고 pass 예시를 선기입했다. 독립 판단을 요청하면서 발견 범위와 예상 결론을 호출자가 좁혔다.
- 기존 규범은 상태 전수성을 요구하지만, 이미 만든 case 목록 밖의 조작 대상을 발견하는 절차와 반환 자리가 구체적이지 않다.
- 가설: case를 먼저 열거하고 거기에 캡처를 맞추는 흐름을, 실제 원본의 조작 대상→조작 결과/새 대상→case·관찰 증거 연결로 바꾸고, reviewer가 같은 원본에서 별도로 누락을 찾게 하면 이 경로를 막을 수 있다.

## 최소 변경 설계

수정 정본은 두 파일이다. Codex 역할 미러 두 파일도 같은 의미로 반영한다.

1. `dddjango-web/commands/dddjango-web.md` Phase 0 입력 준비: 기존 `visual-check.md` 원본 관찰 부분에 `진입 상태 / 조작 대상·동작 / 실제 결과·새로 드러난 대상 / 관찰 근거 / 연결 case·미관찰 사유`를 연결한다. 원본 렌더와 부품 정의에서 대상을 발견하고, 조작 후 새 대상도 같은 방식으로 확인한다. 화면 분기·기존 case·부품 이름은 발견 대상을 한정하지 않는다. 입력범위 호출은 사실/원본을 전달하고 예상 pass를 쓰지 않는다.
2. `dddjango-web/agents/design-review-web.md` G0 입력범위 모드: 제공 목록을 정답으로 삼지 않고 원본 렌더/정의의 조작 대상을 독립 대조한다. 실제 조작 근거가 없는 대상을 `입력 부족`으로 반환한다. 검토 원문에 발견 대상→관찰/누락→case 연결을 넣는다. 원본에서 필요한 상태를 실제로 만들 수 없으면 사유/해소 조건을 기록하며 전체 pass로 합치지 않는다.
3. mirror: `codex-dddjango-web/skills/dddjango-web/SKILL.md`, `codex-dddjango-web/skills/dddjango-web-design-review-web/SKILL.md`.

범위는 요청된 화면의 실제 조작 대상이다. 요소별 실제 조작 근거를 보존하며 같은 전이를 반복하는 데이터 행은 보고 표에서만 묶는다. disabled와 외부 영향 때문에 실행할 수 없는 대상은 존재·미관찰 사유로 남긴다. 외부 화면/프로젝트 전체, 모든 값 조합을 탐색하지 않는다. 원본 UI에 없는 상태/자산을 만들지 않는다. 기존 JSON 스키마·checker·코더·G2는 변경하지 않는다.

## 실행·검증

- [x] 기존 실패 원문과 동결 원본/trace 대조.
- [x] 독립 계획 적대 리뷰: 여전히 목록 밖 상태를 놓칠 수 있는가, 사용자 지목 없이는 작동하지 않는가, 불필요한 전수 조합/승인/새 파일이 생기는가.
- [x] 평가자가 A8 원본에서 전체 조작 대상·동작·결과 기대 목록을 먼저 고정한다. 실행 역할에는 이 목록·진단·계획·이전 평가 결과를 전달하지 않는다. source 기반 목록과 실제 도구/브라우저 기록으로 발견·조작·전달을 각각 판정한다.
- [x] 실제 A8 원본과 현행 산출물을 사용한 1.1.7 기준 G0 입력범위 역할 실행. 전체 앱을 간소 fixture로 바꾸지 않는다. baseline/candidate는 같은 원본 bytes·요청·기존 관찰·브라우저 조건을 사용한다. 입력 prompt에 드롭다운/focus 정답을 주지 않는다.
- [x] baseline 실패가 실제로 확인된 뒤 최소 정본/미러 수정. baseline부터 통과하면 효과 근거로 세지 않고 기존 실패와 실행 차이를 확인한다.
- [ ] candidate가 원본에서 미관찰 조작 상태를 독립 발견하고, 실제 브라우저에서 드러나는 대상·결과를 확인하며, 기존 누락된 증거를 pass로 승인하지 않는지 확인한다. 보고서만의 선언을 성공으로 세지 않는다.
- [ ] Coordinator 원본 관찰 checkpoint에서 사용자 지목 없이 실제 A8 화면을 조작하고 후속 검토에 전달하는지 확인한다. 구현/DB/기존 A8 build는 수정하지 않는다. 별도 진단 산출 경로만 사용한다.
- [ ] Coordinator가 보완한 실제 A8 증거를 독립 reviewer가 수락하고 기존 inputs 검사를 통과하는 정상 경로를 확인한다. evaluator가 증거를 손수 고쳐 통과시키지 않는다. 판정/증거 보완은 실제 역할이 수행한다.
- [ ] 독립 최종 리뷰: source/실제 도구 기록/관찰과 최종 판정 일치, 다른 역할/2번 수정 혼입 없음, 원래 rollback 및 두 기존 문서 변경 보존.
- [x] `make verify`·미러·diff 검증. 실제 A8 행동 평가와 저장소 검사 통과를 구별한다.

## 실행 경계와 종료 기준

- A8 원본·기존 build·앱은 읽기 전용. 로컬 원본을 실제 브라우저에서 조작하며 변경은 해당 페이지의 임시 메모리 상태에만 발생한다. task 전용 서버·브라우저와 `/tmp/dddjango-web-a8-interactions-20260913/`에 진단 자료를 둔다. 사용자 앱 프로세스/DB/설치 cache를 바꾸지 않는다.
- 새 native 세션은 현재 checkout의 plugin snapshot을 명시 로드한다. 실제 사용 모델·도구·지침 hash·실행 범위를 기록한다. 기존 A8 장기 세션 자체를 재개/주입하지 않는다. 이 한계를 전체 native 파이프라인 성공으로 확대하지 않는다.
- 최근 1.1.11/12에서 되돌린 다른 지침은 재도입하지 않는다. 기존 조사 기록을 지우지 않으며 증거 대용량을 배포 prompt에 넣지 않는다.
- 권한/환경 때문에 실제 원본 관찰을 할 수 없거나, 원본의 동작과 사용자 요구가 충돌하여 선택이 필요하면 해당 사실을 보고한다. 테스트만 통과한 상태로 완료하지 않는다.
- 배포·설치 갱신·2번 구현 수정은 하지 않는다. 커밋은 이번 사용자가 별도로 요청하지 않았으므로 미커밋 유지한다.

## 실행 관찰

- 계획 독립 검토: Important 3건(전체 oracle 사전 고정/실행자 비공개, 보완 후 정상 수락, 항목별 실제 클릭 보존)을 반영한 후 승인. 후속 증분 검토의 disabled 정상 관찰 오차단 1건도 비활성 관찰과 필요한 활성 상태 누락을 구별하도록 반영.
- 평가 oracle: `/tmp/a8-interaction-evaluator-20260913/oracle.json`와 sha256. A8 원본의 30 조작군과 실제 메뉴 데이터(관계 8/시 12/시·도 17/시·군 153)를 고정했다. 독립 값의 곱집합은 요구하지 않는다.
- 1.1.7 native baseline: `/tmp/dddjango-web-a8-interactions-20260913/baseline/review.md`, 원문 호출·실행 인자·도구 기록 동봉. 전체 fail(변형본 empty 캡처/옛 scope/Toast 누락)이나, Select 열림 누락은 native 채택 기록을 근거로 nit로 강등했다. 입력 focus 누락도 필수 보완으로 다루지 않았다. 전체 pass→fail 개선이라고 주장하지 않는다.
- 읽기 전용 native G0 reviewer에 실제 노출된 도구는 Read/Grep/Glob이다(Playwright 서버 연결과 역할 도구 노출은 다름). reviewer는 원본 정의와 Coordinator의 브라우저 기록을 감사하며, 실제 원본 조작은 Coordinator checkpoint에서 평가한다. 새 세션 모델은 CLI 기본 `claude-fable-5-1`; 기존 장기 A8 세션과 동일 모델/컨텍스트라는 주장은 하지 않는다.
- disabled 문구 보완 전 Coordinator 초안 실행 2개는 evaluator가 종료했으며 효능 증거에서 제외한다. 최종 지침 snapshot은 `/tmp/dddjango-web-a8-interactions-20260913/final-plugin/`, 실제 관찰 실행은 `coordinator-final/`이다.

### 행동 평가 후 가설 보완

- 첫 후보 reviewer는 Select·몰라요 누락을 필수 보완으로 잡았지만 이름 focus를 nit, 대칭/복귀/이탈을 관찰 불요로 처리했다. 두 번째 후보는 이름·성별·복귀/이탈까지 미관찰로 잡았으나 역법 프리필 2개와 메모 카운터 표시를 실제 조작 확인으로 잘못 수락했다. 둘 다 전체 관찰 요구의 성공으로 세지 않는다.
- 위 실행은 A8의 옛 sc-if/12 case/pass 선기입 호출을 그대로 재생한 **편향 호출 방어 평가**다. 현재 Coordinator는 예상 판정 선기입을 제거했으므로 정상 조합 평가는 현재 호출 계약으로 별도 수행한다.
- 독립 원인 검토 권고에 따라 기존 역할의 G0/G1 진입·지식 로드·반환 형식을 분리한다. G0는 실제 조작 기록 위치와 결과 근거를 각기 반환하고 종료한다. G1 정체성/architecture-web 적재/명세 점검은 G1에 유지한다. 새 agent·checker·JSON 스키마를 만들지 않는다. G1 문맥 간섭은 가설이며 단일 원인으로 확정하지 않는다.
- Coordinator 실행의 Chrome 시작/도구 cache 오류는 실행 환경 실패로 구별했다. `coordinator-live`는 허용된 전용 Chrome에 Playwright CDP로 연결하여 A8 원본을 실제 렌더·조작하고 있다. 그 외 중단된 환경/초안 실행은 효능 증거에서 제외한다.
- 저장소 `make verify`: 6/6, exit 0, 558초(`/tmp/dddjango-web-a8-interactions-20260913/verify.log`, 상세 `/tmp/djr-verify.CGX8Gh`). 이후 reviewer 역할 분기 변경이 있으므로 최종 관련 검증을 다시 수행한다.

### 현재 정상 호출의 실제 A8 관찰 평가

- G0/G1 분리 후 기존 A8 입력(25b5b078)에 현재 호출 계약으로 실행한 `g0-normal-negative/result.md`는 역법 프리필/메모 표시를 실제 조작으로 오인하지 않고 입력 부족으로 반환했다. 독립 평가자는 관찰 확인 행의 거짓 수락을 찾지 못했으나 일부 조작(여자 선택, 역방향 토글, 메뉴 닫힘 등)의 발견·판정 누락을 확인했다. 전체 발견 효능 통과로 세지 않는다.
- 이 검토의 v2/v5 재선택 요구는 기존 변경 승인 원문이 연결되지 않은 문제다. A8 `GATE-web-related-persons-a8-4.md`가 개정 13·14를 가리킨다. 다음 보완 인계에서는 scope가 참조한 원문 읽기를 허용하고 기존 결정 출처부터 확인한다. 평가자가 새 제품 승인을 만들어 주지 않는다.
- `coordinator-live`는 같은 A8 원본 바이트를 실제 Chrome에서 조작해 33 case와 86개 조작 로그를 만들고 관계/시간/지역 메뉴 열린 캡처를 보강했다. 원본 변형 없이 UI 삭제로 빈 목록에 도달했다. 다만 전 항목 선택·삭제 확인 scrim 등의 미관찰이 남아 실행자의 ‘전수’ 완료 선언은 수락하지 않았다. 이 산출물을 최신 역할로 독립 G0 검토하는 실행은 `g0-observed-review`다.
- 최신 4파일 snapshot 기준 `make verify-web` exit 0(9 fixture 파일 실패 0, scripts/assets 및 가이드 미러 통과), `claude plugin validate dddjango-web --strict` exit 0, `git diff --check` exit 0. 원래 두 문서의 SHA-256은 작업 시작 기준선과 동일하다.

### 발견 목록을 먼저 만드는 순서로 보완

- `g0-observed-review/result.md`는 새 자료도 fail로 반송했으나 여자 재선택·윤달 해제·빈 목록 등록 등을 같은 핸들러 nit로 낮췄고 나머지 실제 메뉴 항목을 발견 표에 넣지 않았다. 관찰 자료를 먼저 읽고 그 자료 중심으로 목록을 구성하는 실패가 반복돼 기존 문단을 순서 중심으로 교체했다.
- 독립 계획 증분 검토: Critical/Important 추가 없음, 사용자 선택 충돌 없음. Coordinator는 원본에서 목록을 먼저 작성→실제 조작·새 대상 추가→미대응 행 대조. reviewer는 scope의 요구/승인 부분·원본/부품 정의에서 독립 목록을 먼저 작성→관찰 자료와 case를 읽고 모든 행을 증거에 대응. 기존 표·파일·역할·스키마 유지.
- 실제 승인 원문은 A8 native transcript `54754273-a334-4a58-bdd0-88a043c4010c.jsonl:3190`의 user 메시지(발주자 개정 13·14)에서 확인했다. 원문만 `coordinator-repair/existing-approval.md`에 출처·본문 hash와 함께 발췌해 기존 결정 연결을 복구했다. 분석/예상 관찰 목록은 실행자에게 전달하지 않았다.
- 최신 snapshot `discovery-first-plugin`, 실행 `coordinator-repair`: 실제 기존 A8 관찰 자료와 직전 native reviewer 원문을 인계하고, 같은 전용 Chrome에서 보완·native 독립 G0 reviewer 호출·inputs까지 실행하도록 했다. 새 제품 결정이 필요하면 반환하며 Phase 1 이후는 비허용이다. 이전 검증 통과는 이 순서 변경 전 snapshot의 결과이므로 관련 검증을 다시 수행한다.

- 순서 보완 구현의 독립 코드 리뷰: Critical/Important 없음. 공통 입력 목록과 G0 읽기 순서 충돌 없음, G1·이미지·disabled·부분 범위 유지, 두 플랫폼 의미 일치 확인.
- 최신 snapshot 전체 `make verify`: 6/6, exit 0, 246초. `/tmp/dddjango-web-a8-interactions-20260913/verify-final.log`, 상세 `/tmp/djr-verify.TL4kw2`. `verify-web-discovery-first.log`도 exit 0, strict manifest·diff 검사 통과.
- CLI의 명시 slash 호출이 command 본문을 실제 주입하는지는 도구 없는 읽기 전용 `activation-probe`로 확인했다. source 파일을 읽을 도구 없이 최신 세 단계 제목을 정확히 반환했다. 이는 적재 경로 확인이며 행동 효능 증거로 세지 않는다. native 내부 도구명은 `Agent` 옵션이 `Task`로 노출되는 별칭이다.

### 최신 실제 실행 실패와 구조 보완 계획

- `coordinator-repair/native-review-r3.md`는 선택하지 않은 관계/지역 항목을 같은 핸들러의 데이터 변이로 제외하고 pass를 반환했다. 원문을 보존한 `coverage-review.md`에 대해 기존 `inputs`도 exit 0, 복사본 build-state도 ready가 됐다. 평가자는 이를 거짓 통과로 기각했다. 실제 A8 앱/원본 build 및 Phase 1 이후는 실행하지 않았다. 중단 시도 시 native 실행은 이미 종료돼 있었다.
- 원인: 원본 trace는 비어 있지 않은 바이트인지 검사할 뿐 조작 대상 집합과 실제 조작 집합을 대조하지 않는다. 독립 reviewer의 의미 판정만으로 누락 항목이 면제된다. 프롬프트 순서 변경만으로 해결됐다는 가설은 기각한다.
- 앞의 ‘checker·JSON 변경 없음’은 당시 최소 변경 가설이며 사용자 제한이 아니다. 실제 실패를 막는 데 필요한 다음 변경을 검토한다. 배포/2번/앱 수정 범위는 그대로 제외한다.

**기계 대조 설계(구현 전 적대 검토):**

1. 설치 스크립트 `observe_interactions.mjs`는 이미 연결된 Playwright page를 인자로 받는 작은 수집기다. 브라우저 설치/실행·원본 변경·임의 탐색은 하지 않는다. 지정 원본 영역의 DOM에서 실제 렌더된 semantic control과 클릭 핸들러가 있는 leaf control을 수집한다. source/부품 검토가 발견한 비semantic 대상은 명시 locator로 보충한다. 브라우저 자동 발견의 한계는 전체 source 발견과 별도로 검토한다.
2. 수집기는 실제 조작 호출 전 inventory와 대상의 실제 DOM 식별자, 실제 action 결과 이후 inventory·DOM 값·캡처를 한 step으로 저장한다. click/fill/blur/press/hover는 실제 Playwright locator에 수행한다. 실패한 조작은 성공 기록으로 바꾸지 않는다. 메뉴가 열리거나 상위 선택으로 하위 목록이 바뀌면 다음 inventory에 항목 전체가 들어간다. DOM에 없는 가상 목록은 source 보완 대상이며 수집 완료로 보지 않는다.
3. 대상 식별은 원본 entrypoint·영역·DOM 경로/실제 label/role로, 메뉴 항목은 소유 메뉴와 실제 전체 항목 집합도 포함해 같은 이름의 다른 지역 선택지가 합쳐지지 않게 한다. 체크박스 양 상태를 구별하고, 입력은 click/fill/blur, 선택 항목/버튼은 click의 실제 실행을 대조한다. 결과가 달라지는 진입 상태와 source 이벤트는 기존 독립 검토로 보완한다. 전체 입력값 조합은 열거하지 않는다.
4. `check_design_evidence.py`의 원본 관찰 입력에 구조화된 interaction 기록 pointer를 연결하고 digest에 봉인한다. 원본이 HTML인 경우 누락된 기록·빈 관찰·잘못된 참조는 red다. 이미지 단독은 기존 경로를 유지한다. 내부 작은 검증 함수는 모든 inventory에서 발견된 enabled 대상의 필요한 조작과 실제 action을 집합 대조하며, 같은 핸들러/representative/executed=true 같은 작성자 면제 필드를 두지 않는다. 비활성은 실제 DOM 상태로 구별한다. reviewer pass가 잔여 누락을 지우지 않는다.
5. Coordinator는 source 발견 목록과 수집기의 잔여 항목을 실제로 보완한 뒤 reviewer에 전달한다. reviewer는 source에서 수집기가 놓친 대상을 감사하며 기계 통과를 전체 발견 보증으로 해석하지 않는다. 기존의 실패한 장문 금지문을 더 누적하지 않고 실행/입력 계약으로 교체한다. Claude/Codex 스크립트 byte mirror 및 산문 의미 mirror를 유지한다.
6. 검증 순서: 실제 A8 거짓 통과 자료를 새 계약으로 red 확인 → 원본을 native Coordinator가 수집기와 실제 UI로 관찰·잔여 항목 보완 → 평가자 비공개 oracle/실제 호출 기록으로 발견·실행·전달을 따로 판정 → 독립 reviewer+inputs 정상 경로 → 적대 최종 검토·저장소 검사. A8 성과가 없으면 채택/완료로 보고하지 않는다.

수집기 hash는 버전/동일성 표시이며 브라우저 실행 자체의 인증이라고 주장하지 않는다. 수동 산문 로그를 파싱해서 구조화된 성공 기록으로 바꾸지 않는다. 기존 자료는 재관찰 전 미확인으로 남긴다.

## 후속(2026-09-13 저녁)

- 프롬프트 접근 3회(발견 목록 우선 → G0/G1 분리 → 순서 보완)는 행동 평가에서 거짓 통과(native-review-r3)로 기각됐다. 위 «기계 대조 설계» 초안을 관례 절차로 다시 밟아 기계 계약으로 전환했다.
- 진단: `workspace/eval/web-a8-interaction-observation/diagnosis.md` · 설계 v2: `workspace/design/2026-09-13-web-interaction-evidence.md` · 계획: `workspace/plan/2026-09-13-web-interaction-evidence.md` · 검토 원문: `workspace/eval/web-a8-interaction-observation/design-review/rv-{A,B,C,R}.md`·`plan-review.md`.
- 이 메모의 `/tmp` 실행 자료 중 프롬프트·판정·oracle은 `workspace/eval/web-a8-interaction-observation/prior/`로 이관했다.
