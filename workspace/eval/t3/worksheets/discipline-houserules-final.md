# T3 이관 검수표 — discipline-houserules-final

- 원문: `dddjango/skills/discipline-houserules/references/final.md` (242행 · 센서스 일치 · 드리프트 경고 없음 · `graph-owned` 마커 0건 — 좌표 환산 불요)
- spec: `workspace/eval/t3/specs/discipline-houserules-final.spec.json`
- 규모: REF 15절 · 블록 45 · Work 58(발주서 규범 58 — **전건 일치**)
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/discipline-houserules-final.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

| section_key | 헤딩 | 발주서 | spec | 대사 |
|---|---|---|---|---|
| `s001` | dddjango 표준 파일트리 | 3 | 3 | 일치 |
| `s002` | 무엇이고 왜 | 1 | 1 | 일치 |
| `s003-0` | §0 제1원칙 | 12 | 12 | 일치 |
| `s004-1` | §1 표준 트리 — 140행 | 3 | 3 | 일치 |
| `s006` | BC 직계 — 일곱뿐 | 7 | 7 | 일치 |
| `s007` | 입구 — `driving_layer/` | 8 | 8 | 일치 |
| `s008` | 만들지 않는 칸 | 5 | 5 | 일치 |
| `s009` | `migrations/` — 생성물만 | 3 | 3 | 일치 |
| `s010` | `<project>/` | 5 | 5 | 일치 |
| `s011-3` | §3 명명 | 3 | 3 | 일치 |
| `s013` | 이관 종료 (2026-08-12) | 2 | 2 | 일치 |
| `s014` | brownfield 는 «면제»가 아니라 «빚» | 3 | 3 | 일치 |
| `s015` | 검사기의 가드 계약 | 1 | 1 | 일치 |
| `s016` | 규칙 개정의 이행 순서 | 1 | 1 | 일치 |
| `s017` | 배경 | 1 | 1 | 일치 |
| **합계** | — | **58** | **58** | **차 0** |

불일치 절 없음. 계수가 갈릴 수 있는 절의 분해 실물:

