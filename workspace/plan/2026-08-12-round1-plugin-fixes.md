# 라운드 1 발견 수정 계획 (문제 정의 → 원인 → 계획 → 구현 → 테스트)

2026-08-12. 라운드 1(child_settings) 판정에서 나온 발견의 수정 계획.
근거 실측은 프로토콜 §4 대장과 재현 명령(아래 각 절) — 라운드 정본은
`workspace/plan/2026-08-12-bc-rebuild-protocol.md`.

## 1. 문제 정의 (확정 — 사용자 접수 08-12)

**P1′ — «기존 구현을 따르라» 지침을 파일트리 축에서 발본색원한다(사용자 격상).**
파이프라인이 15개 legacy BC 를 «확립 규약»으로 읽고 V1 트리(presentation_layer·
infra_layer·acl)를 신축 BC 에 재생산했다. houserules §1.1 의 산문 예외(「옛 이름
잔재는 규약이 아니라 빚」)는 실물 예시 15개를 이기지 못했고, 표준 트리를 dddart
것으로 오인하기까지 했다(설계 문서에 명문). **패치(예외 강화)가 아니라 제거**:
파일트리에 관한 한 «기존 규약 우선» 결정 순서 자체를 없앤다 — 트리는 언제나
dddjango 표준이다. 인벤토리(스윕 대상 6곳):

| # | 위치 | 문장 |
|---|---|---|
| 1 | `skills/discipline-houserules/SKILL.md:26` | §1 결정 순서 1 «기존 프로젝트 규약을 우선한다» — **핵심** |
| 2 | `SKILL.md:33` | «남는 변수는 §1.1(기존 규약)뿐» |
| 3 | `agents/design-architect.md:25` | 기존 레이아웃 규약 조사 지시 |
| 4 | `agents/design-architect.md:62` | «조사한 기존 규약이 있으면 그것을, 없으면 표준 트리» |
| 5 | `agents/design-architect.md:64` | «§1.1 존중은 전체 레이아웃 철학에만» (참조 정리) |
| 6 | `agents/discipline-reviewer.md:92` | «기존 규약을 존중한 케이스는 그 규약과 대조» |

**발본색원의 선 — 남기는 것(트리 밖 축·검출 리터럴):**
- 주석 언어 관례(§3)·기존 도구 감지(§4 uv 등)·API 에러 프로필 preserve-established
  (wire 계약 보존 — 스팩 등가 목적) — 이들은 트리가 아니라서 유지.
