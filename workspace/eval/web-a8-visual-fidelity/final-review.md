# A8 시안 재현 교정 — 최종 독립 whole-branch 리뷰

2026-09-13. 첫 입력은 `final-review-input.md`이며 구현 작성자의 이전 작업 문맥 없이 패킷의 정본·계획·진단·diff·실행 증거를 대조했다. 기준 HEAD는 `3e786dce64eee3da81d98e1dc2dcad598ab5d026`, 작업 루트는 `/Users/hyun/.cache/dddjango-web-a8-20260913`다. 이 리뷰의 쓰기는 이 파일 하나뿐이다.

**Critical 0 / Important 0. 중요한 미해결 구현·증거 결함을 발견하지 않았다.**

| 판정 | 결과 | 근거와 적용 한계 |
|---|---|---|
| Spec | PASS | A8-V1의 관련 부모·자식 효과, V2의 미검증/matches 모순, V3의 상태 발견·전달·수용이 기존 역할 계약 안에서 연결됐다. |
| Quality | PASS | 정본 6개·Codex 6개 의미 정합, reference byte 동일, 기존 정상·등가·위임 경로 유지. 실제 역할 증거와 주장 수준이 부합한다. |
| ReadyToRelease | YES — 검토한 변경으로 배포 절차 진입 가능 | 리뷰상 차단 사유가 없다. 계획·진단의 현행 상태 정리, 선별 커밋, `make release-web`, 원격 버전·태그·Release 확인은 실행 담당자의 남은 절차이며 이 리뷰가 수행하거나 완료 판정한 작업은 아니다. |

**확인한 변경 범위**

`git status --short`, 전체 tracked diff와 변경 목록을 확인했다. tracked 변경은 다음 14파일뿐이며 web 런타임 12파일과 backend 봉인 사실 2파일로 나뉜다.

| Claude 정본/기계 사실 | 대응 Codex 파일 |
|---|---|
| `dddjango-web/commands/dddjango-web.md` | `codex-dddjango-web/skills/dddjango-web/SKILL.md` |
| `dddjango-web/agents/coder-web.md` | `codex-dddjango-web/skills/dddjango-web-coder-web/SKILL.md` |
| `dddjango-web/agents/design-architect-web.md` | `codex-dddjango-web/skills/dddjango-web-design-architect-web/SKILL.md` |
| `dddjango-web/agents/design-review-web.md` | `codex-dddjango-web/skills/dddjango-web-design-review-web/SKILL.md` |
| `dddjango-web/agents/discipline-reviewer-web.md` | `codex-dddjango-web/skills/dddjango-web-discipline-reviewer-web/SKILL.md` |
| `dddjango-web/skills/implementation-ui/references/final.md` | `codex-dddjango-web/skills/implementation-ui/references/final.md` |
| `workspace/eval/ab/T2-0b-manifest.json` | 해당 없음 |
| `workspace/design/2026-08-20-ontology-t2-0b-design.md` | 해당 없음 |

4역할과 reference는 diff의 추가·삭제 줄이 양 런타임에서 정확히 같았다. Coordinator의 차이는 기존 Claude 호출/`${CLAUDE_PLUGIN_ROOT}`와 Codex `spawn_agent`/`${SKILL_DIR}` 표기이며 새 상태 전달·수용 문장은 같다. reference 전체 bytes도 직접 비교해 같음을 확인했다. `candidate-hashes.json`의 12개, `verification/result.json`의 14개 hash를 현재 파일에서 다시 계산해 모두 일치했다.

`dddjango/`, `codex-dddjango/`, `ontology/`에는 diff가 없다. web은 `docs/DEVELOPMENT.md` §1의 온톨로지 밖 산문 정본이므로 이번 직접 편집이 graph-owned 규범 수정 절차를 우회하지 않는다. JSON 스키마·checker·매니페스트 버전 변경도 없다.

backend 봉인 변경은 초기 검증의 실제 세 지적(plugin_payload의 두 manifest와 tree drift)에 대응한다. Git의 HEAD^ 두 manifest가 2.18.2이고 현재가 2.18.3임을 직접 확인했으며, 내용+실행 비트 방식으로 이전/현재 봉인 hash가 각각 맞음을 재계산했다. design 문서의 한 줄과 manifest의 cache·hash·버전·sealed_commit 기계 사실 외에 backend runtime 변경은 없다. 개발 가이드 §4에 따른 선행 검사 해소로 판단한다.

untracked 항목은 `.venv` 링크, 승인된 계획 파일, 이 eval 폴더다. `.venv`는 primary의 기존 venv를 가리키는 작업용 링크이며 계획에 커밋 제외가 명시돼 있다. 리뷰 시작 시 eval 파일 목록은 304개·약 2.92MB였고, 중복 fixture/guidance는 아래 해시 대조로 묶어 검토했다. 실제 A8 앱 파일이나 primary의 `docs/master.html` 변경은 이 diff에 없다. 이 리뷰는 primary 전체의 미추적 외부 상태까지 감사한 것은 아니다.