- `s001` **3** = 3행 **2**(① 이 문서가 값의 정본 = SKILL·에이전트는 가리키기만·복제 금지 ② 트리↔`standard_tree.py` 동기는 `tree_mirror_check` 가 지킨다) + 5행 **1**(상세·명명 전수는 `rule-owner-map` 순서로 편입). 3행 셋째 문장(«규칙 문면 끝의 `#N` 은 … 규칙 번호다»)은 **ID 체계 정의**라 비계수 — 센서스 note 와 동일 판정.
- `s003-0` **12** = 15행 **1**(#487) + 17행 **2**(#486 — 골격 유지 / 미준수는 반환) + 18행 **1**(#488) + 19행 **1**(#489) + 20행 **3**(#490 — 트리 밖 경로 위반 / 폐쇄는 칸에만·리프 안은 재량(#15) / `framework/`·`<project>/` 는 주어 아님) + 21행 **1**(#491) + 22행 **1**(#492) + 24행 **2**(실현 주체 coder / 위반은 `check-layer-skeleton` 이 잡는다).
- `s004-1` **3** — 트리 140행(```` ```text ````)은 규범 «값» 이지만 **문장 비계수**(행 번호가 좌표계 — P0 승계). 규범은 30행 «손으로 고치지 않는다»(센서스 note 가 명시) + 177행 «최상위는 셋이다» + 179행 «기계 사본은 `scripts/standard_tree.py` — 검사기들이 import 하는 유일한 트리 데이터다» 3건. 28행(행 번호 좌표계 설명)·178행(표기 설명)은 prose 로 뺐다 — 지시가 없다.
- `s006` **7** = 185행 **2**(#81 일곱뿐 / 여덟째 없다) + 186행 **1**(#82) + 187행 **1**(#10) + 188행 **3**(#628 정의 / 용어집 파일 금지 / 불용어 목록은 저장소 데이터).
- `s007` **8** = 192행 1(#88) + 193행 1(#89) + 194행 **2**(#90 자식 넷뿐 / 행위자로 가르지 않음) + 195행 **2**(#91 전송 전 확장 금지 / 늘리는 주체는 정본 트리) + 196행 1(#92) + 197행 1(#178).
- `s008` **5** = 201행 **2**(#20·#21 이 한 불릿에 동거 — 괄호 문장은 예시라 비계수) + 202·203·204행 각 1.
- `s009` **3** — 208행 5문장 중 «두 상태뿐이라 배치 크기·부분 재실행·진행률이 구조적으로 안 된다»(이유)와 **«덤 — `elidable`…»**(센서스 note 가 «덤이라 제외» 명시)를 뺀 3건.
- `s010` **5** = 212행 **2**(#429 목록 폐쇄 / `celery.py` 조건부·#491 과의 관할 분리) + 213·214·215행 각 1.
- `s011-3` **3** = 219행 **2**(#82 재인용 / 명명 전수는 각 칸 «이름» 줄 소유·편입 예정) + 220행 **1**(유사 변형 금지).
- `s013` **2** · `s014` **3**(첫 문장 «그림자다» 는 설명 제외 — 센서스 note) · `s015`·`s016`·`s017` 각 **1**(`s016` 의 «순서가 뒤집히면 …» 은 이유 서술이라 제외 · `s017` 은 서사 중 «이 문서는 «값»만 싣는다» 1건만 보수 포함).

## 2. 배선 근거 표 (전 58 규범)

| 절 | 블록 | Work label | class | enforcedBy / delegatedTo | 4원 근거 |
|---|---|---|---|---|---|
| `s001` | b1 | 이 문서가 파일트리 «값»의 정본 — SKILL.md·에이전트 문서는 가리키기만 하고 값을 복제하지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s001` | b1 | 트리 블록(§1)과 기계 사본 standard_tree.py 의 동기는 tree_mirror_check 가 지킨다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s001` | b2 | 층·칸별 상세 규칙과 명명 전수는 rule-owner-map 순서로 이 문서에 편입된다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s002` | b2 | 트리는 «있어야 하나»·스킬은 «어떻게 쓰나» — 트리에 조건을 적어 두 채널로 만들지 않는다(#492) | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s003-0` | b1 | 제1원칙은 모든 검사보다 먼저 선다(#487) | Obligation | enforcedBy `check-layer-skeleton.py` | 근거4 |
| `s003-0` | b2 | #486 — 어느 BC 를 열어도 골격이 그대로 있다(내용 유무 무관) | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s003-0` | b2 | #486 — 파일트리를 지키지 않는 구현·설계는 «반환»이다 | Prohibition | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s003-0` | b3 | #488 — 고정 이름 칸은 부모가 있으면 반드시 있다(빈 폴더는 __init__.py·빈 파일로) | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s003-0` | b4 | #489 — 자리표시자 칸만 개념이 생길 때 생긴다 · 「없으니 뺀다」는 위반 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s003-0` | b5 | #490 — application/<bounded_context>/** 에 트리에 없는 경로가 있으면 위반 | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s003-0` | b5 | #490 — 폐쇄는 «칸»에만 걸리고 리프로 닫은 폴더 «안»의 추가 모듈은 작성자 재량(#15) | Permission | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s003-0` | b5 | #490 — framework/·<project>/ 는 이 원칙의 주어가 아니다 | Exception | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s003-0` | b6 | #491 — 칸의 유형은 셋뿐이고 «조건부»는 없다 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s003-0` | b7 | #492 — 「그 파일이 있어야 하나」는 트리가, 「어떻게 쓰나」는 스킬이 정한다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s003-0` | b8 | 골격의 실현 주체는 coder — 승인 스코프의 BC 를 새로 만들거나 touched 하면 고정·재등장 칸을 빈 채로라도 실현 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-coder` | 근거7 |
| `s003-0` | b8 | 골격 위반은 check-layer-skeleton 이 잡는다 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거4 |
| `s004-1` | b2 | TREE 블록은 tree_mirror_check 가 쓴다 — 손으로 고치지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s004-1` | b5 | 최상위는 셋뿐 — application/<bounded_context>/ · framework/ · <project>/ | Obligation | enforcedBy `check-layer-skeleton.py`·`check-app-container.py`·`check-common-container.py` | 근거8 |
| `s004-1` | b7 | 기계 사본 scripts/standard_tree.py 가 검사기들이 import 하는 유일한 트리 데이터 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s006` | b1 | #81 — BC 직계에는 층 폴더 넷·test/·composition_root/·published_event/ 일곱만 온다 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s006` | b1 | #81 — 여덟째 칸은 없다 | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s006` | b2 | #82 — BC 폴더 이름은 장고 앱 이름이 아니라 업무 경계의 이름 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거9 |
| `s006` | b3 | #10 — 네 칸을 모두 아는 것은 composition_root 하나뿐 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거9 |
| `s006` | b4 | #628 — BC 의 업무 어휘는 domain_layer/** 공개 심볼 이름의 토큰 집합(폴더 이름만이 아니다) | Obligation | enforcedBy `check-business-vocabulary.py` | 근거10 |
| `s006` | b4 | #628 — 별도의 «용어집 파일»은 두지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거22 |
| `s006` | b4 | #628 — 불용어 목록도 저장소가 유지하는 데이터 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거23 |
| `s007` | b1 | #88 — 입구 계층 폴더 이름은 driving_layer/(presentation_layer/ 금지) | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s007` | b2 | #89 — 바깥 행위자가 BC 를 부르는 통로는 driving_layer/ 뿐 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s007` | b3 | #90 — driving_layer/ 의 자식은 api/·open_host_service/·cron_job/·event_subscription/ 넷뿐 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s007` | b3 | #90 — 「누가 부르나」(행위자)로 가르지 않는다 | Prohibition | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s007` | b4 | #91 — 새 전송이 실제로 생기기 전에는 driving_layer/ 의 자식을 늘리지 않는다 | Prohibition | enforcedBy `check-missable-entrance.py`·`check-layer-skeleton.py` | 근거11 |
| `s007` | b4 | #91 — 칸을 늘리는 주체는 정본 트리 · 개정되면 #486 에 따라 미사용 BC 도 빈 채로 갖는다 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s007` | b5 | #92 — driving_layer/ 의 잎은 application_layer/<area>/ 아래만 의존(예외 넷) | Obligation | enforcedBy `check-context-isolation.py` | 근거12 |
| `s007` | b6 | #178 — 소비 task 가 조율을 시작하면 새 칸을 여는 게 아니라 입구 로직 금지 위반을 고친다 | Obligation | enforcedBy `check-missable-entrance.py` + delegatedTo `agent-discipline-reviewer` | 근거13 |
| `s008` | b1 | #20 — 값이 하나뿐인 축으로는 폴더를 만들지 않는다 | Prohibition | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s008` | b1 | #21 — 어떤 종류가 하나뿐이면 폴더가 아니라 파일로 둔다 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s008` | b2 | #58 — application/**/management/commands/ 를 만들지 않는다 | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s008` | b3 | #187 — 포트 선언에 BC 최상위 칸을 만들지 않는다(application_layer/port/ 에만) | Prohibition | enforcedBy `check-layer-skeleton.py`·`check-port-adapter-pairing.py` | 근거14 |
| `s008` | b4 | #314 — domain_layer/ 에 specification/ 폴더를 두지 않는다 | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s009` | b1 | #336~#338 — migrations/ 에는 makemigrations 생성물만(RunPython·RunSQL 손 채움 금지) | Prohibition | enforcedBy `check-mechanism-ownership.py` | 근거15 |
| `s009` | b1 | 대량 채우기는 파일이 아니라 배포 절차의 한 단계(Expand→Backfill→Contract · 트리 밖 scripts/ 는 규정하지 않는다) | Obligation | delegatedTo `agent-discipline-reviewer` | 근거16 |
| `s009` | b1 | #593 — 허용 목록은 도구 산출물의 모양이 정한다 · 그 밖의 함수·분기·도메인 import·데코레이터는 위반 | Prohibition | enforcedBy `check-mechanism-ownership.py` | 근거15 |
| `s010` | b1 | #429 — <project>/ 에는 프레임워크가 전역 하나를 요구하는 것만(api.py·urls.py·celery.py·settings/) | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s010` | b1 | #429 — celery.py 항목은 «celery 채택» 전제의 조건부이고 <project>/ 파트는 이 목록이 관할(#491 밖) | Exception | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s010` | b2 | #430 — <project>/ 는 application/ 을 등록만 하고 타입으로 알지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거24 |
| `s010` | b3 | #432 — <project>/ 는 BC 가 늘어도 커지지 않는다 | Obligation | enforcedBy `check-context-isolation.py` + delegatedTo `agent-discipline-reviewer` | 근거25 |
| `s010` | b4 | #436 — health.py·home.py·asgi.py·wsgi.py 는 표준 트리 관할 밖이라 칸을 만들지 않는다 | Exception | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s011-3` | b1 | BC 이름은 업무 경계의 이름(#82 재인용) | Obligation | delegatedTo `agent-discipline-reviewer` | 근거9 |
| `s011-3` | b1 | 파일·클래스 명명 규약 전수는 정본의 각 칸 «이름» 줄이 소유하며 rule-owner-map 순서로 편입 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s011-3` | b2 | BC(앱)명↔애그리거트명 유사 변형 금지 — 같게 하거나 명확히 다른 컨텍스트명으로 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거17 |
| `s013` | b1 | 옛 이름 이중 수용은 2026-08-12 에 종료 — 검사기는 옛 이름을 더 알아보지 않는다 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s013` | b1 | 옛 이름 재등장은 별도 진단이 아니라 트리 밖 칸 위반(#81·#490 · 층 이름 위장 #324) | Prohibition | enforcedBy `check-layer-skeleton.py`·`check-db-table.py` | 근거18 |
| `s014` | b1 | 「리팩터링 대상」을 따로 정의하지 않는다 — 백스톱이 내는 위반이 곧 그것이다 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s014` | b1 | BC 를 작업하면 그 BC 의 백스톱 위반을 먼저 정리하고 시작 · 「가만 있어도 해로운」 위반은 기다리지 않는다 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s014` | b1 | 미루기는 사용자에게 물어서만 가능하고 .dddjango/ 에 기록된다 | Obligation | delegatedTo `command-dddjango`·`agent-discipline-reviewer` | 근거19 |
| `s015` | b1 | #74 — 채택 신호가 있는데 검사 대상 0건이면 검사기는 통과가 아니라 exit 2 로 막는다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거20 |
| `s016` | b1 | #72 — 규칙 개정은 플러그인 셋(검사 스크립트·리뷰어 지침·표준 문서)을 한 커밋에서 먼저 고치고 코드는 그 다음 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거21 |
| `s017` | b1 | 이 문서는 «값»만 싣는다 — 결정 근거·기각 대안은 저장소 정본의 결정 카드 소관 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |

**4원 근거 본문**(공유 근거는 코드로 참조 — 각 코드는 §16 4원 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry/#N 대응 중 **실제 성립한 것만** 적었다):

- **근거1** — registry Agent 등재 · §16 위임 기본값 표(discipline-houserules 문서군 → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례); check-*.py 27종 docstring 선두 전수 실독 결과 이 규범을 지목하는 ①역할명·②§ 인용·③P0 커버 근거 0
- **근거2** — ①문면이 집행 도구로 메인테이너 도구 `tree_mirror_check` 를 명시 — check-*.py 27종 로스터 밖이라 enforcedBy 대상이 아니다 · ②27종 전수 실독 결과 4종(check-layer-skeleton·check-db-table·check-usecase-dto-placement·check-context-isolation)이 «경로 기대는 standard_tree.py 에서 도출한다»로 이 단일 출처를 소비할 뿐 동기 자체를 집행하지 않음 · §16 표 → agent-discipline-reviewer
- **근거3** — ④rule-owner-map #492 행(ast+) → ⓒ workspace/tools/spec_lint.py(로스터 밖)·ⓓ agents/discipline-reviewer.md 명시 · ②27종 전수 실독 결과 트리↔스킬 채널 분리 판정 술어 0 · §16 표와 일치
- **근거4** — ①문면 «모든 검사보다 먼저 서는 원칙이다(#487)» · ②check-layer-skeleton.py docstring 25행 «등록 순서: 이 검사는 다른 모든 검사보다 «먼저» 돌고, 걸리면 나머지를 돌리지 않는다(#487)» + 343행 실발화 · ④rule-owner-map 은 #487 ⓒ 를 workspace/tools/checker_lint.py(로스터 밖)로 두었으나 실장 문면은 check-layer-skeleton 이 소유
- **근거5** — ②check-layer-skeleton.py docstring «표준 파일트리 골격 검사기 — 제1원칙(#486~#491)의 결정적 백스톱»·«트리 데이터는 standard_tree.py(정본 140행의 기계 사본) 하나에서 온다 — 여기는 «존재·폐쇄»만 본다» · ④rule-owner-map 해당 #N → scripts/check-layer-skeleton.py
- **근거6** — ②check-layer-skeleton.py docstring «표준 파일트리 골격 검사기 — 제1원칙(#486~#491)의 결정적 백스톱»·«트리 데이터는 standard_tree.py(정본 140행의 기계 사본) 하나에서 온다 — 여기는 «존재·폐쇄»만 본다» · ④rule-owner-map 해당 #N → scripts/check-layer-skeleton.py; 의미·권한 판정은 기계 밖이라 위임 병기
- **근거7** — ①문면 직접 지목 «골격의 실현 주체는 **coder** 다» — §16 기본값 이탈의 문면 근거 · ②check-layer-skeleton.py 가 위반 적출을 소유(#486·#488)해 문면 «위반은 check-layer-skeleton 이 잡는다»와 일치 · registry Agent 등재
- **근거8** — ②check-app-container.py docstring «앱은 루트 평면이 아니라 `application/<app>/` 아래에 둔다»(§0-1) + check-common-container.py docstring «framework/(저장소 횡단 공용 — 트리 112~134행)는 프로젝트 루트에 둔다 = application/ 의 형제» — 최상위 삼분의 두 축을 각각 결정적으로 집행 · check-layer-skeleton 은 트리 폐쇄 축 · registry Checker 등재
- **근거9** — ④rule-owner-map 해당 #N → scripts/check-layer-skeleton.py(ⓒ) 지목이나, ②그 docstring 26행이 «내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다 — 여기는 «존재·폐쇄»만 본다»로 현행 미커버를 자기 선언 · 27종 나머지 docstring 에도 이 규범 술어 0 → 현행 집행 주체는 에이전트(map ⓓ 와 일치)
- **근거10** — ②check-business-vocabulary.py docstring 5행 «업무 어휘의 정의(#628)는 business_vocab.py(공유 데이터 모듈)가 진다» 직접 #N 인용 + 그 토큰 집합을 재료로 소비하는 #617(280~281행)·#587(283~284행)·#47(286~288행) `f.add` 진단이 이 «정의»를 결정적으로 집행(281행 메시지의 «(#628)» 은 #617 진단의 사유 표기다 — #628 자체의 진단이 아니다) · registry Checker 등재; rule-owner-map 의 #628(ast·재작성) → check-layer-skeleton 은 그 docstring 26행 «Phase 3 편입분» 유예 선언에 막혀 실장 근거가 아니다
- **근거11** — ①문면 역할명 일치 — ②check-missable-entrance.py docstring «바깥이 부르는 입구는 «놓칠 수 있는» 입구다 … 껍데기는 로직을 갖지 않는다» + 33·249행 «#91 — BC 가 형제를 늘리지 않는다» 직접 인용 · registry Checker 등재
- **근거12** — ②check-context-isolation.py docstring «check-layer-skeleton(존재·폐쇄)의 «의존 방향» 짝이다» + «방향 … #93/#94/#95 driving 잎의 import 폭» — #92 는 그 각론(#95)의 총론 · ①문면 역할(의존 방향·예외 4종) 일치 · ④rule-owner-map 은 #92 를 check-layer-skeleton 에 걸었으나 방향 진단 실장은 context-isolation 뿐
- **근거13** — ①문면 역할명 일치(«소비 task» = 바깥이 부르는 놓칠 수 있는 입구) · ②check-missable-entrance.py docstring «바깥이 부르는 입구는 «놓칠 수 있는» 입구다 … 껍데기는 로직을 갖지 않는다» + 담당 #179 [ast] «예약 작업 하나 = 파일 하나 — task 함수는 build 1회 + 유스케이스 1회(+command 생성)뿐. 그 밖 문장·둘째 task 면 위반»(179·191행 `f.add` 진단)이 이 규범이 전제하는 «입구 로직 금지 위반»의 적출을 실장한다 — #178 은 그 위반의 «처방»(새 칸을 열지 말고 위반을 고친다) 규범이라 적출은 검사기·처방 선택은 에이전트(위임 병기) · 그 담당 목록(총 14)에 `#178` 문자열은 없고, ④rule-owner-map 의 #178(ast·재작성) → check-layer-skeleton 은 그 docstring 26행 Phase 3 유예로 미실장이라 실장 실물은 missable-entrance #179 쪽이다
- **근거14** — ②check-port-adapter-pairing.py docstring «port/ #457 선언은 application_layer/port/ 아래뿐» — #187 «애그리거트에 안 붙는 포트는 application_layer/port/ 에만 산다»와 같은 술어 · ④rule-owner-map #187 → check-layer-skeleton(칸 폐쇄 축) 병기
- **근거15** — ②check-mechanism-ownership.py docstring ⑵ «트리 개정 명세 몫 — migrations 규율 4규칙(트리 80·81행 · 조각 ⓑ): #336 마이그레이션은 django_<bounded_context>/migrations/ 에 산다» + #593 실장 · ④rule-owner-map #336~#338·#593 → scripts/check-mechanism-ownership.py
- **근거16** — ①문면이 «그 코드는 트리 밖 scripts/, 규정하지 않는다»로 기계 비커버를 명시 선언 · ②27종 전수 실독 결과 배포 절차 단계 판정 술어 0 · §16 표 → agent-discipline-reviewer
- **근거17** — ①문면이 «권장 — 기계 검사기 없음·reviewer 점검» 으로 비커버를 명시 선언 · ②check-naming.py docstring 전수 확인 — 담당은 #28·#30·#33·#34·#36·#41·#43·#44 등 트리 명명 규약이고 BC명↔애그리거트명 유사 변형 술어 0(P0 발견 5 의 긴장은 «검사기 실존 ≠ 이 규범 커버»로 해소) · §16 표 → agent-discipline-reviewer
- **근거18** — ②check-layer-skeleton.py docstring «표준 파일트리 골격 검사기 — 제1원칙(#486~#491)의 결정적 백스톱»·«트리 데이터는 standard_tree.py(정본 140행의 기계 사본) 하나에서 온다 — 여기는 «존재·폐쇄»만 본다» · ④rule-owner-map 해당 #N → scripts/check-layer-skeleton.py · ②check-db-table.py docstring «#324/#467 층 이름 위장(infra_layer·infrastructure_layer·driven_adapter·secondary_adapter·adapter_layer)» — 문면이 «층 이름 위장은 #324» 로 직접 지목 · registry Checker 등재
- **근거19** — ①문면 «미루기는 사용자에게 물어서만 가능하고 .dddjango/ 에 기록된다» — 사용자 확인 절차라 §16 표 «command+agents(절차 층) → command-dddjango(Coordinator)» 병기 · ②27종 전수 실독 결과 미루기 승인·기록 술어 0 · 문서군 기본값 agent-discipline-reviewer 동시 유지
- **근거20** — ④rule-owner-map #74 → workspace/tools/checker_lint.py(검사기의 검사기) — check-*.py 27종 로스터 밖이라 enforcedBy 대상 아님 · ②27종 전수 실독 결과 전 검사기가 exit 2 가드를 «구현»하나 가드 «집행»은 checker_lint 소관 · §16 표 → agent-discipline-reviewer
- **근거21** — ④rule-owner-map #72 행 = human · ⓒ 열이 «메타(6번 지침·checker_lint)» — check-*.py 27종 로스터 밖이라 enforcedBy 대상 아님 · ②27종 전수 실독 결과 개정 이행 순서 술어 0 · §16 표 → agent-discipline-reviewer
- **근거22** — ①문면의 실현 주체는 `scripts/business_vocab.py`(선두 docstring «#628 «업무 어휘» 데이터 모듈 — 검사기 공유 재료(진단 0 · standard_tree 와 같은 부류)» · 5행 «별도의 용어집 파일은 두지 않는다» 축자 재기) — check-*.py 27종 로스터 밖이라 enforcedBy 대상이 아니다(`registry.ttl` Checker 개체 = `dddjango/scripts/check-*.py` glob 27종) · ②27종 전수 실독 결과 «용어집 파일» 신설을 적출하는 진단 0(check-business-vocabulary.py 도 이 금지의 진단을 갖지 않는다) · §16 표 discipline-houserules → agent-discipline-reviewer(로스터 밖 도구 처리 — tree_mirror_check·checker_lint·spec_lint 와 동형)
- **근거23** — ①문면의 실현 실물은 `scripts/business_vocab.py` 26~27행 STOPWORDS(«# 불용어 — 어느 BC 에나 나오는 낱말(#628 축자 여섯 + 같은 부류). 닫지 않는다» + `frozenset` 정의)와 7행 docstring «불용어 목록도 «저장소가 유지하는 데이터»다(#628 · predicates ⓑ)» — 로스터 밖 데이터 모듈이라 enforcedBy 대상이 아니다 · ②27종 전수 실독 결과 «목록을 저장소가 유지하나»를 묻는 진단 0(검사기들은 이 목록을 «소비»만 한다) · §16 표 discipline-houserules → agent-discipline-reviewer
- **근거24** — ④rule-owner-map #430 행 = `ast` · ⓒ `scripts/check-layer-skeleton.py`(작업=재작성) 지목이나, ②그 docstring 26행이 «내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다 — 여기는 «존재·폐쇄»만 본다» 로 현행 미커버를 자기 선언(같은 절 #429·#436 은 map 판정 = `path` 라 「무엇을 잡나」의 «#429·#436 `<project>/` 직계 폐쇄» 로 실장 — `ast`/`path` 가 이 검사기의 실장 경계다) · 27종 전수에서 `#430` 진단 0건이고, 이웃한 check-context-isolation.py 의 #431(880~911행)은 «부작용 등록»(안 쓰이는 application import)만 잡고 «urls.py 의 `register_<bc>_api(api)` 명시 호출» 은 허용해 #430 의 «타입으로 앎» 술어를 집행하지 않는다 → 현행 집행 주체는 에이전트(§16 표 → agent-discipline-reviewer · 같은 조건의 #10·#82 와 동형 처리)
- **근거25** — ②check-context-isolation.py docstring 33행 «`<project>` #433 규칙을 «주소·예외 목록»으로 적지 않는다 — BC 경로 리터럴 컬렉션» + 858행 진단 «규칙을 «주소 목록»으로 적지 않는다 — BC 경로 리터럴 `…` (BC 가 늘 때마다 이 파일이 바뀐다 · #432)» 가 #432 의 판정 물음(「BC 하나를 통째로 지웠을 때 이 파일이 바뀌나」)을 `<project>/` 파일의 BC 경로 리터럴 축에서 부분 실장(827행 «#433 — `<project>/` 파일의 «주소·예외 목록»» 으로 스코프도 일치) — 27종 전수에서 #432 를 언급하는 유일한 기계 흔적 · ④rule-owner-map 은 #432(ast·재작성)를 check-layer-skeleton 에 걸었으나 그 docstring 26행 «내용 판정 … Phase 3 편입분» 유예 선언 + `#432` 진단 0건이라 실장 근거가 아니다 · 리터럴 밖 «커짐»(설정 분기·import 증식 등) 잔여 판정은 기계 밖이라 위임 병기

## 3. 재진술 유예 (다른 문서 상대 — spec 미기재 · T3 소급 패스 대상)

**문서 내 쌍은 spec 처리 완료** — ① `s002`/b2(#492) → `s003-0`/b7(#492 원출처 — 발주서 note «#492 원출처(사본은 s002)» 가 방향을 확정) ② `s011-3`/b1(«BC 이름은 업무 경계의 이름(#82 — §2)») → `s006`/b2(#82 원문). 둘 다 사본 쪽 Work 를 유지했다(사유 §4).

아래는 상대가 **다른 문서**라 spec 에서 뺀 쌍이다. 이미 이관된 `agent-*` 3종·`discipline-cleancode-final` 의 좌표는 **마커 제거본(센서스) 기준으로 환산**했다.

| # | 사본/정본 블록(이 문서) | 상대 문서/절 | 확인한 상대 문면(센서스 좌표) | 비고 |
|---|---|---|---|---|
| 1 | `s001`/b1 W1(정본 선언·복제 금지) | `discipline-houserules-skill`/s003 · s001 | skill 13행 «트리·칸·규칙의 «값»은 전부 `references/final.md` 가 단일 출처로 소유하고 … 값을 여기에 복제하지 않는다» · skill 3행(frontmatter) «트리와 규칙 «값»의 단일 출처는 references/final.md 다» | **상호 재진술**(발주서 양쪽 Y). 정본 = 이 절, 사본 = skill 2곳 |
| 2 | `s001`/b1 W1 | `agent-discipline-reviewer`/s007 | 센서스 **92행** «트리·배치·명명의 «값» … 전부 `discipline-houserules` `references/final.md` §0·§1·§2·§3·§4 가 소유한다 — 이 문서에는 값을 두지 않는다(값 사본은 썩는다 …)»(현재 99행) | 3중 사본 층 — 리뷰어가 이 절의 소유 선언을 그대로 복창 |
| 3 | `s003-0` 전체(12 Work) | `discipline-houserules-skill`/s004-1 | skill 26행 «**§0 제1원칙**(골격은 내용과 무관 · 고정 칸은 빈 채로도 · 트리 밖 칸은 반환)과 **§1 트리 140행**을 읽고 그대로 실현한다» | 발주서 skill s004-1 재진술 열이 이 절을 지목 — 요약 대 상세(1:N) |
| 4 | `s003-0`/b8 W1(실현 주체 coder) | `agent-coder`/s004 | 센서스 **34행** «**골격 실현 의무.** 승인 스코프의 BC 를 새로 만들거나 touched 하면(touched = G0 스코프의 그 BC …) `final.md` §0·§1 의 골격을 실현한다»(현재 38행) | **거의 축자** — 이 절이 정본, coder 가 사본. 배선의 ①근거(«실현 주체는 coder»)와 짝 |
| 5 | `s003-0`/b3(#488) | `agent-coder`/s004 | 센서스 34행 «고정·재등장 칸은 내용이 없어도 폴더는 `__init__.py` 로, 파일은 빈 파일로 만든다(#488)» | #N 까지 동반한 축자 사본 |
| 6 | `s003-0`/b4·b5(#489·#490) | `agent-coder`/s004 | 센서스 34행 «`<…>` 자리표시자 칸은 그 개념이 실제로 생길 때만 만들고, 트리에 없는 칸은 만들지 않는다(#489·#490)» | 동상 |
| 7 | `s003-0`/b1(#487) · b8 W2 | `agent-coder`/s004 · `discipline-houserules-skill`/s004-1 | coder 센서스 34행 «골격 위반은 `check-layer-skeleton` 이 다른 검사보다 먼저 잡고 반송한다(#487) — 검사기를 통과시키려 트리 밖 우회를 만들지 않는다» · skill 26행 말미 동문 | 3중 사본 층. coder 쪽에 «우회 금지» 가 추가돼 있어 단순 restates 가 아니라 **확장 사본** |
| 8 | `s003-0`·`s004-1` 전체 | `agent-design-architect`/s005 | 센서스 **62행** «**`discipline-houserules` `references/final.md`를 읽고 §0 불변식과 §1 표준 트리(140행)의 고정·재등장 칸을 명세에 그대로 박는다** — … 값을 복사해 두지 않는다»(현재 67행) | 소유 선언 + 값 복제 금지의 재확인 |
| 9 | `s006`/b2(#82) · `s006`/b4(#628) · `s011-3`/b2(유사 변형) | `agent-discipline-reviewer`/s007 | 센서스 **108행** «트리·골격 — #82 이 BC 폴더 이름이 업무의 낱말인가(#628 토큰 0회 후보 · 애그리거트명과 한 글자·복수형 «유사 변형»(`ordering` vs `order`)이면 반송 후보 — houserules final.md §3)»(현재 115행) | 리뷰어가 §3 을 **명시 인용**. `s011-3`/b2 의 «기계 검사기 없음·reviewer 점검» 문면과 정확히 맞물린다 — 위임 배선의 ①근거 실물 |
| 10 | `s004-1` 트리 22~32행(OHS `contract/`) | `agent-discipline-reviewer`/s007 · `agent-design-architect`/s005 · `discipline-cleancode-final`/s026-2.14 | reviewer 센서스 **77행** «OHS published contract(`open_host_service/*/contract/`)의 discriminator wire `Literal`(contract 무의존이 우선 — houserules `references/final.md` §1 트리 22~32행)»(현재 84행) · architect 센서스 62행 «구조·파일 이름의 값은 final.md §1 트리 22~32행 … 이 소유한다» · cleancode-final 318행 «OHS published contract … 의 discriminator는 wire Literal 유지(재예외 — houserules §2)» | **좌표가 트리 내부 행 번호**(트리 22~32행 = 이 파일 **53~63행**, 오프셋 +31). 블록 IRI 는 `s004-1`/b3(code 펜스 31–172행) 하나뿐이라 트리 행 단위 조인이 불가 — 소급 패스에서 **alias 또는 트리 행 좌표 체계**가 필요하다(T3 게이트 조항 «무접두 #N 재검토»와 같은 자리) |
| 11 | `s004-1` 트리 2~4행(`composition_root/`) | `agent-coder`/s004 · `agent-design-architect`/s005 | coder 센서스 **53행** «BC `composition_root/`(`dependency_wiring.py` — final.md §1 트리 2~4행)가 dependency injection만 소유한다»(현재 57행) · architect 센서스 58행 동문 | 10번과 같은 트리 행 좌표 문제 |
| 12 | `s008`/b3(#187) | `agent-design-architect`/s005 | 센서스 **64행** «안 붙는 협력·능력 포트는 `application_layer/port/<capability>/`뿐(#187)»(현재 69행) | #N 동반 축자 사본 |
| 13 | `s014` 전체(3 Work) | `discipline-houserules-skill`/s004-1 · s006-3 | skill 26행 «옛 층 이름·옛 위치는 규약이 아니라 **아직 안 갚은 빚**이고» · skill 46행 «`check-layer-skeleton` 의 exit 2 를 «기존 코드라 면제»로 읽는다 — 빚은 면제가 아니다(`final.md` §4)» | 발주서 재진술 열이 지목한 쌍(Y:discipline-houserules-skill/s004-1) |
| 14 | `s013` 전체(2 Work) | `discipline-houserules-skill`/s006-3 | skill 45행 «옛 이름이 새 코드에 다시 나타난다(`presentation_layer/`·`infra_layer/`·`published_service/` … — 이관은 종료됐고(`final.md` §4) 이제 트리 밖 칸 위반 #81·#490 이다)» | 발주서 note «skill s006-3 신호 4가 이 절의 사본(원출처는 여기)» — 방향 확정 |
| 15 | `s004-1`/b7(«standard_tree.py 가 유일한 트리 데이터») | 검사기 4종 docstring | `check-layer-skeleton.py`·`check-db-table.py`·`check-usecase-dto-placement.py`·`check-context-isolation.py` 가 «경로 기대는 `standard_tree.py` 에서 도출한다 — 이 파일에 트리 경로를 다시 적지 않는다» | **문서-코드 재진술**이라 `djr:restates`(블록↔블록) 로는 못 건다. 소급 시 배선 근거로만 남길 후보 |

### 3-1. 유예 기각 판정(대조했으나 재진술로 보지 않은 것)

- `s009`(migrations) ↔ `implementation-django-final` §10.4(앱 이주·이력 보존) — architect 센서스 64행이 둘을 함께 인용하지만, §10.4 는 **이주 메커니즘**이고 이 절은 **migrations 내용물 규율**이라 대상이 다르다. 기각.
- `s017`(배경) ↔ `architecture-ddd-final` — Evans·Vernon 등 출처 나열은 파생 서사이고 규범 «이 문서는 값만 싣는다» 는 이 문서 고유의 소유 선언이다. 상대 문서에 대응 규범이 없어 기각.
- `s015`(#74 가드 계약) ↔ 검사기 27종의 exit 2 문면 — 15번과 같은 문서-코드 관계라 블록 쌍이 성립하지 않는다. 배선 근거로만 남긴다.

## 4. 경계 판단 메모

- **`s004-1`(155행) 의 블록 분해** — `[27,29]` prose → `[30,30]` norm(TREE:BEGIN 주석) → `[31,172]` **code**(여는 ```` ```text ```` ~ 닫는 ```` ``` ```` 전체 라인 verbatim, §13) → `[173,176]` prose → `[177,177]` norm → `[178,178]` prose → `[179,180]` norm. 7블록으로 155행을 무손실 커버한다.
- **TREE:BEGIN 주석을 code 가 아니라 norm 으로 잡은 판정** — `<!-- TREE:BEGIN — tree_mirror_check 가 쓴다 · 손으로 고치지 않는다 -->` 는 펜스 **밖**의 HTML 주석이고 «손으로 고치지 않는다» 라는 금지 규범을 진다. code 로 접으면 ① 펜스 정의(§13 «여는 펜스~닫는 펜스»)에 어긋나고 ② datatype 이 `xsd:string` 이 되어 규범 리터럴의 `@ko` 규약을 깬다. 센서스 note 도 «TREE 주석 내 «손으로 고치지 않는다» 포함» 으로 이 계수를 지시한다.
- **트리 «행 번호» 는 파일 행 번호가 아니다** — 정본이 «트리 N행» 으로 참조하는 좌표는 코드 블록 내부 번호이고, 파일 행 = 트리 행 + 31 이다(트리 1행 = 파일 32행). 규범·검사기·에이전트 문서가 이 좌표로 이 문서를 가리키는데(§3 표 10·11번), 그래프의 블록 IRI 는 펜스 전체 1개라 **그 좌표를 그래프가 못 짚는다**. 이 절만 예외적으로 «값은 있으나 문장 계수 0» 인 것도 같은 이유다. 소급 패스·T2 소비층이 다뤄야 할 실물 공백으로 기록한다.
- **`#628` 세 규범의 배선은 규범마다 갈린다(W3 적대 리뷰 F4 반영)** — ④`rule-owner-map` 은 #628 을 `check-layer-skeleton.py` 에 걸지만 ②그 docstring 26행이 «내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다» 로 **현행 미커버를 자기 선언**하므로 그쪽은 실장 근거가 아니다. 남은 실물을 규범별로 갈라 보면 ① «어휘 = domain_layer 공개 심볼 토큰 집합» 정의만 `check-business-vocabulary.py` 가 **소비해 집행**한다(#617 280~281행·#587 283~284행·#47 286~288행). 281행은 **#617 진단의 메시지**이고 «(#628)» 은 그 사유 표기다 — #628 자체의 `f.add` 는 27종 어디에도 없다(초판 basis 의 «281행 진단 실장» 문구는 이 오독이었다). ② «별도의 용어집 파일 금지» 와 ③ «불용어 목록 = 저장소 데이터» 의 실현 실물은 `scripts/business_vocab.py`(5행·7행·26~27행)이고 이 파일은 로스터 27종 밖 데이터 모듈(자기 docstring «진단 0»)이라 `enforcedBy` 로 걸 수 없다 — 아래 «로스터 밖 도구» 원칙과 같은 자리다. 그래서 ①만 `enforcedBy`, ②③ 은 위임 단독으로 갈랐다.
- **`#10`·`#82`·`#430` 을 위임으로 둔 것은 도피가 아니다** — 같은 docstring 26행의 Phase 3 유예 선언이 근거다. ④맵의 ⓒ 지목이 있어도 «현행 집행 없음» 이 문면으로 확인되므로 `enforcedBy` 를 걸면 그래프가 존재하지 않는 집행을 주장하게 된다. **`#430` 은 초판에서 이 기준을 스스로 어겼다(W3 적대 리뷰 F1 반영 — 강등).** 판별선은 맵의 «판정» 열이다: 이 절에서 `check-layer-skeleton.py` 가 실제로 지는 것은 `path` 행(#429·#436·#81·#88~#91·#20·#21·#58·#187·#314·#486~#491)뿐이고, `ast` 행(#10·#82·#178·#430·#432·#628)은 전부 Phase 3 유예 구간이다 — 이 절의 layer-skeleton 배선 전건을 이 선으로 재대조했다. `#82` 는 맵 자체가 `ast+`(ⓒ+ⓓ) 라 ⓓ(`discipline-reviewer`)만 남긴 형태이고, `agent-discipline-reviewer` 센서스 108행이 실제로 #82 를 묻는다(§3 표 9번) — 위임의 ①근거까지 성립한다.
- **`#432` 도 `check-context-isolation.py` 로 갔다(W3 적대 리뷰 F2 반영)** — 27종 전수 grep 에서 #432 의 유일한 기계 흔적은 `check-context-isolation.py` 858행의 **#433 진단**이다(«BC 경로 리터럴 … BC 가 늘 때마다 이 파일이 바뀐다 · #432»). 그 진단의 스코프(827행 «`<project>/` 파일의 «주소·예외 목록»»)가 #432 의 주어와 일치하고, 판정 물음(「BC 하나를 통째로 지웠을 때 이 파일이 바뀌나」)을 **경로 리터럴 축에서 부분 실장**한다. 초판의 `check-layer-skeleton.py` 단독 배선은 위 `ast` 유예선에 걸려 성립하지 않았다. 리터럴 밖 «커짐» 은 기계 밖이라 위임을 병기했다 — §16 «역도 성립»(근거가 있는데 기본값 도피 금지)과 «존재하지 않는 집행 주장 금지» 를 동시에 만족시키는 자리다.
- **`#178` 의 ② 근거는 `#179` 진단이다(W3 적대 리뷰 F3 반영)** — 배선(`check-missable-entrance.py` + 위임)은 유지하되 근거를 갈았다. 초판 basis 의 «33·249행» 인용은 전부 **#91 의 앵커**였고 그 검사기 담당 목록(총 14)에 `#178` 은 없다. 실제로 이 규범의 전제(«소비 task 가 껍데기를 넘어 조율을 시작») 를 적출하는 것은 `#179`(179·191행 — 둘째 task·본문 제어 흐름)이고, #178 은 그 위반의 **처방** 규범이라 적출=검사기·처방 선택=에이전트로 갈린다. ④맵의 #178→layer-skeleton 은 `ast` 유예 구간이라 실장이 아니다.
- **`#92` 를 `check-context-isolation.py` 로 뺀 판정** — ④맵은 #92 를 `check-layer-skeleton.py`(존재·폐쇄 축)에 걸지만, #92 는 **의존 방향** 규범이고 그 docstring 이 스스로 «`check-layer-skeleton`(존재·폐쇄)의 «의존 방향» 짝이다 … 방향 #93/#94/#95 driving 잎의 import 폭» 이라 선언한다. #95 는 #92 의 각론이라 총론-각론 관계가 성립한다.
- **`④` 라벨을 `registry.ttl` 개체 등재에 쓰지 않는다(W3 적대 리뷰 F7 반영)** — §16·발주 계약의 4원 ④ 는 «registry **#N** 대응» 이다. 초판은 위임 기본값 basis 의 «registry Agent 등재»(개체 존재 사실)에 ④ 를 붙여 4원 라벨을 오용했다. 사실 기재는 남기고 «④» 접두만 뗐다 — 같은 성질인 «registry Checker 등재» 3건도 한 파일 안 라벨 일관을 위해 함께 뗐다. 위임 기본값 규범의 §16 요건은 «기본값 표 + 27종 전수 0» 경로만으로 충족된다.
- **`#91` 은 두 검사기 병기** — `check-missable-entrance.py` 가 33·249행에서 «#91 — BC 가 형제를 늘리지 않는다» 를 직접 인용(②)하고, 칸 폐쇄 자체는 `check-layer-skeleton.py`(④맵)가 진다. 27종 전수 실독이 없었으면 `check-missable-entrance.py` 를 놓쳤을 자리다(§16 L-F 교훈의 재현).
- **로스터 밖 도구는 `enforcedBy` 대상이 아니다** — `tree_mirror_check`(s001·s004-1)·`checker_lint.py`(#74)·`spec_lint.py`(#492)·`registry_gate.py` 는 전부 문면·④맵이 지목하지만 `registry.ttl` 의 Checker 집합은 `dddjango/scripts/check-*.py` 27종으로 닫혀 있다. 미선언 개체 참조는 게이트 ④(rules 전량+wiring+vocab)에서 위험하므로 **위임 + basis 에 도구명 명기**로 처리했다. 기본값 도피와 구분되도록 basis 마다 «로스터 밖» 사유를 적었다.
- **`agent-coder` 위임(문면 근거 이탈)** — `s003-0`/b8 W1 만 §16 기본값(`agent-discipline-reviewer`)에서 벗어나 `agent-coder` 로 갔다. 근거는 문면의 직접 지목 «골격의 실현 주체는 **coder** 다» 한 줄이고, 같은 문장의 «위반은 `check-layer-skeleton` 이 잡는다» 로 `enforcedBy` 를 병기했다 — 실현 주체와 적출 주체가 문면에서 분리돼 있어 둘 다 필요하다.
- **`s014` 의 «미루기» 만 Coordinator 병기** — «미루기는 사용자에게 물어서만 가능하고 `.dddjango/` 에 기록된다» 는 사용자 확인 절차라 §16 표의 «command+agents(절차 층) → command-dddjango» 행이 문면 근거와 함께 성립한다. 나머지 58 규범 중 이 1건 외에는 Coordinator 를 쓰지 않았다.
- **재진술과 Work 승격** — `s002`(#492)·`s011-3`/b1(#82 재인용) 둘 다 사본이지만 Work 를 유지했다. `s002` 는 정본(`s003-0` 22행)에 없는 «트리에 조건을 적어 두 채널로 만들지 않는다» 라는 금지를 **추가로** 지고, `s011-3`/b1 은 같은 블록에 «명명 전수는 각 칸 «이름» 줄 소유» 라는 고유 규범이 동거한다. §15 의 «정본 1곳만 승격» 요건은 파일럿의 **축자 쌍**(ninja §6.2↔§2.2)이 실물 기준이고, 여기 둘은 축자 등가가 아니다. Work 를 접었다면 발주서 58 ↔ spec 56 의 과소가 생긴다. 이 판정 규칙은 이 묶음 3문서에 일관 적용했다.
