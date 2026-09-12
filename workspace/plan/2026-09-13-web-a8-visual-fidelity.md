# A8 시안 재현 누락 교정 계획

> 실행: 문제 확인 → 계획 독립 적대 검토 → 구현 → 실제 행동 평가와 독립 구현 검토 → 필수 검사 → 커밋·dddjango-web 릴리즈. 사용자는 2026-09-13 특별한 결정 사항이 없으면 배포까지 진행하도록 승인했다.

**Goal:** 원본에서 읽은 부모 구성의 누락, 관찰 없는 시각 일치 주장, 위임 중 focus 검증 누락(A8-V1~V3)을 기존 시안 대조·반환 절차 안에서 막는다.

**Architecture:** `dddjango-web/`의 산문 정본과 Codex 의미 미러를 수정한다. 기존 시각 연결표·motion-notes·visual-check를 사용하고 Coordinator가 기록 소유권을 유지한다. 원본/구현 JSON 스키마와 결정적 검사기의 시각 판정 범위는 확장하지 않는다. 재사용 자체나 정당한 검증 위임·브라우저 미가용은 허용하며, 코드 green과 시각 완료를 구분한다.

**Tech Stack:** Markdown 런타임 지침, 격리 HTML/CSS 행동 평가, 기존 Python/shell 검증 및 make release-web.

**Spec:** `workspace/eval/web-a8-visual-fidelity/diagnosis.md`. A8 실제 앱·빌드 자료는 읽기 전용이다. 2px 부모 여백 복사만으로 3px ring의 완전 재현을 보장하지 않는다. 기존 `docs/master.html` 변경은 보존한다.

## Task 1 — 반환·인계 계약과 원본 대조 절차

대상 정본:
- `dddjango-web/skills/implementation-ui/references/final.md` §2
- `dddjango-web/agents/coder-web.md`
- `dddjango-web/agents/design-review-web.md` G0
- `dddjango-web/agents/discipline-reviewer-web.md`
- `dddjango-web/commands/dddjango-web.md` 구현·시각 검증 위임
- 위 파일들의 `codex-dddjango-web/skills/` 의미 미러

필요할 때만 기존 시각 연결표 소유자인 design-architect-web의 판형을 같은 의미로 갱신한다. 별도 JSON·검사기·온톨로지 규칙은 만들지 않는다.

- [x] 수정 전 원본 지침으로 독립 문맥의 소형 행동 시험 5회를 실행한다. 기존 A8 native 실패와 새 시험을 구분해 보존한다.
- [x] 독립 적대 계획 리뷰에서 원인 대응, 과잉 규율, 위임·미가용 경로, 검증 오라클을 검토하고 중요한 발견을 해소한다.
- [x] 원본에서 구현으로 옮길 때 부품 내부뿐 아니라 실제로 맞닿는 부모 배치·여백·overflow와 자식 효과를 한 구성으로 대조한다. 모든 조상/속성 전수 기록은 요구하지 않는다.
- [x] 기존 스타일 적용 근거를 필수 반환 판형으로 바꾼다: `case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 사유/다음 실행자·필요 조건`. 같은 상태·효과의 묶음은 허용한다. 이미지 시안은 관찰 가능한 범위만 기록한다.
- [x] G0의 기존 case 대응 반환에 원본/컴포넌트에서 확인한 관련 상태와 실제 조작·관찰 위치를 넣는다. focus 같은 부품 내부 상태는 해당 case의 확인 항목으로 연결한다. 별도 독립 렌더가 필요한 화면·상태만 기존 case 절차로 추가하며 모든 CSS pseudo-state를 case로 강제하지 않는다.
- [x] Coordinator는 해당 case/상태 행과 실행 환경을 코더·브라우저 대행·감수자에게 직접 넘기고 반환을 같은 행에 합친다. 브라우저 smoke만 반환되면 확인하지 않은 항목은 미검증으로 남겨 보완한다. 구조만 끝난 슬라이스의 green/커밋을 막지 않는다.
- [x] Coordinator는 전달한 필수 상태와 반환 행을 대조해 누락·미검증·실패를 상위 case의 pass로 합치지 않는다. 실제 관찰과 구체 승인된 이탈 대조가 충족되어야 case를 통과시킨다. 같은 반환의 미검증과 포괄적 외형 일치 주장이 충돌하면 일치 요약을 수용하지 않고 근거에 맞춘 정정·보완을 요청한다. JSON 상태 필드는 추가하지 않는다.
- [x] 감수자는 원본↔현재 구현을 같은 상태로 독립 대조하고 관찰/이탈 승인/미검증을 구별한다. 검사·토큰·기존 DS 재사용만으로 관찰 결과를 채우지 않는다.
- [x] Claude/Codex 의미 일치와 reference 복제 정합을 확인한다.

## Task 2 — 실행 검증과 적대 구현 검토

평가 자료는 `workspace/eval/web-a8-visual-fidelity/`에 필요한 프롬프트·오라클·실행 결과·판정만 보존한다. 외부 서비스·실제 사용자 데이터를 사용하지 않는다.

