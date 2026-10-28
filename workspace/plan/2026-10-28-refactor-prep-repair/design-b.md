# 설계 B — 표준 트리 밖 (⑤) · 3판

- 판: 설계 A 와 한 판(dddjango 다음 판)
- 바탕: 진단 c(트리 밖 자리 · 규칙 대조 · web 선례) · 현장 측정(트리 밖 파이썬 — 현장 처분은 공개 저장소 밖 캠페인 계획에) · 적대 검토 2회(1회 차단 2 · 중요 6 · 사소 7 / 2회 차단 0 · 중요 3 · 사소 6 — 운영자가 재현 다시 돌려 같은 결과 · 아래 «검토 반영»)
- 사용자 결정: 2026-10-28 «BC 밖은 없다 — BC 밖도 결국 dddjango 로 개발한 것»(옛 배치는 빚) · 데이터 생성 공장 폴더는 관할 밖(«가.») · 시험 정리는 넣지 않음
- 규칙이 이미 정한 것: 일회성 `scripts/` 는 관할 밖(D22 · #336~#338) · 다른 BC 는 입구로 검사한다(#385) · 전역 규칙의 시험은 `framework/test/unit/`(D25) · 레포 루트 `conftest.py` 는 공유 fixture 자리(implementation-test §4.2)
- 이 판의 몫은 **성장 막기**(B1 · B2)다. 이미 있는 파일을 옮기는 일(B3)은 플러그인 기능이 아니라 캠페인 단계다.

## 무엇이 문제였나

1. **플러그인 규칙이 루트 시험 폴더를 키운다.** houserules SKILL §1.2 가 승인된 시험을 «기존 프로젝트 테스트 위치나 표준 위치»에 두게 하고, §1.3 «레이아웃을 혼용하지 않는다»가 «루트 `tests/` 를 쓰는 프로젝트면 새 시험도 거기에»로 읽히며, 관찰 축 닫힌 목록 ⑤ «승인 test artifact 의 기존 위치»가 기존 위치를 결정 입력으로 연다. 감수자 규칙(discipline-reviewer)도 «승인된 test artifact 의 기존 테스트 위치(§1.2)만 예외로 그 위치와 대조»한다.
2. **루트 시험 폴더를 어느 검사도 내지 않는다.** 27종 어느 규칙도 루트 `tests/` 를 빚으로 내지 않는다(#490 폐쇄는 BC 안 · #429 는 프로젝트 패키지 안 폴더 한 줄). 플러그인 실행이 거기에 새 시험을 만들어도 G2 귀속에 걸리지 않는다.

## 고침

### B1 성장 막기 — 규칙 글(graph-owned · 한 커밋 · #72)

- houserules SKILL(`ontology/rules/discipline-houserules-skill.ttl`):
  - §1.2 → «새 시험 파일은 — 어느 입장(`add` 케이스를 담을 새 파일 · 승인된 `retain` 재조직의 목적지)에서 만들든 — 표준 위치(BC `test/` 의 자식 — `final.md` §1 트리 136~142행 · 전역 규칙의 시험은 `framework/test/unit/`)에만 만든다. `update` · `remove` 는 기존 파일 그 자리에서 고친다 — 표준 밖 자리는 빚이다. 표준 밖 기존 파일에 새 case 를 더하지 않는다. 새 BC 시험은 루트 시험 폴더(`tests` · `test` 패키지)를 import 하지 않는다 — 루트 fixture · 도우미가 필요하면 그 BC `test/conftest.py` · `test/fake/` 에 새로 쓴다. 이 규칙은 기존 시험을 옮길 권한을 주지 않는다 — BC 밖 시험(루트 시험 폴더 등)의 옮김은 파이프라인 밖 운영 작업이다(리팩토링 실행은 대상 BC 밖을 편집하지 않는다). 구조 규칙 자체는 test file/case/assertion 을 만들거나 기존 테스트를 자동 이동하지 않는다.»
  - §1.3(R-3127) → «한 프로젝트 안에서 표준 밖 새 시험 자리를 만들지 않는다 — 표준으로 옮겨 가는 동안 옛 자리와 표준 자리가 함께 있는 것은 빚이지 혼용 위반이 아니다. 이 규칙만으로 기존 테스트 이동 권한이 생기지는 않는다.»
  - 관찰 축 닫힌 목록에서 ⑤ «승인 test artifact 의 기존 위치(§1.2)»를 걷고 ⑥ → ⑤ 로 당긴다 · R-3134 prefLabel «닫힌 목록 여섯» → «다섯».
- discipline-reviewer(`ontology/rules/agent-discipline-reviewer.ttl` R-1057 · `discipline-reviewer.md:103`) → 예외 문장을 걷고 «시험도 표준 위치와 대조한다 — 기존 시험의 제자리 `update` · `remove` 는 위치 판정 밖 · 입장 `add` 행 owner/path 가 표준 밖 기존 파일이면 발견(새 case 를 표준 밖에 더함)». wiring 의 R-1057 `enforcedBy check-test-config.py` 는 그대로 둔다(#658 이 집행하는 «새 파일 · 새 import 의 자리»와 같은 뜻).
- design-architect(`ontology/rules/agent-design-architect.ttl` · `design-architect.md:30` «기존 test artifact 위치를 … 결과 제약에 쓴다») → «`update` · `remove` 행의 기존 자리를 … 결과 제약에 쓴다»로 좁힌다(Codex 미러 포함).
- implementation-test `references/final.md:411` «의미군 위치의 단일 출처는 houserules §2» → «§1.2»(옛 오기 · 산문 절 — final.md 고친 뒤 `corpus_mirror_sync` · LEDGER 재기준선).
- B1 은 기존 Work 의 개정이라 `ISSUED` 가 필요 없다(산문 절을 고치는 implementation-test 만 LEDGER).
- 이 축과 예외는 2026-08-12 «트리 답습» 봉인 때 열린 것이다 — 걷는 까닭(사용자 «BC 밖은 없다» · 옛 배치는 빚)을 배포 보고에 적는다.
- Codex 의미 미러: `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md` · `dddjango-discipline-reviewer/SKILL.md:96` · (고치면) design-architect 미러.

### B2 새 규칙 #658 — 루트 시험 폴더(검사기 `check-test-config.py`)

- 규칙 ㄱ(자리): 저장소 루트의 `tests/` · `test/` 아래 **모든 `.py`**(이름 무관 — helpers · factories · fakes · conftest 포함 · 비었거나 docstring 뿐인 `__init__.py` 만 뺌 — #655 와 같은 술어 · 코드를 품은 `__init__.py` 는 위반)는 위반이다. 이름이 아니라 자리로 판정한다(머리말 #596 «파일 이름은 pytest 소유»와 같은 결 — `python_files` 설정 · Django `tests.py` 꼴과 무관).
- 규칙 ㄴ(의존): BC `test/` · `framework/test/` 안 파일이 최상위 `tests` · `test` 패키지를 import 하면(`import tests…` · `from tests… import`) 그 파일 한 줄 — 새 BC 시험이 루트 시험 폴더의 fixture · 도우미에 기대어 루트 의존을 새로 늘리는 우회를 막는다(검토 2회 I-1 재현 · 이미 모은 import 를 한 번 더 본다).
- 처방 문구: «시험은 주인의 표준 시험 자리(BC `test/` · 전역 규칙은 `framework/test/unit/`)에 둔다».
- 빼는 것:
  - 레포 루트 `conftest.py`(저장소 루트 바로 아래 — §4.2 공유 fixture 자리).
  - 루트 `tests/web/` · `test/web/` — web 시험이다. web 표준 자리는 `web_test/`(dddjango-web houserules)이고 web 시험 범위 계산도 이 경로를 web 시험으로 알아본다. core 검사기가 core 자리를 처방하면 틀린 자리를 가리킨다 — web 쪽 판정은 web 캠페인 몫으로 넘긴다(진단 c D7 · 사용자 «core 먼저 · web 따로»).
  - 관할 밖 폴더(일회성 `scripts/` 와 프로젝트가 관할 밖으로 둔 도구 폴더)는 애초에 보지 않는다 — 이름을 고정한 두 폴더만 본다. 그래서 프로젝트별 관할 밖 선언 장치가 필요 없다.
- 줄은 파일마다 하나 — G2 귀속(N∖L)이 «이미 있는 폴더 안의 새 파일»을 보려면 줄이 파일 단위여야 한다(폴더 한 줄인 #429 가 새 파일을 못 보는 것과 대비). #658 줄은 Phase 0 · R1 경로 필터(`application/<bc>/`)에 걸러져 G0 배너 · ⓐ 잔존에는 들지 않는다.
- 효과: 플러그인 실행이 루트 시험 폴더에 새 파일을 만들면 G2 귀속 red(신규 위반) · 이미 있던 파일은 legacy 잔존 보고(차단 아님 · 게이트 출력은 검사기별 계수만 늘어남).
- 받아들인 한계(규칙 글 · 감수가 덮음):
  - 기존 루트 파일에 case 덧붙임은 줄이 그대로라 기계로 못 가른다 → B1 §1.2 «표준 밖 기존 파일에 새 case 를 더하지 않는다» + 감수 발견.
  - `<project>/` 안 시험 폴더(#429 폴더 한 줄)의 새 파일 · `testing/` 같은 다른 이름 · 루트 바로 아래 시험 파일 → 이름 판정이 필요해 이번 판 밖 · B1 문면 + 감수가 덮는다.
  - 루트 `tests/web/` 의 자리는 이제 두 플러그인 어느 검사도 판정하지 않는다(web 쪽에도 그 자리를 위반으로 내는 검사가 없음) → web 캠페인 장부에 넘긴다(배포 보고 · 캠페인 계획에 한 줄).
- 규칙 글 · 대장(한 커밋):
  - houserules `references/final.md` 의 해당 절(그래프 정본이면 ttl → 렌더 · `corpus_mirror_sync`).
  - `workspace/design/2026-08-08-tree-revision-spec.md` 의 #658 행 + 집계표(`corpus_lint` ② 가 `#N` 을 살아 있는 번호와 대조).
  - `workspace/plan/2026-08-11-rule-owner-map.md` 의 658 행(`spec_lint` ⑧ 1:1).
  - 새 Work 의 R-ID 는 `ISSUED` 에 설계 A 의 새 R-ID 들과 같은 판 차례로 append(지금 끝 R-3713) · wiring `enforcedBy check-test-config.py` · alias 는 두지 않는다(#385 등과 같이).
  - Coordinator 레지스트리 12번 줄(`dddjango.md:197` · graph-owned `command-dddjango`)과 Codex `skills/dddjango/SKILL.md` 같은 줄.
  - 검사기 머리말 ⑵ 와 #596 문장 · Codex byte 미러.
  - `docs/mkrev2.py`(file_tree.html 원본)의 루트 시험 폴더 표기.
  - 매트릭스(`fixture_matrix` · `checker_baseline_matrix` · `findings_count_matrix`) — 기존 픽스처에 BC · framework 밖 루트 시험 폴더가 없어 기존 기대는 무변일 것 · 새 사례만 더한다(구현 때 확인).

### B3 이미 있는 트리 밖 파일 — 플러그인 기능을 새로 만들지 않는다

- 트리 밖 파일을 BC 실행이 흡수하는 장치(주인 계산 하위 명령 · R1 경로 필터 · 0T 갈래 · 레인 경로)는 만들지 않는다.
- 이미 있는 파일을 옮기는 일은 **플러그인 관할 밖의 운영 작업**이다 — 사용자의 명시적 지시로 운영자가 한 번 옮긴다(파이프라인 안의 셋째 이동 경로가 아니다). 어느 파일을 어디로 옮길지 · 절차 상세는 공개 저장소 밖 캠페인 계획(0-4)에 적는다 — 이 설계에 두면 운영 처분(예: 설정 시험을 `framework/test/unit/` 로 넓혀 읽기)이 규칙처럼 읽힌다.
- 옮길 때의 위험(캠페인 계획이 막아야 할 것 — 검토가 재현):
  - fixture 가 안 보임 — conftest 는 조상 폴더만 보인다. 루트 `tests/conftest.py` fixture 를 쓰는 시험을 옮기면 `fixture '…' not found`(1회 I-3).
  - fixture 를 합치면 동작이 바뀜 — 같은 이름 fixture 덮어쓰기 · autouse · hook 의 범위가 넓어져 원래 있던 BC 시험이 바뀐다. 실패 없이 조용히 퍼지는 경우(autouse mock)는 «전후 green»으로 못 잡는다(2회 I-2) — 옮기기 전에 `pytest --fixtures` 로 이름 겹침 · autouse · hook 을 목록으로 남기고, 겹치지 않고 autouse · hook 이 아닌 것만 넓은 자리로 올린다.
  - 도는 레인과 부딪침 — 옮긴 파일이 다른 레인의 편집 대상이거나, 목적지 BC 실행이 설계 A «대상 낡음»으로 폐기되거나, 옮겨 온 빚이 그 레인 G2 귀속 red 가 된다(1회 I-6 · 2회 S-5) → 저장소 전체 활성 실행 0 일 때만 · 한 커밋 · SHA 기록 · `.py` 가 아닌 시험 자료도 함께.
- «내용 무변»의 뜻: 시험 함수 본문 무변 — import 경로와 fixture 자리만 바꾼다. 확인: 전후 전체 시험 green · 수집 케이스 수 같음 · 27종의 새 줄은 옮겨 온 빚뿐(목록).

## 고르지 않은 안

- web 판박이(옛 폴더를 리팩토링 단위로): core 실행 장치가 대상 BC 하나에 묶여 있고(behavior_guard 의 안쪽 판정 · deps 의 엮인 BC 동시 금지) 자리 없는 종류가 남아 실행이 끝나지 않는다.
- 주인 BC 흡수 장치(진단 c 안 B1): 현장에서 주인이 하나인 core 시험은 두 파일뿐이라 값이 작은데 장치가 크다.
- 루트 시험 폴더를 «여러 BC 흐름 시험» 표준 자리로 올림: 칸이 있으면 쓰게 된다(D25) · 사용자 «BC 밖은 없다»와 어긋남.
- #658 을 이름 판정까지 넓힘(`<project>/` 안 · `testing/` · 루트 직계): 이름은 pytest 소유(#596) · 관할 밖 폴더와 가르려면 선언 장치가 필요하다.

## 시험 사례

- B2(`check-test-config` 픽스처 · G2 게이트 장난감):
  - 위반 1: 루트 `tests/test_x.py` · `tests/sub/conftest.py` · `tests/helpers.py` · `test/factories.py` · 코드를 품은 `tests/support/__init__.py` · BC `test/unit/test_u.py` 가 `from tests.helpers import X` · `import tests.conftest`.
  - 0: 레포 루트 `conftest.py` · 빈 `tests/__init__.py` · `tests/web/test_w.py` · `test/web/x.py` · `scripts/test_y.py` · 도구 폴더 `tools/test_z.py` · BC `test/` 안(루트 import 없음) · BC 운영 코드의 `tests` 라는 이름의 BC 내부 모듈 상대 import.
  - 게이트: 새 `tests/test_new.py` · 새 `tests/helpers2.py` · 루트를 import 하는 새 BC 시험 → 귀속 1 씩 · 새 `tests/web/…` → 0 · 기존 파일에 case 덧붙임 → 0(한계 고정) · 옛 파일 → legacy.
  - 배포 때 도는 실행: 앵커가 옛 판으로 재여도 G2 는 새 검사기로 앵커를 다시 잰다 — G1 에서 루트 `tests/` 를 `add` 로 승인받은 실행은 새 판에서 G2 red(릴리즈 노트).
- B1: 렌더 · rulepack 갱신 · Codex 의미 미러 대조 · R-1057 문면 렌더 대조 · R-3134 prefLabel.

## 고칠 파일

| 파일 | B1 | B2 |
|---|---|---|
| `ontology/rules/discipline-houserules-skill.ttl`(§1.2 · §1.3 R-3127 · 축 ⑤ · R-3134 + 렌더 · rulepack · LEDGER/ISSUED 필요한 것) | ✓ | |
| `ontology/rules/agent-discipline-reviewer.ttl` R-1057 + `ontology/wiring/agent-discipline-reviewer.ttl` + 렌더 | ✓ | |
| `ontology/rules/agent-design-architect.ttl`(:30 좁힘) + 렌더 | ✓ | |
| implementation-test `references/final.md:411`(§2 → §1.2 · `corpus_mirror_sync` · LEDGER) | ✓ | |
| houserules `references/final.md` 규칙 줄(+ 정본이 그래프면 ttl · `corpus_mirror_sync`) | | ✓ |
| `ontology/rules/command-dddjango.ttl` 레지스트리 12번 줄 · `ISSUED` · wiring `enforcedBy` | | ✓ |
| `workspace/design/2026-08-08-tree-revision-spec.md` · `workspace/plan/2026-08-11-rule-owner-map.md` | | ✓ |
| `dddjango/scripts/check-test-config.py`(+ 머리말 ⑵ · #596) ↔ Codex byte 미러 | | ✓ |
| 매트릭스 · 픽스처(`workspace/eval/fixtures/**`) | | ✓ |
| Codex 의미 미러 SKILL.md(houserules · discipline-reviewer · dddjango · 필요하면 design-architect) | ✓ | ✓ |
| `docs/mkrev2.py` · `README.md` · `docs/master.html` 이 싣는 문서 | ✓ | ✓ |

## 검토 반영

| 검토 | 처분 |
|---|---|
| B-1 감수자 «기존 테스트 위치 예외»(R-1057) 남음 | B1 — R-1057 개정 · wiring 재검토 · Codex 미러 · 한 커밋 |
| B-2 `update` · case 덧붙임 · §1.3 혼용 금지 | B1 — 새 파일만 표준 자리 · update/remove 제자리 · 표준 밖 기존 파일에 새 case 금지 · 옮겨 가는 동안은 빚 |
| I-1 #658 이 좁음 | B2 — 루트 `tests/` · `test/` 아래 모든 `.py`(이름 무관) · 나머지(case 덧붙임 · `<project>/` 안 · 다른 이름)는 한계 + B1 문면 + 감수 |
| I-2 `tests/web/` 을 core 가 틀린 자리로 처방 | B2 — `tests/web/` · `test/web/` 뺌 · web 캠페인 몫 |
| I-3 conftest fixture 소실 · `tests.*` 도우미 | B3 — fixture · 도우미 자리와 경로 고침을 절차에 · «내용 무변» = 본문 무변 |
| I-4 여러 BC 시험 → #385 빚을 갚으려면 기대 변경 | 사용자 결정 2026-10-28 «가.» — 캠페인 동안 제자리 · 캠페인 뒤 따로(캠페인 계획 0-4) |
| I-5 목적지 빈칸 셋 | B3 — web · 관할 밖 코드 시험 · 주인 없는 설정 시험 자리 |
| I-6 이동 시점 × 도는 레인 | B3 — 도는 실행 0 일 때만 · 한 커밋 · SHA |
| S-1 고칠 파일 누락 | 고칠 파일 표 |
| S-2 R-3134 prefLabel · 질의 골든 | B1 — 다섯으로 · 질의 골든 언급 지움 |
| S-3 «파일마다 한 줄» 근거 | B2 — N∖L 이 새 파일을 보려면 |
| S-4 채번 | B2 — ISSUED 차례 · alias 없음 · 매트릭스 무변 확인 |
| S-5 권한 인용 | B3 — 플러그인 관할 밖 운영 작업 |
| S-6 배포 때 도는 실행 | 시험 사례 · 릴리즈 노트 |
| S-7 새 시험이 suite 정의에 안 잡힘 | 설계 A A5 — `add` 목적지 폴더 수집 0 이면 G1 배너 알림 |
| 2회 I-1 새 BC 시험의 `from tests…` import 우회(재현) | B1 문면 «루트 시험 폴더를 import 하지 않음 · BC conftest/fake 에 새로» + B2 규칙 ㄴ |
| 2회 I-2 fixture 합치기가 기존 BC 시험 동작을 바꿈(재현) | B3 위험 — `pytest --fixtures` 목록 · 겹침 · autouse · hook 은 넓히지 않음(절차는 캠페인 계획) |
| 2회 I-3 §1.2 의 이동 경로가 루트 시험에 안 닿음 | B1 — 이동 경로를 적지 않고 «BC 밖 시험의 옮김은 파이프라인 밖 운영 작업» |
| 2회 S-1 미룬 결정 | R-1057 wiring 유지 · design-architect:30 좁힘 · B1 ISSUED 없음 |
| 2회 S-2 문구 | §1.2 «새 시험 파일은 어느 입장에서 만들든» · §1.3 «표준 밖 새 시험 자리» |
| 2회 S-3 코드 품은 `__init__.py` | B2 — 비었거나 docstring 뿐인 것만 뺌(#655 술어) |
| 2회 S-4 `tests/web/` 판정 주체 없음 | B2 받아들인 한계 · web 캠페인 장부 |
| 2회 S-5 이동 시점 범위 · 자료 파일 | B3 — 저장소 전체 활성 실행 0 · 자료 함께 |
| 2회 S-6 implementation-test §4.2 오기 | B1 — §1.2 로 |
| 2회 «더 단순하게» | B3 절차 상세를 캠페인 계획으로 · 설계에는 운영 작업이라는 것과 위험만 |