**규범이 결함을 차단하는 연결**

- **A8-V1:** `implementation-ui/references/final.md:53`은 원본 부품과 실제 맞닿는 부모 배치·여백·overflow를 자식 효과와 함께 대조하고 선언 복사만으로 재현을 확정하지 못하게 한다. `:57` 이후의 필수 반환 표는 원본 구성→구현 구성→실제 수행→결과/미검증을 연결한다. architect `:50`은 원본 위치와 관련 부모를 설계 연결표에 넣고, coder `:53`·감수자 `:63`이 각각 이식과 독립 역대조를 맡는다. 시안 정본을 설계 요약이나 기존 DS로 바꾸지 않는다.
- **A8-V2:** coder `:55`와 reference `:62`는 맡은 관찰이 가능하면 실제 조작하고 미실행 범위를 일치로 요약하지 않도록 한다. Coordinator `:181`은 같은 반환의 미검증/matches 모순을 수용하지 않고 정정·보완을 요구한다. 이 반환 검사가 기존 추상적 완료 지침에 추가된 구체 수용 기준이다.
- **A8-V3:** G0 reviewer `:23`·`:25`는 원본/부품에서 확인한 focus 등 관련 상태, 발동 조작·대상·관찰 위치를 기존 case 확인 항목으로 반환한다. architect `:50`, Coordinator `:154`·`:176`·`:180`, coder 입력 `:25`, 감수자 입력 `:28`이 같은 행을 소비한다. Coordinator `:181`은 기본 smoke만 돌아온 경우 빠진 상태를 미검증으로 유지하고 필수 상태가 충족되기 전 상위 case pass를 금지한다.

새 표는 기존 `visual-check.md`에 통합하며 기록 소유는 Coordinator에 남아 있다. 모든 조상·CSS 속성의 전수 행, 모든 pseudo-state의 독립 case, 새 JSON 상태 필드를 요구하지 않는다. 이미지 단독 시안은 관찰/측정 가능한 범위를 사용하며, 다른 토큰 이름·등가 CSS를 허용한다. 미가용·명시적 분리 위임에는 사유·다음 실행자·필요 조건을 남기고 구조 green과 시각 완료를 구별한다. 아직 화면이 없는 데이터 감사의 비적용 문구와 구조 슬라이스 green/커밋 경로도 유지돼 있다. 검토 범위에서 이 정상 경로를 막는 중요한 새 의무는 발견하지 않았다.

**실행 증거와 직접 확인**