- **검출 리터럴은 지시가 아니다**: `migration_gate.py` 의 LEGACY_DIR_NAMES ·
  `check-common-container` 의 «common» 검출(#49)은 옛 이름을 «잡기 위해» 아는 것 —
  제거 금지.
- dddjango/dddart 트리 혼동 교정: 표준 트리(driving_layer/driven_layer …)가
  **dddjango 것**임을 SKILL 에 못 박는다.

**P2 — 백스톱 호출 계약 부재(핵심 — 기계 그물).**
`check-layer-skeleton.py application/child_settings`(BC 폴더 TARGET) →
`rglob("application")` 공집합 → «표준 미채택 clean» exit 0 조용 통과. 같은 검사기를
루트로 부르면 exit 2·child_settings 38건(08-12 재현). #74 가드(조용한 무동작 금지)는
채택 신호가 TARGET 기준이라 이 경우 전제가 무너져 못 막는다. 수정 둘:
- ⓐ **검사기 공통 가드**: TARGET 자체가 BC 모양(4층 폴더 직계 보유 또는 django_* 앱
  마커)인데 TARGET 밑에 `application/` 컨테이너가 없으면 → clean 이 아니라
  **사용 오류 exit 1**(«대상은 저장소 루트다»). 구현 자리는 `standard_tree.py` 공통
  helper + 27종 main 첫머리 — checker_lint(㉢)에 «가드 호출 존재» 그물 추가.
- ⓑ **SKILL 게이트 계약**: 오케스트레이터(commands/dddjango.md 의 registry 표 절)에
  «백스톱은 저장소 루트에서 레지스트리 전체 1회(TARGET=루트)»를 게이트 계약으로 명문화.
- P2 가 되면 P1′ 이 재발해도(에이전트가 또 합리화해도) 기계가 커밋 전에 막는다.

**H1 — 하네스: openapi_shape.py 시간 의존 값 미정규화.**
A축 유일 diff = 타 BC `x-date-maximum` 하루 차이(값이 벽시계에서 파생). `x-date-*`
(벤더 확장 중 날짜값) 정규화(드롭)를 추가한다 — 모양 밖 문서 표면 취급.

**범위 밖(기록만)**: ⑥a 의 «spec 템플릿에 골격 문장» 제안은 채택 보류(spec 이 트리를
지시하면 플러그인 평가가 오염 — P1′·P2 가 정공법). published_service 슬롯 논점은 V2
재라운드에서 #488(published_event)이 잡음 — P2 에 흡수. 사용자 전역 CLAUDE.md 의
「기존 코드의 구조를 먼저 따른다」 한 줄은 플러그인 밖 — 사용자 판단 사항으로 표면화만.

## 2. 원인 (실증 완료 — 대장 참조)

산문 규칙 < 실물 예시 15개(에이전트 합리화) · 백스톱 호출 레벨 오류 → 조용 통과 ·
리뷰 4겹(리뷰어 3+discipline) 전부 같은 합리화에 동조. 명세 «값»(final.md)에는 답습
지침이 없음을 grep 실측 — 수정은 SKILL·agents 산문과 검사기 가드에 한정된다.

## 3. 계획 (구현 순서 — 테스트 먼저)

1. **fixture red 먼저(P2ⓐ)**: `workspace/eval/fixtures/` 에 «BC 폴더 TARGET» 케이스
   신설 — 표준 채택 fixture 의 BC 폴더를 TARGET 으로 27종 실행 → 기대 exit 1.
   지금은 skeleton 이 0 을 내므로 red. fixture_matrix 에 «호출 계약 레인» 추가.
2. **P2ⓐ 구현**: standard_tree.py 공통 helper(`reject_bc_shaped_target`) + 27종 적용
   + checker_lint ㉢ 그물(가드 호출 부재 = red) → fixture green.
3. **P2ⓑ + P1′ 구현**: houserules §1 결정 순서 재작성(1=표준 트리 강제 · 기존-존중은
   트리 밖 축 한정 절로 분리) · 위 6곳 스윕 · dddart 혼동 교정 · 오케스트레이터 게이트
   계약 명문화.
4. **H1 구현**: openapi_shape.py `x-date-*` 정규화 + broccoli 재덤프로 결정성 재확인.
5. **미러·검증**: codex SKILL 재생성 + 검증 8종(corpus·spec_lint·checker_lint·
   tree_mirror·reverse_coverage·fixture_matrix(신규 레인 포함)·backstop_matrix 675·
   byte-copy) 전부 green. **eval v5: FROZEN 유지** — 규칙 «값» 무변(산문·가드·하네스만).
   backstop_matrix 675 재실행으로 판정 무변 실증.
6. **배포**: v2.0.0 → **v2.1.0**(검사기 exit 계약 추가 = 기능 추가·판정 무변) · 설치본
   갱신.
7. **테스트 = 재라운드**: broccoli-rebuild 현 HEAD 에서 child_settings 재삭제(새 앵커·
   spec.md·api_shape_pre.json 재사용) → ④ 새 세션(v2.1.0) → ⑤ 3축 → ⑥a·⑥b.
   **자: C축 green(V2 트리) 이 이번 수정의 성공 판정이다.**

## 4. 열린 결정 (사용자)

- ⓐ P1′ 스윕 범위 동의 — «트리 축 제거·트리 밖 축 유지·검출 리터럴 보존» 선.
- ⓑ 전역 CLAUDE.md 의 「기존 코드 구조 우선」 한 줄에 트리 예외를 달지.
- ⓒ 버전 v2.1.0(minor) 판단.