- [x] 수정본으로 같은 소형 행동 시험을 5회 실행해 각 결과를 수동 판독한다. 기존 지침 대조군과 새 지침군의 차이를 보고하며 완전한 native 파이프라인 성공으로 확대하지 않는다.
- [x] 소형 시험: 기존 DS를 재사용하는 입력 UI를 원본에서 이식하고 검증 보고를 작성한다. 부모 overflow/여백과 focus 효과가 소스에 있으며 정답 CSS는 요구문에 주지 않는다. 실제 수정 파일과 읽기/도구·최종 반환을 대조한다.
- [x] 압력 시나리오: 구조 검사는 green, 납기 우선, 기존 DS라 외형이 같다는 선행 주장 아래서도 브라우저 관찰을 배정받은 가용 실행자는 실제 focus 조작·관찰을 수행해야 합격이다. 미검증 인계만으로 이 양성 시험을 통과시키지 않는다. 브라우저 미가용/명시적 분리 위임 시험에서는 범위·다음 실행자·필요 조건의 정직한 미검증 인계를 별도 합격으로 집계한다.
- [x] G0 입력범위 역할은 원본 내부 focus를 해당 case 확인 항목으로 반환해야 한다. 그 반환을 받은 Coordinator 역할이 실제 검증 위임에 focus를 넣고, 기본 화면 smoke만 돌아온 뒤에는 빠진 focus를 보완 대상으로 유지하는지 실행한다. 미검증/matches가 공존하는 반환도 같은 수용 판단으로 시험한다. 실제 대행의 focus 수행 결과를 받기 전에는 case pass가 없어야 한다.
- [x] 감수자 역할에 원본 부모 여백을 누락한 구현과 DS 재사용/green 보고를 주어 직접 원본 대조로 결함을 발견하는지 실행한다. 별도의 정상·등가 CSS 구현은 결함으로 오인하지 않아야 한다. 평가자 브라우저 관찰이나 플러그인 diff 리뷰로 이 역할 실행을 대신하지 않는다.
- [x] 독립 브라우저에서 같은 viewport·기본/focus 상태를 재현해 부모 여백 누락의 잘림과 원본 구성 보존 여부를 확인한다. 픽셀/기하 관찰은 이 통제 fixture에만 적용한다.
- [x] 독립 구현 리뷰가 전체 diff와 실제 행동 증거를 검토한다. 중요한 미해결 발견이 있으면 같은 단계에서 보완·재검증하며 후속 단계로 건너뛰지 않는다.
- [x] `make verify-web`, 최종 `make verify`, `claude plugin validate dddjango-web --strict`를 실제 실행한다. native 전체 A/B 실런을 하게 되면 그 직전에는 정본 가이드의 `make verify-runready`를 실행한다.
- [x] 검증 선행 문제: 첫 전체 검사에서 backend manifest 봉인이 이전 2.18.2를 가리켜 현재 2.18.3과 불일치했다. 두 봉인 hash가 HEAD^의 실제 bytes+실행 비트와 같음을 확인했다. 개발 가이드 §4에 따라 `manifest_seal.py --write`로 `workspace/eval/ab/T2-0b-manifest.json`과 `workspace/design/2026-08-20-ontology-t2-0b-design.md`의 기계 렌더 사실만 갱신했다. backend 런타임 코드는 변경하지 않았으며 전체 검사를 새로 실행해 6/6·exit 0·293초로 통과했다.

## Task 3 — 배포

- [x] 계획·진단의 현재 상태를 완료 사실과 잔여 한계에 맞춰 갱신한다. 과거 실패 기록을 성공으로 바꾸지 않는다.
- [ ] 최종 검증된 파일만 커밋한다. `.venv` 작업용 링크와 primary의 기존 master.html 변경은 포함하지 않는다.
- [ ] main에 fast-forward 통합하고 기존 변경을 안전하게 보존한 상태에서 `make release-web` patch(예정 1.1.11)로 발행한다. backend 버전은 그대로 둔다.
- [ ] 두 web manifest 버전·원격 main/tag·GitHub Release를 확인하고 보존한 master.html 변경이 동일한지 확인한다.

## 현재 상태

2026-09-13 커밋·릴리즈 직전 기록: 진단, 계획 적대 검토와 Important 2건 해소, 정본 6개·Codex 6개 구현, 지침 micro 기존 5/5·후보 5/5, G0·Coordinator·브라우저 coder·독립 감수 역할 시험, 최종 필수 검사와 전체 적대 구현 리뷰를 완료했다. 최종 리뷰는 Critical 0 / Important 0, Spec·Quality PASS, ReadyToRelease YES다. 기록의 요소 수 오기 1건을 정정했고 미해결 결함은 없다.

최종 필수 검사는 `workspace/eval/web-a8-visual-fidelity/verification/final-verify.log`의 `make verify` 6/6·exit 0·293초와 strict manifest 검증 PASS다. micro의 기존 지침도 모두 통과했으므로 성공률 개선을 주장하지 않는다. 전체 native 파이프라인·실제 A8 앱 수정·최종 G2는 평가 범위가 아니다. 상세는 [개발 검증 기록](../eval/web-a8-visual-fidelity/README.md)을 따른다.

Task 3의 남은 체크박스는 이 기록 이후 실행할 커밋·발행 절차다. 발행 전에 완료로 적지 않으며, 실제 결과는 `dddjango-web--v1.1.11` 태그·정식 GitHub Release와 사용자 완료 보고에서 확인한다.