| 증거 | 이 리뷰에서 직접 확인한 사실 | 판정 범위 |
|---|---|---|
| `micro/results.md`, 열 번의 `verdict.md`·`response.md`·실제 CSS·`review-facts.json` | 기존 5/5와 후보 5/5 모두 여백 1선언을 같은 출력 hash로 보존하며 focus·부모 경계와 미검증 후속 책임을 반환했다. 10회 fixture 보호 파일·guidance 복사본 불변을 다시 비교했다. frozen 입력 14개·후보 guidance 4개 hash도 일치하고 baseline reference는 HEAD 원문과 같다. | 원본 보존·정당한 미검증 인계의 통제 시험이다. 기존도 전부 통과했으므로 개선율·native 실패 해결의 증명이 아니다. |
| `role-g0-return.md` | 기존 단일 case 안에서 focus·전환·입력/해제·부모 경계를 확인 항목으로 연결하고 관찰 부족을 반환했다. | 실제 상태 발견 역할 checkpoint. native 입력 게이트를 실행했다고 하지 않는다. |
| `role-coordinator-decision.md`, `role-dispatch.md` | 합성 부분 반환의 smoke/미검증과 matches를 분리해 일치 주장을 거절했다. 실제 다음 호출문에 focus·전환·부모 경계·환경·담당과 반환 조건을 포함했다. | 합성 불완전 반환의 수용 판단과 실제 인계문 작성 증거다. 전체 native 순차 파이프라인 실행 증거는 아니다. |
| `role-browser-app/handoff.md`, `verification.json`, 전후 관찰 JSON | 실제 CSS는 padding 1선언이다. 전후 관찰의 focus click·fill·Tab·Enter, rAF·transition 이벤트, 390×844와 부모/입력 기하가 보고와 부합한다. 최종 원본과 구현은 각각 진입/해제 34 frame을 기록했고 종결 `elapsedTime`은 0.16이다. | 가용 브라우저에서 실제 상태를 발동한 coder checkpoint. 시간차 live PNG의 프레임 동일성을 주장하지 않는 한계가 적절하다. |
| `role-browser-app/capture-comparisons.json` | 18쌍의 PNG bytes와 양쪽 hash를 재계산해 기록과 모두 일치했다. 최종 원본↔구현 안정 상태 5개+경계 상세 1개는 동일하고 수정 전↔후는 다르다. 원본·수정 전·후 focus 경계 PNG 3개를 직접 열람했다. | 통제 fixture에서 관찰한 상태의 일치를 보강한다. 전체 A8·모든 화면의 일치를 뜻하지 않는다. |
| `role-review/report.md`, `observations.json`, A/B CSS | 감수 원문은 완료돼 있었다. 실제 실행 snippet이 각 CSS를 별도 page에 사용해 click/fill/Tab 뒤 독립 캡처한다. 보호 입력 7개 hash를 재계산했고 8쌍 PNG 비교도 재확인했다. A는 4상태 모두 차이, B는 4상태 모두 bytes 동일이다. 원본/A/B focus PNG를 직접 열람해 보고의 배치·좌우 잘림 차이와 부합함을 확인했다. | 누락된 부모 여백을 사후 발견하고 논리 padding 등가 구현을 오탐하지 않았다. transition 중간 frame 등 감수 요청 밖 항목은 미실행으로 명시한다. |
| `browser/README.md`, 원본 CSS와 관찰 기록 | 원본 2px 공간, 누락 0px, 공간 확보용 4px 통제와 3px shadow의 의미를 구별한다. coder·감수 보고도 원본 자체 일부 잘림을 인정한다. | 4px을 승인된 재현 해법으로 바꾸거나 2px 복사를 3px 링 완전 정상화로 주장하지 않는다. |
| `verification/final-verify.log`, `result.json` | 마지막 `make verify` 로그는 6/6·exit 0·293초이고 현재 14파일 hash가 검증 당시와 같다. strict manifest 검증은 result에 exit 0/Validation passed로 기록돼 있다. | 이 리뷰는 이미 수행된 필수 검사를 재실행하지 않았고, strict 도구의 별도 전체 raw transcript는 패킷에 없다. |

민감정보 점검은 eval의 비-PNG 파일 254개에 대한 private key·긴 credential literal·알려진 token prefix 검색과 실제 fixture/캡처 열람으로 한정했다. 해당 패턴의 발견은 0이며, 캡처의 이름은 통제 fixture 입력이다. 계정·인증정보나 실제 사용자 데이터가 포함됐다는 근거를 발견하지 않았다. 일반 문서에 있는 로컬 경로·도구 오류·Git 해시를 인증 비밀로 분류하지 않았다.

**경미한 기록 정리 — 배포 차단 아님**

리뷰 당시 `role-review/report.md`의 “12개 대상 요소”는 `observations.json`과 수가 다르다. 각 session/state의 `observed.elements`는 dialog·title·scroll·step·field·label·input_shell·icon·input·note·button **11개**다. **12는 캡처 수**(원본/A/B × 4상태)로 맞다. 최소 권고는 보고의 요소 개수만 11로 정정하는 것이다. 원본/B 동일성과 A 차이 판정에는 영향이 없고 구현 수정·재실행이 필요한 발견이 아니다.

**잔여 한계**

프롬프트 계약의 연결과 지정한 역할 행동은 확인했지만 모든 native 실행에서 같은 누락을 불가능하게 만든다는 보장은 아니다. 전체 native Coordinator→Django 앱→최종 G2, 실제 A8 앱 수정/인수, Claude/Codex 설치 cache 양쪽의 행동 비교는 이번 평가에 없다. micro child의 전체 raw tool transcript도 export되지 않았으므로 역할의 과거 수행 진술, 보존된 파일/관찰 JSON, 평가자의 독립 확인을 구별했다. 이 리뷰가 새 브라우저 조작을 실행한 것은 아니며 저장된 대표 PNG 6개를 직접 열고 나머지 관련 캡처의 bytes·관찰 자료를 확인했다. 기록의 초기 실패는 성공 표본으로 바뀌지 않았고, 새 CLI/권한 확장 실행 거절과 이후 기존 도구 사용도 한계에 맞게 남아 있다.

계획 체크박스와 진단의 현재 상태는 패킷이 명시한 후속 사실 정리 대상이므로 과거 실패 기록을 수정 성공으로 뒤집으라는 권고를 하지 않는다. 선택적 개선이나 추가 반복 평가를 배포 선행 조건으로 늘리지 않는다.

Serena·Graphify는 opt-in 부재와 패킷의 명시적 제외에 따라 사용하지 않았다. 새 CLI·권한 확장·자동 승인 옵션·추가 subagent·소스/기존 증거 수정·커밋·배포를 수행하지 않았다.
